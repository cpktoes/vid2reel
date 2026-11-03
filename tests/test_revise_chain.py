"""The phone test's chain on generated clips: a reel, then shorter, mute it and a wide version, each rendered from the newest list. FFmpeg needed; no real footage."""

import json

import pytest
from media import make_clip, peak_volume, probe, sha256, stream

import v2r.look
import v2r.normalize
import v2r.render.revise
from v2r import settings
from v2r.__main__ import main

SMALL_CAPS = {
    "tall": {"portrait": (180, 320), "landscape": (None, 320)},
    "wide": {"landscape": (320, 180), "portrait": (320, None)},
}
CLIP_SIZE = {"tall": (360, 640), "wide": (640, 360)}  # the clip sizes swap with the shape
OTHER = {"tall": "wide", "wide": "tall"}
SILENT = -60.0  # dB: a muted reel is far below this


@pytest.fixture(autouse=True)
def small_and_quick(tmp_path, monkeypatch):
    """Small working sizes, a quick encode, and every default work folder sent into tmp_path."""
    monkeypatch.setattr(settings, "WORKING_SIZE", SMALL_CAPS)
    monkeypatch.setattr(settings, "RENDER_X264_PRESET", "ultrafast")
    folder = tmp_path / "default-work"
    monkeypatch.setattr(v2r.normalize, "WORK_DIR", folder)
    monkeypatch.setattr(v2r.look, "WORK_DIR", folder)
    monkeypatch.setattr(v2r.render.revise, "WORK_DIR", folder)
    return folder


def reels(work):
    return {path.name for path in work.glob("reel-*.mp4")}


def render_and_find(work, *arguments):
    """Render with `arguments`, and return the one new reel."""
    before = reels(work)
    assert main(["render", *arguments, "--work", str(work)]) == 0
    (name,) = reels(work) - before
    return work / name


def frames(reel):
    return int(stream(probe(reel), "video")["nb_frames"])


def written_list(work, shape):
    """cutlist.json over the manifest's clips: three shots with their sound kept, 5.5 seconds."""
    manifest = json.loads((work / "manifest.json").read_text(encoding="utf-8"))
    width, height = settings.SHAPES[shape]
    shots = [("A", 0.0, 2.0), ("B", 0.5, 2.5), ("A", 2.0, 3.5)]
    cutlist = {
        "version": 1,
        "canvas": {"width": width, "height": height, "fps": settings.OUTPUT_FPS},
        "clips": {
            entry["letter"]: {"file": entry["original"]["name"], "seconds": entry["working"]["seconds"]}
            for entry in manifest["clips"]
        },
        "recipe": "lively",
        "segments": [
            {"clip": clip, "from": start, "to": end, "sound": "keep", "why": f"shot {number}"}
            for number, (clip, start, end) in enumerate(shots, 1)
        ],
    }
    (work / "cutlist.json").write_text(json.dumps(cutlist, indent=2), encoding="utf-8")


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_the_follow_up_chain(shape, tmp_path, capsys, small_and_quick):
    other = OTHER[shape]
    work = tmp_path / "chain"
    (tmp_path / "sent").mkdir()
    width, height = CLIP_SIZE[shape]
    one = make_clip(tmp_path / "sent" / "one.mp4", width, height, seconds=4)
    two = make_clip(tmp_path / "sent" / "two.mp4", height, width, seconds=4)

    # 1. a reel from the first list: 5.5 seconds, 165 frames
    assert main(["normalize", "--shape", shape, "--work", str(work), "--", str(one), str(two)]) == 0
    written_list(work, shape)
    first = render_and_find(work)
    assert first.name.startswith(f"reel-{shape}-")
    assert frames(first) == 165

    # 2. "shorter": the same shots, 4.5 seconds, 135 frames
    assert main(["revise", "shorter", "--to", "4.5", "--from", "1", "--work", str(work)]) == 0
    second = work / "cutlist-2.json"
    assert second.exists()
    before = json.loads((work / "cutlist.json").read_text(encoding="utf-8"))["segments"]
    after = json.loads(second.read_text(encoding="utf-8"))["segments"]
    assert [shot["from"] for shot in after] == [shot["from"] for shot in before]
    assert [shot["clip"] for shot in after] == [shot["clip"] for shot in before]
    reel_two = render_and_find(work, str(second))
    assert frames(reel_two) == 135

    # 3. "mute it", from the newest list: still 135 frames, and silent
    assert main(["revise", "sound", "off", "--cutlist", str(second), "--work", str(work)]) == 0
    third = work / "cutlist-3.json"
    assert third.exists()
    reel_three = render_and_find(work, str(third))
    assert frames(reel_three) == 135
    assert peak_volume(reel_three) <= SILENT

    # 4. the other shape's normalize leaves every list and every reel as it was
    kept = [work / "cutlist.json", second, third, first, reel_two, reel_three]
    hashes = {path: sha256(path) for path in kept}
    assert main(["normalize", "--shape", other, "--work", str(work), "--", str(one), str(two)]) == 0
    for path in kept:
        assert path.exists(), f"{path.name} should survive a second normalize"
        assert sha256(path) == hashes[path], f"{path.name} changed"

    # 5. "a wide version" (or tall): no look, no match; canvas on the newest list, then render
    capsys.readouterr()
    assert main(["revise", "canvas", other, "--cutlist", str(third), "--work", str(work)]) == 0
    assert "ready to render" in capsys.readouterr().out
    fourth = work / "cutlist-4.json"
    assert fourth.exists()
    last = render_and_find(work, str(fourth))
    assert last.name.startswith(f"reel-{other}-")
    picture = stream(probe(last), "video")
    assert (picture["width"] > picture["height"]) == (other == "wide")
    assert frames(last) == 135
    assert peak_volume(last) <= SILENT
    assert not (tmp_path / "default-work").exists(), "the default work folder must stay untouched"
