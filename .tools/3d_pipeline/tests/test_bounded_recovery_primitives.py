"""Live adapter regressions; no Blender process, draft modules, or extra dependencies.

Run: python .tools/3d_pipeline/tests/test_adapter_recovery_release.py
Native Blender receipts remain the integration proof recorded in the handoff.
"""
import ast
import copy
import hashlib
import json
from pathlib import Path
import struct
import sys
import sysconfig
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
ADAPTER = ROOT / '.tools/3d_pipeline/adapter'
sys.path.insert(0, str(ADAPTER))
import assembly_yaw
import animation_root_export
import explicit_vertex_remap
import manual_creature_rig
import mesh_winding_repair


class NormalAndTextureRegressions(unittest.TestCase):
    def test_measured_native_normal_encoding(self):
        fixtures = [
            ((1565, 913), (.57055509, .82110113, .01611498),
             (.57549489, .81774521, .00991349), .49, .50),
            ((25653, 7901), (.16119699, .65631938, -.73706198),
             (.15955687, .65305221, -.74031383), .28, .29),
        ]
        for corner, wanted, actual, lower, upper in fixtures:
            with self.subTest(corner=corner), patch.object(
                    mesh_winding_repair, '_corner_normals', return_value={corner: actual}):
                with self.assertRaises(RuntimeError):
                    mesh_winding_repair._verify_normal_signs(None, {corner: wanted}, set())
                proof = mesh_winding_repair._verify_normal_signs(
                    None, {corner: wanted}, set(), angular_tolerance_degrees=.5)
                self.assertGreater(proof['maximum_angle_degrees'], lower)
                self.assertLess(proof['maximum_angle_degrees'], upper)
                self.assertEqual(proof['worst_corner']['face_vertex'], corner)
                self.assertFalse(proof['worst_corner']['selected_face'])

    def test_selected_sign_nonunit_direction_and_zero_rejection(self):
        with patch.object(mesh_winding_repair, '_corner_normals', return_value={(1, 2): (-1, 0, 0)}):
            proof = mesh_winding_repair._verify_normal_signs(None, {(1, 2): (.02, 0, 0)}, {1})
            self.assertEqual(proof['maximum_angle_degrees'], 0)
            self.assertEqual(proof['source_nonunit_normal_count'], 1)
            with self.assertRaises(RuntimeError):
                mesh_winding_repair._verify_normal_signs(None, {(1, 2): (0, 0, 0)}, {1})
            with self.assertRaises(RuntimeError):
                mesh_winding_repair._verify_normal_signs(None, {(1, 2): (0, 1, 0)}, {1})

    def test_2048_body_budget_keeps_component_default_and_payload_guard(self):
        header = bytearray(128)
        header[:4] = b'DDS '
        struct.pack_into('<I', header, 4, 124)
        struct.pack_into('<II', header, 12, 2048, 2048)
        struct.pack_into('<I', header, 76, 32)
        struct.pack_into('<I4sIIIII', header, 80, 0x41, b'\0'*4, 32,
                         0x00ff0000, 0x0000ff00, 0x000000ff, 0xff000000)
        size = 128 + 2048*2048*4
        with self.assertRaises(ValueError):
            manual_creature_rig.validate_component_dds(header, size)
        self.assertEqual(manual_creature_rig.validate_component_dds(
            header, size, max_dimension=2048), (2048, 2048))
        with self.assertRaises(ValueError):
            manual_creature_rig.validate_component_dds(header, size-1, max_dimension=2048)


class ExactRemapRegressions(unittest.TestCase):
    def setUp(self):
        self.positions = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
        self.weights = [[(0, 1.0)] for _ in self.positions]
        self.faces = [[0, 1, 2], [0, 2, 3]]
        self.spec = {
            'mesh_name': 'Body', 'target_armature_name': 'Rig',
            'split_vertices': [{'name': 'fan', 'source_vertex': 0}],
            'corner_remaps': [{'face_index': 0, 'source_vertex': 0, 'target_vertex': 'fan'}],
            'remove_unused_vertices': [], 'triangle_ceiling': 100,
        }

    def validate(self):
        return explicit_vertex_remap.validate_remap(
            self.spec, self.positions, self.weights, self.faces)

    def alias_fixture(self):
        self.positions.append([0, 0, 0])
        self.weights.append([(0, 1.0)])
        self.faces[0][0] = 4
        self.spec.update(split_vertices=[], corner_remaps=[
            {'face_index': 0, 'source_vertex': 4, 'target_vertex': 0}],
            remove_unused_vertices=[4])

    def test_exact_fan_split(self):
        sources, changed, removed = self.validate()
        self.assertEqual(sources['fan'], 0)
        self.assertEqual(changed[0], ['fan', 1, 2])
        self.assertEqual(removed, set())

    def test_exact_coincident_alias(self):
        self.alias_fixture()
        self.assertEqual(self.validate()[2], {4})

    def test_alias_position_drift_rejected(self):
        self.alias_fixture()
        self.positions[4][0] = .00001
        with self.assertRaises(ValueError):
            self.validate()

    def test_alias_weight_drift_rejected(self):
        self.alias_fixture()
        self.weights[4] = [(1, 1.0)]
        with self.assertRaises(ValueError):
            self.validate()

    def test_duplicate_corner_and_connected_removal_rejected(self):
        original = copy.deepcopy(self.spec)
        for change in ({'corner_remaps': original['corner_remaps']*2},
                       {'remove_unused_vertices': [1]},
                       {'split_vertices': original['split_vertices']*2}):
            self.spec = {**copy.deepcopy(original), **change}
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.validate()


class YawRegressions(unittest.TestCase):
    def setUp(self):
        self.payload = {'yaw_degrees': 90, 'object_names': ['Rig', 'Body'],
                        'action_names': ['Idle', 'Move'], 'target_armature_name': 'Rig'}

    def test_cardinal_yaw(self):
        self.assertEqual(assembly_yaw.validate_yaw(self.payload), 90)

    def test_noncardinal_nonfinite_boolean_rejected(self):
        for angle in [True, float('nan'), 360, 45, 0]:
            with self.subTest(angle=angle), self.assertRaises(ValueError):
                assembly_yaw.validate_yaw({**self.payload, 'yaw_degrees': angle})

    def test_explicit_rig_and_unique_objects_required(self):
        for objects in [['Body'], ['Rig', 'Rig'], []]:
            with self.subTest(objects=objects), self.assertRaises(ValueError):
                assembly_yaw.validate_yaw({**self.payload, 'object_names': objects})


class ExportedRootRegressions(unittest.TestCase):
    def fixture(self):
        tree = ET.Element('File')
        info = ET.SubElement(tree, 'info')
        info.set('j', [2])
        root = ET.SubElement(info, 'Root')
        for key, values in {'t': [0., 0., 0.], 'q': [0., 0., 0., 1.], 's': [1.], 'sa': ['']}.items():
            root.set(key, values)
        child = ET.SubElement(info, 'Body')
        child.set('t', [1., 2., 3.])
        child.set('q', [0., 0., 0., 1.])
        samples = ET.SubElement(tree, 'samples')
        samples.set('q', [0., 0., 0., 1., .5, .5, .5, .5])
        expected = {'Root': {'t': [0., 0., .001], 'q': [0., 2**-.5, 0., 2**-.5]}}
        return tree, expected

    def test_constant_yaw_root_and_serialized_readback_preserve_samples(self):
        tree, expected = self.fixture()
        before_samples = copy.deepcopy(tree.find('samples').attrib)
        before_child = copy.deepcopy(tree.find('info').find('Body').attrib)
        proof = animation_root_export.align_initial_root_records(tree, expected)
        self.assertEqual(set(proof['changes']), {'Root'})
        node = tree.find('info').find('Root')
        for field in ('t', 'q'):
            node.set(field, [struct.unpack('<f', struct.pack('<f', v))[0] for v in node.get(field)])
        animation_root_export.verify_initial_root_records(tree, expected, proof['retained_fields_sha256'])
        self.assertEqual(tree.find('samples').attrib, before_samples)
        self.assertEqual(tree.find('info').find('Body').attrib, before_child)

    def test_already_aligned_initial_root_is_noop(self):
        tree, expected = self.fixture()
        animation_root_export.align_initial_root_records(tree, expected)
        self.assertEqual(animation_root_export.align_initial_root_records(tree, expected)['changes'], {})

    def test_sample_change_is_rejected(self):
        tree, expected = self.fixture()
        proof = animation_root_export.align_initial_root_records(tree, expected)
        tree.find('samples').set('q', [1., 0., 0., 0.])
        with self.assertRaises(RuntimeError):
            animation_root_export.verify_initial_root_records(tree, expected, proof['retained_fields_sha256'])

    def test_missing_root_and_nonunit_quaternion_rejected(self):
        for bad in ({'Unknown': {'t': [0., 0., 0.], 'q': [0., 0., 0., 1.]}},
                    {'Root': {'t': [0., 0., 0.], 'q': [0., 0., 0., 2.]}}):
            tree, _ = self.fixture()
            with self.assertRaises(ValueError):
                animation_root_export.align_initial_root_records(tree, bad)

if __name__ == '__main__':
    unittest.main()
