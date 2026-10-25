"""Canonical Clausewitz script reader for the repository audits.

`parse` turns script text into nodes `(key, operator, value, line)`. A value is the raw token
text (quotes kept) or a nested list for a block; a bare token or bare block has `key` and
`operator` set to None. Comments are dropped, `<`, `>`, `<=`, `>=` and `!=` are operators, and
the reader is tolerant: unbalanced braces never raise, and a stray top-level `}` is skipped,
because audits read files that other people are editing.

`pairs` gives the simpler `(key, value)` view the asset audit uses: quotes removed, `=` blocks
and scalars kept, and a comparison flattened into its three bare tokens.

`strip_comment` and `strip_comments` remove `#` comments outside quoted strings.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple, Union

TOKEN = re.compile(r'"(?:[^"\\\n]|\\.)*"|#[^\n]*|[{}]|<=|>=|!=|[=<>]|[^\s{}=<>"#]+|\n')
COMPARATORS = {"=", "<", ">", "<=", ">=", "!="}

Value = Union[str, List["Node"]]
Node = Tuple[Optional[str], Optional[str], Value, int]
Pair = Tuple[Optional[str], Union[str, List["Pair"]]]


def tokens(text: str) -> List[Tuple[str, int]]:
	"""Return (token, line) for every non-comment token."""
	found: List[Tuple[str, int]] = []
	line = 1
	for match in TOKEN.finditer(text):
		token = match.group(0)
		if token == "\n":
			line += 1
		elif token[0] != "#":
			found.append((token, line))
	return found


def parse(text: str) -> List[Node]:
	"""Parse script text into `(key, operator, value, line)` nodes."""
	stream = tokens(text)
	position = 0
	count = len(stream)

	def block(top: bool) -> List[Node]:
		nonlocal position
		items: List[Node] = []
		while position < count:
			token, token_line = stream[position]
			position += 1
			if token == "}":
				if top:
					continue
				return items
			if token == "{":
				items.append((None, None, block(False), token_line))
				continue
			if position < count and stream[position][0] in COMPARATORS:
				operator = stream[position][0]
				position += 1
				if position >= count:
					break
				value, _ = stream[position]
				position += 1
				if value == "{":
					items.append((token, operator, block(False), token_line))
				else:
					items.append((token, operator, value, token_line))
			else:
				items.append((None, None, token, token_line))
		return items

	return block(True)


def unquote(raw: str) -> str:
	return raw[1:-1] if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"' else raw


def pairs(nodes: List[Node]) -> List[Pair]:
	"""Convert nodes to `(key, value)` pairs with quotes removed."""
	result: List[Pair] = []
	for key, operator, value, _ in nodes:
		if isinstance(value, list):
			result.append((None if key is None else unquote(key), pairs(value)))
		elif key is None:
			result.append((None, unquote(value)))
		elif operator == "=":
			result.append((unquote(key), unquote(value)))
		else:
			result.extend([(None, unquote(key)), (None, str(operator)), (None, unquote(value))])
	return result


def strip_comment(line: str) -> str:
	"""Remove a `#` comment that is not inside a quoted string."""
	quoted = False
	for index, character in enumerate(line):
		if character == '"':
			quoted = not quoted
		elif character == "#" and not quoted:
			return line[:index]
	return line


def strip_comments(text: str) -> str:
	"""Remove every `#` comment outside quoted strings, keeping line breaks."""
	return "\n".join(strip_comment(line) for line in text.split("\n"))
