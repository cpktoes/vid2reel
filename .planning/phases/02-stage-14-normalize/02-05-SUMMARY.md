---
phase: 02-stage-14-normalize
plan: "05"
subsystem: video-processing
tags: [ffmpeg, normalize, refusals, safety, doctor]

requires:
  - phase: 02-stage-14-normalize
    provides: plan 01 normalize command and manifest, plan 02 doctor.missing_ffmpeg_features(), plan 04 colour conversion
provides:
  - "one plain sentence per file that is too big, missing, unreadable, unconvertible or already in the work folder; the others carry on"
  - "skipped files keep their letter and have a manifest entry (status skipped, sentence, detail)"
  - "a whole-run stop with a sentence asking for fewer clips when the work folder runs out of room"
  - "check_ffmpeg(): normalize refuses to start if the computer's FFmpeg lacks a piece doctor lists"
  - "proof that originals are never changed and that working copies carry no location or device tags"
affects: [02-06, 02-07, 02-08, stage-15, stage-16]

actuals:
  tokens: 7800
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Refused exception for per-file refusals; one broad catch at the per-file boundary so nothing stops the others"
    - "checks run before any decode: found, not in the work folder, size by os.stat, then readable"

key-files:
  created: []
  modified: [v2r/normalize.py, tests/media.py, tests/test_normalize.py]

key-decisions:
  - "A file whose working name (such as A.mp4) is already taken by an original lying in the work folder is skipped as not converted, so the original can never be overwritten"
  - "The attachment-count setting is never read by normalize; it stays in settings.py as the measured fact only"

requirements-completed: [NORM-05, NORM-06, NORM-07, NORM-08]

duration: 25min
completed: 2026-10-13
status: complete
---

# Phase 2 Plan 05: Polite refusals, untouched originals and the FFmpeg start-up check Summary

**A file that is too big or cannot be read gets one plain sentence naming it exactly as sent, keeps its letter, and never stops the others; originals are proven untouched; and normalize stops before touching anything if FFmpeg lacks a piece.**

## What this does, in plain English

- If she sends something that is not a clip (a text file, a zero-byte file, a sound-only recording), the chat can now say, for example, "The second file, notes.mov, could not be read as a video or a photo." The other files still convert. A file over the size limit gets "The second file, big.mov, is 401 MB, over the 400 MB limit, so it was left out; a way to shrink clips comes in a later stage." A file that is not there at all gets "was not found."
- A skipped file keeps its letter (so B stays B even if B is skipped) and has an entry in the manifest with its sentence, so nothing is ever dropped silently. Each sentence is also printed as it happens.
- The command still says exit 0 when at least one file converted, 1 when none did. If every file is skipped, the manifest is still finished.
- If the work folder runs out of room, the run stops with "The work folder ran out of room, so the run stopped; please send fewer clips." and the manifest records that it did not finish.
- The number of files in one message is not checked: ten arrived in testing, so normalize simply tries them all.
- Originals are only ever read. Tests compare each original's fingerprint, size and modification time before and after, including read-only files. A file lying inside the work folder is refused and left exactly as it was, and no working copy can overwrite it.
- At the start, normalize asks doctor's lists whether this computer's FFmpeg has every encoder, filter and decoder it needs. If not, it stops with one sentence naming what is missing, before the work folder is touched. A test also confirms every filter normalize builds is on doctor's list.
- Working copies carry no location, make or model, and the manifest holds none of them.

## Task Commits

1. **Task 1: one sentence per refused file, letters kept, exit codes, out-of-room stop** - `242c093` (feat; also contains the code of Task 2's start-up check, which sat in the same functions)
2. **Task 2: tests proving originals untouched, doctor check, no location tags** - `93b9b9b` (test)

## Deviations from Plan

**1. [Rule 3 - Blocking] The first normalize test put its clip in the work folder**
- **Found during:** Task 1
- **Issue:** the new rule that a file inside the work folder is left alone made the very first end-to-end test refuse its own clip.
- **Fix:** the test now keeps the clip in a separate folder from the work folder.
- **Files modified:** tests/test_normalize.py
- **Commit:** 242c093

**2. [Rule 2 - Missing critical] An original named like a working copy could be overwritten**
- **Found during:** Task 1
- **Issue:** if an original lying in the work folder were called A.mp4 and a different file came first, the finished copy of the first file would have been moved over that original.
- **Fix:** a file whose working name is already taken is skipped as "could not be converted." with that reason as detail; a skipped file's leftover .part file is only removed if it is not one of the run's own inputs. A test covers it.
- **Files modified:** v2r/normalize.py, tests/test_normalize.py
- **Commit:** 242c093, 93b9b9b

**3. Commit split.** `check_ffmpeg()` was written together with the per-file code in Task 1's commit rather than in Task 2's; Task 2's commit holds its tests. Tests were written after the code in this plan rather than red first, because the behaviour was specified in full and every test was checked to be able to fail (for example by the doctor and ENOSPC monkeypatches).

Otherwise the plan was executed as written.

## Known Stubs

None. The photo half of the "could not be read as a video or a photo" sentence is plan 06's: until it lands, a photo is refused with that same sentence.

## Threat Flags

None. No new network or trust-boundary surface; the plan's threats T-2-03, T-2-04, T-2-05, T-2-07, T-2-08 and T-2-12 are mitigated and tested.

## What to test from a phone before merging

The video itself is unchanged by this plan, but the refusals are what she will see. When you test on a phone, attach one real clip, plus one file that is not a video (for example a text file renamed to end in .mov), and ask the chat to run normalize. Look for the chat telling you, in plain words, that the second file could not be read while the first was converted, and for the manifest listing both. The full video check is still plan 08's phone test.

## Self-Check: PASSED

- v2r/normalize.py, tests/media.py and tests/test_normalize.py exist and contain the new code
- commits 242c093 and 93b9b9b exist
- `uv run pytest -q`: 107 passed
