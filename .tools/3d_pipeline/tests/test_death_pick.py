"""The death pick (tripo/death_pick.py): the joint names it matches, the similarity it carries a clip by, the .anim it writes for the route's
settles, and the rule that picks a death. No Blender."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tripo"))

import death_pick as DP
from lib import pdx_deform


def row(clip: str, fails=(), deformed: int = 100) -> dict:
    return {"clip": clip, "fails": list(fails), "deformed_edges": deformed}


class Names(unittest.TestCase):
    def test_the_rig_prefix_and_leading_zeros_do_not_matter(self) -> None:
        self.assertEqual(DP.bone_key("mixamorig:Spine1"), DP.bone_key("Spine01"))
        self.assertEqual(DP.bone_key("mixamorig:Neck"), DP.bone_key("neck"))
        self.assertNotEqual(DP.bone_key("LeftArm"), DP.bone_key("LeftForeArm"))


class Similarity(unittest.TestCase):
    def setUp(self) -> None:
        self.points = np.random.default_rng(3).normal(size=(12, 3))

    def check(self, matrix: np.ndarray) -> None:
        target = self.points @ matrix[:3, :3].T + matrix[:3, 3]
        fit = DP.similarity(self.points, target)
        np.testing.assert_allclose(self.points @ fit[:3, :3].T + fit[:3, 3], target, atol=1e-9)

    def test_a_scaled_turn_is_found(self) -> None:
        angle = np.radians(20.0)
        turn = np.array([[np.cos(angle), 0.0, np.sin(angle)], [0.0, 1.0, 0.0], [-np.sin(angle), 0.0, np.cos(angle)]])
        matrix = np.eye(4)
        matrix[:3, :3] = 7.3 * turn
        matrix[:3, 3] = (0.1, 2.0, -0.4)
        self.check(matrix)

    def test_a_mirrored_forward_axis_is_found(self) -> None:
        # the PDX exporter flips the forward axis: without the mirror the zombie's feet and hands sat 8% of its height off
        matrix = np.diag([7.3, 7.3, -7.3, 1.0])
        self.check(matrix)


class Writer(unittest.TestCase):
    def test_the_written_anim_reads_back_the_same_keys(self) -> None:
        frames, bones = 5, ["Hips", "Spine"]
        rng = np.random.default_rng(1)
        q = rng.normal(size=(2, frames, 4))
        q /= np.linalg.norm(q, axis=-1, keepdims=True)
        channels = {name: {"t": rng.normal(size=(frames, 3)), "q": q[i], "s": np.ones(frames)} for i, name in enumerate(bones)}
        anim = pdx_deform.Animation(30.0, frames, channels)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "clip.anim"
            DP.write_anim(path, anim, bones)
            back = pdx_deform.load_anim(path)
        self.assertEqual(back.frames, frames)
        for name in bones:
            np.testing.assert_allclose(back.channels[name]["q"], channels[name]["q"], atol=1e-6)
            np.testing.assert_allclose(back.channels[name]["t"], channels[name]["t"], atol=1e-5)


class Pick(unittest.TestCase):
    def test_the_passing_candidate_with_the_fewest_deformed_edges_wins(self) -> None:
        verdict = DP.pick([row("a", deformed=300), row("b", ["TRIPO-DEATH-SPLAY"], 50), row("c", deformed=200)])
        self.assertEqual(verdict["pick"], "c")

    def test_without_a_passing_candidate_the_closest_is_named(self) -> None:
        verdict = DP.pick([row("a", ["TRIPO-DEATH-SPLAY", "TRIPO-DEATH-HOVER"], 50), row("b", ["TRIPO-DEATH-SPLAY"], 400)])
        self.assertIsNone(verdict["pick"])
        self.assertEqual(verdict["closest"], "b")
        self.assertIn("TRIPO-DEATH-SPLAY", verdict["why"])


if __name__ == "__main__":
    unittest.main()
