"""The live authoring helpers: run their Blender test where a supported Blender is installed, and keep them helpers.

Live authoring under decisions 3D-3 and 3D-5 means the author chooses every pose. The helpers may
place, measure, render and key what the author names, but never generate keys, so only `key` may
insert a keyframe, and no helper loops over frames.
"""

from __future__ import annotations

import ast
import math
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


def pure_namespace() -> dict:
    """The helpers' numpy-only functions, compiled without Blender (the module itself imports bpy)."""

    import numpy as np

    sys.path.insert(0, str(PIPELINE))
    from lib import pdx_deform

    tree = ast.parse(HELPERS.read_text(encoding="utf-8"))
    wanted = {"_quaternion_flips", "_region_for_bone", "_welded_edges", "_stretch_edge_share"}
    module = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in wanted], type_ignores=[])
    namespace = {
        "np": np,
        "pdx_deform": pdx_deform,
        "STRETCH_RATIO": pdx_deform.STRETCH_RATIO,
        "SQUASH_RATIO": pdx_deform.SQUASH_RATIO,
        "SIGNIFICANT_SHARE": pdx_deform.SIGNIFICANT_SHARE,
        "Sequence": __import__("typing").Sequence,
        "List": list,
    }
    exec(compile(module, str(HELPERS), "exec"), namespace)
    return namespace


class PureHelperLogic(unittest.TestCase):
    def setUp(self) -> None:
        self.ns = pure_namespace()

    def test_stretch_constants_come_from_the_kit(self) -> None:
        tree = ast.parse(HELPERS.read_text(encoding="utf-8"))
        imported = {alias.name for node in tree.body if isinstance(node, ast.ImportFrom) and node.module == "lib.pdx_deform" for alias in node.names}
        self.assertEqual(imported, {"STRETCH_RATIO", "SQUASH_RATIO", "SIGNIFICANT_SHARE"})
        defined = {t.id for node in tree.body if isinstance(node, ast.Assign) for t in node.targets if isinstance(t, ast.Name)}
        self.assertFalse(defined & imported)

    def test_quaternions_flip_to_the_previous_keys_hemisphere(self) -> None:
        flips = self.ns["_quaternion_flips"]
        self.assertEqual(flips([(1, 0, 0, 0), (0.6, 0.8, 0, 0), (-0.5, -0.866, 0, 0)]), [False, False, True])
        # A run stays consistent: the third key is compared with the flipped second.
        self.assertEqual(flips([(1, 0, 0, 0), (-1, 0, 0, 0), (-1, 0, 0, 0), (1, 0, 0, 0)]), [False, True, True, False])
        self.assertEqual(flips([]), [])
        self.assertEqual(flips([(0, 1, 0, 0)]), [False])

    def test_bone_names_map_to_regions(self) -> None:
        region = self.ns["_region_for_bone"]
        cases = {
            "Head": "head", "Neck": "head", "Spine1": "chest", "Chest": "chest", "Hips": "hips", "LeftArm": "arms",
            "LeftForeArm": "arms", "RightShoulder": "arms", "LeftHand": "hands", "LeftHandIndex1": "hands",
            "LeftUpLeg": "legs", "LeftLeg": "legs", "LeftFoot": "feet", "RightToeBase": "feet", "Tail2": "tail",
            "WingArm_L": "wings", "Wing_A1": "wings", "weapon": "other",
        }
        for bone, expected in cases.items():
            self.assertEqual(region(bone), expected, bone)

    def test_stretch_share_matches_the_kits_rule(self) -> None:
        import numpy as np

        rest = np.array([[0, 0, 0], [0.1, 0, 0], [0.1, 0, 0.0], [0.2, 0, 0], [0.2, 0.1, 1.0]], dtype=float)
        # Vertex 2 sits where vertex 1 is (a split corner) and welds to it.
        raw = np.array([[0, 1], [2, 3], [1, 3], [3, 4]])
        edges = self.ns["_welded_edges"](rest, raw, 1.0)
        self.assertEqual(len(edges), 3)
        moved = rest.copy()
        self.assertEqual(self.ns["_stretch_edge_share"](rest, moved, edges, 1.0), 0.0)
        moved[3] = [0.5, 0, 0]  # edge 1-3 grows from 0.1 to 0.4 (ratio 4, change 0.3 of height)
        moved[4] = [0.5, 0.1, 1.0]
        self.assertAlmostEqual(self.ns["_stretch_edge_share"](rest, moved, edges, 1.0), 1 / 3)
        # A squashed edge counts too; a tiny change on a short edge does not.
        squashed = rest.copy()
        squashed[1] = [0.0, 0.0, 0.0]
        squashed[2] = [0.0, 0.0, 0.0]
        self.assertGreater(self.ns["_stretch_edge_share"](rest, squashed, edges, 1.0), 0.0)
        tiny = rest.copy()
        tiny[1] = [0.1 + 0.002, 0, 0]
        tiny[2] = tiny[1]
        self.assertEqual(self.ns["_stretch_edge_share"](rest, tiny, edges, 1.0), 0.0)
        self.assertTrue(math.isfinite(self.ns["_stretch_edge_share"](rest, moved, edges[:0], 1.0)))


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
