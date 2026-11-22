"""Tripo's two humanoid rigs (lib/tripo_rig.py) and the hip travel read through them (lib/glb_root.py), on synthetic names and GLB files.
No Blender."""

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

from lib import glb_root, tripo_rig as R

# The newer Tripo rig's bones (the demon's export of 2026-11-18, trimmed to one finger chain and one twist bone a limb).
TRIPO = ["BoneRoot", "Hip", "Pelvis", "Waist", "Spine01", "Spine02", "NeckTwist01", "NeckTwist02", "Head", "FacialBone", "neutral_bone"]
for side in "LR":
    TRIPO += [f"{side}_{part}" for part in ("Clavicle", "Upperarm", "UpperarmTwist01", "Forearm", "Hand", "Index1", "Mid1", "Thigh", "Calf",
                                             "KneeShareBone", "Foot", "ToeBase")]
MIXAMO = ["mixamorig:" + name for name in ("Hips", "Spine", "Spine1", "Spine2", "Neck", "Head", "LeftShoulder", "LeftArm", "LeftForeArm",
                                           "LeftHand", "LeftHandIndex1", "RightShoulder", "RightArm", "RightForeArm", "RightHand",
                                           "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase", "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase")]


class Names(unittest.TestCase):
    def test_the_style_is_read_from_the_bones(self) -> None:
        self.assertEqual(R.rig_style(MIXAMO), "mixamo")
        self.assertEqual(R.rig_style(TRIPO), "tripo")
        with self.assertRaises(R.RigError):
            R.rig_style(["Root", "Spine", "Head"])

    def test_both_rigs_reach_every_kit_bone(self) -> None:
        for names in (MIXAMO, TRIPO):
            self.assertEqual(set(R.RigNames(names).kit_map().values()), R.kit_bone_names(), names[0])

    def test_the_newer_rigs_bones_map_by_rule(self) -> None:
        rig = R.RigNames(TRIPO)
        expected = {"Hip": "Hips", "Waist": "Spine", "Spine01": "Spine01", "Spine02": "Spine02", "NeckTwist01": "neck", "Head": "Head",
                    "L_Clavicle": "LeftShoulder", "L_Upperarm": "LeftArm", "L_Forearm": "LeftForeArm", "L_Hand": "LeftHand",
                    "R_Thigh": "RightUpLeg", "R_Calf": "RightLeg", "R_Foot": "RightFoot", "R_ToeBase": "RightToeBase"}
        for actual, kit in expected.items():
            self.assertEqual(rig.kit(actual), kit, actual)
        for dropped in ("BoneRoot", "Pelvis", "NeckTwist02", "L_UpperarmTwist01", "L_KneeShareBone", "FacialBone", "neutral_bone", "L_Index1"):
            self.assertIsNone(rig.kit(dropped), dropped)
        self.assertEqual(rig.canonical("R_Mid1"), "RightHandMiddle1")
        self.assertEqual(rig.actual("LeftHandIndex1"), "L_Index1")
        self.assertEqual(rig.actual("Hips"), "Hip")

    def test_mixamo_names_keep_their_prefix(self) -> None:
        rig = R.RigNames(MIXAMO)
        self.assertEqual(rig.actual("Spine1"), "mixamorig:Spine1")
        self.assertEqual(rig.kit("mixamorig:Spine1"), "Spine01")
        self.assertEqual(R.BoneNamer(MIXAMO).name("Weapon"), "mixamorig:Weapon")
        self.assertEqual(R.BoneNamer(TRIPO).name("Weapon"), "Weapon")
        self.assertEqual(R.BoneNamer().name("RightHand"), "mixamorig:RightHand")
        self.assertTrue(R.BoneNamer(TRIPO).in_family("R_Index1", "RightHand"))

    def test_in_between_bones_are_told_from_leaves(self) -> None:
        parents = {"BoneRoot": None, "Hip": "BoneRoot", "Pelvis": "Hip", "L_Thigh": "Pelvis", "Waist": "Hip", "NeckTwist01": "Waist",
                   "NeckTwist02": "NeckTwist01", "Head": "NeckTwist02", "FacialBone": "Head", "L_ThighTwist01": "L_Thigh", "neutral_bone": None}
        kept = {"Hip", "L_Thigh", "Waist", "NeckTwist01", "Head"}
        roles = R.dropped_roles(parents, kept)
        self.assertEqual({b for b, r in roles.items() if r == "in-between"}, {"BoneRoot", "Pelvis", "NeckTwist02"})
        self.assertEqual({b for b, r in roles.items() if r == "leaf"}, {"FacialBone", "L_ThighTwist01", "neutral_bone"})
        self.assertEqual(R.composition_order(parents, ["NeckTwist02", "Pelvis", "BoneRoot"])[0], "BoneRoot")


def trs(t=(0.0, 0.0, 0.0), axis=(0.0, 0.0, 1.0), degrees=0.0) -> np.ndarray:
    m = np.eye(4)
    a = np.asarray(axis, float) / np.linalg.norm(axis)
    k = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    angle = math.radians(degrees)
    m[:3, :3] = np.eye(3) + math.sin(angle) * k + (1 - math.cos(angle)) * k @ k
    m[:3, 3] = t
    return m


class Compose(unittest.TestCase):
    def test_a_child_keeps_its_pose_when_its_parent_is_removed(self) -> None:
        # rests in armature space: A at the origin, P above it turned, C above P; Blender's pose = parent_pose @ parent_rest^-1 @ rest @ basis
        rest_a, rest_p, rest_c = trs((0, 0, 0)), trs((0, 0, 1), (1, 0, 0), 30.0), trs((0, 0.2, 2), (0, 1, 0), -20.0)
        basis_a, basis_p, basis_c = trs((0.1, 0, 0), (0, 0, 1), 15.0), trs((0, 0.3, 0), (0, 1, 0), 40.0), trs((0, 0, 0), (1, 1, 0), 25.0)
        pose_a = rest_a @ basis_a
        pose_p = pose_a @ np.linalg.inv(rest_a) @ rest_p @ basis_p
        pose_c = pose_p @ np.linalg.inv(rest_p) @ rest_c @ basis_c
        composed = R.compose_basis(rest_p, rest_c, basis_p, basis_c)
        np.testing.assert_allclose(pose_a @ np.linalg.inv(rest_a) @ rest_c @ composed, pose_c, atol=1e-12)
        # a root parent (BoneRoot) removed: the child becomes the root and keeps its pose
        root_pose_c = (rest_p @ basis_p) @ np.linalg.inv(rest_p) @ rest_c @ basis_c
        np.testing.assert_allclose(rest_c @ composed, root_pose_c, atol=1e-12)


class HipTravel(unittest.TestCase):
    def write(self, folder: str, names, parents, rests, moving: int, values, name: str = "u.glb") -> Path:
        import test_glb_root as G  # noqa: F401  (the writer below follows its layout)
        import json
        import struct

        blob = b""
        times = np.linspace(0.0, 1.0, len(values), dtype=np.float32)
        values = np.asarray(values, np.float32)
        accessors, views = [], []
        for array, kind in ((times, "SCALAR"), (values, "VEC3")):
            data = array.tobytes()
            views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(data)})
            accessors.append({"bufferView": len(views) - 1, "componentType": 5126, "count": len(array), "type": kind})
            blob += data
        nodes = [{"name": "Armature", "children": [i + 1 for i, p in enumerate(parents) if p is None]}]
        for i, (n, t) in enumerate(zip(names, rests)):
            nodes.append({"name": n, "translation": list(t), "children": [j + 1 for j, p in enumerate(parents) if p == i]})
        doc = {"asset": {"version": "2.0"}, "nodes": nodes, "skins": [{"joints": list(range(1, len(names) + 1))}],
               "buffers": [{"byteLength": len(blob)}], "bufferViews": views, "accessors": accessors,
               "animations": [{"name": "clip", "samplers": [{"input": 0, "output": 1}], "channels": [{"sampler": 0, "target": {"node": moving + 1, "path": "translation"}}]}]}
        text = json.dumps(doc).encode()
        text += b" " * (-len(text) % 4)
        blob += b"\0" * (-len(blob) % 4)
        body = struct.pack("<I4s", len(text), b"JSON") + text + struct.pack("<I4s", len(blob), b"BIN\0") + blob
        path = Path(folder) / name
        path.write_bytes(struct.pack("<4sII", b"glTF", 2, 12 + len(body)) + body)
        return path

    def test_a_rig_without_a_hip_bone_is_refused_loudly(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, ["Root", "Spine"], [None, 0], [(0, 1, 0), (0, 0.2, 0)], 0, [[0, 1, 0], [0, 1, 3]])
            with self.assertRaises(R.RigError):
                glb_root.root_travel(path)
            with self.assertRaises(R.RigError):  # not swallowed as "not a glTF" by the intake's refusal
                glb_root.travelling_clips(path, ["clip"])

    def test_the_newer_rigs_root_motion_is_read_above_the_hip(self) -> None:
        # the newer rig keeps the travel in BoneRoot, above a Hip whose own offset is about zero
        names = ["BoneRoot", "Hip", "L_Thigh", "R_Thigh"]
        parents = [None, 0, 1, 1]
        rests = [(0, 1, 0), (0, 0, 0), (0.1, 0, 0), (-0.1, 0, 0)]
        walk = [[0.0, 1.0, 2.0 * t] for t in np.linspace(0, 1, 20)]
        with tempfile.TemporaryDirectory() as folder:
            travel = glb_root.root_travel(self.write(folder, names, parents, rests, 0, walk))
        self.assertAlmostEqual(travel["clip"], 2.0, places=3)

    def test_a_death_is_judged_against_vanillas_deaths(self) -> None:
        self.assertAlmostEqual(glb_root.DEATH_TRAVEL_LIMIT, round(1.25 * glb_root.VANILLA_DEATH_TRAVEL, 2))
        fall = [[0.0, 1.0, 0.5 * t] for t in np.linspace(0, 1, 20)]  # 0.5 hip heights: a fall, over the loop limit
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, ["mixamorig:Hips"], [None], [(0, 1, 0)], 0, fall)
            self.assertEqual(list(glb_root.travelling_clips(path, ["clip"])), ["clip"])
            self.assertEqual(glb_root.travelling_clips(path, [], deaths=["clip"]), {})


if __name__ == "__main__":
    unittest.main()
