"""`v2r match`: the touch-up numbers worked out from look.json and written into the cut list, in both shapes.

No FFmpeg is needed: the work folder is made of placeholder files and the tests write their own look.json.
"""

import copy
import json

import pytest
from cutlists import EXAMPLES, clips_block, placeholder_work, segment, write_list

from v2r import settings
from v2r.__main__ import main
from v2r.render import match

SHAPES = ["tall", "wide"]


def overall_of(bright, blue, red, sat):
    return {
        "brightness": bright, "brightness_low": bright - 20, "brightness_high": bright + 20,
        "blue_shift": blue, "red_shift": red, "saturation": sat,
    }


def write_look(work, manifest, measures, finished=True, **more):
    """A look.json with look's frozen names; `measures` maps a letter to (brightness, blue, red, saturation) or None
    (a done entry that could not be measured) or "skipped"."""
    clips = []
    for entry in manifest["clips"]:
        letter = entry["letter"]
        got = measures.get(letter)
        if got == "skipped":
            clips.append({"letter": letter, "number": entry["number"], "status": "skipped", "kind": None, "sentence": "no"})
            continue
        clips.append({
            "letter": letter, "number": entry["number"], "status": "done", "kind": entry["kind"],
            "file": entry["working"]["file"], "seconds": entry["working"]["seconds"],
            "overall": overall_of(*got) if got else {
                "brightness": None, "brightness_low": None, "brightness_high": None,
                "blue_shift": None, "red_shift": None, "saturation": None},
        })
    data = {"version": 1, "shape": manifest["shape"], "finished": finished, "stopped": None, "clips": clips, **more}
    (work / "look.json").write_text(json.dumps(data), encoding="utf-8")
    return data


def one_list(shape, manifest, letters):
    """A short schema-shaped list that uses the clips named by `letters`, in order, and carries clips for every clip."""
    width, height = settings.SHAPES[shape]
    return {
        "version": 1,
        "canvas": {"width": width, "height": height, "fps": settings.OUTPUT_FPS},
        "clips": clips_block(manifest),
        "segments": [segment(letter, 0.0, 2.0, "off", f"{letter} 00.0 to {letter} 02.0: the start") for letter in letters],
    }


def setup(tmp_path, shape, letters, measures, data=None):
    work, manifest = placeholder_work(tmp_path, shape)
    write_look(work, manifest, measures)
    path = write_list(work, data if data is not None else one_list(shape, manifest, letters))
    return work, manifest, path


def letters_of(shape):
    return "ABC" if shape == "wide" else "ABCDE"


def numbers(record):
    return (record["brightness"], record["blue"], record["red"], record["saturation"])


def overall(**by_letter):
    return {letter: {"brightness": b, "blue_shift": u, "red_shift": v, "saturation": s}
            for letter, (b, u, v, s) in by_letter.items()}


# ---- the arithmetic ----


def test_three_clips_move_towards_the_middle_and_stop_at_the_cap():
    found = overall(A=(100, 0, 0, 40), B=(110, 0, 0, 40), C=(140, 0, 0, 40))
    records, capped, notes = match.touch_up_records(found, "ABC", "ABC")
    assert [records[letter]["brightness"] for letter in "ABC"] == [8.0, 0.0, -8.0]  # A's 10 is cut to the cap
    assert capped["A"] == {"brightness"} and capped["B"] == set() and capped["C"] == {"brightness"}
    assert notes == []


def test_four_clips_take_the_mean_of_the_middle_two():
    found = overall(A=(100, 0, 0, 40), B=(110, 0, 0, 40), C=(120, 0, 0, 40), D=(130, 0, 0, 40))
    records, _, _ = match.touch_up_records(found, "ABCD", "ABCD")
    assert [records[letter]["brightness"] for letter in "ABCD"] == [8.0, 5.0, -5.0, -8.0]  # the middle is 115


def test_towards_the_group_never_grey():
    found = overall(A=(120, 10, 10, 40), B=(120, 10, 10, 40), C=(120, 10, 10, 40))
    records, capped, _ = match.touch_up_records(found, "ABC", "ABC")
    assert all(numbers(record) == (0.0, 0.0, 0.0, 1.0) for record in records.values())
    assert all(not hit for hit in capped.values())


def test_a_clip_that_leans_further_is_moved_to_the_group_not_to_grey():
    found = overall(A=(120, 6, 0, 40), B=(120, 3, 0, 40), C=(120, 0, 0, 40))  # the group leans blue by 3
    records, _, _ = match.touch_up_records(found, "ABC", "ABC")
    assert records["A"]["blue"] == -3.0 and records["B"]["blue"] == 0.0 and records["C"]["blue"] == 3.0


def test_saturation_is_the_ratio_to_the_middle_held_to_its_caps():
    found = overall(A=(120, 0, 0, 20), B=(120, 0, 0, 40), C=(120, 0, 0, 80))
    records, capped, _ = match.touch_up_records(found, "ABC", "ABC")
    assert records["A"]["saturation"] == settings.TOUCH_UP_SATURATION_MAX and "saturation" in capped["A"]
    assert records["B"]["saturation"] == 1.0
    assert records["C"]["saturation"] == settings.TOUCH_UP_SATURATION_MIN and "saturation" in capped["C"]


def test_colour_offsets_follow_the_saturation_multiply():
    found = overall(A=(120, 4, 0, 44), B=(120, 0, 0, 40), C=(120, -4, 0, 36))
    records, _, _ = match.touch_up_records(found, "ABC", "ABC")
    # A: saturation 40/44 = 0.91, held to 0.92; the group leans 0, so the offset is 0 - 0.92 * 4 = -3.68
    assert records["A"]["saturation"] == 0.92 and records["A"]["blue"] == pytest.approx(-3.7)


def test_a_value_exactly_at_a_cap_is_within_it():
    found = overall(A=(100, 0, 0, 40), B=(108, 0, 0, 40), C=(116, 0, 0, 40))  # the middle is 108: A is +8, C is -8
    records, capped, _ = match.touch_up_records(found, "ABC", "ABC")
    assert records["A"]["brightness"] == 8.0 and records["C"]["brightness"] == -8.0
    assert capped["A"] == set() and capped["C"] == set()
    over = overall(A=(100, 0, 0, 40), B=(108.5, 0, 0, 40), C=(117, 0, 0, 40))
    records, capped, _ = match.touch_up_records(over, "ABC", "ABC")
    assert records["A"]["brightness"] == 8.0 and capped["A"] == {"brightness"}


def test_offsets_and_saturation_are_rounded_and_minus_zero_is_zero():
    found = overall(A=(100.04, 0.04, 0, 40), B=(100.0, 0, 0, 40), C=(99.96, 0, 0, 40))
    records, _, _ = match.touch_up_records(found, "ABC", "ABC")
    assert records["A"]["brightness"] == 0.0 and str(records["A"]["brightness"]) == "0.0"
    assert str(records["A"]["blue"]) == "0.0" and str(records["A"]["red"]) == "0.0"
    assert records["C"]["brightness"] == 0.0


def test_a_single_clip_is_its_own_middle():
    records, _, _ = match.touch_up_records(overall(A=(90, 7, -3, 55)), "A", "A")
    assert numbers(records["A"]) == (0.0, 0.0, 0.0, 1.0)


def test_an_unmeasured_clip_gets_a_note_and_no_record():
    found = {**overall(A=(100, 0, 0, 40), B=(110, 0, 0, 40)), "C": None}
    records, _, notes = match.touch_up_records(found, "ABC", "ABC")
    assert list(records) == ["A", "B"]
    assert notes == ["Clip C has no brightness and colour in look.json, so it gets no touch-up."]


def test_an_unused_clip_gets_a_record_but_does_not_move_the_middle():
    found = overall(A=(100, 0, 0, 40), B=(110, 0, 0, 40), C=(200, 0, 0, 40))
    records, _, _ = match.touch_up_records(found, "AB", "ABC")
    assert records["A"]["brightness"] == 5.0 and records["B"]["brightness"] == -5.0  # the middle is 105
    assert records["C"]["brightness"] == -8.0  # still nudged towards the group, at the cap


def test_records_come_in_the_order_of_the_lists_clips():
    found = overall(A=(100, 0, 0, 40), B=(110, 0, 0, 40), C=(105, 0, 0, 40))
    records, _, _ = match.touch_up_records(found, "ABC", "CAB")
    assert list(records) == ["C", "A", "B"]


def test_no_measured_clip_in_the_segments_refuses():
    found = {"A": None, "B": overall(B=(100, 0, 0, 40))["B"]}
    with pytest.raises(match.MatchError, match="No clip in the list's segments has brightness and colour"):
        match.touch_up_records(found, "A", "AB")


# ---- the command ----


@pytest.mark.parametrize("shape", SHAPES)
def test_match_writes_one_record_per_measured_clip(shape, tmp_path, capsys):
    letters = letters_of(shape)
    measures = {letter: (100 + 6 * n, n, -n, 40 + n) for n, letter in enumerate(letters)}
    work, manifest, path = setup(tmp_path, shape, letters, measures)
    before = json.loads(path.read_text(encoding="utf-8"))
    assert main(["match", str(path), "--work", str(work)]) == 0
    after = json.loads(path.read_text(encoding="utf-8"))
    touch_up = after["look"]["touch_up"]
    assert list(touch_up) == list(before["clips"])
    assert after["look"]["filter"] == "none"
    out = capsys.readouterr().out
    assert f"The touch-up for {len(touch_up)} clip(s) is in " in out
    assert "A: brightness " in out and "saturation " in out
    for record in touch_up.values():
        assert set(record) == {"brightness", "blue", "red", "saturation"}


@pytest.mark.parametrize("shape", SHAPES)
def test_a_capped_number_is_printed_with_the_cap(shape, tmp_path, capsys):
    letters = letters_of(shape)
    measures = {letter: (100 + 20 * n, 0, 0, 40) for n, letter in enumerate(letters)}
    work, _, path = setup(tmp_path, shape, letters, measures)
    assert main(["match", str(path), "--work", str(work)]) == 0
    out = capsys.readouterr().out
    assert "brightness +8.0 (at the cap)" in out
    assert "brightness -8.0 (at the cap)" in out


@pytest.mark.parametrize("shape", SHAPES)
def test_match_changes_only_the_touch_up(shape, tmp_path):
    work, manifest = placeholder_work(tmp_path, shape)
    data = EXAMPLES[shape](clips_block(manifest))
    data["look"]["filter"] = "warm-evening"
    letters = [entry["letter"] for entry in manifest["clips"]]
    write_look(work, manifest, {letter: (100 + 3 * n, n, -n, 40) for n, letter in enumerate(letters)})
    path = write_list(work, data)
    assert main(["match", str(path), "--work", str(work)]) == 0
    after = json.loads(path.read_text(encoding="utf-8"))
    expected = copy.deepcopy(data)
    expected["look"]["touch_up"] = after["look"]["touch_up"]
    assert after == expected
    assert after["look"]["touch_up"] != data["look"]["touch_up"]
    assert after["look"]["filter"] == "warm-evening"


@pytest.mark.parametrize("shape", SHAPES)
def test_a_list_without_a_look_block_gets_one_with_filter_none(shape, tmp_path):
    letters = letters_of(shape)
    work, manifest, path = setup(tmp_path, shape, letters, {letter: (100, 0, 0, 40) for letter in letters})
    before = json.loads(path.read_text(encoding="utf-8"))
    assert "look" not in before
    assert main(["match", str(path), "--work", str(work)]) == 0
    after = json.loads(path.read_text(encoding="utf-8"))
    assert after["look"]["filter"] == "none"
    assert {key: value for key, value in after.items() if key != "look"} == before


@pytest.mark.parametrize("shape", SHAPES)
def test_rerun_replaces_every_record(shape, tmp_path, monkeypatch):
    letters = letters_of(shape)
    measures = {letter: (100 + 6 * n, 0, 0, 40) for n, letter in enumerate(letters)}
    work, manifest, path = setup(tmp_path, shape, letters, measures)
    assert main(["match", str(path), "--work", str(work)]) == 0
    first = json.loads(path.read_text(encoding="utf-8"))["look"]["touch_up"]
    monkeypatch.setattr(settings, "TOUCH_UP_MAX_BRIGHTNESS", settings.TOUCH_UP_MAX_BRIGHTNESS / 2)
    assert main(["match", str(path), "--work", str(work)]) == 0
    second = json.loads(path.read_text(encoding="utf-8"))["look"]["touch_up"]
    assert list(second) == list(first)
    assert second != first
    assert all(abs(record["brightness"]) <= 4.0 for record in second.values())
    assert first[letters[0]]["brightness"] > 4.0


@pytest.mark.parametrize("shape", SHAPES)
def test_a_letter_dropped_from_clips_loses_its_record(shape, tmp_path):
    letters = letters_of(shape)
    work, manifest, path = setup(
        tmp_path, shape, letters, {letter: (100 + 2 * n, 0, 0, 40) for n, letter in enumerate(letters)})
    assert main(["match", str(path), "--work", str(work)]) == 0
    data = json.loads(path.read_text(encoding="utf-8"))
    del data["clips"][letters[-1]]
    data["segments"] = [item for item in data["segments"] if item["clip"] != letters[-1]]
    write_list(work, data)
    assert main(["match", str(path), "--work", str(work)]) == 0
    assert letters[-1] not in json.loads(path.read_text(encoding="utf-8"))["look"]["touch_up"]


@pytest.mark.parametrize("shape", SHAPES)
def test_an_unmeasured_or_skipped_clip_gets_no_record_and_a_note(shape, tmp_path, capsys):
    letters = letters_of(shape)
    measures = {letter: (100 + 2 * n, 0, 0, 40) for n, letter in enumerate(letters)}
    measures[letters[-1]] = None
    measures[letters[-2]] = "skipped"
    work, _, path = setup(tmp_path, shape, letters, measures)
    assert main(["match", str(path), "--work", str(work)]) == 0
    touch_up = json.loads(path.read_text(encoding="utf-8"))["look"]["touch_up"]
    assert list(touch_up) == list(letters[:-2])
    out = capsys.readouterr().out
    assert f"Clip {letters[-1]} has no brightness and colour in look.json, so it gets no touch-up." in out
    assert f"Clip {letters[-2]} has no brightness and colour in look.json, so it gets no touch-up." in out


@pytest.mark.parametrize("shape", SHAPES)
def test_nothing_measured_changes_nothing(shape, tmp_path, capsys):
    letters = letters_of(shape)
    work, _, path = setup(tmp_path, shape, letters, {})
    before = path.read_bytes()
    assert main(["match", str(path), "--work", str(work)]) == 1
    assert path.read_bytes() == before
    assert "No clip in the list's segments has brightness and colour in look.json, so match changed nothing." in capsys.readouterr().err


@pytest.mark.parametrize("shape", SHAPES)
def test_a_single_measured_clip_gets_a_neutral_record(shape, tmp_path):
    letters = letters_of(shape)
    work, manifest, path = setup(tmp_path, shape, letters[0], {letters[0]: (90, 5, -2, 50)})
    assert main(["match", str(path), "--work", str(work)]) == 0
    touch_up = json.loads(path.read_text(encoding="utf-8"))["look"]["touch_up"]
    assert numbers(touch_up[letters[0]]) == (0.0, 0.0, 0.0, 1.0)
    assert list(touch_up) == [letters[0]]  # the other clips were not measured


# ---- the refusals leave the list untouched ----


def refused(work, path, capsys, sentence):
    before = path.read_bytes()
    assert main(["match", str(path), "--work", str(work)]) == 1
    assert path.read_bytes() == before
    assert not list(work.glob("*.tmp"))
    out, err = capsys.readouterr()
    assert err.startswith("v2r match: ") and sentence in err
    assert err.count("\n") == 1
    return out


@pytest.mark.parametrize("shape", SHAPES)
def test_no_look_json_refuses(shape, tmp_path, capsys):
    letters = letters_of(shape)
    work, _, path = setup(tmp_path, shape, letters, {letter: (100, 0, 0, 40) for letter in letters})
    (work / "look.json").unlink()
    refused(work, path, capsys, "There is no look.json in the work folder yet, so look has to run before match.")


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("text", ["not json", '{"clips": [], "finished": NaN}', "[1, 2]"])
def test_an_unreadable_look_json_refuses(shape, text, tmp_path, capsys):
    letters = letters_of(shape)
    work, _, path = setup(tmp_path, shape, letters, {letter: (100, 0, 0, 40) for letter in letters})
    (work / "look.json").write_text(text, encoding="utf-8")
    refused(work, path, capsys, "look.json could not be read, so match changed nothing.")


@pytest.mark.parametrize("shape", SHAPES)
def test_a_look_json_still_running_refuses(shape, tmp_path, capsys):
    letters = letters_of(shape)
    work, manifest, path = setup(tmp_path, shape, letters, {})
    write_look(work, manifest, {letter: (100, 0, 0, 40) for letter in letters}, finished=False)
    refused(work, path, capsys, "look has not finished yet, so match changed nothing")


@pytest.mark.parametrize("shape", SHAPES)
def test_a_look_json_from_other_clips_refuses(shape, tmp_path, capsys):
    letters = letters_of(shape)
    work, manifest, path = setup(tmp_path, shape, letters, {letter: (100, 0, 0, 40) for letter in letters})
    data = json.loads((work / "look.json").read_text(encoding="utf-8"))
    data["clips"][1]["file"] = "other.mp4"
    (work / "look.json").write_text(json.dumps(data), encoding="utf-8")
    refused(work, path, capsys, "look.json was made from other clips than the work folder holds now")


def change_look_entry(work, index, **changes):
    data = json.loads((work / "look.json").read_text(encoding="utf-8"))
    data["clips"][index].update(changes)
    (work / "look.json").write_text(json.dumps(data), encoding="utf-8")


@pytest.mark.parametrize("shape", SHAPES)
def test_a_look_json_of_a_clip_of_another_length_refuses(shape, tmp_path, capsys):
    # a second job in the same chat reuses the letters and file names; only the length shows it is another clip
    letters = letters_of(shape)
    work, manifest, path = setup(tmp_path, shape, letters, {letter: (100, 0, 0, 40) for letter in letters})
    change_look_entry(work, 1, seconds=manifest["clips"][1]["working"]["seconds"] + 5.0)
    refused(work, path, capsys, "look.json was made from other clips than the work folder holds now")


@pytest.mark.parametrize("shape", SHAPES)
def test_a_look_json_of_a_clip_of_another_kind_refuses(shape, tmp_path, capsys):
    letters = letters_of(shape)
    work, manifest, path = setup(tmp_path, shape, letters, {letter: (100, 0, 0, 40) for letter in letters})
    other = "photo" if manifest["clips"][0]["kind"] == "video" else "video"
    change_look_entry(work, 0, kind=other)
    refused(work, path, capsys, "look.json was made from other clips than the work folder holds now")


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("missing", ["seconds", "kind"])
def test_a_look_json_entry_without_its_length_or_kind_refuses(shape, missing, tmp_path, capsys):
    letters = letters_of(shape)
    work, manifest, path = setup(tmp_path, shape, letters, {letter: (100, 0, 0, 40) for letter in letters})
    data = json.loads((work / "look.json").read_text(encoding="utf-8"))
    del data["clips"][0][missing]
    (work / "look.json").write_text(json.dumps(data), encoding="utf-8")
    refused(work, path, capsys, "look.json was made from other clips than the work folder holds now")


@pytest.mark.parametrize("shape", SHAPES)
def test_look_json_lengths_are_compared_as_look_writes_them(shape, tmp_path, capsys):
    # look writes a clip's length to LOOK_DECIMALS places, so a working copy of 12.004 seconds is 12.0 in look.json
    letters = letters_of(shape)
    work, manifest = placeholder_work(tmp_path, shape)
    manifest_path = work / "manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    data["clips"][0]["working"]["seconds"] = 12.004
    manifest_path.write_text(json.dumps(data), encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    write_look(work, manifest, {letter: (100, 0, 0, 40) for letter in letters})
    change_look_entry(work, 0, seconds=round(12.004, settings.LOOK_DECIMALS))
    path = write_list(work, one_list(shape, manifest, letters))

    assert main(["match", str(path), "--work", str(work)]) == 0
    assert "touch_up" in json.loads(path.read_text(encoding="utf-8"))["look"]


@pytest.mark.parametrize("shape", SHAPES)
def test_a_clips_block_that_does_not_match_refuses(shape, tmp_path, capsys):
    letters = letters_of(shape)
    work, manifest, path = setup(tmp_path, shape, letters, {letter: (100, 0, 0, 40) for letter in letters})
    data = json.loads(path.read_text(encoding="utf-8"))
    data["clips"]["A"]["file"] = "someone-else.MOV"
    write_list(work, data)
    out = refused(work, path, capsys, "The cut list's clips do not match the work folder, so match changed nothing.")
    assert "Problem: Clip A in this list was someone-else.MOV" in out


@pytest.mark.parametrize("shape", SHAPES)
def test_a_list_not_in_the_form_match_needs_refuses(shape, tmp_path, capsys):
    letters = letters_of(shape)
    work, manifest, path = setup(tmp_path, shape, letters, {letter: (100, 0, 0, 40) for letter in letters})
    write_list(work, {"version": 1, "clips": [], "segments": "none"})
    refused(work, path, capsys, "not in the form match needs")


@pytest.mark.parametrize("shape", SHAPES)
def test_no_manifest_or_no_cut_list_refuses(shape, tmp_path, capsys):
    letters = letters_of(shape)
    work, _, path = setup(tmp_path, shape, letters, {letter: (100, 0, 0, 40) for letter in letters})
    assert main(["match", str(work / "missing.json"), "--work", str(work)]) == 1
    assert "no cut list" in capsys.readouterr().err.lower()
    (work / "manifest.json").unlink()
    assert main(["match", str(path), "--work", str(work)]) == 1
    assert "manifest.json" in capsys.readouterr().err


def test_match_uses_the_work_folders_cutlist_by_default(tmp_path, monkeypatch):
    letters = letters_of("tall")
    work, manifest, path = setup(tmp_path, "tall", letters, {letter: (100 + 6 * n, 0, 0, 40) for n, letter in enumerate(letters)})
    monkeypatch.setattr(match, "WORK_DIR", work)
    assert main(["match"]) == 0
    assert "touch_up" in json.loads(path.read_text(encoding="utf-8"))["look"]


def test_match_reads_and_writes_nothing_but_the_list(tmp_path):
    letters = letters_of("tall")
    work, manifest, path = setup(tmp_path, "tall", letters, {letter: (100 + 6 * n, 0, 0, 40) for n, letter in enumerate(letters)})
    names = {item.name: item.read_bytes() for item in work.iterdir() if item.name != "cutlist.json"}
    assert main(["match", str(path), "--work", str(work)]) == 0
    assert {item.name: item.read_bytes() for item in work.iterdir() if item.name != "cutlist.json"} == names


def test_what_match_writes_passes_check(tmp_path, capsys):
    from v2r.render import check

    letters = letters_of("tall")
    work, manifest, path = setup(tmp_path, "tall", letters, {letter: (100 + 20 * n, 3 * n, -3 * n, 30 + 10 * n) for n, letter in enumerate(letters)})
    data = EXAMPLES["tall"](clips_block(manifest))
    write_list(work, data)
    assert main(["match", str(path), "--work", str(work)]) == 0
    checked = check.check(path, work)
    assert [problem for problem in checked.problems if "touch-up" in problem or "look" in problem.lower()] == []
