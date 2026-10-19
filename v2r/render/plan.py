"""The arithmetic that `check` and `render` share, so the two can never disagree about a cut list.

Everything here is pure: no files, no FFmpeg. A cut list that has passed `check` goes in; the whole of what will be
built (which frames of which working copy, which rectangle of each picture, where each shot sits on the reel) comes out.
Every setting is read when a function is called, never when the module is loaded, so tests can change one.
"""

import math
from fractions import Fraction

from v2r import settings


def frames(seconds, fps=None):
    """Whole frames in `seconds`: the nearest frame, half up (D-01), so 2.5 seconds is 75 frames every time.

    The product is rounded to six decimals first, which removes float noise such as 74.99999999999999.
    """
    fps = settings.OUTPUT_FPS if fps is None else fps
    return math.floor(round(seconds * fps, 6) + 0.5)


def clip_frames(seconds, fps=None):
    """The whole frames a working copy holds.

    A working copy's sound can run a few milliseconds past its last picture, and that must not invent a frame, so a
    clip gets a thousandth of a frame of benefit, not half a frame.
    """
    fps = settings.OUTPUT_FPS if fps is None else fps
    return math.floor(round(seconds * fps, 6) + 0.001)


def segment_frames(segment):
    """(first frame, number of frames) a segment covers on its working copy: frames [start, start + n)."""
    return frames(segment["from"]), frames(segment["to"] - segment["from"])


def seek(start_frame):
    """(pre, skip): the frame a shot's fast seek lands on, and how many frames the exact trim then skips.

    The fast seek only has to land somewhere before the first frame; the trim after it is what makes the start exact.
    """
    pre = max(0, start_frame - settings.RENDER_PRESEEK_FRAMES)
    return pre, start_frame - pre


def even(x):
    """The nearest even whole number, half up (never Python's round-half-to-even)."""
    return 2 * math.floor(Fraction(x) / 2 + Fraction(1, 2))


def even_floor(x):
    """The even whole number at or below `x`."""
    return 2 * math.floor(Fraction(x) / 2)


def clamp(x, low, high):
    return max(low, min(high, x))


def shape_of(canvas):
    """The settings.SHAPES name whose size equals the canvas's [width, height], or None."""
    for name, size in settings.SHAPES.items():
        if [size[0], size[1]] == list(canvas):
            return name
    return None


def fill_region(source_size, canvas_size, focus_x=0.5, focus_y=0.5):
    """The rectangle of the source that fills the canvas, cut around the focus point (D-05, the house rule).

    `source_size` and `canvas_size` are (width, height) in pixels. The picture is scaled until it just covers the
    canvas and the part that covers it is the region: a whole number of even pixels (the video format needs that), put
    so the focus point sits at the region's centre when it can, held inside the picture at its edges. On an axis the
    picture already fills, the region is the whole axis and the focus point moves nothing, silently.

    Returns {"crop": [width, height, x, y], "share": share of the picture kept (0 to 1), "focus": [fx, fy]} where
    `focus` is the focus point in canvas pixels once the region is scaled to the canvas.
    """
    source_w, source_h = source_size
    canvas_w, canvas_h = canvas_size
    scale = max(Fraction(canvas_w, source_w), Fraction(canvas_h, source_h))
    region_w, region_h = canvas_w / scale, canvas_h / scale
    crop_w = min(even_floor(source_w), even(region_w))
    crop_h = min(even_floor(source_h), even(region_h))
    focus_px_x, focus_px_y = Fraction(focus_x) * source_w, Fraction(focus_y) * source_h
    crop_x = even_floor(clamp(focus_px_x - Fraction(crop_w, 2), 0, source_w - crop_w))
    crop_y = even_floor(clamp(focus_px_y - Fraction(crop_h, 2), 0, source_h - crop_h))
    share = float(region_w * region_h / (source_w * source_h))
    focus = [
        float((focus_px_x - crop_x) * canvas_w / crop_w),
        float((focus_px_y - crop_y) * canvas_h / crop_h),
    ]
    return {"crop": [crop_w, crop_h, crop_x, crop_y], "share": share, "focus": focus}


def plan(cutlist, manifest):
    """What `render` will build, for a cut list that has passed `check`; segments stay in the list's order (D-13).

    Returns {"shape", "canvas", "fps", "segments": [...], "total_frames", "seconds", "sound_block"}. Each segment
    holds `number` (1-based), `clip`, `kind`, `working` (the working copy's file name), `photo` (the full-size copy's
    file name, or None), `source_size`, `start_frame`, `frames`, `reel_start`, `crop`, `share`, `focus`, `move`,
    `window_start`, `window_end` (canvas rectangles [x, y, w, h]; a move is added by a later plan), `sound`
    ("keep" or "off") and `touch_up` (the list's record for the clip, or None).
    """
    canvas = [cutlist["canvas"]["width"], cutlist["canvas"]["height"]]
    fps = settings.OUTPUT_FPS
    entries = {entry["letter"]: entry for entry in manifest["clips"]}
    touch_ups = (cutlist.get("look") or {}).get("touch_up") or {}
    segments = []
    reel_start = 0
    for number, segment in enumerate(cutlist["segments"], start=1):
        entry = entries[segment["clip"]]
        working = entry["working"]
        start, count = segment_frames(segment)
        size = tuple(working["size"])
        region = fill_region(size, canvas, segment.get("focus_x", 0.5), segment.get("focus_y", 0.5))
        segments.append({
            "number": number,
            "clip": segment["clip"],
            "kind": entry["kind"],
            "working": working["file"],
            "photo": (entry.get("photo") or {}).get("file"),
            "source_size": list(size),
            "start_frame": start,
            "frames": count,
            "reel_start": reel_start,
            "crop": region["crop"],
            "share": region["share"],
            "focus": region["focus"],
            "move": segment.get("move", "none"),
            "window_start": [0, 0, canvas[0], canvas[1]],
            "window_end": [0, 0, canvas[0], canvas[1]],
            "sound": segment["sound"],
            "touch_up": touch_ups.get(segment["clip"]),
        })
        reel_start += count
    return {
        "shape": shape_of(canvas),
        "canvas": canvas,
        "fps": fps,
        "segments": segments,
        "total_frames": reel_start,
        "seconds": reel_start / fps,
        "sound_block": cutlist.get("sound") or {},
    }
