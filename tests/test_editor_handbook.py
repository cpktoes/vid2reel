"""Guards for EDITOR.md, the handbook the phone's Claude follows: at most 1,500 words, real commands, the six steps in order, and no Mac-only option. They check counts and names, never wording, so the user can rewrite any sentence."""

import contextlib
import io
import re

from v2r import ROOT
from v2r.__main__ import main

MAX_WORDS = 1500  # the handbook's cap (Stage 17, D-04; raised from 1,200 to 1,500 on 2026-11-02); a repo rule, so it lives here and not in v2r/settings.py

# The six steps, in the order they must first appear. join is a side road and is left out of the order.
STEPS = ("doctor", "normalize", "look", "check", "match", "render")

NAMED = re.compile(r"python3? -m v2r ([a-z][a-z-]*)")


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


def test_a_text_of_exactly_1500_words_passes_and_1501_fails_the_cap():
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
