"""`v2r look`: measure the working copies and make contact sheets of stills. It reports; it never chooses.

Look measures and shows. It does not say which clip, moment or still belongs in a reel (decision D-04): look.json and
the sheets carry measurements, stills and facts only. Choosing is the chat's Claude's job, following the handbook.

look.json is what Stages 16 and 17 read; these names are frozen (decision D-03). It is written whole or not at all
(look.json.tmp, then renamed), once at the start and again after every clip.
Top level: `version` (1), `shape` (from the manifest), `finished`, `stopped`, `rhythm`, `rhythm_thinned`, `missing`,
`sheets` and `clips`.
Each done clip: `letter`, `number`, `status`, `kind`, `file`, `seconds`, `orientation`, `look_seconds`, `overall`,
`halves`, `shot_changes`, `stills` and `notes`.
Each half: `t`, `movement` and `brightness`. Each still: `label`, `t`, `why`, `sheet`, `cell` and `box`.
`overall` holds `brightness`.
"""

import json
import os
import shutil
import tempfile
import time
from pathlib import Path

from v2r import WORK_DIR, doctor, settings
from v2r.look import measure, pick, sheets

NO_FFMPEG = "FFmpeg is not installed here, so nothing was looked at."


class LookError(Exception):
    """The whole run can't go on; the message is one plain sentence."""


def write_look(work_dir, look):
    """Write look.json whole or not at all, so a reader never sees half a file. NaN and infinity are refused."""
    work_dir = Path(work_dir)
    temp = work_dir / "look.json.tmp"
    temp.write_text(json.dumps(look, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    os.replace(temp, work_dir / "look.json")


def orientation_of(size, shape):
    """"tall" or "wide": the shape of a clip's stills, from its working size; a square follows the job's shape."""
    width, height = size
    if height > width:
        return "tall"
    if width > height:
        return "wide"
    return shape


def plural(count, word):
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def look_at_clip(entry, work_dir, shape, rhythm, have, book):
    """Measure one done video clip and put its stills on the sheets; returns its look.json entry."""
    working = entry["working"]
    path = Path(work_dir) / working["file"]
    seconds, fps = working["seconds"], working["fps"]
    orientation = orientation_of(working["size"], shape)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="v2r-look-") as folder:
        measured = measure.measure_clip(path, entry, have, folder)
    numbers = [pick.frame_number(t, fps, seconds) for t in pick.base_times(seconds, fps, rhythm)]
    times = [number / fps for number in numbers]
    labels = [sheets.label(entry["letter"], t) for t in times]
    cell_w, cell_h = sheets.cell_size(orientation)
    size = sheets.fit_size(working["size"][0], working["size"][1], cell_w, cell_h)
    pictures = sheets.grab_stills(path, numbers, size, seconds)
    records = book.add(list(zip(pictures, labels)), orientation)
    stills = [
        {"label": text, "t": measure.rounded(t), "why": "rhythm", **record}
        for text, t, record in zip(labels, times, records)
    ]
    return {
        "letter": entry["letter"],
        "number": entry["number"],
        "status": "done",
        "kind": entry["kind"],
        "file": working["file"],
        "seconds": measure.rounded(seconds),
        "orientation": orientation,
        "look_seconds": measure.rounded(time.monotonic() - started),
        "overall": measured["overall"],
        "halves": measured["halves"],
        "shot_changes": measured["shot_changes"],
        "stills": stills,
        "notes": measured["notes"],
    }


def look(work_dir=None):
    """Look at every working copy listed in `work_dir`'s manifest.json (the repo's work/ when not given).

    Writes look.json and the contact sheets in `work_dir` and returns the look.json dictionary.
    Only a run that can't go on at all raises LookError.
    """
    work_dir = Path(WORK_DIR if work_dir is None else work_dir)
    manifest = json.loads((work_dir / "manifest.json").read_text(encoding="utf-8"))
    if shutil.which("ffmpeg") is None:
        raise LookError(NO_FFMPEG)
    have = doctor.ffmpeg_names("-filters")  # asked once per run
    missing = measure.missing_measurements(have)
    problem = sheets.picture_problem()
    if problem:
        missing.append(problem)
    for sentence in missing:
        print(sentence, flush=True)

    result = {
        "version": 1,
        "shape": manifest["shape"],
        "finished": False,
        "stopped": None,
        "rhythm": settings.STILL_INTERVAL_STEPS[0],
        "rhythm_thinned": False,
        "missing": missing,
        "sheets": [],
        "clips": [],
    }
    write_look(work_dir, result)
    book = sheets.SheetBook(work_dir)
    for entry in manifest["clips"]:
        if entry["status"] != "done" or entry["kind"] != "video":
            continue
        started = time.monotonic()
        clip = look_at_clip(entry, work_dir, result["shape"], result["rhythm"], have, book)
        result["clips"].append(clip)
        result["sheets"] = book.names()
        write_look(work_dir, result)
        print(
            f"{clip['letter']} looked at in {round(time.monotonic() - started)} s, "
            f"{plural(len(result['sheets']), 'sheet')} so far", flush=True)

    result["finished"] = True
    write_look(work_dir, result)
    done = sum(1 for clip in result["clips"] if clip["status"] == "done")
    print(
        f"{done} of {len(manifest['clips'])} clips looked at; the sheets are in {work_dir / 'sheets'} "
        f"and the measurements in {work_dir / 'look.json'}.", flush=True)
    return result
