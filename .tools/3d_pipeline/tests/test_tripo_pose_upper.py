"""The Tripo route's stance twist and the death's upper-body rest, on a synthetic biped with arms and a head, and their calibration on
vanilla's GER infantry when the game is installed. No Blender."""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))
sys.path.insert(0, str(PIPELINE / "tripo"))

import run_pilot
import test_deformation_checks as TD
from lib import pdx_deform, tripo_pose as P, tripo_trim

GAME = Path(r"C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV")
UNITS = GAME / "gfx/models/units"

BONES = [
    ("Hips", -1, (0.0, 0.55, 0.0)),
    ("LeftUpLeg", 0, (-0.1, 0.5, 0.0)), ("LeftLeg", 1, (-0.1, 0.28, 0.0)), ("LeftFoot", 2, (-0.1, 0.06, 0.0)), ("LeftToeBase", 3, (-0.1, 0.0, 0.1)),
    ("RightUpLeg", 0, (0.1, 0.5, 0.0)), ("RightLeg", 5, (0.1, 0.28, 0.0)), ("RightFoot", 6, (0.1, 0.06, 0.0)), ("RightToeBase", 7, (0.1, 0.0, 0.1)),
    ("Spine", 0, (0.0, 0.7, 0.0)), ("Spine02", 9, (0.0, 0.85, 0.0)), ("neck", 10, (0.0, 0.92, 0.0)), ("Head", 11, (0.0, 0.97, 0.0)),
    ("LeftArm", 10, (-0.15, 0.88, 0.0)), ("LeftForeArm", 13, (-0.3, 0.88, 0.0)), ("LeftHand", 14, (-0.45, 0.88, 0.0)),
    ("RightArm", 10, (0.15, 0.88, 0.0)), ("RightForeArm", 16, (0.3, 0.88, 0.0)), ("RightHand", 17, (0.45, 0.88, 0.0)),
    ("Weapon", 18, (0.6, 0.88, 0.0)),
]
NAMES = [name for name, _parent, _position in BONES]
UPPER = {"Spine", "Spine02", "neck", "LeftArm", "RightArm"}


def turn(axis: str, degrees: float):
    half = math.radians(degrees) / 2.0
    vector = {"x": (1.0, 0.0, 0.0), "y": (0.0, 1.0, 0.0), "z": (0.0, 0.0, 1.0)}[axis]
    return tuple(math.sin(half) * v for v in vector) + (math.cos(half),)


def local(name: str):
    index = NAMES.index(name)
    parent = BONES[index][1]
    base = BONES[parent][2] if parent >= 0 else (0.0, 0.0, 0.0)
    return tuple(BONES[index][2][i] - base[i] for i in range(3))


class Biped(unittest.TestCase):
    def setUp(self) -> None:
        saved = list(TD.BONES)
        TD.BONES[:] = BONES
        self.addCleanup(lambda: TD.BONES.__setitem__(slice(None), saved))
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.mesh_path = self.folder / "unit.mesh"
        positions, triangles, owner = [], [], []
        for index, (_name, _parent, (x, y, z)) in enumerate(BONES):
            points, tris = TD.tetrahedron((x, y, z), 0.05)
            triangles += [tuple(len(positions) + i for i in tri) for tri in tris]
            positions += points
            owner += [index] * 4
        TD.write_mesh(self.mesh_path, positions, triangles, owner)
        self.mesh = pdx_deform.load_mesh(self.mesh_path)

    def clip(self, role: str, frames: int, pose) -> Path:
        path = self.folder / f"unit_{role}.anim"
        TD.write_anim(path, frames, pose)
        return path

    def load(self, path: Path):
        return pdx_deform.load_anim(path)


class StanceTwistTracks(unittest.TestCase):
    """`stance_twist_tracks` on plain tracks: one frame at rest, one with the shoulders turned 50 degrees."""

    def tracks(self, feet_turn=0.0, lift=(0.0, 0.0), pitch=0.0, up=1):
        angle = math.radians(50.0)
        left = np.array([[-1.0, 1.0, 0.0], [-math.cos(angle), 1.0, math.sin(angle)]])
        right = -left * np.array([1.0, -1.0, 1.0])
        yaw = np.array([[math.cos(math.radians(feet_turn)), 0.0, math.sin(math.radians(feet_turn))], [0.0, 1.0, 0.0],
                        [-math.sin(math.radians(feet_turn)), 0.0, math.cos(math.radians(feet_turn))]])
        tip = np.array([[1.0, 0.0, 0.0], [0.0, math.cos(math.radians(pitch)), -math.sin(math.radians(pitch))],
                        [0.0, math.sin(math.radians(pitch)), math.cos(math.radians(pitch))]])
        rotation = np.stack([np.eye(3), yaw @ tip])
        lifts = [np.array([0.0, lift[0]]), np.array([0.0, lift[1]])]
        swap = [0, 2, 1] if up == 2 else [0, 1, 2]  # the same pose with Z up
        flip = np.eye(3)[swap]
        return P.stance_twist_tracks(left @ flip.T, right @ flip.T, left[0] @ flip.T, right[0] @ flip.T,
                                     [flip @ rotation @ flip.T] * 2, [flip @ np.array([0.0, 0.0, 1.0])] * 2, lifts, up, 1.0)

    def test_the_shoulders_turned_against_feet_that_stay_read_their_turn(self) -> None:
        twist = self.tracks()
        self.assertAlmostEqual(float(twist[0]), 0.0)
        self.assertAlmostEqual(abs(float(twist[1])), 50.0, places=3)

    def test_feet_turned_with_the_shoulders_read_no_twist(self) -> None:
        twist = self.tracks(feet_turn=-50.0)
        self.assertAlmostEqual(min(abs(float(twist[1])), abs(float(self.tracks(feet_turn=50.0)[1]))), 0.0, places=3)

    def test_a_lifted_or_steep_foot_gives_no_reading(self) -> None:
        self.assertTrue(np.isnan(self.tracks(lift=(0.0, P.STANCE_PLANTED + 0.01))[1]))
        self.assertFalse(np.isnan(self.tracks(lift=(0.01, 0.01 + P.STANCE_PLANTED * 0.9))[1]))
        self.assertTrue(np.isnan(self.tracks(pitch=45.0)[1]))
        self.assertFalse(np.isnan(self.tracks(pitch=25.0)[1]))

    def test_blender_z_up_reads_as_the_files_y_up(self) -> None:
        self.assertAlmostEqual(abs(float(self.tracks(up=2)[1])), abs(float(self.tracks(up=1)[1])), places=3)

    def test_the_untwist_fills_unread_frames_from_the_read_ones_and_holds_the_ends(self) -> None:
        twist = np.array([np.nan, 30.0, np.nan, 50.0, np.nan])
        np.testing.assert_allclose(P.untwist_excess(twist, 20.0), [10.0, 10.0, 20.0, 30.0, 30.0])
        np.testing.assert_allclose(P.untwist_excess(np.full(3, np.nan), 20.0), [0.0, 0.0, 0.0])

    def test_each_role_has_a_limit_a_quarter_over_vanillas_worst(self) -> None:
        for role, value in P.VANILLA_WAIST_TWIST_DEGREES.items():
            self.assertAlmostEqual(P.WAIST_TWIST_LIMITS[role], round(1.25 * value, 1))
        self.assertEqual(P.VANILLA_WAIST_TWIST_DEGREES["defend"], P.VANILLA_WAIST_TWIST_DEGREES["attack"])


class StanceTwistClip(Biped):
    def wrung(self, hips: float, spine: float):
        """Hips turned `hips` about the up axis with the thighs turned back, the spine a further `spine`: the feet keep facing forward."""

        def pose(frame):
            k = frame / 19.0
            return {"Hips": (local("Hips"), turn("y", hips * k)), "LeftUpLeg": (local("LeftUpLeg"), turn("y", -hips * k)),
                    "RightUpLeg": (local("RightUpLeg"), turn("y", -hips * k)), "Spine": (local("Spine"), turn("y", spine * k))}

        return self.load(self.clip("attack", 20, pose))

    def test_the_hips_turning_with_the_chest_over_still_feet_is_read_by_the_stance_twist_not_the_hip_line(self) -> None:
        # The orc's attack (2026-11-16): the Hips bone turned with the chest and the legs turned back, so the hip line read 28 degrees and
        # passed while the chest turned 62 against the feet.
        anim = self.wrung(45.0, 15.0)
        self.assertAlmostEqual(float(np.abs(P.waist_twist(self.mesh, anim)).max()), 15.0, delta=0.5)
        self.assertAlmostEqual(float(np.nanmax(np.abs(P.stance_twist(self.mesh, anim)))), 60.0, delta=0.5)
        found, numbers = P.pose_findings(self.mesh, {"unit_attack": anim})
        self.assertIn("TRIPO-WAIST-TWIST", [item["rule"] for item in found], numbers)
        self.assertEqual(numbers["unit_attack"]["waist_twist_frame"], 19)
        self.assertAlmostEqual(numbers["unit_attack"]["hip_line_twist_degrees"], 15.0, delta=0.5)

    def test_a_twist_under_vanillas_worst_passes(self) -> None:
        found, _numbers = P.pose_findings(self.mesh, {"unit_attack": self.wrung(10.0, 20.0)})
        self.assertNotIn("TRIPO-WAIST-TWIST", [item["rule"] for item in found])

    def test_a_stride_gives_no_reading(self) -> None:
        def pose(frame):
            return {"LeftUpLeg": (local("LeftUpLeg"), turn("x", -40.0)), "Spine": (local("Spine"), turn("y", 70.0 * frame / 9.0))}

        twist = P.stance_twist(self.mesh, self.load(self.clip("move", 10, pose)))
        self.assertTrue(np.all(np.isnan(twist)))

    def test_a_body_lying_down_gives_no_reading(self) -> None:
        # The ogre's death (ogre_p, 2026-11-18) lay on its belly with both soles level side by side, and its turned shoulders read 75 degrees
        # against them. A body lying down has no stance: only frames whose torso stands within 60 degrees of upright count.
        def pose(frame):
            fall = min(frame / 10.0, 1.0)
            # the feet turned back so their soles lie level side by side, as the ogre's did
            return {"Hips": ((0.0, 0.55 - 0.45 * fall, 0.0), turn("x", 90.0 * fall)), "Spine": (local("Spine"), turn("y", 70.0 * fall)),
                    "LeftFoot": (local("LeftFoot"), turn("x", -90.0 * fall)), "RightFoot": (local("RightFoot"), turn("x", -90.0 * fall))}

        twist = P.stance_twist(self.mesh, self.load(self.clip("death", 20, pose)))
        self.assertFalse(np.isnan(twist[0]))
        self.assertTrue(np.all(np.isnan(twist[10:])), twist)


def lying(sit: float = 0.0, arms: float = 0.0, sit_from: int = 40):
    """Stand 20 frames, fall onto the back over 20 more and lie to frame 70. From `sit_from` the spine raises the chest `sit` degrees off
    the ground over 10 frames and the arms rise `arms` degrees: a body frozen half up."""

    def pose(frame: int):
        fall = min(max((frame - 20) / 20.0, 0.0), 1.0)
        rise = min(max((frame - sit_from) / 10.0, 0.0), 1.0)
        moved = {"Hips": ((0.0, 0.55 - 0.55 * fall, 0.0), turn("x", -90.0 * fall))}
        if sit:
            moved["Spine"] = (local("Spine"), turn("x", sit * rise))
        if arms:
            moved["LeftArm"] = (local("LeftArm"), turn("z", -arms * rise))
            moved["RightArm"] = (local("RightArm"), turn("z", arms * rise))
        return moved

    return pose


class DeathRest(Biped):
    def test_a_body_lying_flat_rests_and_passes(self) -> None:
        anim = self.load(self.clip("death", 70, lying()))
        rest = P.death_rest_heights(self.mesh, anim)
        self.assertLessEqual(max(rest[name] for name in ("chest", "head", "left hand", "right hand")), P.DEATH_REST_LIMIT, rest)
        self.assertLessEqual(rest["hips"], P.DEATH_FEET_LIMIT)
        found, _numbers = P.pose_findings(self.mesh, {"unit_death": anim})
        self.assertNotIn("TRIPO-DEATH-REST", [item["rule"] for item in found])

    def test_a_body_frozen_half_up_fails_and_the_settle_lays_it_down(self) -> None:
        path = self.clip("death", 70, lying(sit=40.0, arms=30.0))
        before = self.load(path)
        found, numbers = P.pose_findings(self.mesh, {"unit_death": before})
        self.assertIn("TRIPO-DEATH-REST", [item["rule"] for item in found], numbers)
        out = self.folder / "settled.anim"
        result = P.settle_death_upper(self.mesh_path, path, out)
        self.assertTrue(result.changed, result)
        self.assertIn("spine", result.turns)
        after = self.load(out)
        rest = P.death_rest_heights(self.mesh, after)
        self.assertLessEqual(max(rest[name] for name in ("chest", "head", "left hand", "right hand")), P.DEATH_REST_TARGET + 0.01, rest)
        self.assertLessEqual(rest["lift"], result.heights_before["lift"] + P.UPPER_SETTLE_LIFT, "never pushed through the ground")
        self.assertLessEqual(rest["hips"], P.DEATH_FEET_LIMIT)
        self.assertNotIn("TRIPO-DEATH-REST", [item["rule"] for item in P.pose_findings(self.mesh, {"unit_death": after})[0]])

    def test_only_the_upper_joints_turn_ramped_in_after_the_body_has_come_to_rest(self) -> None:
        path = self.clip("death", 70, lying(sit=40.0, arms=30.0))
        out = self.folder / "settled.anim"
        result = P.settle_death_upper(self.mesh_path, path, out)
        before, after = self.load(path), self.load(out)
        self.assertGreaterEqual(result.from_frame, 50, "the settle waits until the chest has stopped rising")
        for joint in before.channels:
            same = np.allclose(before.channels[joint]["q"], after.channels[joint]["q"], atol=1e-5)
            if joint not in UPPER:
                self.assertTrue(same, joint)
            self.assertTrue(np.allclose(before.channels[joint]["q"][:result.from_frame], after.channels[joint]["q"][:result.from_frame], atol=1e-6), joint)
            self.assertTrue(np.allclose(before.channels[joint]["t"], after.channels[joint]["t"], atol=1e-6))
            steps = [P.quaternion_turn(after.channels[joint]["q"][i], after.channels[joint]["q"][i + 1]) for i in range(after.frames - 1)]
            original = [P.quaternion_turn(before.channels[joint]["q"][i], before.channels[joint]["q"][i + 1]) for i in range(before.frames - 1)]
            self.assertLessEqual(max(steps), max(max(original), tripo_trim.SETTLE_MAX_RATE) + 1e-3, joint)

    def test_a_dropped_weapon_under_a_turned_arm_stays_where_it_fell(self) -> None:
        # The orc (2026-11-16): its released axe hangs from the right hand, and laying that arm down swung the axe 33% of the height into
        # the ground. A released bone below a turned joint keeps its place in the world.
        path = self.clip("death", 70, lying(sit=40.0, arms=30.0))
        out = self.folder / "settled.anim"
        result = P.settle_death_upper(self.mesh_path, path, out, exclude_bones=("Weapon",))
        self.assertTrue(result.changed, result)
        weapon = NAMES.index("Weapon")
        before = pdx_deform.skinning_matrices(self.mesh, self.load(path)) @ np.linalg.inv(self.mesh.inverse_bind)[None]
        after = pdx_deform.skinning_matrices(self.mesh, self.load(out)) @ np.linalg.inv(self.mesh.inverse_bind)[None]
        np.testing.assert_allclose(after[:, weapon], before[:, weapon], atol=1e-4)
        self.assertFalse(np.allclose(after[:, NAMES.index("RightHand")], before[:, NAMES.index("RightHand")], atol=1e-3))

    def test_a_body_lying_flat_is_left_as_it_was(self) -> None:
        path = self.clip("death", 70, lying())
        out = self.folder / "settled.anim"
        result = P.settle_death_upper(self.mesh_path, path, out)
        self.assertFalse(result.changed)
        self.assertEqual(path.read_bytes(), out.read_bytes())

    def test_a_body_that_does_not_lie_down_is_left_as_it_was(self) -> None:
        path = self.clip("death", 30, lambda frame: {"Spine": (local("Spine"), turn("x", 60.0 * frame / 29.0))})
        result = P.settle_death_upper(self.mesh_path, path, self.folder / "settled.anim")
        self.assertFalse(result.changed)
        self.assertIn("does not lie", result.note)

    def test_the_run_pilot_grounding_settles_the_upper_body_of_a_death(self) -> None:
        path = self.clip("death", 70, lying(sit=40.0, arms=30.0))
        record = run_pilot.ground_exported_clip(self.mesh_path, path, "death", {})
        self.assertTrue(record["upper_body"]["changed"], record)
        found, _numbers = P.pose_findings(self.mesh, {"unit_death": self.load(path)})
        self.assertEqual([item["rule"] for item in found if item["rule"].startswith("TRIPO-DEATH")], [])

    def test_the_limit_is_a_quarter_over_vanillas_worst_and_the_target_under_it(self) -> None:
        self.assertAlmostEqual(P.DEATH_REST_LIMIT, round(1.25 * P.VANILLA_DEATH_REST, 3))
        self.assertLess(P.DEATH_REST_TARGET, P.VANILLA_DEATH_REST)
        self.assertEqual(P.UPPER_SETTLE_GROUPS[0], "spine")


VANILLA_ROLES = {
    "retreat": ["retreat_mg", "retreat_rifle"],
    "move": ["march_mg", "march_rifle", "moving_mg", "moving_rifle"],
    "idle": ["idle_mg", "idle_rifle"] + [f"long_idle0{i}_{kind}" for i in range(1, 6) for kind in ("mg", "rifle")],
    "attack": ["charge_mg", "charge_rifle", "charge_mg_shoot", "charge_rifle_shoot", "attack_stand_mg", "attack_stand_rifle",
               "attack_crouch_mg", "attack_crouch_rifle"],
    "death": ["death_mg", "death_rifle"],
}


@unittest.skipUnless((UNITS / "GER_infantry.mesh").is_file(), "the game is not installed here")
class VanillaCalibration(unittest.TestCase):
    """The limits come from vanilla's GER infantry, whose clips every western infantry mesh plays."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.mesh = pdx_deform.load_mesh(UNITS / "GER_infantry.mesh")

    def test_the_stance_twist_of_each_role_is_vanillas_worst(self) -> None:
        for role, clips in VANILLA_ROLES.items():
            worst = max(float(np.nanmax(np.abs(np.nan_to_num(P.stance_twist(self.mesh, pdx_deform.load_anim(UNITS / f"GER_infantry_{clip}.anim")))))) for clip in clips)
            with self.subTest(role=role):
                self.assertAlmostEqual(worst, P.VANILLA_WAIST_TWIST_DEGREES[role], delta=0.1)

    def test_vanillas_deaths_rest_within_the_vanilla_worst(self) -> None:
        worst = 0.0
        for clip in VANILLA_ROLES["death"]:
            rest = P.death_rest_heights(self.mesh, pdx_deform.load_anim(UNITS / f"GER_infantry_{clip}.anim"))
            worst = max(worst, *(rest[name] for name in ("chest", "head", "left hand", "right hand")))
        self.assertAlmostEqual(worst, P.VANILLA_DEATH_REST, delta=0.001)


if __name__ == "__main__":
    unittest.main()
