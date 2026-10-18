"""Candidate moments: ranked stretches of facts (D-18), proved on hand-made numbers and on clips with a known answer.

Candidates are an order, never a choice (D-04): no reason judges, and nothing in look.json marks one as selected.
"""

import json
import re

import pytest
from media import make_look_clip, make_manifest

from v2r import settings
from v2r.__main__ import main
from v2r.look import pick

FPS = 30


def halves_of(count, state="still", movement=0.0, sharp=True, subject=None, overrides=None):
    """`count` half-second entries; `overrides` maps a half's index to a dictionary of values that replace the default."""
    overrides = overrides or {}
    entries = []
    for i in range(count):
        entry = {
            "t": i / 2, "movement": movement, "camera_state": state, "sharp": sharp,
            "subject": (movement >= settings.SUBJECT_MOVEMENT_MIN) if subject is None and state == "still" else subject,
        }
        entry.update(overrides.get(i, {}))
        entries.append(entry)
    return entries


def stills_of(letter, times):
    return [{"label": f"{letter} {t:04.1f}", "t": t} for t in times]


def spans(found):
    return [(c["start"], c["end"]) for c in found]


def test_windows_short_clip():
    # edge LOOK-04 empty: a clip shorter than one window is judged as a single window from 0 to its end
    assert pick.windows(1.5, FPS) == [(0.0, 1.5)]
    assert pick.windows(2.0, FPS) == [(0.0, 2.0)]
    assert pick.windows(3.0, FPS) == [(0.0, 2.0), (0.5, 2.5), (1.0, 3.0)]
    found = pick.candidates(halves_of(3), [], stills_of("A", [0.0, 1.0]), [], 1.5, FPS)
    assert spans(found) == [(0.0, 1.5)]


def test_window_exclusions():
    seconds = 8.0
    base = halves_of(16, movement=2.0)
    stills = stills_of("A", range(8))
    shaky = halves_of(16, movement=2.0, overrides={6: {"camera_state": "shaky"}})  # the half 3.0 to 3.5
    for found in (pick.candidates(shaky, [], stills, [], seconds, FPS),):
        assert all(not (c["start"] < 3.5 and c["end"] > 3.0) for c in found)
        assert found
    soft = halves_of(16, movement=2.0, overrides={6: {"sharp": False}})
    assert all(not (c["start"] < 3.5 and c["end"] > 3.0) for c in pick.candidates(soft, [], stills, [], seconds, FPS))
    # a cut at 3.4 inside: nothing crosses it
    cut = pick.candidates(base, [3.4], stills, [], seconds, FPS)
    assert cut and all(not (c["start"] < 3.4 < c["end"]) for c in cut)
    # edge LOOK-04 adjacency: a cut exactly at the start or the end of a window does not exclude it
    edge = pick.candidates(base, [3.0], stills, [], 5.0, FPS)
    assert (3.0, 5.0) in spans(edge) and (0.0, 3.0) in spans(edge)  # windows ending and starting exactly at the cut
    at_end = pick.candidates(base, [5.0], stills, [], 5.0, FPS)
    assert any(c["start"] == 0.0 and c["end"] == 4.0 for c in at_end)
    only_window = pick.candidates(halves_of(4), [1.0], stills, [], 2.0, FPS)
    assert only_window == []  # strictly inside the only window
    assert pick.candidates(halves_of(4), [0.0], stills, [], 2.0, FPS) != []
    assert pick.candidates(halves_of(4), [2.0], stills, [], 2.0, FPS) != []
    # values that were not measured never leave a window out
    unmeasured = halves_of(16, state=None, sharp=None, movement=None)
    assert pick.candidates(unmeasured, None, stills, [], seconds, FPS)


def test_ranking_order():
    # edge LOOK-04 ordering: tier first, then more movement, then the earlier start
    seconds = 12.0
    halves = halves_of(24)
    for i in range(0, 4):  # 0 to 2 s: a panning camera with plenty of movement
        halves[i].update(camera_state="panning", movement=9.0, subject=None)
    for i in range(4, 8):  # 2 to 4 s: still, little movement
        halves[i].update(movement=1.0, subject=True)
    for i in range(8, 12):  # 4 to 6 s: still, more movement
        halves[i].update(movement=3.0, subject=True)
    for i in range(12, 24):  # 6 to 12 s: unmeasured camera
        halves[i].update(camera_state=None, movement=5.0, subject=None)
    found = pick.candidates(halves, [], stills_of("A", range(12)), [], seconds, FPS)
    assert [c["rank"] for c in found] == list(range(1, len(found) + 1))
    first = found[0]
    # the busiest still stretch (4 to 6 s) merges with the neighbouring windows that score alike, but stays inside 3.5 to 6
    assert first["start"] >= 3.5 - 1e-9 and first["end"] <= 6.0 + 1e-9 and "steady camera" in first["reason"]
    assert "subject moving" in first["reason"]
    # the quieter still windows overlap the stretch above, so the next in order is the panning one, though busier
    assert "camera panning" in found[1]["reason"]
    reasons = " | ".join(c["reason"] for c in found)
    assert reasons.index("steady camera") < reasons.index("camera panning") < reasons.index("camera not measured")
    pan = next(c for c in found if "camera panning" in c["reason"])
    assert "subject moving" not in pan["reason"] and "nothing moving" not in pan["reason"]
    # equal scores come out in time order
    flat = pick.candidates(halves_of(8, movement=2.0), [], stills_of("A", range(4)), [], 4.0, FPS)
    assert [c["start"] for c in flat] == sorted(c["start"] for c in flat)


def test_merge_cap_no_overlap():
    # edge LOOK-04 adjacency: windows that score alike merge up to the cap, and stretches never overlap
    found = pick.candidates(halves_of(20, movement=2.0), [], stills_of("A", range(10)), [], 10.0, FPS)
    assert 1 <= len(found) <= settings.MAX_CANDIDATES
    assert all(c["end"] - c["start"] <= settings.CANDIDATE_MAX_SECONDS + 1e-9 for c in found)
    ordered = sorted(found, key=lambda c: c["start"])
    assert all(later["start"] >= earlier["end"] - 1e-9 for earlier, later in zip(ordered, ordered[1:]))
    assert spans(found) == [(0.0, 4.0), (4.0, 8.0), (8.0, 10.0)]  # touching, not overlapping
    # a longer clip is held to the most that may be listed
    long = pick.candidates(halves_of(80, movement=2.0), [], stills_of("A", range(40)), [], 40.0, FPS)
    assert len(long) == settings.MAX_CANDIDATES
    # windows whose movement differs by far do not merge
    unlike = halves_of(8)
    for i in range(4):
        unlike[i].update(movement=1.0)
    for i in range(4, 8):
        unlike[i].update(movement=9.0)
    parts = pick.candidates(unlike, [], stills_of("A", range(4)), [], 4.0, FPS)
    # the busier second half comes first; only a window with a mostly-quiet start is left out of its stretch
    assert parts and parts[0]["start"] >= 1.5 - 1e-9 and parts[0]["end"] == 4.0


def test_reason_text_exact():
    halves = halves_of(16, movement=0.0)
    for i in range(8, 12):  # 4.0 to 6.0 s: a subject moving
        halves[i].update(movement=3.0, subject=True)
    stills = stills_of("A", [0.0, 1.0, 2.0, 3.0, 4.0, 4.5, 5.0, 7.0])
    found = pick.candidates(halves, [], stills, [4.5], 8.0, FPS)
    assert found[0]["reason"] == "steady camera, sharp, subject moving, sound peak at 04.5; stills A 04.0, A 04.5, A 05.0"
    assert found[0]["stills"] == ["A 04.0", "A 04.5", "A 05.0"]
    assert found[0]["start"] <= 4.0 and found[0]["end"] >= 5.0  # the windows around 4 to 6 s merged
    # nothing moving, and no still inside
    plain = pick.candidates(halves_of(4), [], stills_of("A", [0.0, 7.0]), [], 2.0, FPS)
    assert plain[0]["reason"] == "steady camera, sharp, nothing moving; stills A 00.0"
    far = pick.candidates(halves_of(4), [], stills_of("A", [3.0]), [], 2.0, FPS)
    assert far[0]["reason"] == "steady camera, sharp, nothing moving; no still inside, nearest A 03.0"


def test_every_window_excluded_gives_empty():
    # edge LOOK-04 empty
    stills = stills_of("A", range(8))
    assert pick.candidates(halves_of(16, state="shaky"), [], stills, [], 8.0, FPS) == []
    assert pick.candidates(halves_of(16, sharp=False), [], stills, [], 8.0, FPS) == []
    assert pick.candidates(halves_of(16), [x + 0.5 for x in range(7)], stills, [], 8.0, FPS) == []
    assert pick.candidates([], [], stills, [], 8.0, FPS) != []  # nothing measured is not "excluded"


def test_sound_peaks_shared_with_extras():
    sound = [{"t": i / 10, "loudness": None} for i in range(80)]
    sound[37] = {"t": 3.7, "loudness": -12.0}
    halves = [{"t": i / 2, "movement": 0.0, "camera_state": "still", "loudness": -12.0 if i == 7 else None}
              for i in range(16)]
    measured = {"halves": halves, "frames": [], "sound": sound, "shot_changes": []}
    assert pick.sound_peak_times(measured) == [3.7]
    extras = pick.extra_times(measured, pick.base_times(8.0, FPS, 1.0), 8.0, FPS)
    assert [round(e["t"], 1) for e in extras if e["why"] == "sound"] == pick.sound_peak_times(measured)
    assert pick.sound_peak_times({"halves": halves, "sound": []}) == []
