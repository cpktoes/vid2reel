---
phase: 05-stage-17-editor-s-handbook
plan: "02"
subsystem: tests
tags: [handbook, guards, tests]
requires: []
provides:
  - "tests/test_editor_handbook.py: four mechanical guards on EDITOR.md (length, command names, step order, no --work)"
affects: [05-04]
tech-stack:
  added: []
  patterns: ["tests check counts and names only, never wording"]
key-files:
  created: [tests/test_editor_handbook.py]
  modified: []
key-decisions:
  - "The 1,200-word limit lives in the test file, not in v2r/settings.py (D-04)"
  - "Step order is read from the python3 -m v2r NAME matches only, never from bare words"
requirements-completed: [HAND-01, HAND-02]
status: complete
actuals:
  tokens: 9000
  tasks: 2
  commits: 2
metrics:
  completed: 2026-10-24
---

# Phase 5 Plan 02: Handbook guards Summary

Automatic checks on EDITOR.md: at most 1,200 words, every `python3 -m v2r NAME` it writes is a command v2r really has, the six steps first appear in order (doctor, normalize, look, check, match, render), and the Mac-only `--work` option never appears.

## What changed (plain English)

A new test file, tests/test_editor_handbook.py. Nothing else changed: EDITOR.md, v2r/settings.py and the draft are untouched, and no video is processed differently, so no phone test is needed for this plan.

The four checks, and what to do if one fails after you edit EDITOR.md. The failure message says what is wrong and by how much:
1. Length: "EDITOR.md has N words; two pages is at most 1200." Cut N minus 1,200 words. Words are counted by splitting on spaces and line breaks, the same as `wc -w`.
2. Real commands: "EDITOR.md names `v2r NAME`, which v2r does not have." Fix the spelling, or remove the line. Also fails if the handbook names no command at all.
3. Step order: "EDITOR.md's steps first appear as ...; they should come in the order doctor, normalize, look, check, match, render." Only the written commands count (`python3 -m v2r look`), not the plain English words, so ordinary sentences about looking or checking are fine. `join` is a side road and may appear anywhere.
4. No Mac-only option: any `--work` in the handbook is refused, because the phone never uses it.

You can rewrite any sentence freely; only those four things are checked.

## Proof that each check can fail

Tests build small bad texts and show each check fires: exactly 1,200 words passes and 1,201 fails; an empty text is refused; a made-up command (`bogus`) is refused, because v2r's own parser exits with code 2 for it and 0 for a real command's help (this settles research assumption A1); a copy with the render line moved above the look line is refused; prose using the plain words look, check and match before any command is not refused; `--work` is refused. A missing EDITOR.md makes the real-file test fail.

The guards pass on today's EDITOR.md (912 words) and on the draft body of 05-HANDBOOK-DRAFT.md (1,199 words): the one-off check printed `[]`, meaning no problems.

## Commits

- 1d7feb4: test(05-02): guard EDITOR.md's length, commands and step order
- caba034: test(05-02): each handbook guard fires on a bad text

## Deviations from Plan

None. The plan was executed as written. The whole file was drafted at once and then committed in the plan's two stages, so each commit passes on its own.

Note: `git diff main -- v2r/` lists v2r/__main__.py, but that is plan 05-01's `--work` change already on this branch, not part of this plan.

## Known Stubs

None.

## Threat Flags

None.

## Self-Check: PASSED

tests/test_editor_handbook.py exists; commits 1d7feb4 and caba034 exist; 11 tests pass.
