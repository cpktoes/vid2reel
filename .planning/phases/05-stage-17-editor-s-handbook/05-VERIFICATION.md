---
phase: 05-stage-17-editor-s-handbook
verified: 2026-11-02T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
deviations_accepted:
  - "D-04 cap raised from 1,200 to 1,500 words by the user on 2026-11-02 (commit 2a94e74; CLAUDE.md, docs/decisions.md, tests/test_editor_handbook.py MAX_WORDS)"
  - "D-13 'only --work plumbing' extended by the user's quick task 415d9c5 (--no-size-limit on normalize; a size check switched off, no editing judgement)"
  - "Phone test ran in a Project of the user's own account with seven files, not in one of her Projects with two to four (recorded in docs/decisions.md and docs/phone-limits.md row 17)"
  - "The user ranked the five reels instead of scoring each 1 to 5; 'approved: 5 of 5' is what HAND-05 needs"
  - "Optional control run (same profile twice on one set) skipped"
---

# Phase 5: Stage 17, Editor's handbook: Verification Report

**Phase Goal:** EDITOR.md is the complete, plain-words handbook the chat's Claude follows, and taste lives in per-account profiles rather than in the repo.
**Verified:** 2026-11-02
**Status:** passed
**Re-verification:** No, initial verification (no earlier VERIFICATION.md in this phase)

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | EDITOR.md fits on two pages and covers: the steps in order, how to study the sheets, rules of craft, Lively and Calm, house rules, honesty rules, unreadable files and too little footage, order of authority | VERIFIED (cap deviation accepted) | Read in full. Present as headed paragraphs: "Who wins" (order of authority: chat, then "Reel style", then handbook); "Before editing" (defaults, two questions, plan first only for talking head); "The steps, in order" (1 to 8: doctor, normalize, look, check, match, render, each with its command); "Long commands"; "Reading the sheets" (stills cited by label, "anything between two stills is a guess", "never say you watched the clips", look.json fields, candidates are facts); "Choosing and ordering moments"; "Two recipes" (Lively 1.5 to 3 s default, Calm 3 to 5 s); "Framing", "Movement", "Colour", "Sound" (house rules); "Before sending" (proof sheets, one fix, then stop and ask); "When things go wrong" (unreadable or too-big file, too little footage); "Just joining". Length: `wc -w EDITOR.md` = 1299 words, under the 1,500 cap now in tests/test_editor_handbook.py (MAX_WORDS = 1500). The 1,200 to 1,500 change is the user's, recorded in CLAUDE.md and docs/decisions.md. Four guards (length, real command names, step order, no --work/--no-size-limit) pass on the committed file. |
| 2 | No editing judgement lives in Python and no one person's taste lives in EDITOR.md | VERIFIED | `git diff main -- v2r` touches only v2r/__main__.py and v2r/normalize.py. Every hunk read: normalize and look gain `--work FOLDER`, look's positional is renamed `folder` with a one-sentence refusal when the two folders differ, normalize gains `--no-size-limit` and a `size_limit` parameter that only switches the over-the-cap check. Nothing chooses a shot, length, order, move or filter. EDITOR.md grep for she/her/wife/instagram/tiktok: 0 hits; the only taste-bearing source is the "Reel style" pointer in "Who wins". No file under v2r/ or tests/ changed since 54dc0d5 (`git diff --stat 54dc0d5 HEAD -- v2r tests` is empty). |
| 3 | A "Reel style" profile drafted for each account named in the taste notes, saved in fixtures/, never in the repo | VERIFIED by record | `ls fixtures/profiles \| wc -l` = 3. `git ls-files fixtures work \| wc -l` = 0. `grep -c "\[check\]"` per profile = 0, 1, 0 (profiles 1, 2, 3), matching the plan 03 summary; the one leftover in profile 2 is the owner's recorded choice. Plan 03: pasted into each account's Project, yes/yes/yes. Plan 06 history scan: 0 private-name hits over 29 commits. Content of the drafts was not opened, by design. |
| 4 | The rehearsal runs for all five sets, and a second profile on the same set changes only what the two profiles differ in | VERIFIED by record | Plan 05 summary: six fresh-session runs (sets 1 to 5 with profile 1; set 1 again with profile 2), `check` exit 0 on each final list, reel, cover and proof sheets present for all six, set 5 carried the unreadable-file variant and passed. Pair table: same = opener, moves, filter, touch-up numbers, canvas, clips, recipe; differs = shot count, length, shortest shot, closing start, sound, cover, order. The user's verdict: differs only where the profiles differ, except the cover, which he attributes to the handbook. Recorded in the plan 05 summary and the user's own judgement; not re-observable from the repo, as designed. |
| 5 | She would post at least three of the five fixture reels with small changes | VERIFIED by record | Plan 05 summary: the user's resume signal "approved: 5 of 5" after ranking the five reels; plan 07: the phone test approved on 2026-11-02 (docs/phone-limits.md row 17). A human check by design; the record is the evidence. Ranking given instead of per-reel scores (accepted deviation). |

**Score:** 5/5 truths verified (3 of them by the user's recorded human check; 0 behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `EDITOR.md` | Complete handbook | VERIFIED | 1299 words, all required sections present and substantive, no stub text; no TBD/FIXME/XXX. |
| `tests/test_editor_handbook.py` | Guards: length, real commands, step order, no Mac-only options | VERIFIED | Present; includes tests that each guard fires on a bad text. |
| `tests/test_work_option.py` | `--work` tests, tall and wide | VERIFIED | Present; 16 tests per plan 01. |
| `v2r/__main__.py` | `--work` on normalize and look | VERIFIED | Lines 39 to 55, 107 to 118: parsed and passed to `normalize.normalize` and `look.look`. |
| `.planning/phases/05-stage-17-editor-s-handbook/05-REHEARSAL.md` | Rehearsal kit, placeholders only | VERIFIED | Exists (commit ce1dde3). |
| `docs/decisions.md`, `CLAUDE.md`, `docs/phone-limits.md` | Stage 17 decisions and phone-test row | VERIFIED | Cap change, `--no-size-limit` and phone test row 17 are recorded. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `EDITOR.md` | v2r commands | `python3 -m v2r NAME` | WIRED | The guard test calls v2r's own parser for every named command (doctor, normalize, look, check, match, render, join); passes. |
| `v2r/__main__.py --work` | `normalize.normalize`, `look.look` | `args.work` | WIRED | Lines 107 and 118. |
| `EDITOR.md` "Who wins" | per-account Project instructions | the heading "Reel style" | WIRED by record | The phone test and rehearsals read the pasted profiles; nothing in the repo reads profiles, as D-12 requires. |

### Data-Flow Trace (Level 4)

Not applicable: the phase renders no dynamic data. The `--work` value flows from the parsed argument to the function that picks the output folder.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Handbook guards and `--work` tests | `uv run pytest -q tests/test_editor_handbook.py tests/test_work_option.py` | 27 passed in 20.58 s | PASS |
| Full suite | not re-run; plan 06 ran `uv run pytest -q` = 1034 passed in 526 s at 54dc0d5, and nothing under v2r/ or tests/ changed since | n/a | PASS (by record) |
| No private files tracked | `git ls-files fixtures work \| wc -l` | 0 | PASS |

Normalize, look and render were not run, per the constraints.

### Probe Execution

SKIPPED: this phase declares no probes.

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|--------------|-------------|--------|----------|
| HAND-01 | 05-02, 05-04, 05-07 | Complete handbook | SATISFIED | Truth 1. |
| HAND-02 | 05-01, 05-02, 05-04, 05-06, 05-07 | No editing judgement in Python, no one person's taste in EDITOR.md | SATISFIED | Truth 2. |
| HAND-03 | 05-03, 05-06, 05-07 | Profiles drafted, saved in fixtures/, never in the repo | SATISFIED | Truth 3. |
| HAND-04 | 05-05, 05-07 | Rehearsal for five sets, second profile pair | SATISFIED (by record) | Truth 4. |
| HAND-05 | 05-05, 05-07 | She would post at least three of five | SATISFIED (by record) | Truth 5. |

All five IDs appear in REQUIREMENTS.md (lines 52 to 56, marked `[x]`; the traceability row at line 172 says Complete) and are claimed by plans. No orphaned requirement is mapped to Phase 5 outside HAND-01 to HAND-05.

### Anti-Patterns Found

None. No TBD, FIXME or XXX in EDITOR.md, the two test files or v2r/__main__.py. No stub implementations. `skill/` and `docs/field-guide.html` are unchanged from main.

### Decision Check (CONTEXT D-01 to D-13)

D-01 (reel first, plan only for talking head), D-02 (order of authority), D-03 (content list), D-05 (defaults), D-06 (two questions), D-07 (no music, own sound kept) are all in EDITOR.md. D-04 held with the user's raised cap (deviation recorded). D-08 held: EDITOR.md changed only as the user's own text. D-09 held: `--work` stays out of EDITOR.md, enforced by a guard. D-10 and D-11 held by the plan 05 and plan 07 records. D-12 held (three drafts in git-ignored fixtures/). D-13 held except the user's quick task 415d9c5.

### Human Verification Required

None outstanding. Criteria 3 to 5 are human checks already performed and recorded by the user.

### Notes for the user (not gaps)

- Thirteen places where the rehearsals found EDITOR.md unclear are listed in the plan 05 summary for your next edit. The most consequential:
  - whether a Reel style's standing answers to the brief count as the message saying what the reel is about, so that nothing is asked (every run took them as answers; plan 07 raised the same point);
  - sound that depends on hearing a voice (the runs split three to three between all off and all keep);
  - the cover against the thumbnail rule.
- 1,299 words is an estimate of "two pages", not a measured page count. You accepted the 1,500 cap; the guide's "two pages" wording is the thing to have revised.
- Nothing is merged into main. Per CLAUDE.md, merging waits for your word.

### Gaps Summary

No gaps. The phase goal is met: EDITOR.md is complete and guarded, the only Python changes are folder and size-switch plumbing, taste is in three profiles kept out of git, and the rehearsals and phone test were approved by the user.

---

_Verified: 2026-11-02_
_Verifier: Claude (gsd-verifier)_
