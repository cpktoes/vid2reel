# Vid2Reel

## What This Is

A personal tool that turns the clips on an iPhone into a finished video from inside a Claude chat on the phone: she attaches clips, answers a few quick questions, and gets back a reel ready to post. It makes two shapes, tall 9:16 for short-form reels and wide 16:9 for longer YouTube videos, and both are first-class. It is a Python and FFmpeg toolbox (`v2r`) in this public repo, fetched into the chat's code sandbox by a small skill, with EDITOR.md as the plain-English handbook the chat's Claude follows. No website, no database, no sign-in, no API.

## Core Value

A reel worth posting, made entirely from her phone. Everything else can fail; this cannot.

## Requirements

### Validated

- ✓ `python -m v2r doctor` reports what the computer it runs on has: FFmpeg and ffprobe versions, the H.264 and AAC encoders, six filters, Python, processors, disk, memory, github.com and pypi.org — Phase 1 (Stage 09)
- ✓ `python -m v2r join --shape tall|wide` joins clips in order, upright, cropped to fill from the centre, 30 fps H.264/AAC fast-start MP4, and fits the result under `MAX_RESULT_BYTES` by stepping the frame size down — Phase 1 (Stages 09, 11)
- ✓ The vid2reel skill clones `main` (or a named branch), installs requirements, reads EDITOR.md and follows it; reels have been made from both phones — Phase 1 (Stage 11)
- ✓ The phone route's real limits are measured and recorded in docs/phone-limits.md — Phase 1 (Stage 11)
- ✓ `python -m v2r normalize --shape tall|wide` turns every clip or photo into one working format: upright, sized for the shape, steady 30 fps, HDR tone-mapped to ordinary colour, sound on every clip, photos as 4-second stills, letters A, B, C and work/manifest.json; bad files get one plain sentence and originals are never written to; verified from a phone on FFmpeg 6.1 with a tall and a wide reel — Phase 2 (Stage 14)

### Active

- [ ] Contact sheets and measurements good enough that a Claude which never saw the clip can say what happens and pick the best two seconds (Stage 15)
- [ ] A cut list, checked against a schema, renders to exactly that video in either shape, with a mild touch-up, gentle movement and a proof sheet (Stage 16)
- [ ] EDITOR.md is the complete handbook; one taste profile per social account lives in that account's Claude Project (Stage 17)
- [ ] A small public-domain music library, chosen with her, mixed under the reel at a steady loudness (Stage 18)
- [ ] A brief of three to five questions, a quiet wait, a short reply, and follow-ups that change only what was asked (Stage 19)
- [ ] Two weeks of her real reels, logged; at least half posted without another editor (Stage 20)
- [ ] Profiles that learn from what she changes; filters only when asked; words on screen inside the safe areas (Stage 21)
- [ ] Cuts land on the beat, checked by ear (Stage 22)
- [ ] One plain sentence at every limit; long jobs resume; long videos are edited on the Mac from start to finish (Stage 23)
- [ ] Talking-head videos tightened by the transcript, with captions, from a plan she approved (Stage 24)
- [ ] Her voice from one clip carried over pictures from the others (Stage 25)
- [ ] Every line of the launch checklist true; v1.0 tagged; a monthly check in the calendar (Stage 26)

### Out of Scope

- A website, accounts, payments, other users — Stage 27, a separate idea chat, and only if Stage 20 shows she would rather use this than anything else
- Until Stage 21 or later: transcripts, captions, voice-over, text on screen, beat matching, files too large to attach, saved preferences — the MVP is defined by what is cut
- Google Drive or any cloud storage — the sandbox can't reach it, and the 30 MiB wall is not a storage problem
- Music that is merely free to download, or attribution-licensed — a public repo redistributes every file, so only CC0 fits
- An MCP server on the Mac — it can't follow her phone
- A phase for Stage 27 — not created

## Context

- Phase 1 (the guide's Stages 09 to 13) was done by hand on 2026-10-12: scaffold, doctor, join, GitHub, the skill, the phone tests, CLAUDE.md and docs/decisions.md. It is complete.
- The sandbox (Ubuntu, 2 processors, Python 3.13, FFmpeg 6.1) is the only runtime. Measured on 2026-10-12: uploads arrive at full size, even 408 MB; nothing over 30 MiB comes back; any single command is stopped after 2 minutes, so EDITOR.md runs the join in the background; a full-size join needs about 2.6 s of work per second of video, 4K about 3.8 s, 960×540 about 0.7 s. Details in docs/phone-limits.md.
- The footage bench is in fixtures/ (ignored by git): 14 real clips (two sideways, four over 30 s, one slow-motion, one shaky, two dim, all HDR) and 7 photos. The taste notes in fixtures/ are not yet written; they are first needed in Stage 17.
- docs/field-guide.html is the plan, read one stage at a time. CLAUDE.md and docs/decisions.md are newer and win where they disagree.
- The person who builds this is not a programmer and cannot be shown video by Claude: every change is explained in plain English, with what to look or listen for and when.

## Constraints

- **Runtime**: Python and FFmpeg only, packages from pip, files from github.com, no other network, no GPU, no paid services, no API keys — it must run in the chat sandbox as it is
- **Size**: at most 30 MiB comes back from a chat (`MAX_RESULT_BYTES` is 24 MiB) — measured, not assumed
- **Time**: any single sandbox command is stopped after 2 minutes — long work runs in the background or in pieces
- **Public repo**: never footage, photos or audio from fixtures/ or work/, never a name, account or secret; no attribution lines in commits — her phone fetches this repo, so it must be public
- **Phone first**: a feature for reels that needs a computer, a second app or a setting she must remember is wrong; the one exception is long YouTube videos, edited on a Mac
- **Two shapes**: tall and wide are one setting, never two programs; every command and test covers both
- **Three jobs**: look measures and decides nothing; the cut list is the only place decisions live and is written by the chat's Claude; render builds exactly the list — a better way of seeing footage later replaces only look
- **Taste**: never in EDITOR.md or the repo; a "Reel style" section per account in its Claude Project
- **Process**: one guide stage is one GSD phase on one branch named for the stage; nothing merges into main until a reel has been made from a phone on that branch

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Public repo fetched by a small skill, not a zipped skill or private repo (Stage 10) | A push reaches both phones with nothing to reinstall; no password in a chat | ✓ Good — reels made from both phones |
| A wide clip in a tall reel is cropped to fill, centred on the subject (Stage 16) | Every shot fills the screen; bars and blurred backgrounds read as mistakes | — Pending |
| The chat asks a brief of three to five questions before editing (Stage 19) | A good reel outranks a short conversation | — Pending |
| Long videos are edited on a Mac from start to finish (Stage 23) | A phone chat cannot hand back a file that size; one place, no notes to carry across | — Pending |
| Python 3.13 minimum, matching the sandbox | The sandbox is the only runtime | ✓ Good |
| The join runs in the background and reads a log until it finishes | The sandbox's 2-minute command limit | ✓ Good — test 7 finished in 142 s |
| GSD phases named by guide stage, one per stage, never merged, split or reordered | The guide's stage is what both of us refer to; GSD's own numbers mean nothing | — Pending |
| HDR is tone-mapped on the processor with zscale and tonemap, hable at a peak of 203 nits, picked by eye from four-panel strips (Stage 14) | libplacebo needs a graphics driver the sandbox lacks; research measured hable at 203 closest to Apple's rendering | ✓ Good — natural colour confirmed from the phone |
| Photos, HEIC included, are read with Pillow and pillow-heif, lazily imported (Stage 14) | The sandbox's FFmpeg cannot open HEIC; video keeps working if pip fails | ✓ Good — a HEIC became a still from the phone |
| The handbook joins the working copies in letter order, not the originals (Stage 14) | Only the working copies share one format and all have sound; the join failed on a photo otherwise | ✓ Good — reels made in both shapes |
| A slow-motion clip attached from the phone arrives pre-rendered at a steady 30 fps (Stage 14) | Measured on the phone; the 120/240 fps flag stays correct but does not fire from a phone | ✓ Noted |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-10-14 after Phase 2 (Stage 14 – Normalize) completed*
