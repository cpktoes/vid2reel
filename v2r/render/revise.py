"""`v2r revise`: make one named change to an existing cut list and write the result as a new numbered list beside it.

The first revise of cutlist.json writes cutlist-2.json, the next cutlist-3.json. The input is never opened for writing
and no existing file is ever replaced. revise never renders and never runs FFmpeg: it writes one list and runs check on
it. It decides nothing about the edit; the chat's Claude names the change (and, for shorter and longer, the shots), and
every other field stays exactly as it was, fields revise has never heard of included.

The change words are sound, canvas, reorder and drop (here) and shorter and longer (a later plan).
"""

import copy
import json
import re
from pathlib import Path

from v2r import WORK_DIR, normalize, settings
from v2r.render import check, plan

WORK_GONE = (
    "There is no cut list and no manifest.json in the work folder, so there is nothing to change; "
    "attach the clips again and make the reel anew.")
BROKEN = "The cut list breaks its rulebook, so nothing was changed; fix the problems above first."
NO_WRITE = "The new cut list could not be written beside the old one, so nothing was changed."
OLD_NUMBERS = "Shot numbers in the lines below are the old list's."
STILL_IN_USE = "{path} is still the list to use."


class ReviseError(Exception):
    """revise can't make the change; the message is one plain sentence and nothing was written."""


class Unchanged(Exception):
    """The list is already as asked; the message is one sentence and nothing was written."""


def digits_pattern():
    """The pattern for one to settings.REVISE_NUMBER_DIGITS ASCII digits, built when called so the setting rules."""
    return "[0-9]{1,%d}" % settings.REVISE_NUMBER_DIGITS


def no_shot(number, count):
    if count == 1:
        return f"There is no shot {number} in this list; it has only shot 1."
    return f"There is no shot {number} in this list; it has shots 1 to {count}."


def not_a_shot(text):
    return f'"{check.shown(text)}" is not a shot number such as 3; shots are counted from 1 in list order.'


def parse_shot(text, count):
    """The shot number `text` names, or ReviseError in one sentence; nothing but plain digits reaches int()."""
    if not isinstance(text, str) or re.fullmatch(digits_pattern(), text, flags=re.ASCII) is None:
        raise ReviseError(not_a_shot(text))
    number = int(text)
    if number < 1 or number > count:
        raise ReviseError(no_shot(number, count))
    return number


def shown_path(path):
    """A path made safe to print; check.shown would cut it at 40 characters, so it is not used for paths."""
    return normalize.clean_text(str(path))


def next_list_path(path):
    """The next free name in the input's family: cutlist.json gives cutlist-2.json, then cutlist-3.json.

    Numbers only go up, even when a middle file has been deleted. The folder is read with iterdir, never glob, because
    the stem may hold glob characters.
    """
    path = Path(path)
    stem = re.sub("-[0-9]+$", "", path.stem)
    pattern = re.compile(re.escape(stem) + "-(" + digits_pattern() + r")\.json", re.ASCII)
    highest = 1
    try:
        names = [entry.name for entry in path.parent.iterdir()]
    except OSError:
        names = []
    for name in names:
        found = pattern.fullmatch(name)
        if found:
            highest = max(highest, int(found.group(1)))
    return path.parent / f"{stem}-{highest + 1}.json"


def write_new(path, data):
    """Write `data` as the next numbered list beside `path`, created exclusively; returns the new path."""
    text = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    for _ in range(max(1, settings.REVISE_NAME_TRIES)):
        target = next_list_path(path)
        try:
            with open(target, "x", encoding="utf-8") as handle:
                try:
                    handle.write(text)
                except (OSError, ValueError):
                    handle.close()
                    target.unlink(missing_ok=True)
                    raise
        except FileExistsError:
            continue
        except (OSError, ValueError):
            raise ReviseError(NO_WRITE) from None
        return target
    raise ReviseError(NO_WRITE)


def read_list(path, folder):
    """The cut list as Python data, read strictly and checked against its rulebook; ReviseError when it can't be used.

    The whole of check is not run here: it refuses a tall list over a wide work folder, which is the very state
    "a wide version" starts from. The closing check on the new list says that instead.
    """
    path = Path(path)
    if not path.is_file() and not (Path(folder) / "manifest.json").is_file():
        raise ReviseError(WORK_GONE)
    data, problems = check.read_cutlist(path)
    if problems:
        raise ReviseError(problems[0])
    missing = check.jsonschema_problem()
    if missing:
        raise ReviseError(missing)
    try:
        schema = check.load_schema()
    except check.Refused as refusal:
        raise ReviseError(str(refusal)) from None
    found = check.schema_problems(data, schema)
    if not found:
        found = check.time_problems(data)
    if found:
        for problem in found:
            print(f"Problem: {problem}")
        raise ReviseError(BROKEN)
    return data


def change_sound(data, options, folder):
    """Keep or mute the shots' own sound: every shot, or the one named by options["shot"]; the music block is not touched."""
    setting = options["setting"]
    segments = data["segments"]
    if options.get("shot") is None:
        numbers = list(range(1, len(segments) + 1))
        same = f"Every shot's sound is already {setting}, so nothing was changed."
    else:
        number = parse_shot(options["shot"], len(segments))
        numbers = [number]
        same = f"Shot {number}'s sound is already {setting}, so nothing was changed."
    lines = []
    for number in numbers:
        shot = segments[number - 1]
        if shot.get("sound") != setting:
            lines.append(f"Shot {number}'s sound: was {shot.get('sound')}, now {setting}.")
            shot["sound"] = setting
    if not lines:
        raise Unchanged(same)
    return lines


def change_canvas(data, options, folder):
    """Make the list tall or wide: only the canvas's width and height change; fps, shots and focus points stay."""
    shape = options["shape"]
    width, height = settings.SHAPES[shape]
    canvas = data["canvas"]
    old = plan.shape_of([canvas["width"], canvas["height"]])
    if old == shape:
        raise Unchanged(f"The canvas is already {shape}, so nothing was changed.")
    old_width, old_height = canvas["width"], canvas["height"]
    canvas["width"] = width
    canvas["height"] = height
    return [
        f"The canvas: was {old or 'not a known shape'} {old_width}x{old_height}, now {shape} {width}x{height}; "
        "nothing else changed."]


def parse_shot_list(text, count):
    """The shot numbers `text` names, in the order given, each once; ReviseError in one sentence when it can't be read.

    The length is checked before anything is converted, so a very long list costs nothing.
    """
    not_a_list = (
        f'"{check.shown(text)}" is not a list of shot numbers such as 4,2; shots are counted from 1 in list order.')
    if not isinstance(text, str):
        raise ReviseError(not_a_list)
    items = [item.strip() for item in text.split(",")]
    if len(items) > settings.MAX_SEGMENTS:
        raise ReviseError(f"That names more than {settings.MAX_SEGMENTS} shots, more than a list can hold.")
    numbers = []
    for item in items:
        if re.fullmatch(digits_pattern(), item, flags=re.ASCII) is None:
            raise ReviseError(not_a_list)
        number = parse_shot(item, count)
        if number in numbers:
            raise ReviseError(f"Shot {number} is named twice; name each shot once.")
        numbers.append(number)
    return numbers


def follow_cover(data, mapping):
    """Keep the cover on its shot. `mapping` takes each old shot number (from 1) to its new number, or None if taken out.

    A cover that is missing or not usable is left alone: check reports that itself. Returns the lines to print.
    """
    cover = data.get("cover")
    if not isinstance(cover, dict):
        return []
    old = cover.get("segment")
    if not check.is_whole(old) or old not in mapping:
        return []
    new = mapping[old]
    if new is None:
        del data["cover"]
        return [f"The cover was in shot {old}, which was taken out, so the reel's first frame is the cover now."]
    if new == old:
        return []
    cover["segment"] = new
    return [f"The cover moved with its shot: it was in shot {old}, now shot {new}."]


def change_reorder(data, options, folder):
    """Play the shots in the order given: the very same shot records, only their places change; the cover follows."""
    count = len(data["segments"])
    order = parse_shot_list(options["order"], count)
    if len(order) != count:
        have = "1 shot" if count == 1 else f"{count} shots"
        raise ReviseError(f"Reorder needs every shot number once, in the new order; this list has {have}.")
    if order == list(range(1, count + 1)):
        raise Unchanged("The shots are already in that order, so nothing was changed.")
    old = data["segments"]
    data["segments"] = [old[number - 1] for number in order]
    lines = [
        OLD_NUMBERS,
        f"The shots now play as old shots {check.letters_sentence([str(number) for number in order])}; "
        "each shot itself is unchanged."]
    return lines + follow_cover(data, {before: after for after, before in enumerate(order, start=1)})


CHANGES = {"sound": change_sound, "canvas": change_canvas, "reorder": change_reorder}


def run(change, options, cutlist_path=None, work_dir=None):
    """Make the change; returns (new list path or None, lines to print, ready). Raises ReviseError when it can't.

    The new path comes first among the lines so it is never lost. Nothing is written when nothing needed changing.
    """
    folder = Path(WORK_DIR if work_dir is None else work_dir)
    path = Path(folder / "cutlist.json" if cutlist_path is None else cutlist_path)
    data = read_list(path, folder)
    new = copy.deepcopy(data)
    try:
        lines = CHANGES[change](new, options, folder)
    except Unchanged as same:
        return None, [f"{same} " + STILL_IN_USE.format(path=shown_path(path))], True
    new_path = write_new(path, new)
    out = ["New cut list: " + shown_path(new_path)] + lines
    checked = check.check(new_path, work_dir)
    out += check.report(checked)
    ready = not checked.problems
    work_words = "" if work_dir is None else " --work " + shown_path(work_dir)
    out.append(("Next: " if ready else "Once the problems above are fixed: ") + "python3 -m v2r render " + shown_path(new_path) + work_words)
    out.append("Any further change starts from this list: python3 -m v2r revise CHANGE --cutlist " + shown_path(new_path) + work_words)
    return new_path, out, ready
