---
phase: 07-stage-19-conversation
verified: 2026-11-04T00:00:00Z
status: passed
score: 5/5 roadmap success criteria verified (7/7 requirements satisfied)
behavior_unverified: 0
overrides_applied: 0
re_verification: false
human_verification_result: criteria 1, 2, 4 and 5 are the chat's Claude following EDITOR.md; given by the user (nine fresh-session rehearsals approved, 07-07-SUMMARY.md; phone test on commit a875e1b approved 2026-11-04 at 7 min 33 s, 07-09-SUMMARY.md and docs/phone-limits.md row 19). Criterion 3 verified directly in code and by a test run.
---

# Phase 7: Stage 19 – Conversation Verification Report

**Phase Goal:** Making a reel is a short conversation: a brief of a few quick questions, a quiet wait, a short reply, and follow-ups that change only what was asked.
**Verified:** 2026-11-04
**Status:** passed
**Re-verification:** No – initial verification

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Three to five numbered questions in one message, each answerable in a few words with a default, answered ones left out, brief skipped on "just make it" | VERIFIED (code can't prove it; handbook text plus human checks) | EDITOR.md line 39, "Talking with her": four numbered questions each with its default, "Leave out any question the user's message or the Reel style section already answers, the message winning, and number the rest from 1", "If the user says 'just make it', ask nothing", one-line example answer, "After looking, ask one more question only if the named moment cannot be found". `tests/test_editor_handbook.py` passes (27 guard tests, word cap 1,800, every named command exists). Rehearsals: nine fresh-session cases approved, and the briefed reel judged clearly better than "just make it" (07-07-SUMMARY.md). Phone test asked zero questions because the Reel style's standing answers covered all four, which is the handbook's own leave-out rule working (07-09-SUMMARY.md). |
| 2 | One line plus a time estimate, then silence; reply is the video, at most two lines on what is in it, three follow-ups, clips described by content, no track named | VERIFIED (human) | EDITOR.md: "send one line giving minutes, the number of clips plus three, and stay silent until the reel"; reply paragraph: "at most two lines ... naming clips by what is in them, never by letter or number; the cover still; and three follow-ups fitted to this reel". The Sound paragraph says the tool adds no music, so no track exists to name. Phone test: first reply was the minutes line (about 8 minutes for five clips), then quiet; delivered in 7 min 33 s. See caveat 1 and 2 below. |
| 3 | `python -m v2r revise` applies one named change (shorter/longer, reorder, drop clip or shot, keep/mute sound, canvas) as a new numbered cut list and leaves every other field untouched, proved by tests | VERIFIED (direct) | See "Criterion 3 in detail". `uv run pytest tests/test_revise.py tests/test_revise_chain.py tests/test_cutlist_check.py tests/test_editor_handbook.py -q` gives 523 passed in 47.71 s. |
| 4 | Errors are plain English ending with a next step; if the work folder is gone Claude asks for the clips again | VERIFIED (code plus handbook plus rehearsal) | `v2r/render/revise.py` WORK_GONE: "There is no cut list and no manifest.json in the work folder, so there is nothing to change; attach the clips again and make the reel anew." Every refusal path is one plain sentence (`ReviseError`, `Unchanged`), covered by tests such as `test_an_empty_work_folder_says_there_is_nothing_to_change`, `test_a_list_that_breaks_its_rulebook_is_refused`, `test_a_bad_shot_is_one_plain_sentence`. EDITOR.md: "give the tool's exact sentence, then one sentence on what to do next: fewer clips, a shorter reel, or attaching the clips again. If work/ is gone ... say the clips must be attached again in the same order and offer the last cut list as text." The nine rehearsals were approved with nothing in the handbook or code needing change (07-07-SUMMARY.md). |
| 5 | From a phone on the branch: attach, brief, reel, then "shorter", "mute it", "a wide version", each changing only what was asked | VERIFIED (human) | Phone test approved ("approved", 2026-11-04) on commit a875e1b, which equals the tested code (`git ls-remote` matched HEAD; 235 tests passed on it). Per 07-09-SUMMARY.md: "shorter" 15.8 s to 12.0 s, same seven shots, only the "to" of shots 4 to 7 changed; "mute it" only "sound" changed; "a wide version" only the canvas changed; nothing started from scratch. |

**Score:** 5/5 truths verified, 0 present but behavior-unverified.

### Criterion 3 in detail

| Check | Evidence | Status |
|-------|----------|--------|
| Command exists and takes each change | `v2r/__main__.py` lines 80 to 130 register `revise` with sub-commands `sound keep|off [--shot N]`, `canvas tall|wide`, `reorder`, `drop`, `shorter --to --from`, `longer --to --from`; line 198 dispatches to `render.revise.run`. | VERIFIED |
| Writes a new numbered list, never the old one | `next_list_path`/`write_new` in `v2r/render/revise.py` open with mode "x" (exclusive), numbers only go up. Tests: `test_each_run_gets_the_next_free_number`, `test_numbers_only_go_up`, `test_the_input_list_is_not_opened_for_writing`, `test_revise_renders_nothing_and_adds_no_other_file`. | VERIFIED |
| Every other field untouched | `run` deep-copies the list and each `change_*` edits only its own fields; fields revise has never heard of survive (`test_unknown_fields_survive`). Tests diff whole lists with an independent `changed_paths` helper: sound (`test_sound_off_changes_only_the_sound_fields`), canvas (`test_canvas_changes_only_the_two_canvas_numbers`), shorter (`test_shorter_changes_only_the_ends_of_the_shots`, asserts the changed set equals exactly the `to` paths), longer (`test_longer_changes_only_the_ends_of_the_named_shots`), reorder (`test_reorder_plays_the_same_records_in_the_given_order`), drop (`test_drop_a_clip_takes_out_all_its_shots_and_touches_nothing_else`, `test_drop_shot_keeps_every_other_record_whole`), in tall and wide. | VERIFIED |
| The change itself is exact | Target length met to the frame (`test_shorter_lands_on_every_target`, `test_the_frame_loop_every_start_and_length`), order as given, cover follows its shot, sound and canvas set. | VERIFIED |
| Deterministic, no code choosing shots | `test_reorder_and_drop_never_choose`, `test_shorter_decides_nothing_the_named_order_is_the_only_choice`. The chat's Claude names the shots; revise scores nothing. | VERIFIED |
| End to end | `tests/test_revise_chain.py` renders a reel, then shorter (135 frames), sound off (peak at or below -60 dB), then the other shape's canvas (aspect flips, 135 frames, silent) with FFmpeg, in both shapes, and shows a second normalize leaves earlier lists and reels byte-identical. | VERIFIED |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `v2r/render/revise.py` (580 lines) | The revise logic | VERIFIED | Substantive, wired into `v2r/__main__.py`, uses `check` and `plan` functions rather than parsing afresh. |
| `v2r/settings.py` | RECIPES (lively/calm lengths), DEFAULT_RECIPE, REVISE_* limits | VERIFIED | Lines 122 to 137; numbers live in settings as the project rule requires. |
| `schema/cutlist.schema.json` | Optional `recipe` enum lively/calm; version stays 1 | VERIFIED | Line 51; not in `required`. |
| `v2r/render/check.py` | `recipe_notes`: assumed-Lively note, notes (never refusals) for shots outside the range | VERIFIED | Lines 691 to 765; called from the notes pass. Covered by `tests/test_cutlist_check.py`. |
| `EDITOR.md` "Talking with her" | The user's section: brief, start line, reply, follow-ups with revise calls and fields changed, errors, fresh chat for new clips | VERIFIED | 1,767 words, under the 1,800 cap; recipe sentence kept in step with settings by a test; no `--work` or `--no-size-limit` named. |
| `README.md` | `revise` command row | VERIFIED | Line 41, and line 44 on `--cutlist` and `--work`. |
| `docs/decisions.md`, `CLAUDE.md`, `docs/phone-limits.md` row 19 | Decisions, closed Decide box, phone-test record | VERIFIED | Nine "Stage 19" lines in decisions.md; row 19 present. `docs/field-guide.html` is not in the branch diff against main. |

### Key Link Verification

| From | To | Via | Status |
|------|----|-----|--------|
| `v2r/__main__.py` | `v2r/render/revise.py` | `render.revise.run(args.change, options, args.cutlist, args.work)`; `ReviseError` printed as `v2r revise: ...` to stderr | WIRED |
| `revise.py` | `check.py` | `read_cutlist`, `schema_problems`, `time_problems`, `clips_problems`, `read_manifest`, `report`, closing `check.check(new_path, ...)` | WIRED |
| `revise.py` | `settings.py` | `RECIPES`, `DEFAULT_RECIPE`, `SHAPES`, `REVISE_*`, `MAX_SEGMENTS`, `MIN_REEL_SECONDS` | WIRED |
| `EDITOR.md` | `v2r` command line | Handbook guard test checks every named command exists, `revise` included | WIRED |
| EDITOR.md recipe sentence | `settings.RECIPES` | `test_editor_handbook.py` keeps them in step | WIRED |

### Data-Flow Trace (Level 4)

Not applicable beyond the lists: revise reads real cut lists and the real manifest (for `longer`) and writes real files; the chain test proves the written lists render.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| revise, check, handbook guards and the rendered follow-up chain | `uv run pytest tests/test_revise.py tests/test_revise_chain.py tests/test_cutlist_check.py tests/test_editor_handbook.py -q` | 523 passed in 47.71 s | PASS |

### Probe Execution

Step 7c: SKIPPED. No probe is declared by the plans.

### Requirements Coverage

Every ID in the phase's PLAN frontmatter (`07-01` to `07-09`) appears in `.planning/REQUIREMENTS.md`, and every REQUIREMENTS.md CONV ID is claimed by at least one plan. No orphans.

| Requirement | Source plans | Description | Status | Evidence |
|-------------|--------------|-------------|--------|----------|
| CONV-01 | 07-01, 07-06, 07-07, 07-09 | Brief straight away, four numbered questions with defaults, left out if answered, skipped on "just make it", no sound question | SATISFIED | EDITOR.md line 39; rehearsals; phone test (zero questions because standing answers covered them) |
| CONV-02 | 07-06, 07-07, 07-09 | At most one further question after looking | SATISFIED | EDITOR.md line 39 |
| CONV-03 | 07-06, 07-07, 07-09 | One line and a time estimate, then silence | SATISFIED | EDITOR.md; phone test |
| CONV-04 | 07-06, 07-07, 07-09 | Reply: video, at most two lines, three fitted follow-ups, clips by content, no track | SATISFIED | EDITOR.md reply paragraph and Sound paragraph; rehearsals (see caveat 2) |
| CONV-05 | 07-01 to 07-05, 07-09 | revise applies one named change as a new numbered list, tests prove only its own fields change | SATISFIED | Criterion 3 table above |
| CONV-06 | 07-02 to 07-06, 07-09 | Plain-English errors with a next step; work folder gone means ask for clips again | SATISFIED | WORK_GONE; EDITOR.md error paragraph |
| CONV-07 | 07-01, 07-09 | Whole conversation works from a phone on the branch | SATISFIED | Phone test, approved (human) |

REQUIREMENTS.md marks CONV-01 to CONV-07 `[x]` and the traceability row "Complete"; the reworded text (no music, "mute it") matches Stage 18 as D-19 required.

### Decisions Honored (07-CONTEXT.md)

D-01 to D-05 (brief, leave-out rule, estimate rule, reply, errors): present in EDITOR.md. D-06 (new numbered file, never render): confirmed in code and tests. D-07 (shorter names shots, trims from the end, never under the floor, drops from the end of the named list, never the first shot): `shorter_frames` and its tests. D-08 (longer, ceiling is clip end, next shot of same clip, recipe longest, photo exempt): `ceiling_frames`. D-09 to D-11 (reorder, drop, sound, canvas, cover follows): `follow_cover`, tests. D-12 (shots by number, clips by letter, plain refusal of unknown ones): `parse_shot`, `no_shot`. D-13 (tests prove only own fields change): confirmed. D-14 to D-16 (recipe field, floors/ceilings in settings, check notes and never refuses, photo exempt from ceiling): confirmed in schema, settings and check. D-17 and D-18 (user's section, cap raised to 1,800 with a decisions line, no Mac-only switches): confirmed. D-19 and D-20 (requirements reworded, Decide box closed in decisions.md and CLAUDE.md): confirmed. D-21 (phone test with shorter, mute it, wide version, timed): done, 7 min 33 s.

### Regression Check

The prior verifications (Stages 14, 15, 16, 17) are all `passed`. The changed test files in this phase (`test_cutlist_check.py`, `test_editor_handbook.py`) run green, including Stage 16's check suite and Stage 17's handbook guards, within the 523 passed. `docs/field-guide.html` is untouched on the branch. No regressions found.

### Anti-Patterns Found

None. No TBD, FIXME, XXX, TODO or HACK in `v2r/render/revise.py`, `v2r/render/check.py`, `v2r/__main__.py`, `v2r/settings.py`, the schema, README.md, EDITOR.md or the revise tests. No stubs: every handler writes real data. The working tree has only the untracked `.gsd/` folder; no media or private folders are tracked in the branch diff.

### Caveats for the user (not gaps, no status change)

1. **The phone test did not show the brief's questions.** The Project's Reel style held standing answers to all four, so zero questions were asked. The questions themselves, the "just make it" skip and the leave-out rule were exercised in the nine rehearsals instead, and the zero-question result is the handbook's own rule. If you want the questions seen on a phone once, it needs a Project with no standing answers (Stage 21 saved preferences will make that rarer).
2. **The reply's line count and its three follow-ups were not recorded on the phone**, and the "mute it" reply ran to three paragraphs over the two-line limit. The two-line limit and the three fitted follow-ups are in the handbook and were judged in rehearsal; this is on your list for the handbook-shortening review (07-09-SUMMARY.md, decisions line dated 2026-11-04).
3. **One false start on the phone**: a trim was first run from an older list and redone from the list the reel was rendered from. The handbook says "the newest cut list"; wording like "the list the last reel was rendered from" is on the shortening-review list. Nothing was lost; the earlier list is never overwritten.
4. A standing Reel style line about sound outranked the handbook (by design: Reel style outranks the handbook; recorded in rehearsal findings and decisions).

### Human Verification Required

None outstanding. Given already: nine rehearsals approved (07-07-SUMMARY.md) and the phone test approved on commit a875e1b (07-09-SUMMARY.md, docs/phone-limits.md row 19).

### Gaps Summary

No gaps. Criterion 3 (the one code can prove) is proved by tests that diff whole lists, both shapes, plus a rendered end-to-end chain. The conversation criteria rest on the handbook text, which the guard tests keep in step with the code, and on the user's recorded approvals. Nothing merges to main until you say so.

---

_Verified: 2026-11-04_
_Verifier: Claude (gsd-verifier)_
