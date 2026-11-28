"""What a unit's clips show in the game's division designer preview, measured on the exported files (D-140, D-174).

Pure numpy on the exported `.mesh` and `.anim` (`lib/pdx_deform`), the files the game loads, seen with the designer's camera
(`lib/designer_preview.VIEW`, against the unit's rest facing). Two kinds of measure:

**The pose on the designer screen** (`ScreenPose`). Each frame's pose is the screen positions of the body's end joints: the joints with no
child that carry skin or hang from a bone that does (the hands, the feet, the head's top, a wing's or a tail's tip, a weapon). The positions
are taken about their own mean, so a slide or a bob is no new pose, and over the rest height on the screen, so a giant and a dwarf compare
alike. Two frames differ by the mean distance their end joints moved (`pose_distance`). This is what a viewer reads in the designer's
small frame: where the limbs are, not which pixels a thin limb crossed. At the designer's size a hand that moves a little crosses
thousands of pixels, and the silhouette's changed pixels and their shares separated no clip a reviewer failed from one a reviewer passed
(the calibration in `tripo/designer_checks.py`).

- `spread`: the largest pose distance between two frames of a clip. An attack whose frames barely differ (the devil's strike) has a small
  spread.
- `held_share`: the largest share of a clip's frames within `HOLD_DISTANCE` of one of its frames: a clip that holds one pose.
- `alike_share(a, b)`: the share of clip a's frames within `ALIKE_DISTANCE` of some frame of clip b: how much of a the clip b shows too.

**The silhouette at the designer's pixel size** (`DesignerCamera`): one pixel is the designer frame's width in game units over its 249 pixels,
divided by the unit's entity scale (`pixel_size`), so a unit fills the frame as it does in the game. Faces are filled
(`map_read.face_samples`).

- `death_end`: the last frame of a death. `solidity` is the silhouette's area over its convex hull's: a body lying with its limbs and head
  apart has gaps between them, while a shapeless mound or a stiff plank fills its hull. `weapon_gap` is how many pixels the weapon's
  silhouette lies from the body's.
- `head_hidden`: per frame, the share of the head's pixels that another part (a wing, an arm, a weapon) covers nearer the camera.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import designer_preview, map_read, pdx_deform, pdx_motion

HOLD_DISTANCE = 0.03  # two frames whose end joints moved less than this share of the height on average show the same pose
ALIKE_DISTANCE = 0.03
HEAD_WORDS = ("head",)
NECK_WORDS = ("neck", "head")


def end_joints(mesh: pdx_deform.SkinnedMesh) -> List[int]:
    """The bones with no child that carry skin, or whose parent does (an end bone such as a head's top carries none itself)."""

    children = [0] * len(mesh.bones)
    for parent in mesh.parents:
        if parent >= 0:
            children[parent] += 1
    weighted = np.zeros(len(mesh.bones), bool)
    used = mesh.joints[mesh.weights > 0]
    weighted[np.unique(used[used >= 0])] = True
    return [i for i in range(len(mesh.bones)) if not children[i] and (weighted[i] or (mesh.parents[i] >= 0 and weighted[mesh.parents[i]]))]


def view_axes(mesh: pdx_deform.SkinnedMesh, view: Tuple[float, float] = designer_preview.VIEW) -> Tuple[np.ndarray, np.ndarray]:
    """The designer screen's right and up axes for this mesh, the camera turned against its rest facing.

    `designer_preview.VIEW` is the review renderer's view in Blender. The `.mesh` file's own frame is its mirror, so the same camera stands
    at the opposite azimuth here. Checked on the ZIN devil's retreat (2026-11-28): the sheet showed a wing over the head in frames 12 to 20,
    and from the `.mesh` frame only the mirrored azimuth reproduced it (the head 81% hidden at worst, 0% from the other side)."""

    return map_read.map_axes(map_read.front_of(mesh), -view[0], view[1])


class ScreenPose:
    """Each clip's frames as end-joint positions on the designer screen, about their mean, over the rest height on the screen."""

    def __init__(self, mesh: pdx_deform.SkinnedMesh, view: Tuple[float, float] = designer_preview.VIEW):
        self.mesh = mesh
        self.right, self.up = view_axes(mesh, view)
        self.joints = end_joints(mesh)
        keep = ~mesh.collision if len(mesh.collision) == len(mesh.positions) else np.ones(len(mesh.positions), bool)
        self.height = max(float(np.ptp(mesh.positions[keep] @ self.up)), 1e-9)

    def frames(self, anim: pdx_deform.Animation) -> np.ndarray:
        """(F, J, 2) the end joints on the screen in every frame."""

        joints = pdx_motion.posed_joints(self.mesh, anim)[:, self.joints]
        screen = np.stack([joints @ self.right, joints @ self.up], axis=-1)
        return (screen - screen.mean(axis=1, keepdims=True)) / self.height


def pose_distance(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    """(Fa, Fb) the mean distance the end joints lie apart between each frame of `first` and each of `second`."""

    return np.linalg.norm(first[:, None] - second[None], axis=-1).mean(axis=-1)


def spread(frames: np.ndarray) -> float:
    return round(float(pose_distance(frames, frames).max()), 3) if len(frames) else 0.0


def held_share(frames: np.ndarray, distance: float = HOLD_DISTANCE) -> float:
    if not len(frames):
        return 0.0
    near = pose_distance(frames, frames) < distance
    return round(float(near.sum(axis=1).max()) / len(frames), 3)


def alike_share(first: np.ndarray, second: np.ndarray, distance: float = ALIKE_DISTANCE) -> float:
    if not len(first) or not len(second):
        return 0.0
    return round(float((pose_distance(first, second).min(axis=1) < distance).mean()), 3)


def pixel_size(entity_scale: float) -> float:
    """One designer pixel in the mesh's own units, for a unit drawn at `entity_scale`."""

    return designer_preview.ortho_for(entity_scale) / designer_preview.PREVIEW_PX


def bone_vertices(mesh: pdx_deform.SkinnedMesh, words: Sequence[str]) -> np.ndarray:
    """Vertices whose largest weight is on a bone whose name holds one of `words` (any case)."""

    dominant = pdx_deform.dominant_bones(mesh)
    names = [name.lower() for name in mesh.bones]
    picked = np.array([any(word in name for word in words) for name in names] + [False])
    return picked[np.where(dominant < 0, len(names), dominant)]


class DesignerCamera:
    """The designer view of one mesh: a fixed screen frame around its rest pose at the designer's pixel size."""

    def __init__(self, mesh: pdx_deform.SkinnedMesh, entity_scale: float, view: Tuple[float, float] = designer_preview.VIEW):
        self.mesh = mesh
        keep = ~mesh.collision if len(mesh.collision) == len(mesh.positions) else np.ones(len(mesh.positions), bool)
        self.keep = keep
        self.triangles = mesh.triangles[keep[mesh.triangles].all(axis=1)]
        self.right, self.up = view_axes(mesh, view)
        self.toward = np.cross(self.right, self.up)  # from the unit toward the camera
        self.pixel = pixel_size(entity_scale)
        screen = self._screen(mesh.positions[keep])
        self.height_px = float(np.ptp(screen[:, 1])) / self.pixel
        margin = int(np.ceil(self.height_px))  # the unit may move a whole height in any direction
        self.origin = screen.min(axis=0) - margin * self.pixel
        self.size = int(np.ceil(float(np.ptp(screen, axis=0).max()) / self.pixel)) + 2 * margin

    def _screen(self, points: np.ndarray) -> np.ndarray:
        return np.stack([points @ self.right, points @ self.up], axis=1)

    def cells(self, points: np.ndarray) -> np.ndarray:
        cells = np.floor((self._screen(points) - self.origin) / self.pixel).astype(int)
        return np.clip(cells, 0, self.size - 1)

    def samples(self, posed: np.ndarray, triangles: Optional[np.ndarray] = None) -> np.ndarray:
        """Points over the faces of `triangles` (default the whole visible mesh), only those faces' own corners among them."""

        triangles = self.triangles if triangles is None else triangles
        if not len(triangles):
            return np.zeros((0, 3))
        used, local = np.unique(triangles, return_inverse=True)
        return map_read.face_samples(posed[used], local.reshape(triangles.shape), 0.5 * self.pixel)

    def silhouette(self, posed: np.ndarray, triangles: Optional[np.ndarray] = None) -> np.ndarray:
        cells = self.cells(self.samples(posed, triangles))
        mask = np.zeros((self.size, self.size), dtype=bool)
        mask[cells[:, 1], cells[:, 0]] = True
        return mask

    def part_triangles(self, vertices: np.ndarray) -> np.ndarray:
        """The camera's triangles whose three corners are all in `vertices`."""

        return self.triangles[vertices[self.triangles].all(axis=1)]


def _turn(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """The z of the cross product of (b - a) and (c - a): above 0 when a, b, c turn counter-clockwise."""

    return float((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))


def _hull_area(points: np.ndarray) -> float:
    """The area of the convex hull of 2D points (Andrew's monotone chain)."""

    pts = np.unique(points, axis=0)
    if len(pts) < 3:
        return 0.0
    pts = pts[np.lexsort((pts[:, 1], pts[:, 0]))]

    def half(sequence):
        out: List[np.ndarray] = []
        for p in sequence:
            while len(out) >= 2 and _turn(out[-2], out[-1], p) <= 0:
                out.pop()
            out.append(p)
        return out

    hull = np.array(half(pts)[:-1] + half(pts[::-1])[:-1], float)
    x, y = hull[:, 0], hull[:, 1]
    return 0.5 * abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def solidity(mask: np.ndarray) -> float:
    """The silhouette's area over the area of its convex hull, counting each pixel as its four corners."""

    rows, cols = np.nonzero(mask)
    if not len(rows):
        return 0.0
    corners = np.concatenate([np.stack([cols + dx, rows + dy], axis=1) for dx in (0, 1) for dy in (0, 1)])
    hull = _hull_area(corners.astype(float))
    return float(mask.sum()) / hull if hull > 0 else 0.0


def _gap(first: np.ndarray, second: np.ndarray, limit: int = 64) -> int:
    """How many pixels `first` must grow before it touches `second` (0 when they touch already), at most `limit`."""

    if not first.any() or not second.any():
        return 0
    grown = first.copy()
    for step in range(limit + 1):
        if (grown & second).any():
            return step
        grown = map_read._grow(grown)
    return limit


def death_end(camera: DesignerCamera, anim: pdx_deform.Animation, weapon: Optional[np.ndarray] = None) -> Dict[str, float]:
    """The last frame of a death: the solidity of the body's silhouette (`solidity`), and with `weapon` (a vertex mask) the gap in pixels
    between the weapon's silhouette and the rest of the body (`weapon_gap`)."""

    matrices = pdx_deform.skinning_matrices(camera.mesh, anim)
    posed = pdx_deform.skin(camera.mesh, matrices[-1])
    body_tris = camera.triangles if weapon is None else camera.part_triangles(~weapon)
    body = camera.silhouette(posed, body_tris)
    out: Dict[str, float] = {"solidity": round(solidity(body), 3)}
    if weapon is not None:
        weapon_tris = camera.part_triangles(weapon)
        out["weapon_gap"] = _gap(camera.silhouette(posed, weapon_tris), body) if len(weapon_tris) else 0
    return out


def head_hidden(camera: DesignerCamera, anim: pdx_deform.Animation, step: int = 2, exclude: Optional[np.ndarray] = None) -> List[float]:
    """Every `step`-th frame, the share of the head's pixels that another part covers nearer the camera. The neck is not a cover (it joins
    the head), nor the vertices of `exclude` (a held weapon in the attack). A mesh with no head bone gets an empty list."""

    head = bone_vertices(camera.mesh, HEAD_WORDS) & camera.keep
    if not head.any():
        return []
    joined = bone_vertices(camera.mesh, NECK_WORDS)
    if exclude is not None:
        joined = joined | exclude
    head_tris = camera.part_triangles(head)
    other_tris = camera.triangles[~joined[camera.triangles].any(axis=1)]
    matrices = pdx_deform.skinning_matrices(camera.mesh, anim)
    shares = []
    for index in range(0, matrices.shape[0], max(1, step)):
        posed = pdx_deform.skin(camera.mesh, matrices[index])
        head_pts, other_pts = camera.samples(posed, head_tris), camera.samples(posed, other_tris)
        head_cells, other_cells = camera.cells(head_pts), camera.cells(other_pts)
        head_key = head_cells[:, 1] * camera.size + head_cells[:, 0]
        other_key = other_cells[:, 1] * camera.size + other_cells[:, 0]
        head_depth, other_depth = head_pts @ camera.toward, other_pts @ camera.toward
        order = np.argsort(-head_depth)
        keys, first = np.unique(head_key[order], return_index=True)
        nearest_head = head_depth[order][first]
        inside = np.isin(other_key, keys)
        if not inside.any():
            shares.append(0.0)
            continue
        okeys, odepth = other_key[inside], other_depth[inside]
        oorder = np.argsort(-odepth)
        ok, ofirst = np.unique(okeys[oorder], return_index=True)
        covered = int((odepth[oorder][ofirst] > nearest_head[np.searchsorted(keys, ok)] + 0.5 * camera.pixel).sum())
        shares.append(round(covered / len(keys), 3))
    return shares
