"""A rider on its mount, measured from the exported files (no Blender).

The game draws a rider entity on the mount's `Saddle_Node`: every frame the node's posed transform, times the rider entity's scale in the
mount's mesh units, carries the rider's own posed mesh. This module plays both, frame by frame, in the mount's file space (Y up):

- `node_matrices`: the node's world transform in each frame of a mount clip.
- `barrel_profile`: the mount's half-width beside the seat at each depth below the node, in rider heights (`rider_seat.py` aims the
  seated legs outside it).
- `clip_profiles`: that barrel and the top of the mount ahead of the seat, widest over each mount clip in the node's own frame
  (`rider_seat.py` fits a role's legs and hands to the mount clip of the same role).
- `seat_report`: for each mount clip and the rider clip it plays, the share of the rider sunk into the mount and how far the saddle's
  surface moves from the node (the rider floats or sinks when the skin under the node does not follow it).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

from .pdx_deform import Animation, SkinnedMesh, load_anim, load_mesh, skin, skinning_matrices
from .pdx_motion import face_centres, inside_share, point_surface_distance

NODE = "Saddle_Node"
# Rider points sampled per frame, and mount faces they are tested against.
RIDER_SAMPLES = 1500
MOUNT_FACES = 4000
# A rider point counts as sunk when it lies behind the mount's nearest face within this share of the rider's height.
SINK_DEPTH = 0.05
# The barrel beside the seat: a slab this share of the rider's height either side of the node along the mount's length.
PROFILE_SLAB = 0.12
PROFILE_STEPS = tuple(round(0.05 * step, 2) for step in range(0, 12))  # depths below the node, in rider heights
# The saddle under the node: mount faces within this share of the rider's height of the node at rest.
SADDLE_REACH = 0.15
# The top of the mount ahead of the seat (withers, neck, mane), where a seated rider's hands reach: cells this far ahead of the node and
# out from its midline, each TOP_CELL either way, in rider heights.
TOP_AHEAD = tuple(round(0.05 * step, 2) for step in range(0, 10))
TOP_OUT = tuple(round(0.05 * step, 2) for step in range(0, 6))
TOP_CELL = 0.025


def node_index(mesh: SkinnedMesh, name: str = NODE) -> int:
    if name not in mesh.bones:
        raise ValueError(f"the mesh has no {name} bone")
    return mesh.bones.index(name)


def rest_node(mesh: SkinnedMesh, name: str = NODE) -> np.ndarray:
    return np.linalg.inv(mesh.inverse_bind[node_index(mesh, name)])


def node_matrices(mesh: SkinnedMesh, anim: Animation, name: str = NODE) -> np.ndarray:
    """(F, 4, 4): the node's world transform in each frame (skinning matrix times the node's bind transform)."""

    index = node_index(mesh, name)
    return skinning_matrices(mesh, anim)[:, index] @ np.linalg.inv(mesh.inverse_bind[index])[None]


def _apply(matrix: np.ndarray, points: np.ndarray) -> np.ndarray:
    return points @ matrix[:3, :3].T + matrix[:3, 3]


def length_axis(mesh: SkinnedMesh) -> int:
    """The mount's long horizontal axis in file space (Y is up): 0 for X, 2 for Z."""

    extent = np.ptp(mesh.positions, axis=0)
    return 0 if extent[0] > extent[2] else 2


def barrel_profile(mount: SkinnedMesh, rider_height: float, name: str = NODE) -> List[Dict[str, float]]:
    """The mount's half-width from the node's side plane at each depth below the node, both in rider heights, at rest."""

    return _barrel_rows(mount.positions, rest_node(mount, name)[:3, 3], length_axis(mount), rider_height)


def _barrel_rows(p: np.ndarray, node: np.ndarray, along: int, rider_height: float) -> List[Dict[str, float]]:
    side = 2 if along == 0 else 0
    slab = p[np.abs(p[:, along] - node[along]) < PROFILE_SLAB * rider_height]
    rows = []
    for depth in PROFILE_STEPS:
        level = node[1] - depth * rider_height
        band = slab[np.abs(slab[:, 1] - level) < 0.025 * rider_height]
        half = float(np.abs(band[:, side] - node[side]).max()) / rider_height if len(band) else 0.0
        rows.append({"depth": depth, "half_width": round(half, 4)})
    return rows


def facing(mesh: SkinnedMesh) -> float:
    """+1 when the mount's head lies toward + along its length axis, else -1: the head (ears, poll) holds its highest points at rest."""

    along = length_axis(mesh)
    p = mesh.positions
    top = p[p[:, 1] >= np.percentile(p[:, 1], 98)]
    return 1.0 if float(top[:, along].mean()) >= float(np.median(p[:, along])) else -1.0


def _top_rows(p: np.ndarray, node: np.ndarray, along: int, ahead_sign: float, rider_height: float) -> List[Dict[str, Optional[float]]]:
    """The mount's highest point above the node in each cell ahead of the seat, in rider heights (None for an empty cell)."""

    side = 2 if along == 0 else 0
    ahead = (p[:, along] - node[along]) * ahead_sign / rider_height
    out = np.abs(p[:, side] - node[side]) / rider_height
    up = (p[:, 1] - node[1]) / rider_height
    rows = []
    for a in TOP_AHEAD:
        near = np.abs(ahead - a) < TOP_CELL
        for o in TOP_OUT:
            cell = near & (np.abs(out - o) < TOP_CELL)
            rows.append({"ahead": a, "out": o, "top": round(float(up[cell].max()), 4) if cell.any() else None})
    return rows


def _widest(rows: List[Dict], key: str, other: List[Dict]) -> List[Dict]:
    merged = []
    for row, more in zip(rows, other):
        values = [v for v in (row[key], more[key]) if v is not None]
        merged.append({**row, key: max(values) if values else None})
    return merged


def clip_profiles(mount: SkinnedMesh, clips: Dict[str, Animation], rider_height: float, name: str = NODE) -> Dict[str, Dict[str, List]]:
    """For the rest pose and every mount clip, the barrel beside the seat (`barrel`, as barrel_profile) and the top of the mount ahead of
    it (`top`: highest point above the node per cell of distance ahead and out from the midline), each the widest or highest over the
    clip's frames and measured in the node's own frame, which is the frame a rider on the node sees. A brace that lifts the shoulders
    widens the barrel under the seat and raises the withers toward the rein hand: legs solved against the rest barrel sank."""

    mesh = _bindable(mount)
    index = node_index(mesh, name)
    rest = rest_node(mesh, name)
    node = rest[:3, 3]
    along = length_axis(mesh)
    sign = facing(mesh)
    rest_profile = {"barrel": _barrel_rows(mesh.positions, node, along, rider_height),
                    "top": _top_rows(mesh.positions, node, along, sign, rider_height)}
    profiles = {"rest": rest_profile}
    for role, anim in clips.items():
        matrices = skinning_matrices(mesh, anim)
        profile = dict(rest_profile)
        for frame in range(len(matrices)):
            # the posed mount carried back so the posed node sits on the rest node
            back = rest @ np.linalg.inv(matrices[frame, index] @ rest)
            points = _apply(back, skin(mesh, matrices[frame]))
            barrel = _barrel_rows(points, node, along, rider_height)
            profile["barrel"] = [{**row, "half_width": max(row["half_width"], more["half_width"])} for row, more in zip(profile["barrel"], barrel)]
            profile["top"] = _widest(profile["top"], "top", _top_rows(points, node, along, sign, rider_height))
        profile["seconds"] = anim.frames / max(anim.fps, 1e-6)
        profiles[role] = profile
    return profiles


def seat_basis(mesh: SkinnedMesh) -> np.ndarray:
    """(3, 3): columns ahead, out and up of a rider seated on the mount, as file-space directions. The kit's exported riders face -Z
    with their right hand toward -X (Blender's -Y and -X), and rider_seat's side axis (forward x up in Blender) is the rider's right, so
    with the mount facing -Z the seat's ahead is -Z and its out -X. A mount must lie along Z, as the kit's exporter writes it."""

    if length_axis(mesh) != 2:
        raise ValueError("the mount does not lie along the file's Z axis; the seat's frame is not known for it")
    sign = facing(mesh)
    return np.array([[0.0, sign, 0.0], [0.0, 0.0, 1.0], [sign, 0.0, 0.0]])


def drop_inputs(mount: SkinnedMesh, anim: Animation, rider_height: float, name: str = NODE, points: int = 1500) -> Dict[str, object]:
    """What a seated rider's seat step needs to drop a held weapon onto the ground through the mount clip (`anim`, the death):

    - `path`: per mount frame, `r` (3x3) and `t` (3) that carry a point fixed in the world, given in the seat's coordinates at rest
      (ahead, out, up in rider heights from the rest node), to the seat's coordinates on the moving node: q_frame = r @ q_rest + t.
    - `ground`: the ground's height in those rest coordinates (the mount's lowest point at rest stands on it).
    - `mount_end`: an even sample of the mount's points at its last frame, in rest coordinates: the weapon lands clear of them.
    - `fps`: the mount clip's rate, for matching a rider frame to a mount frame by time."""

    mesh = _bindable(mount)
    index = node_index(mesh, name)
    rest = rest_node(mesh, name)
    node = rest[:3, 3]
    basis = seat_basis(mesh)
    matrices = skinning_matrices(mesh, anim)
    path = []
    for frame in range(len(matrices)):
        back = rest @ np.linalg.inv(matrices[frame, index] @ rest)
        turn = back[:3, :3]
        path.append({"r": (basis.T @ turn @ basis).round(6).tolist(),
                     "t": (basis.T @ (turn @ node + back[:3, 3] - node) / rider_height).round(6).tolist()})
    end = skin(mesh, matrices[-1])[_evenly(len(mesh.positions), points)]
    return {"path": path, "ground": round(float(mesh.positions[:, 1].min() - node[1]) / rider_height, 6),
            "mount_end": (((end - node) @ basis) / rider_height).round(5).tolist(), "fps": float(anim.fps)}


@dataclass
class ClipSeat:
    mount_clip: str
    rider_clip: str
    frames: int
    worst_sunk: float = 0.0  # share of the rider's sampled points behind the mount's surface
    worst_sunk_frame: int = -1
    worst_gap: float = 0.0  # the saddle surface's distance from the node, in rider heights
    worst_gap_frame: int = -1
    mount_seconds: float = 0.0
    rider_seconds: float = 0.0


@dataclass
class SeatReport:
    rider_height: float  # in the mount's mesh units
    rest_gap: float
    clips: List[ClipSeat] = field(default_factory=list)


def _bindable(mesh: SkinnedMesh) -> SkinnedMesh:
    """The mesh with every singular inverse bind (vanilla infantry's `Root_node_1` and `_2` store zeros; they skin nothing) as identity."""

    singular = np.abs(np.linalg.det(mesh.inverse_bind[:, :3, :3])) < 1e-9 if len(mesh.inverse_bind) else np.zeros(0, dtype=bool)
    if not singular.any():
        return mesh
    fixed = mesh.inverse_bind.copy()
    fixed[singular] = np.eye(4)
    return replace(mesh, inverse_bind=fixed)


def role_of(clip: str) -> str:
    """The role of a clip keyed by its role or by its file stem (`<stem>_<role>`)."""

    return clip.rsplit("_", 1)[-1]


def _evenly(count: int, wanted: int) -> np.ndarray:
    return np.unique(np.linspace(0, count - 1, min(count, wanted)).astype(np.int64)) if count else np.zeros(0, dtype=np.int64)


def seat_report(mount: SkinnedMesh, mount_clips: Dict[str, Animation], rider: SkinnedMesh, rider_clips: Dict[str, Animation],
                scale: float, role_map: Optional[Dict[str, str]] = None, name: str = NODE) -> SeatReport:
    """Play every mount clip with the rider clip it carries (`role_map`, else the same role, else the rider's idle)."""

    role_map = dict(role_map or {})
    mount, rider = _bindable(mount), _bindable(rider)
    rider_height = float(np.ptp(rider.positions[:, 1])) * scale
    rest = rest_node(mount, name)[:3, 3]
    faces = mount.triangles[_evenly(len(mount.triangles), MOUNT_FACES)]
    centres_rest = mount.positions[faces].mean(axis=1)
    saddle = faces[np.linalg.norm(centres_rest - rest, axis=1) < SADDLE_REACH * rider_height]
    report = SeatReport(rider_height=rider_height,
                        rest_gap=point_surface_distance(rest[None], mount.positions[saddle]) / rider_height if len(saddle) else float("inf"))
    sample = _evenly(len(rider.positions), RIDER_SAMPLES)
    for role, anim in mount_clips.items():
        # a clip is keyed by its role or by its file stem (`<stem>_<role>`, as tripo_checks loads it): the 2026-11-23 mount checks matched
        # no stem, so every mount clip carried the rider's idle
        short = role_of(role)
        wanted = role_map.get(role, role_map.get(short, short if short in rider_clips else role))
        rider_role = wanted if wanted in rider_clips else ("idle" if "idle" in rider_clips else next(iter(rider_clips)))
        rider_anim = rider_clips[rider_role]
        mount_matrices = skinning_matrices(mount, anim)
        nodes = mount_matrices[:, node_index(mount, name)] @ np.linalg.inv(mount.inverse_bind[node_index(mount, name)])[None]
        rider_matrices = skinning_matrices(rider, rider_anim)
        frames = mount_matrices.shape[0]
        clip = ClipSeat(role, rider_role, frames, mount_seconds=anim.frames / max(anim.fps, 1e-6),
                        rider_seconds=rider_anim.frames / max(rider_anim.fps, 1e-6))
        for frame in range(frames):
            seconds = frame / max(anim.fps, 1e-6)
            rider_frame = int(round(seconds * rider_anim.fps)) % max(rider_matrices.shape[0], 1)
            moved = skin(mount, mount_matrices[frame])
            centres, normals = face_centres(moved, faces)
            riding = _apply(nodes[frame], scale * skin(rider, rider_matrices[rider_frame])[sample])
            sunk = inside_share(riding, centres, normals, SINK_DEPTH * rider_height)
            if sunk > clip.worst_sunk:
                clip.worst_sunk, clip.worst_sunk_frame = sunk, frame
            if len(saddle):
                gap = point_surface_distance(nodes[frame][:3, 3][None], moved[saddle]) / rider_height
                if gap > clip.worst_gap:
                    clip.worst_gap, clip.worst_gap_frame = gap, frame
        report.clips.append(clip)
    return report


def load_unit(folder: Path, stem: str) -> tuple:
    """A unit's mesh and its clips by role (`<stem>_<role>.anim`)."""

    mesh = load_mesh(folder / f"{stem}.mesh")
    clips = {anim.stem[len(stem) + 1:]: load_anim(anim) for anim in sorted(folder.glob(f"{stem}_*.anim"))}
    return mesh, clips


# Limits, measured on vanilla: `western_european_infantry.mesh` with the cavalry rider's idle and moving clips on `cavalry_horse.mesh`'s
# Saddle_Node (rider entity scale 0.8 over the horse's pdxmesh scale 0.45, so 1.78 in the horse's mesh units) sinks at most 5.9% of its
# sampled points into the horse (idle 5.9%, walk 3.9%, charge 2.5%), and the saddle's surface stays 1.5% of the rider's height from the
# node in every frame. A death is left out: the rider falls with the body by design.
SUNK_LIMIT = 0.06
GAP_LIMIT = 0.03
NOT_JUDGED = ("death",)
# A rider's one-shot roles end with the mount's: the game starts both clips together, so a rider attack or death that runs on past the
# mount's by more than this factor plays out over a mount already done (the zinnish lancer's death took 17.8 s over the horse's 2 s, its
# couched lance 4.4 s to come down). Vanilla's riders have neither clip.
TIMED_ROLES = ("attack", "death")
TIMING_SLACK = 1.5


def seat_findings(report: SeatReport) -> tuple:
    """TRIPO-RIDER-SUNK and TRIPO-RIDER-OFF-SEAT for every mount clip but the death, TRIPO-RIDER-CLIP-LENGTH for the attack and the
    death, and the numbers."""

    findings = []
    numbers = {"rider_height": round(report.rider_height, 4), "rest_gap": round(report.rest_gap, 4), "clips": {}}
    for clip in report.clips:
        numbers["clips"][clip.mount_clip] = {"rider_clip": clip.rider_clip, "sunk": round(clip.worst_sunk, 4), "sunk_frame": clip.worst_sunk_frame,
                                             "gap": round(clip.worst_gap, 4), "gap_frame": clip.worst_gap_frame,
                                             "mount_seconds": round(clip.mount_seconds, 3), "rider_seconds": round(clip.rider_seconds, 3)}
        if role_of(clip.mount_clip) in TIMED_ROLES and clip.rider_seconds > TIMING_SLACK * clip.mount_seconds:
            findings.append({"rule": "TRIPO-RIDER-CLIP-LENGTH", "subject": clip.mount_clip,
                             "message": f"the rider's {clip.rider_clip} runs {clip.rider_seconds:.1f} s over the mount's {clip.mount_seconds:.1f} s "
                                        f"(at most {TIMING_SLACK} times): cut it to the mount's clip with the job's tripo.trim_end",
                             "rider_seconds": clip.rider_seconds, "mount_seconds": clip.mount_seconds})
        if role_of(clip.mount_clip) in NOT_JUDGED:
            continue
        if clip.worst_sunk > SUNK_LIMIT:
            findings.append({"rule": "TRIPO-RIDER-SUNK", "subject": clip.mount_clip,
                             "message": f"{clip.worst_sunk:.1%} of the rider ({clip.rider_clip}) lies inside the mount at frame {clip.worst_sunk_frame} "
                                        f"(limit {SUNK_LIMIT:.0%}, vanilla's horse and rider 5.9%): the legs or seat go through the body",
                             "share": clip.worst_sunk, "frame": clip.worst_sunk_frame})
        if clip.worst_gap > GAP_LIMIT:
            findings.append({"rule": "TRIPO-RIDER-OFF-SEAT", "subject": clip.mount_clip,
                             "message": f"the saddle moves {clip.worst_gap:.1%} of the rider's height from the Saddle_Node at frame {clip.worst_gap_frame} "
                                        f"(limit {GAP_LIMIT:.0%}, vanilla 1.5%): the rider floats above or sinks into the saddle",
                             "gap": clip.worst_gap, "frame": clip.worst_gap_frame})
    return findings, numbers
