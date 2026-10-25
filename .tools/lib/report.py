"""Shared finding, path-filter and exit-code contract for the read-only repository checks.

Every check reports each finding at one of three levels:

- `error`: an exact rule with a zero false-positive design. Any error makes the check exit 1.
- `warning`: a heuristic, or a rule whose source is not settled. It is printed but never fails.
- `review`: a candidate list for a person to judge, such as dead code. The console shows its
  count only; the JSON report lists every entry.

`--paths` limits reporting to findings located in the given files or folders. Cross-reference
checks still read the whole repository, because a reference can only be resolved against every
definition. A finding whose location is unknown is reported only without `--paths`.

Exit codes: 0 when no error was reported, 1 when at least one was, 2 for a usage or input
failure (argparse already exits 2 for bad arguments).

Run tools from the mod root as `python -B .tools/<tool>.py`; that puts `.tools` on `sys.path`, so
a tool imports this module as `from lib.report import ...`.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, NamedTuple, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
LEVELS = ("error", "warning", "review")


class Finding(NamedTuple):
	check: str
	rule: str
	level: str
	path: str
	line: int
	message: str


def relative(path: object) -> str:
	"""Return a repository-relative POSIX path, or an empty string for no location."""
	if path is None:
		return ""
	text = str(path).replace("\\", "/").strip()
	if not text:
		return ""
	candidate = Path(text)
	if candidate.is_absolute():
		try:
			return candidate.resolve().relative_to(REPO_ROOT).as_posix()
		except ValueError:
			return candidate.as_posix()
	return text[2:] if text.startswith("./") else text


def split_site(site: str) -> Tuple[str, int]:
	"""Split a `path:line` site into (path, line); the line is 0 when absent."""
	text = str(site)
	head, separator, tail = text.rpartition(":")
	if separator and tail.isdigit():
		return relative(head), int(tail)
	return relative(text), 0


def add_arguments(parser: argparse.ArgumentParser) -> None:
	"""Add the shared `--paths` and `--fail-on` options to a check's parser."""
	parser.add_argument(
		"--paths",
		nargs="+",
		metavar="PATH",
		help="report only findings located in these files or folders (the scan still covers the repository)",
	)
	parser.add_argument(
		"--paths-from",
		type=Path,
		metavar="FILE",
		help="like --paths, reading one path per line from FILE (for lists too long for a command line)",
	)
	parser.add_argument(
		"--fail-on",
		choices=("error", "none"),
		default="error",
		help="exit 1 when an error-level finding is reported (default), or never",
	)


def requested_paths(arguments: argparse.Namespace) -> Optional[List[str]]:
	"""Combine `--paths` and `--paths-from`; None means no path filter."""
	paths = list(arguments.paths or [])
	if arguments.paths_from:
		paths += [line.strip() for line in arguments.paths_from.read_text(encoding="utf-8").splitlines() if line.strip()]
	return paths or None


class PathFilter:
	def __init__(self, paths: Optional[Sequence[str]]) -> None:
		self.paths = [relative(Path(p).resolve()) if Path(p).exists() else relative(p) for p in paths or ()]
		self.paths = [p.rstrip("/") for p in self.paths if p]

	def active(self) -> bool:
		return bool(self.paths)

	def matches(self, path: str) -> bool:
		if not self.paths:
			return True
		if not path:
			return False
		lowered = path.lower()
		return any(lowered == p.lower() or lowered.startswith(p.lower() + "/") for p in self.paths)


def select(findings: Iterable[Finding], paths: Optional[Sequence[str]]) -> List[Finding]:
	"""Keep findings inside `paths` and return them in stable order."""
	selector = PathFilter(paths)
	kept = [finding for finding in findings if selector.matches(finding.path)]
	return sorted(kept, key=lambda f: (f.path, f.line, f.rule, f.message))


def format_finding(finding: Finding) -> str:
	location = f"{finding.path}:{finding.line}" if finding.line else (finding.path or "<repository>")
	return f"{location}: {finding.level} {finding.rule} {finding.message}"


def print_findings(check: str, findings: Sequence[Finding], show_levels: Sequence[str] = ("error", "warning")) -> None:
	"""Print one line per shown finding, then a per-level summary line."""
	for finding in findings:
		if finding.level in show_levels:
			print(format_finding(finding))
	counts = Counter(finding.level for finding in findings)
	summary = ", ".join(f"{counts[level]} {level}" for level in LEVELS)
	print(f"{check}: {summary}")


def to_json(findings: Sequence[Finding]) -> List[Dict[str, object]]:
	return [finding._asdict() for finding in findings]


def merge_json(destination: Path, findings: Sequence[Finding], levels: Dict[str, str]) -> None:
	"""Add the normalised `findings` and `levels` fields to a check's existing JSON report."""
	payload = json.loads(destination.read_text(encoding="utf-8")) if destination.exists() else {}
	payload["findings"] = to_json(findings)
	payload["levels"] = dict(sorted(levels.items()))
	destination.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def exit_code(findings: Sequence[Finding], fail_on: str) -> int:
	if fail_on == "none":
		return 0
	return 1 if any(finding.level == "error" for finding in findings) else 0
