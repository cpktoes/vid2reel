---
phase: 03-stage-15-seeing-the-footage
plan: "08"
subsystem: look
tags: [blind-test, human-check, timing, look-07]
status: complete

requires:
  - phase: 03-stage-15-seeing-the-footage
    provides: "plans 01 to 07: sheets with a still every second, extra stills, half-second measurements, candidate moments in look.json"
provides:
  - "LOOK-07 passed by a person: the blind test on the user's own footage, 4 of 4 clips approved"
  - "Mac timing for look: about 0.5 to 0.57 s of work per second of video"
  - "An observation about two normalize runs started at once, for a later stage"
affects: [03-09, stage-16]

actuals:
  tokens: 0
  tasks: 2
  commits: 0

tech-stack:
  added: []
  patterns:
    - "The judge for a look change is a person with the sheets and look.json, in a cleared Claude Code session; no repo file changes in a judging plan"

key-files:
  created: []
  modified: []

key-decisions:
  - "The user chose a fixture set of four clips instead of five; the blind test was run on all four and all four passed, so LOOK-07 is recorded as 4 of 4"
  - "No setting changes: there were no misses, so no gap closure is needed before plan 09's phone test"

requirements-completed: [LOOK-07]

duration: one checkpoint round trip
completed: 2026-10-18
---

# Phase 3 Plan 08: The judge Summary

**look passed its blind test on the user's own footage: from the sheets and look.json alone, Claude's description of every one of four clips read as a good description, with no big misses, and look took about half a second of work per second of video on the Mac.**

## What changed, in plain English

Nothing about how a reel looks or sounds changed in this plan, and no file in the repo changed. This plan was the judge for everything built in plans 01 to 07.

First, Claude made a demo from generated test clips (never real footage) in a folder that git ignores, so the sheets and look.json could be seen before the real run. Then the user ran normalize and look on a set of their own clips on the Mac, opened the sheets in Finder, and ran the blind test: in a cleared Claude Code session, with the guide's prompt, Claude saw only the sheets and look.json for each clip, said what happens and which two seconds it would use, and the user compared that with the clip.

Result: the user could say, from each sheet alone, what happens in the clip, and every label was readable. In the blind test on all four clips the user said they "all read well as good descriptions of the clips". The user saw nothing that was a big miss. The count is 4 of 4 approved.

The pass rule in the plan is at least four clips out of five. The user's set had four clips, not five. That was the user's decision and the set they wanted to use. All four passed, which is the same as the pass rule's rate; this is recorded plainly as 4 of 4 on four clips, not as 4 of 5.

What happens next: on to plan 09, the phone test. Because there were no misses, no setting needs changing first, and the reel log needed no entries.

## Performance

- **Duration:** one checkpoint round trip (the user's run was their own hour, not timed here)
- **Completed:** 2026-10-18
- **Tasks:** 2 of 2
- **Files modified:** 0 in the repo (work/check-look/ and the user's bench are git-ignored)

## Timing

**Task 1, generated clips on the Mac (work/check-look/):** three generated clips, 50 s of video in all (a 30 s tall clip, a 12 s tall clip with a cut, an 8 s wide clip with a pan).

| What | Result |
| ---- | ------ |
| look, total | 28.4 s |
| Seconds of look per second of video | about 0.57 |
| Sheets | 5 |
| Extra stills on the 30 s clip | at 12.5 s (the quick moment) and 20.4 s (the beep) |
| Extra still on the clip with a cut | at 7.5 s (the shot change) |
| Full test suite | 347 passed in 12 minutes |
| doctor | no MISSING line |
| Sheet 02 | read clearly |

**Task 2, the user's own set, normalize then look on the Mac (8 processors):** four HDR iPhone clips, 59.7 s of footage, normalized tall.

| Clip | Length | normalize | look |
| ---- | ------ | --------- | ---- |
| A | 38.6 s | 68 s | 19 s |
| B | 6.5 s | 9 s | 3 s |
| C | 10.2 s | 12 s | 4 s |
| D | 4.4 s | 5 s | 4 s |
| All four | 59.7 s | 96 s | 31 s |

look took about 0.5 s of work per second of video, a little under the 0.6 measured when the sampling was decided (D-12). The phone's sandbox has two processors, so expect it to be slower there; plan 09 measures that.

What look produced for the user's set: 6 sheets; rhythm 1.0 (the sheets were not thinned); `missing: []`.

| Clip | Stills | Extra stills | Candidates |
| ---- | ------ | ------------ | ---------- |
| A | 40 | one, for a sound, at 35.3 | two: 16.5 to 20.5 and 35.0 to 38.5, both "steady camera, sharp, subject moving" |
| B | 7 | none | none (every window was ruled out) |
| C | 11 | none | two, both "camera panning, sharp" |
| D | 6 | one, for a sound, at 03.5 | none |

## Finder check and blind test

- **Finder check (from this sheet alone, could I say what happens?):** yes, for each sheet; every label was readable.
- **Blind test, all four clips, guide's prompt in a separate Claude Code session:** "these all read well as good descriptions of the clips".
- **Misses:** none ("I didn't see anything that was a big miss"). So there is no miss to pair with a setting (PEAK_SPREADS, SCENE_THRESHOLD, CANDIDATE_MAX_SECONDS and the others in the plan's list were not implicated), and nothing was written to the reel log.
- **Count:** 4 of 4 approved, on four clips. Pass.

## Accomplishments

- Suite, doctor and a look run over generated clips all green on the Mac before the real run, with the quick moment, the beep and the cut each getting an extra still where the plan expected.
- The user's own footage passed the Finder check and the blind test with no misses, which settles LOOK-07 by the only judge that can settle it.
- The Mac cost of look is recorded: about 0.5 to 0.57 s per second of video.

## Task Commits

1. **Task 1: check folder of generated clips, Mac timing, full suite** - no commit (writes only to the ignored work/check-look/)
2. **Task 2: the user's run, Finder check and blind test** - no commit (the user's own steps)

**Plan metadata:** committed with this summary (docs: complete the judge plan).

## Files Created/Modified

None in the repo. `git status` shows nothing under work/ or fixtures/ and no tracked file changed.

## Decisions Made

- Four clips were used instead of five, at the user's choice. The pass was recorded as 4 of 4 and flagged as such. If the user wants the full five-clip test later, it can be run again at any time with the same prompt.
- No settings were changed.

## Deviations from Plan

None in the work itself. The plan expected a set of at least five clips with one quick moment; the user chose a set of four, which is a decision of theirs and is recorded above rather than treated as a failure.

## Issues Encountered

**Two normalize runs at once (observation for a later stage, not a Stage 15 fix).** The user's first attempt at step 2 failed because two normalize runs were started while one was still going. The second run's clean-up deleted the first run's half-written B.part.mp4, and the first run then reported "could not be converted" with FFmpeg's "Unable to re-open ... B.part.mp4 output file for shifting data ... No such file or directory". The orchestrator re-ran normalize alone and all four converted. Nothing was lost (originals are never touched), but the sentence the user saw does not say "another run is still going". A later stage could add a guard that refuses to start while a run is in progress, or say it in plain words. This is not a look change and nothing was changed here.

## Threat Flags

None - no new attack surface. T-3-05 and T-3-06 held: nothing was read from fixtures/, only work/check-look/ was written by Claude, and this summary names no clip, set, person or account.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 09, the phone test, is next. look is judged good enough on real footage on the Mac; the open question is the phone's own speed (two processors, FFmpeg 6.1) and the 2-minute command limit.
- Nothing merges into main until a reel has been made from a phone on this branch.

---
*Phase: 03-stage-15-seeing-the-footage*
*Completed: 2026-10-18*
