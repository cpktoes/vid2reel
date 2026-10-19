"""Render's tracer: a two-shot cut list over generated clips, command line to finished reel, in both shapes."""

import json

import pytest
from media import index_luma, make_colour_clip, make_index_clip, make_manifest, mp4_boxes, patch_yuv, probe, sha256, stream

from v2r import settings
from v2r.__main__ import main

SHAPES = ["tall", "wide"]
CLIP_SIZE = {"tall": (360, 640), "wide": (640, 360)}  # the job's own orientation: portrait in a tall job, landscape in a wide one
COLOUR = (150, 90, 200)  # the (Y, U, V) of clip B
TOLERANCE = 2  # luma code values; a frame one too early or too late is 8 away, so at least 6 outside it
COLOUR_TOLERANCE = 3  # code values: a flat colour after one scale and one encode


def other_size(shape):
    """The clip size of the other orientation: sideways in a tall job, upright in a wide one."""
    width, height = CLIP_SIZE[shape]
    return height, width


def tracer_work(tmp_path, shape, segments=None):
    """A work folder with clip A (an index clip, 3 s) and clip B (one flat colour, 2.5 s) and a cut list over them.

    A is the job's own orientation and B the other one. The default list takes A from 0.5 to 2.5 seconds with its sound
    and B from 0 to 2 seconds without: 4.0 seconds, above the shortest reel render allows. Returns the work folder.
    """
    work = tmp_path / "work"
    work.mkdir()
    make_index_clip(work / "A.mp4", *CLIP_SIZE[shape], 3)
    make_colour_clip(work / "B.mp4", *other_size(shape), 2.5, COLOUR)
    manifest = make_manifest(work, shape, [work / "A.mp4", work / "B.mp4"])
    width, height = settings.SHAPES[shape]
    segments = segments or [
        {"clip": "A", "from": 0.5, "to": 2.5, "sound": "keep", "why": "the start of A"},
        {"clip": "B", "from": 0.0, "to": 2.0, "sound": "off", "why": "the colour of B"},
    ]
    cutlist = {
        "version": 1,
        "canvas": {"width": width, "height": height, "fps": settings.OUTPUT_FPS},
        "clips": {
            entry["letter"]: {"file": entry["original"]["name"], "seconds": entry["working"]["seconds"]}
            for entry in manifest["clips"]
        },
        "segments": segments,
    }
    (work / "cutlist.json").write_text(json.dumps(cutlist, indent=2), encoding="utf-8")
    return work


def listing(work):
    """Every file and folder under the work folder, by relative name."""
    return sorted(str(path.relative_to(work)) for path in work.rglob("*"))


@pytest.fixture(autouse=True)
def quick_encode(monkeypatch):
    monkeypatch.setattr(settings, "RENDER_X264_PRESET", "ultrafast")


@pytest.mark.parametrize("shape", SHAPES)
def test_tracer_two_shots_to_a_reel(shape, tmp_path, capsys):
    work = tracer_work(tmp_path, shape)
    fixed = {name: sha256(work / name) for name in ("A.mp4", "B.mp4", "manifest.json")}

    assert main(["check", "--work", str(work)]) == 0
    assert "ready to render" in capsys.readouterr().out
    assert main(["render", "--work", str(work)]) == 0
    out = capsys.readouterr().out

    (reel,) = work.glob(f"reel-{shape}-*.mp4")
    assert out.strip().splitlines()[-1] == str(reel)
    info = probe(reel)
    picture, sound = stream(info, "video"), stream(info, "audio")
    width, height = settings.SHAPES[shape]
    assert (picture["codec_name"], picture["pix_fmt"]) == ("h264", "yuv420p")
    assert (picture["width"], picture["height"]) == (width, height)
    assert picture["r_frame_rate"] == "30/1"
    assert picture["nb_frames"] == "120"
    assert (sound["codec_name"], sound["channels"], sound["sample_rate"]) == ("aac", 2, "48000")
    assert float(info["format"]["duration"]) == pytest.approx(4.0, abs=0.05)
    boxes = mp4_boxes(reel)
    assert boxes.index("moov") < boxes.index("mdat")
    assert reel.stat().st_size <= settings.MAX_RESULT_BYTES
    tags = {key.lower() for key in info["format"].get("tags", {})}
    assert not [key for key in tags if "location" in key or "com.apple" in key or "encoder" in key]

    centre = ((width - 40) // 2, (height - 40) // 2)
    for frame, source in ((0, 15), (1, 16), (59, 74)):  # A starts at 0.5 s: reel frame 0 is A's frame 15
        luma = patch_yuv(reel, frame, *centre)[0]
        assert luma == pytest.approx(index_luma(source), abs=TOLERANCE), f"reel frame {frame}"
    assert index_luma(15) == 136 and index_luma(16) == 144 and index_luma(74) == 208
    for frame in (60, 119):
        assert patch_yuv(reel, frame, *centre) == pytest.approx(COLOUR, abs=COLOUR_TOLERANCE)

    assert [path.name for path in (work / "proof").iterdir()] == ["proof-01.jpg"]
    assert not [path for path in work.iterdir() if path.name.startswith(".v2r-render-") or ".part." in path.name]
    assert {name: sha256(work / name) for name in fixed} == fixed


@pytest.mark.parametrize("shape", SHAPES)
def test_tracer_invalid_list_builds_nothing(shape, tmp_path, capsys):
    work = tracer_work(tmp_path, shape, segments=[
        {"clip": "A", "from": 0.5, "to": 2.5, "sound": "keep", "why": "the start of A"},
        {"clip": "B", "from": 0.0, "to": 5.0, "sound": "off", "why": "past the end of B"},
    ])
    before = listing(work)

    assert main(["check", "--work", str(work)]) == 1
    assert "Problem: Segment 2 ends at 5.0 seconds but clip B is only 2.5 seconds long." in capsys.readouterr().out
    assert main(["render", "--work", str(work)]) == 1
    assert "Segment 2 ends at 5.0 seconds" in capsys.readouterr().out
    assert listing(work) == before
