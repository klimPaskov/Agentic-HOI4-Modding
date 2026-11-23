"""The weapon checks on runtime files (a mesh and an animation in memory): the weapon through the body, under the ground, and its grip."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tripo"))

import tripo_checks as TC
from lib import pdx_deform as P

CUBE = np.array([[x, y, z] for x in (-0.5, 0.5) for y in (-0.5, 0.5) for z in (-0.5, 0.5)], float)
CUBE_TRIANGLES = np.array([
    [0, 1, 3], [0, 3, 2], [4, 6, 7], [4, 7, 5], [0, 4, 5], [0, 5, 1],
    [2, 3, 7], [2, 7, 6], [0, 2, 6], [0, 6, 4], [1, 5, 7], [1, 7, 3],
])
JOINT = np.array([1.2, 0.0, 0.0])


def unit_mesh() -> P.SkinnedMesh:
    """A box body on bone `Root` and a vertical stick on bone `Weapon` (a child of the root, its joint at x = 1.2), one unit tall."""

    stick = np.array([[1.2, y, 0.0] for y in np.linspace(-0.5, 0.5, 120)])
    positions = np.concatenate([CUBE, stick])
    joints = np.full((len(positions), 4), -1)
    weights = np.zeros((len(positions), 4))
    joints[: len(CUBE), 0], joints[len(CUBE) :, 0] = 0, 1
    weights[:, 0] = 1.0
    inverse = np.stack([np.eye(4), np.eye(4)])
    inverse[1, :3, 3] = -JOINT
    return P.SkinnedMesh(positions=positions, triangles=CUBE_TRIANGLES, joints=joints, weights=weights, bones=["Root", "Weapon"], parents=[-1, 0], inverse_bind=inverse)


def unit_anim(weapon_t: np.ndarray) -> P.Animation:
    """One frame per row of `weapon_t`, the weapon bone's translation relative to its parent; the root stays at rest."""

    frames = len(weapon_t)
    rest = {"t": np.zeros((frames, 3)), "q": np.tile([0.0, 0.0, 0.0, 1.0], (frames, 1)), "s": np.ones(frames)}
    weapon = {"t": np.asarray(weapon_t, float), "q": rest["q"].copy(), "s": rest["s"].copy()}
    return P.Animation(fps=30.0, frames=frames, channels={"Root": rest, "Weapon": weapon})


class WeaponOnRuntimeFiles(unittest.TestCase):
    def setUp(self) -> None:
        self.mesh = unit_mesh()

    def test_a_weapon_that_stays_clear_passes_with_no_numbers_over(self) -> None:
        findings, numbers = TC.weapon_runtime_findings(self.mesh, {"u_idle": unit_anim([JOINT] * 5)}, "Weapon")
        self.assertEqual(findings, [])
        self.assertEqual(numbers["u_idle"]["frames_over"], 0)
        self.assertEqual(numbers["u_idle"]["moved_in_last_half_share"], 0.0)

    def test_a_weapon_swung_through_the_body_fails_in_the_frames_it_is_inside(self) -> None:
        path = [JOINT, JOINT, JOINT, np.zeros(3), np.zeros(3), JOINT]
        findings, numbers = TC.weapon_runtime_findings(self.mesh, {"u_attack": unit_anim(path)}, "Weapon")
        self.assertEqual([f["rule"] for f in findings], ["TRIPO-WEAPON-IN-BODY"])
        self.assertEqual(findings[0]["frames"], [3, 4])
        self.assertGreater(numbers["u_attack"]["worst_in_body_pct"], 50.0)
        self.assertEqual(numbers["u_attack"]["frames_over"], 2)

    def test_the_grip_zone_around_the_joint_is_left_out_of_the_judged_points(self) -> None:
        weapon, _triangles, indices, free, _c = TC.weapon_split(self.mesh, "Weapon")
        self.assertEqual(int(weapon.sum()), 120)
        zone = np.linalg.norm(self.mesh.positions[indices] - JOINT, axis=1) <= TC.WEAPON_GRIP_ZONE_SHARE * self.mesh.height
        self.assertTrue(zone.any() and bool((~free[zone]).all()) and bool(free[~zone].all()))

    def test_a_weapon_under_the_ground_fails(self) -> None:
        path = [JOINT, JOINT + [0.0, -2.0, 0.0], JOINT + [0.0, -2.0, 0.0]]
        findings, numbers = TC.weapon_runtime_findings(self.mesh, {"u_death": unit_anim(path)}, "Weapon")
        self.assertIn("TRIPO-WEAPON-BELOW-GROUND", [f["rule"] for f in findings])
        self.assertEqual(numbers["u_death"]["frames_below_ground"], 2)
        self.assertEqual(numbers["u_death"]["worst_below_ground_pct"], 100.0)

    def test_only_the_named_roles_are_judged_and_a_unit_without_the_bone_is_left_alone(self) -> None:
        anims = {"u_attack": unit_anim([np.zeros(3)] * 3), "u_idle": unit_anim([JOINT] * 3)}
        findings, numbers = TC.weapon_runtime_findings(self.mesh, anims, "Weapon", roles=["idle"])
        self.assertEqual((findings, list(numbers)), ([], ["u_idle"]))
        self.assertEqual(TC.weapon_runtime_findings(self.mesh, anims, "Sword"), ([], {}))

    def test_a_weapon_that_keeps_moving_after_it_should_have_landed_shows_in_the_movement_number(self) -> None:
        path = [JOINT + [0.0, 0.1 * k, 0.0] for k in range(10)]
        _findings, numbers = TC.weapon_runtime_findings(self.mesh, {"u_death": unit_anim(path)}, "Weapon")
        self.assertGreater(numbers["u_death"]["moved_in_last_half_share"], 0.3)


class GripAdvisory(unittest.TestCase):
    ENCLOSURE = {"rule": "TRIPO-GRIP-ENCLOSURE", "subject": "grip", "message": "hand skin covers 37%"}
    THUMB = {"rule": "TRIPO-GRIP-THUMB", "subject": "grip", "message": "the thumb is on their side"}

    def args(self, **kwargs):
        import argparse

        return argparse.Namespace(**{"grip_advisory": False, "jobs_config": None, "slug": None, **kwargs})

    def job(self, grip_check):
        import json
        import tempfile

        folder = Path(tempfile.mkdtemp(prefix="hoi4_grip_check_"))
        self.addCleanup(lambda: [p.unlink() for p in folder.iterdir()] and folder.rmdir())
        weapon = {"bone": "Weapon"} if grip_check is None else {"bone": "Weapon", "grip_check": grip_check}
        path = folder / "jobs.json"
        path.write_text(json.dumps({"jobs": {"unit": {"tripo": {"weapon": weapon}}}}), encoding="utf-8")
        return path

    def test_by_default_the_enclosure_finding_fails_the_unit(self) -> None:
        rules = TC.advisory_rules(self.args())
        failing, advisory = TC.split_advisory([self.ENCLOSURE, self.THUMB], rules)
        self.assertEqual((failing, advisory), ([self.ENCLOSURE, self.THUMB], []))
        self.assertEqual(TC.advisory_rules(self.args(jobs_config=self.job(None), slug="unit")), set(TC.MAP_READ_RULES))
        self.assertEqual(TC.advisory_rules(self.args(jobs_config=self.job("strict"), slug="unit")), set(TC.MAP_READ_RULES))

    def test_the_map_read_rules_are_advice_and_never_fail_a_unit(self) -> None:
        # D-140: animations are judged at the designer preview's size and in Blender close-ups, so the map camera readings only advise.
        reach = {"rule": "TRIPO-MAP-REACH", "subject": "unit_attack", "message": "strike 3 px outside the body"}
        wings = {"rule": "TRIPO-WING-IDLE-MOVE", "subject": "unit_move", "message": "1.6 times the idle"}
        failing, advisory = TC.split_advisory([reach, wings, self.THUMB], TC.advisory_rules(self.args()))
        self.assertEqual(failing, [self.THUMB])
        self.assertEqual(advisory, [reach, wings])

    def test_a_job_that_says_advisory_reports_the_enclosure_without_failing_and_never_excuses_the_thumb(self) -> None:
        for arguments in (self.args(jobs_config=self.job("advisory"), slug="unit"), self.args(grip_advisory=True)):
            failing, advisory = TC.split_advisory([self.ENCLOSURE, self.THUMB], TC.advisory_rules(arguments))
            self.assertEqual(failing, [self.THUMB])
            self.assertEqual(advisory, [self.ENCLOSURE])


if __name__ == "__main__":
    unittest.main()
