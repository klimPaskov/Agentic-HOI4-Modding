"""UNIT-LOOSE-PART: every part not joined to the body is skinned and stays attached in every frame."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

import check_unit_files
import test_motion_checks as legged
from lib import pdx_deform, pdx_motion

LIMITS = {**legged.LIMITS, "loose_gap": 0.0197}


def cube(centre, size, skin):
    """A closed cube as (vertices with skin, triangles with local indices)."""

    x, y, z = centre
    h = size / 2
    points = [(x + dx, y + dy, z + dz) for dx in (-h, h) for dy in (-h, h) for dz in (-h, h)]
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return [(p, skin) for p in points], [(a, b, c) for a, b, c, _d in quads] + [(a, c, d) for a, _b, c, d in quads]


def connected_body():
    """The legged unit as one surface: both legs and the torso meet a ribbon across the hips."""

    vertices, triangles = [], []
    for side, x in (("Left", 0.15), ("Right", -0.15)):
        leg = [(x, 0.0, 0.0), (x, 0.08, 0.0), (x, 0.5, 0.0), (x, 0.95, 0.0)]
        legged.ribbon(leg, [[(f"{side}Foot", 1.0)], [(f"{side}Foot", 1.0)], [(f"{side}Leg", 1.0)], [(f"{side}UpLeg", 1.0)]], vertices, triangles)
    legged.ribbon([(0.0, 0.95, 0.0), (0.0, 1.3, 0.0), (0.0, 1.8, 0.0)], [[("Hips", 1.0)], [("Spine", 1.0)], [("Head", 1.0)]], vertices, triangles)
    # The hip bar: its lower row lands on the legs' and the torso's top and bottom vertices, which weld.
    start = len(vertices)
    xs = (-0.18, -0.12, -0.03, 0.03, 0.12, 0.18)
    for x in xs:
        vertices.append(((x, 0.95, 0.0), [("Hips", 1.0)]))
        vertices.append(((x, 1.0, 0.0), [("Hips", 1.0)]))
    for step in range(len(xs) - 1):
        a, b, c, d = start + 2 * step, start + 2 * step + 1, start + 2 * step + 2, start + 2 * step + 3
        triangles += [(a, c, d), (a, d, b)]
    return vertices, triangles


def write_unit(folder: Path, extra, collision=None) -> None:
    """The connected unit plus extra cubes in its own stream; `collision` adds a selection box shape."""

    vertices, triangles = connected_body()
    for verts, tris in extra:
        offset = len(vertices)
        vertices += verts
        triangles += [(a + offset, b + offset, c + offset) for a, b, c in tris]
    folder.mkdir(parents=True, exist_ok=True)
    legged.write_mesh(folder / "u.mesh", vertices, triangles)
    if collision is not None:
        # Append a second shape whose material is the game's `Collision` shader (no skin).
        points, tris = collision
        data = (folder / "u.mesh").read_bytes()
        shape = legged._obj("collision_box", 2) + legged._obj("mesh", 3)
        shape += legged._prop("p", "f", [float(v) for p, _skin in points for v in p])
        shape += legged._prop("tri", "i", [int(i) for t in tris for i in t])
        shape += legged._obj("material", 4) + legged._prop("shader", "s", ["Collision"])
        (folder / "u.mesh").write_bytes(data + shape)
    legged.write_anim(folder / "u_move.anim", 20, legged.walk)


def findings(extra, collision=None):
    with tempfile.TemporaryDirectory() as folder:
        write_unit(Path(folder), extra, collision)
        found, facts = check_unit_files.check_files(Path(folder), None, None, limits=LIMITS)
    return [item for item in found if item.rule == "UNIT-LOOSE-PART"], facts


class LooseParts(unittest.TestCase):
    def test_a_part_resting_on_the_hips_and_weighted_to_them_passes(self) -> None:
        loose, facts = findings([cube((0.0, 1.0, 0.06), 0.1, [("Hips", 1.0)])])
        self.assertEqual(loose, [])
        self.assertEqual(len(facts["motion"]["u.mesh"]["loose_parts"]), 1)

    def test_a_part_on_the_knee_weighted_to_the_head_drifts_off(self) -> None:
        loose, _facts = findings([cube((0.15, 0.5, 0.04), 0.06, [("Head", 1.0)])])
        self.assertEqual(len(loose), 1)
        self.assertIn("drift off the body", loose[0].message)
        self.assertIn("u_move.anim", loose[0].message)

    def test_a_part_floating_beside_the_body_fails_at_rest(self) -> None:
        loose, _facts = findings([cube((0.6, 1.2, 0.0), 0.08, [("Spine", 1.0)])])
        self.assertEqual(len(loose), 1)
        self.assertIn("float apart from the body at rest", loose[0].message)

    def test_an_unskinned_part_fails(self) -> None:
        loose, _facts = findings([cube((0.0, 1.0, 0.06), 0.1, [])])
        self.assertTrue(any("no skin weight" in item.message for item in loose))

    def test_many_attached_parts_are_fine(self) -> None:
        plates = [cube((0.0, 1.05 + 0.05 * k, 0.05), 0.04, [("Spine", 1.0)]) for k in range(6)]
        loose, facts = findings(plates)
        self.assertEqual(loose, [])
        self.assertEqual(len(facts["motion"]["u.mesh"]["loose_parts"]), 6)

    def test_the_archer_case_ninety_plates_on_the_body_pass(self) -> None:
        # A smart-topology archer welds to 96 parts: a body and many small plates, all skinned and resting on it.
        plates = [cube((0.0, 1.0 + 0.008 * k, 0.05), 0.02, [("Spine" if k % 2 else "Hips", 1.0)]) for k in range(45)]
        plates += [cube((0.15, 0.5 + 0.009 * k, 0.04), 0.02, [("LeftLeg" if k < 22 else "LeftUpLeg", 1.0)]) for k in range(45)]
        loose, facts = findings(plates)
        self.assertEqual(loose, [])
        self.assertEqual(len(facts["motion"]["u.mesh"]["loose_parts"]), 10)  # the facts keep the ten farthest

    def test_the_selection_box_is_not_a_loose_part(self) -> None:
        box = cube((0.0, 0.9, 0.0), 1.8, [])
        loose, facts = findings([], collision=box)
        self.assertEqual(loose, [])
        self.assertEqual(facts["motion"]["u.mesh"]["loose_parts"], [])

    def test_collision_shapes_are_marked_when_loading(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            write_unit(Path(folder), [], collision=cube((0.0, 0.9, 0.0), 1.8, []))
            mesh = pdx_deform.load_mesh(Path(folder) / "u.mesh")
        self.assertEqual(int(mesh.collision.sum()), 8)
        self.assertEqual(pdx_motion.loose_parts(mesh, {}), [])


if __name__ == "__main__":
    unittest.main()
