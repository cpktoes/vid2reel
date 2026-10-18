import functools

import pytest
from media import filter_names, make_look_clip, make_manifest

from v2r import doctor
from v2r.look import measure

CLIP_SIZE = {"tall": (360, 640), "wide": (640, 360)}  # the clip sizes swap with the shape


@functools.cache
def real_filters():
    return frozenset(doctor.ffmpeg_names("-filters"))


def measured(tmp_path, shape, pattern, have=None, **options):
    """Make a look test clip in `tmp_path` and measure it directly; returns measure_clip's dict."""
    work = tmp_path / "work"
    work.mkdir(exist_ok=True)
    width, height = CLIP_SIZE[shape]
    clip = make_look_clip(work / "A.mp4", width, height, pattern, **options)
    entry = make_manifest(work, shape, [clip])["clips"][0]
    folder = tmp_path / "measuring"
    folder.mkdir(exist_ok=True)
    return measure.measure_clip(clip, entry, set(real_filters()) if have is None else have, folder)


def halves_where(result, low, high):
    """The half-second entries that start at or after `low` and before `high` seconds."""
    return [half for half in result["halves"] if low <= half["t"] < high]


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_camera_still_with_moving_square(shape, tmp_path):
    result = measured(tmp_path, shape, "square", start=4.0, end=5.0)
    for half in result["halves"]:
        assert half["camera"] is not None and half["camera"] < 0.5, half
        assert half["shake"] is not None and half["shake"] < 0.5, half
    assert any(half["subject"] is True for half in halves_where(result, 4.0, 5.0))
    for half in halves_where(result, 0.0, 3.5) + halves_where(result, 5.5, 99):
        assert half["subject"] is False, half


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_camera_shaky_jitter(shape, tmp_path):
    result = measured(tmp_path, shape, "jitter")
    states = [half["camera_state"] for half in result["halves"]]
    assert states.count("shaky") >= 0.75 * len(states), states
    assert all(half["subject"] is not True for half in result["halves"])


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_camera_panning(shape, tmp_path):
    result = measured(tmp_path, shape, "pan")
    inside = halves_where(result, 1.0, 6.51)
    assert [half["camera_state"] for half in inside] == ["panning"] * len(inside), inside
    assert all(half["camera_state"] != "shaky" for half in result["halves"])
    assert all(half["subject"] is None for half in inside)  # never judged while the camera moves


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_shot_change_at_cut(shape, tmp_path):
    result = measured(tmp_path, shape, "cut", start=3.4)
    assert len(result["shot_changes"]) == 1
    assert result["shot_changes"][0] == pytest.approx(3.4, abs=0.1)
    flagged = [half["t"] for half in result["halves"] if half["shot_change"]]
    assert flagged == [3.0]
    assert all(half["shot_change"] is False for half in result["halves"] if half["t"] != 3.0)
    (cut_half,) = halves_where(result, 3.0, 3.5)
    assert cut_half["movement"] < 10  # the cut frame is left out of the half's movement
    cut_frames = [frame for frame in result["frames"] if frame["cut"]]
    assert len(cut_frames) == 1
    assert cut_frames[0]["movement"] > 50  # but it stays in the frame list
    assert cut_frames[0]["camera"] is None and cut_frames[0]["shake"] is None


def test_parse_motion_header_and_rows(tmp_path):
    header = "Ori x, Avg x, Fin x, Ori y, Avg y, Fin y, Ori angle, Avg angle, Fin angle, Ori zoom, Avg zoom, Fin zoom"
    path = tmp_path / "motion.txt"
    path.write_text(
        header + "\n0.000000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0\n"
        "1.500000, 0.15, -1.35, -2.0, -0.2, 1.8, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0\n", encoding="utf-8")
    rows = measure.parse_motion(path)
    assert len(rows) == 2
    assert all(len(row) == 12 for row in rows)
    assert (rows[1][0], rows[1][3]) == (1.5, -2.0)


def test_chain_order():
    have = {"fps", "scale", "signalstats", "scdet", "deshake", "metadata"}
    assert filter_names(measure.video_chain(have)) == ["fps", "scale", "signalstats", "scdet", "deshake", "metadata"]
