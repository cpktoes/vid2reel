---
phase: 04-stage-16-cut-list-and-renderer
fixed_at: 2026-10-19T00:00:00Z
review_path: .planning/phases/04-stage-16-cut-list-and-renderer/04-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 4: Code Review Fix Report

**Fixed at:** 2026-10-19
**Source review:** .planning/phases/04-stage-16-cut-list-and-renderer/04-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 4 (WR-01, WR-02, WR-03, IN-03; the user chose these)
- Fixed: 4
- Skipped: 0
- Not touched on purpose: IN-01 (fixed by the orchestrator), IN-02, IN-04

**Where this ran:** all edits, commits and tests ran in the main checkout on branch `stage-16-render`, as the briefing asked, not in a separate worktree. Nothing was run against `work/` or `fixtures/`; every test uses a temporary folder. Only the targeted test files were run, not the full suite.

## What changed, in plain English

- **WR-01 (crashes on odd numbers).** If Claude wrote the canvas size as `1080.0` instead of `1080`, wrote the cover's segment as `1.0`, or wrote a time that is absurdly large (like `1e308` seconds), `check` and `render` used to die with a Python error message. Now `check` says one plain sentence about the exact field, and `render` builds nothing. A time may now be at most 3 hours (a new setting, `MAX_CUTLIST_SECONDS`). On top of that, if anything else unexpected ever goes wrong in any v2r command, it now prints one plain sentence (`v2r render: something unexpected went wrong (...)`) and stops, instead of showing a Python stack.
- **WR-02 (leftovers from a stopped render).** If a render was killed halfway, it left a hidden scratch folder (big, about 10 MB per second of reel) and half-written reel and cover files. Now, once a cut list has passed the check, `render` first removes exactly those leftovers and nothing else. The file docstring no longer says the scratch folder is "always" removed. A cut list that is refused still changes nothing at all.
- **WR-03 (old measurements on new clips).** `match` now also compares each clip's kind (video or photo) and length with what `look.json` recorded, and refuses with the sentence "look.json was made from other clips than the work folder holds now, so run look again before match" if they differ. And `normalize` now deletes `look.json` when a new job starts, so an old one can never be mistaken for the new job's.
- **IN-03 (numbers in the code).** Three numbers moved into `v2r/settings.py` with units: the thousandth-of-a-frame benefit for a clip's length (`CLIP_FRAME_BENEFIT`), the frame-rate tolerance (`FPS_TOLERANCE`), and the second of slack on the generated test tone (`TEST_TONE_SLACK_SECONDS`). The generated test tone is now never longer than `TEST_TONE_SECONDS`, so that setting and the real tone agree.

**What to look for on the phone:** nothing should look or sound different. All four fixes are about sentences, clean-up and where numbers are written. The values are unchanged (0.001, 0.001, 1 second), and the test tone is the same length as before for any reel the checker allows. If you want to be sure, make one reel with the test tone as music and check it sounds the same as before.

## Fixed Issues

### WR-01: Numbers the schema accepts but the code cannot handle crash `check` and `render`

**Files modified:** `v2r/render/check.py`, `v2r/render/plan.py`, `v2r/__main__.py`, `v2r/settings.py`, `tests/test_cutlist_check.py`, `tests/test_render_settings.py`
**Commit:** 7b78632
**Applied fix:**
- `check.canvas_problems` requires real whole numbers for width, height and fps. When the numbers are right but written with a decimal point, the sentence says exactly that.
- `plan.shape_of` now answers `None` for anything that is not a real whole number. This also stops `crop_notes` from crashing on a float canvas (the review found that crash in `check` itself).
- `check.cover_problems` refuses a cover segment that is not a whole number before using it as a list position.
- New rule `check.time_problems` (setting `MAX_CUTLIST_SECONDS`, 3 hours) covers every time in the list: clips' `seconds`, each segment's `from` and `to`, the cover's `at`, and the sound's `music_from`, `fade_in` and `fade_out`. It runs before every rule that turns seconds into frames and, when it finds anything, reports alone (with the "not compared with the work folder" note), because the later rules cannot be trusted with those numbers. This is wider than the review's examples (`from`, `to`, `at`); clips' `seconds` and the sound times had the same overflow.
- `v2r/__main__.py`: `main` now wraps the command run in a last-resort handler for every subcommand. It prints one line (text cleaned with `normalize.clean_text`, cut to `ERROR_DETAIL_CHARS`, so an error message cannot fake extra lines) and returns 1. The existing specific handlers still answer first. The command body moved into a new `run(args, parser)` function; its behaviour is unchanged.
- Tests (both shapes): nine new rows in the every-rule table (canvas with decimal points, fps with a decimal point, cover segment `1.0`, and `1e308` in a segment's to and from, a clip's seconds, the cover's at, music_from and a fade), `render` stops in a sentence for a float canvas and a huge time, the cap is inclusive, `plan.shape_of` is strict, and eight commands plus a line-faking message prove the last-resort handler. 32 of these failed before the fix.

### WR-02: Render never sweeps up what a killed run leaves behind

**Files modified:** `v2r/render/__init__.py`, `tests/test_render_tracer.py`
**Commit:** 35afee4
**Applied fix:** New `render.clear_leftovers(work_dir)`, called right after the list passes `check` and before anything is built. It removes only (a) real folders (never links) whose whole name is `.v2r-render-` plus letters, digits or underscores, and (b) regular files named `reel-tall|wide-YYYYMMDD-HHMMSS[-N].part.mp4` or `...-cover.part.jpg`. The module docstring now says the scratch folder is removed when the run ends and that a hard-stopped run's leftovers are swept at the start of the next, and that only one render may use a work folder at a time (a second render started while the first runs would sweep the first one's scratch folder).
Tests (both shapes): a render sweeps the planted leftovers and leaves lookalikes, finished reels and covers, look.json, `A.part.mp4`, proof sheets, a link named like a scratch folder and the folder it points to, the originals and the manifest untouched; a refused list leaves everything exactly as it was; a unit test of the exact names.

### WR-03: `match` can apply a previous job's measurements to a new job's clips

**Files modified:** `v2r/render/match.py`, `v2r/normalize.py`, `tests/test_match.py`, `tests/test_normalize.py`
**Commit:** 202e26e
**Applied fix:**
- `match.read_look` also requires each done entry's `kind` to equal the manifest's and its `seconds` to equal the manifest's length rounded to `LOOK_DECIMALS` places, which is exactly how look writes it (look rounds the same manifest number the same way, so a working copy of 12.004 seconds is 12.0 in look.json and still matches; comparing whole frames would have wrongly refused such clips). A missing `kind` or `seconds` also refuses, with the existing `OTHER_CLIPS` sentence.
- `normalize.clear_last_job` now also deletes `look.json` and `look.json.tmp` (by exact name, new tuple `LAST_JOB_RECORDS`), in the same style as `manifest.json`. It does not touch `sheets/`; look's own sweep owns those and only a new `look` run reads them.
- Tests: only the length changed (the review's case), only the kind changed, a missing length or kind, the rounding case passing, `clear_last_job` removing the look records and leaving lookalikes and sheets, and a real second normalize job removing `look.json`. The existing `clear_last_job` and second-run tests pass unchanged.

### IN-03: Behaviour-controlling numbers written in render code instead of settings.py

**Files modified:** `v2r/settings.py`, `v2r/render/plan.py`, `v2r/render/check.py`, `v2r/render/sound.py`, `tests/test_render_settings.py`, `tests/test_render_plan.py`, `tests/test_render_sound.py`, `tests/test_cutlist_check.py`
**Commit:** 83bc2fc
**Applied fix:** Three new names in the `# render:` block, each with a unit comment and added to the guard test (count now 34): `CLIP_FRAME_BENEFIT = 0.001` (frames), `FPS_TOLERANCE = 0.001` (frames per second), `TEST_TONE_SLACK_SECONDS = 1` (seconds). `plan.clip_frames` and `check.clips_problem` read the first two. The test tone's `duration` is now `min(TEST_TONE_SECONDS, music_from + reel seconds + TEST_TONE_SLACK_SECONDS)`. `check` already refuses any reel that needs more than `TEST_TONE_SECONDS` of music, so the tone is always long enough, and it can never be longer than the setting says. Tests change each setting and see the behaviour follow, in both shapes where the code is shape-aware.

## Tests run

Run in the main checkout: `tests/test_cutlist_check.py`, `tests/test_match.py`, `tests/test_normalize.py`, `tests/test_render_settings.py` together (532 passed, after WR-03), then `tests/test_render_plan.py`, `tests/test_render_sound.py`, `tests/test_render_settings.py`, `tests/test_render_tracer.py` (166 passed, after IN-03), and `tests/test_cutlist_check.py` again with the plan and sound files (all passed). Earlier, `tests/test_smoke.py`, `tests/test_doctor.py` and `tests/test_render_tracer.py` passed after WR-01. The full suite was not run (the orchestrator does that). WR-01's new tests were confirmed red against the old code before the fix. FFmpeg here is 8.0.1; nothing new needs a filter or option beyond what 6.1 has.

## For the user to paste into EDITOR.md

Not needed for these fixes to work, but one line may save Claude a round trip. A suggested sentence for the step where the cut list is written (EDITOR.md was not touched):

> Write the canvas width, height and frame rate, and the cover's segment number, as whole numbers (1080, not 1080.0), and keep every time in the list under three hours (10800 seconds).

## Notes for the user

- Behaviour you might notice: a list with a time over three hours, or a canvas written as `1080.0`, now gets a one-line "Problem:" from `check`, where before it crashed.
- IN-02 (unused `check.shape_of`, duplicate `match.clamp`, the shipped `sound.gain_at`) and IN-04 (rounding of shot boundaries) were left alone as asked. `check.shape_of` still exists and simply passes through to the now-stricter `plan.shape_of`.
- Nothing in the guide differs from what was built, so no `docs/decisions.md` line was added; if you want the three-hour cap or the leftover sweep recorded there, that is a one-line decision to write.

---

_Fixed: 2026-10-19_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
