---
phase: 03-stage-15-seeing-the-footage
fixed_at: 2026-10-18T22:30:00Z
review_path: .planning/phases/03-stage-15-seeing-the-footage/03-REVIEW.md
iteration: 1
findings_in_scope: 8
fixed: 8
skipped: 0
status: all_fixed
---

# Phase 3: Code Review Fix Report

**Fixed at:** 2026-10-18
**Source review:** .planning/phases/03-stage-15-seeing-the-footage/03-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 8 (CR-01, CR-02, CR-03, WR-03, WR-05, WR-06, WR-07, WR-08, as narrowed by the orchestrator)
- Fixed: 8
- Skipped: 0
- Left alone on purpose (out of scope): WR-01, WR-02, WR-04, IN-01 to IN-07 (see "Decisions for the user")

Where the checks ran: in an isolated git worktree of the repo (not the main checkout), on this Mac with FFmpeg 8.0.1,
using the main checkout's Python environment. The sandbox's FFmpeg 6.1 was not available, so nothing here proves
the 6.1 behaviour; the fixes do not depend on anything that differs between 6.1 and 8.0. The full test suite was not
run (the orchestrator does that). The look and doctor tests (`tests/test_look*.py`, `tests/test_doctor.py`) were run
on the finished branch; the result is in "Final check" below.

## What changed (in plain English)

look is the step that measures the clips and makes the contact sheets. It still only reports; none of these changes
makes it choose anything.

- **CR-01 (a candidate stretch could run across a shot change).** When the footage cuts to a new shot exactly on a
  half second (about one cut in five), two neighbouring stretches were glued together with the cut in the middle, and
  the written reason ("steady camera, sharp...") described two different shots as one. Two stretches that meet at a
  cut are now kept apart: one ends at the cut and the next starts at it.
  *What to check on the phone:* open `work/look.json`, find a clip whose `shot_changes` lists a time such as 2.0,
  and look at its `candidates`. No candidate may have a `start` smaller than that time and an `end` larger than it.
  A candidate ending exactly at the cut, or starting exactly at it, is correct.
- **CR-02 (one odd number from the camera-movement file stopped the whole run).** If the camera-movement
  measurement ever produced "not a number", look crashed and left `look.json` unfinished with only the earlier clips.
  Now that clip simply gets the usual note "The camera movement of clip X could not be read." and the camera fields
  stay empty (null); the run carries on. As a second safety net, if any clip's entry still held an unwritable number,
  that one clip is reported as "could not be looked at" and the other clips are unaffected.
- **CR-03 (a clip with failed stills was thrown away together with measurements that worked).** A clip is now left
  out only when its picture measuring itself failed and its stills failed too. A smaller problem (for example, the
  loudness reading failed) no longer costs the clip its other numbers.
  *What to check on the phone:* if the log says "The loudness of clip X could not be measured." or "The stills of clip
  X could not be taken...", that clip must still be in `look.json` with `"status": "done"` and its `halves` entries
  (the half-second numbers such as `movement`, `brightness`) filled in.
- **WR-03 (the log did not repeat the clip notes).** After each clip's "looked at in N s" line, look now prints each
  of that clip's notes, as EDITOR.md says it does. The last line says "the sheets are in ..." only when there are
  sheets; otherwise it only says where the measurements are.
- **WR-05 (a long clip could use up the memory).** look now reads a clip's stills one at a time from FFmpeg and
  asks for only as many as still fit within the 20-sheet cap. The rest are listed in `look.json` with no sheet, as
  before. A stuck FFmpeg is still stopped after the same time limit.
- **WR-06 (a failed save left the sheets and look.json disagreeing).** If saving a sheet fails part-way, the sheets are
  put back exactly as they were before that clip, any half-written sheet file is removed, and the clip is kept with the
  note that its stills could not be taken. The next clip then starts in the right cell, with no blank cells.
- **WR-07 (bad manifest values got through).** A `shape` that is a list or a number, or a letter with a hidden line
  break after it, now gives the usual one-sentence "manifest.json could not be read" instead of a crash or a stray
  character. A clip length written as text ("3.0") is turned into a number before it is used. A length of more than 3
  hours is not believed and that clip is skipped, instead of the run planning stills for ever.
- **WR-08 (missing tests).** Added tests, on small clips made on the spot in both tall and wide, for: how many
  sheets a run needs (including tall and wide alternating and a photo between two videos), thinning the rhythm to 1.5
  and to 2 seconds, a run that does not need thinning, a run where nothing fits (the sheet cap is reached and the rest
  are listed but not drawn), the count made up front agreeing with the sheets actually made, an FFmpeg command that runs
  too long (both the measuring and the stills command), and all of CR-01, CR-02 and CR-03.

## Fixed Issues

### CR-01: A merged candidate stretch can contain a shot change strictly inside it

**Files modified:** `v2r/look/pick.py`, `tests/test_look_candidates.py`
**Commit:** 7e0a51a
**Status:** fixed: requires human verification (it is a logic change; see the phone check above)
**Applied fix:** The merge step now refuses to join two windows when the joined stretch would have a shot change
strictly inside it (compared in whole frames, like the window check). Tests: a pure test with cuts at 2.0 (4 s clip),
4.0 (8 s clip) and 2.5, which fails on the old code, and a test on generated clips with a real cut at 2.0 s and 4.0 s,
tall and wide.

### CR-02: A non-finite number from deshake's motion file stops the whole run

**Files modified:** `v2r/look/measure.py`, `v2r/look/__init__.py`, `tests/test_look_measure.py`, `tests/test_look.py`
**Commit:** 2c303be
**Applied fix:** `parse_motion` reads every number through `finite()` and raises `ValueError` for NaN or infinity,
which the existing code already turns into "camera movement could not be read". A new `writable()` check at the
per-clip boundary replaces a clip whose entry cannot be written as JSON by a skipped entry, so no later write can fail
on it. Tests: the parser on nan, inf and -inf; a real clip whose motion file is poisoned with a NaN; and a run where
one clip's numbers contain NaN and the next clip is still looked at.

### CR-03: A clip whose stills failed is thrown away with measurements that worked

**Files modified:** `v2r/look/measure.py`, `v2r/look/__init__.py`, `tests/test_look.py`
**Commit:** 67394d8
**Status:** fixed: requires human verification (it is a logic change; see the phone check above)
**Applied fix:** `measure_clip` now returns `measured` (true when the picture measuring pass ran and finished). The
clip is skipped only when `measured` is false and the stills failed. Tests: a failed loudness pass plus failed stills
keeps the clip with its half-second numbers and both notes; a failed measuring pass plus failed stills still skips it
(and the next clip is unaffected).

### WR-03: The log never prints per-clip notes, contrary to EDITOR.md

**Files modified:** `v2r/look/__init__.py`, `tests/test_look.py`
**Commit:** c1a6108
**Applied fix:** Each note of a done clip is printed after its status line. The final line mentions the sheets folder
only when `look.json` lists at least one sheet. EDITOR.md was not touched; the proposed wording is below.

### WR-05: All of a clip's stills are read and held in memory, including ones that cannot be placed

**Files modified:** `v2r/look/sheets.py`, `v2r/look/__init__.py`, `tests/test_look_sheets.py`, `tests/test_look.py`
**Commit:** f4b6037
**Applied fix:** `grab_stills` is now a generator that reads FFmpeg's output one picture at a time (FFmpeg's error text
goes to a temporary file, a timer stops FFmpeg at the same time limit as before, and FFmpeg is stopped if the caller
stops asking). `SheetBook.room()` says how many more stills fit before the cap; `look_at_clip` asks for only that many
and marks the book full when some are left over. `SheetBook.add` accepts any iterable of (picture, label) pairs, so
at most one picture plus the sheet being filled is in memory. No new setting. Tests: the generator yields in order,
repeats a duplicated frame, and raises for out-of-order or missing frames; with a cap of 1 sheet, the stills asked for
are exactly the cells that fit.

### WR-06: A failure part-way through `SheetBook.add` leaves the book out of step with look.json

**Files modified:** `v2r/look/sheets.py`, `v2r/look/__init__.py`, `tests/test_look_sheets.py`
**Commit:** a726d53
**Applied fix:** `add` takes a snapshot (count, `full`, the sheet being filled and a copy of its picture) and on any
exception restores it, deletes `.part.jpg` files and sheet files that this call began, and rewrites a sheet that this
call had already re-saved. `look_at_clip` now also treats a save failure other than "out of room" as "stills could not
be taken" (the clip and its measurements are kept), so the failed clip no longer becomes a skipped entry. Tests: a
save that fails after clip B (clip C starts at cell 4, no stray files) and a save that fails after a sheet was already
filled (no sheet files left behind, `sheets` is empty).

### WR-07: Manifest checks let bad values through

**Files modified:** `v2r/look/__init__.py`, `v2r/look/measure.py`, `v2r/look/pick.py`, `v2r/settings.py`, `tests/test_look.py`
**Commit:** 5b4444b
**Applied fix:** (a) the shape must be text before it is looked up; (b) the letter is matched with `fullmatch`; (c) the
cleaned `seconds` is passed to `measure_clip`; (d) a new setting `MAX_CLIP_SECONDS` (3 hours, with a unit comment)
is used by `working_facts` and `still_plan` so an absurd length is skipped instead of looped over. The frozen list in
`test_look_settings_have_unit_comments` now has 43 names. Tests for list/dict/number/None/unknown shapes, a letter
with a line break, text seconds, and a length of 1e12.

### WR-08: No tests for the sheet cap, the thinning arithmetic, or the failure paths above

**Files modified:** `tests/test_look_sheets.py` (and the tests that came with the fixes above)
**Commit:** 86250fd
**Applied fix:** Added the tests listed in "What changed". The FFmpeg-timeout tests make the time limit tiny so the
real command is stopped (one for the measuring command in `tests/test_look.py`, one for the stills command in
`tests/test_look_sheets.py`); both check that the other half of the work survives.

## Skipped Issues

None. (WR-05 and WR-06 touch the same lines of `sheets.py`; they were committed separately.)

## For the user to paste into EDITOR.md

EDITOR.md was not changed. Step 4 currently says look "prints a line as each clip is looked at and one plain sentence
for anything it could not measure". The code now really does that. One new case is worth a sentence, so Claude does not
describe sheets that do not exist. Suggested wording to add after "tell the user those sentences in plain words":

> If look.json lists no sheets (the log will not point to a sheets folder), no pictures were made: say so, and
> describe the clips only from the numbers in look.json, never from stills you have not seen.

## Decisions for the user

Left exactly as they are; one plain line each on what I would do.

- **WR-01 (candidates listed for a clip where nothing was measured):** I would list no candidate stretches for a
  clip whose picture measuring failed, because a ranked list built from no facts reads like a recommendation. This
  needs the existing test that says "nothing measured is not excluded" to change, so it is your call.
- **WR-02 (the word "sharp" claims more than look knows):** I would reword it to "no blurrier than the rest of the
  clip", because a clip that is out of focus all the way through is currently called "sharp". It changes the wording
  Claude reads, so you may want to see it first.
- **WR-04 (the temporary folder is outside the work folder):** I would keep look's temporary files inside the work
  folder (hidden name) and have the next run clear leftovers, so a run stopped by the sandbox leaves nothing in the
  system temp area.
- **IN-01 (decisions not all written down):** I would add the sound-peak extras, the sheet-cap thinning to 1.5 or 2
  seconds, and the candidates (their exclusions and order) to CLAUDE.md's settled list and to docs/decisions.md.
  That is your document and it is a process rule, so I did not touch it.
- **IN-02 (candidates drop stretches silently, order partly an editorial preference):** I would correct the docstring
  (sharpness is a filter, not a sort key) and consider listing excluded stretches as facts with a reason, so Claude can
  tell a dull stretch from an excluded one.
- **IN-03 (shake averaged across shot changes):** I would stop the one-second shake average at a cut, so a pan before
  a cut does not make a steady shot after it look shaky and remove stretches wrongly.
- **IN-04 (numbers and names outside settings.py, a wrong range comment):** I would use the existing `MOTION_FILE`
  name in the deshake piece, add a setting for the label's decimals, and fix the "0-255" comment on
  `DESHAKE_CONTRAST` (deshake takes 1 to 255).
- **IN-05 (sheet sizes versus their stated reason and the result limit):** I would size tall sheets so their long edge is
  about 1568 pixels, and tell EDITOR.md to send a few sheets at a time, since 20 sheets can pass the 24 MiB result limit.
- **IN-06 (hang budget and unused parameters):** I would add an overall time limit for a look run in settings, remove
  the unused `start` and `end` parameters of `candidate_reason`, and rename `TALL_SIZE` in the tests.
- **IN-07 (docstring describes the brightness values wrongly):** I would reword it to "the brightness below which a
  tenth of the picture falls, and above which a tenth falls", since Stage 16 reads these.

## Final check

`tests/test_look*.py` and `tests/test_doctor.py` on the finished branch (run in the isolated worktree, FFmpeg 8.0.1):
208 passed in 191 s. The rest of the suite was not run.

After you pull this branch, please run `v2r look` once from a phone on a set of clips that includes a cut and check the
two things under CR-01 and CR-03 above, since the 6.1 FFmpeg in the sandbox has not run these changes.

---

_Fixed: 2026-10-18_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
