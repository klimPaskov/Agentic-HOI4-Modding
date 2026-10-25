"""Location of the installed Hearts of Iron IV game for tools that read vanilla files.

The game folder is taken from, in order:

1. the `HOI4_GAME_DIR` environment variable;
2. `hoi4_game_dir` in the machine-local `.tools/local_settings.json` (not committed; HOI4 Mod Setup
   writes it, and `python -B .tools/check.py doctor --save-game-dir <folder>` can write it);
3. the Steam libraries found on this machine (default Steam folders, the Windows registry and each
   library listed in `steamapps/libraryfolders.vdf`);
4. the default Windows Steam path.

A tool that cannot work without the game calls `require_game_dir()` in `main()` and returns its
result, so a missing installation exits 2 with a message that says how to set the folder instead of
silently skipping the vanilla comparison.

	$env:HOI4_GAME_DIR = "D:/Games/Hearts of Iron IV"   # PowerShell
	export HOI4_GAME_DIR="/mnt/d/Games/Hearts of Iron IV" # POSIX shells
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Iterator, List, Optional

ENVIRONMENT_VARIABLE = "HOI4_GAME_DIR"
DEFAULT_GAME_DIR = Path("C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV")
LOCAL_SETTINGS = Path(__file__).resolve().parents[1] / "local_settings.json"
SETTINGS_KEY = "hoi4_game_dir"
GAME_FOLDER = Path("steamapps") / "common" / "Hearts of Iron IV"
LIBRARY_PATH = re.compile(r'"path"\s*"([^"]+)"')


def is_game_dir(folder: Path) -> bool:
	"""True when `folder` holds the game's script folders."""
	return (folder / "common").is_dir() and (folder / "localisation").is_dir()


def local_setting() -> Optional[Path]:
	"""Return the game folder recorded in `.tools/local_settings.json`, if any."""
	try:
		value = json.loads(LOCAL_SETTINGS.read_text(encoding="utf-8")).get(SETTINGS_KEY, "")
	except (OSError, ValueError, AttributeError):
		return None
	return Path(value) if isinstance(value, str) and value.strip() else None


def save_local_setting(folder: Path) -> None:
	"""Record `folder` as this machine's game folder in `.tools/local_settings.json`."""
	try:
		settings = json.loads(LOCAL_SETTINGS.read_text(encoding="utf-8"))
		if not isinstance(settings, dict):
			settings = {}
	except (OSError, ValueError):
		settings = {}
	settings[SETTINGS_KEY] = folder.resolve().as_posix()
	LOCAL_SETTINGS.write_text(json.dumps(settings, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def steam_roots() -> Iterator[Path]:
	"""Yield the Steam installation folders this platform normally uses."""
	home = Path.home()
	if sys.platform == "win32":
		try:
			import winreg

			with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
				yield Path(str(winreg.QueryValueEx(key, "SteamPath")[0]))
		except OSError:
			pass
		for variable in ("ProgramFiles(x86)", "ProgramFiles"):
			base = os.environ.get(variable)
			if base:
				yield Path(base) / "Steam"
	elif sys.platform == "darwin":
		yield home / "Library" / "Application Support" / "Steam"
	else:
		yield home / ".steam" / "steam"
		yield home / ".local" / "share" / "Steam"
		yield home / ".var" / "app" / "com.valvesoftware.Steam" / ".local" / "share" / "Steam"


def steam_game_dirs() -> List[Path]:
	"""Return every Hearts of Iron IV folder in the Steam libraries of this machine, best first."""
	found: List[Path] = []
	for root in steam_roots():
		libraries = [root]
		try:
			text = (root / "steamapps" / "libraryfolders.vdf").read_text(encoding="utf-8", errors="replace")
			libraries += [Path(match.replace("\\\\", "/")) for match in LIBRARY_PATH.findall(text)]
		except OSError:
			pass
		for library in libraries:
			folder = library / GAME_FOLDER
			if folder not in found and is_game_dir(folder):
				found.append(folder)
	return found


def game_dir() -> Path:
	"""Return the configured or discovered game directory without requiring that it exists."""
	configured = os.environ.get(ENVIRONMENT_VARIABLE, "").strip()
	if configured:
		return Path(configured)
	recorded = local_setting()
	if recorded is not None:
		return recorded
	discovered = steam_game_dirs()
	return discovered[0] if discovered else DEFAULT_GAME_DIR


def missing_game_dir() -> Optional[str]:
	"""Return a message when the resolved directory is not a game installation, else None."""
	root = game_dir()
	if is_game_dir(root):
		return None
	return (f"Hearts of Iron IV was not found at {root}. Set {ENVIRONMENT_VARIABLE} to the game folder (the one "
		"containing common/ and localisation/), or record it once with "
		"`python -B .tools/check.py doctor --save-game-dir <folder>`")


def require_game_dir() -> Optional[int]:
	"""Print the missing-game message and return exit status 2, or return None when the game is present."""
	message = missing_game_dir()
	if message is None:
		return None
	print(message, file=sys.stderr)
	return 2
