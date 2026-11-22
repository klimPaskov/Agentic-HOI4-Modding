"""The map camera's outline rules for a humanoid (lib/map_outline.py): TRIPO-MAP-POSTURE, TRIPO-MAP-SPREAD, TRIPO-MAP-REACH and TRIPO-MAP-SAME,
on a synthetic box humanoid, and their limits against the D-94 zombie runs reviewers failed and the humanoids they passed. No Blender."""

from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tripo"))

import pose_check
import tripo_checks as TC
from lib import map_outline as M
from lib import pdx_deform as P

# name, parent, joint (x right, y up, z: the unit faces -z), box half sizes around the segment to the next joint (or around the joint)
BONES = [
    ("Hips", -1, (0.0, 1.0, 0.0)),
    ("LeftUpLeg", 0, (0.1, 0.95, 0.0)), ("LeftLeg", 1, (0.1, 0.5, 0.0)), ("LeftFoot", 2, (0.1, 0.06, 0.0)),
    ("RightUpLeg", 0, (-0.1, 0.95, 0.0)), ("RightLeg", 4, (-0.1, 0.5, 0.0)), ("RightFoot", 5, (-0.1, 0.06, 0.0)),
    ("Spine", 0, (0.0, 1.2, 0.0)), ("Spine02", 7, (0.0, 1.45, 0.0)), ("neck", 8, (0.0, 1.58, -0.02)), ("Head", 9, (0.0, 1.68, -0.05)),
    ("LeftShoulder", 8, (0.08, 1.52, 0.0)), ("LeftArm", 11, (0.2, 1.5, 0.0)), ("LeftForeArm", 12, (0.2, 1.22, 0.0)), ("LeftHand", 13, (0.2, 0.96, 0.0)),
    ("RightShoulder", 8, (-0.08, 1.52, 0.0)), ("RightArm", 15, (-0.2, 1.5, 0.0)), ("RightForeArm", 16, (-0.2, 1.22, 0.0)), ("RightHand", 17, (-0.2, 0.96, 0.0)),
]
# each part: the bone that carries it, and its two ends (a box 2 * half thick along the segment)
PARTS = [
    ("Hips", (0.0, 0.9, 0.0), (0.0, 1.05, 0.0), 0.14), ("Spine", (0.0, 1.05, 0.0), (0.0, 1.3, 0.0), 0.15), ("Spine02", (0.0, 1.3, 0.0), (0.0, 1.55, 0.0), 0.17),
    ("neck", (0.0, 1.55, -0.02), (0.0, 1.64, -0.03), 0.05), ("Head", (0.0, 1.64, -0.04), (0.0, 1.82, -0.05), 0.09),
    ("LeftUpLeg", (0.1, 0.95, 0.0), (0.1, 0.5, 0.0), 0.07), ("LeftLeg", (0.1, 0.5, 0.0), (0.1, 0.06, 0.0), 0.06), ("LeftFoot", (0.1, 0.06, 0.0), (0.1, 0.0, -0.14), 0.05),
    ("RightUpLeg", (-0.1, 0.95, 0.0), (-0.1, 0.5, 0.0), 0.07), ("RightLeg", (-0.1, 0.5, 0.0), (-0.1, 0.06, 0.0), 0.06), ("RightFoot", (-0.1, 0.06, 0.0), (-0.1, 0.0, -0.14), 0.05),
    ("LeftArm", (0.2, 1.5, 0.0), (0.2, 1.22, 0.0), 0.045), ("LeftForeArm", (0.2, 1.22, 0.0), (0.2, 0.96, 0.0), 0.04), ("LeftHand", (0.2, 0.96, 0.0), (0.2, 0.86, 0.0), 0.04),
    ("RightArm", (-0.2, 1.5, 0.0), (-0.2, 1.22, 0.0), 0.045), ("RightForeArm", (-0.2, 1.22, 0.0), (-0.2, 0.96, 0.0), 0.04), ("RightHand", (-0.2, 0.96, 0.0), (-0.2, 0.86, 0.0), 0.04),
]
CUBE = [(0, 1, 2), (0, 2, 3), (4, 6, 5), (4, 7, 6), (0, 4, 5), (0, 5, 1), (1, 5, 6), (1, 6, 2), (2, 6, 7), (2, 7, 3), (3, 7, 4), (3, 4, 0)]
NAMES = [name for name, _parent, _joint in BONES]


def box(start, end, half):
    """Eight corners of a box around the segment from `start` to `end`, `half` thick on each side."""

    a, b = np.array(start, float), np.array(end, float)
    axis = b - a
    axis /= np.linalg.norm(axis)
    helper = np.array([1.0, 0.0, 0.0]) if abs(axis[0]) < 0.9 else np.array([0.0, 0.0, 1.0])
    u = np.cross(axis, helper)
    u /= np.linalg.norm(u)
    v = np.cross(axis, u)
    ring = [half * (su * u + sv * v) for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return [a + r for r in ring] + [b + r for r in ring]


def humanoid(extra_bones=(), extra_parts=()) -> P.SkinnedMesh:
    bones, parts = list(BONES) + list(extra_bones), list(PARTS) + list(extra_parts)
    names = [name for name, _parent, _joint in bones]
    positions, triangles, joints = [], [], []
    for bone, start, end, half in parts:
        base = len(positions)
        positions += box(start, end, half)
        triangles += [tuple(base + i for i in tri) for tri in CUBE]
        joints += [[names.index(bone), -1, -1, -1]] * 8
    world = np.tile(np.eye(4), (len(bones), 1, 1))
    for index, (_name, _parent, joint) in enumerate(bones):
        world[index, :3, 3] = joint
    weights = np.zeros((len(positions), 4))
    weights[:, 0] = 1.0
    return P.SkinnedMesh(positions=np.array(positions, float), triangles=np.array(triangles), joints=np.array(joints), weights=weights,
                         bones=names, parents=[parent for _name, parent, _joint in bones], inverse_bind=np.linalg.inv(world))


def quat(axis: int, degrees: float) -> np.ndarray:
    half = math.radians(degrees) / 2.0
    q = np.array([0.0, 0.0, 0.0, math.cos(half)])
    q[axis] = math.sin(half)
    return q


def compose(*quats: np.ndarray) -> np.ndarray:
    out = np.array([0.0, 0.0, 0.0, 1.0])
    for q in quats:
        x1, y1, z1, w1 = out
        x2, y2, z2, w2 = q
        out = np.array([w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2, w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
                        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2, w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2])
    return out


def clip(mesh: P.SkinnedMesh, poses: dict, frames: int = 12) -> P.Animation:
    """A clip holding `poses` ({bone: quaternion}) in every frame, the other bones at rest."""

    world = np.linalg.inv(mesh.inverse_bind)
    channels = {}
    for index, name in enumerate(mesh.bones):
        parent = mesh.parents[index]
        offset = world[index, :3, 3] - (world[parent, :3, 3] if parent >= 0 else 0.0)
        q = poses.get(name, np.array([0.0, 0.0, 0.0, 1.0]))
        channels[name] = {"t": np.tile(offset, (frames, 1)), "q": np.tile(q, (frames, 1)), "s": np.ones(frames)}
    return P.Animation(fps=30.0, frames=frames, channels=channels)


# poses: the arms hang along the body at rest. About x a positive turn swings a hanging arm forward (toward -z), about z it raises it sideways.
UPRIGHT = {}
HUNCH = {"Spine": quat(0, -22.0), "Spine02": quat(0, -14.0)}
T_POSE = {"LeftArm": quat(2, 85.0), "RightArm": quat(2, -85.0)}
# both hands forward, down and in toward each other, as zombie_f's grab
FORWARD_REACH = {"LeftArm": compose(quat(2, -20.0), quat(0, 50.0)), "RightArm": compose(quat(2, 20.0), quat(0, 50.0))}
SIDE_SWING = {"LeftArm": compose(quat(2, 70.0), quat(0, 30.0))}
GUARD = {"LeftArm": quat(0, 40.0), "LeftForeArm": quat(0, 80.0), "RightArm": quat(0, 40.0), "RightForeArm": quat(0, 80.0)}


def anims(mesh, idle=UPRIGHT, attack=SIDE_SWING, defend=GUARD) -> dict:
    return {"u_idle": clip(mesh, idle), "u_attack": clip(mesh, attack), "u_defend": clip(mesh, defend)}


def rules(found) -> list:
    return sorted((item["rule"], item["subject"]) for item in found)


class Posture(unittest.TestCase):
    def test_a_hunched_idle_reads_hunched_and_an_upright_one_upright(self) -> None:
        mesh = humanoid()
        found, numbers = M.outline_findings(mesh, anims(mesh, idle=HUNCH), "hunched")
        self.assertLessEqual(numbers["posture"]["ratio"], M.POSTURE_LIMIT)
        self.assertNotIn("TRIPO-MAP-POSTURE", [item["rule"] for item in found])
        found, numbers = M.outline_findings(mesh, anims(mesh), "upright")
        self.assertGreater(numbers["posture"]["ratio"], M.POSTURE_LIMIT)
        self.assertEqual(rules(found), [])

    def test_an_upright_idle_fails_when_the_job_asks_for_a_hunch(self) -> None:
        # zombie_d: the job meant a zombie, the idle stood upright, both reviewers read a live soldier
        mesh = humanoid()
        found, _numbers = M.outline_findings(mesh, anims(mesh), "hunched")
        self.assertEqual(rules(found), [("TRIPO-MAP-POSTURE", "u_idle")])

    def test_a_hunched_idle_fails_when_the_job_asks_for_upright(self) -> None:
        mesh = humanoid()
        found, _numbers = M.outline_findings(mesh, anims(mesh, idle=HUNCH), "upright")
        self.assertEqual(rules(found), [("TRIPO-MAP-POSTURE", "u_idle")])

    def test_the_job_names_the_posture(self) -> None:
        self.assertEqual(M.posture_of({"tripo": {"posture": "hunched"}}), "hunched")
        self.assertEqual(M.posture_of({"tripo": {"idle_pose": "hunch"}}), "hunched", "the hunch rule means a hunched idle")
        self.assertEqual(M.posture_of({"tripo": {}}), "upright")
        self.assertEqual(M.posture_of(None), "upright")
        with self.assertRaises(ValueError):
            M.posture_of({"tripo": {"posture": "crouched"}})
        with self.assertRaises(ValueError):
            M.outline_findings(humanoid(), {}, "sideways")


class Spread(unittest.TestCase):
    def test_arms_spread_wide_read_as_a_t_pose(self) -> None:
        # zombie_h: the wide grab's peak and the recoil defend, both read as a T-pose
        mesh = humanoid()
        found, numbers = M.outline_findings(mesh, anims(mesh, attack=T_POSE), "upright")
        self.assertIn(("TRIPO-MAP-SPREAD", "u_attack"), rules(found))
        self.assertGreaterEqual(numbers["spread"]["u_attack"]["p90"], M.SPREAD_LIMIT)
        self.assertLess(numbers["spread"]["u_defend"]["p90"], M.SPREAD_LIMIT)
        spread = next(item for item in found if item["rule"] == "TRIPO-MAP-SPREAD")
        self.assertIsInstance(spread["frame"], int, "the review sheet shows the flagged frame")

    def test_hands_held_in_front_do_not_spread(self) -> None:
        mesh = humanoid()
        _found, numbers = M.outline_findings(mesh, anims(mesh, attack=FORWARD_REACH), "upright")
        self.assertLess(numbers["spread"]["u_attack"]["p90"], 0.4)


class Same(unittest.TestCase):
    def test_an_attack_and_a_defend_that_both_spread_read_as_each_other(self) -> None:
        mesh = humanoid()
        found, _numbers = M.outline_findings(mesh, anims(mesh, attack=T_POSE, defend=T_POSE), "upright")
        self.assertIn(("TRIPO-MAP-SAME", "u_defend"), rules(found))
        self.assertIn(("TRIPO-MAP-SPREAD", "u_attack"), rules(found))
        self.assertIn(("TRIPO-MAP-SPREAD", "u_defend"), rules(found))

    def test_one_spread_is_not_a_shared_outline(self) -> None:
        mesh = humanoid()
        found, _numbers = M.outline_findings(mesh, anims(mesh, attack=T_POSE), "upright")
        self.assertNotIn("TRIPO-MAP-SAME", [item["rule"] for item in found])


class Reach(unittest.TestCase):
    def test_a_forward_reach_foreshortens_into_the_body(self) -> None:
        # zombie_f: from the high front camera the hands come toward the viewer and land on the body
        mesh = humanoid()
        found, numbers = M.outline_findings(mesh, anims(mesh, attack=FORWARD_REACH), "upright")
        self.assertEqual(rules(found), [("TRIPO-MAP-REACH", "u_attack")])
        self.assertLess(numbers["reach"]["u_attack"]["pixels"], M.MIN_REACH_PIXELS)
        self.assertEqual(numbers["reach"]["u_attack"]["striking_end"], "hands")

    def test_a_swing_out_to_the_side_shows(self) -> None:
        mesh = humanoid()
        found, numbers = M.outline_findings(mesh, anims(mesh), "upright")
        self.assertEqual(rules(found), [])
        self.assertGreaterEqual(numbers["reach"]["u_attack"]["pixels"], M.MIN_REACH_PIXELS)

    def test_an_armed_unit_strikes_with_its_weapon(self) -> None:
        # a pole held in the right hand along the arm: the same forward reach shows its far end beyond the body (orc_k 16 px)
        mesh = humanoid([("Weapon", NAMES.index("RightHand"), (-0.2, 0.9, 0.0))], [("Weapon", (-0.2, 0.95, 0.0), (-0.2, -0.2, 0.0), 0.02)])
        found, numbers = M.outline_findings(mesh, anims(mesh, attack=FORWARD_REACH), "upright", weapon_bone="Weapon")
        self.assertEqual(numbers["reach"]["u_attack"]["striking_end"], "weapon")
        self.assertGreaterEqual(numbers["reach"]["u_attack"]["pixels"], M.MIN_REACH_PIXELS)
        self.assertNotIn("TRIPO-MAP-REACH", [item["rule"] for item in found])

    def test_a_winged_unit_reach_is_not_judged(self) -> None:
        # demon_g: its claws stay inside the outline and reviewers read the attack by its wings
        mesh = humanoid([("LeftWing", NAMES.index("Spine02"), (0.1, 1.45, 0.1))], [("LeftWing", (0.1, 1.45, 0.12), (0.6, 1.7, 0.2), 0.02)])
        found, numbers = M.outline_findings(mesh, anims(mesh, attack=FORWARD_REACH), "upright")
        self.assertNotIn("TRIPO-MAP-REACH", [item["rule"] for item in found])
        self.assertIn("not judged", numbers["reach"]["u_attack"])

    def test_no_idle_no_reading(self) -> None:
        mesh = humanoid()
        self.assertEqual(M.outline_findings(mesh, {"u_attack": clip(mesh, T_POSE)}), ([], {}))


class Calibration(unittest.TestCase):
    """The readings of lib/map_outline.py on the exported files (2026-11-22). Each limit must sit between what reviewers failed and passed."""

    def test_posture(self) -> None:
        hunched_passed = (0.881, 0.881)  # zombie_f, zombie_h with the hunch rule
        upright = (1.0, 1.075, 1.024, 1.0, 0.977, 0.976, 0.976)  # zombie_d, zombie_w, orc_k, ogre_l, dwarf_f, demon_g, vanilla GER idle_rifle
        self.assertGreaterEqual(M.POSTURE_LIMIT, max(hunched_passed))
        self.assertLess(M.POSTURE_LIMIT, min(upright))

    def test_spread(self) -> None:
        failed = (0.869, 1.208)  # zombie_h attack and defend
        passed = (0.624, 0.699, 0.69, 0.563, 0.544, 0.63, 0.025, 0.27, 0.236, 0.199, 0.534, 0.35, 0.448, 0.397)
        self.assertLessEqual(M.SPREAD_LIMIT, min(failed))
        self.assertGreater(M.SPREAD_LIMIT, max(passed))

    def test_reach(self) -> None:
        failed = (4, 4)  # zombie_f, zombie_w
        passed = (16, 9, 29, 11)  # orc_k, ogre_l, dwarf_f, zombie_d (its arm flung to the side)
        self.assertGreater(M.MIN_REACH_PIXELS, max(failed))
        self.assertLessEqual(M.MIN_REACH_PIXELS, min(passed))


class Wiring(unittest.TestCase):
    def test_tripo_checks_reads_the_posture_from_the_job(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            config = Path(temp) / "jobs.json"
            config.write_text(json.dumps({"jobs": {"z": {"tripo": {"idle_pose": "hunch"}}, "o": {"tripo": {}}}}), encoding="utf-8")
            self.assertEqual(TC.job_posture(argparse.Namespace(posture=None, jobs_config=config, slug="z")), "hunched")
            self.assertEqual(TC.job_posture(argparse.Namespace(posture=None, jobs_config=config, slug="o")), "upright")
            self.assertEqual(TC.job_posture(argparse.Namespace(posture="hunched", jobs_config=config, slug="o")), "hunched")
        self.assertEqual(TC.job_posture(argparse.Namespace(posture=None, jobs_config=None, slug=None)), "upright")

    def test_body_findings_runs_the_outline_rules(self) -> None:
        mesh = humanoid()
        saved = TC.hand_bleed_findings
        TC.hand_bleed_findings = lambda _mesh: ([], {})  # the box humanoid has no hand skin to bleed
        self.addCleanup(setattr, TC, "hand_bleed_findings", saved)
        numbers: dict = {}
        found = TC.body_findings(mesh, anims(mesh, attack=FORWARD_REACH), numbers, posture="hunched")
        names = [item["rule"] for item in found]
        self.assertIn("TRIPO-MAP-POSTURE", names)
        self.assertIn("TRIPO-MAP-REACH", names)
        self.assertEqual(numbers["map_outline"]["posture_asked"], "hunched")

    def test_pose_check_does_not_pick_a_t_pose_or_a_foreshortened_attack(self) -> None:
        def row(spread, reach):
            route = {"reach": 0.4, "pelvis_travel": 0.2, "map_pixels": 500.0, "map_spread": spread, "map_reach": reach}
            return {"attack": True, "verdict": "pass", "route": route}

        self.assertIsNone(pose_check.pick_attack({"t": row(0.9, 12), "inside": row(0.3, 3)}))
        self.assertEqual(pose_check.pick_attack({"t": row(0.9, 12), "good": row(0.3, 12)}), "good")


if __name__ == "__main__":
    unittest.main()
