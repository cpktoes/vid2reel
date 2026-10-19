"""`v2r match`: write a small, capped touch-up for each clip into the cut list, from look's measurements.

match does arithmetic on what look measured and writes the answer into the cut list as numbers. It chooses nothing about
the edit; the handbook says when to run it. Each clip is nudged towards the middle (the median) of the clips the
reel uses, so the clips come to agree with each other. It never pushes a clip towards plain grey: a warm evening stays
warm. Every number is held within the caps in settings.py. Render applies exactly the numbers match writes and nothing
else to colour.

The list is rewritten whole or not at all, and only its `look.touch_up` (and `look.filter`, set to "none" when it was
absent) changes. Every run rewrites every record.
"""

import json
import math
import os
import statistics
from pathlib import Path

from v2r import WORK_DIR, settings
from v2r.render import check

NO_LOOK = "There is no look.json in the work folder yet, so look has to run before match."
UNREADABLE_LOOK = "The work folder's look.json could not be read, so match changed nothing."
LOOK_UNFINISHED = "look has not finished yet, so match changed nothing; run match once look is done."
OTHER_CLIPS = "look.json was made from other clips than the work folder holds now, so run look again before match."
BAD_FORM = "The cut list's clips or segments are not in the form match needs, so match changed nothing; run check to see why."
CLIPS_DIFFER = "The cut list's clips do not match the work folder, so match changed nothing."
NONE_MEASURED = "No clip in the list's segments has brightness and colour in look.json, so match changed nothing."
NO_WRITE = "The cut list could not be written, so match changed nothing."

MEASURES = ("brightness", "blue_shift", "red_shift", "saturation")  # look.json's frozen names, under `overall`


class MatchError(Exception):
    """match can't go on; the message is one plain sentence and the list is untouched."""


def no_constant(name):
    raise ValueError(f"look.json holds {name}, which is not valid JSON")


def measured(overall):
    """The four measurements as numbers, or None when any is missing, not a number, NaN or infinite."""
    if not isinstance(overall, dict):
        return None
    values = {}
    for name in MEASURES:
        value = overall.get(name)
        if not check.is_number(value) or not math.isfinite(value):
            return None
        values[name] = float(value)
    return values


def read_look(work_dir, manifest):
    """{letter: its four measurements, or None}: what look.json says about each clip, read strictly.

    Refused, in one sentence: no look.json, one that cannot be read, one still being made, one of another shape than
    the work folder, and one made from other clips (a letter the manifest lacks, or a working copy of another name).
    A skipped entry, or one that is missing a value, maps to None.
    """
    path = Path(work_dir) / "look.json"
    if not path.is_file():
        raise MatchError(NO_LOOK)
    try:
        data = json.loads(path.read_text(encoding="utf-8"), parse_constant=no_constant)
    except (OSError, ValueError):
        raise MatchError(UNREADABLE_LOOK) from None
    if not isinstance(data, dict) or not isinstance(data.get("clips"), list):
        raise MatchError(UNREADABLE_LOOK)
    if data.get("finished") is not True:
        raise MatchError(LOOK_UNFINISHED)
    if data.get("shape") != manifest.get("shape"):
        raise MatchError(OTHER_CLIPS)
    result = {}
    for entry in data["clips"]:
        if not isinstance(entry, dict):
            raise MatchError(UNREADABLE_LOOK)
        letter = entry.get("letter")
        found = check.manifest_entry(manifest, letter)
        if found is None and entry.get("status") != "skipped":
            raise MatchError(OTHER_CLIPS)
        if entry.get("status") != "done":
            result[letter] = None
            continue
        if entry.get("file") != found["working"].get("file"):
            raise MatchError(OTHER_CLIPS)
        result[letter] = measured(entry.get("overall"))
    return result


def clamp(value, low, high):
    return max(low, min(high, value))


def written(value, decimals):
    """A number rounded to `decimals` places, with -0.0 written as 0.0."""
    return round(value, decimals) + 0.0


def beyond(raw, low, high):
    """True when `raw` lies outside low..high; a value exactly at a cap is within it (float noise is ignored)."""
    raw = round(raw, 6)
    return raw < low or raw > high


def touch_up_records(overall, used, listed):
    """(records, capped, notes) for the clips in `listed`, towards the middle of the used clips that were measured.

    `overall` is {letter: four measurements or None}, `used` the letters of the list's segments in order of first use,
    `listed` the letters of the list's `clips` in their order. Records come in `listed` order; `capped` maps a letter to
    the set of names ("brightness", "blue", "red", "saturation") that hit a cap; `notes` has one sentence for each
    listed clip that was not measured. The target is the group's median, never neutral grey (D-24); the colour offsets
    are worked out after the saturation multiply, using the rounded multiplier the list will carry, so that render's
    arithmetic lands on the group's middle.
    """
    group = [overall[letter] for letter in dict.fromkeys(used) if overall.get(letter) is not None]
    if not group:
        raise MatchError(NONE_MEASURED)
    middle = {name: statistics.median(clip[name] for clip in group) for name in MEASURES}
    decimals, sat_decimals = settings.TOUCH_UP_DECIMALS, settings.SATURATION_DECIMALS
    big, small = settings.TOUCH_UP_MAX_BRIGHTNESS, settings.TOUCH_UP_MAX_COLOUR
    low_sat, high_sat = settings.TOUCH_UP_SATURATION_MIN, settings.TOUCH_UP_SATURATION_MAX
    records, capped, notes = {}, {}, []
    for letter in listed:
        clip = overall.get(letter)
        if clip is None:
            notes.append(f"Clip {letter} has no brightness and colour in look.json, so it gets no touch-up.")
            continue
        hit = set()
        raw = middle["saturation"] / clip["saturation"] if clip["saturation"] else 1.0
        if beyond(raw, low_sat, high_sat):
            hit.add("saturation")
        saturation = written(clamp(raw, low_sat, high_sat), sat_decimals)
        values = {}
        for name, cap, wanted in (
            ("brightness", big, middle["brightness"] - clip["brightness"]),
            ("blue", small, middle["blue_shift"] - saturation * clip["blue_shift"]),
            ("red", small, middle["red_shift"] - saturation * clip["red_shift"]),
        ):
            if beyond(wanted, -cap, cap):
                hit.add(name)
            values[name] = written(clamp(wanted, -cap, cap), decimals)
        records[letter] = {**values, "saturation": saturation}
        capped[letter] = hit
    return records, capped, notes


def describe(letter, record, hit):
    """One printed line for a clip's record, each capped number marked."""
    decimals = settings.TOUCH_UP_DECIMALS

    def mark(name):
        return " (at the cap)" if name in hit else ""

    return (
        f"{letter}: brightness {record['brightness']:+.{decimals}f}{mark('brightness')}, "
        f"blue {record['blue']:+.{decimals}f}{mark('blue')}, "
        f"red {record['red']:+.{decimals}f}{mark('red')}, "
        f"saturation {record['saturation']:.{settings.SATURATION_DECIMALS}f}{mark('saturation')}")


def in_form(data):
    """True when the list has the clips and segments match reads."""
    if not isinstance(data, dict) or not isinstance(data.get("clips"), dict) or not isinstance(data.get("segments"), list):
        return False
    if "look" in data and not isinstance(data["look"], dict):
        return False
    for record in data["clips"].values():
        if not (isinstance(record, dict) and isinstance(record.get("file"), str) and check.is_number(record.get("seconds"))):
            return False
    return all(isinstance(item, dict) and isinstance(item.get("clip"), str) for item in data["segments"])


def write_whole(path, data):
    """Write the list as cutlist.json.tmp beside it and rename it over the list, so a reader never sees half a file."""
    temp = path.with_name(path.name + ".tmp")
    try:
        text = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        temp.write_text(text, encoding="utf-8")
        os.replace(temp, path)
    except (OSError, ValueError) as error:
        temp.unlink(missing_ok=True)
        raise MatchError(NO_WRITE) from error


def match(cutlist_path=None, work_dir=None):
    """Write each clip's touch-up into the cut list; returns (records, the lines to print).

    Raises MatchError, in one sentence, and leaves the list exactly as it was, when the list or look.json cannot be used.
    """
    work_dir = Path(WORK_DIR if work_dir is None else work_dir)
    path = Path(work_dir / "cutlist.json" if cutlist_path is None else cutlist_path)
    data, problems = check.read_cutlist(path)
    if problems:
        raise MatchError(problems[0])
    manifest, problems = check.read_manifest(work_dir)
    if problems:
        raise MatchError(problems[0])
    if not in_form(data):
        raise MatchError(BAD_FORM)
    problems = check.clips_problems(data, manifest, work_dir)
    if problems:
        for problem in problems:
            print(f"Problem: {problem}")
        raise MatchError(CLIPS_DIFFER)
    overall = read_look(work_dir, manifest)
    used = [item["clip"] for item in data["segments"]]
    records, capped, notes = touch_up_records(overall, used, list(data["clips"]))
    block = dict(data.get("look") or {})
    block.setdefault("filter", "none")
    block["touch_up"] = records
    data["look"] = block
    write_whole(path, data)
    lines = [describe(letter, record, capped[letter]) for letter, record in records.items()]
    lines += notes
    lines.append(f"The touch-up for {len(records)} clip(s) is in {path}; render applies exactly these numbers.")
    return records, lines
