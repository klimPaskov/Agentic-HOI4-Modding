"""Finite declarative model repair operations; invoked only by the locked adapter.

No caller code, URLs, expressions or shell commands are evaluated. Authoring is
hash-bound to an immutable checkpoint and writes a new sibling checkpoint.
Model-specific landmarks, weights, component geometry and keys belong in jobs.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest().upper()


def name(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,127}", value):
        raise ValueError("An explicit safe identifier is required.")
    return value


def vector(value, count=3, bound=10000):
    if not isinstance(value, (list, tuple)) or len(value) != count or any(type(v) not in (int, float) or not math.isfinite(v) or abs(v) > bound for v in value):
        raise ValueError("Expected a bounded finite numeric vector.")
    return list(map(float, value))


def validate_bones(rows):
    if not isinstance(rows, list) or not 2 <= len(rows) <= 128:
        raise ValueError("A rig requires 2-128 explicitly measured bones.")
    seen, roots = set(), 0
    for row in rows:
        if not isinstance(row, dict) or set(row) - {"name", "parent", "head", "tail", "roll_degrees", "deform"} or not {"name", "parent", "head", "tail"} <= set(row):
            raise ValueError("Malformed bone declaration.")
        bone = name(row["name"])
        if bone in seen or (row["parent"] is not None and row["parent"] not in seen):
            raise ValueError("Bones must be unique and parents must precede their children.")
        head, tail = vector(row["head"]), vector(row["tail"])
        if sum((a-b)**2 for a, b in zip(head, tail)) < 1e-10:
            raise ValueError("Zero-length bones are forbidden.")
        vector([row.get("roll_degrees", 0)], 1, 360)
        if type(row.get("deform", True)) is not bool:
            raise ValueError("deform must be boolean.")
        roots += row["parent"] is None
        seen.add(bone)
    if roots != 1:
        raise ValueError("Exactly one skeleton root is required.")
    return seen


def validate_regions(rows, bone_names):
    if not isinstance(rows, list) or not 1 <= len(rows) <= 256:
        raise ValueError("Require 1-256 ordered weight regions.")
    for row in rows:
        if not isinstance(row, dict) or set(row) - {"name", "min", "max", "bones", "rigid", "mesh_names"} or not {"name", "min", "max", "bones", "rigid"} <= set(row):
            raise ValueError("Weight regions require name/min/max/bones/rigid.")
        name(row["name"])
        if "mesh_names" in row:
            names=row["mesh_names"]
            if not isinstance(names,list) or not 1<=len(names)<=512 or len(set(names))!=len(names):
                raise ValueError("Region mesh_names requires 1-512 exact unique object names.")
            for n in names: name(n)
        lo, hi = vector(row["min"]), vector(row["max"])
        if any(a > b for a, b in zip(lo, hi)):
            raise ValueError("Region bounds must be ordered.")
        candidates = row["bones"]
        if not isinstance(candidates, list) or not 1 <= len(candidates) <= 8 or len(set(candidates)) != len(candidates) or not set(candidates) <= bone_names:
            raise ValueError("Region bone candidates must be explicit known unique names.")
        if type(row["rigid"]) is not bool or (row["rigid"] and len(candidates) != 1):
            raise ValueError("Rigid regions require exactly one bone.")


def validate_component(spec):
    if not isinstance(spec, dict) or set(spec) - {"name", "bone", "material", "vertices", "triangles", "loop_uvs", "material_spec"} or not {"name", "bone", "material", "vertices", "triangles", "loop_uvs"} <= set(spec):
        raise ValueError("Component requires name/bone/material/vertices/triangles/loop_uvs.")
    for key in ("name", "bone", "material"):
        name(spec[key])
    vertices, triangles, uvs = spec["vertices"], spec["triangles"], spec["loop_uvs"]
    if not isinstance(vertices, list) or not 4 <= len(vertices) <= 8192 or not isinstance(triangles, list) or not 4 <= len(triangles) <= 16384:
        raise ValueError("Component exceeds explicit geometry bounds.")
    for point in vertices:
        vector(point)
    used, edges, orientation = set(), {}, {}
    for face in triangles:
        if not isinstance(face, list) or len(face) != 3 or len(set(face)) != 3 or any(type(i) is not int or not 0 <= i < len(vertices) for i in face):
            raise ValueError("Component must have valid distinct triangle indices.")
        used.update(face)
        a, b, c = [vertices[i] for i in face]
        u, v = [b[i]-a[i] for i in range(3)], [c[i]-a[i] for i in range(3)]
        cross = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
        if sum(x*x for x in cross) < 1e-16:
            raise ValueError("Component has a degenerate triangle.")
        for x, y in zip(face, face[1:]+face[:1]):
            edge = tuple(sorted((x, y)))
            edges[edge] = edges.get(edge, 0)+1
            orientation[edge] = orientation.get(edge, 0)+(1 if x < y else -1)
    if len(used) != len(vertices) or any(count != 2 for count in edges.values()) or any(orientation.values()):
        raise ValueError("Component must have no loose vertices or open/nonmanifold edges.")
    if not isinstance(uvs, list) or len(uvs) != len(triangles)*3:
        raise ValueError("Provide one UV coordinate per triangle corner.")
    for uv in uvs:
        if any(v < 0 or v > 1 for v in vector(uv, 2, 1)):
            raise ValueError("Component UVs must lie in [0,1].")


def validate_action(spec):
    required = {"name", "role", "fps", "frame_start", "frame_end", "loop", "root_bone", "ground_contact", "phases", "keys"}
    if not isinstance(spec, dict) or set(spec) != required:
        raise ValueError("Action requires exact declared name/role/fps/range/loop/root/contact/phases/keys.")
    for key in ("name", "role", "root_bone"):
        name(spec[key])
    if type(spec["fps"]) is not int or not 1 <= spec["fps"] <= 120:
        raise ValueError("FPS must be 1-120.")
    start, end = spec["frame_start"], spec["frame_end"]
    if type(start) is not int or type(end) is not int or not 0 <= start < end <= start+1200:
        raise ValueError("Require a bounded action range of at most 1201 frames.")
    if type(spec["loop"]) is not bool or spec["ground_contact"] not in {"per_frame_lowest_point_1mm", "none"}:
        raise ValueError("Explicit loop and contact policies are required.")
    phases = spec["phases"]
    if not isinstance(phases, list) or not 3 <= len(phases) <= 32:
        raise ValueError("Require 3-32 ordered semantic phases.")
    frames, labels = [], set()
    for phase in phases:
        if not isinstance(phase, dict) or set(phase) != {"name", "frame"}:
            raise ValueError("A phase requires name/frame.")
        label = name(phase["name"])
        if label in labels or type(phase["frame"]) is not int:
            raise ValueError("Phases must have unique names and integer frames.")
        labels.add(label); frames.append(phase["frame"])
    if frames[0] != start or frames[-1] != end or any(a >= b for a,b in zip(frames,frames[1:])):
        raise ValueError("Phases must be ordered and include endpoints.")
    keys = spec["keys"]
    if not isinstance(keys, dict) or not 3 <= len(keys) <= 128:
        raise ValueError("Require explicit articulated keys on 3-128 bones.")
    varying = 0
    for bone, rows in keys.items():
        name(bone)
        if not isinstance(rows, list) or not 3 <= len(rows) <= 128:
            raise ValueError("Each keyed bone requires 3-128 keys.")
        keyframes = []
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"frame", "rotation_degrees", "location"} or type(row["frame"]) is not int:
                raise ValueError("Each key requires frame/rotation_degrees/location.")
            keyframes.append(row["frame"])
            vector(row["rotation_degrees"], 3, 360); vector(row["location"], 3, 100)
        if keyframes != sorted(set(keyframes)) or keyframes[0] != start or keyframes[-1] != end or not set(frames) <= set(keyframes):
            raise ValueError("Keys must be ordered, include every phase, and match action bounds.")
        varying += bone != spec["root_bone"] and len({tuple(row["rotation_degrees"]+row["location"]) for row in rows}) > 1
        if spec["loop"] and (rows[0]["rotation_degrees"] != rows[-1]["rotation_degrees"] or rows[0]["location"] != rows[-1]["location"]):
            raise ValueError("Loop pose endpoints must match exactly.")
    if varying < 3:
        raise ValueError("Whole-rig transforms/static aliases cannot satisfy articulated action authoring.")


def _open(req, h):
    p, job = req["payload"], Path(req["job_root"]).resolve()
    source = h["within"](job, p["blend_rel"])
    output = h["within"](job, p["checkpoint_rel"], allow_missing=True)
    expected = p["expected_source_sha256"]
    if not isinstance(expected, str) or not re.fullmatch(r"[A-Fa-f0-9]{64}", expected) or h["file_sha256"](source) != expected.upper():
        raise ValueError("Source checkpoint SHA-256 mismatch.")
    if source.suffix != ".blend" or output.suffix != ".blend" or output.parent != source.parent or output == source or output.exists():
        raise ValueError("Output must be a new sibling .blend; source overwrite is forbidden.")
    h["bpy"].ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
    return job, source, output


def _repair_collection(h):
    bpy = h["bpy"]
    objects = h["mesh_objects"]() + h["armatures"]()
    if not objects or any(not obj.get("hoi4_working") or obj.library or obj.data.library or obj.get("hoi4_source_protected") or obj.get("hoi4_reference_read_only") for obj in objects):
        raise ValueError("Require explicitly approved local working objects.")
    collection = bpy.data.collections.get("WORKING")
    if collection is None:
        collection = bpy.data.collections.new("WORKING")
        bpy.context.scene.collection.children.link(collection)
    elif collection.library or collection.get("hoi4_source_protected") or collection.get("hoi4_reference_read_only"):
        raise ValueError("Working collection is protected or linked.")
    if collection.name not in {c.name for c in bpy.context.scene.collection.children_recursive}:
        raise ValueError("Working collection does not belong to the active scene.")
    return collection


def _mesh_signature(objects):
    return digest({obj.name: {"vertices": [list(v.co) for v in obj.data.vertices], "faces": [list(f.vertices) for f in obj.data.polygons], "uvs": {u.name: [list(v.uv) for v in u.data] for u in obj.data.uv_layers}, "materials": [m.name if m else None for m in obj.data.materials]} for obj in objects})


def _finish(req, h, job, source, output, report):
    if h["file_sha256"](source) != req["payload"]["expected_source_sha256"].upper():
        raise RuntimeError("Source checkpoint changed during repair.")
    h['bpy'].context.view_layer.update()
    check_pixels = any(getattr(node,'image',None) is not None and not node.image.filepath and not node.image.packed_files for material in h['bpy'].data.materials if material.use_nodes for node in material.node_tree.nodes)
    fingerprint = h['_promotion_fingerprint'](job,[],include_sections=True) if check_pixels else None
    h["save_blend"](output)
    if check_pixels:
        h['bpy'].ops.wm.open_mainfile(filepath=str(output),use_scripts=False)
        persisted = h['_promotion_fingerprint'](job,[],include_sections=True)
        if fingerprint['sha256'] != persisted['sha256']:
            raise RuntimeError('Empty-path image checkpoint save/reopen fingerprint mismatch; output is not accepted. Changed sections: '+repr([key for key in fingerprint['sha256'] if fingerprint['sha256'][key]!=persisted['sha256'].get(key)])+'; object deltas: '+repr({n:{key:(row.get(key),persisted['sections']['objects'].get(n,{}).get(key)) for key in row if row.get(key)!=persisted['sections']['objects'].get(n,{}).get(key)} for n,row in fingerprint['sections']['objects'].items() if row!=persisted['sections']['objects'].get(n)}))
        report['empty_path_image_save_reopen_proof'] = {'passed':True,'image_sha256':persisted['sha256']['images'],'image_records':persisted['sections']['images'],'source_blend_sha256':h['file_sha256'](source)}
    report.update(source=source.relative_to(job).as_posix(), source_sha256=h["file_sha256"](source), checkpoint=output.relative_to(job).as_posix(), checkpoint_sha256=h["file_sha256"](output), authoring_route="bounded_blender", new_provider_call=False)
    path = job/"blender"/"reports"/(output.stem+".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    report["report"] = path.relative_to(job).as_posix()
    path.write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    return report


def author_measured_creature_rig(req, h):
    import bpy
    from mathutils import Vector, Matrix
    p = req["payload"]; spec = p["rig_spec"]
    if set(spec) != {"name", "bones", "weight_regions", "body_triangle_target", "repair_boundaries"}:
        raise ValueError("Rig specification has missing/unsupported fields.")
    rig_name = name(spec["name"]); bones = validate_bones(spec["bones"])
    validate_regions(spec["weight_regions"], bones)
    if type(spec["body_triangle_target"]) is not int or spec["body_triangle_target"] < 0 or type(spec["repair_boundaries"]) is not bool:
        raise ValueError("Invalid bounded repair/reduction contract.")
    job, source, output = _open(req,h)
    meshes = h["mesh_objects"]()
    if not meshes or any(obj.data.shape_keys or obj.library or obj.data.library or not obj.get("hoi4_working") for obj in meshes):
        raise ValueError("Require local approved working meshes without shape keys.")
    if any(set(r.get("mesh_names",[]))-{obj.name for obj in meshes} for r in spec["weight_regions"]):
        raise ValueError("Weight region targets an unknown working mesh.")
    before_geometry = h["geometry_metrics"]()
    before_sig = _mesh_signature(meshes)
    worlds = {obj.name: obj.matrix_world.copy() for obj in meshes}
    for obj in meshes:
        obj.parent = None; obj.matrix_parent_inverse = Matrix.Identity(4); obj.matrix_world = worlds[obj.name]
        for modifier in list(obj.modifiers):
            if modifier.type == "ARMATURE": obj.modifiers.remove(modifier)
            else: raise ValueError("Measured rigging permits only the replaced Armature modifier.")
    for rig in h["armatures"]():
        bpy.data.objects.remove(rig, do_unlink=True)
    if _mesh_signature(meshes) != before_sig:
        raise RuntimeError("Unbinding changed body geometry/materials.")
    repair = h["repair_open_surface_boundaries"]() if spec["repair_boundaries"] else None
    target = spec["body_triangle_target"]
    if target and target < before_geometry["triangles"]*.90:
        raise ValueError("Body reduction below 90% requires a separate reviewed geometry operation.")
    reduction = h["controlled_decimate"](target) if target else None
    data = bpy.data.armatures.new(rig_name); rig = bpy.data.objects.new(rig_name,data)
    _repair_collection(h).objects.link(rig)
    rig["hoi4_working"] = True; rig["hoi4_custom_creature_rig"] = True
    rig["hoi4_manual_rig_spec_sha256"] = digest(spec)
    bpy.ops.object.select_all(action="DESELECT"); rig.select_set(True); bpy.context.view_layer.objects.active=rig
    bpy.ops.object.mode_set(mode="EDIT")
    for row in spec["bones"]:
        bone=data.edit_bones.new(row["name"]); bone.head=Vector(row["head"]); bone.tail=Vector(row["tail"])
        bone.roll=math.radians(row.get("roll_degrees",0)); bone.use_deform=row.get("deform",True)
        if row["parent"]: bone.parent=data.edit_bones[row["parent"]]
    bpy.ops.object.mode_set(mode="OBJECT"); rig.show_in_front=True
    segments={b.name:(b.head_local.copy(),b.tail_local.copy()) for b in data.bones}
    weighted_sig = _mesh_signature(meshes); counts={}; region_counts={r["name"]:0 for r in spec["weight_regions"]}
    for obj in meshes:
        for group in list(obj.vertex_groups): obj.vertex_groups.remove(group)
        groups={n:obj.vertex_groups.new(name=n) for n in bones}; counts[obj.name]={n:0 for n in bones}
        for vertex in obj.data.vertices:
            point=obj.matrix_world@vertex.co
            region=next((r for r in spec["weight_regions"] if ("mesh_names" not in r or obj.name in r["mesh_names"]) and all(r["min"][i]<=point[i]<=r["max"][i] for i in range(3))),None)
            if region is None: raise ValueError(f"No declared weight region covers {obj.name} vertex {vertex.index}.")
            region_counts[region["name"]]+=1
            if region["rigid"]: pairs=[(1.0,region["bones"][0])]
            else:
                ranked=sorted((h["_point_segment_distance"](point,*segments[n]),n) for n in region["bones"])[:3]
                raw=[(1/max(distance,.04)**4,n) for distance,n in ranked]; total=sum(w for w,n in raw)
                pairs=[(w/total,n) for w,n in raw if w/total>.002]
                norm=sum(w for w,n in pairs); pairs=[(w/norm,n) for w,n in pairs]
            for weight,n in pairs: groups[n].add([vertex.index],weight,"REPLACE"); counts[obj.name][n]+=1
        world=obj.matrix_world.copy(); obj.parent=rig; obj.matrix_parent_inverse=Matrix.Identity(4); obj.matrix_world=world
        modifier=obj.modifiers.new("HOI4_MEASURED_ARMATURE","ARMATURE"); modifier.object=rig
    if _mesh_signature(meshes)!=weighted_sig: raise RuntimeError("Rig/weight authoring changed body geometry/materials.")
    bpy.context.view_layer.update()
    return _finish(req,h,job,source,output,{"operation":"author_measured_creature_rig","status":"authored_requires_deformation_review","rig":rig.name,"rig_spec":spec,"bone_rest":[{"name":b.name,"parent":b.parent.name if b.parent else None,"head":list(b.head_local),"tail":list(b.tail_local),"matrix_local":[list(v) for v in b.matrix_local]} for b in data.bones],"weights":counts,"region_counts":region_counts,"geometry_before":before_geometry,"geometry_after":h["geometry_metrics"](),"body_signature_before":before_sig,"body_signature_after":weighted_sig,"rigging_preserved_body_geometry_and_uvs":True,"repair":repair,"reduction":reduction})


def attach_rigid_component(req,h):
    import bpy
    from mathutils import Matrix
    p=req["payload"]; spec=p["component_spec"]; validate_component(spec)
    rig_name=name(p["target_armature_name"])
    ceiling=p["triangle_ceiling"]
    if type(ceiling) is not int or not 1<=ceiling<=100000: raise ValueError("Explicit triangle ceiling required.")
    job,source,output=_open(req,h); meshes=h["mesh_objects"](); signature=_mesh_signature(meshes)
    rigs=h["armatures"](); rig=bpy.data.objects.get(rig_name)
    if len(rigs)!=1 or rigs[0]!=rig or spec["bone"] not in rig.data.bones or bpy.data.objects.get(spec["name"]):
        raise ValueError("Require the exact unique working rig, existing bone, and new component name.")
    material=bpy.data.materials.get(spec["material"])
    if "material_spec" in spec:
        if material is not None:
            raise ValueError("Explicit component material must have a new unique name.")
        material = _component_material(req, h, job, spec["material"], spec["material_spec"])
    elif material is None or material not in [mat for obj in meshes for mat in obj.data.materials]:
        raise ValueError("Component requires an existing working material or explicit new job-owned PDX DDS maps.")
    if h["geometry_metrics"]()["triangles"]+len(spec["triangles"])>ceiling:
        raise ValueError("Component exceeds total approved triangle ceiling.")
    mesh=bpy.data.meshes.new(spec["name"]); mesh.from_pydata(spec["vertices"],[],spec["triangles"]); mesh.update()
    obj=bpy.data.objects.new(spec["name"],mesh); _repair_collection(h).objects.link(obj)
    obj["hoi4_working"]=True; obj["hoi4_rigid_component_spec_sha256"]=digest(spec)
    mesh.materials.append(material); uv=mesh.uv_layers.new(name="UVMap")
    for i,value in enumerate(spec["loop_uvs"]): uv.data[i].uv=value
    group=obj.vertex_groups.new(name=spec["bone"]); group.add(list(range(len(mesh.vertices))),1,"REPLACE")
    obj.parent=rig; obj.matrix_parent_inverse=rig.matrix_world.inverted(); obj.matrix_world=Matrix.Identity(4)
    modifier=obj.modifiers.new("HOI4_RIGID_COMPONENT_ARMATURE","ARMATURE"); modifier.object=rig
    if _mesh_signature(meshes)!=signature: raise RuntimeError("Component authoring changed the existing body.")
    return _finish(req,h,job,source,output,{"operation":"attach_rigid_component","status":"authored_requires_visual_review","component":spec["name"],"component_spec_sha256":digest(spec),"component_triangles":len(spec["triangles"]),"bone":spec["bone"],"material":spec["material"],"existing_body_preserved":True,"geometry":h["geometry_metrics"]()})


def author_measured_creature_action(req,h):
    import bpy
    from mathutils import Euler, Vector
    p=req["payload"]; spec=p["action_spec"]; validate_action(spec)
    rig_name=name(p["target_armature_name"]); job,source,output=_open(req,h)
    rig=bpy.data.objects.get(rig_name); rigs=h["armatures"](); meshes=h["mesh_objects"]()
    if rig is None or len(rigs)!=1 or rigs[0]!=rig or not set(spec["keys"])<=set(rig.pose.bones.keys()) or spec["root_bone"] not in rig.pose.bones:
        raise ValueError("Action requires the exact unique rig and declared existing bones.")
    if bpy.data.actions.get(spec["name"]): raise ValueError("Action must have a new name; existing motion is preserved.")
    if rig.constraints or any(b.constraints for b in rig.pose.bones): raise ValueError("Explicit authoring requires unconstrained export bones.")
    signature=_mesh_signature(meshes); scene=bpy.context.scene; scene.render.fps=spec["fps"]; scene.render.fps_base=1
    rig.animation_data_create()
    for track in rig.animation_data.nla_tracks: track.mute=True
    action=bpy.data.actions.new(spec["name"]); action.use_fake_user=True; rig.animation_data.action=action
    scene.frame_start=spec["frame_start"]; scene.frame_end=spec["frame_end"]
    # Each new action has an explicit identity baseline for every bone.
    # Existing actions and their curves are not rewritten or reused as aliases.
    for bone in rig.pose.bones:
        if bone.rotation_mode == "AXIS_ANGLE":
            raise ValueError("Axis-angle rigs require separately reviewed channel conversion.")
        bone.location=(0,0,0); bone.rotation_quaternion=(1,0,0,0); bone.rotation_euler=(0,0,0); bone.scale=(1,1,1)
    for bone in rig.pose.bones:
        rows=spec["keys"].get(bone.name,[{"frame":phase["frame"],"rotation_degrees":[0,0,0],"location":[0,0,0]} for phase in spec["phases"]])
        for row in rows:
            bone.location=Vector(row["location"])
            rotation=Euler([math.radians(v) for v in row["rotation_degrees"]],"XYZ")
            channel="rotation_quaternion" if bone.rotation_mode=="QUATERNION" else "rotation_euler"
            if channel=="rotation_quaternion": bone.rotation_quaternion=rotation.to_quaternion()
            else: bone.rotation_euler=rotation.to_matrix().to_euler(bone.rotation_mode)
            bone.keyframe_insert(data_path="location",frame=row["frame"],group=bone.name)
            bone.keyframe_insert(data_path=channel,frame=row["frame"],group=bone.name)
    for curve,_ in h["action_fcurves"](action):
        for key in curve.keyframe_points: key.interpolation="LINEAR"
    base=rig.location.copy(); ground=[]; samples=[]
    root=rig.pose.bones[spec["root_bone"]]
    root_locations={}
    for frame in range(spec["frame_start"],spec["frame_end"]+1):
        scene.frame_set(frame); root_locations[frame]=root.location.copy()
    for frame in range(spec["frame_start"],spec["frame_end"]+1):
        scene.frame_set(frame); rig.location=base; bpy.context.view_layer.update()
        before,maximum=h["evaluated_world_bounds"](meshes)
        if spec["ground_contact"]=="per_frame_lowest_point_1mm":
            root.location=root_locations[frame]; root.keyframe_insert(data_path="location",frame=frame,group=root.name)
            _root_vertical_contact(h,rig,root,meshes,frame,.001)
            bpy.context.view_layer.update()
        after,maximum=h["evaluated_world_bounds"](meshes); ground.append({"frame":frame,"before":before.z,"after":after.z,"rig_location":list(rig.location)})
        if frame in {v["frame"] for v in spec["phases"]}:
            samples.append({"frame":frame,"bounds_min":list(after),"bounds_max":list(maximum),"bones":{b.name:{"head":list(rig.matrix_world@b.head),"tail":list(rig.matrix_world@b.tail),"rotation_quaternion":list(b.rotation_quaternion)} for b in rig.pose.bones}})
    for curve,_ in h["action_fcurves"](action):
        for key in curve.keyframe_points: key.interpolation="LINEAR"
    action["hoi4_animation_source_kind"]="manual_blender_gpt6_astra"
    action["hoi4_animation_source_sha256"]=h["file_sha256"](source)
    action["hoi4_manual_action_spec_sha256"]=digest(spec)
    action["hoi4_semantic_role"]=spec["role"]; action["hoi4_loop"]=spec["loop"]
    action["hoi4_root_policy"]="in_place_with_per_frame_vertical_contact" if spec["ground_contact"]!="none" else "explicit_bone_keys"
    scene.frame_set(spec["frame_start"]); bpy.context.view_layer.update()
    if _mesh_signature(meshes)!=signature: raise RuntimeError("Action authoring changed mesh/UV/material data.")
    return _finish(req,h,job,source,output,{"operation":"author_measured_creature_action","status":"authored_requires_semantic_and_deformation_review","action":action.name,"role":spec["role"],"action_spec":spec,"fps":spec["fps"],"frame_start":spec["frame_start"],"frame_end":spec["frame_end"],"loop":spec["loop"],"ground":ground,"phase_samples":samples,"body_geometry_preserved":True,"native_action_sha256":h["_mesh_region_action_hash"](action)})


def inspect_mesh_landmarks(req,h):
    import bpy
    p=req["payload"]; job=Path(req["job_root"]).resolve(); source=h["within"](job,p["blend_rel"])
    expected=p["expected_source_sha256"].upper()
    if not re.fullmatch(r"[A-F0-9]{64}",expected) or h["file_sha256"](source)!=expected: raise ValueError("Source SHA mismatch.")
    output=h["within"](job,p["report_rel"],allow_missing=True)
    if output.suffix!=".json" or output.exists() or not output.relative_to(job).parts[0] in {"evidence","blender","validation"}: raise ValueError("Use a new job-owned evidence JSON.")
    bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
    names=p["mesh_names"]
    if not isinstance(names,list) or not 1<=len(names)<=16 or len(set(names))!=len(names): raise ValueError("Require 1-16 exact meshes.")
    meshes=[]
    for n in names:
        obj=bpy.data.objects.get(n)
        if obj is None or obj.type!="MESH" or len(obj.data.vertices)>200000: raise ValueError("Mesh missing or exceeds bounded inventory.")
        meshes.append(obj)
    data={"source":p["blend_rel"],"source_sha256":expected,"meshes":{obj.name:{"vertices":[{"index":v.index,"world":list(obj.matrix_world@v.co)} for v in obj.data.vertices],"triangles":[list(f.vertices) for f in obj.data.polygons],"materials":[m.name if m else None for m in obj.data.materials],"vertex_groups":[g.name for g in obj.vertex_groups],"vertex_weights":[[{"group":g.group,"bone":obj.vertex_groups[g.group].name,"weight":g.weight} for g in v.groups] for v in obj.data.vertices],"triangle_material_indices":[f.material_index for f in obj.data.polygons],"triangle_loop_uvs":{u.name:[[list(u.data[i].uv) for i in f.loop_indices] for f in obj.data.polygons] for u in obj.data.uv_layers},"triangle_normals_local":[list(f.normal) for f in obj.data.polygons],"triangle_corner_normals_local":[[list(obj.data.corner_normals[i].vector) for i in f.loop_indices] for f in obj.data.polygons],"normal_local_to_world":[list(r) for r in obj.matrix_world.inverted().transposed().to_3x3()]} for obj in meshes},"rigs":{rig.name:[{"name":b.name,"parent":b.parent.name if b.parent else None,"head":list(b.head_local),"tail":list(b.tail_local),"matrix_local":[list(v) for v in b.matrix_local],"pose_matrix_basis":[list(v) for v in rig.pose.bones[b.name].matrix_basis],"rotation_mode":rig.pose.bones[b.name].rotation_mode} for b in rig.data.bones] for rig in h["armatures"](False)}}
    for obj in meshes:
        mesh = obj.data
        custom = [a for a in mesh.attributes if a.name in {"custom_normal", ".custom_normal"}]
        data["meshes"][obj.name]["custom_normal_storage"] = [{"name": a.name, "domain": a.domain, "type": a.data_type,
            "values": [list(item.value) for item in a.data] if a.data_type == "INT16_2D" else None} for a in custom]
        data["meshes"][obj.name].update(topology_sha256=h["_mesh_region_topology"](mesh),
            topology_hash_policy="_mesh_region_topology_v1_exact_indexed_vertices_edges_loops_polygons_material_slots",
            topology_records={"vertices": [v.index for v in mesh.vertices],
                "edges": [(e.index, list(e.vertices)) for e in mesh.edges],
                "loops": [(loop.index, loop.vertex_index, loop.edge_index) for loop in mesh.loops],
                "polygons": [(f.index, f.loop_start, f.loop_total, list(f.vertices), f.material_index) for f in mesh.polygons]})
    output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(data,separators=(",",":"))+"\n",encoding="utf-8")
    if h["file_sha256"](source)!=expected: raise RuntimeError("Inspection altered source.")
    return {"operation":"inspect_mesh_landmarks","report":output.relative_to(job).as_posix(),"report_sha256":h["file_sha256"](output),"counts":{obj.name:len(obj.data.vertices) for obj in meshes},"source_immutable":True,"data_semantics":"rest mesh coordinates under current object transforms; no evaluated pose or semantic inference"}


def validate_component_dds(header, file_size, max_dimension=1024):
    import struct
    if len(header)<128 or header[:4]!=b'DDS ' or struct.unpack_from('<I',header,4)[0]!=124 or struct.unpack_from('<I',header,76)[0]!=32:
        raise ValueError('Invalid DDS header.')
    height,width=struct.unpack_from('<II',header,12)
    if max_dimension not in {1024,2048} or width!=height or width not in {128,256,512,1024,2048} or width>max_dimension: raise ValueError('DDS dimensions exceed the verified component/body texture budget.')
    depth,mips=struct.unpack_from('<II',header,24); mips=max(1,mips)
    if depth not in {0,1} or not 1<=mips<=width.bit_length() or struct.unpack_from('<I',header,112)[0]!=0:
        raise ValueError('Only bounded 2D DDS maps without arrays/cubemaps are supported.')
    flags,fourcc,bits,r,g,b,a=struct.unpack_from('<I4sIIIII',header,80)
    offset=128
    if flags==0x41 and fourcc==b'\0'*4 and (bits,r,g,b,a)==(32,0x00ff0000,0x0000ff00,0x000000ff,0xff000000):
        size=sum(max(1,width>>level)*max(1,height>>level)*4 for level in range(mips))
        if struct.unpack_from('<I',header,20)[0] not in {0,width*4}: raise ValueError('Unsupported BGRA row pitch.')
    elif flags&4 and fourcc in {b'DXT5',b'DX10'}:
        if fourcc==b'DX10':
            if len(header)<148: raise ValueError('Missing DX10 DDS extension.')
            fmt,dim,misc,array,misc2=struct.unpack_from('<IIIII',header,128)
            if fmt not in {77,78,98,99} or dim!=3 or misc!=0 or array!=1: raise ValueError('Require one alpha-capable BC3/BC7 2D DDS.')
            offset=148
        size=sum(max(1,(max(1,width>>level)+3)//4)*max(1,(max(1,height>>level)+3)//4)*16 for level in range(mips))
    else: raise ValueError('Require verified uncompressed A8R8G8B8/BGRA or alpha-capable BC3/BC7 DDS.')
    if file_size!=offset+size: raise ValueError('DDS payload size does not match declared dimensions/mips/encoding.')
    return width,height


def _component_material(req, h, job, material_name, spec, *, max_dimension=1024):
    bpy = h['bpy']
    if not isinstance(spec, dict) or set(spec) != {'shader', 'normal_packing', 'specular_packing', 'maps'} or spec['shader'] != 'PdxMeshAdvanced' or spec['normal_packing'] != 'RRxG' or spec['specular_packing'] != 'rgb_specular_alpha_glossiness':
        raise ValueError('Require explicit PdxMeshAdvanced RRxG normal and RGB specular/alpha glossiness maps.')
    if not isinstance(spec['maps'], dict) or set(spec['maps']) != {'diffuse', 'normal', 'specular'}:
        raise ValueError('Require all three exact DDS maps.')
    paths, sizes = {}, set()
    for role, row in spec['maps'].items():
        if not isinstance(row, dict) or set(row) != {'path_rel', 'sha256'}:
            raise ValueError('Map requires exact job path and SHA256.')
        path = h['within'](job, row['path_rel'])
        if path.suffix.lower() != '.dds' or not re.fullmatch(r'[A-Fa-f0-9]{64}', row['sha256']) or h['file_sha256'](path) != row['sha256'].upper():
            raise ValueError('DDS path or checksum mismatch.')
        with path.open('rb') as handle: header=handle.read(148)
        width,height=validate_component_dds(header,path.stat().st_size,max_dimension=max_dimension)
        sizes.add((width,height)); paths[role]=path
    if len(sizes)!=1: raise ValueError('Component map dimensions must match.')
    image_names = {role: material_name+'_'+role for role in paths}
    if any(bpy.data.images.get(n) for n in image_names.values()):
        raise ValueError('Component image names must be new; existing maps cannot be replaced.')
    material=bpy.data.materials.new(material_name)
    h['ensure_material_nodes'](material)
    shader=h['_principled_shader'](material)
    shader.inputs['Metallic'].default_value=0
    shader.inputs['Alpha'].default_value=1
    for role,path in paths.items():
        image=h['_load_texture_image'](path,image_names[role],non_color=role!='diffuse')
        if tuple(image.size) != next(iter(sizes)): raise ValueError('DDS decoder dimensions mismatch.')
        node=material.node_tree.nodes.new('ShaderNodeTexImage'); node.name='HOI4_'+role.upper()+'_TEXTURE'; node.image=image
        if role=='normal':
            separate=material.node_tree.nodes.new('ShaderNodeSeparateColor'); separate.mode='RGB'
            combine=material.node_tree.nodes.new('ShaderNodeCombineColor'); combine.mode='RGB'
            links=material.node_tree.links
            links.new(node.outputs['Color'],separate.inputs['Color'])
            links.new(separate.outputs['Green'],combine.inputs['Red'])
            links.new(node.outputs['Alpha'],combine.inputs['Green'])
            def math_node(op,a=None,b=None,a_value=0,b_value=0):
                n=material.node_tree.nodes.new('ShaderNodeMath'); n.operation=op
                n.inputs[0].default_value=a_value; n.inputs[1].default_value=b_value
                if a is not None: links.new(a,n.inputs[0])
                if b is not None: links.new(b,n.inputs[1])
                return n.outputs[0]
            x=math_node('SUBTRACT',math_node('MULTIPLY',separate.outputs['Green'],b_value=2),b_value=1)
            y=math_node('SUBTRACT',math_node('MULTIPLY',node.outputs['Alpha'],b_value=2),b_value=1)
            squared=math_node('ADD',math_node('MULTIPLY',x,x),math_node('MULTIPLY',y,y))
            z=math_node('SQRT',math_node('MAXIMUM',math_node('SUBTRACT',b=squared,a_value=1),b_value=0))
            encoded_z=math_node('MULTIPLY',math_node('ADD',z,b_value=1),b_value=.5)
            links.new(encoded_z,combine.inputs['Blue'])
            normal=material.node_tree.nodes.new('ShaderNodeNormalMap'); normal.name='HOI4_NORMAL_MAP'
            material.node_tree.links.new(combine.outputs['Color'],normal.inputs['Color'])
            material.node_tree.links.new(normal.outputs['Normal'],shader.inputs['Normal'])
        elif role=='specular':
            separate=material.node_tree.nodes.new('ShaderNodeSeparateColor'); separate.mode='RGB'
            material.node_tree.links.new(node.outputs['Color'],separate.inputs['Color'])
            material.node_tree.links.new(separate.outputs['Green'],shader.inputs['Specular IOR Level'])
            material.node_tree.links.new(separate.outputs['Blue'],shader.inputs['Metallic'])
            inverse=material.node_tree.nodes.new('ShaderNodeMath'); inverse.operation='SUBTRACT'; inverse.inputs[0].default_value=1
            material.node_tree.links.new(node.outputs['Alpha'],inverse.inputs[1])
            material.node_tree.links.new(inverse.outputs[0],shader.inputs['Roughness'])
        else:
            material.node_tree.links.new(node.outputs['Color'],shader.inputs['Base Color'])
    pdx=h['load_pdx'](req['io_pdx_root'])
    material[pdx['PDX_SHADER']]='PdxMeshAdvanced'; material['hoi4_pdx_shader']='PdxMeshAdvanced'
    material['hoi4_component_material_spec_sha256']=digest(spec)
    material['hoi4_component_material_maps']=json.dumps(spec,sort_keys=True)
    return material


def winding_inventory(mesh):
    edges={}
    for face in mesh.polygons:
        ids=list(face.vertices)
        for a,b in zip(ids,ids[1:]+ids[:1]):
            edges.setdefault(tuple(sorted((a,b))),[]).append((face.index,1 if a<b else -1))
    return {'boundary_edges':sum(len(v)==1 for v in edges.values()),'nonmanifold_edges':sum(len(v)>2 for v in edges.values()),'inconsistent_shared_edges':sum(len(v)==2 and v[0][1]==v[1][1] for v in edges.values())}


def repair_explicit_mesh_winding(req,h):
    p=req['payload']; job,source,output=_open(req,h); bpy=h['bpy']
    tolerance=p.get('angular_tolerance_degrees',0.25)
    if type(tolerance) not in (int,float) or not math.isfinite(tolerance) or not 0<tolerance<=0.5:raise ValueError('Explicit native normal angular tolerance must be positive and at most0.5 degrees.')
    obj=bpy.data.objects.get(p['mesh_name'])
    if obj not in h['mesh_objects']() or obj.library or obj.data.library or obj.data.shape_keys or obj.data.users!=1 or obj.get('hoi4_source_protected') or obj.get('hoi4_reference_read_only'):
        raise ValueError('Winding repair requires one exact unshared approved local working mesh.')
    mesh=obj.data; ids=p['face_indices']
    if not isinstance(ids,list) or not 1<=len(ids)<=100000 or len(set(ids))!=len(ids) or any(type(i) is not int or not 0<=i<len(mesh.polygons) for i in ids):
        raise ValueError('Require bounded exact unique existing face indices.')
    if any(len(f.vertices)!=3 for f in mesh.polygons): raise ValueError('Winding repair requires existing triangular topology.')
    # Reject non-UV corner data that requires a separate conversion contract.
    uv_names={u.name for u in mesh.uv_layers}
    if any(a.domain=='CORNER' and a.name not in uv_names and not a.name.startswith('.') and a.name!='custom_normal' for a in mesh.attributes):
        raise ValueError('Unsupported non-UV corner attributes require explicit preservation review.')
    before=h['_promotion_fingerprint'](job,[],include_sections=True)
    positions=digest([list(v.co) for v in mesh.vertices])
    faces={f.index:list(f.vertices) for f in mesh.polygons}
    corners={u.name:{f.index:{mesh.loops[i].vertex_index:list(u.data[i].uv) for i in f.loop_indices} for f in mesh.polygons} for u in mesh.uv_layers}
    from mesh_winding_repair import _corner_normals, _verify_normal_signs
    original_normals=_corner_normals(mesh); selected_faces=set(ids)
    unset_normals=[]
    for key,value in list(original_normals.items()):
        if sum(x*x for x in value)<1e-24:
            if key[0] not in selected_faces:
                raise ValueError('Untouched corner has undefined source normal: '+repr(key))
            geometric=tuple(mesh.polygons[key[0]].normal)
            if sum(x*x for x in geometric)<1e-24:
                raise ValueError('Selected face has no geometric normal for explicit unset-normal repair: '+repr(key))
            original_normals[key]=geometric
            unset_normals.append({'face_vertex':key,'source_normal':value,'geometric_source_normal':geometric})
    topology_before=winding_inventory(mesh)
    for i in ids: mesh.polygons[i].flip()
    for u in mesh.uv_layers:
        for f in mesh.polygons:
            for i in f.loop_indices: u.data[i].uv=corners[u.name][f.index][mesh.loops[i].vertex_index]
    mesh.update()
    desired=[None]*len(mesh.loops)
    for face in mesh.polygons:
        sign=-1 if face.index in selected_faces else 1
        for index in face.loop_indices:
            source_normal=original_normals[(face.index,mesh.loops[index].vertex_index)]
            magnitude=math.sqrt(sum(x*x for x in source_normal))
            desired[index]=tuple(sign*x/magnitude for x in source_normal)
    mesh.normals_split_custom_set(desired)
    mesh.update()
    normal_proof=_verify_normal_signs(mesh,original_normals,selected_faces,angular_tolerance_degrees=tolerance)
    if digest([list(v.co) for v in mesh.vertices])!=positions: raise RuntimeError('Winding repair moved vertices.')
    for f in mesh.polygons:
        old=faces[f.index]; new=list(f.vertices)
        expected=list(reversed(old)) if f.index in set(ids) else old
        if not any(new==expected[n:]+expected[:n] for n in range(3)): raise RuntimeError('Unexpected face connectivity change.')
        for u in mesh.uv_layers:
            if any(list(u.data[i].uv)!=corners[u.name][f.index][mesh.loops[i].vertex_index] for i in f.loop_indices): raise RuntimeError('Corner UV association changed.')
    after=h['_promotion_fingerprint'](job,[],include_sections=True)
    for section in ('objects','rigs','materials','images','actions','scene'):
        if before['sha256'][section]!=after['sha256'][section]: raise RuntimeError('Winding repair changed '+section)
    for n,row in before['sections']['geometry'].items():
        compare=after['sections']['geometry'][n]
        keys=('vertices','polygons','loops','weights','groups','materials','uv_settings','uv_active_index','properties') if n==obj.name else row.keys()
        if any(row[k]!=compare[k] for k in keys): raise RuntimeError('Winding repair changed preserved mesh data.')
    topology_after=winding_inventory(mesh)
    if any(topology_after[k]!=topology_before[k] for k in ('boundary_edges','nonmanifold_edges')) or topology_after['inconsistent_shared_edges']>topology_before['inconsistent_shared_edges']:
        raise RuntimeError('Winding repair changed topology or increased inconsistent edges.')
    mesh_name=obj.name
    report=_finish(req,h,job,source,output,{'operation':'repair_explicit_mesh_winding','mesh':obj.name,'face_indices':ids,'face_indices_sha256':digest(ids),'topology_before':topology_before,'topology_after':topology_after,'positions_preserved':True,'corner_uvs_preserved':True,'rig_weights_actions_materials_preserved':True,'normal_policy':'preserve every unaffected corner normal; negate only explicitly flipped face corners','normal_sign_proof':normal_proof,'selected_unset_normal_replacements':unset_normals,'status':'saved_pending_reopen_normal_proof'})

    bpy.ops.wm.open_mainfile(filepath=str(output),use_scripts=False)
    report['reopened_normal_sign_proof']=_verify_normal_signs(bpy.data.objects[mesh_name].data,original_normals,selected_faces,angular_tolerance_degrees=tolerance)
    report['status']='repaired_requires_culling_on_visual_and_export_reimport_review'
    (job/report['report']).write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return report


def _root_vertical_contact(h,rig,root,meshes,frame,clearance,excluded=()):
    from mathutils import Matrix,Vector
    bpy=h['bpy']; bpy.context.scene.frame_set(frame); bpy.context.view_layer.update()
    if root.parent is not None or rig.constraints or root.constraints:
        raise ValueError('Pure vertical contact requires an unconstrained true skeleton root.')
    original=root.location.copy(); head=rig.matrix_world@root.head
    basis=[]
    for axis in range(3):
        root.location=original; root.location[axis]+=1; bpy.context.view_layer.update()
        basis.append((rig.matrix_world@root.head)-head)
    root.location=original; bpy.context.view_layer.update()
    matrix=Matrix(basis).transposed()
    if abs(matrix.determinant())<1e-10: raise ValueError('Root location world basis is singular.')
    before,maximum=h['evaluated_contact_bounds'](meshes,list(excluded))
    delta=matrix.inverted()@Vector((0,0,clearance-before.z))
    root.location=original+delta
    root.keyframe_insert(data_path='location',frame=frame,group=root.name)
    bpy.context.view_layer.update()
    after,after_max=h['evaluated_contact_bounds'](meshes,list(excluded))
    displacement=(rig.matrix_world@root.head)-head
    if max(abs(displacement.x),abs(displacement.y))>1e-5 or abs(after.z-clearance)>1e-4:
        raise RuntimeError('Root-local correction failed pure world-Z/contact tolerance.')
    return {'frame':frame,'before':before.z,'after':after.z,'root_location_delta':list(delta),'world_displacement':list(displacement),'root_location_world_basis':[list(row) for row in matrix]}


def ground_existing_action(req,h):
    p=req['payload']; job,source,output=_open(req,h); bpy=h['bpy']
    rig=bpy.data.objects.get(p['target_armature_name']); meshes=h['mesh_objects']()
    if h['armatures']()!=[rig] or not meshes: raise ValueError('Require the exact unique working rig and meshes.')
    action=bpy.data.actions.get(p['source_action_name'])
    if action is None or h['_mesh_region_action_hash'](action)!=p['expected_action_sha256'].upper(): raise ValueError('Reviewed source action hash mismatch.')
    name(p['target_action_name'])
    if bpy.data.actions.get(p['target_action_name']): raise ValueError('Grounded action requires a new name.')
    root=rig.pose.bones.get(p['root_bone'])
    if root is None or root.parent is not None: raise ValueError('Require exact true skeleton root.')
    excluded=p.get('excluded_contact_bones',[])
    if not isinstance(excluded,list) or len(excluded)>128 or not set(excluded)<=set(rig.pose.bones.keys()): raise ValueError('Invalid exact contact bone exclusions.')
    kind=action.get('hoi4_animation_source_kind','')
    if kind=='manual_blender_gpt6_astra' and re.fullmatch('[A-Fa-f0-9]{64}',str(action.get('hoi4_manual_action_spec_sha256',''))):
        provenance={'source_kind':kind,'manual_spec_sha256':action['hoi4_manual_action_spec_sha256']}
    elif kind in {'meshy_animate','professional_source'}:
        provenance=h['action_provenance'](action)
    elif rig.get('hoi4_promotion_operation')=='promote_accepted_reimport' and all(obj.get('hoi4_promotion_source_sha256')==rig.get('hoi4_promotion_source_sha256') for obj in meshes):
        provenance={'source_kind':'accepted_recovered_checkpoint','source_sha256':rig['hoi4_promotion_source_sha256'],'validation_sha256':rig['hoi4_promotion_validation_sha256']}
        for relkey,hashkey in [('hoi4_promotion_source','hoi4_promotion_source_sha256'),('hoi4_promotion_validation','hoi4_promotion_validation_sha256')]:
            if h['file_sha256'](h['within'](job,rig[relkey]))!=rig[hashkey]: raise ValueError('Recovered lineage checksum mismatch.')
    else: raise ValueError('No retained reviewed manual/provider/recovered source lineage.')
    if rig.constraints or any(b.constraints for b in rig.pose.bones) or (rig.animation_data and any(not t.mute for t in rig.animation_data.nla_tracks)):
        raise ValueError('Grounding requires unconstrained explicit bone motion without active NLA.')
    before_actions={a.name:h['_mesh_region_action_hash'](a) for a in bpy.data.actions}
    signature=_mesh_signature(meshes)
    corrected=action.copy(); corrected.name=p['target_action_name']; corrected.use_fake_user=True
    rig.animation_data_create(); rig.animation_data.action=corrected
    start,end=map(int,action.frame_range)
    if not 0<=start<end<=start+1200: raise ValueError('Grounding requires a bounded integer action range.')
    path='pose.bones["'+root.name+'"].location'
    def body_keys(a):
        return digest([(c.data_path,c.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in c.keyframe_points]) for c,_ in h['action_fcurves'](a) if c.data_path!=path])
    original_body=body_keys(corrected)
    # Densify all root-location channels before changing any value so each
    # sampled original frame retains its own baseline, without accumulated edits.
    samples=[]
    for frame in range(start,end+1):
        bpy.context.scene.frame_set(frame); samples.append((frame,list(root.location)))
    for frame,location in samples:
        root.location=location; root.keyframe_insert(data_path='location',frame=frame,group=root.name)
    frames=[_root_vertical_contact(h,rig,root,meshes,frame,0,excluded) for frame in range(start,end+1)]
    for curve,_ in h['action_fcurves'](corrected):
        if curve.data_path==path:
            for key in curve.keyframe_points: key.interpolation='LINEAR'
    if body_keys(corrected)!=original_body or any(h['_mesh_region_action_hash'](bpy.data.actions[n])!=v for n,v in before_actions.items()) or _mesh_signature(meshes)!=signature:
        raise RuntimeError('Grounding altered original action/body data.')
    corrected['hoi4_grounding_source_action_sha256']=p['expected_action_sha256'].upper()
    corrected['hoi4_grounding_policy']='root_local_pure_world_z'
    bpy.context.scene.frame_set(start)
    return _finish(req,h,job,source,output,{'operation':'ground_existing_action','source_action':action.name,'action':corrected.name,'source_provenance':provenance,'frames':frames,'body_keys_and_original_actions_preserved':True,'native_action_sha256':h['_mesh_region_action_hash'](corrected),'status':'corrected_requires_export_reimport_review'})
