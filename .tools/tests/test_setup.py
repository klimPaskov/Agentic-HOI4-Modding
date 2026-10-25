"""Tests for `check.py setup` (`.tools/lib/setup.py`) and the doctor's HOI4 Agent Tools workspace check.

Every case works in a temporary mod folder; no package is installed and no real configuration is read.
Run from the repository root: `python -B -m unittest discover -s .tools/tests -p "test_setup.py"`.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

from lib import doctor, game, setup


class Setup(unittest.TestCase):
	def setUp(self):
		self.temp = tempfile.TemporaryDirectory()
		self.mod = Path(self.temp.name) / "mods" / "my_mod"
		(self.mod / ".tools" / "sync").mkdir(parents=True)

	def tearDown(self):
		self.temp.cleanup()

	def test_ignores_are_added_once(self):
		(self.mod / ".gitignore").write_text("*.pyc", encoding="utf-8")
		self.assertIn("added", setup.ensure_ignores(self.mod))
		self.assertIn("already", setup.ensure_ignores(self.mod))
		lines = (self.mod / ".gitignore").read_text(encoding="utf-8").splitlines()
		self.assertEqual(lines[0], "*.pyc")
		self.assertEqual([line for line in lines if line in setup.IGNORE_LINES], list(setup.IGNORE_LINES))

	def test_game_dir_is_recorded_only_when_valid(self):
		settings = Path(self.temp.name) / "local_settings.json"
		folder = Path(self.temp.name) / "game"
		with patch.object(game, "LOCAL_SETTINGS", settings):
			self.assertIn("nothing recorded", setup.record_game_dir(folder))
			self.assertFalse(settings.exists())
			(folder / "common").mkdir(parents=True)
			(folder / "localisation").mkdir()
			self.assertIn("recorded", setup.record_game_dir(folder))
			self.assertEqual(json.loads(settings.read_text(encoding="utf-8"))["hoi4_game_dir"], folder.resolve().as_posix())

	def test_only_installed_synchronizers_run(self):
		self.assertEqual(setup.run_synchronizers(self.mod), ["synchronizers: none installed"])
		(self.mod / ".tools" / "sync" / "sync_skills.py").write_text("print('skills in sync')\n", encoding="utf-8")
		self.assertEqual(setup.run_synchronizers(self.mod), ["sync_skills.py: ok: skills in sync"])

	def test_report_runs_in_a_fresh_interpreter(self):
		# Packages pip installs into a site folder created after this process started are invisible here,
		# so the closing doctor report must come from a new interpreter.
		marker = Path(self.temp.name) / "doctor_pid.txt"
		(self.mod / ".tools" / "check.py").write_text(
			f"import os, sys\nopen({str(marker)!r}, 'w').write(str(os.getpid()))\n"
			"raise SystemExit(3 if sys.argv[1:] == ['doctor'] else 9)\n", encoding="utf-8")
		with patch.object(game, "LOCAL_SETTINGS", Path(self.temp.name) / "local_settings.json"), \
				patch.object(setup, "adopt_quality", lambda root: "quality: skipped in test"):
			self.assertEqual(setup.run(self.mod, None, install=False), 3)
		self.assertNotEqual(marker.read_text(encoding="utf-8"), str(os.getpid()))

	def test_missing_packages_are_reported_without_install(self):
		with patch.object(doctor, "PYTHON_MODULES", (("no_such_module_for_setup_test", "nosuchpackage", "a test"),)):
			self.assertIn("missing nosuchpackage", setup.install_packages(self.mod, allowed=False))


class Workspace(unittest.TestCase):
	def setUp(self):
		self.temp = tempfile.TemporaryDirectory()
		self.mods = Path(self.temp.name) / "mods"
		self.mod = self.mods / "my_mod"
		self.mod.mkdir(parents=True)
		self.config = Path(self.temp.name) / "config.json"
		(self.mod / ".mcp.json").write_text(json.dumps({"mcpServers": {"hoi4_agent_tools": {
			"command": "hoi4-agent-tools", "env": {"HOI4_AGENT_CONFIG": str(self.config)}}}}), encoding="utf-8")

	def tearDown(self):
		self.temp.cleanup()

	def test_no_configuration_selects_the_mod_folder(self):
		self.assertTrue(doctor.workspace_item(self.mod).ok)

	def test_mod_roots_must_cover_the_mod(self):
		self.config.write_text(json.dumps({"version": 1, "modRoots": [str(Path(self.temp.name) / "elsewhere")]}), encoding="utf-8")
		item = doctor.workspace_item(self.mod)
		self.assertFalse(item.ok)
		self.assertIn("modRoots", item.fix)
		self.config.write_text(json.dumps({"version": 1, "modRoots": [str(self.mods)]}), encoding="utf-8")
		self.assertTrue(doctor.workspace_item(self.mod).ok)

	def test_explicit_workspace_covers_the_mod(self):
		self.config.write_text(json.dumps({"version": 1, "workspaces": [{"id": "m", "name": "M", "root": str(self.mod)}]}),
			encoding="utf-8")
		self.assertTrue(doctor.workspace_item(self.mod).ok)

	def test_default_path_is_used_without_registration(self):
		(self.mod / ".mcp.json").write_text(json.dumps({"mcpServers": {"hoi4_agent_tools": {"command": "x"}}}), encoding="utf-8")
		with patch.dict(os.environ, {"APPDATA": self.temp.name, "HOI4_AGENT_CONFIG": ""}):
			self.assertEqual(doctor.server_config_path(self.mod), Path(self.temp.name) / "hoi4-agent-tools" / "config.json")


if __name__ == "__main__":
	unittest.main()
