#!/usr/bin/env python3
"""Read-only inspector for plain-text Hearts of Iron IV saves.

A plain-text save (header `HOI4txt`, written when the game setting
`save_as_binary=no`) is ordinary Clausewitz script, so runtime state such as
country flags, variables, arrays, state data, and global flags can be read
without the game. Binary saves (`HOI4bin`) need Paradox's token table, which is
not distributed, so this tool refuses them with setup instructions.

Paths address nested blocks with `/`, for example `countries/GER/variables`.
Each segment accepts shell-style globs (`countries/*/flags`). A key that
repeats inside one block gets an occurrence suffix after its first use
(`division`, `division[1]`, `division[2]`), and an unnamed block is `-`.

Commands:
	info       SAVE                         header, size, and top-level scalar values
	keys       SAVE [PATH]                  child keys under PATH with counts and kinds
	get        SAVE PATH [--depth N]        print the subtree(s) at PATH as script
	find       SAVE REGEX [--in PATH]       leaves whose path or value matches REGEX
	flatten    SAVE [--in PATH] [--match R] one `path = value` line per leaf
	diff       OLD NEW [--in PATH] [--match R]  added, removed, and changed leaves
	footprint  SAVE [--in PATH] [--prefix-depth N] [--containers A,B]  script-state size by name prefix

Every command is read-only. Large saves take a while in pure Python; narrow
work with --in whenever possible, because blocks outside it are skipped by a
fast structural scan before any full parse.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

TEXT_HEADER = b"HOI4txt"
BINARY_HEADER = b"HOI4bin"

# One token: quoted string, structural character, operator, comment, or bare word.
TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"|[{}]|[<>!]?=|[<>]|#[^\n]*|[^\s{}=<>!"#]+')
# Structural scan used to skip blocks outside the requested path quickly.
STRUCTURE = re.compile(r'"(?:[^"\\]|\\.)*"|#[^\n]*|[{}]')


class SaveError(Exception):
	pass


def load_text(path: Path) -> str:
	data = path.read_bytes()
	if data[:2] == b"PK":
		with zipfile.ZipFile(path) as archive:
			names = [name for name in archive.namelist() if not name.endswith("/")]
			if not names:
				raise SaveError(f"{path}: empty archive")
			data = archive.read(names[0])
	if data.startswith(BINARY_HEADER):
		raise SaveError(
			f"{path} is a binary save (HOI4bin). Set `save_as_binary=no` in the HOI4 "
			"settings.txt (Documents/Paradox Interactive/Hearts of Iron IV/settings.txt), "
			"then save again to write a plain-text HOI4txt save."
		)
	if data.startswith(TEXT_HEADER):
		data = data[len(TEXT_HEADER):]
	return data.decode("utf-8", errors="replace")


def split_path(path: Optional[str]) -> List[str]:
	return [part for part in (path or "").strip("/").split("/") if part]


def prefix_state(parts: List[str], pattern: List[str]) -> str:
	"""Return 'inside' if parts is at or below pattern, 'toward' if it can still reach it, else 'off'."""
	for index, part in enumerate(parts):
		if index >= len(pattern):
			return "inside"
		if not fnmatch.fnmatchcase(part, pattern[index]):
			return "off"
	return "inside" if len(parts) >= len(pattern) else "toward"


class Node:
	__slots__ = ("path", "leaves", "items")

	def __init__(self, path: Tuple[str, ...]) -> None:
		self.path = path
		self.leaves: List[Tuple[str, str]] = []
		self.items: List[str] = []


def walk(text: str, pattern: List[str]) -> Iterator[Tuple[str, Tuple[str, ...], str]]:
	"""Yield ('open', path, ''), ('leaf', path, value), ('items', path, joined), ('close', path, '').

	Only blocks on or inside PATTERN are reported; other blocks are skipped with a
	brace-matching scan that honours quoted strings and comments.
	"""
	state = {"tokens": TOKEN.finditer(text), "end": 0}
	pending: List[re.Match] = []

	def next_token() -> Optional[re.Match]:
		while True:
			match = pending.pop() if pending else next(state["tokens"], None)
			if match is None:
				return None
			state["end"] = match.end()
			if not match.group(0).startswith("#"):
				return match

	def skip_block() -> None:
		# Scan only braces, strings, and comments, then resume full tokenizing after the block.
		depth = 1
		position = state["end"]
		for match in STRUCTURE.finditer(text, position):
			token = match.group(0)
			if token == "{":
				depth += 1
			elif token == "}":
				depth -= 1
				if not depth:
					position = match.end()
					break
		else:
			position = len(text)
		pending.clear()
		state["tokens"] = TOKEN.finditer(text, position)

	stack: List[Tuple[Tuple[str, ...], Counter, List[str]]] = [((), Counter(), [])]
	while True:
		match = next_token()
		if match is None:
			break
		token = match.group(0)
		path, seen, items = stack[-1]
		if token == "}":
			if len(stack) == 1:
				continue
			if items:
				yield ("items", path, " ".join(items))
			yield ("close", path, "")
			stack.pop()
			continue
		if token == "{":
			key = "-"
		else:
			follow = next_token()
			if follow is not None and follow.group(0) in ("=", "<", ">", "<=", ">=", "!="):
				key = token.strip('"')
				value = next_token()
				if value is None:
					break
				if value.group(0) != "{":
					count = seen[key]
					seen[key] += 1
					name = key if count == 0 else f"{key}[{count}]"
					if prefix_state(list(path) + [name], pattern) == "inside":
						yield ("leaf", path + (name,), value.group(0))
					continue
			else:
				if follow is not None:
					pending.append(follow)
				if prefix_state(list(path), pattern) == "inside":
					items.append(token)
				continue
		count = seen[key]
		seen[key] += 1
		name = key if count == 0 else f"{key}[{count}]"
		child = path + (name,)
		if prefix_state(list(child), pattern) == "off":
			skip_block()
			continue
		stack.append((child, Counter(), []))
		yield ("open", child, "")


def fmt_path(path: Tuple[str, ...]) -> str:
	return "/".join(path)


def leaves(text: str, pattern: List[str], match: Optional[re.Pattern]) -> Iterator[Tuple[str, str]]:
	for kind, path, value in walk(text, pattern):
		if kind == "leaf" or kind == "items":
			shown = value if kind == "leaf" else "{ " + value + " }"
			line = fmt_path(path)
			if match is None or match.search(line) or match.search(shown):
				yield line, shown


def cmd_info(args) -> None:
	path = Path(args.save)
	raw = path.read_bytes()[:16]
	print(f"file      : {path}")
	print(f"size      : {path.stat().st_size / 1_048_576:.1f} MiB")
	print(f"header    : {raw[:7].decode('ascii', 'replace')}")
	text = load_text(path)
	shown = 0
	for kind, node, value in walk(text, []):
		if kind == "leaf" and len(node) == 1:
			print(f"{node[0]:<10}: {value}")
			shown += 1
			if shown >= 12:
				break


def cmd_keys(args) -> None:
	pattern = split_path(args.path)
	text = load_text(Path(args.save))
	depth = len(pattern) + 1
	counts: Dict[str, Counter] = defaultdict(Counter)
	for kind, node, _ in walk(text, pattern):
		if len(node) == depth and kind in ("open", "leaf"):
			base = re.sub(r"\[\d+\]$", "", node[-1])
			counts[base]["block" if kind == "open" else "value"] += 1
	for key, kinds in sorted(counts.items(), key=lambda item: (-sum(item[1].values()), item[0]))[: args.limit]:
		described = ", ".join(f"{number} {kind}" for kind, number in kinds.items())
		print(f"{key}  ({described})")
	if len(counts) > args.limit:
		print(f"... {len(counts) - args.limit} more keys")


def cmd_get(args) -> None:
	pattern = split_path(args.path)
	if not pattern:
		raise SaveError("get needs a PATH")
	text = load_text(Path(args.save))
	base = len(pattern)
	printed = 0
	for kind, node, value in walk(text, pattern):
		level = len(node) - base
		if level < 0 or (kind != "items" and level > args.depth):
			continue
		indent = "\t" * max(level, 0)
		name = node[-1]
		if kind == "open":
			print(f"{indent}{fmt_path(node) if level == 0 else name} = {{")
		elif kind == "close":
			print(f"{indent}}}")
		elif kind == "leaf":
			print(f"{indent}{fmt_path(node) if level == 0 else name} = {value}")
		elif kind == "items":
			print(f"{indent}\t{value}")
		printed += 1
		if printed >= args.limit:
			print(f"... output capped at {args.limit} lines; narrow the path or raise --limit")
			return


def cmd_find(args) -> None:
	regex = re.compile(args.regex)
	text = load_text(Path(args.save))
	hits = 0
	for line, value in leaves(text, split_path(args.inside), None):
		if regex.search(line) or regex.search(value):
			print(f"{line} = {value}")
			hits += 1
			if hits >= args.limit:
				print(f"... capped at {args.limit} matches")
				return
	if not hits:
		print("no matches")


def cmd_flatten(args) -> None:
	match = re.compile(args.match) if args.match else None
	text = load_text(Path(args.save))
	for line, value in leaves(text, split_path(args.inside), match):
		print(f"{line} = {value}")


def cmd_diff(args) -> None:
	pattern = split_path(args.inside)
	match = re.compile(args.match) if args.match else None
	old = dict(leaves(load_text(Path(args.old)), pattern, match))
	new = dict(leaves(load_text(Path(args.new)), pattern, match))
	added = sorted(set(new) - set(old))
	removed = sorted(set(old) - set(new))
	changed = sorted(key for key in set(old) & set(new) if old[key] != new[key])
	for title, rows in (("added", added), ("removed", removed), ("changed", changed)):
		print(f"--- {title} ({len(rows)}) ---")
		for key in rows[: args.limit]:
			if title == "changed":
				print(f"  {key}: {old[key]} -> {new[key]}")
			else:
				print(f"  {key} = {(new if title == 'added' else old)[key]}")
		if len(rows) > args.limit:
			print(f"  ... {len(rows) - args.limit} more")


def cmd_footprint(args) -> None:
	"""Count persistent script state by name prefix to expose leaks and save bloat."""
	text = load_text(Path(args.save))
	containers = set(args.containers.split(","))
	counts: Counter = Counter()
	sizes: Counter = Counter()
	for kind, node, value in walk(text, split_path(args.inside)):
		container = next((part for part in node[:-1] if part in containers), None)
		if container is None or kind == "close":
			continue
		index = node.index(container)
		if len(node) != index + 2 and kind != "items":
			continue
		name = re.sub(r"\[\d+\]$", "", node[index + 1]) if len(node) > index + 1 else node[-1]
		prefix = "_".join(name.split("_")[: args.prefix_depth])
		if kind in ("open", "leaf"):
			counts[(container, prefix)] += 1
		if kind == "items":
			sizes[(container, prefix)] += len(value.split())
	print(f"{'container':<18}{'prefix':<44}{'entries':>9}{'elements':>10}")
	for (container, prefix), number in counts.most_common(args.limit):
		print(f"{container:<18}{prefix:<44}{number:>9}{sizes[(container, prefix)]:>10}")


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	sub = parser.add_subparsers(dest="command", required=True)
	p = sub.add_parser("info"); p.add_argument("save"); p.set_defaults(run=cmd_info)
	p = sub.add_parser("keys"); p.add_argument("save"); p.add_argument("path", nargs="?")
	p.add_argument("--limit", type=int, default=200); p.set_defaults(run=cmd_keys)
	p = sub.add_parser("get"); p.add_argument("save"); p.add_argument("path")
	p.add_argument("--depth", type=int, default=3); p.add_argument("--limit", type=int, default=400)
	p.set_defaults(run=cmd_get)
	p = sub.add_parser("find"); p.add_argument("save"); p.add_argument("regex")
	p.add_argument("--in", dest="inside"); p.add_argument("--limit", type=int, default=200)
	p.set_defaults(run=cmd_find)
	p = sub.add_parser("flatten"); p.add_argument("save"); p.add_argument("--in", dest="inside")
	p.add_argument("--match"); p.set_defaults(run=cmd_flatten)
	p = sub.add_parser("diff"); p.add_argument("old"); p.add_argument("new")
	p.add_argument("--in", dest="inside"); p.add_argument("--match")
	p.add_argument("--limit", type=int, default=300); p.set_defaults(run=cmd_diff)
	p = sub.add_parser("footprint"); p.add_argument("save"); p.add_argument("--in", dest="inside")
	p.add_argument("--prefix-depth", type=int, default=2); p.add_argument("--limit", type=int, default=60)
	p.add_argument("--containers", default="variables,flags,arrays,variable_arrays,global_variables,global_flags",
		help="comma-separated block names that hold script state; confirm them with `keys` on a real save")
	p.set_defaults(run=cmd_footprint)
	args = parser.parse_args()
	try:
		sys.stdout.reconfigure(encoding="utf-8", errors="replace")
		args.run(args)
	except SaveError as error:
		print(f"error: {error}", file=sys.stderr)
		return 2
	except BrokenPipeError:
		return 0
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
