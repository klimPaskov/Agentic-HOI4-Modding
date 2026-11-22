"""Static models made in parts (Tripo's Generate in Parts): each part reduced on its own to a share of the budget.

A model exported in parts has one mesh node per part (the hull, the turret, each track band, a lion, a chimney).
Collapsing the joined model straight to a vanilla budget spends the triangles where the surface is large and crumples
what is small and detailed: an HD tank of 18,702 triangles reduced as one to a light tank's 3,948 lost its bogies and
its hull plates. The static route therefore keeps the parts apart and reduces each one on its own:

- `part_need` measures what a part needs: its surface area and its bend (the length of its edges times the angle
  between the two faces each one joins, so a bogie, a rivet row or a lion's mane counts more than a flat plate).
- `allocate` shares a triangle target between the parts by need (half by area, half by bend), never more than a part
  has and never less than `MIN_PART_TRIANGLES` (or all of a smaller part).
- `reduce_parts` reduces each part with the caller's reducer (Blender's Decimate in the stage) and checks every result
  with the unit route's shape check (`lib.tripo_shape`: no new shells, front, side and top silhouette agreement of at
  least `part_shape_iou`) and a closure check (no more open edges than the part had). Each part's least passing share
  is searched on its own from its share by need (`least_share`). When the least shares fit the target, the rest is
  shared by need on top of them. When they do not, it stops with `PartsBudgetError`, which names each part's least
  share: the model is never simplified to fit, the user decides.
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
SEARCH_PRECISION = 0.05  # a part's least passing share is found to this share of itself
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


_ORIGINALS: Dict[int, dict] = {}  # an original part's silhouettes, shells and open edges, kept while its search tries shares


def _shape_report(original: Mesh, reduced: Mesh) -> dict:
    """`tripo_shape.shape_report`, with the original part's own numbers worked out once (the search reduces one part many
    times, and rasterising the original again for each try doubled the time)."""

    key = id(original[1])
    cached = _ORIGINALS.get(key)
    if cached is None or cached["triangles"] is not original[1]:
        low, high = original[0].min(axis=0), original[0].max(axis=0)
        tolerance = float(np.max(high - low)) * 1e-5
        cached = _ORIGINALS[key] = {"triangles": original[1], "low": low, "high": high, "tolerance": tolerance,
                                    "masks": tripo_shape.silhouettes(*original, low, high), "shells": tripo_shape.shell_summary(*original, tolerance),
                                    "open_edges": open_edges(*original)}
    after = tripo_shape.silhouettes(*reduced, cached["low"], cached["high"])
    return {"shells_before": cached["shells"], "shells_after": tripo_shape.shell_summary(*reduced, cached["tolerance"]),
            "iou": {view: round(tripo_shape.iou(cached["masks"][view], after[view]), 4) for view in tripo_shape.VIEWS},
            "triangles_before": int(len(original[1])), "triangles_after": int(len(reduced[1])), "mask_size": tripo_shape.MASK_SIZE}


def part_problems(original: Mesh, reduced: Mesh, min_iou: float = tripo_shape.MIN_IOU) -> Tuple[dict, List[str]]:
    """The shape check of one reduced part (`lib.tripo_shape`) plus its closure: no more open edges than it had."""

    shape = _shape_report(original, reduced)
    problems = tripo_shape.shape_problems(shape, min_iou)
    before, after = _ORIGINALS[id(original[1])]["open_edges"], open_edges(*reduced)
    shape["open_edges_before"], shape["open_edges_after"] = before, after
    if after > before:
        problems.append(f"the reduction opened the part ({after} open edges, it had {before})")
    return shape, problems


def reduce_parts(names: Sequence[str], originals: Sequence[Mesh], target: int, reduce: Callable[[int, int], Mesh],
                 min_iou: float = tripo_shape.MIN_IOU, checker: Callable[[Mesh, Mesh, float], Tuple[dict, List[str]]] = part_problems) -> dict:
    """Reduce each part to the share of `target` that keeps its shape, the slack shared by need.

    Each part's check is its own, so each part's least passing share is searched on its own (`least_share`), starting
    from its share by need. When the least shares fit the target, the rest of the target is shared by need on top of
    them, each part is reduced to its final share and checked once more (a part that fails there takes its least
    share). `reduce(i, triangles)` returns part i reduced from its original to about that many triangles (all of it when
    `triangles` is its count), and the result it was last asked for is the chosen one. Returns the receipt; raises
    PartsBudgetError, naming each part's least share, when they need more than the target."""

    needs = [part_need(*mesh) for mesh in originals]
    counts = [n["triangles"] for n in needs]
    first = allocate(needs, target)
    tries: List[Dict[int, Tuple[dict, List[str], int]]] = [{} for _ in needs]

    def attempt(i: int, share: int) -> Tuple[dict, List[str], int]:
        share = min(counts[i], share)
        if share not in tries[i]:
            mesh = reduce(i, share)
            if share >= counts[i]:
                shape, problems = {"iou": {v: 1.0 for v in tripo_shape.VIEWS}, "open_edges_before": open_edges(*mesh), "open_edges_after": open_edges(*mesh)}, []
            else:
                shape, problems = checker(originals[i], mesh, min_iou)
            tries[i][share] = (shape, problems, int(len(mesh[1])))
        return tries[i][share]

    least = [least_share(lambda share, i=i: not attempt(i, share)[1], first[i], counts[i]) for i in range(len(needs))]
    if sum(least) > target:
        table = "; ".join(f"{names[i]} needs {least[i]} of its {counts[i]} (its share by need was {first[i]}: {tries[i][min(counts[i], first[i])][1][0] if tries[i][min(counts[i], first[i])][1] else 'passed'})"
                          for i in range(len(needs)) if least[i] > first[i])
        raise PartsBudgetError(f"the parts need {sum(least)} triangles to keep their shape at part_shape_iou {min_iou}, over the target of {target}: {table}. "
                               "Do not simplify the model: ask the user whether to accept a lower part_shape_iou or a larger budget for this kind (a tank's job field running_gear_triangles)")
    final = allocate(needs, target, lower=least)
    for i, share in enumerate(final):
        if attempt(i, share)[1]:
            final[i] = least[i]
    results = [attempt(i, share) for i, share in enumerate(final)]
    for i, share in enumerate(final):
        reduce(i, min(counts[i], share))  # the result the reducer keeps is the last one asked for: the final share
    weights = need_weights(needs)
    return {
        "target": target,
        "min_iou": min_iou,
        "triangles": sum(r[2] for r in results),
        "least": sum(least),
        "parts": {names[i]: {"from": counts[i], "to": results[i][2], "share": final[i], "least": least[i], "first_share": first[i],
                             "need": round(weights[i], 4), "area": round(needs[i]["area"], 4), "bend": round(needs[i]["bend"], 4),
                             "iou": results[i][0]["iou"], "open_edges": [results[i][0]["open_edges_before"], results[i][0]["open_edges_after"]],
                             "attempts": len(tries[i])}
                  for i in range(len(needs))},
    }


def least_share(passes: Callable[[int], bool], start: int, count: int, precision: float = SEARCH_PRECISION) -> int:
    """The least share (to `precision` of it, at least 8 triangles) at which `passes` holds, searched from `start`: down
    by halves while it passes, up by doubling while it fails (all of the part always passes), then by bisection."""

    start = max(min(start, count), min(count, MIN_PART_TRIANGLES))
    floor = min(count, MIN_PART_TRIANGLES)
    if passes(start):
        good, bad = start, None
        while good > floor:
            lower = max(floor, good // 2)
            if passes(lower):
                good = lower
            else:
                bad = lower
                break
        if bad is None:
            return good
    else:
        bad, good = start, None
        while good is None:
            upper = min(count, bad * 2)
            if upper >= count or passes(upper):
                good = upper
            else:
                bad = upper
    while good - bad > max(8, int(precision * good)):
        middle = (good + bad) // 2
        if passes(middle):
            good = middle
        else:
            bad = middle
    return good


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
