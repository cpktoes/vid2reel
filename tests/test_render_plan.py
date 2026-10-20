"""The move windows and the photo sizing of the render plan: pure arithmetic, no FFmpeg, both shapes."""

import pytest

from v2r import settings
from v2r.render import plan

SHAPES = ["tall", "wide"]
MOVES = ["none", "push-in", "pull-out", "pan-left", "pan-right"]


def canvas_of(shape):
    return list(settings.SHAPES[shape])


def centre_of(shape):
    width, height = canvas_of(shape)
    return [width / 2, height / 2]


@pytest.mark.parametrize("shape", SHAPES)
def test_no_move_is_the_full_canvas(shape):
    width, height = canvas_of(shape)
    start, end = plan.move_windows("none", canvas_of(shape), centre_of(shape))
    assert start == end == [0, 0, width, height]


@pytest.mark.parametrize("shape", SHAPES)
def test_push_in_ends_four_percent_tighter_on_the_focus(shape):
    width, height = canvas_of(shape)
    amount = settings.MOVE_AMOUNT
    start, end = plan.move_windows("push-in", canvas_of(shape), centre_of(shape))
    assert start == [0, 0, width, height]
    assert end == pytest.approx([width * amount / 2, height * amount / 2, width * (1 - amount), height * (1 - amount)])


@pytest.mark.parametrize("shape", SHAPES)
def test_pull_out_is_push_in_reversed(shape):
    focus = [canvas_of(shape)[0] * 0.3, canvas_of(shape)[1] * 0.6]
    push = plan.move_windows("push-in", canvas_of(shape), focus)
    pull = plan.move_windows("pull-out", canvas_of(shape), focus)
    assert pull == (push[1], push[0])


@pytest.mark.parametrize("shape", SHAPES)
def test_push_in_near_an_edge_stays_inside_the_frame(shape):
    width, height = canvas_of(shape)
    _, end = plan.move_windows("push-in", canvas_of(shape), [0.0, 0.0])
    assert end[:2] == [0, 0]
    _, end = plan.move_windows("push-in", canvas_of(shape), [width, height])
    assert end[0] + end[2] == pytest.approx(width)
    assert end[1] + end[3] == pytest.approx(height)


@pytest.mark.parametrize("shape", SHAPES)
def test_pan_right_travels_the_whole_spare_room(shape):
    width, height = canvas_of(shape)
    amount = settings.MOVE_AMOUNT
    start, end = plan.move_windows("pan-right", canvas_of(shape), centre_of(shape))
    tight_w, tight_h = width * (1 - amount), height * (1 - amount)
    assert start[0] == 0
    assert end[0] == pytest.approx(width * amount)
    assert end[0] + end[2] == pytest.approx(width)  # ends on the right edge of the picture
    assert start[2:] == pytest.approx([tight_w, tight_h]) and end[2:] == pytest.approx([tight_w, tight_h])
    assert start[1] == end[1] == pytest.approx(height * amount / 2)  # centred on the focus
    # the feature moves left on the finished reel by this many pixels
    assert width * (end[0] - start[0]) / tight_w == pytest.approx(width * amount / (1 - amount))


@pytest.mark.parametrize("shape", SHAPES)
def test_pan_left_travels_the_other_way(shape):
    right = plan.move_windows("pan-right", canvas_of(shape), centre_of(shape))
    left = plan.move_windows("pan-left", canvas_of(shape), centre_of(shape))
    assert left == (right[1], right[0])


@pytest.mark.parametrize("shape", SHAPES)
def test_a_pan_keeps_its_height_inside_the_frame(shape):
    width, height = canvas_of(shape)
    for focus_y in (0.0, height):
        start, _ = plan.move_windows("pan-right", canvas_of(shape), [width / 2, focus_y])
        assert 0 <= start[1] and start[1] + start[3] <= height + 1e-9


@pytest.mark.parametrize("shape", SHAPES)
def test_moves_follow_the_setting(shape, monkeypatch):
    monkeypatch.setattr(settings, "MOVE_AMOUNT", 0.02)
    width, height = canvas_of(shape)
    _, end = plan.move_windows("push-in", canvas_of(shape), centre_of(shape))
    assert end == pytest.approx([width * 0.01, height * 0.01, width * 0.98, height * 0.98])
    start, end = plan.move_windows("pan-right", canvas_of(shape), centre_of(shape))
    assert start[2] == pytest.approx(width * 0.98)
    assert end[0] == pytest.approx(width * 0.02)


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("move", MOVES)
def test_moves_are_steady(shape, move):
    start, end = plan.move_windows(move, canvas_of(shape), centre_of(shape))
    frames = 75
    steps = [[a + (b - a) * n / (frames - 1) for a, b in zip(start, end)] for n in range(frames)]
    quarter = frames // 4  # frame 18 of 0..74 is exactly 18/74 of the way, the same for every coordinate
    for column in range(4):
        expected = start[column] + (end[column] - start[column]) * quarter / (frames - 1)
        assert steps[quarter][column] == pytest.approx(expected)
        # equal steps: the difference between neighbouring frames never changes (no easing, D-20)
        deltas = {round(steps[n + 1][column] - steps[n][column], 9) for n in range(frames - 1)}
        assert len(deltas) == 1
    assert steps[0] == pytest.approx(start) and steps[-1] == pytest.approx(end)


def manifest_with(kind, working_size, photo=None):
    entry = {
        "letter": "A", "number": 1, "status": "done", "kind": kind,
        "working": {"file": "A.mp4", "size": working_size, "fps": 30.0, "seconds": 4.0},
    }
    if photo:
        entry["photo"] = photo
    return {"clips": [entry]}


def one_segment_list(shape, **more):
    width, height = canvas_of(shape)
    segment = {"clip": "A", "from": 0.0, "to": 3.5, "sound": "off", "why": "test", **more}
    return {"canvas": {"width": width, "height": height, "fps": 30}, "segments": [segment]}


@pytest.mark.parametrize("shape", SHAPES)
def test_photo_segment_is_sized_from_its_full_size_copy(shape):
    manifest = manifest_with("photo", [1080, 1440], photo={"file": "A-photo.jpg", "size": [3024, 4032]})
    segment = plan.plan(one_segment_list(shape), manifest)["segments"][0]
    expected = plan.fill_region((3024, 4032), canvas_of(shape))
    assert segment["source_size"] == [3024, 4032]
    assert segment["crop"] == expected["crop"]
    assert segment["photo"] == "A-photo.jpg"
    assert segment["working"] == "A.mp4"


@pytest.mark.parametrize("shape", SHAPES)
def test_a_video_segment_is_sized_from_its_working_copy(shape):
    manifest = manifest_with("video", [1920, 1080])
    segment = plan.plan(one_segment_list(shape), manifest)["segments"][0]
    assert segment["source_size"] == [1920, 1080] and segment["photo"] is None


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("move", MOVES)
def test_plan_fills_the_windows_from_the_move_and_the_focus(shape, move):
    manifest = manifest_with("video", [1920, 1080])
    segment = plan.plan(one_segment_list(shape, move=move, focus_x=0.3), manifest)["segments"][0]
    region = plan.fill_region((1920, 1080), canvas_of(shape), 0.3, 0.5)
    assert segment["move"] == move
    assert (segment["window_start"], segment["window_end"]) == plan.move_windows(move, canvas_of(shape), region["focus"])


@pytest.mark.parametrize("shape", SHAPES)
def test_a_segment_with_no_move_named_has_none(shape):
    segment = plan.plan(one_segment_list(shape), manifest_with("photo", [1080, 1440], photo={
        "file": "A-photo.jpg", "size": [3024, 4032]}))["segments"][0]
    assert segment["move"] == "none"
    assert segment["window_start"] == segment["window_end"]


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("move", MOVES)
def test_a_one_frame_segment_is_the_fitted_crop(shape, move):
    width, height = canvas_of(shape)
    cutlist = one_segment_list(shape, move=move)
    cutlist["segments"][0]["to"] = 0.034
    segment = plan.plan(cutlist, manifest_with("video", [1920, 1080]))["segments"][0]
    assert segment["frames"] == 1
    assert segment["window_start"] == segment["window_end"] == [0, 0, width, height]


# ---- the numbers that were written into the code now come from settings.py (IN-03) ----


def test_a_clips_frame_benefit_is_a_setting(monkeypatch):
    assert plan.clip_frames(12.433333) == 373  # 372.99999 frames and a thousandth of a frame of benefit
    assert plan.clip_frames(12.45) == 373  # 373.5 frames: half a frame is not given
    monkeypatch.setattr(settings, "CLIP_FRAME_BENEFIT", 0.5)
    assert plan.clip_frames(12.45) == 374
    monkeypatch.setattr(settings, "CLIP_FRAME_BENEFIT", 0.0)
    assert plan.clip_frames(12.433333) == 372
