"""Render's finished outputs and golden renders, in both shapes, from clips generated in tmp_path.

The cover still, the size limit and failure safety are tested first; the golden renders of the two approved example
lists come after them. Nothing here is committed footage, and no md5 or hash is written into this file: encoders are
not byte-identical between machines, so the contract that holds everywhere is the colour and the luma that each frame
of the reel must decode to, computed in the test from the clip it was cut from. The "same video" tests compare the
decoded pictures and sound of two runs on the same machine (FFmpeg's md5 of the decoded streams), never the file bytes.
"""

import copy
import json
import math
import re
import subprocess
from types import SimpleNamespace

import pytest
from cutlists import CLIP_PLAN, clips_block, placeholder_work, scaled, segment, tall_example, wide_example, write_list
from media import (
    index_luma,
    make_band_photo,
    make_colour_clip,
    make_index_clip,
    make_manifest,
    make_split_clip,
    mp4_boxes,
    patch_yuv,
    probe,
    sha256,
    stream,
)

from v2r import join, render, settings
from v2r.__main__ import main
from v2r.render import plan, proof, sound, video

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


# ---- golden renders of the two approved examples, at a quarter of their length ----

QUARTER = 0.25
TIMEOUT = 120  # seconds: a hung FFmpeg fails one test instead of the whole suite
COLOUR_TOLERANCE = 2  # code values, on a colour worked out by hand
LUMA_TOLERANCE = 2  # code values; the index clip steps 8 a frame, so a frame one too early or too late is 6 outside it
LEFT = (90, 150, 110)  # (Y, U, V) of the left (or top) half of a split clip
RIGHT = (170, 100, 170)  # (Y, U, V) of the right (or bottom) half
FLAT_C = (140, 110, 150)
FLAT_D = (120, 140, 100)
GREY = (128, 128, 128)  # the stand-in clip of a photo: a colour no segment of a photo may show
BANDS = [(200, 40, 40), (40, 200, 40), (40, 40, 200)]  # a photo's bands; the middle one is at the centre of the frame
PHOTO_SIZE = [3000, 4000]
LOUDNESS_WANTED = -14.0
LOUDNESS_TOLERANCE = 0.3  # LU


def limited_yuv(red, green, blue):
    """The BT.709 limited-range (Y, U, V) code values of an sRGB colour, the standard formula."""
    r, g, b = red / 255, green / 255, blue / 255
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return (16 + 219 * y, 128 + 224 * (b - y) / 1.8556, 128 + 224 * (r - y) / 1.5748)


def round_away(x):
    """Round half away from zero, the way FFmpeg's expression round() does (all values here are positive)."""
    return math.floor(x + 0.5)


def expected_colour(source_yuv, record):
    """The (Y, U, V) a touch-up record makes of a source colour: Y + b, and 128 + (C - 128) x s + offset, rounded half
    away from zero and held inside the legal video range. Worked out here, apart from v2r's own code."""
    if not record:
        return tuple(source_yuv)
    y, u, v = source_yuv
    return (
        min(235, max(16, round_away(y + record["brightness"]))),
        min(240, max(16, round_away(128 + (u - 128) * record["saturation"] + record["blue"]))),
        min(240, max(16, round_away(128 + (v - 128) * record["saturation"] + record["red"]))),
    )


def golden_work(tmp_path, shape):
    """A work folder of generated working copies for the shape's example, and the example at a quarter of its length.

    Each clip of CLIP_PLAN is made a quarter as long as the plan says, at a small size in its own orientation (360x640
    upright, 640x360 sideways): the tall job's A is a frame-index clip, B a split clip (left and right), C and D flat
    colours (D with a beep throughout, for its kept laugh) and E a band photo of 3000x4000 with a grey stand-in; the
    wide job's A is a frame-index clip with a beep throughout, B a split clip (top and bottom) and C a band photo.
    Returns (work folder, the cut list written as cutlist.json, the manifest, what each letter is made of).
    """
    work = tmp_path / "work"
    work.mkdir()
    upright, sideways = (360, 640), (640, 360)
    sources, entries = {}, []
    for letter, kind, orientation, seconds, _ in CLIP_PLAN[shape]:
        path = work / f"{letter}.mp4"
        seconds = seconds * QUARTER
        size = upright if orientation == "upright" else sideways
        entry = {"file": path, "kind": kind}
        if kind == "photo":
            make_colour_clip(path, *upright, 4, GREY)  # the stand-in still, 4 seconds as the list says
            make_band_photo(work / f"{letter}-photo.jpg", *PHOTO_SIZE, BANDS)
            entry["photo"] = {"file": f"{letter}-photo.jpg", "size": PHOTO_SIZE}
            sources[letter] = ("photo", limited_yuv(*BANDS[1]))
        elif letter == "A":
            make_index_clip(path, *size, seconds, beep=(0, 100) if shape == "wide" else None)
            sources[letter] = ("index", None)
        elif letter == "B":
            direction = "across" if shape == "tall" else "down"
            make_split_clip(path, *size, seconds, LEFT, RIGHT, direction)
            sources[letter] = ("split", direction)
        else:
            colour = FLAT_C if letter == "C" else FLAT_D
            make_colour_clip(path, *size, seconds, colour, beep=(0, 100) if letter == "D" else None)
            sources[letter] = ("flat", colour)
        entries.append(entry)
    manifest = make_manifest(work, shape, entries)
    cutlist = scaled(EXAMPLES[shape](clips_block(manifest)), QUARTER)
    write_list(work, cutlist)
    return work, cutlist, manifest, sources


EXAMPLES = {"tall": tall_example, "wide": wide_example}


def expected_segments(cutlist):
    """For each segment of the scaled list: (number, clip letter, source frame of its first picture, frames, reel frame
    of its first picture), worked out with plan.frames from the list alone."""
    rows, reel_start = [], 0
    for number, item in enumerate(cutlist["segments"], start=1):
        first, count = plan.frames(item["from"]), plan.frames(item["to"] - item["from"])
        rows.append((number, item["clip"], first, count, reel_start))
        reel_start += count
    return rows


def expected_at(cutlist, sources, letter, item, source_frame):
    """The (Y, U, V) the centre of a segment must show at one of its frames, before and after the touch-up."""
    kind, detail = sources[letter]
    if kind == "index":
        base = (index_luma(source_frame), 128, 128)
    elif kind == "flat":
        base = detail
    elif kind == "photo":
        base = detail
    else:  # a split clip: the focus point picks the half the centre of the frame lands on
        focus = item.get("focus_x", 0.5) if detail == "across" else item.get("focus_y", 0.5)
        base = LEFT if focus < 0.5 else RIGHT
    record = (cutlist.get("look") or {}).get("touch_up", {}).get(letter)
    return expected_colour(base, record)


def centre(width, height):
    return (width - 40) // 2, (height - 40) // 2


def decoded_md5(path, kind):
    """FFmpeg's md5 of the decoded pictures ("v") or decoded sound ("a") of a file: the same video, not the same bytes."""
    out = subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(path), "-map", f"0:{kind}", "-f", "md5", "-"],
        capture_output=True, text=True, check=True, timeout=TIMEOUT).stdout
    return re.search(r"MD5=([0-9a-f]+)", out).group(1)


def integrated_loudness(path):
    """The integrated loudness, in LUFS, of a file's sound, read by ebur128."""
    err = subprocess.run(
        ["ffmpeg", "-nostdin", "-i", str(path), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, check=True, timeout=TIMEOUT).stderr
    return float(re.search(r"I:\s+(\S+) LUFS", err[err.rindex("Summary:"):]).group(1))


@pytest.fixture(scope="module", params=SHAPES)
def golden(request, tmp_path_factory):
    """One example in one shape, built and rendered once for all the tests of this module."""
    shape = request.param
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(settings, "RENDER_X264_PRESET", "ultrafast")
        work, cutlist, manifest, sources = golden_work(tmp_path_factory.mktemp(f"golden-{shape}"), shape)
        reel, sentences = render.render(work / "cutlist.json", work)
    return SimpleNamespace(shape=shape, work=work, cutlist=cutlist, manifest=manifest, sources=sources, reel=reel,
                           sentences=sentences)


def test_golden_render(golden, capsys):
    shape, work, cutlist, reel = golden.shape, golden.work, golden.cutlist, golden.reel
    assert main(["check", "--work", str(work)]) == 0
    assert "ready to render" in capsys.readouterr().out

    rows = expected_segments(cutlist)
    total = sum(count for _, _, _, count, _ in rows)
    assert total == {"tall": 153, "wide": 286}[shape]  # each shot's length rounds to whole frames on its own (D-01)
    width, height = settings.SHAPES[shape]
    info = probe(reel)
    picture, audio = stream(info, "video"), stream(info, "audio")
    assert picture["nb_frames"] == str(total)
    assert float(info["format"]["duration"]) == pytest.approx(total / 30, abs=0.05)
    assert (picture["width"], picture["height"]) == (width, height)
    assert picture["r_frame_rate"] == "30/1"
    assert (picture["codec_name"], audio["codec_name"]) == ("h264", "aac")
    boxes = mp4_boxes(reel)
    assert boxes.index("moov") < boxes.index("mdat")
    assert reel.stat().st_size <= settings.MAX_RESULT_BYTES
    assert integrated_loudness(reel) == pytest.approx(LOUDNESS_WANTED, abs=LOUDNESS_TOLERANCE)

    sheets = sorted(path.name for path in (work / "proof").iterdir())
    assert len(sheets) == math.ceil(2 * len(rows) / 12)
    assert sheets == [f"proof-{number:02d}.jpg" for number in range(1, len(sheets) + 1)]
    cover = reel.with_name(f"{reel.stem}-cover.jpg")
    assert cover.is_file()

    x, y = centre(width, height)
    for number, letter, first, count, reel_start in rows:
        item = cutlist["segments"][number - 1]
        middle = count // 2
        found = patch_yuv(reel, reel_start + middle, x, y)
        wanted = expected_at(cutlist, golden.sources, letter, item, first + middle)
        assert found == pytest.approx(wanted, abs=COLOUR_TOLERANCE), f"shot {number} ({letter}) at its middle frame"
        if golden.sources[letter][0] == "index":
            for place in (0, count - 1):  # the first and the last picture of the shot are its exact first and last
                found = patch_yuv(reel, reel_start + place, x, y)
                wanted = expected_at(cutlist, golden.sources, letter, item, first + place)
                assert found[0] == pytest.approx(wanted[0], abs=LUMA_TOLERANCE), f"shot {number} frame {place}"
                assert index_luma(first + place) != index_luma(first + place + 1)  # a one-frame slip reads 8 away


def test_split_clips_follow_their_focus(golden):
    """The split clip's half that a shot shows is the one its focus point picks (a tall shot looks left of B's middle
    at 0.35 and right of it at 0.6; the wide shot looks at the top of its upright clip)."""
    width, height = settings.SHAPES[golden.shape]
    x, y = centre(width, height)
    rows = {number: (letter, first, count, start) for number, letter, first, count, start in expected_segments(golden.cutlist)}
    record = golden.cutlist["look"]["touch_up"]["B"]
    if golden.shape == "tall":
        wanted = {2: expected_colour(LEFT, record), 7: expected_colour(RIGHT, record)}
    else:
        wanted = {2: expected_colour(LEFT, record)}
    for number, colour in wanted.items():
        letter, _, count, start = rows[number]
        assert letter == "B"
        assert patch_yuv(golden.reel, start + count // 2, x, y) == pytest.approx(colour, abs=COLOUR_TOLERANCE)
    assert expected_colour(LEFT, record) != pytest.approx(expected_colour(RIGHT, record), abs=10)


def test_same_list_same_video(golden, tmp_path):
    work, cutlist, manifest = golden.work, golden.cutlist, golden.manifest
    again, _ = render.render(work / "cutlist.json", work)
    assert again != golden.reel
    for kind in ("v", "a"):
        assert decoded_md5(again, kind) == decoded_md5(golden.reel, kind), f"decoded {kind}"

    # the plan and every command built from it are equal as data, which is what holds from one machine to another
    first, second = plan.plan(cutlist, manifest), plan.plan(copy.deepcopy(cutlist), copy.deepcopy(manifest))
    assert first == second
    out = tmp_path / "out"
    for one, other in zip(first["segments"], second["segments"], strict=True):
        assert video.piece_command(one, first, work, out) == video.piece_command(other, second, work, out)
    assert sound.mix_command(first, work, out) == sound.mix_command(second, work, out)
    fitted = join.fit(golden.shape, first["seconds"])
    assert (video.final_command(out, out, fitted, -3.0, out, canvas=first["canvas"])
            == video.final_command(out, out, fitted, -3.0, out, canvas=second["canvas"]))


@pytest.mark.parametrize("shape", SHAPES)
def test_times_inside_one_frame_plan_the_same_video(shape, tmp_path):
    work, manifest = placeholder_work(tmp_path, shape)
    cutlist = EXAMPLES[shape](clips_block(manifest))
    nudged = copy.deepcopy(cutlist)
    nudged["segments"][1]["to"] = round(nudged["segments"][1]["to"] + 0.01, 3)  # 2.5 seconds written as 2.51: same frames
    assert nudged["segments"][1]["to"] != cutlist["segments"][1]["to"]

    one, other = plan.plan(cutlist, manifest), plan.plan(nudged, manifest)
    assert one == other
    out = work / "out"
    for first, second in zip(one["segments"], other["segments"], strict=True):
        assert video.piece_command(first, one, work, out) == video.piece_command(second, other, work, out)
    assert sound.mix_command(one, work, out) == sound.mix_command(other, work, out)


@pytest.mark.parametrize("shape", SHAPES)
def test_one_segment_list_renders_the_same_twice(shape, tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    make_index_clip(work / "A.mp4", *CLIP_SIZE[shape], 4)
    manifest = make_manifest(work, shape, [work / "A.mp4"])
    width, height = settings.SHAPES[shape]
    write_list(work, {
        "version": 1,
        "canvas": {"width": width, "height": height, "fps": settings.OUTPUT_FPS},
        "clips": clips_block(manifest),
        "segments": [segment("A", 0.0, 3.5, "keep", "the whole of the shot")],
    })

    first, _ = render.render(work / "cutlist.json", work)
    second, _ = render.render(work / "cutlist.json", work)

    assert stream(probe(first), "video")["nb_frames"] == "105"
    for kind in ("v", "a"):
        assert decoded_md5(first, kind) == decoded_md5(second, kind), f"decoded {kind}"
