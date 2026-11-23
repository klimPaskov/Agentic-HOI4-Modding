"""tripo/proportion_check.py: a quadruped model's neck and legs against its reference picture, before the rig."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "adapter"))
sys.path.insert(0, str(PIPELINE / "tripo"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import proportion_check as pc
from test_quadruped_ears import _box


def _dragon(neck_top: float, ruff: bool = False):
    """A blocky winged dragon facing -Y with a thin neck column from the torso's top (1.6) to `neck_top`, under a head 0.35 tall.
    With `ruff` the torso stops at 1.3 and the neck's lower part rises from the breast through a wide, flat ruff of shoulder spikes,
    as on the remade Tripo dragon: seen from the front it is no column, seen from the side it is as deep as the neck above."""

    top = 1.3 if ruff else 1.6
    parts = [((x - 0.08, y - 0.08, 0.0), (x + 0.08, y + 0.08, 1.0), 8) for x in (-0.22, 0.22) for y in (0.0, 1.6)]
    parts.append(((-0.35, -0.2, 1.0), (0.35, 1.8, top), 8))
    parts.append(((-0.06, -0.3, top - 0.05), (0.06, -0.1, neck_top), (2, 3, 24 if ruff else 8)))
    if ruff:
        parts.append(((-0.4, -0.28, 1.3), (0.4, -0.12, 1.6), (10, 2, 12)))
    parts.append(((-0.2, -0.85, neck_top), (0.2, -0.1, neck_top + 0.35), 8))
    parts.append(((-0.04, 2.25, 0.0), (0.04, 3.6, 0.05), (2, 16, 1)))
    parts.append(((-0.04, 1.8, 0.3), (0.04, 2.25, 1.2), (2, 4, 8)))
    parts.append(((-0.04, 2.2, 0.05), (0.04, 2.25, 0.3), (2, 1, 4)))
    parts.append(((0.25, 0.4, 1.3), (1.6, 0.42, 2.2), (16, 1, 10)))
    parts.append(((-1.6, 0.4, 1.3), (-0.25, 0.42, 2.2), (16, 1, 10)))
    points, triangles = [], []
    for lo, hi, steps in parts:
        p, t = _box(lo, hi, steps)
        triangles.append(t + sum(len(x) for x in points))
        points.append(p)
    return np.vstack(points), np.vstack(triangles)


class Proportions(unittest.TestCase):
    def test_the_neck_and_legs_are_measured_as_shares_of_the_height(self) -> None:
        found = pc.model_proportions(*_dragon(2.0))
        height = 2.35
        self.assertAlmostEqual(found["neck"], 0.4 / height, delta=0.06)
        self.assertAlmostEqual(found["legs"], 1.0 / height, delta=0.06)

    def test_a_neck_much_shorter_than_drawn_fails_and_one_as_drawn_passes(self) -> None:
        short = pc.model_proportions(*_dragon(2.0))
        drawn = {"neck": short["neck"], "legs": short["legs"]}
        self.assertEqual(pc.proportion_verdict(short, drawn)["verdict"], "pass")
        long_picture = {"neck": 2.0 * short["neck"], "legs": short["legs"]}
        verdict = pc.proportion_verdict(short, long_picture)
        self.assertEqual(verdict["verdict"], "fail")
        self.assertEqual([item["part"] for item in verdict["findings"]], ["neck"])

    def test_a_neck_rising_from_the_breast_is_measured_from_the_shoulders(self) -> None:
        found = pc.model_proportions(*_dragon(2.0, ruff=True))
        self.assertAlmostEqual(found["neck"], 0.7 / 2.35, delta=0.05, msg="from where it leaves the torso (1.3), not from the ruff's top")
        self.assertEqual(pc.proportion_verdict(found, {"neck": 0.3, "legs": None})["verdict"], "pass")

    def test_the_rig_neck_bones_start_where_the_neck_leaves_the_chest(self) -> None:
        import quadruped_layout as ql
        from lib import mount_size

        for ruff, base in ((True, 1.3), (False, 1.6)):
            points, found = mount_size.winged_body(*_dragon(2.0, ruff=ruff))
            body = points[found["body"]]
            landmarks = ql.detect_landmarks(body)
            neck = ql.detect_neck(body, landmarks)
            self.assertAlmostEqual(neck["base"][2], base, delta=0.08, msg=f"ruff={ruff}: the lower neck rides on the neck bones, not the Chest")
            landmarks["neck"] = neck
            bones = {bone.name: bone for bone in ql.build_layout(landmarks).bones}
            self.assertAlmostEqual(bones["Neck_01"].head[2], neck["base"][2], delta=1e-6)
            self.assertLess(neck["base"][2], neck["middle"][2])
            self.assertLess(neck["middle"][2], neck["head"][2])

    def test_a_model_without_a_neck_column_fails_a_picture_with_one(self) -> None:
        self.assertEqual(pc.proportion_verdict({"neck": 0.0, "legs": 0.4}, {"neck": 0.2, "legs": None})["verdict"], "fail")

    def test_shares_read_off_a_picture_are_judged_before_any_model(self) -> None:
        self.assertEqual(pc.main(["--shares", "neck=0.12,legs=0.36", "--neck", "0.22", "--legs", "0.36"]), 1, "a multi-view that lost the neck")
        self.assertEqual(pc.main(["--shares", "neck=0.21,legs=0.35", "--neck", "0.22", "--legs", "0.36"]), 0, "a redraw that kept it")


if __name__ == "__main__":
    unittest.main()
