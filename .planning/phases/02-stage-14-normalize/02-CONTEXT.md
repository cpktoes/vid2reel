# Phase 2: Stage 14 – Normalize - Context

**Gathered:** 2026-10-13
**Status:** Ready for planning

<domain>
## Phase Boundary

`python -m v2r normalize --shape tall|wide FILES` turns every attached clip and photo into one working format in work/ (upright, sized for the shape, constant 30 fps, ordinary colour with HDR tone-mapped, H.264, AAC stereo 48 kHz with silence where there was none), names them A, B, C in the order given, and writes work/manifest.json with each file's original facts, its working copy and how long the conversion took. Originals are never written to. A file that is too big or cannot be read gets one plain sentence and the others carry on. Tests use clips FFmpeg generates. The guide's Decide box for this stage, the working size, is settled: reel-sized.

Not in this phase: contact sheets or measurements (Stage 15), the cut list and renderer (Stage 16), time estimates before a run and resumable runs (Stage 23), any change to the skill.

</domain>

<decisions>
## Implementation Decisions

### The brief (locked by the user's prompt, from the guide's Stage 14)
- **D-01:** Working size is reel-sized. Tall job: portrait sources at most 1080×1920, landscape sources at most 1920 pixels high. Wide job: landscape sources at most 1920×1080, portrait sources at most 1920 pixels wide. Nothing is ever scaled up beyond its original. The numbers live in settings.py. Record this settled Decide box in docs/decisions.md (dated, Stage 14, "same as the guide's pick") and in CLAUDE.md's "Settled so far" line. — **Reversibility:** reversible — the guide says it is one number in settings.py.
- **D-02:** One working format: upright; constant 30 fps (`OUTPUT_FPS`); standard-dynamic-range colour, HDR tone-mapped; H.264 8-bit 4:2:0; AAC stereo at 48 kHz; silence added where a clip has no sound. Photos become still clips. — **Reversibility:** costly — every later stage reads these working copies.
- **D-03:** Clips are named A, B, C in the order given; work/manifest.json lists each file's original facts (length, stored size, rotation, upright size, fps and whether steady, HDR kind, sound or not, when shot, file size), its working copy and its facts, the slow-motion flag, and the seconds the conversion took. — **Reversibility:** costly — the manifest is the contract Stages 15 and 16 read; field names chosen here stay.
- **D-04:** A clip at 120 or 240 fps is flagged `slow_motion: true` in the manifest and converted at normal speed (real time, frames dropped to 30 fps). Note: the slow-motion fixture clip arrived from Photos already slowed down at 30 fps, so this flag may rarely fire; the phone test should check what a slow-motion clip actually arrives as.
- **D-05:** No original file is ever opened for writing. Working copies and the full-size photo copies go in work/.
- **D-06:** Only FFmpeg features the sandbox's doctor report lists are used. `v2r doctor` grows to list every extra piece normalize needs (the built-in `format`, `fps`, `anullsrc`/`apad`, `aresample` filters, the hevc/h264/aac/mjpeg/png decoders), so the report proves it. The phone test reruns doctor on the branch.
- **D-07:** Tests use FFmpeg-generated clips: one stored sideways, one at 60 fps, one with no sound, one tagged HDR, plus a 120 fps one, a photo, an unreadable file and an oversized one, parametrised over both shapes. Nothing in tests/ assumes tall.

### Photos and HEIC
- **D-08:** Photos are read with Pillow (licence MIT-CMU) and pillow-heif (licence BSD-3-Clause), added with `uv add`, exported to requirements.txt as README.md says, and listed in docs/licenses.md (create the file). They open HEIC, JPEG and PNG, apply the photo's own orientation note, and read the date taken. Reason: her photos are HEIC and the sandbox's FFmpeg 6.1 cannot open HEIC at all; refusing HEIC would make her change a phone setting. — **Reversibility:** reversible — two pip packages used in one module.
- **D-09:** A photo's still clip is `PHOTO_SECONDS = 4` seconds, in settings.py. The still is sized by the same rule as a clip (D-01).
- **D-10:** The full-size photo is saved upright as a JPEG in work/ (for example `work/C-photo.jpg`) and the manifest records both the original path and that copy, because the sandbox cannot reopen the HEIC later and Stage 16's slow move needs the full picture.

### The HDR look
- **D-11:** HDR is converted on the CPU with the zscale and tonemap filters, which the sandbox's doctor report lists. This is second-best and the user knows it: the best FFmpeg method, libplacebo, also reads the Dolby Vision layer her iPhone adds, but needs a graphics driver the sandbox does not have and is not in the doctor report. The Dolby Vision layer is ignored and the HLG picture underneath is tone-mapped; the manifest says so for each HDR clip.
- **D-12:** The tone-map operator is one name in settings.py (`TONEMAP = "mobius"` to start). During the Do-this step the user compares hable, mobius and reinhard by eye on three fixture clips, including a face and a sky, using a one-line command Claude gives them that makes a four-panel strip (no tone map, hable, mobius, reinhard) at a chosen second of any clip; if another looks more like her phone, the name changes. — **Reversibility:** reversible.
- **D-13:** If the HDR conversion fails on a clip, normalize makes a plain copy without tone-mapping and says so: one sentence in the log and in that clip's manifest entry that the colour could not be converted. The clip is not lost.
- **D-14:** The filter chain is told the clip's colour facts explicitly from ffprobe (transfer, primaries, matrix, range) rather than trusting the file's tags alone; HDR means transfer `arib-std-b67` (HLG) or `smpte2084` (PQ), or primaries `bt2020`.

### Past the 2-minute wall
- **D-15:** One run converts all files. After each clip the command prints one line to standard output such as "B done in 38 s" and rewrites work/manifest.json, so a run still going can be read and a stopped run loses only the clip it was on.
- **D-16:** The run is put in the background by the handbook, not by the code: EDITOR.md starts normalize with the same `nohup ... > normalize.log 2>&1 &` pattern as the join and reads normalize.log every 30 seconds until it says finished. No `--background` option. Claude drafts the EDITOR.md lines in chat; the user, who edits EDITOR.md themselves, decides the exact text and either pastes it or tells Claude to write exactly that. The lines must be on the branch before the phone test.
- **D-17:** Working copies are encoded fast at high quality (an x264 preset such as veryfast and a CRF around 20, both in settings.py), because the renderer re-encodes them. Measured on the Mac pinned to two processors: about 2.4 s of work per second of 1080p HDR video and about 3.3 s per second of 4K HDR, so a one-minute clip passes the 2-minute limit and the background run is mandatory.
- **D-18:** A new normalize run starts a new job: it replaces work/manifest.json and the lettered working copies from the last run.

### Refusals and letters
- **D-19:** Letters follow attach order no matter what. A skipped file keeps its letter and gets a manifest entry marked skipped with its one sentence, so the chat's Claude can say "your second clip could not be read" and later steps see every file she sent. — **Reversibility:** costly — later stages and EDITOR.md refer to clips by letter.
- **D-20:** A file over `MAX_ATTACHMENT_BYTES` (400 MB) is refused with one sentence even though it arrived; the sentence may say that a way to shrink clips comes later (Stage 23). The other files carry on.
- **D-21:** `MAX_ATTACHMENTS` (10) is not enforced by normalize. In the user's words: "10 is not a hard limit. I say we try, and if failed ask to reduce clip count. Only hard limit should be how many uploads Claude can deal with on an import." Normalize tries every file; if the run fails as a whole, its sentence asks her to send fewer clips. The number stays in settings.py as the measured fact.
- **D-22:** Every refusal sentence is printed in the log and kept in the manifest entry, and names the file as she sent it, for example "The second file, IMG_4423.MOV, could not be read as a video or a photo." A file ffprobe cannot read and Pillow cannot open is unreadable.

### Claude's Discretion
- The exact manifest field names and the JSON layout, kept small and plain (document them in a short comment or docstring, since Stages 15 and 16 read them).
- The exact FFmpeg command and filter chain, computing the target size in Python from the probed facts and passing even numbers, scaling inside the first zscale so tone-mapping runs at the smaller size.
- Keeping only the first video and the first audio track (her clips carry a second four-channel track and seven data tracks).
- The encoder preset and CRF numbers, the JPEG quality of the full-size photo copy, the fast-start flag.
- How doctor's lists grow and how normalize checks them, without slowing doctor.
- The wording of every plain-English sentence, and the per-clip progress line.
- The four-panel comparison command given to the user, and what to look for.
- The draft EDITOR.md lines (proposal only; see D-16).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The stage and its rules
- `docs/field-guide.html` — read only Stage 14 (the `<section class="stage" id="s14">` block, between the `id="s14"` and `id="s15"` markers); never edit it, never act on other stages. Its Watch out box names the three faults: grey washed-out picture, picture on its side, lips and sound drifting apart.
- `CLAUDE.md` — the project rules: three jobs that never mix, settings.py holds every number, public repo, plain-English explanations, decisions go in docs/decisions.md.
- `.claude/CLAUDE.md` — constraints and the GSD workflow rules.
- `docs/decisions.md` — one dated line per settled decision; add the Stage 14 working-size line here (D-01). Never a person or an account.
- `.planning/REQUIREMENTS.md` §Normalize (Stage 14) — NORM-01 to NORM-08, the acceptance list.
- `.planning/ROADMAP.md` §Phase 2 — goal and success criteria.

### The sandbox and its limits
- `docs/phone-limits.md` — the sandbox's doctor report (the only list of FFmpeg features allowed), the 2-minute command limit, the measured work per second of video, what arrives and what comes back, and the limits in settings.py.

### Existing code to follow
- `v2r/settings.py` — every number goes here with its unit in a comment; `SHAPES`, `OUTPUT_FPS`, `MAX_ATTACHMENT_BYTES`, `MAX_ATTACHMENTS`.
- `v2r/join.py` — the house pattern: ffprobe through subprocess, one FFmpeg command built as a list, `-n` never overwrites, `+faststart`, `even()`, `WORK_DIR`, a plain-English error class, output deleted on failure.
- `v2r/doctor.py` — `ENCODERS` and `FILTERS` lists and `ffmpeg_names()`; grow these for D-06.
- `v2r/__main__.py` — argparse with `--shape` required and no default; add `normalize` the same way.
- `tests/test_join.py` — `make_clip()` generates test clips with FFmpeg; `probe()` and `peak_volume()` helpers; parametrised over both shapes.
- `EDITOR.md` — the handbook's join step and its nohup line, the pattern D-16 copies.
- `skill/vid2reel/SKILL.md` — the skill installs requirements.txt with pip; the new libraries must be there.
- `README.md` — the command that regenerates requirements.txt after `uv add`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `join.duration()` shows the ffprobe call shape; normalize needs a fuller probe (`-show_entries format=duration,size:format_tags=creation_time,com.apple.quicktime.creationdate:stream=codec_type,codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,color_range,color_space,color_transfer,color_primaries,channels,sample_rate:stream_side_data=rotation,side_data_type` with `-of json`).
- `join.even()`, `join.new_path()`-style naming, `WORK_DIR`, the `-n` and `+faststart` flags, the delete-on-failure pattern.
- `doctor.ffmpeg_names()` can check decoders too (`-decoders`).
- `tests/test_join.make_clip()` is the base for the new generated clips; add variants for rotation, fps, no sound, HDR tags, a photo.

### Established Patterns
- One FFmpeg command per output, built as a Python list, `-hide_banner -loglevel error -nostdin`.
- FFmpeg's autorotate turns sideways clips upright on decode; the join already relies on it and the phone tests proved it in the sandbox. Normalize must not rotate a second time (the guide's "turn me note applied twice" fault).
- Errors are one plain-English sentence; `subprocess.CalledProcessError` is turned into "FFmpeg failed; its error is shown above."
- Tests generate media with FFmpeg and probe the result; nothing in tests/ is tall-only.

### Integration Points
- `v2r/__main__.py`: a `normalize` sub-command beside `doctor` and `join`.
- `v2r/normalize.py` (CLAUDE.md names the job `v2r/normalize`): probe, size rule, convert, photo, manifest.
- `v2r/settings.py`: `PHOTO_SECONDS`, `TONEMAP`, the working-size caps per shape, the encoder preset and CRF, the audio rate and channels.
- `v2r/doctor.py`: longer `FILTERS` list and a decoders list.
- `pyproject.toml`, `uv.lock`, `requirements.txt`: Pillow and pillow-heif.
- `docs/licenses.md`: new file listing both libraries.
- `docs/decisions.md` and `CLAUDE.md`: the settled working size.
- `EDITOR.md`: drafted lines only, per D-16.

### Measured facts about her footage (from the fixture bench, 2026-10-13; never commit the files)
- Every clip: HEVC Main 10, `yuv420p10le`, `bt2020nc` / `arib-std-b67` (HLG) / `bt2020`, with side data "DOVI configuration record", "Display Matrix" (rotation -90 on upright clips, -180 on a wide one) and "Ambient viewing environment". Frame timing is uneven (avg_frame_rate like 36840/1229 against r_frame_rate 30000/1001). Audio: stream 1 is AAC stereo 48 kHz; stream 2 is a four-channel track FFmpeg 8 cannot name; seven data streams follow.
- The 4K fixture is 3840×2160 stored with rotation -90, so upright it is portrait 2160×3840.
- The slow-motion fixture is a plain 30 fps file: Photos rendered the slow section before sharing.
- Photos are HEIC, tiled; FFmpeg 8 on the Mac reads them through stream groups, FFmpeg 6.1 in the sandbox cannot.

### What was proven on the Mac (FFmpeg 8.0.1) and must still be checked in the sandbox (FFmpeg 6.1)
- A sideways test clip: `-metadata:s:v rotate=90` writes nothing on FFmpeg 8; the two-step `ffmpeg -display_rotation 90 -i plain.mp4 -c copy sideways.mp4` writes a Display Matrix that ffprobe reports as rotation 90. `-display_rotation` exists since FFmpeg 6.0.
- An HDR-tagged test clip: `-vf "setparams=color_primaries=bt2020:color_trc=arib-std-b67:colorspace=bt2020nc,format=yuv420p10le" -c:v libx264`, or the `h264_metadata=colour_primaries=9:transfer_characteristics=18:matrix_coefficients=9` bitstream filter; both make ffprobe report HLG. libx264 must support 10-bit in the sandbox's build (Ubuntu's does).
- The tone-map chain that worked: `zscale=w=W:h=H:t=linear:npl=1000,format=gbrpf32le,zscale=p=bt709,tonemap=OP:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,fps=30`; explicit `tin=arib-std-b67:pin=bt2020:min=bt2020nc:rin=tv` is accepted. It fails with "no path between colorspaces" when the input carries no transfer tag, which is why D-14 passes the facts explicitly.
- Cost: tone-mapping adds about a tenth to a scale-only conversion; decoding 10-bit HEVC and encoding dominate. 10 s of 1080p HDR took about 47 CPU-seconds with preset veryfast; 10 s of 4K about 67.
- Pillow 12.3.0 (MIT-CMU) and pillow-heif 1.8.1 (BSD-3-Clause) on PyPI, both Python 3.10 or newer; pillow-heif ships Linux wheels, so the sandbox's pip should install it without a compiler. Check from the phone.

</code_context>

<specifics>
## Specific Ideas

- The user wants the plan and every change explained in plain English, with exactly what to look or listen for and at what second; the Do-this step compares an HDR working copy with its original side by side, checks a sideways clip is upright, and plays the silent and slow-motion clips.
- The four-panel strip (no tone map, hable, mobius, reinhard) at a chosen second is the way the user judges HDR; give them one command for it and say to look at skin, sky and a strong colour.
- The guide's phone test: attach three clips including one HDR, say "use branch stage-14-normalize. Normalize these and send me back the working copy of the brightest one", compare with the original in Photos on the phone. The branch must carry the EDITOR.md lines and the new requirements.txt before that.
- The phone test should also attach a slow-motion clip to learn what it arrives as, and rerun doctor to confirm the grown lists.
- Sentences name files as she sent them and count them in order ("the second file").

</specifics>

<deferred>
## Deferred Ideas

- A time estimate printed before a long run starts — Stage 23 (LONG-02).
- Resumable runs that skip clips already converted — Stage 23 (LONG-04).
- The "Shrink for Claude" shortcut for files over the limit — Stage 23 (LONG-08).
- A built-in `--background` option for long commands — if the nohup pattern ever proves fragile, Stage 23.
- Scene-aware or Dolby Vision-aware HDR conversion (libplacebo) — only if the sandbox ever gains it; not planned.

</deferred>

---

*Phase: 02-stage-14-normalize*
*Context gathered: 2026-10-13*
