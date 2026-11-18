"""Run the static route's surface cleanup and shading rule in Blender (tests/blender_static_cleanup_integration.py) where a supported
Blender is installed; skip elsewhere (CI)."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

from test_winding_regression import BLENDER

SCRIPT = PIPELINE / "tests" / "blender_static_cleanup_integration.py"


@unittest.skipUnless(BLENDER and BLENDER.exists(), "no supported Blender installed")
class StaticCleanup(unittest.TestCase):
    def test_slivers_go_cards_get_a_thickness_and_shading_keeps_its_creases(self) -> None:
        completed = subprocess.run(
            [str(BLENDER), "--background", "--factory-startup", "--python-exit-code", "1", "--python", str(SCRIPT)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout[-3000:] + completed.stderr[-3000:])
        self.assertIn("STATIC_CLEANUP_INTEGRATION_OK", completed.stdout)


if __name__ == "__main__":
    unittest.main()
