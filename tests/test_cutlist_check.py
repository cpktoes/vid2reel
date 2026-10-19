"""The cut list's rulebook (schema/cutlist.schema.json) and `check`'s sentences about it, in both shapes."""

import copy
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from types import SimpleNamespace

import pytest
from cutlists import EXAMPLES, clips_block, placeholder_work, segment, touch_up, write_list
from jsonschema import Draft202012Validator

from v2r import join, settings
from v2r.__main__ import main
from v2r.render import check, sound

SHAPES = ["tall", "wide"]
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema" / "cutlist.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def errors_of(data):
    return list(Draft202012Validator(SCHEMA).iter_errors(data))


# ---- the rulebook file ----


def test_schema_is_a_valid_draft_2020_12_schema():
    Draft202012Validator.check_schema(SCHEMA)
    assert SCHEMA["$schema"] == "https://json-schema.org/draft/2020-12/schema"


@pytest.mark.parametrize("shape", SHAPES)
def test_both_examples_pass_the_schema(shape, tmp_path):
    _, manifest = placeholder_work(tmp_path, shape)
    assert errors_of(EXAMPLES[shape](clips_block(manifest))) == []


@pytest.mark.parametrize("shape", SHAPES)
def test_one_segment_list_passes_the_schema(shape, tmp_path):
    _, manifest = placeholder_work(tmp_path, shape)
    width, height = settings.SHAPES[shape]
    data = {
        "version": 1,
        "canvas": {"width": width, "height": height, "fps": settings.OUTPUT_FPS},
        "clips": clips_block(manifest),
        "segments": [segment("A", 0.0, 3.0, "keep", "A 00.0 to A 03.0: the start")],
    }
    assert errors_of(data) == []


def test_schema_holds_no_settings_numbers():
    text = SCHEMA_PATH.read_text(encoding="utf-8")
    for number in ("1080", "1920", "0.92", "1.08", "-14", "0.04"):
        assert number not in text


@pytest.mark.parametrize("shape", SHAPES)
def test_schema_leaves_unknown_fields_open(shape, tmp_path):
    _, manifest = placeholder_work(tmp_path, shape)
    data = EXAMPLES[shape](clips_block(manifest))
    data["colour"] = "warm"
    data["segments"][0]["zoom"] = 2
    assert errors_of(data) == []


# ---- check's sentences about the rulebook ----


RULE_NOTE = re.compile(
    r"There is no touch-up in the list|Segment \d+: \w+ is a photo with no move|(Clip|Photo) \w+ is (sideways|upright) in a "
    r"(tall|wide) frame|This reel has no sound at all")


def run_check(work, data, capsys, name="cutlist.json", all_notes=False):
    """Write the list, run `check`, and return (exit code, problem sentences, note sentences).

    The notes about the rules (no touch-up, a photo with no move, a crop that keeps little, no sound) are left out
    unless `all_notes` is true, so the tests of the field notes read the same for every list.
    """
    path = write_list(work, data, name)
    before, files = path.read_bytes(), listing(work)
    code = main(["check", str(path), "--work", str(work)])
    lines = capsys.readouterr().out.splitlines()
    assert path.read_bytes() == before  # check only reads the list (T-4-12)
    assert listing(work) == files  # and writes nothing anywhere
    problems = [line.removeprefix("Problem: ") for line in lines if line.startswith("Problem: ")]
    notes = [line.removeprefix("Note: ") for line in lines if line.startswith("Note: ")]
    return code, problems, notes if all_notes else [note for note in notes if not RULE_NOTE.match(note)]


def listing(work):
    return sorted(str(path.relative_to(work)) for path in work.rglob("*"))


def set_in(*path, value):
    def apply(data):
        target = data
        for part in path[:-1]:
            target = target[part]
        target[path[-1]] = value
    return apply


def delete_in(*path):
    def apply(data):
        target = data
        for part in path[:-1]:
            target = target[part]
        del target[path[-1]]
    return apply


def rename_clip_key(data):
    data["clips"]["b"] = data["clips"].pop("B")


def add_cover(data):
    data["cover"] = {"segment": 0, "at": 1.0}


FAULTS = [  # (id, edit of a valid list, the one sentence it must give)
    ("version", set_in("version", value=2), "The list's version is 2; this renderer reads version 1."),
    ("version true", set_in("version", value=True), "The list's version is true; this renderer reads version 1."),
    ("canvas width as text", set_in("canvas", "width", value="1080"), "The canvas's width must be a whole number."),
    ("canvas width zero", set_in("canvas", "width", value=0), "The canvas's width is 0; it must be more than 0."),
    ("no segments", set_in("segments", value=[]), "The list has no segments."),
    ("segments not a list", set_in("segments", value="x"), "The list's segments must be a list."),
    ("no clips", set_in("clips", value={}),
     "The list's clips are empty; copy each clip's letter, file and length from the manifest."),
    ("segment without to", delete_in("segments", 3, "to"), "Segment 4 has no to."),
    ("focus too big", set_in("segments", 0, "focus_x", value=1.5),
     "Segment 1's focus_x is 1.5; it must be between 0 and 1."),
    ("focus below zero", set_in("segments", 0, "focus_y", value=-0.25),
     "Segment 1's focus_y is -0.25; it must be between 0 and 1."),
    ("move zoom", set_in("segments", 0, "move", value="zoom"),
     "Segment 1's move is \"zoom\"; it must be one of none, push-in, pull-out, pan-left or pan-right."),
    ("sound on", set_in("segments", 0, "sound", value="on"), "Segment 1's sound is \"on\"; it must be one of keep or off."),
    ("segment clip lower case", set_in("segments", 0, "clip", value="a"),
     "Segment 1's clip is \"a\"; a clip's name must be a capital letter such as A."),
    ("clips key lower case", rename_clip_key,
     "The list's clips name \"b\"; a clip's name must be a capital letter such as A."),
    ("filter warm", set_in("look", "filter", value="warm"), "The look's filter is \"warm\"; only \"none\" can be built until Stage 21."),
    ("music under sound above zero", set_in("sound", "music_under_sound", value=3),
     "The sound's music_under_sound is 3; it must be at most 0."),
    ("loudness above zero", set_in("sound", "loudness", value=0.5), "The sound's loudness is 0.5; it must be at most 0."),
    ("music a number", set_in("sound", "music", value=7), "The sound's music must be text or null."),
    ("fade in below zero", set_in("sound", "fade_in", value=-1), "The sound's fade_in is -1; it must be at least 0."),
    ("cover segment zero", add_cover, "The cover's segment is 0; it must be at least 1."),
    ("cover without at", set_in("cover", value={"segment": 1}), "The cover has no at."),
    ("true where a number belongs", set_in("segments", 0, "from", value=True), "Segment 1's from must be a number."),
    ("null where a number belongs", set_in("segments", 0, "to", value=None), "Segment 1's to must be a number."),
    ("from below zero", set_in("segments", 0, "from", value=-1), "Segment 1's from is -1; it must be at least 0."),
    ("to zero", set_in("segments", 0, "to", value=0), "Segment 1's to is 0; it must be more than 0."),
    ("empty why", set_in("segments", 0, "why", value=""), "Segment 1's why is empty; say which still it rests on."),
    ("no why", delete_in("segments", 0, "why"), "Segment 1 has no why."),
    ("segment not a block", set_in("segments", 0, value=5), "Segment 1 must be a block of named fields."),
    ("clip record without seconds", delete_in("clips", "A", "seconds"), "Clip A's record has no seconds."),
    ("clip seconds zero", set_in("clips", "A", "seconds", value=0), "Clip A's seconds is 0; it must be more than 0."),
    ("clip file empty", set_in("clips", "A", "file", value=""), "Clip A's file is empty."),
    ("touch-up red as text", set_in("look", "touch_up", "B", "red", value="x"), "Clip B's touch-up red must be a number."),
    ("touch-up without blue", delete_in("look", "touch_up", "A", "blue"), "Clip A's touch-up has no blue."),
    ("touch-up key lower case", lambda data: data["look"]["touch_up"].update(a=data["look"]["touch_up"].pop("A")),
     "The touch-up name \"a\"; a clip's name must be a capital letter such as A."),
    ("look not a block", set_in("look", value=3), "The look must be a block of named fields."),
]


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("row", FAULTS, ids=[row[0] for row in FAULTS])
def test_each_schema_fault_is_one_sentence(row, shape, tmp_path, capsys):
    _, apply, sentence = row
    work, manifest = placeholder_work(tmp_path, shape)
    data = EXAMPLES[shape](clips_block(manifest))
    apply(data)

    code, problems, notes = run_check(work, data, capsys)

    assert code == 1
    assert problems == [sentence]
    assert notes == [check.NOT_COMPARED]


@pytest.mark.parametrize("shape", SHAPES)
def test_a_fault_stops_render_too(shape, tmp_path, capsys):
    work, manifest = placeholder_work(tmp_path, shape)
    data = EXAMPLES[shape](clips_block(manifest))
    data["segments"][0]["move"] = "zoom"
    write_list(work, data)
    before = listing(work)

    assert main(["render", "--work", str(work)]) == 1
    out = capsys.readouterr().out
    assert "Problem: Segment 1's move is \"zoom\"" in out
    assert listing(work) == before


@pytest.mark.parametrize("shape", SHAPES)
def test_several_missing_names_get_a_sentence_each(shape, tmp_path, capsys):
    work, manifest = placeholder_work(tmp_path, shape)
    data = EXAMPLES[shape](clips_block(manifest))
    del data["segments"][1]["from"], data["segments"][1]["to"], data["segments"][1]["sound"]

    _, problems, _ = run_check(work, data, capsys)

    assert problems == ["Segment 2 has no from.", "Segment 2 has no to.", "Segment 2 has no sound."]


@pytest.mark.parametrize("shape", SHAPES)
def test_three_faults_come_in_path_order_with_numbers_as_numbers(shape, tmp_path, capsys):
    work, manifest = placeholder_work(tmp_path, shape)
    data = EXAMPLES[shape](clips_block(manifest))
    data["segments"] = [dict(data["segments"][0]) for _ in range(10)]
    data["segments"][9]["move"] = "zoom"  # written first on purpose
    data["segments"][1]["to"] = None
    data["canvas"]["width"] = "wide"

    _, problems, _ = run_check(work, data, capsys)

    assert problems == [
        "The canvas's width must be a whole number.",
        "Segment 2's to must be a number.",
        "Segment 10's move is \"zoom\"; it must be one of none, push-in, pull-out, pan-left or pan-right.",
    ]


def test_an_empty_object_gives_a_sentence_for_each_part(tmp_path, capsys):
    work, _ = placeholder_work(tmp_path, "tall")

    code, problems, _ = run_check(work, {}, capsys)

    assert code == 1
    assert problems == [
        "The cut list has no version.", "The cut list has no canvas.",
        "The cut list has no clips.", "The cut list has no segments.",
    ]


@pytest.mark.parametrize("shape", SHAPES)
def test_a_list_with_one_segment_and_nothing_else_is_ready(shape, tmp_path, capsys):
    work, manifest = placeholder_work(tmp_path, shape)
    width, height = settings.SHAPES[shape]
    data = {
        "version": 1,
        "canvas": {"width": width, "height": height, "fps": settings.OUTPUT_FPS},
        "clips": clips_block(manifest),
        "segments": [segment("A", 0.0, 3.0, "keep", "A 00.0 to A 03.0: the start")],
    }

    code, problems, notes = run_check(work, data, capsys, all_notes=True)

    assert (code, problems, notes) == (
        0, [], ["There is no touch-up in the list; run match if the clips should match."])


# ---- a missing, empty or bare list ----


def test_a_missing_list_is_one_sentence_and_nothing_is_written(tmp_path, capsys):
    work, _ = placeholder_work(tmp_path, "tall")
    before = listing(work)

    assert main(["check", "--work", str(work)]) == 1
    problems = [line for line in capsys.readouterr().out.splitlines() if line.startswith("Problem: ")]
    assert len(problems) == 1 and problems[0].startswith("Problem: There is no cut list at ")
    assert listing(work) == before


def test_an_empty_file_is_not_valid_json(tmp_path, capsys):
    work, _ = placeholder_work(tmp_path, "wide")
    (work / "cutlist.json").write_text("", encoding="utf-8")
    before = listing(work)

    assert main(["check", "--work", str(work)]) == 1
    problems = [line for line in capsys.readouterr().out.splitlines() if line.startswith("Problem: ")]
    assert problems == ["Problem: The cut list is not valid JSON (line 1, column 1: Expecting value)."]
    assert listing(work) == before


@pytest.mark.parametrize("text", ["[]", "3", "null", '"x"'])
def test_a_list_that_is_not_a_block_is_one_sentence(text, tmp_path, capsys):
    work, _ = placeholder_work(tmp_path, "tall")
    (work / "cutlist.json").write_text(text, encoding="utf-8")

    assert main(["check", "--work", str(work)]) == 1
    problems = [line for line in capsys.readouterr().out.splitlines() if line.startswith("Problem: ")]
    assert problems == ["Problem: The cut list must be a block of named fields."]


# ---- fields accepted but not built, and fields v2r does not know (CUT-08) ----

ACCEPTED_NOTES = [
    "The list's text is accepted but not built yet, so no words are drawn.",
    "The list's voice track is accepted but not built yet, so it is not in the reel.",
    "Segment 1's speed is accepted but not built yet, so the shot plays at normal speed.",
    "Segment 1's transition is accepted but not built yet, so the cut is straight.",
    "Segment 1's text is accepted but not built yet, so no words are drawn.",
]


def add_accepted(data):
    data["text"] = [{"words": "hello", "from": 1.0}]
    data["voice"] = {"file": "voice.m4a"}
    data["segments"][0]["speed"] = 0.5
    data["segments"][0]["transition"] = "dissolve"
    data["segments"][0]["text"] = "hello"
    return data


@pytest.mark.parametrize("shape", SHAPES)
def test_accepted_fields_each_give_a_note_and_no_problem(shape, tmp_path, capsys):
    work, manifest = placeholder_work(tmp_path, shape)
    data = add_accepted(EXAMPLES[shape](clips_block(manifest)))

    code, problems, notes = run_check(work, data, capsys)

    assert (code, problems) == (0, [])
    assert notes == ACCEPTED_NOTES


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("empty", [None, "", [], {}], ids=["null", "empty text", "empty list", "empty block"])
def test_an_empty_accepted_field_gives_no_note(empty, shape, tmp_path, capsys):
    work, manifest = placeholder_work(tmp_path, shape)
    data = EXAMPLES[shape](clips_block(manifest))
    data["text"] = data["voice"] = empty
    for name in ("speed", "transition", "text"):
        data["segments"][0][name] = empty

    assert run_check(work, data, capsys) == (0, [], [])


@pytest.mark.parametrize("value", [0, False, 2, "x", [0], {"a": 1}])
def test_any_other_value_of_an_accepted_field_gives_one_note(value, tmp_path, capsys):
    work, manifest = placeholder_work(tmp_path, "tall")
    data = EXAMPLES["tall"](clips_block(manifest))
    data["segments"][0]["speed"] = value

    code, problems, notes = run_check(work, data, capsys)

    assert (code, problems) == (0, [])
    assert notes == [ACCEPTED_NOTES[2]]


@pytest.mark.parametrize("shape", SHAPES)
def test_an_unknown_field_gives_one_note(shape, tmp_path, capsys):
    work, manifest = placeholder_work(tmp_path, shape)
    data = EXAMPLES[shape](clips_block(manifest))
    data["segments"][0]["zoom"] = 2
    data["colour"] = "warm"
    data["canvas"]["dpi"] = 72
    data["clips"]["A"]["codec"] = "h264"
    data["look"]["touch_up"]["A"]["gamma"] = 1.0
    data["sound"]["echo"] = True
    first = "The list has a field called \"colour\" that v2r does not know, so it was ignored."

    code, problems, notes = run_check(work, data, capsys)

    assert (code, problems) == (0, [])
    assert notes == [
        first,
        "The canvas has a field called \"dpi\" that v2r does not know, so it was ignored.",
        "Clip A's record has a field called \"codec\" that v2r does not know, so it was ignored.",
        "Segment 1 has a field called \"zoom\" that v2r does not know, so it was ignored.",
        "Clip A's touch-up has a field called \"gamma\" that v2r does not know, so it was ignored.",
        "The sound has a field called \"echo\" that v2r does not know, so it was ignored.",
    ]


@pytest.mark.parametrize("shape", SHAPES)
def test_field_names_are_compared_exactly(shape, tmp_path, capsys):
    work, manifest = placeholder_work(tmp_path, shape)
    data = EXAMPLES[shape](clips_block(manifest))
    data["segments"][0]["move"] = "push-in"
    data["segments"][0]["Move"] = "push-in"
    data["segments"][0]["Speed"] = 2

    _, _, notes = run_check(work, data, capsys)

    assert notes == [
        "Segment 1 has a field called \"Move\" that v2r does not know, so it was ignored.",
        "Segment 1 has a field called \"Speed\" that v2r does not know, so it was ignored.",
    ]


def test_an_unknown_name_cannot_fake_a_second_line(tmp_path, capsys):
    work, manifest = placeholder_work(tmp_path, "tall")
    data = EXAMPLES["tall"](clips_block(manifest))
    name = "a\nProblem: nothing is wrong\r b" + "z" * 100
    data["segments"][0][name] = 1

    code, problems, notes = run_check(work, data, capsys)

    assert (code, problems) == (0, [])
    assert len(notes) == 1 and notes[0].startswith('Segment 1 has a field called "a Problem: nothing is wrong')
    assert "z" * 41 not in notes[0]


def test_notes_come_with_problems_too(tmp_path, capsys):
    work, manifest = placeholder_work(tmp_path, "tall")
    data = add_accepted(EXAMPLES["tall"](clips_block(manifest)))
    data["segments"][1]["move"] = "zoom"

    code, problems, notes = run_check(work, data, capsys)

    assert code == 1 and len(problems) == 1
    assert notes == ACCEPTED_NOTES + [check.NOT_COMPARED]


@pytest.mark.parametrize("shape", SHAPES)
def test_accepted_fields_plan_the_same_video(shape, tmp_path):
    from v2r.render import plan

    _, manifest = placeholder_work(tmp_path, shape)
    plain = EXAMPLES[shape](clips_block(manifest))
    extra = add_accepted(copy.deepcopy(plain))

    assert plan.plan(extra, manifest) == plan.plan(plain, manifest)


# ---- the library and the rulebook file ----


@pytest.mark.parametrize("shape", SHAPES)
def test_without_jsonschema_check_says_so_and_render_builds_nothing(shape, tmp_path, capsys, monkeypatch):
    def missing():
        raise ImportError("No module named 'jsonschema'")

    monkeypatch.setattr(check, "jsonschema_module", missing)
    work, manifest = placeholder_work(tmp_path, shape)
    write_list(work, EXAMPLES[shape](clips_block(manifest)))
    before = listing(work)

    assert main(["check", "--work", str(work)]) == 1
    problems = [line for line in capsys.readouterr().out.splitlines() if line.startswith("Problem: ")]
    assert problems == [
        "Problem: The jsonschema library is not installed, so the cut list cannot be checked; install the requirements again."]
    assert main(["render", "--work", str(work)]) == 1
    assert "install the requirements again" in capsys.readouterr().out
    assert listing(work) == before


def test_a_missing_rulebook_file_is_one_sentence(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(check, "SCHEMA_PATH", tmp_path / "nope.json")
    work, manifest = placeholder_work(tmp_path, "wide")

    code, problems, _ = run_check(work, EXAMPLES["wide"](clips_block(manifest)), capsys)

    assert code == 1
    assert problems == ["The rulebook schema/cutlist.schema.json is missing or unreadable, so the cut list cannot be checked."]


def test_other_commands_never_load_jsonschema():
    code = (
        "import sys; sys.modules['jsonschema'] = None; "
        "import v2r.doctor, v2r.normalize, v2r.look, v2r.join, v2r.render; print('ok')")
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.stdout.strip() == "ok", result.stderr


def test_every_schema_keyword_has_a_sentence():
    structural = {"properties", "$defs", "$ref", "items", "additionalProperties", "propertyNames", "description", "title", "$schema"}
    used = set()

    def walk(node):
        for key, value in node.items():
            if key in ("properties", "$defs"):
                for sub in value.values():
                    walk(sub)
            elif key in ("items", "additionalProperties", "propertyNames"):
                walk(value)
            elif key not in structural:
                used.add(key)

    walk(SCHEMA)
    assert used and used <= set(check.SENTENCES)
    text = SCHEMA_PATH.read_text(encoding="utf-8")
    assert "oneOf" not in text and "anyOf" not in text
    assert '"additionalProperties": false' not in text


# ---- every rule of the work folder, one sentence each, in both shapes (D-10) ----

OTHER = {"tall": "wide", "wide": "tall"}
INFO = {  # per shape: what the approved example holds, so each row can name the numbers it breaks
    "tall": {
        "letters": "A, B, C, D and E", "last": "E", "b_name": "IMG_4412.MOV", "a_seconds": 12.0, "b_seconds": 10.0,
        "a_from": 1.0, "a_to": 4.0, "unused": (4, "D"), "photo": (5, "E"), "second_seconds": 2.5, "segments": 7, "reel": 20.0,
    },
    "wide": {
        "letters": "A, B and C", "last": "C", "b_name": "IMG_5003.MOV", "a_seconds": 40.0, "b_seconds": 8.0,
        "a_from": 0.0, "a_to": 10.0, "unused": (2, "B"), "photo": (4, "C"), "second_seconds": 3.0, "segments": 5, "reel": 38.0,
    },
}


def edit_manifest(work, apply):
    path = work / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    apply(manifest)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def a_segment(c, start, end):
    c.data["segments"][0]["from"], c.data["segments"][0]["to"] = start, end


def make_canvas_square(c):
    c.data["canvas"].update(width=1000, height=1000)


def make_canvas_other(c):
    width, height = settings.SHAPES[OTHER[c.shape]]
    c.data["canvas"].update(width=width, height=height)


def add_unknown_clip(c):
    c.data["clips"]["Z"] = {"file": "Z.mov", "seconds": 1.0}


def skip_last_clip(c):
    def apply(manifest):
        manifest["clips"][-1]["status"] = "skipped"
    edit_manifest(c.work, apply)


def make_b_fps(c):
    def apply(manifest):
        manifest["clips"][1]["working"]["fps"] = 25.0
    edit_manifest(c.work, apply)


def drop_unused_clip(c):
    _, letter = c.info["unused"]
    del c.data["clips"][letter]
    del c.data["look"]["touch_up"][letter]


def make_one_frame_short(c):
    a_segment(c, c.info["a_from"], c.info["a_from"] + 0.01)


def make_start_past_clip(c):
    a_segment(c, c.info["a_seconds"] + 1.0, c.info["a_seconds"] + 2.0)


def make_end_past_clip(c):
    a_segment(c, c.info["a_from"], c.info["a_seconds"] + 2.0)


def make_end_past_once_rounded(c):
    a_segment(c, round(c.info["a_seconds"] - 2.983, 3), round(c.info["a_seconds"] + 0.01, 3))


def make_photo_too_long(c):
    c.data["segments"][c.info["photo"][0] - 1]["to"] = 5.0


def many_short_segments(count):
    def apply(c):
        c.data["segments"] = [segment("A", 1.0, 1.1, "off", "A 01.0 to A 01.1: a blink") for _ in range(count)]
        c.data["cover"] = {"segment": 1, "at": 0.05}
    return apply


def make_too_big(c):
    c.patch.setattr(settings, "MAX_RESULT_BYTES", 200 * 1024)


def touch_up_value(letter, name, value):
    def apply(c):
        c.data["look"]["touch_up"][letter][name] = value
    return apply


def add_touch_up_for_f(c):
    c.data["look"]["touch_up"]["F"] = touch_up(0.0, 0.0, 0.0, 1.0)


def cover_on(number, at):
    def apply(c):
        c.data["cover"] = {"segment": number, "at": at}
    return apply


def cover_past_second_segment(c):
    c.data["cover"] = {"segment": 2, "at": 3.0}


def make_two_seconds(c):
    c.data["segments"] = [segment("A", c.info["a_from"], c.info["a_from"] + 2.0, "off", "A: a short one")]
    c.data.pop("cover", None)


def fit_sentence(c):
    total = sum(c.plan.segment_frames(item)[1] for item in c.data["segments"])
    try:
        join.fit(c.shape, total / settings.OUTPUT_FPS)
    except join.JoinError as error:
        return str(error)
    raise AssertionError("the monkeypatched limit did not make the reel too long")


def delete_in_work(name_of):
    def apply(c):
        (c.work / name_of(c)).unlink()
    return apply


def music_folder(tracks=None, files=(), raw=None):
    """An edit that points the music folder at an empty tmp one, with a library.json of `tracks` (or `raw` text) in it."""
    def apply(c):
        folder = c.work.parent / "music"
        folder.mkdir()
        for name in files:
            (folder / name).write_bytes(b"")
        if raw is not None:
            (folder / "library.json").write_text(raw, encoding="utf-8")
        elif tracks is not None:
            (folder / "library.json").write_text(json.dumps({"tracks": tracks}), encoding="utf-8")
        c.patch.setattr(sound, "MUSIC_DIR", folder)
    return apply


def play(track, start=None):
    def apply(c):
        c.data["sound"]["music"] = track
        if start is not None:
            c.data["sound"]["music_from"] = start
    return apply


def both(*edits):
    def apply(c):
        for edit in edits:
            edit(c)
    return apply


GOLDEN = {"id": "golden-hour", "file": "golden-hour.mp3", "seconds": 120.0}

RULES = [  # (id, edit of a valid list, the one sentence it must give as a function of the shape's numbers)
    ("canvas size", make_canvas_square,
     lambda c: "The canvas is 1000x1000 at 30 frames a second; it must be 1080x1920 (tall) or 1920x1080 (wide) at 30."),
    ("canvas shape", make_canvas_other,
     lambda c: f"The canvas is {OTHER[c.shape]} but the clips were normalized for a {c.shape} reel; "
               f"normalize them again with --shape {OTHER[c.shape]} to render this list {OTHER[c.shape]}."),
    ("clip not in the manifest", add_unknown_clip,
     lambda c: f"Clip Z in this list is not in the work folder, which has clips {c.info['letters']}."),
    ("skipped clip", skip_last_clip,
     lambda c: f"Clip {c.info['last']} was skipped when the clips were converted, so it cannot be in the list."),
    ("different file", lambda c: c.data["clips"]["B"].update(file="other.mov"),
     lambda c: f"Clip B in this list was other.mov, but B in the work folder is {c.info['b_name']}."),
    ("different length", lambda c: c.data["clips"]["B"].update(seconds=2.0),
     lambda c: f"Clip B in this list is 2.00 seconds long, but B in the work folder is {c.info['b_seconds']:.2f} seconds long."),
    ("missing working copy", delete_in_work(lambda c: "B.mp4"),
     lambda c: "The working copy of clip B is missing or not in the work folder, so it cannot be built."),
    ("working copy not at 30", make_b_fps,
     lambda c: "The working copy of clip B is not at 30 frames a second, so normalize has to make it again."),
    ("missing photo copy", delete_in_work(lambda c: f"{c.info['photo'][1]}-photo.jpg"),
     lambda c: f"The full-size copy of photo {c.info['photo'][1]} is missing from the work folder, so it cannot be built."),
    ("segment clip not in clips", drop_unused_clip,
     lambda c: f"Segment {c.info['unused'][0]} uses clip {c.info['unused'][1]}, which is not in the list's clips."),
    ("from at to", lambda c: a_segment(c, c.info["a_to"], c.info["a_to"]),
     lambda c: f"Segment 1 starts at {c.info['a_to']:g} seconds and ends at {c.info['a_to']:g}; it must end after it starts."),
    ("under one frame", make_one_frame_short,
     lambda c: "Segment 1 lasts less than one frame (1/30 of a second)."),
    ("starts past the clip", make_start_past_clip,
     lambda c: f"Segment 1 starts at {c.info['a_seconds'] + 1:.1f} seconds but clip A is only {c.info['a_seconds']:.1f} seconds long."),
    ("ends past the clip", make_end_past_clip,
     lambda c: f"Segment 1 ends at {c.info['a_seconds'] + 2:.1f} seconds but clip A is only {c.info['a_seconds']:.1f} seconds long."),
    ("ends past it once rounded", make_end_past_once_rounded,
     lambda c: f"Segment 1 ends at {c.info['a_seconds'] + 0.03:.2f} seconds once rounded to whole frames, "
               f"but clip A is only {c.info['a_seconds']:.2f} seconds long."),
    ("photo past its still", make_photo_too_long,
     lambda c: f"Segment {c.info['photo'][0]} ends at 5.0 seconds but {c.info['photo'][1]} is a photo, "
               "and a photo's still lasts 4 seconds."),
    ("too long to fit", make_too_big, fit_sentence),
    ("121 segments", many_short_segments(121),
     lambda c: "The list has 121 segments; one reel can have at most 120."),
    ("brightness over", touch_up_value("A", "brightness", 8.1),
     lambda c: "Clip A's touch-up brightness is 8.1; it can be at most 8 either way."),
    ("brightness under", touch_up_value("A", "brightness", -8.1),
     lambda c: "Clip A's touch-up brightness is -8.1; it can be at most 8 either way."),
    ("blue over", touch_up_value("A", "blue", -4.5),
     lambda c: "Clip A's touch-up blue is -4.5; it can be at most 4 either way."),
    ("red over", touch_up_value("A", "red", 4.5),
     lambda c: "Clip A's touch-up red is 4.5; it can be at most 4 either way."),
    ("saturation over", touch_up_value("A", "saturation", 1.09),
     lambda c: "Clip A's touch-up saturation is 1.09; it must be between 0.92 and 1.08."),
    ("saturation under", touch_up_value("A", "saturation", 0.91),
     lambda c: "Clip A's touch-up saturation is 0.91; it must be between 0.92 and 1.08."),
    ("touch-up for a clip not in the list", add_touch_up_for_f,
     lambda c: "The touch-up names clip F, which is not in the list's clips."),
    ("cover segment too high", lambda c: cover_on(9, 1.0)(c),
     lambda c: f"The cover names segment 9, but the list has only {c.info['segments']} segments."),
    ("cover past its segment", cover_past_second_segment,
     lambda c: f"The cover is at 3.0 seconds into segment 2, but segment 2 is only {c.info['second_seconds']:.1f} seconds long."),
    ("reel under three seconds", make_two_seconds,
     lambda c: "The reel is 2.0 seconds long; it must be at least 3 seconds."),
    ("music runs out", play("test-tone", 286.0),
     lambda c: f"The music runs out at 14.0 seconds but the reel is {c.info['reel']:.1f} seconds long."),
    ("music cannot start there", play("test-tone", 310.0),
     lambda c: 'The music track "test-tone" is 300.0 seconds long, so it cannot start at 310.0 seconds.'),
    ("music starts at the end of the track", play("test-tone", 300.0),
     lambda c: 'The music track "test-tone" is 300.0 seconds long, so it cannot start at 300.0 seconds.'),
    ("music not in a library that is not there", both(music_folder(), play("golden-hour", 0.0)),
     lambda c: 'The music track "golden-hour" is not in music/library.json; there is no music/library.json yet, '
               'so only "test-tone" can be used.'),
    ("music not in the library", both(music_folder([GOLDEN], ["golden-hour.mp3"]), play("sunrise", 0.0)),
     lambda c: 'The music track "sunrise" is not in music/library.json.'),
    ("music file missing", both(music_folder([GOLDEN]), play("golden-hour", 0.0)),
     lambda c: 'The music file for "golden-hour" is missing from music/.'),
    ("music library broken", both(music_folder(raw="{not json"), play("golden-hour", 0.0)),
     lambda c: "music/library.json could not be read, so the music cannot be checked."),
    ("music file outside the folder", both(
        music_folder([{**GOLDEN, "file": "../golden-hour.mp3"}], ["golden-hour.mp3"]), play("golden-hour", 0.0)),
     lambda c: "music/library.json could not be read, so the music cannot be checked."),
    ("library track too short", both(music_folder([GOLDEN], ["golden-hour.mp3"]), play("golden-hour", 110.0)),
     lambda c: f"The music runs out at 10.0 seconds but the reel is {c.info['reel']:.1f} seconds long."),
]


def context(shape, tmp_path, patch):
    from v2r.render import plan

    work, manifest = placeholder_work(tmp_path, shape)
    data = EXAMPLES[shape](clips_block(manifest))
    return SimpleNamespace(
        shape=shape, work=work, manifest=manifest, data=data, patch=patch, info=INFO[shape], plan=plan)


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("row", RULES, ids=[row[0] for row in RULES])
def test_every_rule_gives_its_own_sentence(row, shape, tmp_path, capsys, monkeypatch):
    _, edit, sentence = row
    c = context(shape, tmp_path, monkeypatch)
    edit(c)

    code, problems, _ = run_check(c.work, c.data, capsys)

    assert code == 1
    assert problems == [sentence(c)]  # run_check also proves the list's bytes and the folder are unchanged


@pytest.mark.parametrize("shape", SHAPES)
def test_a_list_that_breaks_a_rule_is_not_changed_or_built(shape, tmp_path, capsys):
    c = context(shape, tmp_path, None)
    make_end_past_clip(c)
    write_list(c.work, c.data)
    before = listing(c.work)

    assert main(["render", "--work", str(c.work)]) == 1
    assert "Problem: Segment 1 ends at" in capsys.readouterr().out
    assert listing(c.work) == before  # nothing is clamped, trimmed or dropped to make it fit


def break_everything(c, with_count):
    """Break every rule that can be broken beside the others: the problems must come in the stated order."""
    seconds = c.info["a_seconds"]
    make_canvas_square(c)
    c.data["clips"]["B"]["file"] = "other.mov"
    c.data["look"]["touch_up"]["A"]["brightness"] = 9.0
    c.data["sound"]["music_from"] = 295.0 if with_count else 299.0
    if with_count:
        many_short_segments(121)(c)
        c.data["segments"][3] = segment("A", seconds + 1.0, seconds + 2.0, "off", "A: past the end")
        c.data["cover"] = {"segment": 200, "at": 1.0}
    else:
        c.data["segments"] = [
            segment("A", 1.0, 1.5, "off", "A 01.0 to A 01.5: a blink"),
            segment("A", seconds + 1.0, seconds + 2.0, "off", "A: past the end"),
        ]
        c.data["cover"] = {"segment": 1, "at": 0.5}


@pytest.mark.parametrize("shape", SHAPES)
def test_all_rules_broken_at_once_come_in_order(shape, tmp_path, capsys):
    canvas = "The canvas is 1000x1000 at 30 frames a second; it must be 1080x1920 (tall) or 1920x1080 (wide) at 30."
    clips = f"Clip B in this list was other.mov, but B in the work folder is {INFO[shape]['b_name']}."
    look = "Clip A's touch-up brightness is 9; it can be at most 8 either way."
    past = INFO[shape]["a_seconds"] + 1.0
    segments = f"Segment {{n}} starts at {past:.1f} seconds but clip A is only {INFO[shape]['a_seconds']:.1f} seconds long."

    (tmp_path / "short").mkdir()
    short = context(shape, tmp_path / "short", None)
    break_everything(short, with_count=False)
    _, problems, _ = run_check(short.work, short.data, capsys)
    assert problems == [
        canvas, clips, segments.format(n=2), look,
        "The music runs out at 1.0 seconds but the reel is 1.5 seconds long.",
        "The cover is at 0.5 seconds into segment 1, but segment 1 is only 0.5 seconds long.",
        "The reel is 1.5 seconds long; it must be at least 3 seconds.",
    ]

    (tmp_path / "many").mkdir()
    many = context(shape, tmp_path / "many", None)
    break_everything(many, with_count=True)
    _, problems, _ = run_check(many.work, many.data, capsys)
    assert problems == [
        canvas, clips, "The list has 121 segments; one reel can have at most 120.", segments.format(n=4), look,
        "The music runs out at 5.0 seconds but the reel is 13.0 seconds long.",
        "The cover names segment 200, but the list has only 121 segments.",
    ]


@pytest.mark.parametrize("shape", SHAPES)
def test_same_list_same_sentences(shape, tmp_path, capsys):
    c = context(shape, tmp_path, None)
    break_everything(c, with_count=False)
    path = write_list(c.work, c.data)

    outputs = []
    for _ in range(2):
        assert main(["check", str(path), "--work", str(c.work)]) == 1
        outputs.append(capsys.readouterr().out)

    assert outputs[0] == outputs[1] and outputs[0].count("Problem: ") == 7


@pytest.mark.parametrize("shape", SHAPES)
def test_key_order_changes_nothing(shape, tmp_path, capsys):
    c = context(shape, tmp_path, None)
    c.data["clips"]["A"]["file"] = "first.mov"
    c.data["clips"]["B"]["file"] = "second.mov"
    c.data["look"]["touch_up"]["A"]["red"] = 5.0
    c.data["look"]["touch_up"]["B"]["red"] = -5.0
    forward = run_check(c.work, c.data, capsys)

    c.data["clips"] = dict(reversed(c.data["clips"].items()))
    c.data["look"]["touch_up"] = dict(reversed(c.data["look"]["touch_up"].items()))
    assert list(c.data["clips"])[0] != "A"
    backward = run_check(c.work, c.data, capsys)

    assert forward == backward and len(forward[1]) == 4
    assert forward[1][0].startswith("Clip A in this list was first.mov")
    assert forward[1][2].startswith("Clip A's touch-up red is 5")

    clean = EXAMPLES[shape](clips_block(c.manifest))
    clean["clips"] = dict(reversed(clean["clips"].items()))
    clean["look"]["touch_up"] = dict(reversed(clean["look"]["touch_up"].items()))
    assert run_check(c.work, clean, capsys)[:2] == (0, [])


@pytest.mark.parametrize("shape", SHAPES)
def test_repeated_and_touching_segments_pass(shape, tmp_path, capsys):
    c = context(shape, tmp_path, None)
    first = c.data["segments"][0]
    c.data["segments"].append(copy.deepcopy(first))  # word for word, built twice
    c.data["segments"].append(segment("A", first["to"], first["to"] + 1.0, "off", "A: right after the first"))
    c.data["segments"].append(segment("A", first["to"] + 1.0, first["to"] + 2.0, "off", "A: and on"))

    code, problems, _ = run_check(c.work, c.data, capsys)

    assert (code, problems) == (0, [])


@pytest.mark.parametrize("shape", SHAPES)
def test_caps_are_inclusive(shape, tmp_path, capsys):
    c = context(shape, tmp_path, None)
    c.data["look"]["touch_up"]["A"] = touch_up(8.0, -4.0, 4.0, 1.08)
    c.data["look"]["touch_up"]["B"] = touch_up(-8.0, 4.0, -4.0, 0.92)
    assert run_check(c.work, c.data, capsys)[:2] == (0, [])

    many_short_segments(120)(c)  # exactly the most
    assert run_check(c.work, c.data, capsys)[:2] == (0, [])

    c.data["segments"] = [segment("A", 0.0, 3.0, "off", "A: exactly the shortest reel")]
    c.data.pop("cover")
    assert run_check(c.work, c.data, capsys)[:2] == (0, [])
    c.data["segments"][0]["to"] = 2.967  # 89 frames
    _, problems, _ = run_check(c.work, c.data, capsys)
    assert problems == ["The reel is 2.97 seconds long; it must be at least 3 seconds."]


@pytest.mark.parametrize("shape", SHAPES)
def test_cover_just_inside_passes(shape, tmp_path, capsys):
    c = context(shape, tmp_path, None)
    length = INFO[shape]["second_seconds"]
    c.data["cover"] = {"segment": 2, "at": length - 0.01}
    assert run_check(c.work, c.data, capsys)[:2] == (0, [])

    c.data["cover"]["at"] = length
    _, problems, _ = run_check(c.work, c.data, capsys)
    assert problems == [f"The cover is at {length:.1f} seconds into segment 2, but segment 2 is only {length:.1f} seconds long."]


@pytest.mark.parametrize("shape", SHAPES)
def test_nfc_and_case_in_file_names(shape, tmp_path, capsys):
    c = context(shape, tmp_path, None)
    cafe = "Caf\u00e9.MOV"

    def name_it(manifest):
        manifest["clips"][1]["original"]["name"] = unicodedata.normalize("NFD", cafe)

    edit_manifest(c.work, name_it)
    c.data["clips"]["B"]["file"] = unicodedata.normalize("NFC", cafe)
    assert run_check(c.work, c.data, capsys)[:2] == (0, [])

    c.data["clips"]["B"]["file"] = cafe.lower().replace("mov", "MOV").replace("caf", "CAF")
    _, problems, _ = run_check(c.work, c.data, capsys)
    assert len(problems) == 1 and problems[0].startswith("Clip B in this list was CAF")


# ---- the music that is long enough, and the notes that never refuse (D-06, D-10, D-17, D-21) ----

NO_TOUCH_UP = "There is no touch-up in the list; run match if the clips should match."
NO_SOUND = "This reel has no sound at all."
EXAMPLE_NOTES = {  # what the approved examples say about their sideways and upright clips
    "tall": ["Clip B is sideways in a tall frame, so the frame keeps only 32 percent of its picture."],
    "wide": [
        "Clip B is upright in a wide frame, so the frame keeps only 32 percent of its picture.",
        "Photo C is upright in a wide frame, so the frame keeps only 42 percent of its picture.",
    ],
}
PHOTO_SEGMENT = {"tall": (5, "E"), "wide": (4, "C")}


@pytest.mark.parametrize("shape", SHAPES)
def test_examples_pass_with_their_notes(shape, tmp_path, capsys):
    c = context(shape, tmp_path, None)

    code, problems, notes = run_check(c.work, c.data, capsys, all_notes=True)

    assert (code, problems) == (0, [])
    assert notes == EXAMPLE_NOTES[shape]


@pytest.mark.parametrize("shape", SHAPES)
def test_a_lower_crop_share_gives_no_crop_note(shape, tmp_path, capsys, monkeypatch):
    c = context(shape, tmp_path, None)
    monkeypatch.setattr(settings, "CROP_NOTE_SHARE", 0.3)  # read when used, never when loaded

    assert run_check(c.work, c.data, capsys, all_notes=True) == (0, [], [])


@pytest.mark.parametrize("shape", SHAPES)
def test_a_square_or_matching_clip_gets_no_crop_note(shape, tmp_path, capsys):
    c = context(shape, tmp_path, None)

    def square(manifest):
        for entry in manifest["clips"]:
            entry["working"]["size"] = [1500, 1500]
    edit_manifest(c.work, square)
    c.data["segments"] = [segment("A", 0.0, 3.0, "keep", "A: a square clip")]
    c.data["look"] = {"filter": "none", "touch_up": {"A": touch_up(0.0, 0.0, 0.0, 1.0)}}
    c.data.pop("cover", None)

    assert run_check(c.work, c.data, capsys, all_notes=True) == (0, [], [])


@pytest.mark.parametrize("shape", SHAPES)
def test_a_photo_with_no_move_gives_its_note(shape, tmp_path, capsys):
    c = context(shape, tmp_path, None)
    number, letter = PHOTO_SEGMENT[shape]
    c.data["segments"][number - 1]["move"] = "none"

    code, problems, notes = run_check(c.work, c.data, capsys, all_notes=True)

    assert (code, problems) == (0, [])
    assert notes == [f"Segment {number}: {letter} is a photo with no move."] + EXAMPLE_NOTES[shape]

    del c.data["segments"][number - 1]["move"]  # a move left out is no move
    assert run_check(c.work, c.data, capsys, all_notes=True)[2] == notes


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("how", ["absent", "empty"])
def test_no_touch_up_gives_its_note(how, shape, tmp_path, capsys):
    c = context(shape, tmp_path, None)
    if how == "absent":
        del c.data["look"]["touch_up"]
    else:
        c.data["look"]["touch_up"] = {}

    code, problems, notes = run_check(c.work, c.data, capsys, all_notes=True)

    assert (code, problems) == (0, [])
    assert notes == [NO_TOUCH_UP] + EXAMPLE_NOTES[shape]


@pytest.mark.parametrize("shape", SHAPES)
def test_a_silent_reel_says_so(shape, tmp_path, capsys):
    c = context(shape, tmp_path, None)
    c.data["sound"]["music"] = None
    for item in c.data["segments"]:
        item["sound"] = "off"

    code, problems, notes = run_check(c.work, c.data, capsys, all_notes=True)

    assert (code, problems) == (0, [])
    assert notes == EXAMPLE_NOTES[shape] + [NO_SOUND]

    c.data["segments"][0]["sound"] = "keep"  # one shot with its sound is not silence
    assert NO_SOUND not in run_check(c.work, c.data, capsys, all_notes=True)[2]
    c.data["segments"][0]["sound"] = "off"
    c.data["sound"]["music"] = "test-tone"  # and neither is music
    assert NO_SOUND not in run_check(c.work, c.data, capsys, all_notes=True)[2]
    del c.data["sound"]  # no sound block and every shot off is silence
    assert NO_SOUND in run_check(c.work, c.data, capsys, all_notes=True)[2]


@pytest.mark.parametrize("shape", SHAPES)
def test_notes_never_refuse(shape, tmp_path, capsys):
    c = context(shape, tmp_path, None)
    number, _ = PHOTO_SEGMENT[shape]
    c.data["segments"][number - 1]["move"] = "none"
    del c.data["look"]
    c.data["sound"]["music"] = None
    for item in c.data["segments"]:
        item["sound"] = "off"
    add_accepted(c.data)
    path = write_list(c.work, c.data)

    assert main(["check", str(path), "--work", str(c.work)]) == 0
    out = capsys.readouterr().out
    notes = [line.removeprefix("Note: ") for line in out.splitlines() if line.startswith("Note: ")]
    assert "Problem:" not in out and "ready to render" in out
    assert notes == ACCEPTED_NOTES + [
        NO_TOUCH_UP, f"Segment {number}: {PHOTO_SEGMENT[shape][1]} is a photo with no move.",
        *EXAMPLE_NOTES[shape], NO_SOUND]


@pytest.mark.parametrize("shape", SHAPES)
def test_a_library_track_that_is_long_enough_passes(shape, tmp_path, capsys, monkeypatch):
    c = context(shape, tmp_path, None)
    music_folder([GOLDEN], ["golden-hour.mp3"])(SimpleNamespace(work=c.work, patch=monkeypatch))
    c.data["sound"]["music"] = "golden-hour"

    assert run_check(c.work, c.data, capsys)[:2] == (0, [])
    c.data["sound"]["music"] = None  # no music asks nothing of the library
    assert run_check(c.work, c.data, capsys)[:2] == (0, [])


@pytest.mark.parametrize("shape", SHAPES)
def test_music_exactly_as_long_as_the_reel_passes(shape, tmp_path, capsys, monkeypatch):
    c = context(shape, tmp_path, None)
    reel = INFO[shape]["reel"]
    track = {"id": "exact", "file": "exact.mp3", "seconds": reel + 5.0}
    music_folder([track], ["exact.mp3"])(SimpleNamespace(work=c.work, patch=monkeypatch))
    c.data["sound"].update(music="exact", music_from=5.0)
    assert run_check(c.work, c.data, capsys)[:2] == (0, [])

    c.data["sound"]["music_from"] = 5.5  # half a second short
    _, problems, _ = run_check(c.work, c.data, capsys)
    assert problems == [f"The music runs out at {reel - 0.5:.1f} seconds but the reel is {reel:.1f} seconds long."]


def test_a_music_name_cannot_fake_a_line(tmp_path, capsys, monkeypatch):
    c = context("tall", tmp_path, monkeypatch)
    music_folder([])(c)
    c.data["sound"]["music"] = "x\nProblem: all is well" + "z" * 100

    _, problems, _ = run_check(c.work, c.data, capsys)

    assert len(problems) == 1 and "\n" not in problems[0] and "z" * 60 not in problems[0]
