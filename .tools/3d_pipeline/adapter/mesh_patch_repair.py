"""Exact reviewed local mesh patches; no inferred filling or geometry reduction."""
from collections import Counter
from pathlib import Path
import math

from manual_creature_rig import _open, _finish, digest, name, vector


def validate_patch(spec, vertices, faces, materials, uv_names, bones):
    fields={'mesh_name','target_armature_name','remove_face_indices','boundary_loops','added_vertices','replacement_triangles','triangle_ceiling'}
    if not isinstance(spec,dict) or set(spec)!=fields: raise ValueError('Patch requires the exact declarative mesh/rig/removed-face/loop/new-vertex/triangle/budget contract.')
    name(spec['mesh_name'])
    if spec['target_armature_name']: name(spec['target_armature_name'])
    remove=spec['remove_face_indices']
    if not isinstance(remove,list) or len(remove)>2048 or len(remove)>max(1,int(len(faces)*.05)) or len(set(remove))!=len(remove) or any(type(i)is not int or not 0<=i<len(faces) for i in remove): raise ValueError('Require at most2048 exact unique removed triangle indices and at most5% of the source faces.')
    remove=set(remove); existing_edges={}
    for index,face in enumerate(faces):
        if len(face)!=3: raise ValueError('Patch requires existing triangular topology.')
        if index in remove: continue
        for a,b in zip(face,face[1:]+face[:1]): existing_edges.setdefault(tuple(sorted((a,b))),[]).append((a,b))
    loops=spec['boundary_loops']; boundary=set(); boundary_vertices=set()
    if not isinstance(loops,list) or not 1<=len(loops)<=64: raise ValueError('Require1-64 explicitly reviewed boundary loops.')
    labels=set()
    for loop in loops:
        if not isinstance(loop,dict) or set(loop)!={'name','vertex_indices'}: raise ValueError('Boundary requires name and exact ordered vertex_indices.')
        name(loop['name'])
        if loop['name'] in labels: raise ValueError('Duplicate loop name.')
        labels.add(loop['name']); ids=loop['vertex_indices']
        if not isinstance(ids,list) or not 3<=len(ids)<=256 or len(set(ids))!=len(ids) or any(type(i)is not int or not 0<=i<len(vertices) for i in ids): raise ValueError('Invalid exact simple boundary loop.')
        for a,b in zip(ids,ids[1:]+ids[:1]):
            edge=tuple(sorted((a,b)))
            if edge in boundary or len(existing_edges.get(edge,[]))!=1: raise ValueError('Declared loop edge is not an unambiguous remaining source boundary.')
            boundary.add(edge)
        boundary_vertices.update(ids)
    additions=spec['added_vertices']
    if not isinstance(additions,list) or len(additions)>512: raise ValueError('At most512 explicit added vertices permitted.')
    positions={i:list(v) for i,v in enumerate(vertices)}; new_ids={}
    for row in additions:
        if not isinstance(row,dict) or set(row)!={'name','world_position','weights'}: raise ValueError('Added vertex requires name/world_position/weights.')
        label=name(row['name'])
        if label in new_ids: raise ValueError('Duplicate added vertex name.')
        positions[label]=vector(row['world_position']); new_ids[label]=row
        weights=row['weights']
        if not isinstance(weights,list) or (not bones and weights) or (bones and not 1<=len(weights)<=4): raise ValueError('Added vertex requires1-4 explicit retained deform-bone weights, or no weights for a source without a rig.')
        seen=set(); total=0
        for weight in weights:
            if not isinstance(weight,dict) or set(weight)!={'bone','weight'} or weight['bone'] not in bones or weight['bone'] in seen or type(weight['weight']) not in (int,float) or not math.isfinite(weight['weight']) or not 0<weight['weight']<=1: raise ValueError('Invalid explicit added-vertex weight.')
            seen.add(weight['bone']); total+=weight['weight']
        if bones and abs(total-1)>1e-6: raise ValueError('Added-vertex weights must already be normalized.')
    triangles=spec['replacement_triangles']
    if not isinstance(triangles,list) or not 1<=len(triangles)<=2048: raise ValueError('Require1-2048 exact replacement triangles.')
    ceiling=spec['triangle_ceiling']
    if type(ceiling)is not int or not 1<=ceiling<=100000: raise ValueError('Require explicit approved total triangle ceiling.')
    new_edges={}; used=set(); identities=set()
    def key(a,b): return tuple(sorted((a,b),key=lambda i:(isinstance(i,str),i)))
    for row in triangles:
        if not isinstance(row,dict) or set(row)!={'vertices','material_index','loop_uvs'}: raise ValueError('Replacement triangle requires exact vertices/material_index/loop_uvs.')
        tri=row['vertices']
        if not isinstance(tri,list) or len(tri)!=3 or len(set(tri))!=3 or any(not ((type(i)is int and i in boundary_vertices) or (isinstance(i,str) and i in new_ids)) for i in tri): raise ValueError('Replacement faces may reference only declared boundary vertices and explicitly added vertices.')
        identity=tuple(sorted(tri,key=lambda i:(isinstance(i,str),i)))
        if identity in identities: raise ValueError('Duplicate replacement triangle.')
        identities.add(identity); used.update(tri)
        if type(row['material_index'])is not int or not 0<=row['material_index']<materials: raise ValueError('Replacement material must be an existing exact slot.')
        if set(row['loop_uvs'])!=set(uv_names): raise ValueError('Explicit corner UVs required for every retained UV layer.')
        for uvs in row['loop_uvs'].values():
            if not isinstance(uvs,list) or len(uvs)!=3: raise ValueError('Require three explicit corner UVs per triangle.')
            for uv in uvs: vector(uv,2,32)
        a,b,c=[positions[i] for i in tri]; u=[b[n]-a[n] for n in range(3)]; v=[c[n]-a[n] for n in range(3)]
        cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        if sum(x*x for x in cross)<1e-16: raise ValueError('Degenerate replacement triangle.')
        for a,b in zip(tri,tri[1:]+tri[:1]): new_edges.setdefault(key(a,b),[]).append((a,b))
    if set(new_ids)-used: raise ValueError('Unused added vertices forbidden.')
    for edge,rows in new_edges.items():
        if all(type(i)is int for i in edge):
            old=existing_edges.get(tuple(sorted(edge)),[])
        else: old=[]
        if edge in boundary:
            if len(rows)!=1 or rows[0]!=tuple(reversed(old[0])): raise ValueError('Patch boundary winding must oppose the retained source face.')
        elif old or len(rows)!=2 or rows[0]!=tuple(reversed(rows[1])):
            raise ValueError('Patch introduces occupied diagonals or nonmanifold/inconsistently wound interior edges.')
    if boundary-set(new_edges): raise ValueError('Every declared boundary edge must be closed exactly once.')
    return {'remove':remove,'new_vertices':new_ids,'boundary_vertices':boundary_vertices,'added_triangles':len(triangles),'removed_triangles':len(remove)}


def repair_explicit_mesh_patch(req,h):
    import bmesh
    from mathutils import Vector
    p=req['payload']; spec=p['patch_spec']; job,source,output=_open(req,h); bpy=h['bpy']
    obj=bpy.data.objects.get(spec.get('mesh_name')); rig=bpy.data.objects.get(spec.get('target_armature_name'))
    if obj not in h['mesh_objects']() or (rig is not None and rig not in h['armatures']()) or (rig is None and (spec['target_armature_name'] or h['armatures']())) or obj.library or obj.data.library or obj.data.users!=1 or obj.data.shape_keys or obj.get('hoi4_source_protected') or obj.get('hoi4_reference_read_only'):
        raise ValueError('Patch requires exact local approved unshared working mesh and rig.')
    if any(m.type!='ARMATURE' or m.object!=rig for m in obj.modifiers): raise ValueError('Patch requires the existing exact rig modifier only.')
    if rig is None and obj.vertex_groups: raise ValueError('Unrigged patch requires no retained vertex groups or armature modifier.')
    mesh=obj.data; faces=[list(f.vertices) for f in mesh.polygons]
    world=[list(obj.matrix_world@v.co) for v in mesh.vertices]
    result=validate_patch(spec,world,faces,len(mesh.materials),[u.name for u in mesh.uv_layers],set(rig.data.bones.keys()) if rig else set())
    before_geometry=h['geometry_metrics']()
    if before_geometry['triangles']-len(result['remove'])+result['added_triangles']>spec['triangle_ceiling']: raise ValueError('Exact patch exceeds complete assembled geometry budget.')
    before=h['_promotion_fingerprint'](job,[],include_sections=True)
    coordinates=[list(v.co) for v in mesh.vertices]
    weights=[[(g.group,g.weight) for g in v.groups] for v in mesh.vertices]
    groups=[g.name for g in obj.vertex_groups]
    old_uv={u.name:{f.index:{mesh.loops[i].vertex_index:list(u.data[i].uv) for i in f.loop_indices} for f in mesh.polygons} for u in mesh.uv_layers}
    old_normals={f.index:{mesh.loops[i].vertex_index:list(mesh.corner_normals[i].vector) for i in f.loop_indices} for f in mesh.polygons}
    allowed={'position','.edge_verts','.corner_vert','.corner_edge','.select_vert','.select_edge','.select_poly','sharp_face','sharp_edge','material_index','custom_normal',*[u.name for u in mesh.uv_layers]}
    if any(a.name not in allowed and not a.name.startswith('.') for a in mesh.attributes): raise ValueError('Unreviewed custom mesh attributes require a separate preservation contract.')
    bm=bmesh.new(); bm.from_mesh(mesh); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    original_v=bm.verts.layers.int.new('hoi4_patch_original_vertex'); original_f=bm.faces.layers.int.new('hoi4_patch_original_face')
    for v in bm.verts: v[original_v]=v.index
    for f in bm.faces: f[original_f]=f.index
    by_id={v.index:v for v in bm.verts}; candidates={i for f in result['remove'] for i in faces[f]}
    bmesh.ops.delete(bm,geom=[bm.faces[i] for i in sorted(result['remove'])],context='FACES_ONLY')
    deform=bm.verts.layers.deform.verify()
    for label,row in result['new_vertices'].items():
        v=bm.verts.new(obj.matrix_world.inverted()@Vector(row['world_position'])); v[original_v]=-1; by_id[label]=v
        for entry in row['weights']:
            group=obj.vertex_groups.get(entry['bone'])
            if group is None: raise ValueError('Added vertex weight requires an existing vertex group.')
            v[deform][group.index]=entry['weight']
    for row in spec['replacement_triangles']:
        f=bm.faces.new([by_id[i] for i in row['vertices']]); f[original_f]=-1; f.material_index=row['material_index']; f.smooth=True
        for layer,uvs in row['loop_uvs'].items():
            uv_layer=bm.loops.layers.uv.get(layer)
            for loop,uv in zip(f.loops,uvs): loop[uv_layer].uv=uv
    for edge in list(bm.edges):
        if not edge.link_faces and all(v[original_v] in candidates for v in edge.verts): bm.edges.remove(edge)
    for v in list(bm.verts):
        if not v.link_edges and v[original_v] in candidates: bm.verts.remove(v)
    bm.verts.index_update(); bm.faces.index_update(); bm.normal_update()
    vertex_map=[v[original_v] for v in bm.verts]; face_map=[f[original_f] for f in bm.faces]
    bm.verts.layers.int.remove(original_v); bm.faces.layers.int.remove(original_f)
    bm.to_mesh(mesh); bm.free(); mesh.update()
    # Preserve every unaffected corner's exact UV association and source normal;
    # only replacement faces use fresh geometric normals.
    normals=[]
    for f in mesh.polygons:
        old=face_map[f.index]
        for i in f.loop_indices:
            original=vertex_map[mesh.loops[i].vertex_index]
            if old>=0:
                for layer in mesh.uv_layers: layer.data[i].uv=old_uv[layer.name][old][original]
                normals.append(old_normals[old][original])
            else: normals.append(list(f.normal))
    mesh.normals_split_custom_set(normals); mesh.update()
    if [g.name for g in obj.vertex_groups]!=groups: raise RuntimeError('Patch changed original vertex-group identities.')
    for vertex,old in zip(mesh.vertices,vertex_map):
        if old>=0 and (list(vertex.co)!=coordinates[old] or [(g.group,g.weight) for g in vertex.groups]!=weights[old]): raise RuntimeError('Patch changed a retained vertex position or weights.')
    for f,old in zip(mesh.polygons,face_map):
        if old<0: continue
        ids=[vertex_map[i] for i in f.vertices]; expected=faces[old]
        if not any(ids==expected[i:]+expected[:i] for i in range(3)): raise RuntimeError('Patch changed an unaffected face.')
        for layer in mesh.uv_layers:
            if any(list(layer.data[i].uv)!=old_uv[layer.name][old][vertex_map[mesh.loops[i].vertex_index]] for i in f.loop_indices): raise RuntimeError('Patch changed unaffected UV corners.')
    after=h['_promotion_fingerprint'](job,[],include_sections=True)
    for key in ('objects','rigs','materials','images','actions','scene'):
        if before['sha256'][key]!=after['sha256'][key]: raise RuntimeError('Patch changed '+key)
    for n,row in before['sections']['geometry'].items():
        if n!=obj.name and row!=after['sections']['geometry'][n]: raise RuntimeError('Patch changed an unrelated mesh.')
    return _finish(req,h,job,source,output,{'operation':'repair_explicit_mesh_patch','patch_spec_sha256':digest(spec),'mesh':obj.name,'geometry_before':before_geometry,'geometry_after':h['geometry_metrics'](),'removed_faces':sorted(result['remove']),'new_vertex_to_source_vertex':vertex_map,'new_face_to_source_face':face_map,'retained_positions_weights_uvs_rig_actions_materials_preserved':True,'status':'patched_requires_visual_and_export_reimport_review'})
