"""Snap easing that keeps the motion (lib/tripo_ease.py): a fast step is retimed along the joint's own path, the raise inside it stays. No Blender."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import tripo_ease as E


def about_x(degrees: float) -> np.ndarray:
    half = np.radians(degrees) / 2.0
    return np.array([np.cos(half), np.sin(half), 0.0, 0.0])


def angle_of(q: np.ndarray) -> float:
    """The signed turn about x of a quaternion that turns about x."""

    return float(np.degrees(2.0 * np.arctan2(q[1], q[0])))


def raise_and_strike(count: int = 60, top: int = 30, strike: int = 34) -> list:
    """An arm that rises slowly to 120 degrees at `top`, then strikes back down to 0 in four frames, then rests."""

    angles = []
    for frame in range(count):
        if frame <= top:
            angles.append(120.0 * frame / top)
        elif frame <= strike:
            angles.append(120.0 * (1.0 - (frame - top) / (strike - top)))
        else:
            angles.append(0.0)
    return [about_x(a) for a in angles]


class Retime(unittest.TestCase):
    def test_a_fast_strike_is_eased_and_the_raise_stays(self) -> None:
        quats = raise_and_strike()
        frames = list(range(len(quats)))
        eased, windows = E.ease_turns(quats, frames, trigger=14.0, target=10.5)
        self.assertTrue(windows)
        self.assertLessEqual(max(E.turn_rates(eased, frames)), 10.5 + 1e-6)
        # the old rule (a straight slerp across the window) never reached the top; the retimed path comes within a few degrees of it
        # (the top key now falls between two sampled frames)
        self.assertGreater(max(angle_of(q) for q in eased), 115.0)

    def test_the_old_straight_slerp_would_have_lost_the_raise(self) -> None:
        quats = raise_and_strike()
        frames = list(range(len(quats)))
        _eased, windows = E.ease_turns(quats, frames, trigger=14.0, target=10.5)
        a, b = windows[0]
        flat = [E.slerp(quats[a], quats[b], (m - a) / (b - a)) for m in range(a, b + 1)]
        self.assertLess(max(angle_of(q) for q in flat), 110.0)

    def test_keys_keep_their_times_and_the_ends_of_the_window(self) -> None:
        quats = raise_and_strike()
        frames = list(range(len(quats)))
        eased, windows = E.ease_turns(quats, frames, trigger=14.0, target=10.5)
        self.assertEqual(len(eased), len(quats))
        a, b = windows[0]
        for k in list(range(0, a + 1)) + list(range(b, len(quats))):
            self.assertAlmostEqual(abs(float(eased[k] @ quats[k])), 1.0, places=9)

    def test_the_path_is_walked_in_order(self) -> None:
        quats = raise_and_strike()
        frames = list(range(len(quats)))
        eased, _windows = E.ease_turns(quats, frames, trigger=14.0, target=10.5)
        angles = [angle_of(q) for q in eased]
        top = int(np.argmax(angles))
        self.assertTrue(all(angles[k] <= angles[k + 1] + 1e-6 for k in range(top)))
        self.assertTrue(all(angles[k] >= angles[k + 1] - 1e-6 for k in range(top, len(angles) - 1)))

    def test_a_slow_clip_is_left_alone(self) -> None:
        quats = [about_x(2.0 * k) for k in range(30)]
        frames = list(range(30))
        eased, windows = E.ease_turns(quats, frames, trigger=14.0, target=10.5)
        self.assertEqual(windows, [])
        for a, b in zip(eased, quats):
            self.assertTrue(np.allclose(a, b))

    def test_uneven_key_times(self) -> None:
        quats = [about_x(a) for a in (0.0, 4.0, 8.0, 60.0, 64.0, 68.0, 72.0, 76.0, 80.0, 84.0, 88.0)]
        frames = [0.0, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0]
        eased, windows = E.ease_turns(quats, frames, trigger=14.0, target=10.5)
        self.assertTrue(windows)
        self.assertLessEqual(max(E.turn_rates(eased, frames)), 10.5 + 1e-6)

    def test_flips_are_put_on_one_hemisphere(self) -> None:
        quats = [about_x(10.0), -about_x(12.0), about_x(14.0)]
        fixed, flips = E.one_hemisphere(quats)
        self.assertEqual(flips, 1)
        self.assertTrue(all(float(fixed[k] @ fixed[k + 1]) > 0 for k in range(2)))


if __name__ == "__main__":
    unittest.main()
