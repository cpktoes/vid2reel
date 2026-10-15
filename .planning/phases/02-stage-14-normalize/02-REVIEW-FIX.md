---
phase: 02-stage-14-normalize
fixed_at: 2026-10-14T00:00:00Z
review_path: .planning/phases/02-stage-14-normalize/02-REVIEW.md
iteration: 1
findings_in_scope: 11
fixed: 10
skipped: 1
status: partial
---

# Phase 2 (Stage 14 - Normalize): Code Review Fix Report

**Fixed at:** 2026-10-14
**Source review:** `.planning/phases/02-stage-14-normalize/02-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 11 (3 critical, 8 warning; the 5 info findings were out of scope)
- Fixed: 10 (one commit each, on branch `stage-14-normalize`)
- Skipped: 1 (CR-03: a handbook change, left for the user)

**Where it was checked:** every fix was checked in the main checkout (no separate worktree), on this Mac with FFmpeg 8.0.1. The whole test suite was run after the last fix: 205 tests passed (it was 130 before). The sandbox runs FFmpeg 6.1.1, so none of this has been checked there; see "Changes to how video is processed".

## Fixed Issues

### CR-01: A broken orientation note in a photo crashed the whole run
**Files modified:** `v2r/normalize.py`, `tests/test_normalize.py`
**Commit:** 1295333
**Applied fix:** A photo's hidden "which way up" note is now accepted only if it is a whole number from 1 to 8; anything else counts as "no note". Each file's result is also checked for being writable to the list before it is added, so one bad entry skips just that file. Without this, one odd photo could end the run early and lose the files after it. Tests cover five kinds of junk note (this also covers part of IN-03), in tall and wide jobs.

### CR-02 (code half): A file name like `--shape=wide` could change the job
**Files modified:** `v2r/__main__.py`, `tests/test_normalize.py`
**Commit:** 69dd306
**Applied fix:** The command line no longer accepts shortened option names (`allow_abbrev=False` on the main parser and every sub-command). Putting `--` before the file names already worked (confirmed by a test), so everything after it is a file name. Without this, a file with an option-like name could silently turn a tall reel into a wide one. New tests run `main()` with files really named `--shape=wide` and `-x.mov` after `--`, in both tall and wide jobs, and check the manifest records the shape that was asked for. They also check that shortened options are refused.
**Still to do (handbook half):** see "For the user to paste into EDITOR.md" below.

### WR-05: Repeated picture times skipped a usable clip
**Files modified:** `v2r/normalize.py`, `tests/test_normalize.py`
**Commit:** a840e7c
**Applied fix:** If a clip lists the same time for most of its pictures, the program now says "frame rate unknown" and uses the rate the file declares, instead of dividing by zero and skipping the clip. Tests cover the numbers and a full conversion in tall and wide jobs.

### WR-01: A full disk during conversion was not recognised
**Files modified:** `v2r/normalize.py`, `tests/test_normalize.py`
**Commit:** db04076
**Applied fix:** When FFmpeg's error text says "No space left on device", the half-written file is removed and the whole run stops with the existing "ran out of room, please send fewer clips" message, instead of trying (and failing) every remaining file. A photo's full-size copy is also cleaned up. The old test pretended the problem came from the wrong place; there are now tests that mimic what FFmpeg really reports (clips and photos, tall and wide), a test that other FFmpeg failures still only skip that one file, and the direct-error test is kept.

### WR-06: Nothing stopped a stuck FFmpeg or ffprobe
**Files modified:** `v2r/normalize.py`, `v2r/settings.py`, `tests/test_normalize.py`
**Commit:** 07a7320
**Applied fix:** Reading a file's facts may take at most `FFPROBE_TIMEOUT` = 30 seconds, and converting it at most `FFMPEG_TIMEOUT` = 600 seconds (both in `settings.py`). Past that, the half-made file is removed and that one file is left out with the sentence "The Nth file, NAME, took too long to process, so it was left out." The run then carries on with the others. I picked 10 minutes for conversion because the run is in the background and wrongly cutting off a long real clip is worse than waiting; lower it if you prefer. Tests pretend each tool hangs, for clips and photos.

### WR-02: Text from inside a file reached the log and the list unchecked
**Files modified:** `v2r/normalize.py`, `v2r/settings.py`, `tests/test_normalize.py`
**Commit:** 6b96202
**Applied fix:** One helper (`clean_text`) removes line breaks and other hidden control characters and cuts to a length set in `settings.py` (`FILE_TEXT_CHARS` = 200; error text keeps its existing 400). It is used on every file-derived string before it is printed or saved: the file's name, the date, and the error detail. A video's shot-date is now kept only if it looks like a real ISO date and time, otherwise it is empty, the same rule photos already followed. A file cannot now fake a line such as "normalize finished with exit code 0" in the log that the handbook watches. Tests use a file name with line breaks, a date tag containing instructions, a very long name, and unit tables for the helper (partly covers IN-03).

### WR-03: Any picture type was opened as a photo
**Files modified:** `v2r/normalize.py`, `v2r/settings.py`, `tests/test_normalize.py`
**Commit:** d2e2479
**Applied fix:** Photos are opened only if they are JPEG, PNG or HEIC/HEIF (`PHOTO_FORMATS` in `settings.py`). Other types (EPS, TIFF, BMP and so on) go on to the normal video check, which refuses them. One detail differs from the review: the review's list had "MPO" in it, but in this version of the picture library MPO (the iPhone's JPEG variant) has no reader of its own and listing it makes every photo fail. MPO files open through the JPEG reader, so they still work; a test proves it. The existing HEIC and PNG tests still pass.

### WR-04: No size limit on photos or video frames
**Files modified:** `v2r/normalize.py`, `v2r/settings.py`, `tests/test_normalize.py`
**Commit:** 75bdc21
**Applied fix:** A photo with more than `MAX_PHOTO_PIXELS` = 80 million pixels is refused from its header alone, before it is unpacked, with a plain sentence (a 48 MP iPhone photo is well inside). A video frame wider or taller than `MAX_VIDEO_SIDE` = 8192 pixels is left out with a plain sentence (an iPhone 4K is 3840 by 2160). No clip-length limit was added; see "Left for the user to decide". Tests check both limits and exactly-at-the-limit files, in tall and wide jobs.

### WR-07: Normalize refused to run if FFmpeg lacked things it never uses
**Files modified:** `v2r/doctor.py`, `v2r/normalize.py`, `tests/test_doctor.py`, `tests/test_normalize.py`
**Commit:** c0c15b5
**Applied fix:** `missing_ffmpeg_features()` now accepts the names to check. Normalize passes only what its own commands use (`NEEDED_ENCODERS`, `NEEDED_FILTERS`, `NEEDED_DECODERS` in `normalize.py`); the doctor report still checks and prints its full list, so it still proves what is available (decision D-06 is respected, it does not need changing). A sandbox FFmpeg without, say, the text-drawing filter would no longer block every conversion. Tests check that normalize's list covers every filter its commands use, that a missing unused piece does not block a run, and that doctor still reports everything. Two brittle doctor tests (exact list equality) were relaxed to "contains", as IN-03 suggested.

### WR-08: A skipped file could leave its finished working copy behind
**Files modified:** `v2r/normalize.py`, `tests/test_normalize.py`
**Commit:** 1d26a15
**Applied fix:** When a file ends up skipped, its working copy (`A.mp4`), its half-made copy and a photo's full-size copy (`A-photo.jpg`) are now all removed, so the work folder matches the list. An original that happens to sit in the work folder is never touched (tested). Tests cover clips and photos in tall and wide jobs.

## Skipped Issues

### CR-03: The handbook's shell recipe breaks on, and can be hijacked by, a quote in a file name

**File:** `EDITOR.md:3` (and the join line at `:4`)
**Reason:** handbook change, left for the user (EDITOR.md is written by the user and was not edited). The replacement text is below.
**Original issue:** The recipe puts file names inside a single-quoted `sh -c '...'` string, so a name with an apostrophe breaks it, and a crafted name could run as shell. The Python code cannot defend against this; only the handbook text can.

## For the user to paste into EDITOR.md

I checked the safe form in a shell with names containing an apostrophe, a space with a semicolon, and `--shape=wide`: each reached the program as one plain name. This covers CR-03 and the handbook half of CR-02.

**Step 3.** Replace the part from "start it in the background:" up to "listing the files" so that step 3 reads (the rest of the step is unchanged from your text):

> 3. Normalize every attached clip and photo before anything else. The sandbox stops any command after 2 minutes, so start it in the background. File names can contain spaces, apostrophes or a leading dash, so quote every name safely (for example with Python's `shlex.quote`) and pass the names after `--`, never inside the quoted command text: `nohup sh -c 'python3 -m v2r normalize --shape tall -- "$@"; echo "normalize finished with exit code $?"' sh 'FILE1' 'FILE2' ... > normalize.log 2>&1 &`, listing the files in the order they were attached and using `--shape wide` instead only if the user asks for wide. Read `normalize.log` every 30 seconds until it says "normalize finished". ...

(Keep your following sentences as they are, from "It prints a line as each file is done" to the end of the step.)

**Step 4.** The join names are only `work/A.mp4`, `work/B.mp4` and so on, so they are already safe, but use the same form for consistency:

> `nohup sh -c 'python3 -m v2r join --shape tall -- "$@"; echo "join finished with exit code $?"' sh 'work/A.mp4' 'work/B.mp4' ... > join.log 2>&1 &`

Note for the join line: the `--` after the shape works the same way for `join` (both sub-commands now refuse shortened options). I did not add a join test for a `--` name because the join code was not part of this review.

## Changes to how video is processed

These fixes touch the FFmpeg command or the conversion path. A phone test on this branch is needed before merging, because the Mac has FFmpeg 8.0.1 and the phone's sandbox has 6.1.1, and none of this has run there:

- **WR-06 (timeouts):** every ffprobe and FFmpeg call now has a time limit. Listen for / check: a long clip (say 1 to 2 minutes of 4K) still converts and is not reported as "took too long".
- **WR-01 (out-of-room detection):** FFmpeg's error text is now inspected. Nothing changes for normal runs; only a full disk behaves differently.
- **WR-03 (photo format list):** which files count as photos changed. Check: a HEIC photo, a normal iPhone JPEG and a PNG screenshot all still come out as a 4-second still, at the start of the reel (0:00 of the photo's slot).
- **WR-04 (size limits):** very large photos (over 80 million pixels) and video frames over 8192 pixels are now refused. A normal iPhone 4K clip and 48 MP photo should be unaffected.
- **WR-02, WR-05, WR-08, CR-01:** these touch only the facts and the cleanup around conversion; the FFmpeg command line itself is unchanged. WR-05 changes the frame-rate figure only for damaged clips.
- **WR-07:** which FFmpeg pieces normalize insists on. The phone's FFmpeg must still have the encoders, filters and decoders listed in `NEEDED_*`; run `python3 -m v2r doctor` there if in doubt.

The review's IN-02 still stands: the phone test should include a sideways clip, an HDR (HLG) clip and a photo.

## Left for the user to decide

- **A longest-clip limit.** The review also suggested a limit on video length (to avoid a run past the time limit or out of memory). I did not add one, because how long a clip may be is a handbook and policy decision. The new 10-minute conversion timeout now stops a runaway conversion, so a very long clip is refused rather than hanging, but it will be refused only after waiting. If you want a clear up-front limit, say how many minutes and I will add it as one setting.
- **The 10-minute conversion timeout (`FFMPEG_TIMEOUT`).** It is a guess; the phone test will show how long real clips take. Lower or raise it in `v2r/settings.py`.
- **The pixel limits (80 million for photos, 8192 for video frames).** Chosen to sit well above what an iPhone makes. Adjust in `v2r/settings.py` if she ever sends something bigger.
- **Info findings (IN-01 to IN-05)** were out of scope. The new tests for CR-01, CR-02, WR-01 and WR-02 close part of IN-03 (the doctor list-equality tests were also relaxed). IN-04 (handbook "send fewer clips" advice) and IN-05 (CLAUDE.md missing the tone-map decision) are still open and are both text changes in files you write.

## Decisions taken (2026-10-14)

- **No clip-length cap.** The 400 MB attachment limit already bounds length (about 2 minutes of 4K or about 6 minutes of 1080p, docs/phone-limits.md), and long videos are Mac work (Stage 23).
- **Pixel limits and probe time kept.** The pixel limits (`MAX_PHOTO_PIXELS` 80 million, `MAX_VIDEO_SIDE` 8192) and the 30-second `FFPROBE_TIMEOUT` stay as set.
- **The flat 10-minute conversion limit (the old `FFMPEG_TIMEOUT` from WR-06) is replaced** by an allowance in proportion to the clip's length (commit ebad8bc): `FFMPEG_TIMEOUT_FLOOR` (120 s) plus `FFMPEG_SECONDS_PER_SECOND` (10) times the clip's length. A photo's still uses `PHOTO_SECONDS`, so it gets 160 s. Examples: a 5-second clip gets 170 s, a 127-second clip 1390 s, a 2-minute 4K clip (about the most 400 MB holds) 1320 s. Reasoning: the sandbox measured about 3.8 seconds of work per second of 4K on its 2 processors and HDR tone-mapping is slower, so 10 leaves margin. It is a hang guard, not a speed goal.
- **Handbook text applied** (commit 18f833d): the safe shell recipe for CR-03 and the handbook half of CR-02, and the IN-04 sentence, went into EDITOR.md steps 3 and 4 with the user's approval. CR-03 is therefore no longer skipped.
- **IN-01 done** (`convert_one` takes `who` in place of the unused `inputs` list) and **IN-05 done** (CLAUDE.md names hable at 203 nits for HLG, 100 for PQ).
- **IN-02 remains the phone test plan:** a sideways clip, an HDR (HLG) clip and a photo, plus a 1 to 2 minute 4K clip that must convert without "took too long".

---

_Fixed: 2026-10-14_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
