"""The measuring pass: one FFmpeg run over a working copy, read back as half-second summaries.

This measures and reports; it decides nothing. A measurement that cannot be made is None, never a guess (D-21).

What the numbers in a clip's `overall` mean (Stage 16's `match` reads them to make clips sit together):
- `brightness`: the average brightness of the whole clip in 8-bit code values; 16 is black, 235 is white.
- `brightness_low` and `brightness_high`: how dark the dark parts and how bright the bright parts are (the average of
  each picture's darkest tenth and brightest tenth), same scale; far apart means a wide range of light and dark.
- `blue_shift`: above 0 the clip leans blue, below 0 it leans yellow (0 is neutral).
- `red_shift`: above 0 the clip leans red, below 0 it leans green (0 is neutral).
- `saturation`: how strong the colour is; 0 is grey, bright bars are about 40, a very vivid clip is higher.
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
MOTION_FILE = "motion.txt"  # deshake's own record of the camera's shift; its name is also written in MEASURES below
HEADER = re.compile(r"frame:(\d+)\s+pts:(-?\d+)\s+pts_time:(\S+)")

# Every measuring filter, in the order it sits in the chain: (filter name, what it measures in words, the chain piece).
# This table is the one place a measuring filter is named. The piece is built when the chain is built, from settings.
MEASURES = [
    ("signalstats", "movement, brightness and colour", lambda: "signalstats"),
    ("blurdetect", "sharpness", lambda: "blurdetect"),
    ("scdet", "shot changes", lambda: f"scdet=threshold={settings.SCENE_THRESHOLD}"),
    # deshake goes last because nothing uses its steadied picture; it is in the chain only to write its motion file.
    ("deshake", "camera movement and shake",
     lambda: f"deshake=rx={settings.DESHAKE_RANGE}:ry={settings.DESHAKE_RANGE}:filename=motion.txt"),
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


def parse_motion(path):
    """Rows of deshake's motion file, one list of 12 numbers per analysed frame (row i is frame i).

    A row is: Ori x, Avg x, Fin x, Ori y, Avg y, Fin y, then the angle and the zoom, three each. The first line of the
    file is a header and is skipped. Only the Ori columns are used, never Avg or Fin (their two-second lag would read
    the start of every pan as shake).
    """
    with open(path, encoding="utf-8", errors="replace") as handle:
        next(handle, None)
        return [[float(part) for part in line.split(",")] for line in handle if line.strip()]


def camera_and_shake(rows, skip):
    """(camera, shake) per analysed frame, each a list; None where `skip[i]` is true (a cut, or no earlier frame).

    camera is the length of the frame's shift (Ori x, Ori y); shake is how far that shift is from the centred moving
    average of the shifts around it, so a smooth pan is taken out and only jitter is left. Frames to skip are also
    left out of the average.
    """
    width = max(1, round(settings.SHAKE_WINDOW_SECONDS * settings.LOOK_FPS))
    reach = width // 2
    camera, shake = [], []
    for index, row in enumerate(rows):
        if skip[index]:
            camera.append(None)
            shake.append(None)
            continue
        near = [rows[i] for i in range(max(0, index - reach), min(len(rows), index + reach + 1)) if not skip[i]]
        mean_x = statistics.fmean(r[0] for r in near)
        mean_y = statistics.fmean(r[3] for r in near)
        camera.append(math.hypot(row[0], row[3]))
        shake.append(math.hypot(row[0] - mean_x, row[3] - mean_y))
    return camera, shake


def overall_of(blocks):
    """The `overall` dict of a clip from all its analysed frames' signalstats (each value None if not measured)."""
    def average(key):
        return mean_of(finite(block.get(key)) for block in blocks)

    def shift(value):
        return None if value is None else value - settings.CHROMA_NEUTRAL

    return {
        "brightness": rounded(average("lavfi.signalstats.YAVG")),
        "brightness_low": rounded(average("lavfi.signalstats.YLOW")),
        "brightness_high": rounded(average("lavfi.signalstats.YHIGH")),
        "blue_shift": rounded(shift(average("lavfi.signalstats.UAVG"))),
        "red_shift": rounded(shift(average("lavfi.signalstats.VAVG"))),
        "saturation": rounded(average("lavfi.signalstats.SATAVG")),
    }


def measure_video(path, seconds, have, folder):
    """Run the measuring pass over `path`; returns (frames, overall, motion_read).

    `frames` has one dict per analysed frame: `t`, `movement`, `cut` (true on the first frame of a new shot, false
    when it is not, None when scdet did not run), `camera`, `shake`, `blur` (edge width in pixels, lower is sharper)
    and `brightness`; a value not measured is None. `overall` is the clip's overall_of dict.
    `motion_read` is false when deshake ran but its motion file could not be matched to the frames.

    FFmpeg runs inside `folder` (a temporary folder) so its text files have plain fixed names. Raises
    subprocess.CalledProcessError or TimeoutExpired when FFmpeg fails; the caller turns that into unknown values.
    """
    folder = Path(folder)
    stats = folder / STATS_FILE
    stats.unlink(missing_ok=True)
    motion = folder / MOTION_FILE
    motion.unlink(missing_ok=True)
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
        "-i", str(Path(path).resolve()),
        "-map", "0:v:0", "-an", "-vf", video_chain(have), "-f", "null", "-",
    ]
    subprocess.run(
        command, cwd=folder, capture_output=True, text=True, check=True, timeout=normalize.ffmpeg_timeout(seconds))
    blocks = parse_metadata(stats)
    cut_ran = "scdet" in have
    cuts = [cut_ran and "lavfi.scd.time" in block for block in blocks]
    # The first frame has no earlier frame to be compared with, so its movement and camera shift mean nothing.
    skip = [index == 0 or cut for index, cut in enumerate(cuts)]
    camera = shake = [None] * len(blocks)
    motion_read = True
    if "deshake" in have:
        try:
            rows = parse_motion(motion)
        except (OSError, ValueError):
            rows = None
        if rows is not None and len(rows) == len(blocks) and all(len(row) == 12 for row in rows):
            camera, shake = camera_and_shake(rows, skip)
        else:
            motion_read = False
    frames = []
    for index, block in enumerate(blocks):
        if block["t"] is None:
            continue
        frames.append({
            "t": block["t"],
            "movement": None if index == 0 else finite(block.get("lavfi.signalstats.YDIF")),
            "cut": cuts[index] if cut_ran else None,
            "camera": camera[index],
            "shake": shake[index],
            "blur": finite(block.get("lavfi.blur")),  # a flat picture has no edges: nan, so None
            "brightness": finite(block.get("lavfi.signalstats.YAVG")),
        })
    return frames, overall_of(blocks), motion_read


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


def camera_state(camera, shake):
    """"shaky", "still" or "panning" from a half second's mean camera shift and mean shake; None if either is unknown."""
    if camera is None or shake is None:
        return None
    if shake >= settings.SHAKE_LIMIT_PX:
        return "shaky"
    return "still" if camera < settings.CAMERA_STILL_PX else "panning"


def summarise(frames, sound, seconds):
    """The half-second entries of a clip, in time order from t = 0.0.

    Each has `t`, `movement`, `camera`, `shake`, `camera_state`, `subject`, `blur`, `sharp`, `brightness` and
    `shot_change`. `frames` are measure_video's dicts. A frame at exactly a half's start belongs to that half, and a
    frame past the last half is counted in the last half.

    Cut frames (the first frame of a new shot) are left out of the movement, camera and shake means, because the change
    from one shot to the next is not movement; the cut itself is reported by `shot_change`. `subject` is true only
    where the camera is still and the picture moves, and None where the camera pans, shakes or was not measured, so
    camera motion is never reported as a subject moving. `blur` is the half's mean edge width and `sharp` is true
    unless that is more than BLUR_SPREADS spreads above the clip's median half (never judged against a fixed number).
    `sound` is the loudness series (empty until a later step measures it). A half without frames has None for its
    numbers.
    """
    per_half = round(settings.SUMMARY_SECONDS * settings.LOOK_FPS)  # analysed frames in one half second
    count = half_count(seconds)
    bins = [[] for _ in range(count)]
    for frame in frames:
        index = round(frame["t"] * settings.LOOK_FPS) // per_half
        bins[min(max(index, 0), count - 1)].append(frame)
    halves = []
    blurs = []
    for index, members in enumerate(bins):
        steady = [f for f in members if not f["cut"]]
        movement = mean_of(f["movement"] for f in steady)
        camera = mean_of(f["camera"] for f in steady)
        shake = mean_of(f["shake"] for f in steady)
        state = camera_state(camera, shake)
        subject = None
        if state == "still" and movement is not None:
            subject = movement >= settings.SUBJECT_MOVEMENT_MIN
        shot_change = None
        if any(f["cut"] is not None for f in members):
            shot_change = any(f["cut"] for f in members)
        blur = mean_of(f["blur"] for f in members)
        blurs.append(blur)
        halves.append({
            "t": rounded(index * settings.SUMMARY_SECONDS),
            "movement": rounded(movement),
            "camera": rounded(camera),
            "shake": rounded(shake),
            "camera_state": state,
            "subject": subject,
            "blur": rounded(blur),
            "sharp": None,
            "brightness": rounded(mean_of(f["brightness"] for f in members)),
            "shot_change": shot_change,
        })
    # Sharpness is judged against the clip's own half seconds: real footage moves only 10 to 15 percent between sharp
    # and blurred, so no fixed blur number could say "blurred".
    known = [blur for blur in blurs if blur is not None]
    if known:
        middle = statistics.median(known)
        spread = statistics.median(abs(blur - middle) for blur in known)
        limit = middle + settings.BLUR_SPREADS * max(spread, settings.BLUR_SPREAD_FLOOR)
        for half, blur in zip(halves, blurs):
            half["sharp"] = None if blur is None else blur <= limit
    return halves


def measure_clip(path, entry, have, folder):
    """Everything look measures about one working copy.

    Returns {"halves", "overall", "shot_changes", "frames", "sound", "notes"}. If FFmpeg fails or runs too long
    every measurement is None and a note says so; the stills still go ahead (D-21).
    """
    seconds = entry["working"]["seconds"]
    notes = []
    frames = []
    overall = overall_of([])
    pass_possible = all(name in have for name in NEEDED_FOR_ANY) and any(name in have for name, _, _ in MEASURES)
    if pass_possible:
        try:
            frames, overall, motion_read = measure_video(path, seconds, have, folder)
            if not motion_read:
                notes.append(f"The camera movement of clip {entry['letter']} could not be read.")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as error:
            if isinstance(error, OSError) and error.errno == errno.ENOSPC:
                raise
            notes.append(f"The measurements of clip {entry['letter']} could not be made.")
    shot_changes = None
    if frames and frames[0]["cut"] is not None:
        shot_changes = [round(f["t"], 1) for f in frames if f["cut"]]
    return {
        "halves": summarise(frames, [], seconds),
        "overall": overall,
        "shot_changes": shot_changes,
        "frames": frames,
        "sound": [],
        "notes": notes,
    }
