"""Provider-free contracts for reusable Blender adapter advances."""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
if str(PIPELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(PIPELINE_ROOT))

from blender_client import BlenderAdapterClient  # noqa: E402


class ReusableAdapterAdvanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.worker = (PIPELINE_ROOT / "adapter" / "blender_worker.py").read_text(encoding="utf-8")
        cls.mcp = (PIPELINE_ROOT / "adapter" / "hoi4_blender_mcp.py").read_text(encoding="utf-8")
        cls.worker_tree = ast.parse(cls.worker)
        cls.mcp_tree = ast.parse(cls.mcp)

    def test_all_new_operations_are_bounded_and_dispatched(self) -> None:
        for operation in ("import_bvh_animation_action", "prepare_export_coordinate_checkpoint"):
            tool = f"hoi4_blender_{operation}"
            function = next(
                node for node in self.mcp_tree.body
                if isinstance(node, ast.FunctionDef) and node.name == tool
            )
            self.assertIn("mcp.tool()", [ast.unparse(item) for item in function.decorator_list])
            arguments = {item.arg for item in function.args.args}
            self.assertFalse({"python", "code", "shell", "url", "absolute_path"} & arguments)
            self.assertIn(f'if operation == "{operation}":', self.worker)

    def test_dual_source_selection_and_reset_fail_closed(self) -> None:
        required = (
            "dual_source_base_rig requires geometry_source_rel",
            "geometry_object_name requires geometry_source_rel",
            "exactly one explicitly selected geometry MESH",
            "selected_geometry.library is not None",
            "target_armature.animation_data_clear()",
            "pose_bone.matrix_basis = Matrix.Identity(4)",
            'obj["hoi4_working"] = False',
            "base_weight_sanitization = sanitize_working_weights()",
        )
        for text in required:
            self.assertIn(text, self.worker)

    def test_weight_transfer_and_grounding_contracts_are_explicit(self) -> None:
        for text in (
            '"nearest_face_interpolated"',
            "BVHTree.FromPolygons",
            "barycentric_tolerance",
            "max_influences_per_vertex must be an integer from 1 through 4",
            "evaluated_contact_bounds(meshes, excluded_contact_bones)",
            '"contact_selection_policy": "exclude_vertices_dominated_by_named_bones"',
        ):
            self.assertIn(text, self.worker)

    def test_bvh_import_retains_verified_external_source_lineage(self) -> None:
        for text in (
            "inspect_bvh_header(source)",
            "bpy.ops.import_anim.bvh",
            "source_action_name must exactly match the verified BVH filename stem",
            '"hoi4_animation_source_format": "bvh"',
            "action_curve_signature(reopened_action)",
            "manual_or_procedural_replacement_authored",
        ):
            self.assertIn(text, self.worker)

    def test_export_checkpoint_has_pre_and_post_save_drift_guards(self) -> None:
        for text in (
            "_validate_export_coordinate_drift(",
            '"drift_guard_before_save": drift',
            '"drift_guard_after_reopen": reopened_drift',
            "protected source/reference drift",
            "material/image binding drift",
            "action_provenance(reopened_action)",
        ):
            self.assertIn(text, self.worker)

    def test_client_forwards_reusable_contracts(self) -> None:
        client = BlenderAdapterClient.__new__(BlenderAdapterClient)
        calls: list[tuple[str, dict[str, object]]] = []
        client.call = lambda tool, arguments: calls.append((tool, arguments)) or {"status": "pass"}  # type: ignore[method-assign]
        client.prepare_candidate(
            "unit", source_rel="rig.fbx", asset_kind="humanoid_unit", target_height_m=8.0,
            runtime_stem="unit", geometry_source_rel="geometry.blend",
            geometry_object_name="ApprovedGeometry", dual_source_base_rig=True,
            geometry_weight_mode="nearest_face_interpolated", source_armature_name="Rig",
            source_mesh_names=["Body", "Equipment"],
        )
        client.correct_action_grounding(
            "unit", "action.blend", "grounded.blend", "Move Action",
            excluded_contact_bones=["Tail1", "Tail2"],
        )
        client.sanitize_runtime_candidate(
            "unit", "grounded.blend", weight_only=True, max_influences_per_vertex=2,
        )
        self.assertEqual(calls[0][1]["geometry_object_name"], "ApprovedGeometry")
        self.assertEqual(calls[0][1]["source_mesh_names"], ["Body", "Equipment"])
        self.assertEqual(calls[1][1]["excluded_contact_bones"], ["Tail1", "Tail2"])
        self.assertTrue(calls[2][1]["weight_only"])
        self.assertEqual(calls[2][1]["max_influences_per_vertex"], 2)


if __name__ == "__main__":
    unittest.main()
