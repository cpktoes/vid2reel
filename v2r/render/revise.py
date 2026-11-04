"""`v2r revise`: make one named change to an existing cut list and write the result as a new numbered list beside it.

The first revise of cutlist.json writes cutlist-2.json, the next cutlist-3.json. The input is never opened for writing
and no existing file is ever replaced. revise never renders and never runs FFmpeg: it writes one list and runs check on
it. It decides nothing about the edit; the chat's Claude names the change (and, for shorter and longer, the shots), and
every other field stays exactly as it was, fields revise has never heard of included.

The change words are sound, canvas, reorder, drop, shorter and longer.
"""

import copy
import json
import math
import re
from pathlib import Path

from v2r import WORK_DIR, look, normalize, settings
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
    """Write `data` as the next numbered list beside `path`, created exclusively; returns the new path.

    The create, the write and the close share one cleanup: a list is small enough to sit in Python's buffer until the
    file is closed, so a full disk shows up at the close, not at the write. Whatever step fails, the half-written file
    is removed before NO_WRITE is raised, so "nothing was changed" stays true and the number is not used up.
    """
    text = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    for _ in range(max(1, settings.REVISE_NAME_TRIES)):
        target = next_list_path(path)
        try:
            with open(target, "x", encoding="utf-8") as handle:
                handle.write(text)
        except FileExistsError:  # the "x" open created nothing, so there is nothing to remove: try the next name
            continue
        except (OSError, ValueError):  # the "x" open did create the file, so removing it is right
            try:
                target.unlink(missing_ok=True)
            except OSError:
                pass
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


DROP_WORDS = "Drop needs a clip letter such as C, or the word shot and a number such as shot 3."
LAST_SHOT = "That would leave the reel with no shots, so nothing was changed."


def change_drop(data, options, folder):
    """Take out every shot of one clip (a capital letter) or one shot (the word shot and its number).

    Only the shots go. The clips block and the touch-up are left as they are: check never requires a clip to have a
    shot, and a touch-up whose clip has no shot harms nothing. The cover follows its shot or is removed with it.
    """
    words = options["what"]
    segments = data["segments"]
    count = len(segments)
    # A clip letter is one to three capitals: normalize's and the schema's own pattern, not a new limit. look.LETTER is
    # the one place it is written in code (check reads letters with it too), so the two never drift apart.
    if len(words) == 1 and look.LETTER.fullmatch(words[0]):
        letter = words[0]
        gone = [number for number, shot in enumerate(segments, start=1) if shot.get("clip") == letter]
        if not gone:
            if isinstance(data.get("clips"), dict) and letter in data["clips"]:
                raise Unchanged(f"Clip {letter} has no shots in this list, so nothing was changed.")
            used = sorted({shot.get("clip") for shot in segments if isinstance(shot.get("clip"), str)})
            raise ReviseError(
                f"There is no clip {letter} in this list's shots; its shots use clips {check.letters_sentence(used)}.")
        whole_clip = True
    elif len(words) == 2 and words[0] == "shot":
        gone = [parse_shot(words[1], count)]
        whole_clip = False
    else:
        raise ReviseError(DROP_WORDS)
    if len(gone) == count:
        raise ReviseError(LAST_SHOT)
    mapping = {}
    kept = []
    for number, shot in enumerate(segments, start=1):
        if number in gone:
            mapping[number] = None
        else:
            kept.append(shot)
            mapping[number] = len(kept)
    lines = [OLD_NUMBERS]
    for number in gone:
        lines.append(f"Shot {number} (clip {check.shown(segments[number - 1].get('clip'))}) was taken out.")
    if whole_clip:
        look_block = data.get("look")  # the list's own "look" field, not the look module
        touch_ups = look_block.get("touch_up") if isinstance(look_block, dict) else None
        if isinstance(touch_ups, dict) and letter in touch_ups:
            lines.append(f"Clip {letter}'s record and touch-up stay in the list, unused.")
        else:
            lines.append(f"Clip {letter}'s record stays in the list, unused.")
    data["segments"] = kept
    return lines + follow_cover(data, mapping)


def seconds_text(frames):
    """`frames` as seconds for revise's own sentences: "15", "2.5", "6.67"; trailing zeros and a bare point are dropped."""
    text = f"{frames / settings.OUTPUT_FPS:.{settings.REVISE_SHOWN_DECIMALS}f}"
    return text.rstrip("0").rstrip(".") if "." in text else text


def parse_target(text):
    """(seconds, whole frames) for a length typed as a plain number of seconds, or ReviseError in one sentence.

    Only ASCII digits, with at most a point and more digits, reach float(): no sign, exponent, nan or inf. The digit
    limits are settings, and the value must be above 0 and at most settings.MAX_CUTLIST_SECONDS.
    """
    refused = "The length to aim for must be a number of seconds, such as 15."
    pattern = "[0-9]{1,%d}(\\.[0-9]{1,%d})?" % (settings.REVISE_SECONDS_DIGITS, settings.REVISE_FRACTION_DIGITS)
    if not isinstance(text, str) or re.fullmatch(pattern, text, flags=re.ASCII) is None:
        raise ReviseError(refused)
    value = float(text)
    if not 0 < value <= settings.MAX_CUTLIST_SECONDS:
        raise ReviseError(refused)
    return value, plan.frames(value)


def set_frames(segment, count):
    """Make the shot last exactly `count` frames from its first frame: "from" is left alone and "to" is written.

    A shot's length is the rounded `to - from`, and its end frame the rounded `to`, so both are checked against what
    check and render will count. "to" is tried to settings.REVISE_DECIMALS places, then to
    settings.REVISE_DECIMALS_EXACT places. That is enough unless the start sits exactly half way into a frame (0.05
    seconds is 1.5 frames): the intended end is then exactly half a frame too, and a repeating decimal such as
    0.083333 falls just short of it, so the last try is the same number rounded up at the last place.
    """
    start = segment["from"]
    first = plan.frames(start)
    exact = 10 ** settings.REVISE_DECIMALS_EXACT
    wanted = start + count / settings.OUTPUT_FPS
    for end in (
            round(wanted, settings.REVISE_DECIMALS), round(wanted, settings.REVISE_DECIMALS_EXACT),
            math.ceil(wanted * exact) / exact):
        segment["to"] = end
        if plan.segment_frames(segment) == (first, count) and plan.frames(end) == first + count:
            return
    raise ReviseError("A shot's end could not be written to the exact frame, so nothing was changed.")


class CannotShorten(Exception):
    """Even with every shot at its shortest, and every shot that may be dropped dropped, the reel is over the target.

    `frames` is the total of the shots left at their shortest and `dropped` the 0-based shots dropped, in the order
    they were dropped. The function that raises it stays pure: the sentence is written by change_shorter.
    """

    def __init__(self, frames, dropped):
        super().__init__(frames, dropped)
        self.frames = frames
        self.dropped = dropped


def shorter_frames(lengths, floor, target, named):
    """The shots' new lengths in frames (None for a dropped shot) and the 0-based shots dropped, in drop order.

    `named` are 0-based shots in the order the chat's Claude named them; nothing here judges a shot. A shot is never
    taken under `floor` (or under its own length, if that is shorter). Whole shots are dropped only when even the
    floors are over `target`, from the end of the named list, never shot 0, never one not named. Otherwise the named
    shots go down to their floors in order, then what remains is shared evenly across the others: equal shares, and
    when frames are left over, one each from the later shots. Raises CannotShorten when the named shots run out.
    """
    named = list(dict.fromkeys(named))
    floors = [min(length, floor) for length in lengths]
    alive = [True] * len(lengths)
    dropped = []
    candidates = [index for index in reversed(named) if index != 0]
    while sum(f for f, here in zip(floors, alive) if here) > target:
        if not candidates:
            raise CannotShorten(sum(f for f, here in zip(floors, alive) if here), dropped)
        index = candidates.pop(0)
        alive[index] = False
        dropped.append(index)
    new = [length if here else None for length, here in zip(lengths, alive)]
    excess = sum(length for length, here in zip(lengths, alive) if here) - target
    for index in named:
        if excess <= 0:
            break
        if alive[index]:
            give = min(new[index] - floors[index], excess)
            new[index] -= give
            excess -= give
    others = [index for index in range(len(lengths)) if alive[index] and index not in named and new[index] > floors[index]]
    while excess > 0 and others:
        share, extra = divmod(excess, len(others))
        if share:
            for index in others:
                give = min(new[index] - floors[index], share)
                new[index] -= give
                excess -= give
        else:
            for index in others[len(others) - extra:]:
                new[index] -= 1
                excess -= 1
        others = [index for index in others if new[index] > floors[index]]
    return new, dropped


def read_shots_and_target(data, options):
    """(0-based named shots, the target as typed in seconds, the target in frames, each shot's frames, their total)."""
    count = len(data["segments"])
    shots = parse_shot_list(options["shots"], count)
    value, target = parse_target(options["to"])
    lengths = check.segment_lengths(data)
    if lengths is None:
        raise ReviseError(
            "A shot in this list lasts less than one frame, so the lengths cannot be worked out; run check to see which.")
    return [number - 1 for number in shots], value, target, lengths, sum(lengths)


def change_shorter(data, options, folder):
    """Trim the named shots from their ends, in the order named, to reach the length asked; see shorter_frames."""
    named, value, target, lengths, total = read_shots_and_target(data, options)
    if target < plan.frames(settings.MIN_REEL_SECONDS):
        raise ReviseError(f"A reel must be at least {settings.MIN_REEL_SECONDS:g} seconds, so it cannot be made shorter than that.")
    if target == total:
        raise Unchanged(f"The reel is already {seconds_text(total)} seconds, so nothing was changed.")
    if target > total:
        raise ReviseError(
            f"The reel is {seconds_text(total)} seconds, already shorter than the {value:g} asked; use longer to make it longer.")
    recipe = data.get("recipe", settings.DEFAULT_RECIPE)
    floor = plan.frames(settings.RECIPES[recipe][0])
    try:
        new, dropped = shorter_frames(lengths, floor, target, named)
    except CannotShorten as refusal:
        gone = [index + 1 for index in named if index in refusal.dropped]  # in the order they were named
        if gone:
            who = check.letters_sentence([str(number) for number in gone])
            raise ReviseError(
                f"Even with every shot at its shortest and shots {who} dropped, the reel would be "
                f"{seconds_text(refusal.frames)} seconds, so nothing was changed; name more shots to take it to {value:g} seconds."
            ) from None
        raise ReviseError(
            f"Even with every shot at its shortest, the reel would be {seconds_text(refusal.frames)} seconds, "
            f"so nothing was changed; name more shots to take it to {value:g} seconds.") from None
    segments = data["segments"]
    lines = [OLD_NUMBERS] if dropped else []
    for index in named:
        if index not in dropped and lengths[index] <= floor:
            lines.append(f"Shot {index + 1} was already at its shortest for {recipe.capitalize()}, so it was left as it was.")
    for index in dropped:
        lines.append(f"Shot {index + 1} was dropped: even at their shortest the shots were too long for {value:g} seconds.")
    mapping = {}
    kept = []
    for index, shot in enumerate(segments):
        if new[index] is None:
            mapping[index + 1] = None
            continue
        kept.append(shot)
        mapping[index + 1] = len(kept)
        if new[index] != lengths[index]:
            set_frames(shot, new[index])
            lines.append(f"Shot {index + 1}: was {seconds_text(lengths[index])} seconds, now {seconds_text(new[index])}.")
    new_total = sum(count for count in new if count is not None)
    lines.append(f"The reel is now {seconds_text(new_total)} seconds; it was {seconds_text(total)}.")
    if new_total < target:
        lines.append(f"That is {seconds_text(target - new_total)} seconds under the {value:g} asked, because a whole shot had to go.")
    data["segments"] = kept
    cover = data.get("cover")
    old_shot = cover.get("segment") if isinstance(cover, dict) else None
    lines += follow_cover(data, mapping)
    cover = data.get("cover")
    if isinstance(cover, dict) and check.is_whole(old_shot) and mapping.get(old_shot) is not None and check.is_number(cover.get("at")):
        index = old_shot - 1
        if new[index] != lengths[index] and cover["at"] >= new[index] / settings.OUTPUT_FPS:
            lines.append(
                f"The cover was {cover['at']:g} seconds into shot {old_shot}, which is now only {seconds_text(new[index])} "
                "seconds long, so the reel's first frame is the cover now.")
            del data["cover"]
    return lines


def longer_frames(lengths, ceilings, target, named):
    """The shots' new lengths in frames: the named shots, in order, each gain what is wanted up to its ceiling.

    `named` are 0-based shots in the order the chat's Claude named them; nothing here judges a shot. A ceiling at or
    under a shot's own length means it gains nothing, and no shot ever gets shorter. The total is at most `target`.
    """
    new = list(lengths)
    wanted = target - sum(lengths)
    for index in named:
        if wanted <= 0:
            break
        give = min(max(0, ceilings[index] - lengths[index]), wanted)
        new[index] += give
        wanted -= give
    return new


def ceiling_frames(shot, shots, entry, recipe_longest):
    """The most frames the shot `shot` can last: the recipe's longest, the end of its clip, the next shot of its clip.

    A photo is exempt from the recipe (its own clip's length is its limit). With no usable length for its clip a shot
    can't be extended at all. `shots` are all the list's shots, `entry` the work folder's record of the shot's clip.
    """
    start, count = plan.segment_frames(shot)
    seconds = None if entry is None else check.working_seconds(entry)
    if seconds is None:
        return count
    most = plan.clip_frames(seconds) - start
    for other in shots:
        if other is not shot and other.get("clip") == shot.get("clip"):
            later = plan.frames(other["from"])
            if later > start:  # a shot starting on the same frame is not "after"
                most = min(most, later - start)
    if entry["kind"] != "photo":
        most = min(most, recipe_longest)
    return most


def change_longer(data, options, folder):
    """Let the named shots run on at their ends, in the order named, towards the length asked; see longer_frames."""
    named, value, target, lengths, total = read_shots_and_target(data, options)
    if target == total:
        raise Unchanged(f"The reel is already {seconds_text(total)} seconds, so nothing was changed.")
    if target < total:
        raise ReviseError(
            f"The reel is {seconds_text(total)} seconds, already longer than the {value:g} asked; use shorter to make it shorter.")
    manifest, problems = check.read_manifest(folder)
    if problems:
        raise ReviseError(problems[0])
    mismatches = check.clips_problems(data, manifest, folder)
    if mismatches:
        for problem in mismatches:
            print(f"Problem: {problem}")
        raise ReviseError("The cut list's clips do not match the work folder, so nothing was changed; run check to see why.")
    recipe = data.get("recipe", settings.DEFAULT_RECIPE)
    longest = plan.frames(settings.RECIPES[recipe][1])
    segments = data["segments"]
    ceilings = [
        ceiling_frames(shot, segments, check.manifest_entry(manifest, shot.get("clip")), longest) for shot in segments]
    new = longer_frames(lengths, ceilings, target, named)
    grown = [index for index in named if new[index] > lengths[index]]
    if not grown:
        if len(named) == 1:
            raise ReviseError(
                f"Shot {named[0] + 1} cannot run longer, being at its recipe's longest, at the end of its clip or at the next "
                "shot of the same clip, so nothing was changed; a longer reel needs a new moment added to the list.")
        who = check.letters_sentence([str(index + 1) for index in named])
        raise ReviseError(
            f"None of shots {who} can run longer, each being at its recipe's longest, at the end of its clip or at the next "
            "shot of the same clip, so nothing was changed; a longer reel needs a new moment added to the list.")
    lines = []
    for index in named:
        if index not in grown:
            lines.append(f"Shot {index + 1} cannot run longer, so it was left as it was.")
    for index in range(len(segments)):
        if index in grown:
            set_frames(segments[index], new[index])
            lines.append(f"Shot {index + 1}: was {seconds_text(lengths[index])} seconds, now {seconds_text(new[index])}.")
    new_total = sum(new)
    lines.append(f"The reel is now {seconds_text(new_total)} seconds; it was {seconds_text(total)}.")
    if new_total < target:
        lines.append(
            f"That is {seconds_text(target - new_total)} seconds short of the {value:g} asked; "
            "the rest needs a new moment added to the list.")
    return lines


CHANGES = {
    "sound": change_sound, "canvas": change_canvas, "reorder": change_reorder, "drop": change_drop,
    "shorter": change_shorter, "longer": change_longer}


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
