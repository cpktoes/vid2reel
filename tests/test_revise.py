"""`v2r revise`: one named change to a cut list, written as a new numbered list beside it, in both shapes; no FFmpeg."""

import json

import pytest
from cutlists import EXAMPLES, clips_block, placeholder_work, write_list

from v2r import settings
from v2r.__main__ import main
from v2r.render import revise

SHAPES = ["tall", "wide"]


def changed_paths(before, after, prefix=()):
    """The set of path tuples where two parsed lists differ (written apart from revise, as a second opinion)."""
    found = set()
    if isinstance(before, dict) and isinstance(after, dict):
        for key in set(before) | set(after):
            if key not in before or key not in after:
                found.add(prefix + (key,))
            else:
                found |= changed_paths(before[key], after[key], prefix + (key,))
    elif isinstance(before, list) and isinstance(after, list):
        for index in range(max(len(before), len(after))):
            if index >= len(before) or index >= len(after):
                found.add(prefix + (index,))
            else:
                found |= changed_paths(before[index], after[index], prefix + (index,))
    elif type(before) is not type(after) or before != after:
        found.add(prefix)
    return found


def setup(tmp_path, shape, edit=None):
    """(work folder, list path, list data): the approved example for `shape`, with fields revise has never heard of."""
    work, manifest = placeholder_work(tmp_path, shape)
    data = EXAMPLES[shape](clips_block(manifest))
    data["colour"] = "warm"
    data["segments"][0]["zoom"] = 2
    data["segments"][1]["transition"] = "cut"
    data["text"] = "hello"
    if edit is not None:
        edit(data)
    return work, write_list(work, data), data


def listing(work):
    return sorted(str(path.relative_to(work)) for path in work.rglob("*"))


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def revise_args(work, *words, path=None):
    args = ["revise", *words]
    if path is not None:
        args += ["--cutlist", str(path)]
    return args + ["--work", str(work)]


@pytest.mark.parametrize("shape", SHAPES)
def test_sound_off_changes_only_the_sound_fields(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape)
    before_bytes = path.read_bytes()
    kept = {i for i, item in enumerate(data["segments"]) if item["sound"] == "keep"}
    assert kept
    assert main(revise_args(work, "sound", "off")) == 0
    new = work / "cutlist-2.json"
    assert new.is_file()
    assert changed_paths(data, load(new)) == {("segments", i, "sound") for i in kept}
    assert path.read_bytes() == before_bytes
    out = capsys.readouterr().out
    assert "ready to render" in out


@pytest.mark.parametrize("shape", SHAPES)
def test_sound_keep_for_one_shot_changes_only_that_shot(tmp_path, shape):
    def mute(data):
        for item in data["segments"]:
            item["sound"] = "off"

    work, path, data = setup(tmp_path, shape, mute)
    assert main(revise_args(work, "sound", "keep", "--shot", "2")) == 0
    assert changed_paths(data, load(work / "cutlist-2.json")) == {("segments", 1, "sound")}


@pytest.mark.parametrize("shape", SHAPES)
def test_unknown_fields_survive(tmp_path, shape):
    work, path, data = setup(tmp_path, shape)
    assert main(revise_args(work, "sound", "off")) == 0
    new = load(work / "cutlist-2.json")
    assert new["colour"] == "warm"
    assert new["segments"][0]["zoom"] == 2
    assert new["segments"][1]["transition"] == "cut"
    assert new["text"] == "hello"
    assert new["sound"] == data["sound"]


@pytest.mark.parametrize("shape", SHAPES)
def test_each_run_gets_the_next_free_number(tmp_path, shape):
    work, path, data = setup(tmp_path, shape)
    start = listing(work)
    assert main(revise_args(work, "sound", "off")) == 0
    assert main(revise_args(work, "sound", "keep")) == 0
    assert (work / "cutlist-2.json").is_file() and (work / "cutlist-3.json").is_file()
    assert main(revise_args(work, "sound", "off", path=work / "cutlist-3.json")) == 0
    assert (work / "cutlist-4.json").is_file()
    assert not (work / "cutlist-2-2.json").exists()
    assert len(listing(work)) == len(start) + 3


@pytest.mark.parametrize("shape", SHAPES)
def test_numbers_only_go_up(tmp_path, shape):
    work, path, data = setup(tmp_path, shape)
    (work / "cutlist-5.json").write_text("{}", encoding="utf-8")
    assert main(revise_args(work, "sound", "off")) == 0
    assert (work / "cutlist-6.json").is_file()
    assert (work / "cutlist-5.json").read_text(encoding="utf-8") == "{}"


@pytest.mark.parametrize("shape", SHAPES)
def test_new_file_text_is_written_the_way_match_writes_it(tmp_path, shape):
    work, path, data = setup(tmp_path, shape)
    assert main(revise_args(work, "sound", "off")) == 0
    new = work / "cutlist-2.json"
    parsed = load(new)
    assert new.read_text(encoding="utf-8") == json.dumps(parsed, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


@pytest.mark.parametrize("shape", SHAPES)
def test_output_names_the_new_list_first_and_the_next_commands(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape)
    assert main(revise_args(work, "sound", "off")) == 0
    lines = capsys.readouterr().out.splitlines()
    new = work / "cutlist-2.json"
    assert lines[0] == "New cut list: " + str(new)
    assert any(line.startswith("Shot ") and "sound: was keep, now off." in line for line in lines)
    assert lines[-2].startswith("Next: python3 -m v2r render ")
    assert lines[-2].endswith(f"{new} --work {work}")
    assert lines[-1].startswith("Any further change starts from this list: python3 -m v2r revise CHANGE --cutlist ")
    assert lines[-1].endswith(f"{new} --work {work}")


@pytest.mark.parametrize("shape", SHAPES)
def test_nothing_to_change_writes_no_file(tmp_path, capsys, shape):
    def mute(data):
        for item in data["segments"]:
            item["sound"] = "off"

    work, path, data = setup(tmp_path, shape, mute)
    before = listing(work)
    assert main(revise_args(work, "sound", "off")) == 0
    assert listing(work) == before
    out = capsys.readouterr().out.strip()
    assert out.endswith("is still the list to use.")
    assert "already off" in out
    assert main(revise_args(work, "sound", "off", "--shot", "1")) == 0
    assert listing(work) == before


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("word", ["0", "99", "x", "1.5", "", "-1", "+1", "1" * 7])
def test_a_bad_shot_is_one_plain_sentence(tmp_path, capsys, shape, word):
    work, path, data = setup(tmp_path, shape)
    before = listing(work)
    assert main(revise_args(work, "sound", "off", "--shot", word)) == 1
    err = capsys.readouterr().err
    assert len(err.strip().splitlines()) == 1
    assert err.startswith("v2r revise: ")
    assert "Traceback" not in err
    assert listing(work) == before


def test_a_shot_one_digit_too_long_is_not_a_shot_number():
    long_word = "1" * (settings.REVISE_NUMBER_DIGITS + 1)
    with pytest.raises(revise.ReviseError) as caught:
        revise.parse_shot(long_word, 5)
    assert "is not a shot number" in str(caught.value)
    assert revise.parse_shot("5", 5) == 5
    with pytest.raises(revise.ReviseError) as caught:
        revise.parse_shot("6", 5)
    assert "There is no shot 6" in str(caught.value)
    with pytest.raises(revise.ReviseError) as caught:
        revise.parse_shot("2", 1)
    assert "only shot 1" in str(caught.value)


def test_the_settings_agree():
    assert len(str(settings.MAX_SEGMENTS)) <= settings.REVISE_NUMBER_DIGITS
    assert settings.REVISE_NAME_TRIES >= 1


@pytest.mark.parametrize("shape", SHAPES)
def test_an_empty_work_folder_says_there_is_nothing_to_change(tmp_path, capsys, shape):
    work = tmp_path / "empty"
    work.mkdir()
    assert main(revise_args(work, "sound", "off")) == 1
    err = capsys.readouterr().err
    assert err.strip() == "v2r revise: " + revise.WORK_GONE
    assert listing(work) == []


@pytest.mark.parametrize("shape", SHAPES)
def test_a_list_that_breaks_its_rulebook_is_refused(tmp_path, capsys, shape):
    def spoil(data):
        data["segments"][0]["sound"] = "loud"

    work, path, data = setup(tmp_path, shape, spoil)
    before = listing(work)
    assert main(revise_args(work, "sound", "off")) == 1
    captured = capsys.readouterr()
    assert "Problem: " in captured.out
    assert captured.err.strip() == "v2r revise: " + revise.BROKEN
    assert listing(work) == before


@pytest.mark.parametrize("shape", SHAPES)
def test_a_list_that_is_not_json_is_refused_in_one_sentence(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape)
    path.write_text("{not json", encoding="utf-8")
    assert main(revise_args(work, "sound", "off")) == 1
    err = capsys.readouterr().err
    assert err.startswith("v2r revise: ") and len(err.strip().splitlines()) == 1
    assert "Traceback" not in err


@pytest.mark.parametrize("shape", SHAPES)
def test_a_missing_manifest_still_writes_the_list_and_says_so(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape)
    (work / "manifest.json").unlink()
    assert main(revise_args(work, "sound", "off")) == 1
    out = capsys.readouterr().out
    assert (work / "cutlist-2.json").is_file()
    assert "There is no manifest.json in the work folder yet" in out
    assert "Once the problems above are fixed: python3 -m v2r render " in out


@pytest.mark.parametrize("shape", SHAPES)
def test_revise_renders_nothing_and_adds_no_other_file(tmp_path, shape):
    work, path, data = setup(tmp_path, shape)
    before = set(listing(work))
    assert main(revise_args(work, "sound", "off")) == 0
    after = set(listing(work))
    assert after - before == {"cutlist-2.json"}
    assert not any(name.startswith("reel-") or name.startswith("proof") for name in after)


@pytest.mark.parametrize("shape", SHAPES)
def test_the_input_list_is_not_opened_for_writing(tmp_path, monkeypatch, shape):
    work, path, data = setup(tmp_path, shape)
    real_open = type(path).open

    def guarded(self, mode="r", *args, **kwargs):
        if self == path and any(flag in mode for flag in "wax+"):
            raise AssertionError("the input list was opened for writing")
        return real_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(type(path), "open", guarded)
    assert main(revise_args(work, "sound", "off")) == 0


@pytest.mark.parametrize("shape", SHAPES)
def test_a_full_name_space_is_a_plain_refusal(tmp_path, capsys, monkeypatch, shape):
    work, path, data = setup(tmp_path, shape)
    monkeypatch.setattr(settings, "REVISE_NAME_TRIES", 1)
    monkeypatch.setattr(revise, "next_list_path", lambda p: work / "cutlist-2.json")
    (work / "cutlist-2.json").write_text("{}", encoding="utf-8")
    assert main(revise_args(work, "sound", "off")) == 1
    err = capsys.readouterr().err
    assert err.strip() == "v2r revise: " + revise.NO_WRITE
    assert (work / "cutlist-2.json").read_text(encoding="utf-8") == "{}"


@pytest.mark.parametrize("shape", SHAPES)
def test_the_top_level_sound_block_and_everything_else_stay(tmp_path, shape):
    work, path, data = setup(tmp_path, shape)
    assert main(revise_args(work, "sound", "off")) == 0
    new = load(work / "cutlist-2.json")
    changed = changed_paths(data, new)
    assert all(p[0] == "segments" and p[2] == "sound" for p in changed)
    assert new["sound"] == data["sound"]


def test_help_exits_clean(capsys):
    for words in (["revise", "--help"], ["revise", "sound", "--help"], ["revise", "canvas", "--help"]):
        with pytest.raises(SystemExit) as caught:
            main(words)
        assert caught.value.code == 0
    assert "sound" in capsys.readouterr().out


# canvas

OTHER = {"tall": "wide", "wide": "tall"}


def to_canvas(shape):
    def edit(data):
        data["canvas"]["width"], data["canvas"]["height"] = settings.SHAPES[shape]

    return edit


@pytest.mark.parametrize("shape", SHAPES)
def test_canvas_changes_only_the_two_canvas_numbers(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape, to_canvas(OTHER[shape]))
    assert main(revise_args(work, "canvas", shape)) == 0
    new = load(work / "cutlist-2.json")
    assert changed_paths(data, new) == {("canvas", "width"), ("canvas", "height")}
    assert [new["canvas"]["width"], new["canvas"]["height"]] == list(settings.SHAPES[shape])
    assert new["canvas"]["fps"] == data["canvas"]["fps"]
    assert "ready to render" in capsys.readouterr().out


@pytest.mark.parametrize("shape", SHAPES)
def test_canvas_over_the_other_shapes_clips_gets_checks_own_sentence(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape)
    other = OTHER[shape]
    assert main(revise_args(work, "canvas", other)) == 1
    out = capsys.readouterr().out
    assert (work / "cutlist-2.json").is_file()
    assert f"normalize them again with --shape {other}" in out
    assert "Once the problems above are fixed: python3 -m v2r render " in out


@pytest.mark.parametrize("shape", SHAPES)
def test_canvas_already_that_shape_changes_nothing(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape)
    before = listing(work)
    assert main(revise_args(work, "canvas", shape)) == 0
    assert listing(work) == before
    out = capsys.readouterr().out
    assert f"The canvas is already {shape}, so nothing was changed." in out
    assert "is still the list to use." in out


@pytest.mark.parametrize("shape", SHAPES)
def test_canvas_square_is_refused_by_the_parser(tmp_path, shape):
    work, path, data = setup(tmp_path, shape)
    before = listing(work)
    with pytest.raises(SystemExit) as caught:
        main(revise_args(work, "canvas", "square"))
    assert caught.value.code == 2
    assert listing(work) == before
