"""Pure guard contracts for the unsaved visibility probe (native proof is separate)."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest


MODULE = Path(__file__).resolve().parents[1] / "adapter" / "material_visibility_probe.py"
SPEC = importlib.util.spec_from_file_location("material_visibility_probe", MODULE)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class MaterialVisibilityGuards(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.job = Path(directory.name)
        (self.job / "source.blend").write_bytes(b"contract fixture only")
        self.payload = {"blend_rel": "source.blend", "expected_source_sha256": hashlib.sha256(b"contract fixture only").hexdigest().upper(), "preview_frame": 24, "runtime_stem": "visibility_proof", "preview_view_names": ["front", "three_quarter"], "render_previews": True, "material_visibility": {"target_mesh_names": ["char1.002"]}}
        self.req = {"job_root": str(self.job), "payload": self.payload}

    def test_valid_exact_static_selection(self):
        result = probe.validate_visibility_request(self.req)
        self.assertEqual(result["source"], self.job / "source.blend")
        self.assertEqual(result["mesh_names"], ["char1.002"])

    def test_source_hash_is_required_and_measured(self):
        for value in (None, "", "0" * 64, "G" * 64, True):
            self.payload["expected_source_sha256"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                probe.validate_visibility_request(self.req)

    def test_path_traversal_absolute_and_wrong_suffix_reject(self):
        for value in ("../source.blend", "C:/outside.blend", "\\\\server\\share\\source.blend", "a/../source.blend", "/outside.blend", "C:source.blend", "source.fbx"):
            self.payload["blend_rel"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                probe.validate_visibility_request(self.req)

    def test_exact_names_bounded_views_frames_and_stem(self):
        for key, values in (("preview_frame", (None, True, -1, 1.5, 1000001)), ("runtime_stem", ("../file", "", " space ")), ("preview_view_names", ([], ["side"], ["front", "front"], list(probe.VIEWS)))):
            old = self.payload[key]
            for value in values:
                self.payload[key] = value
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    probe.validate_visibility_request(self.req)
            self.payload[key] = old
        for names in ([], ["a"] * 2, [" body"], ["a\x00b"], [str(n) for n in range(33)]):
            self.payload["material_visibility"]["target_mesh_names"] = names
            with self.subTest(names=names), self.assertRaises(ValueError):
                probe.validate_visibility_request(self.req)

    def test_action_requires_exact_rig_and_hash(self):
        self.payload["action_name"] = "io_pdx_rigAction"
        with self.assertRaises(ValueError):
            probe.validate_visibility_request(self.req)
        self.payload["target_armature_name"] = "io_pdx_rig"
        with self.assertRaises(ValueError):
            probe.validate_visibility_request(self.req)
        self.payload["material_visibility"]["expected_action_sha256"] = "A" * 64
        self.assertEqual(probe.validate_visibility_request(self.req)["action_sha256"], "A" * 64)

    def test_modes_are_exclusive_and_probe_fields_closed(self):
        for key, value in (("mesh_region", {}), ("include_action_channels", False), ("render_previews", False)):
            self.payload[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                probe.validate_visibility_request(self.req)
            del self.payload[key]
        self.payload["render_previews"] = True
        self.payload["material_visibility"]["python"] = "forbidden"
        with self.assertRaises(ValueError):
            probe.validate_visibility_request(self.req)

    def test_native_routine_reloads_in_finally_and_never_saves(self):
        tree = ast.parse(MODULE.read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "run_material_visibility_probe")
        calls = [ast.unparse(node.func) for node in ast.walk(function) if isinstance(node, ast.Call)]
        self.assertFalse(any("save" in name or "export" in name for name in calls))
        guard = next(node for node in function.body if isinstance(node, ast.Try))
        cleanup_calls = [ast.unparse(node.func) for statement in guard.finalbody for node in ast.walk(statement) if isinstance(node, ast.Call)]
        self.assertIn("bpy.ops.wm.open_mainfile", cleanup_calls)
        self.assertIn("_sha", cleanup_calls)


if __name__ == "__main__":
    unittest.main()
