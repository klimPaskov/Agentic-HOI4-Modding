"""The Tripo route's fall rule (lib/tripo_fall.py, TRIPO-DEATH-HOVER): the hips of a death come down like a falling body. A synthetic biped, and
vanilla's GER infantry deaths when the game is installed. No Blender."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

import run_pilot
from lib import pdx_deform, tripo_fall as F, tripo_pose as P
from test_tripo_pose_upper import UNITS, Biped, local


def lifted(up: float, first: int, last: int, drop: int):
    """The whole body `up` high from frame `first` to `last`, then down to the ground over `drop` frames."""

    def pose(frame: int):
        if frame < first:
            height = 0.0
        elif frame <= last:
            height = up
        else:
            height = up * max(0.0, 1.0 - (frame - last) / drop)
        base = local("Hips")
        return {"Hips": ((base[0], base[1] + height, base[2]), (0.0, 0.0, 0.0, 1.0))}

    return pose


class FallTimes(unittest.TestCase):
    def test_a_free_fall_has_a_ratio_of_one(self) -> None:
        peak = 0.18
        frames = int(round(np.sqrt(2 * peak / F.FALL_G)))
        self.assertAlmostEqual(F.fall_ratio(0, frames - 1, peak), 1.0, delta=0.1)

    def test_the_limit_is_a_quarter_over_vanillas_worst(self) -> None:
        self.assertAlmostEqual(F.HOVER_RATIO_LIMIT, round(1.25 * F.VANILLA_FALL_RATIO, 2))

    def test_spans_are_the_runs_over_the_free_hover(self) -> None:
        track = np.array([0, 0.05, 0.1, 0.02, 0, 0.04, 0.04])
        self.assertEqual(F.hover_spans(track), [(1, 2, 0.1), (5, 6, 0.04)])


class SyntheticFall(Biped):
    def death(self, up=0.15, first=10, last=39, drop=6, frames=60) -> Path:
        return self.clip("death", frames, lifted(up, first, last, drop))

    def test_a_body_held_up_for_a_long_time_fails(self) -> None:
        found, numbers = P.pose_findings(self.mesh, {"unit_death": self.load(self.death())})
        self.assertIn("TRIPO-DEATH-HOVER", [item["rule"] for item in found], numbers)
        self.assertGreater(numbers["unit_death"]["fall_ratio"], F.HOVER_RATIO_LIMIT)

    def test_a_body_that_falls_as_fast_as_gravity_passes(self) -> None:
        frames = int(round(np.sqrt(2 * 0.15 / F.FALL_G)))
        path = self.death(first=10, last=10, drop=frames, frames=60)
        found, numbers = P.pose_findings(self.mesh, {"unit_death": self.load(path)})
        self.assertNotIn("TRIPO-DEATH-HOVER", [item["rule"] for item in found], numbers)

    def test_a_stumble_of_a_few_frames_passes(self) -> None:
        found, _numbers = P.pose_findings(self.mesh, {"unit_death": self.load(self.death(first=10, last=12, drop=1))})
        self.assertNotIn("TRIPO-DEATH-HOVER", [item["rule"] for item in found])

    def test_the_settle_brings_the_hips_down_in_a_fall_and_never_through_the_ground(self) -> None:
        path = self.death()
        out = self.folder / "fallen.anim"
        result = F.settle_death_fall(self.mesh_path, path, out)
        self.assertTrue(result.changed, result)
        self.assertLess(result.ratio_after, F.HOVER_RATIO_LIMIT)
        self.assertGreater(result.ratio_before, F.HOVER_RATIO_LIMIT)
        after = self.load(out)
        found, _numbers = P.pose_findings(self.mesh, {"unit_death": after})
        self.assertNotIn("TRIPO-DEATH-HOVER", [item["rule"] for item in found])
        matrices = pdx_deform.skinning_matrices(self.mesh, after)
        ground = float(self.mesh.positions[:, 1].min())
        lowest = min(float(pdx_deform.skin(self.mesh, matrices[i])[:, 1].min()) for i in range(after.frames))
        self.assertGreaterEqual(lowest, ground - 0.002 * self.mesh.height)

    def test_only_the_pelvis_translation_and_the_legs_change(self) -> None:
        path = self.death()
        out = self.folder / "fallen.anim"
        F.settle_death_fall(self.mesh_path, path, out)
        before, after = self.load(path), self.load(out)
        for joint in before.channels:
            if joint != "Hips":
                self.assertTrue(np.allclose(before.channels[joint]["t"], after.channels[joint]["t"], atol=1e-6), joint)
            if joint not in ("LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot"):
                self.assertTrue(np.allclose(before.channels[joint]["q"], after.channels[joint]["q"], atol=1e-6), joint)
        self.assertTrue(np.allclose(before.channels["Hips"]["t"][:10], after.channels["Hips"]["t"][:10], atol=1e-6))

    def test_a_death_that_falls_like_a_fall_is_left_as_it_was(self) -> None:
        frames = int(round(np.sqrt(2 * 0.15 / F.FALL_G)))
        path = self.death(first=10, last=10, drop=frames)
        out = self.folder / "same.anim"
        result = F.settle_death_fall(self.mesh_path, path, out)
        self.assertFalse(result.changed)
        self.assertEqual(path.read_bytes(), out.read_bytes())

    def test_the_run_pilot_grounding_runs_the_fall_settle(self) -> None:
        path = self.death()
        record = run_pilot.ground_exported_clip(self.mesh_path, path, "death", {})
        self.assertTrue(record["fall"]["changed"], record)
        found, _numbers = P.pose_findings(self.mesh, {"unit_death": self.load(path)})
        self.assertNotIn("TRIPO-DEATH-HOVER", [item["rule"] for item in found])


class SolveLeg(unittest.TestCase):
    def test_a_foot_held_in_place_while_the_hip_comes_down_keeps_its_bones_and_its_target(self) -> None:
        hip, knee, ankle = np.array([0.0, 0.5, 0.0]), np.array([0.0, 0.28, 0.08]), np.array([0.0, 0.06, 0.0])
        shift = np.array([0.0, -0.15, 0.0])
        eye = np.eye(3)
        thigh, shank, foot = F._solve_leg(hip, knee, ankle, shift, 0.0, eye, eye, eye)
        new_knee = hip + shift + thigh @ (knee - hip)
        new_ankle = new_knee + shank @ thigh.T @ (thigh @ (ankle - knee))
        self.assertAlmostEqual(float(np.linalg.norm(new_knee - (hip + shift))), float(np.linalg.norm(knee - hip)), places=6)
        np.testing.assert_allclose(new_ankle, ankle, atol=1e-6)
        self.assertGreater(new_knee[2], knee[2], "the knee folds out on the side it was on")
        np.testing.assert_allclose(foot, eye)


@unittest.skipUnless((UNITS / "GER_infantry.mesh").is_file(), "the game is not installed here")
class VanillaCalibration(unittest.TestCase):
    def test_vanillas_deaths_fall_within_the_vanilla_ratio_and_pass(self) -> None:
        mesh = pdx_deform.load_mesh(UNITS / "GER_infantry.mesh")
        worst = 0.0
        for clip in ("death_mg", "death_rifle"):
            anim = pdx_deform.load_anim(UNITS / f"GER_infantry_{clip}.anim")
            track = F.hover_track(mesh, anim)
            lying = P._lying_frame(mesh, anim, P.pdx_motion.find_legs(mesh).pelvis)
            self.assertEqual(F.holds(track, lying), [])
            worst = max(worst, *[F.fall_ratio(*span) for span in F.hover_spans(track) if span[0] < lying])
        self.assertAlmostEqual(worst, F.VANILLA_FALL_RATIO, delta=0.1)


if __name__ == "__main__":
    unittest.main()
