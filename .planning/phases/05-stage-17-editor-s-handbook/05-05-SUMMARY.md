---
phase: 05-stage-17-editor-s-handbook
plan: "05"
subsystem: handbook
tags: [handbook, rehearsal, EDITOR.md, user-approved, check]
requires: ["05-01", "05-03", "05-04"]
provides:
  - "Six fresh-session rehearsals (five sets with profile 1, set 1 again with profile 2), each ending in a reel, a cover still and the three lists, all passing check"
  - "The pair comparison by category and the user's verdict on it"
  - "The user's ranking of the five reels and the count she would post (five of five)"
  - "A list of thirteen places the handbook was unclear, for the user's next edit"
affects: [05-06, 05-07]
tech-stack:
  added: []
  patterns: ["each rehearsal runs in its own fresh Claude Code session that reads only EDITOR.md, the schema and its own outputs (D-10)"]
key-files:
  created: []
  modified: []
key-decisions:
  - "EDITOR.md was not changed in this round; the user approved five of five reels as they stood (D-08 kept: before the first official run it changed only as the user's own text)"
  - "The optional control run (same profile twice on one set) was not made"
requirements-completed: [HAND-04, HAND-05]
actuals:
  tokens: 3500
  tasks: 3
  commits: 1
metrics:
  duration: several sessions over two days (rehearsals by the user, checks and scoring in one round)
  completed: 2026-11-02
status: complete
---

# Phase 5 Plan 05: Five rehearsals, the pair, and the scores Summary

All five sets were rehearsed in fresh sessions from EDITOR.md alone, every final list passed check, the second-profile pair changed only where the profiles differ (with the cover the one exception, which the user attributes to the handbook), and the user would post five of five reels with small changes, so HAND-04 and HAND-05 are met in one round with no handbook change.

## What ran

Six runs, each in its own fresh Claude Code session that read only EDITOR.md, the schema and its own outputs (D-10):

- sets 1 to 5, each with profile 1;
- set 1 again with profile 2, into a second folder (the pair).

The optional control run was not made. Before this round EDITOR.md changed only as the user's own text: commits 850e6c5 and daed040, and the quick task 2a94e74, all before the first official run (D-08 kept). Three informal warm-up rounds on a spare set, before the handbook's last edits, are outside this plan and logged privately.

## Results by set (numbers and categories only)

`uv run python -m v2r check --work` exited 0 on every run's final list. The reel, the cover still and the proof sheets were present for all six. Each list was copied privately to `fixtures/rehearsals/round-1/` (one .json per run; set 5 also its re-cut). `git ls-files fixtures work | wc -l` printed 0.

| Run | Shape | Length | Shots | Fixes | Notes |
|-----|-------|--------|-------|-------|-------|
| Set 1 | tall | 10.5 s | 5 | 0 | |
| Set 2 | tall | 18.5 s | 5 | 1, then a second render | |
| Set 3 | tall | 19.5 s | 8 | 0 | one clip left out as shaky throughout |
| Set 4 | wide | 58.4 s | 8 | 0 | made wide on the user's message of about 60 seconds; the chat showed a plan first and waited for the user's go, as the handbook says |
| Set 5 | tall | 19.0 s | 9 | 1, then a second render | then a re-cut on the user's follow-up ask in the same chat |
| Set 1 with profile 2 | tall | 12.2 s | 6 | 1, then a second render | |

HAND-04 empty edge: set 5 carried the kit's unreadable-file variant. Normalize skipped the fake file, the reel was made from the rest, and the reply named the file. Passed.

## The pair, compared by category

Why text and focus decimals were ignored.

- Same: opening shot, moves, filter, touch-up (identical numbers), canvas, clips used, recipe.
- Differs: number of shots, total seconds, shortest shot, the closing shot's start second (same clip), sound keep or off (all off against all keep), the cover, and order (one extra shot).

The user's verdict: yes, the two reels differ only where the two profiles differ, except the cover, which the user attributes to the handbook rather than the profiles. HAND-04 is satisfied.

## The scores

The user ranked the five reels from best to worst as sets 2, 5, 1, 4, 3. No 1-to-5 score per reel was given, so the ranking is what is recorded, and no worst reel was traced. The resume signal was "approved: 5 of 5": five of five would be posted with small changes. HAND-05 needs three, so it is satisfied after one round. No handbook change was made.

## Where the rehearsals found EDITOR.md unclear

For the user's next edit. Paragraph names are the handbook's bold paragraph titles.

1. **Before editing.** Whether a Reel style's standing answers to the brief count as the message saying what the reel is about and which moment matters, so that nothing is asked. Every run took them as answers. Also whether a standing answer that still needs a detail the user never gave counts.
2. **Who wins** and **Sound.** A style's sound rule that depends on hearing a voice, or a sound that is the point, against the handbook's interim rule to keep every shot's own sound. The runs split three to three between all off and all keep, and the editor cannot hear.
3. **Two recipes.** No test for telling the post types a style splits its rules by. Two runs on similar footage chose opposite recipes.
4. **Choosing and ordering moments.**
   - "One moment from every clip" against "never pad with weak shots" when a clip has no candidates or is shaky throughout.
   - How far the rules bend to time order, and which ones.
   - Whether attach order or shooting order is "the clips' order".
   - Whether a steady stretch that is not a candidate, or a half-second marked shaky, may be used to reach a minimum.
   - Two length rules (within a tenth; shorter when thin) plus a style's floor and cap, with no word on which gives way.
   - "The first three shots are the shortest" against a four-second photo, ties, and a style's one-second final hold.
   - The opener's thumbnail rule against a style's face-first rule, and against time order when the first clip opens on an unsuitable frame.
   - "Never two alike shots side by side" leaves no room for a run of shots from one spot that differ only in width, in order. The user's follow-up on set 5 settled it.
5. **Movement.** "Give every photo a push-in" against a style that keeps some photos still; whether taste may override that line; whether "at most one in four" invites any move at all.
6. **Framing.** "Aim at the thing, not the person" when the person is the point, and when aiming at the thing crops the person out of a wide frame.
7. **Numbers in the list** and **Before sending.**
   - The thumbnail rule against "name the cover by shot and second when one frame stands out".
   - The cover is not in the before-sending check.
   - Whether a jump cut, or an unwanted element entering at a shot's end or at a photo's edge, counts as "plainly wrong".
   - What to do with a superseded render.
   - Whether a fix refused by check still counts as the one fix.
8. **Long commands.** Where the logs go when the work folder is cleared by normalize; whether a background waiter counts as reading the log every 30 seconds.
9. **Talking head (plan first).** How to know a video is a talking head before look; how far to go before showing the plan; whether match runs before the go; how to choose stretches far longer than any candidate; where to cut speech without hearing it (cuts were placed in measured pauses).
10. **Loudness.** Render reports the sound evened below the target when a peak would clip; the handbook does not say whether to tell the user or act; whether the list must carry a loudness target.
11. **Sheets.** Whether to send any when the reel comes first; what to do with check's notes already resolved by match.
12. **Unused clips.** Whether a converted but unused clip stays in the list's "clips" block.
13. **A blemish that runs through a whole clip.** Nothing says to flag it.

## The kit's known limits and Mac adaptations

- Every run reported that the app injected CLAUDE.md and the memory index into the session before it began; each set it aside (the kit's known limit). No run opened `.planning/`, `docs/`, `v2r/`, the taste notes, another profile or the reel log.
- Rehearsal chats ended their turn while a background job ran and needed either their own waiter loop or a nudge. Worth a line under the kit's Mac adaptations.

## Deviations from Plan

- The optional control run (HAND-04 adjacency edge) was skipped by choice; the pair differed in categories that the profiles account for, so no wider difference needed explaining.
- The user gave a ranking instead of 1-to-5 scores; the approval count of five of five is what HAND-05 needs.
- Otherwise none: the plan ran as written, in one round, with no handbook change.

## Known Stubs

None.

## Privacy

Nothing was added to the repo by hand except planning files. Lists, reel log entries and score notes stay in `fixtures/`; no fixture-set name, account name, person's name, profile line or footage description appears here.

## Self-Check: PASSED

- Branch `stage-17-handbook` confirmed; `git ls-files fixtures work | wc -l` printed 0.
- This plan changed no code; the six runs' checks and copies were done in Task 2 as recorded above.
