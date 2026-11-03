---
phase: 07-stage-19-conversation
plan: "06"
subsystem: handbook
tags: [editor-md, talking-with-her, brief, follow-ups, revise-guard, word-cap]

requires:
  - phase: 07-stage-19-conversation
    provides: "plans 01 to 05: the revise command with its six changes, numbered new lists, the follow-up chain proved in both shapes"
provides:
  - "EDITOR.md: the section 'Talking with her' (the brief, the start line, the reply, the follow-up menu, errors, clips gone), pasted exactly as drafted, 1,767 words"
  - "tests/test_editor_handbook.py: revise_call_problems and its tests; MAX_WORDS raised to 1800"
  - "docs/decisions.md and CLAUDE.md: the cap rise to 1,800 recorded"
affects: [07-07, 07-08, 07-09]

actuals:
  tokens: 12000
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "a handbook guard that checks each call the handbook writes against the tool's own help, never its wording"

key-files:
  created:
    - .planning/phases/07-stage-19-conversation/07-HANDBOOK-DRAFT.md
  modified:
    - EDITOR.md
    - tests/test_editor_handbook.py
    - docs/decisions.md
    - CLAUDE.md

key-decisions:
  - "EDITOR.md is the draft's proposed body exactly, every item kept, no cuts A to F taken, the follow-up time sentence kept"
  - "The cap rises from 1,500 to 1,800 words (option G); the whole is 1,767"
  - "A review to cut and shorten the handbook is wanted after this stage (not acted on here)"

requirements-completed: []

duration: 45min
completed: 2026-11-03
status: complete
---

# Phase 7 Plan 06: The handbook's "Talking with her" Summary

**EDITOR.md now carries the user's approved "Talking with her" section, pasted exactly as drafted (1,767 words, cap raised to 1,800), and a new guard checks that every `revise` call the handbook writes is a real change with real options.**

## The user's choices

His reply to the checkpoint, word for word:

> paste the draft, I'm going to want to do a big review later to cut and make the handbook shorter but for now 1800 words is fine.

Read as: "paste the draft" (every item kept, including the follow-up time sentence; none of the cuts A to F taken) and option G (raise the cap to 1,800).

## For later, in the user's words

"I'm going to want to do a big review later to cut and make the handbook shorter but for now 1800 words is fine."

Noted in STATE.md as a wanted review after this stage. Nothing was cut or reworded now.

## What was built

- **Task 1 (tracer), already committed:** the draft with its numbered changes, word counts, the guard results, and every revise call run on a made-up list (all passed, exit 0, except the one deliberate case of `canvas wide` over clips still converted tall, exit 1).
- **Task 2:** the checkpoint, answered above.
- **Task 3:**
  - EDITOR.md is the draft's body from the line `# Vid2Reel: the editor's handbook` to the end. Proof: `diff` of the extracted body against EDITOR.md printed nothing. `wc -w EDITOR.md` and the guard's own count both give 1,767.
  - `MAX_WORDS` is 1800 in `tests/test_editor_handbook.py`, with its comment saying when and why it rose, the module docstring says 1,800, and the cap test is renamed `test_a_text_at_the_cap_passes_and_one_word_more_fails`.
  - `docs/decisions.md` has the dated 2026-11-03 Stage 19 line (1,500 to 1,800, the whole came to 1,767, the guide gives no number). `CLAUDE.md`'s "Settled so far" now says at most 1,800 words, raised from 1,200 to 1,500 on 2026-11-02 and to 1,800 on 2026-11-03 for the "Talking with her" section (Stage 19).
  - The revise guard: `revise_call_problems(text)` finds every backticked span that is a revise call (`python3 -m v2r revise CHANGE ...`, or a span starting with one of the six change words) and checks the change word against `v2r revise CHANGE --help` and each `--option` against that help text. The tests: the real EDITOR.md names `python3 -m v2r revise` and has no faulty call; a made-up change (`faster`) and a made-up option (`--speed`, `--loud`) are each named in one plain sentence; real calls are accepted; the bare prefix and other commands are not taken for revise calls; the handbook never names `--work` or `--no-size-limit`. `revise` joins the real-commands test and stays out of the six steps. On the real EDITOR.md the guard sees nine calls (shorter, longer, reorder, drop twice, sound twice, canvas twice), so it is not passing on nothing.

## Checks

- `uv run pytest -q tests/test_editor_handbook.py`: 27 passed (21 before the guard was added).
- `grep -cE "@[A-Za-z0-9_]{2,}" EDITOR.md` and the e-mail pattern both print 0.
- No guard failed on his text, so none of his words were touched.

## Task Commits

1. Task 1 (tracer): `63330fa` docs(07-06) handbook draft for Stage 19, for the user's word
2. Task 3, the cap: `87dbd9c` test(07-06) raise the handbook cap from 1,500 to 1,800 words (test file, decisions line, CLAUDE.md)
3. Task 3, his text: `cc48328` docs(07-06) the user's handbook, Talking with her (EDITOR.md only)
4. Task 3, the guard: `16c0b1a` test(07-06) every revise call the handbook writes must be a real change with real options

The cap went in before his text so that every commit on the branch passes the handbook test.

## Deviations from Plan

None - plan executed exactly as written. The plan says to commit the text, cap and guard together or apart as sensible; they went in three commits, cap first, so no commit fails the word guard.

## Known Stubs

None.

## Threat Flags

None. T-7-13 (EDITOR.md changed without his word) is mitigated: it is his reply, and the diff against the draft's body is empty. T-7-15: the handle and e-mail greps print 0; his private-names scan over every tracked file still runs in plan 08.

## Self-Check: PASSED

- EDITOR.md, the draft, the test file and this summary exist.
- Commits 63330fa, 87dbd9c, cc48328 and 16c0b1a exist.
- `grep -c "MAX_WORDS = 1800"` on the test file prints 1; the decisions line and the CLAUDE.md phrase are each present once.

## Plain English for the user

From the next chat on this branch, the phone's Claude does five things differently. First, before it looks at any clip it sends one message with up to four numbered questions (what the reel is about, which moment is the star, lively or calm, tall or wide and how long), each with a default she can skip; anything she already said, or her Reel style section says, is left out, and "just make it" skips the lot. It never asks about sound or music. Second, it tells her how long the wait will be (about a minute a clip plus three) and then stays quiet until the reel is ready. Third, its reply is the reel, two lines at most saying what is in it (by what the clips show, never by letter), the cover still, and three follow-ups that fit this reel, such as "mute it" or "a wide version". Fourth, every follow-up changes the newest cut list in the folder it already has, using the new `revise` command, and tells her a follow-up takes about two minutes; a wide version converts the clips again first. Fifth, when something fails it quotes the tool's own sentence plus one sentence on what to do, and if the work folder has been wiped it asks her to attach the clips again in the same order. The handbook is now 1,767 words, over the old 1,500, so the cap is 1,800 until you do the shortening review you asked for. A new test checks every `revise` command the handbook writes is a real one.
