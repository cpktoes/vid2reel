---
phase: 02-stage-14-normalize
plan: "07"
subsystem: normalize
tags: [hdr, tonemap, hable, real-footage-check, timing-table, decisions]

requires:
  - phase: 02-stage-14-normalize
    provides: plans 01 to 06 (normalize for videos and photos, HDR tone-map settings TONEMAP and TONEMAP_NPL)
provides:
  - "Every sample fixture normalized on the Mac in both shapes (tall and wide), with the guide's before-and-after timing table"
  - "A four-panel HDR strip for each HDR sample clip (15 strips), and the user's by-eye pick: hable at 203"
  - "settings.TONEMAP = hable and settings.TONEMAP_NPL = 203, confirmed and recorded in docs/decisions.md"
affects: [02-08, stage-15, stage-16]

actuals:
  tokens: 1500
  tasks: 3
  commits: 1

key-files:
  created: []
  modified: [v2r/settings.py, docs/decisions.md]

key-decisions:
  - "HDR clips are tone-mapped with hable at a peak of 203 nits, picked by eye from four-panel strips"

requirements-completed: [NORM-02]

duration: 40min
completed: 2026-10-13
status: complete
---

# Phase 2 Plan 07: Real footage check and tone-map pick Summary

Normalize was run on all five sample sets in both shapes on the Mac, the guide's timing table was built, and the user chose hable at 203 by eye from four-panel strips, so the tone-map settings stay as they were and are now recorded as a decision.

## In plain English

This plan was the first time normalize met her real footage. Every clip and photo converted, in tall and in wide, with nothing skipped. All of her videos are the iPhone's HDR kind, which looks washed out or too bright if converted carelessly. For each of them I made a strip of four stills from the middle of the clip: one with no correction, and three with different ways of correcting the colour. The user looked at the strips and picked "hable", the one research had already expected to be closest to what the iPhone itself shows. She reported nothing wrong with the working copies (nothing sideways, no sound problems, no drifting sound, no odd colour). So the setting in `v2r/settings.py` keeps the same two numbers, and only its comment changed to say the choice was made by eye on 2026-10-13. A dated line in `docs/decisions.md` records it.

## What was done

**Task 1 (Mac run, table, strips; nothing committed, all under the git-ignored work/ folder).**
- 5 sample sets, 22 files per shape (15 videos, 7 photos). In both tall and wide: 22 done, 0 skipped. All 10 manifests finished.
- 436.5 seconds of video in total. Converting took 407.2 s in tall (0.93 of the footage length) and 490.0 s in wide (1.12 of the footage length).
- Slowest clip per second: set 3 A, a 4K clip, 44.5 s to convert 31.3 s of video in tall. Longest clip: set 4 B (205 s of video) took 162 s in tall.
- Timing rows, per shape:

| Kind of clip | Clips | Footage | Tall time | Wide time |
|---|---|---|---|---|
| upright, 30 fps or less | 1 | 10.7 s | 10.6 s | 12.5 s |
| upright, above 30 fps | 0 | none | none | none |
| sideways, 30 fps or less | 14 | 425.8 s | 396.6 s | 477.5 s |
| sideways, above 30 fps | 0 | none | none | none |

  The above-30-fps sideways row is present in the table for both shapes but has no data: none of the sample clips is both sideways and above 30 fps, so the question of whether autorotate makes those slow is still open for the phone test.
- Rotations seen in the sample clips: -90 (most), +90 (set 4 A), -180 (set 4 B), 0 (set 4 C).
- Every video is HLG with a Dolby Vision layer, so 15 four-panel strips were made, one per video, at each clip's middle second.
- The clip the user thinks of as slow motion (set 3 B) arrived already rendered at a steady 30 fps, so normalize correctly reports it as not slow motion (research assumption A5). The phone test in plan 08 checks a fresh slow-mo file straight from the camera.

**Task 2 (decision checkpoint).** The user looked at the strips and replied "hable". No problems were reported in the working copies, so there is nothing for verification or gap closure to pick up from this plan.

**Task 3 (commit f1a950a).** `TONEMAP = "hable"` and `TONEMAP_NPL = 203` stay as they were; only the comment above them changed, saying the pair was picked by eye from the four-panel strips on 2026-10-13. One dated line was added to `docs/decisions.md`. The full suite passes with it: 130 passed.

## Deviations from Plan

None - plan executed exactly as written. Because the choice was hable, the settings values did not change; only the comment did, as the plan allows.

## Test from a phone

This plan changed no video-processing code, only a comment and a decision line, so it does not by itself need a phone test. The by-eye pick does carry over to the phone test in plan 08. When you make the reel from a phone, check any clip shot in HDR (nearly all of the iPhone's own videos): look at about 0:02 and confirm the colours are natural and the skin and sky are not washed out or glaring bright, and that it looks like what the Photos app shows for the same clip.

## Known Stubs

None.

## Threat Flags

None. T-2-09 (nothing from fixtures/ or work/ committed; this summary uses set numbers and letters only) and T-2-08 (fixtures only used as inputs, never written to) both held.

## Commits

- f1a950a: feat(02-07) record the tone-map pick, hable at 203, chosen by eye

## Self-Check: PASSED
