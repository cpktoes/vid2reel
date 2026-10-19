import errno
import json
import subprocess

import pytest
from media import make_clip, make_manifest, sha256

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


def test_label_decimals_is_a_setting(monkeypatch):
    monkeypatch.setattr(settings, "LABEL_DECIMALS", 2)
    assert sheets.label("A", 3.25) == "A 03.25"
    assert pick.clock(4.5) == "04.50"
    monkeypatch.setattr(settings, "LABEL_DECIMALS", 0)
    assert pick.clock(4.2) == "04"


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


def make_work(tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    return work


def clip_in(work, name, shape, seconds):
    """A clip of `seconds` saved in the work folder, sized for the shape."""
    width, height = CLIP_SIZE[shape]
    return make_clip(work / name, width, height, seconds=seconds)


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_two_clips_in_letter_order(shape, tmp_path, capsys):
    work = make_work(tmp_path)
    make_manifest(work, shape, [clip_in(work, "A.mp4", shape, 3), clip_in(work, "B.mp4", shape, 2)])

    assert main(["look", str(work)]) == 0

    look = read_look(work)
    assert [clip["letter"] for clip in look["clips"]] == ["A", "B"]
    first, second = look["clips"]
    assert [still["label"] for still in first["stills"]] == ["A 00.0", "A 01.0", "A 02.0"]
    assert [still["label"] for still in second["stills"]] == ["B 00.0", "B 01.0"]
    assert len(first["halves"]) == 6
    assert len(second["halves"]) == 4
    out = capsys.readouterr().out
    assert out.index("A looked at in") < out.index("B looked at in")


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_skipped_entry_keeps_letter(shape, tmp_path):
    work = make_work(tmp_path)
    make_manifest(work, shape, [
        clip_in(work, "A.mp4", shape, 2), {"status": "skipped"}, clip_in(work, "C.mp4", shape, 2)])

    assert main(["look", str(work)]) == 0

    first, skipped, third = read_look(work)["clips"]
    assert (first["letter"], first["status"]) == ("A", "done")
    assert (skipped["letter"], skipped["number"], skipped["status"], skipped["kind"]) == ("B", 2, "skipped", None)
    assert skipped["sentence"] == "Clip B was skipped when the clips were converted, so it has no stills."
    assert "stills" not in skipped
    assert (third["letter"], third["number"], third["status"]) == ("C", 3, "done")
    assert [still["label"] for still in third["stills"]] == ["C 00.0", "C 01.0"]


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_photo_gets_one_still(shape, tmp_path):
    work = make_work(tmp_path)
    width, height = CLIP_SIZE[shape]
    clip = make_clip(work / "A.mp4", width, height, seconds=4, pattern="flat")
    make_manifest(work, shape, [{"file": clip, "kind": "photo"}])

    assert main(["look", str(work)]) == 0

    (entry,) = read_look(work)["clips"]
    assert entry["kind"] == "photo"
    assert [still["label"] for still in entry["stills"]] == ["A 00.0"]
    assert entry["overall"]["brightness"] is not None  # a photo is measured like any clip


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_bad_clip_does_not_stop_the_others(shape, tmp_path, capsys):
    work = make_work(tmp_path)
    width, height = CLIP_SIZE[shape]
    plain = {"size": [width, height], "fps": 30.0, "seconds": 2.0, "bytes": 1, "sound_added": False,
             "colour_converted": False}
    (work / "B.mp4").write_bytes(b"this is not a video" * 100)
    outside = clip_in(tmp_path, "C.mp4", shape, 2)  # a real clip, but outside the work folder
    make_manifest(work, shape, [
        {"file": None, "working": {**plain, "file": "A.mp4"}},  # the working copy is not on disk
        {"file": None, "working": {**plain, "file": "B.mp4"}},  # not a video at all
        {"file": outside, "working": {**plain, "file": "../C.mp4"}},  # not a plain name in the work folder
        clip_in(work, "D.mp4", shape, 2),
    ])

    assert main(["look", str(work)]) == 0

    clips = read_look(work)["clips"]
    assert [(clip["letter"], clip["status"]) for clip in clips] == [
        ("A", "skipped"), ("B", "skipped"), ("C", "skipped"), ("D", "done")]
    assert clips[0]["sentence"] == "The working copy of clip A is missing or not in the work folder, so it was not looked at."
    assert clips[1]["sentence"] == "Clip B could not be looked at."
    assert clips[2]["sentence"] == "The working copy of clip C is missing or not in the work folder, so it was not looked at."
    assert [still["label"] for still in clips[3]["stills"]] == ["D 00.0", "D 01.0"]
    out = capsys.readouterr().out
    assert "Clip B could not be looked at." in out


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_second_run_replaces_last_look(shape, tmp_path):
    work = make_work(tmp_path)
    make_manifest(work, shape, [clip_in(work, "A.mp4", shape, 2)])
    (work / "sheets").mkdir()
    (work / "look.json").write_text('{"old": true}', encoding="utf-8")
    (work / "look.json.tmp").write_text("half", encoding="utf-8")
    (work / "sheets" / "sheet-05.jpg").write_bytes(b"old sheet")
    (work / "sheets" / "keep.txt").write_text("mine", encoding="utf-8")
    (work / "notes.txt").write_text("mine too", encoding="utf-8")
    kept = ["manifest.json", "A.mp4", "notes.txt", "sheets/keep.txt"]
    before = {name: sha256(work / name) for name in kept}

    assert main(["look", str(work)]) == 0

    assert not (work / "sheets" / "sheet-05.jpg").exists()
    assert not (work / "look.json.tmp").exists()
    assert read_look(work)["version"] == 1
    assert {name: sha256(work / name) for name in kept} == before


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_without_manifest(shape, tmp_path, capsys):
    work = make_work(tmp_path)
    (work / "look.json").write_text('{"old": true}', encoding="utf-8")

    assert main(["look", str(work)]) == 1

    assert capsys.readouterr().err.startswith("v2r look: There is no manifest.json")
    assert (work / "look.json").read_text(encoding="utf-8") == '{"old": true}'


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_manifest_that_cannot_be_read(shape, tmp_path, capsys):
    work = make_work(tmp_path)
    (work / "manifest.json").write_text("not json at all", encoding="utf-8")
    (work / "look.json").write_text('{"old": true}', encoding="utf-8")

    assert main(["look", str(work)]) == 1

    assert "manifest.json could not be read" in capsys.readouterr().err
    assert (work / "look.json").read_text(encoding="utf-8") == '{"old": true}'


@pytest.mark.parametrize("shape", ["tall", "wide"])
@pytest.mark.parametrize("bad", [["tall"], {"tall": 1}, 7, None, "square"])
def test_run_manifest_with_a_shape_that_is_not_tall_or_wide(shape, bad, tmp_path, capsys):
    work = make_work(tmp_path)
    manifest = make_manifest(work, shape, [clip_in(work, "A.mp4", shape, 2)])
    manifest["shape"] = bad
    (work / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    assert main(["look", str(work)]) == 1  # a plain sentence, not a traceback

    assert "manifest.json could not be read" in capsys.readouterr().err
    assert not (work / "look.json").exists()


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_manifest_letter_with_a_line_break(shape, tmp_path, capsys):
    work = make_work(tmp_path)
    manifest = make_manifest(work, shape, [clip_in(work, "A.mp4", shape, 2)])
    manifest["clips"][0]["letter"] = "A\n"
    (work / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    assert main(["look", str(work)]) == 1

    assert "manifest.json could not be read" in capsys.readouterr().err


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_seconds_written_as_text_are_used_as_a_number(shape, tmp_path):
    work = make_work(tmp_path)
    width, height = CLIP_SIZE[shape]
    working = {"file": "A.mp4", "size": [width, height], "fps": 30.0, "seconds": "3.0", "bytes": 1,
               "sound_added": False, "colour_converted": False}
    clip_in(work, "A.mp4", shape, 3)
    make_manifest(work, shape, [{"file": None, "working": working}])

    assert main(["look", str(work)]) == 0

    (clip,) = read_look(work)["clips"]
    assert clip["status"] == "done" and clip["seconds"] == 3.0
    assert len(clip["halves"]) == 6 and clip["notes"] == []


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_absurd_length_in_the_manifest_is_not_believed(shape, tmp_path):
    work = make_work(tmp_path)
    width, height = CLIP_SIZE[shape]
    working = {"file": "A.mp4", "size": [width, height], "fps": 30.0, "seconds": 1e12, "bytes": 1,
               "sound_added": False, "colour_converted": False}
    clip_in(work, "A.mp4", shape, 2)
    make_manifest(work, shape, [{"file": None, "working": working}, clip_in(work, "B.mp4", shape, 2)])
    manifest = json.loads((work / "manifest.json").read_text(encoding="utf-8"))

    assert pick.still_plan(manifest["clips"], shape, 1.0) == [(shape, 2)]  # only B counts (two stills); A would loop for ever
    assert main(["look", str(work)]) == 0

    first, second = read_look(work)["clips"]
    assert (first["status"], first["sentence"]) == ("skipped", "Clip A could not be looked at.")
    assert second["status"] == "done"


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_every_entry_skipped(shape, tmp_path):
    work = make_work(tmp_path)
    make_manifest(work, shape, [{"status": "skipped"}, {"status": "skipped"}])

    assert main(["look", str(work)]) == 1

    look = read_look(work)
    assert look["finished"] is True
    assert look["sheets"] == []
    assert [clip["status"] for clip in look["clips"]] == ["skipped", "skipped"]
    assert not list((work / "sheets").glob("*")) if (work / "sheets").exists() else True


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_short_clip_one_still(shape, tmp_path):
    work = make_work(tmp_path)
    make_manifest(work, shape, [clip_in(work, "A.mp4", shape, 0.5)])

    assert main(["look", str(work)]) == 0

    (clip,) = read_look(work)["clips"]
    assert [still["label"] for still in clip["stills"]] == ["A 00.0"]
    assert len(clip["halves"]) == 1


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_stills_that_fail_keep_the_measurements(shape, tmp_path, monkeypatch):
    work = make_work(tmp_path)
    make_manifest(work, shape, [clip_in(work, "A.mp4", shape, 2)])

    def wrong_count(*args):
        raise ValueError("wrong number of stills")

    monkeypatch.setattr(sheets, "grab_stills", wrong_count)

    assert main(["look", str(work)]) == 0

    (clip,) = read_look(work)["clips"]
    assert clip["status"] == "done"
    assert len(clip["halves"]) == 4
    assert clip["notes"] == ["The stills of clip A could not be taken, so it is not on the sheets."]
    assert [(still["sheet"], still["cell"], still["box"]) for still in clip["stills"]] == [(None, None, None)] * 2


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_survives_a_clip_whose_numbers_are_not_finite(shape, tmp_path, monkeypatch, capsys):
    work = make_work(tmp_path)
    make_manifest(work, shape, [clip_in(work, "A.mp4", shape, 2), clip_in(work, "B.mp4", shape, 2)])
    real = measure.measure_clip

    def poisoned(path, entry, have, folder, seconds=None):
        measured = real(path, entry, have, folder, seconds)
        if entry["letter"] == "A":
            measured["overall"]["brightness"] = float("nan")  # whatever the source, a NaN must not reach look.json
        return measured

    monkeypatch.setattr(measure, "measure_clip", poisoned)

    assert main(["look", str(work)]) == 0

    first, second = read_look(work)["clips"]
    assert read_look(work)["finished"] is True
    assert (first["status"], first["sentence"]) == ("skipped", "Clip A could not be looked at.")
    assert second["status"] == "done"
    assert "Clip A could not be looked at." in capsys.readouterr().out


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_partial_note_and_failed_stills_keep_the_measurements(shape, tmp_path, monkeypatch):
    # a failed loudness pass is a note about one number; with failed stills it must not cost the whole clip (CR-03)
    work = make_work(tmp_path)
    make_manifest(work, shape, [clip_in(work, "A.mp4", shape, 2)])

    def no_loudness(*args):
        raise subprocess.CalledProcessError(1, "ffmpeg")

    def wrong_count(*args):
        raise ValueError("wrong number of stills")

    monkeypatch.setattr(measure, "measure_loudness", no_loudness)
    monkeypatch.setattr(sheets, "grab_stills", wrong_count)

    assert main(["look", str(work)]) == 0

    (clip,) = read_look(work)["clips"]
    assert clip["status"] == "done"
    assert len(clip["halves"]) == 4
    assert all(half["movement"] is not None for half in clip["halves"][1:])
    assert clip["notes"] == [
        "The loudness of clip A could not be measured.",
        "The stills of clip A could not be taken, so it is not on the sheets."]


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_measuring_and_stills_both_failed_skips_the_clip(shape, tmp_path, monkeypatch):
    work = make_work(tmp_path)
    make_manifest(work, shape, [clip_in(work, "A.mp4", shape, 2), clip_in(work, "B.mp4", shape, 2)])
    real_video = measure.measure_video
    real_stills = sheets.grab_stills

    def fails_for_a(path, seconds, have, folder):
        if path.name == "A.mp4":
            raise subprocess.CalledProcessError(1, "ffmpeg")
        return real_video(path, seconds, have, folder)

    def stills_fail_for_a(path, *args):
        if path.name == "A.mp4":
            raise ValueError("wrong number of stills")
        return real_stills(path, *args)

    monkeypatch.setattr(measure, "measure_video", fails_for_a)
    monkeypatch.setattr(sheets, "grab_stills", stills_fail_for_a)

    assert main(["look", str(work)]) == 0

    first, second = read_look(work)["clips"]
    assert (first["status"], first["sentence"]) == ("skipped", "Clip A could not be looked at.")
    assert second["status"] == "done" and len(second["halves"]) == 4


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_prints_each_clips_notes(shape, tmp_path, monkeypatch, capsys):
    work = make_work(tmp_path)
    make_manifest(work, shape, [clip_in(work, "A.mp4", shape, 2)])

    def no_loudness(*args):
        raise subprocess.CalledProcessError(1, "ffmpeg")

    monkeypatch.setattr(measure, "measure_loudness", no_loudness)

    assert main(["look", str(work)]) == 0

    out = capsys.readouterr().out
    assert "The loudness of clip A could not be measured." in out
    assert out.index("A looked at in") < out.index("The loudness of clip A")
    assert f"the sheets are in {work / 'sheets'}" in out


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_does_not_point_to_sheets_when_there_are_none(shape, tmp_path, monkeypatch, capsys):
    work = make_work(tmp_path)
    make_manifest(work, shape, [clip_in(work, "A.mp4", shape, 2)])
    monkeypatch.setattr(sheets, "picture_problem", lambda: "The picture library is not installed here.")

    assert main(["look", str(work)]) == 0

    out = capsys.readouterr().out
    assert "The stills of clip A could not be taken, so it is not on the sheets." in out
    assert "the sheets are in" not in out
    assert f"the measurements are in {work / 'look.json'}" in out


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_without_picture_library_still_measures(shape, tmp_path, monkeypatch):
    work = make_work(tmp_path)
    make_manifest(work, shape, [clip_in(work, "A.mp4", shape, 2)])
    problem = "The picture library is not installed here, so no contact sheets could be made."
    monkeypatch.setattr(sheets, "picture_problem", lambda: problem)

    assert main(["look", str(work)]) == 0

    look = read_look(work)
    assert problem in look["missing"]
    assert look["sheets"] == []
    (clip,) = look["clips"]
    assert len(clip["halves"]) == 4
    assert clip["notes"] == ["The stills of clip A could not be taken, so it is not on the sheets."]


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_out_of_room_stops_the_run(shape, tmp_path, monkeypatch, capsys):
    work = make_work(tmp_path)
    make_manifest(work, shape, [clip_in(work, "A.mp4", shape, 2)])

    def no_room(*args):
        raise OSError(errno.ENOSPC, "No space left on device")

    monkeypatch.setattr(sheets, "grab_stills", no_room)

    assert main(["look", str(work)]) == 1

    sentence = "The work folder ran out of room, so look stopped; the clips looked at so far are in look.json."
    assert sentence in capsys.readouterr().err
    assert read_look(work)["stopped"] == sentence


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_without_ffmpeg(shape, tmp_path, monkeypatch, capsys):
    work = make_work(tmp_path)
    make_manifest(work, shape, [clip_in(work, "A.mp4", shape, 2)])
    (work / "look.json").write_text('{"old": true}', encoding="utf-8")
    monkeypatch.setattr(v2r.look.shutil, "which", lambda name: None)

    assert main(["look", str(work)]) == 1

    assert capsys.readouterr().err == "v2r look: FFmpeg is not installed here, so nothing was looked at.\n"
    assert (work / "look.json").read_text(encoding="utf-8") == '{"old": true}'


LOOK_SETTINGS = [
    "LOOK_WIDTH", "LOOK_FPS", "SUMMARY_SECONDS", "STILL_INTERVAL_STEPS", "MAX_SHEETS_PER_RUN", "MAX_CLIP_SECONDS", "SHEET_GRID",
    "CELL_ASPECT", "SHEET_WIDTH", "SHEET_PADDING", "SHEET_BACKGROUND", "SHEET_JPEG_QUALITY", "LABEL_FONT_SHARE",
    "LABEL_PADDING", "LABEL_BOX_COLOUR", "LABEL_TEXT_COLOUR", "LABEL_DECIMALS", "LOOK_DECIMALS",
    "SHEET_JPEG_QUALITY_STEP", "SHEET_JPEG_QUALITY_MIN", "SHEET_MAX_BYTES", "EXTRAS_SHARE", "EXTRA_MIN_GAP",
    "PEAK_SPREADS", "MOVEMENT_SPREAD_FLOOR", "LOUDNESS_SPREAD_FLOOR", "SCENE_THRESHOLD", "CUT_STILL_DELAY",
    "LOUDNESS_DELAY", "SILENCE_LUFS", "DESHAKE_RANGE", "DESHAKE_CONTRAST", "SHAKE_WINDOW_SECONDS", "CAMERA_STILL_PX", "SHAKE_LIMIT_PX",
    "SUBJECT_MOVEMENT_MIN", "BLUR_SPREADS", "BLUR_SPREAD_FLOOR", "CANDIDATE_SECONDS", "CANDIDATE_STEP",
    "MAX_CANDIDATES", "CANDIDATE_MAX_SECONDS", "CANDIDATE_ALIKE_SHARE", "CHROMA_NEUTRAL",
]


def look_block_lines():
    """The lines of v2r/settings.py from the `# look:` comment up to the `# doctor` comment."""
    import pathlib

    lines = pathlib.Path(settings.__file__).read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("# look:"))
    end = next(i for i, line in enumerate(lines) if i > start and line.startswith("# doctor"))
    return lines[start:end]


def test_look_settings_have_unit_comments():
    import re

    assert len(LOOK_SETTINGS) == 44
    for name in LOOK_SETTINGS:
        assert hasattr(settings, name), f"{name} is not in v2r/settings.py"
    block = look_block_lines()
    assignments = [i for i, line in enumerate(block) if re.match(r"[A-Z][A-Z0-9_]* = ", line)]
    assert {block[i].split(" = ")[0] for i in assignments} == set(LOOK_SETTINGS)  # nothing else, nothing missing
    for i in assignments:
        assert "#" in block[i] or block[i - 1].lstrip().startswith("#"), f"no unit comment: {block[i]}"


LOOK_JSON_NAMES = [
    "version", "shape", "finished", "stopped", "rhythm", "rhythm_thinned", "missing", "sheets", "clips",
    "letter", "number", "status", "kind", "sentence", "file", "seconds", "orientation", "look_seconds", "overall",
    "halves", "shot_changes", "stills", "candidates", "notes",
    "brightness", "brightness_low", "brightness_high", "blue_shift", "red_shift", "saturation",
    "t", "movement", "camera", "shake", "camera_state", "subject", "blur", "sharp", "loudness", "shot_change",
    "label", "why", "sheet", "cell", "box",
    "rank", "start", "end", "reason",
    "LUFS",
]


def test_look_json_names_documented():
    for name in LOOK_JSON_NAMES:
        quoted = name if name == "LUFS" else f"`{name}`"  # a key is written in backticks, as in normalize's docstring
        assert quoted in v2r.look.__doc__, f"{name} is not named in the v2r.look docstring"


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_run_measuring_command_that_hangs_still_takes_the_stills(shape, tmp_path, monkeypatch):
    import types

    work = make_work(tmp_path)
    make_manifest(work, shape, [clip_in(work, "A.mp4", shape, 3)])
    monkeypatch.setattr(measure, "normalize", types.SimpleNamespace(ffmpeg_timeout=lambda seconds: 0.001))

    assert main(["look", str(work)]) == 0

    (clip,) = read_look(work)["clips"]
    assert clip["status"] == "done"
    assert clip["notes"] == ["The measurements of clip A could not be made."]
    assert all(half["movement"] is None for half in clip["halves"])
    assert clip["candidates"] == []  # nothing was measured, so no order is offered
    assert [still["sheet"] for still in clip["stills"]] == ["sheets/sheet-01.jpg"] * 3  # the stills went ahead
