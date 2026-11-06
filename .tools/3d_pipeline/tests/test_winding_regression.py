"""Run the Blender winding regression where a supported Blender is installed; skip elsewhere (CI)."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

SCRIPT = PIPELINE / "tests" / "blender_winding_integration.py"


def blender() -> Path | None:
    explicit = os.environ.get("BLENDER_EXE", "").strip()
    if explicit:
        return Path(explicit)
    try:
        import bootstrap_3d_workflow as bootstrap

        executable, _shortcut, _version = bootstrap.select_supported_blender(
            bootstrap.discover_blender_installs(), bootstrap.supported_blender_minors()
        )
        return executable
    except Exception:  # noqa: BLE001 - no supported Blender here
        return None


BLENDER = blender()


@unittest.skipUnless(BLENDER and BLENDER.exists(), "no supported Blender installed")
class WeldedWinding(unittest.TestCase):
    def test_islands_split_at_uv_seams_are_wound_as_one_surface(self) -> None:
        completed = subprocess.run(
            [str(BLENDER), "--background", "--factory-startup", "--python-exit-code", "1", "--python", str(SCRIPT)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout[-3000:] + completed.stderr[-3000:])
        self.assertIn("WINDING_INTEGRATION_OK", completed.stdout)


if __name__ == "__main__":
    unittest.main()
