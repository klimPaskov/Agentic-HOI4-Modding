"""Tests for the mod ledger and completion gate (`.tools/audits/mod_gate.py`, `check.py gate`).

Each test builds a small mod in a temporary Git repository with a stand-in `check.py` whose exit code the test
chooses, so the gate's own rules are tested without the game or the real checks.
"""

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "audits"))

import mod_gate

FAKE_CHECK = """import json, os, sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
log = root / ".tmp" / "check_calls.txt"
log.parent.mkdir(parents=True, exist_ok=True)
with log.open("a", encoding="utf-8") as handle:
	handle.write(" ".join(sys.argv[1:]) + "\\n")
code = int((root / ".tmp" / "check_exit.txt").read_text()) if (root / ".tmp" / "check_exit.txt").exists() else 0
if code == 1:
	print("events/x.txt:3: error SCRIPT-GE uses >=")
raise SystemExit(code)
"""


def feature(identifier, passes=False, **extra):
	row = {"id": identifier, "title": identifier.title(), "phase": "core", "surfaces": ["country"], "depends_on": [], "acceptance": ["it works"], "evidence": [], "passes": passes}
	row.update(extra)
	return row


class GateTest(unittest.TestCase):
	def setUp(self):
		self.folder = tempfile.TemporaryDirectory()
		self.root = Path(self.folder.name)
		(self.root / ".tools").mkdir()
		(self.root / ".tools" / "check.py").write_text(FAKE_CHECK, encoding="utf-8")
		(self.root / ".gitignore").write_text("/.tmp/\n", encoding="utf-8")
		subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
		subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "add", "-A"], cwd=self.root, check=True)
		subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", "init"], cwd=self.root, check=True)

	def tearDown(self):
		self.folder.cleanup()

	def write(self, relative, text):
		path = self.root / relative
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_text(text, encoding="utf-8")

	def ledger(self, features, state="building", **extra):
		data = {"schema": mod_gate.SCHEMA, "mod": "Test", "state": state, "scope": {"phases": [{"id": "core"}, {"id": "expansion"}], "surfaces": ["country"]}, "features": features}
		data.update(extra)
		self.write("docs/mod/ledger.json", json.dumps(data))

	def set_check_exit(self, code):
		self.write(".tmp/check_exit.txt", str(code))

	def problems(self):
		return mod_gate.evaluate(self.root, {}).problems

	def run_main(self, *argv, stdin=""):
		out = io.StringIO()
		old_stdin = sys.stdin
		sys.stdin = io.StringIO(stdin)
		try:
			with contextlib.redirect_stdout(out):
				code = mod_gate.main(list(argv), root=self.root)
		finally:
			sys.stdin = old_stdin
		return code, out.getvalue()

	def stop(self, session="s1"):
		code, out = self.run_main("--hook", "stop", stdin=json.dumps({"session_id": session, "stop_hook_active": False}))
		self.assertEqual(code, 0)
		return json.loads(out) if out.strip() else {}

	def test_no_ledger_is_silent(self):
		self.assertEqual(self.stop(), {})
		self.assertEqual(self.run_main("--hook", "session-start")[1], "")
		self.assertEqual(self.run_main()[0], 0)

	def test_planning_state_does_not_gate(self):
		self.ledger([feature("country")], state="planning")
		self.assertEqual(self.stop(), {})

	def test_open_feature_blocks_and_names_next(self):
		self.ledger([feature("country"), feature("focus-tree", depends_on=["country"])])
		problems = self.problems()
		self.assertTrue(any("country: open" in problem for problem in problems), problems)
		reply = self.stop()
		self.assertEqual(reply["decision"], "block")
		self.assertIn("country: open", reply["reason"])
		self.assertIn("Next feature: `country`", self.run_main("--next")[1])

	def test_pass_needs_existing_evidence_and_passed_dependencies(self):
		self.ledger([feature("country"), feature("focus-tree", passes=True, depends_on=["country"], evidence=["docs/none.md"])])
		problems = "\n".join(self.problems())
		self.assertIn("evidence `docs/none.md` does not exist", problems)
		self.assertIn("passes before its dependency `country`", problems)

	def test_pass_without_evidence_fails(self):
		self.ledger([feature("country", passes=True)])
		self.assertTrue(any("passes with no `evidence`" in problem for problem in self.problems()))

	def test_machine_checks(self):
		self.write("common/national_focus/t.txt", "focus = { id = a }\nfocus = { id = b }\n")
		self.write("docs/evidence.md", "ok")
		count = {"kind": "count", "path": "common/national_focus/*.txt", "regex": r"^focus\s*=", "min": 3}
		self.ledger([feature("focus-tree", passes=True, evidence=["docs/evidence.md"], checks=[count])])
		self.assertTrue(any("occurs 2 time(s)" in problem for problem in self.problems()))
		count["min"] = 2
		self.ledger([feature("focus-tree", passes=True, evidence=["docs/evidence.md"], checks=[count,
			{"kind": "exists", "path": "common/national_focus/t.txt"}, {"kind": "contains", "path": "common/national_focus/t.txt", "text": "id = b"}])])
		self.assertEqual(self.problems(), [])

	def test_escaping_paths_are_refused(self):
		self.ledger([feature("country", passes=True, evidence=["../outside.md"], checks=[{"kind": "exists", "path": "../x"}])])
		problems = "\n".join(self.problems())
		self.assertIn("evidence `../outside.md` does not exist", problems)
		self.assertIn("needs a repository-relative `path`", problems)

	def test_scope_surfaces_must_be_covered(self):
		self.ledger([feature("country")], scope={"phases": [{"id": "core"}]})
		self.assertTrue(any("`scope.surfaces` must list" in problem for problem in self.problems()))
		self.ledger([feature("country")], scope={"phases": [{"id": "core"}], "surfaces": ["country", "events", "ai"]})
		problems = " | ".join(self.problems())
		self.assertIn("scope surface `events` has no feature", problems)
		self.assertIn("scope surface `ai` has no feature", problems)
		self.assertNotIn("scope surface `country`", problems)

	def test_phases_keep_the_build_order(self):
		self.write("docs/evidence.md", "ok")
		self.ledger([feature("country", phase="none")])
		self.assertTrue(any("`phase` must be one of core, expansion" in problem for problem in self.problems()))
		self.ledger([feature("rivals", passes=True, phase="expansion", evidence=["docs/evidence.md"]), feature("country")])
		self.assertTrue(any("passes in phase `expansion` while an earlier phase is open (country)" in problem for problem in self.problems()))
		self.assertIn("Next feature: `country`", self.run_main("--next")[1])
		self.ledger([feature("rivals", passes=True, phase="expansion", evidence=["docs/evidence.md"]),
			feature("country", blocker={"needs": "user", "reason": "the user supplies the flag"})])
		self.assertEqual(self.problems(), [])

	def test_blocker_needs_reason_and_kind(self):
		self.ledger([feature("units", blocker={"reason": "", "needs": "user"})])
		self.assertTrue(any("needs a `reason`" in problem for problem in self.problems()))
		self.ledger([feature("units", blocker={"reason": "the 3D route needs a paid account", "needs": "money"})])
		gate = mod_gate.evaluate(self.root, {})
		self.assertEqual(gate.problems, [])
		self.assertTrue(any("blocked (money)" in note for note in gate.notes))

	def test_schema_problems(self):
		self.ledger([feature("a", depends_on=["b"]), feature("b", depends_on=["a"]), feature("a"), feature("Bad Id", depends_on=["zz"])])
		problems = "\n".join(self.problems())
		self.assertIn("dependency cycle", problems)
		self.assertIn("`a` is used more than once", problems)
		self.assertIn("must be lower-case", problems)
		self.assertIn("depends on `zz`", problems)
		self.write("docs/mod/ledger.json", "{not json")
		self.assertIn("cannot be read", self.problems()[0])

	def test_placeholders(self):
		self.write("docs/evidence.md", "ok")
		self.write("localisation/english/t_l_english.yml", '﻿l_english:\n t_title: "TODO write"\n t_same: "t_same"\n t_ok: "Atlantis rises"\n')
		self.write("events/t.txt", "# FIXME wire the option\nnamespace = t\n")
		self.ledger([feature("country", passes=True, evidence=["docs/evidence.md"])])
		problems = "\n".join(self.problems())
		self.assertIn("t_l_english.yml:2", problems)
		self.assertIn("t_l_english.yml:3", problems)
		self.assertNotIn("t_l_english.yml:4", problems)
		self.assertIn("events/t.txt:1", problems)
		self.ledger([feature("country", passes=True, evidence=["docs/evidence.md"])],
			placeholders_allowed=[{"path": "events/", "reason": "approved pending art"}, {"path": "localisation/english/t_l_english.yml", "reason": "x"}])
		self.assertEqual(self.problems(), [])

	def test_static_checks_block_on_errors_only(self):
		self.write("docs/evidence.md", "ok")
		self.ledger([feature("country", passes=True, evidence=["docs/evidence.md"])])
		self.set_check_exit(1)
		self.assertTrue(any("check.py quick found errors" in problem for problem in self.problems()))
		self.set_check_exit(2)
		gate = mod_gate.evaluate(self.root, {})
		self.assertEqual(gate.problems, [])
		self.assertTrue(any("could not run" in note for note in gate.notes))
		self.set_check_exit(0)
		self.assertEqual(self.problems(), [])
		calls = (self.root / ".tmp" / "check_calls.txt").read_text(encoding="utf-8")
		self.assertIn("full --only localisation asset-wiring script-rules gui-rules", calls)

	def test_final_scan_waits_for_every_feature(self):
		self.ledger([feature("country")])
		self.problems()
		calls = (self.root / ".tmp" / "check_calls.txt").read_text(encoding="utf-8")
		self.assertNotIn("full", calls)

	def test_idle_cap_lets_the_stop_through(self):
		self.ledger([feature("country")], gate={"max_idle_blocks": 2, "max_blocks": 10})
		self.assertEqual(self.stop()["decision"], "block")
		self.assertEqual(self.stop()["decision"], "block")
		reply = self.stop()
		self.assertNotIn("decision", reply)
		self.assertIn("in a row with no change", reply["systemMessage"])

	def test_progress_resets_idle_and_total_cap_holds(self):
		self.ledger([feature("country")], gate={"max_idle_blocks": 2, "max_blocks": 3})
		for number in range(3):
			self.write(f"events/e{number}.txt", "namespace = t\n")
			self.assertEqual(self.stop()["decision"], "block")
		self.write("events/e9.txt", "namespace = t\n")
		self.assertIn("3 blocks this session", self.stop()["systemMessage"])

	def test_wait_allows_one_stop_and_a_prompt_clears_it(self):
		self.ledger([feature("country")])
		self.assertEqual(self.run_main("--wait", "Which start date?")[0], 0)
		self.assertEqual(self.stop(), {})
		self.assertIn("Waiting for the user's answer", self.run_main("--next")[1])
		self.run_main("--hook", "prompt", stdin=json.dumps({"prompt": "1936"}))
		self.assertEqual(self.stop()["decision"], "block")

	def test_pause_and_resume(self):
		self.ledger([feature("country")])
		self.run_main("--pause", "stop for today")
		self.assertEqual(self.stop(), {})
		data = json.loads((self.root / "docs/mod/ledger.json").read_text(encoding="utf-8"))
		self.assertEqual((data["state"], data["pause_reason"]), ("paused", "stop for today"))
		self.run_main("--resume")
		self.assertEqual(self.stop()["decision"], "block")

	def test_environment_switch(self):
		self.ledger([feature("country")])
		with unittest.mock.patch.dict("os.environ", {"HOI4_MOD_GATE": "off"}):
			self.assertEqual(self.stop(), {})

	def test_report_exit_codes_and_complete_build(self):
		self.ledger([feature("country")])
		self.assertEqual(self.run_main()[0], 1)
		self.write("docs/evidence.md", "ok")
		self.ledger([feature("country", passes=True, evidence=["docs/evidence.md"])])
		code, out = self.run_main()
		self.assertEqual(code, 0, out)
		self.assertIn("every feature passed", out)
		self.assertEqual(self.stop(), {})
		self.write("docs/mod/ledger.json", "[]")
		self.assertEqual(self.run_main()[0], 2)

	def test_session_start_prints_the_routine(self):
		self.ledger([feature("country"), feature("events", depends_on=["country"])])
		out = self.run_main("--hook", "session-start")[1]
		self.assertIn("0 of 2 features passed", out)
		self.assertIn("Next feature: `country`", out)
		self.assertIn("check.py quick", out)

	def test_a_big_request_on_an_existing_mod_uses_the_same_gate_as_an_addition(self):
		self.write("docs/evidence.md", "ok")
		scope = {"kind": "addition", "request": "new-nation", "phases": [{"id": "core"}], "surfaces": ["country"]}
		self.ledger([feature("country")], scope=scope)
		self.assertTrue(any("country: open" in problem for problem in self.problems()), self.problems())
		self.ledger([feature("country", passes=True, evidence=["docs/evidence.md"])], scope=scope)
		self.assertEqual(self.problems(), [])

	def test_scope_kind_is_checked(self):
		self.ledger([feature("country")], scope={"kind": "side-quest", "phases": [{"id": "core"}], "surfaces": ["country"]})
		self.assertTrue(any("`scope.kind` must be one of mod, addition" in problem for problem in self.problems()), self.problems())
		self.ledger([feature("country")], scope={"kind": "addition", "phases": [{"id": "core"}], "surfaces": ["country"]})
		self.assertTrue(any("`scope.request`" in problem for problem in self.problems()), self.problems())
		self.ledger([feature("country")], scope={"kind": "mod", "phases": [{"id": "core"}], "surfaces": ["country"]})
		self.assertFalse(any("scope.kind" in problem for problem in self.problems()))

	def test_the_prompt_hook_sizes_a_request_only_while_no_build_is_active(self):
		prompt = lambda: self.run_main("--hook", "prompt", stdin="{}")[1]
		self.assertIn("Kit routing:", prompt())
		self.assertIn("hoi4-new-mod", prompt())
		self.ledger([feature("country")], state="planning")
		self.assertEqual(prompt(), "")
		self.ledger([feature("country")])
		self.assertEqual(prompt(), "")
		self.ledger([feature("country")], state="paused")
		self.assertEqual(prompt(), "")
		self.ledger([feature("country")], state="complete")
		self.assertIn("Kit routing:", prompt())
		with unittest.mock.patch.dict("os.environ", {"HOI4_MOD_GATE": "off"}):
			self.assertEqual(prompt(), "")

	def test_archive_moves_only_a_complete_ledger_and_its_progress_log(self):
		self.write("docs/mod/progress.md", "log")
		self.write("docs/mod/brief.md", "the mod brief stays")
		self.ledger([feature("country")], state="building")
		self.assertEqual(self.run_main("--archive")[0], 1)
		self.assertTrue((self.root / "docs/mod/ledger.json").is_file())
		self.ledger([feature("country", passes=True)], state="complete", scope={"kind": "addition", "request": "Naval Base!", "phases": [{"id": "core"}], "surfaces": ["country"]})
		code, out = self.run_main("--archive")
		self.assertEqual(code, 0, out)
		self.assertFalse((self.root / "docs/mod/ledger.json").exists())
		self.assertFalse((self.root / "docs/mod/progress.md").exists())
		self.assertTrue((self.root / "docs/mod/brief.md").is_file(), "the mod's own brief stays")
		moved = list((self.root / "docs/mod/history").glob("*-naval-base/ledger.json"))
		self.assertEqual(len(moved), 1, out)
		self.assertTrue((moved[0].parent / "progress.md").is_file())
		self.assertEqual(self.run_main("--archive")[0], 2, "nothing left to archive")
		self.assertEqual(self.run_main("--hook", "session-start")[1], "")


if __name__ == "__main__":
	unittest.main()
