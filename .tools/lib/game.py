"""Location of the installed Hearts of Iron IV game for tools that read vanilla files.

Tools take the game directory from the `HOI4_GAME_DIR` environment variable and fall back to the
default Steam path. A tool that cannot work without the game calls `require_game_dir()` in
`main()` and returns its result, so a missing installation exits 2 with a message that names
the variable instead of silently skipping the vanilla comparison.

	$env:HOI4_GAME_DIR = "D:/Games/Hearts of Iron IV"   # PowerShell
	export HOI4_GAME_DIR="/mnt/d/Games/Hearts of Iron IV" # POSIX shells
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

ENVIRONMENT_VARIABLE = "HOI4_GAME_DIR"
DEFAULT_GAME_DIR = Path("C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV")


def game_dir() -> Path:
	"""Return the configured game directory without checking that it exists."""
	configured = os.environ.get(ENVIRONMENT_VARIABLE, "").strip()
	return Path(configured) if configured else DEFAULT_GAME_DIR


def missing_game_dir() -> Optional[str]:
	"""Return a message when the configured directory is not a game installation, else None."""
	root = game_dir()
	if (root / "common").is_dir() and (root / "localisation").is_dir():
		return None
	return (f"Hearts of Iron IV was not found at {root}; set {ENVIRONMENT_VARIABLE} to the game folder "
		"(the one containing common/ and localisation/)")


def require_game_dir() -> Optional[int]:
	"""Print the missing-game message and return exit status 2, or return None when the game is present."""
	message = missing_game_dir()
	if message is None:
		return None
	print(message, file=sys.stderr)
	return 2
