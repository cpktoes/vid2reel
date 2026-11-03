---
phase: 07-stage-19-conversation
plan: "05"
subsystem: render
tags: [revise, chain-test, readme, shorter, sound, canvas, both-shapes]

requires:
  - phase: 07-stage-19-conversation
    provides: "plans 01 to 04: revise sound, canvas, reorder, drop, shorter and longer, numbered new lists, check's report after each change"
provides:
  - "tests/test_revise_chain.py: test_the_follow_up_chain, the phone test's chain rendered on generated clips in tall and wide"
  - "README.md: the revise CHANGE row and revise in the --work sentence"
affects: [07-09]

actuals:
  tokens: 20000
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "a chain test finds each new reel as the set difference of reel-*.mp4 names before and after a render"

key-files:
  created:
    - tests/test_revise_chain.py
  modified:
    - README.md

key-decisions:
  - "No code in v2r/ needed changing: the chain passed on its first run in both shapes"

requirements-completed: []

duration: 15min
completed: 2026-11-03
status: complete
---

# Phase 7 Plan 05: The follow-up chain, proved and documented Summary

**On made-up clips, in both shapes, the Mac now runs the exact conversation the phone test will run (a reel, "shorter", "mute it", then the other shape) and every reel lands on the frame count asked for; README.md documents `revise`.**

## What was built

- **The chain test** (`tests/test_revise_chain.py`, `test_the_follow_up_chain`, once for tall and once for wide). Two four-second clips are generated with FFmpeg inside pytest's temporary folder (one in the job's own orientation, one turned the other way), then:
  1. `normalize` and a hand-written three-shot list with every shot's sound kept (5.5 seconds); `render` gives 165 frames.
  2. `revise shorter --to 4.5 --from 1` writes `cutlist-2.json`; every shot still starts at the same second as before; rendering it gives 135 frames.
  3. `revise sound off` reads `cutlist-2.json` (the newest list, named with `--cutlist`) and writes `cutlist-3.json`; its reel has 135 frames and a loudest moment at or below -60 dB (silent).
  4. `normalize` again with the other shape. `cutlist.json`, `cutlist-2.json`, `cutlist-3.json` and all three reels are still there, byte for byte.
  5. `revise canvas <other shape>` reads `cutlist-3.json`, prints "ready to render" and writes `cutlist-4.json`; no `look` and no `match` ran anywhere. Its reel is named for the other shape, is wider than tall exactly when the shape is wide, has 135 frames, and is silent. So the wide (or tall) version is both shorter and muted, which proves each follow-up builds on the newest list.
- **Isolation.** Every command gets `--work` inside the temporary folder, and the default work folders of normalize, look and revise are redirected there too; the test asserts the default one was never created. Nothing is read from any footage folder.
- **README.md.** A `revise CHANGE` row after the `render` row, naming the six changes, the numbered new list and `--cutlist`; `revise` joins the `--work` sentence; one sentence says `revise` takes `--cutlist` and `--work` after its change word.

## Run time and counts

- `uv run pytest tests/test_revise_chain.py -q`: 2 passed in 23.4 seconds (tall and wide), well under two minutes.
- `uv run pytest tests/test_revise_chain.py tests/test_revise.py -q`: 208 passed in 22.0 seconds.
- `git status --short work fixtures` printed nothing.

## Task Commits

1. Task 1 (tracer): `98b6d4a` test(07-05) the follow-up chain rendered end to end, both shapes
2. Task 2: `f4acf62` docs(07-05) README documents the revise command

## Deviations from Plan

None - plan executed exactly as written. The tracer's gate was met: the chain rendered correctly on the first run, so no change to v2r/ was needed.

## Known Stubs

None.

## Threat Flags

None. The test adds no new surface; T-7-11 and T-7-12 are mitigated as planned (redirected work folders, generated clips only).

## Self-Check: PASSED

- tests/test_revise_chain.py exists; README.md carries the three phrases (each counted once).
- Commits 98b6d4a and f4acf62 exist.

## Plain English for the user

Before you test on the phone, the Mac ran the same conversation itself on made-up clips, once for a tall reel and once for a wide one. It made a reel, then "shorter", "mute it" and "a wide version" (or the tall version, going the other way), and rendered each from the newest list. Each reel came out at exactly the length asked: 5.5 seconds, then 4.5, still 4.5 when muted, still 4.5 in the other shape. The muted reels are silent, the wide one really is wide, and the earlier lists and reels are untouched by the second round of preparing the clips. Making the other version needs no new contact sheets and no new touch-up; the colour numbers already in the list carry over. The test checks shapes, lengths and silence, but it cannot judge how the pictures look. So on the phone, when you ask for the wide version, look at whether its colours seem as even from shot to shot as the tall reel's. README.md now has a line for the new command.
