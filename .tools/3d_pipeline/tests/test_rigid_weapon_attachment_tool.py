"""Focused registration and contract tests for rigid checkpoint weapon attachment."""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PIPELINE_ROOT.parents[1]
if str(PIPELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(PIPELINE_ROOT))

from blender_client import BlenderAdapterClient  # noqa: E402


OPERATION = "attach_rigid_weapon_from_checkpoint"
TOOL = f"hoi4_blender_{OPERATION}"


class RigidWeaponAttachmentContractTests(unittest.TestCase):
    def test_bootstrap_discovers_the_versioned_operation(self) -> None:
        adapter_source = (PIPELINE_ROOT / "adapter" / "hoi4_blender_mcp.py").read_text(encoding="utf-8")
        bootstrap_source = (PIPELINE_ROOT / "bootstrap_3d_workflow.py").read_text(encoding="utf-8")
        self.assertIn(f"def {TOOL}(", adapter_source)
        self.assertIn("worker_operations = [name.removeprefix(\"hoi4_blender_\")", bootstrap_source)

    def test_mcp_wrapper_exposes_bounded_schema_inputs(self) -> None:
        source = (PIPELINE_ROOT / "adapter" / "hoi4_blender_mcp.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == TOOL)
        argument_names = {argument.arg for argument in function.args.args}
        required = {
            "job_id",
            "source_blend_rel",
            "target_blend_rel",
            "output_blend_rel",
            "source_object_name",
            "target_object_name",
            "target_armature_name",
            "parent_bone_name",
            "translation",
            "rotation_euler_degrees",
            "scale",
            "collision_policy",
            "action_name",
        }
        self.assertTrue(required.issubset(argument_names))
        self.assertFalse({"python", "code", "shell", "url", "absolute_path"} & argument_names)
        decorators = [ast.unparse(item) for item in function.decorator_list]
        self.assertIn("mcp.tool()", decorators)

    def test_worker_dispatches_without_animation_authoring(self) -> None:
        source = (PIPELINE_ROOT / "adapter" / "blender_worker.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == OPERATION)
        calls = {ast.unparse(node.func) for node in ast.walk(function) if isinstance(node, ast.Call)}
        self.assertNotIn("bpy.data.actions.new", calls)
        self.assertNotIn("keyframe_insert", {name.rsplit(".", 1)[-1] for name in calls})
        self.assertIn(f'if operation == "{OPERATION}":', source)

    def test_client_wrapper_forwards_the_explicit_contract(self) -> None:
        client = BlenderAdapterClient.__new__(BlenderAdapterClient)
        captured: dict[str, object] = {}

        def fake_call(tool: str, arguments: dict[str, object]) -> dict[str, object]:
            captured["tool"] = tool
            captured["arguments"] = arguments
            return {"status": "pass"}

        client.call = fake_call  # type: ignore[method-assign]
        result = client.attach_rigid_weapon_from_checkpoint(
            "test_humanoid",
            "blender/checkpoints/recovery_3d_weapon_assembled.blend",
            "blender/checkpoints/provider_rig.blend",
            "blender/checkpoints/provider_rig_with_weapon.blend",
            "test_rigid_weapon",
            "test_rigid_weapon",
            "Armature",
            "RightHand",
            create_weapon_bone_name="weapon",
            action_name="Armature|Idle|baselayer_WORKING",
        )
        self.assertEqual(result, {"status": "pass"})
        self.assertEqual(captured["tool"], TOOL)
        arguments = captured["arguments"]
        self.assertEqual(arguments["source_object_name"], "test_rigid_weapon")
        self.assertEqual(arguments["collision_policy"], "reject")
        self.assertEqual(arguments["translation"], [0.0, 0.0, 0.0])
        self.assertEqual(arguments["scale"], [1.0, 1.0, 1.0])


if __name__ == "__main__":
    unittest.main()
