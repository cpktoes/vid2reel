"""The proof sheets: the first and the last picture of every shot of the finished reel, drawn with look's sheet code.

That is where a black frame or a crop onto a shoulder shows. Sheets go in their own folder, work/proof/, so look's
sheets are never touched.
"""

import os
import re
import subprocess
from pathlib import Path

from v2r import settings
from v2r.look import pick, sheets

FOLDER = "proof"
LAST_PROOF = re.compile(r"^proof-\d+(\.part)?\.jpg$")  # the last run's proof sheets, and only those
NO_PICTURE_LIBRARY = "The picture library (Pillow) is not installed, so no proof sheet was made."
NOT_MADE = "The proof sheets could not be made, so the reel was kept without them."
NO_COVER_LIBRARY = "The picture library (Pillow) is not installed, so no cover still was made."
COVER_NOT_MADE = "The cover still could not be made, so the reel was kept without it."


def clear_last_proof(work_dir):
    """Delete the last run's proof sheets: regular files in proof/ whose whole name is proof-NN.jpg. Nothing else."""
    folder = Path(work_dir) / FOLDER
    if not folder.is_dir():
        return
    for entry in folder.iterdir():
        if LAST_PROOF.match(entry.name) and entry.is_file() and not entry.is_symlink():
            entry.unlink()


def make_proof(reel_path, the_plan, size, work_dir):
    """Make the proof sheets of a finished reel; returns (sheet names relative to the work folder, sentence or None).

    `size` is the reel's own (width, height). The sentence is set when no sheet could be made; the reel is kept.
    """
    if sheets.picture_problem():
        return [], NO_PICTURE_LIBRARY
    shape = the_plan["shape"]
    cell = sheets.fit_size(size[0], size[1], *sheets.cell_size(shape))
    numbers, labels = [], []
    fps = the_plan["fps"]
    for segment in the_plan["segments"]:
        first = segment["reel_start"]
        last = first + segment["frames"] - 1
        numbers += [first, last]
        labels += [f"{segment['number']} in {pick.clock(first / fps)}", f"{segment['number']} out {pick.clock(last / fps)}"]
    clear_last_proof(work_dir)
    book = sheets.SheetBook(work_dir, folder=FOLDER, stem="proof")
    try:
        stills = sheets.grab_stills(reel_path, numbers, cell, the_plan["seconds"])
        book.add(zip(stills, labels), shape)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError, OSError):
        return [], NOT_MADE
    return book.names(), None


def cover_path(reel_path):
    """Where a reel's cover still goes: beside the reel, named for it."""
    reel = Path(reel_path)
    return reel.with_name(f"{reel.stem}-cover.jpg")


def make_cover(reel_path, frame, size, cover, seconds=0):
    """Save frame number `frame` of a finished reel as a JPEG at `cover`, whole or not at all; returns None or a sentence.

    `size` is the reel's own (width, height), so the cover is the reel's frame size; `seconds` is the reel's length, which
    sets how long FFmpeg may take to read as far as the frame. The sentence is set when no cover
    could be made; the reel is kept.
    """
    if sheets.picture_problem():
        return NO_COVER_LIBRARY
    cover = Path(cover)
    part = cover.with_name(f"{cover.stem}.part.jpg")
    try:
        for image in sheets.grab_stills(reel_path, [frame], size, seconds):
            image.save(part, "JPEG", quality=settings.COVER_JPEG_QUALITY)
        os.replace(part, cover)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError, OSError):
        part.unlink(missing_ok=True)
        return COVER_NOT_MADE
    return None
