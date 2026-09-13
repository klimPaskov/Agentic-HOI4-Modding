"""Bounded independent explicit selections and strict normal/weight contracts."""
import copy
import importlib
import sys
import unittest
import hashlib
import json
import tempfile
import types
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'adapter'))
batch = importlib.import_module('explicit_batch_repair')


class BatchContracts(unittest.TestCase):
    def row(self, kind):
        row = dict(mesh='Mesh', rig='Rig', topology_sha256='A'*64, selection_sha256='B'*64, review_evidence='Reviewed exact source selection.')
        if kind == 'skin':
            row['vertices'] = [dict(index=3, expected={'Bone':1.0}, replacement={'Bone':.5,'Other':.5})]
        elif kind == 'winding':
            row.update(face_indices=[4,8], angular_tolerance_degrees=.5)
        else:
            row['corners'] = [dict(face_index=4, corner_index=2, vertex_index=3, expected_before=[0,0,1], requested_after=[1,0,0])]
        return row

    def validate(self, kind, rows=None):
        return batch.validate_specs({'meshes':rows or [self.row(kind)]}, kind)

    def test_three_disjoint_operations(self):
        for kind in batch.OPERATIONS.values():
            self.assertEqual(len(self.validate(kind)),1)
            row = self.row(kind)
            row['inferred_selection'] = True
            with self.assertRaises(ValueError): self.validate(kind,[row])

    def test_mesh_count_duplicate_and_empty(self):
        for kind in batch.OPERATIONS.values():
            row = self.row(kind)
            for rows in ([],[row,row],[dict(row,mesh='Mesh'+str(i)) for i in range(513)]):
                with self.assertRaises(ValueError): batch.validate_specs({'meshes':rows},kind)

    def test_selection_hash_required(self):
        for kind in batch.OPERATIONS.values():
            for bad in ('','G'*64,True,None):
                row = self.row(kind); row['selection_sha256']=bad
                with self.assertRaises(ValueError): self.validate(kind,[row])

    def test_no_winding_tolerance_relaxation(self):
        for value in (.50000001,0,-1,float('nan'),float('inf'),True):
            row = self.row('winding'); row['angular_tolerance_degrees']=value
            with self.assertRaises(ValueError): self.validate('winding',[row])

    def test_faces_explicit_unique_integer_bounded(self):
        for value in ([],[1,1],[True],[1.5],[-1],[1000000]):
            row = self.row('winding'); row['face_indices']=value
            with self.assertRaises(ValueError): self.validate('winding',[row])

    def test_skin_positive_normalized_existing_contract(self):
        for value in ({'Bone':0,'Other':1},{'Bone':1e-49,'Other':1},{'Bone':.8},{'Bone':float('nan')},{'A':.2,'B':.2,'C':.2,'D':.2,'E':.2}):
            row=self.row('skin'); row['vertices'][0]['replacement']=value
            with self.assertRaises(ValueError): self.validate('skin',[row])

    def test_skin_no_noops_or_duplicate_vertices(self):
        row=self.row('skin'); row['vertices'][0]['replacement']={'Bone':1}
        with self.assertRaises(ValueError): self.validate('skin',[row])
        row=self.row('skin'); row['vertices']*=2
        with self.assertRaises(ValueError): self.validate('skin',[row])

    def test_corner_explicit_unit_vectors_only(self):
        for value in ([0,0,0],[0,0,2],[0,0,float('nan')],[True,0,0],[0,0,1]):
            row=self.row('normals'); row['corners'][0]['requested_after']=value
            with self.assertRaises(ValueError): self.validate('normals',[row])

    def test_corner_unique_and_no_inferred_index(self):
        row=self.row('normals'); row['corners']*=2
        with self.assertRaises(ValueError): self.validate('normals',[row])
        for key in ('face_index','corner_index','vertex_index'):
            for value in (-1,True,1.5):
                row=self.row('normals'); row['corners'][0][key]=value
                with self.assertRaises(ValueError): self.validate('normals',[row])

    def test_aggregate_item_budget(self):
        rows=[dict(self.row('winding'),mesh='Mesh'+str(i),face_indices=list(range(100000))) for i in range(3)]
        with self.assertRaises(ValueError): self.validate('winding',rows)

    def test_source_spec_output_and_duplicate_json_guards(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            source=root/'source.blend'; source.write_bytes(b'immutable')
            spec=root/'spec.json'; spec.write_text(json.dumps({'meshes':[self.row('skin')]}))
            sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest().upper()
            def path(job,relative,suffix,missing=False):
                resolved=(job/relative).resolve()
                if resolved.parent!=job or resolved.suffix!=suffix or (not missing and not resolved.is_file()): raise ValueError('Path')
                return resolved
            def pairs(values):
                result={}
                for key,value in values:
                    if key in result: raise ValueError('Duplicate key')
                    result[key]=value
                return result
            api=types.SimpleNamespace(_promotion_path=path,file_sha256=sha,_promotion_unique_pairs=pairs,_promotion_digest=lambda v:json.dumps(v,allow_nan=False))
            req=dict(operation='repair_explicit_skin_batch',job_root=str(root),payload=dict(blend_rel='source.blend',checkpoint_rel='output.blend',expected_source_sha256=sha(source),repair_spec_rel='spec.json',expected_repair_spec_sha256=sha(spec)))
            self.assertEqual(batch.inputs(req,api)[0],'skin')
            for key in ('expected_source_sha256','expected_repair_spec_sha256'):
                bad=copy.deepcopy(req);bad['payload'][key]='0'*64
                with self.assertRaises(ValueError): batch.inputs(bad,api)
            (root/'output.blend').write_bytes(b'owned')
            with self.assertRaises(ValueError): batch.inputs(req,api)
            (root/'output.blend').unlink()
            spec.write_text('{"meshes":[],"meshes":[]}')
            req['payload']['expected_repair_spec_sha256']=sha(spec)
            with self.assertRaises(ValueError): batch.inputs(req,api)


if __name__ == '__main__': unittest.main()
