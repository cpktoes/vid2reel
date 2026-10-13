"""Tests for `v2r doctor`: the FFmpeg lists and the fast check normalize can call."""

from v2r import doctor

OLD_FILTERS = ["scale", "crop", "zscale", "tonemap", "loudnorm", "drawtext"]
NEW_FILTERS = ["format", "fps", "setsar", "setpts", "loop", "transpose", "hflip", "vflip", "aresample", "apad", "anullsrc"]


def test_doctor_lists_every_normalize_piece():
    assert doctor.FILTERS[:6] == OLD_FILTERS
    for name in NEW_FILTERS:
        assert name in doctor.FILTERS
    assert doctor.DECODERS == ["hevc", "h264", "aac", "mjpeg", "png"]


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
