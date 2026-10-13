"""`v2r join`: join video clips end to end into one tall or wide video in work/."""

import subprocess
from datetime import datetime

from v2r import WORK_DIR, settings

MIB = 1024 * 1024


class JoinError(Exception):
    """The join can't make a file that fits; the message says why in plain English."""


def join(videos, shape, out_dir=WORK_DIR):
    """Join `videos` in the order given into a new MP4 in `out_dir` that fits under settings.MAX_RESULT_BYTES.

    `shape` is "tall" or "wide" (see settings.SHAPES); there is deliberately no default.
    Returns the file's path and one plain sentence saying the size and quality used.
    """
    seconds = sum(duration(video) for video in videos)
    width, height, bitrate = fit(shape, seconds)  # raises JoinError before anything is built
    fps = settings.OUTPUT_FPS
    out_dir.mkdir(parents=True, exist_ok=True)
    output = new_path(out_dir, shape)

    inputs, graph = [], []
    for i, video in enumerate(videos):
        inputs += ["-i", str(video)]
        # FFmpeg has already turned upright and sideways clips the right way up (autorotate).
        # Scale each clip just big enough to cover the frame, then crop it from the centre.
        graph.append(
            f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},setsar=1,fps={fps}[v{i}]"
        )
    pairs = "".join(f"[v{i}][{i}:a]" for i in range(len(videos)))
    graph.append(f"{pairs}concat=n={len(videos)}:v=1:a=1[v][a]")

    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
        *inputs,
        "-filter_complex", ";".join(graph),
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",  # 8-bit 4:2:0 so every player can show it
        "-maxrate", str(bitrate), "-bufsize", str(bitrate),  # a ceiling that keeps the file under the limit
        "-c:a", "aac", "-b:a", str(settings.AUDIO_BITRATE),
        "-movflags", "+faststart",  # index at the front, so playback starts immediately
        str(output),
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        output.unlink(missing_ok=True)
        raise

    size = output.stat().st_size
    limit = settings.MAX_RESULT_BYTES / MIB
    if size > settings.MAX_RESULT_BYTES:
        output.unlink()
        raise JoinError(f"The video came out at {size / MIB:.1f} MiB, over the {limit:.0f} MiB limit, so it was deleted.")
    summary = (
        f"The video is {width}x{height} at an average of {size * 8 / seconds / 1e6:.1f} Mbit/s, "
        f"and the file is {size / MIB:.1f} MiB, under the {limit:.0f} MiB limit."
    )
    return output, summary


def fit(shape, seconds):
    """The largest frame size, and a video bitrate ceiling, that keep `seconds` of video under the limit."""
    budget = settings.MAX_RESULT_BYTES * 8 * (1 - settings.FIT_HEADROOM)  # bits
    # The encoder's buffer lets it run up to one second ahead of the ceiling, hence seconds + 1.
    bitrate = budget / (seconds + 1) - settings.AUDIO_BITRATE
    full_width, full_height = settings.SHAPES[shape]
    for scale, lowest in settings.FIT_STEPS:
        if bitrate >= lowest:
            return even(full_width * scale), even(full_height * scale), int(bitrate)
    longest = budget / (settings.FIT_STEPS[-1][1] + settings.AUDIO_BITRATE) - 1
    raise JoinError(
        f"A {shape} video can be at most {minutes(longest)} long to come back under the "
        f"{settings.MAX_RESULT_BYTES / MIB:.0f} MiB limit; these clips add up to {minutes(seconds)}, so nothing was built."
    )


def duration(video):
    """A video file's length in seconds."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
        stdout=subprocess.PIPE, text=True, check=True,
    ).stdout
    return float(out)


def even(x):
    return round(x / 2) * 2


def minutes(seconds):
    seconds = int(seconds)
    return f"{seconds} s" if seconds < 60 else f"{seconds // 60} min {seconds % 60} s"


def new_path(out_dir, shape):
    """A file name in `out_dir` that doesn't exist yet."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = out_dir / f"join-{shape}-{stamp}.mp4"
    n = 2
    while path.exists():
        path = out_dir / f"join-{shape}-{stamp}-{n}.mp4"
        n += 1
    return path
