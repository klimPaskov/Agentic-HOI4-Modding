"""Measure one model inside Blender (background mode) with the kit adapter's own geometry metrics.

Run by score_models.py, not by hand:

  blender.exe -b --factory-startup --python score_model.py -- --model M --label L --out out.json
        --adapter <.tools/3d_pipeline/adapter> --previews <dir> [--pdx-root <io_pdx_mesh>]
        [--exclude Icosphere] [--texture-dir D]

Reads the model, writes nothing but --out and the preview PNGs. It never saves a .blend, never
touches Blender's user preferences or add-on folders, and imports io_pdx_mesh only from the given
path for the current session (bytecode writing is switched off so that folder stays untouched).
Imported with the adapter's own `import_candidate` / `load_pdx`, measured with its
`geometry_metrics`, previewed with its `render_previews`, so a later A or B model is measured the same way.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import struct
import time
import traceback
from pathlib import Path

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True)
parser.add_argument("--label", required=True)
parser.add_argument("--out", required=True)
parser.add_argument("--adapter", required=True)
parser.add_argument("--previews", required=True)
parser.add_argument("--pdx-root", default="")
parser.add_argument("--exclude", action="append", default=[])
parser.add_argument("--texture-dir", default="")
parser.add_argument("--resolution", type=int, default=768)
parser.add_argument("--no-previews", action="store_true")
args = parser.parse_args(argv)

sys.path.insert(0, args.adapter)
import bpy
import blender_worker as bw

PREVIEW_VIEWS = ["front", "left", "rear"]  # front, side, back. "front" is the camera on the -Y side.


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def dds_header(path: Path) -> dict:
    with path.open("rb") as stream:
        head = stream.read(128)
    if head[:4] != b"DDS ":
        return {"file": path.name, "bytes": path.stat().st_size, "dds": False}
    height, width = struct.unpack("<II", head[12:20])
    fourcc = head[84:88].decode("ascii", "replace").strip("\x00")
    bits = struct.unpack("<I", head[88:92])[0]
    return {"file": path.name, "bytes": path.stat().st_size, "dds": True, "width": width, "height": height,
            "fourcc": fourcc or None, "rgb_bit_count": bits if not fourcc else None}


def image_records() -> list:
    seen, rows = set(), []
    for material in bpy.data.materials:
        if not material.use_nodes or material.node_tree is None:
            continue
        for node in material.node_tree.nodes:
            image = getattr(node, "image", None) if node.type == "TEX_IMAGE" else None
            if image is None or image.name in seen:
                continue
            seen.add(image.name)
            rows.append({
                "image": image.name,
                "material": material.name,
                "size": list(image.size),
                "packed_bytes": len(image.packed_file.data) if image.packed_file else None,
                "filepath": image.filepath or None,
                "colorspace": image.colorspace_settings.name,
            })
    return rows


def import_model(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".mesh":
        pdx = bw.load_pdx(args.pdx_root)
        pdx["import_meshfile"](str(path), imp_mesh=True, imp_skel=True, imp_locs=True, join_materials=True, bonespace=False)
        return "io_pdx_mesh"
    bw.import_candidate(path)
    return {".glb": "gltf", ".gltf": "gltf", ".fbx": "fbx", ".blend": "append"}[suffix]


def main() -> dict:
    model = Path(args.model)
    result = {"label": args.label, "model": str(model), "blender": bpy.app.version_string, "ok": False}
    result["file"] = {"bytes": model.stat().st_size, "sha256": sha256(model)}
    bw.clear_scene()
    started = time.time()
    result["importer"] = import_model(model)
    result["import_seconds"] = round(time.time() - started, 1)

    meshes = bw.mesh_objects(working_only=False)
    excluded = []
    for obj in list(meshes):
        if any(pattern.casefold() in obj.name.casefold() for pattern in args.exclude):
            record = {"name": obj.name, "vertices": len(obj.data.vertices),
                      "triangles": sum(max(0, len(p.vertices) - 2) for p in obj.data.polygons)}
            record.update(bw.geometry_metrics_for_object(obj))
            excluded.append(record)
            bpy.data.objects.remove(obj, do_unlink=True)
    result["excluded_objects"] = excluded
    meshes = bw.mesh_objects(working_only=False)
    result["mesh_objects"] = [
        {"name": o.name, "vertices": len(o.data.vertices), "polygons": len(o.data.polygons),
         "uv_layers": [layer.name for layer in o.data.uv_layers], "vertex_groups": len(o.vertex_groups)}
        for o in meshes
    ]

    started = time.time()
    geometry = bw.geometry_metrics(working_only=False, position_weld_distance=1e-6)
    result["geometry"] = geometry
    result["metrics_seconds"] = round(time.time() - started, 1)

    names = sorted({slot.material.name for o in meshes for slot in o.material_slots if slot.material})
    result["materials"] = {"materials": names, "unique_slots": len(names),
                           "slot_entries": sum(len(o.material_slots) for o in meshes)}
    result["uv"] = {"present": all(o["uv_layers"] for o in result["mesh_objects"]) and bool(meshes),
                    "objects_without_uv": [o["name"] for o in result["mesh_objects"] if not o["uv_layers"]]}
    images = image_records()
    result["textures_in_blender"] = {"count": len(images), "images": images}
    if args.texture_dir and Path(args.texture_dir).is_dir():
        result["textures_on_disk"] = [dds_header(p) for p in sorted(Path(args.texture_dir).glob("*.dds"))]
    armatures = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    result["armatures"] = [{"name": a.name, "bones": len(a.data.bones)} for a in armatures]
    result["bounding_height"] = geometry["dimensions"][2]
    result["bounding_dimensions"] = geometry["dimensions"]

    if not args.no_previews:
        try:
            preview_root = Path(args.previews)
            preview_root.mkdir(parents=True, exist_ok=True)
            started = time.time()
            written = bw.render_previews(preview_root, args.label, PREVIEW_VIEWS, working_only=False,
                                         preview_resolution=args.resolution)
            result["previews"] = {"views": PREVIEW_VIEWS, "files": written,
                                  "seconds": round(time.time() - started, 1), "resolution": args.resolution,
                                  "note": "kit render_previews, EEVEE, three area lights, camera framed on the evaluated bounds"}
        except Exception as error:  # noqa: BLE001  a preview failure must not lose the measurements
            result["previews"] = {"error": f"{type(error).__name__}: {error}", "trace": traceback.format_exc()[-1500:]}
    result["ok"] = True
    return result


try:
    payload = main()
except Exception as error:  # noqa: BLE001  any failure is written to the result file
    payload = {"label": args.label, "model": args.model, "ok": False,
               "error": f"{type(error).__name__}: {error}", "trace": traceback.format_exc()[-3000:]}
Path(args.out).write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8", newline="\n")
sys.exit(0 if payload.get("ok") else 1)
