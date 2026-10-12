# v2r

A command-line video toolbox for turning source video into finished reels.

## Running it

Development uses [uv](https://docs.astral.sh/uv/), which manages both Python and the libraries:

```bash
uv sync               # create .venv with Python 3.13 and all libraries
uv run v2r --version
uv run pytest
```

v2r finally runs inside Claude's cloud workspace (Python 3.13, pip, no uv), so `requirements.txt` holds the same runtime libraries for plain pip:

```bash
python3 -m pip install -r requirements.txt
python3 -m v2r --version
```

After adding or upgrading a library with `uv add`, regenerate `requirements.txt` and commit it alongside `uv.lock`:

```bash
uv export --format requirements-txt --no-dev --no-emit-project --no-hashes -o requirements.txt
```

## Layout

| Path | Contents |
| --- | --- |
| `v2r/` | The package. `look/` and `render/` are sub-packages. |
| `v2r/settings.py` | Every tunable number, in one place. |
| `tests/` | pytest tests. Test media files may be committed here. |
| `schema/` | Schemas. |
| `music/` | Music tracks. Audio files may be committed here. |
| `docs/` | Documentation. |
| `skill/` | Skill definition. |
| `work/` | Scratch output. Never committed. |
| `fixtures/` | Local sample clips and notes. Never committed. |

Video, audio and image files are ignored by git everywhere except `tests/` and `music/`.
