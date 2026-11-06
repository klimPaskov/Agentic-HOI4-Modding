"""The shared stage verdict and the map from each failed check rule to its fix."""

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

import check_unit_files
import test_motion_checks as legged
from lib import stage_verdict


class Verdict(unittest.TestCase):
    def test_states(self) -> None:
        self.assertEqual(stage_verdict.verdict("check", True, "u")["verdict"], "pass")
        self.assertEqual(stage_verdict.verdict("check", False, "u")["verdict"], "fail")
        self.assertEqual(stage_verdict.verdict("check", False, "u", escalate={"rules": ["UNIT-ANIM-KNEE"]})["verdict"], "escalate")

    def test_extra_keys_and_the_findings_cap(self) -> None:
        findings = [{"rule": "UNIT-HOLE", "file": "u.mesh", "message": "x"}] * 30
        payload = stage_verdict.verdict("generate", False, "u", findings=findings, task_id="abc", credits=15)
        self.assertEqual((payload["task_id"], payload["credits"]), ("abc", 15))
        self.assertEqual((len(payload["findings"]), payload["findings_total"]), (stage_verdict.MAX_FINDINGS, 30))

    def test_write_saves_the_file_and_prints_one_line(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "v" / "verdict.json"
            with redirect_stdout(io.StringIO()) as output:
                stage_verdict.write(stage_verdict.verdict("check", True, "u"), path)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["stage"], "check")
            self.assertEqual(len(output.getvalue().strip().splitlines()), 1)


class NextSteps(unittest.TestCase):
    def test_repairs_are_merged_into_one_command_in_order(self) -> None:
        steps, escalate = stage_verdict.next_for_findings({"UNIT-SEAM", "UNIT-WINDING", "UNIT-ANIM-GROUND"}, "gfx/u", "job/evidence")
        self.assertIsNone(escalate)
        self.assertIn("--repairs winding weights ground", steps[0])
        self.assertIn("check_unit_files.py job/evidence/repair/files", steps[1])

    def test_motion_rules_escalate_to_live_authoring(self) -> None:
        steps, escalate = stage_verdict.next_for_findings({"UNIT-ANIM-KNEE", "UNIT-ANIM-SHARED"}, "gfx/u", "out")
        self.assertEqual(steps, [])
        self.assertEqual(escalate["rules"], ["UNIT-ANIM-KNEE", "UNIT-ANIM-SHARED"])
        self.assertIn("live-authoring.md", escalate["how"])

    def test_stretch_is_repaired_first_and_escalates_once_repaired(self) -> None:
        steps, escalate = stage_verdict.next_for_findings({"UNIT-ANIM-STRETCH"}, "gfx/u", "out")
        self.assertIn("--repairs bridges weights", steps[0])
        self.assertIsNone(escalate)
        steps, escalate = stage_verdict.next_for_findings({"UNIT-ANIM-STRETCH"}, "gfx/u", "out", repaired=True)
        self.assertEqual(steps, [])
        self.assertEqual(escalate["rules"], ["UNIT-ANIM-STRETCH"])

    def test_paths_with_spaces_are_quoted(self) -> None:
        steps, _escalate = stage_verdict.next_for_findings({"UNIT-HOLE"}, "C:/My Mods/gfx/u", "C:/My Mods/job")
        self.assertIn('repair_unit.py "C:/My Mods/gfx/u" --out "C:/My Mods/job/repair"', steps[0])

    def test_textures_and_registration(self) -> None:
        steps, _escalate = stage_verdict.next_for_findings({"UNIT-DDS-MIPS", "UNIT-REG-ENTITY"}, "gfx/u", "out", stem="u_rider", unit_type="rider")
        self.assertIn("--stem u_rider --unit-type rider --repair-textures", steps[0])
        self.assertIn("registration", steps[1])


class CheckVerdict(unittest.TestCase):
    def run_check(self, clips, crotch_blend):
        with tempfile.TemporaryDirectory() as folder:
            unit = Path(folder) / "u"
            legged.write_unit(unit, "u", clips, crotch_blend)
            path = Path(folder) / "evidence" / "check.json"
            original = check_unit_files.load_calibration
            check_unit_files.load_calibration = lambda group="organic", path=None: dict(legged.LIMITS)
            try:
                with redirect_stdout(io.StringIO()) as output:
                    code = check_unit_files.main([str(unit), "--verdict", str(path)])
            finally:
                check_unit_files.load_calibration = original
            payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(json.loads(output.getvalue()), payload)
        return code, payload

    def test_a_clean_unit_passes_and_names_the_review(self) -> None:
        code, payload = self.run_check({"move": (20, legged.walk), "attack": (20, legged.strike)}, 0.5)
        self.assertEqual((code, payload["verdict"]), (0, "pass"))
        self.assertIn("review_unit.py", payload["next"][-1])
        # The ribbons of the synthetic unit are open, so the pass also offers the free hole repair first.
        self.assertIn("--repairs holes", payload["next"][0])

    def test_a_seam_fails_with_the_repair_to_run(self) -> None:
        code, payload = self.run_check({"move": (20, legged.walk), "attack": (20, legged.strike)}, 0.0)
        self.assertEqual((code, payload["verdict"]), (1, "fail"))
        self.assertEqual([item["rule"] for item in payload["findings"]], ["UNIT-SEAM"])
        self.assertIn("--repairs weights", payload["next"][0])

    def test_a_backward_knee_escalates(self) -> None:
        code, payload = self.run_check({"attack": (10, lambda f: {"LeftLeg": legged.about_x(4.0 * f)})}, 0.5)
        self.assertEqual((code, payload["verdict"]), (1, "escalate"))
        self.assertEqual(payload["escalate"]["rules"], ["UNIT-ANIM-KNEE"])


if __name__ == "__main__":
    unittest.main()
