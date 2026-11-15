"""Size a Tripo quadruped mount and its rider by measured rules, from the model file alone (no Blender).

Vanilla's mounts are the scale: `cavalry_horse.mesh` has its `Saddle_Node` 12.566 units up, under `pdxmesh` scale 0.45 and
entity scale 0.65, so a horse's back stands `VANILLA_WITHERS_MAP` units tall on the map. Its rider entity (scale 0.8) is
attached to that node, and an attached entity's scale multiplies its parent's: vanilla's rifle (5.38 units long, scale 1.0)
held by the 7.35-unit soldier (entity scale 0.8) is 0.73 of the soldier's height on the map only if it does. So vanilla's
rider is `VANILLA_RIDER_MAP` = 7.35 x 0.8 x 0.65 units tall on the map.

- **Mount.** The back of the mount stands `size_vs_horse` times a horse's on the map (`size_vs_horse` is the species'
  typical withers height over a horse's, a fact the job states with its source; 1 for a horse). The model's back is
  measured from its own geometry: the top of the body between the legs (`quadruped_layout.detect_landmarks`), or, for a
  mount that carries a load, the load's cut (`quadruped_load.find_load`), where the load rests on the back. The mesh height
  is then the back's map height over the back's share of the model's height, divided by the entity scale.
- **Rider.** The rider entity is vanilla's rider size on the map: its entity scale is `VANILLA_RIDER_MAP` over its own
  mesh height and over the mount's entity scale. In the mount's mesh units it is that height divided by the mount's entity
  scale, which the rig uses to place the `Saddle_Node`.
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np

ADAPTER = Path(__file__).resolve().parents[1] / "adapter"
if str(ADAPTER) not in sys.path:
    sys.path.insert(0, str(ADAPTER))

import quadruped_layout as ql
import quadruped_load as qload

VANILLA_HORSE_SADDLE_NODE = 12.566  # cavalry_horse.mesh, Saddle_Node height in mesh units
VANILLA_HORSE_PDXMESH_SCALE = 0.45
VANILLA_HORSE_ENTITY_SCALE = 0.65
VANILLA_WITHERS_MAP = VANILLA_HORSE_SADDLE_NODE * VANILLA_HORSE_PDXMESH_SCALE * VANILLA_HORSE_ENTITY_SCALE  # 3.676
VANILLA_RIDER_MESH = 7.3518  # western_european_infantry.mesh
VANILLA_RIDER_ENTITY_SCALE = 0.8
VANILLA_RIDER_MAP = VANILLA_RIDER_MESH * VANILLA_RIDER_ENTITY_SCALE * VANILLA_HORSE_ENTITY_SCALE  # 3.823


def read_glb(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Every triangle mesh in a GLB as (points in the working frame: +Z up, triangles); node transforms are not applied (Tripo writes none)."""

    data = Path(path).read_bytes()
    offset, document, binary = 12, None, b""
    while offset < len(data):
        length, kind = struct.unpack_from("<II", data, offset)
        chunk = data[offset + 8 : offset + 8 + length]
        if kind == 0x4E4F534A:
            document = json.loads(chunk)
        else:
            binary = chunk
        offset += 8 + length
    if document is None:
        raise ValueError(f"{path} is not a GLB")

    def accessor(index: int) -> np.ndarray:
        item = document["accessors"][index]
        view = document["bufferViews"][item["bufferView"]]
        dtype = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}[item["componentType"]]
        width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[item["type"]]
        values = np.frombuffer(binary, dtype, item["count"] * width, view.get("byteOffset", 0) + item.get("byteOffset", 0))
        return values.reshape(item["count"], width) if width > 1 else values

    points, triangles, base = [], [], 0
    for mesh in document["meshes"]:
        for primitive in mesh["primitives"]:
            if primitive.get("mode", 4) != 4:
                continue
            p = accessor(primitive["attributes"]["POSITION"]).astype(float)
            t = accessor(primitive["indices"]).astype(np.int64).reshape(-1, 3) if "indices" in primitive else np.arange(len(p)).reshape(-1, 3)
            points.append(p)
            triangles.append(t + base)
            base += len(p)
    p = np.concatenate(points)
    # glTF is +Y up; the working frame is +Z up (Blender's import: x, -z, y).
    return np.c_[p[:, 0], -p[:, 2], p[:, 1]], np.concatenate(triangles)


def back_share(points: np.ndarray, triangles: np.ndarray, load: bool) -> Dict[str, float]:
    """The back's height as a share of the model's height, measured on the body (the load's cut for a loaded mount)."""

    ground = float(points[:, 2].min())
    height = float(points[:, 2].max()) - ground
    if load:
        found = qload.find_load(points, triangles)
        body = points[~found.mask]
        back = found.cut_z - ground
    else:
        body, back = points, None
    # The landmark rules want the animal's length along Y.
    if float(np.ptp(body[:, 0])) > float(np.ptp(body[:, 1])):
        body = body[:, [1, 0, 2]]
    landmarks = ql.detect_landmarks(body, back_z=back)
    return {"back_share": float(landmarks["back_z"]) / height, "model_height": height, "back": float(landmarks["back_z"])}


FOOTPRINT_CELLS = 24  # a rider's height spans this many footprint cells


def rider_footprint(folder: Path, stem: str, roles: Dict[str, str]) -> Dict[str, Any]:
    """Where the rider's clips carry it in plan: the cells (a 24th of its height wide) that any of its points covers in some frame
    of the clips the mount's roles play, as integer (x, y) cells in the working frame (+X its left, -Y its front) with the node at
    the origin, and the farthest reach from the node as a share of its height. The rest pose is not played, so it does not count."""

    from lib import pdx_deform

    mesh = pdx_deform.load_mesh(Path(folder) / f"{stem}.mesh")
    cell = mesh.height / FOOTPRINT_CELLS
    played = {roles.get(role, role) for role in ("idle", "move", "attack", "defend", "retreat", "death")}
    cells, reach = set(), 0.0
    for role in sorted(played):
        path = Path(folder) / f"{stem}_{role}.anim"
        if not path.is_file():
            continue
        anim = pdx_deform.load_anim(path)
        matrices = pdx_deform.skinning_matrices(mesh, anim)
        for frame in range(0, anim.frames, 2):
            posed = pdx_deform.skin(mesh, matrices[frame])
            reach = max(reach, float(np.hypot(posed[:, 0], posed[:, 2]).max()))
            # The .mesh is +Y up with the unit facing -Z; the working frame is +Z up facing -Y.
            cells.update(map(tuple, np.unique(np.floor(posed[:, [0, 2]] / cell).astype(int), axis=0).tolist()))
    return {"cells": sorted(cells), "cell_share": 1.0 / FOOTPRINT_CELLS, "reach_share": reach / max(mesh.height, 1e-9)}


def mount_size(glb: Path, entity_scale: float, size_vs_horse: float, load: bool,
               rider_mesh_height: Optional[float] = None) -> Dict[str, Any]:
    """The mesh height (`blender_target_height_m`) that puts the mount's back at `size_vs_horse` horses on the map, and the rider's scale."""

    points, triangles = read_glb(glb)
    measured = back_share(points, triangles, load)
    back_map = VANILLA_WITHERS_MAP * float(size_vs_horse)
    target = back_map / entity_scale / measured["back_share"]
    rider_mesh = float(rider_mesh_height or VANILLA_RIDER_MESH)
    rider_scale = VANILLA_RIDER_MAP / rider_mesh / entity_scale
    return {
        "rule": "back on the map = vanilla horse's Saddle_Node height on the map x size_vs_horse; rider = vanilla rider's map height",
        "vanilla_withers_map": round(VANILLA_WITHERS_MAP, 4),
        "size_vs_horse": float(size_vs_horse),
        "back_map": round(back_map, 4),
        "back_share": round(measured["back_share"], 4),
        "target_height_m": round(target, 4),
        "map_height": round(target * entity_scale, 4),
        "entity_scale": float(entity_scale),
        "rider_map_height": round(VANILLA_RIDER_MAP, 4),
        "rider_mesh_height": round(rider_mesh, 4),
        "rider_entity_scale": round(rider_scale, 4),
        "rider_height_in_mount_mesh": round(rider_mesh * rider_scale, 4),
    }
