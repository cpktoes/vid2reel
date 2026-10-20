---
phase: 04-stage-16-cut-list-and-renderer
reviewed: 2026-10-19T00:00:00Z
depth: standard
files_reviewed: 31
files_reviewed_list:
  - .gitignore
  - CLAUDE.md
  - EDITOR.md
  - README.md
  - docs/decisions.md
  - docs/licenses.md
  - pyproject.toml
  - schema/cutlist.schema.json
  - tests/cutlists.py
  - tests/media.py
  - tests/test_cutlist_check.py
  - tests/test_doctor.py
  - tests/test_look_sheets.py
  - tests/test_match.py
  - tests/test_render_golden.py
  - tests/test_render_plan.py
  - tests/test_render_settings.py
  - tests/test_render_sound.py
  - tests/test_render_tracer.py
  - tests/test_render_video.py
  - v2r/__main__.py
  - v2r/doctor.py
  - v2r/look/sheets.py
  - v2r/render/__init__.py
  - v2r/render/check.py
  - v2r/render/match.py
  - v2r/render/plan.py
  - v2r/render/proof.py
  - v2r/render/sound.py
  - v2r/render/video.py
  - v2r/settings.py
findings:
  critical: 0
  warning: 3
  info: 4
  total: 7
status: issues_found
---

# Phase 4: Code Review Report

**Reviewed:** 2026-10-19
**Depth:** standard
**Files Reviewed:** 31
**Status:** issues_found

## Summary

I read the whole render package, the schema, the settings, the CLI wiring, the doctor and sheets changes, the docs, and skimmed the tests. I also ran small experiments against FFmpeg 8.0.1 on this Mac using scratch files outside the repo. None of them touched work/.

What holds up, checked by running it:
- A shot's first frame is the right source frame when the fast seek time is rounded to six decimals (tried start frames 60 to 150, including ones whose seek time rounds up). Photos come out at the right limited-range luma (black 16, white 234, mid grey 125). The music drop gives the same level on both channels and the mix is exactly the planned number of samples. `lavfi.r128.true_peak` exists, so the peak ceiling really is applied on this FFmpeg.
- Render does not choose anything the list leaves open beyond the settings.py defaults the decisions file records. It writes only the reel, its cover, `proof/` and its own scratch folder. It never writes to an original, a working copy or manifest.json.
- Every filter number is formatted in code. Every file name reaches FFmpeg as its own list item, and absolute paths are used for inputs. There is no shell=True. Music and photo paths are checked to be plain names directly inside their folder.
- I found no personal name, e-mail, account or absolute Mac path in the reviewed files. EDITOR.md's `check`, `match` and `render` commands match what `v2r/__main__.py` accepts.
- Tall and wide are handled symmetrically; nothing assumes tall.

No Critical findings. There are three Warnings and four Info items. I could not run FFmpeg 6.1 here. Everything stated about FFmpeg 6.1 is from the phase research notes, not from my own run.

## Warnings

### WR-01: Numbers the schema accepts but the code cannot handle crash `check` and `render` with a Python traceback instead of a sentence

**File:** `v2r/render/plan.py:20`, `v2r/render/plan.py:80-88`, `v2r/render/check.py:366-377`, `v2r/render/check.py:539`, `v2r/__main__.py:97-120`
**Issue:** The schema's `"type": "integer"` accepts a whole number written with a decimal point, because jsonschema's 2020-12 reader counts `1080.0` as an integer. The checker then treats the value as fine, and later code fails. I confirmed each of these with a scratch script:
- `canvas.width` or `canvas.height` written as `1080.0`. `canvas_problems` passes it, because `[1080.0, 1920.0] == [1080, 1920]`. `check` then says the list is fine, and `plan.fill_region` raises `TypeError: both arguments should be Rational instances` at `Fraction(canvas_w, source_w)`. So `check` and `render` disagree about a list, which the design says can never happen (plan.py's own docstring). `check` itself crashes the same way in `crop_notes` (`check.py:630`) for a sideways clip.
- `cover.segment` written as `1.0`. `cover_problems` indexes `data["segments"][number - 1]`, and `check` dies with `TypeError: list indices must be integers`.
- A `from`, `to` or `at` of about 1e308. `read_float` only refuses values that are infinite already, but `seconds * 30` overflows. `plan.frames` then raises `OverflowError`, and `segment_problems`, `segment_lengths` and `cover_problems` all call it. T-4-03 meant to turn every number the reader cannot use into one sentence, and this gap is outside what it covers.
- `__main__.py` catches only `RenderError`, `MatchError` and `LookError`. `check` (line 97) catches nothing, and `run_step` re-raises other `OSError`s (`render/__init__.py:82`). So any of the above reaches the user as a raw traceback. EDITOR.md tells Claude to show the user the exact error, so she would see a Python stack, not a plain sentence.

Claude may well write these by accident when it builds the list in Python (a width worked out with `/` is a float).
**Fix:** Refuse these in `check` with a sentence, and keep a last-resort net in the CLI.
```python
# check.py, canvas_problems: require real ints
if not (isinstance(width, int) and isinstance(height, int)) or shape is None or fps != settings.OUTPUT_FPS:
    ...

# check.py, cover_problems: before indexing
if not isinstance(number, int) or number > total: ...

# settings.py: MAX_CUTLIST_SECONDS = 3 * 60 * 60  # seconds: the largest time a cut list may hold
# check.py: one new rule that refuses from/to/at above it before plan.frames is called
```
In `__main__.py`, wrap the `check`, `render` and `match` branches so any other exception prints `v2r <command>: something unexpected went wrong: <short text>` and returns 1. Add tests with `1080.0`, `"segment": 1.0` and `"to": 1e308`.

### WR-02: Render never sweeps up what a killed run leaves behind, although its docstring says the scratch folder is "always removed"

**File:** `v2r/render/__init__.py:5`, `v2r/render/__init__.py:154`, `v2r/render/__init__.py:198-201`
**Issue:** The `finally` block only runs if the process gets to run it. If the sandbox, the phone app or a user stops the background render hard (SIGKILL, a restarted sandbox), the `.v2r-render-XXXX` folder stays. It holds near-lossless pieces (CRF 10), which the phase research measured at about 10 MB per second of reel (31 MB for 3 s of 1080x1920). A leftover `reel-*.part.mp4` and `reel-*-cover.part.jpg` stay too. Nothing ever removes them: look's `clear_last_look` sweeps `.v2r-look-*` leftovers (`look/__init__.py:87-104`) and normalize sweeps its own files, but render has no equivalent. The research file even recommends a `clear_last_render` for this (`04-RESEARCH.md`, Pattern 4). Over a few failed attempts in one chat the 32 GB sandbox disk fills, and the next run reports "work folder ran out of room".
**Fix:** After `check` passes and before `mkdtemp`, remove the leftovers, matching names tightly the way `look` does.
```python
LEFTOVER = re.compile(r"^\.v2r-render-[A-Za-z0-9_]+$")
def clear_leftovers(work_dir):
    for entry in Path(work_dir).iterdir():
        if LEFTOVER.match(entry.name) and entry.is_dir() and not entry.is_symlink():
            shutil.rmtree(entry, ignore_errors=True)
        elif re.fullmatch(r"reel-(tall|wide)-[\d-]+\.part\.mp4|reel-.*-cover\.part\.jpg", entry.name) and entry.is_file():
            entry.unlink()
```
Soften the docstring to "removed when the run ends, and any left by a stopped run are removed at the start of the next".

### WR-03: `match` can apply a previous job's measurements to a new job's clips

**File:** `v2r/render/match.py:55-89` (and `v2r/normalize.py:116-122`)
**Issue:** `read_look` decides that look.json belongs to the work folder by comparing only the shape, the clip letters and the working copy's file name (`A.mp4`). A new `normalize` job does not delete look.json: `clear_last_job` only removes the lettered files and the manifest. File names are the same in every job (A.mp4, B.mp4), so if Claude runs a second job in the same chat and skips or loses its `look` step, `match` silently writes the old clips' brightness and colour numbers into the new list as the touch-up. The result is a wrong colour correction on every clip, with no sentence about it. The look.json entries already carry `seconds` and `kind`, and match ignores them.
**Fix:** In `read_look`, for each `done` entry also require `entry.get("kind") == found["kind"]` and a matching length, for example `plan.clip_frames(entry["seconds"]) == plan.clip_frames(found["working"]["seconds"])`, else raise `MatchError(OTHER_CLIPS)`. Better still, have `normalize.clear_last_job` also delete `look.json` and `sheets/`, so a stale look can never survive a new normalize. Add a test that changes only a clip's length and expects `OTHER_CLIPS`.

## Info

### IN-01: EDITOR.md step 3 points at the wrong step

**File:** `EDITOR.md:3`
**Issue:** Step 3 ends "show the user what the log says, as step 7 says". When the render steps were inserted, the "if anything fails, show the user the exact error and stop" rule moved from step 7 to step 10. Step 7 is now the render. (I am not reviewing the handbook's prose, only this reference.)
**Fix:** Change "as step 7 says" to "as step 10 says" (or drop the cross-reference).

### IN-02: Code that nothing in the product calls, and a duplicate

**File:** `v2r/render/check.py:52-54`, `v2r/render/sound.py:69-80`, `v2r/render/match.py:92-93`
**Issue:**
- `check.shape_of` is a one-line wrapper that nothing calls (everything uses `plan.shape_of`).
- `sound.gain_at` is only used by tests, as the reference for `drop_expression`. That is acceptable as a test oracle, but it sits in the shipped module.
- `match.clamp` repeats `plan.clamp`.
- The FFmpeg piece lists in `render/__init__.py:27-35` (`RENDER_ENCODERS`, `RENDER_FILTERS` and so on) repeat names that `doctor.py` also lists, in two places that must be edited together.
**Fix:** Delete `check.shape_of`. Import `plan.clamp` in match. Consider moving `gain_at` into the test helpers. Optionally build `RENDER_FILTERS` from doctor's list.

### IN-03: Behaviour-controlling numbers written in render code instead of settings.py

**File:** `v2r/render/plan.py:30`, `v2r/render/check.py:437`, `v2r/render/sound.py:189`
**Issue:** The project rule is that every number that controls behaviour lives in `settings.py` with a unit comment.
- `plan.clip_frames` hard-codes `0.001` ("a thousandth of a frame").
- `check.clips_problem` hard-codes the `0.001` frames-a-second tolerance.
- `music_branch` hard-codes `+ 1` second of slack on the generated tone.

`TEST_TONE_SECONDS` is also only used as the stated length for checking; the tone that is actually made has a different length, so the setting and the behaviour can disagree.
**Fix:** Add `FRAME_COUNT_BENEFIT = 0.001  # share of a frame...`, `FPS_TOLERANCE = 0.001  # frames a second...` and `TEST_TONE_SLACK = 1  # seconds...` to settings.py, and make the tone's `duration` follow the setting rather than a literal.

### IN-04: Shot-boundary rounding is not stated in the check's notes

**File:** `v2r/render/plan.py:33-35`
**Issue:** `segment_frames` rounds a segment's start and its length separately (`frames(from)` and `frames(to - from)`), so the shot's last frame can differ from `frames(to)` by one. For back-to-back shots from one clip written with times that are not on frame boundaries, a source frame can be shown twice or skipped at the join. This is the rule the decisions file records ("start and length rounded by one rule"), and `check` guards the clip's end, so I do not count it as a bug. It is worth one line in EDITOR.md or the decisions file saying that adjacent shots should use times on frame boundaries, or a decision to round `to` instead of the length.
**Fix:** No code change needed unless the one-frame duplicate or skip is unwanted. In that case compute `count = frames(to) - frames(from)` and make `check` use the same expression.

---

_Reviewed: 2026-10-19_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
