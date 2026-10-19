---
phase: 04-stage-16-cut-list-and-renderer
plan: "08"
subsystem: render
tags: [render, match, touch-up, colour, cutlist, lutyuv]
requires: ["04-01", "04-03", "04-04", "04-05"]
provides:
  - "python -m v2r match [CUTLIST] [--work FOLDER]: writes look.touch_up into the cut list from look.json"
  - "v2r/render/match.py: MatchError, read_look(), touch_up_records(), match(), module attribute WORK_DIR"
  - "v2r/render/video.py: touch_up_filter(), used in both the clip chain and the photo chain"
affects: [04-09, 04-10, 04-11]
actuals:
  tokens: 11500
  tasks: 2
  commits: 2
tech-stack:
  added: []
  patterns:
    - "match is pure arithmetic on look.json; the list is rewritten whole (cutlist.json.tmp then os.replace) or not at all"
    - "The one colour step in render is lutyuv with explicit round() and legal-range limits, placed after the move"
key-files:
  created:
    - v2r/render/match.py
    - tests/test_match.py
  modified:
    - v2r/__main__.py
    - v2r/render/__init__.py
    - v2r/render/video.py
    - tests/test_render_video.py
key-decisions:
  - "The group whose median is taken is the measured clips the segments use; every measured letter of clips still gets a record, so a later swap has numbers (RESEARCH open question 3). Plan 10 records it, plan 11 asks the user."
  - "The colour offsets are worked out after the saturation multiply, using the rounded multiplier the list carries, so render's arithmetic lands on the group's middle"
  - "A raw correction is compared with a cap after rounding to six places, so float noise never marks an exact-cap value as capped"
requirements-completed: [CUT-05]
duration: "about 50 min, plus the full suite 15 min 07 s"
completed: 2026-10-19
status: complete
---

# Phase 4 Plan 08: match and the Touch-up Summary

`python -m v2r match` works out a small, capped colour nudge for each clip from look's measurements and writes it into the cut list as numbers, and render applies exactly those numbers (and nothing else) to colour.

## What changed, in plain English

- **A new command, `match`.** After look has measured the clips, `match` reads how bright each clip is, how much it leans blue or red, and how colourful it is. It takes the middle of those across the clips the reel actually uses (the median, so one odd clip does not drag the rest) and writes, for each clip, a nudge towards that middle. It never pushes towards plain grey, so a golden evening stays golden; the clips only come to agree with each other.
- **The nudge is small and capped.** At most 8 steps of brightness either way (about a third of a stop), at most 4 steps of blue or red (a faint tint), and saturation between 0.92 and 1.08. A number that hit its cap is printed with `(at the cap)`. The numbers sit in the cut list under `look.touch_up`, one record per clip, where they can be read.
- **Running it again starts fresh.** Every run rewrites every record, so halving a cap in `v2r/settings.py` and running `match` again gives new numbers. Nothing else in the list changes (`look.filter` is kept, or set to `"none"` when the list had none).
- **It refuses rather than guessing.** No look.json, one that is still running, one made from other clips than the work folder holds, a clips block that does not match, or no measured clip in the segments: `match` says so in one sentence and leaves the list exactly as it was. A clip look could not measure gets no record and one note.
- **Render applies the numbers and nothing else.** Brightness is added to the picture's brightness; each colour channel keeps its distance from neutral times the saturation, plus its offset; the result is rounded (not cut off) and held in the legal video range. A list with no touch-up, or a clip whose record is all neutral (0, 0, 0, 1), gets no colour step at all, so its colour is the working copy's own. The step runs after the slow move, on photos and clips alike.

## Example of what match prints

```
A: brightness +8.0 (at the cap), blue +1.5, red -1.5, saturation 1.04
B: brightness +3.0, blue +0.5, red -0.5, saturation 1.01
C: brightness -3.0, blue -0.5, red +0.5, saturation 0.99
D: brightness -8.0 (at the cap), blue -1.4, red +1.4, saturation 0.97
Clip E has no brightness and colour in look.json, so it gets no touch-up.
The touch-up for 4 clip(s) is in <work folder>/cutlist.json; render applies exactly these numbers.
```

## What to look for on the phone

Nothing was watched here; the tests measure flat colour patches on a finished reel (a (100, 120, 140) clip with the numbers 6, -2, 3, 1.05 comes out at (106, 118, 144) within one step). On a phone-rendered reel made with a touch-up, please compare the same reel with and without it (build once with `look.touch_up` removed from the list):

- **At the cut between two clips shot in different light** (for example the first cut where one clip is clearly brighter or warmer than the one before): with the touch-up the two should look like one shoot, with the brightness step at the cut visibly smaller.
- **Nobody should be able to call it a filter.** Skin tones, a sunset or a blue sea should look as they did; nothing should look washed out, grey, tinted or more vivid than before. If it reads as an effect anywhere, halve the caps in `v2r/settings.py` (the `# match:` block) and run `match` again.
- **A clip that was already the group's middle should look unchanged** (its record is close to 0, 0, 0, 1).
- On a **photo**, the colour should match its neighbours in the same way and its slow move should still be smooth.

## Deviations from Plan

None - plan executed exactly as written. (One small addition: `match` is imported in `v2r/render/__init__.py` so `render.match` is reachable from `__main__`, as `render.check` is.)

## Tests

- `tests/test_match.py`: 52 tests, both shapes, no FFmpeg (the arithmetic, the cap and rounding edges, even counts, a single clip, unused and unmeasured clips, re-runs after halving a cap, only `look.touch_up` changing, every refusal leaving the list's bytes unchanged, and the list that match writes passing check's touch-up rules).
- `tests/test_render_video.py`: new touch-up tests on the finished reel and on the scratch piece (exact numbers, no touch-up leaves colour alone, neutral record builds no filter, rounding not truncating at CRF 0, legal range, each clip its own numbers, a photo), and the piece-commands test now includes touch-ups and still uses only filters in `RENDER_FILTERS`.
- Full suite: `917 passed in 906.92s (0:15:06)`.

## Known Stubs

None.

## Threat Flags

None. T-4-01 (numbers only are formatted into the filter), T-4-05 (list written whole or not at all, refusals leave bytes unchanged) and T-4-07 (match writes only the cut list and refuses a look.json from other clips) are mitigated and tested.

## Self-Check: PASSED

Files found: v2r/render/match.py, tests/test_match.py, v2r/render/video.py (touch_up_filter). Commits found: 696a03f (Task 1), d497d7f (Task 2).
