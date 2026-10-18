"""Extra stills: where look adds a still besides the one-a-second rhythm (D-01, D-17), and proof that one lands on a moment."""

import json

import pytest
from media import LOOK_FPS, make_bursts_clip, make_look_clip, make_manifest, white_share

from v2r import settings
from v2r.__main__ import main
from v2r.look import pick

FPS = 30


def halves_of(count, movement=None, state="still", loudness=None):
    """`count` half-second entries; `movement` and `loudness` map a half's index to a number (others: 0 and None)."""
    movement, loudness = movement or {}, loudness or {}
    return [
        {"t": i / 2, "movement": movement.get(i, 0.0), "camera_state": state, "loudness": loudness.get(i)}
        for i in range(count)]


def measured_of(halves, frames=None, sound=None, shot_changes=None):
    return {"halves": halves, "frames": frames or [], "sound": sound or [], "shot_changes": shot_changes}


def base_of(seconds):
    return pick.base_times(seconds, FPS, 1.0)


def test_peaks_rule():
    assert pick.peaks([0, 0, 3.0, 0, 0], 0.5) == [(2, 6.0)]
    assert pick.peaks([0, 0, 0, 0], 0.5) == []
    assert pick.peaks([0, 0.1, 0, 0.2, 0, 0.1], 0.5) == []  # a calm clip's flicker sits under the floor
    assert [index for index, _ in pick.peaks([0, 3.0, 0, 3.0, 0], 0.5)] == [1, 3]  # equal peaks: earlier first
    assert pick.peaks([0, 0, 3.0, 0, 0, 4.0, 0, 0, 0], 0.5)[0][0] == 5  # a stronger one first
    assert pick.peaks([None, None], 0.5) == []
    assert [index for index, _ in pick.peaks([0, None, 3.0, None, 0], 0.5)] == [2]  # a missing neighbour does not count


def test_extras_gap_in_frames():
    # Base stills at 0, 1, 2 ... seconds, so at frames 0, 30, 60, 90, 120. The gap is round(0.3 x 30) = 9 frames:
    # a still exactly 9 frames from a base still (99) is kept, 8 frames away (98) is dropped.
    base = base_of(9.0)
    kept = pick.extra_times(measured_of([], shot_changes=[99 / FPS - settings.CUT_STILL_DELAY]), base, 9.0, FPS)
    assert [round(e["t"] * FPS) for e in kept] == [99]
    dropped = pick.extra_times(measured_of([], shot_changes=[98 / FPS - settings.CUT_STILL_DELAY]), base, 9.0, FPS)
    assert dropped == []
    before = pick.extra_times(measured_of([], shot_changes=[81 / FPS - settings.CUT_STILL_DELAY]), base, 9.0, FPS)
    assert [round(e["t"] * FPS) for e in before] == [81]  # 9 frames before frame 90
    assert pick.extra_times(measured_of([], shot_changes=[82 / FPS - settings.CUT_STILL_DELAY]), base, 9.0, FPS) == []
    # two extras keep the gap from each other too
    pair = pick.extra_times(measured_of([], shot_changes=[99 / FPS - 0.1, 108 / FPS - 0.1]), base, 9.0, FPS)
    assert len(pair) == 2
    close = pick.extra_times(measured_of([], shot_changes=[99 / FPS - 0.1, 107 / FPS - 0.1]), base, 9.0, FPS)
    assert len(close) == 1


def test_extras_cap_and_order():
    base = pick.base_times(12.0, FPS, 2.0)  # 6 base stills, at 0, 2 ... 10 s: a cap of 2
    assert len(base) == 6
    halves = halves_of(24, movement={5: 3.0, 9: 6.0})  # a weak peak at 2.5-3.0 and a strong one at 4.5-5.0
    extras = pick.extra_times(measured_of(halves, shot_changes=[8.4]), base, 12.0, FPS)
    # the cut and the strong peak are chosen, not the weak peak
    assert [(e["why"], round(e["t"], 2)) for e in extras] == [("movement", 4.73), ("shot change", 8.5)]
    # without the cut, the strong and the weak peak
    pair = pick.extra_times(measured_of(halves), base, 12.0, FPS)
    assert [e["why"] for e in pair] == ["movement", "movement"]
    # equal scores go to the earlier time
    tie = pick.extra_times(measured_of(halves_of(24, movement={5: 3.0, 9: 3.0, 13: 3.0})), base, 12.0, FPS)
    assert [round(e["t"]) for e in tie] == [3, 5]
    assert 2.5 < tie[0]["t"] < 3.0 and 4.5 < tie[1]["t"] < 5.0


def test_movement_peaks_only_with_still_camera():
    base = pick.base_times(12.0, FPS, 2.0)
    for state in ("shaky", "panning"):
        assert pick.extra_times(measured_of(halves_of(24, movement={9: 6.0}, state=state)), base, 12.0, FPS) == []
    assert len(pick.extra_times(measured_of(halves_of(24, movement={9: 6.0}, state=None)), base, 12.0, FPS)) == 1
    mixed = halves_of(24, movement={9: 6.0, 3: 6.0})
    mixed[3]["camera_state"] = "panning"
    (only,) = pick.extra_times(measured_of(mixed), base, 12.0, FPS)
    assert 4.5 <= only["t"] <= 5.0


def test_movement_still_at_centre_of_burst():
    frames = [{"t": i / 10, "movement": 6.0 if 42 <= i <= 49 else 0.0, "cut": False} for i in range(80)]
    halves = halves_of(16, movement={8: 3.6, 9: 6.0})
    (extra,) = pick.extra_times(measured_of(halves, frames=frames), base_of(8.0), 8.0, FPS)
    assert extra["why"] == "movement"
    assert 4.3 <= extra["t"] <= 4.7


def test_sound_still_at_loudest_reading():
    sound = [{"t": 3.5 + i / 10, "loudness": -30.0 + (5 - abs(i - 2)) * 3} for i in range(5)]  # loudest at 3.7
    halves = halves_of(10, loudness={7: -15.0})
    (extra,) = pick.extra_times(measured_of(halves, sound=sound), base_of(5.0), 5.0, FPS)
    assert extra["why"] == "sound"
    assert abs(extra["t"] - 3.7) < 1 / FPS


def test_lone_beep_in_silence_is_a_peak():
    sound = [{"t": i / 10, "loudness": None} for i in range(80)]
    sound[37] = {"t": 3.7, "loudness": -12.0}
    halves = halves_of(16, loudness={7: -12.0})  # every other half is silent: null
    (extra,) = pick.extra_times(measured_of(halves, sound=sound), base_of(8.0), 8.0, FPS)
    assert (extra["why"], round(extra["t"], 1)) == ("sound", 3.7)
    # no sound readings at all (nothing measured): no sound peaks
    assert pick.extra_times(measured_of(halves, sound=[]), base_of(8.0), 8.0, FPS) == []


def test_no_extras_when_nothing_happens():
    calm = halves_of(16, movement={i: 0.1 * (i % 2) for i in range(16)})
    assert pick.extra_times(measured_of(calm, shot_changes=[]), base_of(8.0), 8.0, FPS) == []
    silent = [{"t": i / 10, "loudness": None} for i in range(80)]
    assert pick.extra_times(measured_of(halves_of(16), sound=silent), base_of(8.0), 8.0, FPS) == []
    assert pick.extra_times(measured_of([]), base_of(8.0), 8.0, FPS) == []  # nothing was measured


def test_short_clip_cap_zero():
    base = base_of(2.0)
    assert len(base) == 2
    measured = measured_of(halves_of(4, movement={2: 6.0}), shot_changes=[1.4])
    assert pick.extra_times(measured, base, 2.0, FPS) == []


# ---- through the whole of look, on clips made with a known answer, in both shapes ----

SIZE = {"tall": (360, 640), "wide": (640, 360)}  # the clip sizes swap with the shape
MIN_GAP_FRAMES = round(settings.EXTRA_MIN_GAP * LOOK_FPS)


def run_look(tmp_path, shape, make, kind="video"):
    """Make clip A with `make(path, width, height)`, run look on it, and return (work folder, A's look.json entry)."""
    work = tmp_path / "work"
    work.mkdir()
    width, height = SIZE[shape]
    make(work / "A.mp4", width, height)
    make_manifest(work, shape, [{"file": work / "A.mp4", "kind": kind}])
    assert main(["look", str(work)]) == 0
    (clip,) = json.loads((work / "look.json").read_text(encoding="utf-8"))["clips"]
    stills = clip["stills"]
    frames = [round(still["t"] * LOOK_FPS) for still in stills]
    assert all(later - earlier >= MIN_GAP_FRAMES for earlier, later in zip(frames, frames[1:]))
    assert [still["t"] for still in stills] == sorted(still["t"] for still in stills)
    return work, clip


def extras_of(clip, why=None):
    return [still for still in clip["stills"] if still["why"] != "rhythm" and why in (None, still["why"])]


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_moment_still_lands_on_square(shape, tmp_path):
    # visible only from 4.2 to 4.8 s: no base still (4.0, 5.0) can show it, so only an extra can
    work, clip = run_look(tmp_path, shape, lambda p, w, h: make_look_clip(p, w, h, pattern="square", start=4.2, end=4.8))
    assert not [s for s in clip["stills"] if s["why"] == "rhythm" and 4.0 < s["t"] < 5.0]
    inside = [s for s in extras_of(clip, "movement") if 4.2 <= s["t"] <= 4.8]
    assert inside, clip["stills"]
    base = next(s for s in clip["stills"] if s["t"] == 4.0)
    moment = white_share(work / inside[0]["sheet"], inside[0]["box"])
    before = white_share(work / base["sheet"], base["box"])
    assert moment >= before + 0.01


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_cut_still_after_shot_change(shape, tmp_path):
    _, clip = run_look(tmp_path, shape, lambda p, w, h: make_look_clip(p, w, h, pattern="cut", start=3.4))
    assert [s for s in extras_of(clip, "shot change") if 3.4 < s["t"] <= 3.6 + 1e-6], clip["stills"]


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_sound_still_at_beep(shape, tmp_path):
    _, clip = run_look(tmp_path, shape, lambda p, w, h: make_look_clip(p, w, h, beep=(3.4, 3.6)))
    assert [s for s in extras_of(clip, "sound") if abs(s["t"] - 3.5) <= 0.3 + 1e-6], clip["stills"]


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_extras_cap_holds(shape, tmp_path):
    # five quick bursts, each well clear of the base stills: all five qualify and only the cap (8 // 3 = 2) stops them
    _, clip = run_look(
        tmp_path, shape, lambda p, w, h: make_bursts_clip(p, w, h, [1.35, 2.35, 4.35, 5.35, 6.35]))
    assert len([s for s in clip["stills"] if s["why"] == "rhythm"]) == 8
    extras = extras_of(clip)
    assert len(extras) == 2, clip["stills"]
    for still in extras:  # each one lands in a burst, not beside it
        assert any(start - 0.05 <= still["t"] <= start + 0.35 for start in (1.35, 2.35, 4.35, 5.35, 6.35)), still


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_no_extras_static_silent(shape, tmp_path):
    _, clip = run_look(tmp_path, shape, lambda p, w, h: make_look_clip(p, w, h))
    assert extras_of(clip) == []
    assert len(clip["stills"]) == 8


@pytest.mark.parametrize("shape", ["tall", "wide"])
def test_photo_gets_no_extras(shape, tmp_path):
    _, clip = run_look(
        tmp_path, shape, lambda p, w, h: make_look_clip(p, w, h, pattern="grey", level="0x7E7E7E", beep=(3.4, 3.6)),
        kind="photo")
    assert len(clip["stills"]) == 1
    assert clip["stills"][0]["why"] == "rhythm"
