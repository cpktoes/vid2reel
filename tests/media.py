"""Helpers for tests: clips made by FFmpeg on the spot, and ffprobe readers. Nothing here is committed footage."""

import json
import subprocess

BARS = "smptehdbars=size={w}x{h}:rate={fps}:duration={s}"
BEEP = "aevalsrc='0.5*sin(2*PI*1000*t)*lt(mod(t,1),0.2)':s=48000:d={s}"  # the same beep tests/test_join.py uses
TIMEOUT = 60  # seconds: a hung FFmpeg fails one test instead of the whole suite


def make_clip(path, width, height, seconds=2, fps=30, sound=True):
    """A test clip made by FFmpeg: colour bars, plus a 1 kHz beep when `sound` is true."""
    command = ["ffmpeg", "-loglevel", "error", "-nostdin", "-f", "lavfi",
               "-i", BARS.format(w=width, h=height, fps=fps, s=seconds)]
    if sound:
        command += ["-f", "lavfi", "-i", BEEP.format(s=seconds)]
    command += ["-c:v", "libx264", "-preset", "ultrafast"]
    command += ["-c:a", "aac"] if sound else ["-an"]
    subprocess.run([*command, str(path)], check=True, timeout=TIMEOUT)
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
