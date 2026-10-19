---
phase: 04-stage-16-cut-list-and-renderer
plan: "04"
subsystem: render
tags: [render, check, cut-list, json-schema, jsonschema, notes]
requires: ["04-01", "04-02"]
provides:
  - "schema/cutlist.schema.json: the cut list's rulebook, version 1, JSON Schema Draft 2020-12, structure only"
  - "check reports every rulebook fault as one plain sentence naming its place and the offending value"
  - "check notes every accepted-but-unbuilt field (speed, transition, segment text, top-level text and voice) and every unknown field"
  - "tests/cutlists.py: the two approved example lists, a placeholder work folder, clips_block, scaled, write_list"
affects: [04-05, 04-06, 04-07, 04-08, 04-09, 04-10, 04-11]
actuals:
  tokens: 12600
  tasks: 2
  commits: 2
tech-stack:
  added: []
  patterns:
    - "jsonschema imported only inside check (lazy, like Pillow), so doctor, normalize, look and join never load it"
    - "one sentence function per schema keyword (SENTENCES), with a test that no keyword the schema uses is missing"
    - "known field names are read from the schema itself, so the schema stays the single source of names"
key-files:
  created:
    - schema/cutlist.schema.json
    - tests/cutlists.py
    - tests/test_cutlist_check.py
  modified:
    - v2r/render/check.py
key-decisions:
  - "The clips block and look.touch_up are objects keyed by letter, not lists; why is required and must not be empty; when the rulebook finds a problem the work-folder rules wait for the next run and one note says so"
  - "The schema offers no choice between sub-schemas and closes no object, so each fault gives one error and unknown fields reach Python's notes"
  - "A missing-field error is reported once per object with one sentence per missing name (jsonschema reports each missing name as its own error, so the repeats are dropped)"
  - "Errors are ordered by place with segment numbers compared as numbers, then by keyword"
requirements-completed: [CUT-01, CUT-08]
requirements-partial: [CUT-02]
duration: "about 1 h 15 min (full suite 8 min 43 s)"
completed: 2026-10-19
status: complete
---

# Phase 4 Plan 04: The Rulebook and Check's Sentences Summary

The cut list now has a written rulebook (schema/cutlist.schema.json) and `check` reads every list against it with jsonschema, turning each fault into one plain sentence and each accepted-but-unbuilt or unknown field into a note, in both shapes.

## What changed, in plain English

- The cut list has a rulebook file, `schema/cutlist.schema.json`. It says which parts a list has (version, canvas, clips, segments, and optionally look, sound, cover, text, voice) and what each part may hold. It holds structure only. The numbers that control behaviour (the two canvas sizes, the frame rate, the touch-up limits) stay in `v2r/settings.py` and are checked in Python.
- `check` now says exactly what is wrong, one sentence per fault. Examples of what it prints now:
  - `Problem: Segment 4 has no to.`
  - `Problem: Segment 1's move is "zoom"; it must be one of none, push-in, pull-out, pan-left or pan-right.`
  - `Problem: The canvas's width must be a whole number.`
  - `Problem: Segment 1's focus_x is 1.5; it must be between 0 and 1.`
  - `Problem: Segment 1's why is empty; say which still it rests on.`
  A list with three faults gets three sentences in a steady order, with segment 10 after segment 2. A list of just `{}` gets one sentence each for the version, canvas, clips and segments.
- Things a list may carry but that are not built yet (speed, transition and text on a shot; text and a voice track for the whole reel) are accepted. `check` says so in a note and carries on:
  - `Note: Segment 1's speed is accepted but not built yet, so the shot plays at normal speed.`
  - `Note: The list's voice track is accepted but not built yet, so it is not in the reel.`
  An empty value (nothing, empty text, an empty list) gives no note. The reel built is exactly the same with or without these fields (a test proves it).
- A field the rulebook does not know gets a note too, and is ignored: `Note: Segment 1 has a field called "zoom" that v2r does not know, so it was ignored.` Names are compared exactly, so `Move` is unknown while `move` is known. A name carrying a line break cannot fake a second printed line.
- When the rulebook finds any problem, the list is not compared with the work folder in that run. One note says so: `Note: The list was not compared with the work folder, because of the problems above.` Fix the problems, run again, and the work-folder rules (clips, lengths, shots inside their clips, the size limit) run as before.
- If the jsonschema library is missing, `check` says `The jsonschema library is not installed, so the cut list cannot be checked; install the requirements again.` and `render` builds nothing. Doctor, normalize, look and join never load that library.
- `check` still only reads: the tests confirm the list's bytes and the work folder's files are identical before and after every run.
- Your two approved example reels (the 20-second tall reel of seven shots over four clips and a photo, and the 38-second wide talking head with two cut-aways) are written into `tests/cutlists.py` and pass the rulebook in the tests, so every later change is checked against them.
- Nothing here changes how a reel looks or sounds, so no phone test is needed for this plan. Nothing has been seen on a phone yet; a reel must be made from a phone on this branch before the stage merges to main.

## Performance

`tests/test_cutlist_check.py` (124 tests, no FFmpeg) runs in about 3 s. The whole suite, 600 tests, passes in 8 min 43 s (523 s) under `run-with-timeout 1500`; the bound was not reached.

## Task commits

| Task | Name | Commit |
|------|------|--------|
| 1 | The rulebook file and the two approved example lists | 70a9640 |
| 2 | check turns every rulebook fault into one sentence, and notes accepted and unknown fields | 0c943f1 |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] jsonschema repeats a missing-field error once per missing name**
- **Found during:** Task 2, first run of the `{}` test (16 sentences instead of 4)
- **Issue:** jsonschema yields one `required` error for each missing name, and each carries the whole list of required names, so naming every missing name per error repeated each sentence.
- **Fix:** `schema_problems` keeps the first `required` error at each place; its one function names every missing name.
- **Files modified:** v2r/render/check.py
- **Commit:** 0c943f1

### Differences in naming and shape (no behaviour changed)

- The plan asked for `shown(value)` to print values with quotes. `shown` already exists in check.py and is used by plan 01's sentences as plain cut text, so the new printer is named `value_words`; `shown` is unchanged.
- `load_schema()` raises the existing `Refused` exception with the one sentence, as planned, rather than a new exception type.
- Task 1's schema tests read the schema file by their own path; Task 2 added `SCHEMA_PATH` to check.py (tests monkeypatch `check.SCHEMA_PATH` for the missing-rulebook case).
- The plan listed reading tests for NaN, 1e400, a 16-digit integer, a repeated name and an oversized file; plan 01's tests/test_render_tracer.py already prove those exactly, so they are not duplicated. This plan's tests add a missing list, an empty file and non-block lists (`[]`, `3`, `null`, `"x"`).
- On a read problem (no list, bad JSON) `check` still also reports the manifest's own problem, as plan 01 did; the manifest is read only after the rulebook passes otherwise.

## Flagged assumptions settled here (for plan 10 to record and plan 11 to ask)

- `clips` and `look.touch_up` are objects keyed by letter.
- `why` is required and non-empty.
- When the rulebook reports a problem, the work-folder rules wait for the next run, with one note.
- A clip's letter is one to three capitals (matching look.LETTER); the pattern's end-of-text sign also matches before a final line break, so the work-folder rules still test each letter as a whole.

## Known Stubs

None. Speed, transition, text and voice are intentionally accepted but unbuilt (D-08); they are not stubs in code, they get a note each time.

## Threat Flags

None. Mitigations in the plan's threat model are in place: T-4-03 (the reader's size cap and number hooks run before the rulebook), T-4-06 (every echoed value and name goes through `normalize.clean_text`, cut to `CUTLIST_ECHO_CHARS`, tested with a line-break name), T-4-12 (check opens the list read-only; tests compare bytes and file lists before and after).

## Self-Check: PASSED

- schema/cutlist.schema.json, tests/cutlists.py, tests/test_cutlist_check.py and v2r/render/check.py exist.
- Commits 70a9640 and 0c943f1 exist on stage-16-render.
- `grep` finds no top-level jsonschema import, no `structure_problems`, no `oneOf`/`anyOf` and no closed object in the schema.
- With jsonschema's import blocked, doctor, normalize, look, join and render still import.
- Full suite: 600 passed.
