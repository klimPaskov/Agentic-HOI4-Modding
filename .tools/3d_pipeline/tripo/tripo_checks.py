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
- TRIPO-WING-FLANK-HANG: in a winged quadruped's move or retreat (between the ease from and back to the folded wings), more than
  `MAX_WING_FLANK_HANG` of a wing hangs over the flank below the lowest point where it joins the body (`wing_flank_shares`).
- TRIPO-WING-SLIVER: from the game camera a winged quadruped's beating wing keeps less than `MIN_WING_SLIVER` of its flat shape.
- TRIPO-WING-HEAD-FRONT: in a clip's first frame a winged quadruped's wings stand behind more than `MAX_HEAD_FRONT_SHARE` of the head
  seen from the front.
- TRIPO-ATTACK-REACH: a winged quadruped's attack drives the head forward less than `ATTACK_REACH_MIN` of the body's length.
- TRIPO-NECK-SQUASH: a winged quadruped's head comes nearer its chest than `NECK_SQUASH_MIN` of the rest distance in some frame of a clip
  that is not the death: the neck folds into the shoulders.
- TRIPO-DEFEND-HEAD-BOXED: a winged quadruped's defend holds its head behind the front of its wings in some frame: the wings box it in.
- TRIPO-DEATH-HEAD-LOST: in some frame of its end, a winged quadruped's dead head stands clear of every other part, by a margin of `DEATH_HEAD_MARGIN` screen cells,
  for less than `DEATH_HEAD_FINDABLE` of its cells from the game camera or its mirror.
- TRIPO-WING-CRUSH: a winged quadruped's membrane has more than `MAX_WING_CRUSH` of its edges squashed or stretched in some frame.
- TRIPO-WING-THROUGH-BODY: more than `MAX_WING_BELOW_SHARE` of a winged quadruped's wing points hang below the belly in some frame.
- TRIPO-DEATH-WING-HIGH and TRIPO-DEATH-HEAD-HIDDEN: a winged quadruped's dead wing stands over the body, or its head and neck are lost
  against the rest of the body from the game camera.
- TRIPO-DEATH-WING-TENT: from the game camera a winged quadruped's dead wings stand above the lying torso's outline as a tent or a sail
  (`death_wing_tent`), however little higher than the torso they are.
- TRIPO-STEP-READ: a winged quadruped's hooves travel less than `MIN_STEP_READ` of the body's length from the game camera.
- TRIPO-ATTACK-DEFEND-ALIKE: at the attack's farthest reach and the defend's middle the smaller wing silhouette from the map camera is
  more than `MAX_ATTACK_DEFEND_WINGS` of the larger.
- TRIPO-PLATE-STRETCH: in a clip, more than `MAX_PLATE_STRETCH_SHARE` of the edges of an armour plate (`lib/tripo_chains.plate_masks`:
  the shoulder plates and the chest plate) are stretched or squashed. Runs for `--plates` or a job whose `tripo.chains` names plates.
- TRIPO-HAND-BLEED: more than `MAX_HAND_BLEED_SHARE` of a shape's vertices lie outside a hand's own part (`lib/stretch_smooth.hand_parts`:
  cut from the arm across the middle of the forearm) with more than `HAND_BLEED_MIN_WEIGHT` of their weight on that hand. Such skin
  rises with the hand: a fresh review of the orc saw its cloak dragged up the right flank by the axe hand. Every unit.
"""

from __future__ import annotations

import argparse
import json
import math
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
# TRIPO-WING-FLANK-HANG: a wing's points near the flank (within FLANK_REACH times the hooves' reach of the mid-plane) more than
# FLANK_HANG_MARGIN of the height below where the wing joins the body, in the Chest bone's frame. Offline on the Tripo dragon the round 3 poses
# that both fresh reviews of run 7 read as a crumpled skirt over the flank and the hind leg measured 0.19 (move) to 0.36 (retreat), the
# round 4 poses that carry the folded wing over the back 0.03 at most, and the rest pose none.
FLANK_REACH = 1.6
FLANK_HANG_MARGIN = 0.02
MAX_WING_FLANK_HANG = 0.1
# Round 5 lays the folded wings along the back and flanks (a fresh review of run 9 asked for them there): the check judges the open wings of
# the move and the retreat, where the skirt was seen, between the ease from and back to the folded wings.
FLANK_HANG_ROLES = ("move", "retreat")
FLANK_HANG_EASE = 0.2
# TRIPO-WING-SLIVER: from the game camera (the map view) each wing of a winged quadruped's beating clip keeps a shape: the width over the
# length of its screen points (their two principal spreads) over the same ratio of the wing laid flat, median over the clip. Run 9's move
# held one wing upright and both fresh reviews saw a thin spike from the game camera while the other spread: it measured 0.31 to 0.38 in
# the frames they named, from the camera on that wing's side (`wing_sliver`), the round 5 poses 0.86 offline. The face share (TRIPO-WING-EDGE-ON) passed it at 58%: a curled wing fills cells edge-on.
MIN_WING_SLIVER = 0.6
# TRIPO-WING-HEAD-FRONT: in the first frame of each clip (the folded pose every clip starts and ends in) the wings' front view silhouette
# covers at most MAX_HEAD_FRONT_SHARE of the head and neck's, depth aside: wings standing behind the head framed it as a box in run 9
# (both fresh reviews), at 95% of the head and neck offline, which TRIPO-WING-FRONT (wings nearer the camera than the body) measured as 0.
# Round 11 judges the head alone (the Head and Jaw skin). With the neck bones on the measured neck column (quadruped_layout.detect_neck)
# the neck is the short column at the shoulders, and from the front the folded wings stand behind it in any pose: the dragon's idle fold,
# unchanged since run 18, read 0.246 by the head and neck in run 19 against 0.059 in run 18, and by the head alone 0.068 against 0.056.
# On run 18 and run 17, rigged with the withers' neck, the head alone reads within 0.02 of the head and neck in every clip.
MAX_HEAD_FRONT_SHARE = 0.25
# TRIPO-ATTACK-REACH: a winged quadruped's attack drives the head forward at least ATTACK_REACH_MIN of the body's length (pelvis to head
# along the facing): run 9 reached 9% offline and both fresh reviews saw no strike. TRIPO-ATTACK-DEFEND-ALIKE: at the attack's farthest
# reach and the defend's middle frame, the smaller of the two wings' map view silhouettes is at most MAX_ATTACK_DEFEND_WINGS of the larger:
# run 9 opened the wings wide in both (both fresh reviews: at map size the same clip, wings open and wings close).
ATTACK_REACH_MIN = 0.15
MAX_ATTACK_DEFEND_WINGS = 0.75
# TRIPO-WING-CRUSH: in no frame of a winged quadruped's clip may more than MAX_WING_CRUSH of the membrane's edges be squashed or stretched 1.3
# times (and by 0.5% of the height) against the rest pose. Run 12's defend folded tight over the head measured 9.6% and both fresh reviews
# saw creased lumps, the poses they passed 2.9% (idle fold) to 4.5% (attack flare).
MAX_WING_CRUSH = 0.06
CRUSH_RATIO = 1.3
# TRIPO-WING-THROUGH-BODY: in no frame may more than MAX_WING_BELOW_SHARE of the wing points lie more than WING_BELOW_MARGIN of the height
# below the torso's lowest point: run 12's attack hung a finger past the belly across the forelegs to 1% of the height over the ground
# (a fresh review: major). TRIPO-CHAIN-IN-BODY already counts wing points inside the body.
WING_BELOW_MARGIN = 0.02
MAX_WING_BELOW_SHARE = 0.005
# TRIPO-DEATH-WING-HIGH: in a death's last frame no wing stands more than DEATH_WING_ABOVE of the height over where it joins the body (the
# median height of its border with the body): run 12's top wing stood 0.29 over its join as a sail over the body on its side, the round 6
# wings spread on the ground 0.17 at most (offline). Measured on the join, not the ground, since a large body's shoulders stand high. A
# wing whose join lies lower than the lying torso's middle height (the wing underneath, joined at the ground) is measured from that
# middle: the Tripo dragon's wing in the idle's fold is 0.22 of the height thick lying on the ground whichever way it is turned (offline),
# beside a torso 0.55 high, and that is a folded wing on the ground, not a sail.
# TRIPO-DEATH-HEAD-HIDDEN: in the last frame at least DEATH_HEAD_CLEAR of the head and neck's screen cells, from the game camera and from
# its mirror (the lesser of the two), are cells no other part of the body fills, in front of it or behind. Up to round 6 it read the
# head alone from straight above: 90% on run 12, where neither fresh review could find the head, which lay beside the chest and the
# forelegs. Played offline on run 14's files the new measure reads run 12's death 36%, run 14's 38% and round 7's 62%.
DEATH_WING_ABOVE = 0.2
DEATH_HEAD_CLEAR = 0.5
# TRIPO-DEATH-WING-TENT: from the game camera and its mirror, in every judged frame of a death's end (from DEATH_TENT_FROM of the clip, the
# frames both fresh reviews of run 18 judged, every other frame and the last), the wing screen cells (SILHOUETTE_CELL_SHARE of the height)
# that no other part of the body fills and that stand above the lying torso's outline (the torso's highest cell in their screen column) are
# at most DEATH_WING_TENT times the torso's own cells. Only wing points more than DEATH_TENT_GROUND of the height off the ground count, and
# only columns the torso reaches. A height measure misses a wing folded along the top of a body on its side: the run 18 dragon's stood
# 0.013 of the height over the lying torso (TRIPO-DEATH-WING-HIGH 0.03), yet from the high map camera both fresh reviews saw a tall peaked
# tent over the body. The camera looks down at 55 degrees, so ground beyond the body toward the tail shows above it on the screen: a
# folded wing lying there 0.2 of the height thick read as part of that tent. Run 18 reads 1.13 (its last frame 1.11) and run 12's death
# (its rules played on run 14's mesh) 1.61 (its last frame 0.88), both failed by fresh reviews. No reviewed death has passed yet, so the
# limit is provisional: about half the least failed last-frame reading.
DEATH_TENT_FROM = 0.52
DEATH_TENT_GROUND = 0.1
DEATH_WING_TENT = 0.45
# Round 12, after both fresh reviews of run 19 failed its death though every check passed (the tent from the game camera 0.33):
# - the same measure from the eye-level views (front, left and right) at the end, at most DEATH_WING_TENT_EYE: run 19's top wing lay
#   over the body as a mound in every eye-level view (both reviews), 0.15 to 0.17 from the sides (run 18 0.06 to 0.08, its tent was
#   from the game camera);
# - the game camera's measure while the body rolls too, from DEATH_TENT_ROLL_FROM of the clip: in run 19 one wing stood upright from
#   frame 16 to 31 (both reviews), 1.61 at frame 25.
DEATH_WING_TENT_EYE = 0.10
DEATH_TENT_ROLL_FROM = 0.3
# TRIPO-DEATH-HEAD-LOST: over the death's end (as TRIPO-DEATH-WING-TENT judges it), from the game camera and its mirror, at least DEATH_HEAD_FINDABLE of the head's screen cells
# (SILHOUETTE_CELL_SHARE of the height) lie more than DEATH_HEAD_MARGIN cells from every cell another part fills. Neither fresh review
# of run 18 or run 19 could find the head among the forelegs and the claws, while TRIPO-DEATH-HEAD-HIDDEN, which needs only cells no
# other part fills, read 0.68 and 0.67 at the last frame. This measure reads 0 and 0.22 at their worst end frames (run 19 0.41 at its
# last frame: the reviews failed frames 44 to 80). No dead head has passed a review yet: the limit is provisional.
DEATH_HEAD_MARGIN = 2
DEATH_HEAD_FINDABLE = 0.4
# TRIPO-NECK-SQUASH: in every frame of a winged quadruped's clips but the death, the distance from the middle of the head's skin to the
# middle of the Chest's skin stays at least NECK_SQUASH_MIN of its rest value. Both fresh reviews of run 19 saw the strike fold the neck
# into the shoulders (0.75 at frame 35). Run 18's strike, which one review read clearly, keeps 0.87, its defend 0.83.
NECK_SQUASH_MIN = 0.8
# TRIPO-DEFEND-HEAD-BOXED: in every frame of the defend, the middle of the head's skin lies at least DEFEND_HEAD_LEAD of the height ahead of
# the wings' front (their 99th percentile along the facing). Both fresh reviews of run 19 saw the raised wing forearms box the head in
# like a hood: it lay 0.038 behind their front (run 18 0.032 behind). The idle, whose head both reviews read clearly, keeps it 0.12 ahead.
DEFEND_HEAD_LEAD = 0.02
# TRIPO-STEP-READ: in a winged quadruped's move and retreat the hooves travel, from the game camera, at least MIN_STEP_READ of the body's
# length (each hoof's screen path against the torso's, its range, the mean over the hooves). Run 12's move measured 0.24 offline and a
# fresh review saw only the wings move.
MIN_STEP_READ = 0.3
# TRIPO-WING-MIRROR: a winged quadruped's two wings take mirrored poses in the body's frame in every clip but the death (it lies on one side).
# In the Chest bone's frame the planes of the two wings, the right one mirrored, may differ by at most `MAX_WING_MIRROR_DEGREES` in any frame
# (`wing_turns`). In a beating clip each wing must also turn through at least `MIN_WING_BEAT_SHARE` of the other's range. Calibrated on the
# Tripo dragon's run 4: its mirrored clips' planes differ by at most 5.3 degrees, and its retreat, which both fresh reviews read as one wing
# beating while the other stayed frozen upright, by 22 (the wing the retreat's turn carried forward swept back by the turn).
MAX_WING_MIRROR_DEGREES = 15.0
# TRIPO-WING-SIDE-REACH: a winged quadruped's defend and retreat hold the wings back, so in no frame may a wing reach further to its side
# than MAX_SIDE_REACH_OVER_IDLE times the most it reaches in the idle's fold. The reach is the 99th percentile of the wing points' distance
# from the torso's midline, in the Chest bone's frame (a body that turns keeps its own sides). On run 15 the idle's breath varied it by 4%,
# the defend reached 1.26 times the idle (both fresh reviews: the wings stand straight out, wider than the idle) and the retreat 1.17 (one
# review: one wing stretched out).
SIDE_REACH_ROLES = ("defend", "retreat")
MAX_SIDE_REACH_OVER_IDLE = 1.05
SIDE_REACH_PERCENTILE = 99.0
# TRIPO-HEAD-FACING: in every clip but the death the head (from its joint to its snout, the head's point furthest forward at rest) faces at
# most MAX_HEAD_FACING_TURN degrees up or down from its rest facing, read in the vertical plane of the chest's forward direction. A neck's
# turns carried a head bone turned on its own: run 15's attack turned the snout 131 degrees from its rest facing, back at the chest (both
# fresh reviews saw a hook, the throat kinked to a right angle), its defend 30 (75 below level). Its idle, move and retreat stay within 10.
MAX_HEAD_FACING_TURN = 40.0
# TRIPO-ATTACK-HEAD-LEAD: a winged quadruped's attack drops its snout on the game camera's screen (the map view's projection, `lib/map_read`)
# by at least ATTACK_SNOUT_DROP of the height from its first frame, and at that frame the snout lies below the shoulders (the Neck_01 joint
# at rest) and ahead of the fore hooves. Round 9 measures it as reviewers see it: the blows reviewers accepted, the hand of the orc's chop
# (orc_k) and of the ogre's (ogre_l), drop 0.174 and 0.236 of their height on that screen. Run 17's snout dropped 0.154 and both fresh
# reviews saw no strike, while round 8's form of the check (12% of the body's length ahead, 12.5% of the height lower, in the world) passed it.
ATTACK_SNOUT_DROP = 0.17
# TRIPO-GAME-READ: a winged quadruped's attack, defend and retreat each change at least MIN_GAME_READ of the idle's silhouette from the game
# camera (`map_read.clip_reading`, its 90th percentile frame). The units reviewers passed (orc_k, ogre_l, dwarf_f) read 0.276 to 0.445 in
# those clips, but for the ogre's defend (0.143, a guard close to its idle stance). Run 17 read 0.21 (attack) and 0.183 (defend), and
# fresh reviews read its attack as no strike and its defend as the idle (one review).
MIN_GAME_READ = 0.27
GAME_READ_ROLES = ("attack", "defend", "retreat")
# TRIPO-DEFORM-PASSED-BOUND: no clip of a winged quadruped deforms more of its edges (stretched or squashed 1.5 times and by 0.5% of the
# height, `pdx_deform`, its worst frame) than the worst clip of a unit reviewers passed: orc_k's retreat, 2.40% (its other clips 0.25% to
# 2.38%, ogre_l's at most 1.55%, dwarf_f's at most 2.05%, measured 2026-11-18). Under D-83 a change that makes a clip read at game size
# may deform more than the clip did before, as long as it stays within this bound (the kit's no-worse rule does not block it).
DEFORM_PASSED_BOUND = 0.024
# TRIPO-ATTACK-DEFEND-ALIKE is judged only when one of the two clips holds its wings larger in the map view than WINGS_OPEN_SHARE times the
# idle's fold: the check caught two wing displays (run 9), and a blow with the wings closed along the back is no display.
WINGS_OPEN_SHARE = 1.1
# TRIPO-DEATH-SIDE: a winged quadruped's death ends with the torso (the Chest bone's up axis) rolled DEATH_ROLL_RANGE degrees from upright:
# on its side, not on its belly or its back. Run 15 ended at 82 degrees.
DEATH_ROLL_RANGE = (60.0, 120.0)
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
# humanoid. Every view judges its legs, neck and head (`QUADRUPED_PARTS`) at the side views' limit, in every clip. Rounds 1 to 6 judged the
# defend's legs alone, because it raised the wings as a shield in front of the head and neck. Since round 7 the defend is a braced recoil
# with the wings mantled behind the shoulders, never in front of the head, so the head and neck are judged there too.
QUADRUPED_PARTS = ("Front_", "Rear_", "Neck_", "Head")


def quadruped_parts(mesh, wings: np.ndarray, role: str) -> np.ndarray:
    names = np.array(mesh.bones + [""])
    dominant = names[pdx_deform.dominant_bones(mesh)].astype(str)
    return np.array([name.startswith(QUADRUPED_PARTS) for name in dominant.tolist()], dtype=bool) & ~wings


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
                row["cover_judges"] = "legs, neck and head"
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
            if "cover_judges" in row and view != "map":
                continue  # a winged quadruped's wings lie level toward the game camera, so the low side cameras see them edge-on by design
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


def wing_flank_shares(mesh, anim, sides, step: int = 2) -> List[float]:
    """Per judged frame, the larger of the two wings' shares of points that hang over the flank: within `FLANK_REACH` times the hooves' reach
    from the mid-plane and more than `FLANK_HANG_MARGIN` of the height below the lowest point where that wing joins the body, in the Chest
    bone's frame (so a rear or a turn of the whole body does not count). Empty without hooves."""

    names = np.array(mesh.bones).astype(str)
    dominant = pdx_deform.dominant_bones(mesh)
    hooves = np.isin(dominant, np.flatnonzero(np.char.endswith(names, "_Hoof")))
    if not hooves.any():
        return []
    centre = float(np.median(mesh.positions[hooves, 0]))
    reach = FLANK_REACH * float(np.abs(mesh.positions[hooves, 0] - centre).mean())
    height = max(mesh.height, 1e-6)
    joins = []
    for mask in sides:
        tm = mask[mesh.triangles]
        border = np.zeros(len(mask), bool)
        border[mesh.triangles[tm.any(1) & ~tm.all(1)].ravel()] = True
        joins.append(float(mesh.positions[border & mask, 1].min()) if (border & mask).any() else -np.inf)
    chest = {name: i for i, name in enumerate(mesh.bones)}.get("Chest", 0)
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    out = []
    for frame in range(0, matrices.shape[0], step):
        posed = pdx_deform.skin(mesh, matrices[frame])
        inverse = np.linalg.inv(matrices[frame, chest])
        local = posed @ inverse[:3, :3].T + inverse[:3, 3]
        near = np.abs(local[:, 0] - centre) < reach
        out.append(max(float((mask & near & (local[:, 1] < join - FLANK_HANG_MARGIN * height)).sum()) / max(int(mask.sum()), 1)
                       for mask, join in zip(sides, joins)))
    return out


def wing_flank_findings(mesh, anims: Dict[str, object], sides, step: int = 2) -> (List[dict], dict):
    """TRIPO-WING-FLANK-HANG for a winged quadruped (`wing_flank_shares`) in the move and the retreat, the clips' first and last
    `FLANK_HANG_EASE` left out (they ease from and back to the folded wings, which lie along the flanks)."""

    out, numbers = [], {}
    for clip, anim in anims.items():
        if clip_role(clip) not in FLANK_HANG_ROLES:
            continue
        shares = wing_flank_shares(mesh, anim, sides, step)
        if not shares:
            continue
        ease = int(round(FLANK_HANG_EASE * len(shares)))
        shares = [0.0] * ease + shares[ease : len(shares) - ease] + [0.0] * ease
        worst = int(np.argmax(shares))
        numbers[clip] = {"share": round(shares[worst], 4), "frame": worst * step}
        if shares[worst] > MAX_WING_FLANK_HANG:
            out.append(finding("TRIPO-WING-FLANK-HANG", clip, f"{shares[worst]:.0%} of a wing hangs over the flank below where it joins the body in frame {worst * step} (limit {MAX_WING_FLANK_HANG:.0%}): the inner membrane reads as a skirt pulled down to the body and the hind leg", share=round(shares[worst], 4), frame=worst * step))
    return out, numbers


def _view_axes(mesh, view: str) -> Tuple[np.ndarray, np.ndarray]:
    up = np.array([0.0, 1.0, 0.0])
    direction = view_direction(front_direction(mesh), *tripo_chains.REVIEW_VIEWS[view])
    first = tripo_chains.unit(np.cross(up, direction))
    return first, np.cross(direction, first)


def _aspect(points: np.ndarray) -> float:
    spread = np.linalg.svd(points - points.mean(axis=0), compute_uv=False)
    return float(spread[1] / max(float(spread[0]), 1e-9))


def _cells(points: np.ndarray, axes: Tuple[np.ndarray, np.ndarray], cell: float) -> set:
    return set(map(tuple, np.floor(np.stack([points @ axes[0], points @ axes[1]], axis=1) / cell).astype(np.int64)))


def _parts(mesh, wings: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    names = np.array(mesh.bones).astype(str)
    dominant = pdx_deform.dominant_bones(mesh)
    named = np.where(dominant >= 0, names[np.clip(dominant, 0, None)], "")
    head = (np.char.startswith(named, "Head") | np.char.startswith(named, "Jaw")) & ~wings
    head_neck = (head | np.char.startswith(named, "Neck")) & ~wings
    return head, head_neck, np.isin(named, ["Pelvis", "Spine", "Chest"]) | head_neck


def _dilate(cells: set, steps: int) -> set:
    out = set(cells)
    for _ in range(steps):
        out |= {(x + dx, y + dy) for x, y in out for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    return out


def head_findable(mesh, posed: np.ndarray, head: np.ndarray) -> float:
    """TRIPO-DEATH-HEAD-LOST's measure in one frame: the least share, from the game camera and its mirror, of the head's screen cells that
    lie more than DEATH_HEAD_MARGIN cells from every cell another part fills."""

    cell = SILHOUETTE_CELL_SHARE * mesh.height
    least = 1.0
    for axes in game_cameras(mesh):
        seen = _cells(posed[head], axes, cell)
        near = _dilate(_cells(posed[~head], axes, cell), DEATH_HEAD_MARGIN)
        least = min(least, len(seen - near) / max(len(seen), 1))
    return least


def neck_squash(mesh, matrices, head: np.ndarray, chest: np.ndarray) -> Tuple[float, int]:
    """TRIPO-NECK-SQUASH's measure: the least distance over the clip from the middle of the head's skin to the middle of the Chest's,
    over its rest value, and its frame."""

    rest = float(np.linalg.norm(mesh.positions[head].mean(axis=0) - mesh.positions[chest].mean(axis=0)))
    gaps = [float(np.linalg.norm((posed := pdx_deform.skin(mesh, frame))[head].mean(axis=0) - posed[chest].mean(axis=0))) / max(rest, 1e-9) for frame in matrices]
    return min(gaps), int(np.argmin(gaps))


def head_lead_over_wings(mesh, matrices, head: np.ndarray, wings: np.ndarray, front: np.ndarray) -> Tuple[float, int]:
    """TRIPO-DEFEND-HEAD-BOXED's measure: the least lead over the clip of the middle of the head's skin over the wings' front (their 99th
    percentile along the facing), as a share of the height, and its frame."""

    leads = []
    for frame in matrices:
        posed = pdx_deform.skin(mesh, frame)
        leads.append(float(np.median(posed[head] @ front) - np.percentile(posed[wings] @ front, 99)) / mesh.height)
    return min(leads), int(np.argmin(leads))


def head_front_region(head: np.ndarray, head_neck: np.ndarray) -> np.ndarray:
    """The skin TRIPO-WING-HEAD-FRONT judges: the head alone (MAX_HEAD_FRONT_SHARE says why), or the head and neck when no skin is the
    head's."""

    return head if head.any() else head_neck


def head_front_share(mesh, matrices, wings: np.ndarray, head_neck: np.ndarray) -> float:
    """TRIPO-WING-HEAD-FRONT's share in the first frame: the front view cells of `head` (the head's skin) the wings' silhouette also fills."""

    posed = pdx_deform.skin(mesh, matrices[0])
    axes, cell = _view_axes(mesh, "front"), SILHOUETTE_CELL_SHARE * mesh.height
    seen = _cells(posed[head_neck], axes, cell)
    return len(seen & _cells(posed[wings], axes, cell)) / max(len(seen), 1)


def wing_sliver(mesh, matrices, sides, flat: List[float]) -> float:
    """TRIPO-WING-SLIVER's measure: the median over the clip of the thinner wing's width over length from the game camera, over its flat
    shape's. The game camera is judged from both sides (the map view's azimuth and its mirror), since a camera off the unit's axis sees one
    of two mirrored upright wings edge-on: run 9's right wing measured 0.31 from one side and 0.61 from the other."""

    azimuth, elevation = tripo_chains.REVIEW_VIEWS["map"]
    cameras = []
    for side in (1.0, -1.0):
        up = np.array([0.0, 1.0, 0.0])
        direction = view_direction(front_direction(mesh), side * azimuth, elevation)
        first = tripo_chains.unit(np.cross(up, direction))
        cameras.append((first, np.cross(direction, first)))
    ratios = []
    for frame in range(0, matrices.shape[0], 2):
        posed = pdx_deform.skin(mesh, matrices[frame])
        ratios.append(min(_aspect(np.stack([posed[mask] @ a, posed[mask] @ b], axis=1)) / max(rest, 1e-9)
                          for mask, rest in zip(sides, flat) for a, b in cameras))
    return float(np.median(ratios))


def wing_edges(mesh, wings: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    t = mesh.triangles
    edges = np.unique(np.sort(np.concatenate([t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]]), axis=1), axis=0)
    edges = edges[wings[edges[:, 0]] & wings[edges[:, 1]]]
    return edges, np.linalg.norm(mesh.positions[edges[:, 0]] - mesh.positions[edges[:, 1]], axis=1)


def wing_body_numbers(mesh, matrices, wings: np.ndarray, torso: np.ndarray, edges, rest) -> Tuple[float, int, float, int]:
    """TRIPO-WING-CRUSH's and TRIPO-WING-THROUGH-BODY's worst shares over a clip, with their frames."""

    height = max(mesh.height, 1e-6)
    crush, crush_frame, below, below_frame = 0.0, 0, 0.0, 0
    for frame in range(0, matrices.shape[0], 2):
        posed = pdx_deform.skin(mesh, matrices[frame])
        length = np.linalg.norm(posed[edges[:, 0]] - posed[edges[:, 1]], axis=1)
        share = float((((length > CRUSH_RATIO * rest) | (length < rest / CRUSH_RATIO)) & (np.abs(length - rest) > 0.005 * height)).mean()) if len(rest) else 0.0
        if share > crush:
            crush, crush_frame = share, frame
        low = float((posed[wings, 1] < posed[torso, 1].min() - WING_BELOW_MARGIN * height).mean()) if torso.any() else 0.0
        if low > below:
            below, below_frame = low, frame
    return crush, crush_frame, below, below_frame


def game_cameras(mesh) -> List[Tuple[np.ndarray, np.ndarray]]:
    """The screen axes of the game camera (the map view) and of its mirror: a unit on the map is seen from either side of its heading."""

    azimuth, elevation = tripo_chains.REVIEW_VIEWS["map"]
    up = np.array([0.0, 1.0, 0.0])
    cameras = []
    for side in (1.0, -1.0):
        direction = view_direction(front_direction(mesh), side * azimuth, elevation)
        first = tripo_chains.unit(np.cross(up, direction))
        cameras.append((first, np.cross(direction, first)))
    return cameras


def death_end_numbers(mesh, matrices, sides, head: np.ndarray, head_neck: np.ndarray, torso: Optional[np.ndarray] = None) -> Tuple[float, float]:
    """TRIPO-DEATH-WING-HIGH's and TRIPO-DEATH-HEAD-HIDDEN's numbers in a death's last frame: the most a wing stands over where it joins
    the body (or over the lying torso's middle height, when its join lies lower: `torso`), and the least share of the head and neck's
    screen cells, from the game camera and its mirror, that no other part of the body fills."""

    posed = pdx_deform.skin(mesh, matrices[-1])
    above = 0.0
    middle = float(np.median(posed[torso, 1])) if torso is not None and torso.any() else -np.inf
    for mask in sides:
        tm = mask[mesh.triangles]
        border = np.zeros(len(mask), bool)
        border[mesh.triangles[tm.any(1) & ~tm.all(1)].ravel()] = True
        if (border & mask).any():
            above = max(above, float(posed[mask, 1].max() - max(float(np.median(posed[border & mask, 1])), middle)) / max(mesh.height, 1e-6))
    cell = 2.0 * SILHOUETTE_CELL_SHARE * mesh.height
    clear = 1.0
    for axes in game_cameras(mesh):
        seen = _cells(posed[head_neck], axes, cell)
        clear = min(clear, len(seen - _cells(posed[~head_neck], axes, cell)) / max(len(seen), 1))
    return above, clear


def wing_tent_share(points: np.ndarray, wings: np.ndarray, torso: np.ndarray, axes: Tuple[np.ndarray, np.ndarray], cell: float, height: float) -> float:
    """TRIPO-DEATH-WING-TENT's measure in one frame from one camera: the cells of wing points raised more than DEATH_TENT_GROUND of the
    `height` off the ground that no other part fills and that stand above the torso's highest cell in their screen column, over the torso's
    cell count. Columns the torso does not reach are left out: a wing lying beyond the back lies beside the body on the screen, not over it."""

    torso_cells = _cells(points[torso], axes, cell)
    if not torso_cells:
        return 0.0
    top: Dict[int, int] = {}
    for x, y in torso_cells:
        top[x] = max(top.get(x, y), y)
    raised = wings & (points[:, 1] - float(points[:, 1].min()) > DEATH_TENT_GROUND * height)
    free = _cells(points[raised], axes, cell) - _cells(points[~wings], axes, cell)
    return sum(1 for x, y in free if x in top and y > top[x]) / len(torso_cells)


def death_wing_tent(mesh, matrices, wings: np.ndarray, torso: np.ndarray, start: float = DEATH_TENT_FROM, end: float = 1.0,
                    cameras=None) -> Tuple[float, int]:
    """TRIPO-DEATH-WING-TENT's measure: the worst `wing_tent_share` over the death's frames from `start` to `end` of the clip (every other
    frame and the last of them) and `cameras` (the game camera and its mirror unless given), and its frame."""

    cell = SILHOUETTE_CELL_SHARE * mesh.height
    cameras = game_cameras(mesh) if cameras is None else cameras
    last = min(matrices.shape[0] - 1, int(round(end * (matrices.shape[0] - 1))))
    worst, worst_frame = 0.0, last
    frames = list(range(int(start * (matrices.shape[0] - 1)), last + 1, 2))
    if frames[-1] != last:
        frames.append(last)
    for frame in frames:
        posed = pdx_deform.skin(mesh, matrices[frame])
        for axes in cameras:
            share = wing_tent_share(posed, wings, torso, axes, cell, mesh.height)
            if share > worst:
                worst, worst_frame = share, frame
    return worst, worst_frame


def step_read(mesh, matrices, hooves: np.ndarray, torso: np.ndarray, length: float) -> float:
    """TRIPO-STEP-READ's measure: the hooves' screen travel from the game camera against the torso's, over the body's length."""

    axes = _view_axes(mesh, "map")
    paths = []
    for frame in range(0, matrices.shape[0], 2):
        posed = pdx_deform.skin(mesh, matrices[frame])
        feet = np.stack([posed[hooves] @ axes[0], posed[hooves] @ axes[1]], axis=1)
        body = np.stack([posed[torso] @ axes[0], posed[torso] @ axes[1]], axis=1)
        paths.append(feet - body.mean(axis=0))
    return float(np.linalg.norm(np.ptp(np.stack(paths), axis=0), axis=1).mean()) / length


def _winged_clip_findings(mesh, clip: str, anim, c: dict) -> Tuple[List[dict], dict, Optional[int]]:
    """One clip's part of `quadruped_view_findings`: its findings, its numbers and, for the attack and the defend, the wings' map view
    cells at the attack's farthest reach or the defend's middle."""

    out, row, peak = [], {}, None
    role = clip_role(clip)
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    crush, crush_frame, below, below_frame = wing_body_numbers(mesh, matrices, c["wings"], c["torso"], c["edges"], c["rest"])
    row.update(crush=round(crush, 4), crush_frame=crush_frame, below=round(below, 4), below_frame=below_frame)
    if crush > MAX_WING_CRUSH:
        out.append(finding("TRIPO-WING-CRUSH", clip, f"{crush:.1%} of the membrane's edges are squashed or stretched {CRUSH_RATIO:g} times in frame {crush_frame} (limit {MAX_WING_CRUSH:.0%}, the poses reviewers passed 2.9% to 4.5%): the wing crumples", share=round(crush, 4), frame=crush_frame))
    if below > MAX_WING_BELOW_SHARE and role != "death":  # a lying body's wings rest on the ground, below its raised belly
        out.append(finding("TRIPO-WING-THROUGH-BODY", clip, f"{below:.1%} of the wing points hang more than {WING_BELOW_MARGIN:.0%} of the height below the belly in frame {below_frame} (limit {MAX_WING_BELOW_SHARE:.1%}): a finger drops through the legs", share=round(below, 4), frame=below_frame))
    if role == "death" and c["head"].any() and c["torso"].any():
        out += _death_end_findings(mesh, clip, matrices, c, row)
    if role in ("move", "retreat") and c["hooves"].any() and c["torso"].any():
        steps = step_read(mesh, matrices, c["hooves"], c["torso"], c["length"])
        row["step_read"] = round(steps, 3)
        if steps < MIN_STEP_READ:
            out.append(finding("TRIPO-STEP-READ", clip, f"from the game camera the hooves travel {steps:.0%} of the body's length (at least {MIN_STEP_READ:.0%}): only the wings read as moving", share=round(steps, 3)))
    if role != "death" and c["head"].any() and c["chest_skin"].any():
        squash, squash_frame = neck_squash(mesh, matrices, c["head"], c["chest_skin"])
        row.update(neck_gap=round(squash, 3), neck_gap_frame=squash_frame)
        if squash < NECK_SQUASH_MIN:
            out.append(finding("TRIPO-NECK-SQUASH", clip, f"in frame {squash_frame} the head comes within {squash:.0%} of its rest distance from the chest (at least {NECK_SQUASH_MIN:.0%}): the neck folds into the shoulders", share=round(squash, 3), frame=squash_frame))
    if role == "defend" and c["head"].any():
        lead, lead_frame = head_lead_over_wings(mesh, matrices, c["head"], c["wings"], c["front"])
        row.update(head_lead=round(lead, 3), head_lead_frame=lead_frame)
        if lead < DEFEND_HEAD_LEAD:
            out.append(finding("TRIPO-DEFEND-HEAD-BOXED", clip, f"in frame {lead_frame} the head lies {lead:.1%} of the height ahead of the wings' front (at least {DEFEND_HEAD_LEAD:.0%}): the wings box it in", share=round(lead, 3), frame=lead_frame))
    if role != "death" and c["head_neck"].any():
        share = head_front_share(mesh, matrices, c["wings"], head_front_region(c["head"], c["head_neck"]))
        row["head_front_share"] = round(share, 3)
        if share > MAX_HEAD_FRONT_SHARE:
            out.append(finding("TRIPO-WING-HEAD-FRONT", clip, f"in the first frame the wings stand behind {share:.0%} of the head seen from the front (limit {MAX_HEAD_FRONT_SHARE:.0%}): they frame the head as a screen", share=round(share, 3)))
    if role in QUADRUPED_BEATING:
        sliver = wing_sliver(mesh, matrices, c["sides"], c["flat"])
        row["sliver"] = round(sliver, 3)
        if sliver < MIN_WING_SLIVER:
            out.append(finding("TRIPO-WING-SLIVER", clip, f"from the game camera a wing keeps {sliver:.0%} of its flat shape's width over length (median over the clip; at least {MIN_WING_SLIVER:.0%}): it reads as a thin spike", share=round(sliver, 3)))
    if role in ("attack", "defend") and c["head"].any():
        out_reach, peak = _attack_reach(mesh, clip, role, matrices, c, row)
        out += out_reach
    out += _held_pose_findings(mesh, clip, role, matrices, c, row)
    return out, row, peak


def _held_pose_findings(mesh, clip: str, role: str, matrices, c: dict, row: dict) -> List[dict]:
    """TRIPO-HEAD-FACING, TRIPO-ATTACK-HEAD-LEAD and TRIPO-DEATH-SIDE for one clip, and its wings' side reach for TRIPO-WING-SIDE-REACH."""

    out: List[dict] = []
    if c.get("chest") is None:
        return out
    row["side_reach"] = [round(value, 4) for value in side_reach(mesh, matrices, c["sides"], c["torso"], c["chest"], c["front"])]
    if role != "death" and c.get("head_bone") is not None:
        turn, frame = head_facing_turn(mesh, matrices, c["head_bone"], c["snout"], c["chest"], c["front"])
        row.update(head_facing_turn=round(turn, 1), head_facing_frame=frame)
        if turn > MAX_HEAD_FACING_TURN:
            out.append(finding("TRIPO-HEAD-FACING", clip, f"in frame {frame} the head faces {turn:.0f} degrees off its rest facing (at most {MAX_HEAD_FACING_TURN:.0f}): the neck carries the head round into a hook or straight down", degrees=round(turn, 1), frame=frame))
    if role == "attack" and c.get("head_bone") is not None:
        out += _snout_lead(mesh, clip, matrices, c, row)
    if role == "death":
        roll = torso_roll(matrices[-1], c["chest"])
        row["end_roll"] = round(roll, 1)
        low, high = DEATH_ROLL_RANGE
        if not low <= roll <= high:
            out.append(finding("TRIPO-DEATH-SIDE", clip, f"the dead torso ends rolled {roll:.0f} degrees from upright ({low:.0f} to {high:.0f}): it does not lie on its side", degrees=round(roll, 1)))
    return out


def side_reach(mesh, matrices, sides, torso: np.ndarray, chest: int, front: np.ndarray) -> List[float]:
    """TRIPO-WING-SIDE-REACH's measure per wing: the most, over the clip, of the wing points' 99th percentile distance to their own side
    of the torso's midline, in the Chest bone's rest frame (the posed points taken back through the chest's turn)."""

    up = np.array([0.0, 1.0, 0.0])
    across = tripo_chains.unit(np.cross(up, front))
    middle = float(np.median(mesh.positions[torso] @ across)) if torso.any() else 0.0
    signs = [1.0 if float(np.median(mesh.positions[mask] @ across)) > middle else -1.0 for mask in sides]
    best = [0.0 for _ in sides]
    for frame in range(matrices.shape[0]):
        posed = pdx_deform.skin(mesh, matrices[frame])
        turn, shift = matrices[frame][chest][:3, :3], matrices[frame][chest][:3, 3]
        local = (posed - shift) @ turn  # each row R^T (p - t): back through the chest's turn
        for index, mask in enumerate(sides):
            if mask.any():
                reach = float(np.percentile(signs[index] * (local[mask] @ across - middle), SIDE_REACH_PERCENTILE))
                best[index] = max(best[index], reach)
    return best


def head_facing_turn(mesh, matrices, head_bone: int, snout: int, chest: int, front: np.ndarray) -> Tuple[float, int]:
    """TRIPO-HEAD-FACING's measure: the most the head's facing (its joint to its snout, carried by the Head bone) turns from its rest facing
    over the clip, in degrees within the vertical plane of the chest's forward direction, and the frame."""

    up = np.array([0.0, 1.0, 0.0])
    joint = np.linalg.inv(mesh.inverse_bind[head_bone])[:3, 3]
    rest_facing = mesh.positions[snout] - joint

    def below(direction: np.ndarray, forward: np.ndarray) -> float:
        ahead = forward - (forward @ up) * up
        ahead = ahead / max(float(np.linalg.norm(ahead)), 1e-9)
        return math.degrees(math.atan2(-float(direction @ up), float(direction @ ahead)))

    rest = below(rest_facing, front)
    worst, worst_frame = 0.0, 0
    for frame in range(matrices.shape[0]):
        facing = matrices[frame][head_bone][:3, :3] @ rest_facing
        forward = matrices[frame][chest][:3, :3] @ front
        turn = abs((below(facing, forward) - rest + 180.0) % 360.0 - 180.0)
        if turn > worst:
            worst, worst_frame = turn, frame
    return worst, worst_frame


def torso_roll(matrix_frame: np.ndarray, chest: int) -> float:
    """Degrees the Chest bone's up axis lies from the vertical (0 upright, 90 on its side, 180 on its back)."""

    up = np.array([0.0, 1.0, 0.0])
    carried = matrix_frame[chest][:3, :3] @ up
    return math.degrees(math.acos(max(-1.0, min(1.0, float(carried @ up) / max(float(np.linalg.norm(carried)), 1e-9)))))


def _snout_lead(mesh, clip: str, matrices, c: dict, row: dict) -> List[dict]:
    """TRIPO-ATTACK-HEAD-LEAD: the snout's largest drop on the game camera's screen from its first frame, and where it lies at that frame
    against the shoulders and the fore hooves."""

    snout = c["snout"]
    right, up = map_read.map_axes(c["front"])
    start = pdx_deform.skin(mesh, matrices[0])[snout]
    drop, best = -np.inf, 0
    for frame in range(matrices.shape[0]):
        point = pdx_deform.skin(mesh, matrices[frame])[snout]
        value = float((start - point) @ up) / mesh.height
        if value > drop:
            drop, best = value, frame
    posed = pdx_deform.skin(mesh, matrices[best])
    ground = float(mesh.positions[:, 1].min())
    below = float(c["shoulder"] - posed[snout][1]) / mesh.height if c.get("shoulder") is not None else 0.0
    ahead = float(posed[snout] @ c["front"] - (posed[c["fore_hooves"]] @ c["front"]).max()) / mesh.height if c["fore_hooves"].any() else 0.0
    row.update(snout_screen_drop=round(drop, 3), snout_frame=best, snout_below_shoulders=round(below, 3), snout_ahead_of_forefeet=round(ahead, 3),
               snout_height=round(float(posed[snout][1] - ground) / mesh.height, 3))
    if drop < ATTACK_SNOUT_DROP or below <= 0 or ahead <= 0:
        return [finding("TRIPO-ATTACK-HEAD-LEAD", clip, f"at its lowest on the game camera's screen (frame {best}) the snout has dropped {drop:.0%} of the height (at least {ATTACK_SNOUT_DROP:.0%}, the orc's and the ogre's blows 17% and 24%), lies {below:+.0%} below the shoulders and {ahead:+.0%} ahead of the forefeet (both must be above 0): the head does not drive the strike forward and down", drop=round(drop, 3), below=round(below, 3), ahead=round(ahead, 3), frame=best)]
    return []


def _death_end_findings(mesh, clip: str, matrices, c: dict, row: dict) -> List[dict]:
    out = []
    above, clear = death_end_numbers(mesh, matrices, c["sides"], c["head"], c["head_neck"], c["torso"])
    row.update(wing_above_join=round(above, 4), head_clear=round(clear, 3))
    if above > DEATH_WING_ABOVE:
        out.append(finding("TRIPO-DEATH-WING-HIGH", clip, f"at the end a wing stands {above:.0%} of the height over where it joins the body (limit {DEATH_WING_ABOVE:.0%}): it reads as a sail, not a wing lying flat", share=round(above, 4)))
    if clear < DEATH_HEAD_CLEAR:
        out.append(finding("TRIPO-DEATH-HEAD-HIDDEN", clip, f"at the end {clear:.0%} of the head and neck shows clear of the body, legs, wings and tail from the game camera (at least {DEATH_HEAD_CLEAR:.0%}): the head is lost in the heap", share=round(clear, 3)))
    tent, frame = death_wing_tent(mesh, matrices, c["wings"], c["torso"])
    row.update(wing_tent=round(tent, 3), wing_tent_frame=frame)
    if tent > DEATH_WING_TENT:
        out.append(finding("TRIPO-DEATH-WING-TENT", clip, f"in frame {frame} the wings fill {tent:.2f} times the lying torso's screen cells above its outline from the game camera (at most {DEATH_WING_TENT:.2f}): they stand over the dead body as a tent or a sail", share=round(tent, 3), frame=frame))
    roll, roll_frame = death_wing_tent(mesh, matrices, c["wings"], c["torso"], DEATH_TENT_ROLL_FROM, DEATH_TENT_FROM)
    row.update(wing_tent_roll=round(roll, 3), wing_tent_roll_frame=roll_frame)
    if roll > DEATH_WING_TENT:
        out.append(finding("TRIPO-DEATH-WING-TENT", clip, f"while the body rolls (frame {roll_frame}) the wings fill {roll:.2f} times the torso's screen cells above its outline from the game camera (at most {DEATH_WING_TENT:.2f}): a wing stands up as the body falls", share=round(roll, 3), frame=roll_frame))
    eye = {view: death_wing_tent(mesh, matrices, c["wings"], c["torso"], cameras=[_view_axes(mesh, view)]) for view in ("front", "left", "right")}
    row["wing_tent_eye"] = {view: round(value, 3) for view, (value, _frame) in eye.items()}
    for view, (value, eye_frame) in eye.items():
        if value > DEATH_WING_TENT_EYE:
            out.append(finding("TRIPO-DEATH-WING-TENT", clip, f"in frame {eye_frame} from the {view} view the wings fill {value:.2f} times the lying torso's cells above its outline (at most {DEATH_WING_TENT_EYE:.2f}): a wing lies over the dead body as a mound", share=round(value, 3), frame=eye_frame, view=view))
    if c["head"].any():
        end_frames = sorted(set(range(int(DEATH_TENT_FROM * (matrices.shape[0] - 1)), matrices.shape[0], 2)) | {matrices.shape[0] - 1})
        shares = [head_findable(mesh, pdx_deform.skin(mesh, matrices[frame]), c["head"]) for frame in end_frames]
        findable, lost_frame = min(shares), end_frames[int(np.argmin(shares))]
        row.update(head_findable=round(findable, 3), head_findable_frame=lost_frame)
        if findable < DEATH_HEAD_FINDABLE:
            out.append(finding("TRIPO-DEATH-HEAD-LOST", clip, f"in frame {lost_frame} only {findable:.0%} of the head stands clear of every other part from the game camera (at least {DEATH_HEAD_FINDABLE:.0%}, by {DEATH_HEAD_MARGIN} cells): it is lost among the legs and the wings", share=round(findable, 3)))
    return out


def _attack_reach(mesh, clip: str, role: str, matrices, c: dict, row: dict) -> Tuple[List[dict], int]:
    head, front, length = c["head"], c["front"], c["length"]
    reach = [float((pdx_deform.skin(mesh, matrices[f])[head] @ front).mean() - (mesh.positions[head] @ front).mean()) / length for f in range(matrices.shape[0])]
    best = int(np.argmax(reach)) if role == "attack" else matrices.shape[0] // 2
    peak = len(_cells(pdx_deform.skin(mesh, matrices[best])[c["wings"]], _view_axes(mesh, "map"), c["cell"]))
    out = []
    if role == "attack":
        row["head_reach"], row["reach_frame"] = round(reach[best], 3), best
        if reach[best] < ATTACK_REACH_MIN:
            out.append(finding("TRIPO-ATTACK-REACH", clip, f"the head drives forward {reach[best]:.0%} of the body's length at most (frame {best}; at least {ATTACK_REACH_MIN:.0%}): the attack does not strike", share=round(reach[best], 3)))
    return out, peak


def quadruped_view_findings(mesh, anims: Dict[str, object], sides) -> (List[dict], dict):
    """TRIPO-WING-SLIVER, TRIPO-WING-HEAD-FRONT, TRIPO-ATTACK-REACH, TRIPO-ATTACK-DEFEND-ALIKE, TRIPO-WING-CRUSH, TRIPO-WING-THROUGH-BODY,
    TRIPO-DEATH-WING-HIGH, TRIPO-DEATH-HEAD-HIDDEN, TRIPO-DEATH-WING-TENT, TRIPO-STEP-READ, TRIPO-WING-SIDE-REACH, TRIPO-HEAD-FACING, TRIPO-ATTACK-HEAD-LEAD and
    TRIPO-DEATH-SIDE for a winged quadruped."""

    out, numbers = [], {}
    wings = sides[0] | sides[1]
    head, head_neck, trunk = _parts(mesh, wings)
    front = front_direction(mesh)
    length = max(float(np.ptp(mesh.positions[trunk] @ front)), 1e-6) if trunk.any() else 1.0
    cell = SILHOUETTE_CELL_SHARE * mesh.height
    flat = []
    for mask in sides:
        _centre, axes, _values = T.principal_axes(mesh.positions[mask])
        flat.append(_aspect(np.stack([mesh.positions[mask] @ axes[0], mesh.positions[mask] @ axes[1]], axis=1)))
    peaks = {}
    edges, rest = wing_edges(mesh, wings)
    names = np.array(mesh.bones).astype(str)
    named = names[np.clip(pdx_deform.dominant_bones(mesh), 0, None)]
    torso_only = np.isin(named, ["Pelvis", "Spine", "Chest"]) & ~wings
    hooves = np.char.endswith(named, "_Hoof")
    chest = mesh.bones.index("Chest") if "Chest" in mesh.bones else None
    head_bone = mesh.bones.index("Head") if "Head" in mesh.bones and head.any() else None
    snout = int(np.flatnonzero(head)[np.argmax(mesh.positions[head] @ front)]) if head_bone is not None else None
    shoulder = float(np.linalg.inv(mesh.inverse_bind[mesh.bones.index("Neck_01")])[1, 3]) if "Neck_01" in mesh.bones else None
    fore_hooves = np.isin(named, ["Front_Left_Hoof", "Front_Right_Hoof"])
    context = dict(all_edges=pdx_deform.mesh_edges(mesh), wings=wings, head=head, head_neck=head_neck, front=front, length=length, cell=cell, flat=flat, edges=edges, rest=rest,
                   torso=torso_only, hooves=hooves, sides=sides, chest=chest, head_bone=head_bone, snout=snout, shoulder=shoulder,
                   fore_hooves=fore_hooves, chest_skin=(named == "Chest") & ~wings)
    for clip, anim in anims.items():
        found, row, peak = _winged_clip_findings(mesh, clip, anim, context)
        out += found
        numbers[clip] = row
        if peak is not None:
            peaks[clip_role(clip)] = peak
    out += _pair_findings(mesh, anims, numbers, peaks, context)
    return out, numbers


def _pair_findings(mesh, anims: Dict[str, object], numbers: dict, peaks: Dict[str, int], c: dict) -> List[dict]:
    """The findings that compare a winged quadruped's clips: TRIPO-WING-SIDE-REACH and TRIPO-GAME-READ against the idle, TRIPO-ATTACK-
    DEFEND-ALIKE between the attack and the defend, and TRIPO-DEFORM-PASSED-BOUND per clip."""

    out: List[dict] = []
    idle_clip = next((clip for clip in anims if clip_role(clip) == "idle"), None)
    idle = numbers.get(idle_clip, {}).get("side_reach") if idle_clip else None
    for clip, row in numbers.items():
        if not isinstance(row, dict):
            continue
        role = clip_role(clip)
        if idle is not None and role in SIDE_REACH_ROLES and "side_reach" in row:
            ratios = [reach / max(base, 1e-6) for reach, base in zip(row["side_reach"], idle)]
            row["side_reach_over_idle"] = [round(value, 3) for value in ratios]
            if max(ratios) > MAX_SIDE_REACH_OVER_IDLE:
                out.append(finding("TRIPO-WING-SIDE-REACH", clip, f"a wing reaches {max(ratios):.2f} times as far to its side as in the idle's fold (at most {MAX_SIDE_REACH_OVER_IDLE:.2f}): the wings held back stand out to the sides", ratio=round(max(ratios), 3)))
        if idle_clip is not None and role in GAME_READ_ROLES:
            read = map_read.clip_reading(mesh, anims[clip], anims[idle_clip])
            row["game_read"] = round(read, 3)
            if read < MIN_GAME_READ:
                out.append(finding("TRIPO-GAME-READ", clip, f"from the game camera the {role} changes {read:.0%} of the idle's silhouette (at least {MIN_GAME_READ:.0%}, the clips of the units reviewers passed 28% to 45%): at game size it reads as the idle", share=round(read, 3)))
        share = deformed_share(mesh, anims[clip], c["all_edges"])
        row["deformed_share"] = round(share, 4)
        if share > DEFORM_PASSED_BOUND:
            out.append(finding("TRIPO-DEFORM-PASSED-BOUND", clip, f"{share:.1%} of the edges stretch or squash 1.5 times in the worst frame (at most {DEFORM_PASSED_BOUND:.1%}, the worst clip of a unit reviewers passed)", share=round(share, 4)))
    if len(peaks) == 2:
        ratio = min(peaks.values()) / max(max(peaks.values()), 1)
        fold = len(_cells(pdx_deform.skin(mesh, pdx_deform.skinning_matrices(mesh, anims[idle_clip])[0])[c["wings"]], _view_axes(mesh, "map"), c["cell"])) if idle_clip else 0
        numbers["attack_defend_wings"] = round(ratio, 3)
        numbers["wings_over_fold"] = round(max(peaks.values()) / max(fold, 1), 3) if fold else None
        opened = not fold or max(peaks.values()) > WINGS_OPEN_SHARE * fold
        if ratio > MAX_ATTACK_DEFEND_WINGS and opened:
            clip = next(clip for clip in anims if clip_role(clip) == "attack")
            out.append(finding("TRIPO-ATTACK-DEFEND-ALIKE", clip, f"at the attack's farthest reach and the defend's middle the wings fill {ratio:.0%} as much of the map view as each other (at most {MAX_ATTACK_DEFEND_WINGS:.0%}): at map size the two clips read alike", share=round(ratio, 3)))
    return out


def deformed_share(mesh, anim, edges: np.ndarray) -> float:
    """TRIPO-DEFORM-PASSED-BOUND's measure: the most, over the clip's frames, of the share of the mesh's edges stretched or squashed past
    `pdx_deform`'s ratio (1.5) and by its significant share of the height (0.5%)."""

    rest = np.linalg.norm(mesh.positions[edges[:, 0]] - mesh.positions[edges[:, 1]], axis=1)
    usable = rest > 1e-9
    if not usable.any():
        return 0.0
    height = max(mesh.height, 1e-6)
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    worst = 0.0
    for frame in range(matrices.shape[0]):
        posed = pdx_deform.skin(mesh, matrices[frame])
        length = np.linalg.norm(posed[edges[:, 0]] - posed[edges[:, 1]], axis=1)
        ratio = length[usable] / rest[usable]
        growth = (length[usable] - rest[usable]) / height
        bad = ((ratio > pdx_deform.STRETCH_RATIO) & (growth > pdx_deform.SIGNIFICANT_SHARE)) | ((ratio < pdx_deform.SQUASH_RATIO) & (-growth > pdx_deform.SIGNIFICANT_SHARE))
        worst = max(worst, float(bad.mean()))
    return worst

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
            found, numbers["flank_hang"] = wing_flank_findings(mesh, anims, sides)
            out += found
            found, numbers["views"] = quadruped_view_findings(mesh, anims, sides)
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


def map_findings(mesh, anims: Dict[str, object], numbers: dict, posture: str = "upright", weapon_bone: str = "",
                 winged: Optional[bool] = None) -> List[dict]:
    """A humanoid's map camera rules: TRIPO-MAP-READ and TRIPO-MAP-ALIKE (lib/map_read.py) and the outline rules (lib/map_outline.py, with
    the idle `posture` the job asks for). Fills `numbers`."""

    findings: List[dict] = []
    found, numbers["map_read"] = map_read.humanoid_findings(mesh, anims)
    findings += found
    found, numbers["map_alike"] = map_read.alike_findings(mesh, anims)
    findings += found
    if map_outline.is_humanoid(mesh):
        found, numbers["map_outline"] = map_outline.outline_findings(mesh, anims, posture, weapon_bone, winged)
        findings += found
    return findings


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
        findings += map_findings(mesh, anims, numbers, posture, weapon_bone, winged)
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
