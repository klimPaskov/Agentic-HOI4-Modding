"""Explicit rigid world-Z assembly yaw with all-frame skeletal deformation proof."""
import math
from manual_creature_rig import _open,name
from mesh_vertex_material_repair import finish_verified


def validate_yaw(payload):
    angle=payload.get('yaw_degrees')
    if type(angle) not in (int,float) or not math.isfinite(angle) or angle not in {-180,-90,90,180}:raise ValueError('Require exact cardinal rigid yaw: -180,-90,90,180 degrees.')
    for key,limit in [('object_names',64),('action_names',32)]:
        rows=payload.get(key)
        if not isinstance(rows,list) or not 1<=len(rows)<=limit or len(set(rows))!=len(rows):raise ValueError('Require bounded unique explicit '+key)
        for value in rows:name(value)
    name(payload['target_armature_name'])
    if payload['target_armature_name'] not in payload['object_names']:raise ValueError('Exact working armature must be included.')
    return float(angle)


def rotate_existing_assembly_yaw(req,h):
    from mathutils import Matrix
    p=req['payload'];angle=validate_yaw(p);job,source,output=_open(req,h);bpy=h['bpy'];scene=bpy.context.scene
    objects=[bpy.data.objects.get(n) for n in p['object_names']];rig=bpy.data.objects.get(p['target_armature_name'])
    if rig not in h['armatures']() or any(o is None or o.library or o.override_library or o.get('hoi4_source_protected') or o.get('hoi4_reference_read_only') or o.type not in {'MESH','ARMATURE','EMPTY'} or o.constraints for o in objects):raise ValueError('Require explicit local unprotected working assembly only.')
    selected=set(objects);meshes=[o for o in objects if o.type=='MESH'];roots=[o for o in objects if o.parent is None]
    if not meshes or not roots or any(o.parent is not None and o.parent not in selected for o in objects):raise ValueError('Working assembly must contain every parent through its unparented roots.')
    if any(child not in selected for o in objects for child in o.children):raise ValueError('Working yaw cannot move an undeclared/protected descendant.')
    if any(o!=rig and o.type=='ARMATURE' for o in objects):raise ValueError('Exactly one working rig is supported.')
    if any(o not in selected and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers) for o in bpy.data.objects if o.type=='MESH'):raise ValueError('Every mesh deformed by the working rig must be explicitly included.')
    if any(o.animation_data and (o.animation_data.drivers or o.animation_data.nla_tracks or (o!=rig and o.animation_data.action)) for o in objects):raise ValueError('Object animation/drivers/NLA require separate transform review.')
    if not rig.animation_data:raise ValueError('Existing working skeletal actions required.')
    actions=[];frames=0
    for n in p['action_names']:
        a=bpy.data.actions.get(n)
        if a is None or a.library:raise ValueError('Unknown/local action required.')
        curves=list(h['action_fcurves'](a))
        if not curves or any(not c.data_path.startswith('pose.bones[') for c,_ in curves):raise ValueError('Yaw proof supports skeletal bone channels only; object-space animation is not silently rotated.')
        start,end=map(int,a.frame_range)
        if start!=a.frame_range[0] or end!=a.frame_range[1] or not 1<=end-start+1<=600:raise ValueError('Require bounded integer-frame native action ranges.')
        frames+=end-start+1;actions.append((a,start,end))
    if frames>3000 or frames*sum(len(o.data.vertices) for o in meshes)>50000000:raise ValueError('All-frame proof exceeds fifty-million working vertices.')
    bpy.context.view_layer.update();before=h['_promotion_fingerprint'](job,[],include_sections=True)
    Q=Matrix.Rotation(math.radians(angle),4,'Z');root_world={o.name:o.matrix_world.copy() for o in roots};all_world={o.name:o.matrix_world.copy() for o in objects}
    old_action=rig.animation_data.action;old_slot=rig.animation_data.action_slot;old_frame=scene.frame_current;old_subframe=scene.frame_subframe
    pose={b.name:{k:list(getattr(b,k)) for k in ('location','rotation_euler','rotation_quaternion','rotation_axis_angle','scale')} for b in rig.pose.bones}
    def set_world(rotated):
        for o in roots:o.matrix_world=Q@root_world[o.name] if rotated else root_world[o.name]
        bpy.context.view_layer.update()
    def evaluated():
        graph=bpy.context.evaluated_depsgraph_get();result={}
        for o in meshes:
            eo=o.evaluated_get(graph);em=eo.to_mesh()
            try:result[o.name]=[eo.matrix_world@v.co for v in em.vertices]
            finally:eo.to_mesh_clear()
        return result
    proofs=[]
    for action,start,end in actions:
        rig.animation_data.action=action
        if action.slots:rig.animation_data.action_slot=action.slots[0]
        for b in rig.pose.bones:
            for k,v in pose[b.name].items():setattr(b,k,v)
        maximum=0.0
        for frame in range(start,end+1):
            set_world(False);scene.frame_set(frame);bpy.context.view_layer.update();original=evaluated();set_world(True);rotated=evaluated()
            for n,points in original.items():
                if len(points)!=len(rotated[n]):raise RuntimeError('Yaw changed evaluated vertex count.')
                for left,right in zip(points,rotated[n]):maximum=max(maximum,((Q@left)-right).length)
            if maximum>2e-5:raise RuntimeError('Rigid yaw changed skeletal deformation: '+str(maximum))
        proofs.append({'action':action.name,'frame_start':start,'frame_end':end,'all_frames_verified':True,'maximum_world_vertex_error':maximum})
    set_world(False);rig.animation_data.action=old_action
    if old_slot is not None:rig.animation_data.action_slot=old_slot
    for b in rig.pose.bones:
        for k,v in pose[b.name].items():setattr(b,k,v)
    scene.frame_set(old_frame,subframe=old_subframe);bpy.context.view_layer.update();set_world(True)
    for o in objects:
        wanted=Q@all_world[o.name]
        if max(abs(o.matrix_world[i][j]-wanted[i][j]) for i in range(4) for j in range(4))>2e-5:raise RuntimeError('Final explicit object rigid transform mismatch: '+o.name)
    after=h['_promotion_fingerprint'](job,[],include_sections=True)
    for key in ('geometry','rigs','materials','images','actions','scene'):
        if before['sha256'][key]!=after['sha256'][key]:raise RuntimeError('Rigid yaw changed retained '+key)
    transform_settings={'location','rotation_euler','rotation_quaternion','rotation_axis_angle','scale','dimensions','matrix_world','matrix_local','matrix_basis'}
    for n,row in before['sections']['objects'].items():
        other=after['sections']['objects'][n]
        if n not in p['object_names']:
            if row!=other:raise RuntimeError('Rigid yaw changed protected/undeclared object '+n)
        else:
            for key in row:
                if key in {'world','basis','dimensions'}:continue
                if key=='settings':
                    if {k:v for k,v in row[key].items() if k not in transform_settings}!={k:v for k,v in other[key].items() if k not in transform_settings}:raise RuntimeError('Yaw changed non-transform object settings.')
                elif row[key]!=other[key]:raise RuntimeError('Yaw changed non-transform object field '+key)
    return finish_verified(req,h,job,source,output,{'operation':'rotate_existing_assembly_yaw','yaw_degrees':angle,'object_names':p['object_names'],'root_names':[o.name for o in roots],'action_proofs':proofs,'geometry_uv_weights_rest_bind_actions_materials_preserved':True,'protected_objects_preserved':True,'transform_policy':'world-origin rigid Z rotation on explicit assembly roots; no geometry bake','status':'rotated_requires_axis_export_reimport_and_contact_review'})
