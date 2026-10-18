---
phase: 03-stage-15-seeing-the-footage
plan: "01"
subsystem: look
tags: [ffmpeg, signalstats, pillow, contact-sheets, look-json]

requires:
  - phase: 02-stage-14-normalize
    provides: manifest.json with its frozen names and the constant 30 fps working copies
provides:
  - "`python -m v2r look [FOLDER]`: contact sheets (work/sheets/sheet-NN.jpg) and work/look.json"
  - "look.json layout, frozen in the v2r.look docstring for Stages 16 and 17"
  - "the whole `# look:` settings block (41 numbers, each with a unit) for plans 04 to 07"
  - "tests/media.py make_manifest helper"
affects: [03-02, 03-03, 03-04, 03-05, 03-06, 03-07, stage-16, stage-17]

actuals:
  tokens: 13300
  tasks: 3
  commits: 5

tech-stack:
  added: []
  patterns:
    - "look.json written whole or not at all (look.json.tmp then os.replace), rewritten after every clip"
    - "one measuring FFmpeg pass per clip in a temporary folder with a fixed plain file name, read back with parse_metadata"
    - "all of a clip's stills through one select filter and a raw pipe, then Pillow pastes them (Pillow imported lazily)"
    - "per-clip boundary: a bad clip becomes a skipped entry with one sentence, the run carries on"

key-files:
  created:
    - v2r/look/measure.py
    - v2r/look/pick.py
    - v2r/look/sheets.py
    - tests/test_look.py
  modified:
    - v2r/look/__init__.py
    - v2r/__main__.py
    - v2r/settings.py
    - tests/media.py

key-decisions:
  - "A still's orientation follows its working copy; a still of another orientation starts a new sheet (plan 05 adds the sharing rules)"
  - "A still's label time is the working copy's own frame time (frame number divided by fps), so the label never claims a moment the picture is not from"
  - "If Pillow or a scalable font is missing, look still measures: stills get null sheet, cell and box, and the sentence goes in look.json `missing`"
  - "A clip whose measuring pass and stills both fail is skipped; if only one fails the clip stays, with a fixed sentence in `notes`"
  - "A manifest with an unusable letter or number (not like A, B, AA) stops the run with one sentence rather than being guessed at"

requirements-completed: [LOOK-01, LOOK-02, LOOK-03, LOOK-06]

coverage:
  - id: D1
    description: "look command makes a labelled contact sheet and a look.json with half-second movement and brightness, in tall and wide"
    requirement: "LOOK-01"
    verification:
      - kind: unit
        ref: "tests/test_look.py::test_tracer_cli_one_clip_to_sheet_and_look_json"
        status: pass
    human_judgment: false
  - id: D2
    description: "several clips in letter order, skipped entries keep their letter, photos get one still, a bad clip does not stop the run"
    requirement: "LOOK-02"
    verification:
      - kind: unit
        ref: "tests/test_look.py -k run_"
        status: pass
    human_judgment: false
  - id: D3
    description: "a new run replaces only the last run's look.json and sheets"
    requirement: "LOOK-06"
    verification:
      - kind: unit
        ref: "tests/test_look.py::test_run_second_run_replaces_last_look"
        status: pass
    human_judgment: false
  - id: D4
    description: "every look number is in settings.py with a unit and look.json's names are documented"
    requirement: "LOOK-03"
    verification:
      - kind: unit
        ref: "tests/test_look.py::test_look_settings_have_unit_comments, test_look_json_names_documented"
        status: pass
    human_judgment: false
  - id: D5
    description: "the contact sheet is readable on a phone: label large enough, stills not cropped, grid right"
    verification: []
    human_judgment: true
    rationale: "legibility of a label and a still on a phone screen is a judgment no test can make"

duration: 7min
completed: 2026-10-18
status: complete
---

# Phase 3 Plan 01: Look, one clip to a sheet and a measurements file Summary

**`python -m v2r look` takes a still every second of each clip, prints them in a grid on a labelled contact sheet ("A 03.0" in each corner), and writes look.json with how much moves and how bright each half second is, in tall and wide.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-10-18T05:31:58Z
- **Completed:** 2026-10-18T05:38:31Z
- **Tasks:** 3 (one tracer, two TDD)
- **Files modified:** 8 (4 created)

## What changed, in plain English

There is a new command, `look`. After `normalize` has made the working copies, `look` goes through them in letter order. For each clip it does two things.

1. **It makes pictures.** It takes one still every second and arranges them in a grid on a "contact sheet", a single JPEG. A tall job gives 12 stills per sheet (4 across, 3 down); a wide job gives 12 stills per sheet (3 across, 4 down). Short clips share a sheet, so ten 5-second clips do not cost ten sheets. Every still has a small label in its top-left corner, white text on a black box: the clip's letter and the time in seconds, such as `A 03.0` or `B 07.5`. That label is how the chat's Claude and you can say "the moment at B 07.5".
2. **It writes a measurements file**, `look.json`. For every half second of every clip it says how much is moving and how bright the picture is. (Camera shake, sharpness, sound, shot changes and colour come in plans 04 to 07, and slot into the same file.)

Things it handles safely:

- A clip that `normalize` skipped keeps its letter and gets a one-sentence "skipped" entry, so B is still B.
- A photo gets exactly one still, labelled `A 00.0`.
- If one clip cannot be looked at (missing file, damaged file), it gets one plain sentence and the clips after it are still looked at.
- Running `look` again replaces only the last run's `look.json` and sheets. Your working copies, `manifest.json` and any other file in the folder are not touched.
- It prints one line per finished clip, such as `A looked at in 2 s, 1 sheet so far`, so a run in the background can be followed.
- It never decides what goes in a reel. It only measures and shows.

**Where to see it working:** after a normalize, run `python3 -m v2r look` (the handbook step that runs it in the chat's sandbox comes in a later plan of this stage). Then open `work/sheets/sheet-01.jpg`. What to look for: a grid of stills, each with a label like `A 03.0` in its top-left corner, white on black, big enough to read when the sheet is shrunk to phone size, and the stills uncropped (tall stills in a tall job, wide stills in a wide job). `work/look.json` holds the measurements.

**Phone test (needed before anything merges to main):** nothing about how a reel looks or sounds changed, because `look` only reads the working copies and writes sheets and a text file. But this is the first stage that uses FFmpeg's `signalstats`, `metadata`, `select`, `fps` and `scale` filters in the sandbox's FFmpeg 6.1, which this Mac (FFmpeg 8.0) could not run. Please run `look` on branch `stage-15-look` from your phone after normalize and check that it finishes and that `sheet-01.jpg` opens with readable labels. This plan only uses old, long-standing filters, so no surprise is expected.

## Accomplishments

- Tracer: one clip end to end, command line to measuring pass to sheet and look.json, in both shapes, and I opened a generated sheet to check the layout and labels by eye.
- The whole run made safe and whole (letters kept, photos, bad clips, clearing the last run, one sentence per problem, exit codes).
- All 41 look numbers are in `v2r/settings.py` with units (16 used now, 25 reserved for plans 04 to 07 so those plans never need to edit settings.py), and the full look.json layout is written in the `v2r.look` docstring.

## Task Commits

1. **Task 1 (tracer): one clip end to end** - `44faa91` (feat)
2. **Task 2: whole and safe run** - `5b719e3` (test, RED), `31340a7` (feat, GREEN)
3. **Task 3: rest of the settings and the frozen layout** - `433c48f` (test, RED), `fba96cd` (feat, GREEN)

Tracer gate: auto mode was off, but `workflow.human_verify_mode` is `end-of-phase`, so the tracer's human check is carried to the end-of-phase review instead of halting. The tracer's automated check (both shapes) was re-run with the rest of the suite and passed: "Tracer verified end-to-end, expanding". The human-check item is D5 above (sheet legibility on a phone).

## Files Created/Modified

- `v2r/look/__init__.py` - the look job, manifest in, per-clip loop, look.json, clearing the last run, frozen layout in the docstring
- `v2r/look/measure.py` - the FFmpeg measuring pass, the metadata parser, the half-second summary
- `v2r/look/pick.py` - base rhythm and frame numbers
- `v2r/look/sheets.py` - stills through one select pipe, labels, contact sheets (Pillow)
- `v2r/__main__.py` - the `look` sub-command (optional folder argument, no `--shape`)
- `v2r/settings.py` - the `# look:` block, 41 numbers
- `tests/media.py` - `make_manifest`
- `tests/test_look.py` - 34 tests over both shapes

## Decisions Made

See `key-decisions` above. None changes a rule in CLAUDE.md or differs from the guide.

## Deviations from Plan

### Auto-fixed Issues

None needed fixing during the build; the first run of every task's tests passed after implementation.

### Additions beyond the plan's test list (Rule 2, correctness of the whole-run behaviour)

- Added tests for an unreadable manifest, no FFmpeg, running out of room, stills failing (measurements kept) and no picture library. The plan's spec describes these behaviours; the extra tests make them proven rather than assumed.
- `read_manifest` also checks that every manifest entry's letter looks like A, B, AA and that its number is an integer. Reason: sentences name clips by letter only (T-3-07), so a hand-edited letter holding odd text must not reach a sentence or look.json.
- `working_facts` also refuses a working copy whose resolved path is outside the work folder (a symlink), on top of the plain-file-name check (T-3-01).
- `sheets.picture_problem()` (not in the plan's interface list) names a missing picture library or scalable font, so `missing` in look.json carries the sentence and measuring still works.

## Known Stubs

- `v2r/look/measure.py`, `measure_clip`: `shot_changes` is `None` and `sound` is `[]` for now. Intentional: the frozen look.json names exist and null means "not measured"; plan 03-04 measures them. Recorded in `.planning/WINDOWS.md` as an open entry so the ship gate sees it; plan 03-04 should mark it resolved.
- look.json's `candidates`, `camera`, `shake`, `blur` and the colour fields of `overall` are not written yet (plans 04 to 07). They are documented in the docstring, and no reader exists yet.

## Issues Encountered

None. Two things to know: the full test suite now takes about two minutes on this Mac (243 tests), and I could not test on FFmpeg 6.1 (the sandbox's version), only on this Mac's 8.0.1.

## Threat Flags

None. The surface (reads working copies, writes look.json and sheets/ in the work folder it was given) matches the plan's threat model; mitigations T-3-01, 02, 03, 04, 06, 07 and 13 are in the code and tested as the plan lists.

## Next Phase Readiness

Plans 04 to 07 add measurements and stills to `measure.MEASURES`, `look_at_clip` and `SheetBook`. Plans 04 and 05 can run side by side because no settings.py edit is left for them. Plans 03 and 09 push to the remote only with your permission.

## Self-Check: PASSED

All five commits exist (44faa91, 5b719e3, 31340a7, 433c48f, fba96cd); `v2r/look/measure.py`, `pick.py`, `sheets.py` and `tests/test_look.py` exist; full suite 243 passed.
