"""TRIPO-WING-SCREEN (a wing's angle on the game camera's screen) and the side-view wing rules that only report for a winged humanoid's
attack and defend (tripo/tripo_checks.py). A synthetic winged biped. No Blender."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))
sys.path.insert(0, str(PIPELINE / "tripo"))

import test_deformation_checks as TD
import tripo_checks as TC
from lib import pdx_deform
from test_tripo_chain_lift import WingedBiped, local
from test_tripo_pose_upper import turn


class Screen(WingedBiped):
    def clip(self, role: str, back: float) -> Path:
        """Each wing swung back `back` degrees about the up axis at its root, in every frame."""

        def pose(_frame: int):
            out = {}
            for side, sign in (("L", -1.0), ("R", 1.0)):
                for chain in (1, 2):
                    name = f"Wing{side}{chain}_1"
                    out[name] = (local(name), turn("y", sign * back))
            return out

        path = self.folder / f"unit_{role}.anim"
        TD.write_anim(path, 6, pose)
        return path

    def screen(self, role: str, back: float):
        anim = pdx_deform.load_anim(self.clip(role, back))
        return TC.wing_screen_findings(self.mesh, {f"unit_{role}": anim})

    def test_a_spread_wing_passes_and_a_wing_swung_back_fails(self) -> None:
        found, numbers = self.screen("attack", 0.0)
        self.assertEqual(found, [], numbers)
        found, numbers = self.screen("attack", 80.0)
        self.assertEqual([item["rule"] for item in found], ["TRIPO-WING-SCREEN"], numbers)

    def test_a_folded_idle_and_a_death_are_not_judged(self) -> None:
        for role in ("idle", "death"):
            found, numbers = self.screen(role, 80.0)
            self.assertEqual((found, numbers), ([], {}), role)


class Span(Screen):
    def span(self, role: str, back: float):
        anim = pdx_deform.load_anim(self.clip(role, back))
        return TC.wing_span_findings(self.mesh, {f"unit_{role}": anim})

    def test_a_spread_wing_keeps_the_drawn_span_and_a_wing_swung_far_back_does_not(self) -> None:
        for role in ("attack", "move"):
            found, numbers = self.span(role, 0.0)
            self.assertEqual(found, [], numbers)
            self.assertAlmostEqual(numbers[f"unit_{role}"]["span_share"], 1.0, places=2)
            found, numbers = self.span(role, 80.0)
            self.assertEqual([item["rule"] for item in found], ["TRIPO-WING-SPAN"], numbers)

    def test_folded_wrapped_and_dying_wings_are_not_judged(self) -> None:
        for role in ("idle", "retreat", "defend", "death"):
            found, numbers = self.span(role, 80.0)
            self.assertEqual((found, numbers), ([], {}), role)


class Advisory(unittest.TestCase):
    def test_only_the_side_views_of_a_humanoids_attack_and_defend_report(self) -> None:
        class Mesh:  # a humanoid: no quadruped's bones
            bones = ["Hips", "Spine02"]
            parents = [-1, 0]

        findings = [{"rule": "TRIPO-WING-FRONT", "subject": "u_attack", "view": "right"},
                    {"rule": "TRIPO-WING-EDGE-ON", "subject": "u_defend", "view": "left"},
                    {"rule": "TRIPO-WING-EDGE-ON", "subject": "u_attack", "view": "map"},
                    {"rule": "TRIPO-WING-FRONT", "subject": "u_retreat", "view": "right"},
                    {"rule": "TRIPO-WING-SCREEN", "subject": "u_attack"}]
        original = TC.quadruped_checks.is_quadruped
        TC.quadruped_checks.is_quadruped = lambda mesh: False
        try:
            keep, report = TC.side_view_advisory(findings, Mesh())
        finally:
            TC.quadruped_checks.is_quadruped = original
        self.assertEqual([(f["rule"], f["subject"]) for f in report], [("TRIPO-WING-FRONT", "u_attack"), ("TRIPO-WING-EDGE-ON", "u_defend")])
        self.assertEqual(len(keep), 3, "the map view, the retreat and the screen check still fail the unit")


if __name__ == "__main__":
    unittest.main()
