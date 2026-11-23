"""A seated rider's clips keep the seat step's pose: the runtime ground pass and the standing death passes skip it (run_pilot.seated_ground_skip)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import run_pilot


class SeatedGroundSkip(unittest.TestCase):
    def test_the_rider_types_skip_the_ground_pass(self) -> None:
        types = run_pilot.load_unit_types()
        seated = [name for name, unit in types.items() if unit.get("seated")]
        self.assertIn("rider", seated)
        for name in seated:
            self.assertTrue(run_pilot.seated_ground_skip(types[name])["skipped"])

    def test_a_standing_or_missing_type_is_grounded(self) -> None:
        types = run_pilot.load_unit_types()
        for name, unit in types.items():
            if not unit.get("seated"):
                self.assertIsNone(run_pilot.seated_ground_skip(unit), name)
        self.assertIsNone(run_pilot.seated_ground_skip(None))


if __name__ == "__main__":
    unittest.main()
