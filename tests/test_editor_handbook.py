"""Guards for EDITOR.md, the handbook the phone's Claude follows: two pages at most, real commands, the six steps in order, and no Mac-only option. They check counts and names, never wording, so the user can rewrite any sentence."""

import contextlib
import io
import re

from v2r import ROOT
from v2r.__main__ import main

MAX_WORDS = 1200  # the two-pages rule (Stage 17, D-04); a repo rule, so it lives here and not in v2r/settings.py

# The six steps, in the order they must first appear. join is a side road and is left out of the order.
STEPS = ("doctor", "normalize", "look", "check", "match", "render")

NAMED = re.compile(r"python3? -m v2r ([a-z][a-z-]*)")


def word_count(text):
    # whitespace-split is the stated rule for "two pages"; it equals `wc -w`
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
        problems.append(f"EDITOR.md has {words} words; two pages is at most {MAX_WORDS}. Cut something before adding.")
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
