"""Stills and contact sheets: frames pulled from a working copy through one FFmpeg pipe and laid out with Pillow.

Pillow is imported only inside `pillow_modules`, so measuring keeps working on a computer where it failed to install.
"""

import os
import subprocess
from pathlib import Path

from v2r import normalize, settings


def label(letter, t):
    """The words printed on a still: its clip letter and time, such as "A 03.0" or "B 07.5" (D-02)."""
    return f"{letter} {t:04.1f}"


NO_PICTURE_LIBRARY = (
    "The picture library (Pillow) is not installed, so no contact sheets were made; the measurements are in look.json.")
NO_SCALABLE_FONT = "Pillow here has no scalable font, so the labels on the sheets are small."


def pillow_modules():
    """Pillow's Image, ImageDraw, ImageFont and features modules; imported only now, as normalize does for photos,
    so measuring keeps working on a computer where Pillow failed to install. ImportError means it is missing."""
    from PIL import Image, ImageDraw, ImageFont, features

    return Image, ImageDraw, ImageFont, features


def picture_problem():
    """One sentence saying why sheets cannot be drawn on this computer (no Pillow), or None when they can."""
    try:
        pillow_modules()
    except ImportError:
        return NO_PICTURE_LIBRARY
    return None


def filter_problem(have):
    """One sentence saying which FFmpeg filter the stills need that this computer lacks, or None.

    `have` is the set of filter names FFmpeg lists. The stills need `select` to pick frames and `scale` to shrink them.
    """
    for name in ("select", "scale"):
        if name not in have:
            return (
                f"This computer's FFmpeg lacks the {name} filter, so no contact sheets were made; "
                "the measurements are in look.json.")
    return None


def font_problem():
    """The sentence to print when Pillow has no scalable font (labels then use its small built-in one), else None."""
    _, _, _, features = pillow_modules()
    return None if features.check("freetype2") else NO_SCALABLE_FONT


def label_font(cell_w):
    """The font labels are drawn in: sized by the cell when Pillow can scale a font, else Pillow's small built-in one."""
    _, _, ImageFont, features = pillow_modules()
    if features.check("freetype2"):
        return ImageFont.load_default(size=round(cell_w * settings.LABEL_FONT_SHARE))
    return ImageFont.load_default()  # a bitmap font: it has one size and does not take a size


def cell_size(orientation):
    """(width, height) in pixels of one cell on a sheet of this orientation, from the grid and the cell proportion."""
    columns, _ = settings.SHEET_GRID[orientation]
    width = (settings.SHEET_WIDTH - (columns + 1) * settings.SHEET_PADDING) // columns
    aspect_width, aspect_height = settings.CELL_ASPECT[orientation]
    return width, round(width * aspect_height / aspect_width)


def sheet_height(orientation):
    """Pixels high a sheet of this orientation is: every row of the grid, filled or not."""
    _, rows = settings.SHEET_GRID[orientation]
    return settings.SHEET_PADDING + rows * (cell_size(orientation)[1] + settings.SHEET_PADDING)


def fit_size(width, height, cell_w, cell_h):
    """The largest (width, height) with the picture's proportions that fits in the cell; each side even, at least 2."""
    if cell_w * height <= cell_h * width:  # the width is what limits it
        fitted_w, fitted_h = cell_w, cell_w * height // width
    else:
        fitted_w, fitted_h = cell_h * width // height, cell_h
    return max(2, fitted_w // 2 * 2), max(2, fitted_h // 2 * 2)


def grab_stills(path, frame_numbers, size, seconds):
    """The pictures at `frame_numbers` of a working copy, each scaled to `size`, as Pillow RGB images.

    One FFmpeg run reads them all (a `select` filter and a raw pipe). The images come back in the order asked for;
    a frame number given twice is read once. Raises ValueError when FFmpeg gave a different number of pictures than
    were asked for, and subprocess.CalledProcessError or TimeoutExpired when FFmpeg failed.
    """
    Image = pillow_modules()[0]

    wanted = sorted(set(frame_numbers))
    if not wanted:
        return []
    width, height = size
    chooser = "+".join(f"eq(n,{number})" for number in wanted)
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin",
        "-i", str(Path(path).resolve()),
        "-an", "-vf", f"select='{chooser}',scale={width}:{height}:flags=area",
        "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
    ]
    data = subprocess.run(
        command, capture_output=True, check=True, timeout=normalize.ffmpeg_timeout(seconds)).stdout
    frame_bytes = width * height * 3
    if len(data) != frame_bytes * len(wanted):
        raise ValueError("wrong number of stills")
    pictures = {
        number: Image.frombytes("RGB", (width, height), data[index * frame_bytes:(index + 1) * frame_bytes])
        for index, number in enumerate(wanted)
    }
    return [pictures[number] for number in frame_numbers]


class SheetBook:
    """The contact sheets of one look run, filled in order, one still after another.

    A sheet follows the grid of its stills' orientation; a still of another orientation starts a new sheet.
    Every sheet touched is saved whole (a temporary name, then renamed), so a reader never finds half a sheet.
    """

    def __init__(self, work_dir):
        self.folder = Path(work_dir) / "sheets"
        self.count = 0  # sheets started so far
        self.current = None  # the sheet being filled: {"image", "orientation", "number", "used"}
        self.full = False  # true once a still needed a sheet beyond MAX_SHEETS_PER_RUN; nothing after it is placed

    def names(self):
        """The sheet names made so far, in order, relative to the work folder, such as "sheets/sheet-01.jpg"."""
        return [self.name(number) for number in range(1, self.count + 1)]

    @staticmethod
    def name(number):
        return f"sheets/sheet-{number:02d}.jpg"

    def start_sheet(self, orientation):
        Image = pillow_modules()[0]
        self.count += 1
        size = (settings.SHEET_WIDTH, sheet_height(orientation))
        self.current = {
            "image": Image.new("RGB", size, settings.SHEET_BACKGROUND),
            "orientation": orientation,
            "number": self.count,
            "used": 0,
        }

    def save_current(self):
        """Write the sheet being filled to its file, whole or not at all.

        A sheet larger than SHEET_MAX_BYTES is saved again SHEET_JPEG_QUALITY_STEP quality points lower, down to
        SHEET_JPEG_QUALITY_MIN; the last save is kept whatever its size, so a sheet is never lost for being large.
        """
        self.folder.mkdir(exist_ok=True)
        final = self.folder / f"sheet-{self.current['number']:02d}.jpg"
        part = final.with_name(f"{final.stem}.part.jpg")
        quality = settings.SHEET_JPEG_QUALITY
        while True:
            self.current["image"].save(part, "JPEG", quality=quality)
            if part.stat().st_size <= settings.SHEET_MAX_BYTES or quality <= settings.SHEET_JPEG_QUALITY_MIN:
                break
            quality = max(settings.SHEET_JPEG_QUALITY_MIN, quality - settings.SHEET_JPEG_QUALITY_STEP)
        os.replace(part, final)

    def add(self, stills, orientation):
        """Put `stills`, a list of (image, label) pairs, on the sheets in order.

        Returns one record per still: {"sheet": "sheets/sheet-NN.jpg", "cell": 1-based place on the sheet,
        "box": [left, top, right, bottom] of the picture on the sheet, in pixels}.
        Never starts a sheet beyond MAX_SHEETS_PER_RUN: from the first still that would need one, `full` is true and
        that still and every one after it gets {"sheet": None, "cell": None, "box": None}.
        """
        ImageDraw = pillow_modules()[1]
        columns, rows = settings.SHEET_GRID[orientation]
        cell_w, cell_h = cell_size(orientation)
        font = label_font(cell_w)
        records = []
        touched_last = False
        for picture, text in stills:
            if self.full:
                records.append({"sheet": None, "cell": None, "box": None})
                continue
            if self.current is None or self.current["orientation"] != orientation or self.current["used"] >= columns * rows:
                if self.count >= settings.MAX_SHEETS_PER_RUN:
                    self.full = True
                    records.append({"sheet": None, "cell": None, "box": None})
                    continue
                if touched_last:
                    self.save_current()
                self.start_sheet(orientation)
            slot = self.current["used"]
            self.current["used"] += 1
            touched_last = True
            left = settings.SHEET_PADDING + (slot % columns) * (cell_w + settings.SHEET_PADDING)
            top = settings.SHEET_PADDING + (slot // columns) * (cell_h + settings.SHEET_PADDING)
            left += (cell_w - picture.width) // 2
            top += (cell_h - picture.height) // 2
            sheet = self.current["image"]
            sheet.paste(picture, (left, top))
            draw = ImageDraw.Draw(sheet)
            box_left, box_top, box_right, box_bottom = draw.textbbox((0, 0), text, font=font)
            pad = settings.LABEL_PADDING
            draw.rectangle(
                (left, top, left + (box_right - box_left) + 2 * pad, top + (box_bottom - box_top) + 2 * pad),
                fill=settings.LABEL_BOX_COLOUR)
            draw.text((left + pad - box_left, top + pad - box_top), text, font=font, fill=settings.LABEL_TEXT_COLOUR)
            records.append({
                "sheet": self.name(self.current["number"]),
                "cell": slot + 1,
                "box": [left, top, left + picture.width, top + picture.height],
            })
        if touched_last:
            self.save_current()
        return records
