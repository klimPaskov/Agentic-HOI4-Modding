"""Native-depth parser fixture and strict hashed material-only partition regressions."""
from pathlib import Path
import copy
import ast
import hashlib
import importlib.util
import json
import tempfile
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("skeletal_export_partition", ROOT / "adapter" / "skeletal_export_partition.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
FIXTURE = Path(__file__).parent / "fixtures" / "skeletal_material_streams.txt"


class StreamTests(unittest.TestCase):
    def parse(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "stream.txt"
            path.write_text(text, encoding="utf-8")
            return MOD.exported_mesh_streams(path)

    def test_authentic_hierarchy_and_material_batches(self):
        streams = MOD.exported_mesh_streams(FIXTURE)
        self.assertEqual([(s["object_name"], s["mesh_index"], s["vertices"], s["triangle_indices"], s["maximum_index"]) for s in streams], [("char1.002", 0, 3, 3, 2), ("char1.002", 1, 3, 3, 2)])
        MOD.require_bounded_export_streams(streams)

    def test_skeleton_position_cannot_overwrite_mesh(self):
        text = FIXTURE.read_text().replace("                ix (int, 1): [23]", "                p (float, 3): [0, 0, 0]\n                ix (int, 1): [23]")
        self.assertEqual([s["vertices"] for s in self.parse(text)], [3, 3])

    def test_array_count_measured_not_trusted(self):
        for old, new in [("p (float, 9)", "p (float, 12)"), ("tri (int, 3)", "tri (int, 6)"), ("[1, 2, 0]", "[1, 3, 0]"), ("[1, 2, 0]", "[-1, 2, 0]")]:
            with self.subTest(new=new), self.assertRaises(RuntimeError):
                self.parse(FIXTURE.read_text().replace(old, new, 1))

    def test_duplicate_and_missing_stream_rejected(self):
        text = FIXTURE.read_text()
        for altered in [text.replace("            tri (int, 3):  [1, 2, 0]", ""), text.replace("            tri (int, 3):  [1, 2, 0]", "            tri (int, 3): [1, 2, 0]\n            tri (int, 3): [1, 2, 0]")]:
            with self.assertRaises(RuntimeError):
                self.parse(altered)

    def test_conservative_entry_budget_separate_from_max_index(self):
        with self.assertRaisesRegex(RuntimeError, "not an asserted engine"):
            MOD.require_bounded_export_streams([{"vertices": 38906, "triangle_indices": 90000, "maximum_index": 38905}])
        with self.assertRaises(RuntimeError):
            MOD.require_bounded_export_streams([{"vertices": 65536, "triangle_indices": 3}])
        MOD.require_bounded_export_streams([{"vertices": 65535, "triangle_indices": 65535}])

    def test_actual_large_arrays_not_header_only_fixture(self):
        text = "object:\n    native:\n        mesh:\n            p (float, 65538): " + json.dumps([0.0] * 65538) + "\n            tri (int, 65538): " + json.dumps(list(range(21846)) * 3) + "\nlocator:\n    muzzle:\n        p (float, 3): [0, 0, 0]\n"
        streams = self.parse(text)
        self.assertEqual((streams[0]["vertices"], streams[0]["triangle_indices"]), (21846, 65538))
        with self.assertRaises(RuntimeError):
            MOD.require_bounded_export_streams(streams)


class PartitionGuardTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.job = Path(temp.name)
        source = self.job / "source.blend"
        source.write_bytes(b"immutable-test-source")
        self.req = {"job_root": str(self.job), "payload": {"blend_rel": "source.blend", "expected_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "checkpoint_rel": "partition.blend", "target_armature_name": "rig", "target_mesh_names": ["body"], "max_export_vertices_per_batch": 24000}}
        def path(root, value, suffix, missing=False):
            result = (root / value).resolve()
            if not result.is_relative_to(root) or result.suffix != suffix or (not missing and not result.is_file()):
                raise ValueError("path")
            return result
        def name(value, field):
            if not isinstance(value, str) or not value or value != value.strip():
                raise ValueError(field)
            return value
        self.api = types.SimpleNamespace(_promotion_path=path, file_sha256=lambda p: hashlib.sha256(p.read_bytes()).hexdigest().upper(), _locator_exact_name=name)

    def test_source_and_sibling_guards(self):
        MOD._inputs(self.req, self.api)
        for key, value in [("expected_source_sha256", "0" * 64), ("checkpoint_rel", "other/new.blend"), ("checkpoint_rel", "source.blend"), ("target_mesh_names", ["body", "body"]), ("max_export_vertices_per_batch", 65536), ("max_export_vertices_per_batch", True)]:
            changed = copy.deepcopy(self.req)
            changed["payload"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                MOD._inputs(changed, self.api)
        changed = copy.deepcopy(self.req)
        changed["payload"]["arbitrary_python"] = "forbidden"
        with self.assertRaises(ValueError):
            MOD._inputs(changed, self.api)

    def test_material_equivalence_excludes_only_new_ids(self):
        base = {"settings": {"name": "source", "node_tree": {"name": "tree"}, "use_backface_culling": True}, "nodes": [{"image": "diffuse", "alpha": 1.0}], "links": [["A", "B"]]}
        duplicate = copy.deepcopy(base)
        duplicate["settings"].update(name="batch", node_tree={"name": "tree.001"})
        self.assertEqual(MOD._material_signature(base), MOD._material_signature(duplicate))
        for mutate in (lambda m: m["settings"].update(use_backface_culling=False), lambda m: m["nodes"][0].update(alpha=0.0), lambda m: m["links"].clear()):
            changed = copy.deepcopy(duplicate)
            mutate(changed)
            self.assertNotEqual(MOD._material_signature(base), MOD._material_signature(changed))

    def test_clone_normalization_preserves_original_retention_inventory(self):
        material = {"settings": {"name": "source", "node_tree": {"name": "tree"}}, "nodes": [], "links": []}
        clone = copy.deepcopy(material)
        clone["settings"]["name"] = "clone"
        original_inventory = {"discardable_orphan": False, "users": 2, "fake_user": True}
        result = {"sections": {"geometry": {}, "materials": {"source": material, "clone": clone}}, "material_retention": {"inventory": {"source": original_inventory, "clone": copy.deepcopy(original_inventory)}, "retained_sha256": "unused"}}
        digest = lambda value: hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
        api = types.SimpleNamespace(_promotion_fingerprint=lambda *a, **kw: copy.deepcopy(result), _promotion_digest=digest)
        with self.assertRaisesRegex(RuntimeError, "transaction ownership"):
            MOD._fingerprint(api, self.job, [], {"clone": "source"})


class PreviewBoundsTests(unittest.TestCase):
    def test_preview_uses_evaluated_pose_not_normalization_bounds(self):
        tree = ast.parse((ROOT / "adapter" / "blender_worker.py").read_text(encoding="utf-8"))
        render = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "render_previews")
        calls = [ast.unparse(n.func) for n in ast.walk(render) if isinstance(n, ast.Call)]
        self.assertIn("evaluated_world_bounds", calls)
        self.assertNotIn("world_bounds", calls)

    def test_evaluated_bounds_read_deformed_points_and_release_mesh(self):
        tree = ast.parse((ROOT / "adapter" / "blender_worker.py").read_text(encoding="utf-8"))
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "evaluated_world_bounds")
        class Vector:
            def __init__(self, row):
                self.x, self.y, self.z = row
        class Identity:
            def __matmul__(self, value):
                return value
        cleared = []
        mesh = types.SimpleNamespace(vertices=[types.SimpleNamespace(co=Vector(p)) for p in [(5, 6, 7), (8, 9, 10)]])
        evaluated = types.SimpleNamespace(matrix_world=Identity(), to_mesh=lambda: mesh, to_mesh_clear=lambda: cleared.append(True))
        obj = types.SimpleNamespace(type="MESH", evaluated_get=lambda dg: evaluated)
        api = types.SimpleNamespace(context=types.SimpleNamespace(evaluated_depsgraph_get=lambda: object()))
        namespace = {"Vector": Vector, "bpy": api}
        module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), fn], type_ignores=[])
        exec(compile(ast.fix_missing_locations(module), "evaluated_bounds_test", "exec"), namespace)
        low, high = namespace["evaluated_world_bounds"]([obj])
        self.assertEqual((low.x, low.y, low.z, high.x, high.y, high.z), (5, 6, 7, 8, 9, 10))
        self.assertEqual(cleared, [True])


if __name__ == "__main__":
    unittest.main()
