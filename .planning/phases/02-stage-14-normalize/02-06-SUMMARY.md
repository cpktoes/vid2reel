---
phase: 02-stage-14-normalize
plan: "06"
subsystem: normalize
tags: [photos, heic, pillow, pillow-heif, still-clip, ffmpeg-loop]

requires:
  - phase: 02-stage-14-normalize
    provides: plan 01 (working_size, run_ffmpeg, part_path, manifest), plan 05 (convert_one, Refused, sentences), plan 03 (Pillow and pillow-heif)
provides:
  - "Photos (HEIC, JPEG, PNG) become a PHOTO_SECONDS still clip like any other clip, in both shapes"
  - "The full-size upright photo kept as work/LETTER-photo.jpg, with no EXIF, location or device tags"
  - "Photo manifest entries: kind photo, original (stored_size, upright_size, orientation, shot_at), photo (file, size)"
affects: [02-07, 02-08, stage-15, stage-16]

actuals:
  tokens: 5100
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Pillow and pillow-heif are imported inside photo_libraries() only; importing v2r.normalize never loads them"
    - "A photo's still clip is made by scaling once and repeating the frame with the loop filter, never -loop 1"

key-files:
  created: []
  modified: [v2r/normalize.py, tests/media.py, tests/test_normalize.py]

key-decisions:
  - "Pillow looks at every file before ffprobe does, so a JPEG never goes down the video path and a HEIC (which the sandbox FFmpeg cannot open) is still read"
  - "FFmpeg only ever reads the upright JPEG copy, never the original photo"

requirements-completed: [NORM-03]

duration: 25min
completed: 2026-10-13
status: complete
---

# Phase 2 Plan 06: Photos Summary

HEIC, JPEG and PNG photos are read with Pillow, turned upright once, saved full size as a clean JPEG, and turned into a 4-second still clip with silent sound, in both tall and wide.

## In plain English

When she attaches a photo, it now becomes a 4-second clip like any other, so later steps only ever deal with clips. Her iPhone photos are HEIC, which the sandbox's video tool cannot open on its own, so the picture library reads them first. Next to the clip, the full-size photo is kept as, for example, C-photo.jpg, so Stage 16's slow push-in has real detail to zoom into. That copy has no location and no camera make or model, because the finished reel is posted publicly. If the picture library ever fails to install on the phone, only the photos are skipped (each with one plain sentence); videos in the same run still convert.

## What was built

- `photo_libraries()` loads Pillow and pillow-heif only when a file is checked, and switches on HEIC reading.
- `read_photo()` opens the file, records its orientation note and date taken (as `shot_at`, such as 2026-10-10T18:03:24), turns it upright exactly once, makes it RGB, converts an embedded colour profile to sRGB (keeping the colours and adding a note if the profile cannot be read), and saves a JPEG at `PHOTO_JPEG_QUALITY` with no EXIF and no profile data. Pillow's decompression-bomb guard is left at its default.
- `photo_graph()` and `photo_command()` build the still clip: scale the big picture once, then repeat the frame with the `loop` filter (never `-loop 1`), plus a silent stereo 48 kHz sound track. A 4000x3000 photo converts well under 15 seconds.
- `encoder_options()` now holds the encoder settings shared by clips and photos; `video_command` uses it with the same list in the same order.
- `convert_one` asks Pillow first; `convert_photo()` finishes a photo's entry. A leftover photo copy is removed if the still clip cannot be made.
- Test helpers `make_photo` and `corner_mean_image` in tests/media.py generate JPEG, PNG and HEIC photos on the spot. No photo is committed.

## Tests (130 pass in total, 23 new)

Both shapes where a photo is converted: JPEG orientation 6 gives an upright copy (the white box moves from top-left to top-right once) and a correct still clip; a large photo is fast; importing `v2r.normalize` does not import PIL; HEIC opens; an RGBA PNG becomes an RGB copy; an ICC-profiled JPEG keeps its colours; a missing library skips only the photo with the agreed sentence while a clip in the same run converts; the copy and the manifest carry no make, model or location; clip, photo, clip stay A, B, C in order; an empty .jpg is skipped as "could not be read as a video or a photo."; a photo exactly at the cap keeps its size, a 301x401 photo gives a 300x400 still and nothing is enlarged; every filter the photo graph uses is on doctor's list.

## Deviations from Plan

None - plan executed exactly as written. Task 2 needed no code change: its tests passed against Task 1's code, so Task 2 has one test commit and no feature commit.

## Test from a phone

This changes how photos are turned into video, so please test from a phone before merging. Attach one HEIC photo (and one clip) to the chat, choose tall, and check:
- The photo appears as a 4-second still with no sound, in the order you attached it. Look at the very start (0:00) and the end (0:04): it should be the same steady picture with nothing flickering or jumping.
- It is upright (not sideways or upside down), including a photo taken holding the phone sideways.
- Colours look like the original photo, not washed out or oversaturated, at about 0:02.
- Ask the chat for the saved photo copy; it should be full size and should open upright.
- If you can, look at that copy's details in the Photos app: it should show no location and no camera.
Also confirm the skill's pip install of the pinned requirements succeeds (Research A2) and that the whole run stays well under the 2-minute limit.

## Known Stubs

None.

## Threat Flags

None. T-2-03 (size cap before Pillow opens the file, default bomb guard, any Pillow error becomes the could-not-be-read sentence), T-2-05 (no EXIF or ICC in the copy, proven by `test_photo_copy_has_no_exif_location`), T-2-02 (copy named LETTER-photo.jpg, never from the input name) and T-2-14 (lazy import, one sentence per photo) are all applied.

## Commits

- e54d077: test(02-06) failing tests for the JPEG photo path
- db16158: feat(02-06) JPEG photo to upright copy and still clip
- 9295efb: test(02-06) HEIC, PNG, ICC, no location data, mixed order, size edges

## Self-Check: PASSED
