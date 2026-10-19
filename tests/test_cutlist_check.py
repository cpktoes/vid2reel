"""The cut list's rulebook (schema/cutlist.schema.json) and `check`'s sentences about it, in both shapes."""

import json
from pathlib import Path

import pytest
from cutlists import EXAMPLES, clips_block, placeholder_work, segment, write_list
from jsonschema import Draft202012Validator

from v2r import settings

SHAPES = ["tall", "wide"]
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema" / "cutlist.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def errors_of(data):
    return list(Draft202012Validator(SCHEMA).iter_errors(data))


# ---- the rulebook file ----


def test_schema_is_a_valid_draft_2020_12_schema():
    Draft202012Validator.check_schema(SCHEMA)
    assert SCHEMA["$schema"] == "https://json-schema.org/draft/2020-12/schema"


@pytest.mark.parametrize("shape", SHAPES)
def test_both_examples_pass_the_schema(shape, tmp_path):
    _, manifest = placeholder_work(tmp_path, shape)
    assert errors_of(EXAMPLES[shape](clips_block(manifest))) == []


@pytest.mark.parametrize("shape", SHAPES)
def test_one_segment_list_passes_the_schema(shape, tmp_path):
    _, manifest = placeholder_work(tmp_path, shape)
    width, height = settings.SHAPES[shape]
    data = {
        "version": 1,
        "canvas": {"width": width, "height": height, "fps": settings.OUTPUT_FPS},
        "clips": clips_block(manifest),
        "segments": [segment("A", 0.0, 3.0, "keep", "A 00.0 to A 03.0: the start")],
    }
    assert errors_of(data) == []


def test_schema_holds_no_settings_numbers():
    text = SCHEMA_PATH.read_text(encoding="utf-8")
    for number in ("1080", "1920", "0.92", "1.08", "-14", "0.04"):
        assert number not in text


@pytest.mark.parametrize("shape", SHAPES)
def test_schema_leaves_unknown_fields_open(shape, tmp_path):
    _, manifest = placeholder_work(tmp_path, shape)
    data = EXAMPLES[shape](clips_block(manifest))
    data["colour"] = "warm"
    data["segments"][0]["zoom"] = 2
    assert errors_of(data) == []
