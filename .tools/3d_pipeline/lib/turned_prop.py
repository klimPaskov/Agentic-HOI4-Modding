"""A straight prop built from one side-view picture: spears, lances, pikes, poles and staffs (no Blender, no credits).

A polearm is a turned shaft with a flat blade at its head. Its picture already holds every detail a model needs: the outline gives the
width at each point along the length, and the colours give the texture. This module measures that outline and builds the model from it,
so the model keeps the picture's design exactly and adds nothing:

- `measure`: the picture's background is the median colour of its border. The prop is the largest region that differs from it. Its long
  axis is found from the region's pixels (the picture is turned level first when it is tilted), and each column across that axis gives the
  outline's top, bottom and centre.
- The flat part: a blade is flat, not round. From the end with the wider part (the head) inward, the columns wider than FLAT_RATIO of the
  shaft's median width are the blade, down to the first column that is not. A blade gets a diamond section: its edges at the outline, and
  a midrib BLADE_RIB of its width thick (never thicker than the shaft), so it reads as a forged leaf from the side and as a thin plate edge
  on. Every other column is a round ring of RING_SIDES sides whose diameter is the outline's width there: the shaft, a leather grip, a
  socket, the langets, a butt cap.
- The texture is the picture itself, projected along the view direction: each vertex takes the colour of the pixel it covers in the
  picture, so the side the picture shows is the picture, and the far side its mirror. The background around the outline is filled with the
  nearest prop colour (EDGE_FILL passes), so no grey bleeds onto the silhouette.

`build` returns positions, normals, UVs and triangles in glTF axes (the long axis along +X, the picture's up along +Y), and `write_glb`
writes one textured GLB. The tool is `tripo/turned_prop.py`.
"""

from __future__ import annotations

import io
import json
import math
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
from PIL import Image

BACKGROUND_TOLERANCE = 28.0  # RGB distance from the background colour that counts as the prop
FLAT_RATIO = 1.6  # a column this many times the shaft's median width, at the head end, is the blade
BLADE_RIB = 0.22  # the blade's midrib thickness as a share of its width at that column
RING_SIDES = 12
COLUMN_STEP = 2  # pixels between measured columns
BLADE_BASE_STEP = 1.0  # pixels a blade's base narrows toward the socket over BLADE_BASE_SPAN columns
BLADE_BASE_SPAN = 4
RING_TOLERANCE = 1.5  # pixels the model's outline may differ from the picture's between kept rings (the picture's own edge is about this soft)
EDGE_FILL = 12  # passes that spread the prop's colours over the background around it


@dataclass
class Profile:
    image: Image.Image  # the level picture (RGBA)
    xs: np.ndarray  # column x in pixels, from the butt to the head
    centre: np.ndarray  # outline centre (row) per column
    width: np.ndarray  # outline width in pixels per column
    flat: np.ndarray  # True where the column is blade
    shaft_width: float
    head_at_end: bool  # True when the head is at the larger x (the columns run from the butt to the head)

    @property
    def length_px(self) -> float:
        return float(abs(self.xs[-1] - self.xs[0]))


def _mask(rgb: np.ndarray, tolerance: float) -> np.ndarray:
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    background = np.median(border, axis=0)
    mask = np.linalg.norm(rgb - background, axis=2) > tolerance
    return _largest(mask)


def _largest(mask: np.ndarray) -> np.ndarray:
    """The largest 4-connected region of `mask` (a flood fill by rows, no SciPy)."""

    labels = np.zeros(mask.shape, dtype=np.int32)
    best, best_size, current = 0, 0, 0
    height, width = mask.shape
    for start in zip(*np.nonzero(mask)):
        if labels[start]:
            continue
        current += 1
        stack, size = [start], 0
        labels[start] = current
        while stack:
            y, x = stack.pop()
            size += 1
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and not labels[ny, nx]:
                    labels[ny, nx] = current
                    stack.append((ny, nx))
        if size > best_size:
            best, best_size = current, size
    return labels == best


def measure(path: Path, tolerance: float = BACKGROUND_TOLERANCE) -> Profile:
    image = Image.open(path).convert("RGBA")
    rgb = np.asarray(image.convert("RGB"), dtype=float)
    mask = _mask(rgb, tolerance)
    ys, xs = np.nonzero(mask)
    points = np.column_stack([xs, ys]).astype(float)
    points -= points.mean(axis=0)
    _, _, vt = np.linalg.svd(points, full_matrices=False)
    angle = math.degrees(math.atan2(vt[0][1], vt[0][0]))
    angle = (angle + 90.0) % 180.0 - 90.0
    if abs(angle) > 0.3:
        background = tuple(int(v) for v in np.median(np.concatenate([rgb[0], rgb[-1]]), axis=0)) + (255,)
        image = image.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=background)
        rgb = np.asarray(image.convert("RGB"), dtype=float)
        mask = _mask(rgb, tolerance)
    cols = np.nonzero(mask.any(axis=0))[0]
    xs = np.arange(cols.min(), cols.max() + 1, COLUMN_STEP)
    top = np.array([np.nonzero(mask[:, x])[0].min() if mask[:, x].any() else np.nan for x in xs], dtype=float)
    bottom = np.array([np.nonzero(mask[:, x])[0].max() + 1 if mask[:, x].any() else np.nan for x in xs], dtype=float)
    keep = ~np.isnan(top)
    xs, top, bottom = xs[keep], top[keep], bottom[keep]
    width = bottom - top
    centre = 0.5 * (top + bottom)
    shaft = float(np.median(width))
    tenth = max(1, len(xs) // 10)
    head_at_end = float(width[-tenth:].max()) >= float(width[:tenth].max())
    if not head_at_end:
        xs, centre, width = xs[::-1], centre[::-1], width[::-1]
    flat = np.zeros(len(xs), dtype=bool)
    wide = width > FLAT_RATIO * shaft
    if wide.any():
        # the blade runs from the head end inward to the first column (from the shaft side) of the last wide run
        index = len(xs) - 1
        while index >= 0 and not wide[index]:
            index -= 1  # the very tip narrows below the ratio: it is still blade
        while index >= 0 and wide[index]:
            index -= 1
        # the leaf's base narrows into the socket below the ratio: it is blade while it keeps narrowing toward the shaft, by at least
        # BLADE_BASE_STEP pixels over the next BLADE_BASE_SPAN columns (an outline steps in whole pixels, so single columns plateau)
        while index >= BLADE_BASE_SPAN and width[index] - width[index - BLADE_BASE_SPAN] >= BLADE_BASE_STEP:
            index -= 1
        flat[index + 1:] = True
    return Profile(image=image, xs=xs, centre=centre, width=width, flat=flat, shaft_width=shaft, head_at_end=head_at_end)


def build(profile: Profile, length: float) -> Dict[str, np.ndarray]:
    """Vertices along the prop from the butt (x 0) to the head (x `length`), in glTF axes, with UVs into `profile.image`."""

    scale = length / max(profile.length_px, 1.0)
    w_img, h_img = profile.image.size
    rows, flats = [], []
    kept = kept_columns(profile)
    for x_px, centre, width, flat in zip(profile.xs[kept], profile.centre[kept], profile.width[kept], profile.flat[kept]):
        x = (x_px - profile.xs[0]) * scale if profile.head_at_end else (profile.xs[0] - x_px) * scale
        half = 0.5 * width * scale
        if flat:
            rib = min(BLADE_RIB * width, profile.shaft_width) * 0.5 * scale
            # diamond: top edge, front rib, bottom edge, back rib; each corner twice for sharp normals is left out (a forged leaf is soft)
            ring = [(0.0, half), (rib, 0.0), (0.0, -half), (-rib, 0.0)]
            ring = [(z, y) for z, y in ring]
            ring = _resample(ring, RING_SIDES)
        else:
            ring = [(half * math.sin(2 * math.pi * k / RING_SIDES), half * math.cos(2 * math.pi * k / RING_SIDES)) for k in range(RING_SIDES)]
        rows.append([(x, y, z, x_px, centre - y / scale) for z, y in ring])
        flats.append(flat)
    positions, uvs = [], []
    for row in rows:
        for x, y, z, x_px, row_px in row:
            positions.append((x, y, z))
            uvs.append((x_px / w_img, row_px / h_img))
    triangles = []
    count = len(rows)
    for i in range(count - 1):
        for k in range(RING_SIDES):
            a, b = i * RING_SIDES + k, i * RING_SIDES + (k + 1) % RING_SIDES
            c, d = a + RING_SIDES, b + RING_SIDES
            triangles += [(a, c, b), (b, c, d)]
    for end, sign in ((0, -1), (count - 1, 1)):
        x = rows[end][0][0]
        centre_index = len(positions)
        positions.append((x, 0.0, 0.0))
        uvs.append((rows[end][0][3] / w_img, profile.centre[kept][end] / h_img))
        for k in range(RING_SIDES):
            a, b = end * RING_SIDES + k, end * RING_SIDES + (k + 1) % RING_SIDES
            triangles.append((centre_index, a, b) if sign > 0 else (centre_index, b, a))
    positions = np.asarray(positions, dtype=np.float32)
    triangles = np.asarray(triangles, dtype=np.uint32)
    triangles = _outward(positions, triangles)
    return {"positions": positions, "uvs": np.asarray(uvs, dtype=np.float32), "triangles": triangles,
            "normals": _normals(positions, triangles), "blade_share": float(profile.flat.mean())}


def kept_columns(profile: Profile) -> np.ndarray:
    """The columns that get a ring: the fewest whose straight lines between them keep the outline's width and centre within RING_TOLERANCE
    pixels of the picture's (Douglas and Peucker's rule), and both sides of every change between round and blade. A straight stretch of
    shaft needs no rings between its ends: the shape is the same within the picture's own accuracy, and the texture's projection runs
    linearly along it."""

    xs = profile.xs.astype(float)
    keep = np.zeros(len(xs), dtype=bool)
    keep[[0, -1]] = True
    edges = np.nonzero(np.diff(profile.flat.astype(int)) != 0)[0]
    keep[edges] = True
    keep[edges + 1] = True
    anchors = list(np.nonzero(keep)[0])
    for left, right in zip(anchors[:-1], anchors[1:]):
        stack = [(left, right)]
        while stack:
            a, b = stack.pop()
            if b - a < 2:
                continue
            t = (xs[a + 1:b] - xs[a]) / (xs[b] - xs[a])
            error = np.maximum(np.abs(profile.width[a + 1:b] - (profile.width[a] + t * (profile.width[b] - profile.width[a]))),
                               np.abs(profile.centre[a + 1:b] - (profile.centre[a] + t * (profile.centre[b] - profile.centre[a]))))
            worst = int(np.argmax(error))
            if error[worst] > RING_TOLERANCE:
                middle = a + 1 + worst
                keep[middle] = True
                stack += [(a, middle), (middle, b)]
    return np.nonzero(keep)[0]


def _resample(polygon, sides: int):
    """`sides` points evenly round a closed polygon of (z, y) corners."""

    corners = np.asarray(polygon + [polygon[0]], dtype=float)
    segments = np.linalg.norm(np.diff(corners, axis=0), axis=1)
    total = segments.sum()
    out = []
    for k in range(sides):
        target = total * k / sides
        index = int(np.searchsorted(np.cumsum(segments), target, side="right"))
        index = min(index, len(segments) - 1)
        before = np.cumsum(segments)[index - 1] if index else 0.0
        t = (target - before) / max(segments[index], 1e-12)
        out.append(tuple(corners[index] + t * (corners[index + 1] - corners[index])))
    return out


def _outward(positions: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    """Turn every triangle whose normal points toward the long axis (the prop is a tube round +X)."""

    a, b, c = positions[triangles[:, 0]], positions[triangles[:, 1]], positions[triangles[:, 2]]
    normal = np.cross(b - a, c - a)
    centre = (a + b + c) / 3.0
    radial = centre.copy()
    radial[:, 0] = 0.0
    side = (normal * radial).sum(axis=1)
    ends = np.linalg.norm(radial, axis=1) < 1e-9
    flip = (side < 0) & ~ends
    fixed = triangles.copy()
    fixed[flip] = fixed[flip][:, [0, 2, 1]]
    return fixed


def _normals(positions: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    normals = np.zeros_like(positions)
    a, b, c = positions[triangles[:, 0]], positions[triangles[:, 1]], positions[triangles[:, 2]]
    face = np.cross(b - a, c - a)
    for k in range(3):
        np.add.at(normals, triangles[:, k], face)
    return (normals / np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-12)).astype(np.float32)


def filled_texture(profile: Profile, tolerance: float = BACKGROUND_TOLERANCE) -> Image.Image:
    """The picture with the background around the prop filled by its nearest colours, so no background shows on the edge."""

    rgb = np.asarray(profile.image.convert("RGB"), dtype=float)
    mask = _mask(rgb, tolerance)
    known = mask.copy()
    colour = np.where(mask[..., None], rgb, 0.0)
    for _ in range(EDGE_FILL):
        total = np.zeros_like(colour)
        weight = np.zeros(mask.shape)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            shifted_known = np.roll(known, (dy, dx), axis=(0, 1))
            total += np.roll(colour, (dy, dx), axis=(0, 1)) * shifted_known[..., None]
            weight += shifted_known
        grow = ~known & (weight > 0)
        colour[grow] = total[grow] / weight[grow][:, None]
        known |= grow
    out = np.where(known[..., None], colour, rgb)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def write_glb(path: Path, mesh: Dict[str, np.ndarray], texture: Image.Image, name: str = "prop") -> None:
    png = io.BytesIO()
    texture.save(png, format="PNG")
    blobs = [mesh["positions"].tobytes(), mesh["normals"].tobytes(), mesh["uvs"].tobytes(), mesh["triangles"].astype(np.uint32).tobytes(), png.getvalue()]
    views, offset, binary = [], 0, b""
    for blob in blobs:
        pad = (-len(blob)) % 4
        views.append({"buffer": 0, "byteOffset": offset, "byteLength": len(blob)})
        binary += blob + b"\0" * pad
        offset += len(blob) + pad
    count = len(mesh["positions"])
    document = {
        "asset": {"version": "2.0", "generator": "hoi4 kit turned_prop"},
        "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0, "name": name}],
        "meshes": [{"name": name, "primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2}, "indices": 3, "material": 0}]}],
        "materials": [{"name": name, "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}, "metallicFactor": 0.0, "roughnessFactor": 0.8}}],
        "textures": [{"source": 0, "sampler": 0}], "samplers": [{"magFilter": 9729, "minFilter": 9987}],
        "images": [{"bufferView": 4, "mimeType": "image/png"}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": count, "type": "VEC3", "min": mesh["positions"].min(axis=0).tolist(), "max": mesh["positions"].max(axis=0).tolist()},
            {"bufferView": 1, "componentType": 5126, "count": count, "type": "VEC3"},
            {"bufferView": 2, "componentType": 5126, "count": count, "type": "VEC2"},
            {"bufferView": 3, "componentType": 5125, "count": int(mesh["triangles"].size), "type": "SCALAR"},
        ],
        "bufferViews": views, "buffers": [{"byteLength": len(binary)}],
    }
    text = json.dumps(document, separators=(",", ":")).encode("utf-8")
    text += b" " * ((-len(text)) % 4)
    out = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(text) + 8 + len(binary))
    out += struct.pack("<II", len(text), 0x4E4F534A) + text + struct.pack("<II", len(binary), 0x004E4942) + binary
    Path(path).write_bytes(out)
