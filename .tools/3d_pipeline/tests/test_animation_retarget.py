"""Retarget world/rest basis regressions; live module, no Blender or provider calls."""
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'adapter'))
from retarget_root_motion import vertical_root_basis_location, conjugate_rotation, angular_motion_retained

class RootRetargetTests(unittest.TestCase):
    def test_rotated_scaled_root_world_vertical_and_in_place(self):
        # Armature world scale 2; rest root rotates local Y onto world Z.
        basis = ((2,0,0),(0,0,-2),(0,2,0))
        local = vertical_root_basis_location((8,9,-4),(1,2,0),basis)
        self.assertEqual(local, (0,-2,0))
        world = [sum(row[i]*local[i] for i in range(3)) for row in basis]
        self.assertEqual(world, [0,0,-4])
    def test_anatomical_world_ratio_applied_once(self):
        source_delta = -0.5; measured_world_ratio = 4
        local = vertical_root_basis_location((0,0,source_delta*measured_world_ratio),(0,0,0),((2,0,0),(0,2,0),(0,0,2)))
        self.assertEqual(local,(0,0,-1))
    def test_rotated_source_and_target_object_bases(self):
        h=math.sqrt(.5)
        mapped = conjugate_rotation((h,h,0,0),(h,0,0,h),(1,0,0,0))
        for actual,wanted in zip(mapped,(h,0,h,0)): self.assertAlmostEqual(actual,wanted)
        identity = conjugate_rotation((h,h,0,0),(h,0,0,h),(h,0,0,h))
        for actual,wanted in zip(identity,(h,h,0,0)): self.assertAlmostEqual(actual,wanted)
    def test_motion_gate_uses_angles_not_raw_source_translation_units(self):
        # Native pilot has hundreds of source centimeters versus calibrated target units.
        # Neither magnitude is accepted by this angular-only contract.
        self.assertTrue(angular_motion_retained(17.5,17.49999))
        self.assertFalse(angular_motion_retained(17.5,0.0))
        self.assertTrue(angular_motion_retained(0.0,0.0))
        with self.assertRaises(ValueError): angular_motion_retained(float('nan'),1.0)
    def test_explicit_evaluated_frame_bounds(self):
        import ast
        source=Path(__file__).resolve().parents[1] / 'adapter/blender_worker.py'
        fn=next(node for node in ast.parse(source.read_text(encoding='utf-8')).body if isinstance(node,ast.FunctionDef) and node.name=='validate_evaluated_frames')
        namespace={'math':math}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'live_frame_validator','exec'),namespace)
        validate=namespace['validate_evaluated_frames']
        self.assertEqual(validate(list(range(1,91)),1,90),list(range(1,91)))
        for invalid in ([0],[91],[1,1],[True],[],list(range(242))):
            with self.assertRaises(ValueError): validate(invalid,1,90)
    def test_death_requires_articulation_but_allows_terminal_hold(self):
        import ast
        from types import SimpleNamespace
        source=Path(__file__).resolve().parents[1] / 'adapter/blender_worker.py'
        tree=ast.parse(source.read_text(encoding='utf-8'))
        functions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in {'_action_phase_delta','_action_phase_motion'}]
        namespace={'Dict':dict,'Any':object}
        exec(compile(ast.Module(body=functions,type_ignores=[]),'live_phase_motion','exec'),namespace)
        phases=('standing','falling','impact','rebound','settling','terminal_hold')
        def record(angle):
            c=math.cos(angle); z=math.sin(angle)
            return {'bones': {'Joint': {'basis': [[c,-z,0,0],[z,c,0,0],[0,0,1,0],[0,0,0,1]]}}}
        before={phase:record(0) for phase in phases}
        after={phase:record(angle) for phase,angle in zip(phases,(0,.2,.4,.5,.6,.6))}
        context={'allowed_bones':['Joint'],'semantic_role':'death','motion_bone_chain':[]}
        rig=SimpleNamespace(data=SimpleNamespace(bones={'Joint':SimpleNamespace(parent=object())}))
        proof=namespace['_action_phase_motion'](context,rig,before,after)
        self.assertEqual(len(proof['phase_transitions']),4)
        after['rebound']=after['impact']
        with self.assertRaises(ValueError):namespace['_action_phase_motion'](context,rig,before,after)
    def test_invalid_matrices_and_quaternions(self):
        with self.assertRaises(ValueError): vertical_root_basis_location((0,0,1),(0,0,0),((0,0,0),)*3)
        with self.assertRaises(ValueError): vertical_root_basis_location((0,0,float('nan')),(0,0,0),((1,0,0),(0,1,0),(0,0,1)))
        with self.assertRaises(ValueError): conjugate_rotation((0,0,0,0),(1,0,0,0),(1,0,0,0))

if __name__ == '__main__': unittest.main()
