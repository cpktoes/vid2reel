---
phase: 03-stage-15-seeing-the-footage
plan: "06"
subsystem: look
tags: [extra-stills, peaks, shot-change, movement, loudness, known-answer-tests]
status: complete

requires:
  - phase: 03-stage-15-seeing-the-footage
    provides: "plan 04's measured names (frames, sound, halves, shot_changes); plan 05's run rhythm and sheet cap, which already count every clip's full extras allowance; plan 03's phone doctor report (all eight look filters present)"
provides:
  - "pick.spread, pick.peaks, pick.extra_times (plus the helpers movement_time and sound_time): extra-still times as pure functions"
  - "look() adds each video's extras to its base stills before the one FFmpeg pull; look.json stills carry why 'shot change', 'movement' or 'sound' beside 'rhythm'"
  - "tests/media.py: white_share and make_bursts_clip"
  - "tests/test_look_extras.py: 9 pure tests and 6 through-look tests (each over tall and wide)"
affects: [03-07, 03-08]

actuals:
  tokens: 5500
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "gap and cap are compared in whole frames of the working copy, never in floating-point seconds"
    - "a peak is judged against the clip's own median and spread, with a floor on the spread so calm clips make no peaks"

key-files:
  created:
    - tests/test_look_extras.py
  modified:
    - v2r/look/pick.py
    - v2r/look/__init__.py
    - tests/media.py

key-decisions:
  - "A flat-topped peak (two equal neighbouring half seconds) counts once, at the first of them, so one event never earns two extras"
  - "A movement still is placed half an analysed frame before the frames' own times, because a frame's movement is the change since the frame before it"
  - "Extras are returned with the time of a real frame of the clip, so the label on the sheet is the time of the picture shown"

requirements-completed: [LOOK-02, LOOK-06]

duration: 35 min
completed: 2026-10-18
---

# Phase 3 Plan 06: Extra stills where something happened Summary

**Besides the once-a-second stills, look now adds a still at each new shot, at each burst of movement while the camera is still, and at each loud moment, capped at a third more than the ordinary stills and proved on clips with a known answer in both shapes.**

## What changed, in plain English

An extra still is a picture taken at the exact moment a measurement says something happened, between two of the ordinary once-a-second pictures. A splash or a jump that lasts a third of a second can fall between two once-a-second pictures; the extras exist to catch it.

How to spot one on a sheet: its label is not a whole second. A sheet cell labelled "A 04.6" sits between "A 04.0" and "A 05.0", so it is an extra. look.json says why for every still: "rhythm" (ordinary), "shot change" (a new shot starts just before it), "movement" (something moved while the camera was still) or "sound" (a loud moment, such as a laugh or a clap).

Rules you can check:
- **At most one extra for every three ordinary stills.** A 30-second clip (30 ordinary stills) gets at most 10; an 8-second clip at most 2. When more things happen than fit, new shots win first, then the strongest bursts and loudest moments.
- **Clips shorter than 3 seconds get no extras at all** (fewer than 3 ordinary stills means a limit of zero). A photo gets its one still and nothing else. This is the one flagged choice for the blind test: if short clips lose a quick moment, that is D-17 to revisit, not a setting.
- **Camera bumps and pans never earn a movement still.** Movement is only looked for in half seconds where the camera is still, so a wobble of the phone is not mistaken for something happening. If the camera could not be measured, every half second is looked at.
- **A calm clip or a silent still clip gets no extras.** A peak has to stand well above the clip's own usual level.
- **Never crowded:** an extra is at least 0.3 seconds (9 frames at 30 per second) from any other still.

Where to see it working: run `look` on a clip with a short event in it and open `work/sheets/sheet-01.jpg`; the in-between label ("A 04.6") is the extra, and its entry in `work/look.json` says why. The tests do exactly this on made-up clips: a white square visible only from 4.2 to 4.8 seconds (no ordinary still falls in that window) gets a movement still inside it whose picture holds visibly more white than the ordinary 4.0 still, a cut at 3.4 seconds gets a "shot change" still at 3.5, a beep at 3.4 to 3.6 gets a "sound" still at 3.4, and five quick bursts in an 8-second clip get exactly 2 extras, each inside a burst.

Which extras would not appear on the phone if a filter were missing: none. The phone's doctor report (plan 03) showed FFmpeg 6.1.1 has all eight look filters, so shot-change, movement and sound extras are all expected there. For the record: without `scdet` there would be no shot-change extras, without `deshake` movement would be looked for in every half second (camera not measured), and without `ebur128` or `ametadata` there would be no sound extras; no code change is needed for any of these (D-21).

What to look at on the phone test (after plan 07/08 puts it in a chat): make a look on a clip with a quick event and check that a sheet cell labelled between two whole seconds shows the event. No change to how a reel looks or sounds; this only adds pictures to the sheets Claude reads.

## Tasks

1. **Task 1 (a2065cc)**: `spread`, `peaks`, `extra_times` and helpers in v2r/look/pick.py; nine hand-made-number tests (peaks rule, gap in frames, cap and order, still-camera only, burst centre, loudest reading, lone beep, nothing happening, short clip).
2. **Task 2 (1dd94b6)**: look() merges base and extra stills in time order into the one pull; `white_share` and `make_bursts_clip` in tests/media.py; six through-look tests over tall and wide. Full suite: 326 passed in 8 minutes.

## Deviations from Plan

**1. [Rule 1 - Bug] Movement still placed half a frame early**
- **Found during:** Task 2, reading the extras the bursts clip produced
- **Issue:** a frame's movement is the change since the frame before it, so weighting by the frames' own times put the still about 0.05 to 0.1 s late; for a 0.3 s burst the first run landed at 1.67 s, after the square had left (burst 1.35 to 1.65).
- **Fix:** `movement_time` places each frame half an analysed frame earlier (0.5 / LOOK_FPS). The bursts now give 1.60 and 2.53, inside their bursts, and the cap test asserts that each extra lands in a burst.
- **Files modified:** v2r/look/pick.py, tests/test_look_extras.py
- **Commit:** 1dd94b6

**2. [Rule 1 - Bug] Flat-topped peak counted twice**
- **Found during:** Task 1, writing `peaks`
- **Issue:** the plan's "at least as large as each neighbour" makes two equal neighbouring half seconds both peaks, which could give one event two extras.
- **Fix:** a peak must be strictly above its earlier neighbour, so a flat top is one peak, at its first half second. All behaviours in the plan's behaviour list still hold.
- **Files modified:** v2r/look/pick.py
- **Commit:** a2065cc

**3. Test-only corrections (no code deviation):** several first-draft hand-made tests assumed a mid-half-second still could sit near a whole second; with a 9-frame gap it cannot (a half second's middle is at most 7.5 frames from a base still at a 1 s rhythm), so those tests use a 2 s rhythm. TDD was done as one test-plus-implementation commit per task rather than separate red and green commits.

## Known Stubs

None.

## Threat Flags

None. T-3-04 (extras capped at a third of the base stills) and T-3-17 (every frame number clamped by `frame_number`) are implemented as planned.

## Flagged for the blind test

- Clips under 3 seconds get no extras (D-17 cap of zero); the blind test shows whether short clips need another rule.
- PEAK_SPREADS 3 and the two spread floors are starting points; too few or too many extras point at these settings first, one at a time.
- The loudest sound reading in the test lands at 3.4 for a beep centred at 3.5 (loudness readings lag), inside the plan's 0.3 s tolerance.

## Self-Check: PASSED

- FOUND: v2r/look/pick.py (def extra_times, def peaks, def spread), v2r/look/__init__.py (pick.extra_times), tests/media.py (def white_share, def make_bursts_clip), tests/test_look_extras.py
- FOUND commits: a2065cc, 1dd94b6
- Full suite: 326 passed
