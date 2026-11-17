"""The route's last pose step: keep every held weapon and shield out of the body in every frame of every clip, on the exported files.

The grip stage clears the weapon on the rigged GLB, and the prepare stage clears the frames its loop settle adds. The route then retargets
every clip onto its own mesh in Blender, resamples it to the game's 30 frames a second and rewrites the skin weights, and the exported clips
put the prop back in the body (round 4: the ogre's chop had its club inside the body in frames 65 to 90, up to 19.1%, with the grip report
clean at 0.57%, and the dwarf's glaive was inside it in 24% to 36% of its points in the idle and the attack). Measured offline on the raw
export of the dwarf, before the neck lift, the weight smoothing and fit and the grounding, the same frames already failed by the same shares, so the
loss happens in the retarget and the export. This step measures what the game loads and clears it again, whatever the cause.

For each held part (a weapon or a shield on its own bone, a child of a hand) and each clip the part is not let go in: the same solve as the grip
stage (`lib/tripo_clearance.clear_clip`: the smallest turn of the hand about the wrist, per frame, smoothed) on the posed `.mesh` of the exported
files, judged by the check's own test (the held points outside the grip zone, deeper than `MARGIN_SHARE` inside the body, the other held part
counting as no part of the body, the held part below the body's lowest point). The turns are written into the hand's rotation samples of the
`.anim` as a world turn about the hand's own joint, so the hand's children (the prop, the fingers) follow. A clip that passes is copied as it is.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

from lib import pdx_deform, pdx_motion, tripo_clearance as CL, tripo_pose
from lib.pdx_binary import read

UP_AXIS = 1  # the exported files' up axis
GRIP_ZONE_SHARE = 0.12  # as the check (tripo/tripo_checks.WEAPON_GRIP_ZONE_SHARE): held points this near the part's own joint at rest are the grip
MAX_POINTS = 600
MAX_PASSES = 2  # a hand turned for one part can move the other part's frames a little: one more pass


@dataclass
class PropClearance:
    part: str
    hand: str
    changed: bool = False
    frames_changed: int = 0
    max_degrees: float = 0.0
    worst_before: float = 0.0
    worst_after: float = 0.0
    failed_frames: List[int] = field(default_factory=list)
    note: str = ""


def _frames_of(anim: pdx_deform.Animation) -> int:
    return max(anim.frames, 1)


def part_split(mesh: pdx_deform.SkinnedMesh, bone: str, others: Sequence[str]):
    """(held mask, the body's triangles renumbered over the body's own vertices, the body mask), the check's own split (tripo/tripo_checks.weapon_split)."""

    index = mesh.bones.index(bone)
    held = (pdx_deform.dominant_bones(mesh) == index) & (mesh.weights.max(axis=1) > 0.99)
    away = held.copy()
    for other in others:
        if other and other in mesh.bones:
            away |= (pdx_deform.dominant_bones(mesh) == mesh.bones.index(other)) & (mesh.weights.max(axis=1) > 0.99)
    body = ~away
    keep = body[mesh.triangles].all(axis=1)
    remap = np.cumsum(body) - 1
    return held, remap[mesh.triangles[keep]], body


def holding_hand(mesh: pdx_deform.SkinnedMesh, bone: str) -> Optional[str]:
    """The hand a part's own bone hangs from, or None when the part has no bone of its own under a hand."""

    if bone not in mesh.bones:
        return None
    parent = int(mesh.parents[mesh.bones.index(bone)])
    if 0 <= parent < len(mesh.bones) and mesh.bones[parent].endswith("Hand") and mesh.bones[parent] != bone:
        return mesh.bones[parent]
    return None


def _rotation_vectors_to_quaternions(world: np.ndarray, parent: int, hand: int, q: np.ndarray, rotvecs: np.ndarray) -> np.ndarray:
    """The hand's new local rotations (x, y, z, w) after each frame's world turn about the hand's joint."""

    out = q.copy()
    local = pdx_deform._quaternion_matrices(q)
    for frame in range(len(q)):
        vector = rotvecs[frame]
        if float(np.linalg.norm(vector)) < 1e-9:
            continue
        parent_rotation = world[frame, parent, :3, :3] if parent >= 0 else np.eye(3)
        scale = np.cbrt(max(abs(np.linalg.det(parent_rotation)), 1e-12))
        parent_rotation = parent_rotation / scale
        turned = parent_rotation.T @ CL.rotvec_matrix(vector) @ parent_rotation @ local[frame]
        new = tripo_pose._quaternion_from_matrix(turned)
        if float(new @ q[frame]) < 0:
            new = -new
        out[frame] = new
    return out


def clear_part(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, bone: str, others: Sequence[str], keyed: Sequence[str]):
    """(the clip with the hand's turns applied, the record). The clip itself when the part is clear in every frame."""

    hand_name = holding_hand(mesh, bone)
    record = PropClearance(bone, hand_name or "")
    if hand_name is None or hand_name not in keyed:
        record.note = "the part has no bone of its own under a keyed hand"
        return anim, record
    held, triangles, body = part_split(mesh, bone, others)
    if held.sum() < 50:
        record.note = "fewer than 50 vertices"
        return anim, record
    height = float(mesh.height)
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    world = matrices @ np.linalg.pinv(mesh.inverse_bind)[None]
    hand = mesh.bones.index(hand_name)
    rest = pdx_motion.rest_joints(mesh)
    indices = np.nonzero(held)[0]
    indices = indices[np.linspace(0, len(indices) - 1, min(MAX_POINTS, len(indices))).astype(int)]
    grip = rest[mesh.bones.index(bone)]
    free = np.linalg.norm(mesh.positions[indices] - grip, axis=1) > GRIP_ZONE_SHARE * height
    weapon_frames, body_frames, pivots = [], [], []
    for frame in range(_frames_of(anim)):
        posed = pdx_deform.skin(mesh, matrices[frame])
        weapon_frames.append(posed[indices][free])
        body_frames.append(posed[body])
        pivots.append(world[frame, hand, :3, 3])
    result = CL.clear_clip(weapon_frames, pivots, body_frames, triangles, height, ground_axis=UP_AXIS)
    record.worst_before = float(max(result["before"]))
    record.worst_after = float(max(result["after"]))
    record.failed_frames = [int(i) for i in result["failed"]]
    if record.worst_before <= CL.TARGET:
        return anim, record
    rotvecs = result["rotvecs"]
    q = anim.channels[hand_name]["q"]
    channels = {name: dict(channel) for name, channel in anim.channels.items()}
    channels[hand_name] = dict(channels[hand_name], q=_rotation_vectors_to_quaternions(world, int(mesh.parents[hand]), hand, q, rotvecs))
    record.changed = True
    record.frames_changed = int(result["frames_changed"])
    record.max_degrees = round(float(result["max_degrees"]), 1)
    return pdx_deform.Animation(anim.fps, anim.frames, channels), record


def clear_clip_file(mesh_path: Path, anim_path: Path, out_path: Path, parts: Sequence[Dict[str, str]], role: str = "") -> Dict[str, dict]:
    """Write `out_path`: `anim_path` with every held part kept out of the body. `parts` lists {"bone", "release_roles"} for the weapon, then the
    shield. A part the unit lets go of in `role` is left to its fall. Returns the record per part."""

    data = bytearray(Path(anim_path).read_bytes())
    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)
    info = read(anim_path).child("info")
    keyed = [joint.name for joint in info.children if "q" in str((joint.properties.get("sa") or [""])[0])]
    bones = [part["bone"] for part in parts if part.get("bone") and role not in (part.get("release_roles") or [])]
    everyone = [part["bone"] for part in parts if part.get("bone")]
    records: Dict[str, dict] = {}
    changed_hands: List[str] = []
    for _pass in range(MAX_PASSES):
        again = False
        for bone in bones:
            result, record = clear_part(mesh, anim, bone, [b for b in everyone if b != bone], keyed)
            if record.changed:
                anim = result
                again = True
                if record.hand not in changed_hands:
                    changed_hands.append(record.hand)
            first = records.get(bone)
            if first and first["changed"] and not record.changed:
                # a later pass found the part clear: keep what the pass that turned the hand did, and the share it left
                first["worst_after"] = record.worst_after
                first["failed_frames"] = record.failed_frames
            elif first and record.changed:
                record.worst_before = first["worst_before"]
                record.frames_changed = max(record.frames_changed, first["frames_changed"])
                record.max_degrees = max(record.max_degrees, first["max_degrees"])
                records[bone] = dict(record.__dict__)
            else:
                records[bone] = dict(record.__dict__)
        if not again:
            break
    if changed_hands:
        everything = np.ones(max(anim.frames, 1))
        tripo_pose._write_rotations(data, keyed, changed_hands, anim, everything)
    Path(out_path).write_bytes(bytes(data))
    return records
