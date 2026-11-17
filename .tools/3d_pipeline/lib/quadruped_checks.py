"""The Tripo checks for a quadruped unit (the kit's quadruped rig: Root, Pelvis, Spine, Chest, Neck, Head, four legs, optional tail).

`tripo/tripo_checks.py` runs these instead of its humanoid checks when the mesh has the quadruped rig's leg bones. Each reads the
exported `.mesh` and `.anim` files, as the game loads them. Heights are shares of the unit's rest height.

- TRIPO-LOOP-POP: as for a humanoid, the last frame of an idle, move, attack, defend or retreat clip is more than 8 degrees from its first
  at some joint (`lib/tripo_pose.loop_seam`).
- TRIPO-FOOT-BELOW-GROUND: a hoof (the vertices the four `*_Hoof` bones carry most) sinks more than 0.1% of the height under the ground in
  a clip that is not a death.
- TRIPO-NOT-DOWN: a death must end lying down: in its last frame the body's lowest torso point (Pelvis, Spine and Chest vertices) is within
  `DOWN_BELLY_SHARE` of the height of the ground. A standing quadruped's belly is a fifth to a third of its height up.
- TRIPO-LOAD-BELOW-GROUND: a load the mount carries (`adapter/quadruped_load.py`: vertices bound wholly to the load bone) goes more than
  1% of the height under the ground in some frame, the weapon rule (TRIPO-WEAPON-BELOW-GROUND) applied to a tower that would sink.
- TRIPO-LOAD-STRETCH: more than 0.5% of the load's edges stretch or squash in some frame: a rigid tower bends (vanilla clothing's worst is
  2%, a plank never bends).
- TRIPO-LOAD-SEAM: in some frame, more than `LOAD_SEAM_LIMIT` of the seam's edges beside one body part stretch or squash, by the kit's
  measure (UNIT-ANIM-STRETCH: 1.5 times and 0.5% of the height). The seam is every edge with an end that carries some but not all of its
  weight on the load bone, and every edge from the load to the body. Each edge belongs to the part its body end follows most (its
  strongest bone but the load), and a part needs `SEAM_PART_EDGES` edges to be judged. The limit is vanilla clothing's worst share, 2.0%:
  that skin is tight to the body. A share of the whole mesh or of the whole seam misses a band: round 9 of the war elephant stretched
  0.5% of its 28,504 edges in its death (vanilla 4.2%) while the ear roots and the neck under the tower's front tore, and run 3 creased the
  top of the neck against the tower's front in its retreat while only 0.65% of the whole seam's edges stretched. Beside the head that
  crease is 16% of the edges (played offline on the round 9 mesh).
- TRIPO-LOAD-NOT-DOWN: a death ends with the load's lowest point more than `LOAD_REST_LIMIT` of the height above the ground: a review read a
  tower sticking out sideways with its outer end in the air as a rigid block, not a fallen load.
- TRIPO-MAP-READ: an attack or a defend changes the silhouette in the map camera from the idle's less than `map_read.MIN_READ`
  (`lib/map_read.py`: the share of the idle's silhouette that changes shape at the size a player sees the unit, at the clip's 90th
  percentile frame), or a retreat from the move's less than `map_read.MIN_GAIT_READ`. The limits are vanilla's horse charge against its
  forward idle, and against its walk. Both reviews of round 9 read its attack (0.15) and one its defend (0.01) as the idle on the map, and
  both reviews of run 3 its retreat (0.02 from the move) as the move. A retreat is judged against the defend too, at the same limit: run 4
  swung its retreat to both sides as its defend does (0.05 from the defend), and a review read them as one clip. A move is judged against
  the idle at the same 0.15, under the horse walk's 0.175 against its forward idle: run 5's heavy walk read 0.01, and a review could not
  tell it from the idle at map size. A defend is judged against the move at 0.15 too: run 6 swayed its defend to both sides with
  stepping forefeet, and a review read it as a copy of its swaying walk (0.05 from the move).
  A unit under a tall load (a load bone) is held to vanilla's own large units' readings (`map_read.LOADED_MOVE_READ`, `LOADED_READ`, measured
  in `lib/map_read.py`): the tower hides the legs, and a clip that turns the whole body reads as veering.
- TRIPO-LOOP-HEADING: a move, attack, defend or retreat starts or ends turned more than `HEADING_LIMIT` degrees from the unit's rest
  heading (the best turn about the vertical from the rest pose's vertices, seen from above). Vanilla's horse and camel walk and charge
  start and end within 1.6 degrees and its infantry's move within 8.1, while its idles (the horse 43, the camel 45, the infantry 30) and
  its infantry's retreat (42 to 49) hold a turn. Run 5 of the war elephant held its retreat turned 25 degrees, and both fresh reviews saw it
  snap round against the move and face away from its travel.
- TRIPO-LEG-ROOT-STRETCH: in some frame of a clip, more than `LEG_ROOT_LIMIT` of a leg root's edges stretch or squash,
  by the kit's measure. A leg's root is the skin with at least `LEG_ROOT_SHARE` of its weight on the torso and as much on the leg's
  Upper bone, where the hip or shoulder meets the body, and the limit is vanilla clothing's worst share, 2.0%. Run 4 of the war elephant
  stretched 2.4% of its near hind leg's root in the retreat, where both fresh reviews saw the thigh and flank stretch against the belly,
  and 5.3% of its near foreleg's root in the defend. Vanilla's coarse horse is no reference: its charge reaches 20% there.
- TRIPO-DEATH-STIFF-LEGS: in a death the legs bend less than `DEATH_LEG_BEND` degrees (the mean over the four legs of the turn between the
  thigh or upper arm and the foot, from the rest pose, at its largest): the body falls as a block on straight legs. Round 9 bent 8 degrees.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from . import map_read, pdx_deform, pdx_motion, tripo_pose
from . import tripo_checks as T


def _finding(rule: str, subject: str, message: str, **numbers) -> dict:
    return {"rule": rule, "subject": subject, "message": message, **numbers}

HOOF_SUFFIX = "_Hoof"
LEG_PREFIXES = ("Front_", "Rear_")
TORSO = ("Pelvis", "Spine", "Chest")
LOAD_BONE = "Load"
DOWN_BELLY_SHARE = 0.05
LOAD_SINK_LIMIT = 0.01
LOAD_STRETCH_LIMIT = 0.005
LOAD_REST_LIMIT = 0.02  # of the height: how far above the ground a dead body's load may end (run 8's tower stuck out 5.9% up, a review's major)
LOAD_SEAM_LIMIT = 0.02  # vanilla clothing's worst share of deformed edges (tripo_checks VANILLA_CLOAK_WORST, 1.97%), rounded
SEAM_PART_EDGES = 30  # a part beside the load is judged when this many seam edges follow it
# role: (the role it must not look like, the least reading, the vanilla clip that reading comes from)
MAP_READ_ROLES = {
    "move": (("idle", map_read.MIN_GAIT_READ, "under vanilla's horse walk against its idle, 0.175"),),
    "attack": (("idle", map_read.MIN_READ, "vanilla's horse charge against its idle"),),
    "defend": (("idle", map_read.MIN_READ, "vanilla's horse charge against its idle"),
               ("move", map_read.MIN_GAIT_READ, "vanilla's horse charge against its walk")),
    "retreat": (("move", map_read.MIN_GAIT_READ, "vanilla's horse charge against its walk"),
                ("defend", map_read.MIN_GAIT_READ, "vanilla's horse charge against its walk")),
}
HEADING_ROLES = ("move", "attack", "defend", "retreat")
HEADING_LIMIT = 10.0  # degrees: vanilla's horse and camel walk and charge start and end within 1.6, its infantry's move within 8.1
LEG_ROOT_SHARE = 0.2  # a leg's root: skin with at least this weight on the torso (Pelvis, Spine, Chest) and on the leg's Upper bone
LEG_ROOT_LIMIT = 0.02  # vanilla clothing's worst share of deformed edges (tripo_checks VANILLA_CLOAK_WORST, 1.97%), rounded
DEATH_LEG_BEND = 25.0  # degrees


def is_quadruped(mesh: pdx_deform.SkinnedMesh) -> bool:
    return sum(name.endswith(HOOF_SUFFIX) and name.startswith(LEG_PREFIXES) for name in mesh.bones) == 4


def _dominant(mesh: pdx_deform.SkinnedMesh) -> np.ndarray:
    names = np.array(mesh.bones + [""])
    return names[pdx_deform.dominant_bones(mesh)]


def load_mask(mesh: pdx_deform.SkinnedMesh) -> np.ndarray:
    """The load's vertices: weight 1 on the load bone and above the body's mid height (the rule binds nothing else wholly to it)."""

    if LOAD_BONE not in mesh.bones:
        return np.zeros(len(mesh.positions), bool)
    bone = mesh.bones.index(LOAD_BONE)
    whole = ((mesh.joints == bone) & (mesh.weights > 0.999)).any(axis=1)
    floor = float(mesh.positions[:, 1].min())
    return whole & (mesh.positions[:, 1] > floor + 0.5 * mesh.height)


def seam_mask(mesh: pdx_deform.SkinnedMesh) -> np.ndarray:
    """The skin the load blends into: vertices with some weight on the load bone that are not the load itself."""

    if LOAD_BONE not in mesh.bones:
        return np.zeros(len(mesh.positions), bool)
    share = np.where(mesh.joints == mesh.bones.index(LOAD_BONE), mesh.weights, 0.0).sum(axis=1)
    return (share > 1e-3) & ~load_mask(mesh)


def seam_edges(mesh: pdx_deform.SkinnedMesh, edges: np.ndarray, load: np.ndarray, seam: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """The seam's edges (an end on the seam, or one end on the load and one off it) and, per edge, the part beside the load: the strongest
    bone but the load of its body end (the end off the load; the first end when both are off it)."""

    picked = edges[seam[edges[:, 0]] | seam[edges[:, 1]] | (load[edges[:, 0]] != load[edges[:, 1]])]
    names = np.array(mesh.bones + [""])
    own = np.where(mesh.joints == mesh.bones.index(LOAD_BONE), 0.0, mesh.weights) if LOAD_BONE in mesh.bones else mesh.weights
    strongest = np.take_along_axis(mesh.joints, np.argmax(own, axis=1)[:, None], axis=1)[:, 0]
    body_end = np.where(load[picked[:, 0]], picked[:, 1], picked[:, 0])
    return picked, names[strongest[body_end]]


def seam_share(mesh: pdx_deform.SkinnedMesh, posed: np.ndarray, picked: np.ndarray, parts: np.ndarray) -> Tuple[float, int, str]:
    """The worst share, over the frames and the parts with at least `SEAM_PART_EDGES` seam edges, of a part's seam edges that the kit's
    measure counts as stretched or squashed, with that frame and part."""

    judged = [(name, parts == name) for name in np.unique(parts) if (parts == name).sum() >= SEAM_PART_EDGES]
    if not judged:
        return 0.0, 0, ""
    rest = np.linalg.norm(mesh.positions[picked[:, 0]] - mesh.positions[picked[:, 1]], axis=1)
    usable = rest > 1e-9
    height = max(mesh.height, 1e-6)
    worst = (0.0, 0, "")
    for frame, points in enumerate(posed):
        length = np.linalg.norm(points[picked[:, 0]] - points[picked[:, 1]], axis=1)
        ratio = np.where(usable, length / np.where(usable, rest, 1.0), 1.0)
        growth = (length - rest) / height
        bad = ((ratio > pdx_deform.STRETCH_RATIO) & (growth > pdx_deform.SIGNIFICANT_SHARE)) | (
            (ratio < pdx_deform.SQUASH_RATIO) & (-growth > pdx_deform.SIGNIFICANT_SHARE))
        for name, mask in judged:
            share = float(bad[mask].mean())
            if share > worst[0]:
                worst = (share, frame, str(name))
    return worst


def leg_bend(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation) -> float:
    """The largest over the frames of the mean over the four legs of the turn (degrees, from the rest pose) between the leg's upper segment
    (Upper to Lower joint) and its foot (Cannon to Hoof joint)."""

    index = {name: i for i, name in enumerate(mesh.bones)}
    parts = ("Upper", "Lower", "Cannon", "Hoof")
    legs = [leg for leg in ("Front_Left", "Front_Right", "Rear_Left", "Rear_Right") if all(f"{leg}_{part}" in index for part in parts)]
    if not legs:
        return 0.0
    rest = pdx_motion.rest_joints(mesh)[None]
    posed = pdx_motion.posed_joints(mesh, anim)

    def angles(joints: np.ndarray, leg: str) -> np.ndarray:
        top = joints[:, index[f"{leg}_Lower"]] - joints[:, index[f"{leg}_Upper"]]
        foot = joints[:, index[f"{leg}_Hoof"]] - joints[:, index[f"{leg}_Cannon"]]
        cosine = (top * foot).sum(axis=1) / np.maximum(np.linalg.norm(top, axis=1) * np.linalg.norm(foot, axis=1), 1e-12)
        return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

    bends = np.stack([np.abs(angles(posed, leg) - angles(rest, leg)[0]) for leg in legs], axis=1)
    return float(bends.mean(axis=1).max())


def _map_findings(mesh: pdx_deform.SkinnedMesh, anims: Dict[str, pdx_deform.Animation], numbers: dict) -> List[dict]:
    """TRIPO-MAP-READ: each role in `MAP_READ_ROLES` against the unit's own clip of the role it must not look like."""

    by_role = {tripo_pose.role_of(clip): anim for clip, anim in anims.items()}
    camera = map_read.MapCamera(mesh)
    loaded = bool(load_mask(mesh).any())
    references: Dict[str, list] = {}
    out = []
    for clip, anim in anims.items():
        role = tripo_pose.role_of(clip)
        frames = None
        for other, limit, what in MAP_READ_ROLES.get(role, ()):
            if other not in by_role:
                continue
            if other not in references:
                references[other] = camera.frames(by_role[other])
            frames = camera.frames(anim) if frames is None else frames
            reading = map_read.read_against_idle(camera, frames, references[other])
            numbers.setdefault(clip, {}).setdefault("map_read", {})[other] = reading
            limit = map_read.loaded_limit(limit, loaded, move=role == "move")
            if reading < limit:
                out.append(_finding("TRIPO-MAP-READ", clip, f"from the map camera the {role} changes {reading:.0%} of the {other}'s silhouette (at least {limit:.1%}, {what}{", vanilla's large units for a unit under a tall load" if loaded else ""}): it reads as the {other} at map size", share=reading, against=other))
    return out


def leg_roots(mesh: pdx_deform.SkinnedMesh, edges: np.ndarray) -> Dict[str, np.ndarray]:
    """Per leg, the edges of its root: those with an end that carries at least `LEG_ROOT_SHARE` of its weight on the torso and as much on
    the leg's Upper bone (the hip or shoulder where the leg meets the body)."""

    dense = np.zeros((len(mesh.positions), len(mesh.bones)))
    rows = np.arange(len(mesh.positions))
    for slot in range(mesh.joints.shape[1]):
        np.add.at(dense, (rows, np.clip(mesh.joints[:, slot], 0, None)), np.where(mesh.joints[:, slot] >= 0, mesh.weights[:, slot], 0.0))
    index = {name: i for i, name in enumerate(mesh.bones)}
    torso = dense[:, [index[name] for name in TORSO if name in index]].sum(axis=1)
    out = {}
    for prefix in ("Front_Left", "Front_Right", "Rear_Left", "Rear_Right"):
        if f"{prefix}_Upper" not in index:
            continue
        root = (torso >= LEG_ROOT_SHARE) & (dense[:, index[f"{prefix}_Upper"]] >= LEG_ROOT_SHARE)
        picked = edges[root[edges[:, 0]] | root[edges[:, 1]]]
        if len(picked):
            out[prefix] = picked
    return out


def leg_root_share(mesh: pdx_deform.SkinnedMesh, posed: np.ndarray, roots: Dict[str, np.ndarray]) -> Tuple[float, int, str]:
    """The worst share, over the frames and the legs, of a leg root's edges the kit's measure counts as stretched or squashed."""

    height = max(mesh.height, 1e-6)
    worst = (0.0, 0, "")
    for leg, picked in roots.items():
        rest = np.linalg.norm(mesh.positions[picked[:, 0]] - mesh.positions[picked[:, 1]], axis=1)
        length = np.linalg.norm(posed[:, picked[:, 0]] - posed[:, picked[:, 1]], axis=2)
        ratio = length / np.maximum(rest, 1e-9)
        growth = (length - rest) / height
        bad = ((ratio > pdx_deform.STRETCH_RATIO) & (growth > pdx_deform.SIGNIFICANT_SHARE)) | (
            (ratio < pdx_deform.SQUASH_RATIO) & (-growth > pdx_deform.SIGNIFICANT_SHARE))
        shares = bad.mean(axis=1)
        frame = int(np.argmax(shares))
        if shares[frame] > worst[0]:
            worst = (float(shares[frame]), frame, leg)
    return worst


def heading(rest: np.ndarray, posed: np.ndarray) -> float:
    """The turn about the vertical (degrees) that best carries the rest pose's vertices onto the posed ones, seen from above."""

    a = rest[:, [0, 2]] - rest[:, [0, 2]].mean(axis=0)
    b = posed[:, [0, 2]] - posed[:, [0, 2]].mean(axis=0)
    h = a.T @ b
    return float(np.degrees(np.arctan2(h[0, 1] - h[1, 0], h[0, 0] + h[1, 1])))


def _heading_findings(mesh: pdx_deform.SkinnedMesh, clip: str, posed: np.ndarray, row: dict) -> List[dict]:
    """TRIPO-LOOP-HEADING: a looping clip a unit plays while it travels or fights starts and ends at its rest heading."""

    first, last = heading(mesh.positions, posed[0]), heading(mesh.positions, posed[-1])
    row["heading_first_last"] = [round(first, 1), round(last, 1)]
    worst = max(abs(first), abs(last))
    if worst <= HEADING_LIMIT:
        return []
    return [_finding("TRIPO-LOOP-HEADING", clip, f"the clip starts or ends turned {worst:.0f} degrees from the unit's heading (limit {HEADING_LIMIT:.0f}, vanilla's mounts and infantry move): the unit snaps round when the clip begins and faces away from its travel", degrees=round(worst, 1))]


def _frames(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation) -> np.ndarray:
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    return np.stack([pdx_deform.skin(mesh, matrices[f]) for f in range(anim.frames)])


def _load_findings(mesh, clip: str, posed: np.ndarray, edges: np.ndarray, load: np.ndarray, seam: Tuple[np.ndarray, np.ndarray], row: dict) -> List[dict]:
    """TRIPO-LOAD-BELOW-GROUND, TRIPO-LOAD-STRETCH and TRIPO-LOAD-SEAM for one clip; fills `row`."""

    out: List[dict] = []
    height = max(mesh.height, 1e-6)
    floor = float(mesh.positions[:, 1].min())
    if load.any():
        sink = (posed[:, load, 1].min(axis=1) - floor) / height
        row["load_lowest_share"] = round(float(sink.min()), 4)
        if sink.min() < -LOAD_SINK_LIMIT:
            frame = int(np.argmin(sink))
            out.append(_finding("TRIPO-LOAD-BELOW-GROUND", clip, f"the load goes {-sink.min():.1%} of the height under the ground in frame {frame} (limit {LOAD_SINK_LIMIT:.0%})", share=round(float(-sink.min()), 4), frame=frame))
        if tripo_pose.role_of(clip) == "death" and row["load_lowest_share"] > LOAD_REST_LIMIT:
            out.append(_finding("TRIPO-LOAD-NOT-DOWN", clip, f"the dead body's load ends {row['load_lowest_share']:.1%} of the height above the ground (limit {LOAD_REST_LIMIT:.0%}): it sticks out in the air instead of resting on the ground", share=row["load_lowest_share"]))
        share, frame = T.region_stretch_share(mesh.positions, posed, edges, load, mesh.height)
        row["load_stretch_share"] = round(share, 4)
        if share > LOAD_STRETCH_LIMIT:
            out.append(_finding("TRIPO-LOAD-STRETCH", clip, f"{share:.1%} of the load's edges stretch or squash in frame {frame} (limit {LOAD_STRETCH_LIMIT:.1%}): the load bends", share=round(share, 4)))
    if len(seam[0]):
        share, frame, part = seam_share(mesh, posed, *seam)
        row["load_seam_share"] = round(share, 4)
        row["load_seam_part"] = part
        if share > LOAD_SEAM_LIMIT:
            out.append(_finding("TRIPO-LOAD-SEAM", clip, f"{share:.1%} of the edges where the load meets the {part} skin stretch or squash in frame {frame} (limit {LOAD_SEAM_LIMIT:.0%}, vanilla clothing's worst): the skin at the load tears or creases as that part turns against it", share=round(share, 4), frame=frame, part=part))
    return out


def _death_findings(mesh, clip: str, anim, posed: np.ndarray, torso: np.ndarray, row: dict) -> List[dict]:
    """TRIPO-DEATH-STIFF-LEGS and TRIPO-NOT-DOWN for a death clip; fills `row`."""

    out: List[dict] = []
    bend = leg_bend(mesh, anim)
    row["death_leg_bend_degrees"] = round(bend, 1)
    if bend < DEATH_LEG_BEND:
        out.append(_finding("TRIPO-DEATH-STIFF-LEGS", clip, f"the legs bend at most {bend:.0f} degrees (at least {DEATH_LEG_BEND:.0f}): the body falls as a block on straight legs", degrees=round(bend, 1)))
    if torso.any():
        belly = float(posed[-1][torso, 1].min() - mesh.positions[:, 1].min()) / max(mesh.height, 1e-6)
        row["final_torso_lowest_share"] = round(belly, 4)
        if belly > DOWN_BELLY_SHARE:
            out.append(_finding("TRIPO-NOT-DOWN", clip, f"the body's lowest torso point ends {belly:.0%} of the height above the ground (limit {DOWN_BELLY_SHARE:.0%}): it does not end lying down", share=round(belly, 4)))
    return out


def quadruped_findings(mesh: pdx_deform.SkinnedMesh, anims: Dict[str, pdx_deform.Animation]) -> Tuple[List[dict], dict]:
    out: List[dict] = []
    numbers: dict = {}
    height = max(mesh.height, 1e-6)
    floor = float(mesh.positions[:, 1].min())
    dominant = _dominant(mesh)
    hooves = np.array([name.endswith(HOOF_SUFFIX) for name in dominant])
    torso = np.isin(dominant, TORSO)
    load = load_mask(mesh)
    edges = pdx_deform.mesh_edges(mesh)
    seam = seam_edges(mesh, edges, load, seam_mask(mesh)) if load.any() else (np.zeros((0, 2), int), np.zeros(0, str))
    roots = leg_roots(mesh, edges)
    numbers["load_vertices"] = int(load.sum())
    numbers["seam_edges"] = int(len(seam[0]))
    for clip, anim in anims.items():
        role = tripo_pose.role_of(clip)
        posed = _frames(mesh, anim)
        row: dict = {}
        if role in tripo_pose.LOOP_ROLES:
            turn, joint = tripo_pose.loop_seam(mesh, anim)
            row["loop_seam_degrees"] = round(turn, 1)
            if turn > tripo_pose.LOOP_POSE_LIMIT_DEGREES:
                out.append(_finding("TRIPO-LOOP-POP", clip, f"the last frame is {turn:.0f} degrees from the first at {joint} (limit {tripo_pose.LOOP_POSE_LIMIT_DEGREES:g}): the looped {role} pops back to its start", degrees=round(turn, 1)))
        if role != "death" and hooves.any():
            lowest = (posed[:, hooves, 1].min(axis=1) - floor) / height
            row["lowest_hoof_share"] = round(float(lowest.min()), 4)
            if lowest.min() < -tripo_pose.FOOT_SINK_LIMIT:
                frame = int(np.argmin(lowest))
                out.append(_finding("TRIPO-FOOT-BELOW-GROUND", clip, f"a hoof sinks {-lowest.min():.2%} of the height under the ground in frame {frame} (limit {tripo_pose.FOOT_SINK_LIMIT:.1%})", share=round(float(-lowest.min()), 4), frame=frame))
        if role == "death":
            out += _death_findings(mesh, clip, anim, posed, torso, row)
        if role in HEADING_ROLES:
            out += _heading_findings(mesh, clip, posed, row)
        out += _load_findings(mesh, clip, posed, edges, load, seam, row)
        if roots:
            share, frame, leg = leg_root_share(mesh, posed, roots)
            row["leg_root_share"], row["leg_root"] = round(share, 4), leg
            if share > LEG_ROOT_LIMIT:
                out.append(_finding("TRIPO-LEG-ROOT-STRETCH", clip, f"{share:.1%} of the {leg.replace('_', ' ').lower()} leg's root edges (where it meets the body) stretch or squash in frame {frame} (limit {LEG_ROOT_LIMIT:.0%}, vanilla clothing's worst): the hip or shoulder turns too far for the skin there", share=round(share, 4), frame=frame, leg=leg))
        numbers[clip] = row
    out += _map_findings(mesh, anims, numbers)
    return out, numbers
