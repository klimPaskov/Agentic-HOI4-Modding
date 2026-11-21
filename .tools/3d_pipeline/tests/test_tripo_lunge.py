"""The lunge step kept for an attack (tripo/lunge_clip.py), the intake's allowance for it (tripo_intake.refuse_travelling_clips) and the
strike of a lunging grab measured against the ground (lib/tripo_strike.strike_numbers). Synthetic GLBs and joints, no Blender."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))
sys.path.insert(0, str(PIPELINE / "tripo"))

import lunge_clip
import tripo_intake
from lib import glb_root, tripo_strike as S
from test_glb_root import write_glb

FRAMES = 20


def in_place():
    return [[0.0, 1.0 + 0.03 * np.sin(t), 0.0] for t in np.linspace(0.0, 3.0, FRAMES)]


def stepping(distance: float):
    return [[0.0, 1.0 + 0.03 * np.sin(t), distance * min(1.0, 2.0 * s)] for t, s in zip(np.linspace(0.0, 3.0, FRAMES), np.linspace(0.0, 1.0, FRAMES))]


class Step(unittest.TestCase):
    def test_the_step_is_capped_added_to_the_in_place_clip_and_the_rest_kept(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            write_glb(folder / "place.glb", {"lunge forward": in_place(), "idle": in_place()})
            write_glb(folder / "travel.glb", {"lunge forward": stepping(1.2), "idle": stepping(0.4)})
            record = lunge_clip.write_lunge(folder / "place.glb", folder / "travel.glb", "lunge", folder / "out.glb", cap=0.6)
            travel = glb_root.root_travel(folder / "out.glb")
            doc, blob = glb_root._read(folder / "out.glb")
            keys = glb_root._accessor(doc, blob, 1)
        self.assertAlmostEqual(record["step_hip_heights"], 1.2, places=3)
        self.assertAlmostEqual(travel["lunge forward"], 0.6, places=3)
        self.assertLess(travel["idle"], 0.01, "every other clip stays as the in-place export made it")
        np.testing.assert_allclose(keys[:, 1], np.asarray(in_place(), np.float32)[:, 1], atol=1e-6)  # the up and down stays the in-place clip's

    def test_a_short_step_is_kept_whole(self) -> None:
        keys, record = lunge_clip.lunge_step(np.asarray(in_place(), np.float32), np.asarray(stepping(0.3), np.float32), np.array([0.0, 1.0, 0.0]), 0.6)
        self.assertEqual(record["factor"], 1.0)
        self.assertAlmostEqual(float(keys[-1, 2]), 0.3, places=5)

    def test_the_intake_allows_the_named_lunge_up_to_its_cap_only(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "u.glb"
            write_glb(path, {"lunge forward": stepping(0.6), "walk": stepping(0.6)})
            spec = {"tripo": {"roles": {"attack": "lunge", "move": "walk"}, "lunge": {"attack": 0.6}}}
            with self.assertRaises(ValueError) as caught:
                tripo_intake.refuse_travelling_clips(spec, path)
            self.assertIn("walk", str(caught.exception))
            self.assertNotIn("lunge", str(caught.exception))
            spec["tripo"]["roles"].pop("move")
            tripo_intake.refuse_travelling_clips(spec, path)  # the lunge alone passes
            spec["tripo"]["lunge"]["attack"] = 0.3
            with self.assertRaises(ValueError):
                tripo_intake.refuse_travelling_clips(spec, path)  # over its cap it is refused


class RestoreStep(unittest.TestCase):
    def test_the_provider_step_is_read_forward_and_eased_back_before_the_loop(self) -> None:
        from lib import tripo_lunge

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "attack.glb"
            write_glb(path, {"lunge": stepping(0.6)})
            step = tripo_lunge.provider_step(path)
        self.assertAlmostEqual(float(step["forward"][-1]), 0.6, places=4)
        self.assertGreaterEqual(float(step["forward"].min()), -1e-6, "a step toward the rig's facing reads forward")
        frames = tripo_lunge.step_per_frame(step, 40, 40.0)  # the provider clip lasts one second, as the export here
        self.assertEqual(float(frames[0]), 0.0)
        self.assertEqual(float(frames[-1]), 0.0, "the attack ends where it started, so its loop holds")
        self.assertAlmostEqual(float(frames[:int(40 * (1 - tripo_lunge.RETURN_SHARE))].max()), 0.6, places=2)


class GroundStrike(unittest.TestCase):
    def joints(self, step: float, reach: float) -> np.ndarray:
        """(F, 3, 3): Spine02 stepping `step` forward, both hands ahead of it, thrust a further `reach` over frames 8 to 12."""

        frames = 30
        out = np.zeros((frames, 3, 3))
        go = np.clip((np.arange(frames) - 6) / 6.0, 0.0, 1.0)
        thrust = np.clip((np.arange(frames) - 8) / 4.0, 0.0, 1.0)
        out[:, 0, 2] = step * go
        for hand in (1, 2):
            out[:, hand, 2] = out[:, 0, 2] + 0.15 + reach * thrust
            out[:, hand, 1] = 0.7
        return out

    def test_a_lunging_grab_strikes_against_the_ground_and_a_held_reach_does_not(self) -> None:
        bones = ["Spine02", "LeftHand", "RightHand"]
        lunge = self.joints(step=0.3, reach=0.1)
        chest = S.strike_numbers(lunge, bones, 1.0, 30.0)
        ground = S.strike_numbers(lunge, bones, 1.0, 30.0, lunge=True)
        self.assertFalse(chest["strikes"])  # against the chest only the arms' 0.1 counts
        self.assertTrue(ground["strikes"])
        self.assertEqual(ground["against"], "ground")
        held = S.strike_numbers(self.joints(step=0.0, reach=0.05), bones, 1.0, 30.0, lunge=True)
        self.assertFalse(held["strikes"], "a held reach with no step stays under the limits against the ground too")
        self.assertIn("against the ground", S.no_strike_reason(held))


if __name__ == "__main__":
    unittest.main()
