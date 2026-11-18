"""The Tripo route's shoulder rule on a synthetic biped whose upper back is a sheet behind the spine: the swelling measure, TRIPO-SHOULDER-SWELL and
the ease that fixes it (lib/tripo_shoulder.py). No Blender."""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))
sys.path.insert(0, str(PIPELINE / "tripo"))

import run_pilot
import test_deformation_checks as TD
import tripo_checks as TC
from lib import pdx_deform, tripo_pose as P, tripo_shoulder as S
from test_tripo_neck import BONES, about, local

TS_BONES = BONES

# The back sheet: a grid behind the spine on the left side, its lower rows bound to the hips and its upper rows to the spine, so a bent
# spine stretches the row between them (the seam), as Tripo's hard borders on the ogre's hump did.
COLUMNS = (0.02, 0.06, 0.10, 0.14)
ROWS = (1.18, 1.23, 1.28, 1.33, 1.38, 1.43, 1.48, 1.53, 1.58)
DEPTH = 0.15
SEAM = 1.3


def bent(degrees: float) -> dict:
    return {"Spine": (local("Spine"), about(0, degrees))}


class Unit(unittest.TestCase):
    def setUp(self) -> None:
        self.saved = list(TD.BONES)
        TD.BONES[:] = BONES
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.addCleanup(lambda: TD.BONES.__setitem__(slice(None), self.saved))
        self.folder = Path(temp.name)
        self.mesh_path = self.folder / "unit.mesh"
        names = [b[0] for b in BONES]
        positions, triangles, owner = [], [], []
        for index, (_name, _parent, (x, y, z)) in enumerate(BONES):
            base = len(positions)
            points, tris = TD.tetrahedron((x, y, z), 0.03)
            positions += points
            triangles += [tuple(base + i for i in tri) for tri in tris]
            owner += [index] * 4
        base = len(positions)
        for y in ROWS:
            for x in COLUMNS:
                positions.append((x, y, DEPTH))
                owner.append(names.index("Hips") if y < SEAM else names.index("Spine"))
        width = len(COLUMNS)
        for r in range(len(ROWS) - 1):
            for c in range(width - 1):
                a, b = base + r * width + c, base + r * width + c + 1
                d, e = a + width, b + width
                triangles += [(a, b, e), (a, e, d)]
        TD.write_mesh(self.mesh_path, positions, triangles, owner)
        self.mesh = pdx_deform.load_mesh(self.mesh_path)
        self.sheet = np.arange(base, len(positions))

    def clip(self, role: str, frames: int, pose) -> Path:
        path = self.folder / f"unit_{role}.anim"
        TD.write_anim(path, frames, pose)
        return path

    def swelling(self, path: Path) -> np.ndarray:
        return S.swelling(self.mesh, pdx_deform.load_anim(path))


class Measure(Unit):
    def test_the_limit_is_vanillas_worst_with_a_quarter_added_and_the_target_vanillas_worst(self) -> None:
        self.assertAlmostEqual(S.SWELL_LIMIT, 1.25 * S.VANILLA_SWELL_WORST, places=4)
        self.assertEqual(S.SWELL_TARGET, S.VANILLA_SWELL_WORST)
        self.assertAlmostEqual(S.AREA_RATIO, 1.3 ** 2, places=6)

    def test_the_region_is_the_torso_between_the_midline_and_the_arm_joint(self) -> None:
        regions = S.shoulder_regions(self.mesh)
        self.assertEqual(sorted(regions), ["left", "right"])
        self.assertTrue(regions["left"][self.sheet].all(), "the back sheet lies inside the left region")
        self.assertFalse(regions["right"][self.sheet].any())
        arm = [b[0] for b in BONES].index("LeftForeArm")
        self.assertFalse(regions["left"][4 * arm], "the elbow lies beyond the arm joint")

    def test_the_rest_pose_does_not_swell_and_a_bent_spine_does(self) -> None:
        self.assertTrue(np.allclose(self.swelling(self.clip("idle", 3, lambda f: {})), 0.0))
        bent_spine = self.swelling(self.clip("attack", 3, lambda f: bent(60.0)))
        self.assertGreater(float(bent_spine.max()), S.SWELL_LIMIT)
        # only the seam row grows: one of the sheet's eight rows of equal area, less with the bones' own small solids in the region
        self.assertLessEqual(float(bent_spine.max()), 1.0 / (len(ROWS) - 1) + 1e-9)

    def test_a_body_without_a_head_has_no_measure(self) -> None:
        self.mesh.bones[self.mesh.bones.index("Head")] = "Skull"
        self.assertIsNone(S.shoulder_rig(self.mesh))
        self.assertEqual(S.shoulder_findings(self.mesh, {})[0], [])


class Check(Unit):
    def test_a_swollen_clip_fails_and_names_its_worst_frame(self) -> None:
        swollen = pdx_deform.load_anim(self.clip("attack", 6, lambda f: bent(12.0 * f)))
        still = pdx_deform.load_anim(self.clip("idle", 6, lambda f: bent(2.0)))
        found, numbers = S.shoulder_findings(self.mesh, {"unit_attack": swollen, "unit_idle": still})
        self.assertEqual([(item["rule"], item["subject"]) for item in found], [("TRIPO-SHOULDER-SWELL", "unit_attack")])
        self.assertEqual(found[0]["frame"], int(np.argmax(S.swelling(self.mesh, swollen))))
        self.assertLessEqual(numbers["unit_idle"]["worst_share"], S.SWELL_LIMIT)

    def test_the_unit_checks_run_it_for_a_humanoid(self) -> None:
        anims = {"unit_defend": pdx_deform.load_anim(self.clip("defend", 4, lambda f: bent(60.0)))}
        numbers: dict = {}
        found = TC.body_findings(self.mesh, anims, numbers)
        self.assertIn("TRIPO-SHOULDER-SWELL", [item["rule"] for item in found])
        self.assertIn("unit_defend", numbers["shoulders"])


class Ease(Unit):
    def test_a_clip_under_the_limit_is_copied_byte_for_byte(self) -> None:
        path = self.clip("attack", 6, lambda f: bent(3.0))
        before = path.read_bytes()
        out = self.folder / "out.anim"
        ease = S.ease_shoulders(self.mesh_path, path, out, "attack")
        self.assertFalse(ease.changed)
        self.assertEqual(out.read_bytes(), before)

    def test_a_bent_spine_is_turned_toward_the_idles_stance_and_nothing_else_moves(self) -> None:
        idle = self.clip("idle", 4, lambda f: bent(5.0))
        path = self.clip("defend", 21, lambda f: bent(60.0 * math.sin(math.pi * f / 20)))
        anim = pdx_deform.load_anim(path)
        ease = S.ease_shoulders(self.mesh_path, path, path, "defend", idle)
        after = pdx_deform.load_anim(path)
        self.assertTrue(ease.changed)
        self.assertEqual(ease.group, "spine")
        self.assertEqual(ease.reference, "idle's first frame")
        self.assertGreater(ease.worst_before, S.SWELL_LIMIT)
        self.assertLessEqual(float(S.swelling(self.mesh, after).max()), S.SWELL_TARGET + 1e-9)
        self.assertFalse(ease.tried["clavicles"]["reaches_target"])
        for joint in self.mesh.bones:
            if joint != "Spine":
                self.assertTrue(np.allclose(anim.channels[joint]["q"], after.channels[joint]["q"]), joint)
        # the loop's seam stays and the frames that did not swell keep their pose
        self.assertLessEqual(P.loop_seam(self.mesh, after)[0], P.loop_seam(self.mesh, anim)[0] + 1e-3)
        self.assertTrue(np.allclose(anim.channels["Spine"]["q"][0], after.channels["Spine"]["q"][0]))

    def test_the_stance_is_the_idles_first_frame_or_the_rest_pose(self) -> None:
        idle = pdx_deform.load_anim(self.clip("idle", 3, lambda f: bent(20.0 + f)))
        stance = S.stance(self.mesh, idle)
        self.assertAlmostEqual(P.quaternion_turn(stance["Spine"], np.array([0.0, 0.0, 0.0, 1.0])), 20.0, places=3)
        self.assertAlmostEqual(P.quaternion_turn(S.stance(self.mesh, None)["Spine"], np.array([0.0, 0.0, 0.0, 1.0])), 0.0, places=3)

    def test_a_share_that_breaks_the_kits_rule_in_a_frame_is_not_used(self) -> None:
        before = {"stretched": 10, "squashed": 4, "worst": 0.02}
        frames = np.array([[10, 4, 0.02], [11, 5, 0.0203], [12, 4, 0.01], [10, 6, 0.01], [10, 4, 0.021]])
        self.assertEqual(S.within(frames, before).tolist(), [True, True, False, False, False])
        self.assertEqual(S.summary(frames), {"stretched": 12, "squashed": 6, "worst": 0.021})


class Lever(Unit):
    """The clavicle lever on a sheet whose upper rows the left clavicle carries, as Tripo binds the upper back."""

    def setUp(self) -> None:
        super().setUp()
        names = [b[0] for b in TS_BONES]
        positions, triangles, owner = [], [], []
        for index, (_name, _parent, (x, y, z)) in enumerate(TS_BONES):
            base = len(positions)
            points, tris = TD.tetrahedron((x, y, z), 0.03)
            positions += points
            triangles += [tuple(base + i for i in tri) for tri in tris]
            owner += [index] * 4
        base = len(positions)
        for row, y in enumerate(ROWS):
            for x in COLUMNS:
                positions.append((x, y, DEPTH))
                owner.append(names.index("LeftShoulder") if row % 2 else names.index("Spine"))  # every row between the two bones
        width = len(COLUMNS)
        for r in range(len(ROWS) - 1):
            for c in range(width - 1):
                a, b = base + r * width + c, base + r * width + c + 1
                triangles += [(a, b, b + width), (a, b + width, a + width)]
        TD.write_mesh(self.mesh_path, positions, triangles, owner)
        self.mesh = pdx_deform.load_mesh(self.mesh_path)

    def shrug(self, degrees: float) -> dict:
        return {"LeftShoulder": (local("LeftShoulder"), about(0, degrees)), "LeftArm": (local("LeftArm"), about(2, 40.0))}

    def test_a_shrug_that_tears_the_girdle_turns_the_clavicle_back_and_the_arm_keeps_its_direction(self) -> None:
        idle = self.clip("idle", 3, lambda f: {})
        path = self.clip("defend", 21, lambda f: self.shrug(70.0 * math.sin(math.pi * f / 20)))
        anim = pdx_deform.load_anim(path)
        before = float(S.swelling(self.mesh, anim, girdle=True).max())
        self.assertGreater(before, S.GIRDLE_LIMIT)
        ease = S.ease_clavicles(self.mesh_path, path, path, "defend", idle)
        after = pdx_deform.load_anim(path)
        self.assertTrue(ease.changed, ease.note or ease.tried)
        self.assertIn("LeftShoulder", ease.joints)
        self.assertLessEqual(float(S.swelling(self.mesh, after, girdle=True).max()), S.GIRDLE_TARGET + 1e-9)
        arm = self.mesh.bones.index("LeftArm")
        self.assertTrue(np.allclose(S._world_rotations(self.mesh, anim, [arm]), S._world_rotations(self.mesh, after, [arm]), atol=1e-4))
        self.assertLessEqual(S._max_step(after, ["LeftShoulder", "LeftArm"]), S.MAX_STEP_DEGREES)
        self.assertEqual(ease.hand_shift, 0.0)  # the fixture has no hand: the elbow moves with the arm root

    def test_the_lever_aims_at_vanillas_worst_not_the_checks_limit(self) -> None:
        # the review sheets still showed the ogre's armpit torn at 0.154 to 0.156, under the limit
        self.assertEqual(S.GIRDLE_TARGET, S.VANILLA_GIRDLE_WORST)
        self.assertLess(S.GIRDLE_TARGET, S.GIRDLE_LIMIT)
        idle = self.clip("idle", 3, lambda f: {})
        path = self.clip("defend", 21, lambda f: self.shrug(15.0 * math.sin(math.pi * f / 20)))
        before = float(S.swelling(self.mesh, pdx_deform.load_anim(path), girdle=True).max())
        # the fixture's tear moves in steps of a tenth: with the limit set above this clip, only the target can start the lever
        with mock.patch.object(S, "GIRDLE_LIMIT", before + 0.05), mock.patch.object(S, "GIRDLE_TARGET", before - 0.05):
            ease = S.ease_clavicles(self.mesh_path, path, path, "defend", idle)
        self.assertTrue(ease.changed, ease.note or ease.tried)
        self.assertLess(float(S.swelling(self.mesh, pdx_deform.load_anim(path), girdle=True).max()), before)

    def test_a_clip_under_both_limits_is_copied_byte_for_byte(self) -> None:
        path = self.clip("attack", 5, lambda f: self.shrug(2.0))
        data = path.read_bytes()
        out = self.folder / "out.anim"
        ease = S.ease_clavicles(self.mesh_path, path, out, "attack")
        self.assertFalse(ease.changed)
        self.assertEqual(out.read_bytes(), data)


class Pilot(Unit):
    def test_every_role_is_eased_with_the_idle_last_and_recorded(self) -> None:
        records = {"u_idle.anim": {}, "u_attack.anim": {}, "u_defend.anim": {}}
        (self.folder / "u_idle.anim").write_bytes(b"")
        with mock.patch.object(S, "ease_shoulders", return_value=S.ShoulderEase(True, "spine", ("Spine",), 0.5, 4, 6, 0.1, 0.05)) as ease, \
                mock.patch.object(S, "ease_clavicles", return_value=S.ClavicleEase(True, "left clavicle", ("LeftShoulder",), 0.4)) as lever, \
                mock.patch.object(run_pilot, "file_record", lambda path, relative_to=None: {}):
            run_pilot.ease_staged_shoulders(self.folder, self.folder, {"runtime_stem": "u"}, ["attack", "idle", "defend"], records)
        self.assertEqual([call.args[3] for call in ease.call_args_list], ["attack", "defend", "idle"])
        self.assertEqual([call.args[3] for call in lever.call_args_list], ["attack", "defend", "idle"])
        self.assertEqual(records["u_defend.anim"]["clavicle_ease"]["joints"], ["LeftShoulder"])
        self.assertEqual(ease.call_args_list[0].args[4], self.folder / "u_idle.anim")
        self.assertEqual(records["u_attack.anim"]["shoulder_ease"]["joints"], ["Spine"])
        self.assertIn("staged", records["u_defend.anim"])

    def test_a_quadruped_or_the_switch_off_is_left_alone(self) -> None:
        for spec in ({"runtime_stem": "u", "tripo": {"ease_shoulders": False}},):
            with mock.patch.object(S, "ease_shoulders") as ease, mock.patch.object(S, "ease_clavicles") as lever:
                run_pilot.ease_staged_shoulders(self.folder, self.folder, spec, ["attack"], {"u_attack.anim": {}})
            ease.assert_not_called()
            lever.assert_not_called()
        with mock.patch.object(S, "ease_shoulders") as ease, mock.patch.object(run_pilot, "tripo_quadruped", return_value=True):
            run_pilot.ease_staged_shoulders(self.folder, self.folder, {"runtime_stem": "u"}, ["attack"], {"u_attack.anim": {}})
        ease.assert_not_called()


if __name__ == "__main__":
    unittest.main()
