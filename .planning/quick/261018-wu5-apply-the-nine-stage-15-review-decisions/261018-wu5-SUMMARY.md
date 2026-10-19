---
phase: quick-261018-wu5
plan: 01
subsystem: look
tags: [look, candidates, shake, contact-sheets, temporary-files, time-limit]
requires:
  - phase: 03-stage-15-seeing-the-footage
    provides: look, candidates, contact sheets, the nine review decisions of 2026-10-18
provides:
  - candidates only when something about the picture was measured, with honest blur wording
  - shake averaged within one shot
  - tall sheets 1192 by 1568, wide sheets unchanged
  - look's scratch files in a hidden folder inside the work folder, cleared by the next run
  - LOOK_RUN_SECONDS, one time limit for a whole run
affects: [stage-16-cut-list-and-renderer, handbook step 4]
tech-stack:
  added: []
  patterns: [run_timeout(allowance, deadline) cuts every FFmpeg command to the time the run has left]
key-files:
  created: []
  modified:
    - v2r/settings.py
    - v2r/look/__init__.py
    - v2r/look/measure.py
    - v2r/look/pick.py
    - v2r/look/sheets.py
    - tests/media.py
    - tests/test_look.py
    - tests/test_look_candidates.py
    - tests/test_look_measure.py
    - tests/test_look_sheets.py
key-decisions:
  - "LOOK_RUN_SECONDS is 30 minutes, a value the planner chose; the user decided only that there is one setting"
  - "Candidates are decided in one place, pick.candidates, so both a failed measuring pass and one that measured nothing give none"
status: complete
actuals:
  tokens: 16900
  tasks: 3
  commits: 6
---

# Quick task 261018-wu5: the nine Stage 15 review decisions

**Look now says only what it knows: no candidate moments without measurements, blur worded against the clip itself, shake judged inside one shot, tall sheets at the size Claude sees, scratch files kept in a hidden folder in the work folder, and one time limit for a whole run.**

The work is on branch `stage-15-review-fixes`. Nothing was pushed or merged. The full test suite passes: 429 tests, up from 412.

## What changed, in plain English

- **WR-01, no made-up order.** If look could not measure a video's picture (the measuring step failed, ran out of time, or gave no camera, movement or sharpness value in any half second), `look.json` now lists no candidate moments for it. Before, it still listed an order built from nothing, which read like a recommendation. A clip where only some half seconds are missing a value is still listed, because a missing value never leaves a stretch out. The stills and the sheet are still made.
- **WR-02, honest blur wording.** A candidate's reason used to say "sharp". It now says "no blurrier than the rest of the clip", or "... where measured" when some half seconds were not judged, or "sharpness not measured". Blur is only ever judged against the clip's own typical blur, so a clip that is soft all the way through counts as fine, and the old word promised too much.
- **IN-03, a steady shot after a pan is no longer called shaky.** The one-second average that tells shake from a pan now stops at a cut on each side. Before, a pan just before a cut made the first half second of the next, steady shot read "shaky", and that shot lost candidate moments it should have had. I saw this happen on a made-up pan-then-cut clip with the old code (see below).
- **IN-05, tall sheets at the size Claude sees.** A tall sheet is now 1192 by 1568 pixels (cells 288 by 512), so its long edge is the 1568 Claude's viewer shows and nothing is shrunk afterwards. A wide sheet is unchanged at 1950 by 1476. The width is now a setting for each shape (`SHEET_WIDTH` in `v2r/settings.py`). The label text is smaller in the file but ends up the same size on screen as before, because the old tall sheet was being shrunk anyway.
- **WR-04, scratch files in the work folder.** Look's temporary text files (the measuring output and the stills command's error text) now live in a hidden folder named `.v2r-look-<random>` inside the work folder and are removed when each clip is done. The next run deletes any such folder a stopped run left behind, and only those: a link with that name, any other hidden folder and your own files are never touched (a test proves this).
- **IN-02, IN-04, IN-07, tidy-ups.** The deshake step now builds its file name from `MOTION_FILE` instead of writing it twice. The `DESHAKE_CONTRAST` comment now gives its range as 1 to 255 (deshake refuses 0). The number of decimals on still labels and on "sound peak at" times is one setting, `LABEL_DECIMALS` (still 1, so labels stay like "A 03.0"). The `look.json` description now gives the real candidate order: camera still, then panning, then not measured; then more movement; then the earlier start. Sharpness only leaves stretches out and is not part of the order. The description of `brightness_low` and `brightness_high` now says what they are: the brightness below which the darkest tenth of each picture falls and above which the brightest tenth falls, averaged over the clip. Stage 16's match reads these, so the wording had to be exact.
- **IN-06, a time limit for a whole run.** A new setting, `LOOK_RUN_SECONDS`, is **30 minutes**. Every FFmpeg command gets at most the time the run has left. Once it is used up, each clip not yet started becomes a skipped entry, "Clip X was not looked at because look reached its time limit." One sentence naming the first such clip goes into `missing` and the log. The run still ends normally (exit code 0, `finished: true`). **The planner chose 30 minutes**; you decided only that there should be one setting. It covers about an hour of footage at the phone's measured 0.5 seconds of work per second of video. It is the one number to change if long Mac videos (Stage 23) ever need more. Two smaller tidy-ups under IN-06: `candidate_reason` lost two inputs it never used, and the sheet tests' size table, which was named for tall only, is renamed `CLIP_SIZE`.

## The pan-then-cut test failed on the old code

The new test uses a made-up clip that pans (112 pixels a second for a 360-wide clip, about 10 pixels per analysed frame) and then cuts to a still picture at 4.0 seconds. Run against the old averaging, in both shapes, the half second at 4.0 read "shaky" (and in the tall clip the half at 3.5 did too). With the fix, no half second is shaky, every half from 4.0 on is "still" and 1.0 to 3.5 is "panning". The hand-made-numbers test failed on the old code too.

## For the user to paste into EDITOR.md

EDITOR.md was **not changed**. If you agree, put this sentence in step 4, right after "Open the sheets to see the clips, and send them to the user when asked.":

> Send at most five sheets in one reply and offer the rest in the next, because all of a long run's sheets together can be too big for one reply.

Why: twenty sheets can pass the 24 MiB a reply may carry (`MAX_RESULT_BYTES`), and a tall sheet is now seen at full size, so it is worth showing them in small batches.

## Differences to tell you about

- Stage 15's planning (`03-CONTEXT.md`) had D-13's 1950-pixel-wide trial sheet and D-18's example reason using the word "sharp". Both are now different by your 2026-10-18 decisions: tall sheets are 1192 wide, and reasons say "no blurrier than the rest of the clip". If the guide's Stage 15 quotes either, it needs revising. I did not open or edit `docs/field-guide.html`.
- This task did not add a dated line to `docs/decisions.md`, since you gave the decisions log to another quick task. Say whether these two differences belong in it.
- `LOOK_RUN_SECONDS = 30 minutes` is the planner's value, not yours.
- Not done, as the plan said: IN-01, listing excluded stretches as facts, a timeout for `doctor.ffmpeg_names`, the shot-change rounding and the 12-column motion row, and the unused shape parameter in some `test_run_` tests.

## Phone test before merging

This changes how look measures and draws, so test it from her phone on branch `stage-15-review-fixes` before merging, then make a reel on that branch (nothing merges into main until a reel has been made from a phone on the branch).

Attach three short clips: one ordinary upright clip, one filmed sideways, and one with a cut in it (for example a clip saved from an editing app with two shots, ideally a moving or panning shot followed by a steady one). Say: "use branch stage-15-review-fixes. Look at these clips, show me the contact sheets, tell me each sheet's size in pixels, and show me look.json's shot changes and candidates for each clip." Then check:

- **Sheet size.** Each tall sheet is 1192 by 1568 pixels, and the sideways clip's wide sheet is 1950 by 1476. Zoom in on the phone: the white-on-black labels such as "A 03.0" must still read clearly and every still must be recognisable.
- **Reason wording.** Each candidate's reason says "no blurrier than the rest of the clip" (or "... where measured") where it used to say "sharp". The word "sharp" on its own appears in no reason.
- **The clip with a cut.** Find its time in `shot_changes` (for example 3.4). No candidate may start before that time and end after it. The half-second entries just after the cut (the cut time rounded down to the half second, and the next one) must not say "shaky" if the phone was steady after the cut, even when the shot before it moved.
- **Leftovers.** Ask Claude to run `ls -a work`. No entry may start with ".v2r-look-".
- **Time.** `look.log` has no "time limit" sentence, and look takes about as long as before (about 28 s for three clips under 20 s, test 12 in `docs/phone-limits.md`).
- **A reel.** Then join a reel on the same branch and play it. It should play upright with sound, as before (this task does not change normalize or join).

## Commits

| Task | Commit | What |
|------|--------|------|
| 1 test | 0c44320 | candidates say only what look measured |
| 1 fix | 8293975 | no candidates without measurements, honest blur wording, label decimals in settings |
| 2 test | fb63118 | a steady shot after a pan is not called shaky |
| 2 fix | 044695e | average the camera's shake within one shot |
| 3 test | 023c017 | tall sheets at the viewer's size, look's own temporary folder, a run time limit |
| 3 fix | fc40d90 | smaller tall sheets, temporary files in the work folder, a time limit for a whole look run |

## Deviations from Plan

None. The plan was executed as written. Two small points inside it: the `LABEL_DECIMALS` comment sits on the same line as the setting as the plan asked, and the new tests in `test_look_candidates.py` use a hand-made partly-missing case exactly as listed.

## Known Stubs

None.

## Threat Flags

None. The only new file-system action is deleting look's own hidden scratch folders (T-q261018-01), and a test proves a user's hidden folder and a symlink's target survive.

## Self-Check: PASSED

- All six commits exist on `stage-15-review-fixes` (`git log a995d68..HEAD`).
- `EDITOR.md`, `CLAUDE.md`, `docs/`, `fixtures/`, `work/`, `requirements.txt` and `pyproject.toml` are unchanged since a995d68.
- No commit has an attribution line.
- The full suite passes: 429 tests.
