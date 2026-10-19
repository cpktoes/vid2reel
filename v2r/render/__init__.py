"""`v2r render`: build the reel a cut list describes, in the work folder.

Render builds exactly the cut list and makes no choices of its own: nothing is trimmed, nudged, reordered or added. A
list that fails `check` builds nothing. It writes the reel (reel-SHAPE-STAMP.mp4), its proof sheets (proof/proof-NN.jpg)
and a hidden scratch folder (.v2r-render-XXXX) that is always removed, whether the run succeeds or fails.

One piece per shot is built into the scratch folder, the pieces are joined, and the reel is encoded once, under the
frame size and bitrate that join.fit gives for its length. The reel is written under a .part name, checked, and only
then given its real name.
"""

import errno
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from v2r import WORK_DIR, doctor, join, normalize, settings
from v2r.render import check, match, plan, proof, sound, video

# every piece of FFmpeg the stage's chains use; render refuses up front, in one sentence, when this computer lacks one
RENDER_ENCODERS = ["libx264", "aac", "pcm_f32le"]
RENDER_FILTERS = [
    "trim", "setpts", "crop", "scale", "setsar", "format", "setparams", "loop", "perspective", "lutyuv",
    "atrim", "asetpts", "aformat", "aresample", "anullsrc", "apad", "concat", "sine", "afade", "aevalsrc", "amultiply", "amix",
    "volume", "ebur128", "ametadata", "select",
]
RENDER_DECODERS = ["h264", "aac", "mjpeg", "pcm_f32le"]
RENDER_MUXERS = ["mp4", "matroska", "wav"]
RENDER_DEMUXERS = ["concat", "matroska,webm", "wav", "image2", "mov,mp4,m4a,3gp,3g2,mj2"]
RENDER_TEMP_PREFIX = ".v2r-render-"  # a hidden folder in the work folder holds the pieces and the sound bed
NO_FFMPEG = "FFmpeg is not installed here, so nothing was built."
OUT_OF_ROOM = "The work folder ran out of room, so the reel was not built."


class RenderError(Exception):
    """The reel can't be built; the message is one plain sentence."""


def new_path(work_dir, shape):
    """A reel name in `work_dir` that does not exist yet, nor does its .part name."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = Path(work_dir) / f"reel-{shape}-{stamp}.mp4"
    n = 2
    while path.exists() or normalize.part_path(path).exists():
        path = Path(work_dir) / f"reel-{shape}-{stamp}-{n}.mp4"
        n += 1
    return path


def run_step(command, doing, seconds, part, final=None):
    """Run one FFmpeg command that writes `part`; with `final`, a finished `part` is moved onto that name.

    Any failure leaves no `part` behind and raises RenderError in one sentence. `doing` finishes "FFmpeg failed while".
    """
    timeout = normalize.ffmpeg_timeout(seconds)
    try:
        if final is not None:
            normalize.run_ffmpeg(command, part, final, timeout)
        else:
            subprocess.run(command, capture_output=True, text=True, check=True, timeout=timeout)
    except subprocess.CalledProcessError as error:
        Path(part).unlink(missing_ok=True)
        if normalize.NO_ROOM_TEXT in (error.stderr or ""):
            raise RenderError(OUT_OF_ROOM) from error
        detail = normalize.tail(error.stderr)
        if detail:
            print(detail, flush=True)
        raise RenderError(f"FFmpeg failed while {doing}, so nothing was built.") from error
    except subprocess.TimeoutExpired as error:
        Path(part).unlink(missing_ok=True)
        raise RenderError(f"FFmpeg took longer than v2r allows while {doing}, so nothing was built.") from error
    except OSError as error:
        Path(part).unlink(missing_ok=True)
        if error.errno == errno.ENOSPC:
            raise RenderError(OUT_OF_ROOM) from error
        raise


def probe_reel(path):
    """(video codec, width, height, frames, audio codec) of a file, read with ffprobe; None for what it lacks."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,nb_frames",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True, timeout=settings.FFPROBE_TIMEOUT,
    ).stdout
    streams = json.loads(out)["streams"]
    picture = next((s for s in streams if s.get("codec_type") == "video"), {})
    sound_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
    frames = picture.get("nb_frames")
    return (
        picture.get("codec_name"), picture.get("width"), picture.get("height"),
        int(frames) if frames and str(frames).isdigit() else None, sound_stream.get("codec_name"),
    )


def self_check(part, fitted, total_frames):
    """Raise RenderError, in one sentence, when the finished file is not what the plan said it would be."""
    try:
        codec, width, height, frames, audio = probe_reel(part)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, ValueError) as error:
        raise RenderError("The reel could not be read back to check it, so it was deleted.") from error
    fault = "this is a fault in v2r, not in the cut list."
    if frames != total_frames:
        raise RenderError(f"The reel came out with {frames} frames instead of {total_frames}, so it was deleted; {fault}")
    if (width, height) != (fitted[0], fitted[1]):
        raise RenderError(
            f"The reel came out at {width}x{height} instead of {fitted[0]}x{fitted[1]}, so it was deleted; {fault}")
    if codec != "h264" or audio != "aac":
        raise RenderError(f"The reel came out with {codec} picture and {audio} sound instead of h264 and aac, so it was deleted; {fault}")


def render(cutlist_path=None, work_dir=None):
    """Build the reel a cut list describes; returns (the reel's path, the closing sentences).

    Raises RenderError, in one sentence, when nothing could be built; a list with problems builds nothing at all.
    """
    work_dir = Path(WORK_DIR if work_dir is None else work_dir)
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise RenderError(NO_FFMPEG)
    missing = doctor.missing_ffmpeg_features(
        RENDER_ENCODERS, RENDER_FILTERS, RENDER_DECODERS, muxers=RENDER_MUXERS, demuxers=RENDER_DEMUXERS)
    if missing:
        if "FFmpeg" in missing or "ffprobe" in missing:
            raise RenderError(NO_FFMPEG)
        names = missing[0] if len(missing) == 1 else ", ".join(missing[:-1]) + " and " + missing[-1]
        raise RenderError(f"This computer's FFmpeg lacks {names}, so nothing was built.")
    checked = check.check(cutlist_path, work_dir)
    for note in checked.notes:
        print(f"Note: {note}", flush=True)
    if checked.problems:
        for problem in checked.problems:
            print(f"Problem: {problem}", flush=True)
        count = len(checked.problems)
        raise RenderError(f"The cut list has {count} problem{'' if count == 1 else 's'}, so nothing was built.")

    the_plan = plan.plan(checked.cutlist, checked.manifest)
    shape, canvas, seconds = the_plan["shape"], the_plan["canvas"], the_plan["seconds"]
    segments = the_plan["segments"]
    try:
        fitted = join.fit(shape, seconds)
    except join.JoinError as error:
        raise RenderError(str(error)) from error
    width, height, _ = fitted
    print(f"Building {len(segments)} shots for a {seconds:.1f}-second {shape} reel.", flush=True)

    reel = new_path(work_dir, shape)
    part = normalize.part_path(reel)
    scratch = Path(tempfile.mkdtemp(prefix=RENDER_TEMP_PREFIX, dir=work_dir))
    finished = False
    try:
        names = []
        for segment in segments:
            name = f"piece-{segment['number']:03d}.mkv"
            final = scratch / name
            try:
                command = video.piece_command(segment, the_plan, work_dir, normalize.part_path(final))
            except ValueError as error:  # a photo's full-size copy that is not a plain file in the work folder
                raise RenderError(str(error)) from error
            run_step(
                command, f"building shot {segment['number']}", segment["frames"] / the_plan["fps"],
                normalize.part_path(final), final)
            names.append(name)
            print(f"Shot {segment['number']} of {len(segments)} built.", flush=True)
        list_path = scratch / "list.txt"
        list_path.write_text(video.concat_list(names), encoding="utf-8")

        mix = scratch / "mix.wav"
        try:
            mix_command = sound.mix_command(the_plan, work_dir, normalize.part_path(mix))
        except sound.LibraryError as error:  # the music was fine when check ran and is not now
            raise RenderError(str(error)) from error
        run_step(mix_command, "mixing the sound", seconds, normalize.part_path(mix), mix)

        # One plain gain evens the whole mix: no compression, no limiter, nothing that changes its own level over time.
        wanted = sound.sound_settings(checked.cutlist)["loudness"]
        try:
            integrated, true_peak = sound.measure_loudness(mix, scratch, seconds)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, ValueError) as error:
            raise RenderError("FFmpeg failed while measuring the sound, so nothing was built.") from error
        gain, figure, capped = sound.gain_for(integrated, true_peak, wanted, settings.TRUE_PEAK_CEILING)

        run_step(
            video.final_command(list_path, mix, fitted, gain, part, canvas=canvas), "encoding the reel", seconds, part)
        self_check(part, fitted, the_plan["total_frames"])
        size = part.stat().st_size
        if size > settings.MAX_RESULT_BYTES:
            raise RenderError(
                f"The reel came out at {size / join.MIB:.1f} MiB, over the {settings.MAX_RESULT_BYTES / join.MIB:.0f} MiB "
                "limit, so it was deleted.")
        os.replace(part, reel)
        finished = True
    finally:
        if not finished:
            part.unlink(missing_ok=True)
        shutil.rmtree(scratch, ignore_errors=True)

    sentences = []
    if (width, height) != tuple(settings.SHAPES[shape]):
        sentences.append(
            f"The reel is {join.minutes(seconds)} long, so it was made at {width}x{height} instead of "
            f"{canvas[0]}x{canvas[1]} to come back under the {settings.MAX_RESULT_BYTES / join.MIB:.0f} MiB limit.")
    made = f"Made {reel.name}: {size / join.MIB:.1f} MiB, {width}x{height}, {seconds:.1f} seconds"
    if figure is None:
        made += ", with no sound to even."
    elif capped:
        made += (
            f", sound evened to {figure:.1f} LUFS, short of the {wanted:g} LUFS target because the loudest peak "
            f"would have gone past {settings.TRUE_PEAK_CEILING:g} dBTP.")
    else:
        made += f", sound evened to {figure:.1f} LUFS."
    sentences.append(made)
    sheet_names, problem = proof.make_proof(reel, the_plan, (width, height), work_dir)
    if problem:
        sentences.append(problem)
    else:
        sentences.append(
            f"The proof sheets are in {work_dir / proof.FOLDER}: {', '.join(Path(n).name for n in sheet_names)}.")
    return reel, sentences
