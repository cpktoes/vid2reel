import json

import pytest
from media import make_clip, make_manifest

import v2r.look
from v2r import settings
from v2r.__main__ import main
from v2r.look import measure, pick, sheets

CLIP_SIZE = {"tall": (360, 640), "wide": (640, 360)}  # the clip sizes swap with the shape


def no_constant(name):
    raise ValueError(f"look.json holds {name}, which is not valid JSON")


def read_look(work):
    """look.json as written to disk; NaN and Infinity are refused, as a strict JSON reader would."""
    text = (work / "look.json").read_text(encoding="utf-8")
    return json.loads(text, parse_constant=no_constant)


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_tracer_cli_one_clip_to_sheet_and_look_json(shape, tmp_path, capsys):
    from PIL import Image

    work = tmp_path / "work"
    work.mkdir()
    width, height = CLIP_SIZE[shape]
    make_clip(work / "A.mp4", width, height, seconds=4)
    make_manifest(work, shape, [work / "A.mp4"])

    assert main(["look", str(work)]) == 0

    look = read_look(work)
    assert look["version"] == 1
    assert look["shape"] == shape
    assert look["finished"] is True
    assert look["sheets"] == ["sheets/sheet-01.jpg"]
    (clip,) = look["clips"]
    assert (clip["letter"], clip["status"], clip["kind"], clip["file"]) == ("A", "done", "video", "A.mp4")
    assert clip["orientation"] == shape
    assert [half["t"] for half in clip["halves"]] == [i / 2 for i in range(8)]
    for half in clip["halves"]:
        assert isinstance(half["movement"], float)
        assert isinstance(half["brightness"], float)
    assert [still["label"] for still in clip["stills"]] == ["A 00.0", "A 01.0", "A 02.0", "A 03.0"]
    assert {still["why"] for still in clip["stills"]} == {"rhythm"}
    assert [still["cell"] for still in clip["stills"]] == [1, 2, 3, 4]
    assert {still["sheet"] for still in clip["stills"]} == {"sheets/sheet-01.jpg"}

    with Image.open(work / "sheets" / "sheet-01.jpg") as sheet:
        assert sheet.size == (settings.SHEET_WIDTH, sheets.sheet_height(shape))
        rgb = sheet.convert("RGB")
        left, top, _, _ = clip["stills"][0]["box"]
        assert all(channel < 40 for channel in rgb.getpixel((left + 2, top + 2)))  # the dark label box

    out = capsys.readouterr().out
    assert "A looked at in" in out
    assert "1 sheet so far" in out


def test_label_format():
    assert sheets.label("A", 0) == "A 00.0"
    assert sheets.label("B", 7.5) == "B 07.5"
    assert sheets.label("A", 101 / 30) == "A 03.4"
    assert sheets.label("C", 123.4) == "C 123.4"


def test_half_count():
    assert measure.half_count(4.0) == 8
    assert measure.half_count(4.02) == 8
    assert measure.half_count(4.06) == 9
    assert measure.half_count(0.01) == 1


def test_frame_number_clamps():
    assert pick.frame_number(1.0, 30, 4.0) == 30
    assert pick.frame_number(9.0, 30, 4.0) == 119  # past the end: the last frame
    assert pick.frame_number(-1.0, 30, 4.0) == 0


def test_base_times():
    assert pick.base_times(4.0, 30, 1.0) == [0.0, 1.0, 2.0, 3.0]
    assert pick.base_times(0.5, 30, 1.0) == [0.0]
