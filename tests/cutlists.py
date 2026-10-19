"""The two approved example cut lists and a placeholder work folder to check them against (no FFmpeg, no real video).

A helper module beside media.py, not a test file. Every segment carries clip, from, to, sound and a non-empty why, the
shape every list must have to pass the schema. The seconds are written out in full so a reader can follow the cut list
by eye.
"""

import copy
import json
from pathlib import Path

from media import make_manifest

SIZES = {  # placeholder working sizes by (shape, orientation), width and height in pixels
    ("tall", "upright"): [1080, 1920],
    ("tall", "sideways"): [3414, 1920],
    ("wide", "sideways"): [1920, 1080],
    ("wide", "upright"): [1080, 1920],
}
PHOTO_SIZE = {"tall": [1080, 1920], "wide": [1920, 2560]}  # a photo's still is the upright size of its job

CLIP_PLAN = {  # per shape: (letter, kind, orientation, seconds, original name)
    "tall": [
        ("A", "video", "upright", 12.0, "IMG_4410.MOV"),
        ("B", "video", "sideways", 10.0, "IMG_4412.MOV"),
        ("C", "video", "upright", 8.0, "IMG_4415.MOV"),
        ("D", "video", "upright", 9.0, "IMG_4417.MOV"),
        ("E", "photo", "upright", 4.0, "IMG_4420.HEIC"),
    ],
    "wide": [
        ("A", "video", "sideways", 40.0, "IMG_5001.MOV"),
        ("B", "video", "upright", 8.0, "IMG_5003.MOV"),
        ("C", "photo", "upright", 4.0, "IMG_5004.HEIC"),
    ],
}


def placeholder_work(tmp_path, shape):
    """A work folder of empty placeholder files and a matching manifest; returns (work folder, manifest)."""
    work = Path(tmp_path) / "work"
    work.mkdir()
    entries = []
    for letter, kind, orientation, seconds, original in CLIP_PLAN[shape]:
        (work / f"{letter}.mp4").write_bytes(b"")
        if kind == "photo":
            (work / f"{letter}-photo.jpg").write_bytes(b"")
        entries.append({
            "file": Path(tmp_path) / "sent" / original,
            "kind": kind,
            "working": {
                "file": f"{letter}.mp4",
                "size": PHOTO_SIZE[shape] if kind == "photo" else SIZES[(shape, orientation)],
                "fps": 30.0,
                "seconds": seconds,
                "bytes": 0,
                "sound_added": False,
                "colour_converted": False,
            },
        })
    return work, make_manifest(work, shape, entries)


def clips_block(manifest):
    """The cut list's clips block for every done clip of the manifest."""
    return {
        entry["letter"]: {"file": entry["original"]["name"], "seconds": entry["working"]["seconds"]}
        for entry in manifest["clips"] if entry["status"] == "done"
    }


def segment(clip, start, end, sound, why, **more):
    return {"clip": clip, "from": start, "to": end, "sound": sound, "why": why, **more}


def touch_up(brightness, blue, red, saturation):
    return {"brightness": brightness, "blue": blue, "red": red, "saturation": saturation}


def tall_example(clips):
    """The approved 20-second tall reel: seven segments over four clips and a photo."""
    return {
        "version": 1,
        "canvas": {"width": 1080, "height": 1920, "fps": 30},
        "clips": clips,
        "segments": [
            segment("A", 1.0, 4.0, "off", "A 01.0 to A 04.0: waves roll in, camera still"),
            segment("B", 2.0, 4.5, "off", "B 02.0 to B 04.5: she looks up, left of centre", focus_x=0.35),
            segment("C", 0.5, 3.5, "off", "C 00.5 to C 03.5: walking right; the frame follows", move="pan-right"),
            segment("D", 3.0, 6.0, "keep", "D 03.0 to D 06.0: the laugh, sound kept"),
            segment("E", 0.0, 3.0, "off", "E 00.0: the photo, a slow push-in", move="push-in"),
            segment("A", 6.0, 8.5, "off", "A 06.0 to A 08.5: the wave breaks"),
            segment("B", 6.0, 9.0, "off", "B 06.0 to B 09.0: she walks off right", focus_x=0.6),
        ],
        "look": {
            "filter": "none",
            "touch_up": {
                "A": touch_up(2.0, -1.0, 0.5, 1.02),
                "B": touch_up(-3.0, 1.5, -0.5, 0.97),
                "C": touch_up(0.0, 0.0, 0.0, 1.0),
                "D": touch_up(4.5, -2.0, 1.0, 1.05),
                "E": touch_up(-1.0, 0.5, 0.0, 0.99),
            },
        },
        "sound": {"music": "test-tone", "music_from": 6.2, "music_under_sound": -12, "loudness": -14},
        "cover": {"segment": 4, "at": 1.0},
    }


def wide_example(clips):
    """The approved 38-second wide talking head with two cut-aways."""
    return {
        "version": 1,
        "canvas": {"width": 1920, "height": 1080, "fps": 30},
        "clips": clips,
        "segments": [
            segment("A", 0.0, 10.0, "keep", "A 00.0 to A 10.0: the opening sentence"),
            segment("B", 1.0, 4.0, "off", "B 01.0 to B 04.0: the cut-away, framed on her hands", focus_y=0.3),
            segment("A", 13.0, 25.0, "keep", "A 13.0 to A 25.0: the middle"),
            segment("C", 0.0, 3.0, "off", "C 00.0: the photo, a slow pull-out", move="pull-out"),
            segment("A", 28.0, 38.0, "keep", "A 28.0 to A 38.0: the sign-off"),
        ],
        "look": {
            "filter": "none",
            "touch_up": {
                "A": touch_up(1.0, -0.5, 0.5, 1.01),
                "B": touch_up(-2.0, 1.0, -1.0, 0.98),
                "C": touch_up(0.0, 0.0, 0.0, 1.0),
            },
        },
        "sound": {"music": "test-tone", "music_from": 0.0, "music_under_sound": -20, "loudness": -14},
    }


EXAMPLES = {"tall": tall_example, "wide": wide_example}


def scaled(cutlist, factor):
    """A deep copy with every segment's from and to, and the cover's at, multiplied by `factor` (3 decimals)."""
    result = copy.deepcopy(cutlist)
    for item in result["segments"]:
        item["from"] = round(item["from"] * factor, 3)
        item["to"] = round(item["to"] * factor, 3)
    if "cover" in result:
        result["cover"]["at"] = round(result["cover"]["at"] * factor, 3)
    return result


def write_list(work, data, name="cutlist.json"):
    """Write the list as JSON into the work folder; returns its path."""
    path = Path(work) / name
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path
