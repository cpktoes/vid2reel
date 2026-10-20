"""Render's tracer: a two-shot cut list over generated clips, command line to finished reel, in both shapes."""

import json
import unicodedata

import pytest
from media import index_luma, make_colour_clip, make_index_clip, make_manifest, mp4_boxes, patch_yuv, probe, sha256, stream

from v2r import settings
from v2r.__main__ import main
from v2r.render import plan

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


# ---- the frame arithmetic and the crops (pure: no FFmpeg) ----


def test_frames_round_half_up():
    assert plan.frames(2.5) == 75
    assert plan.frames(1 / 60) == 1  # exactly half a frame goes up
    assert plan.frames(0.0166) == 0
    assert plan.frames(2.49) == 75
    assert plan.frames(2.51) == 75
    assert plan.clip_frames(12.433333) == 373  # a whole clip is not given half a frame of benefit
    assert plan.clip_frames(12.437) == 373


def test_fill_region_crops_the_part_that_fills_the_canvas():
    tall, wide = settings.SHAPES["tall"], settings.SHAPES["wide"]
    sideways = plan.fill_region((640, 360), tall)
    assert sideways["crop"] == [202, 360, 218, 0]
    assert sideways["share"] == pytest.approx(0.316, abs=0.001)
    assert plan.fill_region((640, 360), tall, focus_x=0.0)["crop"][2] == 0
    assert plan.fill_region((640, 360), tall, focus_x=1.0)["crop"][2] == 438
    assert plan.fill_region((360, 640), tall, focus_x=0.1)["crop"] == [360, 640, 0, 0]  # the axis already fills
    assert plan.fill_region((360, 640), wide, focus_y=0.5)["crop"] == [360, 202, 0, 218]


def test_plan_keeps_the_lists_order_whatever_the_letters():
    manifest = {"shape": "tall", "clips": [
        {"letter": letter, "kind": "video", "working": {"file": f"{letter}.mp4", "size": [360, 640]}}
        for letter in "ABC"]}
    width, height = settings.SHAPES["tall"]
    cutlist = {"canvas": {"width": width, "height": height, "fps": settings.OUTPUT_FPS}, "segments": [
        {"clip": "C", "from": 0.0, "to": 1.0, "sound": "off"},
        {"clip": "A", "from": 1.0, "to": 3.5, "sound": "keep"},
        {"clip": "B", "from": 0.5, "to": 1.0, "sound": "off"}]}

    built = plan.plan(cutlist, manifest)

    assert [segment["clip"] for segment in built["segments"]] == ["C", "A", "B"]
    assert [segment["frames"] for segment in built["segments"]] == [30, 75, 15]
    assert [segment["reel_start"] for segment in built["segments"]] == [0, 30, 105]
    assert built["total_frames"] == 120 and built["seconds"] == 4.0


# ---- reading a list strictly (D-04, T-4-03, T-4-06) ----

DEEP = "[" * 100000
READER_ROWS = [  # (id, text of the list, the one sentence it must give, MAX_CUTLIST_BYTES to use or None)
    ("big", "{}" + " " * 1000, "The cut list is larger than 0.001 MB, so it was not read.", 1000),
    ("nan", '{"a": NaN}', "The cut list holds NaN, which is not a number a cut list may hold.", None),
    ("infinity", '{"a": Infinity}', "The cut list holds Infinity, which is not a number a cut list may hold.", None),
    ("minus infinity", '{"a": -Infinity}', "The cut list holds -Infinity, which is not a number a cut list may hold.", None),
    ("overflow", '{"a": 1e400}', "The cut list holds 1e400, which is not a number a cut list may hold.", None),
    ("long integer", '{"a": 1234567890123456}',
     "The cut list holds 1234567890123456, which is not a number a cut list may hold.", None),
    ("twice", '{"a": 1, "a": 2}', 'The cut list names "a" twice in one block; each name may appear once.', None),
    ("deep", DEEP, "The cut list is not valid JSON.", 200000),
]


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("row", READER_ROWS, ids=[row[0] for row in READER_ROWS])
def test_reader_refuses_what_a_cut_list_may_not_hold(row, shape, tmp_path, capsys, monkeypatch):
    _, text, sentence, limit = row
    work = tracer_work(tmp_path, shape)
    (work / "cutlist.json").write_text(text, encoding="utf-8")
    if limit:
        monkeypatch.setattr(settings, "MAX_CUTLIST_BYTES", limit)
    before = listing(work)

    assert main(["check", "--work", str(work)]) == 1
    lines = [line for line in capsys.readouterr().out.splitlines() if line.startswith("Problem: ")]
    assert lines == [f"Problem: {sentence}"]
    assert main(["render", "--work", str(work)]) == 1
    capsys.readouterr()
    assert listing(work) == before


def test_long_text_is_cut_in_sentences(tmp_path, capsys, monkeypatch):
    work = tracer_work(tmp_path, "tall")
    digits = "1234567890" * 6
    (work / "cutlist.json").write_text(f'{{"a": {digits}}}', encoding="utf-8")

    assert main(["check", "--work", str(work)]) == 1
    out = capsys.readouterr().out
    assert settings.CUTLIST_ECHO_CHARS == 40
    assert f"The cut list holds {digits[:40]}, which" in out
    assert digits[:41] not in out

    monkeypatch.setattr(settings, "CUTLIST_ECHO_CHARS", 10)  # read when used, never when loaded
    key = "k" * 60
    (work / "cutlist.json").write_text(f'{{"{key}": 1, "{key}": 2}}', encoding="utf-8")
    assert main(["check", "--work", str(work)]) == 1
    out = capsys.readouterr().out
    assert f'The cut list names "{key[:10]}" twice' in out and key[:11] not in out


# ---- the clips block must match the work folder (D-04) ----


def change_clip(letter, **changes):
    def edit(data, manifest, work):
        data["clips"][letter].update(changes)
    return edit


def add_clip(letter, record):
    def edit(data, manifest, work):
        data["clips"][letter] = record
    return edit


def skip_a_third_clip(data, manifest, work):
    make_manifest(work, manifest["shape"], [work / "A.mp4", work / "B.mp4", {"status": "skipped", "file": None}])
    data["clips"]["C"] = {"file": "C-original.mov", "seconds": 1.0}


def rename_key(data, manifest, work):
    data["clips"]["b"] = data["clips"].pop("B")


CLIPS_ROWS = [  # (id, edit of the list, the one sentence it must give)
    ("file", change_clip("B", file="other.mov"), "Clip B in this list was other.mov, but B in the work folder is B.mp4."),
    ("seconds", change_clip("B", seconds=2.0), "Clip B in this list is 2.00 seconds long, but B in the work folder is {B} seconds long."),
    ("unknown letter", add_clip("C", {"file": "C.mov", "seconds": 1.0}),
     "Clip C in this list is not in the work folder, which has clips A and B."),
    ("skipped letter", skip_a_third_clip,
     "Clip C was skipped when the clips were converted, so it cannot be in the list."),
    ("lower case", rename_key, 'The list\'s clips name "b"; a clip\'s name must be a capital letter such as A.'),
]


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("row", CLIPS_ROWS, ids=[row[0] for row in CLIPS_ROWS])
def test_clips_block_must_match_the_work_folder(row, shape, tmp_path, capsys):
    _, edit, sentence = row
    work = tracer_work(tmp_path, shape)
    data = json.loads((work / "cutlist.json").read_text(encoding="utf-8"))
    manifest = json.loads((work / "manifest.json").read_text(encoding="utf-8"))
    edit(data, manifest, work)
    (work / "cutlist.json").write_text(json.dumps(data), encoding="utf-8")
    manifest = json.loads((work / "manifest.json").read_text(encoding="utf-8"))
    sentence = sentence.format(B=f"{manifest['clips'][1]['working']['seconds']:.2f}")
    before = listing(work)

    assert main(["check", "--work", str(work)]) == 1
    lines = [line for line in capsys.readouterr().out.splitlines() if line.startswith("Problem: ")]
    assert lines == [f"Problem: {sentence}"]
    assert main(["render", "--work", str(work)]) == 1
    capsys.readouterr()
    assert listing(work) == before


@pytest.mark.parametrize("shape", SHAPES)
def test_a_name_equal_after_normalization_matches(shape, tmp_path, capsys):
    work = tracer_work(tmp_path, shape)
    manifest = json.loads((work / "manifest.json").read_text(encoding="utf-8"))
    manifest["clips"][1]["original"]["name"] = unicodedata.normalize("NFC", "Caf\u00e9.mov")
    (work / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    data = json.loads((work / "cutlist.json").read_text(encoding="utf-8"))
    data["clips"]["B"]["file"] = unicodedata.normalize("NFD", "Caf\u00e9.mov")
    assert data["clips"]["B"]["file"] != manifest["clips"][1]["original"]["name"]
    (work / "cutlist.json").write_text(json.dumps(data), encoding="utf-8")

    assert main(["check", "--work", str(work)]) == 0
    assert "ready to render" in capsys.readouterr().out


# ---- the cut between two touching shots of one clip (CUT-03) ----


@pytest.mark.parametrize("shape", SHAPES)
def test_touching_shots_of_one_clip_cut_cleanly(shape, tmp_path, capsys):
    work = tracer_work(tmp_path, shape, segments=[
        {"clip": "A", "from": 0.5, "to": 1.5, "sound": "keep", "why": "the first half of a stretch"},
        {"clip": "A", "from": 1.5, "to": 2.5, "sound": "keep", "why": "the second half, touching the first"},
        {"clip": "B", "from": 0.0, "to": 1.5, "sound": "off", "why": "the colour of B"},
    ])

    assert main(["render", "--work", str(work)]) == 0
    capsys.readouterr()

    (reel,) = work.glob(f"reel-{shape}-*.mp4")
    assert stream(probe(reel), "video")["nb_frames"] == "105"
    width, height = settings.SHAPES[shape]
    centre = ((width - 40) // 2, (height - 40) // 2)
    # Reel frames 29 and 30 are A's frames 44 and 45. A frame repeated at the cut would read 168 at frame 30 and a
    # dropped one 184: each 8 away from 176, at least 6 outside the tolerance. Never widen it.
    assert index_luma(44) == 168 and index_luma(45) == 176
    assert patch_yuv(reel, 29, *centre)[0] == pytest.approx(168, abs=TOLERANCE)
    assert patch_yuv(reel, 30, *centre)[0] == pytest.approx(176, abs=TOLERANCE)


@pytest.mark.parametrize("shape", SHAPES)
def test_render_refuses_on_a_missing_ffmpeg_piece(shape, tmp_path, capsys, monkeypatch):
    from v2r import render

    work = tracer_work(tmp_path, shape)
    monkeypatch.setattr(render, "RENDER_FILTERS", render.RENDER_FILTERS + ["nosuchfilter"])
    before = listing(work)

    assert main(["render", "--work", str(work)]) == 1
    err = capsys.readouterr().err
    assert "lacks the nosuchfilter filter, so nothing was built" in err
    assert listing(work) == before


# ---- what a stopped run leaves behind is swept at the start of the next one (WR-02) ----

LEFTOVERS_FILES = [
    "reel-tall-20260101-120000.part.mp4", "reel-wide-20260101-120000-2.part.mp4",
    "reel-tall-20260101-120000-cover.part.jpg", "reel-wide-20260101-120000-2-cover.part.jpg",
]
LEFTOVERS_FOLDERS = [".v2r-render-ab12_Z", ".v2r-render-x"]
MUST_STAY = [  # lookalikes and everything else a work folder holds
    "reel-tall-20260101-120000.mp4", "reel-tall-20260101-120000-cover.jpg", "reel-sideways-20260101-120000.part.mp4",
    "reel-tall-20260101-120000.part.mp4.txt", "reel-tall-notes.part.mp4", "A.part.mp4", "C-photo.part.jpg", "notes.part.mp4",
    ".v2r-render-ab12.txt", ".v2r-render-afile", ".v2r-look-ab12", "v2r-render-ab12", "look.json", "cutlist.json.part",
]


def plant_leftovers(work):
    for name in LEFTOVERS_FILES + MUST_STAY:
        if not (work / name).exists():
            (work / name).write_bytes(b"x")
    for name in LEFTOVERS_FOLDERS:
        (work / name).mkdir()
        (work / name / "piece-001.mkv").write_bytes(b"x" * 10)


@pytest.mark.parametrize("shape", SHAPES)
def test_render_sweeps_what_a_stopped_run_left_and_nothing_else(shape, tmp_path, capsys):
    work = tracer_work(tmp_path, shape)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "precious.txt").write_bytes(b"keep")
    (work / ".v2r-render-link").symlink_to(outside, target_is_directory=True)  # a link is never followed or removed
    plant_leftovers(work)
    (work / "proof").mkdir()
    (work / "proof" / "proof-09.jpg").write_bytes(b"x")  # a leftover that make_proof's own sweep owns, not this one
    fixed = {name: sha256(work / name) for name in ("A.mp4", "B.mp4", "manifest.json", "cutlist.json")}

    assert main(["render", "--work", str(work)]) == 0
    capsys.readouterr()

    names = {path.name for path in work.iterdir()}
    assert not names & set(LEFTOVERS_FILES + LEFTOVERS_FOLDERS)
    assert set(MUST_STAY) <= names
    assert (work / ".v2r-render-link").is_symlink() and (outside / "precious.txt").read_bytes() == b"keep"
    assert {name: sha256(work / name) for name in fixed} == fixed
    assert len([name for name in names if name.startswith(f"reel-{shape}-") and name.endswith(".mp4") and ".part" not in name]) >= 1


@pytest.mark.parametrize("shape", SHAPES)
def test_render_leaves_a_stopped_runs_files_alone_when_the_list_is_refused(shape, tmp_path, capsys):
    work = tracer_work(tmp_path, shape, segments=[
        {"clip": "B", "from": 0.0, "to": 5.0, "sound": "off", "why": "past the end of B"},
    ])
    plant_leftovers(work)
    before = listing(work)

    assert main(["render", "--work", str(work)]) == 1
    capsys.readouterr()

    assert listing(work) == before  # a refused list changes nothing at all


def test_the_leftover_sweep_names_are_tight(tmp_path):
    from v2r import render

    work = tmp_path / "work"
    work.mkdir()
    plant_leftovers(work)

    render.clear_leftovers(work)

    assert {path.name for path in work.iterdir()} == set(MUST_STAY)

