"""The weapon bone's location keys cross every boundary from the job to the retarget (source contracts; the Blender side is
blender_weapon_location_integration.py)."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

PIPELINE_ROOT = Path(__file__).resolve().parents[1]


def function_arguments(path: Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return [argument.arg for argument in node.args.args + node.args.kwonlyargs]
    raise AssertionError(f"{name} not found in {path}")


class WeaponLocationContract(unittest.TestCase):
    def test_the_client_and_the_adapter_tool_take_the_bones_that_keep_their_location(self) -> None:
        self.assertIn("location_bones", function_arguments(PIPELINE_ROOT / "blender_client.py", "import_animation_action"))
        self.assertIn("location_bones", function_arguments(PIPELINE_ROOT / "adapter" / "hoi4_blender_mcp.py", "hoi4_blender_import_animation_action"))
        client = (PIPELINE_ROOT / "blender_client.py").read_text(encoding="utf-8")
        self.assertIn('"location_bones": location_bones', client)
        adapter = (PIPELINE_ROOT / "adapter" / "hoi4_blender_mcp.py").read_text(encoding="utf-8")
        self.assertIn('"location_bones": location_bones or []', adapter)

    def test_the_job_names_the_weapon_bone_for_the_roles_that_let_go_of_it(self) -> None:
        source = (PIPELINE_ROOT / "run_pilot.py").read_text(encoding="utf-8")
        self.assertIn('role in (released.get("release_roles") or [])', source)
        self.assertIn("location_bones=location_bones", source)

    def test_the_retarget_keeps_only_the_named_bones_location_and_zeroes_the_rest(self) -> None:
        worker = (PIPELINE_ROOT / "adapter" / "blender_worker.py").read_text(encoding="utf-8")
        self.assertIn('retarget_location_bones(payload.get("location_bones")', worker)
        self.assertIn("    if name in location_bones:", worker)
        self.assertIn("    return Vector((0.0, 0.0, 0.0))", worker)  # every other bone, as before
        self.assertIn("if name == root_name:", worker)  # the root keeps its own rule
        self.assertIn("name == root_name", worker)  # and is never a location bone


if __name__ == "__main__":
    unittest.main()
