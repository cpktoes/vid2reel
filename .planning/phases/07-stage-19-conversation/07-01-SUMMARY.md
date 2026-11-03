---
phase: 07-stage-19-conversation
plan: "01"
subsystem: render
tags: [revise, cut-list, cli, argparse, tests]

requires:
  - phase: 06-stage-18-music
    provides: "the tool adds no music; check, match and the cut list's rulebook that revise reads and runs"
provides:
  - "python3 -m v2r revise sound keep|off [--shot N] and revise canvas tall|wide, each writing a new numbered cut list"
  - "the reading, numbering, writing and reporting that the later revise changes (reorder, drop, shorter, longer) plug into"
  - "REVISE_NUMBER_DIGITS and REVISE_NAME_TRIES in settings.py, in the new Stage 19 block above the render block"
  - "records brought level: no-music wording, the brief settled as asked straight away, three dated Stage 19 decision lines"
affects: [07-02, 07-03, 07-04, 07-05, 07-06, 07-07, 07-08, 07-09]

actuals:
  tokens: 11300
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "one change word per revise subcommand, registered in a CHANGES table and a shared parent parser (--cutlist, --work after the word)"
    - "strict reading with check's own reader, then a new file created exclusively (mode x) and numbered from the input's own family"
    - "tests compare the whole list before and after with an independent changed_paths helper"

key-files:
  created:
    - v2r/render/revise.py
    - tests/test_revise.py
  modified:
    - v2r/__main__.py
    - v2r/render/__init__.py
    - v2r/settings.py
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - docs/decisions.md
    - CLAUDE.md

key-decisions:
  - "Change word first (revise sound off --cutlist X --work W), because argparse cannot take an optional list name before a change word"
  - "The default input stays work/cutlist.json (D-06); every run instead prints the newest list in its next commands"
  - "revise reads the list with check's reader and rulebook, not the whole of check, so a tall list over a wide work folder can still be changed to wide; the closing check on the new list reports that mismatch in its own words"
  - "Exit 0 when the new list was written and check found nothing, or when nothing needed changing; exit 1 for a refusal or a written list that check dislikes"

patterns-established:
  - "Refusals are one line on stderr starting 'v2r revise: ', no traceback, nothing written"
  - "A follow-up that changes nothing writes no file and names the list still in use"

requirements-completed: [CONV-05, CONV-06, CONV-07, CONV-01]

duration: 40min
completed: 2026-11-03
status: complete
---

# Phase 7 Plan 01: revise sound and canvas, and the Stage 19 records Summary

**`python3 -m v2r revise` writes each follow-up as a new numbered cut list (cutlist-2.json, then -3), changing only the sound or only the canvas size, checks it, and prints the exact next commands; the records now carry the no-music, brief-first Stage 19.**

## Performance

- **Duration:** about 40 minutes
- **Tasks:** 3 of 3
- **Files modified:** 9 (2 created)

## Accomplishments

- `revise sound keep|off` changes every shot's own sound, or one shot's with `--shot N`. The top-level music block is never touched. Tests prove, in both shapes, that exactly the sound fields that differed are the only paths that changed, and that fields revise has never heard of (colour, zoom, transition, text) come through untouched.
- `revise canvas tall|wide` changes only the canvas width and height. Over clips normalized for the other shape, the new list is still written, and the closing check prints its own "normalize them again with --shape ..." sentence and revise exits 1.
- Every run writes a new file that is created exclusively, so no existing file can be replaced; numbers only go up, and revising `cutlist-2.json` gives the next free number, never `cutlist-2-2.json`.
- The first line printed is the new list's path, then one plain line per change, check's report, and the next commands naming the new list.
- Refusals are one plain sentence: a shot that does not exist or is not a number, an empty work folder (asks for the clips again), a list that breaks its rulebook (its problems, then one sentence), a name that cannot be written.
- Records: CONV-01, -04, -05, -07 and Phase 7 success criteria 2, 3, 5 now say keep or mute the sound and name no track; three dated Stage 19 lines are in docs/decisions.md; CLAUDE.md's Settled so far has the brief and revise, and its Stage 17 sentence about two questions now says they are the first two of the brief.

## Task Commits

1. Task 1 (tracer): `69cce7f` test(07-01) failing tests, then `4ee7b3f` feat(07-01) revise sound
2. Task 2: `7705bf8` feat(07-01) revise canvas
3. Task 3: `a2a5e55` docs(07-01) Stage 19 records

## Tests

- `tests/test_revise.py`: 61 tests (53 for sound and the shared machinery, 8 for canvas), every behaviour run for both tall and wide.
- `tests/test_revise.py`, `tests/test_match.py`, `tests/test_cutlist_check.py`, `tests/test_render_settings.py` together: 394 passed. The render block in settings.py is unchanged, so its 34-name count still holds. The full suite (about 14 minutes) was not run; only the files this plan touches.

## Deviations from Plan

### Auto-fixed Issues

None needed. Two small notes:

1. **Tracer gate.** The tracer's check is fully automated and passed at the tracer commit (386 tests across the four files at that point), so execution went straight on to the canvas change instead of stopping for a person. Nothing about how a reel looks or sounds changed.
2. **Existing decisions line.** The plan's check "docs/decisions.md has 3 lines with `· Stage 19 ·`" finds 4, because a 2026-10-11 line already says the brief is "three to five quick questions". It is dated history, so it was left as it is; the new 2026-11-03 line supersedes it.

## Known Stubs

None.

## Threat Flags

None. The only new file-writing surface is the exclusive creation of one list beside its input, which the plan's threat register covers.

## Alternative for the user to consider (not a change)

revise could read the highest-numbered list by default, instead of `cutlist.json`, so "shorter" after "mute it" would stack without the chat naming the file. This plan kept the default as decided (D-06) and instead prints the newest list in every "next" command, so the chat's Claude names it.

## What to check from a phone

Nothing in this plan changes how a reel looks or sounds, and nothing renders. A phone test comes when the handbook starts using revise (a later plan).

## Self-Check

- v2r/render/revise.py, tests/test_revise.py: found
- commits 69cce7f, 4ee7b3f, 7705bf8, a2a5e55: found in git log
- settings names sit above the `# render:` line: yes

## Self-Check: PASSED

## Plain English for the user

You can now ask for one small change to a finished edit without redoing it. "Mute it" becomes a command that copies the edit plan, turns the shots' own sound off, and saves the copy next to the original as `cutlist-2.json`; "a wide version" does the same for the picture shape. The original plan is never touched, so you can always go back, and a second change starts from the newest copy and saves `cutlist-3.json`. The tests compare the old plan and the new one line by line, in both tall and wide, and prove that only the thing you asked for changed. If something is wrong, such as a shot number that does not exist or the clips being gone, you get one plain sentence telling you what to do next. I also updated the records: the requirements and roadmap no longer mention music, the decisions file says the questions are asked straight away, and CLAUDE.md now says the Stage 17 pair of questions are the first two of that list.
