"""One-command preparation for `.tools/check.py setup`: make a mod ready for `check.py full`.

Run once after installing or updating the tooling (HOI4 Mod Setup runs it), and again whenever `doctor`
reports a gap. Each step is idempotent and reports what it did:

1. install the Python packages in `.tools/requirements.txt` when one is missing (skip with `--no-install`).
   When the system Python refuses packages (PEP 668 "externally managed", as on Debian and Ubuntu), they go
   into a project virtual environment at `.tools/.venv`, and `check.py` relaunches itself inside it;
2. record the game folder in the machine-local `.tools/local_settings.json` when `--game-dir` is given;
3. add the machine-local paths to `.gitignore`;
4. run the runtime synchronizers present in `.tools/sync/`, so generated projections match the installed
   canonical files;
5. adopt the quality findings of Python files the baseline has never seen (needs `uvx`; skipped without it);
6. print the `doctor` report and return its status.

Unlike `doctor`, this command writes: the packages, `.tools/local_settings.json`, `.gitignore`, the
synchronizers' generated files and `.tools/quality_baseline.json`. It never edits a canonical file.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from lib import doctor, game

IGNORE_LINES = ("/.tmp/", "/.tools/local_settings.json", "/.tools/.venv/")
VENV = Path(".tools") / ".venv"
SYNCHRONIZERS = ("sync_instructions.py", "sync_agents.py", "sync_skills.py")


def run_step(command: List[str], repo_root: Path) -> subprocess.CompletedProcess[str]:
	return subprocess.run(command, cwd=repo_root, capture_output=True, text=True, encoding="utf-8", errors="replace",
		stdin=subprocess.DEVNULL)


def last_line(completed: subprocess.CompletedProcess[str]) -> str:
	lines = [line for line in (completed.stdout + completed.stderr).splitlines() if line.strip()]
	return lines[-1].strip() if lines else "no output"


def project_python(repo_root: Path) -> Optional[Path]:
	"""Return the interpreter of the project virtual environment, if `setup` created one."""
	folder = repo_root / VENV
	for candidate in (folder / "Scripts" / "python.exe", folder / "bin" / "python"):
		if candidate.is_file():
			return candidate
	return None


def relaunch_in_project_venv(repo_root: Path, argv: List[str]) -> Optional[int]:
	"""Rerun `check.py` inside `.tools/.venv` when it exists and this is another interpreter; else None."""
	venv = project_python(repo_root)
	if venv is None or os.environ.get("HOI4_CHECKS_IN_VENV") == "1":
		return None
	# A venv interpreter is often a symlink to the system one, so compare environments, not executables.
	if os.path.normcase(str(Path(sys.prefix).resolve())) == os.path.normcase(str((repo_root / VENV).resolve())):
		return None
	environment = {**os.environ, "HOI4_CHECKS_IN_VENV": "1"}
	return subprocess.run([str(venv), "-B", *argv], cwd=repo_root, env=environment).returncode


def pip_install(python: str, repo_root: Path) -> subprocess.CompletedProcess[str]:
	return run_step([python, "-m", "pip", "install", "--disable-pip-version-check", "-r",
		str(repo_root / ".tools" / "requirements.txt")], repo_root)


def install_packages(repo_root: Path, allowed: bool) -> str:
	missing = [package for module, package, _ in doctor.PYTHON_MODULES if importlib.util.find_spec(module) is None]
	if not missing:
		return "packages: all present"
	if not allowed:
		return f"packages: missing {', '.join(missing)}; install with `{doctor.INSTALL_REQUIREMENTS}`"
	completed = pip_install(sys.executable, repo_root)
	if completed.returncode == 0:
		return f"packages: installed ({', '.join(missing)}): {last_line(completed)}"
	if "externally-managed-environment" not in completed.stdout + completed.stderr:
		return f"packages: pip exited {completed.returncode} ({', '.join(missing)}): {last_line(completed)}"
	created = run_step([sys.executable, "-m", "venv", str(repo_root / VENV)], repo_root)
	venv = project_python(repo_root)
	if created.returncode != 0 or venv is None:
		return ("packages: this Python is externally managed and a virtual environment could not be created "
			f"({last_line(created)}); install the venv module (for example `sudo apt install python3-venv`) and rerun setup")
	completed = pip_install(str(venv), repo_root)
	state = "installed" if completed.returncode == 0 else f"pip exited {completed.returncode}"
	return f"packages: {state} into {VENV.as_posix()} (this Python is externally managed); check.py uses it automatically: {last_line(completed)}"


def record_game_dir(folder: Optional[Path]) -> str:
	if folder is not None:
		if not game.is_game_dir(folder):
			return f"game folder: {folder} is not a Hearts of Iron IV folder (it needs common/ and localisation/); nothing recorded"
		game.save_local_setting(folder)
		return f"game folder: recorded {folder.resolve().as_posix()} in {game.LOCAL_SETTINGS.as_posix()}"
	found = game.game_dir()
	if game.is_game_dir(found):
		return f"game folder: found {found.as_posix()}"
	return "game folder: not found; rerun with --game-dir <folder>"


def ensure_ignores(repo_root: Path) -> str:
	path = repo_root / ".gitignore"
	text = path.read_text(encoding="utf-8") if path.is_file() else ""
	present = {line.strip() for line in text.splitlines()}
	missing = [line for line in IGNORE_LINES if line not in present and line.lstrip("/") not in present]
	if not missing:
		return ".gitignore: machine-local paths already ignored"
	block = ("" if not text or text.endswith("\n") else "\n") + "# Machine-local tooling files (check.py setup).\n" + "\n".join(missing) + "\n"
	with path.open("a", encoding="utf-8", newline="\n") as handle:
		handle.write(block)
	return f".gitignore: added {', '.join(missing)}"


def run_synchronizers(repo_root: Path) -> List[str]:
	results = []
	for name in SYNCHRONIZERS:
		script = repo_root / ".tools" / "sync" / name
		if script.is_file():
			completed = run_step([sys.executable, "-B", str(script)], repo_root)
			state = "ok" if completed.returncode == 0 else f"exit {completed.returncode}"
			results.append(f"{name}: {state}: {last_line(completed)}")
	return results or ["synchronizers: none installed"]


def adopt_quality(repo_root: Path) -> str:
	if shutil.which("uvx") is None:
		return "quality: uvx is not installed, so the quality check is skipped; nothing to adopt"
	completed = run_step([sys.executable, "-B", str(repo_root / ".tools" / "quality.py"), "--adopt"], repo_root)
	return f"quality: {last_line(completed)}"


def run(repo_root: Path, game_dir: Optional[Path], install: bool, extra: List[doctor.Item]) -> int:
	"""Run every preparation step, then the doctor report; return the doctor status."""
	steps = [install_packages(repo_root, install), record_game_dir(game_dir), ensure_ignores(repo_root),
		*run_synchronizers(repo_root), adopt_quality(repo_root)]
	for step in steps:
		print(f"setup: {step}")
	print(flush=True)
	venv = project_python(repo_root)
	if venv is not None and os.environ.get("HOI4_CHECKS_IN_VENV") != "1":
		# The packages live in the project environment, so the report must run there.
		return subprocess.run([str(venv), "-B", str(repo_root / ".tools" / "check.py"), "doctor"], cwd=repo_root,
			env={**os.environ, "HOI4_CHECKS_IN_VENV": "1"}).returncode
	importlib.invalidate_caches()  # packages installed above must be visible to the report
	return doctor.run(repo_root, extra)
