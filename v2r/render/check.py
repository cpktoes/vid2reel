"""`v2r check`: read a cut list and say, one plain sentence per problem, what is wrong with it.

check changes nothing. `render` runs it first and builds nothing when it reports a problem. The cut list is first read
against its rulebook, schema/cutlist.schema.json, and every way it breaks the rulebook is one plain sentence; fields
that are accepted but not built yet, and fields the rulebook does not name, each get a note. The rules after that are
the ones the cut list cannot state about itself: whether its canvas suits the work folder, whether its clips are the
work folder's clips, whether each shot lies inside its clip, whether the touch-up, music, cover and length keep to
their limits, and whether the whole reel can come back under the limit. Problems come in that order, one sentence each,
and refuse the list; notes (a photo with no move, no touch-up, a crop that keeps little, a silent reel) never refuse.
Every sentence that repeats text from the list or the work folder passes it through `normalize.clean_text` first.
"""

import json
import math
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from v2r import ROOT, WORK_DIR, join, look, normalize, settings
from v2r.render import plan, sound

SCHEMA_PATH = ROOT / "schema" / "cutlist.schema.json"  # the cut list's rulebook; read when check runs, so tests can point elsewhere
NOT_TEXT = "The cut list is not plain text (UTF-8), so it was not read."
NO_MANIFEST = "There is no manifest.json in the work folder yet, so normalize has to run before the cut list can be checked."
UNREADABLE_MANIFEST = "The work folder's manifest.json could not be read, so the cut list was not checked."
UNFINISHED = "Normalize has not finished converting the clips yet, so the cut list was not checked."
NO_JSONSCHEMA = "The jsonschema library is not installed, so the cut list cannot be checked; install the requirements again."
NO_SCHEMA = "The rulebook schema/cutlist.schema.json is missing or unreadable, so the cut list cannot be checked."
NOT_COMPARED = "The list was not compared with the work folder, because of the problems above."


@dataclass
class Checked:
    """What `check` found: sentences for problems and for notes, and the list and manifest it read (or None)."""

    problems: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    cutlist: dict | None = None
    manifest: dict | None = None


def shown(value):
    """Text from the list, made safe to print and cut to settings.CUTLIST_ECHO_CHARS characters (T-4-06)."""
    return normalize.clean_text(value, settings.CUTLIST_ECHO_CHARS)


def is_number(value):
    """True for a real number; a boolean is not one."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def shape_of(canvas):
    """The settings.SHAPES name whose (width, height) equals the canvas's [width, height], or None."""
    return plan.shape_of(canvas)


class Refused(Exception):
    """The reader met something a cut list may not hold; the message is the one sentence that says so."""


def refuse_constant(text):
    raise Refused(f"The cut list holds {shown(text)}, which is not a number a cut list may hold.")


def read_float(text):
    """A decimal number; one that overflows to infinity (such as 1e400) is refused."""
    value = float(text)
    if not math.isfinite(value):
        refuse_constant(text)
    return value


def read_int(text):
    """A whole number of at most settings.CUTLIST_MAX_DIGITS digits, checked before Python turns it into a number."""
    if len(text.lstrip("-")) > settings.CUTLIST_MAX_DIGITS:
        refuse_constant(text)
    return int(text)


def read_block(pairs):
    """One block of the list as a dictionary; a name given twice in it is refused."""
    block = {}
    for key, value in pairs:
        if key in block:
            raise Refused(f'The cut list names "{shown(key)}" twice in one block; each name may appear once.')
        block[key] = value
    return block


def read_cutlist(path):
    """(data, problems): the cut list as Python data, or None and the sentence that says why not.

    The reading is strict (T-4-03): a file that is too large, a list nested too deeply, NaN, infinity, a number that
    overflows, a whole number of too many digits and a name given twice in one block are each refused in one sentence.
    """
    path = Path(path)
    if not path.is_file():
        return None, [f"There is no cut list at {normalize.clean_text(path)} yet."]
    try:
        if path.stat().st_size > settings.MAX_CUTLIST_BYTES:
            return None, [f"The cut list is larger than {settings.MAX_CUTLIST_BYTES / 1e6:g} MB, so it was not read."]
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None, [NOT_TEXT]
    try:
        return json.loads(
            text, parse_constant=refuse_constant, parse_float=read_float, parse_int=read_int,
            object_pairs_hook=read_block), []
    except Refused as refusal:
        return None, [str(refusal)]
    except RecursionError:
        return None, ["The cut list is not valid JSON."]
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


def jsonschema_module():
    """The jsonschema library, imported only here (the way Pillow is) so doctor, normalize, look and join never load it."""
    import jsonschema

    return jsonschema


def jsonschema_problem():
    """The one sentence NO_JSONSCHEMA when the library cannot be imported, else None."""
    try:
        jsonschema_module()
    except ImportError:
        return NO_JSONSCHEMA
    return None


def load_schema():
    """The cut list's rulebook as Python data; raises Refused with the one sentence when it cannot be read."""
    try:
        return json.loads(Path(SCHEMA_PATH).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise Refused(NO_SCHEMA) from error


def value_words(value):
    """A value from the list as a sentence prints it: numbers plainly, text in quotes, a list or block by its kind (T-4-06)."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if is_number(value):
        whole = isinstance(value, float) and value.is_integer()
        return shown(str(int(value)) if whole else repr(value))
    if isinstance(value, str):
        return f'"{shown(value)}"'
    return "a list" if isinstance(value, list) else "a block"


def place(path):
    """Where in the list an error is, in words: "Segment 4's to", "The canvas's width", "Clip B's touch-up red"."""
    if not path:
        return "The cut list"
    head, rest = path[0], path[1:]
    field_name = shown(rest[0]) if rest else None
    if head == "version" and not rest:
        return "The list's version"
    if head == "canvas":
        return f"The canvas's {field_name}" if rest else "The canvas"
    if head == "clips":
        if not rest:
            return "The list's clips"
        return f"Clip {field_name}'s {shown(rest[1])}" if len(rest) > 1 else f"Clip {field_name}'s record"
    if head == "segments":
        if not rest:
            return "The list's segments"
        number = rest[0] + 1 if isinstance(rest[0], int) else field_name
        return f"Segment {number}'s {shown(rest[1])}" if len(rest) > 1 else f"Segment {number}"
    if head == "look":
        if not rest:
            return "The look"
        if field_name == "filter":
            return "The look's filter"
        if field_name == "touch_up":
            if len(rest) == 1:
                return "The touch-up"
            letter = shown(rest[1])
            return f"Clip {letter}'s touch-up {shown(rest[2])}" if len(rest) > 2 else f"Clip {letter}'s touch-up"
    if head == "sound":
        return f"The sound's {field_name}" if rest else "The sound"
    if head == "cover":
        return f"The cover's {field_name}" if rest else "The cover"
    return "The list's " + " ".join(shown(part) for part in path)


TYPE_WORDS = {
    "number": "a number", "integer": "a whole number", "string": "text", "object": "a block of named fields",
    "array": "a list", "null": "null", "boolean": "true or false",
}
LETTER_RULE = "a clip's name must be a capital letter such as A."
BOUND_WORDS = {"minimum": "at least", "maximum": "at most", "exclusiveMinimum": "more than", "exclusiveMaximum": "less than"}


def either(choices):
    """"a", "a or b" or "a, b or c"."""
    choices = [str(choice) for choice in choices]
    return choices[0] if len(choices) == 1 else ", ".join(choices[:-1]) + " or " + choices[-1]


def sentence_required(error, where):
    return [f"{where} has no {shown(name)}." for name in error.validator_value if name not in error.instance]


def sentence_type(error, where):
    expected = error.validator_value
    expected = expected if isinstance(expected, list) else [expected]
    return [f"{where} must be {' or '.join(TYPE_WORDS.get(kind, kind) for kind in expected)}."]


def sentence_const(error, where):
    return [f"{where} is {value_words(error.instance)}; this renderer reads version {error.validator_value}."]


def sentence_enum(error, where):
    path = list(error.absolute_path)
    if path == ["look", "filter"]:
        return [f"{where} is {value_words(error.instance)}; only \"none\" can be built until Stage 21."]
    return [f"{where} is {value_words(error.instance)}; it must be one of {either(error.validator_value)}."]


def sentence_bound(error, where):
    path = list(error.absolute_path)
    value = value_words(error.instance)
    if path and path[-1] in ("focus_x", "focus_y"):
        return [f"{where} is {value}; it must be between 0 and 1."]
    return [f"{where} is {value}; it must be {BOUND_WORDS[error.validator]} {error.validator_value:g}."]


def sentence_min_items(error, where):
    return ["The list has no segments."]


def sentence_min_properties(error, where):
    return ["The list's clips are empty; copy each clip's letter, file and length from the manifest."]


def sentence_min_length(error, where):
    path = list(error.absolute_path)
    if path and path[-1] == "why":
        return [f"{where} is empty; say which still it rests on."]
    return [f"{where} is empty."]


def sentence_pattern(error, where):
    value = value_words(error.instance)
    if "propertyNames" in error.schema_path:  # the instance is a key of the block at the path
        return [f"{where} name {value}; {LETTER_RULE}"]
    return [f"{where} is {value}; {LETTER_RULE}"]


SENTENCES = {  # one function for each schema keyword that can report an error; a test proves no keyword is left out
    "required": sentence_required,
    "type": sentence_type,
    "const": sentence_const,
    "enum": sentence_enum,
    "minimum": sentence_bound,
    "maximum": sentence_bound,
    "exclusiveMinimum": sentence_bound,
    "exclusiveMaximum": sentence_bound,
    "minItems": sentence_min_items,
    "minProperties": sentence_min_properties,
    "minLength": sentence_min_length,
    "pattern": sentence_pattern,
}


def error_order(error):
    """Path order, with a segment's number compared as a number (segment 10 after segment 2), then the keyword."""
    return [(0, part, "") if isinstance(part, int) else (1, 0, str(part)) for part in error.absolute_path], error.validator


def schema_problems(data, schema):
    """One plain sentence for every way the list breaks the rulebook, in a stable order (a missing name gets one each)."""
    validator = jsonschema_module().Draft202012Validator(schema)
    problems = []
    seen = set()
    for error in sorted(validator.iter_errors(data), key=error_order):
        where = place(list(error.absolute_path))
        if error.validator == "required":  # jsonschema reports each missing name as its own error; one sentence names them all
            if tuple(error.absolute_path) in seen:
                continue
            seen.add(tuple(error.absolute_path))
        make = SENTENCES.get(error.validator)
        problems += make(error, where) if make else [f"{where} is not right: {shown(error.message)}."]
    return problems


ACCEPTED = {  # fields the schema accepts but nothing builds yet (D-08): block -> name -> what happens instead
    "list": {
        "text": "The list's text is accepted but not built yet, so no words are drawn.",
        "voice": "The list's voice track is accepted but not built yet, so it is not in the reel.",
    },
    "segment": {
        "speed": "{where}'s speed is accepted but not built yet, so the shot plays at normal speed.",
        "transition": "{where}'s transition is accepted but not built yet, so the cut is straight.",
        "text": "{where}'s text is accepted but not built yet, so no words are drawn.",
    },
}


def resolved(schema, node):
    """A schema node with a local `$defs` reference followed."""
    ref = node.get("$ref", "")
    return schema["$defs"][ref.removeprefix("#/$defs/")] if ref.startswith("#/$defs/") else node


def field_notes(data, schema):
    """A note for each field the list holds that is accepted but not built, and for each the rulebook does not name.

    The known names are the rulebook's own, so the schema stays the one source. Names are compared exactly, case and
    all. An accepted field whose value is null, empty text, an empty list or an empty block gives no note.
    """
    notes = []

    def visit(block, node, where, accepted=None):
        if not isinstance(block, dict):
            return
        known = resolved(schema, node).get("properties", {})
        for name, value in block.items():
            if name not in known:
                notes.append(f"{where} has a field called {value_words(name)} that v2r does not know, so it was ignored.")
            elif name in (accepted or {}):
                if not (value is None or (isinstance(value, (str, list, dict)) and not value)):
                    notes.append(accepted[name].format(where=where))

    props = schema["properties"]
    visit(data, schema, "The list", ACCEPTED["list"])
    visit(data.get("canvas"), props["canvas"], "The canvas")
    clips = data.get("clips")
    for letter, record in (clips.items() if isinstance(clips, dict) else []):
        visit(record, props["clips"]["additionalProperties"], f"Clip {shown(letter)}'s record")
    segments = data.get("segments")
    for number, item in enumerate(segments if isinstance(segments, list) else [], start=1):
        visit(item, props["segments"]["items"], f"Segment {number}", ACCEPTED["segment"])
    look = data.get("look")
    visit(look, props["look"], "The look")
    touch_ups = look.get("touch_up") if isinstance(look, dict) else None
    for letter, record in (touch_ups.items() if isinstance(touch_ups, dict) else []):
        visit(record, props["look"]["properties"]["touch_up"]["additionalProperties"], f"Clip {shown(letter)}'s touch-up")
    visit(data.get("sound"), props["sound"], "The sound")
    visit(data.get("cover"), props["cover"], "The cover")
    return notes


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


def plain_file(name, work_dir):
    """True when `name` is the plain name of a file directly inside the work folder (T-4-02): no folders, no hidden names."""
    if not isinstance(name, str) or not name or name.startswith(".") or Path(name).name != name:
        return False
    folder = Path(work_dir).resolve()
    path = folder / name
    return path.is_file() and path.resolve().parent == folder


def letters_sentence(letters):
    """"A", "A and B" or "A, B and C"."""
    if len(letters) <= 1:
        return "".join(letters)
    return ", ".join(letters[:-1]) + " and " + letters[-1]


def clips_problem(letter, record, manifest, work_dir):
    """The one sentence that says why a clip of the list's clips block does not match the work folder, or None."""
    if not look.LETTER.fullmatch(letter):
        return f"The list's clips name \"{shown(letter)}\"; a clip's name must be a capital letter such as A."
    found = next((entry for entry in manifest["clips"] if entry["letter"] == letter), None)
    if found is None:
        done = [entry["letter"] for entry in manifest["clips"] if entry.get("status") == "done"]
        return f"Clip {letter} in this list is not in the work folder, which has clips {letters_sentence(done)}."
    if found.get("status") == "skipped":
        return f"Clip {letter} was skipped when the clips were converted, so it cannot be in the list."
    entry = manifest_entry(manifest, letter)
    missing = f"The working copy of clip {letter} is missing or not in the work folder, so it cannot be built."
    if entry is None:
        return missing
    name = (entry.get("original") or {}).get("name")
    if unicodedata.normalize("NFC", record["file"]) != unicodedata.normalize("NFC", name if isinstance(name, str) else ""):
        return f"Clip {letter} in this list was {shown(record['file'])}, but {letter} in the work folder is {shown(name)}."
    folder_seconds = working_seconds(entry)
    if folder_seconds is not None and plan.clip_frames(record["seconds"]) != plan.clip_frames(folder_seconds):
        return (
            f"Clip {letter} in this list is {record['seconds']:.2f} seconds long, "
            f"but {letter} in the work folder is {folder_seconds:.2f} seconds long.")
    facts = look.working_facts(entry, work_dir)
    if isinstance(facts, str):
        return missing
    if abs(facts[2] - settings.OUTPUT_FPS) > 0.001:
        return f"The working copy of clip {letter} is not at {settings.OUTPUT_FPS} frames a second, so normalize has to make it again."
    if entry["kind"] == "photo" and not plain_file((entry.get("photo") or {}).get("file"), work_dir):
        return f"The full-size copy of photo {letter} is missing from the work folder, so it cannot be built."
    return None


def clips_problems(data, manifest, work_dir):
    """The list's clips block must be the work folder's clips: same letters, files and lengths, one sentence per clip (D-04)."""
    problems = []
    for letter, record in sorted(data["clips"].items()):  # letter order, so the order the list wrote them in changes nothing
        problem = clips_problem(letter, record, manifest, work_dir)
        if problem:
            problems.append(problem)
    return problems


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


def count_problems(data):
    """A reel can hold at most settings.MAX_SEGMENTS segments, so the proof sheets and the plan stay small (T-4-03)."""
    count = len(data["segments"])
    if count > settings.MAX_SEGMENTS:
        return [f"The list has {count} segments; one reel can have at most {settings.MAX_SEGMENTS}."]
    return []


def look_problems(data):
    """Each touch-up must be for a clip of the list and stay within its caps; a number exactly at a cap is allowed (D-06, D-23)."""
    touch_ups = (data.get("look") or {}).get("touch_up") or {}
    problems = []
    for letter, record in sorted(touch_ups.items()):  # letter order, as for the clips
        name = shown(letter)
        if letter not in data["clips"]:
            problems.append(f"The touch-up names clip {name}, which is not in the list's clips.")
        for field_name, cap in (
                ("brightness", settings.TOUCH_UP_MAX_BRIGHTNESS), ("blue", settings.TOUCH_UP_MAX_COLOUR),
                ("red", settings.TOUCH_UP_MAX_COLOUR)):
            value = record[field_name]
            if abs(value) > cap:
                problems.append(f"Clip {name}'s touch-up {field_name} is {value:g}; it can be at most {cap:g} either way.")
        low, high = settings.TOUCH_UP_SATURATION_MIN, settings.TOUCH_UP_SATURATION_MAX
        value = record["saturation"]
        if not low <= value <= high:
            problems.append(f"Clip {name}'s touch-up saturation is {value:g}; it must be between {low:g} and {high:g}.")
    return problems


def segment_lengths(data):
    """The frames each segment covers, in the list's order, or None when any segment lasts less than a frame.

    A segment that is not a real stretch (it ends before it starts, or lasts under a frame) has its own sentence, and
    a sentence about the whole reel's length would rest on it, so the rules about the whole reel wait for it to be fixed.
    """
    counts = [plan.segment_frames(segment)[1] for segment in data["segments"]]
    return None if any(count < 1 for count in counts) else counts


def cover_problems(data):
    """The cover must name a segment of the list and a moment inside it (D-09)."""
    cover = data.get("cover")
    if not isinstance(cover, dict):
        return []
    number, at = cover["segment"], cover["at"]
    total = len(data["segments"])
    if number > total:
        return [f"The cover names segment {number}, but the list has only {total} segments."]
    count = plan.segment_frames(data["segments"][number - 1])[1]
    if count < 1:  # that segment's own sentence says what is wrong with it
        return []
    seconds = count / settings.OUTPUT_FPS
    if at >= seconds:
        return [
            f"The cover is at {at:.1f} seconds into segment {number}, but segment {number} is only {seconds:.1f} seconds long."]
    return []


def seconds_pair(smaller, larger):
    """Two lengths as text, to one decimal place unless that would make two different lengths read the same."""
    for places in (1, 2, 3):
        first, second = f"{smaller:.{places}f}", f"{larger:.{places}f}"
        if first != second:
            break
    return first, second


def length_problems(data):
    """The reel must last at least settings.MIN_REEL_SECONDS: a shorter one is a mistake, not a reel."""
    counts = segment_lengths(data)
    if counts is None:
        return []
    if sum(counts) < plan.frames(settings.MIN_REEL_SECONDS):
        reel, _ = seconds_pair(sum(counts) / settings.OUTPUT_FPS, settings.MIN_REEL_SECONDS)
        return [f"The reel is {reel} seconds long; it must be at least {settings.MIN_REEL_SECONDS:g} seconds."]
    return []


def sound_problems(data):
    """The music must be a track the library holds, and long enough from where it starts to the end of the reel (D-07, D-15).

    Nothing is looped and nothing is cut: a track that is too short is refused, and the sentence says the reel needs an
    earlier start or another track.
    """
    chosen = sound.sound_settings(data)
    if chosen["music"] is None:
        return []
    try:
        found = sound.track(chosen["music"], sound.MUSIC_DIR)
    except sound.LibraryError as error:
        return [str(error)]
    start, seconds = chosen["music_from"], found["seconds"]
    name = shown(found["id"])
    if start >= seconds:
        return [f'The music track "{name}" is {seconds:.1f} seconds long, so it cannot start at {start:.1f} seconds.']
    counts = segment_lengths(data)
    if counts is None:
        return []
    reel = sum(counts) / settings.OUTPUT_FPS
    remaining = seconds - start
    if round(remaining, 6) < round(reel, 6):
        ends, lasts = seconds_pair(remaining, reel)
        return [f"The music runs out at {ends} seconds but the reel is {lasts} seconds long."]
    return []


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


def crop_notes(data, manifest):
    """A note for each clip, in letter order, that is turned the other way from the canvas and keeps little of its picture.

    Wider than high in a tall frame is "sideways", higher than wide in a wide frame is "upright"; a square is neither.
    The share kept is plan.fill_region's, the one the renderer crops by, and a photo's is over its full-size copy.
    """
    canvas = data["canvas"]
    shape = plan.shape_of([canvas["width"], canvas["height"]])
    notes = []
    for letter in sorted({segment["clip"] for segment in data["segments"]}):
        entry = manifest_entry(manifest, letter)
        if entry is None or shape is None:
            continue
        photo = entry["kind"] == "photo"
        size = (entry.get("photo") or {}).get("size") if photo else entry["working"].get("size")
        if not (isinstance(size, list) and len(size) == 2 and all(isinstance(side, int) and side > 0 for side in size)):
            continue
        width, height = size
        turned = "sideways" if width > height and shape == "tall" else "upright" if height > width and shape == "wide" else None
        if turned is None:
            continue
        share = plan.fill_region(size, [canvas["width"], canvas["height"]])["share"]
        if share < settings.CROP_NOTE_SHARE:
            subject = f"Photo {shown(letter)}" if photo else f"Clip {shown(letter)}"
            notes.append(
                f"{subject} is {turned} in a {shape} frame, so the frame keeps only {round(share * 100)} percent of its picture.")
    return notes


def rule_notes(data, manifest):
    """Notes that are worth saying but never refuse: no touch-up, a photo with no move, a crop that keeps little, no sound.

    In this order: the missing touch-up (D-06), photos with no move in segment order (D-21), crops in letter order
    (D-10), and a reel with no sound at all (D-17). The handbook asks for a push-in on a photo and for match to run;
    the checker only says so and the renderer builds the list as it stands.
    """
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


def check(cutlist_path=None, work_dir=None):
    """Check a cut list against its rulebook and the work folder; returns Checked. Reads only; writes nothing."""
    work_dir = Path(WORK_DIR if work_dir is None else work_dir)
    path = Path(work_dir / "cutlist.json" if cutlist_path is None else cutlist_path)
    data, problems = read_cutlist(path)
    checked = Checked(cutlist=data)
    if problems:
        checked.manifest, more = read_manifest(work_dir)
        checked.problems = problems + more
        return checked
    missing = jsonschema_problem()
    if missing:
        checked.problems = [missing]
        return checked
    try:
        schema = load_schema()
    except Refused as refusal:
        checked.problems = [str(refusal)]
        return checked
    checked.problems = schema_problems(data, schema)
    if isinstance(data, dict):
        checked.notes = field_notes(data, schema)
    if checked.problems:
        checked.notes.append(NOT_COMPARED)
        return checked
    checked.manifest, checked.problems = read_manifest(work_dir)
    if checked.problems:
        return checked
    manifest = checked.manifest
    # The rules run in a stated order and every one of them reports, so a list with several faults gets all its
    # sentences at once. The fit is the exception: it measures the reel, so it waits until nothing before it failed.
    checked.problems = (
        canvas_problems(data, manifest) + clips_problems(data, manifest, work_dir) + count_problems(data)
        + segment_problems(data, manifest, work_dir) + look_problems(data) + sound_problems(data)
        + cover_problems(data) + length_problems(data))
    if not checked.problems:
        checked.problems = fit_problems(data)
    checked.notes += rule_notes(data, manifest)
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
