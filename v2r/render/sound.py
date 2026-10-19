"""The sound half of `render`: the sound bed, each shot's own sound kept or silent, to the exact sample.

A picture frame is a whole number of samples (1600 at 48 kHz and 30 frames a second), so a shot's sound is cut by
sample count and every shot's sound is exactly as long as its picture.
"""

import json
import math
from pathlib import Path

from v2r import ROOT, normalize, settings
from v2r.render import plan, video

MUSIC_DIR = ROOT / "music"  # read when called, so a test can point it at a folder of its own


class LibraryError(Exception):
    """The music cannot be used; the message is one plain sentence."""


def sound_settings(cutlist):
    """The reel's music and loudness choices: the list's own where it states one, else the setting (D-07, D-14, D-16).

    Returns music (a track id or None), music_from, fade_in and fade_out (seconds), music_under_sound (decibels, 0.0
    meaning no drop) and loudness (LUFS). Every default is read now, never when the module was loaded.
    """
    block = cutlist.get("sound") or {}

    def stated(name, default):
        value = block.get(name)
        return default if value is None else value

    return {
        "music": block.get("music"),
        "music_from": stated("music_from", 0.0),
        "fade_in": stated("fade_in", settings.FADE_IN_SECONDS),
        "fade_out": stated("fade_out", settings.FADE_OUT_SECONDS),
        "music_under_sound": stated("music_under_sound", 0.0),
        "loudness": stated("loudness", settings.LOUDNESS_TARGET),
    }


def kept_runs(the_plan):
    """(start, end) in seconds of every stretch of kept sound, in reel order (CUT-06).

    Kept segments that touch (one begins on the frame the one before it ends) are one run, so the music drops once
    across them and does not rise at the cut between them.
    """
    runs = []  # [first frame, frame after the last]
    for segment in the_plan["segments"]:
        if segment["sound"] != "keep":
            continue
        end = segment["reel_start"] + segment["frames"]
        if runs and runs[-1][1] == segment["reel_start"]:
            runs[-1][1] = end
        else:
            runs.append([segment["reel_start"], end])
    fps = settings.OUTPUT_FPS
    return [(first / fps, last / fps) for first, last in runs]


def _need_ramp(ramp):
    if not ramp > 0:
        raise ValueError("The music's drop time must be above zero.")


def gain_at(t, runs, db, ramp):
    """The music's gain (a multiplier) at time `t`: the pure reference of what drop_expression asks FFmpeg for.

    The music sits `db` decibels down for the whole of every run, reaches that `ramp` seconds before the run starts
    and comes back over `ramp` seconds after it ends, so the ramps lie outside the kept stretch.
    """
    _need_ramp(ramp)
    if not runs or db == 0:
        return 1.0
    depth = max(
        plan.clamp(min((t - (start - ramp)) / ramp, ((end + ramp) - t) / ramp), 0.0, 1.0) for start, end in runs)
    return 10 ** (db * depth / 20)


def drop_expression(runs, db, ramp):
    """gain_at as an aevalsrc expression in `t`; every number in it is formatted here (T-4-01)."""
    _need_ramp(ramp)
    depths = [
        f"clip(min((t-({start - ramp:.6f}))/{ramp:.6f},(({end + ramp:.6f})-t)/{ramp:.6f}),0,1)"
        for start, end in runs
    ]
    combined = depths[-1]
    for depth in reversed(depths[:-1]):
        combined = f"max({depth},{combined})"
    return f"pow(10,({db:.6f})*({combined})/20)"


def gain_for(integrated, true_peak, target, ceiling):
    """(gain in dB, the loudness the mix will have, whether the peak ceiling stopped the gain) for a measured mix.

    One plain gain moves the integrated loudness to `target`, but never so far that the loudest true peak (a
    multiplier) would pass `ceiling` dBTP. A mix at or below silence gets no gain and no figure (D-14).
    """
    if integrated is None or integrated <= settings.SILENCE_LUFS:
        return 0.0, None, False
    wanted = target - integrated
    gain, capped = wanted, False
    if true_peak is not None and true_peak > 0:
        room = ceiling - 20 * math.log10(true_peak)
        if room < wanted:
            gain, capped = room, True
    return gain, integrated + gain, capped


def read_library(music_dir=None):
    """{track id: {"file", "seconds"}} from music/library.json; {} when there is no such file.

    Stage 18 defines the rest of the file; this expects {"tracks": [{"id", "file", "seconds", ...}]}.
    """
    folder = Path(MUSIC_DIR if music_dir is None else music_dir)
    path = folder / "library.json"
    if not path.is_file():
        return {}
    broken = LibraryError("music/library.json could not be read, so the music cannot be checked.")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise broken from error
    tracks = data.get("tracks") if isinstance(data, dict) else None
    if not isinstance(tracks, list):
        raise broken
    library = {}
    for item in tracks:
        if not isinstance(item, dict):
            raise broken
        track_id, name, seconds = item.get("id"), item.get("file"), item.get("seconds")
        plain = isinstance(name, str) and name and not name.startswith(".") and Path(name).name == name
        length = (
            seconds if isinstance(seconds, (int, float)) and not isinstance(seconds, bool) and math.isfinite(seconds)
            else None)
        if not isinstance(track_id, str) or not plain or length is None or length <= 0:
            raise broken
        library[track_id] = {"file": name, "seconds": seconds}
    return library


def track(music_id, music_dir=None):
    """{"id", "seconds", "path"} of a music track; `path` is None for the generated test tone. Raises LibraryError.

    A library track's file must be a plain name directly inside the music folder and must exist (T-4-02).
    """
    if music_id == settings.TEST_TONE_ID:
        return {"id": music_id, "seconds": settings.TEST_TONE_SECONDS, "path": None}
    folder = Path(MUSIC_DIR if music_dir is None else music_dir)
    library = read_library(folder)
    shown = normalize.clean_text(music_id)
    entry = library.get(music_id) if isinstance(music_id, str) else None
    if entry is None:
        reason = "" if (folder / "library.json").is_file() else (
            f'; there is no music/library.json yet, so only "{settings.TEST_TONE_ID}" can be used')
        raise LibraryError(f'The music track "{shown}" is not in music/library.json{reason}.')
    path = (folder.resolve() / entry["file"]).resolve()
    if path.parent != folder.resolve() or not path.is_file():
        raise LibraryError(f'The music file for "{shown}" is missing from music/.')
    return {"id": music_id, "seconds": entry["seconds"], "path": path}


def samples_per_frame():
    """Samples of sound in one picture frame; ValueError when the sound rate is not a whole multiple of the frame rate."""
    if settings.AUDIO_RATE % settings.OUTPUT_FPS:
        raise ValueError("The sound rate is not a whole number of samples per picture frame.")
    return settings.AUDIO_RATE // settings.OUTPUT_FPS


def mix_command(the_plan, work_dir, output):
    """The one FFmpeg command that builds the sound bed (a float WAV) of the whole reel into `output`.

    The inputs are the working copies of the shots whose sound is kept, read over the same stretch as their picture.
    A working copy always carries stereo AAC (normalize adds silence where a clip had none), so no other case exists.
    """
    per_frame = samples_per_frame()
    rate = settings.AUDIO_RATE
    form = f"aformat=sample_fmts=fltp:sample_rates={rate}:channel_layouts=stereo"
    inputs, branches, labels = [], [], []
    kept = 0  # inputs given so far
    for index, segment in enumerate(the_plan["segments"]):
        length = segment["frames"] * per_frame
        if segment["sound"] == "keep":
            _, skip = plan.seek(segment["start_frame"])
            seek, window = video.source_window(segment, the_plan)
            source = Path(work_dir).resolve() / segment["working"]
            inputs += ["-ss", f"{seek:.6f}", "-t", f"{window:.6f}", "-i", str(source)]
            kept += 1
            branches.append(
                f"[{kept - 1}:a]atrim=start_sample={skip * per_frame}:end_sample={skip * per_frame + length},"
                f"asetpts=N/{rate}/TB,{form},apad=whole_len={length},atrim=end_sample={length}[s{index}]")
        else:
            branches.append(f"anullsrc=r={rate}:cl=stereo,atrim=end_sample={length},{form}[s{index}]")
        labels.append(f"[s{index}]")
    branches.append(f"{''.join(labels)}concat=n={len(labels)}:v=0:a=1[bed]")
    return [
        *video.QUIET, "-y",
        *inputs,
        "-filter_complex", ";".join(branches),
        "-map", "[bed]", "-c:a", "pcm_f32le", "-ar", str(rate), "-ac", "2",
        str(output),
    ]
