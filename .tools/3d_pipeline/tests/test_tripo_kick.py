"""A leg kicking up from a lying Tripo death (lib/tripo_kick.py): the boot's rise, TRIPO-DEATH-LEG-KICK and the settle that lays the leg across
the kick, on the synthetic biped of test_tripo_pose_upper, and the calibration on vanilla's GER infantry deaths when the game is installed.
No Blender."""

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
from lib import pdx_deform, tripo_kick as K, tripo_trim
from test_tripo_pose_upper import UNITS, Biped, lying, local, turn


def kicked(degrees: float = -20.0, start: int = 50):
    """`lying()` (on the back from frame 40) with the left thigh lifted `degrees` over frames `start` to `start + 6` and laid back by `start + 14`."""

    base = lying()

    def pose(frame: int):
        moved = base(frame)
        up = min(max((frame - start) / 6.0, 0.0), 1.0) - min(max((frame - start - 8) / 6.0, 0.0), 1.0)
        if up > 0:
            moved["LeftUpLeg"] = (local("LeftUpLeg"), turn("x", degrees * up))
        return moved

    return pose


class KickSpan(unittest.TestCase):
    def test_the_span_runs_from_the_low_before_the_peak_to_the_boot_back_down(self) -> None:
        track = np.array([0.30, 0.20, 0.10, 0.10, 0.12, 0.18, 0.25, 0.18, 0.12, 0.11, 0.10, 0.10])
        self.assertEqual(K.kick_span(track, 1, 0.021), (2, 8))

    def test_a_leg_that_only_comes_down_has_no_span(self) -> None:
        self.assertIsNone(K.kick_span(np.array([0.30, 0.20, 0.15, 0.10, 0.10]), 0, 0.021))


class LegKick(Biped):
    def test_a_boot_rising_after_the_hips_are_down_fails(self) -> None:
        anim = self.load(self.clip("death", 70, kicked()))
        numbers = K.kick_numbers(self.mesh, anim)
        self.assertEqual(numbers["onset"], 40, numbers)
        self.assertGreater(numbers["legs"]["left"]["rise"], K.BOOT_RISE_LIMIT, numbers)
        self.assertLessEqual(numbers["legs"]["right"]["rise"], K.BOOT_RISE_LIMIT, numbers)
        found, _numbers = K.kick_findings(self.mesh, {"unit_death": anim, "unit_attack": anim})
        self.assertEqual([(item["rule"], item["subject"], item["leg"]) for item in found], [("TRIPO-DEATH-LEG-KICK", "unit_death", "left")])

    def test_the_hips_are_down_where_the_ground_pass_will_leave_them(self) -> None:
        # Before the ground pass a body that sinks into the floor while it lands reads its raw hips down early; the lift that answers the sink
        # holds them up. The onset is judged on the lifted body, as the check reads it after the ground pass (the D-94 zombie, 2026-11-21).
        anim = self.load(self.clip("death", 70, lying()))
        legs = K._legs(self.mesh)
        self.assertEqual(K.lifted_lying_frame(self.mesh, anim, legs.pelvis), 40)
        lift = np.where(np.arange(70) < 55, 0.1 * self.mesh.height, 0.0)
        with mock.patch.object(K, "_lifts", return_value=lift):
            self.assertEqual(K.lifted_lying_frame(self.mesh, anim, legs.pelvis), 55)
            self.assertEqual(K.kick_numbers(self.mesh, anim)["onset"], 55)

    def test_a_body_that_lies_still_passes(self) -> None:
        found, numbers = K.kick_findings(self.mesh, {"unit_death": self.load(self.clip("death", 70, lying()))})
        self.assertEqual(found, [], numbers)

    def test_the_checks_run_it_on_a_humanoid(self) -> None:
        numbers: dict = {}
        found = TC.body_findings(self.mesh, {"unit_death": self.load(self.clip("death", 70, kicked()))}, numbers)
        self.assertIn("TRIPO-DEATH-LEG-KICK", [item["rule"] for item in found])
        self.assertIn("death_kick", numbers)

    def test_the_settle_lays_the_leg_across_the_kick_and_leaves_the_rest(self) -> None:
        path = self.clip("death", 70, kicked())
        out = self.folder / "settled.anim"
        result = K.settle_death_kick(self.mesh_path, path, out)
        self.assertTrue(result.changed, result)
        self.assertLessEqual(result.after["legs"]["left"]["rise"], K.BOOT_RISE_TARGET, result)
        first, last = result.spans["left"][0]
        before, after = self.load(path), self.load(out)
        for joint in before.channels:
            if joint not in ("LeftUpLeg", "LeftLeg", "LeftFoot"):
                np.testing.assert_allclose(after.channels[joint]["q"], before.channels[joint]["q"], atol=1e-6, err_msg=joint)
        for joint in ("LeftUpLeg", "LeftLeg", "LeftFoot"):
            outside = [f for f in range(before.frames) if f <= first or f >= last]
            np.testing.assert_allclose(after.channels[joint]["q"][outside], before.channels[joint]["q"][outside], atol=1e-6, err_msg=joint)
        steps = [K.tripo_ease.step_degrees(after.channels[j]["q"][f - 1], after.channels[j]["q"][f]) for j in ("LeftUpLeg", "LeftLeg", "LeftFoot")
                 for f in range(first + 1, last + 1)]
        self.assertLessEqual(max(steps), tripo_trim.SETTLE_MAX_RATE + 1e-6)

    def test_a_still_body_is_left_as_it_was(self) -> None:
        path = self.clip("death", 70, lying())
        out = self.folder / "settled.anim"
        result = K.settle_death_kick(self.mesh_path, path, out)
        self.assertFalse(result.changed)
        self.assertEqual(path.read_bytes(), out.read_bytes())

    def test_no_span_is_taken_when_it_makes_the_clip_worse(self) -> None:
        path = self.clip("death", 70, kicked())
        out = self.folder / "settled.anim"
        with mock.patch.object(K.stretch_smooth, "worse", return_value=True):
            result = K.settle_death_kick(self.mesh_path, path, out)
        self.assertFalse(result.changed, result)
        self.assertEqual(path.read_bytes(), out.read_bytes())

    def test_a_leg_goes_a_share_of_the_way_when_the_whole_lay_across_breaks_a_guard(self) -> None:
        path = self.clip("death", 70, kicked())
        whole = K.settle_death_kick(self.mesh_path, path, self.folder / "whole.anim")
        before = self.load(path)
        laid = self.load(self.folder / "whole.anim")
        legs = K._legs(self.mesh)
        leg = next(leg for side, leg in enumerate(legs.legs) if K._leg_key(self.mesh, leg, side) == "left")
        half = K.part_way(self.mesh, before, laid, leg, 0.5)
        np.testing.assert_allclose(K.part_way(self.mesh, before, laid, leg, 0.0).channels["LeftLeg"]["q"], before.channels["LeftLeg"]["q"], atol=1e-9)
        np.testing.assert_allclose(np.abs((K.part_way(self.mesh, before, laid, leg, 1.0).channels["LeftLeg"]["q"] * laid.channels["LeftLeg"]["q"]).sum(axis=1)), 1.0, atol=1e-9)
        np.testing.assert_allclose(half.channels["RightLeg"]["q"], before.channels["RightLeg"]["q"])
        rise = K.kick_numbers(self.mesh, half, (), legs)["legs"]["left"]["rise"]
        self.assertLess(rise, whole.before["legs"]["left"]["rise"])
        self.assertGreater(rise, whole.after["legs"]["left"]["rise"])
        # the guards refuse the whole lay across and pass a share of it: the settle takes the share
        calls = {"count": 0}

        def worse(_reference, _after):
            calls["count"] += 1
            return calls["count"] == 1

        out = self.folder / "part.anim"
        with mock.patch.object(K.stretch_smooth, "worse", side_effect=worse):
            result = K.settle_death_kick(self.mesh_path, path, out)
        self.assertTrue(result.changed, result)
        self.assertLess(result.after["legs"]["left"]["rise"], result.before["legs"]["left"]["rise"])

    def test_the_run_pilot_grounding_settles_the_kick_after_the_legs(self) -> None:
        path = self.clip("death", 70, kicked())
        record = run_pilot.ground_exported_clip(self.mesh_path, path, "death", {})
        self.assertTrue(record["kick"]["changed"], record)
        self.assertLess(list(record).index("legs"), list(record).index("kick"))
        self.assertLess(list(record).index("kick"), list(record).index("upper_body"))
        self.assertLessEqual(K.kick_numbers(self.mesh, self.load(path))["legs"]["left"]["rise"], K.BOOT_RISE_LIMIT)

    def test_the_limit_is_a_quarter_over_vanillas_worst(self) -> None:
        self.assertAlmostEqual(K.BOOT_RISE_LIMIT, round(1.25 * K.VANILLA_BOOT_RISE, 3))
        self.assertEqual(K.BOOT_RISE_TARGET, K.VANILLA_BOOT_RISE)


@unittest.skipUnless((UNITS / "GER_infantry.mesh").is_file(), "the game is not installed here")
class VanillaCalibration(unittest.TestCase):
    def test_vanillas_deaths_raise_a_boot_at_most_the_vanilla_worst(self) -> None:
        worst = 0.0
        for mesh_name in ("GER_infantry", "GER_infantry_alt_0", "ENG_infantry", "GER_infantry_snow"):
            mesh = pdx_deform.load_mesh(UNITS / f"{mesh_name}.mesh")
            for clip in ("death_rifle", "death_mg"):
                numbers = K.kick_numbers(mesh, pdx_deform.load_anim(UNITS / f"GER_infantry_{clip}.anim"))
                worst = max(worst, *(leg["rise"] for leg in numbers["legs"].values()))
        self.assertAlmostEqual(worst, K.VANILLA_BOOT_RISE, delta=0.0002)


if __name__ == "__main__":
    unittest.main()
