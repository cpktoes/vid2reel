import json
import re
import subprocess

import pytest

from v2r import settings
from v2r.join import JoinError, join

CLIP_SECONDS = 2
LONG_SECONDS = 100  # longer than the full frame size allows, so the join has to drop a step


def make_clip(path, width, height, seconds=CLIP_SECONDS):
    """A test clip made by FFmpeg: colour bars, a running clock, and a beep every second."""
    bars = (
        f"smptehdbars=size={width}x{height}:rate={settings.OUTPUT_FPS}:duration={seconds},"
        "drawtext=text='%{pts\\:hms}':fontsize=h/8:fontcolor=white:box=1:boxcolor=black:x=(w-tw)/2:y=(h-th)/2"
    )
    beep = f"aevalsrc='0.5*sin(2*PI*1000*t)*lt(mod(t,1),0.2)':s=48000:d={seconds}"
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-nostdin", "-f", "lavfi", "-i", bars, "-f", "lavfi", "-i", beep,
         "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", str(path)],
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


@pytest.fixture(scope="module")
def long_clips(tmp_path_factory):
    folder = tmp_path_factory.mktemp("long")
    return {
        "wide": make_clip(folder / "wide.mp4", 640, 360, LONG_SECONDS),
        "tall": make_clip(folder / "tall.mp4", 360, 640, LONG_SECONDS),
    }


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_join_makes_one_video_with_sound(clips, shape, tmp_path):
    result, _ = join(clips, shape, out_dir=tmp_path)

    info = probe(result)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    assert (video["width"], video["height"]) == settings.SHAPES[shape]
    assert float(info["format"]["duration"]) == pytest.approx(2 * CLIP_SECONDS, abs=0.1)
    assert any(s["codec_type"] == "audio" for s in info["streams"])
    assert peak_volume(result) > -20


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_long_join_fits_under_the_limit_at_a_smaller_frame(long_clips, shape, tmp_path):
    result, summary = join([long_clips[shape]], shape, out_dir=tmp_path)

    info = probe(result)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    full_width, full_height = settings.SHAPES[shape]
    assert result.stat().st_size <= settings.MAX_RESULT_BYTES
    assert video["width"] < full_width
    assert video["width"] / video["height"] == pytest.approx(full_width / full_height, abs=0.01)
    assert float(info["format"]["duration"]) == pytest.approx(LONG_SECONDS, abs=0.2)
    assert peak_volume(result) > -20
    assert f"{video['width']}x{video['height']}" in summary


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_too_long_to_fit_is_refused_without_building(long_clips, shape, tmp_path):
    with pytest.raises(JoinError, match="can be at most"):
        join([long_clips[shape]] * 3, shape, out_dir=tmp_path)
    assert not any(tmp_path.iterdir())
