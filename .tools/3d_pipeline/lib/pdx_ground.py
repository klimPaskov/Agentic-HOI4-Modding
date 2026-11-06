"""Correct ground contact in an exported `.anim`, without Blender.

Each frame is skinned from the bytes with `pdx_deform`. The root bone's existing translation keys
are then shifted up or down so the unit's lowest point meets the rest pose's ground in every frame.
A death clip is only lifted where it sinks: a body may fall and lie, but not into the ground.

Only existing keys change, in place: the file keeps its size, joints, frame count and every other
value. A clip whose root bone has no translation channel cannot be corrected this way and is
reported instead.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import numpy as np

from . import pdx_deform
from .pdx_binary import PdxFormatError, read


@dataclass
class GroundCorrection:
    root: Optional[str]
    frames: int
    largest_shift: float  # as a share of the unit's height
    corrected: bool
    reason: str = ""


def _samples_t_offset(data: bytes) -> int:
    """Byte offset of the first float of the `samples` block's `t` array."""

    start = data.find(b"[samples\0")
    if start < 0:
        raise PdxFormatError("the file has no samples block")
    marker = data.find(b"!\x01tf", start)
    if marker < 0:
        raise PdxFormatError("the samples block has no translation channel")
    return marker + 4 + 4  # header, then the int32 count


def _root(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, keyed: List[str]) -> Optional[str]:
    for index, parent in enumerate(mesh.parents):
        name = mesh.bones[index]
        if parent < 0 and name in keyed:
            return name
    return None


def ground(mesh_path: Path, anim_path: Path, out_path: Path, death: bool = False, tolerance: float = 0.002) -> GroundCorrection:
    """Write `out_path`: `anim_path` with its root translation shifted so the lowest point meets the ground."""

    data = bytearray(Path(anim_path).read_bytes())
    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)
    info = read(anim_path).child("info")
    keyed = [joint.name for joint in info.children if "t" in str((joint.properties.get("sa") or [""])[0])]
    root = _root(mesh, anim, keyed)
    if root is None:
        Path(out_path).write_bytes(bytes(data))
        return GroundCorrection(None, anim.frames, 0.0, False, "the root bone has no translation keys")
    height = max(mesh.height, 1e-6)
    floor = float(mesh.positions[:, 1].min())
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    shifts = np.zeros(anim.frames)
    for frame in range(anim.frames):
        lowest = float(pdx_deform.skin(mesh, matrices[frame])[:, 1].min())
        gap = floor - lowest  # positive: below the ground
        if death:
            shifts[frame] = gap if gap > tolerance * height else 0.0
        elif abs(gap) > tolerance * height:
            shifts[frame] = gap
    if not shifts.any():
        Path(out_path).write_bytes(bytes(data))
        return GroundCorrection(root, anim.frames, 0.0, False, "already on the ground")
    offset = _samples_t_offset(bytes(data))
    slot = keyed.index(root)
    for frame in range(anim.frames):
        # Frame-major: every keyed joint's (x, y, z) per frame, in info order. PDX is Y up.
        position = offset + 4 * (3 * (frame * len(keyed) + slot) + 1)
        (y,) = struct.unpack_from("<f", data, position)
        struct.pack_into("<f", data, position, y + float(shifts[frame]))
    Path(out_path).write_bytes(bytes(data))
    return GroundCorrection(root, anim.frames, float(np.abs(shifts).max() / height), True)
