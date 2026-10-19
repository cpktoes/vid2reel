"""The slow moves and the photo pieces of render, measured on the finished reel, in both shapes.

A move that stutters is a fault only an eye can judge, so these tests follow a thin white line through every frame of
the reel and measure how smoothly it travels. Every list lasts at least 3.5 seconds.
"""

import re
import subprocess

import pytest
from cutlists import clips_block, segment, touch_up, write_list
from media import (
    TIMEOUT, filter_names, make_band_photo, make_colour_clip, make_line_clip, make_manifest, patch_yuv, probe, stream,
)

from v2r import render, settings
from v2r.render import plan, video

SHAPES = ["tall", "wide"]
MOVE = 0.04  # settings.MOVE_AMOUNT as the default list is checked against
SMOOTH = 0.6  # pixels: the largest change of speed from one frame to the next that still looks steady
RADIUS = 60  # pixels either side of where a line was that the tracker looks in (a wide pan's first frame is already 40 px off)
FLOOR = 12  # brightness (0 to 255) below which a pixel is the dark background, not the edge of a line
TRAVEL = 1.5  # pixels: how far the measured travel may differ from the plan
SECONDS = 3.5
FRAMES = 105  # SECONDS at 30 frames a second


@pytest.fixture(autouse=True)
def quick_encode(monkeypatch):
    monkeypatch.setattr(settings, "RENDER_X264_PRESET", "ultrafast")


def canvas_of(shape):
    return settings.SHAPES[shape]


def line_work(tmp_path, shape, segments, xs=None):
    """A work folder with clip A, a 4-second black clip at the canvas size with white lines at `xs`, and a list of
    `segments` over it, checked against it. Returns the work folder."""
    width, height = canvas_of(shape)
    work = tmp_path / "work"
    work.mkdir()
    make_line_clip(work / "A.mp4", width, height, 4, xs)
    manifest = make_manifest(work, shape, [work / "A.mp4"])
    write_list(work, {
        "version": 1,
        "canvas": {"width": width, "height": height, "fps": settings.OUTPUT_FPS},
        "clips": clips_block(manifest),
        "segments": segments,
    })
    return work


def moving_work(tmp_path, shape, move, xs=None, focus=None):
    return line_work(tmp_path, shape, [
        segment("A", 0.0, SECONDS, "off", f"A 00.0 to A 03.5: the line, {move}", move=move, **(focus or {}))], xs)


def line_positions(path, width, height, near):
    """Where each white line sits in every frame of the reel, one list per line, in pixels across (the line's centre,
    counting the left edge of the frame as 0).

    Each frame's middle row is read; a line's place is the brightness-weighted centroid of the pixels brighter than FLOOR
    within RADIUS pixels of where that line was in the frame before (of `near` for the first frame).
    """
    data = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-nostdin", "-i", str(path), "-vf", f"format=gray,crop={width}:1:0:{height // 2}",
         "-f", "rawvideo", "-"],
        capture_output=True, check=True, timeout=TIMEOUT,
    ).stdout
    assert len(data) % width == 0
    tracks = [[] for _ in near]
    where = [float(x) for x in near]
    for start in range(0, len(data), width):
        row = data[start:start + width]
        for number, centre in enumerate(where):
            low, high = max(0, int(centre) - RADIUS), min(width, int(centre) + RADIUS + 1)
            weight = total = 0.0
            for x in range(low, high):
                if row[x] > FLOOR:
                    weight += row[x]
                    total += row[x] * (x + 0.5)  # the middle of pixel x, so an edge is a whole number
            assert weight, f"no line near {centre:.1f}"
            where[number] = total / weight
            tracks[number].append(where[number])
    return tracks


def second_differences(track):
    return [track[n + 1] - 2 * track[n] + track[n - 1] for n in range(1, len(track) - 1)]


def render_reel(work):
    reel, _ = render.render(work / "cutlist.json", work)
    return reel


def frame_count(path):
    return int(stream(probe(path), "video")["nb_frames"])


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("move, sign", [("pan-right", -1), ("pan-left", 1)])
def test_pan_is_smooth_and_travels_as_planned(shape, move, sign, tmp_path):
    width, height = canvas_of(shape)
    reel = render_reel(moving_work(tmp_path, shape, move))
    (track,) = line_positions(reel, width, height, [width / 2])
    planned = sign * width * MOVE / (1 - MOVE)  # 45 pixels on a 1080-wide frame
    assert track[-1] - track[0] == pytest.approx(planned, abs=TRAVEL)
    assert max(abs(change) for change in second_differences(track)) <= SMOOTH
    assert frame_count(reel) == FRAMES


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("move", ["push-in", "pull-out"])
def test_push_in_moves_lines_outwards_steadily(shape, move, tmp_path):
    width, height = canvas_of(shape)
    left, right = width / 4, 3 * width / 4
    work = moving_work(tmp_path, shape, move, xs=[round(left) - 2, round(right) - 2], focus={"focus_x": 0.5, "focus_y": 0.5})
    reel = render_reel(work)
    tracks = line_positions(reel, width, height, [left, right])
    tight = (left - width * MOVE / 2) / (1 - MOVE)  # the left line once the picture is 4 percent tighter
    unmoved, moved = [left, right], [tight, width - tight]
    if move == "pull-out":
        unmoved, moved = moved, unmoved
    for track, first, last in zip(tracks, unmoved, moved):
        assert track[0] == pytest.approx(first, abs=0.5 if move == "push-in" else TRAVEL)
        assert track[-1] == pytest.approx(last, abs=TRAVEL)
        assert max(abs(change) for change in second_differences(track)) <= SMOOTH
    assert tracks[0][-1] < tracks[0][0] if move == "push-in" else tracks[0][-1] > tracks[0][0]
    assert tracks[1][-1] > tracks[1][0] if move == "push-in" else tracks[1][-1] < tracks[1][0]
    assert frame_count(reel) == FRAMES


@pytest.mark.parametrize("shape", SHAPES)
def test_one_frame_segment_is_the_fitted_crop(shape, tmp_path):
    width, height = canvas_of(shape)
    work = line_work(tmp_path, shape, [
        segment("A", 0.0, 0.034, "off", "A 00.0: one frame that asks for a push-in", move="push-in"),
        segment("A", 0.0, SECONDS, "off", "A 00.0 to A 03.5: the line, still"),
    ])
    the_plan = plan.plan(*_checked(work))
    one, still = the_plan["segments"]
    assert one["frames"] == 1 and still["frames"] == FRAMES
    command = video.piece_command(one, the_plan, work, work / "piece.mkv")
    assert "perspective" not in command[command.index("-filter_complex") + 1]

    reel = render_reel(work)
    track, = line_positions(reel, width, height, [width / 2])
    assert track[0] == pytest.approx(width / 2, abs=0.5)
    assert track[0] == pytest.approx(track[1], abs=0.5)
    assert frame_count(reel) == FRAMES + 1


def _checked(work):
    """(the cut list, the manifest) of a work folder, for plan.plan."""
    import json

    return (json.loads((work / "cutlist.json").read_text(encoding="utf-8")),
            json.loads((work / "manifest.json").read_text(encoding="utf-8")))


def limited_yuv(red, green, blue):
    """The BT.709 limited-range (Y, U, V) code values of an sRGB colour, the standard formula."""
    r, g, b = red / 255, green / 255, blue / 255
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return (16 + 219 * y, 128 + 224 * (b - y) / 1.8556, 128 + 224 * (r - y) / 1.5748)


PHOTO_COLOURS = [(200, 40, 40), (40, 200, 40), (40, 40, 200)]
STILL_SIZE = {"tall": (1080, 1920), "wide": (1920, 2560)}  # a photo's still clip is the upright size of its job


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("move", ["none", "push-in"])
def test_photo_is_built_from_its_full_size_copy(shape, move, tmp_path):
    width, height = canvas_of(shape)
    work = tmp_path / "work"
    work.mkdir()
    make_band_photo(work / "A-photo.jpg", 3000, 4000, PHOTO_COLOURS)
    make_colour_clip(work / "A.mp4", *STILL_SIZE[shape], 4, (128, 128, 128))  # a grey stand-in for the 4-second still
    manifest = make_manifest(work, shape, [
        {"file": work / "A.mp4", "kind": "photo", "photo": {"file": "A-photo.jpg", "size": [3000, 4000]}}])
    write_list(work, {
        "version": 1,
        "canvas": {"width": width, "height": height, "fps": settings.OUTPUT_FPS},
        "clips": clips_block(manifest),
        "segments": [segment("A", 0.0, SECONDS, "off", f"A: the photo, {move}", move=move)],
    })
    reel = render_reel(work)

    expected = limited_yuv(*PHOTO_COLOURS[1])  # the middle band is at the centre of the frame
    assert abs(expected[1] - 128) > 20 or abs(expected[2] - 128) > 20
    for frame in (0, FRAMES - 1):
        found = patch_yuv(reel, frame, (width - 40) // 2, (height - 40) // 2)
        assert found == pytest.approx(expected, abs=4), f"frame {frame}"
        assert max(abs(found[1] - 128), abs(found[2] - 128)) > 20  # nowhere near the grey stand-in
    assert frame_count(reel) == FRAMES


@pytest.mark.parametrize("shape", SHAPES)
def test_piece_commands_use_only_listed_filters(shape, tmp_path):
    width, height = canvas_of(shape)
    work = tmp_path / "work"
    work.mkdir()
    make_line_clip(work / "A.mp4", width, height, 4)
    make_band_photo(work / "B-photo.jpg", 3000, 4000, PHOTO_COLOURS)
    make_colour_clip(work / "B.mp4", *STILL_SIZE[shape], 4)
    manifest = make_manifest(work, shape, [
        work / "A.mp4", {"file": work / "B.mp4", "kind": "photo", "photo": {"file": "B-photo.jpg", "size": [3000, 4000]}}])
    moves = ["none", "push-in", "pull-out", "pan-left", "pan-right"]
    cutlist = {
        "version": 1,
        "canvas": {"width": width, "height": height, "fps": settings.OUTPUT_FPS},
        "clips": clips_block(manifest),
        "segments": [segment(letter, 0.0, SECONDS, "off", f"{letter}: {move}", move=move)
                     for letter in "AB" for move in moves],
        "look": {"filter": "none", "touch_up": {"A": touch_up(6, -2, 3, 1.05), "B": touch_up(-4.5, 1, -1, 0.95)}},
    }
    the_plan = plan.plan(cutlist, manifest)
    for one in the_plan["segments"]:
        command = video.piece_command(one, the_plan, work, work / "piece.mkv")
        graph = command[command.index("-filter_complex") + 1]
        # the colour step's expressions hold commas inside quotes; only the filter names outside them are listed
        names = filter_names(re.sub(r"'[^']*'", "", graph))
        assert set(names) <= set(render.RENDER_FILTERS), graph
        assert command.count("-i") == 1
        assert ("perspective" in names) == (one["move"] != "none")
        assert names.count("lutyuv") == 1
        if one["kind"] == "photo":
            assert command[command.index("-framerate") + 1] == "30"
            assert command[command.index("-frames:v") + 1] == str(FRAMES)
            assert command[command.index("-i") + 1] == str((work / "B-photo.jpg").resolve())


def test_perspective_filter_is_the_move_in_eight_straight_lines():
    text = video.perspective_filter([0, 0, 1080, 1920], [21.6, 38.4, 1036.8, 1843.2], 75)
    assert text.startswith("perspective=x0='(0.000000+(21.600000)*in/74)':y0='(0.000000+(38.400000)*in/74)'")
    assert "x3='(1080.000000+(-21.600000)*in/74)'" in text
    assert text.endswith(":sense=source:eval=frame:interpolation=cubic")
    assert sum(text.count(f"{axis}{n}='") for axis in "xy" for n in range(4)) == 8


def test_no_move_and_one_frame_give_no_filter():
    assert video.perspective_filter([0, 0, 1080, 1920], [0, 0, 1080, 1920], 75) == ""
    assert video.perspective_filter([0, 0, 1080, 1920], [21.6, 38.4, 1036.8, 1843.2], 1) == ""


def test_a_photo_that_is_not_a_plain_file_in_the_work_folder_is_refused(tmp_path):
    for name in ("../A-photo.jpg", "sub/A-photo.jpg", "", None):
        with pytest.raises(ValueError, match="full-size copy of photo A is missing"):
            video.photo_path({"clip": "A", "photo": name}, tmp_path)


# ---- the touch-up: exactly the list's numbers, and nothing else to colour ----

TOUCH = (6, -2, 3, 1.05)  # brightness, blue, red, saturation
FLAT = (100, 120, 140)  # the (Y, U, V) of the flat test clip
SMALL = {"tall": (360, 640), "wide": (640, 360)}  # the colour tests measure flat patches, not the frame size


@pytest.fixture
def small_canvas(monkeypatch):
    monkeypatch.setattr(settings, "SHAPES", SMALL)


def expected_yuv(base, numbers):
    """What the touch-up numbers do to a (Y, U, V) patch, worked out by hand and rounded."""
    brightness, blue, red, saturation = numbers
    return (base[0] + brightness,
            128 + (base[1] - 128) * saturation + blue,
            128 + (base[2] - 128) * saturation + red)


def flat_work(tmp_path, shape, colours, touch_ups, segments):
    """A work folder with one flat colour clip per (Y, U, V) in `colours` (letters A, B...), each 3 seconds long, and
    a list of `segments` (lasting 3.5 seconds or more) with the given touch-up records ({} for no look block)."""
    width, height = SMALL[shape]
    work = tmp_path / "work"
    work.mkdir()
    for number, yuv in enumerate(colours):
        make_colour_clip(work / f"{chr(65 + number)}.mp4", width, height, 4 if len(colours) == 1 else 3, yuv)
    manifest = make_manifest(work, shape, [work / f"{chr(65 + number)}.mp4" for number in range(len(colours))])
    data = {
        "version": 1,
        "canvas": {"width": width, "height": height, "fps": settings.OUTPUT_FPS},
        "clips": clips_block(manifest),
        "segments": segments,
    }
    if touch_ups is not None:
        data["look"] = {"filter": "none", "touch_up": touch_ups}
    write_list(work, data)
    return work


def centre_yuv(path, shape, frame=10):
    width, height = SMALL[shape]
    return patch_yuv(path, frame, (width - 40) // 2, (height - 40) // 2)


def test_touch_up_filter_is_the_numbers_and_the_limits():
    text = video.touch_up_filter(touch_up(*TOUCH))
    assert text.startswith("lutyuv=y='clip(round(val+(6.000000)),16,235)'")
    assert "u='clip(round(128+(val-128)*1.050000+(-2.000000)),16,240)'" in text
    assert "v='clip(round(128+(val-128)*1.050000+(3.000000)),16,240)'" in text


@pytest.mark.parametrize("record", [None, {}, touch_up(0, 0, 0, 1), touch_up(0.0, -0.0, 0.0, 1.0)])
def test_neutral_record_builds_no_colour_filter(record):
    assert video.touch_up_filter(record) == ""


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("record", [None, touch_up(0, 0, 0, 1)])
def test_no_colour_filter_in_a_chain_without_numbers(shape, record, tmp_path, small_canvas):
    work = flat_work(tmp_path, shape, [FLAT], {"A": record} if record else None,
                     [segment("A", 0.0, SECONDS, "off", "A: flat")])
    the_plan = plan.plan(*_checked(work))
    (one,) = the_plan["segments"]
    assert "lutyuv" not in video.video_chain(one, the_plan)


@pytest.mark.parametrize("shape", SHAPES)
def test_touch_up_applies_exactly_the_numbers(shape, tmp_path, small_canvas):
    work = flat_work(tmp_path, shape, [FLAT], {"A": touch_up(*TOUCH)}, [segment("A", 0.0, SECONDS, "off", "A: flat")])
    found = centre_yuv(render_reel(work), shape)
    assert found == pytest.approx((106, 118, 144), abs=1)
    assert found == pytest.approx(expected_yuv(FLAT, TOUCH), abs=1)


@pytest.mark.parametrize("shape", SHAPES)
def test_no_touch_up_leaves_colour_alone(shape, tmp_path, small_canvas):
    work = flat_work(tmp_path, shape, [FLAT], None, [segment("A", 0.0, SECONDS, "off", "A: flat")])
    assert centre_yuv(render_reel(work), shape) == pytest.approx(FLAT, abs=1)


@pytest.mark.parametrize("shape", SHAPES)
def test_touch_up_rounds_not_truncates(shape, tmp_path, monkeypatch, small_canvas):
    monkeypatch.setattr(settings, "RENDER_PIECE_CRF", 0)
    work = flat_work(tmp_path, shape, [(176, 128, 128)], {"A": touch_up(5.96, 0, 0, 1)},
                     [segment("A", 0.0, SECONDS, "off", "A: flat")])
    the_plan = plan.plan(*_checked(work))
    (one,) = the_plan["segments"]
    piece = work / "piece.mkv"
    subprocess.run(video.piece_command(one, the_plan, work, piece), check=True, timeout=TIMEOUT)
    assert centre_yuv(piece, shape) == (182, 128, 128)  # 181.96 is 182, not the truncated 181


@pytest.mark.parametrize("shape", SHAPES)
def test_touch_up_stays_in_the_legal_range(shape, tmp_path, small_canvas):
    work = flat_work(tmp_path, shape, [(233, 238, 18)], {"A": touch_up(8, 4, -4, 1.08)},
                     [segment("A", 0.0, SECONDS, "off", "A: flat")])
    found = centre_yuv(render_reel(work), shape)
    assert found == pytest.approx((235, 240, 16), abs=1)


@pytest.mark.parametrize("shape", SHAPES)
def test_each_clip_gets_its_own_numbers(shape, tmp_path, small_canvas):
    other = (180, 110, 150)
    records = {"A": touch_up(*TOUCH), "B": touch_up(-8, 4, -4, 0.92)}
    work = flat_work(tmp_path, shape, [FLAT, other], records, [
        segment("A", 0.0, 2.0, "off", "A: flat"), segment("B", 0.0, 2.0, "off", "B: flat")])
    reel = render_reel(work)
    first, second = centre_yuv(reel, shape, 10), centre_yuv(reel, shape, 70)
    assert first == pytest.approx(expected_yuv(FLAT, TOUCH), abs=1)
    assert second == pytest.approx(expected_yuv(other, (-8, 4, -4, 0.92)), abs=1)
    assert first != pytest.approx(second, abs=5)


@pytest.mark.parametrize("shape", SHAPES)
def test_touch_up_on_a_photo(shape, tmp_path, small_canvas):
    width, height = SMALL[shape]
    work = tmp_path / "work"
    work.mkdir()
    make_band_photo(work / "A-photo.jpg", 600, 800, PHOTO_COLOURS)
    make_colour_clip(work / "A.mp4", *(360, 640) if shape == "tall" else (640, 1138), 4, (128, 128, 128))
    manifest = make_manifest(work, shape, [
        {"file": work / "A.mp4", "kind": "photo", "photo": {"file": "A-photo.jpg", "size": [600, 800]}}])

    def reel_with(records):
        data = {
            "version": 1,
            "canvas": {"width": width, "height": height, "fps": settings.OUTPUT_FPS},
            "clips": clips_block(manifest),
            "segments": [segment("A", 0.0, SECONDS, "off", "A: the photo")],
        }
        if records:
            data["look"] = {"filter": "none", "touch_up": records}
        write_list(work, data)
        return render_reel(work)

    plain = centre_yuv(reel_with(None), shape)
    touched = centre_yuv(reel_with({"A": touch_up(*TOUCH)}), shape)
    assert max(abs(plain[1] - 128), abs(plain[2] - 128)) > 20  # a real colour, so the saturation shows
    assert touched == pytest.approx(expected_yuv(plain, TOUCH), abs=1.5)
