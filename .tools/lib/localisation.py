"""Canonical reader for HOI4 localisation files and UTF-8 script text.

`read_text` decodes a file as UTF-8, removing a BOM and replacing stray legacy bytes, so audits never
stop on one damaged file. `LOC_LINE` matches one `key: "value"` line (optionally `key:0` and a
trailing comment); the value runs to the last quote on the line, so a `#` inside the text (for
example in a `§Y…§!` colour span) is never taken for a comment. `entries` yields every such line.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator, NamedTuple, Optional

BOM = b"\xef\xbb\xbf"
LOC_LINE = re.compile(r'^(?P<key>[A-Za-z0-9_.\-]+)\s*:\s*(?P<ordinal>\d+)?\s*"(?P<value>.*)"\s*(?:#.*)?$')
HEADER_LINE = re.compile(r"^l_english\s*:\s*(?:#.*)?$")


class Entry(NamedTuple):
	line: int
	key: str
	ordinal: Optional[str]
	value: str


def read_text(path: Path) -> str:
	"""Decode a file as UTF-8, tolerating a BOM and stray legacy bytes."""
	raw = path.read_bytes()
	if raw.startswith(BOM):
		raw = raw[3:]
	return raw.decode("utf-8", errors="replace")


def entries(text: str) -> Iterator[Entry]:
	"""Yield every `key: "value"` line; blank, comment and header lines are skipped."""
	for number, line in enumerate(text.splitlines(), start=1):
		match = LOC_LINE.match(line.strip())
		if match:
			yield Entry(number, match.group("key"), match.group("ordinal"), match.group("value"))
