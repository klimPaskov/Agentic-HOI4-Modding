"""Exact reviewed source-vertex fan splits and coincident corner aliases; no inferred weld."""
from collections import Counter
import math
from manual_creature_rig import _open, digest, name
from mesh_vertex_material_repair import finish_verified


def validate_remap(spec, positions, weights, faces):
    required={'mesh_name','target_armature_name','split_vertices','corner_remaps','remove_unused_vertices','triangle_ceiling'}
    if not isinstance(spec,dict) or set(spec)!=required: raise ValueError('Require exact mesh/rig/split/corner-remap/unused-vertex/budget specification.')
    name(spec['mesh_name']);name(spec['target_armature_name'])
    splits=spec['split_vertices'];rows=spec['corner_remaps'];remove=spec['remove_unused_vertices']
    if not isinstance(splits,list) or len(splits)>1024 or not isinstance(rows,list) or not 1<=len(rows)<=20000: raise ValueError('At most1024 source duplicates and1-20000 exact corner remaps permitted.')
    sources={i:i for i in range(len(positions))};labels=set()
    for row in splits:
        if not isinstance(row,dict) or set(row)!={'name','source_vertex'}: raise ValueError('Split requires exact name/source_vertex.')
        label=name(row['name']);index=row['source_vertex']
        if label in labels or type(index)is not int or not 0<=index<len(positions): raise ValueError('Invalid/duplicate split label or source vertex.')
        labels.add(label);sources[label]=index
    changed={};seen=set();used=set()
    for row in rows:
        if not isinstance(row,dict) or set(row)!={'face_index','source_vertex','target_vertex'}: raise ValueError('Corner remap requires exact face/source/target.')
        f,v,t=row['face_index'],row['source_vertex'],row['target_vertex']
        if type(f)is not int or not 0<=f<len(faces) or type(v)is not int or v not in faces[f] or (f,v) in seen: raise ValueError('Unknown/duplicate source corner.')
        if not (type(t)is int or isinstance(t,str)) or t not in sources or t==v: raise ValueError('Unknown/no-op corner target.')
        ancestor=sources[t]
        if positions[v]!=positions[ancestor] or weights[v]!=weights[ancestor]: raise ValueError('Aliases must have exactly coincident local positions and identical source weights; no implicit averaging.')
        changed.setdefault(f,list(faces[f]))[faces[f].index(v)]=t;seen.add((f,v));used.add(t)
    if labels-used: raise ValueError('Every declared split must be consumed by an explicit corner.')
    if not isinstance(remove,list) or len(remove)>1024 or len(set(remove))!=len(remove) or any(type(i)is not int or not 0<=i<len(positions) for i in remove): raise ValueError('Unused removals require at most1024 exact unique source indices.')
    identities=set();consumed=set()
    for f,old in enumerate(faces):
        tri=changed.get(f,old)
        if len(tri)!=3 or len(set(tri))!=3: raise ValueError('Remap would create a degenerate indexed triangle.')
        identity=tuple(sorted(tri,key=lambda x:(isinstance(x,str),x)))
        if identity in identities: raise ValueError('Remap would create duplicate indexed faces; explicit face repair required first.')
        identities.add(identity);consumed.update(tri)
    if set(remove)&consumed or set(range(len(positions)))-consumed-set(remove): raise ValueError('Every removed vertex must be unused and every unused source vertex must be explicitly removed.')
    if type(spec['triangle_ceiling'])is not int or not 1<=spec['triangle_ceiling']<=100000: raise ValueError('Require explicit complete assembly triangle ceiling.')
    return sources,changed,set(remove)


def repair_explicit_vertex_remap(req,h):
    import bmesh
    from mesh_winding_repair import _verify_normal_signs
    p=req['payload'];spec=p['remap_spec'];job,source,output=_open(req,h);bpy=h['bpy']
    tolerance=p.get('angular_tolerance_degrees',0.25)
    if type(tolerance) not in (int,float) or not math.isfinite(tolerance) or not 0<tolerance<=0.5:raise ValueError('Explicit normal encoding tolerance must be positive and at most0.5 degrees.')
    obj=bpy.data.objects.get(spec.get('mesh_name'));rig=bpy.data.objects.get(spec.get('target_armature_name'))
    if obj not in h['mesh_objects']() or rig not in h['armatures']() or obj.library or obj.data.library or obj.data.users!=1 or obj.data.shape_keys or obj.get('hoi4_source_protected') or obj.get('hoi4_reference_read_only'): raise ValueError('Require exact local unshared working mesh and retained rig.')
    if len(obj.modifiers)!=1 or obj.modifiers[0].type!='ARMATURE' or obj.modifiers[0].object!=rig: raise ValueError('Require one retained existing armature modifier.')
    mesh=obj.data;positions=[list(v.co) for v in mesh.vertices];weights=[sorted((g.group,g.weight) for g in v.groups) for v in mesh.vertices];faces=[list(f.vertices) for f in mesh.polygons]
    face_settings=[(f.material_index,f.use_smooth) for f in mesh.polygons]
    sources,changed,remove=validate_remap(spec,positions,weights,faces)
    if h['geometry_metrics']()['triangles']>spec['triangle_ceiling']: raise ValueError('Source complete assembly exceeds declared triangle budget.')
    allowed={'position','.edge_verts','.corner_vert','.corner_edge','.select_vert','.select_edge','.select_poly','sharp_face','sharp_edge','material_index','custom_normal',*[u.name for u in mesh.uv_layers]}
    if any(a.name not in allowed and not a.name.startswith('.') for a in mesh.attributes): raise ValueError('Unknown mesh attributes require separate preservation review.')
    bpy.context.view_layer.update();before=h['_promotion_fingerprint'](job,[],include_sections=True)
    old_uv={u.name:{f.index:{mesh.loops[i].vertex_index:list(u.data[i].uv) for i in f.loop_indices} for f in mesh.polygons} for u in mesh.uv_layers}
    old_normals={f.index:{mesh.loops[i].vertex_index:tuple(mesh.corner_normals[i].vector) for i in f.loop_indices} for f in mesh.polygons}
    group_names=[g.name for g in obj.vertex_groups]
    bm=bmesh.new();bm.from_mesh(mesh);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
    vl=bm.verts.layers.int.new('hoi4_remap_source_vertex');fl=bm.faces.layers.int.new('hoi4_remap_source_face')
    for v in bm.verts:v[vl]=v.index
    for f in bm.faces:
        f[fl]=f.index
    by_id={v.index:v for v in bm.verts};old_faces=list(bm.faces);old_edges=set()
    for row in spec['split_vertices']:
        original=by_id[row['source_vertex']];v=bm.verts.new(original.co,original);v[vl]=row['source_vertex'];by_id[row['name']]=v
    for index,tri in changed.items():
        original=old_faces[index];old_edges.update(original.edges)
        new=bm.faces.new([by_id[i] for i in tri],original);new[fl]=index
        for loop in new.loops:
            corner=next(i for i,t in enumerate(tri) if by_id[t]==loop.vert)
            old=original.loops[corner]
            # Exact original edge flags, with incompatible alias merges rejected.
            flags=(old.edge.seam,old.edge.smooth,old.edge.select,old.edge.hide)
            current=(loop.edge.seam,loop.edge.smooth,loop.edge.select,loop.edge.hide)
            if len(loop.edge.link_faces)>1 and loop.edge not in original.edges and current!=flags: raise ValueError('Alias would merge incompatible edge attributes.')
            loop.edge.seam,loop.edge.smooth,loop.edge.select,loop.edge.hide=flags
    bmesh.ops.delete(bm,geom=[old_faces[i] for i in sorted(changed)],context='FACES_ONLY')
    for edge in old_edges:
        if edge.is_valid and not edge.link_faces:bm.edges.remove(edge)
    for i in remove:
        v=by_id[i]
        if v.link_edges or v.link_faces:raise RuntimeError('Explicitly removed alias remains connected.')
        bm.verts.remove(v)
    bm.verts.index_update();bm.faces.index_update();bm.normal_update()
    vertex_map=[v[vl] for v in bm.verts];face_map=[f[fl] for f in bm.faces]
    final_indices={key:v.index for key,v in by_id.items() if v.is_valid}
    bm.verts.layers.int.remove(vl);bm.faces.layers.int.remove(fl);bm.to_mesh(mesh);bm.free();mesh.update()
    expected_normals={};desired=[]
    for f in mesh.polygons:
        old_face=face_map[f.index]
        for i in f.loop_indices:
            old_vertex=vertex_map[mesh.loops[i].vertex_index]
            # Aliases may use a different coincident source index at this original corner.
            target=[final_indices[v] for v in changed.get(old_face,faces[old_face])]
            source_corner=faces[old_face][target.index(mesh.loops[i].vertex_index)]
            for layer in mesh.uv_layers:layer.data[i].uv=old_uv[layer.name][old_face][source_corner]
            normal=old_normals[old_face][source_corner];length=math.sqrt(sum(x*x for x in normal))
            if length<1e-12:raise ValueError('Undefined retained corner normal requires explicit face repair.')
            desired.append(tuple(x/length for x in normal));expected_normals[(f.index,mesh.loops[i].vertex_index)]=normal
    mesh.normals_split_custom_set(desired);mesh.update();normal_proof=_verify_normal_signs(mesh,expected_normals,set(),angular_tolerance_degrees=tolerance)
    if len(mesh.polygons)!=len(faces) or len(mesh.vertices)!=len(positions)+len(spec['split_vertices'])-len(remove):raise RuntimeError('Unexpected remap geometry counts.')
    if group_names!=[g.name for g in obj.vertex_groups]:raise RuntimeError('Vertex group identities changed.')
    for v,old in zip(mesh.vertices,vertex_map):
        if list(v.co)!=positions[old] or sorted((g.group,g.weight) for g in v.groups)!=weights[old]:raise RuntimeError('Remap changed source/duplicated position or weights.')
    for f,old in zip(mesh.polygons,face_map):
        if (f.material_index,f.use_smooth)!=face_settings[old]:raise RuntimeError('Face material/smoothing settings changed.')
        target=[final_indices[i] for i in changed.get(old,faces[old])];actual=list(f.vertices)
        if not any(actual==target[k:]+target[:k] for k in range(3)):raise RuntimeError('Explicit face corner target/order changed.')
        for loop_index in f.loop_indices:
            source_corner=faces[old][target.index(mesh.loops[loop_index].vertex_index)]
            for layer in mesh.uv_layers:
                if list(layer.data[loop_index].uv)!=old_uv[layer.name][old][source_corner]:raise RuntimeError('Retained source-face/source-corner UV readback changed.')
    bpy.context.view_layer.update();after=h['_promotion_fingerprint'](job,[],include_sections=True)
    for section in ('objects','rigs','materials','images','actions','scene'):
        if before['sha256'][section]!=after['sha256'][section]:raise RuntimeError('Vertex remap changed protected '+section)
    for n,row in before['sections']['geometry'].items():
        if n!=obj.name and row!=after['sections']['geometry'][n]:raise RuntimeError('Vertex remap changed an unrelated mesh.')
    reverse_vertices={str(i):[] for i in range(len(positions))}
    for new,old in enumerate(vertex_map):reverse_vertices[str(old)].append(new)
    report={'operation':'repair_explicit_vertex_remap','status':'remapped_requires_topology_contact_and_export_reimport_review','remap_spec_sha256':digest(spec),'mesh':obj.name,'new_vertex_to_source_vertex':vertex_map,'new_face_to_source_face':face_map,'source_vertex_to_new_vertices':reverse_vertices,'source_face_to_new_face':{str(old):new for new,old in enumerate(face_map)},'split_count':len(spec['split_vertices']),'removed_unused_vertices':sorted(remove),'normal_proof':normal_proof,'triangle_count_preserved':True,'rig_actions_materials_positions_weights_and_corner_uvs_preserved':True}
    return finish_verified(req,h,job,source,output,report)
