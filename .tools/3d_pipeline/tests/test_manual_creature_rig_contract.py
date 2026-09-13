"""Reject malformed declarative rig, geometry and motion input before Blender."""
import copy
import importlib.util
from pathlib import Path
import unittest

PATH=Path(__file__).parents[1]/"adapter/manual_creature_rig.py"
spec=importlib.util.spec_from_file_location("manual_creature_rig",PATH)
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


class ManualRigContracts(unittest.TestCase):
    def setUp(self):
        self.bones=[{"name":"root","parent":None,"head":[0,0,0],"tail":[0,0,1]}, {"name":"body","parent":"root","head":[0,0,1],"tail":[0,0,2]}]

    def test_bone_hierarchy_rejects_missing_parent_duplicate_and_zero_length(self):
        module.validate_bones(self.bones)
        for change in ({"parent":"missing"},{"name":"root"},{"tail":[0,0,1]}):
            rows=copy.deepcopy(self.bones); rows[1].update(change)
            with self.assertRaises(ValueError): module.validate_bones(rows)

    def test_regions_reject_opposite_unknown_chain_and_malformed_rigid_assignment(self):
        row={"name":"body_region","min":[-1,-1,0],"max":[1,1,2],"bones":["body"],"rigid":True}
        module.validate_regions([row],{"root","body"})
        for change in ({"bones":["missing"]},{"bones":["root","body"]},{"min":[2,2,2]},{"max":[float("nan"),1,2]}):
            broken=dict(row); broken.update(change)
            with self.assertRaises(ValueError): module.validate_regions([broken],{"root","body"})

    def test_component_rejects_open_nonmanifold_unused_and_degenerate_geometry(self):
        component={"name":"tool","bone":"body","material":"Material_0","vertices":[[0,0,0],[1,0,0],[0,1,0],[0,0,1]],"triangles":[[0,2,1],[0,1,3],[1,2,3],[2,0,3]],"loop_uvs":[[0,0]]*12}
        module.validate_component(component)
        for change in ({"triangles":component["triangles"][:-1]},{"vertices":component["vertices"]+[[2,2,2]]},{"triangles":[[0,0,1]]*4}):
            broken=copy.deepcopy(component); broken.update(change)
            with self.assertRaises(ValueError): module.validate_component(broken)

    def test_action_rejects_static_or_whole_rig_motion_and_bad_loops(self):
        action={"name":"test_idle","role":"idle","fps":30,"frame_start":0,"frame_end":30,"loop":True,"root_bone":"root","ground_contact":"per_frame_lowest_point_1mm","phases":[{"name":"start","frame":0},{"name":"breathe","frame":15},{"name":"end","frame":30}],"keys":{bone:[{"frame":f,"rotation_degrees":[v,0,0],"location":[0,0,0]} for f,v in [(0,0),(15,2),(30,0)]] for bone in ["spine","neck","head"]}}
        module.validate_action(action)
        static=copy.deepcopy(action)
        for rows in static["keys"].values():
            for row in rows: row["rotation_degrees"]=[0,0,0]
        with self.assertRaises(ValueError): module.validate_action(static)
        action["keys"]["head"][-1]["rotation_degrees"]=[1,0,0]
        with self.assertRaises(ValueError): module.validate_action(action)


if __name__=="__main__": unittest.main()
