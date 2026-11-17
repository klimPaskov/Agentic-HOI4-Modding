"""How far a clip's silhouette in the HOI4 map camera differs from the idle's, at the size a player sees the unit.

Pure numpy on the exported `.mesh` and `.anim` (`lib/pdx_deform`), in the file's own space (Y up). A role reads as itself on the map only
when its silhouette there changes shape, not when it slides or bobs: a review failed a war elephant's attack (its body pitched 12 degrees
under the tower) and its defend (a small brace) as "the same as the idle at map size".

- Camera: the review sheets' `hoi4` view, 25 degrees round from the front and 55 above the horizon, orthographic.
- Size: one pixel is `1 / MAP_PIXELS` of the rest height, the unit's height on the game-size sheet (about 60 px).
- Silhouette: every triangle filled (points spread over each face half a pixel apart), so a coarse vanilla mesh and a dense Tripo one
  fill the same pixels.
- Change of one frame: against each idle frame, the pixels either silhouette covers that the other, grown by one pixel, does not (so a
  sub-pixel shift does not count), after the shift within `ALIGN_PIXELS` that makes them fewest (moving or bobbing the same shape does
  not count), over the idle's area. The frame's change is the least over the idle frames.
- Reading of a clip: the `READ_PERCENTILE` percentile of its frames' changes, so a pose held for a tenth of the clip counts and one
  stray frame does not.

Measured with this module (2026-11-16) on vanilla `cavalry_horse.mesh` against its forward idle (`cavalry_horse_idle_forward`, the idle the
walk and the charge start from): walk 0.175, charge 0.188, charge_2 0.187. The war elephant of round 9: attack 0.149, defend 0.008, move
0.011, retreat 0.030. `MIN_READ` is the horse's charge, vanilla's mount attack, rounded down: an attack or a defend must change the
silhouette at least as much as a vanilla horse's charge does. (Vanilla's camel idles lying down, so its clips are not a reference.)

Against the horse's walk instead of its idle, its charge reads 0.159 and charge_2 0.167. `MIN_GAIT_READ` is the charge's, rounded down: a
retreat must differ from the move at least as much as a vanilla horse's charge differs from its walk. Run 3 of the war elephant trotted to
retreat and walked to move, and its retreat read 0.016 against the move (offline on the round 9 mesh), the same gait to two reviewers.
"""

from __future__ import annotations

import math
from typing import List, Optional, Sequence

import numpy as np

from . import pdx_deform, pdx_motion

MAP_AZIMUTH = 25.0
MAP_ELEVATION = 55.0
MAP_PIXELS = 60
ALIGN_PIXELS = 6  # a tenth of the height: the largest bob or slide that is not a new pose
READ_PERCENTILE = 90.0
MIN_READ = 0.18
MIN_GAIT_READ = 0.15
# A unit under a tall load (a war elephant's howdah tower) shows its legs and body little in the map camera, which looks down at 55 degrees.
# Played offline on the war elephant of run 7 (2026-11-17) against its idle: the legs' stride and fold alone read 0.01 to 0.014 (a vanilla
# horse's walk 0.175), a body pitch of 8 degrees (the most that keeps the forefeet on the ground) 0.03, a rock of the whole body of 12 degrees
# 0.09, a sway of the whole body about the vertical of 10 degrees 0.17 (two reviews read that as veering off the heading) and a neck swing
# of 30 degrees 0.12. The neck cannot swing: the tower's front is one skin with the head and neck, and 10 degrees at the first neck bone
# tears 29% of the seam's edges (TRIPO-LOAD-SEAM, limit 2%). With the head bone alone (30 degrees keeps the seam at 1.6%), the spread
# forelegs, a rock of 8 degrees and the 8 degree pitch, the clips read 0.06 (move), 0.10 (defend) and 0.09 and 0.05 (retreat from the move
# and the defend). So no yaw-free clip of a loaded unit that keeps its skin reaches the horse's limits, and `loaded_limit` takes
# LOADED_SHARE of them: 0.045 for the move and the gait pairs, 0.054 for an attack or a defend from the idle. Reviewers failed 0.01 (run 5,
# the idle at map size) and read 0.17 as veering, and no review has yet seen a clip between, so run 8's reviews are what confirms the share.
LOADED_SHARE = 0.3
MAX_FRAMES = 30  # frames sampled per clip (evenly), and per idle


def front_of(mesh: pdx_deform.SkinnedMesh) -> np.ndarray:
    """The horizontal direction the unit faces: from the mean of its joints toward its head joint (a bone named `...Head`)."""

    joints = pdx_motion.rest_joints(mesh)
    heads = [index for index, name in enumerate(mesh.bones) if name.endswith("Head")]
    if not heads:
        return np.array([0.0, 0.0, -1.0])
    vector = joints[heads[0]] - joints.mean(axis=0)
    vector[1] = 0.0
    length = float(np.linalg.norm(vector))
    return vector / length if length > 1e-9 else np.array([0.0, 0.0, -1.0])


def map_axes(front: np.ndarray, azimuth: float = MAP_AZIMUTH, elevation: float = MAP_ELEVATION):
    """The screen's right and up axes for the map camera."""

    up = np.array([0.0, 1.0, 0.0])
    lateral = np.cross(up, front)
    a, e = math.radians(azimuth), math.radians(elevation)
    toward = math.cos(e) * (math.cos(a) * front + math.sin(a) * lateral) + math.sin(e) * up
    toward /= np.linalg.norm(toward)
    right = np.cross(up, toward)
    right /= np.linalg.norm(right)
    return right, np.cross(toward, right)


def face_samples(points: np.ndarray, triangles: np.ndarray, spacing: float) -> np.ndarray:
    """The vertices plus points spread over every face about `spacing` apart."""

    out = [points]
    a, b, c = points[triangles[:, 0]], points[triangles[:, 1]], points[triangles[:, 2]]
    longest = np.maximum.reduce([np.linalg.norm(b - a, axis=1), np.linalg.norm(c - b, axis=1), np.linalg.norm(a - c, axis=1)])
    steps = np.clip(np.ceil(longest / max(spacing, 1e-9)).astype(int), 1, 64)
    for count in np.unique(steps):
        if count < 2:
            continue
        pick = steps == count
        grid = np.array([(i, j) for i in range(count + 1) for j in range(count + 1 - i)], dtype=float) / count
        u, v = grid[:, 0][None, :, None], grid[:, 1][None, :, None]
        out.append((a[pick][:, None] + u * (b[pick] - a[pick])[:, None] + v * (c[pick] - a[pick])[:, None]).reshape(-1, 3))
    return np.concatenate(out)


def _grow(mask: np.ndarray) -> np.ndarray:
    padded = np.pad(mask, 1)
    out = np.zeros_like(mask)
    for dy in range(3):
        for dx in range(3):
            out |= padded[dy:dy + mask.shape[0], dx:dx + mask.shape[1]]
    return out


class MapCamera:
    """The map view of one mesh: a fixed screen frame around its rest pose, one pixel `1 / MAP_PIXELS` of its height."""

    def __init__(self, mesh: pdx_deform.SkinnedMesh):
        self.mesh = mesh
        keep = ~mesh.collision if len(mesh.collision) == len(mesh.positions) else np.ones(len(mesh.positions), bool)
        self.triangles = mesh.triangles[keep[mesh.triangles].all(axis=1)]
        self.right, self.up = map_axes(front_of(mesh))
        self.pixel = max(mesh.height, 1e-9) / MAP_PIXELS
        screen = self._screen(mesh.positions[keep])
        margin = MAP_PIXELS  # the unit may move a whole height in any direction
        self.origin = screen.min(axis=0) - margin * self.pixel
        self.size = int(np.ceil(float(np.ptp(screen, axis=0).max()) / self.pixel)) + 2 * margin

    def _screen(self, points: np.ndarray) -> np.ndarray:
        return np.stack([points @ self.right, points @ self.up], axis=1)

    def silhouette(self, posed: np.ndarray) -> np.ndarray:
        cells = np.floor((self._screen(face_samples(posed, self.triangles, 0.5 * self.pixel)) - self.origin) / self.pixel).astype(int)
        cells = np.clip(cells, 0, self.size - 1)
        mask = np.zeros((self.size, self.size), dtype=bool)
        mask[cells[:, 1], cells[:, 0]] = True
        return mask

    def frames(self, anim: pdx_deform.Animation, count: int = MAX_FRAMES) -> List[np.ndarray]:
        matrices = pdx_deform.skinning_matrices(self.mesh, anim)
        picks = np.unique(np.linspace(0, matrices.shape[0] - 1, min(count, matrices.shape[0])).round().astype(int))
        return [self.silhouette(pdx_deform.skin(self.mesh, matrices[index])) for index in picks]


def _centre(mask: np.ndarray) -> np.ndarray:
    rows, cols = np.nonzero(mask)
    return np.array([rows.mean(), cols.mean()]) if len(rows) else np.zeros(2)


def _shifted(mask: np.ndarray, dy: int, dx: int) -> np.ndarray:
    return np.roll(np.roll(mask, dy, axis=0), dx, axis=1)


def change(frame: np.ndarray, idle: np.ndarray, align: int = ALIGN_PIXELS) -> int:
    """Pixels the two silhouettes do not share (each against the other grown by a pixel), after the best shift within `align` pixels."""

    grown_idle = _grow(idle)
    grown_frame = _grow(frame)
    offset = np.round(_centre(idle) - _centre(frame)).astype(int)
    start = np.clip(offset, -align, align)
    best: Optional[int] = None
    for dy in range(max(-align, start[0] - 2), min(align, start[0] + 2) + 1):
        for dx in range(max(-align, start[1] - 2), min(align, start[1] + 2) + 1):
            moved, moved_grown = _shifted(frame, dy, dx), _shifted(grown_frame, dy, dx)
            value = int(((moved & ~grown_idle) | (idle & ~moved_grown)).sum())
            best = value if best is None else min(best, value)
    return int(best or 0)


def read_against_idle(camera: MapCamera, frames: Sequence[np.ndarray], idle: Sequence[np.ndarray]) -> float:
    """The clip's reading: the `READ_PERCENTILE` percentile over its frames of the least change against an idle frame, over the idle's area."""

    area = float(np.mean([mask.sum() for mask in idle])) or 1.0
    changes = [min(change(frame, other) for other in idle) / area for frame in frames]
    return round(float(np.percentile(changes, READ_PERCENTILE)), 4) if changes else 0.0


def clip_reading(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, idle: pdx_deform.Animation) -> float:
    camera = MapCamera(mesh)
    return read_against_idle(camera, camera.frames(anim), camera.frames(idle))


def loaded_limit(limit: float, loaded: bool) -> float:
    """The least reading of a unit that carries a tall load: LOADED_SHARE of the horse's limit."""

    return round(LOADED_SHARE * limit, 4) if loaded else limit
