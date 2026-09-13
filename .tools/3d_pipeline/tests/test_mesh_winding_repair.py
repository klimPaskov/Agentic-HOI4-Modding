"""Pure orientation planner checks; actual Blender retention proof is separate."""
import ast
import importlib.util
from pathlib import Path
import unittest
import math

MODULE = Path(__file__).resolve().parents[1] / "adapter" / "mesh_winding_repair.py"
SPEC = importlib.util.spec_from_file_location("mesh_winding_repair", MODULE)
repair = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(repair)

POSITIONS = [(0.,0.,0.), (1.,0.,0.), (0.,1.,0.), (0.,0.,1.)]
FACES = [(0,2,1), (0,1,3), (0,3,2), (1,2,3)]


class WindingPlanner(unittest.TestCase):
    def test_outward_closed_tetrahedron_is_unchanged(self):
        result = repair.plan_consistent_outward_winding(POSITIONS, FACES)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["flip_face_indices"], [])
        self.assertAlmostEqual(result["components"][0]["final_virtual_closed_volume"], 1/6)

    def test_every_corrupt_face_pattern_repairs_to_same_outward_faces(self):
        for mask in range(16):
            faces = [tuple(reversed(face)) if mask & (1<<i) else face for i, face in enumerate(FACES)]
            result = repair.plan_consistent_outward_winding(POSITIONS, faces)
            self.assertEqual(result["status"], "pass")
            self.assertEqual(result["flip_face_indices"], [i for i in range(4) if mask & (1<<i)])

    def test_exact_seam_duplicates_are_only_diagnostic(self):
        positions = [POSITIONS[v] for face in FACES for v in face]
        faces = [tuple(range(i, i+3)) for i in range(0,12,3)]
        result = repair.plan_consistent_outward_winding(positions, faces)
        self.assertEqual((result["vertices"], result["exact_positional_vertices"]), (12,4))
        self.assertEqual(result["flip_face_indices"], [])
        self.assertEqual(len(positions),12)
        indexed = repair.plan_consistent_outward_winding(positions, faces, adjacency_mode="source_vertex_indices")
        self.assertEqual(len(indexed["components"]),4)
        self.assertEqual(indexed["status"],"blocked")

    def test_large_open_boundary_blocks_instead_of_arbitrary_inversion(self):
        result = repair.plan_consistent_outward_winding(POSITIONS, FACES[:-1])
        self.assertEqual(result["status"], "blocked")
        self.assertIn("virtual_cap_area_exceeds_0.5_percent_of_surface", result["components"][0]["ambiguous_reasons"])

    def test_planar_open_component_is_ambiguous(self):
        result = repair.plan_consistent_outward_winding(POSITIONS, [FACES[0]])
        self.assertEqual(result["status"], "blocked")
        self.assertIn("zero_or_numerically_ambiguous_enclosed_volume", result["components"][0]["ambiguous_reasons"])

    def test_duplicate_degenerate_nonfinite_and_bad_indices_reject(self):
        for positions, faces in ((POSITIONS, FACES+[FACES[0]]), (POSITIONS, [(0,0,1)]), ([(float("nan"),0,0)]+POSITIONS[1:], FACES), (POSITIONS,[(0,1,True)]), (POSITIONS,[(0,1,99)])):
            with self.subTest(faces=faces), self.assertRaises(ValueError):
                repair.plan_consistent_outward_winding(positions,faces)

    def test_translation_does_not_change_orientation(self):
        result = repair.plan_consistent_outward_winding([(x+1000,y-2000,z+3000) for x,y,z in POSITIONS],FACES)
        self.assertEqual(result["flip_face_indices"], [])

    def test_mobius_strip_reports_orientation_conflict_without_mutation(self):
        positions = []
        for i in range(8):
            angle = 2*math.pi*i/8
            for width in (-0.2,0.2):
                positions.append(((1+width*math.cos(angle/2))*math.cos(angle), (1+width*math.cos(angle/2))*math.sin(angle), width*math.sin(angle/2)))
        faces = []
        for i in range(8):
            a,b = 2*i,2*i+1
            c,d = (2*(i+1),2*(i+1)+1) if i<7 else (1,0)
            faces.extend(((a,c,b),(b,c,d)))
        result = repair.plan_consistent_outward_winding(positions,faces)
        self.assertEqual(result["status"],"blocked")
        self.assertIn("component_is_not_coherently_orientable",result["components"][0]["ambiguous_reasons"])
        self.assertGreater(result["components"][0]["orientation_conflict_count"],0)

    def test_native_entry_never_welds_adds_deletes_or_disables_culling(self):
        source = MODULE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        function = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="repair_mesh_winding")
        calls = [ast.unparse(n.func) for n in ast.walk(function) if isinstance(n,ast.Call)]
        self.assertFalse(any("remove_doubles" in x or "from_pydata" in x or "bmesh" in x or "delete" in x for x in calls))
        self.assertIn("mesh.polygons[index].flip", calls)
        self.assertNotIn("use_backface_culling = False", source)


if __name__ == "__main__":
    unittest.main()
