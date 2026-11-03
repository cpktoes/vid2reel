---
phase: 05-stage-17-editor-s-handbook
fixed_at: 2026-11-02T00:00:00Z
review_path: .planning/phases/05-stage-17-editor-s-handbook/05-REVIEW.md
iteration: 1
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 5: Code Review Fix Report

**Fixed at:** 2026-11-02
**Source review:** .planning/phases/05-stage-17-editor-s-handbook/05-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 2 (WR-01, WR-02; IN-01 folded into WR-01)
- Fixed: 2
- Skipped: 0

## Fixed Issues

### WR-01: `--work` lets "clear the last job" delete unrelated lettered files in any folder

**Files modified:** `v2r/normalize.py`, `v2r/__main__.py`, `tests/test_work_option.py`
**Commit:** 6249f18 (`fix(05): normalize cleans only its own job's files`)

**What was wrong:** With `--work FOLDER`, the clean-up deleted every file in FOLDER whose name looked like a working copy (`A.mp4`, `B-photo.jpg`, `.part` files), plus `manifest.json` and `look.json`, even when FOLDER was the user's own media folder that never held a job. That could destroy originals.

**What changed:**
- `clear_last_job` now deletes only the names the folder's own `manifest.json` lists (each clip's working file and photo copy), that manifest, `look.json`, and leftover lettered `.part` copies. If the manifest says the job did not finish, the next letter's two names are included too, because that copy may have been finished just before an interruption.
- A folder with lettered media files but no `manifest.json` is refused with one plain sentence ("The folder already holds A.mp4 and files like it but no manifest.json from an earlier job, so nothing was cleared or converted; ..."), the command exits 1, and nothing is deleted or created.
- A manifest that exists but cannot be read still shows a job was here, so the old lettered-name rule applies to that folder (this keeps the existing tests that plant a junk manifest passing).
- A lettered file that is itself one of the files being converted does not count as stray, as before.
- IN-01: `--work ""` is refused with one sentence before anything runs (the option is now read as text, since `Path("")` silently becomes the current folder). The `--work` folder is now created only after the clean-up checks pass.
- The `--work` help text now says a folder with lettered files but no manifest is refused.

**Tests that prove it** (`tests/test_work_option.py`, temporary folders only, each for tall and wide; all three fail against the old code):
- `test_work_folder_with_a_stray_lettered_file_and_no_manifest_is_refused`: a stray `A.mp4`, no manifest: exit 1, one sentence, folder byte-for-byte unchanged.
- `test_work_folder_loses_exactly_what_its_manifest_lists`: a previous job's manifest lists A and B; A, B, `B.part.mp4`, the manifest and `look.json` go; an unlisted `Z.mp4`, `Y-photo.jpg` and `notes.txt` survive with the same bytes.
- `test_an_empty_work_option_is_refused`: `--work ""` exits 1 with one sentence and creates nothing in the current folder.
- Unchanged and still passing: `test_clear_last_job_*` and `test_manifest_second_run_replaces_last_job` in `tests/test_normalize.py`, and the existing `tests/test_work_option.py` tests.

### WR-02: Handbook guard does not require the six steps, and finds commands only in one spelling

**Files modified:** `tests/test_editor_handbook.py`
**Commit:** b1b8f6a (`test(05): the handbook guard checks every step is present`)

**What was wrong:** The guard checked the order of whichever steps appeared but not that all six were there, and a step written as `python -m v2r X` or a bare `v2r X` was either let through or not seen.

**What changed:** `handbook_problems` now reports, in the existing plain-sentence style, `EDITOR.md never runs `python3 -m v2r STEP`` for each of the six steps that is absent, and `EDITOR.md writes `python -m v2r STEP`` or `` `v2r STEP` `` for either wrong spelling of a step. The command finder now sees only `python3 -m v2r NAME`. The current EDITOR.md passes unchanged.

**Tests that prove it** (new, in `tests/test_editor_handbook.py`):
- `test_a_missing_step_is_refused_whichever_one_it_is`: drops each of the six in turn and the guard names it.
- `test_the_wrong_spellings_of_a_step_are_refused`: both wrong spellings, for every step.
- `test_a_step_written_only_in_a_wrong_spelling_is_missing_and_misspelt`: both complaints fire together.
- `test_every_step_present_is_not_refused` and `test_the_right_spelling_and_ordinary_words_are_not_taken_for_a_wrong_one`: no false alarms on the right spelling or on prose such as "v2r is the name" and "Use v2r join".
- The 11 existing tests still pass.

## Decisions taken (2026-11-02)

The user chose to fix WR-01 and WR-02 (with IN-01 as part of WR-01) and left IN-02 (stale `look` help text) as it is. It is not touched.

## For the user to paste into EDITOR.md

Nothing. The guards pass against the current EDITOR.md, which was not edited.

## Verification

Run in the main checkout (no worktree): `uv run pytest -q tests/test_normalize.py tests/test_work_option.py tests/test_editor_handbook.py` gave 241 passed. The full suite was left to the orchestrator.

## Not changed, worth knowing

- `look --work ""` still means the current folder. `look` only reads the manifest and writes `look.json` and `sheets/`, so it was outside this scope.
- No FFmpeg command and no settings value changed. After this change to how normalize handles folders, no look or sound of any reel changes; a phone test is still advised before merging, as for any change to video processing, but nothing visible should differ.

---

_Fixed: 2026-11-02_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
