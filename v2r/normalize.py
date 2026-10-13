"""`v2r normalize`: turn every clip into one working format, and list them in work/manifest.json.

Normalize measures and converts. It decides nothing about the edit: no colour look, filter,
sharpening, stabilising, crop or speed change beyond the plain conversion (upright, size cap,
constant 30 fps, sound format).

The manifest is what Stages 15 and 16 read; these names are frozen (decision D-03).
Top level: `version` (1), `shape`, `finished` (false until the last file is done), `stopped`
(null, or the sentence of a run that failed as a whole), `clips` (one entry per file given, in order).
Each entry: `letter`, `number` (1-based), `status` ("done" or "skipped"), `kind` ("video", "photo"
or null), `original`. Done entries add `working`, `convert_seconds` and `notes` (sentences);
skipped entries add `sentence` and `detail`; photo entries add `photo`.
A video's `original`: `path` (absolute), `name` (as given), `bytes`, `seconds`, `stored_size` [w, h],
`rotation`, `upright_size`, `fps`, `fps_steady`, `slow_motion`, `hdr` ("hlg", "pq", "bt2020" or null),
`dolby_vision`, `has_sound`, `shot_at` (string or null).
`working`: `file` (a name relative to the manifest's folder, such as "A.mp4"), `size`, `fps`,
`seconds`, `bytes`, `sound_added`, `colour_converted`. `photo`: `file`, `size`.
No GPS, device make or device model appears anywhere.
"""

import json
import os
import subprocess
import time
from pathlib import Path

from v2r import WORK_DIR, settings

PROBE_ENTRIES = (
    "format=duration,size:format_tags=creation_time,com.apple.quicktime.creationdate:"
    "stream=index,codec_type,codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,duration,"
    "color_range,color_space,color_transfer,color_primaries,channels,sample_rate:"
    "stream_side_data=rotation,side_data_type"
)


class NormalizeError(Exception):
    """The whole run can't go on; the message is one plain sentence."""


def letter(n):
    """1 gives A, 26 gives Z, 27 gives AA, and so on with no upper limit."""
    name = ""
    while n > 0:
        n, rest = divmod(n - 1, 26)
        name = chr(ord("A") + rest) + name
    return name


def working_size(shape, width, height):
    """The working frame size for an upright source: capped by settings.WORKING_SIZE, never enlarged, even numbers."""
    if width > height:
        orientation = "landscape"
    elif height > width:
        orientation = "portrait"
    else:  # a square uses its own shape's entry
        orientation = "portrait" if shape == "tall" else "landscape"
    cap_width, cap_height = settings.WORKING_SIZE[shape][orientation]
    factor = min([1.0] + [cap / side for cap, side in ((cap_width, width), (cap_height, height)) if cap])
    # Floor to an even number (never over the cap); join.even() rounds, so it isn't used here.
    return max(2, int(width * factor) // 2 * 2), max(2, int(height * factor) // 2 * 2)


def probe(path):
    """ffprobe's facts about a file, as parsed JSON."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", PROBE_ENTRIES, "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(out)


def video_chain(stream, width, height):
    """The ordinary-colour filter chain for a clip that is not HDR, at the upright working size."""
    # FFmpeg has already turned upright and sideways clips the right way up (autorotate), so there is no transpose here.
    # Known cost, not a fault: on a clip stored sideways, autorotate's own turn runs ahead of this chain, so
    # every source frame is turned before fps thins it.
    return (
        f"fps={settings.OUTPUT_FPS},scale={width}:{height}:flags=bicubic:out_color_matrix=bt709:out_range=tv,"
        "format=yuv420p,setsar=1"
    )


def audio_chain(audio_index, seconds):
    """The sound branch of the filter graph, ending in the label [a], exactly `seconds` long."""
    return (
        f"[0:{audio_index}]aresample={settings.AUDIO_RATE}:async=1:first_pts=0,"
        f"apad=whole_dur={seconds:.3f}[a]"
    )


def video_command(src, dst, stream, size, seconds, audio_index):
    """The one FFmpeg command that makes a working copy of a video."""
    width, height = size
    graph = f"[0:v:0]{video_chain(stream, width, height)}[v];{audio_chain(audio_index, seconds)}"
    return [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
        "-i", str(src),
        "-filter_complex", graph,
        "-map", "[v]", "-map", "[a]",
        "-fps_mode", "cfr", "-r", str(settings.OUTPUT_FPS), "-t", f"{seconds:.3f}",
        "-c:v", "libx264", "-preset", settings.X264_PRESET, "-crf", str(settings.X264_CRF),
        "-pix_fmt", "yuv420p",  # 8-bit 4:2:0 so every player can show it
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
        "-c:a", "aac", "-b:a", str(settings.WORKING_AUDIO_BITRATE), "-ac", "2", "-ar", str(settings.AUDIO_RATE),
        "-map_metadata", "-1", "-map_chapters", "-1",  # no location or device tags in a working copy
        "-movflags", "+faststart",  # index at the front, so playback starts immediately
        str(dst),
    ]


def part_path(final):
    """A.mp4 becomes A.part.mp4 in the same folder."""
    final = Path(final)
    return final.with_name(f"{final.stem}.part{final.suffix}")


def run_ffmpeg(command, part, final):
    """Run `command`, which writes `part`; only a finished file is moved onto its final name."""
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        Path(part).unlink(missing_ok=True)
        raise
    os.replace(part, final)


def write_manifest(out_dir, manifest):
    """Write manifest.json whole or not at all, so a reader never sees half a file."""
    out_dir = Path(out_dir)
    temp = out_dir / "manifest.json.tmp"
    temp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, out_dir / "manifest.json")


def normalize(files, shape, out_dir=None):
    """Convert `files`, in the order given, into working copies A, B, C... in `out_dir`; returns the manifest."""
    if shape not in settings.SHAPES:
        raise NormalizeError("The shape must be tall or wide.")
    out_dir = Path(WORK_DIR if out_dir is None else out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    inputs = [Path(file).resolve() for file in files]
    given = [Path(file) for file in files]
    manifest = {"version": 1, "shape": shape, "finished": False, "stopped": None, "clips": []}
    write_manifest(out_dir, manifest)

    for number, (path, as_given) in enumerate(zip(inputs, given), start=1):
        name = letter(number)
        started = time.monotonic()
        info = probe(path)
        video = next(s for s in info["streams"] if s["codec_type"] == "video")
        audio = next((s for s in info["streams"] if s["codec_type"] == "audio" and s.get("codec_name")), None)
        seconds = float(video.get("duration") or info["format"]["duration"])
        stored = [video["width"], video["height"]]
        original = {
            "path": str(path),
            "name": as_given.name,
            "bytes": path.stat().st_size,
            "seconds": seconds,
            "stored_size": stored,
            "upright_size": list(stored),
        }
        size = working_size(shape, *original["upright_size"])
        final = out_dir / f"{name}.mp4"
        part = part_path(final)
        audio_index = audio["index"] if audio else None
        run_ffmpeg(video_command(path, part, video, size, seconds, audio_index), part, final)

        made = probe(final)
        made_video = next(s for s in made["streams"] if s["codec_type"] == "video")
        numerator, denominator = made_video["r_frame_rate"].split("/")
        manifest["clips"].append({
            "letter": name,
            "number": number,
            "status": "done",
            "kind": "video",
            "original": original,
            "working": {
                "file": final.name,
                "size": [made_video["width"], made_video["height"]],
                "fps": float(numerator) / float(denominator),
                "seconds": float(made["format"]["duration"]),
                "bytes": final.stat().st_size,
                "sound_added": False,
                "colour_converted": False,
            },
            "convert_seconds": round(time.monotonic() - started, 1),
            "notes": [],
        })
        print(f"{name} done in {round(time.monotonic() - started)} s", flush=True)
        write_manifest(out_dir, manifest)

    manifest["finished"] = True
    write_manifest(out_dir, manifest)
    done = sum(1 for clip in manifest["clips"] if clip["status"] == "done")
    print(f"{done} of {len(inputs)} files converted; the list is in {out_dir / 'manifest.json'}.", flush=True)
    return manifest
