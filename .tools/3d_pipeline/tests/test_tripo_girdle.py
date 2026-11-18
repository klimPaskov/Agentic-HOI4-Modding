"""The shoulder girdle rule (lib/tripo_girdle.py): the upper arm's weight kept to its own bone, TRIPO-SHOULDER-TEAR's region, and the bounded
trade that keeps the rule. No Blender."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))
sys.path.insert(0, str(PIPELINE / "tripo"))

import run_pilot
import test_tripo_shoulder as TS
from lib import pdx_deform, stretch_smooth, tripo_girdle as G, tripo_shoulder as S


class Rule(TS.Unit):
    def test_the_arms_weight_far_from_its_bone_goes_to_the_clavicle(self) -> None:
        names = self.mesh.bones
        arm, clavicle = names.index("LeftArm"), names.index("LeftShoulder")
        dense = stretch_smooth.dense_weights(self.mesh)
        # the back sheet's top rows take the left arm's weight, as Tripo binds the upper back to the arm
        top = self.sheet[self.mesh.positions[self.sheet, 1] > 1.5]
        dense[top] = 0.0
        dense[top, arm] = 1.0
        locked = np.zeros(len(dense), bool)
        new, record = G.confined_dense(self.mesh, dense, locked)
        self.assertGreater(record["left"]["vertices"], 0)
        self.assertTrue(np.allclose(new.sum(axis=1), dense.sum(axis=1)))
        self.assertTrue(np.all(new[top, clavicle] > 0.0))
        # the arm's own skin (its tetrahedron at the joint) keeps its weight
        own = np.nonzero(dense[:, arm] == 1.0)[0]
        own = own[~np.isin(own, top)]
        self.assertTrue(np.allclose(new[own, arm], 1.0))
        locked[top] = True
        kept, _record = G.confined_dense(self.mesh, dense, locked)
        self.assertTrue(np.allclose(kept[top], dense[top]))

    def test_the_girdle_region_adds_the_torso_under_the_arm(self) -> None:
        girdle, shoulders = S.girdle_regions(self.mesh), S.shoulder_regions(self.mesh)
        self.assertTrue(np.all(girdle["left"] >= shoulders["left"]))
        self.assertGreater(S.GIRDLE_LIMIT, S.VANILLA_GIRDLE_WORST)
        self.assertAlmostEqual(S.GIRDLE_LIMIT, 1.25 * S.VANILLA_GIRDLE_WORST, places=4)
        names = self.mesh.bones
        arm = names.index("LeftArm")
        under = S.under_arm_regions(self.mesh)["left"]
        self.assertFalse(under[pdx_deform.dominant_bones(self.mesh) == arm].any(), "the limb itself is not the torso")

    def test_the_check_reports_the_tear(self) -> None:
        anim = pdx_deform.load_anim(self.clip("attack", 4, lambda f: TS.bent(60.0)))
        found, numbers = S.shoulder_findings(self.mesh, {"unit_attack": anim})
        self.assertIn("girdle_share", numbers["unit_attack"])
        self.assertEqual(numbers["unit_attack"]["girdle_share"] > S.GIRDLE_LIMIT, "TRIPO-SHOULDER-TEAR" in [f["rule"] for f in found])


def clip(stretched, squashed, worst, girdle=0.01, swell=0.01):
    return {"stretched": stretched, "squashed": squashed, "worst": worst, "girdle": girdle, "swell": swell}


class Trade(unittest.TestCase):
    def test_a_rule_that_fixes_the_failing_clip_within_the_bound_is_kept(self) -> None:
        before = {"attack": clip(335, 135, 0.046, girdle=0.19), "idle": clip(0, 10, 0.011), "death": clip(222, 128, 0.034), "_edges": 20000}
        after = {"attack": clip(329, 109, 0.049, girdle=0.13), "idle": clip(4, 7, 0.012), "death": clip(239, 107, 0.039)}
        result = G.trade(before, after)
        self.assertTrue(result.accepted, result.reasons)
        self.assertEqual((result.deformed_before, result.deformed_after), (830, 795))

    def test_a_clip_worse_past_the_bound_or_a_failing_clip_left_as_it_is_drops_the_rule(self) -> None:
        before = {"attack": clip(335, 135, 0.046, girdle=0.19), "defend": clip(109, 27, 0.028, girdle=0.17), "_edges": 20000}
        worse = {"attack": clip(300, 100, 0.046, girdle=0.13), "defend": clip(109, 60, 0.028, girdle=0.10)}
        self.assertIn("defend: worst-frame squashed 27 to 60", G.trade(before, worse).reasons)
        unfixed = {"attack": clip(300, 100, 0.046, girdle=0.13), "defend": clip(100, 27, 0.028, girdle=0.18)}
        self.assertFalse(G.trade(before, unfixed).accepted)
        more = {"attack": clip(340, 140, 0.046, girdle=0.13), "defend": clip(109, 27, 0.028, girdle=0.10)}
        self.assertTrue(any("do not fall" in r for r in G.trade(before, more).reasons))


class Pilot(unittest.TestCase):
    def test_a_quadruped_or_the_switch_off_keeps_no_start_and_gets_no_trial(self) -> None:
        import tempfile

        for spec, quadruped in (({"runtime_stem": "u", "tripo": {"girdle_weights": False}}, False), ({"runtime_stem": "u"}, True)):
            with tempfile.TemporaryDirectory() as folder, mock.patch.object(run_pilot, "_smooth_and_fit", return_value={"weight_fit": {}}) as fit,                     mock.patch.object(run_pilot, "tripo_quadruped", return_value=quadruped), mock.patch.object(G, "measures") as measures:
                job = Path(folder)
                out = run_pilot.fit_staged_weights(job, job, spec, ["attack"], [])
                self.assertIsNone(run_pilot.girdle_trial(job, job, spec, ["attack"], []))
                self.assertFalse((job / "validation" / "girdle_trial").exists())
            fit.assert_called_once()
            measures.assert_not_called()
            self.assertEqual(out, {"weight_fit": {}})

    def test_a_humanoid_that_passes_keeps_its_weights_and_the_trial_folder_is_removed(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as folder, mock.patch.object(run_pilot, "_smooth_and_fit", return_value={}),                 mock.patch.object(run_pilot, "tripo_quadruped", return_value=False),                 mock.patch.object(G, "measures", return_value={"u_attack": {"girdle": 0.01, "swell": 0.01}, "_edges": 10}):
            job = Path(folder)
            (job / "u.mesh").write_bytes(b"mesh")
            run_pilot.fit_staged_weights(job, job, {"runtime_stem": "u"}, ["attack"], [])
            self.assertTrue((job / "validation" / "girdle_trial" / "start.mesh").is_file())
            record = run_pilot.girdle_trial(job, job, {"runtime_stem": "u"}, ["attack"], [])
            self.assertEqual(record["failing_before"], [])
            self.assertFalse((job / "validation" / "girdle_trial").exists())


if __name__ == "__main__":
    unittest.main()
