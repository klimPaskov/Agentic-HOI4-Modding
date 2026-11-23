"""The mount a seated rider is fitted to, as the mount's clip moves it (lib/rider_fit.clip_profiles, run_pilot.seat_profile).

A brace that lifts the shoulders widens the barrel under the seat and raises the withers toward the rein hand: legs solved against the rest
barrel sank into the zinnish lancer's horse. The synthetic mount below has a body, a shoulder block beside the seat and a withers block ahead
of it. Its clip lifts the whole body (which the rider on the node rides along with), pushes the shoulder out and raises the withers.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import run_pilot
from lib import rider_fit
from lib.pdx_deform import Animation, SkinnedMesh

BONES = ["Body", "Saddle_Node", "Shoulder", "Withers"]


def _block(x, y, z, steps=6):
    grid = np.mgrid[x[0]:x[1]:complex(steps), y[0]:y[1]:complex(steps), z[0]:z[1]:complex(steps)]
    return grid.reshape(3, -1).T


def _mount() -> SkinnedMesh:
    parts = [
        (_block((-0.15, 0.15), (0.4, 1.0), (-0.8, 0.8), 9), 0),  # the body: the node sits on its top at y 1
        (_block((-0.05, 0.05), (1.3, 1.5), (-0.9, -0.7)), 0),  # the head, highest at rest: the mount faces -Z
        (_block((0.1, 0.15), (0.5, 0.7), (-0.1, 0.1)), 2),  # a shoulder block beside the seat
        (_block((0.0, 0.05), (1.0, 1.1), (-0.22, -0.18)), 3),  # the withers, 0.2 ahead of the seat
    ]
    positions = np.concatenate([points for points, _ in parts])
    joints = np.full((len(positions), 4), -1)
    joints[:, 0] = np.concatenate([np.full(len(points), bone) for points, bone in parts])
    weights = np.zeros((len(positions), 4))
    weights[:, 0] = 1.0
    world = np.tile(np.eye(4), (len(BONES), 1, 1))
    world[1, :3, 3] = (0.0, 1.0, 0.0)
    return SkinnedMesh(positions=positions, triangles=np.zeros((0, 3), dtype=int), joints=joints, weights=weights,
                       bones=list(BONES), parents=[-1, 0, 0, 0], inverse_bind=np.linalg.inv(world))


def _clip() -> Animation:
    identity = np.array([[0.0, 0.0, 0.0, 1.0]] * 2)
    moves = {"Body": (0.0, 0.3, 0.0), "Saddle_Node": None, "Shoulder": (0.08, 0.0, 0.0), "Withers": (0.0, 0.05, 0.0)}
    channels = {}
    for name, move in moves.items():
        t = np.zeros((2, 3))
        if name == "Saddle_Node":
            t[:] = (0.0, 1.0, 0.0)
        else:
            t[1] = move
        channels[name] = {"t": t, "q": identity.copy(), "s": np.ones(2)}
    return Animation(fps=15.0, frames=2, channels=channels)


def _width(rows, depth):
    return next(row["half_width"] for row in rows if abs(row["depth"] - depth) < 1e-9)


def _top(rows, ahead, out):
    return next(row["top"] for row in rows if abs(row["ahead"] - ahead) < 1e-9 and abs(row["out"] - out) < 1e-9)


class ClipProfiles(unittest.TestCase):
    def setUp(self) -> None:
        self.mount = _mount()
        self.profiles = rider_fit.clip_profiles(self.mount, {"defend": _clip()}, rider_height=1.0)

    def test_the_head_gives_the_facing(self) -> None:
        self.assertEqual(rider_fit.facing(self.mount), -1.0)

    def test_the_rest_profile_is_the_barrel_profile(self) -> None:
        self.assertEqual(self.profiles["rest"]["barrel"], rider_fit.barrel_profile(self.mount, 1.0))
        self.assertAlmostEqual(_width(self.profiles["rest"]["barrel"], 0.4), 0.15, places=3)
        self.assertAlmostEqual(_top(self.profiles["rest"]["top"], 0.2, 0.0), 0.1, places=3)

    def test_the_clip_widens_the_barrel_and_raises_the_top_in_the_nodes_frame(self) -> None:
        defend = self.profiles["defend"]
        # the shoulder 0.08 further out; the whole body's lift of 0.3 carries the node too, so the seat sees none of it
        self.assertAlmostEqual(_width(defend["barrel"], 0.4), 0.23, places=3)
        self.assertAlmostEqual(_top(defend["top"], 0.2, 0.0), 0.15, places=3)
        # nothing narrows: each row is the widest of the rest pose and every frame
        for rest, posed in zip(self.profiles["rest"]["barrel"], defend["barrel"]):
            self.assertGreaterEqual(posed["half_width"], rest["half_width"])


class SeatProfile(unittest.TestCase):
    def test_a_role_takes_its_mount_clip_else_the_rest(self) -> None:
        profiles = {"rest": {"barrel": [1], "top": [1]}, "defend": {"barrel": [2], "top": [2]}}
        self.assertEqual(run_pilot.seat_profile(profiles, "defend"), profiles["defend"])
        self.assertEqual(run_pilot.seat_profile(profiles, "attack"), profiles["rest"])

    def test_no_measured_mount_gives_nothing(self) -> None:
        self.assertEqual(run_pilot.seat_profile(None, "idle"), {"barrel": [], "top": []})


if __name__ == "__main__":
    unittest.main()
