---
phase: quick-261101-qff
plan: 01
subsystem: normalize
tags: [normalize, size-limit, cli]
requires: []
provides:
  - "normalize --no-size-limit, computer only"
  - "new skip sentence for a file over the phone's size cap"
affects: [normalize, README, decisions]
actuals:
  tokens: 2500
  tasks: 2
  commits: 0
key-files:
  created: []
  modified:
    - v2r/__main__.py
    - v2r/normalize.py
    - tests/test_normalize.py
    - tests/test_editor_handbook.py
    - README.md
    - docs/decisions.md
key-decisions:
  - "The option only switches off the size check; the 400 MB number in settings.py is unchanged."
  - "The skip sentence never names the option, so the phone's Claude does not learn it."
status: complete
completed: 2026-11-01
commit: one commit on stage-17-handbook, made afterwards at the user's request
---

# Quick 261101-qff: Let a computer include a clip over the phone's size cap

## What changed, in plain English

- On the Mac you can now type `--no-size-limit` after `normalize` to keep a clip bigger than 400 MB instead of having it left out. Without that option nothing is different: the phone's way is the default.
- On her phone, a clip over 400 MB is still left out, but with a clearer sentence: "... is N MB, over the 400 MB a phone can reliably send, so it was left out. On a computer the same reel can be made with it included." The old promise that a way to shrink clips would come in a later stage is gone. The sentence does not mention the option, so the phone's Claude never learns it.
- Only the size check is switched off. The picture-size limits, the time allowance per clip and the "already in the work folder" check still apply.
- README.md explains the option in one short paragraph beside the `--work` paragraph, as computer-only. EDITOR.md, skill/, the numbers in settings.py, fixtures/ and work/ were not touched.
- A new one-line check in `tests/test_editor_handbook.py` makes the handbook test fail if EDITOR.md ever mentions `--no-size-limit` (next to the same check for `--work`).
- docs/decisions.md has one new dated line (2026-11-01, Stage 17) about the option.

## Files changed (committed later as one commit on stage-17-handbook, at the user's request)

- v2r/__main__.py: the `--no-size-limit` option (off unless typed), passed to normalize.
- v2r/normalize.py: `normalize()` and `convert_one()` take `size_limit` (default on); the size check runs only when it is on; the new skip sentence.
- tests/test_normalize.py: the oversized-file test now pins the exact new sentence (and that it names no option); new tests for `size_limit=False` and for the command-line option and its default, each in tall and wide.
- tests/test_editor_handbook.py: one line, EDITOR.md must never mention `--no-size-limit`.
- README.md: the computer-only paragraph.
- docs/decisions.md: the dated line.

## What to look for

Video processing itself did not change, so there is nothing new to watch or listen for in a reel. On the Mac, with a real clip over 400 MB, run normalize once without and once with `--no-size-limit` (always with `--work` pointing at a scratch folder): without it you should read the new sentence, with it you should get A.mp4. A phone test is only needed to see the new sentence in the chat.

## Deviations from Plan

- Added the one-line `--no-size-limit` check to `tests/test_editor_handbook.py`, as agreed with the user before the run (not in the written plan).
- The tests were written before the code, but the code was written before the failing run was observed (red step not run separately).

## Known Stubs

None.

## Verification

- `uv run pytest -q tests/test_normalize.py -k "oversized or no_size_limit or entry_that_cannot_be_written"`: 8 passed.
- Full suite `uv run pytest -q`: 1034 passed in 536.06s.
- `git diff --quiet -- EDITOR.md skill/ v2r/settings.py`: no changes. HEAD is still 850e6c5; nothing committed.

## Self-Check: PASSED

## Added afterwards by the user's request (2026-11-01)

- EDITOR.md: the "When things go wrong" sentence now covers a file too big for the phone and says the same reel can be made on a computer with it included; it does not name the option. To stay under the 1,200-word cap, six asides were trimmed (the user chose them).
- .planning/STATE.md: quick-task row 8 and the last-activity line, written by hand.
