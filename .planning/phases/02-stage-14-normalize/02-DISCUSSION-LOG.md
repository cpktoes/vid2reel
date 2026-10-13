# Phase 2: Stage 14 – Normalize - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-13
**Phase:** 2-Stage 14 – Normalize
**Areas discussed:** Photos and HEIC, The HDR look, Past the 2-minute wall, Refusals and letters

Before the questions, Claude gave a plain-English plan, named HDR tone-mapping as the trickiest part (with the 2-minute command limit second), sent a four-panel still of one HDR fixture frame (no tone map, hable, mobius, reinhard), and reported what the fixture bench showed: HEVC 10-bit HLG clips with a Dolby Vision layer and rotation flags, uneven frame timing, extra sound and data tracks, HEIC photos the sandbox's FFmpeg 6.1 cannot open, and a slow-motion clip that arrived already slowed to 30 fps. The user chose all four areas.

---

## Photos and HEIC

| Option | Description | Selected |
|--------|-------------|----------|
| Add Pillow and pillow-heif | Two Python libraries, MIT and BSD licences, in requirements.txt and docs/licenses.md; open HEIC, JPEG, PNG; apply orientation; read the date taken | ✓ |
| JPEG and PNG only, refuse HEIC | No new libraries; HEIC gets a sentence; she would have to change a phone setting | |

**User's choice:** Add Pillow and pillow-heif

| Option | Description | Selected |
|--------|-------------|----------|
| 4 seconds | Room for a slow push-in in Stage 16 | ✓ |
| 3 seconds | Shorter; a push-in would move faster | |
| 6 seconds | Longer than most reels hold a photo; harmless since the cut list trims | |

**User's choice:** 4 seconds
**Notes:** Claude's stated calls, accepted with "Next area": the full-size photo is saved upright as a JPEG in work/ because the sandbox cannot reopen the HEIC later; the still clip is sized by the same rule as a clip.

---

## The HDR look

| Option | Description | Selected |
|--------|-------------|----------|
| Compare on three clips in Do-this, start with mobius | Build with mobius; a one-line command makes the four-panel strip for any fixture clip; the user looks at three and changes the name in settings.py if another looks more like her phone | ✓ |
| Pick mobius now | Keeps colour best in the one frame | |
| Pick hable now | The common filmic choice; a touch darker | |
| Pick reinhard now | The middle option | |

**User's choice:** Compare on three clips in Do-this, start with mobius

| Option | Description | Selected |
|--------|-------------|----------|
| Make a plain copy and say so | Convert without tone-mapping; one sentence in the manifest and log; the reel can still be made | ✓ |
| Skip the clip with a sentence | Treat like an unreadable file; a clip is lost | |

**User's choice:** Make a plain copy and say so
**Notes:** Claude's stated calls, accepted: the Dolby Vision layer is ignored and the manifest says so; the chain is told the clip's colour facts from ffprobe rather than trusting the file's tags alone. The user was told plainly that zscale and tonemap are second-best to libplacebo, which the sandbox lacks.

---

## Past the 2-minute wall

| Option | Description | Selected |
|--------|-------------|----------|
| One run for all files, manifest grows clip by clip | Background with a log like the join; a line per clip; manifest rewritten after each | ✓ |
| One command per clip | Shorter commands, but a single long 4K clip still passes the limit | |

**User's choice:** One run for all files, manifest grows clip by clip

| Option | Description | Selected |
|--------|-------------|----------|
| The handbook's nohup line, as for join | Same pattern she already has; one pattern for every long command | ✓ |
| A built-in --background option | Shorter EDITOR.md lines, but a new mechanism to prove from a phone | |

**User's choice:** The handbook's nohup line, as for join
**Notes:** Claude's stated calls, accepted: working copies encoded fast at high quality since the renderer re-encodes them; a new run replaces work/manifest.json and the lettered copies; one progress line per clip. Claude drafts the EDITOR.md lines; the user edits EDITOR.md themselves.

---

## Refusals and letters

| Option | Description | Selected |
|--------|-------------|----------|
| It stays C; B is kept as a skipped entry | Letters follow attach order; the manifest keeps the skipped entry with its sentence | ✓ |
| It becomes B; skipped files get no letter | Only converted clips are lettered | |

**User's choice:** It stays C; B is kept as a skipped entry

| Option | Description | Selected |
|--------|-------------|----------|
| Refuse it with one sentence | What the brief says; the sentence can point to Stage 23's shrink shortcut | ✓ |
| Convert it anyway and warn | It arrived, so use it; the log warns it will take minutes | |

**User's choice:** Refuse it with one sentence

| Option | Description | Selected |
|--------|-------------|----------|
| Convert the first ten, one sentence for the rest | Files eleven and twelve get letters as skipped entries | |
| Refuse the whole batch | Nothing converted; one sentence asks for ten or fewer | |

**User's choice (free text):** "10 is not a hard limit. I say we try, and if failed ask to reduce clip count. Only hard limit should be how many uploads Claude can deal with on an import."
**Notes:** Normalize does not enforce MAX_ATTACHMENTS; it tries every file, and if the run fails its sentence asks for fewer clips. Claude's stated calls, accepted: every sentence is printed in the log and kept in the manifest entry; an unreadable file's sentence names the file as she sent it.

---

## Claude's Discretion

- Manifest field names and layout; the exact FFmpeg command and filter chain; keeping only the first video and first audio track; encoder preset and CRF; JPEG quality of the full-size photo copy; how doctor's lists grow; the wording of every sentence and progress line; the comparison-strip command; the draft EDITOR.md lines.

## Deferred Ideas

- Time estimate before a run (Stage 23); resumable runs (Stage 23); the Shrink for Claude shortcut (Stage 23); a built-in --background option (Stage 23, only if needed); Dolby Vision-aware conversion with libplacebo (not planned).
