"""Bounded skeletal stream partition and depth-aware native PDX export evidence.

Only the locked Blender worker invokes partition_skeletal_mesh_export_batches.
The pure text reader deliberately measures array entries and object/material depth.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


def exported_mesh_streams(text_path: Path) -> list[dict[str, Any]]:
    streams, stack, object_indices = [], [], {}
    current, mesh_depth = None, None

    def finish():
        nonlocal current
        if current is None:
            return
        if not all(key in current for key in ("vertices", "triangle_indices")):
            raise RuntimeError("Unable to prove complete per-stream vertex and triangle counts from PDX text export.")
        if current["maximum_index"] >= current["vertices"]:
            raise RuntimeError("PDX triangle index refers outside its own position stream.")
        streams.append(current)
        current = None

    with text_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            expanded = line.expandtabs(4).rstrip("\r\n")
            depth = len(expanded) - len(expanded.lstrip())
            if current is not None and depth <= mesh_depth:
                finish()
            while stack and stack[-1][0] >= depth:
                stack.pop()
            node = re.fullmatch(r"\s*([^():]+):\s*", expanded)
            if node:
                name = node.group(1).strip()
                if name == "mesh" and len(stack) == 2 and stack[0][1] == "object":
                    object_name = stack[-1][1]
                    index = object_indices.get(object_name, 0)
                    object_indices[object_name] = index + 1
                    current = {"stream_index": len(streams), "object_name": object_name, "mesh_index": index}
                    mesh_depth = depth
                stack.append((depth, name))
                continue
            if current is None or not stack or stack[-1] != (mesh_depth, "mesh"):
                continue
            field = re.fullmatch(r"\s*(p|tri) \((float|int),\s*(\d+)\):\s*(\[.*\])\s*", expanded)
            if field is None:
                continue
            name, kind, declared, raw = field.groups()
            key = "vertices" if name == "p" else "triangle_indices"
            if key in current or kind != ("float" if name == "p" else "int"):
                raise RuntimeError("PDX position/triangle stream is duplicated or has an invalid type.")
            values = json.loads(raw)
            count = int(declared)
            if len(values) != count or count == 0 or count % 3:
                raise RuntimeError("PDX declared stream count differs from its array or is not a positive multiple of three.")
            if name == "p":
                if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
                    raise RuntimeError("PDX position stream contains nonfinite or nonnumeric values.")
                current.update(vertices=count // 3, position_components=count)
            else:
                if any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in values):
                    raise RuntimeError("PDX triangle stream contains invalid indices.")
                current.update(triangle_indices=count, triangles=count // 3, minimum_index=min(values), maximum_index=max(values))
    finish()
    if not streams:
        raise RuntimeError("Unable to prove complete per-stream vertex and triangle counts from PDX text export.")
    return streams


def require_bounded_export_streams(streams):
    oversized = [s for s in streams if s["vertices"] > 65535 or s["triangle_indices"] > 65535]
    if oversized:
        raise RuntimeError(f"PDX export exceeded the 65,535 vertex ceiling or the project's conservative 65,535 triangle-index-entry batch budget (not an asserted engine index-count limit): {oversized}")


def _material_signature(record):
    record = json.loads(json.dumps(record))
    # A duplicate material/private tree has a new ID. Full nodes, links,
    # sockets, properties and animation are independently compared below it.
    name = record["settings"].pop("name", None)
    original = record["settings"].get("original")
    if isinstance(original, dict) and original.get("id_type") == "Material" and original.get("name") == name:
        original["name"] = "<same_material_self_id>"
    record["settings"].pop("node_tree", None)
    return record


def _partition_clone_ownership(api, result, names, clones, ownership):
    """Verify exact transaction-created clones and their sole approved mesh slots."""
    if not isinstance(ownership, dict) or set(ownership) != set(clones):
        raise RuntimeError("Partition material clones lack exact transaction ownership evidence.")
    sections = result["sections"]
    inventory = result["material_retention"]["inventory"]
    proof = {}
    for clone, source in clones.items():
        owned = ownership[clone]
        if set(owned) != {"source_material", "source_record_sha256", "object", "mesh", "slot", "material_id", "tree_id"}:
            raise RuntimeError("Partition material clone has incomplete transaction evidence.")
        obj = api.bpy.data.objects.get(owned["object"])
        material = api.bpy.data.materials.get(clone)
        if (owned["source_material"] != source or owned["object"] not in names
                or obj is None or obj.data.name != owned["mesh"] or obj.data.users != 1
                or material is None or material.name != clone
                or api._promotion_value(material) != owned["material_id"]
                or api._promotion_value(material.node_tree) != owned["tree_id"]):
            raise RuntimeError("Partition material clone is outside its declared transaction object/mesh.")
        slot = owned["slot"]
        if type(slot) is not int or not 0 <= slot < len(obj.data.materials) or obj.data.materials[slot] != material:
            raise RuntimeError("Partition material clone is not bound to its exact owned slot.")
        tree = material.node_tree
        tree_users = api.bpy.data.user_map(subset=[tree])
        if (tree not in tree_users or tree_users[tree] or not tree.is_embedded_data
                or tree.users not in {0, 1}):
            raise RuntimeError("Partition clone node tree has an independent or unproven consumer.")
        row, original = inventory[clone], inventory[source]
        expected_mesh_slots = [(owned["mesh"], slot)]
        expected_object_slots = [(owned["object"], slot, "DATA")]
        allowed_ids = [api._promotion_value(obj), api._promotion_value(obj.data)]
        if (row["mesh_slots"] != expected_mesh_slots or row["object_slots"] != expected_object_slots
                or not row["id_consumers"] or any(consumer not in allowed_ids for consumer in row["id_consumers"])
                or type(row["users"]) is not int or row["users"] != 1 + int(original["fake_user"])
                or row["fake_user"] != original["fake_user"] or row["extra_user"] is not False
                or row["local"] is not True or row["protected"] is not False or row["tree_retained"] is not False
                or original["local"] is not True or original["protected"] is not False
                or original["record_sha256"] != owned["source_record_sha256"]):
            raise RuntimeError("Partition clone/source material retention or consumers changed outside the transaction.")
        if _material_signature(sections["materials"][clone]) != _material_signature(sections["materials"][source]):
            raise RuntimeError("Partition material clone content differs from its unchanged source.")
        proof[clone] = {"ownership": owned, "retention": row, "private_embedded_tree_consumers": [],
                        "source_record_sha256": original["record_sha256"],
                        "equivalent_material_signature_sha256": api._promotion_digest(_material_signature(sections["materials"][clone]))}
    return proof


def _partition_image_consumers(api, before, after, clones, ownership):
    """Reconcile only exact node/ID users added by already verified material clones."""
    if not isinstance(before, dict) or set(before) != {"inventory", "content_sha256"} or set(after) != set(before):
        raise RuntimeError("Partition image reconciliation lacks complete baseline evidence.")
    if before["content_sha256"] != after["content_sha256"] or set(before["inventory"]) != set(after["inventory"]):
        raise RuntimeError("Partition changed image content or image datablock identities.")
    reconciled = []
    for image_name, original in before["inventory"].items():
        expected = json.loads(json.dumps(original))
        additions = []
        for clone, source in clones.items():
            source_nodes = [row for row in original["material_nodes"] if row["material"] == source]
            if not source_nodes:
                continue
            if (original["consumer_map_complete"] is not True or source not in original["material_consumers"]
                    or {"id_type": "Material", "name": source, "library": None} not in original["id_consumers"]):
                raise RuntimeError("Partition clone image lacks a complete original source consumer.")
            owned = ownership[clone]
            nodes = [dict(row, material=clone, tree=owned["tree_id"]["name"]) for row in source_nodes]
            expected["material_nodes"].extend(nodes)
            expected["material_consumers"].append(clone)
            expected["id_consumers"].append(owned["material_id"])
            expected["users"] += len(nodes)
            additions.append({"material": clone, "source_material": source, "nodes": nodes,
                              "added_users": len(nodes), "id_consumer": owned["material_id"]})
        expected["material_nodes"].sort(key=lambda row: (row["material"], row["node"]))
        expected["material_consumers"].sort()
        expected["id_consumers"].sort(key=lambda row: json.dumps(row, sort_keys=True))
        actual = after["inventory"][image_name]
        if actual != expected:
            raise RuntimeError(f"Partition image has changed content, retention, or unplanned consumers: {image_name}")
        if additions:
            reconciled.append({"image": image_name, "before": original, "after": actual,
                               "planned_clone_additions": additions, "image_content_exact": True})
    return {"accepted": True, "content_sha256": before["content_sha256"], "images": reconciled,
            "policy": "partition_transaction_exact_material_clone_consumers_only_all_image_content_retention_and_original_consumers_exact"}


def _fingerprint(api, job, names, clones, *, ownership=None, baseline_images=None, reconciliation=None):
    result = api._promotion_fingerprint(job, names, include_sections=True)
    if clones:
        clone_proof = _partition_clone_ownership(api, result, names, clones, ownership)
        image_proof = _partition_image_consumers(api, baseline_images, result["image_retention"], clones, ownership)
        if reconciliation is not None:
            reconciliation.update(material_clones=clone_proof, image_consumers=image_proof)
        # This operation-scoped projection follows the exact image proof above.
        # The shared promotion comparator and unprojected receipts remain strict.
        result["image_retention"] = json.loads(json.dumps(baseline_images))
    sections = result.pop("sections")
    for name in names:
        mesh = api.bpy.data.objects[name].data
        row = sections["geometry"][name]
        row["topology"] = api._promotion_digest([
            [list(f.vertices), clones.get(mesh.materials[f.material_index].name, mesh.materials[f.material_index].name), f.use_smooth, list(f.normal)]
            for f in mesh.polygons
        ])
        row.pop("materials")
        row["attributes"].pop("material_index", None)
    for clone, source in clones.items():
        left, right = _material_signature(sections["materials"][clone]), _material_signature(sections["materials"][source])
        if left != right:
            differences = []
            def compare(a, b, path):
                if len(differences) >= 12 or a == b:
                    return
                if isinstance(a, dict) and isinstance(b, dict):
                    for key in sorted(set(a) | set(b)):
                        compare(a.get(key), b.get(key), path + "." + key)
                elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
                    for index, (x, y) in enumerate(zip(a, b)):
                        compare(x, y, f"{path}[{index}]")
                else:
                    differences.append({"path": path, "clone": a, "source": b})
            compare(left, right, "material")
            raise RuntimeError(f"Export batch material differs from its source: {clone}: {differences}")
        sections["materials"].pop(clone)
    result["sha256"] = {k: api._promotion_digest(v) for k, v in sections.items()}
    # The native retention inventory was already captured before normalizing
    # equivalent clone IDs. Do not ask its all-material walker to recapture a
    # dictionary from which those deliberately added clones were removed.
    inventory = {name: row for name, row in result["material_retention"]["inventory"].items() if name not in clones}
    retained = {name: sections["materials"][name] for name, row in inventory.items() if not row["discardable_orphan"]}
    result["material_retention"] = {"inventory": inventory, "retained_sha256": api._promotion_digest(retained)}
    return result


def _inputs(req, api):
    job, payload = Path(req["job_root"]).resolve(), req["payload"]
    expected = {"blend_rel", "expected_source_sha256", "checkpoint_rel", "target_armature_name", "target_mesh_names", "max_export_vertices_per_batch"}
    if set(payload) != expected:
        raise ValueError("Skeletal partition accepts only its explicit hashed source and exact target contract.")
    source = api._promotion_path(job, payload["blend_rel"], ".blend")
    output = api._promotion_path(job, payload["checkpoint_rel"], ".blend", missing=True)
    if source.parent != output.parent or output.exists():
        raise ValueError("Skeletal partition requires a new sibling checkpoint; overwrites are forbidden.")
    expected_sha = payload["expected_source_sha256"]
    if not isinstance(expected_sha, str) or not re.fullmatch(r"[A-Fa-f0-9]{64}", expected_sha) or api.file_sha256(source) != expected_sha.upper():
        raise ValueError("Skeletal partition source SHA256 differs from the explicitly accepted input.")
    maximum = payload["max_export_vertices_per_batch"]
    if isinstance(maximum, bool) or not isinstance(maximum, int) or not 3 <= maximum <= 65535:
        raise ValueError("max_export_vertices_per_batch must be an integer in [3, 65535].")
    names = payload["target_mesh_names"]
    if not isinstance(names, list) or not 1 <= len(names) <= 16 or any(not isinstance(n, str) for n in names) or len(set(names)) != len(names):
        raise ValueError("Skeletal partition requires one to sixteen unique exact mesh names.")
    for name in names:
        api._locator_exact_name(name, "target_mesh_names")
    api._locator_exact_name(payload["target_armature_name"], "target_armature_name")
    report_path = job / "blender" / "reports" / f"{output.stem}_partition.json"
    if report_path.exists():
        raise ValueError("Skeletal partition evidence already exists; use a new checkpoint name.")
    return job, source, output, report_path, maximum, names


def partition_skeletal_mesh_export_batches(req, api):
    """Only identical material copies and polygon material assignments may change."""
    job, source, output, report_path, maximum, names = _inputs(req, api)
    bpy, payload = api.bpy, req["payload"]
    expected_sha = payload["expected_source_sha256"].upper()
    report = {"operation": "partition_skeletal_mesh_export_batches", "status": "fail", "source_blend": payload["blend_rel"], "source_sha256": expected_sha, "checkpoint": payload["checkpoint_rel"], "report": report_path.relative_to(job).as_posix(), "maximum_export_vertices": maximum, "conservative_triangle_index_entry_budget": maximum, "policy": "identical_material_copies_and_polygon_material_indices_only", "new_provider_call": False}
    try:
        bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
        targets = [bpy.context.scene.objects.get(n) for n in names]
        rig = bpy.context.scene.objects.get(payload["target_armature_name"])
        if rig is None or rig.type != "ARMATURE" or rig.library or rig.override_library or rig.data.library or rig.get("hoi4_source_protected") or rig.get("hoi4_reference_read_only"):
            raise ValueError("Skeletal partition requires the exact local, unprotected source armature.")
        if set(o.name for o in api.mesh_objects()) != set(names):
            raise ValueError("Skeletal partition targets must cover exactly all approved working meshes.")
        for obj in targets:
            if obj is None or obj.type != "MESH" or obj.library or obj.override_library or obj.data.library or obj.data.users != 1 or obj.get("hoi4_source_protected") or obj.get("hoi4_reference_read_only"):
                raise ValueError("Skeletal partition rejects missing, shared, linked or protected mesh data.")
            if obj.data.shape_keys or len(obj.modifiers) != 1 or obj.modifiers[0].type != "ARMATURE" or obj.modifiers[0].object != rig:
                raise ValueError("Skeletal partition requires one existing armature modifier and no shape keys or geometry modifiers.")
            if not obj.data.polygons or any(len(f.vertices) != 3 for f in obj.data.polygons):
                raise ValueError("Skeletal partition requires an already triangular mesh.")
            if not obj.data.materials or any(m is None or not m.get("shader") for m in obj.data.materials):
                raise ValueError("Every source material slot must be a nonempty PDX material.")
        report["geometry_before"] = api.geometry_metrics()
        report["weights_before"] = api.weight_metrics()
        report["locators_before"] = api.locator_records()
        before = _fingerprint(api, job, names, {})
        report["fingerprints_before"] = before
        clones, ownership, rows = {}, {}, []
        for obj in targets:
            mesh = obj.data
            initial_materials = list(mesh.materials)
            original_indices = [f.material_index for f in mesh.polygons]
            if any(i >= len(initial_materials) for i in original_indices):
                raise ValueError("A polygon references an absent source material slot.")
            batches = []
            for source_index, material in enumerate(initial_materials):
                face_ids = [i for i, slot in enumerate(original_indices) if slot == source_index]
                if not face_ids:
                    raise ValueError("Empty source material slots are not exportable; implicit cleanup is forbidden.")
                for number, start in enumerate(range(0, len(face_ids), maximum // 3)):
                    faces = face_ids[start:start + maximum // 3]
                    slot = source_index
                    if number:
                        clone_name = f"{material.name}_skeletal_batch_{number + 1:02d}"
                        suffix = 1
                        while clone_name in bpy.data.materials:
                            clone_name = f"{material.name}_skeletal_batch_{number + 1:02d}.{suffix:03d}"
                            suffix += 1
                        duplicate = material.copy()
                        # Native ID.copy clears fake-user retention; the batch
                        # must retain the source's full material settings.
                        duplicate.use_fake_user = material.use_fake_user
                        duplicate.name = clone_name
                        if duplicate.name != clone_name:
                            raise RuntimeError("Partition native clone identity differs from its planned transaction name.")
                        mesh.materials.append(duplicate)
                        slot = len(mesh.materials) - 1
                        clones[duplicate.name] = material.name
                        ownership[duplicate.name] = {"source_material": material.name,
                            "source_record_sha256": before["material_retention"]["inventory"][material.name]["record_sha256"],
                            "object": obj.name, "mesh": mesh.name, "slot": slot,
                            "material_id": api._promotion_value(duplicate), "tree_id": api._promotion_value(duplicate.node_tree)}
                    for face_id in faces:
                        mesh.polygons[face_id].material_index = slot
                    batches.append({"material_slot_index": slot, "material": mesh.materials[slot].name, "source_material_index": source_index, "source_material": material.name, "triangles": len(faces), "triangle_indices": len(faces) * 3, "worst_case_export_vertices": len(faces) * 3, "polygon_indices_sha256": api._promotion_digest(faces)})
            mesh.update()
            rows.append({"object": obj.name, "export_object_name": mesh.name, "batches": sorted(batches, key=lambda r: r["material_slot_index"])})
        bpy.context.view_layer.update()
        report.update(objects=rows, material_clones=clones, material_clone_ownership=ownership)
        report["partition_consumer_reconciliation"] = {}
        changed = _fingerprint(api, job, names, clones, ownership=ownership, baseline_images=before["image_retention"], reconciliation=report["partition_consumer_reconciliation"])
        report["fingerprints_after_partition"] = changed
        if before != changed:
            raise RuntimeError("Skeletal partition changed data beyond equivalent material partition assignments.")
        if api.file_sha256(source) != expected_sha or output.exists():
            raise RuntimeError("Skeletal partition immutable source or output guard changed during processing.")
        output.parent.mkdir(parents=True, exist_ok=True)
        saved = bpy.ops.wm.save_as_mainfile(filepath=str(output), copy=True, relative_remap=False)
        if "FINISHED" not in saved:
            raise RuntimeError("Skeletal partition checkpoint save failed.")
        bpy.ops.wm.open_mainfile(filepath=str(output), use_scripts=False)
        report["reopened_consumer_reconciliation"] = {}
        reopened = _fingerprint(api, job, names, clones, ownership=ownership, baseline_images=before["image_retention"], reconciliation=report["reopened_consumer_reconciliation"])
        report["fingerprints_reopened"] = reopened
        report["reopen_comparison"] = api._promotion_reopen_comparison(changed, reopened)
        if not report["reopen_comparison"]["accepted"]:
            raise RuntimeError("Skeletal partition saved/reopened invariants differ.")
        report["geometry_after"] = api.geometry_metrics()
        report["weights_after"] = api.weight_metrics()
        report["locators_after"] = api.locator_records()
        if api.file_sha256(source) != expected_sha:
            raise RuntimeError("Skeletal partition source changed during processing.")
        report.update(status="pass", source_immutable=True, checkpoint_sha256=api.file_sha256(output), checkpoint_bytes=output.stat().st_size)
    except Exception as exc:
        report.update(error=str(exc), output_approved=False)
        raise
    finally:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
    return report
