"""Move clips from one rigged GLB to another of the same skeleton names, by each bone's turn from its rest pose in the world.

Tripo's humanoid auto-rig fails on some bodies, and its clips then come out wrong even where the rig can be repaired. On the ZIN devil
(2026-11-22 and 23) five rigs gave one usable one (its arms repaired by `lib/tripo_arm_seat.py`), and on that rig Tripo's idle and walk
pulled both feet to the middle, because the rig's hip joints sit close together while the drawn legs stand wide. A clip that reads well
on a body Tripo rigs cleanly can be moved onto such a rig instead:

1. Source and target are rigged GLBs whose joints share names (Mixamo's, `mixamorig:` dropped). Each joint's rest rotation in the world is
   read from its node transforms.
2. For every frame of a source clip, each joint's turn from its own rest pose in the world, `D = R_now R_rest^-1`, is carried from the
   source body's frame into the target's (`body_frame`: across the thighs, up, ahead), `D' = F D F^T`, and put on the target joint's rest
   rotation in the world: `R_target = D' R_target_rest`. A joint in the target that the source lacks follows its parent. Then
   each joint's local rotation is taken against its parent's new world rotation.
3. Bone lengths, rest directions and stance stay the target's own. A leg at rest in the source clip leaves the target's leg at its own
   rest, so a wide stance stays wide.
4. The hips keep the source clip's movement from rest, scaled by the ratio of the two rest hip heights. Every other joint keeps the
   target's rest translation and scale.

The output is the target GLB with its clips replaced by the moved ones, named as in the source. Maths only (numpy) on the GLB's own
arrays: no Blender.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .tripo_arm_seat import get, read_glb, short, trs, write_glb


class TransferError(RuntimeError):
    pass


def quat_to_matrix(q: np.ndarray) -> np.ndarray:
    x, y, z, w = np.asarray(q, float) / max(float(np.linalg.norm(q)), 1e-12)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def matrix_to_quat(m: np.ndarray) -> np.ndarray:
    """(x, y, z, w) of an orthonormal 3x3 rotation."""

    m = np.asarray(m, float)
    trace = m[0, 0] + m[1, 1] + m[2, 2]
    if trace > 0:
        s = 2.0 * np.sqrt(trace + 1.0)
        q = [(m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s, 0.25 * s]
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = 2.0 * np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2])
        q = [0.25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s, (m[2, 1] - m[1, 2]) / s]
    elif m[1, 1] > m[2, 2]:
        s = 2.0 * np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2])
        q = [(m[0, 1] + m[1, 0]) / s, 0.25 * s, (m[1, 2] + m[2, 1]) / s, (m[0, 2] - m[2, 0]) / s]
    else:
        s = 2.0 * np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1])
        q = [(m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, 0.25 * s, (m[1, 0] - m[0, 1]) / s]
    q = np.asarray(q, float)
    return q / np.linalg.norm(q)


def rotation_part(matrix: np.ndarray) -> np.ndarray:
    """The rotation of a 4x4 or 3x3 transform, scale removed (polar decomposition)."""

    u, _s, vt = np.linalg.svd(np.asarray(matrix, float)[:3, :3])
    r = u @ vt
    if np.linalg.det(r) < 0:
        u[:, -1] *= -1
        r = u @ vt
    return r


def sample(times: np.ndarray, values: np.ndarray, t: float, path: str) -> np.ndarray:
    """A channel's value at time `t`: linear between keys, normalised for rotations, held past the ends."""

    times = np.asarray(times, float).ravel()
    if t <= times[0]:
        return values[0]
    if t >= times[-1]:
        return values[-1]
    k = int(np.searchsorted(times, t)) - 1
    share = (t - times[k]) / max(times[k + 1] - times[k], 1e-12)
    a, b = values[k], values[k + 1]
    if path == "rotation":
        if float(a @ b) < 0:
            b = -b
        out = (1 - share) * a + share * b
        return out / max(float(np.linalg.norm(out)), 1e-12)
    return (1 - share) * a + share * b


class Rig:
    """A rigged GLB's node tree: parents, rest transforms and the joints by short name."""

    def __init__(self, path: Path):
        self.doc, self.blob = read_glb(path)
        self.nodes = self.doc["nodes"]
        self.parent = {child: i for i, node in enumerate(self.nodes) for child in node.get("children", [])}
        skin = self.doc["skins"][0]
        self.joints = {short(self.nodes[j].get("name", "")): j for j in skin["joints"]}
        self.order = self._order()
        self.rest_world = self.world_at({})

    def _order(self) -> List[int]:
        seen, out = set(), []

        def visit(i: int) -> None:
            if i in seen:
                return
            if i in self.parent:
                visit(self.parent[i])
            seen.add(i)
            out.append(i)

        for i in range(len(self.nodes)):
            visit(i)
        return out

    def world_at(self, overrides: Dict[int, Dict[str, np.ndarray]]) -> Dict[int, np.ndarray]:
        """Every node's world transform with `overrides` (node: {path: value}) in place of its rest TRS."""

        out: Dict[int, np.ndarray] = {}
        for i in self.order:
            node = dict(self.nodes[i])
            for path, value in overrides.get(i, {}).items():
                node[path] = [float(v) for v in value]
            local = trs(node)
            out[i] = out[self.parent[i]] @ local if i in self.parent else local
        return out

    def clips(self) -> Dict[str, dict]:
        """Each animation's name and its channels: node -> path -> (times, values)."""

        out: Dict[str, dict] = {}
        for animation in self.doc.get("animations", []):
            channels: Dict[int, Dict[str, Tuple[np.ndarray, np.ndarray]]] = {}
            for channel in animation["channels"]:
                sampler = animation["samplers"][channel["sampler"]]
                times = get(self.doc, self.blob, sampler["input"]).astype(float).ravel()
                values = get(self.doc, self.blob, sampler["output"]).astype(float)
                channels.setdefault(channel["target"]["node"], {})[channel["target"]["path"]] = (times, values)
            out[animation.get("name", "")] = channels
        return out


def clip_times(channels: Dict[int, Dict[str, Tuple[np.ndarray, np.ndarray]]]) -> np.ndarray:
    """The densest key times of a clip's channels (Tripo keys every channel of a clip at one or two rates)."""

    return max((times for paths in channels.values() for times, _values in paths.values()), key=len)


def body_frame(rig: "Rig") -> np.ndarray:
    """The rig's own frame at rest, as columns (across, up, ahead): across from the left thigh joint to the right, up the world's +y, ahead
    their cross product. Tripo's exports do not all face one way: the D-94 zombie's left foot is at +x, the ZIN devil's at -x."""

    across = rig.rest_world[rig.joints["RightUpLeg"]][:3, 3] - rig.rest_world[rig.joints["LeftUpLeg"]][:3, 3]
    across[1] = 0.0
    across /= max(float(np.linalg.norm(across)), 1e-12)
    up = np.array([0.0, 1.0, 0.0])
    return np.stack([across, up, np.cross(across, up)], axis=1)


def hips_name(names: Sequence[str]) -> str:
    for name in ("Hips", "Hip"):
        if name in names:
            return name
    raise TransferError("no hips joint")


def transfer_clip(source: Rig, target: Rig, channels: Dict[int, Dict[str, Tuple[np.ndarray, np.ndarray]]]) -> Tuple[np.ndarray, Dict[int, Dict[str, np.ndarray]]]:
    """(times, target node -> path -> per-frame values) of one source clip moved onto the target, by the rules of the module text."""

    times = clip_times(channels)
    hips = hips_name(list(target.joints))
    if hips not in source.joints:
        raise TransferError("the source has no hips joint")
    s_hips, t_hips = source.joints[hips], target.joints[hips]
    s_rest_h = float(source.rest_world[s_hips][1, 3] - min(source.rest_world[j][1, 3] for j in source.joints.values()))
    t_rest_h = float(target.rest_world[t_hips][1, 3] - min(target.rest_world[j][1, 3] for j in target.joints.values()))
    ratio = t_rest_h / max(s_rest_h, 1e-12)
    # a turn in the source's own frame is the same turn in the target's: F maps the source's world into the target's
    frame = body_frame(target) @ body_frame(source).T
    out: Dict[int, Dict[str, List[np.ndarray]]] = {j: {"rotation": [], "translation": []} for j in target.joints.values()}
    for t in times:
        posed = source.world_at({node: {path: sample(ts, vs, t, path) for path, (ts, vs) in paths.items()} for node, paths in channels.items()})
        world_rot: Dict[int, np.ndarray] = {}
        for i in target.order:
            if i not in target.parent:
                world_rot[i] = rotation_part(target.rest_world[i])
                continue
            parent_rot = world_rot[target.parent[i]]
            name = short(target.nodes[i].get("name", ""))
            if i in out and name in source.joints:
                s = source.joints[name]
                turn = frame @ rotation_part(posed[s]) @ rotation_part(source.rest_world[s]).T @ frame.T
                world_rot[i] = turn @ rotation_part(target.rest_world[i])
            else:
                world_rot[i] = parent_rot @ rotation_part(trs(target.nodes[i]))
            if i in out:
                out[i]["rotation"].append(matrix_to_quat(parent_rot.T @ world_rot[i]))
                rest_t = np.asarray(target.nodes[i].get("translation", [0.0, 0.0, 0.0]), float)
                if i == t_hips:
                    shift = frame @ (posed[s_hips][:3, 3] - source.rest_world[s_hips][:3, 3]) * ratio
                    parent_world = target.rest_world[target.parent[i]] if target.parent.get(i) is not None else np.eye(4)
                    shift_local = np.linalg.solve(parent_world[:3, :3], shift)
                    out[i]["translation"].append(rest_t + shift_local)
                else:
                    out[i]["translation"].append(rest_t)
    return times, {node: {path: np.asarray(values) for path, values in paths.items()} for node, paths in out.items()}


def _append(doc: dict, blob: bytearray, values: np.ndarray, kind: str) -> int:
    """Append a float array as a new buffer view and accessor; returns the accessor's index."""

    values = np.ascontiguousarray(values, dtype=np.float32)
    while len(blob) % 4:
        blob.append(0)
    offset = len(blob)
    blob.extend(values.tobytes())
    doc["bufferViews"].append({"buffer": 0, "byteOffset": offset, "byteLength": values.nbytes})
    accessor = {"bufferView": len(doc["bufferViews"]) - 1, "componentType": 5126, "count": int(values.shape[0]), "type": kind}
    if kind == "SCALAR":
        accessor.update(min=[float(values.min())], max=[float(values.max())])
    doc["accessors"].append(accessor)
    return len(doc["accessors"]) - 1


def transfer(source_path: Path, target_path: Path, out_path: Path, clips: Optional[Sequence[str]] = None) -> dict:
    """Move the named source clips (all when None) onto the target rig and write `out_path` with only those clips. Returns a report."""

    source, target = Rig(source_path), Rig(target_path)
    shared = sorted(set(source.joints) & set(target.joints))
    if hips_name(list(target.joints)) not in shared:
        raise TransferError("the two rigs share no hips joint")
    found = source.clips()
    wanted = list(found) if clips is None else [name for name in found if any(name == c or name.startswith(c) for c in clips)]
    missing = [c for c in (clips or []) if not any(name == c or name.startswith(c) for name in found)]
    if missing:
        raise TransferError(f"the source has no clip {', '.join(missing)}; it has {', '.join(found)}")
    doc, blob = target.doc, target.blob
    animations = []
    for name in wanted:
        times, tracks = transfer_clip(source, target, found[name])
        time_accessor = _append(doc, blob, times.reshape(-1, 1), "SCALAR")
        samplers, channels = [], []
        for node, paths in tracks.items():
            for path, values in paths.items():
                samplers.append({"input": time_accessor, "output": _append(doc, blob, values, "VEC4" if path == "rotation" else "VEC3"),
                                 "interpolation": "LINEAR"})
                channels.append({"sampler": len(samplers) - 1, "target": {"node": node, "path": path}})
        animations.append({"name": name, "samplers": samplers, "channels": channels})
    doc["animations"] = animations
    doc["buffers"][0]["byteLength"] = len(blob)
    write_glb(out_path, doc, blob)
    return {"source": str(source_path), "target": str(target_path), "clips": wanted, "shared_joints": len(shared),
            "source_only": sorted(set(source.joints) - set(target.joints)), "target_only": sorted(set(target.joints) - set(source.joints))}
