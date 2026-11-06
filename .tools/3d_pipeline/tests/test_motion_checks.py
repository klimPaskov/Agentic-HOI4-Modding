"""The seam, knee, still, same-role and shared-clip rules, on a small synthetic two-legged unit.

The unit stands 1.8 high (Y up) and faces -Z: hips, two legs with knee, ankle and toe joints, and a
spine with a head. Each leg, the torso and the crotch are ribbons of quads skinned to their bones.
"""

from __future__ import annotations

import contextlib
import io
import math
import struct
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import check_unit_files
from lib import pdx_deform, pdx_motion

BONES = [
    ("Hips", -1, (0.0, 1.0, 0.0)),
    ("LeftUpLeg", 0, (0.15, 0.95, 0.0)),
    ("LeftLeg", 1, (0.15, 0.5, 0.0)),
    ("LeftFoot", 2, (0.15, 0.08, 0.0)),
    ("LeftToeBase", 3, (0.15, 0.0, -0.15)),
    ("RightUpLeg", 0, (-0.15, 0.95, 0.0)),
    ("RightLeg", 5, (-0.15, 0.5, 0.0)),
    ("RightFoot", 6, (-0.15, 0.08, 0.0)),
    ("RightToeBase", 7, (-0.15, 0.0, -0.15)),
    ("Spine", 0, (0.0, 1.3, 0.0)),
    ("Head", 9, (0.0, 1.7, 0.0)),
]
INDEX = {name: index for index, (name, _parent, _position) in enumerate(BONES)}
# Loose limits for the rules these tests do not exercise; tight ones for the motion rules.
LIMITS = {
    "largest_open_loop": 1e9,
    "open_edge_share": 1.0,
    "winding_flips": 1e9,
    "inside_out_triangles": 1e9,
    "bridge_edges": 1e9,
    "stretched_share": 1.0,
    "squashed_share": 1.0,
    "worst_stretch_share": 1e9,
    "sink": 1e9,
    "death_sink": 1e9,
    "hover": 1e9,
    "seam_edges": 0,
    "still_motion": 0.003,
}


def _prop(name: str, kind: str, values) -> bytes:
    data = b"!" + struct.pack("<B", len(name)) + name.encode("latin-1") + kind.encode() + struct.pack("<i", len(values))
    if kind == "i":
        return data + struct.pack(f"<{len(values)}i", *values)
    if kind == "f":
        return data + struct.pack(f"<{len(values)}f", *values)
    for value in values:
        encoded = value.encode("latin-1") + b"\0"
        data += struct.pack("<i", len(encoded)) + encoded
    return data


def _obj(name: str, depth: int) -> bytes:
    return b"[" * depth + name.encode("latin-1") + b"\0"


def ribbon(points, influences, vertices, triangles, width=0.03):
    """Append a ribbon of quads along `points`, each point skinned with its `influences` entry."""

    start = len(vertices)
    for (x, y, z), skin in zip(points, influences):
        vertices.append(((x - width, y, z), skin))
        vertices.append(((x + width, y, z), skin))
    for step in range(len(points) - 1):
        a, b, c, d = start + 2 * step, start + 2 * step + 1, start + 2 * step + 2, start + 2 * step + 3
        triangles += [(a, b, d), (a, d, c)]


def body(crotch_blend: float):
    """The unit's vertices and triangles. The crotch ribbon carries `crotch_blend` of the hips."""

    vertices, triangles = [], []
    for side, x in (("Left", 0.15), ("Right", -0.15)):
        leg = [(x, 0.0, 0.0), (x, 0.08, 0.0), (x, 0.5, 0.0), (x, 0.95, 0.0)]
        ribbon(leg, [[(f"{side}Foot", 1.0)], [(f"{side}Foot", 1.0)], [(f"{side}Leg", 1.0)], [(f"{side}UpLeg", 1.0)]], vertices, triangles)
    ribbon([(0.0, 0.95, 0.0), (0.0, 1.3, 0.0), (0.0, 1.8, 0.0)], [[("Hips", 1.0)], [("Spine", 1.0)], [("Head", 1.0)]], vertices, triangles)
    # The crotch: a ribbon across from the left thigh's top to the right thigh's, along X.
    start = len(vertices)
    for x, side in ((0.12, "Left"), (0.04, "Left"), (-0.04, "Right"), (-0.12, "Right")):
        skin = [(f"{side}UpLeg", 1.0 - crotch_blend)] + ([("Hips", crotch_blend)] if crotch_blend else [])
        vertices.append(((x, 0.92, 0.0), skin))
        vertices.append(((x, 0.86, 0.0), skin))
    for step in range(3):
        a, b, c, d = start + 2 * step, start + 2 * step + 1, start + 2 * step + 2, start + 2 * step + 3
        triangles += [(a, c, d), (a, d, b)]
    return vertices, triangles


def write_mesh(path: Path, vertices, triangles) -> None:
    data = b"@@b@" + _obj("object", 1) + _obj("unit", 2) + _obj("mesh", 3)
    data += _prop("p", "f", [float(v) for position, _skin in vertices for v in position])
    data += _prop("tri", "i", [int(i) for t in triangles for i in t])
    data += _obj("material", 4) + _prop("shader", "s", ["PdxMeshAdvanced"])
    ix, w = [], []
    for _position, skin in vertices:
        pairs = list(skin) + [(None, 0.0)] * (4 - len(skin))
        ix += [INDEX[name] if name else -1 for name, _weight in pairs]
        w += [weight for _name, weight in pairs]
    data += _obj("skin", 4) + _prop("bones", "i", [4]) + _prop("ix", "i", ix) + _prop("w", "f", w)
    data += _obj("skeleton", 3)
    for index, (name, parent, (x, y, z)) in enumerate(BONES):
        data += _obj(name, 4) + _prop("ix", "i", [index])
        if parent >= 0:
            data += _prop("pa", "i", [parent])
        data += _prop("tx", "f", [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, -x, -y, -z])
    path.write_bytes(data)


def about_x(degrees: float):
    half = math.radians(degrees) / 2.0
    return (math.sin(half), 0.0, 0.0, math.cos(half))


def write_anim(path: Path, frames: int, pose) -> None:
    """`pose(frame)` returns {bone: quaternion x y z w} for the bones that turn."""

    rest_local = {}
    for name, parent, position in BONES:
        parent_position = BONES[parent][2] if parent >= 0 else (0.0, 0.0, 0.0)
        rest_local[name] = [position[i] - parent_position[i] for i in range(3)]
    data = b"@@b@" + _obj("info", 1) + _prop("fps", "f", [15.0]) + _prop("sa", "i", [frames]) + _prop("j", "i", [len(BONES)])
    for name, _parent, _position in BONES:
        data += _obj(name, 2) + _prop("sa", "s", ["tq"])
        data += _prop("t", "f", rest_local[name]) + _prop("q", "f", [0.0, 0.0, 0.0, 1.0]) + _prop("s", "f", [1.0])
    t, q = [], []
    for frame in range(frames):
        turned = pose(frame)
        for name, _parent, _position in BONES:
            q += list(turned.get(name, (0.0, 0.0, 0.0, 1.0)))
            t += rest_local[name]
    data += _obj("samples", 1) + _prop("q", "f", q) + _prop("t", "f", t)
    path.write_bytes(data)


def walk(frame: int):
    swing = 30.0 * math.sin(2 * math.pi * frame / 20)
    return {"LeftUpLeg": about_x(swing), "RightUpLeg": about_x(-swing), "LeftLeg": about_x(-20 - 15 * math.sin(2 * math.pi * frame / 20)), "RightLeg": about_x(-20)}


def strike(frame: int):
    lean = 45.0 * math.sin(math.pi * frame / 19)
    return {"Spine": about_x(-lean), "Head": about_x(-lean / 2), "LeftUpLeg": about_x(lean / 2), "LeftLeg": about_x(-lean)}


def write_unit(folder: Path, stem: str, clips, crotch_blend: float = 0.5) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    write_mesh(folder / f"{stem}.mesh", *body(crotch_blend))
    for role, (frames, pose) in clips.items():
        write_anim(folder / f"{stem}_{role}.anim", frames, pose)


class MotionRules(unittest.TestCase):
    def check(self, clips, crotch_blend: float = 0.5):
        with tempfile.TemporaryDirectory() as folder:
            write_unit(Path(folder), "u", clips, crotch_blend)
            findings, facts = check_unit_files.check_files(Path(folder), None, None, limits=LIMITS)
        return findings, facts

    def rules(self, clips, crotch_blend: float = 0.5):
        return {item.rule for item in self.check(clips, crotch_blend)[0]}

    def test_legs_are_found_by_height_and_parentage(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            write_unit(Path(folder), "u", {})
            mesh = pdx_deform.load_mesh(Path(folder) / "u.mesh")
        legs = pdx_motion.find_legs(mesh)
        self.assertTrue(legs.biped)
        self.assertEqual(sorted(mesh.bones[leg.knee] for leg in legs.legs), ["LeftLeg", "RightLeg"])
        self.assertEqual(mesh.bones[legs.pelvis], "Hips")
        self.assertAlmostEqual(float(legs.forward[2]), -1.0)

    def test_a_clean_walk_and_strike_pass(self) -> None:
        rules = self.rules({"move": (20, walk), "attack": (20, strike)})
        self.assertFalse(rules & {"UNIT-SEAM", "UNIT-ANIM-KNEE", "UNIT-ANIM-STILL", "UNIT-ANIM-SAME"}, rules)

    def test_a_knee_bent_backward_fails(self) -> None:
        # Turning the shin about +X swings the ankle forward (-Z): the knee points backward.
        findings, facts = self.check({"attack": (10, lambda f: {"LeftLeg": about_x(4.0 * f)})})
        knee = [item for item in findings if item.rule == "UNIT-ANIM-KNEE"]
        self.assertEqual(len(knee), 1, findings)
        self.assertIn("LeftLeg", knee[0].message)
        self.assertLess(facts["motion"]["u.mesh"]["clips"]["u_attack.anim"]["worst_knee_bend"], -pdx_motion.KNEE_TOLERANCE)

    def test_a_knee_bent_forward_passes(self) -> None:
        self.assertNotIn("UNIT-ANIM-KNEE", self.rules({"attack": (10, lambda f: {"LeftLeg": about_x(-4.0 * f)})}))

    def test_a_crotch_weighted_to_one_thigh_per_side_is_a_seam(self) -> None:
        findings, facts = self.check({}, crotch_blend=0.0)
        self.assertIn("UNIT-SEAM", {item.rule for item in findings})
        self.assertEqual(facts["motion"]["u.mesh"]["seam_pairs"], {"LeftUpLeg-RightUpLeg": facts["motion"]["u.mesh"]["seam_edges"]})

    def test_a_crotch_blended_into_the_hips_is_no_seam(self) -> None:
        _findings, facts = self.check({}, crotch_blend=0.4)
        self.assertEqual(facts["motion"]["u.mesh"]["seam_edges"], 0)

    def test_a_clip_that_barely_moves_is_still(self) -> None:
        rules = self.rules({"idle": (20, lambda f: {"Head": about_x(0.3 * math.sin(f))}), "move": (20, walk)})
        self.assertIn("UNIT-ANIM-STILL", rules)

    def test_two_roles_with_one_motion_are_the_same(self) -> None:
        findings, _facts = self.check({"move": (20, walk), "retreat": (20, walk), "attack": (20, strike)})
        same = [item for item in findings if item.rule == "UNIT-ANIM-SAME"]
        self.assertEqual(len(same), 1, findings)
        self.assertTrue(same[0].file.endswith("u_retreat.anim"))
        self.assertIn("u_move.anim", same[0].message)

    def test_old_calibration_files_skip_the_new_rules(self) -> None:
        limits = {key: value for key, value in LIMITS.items() if key not in ("seam_edges", "still_motion")}
        with tempfile.TemporaryDirectory() as folder:
            write_unit(Path(folder), "u", {"idle": (20, lambda f: {"Head": about_x(0.1 * f)})}, crotch_blend=0.0)
            findings, _facts = check_unit_files.check_files(Path(folder), None, None, limits=limits)
        self.assertFalse({item.rule for item in findings} & {"UNIT-SEAM", "UNIT-ANIM-STILL"})


class SharedClips(unittest.TestCase):
    def shared(self, first_clips, second_clips, reskins=()):
        with tempfile.TemporaryDirectory() as root:
            units = Path(root) / "gfx" / "models" / "units"
            write_unit(units / "alpha", "alpha", first_clips)
            write_unit(units / "beta", "beta", second_clips)
            return check_unit_files.check_shared_clips(units / "alpha", units, reskins=reskins)

    def test_one_clip_on_two_units_is_shared(self) -> None:
        findings = self.shared({"move": (20, walk)}, {"move": (20, walk), "attack": (20, strike)})
        self.assertEqual([item.rule for item in findings], ["UNIT-ANIM-SHARED"])
        self.assertIn("beta/beta_move.anim", findings[0].message)

    def test_a_retimed_copy_is_still_shared(self) -> None:
        findings = self.shared({"move": (20, walk)}, {"move": (40, lambda f: walk(f / 2))})
        self.assertEqual([item.rule for item in findings], ["UNIT-ANIM-SHARED"])

    def test_different_clips_are_not_shared(self) -> None:
        self.assertEqual(self.shared({"move": (20, walk)}, {"attack": (20, strike)}), [])

    def test_a_declared_reskin_may_share(self) -> None:
        self.assertEqual(self.shared({"move": (20, walk)}, {"move": (20, walk)}, reskins=["beta"]), [])

    def test_the_command_compares_with_the_mod_units(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            units = Path(root) / "gfx" / "models" / "units"
            write_unit(units / "alpha", "alpha", {"move": (20, walk)})
            write_unit(units / "beta", "beta", {"move": (20, walk)})
            with contextlib.redirect_stdout(io.StringIO()) as output:
                code = check_unit_files.main([str(units / "alpha"), "--compare-units", str(units)])
        self.assertIn("UNIT-ANIM-SHARED", output.getvalue())
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
