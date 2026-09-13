"""Declarative existing-action patch contracts; no native or production acceptance."""

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


def fixture_payload(source_hash: str) -> dict:
    frames = [0, 2, 4, 6, 8, 10]
    return {
        "blend_rel": "checkpoints/source.blend", "checkpoint_rel": "checkpoints/patched.blend",
        "expected_source_sha256": source_hash, "expected_action_sha256": "A" * 64,
        "target_armature_name": "Rig", "source_action_name": "Source", "target_action_name": "Patched",
        "semantic_role": "attack", "source_fps": 30, "source_fps_base": 1.0,
        "frame_start": 0, "frame_end": 10,
        "phase_frames": {"ready": 0, "aim": 2, "discharge": 4, "recoil": 6, "recovery": 8},
        "allowed_bones": ["Arm"], "motion_bone_chain": [],
        "bone_patches": {"Arm": {"location": [{"frame": frame, "value": [0.1 * frame, 0.0, 0.0]} for frame in frames]}},
    }


class ActionPhaseContracts(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.job = Path(temporary.name).resolve()
        (self.job / "checkpoints").mkdir()
        self.source = self.job / "checkpoints/source.blend"
        self.source.write_bytes(b"contract-only-not-native")
        self.source_hash = hashlib.sha256(self.source.read_bytes()).hexdigest().upper()
        self.payload = fixture_payload(self.source_hash)
        self.req = {"job_id": "fixture", "job_root": str(self.job), "operation": "patch_existing_humanoid_action_phases", "payload": self.payload}
        self.ns, self.tree = load_worker()
        nodes = [node for node in self.tree.body if isinstance(node, ast.FunctionDef) and (node.name.startswith("_action_phase_") or node.name == "_mesh_region_name")]
        module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *nodes], type_ignores=[])
        exec(compile(ast.fix_missing_locations(module), "action_phase_contract", "exec"), self.ns)

    def inputs(self):
        return self.ns["_action_phase_inputs"](self.req)

    def test_exact_source_and_new_sibling(self):
        result = self.inputs()
        self.assertEqual(result["source"], self.source)
        self.assertEqual(result["output"], self.source.with_name("patched.blend"))
        self.assertEqual(self.source.read_bytes(), b"contract-only-not-native")

    def test_missing_unknown_and_wrong_hash_fields_reject(self):
        for key, value in (("script", "forbidden"), ("expected_source_sha256", "0" * 64), ("expected_action_sha256", "not a hash"), ("target_action_name", "Source")):
            old = copy.deepcopy(self.payload)
            self.payload[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.inputs()
            self.payload.clear()
            self.payload.update(old)
        del self.payload["source_fps"]
        with self.assertRaises(ValueError):
            self.inputs()

    def test_paths_escape_wrong_extension_nonsibling_overwrite_reject(self):
        for key, path in (("blend_rel", "../source.blend"), ("blend_rel", str(self.source)), ("checkpoint_rel", "elsewhere/patched.blend"), ("checkpoint_rel", "checkpoints/patched.fbx"), ("checkpoint_rel", "checkpoints/source.blend")):
            old = self.payload[key]
            self.payload[key] = path
            with self.subTest(key=key, path=path), self.assertRaises((ValueError, FileNotFoundError)):
                self.inputs()
            self.payload[key] = old
        self.source.with_name("patched.blend").write_bytes(b"retain collision")
        with self.assertRaisesRegex(ValueError, "exist|overwrite"):
            self.inputs()
        self.assertEqual(self.source.with_name("patched.blend").read_bytes(), b"retain collision")

    def test_role_phase_names_order_and_frame_bounds(self):
        for phases in ({"aim": 2}, {"ready": 0, "aim": 4, "discharge": 2, "recoil": 6, "recovery": 8},
                       {"ready": 0, "aim": 2, "discharge": 2, "recoil": 6, "recovery": 8},
                       {"ready": 0, "aim": 2, "discharge": 4, "recoil": 6, "recovery": 11}):
            self.payload["phase_frames"] = phases
            with self.subTest(phases=phases), self.assertRaises(ValueError):
                self.inputs()
        self.payload = fixture_payload(self.source_hash)
        self.req["payload"] = self.payload
        self.payload["semantic_role"] = "training"
        with self.assertRaises(ValueError):
            self.inputs()

    def test_defend_and_retreat_vocabulary(self):
        self.payload["semantic_role"] = "defend"
        self.payload["phase_frames"] = {"guard_start": 0, "guard_hold": 4, "guard_release": 8}
        self.inputs()
        self.payload["semantic_role"] = "retreat"
        self.payload["phase_frames"] = {"disengage": 0, "withdrawal": 4, "recovery": 8}
        with self.assertRaisesRegex(ValueError, "chain"):
            self.inputs()
        self.payload["allowed_bones"].append("Forearm")
        self.payload["bone_patches"]["Forearm"] = copy.deepcopy(self.payload["bone_patches"]["Arm"])
        self.payload["motion_bone_chain"] = ["Arm", "Forearm"]
        self.inputs()

    def test_bone_allowlist_duplicates_missing_patch_and_scale_reject(self):
        for bones in ([], ["Arm", "Arm"], ["Other"], [" Arm"]):
            old = self.payload["allowed_bones"]
            self.payload["allowed_bones"] = bones
            with self.subTest(bones=bones), self.assertRaises(ValueError):
                self.inputs()
            self.payload["allowed_bones"] = old
        self.payload["bone_patches"]["Arm"]["scale"] = [{"frame": 0, "value": [1, 1, 1]}]
        with self.assertRaises(ValueError):
            self.inputs()

    def test_keys_require_finite_values_unique_order_full_phase_and_endpoints(self):
        rows = self.payload["bone_patches"]["Arm"]["location"]
        malformed = [rows[:-1], rows[1:], [rows[0], rows[0], *rows[1:]], list(reversed(rows)),
                     [{"frame": 0, "value": [float("nan"), 0, 0]}, *rows[1:]],
                     [{"frame": -1, "value": [0, 0, 0]}, *rows[1:]],
                     [{"frame": True, "value": [0, 0, 0]}, *rows[1:]],
                     [{"frame": 0, "value": [0, 0]}, *rows[1:]]]
        for keys in malformed:
            self.payload["bone_patches"]["Arm"]["location"] = keys
            with self.subTest(keys=keys), self.assertRaises(ValueError):
                self.inputs()

    def test_quaternion_policy_rejects_nonunit_zero_and_nonfinite(self):
        frames = [row["frame"] for row in self.payload["bone_patches"]["Arm"]["location"]]
        for value in ([0, 0, 0, 0], [2, 0, 0, 0], [float("inf"), 0, 0, 0], [True, 0, 0, 0]):
            self.payload["bone_patches"]["Arm"] = {"rotation_quaternion": [{"frame": frame, "value": value} for frame in frames]}
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.inputs()
        self.payload["bone_patches"]["Arm"] = {"rotation_quaternion": [{"frame": frame, "value": [1, 0, 0, 0]} for frame in frames]}
        self.inputs()

    def test_native_fps_pair_is_explicit_not_retime(self):
        for key, values in (("source_fps", (0, True, 30.5, 1001)), ("source_fps_base", (0, float("nan"), float("inf"), True))):
            old = self.payload[key]
            for value in values:
                self.payload[key] = value
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    self.inputs()
            self.payload[key] = old

    def test_key_and_bone_caps_are_explicit(self):
        self.payload["bone_patches"]["Arm"]["location"] = [{"frame": frame, "value": [0, 0, 0]} for frame in range(513)]
        with self.assertRaises(ValueError):
            self.inputs()
        self.payload["allowed_bones"] = [f"Bone{index}" for index in range(65)]
        with self.assertRaises(ValueError):
            self.inputs()

    def test_motion_gate_rejects_identity_and_root_only_and_reports_nonsemantic_deltas(self):
        phases = list(self.payload["phase_frames"])
        context = {**self.payload, "allowed_bones": ["Root", "Arm"]}
        rig = types.SimpleNamespace(data=types.SimpleNamespace(bones={"Root": types.SimpleNamespace(parent=None), "Arm": types.SimpleNamespace(parent=object())}))
        matrix = [[float(row == column) for column in range(4)] for row in range(4)]
        source = {phase: {"bones": {bone: {"basis": copy.deepcopy(matrix)} for bone in context["allowed_bones"]}} for phase in phases}
        target = copy.deepcopy(source)
        evaluate = self.ns["_action_phase_motion"]
        with self.assertRaisesRegex(ValueError, "identity-only"):
            evaluate(context, rig, source, target)
        for index, phase in enumerate(phases):
            target[phase]["bones"]["Root"]["basis"][0][3] = index
        with self.assertRaisesRegex(ValueError, "non-root"):
            evaluate(context, rig, source, target)
        for index, phase in enumerate(phases):
            target[phase]["bones"]["Arm"]["basis"][0][3] = index
        report = evaluate(context, rig, source, target)
        self.assertFalse(report["semantic_acceptance"])
        self.assertEqual(set(report["phase_transitions"]), {"ready/aim", "discharge/recoil", "recoil/recovery"})

    def test_defend_hold_must_differ_from_source_not_only_other_phases(self):
        context = {**self.payload, "semantic_role": "defend", "allowed_bones": ["Arm"]}
        rig = types.SimpleNamespace(data=types.SimpleNamespace(bones={"Arm": types.SimpleNamespace(parent=object())}))
        matrix = [[float(row == column) for column in range(4)] for row in range(4)]
        source = {phase: {"bones": {"Arm": {"basis": copy.deepcopy(matrix)}}} for phase in ("guard_start", "guard_hold", "guard_release")}
        target = copy.deepcopy(source)
        target["guard_start"]["bones"]["Arm"]["basis"][0][3] = 1
        target["guard_release"]["bones"]["Arm"]["basis"][0][3] = 2
        with self.assertRaisesRegex(ValueError, "guard hold"):
            self.ns["_action_phase_motion"](context, rig, source, target)

    def test_mcp_and_client_forward_all_exact_payload_fields(self):
        sources = ((PIPELINE_ROOT / "adapter/hoi4_blender_mcp.py", "hoi4_blender_patch_existing_humanoid_action_phases"),
                   (PIPELINE_ROOT / "blender_client.py", "patch_existing_humanoid_action_phases"))
        for path, name in sources:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            function = copy.deepcopy(next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name))
            function.decorator_list = []
            namespace = {"_run": Mock(return_value={})}
            module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), function], type_ignores=[])
            exec(compile(ast.fix_missing_locations(module), "phase_schema", "exec"), namespace)
            client = types.SimpleNamespace(call=Mock(return_value={}))
            arguments = {"job_id": "fixture", **self.payload}
            if name == "patch_existing_humanoid_action_phases":
                arguments["self"] = client
            namespace[name](**arguments)
            callback = client.call if "self" in arguments else namespace["_run"]
            self.assertEqual(callback.call_args.args[-1], {"job_id": "fixture", **self.payload} if "self" in arguments else self.payload)


if __name__ == "__main__":
    unittest.main()
