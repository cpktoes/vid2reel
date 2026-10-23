# Phase 5: Stage 17 - Editor's handbook - Pattern Map

**Mapped:** 2026-10-24
**Files analyzed:** 5
**Analogs found:** 5 / 5

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `v2r/__main__.py` (modify: `--work` on `normalize`, `look`) | config/route (CLI wiring) | request-response | same file, `check`/`render`/`match` parsers (lines 44-66) | exact |
| `tests/test_editor_words.py` (new: word-count guard for EDITOR.md) | test | transform (read file, count) | `tests/test_render_settings.py` (reads a repo file, asserts on it) | role-match |
| `tests/test_editor_commands.py` (new: every command EDITOR.md names exists in CLI) | test | request-response | `tests/test_smoke.py` and `tests/test_cutlist_check.py` (`main([...])` calls) | role-match |
| `tests/test_normalize.py`, `tests/test_look.py` (modify: add `--work` CLI cases) | test | request-response | `tests/test_cutlist_check.py` lines 87, 196, 267 | exact |
| `settings.py` (maybe: `EDITOR_MAX_WORDS = 1200`) | config | n/a | render block in `v2r/settings.py`, guarded by `tests/test_render_settings.py` | role-match |

EDITOR.md itself is prose; no analog needed.

## Pattern Assignments

### `v2r/__main__.py` (CLI wiring, request-response)

**Analog:** the `check`/`render` loop and `match` parser in the same file.

Current `--work` option to copy (lines 53-56):
```python
        cut_parser.add_argument(
            "--work", type=Path, default=None,
            help="the work folder that holds manifest.json; leave out for work/ in this repo",
        )
```

Current `normalize` parser (lines 26-37) has only `--shape` and `files`, and calls `normalize.normalize(args.files, args.shape)` at line ~87. The function already accepts it: `def normalize(files, shape, out_dir=None)` (`v2r/normalize.py:657`). So the change is: add `--work` to the parser and pass `args.work` as `out_dir`.
```python
manifest = normalize.normalize(args.files, args.shape, args.work)
```

`look` currently takes `work` as an optional POSITIONAL (lines 40-43) and calls `look.look(args.work)`; `look(work_dir=None)` at `v2r/look/__init__.py:263`. To get `--work FOLDER`, replace the positional with the `--work` option above. Keep the call unchanged. Decision for the planner: either drop the positional or keep both, but existing tests in `tests/test_look*.py` may call `main(["look", str(work)])`. Grep them first and update or keep the positional working.

Gotchas:
- `normalize` takes `files` with `nargs="+"`, so `--work` must go before the files or the user uses `--`. The comment at the top of `main` documents the `--` habit.
- Parsers use `allow_abbrev=False`; keep it.
- Error handling stays as is: `NormalizeError` / `LookError` print `v2r <cmd>: ...` and return 1.

### CLI tests for `--work` (modify `tests/test_normalize.py`, `tests/test_look.py`)

**Analog:** `tests/test_cutlist_check.py`
```python
code = main(["check", str(path), "--work", str(work)])      # line 87
assert main(["render", "--work", str(work)]) == 1           # line 196
assert main(["check", "--work", str(work)]) == 1            # line 267
```
Use `tmp_path` as the work folder, `from v2r.__main__ import main`, and assert the files land in that folder (manifest.json for normalize, look.json for look), cover both `--shape tall` and `--shape wide` (project rule: never assume tall). Use helpers from `tests/media.py` for tiny clips.

### `tests/test_editor_words.py` (test, transform)

**Analog:** `tests/test_render_settings.py` (lines 1-6, 13-17): reads a repo file by path with pathlib and asserts on its text.
```python
import pathlib
import re

from v2r import settings

def render_block_lines():
    lines = pathlib.Path(settings.__file__).read_text(encoding="utf-8").splitlines()
    ...
```
Pattern to copy: resolve the file from the test location (`pathlib.Path(__file__).resolve().parent.parent / "EDITOR.md"`), `read_text(encoding="utf-8")`, count with `len(text.split())` (or a regex of words; state which in a comment), and assert under 1,200. The limit belongs in `v2r/settings.py` (project rule: every number lives there); the settings test uses `hasattr(settings, name)` so import the constant the same way. Add the constant with a unit comment in the style of the render block (each assignment has a `#` comment on the line or line above, enforced by `test_render_settings_have_unit_comments`; note that test only scans between `# render:` and `# Phone limits`, so place it elsewhere or outside that block and do not break the `len(RENDER_SETTINGS) == 34` check).

### `tests/test_editor_commands.py` (test, request-response)

**Analog:** `tests/test_smoke.py` (`assert main([]) == 0`) for calling the CLI, plus argparse's subparser table.

Approach: pull every `v2r <command>` / `python -m v2r <command>` the handbook names with a regex, then assert each is a real subcommand. Get the real set without running anything by building the parser: `main` constructs the parser inline and does not expose it, so either (a) run `main([cmd, "--help"])` inside `pytest.raises(SystemExit)` and check `code == 0` (argparse exits 0 for a real command's help and 2 for an unknown one), or (b) refactor a small `build_parser()` out of `main` (preferred if the planner accepts a small change to `__main__.py`). Also check each `--flag` the handbook names against that command's `--help` text, including `--work`, `--shape tall|wide`. Known command set today: `doctor, join, normalize, look, check, match, render, build-skill`.

## Shared Patterns

### Test imports and CLI calls
**Source:** `tests/test_cutlist_check.py`, `tests/test_smoke.py`: `from v2r.__main__ import main`; assert on the integer exit code; use `tmp_path` and never touch the repo's `work/`.

### Settings discipline
**Source:** `v2r/settings.py`; any number (the word cap) is a named constant with a unit comment.

### Public repo
No test may read or quote anything under `fixtures/` or `work/`; build any media in `tmp_path` via `tests/media.py`.

## No Analog Found

None. (The only small gap: no existing test reads a Markdown file for its content; `tests/test_render_settings.py` is the nearest, reading `settings.py` source.)

## Metadata

**Analog search scope:** `v2r/__main__.py`, `v2r/normalize.py`, `v2r/look/__init__.py`, `v2r/render/check.py`, `tests/`
**Pattern extraction date:** 2026-10-24
