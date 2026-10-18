# Requirements: Vid2Reel

**Defined:** 2026-10-13
**Core Value:** A reel worth posting, made entirely from her phone.

Each category is one stage of docs/field-guide.html and one roadmap phase. The detail for building each one is in that stage of the guide; these lines say what must be true when it is done. "(checked by a person)" marks things only a person watching or listening can confirm.

## v1 Requirements

### Skeleton — Phase 1, done by hand (Stages 09 to 13)

- [x] **SKEL-01**: `python -m v2r doctor` reports FFmpeg and ffprobe versions, the H.264 and AAC encoders, the scale, crop, zscale, tonemap, loudnorm and drawtext filters, Python, processors, free disk and memory, and whether github.com and pypi.org are reachable
- [x] **SKEL-02**: `python -m v2r join --shape tall|wide` joins clips in the order given, upright, cropped to fill from the centre, at 30 fps in an H.264/AAC fast-start MP4, and keeps the result under `MAX_RESULT_BYTES` by lowering the bitrate and stepping the frame size down, refusing before building if it cannot fit
- [x] **SKEL-03**: The vid2reel skill clones `main` or a named branch, installs requirements with pip, reads EDITOR.md and follows it, and EDITOR.md runs the join in the background past the sandbox's 2-minute command limit
- [x] **SKEL-04**: The phone route's limits are measured and recorded in docs/phone-limits.md, and CLAUDE.md and docs/decisions.md exist

### Normalize (Stage 14)

- [x] **NORM-01**: `python -m v2r normalize` reads each attached file's facts with ffprobe (length, picture size, orientation, frames per second, HDR or not, sound or not, when shot) without changing the file
- [x] **NORM-02**: Each clip gets a working copy in work/ in one format: upright; sized for the job's shape (tall: portrait at most 1080×1920 and landscape at most 1920 high; wide: landscape at most 1920×1080 and portrait at most 1920 wide; never scaled up); constant 30 fps; ordinary colour with HDR tone-mapped so it looks natural; H.264; AAC stereo at 48 kHz, with silence added where a clip has none
- [x] **NORM-03**: A photo becomes a still clip of a length set in settings.py, and the manifest records the full-resolution photo alongside
- [x] **NORM-04**: A clip shot at 120 or 240 fps is flagged as slow-motion source material and converted at normal speed
- [x] **NORM-05**: Clips are named A, B, C in the order given, and work/manifest.json lists each clip's original facts, its working copy and how long the conversion took
- [x] **NORM-06**: A file over the limits in settings.py, or one that can't be read, gets one plain-English sentence and does not stop the others
- [x] **NORM-07**: No original file is ever written to
- [x] **NORM-08**: Only FFmpeg features the sandbox's doctor report shows are used, and tests use generated clips including one stored sideways, one at 60 fps, one with no sound and one tagged HDR

### Seeing the footage (Stage 15)

- [x] **LOOK-01**: `python -m v2r look` reads the manifest and writes contact sheets to work/: grids of stills, each labelled with its clip letter and time like "B 07.5", large enough to read, with sheet size, stills per sheet and a cap on sheets per run in settings.py
- [x] **LOOK-02**: A still is taken every second, plus extra stills at movement peaks and shot changes
- [x] **LOOK-03**: work/look.json holds, for every half second of every clip, movement, camera shake as distinct from subject movement, sharpness, brightness, sound loudness and shot changes, plus each clip's overall exposure and colour balance
- [ ] **LOOK-04**: look.json holds a ranked list of candidate moments per clip (steady, sharp, something moving) with start and end times and the reason in words; the code never chooses what goes in a reel
- [ ] **LOOK-05**: Shot-change detection uses a well-maintained open-source library if one fits, with its licence recorded in docs/licenses.md
- [x] **LOOK-06**: Tests use generated clips with a known answer, such as a shape crossing the frame between seconds 4 and 5, and prove a still lands on it
- [ ] **LOOK-07**: In the blind test, from the sheets and look.json alone, Claude picks the moment you would have picked in at least four clips out of five (checked by a person)

### Cut list and renderer (Stage 16)

- [ ] **CUT-01**: schema/cutlist.schema.json defines the cut list: the canvas (tall 1080×1920 or wide 1920×1080, fps), ordered segments (clip, from, to in seconds, focus_x from 0 to 1, optional move, own sound kept or not), the look (filter "none" unless asked, mild per-clip touch-up numbers), the sound (track id, start point, fades, music level) and a "why" per segment citing a still, with room for text, speed, transitions and a voice track
- [ ] **CUT-02**: `python -m v2r check` validates a cut list against the schema and the manifest and reports every problem as one plain-English sentence
- [ ] **CUT-03**: `python -m v2r render` builds the video from the cut list and the working copies alone, straight cuts only, every segment filling the canvas cropped around focus_x, with no letterbox and no blurred-background mode; a valid list is built exactly and an invalid one builds nothing
- [ ] **CUT-04**: A segment's optional move (push-in, pull-out, pan left, pan right) is a slow, steady change across the segment, capped in settings.py, and a photo's move is rendered from the full-resolution image
- [ ] **CUT-05**: `python -m v2r match` reads each clip's exposure and colour balance from look.json and writes a mild per-clip correction into the cut list, capped in settings.py; the renderer applies exactly those numbers and nothing else to colour, and the filter field accepts only "none" for now
- [ ] **CUT-06**: Each segment's own sound can be on or off, music is laid underneath with the start point, fades and level from the cut list, and the finished mix is normalized to the loudness the main platforms target, with the figure used stated
- [ ] **CUT-07**: The output is an MP4 with H.264 video and AAC sound at the canvas size and frame rate, fast-start, under `MAX_RESULT_BYTES`, with a contact sheet of the finished video and a cover still alongside
- [ ] **CUT-08**: Fields for text, speed, transitions and a voice track are accepted and ignored with a note
- [ ] **CUT-09**: Golden renders exist in both shapes from generated clips, with expected length, size and a colour check at a known second, and the same cut list always makes the same video

### Editor's handbook (Stage 17)

- [ ] **HAND-01**: EDITOR.md is the complete handbook: the steps in order naming each command; how to study the sheets and look.json; rules of craft for choosing and ordering moments; the Lively and Calm recipes with shot lengths; the house rules; the honesty rules (every "why" cites a still, guesses are called guesses, never "I watched your clips"); what to do when a file can't be read or there is too little footage; the order of authority (the chat, then the taste profile, then the handbook); tools only. Two pages at most, plain words
- [ ] **HAND-02**: No editing judgement lives in Python, and no one person's taste lives in EDITOR.md
- [ ] **HAND-03**: A "Reel style" taste profile is drafted for each social account named in the taste notes, saved in fixtures/ and never in the repo
- [ ] **HAND-04**: The rehearsal (after /clear, with EDITOR.md and one profile) runs for all five fixture sets, and a second profile on the same set changes only what the profiles differ in
- [ ] **HAND-05**: She would post at least three of the five fixture reels with small changes (checked by a person)

### Music (Stage 18)

- [ ] **MUS-01**: music/library.json describes each track: id, title, mood words, beats per minute, energy 1 to 5, length, the second where it gets going, licence, source page and date checked
- [ ] **MUS-02**: `python -m v2r music add` measures a track's tempo and loudness, converts it to a compact standard format, asks for mood words, the licence and the source page, and refuses to add a track without a licence and a source; tempo is measured on the Mac, never in the sandbox
- [ ] **MUS-03**: `python -m v2r music list` prints the library for the chat's Claude to choose from
- [ ] **MUS-04**: Music under kept clip sound is lowered while that sound is present and comes back up after; a fast fade in and a fade out over the last 1.5 seconds, both in settings.py; the final mix still normalized
- [ ] **MUS-05**: EDITOR.md says how to choose a track from the list by the user's words or the reel's pace, always names the track chosen, and offers "no music"
- [ ] **MUS-06**: Eight to twelve tracks chosen with her, each with CC0 or public-domain status stated on its own page, are in the library with her mood words

### Conversation (Stage 19)

- [ ] **CONV-01**: EDITOR.md's "Talking with her" section asks a brief of three to five numbered questions in one message (what the reel is about; which moment is the star; lively or calm; shape and length; music), each answerable in a few words and each with a default, leaving out any question already answered, and skipping the brief when she says to just make it
- [ ] **CONV-02**: At most one further question is asked after looking at the footage, and only if the moment she named can't be found
- [ ] **CONV-03**: Work starts with one line and a time estimate, then silence until the reel
- [ ] **CONV-04**: The reply is the video, at most two lines on what is in it and which track, and three suggested follow-ups; clips are described by what is in them, never by letter
- [ ] **CONV-05**: `python -m v2r revise` applies one named change to an existing cut list (shorten or lengthen to a target, reorder, drop a clip, change the music or sound, change the canvas) and leaves every other field untouched, and tests prove each revision changes only its own fields
- [ ] **CONV-06**: Errors are plain English ending with a next step, and if the work folder is gone Claude asks for the clips again instead of failing confusingly
- [ ] **CONV-07**: The whole conversation works from a phone on the branch: attach, brief, reel, then "shorter", "different song" and "a wide version", each changing only what was asked (checked by a person)

### Her two weeks (Stage 20)

- [ ] **WEEK-01**: She has the two-line instructions and has made one reel with you watching
- [ ] **WEEK-02**: fixtures/reel-log.md has one entry per reel: posted as it came, posted after an outside fix (what), or not posted (why, in her words), plus follow-ups, which brief questions she answered, time from send to saved, and whether her plan ran out
- [ ] **WEEK-03**: After two weeks or ten reels, the five most common complaints are listed with their likely cause, and fixed one at a time, each tested from a phone before merging
- [ ] **WEEK-04**: The call is made: at least half posted without another editor means on to Stage 21; otherwise back to Stage 15 or 17

### Her look and words on screen (Stage 21)

- [ ] **STYL-01**: EDITOR.md's "Taste test" makes two versions of the same reel differing in exactly one named respect, asks which she prefers, and writes the single profile line that implies
- [ ] **STYL-02**: EDITOR.md's "Update my profile" proposes at most two dated lines from what she changed in the chat, shows the complete revised "Reel style" section to paste, never claims to have saved it, and offers a line to remove whenever one is added
- [ ] **STYL-03**: Profile lines are suggested for each social account from fixtures/reel-log.md
- [ ] **STYL-04**: The renderer draws text overlays from the cut list's text entries (words, start and end, upper/middle/lower, a named style from settings.py) with one font under the SIL Open Font License bundled and recorded in docs/licenses.md, chosen from three samples
- [ ] **STYL-05**: Text stays inside the safe area for the canvas (the most cautious current platform figures when tall, sources given, stored in settings.py; a plain margin when wide), wraps rather than runs off, reads over light and dark footage, shows for at least 1.5 seconds, reports a missing character instead of drawing a box, and appears on the proof sheet
- [ ] **STYL-06**: Four named filters (warm, cool, black and white, faded) are fixed recipes in settings.py, applied after the touch-up only when the cut list names one, with a sample of each rendered for approval
- [ ] **STYL-07**: EDITOR.md says text only when the user asks, with the exact words repeated in the reply, and a filter only when the user's message or standing preferences ask, with the filter named in the reply
- [ ] **STYL-08**: From her phone inside an account's Project, "make a reel" asks nothing her preferences already answer (checked by a person)

### Cut to the beat (Stage 22)

- [ ] **BEAT-01**: `music add` detects beat times and strong beats with librosa, a development-only dependency not needed in the sandbox, stores them in library.json with a flag for tracks that have no clear beat, and the existing tracks are recomputed
- [ ] **BEAT-02**: `python -m v2r music click` writes a copy of a track with a click on every detected beat
- [ ] **BEAT-03**: `python -m v2r snap` aligns the music start to a strong beat and moves each cut to the nearest beat within a settings.py tolerance, never shortening a segment below the recipe's minimum and never moving a cut into a stretch look.json marks as shaky, printing each change in plain English and changing no other field
- [ ] **BEAT-04**: EDITOR.md says to run snap after choosing music, that Lively follows beats and Calm every second or fourth strong beat, and to skip tracks flagged as having no clear beat
- [ ] **BEAT-05**: Tests use a generated click track at a known tempo, and every track in the library has passed the click check by ear (checked by a person)

### Long and large files (Stage 23)

- [ ] **LONG-01**: Every limit produces one plain sentence saying what the limit is and what to do next, naming the "Shrink for Claude" shortcut
- [ ] **LONG-02**: For clips longer than a settings.py threshold, look takes fewer stills, relies on the measurements to find candidate stretches, adds closer stills only inside them within the sheet cap, processes at a smaller working size, and reports the estimated time before anything that will take more than two minutes
- [ ] **LONG-03**: A render that would exceed the send-back limit is announced before rendering, with a shorter or lower-quality version offered
- [ ] **LONG-04**: Every command is resumable: it skips any step whose output exists and is newer than its input, and says what it skipped
- [ ] **LONG-05**: A video longer than a settings.py threshold is rendered in pieces and joined, so no single step runs past the sandbox's time limit
- [ ] **LONG-06**: The send-back limit applies only in the sandbox; on a Mac a render is full quality at any length and is saved beside the footage, and the toolbox says in one sentence how it knows where it is running
- [ ] **LONG-07**: EDITOR.md says that when a video cannot fit under the send-back limit at a watchable quality, Claude says so before doing any work and says it needs the Mac
- [ ] **LONG-08**: The "Shrink for Claude" shortcut exists on her phone, a shrunk 4K clip's new size has been checked, and one long video has been edited on the Mac from start to finish (checked by a person)
- [ ] **LONG-09**: No server, storage service or account is added

### Talking head (Stage 24)

- [ ] **TALK-01**: `python -m v2r words` produces a transcript with a start and end time for every word, for each clip with speech, using an open-source speech model downloadable inside the sandbox from github.com or pip, cached once per chat; the options were compared on size, speed without a GPU, licence and true word-level times, and one recommended
- [ ] **TALK-02**: Silences are detected with FFmpeg
- [ ] **TALK-03**: The cut list and renderer support speech edits: segments cut at word gaps with padding from settings.py, a short audio crossfade at every join, and an optional alternating slight zoom between consecutive pieces of the same clip
- [ ] **TALK-04**: Captions are drawn from the word times in the Stage 21 text style, a few words at a time, low in a wide frame and inside the safe area of a tall one
- [ ] **TALK-05**: Landscape talking-head footage renders wide by default and is never cropped; tall clips are made from it only when the user asks, cropped around the speaker with focus_x
- [ ] **TALK-06**: EDITOR.md's "Talking head" section reads the transcript, proposes which sentences to keep and what to cut, states the resulting length and waits for the user's go, keeps the last complete take of a repeated sentence, never claims to remove every filler word, and asks for the spelling of any name before captioning it
- [ ] **TALK-07**: Tests use generated tone-and-silence clips for the cutting and one short recorded spoken sample for the transcript, and every cut has been listened to with earphones (checked by a person)

### Voice over pictures (Stage 25)

- [ ] **VOIC-01**: The renderer builds the cut list's voice track: pieces of speech from any clip, chosen at word boundaries, placed at times on the reel, mixed over picture segments whose own sound is off, with music lowered under the voice and the whole mix normalized
- [ ] **VOIC-02**: A helper lists the natural points for picture changes from the chosen speech pieces' word times
- [ ] **VOIC-03**: EDITOR.md's "Voice over pictures" section says when to use it, proposes the sentences and which shots go over them and waits for the go, optionally opens on the speaker, and lets the reel's length follow the voice
- [ ] **VOIC-04**: Tests prove the voice starts and ends where the cut list says, to within one frame

### Launch (Stage 26)

- [ ] **LAUN-01**: Every line of the guide's Stage 26 checklist is true, including: her last ten reels made here with at least eight posted untouched; HDR, sideways, photo, silent and slow-motion clips all right from a phone; both shapes made and watched this month; a long video edited on the Mac; every limit one plain sentence; follow-ups change only what was asked; golden renders pass; every track licensed and click-checked; the repo's history holds no footage, names or secrets; EDITOR.md still two pages
- [ ] **LAUN-02**: The Stage 13 review has been run across the whole project on Fable and its findings fixed
- [ ] **LAUN-03**: The seven phone tests have been rerun and docs/phone-limits.md updated
- [ ] **LAUN-04**: A harmless merge has been undone on main on purpose, and a reel made from a phone afterwards
- [ ] **LAUN-05**: The version is tagged v1.0
- [ ] **LAUN-06**: A monthly reminder exists to rerun the phone tests and remake the five fixture reels

## v2 Requirements

Deferred. Tracked but not in the roadmap; Stage 27 starts as a separate idea chat, not a phase.

### Product version (Stage 27)

- **PROD-01**: A written briefing (docs/product-notes.md) on what a sellable version would reuse, what assumes the chat sandbox, and what the Claude API would have to do
- **PROD-02**: Every library, font and music licence re-read for commercial use
- **PROD-03**: One of two shapes chosen: sell the skill, or build a web app with storage, a render worker and the Claude API

## Out of Scope

| Feature | Reason |
|---------|--------|
| A website, accounts, payments, other users | Stage 27, and only if Stage 20 shows she would rather use this than anything else |
| Transcripts, captions, voice-over, text on screen, beat matching, files too large to attach, saved preferences, before Stage 21 | The MVP is defined by what is cut; these all live in Stages 21 to 25 |
| Google Drive or any cloud storage | The sandbox can't reach it, and the 30 MiB wall is not a storage problem |
| Music that is only free to download, or attribution-licensed | A public repo redistributes every file; only CC0 fits |
| An MCP server on the Mac | It can't follow her phone |
| Fancy transitions, speed changes, filters by default | Straight cuts are what most reels use; filters only when asked (Stage 21) |

## Traceability

Each category maps to one phase, in guide order. Phase 1 is complete.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SKEL-01 to SKEL-04 | Phase 1 – Skeleton | Complete |
| NORM-01 to NORM-08 | Phase 2 – Stage 14 – Normalize | Complete |
| LOOK-01 to LOOK-07 | Phase 3 – Stage 15 – Seeing the footage | Pending |
| CUT-01 to CUT-09 | Phase 4 – Stage 16 – Cut list and renderer | Pending |
| HAND-01 to HAND-05 | Phase 5 – Stage 17 – Editor's handbook | Pending |
| MUS-01 to MUS-06 | Phase 6 – Stage 18 – Music | Pending |
| CONV-01 to CONV-07 | Phase 7 – Stage 19 – Conversation | Pending |
| WEEK-01 to WEEK-04 | Phase 8 – Stage 20 – Her two weeks | Pending |
| STYL-01 to STYL-08 | Phase 9 – Stage 21 – Her look and words on screen | Pending |
| BEAT-01 to BEAT-05 | Phase 10 – Stage 22 – Cut to the beat | Pending |
| LONG-01 to LONG-09 | Phase 11 – Stage 23 – Long and large files | Pending |
| TALK-01 to TALK-07 | Phase 12 – Stage 24 – Talking head | Pending |
| VOIC-01 to VOIC-04 | Phase 13 – Stage 25 – Voice over pictures | Pending |
| LAUN-01 to LAUN-06 | Phase 14 – Stage 26 – Launch | Pending |

**Coverage:**

- v1 requirements: 89 total (4 complete)
- Mapped to phases: 89
- Unmapped: 0 ✓

---
*Requirements defined: 2026-10-13*
*Last updated: 2026-10-13 after initial definition*
