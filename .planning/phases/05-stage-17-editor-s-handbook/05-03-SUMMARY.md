---
phase: 05-stage-17-editor-s-handbook
plan: "03"
subsystem: taste-profiles
tags: [profiles, rehearsal-kit, privacy, handbook]
requires: []
provides:
  - "Three Reel style profiles, reviewed by their owners and pasted into each account's Claude Project (kept in fixtures/, untracked)"
  - ".planning/phases/05-stage-17-editor-s-handbook/05-REHEARSAL.md: the rehearsal kit, placeholders only"
affects: [05-05, 05-06]
tech-stack:
  added: []
  patterns: ["profiles are referred to by number (1, 2, 3), never by name; counts only"]
key-files:
  created: [.planning/phases/05-stage-17-editor-s-handbook/05-REHEARSAL.md]
  modified: []
key-decisions:
  - "Profiles are numbered 1, 2, 3 in the order `ls fixtures/profiles/*.md | sort` lists them, so no file or account name is ever written down"
  - "One [check] line is deliberately left in profile 2 by the user's choice"
requirements-completed: [HAND-03]
status: complete
actuals:
  tokens: 5000
  tasks: 3
  commits: 2
metrics:
  completed: 2026-11-02
---

# Phase 5 Plan 03: Profiles checked, rehearsal kit, owners' review and paste Summary

Three taste profiles are confirmed untracked, free of private names in tracked text, reviewed by their owners and pasted into their Claude Projects; the rehearsal kit that plan 05 runs from is written.

## What changed (plain English)

Nothing under v2r/, tests/, EDITOR.md or docs/ changed, so no phone test is needed for this plan. The only new file in the repo is the rehearsal kit, 05-REHEARSAL.md, in this phase folder. The profiles themselves stay in fixtures/, which git ignores.

## Task 1: profiles checked by count and ignore status (2026-10-24)

- Ignore rule: `.gitignore:3:/fixtures/`.
- 3 profile drafts, each with the five headings (Reel style, Always, Never, Usually, My answers to the brief) at lines 1, 5, 11, 16 and 22 (one draft has the last heading at line 21).
- [check] lines at that time: 5, 4 and 4 (profiles 1, 2, 3).
- Tracked files with a private-name hit: 0.
- History hits for private names over 19 commits: 0. This is the number plan 06 needs.

## Task 2: the rehearsal kit (2026-10-24)

05-REHEARSAL.md, commit ce1dde3 (`docs(05-03): the rehearsal kit, placeholders only`). It holds placeholders only; the private-word search of it printed 0.

How to use it, in plain English: open it at the start of each rehearsal. Section 1 is what to do before each run, section 2 is the prompt to give a fresh session, section 3 the message, section 4 the one unreadable file to include, section 5 what to do after a run. Section 6 sets up the second profile, section 7 compares the two cut lists by category, section 8 traces a bad reel back to its cause, section 9 is the scoring. Section 10 lists what never leaves this Mac.

## Task 3: the owners' review and paste (2026-11-02)

[check] lines marked in each profile, by profile number:

| Profile | At Task 1 (2026-10-24) | After the quick task of 2026-11-02 (commit 2a94e74 added 14 new [check] lines across the three) | After the owners' review |
|---------|------------------------|-----|-----|
| 1 | 5 | 9 | 0 |
| 2 | 4 | 6 | 1 |
| 3 | 4 | 4 | 0 |

Pasted into its Claude Project, 2026-11-02: profile 1 yes, profile 2 yes, profile 3 yes.

The user chose to leave one [check] line in profile 2. It is a deliberate, known leftover and not an open question.

Re-counted at close with `grep -c "\[check\]"`: 0, 1, 0. `git ls-files fixtures | wc -l` prints 0, and `git status --short` shows nothing tracked under fixtures/.

## Commits

- ce1dde3: docs(05-03): the rehearsal kit, placeholders only
- The closing planning commit for this summary (see git log; subject starts `docs(05-03)`)

## Deviations from Plan

None to the plan's steps. One timing note: between Task 1 and Task 3 the quick task of 2026-11-02 added [check] lines, so the review counts above are measured from a larger starting number than Task 1 recorded. Task 1's counts are kept as first recorded.

## Next

Plan 05 (the five rehearsals) can start; its rehearsals are already running in separate sessions.

## Self-Check: PASSED

- 05-REHEARSAL.md exists; commit ce1dde3 exists on stage-17-handbook.
- Counts re-taken this session: 0, 1, 0; 0 tracked files under fixtures/.
