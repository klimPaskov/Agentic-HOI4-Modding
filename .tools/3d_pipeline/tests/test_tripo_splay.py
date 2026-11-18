"""The Tripo route's split thighs in a death (lib/tripo_splay.py): the measure, TRIPO-DEATH-SPLAY and the knee swing that eases it, on the
synthetic biped of test_tripo_pose_upper, and the calibration on vanilla's GER infantry deaths when the game is installed. No Blender."""

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
import tripo_checks as TC
from lib import pdx_deform, tripo_pose as P, tripo_splay as S
from test_tripo_pose_upper import NAMES, UNITS, Biped, lying, local, turn


def lying_spread(degrees: float):
    """`lying` (onto the back by frame 40, to frame 70) with the legs spread `degrees` apart along the ground over frames 40 to 50."""

    base = lying()

    def pose(frame: int):
        share = min(max((frame - 40) / 10.0, 0.0), 1.0)
        moved = base(frame)
        moved["LeftUpLeg"] = (local("LeftUpLeg"), turn("z", -degrees / 2.0 * share))
        moved["RightUpLeg"] = (local("RightUpLeg"), turn("z", degrees / 2.0 * share))
        return moved

    return pose


def kneel(degrees: float):
    """The left thigh swung out sideways `degrees` and the shin hanging back down from the knee, ramped in over frames 0 to 20 and held to
    frame 40, the right leg straight: the thighs end `degrees` apart with the left foot under the knee."""

    def pose(frame: int):
        share = min(frame / 20.0, 1.0)
        return {"LeftUpLeg": (local("LeftUpLeg"), turn("z", -degrees * share)), "LeftLeg": (local("LeftLeg"), turn("z", degrees * share))}

    return pose


def world(mesh, anim):
    return pdx_deform.skinning_matrices(mesh, anim) @ np.linalg.inv(mesh.inverse_bind)[None]


class Splay(Biped):
    def test_the_split_is_the_angle_between_the_thighs(self) -> None:
        split = S.thigh_split(self.mesh, self.load(self.clip("death", 41, kneel(100.0))))
        self.assertAlmostEqual(float(split[0]), 0.0, delta=0.5)
        self.assertAlmostEqual(float(split[-1]), 100.0, delta=0.5)

    def test_a_death_split_past_the_limit_fails_and_other_roles_are_not_judged(self) -> None:
        anim = self.load(self.clip("death", 41, kneel(100.0)))
        found, numbers = S.splay_findings(self.mesh, {"unit_death": anim, "unit_attack": anim})
        self.assertEqual([item["rule"] for item in found], ["TRIPO-DEATH-SPLAY"], numbers)
        self.assertEqual(found[0]["subject"], "unit_death")
        self.assertNotIn("unit_attack", numbers)
        found, numbers = S.splay_findings(self.mesh, {"unit_death": self.load(self.clip("death", 41, kneel(40.0)))})
        self.assertEqual(found, [], numbers)

    def test_the_checks_run_it_on_a_humanoid(self) -> None:
        numbers: dict = {}
        found = TC.body_findings(self.mesh, {"unit_death": self.load(self.clip("death", 41, kneel(100.0)))}, numbers)
        self.assertIn("TRIPO-DEATH-SPLAY", [item["rule"] for item in found])
        self.assertIn("death_splay", numbers)

    def test_the_swing_closes_the_thighs_and_keeps_the_feet_where_they_stand(self) -> None:
        path = self.clip("death", 41, kneel(100.0))
        out = self.folder / "eased.anim"
        with mock.patch.object(S, "CLOSE_PASSES", 0):  # the swing alone: the closing after it moves the feet
            result = S.close_death_legs(self.mesh_path, path, out)
        self.assertTrue(result.changed, result)
        before, after = self.load(path), self.load(out)
        split = S.thigh_split(self.mesh, after)
        # the knee swings round the line from the hip to the planted foot, so a thigh swung out this far closes to about 45 degrees at most
        self.assertLessEqual(float(split[-1]), S.SPLIT_LIMIT, result)
        self.assertLess(result.worst_after, result.worst_before - 30.0, result)
        a, b = world(self.mesh, before), world(self.mesh, after)
        for name in ("LeftFoot", "LeftToeBase", "RightFoot", "RightToeBase", "Hips", "Spine"):
            np.testing.assert_allclose(b[:, NAMES.index(name)], a[:, NAMES.index(name)], atol=1e-4, err_msg=name)
        self.assertGreater(float(np.abs(b[-1, NAMES.index("LeftLeg"), :3, 3] - a[-1, NAMES.index("LeftLeg"), :3, 3]).max()), 0.05, "the knee moves")
        for joint in before.channels:
            if joint not in ("LeftUpLeg", "RightUpLeg", "LeftFoot", "RightFoot"):
                np.testing.assert_allclose(after.channels[joint]["q"], before.channels[joint]["q"], atol=1e-6, err_msg=joint)
            np.testing.assert_allclose(after.channels[joint]["t"], before.channels[joint]["t"], atol=1e-6)

    def test_the_swing_is_ramped_in_no_faster_than_the_settle_rule(self) -> None:
        path = self.clip("death", 41, kneel(100.0))
        result = S.close_death_legs(self.mesh_path, path, self.folder / "eased.anim")
        self.assertTrue(result.changed, result)
        self.assertLessEqual(result.fastest_step_degrees, 1.5 * S.tripo_trim.SETTLE_MAX_RATE, result)

    def test_a_death_under_the_limit_is_left_as_it_was(self) -> None:
        path = self.clip("death", 41, kneel(40.0))
        out = self.folder / "eased.anim"
        result = S.close_death_legs(self.mesh_path, path, out)
        self.assertFalse(result.changed)
        self.assertEqual(path.read_bytes(), out.read_bytes())

    def test_no_share_is_taken_when_every_one_makes_the_frames_worse(self) -> None:
        path = self.clip("death", 41, kneel(100.0))
        out = self.folder / "eased.anim"
        with mock.patch.object(S, "_frame_within", side_effect=lambda frames, before: np.zeros(len(frames), bool)):
            result = S.close_death_legs(self.mesh_path, path, out)
        self.assertFalse(result.changed, result)
        self.assertEqual(path.read_bytes(), out.read_bytes())

    def test_the_run_pilot_grounding_swings_the_knees_of_a_death_first(self) -> None:
        path = self.clip("death", 41, kneel(100.0))
        record = run_pilot.ground_exported_clip(self.mesh_path, path, "death", {})
        self.assertTrue(record["splay"]["changed"], record)
        self.assertEqual(list(record)[0], "splay")
        self.assertLess(float(S.thigh_split(self.mesh, self.load(path)).max()), record["splay"]["worst_before"] - 30.0)

    def test_a_lying_body_with_its_legs_spread_has_them_closed_along_the_ground(self) -> None:
        path = self.clip("death", 70, lying_spread(100.0))
        out = self.folder / "closed.anim"
        before = self.load(path)
        self.assertGreater(float(S.thigh_split(self.mesh, before).max()), 95.0)
        result = S.close_death_legs(self.mesh_path, path, out)
        self.assertTrue(result.changed, result)
        self.assertTrue(result.closing, result)
        after = self.load(out)
        self.assertLessEqual(float(S.thigh_split(self.mesh, after).max()), S.SPLIT_LIMIT, result)
        a, b = world(self.mesh, before), world(self.mesh, after)
        for name in ("LeftFoot", "RightFoot", "LeftLeg", "RightLeg"):
            # the legs slide together along the ground: every joint below the hip keeps its height
            np.testing.assert_allclose(b[:, NAMES.index(name), 1, 3], a[:, NAMES.index(name), 1, 3], atol=0.01, err_msg=name)
        self.assertLess(float(np.linalg.norm(b[-1, NAMES.index("LeftFoot"), :3, 3] - b[-1, NAMES.index("RightFoot"), :3, 3])),
                        float(np.linalg.norm(a[-1, NAMES.index("LeftFoot"), :3, 3] - a[-1, NAMES.index("RightFoot"), :3, 3])) - 0.2)
        gaps = S.leg_gaps(self.mesh, after, S._legs(self.mesh))
        floor = S.LEG_CLEARANCE * S.leg_radii(self.mesh, S._legs(self.mesh)).sum(axis=0)
        self.assertTrue((gaps >= floor[None] - 1e-6).all(), gaps.min(axis=0))
        for joint in before.channels:
            if joint not in ("LeftUpLeg", "RightUpLeg", "LeftFoot", "RightFoot"):
                np.testing.assert_allclose(after.channels[joint]["q"], before.channels[joint]["q"], atol=1e-6, err_msg=joint)

    def test_the_closing_never_brings_the_legs_through_each_other(self) -> None:
        path = self.clip("death", 70, lying_spread(100.0))
        out = self.folder / "closed.anim"
        with mock.patch.object(S, "LEG_CLEARANCE", 1e3):  # no closing keeps legs this far apart
            result = S.close_death_legs(self.mesh_path, path, out)
        self.assertFalse(result.closing, result)

    def test_a_body_bound_with_its_thighs_apart_is_judged_against_its_own_split(self) -> None:
        self.assertEqual(S.rest_split(self.mesh), 0.0)
        self.assertEqual(S.split_limit(self.mesh), S.SPLIT_LIMIT)  # a narrow body keeps vanilla's limit
        self.assertEqual(S.split_target(self.mesh), S.SPLIT_TARGET)
        with mock.patch.object(S, "rest_split", return_value=33.0):  # the round 4 ogre's rest pose
            self.assertAlmostEqual(S.split_limit(self.mesh), round(33.0 + S.OPENING_LIMIT, 1))
            self.assertAlmostEqual(S.split_target(self.mesh), round(33.0 + S.VANILLA_DEATH_OPENING, 1))
            anim = self.load(self.clip("death", 41, kneel(55.0)))
            found, numbers = S.splay_findings(self.mesh, {"unit_death": anim})
            self.assertEqual(found, [], numbers)
            self.assertEqual(numbers["unit_death"]["limit"], 57.8)
        found, _numbers = S.splay_findings(self.mesh, {"unit_death": self.load(self.clip("death", 41, kneel(55.0)))})
        self.assertEqual([item["rule"] for item in found], ["TRIPO-DEATH-SPLAY"])

    def test_the_limit_is_a_quarter_over_vanillas_worst_and_the_target_is_vanillas_worst(self) -> None:
        self.assertAlmostEqual(S.VANILLA_DEATH_OPENING, round(S.VANILLA_DEATH_SPLIT - S.VANILLA_REST_SPLIT, 1))
        self.assertAlmostEqual(S.OPENING_LIMIT, round(1.25 * S.VANILLA_DEATH_OPENING, 1))
        self.assertAlmostEqual(S.SPLIT_LIMIT, round(1.25 * S.VANILLA_DEATH_SPLIT, 1))
        self.assertEqual(S.SPLIT_TARGET, S.VANILLA_DEATH_SPLIT)


class UpperSettleStretch(Biped):
    def test_the_upper_settle_takes_no_turn_that_makes_the_clip_worse(self) -> None:
        path = self.clip("death", 70, lying(sit=40.0, arms=30.0))
        out = self.folder / "settled.anim"
        with mock.patch.object(P, "_tail_deformation", side_effect=lambda mesh, anim, first, edges, rest: {"stretched": 0, "squashed": 0, "worst": 0.0}):
            # every trial reads like the clip before: the guard lets the settle through
            self.assertTrue(P.settle_death_upper(self.mesh_path, path, out).changed)
        calls = {"n": 0}

        def worse_after_the_first(mesh, anim, first, edges, rest):
            calls["n"] += 1
            return {"stretched": 0 if calls["n"] == 1 else 999, "squashed": 0, "worst": 0.0}

        with mock.patch.object(P, "_tail_deformation", side_effect=worse_after_the_first):
            result = P.settle_death_upper(self.mesh_path, path, out)
        self.assertFalse(result.changed, result)
        self.assertEqual(path.read_bytes(), out.read_bytes())


@unittest.skipUnless((UNITS / "GER_infantry.mesh").is_file(), "the game is not installed here")
class VanillaCalibration(unittest.TestCase):
    def test_vanillas_deaths_split_the_thighs_at_most_the_vanilla_worst(self) -> None:
        worst = 0.0
        for mesh_name in ("GER_infantry", "GER_infantry_alt_0", "ENG_infantry", "GER_infantry_snow"):
            mesh = pdx_deform.load_mesh(UNITS / f"{mesh_name}.mesh")
            for clip in ("death_mg", "death_rifle"):
                worst = max(worst, float(S.thigh_split(mesh, pdx_deform.load_anim(UNITS / f"GER_infantry_{clip}.anim")).max()))
        self.assertAlmostEqual(worst, S.VANILLA_DEATH_SPLIT, delta=0.1)

    def test_vanillas_rest_pose_holds_the_thighs_at_the_vanilla_rest_split_and_its_limit_stays(self) -> None:
        for mesh_name in ("GER_infantry", "GER_infantry_alt_0", "ENG_infantry", "GER_infantry_snow"):
            mesh = pdx_deform.load_mesh(UNITS / f"{mesh_name}.mesh")
            self.assertAlmostEqual(S.rest_split(mesh), S.VANILLA_REST_SPLIT, delta=0.1, msg=mesh_name)
            self.assertEqual(S.split_limit(mesh), S.SPLIT_LIMIT, mesh_name)


if __name__ == "__main__":
    unittest.main()
