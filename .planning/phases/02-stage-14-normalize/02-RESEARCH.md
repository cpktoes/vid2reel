# Phase 2: Stage 14 – Normalize - Research

**Researched:** 2026-10-13
**Domain:** FFmpeg 6.1 / ffprobe conversion pipeline in Python (video + HEIC/JPEG photos), CPU only, 2-minute command wall
**Confidence:** HIGH on the FFmpeg command shapes and the photo route (run this session on FFmpeg 6.1 and 8.0.1), MEDIUM on the HDR look (tone-map defaults are a measured recommendation, the user still judges by eye), MEDIUM on the sandbox's pip install of the two photo libraries (not testable from the Mac).

> How "verified" is meant here. The sandbox's real FFmpeg (Ubuntu 6.1.1) cannot be run from the Mac. To check "FFmpeg 6.1, not newer" I downloaded the static FFmpeg 6.1 and ffprobe 6.1 builds into the scratchpad (outside the repo) and ran every command below on them, and again on the Mac's FFmpeg 8.0.1 (the tests' FFmpeg). Tag `[VERIFIED: ffmpeg 6.1 + 8.0.1 run]` means both gave the result described. The Ubuntu build differs from that static build in packaging only (assumption A1); the sandbox's doctor report already proves it has `zscale`, `tonemap`, `libx264` and `aac`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**The brief (locked by the user's prompt, from the guide's Stage 14)**
- **D-01:** Working size is reel-sized. Tall job: portrait sources at most 1080×1920, landscape sources at most 1920 pixels high. Wide job: landscape sources at most 1920×1080, portrait sources at most 1920 pixels wide. Nothing is ever scaled up beyond its original. The numbers live in settings.py. Record this settled Decide box in docs/decisions.md (dated, Stage 14, "same as the guide's pick") and in CLAUDE.md's "Settled so far" line. — **Reversibility:** reversible — the guide says it is one number in settings.py.
- **D-02:** One working format: upright; constant 30 fps (`OUTPUT_FPS`); standard-dynamic-range colour, HDR tone-mapped; H.264 8-bit 4:2:0; AAC stereo at 48 kHz; silence added where a clip has no sound. Photos become still clips. — **Reversibility:** costly — every later stage reads these working copies.
- **D-03:** Clips are named A, B, C in the order given; work/manifest.json lists each file's original facts (length, stored size, rotation, upright size, fps and whether steady, HDR kind, sound or not, when shot, file size), its working copy and its facts, the slow-motion flag, and the seconds the conversion took. — **Reversibility:** costly — the manifest is the contract Stages 15 and 16 read; field names chosen here stay.
- **D-04:** A clip at 120 or 240 fps is flagged `slow_motion: true` in the manifest and converted at normal speed (real time, frames dropped to 30 fps). Note: the slow-motion fixture clip arrived from Photos already slowed down at 30 fps, so this flag may rarely fire; the phone test should check what a slow-motion clip actually arrives as.
- **D-05:** No original file is ever opened for writing. Working copies and the full-size photo copies go in work/.
- **D-06:** Only FFmpeg features the sandbox's doctor report lists are used. `v2r doctor` grows to list every extra piece normalize needs (the built-in `format`, `fps`, `anullsrc`/`apad`, `aresample` filters, the hevc/h264/aac/mjpeg/png decoders), so the report proves it. The phone test reruns doctor on the branch.
- **D-07:** Tests use FFmpeg-generated clips: one stored sideways, one at 60 fps, one with no sound, one tagged HDR, plus a 120 fps one, a photo, an unreadable file and an oversized one, parametrised over both shapes. Nothing in tests/ assumes tall.

**Photos and HEIC**
- **D-08:** Photos are read with Pillow (licence MIT-CMU) and pillow-heif (licence BSD-3-Clause), added with `uv add`, exported to requirements.txt as README.md says, and listed in docs/licenses.md (create the file). They open HEIC, JPEG and PNG, apply the photo's own orientation note, and read the date taken. Reason: her photos are HEIC and the sandbox's FFmpeg 6.1 cannot open HEIC at all; refusing HEIC would make her change a phone setting. — **Reversibility:** reversible — two pip packages used in one module.
- **D-09:** A photo's still clip is `PHOTO_SECONDS = 4` seconds, in settings.py. The still is sized by the same rule as a clip (D-01).
- **D-10:** The full-size photo is saved upright as a JPEG in work/ (for example `work/C-photo.jpg`) and the manifest records both the original path and that copy, because the sandbox cannot reopen the HEIC later and Stage 16's slow move needs the full picture.

**The HDR look**
- **D-11:** HDR is converted on the CPU with the zscale and tonemap filters, which the sandbox's doctor report lists. This is second-best and the user knows it: the best FFmpeg method, libplacebo, also reads the Dolby Vision layer her iPhone adds, but needs a graphics driver the sandbox does not have and is not in the doctor report. The Dolby Vision layer is ignored and the HLG picture underneath is tone-mapped; the manifest says so for each HDR clip.
- **D-12:** The tone-map operator is one name in settings.py, with its peak as a second number (`TONEMAP = "hable"` and `TONEMAP_NPL = 203` to start; changed from `mobius` on 2026-10-13 after research measured hable at 203 as closest to Apple's own rendering of her HLG clips). During the Do-this step the user compares hable, mobius and reinhard by eye on three fixture clips, including a face and a sky, using a one-line command Claude gives them that makes a four-panel strip (no tone map, hable, mobius, reinhard) at a chosen second of any clip; if another looks more like her phone, the name changes. — **Reversibility:** reversible.
- **D-13:** If the HDR conversion fails on a clip, normalize makes a plain copy without tone-mapping and says so: one sentence in the log and in that clip's manifest entry that the colour could not be converted. The clip is not lost.
- **D-14:** The filter chain is told the clip's colour facts explicitly from ffprobe (transfer, primaries, matrix, range) rather than trusting the file's tags alone; HDR means transfer `arib-std-b67` (HLG) or `smpte2084` (PQ), or primaries `bt2020`.

**Past the 2-minute wall**
- **D-15:** One run converts all files. After each clip the command prints one line to standard output such as "B done in 38 s" and rewrites work/manifest.json, so a run still going can be read and a stopped run loses only the clip it was on.
- **D-16:** The run is put in the background by the handbook, not by the code: EDITOR.md starts normalize with the same `nohup ... > normalize.log 2>&1 &` pattern as the join and reads normalize.log every 30 seconds until it says finished. No `--background` option. Claude drafts the EDITOR.md lines in chat; the user, who edits EDITOR.md themselves, decides the exact text and either pastes it or tells Claude to write exactly that. The lines must be on the branch before the phone test.
- **D-17:** Working copies are encoded fast at high quality (an x264 preset such as veryfast and a CRF around 20, both in settings.py), because the renderer re-encodes them. Measured on the Mac pinned to two processors: about 2.4 s of work per second of 1080p HDR video and about 3.3 s per second of 4K HDR, so a one-minute clip passes the 2-minute limit and the background run is mandatory.
- **D-18:** A new normalize run starts a new job: it replaces work/manifest.json and the lettered working copies from the last run.

**Refusals and letters**
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

### Deferred Ideas (OUT OF SCOPE)
- A time estimate printed before a long run starts — Stage 23 (LONG-02).
- Resumable runs that skip clips already converted — Stage 23 (LONG-04).
- The "Shrink for Claude" shortcut for files over the limit — Stage 23 (LONG-08).
- A built-in `--background` option for long commands — if the nohup pattern ever proves fragile, Stage 23.
- Scene-aware or Dolby Vision-aware HDR conversion (libplacebo) — only if the sandbox ever gains it; not planned.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| NORM-01 | `python -m v2r normalize` reads each file's facts with ffprobe (length, size, orientation, fps, HDR, sound, when shot) without changing the file | One ffprobe call shape that works on 6.1 (Code Examples 1); a packet-timestamp scan (0.4 s on a 236 MB file) gives steady-or-not and the slow-motion test; `com.apple.quicktime.creationdate` is the shot-at tag; Pillow EXIF gives a photo's date |
| NORM-02 | One working format: upright, sized for the shape, never scaled up, constant 30 fps, SDR with HDR tone-mapped, H.264, AAC stereo 48 kHz with silence added | Tested `-filter_complex` for video and photo (Code Examples 2-3); size rule as a pure function with a test table; autorotate proven on 6.1 with a corner-marker test; tone-map chain with explicit colour facts; bounded silence (never `-shortest` with an endless source) |
| NORM-03 | A photo becomes a still clip of `PHOTO_SECONDS`; the manifest records the full-resolution photo | Pillow + pillow-heif route; `loop` filter after the scale (1.1 s) instead of `-loop 1` on the big JPEG (56 s); upright full-size JPEG copy |
| NORM-04 | 120/240 fps source flagged as slow motion and converted at normal speed | Median frame rate from packet timestamps; `fps=30` works by timestamp so real time is kept; generated 120 fps test clip |
| NORM-05 | Clips named A, B, C in order; manifest lists facts, working copy, conversion seconds | Manifest layout proposal, atomic rewrite after each clip, `flush=True` for the log (verified: nohup output is block-buffered otherwise) |
| NORM-06 | Over-limit or unreadable file gets one plain sentence; others carry on | Per-file try/except pattern; size check before any decode; Pillow-first sniffing (ffprobe happily "reads" a JPEG as a video, and FFmpeg 6.1 cannot read HEIC) |
| NORM-07 | No original is ever written to | Read-only open everywhere, outputs only under work/ with names made from letters, guard against inputs inside work/, before/after hash test |
| NORM-08 | Only FFmpeg features the doctor report shows; tests use generated clips incl. sideways, 60 fps, no sound, HDR | Exact filter and decoder names to add to doctor; a test that the built graphs use only listed names; generation recipes for every test clip, verified on 6.1 and 8.0.1 |
</phase_requirements>

## Summary

Everything this phase needs can be done with FFmpeg's built-in filters plus Pillow/pillow-heif for photos, and every command shape below was run on both FFmpeg 6.1 and 8.0.1. The conversion is one `ffmpeg` command per file with a `-filter_complex`: the video chain does `fps=30` first (so 60/120/240 fps sources are thinned to 30 before the costly work), then either a plain `scale` or the `zscale` + `tonemap` HDR chain; the audio side is either `aresample`+`apad` on the clip's first audio track or a bounded `anullsrc`. FFmpeg's built-in autorotate (on by default in 6.1) turns an iPhone clip upright at the very start of the graph; Python only needs the rotation to know the upright size. A corner-marker test clip proves, on both versions, that the rotation is applied exactly once and in the right direction.

Four findings change the obvious implementation and the planner must carry them into tasks. (1) A photo must not be made into video with `-loop 1`: that decodes and scales the 24-megapixel JPEG 120 times (56 s here); scaling once and repeating the frame with the `loop` filter takes 1.1 s. (2) `-shortest` with an endless `anullsrc` inside `-filter_complex` hangs FFmpeg 6.1, so silence must be bounded (`anullsrc=...:d=SECONDS` and `-t SECONDS`). (3) HDR brightness depends more on the tone-map "nominal peak" (`npl`) than on the operator: the CONTEXT chain uses `npl=1000`, which gives pictures 10 to 15 luma levels darker than Apple's own QuickLook rendering of the same HLG frames with `mobius` (23 to 59 darker with `hable`); measured on four clips, `hable` at `npl=203` (BT.2408 HLG reference white) matched Apple's mean brightness within about 6 levels on all four, and `mobius`/`reinhard` match at about `npl=800`. `TONEMAP_NPL` therefore needs to be a second setting, and the four-panel strip should use each operator at its matching peak or the user is comparing brightness, not operators. (4) The photo's colour needs an explicit BT.709 conversion and, for her Display P3 HEIC photos, a profile-to-sRGB step in Pillow, or colours drift (a test colour came out (210, 86, 37) instead of (200, 80, 40)).

The two photo libraries are flagged SUS by the legitimacy seam only because the seam has no download count and pillow-heif's newest release is two days old; both are the standard, long-lived Pillow plugin pair. The planner still has to add a `checkpoint:human-verify` before installing them, and should pin `pillow-heif` to the 1.8 line (1.9 will need Pillow 13).

**Primary recommendation:** Build `v2r/normalize.py` around three small pure functions (`working_size`, `hdr_kind`, `video_chain`) plus two command builders copied from Code Examples 2-3, settings for every number (including the new `TONEMAP_NPL`), and a manifest rewritten atomically after each file; start with `hable` at `npl=203` unless the user prefers D-12's `mobius` (then use `npl=800`), and let the four-panel strip settle it.

## Architectural Responsibility Map

This is a command-line tool, so tiers are the program's own layers, not web tiers.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Reading facts (probe, steady, slow-motion, HDR kind, shot date) | `v2r/normalize.py` (ffprobe via subprocess) | Pillow for photo EXIF | Facts only, no decisions about the edit (CLAUDE.md "three jobs") |
| Deciding the working size, HDR vs SDR path | `v2r/normalize.py` pure functions | `v2r/settings.py` | Rules belong to normalize; every number lives in settings.py |
| Pixel work (rotate, scale, fps, tone-map, encode, silence) | FFmpeg subprocess | — | One command per output, built as a list; Python never touches pixels |
| Photo decode, orientation, ICC to sRGB, full-size JPEG copy | Pillow + pillow-heif | FFmpeg (reads only the finished upright JPEG) | The sandbox's FFmpeg 6.1 cannot open HEIC |
| Manifest (the contract for Stages 15 and 16) | `v2r/normalize.py` writes `work/manifest.json` | — | Atomic rewrite after every file |
| Background running and polling | EDITOR.md (nohup + normalize.log) | the command's flushed progress lines | Decided D-16; code must only print and flush |
| Proving the sandbox has the features | `v2r/doctor.py` lists | normalize start-up check | D-06 / NORM-08 |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FFmpeg / ffprobe (system) | sandbox 6.1.1-3ubuntu5; Mac 8.0.1 | rotate, scale, fps, tone-map, encode | The only video tool allowed by the sandbox rules; `zscale`/`tonemap` listed in the sandbox doctor report [VERIFIED: docs/phone-limits.md "The zscale filter is available." and "The tonemap filter is available."] |
| Python standard library (`subprocess`, `json`, `os`, `pathlib`, `statistics`, `time`) | 3.13 | probe parsing, manifest, orchestration | No new dependency needed for anything but photos |
| Pillow | 12.3.0, licence MIT-CMU | open JPEG/PNG/HEIC, EXIF orientation and date, ICC to sRGB, save upright JPEG | Locked by D-08. [VERIFIED: pypi.org JSON API: version 12.3.0, license_expression MIT-CMU, requires_python >=3.10, cp313 manylinux x86_64 and aarch64 wheels] |
| pillow-heif | 1.8.1, licence BSD-3-Clause | lets Pillow open HEIC | Locked by D-08. [VERIFIED: pypi.org JSON API: 1.8.1, BSD-3-Clause, requires pillow>=11.1.0, cp313 manylinux_2_27/2_28 x86_64 and aarch64 wheels] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | >=9.1.1 (already a dev dependency) | tests | all tests; no new test dependency is needed (the manifest is checked with plain asserts) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Pillow + pillow-heif | `heif-convert` CLI, FFmpeg 7+ HEIF demuxer | Not in the sandbox (FFmpeg 6.1 error "moov atom not found" [VERIFIED: ffmpeg 6.1 run on a real HEIC]); D-08 is locked anyway |
| Hand-written `manifest.schema.json` + `jsonschema` | plain asserts in tests + a docstring | A schema file is reasonable but adds a dependency this phase; Stage 16's `check` will bring `jsonschema` anyway. Recommend: docstring + key-set assertions now, schema when Stage 16 needs it |
| `-loop 1` for stills | `loop` filter after scaling | `-loop 1` is 50x slower on a big photo (see Pitfall 1) |
| libplacebo tone-mapping | zscale + tonemap | libplacebo needs a GPU driver, not in the sandbox; locked D-11 |

**Installation (the planner's tasks, after the human-verify checkpoint):**
```bash
uv add pillow pillow-heif        # consider: uv add "pillow>=12.3" "pillow-heif>=1.8,<1.9"
uv export --format requirements-txt --no-dev --no-emit-project --no-hashes -o requirements.txt
```
The export command is the one in README.md ("After adding or upgrading a library with `uv add`, regenerate `requirements.txt`..."). requirements.txt is currently only its two header comment lines [VERIFIED: requirements.txt:1-2], so it will gain `pillow==...` and `pillow-heif==...` lines. The skill installs it with `python3 -m pip install --break-system-packages -r requirements.txt` [VERIFIED: skill/vid2reel/SKILL.md step 3].

**Version verification:** versions and dates read from the PyPI JSON API on 2026-10-13: pillow 12.3.0 (uploaded 2026-07-01), pillow-heif 1.8.1 (2026-10-11; previous 1.8.0 on 2026-09-22, 1.7.0 on 2026-09-06). pillow-heif's changelog says 1.8.1 "is the last version that supports `Python 3.10` and `Pillow` `11`/`12`: version `1.9.0` will require `Pillow 13`" [CITED: github.com/bigcat88/pillow_heif CHANGELOG.md]. Opening a real HEIC with these exact versions worked here: Pillow 12.3.0, pillow-heif 1.8.1, libheif 1.23.6.

## Package Legitimacy Audit

Seam command run: `gsd-tools query package-legitimacy check --ecosystem pypi pillow pillow-heif`.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| pillow | PyPI | latest release 2026-07-01; long-established project [ASSUMED: since 2010] | seam returned `unknown-downloads` | github.com/python-pillow/Pillow | SUS (reason: unknown-downloads only) | Flagged. Named by the user in D-08. Planner must add `checkpoint:human-verify` before install |
| pillow-heif | PyPI | latest release 2026-10-11 (2 days old); releases monthly since 1.0.0 on 2025-06-29 | seam returned `unknown-downloads` | github.com/bigcat88/pillow_heif | SUS (reasons: too-new, unknown-downloads) | Flagged. Named by the user in D-08. Planner must add `checkpoint:human-verify`; consider pinning `<1.9` or `==1.8.0` (released 2026-09-22) |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** `pillow` [WARNING: flagged as suspicious — verify before using.], `pillow-heif` [WARNING: flagged as suspicious — verify before using.]. My own assessment: both flags come from missing download statistics and a fresh patch release, not from anything about the projects (official source repos, project URLs match the documentation). PyPI has no install scripts, so the "postinstall" check does not apply. The human still approves per the protocol.

Licence detail the user asked for, for docs/licenses.md:
- Pillow: MIT-CMU [VERIFIED: PyPI license_expression].
- pillow-heif: BSD-3-Clause [VERIFIED: PyPI]. Its wheels bundle libheif (LGPL-3.0), libde265 (LGPL-3.0) and x265 (GPL-2.0) [CITED: raw.githubusercontent.com/bigcat88/pillow_heif/master/LICENSES_bundled.txt]. This repo does not redistribute them (pip downloads the wheel from PyPI at run time), but docs/licenses.md should say so in one line so the user sees the full picture.

## Architecture Patterns

### System Architecture Diagram

```
python -m v2r normalize --shape tall|wide FILE1 FILE2 ...
        |
        v
  __main__.py (argparse, --shape required, no default, like join)
        |
        v
  normalize.run(files, shape, out_dir=WORK_DIR)
        |-- check doctor lists (filters + decoders) ---- missing? -> one sentence, stop
        |-- clear last job: work/manifest.json, work/<LETTERS>.mp4, work/<LETTERS>-photo.jpg (regex only)
        |
        v   for each file, in the order given (letter = A, B, C ...)
  +-----------------------------------------------------------------+
  | size > MAX_ATTACHMENT_BYTES ? --yes--> skipped entry + sentence |
  | inside work/ ?               --yes--> skipped entry + sentence  |
  | Pillow can open it?  ---------yes--> PHOTO branch               |
  | ffprobe reads a video stream? -yes--> VIDEO branch              |
  | neither ----------------------------> skipped: "could not be read"|
  +-----------------------------------------------------------------+
        |                                  |
   PHOTO branch                       VIDEO branch
   Pillow: open (+pillow-heif),       ffprobe facts + packet scan
   exif_transpose, ICC->sRGB,         (rotation, upright size, fps,
   save upright full-size JPEG        steady?, slow_motion?, hdr kind,
   work/C-photo.jpg, read date        sound?, shot_at)
        |                                  |
        v                                  v
   ffmpeg: scale once + loop       ffmpeg: [autorotate] fps=30 ->
   filter -> 4 s still + silence   (HDR: zscale+tonemap | SDR: scale)
        |                          + aresample/apad or anullsrc
        |                                  | HDR chain fails? -> retry plain, add note (D-13)
        +-----------------+----------------+
                          v
        entry done -> print "B done in 38 s" (flush) -> rewrite manifest.json atomically
                          |
                          v
        at end: manifest "finished": true, print summary sentences, exit 0 if >=1 converted else 1
```

### Recommended Project Structure
```
v2r/
├── normalize.py     # probe, working_size, hdr_kind, command builders, photo, manifest, run()
├── settings.py      # + the numbers listed below
├── doctor.py        # + longer FILTERS, new DECODERS list (+ "-decoders" check)
└── __main__.py      # + `normalize` sub-command
tests/
├── media.py         # NEW helper module: make_clip(...), make_photo(...) (importable, not a test)
└── test_normalize.py
docs/licenses.md     # NEW
.gitignore           # + /normalize.log  (join.log is already listed there)
```
`tests/` has no `__init__.py`, so pytest puts `tests/` on `sys.path` and `from media import make_clip` works. `test_join.py` keeps its own `make_clip` (do not edit it; Phase 2 is not about join).

### Settings to add to `v2r/settings.py` (every number, with unit comments)

Existing values the new code reads (quoted verbatim): `OUTPUT_FPS = 30  # frames per second` [VERIFIED: v2r/settings.py:13]; `SHAPES = {"tall": (1080, 1920), "wide": (1920, 1080)}` [VERIFIED: v2r/settings.py:9-12]; `MAX_ATTACHMENT_BYTES = 400 * 1000**2` [VERIFIED: v2r/settings.py:30]; `MAX_ATTACHMENTS = 10` [VERIFIED: v2r/settings.py:31]. `AUDIO_BITRATE = 128_000` already exists for the join [VERIFIED: v2r/settings.py:16]; give the working copies their own name.

```python
# normalize: working size per job shape and source orientation, as (max width, max height) in pixels;
# None means no limit on that side. Nothing is ever scaled up. A square source uses the shape's own entry
# (tall -> "portrait", wide -> "landscape").
WORKING_SIZE = {
    "tall": {"portrait": (1080, 1920), "landscape": (None, 1920)},
    "wide": {"landscape": (1920, 1080), "portrait": (1920, None)},
}
PHOTO_SECONDS = 4          # seconds a photo's still clip lasts
PHOTO_JPEG_QUALITY = 92    # 1-100, the upright full-size copy of a photo
X264_PRESET = "veryfast"   # working copies: fast encode (the renderer re-encodes them)
X264_CRF = 20              # working copies: lower is better quality
WORKING_AUDIO_BITRATE = 160_000  # bits per second of AAC sound in a working copy
AUDIO_RATE = 48_000        # samples per second of every working copy's sound
TONEMAP = "hable"          # tone-map operator: hable, mobius or reinhard (see Open Question 1)
TONEMAP_NPL = 203          # nits: nominal peak for HLG sources; 203 is BT.2408's HLG reference white
TONEMAP_NPL_PQ = 100       # nits: nominal peak for PQ sources (FFmpeg's documented recipe; not calibrated)
SLOW_MOTION_MIN_FPS = 100  # frames per second: a median frame rate at or above this marks slow-motion source
STEADY_TOLERANCE = 0.25    # share of the median frame gap a frame gap may differ by and still be "steady"
```
If the user prefers D-12's `mobius` as the start, the matching pair is `TONEMAP = "mobius"`, `TONEMAP_NPL = 800` (see the calibration table). A per-operator `npl` dict is the alternative; one number is simpler and the strip command can name its own.

### Pattern 1: Probe once, decide in pure functions
**What:** `ffprobe` JSON in, plain dict of facts out; the decisions (`working_size`, `hdr_kind`, slow-motion, steady) are small pure functions tested with tables, so the 4K and odd-size cases need no 4K file.
**When to use:** always; it also keeps tests fast.
```python
# Source: written and run this session against ffprobe 6.1 and 8.0.1
def working_size(shape, w, h):
    caps = settings.WORKING_SIZE[shape]
    orient = "landscape" if w > h else "portrait" if h > w else ("portrait" if shape == "tall" else "landscape")
    cw, ch = caps[orient]
    f = min([1.0] + [c / d for c, d in ((cw, w), (ch, h)) if c])   # never above 1.0 = never scaled up
    even = lambda x: max(2, int(x) // 2 * 2)                        # floor to even: never over the cap
    return even(w * f), even(h * f)
```
Expected values to put in the test table (computed with this function):

| Job | Upright source | Working size |
|-----|---------------|--------------|
| tall | 2160×3840 (the 4K iPhone clip, stored 3840×2160 + rotation) | 1080×1920 |
| tall | 3840×2160 landscape | 3412×1920 |
| tall | 1920×1080 landscape | 1920×1080 (unchanged: never scaled up) |
| tall | 4284×5712 (a 24 MP photo) | 1080×1440 |
| wide | 3840×2160 | 1920×1080 |
| wide | 2160×3840 portrait | 1920×3412 |
| wide | 1080×1920 portrait | 1080×1920 (unchanged) |
| any | 641×361 (odd) | 640×360 (floored to even) |

### Pattern 2: Rotation is read for sizing only; FFmpeg's autorotate does the turning
**What:** ffprobe reports stored `width`/`height` and a Display Matrix `rotation` (iPhone portrait clips: `-90`). Swap width and height when `rotation % 180 != 0`. Do not pass `-noautorotate` and do not add `transpose` yourself.
**Verified direction (a white box in the stored top-left corner, then normalize):** `-display_rotation 90` puts it bottom-left; `-90` puts it top-right; `180` puts it bottom-right; no rotation leaves it top-left; output always has no rotation side data. Identical on FFmpeg 6.1 and 8.0.1 [VERIFIED: ffmpeg 6.1 + 8.0.1 run]. These are ready-made test assertions (Pitfall 4 is the "applied twice" fault the guide warns about).

### Pattern 3: One file in, one result out; errors are values
Mirror `join.py`: a plain-English error class (`NormalizeError`), `subprocess.CalledProcessError` turned into one sentence, output deleted on failure. Per file: `try: convert; except (NormalizeError, subprocess.CalledProcessError, OSError, Exception-from-Pillow) as e: entry = skipped(sentence)`. One broad `except Exception` at the per-file boundary is justified here (NORM-06: nothing may stop the others); log the real exception text into a `detail` field, show only the sentence.

### Pattern 4: Manifest rewritten atomically after every file
Write `manifest.json.tmp` in `work/`, then `os.replace(tmp, final)`; a reader polling during the run never sees half a file. Include `"finished": false` until the loop ends, then `true`.

### Manifest shape (proposal; the planner may rename, but must freeze it before Stage 15)
Paths: `original.path` is exactly the path given (absolute); `working.file` and `photo.file` are file names relative to the manifest's own folder (so the repo can be cloned anywhere in the sandbox). No GPS, no device model (the files carry both; the manifest is for editing facts only).
```json
{
  "version": 1,
  "shape": "tall",
  "finished": true,
  "clips": [
    {
      "letter": "A",
      "number": 1,
      "status": "done",
      "kind": "video",
      "original": {
        "path": "/mnt/user-data/uploads/IMG_0001.MOV",
        "name": "IMG_0001.MOV",
        "bytes": 12145565,
        "seconds": 10.23,
        "stored_size": [1920, 1080],
        "rotation": -90,
        "upright_size": [1080, 1920],
        "fps": 29.98,
        "fps_steady": true,
        "slow_motion": false,
        "hdr": "hlg",
        "dolby_vision": true,
        "has_sound": true,
        "shot_at": "2026-10-12T18:49:03-07:00"
      },
      "working": {"file": "A.mp4", "size": [1080, 1920], "fps": 30, "seconds": 10.23, "bytes": 13129194, "sound_added": false},
      "convert_seconds": 13.8,
      "notes": ["HDR (HLG) was tone-mapped to ordinary colour; the Dolby Vision layer was ignored."]
    },
    {
      "letter": "B", "number": 2, "status": "skipped", "kind": null,
      "original": {"path": "/mnt/user-data/uploads/IMG_0002.MOV", "name": "IMG_0002.MOV", "bytes": 4},
      "sentence": "The second file, IMG_0002.MOV, could not be read as a video or a photo."
    },
    {
      "letter": "C", "number": 3, "status": "done", "kind": "photo",
      "original": {"path": "...", "name": "IMG_0003.HEIC", "bytes": 4884659, "stored_size": [4284, 5712], "upright_size": [4284, 5712], "shot_at": "2026-10-10T18:03:24"},
      "photo": {"file": "C-photo.jpg", "size": [4284, 5712]},
      "working": {"file": "C.mp4", "size": [1080, 1440], "fps": 30, "seconds": 4.0, "bytes": 457315, "sound_added": true},
      "convert_seconds": 1.3, "notes": []
    }
  ]
}
```
Rules: every entry has `letter`, `number`, `status` (`"done"` or `"skipped"`), and skipped entries always carry `sentence` (D-19, D-22). A colour-fallback clip (D-13) is `done` with a note. `shot_at` is `null` when unknown: for clips use the `com.apple.quicktime.creationdate` tag (local time with offset), else `creation_time`; for photos, EXIF DateTimeOriginal. Letters beyond Z continue AA, AB... (not enforced to 10, D-21).

### Anti-Patterns to Avoid
- **`-loop 1` on a full-size photo:** 56 s instead of 1.1 s (Pitfall 1).
- **`-shortest` with an endless audio source in `-filter_complex`:** hangs 6.1 (Pitfall 2).
- **Trusting the file's colour tags:** an HDR-ish clip with no transfer tag fails with "Generic error in an external library" (D-14, Pitfall 3).
- **Routing every file to ffprobe first:** it reads a JPEG as a one-frame "video"; sniff with Pillow first (Pitfall 6).
- **Naming outputs from the input file name:** use letters only; input names never reach a path or a filter graph.
- **Printing FFmpeg's raw stderr into the log:** the rule is one sentence per bad file; capture stderr, keep its tail in `detail`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Turning clips upright | your own transpose/flip chooser | FFmpeg's default autorotate | proven on 6.1 and 8.0.1; the join relies on it; doing it twice is the guide's named fault |
| 60/120/240 fps to 30 fps | frame counting/dropping in Python | `fps=30` filter (by timestamp) + `-fps_mode cfr` | keeps real time and A/V sync; works on variable-rate input |
| HDR to SDR | a hand-made curve | `zscale` + `tonemap` (operator name from settings) | locked D-11; chain proven on 6.1 |
| HEIC decode, EXIF orientation, ICC conversion | your own parser | Pillow + pillow-heif, `ImageOps.exif_transpose`, `ImageCms.profileToProfile` | HEIC tiling and `irot` are deceptively hard; all verified on a real iPhone HEIC |
| Shot date of a photo | reading EXIF bytes | `Image.getexif()` then `get_ifd(0x8769).get(0x9003)` | works for JPEG and HEIC |
| Silence | writing a WAV | `anullsrc=r=48000:cl=stereo:d=SECONDS` | bounded, exact length on both versions |
| Atomic file write | hand-rolled locking | write temp + `os.replace` | standard library |
| Deciding "steady" from `avg_frame_rate` vs `r_frame_rate` | comparing the two rates | packet timestamps (`-show_entries packet=pts_time`) | the real clips' two rates differ (30000/1001 vs 36840/1229) although every frame gap is within 5% of 33.3 ms; only the packet gaps tell the truth |

**Key insight:** every piece of this phase is a short FFmpeg filter string or a one-line Pillow call; the real work is knowing which obvious versions of them are wrong on 6.1 (see Common Pitfalls).

## Runtime State Inventory

Not a rename/refactor/migration phase. Omitted. (One related note: D-18 deletes the previous job's `work/<LETTERS>.mp4`, `work/<LETTERS>-photo.jpg` and `work/manifest.json` at the start of a run; delete by regex `^[A-Z]{1,3}(-photo)?\.(mp4|jpg)$` plus the manifest, never other files in work/ such as `join-*.mp4`.)

## Common Pitfalls

### Pitfall 1: Making a still clip with `-loop 1` decodes the big photo 120 times
**What goes wrong:** `ffmpeg -loop 1 -framerate 30 -t 4 -i photo_full.jpg ...` took 56 s wall (4 min 20 s of CPU) for a 24 MP photo on an 8-core Mac; in the sandbox it would blow the 2-minute limit for one photo.
**Why it happens:** the image demuxer re-reads and re-decodes the JPEG for every frame, and the scale runs 120 times.
**How to avoid:** read the image once, scale once, then repeat the frame with the `loop` filter: `scale=...,format=yuv420p,setsar=1,loop=loop=119:size=1:start=0,setpts=N/(30*TB)` with `-frames:v 120`. 1.1 s for the same photo; 120 frames, 4.000 s, on 6.1 and 8.0.1 [VERIFIED: ffmpeg 6.1 + 8.0.1 run].
**Warning signs:** a photo taking more than a couple of seconds.

### Pitfall 2: `-shortest` with an endless silence source hangs FFmpeg 6.1
**What goes wrong:** `-filter_complex "...;anullsrc=r=48000:cl=stereo[a]" ... -shortest` never finished on 6.1 (killed after 100 s).
**Why it happens:** in 6.1 `-shortest` does not stop a complex-graph source that never ends.
**How to avoid:** bound everything. Silent clip: `anullsrc=r=48000:cl=stereo:d=D`. Clip with sound: `[0:a:0]aresample=48000:async=1:first_pts=0,apad=whole_dur=D`. Always add `-t D` where D is the video's duration. Result: audio length equals video length (2.000 s and 2.000 s; 3.967 s for a short-audio clip) on 6.1 and 8.0.1 [VERIFIED: ffmpeg 6.1 + 8.0.1 run]. Also give every test FFmpeg call `timeout=` so a hang fails a test instead of the suite.
**Warning signs:** an ffmpeg process at 100% CPU that never exits.

### Pitfall 3: HDR chain fails when the file lacks a transfer tag
**What goes wrong:** `zscale=t=linear:npl=203,...` on a clip tagged `bt2020nc` primaries but no transfer: "Error while filtering: Generic error in an external library".
**How to avoid:** D-14: pass `tin`, `pin`, `min`, `rin` explicitly from ffprobe; if the transfer is missing and primaries are bt2020, treat as gamut-only (`tin=bt709`, no `tonemap`). Wrap the HDR command in the D-13 retry: on any non-zero exit, rebuild the command with the plain SDR chain, add the note "The colour of the Nth file could not be converted, so its colour is unchanged and may look flat." Verified: explicit tags work for HLG, PQ and gamut-only clips; a broken `tonemap` name returns exit code 234, which is what the fallback test can trigger by monkeypatching `settings.TONEMAP` [VERIFIED: ffmpeg 6.1 + 8.0.1 run].

### Pitfall 4: Sideways handling: applied twice, or the test clip silently isn't sideways
**What goes wrong (test side):** `-metadata:s:v rotate=90` writes nothing on FFmpeg 6.1 and 8.0.1 (ffprobe shows no rotation), so a "sideways" test clip made that way is just a normal clip and the test proves nothing.
**How to avoid:** make the clip in two steps: a plain MP4, then `ffmpeg -display_rotation 90 -i plain.mp4 -c copy sideways.mp4` (`-display_rotation` is an input option); ffprobe 6.1 then reports `"side_data_type": "Display Matrix", "rotation": 90` [VERIFIED: ffmpeg 6.1 + 8.0.1 run]. Draw a white box in the stored top-left corner so the test can check where it lands (Pattern 2).

### Pitfall 5: Tone-map brightness is set by `npl`, not just by the operator
**What goes wrong:** with the CONTEXT chain (`npl=1000`) the picture is much darker than Apple's own conversion; comparing hable/mobius/reinhard at one shared `npl` mostly compares brightness.
**Evidence (mean brightness, 0-255 luma, of the tone-mapped frame at the frame QuickLook chose; Apple's QuickLook thumbnail is the reference; four real HLG clips, one dark):**

| Clip | Apple QuickLook | hable npl 203 | mobius npl 800 | reinhard npl 800 | mobius npl 203 | mobius npl 1000 |
|------|----------------|---------------|----------------|------------------|----------------|-----------------|
| 1 (outdoor, bright) | 146 | 152 | 142 | 132 | 196 | 131 |
| 2 (door, mid) | 94 | 97 | 88 | 84 | 132 | 80 |
| 3 (talking, mid) | 102 | 104 | 94 | 90 | 138 | 87 |
| 4 (night, dark) | 49 | 49 | 42 | 42 | 70 | 39 |

[VERIFIED: local measurement this session with ffmpeg 6.1 and `qlmanage -t`; mean luma and mean absolute pixel error; four clips only; QuickLook is a proxy for "like her phone", not a guarantee, assumption A3.] `hable@203` was tied for the lowest mean pixel error on all four clips (22, 26, 25, 4). Brightness of a flat HLG patch through the proposed chain: HLG luma 126 -> about 98, 180 -> about 151, 235 -> about 215 (hable@203); a clip merely relabelled instead of converted would stay at 126, 180, 235 [VERIFIED: ffmpeg 6.1 run], which gives the HDR test a hard assertion.
**How to avoid:** `TONEMAP_NPL` in settings.py; strip command (Code Example 5) uses hable at 203 and mobius/reinhard at 800 so the panels are brightness-matched; say so to the user.

### Pitfall 6: Choosing photo vs video by asking ffprobe first
**What goes wrong:** ffprobe 6.1 reads a plain JPEG as a video (`mjpeg`, `image2`, duration 0.04) so a photo would be sent down the video path; HEIC fails on 6.1 ("moov atom not found") but FFmpeg 8 on the Mac reads only a 640×896 tile of it, so Mac tests could pass while the sandbox fails.
**How to avoid:** sniff with Pillow first (`Image.open` reads only the header). Verified: Pillow with pillow-heif opens JPEG and HEIC and raises `UnidentifiedImageError` for an MP4, a real .MOV, a garbage file and an empty file [VERIFIED: pillow 12.3.0 + pillow-heif 1.8.1 run]. Never hand a HEIC to FFmpeg; FFmpeg only ever sees the upright JPEG Normalize wrote.

### Pitfall 7: Photo colour drifts without an explicit BT.709 conversion
**What goes wrong:** a JPEG is YCbCr BT.601 full range. `scale=...,format=yuv420p` alone gave RGB (210, 86, 37) for a (200, 80, 40) test colour once decoded as BT.709. With `scale=W:H:flags=bicubic:out_color_matrix=bt709:out_range=tv,format=yuv420p` it was (197, 77, 39) [VERIFIED: ffmpeg 6.1 run]. Her HEIC photos carry a Display P3 profile (536-byte ICC, read from a real photo), which FFmpeg ignores.
**How to avoid:** in Pillow, convert with `ImageCms.profileToProfile(im, source_profile, ImageCms.createProfile("sRGB"), outputMode="RGB")` when an ICC profile is present (1.4 s on a 24 MP photo), then save the JPEG without the old profile; tag the output BT.709 (`-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv`). Use the same `out_color_matrix=bt709:out_range=tv` in the SDR video `scale` so odd sources are converted rather than relabelled.

### Pitfall 8: The log shows nothing until the run ends
**What goes wrong:** Python block-buffers stdout when it goes to a file, so `normalize.log` stays empty while the background run works; Claude would wait for nothing. Verified: with output to a file, `print("started")` was not visible after 1 s; it appeared only when the process ended [VERIFIED: python 3 run].
**How to avoid:** `print(line, flush=True)` for every progress line and sentence (join prints once at the end, so it never met this). Also add `/normalize.log` to .gitignore (only `/join.log` is listed [VERIFIED: .gitignore, line `/join.log`]).

### Pitfall 9: Deleting or overwriting an original by accident
**What goes wrong:** D-18 clears the last job's files; if she (or Claude) passes `work/A.mp4` as an input, clearing deletes the input, or FFmpeg reads and writes the same file.
**How to avoid:** resolve every input to an absolute path first; if it lies inside `out_dir`, skip it with a sentence ("The second file, A.mp4, is already in the work folder, so it was left alone."). Absolute paths also prevent a file named `-x.mov` from being read as an option by ffprobe (pass inputs after `-i`). NORM-07 test: SHA-256 and `st_mtime_ns` of every input before and after, plus read-only inputs.

### Pitfall 10: Her footage is not all 30 fps
**What goes wrong:** 2 of the 15 local fixture videos have a median frame rate of 24.00; `fps=30` duplicates frames (a mild judder). Not a bug (D-02 fixes 30 fps), but record the source fps in the manifest and tell the user to look for it. Frame gaps of real clips vary by up to 5% (the 1/600 s timebase) and none of 15 exceeded the 25% `STEADY_TOLERANCE`, so "steady" is true for all of them [VERIFIED: packet scan of 15 local clips].

### Pitfall 11: Heavy imports and missing libraries
`import pillow_heif` only inside the photo function, with `except ImportError` turned into the sentence "Photos could not be read because the picture library is not installed." Then `doctor`, `join` and all video normalizing keep working if pip fails on the two photo libraries on the phone.

### Pitfall 12: Mixed 4K 60 fps work volume
60 fps 4K HDR is the likely worst case she shoots; `fps=30` is placed first in the chain so tone-mapping runs on half the frames, but HEVC decode still dominates. Measured: a 31.3 s 4K portrait HDR clip took 51 s on 8 cores (328 CPU-seconds, about 10 CPU-seconds per video second, so roughly 5 s of wall time per second on the sandbox's 2 processors) [VERIFIED: local run]. A one-minute 4K clip needs about 5 minutes: only safe because EDITOR.md runs it in the background.

## Code Examples

All three were run on FFmpeg 6.1 and 8.0.1 (generated clips, a real HDR clip and a real HEIC photo). They are sketches for the executor to adapt into `v2r/normalize.py`, not finished code.

### 1. One ffprobe call, and the packet scan
```python
# Source: run this session; the -show_entries list is CONTEXT.md's list plus start/duration; works on ffprobe 6.1
PROBE = ["ffprobe", "-v", "error", "-show_entries",
    "format=duration,size:format_tags=creation_time,com.apple.quicktime.creationdate:"
    "stream=index,codec_type,codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,duration,"
    "color_range,color_space,color_transfer,color_primaries,channels,sample_rate:"
    "stream_side_data=rotation,side_data_type", "-of", "json"]
info = json.loads(subprocess.run([*PROBE, str(path)], capture_output=True, text=True, check=True).stdout)
video = next(s for s in info["streams"] if s["codec_type"] == "video")          # first video track only
has_sound = any(s["codec_type"] == "audio" for s in info["streams"])
rotation = next((int(round(sd["rotation"])) for sd in video.get("side_data_list", []) if "rotation" in sd), 0)
dolby_vision = any(sd.get("side_data_type") == "DOVI configuration record" for sd in video.get("side_data_list", []))
upright = (video["height"], video["width"]) if rotation % 180 else (video["width"], video["height"])

# steady and slow-motion from frame gaps: demux only, 0.4 s on a 236 MB file
out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time",
                      "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout
times = sorted(float(t) for t in out.split() if t != "N/A")
gaps = [b - a for a, b in zip(times, times[1:])]
median = statistics.median(gaps)
fps_steady = all(abs(g - median) <= settings.STEADY_TOLERANCE * median for g in gaps)
slow_motion = 1 / median >= settings.SLOW_MOTION_MIN_FPS
```
Facts about ffprobe 6.1 output this relies on (read from real iPhone clips and generated ones): the rotation appears under `side_data_list` as `"side_data_type": "Display Matrix", "rotation": -90`; HDR clips show `color_transfer: arib-std-b67`, `color_primaries: bt2020`, `color_space: bt2020nc`; the first audio stream is stereo AAC while a second multi-channel stream follows, and only `0:a:0` is used. The median-gap rule: a pure 120 fps clip has gaps of 8.3 ms (120 fps), a 60 fps clip 16.7 ms, so `SLOW_MOTION_MIN_FPS = 100` separates them. A mixed iPhone slow-motion file (normal speed, then 240 fps) has mostly 240 fps frames, so the median still flags it (A5). Guard for an empty or one-packet list (photos never reach here; a one-frame video has no gaps: treat as steady, not slow).

### 2. The video command
```python
# Source: run this session on ffmpeg 6.1 and 8.0.1; real HDR clip: 10.2 s in, 10.23 s video + 10.24 s audio out
BASE = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n"]   # -n: never overwrite
TAGS = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]
ENC = ["-c:v", "libx264", "-preset", settings.X264_PRESET, "-crf", str(settings.X264_CRF), "-pix_fmt", "yuv420p", *TAGS,
       "-c:a", "aac", "-b:a", str(settings.WORKING_AUDIO_BITRATE), "-ac", "2", "-ar", str(settings.AUDIO_RATE),
       "-map_metadata", "-1", "-map_chapters", "-1", "-movflags", "+faststart"]   # -map_metadata -1 also drops GPS tags

def video_chain(v, w, h, tonemap=True):
    kind = hdr_kind(v)          # "hlg" | "pq" | "bt2020" | None   (D-14)
    if kind and tonemap:
        tin = {"hlg": "arib-std-b67", "pq": "smpte2084"}.get(kind, "bt709")
        npl = settings.TONEMAP_NPL if kind == "hlg" else settings.TONEMAP_NPL_PQ
        rng = "pc" if v.get("color_range") == "pc" else "tv"
        pri = v.get("color_primaries") or "bt2020"
        mat = v.get("color_space") or "bt2020nc"
        op = f"tonemap={settings.TONEMAP}:desat=0," if kind != "bt2020" else ""    # gamut-only: no tone map
        return (f"fps={settings.OUTPUT_FPS},"
                f"zscale=w={w}:h={h}:tin={tin}:pin={pri}:min={mat}:rin={rng}:t=linear:npl={npl},"
                f"format=gbrpf32le,zscale=p=bt709,{op}zscale=t=bt709:m=bt709:r=tv,format=yuv420p,setsar=1")
    return (f"fps={settings.OUTPUT_FPS},scale={w}:{h}:flags=bicubic:out_color_matrix=bt709:out_range=tv,"
            f"format=yuv420p,setsar=1")

audio = (f"[0:a:0]aresample={settings.AUDIO_RATE}:async=1:first_pts=0,apad=whole_dur={D}[a]" if has_sound
         else f"anullsrc=r={settings.AUDIO_RATE}:cl=stereo:d={D}[a]")           # D = the video's seconds
cmd = [*BASE, "-i", str(src), "-filter_complex", f"[0:v:0]{video_chain(v, W, H)}[v];{audio}",
       "-map", "[v]", "-map", "[a]", "-fps_mode", "cfr", "-r", str(settings.OUTPUT_FPS), "-t", str(D), *ENC, str(dst)]
```
Why each part: FFmpeg inserts the rotation filters ahead of `[0:v:0]` automatically, so `zscale=w=W:h=H` receives the upright frame and `W`×`H` is the upright working size from `working_size()`; `fps=` first thins 60/120/240 fps before the costly steps; the whole zscale chain scales inside the first `zscale` so tone-mapping runs at the small size; `-fps_mode cfr` plus `-r 30` guarantee constant 30; `-t D` and the bounded audio keep both streams the same length. Run with the whole command's stderr captured (`capture_output=True, text=True`), and on non-zero exit and an HDR clip, rebuild with `tonemap=False` (D-13). Delete the output on failure (join's pattern). Measured on the 6.1 build: a generated clip of every kind converted in 0.1-0.4 s; a real 10 s 1080p HDR clip in 13.8 s on 8 cores.

### 3. The photo command
```python
# Source: run this session; 24 MP HEIC -> 1.3 s (tall, 1080x1440) and 2.8 s (wide, 1920x2560) on ffmpeg 6.1
fps, secs = settings.OUTPUT_FPS, settings.PHOTO_SECONDS
graph = (f"[0:v:0]scale={W}:{H}:flags=bicubic:out_color_matrix=bt709:out_range=tv,format=yuv420p,setsar=1,"
         f"loop=loop={secs * fps - 1}:size=1:start=0,setpts=N/({fps}*TB)[v];"
         f"anullsrc=r={settings.AUDIO_RATE}:cl=stereo:d={secs}[a]")
cmd = [*BASE, "-i", str(upright_jpeg), "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
       "-frames:v", str(secs * fps), "-r", str(fps), "-t", str(secs), *ENC, str(dst)]
```
and the Pillow half (lazy import inside the function):
```python
# Source: run this session, pillow 12.3.0 + pillow-heif 1.8.1, real iPhone HEIC 4284x5712
import io, pillow_heif
from PIL import Image, ImageCms, ImageOps
pillow_heif.register_heif_opener()
with Image.open(path) as im:                      # raises PIL.UnidentifiedImageError if not a photo
    im.load()
    shot_at = im.getexif().get_ifd(0x8769).get(0x9003) or im.getexif().get(0x0132)   # "2026:10:10 18:03:24"
    icc = im.info.get("icc_profile")
    im = ImageOps.exif_transpose(im)              # JPEG: applies the orientation note; HEIC: already upright
    if icc:
        im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)),
                                       ImageCms.createProfile("sRGB"), outputMode="RGB")
    im = im.convert("RGB")                        # drops alpha from PNGs
    im.save(jpeg_path, "JPEG", quality=settings.PHOTO_JPEG_QUALITY, subsampling=0)   # no EXIF/GPS is written
```
Verified behaviour: a JPEG with EXIF orientation 6 comes out rotated (stored 400×300 -> 300×400, box from top-left to top-right); a HEIC saved by pillow-heif has the orientation baked in (stored 300×400, orientation 1); the real HEIC reports `(4284, 5712)` and orientation 1 after pillow-heif already applied its `irot`. A 24 MP photo took 0.64 s to open, 1.43 s ICC, 1.02 s save, about 250 MB peak memory, 7.1 MB JPEG. Leave Pillow's decompression-bomb limit at its default; turn `DecompressionBombError`/any Pillow exception into "could not be read".

### 4. Doctor grows (D-06) and normalize checks the same lists
```python
# v2r/doctor.py: names confirmed present in the ffmpeg 6.1 and 8.0.1 builds used here
FILTERS = ["scale", "crop", "zscale", "tonemap", "loudnorm", "drawtext",            # existing, doctor.py:16
           "format", "fps", "setsar", "setpts", "loop", "transpose", "hflip", "vflip",   # video chain + autorotate
           "aresample", "apad", "anullsrc"]                                          # sound
DECODERS = ["hevc", "h264", "aac", "mjpeg", "png"]
# run(): print(f"The {name} decoder is {'available' if name in decoders else 'MISSING'}.") using ffmpeg_names("-decoders")
```
Existing lines to extend, quoted verbatim: `ENCODERS = {"libx264": "H.264 video encoder", "aac": "AAC audio encoder"}` and `FILTERS = ["scale", "crop", "zscale", "tonemap", "loudnorm", "drawtext"]` [VERIFIED: v2r/doctor.py:15-16]. `ffmpeg_names("-decoders")` parses the same way as `-encoders` (the `-decoders` rows have the same "flags name description" layout, confirmed for hevc, h264, aac, mjpeg, png on 6.1). `transpose`/`hflip`/`vflip` are what FFmpeg's autorotate inserts, so a build without them would break upright-ness silently. Normalize's start-up check should call `doctor.ffmpeg_names("-filters")` and `("-decoders")` once (two quick subprocess calls, no network) and refuse in one sentence if a name is missing; keep the network checks out of it (doctor's slow part). Put the lists in one place (doctor.py) and import them from normalize, so a test can assert that the built graphs use only listed names (split the graph on `;`, `,`, strip `[labels]`, take text before `=`).

### 5. The four-panel strip for the user's by-eye HDR choice (D-12)
Run on FFmpeg 6.1 against a real HLG clip; produced a 1080×480 PNG (four 270×480 panels, portrait clip). Panel 1 is visibly grey and flat (the "not converted" fault), panels 2-4 are natural, with hable the most contrasty and bluest sky, mobius and reinhard softer. Replace `5` with the second to look at and `CLIP` with the file. Panel order left to right: none, hable, mobius, reinhard.
```bash
TM(){ echo "zscale=h=480:w=-2:tin=arib-std-b67:pin=bt2020:min=bt2020nc:rin=tv:t=linear:npl=$2,format=gbrpf32le,zscale=p=bt709,tonemap=$1:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"; }
ffmpeg -hide_banner -loglevel error -nostdin -y -ss 5 -i CLIP -frames:v 1 -filter_complex "[0:v:0]split=4[a][b][c][d];[a]scale=-2:480,format=yuv420p[p1];[b]$(TM hable 203)[p2];[c]$(TM mobius 800)[p3];[d]$(TM reinhard 800)[p4];[p1][p2][p3][p4]hstack=4" strip.png
```
This uses a shell function, so as "one line" for the chat it is the whole `ffmpeg` command with the four `zscale...` chains written out, or (better) a documented `python3 -m v2r` helper; the planner should decide, and keep it out of EDITOR.md (it is a development aid for the Do-this step). The `drawtext` label is left out because the static 6.1 build used here lacks that filter; the sandbox has it (doctor report), but the panel order is easy to state in words. For a landscape clip the strip is 4552 px wide; reduce `480` if needed. Say to the user: look at skin, a sky and one strong colour (a red roof or brick) in panels 2-4; panel 1 must look grey (that is the fault); pick the one nearest the clip in Photos on the phone.

### 6. Test clip recipes (all generated by FFmpeg/Pillow, nothing committed)
```python
# tests/media.py (helper) - every recipe below ran on ffmpeg 6.1 and 8.0.1
BARS = "smptehdbars=size={w}x{h}:rate={fps}:duration={s}"
BEEP = "aevalsrc='0.5*sin(2*PI*1000*t)*lt(mod(t,1),0.2)':s=48000:d={s}"          # same beep test_join uses

def make_clip(path, w, h, seconds=2, fps=30, sound=True, rotate=None, hdr=None, ten_bit=True):
    # plain clip: [-f lavfi -i BARS] [-f lavfi -i BEEP if sound] [-an if not sound]
    #   hdr: add  -vf "setparams=color_primaries=bt2020:color_trc=arib-std-b67:colorspace=bt2020nc,format=yuv420p10le"
    #        (use color_trc=smpte2084 for PQ; ten_bit=False -> format=yuv420p, also valid and needs no 10-bit x264)
    #   -c:v libx264 -preset ultrafast -c:a aac
    # rotate: after writing a plain temp file, run
    #   ffmpeg -display_rotation 90 -i temp.mp4 -c copy path        (NOT -metadata:s:v rotate=90, which writes nothing)
    ...
# marker clip (orientation proof):  color=black:size=640x360:rate=30:duration=2,drawbox=x=0:y=0:w=120:h=120:color=white:t=fill
# 60 fps: rate=60 in BARS.  120 fps: rate=120.   no sound: -an and no BEEP input.
# variable frame rate (for "steady = false"): -vf "select='gt(random(1),0.35)'" -fps_mode passthrough
# photo: Pillow Image.new + ImageDraw box, save JPEG with exif orientation 6:  ex = Image.Exif(); ex[0x0112] = 6
#        HEIC: pillow_heif.register_heif_opener(); im.save("x.heic", "HEIF")   (bakes the orientation in)
# unreadable: a text file named x.mov ("not a video").  oversized: monkeypatch settings.MAX_ATTACHMENT_BYTES to a few bytes
#        (or file.truncate(settings.MAX_ATTACHMENT_BYTES + 1) for a sparse file); empty file also unreadable.
```
Generated clips come out as: HDR 10-bit -> `yuv420p10le, bt2020nc, arib-std-b67, bt2020`; plain generated clips carry `color_transfer: unknown` (normalize must treat that as SDR, not fail). The `aevalsrc` beep is mono; the output must still be stereo (`-ac 2`), a ready assertion. Keep each clip 2 s and 640×360 (or 360×640) so a whole parametrised run stays in seconds; the existing suite takes 40 s, mostly the 100 s join clips [VERIFIED: `uv run pytest -q`: 8 passed in 40.43s].

### 7. Draft EDITOR.md lines (proposal only; the user decides the text, D-16)
```
3. Normalize every clip and photo first. The sandbox stops any command after 2 minutes, so start it in the background:
   `nohup sh -c 'python3 -m v2r normalize --shape tall FILE1 FILE2 ...; echo "normalize finished with exit code $?"' > normalize.log 2>&1 &`
   (`--shape wide` only if the user asks for wide; list the files in the order they were attached). Read `normalize.log` every
   30 seconds until it says "normalize finished". It prints a line as each file is done and one sentence for any file it
   could not use; tell the user about those sentences in plain words. If it stops without "normalize finished", or says it
   ran out of room, ask the user to send fewer clips.
```
This copies the join's existing line (`nohup sh -c '...; echo "join finished with exit code $?"' > join.log 2>&1 &`) [VERIFIED: EDITOR.md:3]. The existing step 3 (join) is unchanged by this phase; where the new step goes in the handbook order is the user's call.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `-metadata:s:v rotate=90` to make a sideways test file | `-display_rotation 90` as an input option, then `-c copy` | FFmpeg 6.0 added the option; the metadata route writes nothing on 6.1 and 8.0.1 | the sideways test clip must use the two-step recipe |
| `-vsync cfr` | `-fps_mode cfr` | FFmpeg 5.1 deprecated `-vsync` | use `-fps_mode` (works on 6.1 and 8.0.1) |
| libplacebo for HDR to SDR | zscale + tonemap on CPU | not applicable in the sandbox (no GPU driver) | locked D-11; second-best, Dolby Vision layer ignored |
| `-loop 1` still images | single decode + `loop` filter | always better | 50x faster here |

**Deprecated/outdated:** `-metadata:s:v rotate=` for writing rotation (ignored by the mp4 muxer in these versions); `-vsync` (deprecated).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The sandbox's Ubuntu FFmpeg 6.1.1-3ubuntu5 behaves like the 6.1 static build used for these tests (same autorotate, `fps`, `apad whole_dur`, `loop`, zscale/tonemap behaviour). The doctor report confirms zscale/tonemap/libx264/aac exist, nothing more | Whole document | A command fails on the phone; the phone test and the grown doctor report are the check |
| A2 | `pip` in the sandbox (Ubuntu 24.04, Python 3.13.16, `--break-system-packages`) installs Pillow 12.3.0 and pillow-heif 1.8.1 from the cp313 manylinux wheels without a compiler. Wheels exist for x86_64 and aarch64 (manylinux_2_27/2_28); the sandbox's OS is inferred from the FFmpeg package name | Standard Stack | Photos unreadable on the phone; the lazy-import sentence keeps video working; CONTEXT already says "Check from the phone" |
| A3 | Apple's QuickLook rendering of an HLG frame is a good stand-in for "looks like her phone". Only mean luma and pixel error on four clips were measured; the user still decides by eye | Pitfall 5, Open Question 1 | The default tone-map pair feels too dark/bright; it is two numbers/names in settings.py |
| A4 | `TONEMAP_NPL_PQ = 100` for PQ sources is FFmpeg's documented recipe value, not calibrated; iPhones record HLG, so PQ clips are rare | Settings | PQ clips slightly off in brightness |
| A5 | iPhone slow-motion files that keep their native timing arrive as variable-rate (normal speed then 240 fps), so the median-frame-rate rule flags them; the local slow-motion fixture arrived already rendered at 30 fps and therefore will not flag. Not confirmed on a native file | NORM-04 | The flag rarely fires; D-04 already tells the phone test to check what slow-motion clips arrive as |
| A6 | A HEIC with several images (Live Photo, burst, depth map) opens as its primary image only; any extra images are ignored | Photos | None expected; not tested on such a file |
| A7 | Pillow's project age ("since 2010") | Package Legitimacy Audit | None; cosmetic |
| A8 | Sandbox speed is roughly 5 s of wall time per second of 4K HDR video on 2 processors (extrapolated from CPU seconds measured on the 8-core Mac); D-17 measured 3.3 on a pinned Mac | Pitfall 12 | Only affects how long the background run takes, not correctness |

## Open Questions (RESOLVED)

1. **Which tone-map starting pair: D-12's `mobius`, or `hable` with `TONEMAP_NPL = 203`?**
   - What we know: with the CONTEXT's `npl=1000` the picture is darker than Apple's QuickLook rendering (mobius@1000: 131/80/87/39 against 146/94/102/49, i.e. 10 to 15 levels; hable@1000 is 23 to 59 levels darker) and `npl=203` with mobius is too bright (196/132/138/70). `hable@203` came within 6 on all four clips; `mobius@800` is 4 to 8 levels darker. D-12 names `mobius` only as "to start", and the user decides by eye with the strip.
   - What's unclear: whether `hable`'s extra contrast looks right to her on a face (skin) — nobody has looked at faces yet.
   - Recommendation: add `TONEMAP_NPL` as a second setting (needed whatever is chosen), start with `hable`/203 (closest to Apple), tell the user plainly that this differs from D-12's `mobius` start and why, and have the strip compare hable@203, mobius@800, reinhard@800. If the user insists on `mobius` as the start, use `npl=800`, never 1000.
   - RESOLVED: on 2026-10-13 the user moved the start to `hable` with `TONEMAP_NPL = 203` (D-12 updated; 1000 is never used), so plan 02-01 starts there, and plan 02-07 still has the user confirm by eye from the four-panel strips (hable@203, mobius@800, reinhard@800) and writes the pick into settings.py and docs/decisions.md.
2. **Where does the HDR comparison command live?**
   - What we know: it is a one-off for the Do-this step, not part of the phone route.
   - Recommendation: give it to the user as a copy-paste command from the chat (Code Example 5 inlined); do not add a sub-command or put it in EDITOR.md.
   - RESOLVED: plan 02-07 (Task 1 step 5 and Task 2) gives the strip command to the user in the chat as a one-liner; no sub-command, nothing in EDITOR.md.
3. **What does the manifest do with a clip whose colour fell back (D-13)?**
   - Recommendation: `status: "done"` with a note in `notes` (and printed); not `skipped`.
   - RESOLVED: plan 02-04 Task 2 makes it status "done" with `colour_converted` false and the D-13 sentence in `notes` and in the log.
4. **Exit code.** Recommendation: 0 when at least one file converted (even if others were skipped), 1 when none did or the whole run failed (e.g. out of disk space, which should print "ran out of room; send fewer clips" per D-21).
   - RESOLVED: plan 02-01 Task 1 makes the CLI return 0 when at least one clip is done and 1 otherwise; plan 02-05 Task 1 adds the out-of-room stop (one sentence asking for fewer clips, exit 1).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| FFmpeg + ffprobe (Mac, development and tests) | all conversion tests | yes | 8.0.1 (evermeet build, libx264 with 10-bit, libx265) | — |
| FFmpeg 6.1 static build (scratchpad only, for this research) | checking 6.1 behaviour | yes (downloaded, not in the repo) | 6.1 | the phone's doctor report |
| FFmpeg in the sandbox | the phone route | yes (from docs/phone-limits.md) | 6.1.1-3ubuntu5, 2 processors, 7.9 GB free memory, zscale and tonemap present | — |
| `uv` | `uv add`, `uv sync`, tests | yes | 0.12.7 | — |
| Python 3.13 via uv | tests, package | yes | 3.13 (`.python-version`) | — |
| Pillow and pillow-heif | photos | not yet in the project; installable (PyPI reachable, wheels for macOS and Linux) | 12.3.0 / 1.8.1 | the lazy-import sentence; video unaffected |
| Network from the sandbox to pypi.org | pip install | yes (doctor report: "pypi.org can be reached.") | — | — |
| Hardware GPU / libplacebo | not used | no | — | zscale + tonemap (D-11) |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** Pillow/pillow-heif in the sandbox, until pip installs them from the phone's skill step (photos degrade to a plain sentence, video still works).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >=9.1.1 (dev dependency in pyproject.toml) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options] testpaths = ["tests"]` |
| Quick run command | `uv run pytest tests/test_normalize.py -x -q` |
| Full suite command | `uv run pytest -q` (currently 8 passed in about 40 s; the join's 100 s clips dominate) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| NORM-01 | facts: rotation 90 on the sideways clip and swapped upright size; fps 60; hdr `hlg`; sound true/false; shot_at read when present; original unchanged | unit/integration | `uv run pytest tests/test_normalize.py -k facts -x` | ❌ Wave 0 |
| NORM-02 | per shape: working copy is H.264 yuv420p, `30/1`, size == `working_size`, no rotation side data, bt709 tags, AAC 2 ch 48 kHz; marker lands in the expected corner; HDR flat patch Y=126 -> below 112 (converted, not relabelled); `working_size` table incl. odd sizes and both shapes | integration + unit | `uv run pytest tests/test_normalize.py -k "working or upright or hdr" -x` | ❌ Wave 0 |
| NORM-03 | JPEG with EXIF orientation 6 and a HEIC: upright full-size JPEG exists in work/, still clip is `PHOTO_SECONDS` x 30 frames with sound, manifest records both | integration | `uv run pytest tests/test_normalize.py -k photo -x` | ❌ Wave 0 |
| NORM-04 | 120 fps clip: `slow_motion` true, working copy length equals source length (real time), 30 fps; 60 fps clip: false | integration | `uv run pytest tests/test_normalize.py -k slow -x` | ❌ Wave 0 |
| NORM-05 | letters A, B, C in the given order including a skipped middle file; manifest keys; `convert_seconds` is a number; progress lines flushed (run via `subprocess` with output to a file and read mid-run is optional) | integration | `uv run pytest tests/test_normalize.py -k manifest -x` | ❌ Wave 0 |
| NORM-06 | oversized (monkeypatched `MAX_ATTACHMENT_BYTES`) and unreadable (text file, empty file) each give one sentence naming the file ("The second file, X, ...") and the others still convert; HDR fallback via bogus `settings.TONEMAP` gives a done clip with a note | integration | `uv run pytest tests/test_normalize.py -k "refuse or unreadable or fallback" -x` | ❌ Wave 0 |
| NORM-07 | SHA-256 and `st_mtime_ns` of every input unchanged; read-only inputs; an input inside work/ is skipped, not deleted | integration | `uv run pytest tests/test_normalize.py -k original -x` | ❌ Wave 0 |
| NORM-08 | every filter name in the built graphs is in `doctor.FILTERS`; decoder list present; generated clips cover sideways, 60 fps, no sound, HDR, 120 fps, photo (JPEG + HEIC), unreadable, oversized, in both shapes | unit | `uv run pytest tests/test_normalize.py -k doctor -x` | ❌ Wave 0 |

Test suite hygiene: give every `subprocess.run` of ffmpeg in tests a `timeout=` (Pitfall 2); parametrise `shape` over `["tall", "wide"]` like `test_join.py`; nothing assumes tall. Manual (by a person, in the phase's Do-this step, not automated): HDR working copy side by side with its original; a sideways clip upright; the silent and slow-motion clips play at normal speed; the phone test on branch `stage-14-normalize` with the rerun doctor report.

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_normalize.py -x -q`
- **Per wave merge:** `uv run pytest -q`
- **Phase gate:** full suite green before `/gsd-verify-work`, then the user's phone test before merging

### Wave 0 Gaps
- [ ] `tests/media.py` — shared generators (clip variants, marker clip, VFR clip, photo/HEIC maker, garbage file)
- [ ] `tests/test_normalize.py` — covers NORM-01 to NORM-08
- [ ] Framework install: `uv add pillow pillow-heif` (after the human-verify checkpoint; the photo tests need both, the HEIC test needs `pillow_heif.register_heif_opener()`)

## Security Domain

`security_enforcement` is enabled (absent = enabled) and `security_asvs_level` is 1 in `.planning/config.json`. This is a local command-line tool with no network input, accounts or secrets, so most categories do not apply; the real surface is hostile or malformed files and file paths.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | no accounts, no sign-in |
| V3 Session Management | no | none |
| V4 Access Control | no | single-user tool; originals are only ever read |
| V5 Input Validation | yes | validate before use: size cap from settings, Pillow-first sniffing, ffprobe must return a video stream, inputs resolved to absolute paths and passed after `-i`; a failed decode is a per-file sentence, never a crash |
| V6 Cryptography | no | none (SHA-256 appears only in tests, via `hashlib`) |
| V12 Files and Resources | yes | size limit before opening (D-20), outputs only under work/ with letter-derived names, no overwrite (`-n`), never execute or `eval` file content, Pillow's decompression-bomb guard left at its default |

### Known Threat Patterns for Python + FFmpeg + Pillow

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A file name starting with `-` read as an option by ffmpeg/ffprobe | Tampering | resolve to an absolute path; always `-i path`; never `shell=True`; arguments passed as a list |
| Input name used to build an output path or put into a filter graph | Tampering | output names are letters only; filter graphs never contain file names |
| Decompression bomb or huge image | Denial of service | `MAX_ATTACHMENT_BYTES` check first; leave `Image.MAX_IMAGE_PIXELS` at its default; any Pillow exception becomes "could not be read" |
| Malformed media crashing the decoder | Denial of service | one `ffmpeg`/`ffprobe` subprocess per file with captured stderr; failure isolated to that file |
| Location and device tags carried into working copies and then into a posted reel | Information disclosure | `-map_metadata -1 -map_chapters -1`; photos re-saved by Pillow without EXIF; the manifest records no GPS or device model (checked: the output of a real clip had no location tags even without the flag, but the flag makes it a guarantee) |
| File names or metadata read later by the chat's Claude as instructions (prompt injection through a file name) | Tampering | keep the manifest to facts; sentences quote the file name but the handbook treats log and manifest text as data (a note for the EDITOR.md draft) |
| Disk exhaustion by a long run | Denial of service | catch `OSError` with `errno.ENOSPC` as the whole-run sentence (D-21); manifest still lists what finished |

## Sources

### Primary (HIGH confidence)
- Local runs this session on FFmpeg 6.1 and ffprobe 6.1 (evermeet static builds, scratchpad only) and FFmpeg 8.0.1: rotation, autorotate direction, fps conversion, HDR chains (HLG, PQ, gamut-only, no-tag failure), silent audio, photo still clip, packet scan, tone-map calibration against QuickLook, strip image.
- Local runs of Pillow 12.3.0 and pillow-heif 1.8.1 (libheif 1.23.6) on a real iPhone HEIC and generated JPEG/HEIC.
- PyPI JSON API (pypi.org/pypi/pillow/json, pypi.org/pypi/pillow-heif/json): versions, dates, licences, wheel lists, `requires_dist`.
- Repo files read this session: `CLAUDE.md`, `.claude/CLAUDE.md`, `02-CONTEXT.md`, `REQUIREMENTS.md`, `STATE.md`, `v2r/__init__.py`, `v2r/__main__.py`, `v2r/settings.py`, `v2r/doctor.py`, `v2r/join.py`, `tests/test_join.py`, `tests/test_smoke.py`, `EDITOR.md`, `docs/phone-limits.md`, `docs/decisions.md`, `README.md`, `skill/vid2reel/SKILL.md`, `.gitignore`, `pyproject.toml`, `requirements.txt`, and the Stage 14 section of `docs/field-guide.html` (read only).
- github.com/bigcat88/pillow_heif `CHANGELOG.md` and `LICENSES_bundled.txt` (via raw.githubusercontent.com): 1.8.1 notes; bundled libheif LGPL-3.0, libde265 LGPL-3.0, x265 GPL-2.0.

### Secondary (MEDIUM confidence)
- github.com/bigcat88/pillow_heif README (platform and Python wheel matrix, BSD-3-Clause link).
- Web search on iPhone slow-motion timing (FFmpeg trac #2958 and related threads): slow-motion files are variable frame rate with a 1/600 timebase; used only to shape A5.

### Tertiary (LOW confidence)
- None used for a recommendation. The package-legitimacy seam reported `unknown-downloads` for both packages (no statistics available), which is why they are flagged.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — two locked libraries, versions and licences read from PyPI; legitimacy flag noted
- Architecture: HIGH — every command run end to end on 6.1 and 8.0.1, including a real 4K HDR clip and a real HEIC
- Pitfalls: HIGH — each of the numbered pitfalls was reproduced here (Pitfall 12 is extrapolated)
- HDR default look: MEDIUM — measured against Apple's rendering on four clips; the user's eye decides

**Research date:** 2026-10-13
**Valid until:** 2026-11-12 (FFmpeg 6.1 in the sandbox is stable; re-check pillow-heif's version line, 1.9 needs Pillow 13)

## Project Constraints (from CLAUDE.md)

Directives from `./CLAUDE.md` and `./.claude/CLAUDE.md` that the plan must honour (same authority as locked decisions):
- Tall and wide are first-class; no command, default or test may assume tall; `--shape` is required with no default (as `join` does).
- Every number that controls behaviour lives in `v2r/settings.py`, with its unit in a comment.
- Three jobs never mix: normalize converts and measures facts, decides nothing about the edit (no taste, no filters or colour looks beyond the plain HDR to SDR conversion); `v2r/normalize` converts every clip before anything else touches it.
- Originals are never modified; every output is a new file (NORM-07).
- Sandbox is the truth: Python and FFmpeg only, pip packages, github.com files only, no GPU, no paid services; any command stopped after 2 minutes; FFmpeg 6.1; limits in docs/phone-limits.md. After any change to how video is processed, tell the user to test from a phone before merging, and say exactly what to look or listen for and at what time.
- The assistant cannot watch video or hear audio: for this phase say what to look for (HDR copy beside the original: colours match, not grey, not neon, at the second the user picks; sideways clip upright from the first frame; the silent clip plays with no complaint; a 120/240 fps clip plays at normal speed, its length matching the original).
- Public repo: never commit video, photos or audio from fixtures/ or work/, anyone's name or account, or any secret; no attribution lines (no Co-Authored-By) in commits; this file and the other planning files must not name fixtures or people.
- Before writing something from scratch, check for a maintained open-source library, tell the user the licence, list it in `docs/licenses.md` (create it this phase: Pillow MIT-CMU, pillow-heif BSD-3-Clause with the bundled-library note).
- Record the settled working size in `docs/decisions.md` (one dated line, no person or account, "same as the guide's pick") and in CLAUDE.md's "Settled so far" line (D-01); never edit `docs/field-guide.html`.
- EDITOR.md: the user edits it; this phase only drafts lines for the user to approve (D-16); keep it short and plain, no code or taste inside.
- Phase and branch are named by guide stage: "Stage 14 – Normalize", branch `stage-14-normalize`; nothing merges into main until a reel has been made from a phone on the branch.
- Explain every change in plain English; the user is not a programmer.
- GSD workflow: file-changing work goes through a GSD command (this research only writes the RESEARCH.md).
