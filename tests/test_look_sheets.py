import errno
import json

import pytest
from media import make_clip, make_manifest

from v2r import doctor, settings
from v2r.__main__ import main
from v2r.look import pick, sheets

SHAPES = ["tall", "wide"]
TALL_SIZE = {"tall": (360, 640), "wide": (640, 360)}  # the job's own orientation: portrait in a tall job, landscape in a wide one


def other_size(shape):
    """The clip size of the other orientation: sideways in a tall job, upright in a wide one."""
    width, height = TALL_SIZE[shape]
    return height, width


def no_constant(name):
    raise ValueError(f"look.json holds {name}, which is not valid JSON")


def read_look(work):
    return json.loads((work / "look.json").read_text(encoding="utf-8"), parse_constant=no_constant)


def make_job(tmp_path, shape, specs):
    """A work folder with one clip per spec, each (width, height, seconds) or (width, height, seconds, kind).

    Clips are plain bars with no sound added, so they hold no sound peak, movement peak or shot change.
    """
    work = tmp_path / "work"
    work.mkdir()
    entries = []
    for index, spec in enumerate(specs):
        width, height, seconds = spec[:3]
        kind = spec[3] if len(spec) > 3 else "video"
        path = make_clip(work / f"{chr(ord('A') + index)}.mp4", width, height, seconds=seconds, sound=False)
        entries.append({"file": path, "kind": kind, "sound_added": True})
    make_manifest(work, shape, entries)
    return work


def run_look(work):
    assert main(["look", str(work)]) == 0
    return read_look(work)


def cell_rect(orientation, cell):
    """(left, top, right, bottom) of a cell on a sheet of this orientation, worked out from the settings."""
    columns, _ = settings.SHEET_GRID[orientation]
    width, height = sheets.cell_size(orientation)
    slot = cell - 1
    left = settings.SHEET_PADDING + (slot % columns) * (width + settings.SHEET_PADDING)
    top = settings.SHEET_PADDING + (slot // columns) * (height + settings.SHEET_PADDING)
    return left, top, left + width, top + height


def sheet_size(path):
    from PIL import Image

    with Image.open(path) as sheet:
        return sheet.size


@pytest.mark.parametrize("shape", SHAPES)
def test_sheets_short_clips_share_a_sheet(shape, tmp_path):
    width, height = TALL_SIZE[shape]
    work = make_job(tmp_path, shape, [(width, height, 5), (width, height, 5)])

    look = run_look(work)

    assert look["sheets"] == ["sheets/sheet-01.jpg"]
    first, second = look["clips"]
    assert [(s["sheet"], s["cell"]) for s in first["stills"]] == [("sheets/sheet-01.jpg", n) for n in range(1, 6)]
    assert [(s["sheet"], s["cell"]) for s in second["stills"]] == [("sheets/sheet-01.jpg", n) for n in range(6, 11)]
    assert [s["label"] for s in second["stills"]][0] == "B 00.0"


@pytest.mark.parametrize("shape", SHAPES)
def test_sheets_new_sheet_when_orientation_changes(shape, tmp_path):
    upright = TALL_SIZE[shape]
    sideways = other_size(shape)
    work = make_job(tmp_path, shape, [(*upright, 3), (*sideways, 3), (*upright, 3)])

    look = run_look(work)

    assert look["sheets"] == ["sheets/sheet-01.jpg", "sheets/sheet-02.jpg", "sheets/sheet-03.jpg"]
    here, there = shape, ("wide" if shape == "tall" else "tall")
    assert [clip["orientation"] for clip in look["clips"]] == [here, there, here]
    assert [clip["stills"][0]["sheet"] for clip in look["clips"]] == look["sheets"]
    assert [clip["stills"][0]["cell"] for clip in look["clips"]] == [1, 1, 1]
    for name, orientation in zip(look["sheets"], [here, there, here]):
        assert sheet_size(work / name) == (settings.SHEET_WIDTH, sheets.sheet_height(orientation))
    assert sheets.sheet_height(here) != sheets.sheet_height(there)


@pytest.mark.parametrize("shape", SHAPES)
def test_sheets_exact_fill_then_next_sheet(shape, tmp_path):
    width, height = TALL_SIZE[shape]
    columns, rows = settings.SHEET_GRID[shape]
    full = columns * rows
    first = tmp_path / "exact"
    first.mkdir()
    work = make_job(first, shape, [(width, height, full), (width, height, 3)])

    look = run_look(work)

    a, b = look["clips"]
    assert [(s["sheet"], s["cell"]) for s in a["stills"]] == [("sheets/sheet-01.jpg", n) for n in range(1, full + 1)]
    assert [(s["sheet"], s["cell"]) for s in b["stills"]] == [("sheets/sheet-02.jpg", n) for n in range(1, 4)]

    second = tmp_path / "over"
    second.mkdir()
    work = make_job(second, shape, [(width, height, full + 1)])

    look = run_look(work)

    (clip,) = look["clips"]
    assert len(clip["stills"]) == full + 1
    assert (clip["stills"][-1]["sheet"], clip["stills"][-1]["cell"]) == ("sheets/sheet-02.jpg", 1)
    assert look["sheets"] == ["sheets/sheet-01.jpg", "sheets/sheet-02.jpg"]


@pytest.mark.parametrize("shape", SHAPES)
def test_sheets_order(shape, tmp_path):
    width, height = TALL_SIZE[shape]
    work = make_job(tmp_path, shape, [(width, height, 5), (width, height, 4), (width, height, 6)])

    look = run_look(work)

    places = [
        (int(s["sheet"][-6:-4]), s["cell"]) for clip in look["clips"] for s in clip["stills"]
    ]
    assert len(places) == 15
    for (sheet_a, cell_a), (sheet_b, cell_b) in zip(places, places[1:]):
        assert sheet_b >= sheet_a
        assert cell_b == cell_a + 1 if sheet_b == sheet_a else cell_b == 1
    assert [clip["stills"][0]["label"][0] for clip in look["clips"]] == ["A", "B", "C"]
    assert look["sheets"] == ["sheets/sheet-01.jpg", "sheets/sheet-02.jpg"]


@pytest.mark.parametrize("shape", SHAPES)
def test_sheets_photo_fits_cell(shape, tmp_path):
    # a 3:4 picture (4:3 in a wide job) in a cell of the job's own shape: scaled to fit inside, centred, not stretched
    width, height = (300, 400) if shape == "tall" else (400, 300)
    work = make_job(tmp_path, shape, [(width, height, 4, "photo")])

    look = run_look(work)

    (clip,) = look["clips"]
    (still,) = clip["stills"]
    assert still["label"] == "A 00.0"
    left, top, right, bottom = still["box"]
    cell_left, cell_top, cell_right, cell_bottom = cell_rect(shape, still["cell"])
    assert cell_left <= left and top >= cell_top and right <= cell_right and bottom <= cell_bottom
    assert abs((left - cell_left) - (cell_right - right)) <= 2
    assert abs((top - cell_top) - (cell_bottom - bottom)) <= 2
    assert abs((right - left) / (bottom - top) - width / height) < 0.02
    assert (right - left) < (cell_right - cell_left) or (bottom - top) < (cell_bottom - cell_top)


@pytest.mark.parametrize("shape", SHAPES)
def test_sheets_square_follows_job_shape(shape, tmp_path):
    work = make_job(tmp_path, shape, [(400, 400, 3)])

    look = run_look(work)

    (clip,) = look["clips"]
    assert clip["orientation"] == shape
    assert sheet_size(work / look["sheets"][0]) == (settings.SHEET_WIDTH, sheets.sheet_height(shape))
    left, top, right, bottom = clip["stills"][0]["box"]
    assert right - left == bottom - top


@pytest.mark.parametrize("shape", SHAPES)
def test_sheet_bytes_guard(shape, tmp_path, monkeypatch):
    from PIL import Image

    width, height = TALL_SIZE[shape]
    plain = tmp_path / "plain"
    plain.mkdir()
    roomy = run_look(make_job(plain, shape, [(width, height, 4)]))
    normal_bytes = (plain / "work" / roomy["sheets"][0]).stat().st_size

    monkeypatch.setattr(settings, "SHEET_MAX_BYTES", 1000)  # far too small to ever be met
    tight = tmp_path / "tight"
    tight.mkdir()
    work = make_job(tight, shape, [(width, height, 4)])
    look = run_look(work)

    (name,) = look["sheets"]
    assert (work / name).stat().st_size < normal_bytes  # saved again at lower quality, and still kept
    with Image.open(work / name) as sheet:
        sheet.load()
        assert sheet.size == (settings.SHEET_WIDTH, sheets.sheet_height(shape))
    assert [still["sheet"] for still in look["clips"][0]["stills"]] == [name] * 4
    assert list((work / "sheets").glob("*.part.jpg")) == []


@pytest.mark.parametrize("shape", SHAPES)
def test_no_pillow_still_measures(shape, tmp_path, monkeypatch, capsys):
    width, height = TALL_SIZE[shape]
    work = make_job(tmp_path, shape, [(width, height, 3)])

    def no_pillow():
        raise ImportError("No module named 'PIL'")

    monkeypatch.setattr(sheets, "pillow_modules", no_pillow)

    look = run_look(work)

    assert look["sheets"] == []
    assert look["missing"] == [sheets.NO_PICTURE_LIBRARY]
    assert capsys.readouterr().out.count(sheets.NO_PICTURE_LIBRARY) == 1
    (clip,) = look["clips"]
    assert clip["status"] == "done" and len(clip["halves"]) == 6
    assert len(clip["stills"]) == 3
    assert [(s["sheet"], s["cell"], s["box"]) for s in clip["stills"]] == [(None, None, None)] * 3
    assert not (work / "sheets").exists()


@pytest.mark.parametrize("shape", SHAPES)
def test_no_select_filter(shape, tmp_path, monkeypatch, capsys):
    width, height = TALL_SIZE[shape]
    work = make_job(tmp_path, shape, [(width, height, 3)])
    real = doctor.ffmpeg_names("-filters")
    monkeypatch.setattr(doctor, "ffmpeg_names", lambda option: real - {"select"})

    look = run_look(work)

    sentence = (
        "This computer's FFmpeg lacks the select filter, so no contact sheets were made; "
        "the measurements are in look.json.")
    assert look["sheets"] == []
    assert sentence in look["missing"]
    assert capsys.readouterr().out.count(sentence) == 1
    (clip,) = look["clips"]
    assert clip["status"] == "done" and len(clip["halves"]) == 6
    assert {s["sheet"] for s in clip["stills"]} == {None}
    assert not (work / "sheets").exists()


@pytest.mark.parametrize("shape", SHAPES)
def test_no_scalable_font_sentence(shape, tmp_path, monkeypatch, capsys):
    from PIL import features

    width, height = TALL_SIZE[shape]
    work = make_job(tmp_path, shape, [(width, height, 3)])
    real_check = features.check
    monkeypatch.setattr(features, "check", lambda name, *rest: False if name == "freetype2" else real_check(name, *rest))

    look = run_look(work)

    assert look["missing"] == [sheets.NO_SCALABLE_FONT]
    assert capsys.readouterr().out.count(sheets.NO_SCALABLE_FONT) == 1
    assert look["sheets"] == ["sheets/sheet-01.jpg"]  # the sheets are still drawn
    assert [s["cell"] for s in look["clips"][0]["stills"]] == [1, 2, 3]
    assert sheet_size(work / look["sheets"][0]) == (settings.SHEET_WIDTH, sheets.sheet_height(shape))


@pytest.mark.parametrize("shape", SHAPES)
def test_out_of_room_stops_run(shape, tmp_path, monkeypatch, capsys):
    width, height = TALL_SIZE[shape]
    work = make_job(tmp_path, shape, [(width, height, 3)])

    def no_room(self):
        raise OSError(errno.ENOSPC, "No space left on device")

    monkeypatch.setattr(sheets.SheetBook, "save_current", no_room)

    assert main(["look", str(work)]) == 1

    assert "ran out of room" in capsys.readouterr().err
    look = read_look(work)
    assert "ran out of room" in look["stopped"]
    assert look["finished"] is False


# ---- stills arrive one at a time, only as many as fit, and a failed save leaves the book as it was ----


@pytest.mark.parametrize("shape", SHAPES)
def test_grab_stills_streams_in_order(shape, tmp_path):
    import inspect

    width, height = TALL_SIZE[shape]
    work = make_job(tmp_path, shape, [(width, height, 4)])
    fitted = sheets.fit_size(width, height, *sheets.cell_size(shape))

    stream = sheets.grab_stills(work / "A.mp4", [0, 0, 30, 60], fitted, 4.0)

    assert inspect.isgenerator(stream)  # nothing is read until the first picture is asked for
    pictures = list(stream)
    assert len(pictures) == 4
    assert all(picture.size == fitted for picture in pictures)
    with pytest.raises(ValueError):  # not in time order
        list(sheets.grab_stills(work / "A.mp4", [30, 0], fitted, 4.0))
    with pytest.raises(ValueError):  # a frame that is not in the clip: fewer pictures than asked for
        list(sheets.grab_stills(work / "A.mp4", [0, 5000], fitted, 4.0))


@pytest.mark.parametrize("shape", SHAPES)
def test_only_the_stills_that_fit_are_read(shape, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "MAX_SHEETS_PER_RUN", 1)
    width, height = TALL_SIZE[shape]
    columns, rows = settings.SHEET_GRID[shape]
    cells = columns * rows
    work = make_job(tmp_path, shape, [(width, height, 31)])  # 16 stills even at the widest rhythm: more than a sheet holds
    asked = []
    real = sheets.grab_stills

    def spy(path, numbers, size, seconds):
        asked.append(len(numbers))
        return real(path, numbers, size, seconds)

    monkeypatch.setattr(sheets, "grab_stills", spy)

    look = run_look(work)

    assert asked == [cells]  # not one picture more than the sheet can hold was read
    (clip,) = look["clips"]
    placed = [still for still in clip["stills"] if still["sheet"]]
    assert len(placed) == cells and len(clip["stills"]) > cells
    assert all(still["sheet"] is None and still["cell"] is None and still["box"] is None
               for still in clip["stills"][cells:])
    assert look["sheets"] == ["sheets/sheet-01.jpg"]
    assert any("Even with fewer stills" in sentence for sentence in look["missing"])


@pytest.mark.parametrize("shape", SHAPES)
def test_failed_save_leaves_the_book_as_it_was(shape, tmp_path, monkeypatch):
    width, height = TALL_SIZE[shape]
    work = make_job(tmp_path, shape, [(width, height, 3), (width, height, 3), (width, height, 2)])
    real = sheets.SheetBook.save_current
    calls = []

    def flaky(self):
        calls.append(1)
        if len(calls) == 2:  # the save that follows clip B
            raise OSError(errno.EIO, "the disk hiccuped")
        real(self)

    monkeypatch.setattr(sheets.SheetBook, "save_current", flaky)

    look = run_look(work)

    a, b, c = look["clips"]
    assert (b["status"], b["notes"]) == ("done", ["The stills of clip B could not be taken, so it is not on the sheets."])
    assert all(still["sheet"] is None for still in b["stills"])
    assert len(b["halves"]) == 6  # B's measurements stand
    assert [still["cell"] for still in a["stills"]] == [1, 2, 3]
    assert [still["cell"] for still in c["stills"]] == [4, 5]  # C starts right after A: B left no blank cells
    assert look["sheets"] == ["sheets/sheet-01.jpg"]
    assert sorted(path.name for path in (work / "sheets").iterdir()) == ["sheet-01.jpg"]


@pytest.mark.parametrize("shape", SHAPES)
def test_failed_save_after_a_sheet_was_filled_removes_its_files(shape, tmp_path, monkeypatch):
    width, height = TALL_SIZE[shape]
    columns, rows = settings.SHEET_GRID[shape]
    work = make_job(tmp_path, shape, [(width, height, columns * rows + 2)])  # runs onto a second sheet
    real = sheets.SheetBook.save_current
    calls = []

    def flaky(self):
        calls.append(1)
        if len(calls) == 2:  # the first sheet was saved when it filled; the second cannot be
            raise OSError(errno.EIO, "the disk hiccuped")
        real(self)

    monkeypatch.setattr(sheets.SheetBook, "save_current", flaky)

    look = run_look(work)

    (clip,) = look["clips"]
    assert clip["status"] == "done" and all(still["sheet"] is None for still in clip["stills"])
    assert look["sheets"] == []
    assert list((work / "sheets").iterdir()) == []  # neither the filled sheet nor a half-written one is left


@pytest.mark.parametrize("shape", SHAPES)
def test_stills_command_that_hangs_keeps_the_measurements(shape, tmp_path, monkeypatch):
    import types

    width, height = TALL_SIZE[shape]
    work = make_job(tmp_path, shape, [(width, height, 3)])
    monkeypatch.setattr(sheets, "normalize", types.SimpleNamespace(ffmpeg_timeout=lambda seconds: 0.001))

    look = run_look(work)

    (clip,) = look["clips"]
    assert clip["status"] == "done"
    assert clip["notes"] == ["The stills of clip A could not be taken, so it is not on the sheets."]
    assert len(clip["halves"]) == 6 and clip["halves"][1]["movement"] is not None
    assert look["sheets"] == []


# ---- the sheet cap: how many sheets a run needs, how the rhythm is thinned, what happens when nothing fits ----


def manifest_clip(kind, seconds, size, status="done"):
    """A manifest entry with only what the sheet arithmetic reads."""
    return {"status": status, "kind": kind, "working": {"seconds": seconds, "fps": 30.0, "size": list(size)}}


TALL, WIDE = (360, 640), (640, 360)


def test_sheets_needed_counts_cells_and_changes_of_orientation():
    assert pick.sheets_needed([]) == 0
    assert pick.sheets_needed([("tall", 1)]) == 1
    assert pick.sheets_needed([("tall", 12)]) == 1
    assert pick.sheets_needed([("tall", 13)]) == 2
    assert pick.sheets_needed([("wide", 24)]) == 2
    assert pick.sheets_needed([("tall", 5), ("tall", 7)]) == 1  # the same orientation shares a sheet
    assert pick.sheets_needed([("tall", 5), ("wide", 1)]) == 2  # a change of orientation starts a sheet
    assert pick.sheets_needed([("tall", 5), ("wide", 1), ("tall", 5)]) == 3  # tall and wide alternating
    assert pick.sheets_needed([("tall", 40), ("wide", 1), ("tall", 40)]) == 4 + 1 + 4  # a photo between two videos


def test_still_plan_counts_base_and_full_extras():
    clips = [
        manifest_clip("video", 10.0, TALL),
        manifest_clip("photo", 4.0, WIDE),
        manifest_clip("video", 5.0, TALL, status="skipped"),
        {"status": "done", "kind": "video"},  # no working copy: counts nothing
        manifest_clip("video", 10.0, (500, 500)),  # a square follows the job's shape
    ]
    # ten seconds at one a second is 10 base stills and a third of them as extras: 13; at two seconds 5 and 1
    assert pick.still_plan(clips, "wide", 1.0) == [("tall", 13), ("wide", 1), ("wide", 13)]
    assert pick.still_plan(clips, "tall", 2.0) == [("tall", 6), ("wide", 1), ("tall", 6)]


@pytest.mark.parametrize("limit, expected", [
    (4, (1.0, False)),  # 30 s at one a second: 30 + 10 = 40 stills, 4 sheets
    (3, (1.5, True)),  # at 1.5 s: 20 + 6 = 26 stills, 3 sheets
    (2, (2.0, True)),  # at 2 s: 15 + 5 = 20 stills, 2 sheets
    (1, (2.0, True)),  # nothing fits: the widest rhythm, still thinned
])
def test_run_interval_thins_until_the_run_fits(limit, expected, monkeypatch):
    monkeypatch.setattr(settings, "MAX_SHEETS_PER_RUN", limit)
    assert pick.run_interval([manifest_clip("video", 30.0, TALL)], "tall") == expected


def test_run_interval_mixed_orientations_and_a_photo(monkeypatch):
    clips = [manifest_clip("video", 30.0, TALL), manifest_clip("video", 30.0, WIDE), manifest_clip("photo", 1.0, TALL)]
    # 4 + 4 + 1 sheets at one a second; 3 + 3 + 1 at 1.5; 2 + 2 + 1 at 2
    for limit, expected in [(9, (1.0, False)), (8, (1.5, True)), (7, (1.5, True)), (6, (2.0, True)), (5, (2.0, True)),
                            (4, (2.0, True))]:
        monkeypatch.setattr(settings, "MAX_SHEETS_PER_RUN", limit)
        assert pick.run_interval(clips, "tall") == expected, limit


@pytest.mark.parametrize("shape", SHAPES)
def test_the_up_front_count_agrees_with_the_sheets_actually_made(shape, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "EXTRAS_SHARE", 0)  # plain clips add no extras, so the plan is exactly the stills
    here, there = TALL_SIZE[shape], other_size(shape)
    specs = [(*here, 5), (*there, 14), (*there, 2, "photo"), (*here, 13), (*here, 1, "photo"), (*there, 3)]
    work = make_job(tmp_path, shape, specs)
    manifest = json.loads((work / "manifest.json").read_text(encoding="utf-8"))
    planned = pick.sheets_needed(pick.still_plan(manifest["clips"], shape, 1.0))

    look = run_look(work)

    # one sheet for the 5 stills of the first clip; 14 + 1 stills of the other orientation fill two; 13 + 1 stills of
    # the first orientation again fill two; the last clip's 3 stills start a sixth
    assert len(look["sheets"]) == planned == 1 + 2 + 2 + 1


@pytest.mark.parametrize("shape", SHAPES)
def test_a_thinned_run_takes_its_stills_further_apart(shape, tmp_path, monkeypatch, capsys):
    width, height = TALL_SIZE[shape]
    monkeypatch.setattr(settings, "MAX_SHEETS_PER_RUN", 2)  # 20 s at one a second needs 3 sheets; at 1.5 s it needs 2
    work = make_job(tmp_path, shape, [(width, height, 20)])

    look = run_look(work)

    assert (look["rhythm"], look["rhythm_thinned"]) == (1.5, True)
    sentence = "There are too many stills for 2 sheets, so a still is taken every 1.5 seconds instead of every second."
    assert sentence in look["missing"]
    assert capsys.readouterr().out.count(sentence) == 1
    (clip,) = look["clips"]
    assert [still["t"] for still in clip["stills"] if still["why"] == "rhythm"][:4] == [0.0, 1.5, 3.0, 4.5]
    assert all(still["sheet"] is not None for still in clip["stills"])  # thinned enough to fit: all are drawn
    assert len(look["sheets"]) <= 2


@pytest.mark.parametrize("shape", SHAPES)
def test_a_run_that_fits_is_not_thinned(shape, tmp_path, monkeypatch):
    width, height = TALL_SIZE[shape]
    monkeypatch.setattr(settings, "MAX_SHEETS_PER_RUN", 3)
    work = make_job(tmp_path, shape, [(width, height, 20)])

    look = run_look(work)

    assert (look["rhythm"], look["rhythm_thinned"]) == (1.0, False)
    assert look["missing"] == []


@pytest.mark.parametrize("shape", SHAPES)
def test_nothing_fits_the_cap_and_the_rest_are_listed_but_not_drawn(shape, tmp_path, monkeypatch, capsys):
    width, height = TALL_SIZE[shape]
    columns, rows = settings.SHEET_GRID[shape]
    cells = columns * rows
    monkeypatch.setattr(settings, "MAX_SHEETS_PER_RUN", 1)
    work = make_job(tmp_path, shape, [(width, height, 20), (width, height, 5), (width, height, 2)])
    asked = []
    real = sheets.grab_stills

    def spy(path, numbers, size, seconds):
        asked.append((path.name, len(numbers)))
        return real(path, numbers, size, seconds)

    monkeypatch.setattr(sheets, "grab_stills", spy)

    look = run_look(work)

    assert (look["rhythm"], look["rhythm_thinned"]) == (2.0, True)
    a, b, c = look["clips"]
    assert [still["cell"] for still in a["stills"]] == list(range(1, 11))  # ten stills, two seconds apart
    assert [still["cell"] for still in b["stills"]] == [11, 12, None]  # the sheet is full after two
    assert all(still["sheet"] is None and still["box"] is None for still in c["stills"])
    assert len(c["stills"]) == 1 and c["status"] == "done"  # still listed, still measured
    assert len(c["halves"]) == 4
    assert asked == [("A.mp4", 10), ("B.mp4", 2)]  # nothing was read for C, and only two pictures for B
    assert look["sheets"] == ["sheets/sheet-01.jpg"]
    sentence = (
        "Even with fewer stills the run needs more than 1 sheets, so the stills from clip B on are listed in "
        "look.json but not on a sheet.")
    assert look["missing"].count(sentence) == 1
    assert capsys.readouterr().out.count(sentence) == 1


@pytest.mark.parametrize("shape", SHAPES)
def test_tall_and_wide_alternating_hit_the_cap_one_sheet_each(shape, tmp_path, monkeypatch):
    here, there = TALL_SIZE[shape], other_size(shape)
    monkeypatch.setattr(settings, "MAX_SHEETS_PER_RUN", 2)
    work = make_job(tmp_path, shape, [(*here, 3), (*there, 3), (*here, 3)])

    look = run_look(work)

    a, b, c = look["clips"]
    assert a["stills"][0]["sheet"] == "sheets/sheet-01.jpg" and b["stills"][0]["sheet"] == "sheets/sheet-02.jpg"
    assert all(still["sheet"] is None for still in c["stills"])  # a third sheet would pass the cap
    assert len(look["sheets"]) == 2
    assert any("the stills from clip C on" in sentence for sentence in look["missing"])
