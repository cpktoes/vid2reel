"""Render's finished outputs and golden renders, in both shapes, from clips generated in tmp_path.

The cover still, the size limit and failure safety are tested first; the golden renders of the two approved example
lists come after them. Nothing here is committed footage, and no md5 or hash is written into this file: encoders are
not byte-identical between machines, so the contract that holds everywhere is the colour and the luma that each frame
of the reel must decode to, computed in the test from the clip it was cut from. The "same video" tests compare the
decoded pictures and sound of two runs on the same machine (FFmpeg's md5 of the decoded streams), never the file bytes.
"""

import json
import subprocess

import pytest
from cutlists import clips_block, placeholder_work, segment, tall_example, wide_example
from media import make_colour_clip, make_manifest, probe, sha256, stream

from v2r import join, settings
from v2r.__main__ import main
from v2r.render import plan, proof

SHAPES = ["tall", "wide"]
CLIP_SIZE = {"tall": (360, 640), "wide": (640, 360)}  # the job's own orientation, small, as a working copy would be
RED = (100, 100, 200)  # (Y, U, V): a red-leaning colour
BLUE = (100, 200, 100)  # (Y, U, V): a blue-leaning colour


@pytest.fixture(autouse=True)
def quick_encode(monkeypatch):
    monkeypatch.setattr(settings, "RENDER_X264_PRESET", "ultrafast")


def colour_work(tmp_path, shape, each=2.0, cover=None, clip_seconds=3):
    """A work folder with a red-leaning clip A and a blue-leaning clip B and a list of `each` seconds from each.

    The list lasts 2 x `each` seconds (4.0 by default, above the shortest reel render allows). Returns the work folder.
    """
    work = tmp_path / "work"
    work.mkdir()
    make_colour_clip(work / "A.mp4", *CLIP_SIZE[shape], clip_seconds, RED)
    make_colour_clip(work / "B.mp4", *CLIP_SIZE[shape], clip_seconds, BLUE)
    manifest = make_manifest(work, shape, [work / "A.mp4", work / "B.mp4"])
    width, height = settings.SHAPES[shape]
    cutlist = {
        "version": 1,
        "canvas": {"width": width, "height": height, "fps": settings.OUTPUT_FPS},
        "clips": {
            entry["letter"]: {"file": entry["original"]["name"], "seconds": entry["working"]["seconds"]}
            for entry in manifest["clips"]
        },
        "segments": [
            segment("A", 0.0, each, "off", "the red-leaning clip"),
            segment("B", 0.0, each, "off", "the blue-leaning clip"),
        ],
    }
    if cover:
        cutlist["cover"] = cover
    (work / "cutlist.json").write_text(json.dumps(cutlist, indent=2), encoding="utf-8")
    return work


def listing(work):
    """Every file and folder under the work folder, by relative name."""
    return sorted(str(path.relative_to(work)) for path in work.rglob("*"))


def the_reel(work, shape):
    (reel,) = work.glob(f"reel-{shape}-*.mp4")
    return reel


def the_cover(reel):
    cover = reel.with_name(f"{reel.stem}-cover.jpg")
    assert cover.is_file(), f"no cover beside {reel.name}"
    return cover


def centre_leaning(path):
    """(red, blue) of the middle of a picture file, 0-255, read by Pillow, and the picture's size."""
    from PIL import Image

    with Image.open(path) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        red, _, blue = rgb.getpixel((width // 2, height // 2))
    return red, blue, (width, height)


def reel_size(reel):
    picture = stream(probe(reel), "video")
    return picture["width"], picture["height"]


@pytest.mark.parametrize("shape", SHAPES)
def test_cover_default_is_the_first_frame(shape, tmp_path, capsys):
    work = colour_work(tmp_path, shape)

    assert main(["render", "--work", str(work)]) == 0
    out = capsys.readouterr().out

    reel = the_reel(work, shape)
    red, blue, size = centre_leaning(the_cover(reel))
    assert red > blue + 50, "the first shot is red-leaning, so the cover is"
    assert size == tuple(settings.SHAPES[shape]) == reel_size(reel)
    assert f"The cover still is {reel.stem}-cover.jpg, the frame at 0.0 seconds." in out


@pytest.mark.parametrize("shape", SHAPES)
def test_cover_follows_its_segment(shape, tmp_path, capsys):
    work = colour_work(tmp_path, shape, cover={"segment": 2, "at": 0.5})

    assert main(["render", "--work", str(work)]) == 0
    out = capsys.readouterr().out

    reel = the_reel(work, shape)
    red, blue, size = centre_leaning(the_cover(reel))
    assert blue > red + 50, "shot 2 is blue-leaning, so the cover is"
    assert size == reel_size(reel)
    assert "the frame at 2.5 seconds." in out  # shot 2 starts at 2.0 seconds; the cover is 0.5 seconds in


def test_cover_frame_clamps_to_the_last_frame():
    segments = [{"reel_start": 0, "frames": 75}, {"reel_start": 75, "frames": 60}]
    assert plan.cover_frame({}, segments) == 0
    assert plan.cover_frame({"cover": {"segment": 1, "at": 2.49}}, segments) == 74  # 2.49 s rounds to frame 75, past the end
    assert plan.cover_frame({"cover": {"segment": 2, "at": 1.0}}, segments) == 105
    assert plan.cover_frame({"cover": {"segment": 2, "at": 0.0}}, segments) == 75


@pytest.mark.parametrize("shape", SHAPES)
def test_the_plan_carries_the_cover_frame(shape, tmp_path):
    work, manifest = placeholder_work(tmp_path, shape)
    cutlist = {"tall": tall_example, "wide": wide_example}[shape](clips_block(manifest))
    built = plan.plan(cutlist, manifest)
    if shape == "tall":  # the cover is shot 4, one second in: shots 1 to 3 are 90, 75 and 90 frames
        assert built["cover_frame"] == 90 + 75 + 90 + 30
    else:
        assert built["cover_frame"] == 0


@pytest.mark.parametrize("shape", SHAPES)
def test_long_reel_steps_down_and_says_so(shape, tmp_path, capsys, monkeypatch):
    work = colour_work(tmp_path, shape, each=2.5)
    monkeypatch.setattr(settings, "MAX_RESULT_BYTES", 1_500_000)
    sizes = []
    real_proof = proof.make_proof

    def spy(reel, the_plan, size, work_dir):
        sizes.append(tuple(size))
        return real_proof(reel, the_plan, size, work_dir)

    monkeypatch.setattr(proof, "make_proof", spy)

    assert main(["render", "--work", str(work)]) == 0
    out = capsys.readouterr().out

    smaller = {"tall": (720, 1280), "wide": (1280, 720)}[shape]
    full = tuple(settings.SHAPES[shape])
    reel = the_reel(work, shape)
    assert reel_size(reel) == smaller
    assert reel.stat().st_size <= 1_500_000
    assert f"so it was made at {smaller[0]}x{smaller[1]} instead of {full[0]}x{full[1]}" in out
    assert centre_leaning(the_cover(reel))[2] == smaller
    assert sizes == [smaller]


@pytest.mark.parametrize("shape", SHAPES)
def test_too_long_is_refused_before_building(shape, tmp_path, capsys, monkeypatch):
    work = colour_work(tmp_path, shape, each=2.5)
    monkeypatch.setattr(settings, "MAX_RESULT_BYTES", 100_000)
    before = listing(work)

    assert main(["render", "--work", str(work)]) == 1
    out = capsys.readouterr().out

    assert f"A {shape} video can be at most" in out
    assert "so nothing was built" in out
    assert listing(work) == before


@pytest.mark.parametrize("shape", SHAPES)
def test_a_reel_over_the_limit_is_deleted(shape, tmp_path, capsys, monkeypatch):
    work = colour_work(tmp_path, shape)
    width, height = settings.SHAPES[shape]
    monkeypatch.setattr(settings, "MAX_RESULT_BYTES", 20_000)
    monkeypatch.setattr(join, "fit", lambda shape_name, seconds: (width, height, 2_500_000))  # allows far more than 20 kB
    before = listing(work)

    assert main(["render", "--work", str(work)]) == 1
    err = capsys.readouterr().err

    assert "over the 0 MiB limit, so it was deleted." in err
    assert listing(work) == before


@pytest.mark.parametrize("shape", SHAPES)
def test_failure_leaves_nothing_behind(shape, tmp_path, capsys, monkeypatch):
    work = colour_work(tmp_path, shape)
    assert main(["render", "--work", str(work)]) == 0
    capsys.readouterr()
    first = the_reel(work, shape)
    kept = {
        path.relative_to(work): sha256(path)
        for path in [first, the_cover(first), *sorted((work / "proof").iterdir())]
    }
    before = listing(work)

    real_run = subprocess.run

    def failing(command, *args, **kwargs):
        if isinstance(command, list) and any("piece-002" in str(word) for word in command):
            raise subprocess.CalledProcessError(1, command, stderr="boom")
        return real_run(command, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", failing)
    assert main(["render", "--work", str(work)]) == 1
    monkeypatch.undo()

    assert "FFmpeg failed while building shot 2" in capsys.readouterr().err
    assert listing(work) == before
    assert {name: sha256(work / name) for name in kept} == kept
    assert not [path for path in work.iterdir() if path.name.startswith(".v2r-render-") or ".part" in path.name]


@pytest.mark.parametrize("shape", SHAPES)
def test_success_leaves_only_the_expected_files(shape, tmp_path, capsys):
    work = colour_work(tmp_path, shape)

    assert main(["render", "--work", str(work)]) == 0

    reel = the_reel(work, shape)
    assert sorted(path.name for path in work.iterdir()) == sorted(
        ["A.mp4", "B.mp4", "manifest.json", "cutlist.json", reel.name, f"{reel.stem}-cover.jpg", "proof"])
    assert sorted(path.name for path in (work / "proof").iterdir()) == ["proof-01.jpg"]
    assert not [path for path in work.rglob("*") if ".part" in path.name or path.name.startswith(".v2r-render-")]
