"""The reel's sound: defaults, kept runs, the drop curve, the gain rule and the music library, as pure functions."""

import array
import json
import math
import re
import subprocess

import pytest
from cutlists import clips_block, write_list
from media import filter_names, make_colour_clip, make_manifest

from v2r import render as render_module
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
    assert set(two) <= set("pow(10,-.0123456789)*/tmaxincl ")


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


# --- the sound in a finished reel, measured with FFmpeg's own meters, in both shapes ---------------------------------

SMALL = {"tall": (360, 640), "wide": (640, 360)}  # pictures are not what these tests measure, so the canvas is small
TIMEOUT = 120


@pytest.fixture
def small(monkeypatch):
    monkeypatch.setattr(settings, "SHAPES", dict(SMALL))
    monkeypatch.setattr(settings, "RENDER_X264_PRESET", "ultrafast")


def sound_work(tmp_path, shape, segments, music=None, clip_seconds=5.0, beep=None):
    """A work folder with one clip A (a flat colour; its sound is a 1 kHz tone over `beep`, else silence) and a list.

    `segments` are (from, to, sound) triples on clip A; `music` is the list's sound block, or None for no block.
    Returns the work folder.
    """
    work = tmp_path / "work"
    work.mkdir()
    width, height = SMALL[shape]
    make_colour_clip(work / "A.mp4", width, height, clip_seconds, (120, 128, 128), beep=beep)
    manifest = make_manifest(work, shape, [work / "A.mp4"])
    data = {
        "version": 1,
        "canvas": {"width": width, "height": height, "fps": settings.OUTPUT_FPS},
        "clips": clips_block(manifest),
        "segments": [
            {"clip": "A", "from": start, "to": end, "sound": mode, "why": "a shot"} for start, end, mode in segments],
    }
    if music is not None:
        data["sound"] = music
    write_list(work, data)
    return work


def render_it(work):
    """Render the work folder's list; returns (the reel's path, the closing sentences)."""
    reel, sentences = render_module.render(work / "cutlist.json", work)
    return reel, sentences


def window_levels(path, start, end):
    """(mean volume, max volume) in dB of the reel's sound between two times."""
    err = subprocess.run(
        ["ffmpeg", "-nostdin", "-i", str(path), "-vn", "-af", f"atrim=start={start}:end={end},volumedetect",
         "-f", "null", "-"], capture_output=True, text=True, check=True, timeout=TIMEOUT).stderr
    mean = float(re.search(r"mean_volume: (\S+) dB", err).group(1))
    peak = float(re.search(r"max_volume: (\S+) dB", err).group(1))
    return mean, peak


def integrated_and_peak(path):
    """(integrated loudness in LUFS, true peak in dBTP) of the reel's sound, from ebur128's summary."""
    err = subprocess.run(
        ["ffmpeg", "-nostdin", "-i", str(path), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, check=True, timeout=TIMEOUT).stderr
    summary = err[err.rindex("Summary:"):]
    loudness = float(re.search(r"I:\s+(\S+) LUFS", summary).group(1))
    peak = float(re.search(r"Peak:\s+(\S+) dBFS", summary).group(1))
    return loudness, peak


def envelope_samples(expression, seconds, times):
    """The values of an aevalsrc expression at the given times, rendered alone to raw 32-bit floats at 48 kHz."""
    data = subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-f", "lavfi", "-i",
         f"aevalsrc='{expression}':s={settings.AUDIO_RATE}:d={seconds}", "-f", "f32le", "-"],
        capture_output=True, check=True, timeout=TIMEOUT).stdout
    values = array.array("f")
    values.frombytes(data)
    return [values[round(t * settings.AUDIO_RATE)] for t in times]


@pytest.mark.parametrize("shape", SHAPES)
def test_kept_and_off_sound(shape, small, tmp_path):
    work = sound_work(
        tmp_path, shape, [(0.0, 2.0, "keep"), (2.0, 4.0, "off")], beep=(0.0, 5.0))
    reel, sentences = render_it(work)
    kept_mean, kept_peak = window_levels(reel, 0.2, 1.8)
    _, off_peak = window_levels(reel, 2.2, 3.8)
    assert kept_peak > -20
    assert off_peak < -60
    assert "sound evened to -14.0 LUFS" in sentences[-3]


@pytest.mark.parametrize("shape", SHAPES)
def test_music_drops_under_kept_sound(shape, small, tmp_path):
    work = sound_work(
        tmp_path, shape, [(0.0, 1.5, "off"), (1.5, 3.0, "keep"), (3.0, 4.5, "off")],
        music={"music": "test-tone", "fade_in": 0, "fade_out": 0, "music_under_sound": -12})
    reel, _ = render_it(work)
    first, _ = window_levels(reel, 0.3, 1.0)
    kept, _ = window_levels(reel, 1.8, 2.7)
    last, _ = window_levels(reel, 3.5, 4.3)
    ramp, _ = window_levels(reel, 1.30, 1.40)  # the middle of the 0.3 second ramp that ends as the kept shot begins
    assert first - kept == pytest.approx(12, abs=0.5)
    assert last == pytest.approx(first, abs=0.5)
    assert first - ramp == pytest.approx(6, abs=1.0)


@pytest.mark.parametrize("shape", SHAPES)
def test_adjacent_kept_segments_hold_the_drop(shape, small, tmp_path):
    work = sound_work(
        tmp_path, shape, [(0.0, 1.5, "off"), (1.5, 3.0, "keep"), (3.0, 4.5, "keep")],
        music={"music": "test-tone", "fade_in": 0, "fade_out": 0, "music_under_sound": -12})
    reel, _ = render_it(work)
    before, _ = window_levels(reel, 0.3, 1.0)
    across, _ = window_levels(reel, 2.9, 3.1)  # either side of the cut between the two kept shots
    end, _ = window_levels(reel, 3.5, 4.4)
    assert before - across == pytest.approx(12, abs=0.5)
    assert before - end == pytest.approx(12, abs=0.5)


@pytest.mark.parametrize("shape", SHAPES)
def test_fades(shape, small, tmp_path):
    work = sound_work(
        tmp_path, shape, [(0.0, 2.25, "off"), (2.25, 4.5, "off")],
        music={"music": "test-tone", "fade_in": 1.0, "fade_out": 1.5})
    reel, _ = render_it(work)
    middle, _ = window_levels(reel, 1.5, 2.9)
    start, _ = window_levels(reel, 0.0, 0.1)
    end, _ = window_levels(reel, 4.4, 4.5)
    half, _ = window_levels(reel, 3.70, 3.80)  # the middle of the 1.5 second fade out, which begins at 3.0
    assert middle - start > 15
    assert middle - end > 15
    assert middle - half == pytest.approx(6, abs=1.0)


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("target", [None, -16])
def test_loudness_is_evened_to_the_target(shape, target, small, tmp_path):
    block = {"music": "test-tone", "music_under_sound": -12}
    if target is not None:
        block["loudness"] = target
    work = sound_work(
        tmp_path, shape, [(0.0, 2.0, "keep"), (2.0, 4.0, "off")], music=block, beep=(0.0, 5.0))
    reel, sentences = render_it(work)
    wanted = -14 if target is None else target
    loudness, _ = integrated_and_peak(reel)
    assert loudness == pytest.approx(wanted, abs=0.3)
    assert f"sound evened to {wanted:.1f} LUFS." in sentences[-3]


@pytest.mark.parametrize("shape", SHAPES)
def test_peak_ceiling_stops_the_gain(shape, small, tmp_path):
    work = sound_work(tmp_path, shape, [(0.0, 2.0, "keep"), (2.0, 4.0, "keep")], music={"loudness": 0}, beep=(0.0, 5.0))
    reel, sentences = render_it(work)
    said = sentences[-3]
    assert "short of the 0 LUFS target because the loudest peak would have gone past -1 dBTP." in said
    figure = float(re.search(r"sound evened to (\S+) LUFS", said).group(1))
    loudness, peak = integrated_and_peak(reel)
    assert figure < 0
    assert loudness == pytest.approx(figure, abs=0.3)  # the sentence states what the reel really measures
    assert peak <= -0.5


@pytest.mark.parametrize("shape", SHAPES)
def test_silent_reel_has_a_silent_aac_track(shape, small, tmp_path):
    work = sound_work(tmp_path, shape, [(0.0, 2.0, "off"), (2.0, 4.0, "off")])
    reel, sentences = render_it(work)
    info = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,channels", "-of", "json", str(reel)],
        capture_output=True, text=True, check=True, timeout=TIMEOUT).stdout)
    tracks = [item for item in info["streams"] if item["codec_type"] == "audio"]
    assert [(item["codec_name"], item["channels"]) for item in tracks] == [("aac", 2)]
    assert window_levels(reel, 0.0, 4.0)[1] <= -90
    assert sentences[-3].endswith(", with no sound to even.")


@pytest.mark.parametrize("shape", SHAPES)
def test_a_library_track_is_used(shape, small, tmp_path, monkeypatch):
    folder = tmp_path / "music"
    folder.mkdir()
    # silent until 8 seconds into the track, then a 330 Hz tone: music_from 5 puts the tone 3 seconds into the reel
    subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-f", "lavfi", "-i",
         "aevalsrc='0.5*sin(2*PI*330*t)*gt(t,8)':s=48000:d=30", "-c:a", "aac", str(folder / "hum.m4a")],
        check=True, timeout=TIMEOUT)
    (folder / "library.json").write_text(
        json.dumps({"tracks": [{"id": "hum", "file": "hum.m4a", "seconds": 30.0}]}), encoding="utf-8")
    monkeypatch.setattr(sound, "MUSIC_DIR", folder)
    work = sound_work(
        tmp_path, shape, [(0.0, 2.0, "off"), (2.0, 4.5, "off")],
        music={"music": "hum", "music_from": 5.0, "fade_in": 0, "fade_out": 0})
    reel, sentences = render_it(work)
    assert window_levels(reel, 0.3, 2.7)[1] < -50
    assert window_levels(reel, 3.3, 4.4)[0] > -40
    assert sound.track("hum")["seconds"] == 30.0


@pytest.mark.parametrize("shape", SHAPES)
def test_drop_expression_matches_its_reference(shape):
    runs = [(0.5, 2.0), (3.0, 3.5), (5.0, 6.0)]
    expression = sound.drop_expression(runs, -12, 0.3)
    times = [0.1, 0.3, 0.55, 2.1, 2.2, 2.45, 2.9, 3.2, 4.0, 5.9]
    got = envelope_samples(expression, 7, times)
    for t, value in zip(times, got):
        assert 20 * math.log10(value) == pytest.approx(20 * math.log10(sound.gain_at(t, runs, -12, 0.3)), abs=0.05)


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("music", [
    None,
    {"music": "test-tone"},
    {"music": "test-tone", "music_under_sound": -12, "fade_in": 1.0, "fade_out": 2.0, "music_from": 3.0},
])
def test_sound_commands_use_only_listed_filters(shape, music, tmp_path):
    manifest = {"clips": [clip_entry("A", shape)]}
    width, height = settings.SHAPES[shape]
    cutlist = {
        "version": 1, "canvas": {"width": width, "height": height, "fps": 30},
        "segments": [
            {"clip": "A", "from": 0.0, "to": 2.0, "sound": "keep", "why": "a"},
            {"clip": "A", "from": 2.0, "to": 4.0, "sound": "off", "why": "b"}],
    }
    if music is not None:
        cutlist["sound"] = music
    the_plan = plan.plan(cutlist, manifest)
    command = sound.mix_command(the_plan, tmp_path, tmp_path / "mix.wav")
    assert command == sound.mix_command(the_plan, tmp_path, tmp_path / "mix.wav")  # equal inputs, equal commands
    graph = command[command.index("-filter_complex") + 1]
    names = filter_names(re.sub(r"'[^']*'", "", graph))
    assert set(names) <= set(render_module.RENDER_FILTERS), names
    assert "loudnorm" not in graph and "acompressor" not in graph and "alimiter" not in graph
    assert ("amix=inputs=2:duration=first:normalize=0" in graph) == (music is not None)
    assert ("amultiply" in graph) == bool(music and music.get("music_under_sound"))


# ---- the test tone's length follows the settings (IN-03) ----


def tone_duration(music_from, seconds):
    the_plan = {"seconds": seconds, "total_frames": round(seconds * settings.OUTPUT_FPS), "segments": []}
    graph = sound.music_branch(the_plan, {**sound.sound_settings({}), "music_from": music_from}, None)
    return float(re.search(r"duration=([0-9.]+)", graph[0]).group(1))


def test_the_test_tone_runs_a_stated_slack_past_the_end_of_the_reel(monkeypatch):
    assert tone_duration(0.0, 10.0) == pytest.approx(10.0 + settings.TEST_TONE_SLACK_SECONDS)
    assert tone_duration(20.0, 10.0) == pytest.approx(30.0 + settings.TEST_TONE_SLACK_SECONDS)
    monkeypatch.setattr(settings, "TEST_TONE_SLACK_SECONDS", 2.5)
    assert tone_duration(0.0, 10.0) == pytest.approx(12.5)


def test_the_test_tone_is_never_longer_than_the_length_the_settings_give_it(monkeypatch):
    # check refuses a reel that would need more than TEST_TONE_SECONDS of tone, so the tone never has to be longer
    assert tone_duration(settings.TEST_TONE_SECONDS - 10.0, 10.0) == pytest.approx(settings.TEST_TONE_SECONDS)
    monkeypatch.setattr(settings, "TEST_TONE_SECONDS", 60)
    assert tone_duration(0.0, 10.0) == pytest.approx(10.0 + settings.TEST_TONE_SLACK_SECONDS)
    assert tone_duration(52.0, 10.0) == pytest.approx(60.0)  # 63 seconds would not fit in the track's 60
