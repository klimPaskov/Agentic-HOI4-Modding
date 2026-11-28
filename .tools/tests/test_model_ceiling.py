"""Tests for the model ceiling (`.tools/audits/model_ceiling.py`, `check.py model-ceiling`): a helper never starts on a higher model than the chat."""

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "audits"))

import model_ceiling

REPO = Path(__file__).resolve().parents[2]


class ModelCeilingTest(unittest.TestCase):
	def setUp(self):
		self.folder = tempfile.TemporaryDirectory()
		self.root = Path(self.folder.name)
		(self.root / ".claude" / "agents").mkdir(parents=True)
		(self.root / ".claude" / "agents" / "hoi4-pinned.md").write_text("---\nname: hoi4-pinned\nmodel: sonnet\neffort: high\n---\nBody mentions model: opus.\n", encoding="utf-8")
		(self.root / ".claude" / "agents" / "hoi4-free.md").write_text("---\nname: hoi4-free\nmodel: inherit\n---\nBody\n", encoding="utf-8")

	def tearDown(self):
		self.folder.cleanup()

	def start(self, model, session="s1"):
		model_ceiling.hook_session_start(self.root, {"session_id": session, "model": model})

	def decide(self, tool, data, session="s1"):
		buffer = io.StringIO()
		with contextlib.redirect_stdout(buffer):
			code = model_ceiling.hook_pre_tool(self.root, {"session_id": session, "tool_name": tool, "tool_input": data})
		self.assertEqual(code, 0)
		text = buffer.getvalue().strip()
		return json.loads(text)["hookSpecificOutput"] if text else None

	def test_ranks_aliases_and_full_ids(self):
		self.assertEqual([model_ceiling.rank(name) for name in ("haiku", "claude-sonnet-5-5", "OPUS", "claude-opus-5-5", "claude-fable-5-2")], [1, 2, 3, 3, 4])
		self.assertIsNone(model_ceiling.rank("inherit"))
		self.assertIsNone(model_ceiling.rank(""))
		self.assertIsNone(model_ceiling.rank("gpt-6"))

	def test_a_subagent_above_the_chat_is_refused_and_a_lower_one_is_not(self):
		self.start("claude-sonnet-5-5")
		refused = self.decide("Agent", {"subagent_type": "hoi4-free", "model": "opus", "prompt": "x"})
		self.assertEqual(refused["permissionDecision"], "deny")
		self.assertIn("sonnet", refused["permissionDecisionReason"])
		self.assertIsNone(self.decide("Agent", {"subagent_type": "hoi4-free", "model": "haiku"}))
		self.assertIsNone(self.decide("Agent", {"subagent_type": "hoi4-free", "model": "claude-sonnet-5-5"}))
		self.assertIsNone(self.decide("Agent", {"subagent_type": "hoi4-free"}), "inherit is always fine")
		self.assertIsNone(self.decide("Agent", {"subagent_type": "general-purpose"}), "an unknown type with no model is fine")

	def test_a_pinned_definition_counts_unless_the_call_overrides_it(self):
		self.start("haiku")
		refused = self.decide("Agent", {"subagent_type": "hoi4-pinned"})
		self.assertEqual(refused["permissionDecision"], "deny")
		self.assertIn("haiku", refused["permissionDecisionReason"])
		self.assertIsNone(self.decide("Agent", {"subagent_type": "hoi4-pinned", "model": "haiku"}))
		self.assertIsNone(self.decide("Task", {"subagent_type": "hoi4_free"}))
		self.start("claude-opus-5-5", session="s2")
		self.assertIsNone(self.decide("Agent", {"subagent_type": "hoi4-pinned"}, session="s2"))

	def test_a_session_started_from_a_shell_command_is_judged_by_its_model(self):
		self.start("sonnet")
		for command in ("claude -p \"go\" --model opus", "cd x && claude --model=claude-opus-5-5 -p y", "codex exec -m fable-5 \"x\"", r"C:\Users\k\.local\bin\claude.exe -p x --model opus", "ANTHROPIC_LOG=1 claude -p x --model opus", "echo hi; claude.exe -p x --model fable"):
			self.assertEqual(self.decide("Bash", {"command": command})["permissionDecision"], "deny", command)
		for command in ("claude -p x --model sonnet", "claude -p x", "git commit -m opus", "echo claude --model opus", "ls --model opus"):
			self.assertIsNone(self.decide("Bash", {"command": command}), command)

	def test_nothing_is_refused_when_the_chat_model_is_unknown_or_the_hook_is_off(self):
		self.assertIsNone(self.decide("Agent", {"model": "opus"}), "no recorded start")
		self.start("some-other-model")
		self.assertIsNone(self.decide("Agent", {"model": "opus"}), "a model outside the families is never recorded")
		self.start("sonnet", session="s3")
		with unittest.mock.patch.dict("os.environ", {"HOI4_MODEL_CEILING": "off"}):
			self.assertIsNone(self.decide("Agent", {"model": "opus"}, session="s3"))

	def test_the_first_recorded_model_of_a_session_stays(self):
		self.start("sonnet")
		self.start("opus")
		self.assertEqual(model_ceiling.load_state(self.root)["sessions"]["s1"]["model"], "sonnet")
		self.assertEqual(self.decide("Agent", {"model": "opus"})["permissionDecision"], "deny")

	def test_the_model_comes_from_the_transcript_when_the_payload_has_none(self):
		transcript = self.root / "t.jsonl"
		transcript.write_text("not json\n" + json.dumps({"message": {"role": "user"}}) + "\n" + json.dumps({"message": {"role": "assistant", "model": "claude-sonnet-5-5"}}) + "\n", encoding="utf-8")
		model_ceiling.hook_session_start(self.root, {"session_id": "s4", "transcript_path": str(transcript)})
		self.assertEqual(self.decide("Agent", {"model": "opus"}, session="s4")["permissionDecision"], "deny")

	def test_the_check_passes_on_this_repository(self):
		self.assertEqual(model_ceiling.check(REPO), [])

	def test_the_check_names_an_agent_above_sonnet_and_a_missing_hook(self):
		(self.root / ".claude" / "agents" / "hoi4-high.md").write_text("---\nname: hoi4-high\nmodel: opus\neffort: xhigh\n---\n", encoding="utf-8")
		(self.root / ".claude" / "agents" / "hoi4-odd.md").write_text("---\nname: hoi4-odd\nmodel: gpt\n---\n", encoding="utf-8")
		shutil.copy(REPO / ".claude" / "settings.json", self.root / ".claude" / "settings.json")
		settings = json.loads((self.root / ".claude" / "settings.json").read_text(encoding="utf-8"))
		del settings["hooks"]["PreToolUse"]
		(self.root / ".claude" / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
		problems = "\n".join(model_ceiling.check(self.root))
		self.assertIn("hoi4-high.md: pins opus", problems)
		self.assertIn("hoi4-odd.md", problems)
		self.assertIn("no PreToolUse hook", problems)
		self.assertNotIn("no SessionStart hook", problems)

	def test_main_check_prints_and_exits_nonzero_on_a_problem(self):
		buffer = io.StringIO()
		with contextlib.redirect_stdout(buffer):
			self.assertEqual(model_ceiling.main([], root=self.root), 1)
		self.assertIn("model-ceiling:", buffer.getvalue())


if __name__ == "__main__":
	unittest.main()
