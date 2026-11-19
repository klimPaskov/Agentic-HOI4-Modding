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
# A unit under a tall load (a war elephant's howdah tower) is judged against vanilla's own large units, not against the horse, whose legs show
# in the map camera. Measured with this module on vanilla's gfx (2026-11-17), the clip against the unit's idle: the wheeled mechanized
# vehicles (`GER_mechanized_01`, `SOV_mechanized_01`, `US_mechanized_01`) move 0.000 and attack 0.000, `FIN_mechanized_vehicle_2` moves 0.001,
# the guns `artillery` and `ENG_artillery` move 0.002 and 0.003 (`ENG_anti_tank` 0.003) and attack 0.35 and 0.24, `generic_railway_gun` moves
# 0.000 and attacks 0.034, the locomotive moves 0.02. (Tracked tanks 0.4 to 0.9 and the motorbike 0.33 turn their tracks or wheels, which a
# loaded animal does not. The camel idles lying, so its clips are no reference.) A large unit of vanilla's moves almost without changing its
# silhouette, so a heavy loaded unit's move is held to `LOADED_MOVE_READ`, the artillery's 0.002, and its attack, defend and the gap between
# its clips to `LOADED_READ`, the railway gun's attack, 0.034. The tall load hides the legs: the war elephant's stride and fold read 0.014.
# A yaw reads 0.17 on the elephant and two reviews read it as veering, so no limit is taken from that unit's own result.
LOADED_MOVE_READ = 0.002
LOADED_READ = 0.034
MAX_FRAMES = 30  # frames sampled per clip (evenly), and per idle
# A humanoid's attack and defend against its idle, in pixels changed at game size (`read_pixels`), not as a share of the idle's area: the
# player sees pixels, and a slender body has a small area, so a share made a small motion of the round 4 zombie look large. Measured with this
# module on the exported files of the humanoids two fresh reviewers passed at game size (2026-11-18), the 90th percentile frame: the orc
# (orc_k) attack 441 and defend 453, the ogre (ogre_l) attack 320 and defend 166, the dwarf (dwarf_f) attack 530 and defend 493. The zombie
# (zombie_w), whose attack and defend both reviewers read as its idle from the game camera: attack 192, defend 104 (its recoil peaks at 232 for
# a tenth of a 5 second clip). As shares of the idle's area the zombie's defend (0.164) read above the ogre's (0.143) that passed. The limits
# are the lowest passing readings rounded down: an attack must change at least `MIN_HUMANOID_READ_PIXELS["attack"]`, a defend
# `["defend"]`. Vanilla has no melee attack or defend to calibrate on (`lib/tripo_strike.py`): its infantry attacks shoot from the idle's stance.
MIN_HUMANOID_READ_PIXELS = {"attack": 300.0, "defend": 160.0}


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


def pixel_changes(frames: Sequence[np.ndarray], idle: Sequence[np.ndarray]) -> List[int]:
    """Per clip frame, the least change against an idle frame, in pixels of the map camera at game size."""

    return [min(change(frame, other) for other in idle) for frame in frames]


def read_pixels(frames: Sequence[np.ndarray], idle: Sequence[np.ndarray]) -> float:
    """The humanoid reading (TRIPO-MAP-READ for a humanoid): the `READ_PERCENTILE` percentile over the clip's frames of the least change
    against an idle frame, in pixels of the unit drawn `MAP_PIXELS` tall. Not over the idle's area, see `MIN_HUMANOID_READ_PIXELS`."""

    changes = pixel_changes(frames, idle)
    return round(float(np.percentile(changes, READ_PERCENTILE)), 1) if changes else 0.0


def clip_reading(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, idle: pdx_deform.Animation) -> float:
    camera = MapCamera(mesh)
    return read_against_idle(camera, camera.frames(anim), camera.frames(idle))


def loaded_limit(limit: float, loaded: bool, move: bool = False) -> float:
    """The least reading of a unit that carries a tall load: vanilla's own large units' (`LOADED_MOVE_READ` for a move from the idle,
    `LOADED_READ` for the rest), never more than the horse's `limit`."""

    return min(limit, LOADED_MOVE_READ if move else LOADED_READ) if loaded else limit


def humanoid_findings(mesh: pdx_deform.SkinnedMesh, anims: dict) -> tuple:
    """TRIPO-MAP-READ for a humanoid: the attack and the defend each against the idle, in pixels at game size (`read_pixels`), under
    `MIN_HUMANOID_READ_PIXELS`. Returns (findings, numbers). A unit without an idle clip gets no reading."""

    by_role = {clip.rsplit("_", 1)[-1]: clip for clip in anims}
    if "idle" not in by_role:
        return [], {}
    camera = MapCamera(mesh)
    idle = camera.frames(anims[by_role["idle"]])
    findings, numbers = [], {}
    for role, limit in MIN_HUMANOID_READ_PIXELS.items():
        clip = by_role.get(role)
        if clip is None:
            continue
        changes = pixel_changes(camera.frames(anims[clip]), idle)
        reading = round(float(np.percentile(changes, READ_PERCENTILE)), 1)
        numbers[clip] = {"pixels": reading, "peak_pixels": int(max(changes)), "limit": limit}
        if reading < limit:
            findings.append({"rule": "TRIPO-MAP-READ", "subject": clip, "share": reading, "against": "idle",
                             "message": f"from the map camera the {role} changes {reading:.0f} pixels of the idle's silhouette at game size in its "
                                        f"{READ_PERCENTILE:.0f}th percentile frame (at least {limit:.0f}, the lowest of the humanoids reviewers passed): "
                                        "it reads as the idle at map size"})
    return findings, numbers

