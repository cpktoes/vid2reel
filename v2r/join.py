"""`v2r join`: join video clips end to end into one tall or wide video in work/."""

import subprocess
from datetime import datetime

from v2r import WORK_DIR, settings


def join(videos, shape, out_dir=WORK_DIR):
    """Join `videos` in the order given into a new MP4 in `out_dir` and return its path.

    `shape` is "tall" or "wide" (see settings.SHAPES); there is deliberately no default.
    """
    width, height = settings.SHAPES[shape]
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
        "-c:a", "aac",
        "-movflags", "+faststart",  # index at the front, so playback starts immediately
        str(output),
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        output.unlink(missing_ok=True)
        raise
    return output


def new_path(out_dir, shape):
    """A file name in `out_dir` that doesn't exist yet."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = out_dir / f"join-{shape}-{stamp}.mp4"
    n = 2
    while path.exists():
        path = out_dir / f"join-{shape}-{stamp}-{n}.mp4"
        n += 1
    return path
