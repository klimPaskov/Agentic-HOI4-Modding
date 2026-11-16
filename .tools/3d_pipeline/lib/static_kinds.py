"""Rules for static and rigid-part models (building, landmark, ship, vehicle, plane) on the Tripo route.

Every number a rule uses is measured from vanilla files by `calibrate_static_kinds.py` and stored in
`config/static_kinds.json` with the files it came from. This module holds the parts that run without
Blender, so the tests can reach them and the Blender stage (`tripo/static_model_blender.py`) imports them:

- reading vanilla `pdxmesh`, `entity` and `animation` definitions from `.asset` and `.gfx` text;
- the geometry rules on plain arrays: which way the model faces, how big it is, where it is cut into rigid
  parts (a tank's hull, turret and barrel, a plane's propeller) and where a ship's waterline lies;
- retargeting a vanilla clip onto the model's own pivots (the role clips), and the motions vanilla lacks
  (a propeller's spin, a turret's turn before the shot);
- the `pdxmesh`, entity and animation text a mod needs.

Coordinates: geometry rules work in Blender space (x lateral, y along the model with the front toward -y,
z up). Vanilla files are in PDX space (x lateral, y up, z along the model with the front toward -z);
`io_pdx_mesh` swaps y and z (`SPACE_MATRIX`), and so does `to_blender`.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
CONFIG = PIPELINE_ROOT / "config" / "static_kinds.json"
KINDS = ("building", "landmark", "ship", "vehicle", "plane")
HOI4_FPS = 30
# io_pdx_mesh's SPACE_MATRIX: PDX (x, y up, z) <-> Blender (x, y, z up). It is its own inverse.
SWAP = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]])


# --------------------------------------------------------------------------------------------------
# Configuration


def load_kinds(path: Optional[Path] = None) -> dict:
    """The measured kind contracts (`config/static_kinds.json`)."""

    return json.loads((path or CONFIG).read_text(encoding="utf-8"))["kinds"]


def kind_contract(kind: str, path: Optional[Path] = None) -> dict:
    kinds = load_kinds(path)
    if kind not in kinds:
        raise KeyError(f"unknown model_kind {kind!r}; known: {', '.join(sorted(kinds))}")
    return kinds[kind]


def to_blender(vector: Sequence[float]) -> np.ndarray:
    return SWAP @ np.asarray(vector, dtype=float)


def matrix_to_blender(matrix: np.ndarray) -> np.ndarray:
    """A 4x4 PDX-space transform as the same transform in Blender space."""

    swap = np.eye(4)
    swap[:3, :3] = SWAP
    return swap @ matrix @ swap


# --------------------------------------------------------------------------------------------------
# Vanilla definitions: a small Clausewitz reader that keeps each block's text span


_TOKEN = re.compile(r'"[^"]*"|[{}=]|[^\s{}="]+')


def _blank_comments(text: str) -> str:
    """Replace `# ...` comments (outside quotes) with spaces, so token offsets still index the original text."""

    out, quoted, comment = [], False, False
    for char in text:
        if comment:
            if char == "\n":
                comment = False
                out.append(char)
            else:
                out.append(" ")
            continue
        if char == '"':
            quoted = not quoted
        elif char == "#" and not quoted:
            comment = True
            out.append(" ")
            continue
        out.append(char)
    return "".join(out)


def parse_script(text: str) -> list:
    """Parse Clausewitz text into nested `[key, value, (start, end)]` items; a block's value is a list.

    `start, end` index the original text, so a block's text can be copied. Bare values in a list (`{ 1 2 }`)
    are items with the key None.
    """

    clean = _blank_comments(text)
    tokens = [(m.group(0), m.start(), m.end()) for m in _TOKEN.finditer(clean)]
    position = 0

    def block(level: int) -> Tuple[list, int]:
        nonlocal position
        items: list = []
        while position < len(tokens):
            token, start, end = tokens[position]
            if token == "}":
                position += 1
                return items, end
            if token in ("{", "="):
                position += 1
                if token == "{":
                    value, close = block(level + 1)
                    items.append([None, value, (start, close)])
                continue
            position += 1
            if position < len(tokens) and tokens[position][0] == "=":
                position += 1
                if position < len(tokens) and tokens[position][0] == "{":
                    position += 1
                    value, close = block(level + 1)
                    items.append([token.strip('"'), value, (start, close)])
                elif position < len(tokens):
                    value_token, _value_start, value_end = tokens[position]
                    position += 1
                    items.append([token.strip('"'), value_token.strip('"'), (start, value_end)])
            else:
                items.append([None, token.strip('"'), (start, end)])
        return items, len(text)

    items, _end = block(0)
    return items


def scalar(items: list, key: str) -> Optional[str]:
    for name, value, _span in items:
        if name == key and isinstance(value, str):
            return value
    return None


def scan_definitions(game: Path, folders: Sequence[str] = ("gfx/entities", "gfx/models")) -> dict:
    """Every `pdxmesh`, `entity` and model `animation` block below `folders` of the game (first definition wins)."""

    found: dict = {"pdxmesh": {}, "entity": {}, "animation": {}}

    def walk(items: list, path: Path, text: str, is_asset: bool) -> None:
        for name, value, span in items:
            if not isinstance(value, list):
                continue
            if name in ("pdxmesh", "entity") or (name == "animation" and is_asset and scalar(value, "file")):
                key = scalar(value, "name")
                if key and key not in found[name]:
                    entry = {"source": path.relative_to(game).as_posix(), "text": text[span[0]: span[1]]}
                    for field in ("file", "pdxmesh", "scale"):
                        if scalar(value, field) is not None:
                            entry[field] = scalar(value, field)
                    if name == "pdxmesh":
                        entry["animations"] = {scalar(v, "id"): scalar(v, "type") for n, v, _s in value if n == "animation" and isinstance(v, list)}
                        entry["meshsettings"] = [
                            {f: scalar(v, f) for f in ("name", "index", "texture_diffuse", "texture_normal", "texture_specular", "shader")}
                            for n, v, _s in value if n == "meshsettings" and isinstance(v, list)
                        ]
                    found[name][key] = entry
            else:
                walk(value, path, text, is_asset)

    for folder in folders:
        base = game / folder
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.suffix.lower() not in (".asset", ".gfx") or not path.is_file():
                continue
            text = path.read_bytes().decode("utf-8-sig", errors="replace")
            walk(parse_script(text), path, text, path.suffix.lower() == ".asset")
    return found


def entity_scale(definitions: dict, mesh_rel: str) -> Optional[dict]:
    """The runtime scale of a mesh file: the entity's scale times its pdxmesh's, over the entities that show it.

    The most common value wins (a mesh shown by several entities usually has one scale). None when no entity shows it.
    """

    meshes = {name for name, entry in definitions["pdxmesh"].items() if entry.get("file", "").replace("\\", "/").lower() == mesh_rel.lower()}
    scales: Dict[float, List[str]] = {}
    for name, entity in definitions["entity"].items():
        if entity.get("pdxmesh") in meshes:
            mesh_scale = float(definitions["pdxmesh"][entity["pdxmesh"]].get("scale", 1.0))
            value = round(float(entity.get("scale", 1.0)) * mesh_scale, 4)
            scales.setdefault(value, []).append(name)
    if not scales:
        return None
    value = max(scales, key=lambda v: (len(scales[v]), -v))
    return {"scale": value, "entities": sorted(scales[value])[:4], "pdxmeshes": sorted(meshes)}


# --------------------------------------------------------------------------------------------------
# Geometry rules (Blender space: x lateral, y along the model, front toward -y, z up)


def surface_samples(positions: np.ndarray, triangles: np.ndarray, count: int = 60000, seed: int = 7) -> np.ndarray:
    """Points spread over the surface by area, so slice widths do not depend on how densely a part is meshed."""

    if len(triangles) == 0:
        return positions.copy()
    a, b, c = (positions[triangles[:, k]] for k in range(3))
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    total = float(area.sum())
    if total <= 0:
        return positions.copy()
    rng = np.random.default_rng(seed)
    chosen = rng.choice(len(triangles), size=count, p=area / total)
    u, v = rng.random(count), rng.random(count)
    flip = u + v > 1
    u[flip], v[flip] = 1 - u[flip], 1 - v[flip]
    return a[chosen] + (b[chosen] - a[chosen]) * u[:, None] + (c[chosen] - a[chosen]) * v[:, None]


def _extent(points: np.ndarray, axis: int) -> float:
    return float(np.ptp(points[:, axis])) if len(points) else 0.0


def _slice_widths(points: np.ndarray, along: int, across: int, edges: np.ndarray, trim: float = 1.0) -> np.ndarray:
    """Width across `across` of the points in each bin along `along` (trimmed percentiles, so a stray sample does not count)."""

    widths = np.zeros(len(edges) - 1)
    for k in range(len(edges) - 1):
        inside = points[(points[:, along] >= edges[k]) & (points[:, along] < edges[k + 1])]
        if len(inside) >= 8:
            low, high = np.percentile(inside[:, across], [trim, 100 - trim])
            widths[k] = high - low
    return widths


def facing_quarter_turns(points: np.ndarray, kind: str, rule: Optional[dict] = None) -> int:
    """How many quarter turns about z (counter-clockwise seen from above) put the model's front toward -y.

    - vehicle: the long horizontal axis is the hull; the front is the end the turret (`turret_cut` with `rule`, the
      contract's turret rule) reaches further past its own middle: the barrel.
    - ship: the long horizontal axis is the hull; the bow is the end whose last 15 % is narrower (stern wider).
    - plane: the long horizontal axis is the wingspan, so the fuselage runs across it; the nose is the end
      nearer the wing (the slab of greatest span), as on every single-engine fighter.
    - building, landmark: no front; 0.
    """

    if kind in ("building", "landmark"):
        return 0
    span = np.ptp(points[:, :2], axis=0)
    long_axis = int(np.argmax(span))
    along = long_axis if kind in ("vehicle", "ship") else 1 - long_axis
    across = 1 - along
    centre = (points[:, along].min() + points[:, along].max()) / 2
    if kind == "vehicle":
        # the barrel: the turret (found from the height slices alone) reaches further past its own middle toward the front
        cut = turret_cut(points, rule)["cut_z"] if rule else points[:, 2].min() + 0.6 * np.ptp(points[:, 2])
        top = points[points[:, 2] >= cut]
        middle = float(np.median(top[:, along]))
        front_is_low = (middle - top[:, along].min()) > (top[:, along].max() - middle)
    elif kind == "ship":
        length = np.ptp(points[:, along])
        low_end = points[points[:, along] < points[:, along].min() + 0.15 * length]
        high_end = points[points[:, along] > points[:, along].max() - 0.15 * length]
        front_is_low = _extent(low_end, across) * _extent(low_end, 2) < _extent(high_end, across) * _extent(high_end, 2)
    else:
        edges = np.linspace(points[:, along].min(), points[:, along].max(), 41)
        widths = _slice_widths(points, along, across, edges)
        wing = (edges[int(np.argmax(widths))] + edges[int(np.argmax(widths)) + 1]) / 2
        front_is_low = wing < centre
    # the front's current direction: (axis, sign); the turn takes it to (1, -1)
    direction = {(0, -1): 1, (0, 1): 3, (1, -1): 0, (1, 1): 2}  # a quarter turn takes -x to -y, +y to -x, +x to +y
    sign = -1 if front_is_low else 1
    return direction[(along, sign)]


def rotate_quarter_turns(points: np.ndarray, turns: int) -> np.ndarray:
    turns %= 4
    out = points.copy()
    for _ in range(turns):
        out[:, 0], out[:, 1] = -out[:, 1].copy(), out[:, 0].copy()
    return out


FRONT_TURNS = {"-y": 0, "-x": 1, "+y": 2, "+x": 3}


def main_measure(points: np.ndarray, kind: str) -> float:
    """The size a kind is scaled by: a tank's or ship's length, a plane's wingspan, a building's footprint, a landmark's largest side."""

    span = np.ptp(points, axis=0)
    if kind in ("vehicle", "ship"):
        return float(span[1])
    if kind == "plane":
        return float(span[0])
    if kind == "building":
        return float(max(span[0], span[1]))
    return float(span.max())


def waterline_height(points: np.ndarray, width_share: float) -> float:
    """The height where a hull's beam first reaches `width_share` of its widest, above the keel.

    A hull's sides run nearly upright from the waterline up, and curve in below it toward the keel.
    """

    hull_top = points[:, 2].min() + 0.6 * np.ptp(points[:, 2])
    low = points[points[:, 2] <= hull_top]
    edges = np.linspace(low[:, 2].min(), hull_top, 61)
    widths = _slice_widths(low, 2, 0, edges)
    widest = widths.max()
    for k, width in enumerate(widths):
        if width >= width_share * widest:
            return float(edges[k])
    return float(edges[0])


def placement(points: np.ndarray, kind: str, contract: dict) -> Tuple[float, np.ndarray]:
    """Scale and translation that give the model its kind's vanilla size and position.

    The main measure becomes the contract's `size.source`. Across, the model is centred where vanilla's are
    (`size.centre_share`, a share of the main measure). Up, the lowest point goes to vanilla's ground (`size.ground_share`),
    except a ship, whose waterline (`waterline.width_share`) goes to z = 0, and a building or landmark on a plinth, which
    sinks at most half the plinth (`plinth_height`), so the ground does not show through it.
    """

    size = contract["size"]
    scale = size["source"] / max(main_measure(points, kind), 1e-9)
    scaled = points * scale
    low, high = scaled.min(axis=0), scaled.max(axis=0)
    centre_share = np.asarray(size["centre_share"], dtype=float)
    target_centre = centre_share * size["source"]
    offset = np.zeros(3)
    offset[:2] = target_centre[:2] - (low[:2] + high[:2]) / 2
    if kind == "ship":
        offset[2] = -waterline_height(scaled, contract["waterline"]["width_share"])
    else:
        ground = size["ground_share"] * size["source"]
        if kind in ("building", "landmark") and ground < 0:
            # vanilla sinks its foundations; a generated model often stands on a thin plinth, which sinks at most halfway
            ground = max(ground, -0.5 * plinth_height(scaled))
        offset[2] = ground - low[2]
    return float(scale), offset


def plinth_height(points: np.ndarray, share: float = 0.9) -> float:
    """How tall the base a model stands on is: from its lowest point up to where its footprint first narrows below
    `share` of the bottom's (a plinth wider than the building on it); the whole height when it never narrows."""

    z0, height = points[:, 2].min(), float(np.ptp(points[:, 2]))
    edges = np.linspace(z0, z0 + height, 81)
    widths = _slice_widths(points, 2, 0, edges) * _slice_widths(points, 2, 1, edges)
    filled = np.nonzero(widths > 0)[0]
    if not len(filled):
        return height
    bottom = widths[filled[0]]
    for k in filled[1:]:
        if widths[k] < share * bottom:
            return float(edges[k] - z0)
    return height


def slice_areas(points: np.ndarray, edges: np.ndarray, cell: float) -> np.ndarray:
    """Plan-view area of the points in each height bin: occupied cells of a `cell`-sized grid, times the cell's area."""

    areas = np.zeros(len(edges) - 1)
    for k in range(len(edges) - 1):
        inside = points[(points[:, 2] >= edges[k]) & (points[:, 2] < edges[k + 1])]
        if len(inside):
            cells = np.unique(np.floor(inside[:, :2] / cell).astype(np.int64), axis=0)
            areas[k] = len(cells) * cell * cell
    return areas


SLICES = 80


def turret_cut(points: np.ndarray, rule: dict) -> dict:
    """Where a tank's turret sits on its hull, from the plan-view area of its height slices.

    The hull's area is the median slice area between half of `rule.search_from` and `rule.search_from` of the height.
    A slice can start the turret when the run above it is turret-sized: its median slice and nine in ten of its slices
    cover less than `rule.area_threshold` of the hull (the first slice too), and it is at least `rule.min_height_share` of the height tall (half
    the shortest vanilla turret, so a hatch is not a turret). Of those, the turret starts where the step from the three
    slices below to the run's median is largest: the hull roof (a flat deck, so a wide slice) sits right under the turret, and
    a superstructure under the turret is a smaller step than the turret's own.
    """

    z0, height = points[:, 2].min(), np.ptp(points[:, 2])
    length = float(np.ptp(points[:, :2], axis=0).max())  # either way round: the cut is found before the front is
    edges = np.linspace(z0, z0 + height, SLICES + 1)
    shortest = int(np.ceil(rule.get("min_height_share", 0.0) * SLICES))
    areas = slice_areas(points, edges, rule.get("cell_share", 0.02) * length)
    start = max(int(rule["search_from"] * SLICES), 2)
    band = areas[max(start // 2, 1): start]
    hull = float(np.median(band[band > 0])) if (band > 0).any() else float(areas.max())
    best, cut = 0.0, None
    for k in range(start, SLICES - max(shortest, 3)):
        above = areas[k:][areas[k:] > 0]
        if len(above) < max(shortest, 3) or areas[k] <= 0:
            continue
        typical = float(np.median(above))
        # the run above must be the turret's size: its typical slice and nine in ten of its slices under the threshold
        if typical >= rule["area_threshold"] * hull or (above >= rule["area_threshold"] * hull).mean() > 0.1 or areas[k] >= rule["area_threshold"] * hull:
            continue
        step = float(areas[max(k - 3, 0): k].max()) / typical
        if step > best:  # on a tie the lower slice: the turret's bottom, not a slice inside it
            best, cut = step, k
    if cut is None:
        raise ValueError("no turret found: no slice above the hull covers less than the hull to the top")
    cut_z = float(edges[cut])
    return {"cut_z": cut_z, "hull_area": hull, "turret_area": float(np.median(areas[cut:][areas[cut:] > 0])), "step": round(best, 3)}


def barrel_cut(points: np.ndarray, cut_z: float, rule: dict) -> dict:
    """Where the barrel leaves the turret: walking back from the turret's front (-y), the first slice that is no longer
    thin (narrower and lower than `rule.width_threshold` of the turret body, and within twice the muzzle's size)."""

    turret = points[points[:, 2] >= cut_z]
    edges = np.linspace(turret[:, 1].min(), turret[:, 1].max(), 121)
    widths = _slice_widths(turret, 1, 0, edges)
    heights = _slice_widths(turret, 1, 2, edges)
    body = float(np.percentile(widths[widths > 0], 75))
    body_height = float(np.percentile(heights[heights > 0], 75))
    filled = np.nonzero(widths > 0)[0]
    if len(filled) < 3:
        raise ValueError("no barrel found: nothing reaches forward from the turret")
    muzzle_width = float(np.median(widths[filled[:3]]))
    muzzle_height = float(np.median(heights[filled[:3]]))
    # A barrel is thin against the turret (vanilla's barrels are `rule.width_share` of its width) and keeps about its
    # muzzle's size back to the mantlet (kit rule: within twice it, for a taper or a muzzle brake).
    thin = (widths > 0) & (widths < min(rule["width_threshold"] * body, 2 * muzzle_width)) & (heights < min(rule["width_threshold"] * body_height, 2 * muzzle_height))
    if not thin[filled[0]]:
        raise ValueError("no barrel found: the turret's front is not thin")
    cut = next((k for k in range(filled[0], len(thin)) if not thin[k] and widths[k] > 0), None)
    if cut is None or cut <= filled[0] + 1:
        raise ValueError("no barrel found: the thin run in front of the turret is too short")
    # a round turret's front is narrow too, but only for a sliver: a barrel is at least `rule.min_length_share` of
    # the turret's length (half vanilla's shortest)
    if edges[cut] - edges[filled[0]] < rule.get("min_length_share", 0.0) * (edges[-1] - edges[cut]):
        raise ValueError("no barrel found: the thin run in front of the turret is shorter than any vanilla barrel")
    cut_y = float(edges[cut])
    barrel = turret[turret[:, 1] < cut_y]
    if len(barrel) < 20:
        raise ValueError("no barrel found: the thin run in front of the turret is empty")
    near = barrel[barrel[:, 1] > cut_y - 0.1 * (cut_y - barrel[:, 1].min())]
    pivot = [float(np.median(near[:, 0])), cut_y, float(np.median(near[:, 2]))]
    muzzle = [pivot[0], float(barrel[:, 1].min()), pivot[2]]
    return {"cut_y": cut_y, "pivot": pivot, "muzzle": muzzle, "length": float(cut_y - barrel[:, 1].min()), "turret_body_width": body}


def propeller_cut(points: np.ndarray, rule: dict) -> dict:
    """Where a single-engine plane's propeller ends: in the front `rule.search_share` of the fuselage, the slice of
    greatest span is the blade disc, and the propeller ends at the first slice behind it narrower than
    `rule.width_threshold` of that span. The hub is the middle of the disc."""

    y0, length = points[:, 1].min(), np.ptp(points[:, 1])
    fuselage = points[np.abs(points[:, 0] - np.median(points[:, 0])) < 0.5 * np.ptp(points[:, 0])]
    edges = np.linspace(y0, y0 + rule["search_share"] * length, 61)
    widths = _slice_widths(fuselage, 1, 0, edges, trim=0.2)
    heights = _slice_widths(fuselage, 1, 2, edges, trim=0.2)
    disc = np.maximum(widths, heights)
    peak = int(np.argmax(disc))
    end = None
    for k in range(peak, len(disc)):
        if disc[k] < rule["width_threshold"] * disc[peak]:
            end = k
            break
    if end is None or disc[peak] <= 0:
        raise ValueError("no propeller found: no blade disc ahead of the cowling")
    cut_y = float(edges[end])
    blades = points[points[:, 1] < cut_y]
    hub = [float((blades[:, 0].min() + blades[:, 0].max()) / 2), float(blades[:, 1].min()), float((blades[:, 2].min() + blades[:, 2].max()) / 2)]
    return {"cut_y": cut_y, "hub": hub, "disc_span": float(disc[peak])}


def box_point(low: Sequence[float], high: Sequence[float], share: Sequence[float]) -> List[float]:
    low, high = np.asarray(low, dtype=float), np.asarray(high, dtype=float)
    return [float(v) for v in low + (high - low) * np.asarray(share, dtype=float)]


# --------------------------------------------------------------------------------------------------
# Clips: vanilla's motion, retargeted onto the model's pivots


def _quaternion_from_matrix(m: np.ndarray) -> np.ndarray:
    """(w, x, y, z) of a 3x3 rotation (orthonormalised first)."""

    u, _s, vt = np.linalg.svd(m)
    r = u @ vt
    if np.linalg.det(r) < 0:
        u[:, -1] *= -1
        r = u @ vt
    w = math.sqrt(max(0.0, 1 + r[0, 0] + r[1, 1] + r[2, 2])) / 2
    x = math.sqrt(max(0.0, 1 + r[0, 0] - r[1, 1] - r[2, 2])) / 2
    y = math.sqrt(max(0.0, 1 - r[0, 0] + r[1, 1] - r[2, 2])) / 2
    z = math.sqrt(max(0.0, 1 - r[0, 0] - r[1, 1] + r[2, 2])) / 2
    x = math.copysign(x, r[2, 1] - r[1, 2])
    y = math.copysign(y, r[0, 2] - r[2, 0])
    z = math.copysign(z, r[1, 0] - r[0, 1])
    q = np.array([w, x, y, z])
    return q / np.linalg.norm(q)


def quaternion_matrix(q: Sequence[float]) -> np.ndarray:
    w, x, y, z = np.asarray(q, dtype=float) / np.linalg.norm(q)
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def _slerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    if np.dot(a, b) < 0:
        b = -b
    dot = float(np.clip(np.dot(a, b), -1, 1))
    if dot > 0.9995:
        q = a + t * (b - a)
        return q / np.linalg.norm(q)
    angle = math.acos(dot)
    return (math.sin((1 - t) * angle) * a + math.sin(t * angle) * b) / math.sin(angle)


def bone_rest_heads(mesh) -> Dict[str, np.ndarray]:
    """Each bone's rest position (PDX space) from a `pdx_deform.SkinnedMesh`."""

    heads = {}
    for name, inverse in zip(mesh.bones, mesh.inverse_bind):
        world = np.linalg.inv(inverse) if abs(np.linalg.det(inverse)) > 1e-9 else np.eye(4)
        heads[name] = world[:3, 3]
    return heads


def local_motion(mesh, anim) -> Dict[str, dict]:
    """Each animated bone's motion relative to its parent's, per frame: a rotation (w, x, y, z) about the bone's
    rest position and that position's displacement, both in Blender space.

    From the skinning matrices M (bind pose to frame) of `lib.pdx_deform`: a bone's local motion is
    L = inverse(M_parent) M_bone, the pivot is the bone's rest head c, the displacement is L c - c.
    """

    from lib import pdx_deform

    inverse = np.array([ib if abs(np.linalg.det(ib)) > 1e-9 else np.eye(4) for ib in mesh.inverse_bind])
    mesh = type(mesh)(**{**mesh.__dict__, "inverse_bind": inverse})
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    heads = bone_rest_heads(mesh)
    out = {}
    for index, name in enumerate(mesh.bones):
        if name not in anim.channels:
            continue
        parent = mesh.parents[index]
        frames = []
        for f in range(matrices.shape[0]):
            local = matrices[f, index] if parent < 0 else np.linalg.inv(matrices[f, parent]) @ matrices[f, index]
            local = matrix_to_blender(local)
            c = to_blender(heads[name])
            moved = local[:3, :3] @ c + local[:3, 3]
            frames.append((_quaternion_from_matrix(local[:3, :3]), moved - c))
        out[name] = {"q": np.array([q for q, _d in frames]), "d": np.array([d for _q, d in frames])}
    return out


def resample(motion: Dict[str, dict], source_fps: float, target_fps: int = HOI4_FPS, count: Optional[int] = None) -> Tuple[Dict[str, dict], int]:
    """The same motion at `target_fps`, keeping its length in seconds (rotations slerped, displacements linear).

    With `count`, the clip is stretched to exactly that many frames instead (a spin that must close a whole turn)."""

    frames = len(next(iter(motion.values()))["q"]) if motion else 1
    seconds = (frames - 1) / source_fps if frames > 1 else 0.0
    if count is None:
        count = max(int(round(seconds * target_fps)) + 1, 2)
    step = (frames - 1) / max(count - 1, 1)
    out = {}
    for name, channel in motion.items():
        qs, ds = [], []
        for k in range(count):
            t = k * step
            i = min(int(math.floor(t)), frames - 1)
            j = min(i + 1, frames - 1)
            u = t - i
            qs.append(_slerp(channel["q"][i], channel["q"][j], u))
            ds.append(channel["d"][i] * (1 - u) + channel["d"][j] * u)
        out[name] = {"q": np.array(qs), "d": np.array(ds)}
    return out, count


def rotation_angle(q: Sequence[float]) -> float:
    return math.degrees(2 * math.acos(min(1.0, abs(float(q[0]) / float(np.linalg.norm(q))))))


def smoothstep(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def turn_before_shot(frames: int, recoil: np.ndarray, degrees: float, ease_frames: int) -> np.ndarray:
    """The turret's extra turn (degrees about z) per frame for an attack: eased in to `degrees` over `ease_frames`, held
    while the gun recoils, eased back after the last recoil frame. `recoil` is the barrel's displacement per frame."""

    peak = float(np.max(recoil)) if len(recoil) else 0.0
    moving = np.nonzero(recoil > 0.05 * peak)[0] if peak > 0 else np.array([], dtype=int)
    first, last = (int(moving[0]), int(moving[-1])) if len(moving) else (frames // 3, frames // 3)
    # The turn always takes `ease_frames` (never a snap): it ends at the first recoil frame when the clip leaves room
    # before it, else it starts at frame 0 and the gun fires while the turret is still coming round. Vanilla's light tank
    # fires on its second frame, and a turn squeezed into those frames snapped the turret 21.7 degrees in two.
    ease_frames = max(1, ease_frames)
    start = max(0, first - ease_frames)
    end = start + ease_frames
    hold_until = max(last, end)
    ease_out = max(1, min(ease_frames, frames - 1 - hold_until))
    out = np.zeros(frames)
    for f in range(frames):
        if f <= end:
            out[f] = degrees * smoothstep((f - start) / ease_frames)
        elif f <= hold_until:
            out[f] = degrees
        else:
            out[f] = degrees * (1 - smoothstep((f - hold_until) / ease_out))
    return out


def spin_frames(seconds: float, degrees_per_frame: float, fps: int = HOI4_FPS) -> int:
    """A looping spin's frame count: about `seconds` long and a whole number of turns, so the loop does not jump."""

    per_turn = 360.0 / degrees_per_frame
    turns = max(1, round(seconds * fps / per_turn))
    return int(round(turns * per_turn)) + 1


def axis_quaternion(axis: Sequence[float], degrees: float) -> np.ndarray:
    axis = np.asarray(axis, dtype=float) / np.linalg.norm(axis)
    half = math.radians(degrees) / 2
    return np.concatenate([[math.cos(half)], math.sin(half) * axis])


# --------------------------------------------------------------------------------------------------
# Mod text


def pdxmesh_text(name: str, mesh_file: str, animations: Dict[str, str], settings: List[dict], scale: Optional[float] = None) -> str:
    lines = ["\tpdxmesh = {", f'\t\tname = "{name}_mesh"', f'\t\tfile = "{mesh_file}"']
    for role, animation in animations.items():
        lines.append(f'\t\tanimation = {{ id = "{role}" type = "{animation}" }}')
    if scale is not None:
        lines.append(f"\t\tscale = {scale:g}")
    for setting in settings:
        lines += ["", "\t\tmeshsettings = {", f'\t\t\tname = "{setting["name"]}"', f"\t\t\tindex = {setting.get('index', 0)}"]
        for key in ("texture_diffuse", "texture_normal", "texture_specular"):
            lines.append(f'\t\t\t{key} = "{setting[key]}"')
        lines += [f'\t\t\tshader = "{setting["shader"]}"', "\t\t}"]
    lines.append("\t}")
    return "\n".join(lines)


_NODE = re.compile(r'node\s*=\s*"?([A-Za-z0-9_]+)"?')
_ANIMATION = re.compile(r'animation\s*=\s*"?([A-Za-z0-9_]+)"?')


def entity_text(reference_text: str, name: str, pdxmesh: str, nodes: Sequence[str], animations: Sequence[str], scale: Optional[float],
                aliases: Optional[Dict[str, str]] = None) -> str:
    """Vanilla's entity for the kind, renamed onto the model: its states and events stay; an event at a node the
    model lacks is dropped, a state playing a role the kind folds into another (`aliases`, the contract's
    `role_aliases`) plays that one, a state playing an animation the model lacks plays `idle` (or is dropped when there
    is none), and the scale is the one the model was sized for."""

    nodes, animations = set(nodes), list(animations)
    # The entity's own name is the block's first `name =` (vanilla writes it first; states come after).
    reference_text = re.sub(r'name\s*=\s*"?[A-Za-z0-9_]+"?', f'name = "{name}_entity"', reference_text, count=1)
    out = []
    for line in reference_text.splitlines():
        stripped = line.strip()
        if re.match(r"pdxmesh\s*=", stripped):
            line = re.sub(r'pdxmesh\s*=\s*"?[A-Za-z0-9_]+"?', f'pdxmesh = "{pdxmesh}"', line, count=1)
        elif re.match(r"scale\s*=", stripped):
            continue
        node = _NODE.search(line)
        if node and node.group(1) not in nodes and line.count("{") == line.count("}"):
            continue
        played = _ANIMATION.search(line)
        if played and "state" in line and played.group(1) in (aliases or {}):
            line = line.replace(played.group(0), f'animation = "{aliases[played.group(1)]}"', 1)
            played = _ANIMATION.search(line)
        if played and "state" in line and played.group(1) not in animations:
            if not animations:
                continue
            line = line.replace(played.group(0), f'animation = "{"idle" if "idle" in animations else animations[0]}"', 1)
        if re.match(r"default_state\s*=", stripped) and not animations:
            continue
        out.append(line)
    # the closing brace of the block: put the scale before it
    while out and not out[-1].strip():
        out.pop()
    if scale is not None and out and out[-1].strip() == "}":
        out.insert(len(out) - 1, f"\tscale = {scale:g}")
    return "\n".join(out)


def animation_text(animation: str, file_name: str) -> str:
    return f'animation = {{\n\tname = "{animation}"\n\tfile = "{file_name}"\n}}'


# --------------------------------------------------------------------------------------------------
# Checks on the exported files (STATIC-* rules)


def kind_findings(mesh_path: Path, contract: dict, anims: Sequence[Path] = ()) -> List[Tuple[str, str, str]]:
    """The kind's contract checked on an exported mesh: (rule, severity, message) for each problem.

    - STATIC-SIZE: the main measure is within 2 % of vanilla's (the size the entity scale was chosen for).
    - STATIC-TRIANGLES: no more triangles than the most detailed vanilla model of the kind.
    - STATIC-BONES, STATIC-LOCATORS: the bones and locators vanilla's entity and clips use are there.
    - STATIC-COLLISION: a kind whose vanilla models carry a `Collision` box has one 8-vertex box.
    - STATIC-RIGID: every rendered vertex of a rigid-part kind follows one bone wholly (weight 1.0), so no part bends.
    - STATIC-SHADER: the rendered shapes use the kind's vanilla shader.
    - STATIC-GROUND: a land model's lowest point sits on the ground, a ship's waterline at zero (keel below it at most
      vanilla's draft).
    - STATIC-PART-GAP: in every frame of every clip (deaths excepted), each rigid part stays on the part it is mounted on
      (no gap wider than `rigid.max_gap_share` of the main measure opens between them).
    """

    from lib import pdx_binary, pdx_deform

    findings: List[Tuple[str, str, str]] = []
    summary = pdx_binary.summarize_mesh(pdx_binary.read(mesh_path))
    mesh = pdx_deform.load_mesh(mesh_path)
    visible = ~mesh.collision if len(mesh.collision) else np.ones(len(mesh.positions), dtype=bool)
    points = np.array([to_blender(p) for p in mesh.positions[visible]])
    kind = contract["kind"]
    measure = main_measure(points, kind)
    target = contract["size"]["source"]
    if abs(measure - target) > 0.02 * target:
        findings.append(("STATIC-SIZE", "error", f"the {contract['size']['measure']} is {measure:.3f}; vanilla {kind}s measure {target:.3f} at entity scale {contract['entity']['scale']:g} (median of {len(contract['references'])} models)"))
    triangles = sum(s.triangles for s in summary.streams if s.material_shader.lower() != "collision")
    budget = contract["triangle_budget"]["value"]
    if triangles > budget:
        findings.append(("STATIC-TRIANGLES", "error", f"{triangles} triangles; the most detailed vanilla {kind} ({contract['triangle_budget']['mesh']}) has {budget}"))
    wanted_bones = [bone["name"] for bone in contract.get("skeleton", {}).get("bones", [])] + contract.get("extra_bones", [])
    missing = [bone for bone in wanted_bones if bone not in summary.bones]
    if missing:
        findings.append(("STATIC-BONES", "error", f"missing bones {', '.join(missing)}; vanilla's clips and entity use them"))
    missing = [loc["name"] for loc in contract.get("locators", []) if loc["name"] not in summary.locators]
    if missing:
        findings.append(("STATIC-LOCATORS", "error", f"missing locators {', '.join(missing)}; vanilla's entity places its effects there"))
    if contract.get("collision"):
        boxes = [s for s in summary.streams if s.material_shader.lower() == "collision"]
        if len(boxes) != 1 or boxes[0].vertices != 8:
            findings.append(("STATIC-COLLISION", "error", f"{len(boxes)} Collision shape(s) ({', '.join(str(b.vertices) for b in boxes)} vertices); vanilla {kind}s carry one 8-vertex box, the selection shape"))
    elif any(s.material_shader.lower() == "collision" for s in summary.streams):
        findings.append(("STATIC-COLLISION", "warning", f"a Collision shape on a {kind}; vanilla {kind}s have none"))
    shaders = {s.material_shader for s in summary.streams if s.material_shader.lower() != "collision"}
    if shaders != {contract["shader"]}:
        findings.append(("STATIC-SHADER", "error", f"rendered with {', '.join(sorted(shaders))}; vanilla {kind}s use {contract['shader']}"))
    if contract.get("rigid") and mesh.skinned:
        partial = int((mesh.weights[visible].max(axis=1) < 0.999).sum())
        if partial:
            findings.append(("STATIC-RIGID", "error", f"{partial} vertices are shared between bones; every part of a {kind} is rigid (weight 1.0 on one bone), or it bends"))
    low = float(points[:, 2].min())
    if kind == "ship":
        # the route cuts a hull at vanilla's draft when its keel goes deeper than the draft and 1 % of the length
        draft = contract["waterline"]["draft_share"] * target + 0.01 * target
        if low < -draft - 1e-4:
            findings.append(("STATIC-GROUND", "error", f"the keel is {-low:.3f} below the waterline; vanilla ships draw at most {draft:.3f}"))
    else:
        expected = contract["size"]["ground_share"] * target
        # a building or landmark on a thin plinth sinks less than vanilla's foundations (placement), never above ground
        sunk_less = kind in ("building", "landmark") and expected - 0.01 * target <= low <= 0.01 * target
        # a plane flies: it may sit higher than vanilla's (lifted so its propeller's disc clears the ground), never lower
        sunk_less = sunk_less or (kind == "plane" and low >= expected - 0.01 * target)
        if abs(low - expected) > 0.01 * target and not sunk_less:
            findings.append(("STATIC-GROUND", "error", f"the lowest point is at {low:.3f}; vanilla {kind}s sit at {expected:.3f}"))
    if contract.get("rigid") and mesh.skinned and anims:
        findings += _part_gaps(mesh, visible, anims, contract, measure)
    return findings


def _part_gaps(mesh, visible, anims: Sequence[Path], contract: dict, measure: float) -> List[Tuple[str, str, str]]:
    from lib import pdx_deform

    mounts = contract.get("mounts", {})
    if not mounts:
        return []
    dominant = mesh.joints[np.arange(len(mesh.joints)), np.argmax(mesh.weights, axis=1)]
    index = {name: i for i, name in enumerate(mesh.bones)}
    limit = contract["rigid"]["max_gap_share"] * measure
    findings = []
    inverse = np.array([ib if abs(np.linalg.det(ib)) > 1e-9 else np.eye(4) for ib in mesh.inverse_bind])
    skinnable = type(mesh)(**{**mesh.__dict__, "inverse_bind": inverse})
    for anim_path in anims:
        if anim_path.stem.endswith("_death"):
            continue
        anim = pdx_deform.load_anim(anim_path)
        matrices = pdx_deform.skinning_matrices(skinnable, anim)
        worst = (0.0, "", 0)
        for part, base in mounts.items():
            if part not in index or base not in index:
                continue
            a = visible & (dominant == index[part])
            b = visible & (dominant == index[base])
            if a.sum() < 3 or b.sum() < 3:
                continue
            rest_gap = _nearest_gap(mesh.positions[a], mesh.positions[b])
            low, high = mesh.positions[b].min(axis=0), mesh.positions[b].max(axis=0)
            for f in range(0, matrices.shape[0], max(1, matrices.shape[0] // 24)):
                pa = _apply(matrices[f, index[part]], mesh.positions[a])
                # a part that slides into its mount (a barrel recoiling into the turret) does not lift off it: any of
                # its points inside the mount's box, in the mount's own frame, means it is still seated
                local = _apply(np.linalg.inv(matrices[f, index[base]]), pa)
                if ((local >= low) & (local <= high)).all(axis=1).any():
                    continue
                pb = _apply(matrices[f, index[base]], mesh.positions[b])
                gap = _nearest_gap(pa, pb) - rest_gap
                if gap > worst[0]:
                    worst = (gap, part, f)
        if worst[0] > limit:
            findings.append(("STATIC-PART-GAP", "error", f"{anim_path.name} frame {worst[2]}: the {worst[1]} lifts {worst[0]:.3f} off the part it is mounted on (limit {limit:.3f}, {contract['rigid']['max_gap_share']:.0%} of the {contract['size']['measure']})"))
    return findings


def _apply(matrix: np.ndarray, points: np.ndarray) -> np.ndarray:
    return points @ matrix[:3, :3].T + matrix[:3, 3]


def _nearest_gap(a: np.ndarray, b: np.ndarray) -> float:
    """The smallest distance from the part `a` to `b` (sampled, so it stays fast on dense parts)."""

    a = a[:: max(1, len(a) // 400)]
    b = b[:: max(1, len(b) // 2000)]
    best = np.inf
    for chunk in np.array_split(a, max(1, len(a) // 100)):
        d = np.linalg.norm(chunk[:, None, :] - b[None, :, :], axis=2).min()
        best = min(best, float(d))
    return best


# --------------------------------------------------------------------------------------------------
# GLB geometry without Blender (for the plan and the tests)

_COMPONENTS = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
_WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def _accessor(document: dict, binary: bytes, index: int) -> np.ndarray:
    accessor = document["accessors"][index]
    view = document["bufferViews"][accessor["bufferView"]]
    dtype = np.dtype(_COMPONENTS[accessor["componentType"]])
    width = _WIDTH[accessor["type"]]
    start = int(view.get("byteOffset", 0)) + int(accessor.get("byteOffset", 0))
    stride = int(view.get("byteStride", 0)) or dtype.itemsize * width
    count = int(accessor["count"])
    raw = np.frombuffer(binary, dtype=np.uint8, count=stride * (count - 1) + dtype.itemsize * width, offset=start)
    rows = np.lib.stride_tricks.as_strided(raw, shape=(count, dtype.itemsize * width), strides=(stride, 1))
    return np.ascontiguousarray(rows).view(dtype).reshape(count, width)


def _node_matrix(node: dict) -> np.ndarray:
    if "matrix" in node:
        return np.asarray(node["matrix"], dtype=float).reshape(4, 4).T
    matrix = np.eye(4)
    if "scale" in node:
        matrix = np.diag(list(node["scale"]) + [1.0]) @ matrix
    if "rotation" in node:
        x, y, z, w = node["rotation"]
        rotation = np.eye(4)
        rotation[:3, :3] = quaternion_matrix([w, x, y, z])
        matrix = rotation @ matrix
    if "translation" in node:
        translation = np.eye(4)
        translation[:3, 3] = node["translation"]
        matrix = translation @ matrix
    return matrix


def read_glb_geometry(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Every mesh of a GLB in Blender space (glTF y-up turned z-up, as Blender's importer does): positions and triangles."""

    from lib.texture_lineage import _read_glb

    document, binary = _read_glb(Path(path))
    positions, triangles, offset = [], [], 0

    def visit(index: int, parent: np.ndarray) -> None:
        nonlocal offset
        node = document["nodes"][index]
        world = parent @ _node_matrix(node)
        if "mesh" in node:
            for primitive in document["meshes"][node["mesh"]]["primitives"]:
                if primitive.get("mode", 4) != 4:
                    continue
                p = _accessor(document, binary, primitive["attributes"]["POSITION"]).astype(float)
                p = p @ world[:3, :3].T + world[:3, 3]
                t = _accessor(document, binary, primitive["indices"]).reshape(-1, 3).astype(np.int64) if "indices" in primitive else np.arange(len(p)).reshape(-1, 3)
                positions.append(p)
                triangles.append(t + offset)
                offset += len(p)
        for child in node.get("children", []):
            visit(child, world)

    scene = document.get("scenes", [{}])[document.get("scene", 0)]
    for root in scene.get("nodes", range(len(document.get("nodes", [])))):
        visit(root, np.eye(4))
    p = np.concatenate(positions)
    # glTF (x, y up, z toward the viewer) -> Blender (x, -z, y)
    return np.stack([p[:, 0], -p[:, 2], p[:, 1]], axis=1), np.concatenate(triangles)


def plan(points: np.ndarray, triangles: np.ndarray, contract: dict, front: Optional[str] = None) -> dict:
    """What the Blender stage will do to a model, run on its arrays: the turn, the size and place, the cuts."""

    kind = contract["kind"]
    samples = surface_samples(points, triangles)
    turns = FRONT_TURNS[front] if front else facing_quarter_turns(samples, kind, contract.get("rules", {}).get("turret"))
    samples = rotate_quarter_turns(samples, turns)
    scale, offset = placement(samples, kind, contract)
    placed = samples * scale + offset
    out = {"quarter_turns": turns, "scale": scale, "offset": [float(v) for v in offset],
           "low": [float(v) for v in placed.min(axis=0)], "high": [float(v) for v in placed.max(axis=0)], "triangles": int(len(triangles))}
    if kind == "vehicle":
        out["turret_cut"] = turret_cut(placed, contract["rules"]["turret"])
        out["barrel_cut"] = barrel_cut(placed, out["turret_cut"]["cut_z"], contract["rules"]["barrel"])
    elif kind == "plane":
        out["propeller_cut"] = propeller_cut(placed, contract["rules"]["propeller"])
    elif kind == "ship":
        out["draft"] = contract["waterline"]["draft_share"] * contract["size"]["source"]
    return out
