"""Measure a model's body from its surface: how many legs reach the ground, how long they are, how wide
the torso is and how far the arms reach. No Blender and no rig: it reads a provider `.glb` (glTF 2.0
binary, as Meshy delivers it) or an exported `.mesh`, both Y up.

Every measure is a share of the model's height, so a 2 m soldier and a 7 m giant compare directly.
The surface is sampled evenly by area (a fixed seed, so the result never changes), cut into thin
horizontal slices, and each slice's footprint is split into separate pieces on a grid:

- `contacts` at foot height (4 % of the height) and the most `legs` found between 8 % and 26 %;
- `crotch`: the lowest slice above the feet where the legs have joined into one piece;
- `lower_length`: the longest horizontal reach of everything below half the height (a horse's body
  and legs, a soldier's stance);
- `torso_width` and `torso_depth` at 70 % of the height, of the piece that holds the body's centre;
- `arm_span`: the widest reach above half the height (arms, wings, a held pole);
- `upper_pieces`: the most separate pieces in one slice between 55 % and 85 % (a body with two free
  arms has three; with four arms, five);
- `top_pieces`: the most pieces between 85 % and the top (a rider fused to a mount, horns, ears).
"""

from __future__ import annotations

import json
import struct
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

SAMPLES = 60000
SEED = 1936
SLICE_HALF = 0.02  # each slice is 4 % of the height thick
CELL = 0.015  # grid cell, as a share of the height
MIN_PIECE = 0.0006  # a piece's footprint must cover this share of the height squared
FOOT = 0.04
LEG_BANDS = (0.08, 0.12, 0.16, 0.20, 0.24)
UPPER_BANDS = (0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85)
TOP_BANDS = (0.88, 0.92, 0.96)
CROTCH_BANDS = tuple(round(0.08 + 0.02 * i, 2) for i in range(30))  # 0.08 to 0.66


class BodyFormatError(ValueError):
    pass


# ---- reading ----


def _accessor(gltf: dict, binary: bytes, index: int) -> np.ndarray:
    accessor = gltf["accessors"][index]
    view = gltf["bufferViews"][accessor["bufferView"]]
    width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}[accessor["type"]]
    dtype = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}[accessor["componentType"]]
    itemsize = np.dtype(dtype).itemsize * width
    stride = view.get("byteStride") or itemsize
    start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    count = accessor["count"]
    if stride == itemsize:
        data = np.frombuffer(binary, dtype=dtype, count=count * width, offset=start)
    else:
        raw = np.frombuffer(binary, dtype=np.uint8, count=stride * (count - 1) + itemsize, offset=start)
        rows = np.lib.stride_tricks.as_strided(raw, shape=(count, itemsize), strides=(stride, 1))
        data = np.ascontiguousarray(rows).view(dtype)
    return data.reshape(count, width) if width > 1 else data.reshape(count)


def _node_matrix(node: dict) -> np.ndarray:
    if "matrix" in node:
        return np.asarray(node["matrix"], dtype=float).reshape(4, 4).T
    matrix = np.eye(4)
    x, y, z, w = node.get("rotation", [0.0, 0.0, 0.0, 1.0])
    rotation = np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]
    )
    matrix[:3, :3] = rotation * np.asarray(node.get("scale", [1.0, 1.0, 1.0]))[None, :]
    matrix[:3, 3] = node.get("translation", [0.0, 0.0, 0.0])
    return matrix


def load_glb(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Positions (V, 3) and triangles (T, 3) of every mesh in the default scene, in world space."""

    data = path.read_bytes()
    if data[:4] != b"glTF":
        raise BodyFormatError(f"{path.name} is not a binary glTF file")
    offset, gltf, binary = 12, None, b""
    while offset + 8 <= len(data):
        length, kind = struct.unpack_from("<II", data, offset)
        chunk = data[offset + 8 : offset + 8 + length]
        if kind == 0x4E4F534A:
            gltf = json.loads(chunk.decode("utf-8"))
        elif kind == 0x004E4942:
            binary = chunk
        offset += 8 + length
    if gltf is None:
        raise BodyFormatError(f"{path.name} has no JSON chunk")
    compressed = {"KHR_draco_mesh_compression", "EXT_meshopt_compression"} & set(gltf.get("extensionsRequired", []))
    if compressed:
        raise BodyFormatError(f"{path.name} uses {', '.join(sorted(compressed))}; export it uncompressed")
    positions: List[np.ndarray] = []
    triangles: List[np.ndarray] = []
    count = 0

    def visit(index: int, parent: np.ndarray) -> None:
        nonlocal count
        node = gltf["nodes"][index]
        world = parent @ _node_matrix(node)
        if "mesh" in node:
            for primitive in gltf["meshes"][node["mesh"]]["primitives"]:
                if primitive.get("mode", 4) != 4 or "POSITION" not in primitive.get("attributes", {}):
                    continue
                points = _accessor(gltf, binary, primitive["attributes"]["POSITION"]).astype(float)
                points = points @ world[:3, :3].T + world[:3, 3]
                if "indices" in primitive:
                    tris = _accessor(gltf, binary, primitive["indices"]).astype(np.int64).reshape(-1, 3)
                else:
                    tris = np.arange(len(points), dtype=np.int64).reshape(-1, 3)
                positions.append(points)
                triangles.append(tris + count)
                count += len(points)
        for child in node.get("children", []):
            visit(child, world)

    scene = gltf.get("scenes", [{}])[gltf.get("scene", 0)] if gltf.get("scenes") else {"nodes": list(range(len(gltf.get("nodes", []))))}
    for root in scene.get("nodes", []):
        visit(root, np.eye(4))
    if not positions:
        raise BodyFormatError(f"{path.name} holds no triangle mesh")
    return np.concatenate(positions), np.concatenate(triangles)


def load_surface(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Positions and triangles of a `.glb` or `.mesh` file (Y up)."""

    if path.suffix.lower() == ".glb":
        return load_glb(path)
    if path.suffix.lower() == ".mesh":
        from .pdx_deform import load_mesh

        mesh = load_mesh(path)
        return mesh.positions, mesh.triangles
    raise BodyFormatError(f"{path.name}: measure a .glb or a .mesh file")


# ---- measuring ----


def sample_surface(positions: np.ndarray, triangles: np.ndarray, count: int = SAMPLES) -> np.ndarray:
    """`count` points spread over the surface by area, with a fixed seed."""

    a, b, c = (positions[triangles[:, i]] for i in range(3))
    area = np.linalg.norm(np.cross(b - a, c - a), axis=1)
    if area.sum() <= 0:
        return positions.copy()
    rng = np.random.default_rng(SEED)
    chosen = rng.choice(len(triangles), size=count, p=area / area.sum())
    u, v = rng.random(count), rng.random(count)
    flip = u + v > 1
    u[flip], v[flip] = 1 - u[flip], 1 - v[flip]
    return a[chosen] + (b[chosen] - a[chosen]) * u[:, None] + (c[chosen] - a[chosen]) * v[:, None]


@dataclass
class Piece:
    area: float  # share of height squared
    centre: Tuple[float, float]  # along the major and minor horizontal axes, share of height
    major: float  # extent along the major axis
    minor: float  # extent along the minor axis


def _pieces(points: np.ndarray, height: float) -> List[Piece]:
    """Split a slice's horizontal footprint (N, 2 in axis coordinates) into connected pieces."""

    if len(points) == 0:
        return []
    cell = CELL * height
    grid = np.floor((points - points.min(axis=0)) / cell).astype(int)
    shape = grid.max(axis=0) + 3
    occupied = np.zeros(shape, dtype=bool)
    occupied[grid[:, 0] + 1, grid[:, 1] + 1] = True
    # Close one-cell gaps between samples of one surface.
    grown = occupied.copy()
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            grown |= np.roll(np.roll(occupied, dx, axis=0), dy, axis=1)
    labels = np.zeros(shape, dtype=np.int64)
    current = 0
    for start in zip(*np.nonzero(grown)):
        if labels[start]:
            continue
        current += 1
        stack = [start]
        labels[start] = current
        while stack:
            x, y = stack.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < shape[0] and 0 <= ny < shape[1] and grown[nx, ny] and not labels[nx, ny]:
                        labels[nx, ny] = current
                        stack.append((nx, ny))
    point_label = labels[grid[:, 0] + 1, grid[:, 1] + 1]
    pieces = []
    for label in range(1, current + 1):
        mine = points[point_label == label]
        cells = int((labels == label).sum())
        area = cells * CELL * CELL
        if area < MIN_PIECE or len(mine) < 3:
            continue
        low, high = mine.min(axis=0), mine.max(axis=0)
        pieces.append(Piece(area, tuple((mine.mean(axis=0) / height).round(4)), float((high[0] - low[0]) / height), float((high[1] - low[1]) / height)))
    return sorted(pieces, key=lambda piece: -piece.area)


@dataclass
class BodyMeasures:
    height: float  # in the file's own units
    contacts: int
    legs: int
    crotch: float
    lower_length: float
    lower_width: float
    torso_width: float
    torso_depth: float
    arm_span: float
    upper_pieces: int
    top_pieces: int
    centre_height: float  # mean height of the surface, share of height
    slices: Dict[str, int] = field(default_factory=dict)  # slice height -> pieces, for the record

    def as_dict(self) -> dict:
        data = asdict(self)
        return {key: (round(value, 4) if isinstance(value, float) else value) for key, value in data.items()}


def measure(positions: np.ndarray, triangles: np.ndarray) -> BodyMeasures:
    points = sample_surface(positions, triangles)
    ground = float(points[:, 1].min())
    height = float(points[:, 1].max() - ground)
    if height <= 0:
        raise BodyFormatError("the model is flat")
    level = (points[:, 1] - ground) / height
    flat = points[:, [0, 2]]
    # Horizontal axes: the major axis of the lower body (a quadruped's length, a soldier's stance).
    lower = flat[level < 0.5]
    centred = lower - lower.mean(axis=0)
    _values, vectors = np.linalg.eigh(np.cov(centred.T)) if len(lower) > 2 else (None, np.eye(2))
    major, minor = vectors[:, -1], vectors[:, 0]
    axes = np.stack([flat @ major, flat @ minor], axis=1)

    def band(centre: float) -> List[Piece]:
        chosen = np.abs(level - centre) <= SLICE_HALF
        return _pieces(axes[chosen], height)

    slices = {f"{centre:.2f}": len(band(centre)) for centre in sorted(set((FOOT,) + LEG_BANDS + UPPER_BANDS + TOP_BANDS))}
    contacts = slices[f"{FOOT:.2f}"]
    legs = max(slices[f"{centre:.2f}"] for centre in LEG_BANDS)
    crotch = 1.0
    for centre in CROTCH_BANDS:
        if centre >= 0.12 and len(band(centre)) <= 1:
            crotch = centre
            break
    below = axes[level < 0.5]
    lower_length = float(np.ptp(below[:, 0]) / height) if len(below) else 0.0
    lower_width = float(np.ptp(below[:, 1]) / height) if len(below) else 0.0
    body_centre = axes.mean(axis=0) / height
    torso = band(0.70)
    if torso:
        main = min(torso, key=lambda piece: np.hypot(piece.centre[0] - body_centre[0], piece.centre[1] - body_centre[1]) - piece.area)
        torso_major, torso_minor = main.major, main.minor
    else:
        torso_major = torso_minor = 0.0
    upper = axes[level >= 0.5]
    arm_span = float(max(np.ptp(upper[:, 0]), np.ptp(upper[:, 1])) / height) if len(upper) else 0.0
    return BodyMeasures(
        height=height,
        contacts=contacts,
        legs=legs,
        crotch=crotch,
        lower_length=lower_length,
        lower_width=lower_width,
        torso_width=max(torso_major, torso_minor),
        torso_depth=min(torso_major, torso_minor),
        arm_span=arm_span,
        upper_pieces=max(slices[f"{centre:.2f}"] for centre in UPPER_BANDS),
        top_pieces=max(slices[f"{centre:.2f}"] for centre in TOP_BANDS),
        centre_height=float(level.mean()),
        slices=slices,
    )


def measure_file(path: Path) -> BodyMeasures:
    return measure(*load_surface(path))
