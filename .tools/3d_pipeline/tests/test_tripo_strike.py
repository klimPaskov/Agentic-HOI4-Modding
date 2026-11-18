"""The strike of a Tripo attack (lib/tripo_strike.py): the striking hand's travel and speed, TRIPO-ATTACK-NO-STRIKE, pose_check's attack
verdict and pick, on the synthetic biped of test_tripo_pose_upper, and the calibration on vanilla's shooting attacks when the game is
installed. No Blender."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))
sys.path.insert(0, str(PIPELINE / "tripo"))

import pose_check
import tripo_checks as TC
from lib import pdx_deform, tripo_strike as S
from test_tripo_pose_upper import UNITS, Biped, local, turn


def swing(degrees: float = 90.0, side: str = "Right"):
    """The upper arm swung down `degrees` and back over frames 10 to 22 of 30: a blow."""

    sign = -1.0 if side == "Right" else 1.0

    def pose(frame: int):
        share = min(max((frame - 10) / 6.0, 0.0), 1.0) - min(max((frame - 16) / 6.0, 0.0), 1.0)
        return {f"{side}Arm": (local(f"{side}Arm"), turn("z", sign * degrees * share))}

    return pose


def held(frame: int):
    """Both arms held still in one reach for the whole clip, the hips stepping forward: a lunge with no blow."""

    step = min(frame / 30.0, 1.0)
    return {"Hips": ((0.0, 0.55, 0.2 * step), (0.0, 0.0, 0.0, 1.0)),
            "LeftArm": (local("LeftArm"), turn("y", 80.0)), "RightArm": (local("RightArm"), turn("y", -80.0))}


class Numbers(unittest.TestCase):
    def test_travel_is_the_widest_sweep_and_speed_the_fastest_tenth_of_a_second(self) -> None:
        chest = np.zeros((5, 3))
        hand = np.array([[0.0, 0.0, 0.0], [0.0, 0.1, 0.0], [0.0, 0.4, 0.0], [0.0, 0.5, 0.0], [0.0, 0.5, 0.0]])
        travel, speed = S.hand_strike(hand, chest, 1.0, 30.0, window=3)
        self.assertAlmostEqual(travel, 0.5)
        self.assertAlmostEqual(speed, 0.5 / 0.1)

    def test_the_faster_hand_strikes_for_an_unarmed_unit_and_the_holding_hand_for_an_armed_one(self) -> None:
        frames = 10
        joints = np.zeros((frames, 3, 3))
        joints[:, 1, 1] = np.linspace(0.0, 0.5, frames)  # LeftHand sweeps
        joints[:, 2, 1] = 0.05 * np.sin(np.arange(frames))  # RightHand trembles
        bones = ["Spine02", "LeftHand", "RightHand"]
        self.assertEqual(S.strike_numbers(joints, bones, 1.0, 30.0)["hand"], "LeftHand")
        armed = S.strike_numbers(joints, bones, 1.0, 30.0, "RightHand")
        self.assertEqual(armed["hand"], "RightHand")
        self.assertFalse(armed["strikes"])


class Strike(Biped):
    def test_a_blow_strikes_and_a_held_reach_does_not(self) -> None:
        blow = S.clip_strike(self.mesh, self.load(self.clip("attack", 30, swing())))
        self.assertTrue(blow["strikes"], blow)
        self.assertEqual(blow["hand"], "RightHand")
        still = S.clip_strike(self.mesh, self.load(self.clip("attack", 30, held)))
        self.assertFalse(still["strikes"], still)
        self.assertLess(still["travel"], S.MIN_TRAVEL)

    def test_the_checks_fail_an_attack_with_no_strike_only(self) -> None:
        anims = {"unit_attack": self.load(self.clip("attack", 30, held)), "unit_idle": self.load(self.clip("idle", 30, held))}
        found, numbers = S.strike_findings(self.mesh, anims)
        self.assertEqual([(item["rule"], item["subject"]) for item in found], [("TRIPO-ATTACK-NO-STRIKE", "unit_attack")])
        self.assertIn("map_read", numbers["unit_attack"])
        self.assertIn("idle", numbers["unit_attack"]["map_read"])
        found, _numbers = S.strike_findings(self.mesh, {"unit_attack": self.load(self.clip("attack", 30, swing()))}, map_read_numbers=False)
        self.assertEqual(found, [])

    def test_tripo_checks_runs_it(self) -> None:
        self.clip("attack", 30, held)
        self.clip("idle", 30, held)
        json_path = self.folder / "checks.json"
        TC.main([str(self.folder), "--json", str(json_path)])
        import json

        report = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertIn("TRIPO-ATTACK-NO-STRIKE", [item["rule"] for item in report["findings"]])
        self.assertIn("strike", report["numbers"])


class Pick(unittest.TestCase):
    def row(self, verdict: str, reach: float, attack: bool = True) -> dict:
        return {"verdict": verdict, "attack": attack, "route": {"raise_": 0.0, "reach": reach, "pelvis_travel": 0.0}}

    def test_the_pick_is_the_largest_reach_among_the_attacks_that_pass(self) -> None:
        report = {"lunge": self.row("fail", 0.5), "box": self.row("pass", 0.36), "lurch": self.row("pass", 0.29), "walk": self.row("pass", 0.9, False)}
        self.assertEqual(pose_check.pick_attack(report), "box")

    def test_no_pick_under_the_floor(self) -> None:
        self.assertIsNone(pose_check.pick_attack({"box": self.row("pass", 0.1)}))


VANILLA_SHOOTING = ("attack_stand_rifle", "attack_stand_mg", "attack_crouch_rifle", "attack_crouch_mg", "charge_rifle_shoot", "charge_mg_shoot",
                    "charge_rifle", "charge_mg")


@unittest.skipUnless((UNITS / "GER_infantry.mesh").is_file(), "the game is not installed here")
class VanillaCalibration(unittest.TestCase):
    def test_vanillas_shooting_attacks_stay_under_both_limits(self) -> None:
        mesh = pdx_deform.load_mesh(UNITS / "GER_infantry.mesh")
        travel, speed = 0.0, 0.0
        for clip in VANILLA_SHOOTING:
            numbers = S.clip_strike(mesh, pdx_deform.load_anim(UNITS / f"GER_infantry_{clip}.anim"))
            travel = max(travel, *(hand["travel"] for hand in numbers["hands"].values()))
            speed = max(speed, *(hand["speed"] for hand in numbers["hands"].values()))
        self.assertAlmostEqual(travel, 0.252, delta=0.002)
        self.assertAlmostEqual(speed, 0.98, delta=0.01)
        self.assertLessEqual(travel, S.MIN_TRAVEL + 0.005)
        self.assertLess(speed, S.MIN_SPEED)


if __name__ == "__main__":
    unittest.main()
