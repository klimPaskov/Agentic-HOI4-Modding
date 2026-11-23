"""The rider's seat checks match a mount clip keyed by its file stem to the rider's clip of the same role, and leave the death out
(lib/rider_fit.py). On 2026-11-23 the mount's clips came keyed by stem, so every one carried the rider's idle and the death was judged."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import rider_fit


class RoleKeys(unittest.TestCase):
    def test_a_stem_key_reads_its_role(self) -> None:
        self.assertEqual(rider_fit.role_of("zin_men_cavalry_horse_attack"), "attack")
        self.assertEqual(rider_fit.role_of("defend"), "defend")

    def test_the_death_is_not_judged_under_a_stem_key(self) -> None:
        report = rider_fit.SeatReport(rider_height=1.0, rest_gap=0.0, clips=[
            rider_fit.ClipSeat("zin_men_cavalry_horse_death", "death", 10, worst_sunk=0.5, worst_sunk_frame=3, worst_gap=0.5, worst_gap_frame=3),
            rider_fit.ClipSeat("zin_men_cavalry_horse_move", "move", 10, worst_sunk=0.5, worst_sunk_frame=3),
        ])
        findings, numbers = rider_fit.seat_findings(report)
        self.assertEqual({item["subject"] for item in findings}, {"zin_men_cavalry_horse_move"})
        self.assertIn("zin_men_cavalry_horse_death", numbers["clips"])


class ClipLength(unittest.TestCase):
    """A rider's attack and death end with the mount's (TRIPO-RIDER-CLIP-LENGTH): the zinnish lancer's death ran 17.8 s over the horse's 2 s."""

    def test_a_long_rider_death_or_attack_is_found(self) -> None:
        report = rider_fit.SeatReport(rider_height=1.0, rest_gap=0.0, clips=[
            rider_fit.ClipSeat("zin_men_cavalry_horse_death", "death", 60, mount_seconds=2.0, rider_seconds=17.77),
            rider_fit.ClipSeat("zin_men_cavalry_horse_attack", "attack", 60, mount_seconds=2.0, rider_seconds=2.0),
            rider_fit.ClipSeat("zin_men_cavalry_horse_idle", "idle", 91, mount_seconds=3.0, rider_seconds=17.77),
        ])
        findings, numbers = rider_fit.seat_findings(report)
        self.assertEqual([(item["rule"], item["subject"]) for item in findings], [("TRIPO-RIDER-CLIP-LENGTH", "zin_men_cavalry_horse_death")])
        self.assertEqual(numbers["clips"]["zin_men_cavalry_horse_death"]["rider_seconds"], 17.77)


if __name__ == "__main__":
    unittest.main()
