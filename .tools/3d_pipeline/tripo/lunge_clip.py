"""Give an attack its lunge step back: copy one clip's forward travel from a Tripo export made with "Animation in Place" off into the same
clip of the in-place export, capped. No Blender.

    py -3.13 -B .tools/3d_pipeline/tripo/lunge_clip.py <in-place rigged.glb> <travelling rigged.glb> --clip "<first words>" --out <rigged.glb>
        [--cap 0.6]

Why: Tripo's "Animation in Place" switch strips the hips' travel from every clip, and the route needs it on (lib/glb_root.py). A lunging
attack then loses its step: on the D-94 zombie (2026-11-21) two lunging grabs measured, in place, 0.20 and 0.22 of the height of hand travel
and 169 to 230 px on the game camera, both under the attack limits, while the same clips exported with the switch off stepped 1.21 and
1.17 hip heights forward. The step is what reads as a lunge from the map camera.

What it does: the travelling clip's hips translation, less its first frame, is the step. Its sideways and forward part (across the hips'
rest direction, as `glb_root.root_travel` measures) is scaled down, where needed, so its largest distance from the start is `--cap` hip
heights, and added to the in-place clip's hips translation in every frame. The up-and-down part stays the in-place clip's. The two exports
must hold the clip with the same number of keys (Tripo writes both from one animation). The route's attack settle
(`tripo/prepare_tripo_unit.settle_to_first`) then blends the hips back to the first frame's place with every bone, so the looped attack
starts and ends where the unit stands. Every other clip and every other byte of the in-place file is kept.

The job names the role in `tripo.lunge` (`{"attack": <cap>}`), so the intake allows that role's travel up to the cap
(`tripo_intake.refuse_travelling_clips`). Every other role must still be in place.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import glb_root

DEFAULT_CAP = 0.6


def _hips_translation(doc: dict, clip: str) -> Tuple[int, int, np.ndarray]:
    """(the hips node, the accessor of the named clip's hips translation keys, the hips' rest translation)."""

    names = [node.get("name", "") for node in doc.get("nodes", [])]
    hips = next((i for i, name in enumerate(names) if name.split(":")[-1] == "Hips"), None)
    if hips is None:
        raise ValueError("the rig has no Hips joint")
    for animation in doc.get("animations", []):
        if not animation.get("name", "").startswith(clip):
            continue
        for channel in animation.get("channels", []):
            target = channel.get("target", {})
            if target.get("node") == hips and target.get("path") == "translation":
                accessor = animation["samplers"][channel["sampler"]]["output"]
                return hips, accessor, np.asarray(doc["nodes"][hips].get("translation", [0.0, 0.0, 0.0]), float)
        raise ValueError(f"the clip {clip!r} does not key the hips' translation")
    raise ValueError(f"no clip starts with {clip!r}")


def lunge_step(in_place: np.ndarray, travelling: np.ndarray, rest: np.ndarray, cap: float) -> Tuple[np.ndarray, Dict[str, float]]:
    """The in-place keys with the travelling clip's sideways and forward step added, scaled so it reaches at most `cap` hip heights."""

    if in_place.shape != travelling.shape:
        raise ValueError(f"the two exports key the clip differently ({len(in_place)} and {len(travelling)} keys)")
    scale = float(np.linalg.norm(rest))
    axis = rest / max(scale, 1e-9)
    step = travelling - travelling[0]
    across = step - np.outer(step @ axis, axis)
    reach = float(np.linalg.norm(across, axis=1).max()) / max(scale, 1e-9)
    factor = min(1.0, cap / reach) if reach > 1e-9 else 0.0
    keys = in_place + across * factor
    return keys.astype(np.float32), {"step_hip_heights": round(reach, 3), "kept_hip_heights": round(reach * factor, 3), "factor": round(factor, 3)}


def write_lunge(in_place_path: Path, travelling_path: Path, clip: str, out: Path, cap: float = DEFAULT_CAP) -> Dict[str, float]:
    doc, blob = glb_root._read(in_place_path)
    other_doc, other_blob = glb_root._read(travelling_path)
    _hips, accessor, rest = _hips_translation(doc, clip)
    _other_hips, other_accessor, _other_rest = _hips_translation(other_doc, clip)
    keys, record = lunge_step(glb_root._accessor(doc, blob, accessor), glb_root._accessor(other_doc, other_blob, other_accessor), rest, cap)
    view = doc["bufferViews"][doc["accessors"][accessor]["bufferView"]]
    if view.get("byteStride", 12) != 12:
        raise ValueError("the hips' translation keys are interleaved, which this tool does not write")
    data = bytearray(Path(in_place_path).read_bytes())
    json_length = struct.unpack("<I", data[12:16])[0]
    start = 20 + json_length + 8 + view.get("byteOffset", 0) + doc["accessors"][accessor].get("byteOffset", 0)
    _refuse_bounds(doc, accessor)
    raw = keys.tobytes()
    data[start:start + len(raw)] = raw
    Path(out).write_bytes(bytes(data))
    return dict(record, clip=clip, cap=cap)


def _refuse_bounds(doc: dict, accessor: int) -> None:
    """Tripo writes no min and max for animation outputs. If they are present the file is refused rather than left with wrong bounds."""

    if "min" in doc["accessors"][accessor] or "max" in doc["accessors"][accessor]:
        raise ValueError("the hips' translation accessor carries min and max bounds, which this tool does not rewrite")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("in_place", type=Path, help="the rigged GLB exported with Animation in Place on (the route's input)")
    parser.add_argument("travelling", type=Path, help="the same rig exported with Animation in Place off")
    parser.add_argument("--clip", required=True, help="the first words of the lunge clip's name")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cap", type=float, default=DEFAULT_CAP, help="the largest step kept, in hip heights")
    args = parser.parse_args(argv)
    record = write_lunge(args.in_place, args.travelling, args.clip, args.out, args.cap)
    print(json.dumps(record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
