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
| 02-W0-media | TBD | 0 | NORM-08 | — | generated clips only; nothing from fixtures/ | fixture | `uv run pytest tests/test_normalize.py -k doctor -x` | ❌ W0 | ⬜ pending |
| 02-facts | TBD | TBD | NORM-01 | T-2-01 / — | ffprobe reads facts without writing the input | unit/integration | `uv run pytest tests/test_normalize.py -k facts -x` | ❌ W0 | ⬜ pending |
| 02-working | TBD | TBD | NORM-02 | — | H.264 yuv420p, 30/1, working_size, no rotation side data, bt709, AAC 2ch 48 kHz; HDR converted not relabelled; both shapes | integration + unit | `uv run pytest tests/test_normalize.py -k "working or upright or hdr" -x` | ❌ W0 | ⬜ pending |
| 02-photo | TBD | TBD | NORM-03 | — | upright full-size JPEG in work/, still clip PHOTO_SECONDS x 30 frames with sound | integration | `uv run pytest tests/test_normalize.py -k photo -x` | ❌ W0 | ⬜ pending |
| 02-slowmo | TBD | TBD | NORM-04 | — | 120 fps flagged slow_motion, real-time length at 30 fps; 60 fps not flagged | integration | `uv run pytest tests/test_normalize.py -k slow -x` | ❌ W0 | ⬜ pending |
| 02-manifest | TBD | TBD | NORM-05 | — | letters A, B, C in given order incl. a skipped file; convert_seconds numeric; no location or device metadata | integration | `uv run pytest tests/test_normalize.py -k manifest -x` | ❌ W0 | ⬜ pending |
| 02-refuse | TBD | TBD | NORM-06 | T-2-02 / — | oversized and unreadable files get one sentence each; others still convert; tone-map fallback yields a done clip with a note | integration | `uv run pytest tests/test_normalize.py -k "refuse or unreadable or fallback" -x` | ❌ W0 | ⬜ pending |
| 02-original | TBD | TBD | NORM-07 | T-2-03 / — | SHA-256 and st_mtime_ns of every input unchanged; input inside work/ skipped not deleted | integration | `uv run pytest tests/test_normalize.py -k original -x` | ❌ W0 | ⬜ pending |
| 02-doctor | TBD | TBD | NORM-08 | — | every filter in the built graphs is in doctor.FILTERS; decoders listed | unit | `uv run pytest tests/test_normalize.py -k doctor -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Task IDs and plan/wave columns are filled in by the planner once PLAN.md files exist.*

---

## Wave 0 Requirements

- [ ] `tests/media.py` — shared generators (clip variants: sideways via `-display_rotation`, 60 fps, 120 fps, no sound, HDR-tagged; corner-marker clip; VFR clip; JPEG with EXIF orientation 6 and HEIC maker; garbage and empty files)
- [ ] `tests/test_normalize.py` — stubs for NORM-01 to NORM-08, parametrised over `shape in ["tall", "wide"]`
- [ ] `uv add pillow pillow-heif` — only after the human-verify checkpoint on the two packages; HEIC test needs `pillow_heif.register_heif_opener()`; regenerate requirements.txt afterwards

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| HDR working copy looks natural, not grey or too bright | NORM-02 | Claude cannot see video; brightness match is a judgement | Open the HDR clip's working copy next to the original; compare skin and sky at 0:00–0:03; it should match the phone's playback, not look washed out |
| Sideways clip plays upright | NORM-02 | Visual | Play the working copy of a clip shot sideways; the picture should be upright from the first frame |
| Silent and slow-motion clips play at normal speed with sound track present | NORM-02, NORM-04 | Audio/visual | Play both working copies; the player shows an audio track; motion is real-time, not slowed |
| Phone run on branch `stage-14-normalize` | all | Sandbox is the truth (CLAUDE.md) | From a phone chat, attach a sideways, a 60 fps, an HDR, a silent clip and a photo; run normalize; rerun doctor; confirm manifest and working copies come back |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
