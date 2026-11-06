"""The free mesh repair, end to end in Blender on a small synthetic unit. Skipped where Blender with io_pdx_mesh is not installed (CI)."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

import repair_unit
from lib import pdx_binary, pdx_deform
from test_deformation_checks import BONES, _obj, _prop, write_anim


def blender_available() -> bool:
    try:
        return repair_unit.find_blender().exists()
    except Exception:  # noqa: BLE001 - any discovery failure means no Blender here
        return False


def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float, offset: int):
    """A closed box, wound outward, as 8 points and 12 triangles."""

    points = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    triangles = [(offset + a, offset + b, offset + c) for a, b, c, d in quads] + [(offset + a, offset + c, offset + d) for a, b, c, d in quads]
    return points, triangles


def fused_unit(path: Path) -> None:
    """Two hand boxes joined by a sheet (the fusion), with one triangle of the left box flipped."""

    left, left_tris = box(-2.2, -1.8, 0.9, 1.3, -0.2, 0.2, 0)
    right, right_tris = box(1.8, 2.2, 0.9, 1.3, -0.2, 0.2, 8)
    a, b, c = left_tris[0]
    left_tris[0] = (a, c, b)
    # The sheet joins the inner faces of the two boxes: vertices 4..7 of the left box (x = -1.8)
    # to vertices 0..3 of the right box (x = 1.8).
    sheet = [(4, 8, 9), (4, 9, 5)]
    positions = left + right
    triangles = left_tris + right_tris + sheet
    bones = [2] * 8 + [4] * 8  # HandL, HandR
    normals = []
    for x, _y, _z in positions:
        normals += [1.0 if x > 0 else -1.0, 0.0, 0.0]
    data = b"@@b@" + _obj("object", 1) + _obj("unit", 2) + _obj("mesh", 3)
    data += _prop("p", "f", [float(v) for p in positions for v in p])
    data += _prop("n", "f", normals)
    data += _prop("u0", "f", [0.5, 0.5] * len(positions))
    data += _prop("tri", "i", [int(i) for t in triangles for i in t])
    data += _obj("aabb", 4) + _prop("min", "f", [-2.2, 0.9, -0.2]) + _prop("max", "f", [2.2, 1.3, 0.2])
    data += _obj("material", 4) + _prop("shader", "s", ["PdxMeshAdvanced"]) + _prop("diff", "s", ["unit_diffuse.dds"])
    ix, w = [], []
    for bone in bones:
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


@unittest.skipUnless(blender_available(), "Blender with io_pdx_mesh is not installed here")
class RepairInBlender(unittest.TestCase):
    def test_cuts_the_fusion_fixes_the_winding_and_keeps_the_skeleton(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            unit = Path(folder) / "unit"
            unit.mkdir()
            fused_unit(unit / "u.mesh")
            write_anim(unit / "u_idle.anim", 4, lambda frame: {"HandR": ((1.0 + 0.5 * frame, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0))})
            before = pdx_deform.load_mesh(unit / "u.mesh")
            self.assertGreater(pdx_deform.bridge_edges(before).edges, 0)
            self.assertGreater(pdx_deform.surface_report(before).winding_flips, 0)
            out = Path(folder) / "repair"
            with redirect_stdout(io.StringIO()):
                repair_unit.main([str(unit), "--out", str(out), "--repairs", "winding", "bridges"])
            report = json.loads((out / "repair_report.json").read_text(encoding="utf-8"))
            changed = next(iter(report["blender"]["objects"].values()))
            self.assertGreater(changed["bridge_faces_removed"], 0)
            self.assertGreaterEqual(changed["faces_flipped"], 1)
            after_path = out / "files" / "u.mesh"
            after = pdx_deform.load_mesh(after_path)
            surface = pdx_deform.surface_report(after)
            self.assertEqual(pdx_deform.bridge_edges(after).edges, 0)
            self.assertEqual(surface.winding_flips, 0)
            self.assertEqual(surface.open_edges, 0, "the cut must be capped on both sides")
            self.assertEqual(surface.parts, 2)
            self.assertEqual(pdx_binary.summarize_mesh(pdx_binary.read(after_path)).bones, [name for name, _p, _x in BONES])
            # The original clip still plays on the repaired mesh, now without stretch.
            clip = pdx_deform.deformation_report(after, pdx_deform.load_anim(out / "files" / "u_idle.anim"))
            self.assertEqual(clip.stretched_edges, 0)

    def test_a_join_inside_one_skin_is_kept_as_a_weight_seam(self) -> None:
        # The arm strip runs hand to hand through the arms and root, and one extra triangle joins
        # the hands' own strip vertices directly. Cutting it would open the skin, not separate parts.
        from test_deformation_checks import two_arm_strip, write_mesh

        positions, triangles, bones = two_arm_strip()
        triangles = triangles + [(0, 4, 9)]
        with tempfile.TemporaryDirectory() as folder:
            unit = Path(folder) / "unit"
            unit.mkdir()
            write_mesh(unit / "u.mesh", positions, triangles, bones)
            out = Path(folder) / "repair"
            with redirect_stdout(io.StringIO()):
                repair_unit.main([str(unit), "--out", str(out), "--repairs", "bridges"])
            changed = next(iter(json.loads((out / "repair_report.json").read_text(encoding="utf-8"))["blender"]["objects"].values()))
        self.assertEqual(changed["bridge_faces_removed"], 0)
        self.assertEqual(changed["weight_seams"], {"HandL-HandR": 2})

    def test_a_crotch_seam_is_blended_until_the_rule_passes(self) -> None:
        import test_motion_checks as legged
        from lib import pdx_motion

        with tempfile.TemporaryDirectory() as folder:
            unit = Path(folder) / "unit"
            legged.write_unit(unit, "u", {"move": (20, legged.walk)}, crotch_blend=0.0)
            self.assertGreater(pdx_motion.seam_edges(pdx_deform.load_mesh(unit / "u.mesh")).edges, 0)
            out = Path(folder) / "repair"
            with redirect_stdout(io.StringIO()):
                repair_unit.main([str(unit), "--out", str(out), "--repairs", "weights"])
            changed = next(iter(json.loads((out / "repair_report.json").read_text(encoding="utf-8"))["blender"]["objects"].values()))
            after = pdx_deform.load_mesh(out / "files" / "u.mesh")
        self.assertGreater(changed["leg_seam_edges"], 0)
        self.assertEqual(pdx_motion.seam_edges(after).edges, 0)


class RepairRequest(unittest.TestCase):
    def test_the_request_names_the_leg_seams(self) -> None:
        import test_motion_checks as legged

        with tempfile.TemporaryDirectory() as folder:
            legged.write_unit(Path(folder), "u", {}, crotch_blend=0.0)
            self.assertEqual(repair_unit.leg_seam_pairs(Path(folder) / "u.mesh"), [["LeftUpLeg", "RightUpLeg"]])


if __name__ == "__main__":
    unittest.main()
