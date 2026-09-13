"""Finite world-vertical root displacement converted into a target rest basis."""
import math


def vertical_root_basis_location(source_world, source_start_world, basis_to_world):
    """Retain world Z only; matrix already contains target armature scale once."""
    if len(source_world) != 3 or len(source_start_world) != 3 or len(basis_to_world) != 3 or any(len(row) != 3 for row in basis_to_world):
        raise ValueError("Root conversion requires two 3-vectors and one 3x3 matrix.")
    values = list(source_world) + list(source_start_world) + [v for row in basis_to_world for v in row]
    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("Root conversion requires finite values.")
    a,b,c = basis_to_world[0]
    d,e,f = basis_to_world[1]
    g,h,i = basis_to_world[2]
    determinant = a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g)
    if abs(determinant) < 1e-12:
        raise ValueError("Target root rest basis is singular.")
    dz = float(source_world[2]) - float(source_start_world[2])
    return ((b*f-c*e)*dz/determinant, (c*d-a*f)*dz/determinant, (a*e-b*d)*dz/determinant)


def inspect_animation_source(req, api):
    """Inspect a hash-bound standalone FBX in a disposable Blender scene."""
    from pathlib import Path
    p = req['payload']; job = Path(req['job_root']).resolve()
    source = api['within'](job, p['source_rel'])
    expected = str(p['source_sha256']).upper()
    if source.suffix.lower() != '.fbx' or len(expected) != 64 or api['file_sha256'](source) != expected:
        raise ValueError('Source must be a checksum-matching job-local FBX.')
    bpy = api['bpy']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    imported = api['import_candidate'](source)
    rigs = [obj for obj in imported if obj.type == 'ARMATURE']
    if len(rigs) > 8 or any(len(rig.data.bones) > 512 for rig in rigs) or len(bpy.data.actions) > 32:
        raise ValueError('Source inspection exceeds bounded skeleton/action limits.')
    records = []
    for rig in rigs:
        records.append({'name': rig.name, 'matrix_world': [list(row) for row in rig.matrix_world],
                        'active_action': rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None,
                        'bones': [{'name': b.name, 'parent': b.parent.name if b.parent else None,
                                   'matrix_local': [list(row) for row in b.matrix_local],
                                   'head_world': list(rig.matrix_world @ b.head_local),
                                   'tail_world': list(rig.matrix_world @ b.tail_local)} for b in rig.data.bones]})
    actions = [{'name': a.name, 'frame_range': list(a.frame_range),
                'fcurve_count': len(list(api['action_fcurves'](a)))} for a in bpy.data.actions]
    if api['file_sha256'](source) != expected:
        raise RuntimeError('Source changed during read-only inspection.')
    return {'source_rel': p['source_rel'], 'source_sha256': expected,
            'fps': bpy.context.scene.render.fps, 'fps_base': bpy.context.scene.render.fps_base,
            'unit_scale_length': bpy.context.scene.unit_settings.scale_length,
            'armatures': records, 'actions': actions, 'source_preserved': True,
            'policy': 'disposable_scene_no_target_checkpoint_or_source_write'}


def conjugate_rotation(delta, source_object, target_object):
    """Map a wxyz unit-quaternion delta between armature object bases."""
    def unit(q):
        if len(q) != 4 or not all(math.isfinite(float(v)) for v in q):
            raise ValueError('Rotation must be a finite quaternion.')
        n = math.sqrt(sum(v*v for v in q))
        if n < 1e-12:
            raise ValueError('Rotation quaternion is zero.')
        return tuple(v/n for v in q)
    def mul(a,b):
        w,x,y,z=a; v,i,j,k=b
        return (w*v-x*i-y*j-z*k,w*i+x*v+y*k-z*j,w*j-x*k+y*v+z*i,w*k+x*j-y*i+z*v)
    def inv(q): return (q[0],-q[1],-q[2],-q[3])
    d=unit(delta); s=unit(source_object); t=unit(target_object)
    return unit(mul(mul(mul(mul(inv(t),s),d),inv(s)),t))


def angular_motion_retained(source_radians, target_radians):
    """Static-motion gate accepts only angular magnitudes, never translations."""
    if not all(math.isfinite(v) and v >= 0 for v in (source_radians, target_radians)):
        raise ValueError('Angular motion magnitudes must be finite and nonnegative.')
    return source_radians <= 1e-4 or target_radians >= max(1e-4, source_radians * 0.10)
