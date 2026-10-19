---
phase: 04-stage-16-cut-list-and-renderer
plan: "05"
subsystem: render
tags: [render, move, perspective, photo, plan, video]
requires: ["04-01", "04-03", "04-04"]
provides:
  - "plan.move_windows(): push-in, pull-out, pan-left and pan-right as pairs of windows in canvas pixels, by MOVE_AMOUNT"
  - "video.perspective_filter(): the move drawn between pixels, one steady speed, no easing"
  - "Every photo shot (moving or still) built from the full-size upright JPEG, read at 30 frames a second"
  - "tests/media.py: make_line_clip, make_band_photo, make_manifest(photo=...)"
affects: [04-06, 04-07, 04-08, 04-09, 04-10, 04-11]
actuals:
  tokens: 8700
  tasks: 2
  commits: 2
tech-stack:
  added: []
  patterns:
    - "A move is two windows in canvas pixels; the filter reads the four corners as straight lines in the frame number"
    - "Tests follow a thin white line through every frame of the finished reel and measure the change of speed"
key-files:
  created:
    - tests/test_render_plan.py
    - tests/test_render_video.py
  modified:
    - v2r/render/plan.py
    - v2r/render/video.py
    - v2r/render/__init__.py
    - tests/media.py
key-decisions:
  - "A move is drawn with FFmpeg's perspective filter only (sense=source, eval=frame, cubic); the zoom-and-pan filter and a moving crop tick by about 2 px a frame on a canvas-sized picture"
  - "A one-frame shot is built as its fitted crop whatever its move (both windows become the full canvas, and no filter is added)"
  - "Every photo shot comes from the full-size copy, moving or still; a photo with move none is built still (the renderer adds no move of its own)"
requirements-completed: [CUT-03, CUT-04]
duration: "about 50 min (full suite 11 min 52 s)"
completed: 2026-10-19
status: complete
---

# Phase 4 Plan 05: A Shot's Slow Move and Photos From the Full-Size Picture Summary

A shot can now carry a slow push-in, pull-out or pan, each exactly 4 percent of the frame at one steady speed and drawn between pixels so it does not tick, and every photo shot is built from the big upright copy normalize saved, in both shapes.

## What changed, in plain English

- A shot in the cut list can now have a move: `push-in`, `pull-out`, `pan-left` or `pan-right`. A shot with no move is exactly its fitted crop, as before. The renderer never adds a move of its own, not even to a photo (what to move is the handbook's business).
- Every move is the same small amount: 4 percent of the frame, taken from one setting (`MOVE_AMOUNT`). The list carries no amount. The speed never changes from the first picture of the shot to the last, and there is no easing in or out.
- A push-in begins on the normal framing and ends 4 percent tighter, centred on the shot's focus point (and kept inside the frame near an edge). A pull-out is the same, backwards.
- A pan crops in by the same 4 percent so it always has room, then travels exactly that far, the way a camera turning looks. On a tall reel the picture slides 45 pixels across the 1080-pixel width; on a wide reel 80 pixels across 1920. `pan-right` slides the picture to the left on screen (the camera turning right); `pan-left` is the other way.
- A shot of a single frame has no time to move, so it is just the fitted crop.
- Moves are drawn with FFmpeg's `perspective` filter, which works between pixels. The two simpler methods (a moving crop and the zoom-and-pan filter) move by whole pixels and tick about 2 pixels a frame on a picture the size of the frame, which would show as a shimmer on a phone.
- Every photo shot, moving or still, is cut from the full-size upright JPEG, not from the 4-second 1080-wide still. A photo is therefore as sharp in the reel as the picture allows. A photo shot of N frames gives exactly N frames. If a photo's big copy is not a plain file in the work folder, render says `The full-size copy of photo A is missing from the work folder, so it cannot be built.`
- Nothing was seen on a phone. A reel with moves must be made from a phone on this branch before the stage merges.

## Measured on the finished reel (Mac, FFmpeg 6.1, the full canvas size, a 4 px white line, middle row, x264 ultrafast crf from settings)

Limit: largest change of speed (second difference) at most 0.6 px; travel within 1.5 px of the plan.

| Shape | Move | Planned travel | Measured travel | Largest second difference |
|-------|------|----------------|-----------------|---------------------------|
| tall | pan-right | -45.00 | -44.99 | 0.059 px |
| tall | pan-left | +45.00 | +45.00 | 0.051 px |
| tall | push-in (lines at 1/4 and 3/4) | -11.25 / +11.25 | -11.31 / +11.25 | 0.090 / 0.092 px |
| tall | pull-out | +11.25 / -11.25 | +11.22 / -11.19 | 0.089 / 0.090 px |
| wide | pan-right | -80.00 | -80.00 | 0.062 px |
| wide | pan-left | +80.00 | +80.00 | 0.050 px |
| wide | push-in | -20.00 / +20.00 | -20.06 / +20.02 | 0.070 / 0.072 px |
| wide | pull-out | +20.00 / -20.00 | +19.98 / -19.93 | 0.073 / 0.072 px |

A push-in's first frame matches the unmoved crop within 0.5 px (tested). One whole 3.5-second moving reel (piece, sound, final encode, proof sheets excluded) takes 4.2 to 5.2 s on this Mac, about 1.3 s of work per second of reel.

## What to look for on the phone

You cannot see the Mac numbers, so on a phone-rendered reel with moves:

- **Push-in or pull-out shot:** at the first second the picture looks like the plain framing; at the last second it should look only slightly tighter (push-in) or looser (pull-out), as if the camera leaned 4 percent closer or back. Between those two the change should be even, with no jump near the start, middle or end.
- **Pan shot:** the picture should seem to slide sideways very slowly, as if the camera turned, a pole or door frame near the middle should drift sideways by about 4 percent of the screen's width over the whole shot (a pan-right drifts left, a pan-left drifts right). No edge of the picture, black bar or smear should ever show.
- **Failure signs to report:** a faint tick or shimmer on straight vertical edges (a door frame, a horizon of text) at about 15 times a second; a sudden jump at the very first or last frame of a moving shot; a picture that is clearly softer than the shots beside it.
- **Photo shot:** the photo should be as crisp as the clips either side (finer detail than the old 1080-wide still), with no visible step in colour between a photo with a move and one without. A photo shot should last exactly as long as the list says.
- Time to check on a 3.5 to 5 second shot: at 0:00 of the shot, at the middle, and at the last second.

## Task commits

| Task | Name | Commit |
|------|------|--------|
| 1 | Move windows for every move in canvas pixels, and photo segments sized from their full-size copy | 2795d22 |
| 2 | The move drawn with perspective, the photo piece from the full-size JPEG, and measured smoothness | f5caba1 |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] render had no sentence for a missing full-size photo copy**
- **Found during:** Task 2
- **Issue:** the plan says `piece_command` raises ValueError for a photo that is not a plain file in the work folder and that render turns it into a sentence, but `render()` did not catch it.
- **Fix:** `render()` catches the ValueError around `piece_command` and raises `RenderError` with the same sentence, so the scratch folder is still cleaned and nothing is built.
- **Files modified:** v2r/render/__init__.py (not in the plan's file list)
- **Commit:** f5caba1

**2. [Rule 1 - Bug, in the tests only] the tracker lost the line on a pan's first frame**
- **Found during:** Task 2
- **Issue:** the line tracker looked 20 px either side of the previous position, but a pan's first frame is already 22 px (tall) or 40 px (wide) from the unmoved line, so the first measurement landed on the wrong pixels and gave a false second difference of 1.6 px. Also, the brightness floor of 64 asked for in the plan chops the soft edges of the line unevenly.
- **Fix:** the tracker now looks 60 px either side and counts every pixel above 12 (the dark background) as part of the line. The 0.6 px limit and 1.5 px travel limit are unchanged; real results are 0.05 to 0.09 px.
- **Files modified:** tests/test_render_video.py
- **Commit:** f5caba1

### Differences in naming and shape (no behaviour changed)

- A one-frame shot sets both windows to the full canvas for every move (pull-out and pan start on a tight window, which would otherwise show a 4 percent crop on a one-frame shot). The plan says "built as its fitted crop"; this is that reading.
- `move_windows` returns plain lists of floats (the tests compare them with `pytest.approx`).
- A few extra tests beyond the plan: `perspective_filter` text, no filter for equal windows or one frame, refusal of a photo name that is not a plain file in the work folder, and the plan-level one-frame and no-move tests.

## Flagged assumptions settled here (for plan 10 to record and plan 11 to ask)

- Every photo segment, moving or still, is built from the full-size copy (D-21 names only the move).
- A one-frame segment is its fitted crop whatever its move.
- A push-in near an edge tightens towards the frame rather than past the picture (clamped); a pan's height is placed by focus_y and held inside the frame.

## Known Stubs

None.

## Threat Flags

None. T-4-01 (nothing from the list's text enters the graph: the move name chooses one of five Python rules, every number is a float formatted with six decimals) and T-4-02 (a photo file must be a plain name directly in the work folder, checked by `check` and again in `video.photo_path`, and passed to FFmpeg only as an `-i` argument) are in place and tested.

## Self-Check: PASSED

- v2r/render/plan.py (`move_windows`), v2r/render/video.py (`perspective_filter`, `photo_path`), tests/test_render_plan.py, tests/test_render_video.py exist; tests/media.py has `make_line_clip` and `make_band_photo`.
- Commits 2795d22 and f5caba1 exist on stage-16-render.
- `grep -v '^\s*#' v2r/render/video.py | grep -c zoompan` prints 0.
- Full suite: 671 passed in 11 min 52 s under `run-with-timeout 1500` (the bound was not reached).
