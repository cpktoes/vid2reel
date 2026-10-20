---
phase: 04-stage-16-cut-list-and-renderer
plan: "11"
subsystem: phone-test
tags: [phone-test, editor-md, push, crop-note, check]
requires: ["04-10"]
provides:
  - "EDITOR.md carries the user's check, match and render steps (steps 5 to 7) and a sentence on the focus point"
  - "branch stage-16-render on GitHub, main untouched"
  - "the phone-test results for a tall and a wide reel"
  - "check's crop note names the band of the picture the crop keeps"
affects: [verify-work, ship]
key-files:
  modified:
    - v2r/render/check.py
    - tests/test_cutlist_check.py
    - docs/decisions.md
key-decisions:
  - "The user kept every choice Claude made (option-a) and asked for the draft steps to be pasted into EDITOR.md for him"
  - "After the phone test the user chose both fixes: one more sentence in EDITOR.md about the focus point, and check's crop note naming the band the crop keeps"
  - "The band in the note follows each shot's own focus point; a clip framed two ways names both bands"
requirements-completed: [CUT-03, CUT-04, CUT-05, CUT-06, CUT-07, CUT-09]
status: complete
actuals:
  tokens: 9000
  tasks: 3
  commits: 4
---

# Phase 4 Plan 11: The phone test Summary

The branch ran on the phone in tall and wide and was approved; its one finding (a wide shot framed a little high) led to a sentence in EDITOR.md and to a clearer crop note in `check`, which now says which part of the picture the frame keeps.

## What changed, in plain English

- **EDITOR.md** now has your check, match and render steps (steps 5 to 7, the old 5 to 7 are now 8 to 10), pasted in at your request. After the phone test you asked for one more sentence in step 5: aim the focus point at the thing the reel is about rather than the person holding it, and when check says a crop keeps little, tell you roughly where the frame lands and offer to move it. Commits 7fb0e7f and 36a3db6.
- **check's crop note** used to say only how much of a picture the frame keeps ("Clip B is upright in a wide frame, so the frame keeps only 32 percent of its picture."). It now also says which part, so Claude can see at once when the frame is aimed too high or too low: "...: the part from 20 to 52 percent down the picture." for an upright clip in a wide reel, and "...: the part from 34 to 66 percent across the picture." for a sideways clip in a tall reel. The numbers are worked out with the same code render crops by, from each shot's focus point, and held inside the picture at its edges (a focus at the very bottom gives 68 to 100 percent down). If a clip is used twice with two different framings, both parts are named. It is still only a note, never a refusal. Commit f7bb4a0, with new tests for a focus at each edge, at 0.36 (the case from the phone test) and for a clip framed the same way twice.
- **docs/decisions.md** has one new dated line for this change.

## For the user to paste into EDITOR.md

Offered in Task 1 and, at your request, pasted into EDITOR.md for you by the orchestrator (commit 7fb0e7f; this task did not edit EDITOR.md). The draft, which became steps 5 to 7:

5. To make a reel from a cut list, save it as work/cutlist.json; a list the user pastes is saved exactly as pasted. To write one, follow schema/cutlist.schema.json: copy each clip's letter, file name and length from work/manifest.json into "clips", leaving out skipped letters; give every segment its clip, "from" and "to" in seconds, "sound" "keep" or "off", and a "why" naming the stills it rests on; give a photo a "push-in" unless the user wants it still. Run python3 -m v2r check and fix every Problem it prints before going on; tell the user the Notes in plain words.
6. Unless the user asks for no touch-up, run python3 -m v2r match once check passes, so the clips look like one shoot; it writes the numbers into work/cutlist.json.
7. Start the render in the background: nohup sh -c 'python3 -m v2r render; echo "render finished with exit code $?"' > render.log 2>&1 & and read render.log every 30 seconds until it says "render finished". Open the proof sheets in work/proof/ and look for a black frame or a shot cropped onto someone's shoulder; if you see one, say so instead of sending. Send the reel, whose path render prints on its last line, and offer the cover still beside it. When the user asks for the cut list, show it as text, so it can be pasted into another chat.

The sentence added to step 5 after the phone test (36a3db6): set "focus_x" and "focus_y" on every shot to where the thing the reel is about sits in the stills, 0 at the left or top to 1 at the right or bottom, aiming at the thing rather than the person holding it; when check notes that a crop keeps little of a shot, say in the reply roughly where the frame lands and offer to move it.

## Your answers on the flagged assumptions

You chose **option-a: keep every choice Claude made**, and said the branch could be pushed. All of these stand:

- A reel longer than about 73 seconds is made at 720x1280 (past about 146 seconds at 540x960) so it comes back through the chat, and render says so.
- The shortest reel check allows is 3 seconds (`MIN_REEL_SECONDS`).
- check notes a crop that keeps less than half the picture (`CROP_NOTE_SHARE` 0.5).
- The music fades in over 0.5 seconds (`FADE_IN_SECONDS`); the drop under kept sound ramps over 0.3 seconds (`MUSIC_DROP_RAMP`).
- match takes the middle of the clips the reel actually uses and still writes numbers for an unused clip.
- A photo with no move is built from its big upright copy too.
- The finished reel uses x264's "medium" speed, the same as join.

## The push

The orchestrator ran the branch scan over the whole branch before pushing: 0 home-folder paths, 0 e-mail addresses, no media files, no fixtures/ or work/ files, no attribution lines across 36 commits. `git push -u origin stage-16-render` put 7fb0e7f on GitHub (equal to the local HEAD at that moment). origin/main was eaed834 before and after the push: main was never pushed, merged or force-pushed. The two commits made after the push (36a3db6 and f7bb4a0) and the documents commit are local until the orchestrator pushes them.

## The phone test

Both shapes were made from the phone on branch stage-16-render. You replied "approved all", with the finding below.

- **Tall reel:** about 4 minutes from the request to the finished file (asked 6:21 pm, file at 6:25 pm). That covers setup, normalize (about a minute), look (about 20 seconds), the cut-list conversation, match and render.
- **Wide reel:** about 5 minutes (asked 6:29 pm, first render done 6:32 pm). One shot was re-framed and rendered again by 6:34 pm.
- Normalize took about 20 seconds per clip each time; check and match took a few seconds each. No install error and no doctor MISSING line was reported, so the sandbox's pip wheels and FFmpeg filters behaved as the research expected (A1 to A4).
- Everything else in the test script was approved.

### The finding

In the wide reel, Claude set `focus_y` 0.36 on the planing shot ("framed on his arms, the planer and the blank"). The kept band ran from about 20 to 52 percent down the upright clip, and the planer sat below it. A talking close-up in the wide reel also aimed slightly high, with the subject moving a little. The renderer kept exactly the band the list asked for (the focus point moves the band and is held at the picture's edges, which the tests show), so this was the chat's judgment from the stills aiming a little high, not a renderer fault. It re-framed and re-rendered from one sentence typed on the phone.

### The two fixes (your answer: "both")

1. The sentence in EDITOR.md step 5 (36a3db6), so Claude aims at the thing and tells you where the frame lands.
2. check's crop note now names the band the crop keeps (f7bb4a0), so a frame aimed too high or too low shows up in the note before rendering.

**Per the project rule, these two fixes must be tested from the phone again, with one wide reel, before anything merges into main.** In that reel, watch for check's note to say which part of an upright clip the frame keeps (for example "the part from 14 to 46 percent down the picture"), for Claude to repeat it to you in plain words, and for the thing the shot is about (the planer, the hands) to sit inside the kept part in the rendered shot. Nothing else about how video is made or sounds changed in this plan.

## Deviations from Plan

### Auto-fixed Issues

None. The plan's tasks were a decision, a push and a phone test. The crop-note change was asked for by you after the phone test, so it is a new request rather than a deviation; one choice inside it is worth knowing: the band follows each shot's own focus point (the note before this one looked at the centre of the picture only), because the finding was about the focus.

## Known Stubs

None.

## Threat Flags

None. The plan's push mitigation (T-4-09, T-4-10) held: the scan was clean and origin/main did not move.

## Next steps

1. A quick task to record the phone test in docs/phone-limits.md (as for Stages 14 and 15).
2. Test the two fixes from the phone with one wide reel (above).
3. Then `/gsd-verify-work 4`, the code review, and shipping. Nothing merges into main before then.

## Self-Check: PASSED

- v2r/render/check.py, tests/test_cutlist_check.py and docs/decisions.md changed as described.
- Commits 7fb0e7f, 36a3db6 and f7bb4a0 exist on stage-16-render.
- The full suite passed after the crop-note change.
