---
phase: 04-stage-16-cut-list-and-renderer
plan: "10"
subsystem: docs
tags: [docs, decisions, readme, gates, privacy-scan]
requires: ["04-09"]
provides:
  - "docs/decisions.md: 17 dated Stage 16 lines, one for each way the build differs from the guide"
  - "CLAUDE.md: check | match | render in the stack line and one Stage 16 sentence in the settled list"
  - "README.md: check, match and render rows, the --work note and the schema row"
  - ".gitignore: /check.log, /match.log, /render.log"
  - "the gate results and the answer to the guide's Watch-out question"
affects: [04-11]
key-files:
  modified:
    - docs/decisions.md
    - CLAUDE.md
    - README.md
    - .gitignore
key-decisions:
  - "Every flagged assumption from plans 01 to 09 is written in docs/decisions.md as an assumption to confirm, not as a decision of the user"
  - "All 17 lines are dated 2026-10-19: the discuss step and the build both ran in the days up to today and the file records when it was written down"
requirements-completed: [CUT-01, CUT-02, CUT-03, CUT-04, CUT-05, CUT-06, CUT-07, CUT-08, CUT-09]
status: complete
actuals:
  tokens: 14000
  tasks: 2
  commits: 1
---

# Phase 4 Plan 10: Writing down Stage 16 and the last gates Summary

Stage 16's differences from the guide are now dated lines in docs/decisions.md, the README and CLAUDE.md match the code, and every automated gate passes on the branch (944 tests, doctor, requirements.txt, privacy scan).

## What changed, in plain English

No new programming. Four files changed, in one commit (448f632):

- **docs/decisions.md** has 17 new lines for Stage 16 (the file now has 18 Stage 16 lines with the one from 2026-10-11). Each says what was decided and how it differs from the guide. None names a person or an account. The lines marked "Assumption to confirm" are the ones the build chose and you have not yet seen on a phone.
- **CLAUDE.md** lists `check | match | render` in the stack line and has one new sentence in "Settled so far" (before the brief of three to five questions) covering the cut list's version, clips block, canvas, per-segment sound and focus point, the touch-up numbers written by `match`, the -14 LUFS / -1 dBTP target, the cover, the steady 4 percent moves and the step-down of long reels. Nothing else in the file changed.
- **README.md** has rows for `check [CUTLIST]`, `match [CUTLIST]` and `render [CUTLIST]`, a sentence that they take `--work FOLDER` and no `--shape`, and the `schema/` row naming cutlist.schema.json. The regenerate-requirements command is untouched.
- **.gitignore** ignores `/check.log`, `/match.log` and `/render.log`, as it does the other three logs.

EDITOR.md and docs/field-guide.html are untouched (`git diff --name-only main -- EDITOR.md docs/field-guide.html` prints nothing).

## Gate results

| Gate | Result |
| --- | --- |
| Full suite, `run-with-timeout 1800 -- uv run pytest -q` | **944 passed in 1136.40s (0:18:56)**, exit 0 |
| `uv run python -m v2r doctor` | No MISSING line (0 counted). Every Stage 16 filter, the matroska muxer and the concat demuxer are "available" |
| requirements.txt against a fresh `uv export` | Identical except line 2, the comment that records the output path of the export command (the scratch path against `requirements.txt`). No package line differs |
| Files under fixtures/ or work/ in the branch | none |
| Media files (video, audio, images) in the branch | none |
| E-mail addresses in the branch's diff | The plan's grep counts 131 lines, all of them pytest decorators (`@pytest.mark.parametrize` 125, `@pytest.fixture` 6) matched by the pattern. Reading only added lines and excluding decorators leaves 0. No address, and none of the user's |
| This Mac's home path in the branch's diff | 0 |
| Attribution lines in the branch's commit messages | The plan's grep counts 1: the message of 3878a13 says "requirements.txt regenerated with the README command", and "regenerated with" contains "generated with". It is not an attribution line. Searching for `co-authored-by` or the word `generated with` on its own finds 0. No commit message was changed |

### Time of the full suite

The suite took 18 min 56 s. Plan 10 named a 1500-second limit (25 minutes); the run was bounded at 1800 s and finished well inside it, but **the suite has now grown to about 19 minutes, so anyone running it with a limit under about 20 minutes will see it stopped.** Use 1800 s or more before the phone test. It was not necessary to run the split fallback.

## Is there any case where render produces something the cut list didn't specify?

**No.** One line for each way a renderer could help, and the test that shows this one does not:

- **A trimmed dark frame or a nudged cut:** `tests/test_render_tracer.py::test_tracer_two_shots_to_a_reel` and `tests/test_render_golden.py::test_golden_render` check the picture count against the list's frames, and (for the indexed clips) that each shot's first and last pictures are the exact first and last frames asked for, with a one-frame slip reading 8 luma values away. `test_one_segment_list_renders_the_same_twice` and `test_times_inside_one_frame_plan_the_same_video` show the plan does not wobble.
- **A reordered or dropped shot:** `test_golden_render` reads the middle-frame colour of every shot in list order for both approved examples, tall and wide; `test_plan_keeps_the_lists_order_whatever_the_letters` covers the plan.
- **An added move:** a photo with `move: none` is built still (`test_no_move_and_one_frame_give_no_filter`, `test_photo_is_built_from_its_full_size_copy`, plan 05); check only notes a photo with no move (`test_a_photo_with_no_move_gives_its_note`).
- **A colour step of its own:** with no touch-up block the picture's colour is unchanged (`test_no_touch_up_leaves_colour_alone`, plan 08) and a neutral record builds no filter; with one, exactly its numbers are applied.
- **A sound step of its own:** kept and off sound are built exactly (`test_kept_and_off_sound`), the music drops only under kept segments (`test_music_drops_under_kept_sound`, `test_adjacent_kept_segments_hold_the_drop`), a reel with no sound has a silent track (`test_silent_reel_has_a_silent_aac_track`) (plan 06).
- **A looped or extended track:** `check` refuses a track that runs out before the reel ends (`"The music runs out at ... seconds but the reel is ... seconds long."`, test_cutlist_check.py, plan 07), and the exact-length track passes (`test_music_exactly_as_long_as_the_reel_passes`).
- **A stepped-down frame:** this is the one place the renderer fits the list to a limit. It is done by join's own rule, only for reels past about 73 s, and render says so in a sentence (`test_long_reel_steps_down_and_says_so`, plan 09). A reel too long to fit is refused before anything is built (`test_too_long_is_refused_before_building`). It is listed as a flagged assumption below because CUT-07 says "at the canvas size".
- **The cover's default:** a stated rule (D-09), not a renderer choice: the reel's first frame when the list names none (`test_cover_default_is_the_first_frame`), a named segment and second otherwise (`test_cover_follows_its_segment`), and the closing sentence says which frame it took.
- **A bad list:** `test_tracer_invalid_list_builds_nothing` and `test_failure_leaves_nothing_behind`: no video, and the earlier outputs untouched.
- **Determinism:** `test_same_list_same_video` compares the decoded picture and sound of two renders.

## Flagged assumptions for the user to confirm in plan 11

Each is recorded in docs/decisions.md as "Assumption to confirm" where it is a build choice rather than a decision, and each lives in the place named.

| Assumption | Where it is set |
| --- | --- |
| join's size rule steps the frame down on reels over about 73 s (2/3) and 146 s (1/2), where CUT-07 says "at the canvas size" | `join.fit` / `FIT_STEPS` in settings.py; decision line "A long reel is fitted by join's own rule" |
| The shortest reel is 3 s; at most 120 segments; a crop keeping under half of a clip's picture gets a note | `MIN_REEL_SECONDS`, `MAX_SEGMENTS`, `CROP_NOTE_SHARE` in settings.py; decision line on the checker |
| Music fades in over 0.5 s and the drop ramps over 0.3 s (and out over 1.5 s by default) | `FADE_IN_SECONDS`, `MUSIC_DROP_RAMP`, `FADE_OUT_SECONDS` in settings.py; decision line on the music |
| `match`'s median is over the clips the segments use, not all clips | match.py; decision line on the touch-up |
| Every photo segment, moving or still, is built from the full-size JPEG | video.py (`photo_path`); decision line on photos |
| A photo segment is capped at 4 s | `PHOTO_SECONDS` in settings.py (the Stage 14 still-clip length; check refuses a longer photo segment); not a separate decision line, recorded here |
| The test tone is id "test-tone", 220 Hz, 300 s | `v2r/render/sound.py`; decision line on the music |
| `clips` and `look.touch_up` are objects keyed by letter; `why` is required and non-empty | schema/cutlist.schema.json; decision line on the keyed objects |
| A one-frame shot is the full canvas for every move | `plan.move_windows`; decision line on one-frame shots |

## Differences from the guide you may want the guide revised for

All 17 lines in docs/decisions.md; in short: the list's version and rounding rule, the required clips block, the canvas tied to the manifest's shape (and no `--shape` on the three new commands), sound per segment (not one top-level switch), `focus_x` and `focus_y`, a single steady 4 percent move drawn with perspective, the photo default left to the handbook with every photo built from its full-size copy, the touch-up as capped numbers from `match`, `clips`/`touch_up` keyed by letter and `why` required, the -14 LUFS / -1 dBTP target in the list, the music drop and fade defaults, the cover by segment and second, the proof sheet's first-and-last frame of every segment, long reels stepped down, shots built as scratch pieces, and the checker's library and limits.

## Deviations from Plan

None in the work itself. Two notes:

- The plan's acceptance grep for e-mail addresses and the one for attribution lines are not clean by their own pattern (pytest decorators and the word "regenerated with"); both are false positives, checked by hand as shown in the gate table, so nothing was changed.
- Every line in decisions.md carries 2026-10-19, which is both the date the task ran and the date given for the discuss step's decisions.

## Authentication gates

None.

## Known Stubs

None.

## Threat Flags

None. T-4-09 (private data on the branch) is mitigated by the scan above; T-4-14 (names in decisions.md) by reading each new line: none names a person or an account.

## Open items for plan 11

- Nothing is pushed. The branch has not been tested on a phone.
- The planning documents under `.planning/` were not rewritten; the home-path scan found none in the diff.
- Because `ebur128`, `amix` and the other filters were checked on the Mac's FFmpeg 8.0.1, not on the sandbox's 6.1 (plan 06), the phone test is the first run on 6.1.

## Self-Check: PASSED

- docs/decisions.md, CLAUDE.md, README.md and .gitignore changes are in commit 448f632 on stage-16-render.
- `grep -c "· Stage 16 ·" docs/decisions.md` prints 18; CLAUDE.md and README.md greps print 1; `^/render.log$` prints 1.
