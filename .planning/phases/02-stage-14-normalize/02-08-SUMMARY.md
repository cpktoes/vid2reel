---
phase: 02-stage-14-normalize
plan: "08"
subsystem: normalize
tags: [handbook, phone-test, push, privacy-scan, slow-motion, hdr, tall, wide]

requires:
  - phase: 02-stage-14-normalize
    provides: plans 01 to 07 (normalize for videos and photos, doctor report, photo libraries, tone-map pick)
provides:
  - "The user's normalize step in EDITOR.md (text written exactly as the user gave it), plus a corrected join step that uses the working copies"
  - "Branch stage-14-normalize on GitHub, with main untouched"
  - "A passed phone test on the branch: doctor, install, all four files done in tall and in wide, a tall reel and a wide reel made from the phone"
affects: [stage-15, stage-16]

actuals:
  tokens: 2500
  tasks: 3
  commits: 2

key-files:
  created: []
  modified: [EDITOR.md]

key-decisions:
  - "EDITOR.md got the normalize step by the write-exactly route (D-16): Claude wrote only the user's text"
  - "The join step now joins the working copies, in letter order, and leaves out any letter the manifest marks skipped"
  - "Phone attachments of slow-motion clips arrive pre-rendered at a steady 30 fps, so the 120/240 fps slow-motion flag does not fire from a phone"

requirements-completed: [NORM-02, NORM-03, NORM-04, NORM-08]

duration: phone test across 2026-10-13 to 2026-10-14
completed: 2026-10-14
status: complete
---

# Phase 2 Plan 08: Handbook lines, push and phone test Summary

The normalize step is in the handbook in the user's own words, the branch is on GitHub with main untouched, and the phone test passed in both shapes: all four files converted, the bright clip looked and sounded right, and a tall reel and a wide reel were made from the phone on the branch.

## In plain English

This was the plan that took the stage out of the Mac and onto the phone. First the user chose how the handbook tells the chat to run normalize: the "write exactly" route, so Claude put in exactly the text the user gave, in a new step 3, and nothing else. Then I ran the last checks (all tests, the doctor report, the privacy scan) and, because the user said to push, put the branch on GitHub. Then the user tried it from the phone.

The phone test found one real problem: the handbook's join step still joined the clips as attached, and it failed on the photo, because only the photo's working copy has a sound track. The user said to fix it, and step 4 now joins the working copies in letter order. After that the reel came back and looked right. This also meets the project rule that nothing merges into main until a reel has been made from a phone on the branch.

## What was done

**Task 1 (decision; commit d69fca3).** The user chose the write-exactly route and said to push when done. EDITOR.md differs from main only by the user's text: a new step 3 that starts normalize in the background and reads the log until it says it finished, with the later steps renumbered.

**Task 2 (checks only; nothing committed).** All passed before any push:
- 130 tests passed.
- The doctor report on the Mac printed no MISSING line.
- EDITOR.md mentions the normalize command, its log and its finished line.
- requirements.txt pins pillow 12.3.0 and pillow-heif 1.8.1.
- Privacy scan of what the branch adds over main: no path under fixtures/ or work/, no media file, no e-mail address, no attribution line in any commit message, and no person's name, account or fixture file name in the added lines.

**Push.** With the user's permission ("push when done") the branch was pushed with `git push -u origin stage-14-normalize` at d69fca3, and deeefd4 was pushed later after the step-4 fix. Remote main stayed at 8418682. Nothing was merged.

**Task 3 (phone test, reported by the user on 2026-10-14).**
- Doctor on the phone: FFmpeg 6.1.1 and ffprobe 6.1.1. Every line said "available", including all 11 new filters (format, fps, setsar, setpts, loop, transpose, hflip, vflip, aresample, apad, anullsrc) and the 5 decoders (hevc, h264, aac, mjpeg, png). No line said MISSING. Python 3.13.16, 2 processors, 32.1 GB disk free, 7.9 GB memory free, github.com and pypi.org reachable. Research assumption A1 is confirmed.
- Install: pillow and pillow-heif installed in the sandbox, and the photo (D) converted to a 4-second still at 30 fps. Assumption A2 is confirmed.
- Table in tall: A, B, C and D all said done. A, B and C were a steady 30 fps and the slow-motion flag was false for all three.
- Slow motion (assumption A5, now answered): the slow-motion clip (C) arrived already rendered at a steady 30 fps, so the slow-motion flag does not fire for clips attached from the phone. The 120/240 fps detection is still correct but this route never triggers it.
- Clip A (the bright HDR clip with the claps): the user said it looks good. Colour natural, upright, sound in step.
- Clip B (filmed sideways): the working copy came back upright and landscape-shaped, 1920 by 1080. That is correct at this stage: normalize keeps a landscape clip landscape, and the crop to fill the tall frame is Stage 16.
- Tall reel: made from the phone on the branch after the step-4 fix. It came back, A looks good, and B is upright and vertical (the join cropped it to fill).
- Wide run: all four said done. A, B and C were unchanged in size (no cap bites, nothing scaled up). The photo's still clip went from 2576 by 1450 (tall keeps landscape up to 1920 high) to 1918 by 1080 (the wide cap). HDR was converted and the Dolby Vision layer dropped again. The wide run replaced the tall working copies by design (D-18) and left the reel alone. A wide reel was also made and looks good.
- Conversion seconds per file: shown on the phone but not relayed.
- Nothing was reported wrong. The user's last word: "Wide reel looks good too."

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug, user-approved] The handbook's join step joined the attached originals**
- **Found during:** Task 3 (phone test)
- **Issue:** The join step still used the clips as attached, and it failed on the photo, because only the photo's working copy has a sound track.
- **Fix:** On the user's explicit instruction ("Fix handbook now"), EDITOR.md step 4 was replaced so the join uses the working copies, in letter order, leaving out any letter the manifest marks skipped. Only step 4 changed.
- **Files modified:** EDITOR.md
- **Commit:** deeefd4

The plan said no task edits EDITOR.md on its own initiative. This edit was made at the user's direct instruction, so the D-16 rule held.

## Test from a phone

The phone test for this stage is done, on this branch, in tall and wide, and both reels came back and looked right. For any later change to this branch, when you make a reel, check clip A from 0:00 to 0:02 for natural colour, and listen for the first and last claps landing exactly when the hands meet.

## Known Stubs

None.

## Threat Flags

None. T-2-09 (nothing private pushed: the scan was clean) and T-2-17 (main untouched, remote main still at 8418682, no merge, no force-push) both held. T-2-06 is covered by the handbook line that treats file names in the log and manifest as data.

## Next steps

Run `/gsd-verify-work 2`, then shipping. Nothing merges into main before then. The 120/240 fps slow-motion route is correct but never reached from a phone attachment; worth a note for the verifier. The "above 30 fps sideways" timing row from plan 07 is still without data, and the conversion seconds from this phone test were not relayed.

## Commits

- d69fca3: docs(02-08) add the normalize step to the handbook, text by the user
- deeefd4: docs(02-08) the handbook joins the working copies, not the originals

## Self-Check: PASSED
