"""Tests for scripts/benchmark_new_mod.py with a stand-in client, so no model or game is needed.

The stand-in plays the agent: the first message writes the brief, the reply writes the ledger and one passed
feature, and `continue` passes the rest, unless the prompt asks it to stall.
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import benchmark_new_mod as bench

FAKE_CLIENT = r'''
import json, sys
from pathlib import Path
message = sys.argv[1]
mod = Path("docs/mod")
mod.mkdir(parents=True, exist_ok=True)
state = json.loads(Path(".bench_state").read_text()) if Path(".bench_state").exists() else {"n": 0, "prompt": message}
state["n"] += 1
Path(".bench_state").write_text(json.dumps(state))
feature = lambda i, ok: {"id": f"f{i}", "title": "F", "phase": "core", "surfaces": ["country"], "depends_on": [],
    "acceptance": ["a"], "evidence": ["docs/mod/brief.md"] if ok else [], "passes": ok}
if state["n"] == 1:
    for name in ("brief.md", "decisions.md", "canon.md", "progress.md"):
        (mod / name).write_text("x", encoding="utf-8")
else:
    stall = "stall" in state["prompt"]
    passed = 2 if stall else min(state["n"], 3)
    ledger = {"schema": "hoi4-mod-ledger/1", "mod": "T", "state": "building",
        "scope": {"phases": [{"id": "core"}], "surfaces": ["country"]},
        "live_testing": {"run": "no"}, "features": [feature(i, i < passed) for i in range(3)]}
    (mod / "ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
print(json.dumps({"type": "result", "session_id": "s-%d" % state["n"]}))
'''


class BenchmarkTest(unittest.TestCase):
	def setUp(self):
		self.folder = tempfile.TemporaryDirectory()
		base = Path(self.folder.name)
		self.template = base / "template"
		(self.template / ".tools").mkdir(parents=True)
		shutil.copy(ROOT / ".tools" / "check.py", self.template / ".tools" / "check.py")
		shutil.copytree(ROOT / ".tools" / "lib", self.template / ".tools" / "lib", ignore=shutil.ignore_patterns("__pycache__"))
		(self.template / ".tools" / "audits").mkdir()
		shutil.copy(ROOT / ".tools" / "audits" / "mod_gate.py", self.template / ".tools" / "audits" / "mod_gate.py")
		(self.template / ".gitignore").write_text("/.tmp/\n/.bench_state\n", encoding="utf-8")
		for command in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", "fresh"]):
			subprocess.run(["git", *command], cwd=self.template, check=True)
		(base / "fake.py").write_text(FAKE_CLIENT, encoding="utf-8")
		self.client = f'"{sys.executable}" "{(base / "fake.py").as_posix()}" {{prompt}} {{resume}}'
		self.prompts = base / "prompts.json"
		self.prompts.write_text(json.dumps({"prompts": [{"id": "good", "prompt": "Create a mod."}, {"id": "stuck", "prompt": "Create a stall mod."}],
			"replies": ["Use your suggestions."], "continue": "Continue building."}), encoding="utf-8")
		self.out = base / "run"

	def tearDown(self):
		self.folder.cleanup()

	def test_runs_each_prompt_in_a_fresh_copy_and_judges_from_files(self):
		code = bench.main(["--template", str(self.template), "--prompts", str(self.prompts), "--out", str(self.out),
			"--client", self.client, "--sessions", "4"])
		self.assertEqual(code, 1)
		report = {row["id"]: row for row in json.loads((self.out / "report.json").read_text(encoding="utf-8"))["results"]}
		self.assertTrue(report["good"]["passed"], report["good"]["reasons"])
		self.assertEqual(report["good"]["measured"]["ledger"]["passed"], 3)
		self.assertEqual(len(report["good"]["sessions"]), 3)
		self.assertFalse(report["stuck"]["passed"])
		self.assertIn("gate exit 1", report["stuck"]["reasons"])
		self.assertEqual(len(report["stuck"]["sessions"]), 4)
		self.assertFalse((self.template / "docs").exists(), "the template must stay untouched")
		self.assertIn("| good |", (self.out / "report.md").read_text(encoding="utf-8"))
		self.assertEqual(bench.main(["--report", str(self.out)]), 1)

	def test_resume_passes_the_last_session(self):
		command = bench.client_command('claude -p {prompt} --model {model} {resume}', "hi there", "sonnet", 5, "abc")
		self.assertEqual(command, ["claude", "-p", "hi there", "--model", "sonnet", "--resume", "abc"])
		self.assertNotIn("--resume", bench.client_command('claude -p {prompt} {resume}', "x", "m", 1, None))

	def test_refuses_a_template_without_the_kit(self):
		empty = Path(self.folder.name) / "empty"
		empty.mkdir()
		self.assertEqual(bench.main(["--template", str(empty), "--prompts", str(self.prompts), "--out", str(self.out)]), 2)


if __name__ == "__main__":
	unittest.main()
