"""A retreat that looks back over the shoulder (`"retreat_pose": "look_back"` in a job's `tripo` block). No Blender.

A fresh review of the demon (run demon_f, 2026-11-19) read its retreat at game size as its move: both run in place with the same outline,
and "nothing reads as fleeing (no turn, no look back)". A unit's clips play in place and the game turns the whole entity toward where it
goes, so a turn of the body inside the clip is all that can say "running away". The route turns the upper body and the head back toward
the side the unit flees from, by rule, on the exported clip:

1. Each of `TURN` (the chest, the neck, the head) turns about the world's up axis by its share of `LOOK_BACK` degrees, the chest least
   and the head most, so the face looks back over the left shoulder. Each bone takes the turn in the world, applied from the chest
   out, so a child carries its parent's share and adds its own.
2. The turn is blended in by a weight that rises over the first `RAMP_SHARE` of the clip, holds, and falls over the last, so the clip
   starts and ends on its own first pose and its loop does not pop. The legs and the hips keep the clip's own stride.

The wings follow the chest's turn, folded along the back by the retreat's wing rule (lib/tripo_chains.WING_ROLES).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np

from . import pdx_deform, tripo_pose
from .pdx_binary import read
from .tripo_guard import _set_world, _unit

# Degrees the face turns back from the unit's front, over the chest, the neck and the head together. A look over the shoulder that the
# game camera sees: at 55 degrees down and 60 pixels tall, the head's turn is a few pixels, and the chest's turn widens the shoulders'
# outline. The human neck turns about 80 degrees, the spine adds 20 to 30.
LOOK_BACK = 90.0
TURN = (("Spine02", 0.25), ("neck", 0.3), ("Head", 0.45))
RAMP_SHARE = 0.3


def ramp(frames: int) -> np.ndarray:
    t = np.linspace(0.0, 1.0, frames) if frames > 1 else np.zeros(1)
    up = np.clip(t / RAMP_SHARE, 0.0, 1.0)
    down = np.clip((1.0 - t) / RAMP_SHARE, 0.0, 1.0)
    weight = np.minimum(up, down)
    return weight * weight * (3.0 - 2.0 * weight)


def look_back(mesh_path: Path, anim_path: Path) -> Dict[str, object]:
    """Turn the exported retreat's chest, neck and head back over the left shoulder (see the module text), in place."""

    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)
    turned = [(name, share) for name, share in TURN if name in mesh.bones]
    if not any(name == "Head" for name, _share in turned):
        return {"changed": False, "note": "the rig lacks the kit's head bone"}
    weight = ramp(anim.frames)
    channels = {name: {key: value.copy() for key, value in channel.items()} for name, channel in anim.channels.items()}
    up = np.array([0.0, 1.0, 0.0])
    for frame in range(anim.frames):
        w = float(weight[frame])
        if w <= 0.0:
            continue
        for name, share in turned:
            rotations, _positions = tripo_pose._world_rotations(mesh, pdx_deform.Animation(anim.fps, anim.frames, channels))
            index = mesh.bones.index(name)
            _set_world(channels, mesh, name, frame, tripo_pose._axis_angle(_unit(up), LOOK_BACK * share * w) @ rotations[frame, index], rotations)
    data = bytearray(Path(anim_path).read_bytes())
    info = read(anim_path).child("info")
    keyed = [joint.name for joint in info.children if "q" in str((joint.properties.get("sa") or [""])[0])]
    joints = [name for name, _share in turned if name in keyed]
    tripo_pose._write_rotations(data, keyed, joints, pdx_deform.Animation(anim.fps, anim.frames, channels), (weight > 0).astype(float))
    Path(anim_path).write_bytes(bytes(data))
    return {"changed": True, "frames": int((weight > 0).sum()), "look_back_degrees": LOOK_BACK, "joints": joints}
