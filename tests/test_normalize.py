import errno
import json

import pytest
from media import corner_mean, gray_frame, make_audio, make_clip, mean_luma, peak_volume, probe, stream

import v2r.normalize
from v2r import settings
from v2r.__main__ import main
from v2r.normalize import (clear_last_job, colour_notes, frame_facts, hdr_kind, letter, normalize, ordinal,
                           video_chain, working_size)

SMALL_CAPS = {
    "tall": {"portrait": (180, 320), "landscape": (None, 320)},
    "wide": {"landscape": (320, 180), "portrait": (320, None)},
}


@pytest.fixture
def small_caps(monkeypatch):
    """Small working sizes, so test clips stay tiny and the two shapes still give different sizes."""
    monkeypatch.setattr(settings, "WORKING_SIZE", SMALL_CAPS)


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_tracer_cli_one_clip_to_working_copy_and_manifest(shape, tmp_path, monkeypatch, capsys, small_caps):
    monkeypatch.setattr(v2r.normalize, "WORK_DIR", tmp_path / "work")
    (tmp_path / "sent").mkdir()
    clip = make_clip(tmp_path / "sent" / "in.mp4", 640, 360)

    assert main(["normalize", "--shape", shape, str(clip)]) == 0

    work = tmp_path / "work"
    info = probe(work / "A.mp4")
    video, audio = stream(info, "video"), stream(info, "audio")
    assert video["codec_name"] == "h264"
    assert video["pix_fmt"] == "yuv420p"
    assert video["r_frame_rate"] == "30/1"
    assert (video["width"], video["height"]) == working_size(shape, 640, 360)
    assert "side_data_list" not in video
    assert audio["codec_name"] == "aac"
    assert audio["channels"] == 2
    assert int(audio["sample_rate"]) == 48000
    assert float(video["duration"]) == pytest.approx(2.0, abs=0.1)
    assert float(audio["duration"]) == pytest.approx(2.0, abs=0.1)

    manifest = json.loads((work / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == 1
    assert manifest["shape"] == shape
    assert manifest["finished"] is True
    (entry,) = manifest["clips"]
    assert (entry["letter"], entry["number"], entry["status"], entry["kind"]) == ("A", 1, "done", "video")
    assert entry["working"]["file"] == "A.mp4"
    assert isinstance(entry["convert_seconds"], (int, float))
    assert "A done in" in capsys.readouterr().out


def test_tracer_shape_is_required(tmp_path):
    clip = make_clip(tmp_path / "in.mp4", 640, 360)
    with pytest.raises(SystemExit) as stopped:
        main(["normalize", str(clip)])
    assert stopped.value.code == 2


def convert(clips, shape, out_dir):
    """Normalize `clips` into `out_dir` and return the manifest as written to disk."""
    normalize(clips, shape, out_dir=out_dir)
    return json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("shape", "source", "expected"),
    [
        ("tall", (2160, 3840), (1080, 1920)),  # the 4K iPhone clip, stored sideways
        ("tall", (3840, 2160), (3412, 1920)),
        ("tall", (1920, 1080), (1920, 1080)),  # never scaled up
        ("tall", (4284, 5712), (1080, 1440)),  # a 24 MP photo
        ("wide", (3840, 2160), (1920, 1080)),
        ("wide", (2160, 3840), (1920, 3412)),
        ("wide", (1080, 1920), (1080, 1920)),  # never scaled up
        ("tall", (641, 361), (640, 360)),  # an odd size floors to even
        ("wide", (641, 361), (640, 360)),
        ("tall", (1080, 1920), (1080, 1920)),  # exactly at the cap keeps its size
        ("wide", (1920, 1080), (1920, 1080)),
        ("tall", (2000, 2000), (1080, 1080)),  # a square uses its own shape's entry
        ("wide", (2000, 2000), (1080, 1080)),
    ],
)
def test_working_size_table(shape, source, expected):
    assert working_size(shape, *source) == expected


def test_facts_frame_timing():
    assert frame_facts([i / 30 for i in range(60)]) == (30.0, True, False)
    assert frame_facts([i / 120 for i in range(240)])[2] is True
    assert frame_facts([0.0]) == (None, True, False)
    assert frame_facts([]) == (None, True, False)
    mixed = [0.0, 0.033, 0.099, 0.132, 0.198, 0.231, 0.264, 0.33]  # gaps of 33 ms and 66 ms
    assert frame_facts(mixed)[1] is False


@pytest.mark.parametrize(
    ("tags", "expected"),
    [
        ({"color_transfer": "arib-std-b67", "color_primaries": "bt2020"}, "hlg"),
        ({"color_transfer": "smpte2084"}, "pq"),
        ({"color_transfer": "unknown", "color_primaries": "bt2020"}, "bt2020"),
        ({"color_primaries": "bt2020"}, "bt2020"),
        ({"color_transfer": "bt709", "color_primaries": "bt709"}, None),
        ({"color_transfer": "unknown", "color_primaries": "unknown"}, None),
        ({}, None),
    ],
)
def test_facts_hdr_kind_table(tags, expected):
    assert hdr_kind(tags) == expected


@pytest.mark.parametrize("shape", ["tall", "wide"])
@pytest.mark.parametrize(("rotation", "bright", "dark"), [(90, "bottom-left", "top-right"), (-90, "top-right", "bottom-left")])
def test_upright_sideways_clip_marker(shape, rotation, bright, dark, tmp_path):
    clip = make_clip(tmp_path / "side.mp4", 640, 360, pattern="marker", sound=True, rotate=rotation)
    assert stream(probe(clip), "video")["side_data_list"][0]["rotation"] == rotation  # the test clip really is sideways

    entry = convert([clip], shape, tmp_path / "out")["clips"][0]

    assert entry["original"]["rotation"] == rotation
    assert entry["original"]["stored_size"] == [640, 360]
    assert entry["original"]["upright_size"] == [360, 640]
    assert entry["working"]["size"] == list(working_size(shape, 360, 640))
    working = tmp_path / "out" / "A.mp4"
    assert "side_data_list" not in stream(probe(working), "video")
    frame, width, height = gray_frame(working)
    assert corner_mean(frame, width, height, bright) > 200
    assert corner_mean(frame, width, height, dark) < 50


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_facts_shot_at(shape, tmp_path):
    both = make_clip(tmp_path / "both.mov", 320, 180, metadata={
        "creation_time": "2026-10-12T18:49:03Z", "com.apple.quicktime.creationdate": "2026-10-12T11:49:03-0700"})
    only = make_clip(tmp_path / "only.mov", 320, 180, metadata={"creation_time": "2026-10-12T18:49:03Z"})

    clips = convert([both, only], shape, tmp_path / "out")["clips"]

    assert clips[0]["original"]["shot_at"] == "2026-10-12T11:49:03-0700"
    assert clips[1]["original"]["shot_at"].startswith("2026-10-12T18:49:03")


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_facts_full_fact_sheet(shape, tmp_path):
    clip = make_clip(tmp_path / "in.mp4", 320, 180)

    original = convert([clip], shape, tmp_path / "out")["clips"][0]["original"]

    assert set(original) == {"path", "name", "bytes", "seconds", "stored_size", "rotation", "upright_size", "fps",
                             "fps_steady", "slow_motion", "hdr", "dolby_vision", "has_sound", "shot_at"}
    assert original["path"] == str(clip.resolve())
    assert original["bytes"] == clip.stat().st_size
    assert original["has_sound"] is True
    assert original["hdr"] is None
    assert original["dolby_vision"] is False
    assert original["rotation"] == 0
    assert original["fps"] == pytest.approx(30, abs=0.1)
    assert original["fps_steady"] is True
    assert original["slow_motion"] is False
    assert original["seconds"] == pytest.approx(2.0, abs=0.1)


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_facts_awkward_file_name(shape, tmp_path):
    clip = make_clip(tmp_path / "-my clip \u00e9.mov", 320, 180)

    manifest = convert([clip], shape, tmp_path / "out")

    assert manifest["clips"][0]["status"] == "done"
    assert manifest["clips"][0]["original"]["name"] == "-my clip \u00e9.mov"


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_facts_one_frame_clip(shape, tmp_path):
    clip = make_clip(tmp_path / "one.mp4", 320, 180, seconds=0.03)
    assert stream(probe(clip), "video")["nb_frames"] == "1"

    entry = convert([clip], shape, tmp_path / "out")["clips"][0]

    assert entry["status"] == "done"
    assert entry["original"]["fps_steady"] is True
    assert entry["original"]["slow_motion"] is False


def durations(path):
    info = probe(path)
    return float(stream(info, "video")["duration"]), float(stream(info, "audio")["duration"])


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_working_60fps_becomes_constant_30(shape, tmp_path):
    clip = make_clip(tmp_path / "fast.mp4", 320, 180, fps=60)

    entry = convert([clip], shape, tmp_path / "out")["clips"][0]

    assert entry["original"]["fps"] == pytest.approx(60, abs=0.5)
    working = tmp_path / "out" / "A.mp4"
    assert stream(probe(working), "video")["r_frame_rate"] == "30/1"
    picture, sound = durations(working)
    assert picture == pytest.approx(2.0, abs=0.1)
    assert sound == pytest.approx(2.0, abs=0.1)


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_working_uneven_timing_becomes_constant_30(shape, tmp_path):
    clip = make_clip(tmp_path / "uneven.mp4", 320, 180, vfr=True)
    original_picture, _ = durations(clip)

    entry = convert([clip], shape, tmp_path / "out")["clips"][0]

    assert entry["original"]["fps_steady"] is False
    working = tmp_path / "out" / "A.mp4"
    assert stream(probe(working), "video")["r_frame_rate"] == "30/1"
    picture, sound = durations(working)
    assert picture == pytest.approx(sound, abs=0.1)
    assert picture == pytest.approx(original_picture, abs=0.1)


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_working_silent_clip_gets_silence(shape, tmp_path):
    clip = make_clip(tmp_path / "quiet.mp4", 320, 180, sound=False)

    entry = convert([clip], shape, tmp_path / "out")["clips"][0]

    assert entry["original"]["has_sound"] is False
    assert entry["working"]["sound_added"] is True
    working = tmp_path / "out" / "A.mp4"
    audio = stream(probe(working), "audio")
    assert (audio["codec_name"], audio["channels"], int(audio["sample_rate"])) == ("aac", 2, 48000)
    picture, sound = durations(working)
    assert sound == pytest.approx(picture, abs=0.1)
    assert peak_volume(working) <= -80


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_working_short_sound_padded(shape, tmp_path):
    clip = make_clip(tmp_path / "short.mp4", 320, 180, sound_seconds=1.0)

    convert([clip], shape, tmp_path / "out")

    _, sound = durations(tmp_path / "out" / "A.mp4")
    assert sound == pytest.approx(2.0, abs=0.1)


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_manifest_second_run_replaces_last_job(shape, tmp_path):
    clips = [make_clip(tmp_path / "one.mp4", 320, 180), make_clip(tmp_path / "two.mp4", 320, 180)]
    out = tmp_path / "out"
    out.mkdir()
    keep = out / "join-tall-test.mp4"
    keep.write_bytes(b"a joined video that must stay")

    convert(clips, shape, out)
    assert (out / "B.mp4").exists()
    manifest = convert(clips[:1], shape, out)

    assert (out / "A.mp4").exists()
    assert not (out / "B.mp4").exists()
    assert len(manifest["clips"]) == 1
    assert keep.read_bytes() == b"a joined video that must stay"


def test_clear_last_job_never_touches_an_input_or_other_files(tmp_path):
    for name in ["A.mp4", "B.part.mp4", "C-photo.jpg", "manifest.json", "manifest.json.tmp"]:
        (tmp_path / name).write_bytes(b"old")
    for name in ["notes.txt", "join-wide-1.mp4", "ABCD.mp4", "abc.mp4"]:
        (tmp_path / name).write_bytes(b"other")

    clear_last_job(tmp_path, [tmp_path / "A.mp4"])

    assert sorted(path.name for path in tmp_path.iterdir()) == ["A.mp4", "ABCD.mp4", "abc.mp4", "join-wide-1.mp4", "notes.txt"]


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_manifest_same_file_twice_gets_two_letters(shape, tmp_path):
    clip = make_clip(tmp_path / "in.mp4", 320, 180)

    manifest = convert([clip, clip], shape, tmp_path / "out")

    assert [(c["letter"], c["status"]) for c in manifest["clips"]] == [("A", "done"), ("B", "done")]
    assert (tmp_path / "out" / "A.mp4").exists()
    assert (tmp_path / "out" / "B.mp4").exists()


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_manifest_letters_follow_given_order(shape, tmp_path):
    long_clip = make_clip(tmp_path / "long.mp4", 320, 180, seconds=3)
    short_clip = make_clip(tmp_path / "short.mp4", 320, 180, seconds=2)

    manifest = convert([long_clip, short_clip], shape, tmp_path / "out")

    assert [(c["letter"], c["number"], c["original"]["name"]) for c in manifest["clips"]] == [
        ("A", 1, "long.mp4"), ("B", 2, "short.mp4")]
    assert float(probe(tmp_path / "out" / "A.mp4")["format"]["duration"]) == pytest.approx(3.0, abs=0.1)
    assert float(probe(tmp_path / "out" / "B.mp4")["format"]["duration"]) == pytest.approx(2.0, abs=0.1)


def test_letters_and_ordinals():
    assert [letter(n) for n in (1, 26, 27, 28, 52, 53, 702, 703)] == ["A", "Z", "AA", "AB", "AZ", "BA", "ZZ", "AAA"]
    assert [ordinal(n) for n in (1, 2, 10)] == ["first", "second", "tenth"]
    assert [ordinal(n) for n in (11, 12, 13, 21, 22, 23, 101, 111)] == [
        "11th", "12th", "13th", "21st", "22nd", "23rd", "101st", "111th"]


BT709 = ("bt709", "bt709", "bt709")


def colour_tags(path):
    video = stream(probe(path), "video")
    return video["color_transfer"], video["color_primaries"], video["color_space"]


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_hdr_hlg_clip_is_tone_mapped_not_relabelled(shape, tmp_path, small_caps):
    clip = make_clip(tmp_path / "hlg.mp4", 640, 360, pattern="flat", hdr="hlg")

    manifest = convert([clip], shape, tmp_path / "out")

    (entry,) = manifest["clips"]
    assert entry["status"] == "done"
    assert entry["original"]["hdr"] == "hlg"
    assert entry["working"]["colour_converted"] is True
    assert any("tone-mapped" in note for note in entry["notes"])
    working = tmp_path / "out" / "A.mp4"
    assert mean_luma(working) < 112  # a merely relabelled copy would stay near 124
    assert colour_tags(working) == BT709
    assert stream(probe(working), "video")["pix_fmt"] == "yuv420p"


@pytest.mark.parametrize("shape", ["tall", "wide"])
@pytest.mark.parametrize("hdr", ["pq", "bt2020"])
def test_hdr_pq_and_gamut_only_convert(shape, hdr, tmp_path, small_caps):
    clip = make_clip(tmp_path / f"{hdr}.mp4", 640, 360, hdr=hdr)

    manifest = convert([clip], shape, tmp_path / "out")

    (entry,) = manifest["clips"]
    assert entry["status"] == "done"
    assert entry["original"]["hdr"] == hdr
    assert entry["working"]["colour_converted"] is True
    assert colour_tags(tmp_path / "out" / "A.mp4") == BT709


def test_hdr_colour_notes():
    assert colour_notes("hlg", True) == ["HDR (HLG) was tone-mapped to ordinary colour. The Dolby Vision layer was ignored."]
    assert colour_notes("hlg", False) == ["HDR (HLG) was tone-mapped to ordinary colour."]
    assert colour_notes("pq", False) == ["HDR (PQ) was tone-mapped to ordinary colour."]
    assert colour_notes("bt2020", False) == ["Wide-gamut colour (BT.2020) was converted to ordinary colour."]
    assert "Dolby" not in colour_notes("bt2020", False)[0]
    assert colour_notes(None, False) == []


def test_hdr_chain_reads_settings(monkeypatch):
    monkeypatch.setattr(settings, "TONEMAP", "mobius")
    monkeypatch.setattr(settings, "TONEMAP_NPL", 800)
    hlg = {"color_transfer": "arib-std-b67", "color_primaries": "bt2020", "color_space": "bt2020nc", "color_range": "tv"}

    chain = video_chain(hlg, 1080, 1920)

    for part in ("tonemap=mobius", "npl=800", "tin=arib-std-b67", "pin=bt2020", "min=bt2020nc", "rin=tv", "format=gbrpf32le"):
        assert part in chain
    assert chain.startswith("fps=")
    assert "zscale" not in video_chain(hlg, 1080, 1920, tonemap=False)
    assert "tonemap" not in video_chain({"color_primaries": "bt2020"}, 640, 360)  # gamut-only: no tone map


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_fallback_colour_when_tonemap_fails(shape, tmp_path, monkeypatch, capsys, small_caps):
    monkeypatch.setattr(settings, "TONEMAP", "nosuchoperator")
    clip = make_clip(tmp_path / "hlg.mp4", 640, 360, pattern="flat", hdr="hlg")

    manifest = convert([clip], shape, tmp_path / "out")

    sentence = "The colour of the first file, hlg.mp4, could not be converted, so its colour is unchanged and may look flat."
    (entry,) = manifest["clips"]
    assert entry["status"] == "done"
    assert entry["working"]["colour_converted"] is False
    assert sentence in entry["notes"]
    assert sentence in capsys.readouterr().out
    assert mean_luma(tmp_path / "out" / "A.mp4") >= 112  # the plain path, colour unchanged
    assert not [p for p in (tmp_path / "out").iterdir() if ".part." in p.name]


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_slow_motion_120fps_flagged_and_real_time(shape, tmp_path, small_caps):
    clip = make_clip(tmp_path / "slow.mp4", 640, 360, seconds=2, fps=120)

    manifest = convert([clip], shape, tmp_path / "out")

    (entry,) = manifest["clips"]
    assert entry["original"]["slow_motion"] is True
    assert entry["original"]["fps"] == pytest.approx(120, abs=1)
    assert entry["working"]["fps"] == 30
    assert entry["working"]["seconds"] == pytest.approx(2.0, abs=0.1)
    assert any("was shot as slow motion at 120 fps" in note for note in entry["notes"])


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_slow_motion_60fps_not_flagged(shape, tmp_path, small_caps):
    clip = make_clip(tmp_path / "fast.mp4", 640, 360, seconds=2, fps=60)

    (entry,) = convert([clip], shape, tmp_path / "out")["clips"]

    assert entry["original"]["slow_motion"] is False
    assert not any("slow motion" in note for note in entry["notes"])


def manifest_of(folder):
    return json.loads((folder / "manifest.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_refuse_oversized_file_others_convert(shape, tmp_path, monkeypatch, capsys, small_caps):
    monkeypatch.setattr(settings, "MAX_ATTACHMENT_BYTES", 1_000_000)
    first = make_clip(tmp_path / "one.mp4", 320, 180)
    big = tmp_path / "big.mov"
    with big.open("wb") as handle:
        handle.truncate(1_000_001)  # sparse: takes no real disk space
    third = make_clip(tmp_path / "three.mp4", 320, 180)

    manifest = convert([first, big, third], shape, tmp_path / "out")

    assert [(c["letter"], c["status"]) for c in manifest["clips"]] == [("A", "done"), ("B", "skipped"), ("C", "done")]
    skipped = manifest["clips"][1]
    assert skipped["sentence"].startswith("The second file, big.mov, is ")
    assert "over the " in skipped["sentence"]
    assert "limit, so it was left out" in skipped["sentence"]
    assert skipped["kind"] is None
    assert skipped["original"]["name"] == "big.mov"
    assert skipped["original"]["bytes"] == 1_000_001
    assert skipped["sentence"] in capsys.readouterr().out
    assert (tmp_path / "out" / "C.mp4").exists()
    assert not (tmp_path / "out" / "B.mp4").exists()


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_unreadable_text_empty_and_audio_only_files(shape, tmp_path, small_caps):
    clip = make_clip(tmp_path / "ok.mp4", 320, 180)
    text = tmp_path / "notes.mov"
    text.write_text("this is not a video", encoding="utf-8")
    empty = tmp_path / "empty.mp4"
    empty.write_bytes(b"")
    beep = make_audio(tmp_path / "beep.m4a")

    manifest = convert([clip, text, empty, beep], shape, tmp_path / "out")

    assert [(c["letter"], c["status"]) for c in manifest["clips"]] == [
        ("A", "done"), ("B", "skipped"), ("C", "skipped"), ("D", "skipped")]
    assert [c["sentence"] for c in manifest["clips"][1:]] == [
        "The second file, notes.mov, could not be read as a video or a photo.",
        "The third file, empty.mp4, could not be read as a video or a photo.",
        "The fourth file, beep.m4a, could not be read as a video or a photo.",
    ]
    assert all("detail" in c for c in manifest["clips"][1:])
    assert not [p for p in (tmp_path / "out").iterdir() if p.name[0] in "BCD"]


def test_refuse_missing_file(tmp_path, monkeypatch, capsys, small_caps):
    monkeypatch.setattr(v2r.normalize, "WORK_DIR", tmp_path / "work")

    assert main(["normalize", "--shape", "wide", str(tmp_path / "gone.mov")]) == 1

    (entry,) = manifest_of(tmp_path / "work")["clips"]
    assert entry["sentence"] == "The first file, gone.mov, was not found."
    assert entry["original"]["bytes"] is None
    assert "The first file, gone.mov, was not found." in capsys.readouterr().out


def test_refuse_no_files_usage_error():
    with pytest.raises(SystemExit) as stopped:
        main(["normalize", "--shape", "wide"])
    assert stopped.value.code == 2


def test_manifest_all_skipped_exit_1(tmp_path, monkeypatch):
    monkeypatch.setattr(v2r.normalize, "WORK_DIR", tmp_path / "work")
    one, two = tmp_path / "one.mov", tmp_path / "two.mov"
    one.write_text("no", encoding="utf-8")
    two.write_bytes(b"")

    assert main(["normalize", "--shape", "tall", str(one), str(two)]) == 1

    manifest = manifest_of(tmp_path / "work")
    assert manifest["finished"] is True
    assert manifest["stopped"] is None
    assert [c["status"] for c in manifest["clips"]] == ["skipped", "skipped"]


def test_manifest_letters_beyond_z():
    assert [letter(n) for n in (1, 26, 27, 28, 52, 53, 702, 703)] == ["A", "Z", "AA", "AB", "AZ", "BA", "ZZ", "AAA"]


def test_refuse_ordinal_wording():
    words = {1: "first", 2: "second", 10: "tenth", 11: "11th", 12: "12th", 13: "13th",
             21: "21st", 22: "22nd", 23: "23rd", 101: "101st", 111: "111th"}
    assert {n: ordinal(n) for n in words} == words


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_manifest_attachment_count_not_enforced(shape, tmp_path, monkeypatch, small_caps):
    monkeypatch.setattr(settings, "MAX_ATTACHMENTS", 1)
    clips = [make_clip(tmp_path / "one.mp4", 320, 180), make_clip(tmp_path / "two.mp4", 320, 180)]

    manifest = convert(clips, shape, tmp_path / "out")

    assert [c["status"] for c in manifest["clips"]] == ["done", "done"]


def test_refuse_whole_run_out_of_room_sentence(tmp_path, monkeypatch, capsys, small_caps):
    monkeypatch.setattr(v2r.normalize, "WORK_DIR", tmp_path / "work")
    clip = make_clip(tmp_path / "one.mp4", 320, 180)

    def no_room(command, part, final):
        raise OSError(errno.ENOSPC, "No space left on device")

    monkeypatch.setattr(v2r.normalize, "run_ffmpeg", no_room)

    assert main(["normalize", "--shape", "tall", str(clip)]) == 1

    err = capsys.readouterr().err
    assert "ran out of room" in err
    assert "fewer clips" in err
    manifest = manifest_of(tmp_path / "work")
    assert manifest["finished"] is False
    assert "ran out of room" in manifest["stopped"]
    assert not [p for p in (tmp_path / "work").iterdir() if ".part." in p.name]
