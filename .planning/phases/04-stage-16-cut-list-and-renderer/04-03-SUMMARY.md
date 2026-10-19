---
phase: 04-stage-16-cut-list-and-renderer
plan: "03"
subsystem: render
tags: [settings, doctor, ffmpeg, render, guard-test]
requires: ["04-01"]
provides:
  - "the rest of the `# render:` block and a `# match:` block in v2r/settings.py (30 names with plan 01's nine), each with a unit comment"
  - "tests/test_render_settings.py: RENDER_SETTINGS, render_block_lines(), the unit-comment guard and the agreement test"
  - "doctor.MUXERS and doctor.DEMUXERS, 14 more render filters, pcm_f32le as encoder and decoder"
  - "doctor.missing_ffmpeg_features(..., *, muxers=None, demuxers=None)"
  - "v2r.render.RENDER_ENCODERS, RENDER_FILTERS, RENDER_DECODERS, RENDER_MUXERS, RENDER_DEMUXERS and the up-front piece check in render()"
affects: [04-05, 04-06, 04-07, 04-08, 04-09]
actuals:
  tokens: 9000
  tasks: 2
  commits: 2
tech-stack:
  added: []
  patterns:
    - "a guard test per settings block: the assignments in the block must equal the listed names, each with a unit comment"
    - "a caller that names its own lists is held only to those; muxers and demuxers are checked only for doctor's full set or when named"
key-files:
  created:
    - tests/test_render_settings.py
  modified:
    - v2r/settings.py
    - v2r/doctor.py
    - v2r/render/__init__.py
    - tests/test_doctor.py
    - tests/test_render_tracer.py
key-decisions:
  - "missing_ffmpeg_features with no list named checks all five of doctor's lists; with any encoder, filter or decoder list named, an unnamed muxer or demuxer list means none, so normalize checks exactly what it did before"
  - "render's piece check runs right after the FFmpeg-present check and before check, so a computer missing a piece builds nothing and touches nothing in the work folder"
requirements-completed: [CUT-03, CUT-04, CUT-05, CUT-07]
duration: "about 25 min plus the full suite (11 min 40 s)"
completed: 2026-10-19
status: complete
---

# Phase 4 Plan 03: Settings Block, Guard Test, Doctor and Render FFmpeg Checks Summary

Every remaining Stage 16 number now lives in settings.py with its unit and a guard test, and doctor and render both know every FFmpeg piece the stage uses, so render refuses in one sentence instead of failing half-way.

## What changed, in plain English

Nothing about how a reel looks or sounds changes in this plan.

- **Numbers written down.** settings.py now holds 21 more numbers the rest of the stage will use, each with a note saying what it measures: the 4 percent move (`MOVE_AMOUNT`), the third of a second the music takes to drop and come back (`MUSIC_DROP_RAMP`), the music's fade in (half a second) and fade out (one and a half seconds), the loudness target (-14 LUFS) and the peak ceiling (-1 dBTP), the shortest reel (3 seconds), the share of a picture below which a crop is noted (half), the most shots one list may hold (120), the test tone's name, pitch and length, the cover still's JPEG quality, and the legal black-and-white and colour ranges of video. A second block, `# match:`, holds the touch-up's caps: brightness 8, blue or red 4, colour between 0.92 and 1.08, and how many decimals match writes. Those caps only ever nudge a clip.
- **A test guards them.** `tests/test_render_settings.py` fails if any of the 30 names in the two blocks loses its note, or if a number turns up in the blocks that nobody listed. A second test checks the numbers agree: the first and last pictures of 120 shots fit in 20 proof sheets in both sheet layouts, a frame holds a whole number of sound samples, the colour caps sit either side of 1, the move is a small part of the frame, and the loudness numbers are at or below zero.
- **Doctor checks more.** `python -m v2r doctor` now also reports the extra FFmpeg filters render builds with (such as `perspective` and `lutyuv`), the 32-bit float WAV sound encoder and decoder, three muxers (the writers of mp4, matroska and wav) and five demuxers (the readers of concat lists, matroska, wav, image sequences and mp4/mov). Each says "available" or "MISSING" in doctor's usual style. Here none are missing.
- **Render checks the same list first.** Right after it finds FFmpeg, and before it reads the cut list, render checks every piece it needs. If this computer's FFmpeg lacks one, render says so in one sentence, for example "This computer's FFmpeg lacks the nosuchfilter filter, so nothing was built.", and the work folder is left exactly as it was.
- **Normalize is unchanged.** It still checks exactly its own three lists, and does not check muxers or demuxers.

## What to look and listen for

Nothing to see or hear: no video or sound processing changed. On a phone, `python -m v2r doctor` should end with no line saying MISSING among the FFmpeg lines. If one does say MISSING, render will refuse there by name, which is the point.

## Task commits

| Task | Name | Commit |
|------|------|--------|
| 1 | every remaining Stage 16 number in settings.py with its unit, guarded by a test | f1e1a68 |
| 2 | doctor names every FFmpeg piece render uses; render refuses where one is missing | 085e103 |

## Performance

Full suite: 476 passed in 700 s (11 min 41 s), within the 1500 s bound. The plan's own targeted tests (doctor, tracer, normalize doctor tests) ran in 76 s.

## Deviations from Plan

None - plan executed as written. One note: each task's tests were written together with its code and committed in one commit per task (the plan is `type: execute`, not a plan-level TDD plan), so there is no separate RED commit.

### Auto-fixed Issues

None.

## Authentication gates

None.

## Known Stubs

None. The settings added here (for example `TEST_TONE_*`, `COVER_JPEG_QUALITY`, `MOVE_AMOUNT`) are read by plans 05 to 09, which own them; they are not wired to anything yet, by design.

## Threat Flags

None. Threats T-4-05 and T-4-03 are mitigated as planned: the piece check runs before check and before any scratch folder exists (the test compares the work folder's listing before and after, both shapes), and a test fails if any name in a RENDER_* list is missing from doctor's matching list.

## Self-Check: PASSED

- Files found: tests/test_render_settings.py, v2r/settings.py, v2r/doctor.py, v2r/render/__init__.py, tests/test_doctor.py, tests/test_render_tracer.py.
- Commits found: f1e1a68, 085e103 on stage-16-render.
- Full suite: 476 passed.
