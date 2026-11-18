"""The quadruped rig's ears (adapter/quadruped_ears.py) and the clip rules round 12 of the war elephant added, without Blender: ears found
by rule as thin flaps beside the head, weighted to their own bones, closing onto the head in a death, spreading in a defend and lagging
the head elsewhere; the rear's forearm reach and knee fold, the defend's step back and the hind legs' smaller turn in a death."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE / "adapter"))

import quadruped_ears as qe
import quadruped_layout as ql


def _box(lo, hi, steps=8):
    """A closed box surface as a grid of quads (two triangles each), outward facing; `steps` per axis (an int for all three)."""

    lo, hi = np.asarray(lo, float), np.asarray(hi, float)
    counts = (steps,) * 3 if isinstance(steps, int) else tuple(steps)
    points, triangles = [], []
    for axis in range(3):
        u, v = [a for a in range(3) if a != axis]
        nu, nv = counts[u], counts[v]
        for side, value in ((0, lo[axis]), (1, hi[axis])):
            base = len(points)
            for i in range(nu + 1):
                for j in range(nv + 1):
                    p = np.zeros(3)
                    p[axis] = value
                    p[u] = lo[u] + (hi[u] - lo[u]) * i / nu
                    p[v] = lo[v] + (hi[v] - lo[v]) * j / nv
                    points.append(p)
            for i in range(nu):
                for j in range(nv):
                    a, b, c, d = base + i * (nv + 1) + j, base + (i + 1) * (nv + 1) + j, base + (i + 1) * (nv + 1) + j + 1, base + i * (nv + 1) + j + 1
                    first, second = ((a, b, c), (a, c, d))
                    if (side == 1) == (axis == 1):
                        first, second = (a, c, b), (a, d, c)
                    triangles += [first, second]
    return np.array(points), np.array(triangles)


def _animal(ear_reach: float):
    """A blocky quadruped facing -Y: four legs, a torso, a neck and head, and an ear flap each side of the head reaching `ear_reach` from the
    mid-plane (0.02 thick). The torso is 0.35 wide each side."""

    parts = [((x - 0.08, y - 0.08, 0.0), (x + 0.08, y + 0.08, 1.0)) for x in (-0.22, 0.22) for y in (0.0, 1.6)]
    parts.append(((-0.35, -0.2, 1.0), (0.35, 1.8, 1.6)))
    parts.append(((-0.15, -0.7, 1.3), (0.15, -0.2, 1.8)))
    parts = [(lo, hi, 8) for lo, hi in parts]
    parts.append(((0.15, -0.6, 1.45), (ear_reach, -0.58, 1.75), (8, 1, 8)))  # an ear is one quad across its thickness, as a generator makes it
    parts.append(((-ear_reach, -0.6, 1.45), (-0.15, -0.58, 1.75), (8, 1, 8)))
    points, triangles = [], []
    for lo, hi, steps in parts:
        p, t = _box(lo, hi, steps)
        triangles.append(t + sum(len(x) for x in points))
        points.append(p)
    return np.vstack(points), np.vstack(triangles)


class FindEars(unittest.TestCase):
    def test_thin_flaps_beside_the_head_are_the_ears(self) -> None:
        points, triangles = _animal(0.7)
        landmarks = ql.detect_landmarks(points)
        ears, masks = qe.detect_ears(points, triangles, landmarks)
        self.assertEqual(set(ears), {"Left", "Right"})
        for side, sign in (("Left", 1.0), ("Right", -1.0)):
            flap = (np.abs(points[:, 0]) > 0.16) & (points[:, 1] > -0.61) & (points[:, 1] < -0.57)
            self.assertGreater((masks[side] & flap).sum(), 0.8 * (flap & (points[:, 0] * sign > 0)).sum(), "the flap is the ear")
            self.assertFalse((masks[side] & (np.abs(points[:, 0]) < 0.15)).any(), "the head is not")
            chain = ears[side]
            self.assertLess(abs(chain["root"][0]), abs(chain["tip"][0]), "the chain runs from the head outward")
            self.assertGreater(abs(chain["hinge"][2]), 0.9, "the root line stands upright")
            self.assertGreater(chain["close_room"], 0.0)
        layout = ql.build_layout({**landmarks, "ears": ears})
        self.assertEqual(len(layout.bones), len(ql.build_layout(landmarks).bones) + 4)
        self.assertEqual(layout.bone("Ear_Left_01").parent, "Head")
        self.assertEqual(layout.bone("Ear_Left_02").parent, "Ear_Left_01")

    def test_ears_inside_the_torso_width_ride_the_head(self) -> None:
        points, triangles = _animal(0.3)
        ears, masks = qe.detect_ears(points, triangles, ql.detect_landmarks(points))
        self.assertEqual((ears, masks), ({}, {}))

    def test_an_ear_hangs_from_the_bone_its_root_follows_and_takes_its_own_bones(self) -> None:
        points, triangles = _animal(0.7)
        landmarks = ql.detect_landmarks(points)
        ears, masks = qe.detect_ears(points, triangles, landmarks)
        qe.assign_parents(points, landmarks, ears, masks)
        landmarks["ears"] = ears
        layout = ql.build_layout(landmarks)
        names = layout.names()
        plain_i, plain_w = ql.skin_weights(points, ql.build_layout({key: value for key, value in landmarks.items() if key != "ears"}))
        plain = ql.build_layout({key: value for key, value in landmarks.items() if key != "ears"}).names()
        _s, zone = qe._root_zone(points, masks["Left"], ears["Left"])
        carried = {}
        for row in np.flatnonzero(zone):
            for bone, weight in zip(plain_i[row], plain_w[row]):
                carried[plain[bone]] = carried.get(plain[bone], 0.0) + weight
        self.assertEqual(ears["Left"]["parent"], qe.median_bone({name: carried.get(name, 0.0) for name in qe.EAR_PARENT_ORDER}),
                         "the bone in the middle of the root skin's weight down the neck")
        self.assertEqual(layout.bone("Ear_Left_01").parent, ears["Left"]["parent"])
        indices, weights = ql.skin_weights(points, layout)
        out_i, out_w = qe.ear_weights(points, triangles, layout, masks, indices, weights, ring=0.05)
        tip = int(np.argmax(points[:, 0] * masks["Left"]))
        tip_bones = {names[i] for i, w in zip(out_i[tip], out_w[tip]) if w > 0.5}
        self.assertEqual(tip_bones, {"Ear_Left_02"}, "the ear's tip follows the outer bone")
        np.testing.assert_allclose(out_w.sum(axis=1), 1.0, atol=1e-9)
        untouched = ~(masks["Left"] | masks["Right"])
        np.testing.assert_array_equal(out_w[untouched & (points[:, 1] > 0)], weights[untouched & (points[:, 1] > 0)], "skin far from the ears keeps its weights")


def _eared_layout(load: bool = True, parent: str = "") -> ql.Layout:
    points, triangles = _animal(0.7)
    landmarks = ql.detect_landmarks(points)
    landmarks["legs"] = {key: {**joints, "radius": np.asarray(0.25 * float(landmarks["belly_z"]))} for key, joints in landmarks["legs"].items()}
    ears, masks = qe.detect_ears(points, triangles, landmarks)
    qe.assign_parents(points, landmarks, ears, masks)
    for ear in ears.values():
        ear["parent"] = parent or ear["parent"]
    landmarks["ears"] = ears
    if load:
        landmarks["load"] = {"roll_limit": 70.0, "roll_limit_other_side": -64.0, "bone": ql.LOAD_BONE}
    return ql.build_layout(landmarks)


def _degrees(pose: dict, name: str, axis) -> float:
    return sum(degrees for row_axis, degrees in pose.get(name, []) if np.allclose(row_axis, axis))


class EarParent(unittest.TestCase):
    def test_an_ear_hangs_from_the_middle_of_its_root_weight_down_the_neck(self) -> None:
        self.assertEqual(qe.median_bone({"Head": 0.36, "Neck_02": 0.28, "Neck_01": 0.22, "Chest": 0.12}), "Neck_02")
        self.assertEqual(qe.median_bone({"Chest": 0.33, "Neck_01": 0.32, "Neck_02": 0.29}), "Neck_01")
        self.assertEqual(qe.median_bone({"Head": 0.9, "Neck_02": 0.1}), "Head")
        self.assertEqual(qe.median_bone({}), "Head")


class EarMotion(unittest.TestCase):
    def test_in_a_death_both_ears_close_as_far_as_their_room(self) -> None:
        layout = _eared_layout()
        last = ql.frame_count("quadruped_collapse") - 1
        for roll in (-98.0, 98.0):
            layout.landmarks["death"] = {"roll": roll, "neck_lift": 0.0}
            pose = ql.pose_at("quadruped_collapse", last, layout)
            for side, ear in layout.landmarks["ears"].items():
                turn = _degrees(pose, f"Ear_{side}_01", ear["hinge"]) + _degrees(pose, f"Ear_{side}_02", ear["hinge"])
                self.assertAlmostEqual(turn, ear["close_sign"] * ear["close_room"], places=6)

    def test_in_a_defend_the_ears_spread_forward_within_their_room(self) -> None:
        layout = _eared_layout()
        total = ql.frame_count("quadruped_brace")
        for side, ear in layout.landmarks["ears"].items():
            turns = [_degrees(ql.pose_at("quadruped_brace", frame, layout), f"Ear_{side}_01", ear["hinge"]) for frame in range(total)]
            widest = max(turns, key=abs)
            self.assertLess(widest * ear["close_sign"], 0.0, "spread, not closed")
            self.assertLessEqual(abs(widest), ql.EAR_ROOT_SHARE * min(ql.GUARD_EAR_SPREAD, ear["spread_room"]) + 1e-9)
            self.assertAlmostEqual(turns[0], 0.0, places=6)

    def test_an_ear_lags_the_head_and_loops_back(self) -> None:
        layout = _eared_layout(load=False, parent="Head")
        total = ql.frame_count("quadruped_walk")
        lags = [_degrees(ql.pose_at("quadruped_walk", frame, layout), "Ear_Left_02", ql.Z_AXIS) for frame in range(total + 1)]
        self.assertGreater(max(map(abs, lags)), 1.0, "the outer ear swings behind the head")
        self.assertAlmostEqual(lags[0], lags[-1], places=6)
        self.assertEqual(_degrees(ql.pose_at("quadruped_walk", 5, layout), "Ear_Left_01", ql.Z_AXIS), 0.0, "the root follows the head")


class RoundTwelveClips(unittest.TestCase):
    def test_the_raised_forearm_reaches_and_the_knee_folds_as_the_horse_attack(self) -> None:
        for heavy in (True, False):
            layout = _eared_layout() if heavy else ql.build_layout(ql.detect_landmarks(_animal(0.3)[0]))
            pose = ql.pose_at("quadruped_rear", 17, layout)  # the top of the rear
            forearm = _degrees(pose, "Front_Left_Upper", ql.X_AXIS) + _degrees(pose, "Front_Left_Lower", ql.X_AXIS)
            share = ql.HEAVY_REACH if heavy else 1.0
            rise = ql.HEAVY_PITCH if heavy else 1.0
            kick = -forearm / (ql.HORSE_FOREARM_REACH * share * rise)
            self.assertTrue(0.7 < kick < 1.3, "the forearm reaches forward the horse's share")
            rest = ql.knee_rest_fold(layout.landmarks["legs"]["Front_Left"])
            self.assertAlmostEqual(_degrees(pose, "Front_Left_Cannon", ql.X_AXIS) + rest, ql.HORSE_KNEE_FOLD * share, places=6,
                                   msg="the knee ends bent the horse's fold from straight")

    def test_a_knee_slanted_forward_at_rest_has_a_negative_rest_fold(self) -> None:
        joints = {"upper": np.array([0.0, 0.0, 3.0]), "middle": np.array([0.0, 0.0, 1.5]), "lower": np.array([0.0, -0.5, 0.2])}
        self.assertLess(ql.knee_rest_fold(joints), -15.0)

    def test_the_defend_steps_back_over_planted_feet(self) -> None:
        layout = _eared_layout()
        frame = ql.frame_count("quadruped_brace") // 2
        pose = ql.pose_at("quadruped_brace", frame, layout)
        envelope = ql._brace_envelope(frame / (ql.frame_count("quadruped_brace") - 1))
        lean = (float(layout.landmarks["belly_z"]) + float(layout.landmarks["back_z"])) / 2
        self.assertAlmostEqual(_degrees(pose, "__root_shift__", ql.Y_AXIS), lean * np.sin(np.radians(ql.GUARD_LEAN)) * envelope, places=6)
        for end, side in ql.LEGS:
            self.assertAlmostEqual(_degrees(pose, ql.leg_name(end, side, "Upper"), ql.X_AXIS), -ql.GUARD_LEAN * envelope, places=6)
            self.assertAlmostEqual(_degrees(pose, ql.leg_name(end, side, "Hoof"), ql.X_AXIS), ql.GUARD_LEAN * envelope, places=6, msg="the hoof stays flat")
        self.assertNotIn("__root_yaw__", pose)
        self.assertLessEqual(ql.GUARD_LEAN, ql.PILLAR_SWING)

    def test_the_hind_legs_turn_less_at_the_thigh_when_lying(self) -> None:
        layout = _eared_layout()
        layout.landmarks["death"] = {"roll": -98.0, "neck_lift": 0.0}
        pose = ql.pose_at("quadruped_collapse", ql.frame_count("quadruped_collapse") - 1, layout)
        front = _degrees(pose, "Front_Right_Lower", ql.Y_AXIS)
        hind = _degrees(pose, "Rear_Right_Lower", ql.Y_AXIS)
        self.assertAlmostEqual(hind / front, ql.DEATH_HIND_DROP["Lower"] / ql.DEATH_LEG_DROP["Lower"], places=6)
        self.assertLess(ql.DEATH_HIND_DROP["Lower"], ql.DEATH_LEG_DROP["Lower"])


if __name__ == "__main__":
    unittest.main()
