import json

import pytest
from media import corner_mean, gray_frame, make_clip, probe, stream

import v2r.normalize
from v2r import settings
from v2r.__main__ import main
from v2r.normalize import frame_facts, hdr_kind, normalize, working_size

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


def convert(clips, shape, out_dir):
    """Normalize `clips` into `out_dir` and return the manifest as written to disk."""
    normalize(clips, shape, out_dir=out_dir)
    return json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("shape", "source", "expected"),
    [
        ("tall", (2160, 3840), (1080, 1920)),  # the 4K iPhone clip, stored sideways
        ("tall", (3840, 2160), (3412, 1920)),
        ("tall", (1920, 1080), (1920, 1080)),  # never scaled up
        ("tall", (4284, 5712), (1080, 1440)),  # a 24 MP photo
        ("wide", (3840, 2160), (1920, 1080)),
        ("wide", (2160, 3840), (1920, 3412)),
        ("wide", (1080, 1920), (1080, 1920)),  # never scaled up
        ("tall", (641, 361), (640, 360)),  # an odd size floors to even
        ("wide", (641, 361), (640, 360)),
        ("tall", (1080, 1920), (1080, 1920)),  # exactly at the cap keeps its size
        ("wide", (1920, 1080), (1920, 1080)),
        ("tall", (2000, 2000), (1080, 1080)),  # a square uses its own shape's entry
        ("wide", (2000, 2000), (1080, 1080)),
    ],
)
def test_working_size_table(shape, source, expected):
    assert working_size(shape, *source) == expected


def test_facts_frame_timing():
    assert frame_facts([i / 30 for i in range(60)]) == (30.0, True, False)
    assert frame_facts([i / 120 for i in range(240)])[2] is True
    assert frame_facts([0.0]) == (None, True, False)
    assert frame_facts([]) == (None, True, False)
    mixed = [0.0, 0.033, 0.099, 0.132, 0.198, 0.231, 0.264, 0.33]  # gaps of 33 ms and 66 ms
    assert frame_facts(mixed)[1] is False


@pytest.mark.parametrize(
    ("tags", "expected"),
    [
        ({"color_transfer": "arib-std-b67", "color_primaries": "bt2020"}, "hlg"),
        ({"color_transfer": "smpte2084"}, "pq"),
        ({"color_transfer": "unknown", "color_primaries": "bt2020"}, "bt2020"),
        ({"color_primaries": "bt2020"}, "bt2020"),
        ({"color_transfer": "bt709", "color_primaries": "bt709"}, None),
        ({"color_transfer": "unknown", "color_primaries": "unknown"}, None),
        ({}, None),
    ],
)
def test_facts_hdr_kind_table(tags, expected):
    assert hdr_kind(tags) == expected


@pytest.mark.parametrize("shape", ["tall", "wide"])
@pytest.mark.parametrize(("rotation", "bright", "dark"), [(90, "bottom-left", "top-right"), (-90, "top-right", "bottom-left")])
def test_upright_sideways_clip_marker(shape, rotation, bright, dark, tmp_path):
    clip = make_clip(tmp_path / "side.mp4", 640, 360, pattern="marker", sound=True, rotate=rotation)
    assert stream(probe(clip), "video")["side_data_list"][0]["rotation"] == rotation  # the test clip really is sideways

    entry = convert([clip], shape, tmp_path / "out")["clips"][0]

    assert entry["original"]["rotation"] == rotation
    assert entry["original"]["stored_size"] == [640, 360]
    assert entry["original"]["upright_size"] == [360, 640]
    assert entry["working"]["size"] == list(working_size(shape, 360, 640))
    working = tmp_path / "out" / "A.mp4"
    assert "side_data_list" not in stream(probe(working), "video")
    frame, width, height = gray_frame(working)
    assert corner_mean(frame, width, height, bright) > 200
    assert corner_mean(frame, width, height, dark) < 50


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_facts_shot_at(shape, tmp_path):
    both = make_clip(tmp_path / "both.mov", 320, 180, metadata={
        "creation_time": "2026-10-12T18:49:03Z", "com.apple.quicktime.creationdate": "2026-10-12T11:49:03-0700"})
    only = make_clip(tmp_path / "only.mov", 320, 180, metadata={"creation_time": "2026-10-12T18:49:03Z"})

    clips = convert([both, only], shape, tmp_path / "out")["clips"]

    assert clips[0]["original"]["shot_at"] == "2026-10-12T11:49:03-0700"
    assert clips[1]["original"]["shot_at"].startswith("2026-10-12T18:49:03")


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_facts_full_fact_sheet(shape, tmp_path):
    clip = make_clip(tmp_path / "in.mp4", 320, 180)

    original = convert([clip], shape, tmp_path / "out")["clips"][0]["original"]

    assert set(original) == {"path", "name", "bytes", "seconds", "stored_size", "rotation", "upright_size", "fps",
                             "fps_steady", "slow_motion", "hdr", "dolby_vision", "has_sound", "shot_at"}
    assert original["path"] == str(clip.resolve())
    assert original["bytes"] == clip.stat().st_size
    assert original["has_sound"] is True
    assert original["hdr"] is None
    assert original["dolby_vision"] is False
    assert original["rotation"] == 0
    assert original["fps"] == pytest.approx(30, abs=0.1)
    assert original["fps_steady"] is True
    assert original["slow_motion"] is False
    assert original["seconds"] == pytest.approx(2.0, abs=0.1)


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_facts_awkward_file_name(shape, tmp_path):
    clip = make_clip(tmp_path / "-my clip \u00e9.mov", 320, 180)

    manifest = convert([clip], shape, tmp_path / "out")

    assert manifest["clips"][0]["status"] == "done"
    assert manifest["clips"][0]["original"]["name"] == "-my clip \u00e9.mov"


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_facts_one_frame_clip(shape, tmp_path):
    clip = make_clip(tmp_path / "one.mp4", 320, 180, seconds=0.03)
    assert stream(probe(clip), "video")["nb_frames"] == "1"

    entry = convert([clip], shape, tmp_path / "out")["clips"][0]

    assert entry["status"] == "done"
    assert entry["original"]["fps_steady"] is True
    assert entry["original"]["slow_motion"] is False
