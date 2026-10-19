---
phase: 04-stage-16-cut-list-and-renderer
plan: "01"
subsystem: render
tags: [render, check, cut-list, ffmpeg, frame-arithmetic, proof-sheets]
requires: []
provides:
  - "python -m v2r check and python -m v2r render, both shapes, with the shape taken from the list's canvas"
  - "v2r/render/ (plan, check, video, sound, proof, __init__): frame arithmetic, strict list reading, clips-block matching, per-shot pieces, one final encode under join.fit, proof sheets"
  - "SheetBook(work_dir, folder, stem) so proof sheets live in their own folder"
  - "test helpers make_index_clip, index_luma, make_colour_clip, patch_yuv, mp4_boxes and tracer_work"
affects: [04-03, 04-04, 04-05, 04-06, 04-07, 04-08, 04-09, 04-10, 04-11]
actuals:
  tokens: 16000
  tasks: 2
  commits: 3
tech-stack:
  added: []
  patterns:
    - "one scratch piece per shot, then one final encode (generation count of two)"
    - "check rules run in order and a later rule runs only when the earlier ones found nothing"
    - "every setting read at call time so tests can change it"
key-files:
  created:
    - v2r/render/__init__.py
    - v2r/render/plan.py
    - v2r/render/check.py
    - v2r/render/video.py
    - v2r/render/sound.py
    - v2r/render/proof.py
    - tests/test_render_tracer.py
  modified:
    - v2r/settings.py
    - v2r/__main__.py
    - v2r/look/sheets.py
    - tests/media.py
    - tests/test_look_sheets.py
key-decisions:
  - "Frame arithmetic is frames(s) = floor(round(s x 30, 6) + 0.5), so 2.5 s is 75 frames every time; a whole clip uses a thousandth of a frame of benefit instead, so sound running past the last picture never invents a frame"
  - "check runs canvas, then clips block, then segments, then fit, each only when the ones before found nothing"
  - "Only the first problem of each clip in the clips block is reported: one sentence per clip"
  - "List text echoed in a sentence is cut to CUTLIST_ECHO_CHARS (40) characters; file paths are cleaned but not cut"
requirements-completed: [CUT-02, CUT-03, CUT-07]
duration: "tracer session plus about 1 h for Task 2 (full suite alone 10 min 15 s)"
completed: 2026-10-19
status: complete
---

# Phase 4 Plan 01: Tracer Render and Strict Check Summary

A two-shot cut list now goes through `check` and `render` to a finished reel (exact frame count, filled canvas, one final encode under join's size rule) with a proof sheet, in tall and wide, and `check` reads a list strictly and refuses a clips block that does not match the work folder.

## What changed, in plain English

- There are two new commands. `python -m v2r check` reads a cut list and says, one plain sentence per problem, what is wrong with it. `python -m v2r render` builds exactly what the list says into a reel. Neither asks for a shape: the list's canvas decides tall or wide, and it must match the shape the clips were converted for.
- Every shot fills the frame. The part of the picture that fills the canvas is cut out around the shot's focus point (the middle if the list names none), kept inside the picture at its edges. There are no bars, no blurred background and no way to ask for either.
- Every shot has an exact length in frames. 2.5 seconds is always 75 frames. Two shots from the same clip that touch (one ends where the next begins) join with no frame repeated and none dropped; a test proves this at the cut, to the frame.
- Only the list is built. Nothing is trimmed, nudged, reordered or dropped on its own, and no colour or sound step is added.
- The reel is encoded once at the end and sized with the same rule join already uses (the longer the reel, the smaller the frame, so it comes back under the phone's limit). If the frame had to shrink, render says so in one sentence, then names the file, its size and frame size, and prints the file's path last.
- A proof sheet (`work/proof/proof-NN.jpg`) shows the first and last picture of every shot, labelled like `2 in 01.0` and `2 out 01.9` (shot number, then time on the reel). Look's own sheets keep their names.
- `check` now refuses, in one sentence each: a list over 1 MB, NaN or Infinity, a number too large to hold, a whole number of more than 15 digits, a name written twice in one block, and a list nested too deeply. Any of the list's own text a sentence repeats is cut to 40 characters, so a list cannot print a long instruction.
- `check` also compares the list's `clips` block with the work folder and says, per clip, when the letters, file names or lengths do not match, when a clip was skipped at conversion, or when a working copy is missing. File names that differ only in how an accented letter is stored count as the same name.
- Still to come in later plans: the doctor's list of every FFmpeg piece, the rest of the stage's settings, the full rulebook, moves, photos, music, touch-up and the cover still.
- Nothing here has been seen on a phone. After the whole stage is built, a reel must be made from a phone on this branch before it merges to main.

## What to look and listen for (phone test, later)

Render a short list of two shots of different clips. At the cut between the two shots (the moment the first shot ends) look for a clean straight cut, no flash, no repeated or skipped moment. Check the first and last picture of each shot against the proof sheet's labels. Listen at the same moment for no click or gap in the sound. Nothing in this plan adds touch-up, music or movement.

## Performance

The tracer render (check, two shots, final encode, proof sheet) takes 3.6 s tall and 2.5 s wide on this Mac with the generated 4-second test list at the default x264 preset. The whole suite of 469 tests passes in 10 min 15 s (615 s; the `run-with-timeout 1500` bound was not reached).

## Task commits

| Task | Name | Commit |
|------|------|--------|
| 1 (tracer) | Two-shot cut list to a finished reel and its proof sheet, both shapes | d332bec |
| 2 RED | failing tests for strict reading and the clips block | c2c6230 |
| 2 GREEN | strict reader, `clips_problems`, the three settings | 90e8e46 |

The frame, crop and plan tests and `test_touching_shots_of_one_clip_cut_cleanly` already passed on arrival because the tracer's arithmetic was right; they were added in the RED commit as proof, not as new behaviour. The remaining 27 new tests failed first and pass now.

## Deviations from Plan

### Tracer (Task 1): five small departures from the plan's wording

None of these changes what the plan promised; each is a smaller or neater route to the same result.

1. **`plan.seek(start_frame)` added.** The plan names no such function. A shot's fast seek and exact trim are one calculation shared by `video` and `sound`, so it lives once in plan.py and the two cannot disagree.
2. **`plan.shape_of` is the real implementation and `check.shape_of` wraps it.** The plan's interface list names `check.shape_of`; plan.py needs the same lookup and cannot import check (check imports plan), so the code sits in plan.py and check keeps the promised name.
3. **`structure_problems` already refuses a bad `focus_x` or `focus_y`, and a `clips` entry without a string `file` and a number `seconds`.** The plan describes it only as a guard until the schema arrives in plan 04. Without these refusals the crop and clips rules would meet values they cannot use. Plan 04 replaces the guard with the schema.
4. **`video.final_command` takes an optional `canvas=None`.** The plan's signature has no canvas argument. It lets the final encode be told the frame size when the reel is stepped down by join.fit.
5. **`make_proof` returns a sentence, and the reel is kept if proof sheets fail.** The plan's signature leaves the failure case open. A reel that is built and checked is never thrown away because a picture of it could not be drawn; the closing sentences say the proof sheets are missing.

### Task 2

None - Task 2 executed as written. One small choice inside it: `shown()` (the cleaner for list text) now cuts at CUTLIST_ECHO_CHARS, while the path in "There is no cut list at ..." goes through `normalize.clean_text` directly so a long temporary-folder name is not cut.

### Auto-fixed Issues

None.

## Authentication gates

None. The tracer checkpoint was a human-verify; the answer ("4passed in 10.86s. approved, both") approved the tracer.

## Known Stubs

None. `window_start`, `window_end` and `move` in the plan dict hold the full-canvas rectangle and "none" until plan 05 adds moves; they are deliberate placeholders with a documented owner, not data wired to the screen.

## Threat Flags

None. All new surface is covered by the plan's threat model: T-4-03 (list reading, now complete with the byte cap, number and name checks, depth and echo cut), T-4-02 (working and photo copies must be plain names of files directly in the work folder, checked in `clips_problems` through `look.working_facts` and `plain_file`), T-4-01, T-4-04, T-4-05 and T-4-07 (tracer).

## Self-Check: PASSED

- Files found: v2r/render/__init__.py, plan.py, check.py, video.py, sound.py, proof.py, tests/test_render_tracer.py.
- Commits found: d332bec, c2c6230, 90e8e46 on stage-16-render.
- `uv run pytest tests/test_render_tracer.py -q`: 38 passed. Full suite: 469 passed.
