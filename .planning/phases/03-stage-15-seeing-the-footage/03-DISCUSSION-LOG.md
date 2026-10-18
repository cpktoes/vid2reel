# Phase 3: Stage 15 – Seeing the footage - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-17
**Phase:** 3-Stage 15 – Seeing the footage
**Areas discussed:** Sheets and stills, Extra stills, Candidate moments, Shot changes and libraries

Before the questions, Claude gave a plain-English plan (FFmpeg's own filters for every measurement, the deshake filter's camera shift to separate camera from subject, Pillow for the sheets, no new library, PySceneDetect checked and set aside), named telling camera shake from subject movement as the trickiest part (sheet readability against the cap second), showed timings measured on the Mac at two threads for a 39-second working copy, and made a trial 4-by-3 sheet from one of the user's Stage 14 working copies. The user answered "go".

---

## Sheets and stills

| Option | Description | Selected |
|--------|-------------|----------|
| 12 per sheet | Tall stills 4 across by 3 down, wide 3 by 4; the trial sheet read clearly; about 4 sheets for a 30-second clip | ✓ |
| 16 per sheet | 4 by 4; about 3 sheets; each still a little smaller after Claude's viewer shrinks the sheet | |
| 20 per sheet | 5 by 4; the guide's two or three sheets per clip; each still about a quarter smaller | |

**User's choice:** 12 per sheet

| Option | Description | Selected |
|--------|-------------|----------|
| One still | Labelled with its letter and 00.0; four identical stills would waste sheet space | ✓ |
| Treated like any clip | Four identical stills at one a second; no special case | |

**User's choice:** One still

| Option | Description | Selected |
|--------|-------------|----------|
| Short clips share a sheet | Stills in letter order fill sheets continuously; labels keep clips apart; ten 5-second clips cost 5 sheets | ✓ |
| One clip per sheet, always | Every clip starts a new sheet; ten short clips cost ten sheets | |

**User's choice:** Short clips share a sheet

| Option | Description | Selected |
|--------|-------------|----------|
| 12 sheets, then thin evenly | About three 30-second clips at full rhythm; over the cap the base rhythm stretches while extras are kept, and look.json says so | |
| 20 sheets, then thin evenly | Room for about five 30-second clips before thinning; more of her allowance per reel | ✓ |
| 12 sheets, then stop and say so | No thinning; the first 12 sheets only and one sentence naming the clips that got none | |

**User's choice:** 20 sheets, then thin evenly

---

## Extra stills

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, sound peaks too | A laugh or a splash shows in the loudness curve even when the picture barely changes; capped like the other extras | ✓ |
| No, movement and shot changes only | Exactly what the guide says; sound could be added after the blind test | |

**User's choice:** Yes, sound peaks too

| Option | Description | Selected |
|--------|-------------|----------|
| 0.3 seconds | A splash a third of a second after a base still gets its own still | ✓ |
| 0.5 seconds | Fewer extras and fewer near-duplicates; a quick moment close to a base still is skipped | |
| No minimum | An extra lands exactly on the peak even right next to a base still | |

**User's choice:** 0.3 seconds

| Option | Description | Selected |
|--------|-------------|----------|
| A third more than its base stills | A 30-second clip adds at most 10 extras, about 40 stills, as the guide estimated; strongest peaks first | ✓ |
| As many as its base stills | A 30-second clip could reach 60 stills | |
| A fixed 8 per clip | Predictable sheet counts; a long busy clip loses peaks | |

**User's choice:** A third more than its base stills

| Option | Description | Selected |
|--------|-------------|----------|
| Subject movement, camera motion removed | A splash counts; a pan or walking shot does not flood the sheet; relies on the deshake split | ✓ |
| All movement, camera included | Simpler and never wrong about what moved; a walking shot earns extras everywhere | |

**User's choice:** Subject movement, camera motion removed

---

## Candidate moments

| Option | Description | Selected |
|--------|-------------|----------|
| 2 seconds, stepped by half a second | The guide's "best two seconds"; overlapping windows that score alike merge | ✓ |
| As long as it stays good, 1 to 5 seconds | Fewer, longer candidates; Claude trims them | |
| 1.5 seconds | More distinct moments in a busy clip; tighter than a typical shot | |

**User's choice:** 2 seconds, stepped by half a second

| Option | Description | Selected |
|--------|-------------|----------|
| 5 per clip | Enough choice for a 20-second reel without flooding look.json | ✓ |
| 3 per clip | Tighter; a long varied clip may leave good stretches unlisted | |
| 10 per clip | More to choose from; longer look.json | |

**User's choice:** 5 per clip

| Option | Description | Selected |
|--------|-------------|----------|
| Steady and sharp first, movement as the tiebreak | A calm sharp stretch outranks a busy shaky one; shaky or blurred never listed | ✓ |
| Movement first | Liveliest stretches top as long as not shaky or blurred | |
| Equal weight | A plain sum of the three | |

**User's choice:** Steady and sharp first, movement as the tiebreak

| Option | Description | Selected |
|--------|-------------|----------|
| The facts and the stills inside the stretch | "steady camera, sharp, subject moving, sound peak at 04.5; stills A 04.0, A 04.5, A 05.0"; receipts ready-made | ✓ |
| The facts only | Shorter; Claude finds the stills from the times | |

**User's choice:** The facts and the stills inside the stretch

---

## Shot changes and libraries

| Option | Description | Selected |
|--------|-------------|----------|
| FFmpeg's built-in scene filter | Already in the sandbox; same method as PySceneDetect's default detector; licenses.md records the check | ✓ |
| PySceneDetect | BSD-3; needs OpenCV (80 MB) or PyAV (43 MB) installed by pip in every chat | |

**User's choice:** FFmpeg's built-in scene filter

| Option | Description | Selected |
|--------|-------------|----------|
| Doctor grows, and a phone run comes first | Doctor lists the five analysis filters; running it from a phone is the first task on the branch | ✓ |
| Trust the version numbers | All five predate FFmpeg 6.1; skip the early phone run | |

**User's choice:** Doctor grows, and a phone run comes first

| Option | Description | Selected |
|--------|-------------|----------|
| Carry on with that measurement marked unknown | Sheets and the other measurements still come back; one plain sentence | ✓ |
| Refuse to run with one sentence | Nothing comes back until the filter is sorted out | |

**User's choice:** Carry on with that measurement marked unknown

| Option | Description | Selected |
|--------|-------------|----------|
| Pillow, with its built-in font | Already a dependency; full control of grid, label box and file names; no font file | ✓ |
| FFmpeg's tile and drawtext filters | No drawing code, but the font path differs between Mac and sandbox | |

**User's choice:** Pillow, with its built-in font

---

## Claude's Discretion

The look.json layout and names; sheet file names and JPEG quality; the label box style; the analysis frame size, rate and filter options; how half-second summaries and peaks are computed; the exposure and colour summary; whether one decode is shared between measuring and stills; what a photo gets as a candidate; how doctor's lists grow; the test-clip generators; the proposed EDITOR.md step and the docs/decisions.md lines.

## Deferred Ideas

Sparser looking and resumable runs for long clips (Stage 23); a `--background` option if nohup proves fragile (Stage 23); a PySceneDetect switch only if the built-in filter misses real cuts; face or object recognition never in code.
