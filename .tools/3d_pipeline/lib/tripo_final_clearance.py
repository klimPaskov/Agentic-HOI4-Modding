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
RAMP_DEGREES = 8.0  # the turn added to a hand grows or fades by at most this many degrees a frame (`ramped`), well under the spin rule's 37 and the route's 14 degree snap easing
# The unit's spin check (UNIT-ANIM-SPIN) fails a joint that turns more than vanilla's fastest (37 degrees) in one frame. A turn that cannot be ramped
# (the swing passes through the body in one frame and is clear in the next) is smoothed over more frames until no frame of the hand turns more than this;
# the frames the smoothing leaves in the body are reported and judged by TRIPO-WEAPON-IN-BODY, which fails loudly where a run that stopped would hide it.
MAX_HAND_STEP_DEGREES = 35.0
SMOOTH_RADII = (0, 1, 2, 3, 4, 6, 8)
# A weapon the unit has let go of is cleared by moving it, never by turning the hand: from the frame it came to rest it sits at one place on
# the ground, and the body that settles after it (a death's chest and head laid down) can come to lie in it. The weapon's own bone is shifted
# along the ground by the smallest distance that clears every frame from the ramp on, eased in over the `DROP_RAMP_FRAMES` before it lands.
DROP_RAMP_FRAMES = 8
DROP_STEP_SHARE = 0.02  # the shift grows in steps of this share of the height
DROP_MAX_SHARE = 0.5
DROP_DIRECTIONS = 16
DROP_REST_SHARE = 0.01  # the weapon has landed once its centre stays within this share of the height of where it ends
# The grip stage turns the hand by at most 60 degrees. On the exported files a frame the swing carries through the body can need more: the round 4
# dwarf's idle had its glaive 31% inside the body at frame 73 with the 60 degrees spent. The smallest turn that clears is still the one taken.
MAX_TURN_DEGREES = 90.0
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
    smoothed_over: int = 0  # the radius (frames) the hand's added turn was smoothed over to stay under the spin limit
    max_roll_degrees: float = 0.0  # the part turned about its own long axis where the wrist could not clear it
    max_arm_degrees: float = 0.0  # the upper arm turned about the shoulder, last
    search_bound_reached: bool = False  # a search past the wrist stopped at its bound (lib/tripo_clearance.STAGE_TESTS, BRIDGE_TESTS)


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


def ramped(rotvecs: np.ndarray, needed: Sequence[bool], step_degrees: float = RAMP_DEGREES, clear=None) -> np.ndarray:
    """`rotvecs` with the turn extended into the frames that had none, fading by `step_degrees` a frame, so the hand's added turn never jumps.

    The solve takes the smallest turn that clears each frame, and a turn that starts or ends at a frame (the prop sweeping into the body, or out of it)
    is a step of tens of degrees in one frame, which the unit's own spin check fails (UNIT-ANIM-SPIN). The frames in `needed` (the prop is in the body
    without a turn) keep their turn. Every other frame starts with none and takes the turn of the frame next to it at `step_degrees` less, frame after
    frame, so long as `clear(frame, vector)` says the prop is out of the body with it (a share of that turn is tried when it is not, and none when no
    share is)."""

    step = np.radians(step_degrees)
    out = np.array(rotvecs, float)
    fixed = np.asarray(needed, bool)
    out[~fixed] = 0.0
    for order, side in ((range(1, len(out)), -1), (range(len(out) - 2, -1, -1), 1)):
        for i in order:
            j = i + side
            size = float(np.linalg.norm(out[j]))
            if fixed[i] or size <= step or float(np.linalg.norm(out[i])) >= size - step:
                continue
            wanted = out[j] * ((size - step) / size)
            for share in (1.0, 0.75, 0.5, 0.25):
                if clear is None or clear(i, wanted * share):
                    out[i] = wanted * share
                    break
    return out


def _long_axis(points: np.ndarray) -> np.ndarray:
    """The principal axis of a part's rest points: a weapon's haft, a shield's bar."""

    centred = np.asarray(points, float) - np.mean(points, axis=0)
    _u, _s, vt = np.linalg.svd(centred, full_matrices=False)
    return vt[0]


def _turned(rotation: np.ndarray) -> np.ndarray:
    scale = np.cbrt(max(abs(float(np.linalg.det(rotation))), 1e-12))
    return rotation / scale


def _posed_frames(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, held: np.ndarray, body: np.ndarray, joints: Dict[str, int],
                  can_arm: bool) -> Dict[str, list]:
    """Per frame of the clip: the part's judged points, the body's vertices, the wrist, the grip and the haft's direction, and (with
    `can_arm`) the shoulder with the elbow and the wrist. `joints` names the hand, the part, the elbow and the upper arm by index."""

    height = float(mesh.height)
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    world = matrices @ np.linalg.pinv(mesh.inverse_bind)[None]
    rest_world = np.linalg.pinv(mesh.inverse_bind)
    hand, part, elbow, upper = joints["hand"], joints["part"], joints["elbow"], joints["upper"]
    indices = np.nonzero(held)[0]
    indices = indices[np.linspace(0, len(indices) - 1, min(MAX_POINTS, len(indices))).astype(int)]
    free = np.linalg.norm(mesh.positions[indices] - pdx_motion.rest_joints(mesh)[part], axis=1) > GRIP_ZONE_SHARE * height
    axis_rest = _long_axis(mesh.positions[indices])
    to_rest = np.linalg.inv(_turned(rest_world[part, :3, :3]))
    out: Dict[str, list] = {key: [] for key in ("weapon", "body", "pivots", "grips", "hafts", "shoulders", "arm_joints")}
    out["world"] = world
    for frame in range(_frames_of(anim)):
        posed = pdx_deform.skin(mesh, matrices[frame])
        out["weapon"].append(posed[indices][free])
        out["body"].append(posed[body])
        out["pivots"].append(world[frame, hand, :3, 3])
        out["grips"].append(world[frame, part, :3, 3])
        out["hafts"].append(_turned(world[frame, part, :3, :3]) @ to_rest @ axis_rest)
        if can_arm:
            out["shoulders"].append(world[frame, upper, :3, 3])
            out["arm_joints"].append(np.array([world[frame, elbow, :3, 3], world[frame, hand, :3, 3]]))
    return out


def _written_turns(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, world: np.ndarray, bones, names: Dict[str, str], turns):
    """(the channels with each bone's turn written, the smoothing radius): the turns of the hand, the roll and the arm, smoothed over the
    fewest frames (`SMOOTH_RADII`) that keep every turned joint under `MAX_HAND_STEP_DEGREES` a frame."""

    count = len(turns[0])
    channels = {name: dict(channel) for name, channel in anim.channels.items()}
    for radius in SMOOTH_RADII:
        smooth = [CL.smooth_rotations(v, radius=radius) if radius else v for v in turns]
        # the roll is solved about the haft as the wrist carries it, and the part's bone hangs from the hand: its own turn is that roll
        # taken back through the wrist's turn
        local_roll = np.array([CL.rotvec_matrix(smooth[0][i]).T @ smooth[1][i] for i in range(count)])
        vectors = {names["hand"]: smooth[0], names["part"]: local_roll, names["upper"]: smooth[2]}
        worst = 0.0
        for name, index in bones:
            new_q = _rotation_vectors_to_quaternions(world, int(mesh.parents[index]), index, anim.channels[name]["q"], vectors[name])
            channels[name] = dict(anim.channels[name], q=new_q)
            worst = max([worst] + [tripo_pose.quaternion_turn(new_q[i], new_q[i + 1]) for i in range(len(new_q) - 1)])
        if worst <= MAX_HAND_STEP_DEGREES:
            break
    return channels, smooth, radius


def clear_part(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, bone: str, others: Sequence[str], keyed: Sequence[str]):
    """(the clip with the turns applied, the record, the bones whose rotations changed). The clip itself when the part is clear in every frame.

    The turns come in the grip stage's order (`lib/tripo_clearance.clear_clip_staged`): the hand about the wrist, then the part about its own
    long axis through its joint (when the part's bone is keyed), then the upper arm about the shoulder (when it is keyed), which never lowers a
    hand raised above the shoulder. Each is written into its own bone's rotation samples."""

    hand_name = holding_hand(mesh, bone)
    record = PropClearance(bone, hand_name or "")
    if hand_name is None or hand_name not in keyed:
        record.note = "the part has no bone of its own under a keyed hand"
        return anim, record, []
    held, triangles, body = part_split(mesh, bone, others)
    if held.sum() < 50:
        record.note = "fewer than 50 vertices"
        return anim, record, []
    height = float(mesh.height)
    hand = mesh.bones.index(hand_name)
    elbow = int(mesh.parents[hand])
    upper = int(mesh.parents[elbow]) if elbow >= 0 else -1
    names = {"hand": hand_name, "part": bone, "upper": mesh.bones[upper] if upper >= 0 else ""}
    can_roll = bone in keyed
    can_arm = upper >= 0 and names["upper"] in keyed and names["upper"].endswith("Arm")
    f = _posed_frames(mesh, anim, held, body, {"hand": hand, "part": mesh.bones.index(bone), "elbow": elbow, "upper": upper}, can_arm)
    result = CL.clear_clip_staged(f["weapon"], f["pivots"], f["body"], triangles, height, grips=f["grips"] if can_roll else None,
                                  haft_axes=f["hafts"] if can_roll else None, shoulders=f["shoulders"] if can_arm else None,
                                  arm_joints=f["arm_joints"] if can_arm else None, up_axis=UP_AXIS, max_angle=MAX_TURN_DEGREES, ground_axis=UP_AXIS,
                                  coherent=True)
    record.worst_before = float(max(result["before"]))
    record.worst_after = float(max(result["after"]))
    record.failed_frames = [int(i) for i in result["failed"]]
    if record.worst_before <= CL.TARGET:
        return anim, record, []
    count = len(f["weapon"])
    judged = CL._clip_free_points(f["weapon"], f["pivots"], height, None, None)  # the points the solve judged

    def share_of(frame, wrist, roll, arm):
        points = CL.staged_points(judged[frame], f["pivots"][frame], wrist, f["grips"][frame], roll, f["shoulders"][frame] if can_arm else None, arm)
        return CL.deep_share(points, f["body"][frame], triangles, height, CL.CLEAR_MARGIN_SHARE, ground_axis=UP_AXIS)

    rolls = np.asarray(result["rolls"], float)
    arms = np.asarray(result["arm_rotvecs"], float)
    needed = [CL.deep_share(f["weapon"][i], f["body"][i], triangles, height, CL.CLEAR_MARGIN_SHARE, ground_axis=UP_AXIS) > CL.TARGET
              for i in range(count)]
    wrists = ramped(result["rotvecs"], needed, clear=lambda frame, vector: share_of(frame, vector, rolls[frame], arms[frame]) <= CL.TARGET)
    # a jump the ramp could not soften (a frame that needs a turn next to one the same turn puts in the body) is bridged where a nearer turn
    # stays clear, within what the clip's own hand turn leaves of the spin limit
    q = anim.channels[hand_name]["q"]
    room = [max(MAX_HAND_STEP_DEGREES - tripo_pose.quaternion_turn(q[i], q[i + 1]), 0.0) for i in range(count - 1)]
    wrists = CL.bridge_turns(wrists, lambda frame, vector: share_of(frame, vector, rolls[frame], arms[frame]) <= CL.LIMIT, room)
    bones = [(hand_name, hand)]
    if can_roll and np.abs(rolls).max() > 1e-9:
        bones.append((bone, mesh.bones.index(bone)))
    if can_arm and np.abs(arms).max() > 1e-9:
        bones.append((names["upper"], upper))
    channels, smooth, radius = _written_turns(mesh, anim, f["world"], bones, names, (wrists, rolls, arms))
    after = [share_of(i, smooth[0][i], smooth[1][i], smooth[2][i]) for i in range(count)]
    record.worst_after = float(max(after))
    record.failed_frames = [i for i, share in enumerate(after) if share > CL.LIMIT]
    record.smoothed_over = radius
    record.changed = True
    record.frames_changed = int(result["frames_changed"])
    record.max_degrees = round(float(result["max_degrees"]), 1)
    record.max_roll_degrees = round(float(result["max_roll_degrees"]), 1)
    record.max_arm_degrees = round(float(result["max_arm_degrees"]), 1)
    record.search_bound_reached = bool(result["search_bound_reached"])
    return pdx_deform.Animation(anim.fps, anim.frames, channels), record, [name for name, _index in bones]


def landing_frame(centres: np.ndarray, height: float) -> int:
    """The first frame from which the weapon's centre stays within `DROP_REST_SHARE` of the height of where it ends."""

    away = np.linalg.norm(centres - centres[-1], axis=1) > DROP_REST_SHARE * height
    return int(np.nonzero(away)[0].max()) + 1 if away.any() else 0


def _smoothstep(count: int, start: int, end: int) -> np.ndarray:
    """(count,) 0 up to `start`, 1 from `end` on, a smoothstep between."""

    x = np.clip((np.arange(count) - start) / max(end - start, 1), 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def _shifted_translations(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, world: np.ndarray, index: int, shift: np.ndarray, ramp: np.ndarray):
    """(the bone's translation samples with the world `shift` times each frame's `ramp` added, the frames that changed as 1.0)."""

    parent = int(mesh.parents[index])
    t = anim.channels[mesh.bones[index]]["t"].copy()
    weights = np.zeros(_frames_of(anim))
    for frame in np.nonzero(ramp > 0.0)[0]:
        shifted = world[frame, index].copy()
        shifted[:3, 3] += shift * ramp[frame]
        t[frame] = (np.linalg.inv(world[frame, parent]) @ shifted)[:3, 3]
        weights[frame] = 1.0
    return t, weights


def _drop_directions(base: float):
    """The unit vectors along the ground (x, z), the one at angle `base` first, then the others by their turn from it."""

    turns = sorted(range(DROP_DIRECTIONS), key=lambda k: abs(((k * 2 * np.pi / DROP_DIRECTIONS + np.pi) % (2 * np.pi)) - np.pi))
    for k in turns:
        angle = base + k * 2 * np.pi / DROP_DIRECTIONS
        yield np.array([np.cos(angle), 0.0, np.sin(angle)])


def clear_dropped_part(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, bone: str, others: Sequence[str], moved: Sequence[str]):
    """(the clip with the dropped part shifted, the record, the frames to write). The clip itself when the part is clear in every frame."""

    record = PropClearance(bone, "")
    if bone not in moved or bone not in mesh.bones or mesh.parents[mesh.bones.index(bone)] < 0:
        record.note = "the part's bone has no location keys"
        return anim, record, None
    held, triangles, body = part_split(mesh, bone, others)
    if held.sum() < 50:
        record.note = "fewer than 50 vertices"
        return anim, record, None
    height = float(mesh.height)
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    world = matrices @ np.linalg.pinv(mesh.inverse_bind)[None]
    index = mesh.bones.index(bone)
    indices = np.nonzero(held)[0]
    indices = indices[np.linspace(0, len(indices) - 1, min(MAX_POINTS, len(indices))).astype(int)]
    free = np.linalg.norm(mesh.positions[indices] - pdx_motion.rest_joints(mesh)[index], axis=1) > GRIP_ZONE_SHARE * height
    count = _frames_of(anim)
    weapon_frames, body_frames = [], []
    for frame in range(count):
        posed = pdx_deform.skin(mesh, matrices[frame])
        weapon_frames.append(posed[indices][free])
        body_frames.append(posed[body])
    landed = landing_frame(np.array([points.mean(axis=0) for points in weapon_frames]), height)
    start = max(landed - DROP_RAMP_FRAMES, 0)
    ramp = _smoothstep(count, start, landed)
    frames = range(start, count)

    def share(offset: np.ndarray, i: int) -> float:
        # the body test alone: a shift along the ground cannot lift the part, and the grounding lifts the whole unit with it
        return CL.deep_share(weapon_frames[i] + offset * ramp[i], body_frames[i], triangles, height, CL.CLEAR_MARGIN_SHARE)

    before = [share(np.zeros(3), i) for i in frames]
    record.worst_before = float(max(before, default=0.0))
    if record.worst_before <= CL.LIMIT:
        return anim, record, None
    away = weapon_frames[-1].mean(axis=0) - body_frames[-1].mean(axis=0)  # from the body's middle to the weapon's at the end
    away[UP_AXIS] = 0.0
    base = float(np.arctan2(away[2], away[0])) if float(np.linalg.norm(away)) > 1e-9 else 0.0
    # the worst frames first, then every fourth, then all: a candidate usually fails on the first of them
    order = [[frames[i] for i in np.argsort(-np.asarray(before))[:6]], list(frames)[::4], list(frames)]
    found = None
    for step in range(1, int(DROP_MAX_SHARE / DROP_STEP_SHARE) + 1):
        for direction in _drop_directions(base):
            offset = direction * step * DROP_STEP_SHARE * height
            if all(share(offset, i) <= CL.LIMIT for only in order for i in only):  # stops at the first frame that is not
                found = offset
                break
        if found is not None:
            break
    if found is None:
        record.failed_frames = [int(i) for i, share in zip(frames, before) if share > CL.LIMIT]
        record.worst_after = record.worst_before
        record.note = "no shift along the ground clears the part"
        return anim, record, None
    t, weights = _shifted_translations(mesh, anim, world, index, found, ramp)
    channels = {name: dict(channel) for name, channel in anim.channels.items()}
    channels[bone] = dict(channels[bone], t=t)
    record.changed, record.frames_changed, record.smoothed_over = True, int((weights > 0).sum()), landed  # landed: the frame the part came to rest
    record.worst_after = float(max(share(found, i) for i in frames))
    record.max_degrees = round(float(np.linalg.norm(found)) / height, 4)  # the shift, a share of the height
    return pdx_deform.Animation(anim.fps, anim.frames, channels), record, weights


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
    released = [part["bone"] for part in parts if part.get("bone") and role in (part.get("release_roles") or [])]
    records: Dict[str, dict] = {}
    changed_hands: List[str] = []
    for _pass in range(MAX_PASSES):
        again = False
        for bone in bones:
            result, record, turned = clear_part(mesh, anim, bone, [b for b in everyone if b != bone], keyed)
            if record.changed:
                anim = result
                again = True
                changed_hands += [name for name in turned if name not in changed_hands]
            first = records.get(bone)
            if first and first["changed"] and not record.changed:
                # a later pass found the part clear: keep what the pass that turned the hand did, and the share it left
                first["worst_after"] = record.worst_after
                first["failed_frames"] = record.failed_frames
            elif first and record.changed:
                record.worst_before = first["worst_before"]
                record.frames_changed = max(record.frames_changed, first["frames_changed"])
                record.max_degrees = max(record.max_degrees, first["max_degrees"])
                record.max_roll_degrees = max(record.max_roll_degrees, first.get("max_roll_degrees", 0.0))
                record.max_arm_degrees = max(record.max_arm_degrees, first.get("max_arm_degrees", 0.0))
                records[bone] = dict(record.__dict__)
            else:
                records[bone] = dict(record.__dict__)
        if not again:
            break
    moved = [joint.name for joint in info.children if "t" in str((joint.properties.get("sa") or [""])[0])]
    for bone in released:
        result, record, weights = clear_dropped_part(mesh, anim, bone, [b for b in everyone if b != bone], moved)
        records[bone] = dict(record.__dict__, released=True)
        if record.changed:
            anim = result
            tripo_pose._write_translations(data, moved, [bone], anim, weights)
    if changed_hands:
        everything = np.ones(max(anim.frames, 1))
        tripo_pose._write_rotations(data, keyed, changed_hands, anim, everything)
    Path(out_path).write_bytes(bytes(data))
    return records
