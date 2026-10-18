# Phase 3: Stage 15 - Seeing the footage - Pattern Map

**Mapped:** 2026-10-17
**Files analyzed:** 14 new/modified
**Analogs found:** 13 / 14 (the stills-to-sheets Pillow code has only a partial analog)

Line numbers are from the current tree (v2r/normalize.py 714 lines, v2r/doctor.py 128, v2r/__main__.py 69, v2r/settings.py 67, tests/media.py 183). No file in fixtures/ or work/ was read.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `v2r/look/__init__.py` (look entry, per-clip loop, look.json docstring, progress lines) | service | batch, file-I/O | `v2r/normalize.py` `normalize()` + module docstring | exact |
| `v2r/look/measure.py` (FFmpeg commands, parse text files) | service | transform, file-I/O | `v2r/normalize.py` `video_command()`/`run_ffmpeg()`; `v2r/join.py` command list | role-match |
| `v2r/look/summarise.py` (half-second bins, peaks, shake) | utility | transform | `v2r/normalize.py` `frame_facts()` (statistics over a series) | role-match |
| `v2r/look/pick.py` (base rhythm, extras, candidates, reasons) | utility | transform | `v2r/normalize.py` `working_size()` / `frame_facts()` (pure functions) | partial |
| `v2r/look/sheets.py` (select to raw pipe, Pillow sheets) | service | file-I/O, streaming | `tests/media.py` `gray_frame()` (raw pipe) + `normalize.read_photo()` (lazy Pillow) | partial |
| `v2r/__main__.py` (add `look`) | route/CLI | request-response | the `normalize` branch in the same file | exact |
| `v2r/settings.py` (look numbers) | config | n/a | the `# normalize:` block | exact |
| `v2r/doctor.py` (`FILTERS` grows) | config | n/a | existing `FILTERS` list, lines 16-19 | exact |
| `tests/test_look.py` | test | request-response | `tests/test_normalize.py` | exact |
| `tests/media.py` (new patterns, helpers) | test utility | file-I/O | `make_clip()`, `MARKER`, `FLAT`, `BEEP`, `corner_mean_image()` | exact |
| `tests/test_doctor.py` (assert new filters) | test | n/a | existing tests in the same file | exact |
| `docs/licenses.md` (PySceneDetect "checked, not added") | docs | n/a | existing table rows 7-8 | exact |
| `docs/decisions.md`, `README.md`, `EDITOR.md` (proposed text only) | docs | n/a | `EDITOR.md` steps 3-4 | role-match |
| `work/look.json`, `work/sheets/sheet-NN.jpg` (outputs) | output | file-I/O | `work/manifest.json` | exact |

## Pattern Assignments

### `v2r/look/__init__.py` (service, batch + whole-or-nothing file-I/O)

**Analog:** `v2r/normalize.py`

**Docstring pattern** (lines 1-23): the module docstring freezes the JSON names for later stages ("these names are frozen"). Copy the style: top-level keys, then per-entry keys, then nested. look.json needs the same (Stages 16 and 17 read it).

**Imports** (lines 25-37):
```python
import json
import os
import subprocess
import time
from pathlib import Path

from v2r import WORK_DIR, doctor, settings
```

**One-sentence error classes** (lines 47-60):
```python
class NormalizeError(Exception):
    """The whole run can't go on; the message is one plain sentence."""

class Refused(Exception):
    """One file can't be used; `sentence` says so in plain English and the run goes on with the others."""
    def __init__(self, sentence, detail=None):
        super().__init__(sentence)
        self.sentence = sentence
        self.detail = detail
```

**Atomic write, reuse as is** (lines 343-348):
```python
def write_manifest(out_dir, manifest):
    out_dir = Path(out_dir)
    temp = out_dir / "manifest.json.tmp"
    temp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, out_dir / "manifest.json")
```
Write `look.json.tmp` then `os.replace`. Add `allow_nan=False` to `json.dumps` so a stray NaN raises instead of writing invalid JSON.

**Per-item boundary loop, progress line, rewrite after each item** (lines 652-714): write an initial empty file, loop clips in letter order, one broad catch per clip at the boundary, `print(..., flush=True)`, append entry, rewrite whole file, set `finished` at the end. Skipped entries (lines 635-649, `skipped_entry`) are the model for D-06: keep `letter`, `number`, `status`, no stills.
```python
manifest = {"version": 1, "shape": shape, "finished": False, "stopped": None, "clips": []}
write_manifest(out_dir, manifest)
...
    manifest["clips"].append(entry)
    write_manifest(out_dir, manifest)
...
manifest["finished"] = True
write_manifest(out_dir, manifest)
print(f"{done} of {len(inputs)} files converted; ...", flush=True)
```

**Start-of-run feature check** (lines 357-365): `check_ffmpeg()` raises a one-sentence error. For look, D-21 differs: do not raise for a missing measuring filter; compute `have = doctor.ffmpeg_names("-filters")` once (doctor.py:66-69) and leave out the snippet for any filter not in it. Only a missing FFmpeg/ffprobe (`doctor.missing_ffmpeg_features([], [], [])` returns `["FFmpeg"]`) stops the run.

**Clearing last run** (lines 116-122, `clear_last_job`): D-08 says a new run replaces the last sheets and look.json. Copy the shape (delete only known names, never anything else). Note `LAST_JOB_FILES` (line 100) does not match `sheets/` or `look.json`, so look needs its own pattern, e.g. delete `look.json`, `look.json.tmp`, and files matching `sheet-\d+\.jpg` in `work/sheets/`.

**Text from files is data** (lines 70-91): use `clean_text()` / `display_name()` for anything that came from an original name in sentences or JSON (the manifest already holds cleaned names; reuse them).

---

### `v2r/look/measure.py` (service, transform + file-I/O)

**Analog:** `v2r/normalize.py` lines 323-340 and `v2r/join.py` lines 39-54.

**FFmpeg command as a list, house flags** (`join.py` 39-49):
```python
command = [
    "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
    *inputs,
    "-filter_complex", ";".join(graph),
    ...
]
try:
    subprocess.run(command, check=True)
except subprocess.CalledProcessError:
    output.unlink(missing_ok=True)
    raise
```
For look use `-y` (research commands) instead of `-n`, and `cwd=work_dir` with plain file names (`A.stats.txt`, `A.motion.txt`, `A.loud.txt`) so no path enters a filter string. Build the chain from a dict `{filter name: snippet}` filtered by `have`.

**Time allowance in proportion to the clip** (`normalize.py` 323-325, reuse directly):
```python
def ffmpeg_timeout(seconds):
    return settings.FFMPEG_TIMEOUT_FLOOR + settings.FFMPEG_SECONDS_PER_SECOND * seconds
```
Call `normalize.ffmpeg_timeout(working["seconds"])` and catch `subprocess.TimeoutExpired` per measurement (D-21: that measurement becomes null, sheets still come back).

**Error text kept short** (`normalize.py` 351-354): `tail(error.stderr)`; `run_ffmpeg` (328-340) shows the capture_output/text/check/timeout call and `NO_ROOM_TEXT` ENOSPC handling. Look writes only tiny text files and stills in memory, but if it writes sheets, copy the ENOSPC rule (stop the run with one sentence).

**Parsers** to copy verbatim from RESEARCH.md "Code Examples" (`parse_metadata`, `parse_motion`) plus `finite()` (RESEARCH section 5). Every number goes through `finite()`; never write `nan` or `-inf`.

---

### `v2r/look/summarise.py` and `v2r/look/pick.py` (utility, transform)

**Analog:** `v2r/normalize.py` `frame_facts()` (line 158) and `working_size()` (line 125): small pure functions using `statistics`, tested with hand-made numbers and no FFmpeg. Imports `statistics`, `math` only. Take every threshold from `settings`, never hard-code. Use the prototype code in RESEARCH.md section 5 (`residual`, `mad`, `peaks`) as the body; the analog is for style (pure, documented in one docstring line, no I/O).

Rules to carry from RESEARCH: spread floor on the MAD, leave cut frames out of movement/camera/shake means, cap merged candidate stretches (new setting), reasons state facts only (no "best", no "use").

---

### `v2r/look/sheets.py` (service, file-I/O + streaming)

**Analog (raw pipe):** `tests/media.py` `gray_frame()` lines 80-88:
```python
data = subprocess.run(
    ["ffmpeg", "-loglevel", "error", "-nostdin", "-ss", str(at), "-i", str(path), "-frames:v", "1",
     "-f", "rawvideo", "-pix_fmt", "gray", "-"],
    capture_output=True, check=True, timeout=TIMEOUT,
).stdout
```
For look: one `select='eq(n,..)+..'` command with `-fps_mode passthrough -f rawvideo -pix_fmt rgb24 -`, then slice the bytes into `w*h*3` chunks and `Image.frombytes("RGB", (w, h), chunk)`. Check frame count read equals frames asked for.

**Analog (lazy Pillow):** `normalize.photo_libraries()` (line 368-375) and `tests/media.py` `make_photo()` line 143: `from PIL import Image, ImageDraw, ImageFont` inside the function, with the comment "Pillow is imported here only". If import fails, look still writes look.json and says one sentence (video work keeps going if pip failed). Check `PIL.features.check("freetype2")` once.

Sheet drawing body: RESEARCH.md section 3 recipe (labels `f"{letter} {seconds:04.1f}"`, `ImageFont.load_default(size=...)`, dark box in a corner). Open question 1: one orientation per sheet (new sheet when orientation changes).

---

### `v2r/__main__.py` (CLI route)

**Analog:** the `normalize` branch, same file. Parser (lines 26-37) and dispatch (lines 54-60):
```python
normalize_parser = commands.add_parser(
    "normalize", help="convert clips to one working format in work/", allow_abbrev=False)
...
elif args.command == "normalize":
    try:
        manifest = normalize.normalize(args.files, args.shape)
    except normalize.NormalizeError as error:
        print(f"v2r normalize: {error}", file=sys.stderr)
        return 1
    return 0 if any(clip["status"] == "done" for clip in manifest["clips"]) else 1
```
For look: `commands.add_parser("look", help="make contact sheets and measurements of the working copies in work/", allow_abbrev=False)`, no `--shape` (the manifest carries it), an optional positional or `--work` path (`nargs="?"`, `type=Path`) for tests. Add `look` to the import on line 8 (`from v2r import ... look ...`; `v2r/look/__init__.py` must export `look(...)` and `LookError`). Error format `v2r look: {error}` to stderr, return 1.

---

### `v2r/settings.py` (config)

**Analog:** the `# normalize:` block (lines 26-59): one comment line naming the stage, then `NAME = value  # unit and meaning`. Add a `# look:` block after normalize and before `# doctor`. Example style:
```python
PHOTO_SECONDS = 4  # seconds a photo's still clip lasts
FFPROBE_TIMEOUT = 30  # seconds ffprobe may take to read one file's facts before that file is left out
```
Settings to add (from CONTEXT/RESEARCH): analysis width (320 px) and rate (10 fps), summary step (0.5 s), base still rhythm (1 s) and thinning steps (1.5, 2), `MAX_SHEETS_PER_RUN` (20), stills per sheet (12) and grids (tall 4x3, wide 3x4), sheet width (1950 px), padding, JPEG quality (80-85), `SHEET_MAX_BYTES` (1.5 MB), label font share (0.07), extras spacing (0.3 s) and cap (1/3), peak k and spread floor, shake and camera-still limits, loudness delay (0.1 s) and peak LU, scene threshold (10), candidate window (2 s), step, count (5), merged-stretch cap (4 s).

---

### `v2r/doctor.py` (config)

**Analog:** lines 16-19, the `FILTERS` list; append `"select", "signalstats", "blurdetect", "scdet", "deshake", "ebur128", "metadata", "ametadata"`. `run()` (lines 36-38) prints one line per name, so nothing else changes. Keep `normalize.NEEDED_FILTERS` (normalize.py line ~64) unchanged: normalize must not start requiring look's filters. Look's own list (e.g. `NEEDED_FILTERS` in look) stays separate and is soft (D-21).

---

### `tests/test_look.py` (test)

**Analog:** `tests/test_normalize.py`.

**Imports and path monkeypatching** (lines 1-20):
```python
import json
import pytest
from media import make_clip, probe, stream, corner_mean_image
import v2r.look
from v2r import doctor, settings
from v2r.__main__ import main
```
**Parametrise over both shapes; tmp_path work folder; tracer through `main`** (lines 29-66):
```python
@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_tracer_cli_...(shape, tmp_path, monkeypatch, capsys, small_caps):
    monkeypatch.setattr(v2r.normalize, "WORK_DIR", tmp_path / "work")
    ...
    assert main([...]) == 0
    manifest = json.loads((work / "manifest.json").read_text(encoding="utf-8"))
```
**Small-size fixture** (lines 22-27, `small_caps` monkeypatching `settings.WORKING_SIZE`): copy the idea to monkeypatch small sheet width / `MAX_SHEETS_PER_RUN` / stills per sheet for the cap tests.
**Helper that returns the written JSON** (lines 69-72, `convert`): write a `looked(...)` helper the same way.
**Manifest helper:** per RESEARCH, write `manifest.json` straight from generated clips using normalize's frozen names, rather than running normalize in every test (a few tests may run real normalize for one end-to-end check).
**Atomic/valid JSON:** `json.loads(text, parse_constant=raise)` to prove no NaN.
**Missing filter:** `monkeypatch.setattr(doctor, "ffmpeg_names", lambda option: {...})`, as test_doctor.py monkeypatches `FILTERS`.
Pure-function tests for summarise/pick need no FFmpeg.

---

### `tests/media.py` (test utility)

**Analog:** `make_clip()` (lines 21-54) and the pattern strings (lines 8-12):
```python
MARKER = "color=black:size={w}x{h}:rate={fps}:duration={s},drawbox=x=0:y=0:w=120:h=120:color=white:t=fill"
FLAT = "color=c=0x7E7E7E:size={w}x{h}:rate={fps}:duration={s}"
source = {"marker": MARKER, "flat": FLAT}.get(pattern, BARS).format(w=width, h=height, fps=fps, s=seconds)
```
Extend with new `pattern` names (square, cut, jitter, pan, blur, cast) by adding strings or small builder branches; most need `-filter_complex` (overlay) so add a branch like the `hdr`/`vfr` `-vf` blocks (lines 37-41), or a separate `make_look_clip()` to avoid growing `make_clip`'s signature. Recipes: RESEARCH.md section 4 (use `overlay ... eval=frame`, NOT `drawbox` with `t`; square visible 4.2-4.8; cut at 3.4; 2D grid picture for jitter and pan). A single beep: `aevalsrc='0.5*sin(2*PI*1000*t)*between(t,3,3.4)':s=48000:d={s}` beside the existing `BEEP` (line 11).
**Reading a still back:** extend `corner_mean_image()` (lines 173-183, Pillow open, crop, `ImageStat`) to a `region_mean_image(path, box)` that crops a cell recorded in look.json and counts near-white pixels.
`make_clip` rejects nothing about shape: tests pass width/height for tall (360x640) and wide (640x360).

---

### `tests/test_doctor.py`

**Analog:** same file, lines 5-6 and 12-16: add a `LOOK_FILTERS = [...]` list and an assertion loop `for name in LOOK_FILTERS: assert name in doctor.FILTERS`; `test_doctor_reports_decoders` already asserts no "MISSING" on the Mac.

---

### `docs/licenses.md`

**Analog:** the table rows (lines 7-8): `| Name | Version | Licence | What it is used for | URL |`. Add a "checked, not added" note for PySceneDetect (BSD-3-Clause, needs OpenCV ~80 MB or PyAV ~43 MB; `scdet` is FFmpeg's own). Read the file's top and any existing "checked" section before wording it, to match the style.

---

### `EDITOR.md` (proposed text only; the user writes it)

**Analog:** steps 3-4 (lines 3-4 of EDITOR.md): the `nohup sh -c '...; echo "X finished with exit code $?"' sh ... > X.log 2>&1 &` pattern, "read X.log every 30 seconds until it says 'X finished'", file names as data. Propose a "look" step between 3 and 4 in the same wording (command `python3 -m v2r look`, log `look.log`, show the sheets when asked). Do not edit EDITOR.md.

## Shared Patterns

### Whole-or-nothing JSON write
**Source:** `v2r/normalize.py` lines 343-348. **Apply to:** look.json (rewritten after every clip).

### One plain sentence per problem; a clip never stops the run
**Source:** `v2r/normalize.py` lines 47-60 and the per-file `except` ladder at 668-689. **Apply to:** `look/__init__.py`, `measure.py`. A failed measurement becomes null; a failed clip becomes a skipped-style entry with a sentence; only no-FFmpeg or no-room stops the run.

### FFmpeg house flags, timeouts, list commands
**Source:** `v2r/join.py` 39-49; `v2r/normalize.py` 323-340. **Apply to:** all FFmpeg calls in `look/`. Flags `-hide_banner -loglevel error -nostdin`; `timeout=normalize.ffmpeg_timeout(seconds)`; `cwd` = work folder with plain file names.

### Feature check via doctor
**Source:** `v2r/doctor.py` 66-69 (`ffmpeg_names`) and 72-95 (`missing_ffmpeg_features`). **Apply to:** look start-up (D-20/D-21): call `ffmpeg_names("-filters")` once, drop missing measuring snippets.

### Settings only, each with a unit comment
**Source:** `v2r/settings.py`. **Apply to:** every number in look and its sheets.

### Pillow imported lazily
**Source:** `v2r/normalize.py` `photo_libraries()` (368); `tests/media.py` 143. **Apply to:** `look/sheets.py` only.

### Manifest names are frozen; letters never renumbered
**Source:** `v2r/normalize.py` docstring lines 7-23 (`clips[]`: `letter`, `number`, `status`, `kind`, `working.file/size/fps/seconds/sound_added`, `photo.file`). **Apply to:** look's input reading and look.json's per-clip entries (reuse `letter`, `number`, `status`, `kind`).

### Tests: both shapes, tmp_path, FFmpeg-made clips with known answers
**Source:** `tests/test_normalize.py` lines 29-72; `tests/media.py`. **Apply to:** `tests/test_look.py`.

## No Analog Found

| File / part | Role | Data Flow | Reason |
|---|---|---|---|
| Filter-metadata parsing (`parse_metadata`, `parse_motion`) | utility | transform | No code reads FFmpeg `metadata=print` text yet; use RESEARCH.md "Code Examples" |
| Peak finding, moving-average shake, candidate merge and reasons | utility | transform | No statistical series code beyond `frame_facts()`; use RESEARCH.md section 5 prototype |
| Contact-sheet layout and labels | service | file-I/O | Pillow is used only for photos so far; use RESEARCH.md section 3 recipe |

## Metadata

**Analog search scope:** `v2r/`, `tests/`, `docs/licenses.md`, `EDITOR.md`
**Files read:** v2r/normalize.py (targeted ranges), v2r/join.py, v2r/doctor.py, v2r/__main__.py, v2r/settings.py, v2r/__init__.py, tests/media.py, tests/test_normalize.py (head), tests/test_doctor.py, EDITOR.md, docs/licenses.md (grep)
**Not read, by instruction:** fixtures/, work/
**Pattern extraction date:** 2026-10-17
