"""A defend posed as a guard (`"defend_pose": "guard"` in a job's `tripo` block). No Blender.

A fresh review of the demon (run demon_c, 2026-11-19) read its defend at game size as its attack: `hit_to_body_01` twists the torso and
thrusts one arm out, as `box_01` does at its peak, and no guard reads. None of the rigged GLB's clips raises both arms before the face
(measured with `tripo/pose_check.py`: `hit_to_body_01` and `hit_to_stomach` raise the holding hand 0.05 of the height above the chest, a
guard needs both hands at the face). So the route poses the guard by rule on the exported clip, before the weights are fitted:

1. The torso (Spine, Spine01, Spine02) turns toward the unit's own stance, the idle's first frame, so the twist goes, and then leans back
   by `LEAN_BACK` degrees about the body's lateral axis: a body bracing against a blow.
2. Each upper arm points forward and down (`UPPER_ARM`, in the torso's own frame), each forearm up and in (`FOREARM`), so both hands come
   up before the face. Each bone takes the smallest turn onto its direction.
3. All of it is blended in by a weight that rises over the first `RAMP_SHARE` of the clip and falls over the last, so the clip still starts
   and ends on its own first pose and its loop does not pop. The hips and legs keep the clip's own recoil.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, Optional

import numpy as np

from . import pdx_deform, tripo_pose
from .pdx_binary import read

LEAN_BACK = 10.0  # degrees the braced torso leans back
RAMP_SHARE = 0.25
# Directions in the torso's frame: (forward, up, out toward the arm's side). A boxer's high guard: the upper arm forward and a little down
# and out, the forearm up and in, the hands before the face.
UPPER_ARM = (0.8, -0.45, 0.4)
FOREARM = (0.35, 0.9, -0.3)
TORSO = ("Spine", "Spine01", "Spine02")
ARMS = {"Left": ("LeftArm", "LeftForeArm", "LeftHand"), "Right": ("RightArm", "RightForeArm", "RightHand")}


def ramp(frames: int) -> np.ndarray:
    t = np.linspace(0.0, 1.0, frames) if frames > 1 else np.zeros(1)
    up = np.clip(t / RAMP_SHARE, 0.0, 1.0)
    down = np.clip((1.0 - t) / RAMP_SHARE, 0.0, 1.0)
    weight = np.minimum(up, down)
    return weight * weight * (3.0 - 2.0 * weight)


def _unit(v: np.ndarray) -> np.ndarray:
    return v / max(float(np.linalg.norm(v)), 1e-12)


def _arc(a: np.ndarray, b: np.ndarray, share: float) -> np.ndarray:
    """The rotation matrix turning direction `a` toward `b` by `share` of the smallest arc."""

    a, b = _unit(a), _unit(b)
    axis = np.cross(a, b)
    size = float(np.linalg.norm(axis))
    if size < 1e-9:
        return np.eye(3)
    angle = math.degrees(math.atan2(size, float(a @ b))) * share
    return tripo_pose._axis_angle(axis / size, angle)


def _set_world(channels, mesh, name: str, frame: int, world: np.ndarray, rotations: np.ndarray) -> None:
    index = mesh.bones.index(name)
    parent = mesh.parents[index]
    above = rotations[frame, parent] if parent >= 0 else np.eye(3)
    q = tripo_pose._quaternion_from_matrix(above.T @ world)
    old = channels[name]["q"][frame]
    channels[name]["q"][frame] = q if float(q @ old) >= 0 else -q


def guard_defend(mesh_path: Path, anim_path: Path, idle_path: Optional[Path], front: np.ndarray) -> Dict[str, float]:
    """Pose the exported defend clip as a guard (see the module text), in place. `front` is the unit's facing (the mesh's own axes)."""

    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)
    if any(name not in mesh.bones for name in ("Spine02",) + ARMS["Left"] + ARMS["Right"]):
        return {"changed": False, "note": "the rig lacks the kit's chest or arm bones"}
    torso = [name for name in TORSO if name in mesh.bones]
    leaning = "Spine01" if "Spine01" in mesh.bones else torso[0]
    stance = pdx_deform.load_anim(idle_path) if idle_path and Path(idle_path).is_file() else None
    weight = ramp(anim.frames)
    channels = {name: {key: value.copy() for key, value in channel.items()} for name, channel in anim.channels.items()}
    up = np.array([0.0, 1.0, 0.0])
    front = _unit(np.asarray(front, float) - (np.asarray(front, float) @ up) * up)
    lateral = _unit(np.cross(up, front))  # the unit's left, in the mesh's axes
    chest = mesh.bones.index("Spine02")
    rest = np.linalg.inv(mesh.inverse_bind)[:, :3, 3]
    outward = {}  # each arm's side, read from where its shoulder joint sits at rest
    for side, (upper, _fore, _hand) in ARMS.items():
        away = rest[mesh.bones.index(upper)] - rest[chest]
        away = away - (away @ up) * up - (away @ front) * front
        outward[side] = _unit(away) if np.linalg.norm(away) > 1e-9 else (lateral if side == "Left" else -lateral)
    bind = np.linalg.inv(mesh.inverse_bind)[chest][:3, :3]
    chest_rest = bind / np.cbrt(abs(np.linalg.det(bind)))
    for frame in range(anim.frames):
        w = float(weight[frame])
        if w <= 0.0:
            continue
        if stance is not None:
            for name in torso:
                channels[name]["q"][frame] = tripo_pose.slerp(channels[name]["q"][frame], stance.channels[name]["q"][0], w)
        rotations, _positions = tripo_pose._world_rotations(mesh, pdx_deform.Animation(anim.fps, anim.frames, channels))
        body_turn = rotations[frame, chest] @ chest_rest.T
        lean = tripo_pose._axis_angle(body_turn @ lateral, -LEAN_BACK * w)
        _set_world(channels, mesh, leaning, frame, lean @ rotations[frame, mesh.bones.index(leaning)], rotations)
        for side, (upper, fore, hand) in ARMS.items():
            out = outward[side]
            frame_axes = np.stack([front, up, out], axis=1)
            for bone, child, target in ((upper, fore, UPPER_ARM), (fore, hand, FOREARM)):
                rotations, positions = tripo_pose._world_rotations(mesh, pdx_deform.Animation(anim.fps, anim.frames, channels))
                body_turn = rotations[frame, chest] @ chest_rest.T
                i, c = mesh.bones.index(bone), mesh.bones.index(child)
                wanted = body_turn @ frame_axes @ _unit(np.asarray(target, float))
                _set_world(channels, mesh, bone, frame, _arc(positions[frame, c] - positions[frame, i], wanted, w) @ rotations[frame, i], rotations)
    data = bytearray(Path(anim_path).read_bytes())
    info = read(anim_path).child("info")
    keyed = [joint.name for joint in info.children if "q" in str((joint.properties.get("sa") or [""])[0])]
    result = pdx_deform.Animation(anim.fps, anim.frames, channels)
    joints = [name for name in torso + list(ARMS["Left"][:2] + ARMS["Right"][:2]) if name in keyed]
    tripo_pose._write_rotations(data, keyed, joints, result, (weight > 0).astype(float))
    Path(anim_path).write_bytes(bytes(data))
    return {"changed": True, "frames": int((weight > 0).sum()), "lean_back_degrees": LEAN_BACK, "joints": joints}
