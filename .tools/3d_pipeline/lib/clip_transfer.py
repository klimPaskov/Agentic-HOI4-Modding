"""Move clips from one rigged GLB to another of the same skeleton names, by each bone's turn from its rest pose in the world.

Tripo's humanoid auto-rig fails on some bodies, and its clips then come out wrong even where the rig can be repaired. On the ZIN devil
(2026-11-22 and 23) five rigs gave one usable one (its arms repaired by `lib/tripo_arm_seat.py`), and on that rig Tripo's idle and walk
pulled both feet to the middle, because the rig's hip joints sit close together while the drawn legs stand wide. A clip that reads well
on a body Tripo rigs cleanly can be moved onto such a rig instead:

1. Source and target are rigged GLBs whose joints share names (Mixamo's, `mixamorig:` dropped). Each joint's rest rotation in the world is
   read from its node transforms.
2. For every frame of a source clip, each joint's turn from its own rest pose in the world, `D = R_now R_rest^-1`, is carried from the
   source body's frame into the target's (`body_frame`: left, up, ahead, from the toes), `D' = F D F^T`, and put on the target joint's rest
   rotation in the world: `R_target = D' R_target_rest`. A joint in the target that the source lacks follows its parent. Then
   each joint's local rotation is taken against its parent's new world rotation.
   Bones pair up by the side of the body they lie on: a rig whose Left joints lie on the body's right (`mirrored`) takes its left
   side's motion from the source's right-named bones.
3. Bone lengths, rest directions and stance stay the target's own. A leg at rest in the source clip leaves the target's leg at its own
   rest, so a wide stance stays wide.
4. Each hinged limb (thigh, shin and foot, upper arm, forearm and hand) is solved again as a two-bone chain (`solve_limb`), so a knee or an
   elbow bends the way the source's does on the target's own bones, and the limb keeps the target's rest stance.
5. The hips keep the source clip's movement from rest, scaled by the ratio of the two rest hip heights, less the clip's mean level offset
   (the route plays clips in place). Every other joint keeps the
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
    """The rig's own frame at rest, as columns (left, up, ahead), from its anatomy: ahead from the heels to the toes (level), up the world's
    +y, left their cross product (the body's own left). Tripo's exports do not all face one way (the D-94 zombie's left foot is at +x),
    and the left and right names do not always lie on the body's left and right (`mirrored`)."""

    up = np.array([0.0, 1.0, 0.0])
    toes = [rig.rest_world[rig.joints[f"{side}ToeBase"]][:3, 3] - rig.rest_world[rig.joints[f"{side}Foot"]][:3, 3]
            for side in ("Left", "Right") if f"{side}ToeBase" in rig.joints and f"{side}Foot" in rig.joints]
    if toes:
        ahead = np.mean(toes, axis=0)
    else:  # no toes: the side the names give, as Mixamo means them
        across = rig.rest_world[rig.joints["LeftUpLeg"]][:3, 3] - rig.rest_world[rig.joints["RightUpLeg"]][:3, 3]
        ahead = np.cross(across, up)
    ahead[1] = 0.0
    ahead /= max(float(np.linalg.norm(ahead)), 1e-12)
    left = np.cross(up, ahead)
    return np.stack([left, up, ahead], axis=1)


def mirrored(rig: "Rig") -> bool:
    """Whether the rig's Left joints lie on the body's right. Tripo's rig of the ZIN devil (2026-11-23) named its sides the wrong way round
    for a body facing its toes: its own clips then turned the hooves half round, crossed the legs and bent the knees backward."""

    across = rig.rest_world[rig.joints["LeftUpLeg"]][:3, 3] - rig.rest_world[rig.joints["RightUpLeg"]][:3, 3]
    return float(across @ body_frame(rig)[:, 0]) < 0


def side_swapped(name: str) -> str:
    if name.startswith("Left"):
        return "Right" + name[4:]
    if name.startswith("Right"):
        return "Left" + name[5:]
    return name


def hips_name(names: Sequence[str]) -> str:
    for name in ("Hips", "Hip"):
        if name in names:
            return name
    raise TransferError("no hips joint")


# Hinged limbs: (root, middle, end) joints. A world turn copied bone by bone bends a hinge the target aims differently the wrong way: on
# the ZIN devil (run devil_e, 2026-11-23) the knees read 11 to 24% of the leg backward after the transfer, though the donor's knees bent
# forward. Each limb is solved again as a two-bone chain (`solve_limb`).
LIMBS = tuple((f"{side}{a}", f"{side}{b}", f"{side}{c}") for side in ("Left", "Right")
              for a, b, c in (("UpLeg", "Leg", "Foot"), ("Arm", "ForeArm", "Hand")))
POLE_MIN_SHARE = 0.02  # a middle joint closer than this share of the limb to the root-end line gives no bend direction


def limb_chains(source: "Rig", target: "Rig", swap: bool = False) -> List[Tuple[int, ...]]:
    """(target root, middle, end, source root, middle, end) node indices of every hinged limb both rigs have, the source's limb on the
    same side of the body (`swap`: the two rigs name their sides the other way round)."""

    out = []
    for names in LIMBS:
        partner = [side_swapped(n) if swap else n for n in names]
        if all(n in target.joints for n in names) and all(n in source.joints for n in partner):
            out.append(tuple(target.joints[n] for n in names) + tuple(source.joints[n] for n in partner))
    return out


def world_positions(rig: "Rig", world_rot: Dict[int, np.ndarray], hips: int, shift: np.ndarray) -> Dict[int, np.ndarray]:
    """Joint positions from the frame's world rotations and the rig's own rest offsets (each parent's rest scale kept), the hips moved."""

    pos: Dict[int, np.ndarray] = {}
    for i in rig.order:
        if i not in rig.parent:
            pos[i] = rig.rest_world[i][:3, 3].copy()
            continue
        p = rig.parent[i]
        scale = float(np.cbrt(abs(np.linalg.det(rig.rest_world[p][:3, :3]))))
        pos[i] = pos[p] + scale * (world_rot[p] @ np.asarray(rig.nodes[i].get("translation", [0.0, 0.0, 0.0]), float))
        if i == hips:
            pos[i] = pos[i] + shift
    return pos


def arc(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """The shortest rotation taking direction a to direction b."""

    a = a / max(float(np.linalg.norm(a)), 1e-12)
    b = b / max(float(np.linalg.norm(b)), 1e-12)
    v, c = np.cross(a, b), float(a @ b)
    if c < -0.999999:
        axis = np.cross(a, [1.0, 0.0, 0.0])
        if np.linalg.norm(axis) < 1e-6:
            axis = np.cross(a, [0.0, 1.0, 0.0])
        axis /= np.linalg.norm(axis)
        return 2.0 * np.outer(axis, axis) - np.eye(3)
    k = np.array([[0.0, -v[2], v[1]], [v[2], 0.0, -v[0]], [-v[1], v[0], 0.0]])
    return np.eye(3) + k + k @ k / (1.0 + c)


def solve_limb(target: "Rig", world_rot: Dict[int, np.ndarray], limb: Tuple[int, ...], posed: Dict[int, np.ndarray], source: "Rig",
               frame: np.ndarray, shift: np.ndarray, hips: int) -> None:
    """Re-aim one limb's two bones, in place in `world_rot`: the end reaches where the source's end is against the root, scaled by the
    limb's length and kept at the target's own rest stance (that offset turned with the root's parent), and the middle joint bends
    toward the source's bend, or the target's own rest bend when the source's limb is straight. The end joint keeps its turn."""

    ta, tb, tc, sa, sb, sc = limb
    rest = {i: target.rest_world[i][:3, 3] for i in (ta, tb, tc)}
    l1, l2 = float(np.linalg.norm(rest[tb] - rest[ta])), float(np.linalg.norm(rest[tc] - rest[tb]))
    s_rest = {i: source.rest_world[i][:3, 3] for i in (sa, sb, sc)}
    s_len = float(np.linalg.norm(s_rest[sb] - s_rest[sa]) + np.linalg.norm(s_rest[sc] - s_rest[sb]))
    scale = (l1 + l2) / max(s_len, 1e-12)
    pos = world_positions(target, world_rot, hips, shift)
    parent = target.parent[ta]
    parent_turn = world_rot[parent] @ rotation_part(target.rest_world[parent]).T
    stance = (rest[tc] - rest[ta]) - frame @ (s_rest[sc] - s_rest[sa]) * scale
    goal = pos[ta] + frame @ (posed[sc][:3, 3] - posed[sa][:3, 3]) * scale + parent_turn @ stance
    reach = goal - pos[ta]
    d = float(np.clip(np.linalg.norm(reach), abs(l1 - l2) + 1e-6, (l1 + l2) * 0.9999))
    u = reach / max(float(np.linalg.norm(reach)), 1e-12)
    s_line = posed[sc][:3, 3] - posed[sa][:3, 3]
    s_off = posed[sb][:3, 3] - posed[sa][:3, 3]
    s_off = s_off - (s_off @ s_line) / max(float(s_line @ s_line), 1e-12) * s_line
    if np.linalg.norm(s_off) > POLE_MIN_SHARE * s_len:
        pole = frame @ s_off
    else:
        line = rest[tc] - rest[ta]
        off = rest[tb] - rest[ta]
        pole = parent_turn @ (off - (off @ line) / max(float(line @ line), 1e-12) * line)
    pole = pole - (pole @ u) * u
    if np.linalg.norm(pole) < 1e-9:
        return
    pole /= np.linalg.norm(pole)
    x = (l1 * l1 - l2 * l2 + d * d) / (2.0 * d)
    middle = pos[ta] + u * x + pole * np.sqrt(max(l1 * l1 - x * x, 0.0))
    end = pos[ta] + u * d
    world_rot[ta] = arc(pos[tb] - pos[ta], middle - pos[ta]) @ world_rot[ta]
    pos = world_positions(target, world_rot, hips, shift)
    world_rot[tb] = arc(pos[tc] - pos[tb], end - pos[tb]) @ world_rot[tb]


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
    shifts: List[np.ndarray] = []
    swap = mirrored(source) != mirrored(target)  # pair the bones by the side of the body they lie on, not by their names
    limbs = limb_chains(source, target, swap)
    for t in times:
        posed = source.world_at({node: {path: sample(ts, vs, t, path) for path, (ts, vs) in paths.items()} for node, paths in channels.items()})
        world_rot: Dict[int, np.ndarray] = {}
        for i in target.order:
            if i not in target.parent:
                world_rot[i] = rotation_part(target.rest_world[i])
                continue
            name = short(target.nodes[i].get("name", ""))
            name = side_swapped(name) if swap else name
            if i in out and name in source.joints:
                s = source.joints[name]
                turn = frame @ rotation_part(posed[s]) @ rotation_part(source.rest_world[s]).T @ frame.T
                world_rot[i] = turn @ rotation_part(target.rest_world[i])
            else:
                world_rot[i] = world_rot[target.parent[i]] @ rotation_part(trs(target.nodes[i]))
        shift = frame @ (posed[s_hips][:3, 3] - source.rest_world[s_hips][:3, 3]) * ratio
        for limb in limbs:
            solve_limb(target, world_rot, limb, posed, source, frame, shift, t_hips)
        for i in target.order:
            if i not in out:
                continue
            out[i]["rotation"].append(matrix_to_quat(world_rot[target.parent[i]].T @ world_rot[i]))
            if i == t_hips:
                shifts.append(shift)
                out[i]["translation"].append(None)  # filled once the clip's mean drift is known
            else:
                out[i]["translation"].append(np.asarray(target.nodes[i].get("translation", [0.0, 0.0, 0.0]), float))
    # The route plays every clip in place. A clip that holds the hips off their rest spot throughout (Tripo's run on the demo goblin kept
    # them 0.44 of its units ahead in every frame, and moved onto the devil it stood him 0.13 to the side and 0.19 back) keeps only its
    # level motion around its own mean: the mean of the level shift is taken away, the height kept.
    shifts_arr = np.asarray(shifts)
    if len(shifts_arr):
        mean = shifts_arr.mean(axis=0)
        mean[1] = 0.0
        parent_world = target.rest_world[target.parent[t_hips]]
        rest_t = np.asarray(target.nodes[t_hips].get("translation", [0.0, 0.0, 0.0]), float)
        out[t_hips]["translation"] = [rest_t + np.linalg.solve(parent_world[:3, :3], shift - mean) for shift in shifts_arr]
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
