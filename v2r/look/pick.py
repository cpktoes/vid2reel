"""When look takes its stills: the base rhythm and the frame each time points at. Pure functions, no files."""

import math
import statistics

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


def spread(values, floor):
    """The median absolute deviation of the numbers in `values` (None leaves out), never below `floor`."""
    known = [value for value in values if value is not None]
    if not known:
        return floor
    middle = statistics.median(known)
    return max(statistics.median(abs(value - middle) for value in known), floor)


def peaks(values, floor):
    """[(index, score)] of the peaks in `values`, strongest first, earlier first when equal.

    A peak is a local maximum (not below a neighbour that has a value; of two equal neighbours the first counts, so
    a flat top is one peak) that stands at least PEAK_SPREADS spreads above the median of the numbers. The spread is
    never taken below `floor`, so a calm clip's flicker is never a peak. The score is how many spreads above the median.
    """
    known = [value for value in values if value is not None]
    if not known:
        return []
    middle = statistics.median(known)
    width = spread(values, floor)
    limit = middle + settings.PEAK_SPREADS * width
    found = []
    for index, value in enumerate(values):
        if value is None or value < limit:
            continue
        before = values[index - 1] if index > 0 else None
        after = values[index + 1] if index + 1 < len(values) else None
        if (before is not None and value <= before) or (after is not None and value < after):
            continue
        found.append((index, (value - middle) / width))
    found.sort(key=lambda peak: (-peak[1], peak[0]))
    return found


def movement_time(index, frames, middle):
    """Where the movement of the peak half second `index` is centred, in seconds.

    The middle of the analysed frames in that half and the halves either side, each weighted by how far its movement
    rises above `middle` (the clip's median); the first frame of a new shot counts for nothing. A frame's movement is
    the change since the frame before it, so it is placed half an analysed frame earlier than the frame's own time. When no frame rises
    above the median, the middle of the half.
    """
    per_half = round(settings.SUMMARY_SECONDS * settings.LOOK_FPS)
    total = weighted = 0.0
    for frame in frames:
        if frame.get("cut") or frame.get("movement") is None:
            continue
        if abs(round(frame["t"] * settings.LOOK_FPS) // per_half - index) > 1:
            continue
        weight = max(0.0, frame["movement"] - middle)
        total += weight
        weighted += weight * (frame["t"] - 0.5 / settings.LOOK_FPS)  # a frame's change happened before its time
    if total <= 0:
        return (index + 0.5) * settings.SUMMARY_SECONDS
    return weighted / total


def sound_time(index, sound):
    """The time of the loudest reading inside half second `index` (the earlier of equal ones); the half's middle if none."""
    start, end = index * settings.SUMMARY_SECONDS, (index + 1) * settings.SUMMARY_SECONDS
    inside = [r for r in sound if r.get("loudness") is not None and start - 1e-6 <= r["t"] < end - 1e-6]
    if not inside:
        return start + settings.SUMMARY_SECONDS / 2
    return min(inside, key=lambda reading: (-reading["loudness"], reading["t"]))["t"]


def extra_times(measured, base, seconds, fps):
    """The extra stills of a video clip as [{"t", "why"}] in time order: shot changes, movement and sound (D-01, D-17).

    `measured` is measure_clip's dictionary and `base` the times of the base stills. Shot changes come first (earlier
    first), then peaks of movement (only in half seconds where the camera is still, or in every one when the camera
    was not measured) and of loudness, strongest first (equal ones to the earlier time). An extra is kept only if it
    is at least EXTRA_MIN_GAP seconds, counted in whole frames, from every base still and every extra already kept,
    and a clip adds at most extras_allowance(len(base)) of them. Each `t` is the time of a real frame of the clip.
    """
    allowed = extras_allowance(len(base))
    halves = measured.get("halves") or []
    candidates = []  # (time, why), in the order they are tried
    for change in sorted(measured.get("shot_changes") or []):
        candidates.append((change + settings.CUT_STILL_DELAY, "shot change"))
    scored = []  # (score, time, why)
    if halves:
        measured_camera = any(half.get("camera_state") is not None for half in halves)
        movement = [
            half["movement"] if half.get("camera_state") == "still" or not measured_camera else None
            for half in halves]
        known = [value for value in movement if value is not None]
        if known:
            middle = statistics.median(known)
            for index, score in peaks(movement, settings.MOVEMENT_SPREAD_FLOOR):
                scored.append((score, movement_time(index, measured.get("frames") or [], middle), "movement"))
        sound = measured.get("sound") or []
        if sound:
            loudness = [settings.SILENCE_LUFS if half.get("loudness") is None else half["loudness"] for half in halves]
            for index, score in peaks(loudness, settings.LOUDNESS_SPREAD_FLOOR):
                scored.append((score, sound_time(index, sound), "sound"))
    scored.sort(key=lambda item: (-item[0], item[1]))
    candidates += [(time, why) for _, time, why in scored]

    gap = round(settings.EXTRA_MIN_GAP * fps)
    kept = [frame_number(t, fps, seconds) for t in base]  # frames of every still so far
    extras = []
    for time, why in candidates:
        if len(extras) >= allowed:
            break
        number = frame_number(time, fps, seconds)
        if all(abs(number - other) >= gap for other in kept):
            kept.append(number)
            extras.append({"t": number / fps, "why": why})
    extras.sort(key=lambda extra: extra["t"])
    return extras
