"""Exact image preservation and narrow native orphan-removal evidence contracts."""
import copy
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock

from test_reimport_promotion_contract import Block, load_worker


class OrphanImageRetention(unittest.TestCase):
    def setUp(self):
        self.ns, _ = load_worker()
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.file = Path(temporary.name) / "image.png"
        self.file.write_bytes(b"immutable external image bytes")
        flags = dict(users=0, use_fake_user=False, use_extra_user=False)
        self.tree = Block("OrphanTree", **{**flags, "users": 1}, is_embedded_data=True, nodes=[])
        self.material = Block("Orphan", **flags, node_tree=self.tree)
        self.image = Block("Image", **{**flags, "users": 1}, filepath=str(self.file))
        self.tree.nodes = [types.SimpleNamespace(name="Texture", image=self.image)]
        self.user_map = {self.material: set(), self.tree: set(), self.image: {self.material}}
        self.bpy = types.SimpleNamespace(types=types.SimpleNamespace(ID=Block), path=types.SimpleNamespace(abspath=lambda path: path),
                                        data=types.SimpleNamespace(materials=[self.material], images=[self.image], objects=[], meshes=[], user_map=Mock(side_effect=lambda subset: {block: self.user_map[block] for block in subset if block in self.user_map})))
        self.ns["bpy"] = self.bpy
        self.content = {"packed_hashes": [], "pixel_sha256": None, "missing_data_sentinel": False, "file_sha256": self.ns["file_sha256"](self.file), "filepath": str(self.file)}

    def fingerprint(self):
        materials = {material.name: {"exact_material": material.name} for material in self.bpy.data.materials}
        images = {image.name: copy.deepcopy(self.content) for image in self.bpy.data.images}
        retention = self.ns["_promotion_material_retention"](materials)
        return {"sha256": {"materials": self.ns["_promotion_digest"](materials), "images": self.ns["_promotion_digest"](images), "geometry": "exact"},
                "material_retention": retention, "image_retention": self.ns["_promotion_image_retention"](images, retention)}

    def release(self):
        self.bpy.data.materials = []
        self.user_map[self.image] = set()
        self.image.users = 0
        return self.fingerprint()

    def compare(self, before, after):
        return self.ns["_promotion_reopen_comparison"](before, after)

    def test_surviving_orphan_image_proves_exact_content_and_released_consumers(self):
        before = self.fingerprint()
        after = self.release()
        result = self.compare(before, after)
        self.assertTrue(result["accepted"], result)
        proof = result["retained_images_with_released_orphan_consumers"][0]
        self.assertEqual(proof["name"], "Image")
        self.assertEqual(proof["before"], before["image_retention"]["inventory"]["Image"])
        self.assertEqual(proof["after"], after["image_retention"]["inventory"]["Image"])
        self.assertEqual(before["sha256"]["images"], after["sha256"]["images"])

    def test_packed_bytes_survive_exactly_but_packed_changes_fail(self):
        self.content.update(packed_hashes=["exact packed pixels"], file_sha256=None)
        before = self.fingerprint()
        after = self.release()
        self.assertTrue(self.compare(before, after)["accepted"])
        self.content["packed_hashes"] = ["changed packed pixels"]
        self.assertFalse(self.compare(before, self.fingerprint())["accepted"])
        self.content["packed_hashes"] = []
        self.assertFalse(self.compare(before, self.fingerprint())["accepted"])

    def test_any_image_datablock_loss_rejects_including_packed_orphan(self):
        for packed in ([], ["sole pixels"]):
            with self.subTest(packed=packed):
                self.content["packed_hashes"] = packed
                before = self.fingerprint()
                after = self.release()
                del after["image_retention"]["inventory"]["Image"]
                self.assertFalse(self.compare(before, after)["accepted"])

    def test_independent_retention_flags_consumers_and_count_reject(self):
        before = self.fingerprint()
        after = self.release()
        fields = {"users": [2, True], "fake_user": [True], "extra_user": [True], "protected": [True], "local": [False],
                  "other_id_consumers": [[{"name": "RetainedID"}]], "retained_node_trees": [[{"name": "Tree"}]],
                  "consumer_map_complete": [False], "material_consumers": [[], ["OtherMaterial"]]}
        for key, values in fields.items():
            for value in values:
                with self.subTest(key=key, value=value):
                    changed = copy.deepcopy(before)
                    changed["image_retention"]["inventory"]["Image"][key] = value
                    self.assertFalse(self.compare(changed, after)["accepted"])

    def test_collector_detects_other_id_same_owner_extra_reference_and_tree_retention(self):
        self.user_map[self.image].add(Block("OtherID"))
        self.assertFalse(self.fingerprint()["image_retention"]["inventory"]["Image"]["exclusive_orphan_consumers"])
        self.user_map[self.image] = {self.material}
        self.image.users = 2
        self.assertFalse(self.fingerprint()["image_retention"]["inventory"]["Image"]["exclusive_orphan_consumers"])
        self.image.users = 1
        self.user_map[self.tree] = {Block("RetainedTreeConsumer")}
        self.assertFalse(self.fingerprint()["image_retention"]["inventory"]["Image"]["exclusive_orphan_consumers"])

    def test_missing_native_map_entries_fail_closed(self):
        del self.user_map[self.image]
        with self.assertRaisesRegex(ValueError, "absent from the native ID user map"):
            self.fingerprint()

    def test_native_retention_flags_and_loaded_zero_user_tree_are_classified(self):
        self.tree.users = 0
        self.assertTrue(self.fingerprint()["image_retention"]["inventory"]["Image"]["exclusive_orphan_consumers"])
        for owner, key, value in ((self.image, "use_fake_user", True), (self.image, "use_extra_user", True),
                                  (self.tree, "users", 2), (self.tree, "is_embedded_data", False),
                                  (self.tree, "use_fake_user", True), (self.tree, "use_extra_user", True)):
            previous = getattr(owner, key)
            setattr(owner, key, value)
            with self.subTest(key=key):
                self.assertFalse(self.fingerprint()["image_retention"]["inventory"]["Image"]["exclusive_orphan_consumers"])
            setattr(owner, key, previous)
        for owner in (self.image, self.tree):
            for key in ("hoi4_source_protected", "hoi4_reference_read_only"):
                owner[key] = True
                self.assertFalse(self.fingerprint()["image_retention"]["inventory"]["Image"]["exclusive_orphan_consumers"])
                del owner[key]

    def test_shared_image_retained_material_and_multiple_node_users_are_counted(self):
        self.tree.nodes.append(types.SimpleNamespace(name="SecondTexture", image=self.image))
        self.image.users = 2
        self.assertTrue(self.fingerprint()["image_retention"]["inventory"]["Image"]["exclusive_orphan_consumers"])
        other_tree = Block("RetainedTree", users=1, use_fake_user=False, use_extra_user=False, is_embedded_data=True,
                           nodes=[types.SimpleNamespace(name="OtherTexture", image=self.image)])
        other = Block("RetainedMaterial", users=1, use_fake_user=True, use_extra_user=False, node_tree=other_tree)
        self.bpy.data.materials.append(other)
        self.user_map[other] = set()
        self.user_map[other_tree] = set()
        self.user_map[self.image].add(other)
        self.image.users = 3
        row = self.fingerprint()["image_retention"]["inventory"]["Image"]
        self.assertEqual(len(row["material_nodes"]), 3)
        self.assertFalse(row["exclusive_orphan_consumers"])

    def test_viewer_buffer_pixels_are_hashed_exactly_and_nonfinite_pixels_reject(self):
        image = Block("Viewer Node", size=[1, 1], packed_files=[], filepath="", has_data=True,
                      source="VIEWER", channels=4, pixels=[0.0, 0.25, 0.5, 1.0], alpha_mode="STRAIGHT",
                      colorspace_settings=types.SimpleNamespace(name="Linear"))
        record = self.ns["_promotion_image_record"](self.file.parent, image)
        image.pixels[1] = 0.26
        changed = self.ns["_promotion_image_record"](self.file.parent, image)
        self.assertNotEqual(record["pixel_sha256"], changed["pixel_sha256"])
        image.pixels[1] = float("nan")
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            self.ns["_promotion_image_record"](self.file.parent, image)

    def test_retained_material_cannot_release_image(self):
        self.material.use_fake_user = True
        self.material.users = 1
        before = self.fingerprint()
        self.assertFalse(before["image_retention"]["inventory"]["Image"]["exclusive_orphan_consumers"])
        self.assertFalse(self.compare(before, self.release())["accepted"])

    def test_consumer_release_requires_actual_material_removal(self):
        before = self.fingerprint()
        after = self.release()
        after["material_retention"] = before["material_retention"]
        after["sha256"]["materials"] = before["sha256"]["materials"]
        self.assertFalse(self.compare(before, after)["accepted"])

    def test_image_content_path_addition_or_new_consumer_changes_fail(self):
        before = self.fingerprint()
        after = self.release()
        for mode in ("content", "file_path", "file_hash", "consumer", "added", "image_hash"):
            changed = copy.deepcopy(after)
            row = changed["image_retention"]["inventory"]["Image"]
            if mode == "content":
                row["record_sha256"] = "changed"
            elif mode == "file_path":
                row["source_file"]["path"] = "changed"
            elif mode == "file_hash":
                row["source_file"]["sha256"] = "changed"
            elif mode == "consumer":
                row["id_consumers"] = [{"name": "Other"}]
            elif mode == "added":
                changed["image_retention"]["inventory"]["Added"] = row
            else:
                changed["sha256"]["images"] = "changed"
            with self.subTest(mode=mode):
                self.assertFalse(self.compare(before, changed)["accepted"])


if __name__ == "__main__":
    unittest.main()
