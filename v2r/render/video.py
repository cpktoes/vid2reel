"""The picture half of `render`: the FFmpeg command for each shot's scratch piece, the list that joins the pieces, and
the one final encode.

Only numbers formatted by this code enter a filter string. File names reach FFmpeg only as separate arguments of an
argument list and are never given to a shell.
"""

from pathlib import Path

from v2r import settings
from v2r.render import plan

QUIET = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin"]


def perspective_filter(start, end, frames):
    """The slow move of a shot, drawn with FFmpeg's perspective filter; "" when there is nothing to move.

    `start` and `end` are the picture windows [left, top, width, height] in canvas pixels the shot begins and ends on.
    The four corners of the window are each one straight line in the frame number, from the start window's corner on
    the first frame to the end window's on the last, so the speed never changes (D-20). With sense=source the filter
    reads those four points of the picture and stretches them onto the four corners of the frame, which is the zoom.
    This is the only way a move is drawn: FFmpeg's zoom-and-pan filter and a moving crop both land on whole pixels and
    visibly tick by about two pixels a frame on a canvas-sized picture, while this draws between pixels. Its small
    constant sub-pixel offset (up to 0.6 pixel) is the same on every frame and is left alone.
    A shot of one frame, or a move whose two windows are equal, gets no filter at all.
    """
    if frames <= 1 or list(start) == list(end):
        return ""
    corners = (
        (start[0], end[0], start[1], end[1]),  # top-left
        (start[0] + start[2], end[0] + end[2], start[1], end[1]),  # top-right
        (start[0], end[0], start[1] + start[3], end[1] + end[3]),  # bottom-left
        (start[0] + start[2], end[0] + end[2], start[1] + start[3], end[1] + end[3]),  # bottom-right
    )
    parts = []
    for index, (x_from, x_to, y_from, y_to) in enumerate(corners):
        for axis, first, last in (("x", x_from, x_to), ("y", y_from, y_to)):
            parts.append(f"{axis}{index}='({first:.6f}+({last - first:.6f})*in/{frames - 1})'")
    return "perspective=" + ":".join(parts) + ":sense=source:eval=frame:interpolation=cubic"


def touch_up_filter(record):
    """The one colour step of render: the list's touch-up numbers as exact code-value arithmetic; "" for none.

    `record` is the list's touch-up for the clip (brightness, blue and red offsets in 8-bit code values, saturation as
    a multiplier), or None. A missing record, or one whose numbers are all neutral (0, 0, 0 and 1), builds no colour
    filter at all, so the shot's colour is its working copy's own (CUT-05).
    Brightness is added to Y. Each colour channel keeps its distance from the format's neutral value times the
    saturation, plus its offset; the neutral value is the pivot of the multiply, never a target (D-24). The explicit
    round() and limits are required: a bare lutyuv truncates (181.96 became 181) and its own limits depend on the
    range the frame is tagged with. Only numbers formatted here enter the string (T-4-01).
    """
    if not record:
        return ""
    brightness, blue, red, saturation = (
        float(record["brightness"]), float(record["blue"]), float(record["red"]), float(record["saturation"]))
    if (brightness, blue, red, saturation) == (0.0, 0.0, 0.0, 1.0):
        return ""
    luma_low, luma_high = settings.LUMA_RANGE
    chroma_low, chroma_high = settings.CHROMA_RANGE
    neutral = settings.CHROMA_NEUTRAL

    def colour(offset):
        return (f"clip(round({neutral}+(val-{neutral})*{saturation:.6f}+({offset:.6f})),{chroma_low},{chroma_high})")

    return (
        f"lutyuv=y='clip(round(val+({brightness:.6f})),{luma_low},{luma_high})':"
        f"u='{colour(blue)}':v='{colour(red)}'"
    )


FINISH = "format=yuv420p,setparams=range=tv:colorspace=bt709:color_primaries=bt709:color_trc=bt709[v]"


def video_chain(segment, the_plan):
    """The filter chain that turns one shot into exactly its frames, filling the canvas, in the label [v].

    A shot from a working copy: exact frames (the trim counts frames, not seconds), then the region around the focus
    point cut in whole even pixels, then scaled to the canvas, then the slow move if the list named one.
    A photo (D-21): the region is cut from the full-size upright picture, scaled to the canvas once, and that one
    frame is repeated for the length of the shot before the move, so a photo is as sharp as the picture allows. The
    JPEG is full range and needs the explicit conversion to the limited range of video.
    The touch-up adds its step here, in this one place: after the move, so the move's interpolation never mixes
    corrected and uncorrected values, and on the canvas-sized picture rather than the source.
    """
    canvas_w, canvas_h = the_plan["canvas"]
    crop_w, crop_h, crop_x, crop_y = segment["crop"]
    move = perspective_filter(segment["window_start"], segment["window_end"], segment["frames"])
    move = f"{move}," if move else ""
    touch_up = touch_up_filter(segment.get("touch_up"))
    steps = move + (f"{touch_up}," if touch_up else "")
    if segment["kind"] == "photo":
        return (
            f"[0:v]crop={crop_w}:{crop_h}:{crop_x}:{crop_y}:exact=1,"
            f"scale={canvas_w}:{canvas_h}:flags=bicubic+accurate_rnd:out_color_matrix=bt709:out_range=tv,"
            f"format=yuv420p,setsar=1,loop=loop={segment['frames'] - 1}:size=1:start=0,"
            f"setpts=N/({the_plan['fps']}*TB),{steps}{FINISH}"
        )
    _, skip = plan.seek(segment["start_frame"])
    end = skip + segment["frames"]
    return (
        f"[0:v]trim=start_frame={skip}:end_frame={end},setpts=N/({the_plan['fps']}*TB),"
        f"crop={crop_w}:{crop_h}:{crop_x}:{crop_y},"
        f"scale={canvas_w}:{canvas_h}:flags=bicubic+accurate_rnd,setsar=1,{steps}{FINISH}"
    )


def source_window(segment, the_plan):
    """The fast-seek time and the length to read for a shot, in seconds: a few frames more than it needs at each end."""
    fps = the_plan["fps"]
    pre, skip = plan.seek(segment["start_frame"])
    return pre / fps, (skip + segment["frames"] + settings.RENDER_TAIL_FRAMES) / fps


def photo_path(segment, work_dir):
    """The full-size copy of a photo shot: a plain file name directly in the work folder, else ValueError."""
    folder = Path(work_dir).resolve()
    name = segment["photo"]
    path = (folder / name).resolve() if isinstance(name, str) and name else None
    if path is None or path.parent != folder or Path(name).name != name:
        raise ValueError(f"The full-size copy of photo {segment['clip']} is missing from the work folder, so it cannot be built.")
    return path


def piece_command(segment, the_plan, work_dir, output):
    """The FFmpeg command that builds one shot's picture (no sound) into the scratch piece `output`."""
    if segment["kind"] == "photo":
        # -framerate: the image reader runs at 25 frames a second unless told, and would lose frames of a 30 fps shot
        source = ["-framerate", str(the_plan["fps"]), "-i", str(photo_path(segment, work_dir))]
        count = ["-frames:v", str(segment["frames"])]
    else:
        seek, length = source_window(segment, the_plan)
        source = ["-ss", f"{seek:.6f}", "-t", f"{length:.6f}", "-i", str(Path(work_dir).resolve() / segment["working"])]
        count = []
    return [
        *QUIET, "-y",
        *source,
        "-filter_complex", video_chain(segment, the_plan),
        "-map", "[v]", "-an", "-fps_mode", "passthrough", *count,
        "-c:v", "libx264", "-preset", settings.RENDER_PIECE_PRESET, "-crf", str(settings.RENDER_PIECE_CRF),
        "-pix_fmt", "yuv420p",
        str(output),
    ]


def concat_list(names):
    """The text of the list the concat demuxer reads: one line per piece, in order. `names` are plain file names."""
    return "".join(f"file '{name}'\n" for name in names)


def final_command(list_path, mix_path, fitted, gain_db, output, canvas=None):
    """The one command that joins the pieces, adds the sound and encodes the finished reel.

    `fitted` is the (width, height, bitrate) join.fit chose; when its size differs from `canvas` (the pieces' size) the
    picture is scaled to it.
    The frame-rate mode is passthrough, which never adds or drops a frame, so the reel holds exactly the planned frames.
    """
    width, height, bitrate = fitted
    graph = (
        f"[1:a]volume={gain_db:.2f}dB,aformat=sample_fmts=fltp:sample_rates={settings.AUDIO_RATE}:"
        "channel_layouts=stereo[a]"
    )
    video_map = "0:v"
    if canvas is not None and (width, height) != tuple(canvas):
        graph += f";[0:v]scale={width}:{height}:flags=bicubic+accurate_rnd,setsar=1[v]"
        video_map = "[v]"
    return [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
        "-f", "concat", "-i", str(list_path), "-i", str(mix_path),
        "-filter_complex", graph,
        "-map", video_map, "-map", "[a]", "-fps_mode", "passthrough",
        "-c:v", "libx264", "-preset", settings.RENDER_X264_PRESET, "-crf", str(settings.RENDER_X264_CRF),
        "-maxrate", str(bitrate), "-bufsize", str(bitrate), "-pix_fmt", "yuv420p",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
        "-c:a", "aac", "-b:a", str(settings.AUDIO_BITRATE), "-ar", str(settings.AUDIO_RATE), "-ac", "2",
        "-fflags", "+bitexact", "-flags:v", "+bitexact", "-flags:a", "+bitexact",  # no encoder name in the file
        "-map_metadata", "-1", "-map_chapters", "-1",  # no location or device tags
        "-movflags", "+faststart",  # index at the front, so playback starts immediately
        str(output),
    ]
