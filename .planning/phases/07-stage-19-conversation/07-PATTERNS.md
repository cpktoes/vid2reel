# Phase 7: Stage 19 - Conversation - Pattern Map

**Mapped:** 2026-11-03
**Files analyzed:** 14 (2 new code/test files, 12 modified)
**Analogs found:** 12 / 14 (the two with no code analog are the handbook draft and the record edits, which are prose)

All paths are repo-relative. Line numbers are of the files as read on branch `stage-19-conversation`. The design detail (trimming arithmetic, cover rules, test tables, pitfalls) is in `07-RESEARCH.md` sections 1 to 4; this file only says what to copy from where.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `v2r/render/revise.py` (new) | service (list transform) | file-I/O, transform | `v2r/render/match.py` | role-match (reads a list, writes a list; differs: writes a NEW numbered file) |
| `v2r/__main__.py` | config (command line) | request-response | the check/render loop (lines 57-69) and `match_parser` (70-79) in the same file | exact |
| `v2r/render/check.py` | service (validator) | transform | `rule_notes` / `crop_notes` in the same file (lines 715-732) | exact |
| `v2r/settings.py` | config | none | the `# doctor` and `# render:` blocks | exact (with one trap, see Shared Patterns) |
| `schema/cutlist.schema.json` | config (rulebook) | none | the `move` enum property (lines 102-105) | exact |
| `v2r/render/__init__.py` | config (imports) | none | line 28 import list | exact |
| `tests/test_revise.py` (new) | test | file-I/O | `tests/test_match.py` | exact |
| `tests/cutlists.py` | test fixture | none | its own `tall_example` / `wide_example` | exact |
| `tests/test_cutlist_check.py` | test | request-response | its own `RULE_NOTE`, `context()`, `RULES` table | exact |
| `tests/test_editor_handbook.py` | test (guard) | transform | its own `handbook_problems`, `is_v2r_command` | exact |
| `README.md` | docs | none | command table row for `match` (line 39) and the `--work` paragraph (line 43) | exact |
| `EDITOR.md` | docs (user's own words) | none | the draft-and-approve routine of Stage 17 | no code analog; the user writes it |
| `.planning/REQUIREMENTS.md` | docs | none | CONV-01/04/05/07 lines 71, 74, 75, 77 | in place edit |
| `docs/decisions.md` (+ `CLAUDE.md` "Settled so far" clause) | docs | none | the dated Stage 17 and 18 lines at the file's end (`- 2026-11-03 · Stage 18 · ...`) | exact |

## Pattern Assignments

### `v2r/render/revise.py` (service, file-I/O transform)

**Analog:** `v2r/render/match.py` (module shape) with `v2r/render/check.py` (reading, reporting) and `v2r/render/plan.py` (frame rounding).

**Module docstring, imports, one-sentence constants, own exception** (`match.py` lines 1-35):
```python
import json
import math
import os
import statistics
from pathlib import Path

from v2r import WORK_DIR, settings
from v2r.render import check

NO_LOOK = "There is no look.json in the work folder yet, so look has to run before match."
BAD_FORM = "The cut list's clips or segments are not in the form match needs, so match changed nothing; run check to see why."
NO_WRITE = "The cut list could not be written, so match changed nothing."

class MatchError(Exception):
    """match can't go on; the message is one plain sentence and the list is untouched."""
```
Copy: a `ReviseError(Exception)` whose message is one plain sentence ending in a next step; refusal sentences as module constants; add `from v2r.render import check, plan`. Import `copy` and `re` as well.

**Top-level function shape: resolve paths, read strictly, refuse with problems[0]** (`match.py` lines 201-220):
```python
work_dir = Path(WORK_DIR if work_dir is None else work_dir)
path = Path(work_dir / "cutlist.json" if cutlist_path is None else cutlist_path)
data, problems = check.read_cutlist(path)
if problems:
    raise MatchError(problems[0])
manifest, problems = check.read_manifest(work_dir)
if problems:
    raise MatchError(problems[0])
```
Copy for `revise()`; difference: only `longer` reads the manifest (so the other five changes work when the work folder is gone). After `read_cutlist`, run the schema pass only (`check.load_schema()`, `check.schema_problems(data, schema)`, `check.time_problems(data)`); do NOT run all of `check.check` on the input (it refuses a tall list over wide work folders, the "wide version" start state).

**Return value for the command line: `(thing, lines_to_print)`** (`match.py` line 232): `return records, lines`. Copy: return the new path and the lines (each changed field in plain words, then `check.report(...)`, then the next-command lines naming the new file).

**Write format** (`match.py` lines 189-198). Copy the `json.dumps` arguments exactly so before/after diffs show only changed lines, but NOT the temp-and-replace write, because revise must never overwrite:
```python
text = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
```
Use `open(next_path, "x", encoding="utf-8")` for exclusive creation; map `OSError`/`ValueError` to a `NO_WRITE`-style sentence (`"... so revise changed nothing."`).

**Frame rounding (do not re-derive)** (`v2r/render/plan.py` 14-35): use `plan.frames`, `plan.clip_frames`, `plan.segment_frames`. A shot of exactly n frames is `to = round(from + n / settings.OUTPUT_FPS, 3)`, leaving `from` alone (RESEARCH "Writing a shot of exactly n frames").

**Numbering habit** (`v2r/render/__init__.py` lines 70-78, `new_path`): lowest free number starting at 2 in a `while path.exists()` loop. revise's variant (RESEARCH "Numbering the next list") uses one more than the highest existing `STEM-N.json` and strips a trailing `-N` from the input stem.

**Printing list text:** pass anything taken from the list through `check.shown(...)`; prefer shot numbers and seconds over `why` text.

**Deep copy, change one thing:** `new = copy.deepcopy(data)`; change fields in place on the copy so key order and unknown fields survive.

---

### `v2r/__main__.py` (command line, request-response)

**Analog:** the shared cut-command loop and `match_parser`.

**Parser pattern** (lines 57-79):
```python
for name, text in (("check", "..."), ("render", "...")):
    cut_parser = commands.add_parser(name, help=text, allow_abbrev=False)
    cut_parser.add_argument("cutlist", nargs="?", type=Path, default=None, help="the cut list; leave out for cutlist.json in the work folder")
    cut_parser.add_argument("--work", type=Path, default=None, help="the work folder that holds manifest.json; leave out for work/ in this repo")
```
Deviation (RESEARCH 1.5, tested): an optional positional `cutlist` in front of a change word breaks (`revise drop C` -> "invalid choice"). So use a `parents=[common]` parser holding `--work` and `--cutlist`, and `revise = commands.add_parser("revise", allow_abbrev=False)` with `change = revise.add_subparsers(dest="change", required=True)` and one `change.add_parser("shorter", parents=[common], allow_abbrev=False)` per change. `--from` needs `dest="shots"`. Every parser keeps `allow_abbrev=False`.

**Dispatch pattern** (lines 141-148, `match` branch of `run()`):
```python
elif args.command == "match":
    try:
        _, lines = render.match.match(args.cutlist, args.work)
    except render.match.MatchError as error:
        print(f"v2r match: {error}", file=sys.stderr)
        return 1
    for line in lines:
        print(line)
```
Copy for `revise` (`v2r revise: {error}` to stderr, return 1). Per RESEARCH 1.6: print the new path first, then the changed-field lines, then the check report; return 1 when the file was written but check reports a problem.

The last-resort `except Exception` in `main()` (lines 82-87) already covers the unforeseen; add nothing there.

---

### `v2r/render/check.py` (recipe notes and field check)

**Analog:** `rule_notes` (lines 715-732, quoted):
```python
notes = []
if not (data.get("look") or {}).get("touch_up"):
    notes.append("There is no touch-up in the list; run match if the clips should match.")
for number, segment in enumerate(data["segments"], start=1):
    entry = manifest_entry(manifest, segment["clip"])
    if entry is not None and entry["kind"] == "photo" and segment.get("move", "none") == "none":
        notes.append(f"Segment {number}: {shown(segment['clip'])} is a photo with no move.")
notes += crop_notes(data, manifest)
if sound.sound_settings(data)["music"] is None and all(segment["sound"] == "off" for segment in data["segments"]):
    notes.append("This reel has no sound at all.")
return notes
```
Copy: add the recipe notes (assumed-Lively when `recipe` is absent; shots outside the range) at the top of `rule_notes` and update its docstring's stated order. Compare in frames (`plan.segment_frames(segment)[1]` against `plan.frames(low)` / `plan.frames(high)`), photos (manifest `kind == "photo"`) exempt from the ceiling only. A wrong `recipe` value needs no new code: `sentence_enum` already reports an enum fault once the schema has it. Notes never refuse; they print through `report()` (lines 778-798) as `Note: ...`.

---

### `v2r/settings.py` (config)

**Analog:** the block style `# render: Stage 16's numbers...` then one `NAME = value  # unit and meaning` per line (lines 119-124).

Add a separate block between `# doctor` and `# render:` (RESEARCH section 3): `RECIPES = {"lively": (1.5, 3.0), "calm": (3.0, 5.0)}` and `DEFAULT_RECIPE = "lively"`, each with a unit comment. Trap: `tests/test_render_settings.py` demands the assignments between the `# render:` line and `# Phone limits` be exactly its 34 names; a new block inside it fails that test.

---

### `schema/cutlist.schema.json` (rulebook)

**Analog:** the `move` property (lines 102-105):
```json
"move": {
  "description": "A gentle movement over the shot. None when left out.",
  "enum": ["none", "push-in", "pull-out", "pan-left", "pan-right"]
},
```
Copy as an optional top-level property `recipe` with `"enum": ["lively", "calm"]`; do not add it to `required`; `version` stays `const 1`. No numbers in the schema (a test at `tests/test_cutlist_check.py` lines 56-59 forbids the settings numbers).

---

### `tests/test_revise.py` (new; test, file-I/O)

**Analog:** `tests/test_match.py`.

**Imports and shape loop** (lines 1-16):
```python
import copy
import json

import pytest
from cutlists import EXAMPLES, clips_block, placeholder_work, segment, write_list

from v2r import settings
from v2r.__main__ import main
from v2r.render import match

SHAPES = ["tall", "wide"]
```
Copy, swapping `match` for `revise`; add `from v2r.render import check, plan`.

**Setup helper** (lines 58-63): `work, manifest = placeholder_work(tmp_path, shape)`; `path = write_list(work, data)`; return them. No FFmpeg, no video. Build from `EXAMPLES[shape](clips_block(manifest))` and add fields revise has never heard of (`colour`, `zoom`, `transition`), an off-grid `from` (1.017), a one-frame shot and a shot at its floor.

**Arithmetic tested as pure functions** (lines 70-90 style, `match.touch_up_records(found, ...)` called with plain numbers): keep revise's trimming in a function over frame counts so the property loops (every target from the sum of floors to the current total; off-grid `from` values 0.000 to 1.000) cost microseconds.

**Whole-list proof:** a `changed_paths(before, after)` helper written in the test file, asserting the exact set of changed paths per change (table in RESEARCH section 4), the input file's bytes unchanged, `cutlist-2.json` then `-3`, and a refusal writing no file with one `v2r revise: ...` sentence on stderr (use `main([...])` with `capsys`). Parametrize every test over `SHAPES`.

---

### `tests/cutlists.py` (fixture)

**Analog:** itself; `tall_example(clips)` (line 79) and `wide_example(clips)` (line 109) are the approved lists; `write_list(work, data, name="cutlist.json")` (line 148) already takes a name, so it can write `cutlist-2.json`.

Add `"recipe": "lively"` to both examples (so the examples emit no "assumed" note). Note the wide example's 10-12 second shots will trip the new range note; adjust expected notes, not the example.

---

### `tests/test_cutlist_check.py` (test)

**Analog:** itself.
- `RULE_NOTE` regex (lines 74-76): extend it with the new note sentences, so tests that filter rule notes from field notes still work.
- `context(shape, tmp_path, patch)` (lines 774-780) and the `RULES` table of `(id, edit, sentence)` rows run by `test_every_rule_gives_its_own_sentence`: add rows for a wrong `recipe` value (`The list's recipe is "fast"; it must be one of lively or calm.`).
- Schema section: add a test that the schema's `recipe` enum equals `set(settings.RECIPES)`, a test that an example with `recipe` passes, and a test that a list without it gets the assumed note.
- Exact-note expectations that must change (RESEARCH section 4): lines ~254-257, 959-970 (`EXAMPLE_NOTES`), 1021, 1036, 1045-1051, 1063, 1076, and `test_notes_never_refuse` (~1091-1108).

---

### `tests/test_editor_handbook.py` (guard)

**Analog:** itself.
- `NAMED` regex `python3 -m v2r ([a-z][a-z-]*)` and `is_v2r_command(name)` (calls `main([name, "--help"])`, wants exit 0) already admit `revise` once the command exists; do not add `revise` to `STEPS` (it is a side road like `join`).
- `MAX_WORDS = 1500` (line 10) changes only to 1800 if the tightened handbook will not fit, with a decisions line.
- Add separate tests (not inside `handbook_problems`, because many tests feed it tiny texts): recipe sentence numbers match `settings.RECIPES` (a small reader that accepts digits or words such as "one and a half"); `revise` is named in EDITOR.md; the reader complains on a wrong number.
- The `--work` and `--no-size-limit` absence checks (lines 65-70) stay as they are.

---

### `README.md`

**Analog:** the table row (line 39) `| \`match [CUTLIST]\` | Writes a mild, capped touch-up ... |` and the paragraph at line 43 ("`normalize`, `look`, `check`, `match` and `render` all take `--work FOLDER`..."). Add a `revise` row describing the six changes and the new numbered file, and add `revise` to the `--work` sentence.

---

### `EDITOR.md`, `.planning/REQUIREMENTS.md`, `docs/decisions.md`, `CLAUDE.md`

No code analog.
- `EDITOR.md`: only the user's approved words; a draft goes to this phase folder first (as Stage 17). The existing "Two recipes" sentence (line 25) is what the recipe guard reads.
- `.planning/REQUIREMENTS.md`: reword CONV-01, 04, 05, 07 (lines 71, 74, 75, 77) to match Stage 18.
- `docs/decisions.md`: append `- 2026-11-0N · Stage 19 · <what was decided and how it differs from the guide>` in the file's existing line format, naming no person or account; one line each for "Decide: when to ask" closed (straight away), the `recipe` field, and (if used) the cap raise.

## Shared Patterns

### One plain sentence per refusal, shown text cleaned
**Source:** `v2r/render/match.py` lines 22-29 (constants) and `v2r/render/check.py` (`shown`, `place`).
**Apply to:** `revise.py` and the new check sentences. Every refusal is one sentence ending in what to do next; list text goes through `check.shown`.

### Read strictly, never parse JSON afresh
**Source:** `check.read_cutlist` (`check.py` lines 90-114), `check.read_manifest` (117-125), `check.manifest_entry` (396-403).
**Apply to:** `revise.py`.

### Reports through check's one voice
**Source:** `check.report(checked)` (`check.py` lines 781-798).
**Apply to:** `revise.py` closing lines.

### Whole frames
**Source:** `v2r/render/plan.py` `frames`, `clip_frames`, `segment_frames` (lines 14-35).
**Apply to:** `revise.py` and the recipe notes in `check.py`. Never `round()` on seconds.

### Every output a new file, input untouched
**Source:** `render.new_path` (`v2r/render/__init__.py` 70-78) for the numbering habit.
**Apply to:** `revise.py`. (`match.write_whole` rewrites in place by design; do not copy that part.)

### Test style
**Source:** `tests/test_match.py`, `tests/cutlists.py`.
**Apply to:** `tests/test_revise.py`. Placeholder work folder, no FFmpeg, both shapes, `main([...])` with `capsys`.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| the trimming arithmetic for `shorter`/`longer` inside `revise.py` | utility | transform | Nothing in the repo shares frames among named shots; use RESEARCH section 2 (steps 1-6 and the worked example of 600 frames to 450) |
| the "Talking with her" section of `EDITOR.md` | docs | none | The user's own words; facts for his draft are in RESEARCH "The follow-up menu" |
| the handbook recipe-number reader (words to numbers) | utility (test) | transform | No existing guard reads numbers out of the handbook; they check counts and names only |

## Metadata

**Analog search scope:** `v2r/render/`, `v2r/__main__.py`, `v2r/settings.py`, `schema/`, `tests/`, `README.md`, `docs/decisions.md`
**Files read for excerpts:** `match.py`, `__main__.py`, parts of `check.py`, `test_match.py`, `test_cutlist_check.py`, `test_editor_handbook.py`, `cutlists.py`, `settings.py`, `render/__init__.py`, the schema, README; the two phase documents (the second only to line 407 of 645 on first read)
**Pattern extraction date:** 2026-11-03
