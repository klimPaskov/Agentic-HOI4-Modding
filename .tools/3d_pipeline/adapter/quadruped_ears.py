"""Find a quadruped's ears by rule and weight them to their own bones.

Pure numpy, no Blender: `quadruped_rig.author_rig` calls it inside Blender and the unit tests run it on synthetic meshes. Coordinates are the
working frame of `quadruped_layout.py`: +Z up, the animal facing -Y, its left side toward +X.

The quadruped rig's Head carried the ears, so a war elephant's spread ear stood upright like a fin on the lying body (two fresh reviews of
run 11). The rules:

1. Flap. A vertex ahead of the front hooves and above the belly is on a flap when the points `EAR_PROBE` of the height along its normal on
   both sides lie outside the mesh (generalised winding number under one half): a skull or a neck is thicker than that, an ear is not.
2. Ear. The connected pieces of flap that reach farther from the body's mid-plane than the torso does (`torso_half_width`, the 98th
   percentile over the torso's points) stand beside the head: on each side they and their rim (`close_rim`) are that side's ear. A horse's
   ears stand on top of the head, inside that width, and keep riding the Head bone.
3. Chain. The root is where the flap meets the head (its vertices joined to skin that is not flap or load), the hinge the root line's main
   direction, and the tip the mean of the ear's farthest tenth from the root. Two bones run root to middle and middle to tip, children of the
   Head, so an ear can swing about its root and curl at its middle.
4. Room. How far the ear may close back against the head and neck before its outer half (`ROOM_REACH`) enters the body: the
   largest turn about the hinge, in `EAR_CLOSE_STEP` steps, that leaves at most `EAR_INSIDE_SHARE` of those points inside the rest of the
   mesh (winding number over one half), less one step. The same the other way gives the room it may spread forward. The ear hangs from
   the bone in the middle of its root skin's weight down the neck (`assign_parents`).
5. Weights. Along the ear the two bones share linearly between their middles. The ear takes them whole from `EAR_ROOT_BLEND` of its length
   out from the root and blends into the body's own weights inside that, so the root bends where an ear bends. The skin a load rests on
   (any weight on the load's bone, quadruped_load.bind_load) keeps its weights, and the ear's rise from it over the load's ring of surface
   distance, so that skin never follows the ear (TRIPO-LOAD-SEAM).
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import numpy as np

from quadruped_layout import ear_name

EAR_PROBE = 0.04  # of the body's height: a flap is thinner than this (the war elephant's ears are about 0.02)
EAR_MIN_VERTICES = 12  # a flap piece smaller than this is a crease or a strap end, not an ear
EAR_ROOT_BLEND = 0.25  # share of the ear's length over which its root blends into the head's weights
EAR_CLOSE_STEP = 5.0  # degrees
EAR_CLOSE_MOST = 120.0
EAR_INSIDE_SHARE = 0.02  # share of the ear's outer points that may graze the body
ROOM_SAMPLES = 60  # outer ear points the room is measured on
# The room is measured on the ear's outer half: a few points by its root graze the neck at any turn (on the war elephant 2 of 60 points of
# its outer three quarters from 20 degrees on, none of its outer half before 70).
ROOM_REACH = 0.5
TORSO_PERCENTILE = 98.0
TIP_SHARE = 0.1
EAR_PARENT_ORDER = ("Pelvis", "Spine", "Chest", "Neck_01", "Neck_02", "Head")  # from the torso to the head
LOAD_BONE = "Load"  # quadruped_layout.LOAD_BONE
# The ear's weights rise from the skin the load rests on over this many of the load's rings (surface distance). Over one ring, about two
# edges of the war elephant's coarse mesh, its walk stretched 2.8% of the seam beside the neck and its retreat 9.1% (TRIPO-LOAD-SEAM, limit
# 2%); over three 0.9% and 1.6%, no more than without ear bones (offline on run 11's mesh).
EAR_LOAD_FADE_RINGS = 3
EAR_CARRY_BAND = 0.25  # the ear's farthest tenth from the root is its tip


def vertex_normals(points: np.ndarray, triangles: np.ndarray, canon: np.ndarray) -> np.ndarray:
    """Area-weighted vertex normals over welded vertices (split UV seams joined)."""

    welded = canon[triangles]
    face = np.cross(points[welded[:, 1]] - points[welded[:, 0]], points[welded[:, 2]] - points[welded[:, 0]])
    normals = np.zeros_like(points)
    for corner in range(3):
        np.add.at(normals, welded[:, corner], face)
    normals = normals[canon]
    return normals / np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-12)


def winding_numbers(points: np.ndarray, soup: np.ndarray) -> np.ndarray:
    """The generalised winding number of each point against a triangle soup (T, 3, 3), unsigned (about 1 inside, 0 outside)."""

    out = np.zeros(len(points))
    for index, point in enumerate(points):
        a, b, c = soup[:, 0] - point, soup[:, 1] - point, soup[:, 2] - point
        la, lb, lc = np.linalg.norm(a, axis=1), np.linalg.norm(b, axis=1), np.linalg.norm(c, axis=1)
        numerator = np.einsum("ij,ij->i", a, np.cross(b, c))
        denominator = la * lb * lc + np.einsum("ij,ij->i", a, b) * lc + np.einsum("ij,ij->i", b, c) * la + np.einsum("ij,ij->i", c, a) * lb
        out[index] = np.arctan2(numerator, denominator).sum() / (2.0 * math.pi)
    return np.abs(out)


def weld(points: np.ndarray, tolerance: float) -> np.ndarray:
    """Per vertex, the index of its first copy at the same place."""

    keys = np.round(points / max(tolerance, 1e-12)).astype(np.int64)
    _unique, first, inverse = np.unique(keys, axis=0, return_index=True, return_inverse=True)
    return first[inverse.ravel()]


def welded_edges(triangles: np.ndarray, canon: np.ndarray) -> np.ndarray:
    welded = canon[triangles]
    return np.unique(np.sort(np.concatenate([welded[:, [0, 1]], welded[:, [1, 2]], welded[:, [2, 0]]]), axis=1), axis=0)


def components(count: int, edges: np.ndarray, allowed: np.ndarray) -> np.ndarray:
    """Connected-component labels of the allowed vertices (-1 elsewhere)."""

    labels = np.where(allowed, np.arange(count), -1)
    usable = edges[allowed[edges[:, 0]] & allowed[edges[:, 1]]]
    while len(usable):
        low = np.minimum(labels[usable[:, 0]], labels[usable[:, 1]])
        before = labels.copy()
        np.minimum.at(labels, usable[:, 0], low)
        np.minimum.at(labels, usable[:, 1], low)
        labels[allowed] = labels[labels[allowed]]
        if np.array_equal(before, labels):
            break
    return labels


def close_rim(piece: np.ndarray, edges: np.ndarray, allowed: np.ndarray, passes: int = 2) -> np.ndarray:
    """Add the allowed vertices at least half of whose neighbours are in the piece: a flap's rim, whose normal points along the flap
    rather than through it, and its two faces join into one ear. The skull round the ear's root keeps most of its neighbours outside."""

    piece = piece.copy()
    degree = np.bincount(edges.ravel(), minlength=len(piece))
    for _ in range(passes):
        inside = np.bincount(edges[:, 0], weights=piece[edges[:, 1]], minlength=len(piece)) + np.bincount(
            edges[:, 1], weights=piece[edges[:, 0]], minlength=len(piece))
        grown = allowed & ~piece & (degree > 0) & (2 * inside >= degree)
        if not grown.any():
            break
        piece |= grown
    return piece


def torso_half_width(p: np.ndarray, landmarks: Dict[str, object], body: np.ndarray) -> float:
    cx = float(landmarks["centre_x"])
    torso = body & (p[:, 1] > float(landmarks["front_y"])) & (p[:, 1] < float(landmarks["rear_y"])) & (
        p[:, 2] > float(landmarks["belly_z"])) & (p[:, 2] < float(landmarks["back_z"]))
    return float(np.percentile(np.abs(p[torso, 0] - cx), TORSO_PERCENTILE)) if torso.any() else 0.5 * float(landmarks["width"])


def rotate_about(points: np.ndarray, origin: np.ndarray, axis: np.ndarray, degrees: float) -> np.ndarray:
    a = axis / np.linalg.norm(axis)
    t = math.radians(degrees)
    k = np.array([[0.0, -a[2], a[1]], [a[2], 0.0, -a[0]], [-a[1], a[0], 0.0]])
    r = np.eye(3) + math.sin(t) * k + (1 - math.cos(t)) * k @ k
    return (points - origin) @ r.T + origin


def ear_room(ear: np.ndarray, soup: np.ndarray, root: np.ndarray, hinge: np.ndarray, direction: float) -> float:
    """The largest turn (degrees, positive) about the hinge in `direction` that keeps the ear's outer points out of the body (winding number
    against the rest of the mesh under one half for all but `EAR_INSIDE_SHARE` of them), less a step. Points already inside at rest (an
    ear that touches a strap or the shoulder) do not count."""

    sample = ear[np.linspace(0, len(ear) - 1, min(len(ear), ROOM_SAMPLES)).round().astype(int)] if len(ear) else ear
    free = winding_numbers(sample, soup) <= 0.5
    sample = sample[free]
    reached = 0.0
    angle = EAR_CLOSE_STEP
    while len(sample) and angle <= EAR_CLOSE_MOST + 1e-9:
        moved = rotate_about(sample, root, hinge, direction * angle)
        if (winding_numbers(moved, soup) > 0.5).mean() > EAR_INSIDE_SHARE:
            break
        reached = angle
        angle += EAR_CLOSE_STEP
    return max(0.0, reached - EAR_CLOSE_STEP)


def _ear_chain(p: np.ndarray, ear: np.ndarray, attach: np.ndarray, cx: float, sign: float) -> Dict[str, object]:
    """Root (the attachment's mean, or the ear's points nearest the mid-plane when it touches no skin), tip, hinge and closing sense."""

    if not attach.any():
        lateral = np.abs(p[:, 0] - cx)
        attach = ear & (lateral <= np.quantile(lateral[ear], TIP_SHARE))
    root = p[attach].mean(axis=0)
    distance = np.linalg.norm(p[ear] - root, axis=1)
    far = p[ear][distance >= np.quantile(distance, 1.0 - TIP_SHARE)]
    tip = far.mean(axis=0)
    centred = p[ear] - p[ear].mean(axis=0)
    normal = np.linalg.svd(centred, full_matrices=False)[2][2]
    line = p[attach] - p[attach].mean(axis=0) if attach.sum() >= 3 else None
    hinge = np.linalg.svd(line, full_matrices=False)[2][0] if line is not None else np.cross(normal, tip - root)
    along = (tip - root) / max(float(np.linalg.norm(tip - root)), 1e-12)
    hinge = hinge - (hinge @ along) * along  # the hinge crosses the ear's length
    hinge = hinge / max(float(np.linalg.norm(hinge)), 1e-12)
    if hinge[2] < 0:
        hinge = -hinge
    # a turn that carries the tip backward (+Y) closes the ear against the head and neck
    close = 1.0 if float(np.cross(hinge, tip - root)[1]) > 0 else -1.0
    return {"root": root, "tip": tip, "hinge": hinge, "close_sign": close, "length": float(np.linalg.norm(tip - root)), "side_sign": sign}


def detect_ears(points: np.ndarray, triangles: np.ndarray, landmarks: Dict[str, object],
                exclude: Optional[np.ndarray] = None) -> Tuple[Dict[str, Dict[str, object]], Dict[str, np.ndarray]]:
    """The ears beside the head: per side ("Left", "Right") the chain (`root`, `middle`, `tip`, `hinge`, `close_sign`, `close_room`,
    `spread_room`, `length`, in the model's own coordinates) and the vertex mask. Empty when the model has no such ear."""

    ground = float(landmarks["ground_offset"])
    height = float(landmarks["height"])
    cx = float(landmarks["centre_x"])
    p = np.asarray(points, float) - np.array([0.0, 0.0, ground])
    body = np.ones(len(p), bool) if exclude is None else ~np.asarray(exclude, bool)
    canon = weld(p, 1e-6 * height)
    edges = welded_edges(np.asarray(triangles, int), canon)
    candidates = np.flatnonzero(body & (p[:, 1] < float(landmarks["front_y"])) & (p[:, 2] > float(landmarks["belly_z"])) & (canon == np.arange(len(p))))
    if not len(candidates):
        return {}, {}
    normals = vertex_normals(p, np.asarray(triangles, int), canon)
    soup = p[np.asarray(triangles, int)]
    probe = EAR_PROBE * height
    flap = np.zeros(len(p), bool)
    flap[candidates] = (winding_numbers(p[candidates] - probe * normals[candidates], soup) < 0.5) & (
        winding_numbers(p[candidates] + probe * normals[candidates], soup) < 0.5)
    labels = components(len(p), edges, flap)
    reach = torso_half_width(p, landmarks, body)
    ears: Dict[str, Dict[str, object]] = {}
    masks: Dict[str, np.ndarray] = {}
    region = np.zeros(len(p), bool)
    region[candidates] = True
    for side, sign in (("Left", 1.0), ("Right", -1.0)):
        best = np.zeros(len(p), bool)
        for label in np.unique(labels[labels >= 0]):
            piece = labels == label
            if piece.sum() >= EAR_MIN_VERTICES and float(((p[piece, 0] - cx) * sign).max()) > reach and float(np.median((p[piece, 0] - cx) * sign)) > 0:
                best |= piece
        if best.sum() < EAR_MIN_VERTICES:
            continue
        best = close_rim(best, edges, region)
        ear = best[canon]  # every copy of a welded vertex
        touching = edges[best[edges[:, 0]] ^ best[edges[:, 1]]]
        joined = np.zeros(len(p), bool)
        for a, b in touching:
            inner, outer = (a, b) if best[a] else (b, a)
            if body[outer]:
                joined[inner] = True
        chain = _ear_chain(p, best, joined, cx, sign)
        rest_of_body = soup[~ear[np.asarray(triangles, int)].any(axis=1)]
        outer = p[best][np.linalg.norm(p[best] - chain["root"], axis=1) > ROOM_REACH * chain["length"]]
        chain["close_room"] = ear_room(outer, rest_of_body, chain["root"], chain["hinge"], chain["close_sign"])
        chain["spread_room"] = ear_room(outer, rest_of_body, chain["root"], chain["hinge"], -chain["close_sign"])
        chain["middle"] = (chain["root"] + chain["tip"]) / 2
        chain["vertices"] = int(ear.sum())
        lift = np.array([0.0, 0.0, ground])
        ears[side] = {key: (value + lift if key in ("root", "middle", "tip") else value) for key, value in chain.items()}
        masks[side] = ear
    return ears, masks


def surface_distance(positions: np.ndarray, edges: np.ndarray, seeds: np.ndarray, limit: float) -> np.ndarray:
    """Shortest distance along mesh edges from any seed vertex (0 at a seed), up to `limit` (beyond it: inf)."""

    length = np.linalg.norm(positions[edges[:, 0]] - positions[edges[:, 1]], axis=1)
    distance = np.where(seeds, 0.0, np.inf)
    a = np.concatenate([edges[:, 0], edges[:, 1]])
    b = np.concatenate([edges[:, 1], edges[:, 0]])
    weight = np.concatenate([length, length])
    while True:
        better = np.full(len(distance), np.inf)
        np.minimum.at(better, b, distance[a] + weight)
        updated = np.minimum(distance, np.where(better <= limit, better, np.inf))
        if np.array_equal(updated, distance):
            return distance
        distance = updated


def _root_zone(points: np.ndarray, mask: np.ndarray, ear: Dict[str, object]) -> Tuple[np.ndarray, np.ndarray]:
    """The share of the ear's length out from its root of every vertex (`s`), and the ear's vertices within EAR_ROOT_BLEND of it."""

    root, tip = np.asarray(ear["root"], float), np.asarray(ear["tip"], float)
    length = max(float(np.linalg.norm(tip - root)), 1e-12)
    s = ((points - root) @ ((tip - root) / length)) / length
    return s, mask & (s < EAR_ROOT_BLEND)


def assign_parents(points: np.ndarray, landmarks: Dict[str, object], ears: Dict[str, Dict[str, object]], masks: Dict[str, np.ndarray]) -> None:
    """Hang each ear (`parent` in its chain) from the bone in the middle of its root skin's weight down the neck: the skin weights of the rig
    without ears, summed per bone over the ear's root zone (the load's bone left out), taken in EAR_PARENT_ORDER from the torso to the head,
    and the bone where the running sum passes half. A war elephant's ear set far back grows from the neck and shoulder skin. Hung from the
    Head there it stretched its root whenever the head turned against the neck (offline on run 11's mesh: 80 edges changed by 1.3 times or
    more in the walk), and hung from the bone its root follows most (the Head, 36% of a root that is 64% neck and shoulder) it turned with
    the head's whole raise and toss in the retreat while its root did not: two fresh reviews of run 13 saw a red crease where the ear meets
    the head. From the middle bone (the second neck bone) 2 edges, against 56 (offline on run 13's mesh)."""

    import quadruped_layout as ql

    plain = {key: value for key, value in landmarks.items() if key != "ears"}
    layout = ql.build_layout(plain)
    names = layout.names()
    indices, weights = ql.skin_weights(points, layout)
    for side, mask in masks.items():
        _s, zone = _root_zone(points, mask, ears[side])
        totals = {name: 0.0 for name in EAR_PARENT_ORDER}
        for row in np.flatnonzero(zone if zone.any() else mask):
            for slot in range(indices.shape[1]):
                name = names[int(indices[row, slot])]
                if name in totals:
                    totals[name] += float(weights[row, slot])
        ears[side]["parent"] = median_bone(totals)


def median_bone(totals: Dict[str, float]) -> str:
    """The bone in EAR_PARENT_ORDER where the running sum of `totals` first reaches half of their sum (the Head when they are empty)."""

    whole = sum(totals.values())
    running = 0.0
    for name in EAR_PARENT_ORDER:
        running += totals.get(name, 0.0)
        if whole > 0 and running >= 0.5 * whole:
            return name
    return "Head"


def _mix(row_i: np.ndarray, row_w: np.ndarray, extra: Dict[int, float], keep: float, slots: int) -> Tuple[List[int], List[float]]:
    dense: Dict[int, float] = {}
    for bone, weight in zip(row_i, row_w):
        if weight > 0:
            dense[int(bone)] = dense.get(int(bone), 0.0) + keep * float(weight)
    for bone, weight in extra.items():
        dense[bone] = dense.get(bone, 0.0) + weight
    kept = sorted(((k, v) for k, v in dense.items() if v > 0), key=lambda item: -item[1])[:slots]
    total = sum(value for _, value in kept) or 1.0
    return [item[0] for item in kept] + [kept[0][0]] * (slots - len(kept)), [item[1] / total for item in kept] + [0.0] * (slots - len(kept))


def ear_weights(points: np.ndarray, triangles: np.ndarray, layout, masks: Dict[str, np.ndarray], indices: np.ndarray, weights: np.ndarray,
                ring: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
    """Bind each ear (`indices`, `weights` as `quadruped_layout.skin_weights` returns them, rewritten).

    The ear moves whole with the bone it hangs from: its skin takes that bone alone, and the skin round it blends from that bone back to
    its own weights over EAR_ROOT_BLEND of the ear's length (surface distance), so a mixed root never shears inside the ear. On top, the
    ear's two bones take the ear from its root out (`EAR_ROOT_BLEND` of its length), sharing linearly between their middles. Skin with
    weight on the load's bone keeps its weights, and the ear's rise from it over `ring` of surface distance. Run it after
    `quadruped_load.bind_load`."""

    names = layout.names()
    ears = layout.landmarks.get("ears") or {}
    out_i, out_w = indices.copy(), weights.copy()
    slots = indices.shape[1]
    points = np.asarray(points, float)
    height = float(np.ptp(points[:, 2])) or 1.0
    canon = weld(points, 1e-6 * height)
    edges = welded_edges(np.asarray(triangles, int), canon)
    load_fade = np.ones(len(points))
    if LOAD_BONE in names and ring > 0:
        held = np.zeros(len(points), bool)
        held[canon[((indices == names.index(LOAD_BONE)) & (weights > 1e-3)).any(axis=1)]] = True
        fade = EAR_LOAD_FADE_RINGS * ring
        near = surface_distance(points, edges, held, fade)[canon]
        x = np.clip(np.where(np.isfinite(near), near / fade, 1.0), 0.0, 1.0)
        load_fade = x * x * (3 - 2 * x)
    for side, mask in masks.items():
        chain = ears.get(side)
        if not chain or ear_name(side, 1) not in names:
            continue
        s, _zone = _root_zone(points, mask, chain)
        band = max(EAR_CARRY_BAND * float(chain["length"]), 1e-9)
        seeds = np.zeros(len(points), bool)
        seeds[canon[mask]] = True
        distance = surface_distance(points, edges, seeds, band)[canon]
        x = np.clip(np.where(np.isfinite(distance), distance / band, 1.0), 0.0, 1.0)
        carry = (1.0 - x * x * (3 - 2 * x)) * load_fade
        alpha = np.clip(s / EAR_ROOT_BLEND, 0.0, 1.0)
        alpha = np.where(mask, alpha * alpha * (3 - 2 * alpha), 0.0) * load_fade
        outer = np.clip((s - 0.25) / 0.5, 0.0, 1.0)
        parent = names.index(str(chain.get("parent", "Head")))
        first, second = names.index(ear_name(side, 1)), names.index(ear_name(side, 2))
        for row in np.flatnonzero(carry > 0):
            held = float(carry[row]) * (1.0 - float(alpha[row]))
            extra = {parent: held, first: float(alpha[row] * (1 - outer[row])), second: float(alpha[row] * outer[row])}
            out_i[row], out_w[row] = _mix(out_i[row], out_w[row], extra, 1.0 - float(carry[row]), slots)
    return out_i, out_w
