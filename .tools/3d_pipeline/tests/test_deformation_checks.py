"""The surface and deformation rules of the unit checker, on small synthetic `.mesh` and `.anim` files."""

from __future__ import annotations

import math
import struct
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import numpy as np

import check_unit_files
from lib import pdx_deform

# Limits as tight as a clean model: nothing open, flipped, bridged, stretched or off the ground.
STRICT = {
    "largest_open_loop": 0,
    "open_edge_share": 0.0,
    "winding_flips": 0,
    "inside_out_triangles": 0,
    "bridge_edges": 0,
    "stretched_share": 0.0,
    "squashed_share": 0.0,
    "worst_stretch_share": 0.05,
    "sink": 0.01,
    "death_sink": 0.01,
    "hover": 0.01,
    "seam_edges": 0,
    "knee_backward": 0.0,
    "still_motion": 0.0,
    "turn_per_frame": 180.0,
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


# A skeleton with two arms: Root -> ArmL -> HandL and Root -> ArmR -> HandR (Y up).
BONES = [("Root", -1, (0, 1, 0)), ("ArmL", 0, (-1, 1, 0)), ("HandL", 1, (-2, 1, 0)), ("ArmR", 0, (1, 1, 0)), ("HandR", 3, (2, 1, 0))]


def write_mesh(path: Path, positions, triangles, bone_of_vertex=None) -> None:
    data = b"@@b@" + _obj("object", 1) + _obj("unit", 2) + _obj("mesh", 3)
    data += _prop("p", "f", [float(v) for p in positions for v in p])
    data += _prop("tri", "i", [int(i) for t in triangles for i in t])
    data += _obj("material", 4) + _prop("shader", "s", ["PdxMeshAdvanced"])
    if bone_of_vertex is not None:
        ix, w = [], []
        for bone in bone_of_vertex:
            ix += [bone, -1, -1, -1]
            w += [1.0, 0.0, 0.0, 0.0]
        data += _obj("skin", 4) + _prop("bones", "i", [4]) + _prop("ix", "i", ix) + _prop("w", "f", w)
        data += _obj("skeleton", 3)
        for index, (name, parent, (x, y, z)) in enumerate(BONES):
            data += _obj(name, 4) + _prop("ix", "i", [index])
            if parent >= 0:
                data += _prop("pa", "i", [parent])
            data += _prop("tx", "f", [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, -x, -y, -z])
    path.write_bytes(data)


def write_anim(path: Path, frames: int, pose, fps: float = 30.0) -> None:
    """`pose(frame)` returns {bone: (local translation, quaternion x y z w)} for the moving bones."""

    data = b"@@b@" + _obj("info", 1) + _prop("fps", "f", [fps]) + _prop("sa", "i", [frames]) + _prop("j", "i", [len(BONES)])
    rest_local = {}
    for name, parent, position in BONES:
        parent_position = BONES[parent][2] if parent >= 0 else (0, 0, 0)
        rest_local[name] = [position[i] - parent_position[i] for i in range(3)]
    for name, _parent, _position in BONES:
        data += _obj(name, 2) + _prop("sa", "s", ["tq"])
        data += _prop("t", "f", rest_local[name]) + _prop("q", "f", [0.0, 0.0, 0.0, 1.0]) + _prop("s", "f", [1.0])
    t, q = [], []
    for frame in range(frames):
        moved = pose(frame)
        for name, _parent, _position in BONES:
            translation, rotation = moved.get(name, (rest_local[name], (0.0, 0.0, 0.0, 1.0)))
            q += list(rotation)
            t += list(translation)
    data += _obj("samples", 1) + _prop("q", "f", q) + _prop("t", "f", t)
    path.write_bytes(data)


def tetrahedron(offset=(0.0, 0.0, 0.0), size=0.4):
    x, y, z = offset
    points = [(x, y, z), (x + size, y, z), (x, y + size, z), (x, y, z + size)]
    # Outward winding (counter-clockwise seen from outside).
    return points, [(0, 2, 1), (0, 1, 3), (0, 3, 2), (1, 2, 3)]


def two_arm_strip():
    """A strip of quads from the left hand to the right hand, at the arm bones' height."""

    xs = [-2.0, -1.0, 0.0, 1.0, 2.0]
    positions = [(x, 1.0, 0.0) for x in xs] + [(x, 1.2, 0.0) for x in xs]
    triangles = []
    for i in range(4):
        a, b, c, d = i, i + 1, i + 5, i + 6
        triangles += [(a, b, d), (a, d, c)]
    bones = [2, 1, 0, 3, 4] * 2  # HandL, ArmL, Root, ArmR, HandR
    return positions, triangles, bones


class SurfaceRules(unittest.TestCase):
    def check(self, positions, triangles):
        with tempfile.TemporaryDirectory() as folder:
            write_mesh(Path(folder) / "u.mesh", positions, triangles)
            findings, facts = check_unit_files.check_files(Path(folder), None, None, limits=STRICT)
        return {item.rule for item in findings}, facts

    def test_a_closed_outward_part_passes(self) -> None:
        rules, facts = self.check(*tetrahedron())
        self.assertFalse(rules & {"UNIT-HOLE", "UNIT-WINDING", "UNIT-INSIDE-OUT"})
        self.assertEqual(facts["surface"]["u.mesh"]["open_edges"], 0)

    def test_a_missing_triangle_is_a_hole(self) -> None:
        points, triangles = tetrahedron()
        rules, facts = self.check(points, triangles[:3])
        self.assertIn("UNIT-HOLE", rules)
        self.assertEqual(facts["surface"]["u.mesh"]["open_loops"], [3])

    def test_a_flipped_triangle_is_found(self) -> None:
        points, triangles = tetrahedron()
        a, b, c = triangles[3]
        rules, _ = self.check(points, triangles[:3] + [(a, c, b)])
        self.assertIn("UNIT-WINDING", rules)

    def test_an_inside_out_part_is_found(self) -> None:
        points, triangles = tetrahedron()
        rules, _ = self.check(points, [(a, c, b) for a, b, c in triangles])
        self.assertIn("UNIT-INSIDE-OUT", rules)
        self.assertNotIn("UNIT-WINDING", rules)

    def test_split_vertices_are_welded(self) -> None:
        # The same tetrahedron with every triangle on its own vertices (split normals) is still closed.
        points, triangles = tetrahedron()
        split_points = [points[i] for t in triangles for i in t]
        split_triangles = [(3 * k, 3 * k + 1, 3 * k + 2) for k in range(len(triangles))]
        rules, _ = self.check(split_points, split_triangles)
        self.assertNotIn("UNIT-HOLE", rules)


class BridgeRule(unittest.TestCase):
    def bridges(self, positions, triangles, bones):
        with tempfile.TemporaryDirectory() as folder:
            write_mesh(Path(folder) / "u.mesh", positions, triangles, bones)
            report = pdx_deform.bridge_edges(pdx_deform.load_mesh(Path(folder) / "u.mesh"))
            findings, _ = check_unit_files.check_files(Path(folder), None, None, limits=STRICT)
        return report, {item.rule for item in findings}

    def test_a_sheet_joining_both_hands_is_a_bridge(self) -> None:
        # One quad whose left edge follows HandL and right edge HandR, as when a hand is fused to the other side.
        positions = [(-2.0, 1.0, 0.0), (2.0, 1.0, 0.0), (-2.0, 1.2, 0.0), (2.0, 1.2, 0.0)]
        report, rules = self.bridges(positions, [(0, 1, 3), (0, 3, 2)], [2, 4, 2, 4])
        self.assertEqual(report.pairs, {"HandL-HandR": 3})  # bottom, top and diagonal
        self.assertIn("UNIT-BRIDGE", rules)

    def test_a_strip_through_the_joints_is_not_a_bridge(self) -> None:
        # Every edge of the arm strip joins neighbouring bones (at most two parent steps).
        report, rules = self.bridges(*two_arm_strip())
        self.assertEqual(report.edges, 0)
        self.assertNotIn("UNIT-BRIDGE", rules)

    def test_a_blended_join_is_not_a_bridge(self) -> None:
        # The same hand-to-hand quad, but the right vertices carry 30 % HandL: a soft join that bends instead of tearing.
        with tempfile.TemporaryDirectory() as folder:
            positions = [(-2.0, 1.0, 0.0), (2.0, 1.0, 0.0), (-2.0, 1.2, 0.0), (2.0, 1.2, 0.0)]
            write_mesh(Path(folder) / "u.mesh", positions, [(0, 1, 3), (0, 3, 2)], [2, 4, 2, 4])
            mesh = pdx_deform.load_mesh(Path(folder) / "u.mesh")
        mesh.joints[[1, 3], 1] = 2
        mesh.weights[[1, 3]] = [0.7, 0.3, 0.0, 0.0]
        self.assertEqual(pdx_deform.bridge_edges(mesh).edges, 0)

    def test_hops_follow_the_hierarchy(self) -> None:
        hops = pdx_deform.bone_hops([parent for _name, parent, _p in BONES])
        self.assertEqual(hops[2, 4], 4)  # HandL to HandR through the root
        self.assertEqual(hops[1, 2], 1)
        self.assertEqual(hops[0, 0], 0)


class DeformationRules(unittest.TestCase):
    def run_clip(self, pose, frames=8):
        positions, triangles, bones = two_arm_strip()
        with tempfile.TemporaryDirectory() as folder:
            write_mesh(Path(folder) / "u.mesh", positions, triangles, bones)
            write_anim(Path(folder) / "u_idle.anim", frames, pose)
            mesh = pdx_deform.load_mesh(Path(folder) / "u.mesh")
            report = pdx_deform.deformation_report(mesh, pdx_deform.load_anim(Path(folder) / "u_idle.anim"))
            limits = dict(STRICT, bridge_edges=1000)
            findings, _ = check_unit_files.check_files(Path(folder), None, None, limits=limits)
        return report, {item.rule for item in findings}

    def test_the_rest_pose_does_not_deform(self) -> None:
        report, rules = self.run_clip(lambda frame: {})
        self.assertEqual(report.stretched_edges, 0)
        self.assertAlmostEqual(report.lowest, 0.0, places=5)
        self.assertFalse(rules & {"UNIT-ANIM-STRETCH", "UNIT-ANIM-GROUND"})

    def test_pulling_a_hand_away_stretches_the_strip(self) -> None:
        # HandR slides 1.5 units further out: the edges into it stretch.
        report, rules = self.run_clip(lambda frame: {"HandR": ((1.0 + 1.5 * frame / 7, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0))})
        self.assertGreater(report.stretched_edges, 0)
        self.assertAlmostEqual(report.worst_stretch_share, 1.5 / 0.2, places=3)  # 1.5 units of growth on a strip 0.2 tall
        self.assertIn("HandR", " ".join(report.worst_pairs))
        self.assertIn("UNIT-ANIM-STRETCH", rules)

    def test_a_rotation_skins_through_the_hierarchy(self) -> None:
        # ArmR turns 90 degrees about Z: HandR swings from (2, 1) to (1, 2), so its vertices rise one unit.
        half = math.radians(90) / 2
        report, _rules = self.run_clip(lambda frame: {"ArmR": ((1.0, 0.0, 0.0), (0.0, 0.0, math.sin(half), math.cos(half)))})
        self.assertGreater(report.highest_lowest, -1e-6)
        positions, triangles, bones = two_arm_strip()
        with tempfile.TemporaryDirectory() as folder:
            write_mesh(Path(folder) / "u.mesh", positions, triangles, bones)
            write_anim(Path(folder) / "u_idle.anim", 1, lambda frame: {"ArmR": ((1.0, 0.0, 0.0), (0.0, 0.0, math.sin(half), math.cos(half)))})
            mesh = pdx_deform.load_mesh(Path(folder) / "u.mesh")
            matrices = pdx_deform.skinning_matrices(mesh, pdx_deform.load_anim(Path(folder) / "u_idle.anim"))
            moved = pdx_deform.skin(mesh, matrices[0])
        np.testing.assert_allclose(moved[4], (1.0, 2.0, 0.0), atol=1e-5)  # HandR's lower vertex

    def test_sinking_below_the_ground_is_found(self) -> None:
        report, rules = self.run_clip(lambda frame: {"Root": ((0.0, -0.3, 0.0), (0.0, 0.0, 0.0, 1.0))})
        self.assertLess(report.lowest, -0.5)
        self.assertEqual(report.lowest_frame, 0)
        self.assertIn("UNIT-ANIM-GROUND", rules)


class Calibration(unittest.TestCase):
    def test_the_shipped_calibration_has_every_limit(self) -> None:
        for group in ("organic", "vehicle", "air_naval"):
            limits = check_unit_files.load_calibration(group)
            self.assertIsNotNone(limits, "config/deformation_calibration.json is missing; run calibrate_deformation.py")
            # Loose parts are calibrated on a vanilla soldier and horse only, so only organic units have that limit.
            self.assertEqual(set(STRICT) | ({"loose_gap"} if group == "organic" else set()), set(limits))
        # Soldiers and animals get far tighter hole limits than vehicles with open panel backs.
        organic, vehicle = check_unit_files.load_calibration("organic"), check_unit_files.load_calibration("vehicle")
        self.assertLess(organic["open_edge_share"], vehicle["open_edge_share"])

    def test_without_calibration_the_rules_warn_and_skip(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            points, triangles = tetrahedron()
            write_mesh(Path(folder) / "u.mesh", points, triangles[:3])
            original = check_unit_files.CALIBRATION
            check_unit_files.CALIBRATION = Path(folder) / "missing.json"
            try:
                findings, _ = check_unit_files.check_files(Path(folder), None, None)
            finally:
                check_unit_files.CALIBRATION = original
        rules = {item.rule for item in findings}
        self.assertIn("UNIT-CALIBRATION-MISSING", rules)
        self.assertNotIn("UNIT-HOLE", rules)


if __name__ == "__main__":
    unittest.main()
