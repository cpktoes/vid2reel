"""The reel's sound: defaults, kept runs, the drop curve, the gain rule and the music library, as pure functions."""

import json
import math

import pytest

from v2r import settings
from v2r.render import plan, sound

SHAPES = ["tall", "wide"]
SIZE = {"tall": [360, 640], "wide": [640, 360]}


def clip_entry(letter, shape, seconds=10.0):
    return {
        "letter": letter, "number": ord(letter) - 64, "status": "done", "kind": "video",
        "working": {"file": f"{letter}.mp4", "size": SIZE[shape], "fps": 30.0, "seconds": seconds},
    }


def planned(shape, sounds, length=1.5):
    """A plan over one clip, one segment of `length` seconds per entry of `sounds`, each "keep" or "off"."""
    manifest = {"clips": [clip_entry("A", shape)]}
    width, height = settings.SHAPES[shape]
    segments = [
        {"clip": "A", "from": 0.0, "to": length, "sound": mode, "why": "a shot"} for mode in sounds
    ]
    cutlist = {"version": 1, "canvas": {"width": width, "height": height, "fps": 30}, "segments": segments}
    return plan.plan(cutlist, manifest)


def test_sound_settings_defaults_and_stated_values():
    assert sound.sound_settings({"segments": []}) == {
        "music": None, "music_from": 0.0, "fade_in": settings.FADE_IN_SECONDS,
        "fade_out": settings.FADE_OUT_SECONDS, "music_under_sound": 0.0, "loudness": settings.LOUDNESS_TARGET,
    }
    stated = {"sound": {
        "music": "test-tone", "music_from": 4.5, "fade_in": 0, "fade_out": 2.0, "music_under_sound": -9, "loudness": -16}}
    assert sound.sound_settings(stated) == {
        "music": "test-tone", "music_from": 4.5, "fade_in": 0, "fade_out": 2.0, "music_under_sound": -9,
        "loudness": -16}
    assert sound.sound_settings({"sound": {"music": None}})["music"] is None


def test_sound_settings_read_the_settings_when_called(monkeypatch):
    monkeypatch.setattr(settings, "FADE_IN_SECONDS", 0.8)
    monkeypatch.setattr(settings, "LOUDNESS_TARGET", -18)
    got = sound.sound_settings({})
    assert (got["fade_in"], got["loudness"]) == (0.8, -18)


@pytest.mark.parametrize("shape", SHAPES)
def test_kept_runs_merge_adjacent_kept_segments(shape):
    runs = sound.kept_runs(planned(shape, ["off", "keep", "keep", "off", "keep"]))
    assert runs == [(1.5, 4.5), (6.0, 7.5)]


@pytest.mark.parametrize("shape", SHAPES)
def test_kept_runs_of_nothing_kept_or_everything_kept(shape):
    assert sound.kept_runs(planned(shape, ["off", "off"])) == []
    assert sound.kept_runs(planned(shape, ["keep", "keep", "keep"])) == [(0.0, 4.5)]


RUNS = [(0.0, 2.5), (7.5, 9.0)]


@pytest.mark.parametrize("t, expected", [
    (0.0, -12), (2.5, -12), (2.65, -6), (2.8, 0), (7.1, 0), (7.2, 0), (7.35, -6), (7.5, -12)])
def test_gain_at_matches_the_checked_values(t, expected):
    got = 20 * math.log10(sound.gain_at(t, RUNS, -12, 0.3))
    assert got == pytest.approx(expected, abs=1e-6)


def test_gain_at_is_one_without_runs_or_drop_and_rejects_a_bad_ramp():
    assert sound.gain_at(1.0, [], -12, 0.3) == 1.0
    assert sound.gain_at(1.0, RUNS, 0, 0.3) == 1.0
    with pytest.raises(ValueError):
        sound.gain_at(1.0, RUNS, -12, 0)
    with pytest.raises(ValueError):
        sound.drop_expression(RUNS, -12, -0.1)


def test_drop_expression_is_built_from_formatted_numbers_only():
    one = sound.drop_expression([(1.0, 2.0)], -12, 0.3)
    assert one.startswith("pow(10,(-12.000000)*(") and one.endswith(")/20)")
    assert "max(" not in one
    two = sound.drop_expression(RUNS, -12, 0.3)
    assert two.count("clip(") == 2 and two.count("max(") == 1
    assert set(two) <= set("pow(10,-.0123456789)*/tmincl ")


def test_gain_for_raises_to_the_target_without_a_cap():
    gain, figure, capped = sound.gain_for(-20.0, 0.1, -14, -1)
    assert (gain, figure, capped) == (pytest.approx(6.0), pytest.approx(-14.0), False)


def test_gain_for_is_stopped_by_the_peak_ceiling_and_gives_its_real_figure():
    gain, figure, capped = sound.gain_for(-8.0, 0.5, 0, -1)
    assert capped is True
    assert gain == pytest.approx(-1 - 20 * math.log10(0.5))
    assert figure == pytest.approx(-8.0 + gain)
    assert figure < 0


def test_gain_for_lowers_a_loud_mix_and_gives_nothing_for_silence():
    gain, figure, capped = sound.gain_for(-6.0, 0.2, -14, -1)
    assert (gain, figure, capped) == (pytest.approx(-8.0), pytest.approx(-14.0), False)
    assert sound.gain_for(-70.0, 0.0, -14, -1) == (0.0, None, False)
    assert sound.gain_for(None, None, -14, -1) == (0.0, None, False)
    assert sound.gain_for(-95.0, 0.0, -14, -1) == (0.0, None, False)


def library(tmp_path, content, name="library.json"):
    (tmp_path / name).write_text(content if isinstance(content, str) else json.dumps(content), encoding="utf-8")
    return tmp_path


def test_read_library_without_a_file_is_empty(tmp_path):
    assert sound.read_library(tmp_path) == {}


def test_read_library_reads_each_id(tmp_path):
    folder = library(tmp_path, {"tracks": [
        {"id": "hum", "file": "hum.m4a", "seconds": 30.0, "licence": "CC0"},
        {"id": "pad", "file": "pad.mp3", "seconds": 90},
    ]})
    assert sound.read_library(folder) == {
        "hum": {"file": "hum.m4a", "seconds": 30.0}, "pad": {"file": "pad.mp3", "seconds": 90}}


@pytest.mark.parametrize("content", [
    "not json at all",
    "[]",
    {"tracks": "none"},
    {"tracks": [{"id": "x", "file": "x.m4a"}]},
    {"tracks": [{"id": "x", "file": "x.m4a", "seconds": 0}]},
    {"tracks": [{"id": "x", "file": "x.m4a", "seconds": True}]},
    {"tracks": [{"id": "x", "file": "../x.m4a", "seconds": 5}]},
    {"tracks": [{"id": "x", "file": ".hidden.m4a", "seconds": 5}]},
    {"tracks": [{"id": "x", "file": "sub/x.m4a", "seconds": 5}]},
    {"tracks": [{"id": 7, "file": "x.m4a", "seconds": 5}]},
    {"tracks": [{"id": "x", "file": "x.m4a", "seconds": float("inf")}]},
])
def test_read_library_refuses_a_broken_library_in_one_sentence(tmp_path, content):
    folder = library(tmp_path, json.dumps(content, allow_nan=True) if not isinstance(content, str) else content)
    with pytest.raises(sound.LibraryError) as error:
        sound.read_library(folder)
    assert str(error.value) == "music/library.json could not be read, so the music cannot be checked."


def test_track_test_tone_needs_no_library(tmp_path):
    got = sound.track(settings.TEST_TONE_ID, tmp_path)
    assert got == {"id": "test-tone", "seconds": settings.TEST_TONE_SECONDS, "path": None}


def test_track_uses_the_module_music_folder_by_default(tmp_path, monkeypatch):
    (tmp_path / "hum.m4a").write_bytes(b"x")
    library(tmp_path, {"tracks": [{"id": "hum", "file": "hum.m4a", "seconds": 30.0}]})
    monkeypatch.setattr(sound, "MUSIC_DIR", tmp_path)
    got = sound.track("hum")
    assert got["seconds"] == 30.0 and got["path"] == (tmp_path / "hum.m4a").resolve()


def test_track_of_an_unknown_id(tmp_path):
    with pytest.raises(sound.LibraryError) as error:
        sound.track("nothing", tmp_path)
    assert str(error.value) == (
        'The music track "nothing" is not in music/library.json; there is no music/library.json yet, so only '
        '"test-tone" can be used.')
    library(tmp_path, {"tracks": []})
    with pytest.raises(sound.LibraryError) as error:
        sound.track("nothing", tmp_path)
    assert str(error.value) == 'The music track "nothing" is not in music/library.json.'


def test_track_echoes_an_id_only_after_cleaning_it(tmp_path):
    with pytest.raises(sound.LibraryError) as error:
        sound.track("bad\nline", tmp_path)
    assert "\n" not in str(error.value)


def test_track_whose_file_is_missing(tmp_path):
    library(tmp_path, {"tracks": [{"id": "hum", "file": "hum.m4a", "seconds": 30.0}]})
    with pytest.raises(sound.LibraryError) as error:
        sound.track("hum", tmp_path)
    assert str(error.value) == 'The music file for "hum" is missing from music/.'


def test_track_whose_file_is_outside_the_music_folder(tmp_path):
    folder = tmp_path / "music"
    folder.mkdir()
    (tmp_path / "secret.m4a").write_bytes(b"x")
    (folder / "link.m4a").symlink_to(tmp_path / "secret.m4a")
    library(folder, {"tracks": [{"id": "hum", "file": "link.m4a", "seconds": 30.0}]})
    with pytest.raises(sound.LibraryError) as error:
        sound.track("hum", folder)
    assert str(error.value) == 'The music file for "hum" is missing from music/.'
