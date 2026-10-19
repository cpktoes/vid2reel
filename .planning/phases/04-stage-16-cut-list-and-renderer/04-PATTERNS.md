# Phase 4: Stage 16 - Cut list and renderer - Pattern Map

**Mapped:** 2026-10-19
**Files analyzed:** 22 new or modified
**Analogs found:** 19 / 22 (3 have no analog: schema, plan.py geometry/gain curve, FFmpeg move/sound graphs; RESEARCH.md recipes apply)

Notes on the repo as it is today: `v2r/render/__init__.py` exists and is empty (0 lines). `schema/` holds only `.gitkeep`. There is no `jsonschema` use yet. `SheetBook` hard-codes `sheets/sheet-NN.jpg` (sheets.py lines 169, 191, 211). Line numbers below are from the files as read on 2026-10-19.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `schema/cutlist.schema.json` | config (schema) | transform | none (docstring of `v2r/look/__init__.py` documents the frozen names) | no analog |
| `v2r/settings.py` (modify) | config | n/a | its own `# look:` block (lines 61-117) | exact |
| `v2r/__main__.py` (modify) | route (CLI) | request-response | the `look` and `normalize` branches (lines 38-43, 60-73) | exact |
| `v2r/doctor.py` (modify) | utility | request-response | `FILTERS` / `missing_ffmpeg_features` (lines 15-22, 74-97) | exact |
| `v2r/render/__init__.py` | service (orchestrator) | batch, file-I/O | `v2r/look/__init__.py` `look()` (lines 263-376) and `v2r/join.py` `join()` | exact |
| `v2r/render/plan.py` | utility (pure) | transform | `v2r/join.py` `fit()`/`even()` and `v2r/look/pick.py` `frame_number`/`base_times` | role-match |
| `v2r/render/check.py` | service | request-response | `v2r/look/__init__.py` `read_manifest()` + `working_facts()` (lines 109-128, 156-181) | role-match |
| `v2r/render/match.py` | service | transform, file-I/O | `v2r/look/__init__.py` `write_look()` and `v2r/look/measure.py` `overall_of` | role-match |
| `v2r/render/video.py` | service | file-I/O (FFmpeg) | `v2r/normalize.py` `video_command` / `run_ffmpeg` / `photo_command` | role-match |
| `v2r/render/sound.py` | service | file-I/O (FFmpeg) | `v2r/look/measure.py` `measure_loudness` (ebur128 reading) | partial |
| `v2r/render/proof.py` | service | file-I/O | `v2r/look/sheets.py` `grab_stills` + `SheetBook` | exact (reuse) |
| `v2r/look/sheets.py` (modify `SheetBook`) | utility | file-I/O | itself | exact |
| `docs/decisions.md`, `docs/licenses.md`, `CLAUDE.md` | docs | n/a | existing rows/lines in each | exact |
| `pyproject.toml`, `uv.lock`, `requirements.txt` (modify) | config | n/a | README.md regenerate command | exact |
| `tests/media.py` (modify: new helpers) | test helper | file-I/O | `make_look_clip`, `make_manifest`, `make_clip` (lines 21-141, 310+) | exact |
| `tests/test_cutlist_check.py` | test | request-response | `tests/test_look.py` (run tests with `make_work`/`make_manifest`) | exact |
| `tests/test_match.py` | test | transform | `tests/test_look.py` | role-match |
| `tests/test_render_plan.py` | test | transform | `tests/test_look.py` `test_base_times`, `test_half_count` (pure tests) | role-match |
| `tests/test_render_video.py`, `test_render_sound.py` | test | file-I/O | `tests/test_join.py` (probe, `peak_volume`) | role-match |
| `tests/test_render_golden.py` | test | file-I/O | `tests/test_join.py` parametrised tall/wide tests | role-match |
| `tests/test_doctor.py`, `tests/test_look_sheets.py` (modify) | test | request-response | themselves | exact |
| `tests/test_settings` unit-comment guard (extend) | test | transform | `test_look_settings_have_unit_comments` (test_look.py 528-542) | exact |

## Pattern Assignments

### `v2r/settings.py` (config, modify)

**Analog:** the `# look:` block, lines 61-117. New numbers go in a block headed `# render:` (and `# match:`), placed before `# doctor` (line 119). The unit-comment guard `test_look_settings_have_unit_comments` reads between the `# look:` and `# doctor` lines, so a new block must not sit between them unless the guard's count (45) is changed on purpose; put the new block after `# doctor`'s predecessor line only if the guard is extended. Safest: put `# render:` after the phone limits at the end of the file, or extend the guard.

**Style to copy** (lines 85-90, 117):
```python
LABEL_DECIMALS = 1  # decimal places of seconds on a still's label ... such as A 03.0 (D-02)
SHEET_MAX_BYTES = 1_500_000  # bytes: a sheet larger than this is saved again at lower quality
CHROMA_NEUTRAL = 128  # 8-bit code value of grey in video chroma (a fact of the format): the colour cast is the offset from it
```
Every line: `NAME = value  # unit: what it does`. Lists with an own comment line above (FIT_STEPS lines 18-24). New names from CONTEXT/RESEARCH: `MOVE_AMOUNT = 0.04`, `TOUCH_UP_MAX_BRIGHTNESS = 8`, `TOUCH_UP_MAX_COLOUR = 4`, `TOUCH_UP_SATURATION = (0.92, 1.08)`, `LOUDNESS_TARGET = -14`, `TRUE_PEAK_CEILING = -1`, `FADE_IN_DEFAULT`, `FADE_OUT_DEFAULT = 1.5`, `MUSIC_DROP_RAMP`, `MIN_REEL_SECONDS`, `CROP_NOTE_SHARE`, `RENDER_PIECE_CRF = 10`, `RENDER_X264_PRESET`, `RENDER_X264_CRF = 20`, `RENDER_SECONDS_PER_SECOND`. Reuse existing `OUTPUT_FPS`, `AUDIO_RATE`, `AUDIO_BITRATE`, `FIT_STEPS`, `FIT_HEADROOM`, `MAX_RESULT_BYTES`, `SILENCE_LUFS`, `PHOTO_SECONDS`, `CHROMA_NEUTRAL`, `SHEET_*`.

---

### `v2r/__main__.py` (route/CLI, modify)

**Analog:** the `look` subparser and branch.

**Parser pattern** (lines 38-43):
```python
look_parser = commands.add_parser(
    "look", help="make contact sheets and measurements of the working copies in work/", allow_abbrev=False)
look_parser.add_argument(
    "work", nargs="?", type=Path, default=None,
    help="the work folder that holds manifest.json; leave out for work/ in this repo",
)
```
Add `check`, `match`, `render` the same way: `allow_abbrev=False`, a `work` optional positional, plus an optional cut-list path (default `work/cutlist.json`). No `--shape` (the shape comes from the manifest and the list's canvas, never from a default).

**Dispatch + error pattern** (lines 67-73, join's 49-59):
```python
elif args.command == "look":
    try:
        result = look.look(args.work)
    except look.LookError as error:
        print(f"v2r look: {error}", file=sys.stderr)
        return 1
    return 0 if any(clip["status"] == "done" for clip in result["clips"]) else 1
```
and join's extra branch (line 55): `except subprocess.CalledProcessError: print("v2r join: FFmpeg failed; its error is shown above.", file=sys.stderr); return 1`. Imports line 8 grows: `from v2r import __version__, build_skill, doctor, join, look, normalize, render, settings`. Exit rule: `check` returns 1 when any problem (notes alone return 0); `render` returns 1 on refusal or failure.

---

### `v2r/doctor.py` (utility, modify)

**Analog:** `FILTERS` (lines 16-21) and `missing_ffmpeg_features(encoders=None, filters=None, decoders=None)` (lines 74-97).

```python
FILTERS = [
    "scale", "crop", "zscale", "tonemap", "loudnorm", "drawtext",
    "format", "fps", "setsar", "setpts", "loop", "transpose", "hflip", "vflip", "aresample", "apad", "anullsrc",
    # the filters `v2r look` measures with (fps and scale are listed above)
    "select", "signalstats", "blurdetect", "scdet", "deshake", "ebur128", "metadata", "ametadata",
]
```
Append a third commented group: `# the filters v2r render builds with` -> `"trim", "atrim", "asetpts", "perspective", "lutyuv", "setparams", "afade", "amix", "amultiply", "aevalsrc", "sine", "volume", "aformat", "concat"` (only ones the chosen chains use). Also add `muxers`/`demuxers` lists (`matroska`, `concat`) with a new `ffmpeg_names("-muxers")` / `"-demuxers"` call: `ffmpeg_names` already parses the same way (line 68-71: `{line.split()[1] ...}`). Extend `missing_ffmpeg_features` with `muxers=None, demuxers=None` keeping the existing "the {name} filter" phrase style (line 95). `tests/test_doctor.py` asserts `"MISSING" not in out` and `missing_ffmpeg_features() == []` here, so every name added must exist in FFmpeg 6.1.

---

### `v2r/render/__init__.py` (service/orchestrator, batch + file-I/O)

**Analogs:** `v2r/look/__init__.py` `look()` for run shape, error class, whole-or-nothing, scratch folder clean-up, one-line-per-item printing; `v2r/join.py` `join()` for the fit/size/closing-sentence pattern.

**Imports + error class + temp-prefix** (look/__init__.py 40-66):
```python
from v2r import WORK_DIR, doctor, settings
from v2r.look import measure, pick, sheets
...
LOOK_TEMP_PREFIX = ".v2r-look-"  # a hidden folder in the work folder holds the clip being looked at's scratch files
LAST_LOOK_TEMP = re.compile(r"^\.v2r-look-[A-Za-z0-9_]+$")  # the prefix and what tempfile adds, and nothing else
class LookError(Exception):
    """The whole run can't go on; the message is one plain sentence."""
```
Copy as `RenderError`, `RENDER_TEMP_PREFIX = ".v2r-render-"`, `LAST_RENDER_TEMP = re.compile(r"^\.v2r-render-[A-Za-z0-9_]+$")`.

**Clean-up of leftovers** (look/__init__.py 87-106): only real directories directly in the work folder whose whole name matches, `shutil.rmtree(entry, ignore_errors=True)`, `not entry.is_symlink()`. Copy that, and delete the scratch folder in `finally`.

**Run shape** (look/__init__.py 263-300): read the manifest first (error if missing, before deleting anything), `shutil.which("ffmpeg") is None` -> error sentence, print missing-piece sentences with `flush=True`, whole-or-nothing writes, `OSError` with `errno.ENOSPC` handled as its own sentence (lines 317-322, 364-374 of look; normalize.OUT_OF_ROOM line 67).

**Fit + build + closing sentence** (join.py 15-65). Copy exactly this order:
```python
seconds = sum(duration(video) for video in videos)
width, height, bitrate = fit(shape, seconds)  # raises JoinError before anything is built
...
command = [
    "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
    ...
    "-c:v", "libx264", "-pix_fmt", "yuv420p",
    "-maxrate", str(bitrate), "-bufsize", str(bitrate),
    "-c:a", "aac", "-b:a", str(settings.AUDIO_BITRATE),
    "-movflags", "+faststart",
    str(output),
]
try:
    subprocess.run(command, check=True)
except subprocess.CalledProcessError:
    output.unlink(missing_ok=True)
    raise
size = output.stat().st_size
if size > settings.MAX_RESULT_BYTES:
    output.unlink()
    raise JoinError(f"The video came out at {size / MIB:.1f} MiB, over the {limit:.0f} MiB limit, so it was deleted.")
```
Reuse `join.fit(shape, seconds)` unchanged (it returns `(width, height, bitrate)` and raises `JoinError`; catch it and re-raise as `RenderError`, or let `__main__` catch both). "Quality stepped down" is detected by comparing the returned `(width, height)` with `settings.SHAPES[shape]`. Also reuse `join.new_path` style (join.py 102-110) for the output name (`reel-{shape}-{stamp}.mp4`) and `join.MIB`, `join.even`, `join.minutes`.

**Run each FFmpeg piece whole-or-nothing** (normalize.py 317-340):
```python
def part_path(final):
    final = Path(final)
    return final.with_name(f"{final.stem}.part{final.suffix}")

def ffmpeg_timeout(seconds):
    return settings.FFMPEG_TIMEOUT_FLOOR + settings.FFMPEG_SECONDS_PER_SECOND * seconds

def run_ffmpeg(command, part, final, timeout):
    try:
        subprocess.run(command, capture_output=True, text=True, check=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        Path(part).unlink(missing_ok=True)
        raise
    except subprocess.CalledProcessError as error:
        Path(part).unlink(missing_ok=True)
        if NO_ROOM_TEXT in (error.stderr or ""):
            raise OSError(errno.ENOSPC, NO_ROOM_TEXT) from error
        raise
    os.replace(part, final)
```
Call `normalize.run_ffmpeg`, `normalize.part_path`, `normalize.ffmpeg_timeout` directly (do not copy). Use `normalize.clean_text` (lines 70-86) for any text echoed from the list or manifest in a sentence.

**Printing**: one `print(..., flush=True)` sentence per step, as look prints `"{letter} looked at in N s, ..."` (look 355-357). Render prints a progress line per segment and ends with one sentence naming file, size, frame size and loudness (D-27).

---

### `v2r/render/plan.py` (utility, pure transform)

**Analogs (partial):** `v2r/look/pick.py` for frame arithmetic, `v2r/join.py` for `even`.

**Frame helper style** (pick.py lines 9-17 `frame_number(t, fps, seconds)`; `clock` lines 273-277):
```python
def clock(t):
    """A time as a label writes it, such as 04.5: two digits of whole seconds, then LABEL_DECIMALS decimals."""
    decimals = settings.LABEL_DECIMALS
    width = 3 + decimals if decimals > 0 else 2
    return f"{t:0{width}.{decimals}f}"
```
Reuse `pick.clock` for proof-sheet reel times. The rounding rule (`math.floor(round(seconds * fps, 6) + 0.5)`), crop geometry, move windows and music gain curve are specified in RESEARCH.md Patterns 1, 2, 3, 6; there is no repo analog for those. Reuse `join.even` (`round(x / 2) * 2`, join.py 93-94) or define a local `even` that clamps; RESEARCH uses `even(clamp(...))`. No I/O, no FFmpeg, no settings mutation: take `fps`/caps from `settings` at call time (the look tests monkeypatch settings values, so read them inside functions, not at import).

---

### `v2r/render/check.py` (service, request-response)

**Analog:** `v2r/look/__init__.py` `read_manifest()` (lines 109-128) and `working_facts()` (156-181).

**Manifest reading** (copy shape; `look.read_manifest` can be reused directly, it raises `LookError`, so wrap or reuse its logic with check's own sentences):
```python
path = Path(work_dir) / "manifest.json"
if not path.is_file():
    raise LookError(NO_MANIFEST)
try:
    manifest = json.loads(path.read_text(encoding="utf-8"))
except (OSError, ValueError) as error:
    raise LookError(UNREADABLE_MANIFEST) from error
```
Fixed sentences as module constants (`NO_MANIFEST = "There is no manifest.json in the work folder yet, so normalize has to run before look."`, lines 56-59).

**Working-copy validation** (look 156-181): `working.file` must be a plain name, not starting with `.`, `Path(name).name == name`, and `path.resolve().parent == folder.resolve()`; length via `measure.finite(...)`; reject `seconds` over `settings.MAX_CLIP_SECONDS`. Reuse `look.working_facts(entry, work_dir)` which returns `(path, seconds, fps, size)` or a sentence string. For a photo, validate `entry["photo"]["file"]` with the same plain-name rule (not yet done by any existing code).

**Letter rule:** `LETTER = re.compile(r"[A-Z]{1,3}")` used with `fullmatch` (look line 63).

**Strict JSON reading:** `write_look` uses `allow_nan=False` (look 70-75); the reader must reject NaN/Infinity with `parse_constant` (tests/test_look.py 18-26 `no_constant` shows the idiom) and report duplicate keys with `object_pairs_hook` (RESEARCH Pattern 9).

**Schema validation:** new. Import jsonschema lazily inside the function, as Pillow is (sheets.py `pillow_modules`, lines 26-31):
```python
def pillow_modules():
    from PIL import Image, ImageDraw, ImageFont, features
    return Image, ImageDraw, ImageFont, features

def picture_problem():
    try:
        pillow_modules()
    except ImportError:
        return NO_PICTURE_LIBRARY
    return None
```
Copy as `jsonschema_problem()` returning one sentence when not installed.

**Sentence mapping table:** RESEARCH Pattern 9. Segment numbers are 1-based. Return two lists `(problems, notes)` of plain sentences; `check` prints problems then notes, exit code 1 only for problems.

---

### `v2r/render/match.py` (service, transform + file-I/O)

**Analog:** `v2r/look/__init__.py` `write_look` (70-75), `writable` (78-84); look.json's `overall` block (docstring lines 18-21; produced by `measure.overall_of`, measure.py line 174).

**Whole-or-nothing JSON write** (copy for rewriting the cut list):
```python
def write_look(work_dir, look):
    work_dir = Path(work_dir)
    temp = work_dir / "look.json.tmp"
    temp.write_text(json.dumps(look, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    os.replace(temp, work_dir / "look.json")
```
Write `cutlist.json.tmp` then `os.replace`. Keep key order (do not sort). Inputs: `overall["brightness"]`, `["blue_shift"]`, `["red_shift"]`, `["saturation"]` per clip letter, any of which may be `null` (look.json: "Any value may be null"): a clip with a null or a `"skipped"` entry gets no record and a note. `statistics.median` for the group. Print one line per clip written (as look: `"{letter} looked at in ..."`), then one closing sentence.

---

### `v2r/render/video.py` (service, file-I/O via FFmpeg)

**Analogs:** `v2r/normalize.py` `video_command` (302-315), `photo_graph`/`photo_command` (444-470), `encoder_options` (290-300); `v2r/join.py` command list (39-49).

**House command header:** `["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", ...]` with `-n` in join (never overwrite) or `-y` for scratch pieces. Use `-n` for the final output (`.part` name is fresh; look at how join uses `-n`).

**Photo segment:** normalize's `photo_command` reads only the upright JPEG copy; copy its input-handling (`-loop`/`-framerate`) and add `-framerate 30` as RESEARCH Pattern 7 requires. Read `normalize.py` lines 444-470 when writing the plan to copy the exact option order.

**No analog for:** `perspective` move chain, `lutyuv` touch-up, `trim`/`atrim` exact-frame cutting, `setparams` pinning. Use RESEARCH.md Pattern 2, 3, 5, 10 and "Video piece for a clip segment" code example verbatim. Anything from the list inside a filter string must be a number formatted by our code (`f"{v:.6f}"`); file names only as `-i` arguments (RESEARCH anti-pattern).

**Memory rule:** one FFmpeg run per segment, never one graph with all segments (RESEARCH Pitfall 2); a test asserts no command has more than one video input.

---

### `v2r/render/sound.py` (service, FFmpeg + measurement)

**Analog (partial):** `v2r/look/measure.py` `measure_loudness` (line 250) and `SOUND_FILTERS = ["ebur128", "ametadata"]` (line 32), `STATS_FILE`/`LOUD_FILE` (lines 27-28: "a fixed plain name inside the temporary folder: no file name of the user's is ever in a filter"). Read `measure_loudness` (250-280) and `parse_metadata` (107-121) when writing the plan to copy the `ebur128=...,ametadata=mode=print:file=...` command and the file parser. Silence threshold: `settings.SILENCE_LUFS = -70`. The audio graph (atrim/anullsrc bed, `aevalsrc` envelope with `amultiply`, `amix normalize=0`, `volume` gain from the measured integrated loudness and true peak) comes from RESEARCH Pattern 6; no repo analog. Timeouts via `normalize.ffmpeg_timeout`, and `measure.run_timeout(allowance, deadline)` (measure.py 46-58) if a deadline is used.

---

### `v2r/render/proof.py` (service, file-I/O)

**Analog:** `v2r/look/sheets.py` (`grab_stills`, `SheetBook`, `cell_size`, `fit_size`, `label`). Reuse, do not redraw.

**Reading frames** (sheets.py 93-158): `grab_stills(path, frame_numbers, size, seconds, folder=None, deadline=None)` is a generator of Pillow RGB images; `frame_numbers` must be sorted (raises `ValueError("frame numbers out of order")`); a repeated number gives the same picture twice and is read once. Size per still: `sheets.fit_size(canvas_w, canvas_h, *sheets.cell_size(shape))` as look_at_clip does (read look 184-260 when writing the plan).

**Placing on sheets** (sheets.py 222-231):
```python
book = sheets.SheetBook(work_dir)          # modify: SheetBook(work_dir, folder="proof", stem="proof")
records = book.add(zip(stills, labels), orientation)   # pairs of (image, label text)
```
`orientation` is the canvas shape name (`SHEET_GRID` and `CELL_ASPECT` have exactly "tall" and "wide"). Labels: `f"{n} in {pick.clock(t)}"` / `f"{n} out {pick.clock(t)}"` (segment number then reel time), as `sheets.label` builds `f"{letter} {pick.clock(t)}"` (sheets.py 16-18).

**Required modification of `SheetBook`** (sheets.py lines 168-169, 189-191, 210-211): constructor takes `folder="sheets", stem="sheet"` and `name()` / `save_current()` / `put_back()` use them. Today:
```python
def __init__(self, work_dir):
    self.folder = Path(work_dir) / "sheets"
...
@staticmethod
def name(number):
    return f"sheets/sheet-{number:02d}.jpg"
...
final = self.folder / f"sheet-{self.current['number']:02d}.jpg"
```
`name` is a staticmethod called as `self.name(...)`; it must become an instance method using `self.folder.name` and `self.stem`. `clear_last_look` and `LAST_LOOK_SHEETS = re.compile(r"^sheet-\d+(\.part)?\.jpg$")` (look 60) must keep matching only look's sheets so a `proof/` folder is untouched and look's does not delete proof sheets (separate folder gives that). Existing tests use defaults only (tests/test_look_sheets.py).

**Cover still:** `grab_stills` for one frame, then `image.save(path.with .part, "JPEG", quality=settings.SHEET_JPEG_QUALITY)`, `os.replace` (the same part-then-rename as `save_current`, sheets.py 214-219). Pillow missing -> use `sheets.picture_problem()` and print the sentence; the video is still made (look's behaviour when Pillow is absent, look 263-290).

---

### `tests/media.py` (test helper, modify)

**Analogs:** `make_clip` (21-54), `make_look_clip` (64-141), `make_manifest` (310-360).

**Imports/constants style:** `TIMEOUT = 60`, `run(command)` wrapping `subprocess.run(..., check=True, timeout=TIMEOUT)`; lavfi sources as module-level format strings (`BARS`, `MARKER`, `FLAT`, `BEEP`). Add helpers in the same style: a frame-index-coded clip (luma = 16 + 2*(frame mod 100)), a thin-line clip for stutter measurement, a flat-colour clip at a known Y/U/V, a centroid/pixel probe via `crop=2:2:x:y`, an MP4 top-level box walker, and `ebur128` reader. Generated clips must have working-copy shape: H.264, 30 fps, stereo AAC 48 kHz (the `make_look_clip` closing options at line 139: `-c:v libx264 -preset ultrafast -crf 12 -pix_fmt yuv420p -c:a aac -ac 2 -ar 48000`).

**Manifest for tests:** `make_manifest(work, shape, entries)` writes the frozen names (`letter`, `number`, `status`, `kind`, `original{path,name,bytes}`, `working{file,size,fps,seconds,bytes,sound_added,colour_converted}`, `convert_seconds`, `notes`). Check the tail of that function (lines 355-380 not shown here) for how a `kind: "photo"` entry gets its `photo` block, and extend it so a photo entry gets `photo: {file, size}` plus a real `C-photo.jpg` file when the test needs one.

---

### `tests/test_cutlist_check.py`, `tests/test_match.py` (tests)

**Analog:** `tests/test_look.py`.

**Header and parametrisation** (lines 1-16, 28-29):
```python
import pytest
from media import make_clip, make_manifest, sha256
from v2r import settings
from v2r.__main__ import main

CLIP_SIZE = {"tall": (360, 640), "wide": (640, 360)}  # the clip sizes swap with the shape

@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_...(shape, tmp_path, capsys):
```
**Work folder idiom** (lines 101-111): `make_work(tmp_path)` and `clip_in(work, "A.mp4", shape, seconds)`, then `make_manifest(work, shape, [...])`, then `main(["check", str(work), ...])` and assertions on `capsys.readouterr().out` and the exit code. Every test covers both shapes (CLAUDE.md "No command, default or test may assume tall").

**JSON read helper** (lines 18-26): `no_constant` + `json.loads(text, parse_constant=no_constant)` for reading the rewritten cutlist.

**Exact-sentence tests:** assert the plain-English sentences from CONTEXT D-04/D-10 (e.g. "the music runs out at 14.0 seconds but the reel is 20.0 seconds long").

---

### `tests/test_render_plan.py` (pure tests)

**Analog:** `test_label_format`, `test_half_count`, `test_frame_number_clamps`, `test_base_times` (test_look.py 68-98): plain asserts on pure functions, no FFmpeg. Cover 2.5 s -> 75 frames, the half-up rule, focus clamping at edges, "focus ignored on an axis that already fills", pan direction, move end windows at exactly 4 percent, crop-share, both canvases.

---

### `tests/test_render_video.py`, `test_render_sound.py`, `test_render_golden.py` (tests)

**Analog:** `tests/test_join.py`.

**probe + peak helpers** (lines 29-60):
```python
def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(out)
```
Module-scoped fixtures build clips once (`@pytest.fixture(scope="module")` with `tmp_path_factory`, lines 52-67), and parametrised `["tall", "wide"]` tests per file (lines 62, 74, 89). The golden tests compare decoded-frame hashes (`ffmpeg -f md5` / `-f framemd5`) between two renders, never file bytes (D-11); extend `probe` with `nb_frames`/`r_frame_rate` and check `moov` before `mdat`. Join's size-fit tests (`test_long_join_fits_under_the_limit_at_a_smaller_frame`, `test_too_long_to_fit_is_refused_without_building`) are the model for the "stepped down" sentence and the "nothing built" assertions (check that the output folder holds no `.part`).

---

### `tests/test_doctor.py`, `tests/test_look_sheets.py` (modify)

**test_doctor:** add a `RENDER_FILTERS = [...]` list beside `LOOK_FILTERS` (line 9) and an assertion like `test_doctor_lists_every_normalize_piece` (lines 12-17) that each name is in `doctor.FILTERS`; existing "MISSING not in out" test (lines 20-27) then covers availability. **test_look_sheets:** add a test that `SheetBook(work, folder="proof", stem="proof")` writes `proof/proof-01.jpg` and `names()` reports `proof/proof-01.jpg`, and that the default still gives `sheets/sheet-01.jpg`.

---

## Shared Patterns

### Whole-or-nothing writes
**Source:** `v2r/look/__init__.py` lines 70-75 (`write_look`), `v2r/normalize.py` lines 343-348 (`write_manifest`) and 328-340 (`run_ffmpeg`), `v2r/look/sheets.py` 214-219.
**Apply to:** the rewritten cut list (match), the final MP4, the cover, every scratch piece.
Pattern: write `NAME.part.ext` (or `.tmp`), then `os.replace`; on any failure `unlink(missing_ok=True)`. Never a half-written file in the work folder.

### Plain-English errors, one sentence, per-module exception
**Source:** `LookError`, `JoinError`, `NormalizeError`; handled in `__main__.py` lines 50-58, 61-65, 68-72 as `print(f"v2r <cmd>: {error}", file=sys.stderr); return 1`.
**Apply to:** `RenderError` (render and check). Fixed sentences as module constants (look 56-60). No tracebacks reach the user.

### Safe text from files
**Source:** `normalize.clean_text(value, limit=None, keep_end=False)` (normalize.py 70-86), `display_name`.
**Apply to:** every cut-list string echoed into a sentence (`file`, `why`, `music`, unknown field names).

### Lazy optional libraries
**Source:** `sheets.pillow_modules()` / `picture_problem()` (sheets 26-40), `normalize.photo_libraries()` (368).
**Apply to:** `jsonschema` (check/render say in one sentence when missing; doctor, normalize, look, join keep working). Add `jsonschema` to `pyproject.toml`, regenerate `requirements.txt` with the README.md command, and add the licence row to `docs/licenses.md` (one row for jsonschema plus a sentence for attrs, referencing, jsonschema-specifications, rpds-py, all MIT). RESEARCH flags the install as `checkpoint:human-verify`.

### Settings, not literals
**Source:** `v2r/settings.py`; `tests/test_look.py` 518-550 enforce unit comments for the look block.
**Apply to:** every number in render/match. Read settings at call time inside functions (tests monkeypatch them).

### Both shapes
**Source:** `@pytest.mark.parametrize("shape", ["tall", "wide"])` throughout `tests/test_look.py` and `tests/test_join.py`; `settings.SHAPES`.
**Apply to:** every new test and CLI path; the canvas comes from the list and must equal the manifest's shape.

### FFmpeg command header and timeouts
**Source:** join.py 39-49; normalize.py 323-325 (`ffmpeg_timeout`); `measure.run_timeout(allowance, deadline)` (measure.py 46).
**Apply to:** all render commands. Use `capture_output=True, text=True, check=True, timeout=...` via `normalize.run_ffmpeg`; join's bare `subprocess.run(command, check=True)` shows FFmpeg's error on screen, which is what its CLI message "its error is shown above" relies on.

### Do not touch the user's bench
**Source:** CLAUDE.md and 03-CONTEXT quirks: tests build their own clips in `tmp_path`; never run commands against `work/` or `fixtures/`.

## No Analog Found

| File / part | Role | Data Flow | Reason |
|-------------|------|-----------|--------|
| `schema/cutlist.schema.json` | config | transform | No schema in the repo yet; use RESEARCH Pattern 9 (Draft 2020-12, no `oneOf`/`anyOf`, `"type": ["string","null"]`, permissive extra keys, `const: 1` for version) and CONTEXT D-02 to D-09 for fields |
| Plan geometry, move windows, gain curve (`plan.py` core) | utility | transform | No geometry code exists; RESEARCH Patterns 1, 2, 3, 6 give the formulas |
| `perspective`, `lutyuv`, exact-frame `trim`, `aevalsrc` envelope chains | service | file-I/O | Only `scale`/`crop`/`fps` chains exist (join.py 33-35, normalize `video_chain` 255-278); take RESEARCH Patterns 3, 5, 6, 7, 8, 10 verbatim |
| Concat-demuxer join of pieces | service | file-I/O | join uses the concat filter; the demuxer list file is new (RESEARCH Pattern 4) |

## Metadata

**Analog search scope:** `v2r/` (settings, join, normalize, doctor, __main__, look/*), `tests/` (media, test_join, test_look, test_doctor), `.gitignore`.
**Files scanned:** 12 read in full or in targeted ranges; 04-CONTEXT.md in full; 04-RESEARCH.md lines 1-430 of 619 (Patterns 1-11, code examples start; the remaining 190 lines, which cover the code-example tail, the Validation Architecture and open questions, were not read here, so the planner should read them from line 431 for the test matrix and the open questions on match's group membership).
**Pattern extraction date:** 2026-10-19
