---
phase: 04-stage-16-cut-list-and-renderer
plan: "06"
subsystem: render
tags: [render, sound, music, loudness, ebur128, drop, fades]
requires: ["04-01", "04-03", "04-04"]
provides:
  - "sound.sound_settings(), kept_runs(), gain_at(), drop_expression(), gain_for(), read_library(), track(), LibraryError, MUSIC_DIR (names and sentences fixed for plan 07's check)"
  - "sound.mix_command() with a music branch: music from music_from to the sample, fades, the drop under kept sound, amix with normalize=0"
  - "sound.measure_loudness(mix_path, folder, seconds): integrated loudness and true peak from ebur128, read from loud.txt in the scratch folder"
  - "render() measures the mix, applies one plain gain in the final encode, and states the loudness figure"
affects: [04-07, 04-08, 04-09, 04-10, 04-11]
actuals:
  tokens: 9100
  tasks: 2
  commits: 3
tech-stack:
  added: []
  patterns:
    - "The drop is one aevalsrc gain curve evaluated per sample and multiplied into the music; a pure Python twin (gain_at) is the reference the tests compare it with"
    - "Loudness is measured once with ebur128 and applied as one fixed gain; no compression, no limiter, no normaliser that changes its own level"
key-files:
  created:
    - tests/test_render_sound.py
  modified:
    - v2r/render/sound.py
    - v2r/render/__init__.py
key-decisions:
  - "The loudness is one measured gain (ebur128, then volume), never loudnorm; the figure printed is the measured loudness plus the gain actually applied"
  - "The test tone is 220 Hz for 300 seconds with the id test-tone; any other music id comes from music/library.json shaped {tracks: [{id, file, seconds}]}"
  - "A fade longer than the reel covers the whole reel; no track gets a level of its own before the one final gain"
requirements-completed: [CUT-06, CUT-07]
duration: "about 45 min (full suite 10 min 31 s)"
completed: 2026-10-19
status: complete
---

# Phase 4 Plan 06: The Reel's Sound Summary

Each shot's own sound is kept or off exactly as the list says, a music track runs underneath from its start point with fades, drops 12 dB (or whatever the list says) under every kept stretch, and the whole mix is measured and evened to -14 LUFS with one plain gain, with render stating the figure it used.

## What changed, in plain English

- A shot whose sound is `keep` carries its own sound for exactly its length, and a shot whose sound is `off` is digital silence of the same length. A reel with no music and every shot off still has a (silent) stereo sound track, so it plays everywhere.
- A list can name a music track. Until the music library arrives in Stage 18 the only track is `test-tone`, a plain low hum (220 Hz). It plays under the whole reel starting `music_from` seconds into the track, fades in over half a second and out over the last 1.5 seconds unless the list says otherwise. Any other name is looked up in `music/library.json` (which does not exist yet), and a track that is missing or unnamed is refused with one sentence and nothing is built.
- When the list says `music_under_sound`, the music sits that many decibels lower for the whole of every shot whose own sound is kept. It reaches the lower level 0.3 seconds before the kept shot starts and comes back over 0.3 seconds after it ends, so every second of the shot itself is at the full drop. Two kept shots side by side are one drop with no rise at the cut between them.
- Finally the whole mix is measured and turned up or down by one fixed amount to the list's loudness, or -14 LUFS when it states none. It is never turned up so far that the loudest peak would pass -1 dBTP. Nothing squashes or limits the sound, and nothing changes the level over time apart from the music drop the list asked for.
- Render's closing sentence now says what it did: `Made reel-tall-....mp4: 0.1 MiB, 360x640, 4.0 seconds, sound evened to -14.0 LUFS.` If the peak ceiling stopped it short, it says so and gives the real figure: `..., sound evened to -9.8 LUFS, short of the 0 LUFS target because the loudest peak would have gone past -1 dBTP.` A reel with no sound at all says `..., with no sound to even.`
- Nothing was heard on a phone. A reel with music and a kept laugh must be made from a phone on this branch before the stage merges.

## Measured on the finished reel (Mac, x264 ultrafast, 360x640 and 640x360 test canvases, the test tone, AAC after the final encode)

List: off 0.0 to 1.5, keep 1.5 to 3.0 (the clip's own sound is silent there so only the music is heard), off 3.0 to 4.5; test-tone, no fades, `music_under_sound` -12.

| Shape | Drop under the kept shot | Ramp midpoint (limit 6 dB, within 1) | Level back after (limit 0.5) | Integrated loudness, mixed reel (limit 0.3 LU) |
|-------|--------------------------|--------------------------------------|------------------------------|-----------------------------------------------|
| tall  | 12.0 dB | 5.8 dB | 0.0 dB | -14.0 LUFS (true peak -13.1 dBFS) |
| wide  | 12.0 dB | 5.8 dB | 0.0 dB | -14.0 LUFS (true peak -13.1 dBFS) |

Also checked in both shapes: kept then off over a beeping clip (kept window above -20 dB, off window below -60 dB); two adjacent kept shots hold the drop across their cut within 0.5 dB; fades (first and last 0.1 s more than 15 dB down, the middle of the fade out 6 dB down within 1); loudness -16 gives -16.0 within 0.3; a loud kept beep with loudness 0 is stopped by the ceiling, the sentence says `short of the 0 LUFS target`, the figure it gives matches what the reel measures within 0.3 LU and the reel's true peak is at most -0.5 dBTP; a silent reel has one stereo AAC track and a loudest moment at or below -90 dB; a library track (silent until 8 s in, then a tone) with `music_from` 5.0 is heard 3 seconds into the reel; the aevalsrc drop matches its Python reference within 0.05 dB at ten times; every filter in the mix command is in RENDER_FILTERS.

## What to listen for on the phone

Make a reel from the phone with this list: three shots of 1.5 seconds or more, the middle one with its own sound kept (someone laughing or talking), the first and last off, music `test-tone`, `music_under_sound` -12.

- **0:00 to 0:00.5:** a low steady hum fades in from nothing over the first half second. It should not start with a click or a sudden start.
- **A third of a second before the middle shot starts (about 0:01.2 if the shots are 1.5 s each):** the hum should begin to sink, and by the instant the middle shot starts it should be clearly quieter, roughly half as loud to the ear (12 dB). It should stay at that lower level for the whole middle shot, even while the laugh or voice is loud, and not wobble.
- **A third of a second after the middle shot ends (about 0:03.3):** the hum comes back up to where it was, smoothly.
- **Last 1.5 seconds (from 0:03.0 in a 4.5-second reel):** the hum fades away to nothing at the very last frame.
- **Two kept shots in a row:** the hum should stay low across the cut between them and not pop up for an instant.
- **Overall volume:** the reel should sound about as loud as a normal YouTube video, noticeably not quieter than other reels in her feed. Turn the phone to the same volume you used for another reel and compare. A reel that sounds very loud or distorted is a failure.
- **A reel with every shot off and no music:** silent, but plays normally (no error, no missing sound track).
- The closing sentence in the chat should say `sound evened to -14.0 LUFS` (or the figure the list asked for).

## Task commits

| Task | Name | Commit |
|------|------|--------|
| 1 (RED) | Failing tests for the sound settings, drop curve, gain rule and music library | 6f216fa |
| 1 (GREEN) | The sound settings, kept runs, drop curve, gain rule and music library reader | 25b20da |
| 2 | Music with fades and the drop in the mix, and the loudness measured, evened and stated | 38cedb7 |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `measure_loudness` needs the reel's length for its time limit**
- **Found during:** Task 2
- **Issue:** the plan names `measure_loudness(mix_path, folder)` but every FFmpeg run uses `normalize.ffmpeg_timeout(seconds)` (T-4-03), which needs the length.
- **Fix:** the function takes a third argument, `seconds`.
- **Files modified:** v2r/render/sound.py, v2r/render/__init__.py
- **Commit:** 38cedb7

**2. [Rule 2 - Missing critical functionality] a music file that vanishes between check and render**
- **Found during:** Task 2
- **Issue:** `mix_command` calls `track()`, which raises `LibraryError` if the music is gone; `render()` would have crashed with a traceback.
- **Fix:** `render()` turns it into a `RenderError` with the same sentence, so the scratch folder is still cleaned and nothing is built.
- **Files modified:** v2r/render/__init__.py
- **Commit:** 38cedb7

**3. [Rule 3 - Blocking] `aresample` was not in RENDER_FILTERS**
- **Found during:** Task 2
- **Issue:** a library track is resampled to the working rate before it is cut by sample, and `aresample` was not on render's list of filters it requires. (It was already in doctor's list.)
- **Fix:** added to `RENDER_FILTERS` in `v2r/render/__init__.py`.
- **Commit:** 38cedb7

### Differences in shape (no behaviour changed)

- With no drop, the music is labelled `[ducked]` directly instead of passing through a no-op filter, so no extra filter name is needed.
- A fade is capped at the reel's length (`min(fade, seconds)`), which is how "a fade longer than the reel covers the whole reel" is realised.
- Tests run against the Mac's FFmpeg 8.0.1; no FFmpeg 6.1 is installed here. Only filters and options present in 6.1 are used (`amix normalize=0`, `amultiply`, `aevalsrc`, `sine`, `afade`, `aresample`, `ebur128 peak=true`, `ametadata`), as checked in the research, but the sandbox itself has not run this plan's mix yet.

## Flagged assumptions settled here (for plan 10 to record and plan 11 to ask)

- `music/library.json` is read as `{"tracks": [{"id", "file", "seconds", ...}]}`; the file does not exist yet and Stage 18 defines the rest. A missing file means only `test-tone` is available.
- The test tone is 220 Hz and 300 seconds long.
- No track has a level of its own before mixing; the one final gain evens the whole mix.
- The loudness is measured with ebur128 and applied as one plain gain, not FFmpeg's loudness normaliser.

## Known Stubs

None. (`test-tone` is a deliberate stand-in for the music library until Stage 18, as the plan states.)

## Threat Flags

None. T-4-01 (the music id only chooses the tone or a library entry in Python; every number in the graph is formatted by this code; the track's file reaches FFmpeg only as an `-i` argument), T-4-02 (a track's file must be a plain name whose resolved parent is the music folder and which exists; tested with a symlink pointing outside), T-4-03 (every FFmpeg run has `normalize.ffmpeg_timeout`) and T-4-13 (the figure printed is the measured loudness plus the gain applied; a capped gain is said in words with the target and the ceiling) are in place and tested.

## Verification

- `uv run pytest tests/test_render_sound.py -x -q`: all pass in both shapes.
- Full suite: `735 passed in 631.42s (0:10:31)`.

## Self-Check: PASSED
