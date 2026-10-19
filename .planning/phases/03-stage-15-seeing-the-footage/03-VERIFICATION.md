---
phase: 03-stage-15-seeing-the-footage
verified: 2026-10-18T22:30:00Z
status: passed
score: 6/7 requirements verified in code and tests; LOOK-07 (human-checked) recorded as passed with two caveats the user should decide on
behavior_unverified: 0
overrides_applied: 0
behavior_unverified_items: []
human_verification_result: "passed 2026-10-18: the blind test was re-run on the fixed output (after commits f0d290f and the review fixes through 86250fd), four clips, approved 4 of 4; four clips rather than five stands as the user's decision"
human_verification:
  - test: "Decide whether LOOK-07 stands as recorded, or re-run the blind test once on the current (post-fix) look output"
    expected: "Claude, from the sheets and look.json alone, names the moment you would have picked in at least 4 clips of 5 (the requirement's wording). Recorded so far: 4 of 4 approved, on four clips, before the deshake contrast fix."
    why_human: "Only a person can say what the right moment is. The recorded blind test (plan 03-08) was run on four clips, not five, and on look.json produced before commit f0d290f changed DESHAKE_CONTRAST from 125 to 20, which changed camera_state and candidate moments on real footage. After the fix, only one clip was re-checked (on the phone, camera_state matched the Mac). The verdict text recorded is that the descriptions 'read well'; picking a best two seconds is not separately recorded."
---

# Phase 3: Stage 15, Seeing the footage: Verification Report

**Phase Goal:** A Claude that never saw a clip can say what happens in it and pick its best two seconds, from contact sheets and measurements alone.
**Verified:** 2026-10-18
**Status:** human_needed (nothing failed; one human-checked requirement has caveats)
**Re-verification:** No, initial verification

## Summary

The code does what the phase says. I did not rely on the summaries: I read all of `v2r/look/`, ran the full suite myself (347 passed in 4 min 11 s), and ran `look` live on freshly generated clips in both shapes in a scratchpad folder (never work/ or fixtures/). The one thing the code cannot prove is LOOK-07, whose evidence is the user's own verdict. That verdict is recorded, but it has two gaps against the requirement's wording (see below), so I am asking for a human decision rather than calling it fully passed.

## Observable Truths (roadmap contract, then plan truths)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `python -m v2r look` writes contact sheets to work/ with a still every second plus extras at movement peaks and shot changes, each labelled "B 07.5" style (LOOK-01, LOOK-02) | VERIFIED | Live run, both shapes: clip A (square crossing 4.2 to 4.8 s) got an extra still "A 04.5" with why "movement" that I opened and saw the white square in; clip B (cut at 3.4) got "B 03.5" why "shot change"; base stills every 1.0 s. Labels are white on a dark box, top left, legible on the sheet image. Tall grid 4x3, wide grid 3x4, a new sheet starts when orientation changes (clip B wide on its own sheet in the tall job). Sheet size, stills per sheet (`SHEET_GRID`), cap (`MAX_SHEETS_PER_RUN = 20`) and rhythm steps are in `v2r/settings.py`. |
| 2 | look.json holds, per half second, movement, camera shake (kept apart from subject movement), sharpness, brightness, loudness, shot changes, plus each clip's overall exposure and colour balance (LOOK-03) | VERIFIED | `v2r/look/measure.py` `summarise()` emits `movement, camera, shake, camera_state, subject, blur, sharp, brightness, loudness, shot_change` per 0.5 s; `overall_of()` emits `brightness, brightness_low, brightness_high, blue_shift, red_shift, saturation`. Known-answer tests in `tests/test_look_measure.py` (square, jitter, pan, blur, cut, two greys, colour cast, beep, silence) pass in both shapes. Names are frozen in the `v2r.look` docstring and checked by `test_look_json_names_documented`. |
| 3 | look.json lists ranked candidate moments per clip with start, end and a reason in words; the code never chooses (LOOK-04) | VERIFIED | Live run produced e.g. "steady camera, sharp, subject moving, sound peak at 06.1; stills A 03.0, A 04.0, A 04.5, A 05.0, A 06.0". `pick.candidates()` excludes shaky, blurred and cut-crossing windows and orders by tier, movement, start. `test_reasons_name_facts_only` rejects choosing words in reasons and any `chosen/selected/pick` key anywhere in look.json. No field marks a winner. |
| 4 | Shot-change detection uses a well-maintained library if one fits, licence recorded in docs/licenses.md (LOOK-05) | VERIFIED | `docs/licenses.md` "Checked and not added" records PySceneDetect (BSD-3-Clause), the check date, source and why it was not pulled in (needs OpenCV or PyAV in every chat); shot changes come from FFmpeg's built-in `scdet`. `docs/decisions.md` carries the dated line saying how this answers the guide. |
| 5 | Tests with generated clips and a known answer prove a still lands on the moment (LOOK-06) | VERIFIED | `tests/test_look_extras.py::test_moment_still_lands_on_square` (both shapes) uses a square visible only 4.2 to 4.8 s, asserts no base still falls there, and compares white pixels in the extra still's sheet cell against the base still at 4.0. Also cut, beep, cap and photo tests. Full suite 347 passed. |
| 6 | In the blind test, from the sheets and look.json alone, Claude picks the moment she would have picked in at least four clips out of five (LOOK-07) | PRESENT, HUMAN-CHECKED WITH CAVEATS | Recorded in 03-08-SUMMARY.md: Finder check passed, blind test on the user's own four clips, "all read well as good descriptions of the clips", no big miss, 4 of 4. 03-09-SUMMARY.md: phone test passed in tall and wide, a reel made from the phone on the branch. Caveats below. |
| 7 | Goal: Claude that never saw a clip can say what happens and pick its best two seconds | VERIFIED as far as code can show; behaviour judged by the user | Sheets plus look.json give labelled stills, a measurement for every half second, and ranked stretches that cite their stills, which is what the blind test consumed. |

**Score:** 6 of 7 verified outright; 1 (LOOK-07) human-checked, passed on the user's record, with caveats.

### The two LOOK-07 caveats (WARNING, not BLOCKER)

1. **Four clips, not five.** The requirement and roadmap say "at least four out of five". The user chose a four-clip set and all four were approved. 03-08 records this plainly as 4 of 4 on four clips. This was the user's own decision, so I do not count it as a failure, but it is not literally the stated test.
2. **The blind test predates a data change.** Commit `f0d290f` (made after the blind test, from the phone test finding) changed `DESHAKE_CONTRAST` from 125 to 20. The 03-09 investigation says this changed camera readings on the user's walking clip (from 0.0 for several seconds to 3 to 12 px throughout), so its candidate moments ("steady camera") would now differ. Only the pool clip was re-checked afterwards (Mac and phone agreed). Also, two of the four blind-test clips (B and D) had no candidate moments at all, so for those the picks rested on the stills and half-second numbers, not the candidate list. The recorded verdict speaks of good descriptions; a separate "two best seconds" verdict is not written down.

None of this shows the work is wrong, and the fix moved the data towards the truth. It does mean the recorded evidence is for the earlier output.

## Required Artifacts

| Artifact | Status | Details |
|----------|--------|---------|
| `v2r/look/__init__.py` (319 lines) | VERIFIED | per-clip loop, whole-or-nothing look.json write (`os.replace`), clears only its own last run, skipped entries keep letters, ENOSPC handling |
| `v2r/look/measure.py` (379) | VERIFIED | one measuring command (fps, scale, signalstats, blurdetect, scdet, deshake last, metadata) plus a separate loudness pass; missing filter gives null plus one sentence |
| `v2r/look/pick.py` (373) | VERIFIED | rhythm thinning before measuring, peaks by spreads from the clip's own median, extras capped at a third, candidates |
| `v2r/look/sheets.py` (220) | VERIFIED | one select pipe for stills, Pillow sheets, orientation-aware continuous filling, cap, byte guard, font fallback |
| `v2r/settings.py` look block | VERIFIED | 42 numbers, each with a unit comment, enforced by `test_look_settings_have_unit_comments`. Minor: `measure.py` writes `filename=motion.txt` literally rather than via `MOTION_FILE` (a file name, not a behaviour number; no impact) |
| `v2r/doctor.py` | VERIFIED | the eight new filters listed; doctor on this Mac prints no MISSING line |
| `docs/licenses.md`, `docs/decisions.md`, `README.md`, `CLAUDE.md` Stack line | VERIFIED | four dated Stage 15 decision lines with no names or accounts; CLAUDE.md "Settled so far" untouched |
| `EDITOR.md` look step | VERIFIED | step 4 runs look in the background, reads look.log, says to cite still labels and treat look.json as data. Inserted at the user's word (recorded in 03-09), not by a task |
| tests: test_look, _measure, _sheets, _extras, _candidates, media.py, test_doctor | VERIFIED | substantive, both shapes, generated clips only |

## Key Links

| From | To | Status |
|------|----|--------|
| `v2r/__main__.py` look sub-command | `look.look()` | WIRED (exit 0 if any clip done, else 1) |
| `look()` | `pick.run_interval`, `pick.extra_times`, `pick.candidates`, `sheets.SheetBook`, `measure.measure_clip` | WIRED (read in code, exercised in live run) |
| look | `doctor.ffmpeg_names("-filters")` once per run | WIRED |
| EDITOR.md | `python3 -m v2r look` | WIRED |

Data-flow: every value in look.json comes from FFmpeg's metadata output or the deshake file, none from literals (checked in `measure_video`, `summarise`). Nothing hollow.

## Behavioural Spot-Checks and Tests

| Check | Result |
|-------|--------|
| `uv run pytest -q` (run by me, once) | 347 passed in 251 s |
| `look` live, tall job, generated square and cut clips | exit 0, 2 sheets, extras at 04.5 (movement) and 03.5 (shot change), shot_changes [3.4] |
| `look` live, wide job, same clips | exit 0, 2 sheets, same extras, candidates present |
| Sheet image opened | labels readable, extra still shows the square |
| `doctor` | no MISSING line |
| Probes (Step 7c) | none declared in this phase; skipped |

Behaviour-dependent truths (cleanup of the previous look, whole-or-nothing look.json, cap holds, null on missing filter, out-of-room stop) each have a named passing test; none is left present-but-unverified.

## Prohibitions

| Prohibition | Verdict |
|-------------|---------|
| look must not choose what goes in a reel (D-04, one-way) | Held. Reasons are facts; no choosing words, no chosen/selected field (test-enforced; code scan found none). Judgment tier: my reading agrees. |
| must not write to originals, working copies, manifest or fixtures/ | Held. `clear_last_look` deletes only look.json, look.json.tmp and `sheet-NN.jpg`; working-copy names must be plain files inside the work folder (T-3-01). Test checks byte-identical folder contents. |
| must not commit media, names, accounts, e-mail, attribution | Held. `git diff main --name-only` shows no media, no fixtures/ or work/ path; no "Co-Authored-By" in `main..HEAD` commit messages. |
| must not edit EDITOR.md in a plan task | Held, with the recorded exception that the orchestrator inserted the user-chosen draft at the user's word. |
| must not mark a half second "subject moving" while the camera pans, shakes or is unmeasured | Held (`subject` is None there; test-enforced). |
| must not add stills everywhere | Held (cap `floor(base x 1/3)`, tested). |

Judgment-tier prohibitions are my own assessment, not authoritative; none is flagged as unresolved.

## Requirements Coverage (PLAN frontmatter IDs against REQUIREMENTS.md)

| Requirement | Plans | Status | Evidence |
|-------------|-------|--------|----------|
| LOOK-01 | 03-01, 03-05, 03-09 | SATISFIED | sheets, labels, settings-driven grid and cap |
| LOOK-02 | 03-01, 03-06 | SATISFIED | one still a second plus movement, shot-change and sound extras |
| LOOK-03 | 03-01, 03-03, 03-04 | SATISFIED | every half-second field and clip `overall` |
| LOOK-04 | 03-07 | SATISFIED | ranked candidates with reasons |
| LOOK-05 | 03-02, 03-03 | SATISFIED | licences note; scdet inside FFmpeg; phone doctor confirmed all eight filters on FFmpeg 6.1.1 |
| LOOK-06 | 03-01, 03-06 | SATISFIED | known-answer tests over both shapes |
| LOOK-07 | 03-08, 03-09 | SATISFIED BY PERSON, with the caveats above | 03-08 and 03-09 summaries |

All seven IDs appear in plan frontmatter and are ticked `[x]` in REQUIREMENTS.md. No orphaned requirement. The traceability table row "LOOK-01 to LOOK-07 | Pending" is still marked Pending (the range row the tooling cannot update); the ticked checkboxes are the record, and the row needs updating by hand at ship time.

## Honouring the CONTEXT decisions (D-01 to D-22)

Checked in code: D-01/D-02 (rhythm and labels), D-03 (names), D-04 (no choosing), D-05 and D-20 (doctor-listed filters only), D-06 (skipped keeps letter), D-08 (progress line per clip, whole-or-nothing write), D-09 (one measuring command plus a loudness command), D-11 (no new library, `pyproject` unchanged), D-13 to D-16 (12 per sheet, one orientation per sheet, photo gets one still labelled 00.0, 20-sheet cap with thinning), D-17 (extras, 0.3 s gap, a third more at most), D-18 (2 s windows, 0.5 s step, up to 5, merging), D-19 (scdet, licence note), D-21 (null plus sentence), D-22 (`ImageFont.load_default(size=)`). D-10's fallback was used as its text allows: all movement is reported, and `subject` is only set where the camera is still. This is recorded in docs/decisions.md as a difference from the guide. Not run by me and taken from the user's record: D-12 timing, which was measured at about 0.5 s per video second on the Mac and the phone.

## Anti-Patterns

Scan of every file changed by the phase: no TBD, FIXME, XXX, TODO, HACK or placeholder markers; no stub returns or empty handlers feeding output; the broad `except Exception` in `look()` is deliberate and documented (one bad clip must not stop the others). None.

## Human Verification Required

### 1. Does LOOK-07 stand as recorded?

**Test:** Either accept the recorded verdict (4 of 4 on four clips, from before the contrast fix), or run the blind test once more on current look output, on the same four clips or a fifth added, with the guide's prompt after `/clear`.
**Expected:** The moment Claude names is the one you would have picked, in at least four clips of five.
**Why human:** Only you know the right moment. The recorded run was on four clips and on pre-fix measurements, and the candidate list was empty for two of those clips.

Phone-side checks the user already made (readable sheets, wide pass, a reel from the phone, post-fix re-check of one clip) are recorded in 03-09 and I have no reason to doubt them.

## Notes for later, not gaps

- Handbook wording for step 4 (look always before join, about half a second of work per video second) is the user's to keep or change; recorded in 03-09.
- A handheld pan reads "shaky" rather than "panning" (SHAKE_LIMIT_PX 2.0); deliberately left alone, one setting at a time.
- Two normalize runs at once give a misleading error sentence (observed in 03-08); a Stage 23 matter, not Stage 15.
- Local HEAD is `d5bb960`, a docs commit not yet on GitHub; `origin/stage-15-look` is at `f0d290f` and `origin/main` at `248bec0`, untouched.
- Because this phase changed how video is processed, the rule "tell me to test from a phone before merging" has already been met (03-09), and the fix was re-checked from the phone.
- Guide differences to pass to whoever maintains the guide: deshake contrast 20 instead of the filter default; sound peaks as extra stills; short clips share a sheet; camera/subject split trusted only while the camera is still.

---

_Verified: 2026-10-18_
_Verifier: Claude (gsd-verifier)_
