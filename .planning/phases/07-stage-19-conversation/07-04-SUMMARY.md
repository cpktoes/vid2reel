---
phase: 07-stage-19-conversation
plan: "04"
subsystem: render
tags: [revise, cut-list, cli, shorter, longer, frame-arithmetic, tests]

requires:
  - phase: 07-stage-19-conversation
    provides: "plan 01's revise machinery, plan 02's recipes (RECIPES, DEFAULT_RECIPE), plan 03's parse_shot_list and follow_cover"
provides:
  - "python3 -m v2r revise shorter --to SECONDS --from SHOTS: the named shots trimmed from their ends, to the frame, within the recipe"
  - "python3 -m v2r revise longer --to SECONDS --from SHOTS: the named shots run on at their ends, within the recipe, the clip and the next shot of the same clip"
  - "revise.shorter_frames, longer_frames, set_frames, seconds_text, parse_target, CannotShorten, change_shorter, change_longer"
  - "REVISE_SECONDS_DIGITS, REVISE_FRACTION_DIGITS, REVISE_DECIMALS, REVISE_DECIMALS_EXACT, REVISE_SHOWN_DECIMALS in settings.py's Stage 19 block"
affects: [07-07]

actuals:
  tokens: 60000
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "frame arithmetic is a pure function over lists of whole frames; the command only reads the list and writes the result"
    - "a shot's length is written by keeping `from` and writing `to`, then checked against the same frame rules check and render use"

key-files:
  created: []
  modified:
    - v2r/render/revise.py
    - v2r/__main__.py
    - v2r/settings.py
    - tests/test_revise.py

key-decisions:
  - "set_frames needed a third try: a start exactly half way into a frame (0.05 s) cannot be matched by 3 or 6 decimals, so the end is then rounded up at the last place"
  - "The dropped-shots sentence lists the shots in the order they were named (7 and 6), the lines about each dropped shot are in the order they were dropped"
  - "A single named shot that cannot grow gets 'Shot N cannot run longer, being at ...' instead of 'None of shots N ...'"
  - "The cover is removed for a trimmed-away moment only when its own shot actually got shorter, so a cover check already dislikes is left for check to report"

requirements-completed: []

duration: 45min
completed: 2026-11-03
status: complete
---

# Phase 7 Plan 04: revise shorter and revise longer Summary

**`revise shorter --to 15 --from 6,2` trims the shots Claude names, weakest first, from their ends down to the recipe's shortest and shares the rest evenly, landing on the length asked to the exact frame; `revise longer` is the mirror and never runs into footage the next shot shows.**

## What was built

- **shorter.** Claude names the target length and the shots to take it from, in order. Every shot keeps its first frame; only the end moves. The named shots go down to the recipe's shortest (45 frames for Lively, 90 for Calm), one after the other. If more is needed, it is shared evenly across the other shots: equal shares, and if a few single frames are left over they come off the later shots. Whole shots are dropped only when even every shot at its shortest is over the target, from the end of the named list, never shot 1 and never a shot that was not named. If the named list runs out first, it refuses and writes nothing. When a drop overshoots, the other shots are left untrimmed and revise says how far under the target the reel is.
- **The cover.** If the moment chosen for the cover is trimmed away, the cover is removed and revise says the reel's first frame is the cover now. A cover on a shot that was dropped or moved is handled by plan 03's rule.
- **longer.** The named shots, in order, each gain frames at their ends up to the recipe's longest (a photo may run to its whole clip), never past the end of the clip, and never past the first frame of a later shot of the same clip. If it cannot reach the target it writes what it reached and says how far short it is and that the rest needs a new moment added to the list. If no named shot can grow, it writes nothing and says so. It reads the work folder's manifest, and refuses (printing "Problem:" lines) if the list's clips no longer match it.
- **No-ops and refusals,** each one sentence, nothing written: a target equal to the current length (exit 0), a target the other way (names the other word), a target under 3 seconds, and a length that is not a plain number of seconds (`abc`, `-1`, `nan`, `1e3`, `0`).
- **Numbers.** The five new numbers revise reads and writes by (how many digits a length may have, how many decimal places it writes and prints) are in settings.py's Stage 19 block, above `# render:`. The render block is unchanged and its 34-name test passes.

## The worked example (check it by hand)

The approved tall reel has seven shots of 90, 75, 90, 90, 90, 75 and 90 frames: 600 frames, 20 seconds (30 frames a second). `revise shorter --to 15 --from 6,2` asks for 450 frames, 150 fewer.

1. Shot 6 (75 frames) goes to Lively's floor of 45: 30 frames off. Shot 2 (75 frames) likewise: 30 off. That is 60 of the 150.
2. The 90 frames still to go are shared across the five other shots, 18 each: 90 becomes 72.
3. Result, in order: **72, 45, 72, 72, 72, 45, 72** = 450 frames = 15 seconds exactly.

Each shot still starts on the very same frame as before.

## Task Commits

1. Task 1 (tracer): `06c29aa` test(07-04) failing tests, then `111c08c` feat(07-04) revise shorter
2. Task 2: `cc78eee` test(07-04) failing tests, then `65993a6` feat(07-04) revise longer

## Tests

- `tests/test_revise.py`: 206 tests (was 116), the shorter and longer behaviours run for both tall and wide, with a Calm list for the floor and ceiling.
- `test_shorter_lands_on_every_target`: every target from the sum of the floors up to one frame under the current length, for the tall and the wide example, lands exactly; no shot under its floor or longer than before; the named shots reach their floor first and in order; the other shots differ by at most one frame, extra frames from the later ones.
- The frame loop: every start from 0 to 1 second in thousandths, for lengths of 1, 44, 45, 46, 90, 91 and 150 frames, gives exactly that length and that end frame.
- `tests/test_revise.py`, `tests/test_cutlist_check.py`, `tests/test_match.py`, `tests/test_editor_handbook.py`, `tests/test_render_settings.py` together: 579 passed. The full suite was not run.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] set_frames could not write some shots exactly**
- **Found during:** Task 1, the frame loop
- **Issue:** a shot starting exactly half way into a frame (for example 0.05 seconds, which is 1.5 frames) could not be matched by writing `to` to 3 or 6 decimals. The intended end is also exactly half a frame, and a repeating decimal such as 0.083333 falls just short, so the frame rounded the wrong way. 30 of 7,007 starts failed.
- **Fix:** a third, last try writes the same end rounded up at the last decimal place (0.083334). A finer check (every half-thousandth from 0 to 3 seconds, eleven lengths) found no failure.
- **Files modified:** v2r/render/revise.py
- **Commit:** 111c08c

### Small differences from the plan's wording

- The refusal that names dropped shots lists them in the order Claude named them (`--from 7,6` gives "shots 7 and 6 dropped", as the plan's example reads), although the plan's text says "drop order". The separate "Shot N was dropped" lines are in drop order.
- A single named shot that cannot run longer gets "Shot N cannot run longer, being at its recipe's longest, ..." rather than "None of shots N ...", which would not read as English.
- The cover is removed as trimmed-away only when its shot actually got shorter in this run; a cover that was already past its shot's end is left for check to report.
- The tracer's check is fully automated and passed at its commit, so execution went on to longer without stopping for a person. Nothing about how a reel looks or sounds is rendered by this plan.

## Known edges

- A shot's `why` text (for example "A 01.0 to A 04.0: waves roll in") is left as Claude wrote it, so after a trim it can still name the old end time. Nothing reads it but people.
- `--to` of "1 seconds" reads slightly oddly in the "short of" sentence; the plan fixed that wording.
- A `--from` word starting with a minus and a comma is stopped by argparse before revise sees it (as in plan 03).

## Known Stubs

None.

## Threat Flags

None. The register's items are covered: `parse_target` accepts only plain digits within the settings' limits and a value up to three hours (T-7-09), longer's ceilings use the clip's whole frames and the next shot of the same clip and the closing check re-checks every shot (T-7-10), and `--from` goes through plan 03's capped `parse_shot_list` (T-7-04).

## What to check from a phone

Nothing in this plan renders, and the handbook does not use shorter or longer yet. When it does (a later plan), after "a bit shorter" the reel should open on the very same picture as before, with the same shots in the same order.

## Self-Check: PASSED

- `def shorter_frames(`, `"shorter": change_shorter`, `"longer": change_longer` in v2r/render/revise.py: found
- `def test_shorter_lands_on_every_target` in tests/test_revise.py: found once
- commits 06c29aa, 111c08c, cc78eee, 65993a6: found in git log
- the five new settings sit between `REVISE_NAME_TRIES` and `# render:`; EDITOR.md and docs/field-guide.html not touched

## Plain English for the user

"A bit shorter" is the follow-up the guide worries about most, and it is now safe. The chat's Claude decides which shots are weakest, because only it has seen the pictures, and names them in order. revise then does only arithmetic. Each named shot loses time from its end, down to the recipe's shortest (one and a half seconds for Lively); if that is not enough, the rest comes evenly off the other shots. In your 20-second example, asking for 15 with shots 6 and 2 named gives shots of 72, 45, 72, 72, 72, 45 and 72 frames, which is exactly 15 seconds, and every shot still starts on the same picture, the opener included. A whole shot is only dropped when even every shot at its shortest is too long, and only one Claude named, never the first. If it cannot get there, it says so in one sentence and saves nothing. "Longer" is the reverse: named shots run on past their old end, but never beyond the end of their clip, never into footage the next shot of the same clip shows, and never beyond the recipe's longest (a photo may run its whole clip). If it cannot reach the length asked, it saves what it reached and says how many seconds short it is. The few numbers it works by, such as how many digits a length may have, are in settings.py with the others. On the phone, after "a bit shorter", look at the first picture: it should be the same as before.
