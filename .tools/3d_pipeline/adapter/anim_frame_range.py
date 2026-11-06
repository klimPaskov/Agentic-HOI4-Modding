"""Check that an exported `.anim` holds one sample per frame of its action, at HOI4's 30 frames a second.

io_pdx_mesh's animation export operator (`bpy.ops.io_pdx_mesh.export_anim`) uses its start and end
frames only when the scene's "custom range" export setting is on; otherwise it exports the scene's
frame range. Clips exported in a live session came out padded or cut to whatever range the scene last
held (80 or 85 samples). The kit exports with `export_animfile` and the action's own range, and checks
the written file here.

io_pdx_mesh also writes the scene's frame rate into the file. A scene started from Blender's factory
settings runs at 24, so every clip of one mod came out at 24 while vanilla soldiers, riders and horses
play at 30 (and Paradox's own exporter knows only 15, 30 and 60). `retime_action` scales an action's
keys so it keeps its length in seconds at 30, then the exporter runs at 30 and `verify_fps` checks the
file. Pure Python: the `.anim` is read with the pipeline's `lib/pdx_binary.py`, and the action is
reached through its attributes, so the module imports without Blender.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

PDX_BINARY = Path(__file__).resolve().parents[1] / "lib" / "pdx_binary.py"


HOI4_FPS = 30
# Vanilla organic clips read 30.0 to 30.9 (their exporter rounds the length); ours are written as exactly 30.
FPS_TOLERANCE = 0.01


class AnimFrameRangeError(RuntimeError):
    pass


class AnimFpsError(RuntimeError):
    pass


def _pdx_binary():
    name = "hoi4_kit_pdx_binary"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, PDX_BINARY)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def exported_samples(path: Path) -> int:
    pdx = _pdx_binary()
    return pdx.summarize_anim(pdx.read(Path(path))).samples


def verify_frame_range(path: Path, frame_start: int, frame_end: int) -> int:
    """The file's sample count; raise when it is not the action's frame count."""

    expected = int(frame_end) - int(frame_start) + 1
    samples = exported_samples(path)
    if samples != expected:
        kind = "padded" if samples > expected else "cut short"
        raise AnimFrameRangeError(
            f"{Path(path).name} holds {samples} samples but its action spans frames {frame_start} to {frame_end} "
            f"({expected}): the clip was {kind}. Export it with the action's own frame range."
        )
    return samples


def verify_fps(path: Path, expected: float = HOI4_FPS) -> float:
    """The file's frame rate; raise when it is not `expected`."""

    pdx = _pdx_binary()
    fps = float(pdx.summarize_anim(pdx.read(Path(path))).fps)
    if abs(fps - expected) > FPS_TOLERANCE:
        raise AnimFpsError(
            f"{Path(path).name} plays at {fps:g} frames a second, not {expected:g}: export it with the scene at "
            f"{expected:g} fps (render.fps {expected:g}, fps_base 1) after retiming its keys with retime_action."
        )
    return fps


def action_fcurves(action) -> list:
    """Every F-curve of an action: a layered action's channel bags, or a legacy action's own list."""

    curves, seen = [], set()
    for layer in getattr(action, "layers", None) or []:
        for strip in layer.strips:
            for bag in getattr(strip, "channelbags", None) or []:
                for curve in bag.fcurves:
                    if id(curve) not in seen:
                        seen.add(id(curve))
                        curves.append(curve)
    if not curves:
        curves = list(getattr(action, "fcurves", None) or [])
    return curves


def retime_action(action, start: int, end: int, source_fps: float, target_fps: float = HOI4_FPS) -> tuple:
    """Scale the action's key times so it lasts as long at `target_fps` as it did at `source_fps`.

    Keys and handles move away from `start` by target / source (24 to 30 is 1.25). Returns the new
    (start, end); the clip then has one sample per frame of that range. Nothing changes at the same rate.
    """

    factor = float(target_fps) / float(source_fps)
    if abs(factor - 1.0) < 1e-9:
        return int(start), int(end)
    for curve in action_fcurves(action):
        for key in curve.keyframe_points:
            for point in (key.co, key.handle_left, key.handle_right):
                point[0] = start + (point[0] - start) * factor
        if hasattr(curve, "update"):
            curve.update()
    new_end = int(start) + int(round((end - start) * factor))
    if getattr(action, "use_frame_range", False):
        action.frame_start, action.frame_end = start, new_end
    return int(start), new_end
