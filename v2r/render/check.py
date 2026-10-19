"""`v2r check`: read a cut list and say, one plain sentence per problem, what is wrong with it.

check changes nothing. `render` runs it first and builds nothing when it reports a problem. The rules here are the
ones the cut list cannot state about itself: whether its canvas suits the work folder, whether its clips are the
work folder's clips, whether each shot lies inside its clip, and whether the whole reel can come back under the limit.
Every sentence that repeats text from the list or the work folder passes it through `normalize.clean_text` first.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

from v2r import WORK_DIR, join, look, normalize, settings
from v2r.render import plan

BAD_PART = "The cut list is missing a part, or has one in the wrong form, so it was not checked."
NOT_TEXT = "The cut list is not plain text (UTF-8), so it was not read."
NO_MANIFEST = "There is no manifest.json in the work folder yet, so normalize has to run before the cut list can be checked."
UNREADABLE_MANIFEST = "The work folder's manifest.json could not be read, so the cut list was not checked."
UNFINISHED = "Normalize has not finished converting the clips yet, so the cut list was not checked."


@dataclass
class Checked:
    """What `check` found: sentences for problems and for notes, and the list and manifest it read (or None)."""

    problems: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    cutlist: dict | None = None
    manifest: dict | None = None


def shown(value):
    """Text from the list or a file, made safe to print."""
    return normalize.clean_text(value)


def is_number(value):
    """True for a real number; a boolean is not one."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def shape_of(canvas):
    """The settings.SHAPES name whose (width, height) equals the canvas's [width, height], or None."""
    return plan.shape_of(canvas)


def read_cutlist(path):
    """(data, problems): the cut list as Python data, or None and the sentence that says why not."""
    path = Path(path)
    if not path.is_file():
        return None, [f"There is no cut list at {shown(path)} yet."]
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None, [NOT_TEXT]
    try:
        return json.loads(text), []
    except json.JSONDecodeError as error:
        return None, [f"The cut list is not valid JSON (line {error.lineno}, column {error.colno}: {shown(error.msg)})."]


def read_manifest(work_dir):
    """(manifest, problems): the work folder's manifest.json, or None and the sentence that says why not."""
    try:
        manifest = look.read_manifest(work_dir)
    except look.LookError as error:
        return None, [NO_MANIFEST if str(error) == look.NO_MANIFEST else UNREADABLE_MANIFEST]
    if manifest.get("finished") is not True:
        return None, [UNFINISHED]
    return manifest, []


def structure_problems(data):
    """The one sentence BAD_PART when the list lacks a part this command needs, else nothing.

    A later plan replaces this guard with the schema; until then it keeps the rules below from meeting a list they
    cannot read.
    """
    def fine_segment(segment):
        if not isinstance(segment, dict) or not isinstance(segment.get("clip"), str):
            return False
        if not is_number(segment.get("from")) or not is_number(segment.get("to")):
            return False
        if segment.get("sound") not in ("keep", "off"):
            return False
        for name in ("focus_x", "focus_y"):
            if name in segment and not (is_number(segment[name]) and 0 <= segment[name] <= 1):
                return False
        return True

    def fine_clip(record):
        return isinstance(record, dict) and isinstance(record.get("file"), str) and is_number(record.get("seconds"))

    fine = (
        isinstance(data, dict)
        and isinstance(data.get("canvas"), dict)
        and isinstance(data.get("clips"), dict) and all(fine_clip(record) for record in data["clips"].values())
        and isinstance(data.get("segments"), list) and data["segments"]
        and all(fine_segment(segment) for segment in data["segments"])
    )
    return [] if fine else [BAD_PART]


def canvas_problems(data, manifest):
    """The canvas must be one of the two shapes at the working frame rate, and the shape the clips were made for (D-03)."""
    canvas = data["canvas"]
    width, height, fps = canvas.get("width"), canvas.get("height"), canvas.get("fps")
    shape = plan.shape_of([width, height]) if is_number(width) and is_number(height) else None
    if shape is None or fps != settings.OUTPUT_FPS:
        tall, wide = settings.SHAPES["tall"], settings.SHAPES["wide"]
        return [
            f"The canvas is {shown(width)}x{shown(height)} at {shown(fps)} frames a second; it must be "
            f"{tall[0]}x{tall[1]} (tall) or {wide[0]}x{wide[1]} (wide) at {settings.OUTPUT_FPS}."
        ]
    if shape != manifest["shape"]:
        return [
            f"The canvas is {shape} but the clips were normalized for a {manifest['shape']} reel; "
            f"normalize them again with --shape {shape} to render this list {shape}."
        ]
    return []


def manifest_entry(manifest, letter):
    """The manifest's record of a clip that is done and has a working copy, or None."""
    if not isinstance(letter, str):
        return None
    for entry in manifest["clips"]:
        if entry["letter"] == letter and entry.get("status") == "done" and isinstance(entry.get("working"), dict):
            return entry
    return None


def working_seconds(entry):
    """The length in seconds the manifest gives a working copy, or None when it is not a usable number."""
    seconds = entry["working"].get("seconds")
    return float(seconds) if is_number(seconds) and seconds > 0 else None


def segment_problems(data, manifest, work_dir):
    """Each shot, in the list's order, must be a real stretch of a clip the list names (D-05, D-13)."""
    problems = []
    fps = settings.OUTPUT_FPS
    for n, segment in enumerate(data["segments"], start=1):
        letter, start_s, end_s = segment["clip"], segment["from"], segment["to"]
        if letter not in data["clips"]:
            problems.append(f"Segment {n} uses clip {shown(letter)}, which is not in the list's clips.")
            continue
        if start_s >= end_s:
            problems.append(f"Segment {n} starts at {start_s:g} seconds and ends at {end_s:g}; it must end after it starts.")
            continue
        start, count = plan.segment_frames(segment)
        if count < 1:
            problems.append(f"Segment {n} lasts less than one frame (1/{fps} of a second).")
            continue
        entry = manifest_entry(manifest, letter)
        clip_s = working_seconds(entry) if entry else None
        if clip_s is None:  # a letter the work folder lacks is the clips block's to report, not this rule's
            continue
        whole = plan.clip_frames(clip_s)
        if start >= whole:
            problems.append(f"Segment {n} starts at {start_s:.1f} seconds but clip {shown(letter)} is only {clip_s:.1f} seconds long.")
        elif plan.frames(end_s) > whole:
            if entry["kind"] == "photo":
                problems.append(
                    f"Segment {n} ends at {end_s:.1f} seconds but {shown(letter)} is a photo, "
                    f"and a photo's still lasts {settings.PHOTO_SECONDS} seconds.")
            else:
                problems.append(f"Segment {n} ends at {end_s:.1f} seconds but clip {shown(letter)} is only {clip_s:.1f} seconds long.")
        elif start + count > whole:
            problems.append(
                f"Segment {n} ends at {(start + count) / fps:.2f} seconds once rounded to whole frames, "
                f"but clip {shown(letter)} is only {clip_s:.2f} seconds long.")
    return problems


def fit_problems(data):
    """The whole reel must be short enough to come back under the limit: join's own rule, one rule for both (CUT-07)."""
    canvas = data["canvas"]
    shape = plan.shape_of([canvas["width"], canvas["height"]])
    total = sum(plan.segment_frames(segment)[1] for segment in data["segments"])
    try:
        join.fit(shape, total / settings.OUTPUT_FPS)
    except join.JoinError as error:
        return [str(error)]
    return []


def check(cutlist_path=None, work_dir=None):
    """Check a cut list against the work folder; returns Checked. Writes nothing."""
    work_dir = Path(WORK_DIR if work_dir is None else work_dir)
    path = Path(work_dir / "cutlist.json" if cutlist_path is None else cutlist_path)
    data, problems = read_cutlist(path)
    manifest, more = read_manifest(work_dir)
    checked = Checked(problems=problems + more, cutlist=data, manifest=manifest)
    if checked.problems:
        return checked
    checked.problems = structure_problems(data)
    if checked.problems:
        return checked
    checked.problems = canvas_problems(data, manifest) + segment_problems(data, manifest, work_dir)
    if not checked.problems:
        checked.problems = fit_problems(data)
    return checked


def report(checked):
    """The lines `check` prints: each problem, each note, then one closing line."""
    lines = [f"Problem: {problem}" for problem in checked.problems]
    lines += [f"Note: {note}" for note in checked.notes]
    if checked.problems:
        count = len(checked.problems)
        if count == 1:
            lines.append("The cut list has 1 problem, so nothing can be built until it is fixed.")
        else:
            lines.append(f"The cut list has {count} problems, so nothing can be built until they are fixed.")
    else:
        canvas = checked.cutlist["canvas"]
        total = sum(plan.segment_frames(segment)[1] for segment in checked.cutlist["segments"])
        lines.append(
            f"The cut list is ready to render: {len(checked.cutlist['segments'])} segments, "
            f"{total / settings.OUTPUT_FPS:.1f} seconds, {plan.shape_of([canvas['width'], canvas['height']])} "
            f"{canvas['width']}x{canvas['height']}.")
    return lines
