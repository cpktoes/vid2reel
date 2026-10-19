---
phase: 03-stage-15-seeing-the-footage
reviewed: 2026-10-18T00:00:00Z
depth: standard
files_reviewed: 20
files_reviewed_list:
  - .gitignore
  - CLAUDE.md
  - EDITOR.md
  - README.md
  - docs/decisions.md
  - docs/licenses.md
  - tests/media.py
  - tests/test_doctor.py
  - tests/test_look.py
  - tests/test_look_candidates.py
  - tests/test_look_extras.py
  - tests/test_look_measure.py
  - tests/test_look_sheets.py
  - v2r/__main__.py
  - v2r/doctor.py
  - v2r/look/__init__.py
  - v2r/look/measure.py
  - v2r/look/pick.py
  - v2r/look/sheets.py
  - v2r/settings.py
findings:
  critical: 3
  warning: 8
  info: 7
  total: 18
status: issues_found
---

# Phase 3: Code Review Report

**Reviewed:** 2026-10-18
**Depth:** standard
**Files Reviewed:** 20
**Status:** issues_found

## Summary

The look package is carefully built: no file name ever reaches a filter string (the manifest's `working.file` is checked to be a plain name directly inside the work folder, FFmpeg is given an absolute path, and the text files use fixed names inside a temporary folder). Nothing is passed to a shell. The 143 look and doctor tests pass on the Mac (FFmpeg 8.0.1). No name, account, e-mail or private path was found in any reviewed file.

Three defects are real and were reproduced by running the code:

1. A candidate stretch can run across a shot change, which look.json's own documentation says never happens.
2. One non-finite number in deshake's motion file stops the whole run and leaves look.json unfinished.
3. A clip whose stills fail is discarded together with measurements that worked.

There are also gaps between what EDITOR.md promises and what the log prints, candidates that are listed for a clip where nothing was measured, a reason word ("sharp") that claims more than is known, a temporary folder outside the work folder, and no tests at all for the sheet cap or the thinning arithmetic.

I could not run FFmpeg 6.1 here. The earlier phone doctor report (03-03 summary) confirms all eight filters exist there. I found nothing in the reviewed code that depends on a behaviour known to differ between 6.1 and 8.0, but the metadata, deshake and scdet paths have only been proven on 8.0.

## Critical Issues

### CR-01: A merged candidate stretch can contain a shot change strictly inside it

**File:** `v2r/look/pick.py:337-354` (merge condition at 344-349)
**Issue:** `candidates()` leaves out any window with a cut strictly inside it, but a cut exactly on a window edge is allowed. The merge step then joins two windows that touch at that edge and never re-checks the cut. Reproduced with all halves still, sharp and moving, a cut at 2.0 s and a 4 s clip: the result is one stretch `start 0.0, end 4.0` with the cut at 2.0 inside it. The same happens at any cut that lands on a half second (about one cut in five, because shot changes are rounded to 0.1 s). This breaks the stated rule in `v2r/look/__init__.py:32` ("A stretch with a shaky camera, a blurred picture or a cut is never listed") and the docstring of `candidates()`. It also makes the reason text ("steady camera, sharp...") describe two different shots as one.
**Fix:** Refuse a merge whose union has a cut strictly inside it.
```python
union_start, union_end = min(start, other_start), max(end, other_end)
cut_inside = any(round(union_start * fps) < cut < round(union_end * fps) for cut in cuts)
if other_tier == tier and alike and touching and within and not cut_inside:
```
Add a test with a cut at exactly 2.0 s on a 4 s clip (and one at 4.0 s on an 8 s clip) asserting no stretch has `start < cut < end`.

### CR-02: A non-finite number from deshake's motion file stops the whole run

**File:** `v2r/look/measure.py:106-115` (and 191-195); `v2r/look/__init__.py:63-68, 287-296`
**Issue:** `parse_motion` uses plain `float()`, which accepts `nan`, `inf` and `-inf`; every other FFmpeg number goes through `finite()`. A non-finite value flows into `camera_and_shake`, then `rounded()`, then the half-second entries. `write_look` refuses it with `allow_nan=False` and raises `ValueError`. That write is outside the per-clip `try`, so it is not caught: the clip has already been appended to `result["clips"]`, the run dies with a traceback, and look.json stays at `finished: false` with the earlier clips only. Reproduced by making `parse_motion` return one NaN: `ValueError: Out of range float values are not JSON compliant: nan`, `finished = False`, `clips = 0`. This breaks "the run must survive one bad clip". I could not make deshake print a NaN on black, white, noise or test-pattern sources, so the trigger is unproven, but the guard turns any such value into a total failure.
**Fix:** Treat a non-finite motion value as unreadable, which the code already handles with the "camera movement could not be read" note.
```python
def parse_motion(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        next(handle, None)
        rows = []
        for line in handle:
            if not line.strip():
                continue
            values = [finite(part) for part in line.split(",")]
            if None in values:
                raise ValueError("non-finite motion value")
            rows.append(values)
        return rows
```
Also move the post-clip `write_look` into the per-clip boundary (or catch `ValueError` there and replace the clip with `skipped_entry`) so no single clip can poison every later write.

### CR-03: A clip whose stills failed is thrown away with measurements that worked

**File:** `v2r/look/__init__.py:195-197`
**Issue:** The comment says "neither the measurements nor the stills could be made", but the test is `if measured["notes"]:`. Notes also record partial trouble ("camera movement could not be read", "loudness could not be measured"). So a clip with good half-second measurements, one failed loudness reading and any stills problem (no Pillow, a missing `select` filter, `ValueError: wrong number of stills`) becomes `skipped` with "Clip A could not be looked at." and all of its measurements are lost. Reproduced: Pillow reported missing plus a failed loudness pass gives `status: skipped`, whereas Pillow missing alone (the case the tests cover) keeps the clip. The no-Pillow and no-`select` cases are run-wide, so every clip with any note is lost.
**Fix:** Skip only when the video measurement itself failed. Return that fact from `measure_clip` instead of inferring it from notes.
```python
# measure_clip returns "measured": not failed and pass_possible
if not taken and not measured["measured"]:
    return skipped_entry(entry, f"Clip {letter} could not be looked at.")
if not taken:
    notes.append(...)
```

## Warnings

### WR-01: Candidates are listed for a clip where nothing was measured

**File:** `v2r/look/__init__.py:204-206`; `v2r/look/pick.py:313-373`
**Issue:** If the measuring pass fails (FFmpeg error, timeout) the clip is still "done" when its stills worked, and `candidates()` runs on halves that are all `None`. Nothing is excluded, every window is tier 3 with equal movement, so up to five windows merge into arbitrary stretches (0-4 s, 4-8 s, ...), with rank 1 being the first four seconds. `tests/test_look_candidates.py:127` asserts this on purpose ("nothing measured is not excluded"). A ranked list built from no facts reads as a recommendation, which is the opposite of "look decides nothing" and of the claim in EDITOR.md that candidates are "facts in an order".
**Fix:** In `look_at_clip`, give `found = []` when every half has `camera_state is None and movement is None and sharp is None`, and keep the "could not be measured" note as the explanation.

### WR-02: "sharp" in a candidate reason claims more than look knows

**File:** `v2r/look/pick.py:281-287`; `v2r/look/measure.py:323-331`
**Issue:** `sharp` is judged only against the clip's own median half second ("never judged against a fixed number"). A clip that is out of focus throughout has every half `sharp: true`, so every candidate reads "steady camera, sharp, ...". That is a verdict that is false in the one case it matters, and the handbook tells Claude to treat these as facts.
**Fix:** Word it as what is known: "no blurrier than the rest of the clip" (and "blurrier than the rest of the clip" for the excluded case), and say so in the `v2r/look/__init__.py` docstring. Update the exact-text test at `tests/test_look_candidates.py:123`.

### WR-03: The log never prints per-clip notes, contrary to EDITOR.md

**File:** `v2r/look/__init__.py:297-302, 316-318`; `EDITOR.md` step 4
**Issue:** EDITOR.md says look "prints ... one plain sentence for anything it could not measure; tell the user those sentences". Only run-wide `missing` sentences and skipped-clip sentences are printed. A clip's `notes` (measurements failed, loudness failed, stills not taken) go into look.json only, and the log line says "A looked at in 0 s, 1 sheet so far". Reproduced: a failed loudness pass prints a normal success line. The final line also says "the sheets are in .../sheets" when there are none (no Pillow, no `select`, or every clip skipped).
**Fix:** After the per-clip status line, `print(note, flush=True)` for each note in `clip["notes"]`. Print the sheets sentence only when `result["sheets"]` is not empty.

### WR-04: The temporary folder is outside the work folder

**File:** `v2r/look/__init__.py:166`
**Issue:** `tempfile.TemporaryDirectory(prefix="v2r-look-")` uses the system temp folder, so FFmpeg's text files are written outside the work folder, against "nothing is written outside the work folder". A killed run (the sandbox stops commands) leaves `v2r-look-*` folders behind in `/tmp`, and a full `/tmp` raises ENOSPC, which is reported as "The work folder ran out of room".
**Fix:** `tempfile.TemporaryDirectory(prefix=".v2r-look-", dir=work_dir)`, and have `clear_last_look` remove leftover `.v2r-look-*` folders.

### WR-05: All of a clip's stills are read and held in memory, including ones that cannot be placed

**File:** `v2r/look/__init__.py:189-191`; `v2r/look/sheets.py:90-119`
**Issue:** `grab_stills` is asked for every still of the clip, captures all of them in one `stdout` bytes object, then makes a Pillow copy of each. The sheet cap allows at most 240 placed stills, but the clip's whole list is read even when the cap is nearly reached. A 10-minute clip is 400 stills at about 1.2 MB each (tall cell 477x848), roughly 0.5 GB of bytes plus another 0.5 GB of images in a sandbox of unknown memory. `MemoryError` is caught per clip, but an OOM kill is not. Memory is out of v1 scope in general; this is listed because it can end the whole run.
**Fix:** Work out how many cells are left (`MAX_SHEETS_PER_RUN * cells - placed`) and grab only that many, or read the pipe in frame-sized chunks and paste as they arrive.

### WR-06: A failure part-way through `SheetBook.add` leaves the book out of step with look.json

**File:** `v2r/look/sheets.py:171-220`; `v2r/look/__init__.py:189-194, 281-286`
**Issue:** `add()` increments `used` and `count` and pastes pictures before saving. If a save raises `OSError` (not ENOSPC) the clip becomes `skipped`, but those cells stay marked used, so later clips start after blank cells and a sheet that was never saved is counted in `names()` (so look.json can name a sheet file that does not exist). `look_at_clip` only catches `ValueError` from this call because it wraps `grab_stills` and `add` in one `try`.
**Fix:** On any exception in `add`, roll back `used`, `count` and `current` to their values before the call (snapshot at the top of `add`), and remove a `.part.jpg` left behind.

### WR-07: Manifest checks let bad values through

**File:** `v2r/look/__init__.py:56, 97, 151`; `v2r/look/measure.py:341`
**Issue:** (a) `manifest.get("shape") in settings.SHAPES` raises `TypeError: unhashable type: 'list'` for a list or dict shape; this is not a `LookError`, so the run ends with a traceback. (b) `LETTER = ^[A-Z]{1,3}$` with `re.match` accepts `"A\n"` (`$` matches before a trailing newline); that letter is printed, drawn on a still and written to JSON. (c) `working_facts` cleans `seconds` with `finite()` (so the string `"3.0"` passes), but `measure_clip` reads the raw `entry["working"]["seconds"]`, and `ffmpeg_timeout("3.0")` is `120 + "3.0" * 10`, a `TypeError` that skips the clip with a misleading sentence. (d) `still_plan` runs before the per-clip `try`, so a corrupt but finite `seconds` of 1e12 would loop for a very long time in `base_times`.
**Fix:** `isinstance(manifest.get("shape"), str) and manifest["shape"] in settings.SHAPES`; use `LETTER.fullmatch`; pass the cleaned `seconds` into `measure_clip`; reject `seconds` above a settings limit in `working_facts` and `still_plan`.

### WR-08: No tests for the sheet cap, the thinning arithmetic, or the failure paths above

**File:** `tests/test_look.py`, `tests/test_look_sheets.py`, `tests/test_look_candidates.py`
**Issue:** `grep` finds no test of `run_interval`, `sheets_needed`, `still_plan`, `SheetBook.full`, `rhythm_thinned`, or the "Even with fewer stills" sentence. I checked by hand that `sheets_needed` agrees with the real `SheetBook` for a mixed-orientation run (6 and 6), so the arithmetic looks right, but nothing keeps it so. Also untested: a cut on a window edge inside a merged stretch (CR-01), non-finite motion (CR-02), notes plus failed stills (CR-03), and a hung FFmpeg (`TimeoutExpired`).
**Fix:** Add tests with a small `MAX_SHEETS_PER_RUN` (monkeypatched) for: no thinning, thinned to 1.5 and to 2.0, nothing fits (full), a photo mixed in, tall and wide alternating; a `subprocess.TimeoutExpired` monkeypatch for the measuring and stills commands; and the three cases above.

## Info

### IN-01: Process rule from CLAUDE.md not fully followed for decisions

**File:** `CLAUDE.md` ("Settled so far"), `docs/decisions.md`
**Issue:** Four Stage 15 lines were added to decisions.md, but CLAUDE.md's settled list still says extras come "at movement peaks and scene changes" (no sound peaks) and still says "one a second". Nothing records the 20-sheet cap thinning the rhythm to 1.5 or 2 s. By my run of `run_interval`, ten 30-second clips already thin to 2 s (17 sheets), and five minutes of footage is enough to trigger it, so "one a second" is the exception for a normal attachment set. Candidates (their exclusions and their order, D-18) are also not recorded as a difference from the guide.
**Fix:** Add the sound-peak, thinning and candidates decisions to the settled paragraph in CLAUDE.md and as dated lines in decisions.md. Note that thinning is decided from the full extras allowance, so it thins earlier than the footage strictly needs.

### IN-02: Candidates drop stretches silently and the order is partly an editorial preference

**File:** `v2r/look/pick.py:329-333, 334`; `v2r/look/__init__.py:30-32`
**Issue:** A window with a cut, a shaky half or a soft half is removed and nothing in look.json says a stretch was removed or why, so Claude cannot tell a boring stretch from an excluded one. The order (steady first, more movement first) quietly prefers footage with a moving subject. The docstring says the order is "steady camera, then sharp picture, then movement", but sharpness is a filter, not a sort key. A tier-2 window that is mostly still but has one panning half is worded "camera panning".
**Fix:** Correct the docstring; consider listing exclusions as facts (for example `excluded` windows with a reason), and leave ordering by time with the facts attached if the handbook is to own the choice.

### IN-03: Shake is averaged across shot changes

**File:** `v2r/look/measure.py:118-138`
**Issue:** Cut frames are skipped, but the 1-second centred average still includes the frames before and after the cut, which belong to different shots. A pan before a cut and a still shot after it inflate the "shake" of the frames near the cut and can turn a steady half second "shaky", which then excludes candidate windows.
**Fix:** Restrict `near` to rows in the same shot (stop at the nearest skipped index on each side).

### IN-04: Numbers and names outside settings.py, and a wrong range comment

**File:** `v2r/look/measure.py:40, 27, 33-34, 194, 371`; `v2r/look/sheets.py:15`; `v2r/look/pick.py:275`; `v2r/settings.py:92`
**Issue:** `round(f["t"], 1)` for shot changes and the `04.1f` label format are tied to `LOOK_FPS = 10` and to nothing in settings (`LOOK_DECIMALS` is not used for them). `"motion.txt"` is written as a literal in the `deshake` lambda although `MOTION_FILE` exists. The `12` columns of the motion row is a fact of the format and could be a named constant. `DESHAKE_CONTRAST` is commented "0-255" but deshake accepts 1 to 255.
**Fix:** Use `MOTION_FILE` in the lambda, a `LABEL_DECIMALS` setting, and correct the comment.

### IN-05: Sheet sizes do not match their stated rationale or the result limit

**File:** `v2r/settings.py:70, 81`; `EDITOR.md` step 4
**Issue:** `SHEET_WIDTH` is justified by Claude's viewer shrinking "the long edge to about 1,568", but a tall sheet is 1950 x 2576, so it is shrunk to about 61% and a 477-pixel cell is seen at about 290 pixels. Twenty sheets of up to 1.5 MB (and `SHEET_MAX_BYTES` is a target, not a guarantee, since the lowest quality is kept whatever the size) can come to 30 MB, above `MAX_RESULT_BYTES` (24 MiB), and EDITOR.md says to send sheets "when asked" with no limit.
**Fix:** Size tall sheets to a long edge of about 1568, and tell the handbook to send a few sheets at a time.

### IN-06: Hang budget and unused parameters

**File:** `v2r/look/measure.py:180, 229`; `v2r/look/sheets.py:110`; `v2r/doctor.py:70`; `v2r/look/pick.py:278`
**Issue:** Each clip runs up to three FFmpeg commands, each allowed `120 + 10 x seconds`; a hung clip of 60 s costs up to 12 minutes per command and there is no budget for the whole run. `doctor.ffmpeg_names` has no timeout. `candidate_reason` takes `start` and `end` and uses neither. `TALL_SIZE` in the tests holds both orientations, and several `test_run_*` tests are parametrized by `shape` without using it.
**Fix:** Optional overall time limit in settings; drop the unused parameters; rename `TALL_SIZE`.

### IN-07: A measure docstring describes a signalstats value wrongly

**File:** `v2r/look/measure.py:7-8`
**Issue:** `brightness_low` and `brightness_high` are said to be "the average of each picture's darkest tenth and brightest tenth". FFmpeg's `YLOW` and `YHIGH` are the 10th and 90th percentile values, not averages of those tails. Stage 16's `match` reads these.
**Fix:** "the brightness below which a tenth of the picture falls, and above which a tenth falls".

---

_Reviewed: 2026-10-18_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
