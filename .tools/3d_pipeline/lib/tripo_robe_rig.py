"""Place a humanoid skeleton again from the mesh, for a robed figure whose legs the robe hides and whose rig Tripo misplaced.

Tripo's humanoid auto-rig looks for legs. Under a floor-length robe it finds none: on the Haiku mage Elzon (2026-11-23, TRIPO-RIG-ARMS
failed) it put the hips at 0.90 of the height, the feet at mid-chest, the toes at 0.62 with the robe's whole skirt bound to them, and the
left arm on nothing. A paid re-rig repeats the placement. This module places the joints again from measured landmarks and fixed human
proportions, weights the skin again by rule, and keeps every joint's name, parent and rest rotation, so the clips still fit
(`lib/clip_transfer.py` then moves the export's own clips onto the new joints, `tripo/robe_rig.py`).

The body frame: up is +y, the left is the side the rig's Left thigh joint is on (the names are kept, so a clip moves the same side), ahead
is from the rig's heels to its toes. Heights are shares of the mesh's own height from its lowest point.

1. Neck: from the top down, the first band whose cross-section (width times depth) falls under `NECK_DROP` of the head's widest
   and then grows again, above `NECK_LOW_SHARE` of the height (`find_neck`).
2. Hips: `HIP_SHARE` of the neck's height (people: the hip joint at 0.53 of the stature, the middle of the neck at 0.88). Hidden legs
   cannot be measured, so the leg joints follow from the hips by proportion: the hip joints `HIP_HALF_SHARE` of the neck's height either
   side, the ankles at `ANKLE_SHARE`, the knees at `KNEE_SHARE` of the way from the ankles to the hips, the toes `TOE_AHEAD_SHARE`
   ahead of the ankles.
3. Shoulders: `SHOULDER_DROP_SHARE` of the hips-to-neck span below the neck, at `SHOULDER_WIDTH_SHARE` of the body's half width on that
   side at that height. The clavicle joints sit between the shoulders and the mid-line.
4. Arms: the hand's tip is the mesh's farthest point on each side between the knees and the shoulders, so the arms must stand out from
   the robe (Tripo's A pose). The elbow and the wrist sit on the straight shoulder-to-tip run at `ELBOW_SHARE` and `WRIST_SHARE` of
   it (as `lib/tripo_arm_seat.py`). The arm's skin is found by the gap that parts the sleeve from the robe (`body_edge`): in each band
   where such a gap shows, the body ends at the gap, and above the last such band the body keeps that width. Every connected piece
   beside the body that reaches down into the gapped bands and lies along the run is arm (the hand, the sleeve and a cuff
   are often separate pieces). Where the sleeve
   meets the body it blends in over `ARM_BLEND_SHARE` of the height. An arm that touches the robe all the way down is refused.
5. Spine, neck and head: the spine joints are spread between the hips and the base of the neck at `SPINE_SHARES`, on the middle of the
   body's column at each height. The neck joint is at the base of the neck, the head joint `HEAD_JOINT_SHARE` of the way from the neck
   up to the head's widest band, and the head's end straight above it at the top (a hood's tip may curl away).
6. Weights: the body column takes the spine joints by height (linear between the middles of the bones). Below the hips the robe takes
   the hips and at most `ROBE_LEG_SHARE` of the leg on its side (thigh, then shin, then foot at the hem), growing from the hips to
   the hem and split between the legs across the whole hem: the robe moves partly with a step and does not stretch like a trouser leg.
   The arm takes the upper arm, forearm and hand by its run (`sleeve_weights`): a sleeve hanging far from the run blends at the elbow
   and the wrist over a width that grows with its distance, and only the hand near the run takes the hand's joint. The top of the arm
   blends into the clavicle. Fingers, the toes' ends and other joints keep their offsets to their parents and carry no skin.

Measured on Elzon (2026-11-23, Tripo's own clips moved onto the new joints by `lib/clip_transfer.py`): `tripo/rig_check.py` passes
(it failed on Tripo's rig), and `tripo/clip_check.py` passes all nine clips with 1.4 to 4.9% of edges stretched (Tripo's rig: six
of nine failed, 2.4 to 9.0%). A share of 1.0 of the legs pulled the hem with the feet and stretched it (six clips failed), and a blend
at the elbow and the wrist that widened too little stretched the hanging sleeves (four clips failed at a growth of 0.5, none from 1.0).

It works on a single skinned primitive, Mixamo joint names, and node rest transforms equal to the bind pose (Tripo's exports are).
Maths only: numpy, and scipy for the connected pieces.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

from .tripo_arm_seat import (BLEND_SHARE, ELBOW_SHARE, WRIST_SHARE, SeatError, body_axes, load_rig, put, read_glb, segment_distance,
                             shift_translation_keys, welded_pieces, worlds, write_glb)

BAND_SHARE = 0.02
NECK_LOW_SHARE = 0.55
NECK_DROP = 0.8  # the neck's cross-section is at most this share of the head's widest
HIP_SHARE = 0.6
HIP_HALF_SHARE = 0.055
ANKLE_SHARE = 0.05
KNEE_SHARE = 0.48
TOE_AHEAD_SHARE = 0.08
TOE_END_SHARE = 0.05
SHOULDER_DROP_SHARE = 0.18
SHOULDER_WIDTH_SHARE = 0.7
CLAVICLE_SHARE = 0.3
SPINE_SHARES = (0.12, 0.4, 0.68)
HEAD_JOINT_SHARE = 0.3
ARM_OUT_SHARE = 1.15  # the hand's tip must stand this far beyond the robe's half width at the knees
ARM_BLEND_SHARE = 0.06  # of the height
SLEEVE_BLEND_GROWTH = 1.5  # the elbow's and the wrist's blend widens by this share of a point's distance from the arm's run
HAND_INNER, HAND_OUTER = 0.12, 0.2  # shares of the run: within the first from the run the hand's joint takes the skin, beyond the second never
GAP_SHARE = 0.01  # of the height
EDGE_OUTLIER = 1.3
ARM_PIECE_SHARE = 0.2  # a piece beside the body is arm when its middle lies this far along the run or farther
ARM_PIECE_DISTANCE = 0.5  # and within this share of the run from it
ARM_ROOT_BLEND = 0.12  # the first share of the arm's run blends into the clavicle
ROBE_LEG_SHARE = 0.5
KNEE_BLEND = 0.1  # of the neck's height
FOOT_RISE = 3.0  # the robe below this many ankle heights takes the feet
CLAVICLE_WEIGHT = 0.5
MIN_POINTS = 20


class Frame:
    """Body coordinates: across (+ toward the rig's Left side), up from the lowest point, ahead."""

    def __init__(self, positions: np.ndarray, heads: Dict[str, np.ndarray]) -> None:
        across, ahead = body_axes(heads)  # across points to the Right thigh
        self.left, self.ahead, self.up = -across, ahead, np.array([0.0, 1.0, 0.0])
        self.ground = float(positions[:, 1].min())
        self.height = float(positions[:, 1].max()) - self.ground
        low = positions[positions[:, 1] < self.ground + 0.1 * self.height]
        self.origin = np.array([low[:, 0].mean(), self.ground, low[:, 2].mean()])

    def local(self, points: np.ndarray) -> np.ndarray:
        d = np.asarray(points, float) - self.origin
        return np.stack([d @ self.left, d @ self.up, d @ self.ahead], axis=-1) / self.height

    def world(self, lat: float, up: float, ahead: float) -> np.ndarray:
        return self.origin + self.height * (lat * self.left + up * self.up + ahead * self.ahead)


def bands(local: np.ndarray) -> List[Tuple[float, np.ndarray]]:
    out = []
    for low in np.arange(0.0, 1.0, BAND_SHARE):
        mask = (local[:, 1] >= low) & (local[:, 1] < low + BAND_SHARE)
        out.append((float(low + BAND_SHARE / 2), mask))
    return out


def find_neck(local: np.ndarray) -> Tuple[float, float]:
    """(neck height, head's widest height) by rule 1: from the top down, the head's cross-section grows to its widest band, and the neck
    is the first band below it where the cross-section falls under `NECK_DROP` of that and then grows again."""

    rows = [(y, float(np.ptp(local[m, 0]) * np.ptp(local[m, 2]))) for y, m in bands(local) if m.sum() >= 3]
    rows = [r for r in rows if r[0] >= NECK_LOW_SHARE][::-1]  # from the top down
    widest = rows[0]
    for k, (y, area) in enumerate(rows[1:-1], start=1):
        if area > widest[1]:
            widest = (y, area)
        elif area <= NECK_DROP * widest[1] and rows[k + 1][1] >= area:
            return y, widest[0]
    raise SeatError(f"no neck between the head and {NECK_LOW_SHARE:.0%} of the height")


def column(local: np.ndarray, y: float, half: float) -> np.ndarray:
    """The middle of the body's column at height `y`: the mean of the points near the mid-line there."""

    m = (np.abs(local[:, 1] - y) < BAND_SHARE) & (np.abs(local[:, 0]) < half)
    if m.sum() < 3:
        return np.array([0.0, y, 0.0])
    return np.array([0.0, y, float(np.median(local[m, 2]))])


def half_width(local: np.ndarray, y: float, sign: float) -> float:
    m = (np.abs(local[:, 1] - y) < BAND_SHARE) & (local[:, 0] * sign > 0)
    if m.sum() < 3:
        raise SeatError(f"no body at {y:.2f} of the height")
    return float(np.percentile(np.abs(local[m, 0]), 98))


def body_edge(local: np.ndarray, sign: float, low: float, high: float, inner: float) -> Dict[float, float]:
    """{band height: the body's half width on one side} for every band between `low` and `high` where a gap of at least one
    `GAP_SHARE` bin parts the body from what hangs beside it (the sleeve). The gap is looked for beyond `inner` (the neck's half width)."""

    out = {}
    for y, mask in bands(local):
        if not low <= y <= high:
            continue
        reach = local[mask & (local[:, 0] * sign > 0), 0] * sign
        if len(reach) < MIN_POINTS:
            continue
        counts, edges = np.histogram(reach, bins=np.arange(0.0, reach.max() + GAP_SHARE, GAP_SHARE))
        empty = [k for k in range(len(counts)) if counts[k] == 0 and edges[k] >= inner and counts[k + 1:].sum() > 0]
        if empty:
            out[y] = float(edges[empty[0]])
    if out:  # a gap far outside the others parts fingers or a cuff, not the body from the sleeve
        middle = float(np.median(list(out.values())))
        out = {y: w for y, w in out.items() if w <= EDGE_OUTLIER * middle}
    return out


def place_arm(local: np.ndarray, triangles: np.ndarray, sign: float, shoulder: np.ndarray, knee_y: float, neck_y: float, neck_half: float) -> dict:
    """Rule 4 for one side: the hand's tip, the arm's skin, the elbow and the wrist (body coordinates)."""

    side = local[:, 0] * sign > 0
    zone = side & (local[:, 1] > knee_y) & (local[:, 1] < shoulder[1])
    if zone.sum() < MIN_POINTS:
        raise SeatError("no arm beside the body")
    reach = np.abs(local[:, 0])
    tip_cut = np.percentile(reach[zone], 99.7)
    tips = zone & (reach >= tip_cut)
    tip = local[tips].mean(axis=0)
    robe = half_width(local, knee_y, sign)
    if abs(tip[0]) < ARM_OUT_SHARE * robe:
        raise SeatError(f"the arm does not stand out from the robe (tip {abs(tip[0]):.3f}, robe {robe:.3f}): rig an A pose")
    edge = body_edge(local, sign, knee_y, shoulder[1], neck_half)
    if len(edge) < 2:
        raise SeatError("no gap between the arm and the robe: the arms must hang apart from the body (an A pose)")
    heights = np.array(sorted(edge))
    widths = np.array([edge[h] for h in heights])
    body = np.interp(local[:, 1], heights, widths)
    beside = side & (local[:, 1] >= heights[0] - BAND_SHARE) & (local[:, 1] < neck_y) & (reach > body)
    axis = tip - shoulder
    length = float(np.linalg.norm(axis))
    share = (local - shoulder) @ axis / max(length * length, 1e-12)
    dist = segment_distance(local, shoulder, tip)
    # Every piece beside the body that lies along the arm is the arm: the hand, the sleeve and its cuff are often separate pieces.
    pieces = welded_pieces(local, triangles, beside)
    core = np.zeros(len(local), bool)
    for label in np.unique(pieces[beside]):
        piece = pieces == label
        hangs = (local[piece, 1] <= heights[-1]).any()  # a sliver of the body above the last gap is not the arm
        if hangs and np.median(share[piece]) > ARM_PIECE_SHARE and np.median(dist[piece]) < ARM_PIECE_DISTANCE * length:
            core |= piece
    if not core[tips].any():
        raise SeatError("the hand's tip is not on the arm")
    above = local[:, 1] > heights[-1]  # where the sleeve meets the body: blend over ARM_BLEND_SHARE of the height
    blend = np.where(core, np.where(above, np.clip((reach - body) / ARM_BLEND_SHARE, 0.0, 1.0), 1.0), 0.0)

    # The elbow and the wrist lie on the straight run: an A pose holds the arm straight, and a sleeve hanging below the arm would pull
    # a mean of the skin down.
    return {"tip": tip, "share": share, "offset": dist / max(length, 1e-12), "blend": blend, "core": core, "elbow": shoulder + ELBOW_SHARE * axis, "wrist": shoulder + WRIST_SHARE * axis,
            "length": length, "gap_bands": len(edge), "body_half_width": round(float(np.median(widths)), 4)}


def place(local: np.ndarray, triangles: np.ndarray) -> dict:
    """Every placed joint in body coordinates (rules 1 to 5), with the arms' measures for the weights."""

    neck_y, head_y = find_neck(local)
    hips_y = HIP_SHARE * neck_y
    shoulder_y = neck_y - SHOULDER_DROP_SHARE * (neck_y - hips_y)
    ankle_y = ANKLE_SHARE * neck_y
    knee_y = ankle_y + KNEE_SHARE * (hips_y - ankle_y)
    neck_half = half_width(local, neck_y, 1.0)
    hips = column(local, hips_y, 2 * neck_half)
    joints = {"Hips": hips}
    base_y = (shoulder_y + neck_y) / 2
    for i, share in enumerate(SPINE_SHARES):
        joints[f"spine{i}"] = column(local, hips_y + share * (base_y - hips_y), 2 * neck_half)
    joints["Neck"] = column(local, base_y, 2 * neck_half)
    joints["Head"] = column(local, neck_y + HEAD_JOINT_SHARE * (head_y - neck_y), 2 * neck_half)
    joints["HeadTop_End"] = joints["Head"] * [1, 0, 1] + [0, 1.0, 0]  # straight above: a hood's tip may curl away
    arms = {}
    for side, sign in (("Left", 1.0), ("Right", -1.0)):
        chest = column(local, shoulder_y, 2 * neck_half)
        shoulder = np.array([sign * SHOULDER_WIDTH_SHARE * half_width(local, shoulder_y, sign), shoulder_y, chest[2]])
        joints[f"{side}Shoulder"] = np.array([sign * CLAVICLE_SHARE * abs(shoulder[0]), (shoulder_y + base_y) / 2, chest[2]])
        joints[f"{side}Arm"] = shoulder
        arm = place_arm(local, triangles, sign, shoulder, knee_y, neck_y, neck_half)
        arms[side] = arm
        joints[f"{side}ForeArm"], joints[f"{side}Hand"] = arm["elbow"], arm["wrist"]
        lat = sign * HIP_HALF_SHARE * neck_y
        joints[f"{side}UpLeg"] = np.array([lat, hips_y - 0.02 * neck_y, hips[2]])
        joints[f"{side}Leg"] = np.array([lat, knee_y, hips[2] + 0.01 * neck_y])
        joints[f"{side}Foot"] = np.array([lat, ankle_y, hips[2]])
        joints[f"{side}ToeBase"] = np.array([lat, 0.3 * ankle_y, hips[2] + TOE_AHEAD_SHARE * neck_y])
        joints[f"{side}Toe_End"] = joints[f"{side}ToeBase"] + [0, 0, TOE_END_SHARE * neck_y]
    return {"joints": joints, "arms": arms, "heights": {"neck": neck_y, "head": head_y, "hips": hips_y, "shoulder": shoulder_y,
                                                        "knee": knee_y, "ankle": ankle_y, "neck_base": base_y}}


def sleeve_weights(share: float, offset: float) -> Dict[str, float]:
    """The arm's weights at `share` of its run and `offset` (distance from the run over its length): upper arm, forearm, hand. A hanging
    sleeve lies far from the run, where a joint's turn moves it most, so its blends at the elbow and the wrist widen with the offset, and
    only the hand itself, near the run, takes the hand's joint (on Elzon, 2026-11-23, a sleeve weighted to the hand stretched in every
    clip)."""

    half = max(BLEND_SHARE, SLEEVE_BLEND_GROWTH * offset)

    def ramp(x: float, at: float) -> float:
        return float(np.clip((x - (at - half)) / (2 * half), 0.0, 1.0))

    hand = float(np.clip((HAND_OUTER - offset) / (HAND_OUTER - HAND_INNER), 0.0, 1.0))
    elbow, wrist = ramp(share, ELBOW_SHARE), ramp(share, WRIST_SHARE) * hand
    out = {"Arm": 1.0 - elbow, "ForeArm": elbow * (1.0 - wrist), "Hand": elbow * wrist}
    return {k: v for k, v in out.items() if v > 1e-6}


def spine_names(names: Sequence[str], parent_name: Dict[str, str]) -> List[str]:
    """The joints from the neck's parent down to the hips' child, hips first (Mixamo: Spine, Spine1, Spine2)."""

    chain, name = [], parent_name.get("Neck")
    while name and name != "Hips":
        chain.append(name)
        name = parent_name.get(name)
    if name != "Hips" or not chain:
        raise SeatError("the rig has no spine from the hips to the neck")
    return chain[::-1]


def spine_weights(y: np.ndarray, stations: Sequence[Tuple[str, float]]) -> List[Dict[str, float]]:
    """Each height's weights over the trunk joints: linear between the middles of the bones (a bone runs from its joint to the next)."""

    middles = [(name, (y0 + stations[i + 1][1]) / 2 if i + 1 < len(stations) else y0) for i, (name, y0) in enumerate(stations)]
    out = []
    for h in y:
        if h <= middles[0][1]:
            out.append({middles[0][0]: 1.0})
            continue
        if h >= middles[-1][1]:
            out.append({middles[-1][0]: 1.0})
            continue
        for (a, ya), (b, yb) in zip(middles, middles[1:]):
            if ya <= h <= yb:
                t = (h - ya) / max(yb - ya, 1e-12)
                out.append({a: 1 - t, b: t})
                break
    return out


def skin(local: np.ndarray, placed: dict, spine: Sequence[str]) -> List[Dict[str, float]]:
    """Rule 6: each vertex's joint weights."""

    joints, heights = placed["joints"], placed["heights"]
    stations = [("Hips", joints["Hips"][1])] + [(name, joints[f"spine{i}"][1]) for i, name in enumerate(spine)]
    stations += [("Neck", joints["Neck"][1]), ("Head", joints["Head"][1])]
    rows = spine_weights(local[:, 1], stations)
    hips_y, ankle_y, knee_y = heights["hips"], heights["ankle"], heights["knee"]
    hem = local[:, 1] < heights["ankle"]
    hem_half = float(np.percentile(np.abs(local[hem, 0]), 98)) if hem.sum() >= 3 else abs(joints["LeftUpLeg"][0])
    for v, row in enumerate(rows):
        y, lat = local[v, 1], local[v, 0]
        if y < hips_y:
            depth = float(np.clip((hips_y - y) / max(hips_y - ankle_y, 1e-9), 0.0, 1.0))
            leg = ROBE_LEG_SHARE * depth
            left = float(np.clip(0.5 + lat / (2 * hem_half), 0.0, 1.0))  # across the whole hem: no seam at the middle
            shin = float(np.clip((knee_y - y) / max(KNEE_BLEND * heights["neck"], 1e-9) + 0.5, 0.0, 1.0))
            foot = float(np.clip((ankle_y * FOOT_RISE - y) / max(ankle_y * (FOOT_RISE - 1), 1e-9), 0.0, 1.0))  # the hem stands on the feet
            row.clear()
            row["Hips"] = 1 - leg
            for side, share in (("Left", left), ("Right", 1 - left)):
                if share > 0:
                    row[f"{side}UpLeg"] = leg * share * (1 - shin)
                    row[f"{side}Leg"] = leg * share * shin * (1 - foot)
                    row[f"{side}Foot"] = leg * share * shin * foot
        for side, sign in (("Left", 1.0), ("Right", -1.0)):
            near_clavicle = lat * sign > abs(joints[f"{side}Shoulder"][0]) and y > heights["shoulder"] - 0.04 and y < heights["neck"]
            if near_clavicle:
                w = CLAVICLE_WEIGHT * float(np.clip((lat * sign - abs(joints[f"{side}Shoulder"][0]))
                                                    / max(abs(joints[f"{side}Arm"][0]) - abs(joints[f"{side}Shoulder"][0]), 1e-9), 0.0, 1.0))
                for k in row:
                    row[k] *= 1 - w
                row[f"{side}Shoulder"] = row.get(f"{side}Shoulder", 0.0) + w
    for side, arm in placed["arms"].items():
        for v in np.where(arm["blend"] > 0)[0]:
            a = float(arm["blend"][v])
            s = float(np.clip(arm["share"][v], 0.0, 1.0))
            own = {f"{side}{k}": w for k, w in sleeve_weights(s, float(arm["offset"][v])).items()}
            root = float(np.clip((ARM_ROOT_BLEND - s) / ARM_ROOT_BLEND, 0.0, 1.0)) * CLAVICLE_WEIGHT
            if root:
                own = {k: w * (1 - root) for k, w in own.items()}
                own[f"{side}Shoulder"] = own.get(f"{side}Shoulder", 0.0) + root
            row = rows[v]
            merged = {k: w * (1 - a) for k, w in row.items()}
            for k, w in own.items():
                merged[k] = merged.get(k, 0.0) + w * a
            rows[v] = merged
    out = []
    for row in rows:
        top = sorted(((w, k) for k, w in row.items() if w > 1e-6), reverse=True)[:4]
        total = sum(w for w, _ in top)
        out.append({k: w / total for w, k in top})
    return out


def robe_rig(source: Path, target: Path) -> dict:
    """Re-place `source`'s joints and skin by the module's rules into `target`. The clips are kept as they are (each moved joint's
    translation keys shifted with it): move them onto the new joints with `lib/clip_transfer.py` (`tripo/robe_rig.py` does)."""

    doc, blob = read_glb(source)
    rig = load_rig(doc, blob)
    frame = Frame(rig["positions"], rig["heads"])
    local = frame.local(rig["positions"])
    placed = place(local, rig["triangles"])
    parent_of = {child: i for i, node in enumerate(doc["nodes"]) for child in node.get("children", [])}
    names_of = {node: name for name, node in rig["node_of"].items()}
    parent_name = {name: names_of.get(parent_of.get(node)) for name, node in rig["node_of"].items()}
    spine = spine_names(rig["names"], parent_name)
    if len(spine) != len(SPINE_SHARES):
        raise SeatError(f"the spine has {len(spine)} joints, {len(SPINE_SHARES)} are placed")
    wanted = {(spine[int(key[5:])] if key.startswith("spine") else key): value for key, value in placed["joints"].items()}
    missing = [name for name in wanted if name not in rig["node_of"]]
    if missing:
        raise SeatError(f"the rig has no {', '.join(missing)}")
    moved: Dict[int, np.ndarray] = {}
    order = sorted(wanted, key=lambda name: depth(rig["node_of"][name], parent_of))
    for name in order:
        node = rig["node_of"][name]
        local_pos = np.linalg.inv(worlds(doc)[parent_of[node]]) @ np.append(frame.world(*wanted[name]), 1.0)
        moved[node] = local_pos[:3] - np.asarray(doc["nodes"][node].get("translation", [0.0, 0.0, 0.0]), float)
        doc["nodes"][node]["translation"] = local_pos[:3].tolist()
    # A joint left in place keeps its offset to its parent, so it moves with it (fingers, the toes' and the head's other ends).
    world = worlds(doc)
    rows = skin(local, placed, spine)
    index = {name: k for k, name in enumerate(rig["names"])}
    joint_ids = np.zeros((len(rows), 4), int)
    weights = np.zeros((len(rows), 4), float)
    for v, row in enumerate(rows):
        for slot, (name, w) in enumerate(row.items()):
            joint_ids[v, slot], weights[v, slot] = index[name], w
    skin_doc, attributes = rig["skin"], rig["attributes"]
    put(doc, blob, skin_doc["inverseBindMatrices"], np.stack([np.linalg.inv(world[j]) for j in skin_doc["joints"]]).transpose(0, 2, 1).reshape(-1, 16))
    put(doc, blob, attributes["JOINTS_0"], joint_ids)
    put(doc, blob, attributes["WEIGHTS_0"], weights)
    shifted = shift_translation_keys(doc, blob, moved)
    write_glb(target, doc, blob)
    heights = {k: round(float(v), 4) for k, v in placed["heights"].items()}
    arms = {side: {"vertices": int(arm["core"].sum()), "length": round(arm["length"], 4), "gap_bands": arm["gap_bands"],
                   "body_half_width": arm["body_half_width"]}
            for side, arm in placed["arms"].items()}
    return {"source": str(source), "height": round(frame.height, 4), "heights": heights, "arms": arms, "joints_placed": len(wanted),
            "translation_tracks_shifted": shifted}


def depth(node: int, parent_of: Dict[int, int]) -> int:
    d = 0
    while node in parent_of:
        node, d = parent_of[node], d + 1
    return d
