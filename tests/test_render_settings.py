"""The guard for Stage 16's numbers: every one is in v2r/settings.py with its unit, and they agree with each other."""

import pathlib
import re

from v2r import settings

RENDER_SETTINGS = [
    # plan 01's nine
    "RENDER_PRESEEK_FRAMES", "RENDER_TAIL_FRAMES", "RENDER_PIECE_PRESET", "RENDER_PIECE_CRF", "RENDER_X264_PRESET",
    "RENDER_X264_CRF", "MAX_CUTLIST_BYTES", "CUTLIST_ECHO_CHARS", "CUTLIST_MAX_DIGITS", "MAX_CUTLIST_SECONDS",
    # the rest of the render block
    "MOVE_AMOUNT", "MUSIC_DROP_RAMP", "FADE_IN_SECONDS", "FADE_OUT_SECONDS", "LOUDNESS_TARGET", "TRUE_PEAK_CEILING",
    "MIN_REEL_SECONDS", "CROP_NOTE_SHARE", "MAX_SEGMENTS", "TEST_TONE_ID", "TEST_TONE_HZ", "TEST_TONE_SECONDS",
    "COVER_JPEG_QUALITY", "LUMA_RANGE", "CHROMA_RANGE", "CLIP_FRAME_BENEFIT", "FPS_TOLERANCE", "TEST_TONE_SLACK_SECONDS",
    # the match block
    "TOUCH_UP_MAX_BRIGHTNESS", "TOUCH_UP_MAX_COLOUR", "TOUCH_UP_SATURATION_MIN", "TOUCH_UP_SATURATION_MAX",
    "TOUCH_UP_DECIMALS", "SATURATION_DECIMALS",
]


def render_block_lines():
    """The lines of v2r/settings.py from the `# render:` comment up to the `# Phone limits` comment."""
    lines = pathlib.Path(settings.__file__).read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("# render:"))
    end = next(i for i, line in enumerate(lines) if i > start and line.startswith("# Phone limits"))
    return lines[start:end]


def test_render_settings_have_unit_comments():
    assert len(RENDER_SETTINGS) == 34
    for name in RENDER_SETTINGS:
        assert hasattr(settings, name), f"{name} is not in v2r/settings.py"
    block = render_block_lines()
    assert any(line.startswith("# match:") for line in block)
    assignments = [i for i, line in enumerate(block) if re.match(r"[A-Z][A-Z0-9_]* = ", line)]
    assert {block[i].split(" = ")[0] for i in assignments} == set(RENDER_SETTINGS)  # nothing else, nothing missing
    for i in assignments:
        assert "#" in block[i] or block[i - 1].lstrip().startswith("#"), f"no unit comment: {block[i]}"


def test_render_numbers_agree_with_each_other():
    # the first and last frame of every segment fit in the proof sheets, in both sheet grids
    for columns, rows in settings.SHEET_GRID.values():
        assert 2 * settings.MAX_SEGMENTS <= settings.MAX_SHEETS_PER_RUN * columns * rows
    assert settings.AUDIO_RATE % settings.OUTPUT_FPS == 0  # a frame holds a whole number of sound samples
    assert settings.TOUCH_UP_SATURATION_MIN < 1 < settings.TOUCH_UP_SATURATION_MAX
    assert 0 < settings.MOVE_AMOUNT < 0.5
    assert settings.LOUDNESS_TARGET < 0
    assert settings.TRUE_PEAK_CEILING <= 0
