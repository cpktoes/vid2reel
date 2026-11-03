---
phase: 05-stage-17-editor-s-handbook
reviewed: 2026-11-02T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - v2r/__main__.py
  - v2r/normalize.py
  - tests/test_work_option.py
  - tests/test_editor_handbook.py
  - tests/test_normalize.py
findings:
  critical: 0
  warning: 2
  info: 2
  total: 4
status: issues_found
---

# Phase 5: Code Review Report

**Reviewed:** 2026-11-02
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

The change is small and clean. `--work` on normalize and look and `--no-size-limit` on normalize are wired straight through to existing parameters (`out_dir`, a new `size_limit` flag). No editing judgement and no behaviour number was added to Python. FFmpeg is untouched. The new size-limit sentence contains no option name, and the tests check that. The look command refuses two different folders and accepts the same one named twice, as intended. Running `uv run pytest -q tests/test_work_option.py tests/test_normalize.py tests/test_editor_handbook.py` gave 230 passed.

Two real weaknesses remain. Making `--work` reachable from the command line lets the "clear the last job" step run on any folder the user names. The handbook guard checks the order of the steps but never checks that all six are present.

## Warnings

### WR-01: `--work` lets "clear the last job" delete unrelated lettered files in any folder

**File:** `v2r/normalize.py:117-128` (reached through `v2r/__main__.py:39-42, 107`)
**Issue:** `clear_last_job` deletes every file in the work folder whose name matches `^[A-Z]{1,3}(-photo)?(\.part)?\.(mp4|jpg)$`. It also deletes `manifest.json` and `look.json`. It spares only files passed as inputs. Before this phase the folder was always the repo's own `work/`. With `--work` the user can aim it at any folder, including one holding their own media (`--work ~/Movies/shoot`, or `--work .`). In that case any file such as `A.mp4`, `IMG.jpg` or `MOV.mp4` that was not passed on this command line is silently unlinked. Those are not working copies, and they may be originals. This conflicts with "originals are never modified". The help text says only "its last job is cleared first", which does not warn the user of this. `test_normalize_work_clears_only_that_folders_last_job` covers only `notes.txt`. It never covers a lettered file that this tool did not make.
**Fix:** Delete only what the previous job's manifest says it made, and refuse to clear a folder that has lettered files but no readable `manifest.json`. Sketch:
```python
def clear_last_job(out_dir, inputs):
    protected = {Path(p).resolve() for p in inputs}
    made = _names_from_old_manifest(out_dir)   # {"A.mp4", "B-photo.jpg", ...}; empty when no manifest
    for entry in Path(out_dir).iterdir():
        last_job = entry.name in made or entry.name in LAST_JOB_RECORDS or (entry.name.endswith(".part") and LAST_JOB_FILES.match(entry.name))
        if last_job and entry.is_file() and entry.resolve() not in protected:
            entry.unlink()
```
If that is too big a change for this phase, make normalize raise `NormalizeError` when a `--work` folder already holds a matching lettered file but no `manifest.json`. Add a test with an unrelated `A.mp4` in the folder.

### WR-02: Handbook guard does not require the six steps, and finds commands only in one spelling

**File:** `tests/test_editor_handbook.py:8-9, 17, 57-63`
**Issue:** The module docstring promises "the six steps in order", but the check is `seen != sorted(seen, key=STEPS.index)`. That tests the order of whichever steps happen to be present. An EDITOR.md that drops `look`, `check`, `match` or `render` entirely still passes, because only a handbook with no commands at all fails (`test_an_empty_handbook_is_refused`). Also, `NAMED` matches only the literal form `python3 -m v2r NAME`. A step written as `python -m v2r look`, `v2r look` or `python3 -m v2r  look` is not seen. It is then neither checked against the parser nor counted in the order. A misspelled command in that form would pass.
**Fix:** After the unknown-command loop, add a missing-step check, and put a test beside the order tests:
```python
for step in STEPS:
    if step not in names:
        problems.append(f"EDITOR.md never runs `v2r {step}`.")
```
Loosen the pattern to `r"(?:python3? -m )?v2r\s+([a-z][a-z-]*)"` only if prose such as "v2r is ..." cannot produce false matches. Otherwise keep it strict and say in the failure text that commands must be written as `python3 -m v2r NAME`. Note: `test_a_text_of_exactly_1500_words...` and the join tests build texts with all six steps, so they stay green.

## Info

### IN-01: A mistyped `--work` path is silently created

**File:** `v2r/normalize.py:668-669`
**Issue:** `out_dir.mkdir(parents=True, exist_ok=True)` runs before anything is checked. A typo such as `--work /Volumes/Dirve/set-one` creates the whole path, and the failure shows up later as an unrelated message. `--work ""` becomes `Path("")`, which is the current folder, and that feeds straight into WR-01.
**Fix:** Keep `mkdir` for the final folder only (`parents=False`), or print the folder that was created. Reject an empty `--work` in `__main__.py`.

### IN-02: `look` help text and description are stale or duplicated

**File:** `v2r/__main__.py:47-56`
**Issue:** The command's own help still says "working copies in work/", although the folder can now be named two ways. The positional `folder` and the `--work` option carry the same help string. A user reading `--help` cannot tell whether the two are meant to be used together.
**Fix:** Give `folder` a note such as "the same as --work; name it once", and change the command description to "in the work folder".

---

_Reviewed: 2026-11-02_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
