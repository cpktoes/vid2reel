---
phase: 05-stage-17-editor-s-handbook
plan: "06"
subsystem: release-gates
tags: [full-suite, hand-02, private-data-scan, push]
requires:
  - phase: 05-stage-17-editor-s-handbook
    provides: plans 01 to 05 (the --work options, the handbook guard tests, the profiles, the approved handbook, the rehearsals)
provides:
  - the full suite green on stage-17-handbook (1034 passed)
  - HAND-02 and HAND-03 proved on the final branch
  - a clean private-data scan of everything the push carries
  - stage-17-handbook on GitHub at 54dc0d5, main untouched
affects: [05-07 phone test]
actuals:
  tokens: 2219
  tasks: 3
  commits: 1
tech-stack:
  added: []
  patterns: [scan the whole history a push carries, not only the tip]
key-files:
  created: [.planning/phases/05-stage-17-editor-s-handbook/05-06-SUMMARY.md]
  modified: [.planning/STATE.md, .planning/ROADMAP.md]
key-decisions:
  - "Push as is (option-b), because the history scan found nothing to scrub (2026-11-02)"
patterns-established:
  - "Private-names list built outside the repo, used for one scan, then deleted"
requirements-completed: [HAND-02, HAND-03]
duration: "one session; the full suite took 8m46s"
completed: 2026-11-02
status: complete
---

# Phase 5 Plan 06: the gates and the push Summary

**Full suite green (1034 passed), no editing judgement in Python, a private-data scan of all 29 commits a push carries finding nothing, and `stage-17-handbook` pushed to `54dc0d5` on the user's word with `origin/main` unmoved at `247685e`.**

All three tasks are done. No code, handbook, test, fixture or guide file was changed by this plan; it only ran gates, asked, and pushed.

## Task 1: gate results (2026-11-02)

At scan time: branch `stage-17-handbook`, HEAD `54dc0d5`, `origin/main` `247685e`, `origin/stage-17-handbook` `daed040`. 29 commits in `origin/main..HEAD`, of which 27 are already on GitHub and 2 are not.

| Gate | Result |
| --- | --- |
| 1. Full suite, `run-with-timeout 1800 -- uv run pytest -q` | **1034 passed in 526.10s (0:08:46)**, no failure, run in the background |
| 2. `git diff --name-only main -- v2r/` | Prints `v2r/__main__.py` and `v2r/normalize.py` (the plan expected only the first; the second comes from the user's quick task 415d9c5 of 2026-11-01, see the hunks below) |
| 2a. `v2r/__main__.py` hunks | (1) normalize gets `--work FOLDER` (default: work/ in this repo). (2) normalize gets `--no-size-limit` (a switch, default off). (3) look's positional argument is renamed `folder` and look gets `--work`, both meaning the work folder. (4) normalize passes `args.work` and `size_limit=not args.no_size_limit` through. (5) look refuses with one sentence when the folder is named twice and the two differ. (6) look passes `--work` if given, else the folder. No hunk picks a shot, length, order, move or filter |
| 2b. `v2r/normalize.py` hunks (quick task 415d9c5) | `convert_one` and `normalize` take `size_limit=True`; the over-the-cap check runs only when it is true; the refusal sentence now says "a phone can reliably send ... On a computer the same reel can be made with it included". Only a size check is switched; no editing judgement |
| 2c. `tests/test_normalize.py` hunks (quick task 415d9c5) | The skipped-file sentence is asserted exactly; two new tests for `--no-size-limit` (library call and command line, tall and wide) |
| 2d. HAND-02 and D-13 | HAND-02 holds: nothing in Python picks a shot, length, order, move or filter. D-13 holds except the user's quick task 415d9c5 (approved 2026-11-01: a size-check switch for a computer, not an editing choice) |
| 2e. Other files that differ from main | `CLAUDE.md`, `EDITOR.md`, `README.md`, `docs/decisions.md`, `tests/test_editor_handbook.py` (the handbook guard), `tests/test_work_option.py` (this phase's own tests), and `.planning/` files. Nothing else |
| 3. `git diff --name-only main -- pyproject.toml uv.lock requirements.txt docs/field-guide.html skill/` | Prints nothing: no package added, requirements.txt needs no regeneration, the guide and the skill are untouched |
| 4. `uv run pytest tests/test_editor_handbook.py -q` | **11 passed**. `wc -w < EDITOR.md` is **1299** (cap 1,500, raised by quick task 2a94e74 on 2026-11-02) |
| 5a. Files under fixtures/ or work/ in `origin/main...HEAD` | none |
| 5b. Media files (video, audio, images) | none |
| 5c. E-mail addresses in added lines | The grep counts 5 lines, all `@EDITOR.md` or `@CLAUDE.md` file references in planning text. No address |
| 5d. Home path | 0 in the diff; no tracked file at HEAD holds it |
| 5e. Mac user name as a whole word | 0 in `git log -p origin/main..HEAD`; no tracked file at HEAD holds it |
| 5f. Secrets (key, secret, token, password followed by `:` or `=`) | 0 |
| 5g. Attribution lines in commit messages (`co-authored-by:` or `generated with [claude`) | 0 |
| 5h. Private names, tracked files at HEAD | 0 files |
| 5h. Private names, commit messages in `origin/main..HEAD` | 0 |
| 5h. Private names, history (`git log -p origin/main..HEAD`) | **0 hits over 29 commits**; no commit or path to report. Over only the 2 commits not yet on GitHub: 0 |
| 6. Hashes | `origin/main` `247685e`; `HEAD` `54dc0d5` |

How the private-names list was built: a temporary file outside the repo, from names on this Mac only (the fixture set folder names, distinctive words from the profile file names, the taste-notes file name, first names and place words inside the clip file names, and the Mac user name), 18 entries, never from the contents of any file under fixtures/. A second list of five ordinary English words taken from the same file names (too common to be a fair test) gave 3 tracked files and 1 history line of plain-language hits; it was counted only and has been deleted.

### Commits not yet on GitHub at scan time

`origin/stage-17-handbook` was `daed040`. Two commits were not on GitHub, both planning files only:

- `8b95bf0` docs(05-03): profiles reviewed and pasted, plan complete
- `54dc0d5` docs(05-05): five sets rehearsed and approved, plan complete

Files they change: `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `05-03-SUMMARY.md`, `05-05-SUMMARY.md`. Nothing already on GitHub was rewritten.

### Note on the field guide

`git diff main` is clean for `docs/field-guide.html`, but `origin/main...HEAD` lists it because local main holds the guide's twentieth edition (`512f4cc`, the user's own replacement), which is already on GitHub's `stage-17-handbook` branch. This plan did not touch the guide.

## Task 2: the user's word (2026-11-02)

The history count was 0, so there was nothing to scrub and option-a (scrub the unpushed commits first) fell away. The user chose **option-b, push as is**, on 2026-11-02. No backup branches were made because no scrub happened.

## Task 3: the push (2026-11-02)

- `git push -u origin stage-17-handbook` moved the remote branch from `daed040` to `54dc0d5`, carrying the two unpushed commits `8b95bf0` and `54dc0d5` (planning files only).
- `git ls-remote origin stage-17-handbook` prints `54dc0d5`, equal to local HEAD at that moment.
- `origin/main` was `247685e` before and `247685e` after. `main` was never pushed, merged or force-pushed; no `--force` was used.
- The temporary names file was deleted after the push.
- The branch was already on GitHub up to `daed040` before this plan (pushed earlier in the phase on the user's word), so this plan's push carried only those two commits. 27 of the 29 commits in `origin/main..HEAD` were already public when Task 1 scanned them.
- The commit that closes this plan (this summary, STATE.md and ROADMAP.md, planning files only) is pushed by the orchestrator right after, on the same decision.

## Requirements

- **HAND-02 satisfied.** Nothing in Python picks a shot, length, order, move or filter. Re-proved on the final branch.
- **HAND-03 satisfied.** Taste stays out of the repo; the private-data scan found no account, person or set name in tracked files, commit messages or history.

## Deviations from Plan

**1. [Expected scope, approved earlier] `v2r/normalize.py` also differs from main.** The plan expected `git diff --name-only main -- v2r/` to print only `v2r/__main__.py`. It also prints `v2r/normalize.py`, from the user's quick task 415d9c5 (2026-11-01): a size-limit switch for a computer, no editing judgement. So D-13 holds except that quick task. The hunks were read one by one (gate 2a to 2c above).

Otherwise: none, the plan ran as written.

## Known Stubs

None.

## Threat Flags

None. This plan added no code, endpoint or file access.

## Next

Wave 5, plan 07: the phone test inside one of her Projects on `stage-17-handbook`, the phone-limits row, decision lines and traceability.

## Self-Check: PASSED

The summary file exists; the commits named (`8b95bf0`, `54dc0d5`, `247685e`, `daed040`) exist in the repo; `git ls-files fixtures work | wc -l` prints 0.
