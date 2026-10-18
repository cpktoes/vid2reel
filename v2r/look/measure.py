"""The measuring pass: one FFmpeg run over a working copy, read back as half-second summaries.

This measures and reports; it decides nothing. A measurement that cannot be made is None, never a guess (D-21).
"""

import errno
import math
import re
import statistics
import subprocess
from pathlib import Path

from v2r import normalize, settings

# FFmpeg pieces without which no measuring pass can run at all; any other missing filter only loses its own numbers.
NEEDED_FOR_ANY = ["fps", "scale", "metadata"]
STATS_FILE = "stats.txt"  # a fixed plain name inside the temporary folder: no file name of the user's is ever in a filter
HEADER = re.compile(r"frame:(\d+)\s+pts:(-?\d+)\s+pts_time:(\S+)")

# Every measuring filter, in the order it sits in the chain: (filter name, what it measures in words, the chain piece).
# This table is the one place a measuring filter is named. The piece is built when the chain is built, from settings.
MEASURES = [
    ("signalstats", "movement, brightness and colour", lambda: "signalstats"),
]


def finite(text):
    """A number from text FFmpeg printed, or None for anything empty, not a number, NaN or infinite."""
    try:
        value = float(text)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def rounded(value):
    """A number rounded to settings.LOOK_DECIMALS for look.json; None stays None."""
    return None if value is None else round(value, settings.LOOK_DECIMALS)


def missing_measurements(have):
    """One plain sentence for each measuring piece this computer's FFmpeg lacks (`have` is its set of filter names)."""
    lacking = [name for name in NEEDED_FOR_ANY if name not in have]
    if lacking:
        names = lacking[0] if len(lacking) == 1 else ", ".join(lacking[:-1]) + " and " + lacking[-1]
        return [f"This computer's FFmpeg lacks the {names} filter, so nothing could be measured."]
    return [
        f"This computer's FFmpeg lacks the {name} filter, so {words} are not measured (null in look.json)."
        for name, words, _ in MEASURES if name not in have
    ]


def video_chain(have):
    """The filter string of the measuring pass: thin to LOOK_FPS, shrink to LOOK_WIDTH, measure, print."""
    pieces = [f"fps={settings.LOOK_FPS}", f"scale={settings.LOOK_WIDTH}:-2"]
    pieces += [piece() for name, _, piece in MEASURES if name in have]
    pieces.append(f"metadata=mode=print:file={STATS_FILE}")
    return ",".join(pieces)


def parse_metadata(path):
    """The frames in a `metadata=mode=print` file: a list of dicts, each with `t` (seconds, None if unreadable)
    and every `key=value` line of that frame as text."""
    frames, current = [], None
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            header = HEADER.match(line)
            if header:
                current = {"t": finite(header.group(3))}
                frames.append(current)
            elif current is not None and "=" in line:
                key, value = line.rstrip("\n").split("=", 1)
                current[key] = value
    return frames


def measure_video(path, seconds, have, folder):
    """Run the measuring pass over `path` and return one dict per analysed frame: `t`, `movement`, `brightness`.

    FFmpeg runs inside `folder` (a temporary folder) so its text file has a plain fixed name. Raises
    subprocess.CalledProcessError or TimeoutExpired when FFmpeg fails; the caller turns that into unknown values.
    """
    folder = Path(folder)
    stats = folder / STATS_FILE
    stats.unlink(missing_ok=True)
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
        "-i", str(Path(path).resolve()),
        "-map", "0:v:0", "-an", "-vf", video_chain(have), "-f", "null", "-",
    ]
    subprocess.run(
        command, cwd=folder, capture_output=True, text=True, check=True, timeout=normalize.ffmpeg_timeout(seconds))
    frames = []
    for block in parse_metadata(stats):
        if block["t"] is None:
            continue
        frames.append({
            "t": block["t"],
            "movement": finite(block.get("lavfi.signalstats.YDIF")),
            "brightness": finite(block.get("lavfi.signalstats.YAVG")),
        })
    return frames


def half_count(seconds):
    """How many summary entries a clip of `seconds` has: one for every half second, at least one.

    A sliver at the end shorter than half an analysed frame makes no new entry, so 4.0 and 4.02 seconds give 8.
    """
    sliver = 1 / (2 * settings.LOOK_FPS)
    return max(1, math.ceil((seconds - sliver) / settings.SUMMARY_SECONDS))


def mean_of(values):
    """The mean of the numbers in `values`, leaving out the None ones; None when there are none."""
    kept = [value for value in values if value is not None]
    return statistics.fmean(kept) if kept else None


def summarise(frames, sound, seconds):
    """The half-second entries of a clip, in time order from t = 0.0: `t`, `movement` and `brightness`.

    `frames` are measure_video's dicts. A frame past the last half is counted in the last half. `sound` is the
    loudness series (empty until a later plan measures it). A half without frames has None for its numbers.
    """
    per_half = round(settings.SUMMARY_SECONDS * settings.LOOK_FPS)  # analysed frames in one half second
    count = half_count(seconds)
    bins = [[] for _ in range(count)]
    for frame in frames:
        index = round(frame["t"] * settings.LOOK_FPS) // per_half
        bins[min(max(index, 0), count - 1)].append(frame)
    return [
        {
            "t": rounded(index * settings.SUMMARY_SECONDS),
            "movement": rounded(mean_of(f["movement"] for f in members)),
            "brightness": rounded(mean_of(f["brightness"] for f in members)),
        }
        for index, members in enumerate(bins)
    ]


def measure_clip(path, entry, have, folder):
    """Everything look measures about one working copy.

    Returns {"halves", "overall", "shot_changes", "frames", "sound", "notes"}. If FFmpeg fails or runs too long
    every measurement is None and a note says so; the stills still go ahead (D-21).
    """
    seconds = entry["working"]["seconds"]
    notes = []
    frames = []
    pass_possible = all(name in have for name in NEEDED_FOR_ANY) and any(name in have for name, _, _ in MEASURES)
    if pass_possible:
        try:
            frames = measure_video(path, seconds, have, folder)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as error:
            if isinstance(error, OSError) and error.errno == errno.ENOSPC:
                raise
            notes.append(f"The measurements of clip {entry['letter']} could not be made.")
    return {
        "halves": summarise(frames, [], seconds),
        "overall": {"brightness": rounded(mean_of(frame["brightness"] for frame in frames))},
        "shot_changes": None,  # not measured yet
        "frames": frames,
        "sound": [],
        "notes": notes,
    }
