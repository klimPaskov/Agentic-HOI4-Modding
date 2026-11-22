"""The effects layer of the 3D route: particles at locators, fired by the entity's states at measured frames. No Blender.

HOI4 effects are not part of a model. They are particle systems (`.asset` files), registered in a `.gfx` file (`pdxparticle`), fired by an
`event = { time = <seconds> node = "<locator>" particle = "<name>" }` line in a state of the entity, at a locator of the `.mesh` that is
parented to a bone. `calibrate_effects.py` surveys how vanilla does it for every kind of model (`config/effects_vanilla.json`) and
measured the unit of `time`: seconds of the clip (frame / fps).

A job names its effects in an `effects` block: `{"profiles": [...], "setting": [...], "colour": {...}, "frames": {...}}`. The profiles
and their slots live in `config/effects.json`. For each slot this module

1. places the locator: an existing one (`spot: locator`), or a new one measured on the mesh (a hand's tip, the front of the head, a part's
   top) and written into the `.mesh` with `pdx_write`, its offset in the parent bone's frame as vanilla's are;
2. measures the frame in the role's clip (`recoil`, `strike`, `part_leaves`, `peak`, `start`, or a whole frame from the job);
3. writes the plan beside the files (`<stem>_effects.json`): the locators, the events with their frame and time, the particles (a vanilla
   one by its registered name, or a mod copy changed by colour and scale only) and the sounds, which `wire_unit.py` merges into the
   sound plan at the same frames.

`findings()` checks a plan against the files: EFFECT-FIT, EFFECT-LOCATOR, EFFECT-FRAME, EFFECT-ON-PART and EFFECT-PARTICLE.
"""

from __future__ import annotations

import colorsys
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from . import pdx_deform
from .pdx_binary import PdxNode, read
from .pdx_write import write

CONFIG = Path(__file__).resolve().parents[1] / "config"
EFFECTS = CONFIG / "effects.json"
VANILLA = CONFIG / "effects_vanilla.json"
PLAN_SUFFIX = "_effects.json"
FPS = 30.0  # the kit's clips and vanilla's units
RECOIL_SHARE = 0.10  # `recoil`: the frame the gun's own move first passes this share of its largest move
LEAVE_SHARE = 0.02  # `part_leaves`: the locator moves this share of the model's height from frame 0
ON_PART_SHARE = 0.03  # EFFECT-ON-PART: the locator's distance to its part may change by this share of the height
REGION_TOP_SHARE = 0.05  # a spot's vertices: the farthest 5% of the region along the measured direction
AFTER_CLIP_S = 1.0  # a `duration_s: clip` particle (a wreck's smoke) goes on this long past the clip, as the death's last frame holds
EYE_INSET = 0.25  # `eye`: how far behind the head's front an eye sits, a share of the head's depth (inside a hood)
GREY_SATURATION = 0.25  # a subsystem whose colour is greyer than this (smoke) keeps its colour when a particle is recoloured
# A state with no clip of its own plays this role's clip: vanilla's tanks and the static route's play attack in defend and support_attack
ROLE_CLIPS = {"support_attack": "attack", "defend": "attack", "training": "idle"}
BONE_ALIASES = {
    "righthand": ("righthand", "r_hand", "hand_r", "mixamorig:righthand", "right_hand"),
    "lefthand": ("lefthand", "l_hand", "hand_l", "mixamorig:lefthand", "left_hand"),
    "head": ("head", "mixamorig:head", "head_jnt"),
}
DEFAULT_FRONT = np.array([0.0, 0.0, -1.0])  # the kit's models face -z in the mesh (Blender's -y), as vanilla's do


class EffectsError(ValueError):
    """A job's effects block that cannot be planned; the message says what and why."""


# ---- config -------------------------------------------------------------------------------------------------------------

def load(path: Path = EFFECTS) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_vanilla(path: Path = VANILLA) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8")) if Path(path).is_file() else {}


def check_config(data: Optional[Dict[str, Any]] = None, vanilla: Optional[Dict[str, Any]] = None) -> List[str]:
    """Every way `config/effects.json` disagrees with itself and with the survey of vanilla. Empty when it agrees."""

    data = data or load()
    vanilla = vanilla if vanilla is not None else load_vanilla()
    known = set((vanilla or {}).get("particles", {}))
    found: List[str] = []
    for name, particle in data["particles"].items():
        source = particle.get("vanilla") or particle.get("from")
        if not source or ("vanilla" in particle) == ("from" in particle):
            found.append(f"particle {name}: name exactly one of vanilla or from")
        elif known and source not in known:
            found.append(f"particle {name}: {source} is not a registered vanilla particle (effects_vanilla.json)")
        if particle.get("standin") not in ("flash", "smoke", "fire", "spell", "blast"):
            found.append(f"particle {name}: stand-in {particle.get('standin')!r} is not flash, smoke, fire, spell or blast")
        if "vanilla" in particle and ("colour" in particle or "scale" in particle):
            found.append(f"particle {name}: a vanilla particle is fired as it is; copy it with `from` to change its colour or scale")
    for name, profile in data["profiles"].items():
        found += [f"profile {name}: needs {tag!r}, which is not a setting tag" for tag in profile.get("needs", []) if tag not in data["setting_tags"]]
        names = [slot["locator"] for slot in profile["slots"]]
        for slot in profile["slots"]:
            where = f"profile {name} slot {slot['locator']}"
            if slot.get("spot") not in data["spots"]:
                found.append(f"{where}: spot {slot.get('spot')!r} is unknown")
            if slot.get("spot") not in ("locator", "box_share", "wing_tip") and not slot.get("bone"):
                found.append(f"{where}: the spot {slot.get('spot')} needs a bone")
            if not (isinstance(slot.get("frame"), int) or slot.get("frame") in data["frame_rules"]):
                found.append(f"{where}: frame {slot.get('frame')!r} is neither a whole frame nor a rule")
            if slot.get("frame_from") and slot["frame_from"] not in names:
                found.append(f"{where}: frame_from {slot['frame_from']!r} is no slot of the profile")
            found += [f"{where}: particle {p!r} is not in particles" for p in slot.get("particles", []) if p not in data["particles"]]
    return found


def setting_tags(value: Any) -> List[str]:
    """The job's `setting`: a list of tags, or a mapping of tag to yes or no."""

    if isinstance(value, dict):
        return sorted(tag for tag, on in value.items() if on)
    return sorted(str(tag) for tag in (value or []))


def fit_problems(profiles: Sequence[str], setting: Sequence[str], data: Dict[str, Any], allowed: Optional[Sequence[str]] = None) -> List[str]:
    """EFFECT-FIT (D-127): a profile the unit's world cannot have, or one its preset does not list for the type."""

    found: List[str] = []
    for name in profiles:
        profile = data["profiles"].get(name)
        if profile is None:
            found.append(f"profile {name!r} is not in effects.json ({', '.join(data['profiles'])})")
            continue
        missing = [tag for tag in profile.get("needs", []) if tag not in setting]
        if missing:
            found.append(f"profile {name} needs {', '.join(missing)}, which the unit's setting ({', '.join(setting) or 'none'}) does not have: "
                         f"{data['setting_tags'][missing[0]]}")
        if allowed is not None and name not in allowed:
            found.append(f"profile {name} is not one the preset lists for this type ({', '.join(allowed) or 'none'})")
    return found


# ---- the mesh -----------------------------------------------------------------------------------------------------------

def find_bone(mesh: pdx_deform.SkinnedMesh, name: str) -> Optional[str]:
    if name in mesh.bones:
        return name
    lowered = {bone.lower(): bone for bone in mesh.bones}
    for alias in BONE_ALIASES.get(name.lower(), (name.lower(),)):
        if alias in lowered:
            return lowered[alias]
    return None


def bind_world(mesh: pdx_deform.SkinnedMesh) -> np.ndarray:
    return np.linalg.inv(mesh.inverse_bind)


def descendants(mesh: pdx_deform.SkinnedMesh, bone: int) -> List[int]:
    out = [bone]
    for index, parent in enumerate(mesh.parents):
        if parent >= 0 and parent in out and index not in out:
            out.append(index)
    changed = True
    while changed:
        changed = False
        for index, parent in enumerate(mesh.parents):
            if parent in out and index not in out:
                out.append(index)
                changed = True
    return out


def region(mesh: pdx_deform.SkinnedMesh, bone: str, children: bool = True) -> np.ndarray:
    """Indices of the rendered vertices whose strongest bone is `bone` or one of its children (a hand and its fingers). With
    `children` off, the bone's own part only (a tank's hull without the turret and gun mounted on it)."""

    dominant = pdx_deform.dominant_bones(mesh)
    family = descendants(mesh, mesh.bones.index(bone)) if children else [mesh.bones.index(bone)]
    rendered = ~mesh.collision if len(mesh.collision) == len(mesh.positions) else np.ones(len(mesh.positions), dtype=bool)
    return np.nonzero(np.isin(dominant, family) & rendered)[0]


def front(mesh: pdx_deform.SkinnedMesh) -> np.ndarray:
    """The unit's front in the mesh: from the heels to the toes when the rig has feet and toes, otherwise -z."""

    world = bind_world(mesh)
    pairs = [(find_bone(mesh, f"{side}Foot"), find_bone(mesh, f"{side}ToeBase")) for side in ("Left", "Right")]
    steps = [world[mesh.bones.index(toe)][:3, 3] - world[mesh.bones.index(foot)][:3, 3] for foot, toe in pairs if foot and toe]
    if steps:
        step = np.mean(steps, axis=0)
        step[1] = 0.0
        if np.linalg.norm(step) > 1e-6:
            return step / np.linalg.norm(step)
    return DEFAULT_FRONT.copy()


def _top(points: np.ndarray, direction: np.ndarray) -> np.ndarray:
    along = points @ direction
    count = max(3, int(np.ceil(len(points) * REGION_TOP_SHARE)))
    return points[np.argsort(along)[-count:]].mean(axis=0)


def side_axis(mesh: pdx_deform.SkinnedMesh) -> np.ndarray:
    """The unit's left in the mesh (the rig's left, from the right hand to the left hand), or +x on a rig without hands."""

    world = bind_world(mesh)
    left, right = find_bone(mesh, "LeftHand"), find_bone(mesh, "RightHand")
    if left and right:
        step = world[mesh.bones.index(left)][:3, 3] - world[mesh.bones.index(right)][:3, 3]
        step[1] = 0.0
        if np.linalg.norm(step) > 1e-6:
            return step / np.linalg.norm(step)
    return np.array([1.0, 0.0, 0.0])


def _on_side(points: np.ndarray, side: Optional[str], axis: np.ndarray, centre: np.ndarray) -> np.ndarray:
    if side not in ("l", "r"):
        return points
    along = (points - centre) @ axis
    kept = points[along > 0] if side == "l" else points[along < 0]
    return kept if len(kept) >= 3 else points


def _wing_tip(mesh: pdx_deform.SkinnedMesh, slot: Dict[str, Any]) -> Tuple[np.ndarray, str]:
    """The wing tip on the slot's side: of the vertices whose strongest bone is a wing bone, the farthest 5% from the body's mid-plane,
    and the wing bone that carries most of them."""

    dominant = pdx_deform.dominant_bones(mesh)
    wings = [i for i, name in enumerate(mesh.bones) if "wing" in name.lower()]
    if not wings:
        raise EffectsError(f"slot {slot['locator']}: the rig has no wing bones")
    vertices = np.nonzero(np.isin(dominant, wings))[0]
    axis = side_axis(mesh)
    centre = mesh.positions.mean(axis=0)
    along = (mesh.positions[vertices] - centre) @ axis * (1.0 if slot.get("side") == "l" else -1.0)
    count = max(3, int(np.ceil(len(vertices) * REGION_TOP_SHARE / 2)))
    tip = vertices[np.argsort(along)[-count:]]
    bones, counts = np.unique(dominant[tip], return_counts=True)
    return mesh.positions[tip].mean(axis=0), mesh.bones[int(bones[np.argmax(counts)])]


def spot_point(mesh: pdx_deform.SkinnedMesh, slot: Dict[str, Any], bone: Optional[str]) -> Tuple[np.ndarray, Optional[str]]:
    """The rest-pose point where a new locator goes, in the mesh's space, and the bone it was found on when the spot finds it."""

    spot = slot["spot"]
    if spot == "box_share":
        rendered = mesh.positions[~mesh.collision] if len(mesh.collision) == len(mesh.positions) else mesh.positions
        low, high = rendered.min(axis=0), rendered.max(axis=0)
        return low + np.asarray(slot.get("share", [0.5, 0.5, 0.5]), dtype=float) * (high - low), None
    if spot == "wing_tip":
        return _wing_tip(mesh, slot)
    if bone is None:
        raise EffectsError(f"slot {slot['locator']}: the mesh has no bone {slot.get('bone')!r} ({', '.join(mesh.bones[:12])}...)")
    index = mesh.bones.index(bone)
    vertices = region(mesh, bone, children=spot not in ("bone_top", "bone_centre", "bone_bottom"))
    if len(vertices) < 3:
        raise EffectsError(f"slot {slot['locator']}: the bone {bone} carries no part of the model to measure")
    points = mesh.positions[vertices]
    centre = points.mean(axis=0)
    if spot == "bone_centre":
        return centre, None
    if spot in ("bone_top", "bone_bottom"):
        return np.array([centre[0], points[:, 1].max() if spot == "bone_top" else points[:, 1].min(), centre[2]]), None
    if spot == "hand_tip":
        world = bind_world(mesh)
        parent = mesh.parents[index]
        direction = world[index][:3, 3] - (world[parent][:3, 3] if parent >= 0 else centre)
        if np.linalg.norm(direction) < 1e-9:
            raise EffectsError(f"slot {slot['locator']}: cannot tell which way the hand {bone} points")
        return _top(points, direction / np.linalg.norm(direction)), None
    if spot == "head_front":
        mid = np.median(points[:, 1])
        lower = points[points[:, 1] <= mid + 0.25 * np.ptp(points[:, 1])]
        return _top(lower if len(lower) >= 3 else points, front(mesh)), None
    if spot == "eye":
        # the upper front of the head on one side, pushed back by `inset` of the head's depth: inside a hood's opening, not on its rim
        upper = points[points[:, 1] >= np.median(points[:, 1])]
        half = _on_side(upper if len(upper) >= 3 else points, slot.get("side"), side_axis(mesh), centre)
        ahead = front(mesh)
        depth = float(np.ptp(points @ ahead))
        return _top(half, ahead) - ahead * depth * float(slot.get("inset", EYE_INSET)), None
    raise EffectsError(f"slot {slot['locator']}: the spot {spot} places no new locator")


def mesh_locators(root: PdxNode) -> Dict[str, Dict[str, Any]]:
    locators = root.child("locator")
    return {node.name: dict(node.properties) for node in (locators.children if locators else [])}


def add_locators(mesh_path: Path, locators: Sequence[Dict[str, Any]]) -> List[str]:
    """Write new locators into the `.mesh` (replacing ones of the same name this step wrote before). Returns the names written."""

    root = read(mesh_path)
    node = root.child("locator")
    if node is None:
        node = PdxNode("locator", 1)
        root.children.append(node)
    written = []
    for locator in locators:
        if locator.get("existing"):
            continue
        node.children = [child for child in node.children if child.name != locator["name"]]
        props: Dict[str, Any] = {"p": [float(v) for v in locator["p"]], "q": [0.0, 0.0, 0.0, 1.0]}
        if locator.get("bone"):
            props["pa"] = [locator["bone"]]
        node.children.append(PdxNode(locator["name"], 2, props))
        written.append(locator["name"])
    if written:
        write(mesh_path, root)
    return written


def locator_rest(mesh: pdx_deform.SkinnedMesh, props: Dict[str, Any]) -> Tuple[Optional[str], np.ndarray]:
    """A locator's parent bone and its rest point in the mesh's space (its `p` is in the bone's frame)."""

    parent = props.get("pa")
    bone = str(parent[0]) if parent else None
    p = np.append(np.asarray(props.get("p", [0, 0, 0]), dtype=float), 1.0)
    if bone and bone in mesh.bones:
        return bone, (bind_world(mesh)[mesh.bones.index(bone)] @ p)[:3]
    return bone, p[:3]


def track(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, bone: Optional[str], rest: np.ndarray, matrices: Optional[np.ndarray] = None) -> np.ndarray:
    """(F, 3) positions of a point that follows `bone` rigidly through the clip, as the game moves a locator."""

    frames = max(anim.frames, 1)
    if not bone or bone not in mesh.bones:
        return np.tile(rest, (frames, 1))
    m = (matrices if matrices is not None else pdx_deform.skinning_matrices(mesh, anim))[:, mesh.bones.index(bone)]
    return np.einsum("fij,j->fi", m[:, :3, :3], rest) + m[:, :3, 3]


# ---- frames -------------------------------------------------------------------------------------------------------------

def _hips(mesh: pdx_deform.SkinnedMesh) -> Optional[str]:
    for name in ("Hips", "Hip", "Pelvis", "root", "Root"):
        found = find_bone(mesh, name)
        if found:
            return found
    roots = [bone for bone, parent in zip(mesh.bones, mesh.parents) if parent < 0]
    return roots[0] if roots else None


def _recoil(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, bone: Optional[str]) -> Tuple[int, Dict[str, Any]]:
    chain, index = [], mesh.bones.index(bone) if bone in mesh.bones else -1
    while index >= 0 and len(chain) < 3:
        chain.append(mesh.bones[index])
        index = mesh.parents[index]
    moves = {name: np.linalg.norm(anim.channels[name]["t"] - anim.channels[name]["t"][0], axis=1) for name in chain if name in anim.channels}
    if not moves:
        raise EffectsError(f"recoil: no bone of {', '.join(chain) or bone} is keyed in the clip")
    gun = max(moves, key=lambda name: moves[name].max())
    largest = float(moves[gun].max())
    if largest < 1e-4 * max(mesh.height, 1e-6):
        raise EffectsError(f"recoil: the gun ({', '.join(chain)}) does not move in the clip, so there is no shot to time")
    return int(np.argmax(moves[gun] > RECOIL_SHARE * largest)), {"rule": "recoil", "bone": gun, "largest_move": round(largest, 4)}


def measure_frame(rule: Any, mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, bone: Optional[str], rest: np.ndarray,
                  matrices: Optional[np.ndarray] = None) -> Tuple[int, Dict[str, Any]]:
    """The frame of a slot's rule in a clip, and the numbers it was read from."""

    if isinstance(rule, int):
        return rule, {"rule": "given"}
    if rule == "start":
        return 0, {"rule": rule}
    if rule == "recoil":
        return _recoil(mesh, anim, bone)
    matrices = matrices if matrices is not None else pdx_deform.skinning_matrices(mesh, anim)
    path = track(mesh, anim, bone, rest, matrices)
    height = max(mesh.height, 1e-6)
    if rule == "strike":
        hips = _hips(mesh)
        centre = track(mesh, anim, hips, bind_world(mesh)[mesh.bones.index(hips)][:3, 3], matrices) if hips else np.zeros_like(path)
        reach = (path - centre) @ front(mesh)
        frame = int(np.argmax(reach))
        return frame, {"rule": rule, "reach": round(float(reach[frame]), 4), "reach_frame0": round(float(reach[0]), 4)}
    moved = np.linalg.norm(path - path[0], axis=1)
    if rule == "part_leaves":
        if moved.max() <= LEAVE_SHARE * height:
            raise EffectsError(f"part_leaves: the locator never moves {LEAVE_SHARE:.0%} of the height in the clip")
        return int(np.argmax(moved > LEAVE_SHARE * height)), {"rule": rule, "moved": round(float(moved.max()), 4)}
    if rule == "peak":
        return int(np.argmax(moved)), {"rule": rule, "moved": round(float(moved.max()), 4)}
    raise EffectsError(f"frame rule {rule!r} is unknown")


# ---- the plan -----------------------------------------------------------------------------------------------------------

def clip_for(folder: Path, stem: str, role: str) -> Optional[Path]:
    for name in (role, ROLE_CLIPS.get(role, role)):
        path = folder / f"{stem}_{name}.anim"
        if path.is_file():
            return path
    return None


def plan_path(folder: Path, stem: str) -> Path:
    return Path(folder) / f"{stem}{PLAN_SUFFIX}"


def read_plan(folder: Path, stem: str) -> Optional[Dict[str, Any]]:
    path = plan_path(folder, stem)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def _particle_entry(stem: str, key: str, spec: Dict[str, Any], colour: Optional[Sequence[int]], rest_of_clip: float, vanilla: Dict[str, Any]) -> Dict[str, Any]:
    """A plan's particle. `duration_s` is seconds, `clip` (the rest of the clip and `AFTER_CLIP_S`) or `loop` (vanilla's endless emitter
    kept, for a glow that plays all through every state that fires it)."""

    loop = spec.get("duration_s") == "loop"
    duration = rest_of_clip + AFTER_CLIP_S if spec.get("duration_s") in ("clip", "loop") else float(spec.get("duration_s", 1.0))
    if "vanilla" in spec:
        return {"key": key, "name": spec["vanilla"], "vanilla": True, "standin": spec["standin"], "duration_s": round(duration, 3), "loop": loop}
    source = vanilla.get("particles", {}).get(spec["from"], {})
    return {"key": key, "name": f"{stem}_{key}_particle", "vanilla": False, "from": spec["from"], "source": source.get("file"),
            "source_type": source.get("type"), "colour": list(colour or spec.get("colour") or []) or None, "tint_grey": bool(spec.get("tint_grey")),
            "scale": spec.get("scale", 1), "standin": spec["standin"], "duration_s": round(duration, 3), "loop": loop, "type": f"{stem}_{key}_file"}


def _place(mesh: pdx_deform.SkinnedMesh, slot: Dict[str, Any], existing: Dict[str, Dict[str, Any]], profile: str) -> Tuple[Dict[str, Any], Optional[str], np.ndarray]:
    """The slot's locator entry, the bone its frame is measured on and its rest point."""

    where = f"profile {profile} slot {slot['locator']}"
    if slot["spot"] == "locator":
        if slot["locator"] not in existing:
            raise EffectsError(f"{where}: the mesh has no locator {slot['locator']!r} ({', '.join(existing) or 'none'})")
        bone, rest = locator_rest(mesh, existing[slot["locator"]])
        return {"name": slot["locator"], "bone": bone, "measure_bone": bone, "existing": True}, bone, rest
    bone = find_bone(mesh, slot["bone"]) if slot.get("bone") else None
    if slot.get("bone") and bone is None and slot["spot"] != "box_share":
        raise EffectsError(f"{where}: the mesh has no bone {slot['bone']!r}")
    rest, found = spot_point(mesh, slot, bone)
    bone = found or bone
    # `parent`: measured on one part, hung from another (a blast where the turret leaves stays with the hull)
    hang = find_bone(mesh, slot["parent"]) if slot.get("parent") else bone
    if slot.get("parent") and hang is None:
        raise EffectsError(f"{where}: the mesh has no bone {slot['parent']!r}")
    local = (np.linalg.inv(bind_world(mesh)[mesh.bones.index(hang)]) @ np.append(rest, 1.0))[:3] if hang else rest
    entry = {"name": slot["locator"], "bone": hang, "measure_bone": bone, "existing": False, "spot": slot["spot"],
             "p": [round(float(v), 5) for v in local]}
    return entry, bone, rest


class _Planner:
    """Collects one plan's locators, events, particles and sounds."""

    def __init__(self, folder: Path, stem: str, mesh: pdx_deform.SkinnedMesh, data: Dict[str, Any], vanilla: Dict[str, Any], job_effects: Dict[str, Any]):
        self.folder, self.stem, self.mesh, self.data, self.vanilla = folder, stem, mesh, data, vanilla
        self.colours = job_effects.get("colour") or {}
        self.given = job_effects.get("frames") or {}
        self.locators: List[Dict[str, Any]] = []
        self.events: List[Dict[str, Any]] = []
        self.particles: Dict[str, Dict[str, Any]] = {}
        self.sounds: List[Dict[str, Any]] = []
        self.cache: Dict[str, Tuple[pdx_deform.Animation, np.ndarray]] = {}

    def clip(self, path: Path) -> Tuple[pdx_deform.Animation, np.ndarray]:
        if path.name not in self.cache:
            anim = pdx_deform.load_anim(path)
            self.cache[path.name] = (anim, pdx_deform.skinning_matrices(self.mesh, anim))
        return self.cache[path.name]

    def slot(self, profile: str, slot: Dict[str, Any], entry: Dict[str, Any], bone: Optional[str], rest: np.ndarray, frames: Dict[Tuple[str, str], int]) -> None:
        entry["rest"] = [round(float(v), 4) for v in rest]
        if not any(known["name"] == entry["name"] for known in self.locators):
            self.locators.append(entry)
        for role in slot["roles"]:
            path = clip_for(self.folder, self.stem, role)
            if path is None:
                continue  # the unit has no clip for this role
            anim, matrices = self.clip(path)
            given = self.given.get(slot["locator"])
            if slot.get("frame_from") and (slot["frame_from"], path.name) in frames:
                frame, how = frames[(slot["frame_from"], path.name)], {"rule": "frame_from", "slot": slot["frame_from"]}
            else:
                frame, how = measure_frame(int(given) if given is not None else slot["frame"], self.mesh, anim, bone, rest, matrices)
            frames[(slot["locator"], path.name)] = frame
            fps = anim.fps or FPS
            seconds = frame / fps + float(slot.get("offset_s", 0.0))
            for key in slot.get("particles", []):
                particle = _particle_entry(self.stem, key, self.data["particles"][key], self.colours.get(key),
                                           max(max(anim.frames, 1) / fps - seconds, 0.5), self.vanilla)
                self.particles.setdefault(particle["name"], particle)
                self.events.append({"profile": profile, "role": role, "clip": path.stem, "node": slot["locator"], "bone": entry["bone"],
                                    "measure_bone": bone, "frame": frame, "time": round(seconds, 3), "particle": particle["name"],
                                    "standin": particle["standin"], "duration_s": particle["duration_s"], "loop": particle["loop"],
                                    "colour": particle.get("colour"), "measured": how})
            if slot.get("sound"):
                self.sounds.append({"role": role, "soundeffect": slot["sound"], "frame": int(round(seconds * fps))})


def make_plan(folder: Path, stem: str, job_effects: Dict[str, Any], *, allowed: Optional[Sequence[str]] = None,
              data: Optional[Dict[str, Any]] = None, vanilla: Optional[Dict[str, Any]] = None, write_mesh: bool = True) -> Dict[str, Any]:
    """Measure and write the job's effects for the unit files in `folder` (`<stem>.mesh`, `<stem>_<role>.anim`). Returns the plan."""

    data = data or load()
    vanilla = vanilla if vanilla is not None else load_vanilla()
    folder = Path(folder)
    profiles = list(job_effects.get("profiles") or [])
    if not profiles:
        raise EffectsError("the job's effects block names no profiles")
    setting = setting_tags(job_effects.get("setting"))
    problems = fit_problems(profiles, setting, data, allowed)
    if problems:
        raise EffectsError("EFFECT-FIT: " + "; ".join(problems))
    mesh_path = folder / f"{stem}.mesh"
    mesh = pdx_deform.load_mesh(mesh_path)
    existing = mesh_locators(read(mesh_path))
    planner = _Planner(folder, stem, mesh, data, vanilla, job_effects)
    for name in profiles:
        frames: Dict[Tuple[str, str], int] = {}
        for slot in data["profiles"][name]["slots"]:
            entry, bone, rest = _place(mesh, slot, existing, name)
            planner.slot(name, slot, entry, bone, rest, frames)
    if write_mesh:
        add_locators(mesh_path, [entry for entry in planner.locators if not entry["existing"]])
    plan = {"stem": stem, "profiles": profiles, "setting": setting, "locators": planner.locators, "events": planner.events,
            "particles": list(planner.particles.values()), "sounds": planner.sounds,
            "time_unit": "seconds of the clip (frame / fps), measured on vanilla's destroyed landmarks by calibrate_effects.py"}
    plan_path(folder, stem).write_text(json.dumps(plan, indent=1) + "\n", encoding="utf-8", newline="\n")
    return plan


# ---- particle files -----------------------------------------------------------------------------------------------------

_COLOUR = re.compile(r"(color\s*=\s*\{\s*x\s*=\s*)([-\d.]+)(\s*y\s*=\s*)([-\d.]+)(\s*z\s*=\s*)([-\d.]+)")


def recolour(text: str, colour: Sequence[float], tint_grey: bool = False) -> str:
    """Each coloured subsystem takes `colour`'s hue and saturation at its own brightness. Grey ones (smoke) keep their colour, unless
    `tint_grey` (a necromancer's purple smoke), when they take the hue too."""

    hue, saturation, _value = colorsys.rgb_to_hsv(*[max(0.0, min(255.0, float(c))) / 255.0 for c in colour])

    def swap(match: "re.Match[str]") -> str:
        r, g, b = (float(match.group(i)) for i in (2, 4, 6))
        _h, s, v = colorsys.rgb_to_hsv(*[max(0.0, min(255.0, c)) / 255.0 for c in (r, g, b)])
        if s < GREY_SATURATION and not tint_grey:
            return match.group(0)
        nr, ng, nb = (255.0 * c for c in colorsys.hsv_to_rgb(hue, saturation, v))
        return f"{match.group(1)}{nr:.3f}{match.group(3)}{ng:.3f}{match.group(5)}{nb:.3f}"

    return _COLOUR.sub(swap, text)


def adapted_particle(text: str, source_type: Optional[str], new_type: str, colour: Optional[Sequence[float]], duration: Optional[float],
                     tint_grey: bool = False) -> str:
    """A copy of vanilla's particle `source_type` (the block of that name in the file) under `new_type`, recoloured, its endless
    subsystems made to emit for `duration` seconds (None keeps them endless, for a looping glow). Size is set by the registration's
    `scale`, so nothing else changes."""

    blocks = _particle_blocks(text)
    chosen = next((b for b in blocks if b[0] == source_type), blocks[0] if blocks else None)
    if chosen is None:
        raise EffectsError(f"no particle block in the file for {source_type}")
    out = re.sub(r'(\bname\s*=\s*)"[^"]*"', lambda m: f'{m.group(1)}"{new_type}"', chosen[1], count=1)
    if colour:
        out = recolour(out, colour, tint_grey)
    if duration is not None:
        out = re.sub(r"\bduration\s*=\s*-1(\.0+)?", f"duration={duration:.3f}", out)
    return out.rstrip() + "\n"


def _particle_blocks(text: str) -> List[Tuple[Optional[str], str]]:
    out = []
    for match in re.finditer(r"\bparticle\s*=\s*\{", text):
        depth, index = 0, match.end() - 1
        while index < len(text):
            depth += {"{": 1, "}": -1}.get(text[index], 0)
            if depth == 0:
                break
            index += 1
        body = text[match.start(): index + 1]
        name = re.search(r'\bname\s*=\s*"([^"]*)"', body)
        out.append((name.group(1) if name else None, body))
    return out


def particle_files(plan: Dict[str, Any], game: Optional[Path]) -> Tuple[List[Tuple[str, str]], List[str]]:
    """(mod path, text) for each adapted particle and the `.gfx` that registers them, and the problems (a vanilla file not found)."""

    files, problems, entries = [], [], []
    stem = plan["stem"]
    for particle in plan.get("particles", []):
        if particle.get("vanilla"):
            continue
        source = (Path(game) / particle["source"]) if game and particle.get("source") else None
        if source is None or not source.is_file():
            problems.append(f"particle {particle['name']}: the vanilla file {particle.get('source')} of {particle.get('from')} is not in the game folder")
            continue
        text = adapted_particle(source.read_text(encoding="utf-8", errors="replace"), particle.get("source_type"), particle["type"],
                                particle.get("colour"), None if particle.get("loop") else particle.get("duration_s"), bool(particle.get("tint_grey")))
        files.append((f"gfx/particles/{stem}_{particle['key']}.asset", text))
        entries.append({"name": particle["name"], "type": particle["type"], "scale": particle.get("scale", 1)})
    if entries:
        body = "".join(f'\tpdxparticle = {{\n\t\tname = "{e["name"]}"\n\t\ttype = "{e["type"]}"\n\t\tscale = {float(e["scale"]):g}\n\t}}\n' for e in entries)
        files.append((f"gfx/entities/{stem}_effects_particles.gfx", "objectTypes = {\n" + body + "}\n"))
    return files, problems


# ---- checks -------------------------------------------------------------------------------------------------------------

def _finding(rule: str, message: str, **numbers: Any) -> Dict[str, Any]:
    return {"rule": rule, "severity": "error", "message": message, **numbers}


def _locator_findings(plan: Dict[str, Any], present: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for locator in plan["locators"]:
        props = present.get(locator["name"])
        bone = str(props["pa"][0]) if props and props.get("pa") else None
        if props is None or (locator.get("bone") and bone != locator["bone"]):
            out.append(_finding("EFFECT-LOCATOR", f"the mesh lacks the locator {locator['name']} on {locator.get('bone')} (found {bone if props else 'none'})"))
    return out


def _event_findings(folder: Path, plan: Dict[str, Any], mesh: pdx_deform.SkinnedMesh, present: Dict[str, Dict[str, Any]], data: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    height = max(mesh.height, 1e-6)
    slots = {(slot["locator"], name): slot for name in plan["profiles"] for slot in data["profiles"].get(name, {}).get("slots", [])}
    checked = set()
    for event in plan["events"]:
        clip = folder / f"{event['clip']}.anim"
        if not clip.is_file():
            out.append(_finding("EFFECT-FRAME", f"{event['particle']} fires in {event['clip']}, which is not beside the mesh"))
            continue
        anim = pdx_deform.load_anim(clip)
        if not 0 <= event["frame"] < max(anim.frames, 1):
            out.append(_finding("EFFECT-FRAME", f"{event['particle']} at {event['node']} fires at frame {event['frame']}, outside {event['clip']} ({anim.frames} frames)"))
            continue
        if (event["node"], event["clip"]) in checked or event["node"] not in present:
            continue
        checked.add((event["node"], event["clip"]))
        bone, rest = locator_rest(mesh, present[event["node"]])
        matrices = pdx_deform.skinning_matrices(mesh, anim)
        slot = slots.get((event["node"], event["profile"]), {})
        rule = event.get("measured", {}).get("rule")
        if rule not in (None, "given", "frame_from") and slot:
            try:
                again, _how = measure_frame(slot["frame"], mesh, anim, event.get("measure_bone") or bone, rest, matrices)
            except EffectsError as error:
                out.append(_finding("EFFECT-FRAME", f"{event['node']} in {event['clip']}: {error}"))
                again = event["frame"]
            if again != event["frame"]:
                out.append(_finding("EFFECT-FRAME", f"{event['node']} in {event['clip']}: the plan fires at frame {event['frame']}, its rule {rule} now measures {again}. Run effects_stage.py again", planned=event["frame"], measured=again))
        if bone and bone in mesh.bones and event["role"] != "death":
            drift = on_part_drift(mesh, anim, bone, rest, matrices)
            if drift > ON_PART_SHARE * height:
                out.append(_finding("EFFECT-ON-PART", f"{event['node']} leaves its part in {event['clip']}: its distance to the part changes by {drift / height:.1%} of the height (limit {ON_PART_SHARE:.0%})", share=round(drift / height, 4)))
    return out


def _particle_findings(plan: Dict[str, Any], vanilla: Dict[str, Any], game: Optional[Path]) -> List[Dict[str, Any]]:
    out = []
    known = set((vanilla or {}).get("particles", {}))
    for particle in plan.get("particles", []):
        if particle.get("vanilla"):
            if known and particle["name"] not in known:
                out.append(_finding("EFFECT-PARTICLE", f"{particle['name']} is not a registered vanilla particle (effects_vanilla.json)"))
        elif not particle.get("source"):
            out.append(_finding("EFFECT-PARTICLE", f"{particle['name']}: the vanilla particle {particle.get('from')} it copies has no known file"))
        elif game is not None and not (Path(game) / particle["source"]).is_file():
            out.append(_finding("EFFECT-PARTICLE", f"{particle['name']}: {particle['source']} is not in the game folder"))
    return out


def findings(folder: Path, stem: str, plan: Optional[Dict[str, Any]] = None, *, data: Optional[Dict[str, Any]] = None,
             vanilla: Optional[Dict[str, Any]] = None, game: Optional[Path] = None, allowed: Optional[Sequence[str]] = None) -> List[Dict[str, Any]]:
    """Check a plan against the files: the profiles fit (EFFECT-FIT), each locator is in the mesh on its bone (EFFECT-LOCATOR), each
    event's frame is inside its clip and is still what its rule measures (EFFECT-FRAME), the locator stays on its part through every clip
    that fires it (EFFECT-ON-PART) and each particle exists (EFFECT-PARTICLE)."""

    folder = Path(folder)
    plan = plan or read_plan(folder, stem)
    if plan is None:
        return []
    data = data or load()
    vanilla = vanilla if vanilla is not None else load_vanilla()
    mesh_path = folder / f"{stem}.mesh"
    mesh = pdx_deform.load_mesh(mesh_path)
    present = mesh_locators(read(mesh_path))
    out = [_finding("EFFECT-FIT", text) for text in fit_problems(plan["profiles"], plan.get("setting", []), data, allowed)]
    out += _locator_findings(plan, present)
    out += _event_findings(folder, plan, mesh, present, data)
    out += _particle_findings(plan, vanilla, game)
    return out


def on_part_drift(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, bone: str, rest: np.ndarray, matrices: np.ndarray) -> float:
    """How far the locator's distance to the nearest vertices of its part changes over the clip (its part bends away from it)."""

    vertices = region(mesh, bone)
    if len(vertices) == 0:
        return 0.0
    distance = np.linalg.norm(mesh.positions[vertices] - rest, axis=1)
    near = vertices[np.argsort(distance)[: max(8, len(vertices) // 50)]]
    path = track(mesh, anim, bone, rest, matrices)
    joints = np.clip(mesh.joints[near], 0, None)
    weights = mesh.weights[near]
    base = None
    worst = 0.0
    for frame in range(max(anim.frames, 1)):
        m = matrices[frame][joints]  # (N, 4, 4, 4)
        moved = np.einsum("nk,nkij,nj->ni", weights, m[:, :, :3, :3], mesh.positions[near]) + np.einsum("nk,nki->ni", weights, m[:, :, :3, 3])
        mean = float(np.linalg.norm(moved - path[frame], axis=1).mean())
        base = mean if base is None else base
        worst = max(worst, abs(mean - base))
    return worst


def summary_lines(plan: Dict[str, Any]) -> Iterable[str]:
    for locator in plan["locators"]:
        how = "existing" if locator.get("existing") else f"new, {locator.get('spot')}"
        yield f"locator {locator['name']} on {locator.get('bone')} ({how}) at {locator['rest']}"
    for event in plan["events"]:
        loop = ", looping" if event.get("loop") else ""
        yield f"{event['role']}: {event['particle']} at {event['node']}, frame {event['frame']} = time {event['time']:g} s ({event['measured'].get('rule')}{loop})"
    for sound in plan.get("sounds", []):
        yield f"sound {sound['soundeffect']} in {sound['role']} at frame {sound['frame']}"
