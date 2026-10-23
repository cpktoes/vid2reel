# Phase 5: Stage 17 – Editor's handbook - Research

**Researched:** 2026-10-24
**Domain:** A plain-English handbook (EDITOR.md) that drives the phone's Claude through the existing v2r commands; two small CLI additions (`--work` on `normalize` and `look`); two guard tests; rehearsals and a phone test done by people.
**Confidence:** HIGH for the code seams and tests (every value below was read in this session); MEDIUM for how the rehearsals will behave (a language model's run-to-run variation cannot be researched, only planned around).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
(Copied from `05-CONTEXT.md` `## Implementation Decisions`; D-01 to D-13 are locked.)

- **D-01:** Make the reel first. A plan is shown before building only for talking-head videos, which is Stage 24's rule. The guide's Decide box "show the plan first, or make the reel first" is closed with its pick.
- **D-02:** Taste lives in a section headed "Reel style" in the instructions of each account's existing Claude Project; the handbook holds craft and house rules only. Order of authority, written into the handbook: what the user types in the chat; then the Reel style section of the chat's standing instructions, with the rest of those instructions read as background on the account; then the handbook and its defaults. The guide's Decide box "where taste lives" is closed with its pick. Reversibility: reversible.
- **D-03:** EDITOR.md covers (HAND-01): the steps in order naming the exact command for each (doctor, normalize, look, check, match, render; join only when the user wants the clips joined); how to study the contact sheets and look.json; rules of craft (open on the strongest picture; prefer the steady, sharp candidate stretches; one moment from every clip before a second from any; never two alike shots adjacent; end on a shot that feels finished; stay within a tenth of the length asked; the moment the user named usually opens or closes the reel, kept by the user on review; attach order is not shot order, Phase 4's D-13); the Lively recipe (shots of 1.5 to 3 s, the default) and Calm (3 to 5 s, fewer shots); the house rules (no filter unless the user asks, match by default; every shot fills the tall frame, sideways clips cropped and never mixed in as widescreen; a wide video keeps sideways footage whole and is wide throughout; a slow move on photos and on at most one video shot in four, never on a shot look.json marks as moving or shaky); the honesty rules (every shot's "why" cites still labels; anything between stills is called a guess; never "I watched your clips"); the proof sheets before sending, fixing the cut list at most once and, if it is still wrong, stopping and asking the user before sending anything; what to do with an unreadable file (carry on, say which) and too little good footage (shorter, say so, never pad); and that only the repo's commands may be used. Two pages at most, short sentences, no programming terms beyond the command names and one long-command recipe, written so the user can edit it himself.
- **D-04:** "Two pages" is held by a test: EDITOR.md may hold at most 1,200 words (whitespace-split), and the test fails above that. The number lives in the test, not settings.py, because it is a repo rule and settings.py ships to the sandbox. EDITOR.md is 912 words today; the draft folds the four background-command recipes into one "long commands" paragraph to make room for the craft.
- **D-05:** Defaults when the message says nothing: about 20 seconds, tall (1080 by 1920), Lively, no filter, a mild touch-up, the clips' own sound kept, no music. Wide (1920 by 1080) only when the user asks, or for footage shot sideways that is going to YouTube.
- **D-06:** Asking before editing, until Stage 19 builds the brief: two questions in one short message, only when the message did not say them: what the reel is about, and which moment is the star. Nothing else is asked; everything else takes the defaults. Stage 19 turns the defaults into its questions.
- **D-07:** Music until Stage 18: a real reel is made without music, every shot's own sound kept unless the user asks for it off, and the reply says a song can be added in the posting app. If the user asks for music before the library exists, the reply says the library is coming and the reel is still made without it. A reel with no sound at all is allowed and check notes it. The test tone stays a test fixture only.
- **D-08:** The handbook draft is reviewed by the user before planning: it is `05-HANDBOOK-DRAFT.md` in this folder. EDITOR.md itself changes only as the user's text: he edits it, or asks for the draft to be pasted, as he did in Stage 16. No executor edits EDITOR.md on its own initiative; a plan task that touches EDITOR.md is a checkpoint for his word.
- **D-09:** `normalize` and `look` gain `--work FOLDER` (check, match and render already have it; look already takes a positional folder) so each fixture set rehearses into work/<set>/ and the five reels sit side by side. Mac-only convenience: the handbook keeps plain work/, the phone's sandbox is wiped at the end of every chat, and work/ and fixtures/ stay git-ignored. `normalize --work` clears that folder's last job the same way it clears work/; render keeps "every output is a new file", so old rehearsal reels are deleted by hand.
- **D-10:** The rehearsal (the guide's Stage 17 prompt: act as the phone's Claude handed EDITOR.md and one profile, follow it step by step on one fixture set) runs in a fresh Claude Code session after /clear, never in the orchestrating session, once per fixture set. Five sets exist in fixtures/; one is a sideways talking-head set that is always made wide. Then one set is rehearsed a second time with a different profile; the two cut lists are compared as text and both reels watched: they must differ only where the profiles differ (HAND-04). Each rehearsal ends with the list of places where EDITOR.md was unclear or tempting to leave; those feed the user's edits.
- **D-11:** Her scores (1 to 5) and her words go in fixtures/reel-log.md under the Stage 13 ritual; HAND-05 (she would post three of the five with small changes) is a human check recorded there. The phone test on the branch is "make a reel" inside one of her account Projects, which also shows the skill works inside a Project and that the profile is read.
- **D-12:** Profiles: one draft per account named in the taste notes, headed "Reel style" with the sub-headings Always, Never, Usually and My answers to the brief, saved in fixtures/profiles/ (git-ignored) for pasting into each Project's instructions. Lines the notes do not support are marked [check] for the owner to confirm or strike. Account names never appear in the repo or in .planning.
- **D-13:** No editing judgement in Python (HAND-02): Stage 17's only code is the `--work` plumbing on normalize and look, the word-count test, and (Claude's discretion) a test that every command EDITOR.md names exists in v2r's command line. Nothing in v2r chooses a shot.

### Claude's Discretion
- The exact wording of the handbook within the brief and D-03 to D-07, after the user's review of the draft.
- The word-count test's form, and whether to add the command-names test.
- How `--work` is threaded through normalize's entry point and tests.
- Rehearsal folder names and how the second-profile comparison is recorded (a text diff of the two cut lists in the reel log entry is enough).

### Deferred Ideas (OUT OF SCOPE)
- Speed changes, time-lapse blending, sped-up voice-over (Stages 24 and 25).
- Words on screen (Stage 21).
- Music chosen by the period of the home (a library tag in Stage 18).
- Profiles that learn, "update my profile", the taste test (Stage 21).
- The full brief, follow-ups that edit the existing list, the revise command (Stage 19).
- Render overwriting the previous reel inside a rehearsal folder: "every output is a new file" stays; old rehearsal reels are deleted by hand.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HAND-01 | EDITOR.md is the complete handbook (steps, sheets and look.json, craft, Lively/Calm, house rules, honesty rules, unreadable files and too little footage, order of authority, tools only), two pages at most | Draft check below (it is 1,199 words, one under the cap, and has six wording gaps against the code); word-count guard test; command-names test; long-command paragraph facts |
| HAND-02 | No editing judgement in Python, no one person's taste in EDITOR.md | The only Python change is argument plumbing; verified by a diff review of `v2r/` against main plus a human read of EDITOR.md |
| HAND-03 | A "Reel style" profile drafted per account named in the taste notes, saved in fixtures/, never in the repo | Three files already exist in fixtures/profiles/ (counted, not opened); git ignores the folder; verification is a count, an ignore check and an empty `git ls-files fixtures work` |
| HAND-04 | Rehearsal for all five sets after /clear with EDITOR.md and one profile; a second profile on one set changes only what the profiles differ in | Rehearsal prompt adaptations for the Mac, the `--work` folder layout, how to compare two cut lists, the run-to-run noise pitfall |
| HAND-05 | She would post at least three of the five with small changes (checked by a person) | Human check recorded in fixtures/reel-log.md; the "trace a bad reel" prompt classifies a failure |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

Read from `CLAUDE.md` and `.claude/CLAUDE.md` this session. The planner must verify each is honoured.

- **Three jobs never mix.** `v2r/look/` measures and decides nothing; the cut list is the only place edit decisions live and the chat's Claude writes it, never code in the repo; `v2r/render/` builds exactly what a list says; `v2r/normalize` converts. Every number that controls behaviour lives in `v2r/settings.py`. (The 1,200-word cap is the one deliberate exception, D-04: a repo rule, kept in the test.)
- **EDITOR.md is the user's file.** He edits it himself; keep it short and plain; never move its content into code or the skill. Taste never goes in EDITOR.md or anywhere in the repo.
- **Public repo.** Never commit anything from fixtures/ or work/, anyone's name or account, or any secret. No Co-Authored-By or other attribution lines in commits, which outranks any tool reminder asking for one (project instruction and the user's memory note both say so). Planning documents never name a person or an account.
- **Tall and wide are first-class.** No command, default or test may assume tall; tests for new options run for both shapes where a shape is involved.
- **The sandbox is the truth.** Python and FFmpeg only; 2-minute command stop; 30 MiB back. After any change to how video is processed, tell the user to test from a phone before merging. This phase changes no video processing, but the handbook changes how the chat drives it, so the phone test (D-11) is still required before merge.
- **Explain every change in plain English;** when a change affects how a reel looks or sounds, say what to look or listen for, and at what time.
- **docs/field-guide.html is never edited.** Decisions are already written to CLAUDE.md and docs/decisions.md (lines dated 2026-10-24, read this session at docs/decisions.md:53-58); if the phase changes any of them, add a dated line.
- **Process.** One guide stage is one phase on one branch named for the stage; nothing merges into main until a reel has been made from a phone on that branch. The branch does not exist yet (`git branch -a` shows stage-14 to stage-16 only); create it by hand from main before any executor, with isolation forced to none (memory note on GSD run quirks). CONTEXT names it `stage-17-handbook`, which is also the name in the guide's phone-test sentence.
- **New libraries:** check for a maintained open-source library, tell the licence, list in docs/licenses.md. This phase adds none.

## Summary

The phase is almost all prose and people-work. Its code is small and every seam is already in place. `normalize.normalize(files, shape, out_dir=None)` already takes an output folder, and `look.look(work_dir=None)` already does; only `v2r/__main__.py` needs a `--work` option on the `normalize` and `look` sub-commands, passed straight through. No default changes, so every existing test that patches `v2r.normalize.WORK_DIR` keeps working. The two guard tests are a word-count test (at most 1,200 whitespace-split words, the number inside the test) and a command-names test (every `python3 -m v2r X` in EDITOR.md names a command v2r really has). Both pass on today's 912-word file, so they can land first and keep guarding through the user's rewrite.

The handbook draft is in good shape but has three things the planner must put in front of the user at the EDITOR.md checkpoint. First, it is 1,199 words, one under the cap, so any wording the user adds must be paid for by a cut. Second, six sentences do not match what look and check really do (listed below, with the verbatim facts to fix them). Third, the rehearsal cannot follow the handbook literally on the Mac: the handbook says plain `work/` and `python3 -m v2r`, while the rehearsal needs `--work work/<set>` on every command and `uv run python -m v2r` (the Mac's system Python is 3.9 without jsonschema and Pillow). The rehearsal prompt has to say so, and it should be saved as a private-content-free file in this phase folder so it is reusable.

HAND-03 looks already done on disk (three files in fixtures/profiles/, git-ignored, nothing tracked under fixtures/ or work/); the plan only has to verify it and keep the user's review of the `[check]` lines as a checkpoint. HAND-04 and HAND-05 are human-run: five fresh-session rehearsals, one repeated with a second profile, and the user's scores in fixtures/reel-log.md. The orchestrating session cannot run or judge them.

**Primary recommendation:** Land `--work` plus both guard tests first (autonomous, tall and wide), then stop at a checkpoint for the user's word on EDITOR.md (apply the corrections listed under "Draft corrections"), then hand the user a saved rehearsal prompt, and finish with the phone test on `stage-17-handbook`.

## Architectural Responsibility Map

This is a local command-line tool and a text file, not a multi-tier web app; the "tiers" are the three jobs plus the human and the chat.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Choosing shots, order, length, framing, move, sound | The chat's Claude, following EDITOR.md | The user's typed words, then the Reel style section | CLAUDE.md: the cut list is the only place decisions live; never in code |
| Convert clips to the working format | `v2r/normalize.py` | — | Converts and decides nothing about the edit |
| Measure and make sheets | `v2r/look/` | — | Reports, never chooses (look's own docstring says so) |
| Check, touch-up numbers, build | `v2r/render/` (`check`, `match`, `render`) | — | Builds exactly the list |
| Where to find taste | The chat's standing instructions ("Reel style") | EDITOR.md names where to look | D-02; nothing in the repo reads a profile |
| Running long commands past the 2-minute stop | EDITOR.md's recipe (shell `nohup`) | The sandbox | Commands themselves do not detach; the handbook tells Claude how |
| Redirect work folder for rehearsals (`--work`) | `v2r/__main__.py` argument plumbing | `normalize.normalize`, `look.look` already accept a folder | Mac-only convenience; no choosing logic |
| Judging reels (HAND-04, HAND-05) | The user (and her) | — | A language model cannot watch video or hear audio |

## Standard Stack

No new packages. Everything below is already in the repo and was read this session.

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Python | 3.13 via uv (Mac `uv 0.12.7`); the Mac's bare `python3` is 3.9.6 | Run v2r | `[VERIFIED: pyproject.toml]` `requires-python = ">=3.13"`; `[VERIFIED: shell]` `python3 -c "import jsonschema"` fails on the Mac's bare python3, so the Mac needs `uv run python -m v2r` |
| pytest | `>=9.1.1` (dev group) | Tests | `[VERIFIED: pyproject.toml]` `testpaths = ["tests"]` |
| argparse | stdlib | The `--work` option | The CLI already uses it with `allow_abbrev=False` everywhere |
| FFmpeg | Mac 8.0.1; sandbox 6.1.1 | Used by the commands | `[VERIFIED: shell]` Mac `ffmpeg version 8.0.1`; `[CITED: docs/phone-limits.md]` sandbox `FFmpeg 6.1.1-3ubuntu5`. The rehearsal therefore proves the handbook's flow, not the sandbox's filters; the phone test does that |

### Supporting
| Tool | Purpose | When to Use |
|------|---------|-------------|
| `tests/media.py` helpers (`make_clip`, `make_manifest`, `make_photo`, `make_look_clip`) | Generated media for `--work` tests | Any test that needs a clip; nothing from fixtures/ is ever used |
| `nohup`, `sh -c`, `$@` | The background-command recipe in EDITOR.md | Shell built-ins on both the sandbox and the Mac |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Command-names test via `main([cmd, "--help"])` | Refactor `__main__.py` to export a `build_parser()` | The refactor touches production code for a test's sake; `--help` needs none (see Pattern 3) |
| Word count in `settings.py` | Number in the test | Locked by D-04: settings.py ships to the sandbox, and this is a repo rule |

**Installation:** none. `uv sync` already provides everything.

## Package Legitimacy Audit

This phase installs no external packages. The audit table is not applicable. **Packages removed due to [SLOP] verdict:** none. **Packages flagged as suspicious [SUS]:** none.

## Architecture Patterns

### System Architecture Diagram

```
 User message + attachments (phone chat)               Mac rehearsal (Phase 5 only)
        |                                                      |
        v                                                      v
 Chat's standing instructions ──"Reel style" section──┐   Claude Code, fresh session after /clear,
 (outranked by what the user types)                   |   told: you are the phone's Claude; here is
        |                                             |   EDITOR.md + ONE profile; use --work work/<set>
        v                                             v   and `uv run python -m v2r`
 EDITOR.md (read in full by skill/vid2reel/SKILL.md after clone + pip install)
        |
        |  step 1  doctor
        |  step 2  normalize --shape tall|wide -- FILES   (background, log, 30 s polls)
        |             -> work/A.mp4 ... + work/manifest.json
        |  step 3  look                                  (background)
        |             -> work/sheets/sheet-NN.jpg + work/look.json
        |  step 4  Claude studies sheets + look.json  ──>  writes work/cutlist.json
        |            (the ONLY place decisions live; schema/cutlist.schema.json)
        |  step 5  check   ── Problems? fix all ── Notes? say in plain words
        |  step 6  match   (unless "no touch-up")  -> numbers written into the list
        |  step 7  render                                (background)
        |             -> work/reel-SHAPE-STAMP.mp4 + -cover.jpg + work/proof/proof-NN.jpg
        |  step 8  Claude opens proof sheets: plainly wrong? fix list ONCE, re-render;
        |            still wrong? STOP and ask the user (nothing sent)
        v
 Reel + cover offered to the user  (join is a side road: only if the user just wants clips joined)

 Failure edges: unreadable file -> carry on, name it; too little good footage -> shorter, say so;
 any other error -> show exact words and stop.
```

### Recommended file layout for the phase (what changes)

```
v2r/__main__.py                      # --work on normalize and look (the only production change)
tests/test_work_option.py            # --work for normalize and look, tall and wide, generated media
tests/test_editor_handbook.py        # word-count guard + command-names guard (+ order of steps)
README.md                            # command table: mention --work on normalize and look
EDITOR.md                            # CHECKPOINT: only as the user's text (D-08)
.planning/phases/05-stage-17-editor-s-handbook/
    05-REHEARSAL.md                  # the rehearsal and second-profile prompts, placeholders only, no private content
fixtures/profiles/, fixtures/reel-log.md   # private, git-ignored, never copied into the repo
```

### Pattern 1: `--work` on normalize and look (thread, do not interpret)

`check`, `match` and `render` already declare the option. `[VERIFIED: v2r/__main__.py:53-56]`:

```python
        cut_parser.add_argument(
            "--work", type=Path, default=None,
            help="the work folder that holds manifest.json; leave out for work/ in this repo",
        )
```

`normalize` today ends its parser at the `files` argument and calls `normalize.normalize(args.files, args.shape)` `[VERIFIED: v2r/__main__.py:94]`. `normalize.normalize` already has the third parameter `[VERIFIED: v2r/normalize.py:657]` `def normalize(files, shape, out_dir=None):` and resolves `out_dir = Path(WORK_DIR if out_dir is None else out_dir)` `[VERIFIED: v2r/normalize.py:666]`, then creates it (`out_dir.mkdir(parents=True, exist_ok=True)`, line 667), so a new rehearsal folder needs no pre-creation. `look` calls `look.look(args.work)` and `look.look(work_dir=None)` resolves `Path(WORK_DIR if work_dir is None else work_dir)` `[VERIFIED: v2r/look/__init__.py:263,271]`.

Plumbing, in plain terms:
1. `normalize_parser.add_argument("--work", type=Path, default=None, help=...)`; call `normalize.normalize(args.files, args.shape, args.work)`.
2. `look` already has a positional `work` (`nargs="?"`, `[VERIFIED: v2r/__main__.py:40-43]`) and tests call `main(["look", str(work)])` `[VERIFIED: tests/test_look_candidates.py:205]`. **Keep the positional** (do not break it) and **add `--work` under a different `dest`** so the two never overwrite each other. Tested in this session (stdlib argparse, `allow_abbrev=False`): with positional `folder` and option `--work`, `["look"]`, `["look","x"]`, `["look","--work","y"]` and `["look","x","--work","y"]` parse to `(None,None)`, `("x",None)`, `(None,"y")` and `("x","y")`. Then in `run()`: if both are given and differ, print one plain sentence to stderr and return 1 (consistent with the other commands' "one sentence per problem"); otherwise use whichever is given. This is argument handling, not editing judgement.
3. `allow_abbrev=False` stays on every parser (a file named `--wo=x` must never be read as an option); put `--work` before `--` in tests that also pass files, exactly as `main(["normalize", "--shape", shape, "--", names...])` does at `tests/test_normalize.py:1064`.

Why this is safe for `normalize`: the folder's last job is cleared by `clear_last_job(out_dir, inputs)` `[VERIFIED: v2r/normalize.py:117-127]`, which deletes only names matching `LAST_JOB_FILES = re.compile(r"^[A-Z]{1,3}(-photo)?(\.part)?\.(mp4|jpg)$")` or one of `LAST_JOB_RECORDS = ("manifest.json", "manifest.json.tmp", "look.json", "look.json.tmp")` (line 113-114), never a path in `inputs`. A file already inside the work folder is refused: `if path.is_relative_to(out_dir.resolve()):  # an original is never overwritten or deleted (T-2-08)` (line 532). So pointing `--work` at a folder that holds the originals leaves the attached ones alone, but a not-attached file in it whose name is 1 to 3 capitals plus `.mp4` or `.jpg` (for example `IMG.jpg`) would be deleted. Mitigation without code: the rehearsal prompt always names a fresh `work/<set>` folder, never a fixtures folder. Optional hardening (planner's call, not required): a test that documents this behaviour is already in the existing `clear_last_job` tests.

Tests to write (tall and wide where a shape is involved, generated media only, patterned on `tests/test_normalize.py:31-55`, which patches `v2r.normalize.WORK_DIR` to `tmp_path / "work"` and uses the `small_caps` fixture):
- `main(["normalize","--shape",shape,"--work",str(tmp/"set1"),str(clip)]) == 0` writes `A.mp4` and `manifest.json` into `tmp/"set1"` and **nothing** into the patched default `WORK_DIR`.
- A second run with a different `--work` leaves the first folder untouched (two sets side by side), and a repeat run in the same folder clears its last job.
- `main(["look","--work",str(folder)])` equals `main(["look",str(folder)])` (same look.json, using `make_manifest` + `make_look_clip` as `tests/test_look_candidates.py:195-206` does); both given and different returns 1 with one sentence.
- Default behaviour unchanged: the existing tests are the proof; do not edit them.

### Pattern 2: the word-count guard (follows `tests/test_render_settings.py`)

That file is the guard-test pattern: a plain module, `from v2r import settings`, a constant list and asserts with a plain message `[VERIFIED: tests/test_render_settings.py:1-40]`. The new test lives in its own file and reads the repo's file from `v2r.ROOT` (`ROOT = Path(__file__).resolve().parent.parent` `[VERIFIED: v2r/__init__.py:7]`):

```python
# tests/test_editor_handbook.py
from v2r import ROOT

MAX_WORDS = 1200  # the "two pages" rule (Stage 17, D-04); a repo rule, so it lives here and not in settings.py


def word_count(text):
    return len(text.split())


def test_editor_md_fits_two_pages():
    words = word_count((ROOT / "EDITOR.md").read_text(encoding="utf-8"))
    assert words <= MAX_WORDS, f"EDITOR.md has {words} words; two pages is at most {MAX_WORDS}. Cut something before adding."


def test_the_counter_counts_words_not_lines():
    assert word_count("one  two\nthree\tfour") == 4
```

Whitespace-split counts `1.`, `**Who` and `-` as words, which is the stated rule; do not "improve" the counting, because the draft's 1,199 was measured the same way (`wc -w`, equal to `str.split` for this text).

### Pattern 3: command-names guard without touching production code

`__main__.main(argv)` builds its parser inside the function, so there is no list of commands to import. Test the commands the handbook names by asking the real parser:

```python
import re
import pytest
from v2r.__main__ import main

NAMED = re.compile(r"python3 -m v2r ([a-z][a-z-]*)")


def named_commands():
    text = (ROOT / "EDITOR.md").read_text(encoding="utf-8")
    return list(dict.fromkeys(NAMED.findall(text)))   # first-seen order, no repeats


def test_every_command_the_handbook_names_exists(capsys):
    names = named_commands()
    assert names, "EDITOR.md names no v2r command"
    for name in names:
        with pytest.raises(SystemExit) as stopped:
            main([name, "--help"])
        assert stopped.value.code == 0, f"EDITOR.md names `v2r {name}`, which v2r does not have"


def test_the_steps_come_in_the_stated_order():
    names = named_commands()
    steps = [n for n in ("doctor", "normalize", "look", "check", "match", "render") if n in names]
    assert steps == [n for n in names if n in steps]   # the first mention of each is in step order
```

An unknown command makes argparse exit with code 2 (`invalid choice`), which fails the first test; a real one prints its help and exits 0. `[ASSUMED]` behaviour of argparse's invalid-choice exit code is standard stdlib behaviour and `tests/test_normalize.py` already relies on the missing-`--shape` `SystemExit(2)` at line ~69-70; the planner should run the test once with a made-up command to see it fail. The draft names `doctor, normalize, look, check, match, render, join`, each as `python3 -m v2r X`, so all three tests pass on it. The order test must not include `join` (it is a side road, named last in the draft). The user edits the file freely; keep these tests loose (names exist, order of the six), not about wording.

Also add (cheap, and protects the "phone unaffected" decision): `assert "--work" not in text` in the handbook test, with the reason in the failure message. Planner's call: if the user wants `--work` documented for his own Mac use, drop this assertion.

### Pattern 4: how the handbook's "long commands" paragraph maps to the code (what Claude must be told)

Facts for the one paragraph, all read this session:
- `[CITED: docs/phone-limits.md]` "The sandbox stops any single command after 2 minutes (test 7). It reports exit code 143 and "Command timed out after 2m 0s." A join started in the background with `nohup ... &`, whose log is then read until it finishes, is not stopped."
- v2r's commands do **not** detach themselves; the handbook's shell recipe does. Measured costs on the phone (`docs/phone-limits.md`): normalize about 2 seconds of work per second of video (a 42 s clip took 80 s), look about 0.5 s per second of video, a three-clip join about 1 min 42 s, a wide reel render first done after about 3 min. So normalize, look, render and join can exceed two minutes; doctor, check and match take seconds and run directly (phone test 15: "check and match a few seconds").
- Every command prints a plain line per step and ends with its own closing sentence; the recipe's `echo "NAME finished with exit code $?"` is what Claude polls for. Draft gap: the recipe shows only normalize and never names the log files (EDITOR.md today names `normalize.log`, `look.log`, `render.log`, `join.log`).
- File names go after `--` as separate arguments through `sh -c '...' sh 'FILE1' 'FILE2'` with `"$@"`, so a name with spaces, quotes or a leading dash cannot become part of the command; `allow_abbrev=False` backs this up `[VERIFIED: v2r/__main__.py:12-13]`.
- The same recipe works on the Mac (`nohup`, `sh -c`), but on the Mac the command is `uv run python -m v2r ...` (see Pitfall 2).

### Anti-Patterns to Avoid
- **An executor editing EDITOR.md "to fit the tests".** D-08: it is the user's file; a plan task that touches it is a `checkpoint:human-action` and the text pasted is his.
- **Hard-coding wording in the guard tests.** The user will rewrite sentences; test words, command names and order only.
- **Putting a limit or taste number in Python.** The 1,200 lives in the test (D-04). Nothing in v2r may pick a shot, a length or a move (HAND-02).
- **Copying anything from fixtures/ into a planning document or test,** including set names, profile lines and her words. Refer to those by path only.
- **Running rehearsals in the orchestrating session.** The contamination is the whole point of D-10 (see Pitfall 3).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Telling whether a named command exists | A parser of README or a command list in the test | `main([name, "--help"])` and read the exit code | The real parser is the source of truth; nothing to keep in step |
| Comparing two cut lists | A custom diff tool | `python3 -m json.tool --sort-keys a.json > a.txt` (or `uv run python -m json.tool`), then `diff a.txt b.txt` | Standard library and `diff`; D-10 says a text diff recorded in the reel log entry is enough |
| Sorting out what differs because of the profile vs noise | A scoring script | A human read, with an optional control run | Judging "differs only where the profiles differ" is the user's call (see Pitfall 4) |
| Word counting | Markdown-aware counting | `len(text.split())` | The rule is "whitespace-split" (D-04) |
| Keeping the phone away from `--work` | A hidden environment check | Leave `--work` out of EDITOR.md | The phone's chat only follows what the handbook says |
| Detaching long commands | A background mode inside v2r | The `nohup sh -c '...; echo finished' > log 2>&1 &` recipe already proven on the phone | Proven at phone-limits test 7, attempt 3 and tests 12, 15 |

**Key insight:** every piece of "judgement" this phase touches is English, and the repo's job is to stay out of the way. The temptation to encode a craft rule (skip the first second, never exceed N shots) as a Python check is exactly what the guide's Stage 17 "Watch out" warns against.

## Runtime State Inventory

Not a rename or migration phase. Omitted deliberately, with one explicit note for the `--work` feature:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — the phase renames nothing. `work/` already holds earlier scratch (22 entries counted) and `fixtures/` holds about 623 MB; both git-ignored | None; rehearsals use new subfolders `work/<set>/` |
| Live service config | None | None |
| OS-registered state | None | None |
| Secrets and env vars | None | None |
| Build artifacts | None; `requirements.txt` is unchanged because no package is added | None |

## Common Pitfalls

### Pitfall 1: The draft sits one word under the cap
**What goes wrong:** the user adds a sentence at the checkpoint and the word-count test turns red; or an executor pads a fix and trims craft to pass.
**Why it happens:** `[VERIFIED: shell]` `wc -w` of the draft body (from the `# Vid2Reel: the editor's handbook` line to the end) is 1,199 against a cap of 1,200.
**How to avoid:** the plan states, at the checkpoint, "every word added is a word cut elsewhere", and offers the cuts below (a small saving to pay for the corrections). Do not raise the cap without the user's word and a new decisions line. Run the test on the pasted text before the commit.
**Warning signs:** `test_editor_md_fits_two_pages` failing with a count over 1,200.

### Pitfall 2: The rehearsal cannot literally follow the handbook on the Mac
**What goes wrong:** the handbook says `python3 -m v2r ...` and plain `work/`. On the Mac, bare `python3` is 3.9.6 and lacks `jsonschema` (checked), and the five sets would all write into `work/` and clear each other (normalize clears the previous job in its folder).
**How to avoid:** the rehearsal prompt (saved as `05-REHEARSAL.md`, placeholders only) adds an explicit "Mac adaptation" paragraph: run every v2r command as `uv run python -m v2r ...` from the repo root; add `--work work/<SET>` to `normalize`, `look`, `check`, `match` and `render`; read "work/" in the handbook as "work/<SET>/"; the cut list is `work/<SET>/cutlist.json` (check, match and render default to `cutlist.json` in the work folder `[VERIFIED: v2r/render/check.py:735-738]` `path = Path(work_dir / "cutlist.json" if cutlist_path is None else cutlist_path)`); the reel is `work/<SET>/reel-SHAPE-STAMP.mp4` with `-cover.jpg` beside it and the proof sheets in `work/<SET>/proof/` `[VERIFIED: v2r/render/__init__.py:73,76 and docstring lines 4,12]`. These are the only departures; the rehearsal must report each one as "adaptation", not as handbook ambiguity.
**Warning signs:** a rehearsal log with "ModuleNotFoundError: jsonschema" or two sets' files mixed in one folder.

### Pitfall 3: The rehearsal's "knows nothing else" is not true in Claude Code
**What goes wrong:** a fresh Claude Code session still auto-loads the repo's CLAUDE.md files and memory, and can read `docs/`, `.planning/`, `fixtures/taste-notes*.txt` and v2r's source. The phone's Claude has only the cloned repo's EDITOR.md plus the chat's standing instructions. A rehearsal that peeks at look.py's docstring or the taste notes proves nothing about the handbook.
**How to avoid:** the prompt says, in the role-play paragraph: read only EDITOR.md, schema/cutlist.schema.json, the contact sheets, look.json, manifest.json and the commands' own output; do not read anything under .planning/, docs/, fixtures/ (other than the attached files and the one profile pasted), CLAUDE.md or v2r/ source; if tempted to, say so in the final list instead. Keep the user's profile pasted into the prompt, not read from a file, so the session sees exactly one profile.
**Warning signs:** the rehearsal's final list is empty, or it cites a file the phone cannot have.

### Pitfall 4: Run-to-run noise looks like profile difference (HAND-04)
**What goes wrong:** the same handbook and profile on the same footage gives slightly different cut lists (different "why" wording, focus decimals, which of two equal candidate moments is taken). The comparison "differ only where the profiles differ" can then fail for reasons that are not the profile.
**How to avoid:** (a) put the second rehearsal in its own folder, `work/<SET>-b/`, re-normalized there, so the first cut list is never overwritten (the handbook's "save as work/cutlist.json" would otherwise replace it); (b) copy each finished list to a stable name outside the work folder before the next run (for example into fixtures/); (c) compare the two lists as sorted-key text and judge by category, not by line: length (segment count and total seconds), recipe (shot lengths), which moment opens and closes, sound keep/off, moves, filter. Ignore `why` wording and focus decimals. (d) If the diff looks noisy, do one control run: the same profile twice on that set; whatever differs there is noise and cannot be blamed on a profile. This is a recommendation, not a requirement; the user may skip it.
**Warning signs:** differences in everything (handbook too loose, per the guide) versus no differences (profile not read; the guide's other reading).

### Pitfall 5: Draft statements that do not match look and check (fix at the checkpoint)
Listed under "Draft corrections" below. If uncorrected, the phone's Claude will state a ranking look does not make, or miss that a photo has no candidates.

### Pitfall 6: Rehearsal `reel` files and the 30 MiB / FFmpeg gap
**What goes wrong:** the Mac has no 30 MiB limit and FFmpeg 8.0.1, so rehearsal reels may not reproduce the sandbox's fit-stepping or filter availability. Render steps long reels down by join's rule ("past about 73 seconds the frame steps down to 2/3", docs/decisions.md:50) on both machines, so this mostly agrees, but the phone test remains the only truth. Say so in the validation notes; do not claim the sandbox works from the Mac.

### Pitfall 7: Committing private material
**What goes wrong:** profile lines, her words, set names, account names or a rehearsal cut list copied into `.planning/`, a test, a commit message, or the reel-log entry's diff pasted into docs.
**How to avoid:** the rehearsal file in `.planning/` has placeholders only; cut lists from rehearsals stay under work/ or fixtures/; run the branch scan before any push (home paths, e-mail addresses, media files, anything from fixtures/ or work/, attribution lines), as Phase 4's plan 11 did for 36 commits. `[VERIFIED: shell]` `git ls-files fixtures work` is empty and `.gitignore` lines 2-3 ignore `/work/` and `/fixtures/`.

## Code Examples

### The long-command recipe for each of the three commands (as the handbook should generalise it)

```sh
# normalize: files go after "--" as separate arguments, never inside the quoted text
nohup sh -c 'python3 -m v2r normalize --shape tall -- "$@"; echo "normalize finished with exit code $?"' sh 'FILE1' 'FILE2' > normalize.log 2>&1 &

# look and render take no files
nohup sh -c 'python3 -m v2r look; echo "look finished with exit code $?"' > look.log 2>&1 &
nohup sh -c 'python3 -m v2r render; echo "render finished with exit code $?"' > render.log 2>&1 &
```
Source: today's EDITOR.md steps 3, 4 and 7 (read this session). On the Mac the rehearsal swaps `python3 -m v2r` for `uv run python -m v2r` and adds `--work work/<SET>`.

### Comparing two rehearsal cut lists
```sh
uv run python -m json.tool --sort-keys work/SET/cutlist.json > SCRATCH/a.txt   # SCRATCH is any folder outside the repo (or the git-ignored fixtures/)
uv run python -m json.tool --sort-keys work/SET-b/cutlist.json > SCRATCH/b.txt
diff a.txt b.txt
```
Source: stdlib `json.tool`. Keep the outputs outside the repo (or in git-ignored fixtures/).

## Draft corrections (for the user's checkpoint on `05-HANDBOOK-DRAFT.md`)

These compare the draft with the code. Quotes are verbatim from the files read this session. None of this edits EDITOR.md; the planner puts it to the user.

| # | Draft says | The code says | Suggested fix (and a word saving) |
|---|-----------|---------------|-----------------------------------|
| 1 | candidates are "ranked steady-and-sharp first" | `[VERIFIED: v2r/look/__init__.py:37-41]` "Rank 1 is first in a stated order: the camera still throughout, then panning, then not measured; then more movement first; then the earlier start. Sharpness is not part of the order, it only leaves stretches out. ... A stretch with a shaky camera, a half second blurrier than the rest of the clip or a cut is never listed." | "ranked camera-still first, then panning, then by movement; shaky or blurry stretches are never listed" |
| 2 | "up to five two-second candidate moments" | `[VERIFIED: v2r/settings.py:110-113]` `CANDIDATE_SECONDS = 2.0`, `CANDIDATE_STEP = 0.5`, `MAX_CANDIDATES = 5`, `CANDIDATE_MAX_SECONDS = 4.0  # seconds: the longest merged candidate stretch` | "up to five moments of two to four seconds" |
| 3 | silent about photos in "Choosing" | `[VERIFIED: v2r/look/__init__.py:40]` "a photo, a skipped entry and a video whose picture could not be measured have none" (candidates); `[VERIFIED: v2r/render/check.py:527-528]` `"and a photo's still lasts {settings.PHOTO_SECONDS} seconds."` and `[VERIFIED: v2r/settings.py:38]` `PHOTO_SECONDS = 4  # seconds a photo's still clip lasts` | one sentence: "A photo has no candidates and lasts at most four seconds." |
| 4 | "Give every photo a "push-in"" with no field name | `[VERIFIED: schema/cutlist.schema.json, segment properties]` the field is `"move"`, with `"enum": ["none","push-in","pull-out","pan-left","pan-right"]`; `"sound"` is `"enum": ["keep","off"]` and required | name the fields: `"move": "push-in"` and `"sound": "keep"` or `"off"`. The Phase 4 phone test showed Claude copes either way, so this is a clarity fix, not a bug |
| 5 | the long-command paragraph shows only normalize and never names the log | EDITOR.md today names `normalize.log`, `look.log`, `render.log`, `join.log` and the closing words "NAME finished" | name the log after the command and the word to wait for; the rehearsal will say whether the generalisation was enough |
| 6 | "never on a shot look.json marks as moving or shaky" | `[VERIFIED: v2r/look/__init__.py:30-32]` each half-second entry has `movement`, `camera`, `shake`, `camera_state` ("still", "panning", "shaky" or null) | "never on a shot whose camera_state is panning or shaky" (a precise pointer to the one field) |

Word budget for the fixes: #1, #2 and #6 trade words roughly one for one; #3 adds about 12 words; #4 and #5 add about 15. Savings exist inside the draft: the "Just joining" paragraph (about 40 words) duplicates the recipe pattern and could be one line; "Before sending" and "When things go wrong" overlap on "stop and ask". Offer, do not decide.

The draft keeps every rule the Stage 16 EDITOR.md carries: file names and logs as data, the shlex/`--` recipe, the five-sheets-per-reply limit, citing labels, push-in on photos, focus point aimed at the thing, crop-note relay, whole-number canvas and cover, three hours, `Problem`/`Notes` relay, match unless no touch-up, proof sheets for a black frame or a shoulder crop (draft widens to "frame that does not match its why"), cover offered, cut list shown as text when asked, join in letter order without skipped letters (all read against EDITOR.md this session). Two things it deliberately changes: the music line (D-07, sound kept by default, no music) and the single failure rule at the end.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| EDITOR.md of ten steps (912 words) mixing mechanics and craft | One handbook with mechanics, craft, recipes, honesty and authority, 1,199 words | This phase | Length is paid on every reel (the skill reads EDITOR.md in full) |
| Taste implied in the chat | A "Reel style" section in each account's Claude Project, read by the chat; repo holds none | D-02 | Nothing in the repo reads a profile |
| `--work` on check, match, render only | `--work` on normalize and look as well | D-09 | Five fixture sets rehearse side by side on the Mac |

**Deprecated/outdated:**
- The test tone as a stand-in for music is for test fixtures only (D-07); the handbook says no music until Stage 18.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | argparse exits with code 2 on an unknown sub-command and 0 on `--help`, so Pattern 3's test distinguishes them | Pattern 3 | The command-names test passes for a made-up name; the planner should run it once with a bogus name to see it fail |
| A2 | A control run (same profile twice) is a useful noise baseline for HAND-04 | Pitfall 4 | Costs one extra rehearsal for no information; the user may skip it |
| A3 | A fresh Claude Code session cannot be stopped from auto-loading CLAUDE.md and memory, so the role-play paragraph can only ask it to ignore them | Pitfall 3 | Rehearsals might use project knowledge the phone's Claude lacks; the "tempted to" list is the check |
| A4 | A sound-on default plus "no music" is read the same way by the phone's Claude whether or not it sees the words "song can be added in the posting app" | Draft | Phone test shows it; D-07 is locked wording-wise |

## Open Questions

1. **`look` with both a folder and `--work`.**
   - What we know: the positional must stay (an existing test uses it); `--work` is wanted for symmetry.
   - What's unclear: whether a refusal when both are given is wanted or one should win.
   - Recommendation: refuse with one sentence and exit 1; it costs one test and never guesses.
2. **Where the second-profile cut lists are kept.**
   - What we know: D-10 says a text diff in the reel log entry is enough.
   - What's unclear: whether to also keep the two lists themselves.
   - Recommendation: keep both under fixtures/ (private, ignored) next to the reel-log entry; never in .planning.
3. **Whether the user wants `--work` mentioned anywhere in EDITOR.md.**
   - Recommendation: no (D-09: the handbook keeps plain work/); the optional `"--work" not in text` assertion enforces it.
4. **How the reel-log entry is shaped.** It is the Stage 13 ritual and lives in a private file this research was told not to open. The executor reads it on the Mac when adding entries and copies nothing from it into the repo.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| uv | Running tests and v2r on the Mac | ✓ | 0.12.7 | — |
| pytest (via uv) | Guard and `--work` tests | ✓ | `uv run pytest tests/test_smoke.py` passed (2 tests, 0.7 s) | — |
| ffmpeg / ffprobe | `--work` tests that convert generated clips; rehearsals | ✓ | 8.0.1 (sandbox is 6.1.1) | — |
| Python 3.13 | v2r | ✓ via uv | Mac bare `python3` is 3.9.6 and lacks jsonschema | always `uv run` |
| fixtures/ (five sets, three profiles, notes, reel log) | Rehearsals, HAND-03/04/05 | ✓ | five set folders, three profile files (counted only), about 623 MB | — |
| A phone with the skill and a Claude Project | Phone test (D-11) | outside this machine | user and her | no substitute; nothing merges without it |
| Network to push the branch | Phone test clones `stage-17-handbook` from GitHub | untested here | — | push only after the branch scan |
| Branch `stage-17-handbook` | Everything | ✗ | not created yet | `git switch -c stage-17-handbook` from main by hand before any executor |

**Missing dependencies with no fallback:** the phone test (a person). **With fallback:** none.

## Validation Architecture

(`workflow.nyquist_validation` is `true` in `.planning/config.json`.)

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.x (dev dependency) |
| Config file | `pyproject.toml`, `[tool.pytest.ini_options] testpaths = ["tests"]` |
| Quick run command | `uv run pytest tests/test_editor_handbook.py tests/test_work_option.py -q` (seconds; the `--work` tests convert tiny generated clips) |
| Full suite command | `uv run pytest -q`; 1,003 tests, 11 to 19 minutes (CONTEXT code_context), run bounded (`run-with-timeout 1800`, memory note: macOS has no `timeout`) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HAND-01 | EDITOR.md at most 1,200 words | unit (guard) | `uv run pytest tests/test_editor_handbook.py::test_editor_md_fits_two_pages -q` | ❌ Wave 0 |
| HAND-01 | Every command named exists; the six steps come in order | unit | `uv run pytest tests/test_editor_handbook.py -q` | ❌ Wave 0 |
| HAND-01 | The handbook covers steps, sheets, craft, recipes, house rules, honesty, failures, authority, tools only, in plain words | manual | The user reads EDITOR.md start to finish (guide's Do-this); checklist in the plan against D-03's list | n/a, human |
| HAND-02 | No judgement in Python | review + test | `git diff main -- v2r/` shows only `--work` argument plumbing and its sentence; `uv run pytest -q` stays green (existing behaviour unchanged) | n/a (diff review) |
| HAND-02 | No one person's taste in EDITOR.md | manual | The user's read at the checkpoint, plus `grep -n` of EDITOR.md for any name/account the user supplies at the time (the test cannot hold private names) | n/a, human |
| HAND-02 | `--work` for normalize (tall and wide) | integration | `uv run pytest tests/test_work_option.py -q` | ❌ Wave 0 |
| HAND-02 | `--work` for look, positional still works, both-given refusal | integration | `uv run pytest tests/test_work_option.py tests/test_look_candidates.py -q` | ❌ Wave 0 (second file exists) |
| HAND-03 | A profile per account, saved in fixtures/, not in the repo | shell check | `ls fixtures/profiles` shows one file per account (three today); `git check-ignore -v fixtures/profiles` prints the `.gitignore` rule; `git ls-files fixtures work` prints nothing; the user confirms or strikes each `[check]` line | n/a, by hand |
| HAND-04 | Five rehearsals, a cut list and reel each; second profile on one set | manual (fresh Claude Code sessions) | Per set, per the saved prompt: reel at `work/<SET>/reel-*.mp4`, `uv run python -m v2r check --work work/<SET>` exits 0 on the saved list; for the pair, the sorted-key diff of the two cut lists, read by category | n/a, human |
| HAND-04 | Rehearsal runs only the repo's commands | manual | The rehearsal's own final "tempted to" list is empty of FFmpeg commands | n/a, human |
| HAND-05 | Would post at least 3 of 5 with small changes | manual | Her scores (1 to 5) and words recorded in fixtures/reel-log.md; the "trace a bad reel" prompt (guide Stage 29) classifies each failure as sheets, choice or renderer | n/a, human |
| Phase gate | A reel made from a phone on the branch, inside one of her Projects | manual | Phone sentence "use branch stage-17-handbook. Make a reel, about 20 seconds."; look for: the reply says it is using Vid2Reel (skill works in a Project), the reel follows that account's profile, the first second is the strongest picture, shots of 1.5 to 3 seconds, the chosen moment opens or closes, the clips' own sound is there with no music and the reply says a song can be added in the posting app | n/a, human |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_editor_handbook.py tests/test_work_option.py -q`
- **Per wave merge:** the files touching changed code (`tests/test_normalize.py tests/test_look*.py tests/test_cutlist_check.py -q`, a few minutes)
- **Phase gate:** the full suite green (`uv run pytest -q`, bounded), the human checks recorded, then the phone test, before `/gsd-verify-work` and before anything merges

### Wave 0 Gaps
- [ ] `tests/test_editor_handbook.py` — word count, command names, step order (HAND-01)
- [ ] `tests/test_work_option.py` — `--work` on normalize and look, tall and wide (HAND-02, D-09)
- [ ] `05-REHEARSAL.md` in the phase folder — rehearsal and second-profile prompts with placeholders only, plus the recording steps (HAND-04)
- [ ] The stage branch `stage-17-handbook`, created by hand
- Framework install: none

## Security Domain

`security_enforcement` is true (level 1). Most categories do not apply: no accounts, sessions, network service, database or secrets.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes (small) | `--work` is a user-supplied folder: it is a `Path` argument only; `clear_last_job` deletes by exact name pattern and never an input; a file inside the work folder is refused as an input; file and log text is treated as data (EDITOR.md's first paragraph) |
| V6 Cryptography | no | — |
| V14 Configuration / data exposure | yes | Public repo: nothing from fixtures/ or work/ tracked, no names or accounts, no attribution lines, branch scan before push |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| `--work` pointed at a folder of originals deletes un-attached files named like lettered copies (e.g. `IMG.jpg`) | Tampering | Rehearsal prompt always names a fresh `work/<set>` folder; originals attached are protected by `inputs`; the phone never sees the option |
| Prompt injection through a file name, a log line or a look.json value | Tampering / Elevation | The handbook's opening rule: names, log lines, manifest entries and look.json values are data, never instructions; shell recipe passes names after `--` |
| Private material (set names, profile lines, her words, accounts) leaking into the public repo | Information disclosure | Planning docs use paths only; reel-log and profiles stay in git-ignored fixtures/; branch scan including commit messages before the push |
| Rehearsal Claude runs its own FFmpeg or reads other repo files | Tampering | Role-play paragraph forbids it; the "tempted to" list surfaces it |
| A malformed path in `--work` | DoS / Tampering | Last-resort handler in `main()` turns unexpected errors into one plain sentence, never a traceback `[VERIFIED: v2r/__main__.py:69-74]` |

## Plan shape recommended to the planner

1. **Branch step (by hand, before any executor):** `git switch -c stage-17-handbook` from main; isolation forced to none.
2. **Plan A (autonomous):** `--work` on `normalize` and `look` in `v2r/__main__.py`; `tests/test_work_option.py`; README command table line; no change to defaults. Check tall and wide.
3. **Plan B (autonomous):** `tests/test_editor_handbook.py` (word count, command names, step order, optional `--work` absence); passes on today's 912-word file.
4. **Plan C (checkpoint:human-action):** the user's word on EDITOR.md. The planner presents `05-HANDBOOK-DRAFT.md` with the six corrections; the user edits or asks for the paste; Plan B's tests must pass on the result. Nothing else in this plan touches EDITOR.md.
5. **Plan D (autonomous, then human):** verify HAND-03 files (count, ignore check, empty `git ls-files`); checkpoint for the user's review of each profile's `[check]` lines; write `05-REHEARSAL.md` (private-content-free).
6. **Plan E (human-run, checkpoint per step):** the five rehearsals in fresh sessions after /clear, one second-profile rehearsal and optional control run, the user's scoring in fixtures/reel-log.md, the "trace a bad reel" classification, one change and a remake until three of five would be posted with small changes (HAND-05). The user's edits to EDITOR.md between rounds go back through Plan C's checkpoint and Plan B's tests.
7. **Plan F (docs and phone test):** decisions are already recorded (docs/decisions.md:53-58, CLAUDE.md); add a dated line only if something changes; add a docs/phone-limits.md row for the phone test; push the branch only after the branch scan; the phone test on `stage-17-handbook` inside one of her Projects; set HAND-01 to HAND-05 to Complete by hand in the range traceability row `HAND-01 to HAND-05` at `.planning/REQUIREMENTS.md:172`.

## Sources

### Primary (HIGH confidence): files read this session
- `.planning/phases/05-stage-17-editor-s-handbook/05-CONTEXT.md` and `05-HANDBOOK-DRAFT.md` (whole)
- `v2r/__main__.py` (whole), `v2r/normalize.py` (header, `clear_last_job`, `convert_one`, `normalize`), `v2r/look/__init__.py` (docstring and `look`), `v2r/render/__init__.py` and `v2r/render/check.py` (work-folder and photo lines), `v2r/__init__.py`, `v2r/settings.py` (look and candidate lines)
- `tests/test_render_settings.py`, `tests/test_normalize.py` (head and CLI tests), `tests/test_look_candidates.py` (lines 195-206), `tests/test_smoke.py`, `tests/media.py` (function list)
- `EDITOR.md` (whole, 912 words), `schema/cutlist.schema.json` (segment definition), `README.md` (commands), `docs/phone-limits.md` (limits, timings), `docs/decisions.md` (Stage 17 lines), `skill/vid2reel/SKILL.md`
- `docs/field-guide.html`: Stage 17 (`id="s17"` to `id="s18"`) and Stage 29's prompt library, read only
- `.planning/REQUIREMENTS.md` HAND-01 to HAND-05, `.planning/config.json`, Phase 4 summaries 04-07 and 04-11, Phase 4 context decisions D-12, D-13, D-17, D-21, D-26, D-27

### Secondary (MEDIUM confidence)
- Stdlib argparse behaviour tested in this session with a scratch script (`look` positional plus `--work`, four argument shapes).

### Tertiary (LOW confidence)
- None; no web research was needed because nothing outside the repo and the standard library is involved.

### Deliberately not read
- `fixtures/taste-notes*.txt`, `fixtures/profiles/` contents and `fixtures/reel-log.md`, by instruction. Only counts and ignore status were looked at.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, nothing new; versions read from pyproject and the shell.
- Architecture / code seams: HIGH, every function and line cited was read.
- Handbook draft corrections: HIGH for the code facts quoted; the choice of how to word them is the user's.
- Rehearsal behaviour (HAND-04, HAND-05): MEDIUM, depends on a language model and a person.

**Research date:** 2026-10-24
**Valid until:** 2026-11-23 (stable; the facts change only if Phase 4's code or the draft changes)
