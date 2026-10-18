"""Extra stills: where look adds a still besides the one-a-second rhythm (D-01, D-17), and proof that one lands on a moment."""

from v2r import settings
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
