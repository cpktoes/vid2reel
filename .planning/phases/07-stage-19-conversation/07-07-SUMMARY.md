---
phase: 07-stage-19-conversation
plan: "07"
subsystem: rehearsal
tags: [rehearsal-kit, brief, follow-up-chain, revise, brief-test]

requires:
  - phase: 07-stage-19-conversation
    provides: "plans 01 to 06: the revise command, numbered new lists, the handbook's Talking with her"
provides:
  - "07-REHEARSAL.md: the Stage 19 rehearsal kit (blanks only, nine cases, turn-by-turn conversation, after-run checks)"
  - "The user's verdict: every case behaves and the briefed reel beats the no-question reel; no round again"
  - "A list of places the handbook read unclear in rehearsal, for his later shortening review"
affects: [07-08, 07-09]

actuals:
  tokens: 9000
  tasks: 3
  commits: 1

tech-stack:
  added: []
  patterns:
    - "a rehearsal kit that runs a conversation turn by turn in a fresh window, then checks every numbered list and diffs each pair with sorted keys"

key-files:
  created:
    - .planning/phases/07-stage-19-conversation/07-REHEARSAL.md
  modified: []

key-decisions:
  - "No round again: no handbook sentence changed and no code bug found, so EDITOR.md and the code are untouched by this plan"
  - "The handbook's unclear places are recorded here only; no decision on any of them is taken now (they wait for his shortening review)"

requirements-completed: []

duration: one kit, one rehearsal round, one judging round
completed: 2026-11-03
status: complete
---

# Phase 7 Plan 07: Rehearsals Summary

**The Stage 19 rehearsal kit was written and its after-run commands proven; the user ran all nine cases in fresh windows, judged them and the brief test with her, and approved: every case behaves, the briefed reel wins, and nothing in the handbook or the code had to change.**

## The user's replies, word for word

Task 2 (the rehearsals):

> rehearsed, do I need to do anything with the rehearsal reports or do you have access to them all already?

(His results then came as the case results below. The reports are in his private folders; this plan reads none of them and no report needs to be sent anywhere.)

Task 3 (the judging):

> approved

Read as: every case behaves and the briefed reel wins; no round again, no handbook sentence changed, no code bug.

## What was built

- **Task 1 (tracer), committed as `1843fe0`:** `07-REHEARSAL.md`, Stage 17's kit brought to Stage 19. Blanks only. It spells out the conversation turn by turn (the session stops after the brief and waits for the answers), the Mac adaptations including `--work work/<SET>` after `revise`'s change word, nine cases, the brief-versus-"just make it" comparison, the after-run checks (check on each numbered list, a sorted-keys diff of each pair), and the three closing lists given only when he types "end of rehearsal".
- **The scratch proof of the kit's after-run commands** (run again when this summary was written, in a temporary folder outside the repo with placeholder files from `tests/cutlists.py`, folder deleted afterwards): `revise sound off` exited 0; `check` on the work folder exited 0; `check` on the new numbered list exited 0; the sorted-keys diff of the two lists showed changes only on "sound" lines (0 lines of any other kind): yes.
- **Task 2:** he ran the cases in fresh windows and the after-run checks himself. This plan never opened `fixtures/` or `work/`.
- **Task 3:** he watched the reels with her and judged. Approved.

## Case results (by case and set number only)

| Case | Set, profile | Message | What happened | Checks |
|------|--------------|---------|---------------|--------|
| 1 | set 2, profile 2 | nothing but the clips | the brief alone, 1 question asked (the profile's standing answers covered the rest); reel 14.5 s tall, 7 shots; one re-render before it was sent | exit 0 |
| 2 | set 1, profile 1 | "make a reel" | brief of 2 questions; reel 12.6 s tall, 7 shots | exit 0 |
| 3 | set 3, profile 3 | "20 seconds, calm, tall" | 2 questions, numbered 1 and 2; reel 20.0 s tall, Calm, 5 shots, one clip left out | exit 0 |
| 4 | set 1, profile 1, second folder | "just make it" | no question; reel 11.3 s tall, Calm, 3 shots. Then "slower": `revise longer` stopped at the ceiling at 12.3 s and said how far short it fell | exit 0 on both lists |
| 5 | set 4, profile 2 | "wide, for long-form video" | 2 questions, no shape or length question; a plan shown first, then "go ahead"; reel 199 s wide, 7 shots, 960x540 by the size rule | exit 0 |
| 6 | set 5, profile 1 | "just make it" plus a 401 MB dummy file attached last | no question; the big file left out with normalize's own sentence, quoted word for word, with a next step; reel 16.5 s tall, 7 shots | exit 0 |
| 7 | inside case 3 | a star moment the clips do not hold | exactly one more question after looking | not applicable |
| 8 | same window as case 2 | "shorter", "mute it", "a wide version" | see the chain below | exit 0 on all five lists |
| 9 | same set as case 2 | work folder moved away, then "shorter" | asked for the clips again in order and offered the last list as text | not applicable |

**Case 8, the chain.** "shorter" wrote cutlist-2: 10.0 s, only the "to" lines changed. "mute it" wrote cutlist-3: only the "sound" lines changed. "a wide version" wrote cutlist-4 after a second normalize: only "width" and "height" changed. One hand fix of two `focus_y` values was made as cutlist-5 before the reel was sent. Check exited 0 on all five lists. No new clone of the repo was made.

**Brief test (the guide's step 4).** Case 2's briefed reel was judged clearly better than case 4's "just make it" reel of the same set. Verdict: the briefed reel wins.

**Failure classes traced:** none. No case went wrong enough to need the trace prompt.

**The one change made per round:** there was one round and no change. No handbook sentence was edited and no code bug was found, so EDITOR.md and `v2r/` are untouched by this plan, and no handbook commit was made.

## Findings for the handbook review

For his later review to shorten the handbook. These are what the rehearsals found unclear, in general terms. No decision on any of them is taken now.

1. **Standing answers versus defaults.** A profile's standing answers silence the brief's questions, so a window ends up asking fewer questions than the brief describes (cases 1 and 2 asked 1 and 2). The handbook does not say whether a standing answer counts as an answer or only as a default.
2. **"shorter" or "longer" with no number.** There is no default amount, so each window picks its own.
3. **The `--from` option.** Its format and its meaning are not shown in "Talking with her".
4. **`revise` already runs check.** The handbook still reads as if check is a separate step after every follow-up.
5. **A wide version's order.** That normalize comes first, then the change, is not spelled out; a window had to work it out.
6. **A wrong wide frame.** Two rules compete: fix it once, or offer "move the frame". It is not said which wins.
7. **The reply format is spread over several places.** The two lines, the Notes, the minutes line and the failure sentence pull apart and are not read as one rule.
8. **The minutes line under "just make it".** Whether it goes out then, and when, is unclear.
9. **After the folder is gone.** How a pasted list and the numbering continue is unclear.
10. **"One moment from every clip" against "prefer steady" and against play order.** The three rules disagree in some sets.
11. **Rule precedence with few shots.** Which rule gives way when there are only a few shots is not said.
12. **A zoom or tilt reads as shaky to look.** The handbook's advice on moving shots and what look reports do not line up.
13. **The next step for a too-big file.** It should say convert the file, not trim it.
14. **A stale Reel style line about music.** It outranks the handbook, so an old line in a profile can undo the handbook's music rule.
15. **Logs land at the top of the repo.** Where the commands write their logs is not stated.
16. **Render's loudness note never reaches the reply.** Nothing says whether it should.
17. **The cover is not in the proof-sheet check.** The step that looks at the proof sheet does not name the cover.
18. **"slower" means slow motion.** Slow motion is not built, so "slower" can only be read as "longer"; the handbook does not say so.

## Deviations from Plan

None - plan executed exactly as written. The one thing worth noting: the kit's scratch proof results were not carried in the continuation brief, so the proof was run again for this summary and recorded above.

## Known Stubs

None.

## Threat Flags

None. T-7-16: this summary names cases and set numbers only, no set folder, person or account. T-7-17 and T-7-18: his closing lists are in his private reel log; the too-big file was made outside the repo. T-7-13: EDITOR.md was not changed.

## Self-Check: PASSED

- `07-REHEARSAL.md` and this summary exist.
- Commit `1843fe0` exists on the branch.
- The e-mail pattern and the handle pattern each print 0 on this summary; `git status --short fixtures work` prints nothing.

## Plain English for the user

The dress rehearsal is done and you approved it. Claude wrote the kit; you ran nine cases in fresh windows, and the follow-ups did what they should: "shorter" changed only the length, "mute it" only the sound, "a wide version" only the size, and a wrong guess about where to point the frame was fixed by hand once. The reel made after the brief was clearly better than the one made with "just make it", so the brief earns its place. Nothing in the handbook or the code had to change. The 18 notes above are the places where a fresh window had to guess; I only listed them, I took no decision, and they are for your shortening review. The next plan (08) proves the branch is ready to leave this Mac, and pushes it only on your word; plan 09 is the phone test.
