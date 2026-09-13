"""Bounded exact vertex corrections and isolated existing-material rebinding."""
import math
import json

from manual_creature_rig import _open, _finish, _component_material, digest, name, vector


def verify_requested_vertex(row, world_position, weights):
    """Readback must match the request, not merely leave neighbours unchanged."""
    if 'world_position' in row and any(not math.isfinite(a) or not math.isclose(a,b,rel_tol=2e-6,abs_tol=2e-6) for a,b in zip(world_position,row['world_position'])):
        raise RuntimeError('Requested world vertex position was not applied.')
    if 'weights' in row:
        expected={entry['bone']:entry['weight'] for entry in row['weights']}
        if set(weights)!=set(expected) or any(not math.isfinite(weights[n]) or not math.isclose(weights[n],w,rel_tol=2e-6,abs_tol=2e-7) for n,w in expected.items()):
            raise RuntimeError('Requested exact vertex weights were not applied.')


def finish_verified(req,h,job,source,output,report):
    # Flush evaluated bounds after changed skin/positions before comparing persisted state.
    h['bpy'].context.view_layer.update()
    before=h['_promotion_fingerprint'](job,[],include_sections=True)
    h['save_blend'](output)
    h['bpy'].ops.wm.open_mainfile(filepath=str(output),use_scripts=False)
    after=h['_promotion_fingerprint'](job,[],include_sections=True)
    if before['sha256']!=after['sha256']:
        raise RuntimeError('Repair checkpoint save/reopen fingerprint mismatch; checkpoint is not accepted. Changed sections: '+repr([key for key in before['sha256'] if before['sha256'][key]!=after['sha256'].get(key)])+'; object deltas: '+repr({n:{key:(row.get(key),after['sections']['objects'].get(n,{}).get(key)) for key in row if row.get(key)!=after['sections']['objects'].get(n,{}).get(key)} for n,row in before['sections']['objects'].items() if row!=after['sections']['objects'].get(n)}))
    report['save_reopen_proof']={'passed':True,'sha256':after['sha256'],'image_records':after['sections']['images'],'source_blend_sha256':h['file_sha256'](source),'reopened_checkpoint_sha256':h['file_sha256'](output)}
    if h['file_sha256'](source)!=req['payload']['expected_source_sha256'].upper():
        raise RuntimeError('Source changed during repair.')
    report.update(source=source.relative_to(job).as_posix(),source_sha256=h['file_sha256'](source),checkpoint=output.relative_to(job).as_posix(),checkpoint_sha256=h['file_sha256'](output),authoring_route='bounded_blender',new_provider_call=False)
    path=job/'blender'/'reports'/(output.stem+'.json')
    path.parent.mkdir(parents=True,exist_ok=True)
    report['report']=path.relative_to(job).as_posix()
    path.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return report


def validate_vertex_edits(rows, vertex_count, bone_names, group_names):
    if not isinstance(rows,list) or not 1<=len(rows)<=min(vertex_count,20000): raise ValueError('Require1-20000 exact existing vertex edits.')
    seen=set()
    for row in rows:
        if not isinstance(row,dict) or set(row)-{'index','world_position','weights'} or 'index' not in row or not {'world_position','weights'}&set(row): raise ValueError('Vertex edit requires index and explicit position and/or weights.')
        index=row['index']
        if type(index)is not int or not 0<=index<vertex_count or index in seen: raise ValueError('Vertex indices must be exact, existing and unique.')
        seen.add(index)
        if 'world_position' in row: vector(row['world_position'])
        if 'weights' in row:
            weights=row['weights']
            if not isinstance(weights,list) or not 1<=len(weights)<=4: raise ValueError('Require1-4 existing deform-bone weights.')
            bones=set(); total=0
            for entry in weights:
                if not isinstance(entry,dict) or set(entry)!={'bone','weight'} or entry['bone'] not in bone_names or entry['bone'] not in group_names or entry['bone'] in bones or type(entry['weight'])not in (float,int) or not math.isfinite(entry['weight']) or not 0<entry['weight']<=1: raise ValueError('Invalid exact existing-bone weight.')
                bones.add(entry['bone']); total+=entry['weight']
            if abs(total-1)>1e-6: raise ValueError('Explicit weights must already be normalized.')
    return seen


def edit_explicit_mesh_vertices(req,h):
    from mathutils import Vector
    p=req['payload']; job,source,output=_open(req,h); bpy=h['bpy']
    obj=bpy.data.objects.get(p['mesh_name']); rig=bpy.data.objects.get(p['target_armature_name'])
    if obj not in h['mesh_objects']() or rig not in h['armatures']() or obj.library or obj.data.library or obj.data.shape_keys or obj.data.users!=1 or obj.get('hoi4_source_protected') or obj.get('hoi4_reference_read_only'):
        raise ValueError('Exact vertex edits require a local approved unshared working mesh and existing rig.')
    if len(obj.modifiers)!=1 or obj.modifiers[0].type!='ARMATURE' or obj.modifiers[0].object!=rig: raise ValueError('Exact vertex edits preserve one existing armature modifier.')
    mesh=obj.data; edits=p['vertex_edits']; selected=validate_vertex_edits(edits,len(mesh.vertices),{bone.name for bone in rig.data.bones if bone.use_deform},set(obj.vertex_groups.keys()))
    before=h['_promotion_fingerprint'](job,[],include_sections=True)
    positions=[list(v.co) for v in mesh.vertices]; weights=[sorted((g.group,g.weight) for g in v.groups) for v in mesh.vertices]
    topology=digest([list(f.vertices) for f in mesh.polygons]); uv=digest({u.name:[list(x.uv) for x in u.data] for u in mesh.uv_layers})
    changed_position=set(); inverse=obj.matrix_world.inverted()
    for row in edits:
        vertex=mesh.vertices[row['index']]
        if 'world_position' in row:
            vertex.co=inverse@Vector(row['world_position']); changed_position.add(vertex.index)
        if 'weights' in row:
            for group in obj.vertex_groups: group.remove([vertex.index])
            for entry in row['weights']: obj.vertex_groups[entry['bone']].add([vertex.index],entry['weight'],'REPLACE')
    mesh.update()
    if topology!=digest([list(f.vertices) for f in mesh.polygons]) or uv!=digest({u.name:[list(x.uv) for x in u.data] for u in mesh.uv_layers}): raise RuntimeError('Vertex edit changed topology or UVs.')
    for vertex in mesh.vertices:
        if vertex.index not in selected and (list(vertex.co)!=positions[vertex.index] or sorted((g.group,g.weight) for g in vertex.groups)!=weights[vertex.index]): raise RuntimeError('Vertex edit changed an unselected source vertex.')
    rows={row['index']:row for row in edits}
    for index,row in rows.items():
        vertex=mesh.vertices[index]
        verify_requested_vertex(row,list(obj.matrix_world@vertex.co),{obj.vertex_groups[g.group].name:g.weight for g in vertex.groups})
        if 'world_position' not in row and list(mesh.vertices[index].co)!=positions[index]: raise RuntimeError('Weight-only edit moved a vertex.')
        if 'weights' not in row and sorted((g.group,g.weight) for g in mesh.vertices[index].groups)!=weights[index]: raise RuntimeError('Position-only edit changed weights.')
    after=h['_promotion_fingerprint'](job,[],include_sections=True)
    for section in ('rigs','materials','images','actions','scene'):
        if before['sha256'][section]!=after['sha256'][section]: raise RuntimeError('Vertex edit changed '+section)
    for n,row in before['sections']['objects'].items():
        keys=set(row)-({'bounds','dimensions'} if n==obj.name else set())
        if any(row[k]!=after['sections']['objects'][n][k] for k in keys): raise RuntimeError('Vertex edit changed object transforms/relationships/settings.')
    for n,row in before['sections']['geometry'].items():
        if n!=obj.name and row!=after['sections']['geometry'][n]: raise RuntimeError('Vertex edit changed another mesh.')
    return finish_verified(req,h,job,source,output,{'operation':'edit_explicit_mesh_vertices','mesh':obj.name,'target_armature':rig.name,'vertex_edits_sha256':digest(edits),'changed_vertices':sorted(selected),'position_edited_vertices':sorted(changed_position),'requested_values_verified':True,'unchanged_vertices_uvs_topology_rig_actions_materials_preserved':True,'geometry_before':before['mesh_counts'],'geometry_after':after['mesh_counts'],'normal_policy':'source custom corner normals retained; geometric normals may follow moved positions; changed-position faces require normal review','status':'edited_requires_contact_deformation_and_export_reimport_review'})


def bind_existing_pdx_material(req,h):
    p=req['payload']; job,source,output=_open(req,h); bpy=h['bpy']
    names=p['target_mesh_names']
    if not isinstance(names,list) or not 1<=len(names)<=512 or len(set(names))!=len(names): raise ValueError('Require1-512 exact unique working meshes.')
    source_name=name(p['source_material_name']); new_name=name(p['material_name'])
    if bpy.data.materials.get(new_name): raise ValueError('Replacement PDX material requires a unique new name.')
    targets=[]
    for n in names:
        obj=bpy.data.objects.get(n)
        if obj not in h['mesh_objects']() or obj.library or obj.data.library or obj.get('hoi4_source_protected') or obj.get('hoi4_reference_read_only'): raise ValueError('Material rebind targets must be explicitly approved local working meshes.')
        slots=[i for i,m in enumerate(obj.data.materials) if m and m.name==source_name]
        if not slots: raise ValueError('Every exact target must contain the named source material slot.')
        if obj.data.users>1: raise ValueError('Material rebind cannot modify shared mesh datablocks.')
        targets.append((obj,slots))
    before=h['_promotion_fingerprint'](job,[],include_sections=True)
    original=bpy.data.materials.get(source_name)
    original.use_fake_user=True
    old_image_dimensions=[list(node.image.size) for node in original.node_tree.nodes if getattr(node,'image',None) is not None]
    largest=max([max(size) for size in old_image_dimensions]+[1024])
    texture_budget=2048 if largest>=2048 else 1024
    if largest>2048:raise ValueError('Existing body atlas exceeds currently verified2048 rebind budget.')
    material=_component_material(req,h,job,new_name,p['material_spec'],max_dimension=texture_budget)
    for obj,slots in targets:
        for slot in slots: obj.data.materials[slot]=material
    after=h['_promotion_fingerprint'](job,[],include_sections=True)
    for section in ('rigs','actions','scene'):
        if before['sha256'][section]!=after['sha256'][section]: raise RuntimeError('Material rebind changed '+section)
    for n,row in before['sections']['objects'].items():
        other=after['sections']['objects'][n]
        for key in row:
            if key=='settings' and n in names:
                if {k:v for k,v in row[key].items() if k!='active_material'}!={k:v for k,v in other[key].items() if k!='active_material'}: raise RuntimeError('Material rebind changed object settings.')
            elif row[key]!=other[key]: raise RuntimeError('Material rebind changed object relationships/transforms.')
    for n,row in before['sections']['geometry'].items():
        keys=set(row)-({'materials'} if n in names else set())
        if any(row[k]!=after['sections']['geometry'][n][k] for k in keys): raise RuntimeError('Material rebind changed mesh/UV/weight data.')
    for section in ('materials','images'):
        for n,row in before['sections'][section].items():
            other=after['sections'][section].get(n)
            if section=='materials' and n==source_name:
                row=dict(row); row['settings']=dict(row['settings'])
                if 'use_fake_user' in row['settings']: row['settings']['use_fake_user']=True
            if row!=other: raise RuntimeError('Material rebind changed original '+section+' '+n+': '+repr({key:(row.get(key),other.get(key)) for key in set(row)|set(other) if row.get(key)!=other.get(key)}))
    return finish_verified(req,h,job,source,output,{'operation':'bind_existing_pdx_material','source_material':source_name,'material':material.name,'material_spec_sha256':digest(p['material_spec']),'retained_source_image_dimensions':old_image_dimensions,'texture_dimension_budget':texture_budget,'targets':{obj.name:slots for obj,slots in targets},'geometry_uvs_weights_rig_actions_and_old_materials_preserved':True,'status':'bound_requires_preview_and_export_texture_reference_review'})
