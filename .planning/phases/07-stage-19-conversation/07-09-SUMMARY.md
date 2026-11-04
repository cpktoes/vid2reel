---
phase: 07-stage-19-conversation
plan: "09"
subsystem: phone-test
tags: [phone-test, merge-rule, brief, follow-ups, revise, phone-limits, decisions, traceability]

requires:
  - phase: 07-stage-19-conversation
    provides: "plans 01 to 08: the revise command, the recipe field, the handbook's Talking with her, the rehearsals, and branch stage-19-conversation on GitHub at a875e1b"
provides:
  - "The Stage 19 phone test, approved: the brief, a quiet wait, a reel, then shorter, mute it and a wide version from the user's phone on the stage's branch"
  - "docs/phone-limits.md row 19; four dated Stage 19 lines in docs/decisions.md; CLAUDE.md's Stage 19 clause extended"
  - "CONV-01 to CONV-07 marked complete; the traceability row Complete"
  - "The closing commits scanned (items a to g) and listed for the merge; nothing pushed"
affects: [phase-7-verification, merge-of-stage-19, stage-20]

actuals:
  tokens: 5000
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns:
    - "the stage's phone test as a blocking-human checkpoint, recorded in general terms only, with the closing commits scanned but left unpushed until the merge"

key-files:
  created:
    - .planning/phases/07-stage-19-conversation/07-09-SUMMARY.md
  modified:
    - docs/phone-limits.md
    - docs/decisions.md
    - CLAUDE.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "A wide version converts the clips again with the other shape and changes only the canvas in a new numbered list; no new sheets, no new touch-up; the clips are never asked for again and the repo is never cloned again"
  - "A brief may ask nothing at all when the Reel style's standing answers cover every question; the first reply is then the minutes line"
  - "The handbook's follow-up estimates stay as drafted (about two minutes; a wide version half a minute a clip more)"
  - "Three smaller findings from the phone test wait for the handbook-shortening review, not fixed before the merge"

patterns-established:
  - "Phone-test records name no person, account, fixture set or viewer's words; only general terms, times and counts"

requirements-completed: [CONV-01, CONV-02, CONV-03, CONV-04, CONV-05, CONV-06, CONV-07]

coverage:
  - id: D1
    description: "The commit the phone fetched (a875e1b) is the commit the follow-up chain test passed on"
    requirement: CONV-05
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_revise_chain.py tests/test_revise.py tests/test_editor_handbook.py -q (235 passed) with git ls-remote origin stage-19-conversation equal to HEAD"
        status: pass
    human_judgment: false
  - id: D2
    description: "From a phone on the branch: brief, quiet wait, reel, then shorter, mute it and a wide version, each changing only what was asked"
    requirement: CONV-07
    verification: []
    human_judgment: true
    rationale: "Claude cannot watch video or hear audio; the user watched and listened on his phone and replied approved"
  - id: D3
    description: "Row 19 in docs/phone-limits.md, four Stage 19 lines in docs/decisions.md, CLAUDE.md's clause extended, CONV-01 to CONV-07 marked complete"
    requirement: CONV-07
    verification:
      - kind: other
        ref: "grep -c '| CONV-01 to CONV-07 | Phase 7 – Stage 19 – Conversation | Complete |' .planning/REQUIREMENTS.md (1); grep -c '^| 19 |' docs/phone-limits.md (1); grep -c '· Stage 19 ·' docs/decisions.md (9)"
        status: pass
    human_judgment: false

duration: one phone test round trip plus the records
completed: 2026-11-04
status: complete
---

# Phase 7 Plan 09: The Phone Test Summary

**The whole Stage 19 conversation worked from the user's phone on branch stage-19-conversation in 7 min 33 s from send to saved: no brief question was needed, one line with an estimate, quiet, a 15.8-second tall reel, then "shorter", "mute it" and a cut-off "a wide version" each changed only what was asked; the records are written and CONV-01 to CONV-07 are complete.**

## Performance

- **Duration:** one phone test round trip (checkpoint) plus the records
- **Completed:** 2026-11-04
- **Tasks:** 3 of 3
- **Files modified:** 4 (plus this summary, STATE.md and ROADMAP.md)

## Task 1: tracer, the commit the phone fetches

- `git ls-remote origin stage-19-conversation` printed `a875e1b74a94137730d4d9ede8ddb2bc3f451b5f`, equal to the local HEAD at the time.
- `uv run pytest tests/test_revise_chain.py tests/test_revise.py tests/test_editor_handbook.py -q`: 235 passed on that commit.
- No commit (checks only). One pass; no fix was needed, so plan 08's gates did not run again.

## Task 2: the phone test (checkpoint, gate blocking-human)

The user's reply, word for word:

> approved

With it: "I got 'about 8 minutes' as the first reply and no questions. Delivered in 7:33." and a pasted transcript of the follow-ups. Recorded here in general terms only: no person, account, fixture set or viewer's words.

**Where and what.** The user's own phone, inside a Project of the user's own account (not hers, as in Stage 17), whose Reel style section holds standing answers to all four brief questions, on branch stage-19-conversation. Five attachments: three clips and two photos, one photo filmed sideways; none used in the rehearsals. The message typed was exactly "Use branch stage-19-conversation, make a reel".

| Acceptance item | Result |
|-----------------|--------|
| Stopwatch, send to saved | 7 min 33 s, inside the first reply's estimate of about 8 minutes (five clips plus three) |
| Brief questions | 0. The Reel style's standing answers covered all four; the handbook says to leave out any question the Reel style already answers |
| Start line and quiet | yes: the first reply was the minutes line, then nothing until the reel |
| The reply's line count and its three follow-ups | not recorded (not in the pasted transcript) |
| Step 7, the reel | 15.8 s tall, seven shots, Lively (shots 1.8 to 3.0 s; the two photos 2.5 and 3.0 s), every shot's own sound kept, cover the first frame of shot 1 (the opener) |
| Step 8, "shorter" | yes: no new questions; 15.8 s to 12.0 s; the same seven shots in the same order, the opener unchanged; only the "to" values of shots 4 to 7 changed (to 1.5, 1.5, 1.5 and 1.7 s). One false start: the first trim was run from an older list and redone from the list the reel was rendered from; the unused list stayed in the work folder. "show me the cut list before and after" came back as a table of both lists with only "to" changed |
| Step 9, "mute it" | yes: the same 12.0 s, silent; only each shot's "sound" changed; the reply said music is added in the posting app. The reply ran to three paragraphs, over the handbook's two lines, and quoted a standing Reel style line about sound (the Project's text, not the repo's). The optional second "mute it" was not tried |
| Step 10, "a wide version" | yes: the message arrived cut off ("a wide version of") and was read as a wide version of the muted reel; estimate about 4 minutes; the clips were converted again without being asked for again; 1920x1080, the sideways photo shown whole, the upright clips cropped to a band about a third of their height on the subject, the same length, still silent; only the canvas changed. The reply offered to move one shot's frame up |
| Any follow-up started from scratch or asked for the clips | no: no new clone, no request for the clips, no new questions, no new shots, no new order |

**Findings kept for the later handbook-shortening review, not fixed now:** "change the newest cut list" did not stop one trim from the wrong list (the handbook could say "the list the last reel was rendered from"); follow-up replies ran over two lines; a standing Reel style line on sound outranked the handbook (as rehearsal finding 14 already noted).

## Task 3: the records (no push)

Commit `e8d3e63` `docs(07-09): Stage 19 phone test, decisions and traceability`.

**docs/phone-limits.md, row 19** (one table row, the facts above in general terms): "Stage 19 (2026-11-04): five attachments (three clips and two photos, one photo filmed sideways) inside a Claude Project of the user's own account, whose Reel style section holds standing answers to all four brief questions, on branch stage-19-conversation, from the user's phone; the message was exactly "Use branch stage-19-conversation, make a reel", then "shorter", "mute it" and "a wide version" in the same chat. Not one of her account's Projects." Outcome: approved; 7 min 33 s against about 8 minutes; zero questions and why; the reel's numbers; each follow-up with what changed, the wrong-list false start noted as redone; the cut-off wide message; nothing started from scratch; the reply's lines and follow-ups not recorded.

**docs/decisions.md, four lines dated 2026-11-04 · Stage 19 ·**

1. The phone test ran from the user's own phone inside a Project of the user's own account, as Stage 17's did, with five attachments, where the guide says one of her account's Projects; the Reel style's standing answers silenced all four questions, so the brief asked nothing and the first reply was the minutes line; the merge rule is met as written; 7 min 33 s for the whole chain.
2. A wide version is made by converting the clips again with the other shape, the same files in the same order, then a new numbered list in which only the canvas changed, then check and render: no new sheets, no new touch-up, no new shots, no new order; the clips are never asked for again and the repo never cloned again; every follow-up starts from the newest list; confirmed on a cut-off message. The guide names "a wide version" but not how it is made.
3. The handbook's follow-up estimates are kept as drafted (about two minutes; a wide version half a minute a clip more); the guide gives no number.
4. Three smaller findings from the phone test wait for the handbook-shortening review rather than being fixed before the merge, because none broke a follow-up.

**CLAUDE.md:** changed. The Stage 19 clause in "Settled so far" now also says: a wide version converts the clips again with the other shape and changes only the canvas in a new numbered list, with no new sheets and no new touch-up, and a follow-up in the same chat never clones the repo again or asks for the clips, starting from the newest list; a brief may ask nothing when the Reel style's standing answers cover every question; a follow-up is said to take about two minutes, a wide version half a minute a clip more.

**.planning/REQUIREMENTS.md:** the seven `- [ ] **CONV-0N**` lines are `- [x]`; the traceability row ends `| Complete |`.

### Last scan (plan 08 Task 1 step 5, items a to g, over origin/stage-19-conversation..HEAD)

| Item | Check | Result |
|------|-------|--------|
| (a) | files under fixtures/ or work/ | none |
| (b) | media files | none |
| (c) | e-mail addresses in added lines (pytest decorators excluded) | 0 |
| (d) | home path in the diff / tracked at HEAD | 0 / 0 |
| (e) | Mac user name in the commits / tracked at HEAD | 0 / 0 |
| (f) | secrets in added lines | 0 |
| (g) | attribution lines in commit messages | 0 |

Commits not yet on GitHub at the time of the scan (`git log --oneline origin/stage-19-conversation..HEAD`):

- `e8d3e63` docs(07-09): Stage 19 phone test, decisions and traceability

This summary's own commit (`docs(07-09): phone test approved; summary, state and roadmap`) follows it and was scanned the same way before the plan returned; its hash is in the plan's final report. `git rev-parse --short origin/main`: `bb5cb0f`. `git ls-remote origin stage-19-conversation` still shows `a875e1b`: nothing was pushed.

### Verify

- `grep -c "| CONV-01 to CONV-07 | Phase 7 – Stage 19 – Conversation | Complete |" .planning/REQUIREMENTS.md`: 1
- `grep -c "^| 19 |" docs/phone-limits.md`: 1
- `grep -c "^- \[x\] \*\*CONV-0[1-7]\*\*" .planning/REQUIREMENTS.md`: 7
- `grep -c "· Stage 19 ·" docs/decisions.md`: 9 (five before, four added)
- `git diff --name-only main -- docs/field-guide.html`: nothing
- `uv run pytest tests/test_editor_handbook.py -q`: 27 passed (EDITOR.md untouched)

## Every way Stage 19 differs from docs/field-guide.html

For the user, so the guide can be revised (the guide itself was not edited):

1. The brief is four numbered questions with defaults, asked straight away before looking, leaving out what the message or the Reel style answers, none on "just make it", at most one more after looking; the two questions Stage 17 brought forward fold into it. Same as the guide's pick in "Decide: when to ask", now settled.
2. The cut list has an optional "recipe" field (lively or calm), read as Lively when missing, with its lengths in settings.py; not in the guide.
3. Follow-ups are `revise`, one named change written as a new numbered list beside the old one, with the chat naming the shots for shorter and longer and `longer` stopping at the clip's end and at a later shot of the same clip; the guide names the command but not the numbered lists, the named shots or where longer stops.
4. The handbook's cap rose to 1,800 words for "Talking with her"; the guide gives no number.
5. The phone test ran on the user's own phone in a Project of his own account, not one of hers, with five attachments; and the brief asked nothing because the Reel style's standing answers covered every question, where the guide expects the questions to be seen.
6. A wide version is made by converting the clips again with the other shape and changing only the canvas in a new numbered list, no new sheets or touch-up, never asking for the clips or cloning again; the guide does not say how it is made.
7. The handbook gives follow-up time estimates (about two minutes; a wide version half a minute a clip more); the guide gives none.
8. Three small findings from the phone test are deferred to the handbook-shortening review rather than fixed before the merge; the guide has no such review step.

## Before the merge

Nothing merges in this phase. The merge into main waits for the phase's verification (code review gate, regression gate, the verifier and `phase.complete`) and the user's go-ahead. At the merge, before main is pushed, the user runs his own names scan over the closing commits with plan 08 Task 2's commands and the range `origin/stage-19-conversation..main`, since these commits were scanned here for paths, media, e-mail addresses, the home path, the Mac user name, secrets and attribution lines, but only he holds the private words.

## Decisions Made

See key-decisions above; all four are written into docs/decisions.md and the first three into CLAUDE.md.

## Deviations from Plan

None - plan executed exactly as written. Task 1 passed on the first pass, so the fix loop through plan 08 was not needed. The reel reply's line count and its three follow-ups were not in the user's report and are recorded as "not recorded", as rows 17 and 18 of phone-limits.md record their own gaps.

## Issues Encountered

None in execution. The phone test's own blemishes (the wrong-list false start, a three-paragraph reply, a Reel style line outranking the handbook) are recorded above and deferred, not fixed.

## Known Stubs

None.

## Threat Flags

None - no new attack surface. T-7-22: the row, the lines and this summary hold general terms only and were scanned (items a to g); the user's names scan over them comes before the merge pushes them. T-7-20: main was not merged, pushed or touched. T-7-23: Task 1 confirmed GitHub's branch equalled the tested commit before the test.

## Next Phase Readiness

Phase 7's nine plans are executed. Next: the phase's verification gates and `phase.complete`, then the merge of stage-19-conversation into main on the user's word, then Phase 8 (Stage 20, her two weeks).

## Self-Check: PASSED

- `docs/phone-limits.md` row 19, `docs/decisions.md` four lines, `CLAUDE.md` clause and `.planning/REQUIREMENTS.md` marks: all present at HEAD.
- Commit `e8d3e63` exists on branch stage-19-conversation.
- `git ls-remote origin stage-19-conversation` is still `a875e1b`.

---
*Phase: 07-stage-19-conversation*
*Completed: 2026-11-04*
