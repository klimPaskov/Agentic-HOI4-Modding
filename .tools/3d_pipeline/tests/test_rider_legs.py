"""A seated rider's legs solved outside the mount's measured barrel (adapter/rider_legs.py), without Blender."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "adapter"))

import rider_legs


def barrel(widest: float) -> list:
    """A horse's barrel beside the seat: narrow at the spine, widest a fifth of the rider's height down, narrowing to the belly."""

    rows = []
    for step in range(12):
        depth = round(0.05 * step, 2)
        rows.append({"depth": depth, "half_width": round(widest * min(1.0, depth / 0.2) * (1.0 - max(0.0, depth - 0.3) / 0.4), 4)})
    return rows


HIP = (0.0, 0.05, 0.03)  # a hip joint 0.05 of the height out from the mid-plane, a little above the seat


class SolvedLegs(unittest.TestCase):
    def test_knee_ankle_and_segment_middles_clear_the_barrel(self) -> None:
        profile = barrel(0.2)
        legs = rider_legs.solve_leg(HIP, 0.24, 0.24, profile)
        self.assertTrue(legs["clear"])
        hip = np.asarray(HIP)
        for start, end, check in ((hip, legs["knee"], rider_legs.THIGH_CHECK), (legs["knee"], legs["ankle"], 0.5)):
            for point in (start + check * (end - start), end):
                self.assertGreaterEqual(point[1] + 1e-9, rider_legs.half_width(profile, -point[2]) + rider_legs.CLEARANCE)

    def test_a_wider_barrel_turns_the_thigh_further_out(self) -> None:
        narrow = rider_legs.solve_leg(HIP, 0.24, 0.24, barrel(0.12))
        wide = rider_legs.solve_leg(HIP, 0.24, 0.24, barrel(0.24))
        self.assertGreater(wide["thigh"][1], narrow["thigh"][1])
        self.assertGreater(wide["knee"][1], narrow["knee"][1])

    def test_the_thigh_reaches_forward_its_share_and_drops_the_rest(self) -> None:
        legs = rider_legs.solve_leg(HIP, 0.24, 0.24, barrel(0.2))
        forward, out, down = legs["thigh"]
        self.assertAlmostEqual(forward, rider_legs.THIGH_FORWARD, places=6)
        self.assertAlmostEqual(float(np.linalg.norm(legs["thigh"])), 1.0, places=6)
        self.assertLess(down, -out * 0.5)

    def test_a_wide_barded_barrel_keeps_the_knee_below_the_seat(self) -> None:
        """ZIN's barded warhorse, measured: the knee drops below the seat and stands about 0.21 of the rider's height out, where the fixed
        aim was measured by hand on the same horse."""

        widths = (0.116, 0.126, 0.15, 0.172, 0.181, 0.191, 0.192, 0.194, 0.121, 0.076, 0.0, 0.0)
        profile = [{"depth": round(0.05 * i, 2), "half_width": w} for i, w in enumerate(widths)]
        legs = rider_legs.solve_leg((0.0, 0.05, 0.03), 0.245, 0.245, profile)
        self.assertTrue(legs["clear"])
        self.assertLess(legs["knee"][2], -0.08)
        self.assertAlmostEqual(float(legs["knee"][1]), 0.21, delta=0.02)

    def test_the_shin_turns_out_no_further_than_the_barrel_needs(self) -> None:
        """One step less outward and the shin's middle or the ankle would be inside the clearance: the leg hugs the flank."""

        profile = barrel(0.24)
        legs = rider_legs.solve_leg(HIP, 0.24, 0.24, profile)
        self.assertTrue(legs["clear"])
        forward, out, up = legs["shin"] / -legs["shin"][2]
        tighter = np.array([forward, out - 0.02, up])
        end = legs["knee"] + 0.24 * tighter / np.linalg.norm(tighter)
        middle = 0.5 * (legs["knee"] + end)
        self.assertTrue(any(point[1] < rider_legs.half_width(profile, -point[2]) + rider_legs.CLEARANCE for point in (middle, end)))


class ShoulderTwist(unittest.TestCase):
    """The seat step's twist measure (rider_seat._hold_twist caps it at SEAT_TWIST_MAX)."""

    F, S, U = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)

    def test_square_shoulders_read_zero_and_side_on_ninety(self) -> None:
        self.assertAlmostEqual(rider_legs.shoulder_twist((0.0, 0.4, 0.0), self.F, self.S, self.U), 0.0)
        self.assertAlmostEqual(rider_legs.shoulder_twist((0.4, 0.0, 0.0), self.F, self.S, self.U), 90.0)

    def test_either_way_round_and_height_ignored(self) -> None:
        import math

        turned = (0.4 * math.sin(math.radians(50)), 0.4 * math.cos(math.radians(50)), 0.3)
        mirrored = (-turned[0], turned[1], -0.2)
        self.assertAlmostEqual(rider_legs.shoulder_twist(turned, self.F, self.S, self.U), 50.0, places=6)
        self.assertAlmostEqual(rider_legs.shoulder_twist(mirrored, self.F, self.S, self.U), 50.0, places=6)
        self.assertAlmostEqual(rider_legs.shoulder_twist((0.0, -0.4, 0.0), self.F, self.S, self.U), 0.0)


if __name__ == "__main__":
    unittest.main()


class HandClear(unittest.TestCase):
    """The seated hand against the mount's top ahead of the seat (lib/rider_fit.clip_profiles' `top` rows)."""

    ROWS = [{"ahead": 0.15, "out": 0.0, "top": 0.147}, {"ahead": 0.15, "out": 0.05, "top": 0.143},
            {"ahead": 0.15, "out": 0.15, "top": None}, {"ahead": 0.3, "out": 0.0, "top": 0.2}]

    def test_a_hand_in_the_withers_is_not_clear(self):
        # the zinnish lancer's defend: the rein hand 0.148 ahead, 0.02 out and 0.099 up, the withers there 0.147 up
        self.assertFalse(rider_legs.hand_clear([(0.148, 0.02, 0.099)], self.ROWS))
        self.assertAlmostEqual(rider_legs.top_at(self.ROWS, 0.148, -0.02), 0.147)

    def test_a_hand_above_or_beside_the_mount_is_clear(self):
        self.assertTrue(rider_legs.hand_clear([(0.148, 0.02, 0.2)], self.ROWS))
        self.assertTrue(rider_legs.hand_clear([(0.148, 0.15, 0.0)], self.ROWS))  # an empty cell: beside the neck
        self.assertTrue(rider_legs.hand_clear([(-0.05, 0.0, -0.1)], self.ROWS))  # behind the seat, over the rider's own lap


class PlanDrop(unittest.TestCase):
    """A seated rider's dropped weapon lies on the ground clear of the fallen mount and rider, near the hand (rider_legs.plan_drop)."""

    def test_an_open_ground_takes_the_place_below_the_hand(self):
        plan = rider_legs.plan_drop((0.1, 0.2, 0.3), (0.0, 0.0, 1.0), 1.7, 0.28, -0.9, [])
        self.assertTrue(plan["found"])
        np.testing.assert_allclose(plan["grip"], (0.1, 0.2, -0.89))
        self.assertAlmostEqual(float(plan["haft"][2]), 0.0)

    def test_a_body_below_the_hand_moves_the_lance_clear(self):
        # a fallen body filling the ground below the hand, 1 rider height across and 0.4 high
        grid = np.mgrid[-0.5:0.5:21j, -0.3:0.7:21j, -0.9:-0.5:5j].reshape(3, -1).T
        plan = rider_legs.plan_drop((0.0, 0.2, 0.2), (1.0, 0.0, 0.0), 1.7, 0.28, -0.9, grid)
        self.assertTrue(plan["found"])
        points = rider_legs._lance_points(plan["grip"], plan["haft"], 1.7, 0.28)
        self.assertTrue(rider_legs.clear_of(points, grid, rider_legs.DROP_CLEARANCE))
        self.assertGreater(plan["travel"], 0.0)
