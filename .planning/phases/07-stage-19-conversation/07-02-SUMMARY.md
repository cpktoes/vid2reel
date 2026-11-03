---
phase: 07-stage-19-conversation
plan: "02"
subsystem: render
tags: [cut-list, recipe, check, settings, schema, tests]

requires:
  - phase: 07-stage-19-conversation
    provides: "plan 01's Stage 19 block in settings.py (the revise names) above the render block"
provides:
  - "an optional top-level recipe (lively or calm) in the cut list's rulebook; the list stays version 1"
  - "settings.RECIPES (shot lengths in seconds) and settings.DEFAULT_RECIPE, at the head of the Stage 19 block"
  - "check.recipe_notes: one grouped note for shots too short and one for shots too long, never a refusal"
  - "a test that holds EDITOR.md's recipe sentence and settings.RECIPES to the same numbers"
affects: [07-04, 07-06]

actuals:
  tokens: 5900
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "lengths compared in whole frames with plan.frames, the way render counts them"
    - "a guard test reads the user's text and never rewrites it"

key-files:
  created: []
  modified:
    - schema/cutlist.schema.json
    - v2r/settings.py
    - v2r/render/check.py
    - tests/cutlists.py
    - tests/test_cutlist_check.py
    - tests/test_editor_handbook.py

key-decisions:
  - "Recipes live in settings.py only; the schema holds just the two names and render never reads the field"
  - "One grouped sentence per direction (too short, too long), naming every shot, as research Q2 decided"
  - "A photo is exempt from the longest length only"

requirements-completed: []

duration: 25min
completed: 2026-11-03
status: complete
---

# Phase 7 Plan 02: the cut list's recipe and check's shot-length notes Summary

**A cut list can now say `"recipe": "lively"` or `"calm"`; check adds one plain note for shots shorter or longer than that recipe allows (Lively 1.5 to 3 seconds, Calm 3 to 5), never refuses for it, and a test keeps the handbook's recipe sentence and settings.py agreeing.**

## What was built

- **Schema.** `recipe` is an optional top-level field with the two values. It is not required, the version stays 1, and no number is in the schema. A wrong value such as "fast" is refused with check's usual sentence: `The list's recipe is "fast"; it must be one of lively or calm.`
- **Settings.** `RECIPES = {"lively": (1.5, 3.0), "calm": (3.0, 5.0)}` and `DEFAULT_RECIPE = "lively"` sit under a `# recipes:` comment, above plan 01's `# revise:` names and the `# render:` line. The render block is unchanged, so its 34-name count still holds.
- **check.** `recipe_notes` runs after the crop notes and before the no-sound note. It compares each shot's length in whole frames, so a shot exactly at the shortest or longest length is fine and one frame outside it is noted (tested at 44, 45, 90 and 91 frames). Shots that are too short are named in one sentence and those too long in another, for example `Segments 1, 3 and 5 last longer than a Lively shot's 1.5 to 3 seconds.` A photo is held to the shortest length only. A list with no recipe is read as Lively and check says `The list names no recipe, so Lively (shots of 1.5 to 3 seconds) was assumed.`
- **Render ignores it.** No file in v2r/render other than check.py (and later revise) mentions the field.
- **Guard.** `recipe_numbers` and `recipe_problems` in tests/test_editor_handbook.py read the numbers after "Lively" and "Calm" in EDITOR.md (words such as "one and a half" or digits) and fail with one sentence if they differ from settings.RECIPES. EDITOR.md itself was not touched.

## Task Commits

1. Task 1 (tracer): `fb28be0` test(07-02) failing tests, then `bd54c73` feat(07-02) the recipe field, settings and check's notes
2. Task 2: no separate commit. The "no recipe, read as Lively" note was written in the same function as task 1's notes, so it landed in `bd54c73`, with its test constant and the updated expectations
3. Task 3: `9f7adba` test(07-02) the recipe-number guard

## Tests

- `tests/test_cutlist_check.py`, `tests/test_render_settings.py`, `tests/test_editor_handbook.py`, `tests/test_match.py` together: 373 passed.
- `tests/test_render_tracer.py`: 45 passed (needs FFmpeg).
- Every new test runs in both tall and wide. tests/test_revise.py was not run or edited. The full suite was not run.

## Existing tests whose expected notes changed, and why

- `test_a_list_with_one_segment_and_nothing_else_is_ready`: the hand-built list names no recipe, so it now also gets the "Lively was assumed" note (new constant `ASSUMED_LIVELY`).
- `test_a_lower_crop_share_gives_no_crop_note`: the wide example has three talking-head shots of 10, 12 and 10 seconds, so with the crop notes gone it still shows the Lively "longer than" note; the expected list is the example's notes minus the crop ones.
- `EXAMPLE_NOTES["wide"]` gained the "Segments 1, 3 and 5 last longer..." sentence after its two crop notes, which flows into every test that expects the example's whole note list. The tall example has no recipe note: every shot is 75 or 90 frames.
- `RULE_NOTE`, the filter that hides rule notes in field-note tests, learned the two new kinds of sentence.
- Both examples in tests/cutlists.py now carry `"recipe": "lively"`.

## Deviations from Plan

### Auto-fixed Issues

None. One note on shape: tasks 1 and 2 share one function, so the assumed-Lively note was written with the rest and committed once; task 2's tests were already in the first commit's red tests and only the one old expectation needed updating. The tracer's check is fully automated and passed, so execution continued without a stop.

## Known Stubs

None.

## Threat Flags

None. A value outside the two names is refused by the schema before check's rules run, so `settings.RECIPES[name]` only ever sees "lively" or "calm" (T-7-06).

## What to check from a phone

Nothing in this plan changes how a reel looks or sounds, and nothing renders. The new notes appear in check's output only.

## Self-Check

- schema, settings, check.py, tests: found and committed
- commits fb28be0, bd54c73, 9f7adba: found in git log
- RECIPES line sits before the `# revise:` and `# render:` lines in settings.py: yes
- `git diff -- EDITOR.md`: empty

## Self-Check: PASSED

## Plain English for the user

A cut list can now say which recipe it was cut to, Lively or Calm. The shot lengths (Lively one and a half to three seconds, Calm three to five) now live in settings.py, and a test checks they match the sentence in your handbook; if you ever change one and not the other, the test says which. When you run check, look for new notes in two forms: "Segments 1, 3 and 5 last longer than a Lively shot's 1.5 to 3 seconds" (a long shot, such as a talking head, is flagged but still renders) and "The list names no recipe, so Lively was assumed" (an older list). Neither note blocks anything. A photo may run past the longest length. Nothing about how a reel looks or sounds changes.
