"""How far each clip of a rigged GLB moves its hips sideways, read straight from the file (no Blender).

The Tripo route expects clips exported in place: Tripo's export dialog has an "Animation in Place" switch, and with it off a walk or a
flee carries its travel in the hips. The kit's loop, grounding and weapon-drop rules then work on a body that walks off: on the round 4
orc an export without the switch failed the move's loop (TRIPO-LOOP-POP, 17 degrees at the hand), dropped the axe into the body after
the fall (TRIPO-WEAPON-IN-BODY in 66 frames) and sank the guard's axe below the feet, while the same clips exported in place passed.

`root_travel` gives, per clip, the range of the hips' translation across the rest pose's hips direction (its sideways and forward
motion), as a share of the hips' rest distance from their parent (about the hip height). `travelling_clips` names the clips over
`MAX_ROOT_TRAVEL_SHARE`. A bob or a lean stays well under the limit: the in-place orc's eleven clips measure 0.001 to 0.048 (its
death), and the same clips exported with the switch off 0.10 (a hit reaction) to 6.8 (a flee).
"""

from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import numpy as np

MAX_ROOT_TRAVEL_SHARE = 0.1
_COMPONENTS = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}


def _read(path: Path) -> tuple:
    data = Path(path).read_bytes()
    if data[:4] != b"glTF":
        raise ValueError(f"{path} is not a binary glTF file")
    length = struct.unpack("<I", data[12:16])[0]
    doc = json.loads(data[20:20 + length])
    offset = 20 + length
    blob = b""
    if offset + 8 <= len(data):
        size = struct.unpack("<I", data[offset:offset + 4])[0]
        blob = data[offset + 8:offset + 8 + size]
    return doc, blob


def _accessor(doc: dict, blob: bytes, index: int) -> np.ndarray:
    accessor = doc["accessors"][index]
    view = doc["bufferViews"][accessor["bufferView"]]
    components = _COMPONENTS[accessor["type"]]
    start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    values = np.frombuffer(blob, dtype=np.float32, count=accessor["count"] * components, offset=start)
    return values.reshape(accessor["count"], components) if components > 1 else values


def root_travel(path: Path) -> Dict[str, float]:
    """{clip name: sideways and forward range of the hips' translation, as a share of their rest offset}. Clips that do not move the
    hips' translation measure 0."""

    doc, blob = _read(path)
    names = [node.get("name", "") for node in doc.get("nodes", [])]
    hips = next((i for i, name in enumerate(names) if name.split(":")[-1] == "Hips"), None)
    if hips is None:
        return {}
    rest = np.asarray(doc["nodes"][hips].get("translation", [0.0, 0.0, 0.0]), float)
    scale = float(np.linalg.norm(rest))
    if scale < 1e-9:
        return {}
    axis = rest / scale
    out: Dict[str, float] = {}
    for animation in doc.get("animations", []):
        travel = 0.0
        for channel in animation.get("channels", []):
            target = channel.get("target", {})
            if target.get("node") != hips or target.get("path") != "translation":
                continue
            values = _accessor(doc, blob, animation["samplers"][channel["sampler"]]["output"]) - rest
            across = values - np.outer(values @ axis, axis)
            travel = max(travel, float(np.ptp(across, axis=0).max()) / scale if len(across) else 0.0)
        out[animation.get("name", "")] = round(travel, 3)
    return out


def travelling_clips(path: Path, wanted: Optional[Iterable[str]] = None, limit: float = MAX_ROOT_TRAVEL_SHARE) -> Dict[str, float]:
    """The clips over `limit`; with `wanted`, only those whose name starts with one of the wanted names (the job's role clips)."""

    wanted_list: List[str] = [w for w in (wanted or []) if w]
    out = {}
    for clip, travel in root_travel(path).items():
        if wanted_list and not any(clip.startswith(w) or w.startswith(clip.strip()) for w in wanted_list):
            continue
        if travel > limit:
            out[clip] = travel
    return out
