"""`v2r revise`: one named change to a cut list, written as a new numbered list beside it, in both shapes; no FFmpeg."""

import json

import pytest
from cutlists import EXAMPLES, clips_block, placeholder_work, write_list

from v2r import settings
from v2r.__main__ import main
from v2r.render import check, plan, revise

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
    data.setdefault("cover", {"segment": 2, "at": 1.0})
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


def numbers_of(count):
    return ",".join(str(n) for n in range(1, count + 1))


def one_line_refusal(capsys):
    err = capsys.readouterr().err
    assert len(err.strip().splitlines()) == 1
    assert err.startswith("v2r revise: ")
    assert "Traceback" not in err
    return err.strip()[len("v2r revise: "):]


@pytest.mark.parametrize("shape", SHAPES)
def test_reorder_plays_the_same_records_in_the_given_order(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape)
    count = len(data["segments"])
    order = [4, 1, 2, 3, 5, 6, 7] if shape == "tall" else [5, 4, 3, 2, 1]
    assert main(revise_args(work, "reorder", ",".join(str(n) for n in order))) == 0
    after = load(work / "cutlist-2.json")
    assert len(after["segments"]) == count
    for new, old in zip(after["segments"], [data["segments"][n - 1] for n in order]):
        assert new == old
        assert list(new.items()) == list(old.items())
    cover_moved = order.index(data["cover"]["segment"]) + 1
    assert after["cover"] == {"segment": cover_moved, "at": data["cover"]["at"]}
    rest_before = {k: v for k, v in data.items() if k not in ("segments", "cover")}
    rest_after = {k: v for k, v in after.items() if k not in ("segments", "cover")}
    assert changed_paths(rest_before, rest_after) == set()
    out = capsys.readouterr().out
    assert revise.OLD_NUMBERS in out
    if cover_moved != data["cover"]["segment"]:
        assert f"The cover moved with its shot: it was in shot {data['cover']['segment']}, now shot {cover_moved}." in out


@pytest.mark.parametrize("shape", SHAPES)
def test_start_with_a_shot_keeps_the_others_in_order(tmp_path, shape):
    work, path, data = setup(tmp_path, shape)
    count = len(data["segments"])
    others = [n for n in range(1, count + 1) if n != 3]
    assert main(revise_args(work, "reorder", ",".join(str(n) for n in [3] + others))) == 0
    after = load(work / "cutlist-2.json")
    assert after["segments"] == [data["segments"][n - 1] for n in [3] + others]


@pytest.mark.parametrize("shape", SHAPES)
def test_a_reorder_that_leaves_the_cover_alone_prints_no_cover_line(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape)
    order = [2, 1, 3, 4, 5, 6, 7] if shape == "tall" else [1, 2, 4, 3, 5]
    assert data["cover"]["segment"] == order[data["cover"]["segment"] - 1]
    assert main(revise_args(work, "reorder", ",".join(str(n) for n in order))) == 0
    assert load(work / "cutlist-2.json")["cover"] == data["cover"]
    assert "The cover" not in capsys.readouterr().out


@pytest.mark.parametrize("shape", SHAPES)
def test_reordering_the_same_order_changes_nothing(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape)
    before = listing(work)
    assert main(revise_args(work, "reorder", numbers_of(len(data["segments"])))) == 0
    assert listing(work) == before
    assert "The shots are already in that order, so nothing was changed." in capsys.readouterr().out


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("text, sentence", [
    ("missing", "Reorder needs every shot number once, in the new order; this list has {count} shots."),
    ("1,1,2,3,4,5,6", "Shot 1 is named twice; name each shot once."),
    ("0,1,2,3,4,5,6", "There is no shot 0 in this list; it has shots 1 to {count}."),
    ("a,b", '"a,b" is not a list of shot numbers such as 4,2; shots are counted from 1 in list order.'),
    ("1,,2", '"1,,2" is not a list of shot numbers such as 4,2; shots are counted from 1 in list order.'),
    ("", '"" is not a list of shot numbers such as 4,2; shots are counted from 1 in list order.'),
])
def test_a_bad_order_is_one_plain_sentence(tmp_path, capsys, shape, text, sentence):
    work, path, data = setup(tmp_path, shape)
    count = len(data["segments"])
    if text == "missing":
        text = "2,1"
    before = listing(work)
    assert main(revise_args(work, "reorder", text)) == 1
    assert one_line_refusal(capsys) == sentence.format(count=count)
    assert listing(work) == before


@pytest.mark.parametrize("shape", SHAPES)
def test_a_list_longer_than_a_reel_can_hold_is_refused_before_reading_it(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape)
    text = ",".join(["1"] * (settings.MAX_SEGMENTS + 1))
    assert main(revise_args(work, "reorder", text)) == 1
    assert "more than a list can hold" in one_line_refusal(capsys)


@pytest.mark.parametrize("shape", SHAPES)
def test_a_one_shot_list_reorders_to_nothing(tmp_path, capsys, shape):
    def one(data):
        data["segments"] = data["segments"][:1]
        data["cover"] = {"segment": 1, "at": 1.0}
        data["look"]["touch_up"] = {"A": data["look"]["touch_up"]["A"]}
        data["clips"] = {"A": data["clips"]["A"]}

    work, path, data = setup(tmp_path, shape, one)
    before = listing(work)
    assert main(revise_args(work, "reorder", "1")) == 0
    assert listing(work) == before
    assert main(revise_args(work, "reorder", "1,2")) == 1
    assert "it has only shot 1." in one_line_refusal(capsys)


def test_follow_cover_leaves_a_broken_cover_for_check():
    for cover in ({"segment": 1.0, "at": 0}, {"segment": 9, "at": 0}, "no", {"segment": True, "at": 0}):
        data = {"cover": cover, "segments": [{}, {}]}
        assert revise.follow_cover(data, {1: 2, 2: 1}) == []
        assert data["cover"] == cover
    assert revise.follow_cover({"segments": [{}]}, {1: 1}) == []


def only_first_shot(data):
    data["segments"] = data["segments"][:1]
    data["cover"] = {"segment": 1, "at": 1.0}


def two_short_shots(data):
    data["segments"] = [
        {"clip": "A", "from": 1.0, "to": 3.0, "sound": "off", "why": "A 01.0 to A 03.0: one"},
        {"clip": "A", "from": 4.0, "to": 6.0, "sound": "off", "why": "A 04.0 to A 06.0: two"},
    ]
    data["cover"] = {"segment": 1, "at": 0.5}


def without_clip_c(data):
    kept = [item for item in data["segments"] if item["clip"] != "C"]
    cover = data["segments"][data["cover"]["segment"] - 1]
    data["segments"] = kept
    data["cover"]["segment"] = kept.index(cover) + 1


@pytest.mark.parametrize("shape", SHAPES)
def test_drop_a_clip_takes_out_all_its_shots_and_touches_nothing_else(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape)
    gone = [n for n, item in enumerate(data["segments"], start=1) if item["clip"] == "A"]
    assert main(revise_args(work, "drop", "A")) == 0
    after = load(work / "cutlist-2.json")
    survivors = [item for item in data["segments"] if item["clip"] != "A"]
    assert after["segments"] == survivors
    for new, old in zip(after["segments"], survivors):
        assert list(new.items()) == list(old.items())
    assert after["clips"] == data["clips"]
    assert after["look"] == data["look"]
    rest_before = {k: v for k, v in data.items() if k not in ("segments", "cover")}
    rest_after = {k: v for k, v in after.items() if k not in ("segments", "cover")}
    assert changed_paths(rest_before, rest_after) == set()
    out = capsys.readouterr().out
    assert out.index(revise.OLD_NUMBERS) < out.index(f"Shot {gone[0]} (clip A) was taken out.")
    for number in gone:
        assert f"Shot {number} (clip A) was taken out." in out
    assert "Clip A's record and touch-up stay in the list, unused." in out
    assert "ready to render" in out


def test_drop_a_clip_with_no_touch_up_says_only_its_record_stays(tmp_path, capsys):
    def bare(data):
        del data["look"]["touch_up"]["B"]

    work, path, data = setup(tmp_path, "tall", bare)
    assert main(revise_args(work, "drop", "B")) == 0
    assert "Clip B's record stays in the list, unused." in capsys.readouterr().out


def test_drop_moves_the_cover_down_when_an_earlier_shot_goes(tmp_path, capsys):
    work, path, data = setup(tmp_path, "tall")
    assert main(revise_args(work, "drop", "A")) == 0
    assert load(work / "cutlist-2.json")["cover"] == {"segment": 3, "at": 1.0}
    assert "The cover moved with its shot: it was in shot 4, now shot 3." in capsys.readouterr().out


@pytest.mark.parametrize("shape, words", [("tall", ["shot", "4"]), ("wide", ["B"])])
def test_dropping_the_covers_own_shot_removes_the_cover(tmp_path, capsys, shape, words):
    work, path, data = setup(tmp_path, shape)
    assert main(revise_args(work, "drop", *words)) == 0
    after = load(work / "cutlist-2.json")
    assert "cover" not in after
    out = capsys.readouterr().out
    assert "The cover was in shot" in out and "which was taken out, so the reel's first frame is the cover now." in out
    assert "ready to render" in out


@pytest.mark.parametrize("shape", SHAPES)
def test_drop_shot_keeps_every_other_record_whole(tmp_path, shape):
    work, path, data = setup(tmp_path, shape)
    assert main(revise_args(work, "drop", "shot", "1")) == 0
    after = load(work / "cutlist-2.json")
    assert after["segments"] == data["segments"][1:]
    assert after["clips"] == data["clips"] and after["look"] == data["look"]


@pytest.mark.parametrize("shape", SHAPES)
def test_drop_a_clip_that_is_not_in_the_list(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape)
    before = listing(work)
    assert main(revise_args(work, "drop", "Z")) == 1
    used = "A, B, C, D and E" if shape == "tall" else "A, B and C"
    assert one_line_refusal(capsys) == f"There is no clip Z in this list's shots; its shots use clips {used}."
    assert listing(work) == before


@pytest.mark.parametrize("shape", SHAPES)
def test_drop_a_clip_with_no_shots_is_nothing_to_drop(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape, without_clip_c)
    assert "C" in data["clips"]
    before = listing(work)
    assert main(revise_args(work, "drop", "C")) == 0
    assert listing(work) == before
    assert "Clip C has no shots in this list, so nothing was changed." in capsys.readouterr().out


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("words", [["c"], ["shot"], ["C", "D"], ["drop"], ["ABCD"], ["1"]])
def test_drop_with_the_wrong_words_says_what_it_needs(tmp_path, capsys, shape, words):
    work, path, data = setup(tmp_path, shape)
    before = listing(work)
    assert main(revise_args(work, "drop", *words)) == 1
    assert one_line_refusal(capsys) == revise.DROP_WORDS
    assert listing(work) == before


@pytest.mark.parametrize("shape", SHAPES)
def test_drop_shot_with_a_bad_number(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape)
    count = len(data["segments"])
    assert main(revise_args(work, "drop", "shot", "x")) == 1
    assert "is not a shot number" in one_line_refusal(capsys)
    assert main(revise_args(work, "drop", "shot", "99")) == 1
    assert one_line_refusal(capsys) == revise.no_shot(99, count)


@pytest.mark.parametrize("shape", SHAPES)
def test_taking_out_every_shot_is_refused(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape, only_first_shot)
    before = listing(work)
    assert main(revise_args(work, "drop", "A")) == 1
    assert one_line_refusal(capsys) == revise.LAST_SHOT
    assert main(revise_args(work, "drop", "shot", "1")) == 1
    assert one_line_refusal(capsys) == revise.LAST_SHOT
    assert listing(work) == before


@pytest.mark.parametrize("shape", SHAPES)
def test_a_reel_left_too_short_is_written_and_check_says_so(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape, two_short_shots)
    assert main(revise_args(work, "drop", "shot", "2")) == 1
    assert (work / "cutlist-2.json").is_file()
    assert "The reel is 2.0 seconds long; it must be at least 3 seconds." in capsys.readouterr().out


@pytest.mark.parametrize("shape", SHAPES)
def test_reorder_and_drop_never_choose(tmp_path, shape):
    """The same words always give the same list: nothing in them is decided by revise."""
    work, path, data = setup(tmp_path, shape)
    assert main(revise_args(work, "drop", "shot", "2")) == 0
    assert main(revise_args(work, "drop", "shot", "2")) == 0
    assert load(work / "cutlist-2.json") == load(work / "cutlist-3.json")


# ---------------------------------------------------------------------------------------------------------------
# shorter: the frame arithmetic (pure) and the command
# ---------------------------------------------------------------------------------------------------------------

LIVELY_FLOOR = 45
TALL_LENGTHS = [90, 75, 90, 90, 90, 75, 90]  # the approved tall example, in frames: 600, twenty seconds
WIDE_LENGTHS = [300, 90, 360, 90, 300]  # the approved wide example, in frames: 1140, thirty-eight seconds

CASES = {
    "tall": {
        "lengths": TALL_LENGTHS, "total": "20", "to": "15", "shots": "6,2", "named": [5, 1],
        "after": [72, 45, 72, 72, 72, 45, 72], "line": "Shot 6: was 2.5 seconds, now 1.5.",
        "bigger": "25", "far": "5", "far_shots": "7,6", "far_dropped": "7 and 6", "far_seconds": "7.5",
        "far_one": "10.5", "cover_edit": {"segment": 4, "at": 2.5}, "cover_shots": "6,2", "cover_to": "15",
        "cover_old": 4, "cover_now": "2.4", "cover_at": "2.5",
    },
    "wide": {
        "lengths": WIDE_LENGTHS, "total": "38", "to": "30", "shots": "4,2", "named": [3, 1],
        "after": [250, 45, 310, 45, 250], "line": "Shot 4: was 3 seconds, now 1.5.",
        "bigger": "40", "far": "3", "far_shots": "5,4", "far_dropped": "5 and 4", "far_seconds": "4.5",
        "far_one": "7.5", "cover_edit": {"segment": 2, "at": 2.0}, "cover_shots": "4,2", "cover_to": "30",
        "cover_old": 2, "cover_now": "1.5", "cover_at": "2",
    },
}


def frame_counts(data):
    return [plan.segment_frames(item)[1] for item in data["segments"]]


def test_the_worked_example_is_exact():
    assert revise.shorter_frames(TALL_LENGTHS, LIVELY_FLOOR, 450, [5, 1]) == ([72, 45, 72, 72, 72, 45, 72], [])


@pytest.mark.parametrize("shape", SHAPES)
def test_shorter_lands_on_every_target(shape):
    lengths, named = CASES[shape]["lengths"], CASES[shape]["named"]
    floors = [min(length, LIVELY_FLOOR) for length in lengths]
    for target in range(sum(floors), sum(lengths)):
        new, dropped = revise.shorter_frames(lengths, LIVELY_FLOOR, target, named)
        assert dropped == []
        assert sum(new) == target
        taken = [old - now for old, now in zip(lengths, new)]
        assert all(floor <= now <= old for floor, now, old in zip(floors, new, lengths))
        others = [i for i in range(len(lengths)) if i not in named]
        if any(taken[i] for i in others):  # the named shots reach their shortest before any other shot loses a frame
            assert all(new[i] == floors[i] for i in named)
        first, second = named
        if taken[second]:  # ... and in the order they were named
            assert new[first] == floors[first]
        free = [i for i in others if new[i] > floors[i]]  # shots the sharing did not run down to their shortest
        for a, b in zip(free, free[1:]):
            assert 0 <= taken[b] - taken[a] <= 1  # differ by at most one, the extra single frames from the later shots
        if free:
            assert max(taken[i] for i in free) - min(taken[i] for i in free) <= 1


def test_shorter_trims_equal_shots_alike_and_gives_the_remainder_to_the_later_ones():
    new, dropped = revise.shorter_frames([90] * 5, LIVELY_FLOOR, 447, [])
    assert dropped == []
    assert [90 - now for now in new] == [0, 0, 1, 1, 1]
    new, dropped = revise.shorter_frames([90] * 5, LIVELY_FLOOR, 440, [])
    assert new == [88, 88, 88, 88, 88]


def test_shorter_drops_from_the_end_of_the_named_list_and_never_the_first_shot():
    lengths = [90] * 6
    new, dropped = revise.shorter_frames(lengths, LIVELY_FLOOR, 180, [5, 4, 3])
    assert dropped == [3, 4]  # the end of the named list first; 4 shots at 45 is 180
    assert new == [45, 45, 45, None, None, 45]
    with pytest.raises(revise.CannotShorten) as caught:
        revise.shorter_frames(lengths, LIVELY_FLOOR, 100, [0, 5])
    assert caught.value.frames == 5 * LIVELY_FLOOR and caught.value.dropped == [5]
    with pytest.raises(revise.CannotShorten) as caught:
        revise.shorter_frames(lengths, LIVELY_FLOOR, 100, [0])
    assert caught.value.frames == 6 * LIVELY_FLOOR and caught.value.dropped == []


def test_a_drop_that_overshoots_writes_the_survivors_untrimmed():
    new, dropped = revise.shorter_frames([45, 45, 45, 45, 300], LIVELY_FLOOR, 200, [4])
    assert (new, dropped) == ([45, 45, 45, 45, None], [4])


def test_a_calm_floor_is_longer():
    new, dropped = revise.shorter_frames([200, 200, 200], 90, 300, [2])
    assert dropped == [] and sum(new) == 300 and new[2] == 90


def test_the_frame_loop_every_start_and_length():
    for thousandths in range(0, 1001):
        start = thousandths / 1000
        for count in (1, 44, 45, 46, 90, 91, 150):
            item = {"clip": "A", "from": start, "to": start + 99.0}
            revise.set_frames(item, count)
            assert item["from"] == start
            assert plan.segment_frames(item) == (plan.frames(start), count), (start, count)
            assert plan.frames(item["to"]) == plan.frames(start) + count, (start, count)
            assert list(item) == ["clip", "from", "to"]


def test_the_digit_and_decimal_settings_agree():
    assert len(str(int(settings.MAX_CUTLIST_SECONDS))) <= settings.REVISE_SECONDS_DIGITS
    assert 1 <= settings.REVISE_DECIMALS < settings.REVISE_DECIMALS_EXACT
    assert settings.REVISE_SHOWN_DECIMALS == 2
    assert revise.seconds_text(201) == "6.7"
    assert revise.seconds_text(200) == "6.67"
    assert revise.seconds_text(450) == "15"
    assert revise.seconds_text(75) == "2.5"


@pytest.mark.parametrize("text", ["15", "0.5", "10800", "3.123456"])
def test_a_plain_number_of_seconds_is_read(text):
    value, frames = revise.parse_target(text)
    assert value == float(text) and frames == plan.frames(float(text))


@pytest.mark.parametrize("text", [
    "abc", "-1", "nan", "inf", "1e3", "0", "0.0", "", " ", "1,5", "15s", "10801", "100000", "1.1234567", ".5", "5.",
    "\u0661\u0662"])
def test_anything_else_is_one_plain_sentence(text):
    with pytest.raises(revise.ReviseError) as caught:
        revise.parse_target(text)
    assert str(caught.value) == "The length to aim for must be a number of seconds, such as 15."


@pytest.mark.parametrize("shape", SHAPES)
def test_shorter_changes_only_the_ends_of_the_shots(tmp_path, capsys, shape):
    case = CASES[shape]
    work, path, data = setup(tmp_path, shape)
    before = path.read_bytes()
    assert frame_counts(data) == case["lengths"]
    assert main(revise_args(work, "shorter", "--to", case["to"], "--from", case["shots"])) == 0
    new = load(work / "cutlist-2.json")
    assert changed_paths(data, new) == {("segments", i, "to") for i in range(len(case["lengths"]))}
    assert frame_counts(new) == case["after"]
    assert [item["from"] for item in new["segments"]] == [item["from"] for item in data["segments"]]
    assert new["cover"] == data["cover"]
    assert path.read_bytes() == before
    out = capsys.readouterr().out
    assert case["line"] in out
    assert f"The reel is now {case['to']} seconds; it was {case['total']}." in out
    assert "ready to render" in out


@pytest.mark.parametrize("shape", SHAPES)
def test_shorter_decides_nothing_the_named_order_is_the_only_choice(tmp_path, shape):
    case = CASES[shape]
    work, path, data = setup(tmp_path, shape)
    assert main(revise_args(work, "shorter", "--to", case["to"], "--from", case["shots"])) == 0
    first = frame_counts(load(work / "cutlist-2.json"))
    assert main(revise_args(work, "shorter", "--to", case["to"], "--from", case["shots"])) == 0
    assert frame_counts(load(work / "cutlist-3.json")) == first
    assert sum(first) == plan.frames(float(case["to"]))


def test_tall_shorter_by_a_little_trims_only_the_first_named_shot(tmp_path, capsys):
    work, path, data = setup(tmp_path, "tall")
    assert main(revise_args(work, "shorter", "--to", "19", "--from", "6,2")) == 0
    new = load(work / "cutlist-2.json")
    assert changed_paths(data, new) == {("segments", 5, "to")}  # 30 frames off shot 6 alone, to its floor
    assert frame_counts(new) == [90, 75, 90, 90, 90, 45, 90]


def test_tall_dropping_a_named_shot_when_even_the_floors_are_too_long(tmp_path, capsys):
    work, path, data = setup(tmp_path, "tall")
    assert main(revise_args(work, "shorter", "--to", "9", "--from", "7,6,5,2")) == 0
    new = load(work / "cutlist-2.json")
    assert frame_counts(new) == [45] * 6
    assert len(new["segments"]) == 6
    assert new["cover"] == {"segment": 3, "at": 1.0}
    out = capsys.readouterr().out
    assert revise.OLD_NUMBERS in out
    assert "Shot 2 was dropped: even at their shortest the shots were too long for 9 seconds." in out
    assert "The cover moved with its shot: it was in shot 4, now shot 3." in out
    assert "The reel is now 9 seconds; it was 20." in out
    assert out.index(revise.OLD_NUMBERS) < out.index("Shot 2 was dropped")


@pytest.mark.parametrize("shape", SHAPES)
def test_shorter_that_cannot_reach_it_even_after_dropping_the_named_refuses(tmp_path, capsys, shape):
    case = CASES[shape]
    work, path, data = setup(tmp_path, shape)
    before = listing(work)
    assert main(revise_args(work, "shorter", "--to", case["far"], "--from", case["far_shots"])) == 1
    assert one_line_refusal(capsys) == (
        f"Even with every shot at its shortest and shots {case['far_dropped']} dropped, the reel would be "
        f"{case['far_seconds']} seconds, so nothing was changed; name more shots to take it to {case['far']} seconds.")
    assert listing(work) == before
    assert main(revise_args(work, "shorter", "--to", case["far"], "--from", "1")) == 1
    assert one_line_refusal(capsys) == (
        f"Even with every shot at its shortest, the reel would be {case['far_one']} seconds, so nothing was changed; "
        f"name more shots to take it to {case['far']} seconds.")
    assert listing(work) == before


def five_shots_one_long(data):
    data["segments"] = [
        {"clip": "A", "from": 0.0, "to": 1.5, "sound": "off", "why": "one"},
        {"clip": "A", "from": 1.5, "to": 3.0, "sound": "off", "why": "two"},
        {"clip": "A", "from": 3.0, "to": 4.5, "sound": "off", "why": "three"},
        {"clip": "A", "from": 4.5, "to": 6.0, "sound": "off", "why": "four"},
        {"clip": "B", "from": 0.0, "to": 6.5, "sound": "off", "why": "five"},
    ]
    data["cover"] = {"segment": 1, "at": 0.5}


@pytest.mark.parametrize("shape", SHAPES)
def test_a_drop_that_overshoots_says_how_far_under_the_reel_is(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape, five_shots_one_long)
    assert frame_counts(data) == [45, 45, 45, 45, 195]
    assert main(revise_args(work, "shorter", "--to", "6.67", "--from", "5")) == 0
    new = load(work / "cutlist-2.json")
    assert frame_counts(new) == [45, 45, 45, 45]
    assert new["segments"] == data["segments"][:4]
    out = capsys.readouterr().out
    assert "Shot 5 was dropped: even at their shortest the shots were too long for 6.67 seconds." in out
    assert "That is 0.67 seconds under the 6.67 asked, because a whole shot had to go." in out


def short_second_shot(data):
    first = data["segments"][1]
    first["to"] = first["from"] + 1.5


@pytest.mark.parametrize("shape,to,shots", [("tall", "18", "2,6"), ("wide", "35", "2,4")])
def test_a_named_shot_already_at_its_shortest_is_left_and_the_next_is_used(tmp_path, capsys, shape, to, shots):
    work, path, data = setup(tmp_path, shape, short_second_shot)
    assert frame_counts(data)[1] == 45
    assert main(revise_args(work, "shorter", "--to", to, "--from", shots)) == 0
    new = load(work / "cutlist-2.json")
    assert ("segments", 1, "to") not in changed_paths(data, new)
    assert sum(frame_counts(new)) == plan.frames(float(to))
    out = capsys.readouterr().out
    assert "Shot 2 was already at its shortest for Lively, so it was left as it was." in out
    assert "Shot 2: was" not in out


@pytest.mark.parametrize("shape", SHAPES)
def test_a_cover_whose_moment_is_trimmed_away_is_removed_and_said(tmp_path, capsys, shape):
    case = CASES[shape]

    def move_cover(data):
        data["cover"] = dict(case["cover_edit"])

    work, path, data = setup(tmp_path, shape, move_cover)
    assert main(revise_args(work, "shorter", "--to", case["cover_to"], "--from", case["cover_shots"])) == 0
    new = load(work / "cutlist-2.json")
    assert "cover" not in new
    out = capsys.readouterr().out
    assert (
        f"The cover was {case['cover_at']} seconds into shot {case['cover_old']}, which is now only "
        f"{case['cover_now']} seconds long, so the reel's first frame is the cover now.") in out
    assert "ready to render" in out


def test_a_calm_list_is_trimmed_to_the_calm_floor(tmp_path):
    work, path, data = setup(tmp_path, "wide", lambda d: d.update(recipe="calm"))
    assert main(revise_args(work, "shorter", "--to", "20", "--from", "3,1")) == 0
    after = frame_counts(load(work / "cutlist-2.json"))
    assert after[2] == 90 and after[0] == 90  # Calm's shortest, 3 seconds, not Lively's 1.5
    assert sum(after) == 600
    assert after == [90, 90, 90, 90, 240]


@pytest.mark.parametrize("shape", SHAPES)
def test_shorter_to_the_current_length_or_longer_changes_nothing(tmp_path, capsys, shape):
    case = CASES[shape]
    work, path, data = setup(tmp_path, shape)
    before = listing(work)
    assert main(revise_args(work, "shorter", "--to", case["total"], "--from", "1")) == 0
    out = capsys.readouterr().out
    assert out.startswith(f"The reel is already {case['total']} seconds, so nothing was changed. ")
    assert out.strip().endswith("is still the list to use.")
    assert listing(work) == before
    assert main(revise_args(work, "shorter", "--to", case["bigger"], "--from", "1")) == 1
    assert one_line_refusal(capsys) == (
        f"The reel is {case['total']} seconds, already shorter than the {case['bigger']} asked; "
        "use longer to make it longer.")
    assert main(revise_args(work, "shorter", "--to", "2", "--from", "1")) == 1
    assert one_line_refusal(capsys) == "A reel must be at least 3 seconds, so it cannot be made shorter than that."
    assert listing(work) == before


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("word", ["abc", "-1", "nan", "1e3", "0"])
def test_shorter_with_a_bad_length_is_one_plain_sentence(tmp_path, capsys, shape, word):
    work, path, data = setup(tmp_path, shape)
    before = listing(work)
    assert main(revise_args(work, "shorter", "--to", word, "--from", "1")) == 1
    assert one_line_refusal(capsys) == "The length to aim for must be a number of seconds, such as 15."
    assert listing(work) == before


@pytest.mark.parametrize("shape", SHAPES)
def test_shorter_with_a_bad_shot_list_is_one_plain_sentence(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape)
    count = len(data["segments"])
    before = listing(work)
    assert main(revise_args(work, "shorter", "--to", "5", "--from", "9")) == 1
    assert one_line_refusal(capsys) == revise.no_shot(9, count)
    assert main(revise_args(work, "shorter", "--to", "5", "--from", "2,2")) == 1
    assert one_line_refusal(capsys) == "Shot 2 is named twice; name each shot once."
    assert listing(work) == before


def test_shorter_help_shows_its_two_words(capsys):
    with pytest.raises(SystemExit) as caught:
        main(["revise", "shorter", "--help"])
    assert caught.value.code == 0
    out = capsys.readouterr().out
    assert "--to" in out and "--from" in out


# ---------------------------------------------------------------------------------------------------------------
# longer: the mirror, inside each clip and each recipe
# ---------------------------------------------------------------------------------------------------------------

LONGER = {  # the named shots: one that can grow and one that cannot (tall), a photo and a shot at its longest (wide)
    "tall": {"shots": "2,6", "to": "21", "grown": [1, 5], "after": [90, 90, 90, 90, 90, 90, 90], "total": "20",
             "short_to": "25", "short_by": "4", "smaller": "15", "stuck": "1,3", "stuck_to": "21"},
    "wide": {"shots": "2,4", "to": "39", "grown": [3], "after": [300, 90, 360, 120, 300], "total": "38",
             "short_to": "45", "short_by": "6", "smaller": "30", "stuck": "1,3", "stuck_to": "40"},
}


def test_longer_frames_gives_the_named_shots_their_room_in_order():
    ceilings = [90] * 7
    new = revise.longer_frames(TALL_LENGTHS, ceilings, 630, [1, 5])
    assert new == [90, 90, 90, 90, 90, 90, 90]
    assert revise.longer_frames(TALL_LENGTHS, ceilings, 610, [1, 5]) == [90, 85, 90, 90, 90, 75, 90]  # the first named first
    assert revise.longer_frames(TALL_LENGTHS, ceilings, 700, [1, 5]) == [90, 90, 90, 90, 90, 90, 90]  # as far as they go
    assert revise.longer_frames(TALL_LENGTHS, [90, 80, 90, 90, 90, 200, 90], 700, [5, 1]) == [90, 75, 90, 90, 90, 175, 90]
    assert revise.longer_frames(TALL_LENGTHS, ceilings, 600, [1]) == TALL_LENGTHS  # nothing wanted
    assert revise.longer_frames([100], [90], 200, [0]) == [100]  # a ceiling under the length never shrinks a shot


@pytest.mark.parametrize("shape", SHAPES)
def test_longer_changes_only_the_ends_of_the_named_shots(tmp_path, capsys, shape):
    case = LONGER[shape]
    work, path, data = setup(tmp_path, shape)
    before = path.read_bytes()
    assert main(revise_args(work, "longer", "--to", case["to"], "--from", case["shots"])) == 0
    new = load(work / "cutlist-2.json")
    assert changed_paths(data, new) == {("segments", i, "to") for i in case["grown"]}
    assert frame_counts(new) == case["after"]
    assert sum(frame_counts(new)) == plan.frames(float(case["to"]))
    assert path.read_bytes() == before
    out = capsys.readouterr().out
    assert f"The reel is now {case['to']} seconds; it was {case['total']}." in out
    assert "ready to render" in out
    assert "short of" not in out


def test_tall_longer_names_a_shot_that_cannot_grow_and_lets_the_others_grow(tmp_path, capsys):
    work, path, data = setup(tmp_path, "tall")
    assert main(revise_args(work, "longer", "--to", "21", "--from", "1,2,6")) == 0
    new = load(work / "cutlist-2.json")
    assert changed_paths(data, new) == {("segments", 1, "to"), ("segments", 5, "to")}
    out = capsys.readouterr().out
    assert "Shot 1 cannot run longer, so it was left as it was." in out
    assert "Shot 2: was 2.5 seconds, now 3." in out
    assert "Shot 6: was 2.5 seconds, now 3." in out


@pytest.mark.parametrize("shape", SHAPES)
def test_longer_that_cannot_get_there_writes_what_it_reached_and_says_how_far_short(tmp_path, capsys, shape):
    case = LONGER[shape]
    work, path, data = setup(tmp_path, shape)
    assert main(revise_args(work, "longer", "--to", case["short_to"], "--from", case["shots"])) == 0
    assert frame_counts(load(work / "cutlist-2.json")) == case["after"]
    out = capsys.readouterr().out
    assert (
        f"That is {case['short_by']} seconds short of the {case['short_to']} asked; "
        "the rest needs a new moment added to the list.") in out


def test_a_photo_may_run_to_its_whole_clip_past_the_recipe(tmp_path):
    work, path, data = setup(tmp_path, "tall")
    assert main(revise_args(work, "longer", "--to", "21", "--from", "5")) == 0
    new = load(work / "cutlist-2.json")
    assert frame_counts(new)[4] == 120  # four seconds: the photo's whole clip, past Lively's three
    assert changed_paths(data, new) == {("segments", 4, "to")}


def calm_with_a_later_shot_of_the_same_clip(data):
    data["recipe"] = "calm"
    data["segments"] = [
        {"clip": "A", "from": 1.0, "to": 2.0, "sound": "off", "why": "one"},
        {"clip": "B", "from": 2.0, "to": 4.5, "sound": "off", "why": "two"},
        {"clip": "A", "from": 2.5, "to": 4.0, "sound": "off", "why": "three"},
    ]
    data["cover"] = {"segment": 1, "at": 0.5}


@pytest.mark.parametrize("shape", SHAPES)
def test_longer_stops_at_the_first_frame_of_a_later_shot_of_the_same_clip(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape, calm_with_a_later_shot_of_the_same_clip)
    assert frame_counts(data) == [30, 75, 45]
    assert main(revise_args(work, "longer", "--to", "10", "--from", "1")) == 0
    new = load(work / "cutlist-2.json")
    assert (new["segments"][0]["from"], new["segments"][0]["to"]) == (1.0, 2.5)
    assert frame_counts(new)[0] == 45
    assert changed_paths(data, new) == {("segments", 0, "to")}
    assert "short of the 10 asked" in capsys.readouterr().out


def calm_with_a_shot_starting_on_the_same_frame(data):
    calm_with_a_later_shot_of_the_same_clip(data)
    data["segments"][2]["from"] = 1.0
    data["segments"][2]["to"] = 4.0


@pytest.mark.parametrize("shape", SHAPES)
def test_a_shot_starting_on_the_same_frame_is_not_a_later_one(tmp_path, shape):
    work, path, data = setup(tmp_path, shape, calm_with_a_shot_starting_on_the_same_frame)
    assert main(revise_args(work, "longer", "--to", "20", "--from", "1")) == 0
    new = load(work / "cutlist-2.json")
    assert (new["segments"][0]["from"], new["segments"][0]["to"]) == (1.0, 6.0)  # the recipe's longest, 5 seconds, from 1.0


def calm_near_the_end_of_its_clip(shape):
    last = {"tall": (11.0, 11.5), "wide": (38.0, 39.0)}[shape]

    def edit(data):
        data["recipe"] = "calm"
        data["segments"] = [
            {"clip": "B", "from": 0.0, "to": 3.0, "sound": "off", "why": "one"},
            {"clip": "A", "from": last[0], "to": last[1], "sound": "off", "why": "two"},
        ]
        data["cover"] = {"segment": 1, "at": 0.5}

    return edit


@pytest.mark.parametrize("shape", SHAPES)
def test_longer_stops_at_the_end_of_the_clip(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape, calm_near_the_end_of_its_clip(shape))
    assert main(revise_args(work, "longer", "--to", "20", "--from", "2")) == 0
    new = load(work / "cutlist-2.json")
    clip_end = {"tall": 12.0, "wide": 40.0}[shape]
    assert new["segments"][1]["to"] == clip_end
    assert frame_counts(new)[1] == plan.frames(clip_end) - plan.frames(data["segments"][1]["from"])
    assert "ready to render" in capsys.readouterr().out


@pytest.mark.parametrize("shape", SHAPES)
def test_longer_with_every_named_shot_at_its_ceiling_writes_nothing(tmp_path, capsys, shape):
    case = LONGER[shape]
    work, path, data = setup(tmp_path, shape)
    before = listing(work)
    assert main(revise_args(work, "longer", "--to", case["stuck_to"], "--from", case["stuck"])) == 1
    assert one_line_refusal(capsys) == (
        "None of shots 1 and 3 can run longer, each being at its recipe's longest, at the end of its clip or at the "
        "next shot of the same clip, so nothing was changed; a longer reel needs a new moment added to the list.")
    assert listing(work) == before
    assert main(revise_args(work, "longer", "--to", case["stuck_to"], "--from", "3")) == 1
    assert one_line_refusal(capsys) == (
        "Shot 3 cannot run longer, being at its recipe's longest, at the end of its clip or at the next shot of the "
        "same clip, so nothing was changed; a longer reel needs a new moment added to the list.")
    assert listing(work) == before


@pytest.mark.parametrize("shape", SHAPES)
def test_longer_to_the_current_length_or_shorter_changes_nothing(tmp_path, capsys, shape):
    case = LONGER[shape]
    work, path, data = setup(tmp_path, shape)
    before = listing(work)
    assert main(revise_args(work, "longer", "--to", case["total"], "--from", "1")) == 0
    out = capsys.readouterr().out
    assert out.startswith(f"The reel is already {case['total']} seconds, so nothing was changed. ")
    assert listing(work) == before
    assert main(revise_args(work, "longer", "--to", case["smaller"], "--from", "1")) == 1
    assert one_line_refusal(capsys) == (
        f"The reel is {case['total']} seconds, already longer than the {case['smaller']} asked; "
        "use shorter to make it shorter.")
    assert listing(work) == before


@pytest.mark.parametrize("shape", SHAPES)
def test_longer_without_a_manifest_says_what_check_says(tmp_path, capsys, shape):
    work, path, data = setup(tmp_path, shape)
    (work / "manifest.json").unlink()
    before = listing(work)
    assert main(revise_args(work, "longer", "--to", LONGER[shape]["to"], "--from", LONGER[shape]["shots"])) == 1
    assert one_line_refusal(capsys) == check.NO_MANIFEST
    assert listing(work) == before


@pytest.mark.parametrize("shape", SHAPES)
def test_longer_over_clips_that_no_longer_match_the_work_folder_refuses(tmp_path, capsys, shape):
    def wrong_length(data):
        data["clips"]["A"]["seconds"] = 99.0

    work, path, data = setup(tmp_path, shape, wrong_length)
    before = listing(work)
    assert main(revise_args(work, "longer", "--to", LONGER[shape]["to"], "--from", LONGER[shape]["shots"])) == 1
    captured = capsys.readouterr()
    assert "Problem: Clip A in this list is 99.00 seconds long" in captured.out
    assert captured.err.strip() == (
        "v2r revise: The cut list's clips do not match the work folder, so nothing was changed; run check to see why.")
    assert listing(work) == before


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("word", ["abc", "-1", "0", "1e3"])
def test_longer_with_a_bad_length_or_shot_is_one_plain_sentence(tmp_path, capsys, shape, word):
    work, path, data = setup(tmp_path, shape)
    assert main(revise_args(work, "longer", "--to", word, "--from", "1")) == 1
    assert one_line_refusal(capsys) == "The length to aim for must be a number of seconds, such as 15."
    assert main(revise_args(work, "longer", "--to", "30", "--from", "99")) == 1
    assert "There is no shot 99" in one_line_refusal(capsys)


def test_the_revise_help_lists_every_change(capsys):
    with pytest.raises(SystemExit) as caught:
        main(["revise", "--help"])
    assert caught.value.code == 0
    out = capsys.readouterr().out
    for word in ("sound", "canvas", "reorder", "drop", "shorter", "longer"):
        assert word in out
    with pytest.raises(SystemExit) as caught:
        main(["revise", "longer", "--help"])
    assert caught.value.code == 0
