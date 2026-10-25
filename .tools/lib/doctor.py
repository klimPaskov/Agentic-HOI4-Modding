"""Environment report for `.tools/check.py doctor`: what the checks need and how to fix each gap.

Each item is `required` (a check cannot run without it) or `optional` (its check is skipped with a
notice). The report reads the machine and writes nothing, except `--save-game-dir`, which records the
game folder in the machine-local `.tools/local_settings.json`.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, NamedTuple, Optional, Sequence

from lib import game

PYTHON_MODULES = (
	("PIL", "Pillow", "gfx and asset tools"),
	("numpy", "numpy", "gfx checks"),
	("scipy", "scipy", "gfx checks"),
	("openpyxl", "openpyxl", "spreadsheet tools and exports"),
)
INSTALL_REQUIREMENTS = "python -m pip install -r .tools/requirements.txt"
IGNORED_PATHS = (".tmp/", ".tools/local_settings.json")


class Item(NamedTuple):
	name: str
	ok: bool
	required: bool
	detail: str
	fix: str


def python_items() -> List[Item]:
	version = sys.version_info
	items = [Item("python", version >= (3, 9), True, f"{version.major}.{version.minor}.{version.micro} at {sys.executable}",
		"install Python 3.9 or newer")]
	for module, package, used_by in PYTHON_MODULES:
		present = importlib.util.find_spec(module) is not None
		items.append(Item(package, present, True, f"needed by the {used_by}", INSTALL_REQUIREMENTS))
	return items


def game_item() -> Item:
	root = game.game_dir()
	if game.is_game_dir(root):
		return Item("game folder", True, True, root.as_posix(), "")
	return Item("game folder", False, True, f"not found at {root.as_posix()}",
		f"set {game.ENVIRONMENT_VARIABLE}, or run `python -B .tools/check.py doctor --save-game-dir <folder>`")


def executable_item(name: str, required: bool, purpose: str, fix: str) -> Item:
	found = shutil.which(name)
	return Item(name, found is not None, required, found or f"not on PATH ({purpose})", fix)


def mcp_item(repo_root: Path) -> Item:
	"""Check that the HOI4 Agent Tools command in `.mcp.json` resolves; the server is not started."""
	try:
		servers = json.loads((repo_root / ".mcp.json").read_text(encoding="utf-8")).get("mcpServers", {})
		command = str(servers["hoi4_agent_tools"]["command"])
	except (OSError, ValueError, KeyError, AttributeError):
		return Item("HOI4 Agent Tools", False, False, "no hoi4_agent_tools server in .mcp.json (changed-file script validation)",
			"install it with HOI4 Mod Setup or `python .tools/mcp/bootstrap_hoi4_agent_tools.py`")
	found = shutil.which(command) or (command if Path(command).is_file() else None)
	return Item("HOI4 Agent Tools", found is not None, False, found or f"`{command}` not found (changed-file script validation)",
		"install it with HOI4 Mod Setup or `python .tools/mcp/bootstrap_hoi4_agent_tools.py`")


def server_config_path(repo_root: Path) -> Path:
	"""Return the configuration file the HOI4 Agent Tools server reads (its documented lookup order)."""
	try:
		entry = json.loads((repo_root / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["hoi4_agent_tools"]
		configured = str(entry.get("env", {}).get("HOI4_AGENT_CONFIG", ""))
	except (OSError, ValueError, KeyError, AttributeError):
		configured = ""
	configured = configured or os.environ.get("HOI4_AGENT_CONFIG", "")
	if configured:
		return Path(configured)
	if os.environ.get("APPDATA"):
		return Path(os.environ["APPDATA"]) / "hoi4-agent-tools" / "config.json"
	base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
	return Path(base) / "hoi4-agent-tools" / "config.json"


def same_path(left: Path, right: Path) -> bool:
	return os.path.normcase(str(left.resolve())) == os.path.normcase(str(right.resolve()))


def workspace_item(repo_root: Path) -> Item:
	"""Check that the server can select this mod: no configuration, or a modRoots entry or workspace that covers it."""
	config = server_config_path(repo_root)
	fix = f"add {repo_root.parent.as_posix()} to `modRoots` (or this mod to `workspaces`) in {config.as_posix()}"
	if not config.is_file():
		return Item("HOI4 Agent Tools workspace", True, False, "no server configuration; the server selects this mod from its folder", "")
	try:
		settings = json.loads(config.read_text(encoding="utf-8"))
		roots = [Path(str(root)) for root in settings.get("modRoots", [])]
		workspaces = [Path(str(entry.get("root", ""))) for entry in settings.get("workspaces", []) if entry.get("kind", "mod") == "mod"]
	except (OSError, ValueError, AttributeError):
		return Item("HOI4 Agent Tools workspace", False, False, f"cannot read {config.as_posix()}", fix)
	covered = any(same_path(repo_root.parent, root) for root in roots) or any(same_path(repo_root, root) for root in workspaces)
	return Item("HOI4 Agent Tools workspace", covered, False,
		f"registered in {config.as_posix()}" if covered else f"this mod is not a workspace in {config.as_posix()} (changed-file script validation)",
		"" if covered else fix)

def ignore_item(repo_root: Path) -> Item:
	try:
		completed = subprocess.run(["git", "check-ignore", "--no-index", *IGNORED_PATHS], cwd=repo_root,
			capture_output=True, text=True, timeout=30)
	except (OSError, subprocess.SubprocessError):
		return Item("git ignores", False, False, "git is not available", "install Git")
	ignored = set(completed.stdout.split())
	missing = [path for path in IGNORED_PATHS if path not in ignored]
	return Item("git ignores", not missing, False, "ok" if not missing else "not ignored: " + ", ".join(missing),
		"add " + " and ".join(missing) + " to .gitignore" if missing else "")


def run(repo_root: Path, extra: Sequence[Item] = (), save_game_dir: Optional[Path] = None) -> int:
	"""Print the report; return 0 when every required item is present, else 1 (2 for a bad --save-game-dir)."""
	if save_game_dir is not None:
		if not game.is_game_dir(save_game_dir):
			print(f"{save_game_dir} is not a Hearts of Iron IV folder (it needs common/ and localisation/)", file=sys.stderr)
			return 2
		game.save_local_setting(save_game_dir)
		print(f"recorded {save_game_dir.resolve().as_posix()} in {game.LOCAL_SETTINGS.as_posix()}")
	items = [*python_items(), game_item(),
		executable_item("git", True, "changed-file detection", "install Git"),
		executable_item("uvx", False, "ruff and mypy for the quality check", "install uv: https://docs.astral.sh/uv/"),
		mcp_item(repo_root), workspace_item(repo_root), ignore_item(repo_root), *extra]
	for item in items:
		state = "ok" if item.ok else ("MISSING" if item.required else "optional")
		line = f"{state:8s} {item.name}: {item.detail}"
		if not item.ok and item.fix:
			line += f"\n         fix: {item.fix}"
		print(line)
	missing = [item.name for item in items if item.required and not item.ok]
	print("doctor: ready for `check.py full`" if not missing else f"doctor: {len(missing)} required item(s) missing: {', '.join(missing)}")
	return 1 if missing else 0
