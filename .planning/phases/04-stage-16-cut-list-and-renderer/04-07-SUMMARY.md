---
phase: 04-stage-16-cut-list-and-renderer
plan: "07"
subsystem: render
tags: [render, check, cutlist, rules, notes, music]
requires: ["04-03", "04-04", "04-06"]
provides:
  - "check.count_problems(), look_problems(), cover_problems(), length_problems(), sound_problems(), segment_lengths(), seconds_pair()"
  - "check.rule_notes() and crop_notes(): the four notes that never refuse"
  - "check() runs canvas, clips, count, segments, touch-up, sound, cover, length and (only if all pass) fit, then the notes"
affects: [04-08, 04-09, 04-10, 04-11]
actuals:
  tokens: 36000
  tasks: 2
  commits: 2
tech-stack:
  added: []
  patterns:
    - "Every rule is a function from the list (and the manifest) to a list of sentences; check() joins them in a stated order, so one run reports every fault"
    - "A rule about the whole reel (length, music) waits when any single segment is not a real stretch, so no sentence rests on something already wrong"
key-files:
  created: []
  modified:
    - v2r/render/check.py
    - v2r/render/sound.py
    - tests/test_cutlist_check.py
key-decisions:
  - "The rules no longer wait for each other (only the fit does), so a list with several faults gets all its sentences at once, in the stated order"
  - "Clips and touch-ups are checked in letter order, so the order keys were written in changes nothing"
  - "When one decimal would make two different lengths read the same (a 2.967-second reel against a 3-second minimum), the sentence gives two decimals"
requirements-completed: [CUT-02]
duration: "about 70 min (full suite 12 min 43 s)"
completed: 2026-10-19
status: complete
---

# Phase 4 Plan 07: The Checker's Whole Rulebook Summary

`v2r check` now knows every rule of the design: it names each broken rule in one plain sentence, in a fixed order, and says four things worth saying (a photo with no move, no touch-up, a silent reel, a crop that keeps little of the picture) without refusing the list.

## What changed, in plain English

- **More rules, each one sentence.** `check` now says when a list has more than 120 shots, when a touch-up number is over its limit (brightness 8, blue and red 4, saturation between 0.92 and 1.08; a number exactly at a limit is fine), when a touch-up is for a clip that is not in the list, when the cover points at a shot that does not exist or at a moment past the end of its shot, and when the whole reel is shorter than 3 seconds.
- **The music rules.** `check` says when the music track is not in the library (and that only `test-tone` can be used until the library exists), when its file is missing or the library file cannot be read, when the reel starts past the end of the track, and, in the guide's own words, when the track is too short: `The music runs out at 14.0 seconds but the reel is 20.0 seconds long.` Nothing is looped or cut to make it fit; the list has to name an earlier start or another track.
- **All the faults at once.** Before, the checker stopped at the first rule that found something. Now every rule runs and the sentences come in one fixed order (canvas, clips, how many shots, shots, touch-up, music, cover, length), so Claude can fix a whole list in one go. Only the "does it fit under the size limit" test still waits, because it measures a reel that has to be sound first. The same list always gives the same sentences in the same order.
- **Four notes that never refuse.** `Segment 5: E is a photo with no move.` / `There is no touch-up in the list; run match if the clips should match.` / `This reel has no sound at all.` / `Clip B is sideways in a tall frame, so the frame keeps only 32 percent of its picture.` (and `upright in a wide frame`, and `Photo C` for a photo). The crop note shows once per clip whose kept share is under half. The list is still ready to render.
- **The two approved example reels pass.** The tall one with exactly one note (clip B keeps 32 percent) and the wide one with exactly two (clip B keeps 32 percent and photo C keeps 42 percent).
- **Nothing is ever fixed behind your back.** No rule clamps, trims or drops a bad time; a list that breaks a rule builds nothing and the sentence says what to fix.
- **Nothing looks or sounds different yet.** This plan changes only what `check` says. No video or sound was produced, so there is nothing to look at or listen to on a phone for this plan.

## Every sentence check can print from this plan

Problems (one per broken rule, `{...}` filled in from the list):

1. `The list has {k} segments; one reel can have at most 120.`
2. `The touch-up names clip {L}, which is not in the list's clips.`
3. `Clip {L}'s touch-up brightness is {v}; it can be at most 8 either way.` (and `blue`, `red` with 4)
4. `Clip {L}'s touch-up saturation is {v}; it must be between 0.92 and 1.08.`
5. `The music track "{id}" is not in music/library.json.` and, with no library file, `...; there is no music/library.json yet, so only "test-tone" can be used.`
6. `The music file for "{id}" is missing from music/.`
7. `music/library.json could not be read, so the music cannot be checked.`
8. `The music track "{id}" is {n} seconds long, so it cannot start at {s} seconds.`
9. `The music runs out at {remaining} seconds but the reel is {reel} seconds long.`
10. `The cover names segment {k}, but the list has only {n} segments.`
11. `The cover is at {at} seconds into segment {k}, but segment {k} is only {len} seconds long.`
12. `The reel is {s} seconds long; it must be at least 3 seconds.`

(Plus the sentences of plans 01 and 04: the canvas, the clips block, the shots and the size fit.)

Notes, after all problems, in this order: the field notes (plan 04), the touch-up note, photos with no move in segment order, crop notes in letter order, the silence note.

## Deviations from Plan

**1. [Rule 2 - Missing critical functionality] The music id echoed by `sound.track` was not cut to 40 characters**
- **Found during:** Task 2 (the "a music name cannot fake a line" test, threat T-4-06)
- **Issue:** `sound.track` passed the track name through `clean_text` with the longer file-name limit, so a very long music name in a list would be printed in full in a check sentence.
- **Fix:** it is cut to `settings.CUTLIST_ECHO_CHARS` like every other echoed value.
- **Files modified:** v2r/render/sound.py (one line)
- **Commit:** 42470f0

**2. [Plan wording] Crop notes are in letter order, not order of first use**
- The task text said "order of first use" while the plan's own truths said "crops in letter order". Letter order is what makes the order of keys irrelevant, so that is what was built. For both approved examples the two orders are the same.

**3. [Plan wording] The clips block and touch-ups are checked in letter order, not the order the list wrote them in**
- The task said "key order"; the plan's edge cases say the order of keys changes nothing. Sorted order satisfies both; a single fault gives the same sentence as before.

**4. [Rule 1 - Bug] A reel just under the minimum read as "3.0 seconds long; it must be at least 3 seconds"**
- A 2.967-second reel (89 frames) printed as 3.0 with one decimal. The sentence now gives two decimals when one decimal would read the same as the limit (`2.97`); the same helper guards the music sentence. Sentences for the plan's own examples (2.0, 14.0, 20.0) are unchanged.

**5. Tests**
- The plan's earlier examples tests (`test_the_approved_examples_are_ready_to_render` and the one-segment list) expected no notes; they now expect the notes the rules give (`test_examples_pass_with_their_notes` replaces the first). The field-note tests ignore the four rule notes via `run_check`'s default so they keep testing only field notes.
- No render test list needed lengthening: all tests in test_render_tracer.py, test_render_video.py and test_render_sound.py pass unchanged with the length rule in place.

## Known Stubs

None.

## Threat Flags

None. The only new surface is `check` reading `music/library.json` through plan 06's `sound.track`, which already refuses a file name that is not a plain name inside the music folder (T-4-02); a test covers a `../` name.

## Test results

- `uv run pytest tests/test_cutlist_check.py -q`: 233 passed (tall and wide), a few seconds.
- Render tests after the length rule (tracer, video, sound, plan, settings): 177 passed in 3 min 3 s.
- Full suite `uv run pytest -x -q`: 844 passed in 12 min 43 s.

## Task commits

| Task | Name | Commit |
|------|------|--------|
| 1 | Segment count, touch-up caps, cover, length and the order of the rules | 595b008 |
| 2 | The music rules and the four notes | 42470f0 |

## Self-Check: PASSED
