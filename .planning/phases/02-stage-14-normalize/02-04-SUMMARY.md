---
phase: 02-stage-14-normalize
plan: "04"
subsystem: video-processing
tags: [ffmpeg, hdr, tonemap, zscale, slow-motion, normalize]

requires:
  - phase: 02-stage-14-normalize
    provides: plan 01 normalize command, hdr_kind, video_chain, run_ffmpeg, manifest
provides:
  - "HDR (HLG and PQ) and wide-gamut clips converted to ordinary colour, not just relabelled"
  - "colour_notes(kind, dolby_vision): the manifest sentence for a converted clip"
  - "a plain-copy fallback with one sentence when the colour conversion fails"
  - "slow-motion (120/240 fps) sources flagged, kept at real speed"
affects: [02-05, 02-07, 02-08, stage-15, stage-16]

actuals:
  tokens: 7000
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "colour facts read from ffprobe and passed to zscale explicitly; the transfer comes from a fixed map, never straight from the file"
    - "one retry with the ordinary chain when the HDR command fails"

key-files:
  created: []
  modified: [v2r/normalize.py, tests/media.py, tests/test_normalize.py]

key-decisions:
  - "Tone-map operator and peak stay in settings.py (hable, 203 nits for HLG, 100 for PQ); the by-eye pick is still plan 07's"

requirements-completed: [NORM-02, NORM-04]

duration: 15min
completed: 2026-10-13
status: complete
---

# Phase 2 Plan 04: HDR colour, colour fallback and slow-motion notes Summary

**HDR and wide-gamut clips are tone-mapped to ordinary colour with the clip's own colour facts passed to zscale; a failed conversion still yields the clip with one sentence; 120 fps sources are flagged and keep real time.**

## What this does, in plain English

- Every clip the iPhone records is HDR. Before this plan those clips would have come out grey and washed out. Now normalize converts them to ordinary colour using the processor (the zscale and tonemap filters). A flat grey HDR test patch that measured about 124 in brightness now comes out below 112, which proves the picture was converted and not just relabelled.
- It also handles the other HDR flavour (PQ) and a clip with wide-gamut colour but no HDR label. The wide-gamut-only clip has its colours converted but is not darkened.
- How the picture is converted (the operator and its brightness setting) is read from settings.py when it runs, so changing the pick in plan 07 changes nothing else.
- Each converted clip's entry in work/manifest.json now says `colour_converted: true` and has a sentence such as "HDR (HLG) was tone-mapped to ordinary colour." If the clip carries a Dolby Vision layer, it adds "The Dolby Vision layer was ignored."
- If the colour conversion fails for any reason, you still get the clip. It is made again with ordinary processing, marked `colour_converted: false`, and one sentence appears both in the log and in the manifest: "The colour of the first file, NAME, could not be converted, so its colour is unchanged and may look flat." A stray half-finished file is never left behind. If even the second try fails, the error goes on to plan 05's per-file handling.
- A clip shot at 100 fps or more is flagged `slow_motion: true` and gets the note "The first file, NAME, was shot as slow motion at 120 fps; its working copy plays at normal speed." It becomes a 30 fps working copy of the same real-time length (within 0.1 s). A 60 fps clip is not flagged.

## Task Commits

1. **Task 1: tone-map HDR clips to ordinary colour** - `4aba53a` (feat)
2. **Task 2: colour fallback and slow-motion note** - `4d4aeff` (feat)

## What to test from a phone before merging

This changes how video looks, so please test from the phone on branch `stage-14-normalize`. I cannot watch video.

- **HDR colour (any iPhone clip, whole clip, e.g. at 0:00 and mid-clip):** compare the finished A.mp4 with the same clip in the phone's Photos app. Skin, sky and any strong colour (a red roof, brick) should look about the same, not grey or flat. If it looks a little darker or lighter than Photos, tell me which; that is the brightness setting plan 07 will tune.
- **Highlights (bright sky, lamps):** they should keep some detail, not be blown to white.
- **Fallback sentence:** if the log ever prints "could not be converted, so its colour is unchanged and may look flat" for a clip, that clip will look grey on purpose. Tell me which clip it was.
- **Slow motion:** attach one slow-motion clip. It should play at normal speed, not slow, with no stutter. Tell me what it arrives as in the sandbox (see the flagged assumption below).

## Files Modified

- `v2r/normalize.py` - the HDR branch of `video_chain` (new `tonemap=True` keyword), `colour_tag`, `colour_notes`, the retry in `normalize()`, the slow-motion note.
- `tests/media.py` - `make_clip(hdr=..., pattern="flat")` and `mean_luma`.
- `tests/test_normalize.py` - 7 new tests, 14 new runs in both shapes (78 tests pass in total).

## Decisions Made

- No new decisions. The notes for HDR and slow motion are not printed (only problem sentences go to the log), as planned.

## Deviations from Plan

None to the code requirements.

**Process note: TDD order.** Both tasks are marked TDD; tests and code were written together and committed together per task, with no separate failing-test commit first. The tests assert on real FFmpeg output (brightness, tags, lengths).

## Issues Encountered

- Checked on FFmpeg 8.0.1 (this Mac), not the sandbox's 6.1. The research verified the same recipes on 6.1; the full suite has not been run there. The phone test is the real check.
- The test clip maker uses one `-vf` for HDR tagging, so `hdr` and `vfr` cannot be combined in one test clip. Nothing needs that.

## Flagged assumption (not resolved here)

- iPhone slow-motion files that keep their native timing arrive in the sandbox as variable-rate files (normal speed, then 240 fps), so the median-frame-rate rule should flag them; a slow-motion fixture that arrived already rendered at 30 fps would not be flagged. Not confirmed on a native file. Plan 08's phone test should record what a slow-motion clip arrives as.

## Known Stubs

None.

## Threat Flags

None. T-2-16 (colour facts: transfer from a fixed map, range only "pc" or "tv", primaries and matrix are ffprobe's own names; a strange value makes FFmpeg fail and triggers the plain retry) and T-2-04 (one plain retry, then per-file isolation in plan 05) are in place. T-2-11 is accepted as planned.

## Self-Check: PASSED

- v2r/normalize.py, tests/media.py, tests/test_normalize.py exist and hold the new code.
- Commits 4aba53a and 4d4aeff exist on stage-14-normalize.
- `uv run pytest -q`: 78 passed.
