"""Tests for the generator registry (`.tools/sync/generators.json`), its runner, the Claude Code hook and the
synchronizers it runs.

Every case builds a small mod in a temporary folder with copies of the real `.tools/sync/` tools, so the tests
exercise the shipped code, never the live projections. Run from the repository root:
`python -B -m unittest discover -s .tools/tests -p "test_sync.py"`.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
SYNC = TOOLS / "sync"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(SYNC))

import check
import generators

# HOI4 Mod Setup lets `check.py setup` rewrite only these tracked paths (src-tauri/src/agent_setup.rs in
# HOI4-Mod-Setup). Every generated output of an installed mod must stay inside them.
SETUP_REWRITABLE_EXACT = (".gitignore", "AGENTS.md", ".claude/agent-map.md", ".tools/quality_baseline.json")
SETUP_REWRITABLE_PREFIXES = (".codex/", ".cursor/", ".opencode/", ".qoder/", ".agents/")

AGENT = """---
name: {name}
description: "{description}"
model: haiku
effort: medium
---

You are the {name} worker. Read CLAUDE.md first.
"""


def agent_text(name, description="Does one fixture job."):
	return AGENT.format(name=name, description=description)


class Mod:
	"""An installed mod with Codex selected: canonical files, the real sync tools and generated projections."""

	def __init__(self, folder, source_package=False):
		self.root = Path(folder)
		shutil.copytree(SYNC, self.root / ".tools" / "sync", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
		instructions = "CLAUDE_template.md" if source_package else "CLAUDE.md"
		self.write(instructions, "# Fixture mod\n\nInstall this template as `CLAUDE.md`.\n\nRead CLAUDE.md before editing.\n")
		self.write(".claude/agents/hoi4-alpha.md", agent_text("hoi4-alpha"))
		self.write(".claude/agents/hoi4-beta.md", agent_text("hoi4-beta"))
		self.write(".claude/skills/skill-a/SKILL.md", "---\nname: skill-a\n---\nSkill A.\n")
		self.write(".claude/skills/skill-b/SKILL.md", "---\nname: skill-b\n---\nSkill B.\n")
		self.write(".claude/skills/skill-b/references/notes.md", "Reference notes.\n")
		self.write(".codex/config.toml", "model = \"inherit\"\n")
		(self.root / ".codex" / "agents").mkdir(parents=True)

	def path(self, rel):
		return self.root / rel

	def write(self, rel, text):
		target = self.path(rel)
		target.parent.mkdir(parents=True, exist_ok=True)
		target.write_text(text, encoding="utf-8", newline="\n")

	def read(self, rel):
		return self.path(rel).read_text(encoding="utf-8")

	def run(self, *args):
		return subprocess.run([sys.executable, "-B", str(self.path(".tools/sync/generators.py")), "--root", str(self.root), *args],
			capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)

	def hook(self, rel, tool="Edit"):
		native = str(self.path(rel)).replace("/", "\\") if os.name == "nt" else str(self.path(rel))
		payload = {"hook_event_name": "PostToolUse", "tool_name": tool, "cwd": str(self.root), "tool_input": {"file_path": native}}
		return subprocess.run([sys.executable, "-B", str(self.path(".tools/sync/generators.py")), "--hook"], input=json.dumps(payload),
			capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)

	def stamps(self, folder):
		return {path.relative_to(self.root).as_posix(): (path.stat().st_mtime_ns, path.read_bytes())
			for path in self.path(folder).rglob("*") if path.is_file()}

	def registry(self):
		return json.loads(self.read(".tools/sync/generators.json"))

	def save_registry(self, data):
		self.write(".tools/sync/generators.json", json.dumps(data, indent=2))


class SyncCase(unittest.TestCase):
	def setUp(self):
		self.temp = tempfile.TemporaryDirectory()
		self.mod = Mod(self.temp.name)
		first = self.mod.run()
		self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

	def tearDown(self):
		self.temp.cleanup()

	def assertInSync(self):
		result = self.mod.run("--check")
		self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class InstructionProjection(SyncCase):
	"""Criterion 1: a canonical instruction change regenerates or flags AGENTS.md."""

	def test_edit_regenerates_agents_md(self):
		self.mod.write("CLAUDE.md", self.mod.read("CLAUDE.md") + "\nA new rule.\n")
		stale = self.mod.run("--check")
		self.assertEqual(stale.returncode, 1)
		self.assertIn("DRIFT: AGENTS.md", stale.stdout)
		result = self.mod.hook("CLAUDE.md")
		self.assertEqual(result.returncode, 0, result.stderr)
		self.assertIn("A new rule.", self.mod.read("AGENTS.md"))
		context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
		self.assertIn("`AGENTS.md`", context)
		self.assertIn("Commit them together", context)
		self.assertInSync()

	def test_hand_edit_of_agents_md_is_refused_and_kept(self):
		self.mod.write("AGENTS.md", self.mod.read("AGENTS.md") + "\nHand edit.\n")
		result = self.mod.hook("AGENTS.md")
		self.assertEqual(result.returncode, 2)
		self.assertIn("generated by `.tools/sync/sync_instructions.py`", result.stderr)
		self.assertIn("`CLAUDE.md`", result.stderr)
		self.assertIn("Hand edit.", self.mod.read("AGENTS.md"), "the hook must not overwrite without a canonical change")
		restored = self.mod.run("--paths", "AGENTS.md")
		self.assertEqual(restored.returncode, 0, restored.stdout)
		self.assertNotIn("Hand edit.", self.mod.read("AGENTS.md"))

	def test_unused_replacement_is_reported(self):
		config = {"pairs": [{"source": "CLAUDE.md", "target": "AGENTS.md"}],
			"replacements": [["a phrase CLAUDE.md never contains", "x", ["CLAUDE.md"]]]}
		self.mod.write(".tools/sync/instruction_projection.json", json.dumps(config))
		result = self.mod.run("--check")
		self.assertEqual(result.returncode, 1)
		self.assertIn("UNUSED", result.stdout)

	def test_template_only_replacement_is_not_required_in_an_installed_mod(self):
		config = {"pairs": [{"source": "CLAUDE.md", "target": "AGENTS.md"}],
			"replacements": [["phrase only in the template", "x", ["CLAUDE_template.md"]]]}
		self.mod.write(".tools/sync/instruction_projection.json", json.dumps(config))
		self.assertInSync()


class SkillCopies(SyncCase):
	"""Criterion 2: a canonical skill change updates or flags its runtime copies, and only that skill's."""

	def test_mirror_required_by_codex_was_created(self):
		self.assertEqual(self.mod.read(".agents/skills/skill-a/SKILL.md"), self.mod.read(".claude/skills/skill-a/SKILL.md"))

	def test_edit_refreshes_only_that_skill(self):
		untouched = self.mod.stamps(".agents/skills/skill-b")
		agents_before = self.mod.stamps(".codex")
		self.mod.write(".claude/skills/skill-a/SKILL.md", "---\nname: skill-a\n---\nSkill A, revised.\n")
		result = self.mod.hook(".claude/skills/skill-a/SKILL.md")
		self.assertEqual(result.returncode, 0, result.stderr)
		self.assertIn("revised", self.mod.read(".agents/skills/skill-a/SKILL.md"))
		self.assertIn("`.agents/skills/skill-a/SKILL.md`", json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"])
		self.assertEqual(self.mod.stamps(".agents/skills/skill-b"), untouched)
		self.assertEqual(self.mod.stamps(".codex"), agents_before, "a skill edit must not start the agent generator")

	def test_new_reference_file_is_copied_and_removed_file_is_deleted(self):
		self.mod.write(".claude/skills/skill-b/references/more.md", "More.\n")
		self.assertEqual(self.mod.hook(".claude/skills/skill-b/references/more.md").returncode, 0)
		self.assertTrue(self.mod.path(".agents/skills/skill-b/references/more.md").is_file())
		self.mod.path(".claude/skills/skill-b/references/more.md").unlink()
		self.assertEqual(self.mod.run("--check").returncode, 1)
		self.assertEqual(self.mod.run().returncode, 0)
		self.assertFalse(self.mod.path(".agents/skills/skill-b/references/more.md").exists())

	def test_missing_required_mirror_fails_the_check(self):
		shutil.rmtree(self.mod.path(".agents"))
		result = self.mod.run("--check")
		self.assertEqual(result.returncode, 1)
		self.assertIn(".agents/skills is missing", result.stdout)

	def test_tool_caches_are_not_skill_content(self):
		# check.py full runs mypy on skill tools, which writes .mypy_cache next to them.
		for cache in (".mypy_cache", ".ruff_cache", ".pytest_cache"):
			self.mod.write(f".claude/skills/skill-a/tools/{cache}/3.9/x.json", "{}\n")
		self.assertEqual(self.mod.run("--check").returncode, 0)
		self.assertEqual(self.mod.run().returncode, 0)
		self.assertFalse(self.mod.path(".agents/skills/skill-a/tools").exists())

	def test_hand_edit_of_a_copy_is_refused(self):
		self.mod.write(".agents/skills/skill-a/SKILL.md", "edited copy\n")
		result = self.mod.hook(".agents/skills/skill-a/SKILL.md")
		self.assertEqual(result.returncode, 2)
		self.assertIn("`.claude/skills/skill-a/`", result.stderr)


class SourcePackageMirror(unittest.TestCase):
	"""The skill check is not vacuous: a mirror built from the source package round-trips and detects mutation."""

	def test_round_trip(self):
		with tempfile.TemporaryDirectory() as folder:
			mod = Mod(folder, source_package=True)
			skills = [sys.executable, "-B", str(mod.path(".tools/sync/sync_skills.py")), "--root", str(mod.root)]
			nothing = subprocess.run(skills + ["--check"], capture_output=True, text=True)
			self.assertEqual(nothing.returncode, 0)
			self.assertIn("source package", nothing.stdout)
			self.assertEqual(subprocess.run(skills + ["--target", "agents"], capture_output=True).returncode, 0)
			self.assertEqual(subprocess.run(skills + ["--check"], capture_output=True).returncode, 0)
			mod.write(".agents/skills/skill-b/references/notes.md", "mutated\n")
			drift = subprocess.run(skills + ["--check"], capture_output=True, text=True)
			self.assertEqual(drift.returncode, 1)
			self.assertIn("changed references/notes.md", drift.stdout)


class AgentProjections(SyncCase):
	"""Criterion 3: adding, modifying or removing an agent updates or flags its projections."""

	def codex_rows(self):
		return [line for line in self.mod.read(".codex/config.toml").splitlines() if line.startswith("[agents.")]

	def test_add_modify_remove(self):
		self.mod.write(".claude/agents/hoi4-gamma.md", agent_text("hoi4-gamma"))
		self.assertEqual(self.mod.hook(".claude/agents/hoi4-gamma.md", tool="Write").returncode, 0)
		self.assertTrue(self.mod.path(".codex/agents/hoi4_gamma.toml").is_file())
		self.assertIn("[agents.hoi4_gamma]", self.codex_rows())
		self.assertIn("hoi4-gamma", self.mod.read(".claude/agent-map.md"))

		self.mod.write(".claude/agents/hoi4-gamma.md", agent_text("hoi4-gamma", "Does a changed job."))
		self.assertEqual(self.mod.hook(".claude/agents/hoi4-gamma.md").returncode, 0)
		self.assertIn("Does a changed job.", self.mod.read(".codex/agents/hoi4_gamma.toml"))

		self.mod.path(".claude/agents/hoi4-gamma.md").unlink()
		stale = self.mod.run("--check")
		self.assertEqual(stale.returncode, 1)
		self.assertIn("STALE: .codex/agents/hoi4_gamma.toml", stale.stdout)
		self.assertEqual(self.mod.run().returncode, 0)
		self.assertFalse(self.mod.path(".codex/agents/hoi4_gamma.toml").exists())
		self.assertNotIn("[agents.hoi4_gamma]", self.codex_rows())

	def test_count_is_derived_from_the_folder(self):
		for index in range(3):
			self.mod.write(f".claude/agents/hoi4-extra-{index}.md", agent_text(f"hoi4-extra-{index}"))
		self.assertEqual(self.mod.run().returncode, 0)
		self.assertEqual(len(self.codex_rows()), 5)

	def test_malformed_agent_fails_visibly(self):
		self.mod.write(".claude/agents/hoi4-broken.md", "no frontmatter here\n")
		result = self.mod.hook(".claude/agents/hoi4-broken.md")
		self.assertEqual(result.returncode, 2)
		self.assertIn("frontmatter", result.stderr)
		self.assertEqual(self.mod.run("--check").returncode, 2)


class Targeting(SyncCase):
	"""Criterion 4: edits outside the registry start nothing, and each edit starts only its own generator."""

	def setUp(self):
		super().setUp()
		self.log = self.mod.path("sentinel.log")
		self.mod.write(".tools/sync/sentinel.py", "import sys\nfrom pathlib import Path\n"
			f"Path({str(self.log)!r}).open('a').write(' '.join(sys.argv[1:]) + '\\n')\n")
		data = self.mod.registry()
		data["generators"].append({"id": "sentinel", "script": ".tools/sync/sentinel.py", "inputs": [".claude/agents/*.md"]})
		self.mod.save_registry(data)

	def test_unrelated_paths_start_nothing(self):
		for rel in ("events/fixture_events.txt", "localisation/english/fixture_l_english.yml", "common/national_focus/x.txt",
				"docs/specs/a.md", ".claude/settings.json"):
			self.mod.write(rel, "x\n")
			started = time.monotonic()
			result = self.mod.hook(rel)
			self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""), rel)
			self.assertLess(time.monotonic() - started, 10, rel)
		self.assertFalse(self.log.exists(), "no generator may start for an unrelated path")

	def test_skill_edit_does_not_start_agent_entries(self):
		self.mod.write(".claude/skills/skill-a/SKILL.md", "---\nname: skill-a\n---\nChanged.\n")
		self.assertEqual(self.mod.hook(".claude/skills/skill-a/SKILL.md").returncode, 0)
		self.assertFalse(self.log.exists())
		self.mod.write(".claude/agents/hoi4-alpha.md", agent_text("hoi4-alpha", "Changed."))
		self.assertEqual(self.mod.hook(".claude/agents/hoi4-alpha.md").returncode, 0)
		self.assertTrue(self.log.exists())

	def test_file_outside_any_project_is_ignored(self):
		with tempfile.TemporaryDirectory() as other:
			outside = Path(other) / "CLAUDE.md"
			outside.write_text("x\n", encoding="utf-8")
			payload = {"tool_name": "Edit", "tool_input": {"file_path": str(outside)}}
			result = subprocess.run([sys.executable, "-B", str(SYNC / "generators.py"), "--hook"], input=json.dumps(payload),
				capture_output=True, text=True)
			self.assertEqual((result.returncode, result.stdout), (0, ""))


class Detection(SyncCase):
	"""Criterion 5: the check that CI runs fails on every kind of stale projection."""

	def test_each_mutation_fails_the_check(self):
		mutations = (
			("AGENTS.md", "stale\n"),
			(".codex/agents/hoi4_alpha.toml", "stale = true\n"),
			(".claude/agent-map.md", "stale\n"),
			(".agents/skills/skill-b/references/notes.md", "stale\n"),
		)
		for rel, text in mutations:
			original = self.mod.read(rel)
			self.mod.write(rel, text)
			result = self.mod.run("--check")
			self.assertEqual(result.returncode, 1, rel)
			self.mod.write(rel, original)
		self.assertInSync()

	def test_check_py_reports_stale_projection_as_an_error(self):
		self.mod.write("AGENTS.md", "stale\n")
		with patch.object(check, "REPO_ROOT", self.mod.root):
			findings, failure = check.run_generators(None)
		self.assertIsNone(failure)
		self.assertTrue(any(finding.rule == "GEN-STALE" and finding.level == "error" for finding in findings))

	def test_staged_check_covers_committed_layout(self):
		git = ["git", "-c", "core.autocrlf=false", "-C", str(self.mod.root)]
		subprocess.run(git + ["init", "-q"], check=True)
		subprocess.run(git + ["add", "-A"], check=True)
		self.mod.write("CLAUDE.md", self.mod.read("CLAUDE.md") + "\nUnsynced rule.\n")
		subprocess.run(git + ["add", "CLAUDE.md"], check=True)
		result = self.mod.run("--check", "--staged")
		self.assertEqual(result.returncode, 1)
		self.assertIn("DRIFT: AGENTS.md", result.stdout)


class SetupCompatibility(SyncCase):
	"""Criterion 6: Setup's finishing step regenerates only paths HOI4 Mod Setup lets it rewrite."""

	def test_outputs_stay_inside_setups_allowlist(self):
		for entry in generators.load_registry(SYNC.parents[1]):
			for pattern in entry.outputs:
				if pattern.endswith("_template.md"):
					continue  # exists only in the source package
				allowed = pattern in SETUP_REWRITABLE_EXACT or pattern.startswith(SETUP_REWRITABLE_PREFIXES)
				self.assertTrue(allowed, f"{entry.id} writes {pattern}, which HOI4 Mod Setup refuses after check.py setup")

	def test_finish_setup_repairs_an_installed_mod(self):
		shutil.rmtree(self.mod.path(".agents"))
		self.mod.write("AGENTS.md", "stale\n")
		before = {rel: data for rel, (_, data) in self.mod.stamps(".claude").items()}
		with patch.object(check, "REPO_ROOT", self.mod.root):
			self.assertEqual(check.finish_setup(), 0)
		self.assertInSync()
		after = {rel: data for rel, (_, data) in self.mod.stamps(".claude").items()}
		changed = {rel for rel in set(before) | set(after) if before.get(rel) != after.get(rel)}
		self.assertTrue(changed <= {".claude/agent-map.md"}, changed)

	def test_finish_setup_reports_a_broken_generator(self):
		self.mod.write(".tools/sync/sync_skills.py", "raise SystemExit(3)\n")
		with patch.object(check, "REPO_ROOT", self.mod.root):
			self.assertEqual(check.finish_setup(), 2)

	def test_git_hook_is_written_once_and_never_over_a_foreign_hook(self):
		subprocess.run(["git", "-C", str(self.mod.root), "init", "-q"], check=True)
		with patch.object(check, "REPO_ROOT", self.mod.root):
			self.assertEqual(check.install_git_hook(), 0)
			hook = self.mod.path(".git/hooks/pre-commit")
			self.assertIn("generators.py --check --staged", hook.read_text(encoding="utf-8"))
			self.assertEqual(check.install_git_hook(), 0)
			hook.write_text("#!/bin/sh\necho mine\n", encoding="utf-8")
			self.assertEqual(check.install_git_hook(), 1)
			self.assertIn("echo mine", hook.read_text(encoding="utf-8"))


class VisibleFailures(SyncCase):
	"""Criterion 7: a broken generator or registry can never pass silently."""

	def test_missing_script_cannot_run(self):
		self.mod.path(".tools/sync/sync_instructions.py").unlink()
		result = self.mod.run("--check")
		self.assertEqual(result.returncode, 2)
		self.assertIn("MISSING", result.stdout)
		with patch.object(check, "REPO_ROOT", self.mod.root):
			_, failure = check.run_generators(None)
		self.assertIn("sync_instructions.py", failure or "")

	def test_missing_or_invalid_registry_cannot_run(self):
		self.mod.write(".tools/sync/generators.json", "{not json")
		self.assertEqual(self.mod.run("--check").returncode, 2)
		self.mod.path(".tools/sync/generators.json").unlink()
		self.assertEqual(self.mod.run("--check").returncode, 2)

	def test_crashing_generator_fails_check_and_hook(self):
		self.mod.write(".tools/sync/sync_instructions.py", "this is not python\n")
		self.assertEqual(self.mod.run("--check").returncode, 2)
		self.mod.write("CLAUDE.md", self.mod.read("CLAUDE.md") + "\nMore.\n")
		result = self.mod.hook("CLAUDE.md")
		self.assertEqual(result.returncode, 2)
		self.assertIn("failed", result.stderr)

	def test_nothing_to_check_is_an_error(self):
		with tempfile.TemporaryDirectory() as folder:
			empty = Path(folder)
			shutil.copytree(SYNC, empty / ".tools" / "sync", ignore=shutil.ignore_patterns("__pycache__"))
			result = subprocess.run([sys.executable, "-B", str(empty / ".tools/sync/generators.py"), "--check"],
				capture_output=True, text=True)
			self.assertEqual(result.returncode, 2)
			self.assertIn("nothing was checked", result.stderr)

	def test_needs_cycle_is_rejected(self):
		data = self.mod.registry()
		data["generators"][0]["needs"] = ["guidance"]
		self.mod.save_registry(data)
		result = self.mod.run("--check")
		self.assertEqual(result.returncode, 2)
		self.assertIn("cycle", result.stderr)


class LegacyGenerator(SyncCase):
	"""A generator that predates the runner: its own interpreter, check flag and drift wording, and no --root."""

	def setUp(self):
		super().setUp()
		self.mod.write(".tools/sync/legacy.py", "import sys\nfrom pathlib import Path\n"
			"root = Path(__file__).resolve().parents[2]\n"
			"assert '--root' not in sys.argv\n"
			"source, target = root / 'legacy.src', root / 'legacy.out'\n"
			"want = source.read_text() if source.exists() else ''\n"
			"if '--verify' in sys.argv:\n"
			"    have = target.read_text() if target.exists() else None\n"
			"    if have != want:\n"
			"        print('Would update legacy.out')\n"
			"        sys.exit(1)\n"
			"    print('legacy.out in sync')\n"
			"else:\n"
			"    target.write_text(want)\n")
		data = self.mod.registry()
		data["generators"].append({"id": "legacy", "script": ".tools/sync/legacy.py", "interpreter": [sys.executable],
			"root_args": [], "check_args": ["--verify"], "stale_markers": ["Would update"],
			"inputs": ["legacy.src"], "outputs": ["legacy.out"]})
		self.mod.save_registry(data)

	def test_legacy_contract(self):
		self.mod.write("legacy.src", "v1\n")
		stale = self.mod.run("--check", "--paths", "legacy.src")
		self.assertEqual(stale.returncode, 1, stale.stdout + stale.stderr)
		self.assertIn("Would update legacy.out", stale.stdout)
		self.assertEqual(self.mod.hook("legacy.src").returncode, 0)
		self.assertEqual(self.mod.read("legacy.out"), "v1\n")
		self.assertInSync()


class GuidanceSize(SyncCase):
	"""The single-read ceiling measures content, so CRLF from a Windows checkout does not push a file over it."""

	def size_check(self, text):
		self.mod.write("CLAUDE.md", "")
		self.mod.path("CLAUDE.md").write_bytes(text)
		return subprocess.run([sys.executable, "-B", str(self.mod.path(".tools/sync/check_guidance_size.py")), "--root", str(self.mod.root)],
			capture_output=True, text=True)

	def test_crlf_does_not_count(self):
		line = b"x" * 99 + b"\n"
		under = line * 595  # 59,500 bytes with LF, 60,095 with CRLF
		self.assertEqual(self.size_check(under.replace(b"\n", b"\r\n")).returncode, 0)

	def test_content_over_the_ceiling_still_fails(self):
		over = (b"x" * 99 + b"\n") * 610  # 61,000 bytes with LF
		result = self.size_check(over)
		self.assertEqual(result.returncode, 1)
		self.assertIn("OVER: CLAUDE.md", result.stdout)


class Concurrency(SyncCase):
	def test_parallel_hooks_both_finish(self):
		self.mod.write(".claude/skills/skill-a/SKILL.md", "---\nname: skill-a\n---\nParallel A.\n")
		self.mod.write(".claude/skills/skill-b/SKILL.md", "---\nname: skill-b\n---\nParallel B.\n")
		with ThreadPoolExecutor(max_workers=2) as pool:
			results = list(pool.map(self.mod.hook, (".claude/skills/skill-a/SKILL.md", ".claude/skills/skill-b/SKILL.md")))
		self.assertEqual([result.returncode for result in results], [0, 0], [result.stderr for result in results])
		self.assertFalse(self.mod.path(".tmp/generators.lock").exists())
		self.assertInSync()


class Patterns(unittest.TestCase):
	def test_item_capture_and_folder_boundaries(self):
		self.assertEqual(generators.match([".claude/skills/{item}/**"], ".claude/skills/hoi4-mtth/references/a.md"), (True, "hoi4-mtth"))
		self.assertEqual(generators.match([".claude/agents/*.md"], ".claude/agents/sub/x.md"), (False, None))
		self.assertEqual(generators.match(["CLAUDE.md"], "docs/CLAUDE.md"), (False, None))

	def test_needs_rerun_dependants(self):
		entries = generators.load_registry(SYNC.parents[1])
		chosen = generators.select(entries, ["CLAUDE.md"])
		self.assertEqual(sorted(chosen), ["guidance", "instructions"])
		chosen = generators.select(entries, [".claude/skills/hoi4-mtth/SKILL.md"])
		self.assertEqual(chosen["skills"].items, {"hoi4-mtth"})
		self.assertFalse(chosen["skills"].whole)
		self.assertEqual(sorted(generators.select(entries, [".tools/sync/generators.json"])), sorted(entry.id for entry in entries))


if __name__ == "__main__":
	unittest.main()
