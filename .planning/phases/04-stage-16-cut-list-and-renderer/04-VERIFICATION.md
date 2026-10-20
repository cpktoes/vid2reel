---
phase: 04-stage-16-cut-list-and-renderer
verified: 2026-10-19T00:00:00Z
status: passed
score: 5/5 roadmap truths verified (9/9 requirements satisfied)
behavior_unverified: 0
overrides_applied: 0
human_verification_result: passed. The user made one wide reel from the phone on branch stage-16-render with commits 36a3db6 and f7bb4a0 and the review fixes in place, and replied "approved" in chat on 2026-10-19 (see 04-UAT.md).
human_verification:
  - test: "Make one wide reel from a phone on branch stage-16-render with the two follow-up changes in place (the EDITOR.md focus-point sentence, commit 36a3db6, and check's crop note naming the band the crop keeps, commit f7bb4a0)"
    expected: "check prints a crop note that names the part of the picture the frame keeps (for example 'the part from 20 to 52 percent down the picture'); Claude aims focus_y at the thing the reel is about and says roughly where the frame lands; the finished wide reel looks right on the phone"
    why_human: "The project's merge rule says nothing merges into main until a reel has been made from a phone on the stage's branch, and these two changes landed after the 2026-10-19 phone test. Framing and how a crop looks cannot be judged by code. docs/decisions.md records this as the assumption to confirm."
---

# Phase 4: Stage 16 - Cut list and renderer Verification Report

**Phase Goal:** A cut list, checked against a schema, renders to exactly that video in either shape, with a mild touch-up, gentle movement and a proof sheet.
**Verified:** 2026-10-19
**Status:** passed (no gaps; the phone check was approved by the user on 2026-10-19)
**Re-verification:** No, initial verification
**Branch confirmed:** stage-16-render

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `python -m v2r check` reports every problem as one plain-English sentence, against the schema and the manifest | VERIFIED | `v2r/render/check.py` (743 lines) validates with jsonschema against `schema/cutlist.schema.json`, then against the manifest (`clips_problems`, `segment_problems`, `canvas_problems`) and the music library (`sound_problems`), and has a sentence function per fault kind. I ran it on a deliberately broken list built from the approved tall example: it printed four separate sentences ("Segment 2's move is \"zoom\"; it must be one of none, push-in, pull-out, pan-left or pan-right.", "The look's filter is \"sepia\"; only \"none\" can be built until Stage 21.", the focus_x and music_under_sound ones) plus the notes. `tests/test_cutlist_check.py` and the rest of the checker, plan, settings, match and doctor tests: 352 passed. |
| 2 | `render` builds exactly the list in tall or wide, straight cuts, every segment filling the canvas around its focus point, no letterbox or blurred background; an invalid list builds nothing | VERIFIED | `render()` in `v2r/render/__init__.py` runs `check.check` first and raises `RenderError` ("The cut list has N problems, so nothing was built.") before any scratch folder exists. `plan.fill_region` crops to fill around focus_x and focus_y; `video.video_chain` is trim, crop, scale, move, touch-up and nothing else. A grep for pad, blur and letterbox in `v2r/render/` finds none in picture code (the one `apad` is the sound bed). Straight cuts: pieces joined with the concat demuxer. Tests: `test_tracer_two_shots_to_a_reel`, `test_tracer_invalid_list_builds_nothing`, `test_golden_render` in both shapes: all pass. |
| 3 | A segment can have a slow steady push-in, pull-out or pan; `match` writes a mild per-clip correction that render applies and nothing more | VERIFIED | `plan.move_windows` and `video.perspective_filter`: one steady speed, `MOVE_AMOUNT = 0.04` in settings.py, photos built from the full-size copy (`photo_path`, `test_photo_is_built_from_its_full_size_copy`). `match.touch_up_records` aims at the median, never neutral grey, capped by `TOUCH_UP_*` settings; `video.touch_up_filter` applies exactly the numbers (a neutral or absent record builds no colour filter). The schema's `filter` is an enum of "none" only. `tests/test_render_video.py` (smoothness, steady travel, exact touch-up numbers, rounding, legal range) and `tests/test_match.py`: pass. |
| 4 | Each segment's own sound kept or dropped, music underneath, the mix normalized to a stated loudness | VERIFIED | `v2r/render/sound.py`: per-segment keep or off, music from `music_from` with fades, the drop under kept runs with a ramp, `measure_loudness` (ebur128) and `gain_for` with a true-peak ceiling. Target -14 LUFS and -1 dBTP are in settings.py (`LOUDNESS_TARGET`, `TRUE_PEAK_CEILING`) and the figure is stated in render's closing sentence ("sound evened to X LUFS") and in docs/decisions.md. `test_loudness_is_evened_to_the_target`, `test_music_drops_under_kept_sound`, `test_fades`, `test_peak_ceiling_stops_the_gain`, `test_silent_reel_has_a_silent_aac_track`: pass (test_render_sound.py, 144 passed with the video and tracer files). |
| 5 | H.264/AAC fast-start MP4 under the send-back limit with a contact sheet and cover still; golden renders in both shapes prove the same list always makes the same video | VERIFIED | `video.final_command` (libx264, aac, `+faststart`, bitexact flags) and `self_check` (frame count, size, codecs, deleted on mismatch); the size is checked against `MAX_RESULT_BYTES` and the file deleted if over; `join.fit` steps long reels down. `proof.make_proof` (first and last frame of every shot, in `proof/`) and `proof.make_cover` (beside the reel). `tests/test_render_golden.py`: 27 passed in 90 s (both approved examples in both shapes, length to the frame, size, colour at a known second, moov before mdat, same list gives the same decoded video twice, failure leaves nothing behind). |

**Score:** 5/5 truths verified, 0 present but behavior-unverified. Behavior-dependent truths (move smoothness, music drop, cleanup on failure) each have a passing behavioural test.

### Requirements Coverage

Every ID in the PLAN frontmatter (04-01 to 04-11) is in REQUIREMENTS.md, and REQUIREMENTS.md maps CUT-01 to CUT-09 only to this phase; no orphans.

| Requirement | Source plans | Status | Evidence |
|-------------|--------------|--------|----------|
| CUT-01 schema | 04-02, 04-04, 04-10 | SATISFIED | `schema/cutlist.schema.json` (canvas, clips, segments with focus_x/y, move, sound, why; look with touch_up per clip and filter "none"; sound block; cover; text and voice accepted) |
| CUT-02 check | 04-01, 04-02, 04-04, 04-07, 04-10 | SATISFIED | `v2r check` wired in `__main__.py`; one sentence per problem; manifest, clips block and music compared |
| CUT-03 render | 04-01, 04-03, 04-05, 04-09, 04-10, 04-11 | SATISFIED | see truth 2 |
| CUT-04 moves | 04-03, 04-05, 04-10, 04-11 | SATISFIED | see truth 3 |
| CUT-05 match | 04-03, 04-08, 04-10, 04-11 | SATISFIED | see truth 3 |
| CUT-06 sound | 04-06, 04-10, 04-11 | SATISFIED | see truth 4 |
| CUT-07 output | 04-01, 04-03, 04-06, 04-09, 04-10, 04-11 | SATISFIED (see note 1) | see truth 5 |
| CUT-08 ignored fields | 04-04, 04-10 | SATISFIED | speed, transition, text and voice are accepted by the schema; my check run printed "Segment 4's speed is accepted but not built yet, so the shot plays at normal speed." as a note, not a refusal |
| CUT-09 golden renders | 04-09, 04-10, 04-11 | SATISFIED | `tests/test_render_golden.py` |

### Key links

| From | To | Status |
|------|----|--------|
| `__main__.py` check, match, render | `render.check`, `render.match`, `render.render` | WIRED |
| `render()` | `check.check` before any build, `plan.plan`, `video.piece_command`, `sound.mix_command`, `join.fit`, `proof.make_proof`, `proof.make_cover` | WIRED |
| `check` and `render` | the same `plan` arithmetic | WIRED (shared module, so they cannot disagree) |
| `match` | `look.json` overall block and `check.clips_problems` | WIRED |
| doctor | the FFmpeg pieces render uses (perspective, lutyuv, ebur128 and so on) | WIRED (`RENDER_*` lists checked at render start; `test_render_refuses_on_a_missing_ffmpeg_piece`) |

### Data-flow trace

The reel is built from decoded working copies and full-size photos, and the golden tests read the colours and frame luma back from the finished file, so values are traced from real source to real output. No static or hollow data sources found.

### Project rules and context decisions

- Three jobs: `v2r/render/` makes no choices (no moves added, no trimming, no reordering); `match` writes decisions into the cut list; look is untouched apart from a 12-line reuse change in `look/sheets.py` (test added). Honoured.
- Numbers in settings.py: move amount, touch-up caps, loudness, ceiling, fades, ramp, shortest reel, crop-note share, segment limit, cover quality, ranges all live there; a guard test exists (`test_render_settings.py`).
- Both shapes first-class: the golden, tracer, video and sound tests are parametrized over tall and wide.
- No attribution lines found in the 39 commits ahead of main. Library added with licence in docs/licenses.md (jsonschema, MIT) and requirements.txt regenerated.
- docs/decisions.md has 18 dated Stage 16 lines; CLAUDE.md updated (commands and settled list). The 27 decisions D-01 to D-27 were checked against code and tests; none was found dropped.
- EDITOR.md carries the check, match and render steps (user-authored per plan 11) and the photo push-in line.
- No debt markers (TBD, FIXME, XXX) in the phase's code or tests.

### Behavioral spot-checks and probes

Targeted test runs only (the orchestrator is running the full suite; plan 11's summary reports 946 passed):

| Files | Result |
|-------|--------|
| test_cutlist_check, test_render_plan, test_render_settings, test_match, test_doctor | 352 passed in 12 s |
| test_render_golden | 27 passed in 90 s |
| test_render_video, test_render_tracer, test_render_sound | 144 passed in 191 s |
| check run on a broken list in a temp folder | four problems and a note, each one plain sentence |

No probe scripts are declared by this phase (step skipped).

### Anti-patterns

None blocking. No stubs, placeholders or console-only handlers in `v2r/render/`.

### Notes (information only, not gaps)

1. CUT-07 says "at the canvas size". Reels longer than about 73 seconds are stepped down to 2/3 size (and past about 146 seconds to 1/2) by join's existing size rule, and render says so in a sentence. This is a recorded decision in docs/decisions.md, flagged there as an assumption to confirm. The roadmap criterion (under the send-back limit) is met.
2. Follow-up chores named in the summaries: record the phone test in docs/phone-limits.md (as for Stages 14 and 15), and the ROADMAP plan checkboxes for Phase 4 are still unticked in the top list.
3. Several decisions.md lines are marked "Assumption to confirm" (fade-in 0.5 s, ramp 0.3 s, three limits, long-reel step-down, median over used clips). These are for the user, not defects.

### Human Verification Required

#### 1. One wide reel from the phone after the two follow-up fixes

**Test:** On branch stage-16-render, make one wide reel from the phone with a clip where the crop keeps little of the picture. Watch what `check` says about the crop, and look at the finished reel and its cover.
**Expected:** The crop note names the band of the picture kept; the reel frames the thing the reel is about at the moments named in the proof sheets; the cover still is the frame the list names (or the first frame).
**Why human:** Framing and look cannot be seen by code, and the project's merge rule requires a phone reel on the branch after these two changes (commits 36a3db6 and f7bb4a0), which came after the approved 2026-10-19 tall and wide phone test.

## Gaps Summary

No gaps. Every roadmap truth and all nine requirements are backed by code that exists, is wired, and is exercised by passing tests (523 targeted tests passed in this verification; the full suite is being run separately). The one open item is the human phone check above, which the merge rule requires before the stage goes into main.

---

_Verified: 2026-10-19_
_Verifier: Claude (gsd-verifier)_
