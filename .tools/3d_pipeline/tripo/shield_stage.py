"""The shield stage: close a unit's free fist round a separately modelled shield. Run in headless Blender after the grip stage.

    blender -b --factory-startup --python shield_stage.py -- <gripped.glb> <shield.glb> --out <shielded.glb>
        [--report report.json] [--hand RightHand] [--height-share 0.65] [--roll 180] [--hold-clips idle,walk,...]
        [--hold-fade-clips CLIP] [--release-clips defeat_03 | --fall-fade-clips defeat_03] [--clearance-clips idle,walk,...]
        [--hold-hand out,forward,up]

The body is the grip stage's GLB (`tripo/grip_weapon.py`: body `tripo_part_0`, weapon `tripo_part_1` on its `Weapon` bone, the
65-joint skeleton with the free hand's fingers, every clip). The shield is an unrigged model. The stage runs the grip stage's own
steps on the free hand, with the grip on the shield found by `lib/tripo_shield.shield_grip` (the fist closes round the middle of the
crescent's inner edge, the outer edge away from the body; the module says why):

1. the shield is scaled so its long axis is `--height-share` of the body's height, and a bar along that axis just inside its inner edge
   is laid across the palm as a weapon's haft is (the grip search). The fingers and the thumb close round the bar and the fist is
   baked into the rest pose, as for the weapon;
2. it is bound rigidly (weight 1.0) to its own bone `Shield`, a child of the hand at the grip, as mesh `tripo_part_2`;
3. the arm hold puts the grip at the unit's side (`--hold-hand`: out, forward, up as shares of the height; by default up so the shield's
   lower end is `GROUND_CLEAR_SHARE` above the ground) with the long axis upright and the outer edge out along the unit's side axis, in
   the clips the weapon arm is held in;
4. the clearance turns the hand about the wrist until the shield leaves the body and the ground (`lib/tripo_clearance.py`, the
   weapon's rule), and reports the frames it could not clear;
5. the death, by the weapon's rule (`--release-clips <death>`): the fist lets go at the first frame of the fall and the shield lies flat
   on the ground clear of the body and of the weapon the grip stage dropped (`lib/tripo_clearance.plan_drop`). Vanilla infantry keep
   their rifle in the hand, and `--fall-fade-clips <death>` does that (the hold fades out by the fall, the clearance judges every frame),
   but measured on the round-4 dwarf's exported files the kept shield ended standing on its edge beside the fallen body: 5.1% of it in
   the body, 3.8% under the ground, and the body 56% of its height tall (TRIPO-NOT-DOWN), with the wrist already turned up to 58
   degrees. Dropped, it landed flat 4.3% of the height clear of the body, 0% in the body or under the ground, the body 39% tall.

The earlier stage's weapon bone keeps its keys: nothing here eases or moves it. The result takes
`prepare_tripo_unit.py --rigid-part tripo_part_1=Weapon --rigid-part tripo_part_2=Shield` unchanged. Exit 3 when a frame could not be
cleared or a drop broke its rule (after writing the files), unless `--clearance-allow-fail`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import bpy
import numpy as np
from mathutils import Quaternion, Vector

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import tripo_clearance as CL
from lib import tripo_grip as G
from lib import tripo_shield as S
from lib.tripo import resolve_clip_name
import grip_weapon as GW

PREFIX = GW.PREFIX
GROUND_CLEAR_SHARE = 0.08  # the held shield's lower end this far over the ground at the hold (shares of the height)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("body", type=Path)
    parser.add_argument("shield", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--hand", default="RightHand", help="the free hand that holds the shield")
    parser.add_argument("--height-share", dest="length_ratio", type=float, default=S.HEIGHT_SHARE, help="the shield's long axis as a share of the body's height")
    parser.add_argument("--roll", type=float, default=S.ROLL_DEGREES, help="the shield's outer edge, degrees about the bar from the palm's normal (180: out of the back of the hand)")
    parser.add_argument("--head-toward", choices=("index", "pinky"), default="index")
    parser.add_argument("--hold-clips", default="")
    parser.add_argument("--hold-fade-clips", default="")
    parser.add_argument("--release-clips", default="", help="clips in which the fist lets go of the shield at the first frame of the fall (the weapon's drop)")
    parser.add_argument("--fall-fade-clips", default="", help="clips (a death) in which the shield stays in the fist: the arm hold fades out by the first frame of the fall and the clearance judges every frame")
    parser.add_argument("--release-drop", type=float, default=CL.HAND_DROP_SHARE)
    parser.add_argument("--hold-hand", default="", help="out, forward, up of the grip as shares of the height (default 0.257, 0.07 and half the shield's share plus GROUND_CLEAR_SHARE)")
    parser.add_argument("--hold-axis", default="0,0,1")
    parser.add_argument("--clearance-clips", default="")
    parser.add_argument("--soft-share", type=float, default=CL.SOFT_SHARE)
    parser.add_argument("--no-clearance", action="store_true")
    parser.add_argument("--clearance-allow-fail", action="store_true")
    parser.add_argument("--diagonal-min", type=float, default=28.0)
    parser.add_argument("--diagonal-max", type=float, default=55.0)
    parser.add_argument("--ease-snaps", type=float, default=14.0)
    parser.add_argument("--check-frames", type=int, default=6)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    args = parser.parse_args(argv)
    if not args.hold_hand:
        args.hold_hand = f"0.257,0.07,{args.length_ratio / 2 + GROUND_CLEAR_SHARE:.4f}"
    # the grip stage's own options this stage fixes: the part gets its own bone, the grip is the bar's middle, no grip dump
    args.weapon_bone, args.grip, args.dump_grip = True, 0.5, None
    return args


def load_body(c):
    """Import the gripped body: the skinned body `tripo_part_0`, the parts an earlier stage bound (kept as they are), every bone at rest."""

    args = c.args
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(args.body))
    arm = max((o for o in bpy.data.objects if o.type == "ARMATURE"), key=lambda o: len(o.data.bones))
    skinned = [o for o in bpy.data.objects if o.type == "MESH" and len(o.vertex_groups) > 0]
    for obj in [o for o in bpy.data.objects if o.type == "MESH" and o not in skinned]:
        bpy.data.objects.remove(obj, do_unlink=True)
    if any(o.name.startswith(S.SHIELD_PART) for o in skinned):
        raise SystemExit(f"{args.body.name} already holds a {S.SHIELD_PART}")
    named = [o for o in skinned if o.name.startswith("tripo_part_0")]
    body = named[0] if named else max(skinned, key=lambda o: len(o.data.vertices))
    c.others = [o for o in skinned if o is not body]
    if PREFIX + S.SHIELD_BONE in arm.data.bones:
        raise SystemExit(f"the rig already has a {S.SHIELD_BONE} bone")
    if PREFIX + c.hand + "Index1" not in arm.data.bones:
        raise SystemExit(f"the rig has no finger bones on {c.hand}: run this stage on the grip stage's GLB, before the intake")
    c.arm, c.body, c.scene = arm, body, bpy.context.scene
    c.rest_coords = GW.world_array(body, GW.mesh_coords(body))
    c.height = float(np.ptp(c.rest_coords[:, 2]))
    c.ground = float(c.rest_coords[:, 2].min())
    c.centre_x = float(c.rest_coords[:, 0].mean())
    c.report["body_height"] = round(c.height, 4)
    c.report["other_parts"] = [o.name for o in c.others]
    arm.animation_data_create()
    arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)
    bpy.context.view_layer.update()


def load_shield(c):
    """Import the shield (its meshes joined), scale it to `--height-share` of the height and find the bar the fist closes on."""

    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(c.args.shield))
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == "MESH"]
    if not meshes:
        raise SystemExit(f"{c.args.shield.name} has no mesh")
    for obj in meshes:
        matrix = obj.matrix_world.copy()
        obj.parent = None
        obj.matrix_world = matrix
    for obj in [o for o in new if o.type != "MESH"]:
        bpy.data.objects.remove(obj, do_unlink=True)
    if len(meshes) > 1:
        bpy.ops.object.select_all(action="DESELECT")
        for obj in meshes:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]
        bpy.ops.object.join()
    c.weapon = meshes[0]
    for group in list(c.weapon.vertex_groups):
        c.weapon.vertex_groups.remove(group)
    points = GW.world_array(c.weapon, GW.mesh_coords(c.weapon))
    grip = S.shield_grip(points, c.args.length_ratio)
    c.scale = c.args.length_ratio * c.height / grip["length"]
    c.local = c.scale * ((points - grip["grip"]) @ grip["axes"])  # (along the bar to the head, toward the outer edge, third)
    c.radius = S.GRIP_RADIUS_SHARE * c.height
    c.report["shield_grip"] = {"scale": round(c.scale, 4), "bar_radius_share": S.GRIP_RADIUS_SHARE, "bow_share": round(grip["bow_share"], 4),
                               "bowed": grip["bowed"], "extents_share": np.round(np.ptp(c.local, axis=0) / c.height, 4).tolist()}


def occupants(c):
    """The dropped weapon in each frame of the release clips, in the world the pipeline grounds by the body: the shield lands clear of it."""

    out = {}
    for name in c.drop_clips:
        action = bpy.data.actions[name]
        GW.use_action(c.arm, action)
        f0, f1 = int(action.frame_range[0]), int(action.frame_range[1])
        frames = []
        for frame in range(f0, f1 + 1):
            c.scene.frame_set(frame)
            lift = -float(GW.evaluated_coords(c.body)[:, 2].min())
            frames.append(np.concatenate([GW.evaluated_coords(o)[::4] for o in c.others]) + np.array([0.0, 0.0, lift]) if c.others else np.zeros((0, 3)))
        out[name] = frames
    return out


def side_axis(c) -> np.ndarray:
    """The unit's side on the shield hand's side: Tripo's units face -Y in Blender's world, so the right side is -X."""

    return np.array([-1.0 if "Right" in c.hand else 1.0, 0.0, 0.0])


def shield_now(c):
    """The bar's centre, the long axis and the outer edge's direction now, carried by the hand from rest."""

    motion = np.array(c.arm.matrix_world @ c.arm.pose.bones[PREFIX + c.hand].matrix) @ np.linalg.inv(c.hand_rest)
    return motion[:3, :3] @ c.haft_centre + motion[:3, 3], motion[:3, :3] @ c.head_dir, motion[:3, :3] @ c.blade


def facing_degrees(c, long_axis, outer):
    """(the long axis to the vertical, the outer edge to the side axis), degrees."""

    level = G.unit(outer - (outer @ long_axis) * long_axis)
    return (round(float(np.degrees(np.arccos(np.clip(abs(long_axis[2]), -1, 1)))), 1),
            round(float(np.degrees(np.arccos(np.clip(level @ side_axis(c), -1, 1)))), 1))


def solve_clip_hold(c, name):
    """The grip stage's arm hold (`grip_weapon.solve_clip_hold`) with one more target: the shield's outer edge points out along the unit's side
    axis, as the art holds it, as well as the long axis upright and the grip at `--hold-hand`. The two directions go to the same least squares
    (`lib/tripo_grip.solve_hold`) as one six-component direction, each half of it weighed alike."""

    arm, scene, height = c.arm, c.scene, c.height
    action = bpy.data.actions[name]
    GW.use_action(arm, action)
    f0 = int(action.frame_range[0])
    scene.frame_set(f0)
    base_q = {b: arm.pose.bones[b].rotation_quaternion.copy() for b in c.arm_bones}
    falls = name in c.drop_clips or name in c.fall_clips
    fade_to = GW.hold_fade_frame(c, action, falls) if falls or name in c.fade_clips else None
    _point, long_before, outer_before = shield_now(c)

    def offsets_of(params):
        out = {}
        for k, bone in enumerate(c.arm_bones):
            rv = params[3 * k : 3 * k + 3] * GW.ARM_SCALES[k]
            angle = float(np.linalg.norm(rv))
            out[bone] = Quaternion(Vector(rv / angle), angle) if angle > 1e-9 else Quaternion()
        return out

    def forward_kinematics(params):
        for bone, q_off in offsets_of(params).items():
            arm.pose.bones[bone].rotation_quaternion = base_q[bone] @ q_off
        bpy.context.view_layer.update()
        point, long_axis, outer = shield_now(c)
        return point, np.concatenate([long_axis, outer])

    starts = [np.zeros(12)]
    for roll in (np.pi / 2, np.pi, -np.pi / 2):
        guess = np.zeros(12)
        guess[7] = roll  # the forearm's own axis
        starts.append(guess)
    target = np.concatenate([c.hold_axis, side_axis(c)])
    solved = G.solve_hold(forward_kinematics, starts, c.hold_target, target, scale=height, ridge=0.01)
    GW.multiply_hold_into_keys(arm, action, offsets_of(solved["params"]), fade_to)
    GW.use_action(arm, action)
    scene.frame_set(f0)
    point, long_after, outer_after = shield_now(c)
    return {
        "grip_point_after": np.round(point, 3).tolist(), "position_error": round(float(np.linalg.norm(point - c.hold_target)), 4),
        "long_axis_and_outer_edge_degrees_before": facing_degrees(c, long_before, outer_before),
        "long_axis_and_outer_edge_degrees_after": facing_degrees(c, long_after, outer_after),
        "offsets_degrees": {b.replace(PREFIX, ""): round(float(np.degrees(q.angle)), 1) for b, q in offsets_of(solved["params"]).items()},
        "faded_out_by_frame": fade_to,
    }


def hold_arm(c):
    """The arm hold of the grip stage (`grip_weapon.hold_arm`, the same clips, target and bones), solved with the outer edge's target too."""

    args, hand, height = c.args, c.hand, c.height
    c.action_names = [a.name for a in bpy.data.actions]
    c.fade_clips = [resolve_clip_name(n, c.action_names) for n in args.hold_fade_clips.split(",") if n]
    c.drop_clips = [resolve_clip_name(n, c.action_names) for n in args.release_clips.split(",") if n]
    c.fall_clips = [resolve_clip_name(n, c.action_names) for n in args.fall_fade_clips.split(",") if n]
    hold_clips = [resolve_clip_name(n, c.action_names) for n in args.hold_clips.split(",") if n] + c.fade_clips + c.drop_clips + c.fall_clips
    out_f, fwd_f, up_f = (float(v) for v in args.hold_hand.split(","))
    hips_y = float(GW.rest_head(c.arm, PREFIX + "Hips")[1])
    c.hold_target = np.array([c.centre_x + side_axis(c)[0] * out_f * height, hips_y - fwd_f * height, c.ground + up_f * height])
    c.hold_axis = np.array([float(v) for v in args.hold_axis.split(",")])
    c.arm_bones = [PREFIX + hand.replace("Hand", part) for part in ("Shoulder", "Arm", "ForeArm")] + [PREFIX + hand]
    arm_groups = [PREFIX + hand.replace("Hand", "Arm"), PREFIX + hand.replace("Hand", "ForeArm"), PREFIX + hand]
    c.arm_family = [n for n in set(c.groups) if n in arm_groups or n.startswith(PREFIX + hand)]
    c.hold = {"target_position": np.round(c.hold_target, 3).tolist(), "target_axis": c.hold_axis.tolist(), "target_outer_edge": side_axis(c).tolist(),
              "clips": {name: solve_clip_hold(c, name) for name in hold_clips}}
    c.report["hold"] = c.hold


def export(c):
    for action in bpy.data.actions:
        action.use_fake_user = True
    GW.use_action(c.arm, bpy.data.actions[0])
    bpy.ops.object.select_all(action="DESELECT")
    for obj in [c.arm, c.body, c.weapon] + c.others:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = c.arm
    c.args.out.parent.mkdir(parents=True, exist_ok=True)
    properties = bpy.ops.export_scene.gltf.get_rna_type().properties
    options = {"filepath": str(c.args.out), "export_format": "GLB", "use_selection": True, "export_skins": True, "export_animations": True,
               "export_animation_mode": "ACTIONS", "export_image_format": "AUTO"}
    bpy.ops.export_scene.gltf(**{k: v for k, v in options.items() if k in properties})
    c.report["exported_clips"] = sorted(a.name for a in bpy.data.actions)
    print(json.dumps(c.report, sort_keys=True))
    if c.args.report:
        c.args.report.parent.mkdir(parents=True, exist_ok=True)
        c.args.report.write_text(json.dumps(c.report, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def main():
    args = parse_args()
    from lib import glb_root

    named = [n for text in (args.hold_clips, args.hold_fade_clips, args.release_clips, args.clearance_clips) for n in (text or "").split(",")]
    travelling = glb_root.travelling_clips(args.body, named)
    if travelling:
        print("shield_stage refused: clips that move the hips across the ground " + json.dumps(travelling), file=sys.stderr)
        sys.exit(4)
    c = SimpleNamespace(args=args, hand=args.hand, bone_name=S.SHIELD_BONE, part_name=S.SHIELD_PART, ease_skip=(PREFIX + GW.WEAPON_BONE,),
                        report={"tool": "shield_stage", "body": args.body.name, "shield": args.shield.name, "hand": args.hand})
    load_body(c)
    GW.find_hand_frame(c)
    GW.find_finger_skins(c)
    load_shield(c)
    GW.search_grip(c)
    GW.close_thumb(c)
    GW.describe_grip(c)
    GW.pose_and_bake_fingers(c)
    GW.bind_weapon(c)
    hold_arm(c)
    c.report["rotation_keys"] = {action.name: GW.ease_clip(c, action) for action in bpy.data.actions}
    GW.clear_weapon_from_body(c)
    c.report["rotation_keys_after_clearance"] = {action.name: GW.ease_clip(c, action) for action in bpy.data.actions}
    for name in c.drop_clips:
        GW.smooth_rotation_keys(bpy.data.actions[name])  # as the drop does first, so the weapon is read where the drop will judge it
    c.occupant_frames = occupants(c)
    GW.release_clips(c)
    GW.check_fingers(c)
    dropped = GW.drop_failures(c)
    export(c)
    failed = c.clearance_failed
    if (failed or dropped) and not args.clearance_allow_fail:
        if failed:
            print("CLEARANCE_FAILED " + json.dumps(failed), file=sys.stderr)
        if dropped:
            print("DROP_FAILED " + json.dumps(dropped), file=sys.stderr)
        raise SystemExit(3)


try:
    main()
except SystemExit as failure:
    import os

    if failure.code not in (None, 0):
        sys.stdout.flush()
        print(f"shield_stage failed: {failure.code}", file=sys.stderr)
        sys.stderr.flush()
        os._exit(1)
    raise
