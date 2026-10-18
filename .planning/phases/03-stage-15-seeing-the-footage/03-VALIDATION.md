---
phase: 3
slug: stage-15-seeing-the-footage
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-10-17
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1, run through uv (`[tool.pytest.ini_options] testpaths = ["tests"]` in pyproject.toml) |
| **Config file** | pyproject.toml (existing; no change needed) |
| **Quick run command** | `uv run pytest tests/test_look.py -x -q` (or the plan's own test file: `tests/test_look_measure.py`, `tests/test_look_sheets.py`, `tests/test_look_extras.py`, `tests/test_look_candidates.py`, `tests/test_doctor.py`) |
| **Full suite command** | `uv run pytest -q` (on macOS, which has no `timeout`: `gsd-tools run-with-timeout 600 -- uv run pytest -q`) |
| **Estimated runtime** | about 300 seconds for the full suite (about 80 s before this phase, plus roughly 100 short look runs on generated 360x640 and 640x360 clips); 30 to 90 seconds for one plan's test file |

Every look test generates its clips with FFmpeg into tmp_path (tests/media.py) and is parametrised over both shapes, "tall" and "wide". No test reads fixtures/ or work/. Pure functions (half-second binning, peaks, extra-still choice, candidate windows, merging, reasons, the rhythm decision) are tested on hand-made numbers with no FFmpeg.

---

## Sampling Rate

- **After every task commit:** run the task's own `<automated>` command (the plan's test file, filtered with `-k`)
- **After every plan wave:** run `uv run pytest -q`
- **Before `/gsd-verify-work`:** full suite green, plus the manual checks below (phone doctor, blind test, phone sheet test)
- **Max feedback latency:** 90 seconds per task command; about 300 seconds per wave

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 3-01-01 | 01 | 1 | LOOK-01, LOOK-02, LOOK-03, LOOK-06 | T-3-03, T-3-13 | FFmpeg called with list arguments, no shell, no file name in a filter string; look.json has no NaN | integration + unit | `uv run pytest tests/test_look.py -k "tracer or label or half_count or frame_number or base_times" -x -q` | ❌ W0 (the task creates tests/test_look.py) | ⬜ pending |
| 3-01-02 | 01 | 1 | LOOK-01, LOOK-03 | T-3-01, T-3-02, T-3-06, T-3-07 | working.file must be a plain name inside the work folder; only look's own outputs are deleted; originals, working copies and the manifest stay byte-identical | integration | `uv run pytest tests/test_look.py -x -q` | ❌ W0 | ⬜ pending |
| 3-02-01 | 02 | 1 | LOOK-03 | T-3-15 | N/A (doctor lists names from one local FFmpeg call) | unit | `uv run pytest tests/test_doctor.py -x -q` | ✅ | ⬜ pending |
| 3-02-02 | 02 | 1 | LOOK-05 | T-3-05 | no person, account or fixture file named in docs | source grep | `grep -c "2026-10-17 · Stage 15 ·" docs/decisions.md && grep -c "PySceneDetect" docs/licenses.md && grep -cx "/look.log" .gitignore && grep -c "\| look \| build-skill" CLAUDE.md` | ✅ | ⬜ pending |
| 3-03-01 | 03 | 2 | LOOK-03 | T-3-09 | push only on the user's word | manual (decision) | — (checkpoint) | n/a | ⬜ pending |
| 3-03-02 | 03 | 2 | LOOK-03, LOOK-05 | T-3-09, T-3-10 | privacy scan of the branch diff before push; main untouched | integration | `uv run pytest -q && ! (uv run python -m v2r doctor \| grep -q MISSING)` | ✅ | ⬜ pending |
| 3-03-03 | 03 | 2 | LOOK-03, LOOK-05 | T-3-16 | report recorded without names | manual (phone) | — (checkpoint: doctor from the phone) | n/a | ⬜ pending |
| 3-04-01 | 04 | 2 | LOOK-03, LOOK-06 | T-3-03, T-3-04 | fixed text-file names in a temp folder; proportional timeout | integration + unit | `uv run pytest tests/test_look_measure.py -k "camera or shot_change or parse_motion or chain_order" -x -q` | ❌ W0 (the task creates tests/test_look_measure.py) | ⬜ pending |
| 3-04-02 | 04 | 2 | LOOK-03, LOOK-06 | T-3-13 | nan from blurdetect becomes null | integration | `uv run pytest tests/test_look_measure.py -k "sharpness or brightness or colour or flat or chain_order" -x -q` | ❌ W0 | ⬜ pending |
| 3-04-03 | 04 | 2 | LOOK-03, LOOK-05, LOOK-06 | T-3-03, T-3-04, T-3-13 | a missing filter gives null and one sentence, never a failed run | integration + unit | `uv run pytest tests/test_look_measure.py -x -q` | ❌ W0 | ⬜ pending |
| 3-05-01 | 05 | 2 | LOOK-01, LOOK-06 | T-3-02 | sheet names come from a counter, written by temp name then rename | integration | `uv run pytest tests/test_look_sheets.py -k "sheets_" -x -q` | ❌ W0 (the task creates tests/test_look_sheets.py) | ⬜ pending |
| 3-05-02 | 05 | 2 | LOOK-01, LOOK-06 | T-3-08 | at most MAX_SHEETS_PER_RUN sheets | unit + integration | `uv run pytest tests/test_look_sheets.py -k "run_interval or cap_" -x -q` | ❌ W0 | ⬜ pending |
| 3-05-03 | 05 | 2 | LOOK-01 | T-3-08, T-3-14 | byte guard; no untrusted image opened; ENOSPC stops with a sentence | integration | `uv run pytest tests/test_look_sheets.py -x -q` | ❌ W0 | ⬜ pending |
| 3-06-01 | 06 | 3 | LOOK-02 | T-3-17 | frame numbers clamped to the last frame | unit | `uv run pytest tests/test_look_extras.py -x -q` | ❌ W0 (the task creates tests/test_look_extras.py) | ⬜ pending |
| 3-06-02 | 06 | 3 | LOOK-02, LOOK-06 | T-3-04 | extras capped, so commands and sheets stay bounded | integration | `uv run pytest tests/test_look_extras.py -x -q` | ❌ W0 | ⬜ pending |
| 3-07-01 | 07 | 4 | LOOK-04 | T-3-18 | no selected field; facts-only reasons | unit | `uv run pytest tests/test_look_candidates.py -x -q` | ❌ W0 (the task creates tests/test_look_candidates.py) | ⬜ pending |
| 3-07-02 | 07 | 4 | LOOK-04, LOOK-06 | T-3-07, T-3-18 | reasons built from fixed phrases and real still labels only | integration | `uv run pytest tests/test_look_candidates.py -x -q` | ❌ W0 | ⬜ pending |
| 3-08-01 | 08 | 5 | LOOK-07 | T-3-05, T-3-06 | executor writes only work/check-look/, never the work/ root or fixtures/ | integration | `uv run pytest -q && test -f work/check-look/look.json && test -f work/check-look/sheets/sheet-01.jpg` | ✅ | ⬜ pending |
| 3-08-02 | 08 | 5 | LOOK-07 | T-3-05 | misses logged in fixtures/reel-log.md, never committed | manual (blind test) | — (checkpoint) | n/a | ⬜ pending |
| 3-09-01 | 09 | 6 | LOOK-01 | — | EDITOR.md written by the user, never by a task | manual (decision) | — (checkpoint) | n/a | ⬜ pending |
| 3-09-02 | 09 | 6 | LOOK-01, LOOK-07 | T-3-09, T-3-10 | privacy scan before push; main untouched | integration | `grep -q "v2r look" EDITOR.md && grep -q "look.log" EDITOR.md && uv run pytest -q && ! (uv run python -m v2r doctor \| grep -q MISSING)` | ✅ | ⬜ pending |
| 3-09-03 | 09 | 6 | LOOK-01, LOOK-07 | T-3-07 | look.json read as data by the chat | manual (phone) | — (checkpoint: phone sheet test and a reel) | n/a | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

No framework install: pytest, `tests/media.py` and the both-shapes test style already exist. Each code plan's first task creates its own test file test-first, so the "❌ W0" rows are filled by the task itself:

- [ ] `tests/test_look.py` — plan 01 (tracer, labels, half-second count, frame clamp, run robustness), LOOK-01, LOOK-02, LOOK-03, LOOK-06
- [ ] `tests/test_look_measure.py` — plan 04 (camera, shake, subject, shot changes, sharpness, brightness, colour, loudness, missing filters, parser edges), LOOK-03, LOOK-05, LOOK-06
- [ ] `tests/test_look_sheets.py` — plan 05 (continuous fill, one orientation per sheet, cap and thinning, byte guard, no Pillow, no select, no font, full disk), LOOK-01, LOOK-06
- [ ] `tests/test_look_extras.py` — plan 06 (peaks, gap in frames, cap and order, known-answer stills), LOOK-02, LOOK-06
- [ ] `tests/test_look_candidates.py` — plan 07 (windows, exclusions, ranking, merging, facts-only reasons), LOOK-04, LOOK-06
- [ ] `tests/media.py` additions — `make_manifest` (plan 01), `make_look_clip` (plan 04), `white_share` and `make_bursts_clip` (plan 06)
- [ ] `tests/test_doctor.py` additions — plan 02 (`LOOK_FILTERS`), existing file

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The sandbox's FFmpeg 6.1 lists every look filter (select, signalstats, blurdetect, scdet, deshake, ebur128, metadata, ametadata) | LOOK-03, LOOK-05 (D-20) | Only the phone reaches the sandbox; the Mac has FFmpeg 8.0 | Plan 03, Task 3: attach two clips, type "use branch stage-15-look. Show me the doctor report in full", paste the report back; every look filter line should say available |
| From a sheet alone one can say what happens in a clip | LOOK-01 | Readability is judged by eye | Plan 08, Task 2: run normalize and look on a fixture set on the Mac, open work/sheets/ in Finder |
| Blind test: Claude picks the user's moment in at least four of five clips | LOOK-07 | Checked by a person by definition | Plan 08, Task 2: Claude Code after /clear, the guide's prompt per clip, compare with the clip, log misses in fixtures/reel-log.md, change one setting at a time until four of five |
| Sheets readable on the phone, description cites labels, wide run, a reel made on the branch | LOOK-01, LOOK-07 | The phone and the sandbox are the truth (CLAUDE.md) | Plan 09, Task 3: attach three clips, type "use branch stage-15-look. Show me the contact sheets and tell me what happens in each clip", then the wide run and a reel |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or are checkpoint tasks that only a person can do
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (each test file is created by the first task of its plan)
- [x] No watch-mode flags
- [x] Feedback latency < 90s per task command
- [ ] `nyquist_compliant: true` set in frontmatter (set by validate-phase)

**Approval:** pending
