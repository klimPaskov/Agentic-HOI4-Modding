"""The strike of a Tripo attack: how far and how fast the striking hand moves against the chest (TRIPO-ATTACK-NO-STRIKE).

Two fresh reviewers failed the zombie's attack (zombie_o, the text-to-motion "A zombie soldier standing upright lunges", 2026-11-18): the arms stay
locked in one forward reach for all 155 frames and only a leg steps, so at map size it reads as the defend and the idle. Two earlier runs with the
same clip were failed the same way (zombie_i, "an arms-out shamble with no strike", and zombie_k, "no clear strike"). `tripo/pose_check.py` had
picked it on its forward reach (0.31 of the height), which a held pose has as much as a blow. What a viewer misses is motion of the hand.

The measure (`strike_numbers`): per hand, its position against the chest joint (Spine02, vanilla's back_mid) in every frame, as a share of the
height. The travel is the largest distance between two of those positions over the clip (the hand's whole sweep, a wind-up to a blow); the peak
speed is the largest distance it covers in `SPEED_WINDOW` frames, in heights a second. The striking hand is the one that holds the weapon, or for
an unarmed unit the faster of the two (`striking_hand`).

Calibration (2026-11-18). Vanilla has no melee attack to measure: its infantry attacks shoot (GER_infantry on its own mesh), and its cavalry clips
are horse frames and riders idling or moving. Those shooting attacks bound what a hand does without a blow, raising, aiming and firing a gun:
travel 0.155 to 0.178 (attack_stand_rifle), 0.168 (attack_crouch_rifle), 0.227 (charge_rifle_shoot), 0.252 (charge_mg_shoot's left hand), peak
speed at most 0.98 heights a second (charge_rifle_shoot). Vanilla's idle_rifle moves a hand 0.138. A melee attack must strike further and faster
than a gun is aimed, so the limits are that worst rounded: travel `MIN_TRAVEL` 0.25 and speed `MIN_SPEED` 1.0. Against the attacks fresh
reviewers have judged, on the exported files (striking hand, travel and speed):

- Read as a blow: the ogre's poleaxe-upright attack (ogre_l, "raises the club and strikes") 0.636 and 1.59, the orc's poleaxe attack (orc_k, the
  same clip as orc_j, "the chop lands") 0.575 and 1.68. Not failed for want of a strike: the dwarf's glaive (dwarf_g) 0.552 and 2.18, the ogre's
  chop (ogre_h) 0.556 and 2.11. The zombie's "hunched zombie lurches ... swipes" (zombie_e, a swipe seen at frames 39 to 45, the clip failed
  for folding into a ball), measured on zombie_o's skin by pose_check: 0.328 and 1.15.
- Read as no strike: the zombie's lunge (zombie_o, zombie_k, zombie_i) 0.084 and 0.26 exported (0.114 and 0.44 on the route by pose_check), the
  "shambling zombie soldier ... claws" (zombie_f, "almost static") 0.119 and 0.34 by pose_check.

Every clip read as a blow is over both limits, every clip read as static under both. The lunge moves its hands against the chest less than vanilla's
rifle idle does.

The silhouette. The reviewers also say the attack and the defend read alike at map size. `lib/map_read.py` measures that from the exported files
without Blender (the share of one clip's map-camera silhouette that the other never shows, at the size a player sees), and `strike_findings`
reports it (`map_read`, against the idle and the defend), but it does not separate the clips the reviewers did: zombie_o's attack changes 0.34 of
its defend's silhouette and 0.41 of its idle's, more than the ogre_l attack that reads (0.20 and 0.28), because the lunge's step and its arms held
out change the outline while nothing in it strikes. Against the attack's own first frame the zombie reads 0.17 and the ogre 0.22. So no limit is
taken from that share. Counted in pixels at game size instead (`map_read.read_pixels`), the clips separate: TRIPO-MAP-READ
(`map_read.humanoid_findings`) holds a humanoid's attack and defend to the lowest readings of the humanoids reviewers passed, and zombie_w's
attack and defend, read as its idle by two reviewers (2026-11-18), fail it. The strike stays its own check: a clip can change its outline
with no blow.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import pdx_deform, pdx_motion

MIN_TRAVEL = 0.25
MIN_SPEED = 1.0
SPEED_WINDOW = 3  # frames: a tenth of a second at 30 a second
CHEST_BONES = ("Spine02", "back_mid", "Spine01", "Spine", "Hips", "Hip")
HANDS = ("LeftHand", "RightHand")


def chest_index(bones: Sequence[str]) -> int:
    return next((list(bones).index(name) for name in CHEST_BONES if name in bones), -1)


def hand_strike(hand: np.ndarray, chest: np.ndarray, height: float, fps: float, window: int = SPEED_WINDOW) -> Tuple[float, float]:
    """(travel, peak speed) of one hand: `hand` and `chest` are (F, 3) joint positions. Travel in shares of `height`, speed in heights a second."""

    relative = (np.asarray(hand, float) - np.asarray(chest, float)) / max(height, 1e-9)
    if len(relative) < 2:
        return 0.0, 0.0
    travel = float(np.linalg.norm(relative[:, None] - relative[None], axis=2).max())
    step = min(window, len(relative) - 1)
    speed = float((np.linalg.norm(relative[step:] - relative[:-step], axis=1) / (step / max(fps, 1e-6))).max())
    return travel, speed


def strike_numbers(joints: np.ndarray, bones: Sequence[str], height: float, fps: float, hand: str = "", lunge: bool = False) -> Optional[dict]:
    """The strike of a clip from its (F, B, 3) joint positions: per hand travel and speed, the striking hand (`hand` when given and present,
    else the faster), and whether it strikes. None without a chest bone or hands.

    `lunge`: an unarmed lunging grab whose job keeps its step (`tripo.lunge`, tripo/lunge_clip.py). Its hands are measured against the
    ground, not the chest, since the chest moves with them in a lunge: the D-94 zombie's sudden lunge with its step kept read 587 px on the
    game camera and struck 0.23 at 0.97 against the chest. The limits are the same. A held pose with no step still moves its hands as
    little against the ground as against the chest, so the zombie_o lunge reviewers read as no strike (exported in place) stays under them.
    Only that job's attack is measured this way, and two fresh reviews still judge whether it reads as a grab."""

    chest = chest_index(bones)
    present = [name for name in HANDS if name in bones]
    if chest < 0 or not present:
        return None
    ground = np.zeros_like(joints[:, chest])
    hands = {name: hand_strike(joints[:, list(bones).index(name)], ground if lunge else joints[:, chest], height, fps) for name in present}
    striking = hand if hand in hands else max(hands, key=lambda name: hands[name][1])
    travel, speed = hands[striking]
    out = {"hand": striking, "travel": round(travel, 3), "speed": round(speed, 3),
           "hands": {name: {"travel": round(t, 3), "speed": round(s, 3)} for name, (t, s) in hands.items()}}
    out["strikes"] = travel >= MIN_TRAVEL and speed >= MIN_SPEED
    out["against"] = "ground" if lunge else "chest"
    return out


def no_strike_reason(numbers: dict) -> Optional[str]:
    if numbers is None or numbers["strikes"]:
        return None
    return (f"the striking hand ({numbers['hand']}) travels {numbers['travel']:.2f} of the height against the {numbers.get('against', 'chest')} at {numbers['speed']:.2f} heights "
            f"a second at most (at least {MIN_TRAVEL} and {MIN_SPEED}, past vanilla's shooting attacks): the attack holds a pose and never strikes")


def clip_strike(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, hand: str = "", lunge: bool = False) -> Optional[dict]:
    joints = pdx_motion.posed_joints(mesh, anim)
    return strike_numbers(joints, mesh.bones, mesh.height, float(getattr(anim, "fps", 30.0) or 30.0), hand, lunge)


def strike_findings(mesh: pdx_deform.SkinnedMesh, anims: Dict[str, pdx_deform.Animation], hand: str = "", map_read_numbers: bool = True,
                    lunge: bool = False) -> Tuple[List[dict], dict]:
    """TRIPO-ATTACK-NO-STRIKE on each attack clip of a humanoid; `hand` the weapon's holding hand ("" for an unarmed unit). With
    `map_read_numbers` the attack's map-size reading against the idle and the defend is reported too (not judged, see the module text).
    `lunge` (an unarmed job whose `tripo.lunge` names the attack): the hands are measured against the ground (`strike_numbers`)."""

    out, numbers = [], {}
    by_role = {clip.rsplit("_", 1)[-1]: anim for clip, anim in anims.items()}
    for clip, anim in anims.items():
        if clip.rsplit("_", 1)[-1] != "attack":
            continue
        row = clip_strike(mesh, anim, hand, lunge and not hand)
        if row is None:
            continue
        if map_read_numbers:
            from . import map_read

            camera = map_read.MapCamera(mesh)
            frames = camera.frames(anim)
            row["map_read"] = {other: map_read.read_against_idle(camera, frames, camera.frames(by_role[other])) for other in ("idle", "defend") if other in by_role}
        numbers[clip] = row
        reason = no_strike_reason(row)
        if reason:
            out.append({"rule": "TRIPO-ATTACK-NO-STRIKE", "subject": clip, "message": reason, "hand": row["hand"], "travel": row["travel"], "speed": row["speed"]})
    return out, numbers
