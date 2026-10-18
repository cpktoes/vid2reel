---
phase: 03-stage-15-seeing-the-footage
plan: "07"
subsystem: look
tags: [candidates, ranking, reasons, facts-only, d-04, known-answer-tests]
status: complete

requires:
  - phase: 03-stage-15-seeing-the-footage
    provides: "plan 04's half-second rows (movement, camera_state, subject, sharp, loudness) and shot_changes; plan 06's stills list and the sound rule in extra_times"
provides:
  - "pick.windows, pick.candidates, pick.sound_peak_times (and pick.sound_peaks, the shared sound rule): candidate moments as pure functions"
  - "look.json: every done clip has `candidates` (rank, start, end, reason, stills); an empty list for photos; no key for skipped clips"
  - "tests/test_look_candidates.py: 7 pure tests and 7 through-look tests (each over tall and wide)"
affects: [03-08, stage-16, stage-17]

actuals:
  tokens: 9500
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "look ranks facts in a stated order and never chooses: no selected field, reasons built only from fixed phrases, numbers and code-made still labels"
    - "the sound-peak rule lives in one function used by both the extra stills and the candidate reasons, so they always agree"

key-files:
  created:
    - tests/test_look_candidates.py
  modified:
    - v2r/look/pick.py
    - v2r/look/__init__.py

key-decisions:
  - "A still exactly at a stretch's end counts as inside it (the plan's [start, end]), so a stretch ending at 6.0 lists the 06.0 still"
  - "A stretch merges windows of the same tier whose movement is alike to the seed window's, so its edges can include a quieter half second; the reason is built from the whole merged stretch"
  - "When nothing was measured for a part of a reason, the reason says so ('sharpness not measured', 'movement not measured') instead of claiming a fact"

requirements-completed: [LOOK-04, LOOK-06]

duration: 30 min
completed: 2026-10-18
---

# Phase 3 Plan 07: Candidate moments Summary

**Each video clip in look.json now lists up to five stretches that are steady and sharp, in a stated order (steady camera, then movement, then earlier), each with a facts-only reason and the stills it rests on; nothing in the output says which one to use.**

## What changed, in plain English

A candidate moment is a stretch of a clip, two to four seconds long, that look found steady and sharp, written down with the facts that describe it. look does not say "use this one". It lists the stretches in a fixed order and leaves the choosing to the chat's Claude, which follows the handbook.

Where to find them: after `look` runs, open `work/look.json`; each clip has a `candidates` list. A made-up clip with a white square crossing the picture between 4.0 and 5.0 seconds gave this first entry:

`3.0 to 6.0: steady camera, sharp, subject moving; stills A 03.0, A 04.0, A 04.5, A 05.0, A 06.0`

and then two quiet stretches, `0.0 to 3.0` and `6.0 to 8.0`, each saying "steady camera, sharp, nothing moving". The words in a reason are always facts: the camera (steady, panning, or not measured), the picture (sharp), what moved (subject moving, nothing moving, some movement), any sound peak in the stretch ("sound peak at 04.5") and then the labels of the stills inside it, so every claim can be checked against a picture on the sheets.

The order, and why rank 1 is not a verdict:
- A steady camera ranks above a panning camera, even if the panning one has more going on. A panning camera is named as "camera panning" and a camera that could not be measured as "camera not measured".
- Within the same kind of camera, more movement comes first; equal movement goes to the earlier time.
- Stretches that run together and are alike are joined into one stretch, at most 4 seconds long, and stretches never overlap. A clip lists at most 5.
- A stretch with a shaky camera, a blurred picture or a cut inside it is never listed. A cut exactly at the start or end of a stretch is allowed. A clip where every stretch is shaky, blurred or cut gets an empty list.
- A photo has an empty list. A clip with nothing moving still gets its steadiest, sharpest stretches.
- No reason uses a word that judges or chooses (best, use, pick, choose, chosen, recommend, should, good, great), and look.json has no field that marks anything as selected. Tests fail if either appears. The module's description says in words that the order is not a choice.

What to look at on the phone test: nothing in how a reel looks or sounds changes; this only adds facts to look.json. When the chat's Claude is asked which two seconds of a clip and why, its answer should cite stills by label (such as A 04.5) taken from a candidate's list, and the stretch it names should not be shaky, blurred or crossing a cut.

## Tasks

1. **Task 1 (80c7dcc)**: `windows`, `candidates`, `sound_peak_times` (over `sound_peaks`) and helpers in v2r/look/pick.py; the sound rule moved out of `extra_times` without changing it (tests/test_look_extras.py still passes). Seven pure tests on hand-made numbers: short clip, exclusions, ranking order, merge cap with no overlap, exact reason text, all-excluded gives empty, sound rule shared.
2. **Task 2 (f60ad21)**: look() writes `candidates` into every done entry (empty for photos); look.json's description documents the names and the "not a choice" note. Seven through-look tests, each over tall (360x640) and wide (640x360): square, blur, cut, jitter, plain, photo, and a facts-only check across four clips. Full suite: 347 passed in about 11 minutes.

## Deviations from Plan

None - plan executed as written. Two small decisions, both within the plan's wording: reasons say "sharpness not measured" or "movement not measured" when nothing was measured, rather than claim a fact; and the helper `sound_peaks` (scores and times) sits under `sound_peak_times` so `extra_times` can keep ordering sound extras by strength.

## Known Stubs

None.

## Threat Flags

None. Reasons are assembled only from fixed phrases, numbers and code-made still labels (T-3-07); a test checks every cited label is a real still of that clip, and the D-04 tests cover T-3-18.

## Self-Check: PASSED

- v2r/look/pick.py: contains `def candidates(`, `def windows(`, `def sound_peak_times(`
- tests/test_look_candidates.py: present, contains `test_reasons_name_facts_only`
- commits 80c7dcc and f60ad21 present; full suite 347 passed
