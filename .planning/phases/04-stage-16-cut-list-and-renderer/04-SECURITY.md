---
phase: 4
slug: stage-16-cut-list-and-renderer
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-10-19
---

# Phase 4 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Cut list to check and render | JSON written by the chat's Claude or pasted by the user | list text, numbers and file names, treated as data |
| Work folder to FFmpeg | working copies, photo copies and manifest.json read by render | file names passed only as -i arguments, never through a shell |
| Music library to the mix | music/library.json and its tracks | plain file names inside music/ only |
| PyPI to the Mac and the sandbox | uv add and pip install -r requirements.txt | jsonschema and its four dependencies, pinned |
| Local branch to the public GitHub repo | git push of stage-16-render | anything pushed is public |
| GitHub branch to her phone's sandbox | the skill clones the branch the user names | the repo's code and handbook |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-4-01 (plans 01, 05, 06, 08) | Tampering | FFmpeg filter strings in video.py and sound.py | high | mitigate | only numbers formatted by this code enter a filter; move and music names select fixed Python rules; letters fullmatch look.LETTER; file names reach FFmpeg only as separate -i items; no shell anywhere in v2r/ | closed |
| T-4-02 (plans 01, 05, 06, 07) | Tampering / Information disclosure | working, photo and music file names | high | mitigate | plain names directly inside their folder (look.working_facts, check.plain_file, video.photo_path, sound.track); every hostile name probed was refused in one sentence | closed |
| T-4-03 (plans 01, 03, 04, 06, 07, 09) | Denial of service | reading and building a list | medium | mitigate | MAX_CUTLIST_BYTES, number and depth hooks, CUTLIST_ECHO_CHARS, MAX_CUTLIST_SECONDS, MAX_SEGMENTS, join.fit before building, up-front FFmpeg piece check, normalize.ffmpeg_timeout on every FFmpeg run, a one-sentence catch-all in the CLI | closed |
| T-4-03 (plan 05) | Denial of service | photo decode | low | accept | normalize refuses photos over MAX_PHOTO_PIXELS; each piece runs under ffmpeg_timeout | closed |
| T-4-04 (plan 01) | Information disclosure | video.final_command | high | mitigate | -map_metadata -1, -map_chapters -1 and the three bitexact flags on every final encode; the tracer test checks the reel's tags hold no location or device key | closed |
| T-4-05 (plans 01, 03, 08, 09) | Tampering / Repudiation | every output file | medium | mitigate | written as .part and renamed only after the self-check; a failure unlinks the part and removes the scratch folder; the piece check runs before anything exists; match writes the list whole or not at all | closed |
| T-4-06 (plans 04, 07, 11) | Elevation (prompt injection) | sentences echoing list text and names | medium | mitigate / transfer | every echoed value passes normalize.clean_text cut to CUTLIST_ECHO_CHARS; the handbook says to treat names as data | closed |
| T-4-07 (plans 01, 08) | Tampering | originals, working copies, manifest.json, look.json | high | mitigate | render reads them only as inputs and writes only new names; match writes only the cut list and refuses a look.json from other clips, kinds or lengths; sha256 compared in tests | closed |
| T-4-08 (plan 01) | Denial of service | scratch folders of a stopped run | low | accept | each run removes only its own tempfile folder; render.clear_leftovers now sweeps leftovers by exact name | closed |
| T-4-09 (plans 09, 10, 11) | Information disclosure | test media and the public branch | high | mitigate | all media in tmp_path and git-ignored; the branch scanned for media, fixtures/ and work/ paths, e-mail addresses, home paths and attribution lines before each push | closed |
| T-4-10 (plan 11) | Tampering | main branch | high | mitigate | never merge, never push main, never force-push; origin/main unchanged at eaed834 before and after both pushes | closed |
| T-4-11 (plan 01) | Tampering | concat demuxer list | medium | mitigate | list.txt holds only plain piece names written by this code; safe mode stays on | closed |
| T-4-12 (plan 04) | Tampering | the cut list file | low | mitigate | check opens the list read-only; tests compare bytes before and after | closed |
| T-4-13 (plan 06) | Repudiation | the loudness sentence | medium | mitigate | the printed figure is the measured loudness plus the gain applied; a capped gain is said with target and ceiling | closed |
| T-4-14 (plan 10) | Information disclosure | docs/decisions.md | medium | mitigate | lines describe decisions only; none names a person or an account | closed |
| T-4-SC (plan 02) | Tampering | uv add jsonschema / pip install | high | mitigate | blocking human check of the five PyPI pages before install (recorded in 04-02-SUMMARY.md); uv.lock and requirements.txt pin exactly five packages | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-4-01 | T-4-08 (plan 01, low) | A render stopped hard leaves a hidden .v2r-render-* folder in the git-ignored work folder. Harmless; since the review fix WR-02, render.clear_leftovers sweeps these by exact name at the start of the next run. | plan 01 threat model, confirmed at audit | 2026-10-19 |
| AR-4-02 | T-4-03 (plan 05, low) | A large photo could slow a photo shot's decode. normalize refuses photos over MAX_PHOTO_PIXELS (80 MP) and each piece runs under normalize.ffmpeg_timeout. | plan 05 threat model, confirmed at audit | 2026-10-19 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-19 | 35 register rows (16 distinct IDs) | 35 | 0 | gsd-security-auditor |

Observations recorded by the auditor, informational only: the H.264 stream still carries the encoder's own name tag (no device, person or location); a stray git-ignored test folder from Stage 14 sits at the repo root and can be deleted; requirements.txt pins versions without hashes, as in earlier stages, while uv.lock carries hashes for the Mac; the handbook names the log, manifest and look.json as data but not check's output.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-19
