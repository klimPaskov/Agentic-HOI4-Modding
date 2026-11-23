"""Right after the export, before any Blender run: did Tripo's humanoid auto-rig put the arms into the arms?

    py -3.13 -B .tools/3d_pipeline/tripo/rig_check.py <rigged.glb> [--json out.json]

Large wings can make Tripo's auto-rig place the arm chain wrong. On the ZIN devil (2026-11-22, after Tripo's "Not Ready for Auto-Rigging"
dialog) the shoulder, upper arm, forearm and wrist joints sat close together high on the chest, and the hand joint with its finger joints
carried both whole wings and the real arms: no vertex at all was bound to a forearm. The route then reads the wing as an arm and finds no
wing, and every clip moves the wings with the hands. No later step repairs such a rig, so check it before paying for clips or running Blender.

TRIPO-RIG-ARMS fails a side when either holds:
- no skin is bound mostly to the forearm (a forearm that moves nothing), or
- the skin bound mostly to the upper arm, forearm, hand or fingers lies, in its 95th percentile, farther from those bones than
  `MAX_ARM_SKIN_REACH` arm lengths (the arm holds a wing), or
- the skin bound mostly to the hand or its fingers reaches, in its 95th percentile, farther from the wrist joint than `MAX_HAND_REACH`
  times the arm's own length (upper arm plus forearm): the hand carries more than a hand.

Joint positions come from the skin's inverse bind matrices, so no node hierarchy is read. The model faces +z with y up. Reading files only:
no Blender, no cost. What to do on a fail: for a winged unit run tripo/arm_seat.py (free), then check again. A paid Retry on Tripo's Rig page made the devil's rig worse.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import glb_root

# Measured on passed rigs (2026-11-22): the hand skin reaches 0.37 to 0.57 arm lengths (zombie, dwarf, demon, the stone golem). The devil
# whose rig missed its arms reached 2.1 and 5.3, with no skin on the right forearm.
MAX_HAND_REACH = 1.0
# The skin bound to the whole arm (upper arm, forearm, hand and fingers), its 95th percentile distance from the arm's bones, in arm lengths.
# Passed rigs read 0.33 to 0.62, the demon's right side 1.6 (part of its wing on that arm, passed by two reviews). Tripo's rigs of the devil
# read 7.6 to 10.9: the upload's rig carried each whole wing on the upper arm or the forearm, with no skin on the hands (2026-11-22).
MAX_ARM_SKIN_REACH = 2.5
_TYPES = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
_DTYPES = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}


def accessor(doc: dict, blob: bytes, index: int) -> np.ndarray:
    """Any accessor of a GLB, strided or packed, as an array (count, components)."""

    item = doc["accessors"][index]
    view = doc["bufferViews"][item["bufferView"]]
    dtype = np.dtype(_DTYPES[item["componentType"]])
    width = _TYPES[item["type"]]
    start = view.get("byteOffset", 0) + item.get("byteOffset", 0)
    stride = view.get("byteStride") or width * dtype.itemsize
    raw = np.frombuffer(blob, np.uint8, count=stride * (item["count"] - 1) + width * dtype.itemsize, offset=start)
    rows = np.lib.stride_tricks.as_strided(raw, shape=(item["count"], width * dtype.itemsize), strides=(stride, 1))
    return np.ascontiguousarray(rows).view(dtype).reshape(item["count"], width)


def short(name: str) -> str:
    return str(name).split(":")[-1]


def skin_layout(path: Path) -> Dict[str, object]:
    """Vertex positions, each vertex's dominant joint name and each joint's rest position, from the first skinned mesh."""

    doc, blob = glb_root._read(path)
    skin = doc["skins"][0]
    names = [short(doc["nodes"][i].get("name", "")) for i in skin["joints"]]
    inverse = accessor(doc, blob, skin["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1)
    heads = {name: np.linalg.inv(matrix)[:3, 3] for name, matrix in zip(names, inverse)}
    node = next(n for n in doc["nodes"] if "skin" in n and "mesh" in n)
    positions, dominant = [], []
    for primitive in doc["meshes"][node["mesh"]]["primitives"]:
        attributes = primitive["attributes"]
        if "JOINTS_0" not in attributes:
            continue
        positions.append(accessor(doc, blob, attributes["POSITION"]).astype(float))
        joints = accessor(doc, blob, attributes["JOINTS_0"]).astype(int)
        weights = accessor(doc, blob, attributes["WEIGHTS_0"]).astype(float)
        dominant.append(np.array([names[j] for j in joints[np.arange(len(joints)), weights.argmax(axis=1)]]))
    return {"positions": np.concatenate(positions), "dominant": np.concatenate(dominant), "heads": heads}


def side_numbers(layout: Dict[str, object], side: str) -> Dict[str, float]:
    heads, dominant, positions = layout["heads"], layout["dominant"], layout["positions"]
    arm, forearm, hand = heads[f"{side}Arm"], heads[f"{side}ForeArm"], heads[f"{side}Hand"]
    length = float(np.linalg.norm(forearm - arm) + np.linalg.norm(hand - forearm))
    hand_skin = np.array([str(name).startswith(f"{side}Hand") for name in dominant])
    reach = float(np.percentile(np.linalg.norm(positions[hand_skin] - hand, axis=1), 95)) if hand_skin.any() else 0.0
    family = np.array([str(name) in (f"{side}Arm", f"{side}ForeArm") or str(name).startswith(f"{side}Hand") for name in dominant])
    far = 0.0
    if family.any():
        points = positions[family]
        near = np.minimum(segment_distance(points, arm, forearm), segment_distance(points, forearm, hand))
        near = np.minimum(near, np.linalg.norm(points - hand, axis=1))
        far = float(np.percentile(near, 95))
    return {"arm_length": round(length, 4), "forearm_vertices": int((dominant == f"{side}ForeArm").sum()),
            "hand_vertices": int(hand_skin.sum()), "hand_reach": round(reach / max(length, 1e-9), 2),
            "arm_skin_reach": round(far / max(length, 1e-9), 2)}


def segment_distance(points: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    ab = b - a
    t = np.clip((points - a) @ ab / max(float(ab @ ab), 1e-12), 0.0, 1.0)
    return np.linalg.norm(points - (a + t[:, None] * ab), axis=1)


def rig_findings(layout: Dict[str, object]) -> (List[dict], dict):
    found, numbers = [], {}
    for side in ("Left", "Right"):
        missing = [f"{side}{part}" for part in ("Arm", "ForeArm", "Hand") if f"{side}{part}" not in layout["heads"]]
        if missing:
            # the paid retry of the devil's rig dropped RightHand and bound 91% of the skin to the head
            numbers[side] = {"missing_joints": missing}
            found.append({"rule": "TRIPO-RIG-ARMS", "subject": side, "message": f"the rig has no {', '.join(missing)} joint: Tripo's rig missed the arm"})
            continue
        row = side_numbers(layout, side)
        numbers[side] = row
        if row["forearm_vertices"] == 0:
            found.append({"rule": "TRIPO-RIG-ARMS", "subject": side, "message": f"no skin is bound mostly to the {side.lower()} forearm: Tripo's rig "
                          "missed the arm. For a winged unit repair it free with tripo/arm_seat.py"})
        if row["arm_skin_reach"] > MAX_ARM_SKIN_REACH:
            found.append({"rule": "TRIPO-RIG-ARMS", "subject": side, "message": f"the {side.lower()} arm's bones carry skin {row['arm_skin_reach']:.1f} arm lengths "
                          f"from them (limit {MAX_ARM_SKIN_REACH:g}): the arm holds a wing. For a winged unit repair it free with tripo/arm_seat.py"})
        if row["hand_reach"] > MAX_HAND_REACH:
            found.append({"rule": "TRIPO-RIG-ARMS", "subject": side, "message": f"the {side.lower()} hand carries skin {row['hand_reach']:.1f} arm lengths from "
                          f"the wrist (limit {MAX_HAND_REACH:g}): the hand holds more than a hand, such as a wing. For a winged unit repair it free with tripo/arm_seat.py"})
    return found, numbers


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("glb", type=Path, help="the rigged export")
    parser.add_argument("--json", type=Path, help="write the numbers and findings here")
    args = parser.parse_args(argv)
    found, numbers = rig_findings(skin_layout(args.glb))
    for side, row in numbers.items():
        if "missing_joints" in row:
            print(f"{side}: no joint {', '.join(row['missing_joints'])}")
            continue
        print(f"{side}: arm {row['arm_length']:.3f}, forearm skin {row['forearm_vertices']}, hand skin {row['hand_vertices']} reaching {row['hand_reach']:.2f} arm lengths")
    for item in found:
        print(f"{item['rule']} [{item['subject']}] {item['message']}")
    print("rig: fail" if found else "rig: pass")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps({"numbers": numbers, "findings": found}, indent=2) + "\n", encoding="utf-8")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
