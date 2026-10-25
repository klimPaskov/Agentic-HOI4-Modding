"""Tests for the game-folder lookup in `.tools/lib/game.py` and the `check.py doctor` report.

Every case uses temporary folders and patched Steam roots, so no real game installation is read.
Run from the repository root: `python -B -m unittest discover -s .tools/tests -p "test_game_dir.py"`.
"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

from lib import doctor, game


def make_game(folder: Path) -> Path:
	(folder / "common").mkdir(parents=True)
	(folder / "localisation").mkdir()
	return folder


class GameDir(unittest.TestCase):
	def setUp(self):
		self.temp = tempfile.TemporaryDirectory()
		self.root = Path(self.temp.name)
		self.settings = self.root / "local_settings.json"
		self.patches = [patch.object(game, "LOCAL_SETTINGS", self.settings), patch.dict(os.environ, {}, clear=False)]
		for active in self.patches:
			active.start()
		os.environ.pop(game.ENVIRONMENT_VARIABLE, None)

	def tearDown(self):
		for active in reversed(self.patches):
			active.stop()
		self.temp.cleanup()

	def test_steam_library_from_libraryfolders_vdf(self):
		steam = self.root / "Steam"
		library = self.root / "Library Two"
		(steam / "steamapps").mkdir(parents=True)
		escaped = str(library).replace("\\", "\\\\")
		(steam / "steamapps" / "libraryfolders.vdf").write_text(
			'"libraryfolders"\n{\n\t"0"\n\t{\n\t\t"path"\t\t"' + escaped + '"\n\t}\n}\n', encoding="utf-8")
		expected = make_game(library / "steamapps" / "common" / "Hearts of Iron IV")
		with patch.object(game, "steam_roots", lambda: iter([steam])):
			self.assertEqual(game.game_dir().resolve(), expected.resolve())
			self.assertIsNone(game.missing_game_dir())

	def test_local_setting_beats_discovery_and_environment_beats_both(self):
		recorded = make_game(self.root / "recorded")
		game.save_local_setting(recorded)
		self.assertEqual(json.loads(self.settings.read_text(encoding="utf-8"))["hoi4_game_dir"], recorded.resolve().as_posix())
		with patch.object(game, "steam_roots", lambda: iter([])):
			self.assertEqual(game.game_dir().resolve(), recorded.resolve())
			os.environ[game.ENVIRONMENT_VARIABLE] = str(self.root / "elsewhere")
			self.assertEqual(game.game_dir(), self.root / "elsewhere")
			self.assertIn("doctor --save-game-dir", game.missing_game_dir() or "")
			self.assertEqual(game.require_game_dir(), 2)

	def test_doctor_records_a_game_folder_and_refuses_a_wrong_one(self):
		recorded = make_game(self.root / "game")
		with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
			self.assertEqual(doctor.run(self.root, save_game_dir=self.root / "not_a_game"), 2)
			doctor.run(self.root, save_game_dir=recorded)
		self.assertEqual(game.local_setting(), Path(recorded.resolve().as_posix()))


if __name__ == "__main__":
	unittest.main()
