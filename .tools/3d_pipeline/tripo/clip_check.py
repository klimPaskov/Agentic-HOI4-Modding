"""Blender-free check of a rigged Tripo GLB's clips: mesh stretch plus a rigid weapon against the moving body.

    py -3.13 .tools/3d_pipeline/tripo/clip_check.py <rigged.glb> [--body tripo_part_0] [--weapon tripo_part_1]
        [--weapon-bone auto|<joint name>] [--samples 24] [--grip-radius 0.12] [--json out.json] [--fail-on-verdict]
        [--attack <candidate> ...]

With `--attack` it ends with one `attack:` line: the candidates that pass, or `attack: none passes` and exit 3. Run it on the first
export before you leave Tripo (the card's step 6), so a text-to-motion attack is made while the rigged model is still open.

A plain Tripo export (Rig, Animate, Export, no Segment step) is one skinned mesh: its mesh node is named `tripo_node_<id>` and its mesh
`tripo_mesh_<id>`, not `tripo_part_0`. When the body is left at its default name and the file has no such node, the one skinned mesh is
the body. It has no weapon part either, so with the default weapon name absent (or `--weapon none`) the check measures stretch only, for an
unarmed unit. A body or weapon named on the command line that the file lacks is still an error.

Ranking clips by mesh stretch alone passes a clip whose weapon goes through the torso. This tool
skins the body with linear blend skinning, numpy only, at `--samples` times per clip and measures:

- stretch: the share of body edges longer than 1.5x or shorter than 0.5x of their rest length in the
  worst sampled frame, and the longest edge growth as a share of the body height (the same numbers
  as the stretch script from the Tripo orc trials);
- weapon in body: the weapon is treated as rigid. It follows one hand joint (`--weapon-bone auto`
  picks the hand joint nearest to the weapon in the rest pose) instead of its own skin weights, the
  way the weapon is bound later. At most 600 weapon vertices, evenly spaced, are tested per frame.
  Points within `--grip-radius` of the hand joint (a share of the body height, 12 % by default) are
  left out, because the fist always encloses the haft. The result is the share of the remaining
  points inside the deformed body, the share of them deeper than a margin (4 % of the body height,
  `PENETRATION_MARGIN_SHARE`), the deepest penetration as a share of the body height and the worst
  frame. Only the deep share drives the verdict: a haft end or axe head always grazes a thigh or a
  hip a little (the believed-good idle and walk clips show 8 to 13 % of points inside by any
  depth and none deeper than the margin), while the known-bad swing goes about 9 to 10 % of the
  height into the torso;
- weapon below ground: the share of weapon points lower than the lowest rest-pose body vertex minus
  a small tolerance (1 % of the body height), in the worst frame. With `--ground-per-frame` the ground
  is the lowest body vertex of each frame minus 2 %, for clips where the body sinks (death);
- a verdict per clip, pass or fail, with the reasons, from the named thresholds below.

Inside test. The body is a triangle soup that may have holes, reversed faces and inner shells, so a
signed volume or a winding-number test is not trustworthy and a normal-based "behind the nearest
surface" test flips with every reversed face. This module counts ray crossings instead (parity) and
does not read triangle orientation. Each point shoots rays in several fixed, tilted directions. A
point is inside when most rays cross the surface an odd number of times. A hole spoils only the
rays that escape through it, so the vote keeps the answer for points that are not right at the hole.
To stay fast, the triangles are projected along each ray direction and binned in a coarse 2D grid,
so a point meets only the triangles of its own cell. Depth is the distance to the nearest body
vertex, which overestimates by up to about one edge length. Everything is plain numpy.

Exit code 0 always for a report. `--fail-on-verdict` exits 1 when any clip fails.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

# Thresholds. Calibrated against the Tripo orc trials: the known-bad text-to-motion swing clip
# (the haft through torso and cape in its first frames) fails clearly, idle and walk pass.
MAX_IN_BODY_SHARE = 0.02  # share of non-grip weapon points deeper inside the body than the margin, in any sampled frame
PENETRATION_MARGIN_SHARE = 0.04  # a point counts as through the body only when this deep (share of body height)
MAX_BELOW_GROUND_SHARE = 0.02  # share of weapon points below the ground, in any sampled frame
MAX_STRETCHED_PCT = 5.0  # percent of body edges stretched past 1.5x in the worst frame
GRIP_RADIUS_SHARE = 0.12  # grip zone radius as a share of the body height
GROUND_TOLERANCE_SHARE = 0.01  # below-ground tolerance as a share of the body height
FRAME_GROUND_TOLERANCE_SHARE = 0.02  # the same with --ground-per-frame (the ground is the lowest body vertex of the frame)
MAX_WEAPON_POINTS = 600
STRETCH_LONG, STRETCH_SHORT = 1.5, 0.5

# Fixed, tilted ray directions (no axis alignment, so rays do not graze mesh edges). Normalised below.
RAY_DIRECTIONS = np.array(
    [[0.267, 0.534, 0.802], [-0.611, 0.302, 0.733], [0.436, -0.718, 0.543], [-0.287, -0.641, -0.713], [0.874, 0.157, -0.461]]
)
RAY_DIRECTIONS = RAY_DIRECTIONS / np.linalg.norm(RAY_DIRECTIONS, axis=1, keepdims=True)

DEFAULT_BODY = "tripo_part_0"
DEFAULT_WEAPON = "tripo_part_1"
NO_WEAPON = ("", "none")

COMPONENT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


# ---------------------------------------------------------------------------------------------
# Pure maths
# ---------------------------------------------------------------------------------------------


def _basis(direction: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    axis = np.zeros(3)
    axis[int(np.argmin(np.abs(direction)))] = 1.0
    u = np.cross(direction, axis)
    u /= np.linalg.norm(u)
    v = np.cross(direction, u)
    return u, v


def _bin_triangles(t2: np.ndarray, grid: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Cells of a `grid` x `grid` lattice over the projected triangles (T, 3, 2).

    Returns the cell keys and the triangle of each (pairs sorted by key), the lattice origin and cell size,
    and the upper corner of the projected bounds.
    """

    lo, hi = t2.min(axis=1), t2.max(axis=1)
    origin = lo.min(axis=0)
    cell = np.maximum((hi.max(axis=0) - origin) / grid, 1e-12)
    i0 = np.clip(np.floor((lo - origin) / cell).astype(np.int64), 0, grid - 1)
    i1 = np.clip(np.floor((hi - origin) / cell).astype(np.int64), 0, grid - 1)
    nx, ny = i1[:, 0] - i0[:, 0] + 1, i1[:, 1] - i0[:, 1] + 1
    counts = nx * ny
    total = int(counts.sum())
    tri = np.repeat(np.arange(len(t2)), counts)
    local = np.arange(total) - np.repeat(np.cumsum(counts) - counts, counts)
    cx = i0[tri, 0] + local % nx[tri]
    cy = i0[tri, 1] + local // nx[tri]
    key = cx * grid + cy
    order = np.argsort(key, kind="stable")
    return key[order], tri[order], origin, cell, hi.max(axis=0)


def _project(triangles: np.ndarray, direction: np.ndarray, grid: int) -> tuple:
    """The triangles projected along `direction` and binned (`_bin_triangles`): what the ray test needs of a mesh, whatever the points."""

    u, v = _basis(direction)
    plane = np.stack([u, v], axis=1)
    t2 = triangles @ plane  # (T, 3, 2)
    td = triangles @ direction  # (T, 3)
    key, tri, origin, cell, upper = _bin_triangles(t2, grid)
    return plane, direction, t2, td, key, tri, origin, cell, upper, grid


def _inside_projected(points: np.ndarray, projected: tuple) -> np.ndarray:
    """True where a ray from the point along the projection's direction crosses the triangles an odd number of times."""

    plane, direction, t2, td, key, tri, origin, cell, upper, grid = projected
    p2 = points @ plane
    pd = points @ direction
    # Points outside the projected bounds cannot be crossed by any triangle.
    q = np.floor((p2 - origin) / cell).astype(np.int64)
    inside_bounds = np.all((q >= 0) & (q < grid), axis=1) & np.all(p2 >= origin, axis=1) & np.all(p2 <= upper, axis=1)
    result = np.zeros(len(points), dtype=bool)
    candidates = np.nonzero(inside_bounds)[0]
    if not len(candidates):
        return result
    qkey = q[candidates, 0] * grid + q[candidates, 1]
    start = np.searchsorted(key, qkey, side="left")
    stop = np.searchsorted(key, qkey, side="right")
    span = stop - start
    n = int(span.sum())
    if n == 0:
        return result
    owner = np.repeat(np.arange(len(candidates)), span)
    slot = np.arange(n) - np.repeat(np.cumsum(span) - span, span) + np.repeat(start, span)
    t = tri[slot]
    pt = p2[candidates[owner]]
    a, b, c = t2[t, 0], t2[t, 1], t2[t, 2]

    def cross(x, y):
        return x[:, 0] * y[:, 1] - x[:, 1] * y[:, 0]

    det = cross(b - a, c - a)
    ok = np.abs(det) > 1e-14
    safe = np.where(ok, det, 1.0)
    l0 = cross(b - pt, c - pt) / safe
    l1 = cross(c - pt, a - pt) / safe
    l2 = 1.0 - l0 - l1
    eps = -1e-9
    hit = ok & (l0 >= eps) & (l1 >= eps) & (l2 >= eps)
    depth = l0 * td[t, 0] + l1 * td[t, 1] + l2 * td[t, 2]
    hit &= depth > pd[candidates[owner]]
    crossings = np.bincount(owner[hit], minlength=len(candidates))
    result[candidates] = crossings % 2 == 1
    return result


def _inside_along(points: np.ndarray, triangles: np.ndarray, direction: np.ndarray, grid: int) -> np.ndarray:
    """True where a ray from the point along `direction` crosses the triangles an odd number of times."""

    return _inside_projected(points, _project(triangles, direction, grid))


class InsideTest:
    """`points_inside_mesh` for one mesh and many sets of points: the projections and bins are made once.

    The clearance tests hundreds of trial poses of a weapon against one posed body, and binning the body's 20,000 triangles took most of each
    test's 60 ms."""

    def __init__(self, triangles: np.ndarray, directions: Optional[np.ndarray] = None, grid: int = 48):
        triangles = np.asarray(triangles, dtype=np.float64).reshape(-1, 3, 3)
        directions = RAY_DIRECTIONS if directions is None else np.asarray(directions, dtype=np.float64)
        self.empty = not len(triangles)
        self.projected = [] if self.empty else [_project(triangles, d / np.linalg.norm(d), grid) for d in directions]

    def __call__(self, points: np.ndarray) -> np.ndarray:
        points = np.asarray(points, dtype=np.float64).reshape(-1, 3)
        if not len(points) or self.empty:
            return np.zeros(len(points), dtype=bool)
        votes = np.zeros(len(points), dtype=np.int64)
        for projected in self.projected:
            votes += _inside_projected(points, projected)
        return votes * 2 > len(self.projected)


def points_inside_mesh(points: np.ndarray, triangles: np.ndarray, directions: Optional[np.ndarray] = None, grid: int = 48) -> np.ndarray:
    """Boolean mask of the points inside a triangle soup, by majority vote of ray-parity tests.

    `triangles` is (T, 3, 3). Triangle orientation is ignored and the mesh need not be watertight.
    """

    return InsideTest(triangles, directions, grid)(points)


def grip_zone_mask(points: np.ndarray, hand: np.ndarray, radius: float) -> np.ndarray:
    """True for points within `radius` of the hand joint: the fist encloses them by design."""

    return np.linalg.norm(np.asarray(points, dtype=np.float64).reshape(-1, 3) - np.asarray(hand, dtype=np.float64), axis=1) <= radius


def nearest_vertex_distance(points: np.ndarray, vertices: np.ndarray, chunk: int = 64) -> np.ndarray:
    """Distance from each point to its nearest body vertex (an upper bound of the distance to the surface)."""

    points = np.asarray(points, dtype=np.float64).reshape(-1, 3)
    vertices = np.asarray(vertices, dtype=np.float64)
    out = np.empty(len(points))
    vv = (vertices * vertices).sum(axis=1)
    for start in range(0, len(points), chunk):
        block = points[start : start + chunk]
        d2 = (block * block).sum(axis=1)[:, None] + vv[None, :] - 2.0 * block @ vertices.T
        out[start : start + chunk] = np.sqrt(np.maximum(d2.min(axis=1), 0.0))
    return out


def clip_verdict(
    deep_in_body_share: float,
    below_ground_share: float,
    stretched_pct: float,
    max_in_body: float = MAX_IN_BODY_SHARE,
    max_below_ground: float = MAX_BELOW_GROUND_SHARE,
    max_stretched_pct: float = MAX_STRETCHED_PCT,
) -> Dict[str, object]:
    """Pass or fail for one clip, with the reasons. Shares are 0..1, the stretch is in percent."""

    reasons: List[str] = []
    if deep_in_body_share > max_in_body:
        reasons.append(f"weapon through the body (deeper than {PENETRATION_MARGIN_SHARE:.0%} of its height) in {deep_in_body_share:.1%} of its free points (limit {max_in_body:.0%})")
    if below_ground_share > max_below_ground:
        reasons.append(f"weapon below the ground in {below_ground_share:.1%} of its points (limit {max_below_ground:.0%})")
    if stretched_pct > max_stretched_pct:
        reasons.append(f"{stretched_pct:.1f}% of body edges stretched past {STRETCH_LONG}x (limit {max_stretched_pct:g}%)")
    return {"verdict": "fail" if reasons else "pass", "reasons": reasons}


# ---------------------------------------------------------------------------------------------
# GLB loading and skinning
# ---------------------------------------------------------------------------------------------


def load_glb(path) -> Tuple[dict, bytes]:
    """The JSON document and the binary chunk of a GLB, from a path or from the file's bytes."""

    raw = bytes(path) if isinstance(path, (bytes, bytearray)) else Path(path).read_bytes()
    length = struct.unpack("<I", raw[12:16])[0]
    doc = json.loads(raw[20 : 20 + length])
    return doc, raw[20 + length + 8 :]


def read_accessor(doc: dict, binary: bytes, index: int) -> np.ndarray:
    acc = doc["accessors"][index]
    view = doc["bufferViews"][acc["bufferView"]]
    dtype = np.dtype(COMPONENT[acc["componentType"]])
    width = WIDTH[acc["type"]]
    start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    stride = view.get("byteStride") or dtype.itemsize * width
    count = acc["count"]
    if stride == dtype.itemsize * width:
        data = np.frombuffer(binary, dtype=dtype, count=count * width, offset=start).reshape(count, width)
    else:
        data = np.stack([np.frombuffer(binary, dtype=dtype, count=width, offset=start + i * stride) for i in range(count)])
    data = data.astype(np.float64) if dtype.kind == "f" else data
    if acc.get("normalized") and dtype.kind != "f":
        data = data.astype(np.float64) / np.iinfo(dtype).max
    return data


def quat_matrix(q) -> np.ndarray:
    x, y, z, w = q
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]
    )


def local_matrix(t, r, s) -> np.ndarray:
    m = np.eye(4)
    m[:3, :3] = quat_matrix(r) * np.asarray(s)[None, :]
    m[:3, 3] = t
    return m


def sample_track(times, values, t, rotation):
    if t <= times[0]:
        return values[0]
    if t >= times[-1]:
        return values[-1]
    i = int(np.searchsorted(times, t)) - 1
    f = (t - times[i]) / (times[i + 1] - times[i])
    a, b = values[i], values[i + 1]
    if rotation:
        if np.dot(a, b) < 0:
            b = -b
        q = a + (b - a) * f
        return q / np.linalg.norm(q)
    return a + (b - a) * f


class Rig:
    """The skeleton, the skinned parts and the clips of one GLB."""

    def __init__(self, path, body_name: str, weapon_name: Optional[str]):
        self.doc, self.binary = load_glb(path)
        doc = self.doc
        self.nodes = doc["nodes"]
        self.parent = {}
        for index, node in enumerate(self.nodes):
            for child in node.get("children", []):
                self.parent[child] = index
        self.base = []
        for node in self.nodes:
            if "matrix" in node:
                self.base.append(None)
            else:
                self.base.append(
                    (
                        np.array(node.get("translation", [0, 0, 0]), float),
                        np.array(node.get("rotation", [0, 0, 0, 1]), float),
                        np.array(node.get("scale", [1, 1, 1]), float),
                    )
                )
        skin = doc["skins"][0]
        self.joints = skin["joints"]
        self.inverse = read_accessor(doc, self.binary, skin["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1)
        self.joint_names = [self.nodes[j].get("name", str(j)) for j in self.joints]
        self.body_note = self.weapon_note = ""
        skinned = [n for n in self.nodes if "mesh" in n and "skin" in n]
        if body_name == DEFAULT_BODY and not any(n.get("name") == body_name for n in self.nodes if "mesh" in n) and len(skinned) == 1:
            body_name = self.body_name = skinned[0].get("name", "")
            self.body_note = f"the file has no mesh node named {DEFAULT_BODY!r}: the one skinned mesh {body_name!r} is the body"
        else:
            self.body_name = body_name
        self.body = self._part(body_name)
        weapon_missing = weapon_name == DEFAULT_WEAPON and not any(n.get("name") == weapon_name for n in self.nodes if "mesh" in n)
        if weapon_missing:
            self.weapon_note = f"the file has no mesh node named {DEFAULT_WEAPON!r}: no weapon is checked (an unarmed unit)"
        self.weapon = self._part(weapon_name) if weapon_name and weapon_name not in NO_WEAPON and not weapon_missing else None

    def _part(self, name: str) -> dict:
        nodes = [n for n in self.nodes if "mesh" in n and n.get("name") == name]
        if not nodes:
            names = [n.get("name") for n in self.nodes if "mesh" in n]
            raise SystemExit(f"No mesh node named {name!r}; the mesh nodes are {names}")
        positions, joint_ids, weights, tris, offset = [], [], [], [], 0
        for node in nodes:
            for prim in self.doc["meshes"][node["mesh"]]["primitives"]:
                attr = prim["attributes"]
                p = read_accessor(self.doc, self.binary, attr["POSITION"])
                positions.append(p)
                if "JOINTS_0" in attr:
                    joint_ids.append(read_accessor(self.doc, self.binary, attr["JOINTS_0"]).astype(int))
                    weights.append(read_accessor(self.doc, self.binary, attr["WEIGHTS_0"]).astype(float))
                if "indices" in prim:
                    tri = read_accessor(self.doc, self.binary, prim["indices"]).astype(int).reshape(-1, 3) + offset
                else:
                    tri = np.arange(len(p)).reshape(-1, 3) + offset
                tris.append(tri)
                offset += len(p)
        positions = np.concatenate(positions)
        part = {"name": name, "positions": positions, "triangles": np.concatenate(tris)}
        if joint_ids:
            ids, wts = np.concatenate(joint_ids), np.concatenate(weights)
            part["joint_ids"] = ids
            part["weights"] = wts / np.maximum(wts.sum(axis=1, keepdims=True), 1e-9)
        part["homogeneous"] = np.concatenate([positions, np.ones((len(positions), 1))], axis=1)
        return part

    def pose_for(self, tracks: dict, t: float) -> dict:
        pose = {}
        for index, paths in tracks.items():
            if self.base[index] is None:
                continue
            tr, ro, sc = self.base[index]
            if "translation" in paths:
                tr = sample_track(*paths["translation"], t, False)
            if "rotation" in paths:
                ro = sample_track(*paths["rotation"], t, True)
            if "scale" in paths:
                sc = sample_track(*paths["scale"], t, False)
            pose[index] = (tr, ro, sc)
        return pose

    def joint_worlds(self, pose: dict) -> np.ndarray:
        local = []
        for index, node in enumerate(self.nodes):
            if self.base[index] is None:
                local.append(np.array(node["matrix"], float).reshape(4, 4).T)
            else:
                t, r, s = pose.get(index, self.base[index])
                local.append(local_matrix(t, r, s))
        cache: Dict[int, np.ndarray] = {}

        def resolve(i):
            if i not in cache:
                m = local[i]
                if i in self.parent:
                    m = resolve(self.parent[i]) @ m
                cache[i] = m
            return cache[i]

        return np.stack([resolve(j) for j in self.joints])

    def skin_mats(self, worlds: np.ndarray) -> np.ndarray:
        return np.einsum("kij,kjl->kil", worlds, self.inverse)

    @staticmethod
    def skin(part: dict, mats: np.ndarray) -> np.ndarray:
        out = np.zeros((len(part["positions"]), 3))
        for slot in range(4):
            m = mats[part["joint_ids"][:, slot]]
            out += part["weights"][:, slot : slot + 1] * np.einsum("nij,nj->ni", m, part["homogeneous"])[:, :3]
        return out

    def clips(self):
        for anim in self.doc["animations"]:
            tracks, end = {}, 0.0
            for channel in anim["channels"]:
                sampler = anim["samplers"][channel["sampler"]]
                times = read_accessor(self.doc, self.binary, sampler["input"]).ravel()
                values = read_accessor(self.doc, self.binary, sampler["output"])
                tracks.setdefault(channel["target"]["node"], {})[channel["target"]["path"]] = (times, values)
                end = max(end, float(times[-1]))
            yield anim["name"], tracks, end


def canonical_names(names: Sequence[str]) -> List[str]:
    """Each joint's canonical (Mixamo short) name, through lib/tripo_rig.py (the newer Tripo rig's `R_Hand` is `RightHand`); a rig that is
    neither of Tripo's keeps its names without a prefix."""

    from lib import tripo_rig

    try:
        rig = tripo_rig.RigNames(names)
    except tripo_rig.RigError:
        return [tripo_rig.short(name) for name in names]
    return [rig.canonical(name) for name in names]


def hand_joint_indices(names: Sequence[str]) -> List[int]:
    """Indices of palm joints (`...Hand`, not a finger such as `RightHandIndex1`)."""

    return [i for i, name in enumerate(canonical_names(names)) if re.search(r"hand$", name, re.IGNORECASE)]


def resolve_weapon_joint(names: Sequence[str], weapon_rest: np.ndarray, joint_rest: np.ndarray, wanted: str = "auto") -> int:
    """The joint the weapon follows. `auto` takes the hand joint with a weapon vertex closest to it."""

    if wanted != "auto":
        for i, (name, canonical) in enumerate(zip(names, canonical_names(names))):
            if name == wanted or name.split(":")[-1] == wanted or canonical == wanted:
                return i
        raise SystemExit(f"No joint named {wanted!r}; the hand joints are {[names[i] for i in hand_joint_indices(names)]}")
    hands = hand_joint_indices(names)
    if not hands:
        raise SystemExit("The rig has no joint whose name ends in Hand; pass --weapon-bone")
    distance = [float(np.linalg.norm(weapon_rest - joint_rest[i], axis=1).min()) for i in hands]
    return hands[int(np.argmin(distance))]


# ---------------------------------------------------------------------------------------------
# The check
# ---------------------------------------------------------------------------------------------


@dataclass
class _CheckContext:
    """What every clip of one `check` call shares: the rig, the body's rest edges and the weapon's points."""

    rig: "Rig"
    tri: np.ndarray
    edges: np.ndarray
    rest_len: np.ndarray
    keep: np.ndarray
    height: float
    ground: float
    joint: int
    all_points: np.ndarray  # (N, 4) every weapon point, homogeneous
    free_points: np.ndarray  # (M, 4) the weapon points outside the grip zone
    margin_share: float
    per_frame_ground: bool


def _penetration(ctx: _CheckContext, hand: np.ndarray, now: np.ndarray) -> Tuple[float, float, float]:
    """For one frame: the share of free weapon points inside the body, the share deeper than the margin, and the deepest depth (share of height)."""

    if not len(ctx.free_points):
        return 0.0, 0.0, 0.0
    world_free = (ctx.free_points @ hand.T)[:, :3]
    lo, hi = now.min(axis=0), now.max(axis=0)
    near = np.all((world_free >= lo) & (world_free <= hi), axis=1)
    inside = np.zeros(len(world_free), dtype=bool)
    if near.any():
        inside[near] = points_inside_mesh(world_free[near], now[ctx.tri])
    share = float(inside.mean())
    if not inside.any():
        return share, 0.0, 0.0
    depths = nearest_vertex_distance(world_free[inside], now) / ctx.height
    return share, float((depths > ctx.margin_share).sum()) / len(world_free), float(depths.max())


def _check_clip(ctx: _CheckContext, tracks: dict, end: float, count: int, tolerance: float, keep_series: bool) -> dict:
    """Pose the body at `count` times of one clip and measure stretch, the weapon in the body and the weapon below the ground."""

    rig, height = ctx.rig, ctx.height
    deep_series, in_series = [], []
    worst_stretch = {"stretched": 0.0, "squashed": 0.0, "frame": 0}
    growth = 0.0
    worst_in, worst_in_frame, deepest, deepest_frame, worst_ground = 0.0, 0, 0.0, 0, 0.0
    worst_deep, worst_deep_frame, lowest_body, worst_rest_ground = 0.0, 0, 0.0, 0.0
    for step in range(count):
        t = end * step / max(count - 1, 1)
        worlds = rig.joint_worlds(rig.pose_for(tracks, t))
        mats = rig.skin_mats(worlds)
        now = rig.skin(rig.body, mats)
        length = np.linalg.norm(now[ctx.edges[:, 0]] - now[ctx.edges[:, 1]], axis=1)
        ratio = length[ctx.keep] / ctx.rest_len[ctx.keep]
        stretched = float((ratio > STRETCH_LONG).mean())
        if stretched > worst_stretch["stretched"]:
            worst_stretch.update(stretched=stretched, squashed=float((ratio < STRETCH_SHORT).mean()), frame=step)
        growth = max(growth, float((length - ctx.rest_len).max() / height))
        # The weapon rides the hand joint rigidly.
        lowest_body = max(lowest_body, float((ctx.ground + GROUND_TOLERANCE_SHARE * height - now[:, 1].min()) / height))
        hand = mats[ctx.joint]
        if len(ctx.all_points):  # an unarmed unit has no weapon points: nothing to ground
            world_all = (ctx.all_points @ hand.T)[:, :3]
            frame_ground = float(now[:, 1].min()) - tolerance * height if ctx.per_frame_ground else ctx.ground
            worst_ground = max(worst_ground, float((world_all[:, 1] < frame_ground).mean()))
            worst_rest_ground = max(worst_rest_ground, float((world_all[:, 1] < ctx.ground).mean()))
        share, deep, depth = _penetration(ctx, hand, now)
        in_series.append(share)
        deep_series.append(deep)
        if share > worst_in:
            worst_in, worst_in_frame = share, step
        if depth > deepest:
            deepest, deepest_frame = depth, step
        if deep > worst_deep:
            worst_deep, worst_deep_frame = deep, step
    entry = {
        "seconds": round(end, 2),
        "stretched_pct": round(100 * worst_stretch["stretched"], 2),
        "squashed_pct": round(100 * worst_stretch["squashed"], 2),
        "worst_growth_pct_of_height": round(100 * growth, 1),
        "worst_stretch_sample": worst_stretch["frame"],
        "weapon_in_body_pct": round(100 * worst_in, 2),
        "weapon_in_body_worst_sample": worst_in_frame,
        "weapon_deep_in_body_pct": round(100 * worst_deep, 2),
        "weapon_deep_in_body_worst_sample": worst_deep_frame,
        "deepest_penetration_pct_of_height": round(100 * deepest, 2),
        "deepest_penetration_sample": deepest_frame,
        "weapon_below_ground_pct": round(100 * worst_ground, 2),
        "weapon_below_rest_ground_pct": round(100 * worst_rest_ground, 2),
        "body_lowest_below_rest_ground_pct_of_height": round(100 * max(lowest_body, 0.0), 1),
        **clip_verdict(worst_deep, worst_ground, 100 * worst_stretch["stretched"]),
    }
    if keep_series:
        entry["frames"] = count
        entry["weapon_deep_in_body_pct_by_frame"] = [round(100 * v, 2) for v in deep_series]
        entry["weapon_in_body_pct_by_frame"] = [round(100 * v, 2) for v in in_series]
    return entry


def check(path, body="tripo_part_0", weapon="tripo_part_1", weapon_bone="auto", samples=24, grip_radius=GRIP_RADIUS_SHARE, per_frame_ground=False, only: Optional[Sequence[str]] = None, ground_tolerance_by_clip: Optional[Dict[str, float]] = None, frame_rate: float = 24.0, margin_share: float = PENETRATION_MARGIN_SHARE) -> dict:
    rig = Rig(path, body, weapon)
    body_part, weapon_part = rig.body, rig.weapon
    rest_worlds = rig.joint_worlds({})
    rest_mats = rig.skin_mats(rest_worlds)
    rest_body = rig.skin(body_part, rest_mats)
    height = float(rest_body[:, 1].max() - rest_body[:, 1].min())
    ground = float(rest_body[:, 1].min()) - GROUND_TOLERANCE_SHARE * height
    tri = body_part["triangles"]
    edges = np.unique(np.sort(np.concatenate([tri[:, [0, 1]], tri[:, [1, 2]], tri[:, [2, 0]]]), axis=1), axis=0)
    rest_len = np.linalg.norm(rest_body[edges[:, 0]] - rest_body[edges[:, 1]], axis=1)
    keep = rest_len > 1e-6

    radius = grip_radius * height
    if weapon_part is None:
        # An unarmed unit: no weapon points, so the clip table holds the stretch numbers and a zero weapon.
        points, joint, free = np.zeros((0, 3)), 0, np.zeros(0, dtype=bool)
    else:
        weapon_rest = rig.skin(weapon_part, rest_mats) if "joint_ids" in weapon_part else weapon_part["positions"]
        pick = np.linspace(0, len(weapon_rest) - 1, min(MAX_WEAPON_POINTS, len(weapon_rest))).astype(int)
        points = weapon_rest[pick]
        joint_rest = rest_worlds[:, :3, 3]
        joint = resolve_weapon_joint(rig.joint_names, weapon_rest, joint_rest, weapon_bone)
        free = ~grip_zone_mask(points, joint_rest[joint], radius)
    free_points = np.concatenate([points[free], np.ones((int(free.sum()), 1))], axis=1)
    all_points = np.concatenate([points, np.ones((len(points), 1))], axis=1)

    ctx = _CheckContext(rig, tri, edges, rest_len, keep, height, ground, joint, all_points, free_points, margin_share, per_frame_ground)
    report = {}
    for name, tracks, end in rig.clips():
        if only is not None and name not in only:
            continue
        tolerance = (ground_tolerance_by_clip or {}).get(name, FRAME_GROUND_TOLERANCE_SHARE)
        # samples == "all": every frame of the clip at `frame_rate`, and the per-frame series is kept in the report
        count = int(round(end * frame_rate)) + 1 if samples == "all" else int(samples)
        report[name] = _check_clip(ctx, tracks, end, count, tolerance, keep_series=samples == "all")
    return {
        "file": "<bytes>" if isinstance(path, (bytes, bytearray)) else str(path),
        "body": rig.body_name,
        "weapon": None if weapon_part is None else weapon,
        "weapon_joint": None if weapon_part is None else rig.joint_names[joint],
        "notes": [note for note in (rig.body_note, rig.weapon_note) if note],
        "body_height": round(height, 4),
        "grip_radius": round(radius, 4),
        "grip_points_excluded": int((~free).sum()),
        "weapon_points": int(len(points)),
        "samples": samples,
        "ground": "per-frame" if per_frame_ground else "rest",
        "thresholds": {
            "max_in_body_share": MAX_IN_BODY_SHARE,
            "penetration_margin_share": PENETRATION_MARGIN_SHARE,
            "max_below_ground_share": MAX_BELOW_GROUND_SHARE,
            "max_stretched_pct": MAX_STRETCHED_PCT,
        },
        "clips": report,
    }


def print_table(result: dict) -> None:
    for note in result.get("notes", []):
        print(f"note: {note}")
    follows = f"weapon follows {result['weapon_joint']}" if result["weapon_joint"] else "no weapon"
    print(f"{result['file']}  {follows}  height {result['body_height']}  grip radius {result['grip_radius']}")
    print(f"{'clip':<34}{'stretch%':>9}{'in-body%':>9}{'thru%':>7}{'deep%H':>8}{'ground%':>8}  verdict")
    for name, c in result["clips"].items():
        label = name if len(name) <= 33 else name[:30] + "..."
        print(f"{label:<34}{c['stretched_pct']:>9.2f}{c['weapon_in_body_pct']:>9.2f}{c['weapon_deep_in_body_pct']:>7.2f}{c['deepest_penetration_pct_of_height']:>8.2f}{c['weapon_below_ground_pct']:>8.2f}  {c['verdict']}" + (f"  ({'; '.join(c['reasons'])})" if c["reasons"] else ""))


# `--attack`: exit code when no attack candidate passes, so the card's "before you leave Tripo" step can branch on it.
NO_ATTACK_EXIT = 3


def attack_line(result: dict, candidates: List[str]) -> tuple:
    """The `attack:` line of the card's "before you leave Tripo" step: which attack candidates pass, by the clip verdicts above, and
    whether a text-to-motion attack must be made before the Tripo tab is closed (the hobgoblin run, 2026-11-22, learnt only after leaving
    that `chop`, its one free candidate, fails the stretch). A candidate is a clip name or its first words."""

    clips = result["clips"]
    passed, failed, absent = [], [], []
    for wanted in candidates:
        names = [name for name in clips if name == wanted] or [name for name in clips if name.startswith(wanted)]
        if not names:
            absent.append(wanted)
        for name in names:
            (passed if clips[name]["verdict"] == "pass" else failed).append(name)
    notes = []
    if failed:
        notes.append("fail: " + ", ".join(f"{name} ({'; '.join(clips[name]['reasons'])})" for name in failed))
    if absent:
        notes.append("not in the file: " + ", ".join(absent) + " (apply the tile and export again)")
    if passed:
        return f"attack: pass {', '.join(passed)}" + (f". {'. '.join(notes)}" if notes else ""), True
    return ("attack: none passes. " + (". ".join(notes) + ". " if notes else "")
            + "Make one text-to-motion attack now, before you leave Tripo, export again and run this again"), False


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("glb", type=Path)
    parser.add_argument("--body", default=DEFAULT_BODY, help="the body's mesh node (default tripo_part_0, or the one skinned mesh of a plain export)")
    parser.add_argument("--weapon", default=DEFAULT_WEAPON, help="the weapon's mesh node, or none for an unarmed unit (default tripo_part_1, or none when the file has no such node)")
    parser.add_argument("--weapon-bone", default="auto")
    parser.add_argument("--samples", type=lambda v: v if v == "all" else int(v), default=24, help="sampled times per clip, or `all` for every frame at 24 fps with the per-frame series")
    parser.add_argument("--grip-radius", type=float, default=GRIP_RADIUS_SHARE, help="grip zone radius as a share of the body height")
    parser.add_argument("--ground-per-frame", action="store_true", help="below-ground test against the lowest body vertex of each frame (for clips where the body sinks)")
    parser.add_argument("--ground-tolerance", help="clip=share,... : own per-frame below-ground tolerance (share of the body height) for named clips, for example a death clip that lies on the ground")
    parser.add_argument("--json", type=Path, help="write the full report here")
    parser.add_argument("--fail-on-verdict", action="store_true", help="exit 1 when any clip fails")
    parser.add_argument("--attack", nargs="+", metavar="CLIP", help="the attack candidates (names or first words): print the `attack:` line and exit 3 when none passes")
    args = parser.parse_args(argv)
    result = check(args.glb, args.body, args.weapon, args.weapon_bone, args.samples, args.grip_radius, args.ground_per_frame, ground_tolerance_by_clip={k: float(v) for k, _, v in (item.rpartition("=") for item in args.ground_tolerance.split(","))} if args.ground_tolerance else None)
    print_table(result)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=1), encoding="utf-8", newline="\n")
    failed = [n for n, c in result["clips"].items() if c["verdict"] == "fail"]
    if args.attack:
        line, ok = attack_line(result, args.attack)
        print(line)
        if not ok:
            return NO_ATTACK_EXIT
    return 1 if args.fail_on_verdict and failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
