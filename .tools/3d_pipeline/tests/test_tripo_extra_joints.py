"""Extra joints in a Tripo rig (lib/tripo_extra_joints.py): `neutral_bone`, a childless joint with no animation under the armature.

The rule runs on plain data, so these tests need no Blender. The synthetic GLB has the structure of the real export that stopped the intake
("Bone neutral_bone has no kept ancestor"), and one test reads that real export when it is present (it is not part of the kit)."""

from __future__ import annotations

import ast
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import rig_glb
from lib import tripo_extra_joints as extra

REAL_EXPORT = rig_glb.REAL_EXPORT

KEPT = {"Hips", "Spine", "Head"}
PARENTS = {"Hips": None, "Spine": "Hips", "Head": "Spine", "Finger": "Head", "neutral_bone": None}


class Rule(unittest.TestCase):
    def test_a_childless_unanimated_joint_with_no_kept_ancestor_is_extra(self) -> None:
        self.assertEqual(extra.find_extra_joints(PARENTS, KEPT, animated=set()), ["neutral_bone"])

    def test_a_joint_under_a_kept_bone_is_never_extra(self) -> None:
        # the finger merges into the head as before
        self.assertNotIn("Finger", extra.find_extra_joints(PARENTS, KEPT, animated=set()))

    def test_a_rig_without_the_joint_has_no_extras(self) -> None:
        self.assertEqual(extra.find_extra_joints({"Hips": None, "Spine": "Hips"}, {"Hips", "Spine"}, set()), [])

    def test_an_animated_orphan_stops_the_intake_and_names_it(self) -> None:
        with self.assertRaisesRegex(extra.ExtraJointError, "neutral_bone"):
            extra.find_extra_joints(PARENTS, KEPT, animated={"neutral_bone"})

    def test_an_orphan_with_a_child_stops_the_intake(self) -> None:
        parents = dict(PARENTS, neutral_child="neutral_bone")
        with self.assertRaisesRegex(extra.ExtraJointError, "neutral_bone"):
            extra.find_extra_joints(parents, KEPT, animated=set())

    def test_the_mixamo_prefix_and_the_optional_bones_count_as_kit_bones(self) -> None:
        self.assertTrue(extra.is_kit_bone("mixamorig:Hips"))
        self.assertTrue(extra.is_kit_bone("mixamorig1:LeftToeBase"))
        self.assertTrue(extra.is_kit_bone("mixamorig:Weapon"))
        self.assertFalse(extra.is_kit_bone("mixamorig:LeftHandIndex1"))
        self.assertFalse(extra.is_kit_bone("neutral_bone"))


class Weights(unittest.TestCase):
    SEGMENTS = {"Hips": ((0.0, 1.0, 0.0), (0.0, 1.3, 0.0)), "Head": ((0.0, 1.7, 0.0), (0.0, 1.7, 0.0)), "Foot": ((0.1, 0.0, 0.0), (0.1, 0.1, 0.0))}

    def test_the_nearest_kept_bone_is_found_by_the_distance_to_its_segment(self) -> None:
        self.assertEqual(extra.nearest_kept_bone((0.0, 1.15, 0.05), self.SEGMENTS, "Hips", 0.5), "Hips")
        self.assertEqual(extra.nearest_kept_bone((0.0, 1.65, 0.0), self.SEGMENTS, "Hips", 0.5), "Head")
        self.assertEqual(extra.nearest_kept_bone((0.12, 0.02, 0.0), self.SEGMENTS, "Hips", 0.5), "Foot")

    def test_a_vertex_far_from_every_kit_bone_goes_to_the_hips(self) -> None:
        self.assertEqual(extra.nearest_kept_bone((5.0, 5.0, 5.0), self.SEGMENTS, "Hips", 0.5), "Hips")

    def test_weights_move_by_the_vertex_position_and_the_count_is_reported(self) -> None:
        rows = [{"Head": 0.6, "neutral_bone": 0.4}, {"Foot": 1.0}, {"Foot": 0.7, "neutral_bone": 0.3}, {"Hips": 0.5, "neutral_bone": 0.0, "Head": 0.5}]
        points = [(0.0, 1.69, 0.0), (0.1, 0.05, 0.0), (0.1, 0.05, 0.0), (0.0, 1.1, 0.0)]
        moved = extra.move_extra_weights(rows, ["neutral_bone"], points, self.SEGMENTS, "Hips", 0.5)
        self.assertEqual(moved, 2, "a zero weight is not a move")
        self.assertEqual(rows[0], {"Head": 1.0})
        self.assertAlmostEqual(rows[2]["Foot"], 1.0)
        self.assertNotIn("neutral_bone", rows[3])
        for row in rows:
            self.assertAlmostEqual(sum(row.values()), 1.0)

    def test_the_report_line_names_the_joints_and_the_count(self) -> None:
        self.assertEqual(extra.report_line(["neutral_bone"], 3), "extra joints dropped: neutral_bone (1 joint, 3 vertex weights moved to the nearest kit bone)")
        self.assertIn("1 vertex weight moved", extra.report_line(["neutral_bone"], 1))
        self.assertEqual(extra.report_line([], 0), "extra joints dropped: none")


class SyntheticExport(unittest.TestCase):
    """A GLB built like the real export: a `tripo_node_<id>` mesh, the Hips chain, and `neutral_bone` under the armature."""

    def build(self, **options):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "unit__rigged.glb"
        return path, rig_glb.write_rig_glb(path, **options)

    def test_the_extra_joint_is_found_and_its_weight_moves_to_the_head(self) -> None:
        path, info = self.build()
        plan = extra.plan_from_glb(path)
        self.assertEqual(plan["extras"], ["neutral_bone"])
        self.assertEqual(plan["moved"], 1)
        self.assertEqual(plan["targets"], {"neutral_bone": {"mixamorig:Head": 1}})
        row = plan["rows"][info["vertex"]]
        self.assertAlmostEqual(row["mixamorig:Head"], 1.0)
        self.assertNotIn("neutral_bone", row)
        self.assertEqual(plan["line"], "extra joints dropped: neutral_bone (1 joint, 1 vertex weight moved to the nearest kit bone)")

    def test_the_weight_goes_where_the_vertex_is_not_where_the_joint_was(self) -> None:
        # the vertex sits beside the thigh: its weight on neutral_bone must go to the thigh, not to the hips or the head
        path, _info = self.build(extra_position=(0.2, 0.7, 0.0))
        plan = extra.plan_from_glb(path)
        self.assertEqual(list(plan["targets"]["neutral_bone"]), ["mixamorig:LeftUpLeg"])

    def test_a_vertex_far_from_the_body_goes_to_the_hips(self) -> None:
        # 18 units above the head: the head is the nearest bone, but it is farther than a quarter of the body's extent
        path, _info = self.build(extra_position=(0.0, 20.0, 0.0))
        plan = extra.plan_from_glb(path)
        self.assertEqual(list(plan["targets"]["neutral_bone"]), ["mixamorig:Hips"])

    def test_an_export_without_the_joint_changes_nothing(self) -> None:
        path, _info = self.build(extra_joint=None)
        plan = extra.plan_from_glb(path)
        self.assertEqual((plan["extras"], plan["moved"]), ([], 0))
        self.assertEqual(plan["line"], "extra joints dropped: none")

    def test_a_joint_with_zero_weight_is_dropped_and_moves_nothing(self) -> None:
        path, _info = self.build(extra_weight=0.0)
        plan = extra.plan_from_glb(path)
        self.assertEqual((plan["extras"], plan["moved"]), (["neutral_bone"], 0))

    def test_an_animated_extra_joint_is_refused(self) -> None:
        path, _info = self.build(extra_animated=True)
        with self.assertRaisesRegex(extra.ExtraJointError, "neutral_bone"):
            extra.plan_from_glb(path)

    def test_a_joint_whose_channels_hold_one_value_is_still_extra(self) -> None:
        # the grip stage's export writes a constant key per clip for neutral_bone: it moves nothing, so it is dropped (gap 18)
        path, _info = self.build(extra_constant=True)
        plan = extra.plan_from_glb(path)
        self.assertEqual(plan["extras"], ["neutral_bone"])

    def test_an_extra_joint_with_a_child_is_refused(self) -> None:
        path, _info = self.build(extra_children=True)
        with self.assertRaisesRegex(extra.ExtraJointError, "neutral_bone"):
            extra.plan_from_glb(path)

    def test_the_skeleton_reader_matches_the_file(self) -> None:
        path, info = self.build()
        skeleton = extra.read_skeleton(path)
        self.assertIsNone(skeleton["parents"]["neutral_bone"])
        self.assertEqual(skeleton["parents"]["mixamorig:Head"], "mixamorig:Spine")
        self.assertEqual(skeleton["animated"], {"mixamorig:Hips", "mixamorig:Spine"})
        for got, wanted in zip(skeleton["heads"]["mixamorig:Head"], (0.0, 1.7, 0.0)):
            self.assertAlmostEqual(got, wanted, places=6)
        self.assertEqual(len(skeleton["points"]), 4 * len(rig_glb.CHAIN))


class RealExport(unittest.TestCase):
    @unittest.skipUnless(REAL_EXPORT.is_file(), "the real Tripo export that carries neutral_bone is not on this machine")
    def test_the_real_export_has_one_extra_joint_and_every_other_joint_has_a_kept_ancestor(self) -> None:
        skeleton = extra.read_skeleton(REAL_EXPORT)
        kept = {name for name in skeleton["parents"] if extra.is_kit_bone(name)}
        self.assertEqual(len(skeleton["parents"]), 66)
        self.assertEqual(extra.find_extra_joints(skeleton["parents"], kept, skeleton["animated"]), ["neutral_bone"])
        plan = extra.plan_from_glb(REAL_EXPORT)
        self.assertEqual(plan["extras"], ["neutral_bone"])
        self.assertIsNone(skeleton["parents"]["neutral_bone"])
        self.assertEqual(skeleton["children"]["neutral_bone"], [])
        self.assertNotIn("neutral_bone", skeleton["animated"])
        # whatever weight the joint carries lands on a kit bone, and each row stays normalised
        self.assertTrue(all(name in kept for target in plan["targets"].values() for name in target))
        self.assertTrue(all(abs(sum(row.values()) - 1.0) < 1e-4 for row in plan["rows"]))
        self.assertTrue(all("neutral_bone" not in row for row in plan["rows"]))
        self.assertEqual(plan["moved"], sum(sum(target.values()) for target in plan["targets"].values()))


class ReadersBeforeBlender(unittest.TestCase):
    """The intake's Python-side readers of the rig (the hips travel, the loop windows, the still tails) run before Blender and must read an
    export that carries `neutral_bone` as they read any other."""

    ROLES = {"idle": "idle", "move": "walk", "attack": "box_01", "defend": "hit_to_body_01", "retreat": "flee_01", "death": "fall"}

    @unittest.skipUnless(REAL_EXPORT.is_file(), "the real Tripo export that carries neutral_bone is not on this machine")
    def test_the_real_export_is_read_by_the_intake_before_blender(self) -> None:
        from lib import glb_root, tripo_loop, tripo_trim

        self.assertEqual(glb_root.travelling_clips(REAL_EXPORT, self.ROLES.values()), {})
        windows = tripo_loop.auto_windows(REAL_EXPORT, self.ROLES)
        self.assertEqual(sorted(windows), ["move", "retreat"])
        trims = tripo_trim.auto_trims(REAL_EXPORT, self.ROLES)
        self.assertLessEqual(set(trims), {"attack", "defend", "retreat"})

    def test_the_synthetic_export_is_read_the_same_way(self) -> None:
        from lib import glb_root

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "unit__rigged.glb"
            rig_glb.write_rig_glb(path)
            self.assertEqual(glb_root.travelling_clips(path, ["idle", "walk"]), {})
            self.assertEqual(sorted(glb_root.root_travel(path)), ["idle", "walk"])


class BlenderStageWiring(unittest.TestCase):
    """prepare_tripo_unit.py runs only inside Blender, so its use of the rule is read from its source."""

    SOURCE = (PIPELINE / "tripo" / "prepare_tripo_unit.py").read_text(encoding="utf-8")

    def test_the_stage_drops_the_extra_joints_and_reports_them(self) -> None:
        self.assertIn("tripo_extra_joints.find_extra_joints(parents, set(keep), animated)", self.SOURCE)
        self.assertIn("tripo_extra_joints.move_extra_weights(", self.SOURCE)
        self.assertIn('"extra_joints": {"dropped": extra_joints, "weights_moved": weights_moved}', self.SOURCE)
        self.assertNotIn('raise SystemExit(f"Bone {bone.name} has no kept ancestor")', self.SOURCE)

    def test_the_report_names_the_extra_joints_not_the_per_step_record(self) -> None:
        """`extras` in main() is the per-step record of the role clips (a dict). The first Blender run of this change reported that dict as the
        dropped joints, because the joints had been bound to the same name."""

        main = next(node for node in ast.parse(self.SOURCE).body if isinstance(node, ast.FunctionDef) and node.name == "main")
        bound = [ast.unparse(target) for node in ast.walk(main) if isinstance(node, ast.Assign) for target in node.targets]
        self.assertEqual(bound.count("extras"), 1)
        self.assertIn("(keep, merge_into, dropped, extra_joints)", bound)

    def test_the_kit_bones_come_from_the_shared_module(self) -> None:
        tree = ast.parse(self.SOURCE)
        assigned = {target.id: node.value for node in tree.body if isinstance(node, ast.Assign) for target in node.targets if isinstance(target, ast.Name)}
        self.assertIn("MIXAMO_KIT_BONES", ast.unparse(assigned["KIT_BONES"]))
        self.assertEqual(len(extra.MIXAMO_KIT_BONES), 22)


if __name__ == "__main__":
    unittest.main()
