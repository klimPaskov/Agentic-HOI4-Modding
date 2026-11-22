"""Named locators for particle effects, placed by rule on the unit's own skin (the job's `tripo.locators`).

A locator is a point that follows one bone, where an entity state can fire a particle (vanilla's GER rifle infantry fires `blood_particle` at
its `head` locator, parented to the bone `head`, its position in that bone's own frame). The ZIN devil breathes and throws fire (card 46):
`fire_mouth` at its jaw and `fire_hand_l` and `fire_hand_r` at its claws. The names are the kit's convention for fire effects.

Each entry of `tripo.locators` is `{"name": ..., "bone": ..., "at": ...}`, `at` one of:

- `mouth`: the front of the jaw, the bone's skin point farthest forward in the band from `MOUTH_LOW` to `MOUTH_HIGH` of that skin's height,
  at the middle of the band's width.
- `tip`: the bone's skin point farthest from its joint (a claw's tip), the mean of its farthest `TIP_PERCENT` percent.
- `joint`: the joint itself.

Without `tripo.locators` a unit gets none. Positions are measured on the exported `.mesh` (y up, the front from the heels to the toes) and
written in the bone's own bind frame, with no rotation of their own.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Sequence

import numpy as np

from . import pdx_deform, pdx_motion
from .pdx_binary import PdxNode, read
from .pdx_write import write

PLACES = ("mouth", "tip", "joint")
MOUTH_LOW, MOUTH_HIGH = 0.15, 0.45
TIP_PERCENT = 2.0
# The fire effects' names (ZIN card 46, agreed with the effects work): one at the mouth, one at each hand's claws.
FIRE = [{"name": "fire_mouth", "bone": "Head", "at": "mouth"},
        {"name": "fire_hand_l", "bone": "LeftHand", "at": "tip"},
        {"name": "fire_hand_r", "bone": "RightHand", "at": "tip"}]


def front_of(mesh: pdx_deform.SkinnedMesh) -> np.ndarray:
    """The direction the unit faces, level: from the heels to the toes in the rest pose (+z when the feet have no toes)."""

    rest = pdx_motion.rest_joints(mesh)
    names = {name: i for i, name in enumerate(mesh.bones)}
    vectors = [rest[names[f"{s}ToeBase"]] - rest[names[f"{s}Foot"]] for s in ("Left", "Right") if f"{s}ToeBase" in names and f"{s}Foot" in names]
    front = np.mean(vectors, axis=0) if vectors else np.array([0.0, 0.0, 1.0])
    front[1] = 0.0
    return front / max(float(np.linalg.norm(front)), 1e-12)


def place(mesh: pdx_deform.SkinnedMesh, bone: str, at: str) -> np.ndarray:
    """The locator's point in the rest pose, by `at`."""

    if at not in PLACES:
        raise ValueError(f"locator place {at!r}: use one of {', '.join(PLACES)}")
    index = mesh.bones.index(bone)
    joint = pdx_motion.rest_joints(mesh)[index]
    if at == "joint":
        return joint
    skin = mesh.positions[pdx_deform.dominant_bones(mesh) == index]
    if len(skin) < 3:
        raise ValueError(f"the bone {bone} carries no skin to place a locator on")
    if at == "tip":
        distance = np.linalg.norm(skin - joint, axis=1)
        return skin[distance >= np.percentile(distance, 100.0 - TIP_PERCENT)].mean(axis=0)
    low, high = np.percentile(skin[:, 1], [0, 100])
    band = skin[(skin[:, 1] >= low + MOUTH_LOW * (high - low)) & (skin[:, 1] <= low + MOUTH_HIGH * (high - low))]
    if len(band) < 3:
        band = skin
    front = front_of(mesh)
    lateral = np.cross([0.0, 1.0, 0.0], front)
    middle = np.abs((band - joint) @ lateral) <= np.percentile(np.abs((band - joint) @ lateral), 30)
    pick = band[middle] if middle.any() else band
    return pick[np.argmax(pick @ front)].copy()


def add_locators(mesh_path: Path, entries: Sequence[Dict[str, str]]) -> List[dict]:
    """Add the locators to the `.mesh`, in place. Returns each one's name, bone and point. A name already in the mesh is replaced."""

    mesh = pdx_deform.load_mesh(mesh_path)
    bind = np.linalg.inv(mesh.inverse_bind)
    root = read(mesh_path)
    locators = root.child("locator")
    if locators is None:
        locators = PdxNode("locator", 1)
        root.children.append(locators)
    out = []
    for entry in entries:
        name, bone, at = entry["name"], entry["bone"], entry.get("at", "joint")
        if bone not in mesh.bones:
            raise ValueError(f"locator {name}: the mesh has no bone {bone}")
        point = place(mesh, bone, at)
        local = np.linalg.inv(bind[mesh.bones.index(bone)]) @ np.append(point, 1.0)
        locators.children = [child for child in locators.children if child.name != name]
        locators.children.append(PdxNode(name, 2, {"p": [float(v) for v in local[:3]], "q": [0.0, 0.0, 0.0, 1.0], "pa": [bone]}))
        out.append({"name": name, "bone": bone, "at": at, "point": [round(float(v), 4) for v in point]})
    write(mesh_path, root)
    return out
