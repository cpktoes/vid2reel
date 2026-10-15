---
phase: quick-261014-rvv
plan: 01
subsystem: normalize
tags: [timeouts, handbook, shell-safety, stage-14]
status: complete
requirements: [WR-06, IN-01, CR-03, CR-02, IN-04, IN-05]
key-files:
  modified:
    - v2r/settings.py
    - v2r/normalize.py
    - tests/test_normalize.py
    - EDITOR.md
    - CLAUDE.md
    - .planning/phases/02-stage-14-normalize/02-REVIEW-FIX.md
decisions:
  - "Conversion allowance is 120 s plus 10 s per second of video (a photo's still: 160 s); no clip-length cap"
  - "EDITOR.md steps 3 and 4 pass each shell-quoted file name after -- through \"$@\""
actuals:
  tokens: 30000
  tasks: 3
  commits: 3
completed: 2026-10-14
---

# Quick task 261014-rvv: Stage 14 review follow-ups, safe handbook commands

A long clip is no longer cut off by a flat 10-minute guess, and the handbook's commands can no longer be broken by an odd file name.

## What changed, in plain English

**1. Time to convert now grows with the clip (commit ebad8bc).** Before, every file got a flat 10 minutes before it was given up on as stuck. Now a clip gets 2 minutes plus 10 seconds for every second of video: a 5-second clip gets 170 seconds, a 127-second clip gets 1390 seconds. A photo gets 160 seconds. A short clip that hangs is noticed sooner, and a long real clip is not cut off. The two numbers (`FFMPEG_TIMEOUT_FLOOR` and `FFMPEG_SECONDS_PER_SECOND`) are in `v2r/settings.py` with their units. The sandbox measured about 3.8 seconds of work per second of 4K video, so 10 leaves a wide margin (HDR colour conversion is slower than plain video). A stuck file still leaves out only that one file, with the same sentence as before, and leaves nothing half-made in the work folder. The tests cover both tall and wide and show the allowance getting larger for a longer clip.

Small tidy-up in the same commit (review finding IN-01): the convert step no longer takes a list it never used, and each file's sentence opening ("The first file, NAME,") is now built once instead of twice.

**2. Handbook commands are safe for any file name (commit 18f833d).** EDITOR.md steps 3 and 4 now hand each file name to the command as its own safely quoted item after `--`, instead of pasting names inside the quoted command text. A name with an apostrophe, a semicolon or a leading dash now reaches v2r as one plain name. I proved this with a throwaway check: the names `it's a clip.mov`, `x; touch HACKED` and `--shape=wide` arrived whole, in order, and nothing named HACKED was created. Only lines 3 and 4 of EDITOR.md changed (you authorised this edit). Step 3 now asks for shorter or fewer clips only when the log says it ran out of room; any other stop is shown to you as step 6 says.

**3. CLAUDE.md** now names the tone-map pick: hable at a nominal peak of 203 nits for HLG, 100 for PQ, picked by eye on 2026-10-13 (review finding IN-05). Nothing else in it changed.

**4. The Stage 14 fix report (commit 0d3f8e2)** has a new "Decisions taken (2026-10-14)" section recording these decisions: no clip-length cap, the pixel limits and 30-second probe time kept, the new proportional allowance, the handbook text applied, IN-01 and IN-05 done, and IN-02 (the phone test) still standing.

## Deviations from plan

None - the plan was executed as written. Two small notes: the out-of-room test was parametrised over tall and wide as the plan asked, and the video path passes a once-computed `allowance` to both FFmpeg attempts (the first try and the HDR fallback).

## Verification

- Full suite: 209 passed (205 before, 4 new: the allowance helper, growth with length in both shapes, the out-of-room test now in both shapes).
- `FFMPEG_TIMEOUT_FLOOR` is the only timeout name left in `v2r/` and `tests/`; `FFPROBE_TIMEOUT` is unchanged at 30.
- The quoting check for the new EDITOR.md recipe passed. The join command's file argument is positional, so `--` ends its options too.

## Phone test before merging

This changes how long a conversion may take before a file is left out, so test from her phone on branch `stage-14-normalize` before merging. Attach, in one chat, a 1 to 2 minute 4K clip, a sideways clip, an HDR (HLG) clip and a photo.

- In `normalize.log`, look for a "done in N s" line for every file and no "took too long" sentence.
- Check the `nohup` line Claude ran shows each file name in its own quotes after `--`.
- In the finished reel: the photo shows as a 4-second still at the start of its slot; the sideways clip fills the frame; the HDR clip's colours do not look flat or washed out from the moment it starts.

## Known stubs

None.

## Threat flags

None.

## Self-Check: PASSED

Commits ebad8bc, 18f833d and 0d3f8e2 exist on `stage-14-normalize`; all edited files are in place.
