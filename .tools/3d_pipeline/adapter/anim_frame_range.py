"""Check that an exported `.anim` holds one sample per frame of the action it was exported from.

io_pdx_mesh's animation export operator (`bpy.ops.io_pdx_mesh.export_anim`) uses its start and end
frames only when the scene's "custom range" export setting is on; otherwise it exports the scene's
frame range. Clips exported in a live session came out padded or cut to whatever range the scene last
held (80 or 85 samples). The kit exports with `export_animfile` and the action's own range, and checks
the written file here. Pure Python: the `.anim` is read with the pipeline's `lib/pdx_binary.py`.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

PDX_BINARY = Path(__file__).resolve().parents[1] / "lib" / "pdx_binary.py"


class AnimFrameRangeError(RuntimeError):
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
