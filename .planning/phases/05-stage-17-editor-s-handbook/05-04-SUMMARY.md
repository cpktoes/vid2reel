---
phase: 05-stage-17-editor-s-handbook
plan: "04"
subsystem: handbook
tags: [handbook, EDITOR.md, user-approved]
requires: ["05-02"]
provides:
  - "EDITOR.md: the complete handbook in the user's approved words, 1,192 words, guards green"
affects: [05-05, 05-07]
tech-stack:
  added: []
  patterns: ["every word in EDITOR.md is the user's, pasted on his word (D-08)"]
key-files:
  created: []
  modified: [EDITOR.md]
key-decisions:
  - "The handbook's ordering rule: time order wins where time carries the meaning (talking, making, journeys); the user's own addition at the read-through"
  - "The 1,200-word cap (D-04) was never exceeded; raising it would be a decision change guarded by a test"
requirements-completed: [HAND-01, HAND-02]
status: complete
actuals:
  tokens: 22000
  tasks: 3
  commits: 2
metrics:
  completed: 2026-10-24
---

# Phase 5 Plan 04: The user's handbook in EDITOR.md Summary

EDITOR.md is now the complete handbook, 1,192 words, in the words the user approved: the draft with six corrections, three cuts, and his own ordering rule, checked by the four guards and read by him against the twelve-line checklist.

## The user's choices

Recorded word for word.

At Task 1:

> paste 1 2 3 4 5 6 A B C

That is all six corrections and all three cuts. The optional Reel style guard was not asked for, so tests/test_editor_handbook.py is unchanged.

At Task 3, first round, on checklist line 3 (craft):

> I'm not sure about Craft: open on the strongest picture; prefer steady, sharp candidate stretches; one moment from every clip before a second from any; never two alike shots side by side; end on a shot that feels finished; stay within a tenth of the length asked; the moment she named usually opens or closes; attach order is not shot order. I can see times when a talking head video especially, but also others would need to be in chronological order, and this rule eliminates that from happening.

He was then shown three wording options and three cuts with word counts, and replied:

> 1 D E G and I'm not too worried about going slighly over the 1200 words.

- Option 1 replaced "Attach order is not shot order." with "Attach order is not shot order, unless time carries the meaning: someone talking, a thing being made, a journey keep their order, whatever the rules above say."
- Cut D shortened "Open on the strongest picture; the first second decides whether a viewer stays." to "Open on the strongest picture."
- Cut E shortened "The candidates are facts in an order, not choices; the choice is yours, by the rules below." to "The candidates are facts, not choices."
- Cut G shortened "Show the cut list as text when asked, so it can be pasted into another chat." to "Show the cut list as text when asked."

The result is 1,192 words, so the 1,200 cap (D-04) was never exceeded. The cap is a settled decision guarded by a test; raising it, as he was willing to, would be a decision change and was not needed.

At Task 3, second round, on all twelve lines:

> approved

## Final result

- Word count: 1,192 (`wc -w EDITOR.md`; the guard counts the same way).
- Guards: 11 tests in tests/test_editor_handbook.py passed on the committed EDITOR.md.
- Names scan: 0 hits (temporary list of 51 candidates kept outside the repo and deleted; 20 ordinary English words were dropped from it to avoid false hits). The check for anything shaped like a social handle also printed 0.

## The twelve checklist answers

| Line | What it checks | Answer |
|------|----------------|--------|
| 1 | Steps in order naming each command; make the reel first, plan first only for a talking-head video | yes |
| 2 | How to read the sheets and look.json; candidates are facts, not choices | yes |
| 3 | Craft rules | changed (the ordering rule above), then yes |
| 4 | Lively and Calm with shot lengths | yes |
| 5 | House rules | yes |
| 6 | Honesty rules | yes |
| 7 | Before sending: proof sheets, one fix, then stop and ask | yes |
| 8 | Unreadable files and too little footage | yes |
| 9 | Order of authority | yes |
| 10 | Only the repo's commands | yes |
| 11 | Defaults, two questions, the music sentence | yes |
| 12 | No one person's or account's taste | yes |

## What changed (plain English)

Only EDITOR.md. No code, no tests, no video processing. The phone's Claude will now do these things differently:

1. It describes candidate moments correctly: two to four seconds long, camera-still ones first, never a shaky or blurry stretch.
2. It knows a photo has no candidate moments and its clip is four seconds long, so it never asks for a longer shot of a photo.
3. It uses the cut list's real field names, "move" and "sound", for a photo's slow move and for keeping or turning off a shot's own sound.
4. It runs normalize, look and render in the background, each into its own log (normalize.log, look.log, render.log), and reads the log every 30 seconds until it says "finished".
5. It decides "no move on a moving shot" by look.json's camera_state: never a push-in or pan on a shot that is panning or shaky.
6. It makes the reel first, and shows a plan before building only for a talking-head video.
7. New, and the user's own: attach order is not shot order, unless time carries the meaning. Someone talking, a thing being made, a journey keep their order, whatever the other rules say.

## What to look for in the first rehearsal

- In the talking-head set, does the editor keep speech in the order it was spoken, even where a craft rule (the strongest picture first, one moment from every clip) would shuffle it?
- Does it show a plan before building for the talking-head set, and not for the others?
- In the cut list, are the fields called "move" and "sound" (not other names), and does check accept it without a complaint about them?
- Does it read normalize.log, look.log and render.log, rather than waiting blind or running everything in the foreground?
- On the non-talking sets, does it go straight to making the reel after the two questions, with no plan shown first?
- Does a photo get a four-second shot, and no shot longer than that?
- Does it add a slow move only to photos and to at most one video shot in four, and never to a shaky or panning shot?

## Commits

- 3d9cf2d: docs(05-04): the user's handbook in EDITOR.md (items 1 to 6 and cuts A, B, C pasted; 1,198 words)
- 745de0d: docs(05-04): the user's ordering rule in EDITOR.md (his rule plus cuts D, E, G; 1,192 words)

Task 1 and Task 3 were the user's decisions and changed no file.

## Phone test

No video processing changed, so this plan needs no phone test on its own. The stage's phone test comes with plan 07.

## Deviations from Plan

None. The plan expected one paste and one read-through; the read-through produced a second pass (his ordering rule), which went through the same route (his wording, guards, names scan, commit) as the first.

## Known Stubs

None.

## Threat Flags

None.

## Self-Check: PASSED

EDITOR.md exists at 1,192 words; commits 3d9cf2d and 745de0d exist; 11 guard tests passed; names scan and handle scan printed 0.
