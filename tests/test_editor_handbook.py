"""Guards for EDITOR.md, the handbook the phone's Claude follows: at most 1,800 words, real commands, the six steps all there, in order and written as `python3 -m v2r STEP`, no Mac-only option, and the two recipes' shot lengths agree with v2r/settings.py. They check counts and names, never wording, so the user can rewrite any sentence."""

import contextlib
import io
import re

from v2r import ROOT, settings
from v2r.__main__ import main

MAX_WORDS = 1800  # the handbook's cap (Stage 17, D-04; raised from 1,200 to 1,500 on 2026-11-02 and to 1,800 on 2026-11-03 for Stage 19's "Talking with her"); a repo rule, so it lives here and not in v2r/settings.py

# The six steps, in the order they must first appear. join is a side road and is left out of the order.
STEPS = ("doctor", "normalize", "look", "check", "match", "render")

NAMED = re.compile(r"python3 -m v2r ([a-z][a-z-]*)")  # the one spelling the phone's sandbox runs
# The two spellings that look right but are not what the sandbox runs, for the six steps only: `python -m v2r STEP` and
# a bare `v2r STEP`. The lookbehinds keep the correct `python3 -m v2r STEP` from counting as a bare `v2r STEP`.
WRONG_SPELLING = re.compile(
    rf"(?:python -m v2r|(?<!-m )(?<![\w-])v2r)\s+(?:{'|'.join(STEPS)})\b")


NUMBER_WORDS = {  # the number words the handbook may use for a shot length, with their values
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}
NUMBER = rf"(?:\d+(?:\.\d+)?|(?:{'|'.join(NUMBER_WORDS)})(?: and a half)?)"  # 3, 1.5, three, one and a half
RANGE = re.compile(rf"(?P<low>{NUMBER}) to (?P<high>{NUMBER}) seconds")


def number_value(text):
    """The value of one number as the handbook writes it: digits, a number word, or a number word and a half."""
    half = text.endswith(" and a half")
    word = text.removesuffix(" and a half")
    return (NUMBER_WORDS[word] if word in NUMBER_WORDS else float(word)) + (0.5 if half else 0)


def recipe_numbers(text):
    """{Name: [(shortest, longest), ...]} for each recipe of settings.RECIPES: the "A to B seconds" that follows its name.

    The numbers are read from the first "A to B seconds" after the capitalised name within the same clause (no full
    stop, semicolon, exclamation or question mark between), so "Lively: shots of one and a half to three seconds" gives
    (1.5, 3.0). A recipe the text never gives numbers for is left out.
    """
    found = {}
    for recipe in settings.RECIPES:
        name = recipe.capitalize()
        for match in re.finditer(rf"\b{name}\b[^.;!?]*?{RANGE.pattern}", text):
            found.setdefault(name, []).append((number_value(match["low"]), number_value(match["high"])))
    return found


def recipe_problems(text):
    """Plain sentences saying where the text's recipe lengths and settings.RECIPES disagree; empty when they agree."""
    problems = []
    found = recipe_numbers(text)
    for recipe, (low, high) in settings.RECIPES.items():
        name = recipe.capitalize()
        if name not in found:
            problems.append(f"EDITOR.md never states {name}'s shot lengths; say them as settings.RECIPES does, {low:g} to {high:g} seconds.")
        for said_low, said_high in found.get(name, []):
            if (said_low, said_high) != (low, high):
                problems.append(
                    f"EDITOR.md says {name} shots last {said_low:g} to {said_high:g} seconds, but settings.RECIPES says "
                    f"{low:g} to {high:g}; change one so they agree.")
    return problems


def word_count(text):
    # whitespace-split is the stated rule for the cap; it equals `wc -w`
    return len(text.split())


def named_commands(text):
    """The v2r command names the text writes as `python3 -m v2r NAME`, in the order first seen, no repeats."""
    return list(dict.fromkeys(NAMED.findall(text)))


def is_v2r_command(name):
    """True when v2r's own parser accepts the name: argparse exits 0 after a real command's --help and 2 for an unknown one."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        try:
            main([name, "--help"])
        except SystemExit as stop:
            return stop.code == 0
    return False


def handbook_problems(text):
    """Plain sentences saying what is wrong with a handbook text; empty when all is well."""
    problems = []
    words = word_count(text)
    if words > MAX_WORDS:
        problems.append(f"EDITOR.md has {words} words; the cap is {MAX_WORDS}. Cut something before adding.")
    names = named_commands(text)
    if not names:
        problems.append("EDITOR.md names no v2r command.")
    for name in names:
        if not is_v2r_command(name):
            problems.append(f"EDITOR.md names `v2r {name}`, which v2r does not have.")
    for step in STEPS:
        if step not in names:
            problems.append(f"EDITOR.md never runs `python3 -m v2r {step}`; all six steps must be there.")
    for wrong in dict.fromkeys(match.group(0) for match in WRONG_SPELLING.finditer(text)):
        problems.append(f"EDITOR.md writes `{wrong}`; write the command as `python3 -m v2r STEP`.")
    # The order comes from the `python3 -m v2r NAME` matches only, never from the bare words: look, check and match
    # are ordinary English words that appear earlier in prose.
    seen = [name for name in names if name in STEPS]
    if seen != sorted(seen, key=STEPS.index):
        problems.append(
            f"EDITOR.md's steps first appear as {', '.join(seen)}; "
            f"they should come in the order {', '.join(STEPS)}."
        )
    if "--work" in text:
        problems.append("EDITOR.md mentions --work, a Mac-only option the phone never uses (D-09).")
    if "--no-size-limit" in text:
        problems.append("EDITOR.md mentions --no-size-limit, a Mac-only option the phone never uses.")
    return problems


def steps_text(order, extra_words=0):
    """A small valid handbook: one line per named command, then filler words to reach exactly the word count asked for."""
    text = "\n".join(f"Run `python3 -m v2r {name}`." for name in order) + "\n"
    if extra_words:
        text += " ".join(["word"] * (extra_words - word_count(text)))
    return text


def test_editor_md_passes_every_guard():
    text = (ROOT / "EDITOR.md").read_text(encoding="utf-8")  # a missing file fails here, which is intended
    problems = handbook_problems(text)
    assert problems == [], "\n".join(problems)


def test_the_counter_counts_words_not_lines():
    assert word_count("one  two\nthree\tfour") == 4


def test_a_text_at_the_cap_passes_and_one_word_more_fails():
    at_cap = steps_text(STEPS, extra_words=MAX_WORDS)
    assert word_count(at_cap) == MAX_WORDS
    assert handbook_problems(at_cap) == []
    over_cap = at_cap + " word"
    assert word_count(over_cap) == MAX_WORDS + 1
    problems = handbook_problems(over_cap)
    assert len(problems) == 1 and "the cap is" in problems[0]


def test_an_empty_handbook_is_refused():
    assert any("names no v2r command" in problem for problem in handbook_problems(""))


def test_an_unknown_command_is_refused():
    problems = handbook_problems(steps_text(STEPS) + "Then run `python3 -m v2r bogus`.\n")
    assert any("v2r bogus" in problem and "does not have" in problem for problem in problems)


def test_every_real_command_is_accepted_and_a_made_up_one_is_not():
    for name in (*STEPS, "join", "build-skill"):
        assert is_v2r_command(name), name
    assert not is_v2r_command("bogus")


def test_steps_out_of_order_are_refused():
    swapped = ["doctor", "normalize", "render", "check", "match", "look"]
    problems = handbook_problems(steps_text(swapped))
    assert any("should come in the order" in problem for problem in problems)


def test_render_line_moved_above_look_line_is_refused():
    good = steps_text(STEPS)
    assert handbook_problems(good) == []
    lines = good.splitlines()
    render_line = lines.pop(lines.index("Run `python3 -m v2r render`."))
    lines.insert(lines.index("Run `python3 -m v2r look`."), render_line)
    problems = handbook_problems("\n".join(lines) + "\n")
    assert any("should come in the order" in problem for problem in problems)


def test_bare_words_in_prose_do_not_count_for_the_order():
    prose = "Look at the clips, check them and match the light.\n"
    assert handbook_problems(prose + steps_text(STEPS)) == []


def test_join_is_a_side_road_left_out_of_the_order():
    assert handbook_problems(steps_text(("join", *STEPS))) == []
    assert handbook_problems(steps_text((*STEPS, "join"))) == []


def test_the_mac_only_work_option_is_refused():
    problems = handbook_problems(steps_text(STEPS) + "Add `--work` to point at a folder.\n")
    assert any("Mac-only option" in problem for problem in problems)


def test_a_missing_step_is_refused_whichever_one_it_is():
    for gone in STEPS:
        problems = handbook_problems(steps_text([step for step in STEPS if step != gone]))
        assert any(f"never runs `python3 -m v2r {gone}`" in problem for problem in problems), gone


def test_every_step_present_is_not_refused():
    assert handbook_problems(steps_text(STEPS)) == []


def test_the_wrong_spellings_of_a_step_are_refused():
    for step in STEPS:
        for wrong in (f"python -m v2r {step}", f"v2r {step}"):
            problems = handbook_problems(steps_text(STEPS) + f"Then run `{wrong} --help`.\n")
            assert any(f"writes `{wrong}`" in problem for problem in problems), wrong


def test_a_step_written_only_in_a_wrong_spelling_is_missing_and_misspelt():
    text = steps_text(STEPS).replace("python3 -m v2r look", "python -m v2r look")
    problems = handbook_problems(text)
    assert any("never runs `python3 -m v2r look`" in problem for problem in problems)
    assert any("writes `python -m v2r look`" in problem for problem in problems)


def test_the_right_spelling_and_ordinary_words_are_not_taken_for_a_wrong_one():
    prose = "The v2r tool will look, check and match; v2r is the name. Use v2r join for one clip.\n"
    assert handbook_problems(prose + steps_text(STEPS)) == []


def test_recipe_numbers_are_read_from_words_and_from_digits():
    assert recipe_numbers("Lively: shots of one and a half to three seconds; the default.") == {"Lively": [(1.5, 3.0)]}
    assert recipe_numbers("Calm: 3 to 5 seconds, fewer shots.") == {"Calm": [(3.0, 5.0)]}
    assert recipe_numbers("Lively: 1.5 to 3 seconds. Calm: three to five seconds.") == {
        "Lively": [(1.5, 3.0)], "Calm": [(3.0, 5.0)]}


def test_a_recipe_number_after_a_full_stop_belongs_to_no_recipe():
    assert recipe_numbers("Lively is the default. A photo lasts three to four seconds.") == {}


def test_editor_md_recipe_numbers_match_settings():
    text = (ROOT / "EDITOR.md").read_text(encoding="utf-8")
    assert recipe_problems(text) == []


def test_a_recipe_sentence_that_differs_from_settings_is_named():
    problems = recipe_problems("Lively: shots of one and a half to three seconds. Calm: three to six seconds.")
    assert problems == ["EDITOR.md says Calm shots last 3 to 6 seconds, but settings.RECIPES says 3 to 5; change one so they agree."]


def test_a_handbook_that_never_states_a_recipe_is_named():
    problems = recipe_problems("Lively: shots of one and a half to three seconds.")
    assert problems == ["EDITOR.md never states Calm's shot lengths; say them as settings.RECIPES does, 3 to 5 seconds."]
