"""When look takes its stills: the base rhythm and the frame each time points at. Pure functions, no files."""

import math

from v2r import settings


def frame_number(t, fps, seconds):
    """The frame of a clip nearest to time `t`: round(t x fps), held between the first and the last frame.

    `seconds` is the clip's length, so a time at or past the end gives the last frame instead of one that is not there.
    """
    last = round(seconds * fps) - 1
    return max(0, min(round(t * fps), last))


def base_times(seconds, fps, interval):
    """The times of the base stills: 0, interval, 2 x interval ... up to the last frame's time; never empty."""
    last_time = (round(seconds * fps) - 1) / fps
    times = []
    step = 0
    while step * interval <= last_time + 1e-9:
        times.append(round(step * interval, 3))  # rounded so repeated additions can't drift off 1.5, 3.0 ...
        step += 1
    return times or [0.0]


def orientation(size, shape):
    """"tall" or "wide": the shape of a clip's stills, from its working size; a square follows the job's shape.

    The one rule for this, used both by the sheets and by the up-front count of how many sheets a run needs.
    """
    width, height = size
    if height > width:
        return "tall"
    if width > height:
        return "wide"
    return shape


def extras_allowance(base_count):
    """The most extra stills a clip with `base_count` base stills may add (D-17): a share of the base, rounded down."""
    return math.floor(base_count * settings.EXTRAS_SHARE + 1e-9)


def still_plan(clips, shape, interval):
    """[(orientation, most stills)] for every usable done clip of a manifest, in letter order, at this rhythm.

    A photo is one still and has no allowance; a video has its base stills plus its full allowance of extras.
    Entries that were skipped, or whose facts can't be used, count nothing.
    """
    plan = []
    for clip in clips:
        working = clip.get("working") if clip.get("status") == "done" else None
        if not isinstance(working, dict) or clip.get("kind") not in ("video", "photo"):
            continue
        seconds, fps, size = working.get("seconds"), working.get("fps"), working.get("size")
        if not (isinstance(size, list) and len(size) == 2 and all(isinstance(side, int) and side > 0 for side in size)):
            continue
        if clip["kind"] == "photo":
            plan.append((orientation(size, shape), 1))
            continue
        usable = all(
            isinstance(number, (int, float)) and not isinstance(number, bool) and math.isfinite(number) and number > 0
            for number in (seconds, fps))
        if not usable:
            continue
        base = len(base_times(seconds, fps, interval))
        plan.append((orientation(size, shape), base + extras_allowance(base)))
    return plan


def sheets_needed(plan):
    """How many sheets `still_plan`'s stills fill, laid out in order with a new sheet at every change of orientation."""
    count = 0
    current, used = None, 0
    for kind, stills in plan:
        columns, rows = settings.SHEET_GRID[kind]
        for _ in range(stills):
            if kind != current or used >= columns * rows:
                count += 1
                current, used = kind, 0
            used += 1
    return count


def run_interval(clips, shape):
    """(seconds between base stills, whether it was thinned) for a run, decided before anything is measured (D-16).

    Tries STILL_INTERVAL_STEPS in turn and keeps the first at which every clip's base stills and its full extras
    allowance fit in MAX_SHEETS_PER_RUN sheets. When none does, the last step is used and the run is thinned all the
    same; the sheets themselves stop at the cap.
    """
    steps = settings.STILL_INTERVAL_STEPS
    for index, interval in enumerate(steps):
        if sheets_needed(still_plan(clips, shape, interval)) <= settings.MAX_SHEETS_PER_RUN:
            return interval, index > 0
    return steps[-1], len(steps) > 1
