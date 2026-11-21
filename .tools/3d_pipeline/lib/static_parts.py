"""Static models made in parts (Tripo's Generate in Parts): each part reduced on its own to a share of the budget.

A model exported in parts has one mesh node per part (the hull, the turret, each track band, a lion, a chimney).
Collapsing the joined model straight to a vanilla budget spends the triangles where the surface is large and crumples
what is small and detailed: an HD tank of 18,702 triangles reduced as one to a light tank's 3,948 lost its bogies and
its hull plates. The static route therefore keeps the parts apart and reduces each one on its own:

- `part_need` measures what a part needs: its surface area and its bend (the length of its edges times the angle
  between the two faces each one joins, so a bogie, a rivet row or a lion's mane counts more than a flat plate).
- `allocate` shares a triangle target between the parts by need (half by area, half by bend), never more than a part
  has and never less than `MIN_PART_TRIANGLES` (or all of a smaller part).
- `reduce_parts` reduces each part to its share with the caller's reducer (Blender's Decimate in the stage) and checks
  every result with the unit route's shape check (`lib.tripo_shape`: no new shells, front, side and top silhouette
  agreement of at least `part_shape_iou`) and a closure check (no more open edges than the part had). A part that
  fails gets `GROWTH` times its share, taken from the others, and every part whose share changed is reduced and
  checked again. When the parts that fail need more than the target holds, it stops with `PartsBudgetError`, which
  names them and what they need.
- `whole_parts` says which parts lie wholly on one side of a rigid-part cut (a tank's turret over its turret cut), so
  the stage moves a part whole onto its bone instead of slicing it.

Positions are (N, 3) float arrays and triangles (T, 3) integer indices. No Blender here.
"""

from __future__ import annotations

import json
import math
import struct
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from lib import tripo_shape

PART_LAYER = "static_part"  # a face attribute in the Blender stage: the part a face came from, counted from 1 (0: a cap or a new face)
NEED_AREA_WEIGHT = 0.5  # the rest of a part's need is its bend
MIN_PART_TRIANGLES = 24  # a part is never asked to go below this (an 8-corner box has 12)
GROWTH = 1.5  # a part whose shape failed asks for this much more
MAX_ROUNDS = 10
WHOLE_SHARE = 0.9  # a part with this share of its area on one side of a cut goes whole to that side
WELD_SHARE = 1e-5  # vertices within this share of a part's size are one (as the stage's weld)

Mesh = Tuple[np.ndarray, np.ndarray]


class PartsBudgetError(ValueError):
    """The parts that fail their shape check need more triangles than the target holds."""


def _welded(positions: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    size = float(np.ptp(positions, axis=0).max()) if len(positions) else 0.0
    return tripo_shape.weld(positions, size * WELD_SHARE)[np.asarray(triangles, dtype=np.int64)]


def _edge_counts(welded: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Unique welded edges, how many triangles use each, and for each triangle side the index of its edge."""

    sides = np.concatenate([welded[:, [0, 1]], welded[:, [1, 2]], welded[:, [2, 0]]])
    edges, inverse, counts = np.unique(np.sort(sides, axis=1), axis=0, return_inverse=True, return_counts=True)
    return edges, counts, inverse.ravel()


def open_edges(positions: np.ndarray, triangles: np.ndarray) -> int:
    """Welded edges used by one triangle only."""

    if not len(triangles):
        return 0
    _edges, counts, _inverse = _edge_counts(_welded(positions, triangles))
    return int((counts == 1).sum())


def part_need(positions: np.ndarray, triangles: np.ndarray) -> dict:
    """A part's triangle count, surface area and bend (sum of edge length times the angle between its two faces)."""

    positions = np.asarray(positions, dtype=float)
    triangles = np.asarray(triangles, dtype=np.int64)
    if not len(triangles):
        return {"triangles": 0, "area": 0.0, "bend": 0.0}
    a, b, c = (positions[triangles[:, k]] for k in range(3))
    cross = np.cross(b - a, c - a)
    doubled = np.linalg.norm(cross, axis=1)
    normals = cross / np.maximum(doubled, 1e-20)[:, None]
    welded = _welded(positions, triangles)
    edges, counts, inverse = _edge_counts(welded)
    count = len(triangles)
    owner = np.concatenate([np.arange(count)] * 3)
    bend = 0.0
    shared = np.flatnonzero(counts == 2)
    if len(shared):
        order = np.argsort(inverse, kind="stable")
        starts = np.searchsorted(inverse[order], shared)
        first, second = owner[order[starts]], owner[order[starts + 1]]
        cosine = np.clip((normals[first] * normals[second]).sum(axis=1), -1.0, 1.0)
        representative = np.zeros((int(welded.max()) + 1, 3))
        representative[welded.ravel()] = positions[triangles.ravel()]
        lengths = np.linalg.norm(representative[edges[shared, 0]] - representative[edges[shared, 1]], axis=1)
        bend = float((lengths * np.arccos(cosine)).sum())
    return {"triangles": count, "area": float(doubled.sum() / 2), "bend": bend}


def need_weights(needs: Sequence[dict]) -> List[float]:
    """Each part's share of the whole need: NEED_AREA_WEIGHT by area, the rest by bend (by area alone when nothing bends)."""

    area = sum(n["area"] for n in needs) or 1.0
    bend = sum(n["bend"] for n in needs)
    weight = NEED_AREA_WEIGHT if bend > 0 else 1.0
    return [weight * n["area"] / area + (1 - weight) * (n["bend"] / bend if bend > 0 else 0.0) for n in needs]


def allocate(needs: Sequence[dict], target: int, lower: Optional[Sequence[int]] = None) -> List[int]:
    """Triangles for each part out of `target`, in proportion to its need: at most what it has, at least its lower bound
    (`lower`, else `MIN_PART_TRIANGLES` or all of a smaller part). Raises PartsBudgetError when the lower bounds exceed it."""

    counts = [int(n["triangles"]) for n in needs]
    floors = [min(c, max(MIN_PART_TRIANGLES, int(lower[i]) if lower else 0)) for i, c in enumerate(counts)]
    if sum(floors) > target:
        raise PartsBudgetError(f"the parts need at least {sum(floors)} triangles, over the target of {target}")
    if sum(counts) <= target:
        return counts
    weights = need_weights(needs)
    fixed: Dict[int, int] = {}
    while True:
        free = [i for i in range(len(counts)) if i not in fixed]
        left = target - sum(fixed.values())
        total = sum(weights[i] for i in free)
        shares = {i: left * (weights[i] / total if total > 0 else 1.0 / len(free)) for i in free}
        over = [i for i in free if shares[i] >= counts[i]]
        under = [i for i in free if shares[i] < floors[i]]
        if not over and not under:
            break
        for i in over:
            fixed[i] = counts[i]
        if not over:
            for i in under:
                fixed[i] = floors[i]
    result = [fixed.get(i, 0) for i in range(len(counts))]
    for i in free:
        result[i] = max(floors[i], min(counts[i], int(math.floor(shares[i]))))
    return result


def part_problems(original: Mesh, reduced: Mesh, min_iou: float = tripo_shape.MIN_IOU) -> Tuple[dict, List[str]]:
    """The shape check of one reduced part (`lib.tripo_shape`) plus its closure: no more open edges than it had."""

    shape = tripo_shape.shape_report(original, reduced)
    problems = tripo_shape.shape_problems(shape, min_iou)
    before, after = open_edges(*original), open_edges(*reduced)
    shape["open_edges_before"], shape["open_edges_after"] = before, after
    if after > before:
        problems.append(f"the reduction opened the part ({after} open edges, it had {before})")
    return shape, problems


def reduce_parts(names: Sequence[str], originals: Sequence[Mesh], target: int, reduce: Callable[[int, int], Mesh],
                 min_iou: float = tripo_shape.MIN_IOU, checker: Callable[[Mesh, Mesh, float], Tuple[dict, List[str]]] = part_problems) -> dict:
    """Share `target` triangles between the parts by need and reduce each to its share, growing the share of a part whose
    shape fails. `reduce(i, triangles)` returns part i reduced from its original to about that many triangles; the
    chosen result of each part is the last one asked for. Returns the receipt; raises PartsBudgetError when it cannot."""

    needs = [part_need(*mesh) for mesh in originals]
    counts = [n["triangles"] for n in needs]
    lower = [0] * len(needs)
    passed: Dict[int, int] = {}  # the smallest share each part passed at
    tried: Dict[int, int] = {}
    results: Dict[int, dict] = {}
    attempts: List[List[dict]] = [[] for _ in needs]
    rounds = 0
    while True:
        rounds += 1
        shares = allocate(needs, target, lower)
        failing = []
        for i, share in enumerate(shares):
            if tried.get(i) == share:
                if results[i]["problems"]:
                    failing.append(i)
                continue
            # the reducer is called for every share, a whole part too, so the result it keeps is always the chosen one
            mesh = reduce(i, share)
            whole = share >= counts[i]
            shape, problems = (({"iou": {v: 1.0 for v in tripo_shape.VIEWS}, "open_edges_before": open_edges(*mesh), "open_edges_after": open_edges(*mesh)}, [])
                               if whole else checker(originals[i], mesh, min_iou))
            tried[i] = share
            results[i] = {"share": share, "triangles": int(len(mesh[1])), "iou": shape["iou"], "open_edges": [shape["open_edges_before"], shape["open_edges_after"]], "problems": problems}
            attempts[i].append({"share": share, "triangles": int(len(mesh[1])), "iou": shape["iou"], "problems": problems})
            if problems:
                failing.append(i)
            else:
                passed[i] = min(share, passed.get(i, share))
        if not failing:
            break
        for i in failing:
            grown = min(counts[i], int(math.ceil(max(shares[i], MIN_PART_TRIANGLES) * GROWTH)))
            lower[i] = min(grown, passed[i]) if i in passed and passed[i] > shares[i] else grown
        if sum(min(c, max(MIN_PART_TRIANGLES, l)) for c, l in zip(counts, lower)) > target or rounds >= MAX_ROUNDS:
            table = "; ".join(f"{names[i]} ({counts[i]} triangles) failed at {shares[i]}: {results[i]['problems'][0]}" for i in failing)
            raise PartsBudgetError(f"the parts cannot share {target} triangles and keep their shape after {rounds} rounds: {table}. "
                                   "Give the model a larger budget, lower part_shape_iou, or make the failing part again with fewer details it does not need")
        for i in failing:
            tried.pop(i, None)
    weights = need_weights(needs)
    return {
        "target": target,
        "min_iou": min_iou,
        "rounds": rounds,
        "triangles": sum(results[i]["triangles"] for i in range(len(needs))),
        "parts": {names[i]: {"from": counts[i], "to": results[i]["triangles"], "share": results[i]["share"], "need": round(weights[i], 4),
                             "area": round(needs[i]["area"], 4), "bend": round(needs[i]["bend"], 4), "iou": results[i]["iou"],
                             "open_edges": results[i]["open_edges"], "attempts": len(attempts[i])}
                  for i in range(len(needs))},
    }


def silhouette_problems(shape: dict, min_iou: float = tripo_shape.MIN_IOU) -> List[str]:
    """The silhouette refusals of `tripo_shape.shape_problems` alone. A model in parts is judged whole this way: parts
    that only touched come apart in their own reductions, which the shell count would read as a split."""

    return [f"the {view} silhouette agrees only {value:.3f} with the original (needs {min_iou})" for view, value in shape["iou"].items() if value < min_iou]


def whole_parts(part_ids: np.ndarray, areas: np.ndarray, side: np.ndarray, share: float = WHOLE_SHARE) -> Dict[int, bool]:
    """For each part id (0 is no part) that lies at least `share` of its area on one side of a cut, which side
    (True: the side `side` marks). A part with less on both sides is cut as before and left out."""

    result = {}
    for part in np.unique(part_ids):
        if part <= 0:
            continue
        mine = part_ids == part
        total = float(areas[mine].sum())
        if total <= 0:
            continue
        on = float(areas[mine & side].sum()) / total
        if on >= share:
            result[int(part)] = True
        elif on <= 1 - share:
            result[int(part)] = False
    return result


# ---- GLB parts ----

def glb_parts(path: Path) -> List[Tuple[str, np.ndarray, np.ndarray]]:
    """Every mesh node of a GLB as (name, positions in Blender space, triangles), as Blender's importer makes one object
    of each. A part export has one per part, a plain export one."""

    from lib import static_kinds as sk
    from lib.texture_lineage import _read_glb

    document, binary = _read_glb(Path(path))
    parts: List[Tuple[str, np.ndarray, np.ndarray]] = []

    def visit(index: int, parent: np.ndarray) -> None:
        node = document["nodes"][index]
        world = parent @ sk._node_matrix(node)
        if "mesh" in node:
            positions, triangles, offset = [], [], 0
            mesh = document["meshes"][node["mesh"]]
            for primitive in mesh["primitives"]:
                if primitive.get("mode", 4) != 4:
                    continue
                p = sk._accessor(document, binary, primitive["attributes"]["POSITION"]).astype(float)
                p = p @ world[:3, :3].T + world[:3, 3]
                t = sk._accessor(document, binary, primitive["indices"]).reshape(-1, 3).astype(np.int64) if "indices" in primitive else np.arange(len(p)).reshape(-1, 3)
                positions.append(p)
                triangles.append(t + offset)
                offset += len(p)
            if positions:
                p = np.concatenate(positions)
                name = node.get("name") or mesh.get("name") or f"part_{len(parts) + 1}"
                parts.append((name, np.stack([p[:, 0], -p[:, 2], p[:, 1]], axis=1), np.concatenate(triangles)))
        for child in node.get("children", []):
            visit(child, world)

    scene = document.get("scenes", [{}])[document.get("scene", 0)]
    for root in scene.get("nodes", range(len(document.get("nodes", [])))):
        visit(root, np.eye(4))
    return parts


def write_parts_glb(parts: Sequence[Tuple[str, np.ndarray, np.ndarray]], path: Path, uvs: Optional[Sequence[np.ndarray]] = None,
                    image: Optional[bytes] = None) -> Path:
    """A GLB with one mesh node per part (positions in Blender space), for tests and offline trials of the parts route.
    With `uvs` and a PNG `image`, the parts share one textured material, as a part export's atlas does."""

    chunks = bytearray()
    views, accessors, meshes, nodes = [], [], [], []

    def add(data: bytes, target: Optional[int] = None) -> int:
        while len(chunks) % 4:
            chunks.append(0)
        view = {"buffer": 0, "byteOffset": len(chunks), "byteLength": len(data)}
        if target:
            view["target"] = target
        chunks.extend(data)
        views.append(view)
        return len(views) - 1

    material = image is not None and uvs is not None
    for k, (name, positions, triangles) in enumerate(parts):
        gltf = np.stack([positions[:, 0], positions[:, 2], -positions[:, 1]], axis=1).astype(np.float32)
        position = add(gltf.tobytes(), 34962)
        accessors.append({"bufferView": position, "componentType": 5126, "count": len(gltf), "type": "VEC3",
                          "min": gltf.min(axis=0).tolist(), "max": gltf.max(axis=0).tolist()})
        attributes = {"POSITION": len(accessors) - 1}
        if material:
            uv = add(np.asarray(uvs[k], dtype=np.float32).tobytes(), 34962)
            accessors.append({"bufferView": uv, "componentType": 5126, "count": len(gltf), "type": "VEC2"})
            attributes["TEXCOORD_0"] = len(accessors) - 1
        index = add(np.asarray(triangles, dtype=np.uint32).ravel().tobytes(), 34963)
        accessors.append({"bufferView": index, "componentType": 5125, "count": int(np.asarray(triangles).size), "type": "SCALAR"})
        primitive = {"attributes": attributes, "indices": len(accessors) - 1}
        if material:
            primitive["material"] = 0
        meshes.append({"name": name, "primitives": [primitive]})
        nodes.append({"name": name, "mesh": k})
    document = {"asset": {"version": "2.0", "generator": "hoi4 kit static_parts"}, "scene": 0, "scenes": [{"nodes": list(range(len(nodes)))}],
                "nodes": nodes, "meshes": meshes, "accessors": accessors, "bufferViews": views}
    if material:
        picture = add(image)
        document.update(images=[{"bufferView": picture, "mimeType": "image/png"}], textures=[{"source": 0}],
                        materials=[{"name": "atlas", "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}, "metallicFactor": 0.0}}])
    while len(chunks) % 4:
        chunks.append(0)
    document["buffers"] = [{"byteLength": len(chunks)}]
    text = json.dumps(document).encode("utf-8")
    text += b" " * (-len(text) % 4)
    body = struct.pack("<II", len(text), 0x4E4F534A) + text + struct.pack("<II", len(chunks), 0x004E4942) + bytes(chunks)
    Path(path).write_bytes(struct.pack("<III", 0x46546C67, 2, 12 + len(body)) + body)
    return Path(path)
