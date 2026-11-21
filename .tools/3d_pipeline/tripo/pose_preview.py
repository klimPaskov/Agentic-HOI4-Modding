"""Try a quadruped clip or key pose on a unit's exported files before spending a full run.

    py -3.13 pose_preview.py <unit folder> --landmarks <job root or json> --out <folder> [--plan plan.json] [--sheet]

The kit's quadruped rig (`adapter/quadruped_layout.py`, `adapter/quadruped_wings.py`) writes every clip by rule, and a full run of the
route takes many minutes of Blender to show one choice of numbers. This tool plays the same rules on the files a run already exported:
it reads the `.mesh` (the bones, the final weights), builds the layout from the rig's landmarks (the adapter's rig result in the job
root, or a JSON file of them), poses each frame as `quadruped_rig.author_action` does (the body's turn, the ground contact, a death's
side and rest) and writes `.anim` files beside a copy of the mesh and its textures. No Blender runs, so a candidate takes seconds, and
the folder it writes is a unit folder: `tripo/tripo_checks.py` and `check_unit_files.py` measure it as they measure a run, and
`tripo/clip_sheet.py` (one Blender start, through the gate) renders its frames from the game camera, the front and the left at review
size. `--sheet` runs that render.

A plan names the candidates. Without one, the six roles are written with the kit's rules as they stand:

    {"clips": [
      {"name": "defend", "style": "winged_guard"},
      {"name": "defend_low", "style": "winged_guard",
       "set": {"quadruped_wings.MANTLE": {"sweep": 60.0}, "quadruped_layout.GUARD_BEND": 40.0}},
      {"name": "death_end", "style": "winged_collapse", "times": [1.0]}
    ]}

`set` changes a module's constant for that clip only (a dict value updates the constant's keys). `times` writes only those moments of
the clip (0 to 1) as a short clip of key poses, one frame each: a batch of candidate poses renders as one sheet. `collapse` fixes a
death's side and rest (`{"roll": -82.0, "neck_drop": 30.0, ...}`) instead of searching for them.

On the Tripo dragon the clips this writes from run 14's landmarks lie within 0.05% of the height of the clips the route exported
(`--compare`), and the checks read the same three findings on them. A death lies up to 2.7% of the height aside and may rest its
neck 10 degrees differently: the route picks a death's rest and its spot on the mesh before the weights are smoothed.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import shutil
import struct
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(PIPELINE_ROOT / "adapter"))

from lib import pdx_deform

import quadruped_layout as ql
import quadruped_wings as qw

MODULES = {"quadruped_layout": ql, "quadruped_wings": qw}
AUTHOR_FPS = 24.0  # quadruped_rig.FPS
EXPORT_FPS = 30.0
TORSO = ("Pelvis", "Spine", "Chest")
ROLES = ("idle", "move", "attack", "defend", "retreat", "death")


# ---------------------------------------------------------------------------------------------
# Landmarks and the frame of the exported files
# ---------------------------------------------------------------------------------------------


def _json_tail(text: str) -> Optional[dict]:
    """The first JSON object that starts a line (the adapter writes its log lines round the result)."""

    for index, char in enumerate(text):
        if char == "{" and (index == 0 or text[index - 1] == "\n"):
            try:
                return json.JSONDecoder().raw_decode(text, index)[0]
            except json.JSONDecodeError:
                continue
    return None


def _find_landmarks(value: object) -> Optional[dict]:
    if isinstance(value, dict):
        found = value.get("landmarks")
        if isinstance(found, dict) and "ground_offset" in found and "legs" in found:
            return found
        for item in value.values():
            inner = _find_landmarks(item)
            if inner is not None:
                return inner
    return None


def read_landmarks(source: Path) -> dict:
    """The rig's landmarks: a JSON file of them, or the rig result under a job root's `logs/adapter`."""

    source = Path(source)
    files = [source] if source.is_file() else sorted((source / "logs" / "adapter").glob("*.result.json"))
    for path in files:
        data = _json_tail(path.read_text(encoding="utf-8", errors="replace"))
        found = _find_landmarks(data) if data is not None else None
        if found is None and isinstance(data, dict) and "ground_offset" in data:
            found = data
        if found is not None:
            return as_arrays(found)
    raise FileNotFoundError(f"no quadruped landmarks under {source}")


def as_arrays(measured: dict) -> dict:
    """`quadruped_rig._landmarks_from_payload` without Blender."""

    landmarks = copy.deepcopy(dict(measured))
    for key in ("muzzle", "poll", "saddle"):
        landmarks[key] = np.asarray(landmarks[key], dtype=float)
    if landmarks.get("tail"):
        landmarks["tail"] = [np.asarray(item, dtype=float) for item in landmarks["tail"]]
    landmarks["legs"] = {leg: {joint: np.asarray(value, dtype=float) for joint, value in joints.items()} for leg, joints in landmarks["legs"].items()}
    landmarks.pop("death", None)
    return landmarks


def fit_frame(source: np.ndarray, target: np.ndarray) -> Tuple[np.ndarray, float]:
    """The 4x4 similarity (a turn or a mirror, one scale, a shift) that best carries `source` points onto `target`, and its worst miss."""

    a, b = source - source.mean(axis=0), target - target.mean(axis=0)
    u, values, vt = np.linalg.svd(b.T @ a)
    best = None
    for flip in (1.0, -1.0):
        d = np.diag([1.0, 1.0, flip])
        turn = u @ d @ vt
        scale = float((values * np.diag(d)).sum() / (a**2).sum())
        matrix = np.eye(4)
        matrix[:3, :3] = scale * turn
        matrix[:3, 3] = target.mean(axis=0) - scale * turn @ source.mean(axis=0)
        miss = float(np.abs(source @ matrix[:3, :3].T + matrix[:3, 3] - target).max())
        if best is None or miss < best[1]:
            best = (matrix, miss)
    return best


# ---------------------------------------------------------------------------------------------
# Posing
# ---------------------------------------------------------------------------------------------


def _turn(rows: Sequence[Tuple[Sequence[float], float]]) -> np.ndarray:
    result = np.eye(3)
    for axis, degrees in rows:
        result = qw.rotation(axis, degrees) @ result
    return result


def _about(centre: np.ndarray, turn: np.ndarray) -> np.ndarray:
    matrix = np.eye(4)
    matrix[:3, :3] = turn
    matrix[:3, 3] = centre - turn @ centre
    return matrix


def _shift(vector: Sequence[float]) -> np.ndarray:
    matrix = np.eye(4)
    matrix[:3, 3] = vector
    return matrix


def whole_turn(pose: dict, landmarks: dict, root_head: np.ndarray) -> np.ndarray:
    """`quadruped_rig._whole_turn`: the body's pitch about the hind hooves, its roll about the edge of the side it falls toward, a step
    back, and a turn about the vertical through its middle."""

    ground = float(landmarks["ground_offset"])
    rear = [landmarks["legs"][f"Rear_{side}"]["ground"] for side in ("Left", "Right")]
    rear_pivot = np.array([(rear[0][0] + rear[1][0]) / 2, (rear[0][1] + rear[1][1]) / 2, ground])
    body = _shift(sum((np.asarray(axis, float) * distance for axis, distance in pose.get("__root_shift__", [])), np.zeros(3)))
    if "__root_pitch__" in pose or "__root_yaw__" in pose:
        body = body @ _about(rear_pivot, _turn(list(pose.get("__root_pitch__", [])) + list(pose.get("__root_yaw__", []))))
    elif "__root_roll__" in pose:
        degrees = pose["__root_roll__"][0][1]
        edge = root_head + np.array([math.copysign(0.5 * float(landmarks["width"]), degrees), 0.0, 0.0])
        body = body @ _about(edge, _turn(pose["__root_roll__"]))
    if "__root_turn__" in pose:
        body = _about(root_head, _turn(pose["__root_turn__"])) @ body
    return body


class Stage:
    """A unit's exported mesh in the rig's own frame, ready to be posed by the layout's rules."""

    def __init__(self, mesh: pdx_deform.SkinnedMesh, landmarks: dict):
        self.mesh = mesh
        self.landmarks = landmarks
        self.layout = ql.build_layout(landmarks)
        names = [bone.name for bone in self.layout.bones if bone.name in mesh.bones]
        missing = [name for name in mesh.bones if name not in self.layout.names()]
        if missing or len(names) < 4:
            raise ValueError(f"the mesh's bones are not the layout's: {missing[:5]}")
        self.bind = np.linalg.inv(mesh.inverse_bind)
        heads = np.array([self.layout.bone(name).head for name in names])
        self.to_file, self.miss = fit_frame(heads, np.array([self.bind[mesh.bones.index(name)][:3, 3] for name in names]))
        self.to_rig = np.linalg.inv(self.to_file)
        self.points = mesh.positions @ self.to_rig[:3, :3].T + self.to_rig[:3, 3]
        self.height = float(landmarks["height"])
        self.ground = float(landmarks["ground_offset"])
        self.root_head = np.asarray(self.layout.bone("Root").head, float)
        dominant = np.asarray(mesh.bones)[mesh.joints[np.arange(len(mesh.joints)), np.argmax(mesh.weights, axis=1)]]
        self.dominant = dominant.astype(str)
        self.torso = np.isin(self.dominant, TORSO)

    def deltas(self, pose: dict, lift: float = 0.0, shift: float = 0.0) -> np.ndarray:
        """(B, 4, 4) in the mesh's bone order: how each bone moves from rest, in the rig's frame."""

        out: Dict[str, np.ndarray] = {}
        for bone in self.layout.bones:
            if bone.parent is None:
                out[bone.name] = _shift((shift, 0.0, lift)) @ whole_turn(pose, self.landmarks, self.root_head)
            else:
                out[bone.name] = out[bone.parent] @ _about(np.asarray(bone.head, float), _turn(pose.get(bone.name) or []))
        return np.stack([out[name] for name in self.mesh.bones])

    def skinned(self, deltas: np.ndarray) -> np.ndarray:
        mesh = self.mesh
        moved = np.zeros_like(self.points)
        for k in range(mesh.joints.shape[1]):
            weight = mesh.weights[:, k]
            used = weight > 0
            m = deltas[np.clip(mesh.joints[used, k], 0, None)]
            moved[used] += weight[used, None] * (np.einsum("vij,vj->vi", m[:, :3, :3], self.points[used]) + m[:, :3, 3])
        loose = mesh.weights.sum(axis=1) == 0
        moved[loose] = self.points[loose]
        return moved

    def frame(self, style: str, frame: float, keep_spot: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray]:
        """(deltas, points) of an authoring frame, set on the ground as `author_action` sets it: the lowest point at the ground's height
        and, for a death (`keep_spot`, the standing torso's middle across), the torso over the spot it stood on."""

        pose = ql.pose_at(style, frame, self.layout)
        points = self.skinned(self.deltas(pose))
        lift = self.ground - float(points[:, 2].min())
        shift = keep_spot - float(points[self.torso, 0].mean()) if keep_spot is not None else 0.0
        deltas = self.deltas(pose, lift, shift)
        return deltas, self.skinned(deltas)

    def lowest(self, style: str, frame: float) -> Dict[str, float]:
        points = self.skinned(self.deltas(ql.pose_at(style, frame, self.layout)))
        return {name: float(points[self.dominant == name, 2].min()) for name in np.unique(self.dominant)}

    def tune_collapse(self, style: str) -> dict:
        """`quadruped_rig.tune_collapse`: the death's side, roll and rest, chosen on its final pose."""

        landmarks = self.landmarks
        last = ql.frame_count(style) - 1
        winged = bool(landmarks.get("wings"))
        thin = ("Ear_", qw.WING_PREFIX, "Tail_") if winged else ("Ear_",)

        def evaluate(roll: float, lift: float):
            landmarks["death"] = {"roll": roll, "neck_lift": lift, **({"leg_drop": 0.0, "side_search": True} if winged else {})}
            lowest = {name: z for name, z in self.lowest(style, last).items() if not name.startswith(thin)}
            torso = min(lowest.get(name, math.inf) for name in TORSO)
            return (torso - min(lowest.values())) / self.height, min(lowest, key=lowest.get)

        chosen = ql.choose_collapse(evaluate, ql.roll_limits(landmarks))
        landmarks["death"] = {"roll": chosen["roll"], "neck_lift": chosen["neck_lift"]}
        if winged:
            def rest(**parts: float) -> Dict[str, float]:
                landmarks["death"] = {"roll": chosen["roll"], "neck_lift": chosen["neck_lift"], **parts}
                lowest = self.lowest(style, last)
                torso = min(lowest.get(name, math.inf) for name in TORSO)

                def gap(prefixes) -> float:
                    return (min((z for name, z in lowest.items() if name.startswith(prefixes)), default=torso) - torso) / self.height

                outer = tuple(name for name in lowest if name.startswith(qw.WING_PREFIX + qw.lower_side(chosen["roll"])) and name.endswith(f"_{qw.WING_BONES}"))
                return {"legs": gap(("Front_", "Rear_")), "wings": gap(outer) if outer else 0.0, "tail": gap("Tail_"), "head": gap("Head")}

            laid = ql.choose_winged_rest(rest)
            landmarks["death"].update(laid)
            chosen = {**chosen, **laid}
        return chosen


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------


def export_frames(style: str) -> int:
    """How many frames the route exports for a style: its authoring frames at 24 a second, resampled to 30 (a loop keeps its last frame,
    the copy of its first)."""

    total = ql.frame_count(style)
    return int(round(total * EXPORT_FPS / AUTHOR_FPS)) + (1 if style in ql.LOOPING else 0)


def _quaternion(matrix: np.ndarray) -> Tuple[float, float, float, float]:
    """A rotation matrix as x, y, z, w."""

    m = matrix
    trace = m[0, 0] + m[1, 1] + m[2, 2]
    if trace > 0:
        s = 2.0 * math.sqrt(trace + 1.0)
        q = ((m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s, 0.25 * s)
    else:
        i = int(np.argmax([m[0, 0], m[1, 1], m[2, 2]]))
        j, k = (i + 1) % 3, (i + 2) % 3
        s = 2.0 * math.sqrt(max(1e-12, 1.0 + m[i, i] - m[j, j] - m[k, k]))
        q = [0.0, 0.0, 0.0, (m[k, j] - m[j, k]) / s]
        q[i] = 0.25 * s
        q[j] = (m[j, i] + m[i, j]) / s
        q[k] = (m[k, i] + m[i, k]) / s
    return tuple(float(v) for v in q)


def locals_of(stage: Stage, deltas: np.ndarray) -> List[Tuple[np.ndarray, Tuple[float, float, float, float], float]]:
    """A frame's bone transforms relative to their parents in the file's frame, as (translation, quaternion x y z w, scale)."""

    world = np.einsum("ij,bjk,kl,blm->bim", stage.to_file, deltas, stage.to_rig, stage.bind)
    out = []
    for index, parent in enumerate(stage.mesh.parents):
        local = world[index] if parent < 0 else np.linalg.inv(world[parent]) @ world[index]
        scale = float(np.cbrt(abs(np.linalg.det(local[:3, :3]))))
        out.append((local[:3, 3].copy(), _quaternion(local[:3, :3] / scale), scale))
    return out


def _blend(first, second, share: float):
    """Two frames' bone rows mixed as the exporter's resampling mixes two keyed frames: straight between the translations and along the
    shorter arc between the rotations."""

    out = []
    for (t0, q0, s0), (t1, q1, s1) in zip(first, second):
        q0, q1 = np.asarray(q0), np.asarray(q1)
        if float(q0 @ q1) < 0:
            q1 = -q1
        q = (1.0 - share) * q0 + share * q1
        out.append(((1.0 - share) * t0 + share * t1, tuple(float(v) for v in q / np.linalg.norm(q)), (1.0 - share) * s0 + share * s1))
    return out


def _grounded(stage: Stage, rows):
    """The rows with the root moved so the lowest point of the skin is on the ground: the route sets every exported frame down again, a
    mixed frame included (on the Tripo dragon a mixed frame of the walk otherwise sank a hoof 0.24% of the height)."""

    mesh = stage.mesh
    world = np.zeros((len(rows), 4, 4))
    for index, parent in enumerate(mesh.parents):
        t, q, scale = rows[index]
        local = np.eye(4)
        local[:3, :3] = pdx_deform._quaternion_matrices(np.asarray([q]))[0] * scale
        local[:3, 3] = t
        world[index] = local if parent < 0 else world[parent] @ local
    deltas = np.einsum("ij,bjk,bkl,lm->bim", stage.to_rig, world, mesh.inverse_bind, stage.to_file)
    lift = stage.ground - float(stage.skinned(deltas)[:, 2].min())
    move = stage.to_file[:3, :3] @ np.array([0.0, 0.0, lift])
    return [(t + move, q, scale) if mesh.parents[index] < 0 else (t, q, scale) for index, (t, q, scale) in enumerate(rows)]


def author(stage: Stage, style: str, times: Optional[Sequence[float]] = None, collapse: Optional[dict] = None):
    """(rows, what a death's search chose): per export frame, each bone's (translation, quaternion, scale) under its parent in the file's
    frame. The rig keys every authoring frame (24 a second) and the export samples those keys 30 times a second, so a frame between two
    keys is their mix. `times` (0 to 1) gives those moments only, each posed exactly. `collapse` fixes a death's side and rest instead of
    searching for them."""

    style = ql.stance_style(style, stage.landmarks)
    total = ql.frame_count(style)
    last = total if style in ql.LOOPING else total - 1
    dying = style in ("quadruped_collapse", "winged_collapse")
    tuned = None
    if dying and collapse:
        stage.landmarks["death"] = dict(collapse)
        tuned = dict(collapse)
    elif dying:
        tuned = stage.tune_collapse(style)
    keep_spot = None
    if dying:
        keep_spot = float(stage.skinned(stage.deltas(ql.pose_at(style, 0, stage.layout)))[stage.torso, 0].mean())
    if times is not None:
        return [locals_of(stage, stage.frame(style, float(t) * last, keep_spot)[0]) for t in times], tuned
    keys = [locals_of(stage, stage.frame(style, frame, keep_spot)[0]) for frame in range(last + 1)]
    rows = []
    for index in range(export_frames(style)):
        at = min(float(last), index * AUTHOR_FPS / EXPORT_FPS)
        low = min(int(math.floor(at + 1e-9)), last)
        rows.append(keys[low] if at - low < 1e-9 or low == last else _grounded(stage, _blend(keys[low], keys[low + 1], at - low)))
    return rows, tuned


def _prop(name: str, kind: str, values) -> bytes:
    data = b"!" + struct.pack("<B", len(name)) + name.encode("latin-1") + kind.encode() + struct.pack("<i", len(values))
    if kind == "i":
        return data + struct.pack(f"<{len(values)}i", *values)
    if kind == "f":
        return data + struct.pack(f"<{len(values)}f", *values)
    for value in values:
        encoded = value.encode("latin-1") + b"\0"
        data += struct.pack("<i", len(encoded)) + encoded
    return data


def _obj(name: str, depth: int) -> bytes:
    return b"[" * depth + name.encode("latin-1") + b"\0"


def write_anim(path: Path, bones: Sequence[str], rows: Sequence[Sequence[tuple]], fps: float = EXPORT_FPS) -> None:
    """An `.anim` of the frames' rows (`author`), in io_pdx_mesh's layout: every joint keyed in translation, rotation and scale."""

    data = b"@@b@" + _obj("info", 1) + _prop("sa", "i", [len(rows)]) + _prop("j", "i", [len(bones)]) + _prop("fps", "f", [fps])
    for index, name in enumerate(bones):
        t, q, s = rows[0][index]
        data += _obj(name, 2) + _prop("sa", "s", ["tqs"]) + _prop("t", "f", list(t)) + _prop("q", "f", list(q)) + _prop("s", "f", [s])
    t_all, q_all, s_all = [], [], []
    for row in rows:
        for t, q, s in row:
            t_all += [float(v) for v in t]
            q_all += list(q)
            s_all.append(s)
    data += _obj("samples", 1) + _prop("t", "f", t_all) + _prop("q", "f", q_all) + _prop("s", "f", s_all)
    Path(path).write_bytes(data)


# ---------------------------------------------------------------------------------------------
# Plans
# ---------------------------------------------------------------------------------------------


class Settings:
    """Module constants changed for one clip and put back after it (`{"quadruped_wings.MANTLE": {...}}`)."""

    def __init__(self, changes: Optional[dict]):
        self.changes = changes or {}
        self.saved: List[Tuple[object, str, object]] = []

    def __enter__(self):
        for key, value in self.changes.items():
            module_name, _dot, name = key.rpartition(".")
            module = MODULES[module_name]
            if not hasattr(module, name):
                raise KeyError(f"{key} is not a constant of {module_name}")
            old = getattr(module, name)
            self.saved.append((module, name, copy.deepcopy(old)))
            if isinstance(old, dict) and isinstance(value, dict):
                setattr(module, name, {**old, **value})
            else:
                setattr(module, name, tuple(value) if isinstance(old, tuple) and isinstance(value, list) else value)
        return self

    def __exit__(self, *_exc):
        for module, name, old in reversed(self.saved):
            setattr(module, name, old)
        return False


def role_styles(unit_type: str) -> Dict[str, str]:
    """Each role's Blender style for a unit type (`config/unit_types.json`), the quadruped defaults otherwise."""

    config = json.loads((PIPELINE_ROOT / "config" / "unit_types.json").read_text(encoding="utf-8"))

    def find(value: object) -> Optional[dict]:
        if isinstance(value, dict):
            entry = value.get(unit_type)
            if isinstance(entry, dict) and isinstance(entry.get("roles"), dict):
                return entry["roles"]
            for item in value.values():
                inner = find(item)
                if inner is not None:
                    return inner
        return None

    roles = find(config) or {}
    return {role: str((roles.get(role) or {}).get("blender") or ql.DEFAULT_STYLE[role]) for role in ROLES}


def write_folder(folder: Path, landmarks: dict, out: Path, clips: Sequence[dict]) -> List[dict]:
    """Copy the unit's mesh and textures to `out` and write each clip of the plan as `<stem>_<name>.anim`."""

    folder, out = Path(folder), Path(out)
    mesh_path = sorted(folder.glob("*.mesh"))[0]
    out.mkdir(parents=True, exist_ok=True)
    for path in folder.iterdir():
        if path.suffix.lower() in (".mesh", ".dds"):
            shutil.copy2(path, out / path.name)
    mesh = pdx_deform.load_mesh(mesh_path)
    report = []
    for clip in clips:
        with Settings(clip.get("set")):
            stage = Stage(mesh, copy.deepcopy(landmarks))
            frames, tuned = author(stage, clip["style"], clip.get("times"), clip.get("collapse"))
            target = out / f"{mesh_path.stem}_{clip['name']}.anim"
            write_anim(target, mesh.bones, frames)
            report.append({"name": clip["name"], "style": clip["style"], "frames": len(frames), "frame_fit": round(stage.miss / stage.height, 5),
                           **({"collapse": tuned} if tuned else {})})
    return report


def compare(folder: Path, out: Path) -> Dict[str, float]:
    """Per clip in both folders, the farthest any vertex lies from where the other folder's clip puts it, as a share of the height."""

    mesh = pdx_deform.load_mesh(sorted(Path(folder).glob("*.mesh"))[0])
    height = float(np.ptp(mesh.positions[:, 1])) or 1.0
    result = {}
    for path in sorted(Path(out).glob("*.anim")):
        other = Path(folder) / path.name
        if not other.exists():
            continue
        a, b = pdx_deform.load_anim(path), pdx_deform.load_anim(other)
        ma, mb = pdx_deform.skinning_matrices(mesh, a), pdx_deform.skinning_matrices(mesh, b)
        worst = 0.0
        for frame in range(min(len(ma), len(mb))):
            worst = max(worst, float(np.linalg.norm(pdx_deform.skin(mesh, ma[frame]) - pdx_deform.skin(mesh, mb[frame]), axis=1).max()))
        result[path.stem] = round(worst / height, 5)
        if len(ma) != len(mb):
            result[path.stem + ":frames"] = float(len(ma) - len(mb))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", type=Path, help="a unit folder a run exported (.mesh, .dds)")
    parser.add_argument("--landmarks", type=Path, required=True, help="the run's job root, or a JSON file of the rig's landmarks")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--plan", type=Path, help="JSON: {\"clips\": [{\"name\", \"style\", \"set\", \"times\"}]}")
    parser.add_argument("--unit-type", default="winged_quadruped", help="names the six roles' styles when there is no plan")
    parser.add_argument("--compare", action="store_true", help="measure the written clips against the folder's own")
    parser.add_argument("--sheet", action="store_true", help="render the clips with tripo/clip_sheet.py (starts Blender: run it through the gate)")
    parser.add_argument("--views", nargs="+", default=["hoi4", "front", "left"])
    parser.add_argument("--frames", type=int, default=6)
    parser.add_argument("--size", type=int, default=320)
    args = parser.parse_args()
    if args.plan:
        clips = json.loads(args.plan.read_text(encoding="utf-8"))["clips"]
    else:
        clips = [{"name": role, "style": style} for role, style in role_styles(args.unit_type).items()]
    landmarks = read_landmarks(args.landmarks)
    report = {"clips": write_folder(args.folder, landmarks, args.out, clips)}
    if args.compare:
        report["compare"] = compare(args.folder, args.out)
    print(json.dumps(report, indent=1))
    if args.sheet:
        command = [sys.executable, "-B", str(Path(__file__).with_name("clip_sheet.py")), str(args.out), "--roles", *[clip["name"] for clip in clips],
                   "--frames", str(args.frames), "--views", *args.views, "--size", str(args.size), "--out", str(args.out / "preview.png")]
        return subprocess.run(command, check=False).returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
