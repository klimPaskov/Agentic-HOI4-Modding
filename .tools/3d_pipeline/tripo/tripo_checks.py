"""Checks that fail what a viewer fails on a Tripo unit: the weapon through the body in any frame, a hand that does not enclose
its haft, a cloak that stretches, a blade seen edge-on.

    py -3.13 .tools/3d_pipeline/tripo/tripo_checks.py <unit folder> [--gripped gripped.glb] [--weapon-bone Weapon]
        [--clips CLIP ...] [--json out.json]

The unit folder holds the runtime `.mesh` and `.anim` files. `--gripped` is the GLB the grip stage made (with the finger
bones and the clips); the weapon checks need it, and `--weapon-bone` names the weapon's bone in the unit's mesh. A unit
without a weapon gets the cloak check only. Findings (exit code 1 when there is one):

- TRIPO-SHIELD-IN-BODY and TRIPO-SHIELD-BELOW-GROUND are the same two rules for a shield held in the other hand (`--shield-bone`, or a job
  with `tripo.shield`): its points in the body, leaving out the fist's zone, and under the body's lowest point. Each part's check leaves the
  other part out of the body.
- TRIPO-WEAPON-IN-BODY and TRIPO-WEAPON-BELOW-GROUND are judged on the exported `.mesh` and `.anim` (what the game loads), every frame of each clip
  (`weapon_runtime_findings`), and TRIPO-GRIP-ENCLOSURE on the exported mesh's rest pose. The grip stage's GLB (`--gripped`) is kept as a
  diagnostic of that stage: its weapon numbers are in the report, and only its thumb check (it needs the finger bones) can fail the unit.
- TRIPO-GRIP-ENCLOSURE is advisory when the job says `tripo.weapon.grip_check: "advisory"` (or with `--grip-advisory`): it is reported under
  "advisory" and not counted as a failure, because the unit keeps Tripo's own closed hand, judged by a reviewer at the zoom players see (D-70).
  TRIPO-GRIP-THUMB is never advisory.
- Rule of the GLB version, which the runtime one repeats frame by frame: in EVERY frame of a clip (24 fps, not 24 samples), more than `MAX_IN_BODY_SHARE` of the weapon's
  points (outside the grip zone) are deeper than `PENETRATION_MARGIN_SHARE` of the height inside the body. 1% of the height
  (1.8 cm) is the lowest margin at which idle, walk and the retreat still pass (0 to 0.7% of points) while the orc's attack
  (6 to 13% from frame 28 of 24 fps, 35 of 30) and death (2 to 5% from frame 45 of 24 fps) fail, as a viewer saw them.
- TRIPO-GRIP-ENCLOSURE: skin of the hand covers less than `MIN_ENCLOSURE_SHARE` of the haft's circumference at the grip.
- TRIPO-WEAPON-HEAD-LEAD: in an attack the weapon's head trails the holding hand at the strike, so the blow lands butt first
  (`lib/tripo_swing.py`, whose grip side the grip stage's `--head-toward auto` picks).
- TRIPO-GRIP-THUMB: the thumb's tip is not on the other side of the haft than the fingertips (`MIN_THUMB_OPPOSITION_DEGREES`).
- TRIPO-CLOAK-STRETCH: in a clip, more than `CLOAK_MAX_STRETCH_SHARE` of the edges of the cloak region (vertices behind
  the body, weighted to the torso, hips or thighs) are stretched past 1.5x or squashed under 0.5x. The limit is the worst
  vanilla clothing stretch with a margin (see `CLOAK_MAX_STRETCH_SHARE`).
- TRIPO-HANDS-HIGH: in the attack, the move or the retreat of an unarmed unit a hand is above the head in more than 20% of the frames, or the hands
  are above the shoulders in more than 80% (lib/tripo_arms.py; Tripo's text-to-motion attacks do this and hide the head, and its reaching zombie walk
  reads as hands up). `--arm-level attack` in the intake fixes the attack, `--arm-level-high move retreat` a gait.
- TRIPO-LIMB-IN-TORSO: in a death clip, limb skin (arms, legs) is deeper than `LIMB_MARGIN_SHARE` of the height inside the torso in some frame, in more
  than `MAX_LIMB_IN_TORSO_SHARE` of the limb points: an arm or a leg through the body.
- TRIPO-NOT-DOWN: a death clip must end lying down, prone or supine: the body's extent at the end at most `MAX_FINAL_EXTENT_SHARE` of its
  standing height and the torso (hips to head) near horizontal (at most `MAX_TORSO_VERTICAL_SHARE` of its length vertical).
- TRIPO-LOOP-POP: the last frame of an idle, move, attack, defend or retreat clip is more than 8 degrees from its first at some joint (vanilla's role
  clips reach 6.3), so the looped clip pops. TRIPO-FOOT-BELOW-GROUND: a foot or toe sinks more than 0.1% of the height in a clip that is not a death.
  TRIPO-DEATH-FEET: in the last 15 frames of a death the boots hang more than 1% above the ground (vanilla's deaths end within 0.6%).
  TRIPO-DEATH-HOVER: the hips of a death hold themselves up for 4 frames or more, 8% or more of the height over the support they would stand on, for more than 2.12 times the time
  a free fall takes (vanilla's falls measure 1.7 at most). TRIPO-DEATH-REST: a death ends with the hips down and the chest, the head or a hand more than 10.2% of the height above the ground (vanilla's end
  within 8.2%). TRIPO-WAIST-TWIST: the shoulders turn further against the standing feet than vanilla's worst for the role with a quarter added. All are
  `lib/tripo_pose.py`, which also holds the settles that fix them (`lib/tripo_trim.settle_frames`, `settle_death_legs`, `settle_death_upper`, the
  grounding in `run_pilot`, the untwist in `tripo/prepare_tripo_unit.py`).
- TRIPO-NECK-SUNK: in some frame of a humanoid's clip the head's base sits less than 74% of its rest height above the shoulder line, in the
  chest's own frame (vanilla's worst role clip keeps 79%, a rifle shouldered). The head sinks between the shoulders with no neck. `lib/tripo_neck.py`,
  whose lift `run_pilot` applies to the staged clips.
- TRIPO-SHOULDER-SWELL: in some frame of a humanoid's clip more than 7.75% of a shoulder region's skin (the torso between the midline and the
  upper arm's joint, down to 1.5 upper arm lengths below it) has grown past 1.69 times its rest area (vanilla's worst clip 6.2%). The shoulder and
  the upper back swell into one ball. `lib/tripo_shoulder.py`, whose ease `run_pilot` applies to the staged clips.
- TRIPO-SHOULDER-TEAR: in some frame of a humanoid's clip more than 15.6% of a shoulder girdle's skin (the shoulder region and the torso under
  the arm) has grown past 1.44 times its rest area (vanilla's worst 12.5%). The raised arm tears the armpit and the side of the chest.
  `lib/tripo_shoulder.py`, with the weight rule of `lib/tripo_girdle.py`.
- TRIPO-DEATH-SPLAY: in some frame of a humanoid's death the two thighs are further apart than 47.9 degrees, or than the rest pose's own
  split plus 24.8 when the body is bound wider (vanilla's deaths split them 38.3 at most, 19.8 past its rest pose). The crotch and the raised
  thigh stretch into one mass with no knee shape. `lib/tripo_splay.py`, whose knee swing and leg closing `run_pilot` applies to the exported
  death before its settles.
- TRIPO-DEATH-LEG-KICK: once the hips of a humanoid's death are down, a boot rises more than 3.4% of the height above where it had come down
  (vanilla's deaths 2.7%): a leg kicks up from the lying body. `lib/tripo_kick.py`, whose settle `run_pilot` applies after the legs' settle.
- TRIPO-ATTACK-NO-STRIKE: in a humanoid's attack the striking hand (the weapon's, or the faster of an unarmed unit's) moves less than 0.25 of the
  height against the chest over the clip, or never faster than 1.0 heights a second (past what vanilla's shooting attacks do): the attack holds a
  pose and never strikes. `lib/tripo_strike.py`, which also reports the attack's map-size reading against the idle and the defend.
- TRIPO-MAP-READ: from the map camera at game size (the unit 60 pixels tall), a humanoid's attack or defend changes fewer pixels of the
  idle's silhouette than `map_read.MIN_HUMANOID_READ_PIXELS` (attack 300, defend 160) in its 90th percentile frame: it reads as the idle on the
  map. The limits are the lowest readings of the humanoids fresh reviewers passed at game size (`lib/map_read.py`).
- TRIPO-MAP-POSTURE, TRIPO-MAP-SPREAD, TRIPO-MAP-REACH, TRIPO-MAP-SAME: what a humanoid's clips read as from the map camera at game size, by
  their outline (`lib/map_outline.py`). The idle's body outline must match the posture the job asks for (`tripo.posture`: `hunched` at most
  0.93 of the rest pose's height, `upright` above it). The attack and the defend must not spread both hands wider than 0.80 of the body's
  height (a T-pose), nor both hold that spread (they read as each other). A melee attack's striking end (the weapon, or each hand's middle)
  must show at least 5 pixels outside the body's outline at the strike, or the reach foreshortens into the body. Not judged for a winged
  unit's reach. The limits sit between the D-94 zombie runs reviewers failed and the humanoids they passed.
- TRIPO-LOOP-STANDS: in a humanoid's move or retreat the feet stop striding in some frame step (one ankle moves against the other slower than
  0.14 heights a second, smoothed over a sixth of a second around the loop; vanilla's slowest locomotion clip keeps 0.179), or the last step does
  not flow into the first (across the seam a joint's speed against the pelvis changes by more than 1.2 times the largest change between two
  steps inside the clip, vanilla's worst 0.96).
  The game loops both clips in place, so the unit would stop and stand, or jerk, once per cycle. `lib/tripo_loop.py`, whose loop window the
  intake finds and `tripo/prepare_tripo_unit.py` cuts and closes.
- TRIPO-BLADE-FACING: in the idle pose the broad face of the weapon's head turns more than `MAX_BLADE_FACING_DEGREES` from the
  direction the unit faces (the front view shows it edge-on). A head whose thinnest spread is above `MAX_FACE_FLATNESS` of its middle one (a club, a
  mace: no broad face) is not judged, and the numbers carry its `head_flatness`.
- TRIPO-WING-STRETCH: as TRIPO-CLOAK-STRETCH, for the wing region (`lib/tripo_chains.wing_masks`), with the same limit.
- TRIPO-CHAIN-IN-BODY, TRIPO-CHAIN-GROUND: cloak or wing points that go deeper than `CHAIN_IN_BODY_MARGIN_SHARE` of the height inside the
  rest of the body (points modelled that deep at rest are left out) in more than `MAX_CHAIN_IN_BODY_SHARE` of them, or vertices more than
  `CHAIN_GROUND_MARGIN_SHARE` under the ground in more than 1% of them, in some frame. They run for a cape (`--cape`) and for wings
  (`--wings`, or a job whose anatomy has wings or whose `tripo.chains` names wings).
- TRIPO-WING-FRONT: in a clip, the wings hide more than `MAX_WING_COVER_SHARE` of the body in the front view or the map view, or more than
  `MAX_WING_SIDE_COVER` of the arms, legs and head a viewer sees in a side view (`lib/tripo_chains.front_cover_share`: a wing point in a
  screen cell of the body, nearer the camera than its surface). A death skips the front view (from a low front camera a body lying face
  down has its wings ahead of its back by construction), and the side views while the torso lies.
  A defend whose wings wrap forward (`wrap` in lib/tripo_chains.WING_ROLES) is judged in the front and map views on the head alone
  (`WRAP_COVER_PARTS`).
- TRIPO-WING-EDGE-ON: in a clip whose wings beat hard (the attack and the retreat), a wing's median face share in a side or the map view is
  under `MIN_WING_FACE_SHARE`: seen edge-on it reads as a spike.
- TRIPO-WING-IDLE-MOVE: at map size the move's wings move less than `MIN_MOVE_IDLE_MOTION_RATIO` times as much as the idle's.
- TRIPO-WING-ROOT-STRETCH: in a clip, more than `MAX_WING_ROOT_STRETCH` of the edges where the wings blend into the body stretch or squash.
- TRIPO-WING-MIRROR: a winged quadruped's two wings do not mirror each other within `MAX_WING_MIRROR_DEGREES` (every clip but the death), or
  in a beating clip one wing turns through less than `MIN_WING_BEAT_SHARE` of the other's range.
- TRIPO-PLATE-STRETCH: in a clip, more than `MAX_PLATE_STRETCH_SHARE` of the edges of an armour plate (`lib/tripo_chains.plate_masks`:
  the shoulder plates and the chest plate) are stretched or squashed. Runs for `--plates` or a job whose `tripo.chains` names plates.
- TRIPO-HAND-BLEED: more than `MAX_HAND_BLEED_SHARE` of a shape's vertices lie outside a hand's own part (`lib/stretch_smooth.hand_parts`:
  cut from the arm across the middle of the forearm) with more than `HAND_BLEED_MIN_WEIGHT` of their weight on that hand. Such skin
  rises with the hand: a fresh review of the orc saw its cloak dragged up the right flank by the axe hand. Every unit.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import map_outline, map_read, pdx_deform, pdx_motion, quadruped_checks, stretch_smooth, tripo_arms, tripo_burn, tripo_chains, tripo_checks as T, tripo_grip as G, tripo_kick, tripo_loop, tripo_neck, tripo_pose, tripo_shoulder, tripo_splay, tripo_strike, tripo_swing

# Weapon through the body (clip_check's deep share, every frame).
MAX_IN_BODY_SHARE = 0.01
PENETRATION_MARGIN_SHARE = 0.01
# The cloak: the worst share of region edges a clip stretches or squashes. Vanilla clothing (the torso and thigh vertices of the GER infantry
# mesh, Hip, back_mid and the thighs, over 16 of its clips) reaches `VANILLA_CLOAK_WORST`, 2.0%. A cloak is loose cloth and may move more
# than tailored clothing, so the limit is 2.5 times that: the orc idle (3.6%) and move (4.7%) pass, its defend (8.6%) and retreat (10%) fail.
VANILLA_CLOAK_WORST = 0.0197
CLOAK_MAX_STRETCH_SHARE = 0.05
# Tripo's skeleton names the torso Hips, Spine, Spine01, Spine02; vanilla infantry's names it Hip and back_mid. Both are listed so one rule serves both.
CLOAK_BONES = ("Hips", "Spine", "Spine01", "Spine02", "Hip", "back_mid", "LeftUpLeg", "RightUpLeg")
# Chain regions (lib/tripo_chains.py). A wing membrane is skin and stretches no more than the cloak may. Cloth and membrane inside the body
# use the weapon's rule (TRIPO-WEAPON-IN-BODY): points deeper than 1% of the height, at most 1% of them in any frame. Below the ground: the
# region's vertices more than 1% of the height under the rest pose's ground, at most 1% of them.
MAX_WING_STRETCH_SHARE = CLOAK_MAX_STRETCH_SHARE
CHAIN_IN_BODY_MARGIN_SHARE = 0.01
# Calibrated on vanilla clothing: the clothing region of the cloak calibration (vertices weighted mostly to the torso, hips or thighs, a
# quarter to 0.85 of the height) of GER_infantry over 16 of its own clips. With the inside test that also asks for a winding number above
# one half (lib/tripo_chains.deep_inside, 2026-11-15, round 3) it puts at most 4.25% of its points that deep inside the rest of its body
# (death_rifle), ENG_infantry 3.0%; the old ray-vote test read 5.0%. The limit is that worst rounded up to the next half percent. Cloth
# pressed by a moving limb sinks in; a rigid weapon does not, hence its 1%.
MAX_CHAIN_IN_BODY_SHARE = 0.045
# Wings may hide at most a twentieth of the body (all of it but the wings) in the front or map view (judgement: Tripo's own wings, bound to
# the arms, hide up to 1.2% in the demon's defend). The review cameras are blender/review_render.py's (lib/tripo_chains.REVIEW_VIEWS).
MAX_WING_COVER_SHARE = 0.05
COVER_VIEWS = {view: tripo_chains.REVIEW_VIEWS[view] for view in ("front", "map")}
# Side views (left and right) judge the arms, legs and head a viewer sees (`SIDE_PARTS`, cells whose nearest body point is one of them):
# a wing grows from the upper back, which the rig gives to the spine and the shoulder (clavicle) bones, so from the side its root always
# covers some of the back (6% of the demon's body even swept fully back), and a far arm the torso already hides is not the wing's doing.
# Calibrated on a fresh review of the round 2 demon (2026-11-15): the side views it accepted hide at most 5.3% (retreat, right view),
# those it failed for a wing over the shoulder and arm at least 17.5% (defend, left view; the attack 20.9%). The limit lies between.
MAX_WING_SIDE_COVER = 0.10
SIDE_VIEWS = {view: tripo_chains.REVIEW_VIEWS[view] for view in ("left", "right")}
SIDE_PARTS = ("Arm", "Hand", "Leg", "Foot", "Toe", "Head", "head", "neck")
# A defend whose wings wrap forward round the body (lib/tripo_chains.WING_ROLES "wrap", round g of the demon, 2026-11-21) is judged in the
# front and map views on the head alone: the wrap is meant to hide the torso and arms, and the unit still reads as itself while its head
# shows above the wings.
WRAP_COVER_PARTS = ("Head",)
# A death is judged from the side only while the torso stands (hips to head more than half vertical): wings lying flat beside a fallen
# body are in front of it from a low side camera by construction.
UPRIGHT_SHARE = 0.5
# TRIPO-WING-EDGE-ON: in a clip whose wings beat hard (flap of at least `EDGE_ON_FLAP` degrees, lib/tripo_chains.WING_ROLES: the attack and
# the retreat), each wing's silhouette in a side or the map view, as a share of its silhouette seen square-on, has a median under
# `MIN_WING_FACE_SHARE` over the clip. Calibrated on the same review: the round 2 retreat it read as a spike measured 0.26 to 0.38, the
# idle it accepted 0.47 to 0.55.
EDGE_ON_FLAP = 20.0
MIN_WING_FACE_SHARE = 0.4
# TRIPO-WING-IDLE-MOVE: at map size the move's wings must move clearly more than the idle's: the range of the wings' map-view silhouette
# over the clip, as a share of its median, at least `MIN_MOVE_IDLE_MOTION_RATIO` times the idle's. The round 2 pair the review found
# almost alike measured 1.6 (idle 0.13, move 0.21); the limit is judgement, about twice that.
MIN_MOVE_IDLE_MOTION_RATIO = 3.0
# TRIPO-WING-ROOT-STRETCH: where the wing chains blend into the body (`wing_root_zone`), at most this share of the edges may stretch or squash
# by the kit's measure in a frame. Set from the reviewed units: fresh reviews saw the round 4 demon's wing roots stretch, its worst clip 5.2%
# (the attack), and failed every clip of the Tripo dragon's run 3 where the wing meets the body (the membrane pinned to the flank, the
# creased fold beside the shoulders, the pinched wing forearm), which measured 9.2% (move) to 18.7% (defend). No reviewed clip above 5.2%
# passed. The limit lies just under the least a reviewer flagged.
MAX_WING_ROOT_STRETCH = 0.05
# A winged quadruped's beating clips (`QUADRUPED_BEATING`) are judged by TRIPO-WING-EDGE-ON as a humanoid's attack and retreat are: run 4's move
# held its half-folded wings upright, and from the map camera one of the two read as a thin spike (0.27 of its face) while the other spread,
# which both fresh reviews failed.
QUADRUPED_BEATING = ("move", "attack", "retreat")
# TRIPO-WING-MIRROR: a winged quadruped's two wings take mirrored poses in the body's frame in every clip but the death (it lies on one side).
# In the Chest bone's frame the planes of the two wings, the right one mirrored, may differ by at most `MAX_WING_MIRROR_DEGREES` in any frame
# (`wing_turns`). In a beating clip each wing must also turn through at least `MIN_WING_BEAT_SHARE` of the other's range. Calibrated on the
# Tripo dragon's run 4: its mirrored clips' planes differ by at most 5.3 degrees, and its retreat, which both fresh reviews read as one wing
# beating while the other stayed frozen upright, by 22 (the wing the retreat's turn carried forward swept back by the turn).
MAX_WING_MIRROR_DEGREES = 15.0
MIN_WING_BEAT_SHARE = 0.5
WING_MIRROR_SKIP = ("death",)
SILHOUETTE_CELL_SHARE = 0.02
# An armour plate is rigid: it may stretch no more than vanilla's tailored clothing does at its worst.
MAX_PLATE_STRETCH_SHARE = VANILLA_CLOAK_WORST
CHAIN_GROUND_MARGIN_SHARE = 0.01
MAX_CHAIN_BELOW_GROUND_SHARE = 0.01
ENCLOSURE_HALF_LENGTH_SHARE = 0.03
TORSO_BONES = ("Hips", "Spine", "Spine01", "Spine02", "neck", "Head", "Hip", "back_mid", "head")
LIMB_BONES = tuple(f"{side}{part}" for side in ("Left", "Right") for part in ("Arm", "ForeArm", "ForeArmRoll", "Hand", "UpLeg", "Leg", "Foot", "ToeBase"))
LIMB_MARGIN_SHARE = 0.015  # limb skin this deep inside the torso counts (1.5% of the height)
# Calibrated on the only two vanilla infantry death clips (GER_infantry_death_rifle and _mg, on the GER mesh): their worst frames put 5.5% and
# 2.0% of the limb points inside the torso by this measure (a low-poly mesh overstates depth: it is the distance to the nearest vertex). 1% would
# fail the vanilla deaths themselves; the limit is the worst of them with a margin of half again. The orc death measures 1.0%, the zombie 0.5 to 1.5%.
MAX_LIMB_IN_TORSO_SHARE = 0.08
MAX_FINAL_EXTENT_SHARE = 0.4
# TRIPO-HANDS-HIGH's roles: the attack, and the gaits, whose raised hands read as hands up from the front (the round 4 zombie's reaching walk)
HANDS_HIGH_ROLES = ("attack", "move", "retreat")
# A lying body is as tall as its torso is thick. The limit above holds for a human torso (the Tripo zombie's is 0.217 of its height, vanilla
# infantry's whole body 0.209 deep). A thicker body gets its extra thickness on top: the ogre's torso is 0.403 deep, and it lay flat on its front
# (torso 6% upright) at 51% of its standing height, which the fixed limit read as not lying down (2026-11-16).
HUMAN_TORSO_THICKNESS_SHARE = 0.22
TORSO_WORDS = ("hips", "pelvis", "spine", "chest")
HAND_BLEED_MIN_WEIGHT = 0.05
MAX_HAND_BLEED_SHARE = 0.002  # the orc before the rule: 1,144 of 18,375 at the axe hand
MAX_TORSO_VERTICAL_SHARE = 0.5  # the vanilla death clips end at 0.02 and 0.08
ENCLOSURE_TOLERANCE_SHARE = T.ENCLOSURE_TOLERANCE_SHARE
MIN_ENCLOSURE_SHARE = T.MIN_ENCLOSURE_SHARE
MIN_THUMB_OPPOSITION_DEGREES = T.MIN_THUMB_OPPOSITION_DEGREES
MAX_BLADE_FACING_DEGREES = T.MAX_BLADE_FACING_DEGREES
MAX_FACE_FLATNESS = T.MAX_FACE_FLATNESS


def finding(rule: str, subject: str, message: str, **numbers) -> dict:
    return {"rule": rule, "subject": subject, "message": message, **numbers}


def front_direction(mesh) -> np.ndarray:
    """The direction the unit faces (horizontal, y up): from the heels to the toes in the rest pose."""

    joints = pdx_motion.rest_joints(mesh)
    names = {name: index for index, name in enumerate(mesh.bones)}
    vectors = []
    for side in ("Left", "Right"):
        if f"{side}Foot" in names and f"{side}ToeBase" in names:
            vectors.append(joints[names[f"{side}ToeBase"]] - joints[names[f"{side}Foot"]])
    if not vectors and quadruped_checks.is_quadruped(mesh):
        # the kit's quadruped rig has hooves, not toes: it faces from its hind hooves toward its fore hooves. From its joints' middle
        # toward its head the Tripo dragon faced 21 degrees off, the curled tail and the wing chains pulling the middle aside.
        fore = np.mean([joints[names[f"Front_{side}_Hoof"]] for side in ("Left", "Right")], axis=0)
        hind = np.mean([joints[names[f"Rear_{side}_Hoof"]] for side in ("Left", "Right")], axis=0)
        vectors.append(fore - hind)
    if not vectors:
        return np.array([0.0, 0.0, 1.0])
    front = np.mean(vectors, axis=0)
    front[1] = 0.0
    return T.unit(front)


def posed_frames(mesh, anim, step: int = 1):
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    return [pdx_deform.skin(mesh, matrices[i]) for i in range(0, matrices.shape[0], step)]


def cloak_findings(mesh, anims: Dict[str, object], step: int = 2) -> (List[dict], dict):
    """TRIPO-CLOAK-STRETCH per clip. Also returns the numbers (region size and each clip's worst share)."""

    names = np.array(mesh.bones)
    dominant = pdx_deform.dominant_bones(mesh)
    dominant_names = np.where(dominant >= 0, names[np.clip(dominant, 0, None)], "")
    joints = pdx_motion.rest_joints(mesh)
    index = {name: i for i, name in enumerate(mesh.bones)}
    hips = joints[index["Hips"]] if "Hips" in index else mesh.positions.mean(axis=0)
    front = front_direction(mesh)
    height = mesh.height
    mask = T.cloak_region(mesh.positions, dominant_names, hips, front, height, cloak_bones(mesh))
    edges = pdx_deform.mesh_edges(mesh)
    out, numbers = [], {"region_vertices": int(mask.sum()), "clips": {}}
    for clip, anim in anims.items():
        share, frame = T.region_stretch_share(mesh.positions, posed_frames(mesh, anim, step), edges, mask, height)
        numbers["clips"][clip] = {"worst_share": round(share, 4), "frame": frame * step}
        if share > CLOAK_MAX_STRETCH_SHARE:
            out.append(finding("TRIPO-CLOAK-STRETCH", clip,
                               f"{share:.1%} of the cloak region's edges are stretched or squashed in frame {frame * step} ({int(mask.sum())} vertices behind the body); the limit is {CLOAK_MAX_STRETCH_SHARE:.0%}",
                               share=round(share, 4), frame=frame * step))
    return out, numbers


def cloak_bones(mesh) -> tuple:
    """The torso, hip and thigh bones, plus the cloak's own chain bones when the unit has them (lib/tripo_chains.py)."""

    return CLOAK_BONES + tuple(tripo_chains.chain_bones(mesh.bones, "cloak"))


def quadruped_wing_sides(mesh) -> Optional[tuple]:
    """(left, right) wing masks of the kit's winged quadruped rig (`adapter/quadruped_wings.py`): the vertices with at least half their weight
    on that side's `WingLeft_` or `WingRight_` chain bones. None when the mesh has no such bones."""

    names = np.array(mesh.bones)
    out = []
    for side in ("Left", "Right"):
        chain = np.char.startswith(names.astype(str), f"Wing{side}_")
        if not chain.any():
            return None
        share = np.where(mesh.joints >= 0, mesh.weights * chain[np.clip(mesh.joints, 0, None)], 0.0).sum(axis=1)
        out.append(share >= 0.5)
    return tuple(out)


def wing_sides(mesh) -> (np.ndarray, np.ndarray):
    """(left, right) wing masks by the chain stage's rule (`lib/tripo_chains.wing_masks`), or a winged quadruped's by its wing bones."""

    if quadruped_checks.is_quadruped(mesh):
        found = quadruped_wing_sides(mesh)
        if found is not None:
            return found
    names = np.array(mesh.bones)
    dominant = pdx_deform.dominant_bones(mesh)
    dominant_names = np.where(dominant >= 0, names[np.clip(dominant, 0, None)], "")
    index = {name: i for i, name in enumerate(mesh.bones)}
    hips = pdx_motion.rest_joints(mesh)[index["Hips"]] if "Hips" in index else mesh.positions.mean(axis=0)
    return tripo_chains.wing_masks(mesh.positions, dominant_names, hips, front_direction(mesh), np.array([0.0, 1.0, 0.0]))


def chain_regions(mesh, wings: bool, cloak: bool) -> Dict[str, np.ndarray]:
    """Vertex masks of the regions a chain stage moves, by the same rules that stage selects them with."""

    regions = {}
    if cloak:
        names = np.array(mesh.bones)
        dominant = pdx_deform.dominant_bones(mesh)
        dominant_names = np.where(dominant >= 0, names[np.clip(dominant, 0, None)], "")
        index = {name: i for i, name in enumerate(mesh.bones)}
        hips = pdx_motion.rest_joints(mesh)[index["Hips"]] if "Hips" in index else mesh.positions.mean(axis=0)
        front = front_direction(mesh)
        regions["cloak"] = T.cloak_region(mesh.positions, dominant_names, hips, front, mesh.height, cloak_bones(mesh))
    if wings:
        left, right = wing_sides(mesh)
        regions["wings"] = left | right
    return regions


def view_direction(front: np.ndarray, azimuth: float, elevation: float) -> np.ndarray:
    """The direction from the unit to a review camera at (azimuth, elevation) degrees, azimuth 0 in front, y up."""

    return tripo_chains.review_view(front, np.array([0.0, 1.0, 0.0]), azimuth, elevation)


def side_parts(mesh, wings: np.ndarray) -> np.ndarray:
    """The vertices the side views judge: dominated by an arm, shoulder, leg or the head (`SIDE_PARTS`), not the wings."""

    names = np.array(mesh.bones)
    dominant = names[np.clip(pdx_deform.dominant_bones(mesh), 0, None)]
    return np.array([any(part in str(name) for part in SIDE_PARTS) for name in dominant], dtype=bool) & ~wings


def upright_series(mesh, anim, step: int) -> np.ndarray:
    """Per judged frame, how vertical the torso is (hips to head, 1 upright, 0 lying); ones when the rig lacks those bones."""

    index = {name: i for i, name in enumerate(mesh.bones)}
    hips = next((index[n] for n in ("Hips", "Hip") if n in index), None)
    head = next((index[n] for n in ("Head", "head") if n in index), None)
    joints = pdx_motion.posed_joints(mesh, anim)[::step]
    if hips is None or head is None:
        return np.ones(len(joints))
    axis = joints[:, head] - joints[:, hips]
    return np.abs(axis[:, 1]) / np.maximum(np.linalg.norm(axis, axis=1), 1e-9)


# A winged quadruped's wings grow from its back, so from every review camera their roots cover some of the back, as from the side on a
# humanoid. Every view judges its legs, neck and head (`QUADRUPED_PARTS`) at the side views' limit. Its defend raises the wings as a shield
# in front of the head and neck (the role's intent, decision D-76), so the defend judges the legs alone. On the Tripo dragon, played
# offline: the shield hides 25% of the legs, neck and head from the side and none of the legs.
QUADRUPED_PARTS = ("Front_", "Rear_", "Neck_", "Head")
QUADRUPED_SHIELD_PARTS = ("Front_", "Rear_")


def quadruped_parts(mesh, wings: np.ndarray, role: str) -> np.ndarray:
    names = np.array(mesh.bones + [""])
    dominant = names[pdx_deform.dominant_bones(mesh)].astype(str)
    parts = QUADRUPED_SHIELD_PARTS if role == "defend" else QUADRUPED_PARTS
    return np.array([name.startswith(parts) for name in dominant.tolist()], dtype=bool) & ~wings


def quadruped_upright(mesh, anim, step: int) -> np.ndarray:
    """Per judged frame, how level the body stands across: one less the vertical share of the line between the two shoulders and between
    the two hips (1 standing, 0 lying on its side). A height measure read a dragon lying on its side as standing, because its legs hold
    the lying torso up a little."""

    index = {name: i for i, name in enumerate(mesh.bones)}
    joints = pdx_motion.posed_joints(mesh, anim)[::step]
    pairs = [(f"{end}_Left_Upper", f"{end}_Right_Upper") for end in ("Front", "Rear")]
    pairs = [(index[a], index[b]) for a, b in pairs if a in index and b in index]
    if not pairs:
        return np.ones(len(joints))
    shares = []
    for a, b in pairs:
        across = joints[:, a] - joints[:, b]
        shares.append(np.abs(across[:, 1]) / np.maximum(np.linalg.norm(across, axis=1), 1e-9))
    return 1.0 - np.mean(shares, axis=0)


def wing_cover(mesh, frames, wings: np.ndarray, death: bool, upright: Optional[np.ndarray] = None, role: str = "") -> Dict[str, float]:
    """The worst share of the body each review view loses behind the wings over the frames: the front and map views judge all of the body
    but the wings and the weapon, the side views the limbs and the head (`side_parts`). A death skips the front view, and the side views
    while the torso lies (`UPRIGHT_SHARE`). A winged quadruped is judged in every view on its legs, neck and head (`quadruped_parts`)."""

    if quadruped_checks.is_quadruped(mesh):
        # the whole body hides what lies behind it, the legs, neck and head are judged
        return wing_cover_points(frames, ~wings, wings, quadruped_parts(mesh, wings, role), front_direction(mesh), np.array([0.0, 1.0, 0.0]),
                                 mesh.height, death, upright, limbs_everywhere=True)
    names = np.array(mesh.bones)
    dominant = names[np.clip(pdx_deform.dominant_bones(mesh), 0, None)]
    body = ~wings & ~np.isin(dominant, ["Weapon", "Shield"])
    if float(tripo_chains.WING_ROLES.get(role, {}).get("wrap", 0.0)) > 0.0 and np.any(np.isin(dominant, WRAP_COVER_PARTS)):
        # a defend that wraps its wings forward round the body is meant to hide it: the front and map views judge the head alone
        body = np.isin(dominant, WRAP_COVER_PARTS)
    return wing_cover_points(frames, body, wings, side_parts(mesh, wings), front_direction(mesh), np.array([0.0, 1.0, 0.0]), mesh.height,
                             death, upright)


def wing_cover_points(frames, body: np.ndarray, wings: np.ndarray, limbs: np.ndarray, front: np.ndarray, up: np.ndarray, height: float,
                      death: bool, upright: Optional[np.ndarray] = None, limbs_everywhere: bool = False) -> Dict[str, float]:
    """`wing_cover` on posed points in any frame (`up` the world's up): `body` the vertices judged in the front and map views, `limbs` those
    judged in the side views (in every view with `limbs_everywhere`). `tripo/chain_replay.py` measures with it in Blender's Z-up world."""

    upright = np.ones(len(frames)) if upright is None else np.asarray(upright, float)
    out = {}
    for view, (azimuth, elevation) in {**COVER_VIEWS, **SIDE_VIEWS}.items():
        if death and view == "front":
            continue
        side = view in SIDE_VIEWS
        judged = [posed for posed, standing in zip(frames, upright) if not (death and side) or standing > UPRIGHT_SHARE]
        if not judged:
            continue
        direction = tripo_chains.review_view(front, up, azimuth, elevation)
        out[view] = round(max(tripo_chains.front_cover_share(posed, body, wings, direction, up, height, judged=limbs if side or limbs_everywhere else None) for posed in judged), 4)
    return out


def silhouette_cells(points: np.ndarray, first: np.ndarray, second: np.ndarray, cell: float) -> int:
    return len(set(map(tuple, np.floor(np.stack([points @ first, points @ second], axis=1) / cell).astype(np.int64))))


def wing_face_shares(mesh, frames, sides) -> Dict[str, float]:
    """Per side view and the map view, the lower of the two wings' median face share over the frames (`wing_face_shares_points`)."""

    return wing_face_shares_points(frames, sides, front_direction(mesh), np.array([0.0, 1.0, 0.0]), mesh.height)


def wing_face_shares_points(frames, sides, front: np.ndarray, up: np.ndarray, height: float) -> Dict[str, float]:
    """Per side view and the map view, the lower of the two wings' median face share over the frames: the screen cells
    (`SILHOUETTE_CELL_SHARE` of the height) a wing's vertices fill in that view over those they fill on the wing's own principal plane
    (1 face on, about 0.2 edge-on for a ragged membrane). Posed points in any frame, `up` the world's up."""

    cell = SILHOUETTE_CELL_SHARE * height
    out = {}
    for view in ("left", "right", "map"):
        direction = tripo_chains.review_view(front, up, *tripo_chains.REVIEW_VIEWS[view])
        first = tripo_chains.unit(np.cross(up, direction))
        second = np.cross(direction, first)
        medians = []
        for mask in sides:
            shares = []
            for posed in frames:
                points = posed[mask]
                _centre, axes, _values = T.principal_axes(points)
                shares.append(silhouette_cells(points, first, second, cell) / max(silhouette_cells(points, axes[0], axes[1], cell), 1))
            medians.append(float(np.median(shares)))
        out[view] = round(min(medians), 3)
    return out


def wing_map_motion(mesh, frames, wings: np.ndarray) -> float:
    """The range of the wings' map-view silhouette (screen cells) over the frames, as a share of its median: how much the wings move at
    map size."""

    up = np.array([0.0, 1.0, 0.0])
    direction = view_direction(front_direction(mesh), *tripo_chains.REVIEW_VIEWS["map"])
    first = tripo_chains.unit(np.cross(up, direction))
    second = np.cross(direction, first)
    cells = np.array([silhouette_cells(posed[wings], first, second, SILHOUETTE_CELL_SHARE * mesh.height) for posed in frames], float)
    return round(float(np.ptp(cells) / max(float(np.median(cells)), 1.0)), 3)


def clip_role(clip: str) -> str:
    return clip.rsplit("_", 1)[-1]


def wing_root_zone(mesh) -> np.ndarray:
    """The wings' root zone (`lib/tripo_chains.root_zone`): where the wing chains' weights blend into the body at the shoulders."""

    chain = np.isin(np.array(mesh.bones), tripo_chains.chain_bones(mesh.bones, "wings"))
    share = np.where(mesh.joints >= 0, mesh.weights * chain[np.clip(mesh.joints, 0, None)], 0.0).sum(axis=1)
    return tripo_chains.root_zone(share, pdx_deform.mesh_edges(mesh))


def chain_clip_numbers(mesh, anim, regions, body, step: int, death: bool = False, sides=None, root=None, role: str = "") -> dict:
    """One clip's worst in-body share and below-ground share per region; for the wings also the worst stretch, the worst stretch of the
    root zone (with `root`, `wing_root_zone`), the cover per review view, the face shares (with `sides`, the left and right wing masks)
    and the map-view motion."""

    frames = posed_frames(mesh, anim, step)
    edges = pdx_deform.mesh_edges(mesh)
    ground = float(mesh.positions[:, 1].min())
    out = {}
    for name, mask in regions.items():
        inside = tripo_chains.inside_share_series(frames, mesh.triangles, body, mask, mesh.height, CHAIN_IN_BODY_MARGIN_SHARE, rest=mesh.positions)
        below = tripo_chains.below_ground_series(frames, mask, ground, mesh.height, CHAIN_GROUND_MARGIN_SHARE)
        row = {"in_body_worst_share": round(max(inside), 4), "in_body_frame": int(np.argmax(inside)) * step,
               "below_ground_worst_share": round(max(below), 4), "below_ground_frame": int(np.argmax(below)) * step}
        if name == "wings":
            share, frame = T.region_stretch_share(mesh.positions, frames, edges, mask, mesh.height)
            quadruped = quadruped_checks.is_quadruped(mesh)
            upright = (quadruped_upright(mesh, anim, step) if quadruped else upright_series(mesh, anim, step)) if death else None
            row.update(stretch_worst_share=round(share, 4), stretch_frame=frame * step,
                       cover=wing_cover(mesh, frames, mask, death, upright, role),
                       map_motion=wing_map_motion(mesh, frames, mask))
            if quadruped:
                row["cover_judges"] = "legs" if role == "defend" else "legs, neck and head"
            if sides is not None:
                row["face"] = wing_face_shares(mesh, frames[::2], sides)
            if root is not None and np.any(root):
                root_share, root_frame = T.region_stretch_share(mesh.positions, frames, edges, root, mesh.height)
                row.update(root_stretch_share=round(root_share, 4), root_stretch_frame=root_frame * step)
        out[name] = row
    return out


def chain_row_findings(clip: str, name: str, row: dict) -> List[dict]:
    out = []
    if row.get("root_stretch_share", 0.0) > MAX_WING_ROOT_STRETCH:
        out.append(finding("TRIPO-WING-ROOT-STRETCH", clip, f"{row['root_stretch_share']:.1%} of the edges where the wings blend into the body stretch or squash in frame {row['root_stretch_frame']}; the limit is {MAX_WING_ROOT_STRETCH:.0%}", share=row["root_stretch_share"]))
    if row.get("stretch_worst_share", 0.0) > MAX_WING_STRETCH_SHARE:
        out.append(finding("TRIPO-WING-STRETCH", clip, f"{row['stretch_worst_share']:.1%} of the wing region's edges are stretched or squashed in frame {row['stretch_frame']}; the limit is {MAX_WING_STRETCH_SHARE:.0%}", share=row["stretch_worst_share"]))
    for view, share in (row.get("cover") or {}).items():
        side = view in SIDE_VIEWS or "cover_judges" in row
        limit = MAX_WING_SIDE_COVER if side else MAX_WING_COVER_SHARE
        if share > limit:
            what = f"the {row['cover_judges']}" if "cover_judges" in row else ("the limbs and head" if side else "the body")
            out.append(finding("TRIPO-WING-FRONT", clip, f"the wings hide {share:.1%} of {what} in the {view} view; the limit is {limit:.0%}", view=view, share=share))
    rule = tripo_chains.WING_ROLES.get(clip_role(clip), {})
    beating = clip_role(clip) in QUADRUPED_BEATING if "cover_judges" in row else rule.get("flap", 0.0) >= EDGE_ON_FLAP
    if row.get("face") and beating:
        for view, share in row["face"].items():
            if share < MIN_WING_FACE_SHARE:
                out.append(finding("TRIPO-WING-EDGE-ON", clip, f"a beating wing shows {share:.0%} of its face in the {view} view (median over the clip; limit {MIN_WING_FACE_SHARE:.0%}): seen edge-on it reads as a spike", view=view, share=share))
    if row["in_body_worst_share"] > MAX_CHAIN_IN_BODY_SHARE:
        out.append(finding("TRIPO-CHAIN-IN-BODY", clip, f"{row['in_body_worst_share']:.1%} of the {name} points go more than {CHAIN_IN_BODY_MARGIN_SHARE:.0%} of the height inside the body in frame {row['in_body_frame']} (limit {MAX_CHAIN_IN_BODY_SHARE:.1%}, vanilla clothing's worst)", region=name, share=row["in_body_worst_share"]))
    if row["below_ground_worst_share"] > MAX_CHAIN_BELOW_GROUND_SHARE:
        out.append(finding("TRIPO-CHAIN-GROUND", clip, f"{row['below_ground_worst_share']:.1%} of the {name} vertices are more than {CHAIN_GROUND_MARGIN_SHARE:.0%} of the height below the ground in frame {row['below_ground_frame']} (limit {MAX_CHAIN_BELOW_GROUND_SHARE:.0%})", region=name, share=row["below_ground_worst_share"]))
    return out


def _best_turn(rest: np.ndarray, posed: np.ndarray) -> np.ndarray:
    """The rotation that best carries the centred `rest` points onto the centred `posed` ones (Kabsch)."""

    a, b = rest - rest.mean(axis=0), posed - posed.mean(axis=0)
    u, _s, vt = np.linalg.svd(a.T @ b)
    flip = np.sign(np.linalg.det(vt.T @ u.T)) or 1.0
    return vt.T @ np.diag([1.0, 1.0, flip]) @ u.T


def _turn_degrees(r: np.ndarray) -> float:
    return float(np.degrees(np.arccos(np.clip((np.trace(r) - 1.0) / 2.0, -1.0, 1.0))))


def wing_turns(mesh, anim, sides, step: int = 2) -> Tuple[List[np.ndarray], List[np.ndarray], List[float]]:
    """Per judged frame, each wing's turn from its rest pose in the Chest bone's frame (`_best_turn`), the right wing's mirrored across the
    body's mid-plane (the mesh's X), and the angle between the two wings' planes once mirrored (degrees, their least principal axes). A
    model's two wings may be modelled at different angles (the Tripo dragon's 15 to 20 degrees apart), so their turns from rest differ by that
    much even when they pose alike: the planes are what must mirror."""

    index = {name: i for i, name in enumerate(mesh.bones)}
    chest = index.get("Chest", 0)
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    mirror = np.diag([-1.0, 1.0, 1.0])
    left, right, planes = [], [], []
    for frame in range(0, matrices.shape[0], step):
        posed = pdx_deform.skin(mesh, matrices[frame])
        inverse = np.linalg.inv(matrices[frame, chest])
        local = posed @ inverse[:3, :3].T + inverse[:3, 3]
        left.append(_best_turn(mesh.positions[sides[0]], local[sides[0]]))
        right.append(mirror @ _best_turn(mesh.positions[sides[1]], local[sides[1]]) @ mirror)
        normals = [T.principal_axes(local[mask])[1][2] for mask in sides]
        planes.append(float(np.degrees(np.arccos(min(1.0, abs(float(normals[0] @ (mirror @ normals[1]))))))))
    return left, right, planes


def wing_mirror_findings(mesh, anims: Dict[str, object], sides, step: int = 2) -> (List[dict], dict):
    """TRIPO-WING-MIRROR for a winged quadruped: its two wings' turns mirror each other within `MAX_WING_MIRROR_DEGREES`, and in a beating clip
    each turns through at least `MIN_WING_BEAT_SHARE` of the other's range."""

    out, numbers = [], {}
    for clip, anim in anims.items():
        role = clip_role(clip)
        if role in WING_MIRROR_SKIP:
            continue
        left, right, planes = wing_turns(mesh, anim, sides, step)
        worst = int(np.argmax(planes))
        mismatch = planes[worst]
        ranges = [max(_turn_degrees(turns[0].T @ turn) for turn in turns) for turns in (left, right)]
        numbers[clip] = {"mismatch_degrees": round(mismatch, 1), "frame": worst * step, "beat_degrees": [round(value, 1) for value in ranges]}
        if mismatch > MAX_WING_MIRROR_DEGREES:
            out.append(finding("TRIPO-WING-MIRROR", clip, f"the two wings' poses differ by {mismatch:.0f} degrees once mirrored in frame {worst * step} (limit {MAX_WING_MIRROR_DEGREES:.0f}): one wing does not do what the other does", degrees=round(mismatch, 1)))
        if role in QUADRUPED_BEATING and max(ranges) > 0 and min(ranges) < MIN_WING_BEAT_SHARE * max(ranges):
            out.append(finding("TRIPO-WING-MIRROR", clip, f"one wing turns through {min(ranges):.0f} degrees and the other {max(ranges):.0f} (at least {MIN_WING_BEAT_SHARE:.0%} of it): only one wing beats", degrees=[round(value, 1) for value in ranges]))
    return out, numbers


def idle_move_findings(rows: Dict[str, dict]) -> List[dict]:
    """TRIPO-WING-IDLE-MOVE: the move's wings move at map size at least `MIN_MOVE_IDLE_MOTION_RATIO` times as much as the idle's."""

    idle = next((row["wings"] for clip, row in rows.items() if clip_role(clip) == "idle" and "wings" in row), None)
    move_clip, move = next(((clip, row["wings"]) for clip, row in rows.items() if clip_role(clip) == "move" and "wings" in row), (None, None))
    if idle is None or move is None:
        return []
    ratio = move["map_motion"] / max(idle["map_motion"], 1e-3)
    if ratio < MIN_MOVE_IDLE_MOTION_RATIO:
        return [finding("TRIPO-WING-IDLE-MOVE", move_clip, f"at map size the move's wings move {ratio:.1f} times as much as the idle's (silhouette range {move['map_motion']:.0%} against {idle['map_motion']:.0%}; at least {MIN_MOVE_IDLE_MOTION_RATIO:.0f} times): idle and move look alike", ratio=round(ratio, 2))]
    return []


def chain_findings(mesh, anims: Dict[str, object], wings: bool, cloak: bool, step: int = 2) -> (List[dict], dict):
    """TRIPO-WING-STRETCH, TRIPO-WING-FRONT, TRIPO-WING-EDGE-ON, TRIPO-WING-IDLE-MOVE, TRIPO-CHAIN-IN-BODY and TRIPO-CHAIN-GROUND per clip,
    for the cloak and wing regions."""

    regions = chain_regions(mesh, wings, cloak)
    if not regions:
        return [], {}
    sides = wing_sides(mesh) if wings else None
    root = wing_root_zone(mesh) if wings else None
    weapon = np.isin(np.array(mesh.bones)[np.clip(pdx_deform.dominant_bones(mesh), 0, None)], ["Weapon"])
    body = ~np.any(np.stack(list(regions.values())), axis=0) & ~weapon
    out, numbers = [], {"region_vertices": {name: int(mask.sum()) for name, mask in regions.items()}, "clips": {}}
    for clip, anim in anims.items():
        rows = chain_clip_numbers(mesh, anim, regions, body, step, death=clip.endswith("death"), sides=sides, root=root, role=clip_role(clip))
        numbers["clips"][clip] = rows
        for name, row in rows.items():
            out += chain_row_findings(clip, name, row)
    if wings:
        out += idle_move_findings(numbers["clips"])
        if quadruped_checks.is_quadruped(mesh):
            found, numbers["mirror"] = wing_mirror_findings(mesh, anims, sides)
            out += found
    return out, numbers


def blade_findings(mesh, anims: Dict[str, object], weapon_bone: str) -> (List[dict], dict):
    if weapon_bone not in mesh.bones:
        return [], {}
    bone = mesh.bones.index(weapon_bone)
    dominant = pdx_deform.dominant_bones(mesh)
    weapon = (dominant == bone) & (mesh.weights.max(axis=1) > 0.99)
    idle = next((anim for clip, anim in anims.items() if clip.endswith("idle")), None)
    if idle is None or weapon.sum() < 50:
        return [], {}
    posed = posed_frames(mesh, idle, step=max(1, idle.frames))[0]
    joints = pdx_motion.posed_joints(mesh, idle)[0]
    hand = next((i for i, name in enumerate(mesh.bones) if name == holding_hand(mesh, weapon_bone)), None)
    hand_point = joints[hand] if hand is not None else posed[weapon].mean(axis=0)
    _head, normal, flatness = T.blade_head(posed[weapon], hand_point)
    angle, normal = T.blade_facing_degrees(posed[weapon], hand_point, front_direction(mesh))
    numbers = {"degrees": round(angle, 1), "face_normal": np.round(normal, 3).tolist(), "head_flatness": round(flatness, 3)}
    if flatness > MAX_FACE_FLATNESS:
        numbers["judged"] = False  # a near-round head has no broad face (lib/tripo_checks.MAX_FACE_FLATNESS)
        return [], numbers
    if angle > MAX_BLADE_FACING_DEGREES:
        return [finding("TRIPO-BLADE-FACING", "idle", f"the broad face of the weapon's head is {angle:.0f} degrees off the front view (limit {MAX_BLADE_FACING_DEGREES:.0f}): it shows edge-on", degrees=round(angle, 1))], numbers
    return [], numbers


def limb_torso_core(frames, triangles, torso: np.ndarray, limb: np.ndarray, height: float, margin_share: float = LIMB_MARGIN_SHARE) -> List[float]:
    """Per frame: the share of limb points (at most 400, evenly spaced) deeper than `margin_share` of the height inside the torso.

    `frames` are posed vertex positions, `torso` and `limb` vertex masks, `triangles` the mesh's (indices)."""

    import clip_check as cc

    torso_triangles = triangles[torso[triangles].all(axis=1)]
    limb_index = np.where(limb)[0]
    limb_index = limb_index[np.linspace(0, len(limb_index) - 1, min(400, len(limb_index))).astype(int)] if len(limb_index) else limb_index
    torso_index = np.where(torso)[0]
    out = []
    for posed in frames:
        points = posed[limb_index]
        lo, hi = posed[torso_index].min(axis=0), posed[torso_index].max(axis=0)
        near = np.all((points >= lo) & (points <= hi), axis=1)
        inside = np.zeros(len(points), dtype=bool)
        if near.any():
            inside[near] = cc.points_inside_mesh(points[near], posed[torso_triangles])
        deep = 0
        if inside.any():
            depth = cc.nearest_vertex_distance(points[inside], posed[torso_index]) / height
            deep = int((depth > margin_share).sum())
        out.append(deep / max(len(points), 1))
    return out


def limb_torso_series(mesh, anim, step: int = 2, margin_share: float = LIMB_MARGIN_SHARE) -> List[float]:
    names = np.array(mesh.bones)
    dominant = pdx_deform.dominant_bones(mesh)
    dominant_names = np.where(dominant >= 0, names[np.clip(dominant, 0, None)], "")
    return limb_torso_core(posed_frames(mesh, anim, step), mesh.triangles, np.isin(dominant_names, TORSO_BONES), np.isin(dominant_names, LIMB_BONES), mesh.height, margin_share)


def final_extent_share(mesh, anim) -> float:
    """The body height at the end of the clip as a share of its standing height. The selection box of a vanilla mesh is left out, and so
    are the cloak and wings a chain stage moves (vertices weighted mostly to a `Cloak` or `Wing` bone): the rule asks whether the body lies
    down, and cloth lying on its back is not the body. Vanilla meshes have no such bones, so the vanilla deaths it was set on (0.19 to
    0.23 on GER_infantry and ENG_infantry) measure as before."""

    last = pdx_deform.skin(mesh, pdx_deform.skinning_matrices(mesh, anim)[-1])
    keep = ~mesh.collision if len(mesh.collision) == len(last) else np.ones(len(last), bool)
    names = np.array(mesh.bones)
    dominant = names[np.clip(pdx_deform.dominant_bones(mesh), 0, None)]
    keep = keep & ~np.isin(dominant, tripo_chains.chain_bones(mesh.bones))
    standing = mesh.positions[keep][:, 1]
    return float(np.ptp(last[keep][:, 1]) / max(float(np.ptp(standing)), 1e-9))


def torso_thickness_share(mesh) -> float:
    """The rest torso's smaller horizontal extent (vertices weighted mostly to the hips, pelvis, spine or chest bones) as a share of the standing
    height: how tall the body is when it lies on its front or back. 0 when the mesh has no such bones."""

    names = np.array(mesh.bones)
    dominant = names[np.clip(pdx_deform.dominant_bones(mesh), 0, None)]
    torso = np.array([any(word in str(name).lower() for word in TORSO_WORDS) for name in dominant])
    if len(mesh.collision) == len(torso):
        torso &= ~mesh.collision
    if not torso.any():
        return 0.0
    points = mesh.positions[torso]
    height = max(float(np.ptp(mesh.positions[:, 1])), 1e-9)
    return float(min(np.ptp(points[:, 0]), np.ptp(points[:, 2])) / height)


def final_extent_limit(mesh) -> float:
    """`MAX_FINAL_EXTENT_SHARE`, raised by however much thicker than a human's the body's torso is."""

    return MAX_FINAL_EXTENT_SHARE + max(0.0, torso_thickness_share(mesh) - HUMAN_TORSO_THICKNESS_SHARE)


def torso_vertical_share(mesh, anim) -> float:
    """How upright the torso is at the end: the vertical part of the hips-to-head vector as a share of its length (1 upright, 0 lying)."""

    index = {name: i for i, name in enumerate(mesh.bones)}
    hips = next((index[n] for n in ("Hips", "Hip") if n in index), None)
    head = next((index[n] for n in ("Head", "head") if n in index), None)
    if hips is None or head is None:
        return 1.0
    last = pdx_motion.posed_joints(mesh, anim)[-1]
    axis = last[head] - last[hips]
    return float(abs(axis[1]) / max(float(np.linalg.norm(axis)), 1e-9))


def death_findings(mesh, anims: Dict[str, object]) -> (List[dict], dict):
    out, numbers = [], {}
    for clip, anim in anims.items():
        if not clip.endswith("death"):
            continue
        series = limb_torso_series(mesh, anim)
        extent = final_extent_share(mesh, anim)
        upright = torso_vertical_share(mesh, anim)
        worst = max(series) if series else 0.0
        limit = final_extent_limit(mesh)
        numbers[clip] = {"limb_in_torso_worst_share": round(worst, 4), "worst_frame": int(np.argmax(series)) * 2 if series else 0, "final_extent_share": round(extent, 3),
                         "final_extent_limit": round(limit, 3), "torso_vertical_share": round(upright, 2)}
        if worst > MAX_LIMB_IN_TORSO_SHARE:
            out.append(finding("TRIPO-LIMB-IN-TORSO", clip, f"{worst:.1%} of the limb points are more than {LIMB_MARGIN_SHARE:.1%} of the height inside the torso in frame {numbers[clip]['worst_frame']} (limit {MAX_LIMB_IN_TORSO_SHARE:.0%}): a limb goes through the body", share=round(worst, 4)))
        if extent > limit or upright > MAX_TORSO_VERTICAL_SHARE:
            out.append(finding("TRIPO-NOT-DOWN", clip, f"the body ends {extent:.0%} of its standing height with the torso {upright:.0%} upright (limits {limit:.0%} and {MAX_TORSO_VERTICAL_SHARE:.0%}): it does not end lying down", share=round(extent, 3), torso_vertical=round(upright, 2)))
    return out, numbers


def hands_findings(mesh, anims: Dict[str, object]) -> (List[dict], dict):
    """TRIPO-HANDS-HIGH for the attack, the move and the retreat of an unarmed unit (run only when the job names no weapon)."""

    index = {name: i for i, name in enumerate(mesh.bones)}
    needed = ("LeftHand", "RightHand", "LeftArm", "RightArm", "Head")
    if not all(name in index for name in needed):
        return [], {}
    out, numbers = [], {}
    for clip, anim in anims.items():
        if clip.rsplit("_", 1)[-1] not in HANDS_HIGH_ROLES:
            continue
        joints = pdx_motion.posed_joints(mesh, anim)
        track = {name: joints[:, index[name]] for name in needed}
        levels = tripo_arms.hand_levels(track["LeftHand"], track["RightHand"], track["LeftArm"], track["RightArm"], track["Head"])
        numbers[clip] = {k: round(v, 3) for k, v in levels.items()}
        reason = tripo_arms.hands_high(levels)
        if reason:
            out.append(finding("TRIPO-HANDS-HIGH", clip, reason, **numbers[clip]))
    return out, numbers


def weapon_in_body_findings(gripped: Path, clips: Sequence[str], weapon_joint: str) -> (List[dict], dict):
    import clip_check as cc

    result = cc.check(str(gripped), "tripo_part_0", "tripo_part_1", weapon_joint, "all", only=list(clips) or None,
                      per_frame_ground=True, margin_share=PENETRATION_MARGIN_SHARE)
    out, numbers = [], {}
    for clip, row in result["clips"].items():
        series = row["weapon_deep_in_body_pct_by_frame"]
        limit = 100 * MAX_IN_BODY_SHARE
        bad = [i for i, value in enumerate(series) if value > limit]
        numbers[clip] = {"frames": row["frames"], "worst_pct": max(series), "worst_frame": series.index(max(series)), "frames_over": len(bad)}
        if bad:
            out.append(finding("TRIPO-WEAPON-IN-BODY", clip,
                               f"the weapon is more than {PENETRATION_MARGIN_SHARE:.0%} of the height inside the body in {len(bad)} of {row['frames']} frames (24 fps frames {bad[0]} to {bad[-1]}), up to {max(series):.1f}% of its points (limit {limit:.1f}%)",
                               frames=bad[:40], worst_pct=max(series)))
    return out, numbers


def grip_findings(gripped: Path, hand: str = "mixamorig:RightHand") -> (List[dict], dict):
    import clip_check as cc

    rig = cc.Rig(str(gripped), "tripo_part_0", "tripo_part_1")
    mats = rig.skin_mats(rig.joint_worlds({}))
    body = rig.skin(rig.body, mats)
    weapon = rig.skin(rig.weapon, mats) if "joint_ids" in rig.weapon else rig.weapon["positions"]
    height = float(np.ptp(body[:, 1]))
    names = rig.joint_names
    ids, weights = rig.body["joint_ids"], rig.body["weights"]

    def share(selected):
        return sum(weights[:, k] * np.isin(ids[:, k], list(selected)) for k in range(4))

    hand_joints = {i for i, n in enumerate(names) if n.startswith(hand)}
    thumb_joints = {i for i, n in enumerate(names) if n.startswith(hand + "Thumb")}
    tip_joints = {i for i, n in enumerate(names) if n.startswith(hand) and n.rstrip("0123456789").endswith(("Index", "Middle", "Ring", "Pinky")) and n[-1] in "34"}
    skin = body[share(hand_joints) > 0.5]
    centre, axes, _values = T.principal_axes(weapon)
    palm = rig.joint_worlds({})[:, :3, 3][names.index(hand)]
    haft = axes[0]
    point = centre + float((palm - centre) @ haft) * haft
    radius = G.haft_radius(weapon, point, haft, 0.0, 0.05 * height)
    coverage = T.enclosure_share(point, haft, radius, skin, ENCLOSURE_TOLERANCE_SHARE * height, ENCLOSURE_HALF_LENGTH_SHARE * height)
    numbers = {"enclosure_share": round(coverage, 3), "haft_radius": round(radius, 4), "skin_points": int(len(skin))}
    out = []
    if coverage < MIN_ENCLOSURE_SHARE:
        out.append(finding("TRIPO-GRIP-ENCLOSURE", "grip", f"hand skin covers {coverage:.0%} of the haft's circumference at the grip (limit {MIN_ENCLOSURE_SHARE:.0%}): the fingers do not wrap it", share=round(coverage, 3)))
    thumb, tips = body[share(thumb_joints) > 0.5], body[share(tip_joints) > 0.3]
    if len(thumb) and len(tips):
        opposition = G.opposite_sides([tips.mean(axis=0)], thumb.mean(axis=0), point, haft)
        numbers["thumb_opposition_degrees"] = round(opposition, 1)
        if opposition < MIN_THUMB_OPPOSITION_DEGREES:
            out.append(finding("TRIPO-GRIP-THUMB", "grip", f"the thumb is {opposition:.0f} degrees from the fingertips round the haft (limit {MIN_THUMB_OPPOSITION_DEGREES:.0f}): it is on their side", degrees=round(opposition, 1)))
    return out, numbers


# ---- the weapon on the runtime files (what the game loads) ---------------------------------------------------------------------
#
# The weapon checks judge the exported `.mesh` and `.anim`, not the grip stage's GLB: the kit's retarget between the two drops the location
# keys of every bone but the root, so a GLB can look right where the unit does not. The judged points and the margins are the GLB check's
# own (up to `WEAPON_MAX_POINTS` evenly spaced weapon vertices, those outside the grip zone around the weapon bone's rest joint for the
# body test, all of them for the ground test; one frame per frame of the clip).

WEAPON_MAX_POINTS = 600
WEAPON_GRIP_ZONE_SHARE = 0.12
WEAPON_GROUND_TOLERANCE_SHARE = 0.02
MAX_WEAPON_BELOW_GROUND_SHARE = 0.02


def weapon_vertices(mesh, weapon_bone: str) -> np.ndarray:
    """Boolean mask of the vertices that belong to the weapon: dominated by its bone and weighted to it almost wholly."""

    bone = mesh.bones.index(weapon_bone)
    return (pdx_deform.dominant_bones(mesh) == bone) & (mesh.weights.max(axis=1) > 0.99)


def weapon_split(mesh, weapon_bone: str, other_bones: Sequence[str] = ()):
    """(the held mask, the body's triangles renumbered over the body's own vertices, the sampled weapon vertex indices, which of them are free,
    the clearance module). The held mask is the part's own vertices and those of the other held parts, and the body is every other vertex (`other_bones`: the weapon's
    check leaves the shield out of the body and the shield's check the weapon)."""

    from lib import tripo_clearance as C

    weapon = weapon_vertices(mesh, weapon_bone)
    held = weapon.copy()
    for bone in other_bones:
        if bone and bone in mesh.bones:
            held |= weapon_vertices(mesh, bone)
    body = ~held
    keep = body[mesh.triangles].all(axis=1)
    remap = np.cumsum(body) - 1
    body_triangles = remap[mesh.triangles[keep]]
    indices = np.nonzero(weapon)[0]
    indices = indices[np.linspace(0, len(indices) - 1, min(WEAPON_MAX_POINTS, len(indices))).astype(int)]
    joint = pdx_motion.rest_joints(mesh)[mesh.bones.index(weapon_bone)]
    free = np.linalg.norm(mesh.positions[indices] - joint, axis=1) > WEAPON_GRIP_ZONE_SHARE * mesh.height
    return held, body_triangles, indices, free, C


def weapon_frame_numbers(mesh, anim, weapon_bone: str, other_bones: Sequence[str] = ()) -> dict:
    """Per frame of one clip: the share of the weapon's free points deeper than the margin inside the body, the share of all its sampled points
    under the body's lowest vertex of that frame, and where its centre is (all as shares of the height)."""

    held, body_triangles, indices, free, C = weapon_split(mesh, weapon_bone, other_bones)
    height = mesh.height
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    deep, below, centres = [], [], []
    for frame in range(matrices.shape[0]):
        posed = pdx_deform.skin(mesh, matrices[frame])
        body = posed[~held]
        points = posed[indices]
        deep.append(C.deep_share(points[free], body, body_triangles, height, PENETRATION_MARGIN_SHARE))
        below.append(float((points[:, 1] < body[:, 1].min() - WEAPON_GROUND_TOLERANCE_SHARE * height).mean()))
        centres.append(points.mean(axis=0))
    return {"deep": deep, "below": below, "centres": np.array(centres) / max(height, 1e-9)}


def weapon_runtime_findings(mesh, anims: Dict[str, object], weapon_bone: str, roles: Sequence[str] = (), other_bones: Sequence[str] = (),
                            part: str = "weapon") -> (List[dict], dict):
    """TRIPO-WEAPON-IN-BODY and TRIPO-WEAPON-BELOW-GROUND per clip of the unit, measured on the runtime files.

    `roles` limits the clips to those whose name ends with one of them (default all). The numbers also say how far the weapon's centre moves
    in the last half of the clip (the largest distance from its final place, a share of the height), which a dropped weapon should not.
    `other_bones` are the other held parts, left out of the body. With `part="shield"` the same rules judge a held shield and are named
    TRIPO-SHIELD-IN-BODY and TRIPO-SHIELD-BELOW-GROUND (`shield_runtime_findings`)."""

    if weapon_bone not in mesh.bones or weapon_vertices(mesh, weapon_bone).sum() < 50:
        return [], {}
    out, numbers = [], {}
    rule = part.upper()
    for clip, anim in anims.items():
        if roles and not any(clip.endswith("_" + role) for role in roles):
            continue
        row = weapon_frame_numbers(mesh, anim, weapon_bone, other_bones)
        deep, below, centres = row["deep"], row["below"], row["centres"]
        bad = [i for i, value in enumerate(deep) if value > MAX_IN_BODY_SHARE]
        low = [i for i, value in enumerate(below) if value > MAX_WEAPON_BELOW_GROUND_SHARE]
        half = len(centres) // 2
        numbers[clip] = {
            "frames": len(deep), "worst_in_body_pct": round(100 * max(deep), 2), "worst_frame": int(np.argmax(deep)), "frames_over": len(bad),
            "worst_below_ground_pct": round(100 * max(below), 2), "frames_below_ground": len(low),
            "moved_in_last_half_share": round(float(np.linalg.norm(centres[half:] - centres[-1], axis=1).max()), 4),
        }
        if bad:
            out.append(finding(f"TRIPO-{rule}-IN-BODY", clip,
                               f"the {part} is more than {PENETRATION_MARGIN_SHARE:.0%} of the height inside the body in {len(bad)} of {len(deep)} frames of the exported clip (frames {bad[0]} to {bad[-1]}), up to {100 * max(deep):.1f}% of its points (limit {100 * MAX_IN_BODY_SHARE:.1f}%)",
                               frames=bad[:40], worst_pct=round(100 * max(deep), 2)))
        if low:
            out.append(finding(f"TRIPO-{rule}-BELOW-GROUND", clip,
                               f"more than {MAX_WEAPON_BELOW_GROUND_SHARE:.0%} of the {part}'s points are under the body's lowest point in {len(low)} of {len(below)} frames of the exported clip, up to {100 * max(below):.1f}%",
                               frames=low[:40], worst_pct=round(100 * max(below), 2)))
    return out, numbers


def shield_runtime_findings(mesh, anims: Dict[str, object], shield_bone: str, roles: Sequence[str] = (), weapon_bone: str = "") -> (List[dict], dict):
    """TRIPO-SHIELD-IN-BODY and TRIPO-SHIELD-BELOW-GROUND: the weapon's rules for a shield held in the other hand (tripo/shield_stage.py),
    on the runtime files, every frame. The judged points leave out the fist's zone round the grip, as for a weapon, and the weapon is not
    part of the body. A dropped shield's stillness is reported as `moved_in_last_half_share`."""

    return weapon_runtime_findings(mesh, anims, shield_bone, roles, (weapon_bone,), part="shield")


def holding_hand(mesh, weapon_bone: str, default: str = "RightHand") -> str:
    """The hand that holds the part: the parent of its own bone when that is a hand (the grip stage's `Weapon` bone is a child of the hand it
    closed, the left one for a left-handed unit), else `default`."""

    if weapon_bone in mesh.bones:
        parent = mesh.parents[mesh.bones.index(weapon_bone)]
        if 0 <= parent < len(mesh.bones) and mesh.bones[parent].endswith("Hand"):
            return mesh.bones[parent]
    return default


def grip_runtime_findings(mesh, weapon_bone: str, hand: str = "") -> (List[dict], dict):
    """TRIPO-GRIP-ENCLOSURE on the exported mesh's rest pose: the hand's skin (the fingers are merged into the hand bone) round the weapon's haft.

    The hand is the one that holds the weapon's bone (`holding_hand`). The thumb check needs the finger bones, which the unit no longer has: it
    stays on the grip stage's GLB. A haft the intake's reduction left with too few vertices at the grip to measure is reported unmeasured."""

    hand = hand or holding_hand(mesh, weapon_bone)
    if weapon_bone not in mesh.bones or hand not in mesh.bones or weapon_vertices(mesh, weapon_bone).sum() < 50:
        return [], {}
    weapon = mesh.positions[weapon_vertices(mesh, weapon_bone)]
    hand_bone = mesh.bones.index(hand)
    on_hand = sum(mesh.weights[:, k] * (mesh.joints[:, k] == hand_bone) for k in range(mesh.joints.shape[1]))
    skin = mesh.positions[on_hand > 0.5]
    height = mesh.height
    centre, axes, _values = T.principal_axes(weapon)
    palm = pdx_motion.rest_joints(mesh)[hand_bone]
    haft = axes[0]
    point = centre + float((palm - centre) @ haft) * haft
    try:
        radius = G.haft_radius(weapon, point, haft, 0.0, 0.05 * height)
    except ValueError as problem:
        return [], {"hand": hand, "unmeasured": str(problem)}
    coverage = T.enclosure_share(point, haft, radius, skin, ENCLOSURE_TOLERANCE_SHARE * height, ENCLOSURE_HALF_LENGTH_SHARE * height)
    numbers = {"hand": hand, "enclosure_share": round(coverage, 3), "haft_radius": round(radius, 4), "skin_points": int(len(skin))}
    if coverage < MIN_ENCLOSURE_SHARE:
        return [finding("TRIPO-GRIP-ENCLOSURE", "grip", f"hand skin covers {coverage:.0%} of the haft's circumference at the grip of the exported mesh (limit {MIN_ENCLOSURE_SHARE:.0%}): the fingers do not wrap it", share=round(coverage, 3))], numbers
    return [], numbers


def load_unit(folder: Path):
    mesh_path = sorted(folder.glob("*.mesh"))[0]
    mesh = pdx_deform.load_mesh(mesh_path)
    anims = {path.stem: pdx_deform.load_anim(path) for path in sorted(folder.glob(f"{mesh_path.stem}_*.anim"))}
    return mesh, anims


def advisory_rules(args) -> set:
    """The rules the job (or `--grip-advisory`) makes advisory: `tripo.weapon.grip_check: "advisory"` reports TRIPO-GRIP-ENCLOSURE without counting it
    as a failure (the closed hand is Tripo's own and is judged by eye at the zoom a player sees). TRIPO-GRIP-THUMB is never advisory."""

    advisory = args.grip_advisory
    if args.jobs_config and args.slug:
        job = json.loads(args.jobs_config.read_text(encoding="utf-8"))["jobs"][args.slug]
        advisory = advisory or ((job.get("tripo") or {}).get("weapon") or {}).get("grip_check") == "advisory"
    return {"TRIPO-GRIP-ENCLOSURE"} if advisory else set()


def job_lunges(args) -> bool:
    """Whether the job keeps its attack's lunge step (`tripo.lunge` names `attack`, tripo/lunge_clip.py): TRIPO-ATTACK-NO-STRIKE then measures
    an unarmed unit's hands against the ground (lib/tripo_strike.strike_numbers). False without a job."""

    if getattr(args, "jobs_config", None) and getattr(args, "slug", None):
        job = json.loads(args.jobs_config.read_text(encoding="utf-8"))["jobs"][args.slug]
        return "attack" in ((job.get("tripo") or {}).get("lunge") or {})
    return False


def shield_bone(args) -> str:
    """The shield's bone: `--shield-bone`, or the job's `tripo.shield` (its `bone`, `Shield` by default). Empty for a unit without a shield."""

    if getattr(args, "shield_bone", ""):
        return args.shield_bone
    if getattr(args, "jobs_config", None) and getattr(args, "slug", None):
        from lib.tripo_shield import SHIELD_BONE

        job = json.loads(args.jobs_config.read_text(encoding="utf-8"))["jobs"][args.slug]
        shield = (job.get("tripo") or {}).get("shield")
        if isinstance(shield, dict):
            return shield.get("bone", SHIELD_BONE)
    return ""


def split_advisory(findings: List[dict], rules: set, reported: Sequence[dict] = ()) -> (List[dict], List[dict]):
    """(the findings that fail the unit, the ones only reported, `reported` among them)."""

    return [item for item in findings if item["rule"] not in rules], [item for item in findings if item["rule"] in rules] + list(reported)


def job_posture(args) -> str:
    """The idle posture TRIPO-MAP-POSTURE judges: `--posture`, else the job's (`lib/map_outline.posture_of`: `tripo.posture`, or `hunched` for
    `"idle_pose": "hunch"`), else `upright`."""

    if getattr(args, "posture", None):
        return args.posture
    if getattr(args, "jobs_config", None) and getattr(args, "slug", None):
        return map_outline.posture_of(json.loads(args.jobs_config.read_text(encoding="utf-8"))["jobs"][args.slug])
    return "upright"


def job_regions(args) -> (bool, bool, bool):
    """(cape, wings, plates) from the flags, or from the job: `cape: true`, `anatomy.wings`, or the regions its `tripo.chains` names."""

    cape, wings, plates = args.cape, args.wings, args.plates
    if args.jobs_config and args.slug:
        job = json.loads(args.jobs_config.read_text(encoding="utf-8"))["jobs"][args.slug]
        chains = {item["region"] if isinstance(item, dict) else str(item) for item in (job.get("tripo") or {}).get("chains") or []}
        cape = cape or bool(job.get("cape")) or "cloak" in chains
        wings = wings or bool((job.get("anatomy") or {}).get("wings")) or "wings" in chains
        plates = plates or "plates" in chains
    return cape, wings, plates


def plate_findings(mesh, anims: Dict[str, object], step: int = 2) -> (List[dict], dict):
    """TRIPO-PLATE-STRETCH per clip and plate (the plates found by the same rule the chain stage binds them by)."""

    index = {name: i for i, name in enumerate(mesh.bones)}
    needed = ("Hips", "Spine01", "Spine02", "neck", "LeftArm", "RightArm", "LeftShoulder", "RightShoulder", "LeftForeArm", "RightForeArm")
    if not all(name in index for name in needed):
        return [], {"skipped": "the rig lacks the kit's shoulder, spine or neck bones"}
    joints = pdx_motion.rest_joints(mesh)
    heads = {name: joints[i] for name, i in index.items()}
    names = np.array(mesh.bones)
    dominant = names[np.clip(pdx_deform.dominant_bones(mesh), 0, None)]
    torso = np.isin(dominant, ["Hips", "Spine", "Spine01", "Spine02"])
    radius = tripo_chains.capsule_radius(mesh.positions[torso], heads["Hips"], heads["neck"])
    masks = tripo_chains.plate_masks(mesh.positions, heads, front_direction(mesh), np.array([0.0, 1.0, 0.0]), radius)
    edges = pdx_deform.mesh_edges(mesh)
    out, numbers = [], {"plate_vertices": {name: int(mask.sum()) for name, mask in masks.items()}, "clips": {}}
    for clip, anim in anims.items():
        frames = posed_frames(mesh, anim, step)
        numbers["clips"][clip] = {}
        for name, mask in masks.items():
            share, frame = T.region_stretch_share(mesh.positions, frames, edges, mask, mesh.height)
            numbers["clips"][clip][name] = round(share, 4)
            if share > MAX_PLATE_STRETCH_SHARE:
                out.append(finding("TRIPO-PLATE-STRETCH", clip, f"{share:.1%} of the {name.replace('_', ' ')}'s edges are stretched or squashed in frame {frame * step}; an armour plate may stretch no more than vanilla clothing at its worst, {MAX_PLATE_STRETCH_SHARE:.1%}", plate=name, share=round(share, 4)))
    return out, numbers


def head_lead_findings(mesh, anims: Dict[str, object], weapon_bone: str) -> (List[dict], dict):
    """TRIPO-WEAPON-HEAD-LEAD on the attack clips: around the strike (the holding hand's fastest frame) the weapon's head must lead the hand
    along its motion (`lib/tripo_swing.head_lead`), not trail it with the butt first."""

    if weapon_bone not in mesh.bones or weapon_vertices(mesh, weapon_bone).sum() < 50:
        return [], {}
    hand = holding_hand(mesh, weapon_bone)
    if hand not in mesh.bones:
        return [], {}
    weapon = weapon_vertices(mesh, weapon_bone)
    head, _axis = tripo_swing.head_end_mask(mesh.positions[weapon])
    out, numbers = [], {}
    for clip, anim in anims.items():
        if not clip.endswith("_attack"):
            continue
        matrices = pdx_deform.skinning_matrices(mesh, anim)
        joints = (matrices @ np.linalg.inv(mesh.inverse_bind)[None])[:, mesh.bones.index(hand), :3, 3]
        heads = np.array([pdx_deform.skin(mesh, matrices[frame])[weapon][head].mean(axis=0) for frame in range(anim.frames)])
        frame, cosine = tripo_swing.head_lead(joints, heads - joints)
        numbers[clip] = {"strike_frame": frame, "head_lead_cosine": round(cosine, 3)}
        if cosine < tripo_swing.HEAD_LEAD_MIN:
            out.append(finding("TRIPO-WEAPON-HEAD-LEAD", clip,
                               f"at the strike (frame {frame}, the hand's fastest) the weapon's head trails the hand (cosine {cosine:+.2f} of the hand-to-head line to the hand's motion, limit {tripo_swing.HEAD_LEAD_MIN:+.1f}): the blow lands butt first",
                               frame=frame, cosine=round(cosine, 3)))
    return out, numbers


def weapon_stage_findings(args, mesh, anims: Dict[str, object], numbers: dict) -> List[dict]:
    """The weapon and grip checks of a run: on the runtime files when the unit has a weapon bone, and the grip stage's GLB as a diagnostic.

    The GLB's numbers are kept and its weapon findings only printed (they do not fail the unit); its thumb check needs the finger bones the
    unit no longer has, so it stays a finding."""

    findings = []
    shield = shield_bone(args)
    if args.weapon_bone:
        found, numbers["weapon_runtime"] = weapon_runtime_findings(mesh, anims, args.weapon_bone, args.roles, (shield,))
        findings += found
        found, numbers["grip_runtime"] = grip_runtime_findings(mesh, args.weapon_bone)
        findings += found
        found, numbers["head_lead"] = head_lead_findings(mesh, anims, args.weapon_bone)
        findings += found
    if shield:
        found, numbers["shield_runtime"] = shield_runtime_findings(mesh, anims, shield, args.roles, args.weapon_bone)
        findings += found
    if args.gripped:
        found, numbers["weapon_in_body_glb"] = weapon_in_body_findings(args.gripped, args.clips, args.weapon_joint)
        for item in found:
            print(f"diagnostic (grip stage GLB): {item['rule']} [{item['subject']}] {item['message']}")
        found, numbers["grip_glb"] = grip_findings(args.gripped)
        findings += [item for item in found if item["rule"] == "TRIPO-GRIP-THUMB"]
    return findings


def hand_bleed_findings(mesh) -> (List[dict], dict):
    """TRIPO-HAND-BLEED per hand, on the exported mesh's rest pose."""

    if not mesh.skinned:
        return [], {}
    dense = stretch_smooth.dense_weights(mesh)
    canon = pdx_deform.weld(mesh.positions, max(mesh.height, 1e-6) * 1e-5)
    edges = pdx_deform.mesh_edges(mesh)
    out, numbers = [], {}
    for side, bled in stretch_smooth.hand_bleed(mesh, dense, canon, edges, HAND_BLEED_MIN_WEIGHT).items():
        hand = f"{side}Hand"
        shape = mesh.shape == mesh.shape[int(np.argmax(dense[:, mesh.bones.index(hand)]))]
        share = float(bled[shape].sum()) / max(int(shape.sum()), 1)
        numbers[hand] = {"vertices": int(bled.sum()), "share": round(share, 4)}
        if share > MAX_HAND_BLEED_SHARE:
            out.append(finding("TRIPO-HAND-BLEED", hand,
                               f"{int(bled.sum())} vertices outside the hand carry more than {HAND_BLEED_MIN_WEIGHT:.0%} of its weight "
                               f"({share:.2%} of the body, limit {MAX_HAND_BLEED_SHARE:.1%}): that skin rises with the hand",
                               vertices=int(bled.sum()), share=round(share, 4)))
    return out, numbers


def wing_screen_findings(mesh, anims: Dict[str, object], step: int = 2) -> (List[dict], dict):
    """TRIPO-WING-SCREEN: in a clip whose wings are spread (a role that folds them less than fully, not a death), each wing's mean direction
    from its root may rise at most `tripo_chains.SCREEN_MAX` above the screen's level in the review sheets' map view, the game's camera, on
    either side of the unit, in every judged frame. Past it a wing swung back stands up the screen as a spike (lib/tripo_chains.py says how
    the bound was measured). Wings are the vertices bound mostly to `Wing` chain bones, each side's root the first bone of its chains."""

    dominant = pdx_deform.dominant_bones(mesh)
    names = mesh.bones
    sides = {}
    for side in ("L", "R"):
        bones = [i for i, name in enumerate(names) if name.startswith(f"Wing{side}")]
        roots = [i for i in bones if mesh.parents[i] < 0 or not names[mesh.parents[i]].startswith("Wing")]
        if bones and roots:
            sides[side] = (np.isin(dominant, bones), roots)
    if len(sides) != 2:
        return [], {}
    front = front_direction(mesh)
    up = np.array([0.0, 1.0, 0.0])
    out, numbers = [], {}
    for clip, anim in anims.items():
        rule = tripo_chains.WING_ROLES.get(clip_role(clip))
        if rule is None or "fold_end" in rule or float(rule.get("fold", 0.0)) >= 1.0:
            continue
        matrices = pdx_deform.skinning_matrices(mesh, anim)
        joints = pdx_motion.posed_joints(mesh, anim)
        worst, worst_frame = 0.0, 0
        for frame in range(0, anim.frames, step):
            posed = pdx_deform.skin(mesh, matrices[frame])
            for mask, roots in sides.values():
                direction = posed[mask].mean(axis=0) - joints[frame, roots].mean(axis=0)
                angle = tripo_chains.map_screen_angle(direction, front, up)
                if angle > worst:
                    worst, worst_frame = angle, frame
        numbers[clip] = {"screen_angle_worst": round(worst, 1), "frame": worst_frame}
        if worst > tripo_chains.SCREEN_MAX:
            out.append(finding("TRIPO-WING-SCREEN", clip, f"a wing rises {worst:.0f} degrees above the screen's level in the game's camera in frame {worst_frame} (limit "
                               f"{tripo_chains.SCREEN_MAX:g}, the highest angle fresh reviews passed, 57.5, with a twentieth added): swung back it stands up as a spike at map size", degrees=round(worst, 1), frame=worst_frame))
    return out, numbers


# For a winged humanoid's attack and defend the game camera decides (D-83): their wings aim at it (lib/tripo_chains.SCREEN_ROLES), so the
# side views' cover and edge-on rules only report there. They block in the map view, and in the side views of every other clip.
SIDE_ADVISORY_RULES = ("TRIPO-WING-FRONT", "TRIPO-WING-EDGE-ON")


def side_view_advisory(findings: List[dict], mesh) -> (List[dict], List[dict]):
    """(the findings that fail the unit, the side-view wing findings of a winged humanoid's attack and defend, which only report)."""

    if quadruped_checks.is_quadruped(mesh):
        return findings, []
    keep, report = [], []
    for item in findings:
        advisory = item["rule"] in SIDE_ADVISORY_RULES and item.get("view") in SIDE_VIEWS and clip_role(item["subject"]) in tripo_chains.SCREEN_ROLES
        (report if advisory else keep).append(item)
    return keep, report


def wing_checks(mesh, anims: Dict[str, object], wings: bool, cape: bool, numbers: dict) -> (List[dict], List[dict]):
    """The chain checks and, for wings, TRIPO-WING-SCREEN: (the findings that fail the unit, the side-view ones that only report)."""

    found, numbers["chains"] = chain_findings(mesh, anims, wings, cape)
    found, advisory = side_view_advisory(found, mesh)
    if wings:
        screen, numbers["wing_screen"] = wing_screen_findings(mesh, anims)
        found += screen
    return found, advisory


def burn_split(folder: Path, mesh, anims: Dict[str, object], numbers: dict):
    """A death that burns away (lib/tripo_burn.py, its plan beside the files): (its BURN findings and clip, the clips with that death cut at
    the burn's start for every other check). The lying-body rules are dropped for it (`tripo_burn.LYING_RULES`). (None, anims) without one."""

    mesh_path = sorted(folder.glob("*.mesh"))[0]
    plan = tripo_burn.read_plan(folder, mesh_path.stem)
    if plan is None or plan.get("clip") not in anims:
        return None, anims
    clip = plan["clip"]
    found, numbers["burn"] = tripo_burn.burn_findings(mesh, anims[clip], plan, clip, tripo_burn.mesh_locators(mesh_path))
    cut = dict(anims)
    cut[clip] = tripo_burn.truncated(anims[clip], int(plan["burn_start"]) + 1)
    return {"clip": clip, "findings": found}, cut


def burn_filtered(findings: List[dict], burn: Optional[dict]) -> List[dict]:
    """The findings with a burning death's lying-body rules dropped and its BURN findings added (`burn_split`)."""

    if burn is None:
        return findings
    return [item for item in findings if not (item["subject"] == burn["clip"] and item["rule"] in tripo_burn.LYING_RULES)] + burn["findings"]


def body_findings(mesh, anims: Dict[str, object], numbers: dict, held_bones: Sequence[str] = (), posture: str = "upright",
                  weapon_bone: str = "", winged: Optional[bool] = None) -> List[dict]:
    """The checks that depend on the body: the kit's quadruped rig (a Tripo mount or beast) gets its own loop, hoof, lying-down and load
    rules (lib/quadruped_checks.py), any other body the death and pose checks and the map camera's outline rules (lib/map_outline.py, with
    the idle `posture` the job asks for); every body the hand bleed check. Fills `numbers`."""

    findings: List[dict] = []
    if quadruped_checks.is_quadruped(mesh):
        found, numbers["quadruped"] = quadruped_checks.quadruped_findings(mesh, anims)
        findings += found
    else:
        found, numbers["death"] = death_findings(mesh, anims)
        findings += found
        found, numbers["pose"] = tripo_pose.pose_findings(mesh, anims, [bone for bone in held_bones if bone in mesh.bones])
        findings += found
        found, numbers["neck"] = tripo_neck.neck_findings(mesh, anims)
        findings += found
        found, numbers["shoulders"] = tripo_shoulder.shoulder_findings(mesh, anims)
        findings += found
        found, numbers["death_splay"] = tripo_splay.splay_findings(mesh, anims)
        findings += found
        found, numbers["death_kick"] = tripo_kick.kick_findings(mesh, anims)
        findings += found
        found, numbers["gait"] = tripo_loop.loop_findings(mesh, anims)
        findings += found
        found, numbers["map_read"] = map_read.humanoid_findings(mesh, anims)
        findings += found
        found, numbers["map_alike"] = map_read.alike_findings(mesh, anims)
        findings += found
        if map_outline.is_humanoid(mesh):
            found, numbers["map_outline"] = map_outline.outline_findings(mesh, anims, posture, weapon_bone, winged)
            findings += found
    found, numbers["hand_bleed"] = hand_bleed_findings(mesh)
    return findings + found


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--gripped", type=Path, help="the grip stage's GLB, for the weapon-in-body and grip checks")
    parser.add_argument("--weapon-bone", default="", help="the weapon's bone in the unit's mesh (blade facing)")
    parser.add_argument("--weapon-joint", default="mixamorig:Weapon", help="the weapon's joint in the gripped GLB")
    parser.add_argument("--shield-bone", default="", help="the bone of a shield held in the other hand (the job's `tripo.shield` names it too)")
    parser.add_argument("--clips", nargs="*", default=[], help="clips of the gripped GLB to check for the weapon in the body (default all)")
    parser.add_argument("--roles", nargs="*", default=[], help="roles (idle, move, attack, defend, retreat, death) whose exported clips get the weapon checks (default all)")
    parser.add_argument("--grip-advisory", action="store_true", help="report TRIPO-GRIP-ENCLOSURE without failing the unit (the job's `tripo.weapon.grip_check: \"advisory\"` does the same)")
    parser.add_argument("--cape", action="store_true", help="the unit has a cloak or cape: run the cloak check (the job's `cape: true` does the same with --jobs-config and --slug)")
    parser.add_argument("--wings", action="store_true", help="the unit has wings: run the wing stretch, in-body and ground checks")
    parser.add_argument("--plates", action="store_true", help="the unit wears armour plates: run the plate stretch check")
    parser.add_argument("--posture", choices=map_outline.POSTURES, help="the idle posture TRIPO-MAP-POSTURE judges (default: the job's tripo.posture, or upright)")
    parser.add_argument("--jobs-config", type=Path)
    parser.add_argument("--slug")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    mesh, anims = load_unit(args.folder.resolve())
    findings, numbers = [], {}
    burn, anims = burn_split(args.folder.resolve(), mesh, anims, numbers)
    cape, wings, plates = job_regions(args)
    if cape:
        found, numbers["cloak"] = cloak_findings(mesh, anims)
        findings += found
    else:
        numbers["cloak"] = "not run: the job's anatomy has no cape"
    found, side_advisory = wing_checks(mesh, anims, wings, cape, numbers)
    findings += found
    if plates:
        found, numbers["plates"] = plate_findings(mesh, anims)
        findings += found
    findings += body_findings(mesh, anims, numbers, [args.weapon_bone, args.shield_bone], job_posture(args), args.weapon_bone, wings or None)
    if not args.weapon_bone and not quadruped_checks.is_quadruped(mesh):
        found, numbers["hands"] = hands_findings(mesh, anims)
        findings += found
    if not quadruped_checks.is_quadruped(mesh):
        strike_hand = holding_hand(mesh, args.weapon_bone) if args.weapon_bone and args.weapon_bone in mesh.bones else ""
        found, numbers["strike"] = tripo_strike.strike_findings(mesh, anims, strike_hand, lunge=job_lunges(args))
        findings += found
    if args.weapon_bone:
        found, numbers["blade"] = blade_findings(mesh, anims, args.weapon_bone)
        findings += found
    findings += weapon_stage_findings(args, mesh, anims, numbers)
    findings = burn_filtered(findings, burn)
    findings, advisory = split_advisory(findings, advisory_rules(args), side_advisory)
    report = {"findings": findings, "advisory": advisory, "numbers": numbers}
    if args.json:
        args.json.write_text(json.dumps(report, indent=1), encoding="utf-8", newline="\n")
    for item in findings:
        print(f"{item['rule']} [{item['subject']}] {item['message']}")
    for item in advisory:
        print(f"advisory (not a failure): {item['rule']} [{item['subject']}] {item['message']}")
    print(f"{len(findings)} finding(s), {len(advisory)} advisory")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
