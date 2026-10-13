---
phase: 02-stage-14-normalize
plan: "03"
subsystem: dependencies
tags: [pillow, pillow-heif, pip, licences, heic]

requires:
  - phase: 02-stage-14-normalize
    provides: plan 05 (ordering only)
provides:
  - "pillow 12.3.0 and pillow-heif 1.8.1 installed for development and pinned in requirements.txt for the sandbox"
  - "proof that Linux wheels for Python 3.13 exist for both pins, so the sandbox needs no compiler"
  - "docs/licenses.md listing every library beyond Python and FFmpeg with its licence"
affects: [02-06]

actuals:
  tokens: 2500
  tasks: 2
  commits: 1

tech-stack:
  added: [pillow 12.3.0, pillow-heif 1.8.1]
  patterns:
    - "requirements.txt is regenerated with the README uv export command, never hand-edited"

key-files:
  created: [docs/licenses.md]
  modified: [pyproject.toml, uv.lock, requirements.txt]

key-decisions:
  - "pillow-heif is held on the 1.8 line (below 1.9, which will need Pillow 13)"

requirements-completed: [NORM-03]

duration: 5min
completed: 2026-10-13
status: complete
---

# Phase 2 Plan 03: Photo libraries Summary

Pillow 12.3.0 and pillow-heif 1.8.1 added so photos (HEIC) can be read in plan 06, pinned for the phone's sandbox, with their licences written down.

## In plain English

Her photos are HEIC, which the sandbox's FFmpeg cannot open. These two free libraries can. Nothing was installed until you had checked their PyPI pages and answered.

## The package check (Task 1)

You replied "approved" on 2026-10-13 after checking both PyPI pages. GSD's audit had flagged both packages only for unknown download counts (both) and for being too new (pillow-heif 1.8.1, released 2026-10-11). This was a human check, never auto-approved, and nothing was installed before your reply.

## What was done (Task 2)

- Ran `uv add pillow "pillow-heif>=1.8,<1.9"`. Installed Pillow 12.3.0 and pillow-heif 1.8.1.
- Regenerated requirements.txt with the README command. It now pins `pillow==12.3.0` and `pillow-heif==1.8.1`; the uv-generated header is intact.
- Proved the sandbox's pip can install both without a compiler, using `pip download --only-binary=:all: --no-deps --python-version 3.13 --implementation cp` for each platform. Both runs exited 0. Wheels found:
  - manylinux x86_64: `pillow-12.3.0-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl`, `pillow_heif-1.8.1-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl`
  - manylinux aarch64: `pillow-12.3.0-cp313-cp313-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl`, `pillow_heif-1.8.1-cp313-cp313-manylinux_2_26_aarch64.manylinux_2_28_aarch64.whl`
  - The download folders were temporary and deleted.
- Wrote docs/licenses.md: Pillow (MIT-CMU), pillow-heif (BSD-3-Clause), pytest (MIT, Mac only), plus the note that pillow-heif's downloads bundle libheif and libde265 (LGPL-3.0) and x265 (GPL-2.0), none of which this repo contains or redistributes.
- `import PIL, pillow_heif` prints 12.3.0 and 1.8.1. `uv run pytest -q`: 107 passed.

Commit: a883d16 (chore(02-03)).

## Deviations from Plan

None - plan executed exactly as written.

## Test from a phone

No video processing changed here, so no look-or-listen check. Before this branch merges, the phone run must show that the skill's pip install of requirements.txt succeeds in the sandbox (it should now fetch pillow and pillow-heif from ready-made Linux wheels).

## Known Stubs

None.

## Threat Flags

None.

## Self-Check: PASSED

- docs/licenses.md, requirements.txt, uv.lock and pyproject.toml present; commit a883d16 present on stage-14-normalize.
