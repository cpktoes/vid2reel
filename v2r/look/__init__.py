"""`v2r look`: measure the working copies and make contact sheets of stills. It reports; it never chooses.

Look measures and shows. It does not say which clip, moment or still belongs in a reel (decision D-04): look.json and
the sheets carry measurements, stills and facts only. Choosing is the chat's Claude's job, following the handbook.

look.json is what Stages 16 and 17 read; these names are frozen (decision D-03): names are added, never renamed.
It is written whole or not at all (look.json.tmp, then renamed), once at the start and again after every clip.
Any value may be null when it could not be measured; it is never NaN or infinity.
Top level: `version` (1), `shape` ("tall" or "wide", from the manifest), `finished` (false until the last clip is
done), `stopped` (null, or the sentence of a run that stopped as a whole), `rhythm` (seconds between base stills this
run), `rhythm_thinned` (true when the run thinned the rhythm to stay within the sheet cap), `missing` (sentences naming
what this computer could not measure or draw: a missing filter, no picture library, no scalable font), `sheets` (sheet
file names relative to the work folder, in the order filled, such as "sheets/sheet-01.jpg") and `clips` (one entry per
manifest entry, in letter order; letters and numbers are the manifest's, never recounted).
Each clip: `letter`, `number`, `status` ("done" or "skipped"), `kind` ("video", "photo" or null). A skipped entry adds
`sentence` and nothing more. A done entry adds `file` (the working copy's name, such as "A.mp4"), `seconds`,
`orientation` ("tall" or "wide": the shape of its stills, which follows its working copy), `look_seconds` (seconds
look spent on it), `overall`, `halves`, `shot_changes`, `stills`, `candidates` and `notes` (fixed sentences about
anything that could not be made).
`overall` (the whole clip): `brightness`, `brightness_low`, `brightness_high`, `blue_shift`, `red_shift`, `saturation`.
Each `halves` entry (one for every half second from t = 0.0): `t` (seconds), `movement`, `camera`, `shake`,
`camera_state` ("still", "panning", "shaky" or null), `subject`, `blur`, `sharp`, `brightness`, `loudness` and
`shot_change`.
`shot_changes`: the seconds where a new shot starts, or null when not measured.
Each `stills` entry: `label` (such as "A 03.0": the letter and the time, written on the still), `t` (seconds), `why`
("rhythm", "movement", "shot change" or "sound"), `sheet` (such as "sheets/sheet-01.jpg"; null when its picture could
not be taken), `cell` (1-based place on the sheet, left to right then top to bottom) and `box` ([left, top, right,
bottom] of the still on its sheet, in pixels).
Each `candidates` entry: `rank`, `start`, `end` (seconds), `reason` (facts in words) and `stills` (their labels).
Units: brightness in 8-bit code values (16 is black, 235 is white); movement as the mean frame difference, 0-255,
between analysed frames; camera and shake in pixels per analysed frame at LOOK_WIDTH; blur as edge width in pixels
(lower is sharper); loudness in LUFS; times in seconds. Every number is rounded to LOOK_DECIMALS places.
"""

import errno
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from v2r import WORK_DIR, doctor, settings
from v2r.look import measure, pick, sheets

NO_MANIFEST = "There is no manifest.json in the work folder yet, so normalize has to run before look."
UNREADABLE_MANIFEST = "The work folder's manifest.json could not be read, so nothing was looked at."
NO_FFMPEG = "FFmpeg is not installed here, so nothing was looked at."
OUT_OF_ROOM = "The work folder ran out of room, so look stopped; the clips looked at so far are in look.json."
LAST_LOOK_SHEETS = re.compile(r"^sheet-\d+(\.part)?\.jpg$")  # the last run's sheets, and only those
LETTER = re.compile(r"^[A-Z]{1,3}$")  # what normalize's letters look like


class LookError(Exception):
    """The whole run can't go on; the message is one plain sentence."""


def write_look(work_dir, look):
    """Write look.json whole or not at all, so a reader never sees half a file. NaN and infinity are refused."""
    work_dir = Path(work_dir)
    temp = work_dir / "look.json.tmp"
    temp.write_text(json.dumps(look, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    os.replace(temp, work_dir / "look.json")


def clear_last_look(work_dir):
    """Delete the last run's look.json, look.json.tmp and sheets/sheet-NN.jpg files; nothing else, ever (D-08)."""
    work_dir = Path(work_dir)
    for name in ("look.json", "look.json.tmp"):
        leftover = work_dir / name
        if leftover.is_file():
            leftover.unlink()
    sheets_folder = work_dir / "sheets"
    if sheets_folder.is_dir():
        for entry in sheets_folder.iterdir():
            if LAST_LOOK_SHEETS.match(entry.name) and entry.is_file():
                entry.unlink()


def read_manifest(work_dir):
    """The work folder's manifest.json as a dictionary; LookError, in one sentence, when it is missing or unusable."""
    path = Path(work_dir) / "manifest.json"
    if not path.is_file():
        raise LookError(NO_MANIFEST)
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:  # not valid JSON, or not text
        raise LookError(UNREADABLE_MANIFEST) from error
    clips = manifest.get("clips") if isinstance(manifest, dict) else None
    usable = (
        isinstance(clips, list)
        and manifest.get("shape") in settings.SHAPES
        and all(
            isinstance(clip, dict) and isinstance(clip.get("letter"), str) and LETTER.match(clip["letter"])
            and isinstance(clip.get("number"), int) for clip in clips)
    )
    if not usable:
        raise LookError(UNREADABLE_MANIFEST)
    return manifest


def plural(count, word):
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def thinned_sentence(interval):
    """The one sentence a run prints when it takes its stills further apart to stay within the sheet cap."""
    def seconds(number):
        return "second" if number == 1 else f"{number:g} seconds"

    return (
        f"There are too many stills for {settings.MAX_SHEETS_PER_RUN} sheets, so a still is taken every "
        f"{seconds(interval)} instead of every {seconds(settings.STILL_INTERVAL_STEPS[0])}.")


def skipped_entry(entry, sentence):
    """The look.json entry of a clip that was not looked at; it keeps the manifest's letter and number (D-06)."""
    return {
        "letter": entry["letter"],
        "number": entry["number"],
        "status": "skipped",
        "kind": None,
        "sentence": sentence,
    }


def working_facts(entry, work_dir):
    """(path, seconds, fps, size) of an entry's working copy, or a skipped sentence string when it can't be used.

    The manifest's `working.file` must be a plain file name of a file directly inside the work folder (T-3-01);
    only working copies are ever read, never the originals.
    """
    letter = entry["letter"]
    working = entry.get("working")
    not_found = f"The working copy of clip {letter} is missing or not in the work folder, so it was not looked at."
    could_not = f"Clip {letter} could not be looked at."
    if not isinstance(working, dict):
        return not_found
    name = working.get("file")
    if not isinstance(name, str) or not name or name.startswith(".") or Path(name).name != name:
        return not_found
    folder = Path(work_dir).resolve()
    path = folder / name
    if not path.is_file() or path.resolve().parent != folder:
        return not_found
    seconds, fps, size = measure.finite(working.get("seconds")), measure.finite(working.get("fps")), working.get("size")
    sizes_ok = (
        isinstance(size, list) and len(size) == 2
        and all(isinstance(side, int) and not isinstance(side, bool) and side > 0 for side in size))
    if not seconds or seconds <= 0 or not fps or fps <= 0 or not sizes_ok:
        return could_not
    return path, seconds, fps, size


def look_at_clip(entry, facts, shape, rhythm, have, book, picture_problem):
    """Measure one done clip and put its stills on the sheets; returns its look.json entry, or a skipped one."""
    path, seconds, fps, size = facts
    letter = entry["letter"]
    orientation = pick.orientation(size, shape)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="v2r-look-") as folder:
        measured = measure.measure_clip(path, entry, have, folder)
    # A photo is one still, labelled 00.0 (D-14); a video gets the base rhythm.
    times = [0.0] if entry["kind"] == "photo" else pick.base_times(seconds, fps, rhythm)
    numbers = [pick.frame_number(t, fps, seconds) for t in times]
    times = [number / fps for number in numbers]  # the time of the working copy's own frame
    labels = [sheets.label(letter, t) for t in times]
    notes = list(measured["notes"])
    records = [{"sheet": None, "cell": None, "box": None} for _ in times]
    taken = False
    if picture_problem is None and book.full:
        taken = True  # the sheet cap was reached by an earlier clip: its stills are listed, but not drawn
    elif picture_problem is None:
        cell_w, cell_h = sheets.cell_size(orientation)
        fitted = sheets.fit_size(size[0], size[1], cell_w, cell_h)
        try:
            pictures = sheets.grab_stills(path, numbers, fitted, seconds)
            records = book.add(list(zip(pictures, labels)), orientation)
            taken = True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError):
            pass
    if not taken:
        if measured["notes"]:  # neither the measurements nor the stills could be made
            return skipped_entry(entry, f"Clip {letter} could not be looked at.")
        notes.append(f"The stills of clip {letter} could not be taken, so it is not on the sheets.")
    stills = [
        {"label": text, "t": measure.rounded(t), "why": "rhythm", **record}
        for text, t, record in zip(labels, times, records)
    ]
    return {
        "letter": letter,
        "number": entry["number"],
        "status": "done",
        "kind": entry["kind"],
        "file": path.name,
        "seconds": measure.rounded(seconds),
        "orientation": orientation,
        "look_seconds": measure.rounded(time.monotonic() - started),
        "overall": measured["overall"],
        "halves": measured["halves"],
        "shot_changes": measured["shot_changes"],
        "stills": stills,
        "notes": notes,
    }


def look(work_dir=None):
    """Look at every working copy listed in `work_dir`'s manifest.json (the repo's work/ when not given).

    Writes look.json and the contact sheets in `work_dir` and returns the look.json dictionary. A clip that can't
    be looked at is skipped with one sentence and the others carry on; only a run that can't go on at all (no
    manifest, no FFmpeg, no room) raises LookError, and it deletes nothing when it cannot start.
    """
    work_dir = Path(WORK_DIR if work_dir is None else work_dir)
    manifest = read_manifest(work_dir)
    if shutil.which("ffmpeg") is None:
        raise LookError(NO_FFMPEG)
    clear_last_look(work_dir)  # a new run replaces the last one (D-08)
    have = doctor.ffmpeg_names("-filters")  # asked once per run
    missing = measure.missing_measurements(have)
    problem = sheets.picture_problem() or sheets.filter_problem(have)  # why no sheets can be made, if so
    if problem:
        missing.append(problem)
    else:
        font_sentence = sheets.font_problem()  # sheets are still drawn, with a small built-in font
        if font_sentence:
            missing.append(font_sentence)
    interval, thinned = settings.STILL_INTERVAL_STEPS[0], False
    if problem is None:  # the rhythm only needs thinning when sheets are going to be made
        interval, thinned = pick.run_interval(manifest["clips"], manifest["shape"])
    if thinned:
        missing.append(thinned_sentence(interval))
    for sentence in missing:
        print(sentence, flush=True)

    result = {
        "version": 1,
        "shape": manifest["shape"],
        "finished": False,
        "stopped": None,
        "rhythm": interval,
        "rhythm_thinned": thinned,
        "missing": missing,
        "sheets": [],
        "clips": [],
    }
    write_look(work_dir, result)
    book = sheets.SheetBook(work_dir)
    said_full = False
    try:
        for entry in manifest["clips"]:
            letter = entry["letter"]
            try:
                if entry.get("status") != "done" or entry.get("kind") not in ("video", "photo"):
                    clip = skipped_entry(
                        entry, f"Clip {letter} was skipped when the clips were converted, so it has no stills.")
                else:
                    facts = working_facts(entry, work_dir)
                    if isinstance(facts, str):
                        clip = skipped_entry(entry, facts)
                    else:
                        clip = look_at_clip(entry, facts, result["shape"], result["rhythm"], have, book, problem)
            except OSError as error:
                if error.errno == errno.ENOSPC:
                    raise
                clip = skipped_entry(entry, f"Clip {letter} could not be looked at.")
            except Exception:  # one broad catch at the per-clip boundary: nothing may stop the others
                clip = skipped_entry(entry, f"Clip {letter} could not be looked at.")
            result["clips"].append(clip)
            result["sheets"] = book.names()
            if book.full and not said_full:
                said_full = True
                sentence = (
                    f"Even with fewer stills the run needs more than {settings.MAX_SHEETS_PER_RUN} sheets, so the "
                    f"stills from clip {letter} on are listed in look.json but not on a sheet.")
                missing.append(sentence)
                print(sentence, flush=True)
            write_look(work_dir, result)
            if clip["status"] == "skipped":
                print(clip["sentence"], flush=True)
            else:
                print(
                    f"{letter} looked at in {round(clip['look_seconds'])} s, "
                    f"{plural(len(result['sheets']), 'sheet')} so far", flush=True)
    except OSError as error:
        if error.errno != errno.ENOSPC:
            raise
        result["stopped"] = OUT_OF_ROOM
        try:
            write_look(work_dir, result)
        except OSError:
            pass
        raise LookError(OUT_OF_ROOM) from error

    result["finished"] = True
    write_look(work_dir, result)
    done = sum(1 for clip in result["clips"] if clip["status"] == "done")
    print(
        f"{done} of {len(manifest['clips'])} clips looked at; the sheets are in {work_dir / 'sheets'} "
        f"and the measurements in {work_dir / 'look.json'}.", flush=True)
    return result
