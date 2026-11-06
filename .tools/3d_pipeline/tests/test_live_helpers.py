"""The live authoring helpers: run their Blender test where a supported Blender is installed, and keep them helpers.

Live authoring under decisions 3D-3 and 3D-5 means the author chooses every pose. The helpers may
place, measure, render and key what the author names, but never generate keys, so only `key` may
insert a keyframe, and no helper loops over frames.
"""

from __future__ import annotations

import ast
import subprocess
import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE / "tests"))

from test_winding_regression import BLENDER

HELPERS = PIPELINE / "authoring" / "live_helpers.py"
SCRIPT = PIPELINE / "tests" / "blender_live_helpers_integration.py"
GUIDE = PIPELINE.parents[1] / ".claude" / "skills" / "hoi4-3d-model-pipeline" / "references" / "live-authoring.md"


class HelpersStayHelpers(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = ast.parse(HELPERS.read_text(encoding="utf-8"))
        self.functions = {node.name: node for node in self.tree.body if isinstance(node, ast.FunctionDef)}

    def test_only_key_inserts_keyframes(self) -> None:
        inserting = {
            name
            for name, node in self.functions.items()
            if any(isinstance(call, ast.Attribute) and call.attr == "keyframe_insert" for call in ast.walk(node))
        }
        self.assertEqual(inserting, {"key"})

    def test_no_helper_keys_inside_a_loop_over_frames(self) -> None:
        # Rendering a strip of frames is fine; keying one is generating motion.
        for name, node in self.functions.items():
            for loop in (item for item in ast.walk(node) if isinstance(item, ast.For)):
                if "frame" not in ast.unparse(loop.target):
                    continue
                calls = {ast.unparse(call.func) for call in ast.walk(loop) if isinstance(call, ast.Call)}
                self.assertFalse(calls & {"key", "plant", "seat_grip"} or any("keyframe" in call for call in calls), f"{name} keys inside a loop over frames")

    def test_every_helper_the_guide_names_exists(self) -> None:
        guide = GUIDE.read_text(encoding="utf-8")
        named = {word.split("(")[0][2:] for word in guide.replace("`", " ").split() if word.startswith("h.")}
        self.assertTrue(named)
        self.assertEqual(sorted(named - set(self.functions)), [])


@unittest.skipUnless(BLENDER and BLENDER.exists(), "no supported Blender installed")
class HelpersInBlender(unittest.TestCase):
    def test_pose_plant_weight_and_grip_on_a_small_unit(self) -> None:
        completed = subprocess.run(
            [str(BLENDER), "--background", "--factory-startup", "--python-exit-code", "1", "--python", str(SCRIPT)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout[-3000:] + completed.stderr[-3000:])
        self.assertIn("LIVE_HELPERS_INTEGRATION_OK", completed.stdout)


if __name__ == "__main__":
    unittest.main()
