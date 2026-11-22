"""A humanoid's idle posed hunched with the head forward (`"idle_pose": "hunch"` in a job's `tripo` block). No Blender.

Two fresh reviews of the D-94 zombie (run zombie_d, 2026-11-21) read its idle at game size as an ordinary live soldier standing. Tripo's
text-to-motion idle ("A zombie soldier stands in place, idle. He is slightly hunched") bends the torso 2 to 4 degrees from upright, so at
map zoom the outline is upright. A zombie reads through its outline, so the route poses the hunch by rule on the exported idle, before the
weights are fitted:

1. The spine bends forward, shared evenly over Spine, Spine01 and Spine02, about the body's lateral axis, and the neck turns back up by
   `NECK_BACK` of that bend, so the head juts forward and the face looks ahead instead of at the ground.
2. The bend is the smallest, in steps of `STEP` degrees up to `MAX_BEND`, that leans the line from the hips to the head `TARGET` degrees
   forward of upright on the clip's first frame (a body whose neck takes back most of the bend may stop short at `MAX_BEND`, and
   the record says so). Tripo's idle leans back at the waist, so the bend it needs depends on the clip: run zombie_d's
   idle took 36 degrees of spine to lean that line 19 degrees, about the lean of its lunge at the peak (23 to 27 degrees).
3. Every frame takes the same turn, so the idle's loop is unchanged. The hips, legs and arms keep the clip's own motion: the arms hang from
   the bent torso.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np

from . import pdx_deform, tripo_guard, tripo_pose
from .pdx_binary import read

TARGET = 20.0  # degrees the hips-to-head line leans forward of upright
STEP = 2.0
MAX_BEND = 48.0  # degrees of spine bend at most
NECK_BACK = 0.6  # share of the bend the neck turns back up
SPINE = ("Spine", "Spine01", "Spine02")
NECK = ("neck", "Neck")


def lean(mesh, anim, front: np.ndarray, frame: int = 0) -> float:
    """Degrees the line from the hips to the head leans forward of upright at `frame` (negative when it leans back)."""

    _rotations, positions = tripo_pose._world_rotations(mesh, anim)
    line = positions[frame, mesh.bones.index("Head")] - positions[frame, mesh.bones.index("Hips")]
    return float(np.degrees(np.arctan2(line @ front, line[1])))


def _bent(mesh, anim, turns, lateral: np.ndarray, frames) -> Dict[str, Dict[str, np.ndarray]]:
    channels = {name: {key: value.copy() for key, value in channel.items()} for name, channel in anim.channels.items()}
    for frame in frames:
        for name, angle in turns:
            rotations, _positions = tripo_pose._world_rotations(mesh, pdx_deform.Animation(anim.fps, anim.frames, channels))
            i = mesh.bones.index(name)
            tripo_guard._set_world(channels, mesh, name, frame, tripo_pose._axis_angle(lateral, angle) @ rotations[frame, i], rotations)
    return channels


def hunch_idle(mesh_path: Path, anim_path: Path, front: np.ndarray, target: float = TARGET) -> Dict[str, object]:
    """Pose the exported idle hunched with the head forward (see the module text), in place. `front` is the unit's facing."""

    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)
    spine = [name for name in SPINE if name in mesh.bones]
    neck = next((name for name in NECK if name in mesh.bones), None)
    if not spine or "Hips" not in mesh.bones or "Head" not in mesh.bones:
        return {"changed": False, "note": "the rig lacks the kit's hips, spine or head bones"}
    up = np.array([0.0, 1.0, 0.0])
    front = tripo_guard._unit(np.asarray(front, float) - (np.asarray(front, float) @ up) * up)
    lateral = tripo_guard._unit(np.cross(up, front))  # bending about this axis by a positive angle tips the top toward the front
    if float(np.cross(lateral, up) @ front) < 0:
        lateral = -lateral

    def turns(degrees: float):
        return [(name, degrees / len(spine)) for name in spine] + ([(neck, -degrees * NECK_BACK)] if neck else [])

    before = lean(mesh, anim, front)
    if before >= target:
        return {"changed": False, "lean_before": round(before, 1), "note": "the idle already leans forward that far"}
    degrees = STEP
    while degrees < MAX_BEND:
        trial = pdx_deform.Animation(anim.fps, anim.frames, _bent(mesh, anim, turns(degrees), lateral, [0]))
        if lean(mesh, trial, front) >= target:
            break
        degrees += STEP
    degrees = min(degrees, MAX_BEND)
    channels = _bent(mesh, anim, turns(degrees), lateral, range(anim.frames))
    after = lean(mesh, pdx_deform.Animation(anim.fps, anim.frames, channels), front)
    data = bytearray(Path(anim_path).read_bytes())
    info = read(anim_path).child("info")
    keyed = [joint.name for joint in info.children if "q" in str((joint.properties.get("sa") or [""])[0])]
    joints = [name for name, _angle in turns(degrees) if name in keyed]
    tripo_pose._write_rotations(data, keyed, joints, pdx_deform.Animation(anim.fps, anim.frames, channels), np.ones(anim.frames))
    Path(anim_path).write_bytes(bytes(data))
    return {"changed": True, "frames": int(anim.frames), "bend_degrees": degrees, "neck_back_degrees": round(degrees * NECK_BACK, 1),
            "lean_before": round(before, 1), "lean_after": round(after, 1), "reached": after >= target, "joints": joints}
