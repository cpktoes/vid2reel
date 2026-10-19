# Phase 4: Stage 16 – Cut list and renderer - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-19
**Phase:** 04-stage-16-cut-list-and-renderer
**Areas discussed:** Three changes to the draft, Sound, Movement, The match step, Outputs

The session opened with the guide's Stage 05 cut-list design prompt: the design, a 20-second tall example and a wide example were shown in plain English with what would be hardest to change later, and the user said "proceed and let's answer the questions". The draft's D-01 to D-12 stayed locked; the questions below settled the rest.

---

## Three changes to the draft

| Option | Description | Selected |
|--------|-------------|----------|
| Clips block, required | Every list names each letter's file and length; the checker refuses a mismatch | ✓ |
| Clips block, optional | Confirmed when present, trusted when absent | |
| No clips block | Letters trusted; a pasted list relies on attach order | |

| Option | Description | Selected |
|--------|-------------|----------|
| Cover by segment and second | Follows the shot when the reel changes | ✓ |
| Cover as a time on the finished reel | As drafted; drifts when an earlier shot changes length | |

| Option | Description | Selected |
|--------|-------------|----------|
| Build the music drop now, per segment | Music drops by `music_under_sound` for every kept segment; Stage 18 refines | ✓ |
| Accept the field, build in Stage 18 | Music at one level throughout until then | |

**User's choice:** all three recommended options.

---

## Sound

| Option | Description | Selected |
|--------|-------------|----------|
| -14 LUFS, -1 dBTP | The figure every source agrees YouTube uses; the common short-form target | ✓ |
| -16 LUFS, -1 dBTP | Quieter and safer, may sound soft in her feed | |

| Option | Description | Selected |
|--------|-------------|----------|
| Checker refuses when the music runs out | One sentence, nothing built | ✓ |
| Music ends early, noted | A silent tail | |
| Loop the track | Audible loop point | |

| Option | Description | Selected |
|--------|-------------|----------|
| Fades optional, defaults in settings.py | A stated value wins | ✓ |
| Fades required in every list | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Silent reel allowed, with a note | She may add music in the app | ✓ |
| Silent reel refused | | |

**Notes:** a web search found no official platform page; the sources disagree on Instagram and TikTok and agree on YouTube's -14.

---

## Movement

| Option | Description | Selected |
|--------|-------------|----------|
| 4 percent | About 43 pixels of a tall frame over 3 seconds | ✓ |
| 3 percent | May read as nothing on a photo | |
| 6 percent | Risks reading as an effect | |

| Option | Description | Selected |
|--------|-------------|----------|
| Handbook rule plus a checker note | EDITOR.md says push-in on every photo unless still; the checker notes a still photo | ✓ |
| Handbook rule only | | |
| Checker refuses a still photo | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Crop in by the cap, then travel | A pan means the same on every shot | ✓ |
| Spare width only, else refuse | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Steady, same speed throughout | CUT-04's wording; provable across FFmpeg versions | ✓ |
| Eased | | |

---

## The match step

| Option | Description | Selected |
|--------|-------------|----------|
| Median | One odd clip does not pull the rest | ✓ |
| Mean | | |
| The first clip | | |

| Option | Description | Selected |
|--------|-------------|----------|
| ±8 brightness, ±4 colour, 0.92 to 1.08 saturation | A third of a stop, a faint tint, a hair of colour | ✓ |
| Half of those | | |
| Double those | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Towards the group's middle | A golden hour stays golden | ✓ |
| Towards neutral grey | A look, undoes a warm evening | |

| Option | Description | Selected |
|--------|-------------|----------|
| Rerun rewrites every record | "Halve the cap and run again" works | ✓ |
| Rerun fills only missing records | | |

---

## Outputs

| Option | Description | Selected |
|--------|-------------|----------|
| Cover default: first frame of the reel | A stated rule, the platforms' own default | ✓ |
| Middle of the first segment | | |
| Required, no default | | |

| Option | Description | Selected |
|--------|-------------|----------|
| First and last frame of every segment | Where a black frame or a bad crop shows; look's sheet code | ✓ |
| One still a second, like look | | |
| One sheet of twelve, evenly spaced | | |

| Option | Description | Selected |
|--------|-------------|----------|
| No touch-up block: built untouched, checker notes it | The house rule stays the handbook's | ✓ |
| Checker refuses: run match first | | |

---

## Claude's Discretion

The FFmpeg filter chains; the half-open interval rule; the test tone; the music-drop ramp length; the crop-share note threshold; the schema's structure and sentence mapping; file names in work/; the proof-sheet label format; the fit step's reuse of FIT_STEPS; the names of the new settings; the order of the checker's sentences and match's printed lines; photos in the match group.

## Deferred Ideas

Ducking that follows the sound and the music library (Stage 18); filters and text (Stage 21); beat alignment (Stage 22); resumable renders and the Mac's no-limit mode (Stage 23); speech cuts, captions and voice (Stages 24, 25); excluded candidate stretches as facts; a run-in-progress guard for normalize.
