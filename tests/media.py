"""Helpers for tests: clips made by FFmpeg on the spot, and ffprobe readers. Nothing here is committed footage."""

import json
import re
import subprocess

BARS = "smptehdbars=size={w}x{h}:rate={fps}:duration={s}"
# A black picture with a white square in the stored top-left corner, to show where a turn puts that corner.
MARKER = "color=black:size={w}x{h}:rate={fps}:duration={s},drawbox=x=0:y=0:w=120:h=120:color=white:t=fill"
BEEP = "aevalsrc='0.5*sin(2*PI*1000*t)*lt(mod(t,1),0.2)':s=48000:d={s}"  # the same beep tests/test_join.py uses
TIMEOUT = 60  # seconds: a hung FFmpeg fails one test instead of the whole suite


def run(command):
    subprocess.run(command, check=True, timeout=TIMEOUT)


def make_clip(path, width, height, seconds=2, fps=30, sound=True, rotate=None, pattern="bars", metadata=None,
              sound_seconds=None, vfr=False):
    """A test clip made by FFmpeg.

    `pattern` is "bars" (colour bars) or "marker" (black with a white corner square). `sound` adds a 1 kHz beep.
    `rotate` (90, -90 or 180) stores the clip sideways: the picture is unchanged and only the turn flag is set.
    `sound_seconds` makes the beep shorter than the picture. `vfr` drops random pictures, so the timing is uneven.
    `metadata` is a dict of tags written into the file (use a .mov name for the Apple tags).
    """
    source = (MARKER if pattern == "marker" else BARS).format(w=width, h=height, fps=fps, s=seconds)
    first = path.with_name(f"plain-{path.name}") if rotate else path
    command = ["ffmpeg", "-loglevel", "error", "-nostdin", "-f", "lavfi", "-i", source]
    if sound:
        command += ["-f", "lavfi", "-i", BEEP.format(s=sound_seconds or seconds)]
    if vfr:
        command += ["-vf", "select='gt(random(1),0.35)'", "-fps_mode", "passthrough"]
    command += ["-c:v", "libx264", "-preset", "ultrafast"]
    command += ["-c:a", "aac"] if sound else ["-an"]
    if metadata:
        for key, value in metadata.items():
            command += ["-metadata", f"{key}={value}"]
        command += ["-movflags", "use_metadata_tags"]
    run([*command, str(first)])
    if rotate:
        # -metadata:s:v rotate=... writes nothing; -display_rotation, an input option, is what stores the turn flag.
        run(["ffmpeg", "-loglevel", "error", "-nostdin", "-display_rotation", str(rotate), "-i", str(first),
             "-c", "copy", str(path)])
        first.unlink()
    return path


def probe(path):
    """ffprobe's JSON for the facts the tests look at."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=index,codec_type,codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,duration,channels,"
         "sample_rate,nb_frames,color_transfer,color_space,color_primaries:stream_side_data=rotation,side_data_type:"
         "format=duration:format_tags", "-of", "json", str(path)],
        capture_output=True, text=True, check=True, timeout=TIMEOUT,
    ).stdout
    return json.loads(out)


def stream(info, kind):
    """The first stream of `kind` ("video" or "audio") in probe() output."""
    return next(s for s in info["streams"] if s["codec_type"] == kind)


def gray_frame(path, at=0.5):
    """One picture from `path` as raw grey bytes (one byte per pixel), with its width and height."""
    video = stream(probe(path), "video")
    data = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-nostdin", "-ss", str(at), "-i", str(path), "-frames:v", "1",
         "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        capture_output=True, check=True, timeout=TIMEOUT,
    ).stdout
    return data, video["width"], video["height"]


def corner_mean(frame, width, height, corner, size=40):
    """Average brightness (0-255) of a `size` x `size` square in one corner: "top-left", "top-right", "bottom-left" or "bottom-right"."""
    top, side = corner.split("-")
    rows = range(0, size) if top == "top" else range(height - size, height)
    columns = range(0, size) if side == "left" else range(width - size, width)
    values = [frame[y * width + x] for y in rows for x in columns]
    return sum(values) / len(values)


def peak_volume(path):
    """The loudest moment of the sound, in dB (silence is -inf or about -91)."""
    err = subprocess.run(
        ["ffmpeg", "-nostdin", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True, check=True, timeout=TIMEOUT,
    ).stderr
    return float(re.search(r"max_volume: (\S+) dB", err).group(1))
