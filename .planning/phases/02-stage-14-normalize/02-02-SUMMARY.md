---
phase: 02-stage-14-normalize
plan: "02"
subsystem: tooling
tags: [doctor, ffmpeg, decisions]

requires:
  - phase: 02-stage-14-normalize
    provides: plan 01 normalize command (the FFmpeg pieces it uses are what doctor now lists)
provides:
  - "doctor report lines for every extra FFmpeg filter and decoder normalize uses"
  - "doctor.missing_ffmpeg_features(): fast, network-free check returning plain phrases"
  - "Stage 14 decisions recorded in docs/decisions.md and CLAUDE.md"
affects: [02-05, stage-14]

actuals:
  tokens: 6500
  tasks: 2
  commits: 2

key-files:
  created: [tests/test_doctor.py]
  modified: [v2r/doctor.py, docs/decisions.md, CLAUDE.md, .gitignore]

key-decisions:
  - "Five Stage 14 decision lines dated 2026-10-13 (working size, photo libraries, HDR second-best, unenforced attachment count, letters kept by skipped files)"

requirements-completed: [NORM-08]

duration: 10min
completed: 2026-10-13
status: complete
---

# Phase 2 Plan 02: Doctor lists every FFmpeg piece normalize needs Summary

**`v2r doctor` now reports 11 more filters and 5 decoders (one plain line each), `missing_ffmpeg_features()` gives normalize a quick check of the same lists, and the Stage 14 decisions are written down.**

## What this does, in plain English

- The doctor report grew by 16 lines: the filters format, fps, setsar, setpts, loop, transpose, hflip, vflip, aresample, apad and anullsrc, and the hevc, h264, aac, mjpeg and png decoders. Each says "available" or "MISSING". Running doctor from the phone will show whether the sandbox has them all. On this Mac every line says available.
- There is a new function, `missing_ffmpeg_features()`, that checks the same lists and returns an empty list when nothing is missing, or plain phrases such as "the apad filter". It makes three quick local FFmpeg calls and never uses the network. Plan 05 will call it.
- The settled working size and the other Stage 14 decisions are written into docs/decisions.md and CLAUDE.md. `normalize.log` can never be committed (like `join.log`).

## Task Commits

1. **Task 1: doctor lists the FFmpeg pieces and offers one check** - `abec230` (feat)
2. **Task 2: Stage 14 decisions, CLAUDE.md lines, ignore normalize.log** - `532eaed` (docs)

## Where this stage differs from the guide (so you can have the guide revised)

- **Photos** are read with two Python libraries (Pillow and pillow-heif), because the sandbox's FFmpeg cannot open HEIC. The guide asks for FFmpeg features only.
- **HDR** is converted with the second-best method (zscale and tonemap on the processor). The best one needs a graphics driver the sandbox lacks, and the Dolby Vision layer is ignored. The guide asked to be told.
- **Attachment count** is not enforced by normalize: it tries every file, and a whole-run failure asks for fewer clips. The guide refuses files by the Stage 11 limits.
- **Letters of skipped files**: a file that cannot be used keeps its letter and gets a "skipped" entry. The guide does not say.
- The working size is the same as the guide's pick.

## What to test from a phone before merging

This plan changes only the report and notes, not video. When you run `python -m v2r doctor` in the chat, look for 16 new lines (11 "filter" lines and 5 "decoder" lines) and check that none says MISSING. If one does, tell me which. The full video check is still plan 08's phone test.

## Deviations from Plan

None - plan executed exactly as written. Task 1 was marked TDD; tests and code were committed together in one commit, not as a separate failing-test commit first.

## Issues Encountered

None. Full suite: 64 passed. Checked on FFmpeg 8.0.1 (this Mac), not the sandbox's 6.1.

## Known Stubs

None.

## Threat Flags

None. T-2-09 (only the intended lines changed in the public docs; no person, account or fixture named), T-2-12 (three local calls, no network) and T-2-13 (`/normalize.log` ignored) are in place.

## Self-Check: PASSED
