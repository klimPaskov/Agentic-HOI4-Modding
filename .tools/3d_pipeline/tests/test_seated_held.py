"""A seated rider's held weapon and clip length reach the seat step (run_pilot.seat_held, run_pilot.seat_seconds).

The zinnish lancer carries a 3 m demi-lance upright, couches it level in the attack and drops it in the death. Every one of its roles but
the defend reused Tripo's 17.8 s standing_relax, so the attack and the death are cut to the horse's 2 s clips.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import run_pilot

SPEC = {
    "target_height_m": 7.35,
    "tripo": {"weapon": {"part": "tripo_part_1", "bone": "Weapon", "source": "rigged", "release_roles": ["death"]}},
    "seat": {"scale": 0.65, "held": {"bone": "Weapon", "hand": "RightHand", "carry": [0.12, 0.05, 1.0], "couch": [1.0, -0.18, 0.0]}},
}


class SeatHeld(unittest.TestCase):
    def test_the_held_block_reaches_the_seat_step(self) -> None:
        held = run_pilot.seat_held(SPEC, "attack")
        self.assertEqual(held["bone"], "Weapon")
        self.assertEqual(held["couch"], [1.0, -0.18, 0.0])
        self.assertNotIn("drop", held)

    def test_a_release_role_without_a_measured_mount_has_no_drop(self) -> None:
        # no seat.folder: the node path cannot be measured, so the seat step keeps the weapon in hand
        self.assertNotIn("drop", run_pilot.seat_held(SPEC, "death"))

    def test_no_held_block_gives_nothing(self) -> None:
        self.assertIsNone(run_pilot.seat_held({"seat": {}}, "idle"))


class SeatSeconds(unittest.TestCase):
    PROFILES = {"rest": {}, "attack": {"seconds": 2.0}, "death": {"seconds": 2.0}, "idle": {"seconds": 3.03}}

    def test_the_attack_and_the_death_end_with_the_mount(self) -> None:
        self.assertEqual(run_pilot.seat_seconds(self.PROFILES, "attack"), 2.0)
        self.assertEqual(run_pilot.seat_seconds(self.PROFILES, "death"), 2.0)

    def test_a_looping_role_keeps_its_length(self) -> None:
        self.assertIsNone(run_pilot.seat_seconds(self.PROFILES, "idle"))
        self.assertIsNone(run_pilot.seat_seconds(None, "attack"))


if __name__ == "__main__":
    unittest.main()
