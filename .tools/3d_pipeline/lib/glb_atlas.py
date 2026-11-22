"""One texture atlas for a GLB whose parts carry their own maps (Tripo's Generate in Parts can give each part its own).

The static route packs one diffuse, one normal and one specular map per model, so a GLB with several base colour maps
is first rewritten with one material: each used material's base colour, normal and metallic-roughness maps go into a
square tile of one atlas, and the UVs of the primitives that use it are moved into that tile.

- **Tile sizes follow surface area.** Each material's tile is a power-of-two share of the atlas side, its area at most
  the material's share of the model's surface area, rounded down to a power of four. Such squares always pack into the
  atlas (largest first, each into the first free cell of a quadtree), so no part loses its tile, and texel density
  stays close to even, so a small part such as the gun does not take as much texture as the hull.
- **Gutters.** Each map is resized into its tile less a gutter and its edge pixels are repeated outward, so mip levels
  do not bleed a neighbour's colour across a seam. The UVs move into the tile's inner square.
- **Factors are baked in.** A material's base colour factor multiplies its colour tile, and its metallic and roughness
  factors its metallic-roughness tile (a missing map is the factor itself). A missing normal map is flat.
- **Refusals.** UVs outside 0 to 1 (a repeating texture cannot share an atlas), a primitive without UVs or a material,
  or an embedded map that cannot be read stop the stage with a message, never a silent change of the model's look.

The geometry, nodes and part names are kept unchanged, so the parts route reads the merged GLB as it read the source.
"""

from __future__ import annotations

import io
import json
import math
import struct
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image

from lib import texture_lineage

GUTTER = 8
"""Pixels each tile keeps free on every side at the atlas side, enough for the mip levels the game samples at map zoom."""

_COMPONENTS = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
_WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
_NORMALISED = {5121: 255.0, 5123: 65535.0}
_UV_SLACK = 1e-3


class AtlasError(ValueError):
    """The GLB's maps cannot share one atlas without changing how the model looks."""


def _accessor(document: dict, binary: bytes, index: int) -> np.ndarray:
    accessor = document["accessors"][index]
    dtype = np.dtype(_COMPONENTS[accessor["componentType"]])
    width = _WIDTH[accessor["type"]]
    count = int(accessor["count"])
    view = document["bufferViews"][accessor["bufferView"]]
    start = int(view.get("byteOffset", 0)) + int(accessor.get("byteOffset", 0))
    stride = int(view.get("byteStride") or dtype.itemsize * width)
    rows = np.ndarray((count, width), dtype=dtype, buffer=binary, offset=start, strides=(stride, dtype.itemsize))
    values = rows.astype(np.float64)
    if accessor.get("normalized") and accessor["componentType"] in _NORMALISED:
        values /= _NORMALISED[accessor["componentType"]]
    return values if width > 1 else values[:, 0]


def _area(document: dict, binary: bytes, primitive: dict) -> float:
    positions = _accessor(document, binary, primitive["attributes"]["POSITION"])
    if "indices" in primitive:
        triangles = _accessor(document, binary, primitive["indices"]).astype(np.int64).reshape(-1, 3)
    else:
        triangles = np.arange(len(positions) - len(positions) % 3).reshape(-1, 3)
    a, b, c = (positions[triangles[:, i]] for i in range(3))
    return float(0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1).sum())


def _image(document: dict, binary: bytes, glb: Path, slot: Optional[dict]) -> Optional[Image.Image]:
    if not isinstance(slot, dict) or not isinstance(slot.get("index"), int):
        return None
    if slot.get("texCoord", 0) != 0:
        raise AtlasError(f"{glb.name}: a map reads UV set {slot['texCoord']}; the atlas moves UV set 0 only")
    source = document["textures"][slot["index"]].get("source")
    raw = texture_lineage._image_bytes(document, binary, glb, source) if isinstance(source, int) else None
    if not raw:
        raise AtlasError(f"{glb.name}: texture {slot['index']} has no readable image")
    return Image.open(io.BytesIO(raw))


def tile_sides(areas: List[float], side: int) -> List[int]:
    """Each material's tile side: a power-of-two share of `side` whose area is at most its share of the surface."""

    total = sum(areas) or 1.0
    sides = []
    for area in areas:
        share = max(area / total, 1e-9)
        level = max(0, math.ceil(math.log(1.0 / share, 4) - 1e-9))
        sides.append(max(side >> level, 4 * GUTTER))
    return sides


def pack(sides: List[int], side: int) -> List[Tuple[int, int]]:
    """Top-left corners for power-of-two squares whose areas sum to at most side**2: largest first, each into the first
    free cell of a quadtree (always fits)."""

    order = sorted(range(len(sides)), key=lambda i: -sides[i])
    free = [(0, 0, side)]
    corners: Dict[int, Tuple[int, int]] = {}
    for i in order:
        want = sides[i]
        for k, (x, y, s) in enumerate(free):
            if s >= want:
                del free[k]
                while s > want:
                    s //= 2
                    free[k:k] = [(x + s, y, s), (x, y + s, s), (x + s, y + s, s)]
                corners[i] = (x, y)
                break
        else:
            raise AtlasError(f"the tiles ({sides}) do not fit an atlas of {side}")
    return [corners[i] for i in range(len(sides))]


def _tile(image: Image.Image, side: int) -> Image.Image:
    inner = side - 2 * GUTTER
    small = np.asarray(image.resize((inner, inner), Image.LANCZOS))
    padding = ((GUTTER, GUTTER), (GUTTER, GUTTER)) + ((0, 0),) * (small.ndim - 2)
    return Image.fromarray(np.pad(small, padding, mode="edge"))


def _scaled(image: Image.Image, factors: Tuple[float, float, float]) -> Image.Image:
    if all(abs(f - 1.0) < 1e-6 for f in factors):
        return image
    data = np.asarray(image, dtype=np.float64) * np.asarray(factors)
    return Image.fromarray(np.clip(data + 0.5, 0, 255).astype(np.uint8))


def material_maps(document: dict, binary: bytes, glb: Path, material: dict, side: int) -> Dict[str, Image.Image]:
    """The material's colour, normal and metallic-roughness maps as RGB images of `side`, its factors baked in."""

    pbr = material.get("pbrMetallicRoughness", {})
    colour = _image(document, binary, glb, pbr.get("baseColorTexture"))
    factor = pbr.get("baseColorFactor", [1, 1, 1, 1])[:3]
    colour = (colour.convert("RGB").resize((side, side), Image.LANCZOS) if colour
              else Image.new("RGB", (side, side), (255, 255, 255)))
    normal = _image(document, binary, glb, material.get("normalTexture"))
    normal = normal.convert("RGB").resize((side, side), Image.LANCZOS) if normal else Image.new("RGB", (side, side), (128, 128, 255))
    metal = _image(document, binary, glb, pbr.get("metallicRoughnessTexture"))
    metal = metal.convert("RGB").resize((side, side), Image.LANCZOS) if metal else Image.new("RGB", (side, side), (255, 255, 255))
    rough_factor, metal_factor = float(pbr.get("roughnessFactor", 1.0)), float(pbr.get("metallicFactor", 1.0))
    return {"diffuse": _scaled(colour, tuple(float(f) for f in factor)), "normal": normal,
            "specular": _scaled(metal, (1.0, rough_factor, metal_factor))}


def _png(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _material_areas(document: dict, binary: bytes, glb: Path) -> Dict[int, float]:
    """Each used material's surface area, in first-use order; refuses a primitive the atlas cannot move."""

    areas: Dict[int, float] = {}
    for m, mesh in enumerate(document.get("meshes") or []):
        for p, primitive in enumerate(mesh.get("primitives") or []):
            material = primitive.get("material")
            if not isinstance(material, int):
                raise AtlasError(f"{glb.name}: mesh {m} primitive {p} has no material, so its tile is unknown")
            if "TEXCOORD_0" not in primitive.get("attributes", {}):
                raise AtlasError(f"{glb.name}: mesh {m} primitive {p} has no UVs")
            uv = _accessor(document, binary, primitive["attributes"]["TEXCOORD_0"])
            if len(uv) and (uv.min() < -_UV_SLACK or uv.max() > 1 + _UV_SLACK):
                raise AtlasError(f"{glb.name}: mesh {m} primitive {p} has UVs from {uv.min():.3f} to {uv.max():.3f}; "
                                 "a repeating texture cannot share an atlas")
            areas[material] = areas.get(material, 0.0) + _area(document, binary, primitive)
    return areas


def _atlas_side(document: dict, binary: bytes, glb: Path, used: List[int]) -> int:
    """Twice the largest colour map, a power of two of at least 1024 (the route resizes to the kind's size later)."""

    largest = 0
    for material in used:
        image = _image(document, binary, glb, document["materials"][material].get("pbrMetallicRoughness", {}).get("baseColorTexture"))
        largest = max(largest, max(image.size) if image else 0)
    return 1 << max(10, math.ceil(math.log2(max(largest, 1) * 2)))


def _paint(document: dict, binary: bytes, glb: Path, used: List[int], sides: List[int], corners, side: int) -> Dict[str, Image.Image]:
    atlases = {"diffuse": Image.new("RGB", (side, side), (0, 0, 0)), "normal": Image.new("RGB", (side, side), (128, 128, 255)),
               "specular": Image.new("RGB", (side, side), (255, 255, 255))}
    for material, tile_side, corner in zip(used, sides, corners):
        for role, image in material_maps(document, binary, glb, document["materials"][material], tile_side).items():
            atlases[role].paste(_tile(image, tile_side), corner)
    return atlases


class _Buffer:
    """The GLB's binary chunk with views appended to it."""

    def __init__(self, document: dict, binary: bytes) -> None:
        self.document, self.chunks = document, bytearray(binary)

    def _align(self) -> None:
        while len(self.chunks) % 4:
            self.chunks.append(0)

    def append(self, data: bytes) -> int:
        self._align()
        self.document.setdefault("bufferViews", []).append({"buffer": 0, "byteOffset": len(self.chunks), "byteLength": len(data)})
        self.chunks.extend(data)
        return len(self.document["bufferViews"]) - 1

    def write(self, out: Path) -> None:
        self._align()
        self.document["buffers"] = [{"byteLength": len(self.chunks)}]
        text = json.dumps(self.document, separators=(",", ":")).encode("utf-8")
        text += b" " * (-len(text) % 4)
        body = struct.pack("<II", len(text), 0x4E4F534A) + text + struct.pack("<II", len(self.chunks), 0x004E4942) + bytes(self.chunks)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(struct.pack("<III", 0x46546C67, 2, 12 + len(body)) + body)


def _move_uvs(document: dict, binary: bytes, buffer: _Buffer, tiles: Dict[int, tuple], side: int) -> None:
    """Each primitive's UVs moved into its material's tile, inside the gutter, and the primitive set to the atlas."""

    for mesh in document.get("meshes") or []:
        for primitive in mesh.get("primitives") or []:
            x, y, tile_side = tiles[primitive["material"]]
            uv = np.clip(_accessor(document, binary, primitive["attributes"]["TEXCOORD_0"]), 0.0, 1.0)
            inner = tile_side - 2 * GUTTER
            moved = np.stack([(x + GUTTER + uv[:, 0] * inner) / side, (y + GUTTER + uv[:, 1] * inner) / side], axis=1)
            view = buffer.append(moved.astype("<f4").tobytes())
            document["accessors"].append({"bufferView": view, "componentType": 5126, "count": len(moved), "type": "VEC2",
                                          "min": moved.min(axis=0).tolist(), "max": moved.max(axis=0).tolist()})
            primitive["attributes"]["TEXCOORD_0"] = len(document["accessors"]) - 1
            primitive["material"] = 0


def merged_glb(glb: Path, out: Path, side: Optional[int] = None) -> Optional[dict]:
    """Write `out` with one atlas material when `glb` uses more than one base colour map; return what was done, or None
    (and write nothing) when the GLB already has one map."""

    if len(texture_lineage.embedded_images(glb)["diffuse"]) < 2:
        return None
    document, binary = texture_lineage._read_glb(glb)
    areas = _material_areas(document, binary, glb)
    used = list(areas)
    side = side or _atlas_side(document, binary, glb, used)
    sides = tile_sides([areas[m] for m in used], side)
    corners = pack(sides, side)
    atlases = _paint(document, binary, glb, used, sides, corners, side)
    tiles = {m: (x, y, s) for m, s, (x, y) in zip(used, sides, corners)}
    names = {m: str(document["materials"][m].get("name") or f"material_{m}") for m in used}
    buffer = _Buffer(document, binary)
    _move_uvs(document, binary, buffer, tiles, side)
    document["images"] = [{"bufferView": buffer.append(_png(atlases[role])), "mimeType": "image/png", "name": f"atlas_{role}"}
                          for role in ("diffuse", "normal", "specular")]
    document["samplers"] = [{"magFilter": 9729, "minFilter": 9987, "wrapS": 33071, "wrapT": 33071}]
    document["textures"] = [{"source": i, "sampler": 0} for i in range(3)]
    document["materials"] = [{"name": "atlas", "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}, "metallicRoughnessTexture": {"index": 2},
                                                                         "baseColorFactor": [1, 1, 1, 1], "metallicFactor": 1.0, "roughnessFactor": 1.0},
                              "normalTexture": {"index": 1}}]
    buffer.write(Path(out))
    return {"atlas": side, "gutter": GUTTER, "materials": len(used),
            "tiles": {names[m]: {"corner": list(tiles[m][:2]), "side": tiles[m][2], "area": round(areas[m], 6)} for m in used}}
