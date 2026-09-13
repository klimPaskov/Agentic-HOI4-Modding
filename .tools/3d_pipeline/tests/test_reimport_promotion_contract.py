"""Metadata promotion contracts, no Blender/provider invocation or fake native acceptance."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import math
import re
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock

from test_locator_adapter_contract import MatrixDouble, Objects


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
WORKER = PIPELINE_ROOT / "adapter/blender_worker.py"
TOOL = "hoi4_blender_promote_accepted_reimport"


class Block(dict):
    __hash__ = object.__hash__

    def __init__(self, name="", props=None, **attributes):
        super().__init__(props or {})
        self.name = self.name_full = name
        self.library = self.override_library = None
        self.bl_rna = types.SimpleNamespace(identifier="FixtureID", properties=[])
        self.__dict__.update(attributes)

    def __bool__(self):
        return True

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other


class SequenceOnly:
    """Exercise the sequence protocol used by mathutils without __iter__."""

    def __init__(self, *values):
        self.values = values

    def __len__(self):
        return len(self.values)

    def __getitem__(self, index):
        return self.values[index]


def load_worker():
    tree = ast.parse(WORKER.read_text(encoding="utf-8"))
    functions = {"within", "file_sha256", "_locator_exact_name", "_locator_numbers", "_locator_matrix_record", "promote_accepted_reimport", "run"}
    nodes = [ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)]
    nodes += [node for node in tree.body if (isinstance(node, ast.FunctionDef) and (node.name.startswith("_promotion_") or node.name in functions)) or (isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "PROMOTION_METADATA_KEYS" for target in node.targets))]
    namespace = {"Path": Path, "hashlib": hashlib, "json": json, "math": math, "re": re}
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), str(WORKER), "exec"), namespace)
    return namespace, tree


class PromotionContracts(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.job = Path(temporary.name).resolve()
        for directory in ("blender/checkpoints", "validation", "export"):
            (self.job / directory).mkdir(parents=True)
        self.req = {"job_id": "fixture", "job_root": str(self.job), "operation": "promote_accepted_reimport", "payload": {
            "blend_rel": "blender/checkpoints/proof.blend", "expected_source_sha256": "",
            "validation_rel": "validation/proof.json", "expected_validation_sha256": "",
            "checkpoint_rel": "blender/checkpoints/working.blend", "target_armature_name": "Rig", "target_mesh_names": ["Body"],
            "mesh_rel": "export/proof.mesh", "expected_mesh_sha256": "", "anim_rel": "export/proof.anim", "expected_anim_sha256": "",
        }}
        self.receipt = {"proof_blend": self.req["payload"]["blend_rel"], "mesh": "export/proof.mesh", "anim": "export/proof.anim",
                        "objects": [{"name": "Rig", "type": "ARMATURE"}, {"name": "Body", "type": "MESH"}],
                        "meshes": [{"name": "Body", "vertices": 27, "polygons": 1, "materials": ["Material"]}],
                        "armatures": [{"name": "Rig", "bones": 2}], "actions": ["RetainedAction"],
                        "geometry": {"objects": 1, "vertices": 27, "polygons": 1, "triangles": 1},
                        "animation_bounds": [{"frame": 1, "bounds_min": [0, 0, 0], "bounds_max": [1, 1, 1], "dimensions": [1, 1, 1]}],
                        "previews": ["blender/previews/proof.png"], "runtime_texture_staging": []}
        for field, hash_field in (("blend_rel", "expected_source_sha256"), ("mesh_rel", "expected_mesh_sha256"), ("anim_rel", "expected_anim_sha256")):
            path = self.job / self.req["payload"][field]
            path.write_bytes(f"not-native-fixture-{field}".encode())
            self.req["payload"][hash_field] = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        self.write_receipt()
        self.ns, self.tree = load_worker()
        self.collection = Block("Collection")
        self.material = Block("Material", {"shader": "PdxMeshAdvanced"}, use_nodes=True)
        self.rig = Block("Rig", type="ARMATURE", data=Block("RigData", bones=["Root", "Gun"]), matrix_world=MatrixDouble(), users_collection=[self.collection])
        self.mesh = Block("Body", type="MESH", data=Block("MeshData", vertices=[1, 2, 3], polygons=[1], materials=[self.material], shape_keys=None), matrix_world=MatrixDouble(), users_collection=[self.collection], modifiers=[types.SimpleNamespace(type="ARMATURE", object=self.rig)])
        self.action = Block("RetainedAction", users=1, use_fake_user=True)
        self.objects = Objects([self.rig, self.mesh])
        self.scene = Block("Scene", objects=self.objects, render=types.SimpleNamespace(fps=30, fps_base=1.0), frame_current=1, frame_subframe=0.0, frame_start=1, frame_end=20)
        self.bpy = types.SimpleNamespace(types=types.SimpleNamespace(ID=Block), data=types.SimpleNamespace(objects=self.objects, actions=[self.action], materials=[], images=[], meshes=[], collections=[], user_map=Mock(return_value={})), context=types.SimpleNamespace(scene=self.scene), ops=types.SimpleNamespace(wm=types.SimpleNamespace(open_mainfile=Mock(), save_as_mainfile=Mock(side_effect=self.save))))
        self.ns["bpy"] = self.bpy
        self.baseline = {"sha256": {name: "unchanged" for name in ("objects", "geometry", "rigs", "materials", "images", "actions", "scene")}, "material_retention": {"inventory": {}, "retained_sha256": "unchanged"}, "mesh_counts": {"Body": {"vertices": 3, "polygons": 1, "loops": 3}}, "actions": ["RetainedAction"], "objects": ["Body", "Rig"]}

    def write_receipt(self):
        path = self.job / self.req["payload"]["validation_rel"]
        path.write_text(json.dumps(self.receipt), encoding="utf-8")
        self.req["payload"]["expected_validation_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest().upper()

    def save(self, **kwargs):
        Path(kwargs["filepath"]).write_bytes(b"not-native-saved-copy")
        return {"FINISHED"}

    def context(self):
        return self.ns["_promotion_inputs"](self.req)

    def test_exact_tool_schema_and_client_forwarding(self):
        fields = {"job_id", *self.req["payload"]}
        source = ast.parse((PIPELINE_ROOT / "adapter/hoi4_blender_mcp.py").read_text(encoding="utf-8"))
        tool = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == TOOL)
        self.assertEqual({arg.arg for arg in tool.args.args}, fields)
        self.assertIn("mcp.tool()", [ast.unparse(node) for node in tool.decorator_list])
        self.assertFalse({"code", "python", "url", "shell"} & fields)
        client = ast.parse((PIPELINE_ROOT / "blender_client.py").read_text(encoding="utf-8"))
        owner = next(node for node in client.body if isinstance(node, ast.ClassDef) and node.name == "BlenderAdapterClient")
        method = next(node for node in owner.body if isinstance(node, ast.FunctionDef) and node.name == "promote_accepted_reimport")
        self.assertEqual({arg.arg for arg in method.args.args}, {"self", *fields})
        for function, args, callback_name in ((tool, {"job_id": "fixture", **self.req["payload"]}, "_run"), (method, {"self": types.SimpleNamespace(call=Mock()), "job_id": "fixture", **self.req["payload"]}, "call")):
            function = copy.deepcopy(function)
            function.decorator_list = []
            namespace = {"_run": Mock(return_value={"ok": True})}
            module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), function], type_ignores=[])
            exec(compile(ast.fix_missing_locations(module), "fixture", "exec"), namespace)
            namespace[function.name](**args)
            if callback_name == "_run":
                namespace["_run"].assert_called_once_with("fixture", "promote_accepted_reimport", self.req["payload"])
            else:
                args["self"].call.assert_called_once_with(TOOL, {"job_id": "fixture", **self.req["payload"]})

    def test_legacy_receipt_is_hash_bound_without_inventing_status_or_hashes(self):
        before = (self.job / self.req["payload"]["validation_rel"]).read_bytes()
        context = self.context()
        self.assertEqual(context["receipt"], self.receipt)
        self.assertNotIn("status", context["receipt"])
        self.assertEqual((self.job / self.req["payload"]["validation_rel"]).read_bytes(), before)
        self.assertEqual(set(context["inputs"]), {"source", "validation", "mesh", "anim"})

    def test_all_four_expected_hashes_are_required_and_checked(self):
        for field in ("expected_source_sha256", "expected_validation_sha256", "expected_mesh_sha256", "expected_anim_sha256"):
            for value in ("0" * 64, "", True, "G" * 64):
                request = copy.deepcopy(self.req)
                request["payload"][field] = value
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    self.ns["_promotion_inputs"](request)

    def test_path_escape_traversal_absolute_and_wrong_types_fail(self):
        for field in ("blend_rel", "validation_rel", "mesh_rel", "anim_rel", "checkpoint_rel"):
            for value in ("../outside.blend", "C:/outside.blend", "\\\\server\\outside.blend", str(self.job / "proof.blend"), "blender/../proof.blend", None):
                request = copy.deepcopy(self.req)
                request["payload"][field] = value
                with self.subTest(field=field, value=value), self.assertRaises((ValueError, FileNotFoundError)):
                    self.ns["_promotion_inputs"](request)

    def test_sibling_output_and_report_must_be_new(self):
        request = copy.deepcopy(self.req)
        request["payload"]["checkpoint_rel"] = "export/working.blend"
        with self.assertRaisesRegex(ValueError, "sibling"):
            self.ns["_promotion_inputs"](request)
        output = self.job / self.req["payload"]["checkpoint_rel"]
        output.write_bytes(b"existing")
        with self.assertRaisesRegex(ValueError, "overwrite"):
            self.context()
        self.assertEqual(output.read_bytes(), b"existing")
        output.unlink()
        report = self.job / "blender/reports/promote_working.json"
        report.parent.mkdir()
        report.write_text("existing", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "report already"):
            self.context()

    def test_names_are_explicit_unique_and_bounded(self):
        for names in ([], ["Body"] * 2, ["Rig"], [" Body"], [str(index) for index in range(17)], "Body"):
            request = copy.deepcopy(self.req)
            request["payload"]["target_mesh_names"] = names
            with self.subTest(names=names), self.assertRaises(ValueError):
                self.ns["_promotion_inputs"](request)
        request = copy.deepcopy(self.req)
        request["payload"]["code"] = "not permitted"
        with self.assertRaises(ValueError):
            self.ns["_promotion_inputs"](request)

    def test_receipt_failure_incomplete_duplicate_and_nonfinite_shapes_reject(self):
        original = copy.deepcopy(self.receipt)
        changes = [("status", "fail"), ("error", "bad export"), ("actions", []), ("objects", self.receipt["objects"] * 2), ("meshes", []), ("geometry", {}), ("previews", []), ("animation_bounds", []), ("unused_nan", float("nan"))]
        for key, value in changes:
            self.receipt = {**copy.deepcopy(original), key: value}
            self.write_receipt()
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.context()
        self.receipt = copy.deepcopy(original)
        del self.receipt["proof_blend"]
        self.write_receipt()
        with self.assertRaises(ValueError):
            self.context()
        path = self.job / self.req["payload"]["validation_rel"]
        path.write_text('{"mesh":"a", "mesh":"b"}', encoding="utf-8")
        self.req["payload"]["expected_validation_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.context()

    def test_receipt_exact_paths_and_optional_embedded_hashes_must_match(self):
        for key, suffix in (("proof_blend", ".blend"), ("mesh", ".mesh"), ("anim", ".anim")):
            original = self.receipt[key]
            alternative = self.job / f"export/other{suffix}"
            alternative.write_bytes(b"other")
            self.receipt[key] = alternative.relative_to(self.job).as_posix()
            self.write_receipt()
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "match"):
                self.context()
            self.receipt[key] = original
        self.receipt["mesh_sha256"] = "0" * 64
        self.write_receipt()
        with self.assertRaisesRegex(ValueError, "conflicts"):
            self.context()

    def test_current_vertex_count_is_not_forced_to_equal_exported_receipt_count(self):
        targets = self.ns["_promotion_targets"](self.context())
        self.assertEqual(targets, [self.rig, self.mesh])
        self.assertEqual(len(self.mesh.data.vertices), 3)
        self.assertEqual(self.receipt["meshes"][0]["vertices"], 27)

    def test_rejects_wrong_duplicate_linked_protected_or_already_working_targets(self):
        context = self.context()
        for block in (self.rig, self.rig.data, self.collection, self.mesh, self.mesh.data):
            for key in ("hoi4_source_protected", "hoi4_reference_read_only"):
                block[key] = True
                with self.subTest(name=block.name, key=key), self.assertRaisesRegex(ValueError, "protected"):
                    self.ns["_promotion_targets"](context)
                del block[key]
            block.library = object()
            with self.assertRaisesRegex(ValueError, "Linked"):
                self.ns["_promotion_targets"](context)
            block.library = None
        self.rig["hoi4_working"] = True
        with self.assertRaisesRegex(ValueError, "already working"):
            self.ns["_promotion_targets"](context)
        del self.rig["hoi4_working"]
        self.objects.append(self.rig)
        with self.assertRaisesRegex(ValueError, "one exact"):
            self.ns["_promotion_targets"](context)

    def test_rejects_wrong_rig_binding_material_action_or_topology(self):
        context = self.context()
        self.mesh.modifiers[0].object = Block("Rig")
        with self.assertRaisesRegex(ValueError, "exact accepted rig"):
            self.ns["_promotion_targets"](context)
        self.mesh.modifiers[0].object = self.rig
        self.material.name = "Other"
        with self.assertRaisesRegex(ValueError, "material identity"):
            self.ns["_promotion_targets"](context)
        self.material.name = "Material"
        self.action.name = "RenamedAction"
        with self.assertRaisesRegex(ValueError, "action identities"):
            self.ns["_promotion_targets"](context)
        self.action.name = "RetainedAction"
        self.mesh.data.polygons.append(2)
        with self.assertRaisesRegex(ValueError, "topology"):
            self.ns["_promotion_targets"](context)

    def test_success_sets_only_named_metadata_copy_saves_reopens_and_keeps_inputs(self):
        self.ns["_promotion_fingerprint"] = Mock(return_value=self.baseline)
        result = self.ns["promote_accepted_reimport"](self.req)
        self.assertEqual(result["status"], "pass")
        self.assertFalse(result["new_provider_call"])
        self.assertTrue(result["all_inputs_immutable"])
        self.assertEqual(result["fingerprints_before"], result["fingerprints_after"])
        for obj in (self.rig, self.mesh):
            self.assertEqual(set(obj.keys()), set(self.ns["PROMOTION_METADATA_KEYS"]))
            self.assertTrue(obj["hoi4_working"])
        self.bpy.ops.wm.save_as_mainfile.assert_called_once_with(filepath=str(self.job / result["checkpoint"]), copy=True, relative_remap=False)
        self.assertEqual(self.bpy.ops.wm.open_mainfile.call_count, 2)
        self.assertTrue(all(call.kwargs["use_scripts"] is False for call in self.bpy.ops.wm.open_mainfile.call_args_list))
        self.assertEqual(json.loads((self.job / result["report"]).read_text())["status"], "pass")

    def test_each_post_reopen_invariant_mismatch_fails_hard_with_failure_report(self):
        for category in self.baseline["sha256"]:
            with self.subTest(category=category):
                self.rig.clear()
                self.mesh.clear()
                for path in (self.job / "blender/reports/promote_working.json", self.job / self.req["payload"]["checkpoint_rel"]):
                    if path.exists():
                        path.unlink()
                changed = copy.deepcopy(self.baseline)
                changed["sha256"][category] = "drift"
                self.ns["_promotion_fingerprint"] = Mock(side_effect=[self.baseline, self.baseline, changed])
                with self.assertRaisesRegex(RuntimeError, "invariant mismatch"):
                    self.ns["promote_accepted_reimport"](self.req)
                failure = json.loads((self.job / "blender/reports/promote_working.json").read_text())
                self.assertEqual(failure["status"], "fail")
                self.assertFalse(failure["output_approved"])

    def test_changed_immutable_input_fails_even_when_scene_fingerprint_matches(self):
        self.ns["_promotion_fingerprint"] = Mock(return_value=self.baseline)
        source = self.job / self.req["payload"]["mesh_rel"]
        def corrupt_input(**kwargs):
            source.write_bytes(b"changed")
            return self.save(**kwargs)
        self.bpy.ops.wm.save_as_mainfile.side_effect = corrupt_input
        with self.assertRaisesRegex(RuntimeError, "Immutable promotion mesh"):
            self.ns["promote_accepted_reimport"](self.req)

    def orphan_inventory(self):
        orphan = Block("Orphan", users=0, use_fake_user=False, use_extra_user=False,
                       node_tree=Block("OrphanTree", use_fake_user=False, use_extra_user=False))
        self.bpy.data.materials = [orphan]
        self.bpy.data.objects = []
        self.bpy.data.user_map.return_value = {orphan: set()}
        return orphan, self.ns["_promotion_material_retention"]({"Orphan": {"exact": [1, 2, 3]}})

    def test_plain_orphan_disappearance_passes_and_records_exact_before_evidence(self):
        orphan, inventory = self.orphan_inventory()
        before, after = copy.deepcopy(self.baseline), copy.deepcopy(self.baseline)
        before["material_retention"] = inventory
        after["material_retention"] = {"inventory": {}, "retained_sha256": inventory["retained_sha256"]}
        after["sha256"]["materials"] = "native_orphan_drop"
        result = self.ns["_promotion_reopen_comparison"](before, after)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["removed_orphan_materials"][0]["name"], orphan.name)
        self.assertEqual(result["removed_orphan_materials"][0]["before"], inventory["inventory"]["Orphan"])
        self.bpy.data.user_map.assert_called_once_with(subset=[orphan])

    def test_material_retention_uses_complete_id_map_and_independent_slots(self):
        orphan, _ = self.orphan_inventory()
        self.bpy.data.user_map.return_value = {}
        with self.assertRaisesRegex(ValueError, "absent from the native ID user map"):
            self.ns["_promotion_material_retention"]({"Orphan": {}})
        consumer = Block("GeometryNodeConsumer")
        self.bpy.data.user_map.return_value = {orphan: {consumer}}
        record = self.ns["_promotion_material_retention"]({"Orphan": {}})["inventory"]["Orphan"]
        self.assertFalse(record["discardable_orphan"])
        self.assertEqual(record["id_consumers"], [self.ns["_promotion_value"](consumer)])
        self.bpy.data.user_map.return_value = {orphan: set()}
        self.bpy.data.meshes = [Block("UnlinkedMesh", materials=[orphan])]
        record = self.ns["_promotion_material_retention"]({"Orphan": {}})["inventory"]["Orphan"]
        self.assertFalse(record["discardable_orphan"])
        self.assertEqual(record["mesh_slots"], [("UnlinkedMesh", 0)])
        self.bpy.data.meshes = []
        self.bpy.data.objects = [Block("ObjectSlot", material_slots=[types.SimpleNamespace(material=orphan, link="OBJECT")])]
        record = self.ns["_promotion_material_retention"]({"Orphan": {}})["inventory"]["Orphan"]
        self.assertFalse(record["discardable_orphan"])
        self.assertEqual(record["object_slots"], [("ObjectSlot", 0, "OBJECT")])

    def test_native_retention_flags_and_protection_feed_classification_without_mutation(self):
        orphan, baseline = self.orphan_inventory()
        material_value = {"exact": [1, 2, 3]}
        self.assertEqual(baseline["inventory"]["Orphan"]["record_sha256"], self.ns["_promotion_digest"](material_value))
        for block, attribute, value in ((orphan, "use_fake_user", True), (orphan, "use_extra_user", True), (orphan, "users", 1), (orphan.node_tree, "use_fake_user", True), (orphan.node_tree, "use_extra_user", True)):
            previous = getattr(block, attribute)
            setattr(block, attribute, value)
            record = self.ns["_promotion_material_retention"]({"Orphan": material_value})
            self.assertFalse(record["inventory"]["Orphan"]["discardable_orphan"])
            self.assertEqual(record["retained_sha256"], self.ns["_promotion_digest"]({"Orphan": material_value}))
            self.assertEqual(getattr(block, attribute), value)
            setattr(block, attribute, previous)
        for block in (orphan, orphan.node_tree):
            for key in ("hoi4_source_protected", "hoi4_reference_read_only"):
                block[key] = True
                self.assertFalse(self.ns["_promotion_material_retention"]({"Orphan": material_value})["inventory"]["Orphan"]["discardable_orphan"])
                self.assertTrue(block[key])
                del block[key]

    def test_fake_user_protected_linked_extra_user_and_consumed_disappearance_reject(self):
        _, inventory = self.orphan_inventory()
        for key, value in (("users", 1), ("users", False), ("fake_user", True), ("extra_user", True), ("protected", True), ("local", False), ("tree_retained", True), ("id_consumers", [{"name": "NodeConsumer"}]), ("mesh_slots", [["Mesh", 0]]), ("object_slots", [["Object", 0, "OBJECT"]])):
            before, after = copy.deepcopy(self.baseline), copy.deepcopy(self.baseline)
            before["material_retention"] = copy.deepcopy(inventory)
            # Even an incorrect cached classification cannot override native facts.
            before["material_retention"]["inventory"]["Orphan"][key] = value
            after["material_retention"]["retained_sha256"] = inventory["retained_sha256"]
            with self.subTest(key=key):
                self.assertFalse(self.ns["_promotion_reopen_comparison"](before, after)["accepted"])

    def test_orphan_addition_mutation_and_retained_material_mutation_reject(self):
        _, inventory = self.orphan_inventory()
        before = copy.deepcopy(self.baseline)
        before["material_retention"] = inventory
        for change in ("addition", "orphan_value", "retained_value", "new_consumer"):
            after = copy.deepcopy(before)
            if change == "addition":
                after["material_retention"]["inventory"]["Added"] = copy.deepcopy(inventory["inventory"]["Orphan"])
            elif change == "orphan_value":
                after["material_retention"]["inventory"]["Orphan"]["record_sha256"] = "changed"
            elif change == "retained_value":
                after["material_retention"]["retained_sha256"] = "changed"
            else:
                after["material_retention"]["inventory"]["Orphan"]["id_consumers"] = [{"name": "Consumer"}]
            with self.subTest(change=change):
                self.assertFalse(self.ns["_promotion_reopen_comparison"](before, after)["accepted"])

    def test_orphan_drop_cannot_hide_image_geometry_action_or_retained_material_drift(self):
        _, inventory = self.orphan_inventory()
        before, after = copy.deepcopy(self.baseline), copy.deepcopy(self.baseline)
        before["material_retention"] = inventory
        after["material_retention"]["retained_sha256"] = inventory["retained_sha256"]
        after["sha256"]["materials"] = "native_orphan_drop"
        for category in ("images", "geometry", "actions", "objects", "rigs", "scene"):
            changed = copy.deepcopy(after)
            changed["sha256"][category] = "changed"
            with self.subTest(category=category):
                self.assertFalse(self.ns["_promotion_reopen_comparison"](before, changed)["accepted"])
        after["material_retention"]["retained_sha256"] = "changed"
        self.assertFalse(self.ns["_promotion_reopen_comparison"](before, after)["accepted"])

    def test_orphan_disappearance_is_not_allowed_before_save(self):
        _, inventory = self.orphan_inventory()
        before, changed = copy.deepcopy(self.baseline), copy.deepcopy(self.baseline)
        before["material_retention"] = inventory
        changed["material_retention"]["retained_sha256"] = inventory["retained_sha256"]
        self.bpy.data.objects = self.objects
        self.ns["_promotion_fingerprint"] = Mock(side_effect=[before, changed])
        with self.assertRaisesRegex(RuntimeError, "before saving"):
            self.ns["promote_accepted_reimport"](self.req)
        self.bpy.ops.wm.save_as_mainfile.assert_not_called()

    def test_dispatch_does_not_load_exporter(self):
        self.ns["load_pdx"] = Mock(side_effect=AssertionError("must not load"))
        self.ns["promote_accepted_reimport"] = Mock(return_value={"dispatched": True})
        self.assertEqual(self.ns["run"](self.req), {"dispatched": True})
        self.ns["load_pdx"].assert_not_called()

    def test_original_fingerprint_rejects_unretained_actions(self):
        self.bpy.data.objects = []
        self.action.users, self.action.use_fake_user = 0, False
        with self.assertRaisesRegex(ValueError, "unretained"):
            self.ns["_promotion_fingerprint"](self.job, [])

    def test_serializer_reads_non_iter_sequence_values_and_nested_matrix_rows_exactly(self):
        vector = SequenceOnly(0.123456789012345, -0.0, 9.75)
        self.assertFalse(hasattr(vector, "__iter__"))
        self.assertEqual(list(vector), [0.123456789012345, -0.0, 9.75])
        matrix = SequenceOnly(*(SequenceOnly(*(float(row == column) for column in range(4))) for row in range(4)))
        value = self.ns["_promotion_value"](SequenceOnly(vector, matrix, SequenceOnly(0.1, 0.2, 0.3, 0.9)))
        self.assertEqual(value, [[0.123456789012345, -0.0, 9.75], [[float(row == column) for column in range(4)] for row in range(4)], [0.1, 0.2, 0.3, 0.9]])
        block = Block(position=vector)
        block.bl_rna.properties = [types.SimpleNamespace(identifier="position", type="FLOAT", is_readonly=False)]
        self.assertEqual(self.ns["_promotion_scalars"](block), {"position": value[0]})
        changed = copy.deepcopy(value)
        changed[0][0] += 1e-14
        self.assertNotEqual(self.ns["_promotion_digest"](value), self.ns["_promotion_digest"](changed))

    def test_non_iter_sequences_still_reject_nonfinite_and_unsupported_members(self):
        for number in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(number=number), self.assertRaisesRegex(ValueError, "nonfinite"):
                self.ns["_promotion_value"](SequenceOnly(SequenceOnly(1.0, number)))
        class Unsupported:
            def __repr__(self):
                raise AssertionError("Fingerprint must not use repr fallback")
        with self.assertRaisesRegex(ValueError, "Unsupported promotion fingerprint value: Unsupported"):
            self.ns["_promotion_value"](SequenceOnly(Unsupported()))

    def test_integer_vector_attributes_hash_both_signed_components_losslessly(self):
        for data_type, values in (("INT16_2D", [-32768, 32767]), ("INT32_2D", [-2147483648, 2147483647])):
            attribute = types.SimpleNamespace(data_type=data_type, domain="CORNER", data=[types.SimpleNamespace(value=SequenceOnly(*values))])
            record = self.ns["_promotion_attribute_record"](attribute)
            self.assertEqual(record, {"domain": "CORNER", "type": data_type, "sha256": self.ns["_promotion_digest"]([values])})
            for component in (0, 1):
                changed = list(values)
                changed[component] += 1 if component == 0 else -1
                attribute.data[0].value = SequenceOnly(*changed)
                self.assertNotEqual(self.ns["_promotion_attribute_record"](attribute)["sha256"], record["sha256"])

    def test_string_attributes_preserve_text_and_raw_bytes_without_lossy_decoding(self):
        for value in ("fixture-\u03bb\x00tail", b"\xff\x00\x80tail"):
            attribute = types.SimpleNamespace(data_type="STRING", domain="POINT", data=[types.SimpleNamespace(value=value)])
            expected = value if isinstance(value, str) else list(value)
            self.assertEqual(self.ns["_promotion_attribute_record"](attribute)["sha256"], self.ns["_promotion_digest"]([expected]))
        attribute.data_type = "UNRECOGNIZED"
        with self.assertRaisesRegex(ValueError, "Unsupported promotion mesh attribute"):
            self.ns["_promotion_attribute_record"](attribute)

    def test_original_fingerprint_detects_action_handles_interpolation_provenance_and_fps(self):
        self.bpy.data.objects = []
        self.action.frame_range = [1, 20]
        key = Block(co=[1, 2], handle_left=[0, 2], handle_right=[2, 2], interpolation="LINEAR")
        key.bl_rna.properties = [types.SimpleNamespace(identifier="interpolation", type="ENUM", is_readonly=False)]
        curve = Block(data_path='pose.bones["Gun"].location', array_index=0, modifiers=[], keyframe_points=[key], sampled_points=[])
        self.ns["action_fcurves"] = lambda action: [(curve, None)]
        fingerprint = lambda: self.ns["_promotion_fingerprint"](self.job, [])
        before = fingerprint()
        key.handle_left[1] = 3
        self.assertNotEqual(fingerprint()["sha256"]["actions"], before["sha256"]["actions"])
        key.handle_left[1] = 2
        key.interpolation = "BEZIER"
        self.assertNotEqual(fingerprint()["sha256"]["actions"], before["sha256"]["actions"])
        key.interpolation = "LINEAR"
        self.action["source_sha256"] = "a" * 64
        self.assertNotEqual(fingerprint()["sha256"]["actions"], before["sha256"]["actions"])
        self.action.clear()
        self.scene.render.fps = 24
        self.assertNotEqual(fingerprint()["sha256"]["scene"], before["sha256"]["scene"])

    def test_fingerprint_source_covers_geometry_material_and_rig_surfaces(self):
        function = next(node for node in self.tree.body if isinstance(node, ast.FunctionDef) and node.name == "_promotion_fingerprint")
        strings = {node.value for node in ast.walk(function) if isinstance(node, ast.Constant) and isinstance(node.value, str)}
        self.assertTrue({"positions_normals", "topology", "loops_normals", "uvs", "groups", "weights", "attributes", "parent_inverse", "properties", "bones", "rest", "images", "links", "filepath", "packed_hashes", "file_sha256", "actions"}.issubset(strings))


if __name__ == "__main__":
    unittest.main()
