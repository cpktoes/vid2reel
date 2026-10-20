---
phase: 04-stage-16-cut-list-and-renderer
plan: "09"
subsystem: render
tags: [render, cover, size-limit, golden, determinism, tests]
requires: ["04-05", "04-06", "04-07", "04-08"]
provides:
  - "v2r/render/plan.py: cover_frame(), and the plan's cover_frame"
  - "v2r/render/proof.py: make_cover(), cover_path(), NO_COVER_LIBRARY, COVER_NOT_MADE"
  - "render writes WORK/{reel stem}-cover.jpg beside every reel and says which frame it is"
  - "tests/media.py: make_split_clip()"
  - "tests/test_render_golden.py: golden renders of both approved examples in both shapes, determinism, cover, size limit, failure safety"
affects: [04-10, 04-11]
actuals:
  tokens: 21000
  tasks: 2
  commits: 3
tech-stack:
  added: []
  patterns:
    - "The cover is read from the finished reel with look's grab_stills and saved as .part.jpg then os.replace, whole or not at all"
    - "Golden tests compare worked-out colours and frame luma, never a hard-coded hash; 'same video' is FFmpeg's md5 of the decoded streams"
key-files:
  created:
    - tests/test_render_golden.py
  modified:
    - v2r/render/plan.py
    - v2r/render/proof.py
    - v2r/render/__init__.py
    - tests/media.py
    - tests/test_render_sound.py
key-decisions:
  - "make_cover takes the reel's length as an optional last argument so FFmpeg's time allowance follows the reel, as the proof sheets' does"
  - "A cover that cannot be made (no Pillow, or FFmpeg fails reading the frame) returns a sentence and the reel is kept, the same rule as the proof sheets"
  - "Golden reel fixtures are built once per shape for the whole test module, so the two examples render once and several tests read them"
requirements-completed: [CUT-03, CUT-07, CUT-09]
duration: "about 45 min, plus two full suite runs (13 min stopped at one failure, then 16 min 05 s)"
completed: 2026-10-19
status: complete
---

# Phase 4 Plan 09: Cover, Size Limit and Golden Renders Summary

Render now saves a cover still beside every reel, and both approved example reels are rebuilt in the tests from made-up clips and checked frame by frame and colour by colour, including that the same list always gives the same video.

## What changed, in plain English

- **A cover still beside every reel.** After the reel is finished, render saves a picture named like the reel with `-cover` on the end (for example `reel-tall-20261019-164419-cover.jpg`). It is the moment the cut list names (a shot number and a second into that shot), or the very first frame when the list names none, which is what the platforms show by default. The picture is the reel's own frame size. If the named second lands past the shot's last frame, the shot's last frame is used. Render says which frame it chose: "The cover still is ...-cover.jpg, the frame at 2.4 seconds."
- **The cover follows its shot.** It is tied to the shot number, not to a time on the reel, so if the reel is shortened or reordered the cover is still that shot.
- **Nothing is half-made.** The cover is written under a temporary name and given its real name only when whole. A reel that fails part-way leaves no reel, no half-made file and no scratch folder, and the previous reel's proof sheets and cover are exactly as they were (tested by comparing the files' fingerprints before and after). A cover that cannot be made does not delete the reel; render says so in one sentence.
- **Long reels.** This already worked from earlier plans and is now tested in both shapes: when a reel is too long for the full frame to come back under the size limit, render makes it smaller (720x1280 tall, 1280x720 wide) and says so naming both sizes; the proof sheets and the cover follow the smaller size. A reel too long even for the smallest step is refused by `check` with join's own sentence before anything is built, and the work folder is left unchanged. A finished file over the limit is deleted with a sentence.
- **The big test.** Your two example reels, the 20-second tall one (seven shots over four clips and a photo) and the 38-second wide one (a talking head with two cut-aways), are rebuilt at a quarter of their length at the real frame sizes from clips made on the spot with known colours: a clip whose brightness says which frame it is, a clip split in two colours, flat colours, and a striped photo. Each is checked for the right number of frames, the right length and size, H.264 picture and AAC sound, the index at the front of the file, the size limit, the loudness within 0.3 of the -14 target and the right number of proof sheets. Then every shot's middle shows the colour worked out independently (the clip's colour plus that clip's touch-up numbers, and the correct half of the split clip for the shot's focus point), and the first and last pictures of the frame-index shots are exactly the right frames. Building the same list twice gives the same decoded pictures and sound (checked with FFmpeg's fingerprint of the decoded video and of the decoded sound, not of the file, since two encodes of the same video are not byte-identical).

## Golden render numbers (this Mac, FFmpeg 8.0.1, ultrafast preset, real canvas)

| Shape | Segments | Frames | Length | Size | Loudness | Proof sheets | Render time |
| ----- | -------- | ------ | ------ | ---- | -------- | ------------ | ----------- |
| tall (1080x1920) | 7 | 153 | 5.1 s | 0.6 MiB | -14.0 LUFS | 2 | about 6.3 s |
| wide (1920x1080) | 5 | 286 | 9.5 s | 2.4 MiB | -14.0 LUFS | 1 | about 6.3 s |

Measured colours matched the worked-out ones to within one code value on every shot except the photo shots, which were off by one in Y (147 against 148, 148 against 149), well inside the allowed 2. The frame-index shots matched exactly on first, middle and last frames.

## What to look for on the phone

Nothing was watched here; the tests measure pictures and sound numerically. On a phone-rendered reel and its cover:

- **The cover still.** Open `reel-...-cover.jpg` beside the reel. With a cover in the cut list it must be the picture from the shot you named, that many seconds in (for example, the laugh in shot 4 one second after it starts), and sharp. With none named it must be the reel's very first picture. It should be the same shape as the reel (tall for a tall reel, wide for a wide one), with no bars and no border.
- **The sentence.** After rendering you should see a line "The cover still is ..., the frame at N seconds." and the number should match where in the reel that moment is (shot start plus the seconds you named).
- **A long reel.** For a reel long enough to be made smaller, the sentence "so it was made at 720x1280 instead of 1080x1920" (or the wide equivalent) should appear, and the proof sheets and cover should look like the smaller reel. A reel beyond the last step is refused at `check` with "can be at most ...", and the work folder should have no new file.
- **Shots and cuts.** Open the proof sheets: each shot's first and last picture, in order, none black, none cropped onto a shoulder.
- **Repeatability.** Rendering the same cut list twice on the phone should give two reels that look and sound the same; if one differs at a cut or in loudness, say at what time.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Existing sound tests read the wrong closing sentence**
- **Found during:** the first full-suite run (Task 2 verification)
- **Issue:** `tests/test_render_sound.py` read the "Made ..." sentence as `sentences[-2]`; the new cover sentence now comes after the proof-sheet sentence, so that sentence is third from the end.
- **Fix:** the four reads now use `sentences[-3]`.
- **Files modified:** tests/test_render_sound.py
- **Commit:** f73fa00

### Other notes

- The plan's step 2 gave `make_cover(reel_path, frame, size, cover_path)`; an optional fifth argument `seconds` (the reel's length) was added so the FFmpeg time allowance follows the reel's length, and a second failure sentence (`COVER_NOT_MADE`) covers FFmpeg failing to read the frame. Both are in line with how `make_proof` behaves.
- Task 1 and Task 2 were both written test-after-code rather than red-first; the golden tests were confirmed to be sensitive (the printed expected and found values agree to 0 to 1 code values, and a frame one off would read 8 away).
- `join.fit` was already used by `check` and `render` from earlier plans, so the stepped-down and refused sizes needed tests only, not new code.
- `plan.cover_frame` is the shared rule; the closing sentence reports `cover_frame / fps`.

## Tests

- `tests/test_render_golden.py`: 27 tests, both shapes. Cover (default first frame, follows its shot, clamping, plan carries it), step-down size and sentence, refusal before building, over-the-limit deletion, failure leaving nothing behind and the previous outputs untouched, only the expected files left, both golden renders, split clips following the focus, same list same video (decoded md5 of picture and of sound, plan and commands equal as data), times inside one frame planning the same video, a one-segment list rendering the same twice. No hash is written into the file and no media is committed (`git status` shows none).
- Full suite: `944 passed in 965.02s (0:16:05)`. An earlier run of the whole suite stopped at the one test fixed above after 13 min 04 s with 836 passed.

## Known Stubs

None.

## Threat Flags

None. T-4-05 (cover and reel written as .part and renamed only when whole; a failure leaves no part and no scratch; previous proof sheets and cover left alone), T-4-03 (check refuses an overlong reel with join's sentence; a file over the limit is deleted) and T-4-09 (all media in tmp_path; no media in the working tree) are mitigated and tested.

## Backstop

The same list giving the same decoded frames on the sandbox's FFmpeg 6.1 as on this Mac's 8.0.1 was measured once in scratch by the research; the phone render's proof sheets and reel are the only check of it here. Please test from a phone on branch `stage-16-render` before anything merges.

## Self-Check: PASSED

Files found: v2r/render/plan.py (cover_frame), v2r/render/proof.py (make_cover), tests/media.py (make_split_clip), tests/test_render_golden.py. Commits found: 644974f (Task 1), 987f469 (Task 2), f73fa00 (sound test fix).
