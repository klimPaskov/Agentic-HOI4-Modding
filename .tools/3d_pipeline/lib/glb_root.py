"""How far each clip of a rigged GLB moves its hips sideways, read straight from the file (no Blender).

The Tripo route expects clips exported in place: Tripo's export dialog has an "Animation in Place" switch, and with it off a walk or a
flee carries its travel in the hips. The kit's loop, grounding and weapon-drop rules then work on a body that walks off: on the round 4
orc an export without the switch failed the move's loop (TRIPO-LOOP-POP, 17 degrees at the hand), dropped the axe into the body after
the fall (TRIPO-WEAPON-IN-BODY in 66 frames) and sank the guard's axe below the feet, while the same clips exported in place passed.

`root_travel` gives, per clip, the range of the hips' translation across the rest pose's hips direction (its sideways and forward
motion), as a share of the hips' rest distance from their parent (about the hip height). `travelling_clips` names the clips over
`MAX_ROOT_TRAVEL_SHARE`. A bob or a lean stays well under the limit: the in-place orc's eleven clips measure 0.001 to 0.048 (its
death), and the same clips exported with the switch off 0.10 (a hit reaction) to 6.8 (a flee). A death is judged against vanilla's deaths
instead (`DEATH_TRAVEL_LIMIT`). The hips are found through lib/tripo_rig.py, composed with the joints above them (the newer Tripo rig keeps
its root motion in `BoneRoot`, above `Hip`), and a rig with no hip bone is refused loudly.
"""

from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

import numpy as np

MAX_ROOT_TRAVEL_SHARE = 0.1
# A death falls, and a falling body moves its hips: vanilla's GER infantry deaths (death_mg, death_rifle, 2026-11-18) move the pelvis 1.31
# hip heights across the ground. A death is judged against that worst with a quarter added. Under the loop limit above, three of the
# demon's in-place deaths (defeat_03 0.129, two text-to-motion falls 0.13 and 0.132) were refused as exported without the switch.
VANILLA_DEATH_TRAVEL = 1.31
DEATH_TRAVEL_LIMIT = round(1.25 * VANILLA_DEATH_TRAVEL, 2)
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


def _hips_chain(doc: dict, path: Path) -> List[int]:
    """The hips node and the joints above it, top first. The hips are named through lib/tripo_rig.py (Mixamo's `Hips`, the newer Tripo rig's
    `Hip`, whose root motion is carried by `BoneRoot` above it). A rig without a hip bone is refused loudly (`tripo_rig.RigError`): reading
    no hips once let every clip pass as in place."""

    from . import tripo_rig

    nodes = doc.get("nodes", [])
    names = [node.get("name", "") for node in nodes]
    try:
        hips_name = tripo_rig.RigNames(names).actual("Hips")
    except tripo_rig.RigError as problem:
        raise tripo_rig.RigError(f"{Path(path).name}: no hip bone to measure the clips' travel on ({problem})") from None
    hips = names.index(hips_name)
    joints = {j for skin in doc.get("skins", []) for j in skin.get("joints", [])}
    parent = {child: i for i, node in enumerate(nodes) for child in node.get("children", [])}
    chain = [hips]
    while chain[0] in parent and parent[chain[0]] in joints:
        chain.insert(0, parent[chain[0]])
    return chain


def _trs(node: dict, translation=None, rotation=None, scale=None) -> np.ndarray:
    t = np.asarray(node.get("translation", [0.0, 0.0, 0.0]) if translation is None else translation, float)
    x, y, z, w = np.asarray(node.get("rotation", [0.0, 0.0, 0.0, 1.0]) if rotation is None else rotation, float) / max(
        float(np.linalg.norm(node.get("rotation", [0.0, 0.0, 0.0, 1.0]) if rotation is None else rotation)), 1e-12)
    s = np.asarray(node.get("scale", [1.0, 1.0, 1.0]) if scale is None else scale, float)
    r = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                  [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    m = np.eye(4)
    m[:3, :3], m[:3, 3] = r * s, t
    return m


def _sampled(times: np.ndarray, keys: np.ndarray, values: np.ndarray) -> np.ndarray:
    """`values` keyed at `keys`, read at `times` (linear, held past the ends)."""

    return np.stack([np.interp(times, keys, values[:, k]) for k in range(values.shape[1])], axis=1)


def _chain_positions(doc: dict, blob: bytes, animation: dict, chain: Sequence[int]) -> Optional[np.ndarray]:
    """The hips' position in the top joint's parent space at every key time of the chain's channels in `animation` (None: nothing moves)."""

    tracks: Dict[tuple, tuple] = {}
    for channel in animation.get("channels", []):
        target = channel.get("target", {})
        if target.get("node") in chain and target.get("path") in ("translation", "rotation", "scale"):
            sampler = animation["samplers"][channel["sampler"]]
            tracks[(target["node"], target["path"])] = (np.asarray(_accessor(doc, blob, sampler["input"]), float),
                                                        np.asarray(_accessor(doc, blob, sampler["output"]), float))
    if not tracks:
        return None
    times = np.unique(np.concatenate([keys for keys, _values in tracks.values()]))
    out = np.zeros((len(times), 3))
    for f, time in enumerate(times):
        m = np.eye(4)
        for node in chain:
            parts = {path: _sampled(np.array([time]), *tracks[(node, path)])[0] for path in ("translation", "rotation", "scale") if (node, path) in tracks}
            m = m @ _trs(doc["nodes"][node], parts.get("translation"), parts.get("rotation"), parts.get("scale"))
        out[f] = m[:3, 3]
    return out


def root_travel(path: Path) -> Dict[str, float]:
    """{clip name: sideways and forward range of the hips' translation, as a share of their rest offset}. Clips that do not move the
    hips' translation measure 0. The hips are composed with the joints above them (`_hips_chain`), and a rig without a hip bone raises
    `tripo_rig.RigError`."""

    doc, blob = _read(path)
    chain = _hips_chain(doc, path)
    hips = chain[-1]
    if len(chain) == 1:
        rest = np.asarray(doc["nodes"][hips].get("translation", [0.0, 0.0, 0.0]), float)
    else:
        m = np.eye(4)
        for node in chain:
            m = m @ _trs(doc["nodes"][node])
        rest = m[:3, 3]
    scale = float(np.linalg.norm(rest))
    if scale < 1e-9:
        return {}
    axis = rest / scale
    out: Dict[str, float] = {}
    for animation in doc.get("animations", []):
        travel = 0.0
        if len(chain) == 1:
            for channel in animation.get("channels", []):
                target = channel.get("target", {})
                if target.get("node") != hips or target.get("path") != "translation":
                    continue
                values = _accessor(doc, blob, animation["samplers"][channel["sampler"]]["output"]) - rest
                across = values - np.outer(values @ axis, axis)
                travel = max(travel, float(np.ptp(across, axis=0).max()) / scale if len(across) else 0.0)
        else:
            positions = _chain_positions(doc, blob, animation, chain)
            if positions is not None and len(positions):
                values = positions - rest
                across = values - np.outer(values @ axis, axis)
                travel = float(np.ptp(across, axis=0).max()) / scale
        out[animation.get("name", "")] = round(travel, 3)
    return out


def _named(clip: str, names: Sequence[str]) -> bool:
    return any(clip.startswith(w) or w.startswith(clip.strip()) for w in names)


def travelling_clips(path: Path, wanted: Optional[Iterable[str]] = None, limit: float = MAX_ROOT_TRAVEL_SHARE,
                     deaths: Optional[Iterable[str]] = None) -> Dict[str, float]:
    """The clips over `limit`; with `wanted`, only those whose name starts with one of the wanted names (the job's role clips). A clip
    named in `deaths` is judged against `DEATH_TRAVEL_LIMIT` instead: a body that falls moves its hips."""

    wanted_list: List[str] = [w for w in (wanted or []) if w]
    death_list: List[str] = [w for w in (deaths or []) if w]
    out = {}
    for clip, travel in root_travel(path).items():
        if wanted_list and not _named(clip, wanted_list) and not (death_list and _named(clip, death_list)):
            continue
        if travel > (DEATH_TRAVEL_LIMIT if death_list and _named(clip, death_list) else limit):
            out[clip] = travel
    return out
