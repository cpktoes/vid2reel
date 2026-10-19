import functools
import json

import pytest
from media import filter_names, make_look_clip, make_manifest

from v2r import doctor, settings
from v2r.__main__ import main
from v2r.look import measure

CLIP_SIZE = {"tall": (360, 640), "wide": (640, 360)}  # the clip sizes swap with the shape


@functools.cache
def real_filters():
    return frozenset(doctor.ffmpeg_names("-filters"))


def measured(tmp_path, shape, pattern, have=None, **options):
    """Make a look test clip in `tmp_path` and measure it directly; returns measure_clip's dict."""
    work = tmp_path / "work"
    work.mkdir(parents=True, exist_ok=True)
    width, height = CLIP_SIZE[shape]
    clip = make_look_clip(work / "A.mp4", width, height, pattern, **options)
    entry = make_manifest(work, shape, [clip])["clips"][0]
    folder = tmp_path / "measuring"
    folder.mkdir(parents=True, exist_ok=True)
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


@pytest.mark.parametrize("bad", ["nan", "inf", "-inf"])
def test_parse_motion_refuses_a_number_that_is_not_finite(bad, tmp_path):
    header = "Ori x, Avg x, Fin x, Ori y, Avg y, Fin y, Ori angle, Avg angle, Fin angle, Ori zoom, Avg zoom, Fin zoom"
    path = tmp_path / "motion.txt"
    path.write_text(
        header + f"\n0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0\n"
        f"{bad}, 0.15, -1.35, -2.0, -0.2, 1.8, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0\n", encoding="utf-8")
    with pytest.raises(ValueError):
        measure.parse_motion(path)


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_a_non_finite_motion_value_is_an_unreadable_motion_file(shape, tmp_path, monkeypatch):
    real = measure.parse_motion

    def poisoned(path):
        lines = path.read_text(encoding="utf-8").splitlines()
        lines[3] = ",".join(["nan"] + lines[3].split(",")[1:])
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return real(path)

    monkeypatch.setattr(measure, "parse_motion", poisoned)
    result = measured(tmp_path, shape, "plain")
    assert result["notes"] == ["The camera movement of clip A could not be read."]
    assert all(half["camera"] is None and half["shake"] is None for half in result["halves"])
    assert all(half["movement"] is not None for half in result["halves"][1:])  # the other measurements stand


def test_chain_order():
    have = {"fps", "scale", "signalstats", "blurdetect", "scdet", "deshake", "metadata"}
    assert filter_names(measure.video_chain(have)) == [
        "fps", "scale", "signalstats", "blurdetect", "scdet", "deshake", "metadata"]
    have.discard("deshake")
    assert filter_names(measure.video_chain(have)) == ["fps", "scale", "signalstats", "blurdetect", "scdet", "metadata"]


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_sharpness_blurred_stretch(shape, tmp_path):
    result = measured(tmp_path, shape, "blur", start=2.0, end=3.0)
    blurred = halves_where(result, 2.0, 3.0)
    assert [half["sharp"] for half in blurred] == [False, False]
    outside = halves_where(result, 0.0, 1.5) + halves_where(result, 3.5, 99)
    assert all(half["sharp"] is True for half in outside), outside
    assert min(half["blur"] for half in blurred) > max(half["blur"] for half in outside)


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_brightness_two_grey_levels(shape, tmp_path):
    dark = measured(tmp_path / "dark", shape, "grey", level="0x303030")
    light = measured(tmp_path / "light", shape, "grey", level="0xC0C0C0")
    assert light["overall"]["brightness"] - dark["overall"]["brightness"] > 100
    for low, high in zip(dark["halves"], light["halves"]):
        assert high["brightness"] - low["brightness"] > 100


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_colour_cast(shape, tmp_path):
    plain = measured(tmp_path / "plain", shape, "plain")["overall"]
    cast = measured(tmp_path / "cast", shape, "cast")["overall"]
    assert cast["red_shift"] - plain["red_shift"] > 4
    assert plain["blue_shift"] - cast["blue_shift"] > 4
    assert set(cast) == {"brightness", "brightness_low", "brightness_high", "blue_shift", "red_shift", "saturation"}
    assert cast["brightness_low"] < cast["brightness"] < cast["brightness_high"]
    assert cast["saturation"] > 0


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_flat_picture_has_no_sharpness(shape, tmp_path):
    result = measured(tmp_path / "grey", shape, "grey", level="0x303030")
    assert all(half["blur"] is None and half["sharp"] is None for half in result["halves"])
    assert all(frame["blur"] is None for frame in result["frames"])
    assert result["overall"]["saturation"] == 0


def no_constant(name):
    raise ValueError(f"look.json holds {name}, which is not valid JSON")


def look_run(tmp_path, shape, pattern, monkeypatch=None, drop=None, **options):
    """Make a look test clip and run `v2r look` on it, with the filter `drop` taken away from this computer's FFmpeg.

    Returns (exit code, look.json as a dictionary, the work folder).
    """
    work = tmp_path / "work"
    work.mkdir()
    width, height = CLIP_SIZE[shape]
    clip = make_look_clip(work / "A.mp4", width, height, pattern, **options)
    make_manifest(work, shape, [clip])
    if drop:
        real = doctor.ffmpeg_names

        def without(option):
            names = real(option)
            return names - {drop} if option == "-filters" else names

        monkeypatch.setattr(doctor, "ffmpeg_names", without)
    code = main(["look", str(work)])
    look = json.loads((work / "look.json").read_text(encoding="utf-8"), parse_constant=no_constant)
    return code, look, work


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_loudness_beep(shape, tmp_path):
    result = measured(tmp_path, shape, "plain", beep=(3.0, 3.4))
    by_time = {half["t"]: half["loudness"] for half in result["halves"]}
    assert by_time[3.0] is not None and by_time[3.0] >= -30
    assert by_time[3.0] == max(value for value in by_time.values() if value is not None)
    assert all(value is None for t, value in by_time.items() if t + settings.SUMMARY_SECONDS < 3.0)
    assert all(value is None for t, value in by_time.items() if t >= 4.0)
    assert all(reading["t"] >= 0 for reading in result["sound"])


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_loudness_silent_track(shape, tmp_path):
    result = measured(tmp_path, shape, "plain")
    assert all(half["loudness"] is None for half in result["halves"])
    assert result["notes"] == []


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_loudness_skipped_when_sound_added(shape, tmp_path, monkeypatch):
    def not_called(*args, **kwargs):
        raise AssertionError("the loudness command ran for a clip whose sound normalize added")

    monkeypatch.setattr(measure, "measure_loudness", not_called)
    work = tmp_path / "work"
    work.mkdir()
    width, height = CLIP_SIZE[shape]
    clip = make_look_clip(work / "A.mp4", width, height, "plain", beep=(3.0, 3.4))
    entry = make_manifest(work, shape, [{"file": clip, "sound_added": True}])["clips"][0]
    (tmp_path / "measuring").mkdir()
    result = measure.measure_clip(clip, entry, set(real_filters()), tmp_path / "measuring")
    assert all(half["loudness"] is None for half in result["halves"])
    assert result["sound"] == []


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_missing_filter_deshake(shape, tmp_path, monkeypatch, capsys):
    code, look, work = look_run(tmp_path, shape, "square", monkeypatch, "deshake", start=4.0, end=5.0)
    assert code == 0
    (sentence,) = look["missing"]
    assert "deshake" in sentence and sentence in capsys.readouterr().out
    (clip,) = look["clips"]
    for half in clip["halves"]:
        assert half["camera"] is None and half["shake"] is None
        assert half["camera_state"] is None and half["subject"] is None
        assert isinstance(half["movement"], float)
    assert clip["shot_changes"] == []
    assert (work / "sheets" / "sheet-01.jpg").is_file()


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_missing_filter_ebur128(shape, tmp_path, monkeypatch):
    code, look, work = look_run(tmp_path, shape, "plain", monkeypatch, "ebur128", beep=(3.0, 3.4))
    assert code == 0
    (sentence,) = look["missing"]
    assert "ebur128" in sentence and "loudness" in sentence
    (clip,) = look["clips"]
    assert all(half["loudness"] is None for half in clip["halves"])
    assert all(isinstance(half["brightness"], float) for half in clip["halves"])
    assert (work / "sheets" / "sheet-01.jpg").is_file()


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_missing_filter_metadata(shape, tmp_path, monkeypatch):
    code, look, work = look_run(tmp_path, shape, "plain", monkeypatch, "metadata", beep=(3.0, 3.4))
    assert code == 0
    (sentence,) = look["missing"]
    assert "metadata" in sentence and "nothing could be measured" in sentence
    (clip,) = look["clips"]
    assert clip["shot_changes"] is None
    assert clip["overall"] == {key: None for key in clip["overall"]}
    for half in clip["halves"]:
        values = {key: value for key, value in half.items() if key != "t"}
        assert all(value is None for value in values.values()), half
    assert (work / "sheets" / "sheet-01.jpg").is_file()


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_missing_filter_scdet(shape, tmp_path, monkeypatch):
    code, look, _ = look_run(tmp_path, shape, "cut", monkeypatch, "scdet", start=3.4)
    assert code == 0
    (sentence,) = look["missing"]
    assert "scdet" in sentence
    (clip,) = look["clips"]
    assert clip["shot_changes"] is None
    assert all(half["shot_change"] is None for half in clip["halves"])
    assert all(isinstance(half["movement"], float) for half in clip["halves"])  # the cut stays in the movement


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_missing_filter_blurdetect(shape, tmp_path, monkeypatch):
    code, look, _ = look_run(tmp_path, shape, "blur", monkeypatch, "blurdetect", start=2.0, end=3.0)
    assert code == 0
    (sentence,) = look["missing"]
    assert "blurdetect" in sentence
    (clip,) = look["clips"]
    assert all(half["blur"] is None and half["sharp"] is None for half in clip["halves"])
    assert all(isinstance(half["camera"], float) for half in clip["halves"])


def test_finite_values():
    for text in ["nan", "-inf", "inf", "", "abc", None]:
        assert measure.finite(text) is None
    assert measure.finite("4.5") == 4.5


def hand_frames(times, movement=1.0, cut_at=None):
    return [
        {"t": t, "movement": movement, "cut": t == cut_at, "camera": 0.0, "shake": 0.0, "blur": 5.0, "brightness": 100.0}
        for t in times
    ]


def test_summarise_boundary_frame():
    # a frame at exactly 0.5 s is the first frame of the half that starts at 0.5
    frames = hand_frames([0.0, 0.1, 0.2, 0.3, 0.4], movement=1.0) + hand_frames([0.5, 0.6, 0.7, 0.8, 0.9], movement=3.0)
    first, second = measure.summarise(frames, [], 1.0)
    assert (first["movement"], second["movement"]) == (1.0, 3.0)
    # a reading whose corrected time is exactly 1.0 belongs to the half that starts at 1.0
    sound = [{"t": 0.9, "loudness": -40.0}, {"t": 1.0, "loudness": -20.0}]
    halves = measure.summarise(hand_frames([i / 10 for i in range(15)]), sound, 1.5)
    assert [half["loudness"] for half in halves] == [None, -40.0, -20.0]
    # a cut frame counts in the half that holds it, and its jump is left out of that half's movement
    frames = hand_frames([i / 10 for i in range(10)])
    frames[5]["cut"] = True
    frames[5]["movement"] = 120.0
    first, second = measure.summarise(frames, [], 1.0)
    assert (first["shot_change"], second["shot_change"]) == (False, True)
    assert second["movement"] == 1.0


def test_summarise_empty_half():
    halves = measure.summarise(hand_frames([i / 10 for i in range(10)]), [], 1.5)
    assert len(halves) == 3
    assert halves[2] == {
        "t": 1.0, "movement": None, "camera": None, "shake": None, "camera_state": None, "subject": None,
        "blur": None, "sharp": None, "brightness": None, "loudness": None, "shot_change": None,
    }
