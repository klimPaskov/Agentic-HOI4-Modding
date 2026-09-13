"""Read-only mesh-region contracts; native geometry proof is a separate fixture."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock

from test_reimport_promotion_contract import load_worker, PIPELINE_ROOT


class MeshRegionContracts(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.job = Path(temporary.name).resolve()
        (self.job / "proof.blend").write_bytes(b"not-a-native-blend-contract-fixture")
        self.ns, self.tree = load_worker()
        functions = [node for node in self.tree.body if isinstance(node, ast.FunctionDef) and (node.name.startswith("_mesh_region_") or node.name in {"inspect", "inspect_mesh_region"})]
        module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *functions], type_ignores=[])
        exec(compile(ast.fix_missing_locations(module), "mesh_region_contract", "exec"), self.ns)
        self.region = {"mesh_name": "Body", "bone_name": "Gun", "expected_source_sha256": hashlib.sha256((self.job / "proof.blend").read_bytes()).hexdigest().upper(),
                       "expected_action_sha256": "A" * 64, "aabb": {"space": "WORLD", "min": [-10, -10, -10], "max": [10, 10, 10]}}
        self.req = {"job_id": "fixture", "job_root": str(self.job), "payload": {"blend_rel": "proof.blend", "target_armature_name": "Rig", "action_name": "Action", "preview_frame": 6, "mesh_region": self.region}}

    def inputs(self):
        return self.ns["_mesh_region_inputs"](self.req)

    def test_exact_selector_and_default_bounded_page(self):
        result = self.inputs()
        self.assertEqual((result["offset"], result["limit"]), (0, 64))
        self.assertEqual(result["source"], self.job / "proof.blend")
        self.region["weight"] = {"bone_name": "Gun", "min": 0.75, "max": 1}
        self.assertEqual(self.inputs()["weight"]["min"], 0.75)
        del self.region["aabb"]
        self.assertIn("weight", self.inputs())

    def test_requires_selector_exact_names_frame_and_known_fields(self):
        for key, value in (("mesh_name", " Body"), ("bone_name", ""), ("bone_name", "Bad\x00Name"), ("code", "forbidden")):
            region = copy.deepcopy(self.region)
            self.region[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.inputs()
            self.region.clear()
            self.region.update(region)
        for frame in (-1, True, 1.5, 1000001):
            self.req["payload"]["preview_frame"] = frame
            with self.subTest(frame=frame), self.assertRaises(ValueError):
                self.inputs()
        self.req["payload"]["preview_frame"] = 6
        del self.region["aabb"]
        with self.assertRaisesRegex(ValueError, "selector"):
            self.inputs()

    def test_source_and_native_action_hash_fields_are_explicit(self):
        for key in ("expected_source_sha256", "expected_action_sha256"):
            original = self.region[key]
            for value in ("", None, True, "G" * 64):
                self.region[key] = value
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    self.inputs()
            self.region[key] = original
        self.region["expected_source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source SHA-256 mismatch"):
            self.inputs()

    def test_path_escape_wrong_suffix_and_absolute_paths_reject(self):
        for path in ("../outside.blend", "C:/outside.blend", "\\\\server\\outside.blend", "a/../proof.blend", "proof.fbx", str(self.job / "proof.blend")):
            self.req["payload"]["blend_rel"] = path
            with self.subTest(path=path), self.assertRaises((ValueError, FileNotFoundError)):
                self.inputs()

    def test_nonfinite_reversed_unbounded_or_unknown_aabb_reject(self):
        for box in ({"space": [], "min": [0] * 3, "max": [1] * 3}, {"space": "SCREEN", "min": [0] * 3, "max": [1] * 3}, {"space": "WORLD", "min": [2] * 3, "max": [1] * 3},
                    {"space": "WORLD", "min": [float("nan"), 0, 0], "max": [1] * 3}, {"space": "WORLD", "min": [0] * 3, "max": [float("inf"), 1, 1]},
                    {"space": "WORLD", "min": [-1000001, 0, 0], "max": [1] * 3}, {"space": "WORLD", "min": [0, 0], "max": [1] * 3}):
            self.region["aabb"] = box
            with self.subTest(box=box), self.assertRaises(ValueError):
                self.inputs()

    def test_weight_ranges_reject_nonfinite_bool_and_outside_unit_interval(self):
        for low, high in ((-0.1, 1), (0, 1.1), (0.9, 0.1), (True, 1), (float("nan"), 1)):
            self.region["weight"] = {"bone_name": "Gun", "min": low, "max": high}
            with self.subTest(low=low), self.assertRaises(ValueError):
                self.inputs()

    def test_pagination_caps_are_explicit(self):
        for key, values in (("limit", (0, 257, True, 1.5)), ("offset", (-1, 1000001, False, 0.5))):
            for value in values:
                self.region[key] = value
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    self.inputs()
            del self.region[key]

    def test_measurement_sets_must_be_bounded_unique_disjoint_indices(self):
        for origin, endpoint in (([], [1]), ([0, 0], [1]), ([0], [0]), ([True], [1]), ([-1], [1]), (list(range(65)), [100]), ([1000000], [1])):
            self.region["measurement"] = {"origin_vertex_indices": origin, "endpoint_vertex_indices": endpoint}
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                self.inputs()
        self.region["measurement"] = {"origin_vertex_indices": [0, 2], "endpoint_vertex_indices": [1, 3]}
        self.assertEqual(self.inputs()["measurement"], self.region["measurement"])

    def test_region_mode_forbids_preview_writers(self):
        for key, value in (("render_previews", True), ("runtime_stem", "preview"), ("preview_view_names", ["front"])):
            self.req["payload"][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "does not render"):
                self.inputs()
            del self.req["payload"][key]

    def test_native_action_hash_matches_existing_inspector_definition(self):
        key = types.SimpleNamespace(co=types.SimpleNamespace(x=6.0, y=0.2), interpolation="LINEAR")
        curve = types.SimpleNamespace(data_path='pose.bones["Gun"].location', array_index=0, keyframe_points=[key])
        self.ns["action_fcurves"] = lambda action: [(curve, object())]
        records = [{"slot": None, "data_path": curve.data_path, "array_index": 0, "keyframes": [[6.0, 0.2, "LINEAR"]]}]
        expected = hashlib.sha256(json.dumps(records, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()
        self.assertEqual(self.ns["_mesh_region_action_hash"](object()), expected)
        key.co.y = 0.3
        self.assertNotEqual(self.ns["_mesh_region_action_hash"](object()), expected)

    def test_uninspected_parent_and_data_animation_dependencies_reject(self):
        rig = types.SimpleNamespace(parent=None, data=types.SimpleNamespace(animation_data=None))
        mesh = types.SimpleNamespace(parent=None, parent_type="OBJECT", data=types.SimpleNamespace(animation_data=None))
        validate = self.ns["_mesh_region_object_dependencies"]
        validate(mesh, rig)
        mesh.parent = rig
        validate(mesh, rig)
        for target, field, value, message in ((rig, "parent", object(), "uninspected parent"),
                                              (mesh, "parent", object(), "uninspected parent"),
                                              (mesh, "parent_type", "BONE", "uninspected parent"),
                                              (mesh.data, "animation_data", object(), "animated mesh"),
                                              (rig.data, "animation_data", object(), "animated mesh")):
            old = getattr(target, field)
            setattr(target, field, value)
            with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, message):
                validate(mesh, rig)
            setattr(target, field, old)

    def test_topology_signature_rejects_index_reorder_but_not_deformation(self):
        mesh = types.SimpleNamespace(vertices=[types.SimpleNamespace(index=n, co=[n, 0, 0]) for n in range(3)],
                                     edges=[types.SimpleNamespace(index=0, vertices=[0, 1])],
                                     loops=[types.SimpleNamespace(index=0, vertex_index=0, edge_index=0)],
                                     polygons=[types.SimpleNamespace(index=0, loop_start=0, loop_total=1, vertices=[0], material_index=0)])
        before = self.ns["_mesh_region_topology"](mesh)
        mesh.vertices[0].co = [0.1, 0.2, 0.3]
        self.assertEqual(self.ns["_mesh_region_topology"](mesh), before)
        mesh.loops[0].vertex_index = 1
        self.assertNotEqual(self.ns["_mesh_region_topology"](mesh), before)

    def test_dispatch_is_readonly_region_mode_and_retains_legacy_default(self):
        self.ns["inspect_mesh_region"] = Mock(return_value={"mesh_region": {"read_only": True}})
        self.assertEqual(self.ns["inspect"](self.req), {"mesh_region": {"read_only": True}})
        function = next(node for node in self.tree.body if isinstance(node, ast.FunctionDef) and node.name == "inspect_mesh_region")
        calls = [ast.unparse(node.func) for node in ast.walk(function) if isinstance(node, ast.Call)]
        self.assertFalse(any("save" in name or "render" in name or "export" in name for name in calls))
        self.assertIn("evaluated_obj.to_mesh_clear", calls)
        self.assertIn("bpy.ops.wm.open_mainfile", calls)

    def test_mcp_and_client_forward_optional_dict_without_changing_legacy_payload(self):
        sources = ((PIPELINE_ROOT / "adapter/hoi4_blender_mcp.py", "hoi4_blender_inspect_scene"), (PIPELINE_ROOT / "blender_client.py", "inspect_scene"))
        for path, name in sources:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            function = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name)
            function = copy.deepcopy(function)
            function.decorator_list = []
            namespace = {"_run": Mock(return_value={})}
            module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), function], type_ignores=[])
            exec(compile(ast.fix_missing_locations(module), "schema_contract", "exec"), namespace)
            client = types.SimpleNamespace(call=Mock(return_value={}))
            args = {"job_id": "fixture", "blend_rel": "proof.blend", "mesh_region": self.region}
            if name == "inspect_scene":
                args["self"] = client
            namespace[name](**args)
            callback = client.call if name == "inspect_scene" else namespace["_run"]
            self.assertEqual(callback.call_args.args[-1]["mesh_region"], self.region)
            del args["mesh_region"]
            namespace[name](**args)
            self.assertNotIn("mesh_region", callback.call_args.args[-1])


if __name__ == "__main__":
    unittest.main()
