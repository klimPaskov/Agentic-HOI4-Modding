"""Operation-scoped material-clone image reconciliation; shared gates stay exact."""
import copy
import types
import unittest

from test_reimport_promotion_contract import Block, load_worker
from test_skeletal_export_streams import MOD


class PartitionImageConsumers(unittest.TestCase):
    def setUp(self):
        self.ns, _ = load_worker()
        def block(name, kind, **attrs):
            value = Block(name, **attrs)
            value.bl_rna.identifier = kind
            return value
        self.tree = block("CloneTree", "ShaderNodeTree", users=1, is_embedded_data=True)
        self.source = block("Source", "Material")
        self.clone = block("Clone", "Material", node_tree=self.tree)
        self.mesh = block("Mesh", "Mesh", users=1, materials=[self.source, self.clone])
        self.obj = block("Body", "Object", data=self.mesh)
        self.ns["bpy"] = types.SimpleNamespace(types=types.SimpleNamespace(ID=Block))
        self.api = types.SimpleNamespace(_promotion_value=self.ns["_promotion_value"], _promotion_digest=self.ns["_promotion_digest"],
                                         bpy=types.SimpleNamespace(data=types.SimpleNamespace(objects={"Body": self.obj}, materials={"Source": self.source, "Clone": self.clone}, user_map=lambda subset: {tree: set() for tree in subset})))
        self.clones = {"Clone": "Source"}
        self.ownership = {"Clone": {"source_material": "Source", "source_record_sha256": "sourceexact", "object": "Body", "mesh": "Mesh", "slot": 1,
                                    "material_id": self.api._promotion_value(self.clone), "tree_id": self.api._promotion_value(self.tree)}}
        base = {"settings": {"name": "Source", "node_tree": {"name": "SourceTree"}}, "nodes": [{"name": "Texture", "image": "Image"}], "links": []}
        clone = copy.deepcopy(base)
        clone["settings"].update(name="Clone", node_tree={"name": "CloneTree"})
        source_retention = {"record_sha256": "sourceexact", "fake_user": False, "local": True, "protected": False}
        clone_retention = {"record_sha256": "cloneexact", "fake_user": False, "extra_user": False, "local": True, "protected": False, "tree_retained": False,
                           "users": 1, "mesh_slots": [("Mesh", 1)], "object_slots": [("Body", 1, "DATA")], "id_consumers": [self.api._promotion_value(self.mesh)]}
        self.result = {"sections": {"materials": {"Source": base, "Clone": clone}},
                       "material_retention": {"inventory": {"Source": source_retention, "Clone": clone_retention}}}
        row = {"record_sha256": "unchanged pixels settings and path", "users": 1, "local": True, "fake_user": False, "extra_user": False, "protected": False,
               "material_nodes": [{"material": "Source", "node": "Texture", "tree": "SourceTree"}], "material_consumers": ["Source"],
               "id_consumers": [self.api._promotion_value(self.source)], "other_id_consumers": [], "retained_node_trees": [],
               "packed_hashes": ["exact packed pixels"], "pixel_sha256": None, "missing_data_sentinel": False,
               "source_file": {"path": "fixed image path", "sha256": "fixed file bytes"}, "consumer_map_complete": True, "exclusive_orphan_consumers": False}
        self.before = {"inventory": {"Image": row}, "content_sha256": "exact image content"}
        self.after = copy.deepcopy(self.before)
        changed = self.after["inventory"]["Image"]
        changed["users"] = 2
        changed["material_nodes"] = [{"material": "Clone", "node": "Texture", "tree": "CloneTree"}, *row["material_nodes"]]
        changed["material_consumers"] = ["Clone", "Source"]
        changed["id_consumers"] = [self.api._promotion_value(self.clone), *row["id_consumers"]]

    def validate(self):
        ownership = MOD._partition_clone_ownership(self.api, self.result, ["Body"], self.clones, self.ownership)
        images = MOD._partition_image_consumers(self.api, self.before, self.after, self.clones, self.ownership)
        return ownership, images

    def test_planned_owned_clone_addition_preserves_image_bytes_and_receipt(self):
        ownership, proof = self.validate()
        self.assertTrue(proof["accepted"])
        self.assertEqual(ownership["Clone"]["ownership"], self.ownership["Clone"])
        self.assertEqual(proof["images"][0]["before"], self.before["inventory"]["Image"])
        self.assertEqual(proof["images"][0]["after"], self.after["inventory"]["Image"])
        self.assertEqual(proof["images"][0]["planned_clone_additions"][0]["added_users"], 1)

    def test_missing_extra_and_outside_transaction_ownership_reject(self):
        for ownership in (None, {}, {**self.ownership, "Other": self.ownership["Clone"]}):
            with self.subTest(ownership=ownership), self.assertRaises(RuntimeError):
                MOD._partition_clone_ownership(self.api, self.result, ["Body"], self.clones, ownership)
        for key, value in (("object", "Other"), ("mesh", "Other"), ("slot", 0), ("source_material", "Other"), ("source_record_sha256", "changed"), ("material_id", {"name": "Other"}), ("tree_id", {"name": "Other"})):
            changed = copy.deepcopy(self.ownership)
            changed["Clone"][key] = value
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                MOD._partition_clone_ownership(self.api, self.result, ["Body"], self.clones, changed)

    def test_clone_content_or_source_content_change_rejects(self):
        for owner in ("Clone", "Source"):
            changed = copy.deepcopy(self.result)
            changed["sections"]["materials"][owner]["nodes"][0]["image"] = "Other"
            with self.subTest(owner=owner), self.assertRaises(RuntimeError):
                MOD._partition_clone_ownership(self.api, changed, ["Body"], self.clones, self.ownership)

    def test_clone_node_tree_external_or_missing_native_consumer_evidence_rejects(self):
        for mapping in ({}, {self.tree: {self.obj}}):
            self.api.bpy.data.user_map = lambda subset: mapping
            with self.subTest(mapping=mapping), self.assertRaises(RuntimeError):
                self.validate()

    def test_clone_retention_and_other_slot_consumers_reject(self):
        values = {"users": 2, "fake_user": True, "extra_user": True, "local": False, "protected": True, "tree_retained": True,
                  "mesh_slots": [("OtherMesh", 1)], "object_slots": [("Other", 1, "DATA")],
                  "id_consumers": [{"id_type": "Object", "name": "Other", "library": None}]}
        for key, value in values.items():
            changed = copy.deepcopy(self.result)
            changed["material_retention"]["inventory"]["Clone"][key] = value
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                MOD._partition_clone_ownership(self.api, changed, ["Body"], self.clones, self.ownership)

    def test_image_content_path_flags_and_original_consumers_cannot_change(self):
        values = {"record_sha256": "changed", "users": 3, "fake_user": True, "extra_user": True, "local": False, "protected": True,
                  "packed_hashes": ["changed"], "source_file": {"path": "changed", "sha256": "changed"},
                  "material_consumers": ["Clone"], "id_consumers": [self.api._promotion_value(self.clone)],
                  "other_id_consumers": [{"name": "Other"}], "consumer_map_complete": False}
        for key, value in values.items():
            changed = copy.deepcopy(self.after)
            changed["inventory"]["Image"][key] = value
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                MOD._partition_image_consumers(self.api, self.before, changed, self.clones, self.ownership)

    def test_image_addition_loss_or_content_hash_change_rejects(self):
        for mode in ("added", "missing", "content"):
            changed = copy.deepcopy(self.after)
            if mode == "added":
                changed["inventory"]["Other"] = changed["inventory"]["Image"]
            elif mode == "missing":
                changed["inventory"].clear()
            else:
                changed["content_sha256"] = "changed"
            with self.subTest(mode=mode), self.assertRaises(RuntimeError):
                MOD._partition_image_consumers(self.api, self.before, changed, self.clones, self.ownership)

    def test_unplanned_material_node_or_id_consumer_rejects(self):
        for key, value in (("material_nodes", {"material": "Other", "node": "Texture", "tree": "Tree"}),
                           ("material_consumers", "Other"), ("id_consumers", {"id_type": "Material", "name": "Other", "library": None})):
            changed = copy.deepcopy(self.after)
            changed["inventory"]["Image"][key].append(value)
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                MOD._partition_image_consumers(self.api, self.before, changed, self.clones, self.ownership)

    def test_default_promotion_comparison_remains_strict_for_clone_additions(self):
        base = {"sha256": {"materials": "same", "images": "same"}, "material_retention": {"inventory": {}, "retained_sha256": "same"}}
        before, after = copy.deepcopy(base), copy.deepcopy(base)
        before["image_retention"], after["image_retention"] = self.before, self.after
        proof = self.ns["_promotion_reopen_comparison"](before, after)
        self.assertFalse(proof["accepted"])
        self.assertIn("image_retention.inventory['Image'].changed", proof["mismatches"])


if __name__ == "__main__":
    unittest.main()
