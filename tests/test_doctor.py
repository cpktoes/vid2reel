"""Tests for `v2r doctor`: the FFmpeg lists and the fast check normalize can call."""

from v2r import doctor, normalize

OLD_FILTERS = ["scale", "crop", "zscale", "tonemap", "loudnorm", "drawtext"]
NEW_FILTERS = ["format", "fps", "setsar", "setpts", "loop", "transpose", "hflip", "vflip", "aresample", "apad", "anullsrc"]

LOOK_FILTERS = ["select", "signalstats", "blurdetect", "scdet", "deshake", "ebur128", "metadata", "ametadata", "fps", "scale"]


def test_doctor_lists_every_normalize_piece():
    for name in OLD_FILTERS + NEW_FILTERS:
        assert name in doctor.FILTERS
    for name in ["hevc", "h264", "aac", "mjpeg", "png"]:
        assert name in doctor.DECODERS


def test_doctor_reports_decoders(capsys, monkeypatch):
    monkeypatch.setattr(doctor, "reach", lambda host: None)  # never use the network
    doctor.run()
    out = capsys.readouterr().out
    for name in ["hevc", "h264", "aac", "mjpeg", "png"]:
        assert f"The {name} decoder is available." in out
    assert "The anullsrc filter is available." in out
    assert "MISSING" not in out


def test_doctor_missing_features_empty_here():
    assert doctor.missing_ffmpeg_features() == []


def test_doctor_missing_features_names_what_is_missing(monkeypatch):
    monkeypatch.setattr(doctor, "FILTERS", doctor.FILTERS + ["nosuchfilter"])
    monkeypatch.setattr(doctor, "DECODERS", doctor.DECODERS + ["nosuchdecoder"])
    assert doctor.missing_ffmpeg_features() == ["the nosuchfilter filter", "the nosuchdecoder decoder"]


def test_doctor_missing_features_only_checks_the_names_it_is_given(monkeypatch):
    monkeypatch.setattr(doctor, "FILTERS", doctor.FILTERS + ["nosuchfilter"])
    assert doctor.missing_ffmpeg_features(["libx264"], ["scale"], ["h264"]) == []
    assert doctor.missing_ffmpeg_features([], ["scale", "nosuchfilter"], []) == ["the nosuchfilter filter"]
    assert doctor.missing_ffmpeg_features(["nosuchencoder"], [], ["nosuchdecoder"]) == [
        "the nosuchencoder encoder", "the nosuchdecoder decoder"]
    assert doctor.missing_ffmpeg_features([], [], []) == []


def test_doctor_lists_every_look_filter():
    for name in LOOK_FILTERS + OLD_FILTERS + NEW_FILTERS:
        assert name in doctor.FILTERS


def test_doctor_reports_look_filters(capsys, monkeypatch):
    monkeypatch.setattr(doctor, "reach", lambda host: None)  # never use the network
    doctor.run()
    out = capsys.readouterr().out
    for name in LOOK_FILTERS:
        assert f"The {name} filter is available." in out
    assert "MISSING" not in out


def test_normalize_needs_no_look_filter():
    for name in ["select", "signalstats", "blurdetect", "scdet", "deshake", "ebur128", "metadata", "ametadata"]:
        assert name not in normalize.NEEDED_FILTERS
