"""Align exported initial root transforms with locked world-space animation samples."""
import copy
import hashlib
import json
import math
from pathlib import Path


def _record(node, root_names, parent=None):
    attributes = copy.deepcopy(node.attrib)
    if parent == 'info' and node.tag in root_names:
        attributes.pop('t', None)
        attributes.pop('q', None)
    return [node.tag, attributes, [_record(child, root_names, node.tag) for child in node]]


def _digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,allow_nan=False).encode()).hexdigest().upper()


def align_initial_root_records(tree, expected):
    """Only initial root t/q may change; every child and sample field is retained."""
    info = tree.find('info')
    if info is None or not expected or len(expected)>128:
        raise ValueError('Require bounded actual exported root transforms.')
    before = _digest(_record(tree,set(expected)))
    changes = {}
    for root_name, values in expected.items():
        matches = [node for node in info if node.tag==root_name]
        if len(matches)!=1 or set(values)!={'t','q'}:
            raise ValueError('Expected one exact exported root record and world t/q.')
        node = matches[0]
        for field, length in [('t',3),('q',4)]:
            row=values[field]
            if len(row)!=length or any(type(v) not in (int,float) or not math.isfinite(v) for v in row):
                raise ValueError('Root transform must contain finite native values.')
        if abs(sum(v*v for v in values['q'])-1)>2e-5:
            raise ValueError('Expected a unit world-pose quaternion.')
        old = {field:list(node.get(field,[])) for field in ('t','q')}
        if len(old['t'])!=3 or len(old['q'])!=4 or any(not math.isfinite(v) for row in old.values() for v in row):
            raise ValueError('Malformed existing root initial transform.')
        translation_error=max(abs(a-b) for a,b in zip(old['t'],values['t']))
        quaternion_error=min(max(abs(a-b) for a,b in zip(old['q'],values['q'])),max(abs(a+b) for a,b in zip(old['q'],values['q'])))
        if max(translation_error,quaternion_error)>2e-6:
            node.set('t',list(values['t']));node.set('q',list(values['q']))
            changes[root_name]={'before':old,'after':copy.deepcopy(values)}
    if before!=_digest(_record(tree,set(expected))):
        raise RuntimeError('Initial-root correction changed child/sample/non-pose fields.')
    return {'changes':changes,'retained_fields_sha256':before}


def verify_initial_root_records(tree, expected, retained_hash):
    if _digest(_record(tree,set(expected)))!=retained_hash:
        raise RuntimeError('Serialized correction changed child/sample/non-pose fields.')
    for name,values in expected.items():
        node=next(n for n in tree.find('info') if n.tag==name)
        t=node.get('t');q=node.get('q')
        te=max(abs(a-b) for a,b in zip(t,values['t']))
        qe=min(max(abs(a-b) for a,b in zip(q,values['q'])),max(abs(a+b) for a,b in zip(q,values['q'])))
        if max(te,qe)>2e-6:raise RuntimeError('Serialized root initial transform differs from native world pose.')


def correct_exported_initial_roots(output, rig, frame_start, bpy):
    from io_pdx_mesh import pdx_data
    from io_pdx_mesh.pdx_blender.blender_import_export import swap_coord_space
    old_frame=bpy.context.scene.frame_current;old_subframe=bpy.context.scene.frame_subframe
    bpy.context.scene.frame_set(frame_start);bpy.context.view_layer.update()
    expected={}
    for bone in rig.pose.bones:
        if bone.parent is not None:continue
        world=rig.convert_space(pose_bone=bone,matrix=bone.matrix,from_space='POSE',to_space='WORLD')
        translation,rotation,scale=swap_coord_space(world).decompose()
        expected[bone.name]={'t':list(translation),'q':[rotation.x,rotation.y,rotation.z,rotation.w]}
    tree=pdx_data.read_meshfile(str(output));proof=align_initial_root_records(tree,expected)
    if proof['changes']:
        temporary=Path(str(output)+'.root_initial_tmp')
        if temporary.exists():raise FileExistsError('Root correction temporary file already exists.')
        pdx_data.write_animfile(str(temporary),tree)
        reopened=pdx_data.read_meshfile(str(temporary))
        verify_initial_root_records(reopened,expected,proof['retained_fields_sha256'])
        temporary.replace(output)
        output.with_suffix('.txt').write_text(str(pdx_data.PDXData(reopened))+'\n',encoding='utf-8')
    else:
        verify_initial_root_records(tree,expected,proof['retained_fields_sha256'])
    bpy.context.scene.frame_set(old_frame,subframe=old_subframe);bpy.context.view_layer.update()
    return {'policy':'initial root t/q use identical locked POSE-to-WORLD conversion as samples; child/sample payload retained','frame_start':frame_start,'expected_world_initial_roots':expected,'serialized_readback_passed':True,'child_and_sample_fields_preserved':True,**proof}
