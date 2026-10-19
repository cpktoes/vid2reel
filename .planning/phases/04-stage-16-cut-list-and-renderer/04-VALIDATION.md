---
phase: 4
slug: stage-16-cut-list-and-renderer
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-10-19
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 via uv |
| **Config file** | pyproject.toml (`[tool.pytest.ini_options] testpaths = ["tests"]`, unchanged) |
| **Quick run command** | `uv run pytest tests/test_render_plan.py tests/test_cutlist_check.py tests/test_match.py -x -q` (no FFmpeg) |
| **Full suite command** | `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs" run-with-timeout 1500 -- uv run pytest -x -q` (macOS has no `timeout`; about seven minutes before this phase, a few more after it; 1500 s leaves room for the full-canvas golden renders). On a timeout: re-run the plan's own test files, then `uv run pytest -x -q -k "not golden"`, and report both run times in the SUMMARY |
| **Estimated runtime** | quick: under 10 seconds; each task's own render tests: under 2 minutes; full suite: about 10 to 12 minutes |

---

## Sampling Rate

- **After every task commit:** the task's own `<automated>` command (its test files, both shapes)
- **After every plan wave:** the full suite command above, run once in the last task of each plan
- **Before `/gsd-verify-work`:** full suite green (plan 10 Task 2), then the phone test (plan 11 Task 3)
- **Reel lengths:** plan 07 adds the rule that a reel lasts at least MIN_REEL_SECONDS (3 s) and render runs check first, so every render test of plans 01, 03, 05, 06, 08 and 09 renders a list of 3.5 s or more
- **Frame exactness:** the frame-index clip steps luma by 8 a frame (16 + 8 x (frame mod 25)) and every frame probe allows 2, so a one-frame slip reads at least 6 outside the tolerance (plans 01 and 09)
- **Max feedback latency:** under 2 minutes per task; the full suite once per plan

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 4-01-01 | 01 | 1 | CUT-02, CUT-03, CUT-07 | T-4-01, T-4-02, T-4-04, T-4-05, T-4-07 | numbers only in filters; plain names in the work folder; no metadata in the reel; .part then rename; originals untouched | tracer (e2e) | `uv run pytest tests/test_render_tracer.py tests/test_look_sheets.py -x -q` | created by the task | ⬜ pending |
| 4-01-02 | 01 | 1 | CUT-02, CUT-03, CUT-07 | T-4-03, T-4-06 | strict reading; echoed text cut to CUTLIST_ECHO_CHARS; clips block must match the work folder; a one-frame slip at a cut is visible | unit + integration | `uv run pytest tests/test_render_tracer.py -x -q` | ✅ (Task 1) | ⬜ pending |
| 4-02-01 | 02 | 1 | CUT-01, CUT-02 | T-4-SC | human check of five PyPI pages | checkpoint | (blocking-human) | — | ⬜ pending |
| 4-02-02 | 02 | 1 | CUT-01, CUT-02 | T-4-SC | pinned versions, regenerated requirements.txt | smoke | `uv run pytest tests/test_smoke.py tests/test_doctor.py -x -q` | ✅ | ⬜ pending |
| 4-03-01 | 03 | 2 | CUT-04, CUT-05 | — | every number in settings.py with its unit, guarded | unit | `uv run pytest tests/test_render_settings.py tests/test_look.py -k "settings or unit_comments" -x -q` | created by the task | ⬜ pending |
| 4-03-02 | 03 | 2 | CUT-03, CUT-07 | T-4-03, T-4-05 | refuses on a missing FFmpeg piece before building | unit + integration | `uv run pytest tests/test_doctor.py tests/test_render_tracer.py -k "doctor or missing or pieces or tracer" -x -q` | ✅ | ⬜ pending |
| 4-04-01 | 04 | 2 | CUT-01 | — | schema holds structure only | unit | `uv run pytest tests/test_cutlist_check.py -k schema -x -q` | created by the task | ⬜ pending |
| 4-04-02 | 04 | 2 | CUT-01, CUT-02, CUT-08 | T-4-03, T-4-06 | strict reading; echoed text cleaned | unit | `uv run pytest tests/test_cutlist_check.py tests/test_render_tracer.py -x -q` | ✅ (Task 1) | ⬜ pending |
| 4-05-01 | 05 | 3 | CUT-04 | — | N/A (pure) | unit | `uv run pytest tests/test_render_plan.py -x -q` | created by the task | ⬜ pending |
| 4-05-02 | 05 | 3 | CUT-03, CUT-04 | T-4-01, T-4-02 | numbers only in the move; photo path inside the work folder; a one-frame segment is its fitted crop | integration | `uv run pytest tests/test_render_video.py tests/test_render_plan.py -x -q` | created by the task | ⬜ pending |
| 4-06-01 | 06 | 3 | CUT-06 | T-4-02 | track files inside music/ | unit | `uv run pytest tests/test_render_sound.py -k "settings or runs or gain or library or track" -x -q` | created by the task | ⬜ pending |
| 4-06-02 | 06 | 3 | CUT-06, CUT-07 | T-4-01, T-4-13 | honest loudness figure | integration | `uv run pytest tests/test_render_sound.py tests/test_render_tracer.py -x -q` | ✅ (Task 1) | ⬜ pending |
| 4-07-01 | 07 | 4 | CUT-02 | T-4-03 | refuses, never clamps; the length rule refuses none of the stage's render tests | unit | `uv run pytest tests/test_cutlist_check.py -x -q` | ✅ | ⬜ pending |
| 4-07-02 | 07 | 4 | CUT-02 | T-4-02, T-4-06 | music paths checked; text cleaned | unit | `uv run pytest tests/test_cutlist_check.py tests/test_render_tracer.py -x -q` | ✅ | ⬜ pending |
| 4-08-01 | 08 | 4 | CUT-05 | T-4-05, T-4-07 | whole-or-nothing rewrite; stale look.json refused | unit | `uv run pytest tests/test_match.py -x -q` | created by the task | ⬜ pending |
| 4-08-02 | 08 | 4 | CUT-05 | T-4-01 | numbers only in lutyuv | integration | `uv run pytest tests/test_render_video.py tests/test_match.py -x -q` | ✅ | ⬜ pending |
| 4-09-01 | 09 | 5 | CUT-03, CUT-07 | T-4-05, T-4-03 | nothing half-made; overlong refused | integration | `uv run pytest tests/test_render_golden.py -k "cover or long or too_long or over_the_limit or failure or expected_files" -x -q` | created by the task | ⬜ pending |
| 4-09-02 | 09 | 5 | CUT-09 | T-4-09 | no media committed; frame probes see a one-frame slip | golden | `uv run pytest tests/test_render_golden.py -x -q` | ✅ (Task 1) | ⬜ pending |
| 4-10-01 | 10 | 6 | CUT-01 to CUT-09 | T-4-14 | no person or account named | docs grep | `grep -c "Stage 16 ·" docs/decisions.md` | ✅ | ⬜ pending |
| 4-10-02 | 10 | 6 | CUT-01 to CUT-09 | T-4-09 | branch scan before push | full suite + scan | the full suite command | ✅ | ⬜ pending |
| 4-11-01 | 11 | 7 | CUT-03 to CUT-09 | — | the user's own handbook text | checkpoint | (decision) | — | ⬜ pending |
| 4-11-02 | 11 | 7 | — | T-4-09, T-4-10 | push only on the user's word; main untouched | git | `git ls-remote origin stage-16-render` | — | ⬜ pending |
| 4-11-03 | 11 | 7 | CUT-03 to CUT-09 | — | N/A | phone test | (human-verify) | — | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

pytest and the test helpers already exist (tests/media.py). Every new test file is created by the task that needs it, test-first (`tdd="true"`), before its implementation, so no task's `<automated>` command points at a missing file:

- [ ] `tests/test_render_tracer.py` — plan 01 (CUT-02, CUT-03, CUT-07)
- [ ] `tests/test_render_settings.py` — plan 03 (CUT-04, CUT-05)
- [ ] `tests/cutlists.py`, `tests/test_cutlist_check.py` — plan 04 (CUT-01, CUT-02, CUT-08)
- [ ] `tests/test_render_plan.py`, `tests/test_render_video.py` — plan 05 (CUT-03, CUT-04)
- [ ] `tests/test_render_sound.py` — plan 06 (CUT-06)
- [ ] `tests/test_match.py` — plan 08 (CUT-05)
- [ ] `tests/test_render_golden.py` — plan 09 (CUT-07, CUT-09)
- [ ] `jsonschema` installed — plan 02, after the user's check of its PyPI pages

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| A photo's push-in reads as a slow drift, noticed only when looked for, with no tick or shimmer | CUT-04 | the user's eye on a phone is the judge (CONTEXT: the trickiest part) | plan 11 Task 3 step 3: watch the photo's first and last second |
| The touch-up makes clips look like one shoot and does not read as a filter | CUT-05 | taste, judged by eye | plan 11 Task 3 step 4: compare the cut between the two most different clips with and without it |
| The music drop under a kept laugh, the fades and the level against her feed | CUT-06 | Claude cannot hear | plan 11 Task 3 step 3: listen with earphones a third of a second either side of the kept shot |
| The sandbox installs jsonschema and rpds-py and its FFmpeg 6.1.1 has every render piece | CUT-07 | the sandbox is not reachable from the Mac | plan 11 Task 3 step 2: no install error, no MISSING in doctor |
| The same list pasted into a fresh chat makes the same reel | CUT-09 | phone-to-phone, across chats | plan 11 Task 3 step 8 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 4s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** {pending / approved YYYY-MM-DD}
