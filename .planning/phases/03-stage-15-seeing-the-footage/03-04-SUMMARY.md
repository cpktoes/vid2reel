---
phase: 03-stage-15-seeing-the-footage
plan: "04"
subsystem: look
tags: [ffmpeg, deshake, scdet, blurdetect, ebur128, signalstats, look-json]

requires:
  - phase: 03-stage-15-seeing-the-footage
    provides: "plan 01's look command, the one measuring pass, parse_metadata, the frozen look.json names, the settings block; plan 02's doctor filter list"
provides:
  - "look.json half-second entries now carry movement, camera, shake, camera_state, subject, blur, sharp, brightness, loudness and shot_change"
  - "look.json clip entries now carry overall (brightness, brightness_low, brightness_high, blue_shift, red_shift, saturation) and shot_changes"
  - "measure.parse_motion, measure.measure_loudness, measure.SOUND_FILTERS, MEASURES with signalstats, blurdetect, scdet, deshake"
  - "the measured dict's frames[] (t, movement, cut, camera, shake, blur, brightness) and sound[] (t, loudness) for plans 06 and 07"
  - "tests/media.py make_look_clip: test clips with a known answer"
affects: [03-05, 03-06, 03-07, 03-08, stage-16, stage-17]

actuals:
  tokens: 9400
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "one picture pass (fps, scale, signalstats, blurdetect, scdet, deshake last, metadata print) plus one sound-only pass, both in a temporary folder with fixed plain file names"
    - "a missing filter removes only its own measurements (null) and adds one plain sentence; a missing common piece (fps, scale, metadata) removes all measurements"
    - "camera shift read from deshake's Ori columns and smoothed by look's own centred one-second average; Avg and Fin never used"

key-files:
  created:
    - tests/test_look_measure.py
  modified:
    - v2r/look/measure.py
    - tests/media.py

key-decisions:
  - "subject (something in the frame is moving) is judged only where camera_state is still; it is null while the camera pans or shakes or was not measured"
  - "The first analysed frame has no earlier frame, so its movement, camera and shake are null and it is left out of the half's means (a cut frame is treated the same)"
  - "sharp is judged against the clip's own half seconds (median plus BLUR_SPREADS spreads), never a fixed blur number"
  - "When a picture piece every measurement needs (fps, scale, metadata) is missing, nothing at all is measured, loudness included, and one sentence says so"
  - "If the picture pass fails for a clip, its loudness is not attempted; the clip gets the one note"

requirements-completed: [LOOK-03, LOOK-05, LOOK-06]

coverage:
  - id: D1
    description: "camera still with a moving square: camera and shake low, subject true only while the square moves"
    requirement: "LOOK-03"
    verification:
      - kind: unit
        ref: "tests/test_look_measure.py::test_camera_still_with_moving_square"
        status: pass
    human_judgment: false
  - id: D2
    description: "shaky camera reads shaky and never a subject; a steady pan reads panning and never shaky"
    requirement: "LOOK-03"
    verification:
      - kind: unit
        ref: "tests/test_look_measure.py::test_camera_shaky_jitter, test_camera_panning"
        status: pass
    human_judgment: false
  - id: D3
    description: "shot changes found at a cut, with the cut frame left out of the half's movement"
    requirement: "LOOK-03"
    verification:
      - kind: unit
        ref: "tests/test_look_measure.py::test_shot_change_at_cut"
        status: pass
    human_judgment: false
  - id: D4
    description: "sharpness relative to the clip, brightness, colour cast and saturation, flat picture gives null not zero"
    requirement: "LOOK-03"
    verification:
      - kind: unit
        ref: "tests/test_look_measure.py::test_sharpness_blurred_stretch, test_brightness_two_grey_levels, test_colour_cast, test_flat_picture_has_no_sharpness"
        status: pass
    human_judgment: false
  - id: D5
    description: "loudness per half second, null for silence and for sound normalize added"
    requirement: "LOOK-03"
    verification:
      - kind: unit
        ref: "tests/test_look_measure.py::test_loudness_beep, test_loudness_silent_track, test_loudness_skipped_when_sound_added"
        status: pass
    human_judgment: false
  - id: D6
    description: "a missing filter gives null for what it feeds, one plain sentence, other measurements and sheets intact, exit 0"
    requirement: "LOOK-05"
    verification:
      - kind: unit
        ref: "tests/test_look_measure.py -k missing_filter (10 tests)"
        status: pass
    human_judgment: false
  - id: D7
    description: "boundary and empty half-second rows of the parser"
    requirement: "LOOK-06"
    verification:
      - kind: unit
        ref: "tests/test_look_measure.py::test_summarise_boundary_frame, test_summarise_empty_half, test_finite_values"
        status: pass
    human_judgment: false
  - id: D8
    description: "the camera, subject and sharpness readings rank real handheld footage usefully (walking shots, fast pans)"
    verification: []
    human_judgment: true
    rationale: "tests use generated clips; whether the thresholds suit real phone footage is decided by the blind test (plan 08) and a run on a phone"

duration: 40min
completed: 2026-10-18
status: complete
---

# Phase 3 Plan 04: Camera, subject, sharpness, shot changes, colour and loudness Summary

**look.json now says, for every half second, whether the camera is still, panning or shaky, whether something in the frame is moving (only judged while the camera is still), how sharp and bright the picture is, how loud the sound is and whether the shot changed; and for each clip its overall brightness and colour cast.**

## Performance

- **Duration:** about 40 min
- **Tasks:** 3 (all TDD, no checkpoints)
- **Files modified:** 3 (1 created)
- **Full suite:** 283 passed

## What changed, in plain English

Before this plan, look.json only told how much of the picture changed and how bright it was. Now each half second of each clip also has these words and numbers. Open `work/look.json` after a `look` run and find clip A's `halves` list to see them.

- **camera_state** is one of three words. `still` means the phone was held steady. `panning` means it was moving smoothly (a slow sweep or a walk with a smooth glide). `shaky` means it was jittering. It is null if the camera could not be measured.
- **camera** and **shake** are the numbers behind that word: how far the picture slid between looks, and how much of that slide was jitter rather than a smooth movement. Low numbers are steady.
- **subject** is `true` when something in the frame is moving while the camera is still, `false` when nothing moves, and null when the camera is panning or shaky. This is on purpose: when the camera moves, everything in the picture moves, so we cannot tell a person walking from the phone swinging. Rather than guess and call camera motion "a subject", look says nothing there. (This is the fallback the earlier decision D-10 allowed for.)
- **movement** is how much the whole picture changes (0 is a frozen picture). A shot change is left out of it, so a cut does not look like action.
- **blur** and **sharp**: blur is the width of edges (lower is sharper). `sharp` is `false` for a half second noticeably blurrier than the rest of that same clip, and `true` otherwise. It is compared with the clip itself because real footage only differs 10 to 15 percent between sharp and blurred. A flat picture with no edges has null here, never 0.
- **brightness**: 16 is black, 235 is white.
- **loudness**: the loudest moment in that half second in LUFS. Around -14 is loud speech, quieter is a lower number such as -30, and **null means silence** (or a clip where the app added silence because the phone clip had none).
- **shot_change**: `true` in the half second where a new shot starts. The clip's `shot_changes` lists the seconds, such as `[3.4]` (empty list means none; null means it could not be measured).
- **overall** (one per clip, for Stage 16 to make clips look like one shoot): `brightness`, `brightness_low` and `brightness_high` (how dark the dark parts and how bright the bright parts are), `blue_shift` (above 0 leans blue, below 0 leans yellow), `red_shift` (above 0 leans red, below 0 leans green), and `saturation` (0 is grey, higher is more vivid colour).

If this computer's FFmpeg is missing a filter (the phone's chat may lack one), look prints one plain sentence naming it, repeats it in look.json's `missing` list, writes null for the numbers that filter would have given, and carries on: every other number and the contact sheets still come back and the command still succeeds.

**Where to see it working:** run `python3 -m v2r look` after a normalize, then open `work/look.json` and look at clip A's `halves`. Things to check on your own footage: a stretch where you held the phone steadily should read `still`, a deliberate slow sweep `panning`, and a handheld walk with bounce `shaky` (a very fast pan or a brisk walk may read `shaky` rather than `panning`; that is the known limit). Where someone speaks, `loudness` should be a number in those half seconds and null in the quiet ones.

**Phone test (needed before anything merges to main):** nothing about how a reel looks or sounds changed, because look only reads the working copies. But this is the first stage to use FFmpeg's `deshake`, `scdet`, `blurdetect` and `ebur128` in the sandbox's FFmpeg 6.1, which this Mac (8.0.1) could not run. Please run `look` from your phone on branch `stage-15-look` and open look.json: if the doctor report (plan 03) says any of those four filters is missing, the matching numbers will be null and look.json's `missing` will say so, which is the safe result. Note the starting thresholds (camera still below 1.5 px, shaky at 2.0 px, subject at movement 1.0, sharp within 3 spreads) come from generated clips and one real clip; the blind test (plan 08) sets their final values.

## Accomplishments

- One picture pass now measures movement, brightness, colour, sharpness, shot changes and camera movement (deshake last, since nothing uses its picture); one cheap sound pass measures loudness.
- Camera versus subject movement are three separate figures (movement, camera, shake) plus a camera word; subject is never judged while the camera moves.
- A missing filter is a null and a sentence, never a failed run; proved by taking each of deshake, ebur128, metadata, scdet and blurdetect away in turn, in both shapes.
- Test clips with a known answer (`make_look_clip`: plain, square, cut, jitter, pan, blur, grey, cast, beep) exercise every measurement in tall and wide.

## Task Commits

1. **Task 1: camera, shake, subject movement and shot changes** - `40d4a7a` (feat)
2. **Task 2: sharpness, brightness, exposure and colour balance** - `88d0f39` (feat)
   - follow-up fix to the test clips - `82122fe` (test)
3. **Task 3: loudness, missing-filter nulls, parser edge rows** - `1d673d2` (feat)

## Files Created/Modified

- `v2r/look/measure.py` - MEASURES grows blurdetect, scdet, deshake; `parse_motion`, `camera_and_shake`, `overall_of`, `measure_loudness`, `camera_state`; `summarise` produces every half-second value; `missing_measurements` names every filter
- `tests/media.py` - `make_look_clip`
- `tests/test_look_measure.py` - 37 tests over both shapes

## Decisions Made

See `key-decisions` above. None changes a rule in CLAUDE.md or differs from the guide; the D-10 fallback was already recorded in docs/decisions.md by plan 02.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Pan and jitter test clips gave unreliable camera readings**
- **Found during:** Tasks 1 and 2
- **Issue:** With the recipe's thin, half-transparent grid lines, deshake found no usable detail in the wide clips (camera read 0 during a pan), and after raising the encode quality the tall pan read as shaky: a hard-edged grid shrunk to a shimmer that does not move with the picture.
- **Fix:** grid lines scale with the clip width, are opaque white and black, and the detail picture gets a light blur (`gblur=sigma=1`). Readings are then steady in both shapes (tall pan camera 4.0 shake 0.0, wide pan camera 3.5 shake 0.5).
- **Files modified:** tests/media.py
- **Commits:** 40d4a7a, 82122fe

**2. [Rule 1 - Bug] A steady picture's sharpness drifted in the test clip**
- **Found during:** Task 2
- **Issue:** at the default encode quality the first seconds of a wide clip read about 5 percent blurrier than the rest, so the relative `sharp` test called them not sharp.
- **Fix:** test clips are encoded at `-crf 12`, after which blur is constant. No threshold in settings.py was changed.
- **Files modified:** tests/media.py
- **Commit:** 88d0f39

### Additions beyond the plan text

- The first analysed frame is treated like a cut frame: movement, camera and shake are null for it and it is left out of the half's means. Its frame difference and shift are 0 only because there is no earlier frame, which would otherwise pull the first half toward "still" (Rule 2, correctness).
- When fps, scale or metadata is missing, loudness is not measured either (the sentence says nothing could be measured), so "every measurement null" holds literally.
- Plural wording for two missing sound filters ("ebur128 and ametadata filters").

## Known Stubs

None. The stub recorded by plan 01 (`shot_changes` and `sound` placeholders) is resolved: both are measured now, and the ledger entry is marked fixed.

## Issues Encountered

- FFmpeg 6.1 (the phone's) could not be run here; the measurements ran on this Mac's 8.0.1. The doctor report from a phone (plan 03) settles whether the four new filters exist there; D-21 is the safety net.
- The full suite takes close to three minutes on this Mac (283 tests).

## Threat Flags

None. T-3-03 (list arguments, no shell, absolute input path, fixed text-file names, temporary folder as cwd), T-3-04 (a timeout on both FFmpeg calls, a timeout makes those values null with one note) and T-3-13 (every printed value goes through `finite()`) are in the code and tested.

## Next Phase Readiness

Plans 06 and 07 can read `frames[]` (t, movement, cut, camera, shake, blur, brightness) and `sound[]` (t, loudness) from `measure_clip`, and the half-second words above. Plan 05 (sheets and the look loop) shares no files with this one.

## Self-Check: PASSED

Commits 40d4a7a, 88d0f39, 82122fe and 1d673d2 exist; v2r/look/measure.py, tests/media.py and tests/test_look_measure.py exist; full suite 283 passed.
