import json
import re
import subprocess

import pytest

from v2r import settings
from v2r.join import join

CLIP_SECONDS = 2


def make_clip(path, width, height):
    """A test clip made by FFmpeg: colour bars, a running clock, and a beep every second."""
    bars = (
        f"smptehdbars=size={width}x{height}:rate={settings.OUTPUT_FPS}:duration={CLIP_SECONDS},"
        "drawtext=text='%{pts\\:hms}':fontsize=h/8:fontcolor=white:box=1:boxcolor=black:x=(w-tw)/2:y=(h-th)/2"
    )
    beep = f"aevalsrc='0.5*sin(2*PI*1000*t)*lt(mod(t,1),0.2)':s=48000:d={CLIP_SECONDS}"
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-nostdin", "-f", "lavfi", "-i", bars, "-f", "lavfi", "-i", beep,
         "-c:v", "libx264", "-c:a", "aac", str(path)],
        check=True,
    )
    return path


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(out)


def peak_volume(path):
    """The loudest moment of the sound, in dB (silence is -inf or about -91)."""
    err = subprocess.run(
        ["ffmpeg", "-nostdin", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True, check=True,
    ).stderr
    return float(re.search(r"max_volume: (\S+) dB", err).group(1))


@pytest.fixture(scope="module")
def clips(tmp_path_factory):
    folder = tmp_path_factory.mktemp("clips")
    return [make_clip(folder / "wide.mp4", 640, 360), make_clip(folder / "tall.mp4", 360, 640)]


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_join_makes_one_video_with_sound(clips, shape, tmp_path):
    result = join(clips, shape, out_dir=tmp_path)

    info = probe(result)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    assert (video["width"], video["height"]) == settings.SHAPES[shape]
    assert float(info["format"]["duration"]) == pytest.approx(2 * CLIP_SECONDS, abs=0.1)
    assert any(s["codec_type"] == "audio" for s in info["streams"])
    assert peak_volume(result) > -20
