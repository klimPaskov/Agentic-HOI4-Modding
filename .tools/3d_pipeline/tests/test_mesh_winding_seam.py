"""Pure tiny-seam contract and retained Temporal canonical-byte regression.

These tests do not import Blender or modify any model. Native RNA preservation
and saved/reopened deformation evidence are separate required acceptance gates.
"""
import ast
import importlib.util
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
MODULE = ROOT/".tools/3d_pipeline/adapter/mesh_winding_seam.py"
SPEC = importlib.util.spec_from_file_location("mesh_winding_seam", MODULE)
repair = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(repair)
POSITIONS = [(0.,0.,0.), (1.,0.,0.), (0.,1.,0.), (0.,0.,1.)]
FACES = [(0,2,1), (0,1,3), (0,3,2), (1,2,3)]


class SeamContract(unittest.TestCase):
    def test_volume_bound_for_closed_tetrahedron(self):
        flips, normals, proof = repair._orient_component(POSITIONS, FACES, list(range(4)))
        self.assertFalse(any(flips.values()))
        self.assertEqual(proof["cap_volume_absolute_upper_bound"], 0.)
        self.assertAlmostEqual(proof["closed_volume_interval"][0], 1/6)

    def test_orientation_corrects_all_corruption_patterns(self):
        for mask in range(16):
            faces = [tuple(reversed(f)) if mask & (1 << i) else f for i, f in enumerate(FACES)]
            flips, normals, proof = repair._orient_component(POSITIONS, faces, list(range(4)))
            inverted = proof["closed_volume_interval"][1] < 0
            self.assertEqual(sorted(i for i, f in flips.items() if f != inverted), [i for i in range(4) if mask & (1 << i)])

    def test_large_open_body_rejected(self):
        with self.assertRaisesRegex(ValueError, "0.5 percent"):
            repair.plan_seam_winding(POSITIONS, FACES, [3], [0,1,2])

    def test_bad_indices_and_reference_overlap_rejected(self):
        for selected, neighbors in (([3,3],[0]), ([True],[0]), ([4],[0]), ([3],[3])):
            with self.assertRaises(ValueError):
                repair.plan_seam_winding(POSITIONS, FACES, selected, neighbors)

    def test_nonfinite_and_invalid_vertex_indices_rejected(self):
        with self.assertRaises(ValueError):
            repair.plan_seam_winding([(float("nan"),0,0)]+POSITIONS[1:], FACES, [3], [0])
        with self.assertRaises(ValueError):
            repair.plan_seam_winding(POSITIONS, [(0,1,99)]+FACES[1:], [3], [0])

    def test_native_route_has_no_weld_caps_new_mesh_or_culling_shortcut(self):
        source = MODULE.read_text(encoding="utf-8")
        calls = [ast.unparse(n.func) for n in ast.walk(ast.parse(source)) if isinstance(n,ast.Call)]
        for forbidden in ("bmesh", "from_pydata", "remove_doubles", "bpy.data.meshes.new", "mesh.polygons.add", "mesh.vertices.remove"):
            self.assertFalse(any(forbidden in call for call in calls))
        self.assertIn("mesh.vertices.add", calls)
        self.assertIn("mesh.edges.add", calls)
        self.assertIn("mesh.polygons[index].flip", calls)
        self.assertNotIn("use_backface_culling = False", source)
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Call) and ast.unparse(node.func) == "bpy.ops.wm.open_mainfile":
                self.assertTrue(any(k.arg == "use_scripts" and isinstance(k.value, ast.Constant) and k.value.value is False for k in node.keywords))


if __name__ == "__main__":
    unittest.main()
