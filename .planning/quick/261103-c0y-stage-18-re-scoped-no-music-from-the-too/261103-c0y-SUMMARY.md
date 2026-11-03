---
phase: quick-261103-c0y
plan: 01
subsystem: docs
tags: [stage-18, handbook, sound, records]
status: complete
completed: 2026-11-03
key-files:
  modified:
    - EDITOR.md
    - CLAUDE.md
    - docs/decisions.md
    - README.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
    - .planning/PROJECT.md
    - .planning/STATE.md
decisions:
  - "Stage 18 (2026-11-03): the tool adds no music; a reel keeps the clips' own sound or, when asked, every shot is muted; music is added in the posting app"
actuals:
  tokens: 6000
  tasks: 3
  commits: 1
---

# Quick Task 261103-c0y: Stage 18 re-scoped, no music from the tool

One commit of seven text files makes the handbook, the project rules and the planning files all say the same thing: the tool adds no music, a reel keeps the clips' own sound or goes mute, and a song is added in the posting app.

## What changed, in plain English

- **EDITOR.md (what the phone's Claude follows).** The Sound paragraph no longer says a music library is coming. It now says: keep every shot's own sound unless asked; "mute" or "no sound" turns every shot off; the tool adds no music, so if she asks for a song the reply says music (and how loud it sits against the clips' sound) is added in the posting app, and the reel is made anyway. This is the only line of the handbook that changed.
- **CLAUDE.md.** The public-repo rule now says no music files go in the repo and `music/` stays empty. The "Settled so far" list records the Stage 18 decision of 2026-11-03, just before the Stage 19 entry, and the "until the music library exists" wording is gone.
- **docs/decisions.md.** One new dated line (2026-11-03, Stage 18) saying what was decided, what was shelved, what stays, and how it differs from the guide (the guide's Stage 18 builds a library and its Stage 22 depends on one).
- **README.md.** The `music/` row now says it is empty because the tool adds no music.
- **ROADMAP.md, REQUIREMENTS.md, PROJECT.md.** Phase 6 is re-scoped (new goal, three success criteria, plans line). Phase 10 (cut to the beat) carries a dated note that it depended on a track chosen inside the tool. MUS-01 to MUS-06 read "Dropped" and stay unticked. PROJECT.md's active line is replaced.
- **STATE.md.** Updated to show Stage 18 re-scoped and waiting for the phone test and the merge. Left uncommitted for the orchestrator.

The earlier music work stays shelved on its own unmerged local branch; nothing here touched it. No code, schema, tests, music files, footage or the guide changed. Nothing was pushed or merged.

## Results

- Content commit: `022131a`, message exactly `docs(18): no music from the tool; keep the sound or go mute`, no attribution line, holding exactly the seven files.
- Handbook test (`uv run pytest -q tests/test_editor_handbook.py`): 16 passed, before the commit and again after the planning files were edited.
- EDITOR.md word count: 1,309 (cap 1,500). It differs from before in exactly one line.
- Library-wording grep (`library arrives`, `library is coming`, `library exists` over EDITOR.md, CLAUDE.md, README.md): printed nothing.
- Tests that read README.md, CLAUDE.md or decisions.md: none (the search printed nothing), so nothing extra to run.
- Staged diff scanned for personal names, account names, email addresses and absolute paths: none found.
- `git diff --stat main..HEAD`:

```
 .planning/PROJECT.md      |  2 +-
 .planning/REQUIREMENTS.md |  4 +++-
 .planning/ROADMAP.md      | 16 ++++++++--------
 CLAUDE.md                 |  4 ++--
 EDITOR.md                 |  2 +-
 README.md                 |  2 +-
 docs/decisions.md         |  1 +
 7 files changed, 17 insertions(+), 14 deletions(-)
```

- `git status --short` afterwards: STATE.md modified; `.gsd/` and this quick task's folder untracked; nothing else.

## Deviations from Plan

None - plan executed exactly as written. (I also started the whole test suite once as an extra check; it took longer than two minutes, so I stopped it. Only the handbook test, which the plan asks for, was relied on. Nothing in the code changed, so the full suite is not affected.)

## What you should do next

1. Push the branch only when you say so; I have not pushed it.
2. From the phone, on branch stage-18-music, ask for a reel, for example: "use branch stage-18-music. Make a reel, about 20 seconds." Use clips that have sound.
3. Listen from the first second to the last. You should hear each clip's own sound, with no music and no test tone.
4. Read the reply. It must not promise that a music library is coming.
5. Ask once more, this time with "add a song". The reply should say music is added in the posting app, and a reel should still arrive.
6. Main is not merged until you have done this.

Also worth knowing: the guide still describes the old Stage 18 (a music library) and Stage 22 (cut to the beat) as depending on it. CLAUDE.md and docs/decisions.md win over the guide, so the guide needs revising when you next update it.

## Self-Check: PASSED

- The seven files were changed in commit `022131a` (verified with `git diff --name-only main..HEAD`).
- STATE.md is modified and uncommitted, as required.
