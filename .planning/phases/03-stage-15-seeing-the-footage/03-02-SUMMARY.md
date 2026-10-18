---
phase: 03-stage-15-seeing-the-footage
plan: "02"
subsystem: doctor
tags: [doctor, ffmpeg-filters, licences, decisions, docs]

requires:
  - phase: 02-stage-14-normalize
    provides: "doctor.FILTERS, ffmpeg_names() and the normalize.NEEDED_FILTERS list"
provides:
  - "doctor.FILTERS lists the eight FFmpeg filters look measures with (select, signalstats, blurdetect, scdet, deshake, ebur128, metadata, ametadata)"
  - "four Stage 15 lines in docs/decisions.md and the PySceneDetect checked-not-added note in docs/licenses.md"
  - "README Commands section, look in CLAUDE.md's Stack line, /look.log ignored by git"
affects: [03-03, 03-04, 03-05, 03-06, 03-07]

actuals:
  tokens: 2600
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "doctor prints one plain line per name in FILTERS; look reads the same list but never refuses a run for a missing measuring filter"

key-files:
  created: []
  modified:
    - v2r/doctor.py
    - tests/test_doctor.py
    - docs/decisions.md
    - docs/licenses.md
    - README.md
    - CLAUDE.md
    - .gitignore

key-decisions:
  - "normalize.NEEDED_FILTERS is untouched, so a computer missing a look filter can still normalize"
  - "No new library: shot changes come from FFmpeg's scdet; PySceneDetect is recorded as checked and not added"

requirements-completed: [LOOK-03, LOOK-05]

coverage:
  - id: D1
    description: "doctor lists every look filter, one plain line each, with no MISSING on this Mac, and normalize needs none of them"
    requirement: "LOOK-03"
    verification:
      - kind: unit
        ref: "tests/test_doctor.py::test_doctor_lists_every_look_filter, test_doctor_reports_look_filters, test_normalize_needs_no_look_filter"
        status: pass
    human_judgment: false
  - id: D2
    description: "PySceneDetect checked and not added, and the shot-change method recorded"
    requirement: "LOOK-05"
    verification:
      - kind: other
        ref: "grep PySceneDetect docs/licenses.md; grep -c '2026-10-17 · Stage 15 ·' docs/decisions.md prints 5"
        status: pass
    human_judgment: false
  - id: D3
    description: "all eight filters exist in the sandbox's FFmpeg 6.1 (this Mac has 8.0)"
    verification: []
    human_judgment: true
    rationale: "can only be seen by running doctor from the phone in plan 03"

duration: 6min
completed: 2026-10-18
status: complete
---

# Phase 3 Plan 02: Doctor lists look's filters, and the Stage 15 decisions are written down Summary

**`python -m v2r doctor` now has eight more lines, one per FFmpeg part look measures with (for example "The scdet filter is available."), and the four ways Stage 15 differs from your guide are written into docs/decisions.md.**

## What changed, in plain English

**The doctor report.** The report that `doctor` prints now checks eight more FFmpeg parts, one plain line each. On this Mac every one says "is available" and nothing says MISSING. What each part is for:

- **select**: picking which stills to take
- **signalstats**: how much moves, and the brightness and colour
- **blurdetect**: how sharp a picture is
- **scdet**: where the shot changes
- **deshake**: camera movement and shake
- **ebur128**: loudness of the sound
- **metadata** and **ametadata**: reading the numbers back out of FFmpeg

The point is that when you run doctor from your phone in plan 03, you can see whether the chat's FFmpeg (version 6.1, older than this Mac's 8.0) has all of them. The report only tells you; it never blocks anything. `normalize` still asks for exactly the parts it asked for before, so a computer missing one of the new parts can still normalize. If one is missing in the chat, look will leave that one measurement empty and carry on.

**Written decisions.** `docs/licenses.md` now has a "Checked and not added" table saying PySceneDetect (BSD-3-Clause) was looked at and left out: it needs OpenCV (about 80 MB) or PyAV (about 43 MB) downloaded in every chat, and FFmpeg's own `scdet` filter does the same job. `README.md` has a "Commands" table that names `look` and says it writes `work/sheets/` and `work/look.json`. `CLAUDE.md`'s Stack line now lists `look` (that is the only change in that file). `.gitignore` now ignores `look.log`, like `join.log` and `normalize.log`.

**Four differences from your guide** (each is a dated line in docs/decisions.md, so you can have the guide revised):

1. **Sound peaks as extra stills.** Besides movement peaks and scene changes, extra stills are taken at loud moments (a laugh, a splash). They share the cap of a third more than the one-a-second stills. The guide names only movement and scene changes.
2. **FFmpeg's scdet instead of a shot-change library.** The guide said to check for a library first; I did, and none is added.
3. **Camera versus subject.** look.json gives all movement, camera movement and camera shake as three separate figures, and only calls a half second "subject moving" where the camera is still, because on real footage the steadied picture hardly changes how much of the frame differs. The guide asks for shake kept apart from subject movement; this split is only trusted while the camera is still.
4. **Short clips share a contact sheet.** Stills fill sheets in clip-letter order, so one sheet can hold the end of one clip and the start of the next; a new sheet starts only when stills change between tall and wide. This comes from our discussion of 2026-10-17 and reads differently from the guide's "short clips on one sheet each".

**Phone test:** nothing about how a reel looks or sounds changed in this plan. Please run `doctor` on branch `stage-15-look` from your phone (plan 03) and check that all eight new lines say "is available". Any that says MISSING is the one look cannot measure there.

## Accomplishments

- RED then GREEN for the doctor list, with three new tests (`test_doctor_lists_every_look_filter`, `test_doctor_reports_look_filters`, `test_normalize_needs_no_look_filter`).
- The full suite passes (246 tests, about two minutes).
- Docs, README, CLAUDE.md Stack line and .gitignore updated; none of them names a person, an account or a file from fixtures/ or work/.

## Task Commits

1. **Task 1: doctor lists every look filter** - `018fd3f` (test, RED), `0cd73ac` (feat, GREEN)
2. **Task 2: decisions, licence note, README, CLAUDE.md, .gitignore** - `512b45c` (docs)

## Files Created/Modified

- `v2r/doctor.py` - `FILTERS` gains the eight look filters
- `tests/test_doctor.py` - `LOOK_FILTERS` and three tests
- `docs/decisions.md` - four `2026-10-17 · Stage 15 ·` lines
- `docs/licenses.md` - "Checked and not added" table with PySceneDetect, and the scdet note
- `README.md` - "Commands" table
- `CLAUDE.md` - `look` in the Stack line only
- `.gitignore` - `/look.log`

## Decisions Made

See `key-decisions` above. The four guide differences are recorded in docs/decisions.md; CLAUDE.md's "Settled so far" list is unchanged.

## Deviations from Plan

None - plan executed exactly as written. (The README's `join` and `build-skill` descriptions were worded to match the commands' own `--help` text.)

## Known Stubs

None in this plan's files. Plan 01's open stub entry (shot_changes and sound) in `.planning/WINDOWS.md` stays open for plan 03-04.

## Issues Encountered

None.

## Threat Flags

None. The added text describes decisions only (T-3-05); no person, account, fixture file or footage detail is in it.

## Next Phase Readiness

Plan 03 can push (with your permission) and run `doctor` from the phone to prove the eight filters exist in the sandbox's FFmpeg 6.1.

## Self-Check: PASSED

Commits 018fd3f, 0cd73ac and 512b45c exist; all seven files exist; full suite 246 passed.
