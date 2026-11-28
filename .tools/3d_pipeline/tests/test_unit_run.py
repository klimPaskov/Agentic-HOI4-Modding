"""tripo/unit_run.py: a unit run resumes from its last finished step after a kill, and refuses to start when its inputs are gone or
changed. No Blender: the steps are fake commands."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tripo"))

import unit_run as U


class Killed(Exception):
    """A pause, a crash or a restart in the middle of a step."""


class FakeRunner:
    def __init__(self, kill_at: str = "", codes=None):
        self.calls, self.kill_at, self.codes = [], kill_at, codes or {}

    def __call__(self, command, cwd, log_path, env):
        name = command[-1]
        self.calls.append(list(command))
        if name == self.kill_at:
            self.kill_at = ""
            raise Killed(name)
        return self.codes.get(name, 0)


def steps():
    return [U.Step(name, ["tool", name], heavy=name in ("intake", "pilot", "preview")) for name in
            ("intake", "pilot", "tripo_checks", "preview")]


def names(runner):
    return [call[-1] for call in runner.calls]


class Resume(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.run = self.root / "run"
        (self.root / "jobs.json").write_text('{"jobs": {}}', encoding="utf-8")
        (self.root / "u__rigged.glb").write_bytes(b"glb")
        self.sources = {"jobs": self.root / "jobs.json", "rigged": self.root / "u__rigged.glb"}

    def tearDown(self):
        self.tmp.cleanup()

    def manifest(self):
        return U.take_inputs(self.run, self.sources)

    def test_a_step_killed_half_way_runs_again_and_the_finished_ones_do_not(self):
        manifest = self.manifest()
        first = FakeRunner(kill_at="tripo_checks")
        with self.assertRaises(Killed):
            U.run_steps(self.run, "u", steps(), manifest, runner=first, log=lambda _l: None)
        self.assertEqual(names(first), ["intake", "pilot", "tripo_checks"])
        state = json.loads((self.run / U.STATE).read_text(encoding="utf-8"))
        self.assertEqual(sorted(state), ["intake", "pilot"], "the killed step is never recorded as finished")
        self.assertIn("next step `tripo_checks`", (self.run / "STATUS.md").read_text(encoding="utf-8"))
        second = FakeRunner()
        self.assertEqual(U.run_steps(self.run, "u", steps(), manifest, runner=second, log=lambda _l: None), 0)
        self.assertEqual(names(second), ["tripo_checks", "preview"])
        self.assertIn("State: finished", (self.run / "STATUS.md").read_text(encoding="utf-8"))

    def test_the_gate_wraps_only_the_heavy_steps(self):
        runner = FakeRunner()
        U.run_steps(self.run, "u", steps(), self.manifest(), gate=["sh", "gated.sh", "14400"], runner=runner, log=lambda _l: None)
        gated = {call[-1]: call[:3] == ["sh", "gated.sh", "14400"] for call in runner.calls}
        self.assertEqual(gated, {"intake": True, "pilot": True, "tripo_checks": False, "preview": True})

    def test_a_check_with_findings_finishes_and_a_failed_step_stops_the_run(self):
        manifest = self.manifest()
        runner = FakeRunner(codes={"tripo_checks": 1, "preview": 3})
        self.assertEqual(U.run_steps(self.run, "u", steps(), manifest, runner=runner, log=lambda _l: None), 3)
        state = json.loads((self.run / U.STATE).read_text(encoding="utf-8"))
        self.assertEqual(state["tripo_checks"]["exit"], 1)
        self.assertNotIn("preview", state)
        again = FakeRunner()
        U.run_steps(self.run, "u", steps(), manifest, runner=again, log=lambda _l: None)
        self.assertEqual(names(again), ["preview"])

    def test_again_runs_the_named_step_and_every_later_one(self):
        manifest = self.manifest()
        U.run_steps(self.run, "u", steps(), manifest, runner=FakeRunner(), log=lambda _l: None)
        runner = FakeRunner()
        U.run_steps(self.run, "u", steps(), manifest, runner=runner, again=["pilot"], log=lambda _l: None)
        self.assertEqual(names(runner), ["pilot", "tripo_checks", "preview"])
        with self.assertRaises(U.RunRefused):
            U.run_steps(self.run, "u", steps(), manifest, runner=FakeRunner(), again=["nosuch"], log=lambda _l: None)

    def test_a_changed_command_runs_that_step_and_the_later_ones_again(self):
        manifest = self.manifest()
        U.run_steps(self.run, "u", steps(), manifest, runner=FakeRunner(), log=lambda _l: None)
        changed = steps()
        changed[1].command = ["tool", "--new-flag", "pilot"]
        runner = FakeRunner()
        U.run_steps(self.run, "u", changed, manifest, runner=runner, log=lambda _l: None)
        self.assertEqual(names(runner), ["pilot", "tripo_checks", "preview"])

    def test_the_inputs_are_copied_into_the_run_and_survive_a_cleanup_of_the_originals(self):
        manifest = self.manifest()
        self.assertTrue((self.run / "inputs" / "u__rigged.glb").is_file())
        self.sources["rigged"].unlink()  # a cleanup moved the export away
        self.assertEqual(self.manifest(), manifest, "the run keeps its own copy")

    def test_a_run_refuses_to_start_when_its_inputs_are_missing_or_changed(self):
        with self.assertRaises(U.RunRefused):
            U.take_inputs(self.run, {"rigged": self.root / "gone.glb"})
        self.manifest()
        (self.run / "inputs" / "u__rigged.glb").write_bytes(b"other")
        with self.assertRaisesRegex(U.RunRefused, "changed"):
            self.manifest()
        (self.run / "inputs" / "u__rigged.glb").unlink()
        with self.assertRaisesRegex(U.RunRefused, "missing"):
            self.manifest()

    def test_a_new_export_under_the_same_run_folder_is_refused(self):
        self.manifest()
        self.sources["rigged"].write_bytes(b"a new export")
        with self.assertRaisesRegex(U.RunRefused, "new run"):
            self.manifest()


if __name__ == "__main__":
    unittest.main()
