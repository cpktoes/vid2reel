---
phase: 07-stage-19-conversation
plan: "03"
subsystem: render
tags: [revise, cut-list, cli, reorder, drop, cover, tests]

requires:
  - phase: 07-stage-19-conversation
    provides: "plan 01's revise machinery (reading, numbering, writing, reporting, CHANGES table)"
provides:
  - "python3 -m v2r revise reorder ORDER: the shots in a new order, every shot number once; starting with a shot is a reorder"
  - "python3 -m v2r revise drop C and revise drop shot N: a clip's shots or one shot taken out"
  - "revise.parse_shot_list (plan 04 reuses it for --from), revise.follow_cover, DROP_WORDS, LAST_SHOT"
affects: [07-04, 07-07]

actuals:
  tokens: 14000
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "one shared cover rule: an old-to-new shot-number map, None for a shot taken out"
    - "the survivors and the reordered shots are the very same records, never rebuilt"

key-files:
  created: []
  modified:
    - v2r/render/revise.py
    - v2r/__main__.py
    - tests/test_revise.py

key-decisions:
  - "A list of shot numbers is checked item by item before any is used; letters, blanks and over-long numbers get one sentence saying what a list looks like"
  - "drop never touches the clips block or the touch-up; check never requires a clip to have a shot, so the list still passes"
  - "A drop that leaves a reel under 3 seconds is written and check says so (exit 1); a drop that leaves no shots is refused"
  - "tests/test_revise.py's setup gives the wide example a cover on shot 2, so the cover rule is tested in both shapes"

requirements-completed: []

duration: 25min
completed: 2026-11-03
status: complete
---

# Phase 7 Plan 03: revise reorder and revise drop Summary

**`revise reorder 3,1,2,...` plays the very same shot records in a new order and `revise drop C` / `revise drop shot 3` takes out a clip's shots or one shot; the cover follows its shot (renumbered, or removed with it) and revise says which.**

## What was built

- **reorder.** `revise reorder ORDER` needs every shot number once. The new list holds the original shot records, with every field and key in the original order; only their places change. "Start with that shot" is the same thing: that number first, the others in their old order. A reorder to the order the list already has writes nothing and says so.
- **drop.** `revise drop C` removes every shot of clip C; `revise drop shot N` removes shot N. The surviving shots are the original records in their original order. The clips block and the touch-up are left alone: check never asks a clip to have a shot, so the new list passes check. The output says which shots went, and that the clip's record (and touch-up) stay unused.
- **The cover rule (`follow_cover`).** When the cover's shot moves, its shot number is changed and revise prints "The cover moved with its shot: it was in shot 4, now shot 1." When the cover's own shot is taken out, the cover is removed and revise prints that the reel's first frame is the cover now. A cover that is missing or not usable is left for check to report.
- **Refusals, one plain sentence each, nothing written:** a missing, repeated, zero, too-high or non-number shot; a list that is not numbers (`a,b`, `1,,2`, empty); more numbers than a list can hold (refused before any is converted); a clip letter the shots do not use (the sentence names the letters they do use); wrong drop words; taking out every shot. A clip in the clips block with no shot is "nothing to drop" (exit 0, no file). A one-shot list: `reorder 1` changes nothing, `drop shot 1` is refused.
- **A reel left under 3 seconds** is written, check prints "The reel is 2.0 seconds long; it must be at least 3 seconds.", and revise exits 1.
- revise decides nothing: the order and the shot or clip come only from the command's words.

## Task Commits

1. Task 1 (tracer): `65feb42` test(07-03) failing tests, then `304185b` feat(07-03) reorder and the cover rule
2. Task 2: `0a2780b` test(07-03) failing tests, then `227bbff` feat(07-03) drop

## Tests

- `tests/test_revise.py`: 116 tests (was 61), each run for both tall and wide.
- `tests/test_revise.py`, `tests/test_cutlist_check.py`, `tests/test_render_settings.py` together: 406 passed. The render block in settings.py is unchanged (its 34-name count holds); this plan added no setting. The full suite was not run.
- The tests compare whole records including key order (`list(a.items()) == list(b.items())`), the clips block and touch-up before and after a drop, and everything outside the segments and the cover before and after.

## Deviations from Plan

None - plan executed exactly as written. Two small notes:

1. **A reorder-count sentence nobody can reach.** Because every item must be a valid, unrepeated shot number, a list of the wrong length can only be a short one, so "this list has 1 shot" is never printed for a one-shot list (`reorder 1,2` gets the no-shot sentence first). The sentence is kept for the wording the plan asked for.
2. **Tracer gate.** The tracer's check is fully automated and passed, so execution went straight on to drop.

## Known edges

An order or `--from` word starting with a minus and a comma (such as `-1,2`) is stopped by argparse with exit 2 and its usage text, not by revise's one sentence; nothing is written. The chat's Claude never writes a minus in a shot list. (A plain `-1` for `drop shot` also stops at argparse for the same reason.)

## Known Stubs

None.

## Threat Flags

None. The register's three items are covered: the order list's length is checked before anything is converted (T-7-04), the cover is renumbered or removed and printed, with tests for a reorder, an earlier drop and the cover's own shot (T-7-08), and clip letters are matched against `[A-Z]{1,3}` before use while any other echoed text passes through `check.shown` (T-7-03).

## What to check from a phone

Nothing in this plan changes how a reel looks or sounds, and nothing renders. A phone test comes when the handbook starts using revise.

## Self-Check: PASSED

- v2r/render/revise.py has `def follow_cover(`, `def parse_shot_list(` and `"drop": change_drop`: found
- commits 65feb42, 304185b, 0a2780b, 227bbff: found in git log
- EDITOR.md and docs/field-guide.html: not touched

## Plain English for the user

Two more follow-ups now work. "Start with the one where the dog runs in" becomes a reorder: the shots play in a new order, but each shot is exactly the same stretch of video, with the same framing and sound as before. "Drop that clip" takes out every shot of that clip, or you can take out just one shot. If the cover picture belonged to a shot that moved, it moves with it; if its own shot is taken out, the reel's first frame becomes the cover, and revise says so. If a drop would leave nothing, or you name a clip or shot that is not there, you get one plain sentence and nothing is saved. If a drop leaves a reel shorter than 3 seconds, the new plan is saved but the check tells you it is too short. One rough edge: a shot list that begins with a minus sign gets an argparse usage message instead of a plain sentence; nothing is saved, and it will not come up in practice.
