"""When look takes its stills: the base rhythm and the frame each time points at. Pure functions, no files."""


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
