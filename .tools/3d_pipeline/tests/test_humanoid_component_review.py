"""Read-only component-review and action-channel inventory contracts."""

from __future__ import annotations

import ast
import copy
import hashlib
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock

from test_reimport_promotion_contract import PIPELINE_ROOT, load_worker


TOOL = "hoi4_blender_review_humanoid_components"


class HumanoidComponentReviewContracts(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.job = Path(temporary.name).resolve()
        self.source = self.job / "source.blend"
        self.source.write_bytes(b"contract-only-component-review-source")
        self.source_hash = hashlib.sha256(self.source.read_bytes()).hexdigest().upper()
        self.payload = {
            "blend_rel": "source.blend", "expected_source_sha256": self.source_hash,
            "mesh_name": "Exact Mesh", "render_group": True, "component_ids": [],
            "component_offset": 0, "component_limit": 16,
            "preview_view_names": ["front", "left", "right", "rear", "top", "three_quarter"],
        }
        self.req = {"request_id": "f" * 32, "job_id": "fixture", "job_root": str(self.job),
                    "operation": "review_humanoid_components", "payload": self.payload}
        self.ns, self.tree = load_worker()
        selected = {"_mesh_region_name", "_component_review_inputs", "_component_index_catalog",
                    "_action_channel_inventory_inputs", "_action_channel_rows", "inspect"}
        functions = [node for node in self.tree.body if isinstance(node, ast.FunctionDef) and node.name in selected]
        module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *functions], type_ignores=[])
        exec(compile(ast.fix_missing_locations(module), "component_review_contract", "exec"), self.ns)

    def inputs(self):
        return self.ns["_component_review_inputs"](self.req)

    def test_exact_bounded_contract_and_defaults(self):
        result = self.inputs()
        self.assertEqual(result["source"], self.source)
        self.assertEqual(result["component_limit"], 16)
        self.assertEqual(len(result["preview_view_names"]), 6)
        self.assertEqual(result["expected_source_sha256"], self.source_hash)

    def test_unknown_field_false_render_and_bad_source_identity_reject(self):
        for key, value in (("script", "forbidden"), ("render_group", False), ("expected_source_sha256", "G" * 64),
                           ("expected_source_sha256", "0" * 64), ("mesh_name", " Bad")):
            old = copy.deepcopy(self.payload)
            self.payload[key] = value
            with self.subTest(key=key), self.assertRaises((ValueError, FileNotFoundError)):
                self.inputs()
            self.payload.clear()
            self.payload.update(old)

    def test_path_escape_absolute_wrong_suffix_and_backslash_reject(self):
        for path in ("../source.blend", str(self.source), "folder\\source.blend", "source.fbx", "a/../source.blend"):
            self.payload["blend_rel"] = path
            with self.subTest(path=path), self.assertRaises((ValueError, FileNotFoundError)):
                self.inputs()
        self.payload["blend_rel"] = "source.blend"

    def test_component_id_pagination_and_view_validation(self):
        for key, value in (("component_ids", ["c_v1", "c_v1"]), ("component_ids", ["weapon"]),
                           ("component_ids", [f"c_v{value}" for value in range(17)]),
                           ("component_offset", -1), ("component_offset", 8193),
                           ("component_limit", 0), ("component_limit", 17),
                           ("preview_view_names", ["front", "front"]), ("preview_view_names", ["underside"]),
                           ("preview_view_names", {})):
            old = copy.deepcopy(self.payload)
            self.payload[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.inputs()
            self.payload.clear()
            self.payload.update(old)
        self.payload["component_ids"] = ["c_v12"]
        self.payload["component_offset"] = 1
        with self.assertRaisesRegex(ValueError, "pagination"):
            self.inputs()

    def test_adapter_request_id_is_exact_bounded_filename_identity(self):
        for value in ("request", "F" * 32, "f" * 31, "f" * 33, "../" + "f" * 32):
            self.req["request_id"] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "UUID request_id"):
                self.inputs()

    def test_source_index_connectivity_shared_vertices_and_isolates(self):
        catalog = self.ns["_component_index_catalog"](
            8,
            [(0, (0, 1)), (1, (1, 2)), (2, (3, 4)), (3, (6, 7))],
            [(0, (0, 1, 2)), (1, (3, 4, 5))],
        )
        self.assertEqual([row["component_id"] for row in catalog], ["c_v0", "c_v3", "c_v6"])
        self.assertEqual(catalog[0]["vertex_indices"], [0, 1, 2])
        self.assertEqual(catalog[1]["polygon_indices"], [1])
        self.assertEqual(catalog[2]["edge_indices"], [3])
        # A shared source vertex joins faces; separately indexed coincident positions never enter this graph.
        joined = self.ns["_component_index_catalog"](5, [], [(0, (0, 1, 2)), (1, (2, 3, 4))])
        self.assertEqual(len(joined), 1)

    def test_invalid_topology_and_vertex_caps_fail_closed(self):
        for vertices, edges, polygons in ((0, [], []), (250001, [], []), (3, [(0, (0, 3))], []),
                                          (3, [(0, (1, 1))], []), (3, [], [(0, (0, 1))]),
                                          (3, [], [(0, (0, 1, 4))])):
            with self.subTest(vertices=vertices, edges=edges, polygons=polygons), self.assertRaises(ValueError):
                self.ns["_component_index_catalog"](vertices, edges, polygons)

    def test_action_channel_inputs_are_hash_bound_and_exclusive(self):
        payload = {"blend_rel": "source.blend", "target_armature_name": "Rig", "action_name": "Attack",
                   "preview_frame": -1, "include_action_channels": True, "expected_source_sha256": self.source_hash,
                   "render_previews": False, "runtime_stem": "", "preview_view_names": []}
        req = {"job_root": str(self.job), "payload": payload}
        result = self.ns["_action_channel_inventory_inputs"](req)
        self.assertEqual((result["rig_name"], result["action_name"]), ("Rig", "Attack"))
        for key, value in (("include_action_channels", False), ("render_previews", True), ("runtime_stem", "writer"),
                           ("preview_frame", 0), ("mesh_region", {}), ("expected_source_sha256", "0" * 64)):
            old = copy.deepcopy(payload)
            payload[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.ns["_action_channel_inventory_inputs"](req)
            payload.clear()
            payload.update(old)

    def test_action_rows_preserve_exact_paths_groups_modes_and_duplicates(self):
        class Bone:
            def __init__(self, name, mode):
                self.name, self.rotation_mode = name, mode
            def path_from_id(self):
                return f'pose.bones["{self.name}"]'
        bone_euler, bone_quat = Bone("Euler", "XYZ"), Bone("Quat", "QUATERNION")
        rig = types.SimpleNamespace(rotation_mode="ZYX", pose=types.SimpleNamespace(bones=[bone_euler, bone_quat]))
        group = types.SimpleNamespace(name="Literal Group")
        curves = [
            types.SimpleNamespace(data_path='pose.bones["Euler"].rotation_euler', array_index=2, group=group),
            types.SimpleNamespace(data_path='pose.bones["Quat"].rotation_quaternion', array_index=0, group=None),
            types.SimpleNamespace(data_path='pose.bones["Quat"].scale', array_index=1, group=group),
            types.SimpleNamespace(data_path="location", array_index=0, group=None),
            types.SimpleNamespace(data_path='pose.bones["Euler"]["custom"]', array_index=0, group=None),
            types.SimpleNamespace(data_path="unresolved.property", array_index=3, group=None),
        ]
        curves.append(copy.copy(curves[0]))
        point = types.SimpleNamespace(co=[1.0, 0.2], interpolation="BEZIER", handle_left=[0.5, 0.1], handle_right=[1.5, 0.3], handle_left_type="AUTO", handle_right_type="AUTO")
        for curve in curves:
            curve.keyframe_points = [point]
            curve.extrapolation = "CONSTANT"
        self.ns["action_fcurves"] = lambda action: [(curve, object()) for curve in curves]
        rows = self.ns["_action_channel_rows"](object(), rig)
        self.assertEqual(len(rows), 7)
        self.assertEqual(sum(row["data_path"].endswith("rotation_euler") for row in rows), 2)
        self.assertEqual(next(row for row in rows if row["data_path"] == "location")["rotation_mode"], "ZYX")
        self.assertEqual(next(row for row in rows if row["data_path"] == "unresolved.property")["rotation_mode"], None)
        scale = next(row for row in rows if row["data_path"].endswith(".scale"))
        self.assertEqual((scale["group"], scale["rotation_mode"]), ("Literal Group", "QUATERNION"))
        self.assertEqual(scale["keyframes"][0]["co"], [1.0, 0.2])
        self.assertEqual(scale["extrapolation"], "CONSTANT")

    def test_action_row_caps_and_malformed_native_fields_reject(self):
        rig = types.SimpleNamespace(rotation_mode="XYZ", pose=types.SimpleNamespace(bones=[]))
        for curve in (types.SimpleNamespace(data_path="", array_index=0, group=None),
                      types.SimpleNamespace(data_path="location", array_index=-1, group=None),
                      types.SimpleNamespace(data_path="location", array_index=0, group=types.SimpleNamespace(name="x" * 129))):
            curve.keyframe_points = []
            curve.extrapolation = "CONSTANT"
            self.ns["action_fcurves"] = lambda action, value=curve: [(value, object())]
            with self.assertRaises(ValueError):
                self.ns["_action_channel_rows"](object(), rig)
        curve = types.SimpleNamespace(data_path="location", array_index=0, group=None)
        self.ns["action_fcurves"] = lambda action: [(curve, object())] * 4097
        with self.assertRaisesRegex(ValueError, "4096"):
            self.ns["_action_channel_rows"](object(), rig)

    def test_inspect_dispatch_keeps_legacy_default_and_modes_separate(self):
        self.ns["inspect_action_channels"] = Mock(return_value={"action_channels": {}})
        self.ns["inspect_mesh_region"] = Mock(return_value={"mesh_region": {}})
        req = {"payload": {"include_action_channels": True}}
        self.assertIn("action_channels", self.ns["inspect"](req))
        req = {"payload": {"mesh_region": {}}}
        self.assertIn("mesh_region", self.ns["inspect"](req))
        function = next(node for node in self.tree.body if isinstance(node, ast.FunctionDef) and node.name == "inspect")
        tests = [ast.unparse(node.test) for node in function.body if isinstance(node, ast.If)]
        self.assertIn("material_visibility", tests[0])
        self.assertTrue(any("include_action_channels" in test for test in tests))

    def test_exact_tool_and_client_forwarding_contract(self):
        tool_tree = ast.parse((PIPELINE_ROOT / "adapter/hoi4_blender_mcp.py").read_text(encoding="utf-8"))
        function = next(node for node in tool_tree.body if isinstance(node, ast.FunctionDef) and node.name == TOOL)
        fields = {arg.arg for arg in function.args.args}
        self.assertEqual(fields, {"job_id", *self.payload})
        self.assertIn("mcp.tool()", [ast.unparse(node) for node in function.decorator_list])
        self.assertFalse({"code", "python", "shell", "url", "output_rel"} & fields)
        client_tree = ast.parse((PIPELINE_ROOT / "blender_client.py").read_text(encoding="utf-8"))
        owner = next(node for node in client_tree.body if isinstance(node, ast.ClassDef) and node.name == "BlenderAdapterClient")
        client = next(node for node in owner.body if isinstance(node, ast.FunctionDef) and node.name == "review_humanoid_components")
        self.assertEqual({arg.arg for arg in client.args.args if arg.arg != "self"}, fields)
        inspect_tool = next(node for node in tool_tree.body if isinstance(node, ast.FunctionDef) and node.name == "hoi4_blender_inspect_scene")
        inspect_client = next(node for node in owner.body if isinstance(node, ast.FunctionDef) and node.name == "inspect_scene")
        for node in (inspect_tool, inspect_client):
            names = {arg.arg for arg in node.args.args}
            self.assertTrue({"include_action_channels", "expected_source_sha256"}.issubset(names))

        forwarded = Mock(return_value={})
        component_copy = copy.deepcopy(function)
        component_copy.decorator_list = []
        inspect_copy = copy.deepcopy(inspect_tool)
        inspect_copy.decorator_list = []
        module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), component_copy, inspect_copy], type_ignores=[])
        namespace = {"_run": forwarded}
        exec(compile(ast.fix_missing_locations(module), "mcp_forwarding", "exec"), namespace)
        namespace[TOOL]("fixture", "source.blend", "A" * 64, "Mesh")
        self.assertEqual(forwarded.call_args.args, ("fixture", "review_humanoid_components", {
            "blend_rel": "source.blend", "expected_source_sha256": "A" * 64, "mesh_name": "Mesh", "render_group": True,
            "component_ids": [], "component_offset": 0, "component_limit": 16, "preview_view_names": [],
        }))
        namespace["hoi4_blender_inspect_scene"]("fixture", "source.blend")
        self.assertNotIn("include_action_channels", forwarded.call_args.args[-1])
        namespace["hoi4_blender_inspect_scene"]("fixture", "source.blend", action_name="Attack", target_armature_name="Rig",
                                                        include_action_channels=True, expected_source_sha256="B" * 64)
        self.assertEqual(forwarded.call_args.args[-1]["include_action_channels"], True)
        self.assertEqual(forwarded.call_args.args[-1]["expected_source_sha256"], "B" * 64)

        methods = [copy.deepcopy(node) for node in owner.body if isinstance(node, ast.FunctionDef) and node.name in {"inspect_scene", "review_humanoid_components"}]
        holder = ast.ClassDef(name="Client", bases=[], keywords=[], decorator_list=[], body=methods)
        namespace = {}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), holder], type_ignores=[])), "client_forwarding", "exec"), namespace)
        instance = namespace["Client"]()
        instance.call = Mock(return_value={})
        instance.inspect_scene("fixture", "source.blend")
        self.assertNotIn("include_action_channels", instance.call.call_args.args[-1])
        instance.inspect_scene("fixture", "source.blend", action_name="Attack", target_armature_name="Rig",
                               include_action_channels=True, expected_source_sha256="C" * 64)
        self.assertEqual(instance.call.call_args.args[-1]["expected_source_sha256"], "C" * 64)
        instance.review_humanoid_components("fixture", "source.blend", "D" * 64, "Mesh", component_ids=["c_v3"])
        self.assertEqual(instance.call.call_args.args[-1]["component_ids"], ["c_v3"])

    def test_component_operation_is_read_only_and_bypasses_pdx_loader(self):
        function = next(node for node in self.tree.body if isinstance(node, ast.FunctionDef) and node.name == "review_humanoid_components")
        calls = {ast.unparse(node.func) for node in ast.walk(function) if isinstance(node, ast.Call)}
        self.assertFalse(any("save" in name or "export" in name or "import_" in name for name in calls))
        run = next(node for node in self.tree.body if isinstance(node, ast.FunctionDef) and node.name == "run")
        text = ast.unparse(run)
        self.assertIn("'review_humanoid_components'", text)
        self.assertIn("return review_humanoid_components(req)", text)

    def test_full_membership_report_uses_lossless_compact_json(self):
        function = next(node for node in self.tree.body if isinstance(node, ast.FunctionDef) and node.name == "review_humanoid_components")
        text = ast.unparse(function)
        self.assertIn("separators=(',', ':')", text)
        self.assertNotIn("indent=2", text)


if __name__ == "__main__":
    unittest.main()
