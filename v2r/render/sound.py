"""The sound half of `render`: the sound bed, each shot's own sound kept or silent, to the exact sample.

A picture frame is a whole number of samples (1600 at 48 kHz and 30 frames a second), so a shot's sound is cut by
sample count and every shot's sound is exactly as long as its picture.
"""

import json
import math
import subprocess
from pathlib import Path

from v2r import ROOT, normalize, settings
from v2r.look import measure
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
    shown = normalize.clean_text(music_id, settings.CUTLIST_ECHO_CHARS)  # T-4-06: cut like every echoed value
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


def music_branch(the_plan, settings_for_reel, extra_input):
    """The graph pieces that make the music: cut from `music_from`, faded, and dropped under kept sound; ends in [ducked].

    The music's first sample is round(music_from x rate) and its length is exactly the bed's, so music_from is exact to
    the sample and the music never needs looping or extending: a track too short is refused by check (D-15).
    `extra_input` is the index of the library track among the command's inputs, or None for the generated test tone.
    Every number is formatted here; the track's file reaches FFmpeg only as an input argument (T-4-01).
    """
    rate = settings.AUDIO_RATE
    seconds = the_plan["seconds"]
    length = the_plan["total_frames"] * samples_per_frame()
    first = round(settings_for_reel["music_from"] * rate)
    if extra_input is None:
        source = (
            f"sine=frequency={settings.TEST_TONE_HZ}:sample_rate={rate}:"
            f"duration={settings_for_reel['music_from'] + seconds + 1:.6f}")
    else:
        source = f"[{extra_input}:a]aresample={rate}"
    steps = [
        source,
        f"atrim=start_sample={first}:end_sample={first + length}",
        f"asetpts=N/{rate}/TB",
        f"aformat=sample_fmts=fltp:sample_rates={rate}:channel_layouts=stereo",
    ]
    fade_in, fade_out = settings_for_reel["fade_in"], settings_for_reel["fade_out"]
    if fade_in > 0:  # a fade longer than the reel covers the whole reel
        steps.append(f"afade=t=in:st=0:d={min(fade_in, seconds):.6f}")
    if fade_out > 0:
        steps.append(f"afade=t=out:st={max(0.0, seconds - fade_out):.6f}:d={min(fade_out, seconds):.6f}")
    runs = kept_runs(the_plan)
    drop = settings_for_reel["music_under_sound"]
    dropped = drop < 0 and bool(runs)
    graph = [",".join(steps) + ("[music]" if dropped else "[ducked]")]
    if dropped:
        graph.append(
            f"aevalsrc='{drop_expression(runs, drop, settings.MUSIC_DROP_RAMP)}':s={rate}:d={seconds:.6f},"
            "aformat=channel_layouts=mono[env]")
        graph.append("[music][env]amultiply[ducked]")
    return graph


def mix_command(the_plan, work_dir, output):
    """The one FFmpeg command that builds the sound of the whole reel (a float WAV) into `output`.

    The bed is the working copies of the shots whose sound is kept, read over the same stretch as their picture, and
    digital silence for the others. A working copy always carries stereo AAC (normalize adds silence where a clip had
    none), so no other case exists. With a music id, the music is laid under the whole bed (music_branch) and the two
    are added together at their own levels (normalize=0, or FFmpeg halves the bed). Raises LibraryError when the
    music cannot be read.
    """
    per_frame = samples_per_frame()
    rate = settings.AUDIO_RATE
    form = f"aformat=sample_fmts=fltp:sample_rates={rate}:channel_layouts=stereo"
    chosen = sound_settings({"sound": the_plan["sound_block"]})
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
    result = "[bed]"
    if chosen["music"] is not None:
        found = track(chosen["music"])
        extra = None
        if found["path"] is not None:
            extra = kept
            inputs += ["-i", str(found["path"])]
        branches += music_branch(the_plan, chosen, extra)
        branches.append("[bed][ducked]amix=inputs=2:duration=first:normalize=0[mix]")
        result = "[mix]"
    return [
        *video.QUIET, "-y",
        *inputs,
        "-filter_complex", ";".join(branches),
        "-map", result, "-c:a", "pcm_f32le", "-ar", str(rate), "-ac", "2",
        str(output),
    ]


def measure_loudness(mix_path, folder, seconds):
    """(integrated loudness in LUFS, loudest true peak as a multiplier) of the mix file, read with FFmpeg's ebur128.

    One run with its working folder set to `folder`, the readings printed to the fixed name loud.txt there, so no name
    of the user's is ever in a filter. The last reading printed is the whole mix's. Either value is None when it is
    not a number. Raises subprocess.CalledProcessError or TimeoutExpired when FFmpeg fails, and ValueError when it
    printed no reading.
    """
    folder = Path(folder)
    loud = folder / measure.LOUD_FILE
    loud.unlink(missing_ok=True)
    command = [
        *video.QUIET, "-y", "-i", str(Path(mix_path).resolve()),
        "-af", f"ebur128=peak=true:metadata=1,ametadata=mode=print:file={measure.LOUD_FILE}", "-f", "null", "-",
    ]
    subprocess.run(
        command, cwd=folder, capture_output=True, text=True, check=True, timeout=normalize.ffmpeg_timeout(seconds))
    blocks = measure.parse_metadata(loud) if loud.is_file() else []
    loud.unlink(missing_ok=True)
    if not blocks:
        raise ValueError("FFmpeg printed no loudness reading.")
    last = blocks[-1]
    return measure.finite(last.get("lavfi.r128.I")), measure.finite(last.get("lavfi.r128.true_peak"))
