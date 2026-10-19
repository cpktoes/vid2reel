"""The cut list's rulebook (schema/cutlist.schema.json) and `check`'s sentences about it, in both shapes."""

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest
from cutlists import EXAMPLES, clips_block, placeholder_work, segment, write_list
from jsonschema import Draft202012Validator

from v2r import settings
from v2r.__main__ import main
from v2r.render import check

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


def run_check(work, data, capsys, name="cutlist.json"):
    """Write the list, run `check`, and return (exit code, problem sentences, note sentences, the file's bytes before)."""
    path = write_list(work, data, name)
    before, files = path.read_bytes(), listing(work)
    code = main(["check", str(path), "--work", str(work)])
    lines = capsys.readouterr().out.splitlines()
    assert path.read_bytes() == before  # check only reads the list (T-4-12)
    assert listing(work) == files  # and writes nothing anywhere
    problems = [line.removeprefix("Problem: ") for line in lines if line.startswith("Problem: ")]
    notes = [line.removeprefix("Note: ") for line in lines if line.startswith("Note: ")]
    return code, problems, notes


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

    code, problems, notes = run_check(work, data, capsys)

    assert (code, problems, notes) == (0, [], [])


@pytest.mark.parametrize("shape", SHAPES)
def test_the_approved_examples_are_ready_to_render(shape, tmp_path, capsys):
    work, manifest = placeholder_work(tmp_path, shape)
    data = EXAMPLES[shape](clips_block(manifest))

    code, problems, notes = run_check(work, data, capsys)

    assert (code, problems, notes) == (0, [], [])


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
