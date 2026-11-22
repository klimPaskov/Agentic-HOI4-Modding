"""What a humanoid's clip reads as from the map camera at game size: its outline, not only how many pixels change.

Pure numpy on the exported `.mesh` and `.anim` (`lib/pdx_deform`), with the camera of `lib/map_read.py` (the review sheets' `hoi4` view, 25
degrees round from the front and 55 above the horizon, one pixel `1 / MAP_PIXELS` of the rest height, so the unit is about 60 pixels tall).

TRIPO-MAP-READ and TRIPO-MAP-ALIKE count changed pixels. The D-94 zombie passed both in run h (attack 358, defend 307, defend against attack
338) and both fresh reviews failed it: its wide grab and its recoil defend read as a T-pose and as each other. In run f the forward grab
foreshortened into the body. In run d the idle stood upright and read as a live soldier. These four rules read the outline itself:

- TRIPO-MAP-POSTURE: the idle's posture. The body outline (the skin of every bone but the arms, a weapon, a shield and wings) of the idle is
  measured against the rest pose's, as its height on the map camera (the median over the idle's frames over the rest pose's). A hunched body
  is lower from above, because the head comes forward toward the camera. Measured 2026-11-22: zombie_d 1.00 (upright idle, both reviewers
  read a live soldier), zombie_f and zombie_h 0.88 (the `idle_pose: hunch` rule, four reviewers read it hunched), vanilla GER infantry
  `idle_rifle` 0.98, the passed humanoids orc_k 1.02, ogre_l 1.00, dwarf_f 0.98, demon_g 0.98, zombie_w 1.07. `POSTURE_LIMIT` lies between
  the hunch (0.88) and vanilla's upright soldier (0.98): a job's `tripo.posture` of `hunched` needs the idle at or under it, `upright` above.
- TRIPO-MAP-SPREAD: an attack or a defend that spreads both arms wide reads as a T-pose. Per frame, the horizontal distance on the map
  camera between the two hand joints when they lie on either side of the chest joint, over the idle body outline's height. The reading is
  the clip's 90th percentile frame. zombie_h's attack 0.87 and defend 1.21 (both reviewers: a T-pose). Passed: orc_k attack 0.62 and
  defend 0.70 (hands on one haft), ogre_l 0.69 and 0.56, dwarf_f 0.54 and 0.63, demon_g 0.03 and 0.27, vanilla GER 0.24 and 0.20 (its
  attack_stand_rifle and attack_crouch_rifle). zombie_d's flung arms 0.53, zombie_f 0.45. `SPREAD_LIMIT` lies between the passed 0.70 and
  the failed 0.87.
- TRIPO-MAP-REACH: an attack's strike that stays inside the body's outline reads as nothing. The striking end is the weapon's skin, or both
  hands' skin for an unarmed unit. The strike is the frames where it reaches furthest ahead of the chest joint, within `STRIKE_WINDOW` of
  the height of its peak. The reading is how far, in pixels at game size, its furthest point lies outside the body outline at the strike.
  From the high front camera a forward reach comes toward the viewer and lands on the body and legs: zombie_f 4 (reviewers: the hands
  foreshorten under the helmet) and zombie_w 4 (reviewers: the attack reads as the idle) (zombie_h 8, its wide grab closing, which TRIPO-MAP-SPREAD fails). Passed: orc_k 16 (the poleaxe head), ogre_l 9
  (the club), dwarf_f 29 (the glaive). zombie_d 11 (an arm flung out to the side). `MIN_REACH_PIXELS` lies between. A winged unit is not judged here: demon_g's claws stay
  inside its outline at the strike (0) and two reviewers read its attack by the wings' beat and the body's drop (the wing checks judge
  those). Vanilla's infantry attacks shoot a rifle held in the hands, with no melee strike to see (GER infantry reads 0), so they are no
  reference here, and the rule is for a melee attack.
- TRIPO-MAP-SAME: the attack and the defend share an outline type, so they read as each other. The type this module reads is the wide
  spread of TRIPO-MAP-SPREAD: zombie_h's attack (0.87) and defend (1.21) both reach it, and both reviewers read the defend as the attack's
  peak. Add a type here when a review names another shared shape, with its measure and the runs that set its limit.

Every reading is reported with its limit in the check's numbers, so a weaker model can read which rule failed and by how much.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence

import numpy as np

from . import map_read, pdx_deform

POSTURES = ("upright", "hunched")
POSTURE_LIMIT = 0.93
SPREAD_LIMIT = 0.80
MIN_REACH_PIXELS = 5
STRIKE_WINDOW = 0.02  # of the height: the frames within this of the striking end's furthest reach are the strike
SPREAD_ROLES = ("attack", "defend")
REACH_CAP = 40  # pixels: a striking end further out than this reads anyway


def _descendants(parents: Sequence[int], roots: Sequence[int]) -> np.ndarray:
    inside = np.zeros(len(parents), dtype=bool)
    inside[list(roots)] = True
    changed = True
    while changed:
        changed = False
        for index, parent in enumerate(parents):
            if not inside[index] and parent >= 0 and inside[parent]:
                inside[index] = True
                changed = True
    return inside


def bone_parts(mesh: pdx_deform.SkinnedMesh, weapon_bone: str = "") -> Dict[str, np.ndarray]:
    """Per bone: `arm` (the upper arms down through the hands), `hand` (the hands and below, also as `left_hand` and `right_hand`), `weapon` (the weapon's bone and below, or any
    bone named `Weapon`), `shield`, `wing` (a bone whose name holds `wing`), and `body` (every other bone)."""

    names = list(mesh.bones)
    index = {name: i for i, name in enumerate(names)}
    arm_roots = [index[name] for name in ("LeftArm", "RightArm") if name in index]
    hand_roots = [index[name] for name in ("LeftHand", "RightHand") if name in index]
    weapon_roots = [i for i, name in enumerate(names) if name == weapon_bone or name.startswith("Weapon")]
    shield_roots = [i for i, name in enumerate(names) if name.startswith("Shield")]
    weapon = _descendants(mesh.parents, weapon_roots) if weapon_roots else np.zeros(len(names), bool)
    shield = _descendants(mesh.parents, shield_roots) if shield_roots else np.zeros(len(names), bool)
    wing = np.array(["wing" in name.lower() for name in names], dtype=bool)
    arm = (_descendants(mesh.parents, arm_roots) if arm_roots else np.zeros(len(names), bool)) & ~weapon & ~shield
    hand = (_descendants(mesh.parents, hand_roots) if hand_roots else np.zeros(len(names), bool)) & ~weapon & ~shield
    body = ~(arm | weapon | shield | wing)
    sides = {}
    for side in ("Left", "Right"):
        root = index.get(f"{side}Hand")
        sides[f"{side.lower()}_hand"] = (_descendants(mesh.parents, [root]) & ~weapon & ~shield) if root is not None else np.zeros(len(names), bool)
    return {"arm": arm, "hand": hand, "weapon": weapon, "shield": shield, "wing": wing, "body": body, **sides}


class OutlineCamera:
    """The map camera of `lib/map_read.MapCamera`, with the body outline (no arms, weapon, shield or wings) beside the full silhouette."""

    def __init__(self, mesh: pdx_deform.SkinnedMesh, weapon_bone: str = ""):
        self.mesh = mesh
        self.camera = map_read.MapCamera(mesh)
        dominant = pdx_deform.dominant_bones(mesh)
        self.parts = {name: mask[dominant] for name, mask in bone_parts(mesh, weapon_bone).items()}
        triangles = self.camera.triangles
        body_triangles = triangles[self.parts["body"][triangles].all(axis=1)]
        self.body_vertices = np.unique(body_triangles)
        remap = -np.ones(len(mesh.positions), dtype=int)
        remap[self.body_vertices] = np.arange(len(self.body_vertices))
        self.body_triangles = remap[body_triangles]
        self.bind = np.linalg.inv(mesh.inverse_bind)

    def screen(self, points: np.ndarray) -> np.ndarray:
        """(N, 2) pixel coordinates (column, row; rows grow upward) of world points on this camera."""

        camera = self.camera
        return (np.stack([points @ camera.right, points @ camera.up], axis=-1) - camera.origin) / camera.pixel

    def body_mask(self, posed: np.ndarray) -> np.ndarray:
        camera = self.camera
        points = posed[self.body_vertices]
        samples = map_read.face_samples(points, self.body_triangles, 0.5 * camera.pixel)
        cells = np.clip(np.floor(self.screen(samples)).astype(int), 0, camera.size - 1)
        mask = np.zeros((camera.size, camera.size), dtype=bool)
        mask[cells[:, 1], cells[:, 0]] = True
        return mask

    def posed(self, anim: pdx_deform.Animation, count: Optional[int] = map_read.MAX_FRAMES):
        """[(frame index, posed vertices, joint positions)] for `count` evenly spaced frames, or every frame with `count=None`."""

        matrices = pdx_deform.skinning_matrices(self.mesh, anim)
        total = matrices.shape[0]
        picks = range(total) if count is None else np.unique(np.linspace(0, total - 1, min(count, total)).round().astype(int))
        return [(int(i), pdx_deform.skin(self.mesh, matrices[i]), (matrices[i] @ self.bind)[:, :3, 3]) for i in picks]


def outline_height(mask: np.ndarray) -> int:
    rows = np.nonzero(mask.any(axis=1))[0]
    return int(rows[-1] - rows[0] + 1) if len(rows) else 0


def distance_outside(mask: np.ndarray, cap: int = REACH_CAP) -> np.ndarray:
    """Per pixel, how many pixels (8-neighbour steps) it lies outside `mask`, up to `cap`. Inside the mask 0."""

    distance = np.full(mask.shape, cap, dtype=int)
    grown = mask.copy()
    distance[grown] = 0
    for step in range(1, cap):
        wider = map_read._grow(grown)
        distance[wider & ~grown] = step
        grown = wider
    return distance


def _bone(mesh: pdx_deform.SkinnedMesh, *names: str) -> int:
    for name in names:
        if name in mesh.bones:
            return mesh.bones.index(name)
    return -1


def chest_bone(mesh: pdx_deform.SkinnedMesh) -> int:
    return _bone(mesh, "Spine02", "Spine2", "Spine01", "back_mid", "Spine")


def posture_reading(view: OutlineCamera, idle: pdx_deform.Animation) -> dict:
    """The idle's body outline height over the rest pose's, on the map camera (median over the idle's frames)."""

    rest = outline_height(view.body_mask(view.mesh.positions))
    heights = [outline_height(view.body_mask(posed)) for _, posed, _ in view.posed(idle)]
    ratio = float(np.median(heights)) / rest if rest else 1.0
    return {"idle_height_px": float(np.median(heights)), "rest_height_px": rest, "ratio": round(ratio, 3)}


def idle_body_height(view: OutlineCamera, idle: pdx_deform.Animation) -> float:
    return float(np.median([outline_height(view.body_mask(posed)) for _, posed, _ in view.posed(idle)]))


def spread_series(view: OutlineCamera, anim: pdx_deform.Animation, body_height: float) -> List[tuple]:
    """[(frame, spread)]: per frame, the horizontal distance between the hand joints on the map camera when they lie either side of the chest, over the idle
    body outline's height (0 when both hands are on one side)."""

    left, right, chest = _bone(view.mesh, "LeftHand"), _bone(view.mesh, "RightHand"), chest_bone(view.mesh)
    if min(left, right, chest) < 0 or body_height <= 0:
        return []
    out = []
    for frame, _, joints in view.posed(anim):
        hands = view.screen(joints[[left, right]])
        middle = view.screen(joints[chest][None])[0]
        sides = np.sign(hands[:, 0] - middle[0])
        out.append((frame, float(abs(hands[0, 0] - hands[1, 0])) / body_height if sides[0] != sides[1] else 0.0))
    return out


def spread_reading(view: OutlineCamera, anim: pdx_deform.Animation, body_height: float) -> Optional[dict]:
    """TRIPO-MAP-SPREAD's reading of one clip: its 90th percentile frame of `spread_series`, its peak and the peak's frame. None without hands."""

    series = spread_series(view, anim, body_height)
    if not series:
        return None
    values = [value for _, value in series]
    return {"p90": round(float(np.percentile(values, map_read.READ_PERCENTILE)), 3), "peak": round(max(values), 3),
            "peak_frame": series[int(np.argmax(values))][0], "limit": SPREAD_LIMIT}


def striking_points(view: OutlineCamera, posed: np.ndarray, armed: bool) -> np.ndarray:
    """The striking end in one frame: every vertex of the weapon's skin, or for an unarmed unit the middle of each hand's skin. A hand is a
    few pixels at game size, so its middle is what shows: its fingertips reach a few pixels further (zombie_f 7 pixels at the fingertips, 3
    at the hand's middle and wrist) and a reviewer still saw the hands under the helmet."""

    parts = view.parts
    if armed:
        return posed[parts["weapon"]]
    hands = [posed[parts[side]].mean(axis=0) for side in ("left_hand", "right_hand") if parts[side].any()]
    return np.array(hands) if hands else np.zeros((0, 3))


def reach_reading(view: OutlineCamera, attack: pdx_deform.Animation, armed: bool) -> dict:
    """How far, in pixels at game size, the striking end (`striking_points`) shows outside the body outline at the strike: the frames where it
    reaches within `STRIKE_WINDOW` of the height of its furthest ahead of the chest joint. The most over those frames."""

    chest = chest_bone(view.mesh)
    if chest < 0:
        return {}
    front = map_read.front_of(view.mesh)
    height = max(view.mesh.height, 1e-9)
    frames = [(index, posed, joints, striking_points(view, posed, armed)) for index, posed, joints in view.posed(attack, None)]
    if not len(frames) or not len(frames[0][3]):
        return {}
    reach = [float(((points - joints[chest]) @ front).max()) / height for _, _, joints, points in frames]
    peak = max(reach)
    strike = [frame for frame, value in zip(frames, reach) if value >= peak - STRIKE_WINDOW]
    best, best_frame = 0, strike[0][0]
    for index, posed, _, points in strike:
        distance = distance_outside(view.body_mask(posed))
        cells = np.clip(np.floor(view.screen(points)).astype(int), 0, distance.shape[0] - 1)
        value = int(distance[cells[:, 1], cells[:, 0]].max())
        if value > best:
            best, best_frame = value, index
    return {"pixels": best, "frame": best_frame, "strike_frames": [frame[0] for frame in strike], "reach_peak": round(peak, 3),
            "striking_end": "weapon" if armed else "hands"}


def posture_of(job: Optional[dict]) -> str:
    """The idle posture a job asks for: `tripo.posture`, else `hunched` when `tripo.idle_pose` is `hunch`, else `upright`."""

    tripo = (job or {}).get("tripo") or {}
    posture = tripo.get("posture")
    if posture:
        if posture not in POSTURES:
            raise ValueError(f"tripo.posture must be one of {', '.join(POSTURES)}, not {posture!r}")
        return posture
    return "hunched" if tripo.get("idle_pose") == "hunch" else "upright"


def _role(clip: str) -> str:
    return clip.rsplit("_", 1)[-1]


def outline_findings(mesh: pdx_deform.SkinnedMesh, anims: dict, posture: str = "upright", weapon_bone: str = "",
                     winged: Optional[bool] = None) -> tuple:
    """TRIPO-MAP-POSTURE, TRIPO-MAP-SPREAD, TRIPO-MAP-REACH and TRIPO-MAP-SAME for a humanoid. Returns (findings, numbers). A unit without an
    idle clip gets no reading."""

    if posture not in POSTURES:
        raise ValueError(f"posture must be one of {', '.join(POSTURES)}, not {posture!r}")
    by_role = {_role(clip): clip for clip in anims}
    if "idle" not in by_role:
        return [], {}
    view = OutlineCamera(mesh, weapon_bone)
    if winged is None:
        winged = bool(view.parts["wing"].any())
    armed = bool(view.parts["weapon"].any())
    findings: List[dict] = []
    numbers: Dict[str, object] = {"posture_asked": posture}

    stance = posture_reading(view, anims[by_role["idle"]])
    numbers["posture"] = dict(stance, limit=POSTURE_LIMIT)
    ratio = stance["ratio"]
    if posture == "hunched" and ratio > POSTURE_LIMIT:
        findings.append({"rule": "TRIPO-MAP-POSTURE", "subject": by_role["idle"], "share": ratio, "against": "rest",
                         "message": f"the job asks for a hunched idle, but from the map camera its body outline stands {ratio:.2f} of the rest pose's "
                                    f"height (a hunch is at most {POSTURE_LIMIT:.2f}, vanilla's upright soldier 0.98): it reads as an upright soldier"})
    if posture == "upright" and ratio <= POSTURE_LIMIT:
        findings.append({"rule": "TRIPO-MAP-POSTURE", "subject": by_role["idle"], "share": ratio, "against": "rest",
                         "message": f"the job asks for an upright idle, but from the map camera its body outline stands only {ratio:.2f} of the rest "
                                    f"pose's height (upright is above {POSTURE_LIMIT:.2f}): it reads hunched. Set `tripo.posture` if that is meant"})

    body_height = stance["idle_height_px"]
    spreads = {}
    for role in SPREAD_ROLES:
        clip = by_role.get(role)
        if clip is None:
            continue
        reading = spread_reading(view, anims[clip], body_height)
        if reading is None:
            continue
        value, peak_frame = reading["p90"], reading["peak_frame"]
        spreads[role] = value
        numbers.setdefault("spread", {})[clip] = reading
        if value >= SPREAD_LIMIT:
            findings.append({"rule": "TRIPO-MAP-SPREAD", "subject": clip, "share": value, "against": "idle body height", "frame": peak_frame,
                             "message": f"from the map camera the {role} spreads its hands {value:.2f} of the body's height apart, one each side of "
                                        f"the chest, in its 90th percentile frame (it must stay under {SPREAD_LIMIT:.2f}, the passed humanoids at most 0.70): "
                                        "it reads as a T-pose or a flail at map size"})

    if "attack" in spreads and "defend" in spreads and min(spreads["attack"], spreads["defend"]) >= SPREAD_LIMIT:
        findings.append({"rule": "TRIPO-MAP-SAME", "subject": by_role["defend"], "share": spreads["defend"], "against": "attack",
                         "message": f"the attack ({spreads['attack']:.2f}) and the defend ({spreads['defend']:.2f}) both hold a wide spread of the arms "
                                    "from the map camera: they read as each other at map size. Give one of them another outline"})

    attack = by_role.get("attack")
    if attack is not None:
        if winged:
            numbers["reach"] = {attack: "not judged: a winged unit's attack reads by its wings (the wing checks)"}
        else:
            reach = reach_reading(view, anims[attack], armed)
            if reach:
                numbers["reach"] = {attack: dict(reach, limit=MIN_REACH_PIXELS)}
                if reach["pixels"] < MIN_REACH_PIXELS:
                    findings.append({"rule": "TRIPO-MAP-REACH", "subject": attack, "share": reach["pixels"], "against": "body outline",
                                     "frame": reach["frame"],
                                     "message": f"at the strike (frames {reach['strike_frames'][0]} to {reach['strike_frames'][-1]}) the {reach['striking_end']} "
                                                f"show at most {reach['pixels']} pixels outside the body's outline from the map camera (at least "
                                                f"{MIN_REACH_PIXELS}, the passed weapons 9 to 29): the reach foreshortens into the body and reads as nothing"})
    return findings, numbers


def is_humanoid(mesh: pdx_deform.SkinnedMesh) -> bool:
    return _bone(mesh, "LeftHand") >= 0 and _bone(mesh, "RightHand") >= 0 and chest_bone(mesh) >= 0


__all__ = ["POSTURES", "POSTURE_LIMIT", "SPREAD_LIMIT", "MIN_REACH_PIXELS", "OutlineCamera", "outline_findings", "posture_of",
           "bone_parts", "is_humanoid"]
