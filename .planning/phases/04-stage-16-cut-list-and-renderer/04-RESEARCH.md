# Phase 4: Stage 16 – Cut list and renderer - Research

**Researched:** 2026-10-19
**Domain:** FFmpeg 6.1 video/audio rendering driven by a JSON cut list; JSON Schema validation; deterministic output
**Confidence:** HIGH for the FFmpeg recipes (every one was run on a real FFmpeg 6.1 binary and on 8.0.1 in this session); MEDIUM for sandbox timing (measured on the Mac only)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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

### Deferred Ideas (OUT OF SCOPE)
- Ducking that follows the actual sound and the real music library — Stage 18 (the per-segment drop built here is its first form). Named filters and text — Stage 21. Beat alignment — Stage 22. Resumable renders in pieces and the Mac's no-limit mode — Stage 23. Speech cuts, captions, voice — Stages 24 and 25.
- Listing excluded candidate stretches as facts (IN-02's optional idea) — if the reel log shows Claude needs it.
- A run-in-progress guard for two normalize runs at once (Phase 3's observation) — a later stage.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CUT-01 | schema/cutlist.schema.json defines the cut list | jsonschema 4.26.0 with a Draft 2020-12 schema; permissive on unknown keys (notes come from Python); see "Check" pattern and sentence mapping |
| CUT-02 | `check` validates against schema and manifest, one plain sentence per problem | `Draft202012Validator.iter_errors` reports every error with `validator`, `absolute_path`, `instance`; semantic checks run on one shared pure `plan()` |
| CUT-03 | `render` builds exactly the list, straight cuts, fill the canvas around focus, nothing built when invalid | Pure `plan()` + per-segment FFmpeg pieces (exact frames via `-ss` pre-seek + `trim=start_frame/end_frame`); crop-first geometry; check runs first |
| CUT-04 | slow steady move, capped; photo move from the full-resolution copy | `perspective` filter with `eval=frame` (sub-pixel, measured smooth); photo cropped and scaled once from `photo.file`, `loop`ed, then moved |
| CUT-05 | `match` writes mild capped per-clip correction; renderer applies exactly those numbers | median of `overall`; `lutyuv` with explicit clamps and `round()`; verified exact arithmetic |
| CUT-06 | segment sound kept/off, music underneath, mix normalized to stated loudness | sample-exact `atrim`, `aevalsrc`+`amultiply` music envelope, `amix normalize=0`, ebur128 measure + `volume` gain (hit -14.0 LUFS exactly) |
| CUT-07 | H.264/AAC fast-start MP4 at canvas size under MAX_RESULT_BYTES, contact sheet and cover | `join.fit()` reused; `-movflags +faststart`; SheetBook with its own folder/prefix; cover via `grab_stills` |
| CUT-08 | text, speed, transitions, voice accepted and ignored with a note | schema leaves these keys open; Python note table |
| CUT-09 | golden renders in both shapes, same list same video | decoded-frame hashes (`-f md5`) equal across runs; measured colour at known frames; see Validation Architecture |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

Both `./CLAUDE.md` and `./.claude/CLAUDE.md` were read. Directives that bind this phase:

- **Runtime is the chat sandbox:** Python 3.13 and FFmpeg only (6.1.1 there, 8.0.1 on the Mac), packages from pip via `requirements.txt` (regenerate after any `uv add` with the command in README.md), no GPU, no network except github.com, any command stopped after 2 minutes, at most 30 MiB back.
- **Three jobs never mix:** `v2r/look/` measures only; the cut list is the only place edit decisions live; `v2r/render/` builds exactly what the list says and makes no choices; `v2r/normalize` is the only converter. Originals are never modified; every output is a new file.
- **Every tunable number lives in `v2r/settings.py`** with a unit comment.
- **Both shapes first-class;** no command, default or test may assume tall.
- **EDITOR.md is the user's:** propose lines as text only, never edit it. Taste never goes in the repo.
- **Public repo:** no video/photos/audio from fixtures/ or work/; no names; no secrets; no attribution lines in commits. Only CC0 music in music/ with licence in music/library.json.
- **Library check first:** before writing anything from scratch check for a maintained open-source library, say its licence, list it in docs/licenses.md.
- **Decisions:** write each settled or changed decision into CLAUDE.md and add a dated line to docs/decisions.md (stage, what, how it differs from the guide; no person or account named).
- **Never edit docs/field-guide.html;** read only Stage 16.
- **Phone test before merge:** after any change to how video is processed, tell the user to test from a phone; say exactly what to look or listen for and at what second (the model cannot watch or hear).
- **Do not run `normalize` or `look` against the repo's `work/`** (it holds the user's bench); tests generate their own clips in `tmp_path`.
- **GSD:** one phase per stage on branch `stage-16-render` (guide's name), never merged until a phone reel exists.

## Summary

The renderer is a pure function from (cut list, manifest, library) to a *plan* (frame ranges, crop rectangles, move windows, touch-up numbers, music gain curve) followed by an FFmpeg executor. Everything below was proven by running real FFmpeg 6.1 (the evermeet 6.1 build, Mach-O, not the sandbox's Ubuntu 6.1.1-3 but the same release line) and cross-checked against the Mac's 8.0.1. The big findings are not the ones the context expected:

1. **Movement must use the `perspective` filter, not `crop` and not `zoompan`.** With a source the same size as the canvas (the common case: working copies are canvas-sized) integer `crop` stutters (second difference 2.1 px, because yuv420p snaps crop x to even pixels), `zoompan` stutters (1.9 px), while `perspective ... eval=frame:interpolation=cubic` is smooth (0.05 px before encoding, 0.28 to 0.37 px after x264 crf 20). It is also bit-identical between FFmpeg 6.1 and 8.0.1.
2. **One giant `filter_complex` over all segments does not scale in memory.** FFmpeg's concat filter queues every later segment's decoded frames: 24 one-second segments used 2.5 GB, 6 used 1.0 GB, roughly 93 MB per second of 1080x1920 reel, so a 60 s reel would want about 5.6 GB. Render each segment to its own near-lossless intermediate, then join with the concat *demuxer* and encode once. Peak memory fell to 0.5 GB and total time fell too; the final decoded frames were identical to the single-graph version.
3. **Exact frames and exact samples are achievable and testable:** `-ss <whole frames>/30` pre-seek plus `trim=start_frame/end_frame` plus `atrim=start_sample/end_sample` (1600 samples per frame at 48 kHz and 30 fps, an exact integer) returned exactly the requested frames and zero sample offset on both FFmpeg versions.
4. **Loudness:** `loudnorm` two-pass landed 0.3 LU off (-13.7 for a -14 target). Measuring with `ebur128` (the same meter the tests use) and applying a plain `volume` gain landed on -14.0 LUFS after AAC encoding.
5. **The whole video graph (crop with focus, photo, pan, pull-out, push-in, touch-up, concat) is bit-identical on FFmpeg 6.1 and 8.0.1** once three details are pinned: `scale ... flags=bicubic+accurate_rnd` everywhere, an explicit `setparams=range=tv:colorspace=bt709:...` at the end of each segment, and `-fps_mode passthrough` (with `-framerate 30` on the image input and no `-r`).

**Primary recommendation:** Build `v2r/render/plan.py` as one pure module that `check`, `match` tests and `render` all share; render each segment to a crf-10 ultrafast Matroska piece in a hidden scratch folder, mix and measure the audio as a separate float WAV (sample-exact, music ducked with an `aevalsrc` gain curve, gain from an `ebur128` measurement), then do one final x264/AAC encode from the concat demuxer under `join.fit()`'s bitrate. Add `jsonschema` (MIT) for the schema check and nothing else.

## Architectural Responsibility Map

The project is a CLI toolbox, not a web app, so the tiers are the project's own layers.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Cut-list layout and rules | `schema/cutlist.schema.json` | `v2r/render/check.py` (sentences) | The schema is the single source of field names/ranges; Python only adds meaning the schema cannot (manifest, library, frames) |
| Turning a list into frames, windows, gains | Pure `plan` module (no I/O, no FFmpeg) | — | Shared by check and render so they can never disagree; unit-testable on hand numbers |
| Every edit decision | The cut list (written by the chat's Claude) | — | Renderer makes none (CLAUDE.md "three jobs") |
| Exposure/colour measurement | `v2r/look` (already done; reads `overall`) | `match` reads it | `look` decides nothing; `match` only does arithmetic on its numbers and writes into the list |
| Touch-up numbers | `match` (writes the list) | renderer applies verbatim | Colour decisions live in the list, not in render |
| Picture building | FFmpeg executor in `v2r/render` | `v2r/normalize` provided the working copies | One conversion format in, canvas-sized frames out |
| Sound building and loudness | FFmpeg executor (audio pass) | Python gain arithmetic | Measurement and one `volume` gain; no dynamic processing |
| Size fitting | `v2r/join.fit()` (reused) | render closing sentence | One rule for join and render |
| Proof sheet and cover | `v2r/look/sheets.py` `SheetBook` + `grab_stills` | Pillow | D-26 says reuse look's sheet code |
| Persistence | Work folder files, written whole-or-nothing (`.part` then `os.replace`) | scratch folder deleted at the end | Pattern already used by normalize and look |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FFmpeg / ffprobe (not pip) | 6.1.1 in sandbox; 8.0.1 on the Mac | all picture and sound work | Already the toolbox's engine; every filter used below exists in 6.1 [VERIFIED: ran on ffmpeg 6.1-tessus binary, 2026-10-19] |
| jsonschema | 4.26.0 (MIT) | validate the cut list against `schema/cutlist.schema.json`, reporting *every* error | The reference Python implementation; `iter_errors` returns all errors with `validator`, `absolute_path`, `instance`, `validator_value` [CITED: python-jsonschema.readthedocs.io/en/stable/errors/] [VERIFIED: pypi.org JSON 4.26.0, MIT, first upload 2012-01-02; ran `iter_errors` in a scratch venv] |
| Pillow | 12.3.0 (already installed) | proof sheets, cover still (through look's `SheetBook`) | Already a dependency |

jsonschema pulls in four small pure-or-wheel packages (all MIT): `attrs`, `referencing`, `jsonschema-specifications` and `rpds-py` (a Rust extension; PyPI has `cp313` manylinux x86_64 and aarch64 wheels, so plain pip in the sandbox needs no compiler) [VERIFIED: pypi.org JSON for rpds-py 2026.9.1 file list]. Import jsonschema lazily inside `check` (as Pillow is imported lazily) so doctor, normalize, look and join keep working if the install failed, and make `check`/`render` say so in one sentence.

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 9.1.1 (already) | tests | all new tests |
| (standard library only) | — | `statistics.median` for match, `struct` for the MP4 box walk, `json`, `subprocess`, `array` | no new package needed for these |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| jsonschema | fastjsonschema 2.x (BSD-3, no dependencies) | **Rejected:** it raises on the *first* error only, and the requirement is every problem; it also stops at draft-07 |
| jsonschema | a hand-written validator | **Rejected:** CLAUDE.md says check for a library first; a schema file that nothing validates against is a lie |
| `perspective` for moves | `zoompan` | **Rejected, measured:** jitter 1.9 px per frame on a canvas-sized source; only smooth after upscaling the input 8x (16.6 s vs 3.3 s for 90 frames) |
| `perspective` for moves | integer `crop` expressions | **Rejected, measured:** 2.1 px stutter (crop snaps to even pixels in yuv420p unless `exact=1`, and is whole-pixel even then) |
| ebur128 measure + `volume` | `loudnorm` two-pass | loudnorm landed 0.3 LU off in the measured case and silently switches to dynamic mode when the true peak would pass the ceiling or the loudness range is over its target; acceptable fallback if the planner prefers one filter |
| per-segment pieces | one `filter_complex` with all segments | single graph is simpler to read but memory grows about 93 MB per second of reel |
| intermediate files | raw-frame pipe from per-segment FFmpeg runs into one encoder | no disk use and the same memory bound; harder to debug and not resumable (Stage 23 wants pieces); mention only |

**Installation:**
    uv add jsonschema
    uv export --format requirements-txt --no-dev --no-emit-project --no-hashes -o requirements.txt

**Version verification (this session):**
    pypi.org: jsonschema 4.26.0 (MIT), attrs 26.1.0 (MIT), referencing 0.37.0 (MIT),
              jsonschema-specifications 2025.9.1 (MIT), rpds-py 2026.9.1 (MIT, published 2026-10-04)

## Package Legitimacy Audit

Run with `gsd-tools query package-legitimacy check --ecosystem pypi ...`. The seam cannot read download counts for PyPI, so every package gets `unknown-downloads`, which it rates SUS. The packages themselves are long-established (ages below from PyPI's first upload dates) and share one maintainer organisation, but the protocol says SUS means the planner adds a human check before the install.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| jsonschema | PyPI | 14 yrs (2012-01-02) | not available to the seam | github.com/python-jsonschema/jsonschema | SUS (unknown-downloads only) | Flagged — planner adds checkpoint:human-verify before `uv add` |
| referencing | PyPI | 3.9 yrs (2022-11-21) | not available | github.com/python-jsonschema/referencing | SUS (unknown-downloads only) | Flagged (installs with jsonschema) |
| jsonschema-specifications | PyPI | 3.8 yrs (2022-12-27) | not available | github.com/python-jsonschema/jsonschema-specifications | SUS (unknown-downloads only) | Flagged (installs with jsonschema) |
| rpds-py | PyPI | 3.6 yrs (2023-03-01); latest release 2026-10-04 | not available | github.com/crate-py/rpds | SUS (unknown-downloads, too-new for the latest release) | Flagged; `uv.lock`/`requirements.txt` pin the exact version; compiled wheel, no build step |
| attrs | PyPI | 11 yrs (2015-02-21) | not available | seam found none; project is github.com/python-attrs/attrs | SUS (unknown-downloads, no-repository) | Flagged (installs with jsonschema) |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** jsonschema, referencing, jsonschema-specifications, rpds-py, attrs — one `checkpoint:human-verify` before the single `uv add jsonschema`, which installs all five. No PyPI package has a postinstall step.

jsonschema was named by this phase's brief and confirmed against its official documentation, so the name is not an unverified web-search guess. docs/licenses.md needs one row for jsonschema and a sentence for its four dependencies (all MIT).

## Architecture Patterns

### System Architecture Diagram

    cutlist.json ─┐                      ┌──────────────────────────────────────┐
    (written by   │                      │ check (also run first by render)     │
    Claude)       ├─► parse JSON ──► schema (jsonschema, all errors) ──┐        │
                  │   (reject NaN,                                      ▼        │
    work/         │    duplicate keys)   manifest.json ─► semantic rules ─► sentences:
    manifest.json ┤                      music/library.json ─►            "Problem" / "Note"
    work/look.json┤                      join.fit() (too long?)                   │
    music/*       │                                                              ▼
                  │                         problems? ──yes──► print, exit 1, build NOTHING
                  │                              │ no
                  │                              ▼
                  │            plan(list, manifest) — pure, no I/O
                  │   per segment: start_frame, n_frames, crop rect (integer),
                  │   window start/end (canvas px), touch-up numbers, kept-sound run list
                  │   reel: total frames, music gain curve, cover frame, fitted size/bitrate
                  │                              │
                  │        ┌─────────────────────┼───────────────────────┐
                  │        ▼                     ▼                       ▼
                  │  video pieces (one      audio pass (one FFmpeg   fit: join.fit(shape, seconds)
                  │  FFmpeg per segment)    run, float WAV)          → (w, h, bitrate)
                  │  trim → crop → scale →  atrim kept / silence                 │
                  │  [perspective] →        concat → bed;            measure ebur128 → gain
                  │  [lutyuv] → setparams   music: atrim, afade,                 │
                  │  → piece-NN.mkv         aevalsrc×amultiply, amix            │
                  │        │                     │                              │
                  │        └──► concat demuxer ──┴──► FINAL encode: x264 + AAC, +faststart,
                  │             (list.txt)            maxrate from fit, volume gain, bitexact
                  │                                        │
                  │                                        ▼
                  │                         reel.part.mp4 ─► verify (frames, size, duration, bytes)
                  │                                        │ ok → os.replace → reel-….mp4
                  │                                        ▼
                  │               grab_stills (first/last frame of every segment) → SheetBook
                  │               → proof sheets;  cover still → cover.jpg
                  └─ scratch folder deleted in `finally`; any failure removes the .part file

### Recommended Project Structure
    schema/
    └── cutlist.schema.json        # Draft 2020-12; permissive on unknown keys
    v2r/
    ├── settings.py                # new render/match numbers (list below)
    ├── doctor.py                  # FILTERS grows; add muxer/demuxer lists
    ├── __main__.py                # check, match, render sub-commands
    └── render/
        ├── __init__.py            # render(): check → plan → pieces → audio → final → proof; RenderError
        ├── plan.py                # PURE: frames, geometry, windows, gain curve, fit; used by check AND render
        ├── check.py               # schema errors → sentences; manifest/library rules; notes
        ├── match.py               # median, caps, in-place rewrite of look.touch_up
        ├── video.py               # per-segment FFmpeg command + piece runner
        ├── sound.py               # audio graph, ebur128 measurement, gain
        └── proof.py               # proof sheets (SheetBook with own folder) and cover
    tests/
    ├── test_cutlist_check.py  test_match.py  test_render_plan.py
    ├── test_render_video.py   test_render_sound.py  test_render_golden.py
    └── media.py                   # + helpers (frame-index clip, line clip, centroid, box walker)

### Pattern 1: One pure `plan()` that check and render share
**What:** `plan(cutlist, manifest, library)` returns plain data: for every segment `start_frame`, `n_frames`, `crop` (integer w, h, x, y), `window_start`/`window_end` (canvas-pixel rectangles, equal when there is no move), `touch_up`, `sound`; for the reel `total_frames`, `kept_runs` (merged), `cover_frame`, `fitted (w, h, bitrate)`. No file or FFmpeg access.
**When to use:** always. It is what makes "an invalid list builds nothing" and "the renderer makes no choices" checkable, and it is where the half-open rule and the rounding rule live once.
**Rounding rule to state (D-01):**

    # start frame = nearest frame to `from`; length = nearest whole number of frames to (to - from)
    def frames(seconds, fps=settings.OUTPUT_FPS):
        return math.floor(round(seconds * fps, 6) + 0.5)      # round half up; round(...,6) kills float noise
    start = frames(seg["from"]);  n = frames(seg["to"] - seg["from"])      # 2.5 s -> 75
    # a segment covers frames [start, start + n); it must satisfy start + n <= round(clip_seconds * fps)

Check and render must both use this function so they cannot disagree about "inside the clip". Compare in frames, not seconds (a list copied with `38.63` for a `38.633008` clip would otherwise fail on float equality).

### Pattern 2: Geometry — crop first (integer), move second (sub-pixel)
**What:** for each segment compute the fitted region R in source pixels, crop it once with integer even numbers, scale it to the canvas, then apply the move in canvas coordinates with `perspective`.

    k   = max(CW / SW, CH / SH)              # cover scale; (SW, SH) = working copy size (photo: photo.size)
    Rw, Rh = CW / k, CH / k                  # region of the source that fills the canvas
    crop_w = min(SW, even(Rw)); crop_h = min(SH, even(Rh))
    crop_x = even(clamp(focus_x * SW - crop_w / 2, 0, SW - crop_w))     # 0 when the clip already fills that axis
    crop_y = even(clamp(focus_y * SH - crop_h / 2, 0, SH - crop_h))

Then, in canvas coordinates (w = CW*(1-MOVE), h = CH*(1-MOVE), progress p runs 0→1 linearly over the segment, `p = n/(N-1)` so the first frame is the fitted crop exactly and the last frame is exactly 4 % tighter):

- **push-in:** start = full canvas, end = tight window of size (w, h) centred on the focus point's position inside the crop, clamped to stay inside the canvas. **pull-out:** swapped.
- **pan-right / pan-left:** window (w, h) always; horizontal position runs the whole spare room, 0 → CW·MOVE (pan-right) or CW·MOVE → 0 (pan-left, the window travels left); vertical position is centred on the focus, clamped.

Window corners are linear in the frame number, so each coordinate is `start + (end - start) * in / (N - 1)` and the FFmpeg expression is one multiply-add (verified). "Cropping in by 4 %" means the window is `(1 - MOVE)` of the canvas and the travel is `MOVE` of the canvas, which add to exactly 1: that reading keeps D-19's "travels exactly that far" and "never shows anything outside the picture".

**Crop-share note (D-10):** share kept = `(Rw*Rh) / (SW*SH)` = 0.316 for a 16:9 clip in a 9:16 canvas (exactly the mismatch case) and 0.42 for a 4:3 photo in tall. With a threshold of 0.5 the note fires once per clip (not per segment) for every sideways clip in a tall reel; that is by design in D-10 but the user may want 0.35. Make it `CROP_NOTE_SHARE`.

### Pattern 3: Move filter, verified on FFmpeg 6.1 and 8.0.1
    perspective=x0='<l0>+(<l1-l0>)*in/<N-1>':y0='<t…>':x1='<r…>':y1='<t…>':x2='<l…>':y2='<b…>':x3='<r…>':y3='<b…>':
                sense=source:eval=frame:interpolation=cubic
`sense=source` means "these are source locations that map to the output corners" and `in` is the input frame count (first frame 0). Format numbers with a fixed `f"{v:.6f}"` so the string is deterministic. At p = 0 the filter is the identity, so the first frame of a moving segment equals the same segment without a move.
Measured smoothness (centroid of a 4 px line over 90 frames, canvas-sized 1080x1920 source) [VERIFIED: scratch experiment smooth.py, FFmpeg 6.1]:

| Method | Max second difference (stutter) | Cost for 90 frames |
|--------|---------------------------------|--------------------|
| `perspective` cubic | 0.05 px (0.28 to 0.37 px after x264 crf 20) | 3.3 s |
| `perspective` linear | 0.07 px | 2.5 s |
| `zoompan` | 1.9 px | 1.1 s |
| `zoompan` after 8x upscale | 0.13 px | 16.6 s |
| integer `crop` + scale (pan) | 2.1 px (2.3 after x264) | 0.9 s |
| `scale eval=frame` + `crop` | failed (size changes mid-graph; the output was empty) | — |
`perspective` has a constant sub-pixel bias (up to 0.6 px) versus an ideal continuous model; it is the same on every frame, so it is not visible and must not be "fixed".

### Pattern 4: Per-segment pieces, one final encode
**What:** each segment is its own FFmpeg run into `scratch/piece-NN.mkv` (video only, `libx264 -preset ultrafast -crf 10`, `-fps_mode passthrough`). The final run reads `-f concat -i list.txt` (the list is written by the program, names are `piece-NN.mkv`), adds the audio WAV, scales to the fitted size if `join.fit()` stepped down, and encodes once.
**Measured on a 24-second reel of 24 segments (FFmpeg 6.1, loaded 8-core Mac):** single graph 39 s and 2.5 GB peak; pieces 21 s + final encode 6.8 s and 0.51 GB peak; decoded final frames identical in both. Lossless (`-qp 0`) was the same speed as crf 10 but 2.6x the disk on real footage (82 MB vs 31 MB for 3 s of tone-mapped 1080x1920); ffv1 was 1.6x slower and smaller. PTS after concat were exactly 512 ticks apart at 1/15360 (even 30 fps).
**Recommendation:** crf 10 ultrafast Matroska (`RENDER_PIECE_CRF = 10`), scratch folder `work/.v2r-render-XXXX` removed in `finally`, and a `clear_last_render` pattern for leftovers like look's `.v2r-look-` handling. Doctor needs the `matroska` muxer and `concat` demuxer in new `MUXERS`/`DEMUXERS` lists (names parse the same way as `-encoders`).

### Pattern 5: Exact frames and exact samples from a working copy
    # video piece for a clip segment starting at frame S with N frames (FPS = 30, 1600 samples per frame at 48 kHz)
    pre = max(0, S - 30);  skip = S - pre
    ffmpeg ... -ss <pre/30 to 6 decimals> -t <(skip+N+3)/30> -i A.mp4
      -filter_complex "[0:v]trim=start_frame=<skip>:end_frame=<skip+N>,setpts=N/(30*TB),crop=…,scale=…[v]" ...
    # audio: atrim=start_sample=<skip*1600>:end_sample=<(skip+N)*1600>,asetpts=N/(48000*TB)
Verified on FFmpeg 6.1 and 8.0.1 for S in {0,1,2,3,29,30,31,75,150,223,250} and N in {1,3,10,15,30,45,60}: frames matched a frame-index-coded clip exactly and the decoded 440 Hz sine had zero sample offset. **Do not** use `-ss (S-0.5)/30` or an `-ss` that is not a whole number of frames without `trim`: it duplicates the first frame (verified, 74 mismatches).

### Pattern 6: Sound — a bed, a ducked bed of music, one measured gain
1. **Bed:** per segment, `keep` → `atrim` of the working copy's stereo AAC (always present: normalize adds silence), `off` or a photo → `anullsrc=r=48000:cl=stereo` of exactly `N*1600` samples; `apad=whole_len=N*1600,atrim=end_sample=N*1600` guarantees the length; `concat=n=K:v=0:a=1`.
2. **Music (id `test-tone` until Stage 18):** `sine=frequency=220:sample_rate=48000:duration=…` (filter exists in 6.1) → `atrim=start=music_from:duration=reel` → `afade=in` and `afade=out st=reel-fade_out` (values from the list, else settings).
3. **Drop (music_under_sound):** merge adjacent kept segments into runs in Python, then one gain-curve expression, evaluated per sample, multiplied in with `amultiply`:

        aevalsrc='pow(10,(<DB>*max(clip(min((t-(<a1>-R))/R,((<b1>+R)-t)/R),0,1),clip(min(...2...),0,1)))/20)':s=48000:d=<reel>,aformat=channel_layouts=mono[env]
        [music][env]amultiply[m1];[bed][m1]amix=inputs=2:duration=first:normalize=0[mix]
   `<DB>` is `music_under_sound` (negative); `R` is the ramp setting; the ramps sit *outside* the kept window so every kept second is at the full drop. Values checked at 0, 2.5, 2.65, 2.8, 7.1, 7.2, 7.35, 7.5 s: -12.0, -12.0, -6.0, 0.0, 0.0, 0.0, -6.0, -12.0 dB. `amix` in 6.1 has `normalize` (default true), so `normalize=0` is required or the bed is halved.
4. **Loudness:** write the mix as `pcm_f32le` WAV, then measure with `ebur128=peak=true:metadata=1,ametadata=mode=print:file=-` and read the **last** `lavfi.r128.I` (three decimals) and `lavfi.r128.true_peak` (linear). `gain_db = min(target - I, ceiling - 20*log10(true_peak))`; `I <= settings.SILENCE_LUFS` (-70.000 for digital silence) means no gain. Apply `volume=<gain>dB` in the final encode. Result on the test reel: -14.0 LUFS integrated after AAC, true peak -10.1 dBFS [VERIFIED: ran on 6.1 and 8.0.1]. If the ceiling caps the gain, say so in the closing sentence ("the loudest peak stopped it at -15.2 LUFS").

### Pattern 7: Photo segments
Read `manifest.clips[i].photo.file` (the full-size upright JPEG, `C-photo.jpg`). Chain: `crop=w:h:x:y:exact=1,scale=CW:CH:flags=bicubic+accurate_rnd:out_color_matrix=bt709:out_range=tv,format=yuv420p,setsar=1,loop=loop=N-1:size=1:start=0,setpts=N/(30*TB)` with `-framerate 30 -i photo.jpg`, then the move. The JPEG is decoded and scaled once; a 48 MP photo cost 2.85 s vs 2.34 s for 12 MP for the 90-frame segment including the move. Without `-framerate 30` the image demuxer defaults to 25 fps and the output lost 15 frames on FFmpeg 8.0 (270 vs 285). **Recommendation (beyond D-21's words):** render *every* photo segment from the JPEG, moving or not: a still portrait photo in a tall reel would otherwise be upscaled from the 1080-wide working still. The photo's segment length is still limited by the still clip's `PHOTO_SECONDS = 4` (the manifest's `working.seconds` is what check compares `to` against).

### Pattern 8: Final encode (one command, all verified)
    ffmpeg -hide_banner -loglevel error -nostdin -n  -f concat -safe 0 -i list.txt  -i mix.wav
      -filter_complex "[1:a]volume=<gain>dB,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a]"   # video: add scale=w:h if fit stepped down
      -map 0:v -map "[a]" -fps_mode passthrough
      -c:v libx264 -preset <RENDER_X264_PRESET> -crf 20 -maxrate <bitrate> -bufsize <bitrate> -pix_fmt yuv420p
      -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv
      -c:a aac -b:a 128000 -fflags +bitexact -flags:v +bitexact -flags:a +bitexact -map_metadata -1 -map_chapters -1
      -movflags +faststart  reel.part.mp4
`-fps_mode passthrough` **cannot** be combined with `-r` (FFmpeg errors: "One of -r/-fpsmax was specified together a non-CFR -vsync/-fps_mode") and, unlike `cfr`, never duplicates or drops a frame silently, which is the "renderer makes no choices" guarantee. The result: 30/1, exactly the planned frame count, audio duration = video duration, `ftyp, moov, free, mdat` box order. The silent reel (D-17) gets a stereo `anullsrc` AAC track so every output is video + AAC.

### Pattern 9: The check — jsonschema errors to sentences
Use `Draft202012Validator(schema).iter_errors(data)` and map by `(error.validator, path shape)`:

| validator | Example path | Sentence shape |
|-----------|--------------|----------------|
| `required` | `[]`, `["segments", 3]` | one sentence per *missing name* (compute `[n for n in validator_value if n not in instance]`; the message has only the first): "Segment 4 has no `to`." |
| `type` | `["canvas", "width"]` | "The canvas width must be a whole number." (booleans are rejected as numbers, verified) |
| `enum` | `["segments", 0, "move"]` | "Segment 1's move is "zoom"; it must be one of none, push-in, pull-out, pan-left or pan-right." |
| `minimum` / `maximum` / `exclusiveMinimum` | `focus_x` | "Segment 1's focus_x is 1.5; it must be between 0 and 1." |
| `const` | `["version"]` | "The list's version is 2; this renderer reads version 1." |
| `pattern` | `["segments", 0, "clip"]` | "Segment 1's clip must be a letter such as A." |
| `minItems` | `["segments"]` | "The list has no segments." |

Segment numbers in sentences are 1-based (D-09). Echo any text from the list only through `normalize.clean_text`. Keep the schema free of `oneOf`/`anyOf` (use `"type": ["string", "null"]`) so errors stay one per fault. Unknown keys are noted by comparing each object's keys with the schema's own `properties` (derive the known-field sets from the loaded schema, so the schema stays the single source). Parse the file with `parse_constant` rejecting `NaN`/`Infinity` and an `object_pairs_hook` that reports duplicate keys (Python otherwise keeps the last silently).

### Pattern 10: match
Group = every measured, non-skipped clip in the list's `clips` block (recommend using only letters that appear in a segment so an unused dark clip does not pull the rest; see Open Question 3). `median = statistics.median`. Per clip: `saturation = clamp(median_sat / sat, 0.92, 1.08)`; `brightness = clamp(median_bright - bright, ±8)`; colour offsets applied *after* the saturation multiply, so `blue = clamp(median_blue - saturation * blue_shift, ±4)` and likewise `red`; round to one decimal (offsets) and two decimals (saturation). Write by loading the list, replacing `look.touch_up` and `look.filter` default, and saving whole-or-nothing; keep key order. The renderer's chain per clip:

    lutyuv=y='clip(round(val+(B)),16,235)':u='clip(round(128+(val-128)*S+(U)),16,240)':v='clip(round(128+(val-128)*S+(V)),16,240)'
Explicit `round()` and explicit 16/235/240 limits are required: bare `lutyuv` expressions **truncate** (181.96 became 181 on both versions) and its `minval/maxval` depend on the frame's range tag [VERIFIED: ran on 6.1 and 8.0.1]. Put the colour step after crop/scale/move (fewer pixels when the source is 4K) and before `setparams`.

### Pattern 11: Proof sheet and cover
`grab_stills(finished.mp4, frame_numbers, size, seconds, folder)` already reads many frames in one FFmpeg run, sorted and de-duplicated. Frame numbers: `start_frame_of_segment` and `start + n - 1` for every segment, which are exact because the output is the plan. `SheetBook` hard-codes the folder `sheets` and the names `sheet-NN.jpg` (lines 169 and 211 of sheets.py), which would overwrite look's sheets; add `folder="sheets", stem="sheet"` constructor arguments with those defaults (look's tests only use the defaults), and use `folder="proof", stem="proof"` here. Orientation is the canvas shape (`SHEET_GRID` has "tall" and "wide" keys, 12 per sheet, so 7 segments = 14 stills = 2 sheets as D-26 says). Label text such as `3 in 07.5` and `3 out 09.0` (segment number, then reel time via `pick.clock`). Cover: `grab_stills` for the single frame `segment_start + frames(at)` (clamped inside the segment; absent → frame 0), saved with Pillow at `SHEET_JPEG_QUALITY`-style quality. Note SheetBook counts toward `MAX_SHEETS_PER_RUN = 20`, i.e. up to 120 segments.

### Anti-Patterns to Avoid
- **`zoompan` for moves** (jitter), **`crop` expressions for push-in** (crop's `w`/`h` are evaluated once, only `x`/`y` per frame), **`scale eval=frame`** (broke the graph).
- **`-r 30` or `-fps_mode cfr`** in the final encode: either hides a frame-count error by duplicating frames.
- **One `filter_complex` with every segment** (memory grows with reel length).
- **Anything from the list inside a filter string except numbers formatted by our code.** Letters are looked up in the manifest; the music id is looked up in the library; the working-copy file name is validated as look does (`working_facts`: plain name directly in the work folder) and passed as an `-i` argument.
- **Reordering or "improving"** anything: no auto-trim of a dark frame, no clamping a bad `to` (refuse instead).
- **`loudnorm` dynamic mode** for the final level: it makes processing decisions.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON Schema validation with all errors | own validator | `jsonschema` `iter_errors` | Types, ranges, enums, required, patterns done and tested; only the sentences are ours |
| Median | own sort | `statistics.median` | Stdlib; even counts handled |
| Loudness meter | own BS.1770 | FFmpeg `ebur128` (`peak=true`) | Same meter the tests use |
| Sub-pixel zoom/pan | own resampler / per-frame Python | FFmpeg `perspective` | Measured smooth, identical on 6.1 and 8.0 |
| Contact sheets | new drawing code | `look.sheets.SheetBook` + `grab_stills` | D-26; labels, grid, byte guard exist |
| Size/bitrate fit | new rule | `join.fit()` | D-27; one rule for join and render |
| Whole-or-nothing writes | ad-hoc | `normalize.run_ffmpeg` pattern (`.part` + `os.replace`), `normalize.ffmpeg_timeout`, `clean_text` | Already tested |
| MP4 fast-start check | ffprobe guess | 15-line top-level box walk in tests | Direct proof that `moov` precedes `mdat` |
| Frame hashing | PNG diffs | `ffmpeg -f md5` / `-f framemd5` | Decoded-frame comparison, no extra tools |

**Key insight:** every hard part (resampling, loudness, schema checking, sheet drawing, fitting) already exists in FFmpeg or in this repo. The new code is arithmetic (plan), sentences (check) and FFmpeg argument lists; keep it small and test the arithmetic without FFmpeg.

## Common Pitfalls

### Pitfall 1: Moves that stutter
**What goes wrong:** a push-in or pan on a canvas-sized source judders (alternating 0 and 1 pixel steps).
**Why:** integer `crop`/`zoompan` positions; yuv420p snaps crop x to even pixels.
**How to avoid:** `perspective` as in Pattern 3; test with a thin-line clip and a 0.6 px second-difference bound.
**Warning signs:** a measured second difference above 1 px; a pan that "ticks" at about 15 Hz.

### Pitfall 2: Memory climbs with reel length
**What goes wrong:** the render is killed or swaps in the sandbox at about a minute of 1080x1920.
**Why:** concat queues each later branch's frames.
**How to avoid:** pieces plus the concat demuxer (Pattern 4). Assert in a test that the render never builds a single graph with more than one video input.

### Pitfall 3: A frame too many, a frame too few, or an offset first frame
**What goes wrong:** segments are one frame long or start one frame late; the vsync option hides it.
**Why:** unaligned `-ss`, `-r`/`cfr` duplicating frames, image input defaulting to 25 fps (FFmpeg 8.0 lost 15 frames of a 90-frame photo segment).
**How to avoid:** Pattern 5, `-framerate 30` on the photo input, `-fps_mode passthrough`, and a post-encode self-check that `nb_frames == plan.total_frames` and the frame size is as fitted. A frame-index-coded test clip (luma = 16 + 2*(frame mod 100)) makes this a one-line assertion.

### Pitfall 4: Colour that is "almost" the numbers
**What goes wrong:** the golden test expects Y+6 and gets Y+5 or a colour step on photos.
**Why:** `lutyuv` truncates; range-dependent `minval/maxval`; JPEG photos are full-range 4:4:4 (`yuvj444p`, matrix `bt470bg`) and need `out_color_matrix=bt709:out_range=tv`; swscale's default rounding differs between FFmpeg 6.1 and 8.0 for that conversion (md5s differed until `accurate_rnd` was added).
**How to avoid:** explicit `round()` and limits; `flags=bicubic+accurate_rnd` on every `scale`; `setparams=range=tv:colorspace=bt709:color_primaries=bt709:color_trc=bt709` at the end of every segment chain. With these, the full four-segment video graph (focus crops, a 48 MP and a 12 MP photo, pan, pull-out, push-in, touch-up) produced identical decoded frames on 6.1 and 8.0.1 in tall and wide.

### Pitfall 5: Loudness off by a fraction
**What goes wrong:** the reel says -14 LUFS and measures -13.7.
**Why:** `loudnorm` pass 1 reports -12.10 where `ebur128` says -11.78 for the same file; linear mode inherits the gap.
**How to avoid:** Pattern 6 step 4. The test bound is ±0.3 LU on the finished MP4.

### Pitfall 6: A filter graph with an unmapped output
`-filter_complex` with two labelled outputs and only one `-map` fails ("unconnected output"). Build the video and audio graphs as separate commands (as above).

### Pitfall 7: Huge-factor `scale` is not a pixel probe
A 1080x1920 → 16x16 `scale=…:flags=area` returned 22 for pixels of value 16 to 20. Probe pixels with `crop=2:2:x:y` on the decoded frame, never with a big downscale.

### Pitfall 8: Truncated or misleading time
`ffmpeg -t` after `-ss` plus `trim` end frames keeps decode bounded (`-t` is `(skip+N+3)/30`). The sandbox kills any command at 2 minutes: render runs in the background like normalize/look (the handbook's job); the closing time is about 1.0 s of work per second of reel on the loaded 8-core Mac (not measured on 2 cores; the join measured 2.6 s per second in the sandbox, so expect 2 to 2.6).

### Pitfall 9: Photo segment over 4 seconds
A photo's working copy is `PHOTO_SECONDS = 4`. The checker's "inside the clip" rule refuses a longer photo segment; make the sentence say the photo lasts 4 seconds at most (this is a real limit of the manifest, not a choice).

### Pitfall 10: Concurrency and leftovers
Two renders into the same work folder must not delete each other's scratch; scratch name = `.v2r-render-` + `tempfile` suffix and a clean-up regex like look's `LAST_LOOK_TEMP`; delete only real folders matching that exactly.

## Code Examples

All commands below were run in this session on FFmpeg 6.1 (evermeet build) and, where marked, on 8.0.1 [VERIFIED: scratch runs 2026-10-19]. They are skeletons: numbers are formatted by the program, names come from the manifest.

### Video piece for a clip segment (focus crop + push-in + touch-up)
    ffmpeg -hide_banner -loglevel error -nostdin -y -ss 0.000000 -t 3.700000 -i A.mp4 \
      -filter_complex "[0:v]trim=start_frame=30:end_frame=105,setpts=N/(30*TB),
        crop=1080:1920:0:0:exact=1,scale=1080:1920:flags=bicubic+accurate_rnd,setsar=1,
        perspective=x0='(0.000000+(21.600000)*in/74)':y0='(0.000000+(38.400000)*in/74)':
                    x1='(1080.000000+(-21.600000)*in/74)':y1='(0.000000+(38.400000)*in/74)':
                    x2='(0.000000+(21.600000)*in/74)':y2='(1920.000000+(-38.400000)*in/74)':
                    x3='(1080.000000+(-21.600000)*in/74)':y3='(1920.000000+(-38.400000)*in/74)':
                    sense=source:eval=frame:interpolation=cubic,
        lutyuv=y='clip(round(val+(6)),16,235)':u='clip(round(128+(val-128)*1.0+(0)),16,240)':v='clip(round(128+(val-128)*1.0+(0)),16,240)',
        format=yuv420p,setparams=range=tv:colorspace=bt709:color_primaries=bt709:color_trc=bt709,setpts=N/(30*TB)[v]" \
      -map "[v]" -fps_mode passthrough -c:v libx264 -preset ultrafast -crf 10 -pix_fmt yuv420p piece-00.mkv
(write the filter script to a file or a list element; spaces/newlines above are for reading only.)

### Frame probes for tests (pure Python, no numpy)
    # luma of frame n at a pixel: decode with crop=2:2:x:y and read bytes
    ffmpeg -nostdin -i out.mp4 -vf "select=eq(n\,K),crop=2:2:540:960" -frames:v 1 -pix_fmt yuv420p -f rawvideo -   # d[0]=Y, d[4]=U, d[5]=V
    # decoded-frame hash of the whole video (determinism / golden)
    ffmpeg -nostdin -i out.mp4 -map 0:v -f md5 -
    # loudness and true peak of the finished mix
    ffmpeg -nostdin -i out.mp4 -map 0:a -af ebur128=peak=true -f null - 2>&1 | grep -E "^ +I: |Peak:"
    # fast-start: walk top-level boxes; moov must come before mdat
    pos=0; while pos < len(d): size, typ = struct.unpack(">I4s", d[pos:pos+8]); …    # saw: ftyp, moov, free, mdat

### Check: all errors at once
    from jsonschema import Draft202012Validator          # imported inside check(), not at module top
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: [str(p) for p in e.absolute_path])
    for e in errors:  sentence = SENTENCES[e.validator](e)      # one function per validator in the table above

### Test-frame clip (every frame's luma says which frame it is)
    ffmpeg -f lavfi -i "color=c=black:size=1080x1920:rate=30:duration=10,geq=lum='16+2*mod(N,100)':cb=128:cr=128,format=yuv420p" …
    # frame k decodes to Y = 16 + 2*(k mod 100); keep the stripes flat (no scaling) so mean = value

## State of the Art

| Old approach | Current approach | When changed | Impact |
|--------------|------------------|--------------|--------|
| `zoompan` for Ken Burns | `perspective eval=frame` for sub-pixel; or upscale then zoompan | long-standing | stutter-free without 8x upscaling |
| `loudnorm` single/dual pass | measure with `ebur128`, apply plain gain | project decision | exact target, no dynamic mode |
| `-vsync cfr` | `-fps_mode` (FFmpeg 5.1+; `-vsync` deprecated) | 5.1 | explicit; the existing code already uses `-fps_mode` |
| one concat graph | pieces + concat demuxer | this phase | bounded memory |

**Deprecated/outdated:** `-vsync` (use `-fps_mode`); `jsonschema.__version__` (use `importlib.metadata`); `RefResolver` in jsonschema (replaced by `referencing`; never needed here, all `$ref`s are local `#/$defs`).

## Runtime State Inventory

Not a rename/refactor/migration phase. Omitted. (Greenfield additions; nothing renamed. New files in `work/` follow existing patterns; `work/` is gitignored.)

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The sandbox's Ubuntu FFmpeg 6.1.1-3ubuntu5 behaves like the evermeet 6.1 build for every filter used (all are core libavfilter filters with no external library) | Whole document | A filter or option differs; the first phone test (and doctor listing the new filters) would show it |
| A2 | Render speed on the 2-core sandbox is about 2 to 2.6 s of work per second of reel (extrapolated from the join's 2.6 and the Mac measurements) | Pitfall 8 | Long reels hit the in-command limit; they run in the background anyway |
| A3 | `rpds-py` has a usable wheel for the sandbox's CPU architecture (manylinux x86_64 or aarch64 on cp313) | Standard Stack | `pip install` would try to build Rust and fail; phone test of install |
| A4 | The sandbox pip can reach PyPI for the five jsonschema packages (doctor reports pypi.org reachable) | Standard Stack | install fails; `check` would say so in one sentence |
| A5 | music/library.json will have `id`, a file name and a length in seconds per track (Stage 18 defines it; MUS-01 lists id, length, licence etc. but no file field) | Check | Stage 18 may name fields differently; keep the reader in one small function |
| A6 | A near-lossless crf 10 intermediate is acceptable instead of lossless | Pattern 4 | A very faint extra generation of loss; switch to `-qp 0` (setting) if the user objects; disk use rises 2.6x |
| A7 | -14 LUFS / -1 dBTP is right for the platforms (user decided in D-14; not re-checked) | Pattern 6 | None for this phase; settled |

## Open Questions (RESOLVED)

1. **"At the canvas size" (CUT-07) vs "fits by join's rule" (D-27).**
   - What we know: `join.fit()` steps the frame to 2/3 and 1/2 for reels over about 73 s and 146 s (docs/phone-limits.md).
   - What's unclear: whether a stepped-down frame still satisfies "canvas size".
   - Recommendation: golden tests assert the full canvas for short reels; for long reels `fit()` decides and the closing sentence says the smaller size. Put the sentence in the plan so the user sees it.
   - RESOLVED in plan 01 (render fits with `join.fit`, D-27 wins, and the closing sentence names the smaller size) and plan 09 (the step-down and refusal tests); plan 10 records it in docs/decisions.md and plan 11 asks the user.
2. **Shortest reel and other new settings.** CONTEXT says "a setting" with no number.
   - Recommendation: `MIN_REEL_SECONDS = 3.0`? The user decides; propose 3 s and say so in the plan.
   - RESOLVED in plan 03 (`MIN_REEL_SECONDS = 3` and the other new settings, each with a unit comment) and plan 07 (the length rule); plan 11 asks the user.
3. **Which clips form the match group.**
   - What we know: D-22 says "the group's middle is the median of the clips' values" and D-06 says "one record per clip letter".
   - Recommendation: median over the letters that appear in segments (so a skipped or unused clip never pulls); write a record for every measured letter in `clips` so a later swap still has numbers. Confirm with the user.
   - RESOLVED in plan 08 (the median of the measured clips the segments use; a record for every measured letter in `clips`), as recommended; plan 11 asks the user.
4. **Music level before the drop.** The list has no base gain; the test tone is generated at a fixed level and a real track's loudness is Stage 18's job. Recommendation: no per-track normalisation this phase; the final gain evens the mix; say so in a decisions line.
   - RESOLVED in plan 06 (no track has a level of its own; one measured gain evens the whole mix), recorded by plan 10 in docs/decisions.md.
5. **A photo that gets a still (no move) rendered from the JPEG too.** D-21 only names the move. Recommendation: do both from the JPEG (sharper); the colour matches the still clip because the scale flags are the same as normalize's.
   - RESOLVED in plan 05 (every photo segment, moving or still, is built from the full-size copy), as recommended; plan 11 lists it among the user's choices.
6. **A skipped clip's record in `clips`.** Recommend allowing the letter with `seconds: null` or leaving it out; only a segment that uses it is a problem.
   - RESOLVED in plan 01 (the clips block holds done letters only: a skipped letter in it gets its own sentence, so a skipped letter is left out of the block rather than given `seconds: null`) and plan 07 (its row in the sentence table).
7. **Where cut lists live.** Default `work/cutlist.json` per CONTEXT; the three commands take an optional path and `--work` (default `work/`).
   - RESOLVED in plan 01 (`check` and `render` take an optional cut-list path, default WORK/cutlist.json, and `--work`) and plan 08 (`match` takes the same).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| FFmpeg 8.0.1 / ffprobe (Mac) | development, tests | yes | 8.0.1-tessus | — |
| FFmpeg 6.1 (evermeet build, scratch only) | verifying 6.1 behaviour | yes | 6.1-tessus (Mach-O, downloaded into the session scratchpad only; not part of the repo) | the phone test |
| uv / Python 3.13 | tests | yes | uv 0.12.7, 3.13.15 | — |
| numpy | — | no | — | not needed; probes use pure Python |
| Docker | exact sandbox image | no | — | the first phone test is the sandbox check |
| PyPI (for jsonschema) | install | yes (reached from the Mac this session) | — | — |
| The sandbox (Ubuntu FFmpeg 6.1.1) | final check of every claim here | not reachable now | — | phone test on branch `stage-16-render`; add the new filters to doctor first |

**Missing dependencies with no fallback:** none for planning. **Phone test is mandatory** before merging: doctor must list the new filters, then a reel.

New filters/encoders/muxers for doctor (the render uses all of them): `trim`, `atrim`, `perspective`, `lutyuv`, `setparams`, `concat` (demuxer, not filter), `afade`, `amix`, `amultiply`, `aevalsrc`, `sine`, `volume`, `aformat`, `ebur128`/`ametadata` (already), plus muxer `matroska`. Existing list already has `crop, scale, format, fps, setsar, setpts, loop, aresample, apad, anullsrc, loudnorm`. `asetpts` is needed too. `loudnorm` can stay (SKEL-01 lists it).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 via uv (`[tool.pytest.ini_options] testpaths = ["tests"]` in pyproject.toml) |
| Config file | pyproject.toml (no change) |
| Quick run command | `uv run pytest tests/test_render_plan.py tests/test_cutlist_check.py tests/test_match.py -x -q` (no FFmpeg, a few seconds) |
| Full suite command | `uv run pytest -q` (about 7 minutes today; macOS has no `timeout`, use `gsd-tools run-with-timeout 600 -- uv run pytest -q`) |

Every video test generates its own clips with FFmpeg into `tmp_path` (extend `tests/media.py`) and is parametrised over both shapes. No test reads `work/` or `fixtures/`. Pure functions are tested on hand-made numbers with no FFmpeg.

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CUT-01 | schema file loads, `check_schema` passes; a minimal valid list passes; both example lists (tall 20 s, wide 38 s) pass | unit | `uv run pytest tests/test_cutlist_check.py -k schema -x -q` | ❌ Wave 0 |
| CUT-02 | each fault gives exactly one sentence (table-driven: wrong version, canvas vs manifest shape, clip letter/file/length mismatch, skipped letter used, `from>=to`, past clip end, focus out of range, bad move, bad sound, music too short with the 14.0/20.0 wording, touch-up over cap, reel too short, bad cover, too long to fit, NaN, duplicate key); several faults give several sentences; notes (photo no move, no touch-up, silent reel, crop share, accepted-not-built, unknown fields) do not fail | unit | `uv run pytest tests/test_cutlist_check.py -x -q` | ❌ Wave 0 |
| CUT-03 | plan arithmetic: 2.5 s → 75 frames; half-frame ties; start+n inside clip; crop/clamp/focus on both shapes and for clips that already fill an axis; invalid list builds nothing (output folder unchanged, no scratch left) | unit + integration | `uv run pytest tests/test_render_plan.py tests/test_render_video.py -x -q` | ❌ Wave 0 |
| CUT-04 | window corners linear in the frame number; first frame equals the unmoved crop; pan direction; amount equals `MOVE_AMOUNT`; measured smoothness on a thin-line clip: max second difference of the line's centroid ≤ 0.6 px, total travel within 1.5 px of the plan, pan-left moves features rightwards; photo move rendered from `photo.file` (change the still clip's colour and prove the output does not change) | unit + integration | `uv run pytest tests/test_render_video.py -k "move or photo" -x -q` | ❌ Wave 0 |
| CUT-05 | median/caps arithmetic on hand numbers incl. even count, one outlier, caps hit, `None` values, rewrite replaces old records; rendered colour at a known frame equals source + exact offsets within ±1 code value (flat-colour clips) and the touch-up block absent means source unchanged | unit + integration | `uv run pytest tests/test_match.py tests/test_render_video.py -k "touch or match" -x -q` | ❌ Wave 0 |
| CUT-06 | `keep` vs `off` (beep present/absent in the right segments by `volumedetect` over a window); music absent when `null`; envelope values at fixed times (-12, ramp midpoint -6, 0); fade in/out; finished integrated loudness within 0.3 LU of target; true peak ≤ ceiling; silent reel has an AAC track at digital silence | integration | `uv run pytest tests/test_render_sound.py -x -q` | ❌ Wave 0 |
| CUT-07 | codec h264/aac, `pix_fmt yuv420p`, size equals canvas (full size for short reels), `r_frame_rate 30/1`, box order `ftyp, moov` before `mdat`, bytes ≤ `MAX_RESULT_BYTES`, long reel steps down and says so in one sentence, proof sheet count = ceil(2·segments/12), cover exists and is canvas-sized, no `.part` or scratch left, a failing ffmpeg leaves nothing | integration | `uv run pytest tests/test_render_golden.py -x -q` | ❌ Wave 0 |
| CUT-08 | speed, transition, text, voice present → notes only, same video as without them | unit + integration | `uv run pytest tests/test_cutlist_check.py -k accepted -x -q` | ❌ Wave 0 |
| CUT-09 | golden tall and wide renders (below) | integration | `uv run pytest tests/test_render_golden.py -x -q` | ❌ Wave 0 |

### Golden renders: how to make them deterministic and compare them
- **Inputs:** generated, never committed: (a) a *frame-index clip* (flat grey whose luma is `16 + 2*(frame mod 100)`), (b) *flat colour clips* (one distinct colour each, with a beep at known seconds), (c) a *split clip* (left half red, right half blue, sized like a sideways working copy: 3412x1920 in a tall job) so focus is provable by colour, (d) a *thin-line clip* for movement, (e) a photo made by Pillow (`tests/media.make_photo`) with a distinct left/middle/right colour band and a stand-in still clip of a *different* colour, written to a fake work folder with `tests/media.make_manifest` (extend it with the `photo.file` copy). The tall example (7 segments, 4 clips + photo, kept sound on one laugh, pan, push-in on the photo, music -12 dB under the laugh, cover from the laugh) and the wide example (38 s talking head, two cut-aways, upright cut-away cropped by `focus_y`, pull-out on a photo, music -20 dB) from CONTEXT go in as JSON, with durations cut to about one quarter for the render tests (full-length versions run through `check` and `plan` only), so each render takes seconds. Set `settings.X264_*`/preset to `ultrafast` for the test run by monkeypatch.
- **Pinned settings in tests:** same thread count both runs (default is fine on one machine); `-fflags +bitexact`.
- **What is asserted (never file bytes across machines):**
  1. `nb_frames == plan.total_frames` and `float(format.duration)` within 0.05 s of `total_frames/30`; audio duration within 0.05 s of video.
  2. Canvas size equals `settings.SHAPES[shape]`; `r_frame_rate == "30/1"`; `bytes ≤ MAX_RESULT_BYTES`.
  3. At the midpoint frame of every segment, mean (Y, U, V) of a 40x40 patch equals the expected colour *computed independently in the test* (source colour + touch-up offsets, or the focus-selected half of the split clip) within ±2 code values. This proves every segment is present, in order, cropped around its focus and touched up with exactly the list's numbers.
  4. First and last frame of every segment decode to the frame-index clip's expected luma (±2), proving exact start frame and length.
  5. **Same list, same video:** render twice into two folders and compare `ffmpeg -f md5` of the decoded video of both (equal in all my runs on one machine with the same thread count; byte-identical files in two of three runs). Also assert `plan()` and the built command lists are equal as data across two calls (this holds across machines).
  6. Cross-version: do not hard-code md5s. Expected colours and frame luma are the cross-machine contract; the project's own 6.1/8.0 comparison is a one-off scratch result (identical decoded frames) recorded in the decisions line.
- **Loudness:** `ebur128` integrated within ±0.3 LU of the stated target (measured -14.0 after AAC); true peak ≤ ceiling; silence case: `I == -70.000` and no gain applied.
- **Movement:** line-centroid tracker (pure Python, middle row via `crop=W:1:0:H/2`, brightness-weighted centroid of ±14 px around the expected position). Failure thresholds: stutter (max |second difference|) > 0.6 px fails; known-bad methods measure 1.9 to 2.3 px, `perspective` 0.28 to 0.37 px after crf 20.
- **Schema errors:** a table of `(bad list fragment, expected sentence)`; assert the *number* of sentences equals the number of injected faults and each contains the 1-based segment number and the offending value; assert nothing is built (output folder unchanged) on any problem.
- **Fast-start:** top-level box walk (`moov` offset < `mdat` offset).
- **Size limit:** a reel just over `FIT_STEPS[0]`'s length asserts the smaller frame and the stepped-down sentence; one over the last step's length asserts the refusal sentence and an empty output folder (same pattern as `tests/test_join.py`).
- **Leftovers:** after success and after an injected FFmpeg failure (monkeypatch `subprocess.run` to raise on the Nth piece), `os.listdir(work)` shows only the expected files.

### Sampling Rate
- **Per task commit:** the task's own test file (`-k` filter).
- **Per wave merge:** the quick run command above plus the render tests touched.
- **Phase gate:** full suite green, then the manual phone checks (below) before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `schema/cutlist.schema.json` and `tests/test_cutlist_check.py`
- [ ] `tests/test_render_plan.py`, `tests/test_match.py`
- [ ] `tests/test_render_video.py`, `tests/test_render_sound.py`, `tests/test_render_golden.py`
- [ ] `tests/media.py`: frame-index clip, split clip, thin-line clip, `make_manifest` support for a photo's full-size copy, centroid tracker, box walker, loudness reader
- [ ] `uv add jsonschema` (after the human check) and regenerated `requirements.txt`
- [ ] `v2r/doctor.py`: new filters, `matroska` muxer, `concat` demuxer, with `tests/test_doctor.py` additions in the file's existing style

### Manual checks (cannot be automated; say exactly what to look or hear)
1. Phone: doctor lists every new filter; `check` then `render` of a cut list pasted as text on branch `stage-16-render`.
2. Watch the push-in on a photo: at about 1 s and 3 s the picture should be slightly tighter, with no tick or shimmer; noticed only when looked for.
3. Compare with and without the touch-up: clips should look like one shoot; if the change reads as an effect, halve the cap and run `match` again.
4. Listen for the music dropping under the kept laugh within about a third of a second before it starts and returning just after; levels the same from reel to reel.
5. Proof sheet: first and last frames of each shot, no black frame, no crop onto a shoulder; cover is the shot she chose.

## Security Domain

Applicable (`security_enforcement` is on; ASVS level 1). The cut list is untrusted text written by an LLM that has read user files and file names; the manifest and look.json are data produced by this program from user files.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | no accounts |
| V3 Session Management | no | none |
| V4 Access Control | partly | file reads limited to the work folder (plain names, as `look.working_facts`), `music/` entries named by the library, and the cut list path given on the command line; outputs only into the work folder |
| V5 Input Validation | yes | jsonschema for structure and ranges; Python for meaning; reject NaN/Infinity and duplicate keys; limit file size (`MAX_CUTLIST_BYTES`) and segment count (`MAX_SEGMENTS`); numbers only in filter strings |
| V6 Cryptography | no | none |
| V7 Error handling / logging | yes | sentences echo list text only through `clean_text`; FFmpeg's own error text stays in a bounded `detail` as normalize does |
| V12 Files | yes | `.part` then `os.replace`; scratch folder with a fixed prefix; never write over an original; output names built from a fixed pattern and a timestamp |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Filter-graph injection through a string in the list (a `why`, a track id, a clip name containing `,`/`[`/`;`/`'`) | Tampering | Only integers and floats formatted by our code enter a filter; letters match `[A-Z]{1,3}` and are looked up; the music id must equal a library id; working file names validated as plain names; `-i` takes paths as separate arguments with no shell |
| Path traversal (`../..` in a track file or `working.file`) | Tampering / Information disclosure | resolve and require `parent == work folder` (or `music/`); refuse otherwise |
| Resource exhaustion (1e9-second segments, thousands of segments, giant JSON) | Denial of service | segment bound, file-size bound, `to` limited to the clip, `fit()` refuses overlong reels before anything is built, per-command timeouts from `normalize.ffmpeg_timeout` |
| Leaking device/location metadata into a posted reel | Information disclosure | `-map_metadata -1 -map_chapters -1`, `+bitexact` (no encoder strings); working copies already carry none |
| Half-written outputs mistaken for finished ones | Repudiation / Tampering | `.part` names, post-encode self-check, delete on any failure |
| Prompt-injection text in `why` or file names steering the chat | Elevation | printed only after `clean_text`; EDITOR.md already says to treat names as data (the user's file) |

## Sources

### Primary (HIGH confidence)
- Local runs on FFmpeg 6.1-tessus and 8.0.1-tessus, 2026-10-19 (scratch experiments in the session scratchpad: `smooth.py`, `seek2.py`, `proto.py`, `pieces.py`): move smoothness, exact seeking, cross-version equality, loudness, memory, timing.
- Repo files read this session: v2r/settings.py, v2r/join.py, v2r/normalize.py, v2r/look/__init__.py, v2r/look/sheets.py, v2r/look/measure.py (docstring and `overall_of`), v2r/doctor.py, v2r/__main__.py, tests/media.py, tests/test_join.py, tests/test_doctor.py, docs/phone-limits.md, docs/decisions.md, docs/licenses.md, EDITOR.md, README.md, pyproject.toml, requirements.txt, the real manifest.json and look.json in work/ (read only, key names).
- python-jsonschema.readthedocs.io/en/stable/errors/ (ValidationError attributes, `iter_errors`, `best_match`).
- pypi.org JSON for jsonschema, rpds-py, referencing, jsonschema-specifications, attrs (versions, licences, wheels, first upload dates).

### Secondary (MEDIUM confidence)
- docs/field-guide.html Stage 16 section (the guide's intent; newer decisions win).
- `gsd-tools query package-legitimacy check` (all SUS for lack of a downloads figure).

### Tertiary (LOW confidence)
- Sandbox timing extrapolation from the join's measured 2.6 s per second (docs/phone-limits.md) — not measured for render.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — one new library, confirmed against its docs and registry; everything else is FFmpeg already in use.
- Architecture: HIGH — pieces vs single graph, perspective vs crop/zoompan, loudness method and exact seeking were each tested head to head.
- Pitfalls: HIGH — each was hit and reproduced during the experiments.
- Sandbox performance and install of `rpds-py`: MEDIUM — Mac only; phone test decides.

**Research date:** 2026-10-19
**Valid until:** 2026-11-18 (FFmpeg and jsonschema are stable; the sandbox's FFmpeg may change under the project)
