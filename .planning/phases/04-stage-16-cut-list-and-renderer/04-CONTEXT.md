# Phase 4: Stage 16 – Cut list and renderer - Context

**Gathered:** 2026-10-19 (the design in the Stage 15 session; the discuss step the same day, in a fresh window)
**Status:** Ready for planning

<domain>
## Phase Boundary

Three commands and a rulebook. `schema/cutlist.schema.json` describes a cut list. `python -m v2r check` validates a cut list against the schema, against work/manifest.json and against music/library.json, and prints every problem as one plain-English sentence and every note as one more. `python -m v2r match` reads each clip's exposure and colour balance from work/look.json and writes a mild, capped per-clip correction into the cut list. `python -m v2r render` builds the video from the cut list and the working copies alone: straight cuts, every segment filling the canvas cropped around its focus point, the optional slow move, the touch-up numbers applied and nothing else to colour, each segment's own sound kept or off, music underneath from its start point with fades and dropped under kept sound, the mix evened to the stated loudness, an H.264/AAC fast-start MP4 at the canvas size under MAX_RESULT_BYTES, plus a proof sheet and a cover still. The renderer makes no choices: a valid list is built exactly, an invalid one builds nothing. Golden renders in both shapes.

Not in this phase: filters other than "none" (Stage 21), text (Stage 21), beat matching (Stage 22), the music library itself and ducking that follows the sound (Stage 18), speech cuts, captions and the voice track (Stages 24, 25), the handbook's choosing rules (Stage 17). EDITOR.md lines are proposed as text only; the user writes EDITOR.md.

</domain>

<decisions>
## Implementation Decisions

### The cut-list file (designed 2026-10-19 from the guide's Stage 05 prompt; confirmed with the two examples in the discuss step)
- **D-01:** One JSON file per edit, written by the chat's Claude, checked by `check`, built by `render`. Every time is seconds on a working copy, never a frame number; the working copies keep the originals' timing (Stage 14 never trims, retimes or speeds a clip), so a list means the same thing on the Mac and the phone. The renderer rounds each segment's length to whole frames at OUTPUT_FPS by one stated rule (nearest frame), so 2.5 seconds is 75 frames every time and two lists that differ by less than a frame make the same video. — **Reversibility:** one-way — every logged cut list depends on it.
- **D-02:** `version`: 1. A later change to the layout gets a new number and old lists still render.
- **D-03:** `canvas`: `width`, `height`, `fps`. Only the two shapes are allowed (1080×1920 or 1920×1080 at OUTPUT_FPS), and the canvas must match the shape the manifest was normalized for, because working copies are sized per job shape and nothing is enlarged. "Render the same list wide" means normalize wide first; the checker says so in one sentence. — **Reversibility:** costly — the handbook's "wide version" follow-up (Stage 19) is built on it.
- **D-04:** `clips`, required: one record per letter with `file` (the original's name as the manifest records it) and `seconds` (the working copy's length), copied from the manifest. The checker refuses, one sentence per clip, a list whose letters do not match the work folder's files ("clip B in this list was IMG_4423.MOV, but B in the work folder is IMG_4410.MOV"), so a list pasted into a fresh chat on the phone cannot silently cut the wrong clip. A letter the manifest marks skipped may not appear in a segment. — **Reversibility:** one-way — lists are pasted between chats from the first phone test on.
- **D-05:** `segments`, in order, each with `clip` (letter), `from` and `to` (seconds on that clip's working copy, `from` before `to`, both inside the clip), `focus_x` and `focus_y` (0 to 1, default 0.5), `move` ("none" by default, "push-in", "pull-out", "pan-left" or "pan-right"), `sound` ("keep" or "off", required so a reel's sound is never an accident) and `why` (a sentence citing still labels). The focus point is the spot in the source picture that sits at the centre of the frame when it can: 0 is the left or top edge, 1 the right or bottom; near an edge the window stops at the edge and never shows anything outside the picture; a focus point that can move nothing (a clip that already fills the canvas on that axis) is ignored silently, so one list serves both shapes. "pan-left" means the frame travels left across the picture, the way a camera turning left looks. The reel's length is the sum of the segments and nothing else. — **Reversibility:** one-way — the other reading of a focus point (the window's position) gives different crops from the same number, and a reversed pan reverses every old list.
- **D-06:** `look`: `filter` (always "none" until Stage 21; accepted, only "none" built) and `touch_up`, one record per clip letter written by `match` from look.json's `overall`: `brightness`, `blue` and `red` as offsets in 8-bit code values (the units look.json measures: 16 is black, 235 white, colour offsets from neutral 128) and `saturation` as a multiplier, each capped in settings.py. The renderer applies exactly those numbers and nothing else to colour. The block is optional: a list without it is built with nothing done to colour and the checker notes "no touch-up in the list; run match if the clips should match" (the house rule of a mild touch-up stays the handbook's job). — **Reversibility:** costly — the units are fixed once reels are logged with them.
- **D-07:** `sound`: `music` (a track id from music/library.json, or null; a generated test tone with its own id stands in until Stage 18), `music_from` (seconds into the track), `fade_in` and `fade_out` (seconds; optional, the defaults are settings in settings.py and a stated value wins), `music_under_sound` (dB, at or below 0: how far the music drops for the whole of every segment whose sound is kept; built now, segment by segment, with a short ramp at each boundary that is a setting and a technical necessity, not a choice; Stage 18 makes it follow the actual sound under the same name) and `loudness` (the LUFS target the whole mix is evened to, stated in the list so it is never a hidden choice; the default is in settings.py). — **Reversibility:** costly — the sound model is what Stage 18's ducking refines.
- **D-08:** Accepted and ignored with a note (CUT-08): per-segment `speed` and `transition`, `text` entries (per segment or top level) and a top-level `voice` track. The checker reports "accepted but not built yet", never fails on them. Unknown fields are noted, not fatal.
- **D-09:** `cover`: optional, `{ "segment": n, "at": seconds }`, a segment number (1-based, in list order) and seconds into that segment, so the cover follows its shot when the reel is shortened or reordered. When absent, the cover is the first frame of the reel: a stated rule, and what the platforms show by default; the handbook may tell Claude to name a better one.
- **D-10:** The checker's sentences, one each, in plain English: the list is JSON and has the version; the canvas is one of the two shapes and matches the manifest's shape; every `clips` letter exists in the manifest with the same file and length, and every segment's letter is in `clips` and not skipped; `from` is before `to` and both sit inside the clip's length; focus points are between 0 and 1; the move is one of the five names; segment sound is "keep" or "off"; the music track exists in the library (or is the test tone) and, from `music_from`, is at least as long as the reel ("the music runs out at 14.0 seconds but the reel is 20.0 seconds long"); every touch-up number is within its cap; the total length is at least the shortest reel allowed (a setting); the cover's segment exists and `at` is inside it. Notes, never refusals: a photo with no move; no touch-up block; a silent reel (no music and every segment off); an upright clip in a wide canvas (or a sideways one in a tall canvas) that keeps less than a set share of its picture, as the guide asks Claude to say; the accepted-but-not-built fields; unknown fields.
- **D-11:** Golden renders: fixed cut lists in both shapes over generated clips, checked for length to the frame, size under the limit, the right colour at a known second, every segment present, and the same list giving the same video twice — compared by what the frames show (decoded frame hashes or measured values), not file bytes, since encoders are not byte-identical between runs.

### Steers from the user (2026-10-19)
- **D-12:** Naming the subject in the message steers the reel: what the user types outranks everything, and the chat's Claude uses it to pick moments and set focus points. Stage 19 makes it the first two brief questions; nothing in this phase needs to change for it.
- **D-13:** Attach order only names clips (A, B, C). The cut list orders shots freely by craft (Stage 17's rules); the manifest's `shot_at` gives the real chronology when "in the order they happened" is asked for. Nothing ties a reel to attach order.

### Sound (discussed 2026-10-19)
- **D-14:** The default loudness target is -14 LUFS integrated with a true-peak ceiling of -1 dBTP, both settings in settings.py. No platform publishes an official page; -14 is the figure every source agrees YouTube uses and the common short-form target, and reports for Instagram and TikTok vary around it. The figure is stated in docs/decisions.md and in render's closing sentence; a list's `loudness` may say otherwise.
- **D-15:** When the track, from `music_from`, is shorter than the reel, the checker refuses with one sentence and nothing is built; the chat's Claude picks an earlier start or another track. No looping, no silent tail.
- **D-16:** Fades are optional in the list; absent, the values in settings.py apply (a short fade in, a fade out over the last 1.5 seconds, which is where Stage 18's MUS-04 wants them). A stated value always wins.
- **D-17:** A silent reel (no music, every segment off) is allowed: the checker notes "this reel has no sound at all" and builds it, since she may add music in the app.

### Movement (discussed 2026-10-19)
- **D-18:** The move amount is one setting, 4 percent of the frame (`MOVE_AMOUNT = 0.04`), used in full by every move; the list carries no amount. On a 3-second shot that is about 43 pixels of a tall frame, half a pixel a frame: noticed only when looked for. The user halves it on sight if a move reads as an effect, as the guide says.
- **D-19:** A push-in starts at the fitted crop and ends 4 percent tighter, centred on the focus point; a pull-out is the reverse. A pan crops in by the move amount so there is always room, then travels exactly that far across the picture: a pan means the same thing on every shot, including an upright clip in a tall canvas with no spare width.
- **D-20:** A move progresses at one steady speed across the whole segment (CUT-04's "slow, steady change"); no easing. Simplest to prove identical on FFmpeg 6.1 and 8.0 and to judge for stutter.
- **D-21:** The guide's "a photo gets a move by default" lives in the handbook, not the renderer: an EDITOR.md line (proposed as text) tells the chat's Claude to write a push-in on every photo unless she wants it still, and the checker notes "D is a photo with no move" and still builds. A photo's move is rendered from the full-resolution upright copy normalize saved (Phase 2's D-10), never from the 4-second still clip.

### The match step (discussed 2026-10-19)
- **D-22:** The group's middle is the median of the clips' values (brightness, blue offset, red offset, saturation from look.json's `overall`), so one odd clip, a dark one or a photo, does not pull the rest. Photos are treated like any clip; a skipped clip or one look could not measure gets no record and a note.
- **D-23:** Caps, in settings.py: brightness ±8 code values, each colour offset ±4 code values, saturation 0.92 to 1.08. About a third of a stop, a faint tint, a hair of colour: enough to make one shoot of two, not enough to call a filter. The user halves them on sight.
- **D-24:** Colour is nudged towards the group's middle, never towards neutral grey: a golden-hour shoot stays golden and the clips only come to agree with each other.
- **D-25:** `match` rewrites every clip's record each run, so "halve the cap and run match again" gives new numbers; it never fills only the missing ones.

### Outputs (discussed 2026-10-19)
- **D-26:** The proof sheet shows the first and the last frame of every segment, labelled with the segment number and the reel time, drawn with look's sheet code on as many sheets as needed (a seven-shot reel is two sheets); that is where a black frame or a crop onto a shoulder shows. The cover still follows D-09.
- **D-27:** render runs the check itself first, builds nothing on a refusal, leaves no half-written file behind on a failure, fits the file under MAX_RESULT_BYTES by join's length-to-quality rule and says so in one sentence when quality was stepped down, and ends with one sentence naming the file, its size, the frame size and the loudness figure used.

### Claude's Discretion
- The exact FFmpeg filter chains (trim/setpts, crop with focus and the move via crop expressions or zoompan on the full-resolution source, lutyuv or eq for the touch-up, concat, volume/afade/amix/loudnorm), as long as they exist in FFmpeg 6.1 and doctor lists them; the half-open [from, to) rule; the test-tone recipe and id; the ramp length at a music-drop boundary (a setting); the share of picture below which the checker notes a crop (a setting).
- The JSON Schema's structure and the error-to-sentence mapping; the file names of the list (work/cutlist.json by default), the output, the proof sheets and the cover still; the label format on the proof sheet; how the fit step reuses join's FIT_STEPS; the names of the new settings.
- The order of the checker's sentences and how match prints what it wrote (one line per clip, as normalize and look do).

</decisions>

<the_plan_given_on_2026-10-19>
## The plain-English plan already given (the guide's Stage 16 prompt was answered in the Stage 15 session)

Three commands and a rulebook (see the domain). For each segment: trim to its seconds, crop to the canvas around the focus point, apply the optional move, apply the touch-up numbers; join with straight cuts; sound per segment or silence, music underneath from its start with fades and dropped under kept sound, the mix evened to the stated loudness; MP4 fitted under the send limit by the join's length-to-quality rule, saying so when quality was stepped down; proof sheet with the look step's sheet code; cover still from the list's segment and second or the first frame. The renderer refuses to choose: an invalid list builds nothing; nothing is trimmed, nudged or reordered; text, speed, transitions and voice are noted, not built; a tall canvas has one mode, crop to fill. Tests: the golden renders in both shapes; the checker's sentences; caps on the touch-up; a photo's push-in from the full-resolution copy; both shapes throughout. Time: about 2.6 s of work per second of video at full size on the phone (docs/phone-limits.md), so a 20 s reel is under a minute and longer ones run in the background as normalize and look do; doctor grows to list the filters render uses.

**Trickiest part:** the gentle movement — a push-in or pan that is slow and perfectly smooth, rendered from a 48-megapixel photo or a 4K working copy, identical on FFmpeg 6.1 and 8.0, inside the sandbox's time; a stutter in a slow move is a fault only the user's eye on a phone can judge. Second: proving the same list makes the same video, since encoders are not byte-identical between runs.

</the_plan_given_on_2026-10-19>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The stage and its rules
- `docs/field-guide.html` — read only Stage 16 (between the `id="s16"` and `id="s17"` markers); never edit it. Its example cut list, "What this stage must do" list, the settled Decide box (crop to fill), the Do-this steps and the Watch out (a renderer that tries to help is the bug).
- `CLAUDE.md` and `.claude/CLAUDE.md` — three jobs that never mix (render builds exactly the list), settings.py holds every number, public repo, plain-English explanations, decisions in docs/decisions.md, no attribution lines in commits.
- `docs/decisions.md` — add dated Stage 16 lines for what differs from the guide: sound per segment instead of one top-level switch; touch-up as numbers per clip instead of the word "match"; a vertical focus point; the loudness target written in the list and its figure (-14 LUFS, -1 dBTP); the required `clips` block; the cover by segment and second; the canvas tied to the manifest's shape; the 4 percent move amount and pans that crop in by it; the touch-up caps and the median; the proof sheet's first-and-last-frame rule.
- `.planning/REQUIREMENTS.md` §Cut list and renderer (Stage 16) — CUT-01 to CUT-09.
- `.planning/ROADMAP.md` §Phase 4 — goal and success criteria.
- `.planning/phases/03-stage-15-seeing-the-footage/03-CONTEXT.md` and `v2r/look/__init__.py` (docstring) — look.json's frozen names (`overall`, `stills` labels, `candidates`), which `match` reads and `why` cites.
- `.planning/phases/02-stage-14-normalize/02-CONTEXT.md` — the manifest's frozen names, the full-size photo copy (D-10) the move is rendered from, skipped letters (D-19).

### The sandbox and its limits
- `docs/phone-limits.md` — FFmpeg 6.1, two processors, the 2-minute command limit, 30 MiB back, the measured work per second of video, tests 1 to 14.

### Existing code to follow
- `v2r/join.py` — the fit step (FIT_STEPS, FIT_HEADROOM, MAX_RESULT_BYTES), the crop-to-fill, the house FFmpeg pattern, fast-start.
- `v2r/normalize.py` — the manifest's frozen names and the whole-or-nothing write; `run_ffmpeg()` and `ffmpeg_timeout()`.
- `v2r/look/sheets.py` — the sheet drawing to reuse for the proof sheet; `v2r/look/__init__.py` — the run shape (one line per clip, background by the handbook).
- `v2r/settings.py` — every number with a unit comment; the `# look:` block's style. New here: the move amount, the touch-up caps, the loudness target and true-peak ceiling, the fade defaults, the music-drop ramp, the shortest reel, the crop-share note threshold.
- `v2r/doctor.py` — `FILTERS`; grow for concat, trim, atrim, afade, amix, volume, loudnorm, zoompan, lutyuv or whatever render uses.
- `tests/media.py`, `tests/test_join.py`, `tests/test_look*.py` — generated clips, both shapes, `probe()`.
- `EDITOR.md` — the user's handbook; propose the check, match and render steps and the photo push-in line as text only.
- `music/library.json` — empty until Stage 18; the checker reads it when it exists and knows the test tone's id without it.

</canonical_refs>

<code_context>
## Existing Code Insights
- The join already fits a video under MAX_RESULT_BYTES by length (FIT_STEPS), crops to fill from the centre, and writes fast-start MP4: render generalises it with focus points, per-segment trims, moves, colour and sound.
- look.json's `overall` block gives `brightness`, `brightness_low`, `brightness_high`, `blue_shift`, `red_shift`, `saturation` per clip, measured on signalstats averages against neutral grey (128): `match` works from these, and its offsets are in the same units, so the touch-up can be applied as exact code-value offsets on the luma and chroma planes.
- The manifest records each clip's original file name, its working copy, its length, `shot_at`, a photo's full-size upright copy and skipped entries with their letters: everything `clips` and the checker need.
- Stills are labelled "B 07.5"; `why` cites those labels; the proof sheet reuses `SheetBook` with its own labels.
- Phase 3's run quirks apply: sequential executors on the branch, `--force-isolation none`, macOS has no `timeout` (use gsd-tools run-with-timeout), the full suite is about 7 minutes, never run commands against work/ or fixtures/ from the repo root.

</code_context>

<specifics>
## Specific Ideas
- The two examples the user approved on 2026-10-19 are the shape of every list: a 20-second tall reel of seven segments over four clips and a photo (sound kept on one laugh, a pan following a walk, a push-in on the photo, music dropped 12 dB under the laugh, cover from the laugh), and a 38-second wide talking head with two cut-aways (every talking segment keeps its sound, music 20 dB under it, the upright cut-away cropped around `focus_y`, a pull-out on a photo). The planner writes both into the golden tests, with generated clips in place of the files.
- The guide's Do-this: a reel by hand from one fixture set, watched on a phone with sound; the same reel with and without the touch-up; a photo with a slow push-in that is noticed only when looked for; a segment past a clip's end gives a sentence and no video; "make the second shot one second shorter" changes one number and one shot; the same list rendered wide after normalizing wide; the phone test on branch stage-16-render with the cut list pasted as text.
- Every change explained in plain English with what to look at and at what second.

</specifics>

<deferred>
## Deferred Ideas
- Ducking that follows the actual sound and the real music library — Stage 18 (the per-segment drop built here is its first form). Named filters and text — Stage 21. Beat alignment — Stage 22. Resumable renders in pieces and the Mac's no-limit mode — Stage 23. Speech cuts, captions, voice — Stages 24 and 25.
- Listing excluded candidate stretches as facts (IN-02's optional idea) — if the reel log shows Claude needs it.
- A run-in-progress guard for two normalize runs at once (Phase 3's observation) — a later stage.

</deferred>

---

*Phase: 04-stage-16-cut-list-and-renderer*
*Context gathered: 2026-10-19*
