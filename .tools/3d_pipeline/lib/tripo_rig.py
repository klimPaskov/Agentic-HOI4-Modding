"""The two humanoid rigs Tripo exports, and the one set of names the Tripo route works in. No Blender.

Tripo rigged humanoids with a Mixamo skeleton (`mixamorig:Hips`, `mixamorig:LeftUpLeg`, ...) until November 2026, and now rigs new
assets with its own (`BoneRoot`, `Hip`, `Pelvis`, `Waist`, `L_Thigh`, `L_Upperarm`, `L_Index1`, twist and share bones, a facial bone).
Every tool that reads a rigged GLB or the rig in Blender names bones through this module, so both rigs reach the same kit skeleton.

Canonical names. The route's tools speak Mixamo's short names (`Hips`, `Spine2`, `LeftHand`, `LeftHandIndex1`), the canonical names. A
rig is read by `RigNames`: `canonical(actual)` gives a bone's canonical name, `actual(canonical)` the name it has in this rig (None
when the rig has no such bone), `kit(actual)` the kit bone it becomes (`KIT_FROM_CANONICAL`: `Spine1` is the kit's `Spine01`).

The newer rig (`TRIPO_FROM_CANONICAL`), from the demon's export of 2026-11-18 (tripo-demon/clips2, 79 joints):
- `Hip` is the hips (both `Pelvis`, which carries the thighs, and `Waist`, which carries the spine, hang from it), `Waist` the kit's
  `Spine`, `Spine01` and `Spine02` themselves, `NeckTwist01` the neck (`NeckTwist02` lies between it and `Head`), `L_Clavicle`,
  `L_Upperarm`, `L_Forearm`, `L_Hand` the arm, `L_Thigh`, `L_Calf`, `L_Foot`, `L_ToeBase` the leg, and `L_Thumb1` to `L_Pinky3` the
  fingers (`Mid` is Mixamo's `Middle`, and there is no fourth joint).
- `BoneRoot` lies above `Hip` and carries the clips' root motion (its translation moves, `Hip`'s rest offset is about zero).
- The rest (twist bones, knee and elbow share bones, eyes, the facial bone, `neutral_bone`) are leaves or off the body chain.

Bones the kit does not keep (`dropped_roles`): an in-between bone, a dropped bone with kept bones below it (`Pelvis`, `NeckTwist02`,
`BoneRoot`), has its motion composed onto its children before it goes (`compose_basis`), so no kept bone moves differently. Any other
dropped bone is a leaf: its skin weights merge into its nearest kept ancestor, or into the kept root when it has none (`neutral_bone`).
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional, Sequence

import numpy as np

MIXAMO_PREFIX = re.compile(r"^mixamorig\d*:")
FINGERS = ("Thumb", "Index", "Middle", "Ring", "Pinky")

# Canonical (Mixamo short) names to the kit's bones.
KIT_FROM_CANONICAL: Dict[str, str] = {"Hips": "Hips", "Spine": "Spine", "Spine1": "Spine01", "Spine2": "Spine02", "Neck": "neck", "Head": "Head"}
for _side in ("Left", "Right"):
    for _part in ("Shoulder", "Arm", "ForeArm", "Hand", "UpLeg", "Leg", "Foot", "ToeBase"):
        KIT_FROM_CANONICAL[f"{_side}{_part}"] = f"{_side}{_part}"

# Canonical names to the newer Tripo rig's.
TRIPO_FROM_CANONICAL: Dict[str, str] = {"Hips": "Hip", "Spine": "Waist", "Spine1": "Spine01", "Spine2": "Spine02", "Neck": "NeckTwist01", "Head": "Head"}
for _side, _short in (("Left", "L"), ("Right", "R")):
    for _part, _theirs in (("Shoulder", "Clavicle"), ("Arm", "Upperarm"), ("ForeArm", "Forearm"), ("Hand", "Hand"), ("UpLeg", "Thigh"),
                           ("Leg", "Calf"), ("Foot", "Foot"), ("ToeBase", "ToeBase")):
        TRIPO_FROM_CANONICAL[f"{_side}{_part}"] = f"{_short}_{_theirs}"
    for _finger in FINGERS:
        for _joint in (1, 2, 3):
            TRIPO_FROM_CANONICAL[f"{_side}Hand{_finger}{_joint}"] = f"{_short}_{'Mid' if _finger == 'Middle' else _finger}{_joint}"
CANONICAL_FROM_TRIPO = {theirs: canonical for canonical, theirs in TRIPO_FROM_CANONICAL.items()}

# What tells the two rigs apart: bones only that rig has.
MIXAMO_MARKS = ("Hips",)
TRIPO_MARKS = ("Hip", "L_Thigh", "R_Thigh")


class RigError(RuntimeError):
    """The rig is neither of Tripo's humanoid rigs (no hip bone, or not both legs)."""


def short(name: str) -> str:
    """A name without Mixamo's `mixamorig:` prefix (or any `prefix:`)."""

    return MIXAMO_PREFIX.sub("", str(name)).split(":")[-1]


def rig_style(names: Iterable[str]) -> str:
    """"mixamo" or "tripo", by which rig's marks the names hold; RigError when neither's are all there."""

    shorts = {short(name) for name in names}
    if all(mark in shorts for mark in MIXAMO_MARKS):
        return "mixamo"
    if all(mark in shorts for mark in TRIPO_MARKS):
        return "tripo"
    raise RigError(f"neither of Tripo's humanoid rigs: no {' / '.join(MIXAMO_MARKS)} (Mixamo) and no {' / '.join(TRIPO_MARKS)} (Tripo's own) among "
                   f"{len(shorts)} bones")


class RigNames:
    """One rig's names: canonical (Mixamo short) names to the rig's own and back, and each to the kit's bone."""

    def __init__(self, names: Sequence[str]):
        self.names = [str(name) for name in names]
        self.style = rig_style(self.names)
        self._actual: Dict[str, str] = {}
        self._canonical: Dict[str, str] = {}
        for name in self.names:
            own = short(name)
            canonical = CANONICAL_FROM_TRIPO.get(own, own) if self.style == "tripo" else own
            self._canonical[name] = canonical
            self._actual.setdefault(canonical, name)

    def canonical(self, actual: str) -> str:
        return self._canonical.get(str(actual), short(actual))

    def actual(self, canonical: str) -> Optional[str]:
        return self._actual.get(canonical)

    def kit(self, actual: str) -> Optional[str]:
        return KIT_FROM_CANONICAL.get(self.canonical(actual))

    def kit_map(self) -> Dict[str, str]:
        """{the rig's bone: the kit bone it becomes} for every bone the kit keeps."""

        return {name: kit for name in self.names if (kit := self.kit(name)) is not None}


def kit_bone_names() -> set:
    return set(KIT_FROM_CANONICAL.values())


def dropped_roles(parents: Dict[str, Optional[str]], kept: Iterable[str]) -> Dict[str, str]:
    """{dropped bone: "in-between" or "leaf"} for every bone of the rig (`parents`: bone to parent, None at a root) the kit does not keep.
    An in-between bone has a kept bone below it, so its motion is composed onto its children before it is removed."""

    kept = set(kept)
    children: Dict[str, List[str]] = {}
    for bone, parent in parents.items():
        if parent is not None:
            children.setdefault(parent, []).append(bone)

    def holds_kept(bone: str) -> bool:
        return any(child in kept or holds_kept(child) for child in children.get(bone, []))

    return {bone: ("in-between" if holds_kept(bone) else "leaf") for bone in parents if bone not in kept}


def composition_order(parents: Dict[str, Optional[str]], dropped: Iterable[str]) -> List[str]:
    """The in-between bones to compose, parents first, so a bone composed onto a child that is itself dropped is composed further down."""

    dropped = set(dropped)

    def depth(bone: str) -> int:
        level = 0
        while parents.get(bone) is not None:
            bone = parents[bone]
            level += 1
        return level

    return sorted(dropped, key=depth)


def compose_basis(rest_parent: np.ndarray, rest_child: np.ndarray, basis_parent: np.ndarray, basis_child: np.ndarray) -> np.ndarray:
    """The child's pose basis once its parent is removed and it hangs from the parent's parent, so it stays where it was in every frame.

    Blender poses a bone as `pose = parent_pose @ (parent_rest^-1 @ rest) @ basis` in armature space (rests are the bones' armature-space
    rest matrices, 4x4). With the parent P removed, the child C keeps its pose when its new basis is
    `C_rest^-1 @ P_rest @ P_basis @ P_rest^-1 @ C_rest @ C_basis`: P's own basis carried into C's rest frame, then C's. `basis_*` may be
    (frames, 4, 4)."""

    carry = np.linalg.inv(rest_child) @ rest_parent
    back = np.linalg.inv(rest_parent) @ rest_child
    return carry @ np.asarray(basis_parent, float) @ back @ np.asarray(basis_child, float)


class BoneNamer:
    """Names for the Blender stages that work on Tripo's rig before the intake (the grip, shield and hand stages): `name(canonical)` is the
    bone's name in this rig, or the rig's prefix plus the canonical name for a bone it does not have yet (the grip stage's `Weapon`);
    `canonical(actual)` the other way, and `in_family(actual, hand)` whether a bone is that hand or one of its fingers. Before a rig is read
    it names Mixamo's bones, as those stages always did."""

    def __init__(self, names: Optional[Sequence[str]] = None):
        self.rig: Optional[RigNames] = RigNames(names) if names is not None else None
        prefixed = [n for n in (names or []) if MIXAMO_PREFIX.match(str(n))]
        self.prefix = MIXAMO_PREFIX.match(prefixed[0]).group(0) if prefixed else ("mixamorig:" if names is None else "")

    def name(self, canonical: str) -> str:
        actual = self.rig.actual(canonical) if self.rig is not None else None
        return actual if actual is not None else self.prefix + canonical

    def canonical(self, actual: str) -> str:
        return self.rig.canonical(actual) if self.rig is not None else short(actual)

    def in_family(self, actual: str, hand: str) -> bool:
        return self.canonical(actual).startswith(hand)
