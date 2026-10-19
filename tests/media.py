"""Helpers for tests: clips made by FFmpeg on the spot, and ffprobe readers. Nothing here is committed footage."""

import hashlib
import json
import re
import subprocess

BARS = "smptehdbars=size={w}x{h}:rate={fps}:duration={s}"
# A black picture with a white square in the stored top-left corner, to show where a turn puts that corner.
MARKER = "color=black:size={w}x{h}:rate={fps}:duration={s},drawbox=x=0:y=0:w=120:h=120:color=white:t=fill"
BEEP = "aevalsrc='0.5*sin(2*PI*1000*t)*lt(mod(t,1),0.2)':s=48000:d={s}"  # the same beep tests/test_join.py uses
FLAT = "color=c=0x7E7E7E:size={w}x{h}:rate={fps}:duration={s}"  # one grey patch, for brightness checks
TRC = {"hlg": "arib-std-b67", "pq": "smpte2084"}  # a gamut-only clip ("bt2020") gets no transfer tag
TIMEOUT = 60  # seconds: a hung FFmpeg fails one test instead of the whole suite


def run(command):
    subprocess.run(command, check=True, timeout=TIMEOUT)


def make_clip(path, width, height, seconds=2, fps=30, sound=True, rotate=None, pattern="bars", metadata=None,
              sound_seconds=None, vfr=False, hdr=None):
    """A test clip made by FFmpeg.

    `pattern` is "bars" (colour bars), "marker" (black with a white corner square) or "flat" (one grey patch).
    `hdr` ("hlg", "pq" or "bt2020") tags the clip 10-bit BT.2020; "bt2020" has the wide gamut but no HDR transfer.
    `sound` adds a 1 kHz beep.
    `rotate` (90, -90 or 180) stores the clip sideways: the picture is unchanged and only the turn flag is set.
    `sound_seconds` makes the beep shorter than the picture. `vfr` drops random pictures, so the timing is uneven.
    `metadata` is a dict of tags written into the file (use a .mov name for the Apple tags).
    """
    source = {"marker": MARKER, "flat": FLAT}.get(pattern, BARS).format(w=width, h=height, fps=fps, s=seconds)
    first = path.with_name(f"plain-{path.name}") if rotate else path
    command = ["ffmpeg", "-loglevel", "error", "-nostdin", "-f", "lavfi", "-i", source]
    if sound:
        command += ["-f", "lavfi", "-i", BEEP.format(s=sound_seconds or seconds)]
    if hdr:
        trc = f":color_trc={TRC[hdr]}" if hdr in TRC else ""
        command += ["-vf", f"setparams=color_primaries=bt2020{trc}:colorspace=bt2020nc,format=yuv420p10le"]
    if vfr:
        command += ["-vf", "select='gt(random(1),0.35)'", "-fps_mode", "passthrough"]
    command += ["-c:v", "libx264", "-preset", "ultrafast"]
    command += ["-c:a", "aac"] if sound else ["-an"]
    if metadata:
        for key, value in metadata.items():
            command += ["-metadata", f"{key}={value}"]
        command += ["-movflags", "use_metadata_tags"]
    run([*command, str(first)])
    if rotate:
        # -metadata:s:v rotate=... writes nothing; -display_rotation, an input option, is what stores the turn flag.
        run(["ffmpeg", "-loglevel", "error", "-nostdin", "-display_rotation", str(rotate), "-i", str(first),
             "-c", "copy", str(path)])
        first.unlink()
    return path


LOOK_FPS = 30  # frames a second of a look test clip, as in a working copy
# Detail in both directions for the clips that need the camera to be measurable: bars plus two grids.
# k is the clip's width over 360, so a wide clip, which look shrinks more, keeps lines as thick as a narrow one's.
DETAIL = ("smptehdbars=size={w}x{h}:rate=30:duration={s},drawgrid=w={g1}:h={g1}:t={t1}:c=white,"
          "drawgrid=w={g2}:h={g3}:t={t2}:c=black,gblur=sigma=1")


def make_look_clip(path, width, height, pattern="plain", seconds=8, start=None, end=None, level=None, beep=None, speed=None):
    """A clip shaped like a working copy (H.264, 30 fps, stereo AAC at 48 kHz) with a known answer for look to find.

    `pattern`: "plain" (colour bars); "square" (bars with a white square a fifth of the width wide that crosses the
    picture left to right between `start` and `end` seconds); "cut" (bars, then at `start` the same bars negated and
    turned in hue); "jitter" (the whole picture shaken by random offsets of up to 12 pixels each way every frame);
    "pan" (a steady sideways drift of the camera, 40 pixels a second for a 360-wide clip, faster in proportion for a
    wider one); "pan-cut" (the same detailed picture drifting, by default at 112 pixels a second for a 360-wide clip,
    until `start`, then a cut to the plain bars standing still); "blur" (bars blurred between `start` and `end`); "grey" (one flat grey at `level`, such as "0x303030");
    "cast" (bars with a red-and-yellow cast). `beep` is (from, to) seconds of a 1 kHz tone; otherwise the sound is
    digital silence, so every clip has a sound track as working copies do.
    """
    size = f"size={width}x{height}:rate={LOOK_FPS}:duration={seconds}"
    bars = BARS.format(w=width, h=height, fps=LOOK_FPS, s=seconds)
    command = ["ffmpeg", "-loglevel", "error", "-nostdin", "-y"]
    complex_graph = None
    video_filter = None  # an output option, so it is added after the last input
    if pattern == "plain":
        command += ["-f", "lavfi", "-i", bars]
    elif pattern == "square":
        side = width // 5
        x = f"if(between(t,{start},{end}),(t-{start})/({end}-{start})*({width}-{side}),-{side})"
        command += ["-f", "lavfi", "-i", bars, "-f", "lavfi", "-i", f"color=white:size={side}x{side}:rate={LOOK_FPS}:duration={seconds}"]
        complex_graph = f"[0][1]overlay=x='{x}':y={(height - side) // 2}:eval=frame[v]"
    elif pattern == "cut":
        first = BARS.format(w=width, h=height, fps=LOOK_FPS, s=start)
        second = BARS.format(w=width, h=height, fps=LOOK_FPS, s=round(seconds - start, 3))
        command += ["-f", "lavfi", "-i", first, "-f", "lavfi", "-i", second]
        complex_graph = "[1]negate,hue=h=90[b];[0][b]concat=n=2:v=1:a=0[v]"
    elif pattern == "pan-cut":
        speed = speed or 112 * width / 360  # about 10 pixels per analysed frame at the measuring width, inside deshake's search
        k = width / 360
        source = DETAIL.format(
            w=width + 400 + int(speed * start), h=height + 400, s=start,
            g1=round(40 * k), t1=round(2 * k), g2=round(130 * k), g3=round(90 * k), t2=round(3 * k))
        after = BARS.format(w=width, h=height, fps=LOOK_FPS, s=round(seconds - start, 3))
        command += ["-f", "lavfi", "-i", source, "-f", "lavfi", "-i", after]
        complex_graph = (
            f"[0]crop={width}:{height}:x='20+t*{speed}':y=100,setsar=1,format=yuv420p[a];"
            "[1]setsar=1,format=yuv420p[b];[a][b]concat=n=2:v=1:a=0[v]")
    elif pattern in ("jitter", "pan"):
        speed = speed or 40 * width / 360  # pixels a second of the pan; the picture is wide enough for the whole drift
        k = width / 360
        source = DETAIL.format(
            w=width + 400 + int(speed * seconds), h=height + 400, s=seconds,
            g1=round(40 * k), t1=round(2 * k), g2=round(130 * k), g3=round(90 * k), t2=round(3 * k))
        if pattern == "jitter":
            crop = f"crop={width}:{height}:x='200+(random(0)-0.5)*24':y='200+(random(1)-0.5)*24'"
        else:
            crop = f"crop={width}:{height}:x='20+t*{speed}':y=100"
        command += ["-f", "lavfi", "-i", source]
        video_filter = crop
    elif pattern == "blur":
        command += ["-f", "lavfi", "-i", bars]
        video_filter = f"gblur=sigma=10:enable='between(t,{start},{end})'"
    elif pattern == "grey":
        command += ["-f", "lavfi", "-i", f"color=c={level}:{size}"]
    elif pattern == "cast":
        command += ["-f", "lavfi", "-i", bars]
        video_filter = "colorbalance=rm=0.5:bm=-0.5:rs=0.4:bs=-0.4"
    else:
        raise ValueError(pattern)
    if beep:
        tone = f"aevalsrc='0.5*sin(2*PI*1000*t)*between(t,{beep[0]},{beep[1]})':s=48000:d={seconds}"
    else:
        tone = "anullsrc=channel_layout=stereo:sample_rate=48000"
    command += ["-f", "lavfi", "-i", tone]
    inputs = command.count("-i")
    if complex_graph:
        command += ["-filter_complex", complex_graph, "-map", "[v]"]
    else:
        command += ["-map", "0:v"]
        if video_filter:
            command += ["-filter:v:0", video_filter]
    command += ["-map", f"{inputs - 1}:a", "-t", str(seconds)]
    command += ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "12", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ac", "2", "-ar", "48000"]
    run([*command, str(path)])
    return path


BURST_SECONDS = 0.3  # how long a burst of make_bursts_clip lasts


def make_bursts_clip(path, width, height, times, seconds=8):
    """A silent clip shaped like a working copy with a quick burst of movement after each of `times`.

    A white square a third of the width wide crosses the frame left to right during the 0.3 s after each time and is
    hidden the rest of the time (by `overlay` with `eval=frame`, where `t` is time; a still square would change the
    picture only on the frames where it appears and vanishes).
    """
    side = width // 3
    x = f"-{side}"
    for start in times:
        end = round(start + BURST_SECONDS, 3)
        x = f"if(between(t,{start},{end}),(t-{start})/{BURST_SECONDS}*({width}-{side}),{x})"
    bars = BARS.format(w=width, h=height, fps=LOOK_FPS, s=seconds)
    square = f"color=white:size={side}x{side}:rate={LOOK_FPS}:duration={seconds}"
    graph = f"[0][1]overlay=x='{x}':y={(height - side) // 2}:eval=frame[v]"
    run(["ffmpeg", "-loglevel", "error", "-nostdin", "-y", "-f", "lavfi", "-i", bars, "-f", "lavfi", "-i", square,
         "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000", "-filter_complex", graph,
         "-map", "[v]", "-map", "2:a", "-t", str(seconds), "-c:v", "libx264", "-preset", "ultrafast", "-crf", "12",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-ac", "2", "-ar", "48000", str(path)])
    return path


def make_audio(path, seconds=2):
    """A sound-only file (the beep, AAC in .m4a): not a video and not a photo."""
    run(["ffmpeg", "-loglevel", "error", "-nostdin", "-f", "lavfi", "-i", BEEP.format(s=seconds), "-c:a", "aac", str(path)])
    return path


def probe(path):
    """ffprobe's JSON for the facts the tests look at."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=index,codec_type,codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,duration,channels,"
         "sample_rate,nb_frames,color_transfer,color_space,color_primaries:stream_side_data=rotation,side_data_type:"
         "format=duration:format_tags", "-of", "json", str(path)],
        capture_output=True, text=True, check=True, timeout=TIMEOUT,
    ).stdout
    return json.loads(out)


def stream(info, kind):
    """The first stream of `kind` ("video" or "audio") in probe() output."""
    return next(s for s in info["streams"] if s["codec_type"] == kind)


def gray_frame(path, at=0.5):
    """One picture from `path` as raw grey bytes (one byte per pixel), with its width and height."""
    video = stream(probe(path), "video")
    data = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-nostdin", "-ss", str(at), "-i", str(path), "-frames:v", "1",
         "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        capture_output=True, check=True, timeout=TIMEOUT,
    ).stdout
    return data, video["width"], video["height"]


def corner_mean(frame, width, height, corner, size=40):
    """Average brightness (0-255) of a `size` x `size` square in one corner: "top-left", "top-right", "bottom-left" or "bottom-right"."""
    top, side = corner.split("-")
    rows = range(0, size) if top == "top" else range(height - size, height)
    columns = range(0, size) if side == "left" else range(width - size, width)
    values = [frame[y * width + x] for y in rows for x in columns]
    return sum(values) / len(values)


def peak_volume(path):
    """The loudest moment of the sound, in dB (silence is -inf or about -91)."""
    err = subprocess.run(
        ["ffmpeg", "-nostdin", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True, check=True, timeout=TIMEOUT,
    ).stderr
    return float(re.search(r"max_volume: (\S+) dB", err).group(1))


def mean_luma(path, at=0.5):
    """Average brightness (0-255) of one whole picture of `path`."""
    frame, _, _ = gray_frame(path, at)
    return sum(frame) / len(frame)


def sha256(path):
    """The SHA-256 of a file, read in blocks."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def filter_names(graph):
    """The filter names in an FFmpeg filter graph: split on ; and ,, drop [labels], keep the text before "="."""
    names = []
    for piece in re.split(r"[;,]", graph):
        piece = re.sub(r"^(\[[^\]]*\])+|(\[[^\]]*\])+$", "", piece.strip())
        name = piece.split("=")[0].strip()
        if name:
            names.append(name)
    return names


def make_photo(path, width, height, orientation=None, fmt=None, mode="RGB", colour=(200, 80, 40), box=True,
               date=None, icc=False, exif_extra=None):
    """A test photo made by Pillow: a flat colour with a 60x60 white box in the stored top-left corner.

    `fmt` is "JPEG", "PNG" or "HEIF" (default: from the file name). `mode` "RGBA" makes the picture half see-through.
    `orientation` is the photo's turn note (EXIF 0x0112, such as 6); `date` is the date taken as "2026:10:10 18:03:24"
    (EXIF DateTimeOriginal); `exif_extra` maps other EXIF tags to values (such as 0x010F make); `icc` embeds an sRGB profile.
    """
    from PIL import Image, ImageCms, ImageDraw  # Pillow is imported here only, as in the program itself

    suffix = path.suffix.lower()
    fmt = fmt or {".png": "PNG", ".heic": "HEIF", ".heif": "HEIF"}.get(suffix, "JPEG")
    if fmt == "HEIF":
        import pillow_heif

        pillow_heif.register_heif_opener()
    image = Image.new("RGB", (width, height), colour)
    if box:
        ImageDraw.Draw(image).rectangle((0, 0, 59, 59), fill=(255, 255, 255))
    if mode == "RGBA":
        image = image.convert("RGBA")
        image.putalpha(128)
    exif = Image.Exif()
    if orientation:
        exif[0x0112] = orientation
    if date:
        exif.get_ifd(0x8769)[0x9003] = date
    for tag, value in (exif_extra or {}).items():
        exif[tag] = value
    options = {}
    if orientation or date or exif_extra:
        options["exif"] = exif
    if icc:
        options["icc_profile"] = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    image.save(path, fmt, **options)
    return path


def corner_mean_image(path, corner, size=20):
    """Average brightness (0-255) of a `size` x `size` square in one corner of a picture file, read by Pillow."""
    from PIL import Image, ImageStat

    with Image.open(path) as image:
        grey = image.convert("L")
    width, height = grey.size
    top, side = corner.split("-")
    left = 0 if side == "left" else width - size
    upper = 0 if top == "top" else height - size
    return ImageStat.Stat(grey.crop((left, upper, left + size, upper + size))).mean[0]


def white_share(path, box):
    """The share (0 to 1) of pixels in `box` ([left, top, right, bottom]) of a picture file whose three channels are all
    at least 200 (near white), read by Pillow."""
    from PIL import Image, ImageChops

    with Image.open(path) as image:
        red, green, blue = image.convert("RGB").crop(tuple(box)).split()
    darkest = ImageChops.darker(ImageChops.darker(red, green), blue)  # per pixel, the lowest of the three channels
    counts = darkest.histogram()
    return sum(counts[200:]) / sum(counts)


def make_manifest(work, shape, entries):
    """Write work/manifest.json with normalize's frozen names, so look tests need not run normalize; returns it.

    Each entry is a Path to a clip already saved in `work` (a done video), or a dict with `file` (Path or None),
    `kind` ("video" or "photo"), `status` ("done" or "skipped") and `sound_added` (bool); the keys left out are
    "video", "done" and False. A dict may also carry `working`, used exactly as given without probing, for a missing,
    broken or wrongly named working copy. Letters are A, B, C in order and numbers count from 1.
    """
    clips = []
    for number, item in enumerate(entries, start=1):
        spec = item if isinstance(item, dict) else {"file": item}
        file = spec.get("file")
        kind = spec.get("kind", "video")
        status = spec.get("status", "done")
        sound_added = spec.get("sound_added", False)
        letter = chr(ord("A") + number - 1)
        original = {
            "path": str(file) if file else f"/sent/{letter}-original.mov",
            "name": file.name if file else f"{letter}-original.mov",
            "bytes": file.stat().st_size if file and file.exists() else None,
        }
        if status == "skipped":
            clips.append({
                "letter": letter, "number": number, "status": "skipped", "kind": None, "original": original,
                "sentence": f"The file number {number} could not be converted.", "detail": None,
            })
            continue
        if "working" in spec:
            working = spec["working"]
        else:
            info = probe(file)
            video = stream(info, "video")
            top, bottom = video["r_frame_rate"].split("/")
            working = {
                "file": file.name,
                "size": [video["width"], video["height"]],
                "fps": float(top) / float(bottom),
                "seconds": float(info["format"]["duration"]),
                "bytes": file.stat().st_size,
                "sound_added": sound_added,
                "colour_converted": False,
            }
        entry = {
            "letter": letter, "number": number, "status": "done", "kind": kind, "original": original,
            "working": working, "convert_seconds": 0.1, "notes": [],
        }
        if kind == "photo":
            entry["photo"] = {"file": f"{letter}-photo.jpg", "size": list(working.get("size", [0, 0]))}
        clips.append(entry)
    manifest = {"version": 1, "shape": shape, "finished": True, "stopped": None, "clips": clips}
    (work / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
