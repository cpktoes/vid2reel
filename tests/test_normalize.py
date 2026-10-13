import json

import pytest
from media import make_clip, probe, stream

import v2r.normalize
from v2r import settings
from v2r.__main__ import main
from v2r.normalize import working_size

SMALL_CAPS = {
    "tall": {"portrait": (180, 320), "landscape": (None, 320)},
    "wide": {"landscape": (320, 180), "portrait": (320, None)},
}


@pytest.fixture
def small_caps(monkeypatch):
    """Small working sizes, so test clips stay tiny and the two shapes still give different sizes."""
    monkeypatch.setattr(settings, "WORKING_SIZE", SMALL_CAPS)


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_tracer_cli_one_clip_to_working_copy_and_manifest(shape, tmp_path, monkeypatch, capsys, small_caps):
    monkeypatch.setattr(v2r.normalize, "WORK_DIR", tmp_path)
    clip = make_clip(tmp_path / "in.mp4", 640, 360)

    assert main(["normalize", "--shape", shape, str(clip)]) == 0

    info = probe(tmp_path / "A.mp4")
    video, audio = stream(info, "video"), stream(info, "audio")
    assert video["codec_name"] == "h264"
    assert video["pix_fmt"] == "yuv420p"
    assert video["r_frame_rate"] == "30/1"
    assert (video["width"], video["height"]) == working_size(shape, 640, 360)
    assert "side_data_list" not in video
    assert audio["codec_name"] == "aac"
    assert audio["channels"] == 2
    assert int(audio["sample_rate"]) == 48000
    assert float(video["duration"]) == pytest.approx(2.0, abs=0.1)
    assert float(audio["duration"]) == pytest.approx(2.0, abs=0.1)

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == 1
    assert manifest["shape"] == shape
    assert manifest["finished"] is True
    (entry,) = manifest["clips"]
    assert (entry["letter"], entry["number"], entry["status"], entry["kind"]) == ("A", 1, "done", "video")
    assert entry["working"]["file"] == "A.mp4"
    assert isinstance(entry["convert_seconds"], (int, float))
    assert "A done in" in capsys.readouterr().out


def test_tracer_shape_is_required(tmp_path):
    clip = make_clip(tmp_path / "in.mp4", 640, 360)
    with pytest.raises(SystemExit) as stopped:
        main(["normalize", str(clip)])
    assert stopped.value.code == 2
