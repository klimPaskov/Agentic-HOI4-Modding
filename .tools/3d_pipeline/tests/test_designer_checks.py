"""The designer-size rules (tripo/designer_checks.py, lib/designer_read.py) on the synthetic box humanoid of test_map_outline: an attack that
barely moves, a retreat that shows the move's poses and a part that hides the head, with the death's end measured and reported. No
Blender."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))
sys.path.insert(0, str(PIPELINE / "tripo"))

import designer_checks as DC
from lib import designer_read as D
from lib import pdx_deform as P
from test_map_outline import compose, humanoid, quat

REST = np.array([0.0, 0.0, 0.0, 1.0])


def slerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    dot = float(np.dot(a, b))
    if dot < 0:
        b, dot = -b, -dot
    if dot > 0.9995:
        out = a + t * (b - a)
        return out / np.linalg.norm(out)
    theta = math.acos(dot)
    return (math.sin((1 - t) * theta) * a + math.sin(t * theta) * b) / math.sin(theta)


def moving(mesh: P.SkinnedMesh, keys, frames: int = 24, root_shift=None) -> P.Animation:
    """A clip through the poses `keys` ({bone: quaternion} each), evenly spaced and blended, the other bones at rest. `root_shift` moves
    the hips by (frame -> offset) for a body that falls."""

    world = np.linalg.inv(mesh.inverse_bind)
    channels = {}
    for index, name in enumerate(mesh.bones):
        parent = mesh.parents[index]
        offset = world[index, :3, 3] - (world[parent, :3, 3] if parent >= 0 else 0.0)
        q = np.zeros((frames, 4))
        t = np.tile(offset, (frames, 1))
        for frame in range(frames):
            position = frame / max(frames - 1, 1) * (len(keys) - 1)
            low = int(math.floor(position))
            high = min(low + 1, len(keys) - 1)
            q[frame] = slerp(keys[low].get(name, REST), keys[high].get(name, REST), position - low)
            if root_shift is not None and parent < 0:
                t[frame] = offset + root_shift(frame)
        channels[name] = {"t": t, "q": q, "s": np.ones(frames)}
    return P.Animation(fps=24.0, frames=frames, channels=channels)


# a two-handed overhead blow: both arms raised behind the head, then brought down in front with the torso bent into it
WIND_UP = {"LeftArm": quat(0, -150.0), "RightArm": quat(0, -150.0), "Spine": quat(0, -15.0)}
BLOW = {"LeftArm": quat(0, 60.0), "RightArm": quat(0, 60.0), "Spine": quat(0, 40.0), "Spine02": quat(0, 20.0)}
TWITCH = {"RightArm": quat(0, 6.0)}
STRIDE_A = {"LeftUpLeg": quat(0, 25.0), "RightUpLeg": quat(0, -25.0), "LeftArm": quat(0, -20.0), "RightArm": quat(0, 20.0)}
STRIDE_B = {"LeftUpLeg": quat(0, -25.0), "RightUpLeg": quat(0, 25.0), "LeftArm": quat(0, 20.0), "RightArm": quat(0, -20.0)}
RUN_A = {"LeftUpLeg": quat(0, 60.0), "LeftLeg": quat(0, -70.0), "RightUpLeg": quat(0, -40.0), "Spine": quat(0, 25.0),
         "LeftArm": quat(0, -55.0), "RightArm": quat(0, 55.0), "LeftForeArm": quat(0, 70.0), "RightForeArm": quat(0, 70.0)}
RUN_B = {"LeftUpLeg": quat(0, -40.0), "RightUpLeg": quat(0, 60.0), "RightLeg": quat(0, -70.0), "Spine": quat(0, 25.0),
         "LeftArm": quat(0, 55.0), "RightArm": quat(0, -55.0), "LeftForeArm": quat(0, 70.0), "RightForeArm": quat(0, 70.0)}
SWAY = {"Spine": quat(2, 3.0)}


def rules(found) -> list:
    return sorted((item["rule"], item["subject"].rsplit("_", 1)[-1]) for item in found)


class Pose(unittest.TestCase):
    def setUp(self) -> None:
        self.mesh = humanoid()

    def anims(self, attack, move, retreat, idle=None):
        return {"u_idle": moving(self.mesh, idle or [{}, SWAY, {}]), "u_attack": moving(self.mesh, attack),
                "u_move": moving(self.mesh, move), "u_retreat": moving(self.mesh, retreat)}

    def test_a_strike_with_a_wind_up_and_a_blow_passes_and_a_twitch_fails(self) -> None:
        found, numbers = DC.pose_findings(self.mesh, self.anims([{}, WIND_UP, BLOW, {}], [STRIDE_A, STRIDE_B, STRIDE_A], [RUN_A, RUN_B, RUN_A]))
        self.assertEqual(rules(found), [])
        self.assertGreaterEqual(numbers["attack"]["spread"], DC.MIN_ATTACK_SPREAD)
        found, numbers = DC.pose_findings(self.mesh, self.anims([{}, TWITCH, {}], [STRIDE_A, STRIDE_B, STRIDE_A], [RUN_A, RUN_B, RUN_A]))
        self.assertEqual(rules(found), [("TRIPO-DESIGNER-STRIKE-STILL", "attack")])
        self.assertLess(numbers["attack"]["spread"], DC.MIN_ATTACK_SPREAD)

    def test_a_retreat_that_is_the_move_again_fails(self) -> None:
        found, numbers = DC.pose_findings(self.mesh, self.anims([{}, WIND_UP, BLOW, {}], [STRIDE_A, STRIDE_B, STRIDE_A], [STRIDE_A, STRIDE_B, STRIDE_A]))
        self.assertIn(("TRIPO-DESIGNER-GAIT-ALIKE", "retreat"), rules(found))
        self.assertGreater(numbers["gait_alike"], DC.MAX_GAIT_ALIKE)

    def test_a_slide_or_a_bob_is_no_new_pose(self) -> None:
        pose = D.ScreenPose(self.mesh)
        still = pose.frames(moving(self.mesh, [{}, {}]))
        slid = pose.frames(moving(self.mesh, [{}, {}], root_shift=lambda f: np.array([0.02 * f, 0.01 * f, 0.0])))
        self.assertLess(float(D.pose_distance(still, slid).max()), 1e-6)


class Silhouette(unittest.TestCase):
    def setUp(self) -> None:
        self.mesh = humanoid()

    def test_solidity_of_a_block_and_of_an_l(self) -> None:
        block = np.zeros((20, 20), bool)
        block[5:15, 5:15] = True
        self.assertAlmostEqual(D.solidity(block), 1.0, places=2)
        ell = np.zeros((20, 20), bool)
        ell[2:18, 2:5] = True
        ell[15:18, 2:18] = True
        self.assertLess(D.solidity(ell), 0.55)

    def test_a_body_lying_with_its_limbs_apart_passes_and_a_curled_lump_fails(self) -> None:
        lie = {"Hips": quat(0, -90.0)}
        spread = dict(lie, LeftArm=quat(2, 80.0), RightArm=quat(2, -80.0), LeftUpLeg=quat(2, 30.0), RightUpLeg=quat(2, -30.0))
        curled = dict(lie, Spine=quat(0, 70.0), Spine02=quat(0, 60.0), LeftUpLeg=quat(0, 120.0), RightUpLeg=quat(0, 120.0),
                      LeftLeg=quat(0, -150.0), RightLeg=quat(0, -150.0), LeftArm=quat(0, 100.0), RightArm=quat(0, 100.0),
                      LeftForeArm=quat(0, 120.0), RightForeArm=quat(0, 120.0))
        down = lambda f: np.array([0.0, -0.85 * f / 23, 0.0])  # noqa: E731
        camera = D.DesignerCamera(self.mesh, 1.0)
        apart = D.death_end(camera, moving(self.mesh, [{}, spread], root_shift=down))["solidity"]
        lump = D.death_end(camera, moving(self.mesh, [{}, curled], root_shift=down))["solidity"]
        self.assertLess(apart, lump)

    def test_a_weapon_left_apart_from_the_dead_body_is_measured_and_reported_not_judged(self) -> None:
        mesh = humanoid(extra_bones=[("Weapon", 18, (-0.2, 0.86, 0.0))], extra_parts=[("Weapon", (-0.2, 0.86, 0.0), (-0.2, 0.86, -0.6), 0.03)])
        held = moving(mesh, [{}, {}])
        dropped = moving(mesh, [{}, {}])
        dropped.channels["Weapon"]["t"] = dropped.channels["Weapon"]["t"] + np.linspace(0, 1, 24)[:, None] * np.array([-0.9, -0.5, 0.0])
        found, numbers = DC.silhouette_findings(mesh, {"u_death": held}, 1.0, "Weapon")
        self.assertEqual(numbers["death_end"]["weapon_gap"], 0)
        found, numbers = DC.silhouette_findings(mesh, {"u_death": dropped}, 1.0, "Weapon")
        self.assertGreater(numbers["death_end"]["weapon_gap"], 3)
        self.assertEqual(found, [], "the passed orc and ogre drop their weapons apart from the body too")
        self.assertFalse(numbers["death_end"]["judged"])

    def test_the_held_weapon_is_no_cover_in_the_attack_but_is_in_the_idle(self) -> None:
        # a broad blade held up before the face for the whole clip
        mesh = humanoid(extra_bones=[("Weapon", 18, (0.0, 1.73, -0.3))],
                        extra_parts=[("Weapon", (-0.2, 1.73, -0.3), (0.2, 1.73, -0.3), 0.2)])
        clip = moving(mesh, [{}, {}], frames=24)
        camera = D.DesignerCamera(mesh, 1.0)
        self.assertGreater(max(D.head_hidden(camera, clip, step=1)), DC.HEAD_HIDDEN_SHARE, "the blade covers the head")
        found, numbers = DC.silhouette_findings(mesh, {"u_attack": clip, "u_idle": clip}, 1.0, "Weapon")
        self.assertEqual(rules(found), [("TRIPO-DESIGNER-HEAD-HIDDEN", "idle")])
        self.assertEqual(numbers["head_hidden"]["u_attack"]["longest_seconds"], 0.0)

    def test_a_wing_held_before_the_head_fails_and_one_that_passes_it_briefly_does_not(self) -> None:
        # a flat wing on its own bone off the chest, swung in front of the face (toward the camera)
        mesh = humanoid(extra_bones=[("Wing_R1", 8, (-0.1, 1.73, 0.05))],
                        extra_parts=[("Wing_R1", (-0.1, 1.73, 0.05), (-0.7, 1.73, 0.05), 0.25)])
        front = quat(1, -120.0)  # the wing (on the far side from the camera) turns forward about the up axis, across the face
        held = moving(mesh, [{}, {"Wing_R1": front}, {"Wing_R1": front}, {"Wing_R1": front}, {}], frames=48)
        brief = moving(mesh, [{}] * 12 + [{"Wing_R1": front}] + [{}] * 12, frames=48)  # in front for about two frames
        camera = D.DesignerCamera(mesh, 1.0)
        held_shares, brief_shares = D.head_hidden(camera, held, step=1), D.head_hidden(camera, brief, step=1)
        self.assertGreater(max(held_shares), DC.HEAD_HIDDEN_SHARE, "the wing covers the head")
        self.assertLess(max(D.head_hidden(camera, moving(mesh, [{}, {}]), step=1)), 0.05, "at rest the wing stands beside the head")
        found, _numbers = DC.silhouette_findings(mesh, {"u_retreat": held}, 1.0)
        self.assertEqual(rules(found), [("TRIPO-DESIGNER-HEAD-HIDDEN", "retreat")])
        found, _numbers = DC.silhouette_findings(mesh, {"u_retreat": brief}, 1.0)
        self.assertEqual(rules(found), [], f"a brief pass of the wing ({max(brief_shares):.2f} at worst) is no fault")


class Limits(unittest.TestCase):
    def test_the_limits_sit_between_the_passed_runs_and_the_failed_ones(self) -> None:
        # tripo/designer_checks.py's calibration, on the lanes' exported files (2026-11-28)
        # (the lowest passed and the highest failed reading over the designer camera and the camera turned 10 degrees each way)
        passed_spread, failed_spread = (0.149, 0.195, 0.271, 0.215), (0.106, 0.125)
        self.assertLess(DC.MIN_ATTACK_SPREAD, min(passed_spread))
        self.assertGreater(DC.MIN_ATTACK_SPREAD, max(failed_spread))
        passed_gait, failed_gait = (0.0, 0.0, 0.0, 0.0), 0.43
        self.assertGreater(DC.MAX_GAIT_ALIKE, max(passed_gait))
        self.assertLess(DC.MAX_GAIT_ALIKE, failed_gait)
        # the head: the devil's retreat over its wing side hid the head 0.2 s running at 30 frames a second, the passed bipeds 0 s
        self.assertLess(DC.MAX_HEAD_HIDDEN_SECONDS, 6 / 30)
        self.assertGreaterEqual(DC.MAX_HEAD_HIDDEN_SECONDS, 0.0)


if __name__ == "__main__":
    unittest.main()
