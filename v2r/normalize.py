"""`v2r normalize`: turn every clip into one working format, and list them in work/manifest.json.

Normalize measures and converts. It decides nothing about the edit: no colour look, filter,
sharpening, stabilising, crop or speed change beyond the plain conversion (upright, size cap,
constant 30 fps, sound format).

The manifest is what Stages 15 and 16 read; these names are frozen (decision D-03).
Top level: `version` (1), `shape`, `finished` (false until the last file is done), `stopped`
(null, or the sentence of a run that failed as a whole), `clips` (one entry per file given, in order).
Each entry: `letter`, `number` (1-based), `status` ("done" or "skipped"), `kind` ("video", "photo"
or null), `original`. Done entries add `working`, `convert_seconds` and `notes` (sentences);
skipped entries add `sentence` and `detail` (FFmpeg's own error text, cut short, or null) and an `original`
of just `path`, `name` and `bytes` (null when the file was not found); photo entries add `photo`.
A photo's `original`: `path` (absolute), `name` (as given), `bytes`, `stored_size` [w, h] (as stored, before it
is turned upright), `upright_size`, `orientation` (the photo's own turn note, 1 when it has none), `shot_at`
(string or null). Its `photo`: `file` (the full-size upright JPEG copy, such as "C-photo.jpg") and `size`.
A video's `original`: `path` (absolute), `name` (as given), `bytes`, `seconds`, `stored_size` [w, h],
`rotation`, `upright_size`, `fps`, `fps_steady`, `slow_motion`, `hdr` ("hlg", "pq", "bt2020" or null),
`dolby_vision`, `has_sound`, `shot_at` (string or null).
`working`: `file` (a name relative to the manifest's folder, such as "A.mp4"), `size`, `fps`,
`seconds`, `bytes`, `sound_added`, `colour_converted`. `photo`: `file`, `size`.
No GPS, device make or device model appears anywhere.
"""

import datetime
import errno
import io
import json
import os
import re
import statistics
import subprocess
import time
from pathlib import Path

from v2r import WORK_DIR, doctor, settings

PROBE_ENTRIES = (
    "format=duration,size:format_tags=creation_time,com.apple.quicktime.creationdate:"
    "stream=index,codec_type,codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,duration,"
    "color_range,color_space,color_transfer,color_primaries,channels,sample_rate:"
    "stream_side_data=rotation,side_data_type"
)


class NormalizeError(Exception):
    """The whole run can't go on; the message is one plain sentence."""


class Refused(Exception):
    """One file can't be used; `sentence` says so in plain English and the run goes on with the others."""

    def __init__(self, sentence, detail=None):
        super().__init__(sentence)
        self.sentence = sentence
        self.detail = detail


PHOTO_SUFFIXES = {".heic", ".heif", ".jpg", ".jpeg", ".png"}  # compared in lower case
OUT_OF_ROOM = "The work folder ran out of room, so the run stopped; please send fewer clips."


def letter(n):
    """1 gives A, 26 gives Z, 27 gives AA, and so on with no upper limit."""
    name = ""
    while n > 0:
        n, rest = divmod(n - 1, 26)
        name = chr(ord("A") + rest) + name
    return name


ORDINAL_WORDS = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]
LAST_JOB_FILES = re.compile(r"^[A-Z]{1,3}(-photo)?(\.part)?\.(mp4|jpg)$")


def ordinal(n):
    """1 gives "first" ... 10 "tenth", then "11th", "12th", "13th", "21st", "22nd", "23rd", "101st", "111th"."""
    if 1 <= n <= len(ORDINAL_WORDS):
        return ORDINAL_WORDS[n - 1]
    if n % 100 in (11, 12, 13):
        return f"{n}th"
    return f"{n}{({1: 'st', 2: 'nd', 3: 'rd'}).get(n % 10, 'th')}"


def clear_last_job(out_dir, inputs):
    """Delete the last run's lettered files and manifest in `out_dir`; nothing else, and never one of `inputs`."""
    protected = {Path(path).resolve() for path in inputs}
    for entry in Path(out_dir).iterdir():
        last_job = LAST_JOB_FILES.match(entry.name) or entry.name in ("manifest.json", "manifest.json.tmp")
        if last_job and entry.is_file() and entry.resolve() not in protected:
            entry.unlink()


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


def packet_times(path):
    """When each picture of the first video track is shown, in seconds, sorted (reads the index only, so it is fast)."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return sorted(float(t) for t in out.split() if t != "N/A")


def frame_facts(times):
    """(fps, steady, slow_motion) from the times pictures are shown; this reports, the editing decision is later."""
    if len(times) < 2:  # a one-frame clip has no gaps: steady, not slow motion
        return None, True, False
    gaps = [b - a for a, b in zip(times, times[1:])]
    median = statistics.median(gaps)
    if median <= 0:  # duplicate or stuck timestamps: the rate is unknown, so the caller falls back to avg_frame_rate
        return None, False, False
    steady = all(abs(gap - median) <= settings.STEADY_TOLERANCE * median for gap in gaps)
    return round(1 / median, 2), steady, 1 / median >= settings.SLOW_MOTION_MIN_FPS


def colour_tag(stream, key):
    """One colour tag of a stream, or None when it is missing, "unknown" or "unspecified"."""
    value = stream.get(key)
    return None if value in (None, "unknown", "unspecified") else value


def hdr_kind(stream):
    """"hlg", "pq" or "bt2020" when the colour is not ordinary, else None. Missing or "unknown" tags count as missing."""
    if colour_tag(stream, "color_transfer") == "arib-std-b67":
        return "hlg"
    if colour_tag(stream, "color_transfer") == "smpte2084":
        return "pq"
    if colour_tag(stream, "color_primaries") == "bt2020":
        return "bt2020"
    return None


COLOUR_NOTES = {
    "hlg": "HDR (HLG) was tone-mapped to ordinary colour.",
    "pq": "HDR (PQ) was tone-mapped to ordinary colour.",
    "bt2020": "Wide-gamut colour (BT.2020) was converted to ordinary colour.",
}


def colour_notes(kind, dolby_vision):
    """The manifest notes for a clip whose colour was converted; none for an ordinary clip (D-11)."""
    if kind is None:
        return []
    note = COLOUR_NOTES[kind]
    return [note + " The Dolby Vision layer was ignored." if dolby_vision else note]


def fraction(text):
    """"30000/1001" as a number; None for "0/0" or anything unreadable."""
    try:
        top, bottom = text.split("/")
        return round(float(top) / float(bottom), 2)
    except (AttributeError, ValueError, ZeroDivisionError):
        return None


def video_facts(path, info, times):
    """The `original` block of a video's manifest entry: every fact about the file as it was given."""
    path = Path(path)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    side_data = video.get("side_data_list", [])
    # Rotation is read for sizing only; FFmpeg's autorotate does the turning.
    rotation = next((int(round(item["rotation"])) for item in side_data if "rotation" in item), 0)
    stored = [video["width"], video["height"]]
    fps, steady, slow_motion = frame_facts(times)
    tags = {key.lower(): value for key, value in info.get("format", {}).get("tags", {}).items()}
    return {
        "path": str(path.resolve()),
        "name": path.name,
        "bytes": path.stat().st_size,
        "seconds": float(video.get("duration") or info["format"]["duration"]),
        "stored_size": stored,
        "rotation": rotation,
        "upright_size": stored[::-1] if rotation % 180 else list(stored),
        "fps": fps if fps is not None else fraction(video.get("avg_frame_rate")),
        "fps_steady": steady,
        "slow_motion": slow_motion,
        "hdr": hdr_kind(video),
        "dolby_vision": any(item.get("side_data_type") == "DOVI configuration record" for item in side_data),
        "has_sound": any(s["codec_type"] == "audio" and s.get("codec_name") for s in info["streams"]),
        "shot_at": tags.get("com.apple.quicktime.creationdate") or tags.get("creation_time"),
    }


def video_chain(stream, width, height, tonemap=True):
    """The filter chain for a clip at the upright working size: tone-mapped if the clip is HDR, else ordinary colour."""
    # FFmpeg has already turned upright and sideways clips the right way up (autorotate), so there is no transpose here.
    # Known cost, not a fault: on a clip stored sideways, autorotate's own turn runs ahead of this chain, so
    # every source frame is turned before fps thins it.
    kind = hdr_kind(stream)
    if kind is None or not tonemap:
        return (
            f"fps={settings.OUTPUT_FPS},scale={width}:{height}:flags=bicubic:out_color_matrix=bt709:out_range=tv,"
            "format=yuv420p,setsar=1"
        )
    # Every colour fact is passed explicitly from ffprobe (D-14); the transfer comes from a fixed map, never the file.
    transfer = {"hlg": "arib-std-b67", "pq": "smpte2084"}.get(kind, "bt709")
    peak = settings.TONEMAP_NPL if kind == "hlg" else settings.TONEMAP_NPL_PQ
    colour_range = "pc" if colour_tag(stream, "color_range") == "pc" else "tv"
    primaries = colour_tag(stream, "color_primaries") or "bt2020"
    matrix = colour_tag(stream, "color_space") or "bt2020nc"
    operator = f"tonemap={settings.TONEMAP}:desat=0," if kind != "bt2020" else ""  # gamut-only: no tone map
    return (
        f"fps={settings.OUTPUT_FPS},"
        f"zscale=w={width}:h={height}:tin={transfer}:pin={primaries}:min={matrix}:rin={colour_range}:t=linear:npl={peak},"
        f"format=gbrpf32le,zscale=p=bt709,{operator}zscale=t=bt709:m=bt709:r=tv,format=yuv420p,setsar=1"
    )


def audio_chain(audio_index, seconds):
    """The sound branch of the filter graph, ending in the label [a], exactly `seconds` long."""
    if audio_index is None:  # no usable sound: silence exactly as long as the picture, never an endless source
        return f"anullsrc=r={settings.AUDIO_RATE}:cl=stereo:d={seconds:.3f}[a]"
    return (
        f"[0:{audio_index}]aresample={settings.AUDIO_RATE}:async=1:first_pts=0,"
        f"apad=whole_dur={seconds:.3f}[a]"
    )


def encoder_options():
    """The encoder settings every working copy shares, a clip's and a photo's still alike."""
    return [
        "-c:v", "libx264", "-preset", settings.X264_PRESET, "-crf", str(settings.X264_CRF),
        "-pix_fmt", "yuv420p",  # 8-bit 4:2:0 so every player can show it
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
        "-c:a", "aac", "-b:a", str(settings.WORKING_AUDIO_BITRATE), "-ac", "2", "-ar", str(settings.AUDIO_RATE),
        "-map_metadata", "-1", "-map_chapters", "-1",  # no location or device tags in a working copy
        "-movflags", "+faststart",  # index at the front, so playback starts immediately
    ]


def video_command(src, dst, stream, size, seconds, audio_index, tonemap=True):
    """The one FFmpeg command that makes a working copy of a video."""
    width, height = size
    graph = f"[0:v:0]{video_chain(stream, width, height, tonemap)}[v];{audio_chain(audio_index, seconds)}"
    return [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
        "-i", str(src),
        "-filter_complex", graph,
        "-map", "[v]", "-map", "[a]",
        "-fps_mode", "cfr", "-r", str(settings.OUTPUT_FPS), "-t", f"{seconds:.3f}",
        *encoder_options(),
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


def tail(text):
    """The last settings.ERROR_DETAIL_CHARS characters of an error text; None when there is none."""
    text = (text or "").strip()
    return text[-settings.ERROR_DETAIL_CHARS:] if text else None


def check_ffmpeg():
    """Stop with one sentence if this computer's FFmpeg lacks a piece doctor lists (D-06); changes nothing."""
    missing = doctor.missing_ffmpeg_features()
    if not missing:
        return
    if "FFmpeg" in missing or "ffprobe" in missing:
        raise NormalizeError("FFmpeg is not installed here, so nothing was converted.")
    names = missing[0] if len(missing) == 1 else ", ".join(missing[:-1]) + " and " + missing[-1]
    raise NormalizeError(f"This computer's FFmpeg lacks {names}, so nothing was converted.")


def photo_libraries():
    """Pillow's modules (Image, ImageCms, ImageOps), with HEIC reading switched on; imported only now, so video
    and doctor keep working on a computer where these packages failed to install. ImportError means they are missing."""
    from PIL import Image, ImageCms, ImageOps
    import pillow_heif

    pillow_heif.register_heif_opener()
    return Image, ImageCms, ImageOps


def date_taken(exif):
    """The date a photo was taken as "2026-10-10T18:03:24" (plus the clock offset when it has one), else None."""
    text = exif.get_ifd(0x8769).get(0x9003) or exif.get(0x0132)  # DateTimeOriginal, else DateTime
    try:
        moment = datetime.datetime.strptime(str(text).strip(), "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None
    offset = str(exif.get_ifd(0x8769).get(0x9011) or "").strip()  # OffsetTimeOriginal, such as "+02:00"
    return moment.isoformat() + (offset if re.fullmatch(r"[+-]\d\d:\d\d", offset) else "")


def read_photo(path, copy_final, label=None):
    """Open a photo with Pillow, turn it upright once, and save the full-size copy as `copy_final` (a JPEG).

    Returns (original, photo, notes): the manifest's `original` and `photo` blocks and any sentences (`label` names
    the file in them, such as "first file, IMG_1.HEIC,"). Returns None when Pillow says the file is not a picture.
    The copy is made from pixels only: it carries no EXIF, no location, no device make or model and no
    colour-profile data, because working copies end up in reels she posts publicly.
    """
    Image, ImageCms, ImageOps = photo_libraries()
    path = Path(path)
    notes = []
    try:
        picture = Image.open(path)  # Pillow's decompression-bomb guard stays at its default
    except Image.UnidentifiedImageError:
        return None
    with picture:
        picture.load()
        stored = list(picture.size)
        exif = picture.getexif()
        orientation = exif.get(0x0112, 1)
        if not (isinstance(orientation, int) and 1 <= orientation <= 8):  # a note of any other kind is junk: none
            orientation = 1
        shot_at = date_taken(exif)
        icc = picture.info.get("icc_profile")
        image = ImageOps.exif_transpose(picture)  # once; a HEIC from pillow-heif is already upright
        if image.mode != "RGB":
            image = image.convert("RGB")
    if icc:
        try:
            image = ImageCms.profileToProfile(
                image, ImageCms.ImageCmsProfile(io.BytesIO(icc)), ImageCms.createProfile("sRGB"), outputMode="RGB")
        except Exception:  # a profile Pillow can't use: keep the colours as they are, and say so
            notes.append(
                f"The colour profile of the {label or 'photo'} could not be read, so its colours were used as they are.")
    part = part_path(copy_final)
    image.save(part, "JPEG", quality=settings.PHOTO_JPEG_QUALITY, subsampling=0)  # no exif, no icc_profile
    os.replace(part, copy_final)
    upright = list(image.size)
    original = {
        "path": str(path.resolve()),
        "name": path.name,
        "bytes": path.stat().st_size,
        "stored_size": stored,
        "upright_size": upright,
        "orientation": orientation,
        "shot_at": shot_at,
    }
    return original, {"file": Path(copy_final).name, "size": upright}, notes


def photo_graph(size):
    """The filter graph of a photo's still clip: decode and scale the big picture once, then repeat the frame."""
    width, height = size
    frames = settings.PHOTO_SECONDS * settings.OUTPUT_FPS
    # The loop filter repeats the one scaled frame. The image reader's own repeat option would decode and scale
    # the full-size photo again for every frame, about fifty times slower.
    return (
        f"[0:v:0]scale={width}:{height}:flags=bicubic:out_color_matrix=bt709:out_range=tv,format=yuv420p,setsar=1,"
        f"loop=loop={frames - 1}:size=1:start=0,setpts=N/({settings.OUTPUT_FPS}*TB)[v];"
        f"anullsrc=r={settings.AUDIO_RATE}:cl=stereo:d={settings.PHOTO_SECONDS}[a]"
    )


def photo_command(jpeg, dst, size):
    """The one FFmpeg command that makes a photo's still clip. It only ever reads the upright JPEG copy."""
    return [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
        "-i", str(jpeg),
        "-filter_complex", photo_graph(size),
        "-map", "[v]", "-map", "[a]",
        "-frames:v", str(settings.PHOTO_SECONDS * settings.OUTPUT_FPS),
        "-r", str(settings.OUTPUT_FPS), "-t", str(settings.PHOTO_SECONDS),
        *encoder_options(),
        str(dst),
    ]


def convert_photo(read, who, number, letter, shape, out_dir, started):
    """Make the still clip of a photo whose upright copy read_photo has saved; returns its "done" entry."""
    original, photo, notes = read
    copy = out_dir / photo["file"]
    final = out_dir / f"{letter}.mp4"
    part = part_path(final)
    if final.exists() or part.exists():  # only an original lying in the work folder can still be there
        copy.unlink(missing_ok=True)
        raise Refused(f"{who} could not be converted.", f"A file named {final.name} is already in the work folder.")
    size = working_size(shape, *original["upright_size"])
    try:
        run_ffmpeg(photo_command(copy, part, size), part, final)
    except subprocess.CalledProcessError as error:
        copy.unlink(missing_ok=True)
        raise Refused(f"{who} could not be converted.", tail(error.stderr)) from error
    made = probe(final)
    made_video = next(s for s in made["streams"] if s["codec_type"] == "video")
    numerator, denominator = made_video["r_frame_rate"].split("/")
    print(f"{letter} done in {round(time.monotonic() - started)} s", flush=True)
    for note in notes:
        print(note, flush=True)
    return {
        "letter": letter,
        "number": number,
        "status": "done",
        "kind": "photo",
        "original": original,
        "photo": photo,
        "working": {
            "file": final.name,
            "size": [made_video["width"], made_video["height"]],
            "fps": float(numerator) / float(denominator),
            "seconds": float(made["format"]["duration"]),
            "bytes": final.stat().st_size,
            "sound_added": True,
            "colour_converted": False,
        },
        "convert_seconds": round(time.monotonic() - started, 1),
        "notes": notes,
    }


def convert_one(path, given, number, letter, shape, out_dir, inputs):
    """Convert one file into `letter`.mp4 in `out_dir`; returns its "done" manifest entry or raises Refused.

    Checks run before any decode: found, not already in the work folder, not over the size limit, readable.
    `path` is the resolved path, `given` the path as she sent it, `inputs` every resolved input of the run.
    """
    started = time.monotonic()
    out_dir = Path(out_dir)
    who = f"The {ordinal(number)} file, {Path(given).name},"
    if not path.is_file():
        raise Refused(f"{who} was not found.")
    if path.is_relative_to(out_dir.resolve()):  # an original is never overwritten or deleted (T-2-08)
        raise Refused(f"{who} is already in the work folder, so it was left alone.")
    size_bytes = path.stat().st_size
    limit = settings.MAX_ATTACHMENT_BYTES
    if size_bytes > limit:  # by size alone: the file is never opened
        raise Refused(
            f"{who} is {size_bytes / 1e6:.0f} MB, over the {limit / 1e6:.0f} MB limit, so it was left out; "
            "a way to shrink clips comes in a later stage."
        )
    try:
        photo_libraries()
    except ImportError:
        if path.suffix.lower() in PHOTO_SUFFIXES:
            raise Refused(f"{who} looks like a photo, but photos could not be read because the picture library is not installed.")
    else:
        copy = out_dir / f"{letter}-photo.jpg"
        try:
            read = read_photo(path, copy, f"{ordinal(number)} file, {Path(given).name},")
        except Exception as error:  # Pillow's own refusals (a corrupt file, a decompression bomb, an odd format)
            copy.unlink(missing_ok=True)
            part_path(copy).unlink(missing_ok=True)
            if isinstance(error, OSError) and error.errno == errno.ENOSPC:
                raise
            raise Refused(f"{who} could not be read as a video or a photo.", tail(repr(error))) from error
        if read is not None:
            return convert_photo(read, who, number, letter, shape, out_dir, started)
    try:
        info = probe(path)
        video = next(s for s in info["streams"] if s["codec_type"] == "video")
        audio = next((s for s in info["streams"] if s["codec_type"] == "audio" and s.get("codec_name")), None)
        original = video_facts(given, info, packet_times(path))
    except (subprocess.CalledProcessError, json.JSONDecodeError, StopIteration, KeyError, ValueError) as error:
        raise Refused(
            f"{who} could not be read as a video or a photo.",
            tail(getattr(error, "stderr", None)) or tail(repr(error)),
        ) from error
    seconds = original["seconds"]
    size = working_size(shape, *original["upright_size"])
    final = out_dir / f"{letter}.mp4"
    part = part_path(final)
    if final.exists() or part.exists():  # only an original lying in the work folder can still be there
        raise Refused(f"{who} could not be converted.", f"A file named {final.name} is already in the work folder.")
    audio_index = audio["index"] if audio else None
    notes = []
    if audio is None and any(s["codec_type"] == "audio" for s in info["streams"]):
        notes.append(f"The sound of the {ordinal(number)} file, {original['name']}, could not be read, so silence was added.")
    colour_converted = original["hdr"] is not None
    colour_problem = None
    try:
        run_ffmpeg(video_command(path, part, video, size, seconds, audio_index), part, final)
    except subprocess.CalledProcessError as error:
        if not colour_converted:
            raise Refused(f"{who} could not be converted.", tail(error.stderr)) from error
        # D-13: keep the clip. Try once more with the ordinary chain; if that fails too, the file is skipped.
        colour_converted = False
        colour_problem = (
            f"The colour of the {ordinal(number)} file, {original['name']}, could not be converted, "
            "so its colour is unchanged and may look flat."
        )
        try:
            run_ffmpeg(video_command(path, part, video, size, seconds, audio_index, tonemap=False), part, final)
        except subprocess.CalledProcessError as second:
            raise Refused(f"{who} could not be converted.", tail(second.stderr)) from second
    if colour_converted:
        notes.extend(colour_notes(original["hdr"], original["dolby_vision"]))
    if colour_problem:
        notes.append(colour_problem)
    if original["slow_motion"]:
        notes.append(
            f"The {ordinal(number)} file, {original['name']}, was shot as slow motion at "
            f"{round(original['fps'])} fps; its working copy plays at normal speed."
        )

    made = probe(final)
    made_video = next(s for s in made["streams"] if s["codec_type"] == "video")
    numerator, denominator = made_video["r_frame_rate"].split("/")
    print(f"{letter} done in {round(time.monotonic() - started)} s", flush=True)
    if colour_problem:
        print(colour_problem, flush=True)
    return {
        "letter": letter,
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
            "sound_added": audio is None,
            "colour_converted": colour_converted,
        },
        "convert_seconds": round(time.monotonic() - started, 1),
        "notes": notes,
    }


def skipped_entry(letter, number, path, given, sentence, detail):
    """The manifest entry of a file that was left out; it keeps its letter (D-19)."""
    try:
        size = path.stat().st_size
    except OSError:
        size = None
    return {
        "letter": letter,
        "number": number,
        "status": "skipped",
        "kind": None,
        "original": {"path": str(path), "name": Path(given).name, "bytes": size},
        "sentence": sentence,
        "detail": detail,
    }


def normalize(files, shape, out_dir=None):
    """Convert `files`, in the order given, into working copies A, B, C... in `out_dir`; returns the manifest.

    A file that can't be used is skipped with one sentence and the others carry on; only a run that can't
    go on at all (no FFmpeg piece, out of room) raises NormalizeError.
    """
    if shape not in settings.SHAPES:
        raise NormalizeError("The shape must be tall or wide.")
    check_ffmpeg()  # before anything in the work folder is touched
    out_dir = Path(WORK_DIR if out_dir is None else out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    inputs = [Path(file).resolve() for file in files]
    given = [Path(file) for file in files]
    clear_last_job(out_dir, inputs)  # a new run is a new job (D-18)
    manifest = {"version": 1, "shape": shape, "finished": False, "stopped": None, "clips": []}
    write_manifest(out_dir, manifest)

    try:
        for number, (path, as_given) in enumerate(zip(inputs, given), start=1):
            name = letter(number)
            who = f"The {ordinal(number)} file, {as_given.name},"
            try:
                entry = convert_one(path, as_given, number, name, shape, out_dir, inputs)
                json.dumps(entry)  # a value that can't be written to the manifest turns this one file into a skipped one
            except Refused as refused:
                entry = skipped_entry(name, number, path, as_given, refused.sentence, refused.detail)
            except subprocess.CalledProcessError as error:
                entry = skipped_entry(name, number, path, as_given, f"{who} could not be converted.", tail(error.stderr))
            except OSError as error:
                if error.errno == errno.ENOSPC:
                    raise
                entry = skipped_entry(
                    name, number, path, as_given, f"{who} could not be read as a video or a photo.", tail(repr(error)))
            except Exception as error:  # one broad catch at the per-file boundary: nothing may stop the others
                entry = skipped_entry(
                    name, number, path, as_given, f"{who} could not be read as a video or a photo.", tail(repr(error)))
            if entry["status"] == "skipped":
                leftover = part_path(out_dir / f"{name}.mp4")
                if leftover.resolve() not in inputs:  # never a half-made copy, and never an original
                    leftover.unlink(missing_ok=True)
                print(entry["sentence"], flush=True)
            manifest["clips"].append(entry)
            write_manifest(out_dir, manifest)
    except OSError as error:
        if error.errno != errno.ENOSPC:
            raise
        manifest["stopped"] = OUT_OF_ROOM
        try:
            write_manifest(out_dir, manifest)
        except OSError:
            pass
        raise NormalizeError(OUT_OF_ROOM) from error

    manifest["finished"] = True
    write_manifest(out_dir, manifest)
    done = sum(1 for clip in manifest["clips"] if clip["status"] == "done")
    print(f"{done} of {len(inputs)} files converted; the list is in {out_dir / 'manifest.json'}.", flush=True)
    return manifest
