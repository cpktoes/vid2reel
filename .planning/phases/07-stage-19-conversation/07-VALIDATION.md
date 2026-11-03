---
phase: 7
slug: stage-19-conversation
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-11-03
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x (dev dependency, via uv) |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| **Quick run command** | `uv run pytest tests/test_revise.py tests/test_cutlist_check.py tests/test_editor_handbook.py tests/test_render_settings.py -q` (only the files that exist yet; tests/test_revise.py appears with plan 01 Task 1) |
| **Full suite command** | `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs" run-with-timeout 1800 -- uv run pytest -q` (macOS has no `timeout`) |
| **Estimated runtime** | quick run about 20 to 30 seconds (measured 25 s for the three files that exist today; revise's tests use placeholder work folders, no FFmpeg); tests/test_revise_chain.py renders generated clips, well under two minutes; full suite about 1,100 tests in about 15 minutes |

---

## Sampling Rate

- **After every task commit:** Run the quick run command (the files that exist yet), plus the task's own `<automated>` command
- **After every plan wave:**
  - Wave 1 (plan 01): the quick run plus `uv run pytest tests/test_match.py -q`
  - Wave 2 (plans 02 and 03): the quick run plus `uv run pytest tests/test_match.py tests/test_render_tracer.py -q` (FFmpeg, about a minute; plan 02 Task 2)
  - Wave 3 (plan 04): the quick run plus `uv run pytest tests/test_match.py -q`
  - Wave 4 (plan 05): the quick run plus `uv run pytest tests/test_revise_chain.py -q`
  - Waves 5 and 6 (plans 06 and 07) change only the draft, EDITOR.md and private files: `uv run pytest tests/test_editor_handbook.py -q` after every EDITOR.md change
  - Wave 7 (plan 08): the full suite command
  - Wave 8 (plan 09): `uv run pytest tests/test_revise_chain.py tests/test_revise.py tests/test_editor_handbook.py -q` on the pushed commit
- **Before `/gsd-verify-work`:** Full suite must be green (plan 08 Task 1), the rehearsals approved (plan 07 Task 3), and the phone test approved (plan 09 Task 2)
- **Max feedback latency:** about 30 seconds for the quick run

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 7-01-01 | 01 | 1 | CONV-05, CONV-06 | T-7-01, T-7-02, T-7-03, T-7-04 | the input list's bytes never change; the new list is created exclusively beside it; a bad shot word is refused in one sentence before int(); revise's limits are read from settings.py | unit (tracer, TDD) | `uv run pytest tests/test_revise.py tests/test_render_settings.py -q` | ❌ created by this task (tests first) | ⬜ pending |
| 7-01-02 | 01 | 1 | CONV-05 | — | only the canvas width and height change; a shape mismatch is check's own refusal | unit (TDD) | `uv run pytest tests/test_revise.py -q` | ✅ from 7-01-01 | ⬜ pending |
| 7-01-03 | 01 | 1 | CONV-01, CONV-04, CONV-05, CONV-07 | T-7-05 | the records name no person, account, set or path; CLAUDE.md states the brief once | grep | `grep -cF '"shorter", "mute it" and "a wide version"' .planning/REQUIREMENTS.md .planning/ROADMAP.md && grep -c "· Stage 19 ·" docs/decisions.md && grep -cF "the brief is asked straight away" CLAUDE.md && grep -cF "are now the first two of the Stage 19 brief below" CLAUDE.md` | ✅ | ⬜ pending |
| 7-02-01 | 02 | 2 | CONV-05 | T-7-06 | a recipe other than lively or calm is refused by the schema before it is used as a settings key; recipe notes never refuse | unit (tracer, TDD) | `uv run pytest tests/test_cutlist_check.py tests/test_render_settings.py -q` | ✅ | ⬜ pending |
| 7-02-02 | 02 | 2 | CONV-05 | T-7-07 | a list naming no recipe is read as Lively with one note | unit (TDD) | `uv run pytest tests/test_cutlist_check.py tests/test_match.py -q` | ✅ | ⬜ pending |
| 7-02-03 | 02 | 2 | CONV-05 | — | EDITOR.md's recipe numbers and settings.RECIPES cannot drift apart; EDITOR.md is never edited by the test | unit (TDD) | `uv run pytest tests/test_editor_handbook.py -q` | ✅ | ⬜ pending |
| 7-03-01 | 03 | 2 | CONV-05, CONV-06 | T-7-04, T-7-08 | an order list longer than MAX_SEGMENTS is refused before any conversion; each record moves whole; the cover follows its shot | unit (tracer, TDD) | `uv run pytest tests/test_revise.py -q` | ✅ from 7-01-01 | ⬜ pending |
| 7-03-02 | 03 | 2 | CONV-05, CONV-06 | T-7-08, T-7-03 | a drop word is checked against the clip-letter pattern before use; the clips block and touch-up stay; the cover follows or clears | unit (TDD) | `uv run pytest tests/test_revise.py -q` | ✅ from 7-01-01 | ⬜ pending |
| 7-04-01 | 04 | 3 | CONV-05, CONV-06 | T-7-09, T-7-04 | --to takes only plain digits within settings' limits and MAX_CUTLIST_SECONDS; every target is met to the frame; no first frame moves | unit and property loops (tracer, TDD) | `uv run pytest tests/test_revise.py tests/test_render_settings.py -q` | ✅ from 7-01-01 | ⬜ pending |
| 7-04-02 | 04 | 3 | CONV-05, CONV-06 | T-7-10 | no shot runs past its clip's end or into a later shot of the same clip | unit (TDD) | `uv run pytest tests/test_revise.py -q` | ✅ from 7-01-01 | ⬜ pending |
| 7-05-01 | 05 | 4 | CONV-05, CONV-07 | T-7-11, T-7-12 | every command gets --work inside tmp_path; clips are generated, nothing read from fixtures/; earlier lists and reels keep their sha256 | integration, FFmpeg (tracer) | `uv run pytest tests/test_revise_chain.py -q` | ❌ created by this task | ⬜ pending |
| 7-05-02 | 05 | 4 | CONV-05 | — | README documents revise and its --cutlist and --work | grep | ``grep -c '`revise CHANGE`' README.md`` | ✅ | ⬜ pending |
| 7-06-01 | 06 | 5 | CONV-01, CONV-02, CONV-03, CONV-04, CONV-06 | T-7-14 | the draft names no Mac-only switch; its revise calls ran on a scratch list outside the repo; EDITOR.md untouched | script check (tracer) | the `uv run python -c` draft check in 07-06 Task 1's verify (the body holds "Talking with her" and `python3 -m v2r revise`, and no Mac-only switch) | ❌ created by this task | ⬜ pending |
| 7-06-02 | 06 | 5 | CONV-01 to CONV-04, CONV-06 | T-7-13 | nothing enters EDITOR.md without the user's word | manual | see Manual-Only | n/a | ⬜ pending |
| 7-06-03 | 06 | 5 | CONV-01 to CONV-04, CONV-06 | T-7-13, T-7-15 | EDITOR.md equals the approved text; every revise call it writes is real; the handle and e-mail greps print 0 | unit and diff | `uv run pytest tests/test_editor_handbook.py -q` | ✅ from 7-02-03 | ⬜ pending |
| 7-07-01 | 07 | 6 | CONV-01 to CONV-04, CONV-06 | T-7-16, T-7-18 | the kit holds blanks only; its after-run commands were proven on a scratch list outside the repo | shell | `test -f .planning/phases/07-stage-19-conversation/07-REHEARSAL.md && grep -c "end of rehearsal" .planning/phases/07-stage-19-conversation/07-REHEARSAL.md` | ❌ created by this task | ⬜ pending |
| 7-07-02 | 07 | 6 | CONV-01 to CONV-04, CONV-06 | T-7-17 | each rehearsal runs in its own fresh session | manual | see Manual-Only | n/a | ⬜ pending |
| 7-07-03 | 07 | 6 | CONV-01 to CONV-04, CONV-06 | T-7-13, T-7-16 | the cases and the brief test judged by watching; EDITOR.md changes only as the user's text | manual | see Manual-Only | n/a | ⬜ pending |
| 7-08-01 | 08 | 7 | CONV-05, CONV-07 | T-7-19 | full suite green; only the five expected v2r files changed; the push range holds nothing private and no attribution line | full suite and scan (tracer) | `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs" run-with-timeout 1800 -- uv run pytest -q`, then 07-08 Task 1's verify gates | ✅ | ⬜ pending |
| 7-08-02 | 08 | 7 | CONV-07 | T-7-19, T-7-21 | the user's own names scan, and the push only on his word | manual | see Manual-Only | n/a | ⬜ pending |
| 7-08-03 | 08 | 7 | CONV-07 | T-7-20 | the branch on GitHub equals local HEAD; origin/main unchanged; never --force | shell | `test "$(git ls-remote origin stage-19-conversation \| cut -f1)" = "$(git rev-parse HEAD)"` | ✅ (git) | ⬜ pending |
| 7-09-01 | 09 | 8 | CONV-07 | T-7-23 | the phone fetches the very commit the chain test passed on | shell and tests (tracer) | `test "$(git ls-remote origin stage-19-conversation \| cut -f1)" = "$(git rev-parse HEAD)" && uv run pytest tests/test_revise_chain.py tests/test_revise.py tests/test_editor_handbook.py -q` | ✅ | ⬜ pending |
| 7-09-02 | 09 | 8 | CONV-01 to CONV-07 | — | the whole conversation from a phone inside a Project on the branch | manual | see Manual-Only | n/a | ⬜ pending |
| 7-09-03 | 09 | 8 | CONV-01 to CONV-07 | T-7-22, T-7-20 | the records name no one; the closing commits are scanned and not pushed | grep | `grep -c "\| CONV-01 to CONV-07 \| Phase 7 – Stage 19 – Conversation \| Complete \|" .planning/REQUIREMENTS.md && grep -c "^\| 19 \|" docs/phone-limits.md` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements: pytest is already in the dev group, and tests/cutlists.py (placeholder work folders and the approved example lists) and tests/media.py (generated clips) already exist. The two new test files are written test-first by the tasks that need them (tests/test_revise.py by plan 01 Task 1, tests/test_revise_chain.py by plan 05 Task 1), so no task depends on a file a Wave 0 would have to create.

- Framework install: none
- Branch `stage-19-conversation`: already exists and is checked out (every plan stops if `git branch --show-current` prints anything else)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The user's word on the handbook draft (items, cuts, the 1,800 cap, or his own edit) | CONV-01 to CONV-04, CONV-06 | D-17: EDITOR.md is his text | 07-06 Task 2; Task 3 pastes exactly that, diffs it and runs the guards |
| The rehearsals, each in a fresh Claude Code window after /clear, answering the brief turn by turn, with the kit's after-run checks | CONV-01 to CONV-04, CONV-06 | no command can open a session that knows nothing of this project; a session that has read .planning/ cannot stand in for the phone's Claude | 07-07 Task 2 with 07-REHEARSAL.md; he reports check exit codes and the case 8 diffs |
| Each case judged against the kit, the follow-up chain watched, and the briefed reel against "just make it" | CONV-01 to CONV-04, CONV-06 | Claude cannot watch video or hear audio; "clearly better" and "fits the reel" are a person's judgement | 07-07 Task 3, with what to look for and at what second |
| The user's own private-names scan over the push range, and his word on the push | CONV-07 | only he holds the private words; a push to a public repo cannot be taken back | 07-08 Task 2 (checkpoint:decision) |
| The whole conversation from a phone inside a Project with a Reel style section, on the branch: the brief, a reel, then "shorter", "mute it" and "a wide version", timed from send to saved | CONV-01 to CONV-07 | CLAUDE.md's merge rule; the sandbox (FFmpeg 6.1, 30 MiB, 2 minutes) exists only on the phone | 07-09 Task 2, with what to look and listen for and when; a fix returns through 07-08 Tasks 1 to 3 before the repeat |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (every auto and tracer task has one; the five manual items are checkpoints)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (the longest run is 7-07-02 and 7-07-03, then 7-08-01)
- [x] Wave 0 covers all MISSING references (none: the new test files are written test-first by their own tasks)
- [x] No watch-mode flags
- [x] Feedback latency under 30 s for the quick run
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-11-03 (planner, after the checker's review; status stays draft until validate-phase marks it validated)
