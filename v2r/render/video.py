"""The picture half of `render`: the FFmpeg command for each shot's scratch piece, the list that joins the pieces, and
the one final encode.

Only numbers formatted by this code enter a filter string. File names reach FFmpeg only as separate arguments of an
argument list and are never given to a shell.
"""

from pathlib import Path

from v2r import settings
from v2r.render import plan

QUIET = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin"]


def video_chain(segment, the_plan):
    """The filter chain that turns one shot into exactly its frames, filling the canvas, in the label [v].

    Exact frames (the trim counts frames, not seconds), then the region around the focus point cut in whole even
    pixels, then scaled to the canvas. Plans for a move and for the touch-up add their steps here, in this one place.
    """
    canvas_w, canvas_h = the_plan["canvas"]
    crop_w, crop_h, crop_x, crop_y = segment["crop"]
    _, skip = plan.seek(segment["start_frame"])
    end = skip + segment["frames"]
    return (
        f"[0:v]trim=start_frame={skip}:end_frame={end},setpts=N/({the_plan['fps']}*TB),"
        f"crop={crop_w}:{crop_h}:{crop_x}:{crop_y},"
        f"scale={canvas_w}:{canvas_h}:flags=bicubic+accurate_rnd,setsar=1,format=yuv420p,"
        "setparams=range=tv:colorspace=bt709:color_primaries=bt709:color_trc=bt709[v]"
    )


def source_window(segment, the_plan):
    """The fast-seek time and the length to read for a shot, in seconds: a few frames more than it needs at each end."""
    fps = the_plan["fps"]
    pre, skip = plan.seek(segment["start_frame"])
    return pre / fps, (skip + segment["frames"] + settings.RENDER_TAIL_FRAMES) / fps


def piece_command(segment, the_plan, work_dir, output):
    """The FFmpeg command that builds one shot's picture (no sound) into the scratch piece `output`."""
    seek, length = source_window(segment, the_plan)
    source = Path(work_dir).resolve() / segment["working"]
    return [
        *QUIET, "-y",
        "-ss", f"{seek:.6f}", "-t", f"{length:.6f}", "-i", str(source),
        "-filter_complex", video_chain(segment, the_plan),
        "-map", "[v]", "-an", "-fps_mode", "passthrough",
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
