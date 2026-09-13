"""Locator validation/control-flow contracts, with no Blender or live export.

The worker functions are AST-loaded against a minimal in-memory test double.
These tests do not certify Blender parenting, deformation, or PDX round-trips.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
import os
import re
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
WORKER_PATH = PIPELINE_ROOT / "adapter" / "blender_worker.py"
ADAPTER_PATH = PIPELINE_ROOT / "adapter" / "hoi4_blender_mcp.py"


class VectorDouble(list):
    def __imul__(self, value):
        self[:] = [item * value for item in self]
        return self


class MatrixDouble:
    """Diagonal-scale/translation double; never Blender acceptance proof."""

    def __init__(self, rows=None):
        self.rows = rows or [[float(i == j) for j in range(4)] for i in range(4)]

    @classmethod
    def Identity(cls, size):
        assert size == 4
        return cls()

    @classmethod
    def Translation(cls, xyz):
        result = cls()
        for i, value in enumerate(xyz):
            result.rows[i][3] = value
        return result

    def __iter__(self):
        return iter(self.rows)

    def __getitem__(self, index):
        return self.rows[index]

    def __matmul__(self, other):
        return MatrixDouble([[sum(self[i][k] * other[k][j] for k in range(4)) for j in range(4)] for i in range(4)])

    def determinant(self):
        return math.prod(self[i][i] for i in range(4))

    def inverted(self):
        result = MatrixDouble()
        for i in range(3):
            result.rows[i][i] = 1.0 / self[i][i]
            result.rows[i][3] = -self[i][3] / self[i][i]
        return result

    def to_scale(self):
        return [abs(self[i][i]) for i in range(3)]

    @property
    def translation(self):
        return VectorDouble(self[i][3] for i in range(3))

    @translation.setter
    def translation(self, values):
        for i, value in enumerate(values):
            self.rows[i][3] = value

    def to_4x4(self):
        return self


class Objects(list):
    def get(self, name):
        return next((obj for obj in self if obj.name == name), None)

    def __contains__(self, item):
        return self.get(item) is not None if isinstance(item, str) else super().__contains__(item)

    def __getitem__(self, item):
        return self.get(item) if isinstance(item, str) else super().__getitem__(item)

    def new(self, name, data):
        obj = ObjectDouble(name, "EMPTY", data=data)
        self.append(obj)
        return obj

    def link(self, obj):
        if obj not in self:
            self.append(obj)


class ObjectDouble:
    def __init__(self, name, kind, *, data=None, parent=None, parent_bone="", props=None):
        self.name, self.type, self.data = name, kind, data
        self.parent, self.parent_bone = parent, parent_bone
        self.parent_type = "BONE" if parent else "OBJECT"
        self.library = self.override_library = self.animation_data = None
        self.constraints, self.modifiers, self.children = [], [], []
        self.instance_type = "NONE"
        self.matrix_world = MatrixDouble()
        self.matrix_basis = MatrixDouble()
        self.matrix_parent_inverse = MatrixDouble()
        self.props = props or {}
        self.selected = False

    def get(self, key, default=None):
        return self.props.get(key, default)

    def __setitem__(self, key, value):
        self.props[key] = value

    def select_set(self, selected):
        self.selected = selected


class ContextDouble:
    def __init__(self, objects):
        self.scene = types.SimpleNamespace(objects=objects, frame_current=145, collection=types.SimpleNamespace(objects=objects))
        self.view_layer = types.SimpleNamespace(objects=types.SimpleNamespace(active=None), update=Mock())

    @property
    def selected_objects(self):
        return [obj for obj in self.scene.objects if obj.selected]


class RnaWrapperDouble:
    """Distinct Python wrapper with Blender-style underlying data equality."""

    def __init__(self, target):
        self.target = target

    def __getattr__(self, name):
        return getattr(self.target, name)

    def __eq__(self, other):
        return self.target is (other.target if isinstance(other, RnaWrapperDouble) else other)

    def __hash__(self):
        return hash(self.target)


class RnaLookupObjects(Objects):
    def get(self, name):
        target = super().get(name)
        return RnaWrapperDouble(target) if target is not None else None

    def __getitem__(self, item):
        target = super().__getitem__(item)
        return target if isinstance(target, RnaWrapperDouble) else RnaWrapperDouble(target)


def load_worker():
    source = WORKER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {
        "within", "safe_name", "armatures", "_locator_exact_name", "_locator_numbers",
        "_locator_request", "_locator_registration", "_locator_matrix_record",
        "_locator_bone_world", "_locator_parent", "_validate_registered_locator",
        "locator_records", "author_locator", "approved_export_locators", "export_mesh", "run",
    }
    nodes = [ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)]
    nodes += [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    module = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    namespace = {
        "Path": Path, "math": math, "os": os, "re": re, "hashlib": hashlib, "json": json,
        "Matrix": MatrixDouble, "LOCATOR_REGISTRY_VERSION": 1, "LOCATOR_TRANSFORM_TOLERANCE": 1e-5,
    }
    exec(compile(module, str(WORKER_PATH), "exec"), namespace)
    return namespace, tree


class LocatorAdapterContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.job = Path(self.tmp.name).resolve()
        self.checkpoints = self.job / "blender" / "checkpoints"
        self.checkpoints.mkdir(parents=True)
        self.source = self.checkpoints / "accepted.blend"
        self.source.write_bytes(b"fixture-not-a-blend")
        self.req = {
            "job_id": "test_unit", "job_root": str(self.job), "operation": "author_locator",
            "io_pdx_root": "not-invoked",
            "payload": {
                "blend_rel": "blender/checkpoints/accepted.blend",
                "checkpoint_rel": "blender/checkpoints/with_muzzle.blend",
                "target_armature_name": "Accepted Rig", "parent_bone": "Gun Bone",
                "locator_name": "muzzle", "bone_local_position": [0.1, 0.2, 0.3],
                "bone_local_rotation_xyzw": [0.0, 0.0, 0.0, 1.0],
            },
        }
        self.ns, self.tree = load_worker()
        self.bone = ObjectDouble("Gun Bone", "BONE")
        self.bone.matrix_local = MatrixDouble()
        self.bone.matrix = MatrixDouble()
        self.rig = ObjectDouble("Accepted Rig", "ARMATURE", props={"hoi4_working": True})
        self.rig.data = types.SimpleNamespace(bones=Objects([self.bone]), library=None, pose_position="POSE")
        self.rig.pose = types.SimpleNamespace(bones=Objects([self.bone]))
        self.mesh = ObjectDouble("Body", "MESH", props={"hoi4_working": True})
        self.mesh.modifiers = [types.SimpleNamespace(type="ARMATURE", object=self.rig)]
        self.objects = Objects([self.rig, self.mesh])
        self.bpy = types.SimpleNamespace(
            data=types.SimpleNamespace(objects=self.objects, actions=[], user_map=Mock(return_value={})), context=ContextDouble(self.objects),
            types=types.SimpleNamespace(Scene=ContextDouble, Collection=Objects),
            ops=types.SimpleNamespace(wm=types.SimpleNamespace(open_mainfile=Mock(), save_as_mainfile=Mock()),
                                      object=types.SimpleNamespace(select_all=Mock(side_effect=lambda **_: [obj.select_set(False) for obj in self.objects]))),
        )
        self.ns["bpy"] = self.bpy
        def save_copy(**kwargs):
            Path(kwargs["filepath"]).write_bytes(b"fixture-not-a-blend-copy")
            return {"FINISHED"}
        self.bpy.ops.wm.save_as_mainfile.side_effect = save_copy
        self.ns["Quaternion"] = Mock(return_value=types.SimpleNamespace(to_matrix=lambda: MatrixDouble()))
        self.ns["_export_checkpoint_action_snapshot"] = Mock(return_value=[])

    def registered(self, name="muzzle", rig=None, bone_name="Gun Bone", job_id="test_unit"):
        rig = rig or self.rig
        props = self.ns["_locator_registration"](self.job, job_id, name, rig.name, bone_name)
        obj = ObjectDouble(name, "EMPTY", parent=rig, parent_bone=bone_name, props=props)
        self.objects.append(obj)
        return obj

    def test_exact_tool_schema_and_allowlist_registration(self):
        tree = ast.parse(ADAPTER_PATH.read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "hoi4_blender_author_locator")
        fields = {arg.arg for arg in function.args.args}
        self.assertEqual(fields, {"job_id", *self.req["payload"]})
        self.assertEqual(ast.unparse(function.args.args[-1].annotation), "tuple[float, float, float, float]")
        self.assertIn("mcp.tool()", [ast.unparse(node) for node in function.decorator_list])
        registered = [node.name.removeprefix("hoi4_blender_") for node in tree.body if isinstance(node, ast.FunctionDef) and node.name.startswith("hoi4_blender_")]
        self.assertEqual(registered.count("author_locator"), 1)
        bootstrap = (PIPELINE_ROOT / "bootstrap_3d_workflow.py").read_text(encoding="utf-8")
        self.assertIn('"operations": worker_operations', bootstrap)
        self.assertFalse({"python", "code", "shell", "url", "absolute_path"} & fields)

    def test_request_accepts_exact_measured_contract(self):
        result = self.ns["_locator_request"](self.req)
        self.assertEqual(result[1], self.source)
        self.assertEqual(result[-2:], ([0.1, 0.2, 0.3], [0.0, 0.0, 0.0, 1.0]))

    def test_client_forwards_exact_measured_contract(self):
        path = PIPELINE_ROOT / "blender_client.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        client = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "BlenderAdapterClient")
        method = next(node for node in client.body if isinstance(node, ast.FunctionDef) and node.name == "author_locator")
        self.assertEqual({arg.arg for arg in method.args.args}, {"self", "job_id", *self.req["payload"]})
        module = ast.fix_missing_locations(ast.Module(body=[
            ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), method,
        ], type_ignores=[]))
        namespace = {}
        exec(compile(module, str(path), "exec"), namespace)
        receiver = types.SimpleNamespace(call=Mock(return_value={"forwarded": True}))
        values = {"job_id": "test_unit", **self.req["payload"]}
        values["bone_local_position"] = tuple(values["bone_local_position"])
        values["bone_local_rotation_xyzw"] = tuple(values["bone_local_rotation_xyzw"])
        self.assertEqual(namespace["author_locator"](receiver, **values), {"forwarded": True})
        receiver.call.assert_called_once_with("hoi4_blender_author_locator", {"job_id": "test_unit", **self.req["payload"]})

    def test_codex_runtime_exposes_exact_locator_tool(self):
        # This general package is dormant until reviewed bootstrap, unlike the source mod.
        bootstrap = (PIPELINE_ROOT / "bootstrap_3d_workflow.py").read_text(encoding="utf-8")
        self.assertIn("[mcp_servers.blender_hoi4]", bootstrap)
        self.assertIn('"worker_operations": worker_operations', bootstrap)
        wrapper = (PIPELINE_ROOT / "wrappers/run_blender_hoi4_adapter.cmd").read_text(encoding="utf-8")
        self.assertIn("-m hoi4_blender_mcp", wrapper)

    def test_rejects_paths_outside_job_and_traversal(self):
        for value in (str(self.source), "../outside.blend", "blender/../accepted.blend", "C:/outside.blend", "\\\\server\\share\\x.blend"):
            with self.subTest(value=value):
                self.req["payload"]["checkpoint_rel"] = value
                with self.assertRaises(ValueError):
                    self.ns["_locator_request"](self.req)

    def test_rejects_checkpoint_collision_and_cross_directory_remap(self):
        for value in (self.req["payload"]["blend_rel"], "blender/elsewhere.blend", "blender/checkpoints/wrong.txt"):
            self.req["payload"]["checkpoint_rel"] = value
            with self.assertRaises(ValueError):
                self.ns["_locator_request"](self.req)

    def test_existing_sibling_checkpoint_is_never_overwritten(self):
        output = self.checkpoints / "with_muzzle.blend"
        output.write_bytes(b"owned-by-another-run")
        with self.assertRaisesRegex(ValueError, "never overwrites"):
            self.ns["author_locator"](self.req)
        self.assertEqual(output.read_bytes(), b"owned-by-another-run")
        self.bpy.ops.wm.open_mainfile.assert_not_called()
        self.bpy.ops.wm.save_as_mainfile.assert_not_called()

    def test_rejects_missing_input_and_output_directory(self):
        self.source.unlink()
        with self.assertRaises(FileNotFoundError):
            self.ns["_locator_request"](self.req)
        self.source.mkdir()
        with self.assertRaises(ValueError):
            self.ns["_locator_request"](self.req)

    def test_rejects_extra_inputs_and_unstable_names(self):
        self.req["payload"]["python"] = "no"
        with self.assertRaises(ValueError):
            self.ns["_locator_request"](self.req)
        del self.req["payload"]["python"]
        for name in ("", " muzzle", "muzzle ", "Muzzle", "muzzle.001", "muzzle/other", "a" * 64):
            self.req["payload"]["locator_name"] = name
            with self.assertRaises(ValueError):
                self.ns["_locator_request"](self.req)

    def test_rejects_nonfinite_wrong_size_bool_string_and_nonunit_rotation(self):
        for value in ([math.nan, 0, 0], [math.inf, 0, 0], [-math.inf, 0, 0], [True, 0, 0], ["1", 0, 0], [0, 0], [0, 0, 0, 0]):
            self.req["payload"]["bone_local_position"] = value
            with self.assertRaises(ValueError):
                self.ns["_locator_request"](self.req)
        self.req["payload"]["bone_local_position"] = [0, 0, 0]
        for value in ([0, 0, 0, 0], [0, 0, 0, 2], [0, 0, 0], [0, 0, math.nan, 1]):
            self.req["payload"]["bone_local_rotation_xyzw"] = value
            with self.assertRaises(ValueError):
                self.ns["_locator_request"](self.req)

    def test_exact_parent_type_bone_and_protection_checks(self):
        for rig, bone in (("missing", "Gun Bone"), ("Body", "Gun Bone"), ("Accepted Rig", "missing")):
            with self.assertRaises(ValueError):
                self.ns["_locator_parent"](rig, bone)
        for key in ("hoi4_source_protected", "hoi4_reference_read_only"):
            self.rig.props[key] = True
            with self.assertRaises(ValueError):
                self.ns["_locator_parent"](self.rig.name, self.bone.name)
            del self.rig.props[key]

    def test_zero_nonuniform_and_negative_rig_scale_fail_closed(self):
        for values in ((0, 0, 0), (1, 2, 1), (-1, 1, 1)):
            self.rig.matrix_world = MatrixDouble()
            for i, value in enumerate(values):
                self.rig.matrix_world.rows[i][i] = value
            with self.assertRaisesRegex(ValueError, "positive uniform"):
                self.ns["_locator_parent"](self.rig.name, self.bone.name)
        for i in range(3):
            self.rig.matrix_world.rows[i][i] = 0.5
        self.assertIs(self.ns["_locator_parent"](self.rig.name, self.bone.name), self.rig)

    def test_singular_bone_matrix_is_rejected(self):
        self.bone.matrix.rows[1][1] = 0.0
        with self.assertRaisesRegex(ValueError, "singular"):
            self.ns["_locator_parent"](self.rig.name, self.bone.name)

    def test_duplicate_locator_or_armature_names_are_rejected(self):
        self.registered()
        self.registered()
        with self.assertRaisesRegex(ValueError, "Duplicate locator names"):
            self.ns["author_locator"](self.req)
        self.objects.append(ObjectDouble(self.rig.name, "ARMATURE"))
        with self.assertRaisesRegex(ValueError, "one exact scene armature"):
            self.ns["_locator_parent"](self.rig.name, self.bone.name)

    def test_rejects_foreign_or_renamed_registered_empty(self):
        obj = self.registered(job_id="foreign_job")
        with self.assertRaisesRegex(ValueError, "ownership"):
            self.ns["author_locator"](self.req)
        obj.props["hoi4_locator_owner_job"] = "test_unit"
        obj.props["hoi4_locator_name"] = "renamed_predecessor"
        with self.assertRaisesRegex(ValueError, "ownership"):
            self.ns["author_locator"](self.req)
        self.bpy.ops.wm.save_as_mainfile.assert_not_called()

    def test_rejects_destructive_name_collisions(self):
        collision = ObjectDouble("muzzle", "MESH", data=object())
        self.objects.append(collision)
        with self.assertRaisesRegex(ValueError, "collision"):
            self.ns["author_locator"](self.req)
        self.assertIs(collision.data, self.objects.get("muzzle").data)
        self.bpy.ops.wm.save_as_mainfile.assert_not_called()

    def test_rejects_unregistered_empty_wrong_parent_and_nonleaf(self):
        obj = self.registered()
        for field, value in (("parent_type", "OBJECT"), ("parent_bone", "wrong"), ("parent", None), ("children", [self.mesh]), ("constraints", [object()]), ("animation_data", object()), ("instance_type", "COLLECTION")):
            previous = getattr(obj, field)
            setattr(obj, field, value)
            with self.assertRaises(ValueError):
                self.ns["author_locator"](self.req)
            setattr(obj, field, previous)
        obj.props.clear()
        with self.assertRaisesRegex(ValueError, "ownership"):
            self.ns["author_locator"](self.req)

    def test_rejects_bone_name_collision(self):
        self.req["payload"]["locator_name"] = "muzzle"
        self.rig.data.bones.append(ObjectDouble("muzzle", "BONE"))
        with self.assertRaisesRegex(ValueError, "skeleton bone"):
            self.ns["author_locator"](self.req)

    def test_rejects_locator_used_by_mesh_modifier_constraint_or_other_datablock(self):
        obj = self.registered()
        self.bpy.data.user_map.return_value = {obj: {self.mesh}}
        with self.assertRaisesRegex(ValueError, "referenced by another data-block"):
            self.ns["author_locator"](self.req)
        self.bpy.ops.wm.save_as_mainfile.assert_not_called()

    def test_rejects_unretained_actions_instead_of_changing_fake_user_flags(self):
        action = types.SimpleNamespace(name="orphan", users=0, use_fake_user=False)
        self.bpy.data.actions.append(action)
        with self.assertRaisesRegex(ValueError, "unretained"):
            self.ns["author_locator"](self.req)
        self.assertFalse(action.use_fake_user)
        self.assertIsNone(self.objects.get("muzzle"))

    def test_author_control_flow_creates_or_updates_only_one_empty_and_copy_saves(self):
        result = self.ns["author_locator"](self.req)
        self.assertTrue(result["created"])
        self.assertEqual(result["locator"]["parent_bone"], "Gun Bone")
        self.assertEqual(result["locator"]["bone_local_matrix"][0][3], 0.1)
        self.ns["Quaternion"].assert_called_with((1.0, 0.0, 0.0, 0.0))
        self.bpy.ops.wm.open_mainfile.assert_called_once_with(filepath=str(self.source), use_scripts=False)
        self.bpy.ops.wm.save_as_mainfile.assert_called_once_with(filepath=str(self.checkpoints / "with_muzzle.blend"), copy=True, relative_remap=False)
        self.assertEqual(len(self.objects), 3)
        locator = self.objects.get("muzzle")
        self.req["payload"]["checkpoint_rel"] = "blender/checkpoints/updated_muzzle.blend"
        result = self.ns["author_locator"](self.req)
        self.assertFalse(result["created"])
        self.assertIs(self.objects.get("muzzle"), locator)
        self.assertEqual(len(self.objects), 3)
        self.assertEqual(self.rig.props, {"hoi4_working": True})
        self.assertEqual(self.mesh.props, {"hoi4_working": True})
        self.assertEqual(self.source.read_bytes(), b"fixture-not-a-blend")

    def test_worker_dispatch_does_not_load_exporter_for_authoring(self):
        self.ns["load_pdx"] = Mock(side_effect=AssertionError("must not load extension"))
        self.ns["author_locator"] = Mock(return_value={"operation": "author_locator"})
        self.assertEqual(self.ns["run"](self.req), {"operation": "author_locator"})
        self.ns["load_pdx"].assert_not_called()

    def test_only_registered_locators_on_exported_approved_rig_are_returned(self):
        approved = self.registered()
        unregistered = ObjectDouble("unapproved_empty", "EMPTY", parent=self.rig, parent_bone="Gun Bone")
        self.objects.append(unregistered)
        self.assertEqual(self.ns["approved_export_locators"](self.job, "test_unit", [self.mesh]), [approved])
        self.assertEqual(self.ns["approved_export_locators"](self.job, "test_unit", []), [])
        self.rig.props["hoi4_working"] = False
        with self.assertRaisesRegex(ValueError, "approved working"):
            self.ns["approved_export_locators"](self.job, "test_unit", [self.mesh])

    def test_export_rejects_foreign_registry_and_ignored_skeleton_branch(self):
        obj = self.registered(job_id="foreign")
        with self.assertRaisesRegex(ValueError, "ownership"):
            self.ns["approved_export_locators"](self.job, "test_unit", [self.mesh])
        obj.props["hoi4_locator_owner_job"] = "test_unit"
        root = ObjectDouble("root", "BONE")
        self.bone.parent = root
        self.bone.props["pdxIgnoreJoint"] = True
        self.rig.data.bones.insert(0, root)
        with self.assertRaisesRegex(ValueError, "excluded"):
            self.ns["approved_export_locators"](self.job, "test_unit", [self.mesh])

    def test_locator_reports_parent_and_local_world_matrices(self):
        obj = self.registered()
        result = self.ns["locator_records"]([obj])[0]
        self.assertEqual(result["parent"], "Accepted Rig")
        self.assertEqual(result["parent_bone"], "Gun Bone")
        self.assertEqual(result["parent_type"], "BONE")
        self.assertEqual(result["frame"], 145)
        for field in ("matrix_world", "matrix_basis", "matrix_parent_inverse", "bone_local_matrix", "rest_bone_relative_matrix"):
            self.assertEqual(len(result[field]), 4)
        self.assertTrue(result["registered_for_export"])

    def test_first_root_own_ignore_flag_matches_installed_exporter_semantics(self):
        obj = self.registered()
        self.bone.props["pdxIgnoreJoint"] = True
        self.assertEqual(self.ns["approved_export_locators"](self.job, "test_unit", [self.mesh]), [obj])

    def test_rna_wrapper_equality_accepts_same_data_and_rejects_distinct_data(self):
        obj = self.registered()
        root = ObjectDouble("root", "BONE")
        self.bone.parent = root
        self.rig.data.bones = RnaLookupObjects([root, self.bone])
        self.bpy.context.scene.objects = RnaLookupObjects(self.objects)
        obj.parent = RnaWrapperDouble(self.rig)
        self.assertIsNot(self.bpy.context.scene.objects.get(self.rig.name), self.rig)
        self.assertIsNot(self.rig.data.bones[0], root)
        self.assertIs(self.ns["_locator_parent"](self.rig.name, self.bone.name), self.rig)
        self.assertEqual(self.ns["approved_export_locators"](self.job, "test_unit", [self.mesh]), [obj])
        # Equality must remain RNA-data identity, never merely equal names.
        obj.parent = RnaWrapperDouble(ObjectDouble(self.rig.name, "ARMATURE"))
        with self.assertRaisesRegex(ValueError, "different parent"):
            self.ns["approved_export_locators"](self.job, "test_unit", [self.mesh])
        obj.parent = RnaWrapperDouble(self.rig)
        self.bone.parent = ObjectDouble(root.name, "BONE")
        with self.assertRaisesRegex(ValueError, "first-root"):
            self.ns["approved_export_locators"](self.job, "test_unit", [self.mesh])

    def test_nonfinite_matrix_evidence_fails_closed(self):
        invalid = MatrixDouble()
        invalid[0][3] = math.nan
        with self.assertRaisesRegex(ValueError, "finite"):
            self.ns["_locator_matrix_record"](invalid)

    def test_inspect_and_reimport_report_parent_bone_and_locator_records(self):
        for name in ("inspect", "reimport_export"):
            function = next(node for node in self.tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
            source = ast.unparse(function)
            self.assertIn("'parent_bone': obj.parent_bone", source)
            self.assertIn("'locators': locator_records()", source)
        reimport = next(node for node in self.tree.body if isinstance(node, ast.FunctionDef) and node.name == "reimport_export")
        self.assertIn("imp_locs=True", ast.unparse(reimport))

    def test_export_control_flow_uses_exact_selection_and_rest_then_restores_on_error(self):
        approved = self.registered()
        unapproved = ObjectDouble("unregistered", "EMPTY")
        unapproved.selected = True
        self.objects.append(unapproved)
        captured = {}

        def exporter(path, **kwargs):
            captured.update(kwargs)
            captured["selection"] = sorted(obj.name for obj in self.bpy.context.selected_objects)
            captured["pose_position"] = self.rig.data.pose_position
            raise RuntimeError("test-only exporter sentinel")

        self.ns["load_pdx"] = Mock(return_value={"export_meshfile": exporter, "list_scene_pdx_meshes": lambda: [self.mesh]})
        self.ns["prepare_pdx_export_transforms"] = Mock(return_value={"armature_data_scale_factor": 1.0})
        self.req["payload"] = {"blend_rel": "blender/checkpoints/accepted.blend", "output_rel": "export/mesh/test.mesh"}
        with self.assertRaisesRegex(RuntimeError, "test-only exporter sentinel"):
            self.ns["export_mesh"](self.req, {})
        self.assertEqual(captured["selection"], ["Body", "muzzle"])
        self.assertTrue(captured["exp_selected"])
        self.assertTrue(captured["exp_locs"])
        self.assertEqual(captured["pose_position"], "REST")
        self.assertEqual(self.rig.data.pose_position, "POSE")
        self.assertTrue(approved.selected)
        self.assertFalse(unapproved.selected)

    def test_export_does_not_include_locator_when_no_pdx_material_mesh_uses_its_rig(self):
        self.registered()
        captured = []

        def exporter(path, **kwargs):
            captured.extend(obj.name for obj in self.bpy.context.selected_objects)
            raise RuntimeError("test-only exporter sentinel")

        self.ns["load_pdx"] = Mock(return_value={"export_meshfile": exporter, "list_scene_pdx_meshes": lambda: []})
        self.ns["prepare_pdx_export_transforms"] = Mock(return_value={})
        self.req["payload"] = {"blend_rel": "blender/checkpoints/accepted.blend", "output_rel": "export/mesh/test.mesh"}
        with self.assertRaisesRegex(RuntimeError, "test-only exporter sentinel"):
            self.ns["export_mesh"](self.req, {})
        self.assertEqual(captured, ["Body"])

    def test_uniform_export_scale_applies_once_to_registered_local_offset(self):
        locator = self.registered()
        for i in range(3):
            self.rig.matrix_world.rows[i][i] = 0.5
        locator.matrix_world = self.rig.matrix_world @ MatrixDouble.Translation([2, 4, 6])
        captured = {}

        def prepare():
            self.rig.matrix_world = MatrixDouble()
            return {"armature_data_scale_factor": 0.5}

        def exporter(path, **kwargs):
            captured["local"] = self.ns["locator_records"]([locator])[0]["bone_local_matrix"]
            raise RuntimeError("test-only exporter sentinel")

        self.ns["load_pdx"] = Mock(return_value={"export_meshfile": exporter, "list_scene_pdx_meshes": lambda: [self.mesh]})
        self.ns["prepare_pdx_export_transforms"] = prepare
        self.req["payload"] = {"blend_rel": "blender/checkpoints/accepted.blend", "output_rel": "export/mesh/test.mesh"}
        with self.assertRaisesRegex(RuntimeError, "test-only exporter sentinel"):
            self.ns["export_mesh"](self.req, {})
        self.assertEqual([captured["local"][i][3] for i in range(3)], [1.0, 2.0, 3.0])
        self.assertEqual(self.rig.data.pose_position, "POSE")


if __name__ == "__main__":
    unittest.main()
