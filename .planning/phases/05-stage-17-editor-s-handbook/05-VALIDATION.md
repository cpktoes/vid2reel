---
phase: 5
slug: stage-17-editor-s-handbook
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-10-24
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x (dev dependency, via uv) |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options] testpaths = ["tests"]`) |
| **Quick run command** | `uv run pytest tests/test_editor_handbook.py tests/test_work_option.py -q` |
| **Full suite command** | `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs" run-with-timeout 1800 -- uv run pytest -q` (macOS has no `timeout`) |
| **Estimated runtime** | quick run about 20 seconds (the `--work` tests convert tiny generated clips); full suite about 1,000 tests in 11 to 19 minutes |

---

## Sampling Rate

- **After every task commit:** Run the quick run command (only the files that exist yet)
- **After every plan wave:** Wave 1: the bounded run of tests/test_work_option.py, tests/test_normalize.py, tests/test_look*.py, tests/test_cutlist_check.py, tests/test_smoke.py (plan 01 Task 2) plus tests/test_editor_handbook.py; waves 2 and 3 change only EDITOR.md and private files, so tests/test_editor_handbook.py after each EDITOR.md change
- **Before `/gsd-verify-work`:** Full suite must be green (plan 06 Task 1), the human checks recorded, and the phone test approved (plan 07 Task 1)
- **Max feedback latency:** about 20 seconds for the quick run

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 5-01-01 | 01 | 1 | HAND-02 | T-5-01 | `--work` writes only into the named folder; the default work folder is never touched (tall and wide) | integration (tracer) | `uv run pytest tests/test_work_option.py -q -k tracer` | ❌ W0, created by this task | ⬜ pending |
| 5-01-02 | 01 | 1 | HAND-02 | T-5-01, T-5-08 | an original inside the `--work` folder keeps its sha256; look given two different folders refuses with one sentence | integration | `uv run pytest tests/test_work_option.py tests/test_smoke.py -q` | ❌ W0, file from 5-01-01 | ⬜ pending |
| 5-02-01 | 02 | 1 | HAND-01, HAND-02 | T-5-10 | EDITOR.md names only real commands and never the Mac-only option | unit | `uv run pytest tests/test_editor_handbook.py -q` | ❌ W0, created by this task | ⬜ pending |
| 5-02-02 | 02 | 1 | HAND-01 | T-5-10 | each guard fires on a bad text; 1,200 words pass and 1,201 fail | unit | `uv run pytest tests/test_editor_handbook.py -q` | ❌ W0, file from 5-02-01 | ⬜ pending |
| 5-03-01 | 03 | 1 | HAND-03 | T-5-03, T-5-09 | profiles git-ignored; no private name in any tracked file | shell | `git check-ignore -v fixtures/profiles && test "$(git ls-files fixtures work \| wc -l \| tr -d ' ')" = 0` | ✅ (git) | ⬜ pending |
| 5-03-02 | 03 | 1 | HAND-04 | T-5-03, T-5-01 | the rehearsal kit holds placeholders only and always names a fresh work/<SET> | shell | `grep -c "stepping out of the role" .planning/phases/05-stage-17-editor-s-handbook/05-REHEARSAL.md` | ❌ W0, created by this task | ⬜ pending |
| 5-03-03 | 03 | 1 | HAND-03 | T-5-03 | profiles reviewed by their owners and pasted into each Project | manual | see Manual-Only | n/a | ⬜ pending |
| 5-04-01 | 04 | 2 | HAND-01, HAND-02 | T-5-05 | nothing enters EDITOR.md without the user's word | manual | see Manual-Only | n/a | ⬜ pending |
| 5-04-02 | 04 | 2 | HAND-01, HAND-02 | T-5-05, T-5-03 | EDITOR.md equals the approved text; guards pass; names scan prints 0 | unit + diff | `uv run pytest tests/test_editor_handbook.py -q` | ✅ from 5-02 | ⬜ pending |
| 5-04-03 | 04 | 2 | HAND-01, HAND-02 | — | the user reads the handbook against the twelve-line checklist | manual | see Manual-Only | n/a | ⬜ pending |
| 5-05-01 | 05 | 3 | HAND-04 | T-5-04 | each rehearsal in its own fresh session | manual | see Manual-Only | n/a | ⬜ pending |
| 5-05-02 | 05 | 3 | HAND-04 | T-5-03 | every rehearsal's list passes check; nothing private becomes tracked | shell | `test "$(git ls-files fixtures work \| wc -l \| tr -d ' ')" = 0 && test -d fixtures/rehearsals/round-1` | ✅ (git) | ⬜ pending |
| 5-05-03 | 05 | 3 | HAND-04, HAND-05 | — | scores, pair verdict, three of five | manual | see Manual-Only | n/a | ⬜ pending |
| 5-06-01 | 06 | 4 | HAND-02, HAND-03 | T-5-03 | full suite green; only v2r/__main__.py changed in v2r/; the push range holds nothing private | full suite + scan | `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs" run-with-timeout 1800 -- uv run pytest -q` | ✅ | ⬜ pending |
| 5-06-02 | 06 | 4 | HAND-03 | T-5-03 | push and any scrub only on the user's word | manual | see Manual-Only | n/a | ⬜ pending |
| 5-06-03 | 06 | 4 | HAND-02 | T-5-06 | the branch on GitHub equals local HEAD; origin/main unchanged | shell | `test "$(git ls-remote origin stage-17-handbook \| cut -f1)" = "$(git rev-parse HEAD)"` | ✅ (git) | ⬜ pending |
| 5-07-01 | 07 | 5 | HAND-01 to HAND-05 | — | a reel from her phone inside one of her Projects on the branch | manual | see Manual-Only | n/a | ⬜ pending |
| 5-07-02 | 07 | 5 | HAND-01 to HAND-05 | T-5-03, T-5-06 | records written, scan clean, branch pushed again | shell | `grep -c "\| HAND-01 to HAND-05 \| Phase 5 – Stage 17 – Editor's handbook \| Complete \|" .planning/REQUIREMENTS.md` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_work_option.py` — created by plan 01 Task 1 (the tracer), its own `small_caps` and `default_work` fixtures (HAND-02, D-09)
- [ ] `tests/test_editor_handbook.py` — created by plan 02 Task 1 (HAND-01)
- [ ] `.planning/phases/05-stage-17-editor-s-handbook/05-REHEARSAL.md` — created by plan 03 Task 2 (HAND-04)
- [ ] Branch `stage-17-handbook` — created from main by hand by the orchestrator before any executor
- Framework install: none (pytest already in the dev group)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Profiles reviewed with their owners, [check] lines settled, each pasted into its Project under Reel style | HAND-03 | the owners' own taste; the Claude app has no command line | plan 03 Task 3; Claude re-counts [check] lines and `git ls-files fixtures` afterwards |
| The user's word on EDITOR.md (corrections, cuts, or his own edit) | HAND-01, HAND-02 | D-08: the handbook is his text | plan 04 Task 1; Task 2 pastes exactly that and diffs it |
| The user reads EDITOR.md against the twelve-line checklist; no one person's taste in it | HAND-01, HAND-02 | judging plain words and taste needs a person | plan 04 Task 3 |
| Five rehearsals and the second-profile run, each in a fresh Claude Code session after /clear | HAND-04 | D-10: a session that has read the planning files cannot stand in for the phone's Claude | plan 05 Task 1 with 05-REHEARSAL.md; Task 2 checks the folders |
| The profile pair differs only where the profiles differ | HAND-04 | the reels must be watched; run-to-run noise needs a person's eye (optional control run) | plan 05 Task 3 with Task 2's category table |
| She would post at least three of the five with small changes | HAND-05 | Claude cannot watch video or hear audio | plan 05 Task 3; scores in fixtures/reel-log.md, count in the SUMMARY |
| Push to GitHub, and any scrub of unsent history | HAND-03 | a push to a public repo cannot be taken back | plan 06 Task 2 (checkpoint:decision) |
| A reel made from her phone inside one of her Projects on the branch | HAND-01 to HAND-05 | CLAUDE.md's merge rule; the sandbox (FFmpeg 6.1, 30 MiB, 2 minutes) exists only on the phone | plan 07 Task 1, with what to look for and when |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** {pending / approved YYYY-MM-DD}
