---
phase: 02-stage-14-normalize
verified: 2026-10-14T00:00:00Z
status: passed
score: 5/5 roadmap success criteria verified (all plan truths verified; 2 backstop truths confirmed by the verifier's own runs)
behavior_unverified: 0
overrides_applied: 0
re_verification: false
flags:
  - "judgment-tier prohibition (plan 02-01: no colour look, filter, sharpening, stabilising, crop or speed change beyond plain conversion): NON-AUTHORITATIVE verifier judgment = held (filter lists checked, see below) and the user's phone look agreed; human review still welcome, not blocking"
gaps: []
deferred: []
human_verification: []
---

# Phase 2: Stage 14 – Normalize Verification Report

**Phase Goal:** Any clip or photo she shoots becomes one working format, upright, 30 fps and in ordinary colour, with a manifest naming every clip.
**Verified:** 2026-10-14
**Status:** passed
**Re-verification:** No, initial verification
**Branch / HEAD:** `stage-14-normalize` at f7b4667 (e520806 and after)

The goal is achieved in the code. The full suite passes (130 tests, run by me on this Mac, FFmpeg 8.0.1). I also ran my own end-to-end checks with generated clips, and the user's phone test of 2026-10-14 (sandbox FFmpeg 6.1.1) supplies the human evidence for how it looks and sounds.

## Goal Achievement

### Roadmap success criteria

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `python -m v2r normalize` on sideways, 60 fps, HDR and silent clips and photos gives upright, constant 30 fps, naturally coloured working copies with sound on every one | VERIFIED | `v2r/normalize.py` `video_command`/`video_chain`/`audio_chain`/`photo_command`. My run (tall and wide) with a 60 fps clip, a silent 60 fps clip, a clip stored sideways (rotation 90, 640x360 stored, came out 360x640) and a JPEG: all 30/1 fps, H.264, AAC 48 kHz stereo, silent track added where none existed (`sound_added` true). Tests: `test_working_60fps_becomes_constant_30`, `test_working_uneven_timing_becomes_constant_30`, `test_working_silent_clip_gets_silence`, `test_upright_sideways_clip_marker` (marker lands in the right corner for 90 and -90, both shapes), `test_hdr_hlg_clip_is_tone_mapped_not_relabelled` (luma drops, bt709 tags), `test_hdr_pq_and_gamut_only_convert`, `test_photo_*`. Human evidence: on the phone the HDR clip's colour and sound looked right and the sideways clip came back upright. |
| 2 | work/manifest.json names every clip A, B, C in order, with original facts (slow-motion flagged), working copy and conversion time | VERIFIED | Manifest layout documented and built in `normalize()`, `convert_one()`, `skipped_entry()`. `test_facts_full_fact_sheet` checks every fact field in both shapes; `test_manifest_letters_follow_given_order`, `test_manifest_same_file_twice_gets_two_letters`, `test_manifest_letters_beyond_z`; `slow_motion` via `frame_facts` and `test_slow_motion_120fps_flagged_and_real_time` (flagged, real-time length kept) and `test_slow_motion_60fps_not_flagged`; `convert_seconds` on each done entry. The manifest is written atomically after every file (`write_manifest`, `os.replace`) and ends `finished: true`. My run: letters A..E in given order, skipped files keep their letters. |
| 3 | A file too large or unreadable gets one plain-English sentence and the others still convert | VERIFIED | `convert_one` raises `Refused(sentence)` (size check by bytes before opening, probe failure, missing file, inside work folder); `normalize()` catches per file and carries on; CLI exits 0 if any converted, 1 if none. Tests: `test_refuse_oversized_file_others_convert`, `test_unreadable_text_empty_and_audio_only_files`, `test_refuse_missing_file`, `test_manifest_all_skipped_exit_1`, `test_refuse_no_files_usage_error`, `test_refuse_whole_run_out_of_room_sentence`. My run: a junk `.mov` got "The fourth file, bad.mov, could not be read as a video or a photo." and the files after it converted. |
| 4 | No original file is ever written to | VERIFIED | FFmpeg always writes to a `.part` name in the work folder; originals are only read. `clear_last_job` never deletes an input; an input inside the work folder is skipped. Tests: `test_original_files_unchanged_hash_and_mtime`, `test_original_read_only_inputs_convert`, `test_original_inside_work_folder_*`, `test_original_clear_keeps_other_files`. My own check: SHA-256 of every input identical after tall and wide runs, after a run killed part-way, and after two simultaneous runs into one folder. |
| 5 | Tests pass using generated clips, including sideways, 60 fps, no sound and HDR | VERIFIED | `tests/media.py` generates every clip with FFmpeg (no committed media). `uv run pytest -q`: 130 passed. Sideways, 60 fps, silent and HLG/PQ/gamut-only clips are all parametrised over tall and wide. |

**Score:** 5/5 roadmap criteria verified. No truth is behaviour-unverified: the state and ordering invariants (atomic manifest, no `.part` left after a failure, letters kept by skipped files, the second run replacing only the last job's files) each have a named test, and I exercised the interruption and concurrency cases myself (below).

### Plan must-haves (merged, all eight plans)

| Plan | Truths | Status | Notes |
|------|--------|--------|-------|
| 02-01 | CLI, working format, sideways once, 60 fps and uneven timing, silent clip, manifest fields and atomic write, progress line, replace-last-job, edge cases (same file twice, awkward names, ordering, size cap and odd sizes, one-frame clip) | VERIFIED | Tests named in the table above plus `test_working_size_table` (13 cases incl. exactly at the cap, 641x361 to 640x360, never enlarged), `test_facts_awkward_file_name`, `test_facts_one_frame_clip`, `test_manifest_second_run_replaces_last_job`, `test_clear_last_job_never_touches_an_input_or_other_files`, `test_tracer_shape_is_required` (argparse exit 2, no default). |
| 02-02 | Doctor lists every new filter and decoder; `missing_ffmpeg_features()`; Stage 14 lines in decisions.md; CLAUDE.md names the decisions; normalize.log ignored | VERIFIED | `v2r/doctor.py` has `FILTERS` (17 names) and `DECODERS`; `missing_ffmpeg_features()` reads them at call time with no network. Tests `test_doctor_lists_every_normalize_piece`, `test_doctor_reports_decoders`, `test_doctor_missing_features_*`. `docs/decisions.md` carries six dated 2026-10-13 Stage 14 lines naming no person or account. CLAUDE.md "Settled so far" and the Stack line updated. `git check-ignore normalize.log` confirms it is ignored. |
| 02-03 | Pillow and pillow-heif checked, pinned, in requirements.txt and docs/licenses.md | VERIFIED | `requirements.txt` pins `pillow==12.3.0` and `pillow-heif==1.8.1` (held below 1.9); `docs/licenses.md` lists both with licence, purpose, source and the LGPL/GPL note that bundled libraries are not redistributed. The user approved them (summary) and the phone installed them (doctor/phone test: photo converted). |
| 02-04 | HDR tone-mapped not relabelled; colour facts passed explicitly; operator/peak from settings; notes and Dolby Vision note; fallback sentence; 120 fps flagged | VERIFIED | `video_chain` reads `settings.TONEMAP`, `TONEMAP_NPL`, `TONEMAP_NPL_PQ` at call time; `test_hdr_chain_reads_settings`, `test_hdr_colour_notes`, `test_fallback_colour_when_tonemap_fails` (status done, `colour_converted` false, exact D-13 sentence). Settings value: hable at 203, matching the user's pick. |
| 02-05 | Size refusal wording, unreadable wording, skipped keeps letter, exit codes, out-of-room stop, attachment count not enforced, originals untouched, doctor start-up check, no location/device tags | VERIFIED | `check_ffmpeg()` calls `doctor.missing_ffmpeg_features()` before touching the work folder (`test_doctor_missing_feature_stops_run`); `test_doctor_graph_filters_all_listed` ties every graph filter to `doctor.FILTERS`; `test_manifest_attachment_count_not_enforced`; `test_original_no_location_or_device_tags` (encoder runs with `-map_metadata -1`). Backstop truths below. |
| 02-06 | Photos: still clip of `PHOTO_SECONDS`, upright full-size JPEG copy without EXIF, orientation applied once, `shot_at`, Pillow before ffprobe, lazy import, speed, edge cases | VERIFIED | `read_photo`, `photo_graph` (decode and scale once, `loop` filter), `photo_command`. Tests `test_photo_jpeg_orientation_upright_copy_and_still_clip`, `test_photo_heic_opens`, `test_photo_png_with_transparency`, `test_photo_icc_profile_converted`, `test_photo_libraries_imported_lazily`, `test_photo_library_missing_sentence`, `test_photo_copy_has_no_exif_location`, `test_photo_still_is_fast`, `test_photo_sizes_never_enlarged`, `test_photo_mixed_with_clips_keeps_order`. My run: a 400x300 JPEG gave a 4.0 s, 30/1 fps, 400x300 still (not enlarged) in a wide job, plus `A-photo.jpg`, with silent AAC track. HEIC is read with pillow-heif, so the sandbox's FFmpeg never sees it. |
| 02-07 | Real-footage check, tone-map strips, pick recorded, nothing from fixtures/work committed | VERIFIED | `work/check-table.md` (146 lines, both shapes), `work/strips/`, `work/check-tall`, `work/check-wide` exist locally and are gitignored. `settings.py` holds `TONEMAP = "hable"`, `TONEMAP_NPL = 203`, with the reasoning comment; decisions.md line recorded. I scanned every fixture media file name against all tracked content at HEAD and the whole non-.planning diff: no hits. The one part of the plan still without data (a timing row for sideways clips above 30 fps) is an optional measurement, not a requirement. |
| 02-08 | Handbook step in the user's words; pre-push checks; pushed only on the user's say; phone test in both shapes plus a reel | VERIFIED (human evidence) | `EDITOR.md` step 3 starts normalize in the background with nohup and reads `normalize.log` until "normalize finished"; commit d69fca3 is "text by the user". Step 4 (joins the working copies, skipping skipped letters) was added at the user's explicit instruction after the phone test found the join failed on a photo's original; that fix is in deeefd4. The user reported on 2026-10-14: doctor on the phone's FFmpeg 6.1.1 shows every filter and decoder available, pillow installed, all four test files converted in tall and in wide, the bright HDR clip's colour and sound were right, the sideways clip came back upright, a tall reel and a wide reel were made from the phone on the branch (which satisfies the CLAUDE.md merge rule). Commit history for the branch: no attribution trailers, no media, no e-mail addresses in any committed file. |

### Backstop truths (plan 02-05), confirmed by the verifier's own runs

| Truth | Status | Evidence |
|-------|--------|----------|
| A run stopped part-way leaves every original unchanged | VERIFIED | I started a normalize of a 40 s 1080p60 clip plus a photo and killed it (SIGKILL) after 3 s. Result: only `A.part.mp4` and a parsing `manifest.json` with `finished: false` remained in the work folder; both originals' SHA-256 and mtime were identical. The next run clears `.part` files (`LAST_JOB_FILES` regex covers them). |
| Two simultaneous runs into one folder are unsupported, but a second run replaces lettered files and never touches an original | VERIFIED | I ran a tall and a wide run at the same time into one folder. They collided as the plan says (some files skipped in each run, manifest still parsed), and every original was byte-identical afterwards. Sequential replacement is covered by `test_manifest_second_run_replaces_last_job`. |

### Prohibitions

| Prohibition | Tier | Status | Evidence |
|-------------|------|--------|----------|
| No colour look, filter, sharpening, stabilising, crop or speed change beyond plain conversion | judgment | HELD (non-authoritative verifier judgment, flagged for optional human review) | I printed every filter graph normalize builds. Ordinary clip: `fps, scale, format, setsar` plus `aresample, apad`. HDR: those plus `zscale` and `tonemap` (the colour conversion the requirement asks for; `desat=0`). Photo: `scale, format, setsar, loop, setpts`. No `crop`, `eq`, `unsharp`, `deshake`, `setpts` speed change on clips, or colour-look filter anywhere. The user also judged the colour natural on the phone. |
| MUST NOT drop a file silently | test | VERIFIED | Every file gets a letter and a manifest entry, done or skipped with a sentence printed in the log; `test_refuse_*`, `test_manifest_all_skipped_exit_1`, `test_unreadable_text_empty_and_audio_only_files`. |
| MUST NOT carry GPS or device make/model into copies or manifest | test | VERIFIED | `test_original_no_location_or_device_tags`, `test_photo_copy_has_no_exif_location` (the photo copy is saved from pixels only; clips use `-map_metadata -1`). |
| MUST NOT make her change a setting or use another app for photos (HEIC read as it arrives) | judgment | HELD | `read_photo` registers `pillow_heif` so HEIC opens directly; `test_photo_heic_opens`; the photo in the user's phone test converted with no workaround. |
| MUST NOT commit or push media, fixture names, names or accounts, e-mail addresses, attribution trailers | test | VERIFIED | Diff of `main..HEAD` has no media files and nothing under fixtures/ or work/; no trailers in any commit message; no fixture file name in any tracked file; no e-mail address or secret in the added source/doc lines. |

### Required Artifacts (levels 1 to 3, data flow)

| Artifact | Status | Details |
|----------|--------|---------|
| `v2r/normalize.py` (630 lines) | VERIFIED | Real implementation, no stubs. Data flows from ffprobe/Pillow to the manifest; the manifest is read nowhere yet because Stage 15 and 16 consume it later. |
| `v2r/settings.py` | VERIFIED | `WORKING_SIZE`, `PHOTO_SECONDS`, `X264_*`, `AUDIO_RATE`, `TONEMAP*`, `SLOW_MOTION_MIN_FPS`, `STEADY_TOLERANCE`, `ERROR_DETAIL_CHARS`, limits. All read at call time. |
| `v2r/__main__.py` | VERIFIED | `normalize` sub-command, `--shape` required with no default, `files` nargs+; return code from the manifest. |
| `v2r/doctor.py` | VERIFIED | Wired to `normalize.check_ffmpeg()`. |
| `tests/media.py`, `tests/test_normalize.py`, `tests/test_doctor.py` | VERIFIED | Generated media only. |
| `docs/licenses.md`, `docs/decisions.md`, `requirements.txt`, `CLAUDE.md`, `EDITOR.md` | VERIFIED | As described above. |

### Key links

| From | To | Status |
|------|----|--------|
| `__main__.py` | `normalize.normalize(args.files, args.shape)` | WIRED |
| `normalize.py` | `settings.WORKING_SIZE`, `settings.TONEMAP*`, `settings.MAX_ATTACHMENT_BYTES` | WIRED (call-time reads) |
| `normalize.py` | `doctor.missing_ffmpeg_features()` via `check_ffmpeg()` | WIRED |
| `normalize.py write_manifest` | `os.replace` of `manifest.json.tmp` | WIRED |
| `video_chain` | `hdr_kind()` chooses the HDR or ordinary chain | WIRED |
| `convert_one` | `read_photo` before `probe()` | WIRED |
| skill / EDITOR.md | branch `stage-14-normalize` | WIRED (phone test ran from the branch) |

### Requirements coverage

All eight phase IDs appear in plan frontmatter (02-01: NORM-01, 02, 05; 02-02: NORM-08; 02-03: NORM-03; 02-04: NORM-02, 04; 02-05: NORM-05, 06, 07, 08; 02-06: NORM-03; 02-07: NORM-02; 02-08: NORM-02, 03, 04, 08). No orphaned requirement.

| Requirement | Status | Evidence |
|-------------|--------|----------|
| NORM-01 facts via ffprobe, originals unchanged | SATISFIED (delivered; the unticked box is only bookkeeping) | `probe`, `packet_times`, `video_facts` produce length, stored and upright size, rotation, fps and steadiness, HDR kind, Dolby Vision, sound, shot_at. `test_facts_*` (full fact sheet, frame timing, hdr table, shot_at, awkward names, one-frame clip) pass in both shapes; originals untouched by hash. The executor left the box unticked in plan 02-01 because HDR and photos were not in yet; they landed in plans 04 to 06. |
| NORM-02 one format: upright, size by shape, 30 fps, tone-mapped, H.264, AAC stereo 48 kHz, silence added | SATISFIED | See criterion 1 and `test_working_size_table`. |
| NORM-03 photo becomes a still clip, full-resolution photo recorded | SATISFIED | See plan 02-06. |
| NORM-04 120/240 fps flagged, converted at normal speed | SATISFIED | `slow_motion` flag and note; `test_slow_motion_120fps_flagged_and_real_time`. On the phone this path never fires (attachments arrive pre-rendered at a steady 30 fps), which is expected and recorded; the code path is covered by the generated-clip tests. |
| NORM-05 letters A, B, C; manifest lists facts, copy, conversion time | SATISFIED | See criterion 2. |
| NORM-06 over-limit or unreadable file gets one sentence, others go on | SATISFIED | See criterion 3. |
| NORM-07 no original written to | SATISFIED | See criterion 4. |
| NORM-08 only FFmpeg pieces doctor shows; tests use generated clips | SATISFIED | `check_ffmpeg`, `test_doctor_graph_filters_all_listed`, `test_doctor_photo_graph_filters_listed`; phone doctor showed all pieces available. |

### Anti-patterns

None blocking. No TBD, FIXME, XXX, TODO or HACK in any line added by the phase to source, tests, EDITOR.md or docs. Info only: `desat=0` and `flags=bicubic` are fixed inside the filter strings rather than in settings.py (they are not user-tuned limits; CLAUDE.md asks for numbers that control behaviour, which all live in settings.py). The broad `except Exception` in `normalize()` is deliberate and commented (nothing may stop the other files).

### Probe execution

No `probe-*.sh` scripts are declared by the phase or exist in `scripts/`: skipped.

### Deferred items

None.

## Human verification

None outstanding. The look and sound items (HDR colour, sound sync, upright result, photo, both reels) were covered by the user's phone test on 2026-10-14 and are cited above as human evidence.

## Housekeeping for the orchestrator (not gaps)

1. `.planning/REQUIREMENTS.md`: tick the NORM-01 checkbox, and change the single range row "NORM-01 to NORM-08 | Phase 2 | Pending" to Complete. NORM-01 is delivered.
2. `02-VALIDATION.md` still says `status: draft`, `nyquist_compliant: false`; `/gsd-validate-phase` could set it.
3. Optional leftover from plan 02-07: the "sideways clips above 30 fps" timing row has no data, and the phone's conversion seconds were not relayed. Neither is a requirement.
4. The 120/240 fps slow-motion flag cannot be exercised from a phone attachment; worth a line in the Stage 15/16 notes.
5. Side effect of my checks: one of my spot-checks wrote into the real, gitignored `work/` folder, so its lettered files (`A.mp4`, `A-photo.jpg`, `B.mp4`) and `manifest.json` there were replaced by my small generated clips' results. Join outputs and `check-*` folders were left alone. Nothing tracked changed (`git status` shows only the untracked `.gsd/`).
6. Merge note: per CLAUDE.md, a reel has been made from a phone on this branch (both shapes), so the merge condition is met; shipping is the user's call. Remind them the guide differs from what was built in the six Stage 14 decisions recorded in docs/decisions.md.

---

_Verified: 2026-10-14_
_Verifier: Claude (gsd-verifier)_
