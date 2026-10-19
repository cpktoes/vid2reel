# Phase 4: Stage 16 – Cut list and renderer - Context

**Gathered:** 2026-10-19 (pre-discussion in the Stage 15 session; the discuss step finishes it)
**Status:** Draft — the cut-list design below is settled; the "Open for the discuss step" list is not

<domain>
## Phase Boundary

Three commands and a rulebook. `schema/cutlist.schema.json` describes a cut list. `python -m v2r check` validates a cut list against the schema and against work/manifest.json and prints every problem as one plain-English sentence. `python -m v2r match` reads each clip's exposure and colour balance from work/look.json and writes a mild, capped per-clip correction into the cut list. `python -m v2r render` builds the video from the cut list and the working copies alone: straight cuts, every segment filling the canvas cropped around its focus point, the optional slow move, the touch-up numbers applied and nothing else to colour, each segment's own sound kept or off, music underneath from its start point with fades, the mix evened to a stated loudness, an H.264/AAC fast-start MP4 at the canvas size under MAX_RESULT_BYTES, plus a proof sheet and a cover still. The renderer makes no choices: a valid list is built exactly, an invalid one builds nothing. Golden renders in both shapes.

Not in this phase: filters other than "none" (Stage 21), text (Stage 21), beat matching (Stage 22), the music library itself and ducking (Stage 18), speech cuts, captions and the voice track (Stages 24, 25), the handbook's choosing rules (Stage 17). EDITOR.md lines are proposed as text only; the user writes EDITOR.md.

</domain>

<decisions>
## Implementation Decisions

### The cut-list design (settled by the user on 2026-10-19 from the guide's Stage 05 prompt)
- **D-01:** One JSON file per edit, written by the chat's Claude, checked by `check`, built by `render`. Every time is seconds on a working copy, never a frame number; the working copies keep the originals' timing (Stage 14 never trims, retimes or speeds a clip), so a list means the same thing on the Mac and the phone. — **Reversibility:** one-way — every logged cut list depends on it.
- **D-02:** `version`: 1. A later change to the layout gets a new number and old lists still render.
- **D-03:** `canvas`: `width`, `height`, `fps`. Only the two shapes are allowed (1080×1920 or 1920×1080 at OUTPUT_FPS), and the canvas must match the shape the manifest was normalized for, because working copies are sized per job shape and nothing is ever enlarged. "Render the same list wide" means normalize wide first; the checker says so in one sentence. — **Reversibility:** costly — the handbook's "wide version" follow-up (Stage 19) is built on it.
- **D-04:** `segments`, in order, each with `clip` (letter), `from`, `to`, `focus_x` and `focus_y` (0 to 1, default 0.5; the vertical point is for a wide canvas, where an upright clip is cropped top and bottom — the user chose to add it now), `move` ("none", "push-in", "pull-out", "pan-left", "pan-right"; the amount is one capped number in settings.py, not a knob in the list), `sound` ("keep" or "off") and `why` (a sentence citing still labels). The reel's length is the sum of the segments and nothing else.
- **D-05:** `look`: `filter` (always "none" until Stage 21; accepted, only "none" built) and `touch_up`, one record per clip letter written by `match` from look.json's `overall` (brightness, blue_shift, red_shift, saturation): a brightness offset in 8-bit code values, a blue offset and a red offset in the same units, and a saturation factor, each capped in settings.py. The renderer applies exactly those numbers and nothing else to colour. — **Reversibility:** costly — the units are fixed once reels are logged with them.
- **D-06:** `sound`: `music` (a track id, or null; a generated test tone stands in until Stage 18), `music_from` (seconds into the track), `fade_in` and `fade_out` (seconds), `music_under_speech` (dB the music drops to under a kept segment's sound; used from Stage 18, accepted now) and `loudness` (the target in LUFS the whole mix is evened to, stated in the list so it is never a hidden choice).
- **D-07:** Accepted and ignored with a note (CUT-08): per-segment `speed` and `transition`, `text` entries (per segment or top level) and a top-level `voice` track. The checker reports "accepted but not built yet", never fails on them. Unknown fields are noted, not fatal.
- **D-08:** `cover`: an optional time on the finished reel for the cover still; default the first frame (the discuss step may change the default).
- **D-09:** The checker's sentences, one each: the clip exists in the manifest and was converted; `from` is before `to` and both sit inside the clip's length; focus points are between 0 and 1; the move is one of the five names; the canvas is one of the two shapes and matches the manifest's shape; the music track exists; every touch-up number is within its cap; the total length is at least the shortest reel allowed (a setting); segment sound is "keep" or "off".
- **D-10:** Golden renders: fixed cut lists in both shapes over generated clips, checked for length to the frame, size under the limit, the right colour at a known second, every segment present, and the same list giving the same video twice — compared by what the frames show (decoded frame hashes or measured values), not file bytes, since encoders are not byte-identical between runs.

### Steers from the user (2026-10-19)
- **D-11:** Naming the subject in the message steers the reel: what the user types outranks everything, and the chat's Claude uses it to pick moments and set focus points. Stage 19 makes it the first two brief questions; nothing in this phase needs to change for it.
- **D-12:** Attach order only names clips (A, B, C). The cut list orders shots freely by craft (Stage 17's rules); the manifest's `shot_at` gives the real chronology when "in the order they happened" is asked for. Nothing ties a reel to attach order.

### Open for the discuss step
- The loudness target: the common short-form figure is about -14 LUFS (check the current platform guidance and state the figure used, per the Stage 16 prompt).
- How far a push-in or pan may go: a few percent over the segment (the cap in settings.py).
- Whether a photo's move is on by default when the list says "none" (the guide: a photo gets one by default; the renderer must not choose, so the default belongs in the handbook or the checker's wording, not in render).
- What the cover still defaults to (first frame, or the midpoint of the first segment).
- How `match` finds the group's middle: a plain median, so one odd clip does not pull the rest.
- Whether the proof sheet reuses the look step's sheet code as it is (one orientation per sheet, 12 cells) or a smaller one-sheet layout.

### Claude's Discretion
- The exact FFmpeg filter chains (trim/setpts, crop with focus, the move via zoompan or crop expressions, eq/colorbalance for the touch-up, concat, afade/amix/loudnorm), as long as they exist in FFmpeg 6.1 and doctor lists them.
- The JSON Schema's structure and error-to-sentence mapping; the file names of the output, proof sheet and cover still; how the fit step reuses join's FIT_STEPS; the test-tone recipe.

</decisions>

<the_plan_given_on_2026-10-19>
## The plain-English plan already given (the guide's Stage 16 prompt was answered in the Stage 15 session)

Three commands and a rulebook (see the domain). For each segment: trim to its seconds, crop to the canvas around the focus point, apply the optional move, apply the touch-up numbers; join with straight cuts; sound per segment or silence, music underneath from its start with fades, the mix evened to the stated loudness; MP4 fitted under the send limit by the join's length-to-quality rule, saying so when quality was stepped down; proof sheet with the look step's sheet code; cover still from the list's time or the first frame. The renderer refuses to choose: an invalid list builds nothing; nothing is trimmed, nudged or reordered; text, speed, transitions and voice are noted, not built; a tall canvas has one mode, crop to fill. Tests: the golden renders in both shapes; the checker's sentences; caps on the touch-up; a photo's push-in from the full-resolution copy; both shapes throughout. Time: about 2.6 s of work per second of video at full size on the phone (docs/phone-limits.md), so a 20 s reel is under a minute and longer ones run in the background as normalize and look do; doctor grows to list the filters render uses.

**Trickiest part:** the gentle movement — a push-in or pan that is slow and perfectly smooth, rendered from a 48-megapixel photo or a 4K working copy, identical on FFmpeg 6.1 and 8.0, inside the sandbox's time; a stutter in a slow move is a fault only the user's eye on a phone can judge. Second: proving the same list makes the same video, since encoders are not byte-identical between runs.

</the_plan_given_on_2026-10-19>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The stage and its rules
- `docs/field-guide.html` — read only Stage 16 (between the `id="s16"` and `id="s17"` markers); never edit it. Its example cut list, "What this stage must do" list, the settled Decide box (crop to fill), the Do-this steps and the Watch out (a renderer that tries to help is the bug).
- `CLAUDE.md` and `.claude/CLAUDE.md` — three jobs that never mix (render builds exactly the list), settings.py holds every number, public repo, plain-English explanations, decisions in docs/decisions.md.
- `docs/decisions.md` — add lines for anything here that differs from the guide (the vertical focus point; the canvas tied to the manifest's shape).
- `.planning/REQUIREMENTS.md` §Cut list and renderer (Stage 16) — CUT-01 to CUT-09.
- `.planning/ROADMAP.md` §Phase 4 — goal and success criteria.
- `.planning/phases/03-stage-15-seeing-the-footage/03-CONTEXT.md` and `v2r/look/__init__.py` (docstring) — look.json's frozen names (`overall`, `stills` labels, `candidates`), which `match` reads and `why` cites.

### The sandbox and its limits
- `docs/phone-limits.md` — FFmpeg 6.1, two processors, the 2-minute command limit, 30 MiB back, the measured work per second of video, tests 1 to 14.

### Existing code to follow
- `v2r/join.py` — the fit step (FIT_STEPS, FIT_HEADROOM, MAX_RESULT_BYTES), the crop-to-fill, the house FFmpeg pattern, fast-start.
- `v2r/normalize.py` — the manifest's frozen names and the whole-or-nothing write; `run_ffmpeg()` and `ffmpeg_timeout()`.
- `v2r/look/sheets.py` — the sheet drawing to reuse for the proof sheet; `v2r/look/__init__.py` — the run shape (one line per clip, background by the handbook).
- `v2r/settings.py` — every number with a unit comment; the `# look:` block's style.
- `v2r/doctor.py` — `FILTERS`; grow for concat, trim, atrim, afade, amix, loudnorm, zoompan or whatever render uses.
- `tests/media.py`, `tests/test_join.py`, `tests/test_look*.py` — generated clips, both shapes, `probe()`.
- `EDITOR.md` — the user's handbook; propose the check/match/render steps as text only.

</canonical_refs>

<code_context>
## Existing Code Insights
- The join already fits a video under MAX_RESULT_BYTES by length (FIT_STEPS), crops to fill from the centre, and writes fast-start MP4: render generalises it with focus points, per-segment trims, moves, colour and sound.
- look.json's `overall` block gives `brightness`, `brightness_low`, `brightness_high`, `blue_shift`, `red_shift`, `saturation` per clip, measured on signalstats averages against neutral grey (128): `match` works from these.
- Stills are labelled "B 07.5"; `why` cites those labels; the proof sheet can reuse `SheetBook`.
- Phase 3's run quirks apply: sequential executors on the branch, `--force-isolation none`, macOS has no `timeout` (use gsd-tools run-with-timeout), the full suite is about 7 minutes, never run commands against work/ or fixtures/ from the repo root.

</code_context>

<specifics>
## Specific Ideas
- The guide's Do-this: a reel by hand from one fixture set, watched on a phone with sound; the same reel with and without the touch-up; a photo with a slow push-in that is noticed only when looked for; a segment past a clip's end gives a sentence and no video; "make the second shot one second shorter" changes one number and one shot; the same list rendered wide after normalizing wide; the phone test on branch stage-16-render with the cut list pasted as text.
- Every change explained in plain English with what to look at and at what second.

</specifics>

<deferred>
## Deferred Ideas
- Ducking under speech and the real music library — Stage 18. Named filters and text — Stage 21. Beat alignment — Stage 22. Resumable renders in pieces and the Mac's no-limit mode — Stage 23. Speech cuts, captions, voice — Stages 24 and 25.
- Listing excluded candidate stretches as facts (IN-02's optional idea) — if the reel log shows Claude needs it.

</deferred>

---

*Phase: 04-stage-16-cut-list-and-renderer*
*Context gathered: 2026-10-19 (draft)*
