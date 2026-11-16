"""The shield held in the free hand: the grip rule on a crescent, the job's shield block in the intake and the pipeline, and the shield
checks on runtime files (a mesh and an animation in memory)."""

from __future__ import annotations

import argparse
import ast
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tripo"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import tripo_checks as TC
import tripo_intake
from lib import pdx_deform as P
from lib import tripo, tripo_shield as S


def turned(points: np.ndarray) -> np.ndarray:
    """The points turned 90 degrees about x and moved, as a model file may have them."""

    turn = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]])
    return points @ turn.T * 2.5 + np.array([3.0, -1.0, 0.5])


class GripRule(unittest.TestCase):
    def setUp(self) -> None:
        self.points = S.crescent()["vertices"]

    def test_the_outer_edge_is_the_side_the_middle_bows_to(self) -> None:
        grip = S.shield_grip(self.points)
        self.assertTrue(grip["bowed"])
        self.assertGreater(float(grip["axes"][:, 1] @ [-1.0, 0.0, 0.0]), 0.99)  # the crescent bows to -x
        self.assertGreater(float(abs(grip["axes"][:, 0] @ [0.0, 1.0, 0.0])), 0.99)  # its ends lie on the y axis

    def test_the_fist_closes_on_the_middle_of_the_inner_edge_just_inside_the_hollow(self) -> None:
        grip = S.shield_grip(self.points, share=0.65)
        self.assertAlmostEqual(float(grip["inner_edge"][1]), 0.5, delta=0.02)
        inner_x = -0.25 + 0.18  # the middle bows 0.25 to -x and is 0.18 wide
        self.assertAlmostEqual(float(grip["inner_edge"][0]), inner_x, delta=0.01)
        self.assertAlmostEqual(grip["radius"], S.GRIP_RADIUS_SHARE / 0.65, places=6)
        # the bar's centre is one radius off the edge, away from the outer edge: the shield reaches out of the fist across its width
        self.assertAlmostEqual(float((grip["grip"] - grip["inner_edge"]) @ grip["axes"][:, 1]), -grip["radius"], places=6)

    def test_the_rule_does_not_depend_on_how_the_file_is_turned_or_placed(self) -> None:
        plain, moved = S.shield_grip(self.points), S.shield_grip(turned(self.points))
        self.assertAlmostEqual(moved["length"], 2.5 * plain["length"], places=6)
        turn = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]])
        self.assertGreater(float(moved["axes"][:, 1] @ (turn @ plain["axes"][:, 1])), 0.99)
        self.assertTrue(np.allclose(moved["inner_edge"], turned(plain["inner_edge"][None])[0], atol=0.02))

    def test_the_end_with_the_larger_cross_section_is_the_head(self) -> None:
        points = self.points.copy()
        top = points[:, 1] > 0.85
        points[top, 0] = points[top, 0] * 2.0  # widen the end at y = 1
        grip = S.shield_grip(points)
        self.assertGreater(float(grip["axes"][:, 0] @ [0.0, 1.0, 0.0]), 0.99)
        self.assertGreater(float(S.shield_grip(points * [1.0, -1.0, 1.0])["axes"][:, 0] @ [0.0, -1.0, 0.0]), 0.99)

    def test_a_straight_shield_keeps_its_second_axis(self) -> None:
        bar = np.array([[x, y, z] for x in (-0.1, 0.1) for y in np.linspace(0, 1, 30) for z in (-0.02, 0.02)])
        grip = S.shield_grip(bar)
        self.assertFalse(grip["bowed"])
        self.assertGreater(float(abs(grip["axes"][:, 1] @ [1.0, 0.0, 0.0])), 0.99)

    def test_the_stand_in_is_a_closed_crescent_with_spikes_on_the_outer_edge(self) -> None:
        shape = S.crescent()
        vertices, triangles = shape["vertices"], shape["triangles"]
        self.assertTrue(np.isclose(np.ptp(vertices[:, 1]), 1.0, atol=0.03))
        self.assertTrue(int(triangles.max()) < len(vertices))
        spikes = vertices[-12:]
        self.assertTrue(bool((spikes[:, 0] < S.shield_grip(vertices)["inner_edge"][0]).all()))


class JobShieldBlock(unittest.TestCase):
    def spec(self, **block):
        return {"provider": "tripo", "tripo": {"roles": {"idle": "idle"}, **block}}

    def test_the_held_parts_are_the_weapon_then_the_shield_with_its_defaults(self) -> None:
        spec = self.spec(weapon={"part": "tripo_part_1", "bone": "Weapon", "release_roles": ["death"]}, shield={"release_roles": ["death"]})
        parts = tripo.held_parts(spec)
        self.assertEqual([(p["part"], p["bone"]) for p in parts], [("tripo_part_1", "Weapon"), ("tripo_part_2", "Shield")])
        self.assertEqual(tripo.released_bones(parts, "death"), ["Weapon", "Shield"])
        self.assertEqual(tripo.released_bones(parts, "idle"), [])
        self.assertEqual(tripo.held_bones(parts), ["Weapon", "Shield"])
        self.assertEqual(tripo.held_parts({"tripo": {"shield": {}}}), [])  # a Meshy job holds nothing here
        self.assertEqual(tripo.held_parts(self.spec(shield={"bone": "Buckler"}))[0]["bone"], "Buckler")

    def test_the_intake_binds_the_shield_as_a_second_rigid_part(self) -> None:
        import run_pilot
        from test_tripo_route import tripo_spec

        def pairs(**block):
            spec = run_pilot.prepare_spec(tripo_spec())
            spec["tripo"].update(block)
            command = tripo_intake.prepare_command(Path("blender.exe"), spec, {"rigged": Path("r.glb")}, Path("out"), Path("report.json"))
            return [command[i + 1] for i, item in enumerate(command) if item == "--rigid-part"]

        self.assertEqual(pairs(weapon={"part": "tripo_part_1", "bone": "Weapon"}, shield={}), ["tripo_part_1=Weapon", "tripo_part_2=Shield"])
        self.assertEqual(pairs(weapon={"part": "tripo_part_1", "bone": "Weapon"}), ["tripo_part_1=Weapon"])
        self.assertEqual(pairs(weapon=None, shield={"part": "tripo_part_1", "bone": "Shield"}), ["tripo_part_1=Shield"])

    def test_the_prepare_stage_keeps_the_shield_bone_within_the_bone_budget(self) -> None:
        source = (PIPELINE / "tripo" / "prepare_tripo_unit.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        values = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in ("OPTIONAL_BONES", "MAX_BONES"):
                values[node.targets[0].id] = ast.literal_eval(node.value)
        self.assertEqual(values["OPTIONAL_BONES"].get("Shield"), "Shield")
        kit_bones = 6 + 2 * 8  # Hips, the three spine bones, neck and Head; eight bones each side
        self.assertLessEqual(kit_bones + len(values["OPTIONAL_BONES"]), values["MAX_BONES"])


class StageUsesTheGripStage(unittest.TestCase):
    def test_the_grip_stage_runs_only_as_a_script_and_has_every_step_the_shield_stage_calls(self) -> None:
        grip = ast.parse((PIPELINE / "tripo" / "grip_weapon.py").read_text(encoding="utf-8"))
        guarded = [node for node in grip.body if isinstance(node, ast.If) and "__main__" in ast.unparse(node.test)]
        self.assertEqual(len(guarded), 1)
        self.assertFalse([node for node in grip.body if isinstance(node, ast.Try)])  # main() is not run on import
        defined = {node.name for node in grip.body if isinstance(node, ast.FunctionDef)}
        defined |= {target.id for node in grip.body if isinstance(node, ast.Assign) for target in node.targets if isinstance(target, ast.Name)}
        stage = ast.parse((PIPELINE / "tripo" / "shield_stage.py").read_text(encoding="utf-8"))
        called = {node.attr for node in ast.walk(stage) if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "GW"}
        self.assertTrue(called <= defined, called - defined)


CUBE = np.array([[x, y, z] for x in (-0.5, 0.5) for y in (-0.5, 0.5) for z in (-0.5, 0.5)], float)
CUBE_TRIANGLES = np.array([
    [0, 1, 3], [0, 3, 2], [4, 6, 7], [4, 7, 5], [0, 4, 5], [0, 5, 1],
    [2, 3, 7], [2, 7, 6], [0, 2, 6], [0, 6, 4], [1, 5, 7], [1, 7, 3],
])
SHIELD_JOINT = np.array([-1.2, 0.0, 0.0])
WEAPON_JOINT = np.array([1.2, 0.0, 0.0])


def held_mesh() -> P.SkinnedMesh:
    """A box body on `Root`, a vertical weapon stick on `Weapon` (joint at x = 1.2) and a shield plate on `Shield` (joint at x = -1.2),
    the plate reaching from 0.15 to 0.45 beyond its joint so its grip zone leaves most of it judged. One unit tall."""

    stick = np.array([[1.2, y, 0.0] for y in np.linspace(-0.5, 0.5, 120)])
    plate = np.array([[-1.2 - d, y, z] for d in np.linspace(0.15, 0.45, 8) for y in np.linspace(-0.4, 0.4, 10) for z in (-0.02, 0.02)])
    positions = np.concatenate([CUBE, stick, plate])
    joints = np.full((len(positions), 4), -1)
    weights = np.zeros((len(positions), 4))
    joints[: len(CUBE), 0], joints[len(CUBE) : len(CUBE) + len(stick), 0], joints[len(CUBE) + len(stick) :, 0] = 0, 1, 2
    weights[:, 0] = 1.0
    inverse = np.stack([np.eye(4)] * 3)
    inverse[1, :3, 3], inverse[2, :3, 3] = -WEAPON_JOINT, -SHIELD_JOINT
    return P.SkinnedMesh(positions=positions, triangles=CUBE_TRIANGLES, joints=joints, weights=weights, bones=["Root", "Weapon", "Shield"],
                         parents=[-1, 0, 0], inverse_bind=inverse)


def held_anim(shield_t, weapon_t=None) -> P.Animation:
    frames = len(shield_t)
    rest = {"t": np.zeros((frames, 3)), "q": np.tile([0.0, 0.0, 0.0, 1.0], (frames, 1)), "s": np.ones(frames)}
    weapon = {"t": np.asarray(weapon_t if weapon_t is not None else [WEAPON_JOINT] * frames, float), "q": rest["q"].copy(), "s": rest["s"].copy()}
    shield = {"t": np.asarray(shield_t, float), "q": rest["q"].copy(), "s": rest["s"].copy()}
    return P.Animation(fps=30.0, frames=frames, channels={"Root": rest, "Weapon": weapon, "Shield": shield})


class ShieldOnRuntimeFiles(unittest.TestCase):
    def setUp(self) -> None:
        self.mesh = held_mesh()

    def test_a_shield_that_stays_clear_passes(self) -> None:
        findings, numbers = TC.shield_runtime_findings(self.mesh, {"u_idle": held_anim([SHIELD_JOINT] * 4)}, "Shield", weapon_bone="Weapon")
        self.assertEqual(findings, [])
        self.assertEqual(numbers["u_idle"]["frames_over"], 0)

    def test_a_shield_through_the_body_fails_with_its_own_rule(self) -> None:
        inside = SHIELD_JOINT + [1.5, 0.0, 0.0]  # the plate now spans x 0.15 to 0.45, inside the box
        findings, numbers = TC.shield_runtime_findings(self.mesh, {"u_attack": held_anim([SHIELD_JOINT, inside, inside])}, "Shield", weapon_bone="Weapon")
        self.assertEqual([f["rule"] for f in findings], ["TRIPO-SHIELD-IN-BODY"])
        self.assertEqual(findings[0]["frames"], [1, 2])
        self.assertIn("the shield is more than", findings[0]["message"])

    def test_a_shield_under_the_ground_fails_with_its_own_rule(self) -> None:
        low = SHIELD_JOINT + [0.0, -2.0, 0.0]
        findings, _numbers = TC.shield_runtime_findings(self.mesh, {"u_death": held_anim([SHIELD_JOINT, low])}, "Shield", weapon_bone="Weapon")
        self.assertEqual([f["rule"] for f in findings], ["TRIPO-SHIELD-BELOW-GROUND"])

    def test_the_weapon_is_not_body_to_the_shield_and_the_shield_not_body_to_the_weapon(self) -> None:
        # The shield sunk a unit and the weapon two: were the weapon body, the body's lowest point would be the weapon's and the shield
        # would not count as under the ground. The same frames the other way round for the weapon's check.
        anim = held_anim([SHIELD_JOINT + [0.0, -1.0, 0.0]] * 2, [WEAPON_JOINT + [0.0, -2.0, 0.0]] * 2)
        findings, _numbers = TC.shield_runtime_findings(self.mesh, {"u_idle": anim}, "Shield", weapon_bone="Weapon")
        self.assertEqual([f["rule"] for f in findings], ["TRIPO-SHIELD-BELOW-GROUND"])
        swapped = held_anim([SHIELD_JOINT + [0.0, -2.0, 0.0]] * 2, [WEAPON_JOINT + [0.0, -1.0, 0.0]] * 2)
        findings, _numbers = TC.weapon_runtime_findings(self.mesh, {"u_idle": swapped}, "Weapon", other_bones=("Shield",))
        self.assertEqual([f["rule"] for f in findings], ["TRIPO-WEAPON-BELOW-GROUND"])
        held, _triangles, _indices, _free, _c = TC.weapon_split(self.mesh, "Shield", ("Weapon",))
        self.assertEqual(int(held.sum()), 120 + 160)

    def test_the_grip_check_reads_the_hand_that_holds_the_weapon_and_survives_a_haft_it_cannot_measure(self) -> None:
        mesh = held_mesh()
        mesh.bones[0] = "LeftHand"  # the weapon's bone is a child of the left hand, as in a left-handed unit
        self.assertEqual(TC.holding_hand(mesh, "Weapon"), "LeftHand")
        self.assertEqual(TC.holding_hand(mesh, "Sword"), "RightHand")
        findings, numbers = TC.grip_runtime_findings(mesh, "Weapon")
        self.assertEqual(numbers["hand"], "LeftHand")
        self.assertTrue(findings == [] or findings[0]["rule"] == "TRIPO-GRIP-ENCLOSURE")
        sparse = held_mesh()
        sparse.bones[0] = "LeftHand"
        stick = slice(len(CUBE), len(CUBE) + 120)
        sparse.positions[stick, 1] = np.where(np.arange(120) < 60, -0.5, 0.5)  # a haft with vertices only at its two ends
        findings, numbers = TC.grip_runtime_findings(sparse, "Weapon")
        self.assertEqual(findings, [])
        self.assertIn("unmeasured", numbers)

    def test_the_shield_bone_comes_from_the_flag_or_the_job(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            config = Path(folder) / "jobs.json"
            config.write_text(json.dumps({"jobs": {"u": {"tripo": {"shield": {"release_roles": ["death"]}}}, "v": {"tripo": {}}}}), encoding="utf-8")
            args = argparse.Namespace(shield_bone="", jobs_config=config, slug="u")
            self.assertEqual(TC.shield_bone(args), "Shield")
            self.assertEqual(TC.shield_bone(argparse.Namespace(shield_bone="", jobs_config=config, slug="v")), "")
            self.assertEqual(TC.shield_bone(argparse.Namespace(shield_bone="Buckler", jobs_config=None, slug=None)), "Buckler")


if __name__ == "__main__":
    unittest.main()
