# Phase 2: Stage 14 - Normalize - Pattern Map

**Mapped:** 2026-10-13
**Files analyzed:** 14 (new or modified)
**Analogs found:** 11 / 14 (3 have no code analog: docs/licenses.md, Pillow photo half, manifest writer; use RESEARCH.md Code Examples 1-6)

Scope searched: v2r/, tests/, docs/, schema/, pyproject.toml, requirements.txt, .gitignore, EDITOR.md, CLAUDE.md. Nothing under fixtures/ or work/ was read. The whole codebase is 8 Python files, so every analog below was read in full.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `v2r/normalize.py` (new) | service | batch / file-I/O (per-file FFmpeg subprocess) | `v2r/join.py` | role-match (same job: probe, one FFmpeg list, error class, delete on failure) |
| `v2r/settings.py` (mod) | config | n/a | itself (`settings.py:8-32`) | exact |
| `v2r/doctor.py` (mod) | utility | request-response (reports) | itself (`doctor.py:15-36, 59-62`) | exact |
| `v2r/__main__.py` (mod) | route (CLI) | request-response | the `join` branch of itself (`__main__.py:16-39`) | exact |
| `tests/media.py` (new helper) | test utility | file-I/O | `make_clip`/`probe`/`peak_volume` in `tests/test_join.py:14-44` | role-match |
| `tests/test_normalize.py` (new) | test | file-I/O | `tests/test_join.py` | exact |
| `tests/test_smoke.py` (maybe mod) | test | request-response | itself | exact |
| `pyproject.toml`, `uv.lock` (mod) | config | n/a | `[dependency-groups]` block | partial (`dependencies = []` is empty today) |
| `requirements.txt` (mod, regenerated) | config | n/a | existing 2-line header file | exact (regenerate, never hand-edit) |
| `docs/licenses.md` (new) | doc | n/a | none | no analog |
| `docs/decisions.md` (mod) | doc | n/a | existing dated lines | exact |
| `CLAUDE.md` (mod, "Settled so far" sentence) | doc | n/a | itself | exact |
| `.gitignore` (mod) | config | n/a | `/join.log` line | exact |
| `EDITOR.md` (draft lines only, user decides) | doc | n/a | EDITOR.md line 3 (join nohup) | exact |

## Pattern Assignments

### `v2r/normalize.py` (service, batch / file-I/O)

**Analog:** `v2r/join.py`

**Imports and module docstring** (join.py:1-9). Use the same shape: one-line docstring, `subprocess`, then `from v2r import WORK_DIR, settings` (`v2r/__init__.py` defines `ROOT` and `WORK_DIR = ROOT / "work"`):
```python
"""`v2r join`: join video clips end to end into one tall or wide video in work/."""

import subprocess
from datetime import datetime

from v2r import WORK_DIR, settings

MIB = 1024 * 1024
```
Add `json, os, re, statistics, time` from the standard library. Import `pillow_heif`/`PIL` lazily inside the photo function only (RESEARCH Pitfall 11, "Photos could not be read because the picture library is not installed.").

**Plain-English error class** (join.py:11-12):
```python
class JoinError(Exception):
    """The join can't make a file that fits; the message says why in plain English."""
```
Copy as `NormalizeError`.

**Public function signature: shape has no default, out_dir defaults to WORK_DIR** (join.py:15-25):
```python
def join(videos, shape, out_dir=WORK_DIR):
    """... `shape` is "tall" or "wide" (see settings.SHAPES); there is deliberately no default. ..."""
    ...
    out_dir.mkdir(parents=True, exist_ok=True)
```
So `normalize(files, shape, out_dir=WORK_DIR)` (tests pass `tmp_path`, as `test_join.py:64` does).

**FFmpeg command as a Python list, `-n`, `+faststart`, delete on failure** (join.py:39-54):
```python
command = [
    "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
    ...
    "-c:v", "libx264", "-pix_fmt", "yuv420p",  # 8-bit 4:2:0 so every player can show it
    "-c:a", "aac", "-b:a", str(settings.AUDIO_BITRATE),
    "-movflags", "+faststart",  # index at the front, so playback starts immediately
    str(output),
]
try:
    subprocess.run(command, check=True)
except subprocess.CalledProcessError:
    output.unlink(missing_ok=True)
    raise
```
Deviation to carry: normalize must capture stderr (`capture_output=True, text=True`) and keep its tail in a `detail` field instead of letting raw FFmpeg text reach the log (RESEARCH anti-pattern). Use `-fps_mode cfr`, `-t D`, `-map_metadata -1`; full chain in RESEARCH Code Examples 2 and 3 (copy from there, do not retype the filter strings differently).

**ffprobe call shape** (join.py:84-90):
```python
def duration(video):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
        stdout=subprocess.PIPE, text=True, check=True,
    ).stdout
    return float(out)
```
Normalize's fuller probe is RESEARCH Code Example 1 (`-of json`, `json.loads`, first video stream, `side_data_list` rotation, packet scan with `statistics.median`).

**Pure helper functions** (join.py:93-99): `even(x)` rounds to nearest even, which can round up past a cap. Do NOT reuse it for the size cap; RESEARCH Pattern 1 `working_size` floors to even (`int(x) // 2 * 2`). Reuse the `minutes()` style of tiny pure helpers with one-line docstrings.

**Unique naming** (join.py:102-110): `new_path()` avoids collisions. Normalize does the opposite on purpose (D-18: a new run replaces last run's `^[A-Z]{1,3}(-photo)?\.(mp4|jpg)$` files and `manifest.json` in `work/`, never `join-*.mp4`); outputs are named by letter only (`A.mp4`, `C-photo.jpg`), never from the input name. Because `-n` refuses to overwrite, delete the previous lettered files first.

**Autorotate comment to keep** (join.py:30): "FFmpeg has already turned upright and sideways clips the right way up (autorotate)." Normalize reads rotation only to compute the upright size; no `transpose`, no `-noautorotate`.

**Error to sentence conversion** is done in `__main__.py` for join (see below); normalize instead converts per file inside the loop (RESEARCH Pattern 3) so one bad file never stops the others, and writes the sentence to the log and the manifest entry. Sentence style from join.py:78-81:
```python
raise JoinError(
    f"A {shape} video can be at most {minutes(longest)} long to come back under the "
    f"{settings.MAX_RESULT_BYTES / MIB:.0f} MiB limit; these clips add up to {minutes(seconds)}, so nothing was built."
)
```
Plain, specific, ends with what happened ("so nothing was built"). Normalize sentences: "The second file, IMG_4423.MOV, could not be read as a video or a photo."

**Progress output:** join prints once at the end; normalize must `print(line, flush=True)` after every file (RESEARCH Pitfall 8) and rewrite the manifest with temp file plus `os.replace`. No analog in the repo for either; take from RESEARCH Pattern 4.

---

### `v2r/settings.py` (config)

**Analog:** itself. Convention (settings.py:1-6 docstring, then one `# command:` header comment per group, every value carrying a unit comment):
```python
# join: the finished video's frame, as (width, height) in pixels
SHAPES = {
    "tall": (1080, 1920),  # short-form
    "wide": (1920, 1080),  # longer-form YouTube
}
OUTPUT_FPS = 30  # frames per second

# join: fitting the result under MAX_RESULT_BYTES (below, with the phone limits)
AUDIO_BITRATE = 128_000  # bits per second of AAC sound
```
Add a `# normalize:` group using the exact block in RESEARCH "Settings to add" (`WORKING_SIZE`, `PHOTO_SECONDS`, `PHOTO_JPEG_QUALITY`, `X264_PRESET`, `X264_CRF`, `WORKING_AUDIO_BITRATE`, `AUDIO_RATE`, `TONEMAP`, `TONEMAP_NPL`, `TONEMAP_NPL_PQ`, `SLOW_MOTION_MIN_FPS`, `STEADY_TOLERANCE`). Place it between the join group and `# doctor` (line 26). Do not touch `MAX_ATTACHMENT_BYTES` / `MAX_ATTACHMENTS` (lines 30-31; the latter is deliberately unenforced, D-21). Tests monkeypatch `settings.X` and normalize must read `settings.X` at call time (as join does, `settings.OUTPUT_FPS`), never `from v2r.settings import X`.

---

### `v2r/doctor.py` (utility, report)

**Analog:** itself.

**Lists to grow** (doctor.py:15-16):
```python
ENCODERS = {"libx264": "H.264 video encoder", "aac": "AAC audio encoder"}
FILTERS = ["scale", "crop", "zscale", "tonemap", "loudnorm", "drawtext"]
```
Extend `FILTERS` with `format, fps, setsar, setpts, loop, transpose, hflip, vflip, aresample, apad, anullsrc` and add `DECODERS = ["hevc", "h264", "aac", "mjpeg", "png"]` (RESEARCH Code Example 4).

**Report loop to copy for decoders** (doctor.py:28-34):
```python
if ffmpeg:
    encoders = ffmpeg_names("-encoders")
    for name, what in ENCODERS.items():
        print(f"The {what} ({name}) is {'available' if name in encoders else 'MISSING'}.")
    filters = ffmpeg_names("-filters")
    for name in FILTERS:
        print(f"The {name} filter is {'available' if name in filters else 'MISSING'}.")
```
Add `decoders = ffmpeg_names("-decoders")` and a matching `The {name} decoder is available/MISSING.` loop. `ffmpeg_names(option)` (doctor.py:59-62) already works for `-decoders` (takes `line.split()[1]`). Normalize's start-up check should import `doctor.FILTERS`/`DECODERS` and call `doctor.ffmpeg_names` once, so the lists live in one place (NORM-08 test: every filter in the built graphs is in `doctor.FILTERS`).

---

### `v2r/__main__.py` (route / CLI)

**Analog:** the `join` sub-command in the same file.

**Parser block to copy** (__main__.py:16-23):
```python
join_parser = commands.add_parser("join", help="join videos into one MP4 in work/")
join_parser.add_argument(
    "--shape",
    required=True,
    choices=list(settings.SHAPES),
    help=" or ".join(f"{name} ({w}x{h})" for name, (w, h) in settings.SHAPES.items()) + "; there is no default",
)
join_parser.add_argument("videos", nargs="+", type=Path, help="video files, in the order to join them")
```
Add `normalize_parser` identically, positional `files` (`nargs="+", type=Path`), help "files, in the order they were attached; they get the letters A, B, C...". Add `normalize` to the import line (`from v2r import __version__, build_skill, doctor, join, normalize, settings`).

**Dispatch and exit codes** (__main__.py:29-39):
```python
elif args.command == "join":
    try:
        output, summary = join.join(args.videos, args.shape)
    except join.JoinError as error:
        print(f"v2r join: {error}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError:
        print("v2r join: FFmpeg failed; its error is shown above.", file=sys.stderr)
        return 1
    print(summary)
    print(output)
```
Copy the `v2r normalize: ...` prefix and `return 1` on whole-run failure (e.g. `NormalizeError`, `OSError` ENOSPC with the "send fewer clips" sentence, D-21). Exit 0 when at least one file converted, 1 otherwise (RESEARCH Open Question 4). `main(argv)` returns an int and `raise SystemExit(main())` stays at the bottom (line 47-48). Note: stdout lines must be flushed (log is redirected to a file).

---

### `tests/media.py` (test helper) and `tests/test_normalize.py` (test, file-I/O)

**Analog:** `tests/test_join.py`.

**Generated clip with FFmpeg** (test_join.py:14-26): base for `make_clip`; RESEARCH Code Example 6 lists the variants (rotate via two-step `-display_rotation`, `hdr=` via `setparams`, `fps`, `sound=False`, marker clip, VFR, JPEG with EXIF orientation 6, HEIC, text file named x.mov):
```python
def make_clip(path, width, height, seconds=CLIP_SECONDS):
    bars = (
        f"smptehdbars=size={width}x{height}:rate={settings.OUTPUT_FPS}:duration={seconds},"
        "drawtext=text='%{pts\\:hms}':fontsize=h/8:fontcolor=white:box=1:boxcolor=black:x=(w-tw)/2:y=(h-th)/2"
    )
    beep = f"aevalsrc='0.5*sin(2*PI*1000*t)*lt(mod(t,1),0.2)':s=48000:d={seconds}"
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-nostdin", "-f", "lavfi", "-i", bars, "-f", "lavfi", "-i", beep,
         "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", str(path)],
        check=True,
    )
    return path
```
New helper must add `timeout=` to every ffmpeg call (RESEARCH Pitfall 2) and must not require `drawtext` for the HDR/marker clips (keep them simple). Do not edit test_join.py; `tests/` has no `__init__.py`, so `from media import make_clip` works under pytest.

**probe and peak_volume helpers** (test_join.py:29-44): copy into `media.py` and widen the `-show_entries` to include `codec_name,pix_fmt,r_frame_rate,channels,sample_rate,color_transfer,color_space` and `stream_side_data=rotation` so tests can assert H.264/yuv420p/`30/1`/AAC 2 ch 48 kHz/no rotation:
```python
def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(out)
```

**Fixtures, module-scoped, generated into tmp** (test_join.py:47-59):
```python
@pytest.fixture(scope="module")
def clips(tmp_path_factory):
    folder = tmp_path_factory.mktemp("clips")
    return [make_clip(folder / "wide.mp4", 640, 360), make_clip(folder / "tall.mp4", 360, 640)]
```

**Parametrised over both shapes, out_dir=tmp_path** (test_join.py:62-71):
```python
@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_join_makes_one_video_with_sound(clips, shape, tmp_path):
    result, _ = join(clips, shape, out_dir=tmp_path)

    info = probe(result)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    assert (video["width"], video["height"]) == settings.SHAPES[shape]
    assert float(info["format"]["duration"]) == pytest.approx(2 * CLIP_SECONDS, abs=0.1)
    assert any(s["codec_type"] == "audio" for s in info["streams"])
    assert peak_volume(result) > -20
```
Use `["tall", "wide"]` literally, never assume tall. For expected sizes compare to `normalize.working_size(shape, w, h)` plus the fixed table in RESEARCH Pattern 1.

**Refusal test shape** (test_join.py:89-93):
```python
with pytest.raises(JoinError, match="can be at most"):
    join([long_clips[shape]] * 3, shape, out_dir=tmp_path)
assert not any(tmp_path.iterdir())
```
Normalize analog: refusals are manifest entries, not exceptions, so assert `entry["status"] == "skipped"`, the sentence names the file ("The second file, X"), and the other letters still converted. Oversized: `monkeypatch.setattr(settings, "MAX_ATTACHMENT_BYTES", 10)`. Keep clips 2 s and 640x360 so the suite stays fast (join's 100 s clips already dominate the 40 s run).

**Smoke test** (test_smoke.py:12-13): `main([])` must still return 0 with the new sub-command registered; no change needed unless adding a `main(["normalize"])` missing-arguments check.

---

### `pyproject.toml`, `uv.lock`, `requirements.txt`

**Analog:** `pyproject.toml` has `dependencies = []` (line 7). Run `uv add pillow pillow-heif` (pin pillow-heif below 1.9 per RESEARCH), then regenerate with the exact command in README.md (RESEARCH quotes it: `uv export --format requirements-txt --no-dev --no-emit-project --no-hashes -o requirements.txt`). requirements.txt is only two header comment lines today; never hand-edit it. The RESEARCH package audit flags both packages SUS: the plan needs a `checkpoint:human-verify` before install.

---

### `.gitignore`

**Analog:** the Never-committed block (lines 1-4):
```
/work/
/fixtures/
/join.log
```
Add `/normalize.log` on the line after `/join.log`. Note the media rules (lines 6-45) ignore `*.jpg`, `*.heic` etc. everywhere except `tests/**` and `music/**` (`!/tests/**`), so generated test photos are never committed by accident, but nothing under tests/ should be committed anyway: generate into `tmp_path`.

---

### `docs/decisions.md`, `CLAUDE.md`

**Analog:** existing lines in decisions.md, format `- YYYY-MM-DD · Stage N · what was decided and how it differs from the guide.` Example:
```
- 2026-10-12 · Stage 11 · `MAX_ATTACHMENT_BYTES` is 400 MB, the app's warning point, with no margin below it, because a 408.7 MB file arrived. ...
```
Add a line for D-01: `- 2026-10-13 · Stage 14 · The working size is reel-sized (tall: portrait at most 1080x1920, landscape at most 1920 high; wide: landscape at most 1920x1080, portrait at most 1920 wide; never scaled up), same as the guide's pick.` Never name a person or account. Likewise extend CLAUDE.md's "Settled so far:" sentence (grep `Settled so far` in CLAUDE.md) with "the working size is reel-sized (Stage 14)". Also candidates for decisions lines where the build differs from the guide: `TONEMAP_NPL` second setting and hable-vs-mobius if the user picks, D-21 (10 attachments not enforced).

---

### `EDITOR.md` (draft only; the user decides the text, D-16)

**Analog:** EDITOR.md line 3 (the join step):
```
3. Join them in the order they were attached; ... start the join in the background: `nohup sh -c 'python3 -m v2r join --shape tall FILE1 FILE2 ...; echo "join finished with exit code $?"' > join.log 2>&1 &`, using `--shape wide` instead only if the user asks for wide. Then read `join.log` every 30 seconds until it says "join finished", and use what it printed.
```
The draft normalize step is RESEARCH Code Example 7; same structure with `normalize.log` and "normalize finished". The planner must make a human checkpoint task for this, not an automatic edit.

---

### `docs/licenses.md` (new)

No analog (docs/ holds decisions.md, phone-limits.md, field-guide.html). Follow decisions.md tone: short, plain English, no names. Content from RESEARCH: Pillow MIT-CMU, pillow-heif BSD-3-Clause, plus one line that pillow-heif's wheels bundle libheif (LGPL-3.0), libde265 (LGPL-3.0) and x265 (GPL-2.0), downloaded by pip at run time, not redistributed by this repo. Include what each is used for and the source URL.

## Shared Patterns

### One FFmpeg command per output, built as a list, never `shell=True`
**Source:** `v2r/join.py:39-54`. Apply to every ffmpeg/ffprobe call in `normalize.py` and to test helpers. Always `-hide_banner -loglevel error -nostdin -n`; inputs absolute and passed after `-i`; file names never enter a filter graph or an output path.

### Shape is required, never defaulted, never assumed tall
**Source:** `v2r/__main__.py:17-22` (argparse `required=True, choices=list(settings.SHAPES)`), `join.py:15-18`. Apply to the CLI, to `normalize()`, to every test (`@pytest.mark.parametrize("shape", ["tall", "wide"])`, `test_join.py:62`).

### Every number from `settings`, read at call time
**Source:** `v2r/settings.py` and `join.py:23,46,57` (`settings.OUTPUT_FPS`, `settings.AUDIO_BITRATE`, `settings.MAX_RESULT_BYTES`). Apply to all of normalize.py; no literal 30, 48000, 4, 1080, 400 MB in code.

### Errors are one plain sentence; the real cause stays out of the log
**Source:** `join.py:11-12, 59-60, 78-81` and `__main__.py:32-36` ("FFmpeg failed; its error is shown above."). For normalize: per-file sentences go to the log and the manifest entry; subprocess stderr is captured and kept in a `detail` field rather than printed.

### Output deleted on failure, originals never opened for writing
**Source:** `join.py:50-54` (`output.unlink(missing_ok=True)` then re-raise). Apply to each working copy and photo copy; D-05/NORM-07: inputs only read, outputs only under `out_dir`, skip any input that resolves inside `out_dir`.

### Tests generate media with FFmpeg into `tmp_path`, probe it, assert facts
**Source:** `tests/test_join.py:14-71`. Apply to all of test_normalize.py; nothing from fixtures/ or work/ is ever read, and every ffmpeg call in tests gets a `timeout=`.

## No Analog Found

| File / part | Role | Data Flow | Reason |
|---|---|---|---|
| Pillow / pillow-heif photo half of `normalize.py` | service | file-I/O | No image code exists yet; use RESEARCH Code Example 3 (Pillow half) |
| Manifest writer (temp file plus `os.replace`, `finished` flag, flushed progress lines) | utility | batch | join writes no JSON and prints once at the end; use RESEARCH Pattern 4 and "Manifest shape" |
| ffprobe JSON and packet scan | utility | transform | join only reads `format=duration` as csv; use RESEARCH Code Example 1 |
| `docs/licenses.md` | doc | n/a | file does not exist yet |
| four-panel HDR strip command | dev aid | transform | not a repo file; RESEARCH Code Example 5, given to the user in chat, not added to EDITOR.md |

## Metadata

**Analog search scope:** v2r/, tests/, docs/ (decisions.md only), pyproject.toml, .gitignore, EDITOR.md line 3, CLAUDE.md
**Files scanned:** 12 (all code in the repo; whole files read once)
**Pattern extraction date:** 2026-10-13
