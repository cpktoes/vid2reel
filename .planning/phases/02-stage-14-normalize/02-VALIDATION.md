---
phase: 2
slug: stage-14-normalize
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-10-13
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest >=9.1.1 (dev dependency in pyproject.toml) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options] testpaths = ["tests"]` |
| **Quick run command** | `uv run pytest tests/test_normalize.py -x -q` |
| **Full suite command** | `uv run pytest -q` |
| **Estimated runtime** | ~40 seconds today (the join tests' 100 s clips dominate); normalize tests add generated clips, keep each ffmpeg call under a `timeout=` |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/test_normalize.py -x -q`
- **After every plan wave:** Run `uv run pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green, then the user's phone test on branch `stage-14-normalize` before merging
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-T1 (tracer) | 01 | 1 | NORM-01, NORM-02, NORM-05 | T-2-01, T-2-02, T-2-05, T-2-11 | one ordinary generated clip becomes A.mp4 + manifest.json in both shapes through the CLI; shape required; creates tests/media.py and tests/test_normalize.py (Wave 0) | integration | `uv run pytest tests/test_normalize.py -k tracer -x -q` | ❌ created by this task | ⬜ pending |
| 02-01-T2 | 01 | 1 | NORM-01, NORM-02 | T-2-01 | full fact sheet; size table; sideways marker upright (rotation applied once); shot_at; edge rows NORM-01 encoding, NORM-02 adjacency and the one-frame half of NORM-02 empty | integration + unit | `uv run pytest tests/test_normalize.py -k "tracer or facts or upright or working_size" -x -q` | ✅ after T1 | ⬜ pending |
| 02-01-T3 | 01 | 1 | NORM-01, NORM-02, NORM-05 | T-2-08, T-2-11 | 60 fps and uneven timing to constant 30 with sound in step; silence added; short sound padded; a new run replaces only lettered files (D-18); edge rows NORM-01 adjacency and ordering, NORM-02 ordering, NORM-05 ordering and the silence half of NORM-02 empty | integration | `uv run pytest tests/test_normalize.py -x -q` | ✅ after T1 | ⬜ pending |
| 02-02-T1 | 02 | 1 | NORM-08 | T-2-12 | doctor lists the new filters and decoders; `missing_ffmpeg_features()` without network | unit | `uv run pytest tests/test_doctor.py -x -q` | ❌ created by this task | ⬜ pending |
| 02-02-T2 | 02 | 1 | (docs for D-01, D-08, D-11, D-19, D-21) | T-2-09, T-2-13 | five dated Stage 14 lines; CLAUDE.md settled list; /normalize.log ignored | grep | `grep -c "2026-10-13 · Stage 14 ·" docs/decisions.md` | ✅ | ⬜ pending |
| 02-03-T1 | 03 | 4 | NORM-03 | T-2-SC | the user checks both PyPI pages before any install | manual (blocking-human) | — checkpoint | — | ⬜ pending |
| 02-03-T2 | 03 | 4 | NORM-03 | T-2-SC, T-2-14 | pillow + pillow-heif 1.8.x pinned; Linux wheels proven; docs/licenses.md | smoke | `uv run python -c "import PIL, pillow_heif" && grep -E "^pillow-heif==1\.8\." requirements.txt && uv run pytest -q` | ✅ | ⬜ pending |
| 02-04-T1 | 04 | 2 | NORM-02 | T-2-16 | HLG flat patch tone-mapped (luma below 112), not relabelled; PQ and gamut-only convert; colour facts explicit | integration | `uv run pytest tests/test_normalize.py -k hdr -x -q` | ✅ | ⬜ pending |
| 02-04-T2 | 04 | 2 | NORM-02, NORM-04 | T-2-04 | tone-map failure gives a done clip with the D-13 sentence; 120 fps flagged and real time; 60 fps not flagged | integration | `uv run pytest tests/test_normalize.py -k "fallback or slow" -x -q` | ✅ | ⬜ pending |
| 02-05-T1 | 05 | 3 | NORM-05, NORM-06 | T-2-03, T-2-04, T-2-07 | oversized, missing and unreadable files get one sentence naming the file; letters kept; exit codes; out-of-room stop; count limit not enforced | integration | `uv run pytest tests/test_normalize.py -k "refuse or unreadable or manifest" -x -q` | ✅ | ⬜ pending |
| 02-05-T2 | 05 | 3 | NORM-07, NORM-08 | T-2-05, T-2-08, T-2-12 | SHA-256 and st_mtime_ns unchanged; read-only inputs; inside-work input skipped not deleted; no partial files; doctor start-up check; every graph filter listed; no location or device tags | integration + unit | `uv run pytest tests/test_normalize.py -k "original or doctor" -x -q` | ✅ | ⬜ pending |
| 02-06-T1 | 06 | 5 | NORM-03 | T-2-03, T-2-05 | JPEG with orientation 6 turned upright once; full-size copy without EXIF; PHOTO_SECONDS x 30 frame still with silence; fast; lazy import | integration | `uv run pytest tests/test_normalize.py -k photo -x -q` | ✅ | ⬜ pending |
| 02-06-T2 | 06 | 5 | NORM-03 | T-2-05, T-2-14 | HEIC, RGBA PNG, ICC to sRGB, missing-library sentence, no EXIF in copies, mixed order, photo edge rows, photo graph filters listed | integration | `uv run pytest tests/test_normalize.py -k "photo or doctor" -x -q` | ✅ | ⬜ pending |
| 02-07-T1 | 07 | 6 | NORM-02 | T-2-09 | all fixtures converted on the Mac in both shapes into work/ only; table (sideways clips above 30 fps timed in their own row) and strips; nothing committed | smoke | python check that every work/check-*/set-*/manifest.json has finished true (see plan 07) | — | ⬜ pending |
| 02-07-T2 | 07 | 6 | NORM-02 | — | the user picks the tone-map pair by eye | manual (decision) | — checkpoint | — | ⬜ pending |
| 02-07-T3 | 07 | 6 | NORM-02 | — | chosen pair in settings.py and docs/decisions.md; suite green | full suite | `uv run pytest -q` | ✅ | ⬜ pending |
| 02-08-T1 | 08 | 7 | (D-16) | T-2-06 | the user writes the EDITOR.md normalize step | manual (decision) | — checkpoint | — | ⬜ pending |
| 02-08-T2 | 08 | 7 | NORM-08 | T-2-09, T-2-17 | privacy scan of the branch; suite green; doctor has no MISSING; push only with permission | scan + full suite | see plan 08 Task 2 verify | ✅ | ⬜ pending |
| 02-08-T3 | 08 | 7 | NORM-02, NORM-03, NORM-04, NORM-08 | — | phone test on the branch, including a reel | manual (human-verify) | — checkpoint | — | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Filled in by the planner from 02-01-PLAN.md to 02-08-PLAN.md. Every `-k` keyword above matches test names those plans define.*

---

## Wave 0 Requirements

- [ ] `tests/media.py` — created by 02-01-T1 (tracer) and grown by 02-01-T2 (sideways, marker, metadata), 02-01-T3 (VFR, short sound, peak_volume), 02-04-T1 (HDR, flat patch), 02-05 (audio-only, sha256, filter_names) and 02-06-T1 (JPEG, PNG, HEIC photos)
- [ ] `tests/test_normalize.py` — created by 02-01-T1 with the tracer test, parametrised over `shape in ["tall", "wide"]`; each later task adds its own tests
- [ ] `uv add pillow "pillow-heif>=1.8,<1.9"` — 02-03-T2 (wave 4, alone, so `uv add` never runs while another plan runs `uv run`), only after the blocking human check 02-03-T1; requirements.txt regenerated with the README command; HEIC tests (02-06-T2) need `pillow_heif.register_heif_opener()`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| HDR working copy looks natural, not grey or too bright; tone-map pick | NORM-02 | Claude cannot see video; brightness match is a judgement | 02-07-T2: four-panel strips in work/strips/ and an HDR working copy beside its original, first 3 seconds and the brightest moment; skin, sky, one strong colour |
| Sideways clip plays upright | NORM-02 | Visual | 02-07-T2 on the Mac and 02-08-T3 step 7 on the phone: upright from the first frame |
| Slow-motion clip plays like the original; sound in step at the end | NORM-02, NORM-04 | Audio/visual | 02-07-T2 on the Mac; 02-08-T3 steps 5 and 6 (clap in the first and last 2 seconds) on the phone |
| Phone run on branch `stage-14-normalize`, doctor rerun, a reel made | all | Sandbox is the truth (CLAUDE.md) | 02-08-T3: HDR clip with claps, sideways clip, slow-motion clip and a photo, each under 15 s; doctor report; manifest table; working copies of A and B back; then a reel |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
