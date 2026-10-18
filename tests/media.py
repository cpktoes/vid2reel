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
