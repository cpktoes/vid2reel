---
phase: 05-stage-17-editor-s-handbook
plan: "07"
subsystem: release-records
tags: [phone-test, decisions, traceability, HAND-01, HAND-05]
requires:
  - phase: 05-stage-17-editor-s-handbook
    provides: plans 01 to 06 (the handbook, the profiles, the rehearsals, the gates and the first push)
provides:
  - "The Stage 17 phone test, approved by the user on 2026-11-02, recorded without names (phone-limits row 17)"
  - "Three dated Stage 17 decision lines for the ways this stage differs from the guide, and the matching additions to CLAUDE.md"
  - "HAND-01 to HAND-05 marked complete in REQUIREMENTS.md"
affects: [verify-work, merge into main]
actuals:
  tokens: 3000
  tasks: 2
  commits: 2
key-files:
  created: []
  modified: [docs/phone-limits.md, docs/decisions.md, CLAUDE.md, .planning/REQUIREMENTS.md]
key-decisions:
  - "One phone test inside a Project on the stage's branch stands for both of the guide's checks (D-11)"
requirements-completed: [HAND-01, HAND-02, HAND-03, HAND-04, HAND-05]
status: in-progress
---

# Phase 5 Plan 07: the phone test, the records and the closing push Summary

**IN PROGRESS: Tasks 1 and 2 are done (the phone test approved and the records written and committed locally); Task 3 (the user's word on the push) and Task 4 (the push) are pending. Nothing from this plan has been pushed.**

## Task 1: the phone test (approved 2026-11-02)

What ran, in numbers and paths only:

- It ran from the user's own phone, inside a Project of the user's own account whose Reel style profile was pasted in plan 03. It did not run inside one of her account's Projects, and it used seven files rather than two to four.
- The message was exactly: "use branch stage-17-handbook. Make a reel, about 20 seconds."
- Time: about 9 to 11 minutes from the message to the reel, about 3 of those converting the seven files.
- The user replied "approved" and reported nothing wrong.

What the user did not itemize (recorded as not itemized, never as a result): the number of questions asked; whether the reply named Vid2Reel; whether it offered a cover and said a song can be added; each of the plan's step 6 watch checks; whether the profile was followed.

Deviation from the plan: the plan says "one of her account Projects" with two to four clips. CLAUDE.md's merge rule (a reel made from a phone by the user on the stage's branch) is met as written; the plan's wording is stricter than the rule.

## Task 2: the records

- docs/phone-limits.md: row 17.
- docs/decisions.md: three lines dated 2026-11-02 for Stage 17 (the single phone test; the clips' order wins when time carries the meaning and the top or bottom of the length range follows how much good footage there is; a photo runs up to four seconds). Already recorded and not repeated: the six lines of 2026-10-24, the computer-only size switch (2026-11-01) and the 1,500-word cap with four craft rules (2026-11-02).
- Checked and skipped: the move rule ("camera_state panning or shaky") says the same as the guide's Stage 17 prompt ("moving or shaky"), so no line; there is no Reel style guard test in tests/test_editor_handbook.py, so no line; the guide's Stage 17 does not say who opens the rehearsal window (it says "after /clear"), so the process difference below is here only.
- CLAUDE.md: the "Settled so far" sentence now also holds the clips' order when time carries the meaning, the top or bottom of the length range, the up-to-four-second photo, and the single phone test (Stage 17).
- .planning/REQUIREMENTS.md: HAND-01 to HAND-05 are `[x]` and the traceability row says `Complete`.

Handbook check: `uv run pytest tests/test_editor_handbook.py -q` gave 11 passed; EDITOR.md is 1299 words (cap 1,500).

## How this stage differs from docs/field-guide.html (for the user to have the guide revised)

1. Phone test: one test inside a Project on the stage's branch stands for both of the guide's checks ("make a reel inside a Project" and "use branch stage-17-handbook"). It ran in a Project of the user's own account from his phone with seven files, where the guide says one of her account's Projects with two clips.
2. The rehearsals ran as fresh Claude desktop sessions started by the orchestrating session on the user's word, each reading only EDITOR.md, the schema and its own outputs, rather than windows the user opened himself. The guide's intent (a fresh session that knows nothing else) was kept.
3. Until the music library exists a reel has no music, with the clips' own sound kept and the reply saying a song can be added in the posting app. The guide has the test tone stand in (2026-10-24).
4. Two of the brief's questions come forward from Stage 19 into Stage 17: what the reel is about and which moment is the star (2026-10-24).
5. EDITOR.md is held to 1,500 words by a test; the guide gives no number. Four craft rules were added (thumbnail first frame, a loop-like end, shortest first three shots, nothing important in the bottom fifth); the guide has none of them (2026-11-02).
6. Two ordering rules and the photo length were added during the rehearsals in the user's own words: the clips' order wins when time carries the meaning; the top or bottom of the length range follows how much good footage there is; a photo runs up to four seconds (2026-11-02).
7. Code: normalize and look take `--work FOLDER` (not in the guide, 2026-10-24) and normalize takes `--no-size-limit`, a computer-only switch kept out of EDITOR.md (2026-11-01).

## Open item for the user (not a decision)

Every rehearsal took a profile's standing answers to the brief as the message saying what the reel is about, so no question was asked. Whether that is wanted is the user's call for the handbook.

## Last scan, commits and hashes

To be filled in at Task 3 from the report of the scan run after this draft was committed.

## Next

Task 3: the user's word on pushing the closing commits. Task 4: the push, if he says "push". The merge into main waits for /gsd-verify-work and the user's go-ahead.

## Deviations from Plan

The plan's wording of the phone test ("one of her account Projects", two to four clips) was not met as written; the user's own-account Project and seven files stood in, and the user approved. Otherwise none so far.

## Known Stubs

None.
