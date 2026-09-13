"""Pure declarative repair guards; native Blender acceptance is separate."""

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "adapter/fitted_humanoid_repair.py"
LOADER = importlib.util.spec_from_file_location("fitted_humanoid_repair", MODULE)
repair = importlib.util.module_from_spec(LOADER)
LOADER.loader.exec_module(repair)


def rig_spec():
    return {"schema_version": "1.0.0", "author": "gpt-5.6-sol", "acceptance_basis": "Approved preservation-only repair.",
            "source_mesh_name": "Source.001", "output_mesh_name": "Body", "rig_name": "Rig",
            "bones": [{"name": f"Bone{i}", "head": [0, 0, i], "tail": [0, 0, i + 1],
                       "parent": None if i == 0 else f"Bone{i-1}", "roll": 0} for i in range(16)],
            "weight_regions": [{"name": "all", "selection": {"aabb": {"min": [-10, -10, -10], "max": [10, 10, 20]}},
                                "skin": {"weights": {"Bone0": 1}}}], "ik_chains": []}


def action_spec(role="attack"):
    phases = {name: 3 * index for index, name in enumerate(repair.ROLES[role])}
    end = max(12, max(phases.values()))
    return {"schema_version": "1.0.0", "author": "gpt-5.6-sol", "acceptance_basis": "Approved manual role keys.",
            "rig_name": "Rig", "mesh_name": "Body", "action_name": "Test_" + role, "role": role,
            "fps": 24, "frame_start": 0, "frame_end": end, "loop": False, "phases": phases,
            "bone_keys": {name: [{"frame": 0, "rotation_xyz_deg": [0, 0, 0], "location": [0, 0, 0]},
                                  {"frame": end, "rotation_xyz_deg": [value, 0, 0], "location": [0, 0, 0]}]
                          for name, value in (("Bone0", 3), ("Bone1", 7))},
            "grounding": "none", "contact_bones": []}


class FittedRepairContracts(unittest.TestCase):
    def test_actual_author_is_not_pinned_to_a_source_project_model(self):
        for build, validate in ((rig_spec, repair.validate_rig_spec), (action_spec, repair.validate_action_spec)):
            for author in ("gpt-5.6-sol", "manual-artist"):
                target = build()
                target["author"] = author
                self.assertEqual(validate(target)["author"], author)
            for author in (None, 123, "", "   ", "x" * 129):
                target = build()
                target["author"] = author
                with self.subTest(author=author), self.assertRaises(ValueError):
                    validate(target)

    def test_good_explicit_rig_and_all_nine_role_schemas(self):
        self.assertEqual(repair.validate_rig_spec(rig_spec())["rig_name"], "Rig")
        for role in repair.ROLES:
            self.assertEqual(repair.validate_action_spec(action_spec(role))["role"], role)

    def test_source_sha_spec_sha_new_sibling_and_immutable_input(self):
        with tempfile.TemporaryDirectory() as directory:
            job = Path(directory).resolve()
            (job / "checkpoints").mkdir()
            source = job / "checkpoints/source.blend"
            source.write_bytes(b"native-fixture-marker")
            spec = job / "rig.json"
            spec.write_text(json.dumps(rig_spec()), encoding="utf-8")
            payload = {"blend_rel": "checkpoints/source.blend", "expected_source_sha256": repair.digest(source),
                       "spec_rel": "rig.json", "expected_spec_sha256": repair.digest(spec), "checkpoint_rel": "checkpoints/result.blend"}
            req = {"job_root": str(job), "payload": payload}
            self.assertEqual(repair._inputs(req, True)[3], job / "checkpoints/result.blend")
            for key, value in (("blend_rel", "../source.blend"), ("blend_rel", str(source)),
                               ("checkpoint_rel", "checkpoints/source.blend"), ("checkpoint_rel", "elsewhere/result.blend"),
                               ("checkpoint_rel", "https://invalid/result.blend"), ("checkpoint_rel", "checkpoints/result.py"),
                               ("expected_source_sha256", "0" * 64), ("expected_spec_sha256", "0" * 64)):
                changed = {"job_root": str(job), "payload": {**payload, key: value}}
                with self.subTest(key=key, value=value), self.assertRaises((ValueError, FileNotFoundError)):
                    repair._inputs(changed, True)
            self.assertEqual(source.read_bytes(), b"native-fixture-marker")

    def test_reject_unknown_fields_code_and_identifiers(self):
        for target, key, value in ((rig_spec(), "script", "print('forbidden')"), (action_spec(), "expression", "sin(frame)"),
                                   (rig_spec(), "rig_name", "../Rig"), (action_spec(), "action_name", "a\nscript")):
            target[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                (repair.validate_rig_spec if "bones" in target else repair.validate_action_spec)(target)

    def test_reject_unbounded_vectors_nan_duplicate_and_unordered_bones(self):
        for field, value in (("head", [float("nan"), 0, 0]), ("tail", [0, 0, 0]), ("head", [True, 0, 0]),
                             ("parent", "Absent"), ("roll", 100)):
            target = rig_spec()
            target["bones"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                repair.validate_rig_spec(target)
        target = rig_spec()
        target["bones"][1]["name"] = "Bone0"
        with self.assertRaises(ValueError):
            repair.validate_rig_spec(target)

    def test_reject_bad_weight_selections_and_skin_rules(self):
        for selection in ({"vertex_indices": [-1]}, {"vertex_indices": [1, 1]}, {"vertex_indices": [True]},
                          {"aabb": {"min": [1, 0, 0], "max": [0, 0, 0]}}, {"expression": "z > 1"}):
            target = rig_spec()
            target["weight_regions"][0]["selection"] = selection
            with self.subTest(selection=selection), self.assertRaises(ValueError):
                repair.validate_rig_spec(target)
        for skin in ({"weights": {"Bone0": 0.5}}, {"weights": {"Absent": 1}}, {"weights": {"Bone0": -1, "Bone1": 2}},
                     {"nearest_segments": {"bones": ["Bone0"], "influences": 5, "softening": 0.1, "power": 2}}):
            target = rig_spec()
            target["weight_regions"][0]["skin"] = skin
            with self.subTest(skin=skin), self.assertRaises(ValueError):
                repair.validate_rig_spec(target)

    def test_reject_static_alias_whole_root_only_and_bad_loop(self):
        for count in (0, 1):
            target = action_spec()
            for name in list(target["bone_keys"])[count:]:
                target["bone_keys"][name][1]["rotation_xyz_deg"] = [0, 0, 0]
            with self.subTest(moving_bones=count), self.assertRaises(ValueError):
                repair.validate_action_spec(target)
        target = action_spec()
        target["loop"] = True
        with self.assertRaises(ValueError):
            repair.validate_action_spec(target)

    def test_reject_wrong_role_phases_and_key_bounds(self):
        for field, value in (("phases", {"ready": 0}), ("role", "generic"), ("fps", 120), ("frame_end", 1000),
                             ("grounding", "eval(expression)")):
            target = action_spec()
            target[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                repair.validate_action_spec(target)
        target = action_spec()
        target["bone_keys"]["Bone0"][1]["frame"] = 999
        with self.assertRaises(ValueError):
            repair.validate_action_spec(target)

    def test_approved_region_overrides_allow_explicit_vertex_evidence(self):
        target = rig_spec()
        target["weight_regions"].append({"name": "hand", "selection": {"vertex_indices": [1, 3, 7]}, "skin": {"weights": {"Bone3": 0.25, "Bone4": 0.75}}})
        target["weight_regions"].append({"name": "forearm", "selection": {"vertex_indices": [10]},
                                         "skin": {"nearest_segments": {"bones": ["Bone3", "Bone4"], "influences": 2, "softening": 0.05, "power": 4}}})
        self.assertEqual(len(repair.validate_rig_spec(target)["weight_regions"]), 3)

    def test_explicit_existing_pole_parent_accepts_without_changing_bones(self):
        target = rig_spec()
        target["bones"][9]["parent"] = "Bone2"
        before = copy.deepcopy(target["bones"])
        target["ik_chains"] = [{"forearm": "Bone6", "target_hand": "Bone9", "pole": [1, 2, 3], "pole_angle": 0, "pole_parent_bone": "Bone2"}]
        repair.validate_rig_spec(target)
        self.assertEqual(target["bones"], before)
        target["ik_chains"][0]["pole_parent_bone"] = "Absent"
        with self.assertRaises(ValueError):
            repair.validate_rig_spec(target)
        target["ik_chains"][0]["pole_parent_bone"] = "Bone6"
        with self.assertRaises(ValueError):
            repair.validate_rig_spec(target)


if __name__ == "__main__":
    unittest.main()
