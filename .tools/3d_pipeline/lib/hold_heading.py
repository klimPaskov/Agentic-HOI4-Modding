"""Hold a clip's heading: the hips' turn about the world's up axis stays within a limit of the clip's first frame.

A made retreat can turn the unit away from the camera (the demon's turned 192 degrees, and its spread wings then crossed the body from the
front, TRIPO-WING-FRONT 19 to 31%). The game turns the whole unit to face its way of travel, so the clip itself does not need to turn. The
yaw beyond the limit is taken off the hips' world rotation frame by frame, so the lean, the bend and the steps stay as they were.

With `spine`, the spine's bones (`Spine`, `Spine1`, `Spine2`) are held the same way after the hips, parent first. In a made turn the
shoulders lead the hips: with only the hips held, the demon's shoulders still turned 21 degrees against them, and with the route's look back
on top the waist read 43 degrees wrung (TRIPO-WAIST-TWIST, limit 24.5).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Sequence

import numpy as np

from .clip_transfer import matrix_to_quat, quat_to_matrix
from .tripo_arm_seat import get, put, read_glb, short, trs, worlds, write_glb
from .tripo_rig import RigError, RigNames

SPINE = ("Spine", "Spine1", "Spine2")


class HeadingError(RuntimeError):
    pass


def _yaw(degrees: float) -> np.ndarray:
    a = np.radians(degrees)
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])


def _rotation(matrix: np.ndarray) -> np.ndarray:
    return matrix / np.linalg.norm(matrix, axis=0)


def _joints(doc: dict, canonical: Sequence[str]) -> List[int]:
    names = [short(node.get("name", "")) for node in doc["nodes"]]
    try:
        rig = RigNames([n for n in names if n])
    except RigError as error:
        raise HeadingError(str(error)) from error
    out = []
    for bone in canonical:
        actual = rig.actual(bone)
        if actual is None:
            if bone == "Hips":
                raise HeadingError("no hip bone in the GLB")
            continue
        out.append(names.index(actual))
    return out


def headings(quats: np.ndarray, parent: np.ndarray) -> np.ndarray:
    """A joint's heading in degrees about world up for each key, unwrapped. `parent` is the parent's world rotation, one (3, 3) or one per
    key (K, 3, 3)."""

    parents = np.broadcast_to(parent, (len(quats), 3, 3))
    forward = [p @ quat_to_matrix(q) @ np.array([0.0, 0.0, 1.0]) for p, q in zip(parents, quats)]
    return np.degrees(np.unwrap(np.array([np.arctan2(f[0], f[2]) for f in forward])))


def held(quats: np.ndarray, parent: np.ndarray, limit: float) -> np.ndarray:
    """The local turns with the heading clipped to `limit` degrees of the first key, the rest of each turn kept."""

    parents = np.broadcast_to(parent, (len(quats), 3, 3))
    turn = headings(quats, parents)
    delta = turn - turn[0]
    kept = np.clip(delta, -limit, limit)
    out = []
    for p, q, d, k in zip(parents, quats, delta, kept):
        world = _yaw(k - d) @ p @ quat_to_matrix(q)
        new = matrix_to_quat(p.T @ world)
        out.append(new / np.linalg.norm(new))
    out = np.array(out)
    for i in range(1, len(out)):
        if np.dot(out[i], out[i - 1]) < 0:
            out[i] = -out[i]
    return out


def _sample(times: np.ndarray, quats: np.ndarray, at: np.ndarray) -> np.ndarray:
    """A rotation channel at the times `at`, normalised linear blend of the neighbouring keys."""

    out = []
    for t in at:
        i = int(np.clip(np.searchsorted(times, t), 1, len(times) - 1)) if len(times) > 1 else 0
        if len(times) == 1:
            out.append(quats[0])
            continue
        a, b = quats[i - 1], quats[i]
        if np.dot(a, b) < 0:
            b = -b
        w = float(np.clip((t - times[i - 1]) / max(times[i] - times[i - 1], 1e-9), 0.0, 1.0))
        q = (1 - w) * a + w * b
        out.append(q / np.linalg.norm(q))
    return np.array(out)


def hold(source: Path, out: Path, clips: Sequence[str], limit: float, spine: bool = False) -> List[Dict[str, object]]:
    """Write `out` with each named clip's heading held within `limit` degrees. `clips` takes exact names or first words."""

    doc, blob = read_glb(Path(source))
    joints = _joints(doc, ("Hips",) + (SPINE if spine else ()))
    parent_of = {child: i for i, node in enumerate(doc["nodes"]) for child in node.get("children", [])}
    rest_world = worlds(doc)
    report = []
    for clip in clips:
        animation = next((a for a in doc.get("animations", []) if a.get("name", "") == clip), None)
        animation = animation or next((a for a in doc.get("animations", []) if a.get("name", "").startswith(clip)), None)
        if animation is None:
            raise HeadingError(f"no clip named or starting {clip!r}")
        rotations = {c["target"]["node"]: animation["samplers"][c["sampler"]] for c in animation["channels"] if c["target"]["path"] == "rotation"}
        row: Dict[str, object] = {"clip": animation["name"], "limit": limit, "turned": 0.0}
        for joint in joints:
            if joint not in rotations:
                continue
            sampler = rotations[joint]
            times = get(doc, blob, sampler["input"]).astype(float).ravel()
            quats = get(doc, blob, sampler["output"]).astype(float)
            parent = _parent_world(doc, blob, parent_of, rest_world, rotations, joint, times)
            turn = headings(quats, parent)
            put(doc, blob, sampler["output"], held(quats, parent, limit).astype(np.float32))
            name = short(doc["nodes"][joint].get("name", ""))
            row.setdefault("joints", {})[name] = round(float(np.abs(turn - turn[0]).max()), 1)
            if joint == joints[0]:
                row["turned"] = float(np.abs(turn - turn[0]).max())
        if spine and len(joints) > 1 and joints[-1] in rotations:
            row["shoulder_line"] = _hold_shoulder_line(doc, blob, parent_of, rest_world, rotations, joints[-1], limit)
        report.append(row)
    write_glb(Path(out), doc, blob)
    return report


def _hold_shoulder_line(doc: dict, blob: bytearray, parent_of: Dict[int, int], rest_world: Dict[int, np.ndarray], rotations: Dict[int, dict],
                        top: int, limit: float) -> float:
    """Turn the top spine bone about world up so the line between the upper arms keeps its heading within `limit` of the first key. The
    collar bones' swing turns that line even with the spine held (the demon's by 12 degrees), and TRIPO-WAIST-TWIST reads that line. Both
    upper arms hang under the top spine bone, so a world turn of it turns the line by exactly as much. Returns the largest turn taken off."""

    names = [short(node.get("name", "")) for node in doc["nodes"]]
    rig = RigNames([n for n in names if n])
    arms = [rig.actual(side) for side in ("LeftArm", "RightArm")]
    if None in arms:
        return 0.0
    left, right = (names.index(a) for a in arms)
    sampler = rotations[top]
    times = get(doc, blob, sampler["input"]).astype(float).ravel()
    quats = get(doc, blob, sampler["output"]).astype(float)
    channels = {}
    animation = next(a for a in doc["animations"] if any(s is sampler for s in a["samplers"]))
    for channel in animation["channels"]:
        source = animation["samplers"][channel["sampler"]]
        channels.setdefault(channel["target"]["node"], {})[channel["target"]["path"]] = (
            get(doc, blob, source["input"]).astype(float).ravel(), get(doc, blob, source["output"]).astype(float))
    line = []
    for t in times:
        posed = _world_positions(doc, parent_of, channels, t)
        v = posed[right] - posed[left]
        line.append(np.arctan2(v[0], v[2]))
    delta = np.degrees(np.unwrap(np.array(line)))
    delta = delta - delta[0]
    correction = np.clip(delta, -limit, limit) - delta
    parent = _parent_world(doc, blob, parent_of, rest_world, rotations, top, times)
    out = []
    for p, q, c in zip(parent, quats, correction):
        new = matrix_to_quat(p.T @ _yaw(c) @ p @ quat_to_matrix(q))
        out.append(new / np.linalg.norm(new))
    out = np.array(out)
    for i in range(1, len(out)):
        if np.dot(out[i], out[i - 1]) < 0:
            out[i] = -out[i]
    put(doc, blob, sampler["output"], out.astype(np.float32))
    return round(float(np.abs(correction).max()), 1)


def _world_positions(doc: dict, parent_of: Dict[int, int], channels: Dict[int, Dict[str, tuple]], t: float) -> Dict[int, np.ndarray]:
    """Every node's world position at time `t`: the clip's sampled rotation and translation where it keys them, the node's own otherwise."""

    cache: Dict[int, np.ndarray] = {}

    def world(i: int) -> np.ndarray:
        if i in cache:
            return cache[i]
        node = dict(doc["nodes"][i])
        for path, (times, values) in channels.get(i, {}).items():
            if path == "rotation":
                node[path] = list(_sample(times, values, np.array([t]))[0])
            elif path in ("translation", "scale"):
                node[path] = [float(np.interp(t, times, values[:, k])) for k in range(values.shape[1])]
        local = trs(node)
        cache[i] = world(parent_of[i]) @ local if i in parent_of else local
        return cache[i]

    return {i: world(i)[:3, 3] for i in range(len(doc["nodes"]))}


def _parent_world(doc: dict, blob: bytearray, parent_of: Dict[int, int], rest_world: Dict[int, np.ndarray], rotations: Dict[int, dict],
                  joint: int, times: np.ndarray) -> np.ndarray:
    """The world rotation of `joint`'s parent at each of `times`: the clip's own rotation for every animated ancestor, the rest pose's
    for the others (read after the ancestors above were held)."""

    chain = []
    node = parent_of.get(joint)
    while node is not None:
        chain.append(node)
        node = parent_of.get(node)
    out = np.broadcast_to(np.eye(3), (len(times), 3, 3)).copy()
    for node in reversed(chain):
        if node in rotations:
            sampler = rotations[node]
            local = _sample(get(doc, blob, sampler["input"]).astype(float).ravel(), get(doc, blob, sampler["output"]).astype(float), times)
            out = np.array([o @ quat_to_matrix(q) for o, q in zip(out, local)])
        else:
            parent = parent_of.get(node)
            base = rest_world[parent][:3, :3] if parent is not None else np.eye(3)
            local = _rotation(np.linalg.inv(_rotation(base)) @ _rotation(rest_world[node][:3, :3])) if parent is not None else _rotation(rest_world[node][:3, :3])
            out = np.array([o @ local for o in out])
    return out
