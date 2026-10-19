---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 04
current_phase_name: stage-16-cut-list-and-renderer
status: executing
stopped_at: Completed 04-04-PLAN.md
last_updated: "2026-10-19T21:53:42.481Z"
last_activity: 2026-10-19
last_activity_desc: Phase 04 execution started
progress:
  total_phases: 3
  completed_phases: 2
  total_plans: 28
  completed_plans: 21
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-10-13)

**Core value:** A reel worth posting, made entirely from her phone.
**Current focus:** Phase 04 — stage-16-cut-list-and-renderer

## Current Position

Phase: 04 (stage-16-cut-list-and-renderer) — EXECUTING
Plan: 5 of 11
Status: Ready to execute
Last activity: 2026-10-19 — Phase 04 execution started

Progress: [████████░░] 75% (1 of 14 phases complete)

## Performance Metrics

**Velocity:**

- Total plans completed: 17
- Average duration: -
- Total execution time: 0.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Skeleton | done by hand | - | - |
| 2 | 8 | - | - |
| 3 | 9 | - | - |

**Recent Trend:**

- Last 5 plans: none yet
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 02 P01 | 25min | 3 tasks | 5 files |
| Phase 02 P02 | 10min | 2 tasks | 5 files |
| Phase 02 P04 | 15min | 2 tasks | 3 files |
| Phase 02 P05 | 25min | 2 tasks | 3 files |
| Phase 02 P03 | 5min | 2 tasks | 4 files |
| Phase 02 P06 | 25min | 2 tasks | 3 files |
| Phase 02 P07 | 40min | 3 tasks | 2 files |
| Phase 02 P08 | phone test | 3 tasks | 1 files |
| Phase 03 P01 | 7min | 3 tasks | 8 files |
| Phase 03 P02 | 6min | 2 tasks | 7 files |
| Phase 03 P04 | 40min | 3 tasks | 3 files |
| Phase 03 P05 | 25 min | 3 tasks | 4 files |
| Phase 3 P03 | one checkpoint round trip | 3 tasks | 0 files |
| Phase 03 P06 | 35 min | 2 tasks | 4 files |
| Phase 03 P07 | 30 min | 2 tasks | 3 files |
| Phase 03 P08 | one checkpoint round trip | 2 tasks | 0 files |
| Phase 03 P09 | 3 checkpoint round trips | 3 tasks | 4 files |
| Phase 04 P02 | 5min | 2 tasks | 4 files |
| Phase 04 P01 | about 1h (Task 2) | 2 tasks | 14 files |
| Phase 04 P03 | 25 min plus 11 min 40 s suite | 2 tasks | 6 files |
| Phase 4 P04 | 75min | 2 tasks | 4 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Settled decisions that shape later phases:

- [Phase 4 / Stage 16]: A wide clip in a tall reel is cropped to fill, centred on the subject; bars and blurred backgrounds read as mistakes
- [Phase 7 / Stage 19]: The chat asks a brief of three to five questions before editing; a good reel outranks a short conversation
- [Phase 11 / Stage 23]: Long videos are edited on a Mac from start to finish; a phone chat cannot hand back a file that size
- [Process]: GSD phases are named by guide stage, one per stage, never merged, split or reordered
- [Phase 2 / Stage 14]: HDR tone-mapping starts at hable with a peak of 203 nits (chosen 2026-10-13 from the research measurement, replacing D-12's mobius start); the user still confirms by eye from the four-panel strips in plan 02-07
- [Phase 2 / Stage 14]: Stage 14 plan 01: normalize manifest field names are frozen as documented in v2r/normalize.py (D-03)
- [Phase 2 / Stage 14]: Stage 14 plan 05: a file whose working name is taken by an original in the work folder is skipped, never overwritten
- [Phase 2 / Stage 14]: 02-03: pillow and pillow-heif approved by the user 2026-10-13; pillow-heif held on the 1.8 line (below 1.9)
- [Phase 2 / Stage 14]: 02-06: Pillow reads every file before ffprobe; FFmpeg only reads the upright JPEG copy of a photo, never the HEIC
- [Phase 2 / Stage 14]: Stage 14: HDR clips are tone-mapped with hable at a peak of 203 nits, picked by eye from four-panel strips
- [Phase 2 / Stage 14]: Phone attachments of slow-motion clips arrive pre-rendered at a steady 30 fps; the 120/240 fps flag does not fire from a phone
- [Phase 2 / Stage 14]: Handbook join step uses the working copies in letter order, leaving out skipped letters
- [Phase ?]: Phase 03-01: a still's orientation follows its working copy and a still of another orientation starts a new sheet; its label time is the working copy's own frame time
- [Phase ?]: Phase 03-01: if Pillow or a scalable font is missing, look still measures; stills get null sheet/cell/box and the sentence goes in look.json missing
- [Phase ?]: Plan 03-02: PySceneDetect checked and not added; shot changes come from FFmpeg's scdet; four Stage 15 differences from the guide recorded in docs/decisions.md
- [Phase ?]: 03-04: subject movement is judged only where the camera is still; null while panning, shaky or unmeasured
- [Phase ?]: 03-04: sharp is judged against the clip's own half seconds (median plus BLUR_SPREADS spreads), never a fixed number
- [Phase ?]: Plan 03-05: once the sheet cap is reached no later still is placed on a sheet, keeping letter order unbroken; thinning is skipped when no sheets can be made
- [Phase ?]: [Phase 3] Plan 03: user allowed the push; stage-15-look pushed at 22b6ceb, main unchanged; phone FFmpeg 6.1.1-3ubuntu5 has all eight look filters
- [Phase ?]: [Phase 3] Plan 06: a flat-topped peak counts once, and a movement still sits half an analysed frame before the frames' times; short clips under 3 s get no extras
- [Phase ?]: [03-07] Candidates are facts in a stated order; a still exactly at a stretch's end counts as inside it; unmeasured parts are named as not measured
- [Phase ?]: [03-08] Blind test on the user's own footage passed 4 of 4 on four clips (user's choice of set size); no misses, no setting changes; look costs about 0.5 to 0.57 s per second of video on the Mac
- [Phase ?]: [03-08] Observation for a later stage: two normalize runs at once make the second run's clean-up delete the first run's half-written file; a run-in-progress guard or a plainer sentence is wanted, not a Stage 15 fix
- [Phase ?]: [Phase 3] Stage 15 phone test: look step taken from the offered draft (step 4 of EDITOR.md) at the user's word; branch pushed, main untouched at 248bec0
- [Phase ?]: [Phase 3] DESHAKE_CONTRAST set to 20 (deshake default 125 read a panning camera as still on small tone-mapped frames); confirmed on Mac, bench clips and phone
- [Phase ?]: [Phase 3] Handheld pan reads shaky not panning (SHAKE_LIMIT_PX 2.0): left alone, candidate for a later tuning pass
- [Phase 04]: 04-01: frames(s) = floor(round(s x 30, 6) + 0.5); whole clips use a thousandth-of-a-frame benefit
- [Phase 04]: 04-01: check runs canvas, clips block, segments, fit in order, each only if earlier ones found nothing; one sentence per clip in the clips block
- [Phase ?]: 04-03: missing_ffmpeg_features with no list named checks all five of doctor's lists; naming any encoder/filter/decoder list means unnamed muxers/demuxers are none, so normalize is unchanged
- [Phase ?]: 04-03: render's FFmpeg piece check runs right after the FFmpeg-present check and before check, building and touching nothing
- [Phase ?]: 04-04: clips and look.touch_up are objects keyed by letter; why is required and non-empty; when the rulebook finds a problem the work-folder rules wait and one note says so

### Pending Todos

None yet.

### Blockers/Concerns

None.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 261014-rvv | Stage 14 review follow-ups: safe handbook recipe, proportional FFmpeg timeout, IN-01 and IN-05 | 2026-10-14 | 0d3f8e2 | [261014-rvv-stage-14-review-follow-ups-safe-handbook](./quick/261014-rvv-stage-14-review-follow-ups-safe-handbook/) |
| 2 | Record the Stage 14 phone test of 2026-10-14 in docs/phone-limits.md | 2026-10-15 | 8e1fd6f | — |
| 3 | Record the Stage 15 sampling decision (one still a second plus extras at movement peaks and scene changes) in CLAUDE.md, docs/decisions.md and the guide's seventeenth edition | 2026-10-17 | 7e81d4f | — |
| 4 | Bring the guide's Stage 14 level with the build and publish the eighteenth edition; record in docs/decisions.md that both editions were made from Claude Code | 2026-10-17 | 048423e | — |
| 5 | Record the Stage 15 phone tests in docs/phone-limits.md and settle the Stage 15 wording in CLAUDE.md and docs/decisions.md | 2026-10-18 | 6577548 | — |
| 6 | Bring the guide's Stage 15 level with the build and publish the nineteenth edition; record it in docs/decisions.md | 2026-10-18 | 4bdbd92 | — |
| 7 | Apply the nine Stage 15 review decisions (WR-01, WR-02, WR-04, IN-02 to IN-07) on branch stage-15-review-fixes | 2026-10-18 | fc40d90 | [261018-wu5-apply-the-nine-stage-15-review-decisions](./quick/261018-wu5-apply-the-nine-stage-15-review-decisions/) |

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none)* | | | |

## Session Continuity

Last session: 2026-10-19T21:53:42.455Z
Stopped at: Completed 04-04-PLAN.md
Resume file: None
