---
phase: 03-stage-15-seeing-the-footage
plan: "05"
subsystem: look
tags: [contact-sheets, pillow, sheet-cap, graceful-fallback, look-json]
status: complete

requires:
  - phase: 03-stage-15-seeing-the-footage
    provides: "plan 01's look command, SheetBook, cell_size/fit_size and the sheet settings; plan 02's doctor filter list; plan 04's finished measure.py (not touched here)"
provides:
  - "pick.run_interval, pick.orientation, pick.still_plan and pick.sheets_needed: the run's base rhythm, decided from the manifest before anything is measured"
  - "SheetBook stops at MAX_SHEETS_PER_RUN (attribute full); stills past the cap are listed with sheet, cell and box null"
  - "sheets.pillow_modules, picture_problem, filter_problem, font_problem, label_font: one place Pillow is imported, and the plain sentences for what is missing"
  - "a sheet over SHEET_MAX_BYTES is saved again at lower quality and always kept"
  - "tests/test_look_sheets.py: 15 behaviours, each over tall and wide"
affects: [03-06, 03-07, 03-08, 03-03]

actuals:
  tokens: 5800
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "the sheet count is worked out up front from the manifest, counting every clip's full extras allowance, so later extra stills can never overrun the cap"
    - "Pillow is imported only inside pillow_modules(), the same lazy pattern normalize uses for photos"
    - "a missing piece (Pillow, select, scale, scalable font) costs only its own output and adds one sentence to look.json's missing list"

key-files:
  created:
    - tests/test_look_sheets.py
  modified:
    - v2r/look/pick.py
    - v2r/look/sheets.py
    - v2r/look/__init__.py

key-decisions:
  - "Once the cap is reached, no later still is placed on any sheet, even one that would fit the last sheet's free cells, so the stills on sheets are always an unbroken run from the start in letter order"
  - "When sheets cannot be made at all (no Pillow, no select or scale filter) the rhythm is not thinned: thinning exists only to save sheets"
  - "orientation_of moved from the look package into pick.orientation, so the up-front count and the sheets use one rule"

requirements-completed: [LOOK-01, LOOK-06]

duration: 25 min
completed: 2026-10-17
---

# Phase 3 Plan 05: Contact sheets across a whole run Summary

**Short clips share sheets in letter order, a sheet holds one orientation, a run is held to 20 sheets by thinning the stills' rhythm before measuring, and look still measures when sheets cannot be drawn.**

## What changed, in plain English

- **Short clips share sheets.** Ten short clips no longer cost ten sheets. Their stills run on from one clip to the next, and the labels (such as "A 04.0", then "B 00.0") keep them apart. To see it: run look on a few short clips and open `work/sheets/sheet-01.jpg`; the letter in the labels changes part-way across the grid.
- **A sideways clip gets its own sheet.** In a tall job, a landscape clip's stills go on a separate sheet of wide cells (3 across, 4 down), then the next upright clip starts a new tall sheet (4 across, 3 down). Nothing is squashed or cropped; a photo or square clip is shrunk to fit its cell and centred. A square clip uses the job's own shape.
- **At most 20 sheets, decided up front.** Before measuring, look works out from the clips' lengths how many sheets the whole run would need. If that is over 20 (roughly three minutes of footage in total), it takes a still every 1.5 seconds, or every 2 seconds, instead of every second, and says so in one sentence: "There are too many stills for 20 sheets, so a still is taken every 1.5 seconds instead of every second." look.json records `rhythm` and `rhythm_thinned`. If even every 2 seconds is too many, sheets stop at 20 and one sentence names the clip from which stills are only listed, not drawn. Nothing measured is ever dropped.
- **Sheets that are too big** (over about 1.5 MB) are saved again at slightly lower quality, never lost.
- **Without the tools, look still reports.** With no Pillow, or no `select` or `scale` filter in FFmpeg, look measures every clip, writes look.json with no sheets and says why in one sentence. With no scalable font the sheets are drawn with a small built-in font and one sentence says so. If the disk fills while a sheet is saved, look stops with one sentence and look.json's `stopped` is set.

Nothing in this plan changes how a finished reel looks or sounds; it only changes the sheets and look.json that the chat's Claude reads. There is no phone test needed for this plan on its own, but the sheets are worth a look once real clips go through (plan 03's phone run).

## Accomplishments

- Task 1: tests for continuous filling, orientation changes, exact fills, ordering, photo fit and square clips. Plan 01 had already built the SheetBook behaviour these describe, so the tests passed on first run (no red phase); they pin it down for both shapes.
- Task 2: `pick.run_interval` with the extras allowance counted, SheetBook cap, thinning and "not on a sheet" sentences, boundary tests at a cap of 1 (9 s keeps 1 s, 10 s thins to 1.5 s, 30 s needs the cap).
- Task 3: `pillow_modules` and the graceful fallbacks, the byte guard, the full-disk stop.

## Task Commits

1. Task 1: `72f0bff` test(03-05): sheets share cells in letter order, change at a new orientation and fit odd shapes
2. Task 2: `6865f2e` feat(03-05): hold the run to the sheet cap by thinning the rhythm before measuring
3. Task 3: `43b33b8` feat(03-05): sheets degrade gracefully without Pillow, the select filter or a scalable font

## Deviations from Plan

**1. [Rule 3 - Blocking] Task 1 needed no source change.** Plan 01's SheetBook already starts a new sheet on an orientation change, fills continuously and fits odd shapes, so Task 1 became tests only. No behaviour was missing.

**2. [Rule 2 - Missing critical] Once the cap is reached, later stills are not squeezed into free cells.** The plan said sheets stop at the cap; placing a later clip's stills into leftover cells of the last sheet would break the unbroken letter order the sheet and cell numbers promise, so from the first overflow nothing more is placed.

**3. Thinning is skipped when no sheets can be made.** Not in the plan; saying "too many stills for 20 sheets" when no sheet is made would be wrong.

**4. `picture_problem()` kept its no-argument shape and now means "no Pillow" only;** a separate `filter_problem(have)` covers `select` and `scale`, so plan 01's existing test that replaces `picture_problem` still works unchanged.

## Known Stubs

None.

## Threat Flags

None. Sheet names still come from a counter only and are written by temporary name then rename (T-3-02); the cap and the byte guard bound what look writes (T-3-08).

## Issues Encountered

None. The full suite (305 tests) passes in about 3 minutes.

## Self-Check: PASSED

- FOUND: tests/test_look_sheets.py, v2r/look/pick.py (`def run_interval(`, `def orientation(`), v2r/look/sheets.py (`def pillow_modules(`)
- FOUND commits: 72f0bff, 6865f2e, 43b33b8
- No top-level Pillow import in v2r/look/__init__.py (grep count 0)
