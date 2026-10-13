# Roadmap: Vid2Reel

## Overview

Vid2Reel is a Python and FFmpeg toolbox (`v2r`) that turns the clips on her iPhone into a finished reel from inside a Claude chat on the phone. The skeleton is done and a reel has been made from a phone. Next the toolbox learns to see footage, then to cut it, then to hold a conversation about it; then she uses it for two weeks on her real reels, and what she finds shapes the rest: her look, big files, talking-head videos and finally launch. Each phase is one stage of the field guide, planned later from its own stage, one phase at a time.

## Milestones

- **M1: A reel from a phone** (complete 2026-10-12) - Phase 1 (Skeleton)
- **M2: It can see** - Phases 2 and 3 (Stage 14 – Normalize; Stage 15 – Seeing the footage)
- **M3: It can cut** - Phases 4, 5 and 6 (Stage 16 – Cut list and renderer; Stage 17 – Editor's handbook; Stage 18 – Music)
- **M4: It's a conversation** - Phase 7 (Stage 19 – Conversation)
- **M5: Her two weeks** - Phase 8 (Stage 20 – Her two weeks)
- **M6: Her look** - Phases 9 and 10 (Stage 21 – Her look and words on screen; Stage 22 – Cut to the beat)
- **M7: Big files** - Phase 11 (Stage 23 – Long and large files)
- **M8: Words, then launch** - Phases 12, 13 and 14 (Stage 24 – Talking head; Stage 25 – Voice over pictures; Stage 26 – Launch)

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Skeleton** - Doctor check, join command, the skill and the phone route's measured limits, done by hand (completed 2026-10-12)
- [ ] **Phase 2: Stage 14 – Normalize** - Any clip or photo becomes one working format, with a manifest naming every clip
- [ ] **Phase 3: Stage 15 – Seeing the footage** - Contact sheets and measurements good enough for Claude to pick the best moment unseen
- [ ] **Phase 4: Stage 16 – Cut list and renderer** - A checked cut list renders to exactly that video in either shape
- [ ] **Phase 5: Stage 17 – Editor's handbook** - EDITOR.md becomes the complete handbook, with taste kept in per-account profiles
- [ ] **Phase 6: Stage 18 – Music** - A small public-domain music library, chosen with her, mixed under the reel
- [ ] **Phase 7: Stage 19 – Conversation** - A short brief, a quiet wait, a short reply, and follow-ups that change only what was asked
- [ ] **Phase 8: Stage 20 – Her two weeks** - Two weeks of her real reels, logged, and the call on what comes next
- [ ] **Phase 9: Stage 21 – Her look and words on screen** - Profiles that learn, filters only when asked, words inside the safe areas
- [ ] **Phase 10: Stage 22 – Cut to the beat** - Cuts land on the beat, checked by ear
- [ ] **Phase 11: Stage 23 – Long and large files** - One plain sentence at every limit, resumable jobs, long videos edited on the Mac
- [ ] **Phase 12: Stage 24 – Talking head** - Talking-head videos tightened by the transcript, with captions, from a plan she approved
- [ ] **Phase 13: Stage 25 – Voice over pictures** - Her voice from one clip carried over pictures from the others
- [ ] **Phase 14: Stage 26 – Launch** - Every line of the launch checklist true, v1.0 tagged, a monthly check set

## Phase Details

### Phase 1: Skeleton

**Goal**: The toolbox exists end to end: it can report what the computer has, join clips into a reel, and be fetched into a chat on her phone, with the phone route's limits measured.
**Depends on**: Nothing (first phase)
**Requirements**: SKEL-01, SKEL-02, SKEL-03, SKEL-04
**Success Criteria** (what must be TRUE):

  1. `python -m v2r doctor` reports FFmpeg and ffprobe versions, the encoders and filters it needs, Python, processors, disk, memory, and whether github.com and pypi.org are reachable
  2. User can join clips in order into a tall or wide MP4 that is upright, cropped to fill, 30 fps, fast-start and under the send-back size limit
  3. The vid2reel skill fetches the repo into a chat, reads EDITOR.md and follows it, and reels have been made from both phones
  4. The phone route's limits are measured and written down in docs/phone-limits.md

**Plans**: done by hand (0 plans)

### Phase 2: Stage 14 – Normalize

**Goal**: Any clip or photo she shoots becomes one working format, upright, 30 fps and in ordinary colour, with a manifest naming every clip.
**Depends on**: Phase 1
**Requirements**: NORM-01, NORM-02, NORM-03, NORM-04, NORM-05, NORM-06, NORM-07, NORM-08
**Success Criteria** (what must be TRUE):

  1. User can run `python -m v2r normalize` on sideways, 60 fps, HDR and silent clips and on photos, and get working copies in work/ that are upright, constant 30 fps, naturally coloured and with sound on every one
  2. work/manifest.json names every clip A, B, C in the order given, with its original facts (including slow-motion source flagged), its working copy and how long the conversion took
  3. A file that is too large or can't be read gets one plain-English sentence and the other files still convert
  4. No original file is ever written to
  5. Tests pass using generated clips, including one stored sideways, one at 60 fps, one with no sound and one tagged HDR

**Plans**: 5/8 plans executed

Plans:
**Wave 1**

- [x] 02-01-PLAN.md — Tracer: one clip to an upright 30 fps working copy and manifest in both shapes, then the full fact sheet, sideways, 60 fps, uneven-timing and silent clips (wave 1)
- [x] 02-02-PLAN.md — Doctor lists every FFmpeg piece normalize needs; Stage 14 decisions recorded; normalize.log ignored (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 02-04-PLAN.md — HDR tone-mapped to ordinary colour with a safe fallback; slow-motion sources flagged at real speed (wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 02-05-PLAN.md — One plain sentence per refused or unreadable file, letters kept, originals proven untouched, doctor check at start-up (wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 02-03-PLAN.md — User checks, then installs, Pillow and pillow-heif; requirements.txt and docs/licenses.md (wave 4, alone, checkpoint)

**Wave 5** *(blocked on Wave 4 completion)*

- [ ] 02-06-PLAN.md — Photos (HEIC, JPEG, PNG) become upright full-size copies and 4-second still clips (wave 5)

**Wave 6** *(blocked on Wave 5 completion)*

- [ ] 02-07-PLAN.md — Mac run over the fixtures, HDR strips, the user's tone-map pick (wave 6, checkpoint)

**Wave 7** *(blocked on Wave 6 completion)*

- [ ] 02-08-PLAN.md — The user's EDITOR.md lines, pre-push privacy checks, push with permission, phone test with a reel (wave 7, checkpoints)

### Phase 3: Stage 15 – Seeing the footage

**Goal**: A Claude that never saw a clip can say what happens in it and pick its best two seconds, from contact sheets and measurements alone.
**Depends on**: Phase 2
**Requirements**: LOOK-01, LOOK-02, LOOK-03, LOOK-04, LOOK-05, LOOK-06, LOOK-07
**Success Criteria** (what must be TRUE):

  1. User can run `python -m v2r look` and get contact sheets in work/ with a still every second plus extra stills at movement peaks and shot changes, each labelled with its clip letter and time like "B 07.5"
  2. work/look.json holds, for every half second of every clip, movement, camera shake, sharpness, brightness, loudness and shot changes, plus each clip's overall exposure and colour balance, with the shot-change library's licence recorded in docs/licenses.md
  3. look.json lists ranked candidate moments per clip with start and end times and the reason in words, and the code never chooses what goes in a reel
  4. Tests using generated clips with a known answer prove a still lands on the moment that matters
  5. In the blind test, from the sheets and look.json alone, Claude picks the moment she would have picked in at least four clips out of five

**Plans**: TBD

### Phase 4: Stage 16 – Cut list and renderer

**Goal**: A cut list, checked against a schema, renders to exactly that video in either shape, with a mild touch-up, gentle movement and a proof sheet.
**Depends on**: Phase 3
**Requirements**: CUT-01, CUT-02, CUT-03, CUT-04, CUT-05, CUT-06, CUT-07, CUT-08, CUT-09
**Success Criteria** (what must be TRUE):

  1. User can run `python -m v2r check` on a cut list and get every problem reported as one plain-English sentence, checked against the schema and the manifest
  2. `python -m v2r render` builds exactly the cut list in tall or wide, with straight cuts and every segment filling the canvas around its focus point, with no letterbox or blurred background; an invalid list builds nothing
  3. A segment can have a slow, steady push-in, pull-out or pan, and `python -m v2r match` writes a mild per-clip colour correction that the renderer applies and nothing more
  4. Each segment's own sound can be kept or dropped, music sits underneath, and the finished mix is normalized to a stated loudness
  5. The output is an H.264/AAC fast-start MP4 under the send-back limit with a contact sheet and cover still alongside, and golden renders in both shapes prove the same cut list always makes the same video

**Plans**: TBD

### Phase 5: Stage 17 – Editor's handbook

**Goal**: EDITOR.md is the complete, plain-words handbook the chat's Claude follows, and taste lives in per-account profiles rather than in the repo.
**Depends on**: Phase 4
**Requirements**: HAND-01, HAND-02, HAND-03, HAND-04, HAND-05
**Success Criteria** (what must be TRUE):

  1. EDITOR.md fits on two pages and covers the steps in order, how to study the sheets, rules of craft, the Lively and Calm recipes, the house rules, the honesty rules, what to do with unreadable files or too little footage, and the order of authority
  2. No editing judgement lives in Python and no one person's taste lives in EDITOR.md
  3. A "Reel style" profile is drafted for each social account named in the taste notes, saved in fixtures/ and never in the repo
  4. The rehearsal runs for all five fixture sets, and a second profile on the same set changes only what the two profiles differ in
  5. She would post at least three of the five fixture reels with small changes

**Plans**: TBD

### Phase 6: Stage 18 – Music

**Goal**: A small public-domain music library, chosen with her, is mixed under the reel at a steady loudness.
**Depends on**: Phase 5
**Requirements**: MUS-01, MUS-02, MUS-03, MUS-04, MUS-05, MUS-06
**Success Criteria** (what must be TRUE):

  1. Eight to twelve tracks chosen with her are in music/library.json, each with her mood words, tempo, energy, licence, source page and date checked, and each shown as CC0 or public domain on its own source page
  2. User can add a track with `python -m v2r music add`, which measures tempo and loudness and refuses a track without a licence and a source; tempo is measured on the Mac, never in the sandbox
  3. `python -m v2r music list` prints the library, and EDITOR.md tells Claude how to choose a track, always name it, and offer "no music"
  4. Music dips while a clip's own sound is present and comes back after, with a fast fade in and a fade out over the last 1.5 seconds, and the final mix is still normalized

**Plans**: TBD

### Phase 7: Stage 19 – Conversation

**Goal**: Making a reel is a short conversation: a brief of a few quick questions, a quiet wait, a short reply, and follow-ups that change only what was asked.
**Depends on**: Phase 6
**Requirements**: CONV-01, CONV-02, CONV-03, CONV-04, CONV-05, CONV-06, CONV-07
**Success Criteria** (what must be TRUE):

  1. User is asked three to five numbered questions in one message, each answerable in a few words and each with a default, with already-answered questions left out, and the brief skipped when she says to just make it
  2. Work starts with one line and a time estimate, then silence until the reel; the reply is the video, at most two lines on what is in it and which track, and three suggested follow-ups, with clips described by what is in them
  3. `python -m v2r revise` applies one named change (shorten or lengthen, reorder, drop a clip, change the music or sound, change the canvas) and leaves every other field untouched, proved by tests
  4. Errors are plain English ending with a next step, and if the work folder is gone Claude asks for the clips again
  5. From a phone on the branch, she can attach clips, answer the brief, get a reel, then say "shorter", "different song" and "a wide version", each changing only what was asked

**Plans**: TBD

### Phase 8: Stage 20 – Her two weeks

**Goal**: She uses the tool for her real reels for two weeks, and what she finds decides what comes next.
**Depends on**: Phase 7
**Requirements**: WEEK-01, WEEK-02, WEEK-03, WEEK-04
**Success Criteria** (what must be TRUE):

  1. She has the two-line instructions and has made one reel with the builder watching
  2. fixtures/reel-log.md has one entry per reel: posted as it came, posted after an outside fix (what), or not posted (why, in her words), plus follow-ups, brief answers, time from send to saved, and whether her plan ran out
  3. After two weeks or ten reels, the five most common complaints are listed with their likely cause and fixed one at a time, each tested from a phone before merging
  4. The call is made and recorded: at least half posted without another editor means on to Stage 21, otherwise back to Stage 15 or 17

**Plans**: TBD

### Phase 9: Stage 21 – Her look and words on screen

**Goal**: Her profiles learn from what she changes, filters appear only when asked, and words on screen stay inside the safe areas.
**Depends on**: Phase 8
**Requirements**: STYL-01, STYL-02, STYL-03, STYL-04, STYL-05, STYL-06, STYL-07, STYL-08
**Success Criteria** (what must be TRUE):

  1. User can take a taste test that makes two versions of the same reel differing in one named respect and turns her pick into a single profile line; "Update my profile" proposes at most two dated lines, shows the complete revised section to paste, and never claims to have saved it
  2. The renderer draws text from the cut list's text entries in a named style, using one bundled SIL Open Font License font chosen from three samples and recorded in docs/licenses.md
  3. Text stays inside the safe area for the canvas, wraps rather than running off, reads over light and dark footage, shows for at least 1.5 seconds, reports a missing character instead of drawing a box, and appears on the proof sheet
  4. Four named filters (warm, cool, black and white, faded) are applied only when asked, with a sample of each rendered for approval, and EDITOR.md says text and filters come only from her words or standing preferences
  5. From her phone inside an account's Project, "make a reel" asks nothing her preferences already answer

**Plans**: TBD

### Phase 10: Stage 22 – Cut to the beat

**Goal**: Cuts land on the beat of the chosen music, checked by ear.
**Depends on**: Phase 9
**Requirements**: BEAT-01, BEAT-02, BEAT-03, BEAT-04, BEAT-05
**Success Criteria** (what must be TRUE):

  1. `python -m v2r music add` detects beat times and strong beats and flags tracks with no clear beat, and the existing tracks are recomputed
  2. User can run `python -m v2r music click` to get a copy of a track with a click on every detected beat, to check by ear
  3. `python -m v2r snap` aligns the music start to a strong beat and moves each cut to the nearest beat within the tolerance, never shortening a segment below the recipe's minimum or moving a cut into a shaky stretch, printing each change in plain English and changing no other field
  4. EDITOR.md says to run snap after choosing music, that Lively follows the beats and Calm every second or fourth strong beat, and to skip tracks flagged as having no clear beat
  5. Tests use a generated click track at a known tempo, and every track in the library has passed the click check by ear

**Plans**: TBD

### Phase 11: Stage 23 – Long and large files

**Goal**: Every limit is met with one plain sentence, long jobs resume, and long videos are edited on the Mac from start to finish.
**Depends on**: Phase 10
**Requirements**: LONG-01, LONG-02, LONG-03, LONG-04, LONG-05, LONG-06, LONG-07, LONG-08, LONG-09
**Success Criteria** (what must be TRUE):

  1. Every limit produces one plain sentence saying what the limit is and what to do next, naming the "Shrink for Claude" shortcut, and a render that would exceed the send-back limit is announced before rendering with a shorter or lower-quality version offered
  2. For long clips, look takes fewer stills and adds closer ones only inside candidate stretches, works at a smaller size, and reports the estimated time before anything that will take more than two minutes
  3. Every command is resumable and says what it skipped, and a video longer than the threshold is rendered in pieces and joined so no single step runs past the sandbox's time limit
  4. On a Mac a render is full quality at any length and saved beside the footage, the toolbox says in one sentence how it knows where it is running, and EDITOR.md has Claude say before any work that a video too big for the send-back limit needs the Mac
  5. The "Shrink for Claude" shortcut exists on her phone, a shrunk 4K clip's new size has been checked, one long video has been edited on the Mac from start to finish, and no server, storage service or account was added

**Plans**: TBD

### Phase 12: Stage 24 – Talking head

**Goal**: Talking-head videos are tightened by the transcript, with captions, from a plan she approved.
**Depends on**: Phase 11
**Requirements**: TALK-01, TALK-02, TALK-03, TALK-04, TALK-05, TALK-06, TALK-07
**Success Criteria** (what must be TRUE):

  1. User can run `python -m v2r words` to get a transcript with a start and end time for every word of each clip with speech, from an open-source model downloadable in the sandbox and cached once per chat, and silences are detected with FFmpeg
  2. Speech edits cut at word gaps with padding, a short audio crossfade at every join, and an optional slight alternating zoom between consecutive pieces of the same clip
  3. Captions are drawn from the word times a few words at a time, low in a wide frame and inside the safe area of a tall one, and landscape talking-head footage renders wide by default and is never cropped unless she asks for a tall version
  4. EDITOR.md's "Talking head" section proposes which sentences to keep and what to cut, states the resulting length and waits for her go, never claims to remove every filler word, and asks for the spelling of any name before captioning it
  5. Tests use generated tone-and-silence clips for the cutting and one short recorded sample for the transcript, and every cut has been listened to with earphones

**Plans**: TBD

### Phase 13: Stage 25 – Voice over pictures

**Goal**: Her voice from one clip is carried over pictures from the others.
**Depends on**: Phase 12
**Requirements**: VOIC-01, VOIC-02, VOIC-03, VOIC-04
**Success Criteria** (what must be TRUE):

  1. The renderer builds the cut list's voice track: pieces of speech from any clip, cut at word boundaries and placed at set times, mixed over picture segments whose own sound is off, with music lowered under the voice and the whole mix normalized
  2. A helper lists the natural points for picture changes from the chosen speech pieces' word times
  3. EDITOR.md's "Voice over pictures" section says when to use it, proposes the sentences and which shots go over them, waits for her go, optionally opens on the speaker, and lets the reel's length follow the voice
  4. Tests prove the voice starts and ends where the cut list says, to within one frame

**Plans**: TBD

### Phase 14: Stage 26 – Launch

**Goal**: Every line of the launch checklist is true, v1.0 is tagged, and a monthly check is in the calendar.
**Depends on**: Phase 13
**Requirements**: LAUN-01, LAUN-02, LAUN-03, LAUN-04, LAUN-05, LAUN-06
**Success Criteria** (what must be TRUE):

  1. Every line of the Stage 26 checklist is true, including her last ten reels made here with at least eight posted untouched, all the tricky clip types right from a phone, both shapes made and watched this month, and EDITOR.md still two pages
  2. The Stage 13 review has been run across the whole project and its findings fixed
  3. The seven phone tests have been rerun and docs/phone-limits.md updated
  4. A harmless merge has been undone on main on purpose, and a reel made from a phone afterwards
  5. The version is tagged v1.0 and a monthly reminder exists to rerun the phone tests and remake the five fixture reels

**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Skeleton | M1: A reel from a phone | done by hand | Complete | 2026-10-12 |
| 2. Stage 14 – Normalize | M2: It can see | 5/8 | In Progress|  |
| 3. Stage 15 – Seeing the footage | M2: It can see | 0/TBD | Not started | - |
| 4. Stage 16 – Cut list and renderer | M3: It can cut | 0/TBD | Not started | - |
| 5. Stage 17 – Editor's handbook | M3: It can cut | 0/TBD | Not started | - |
| 6. Stage 18 – Music | M3: It can cut | 0/TBD | Not started | - |
| 7. Stage 19 – Conversation | M4: It's a conversation | 0/TBD | Not started | - |
| 8. Stage 20 – Her two weeks | M5: Her two weeks | 0/TBD | Not started | - |
| 9. Stage 21 – Her look and words on screen | M6: Her look | 0/TBD | Not started | - |
| 10. Stage 22 – Cut to the beat | M6: Her look | 0/TBD | Not started | - |
| 11. Stage 23 – Long and large files | M7: Big files | 0/TBD | Not started | - |
| 12. Stage 24 – Talking head | M8: Words, then launch | 0/TBD | Not started | - |
| 13. Stage 25 – Voice over pictures | M8: Words, then launch | 0/TBD | Not started | - |
| 14. Stage 26 – Launch | M8: Words, then launch | 0/TBD | Not started | - |
