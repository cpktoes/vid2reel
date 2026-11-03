"""`v2r revise`: make one named change to an existing cut list and write the result as a new numbered list beside it.

The first revise of cutlist.json writes cutlist-2.json, the next cutlist-3.json. The input is never opened for writing
and no existing file is ever replaced. revise never renders and never runs FFmpeg: it writes one list and runs check on
it. It decides nothing about the edit; the chat's Claude names the change (and, for shorter and longer, the shots), and
every other field stays exactly as it was, fields revise has never heard of included.

The change words are sound and canvas (here), reorder and drop (a later plan) and shorter and longer (a later plan).
"""

import copy
import json
import re
from pathlib import Path

from v2r import WORK_DIR, normalize, settings
from v2r.render import check

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


CHANGES = {"sound": change_sound}


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
