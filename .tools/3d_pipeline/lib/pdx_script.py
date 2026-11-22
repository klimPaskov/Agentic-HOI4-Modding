"""A small reader for Paradox script text (`key = value`, `key = { ... }`), enough for the entity `.asset`, `.gfx` and particle files.

`parse(text)` gives a list of `(key, value)` pairs, where a value is a string or a nested list of the same shape. A bare word inside a
block (`{ 1.0 2.0 }`) is stored with the key `""`. Comments (`#` to the end of the line) are dropped. Unbalanced braces are tolerated:
a missing `}` closes at the end of the text, an extra one is skipped, since vanilla files carry a few of each.
"""

from __future__ import annotations

import re
from typing import Iterator, List, Optional, Tuple, Union

Value = Union[str, List[Tuple[str, "Value"]]]
TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"|[{}=]|[^\s{}=#"]+|#[^\n]*')


def tokens(text: str) -> Iterator[str]:
    for match in TOKEN.finditer(text):
        token = match.group(0)
        if token.startswith("#"):
            continue
        yield token


def _unquote(token: str) -> str:
    return token[1:-1] if len(token) >= 2 and token[0] == token[-1] == '"' else token


def parse(text: str) -> List[Tuple[str, Value]]:
    stream = list(tokens(text))
    position = 0

    def block() -> List[Tuple[str, Value]]:
        nonlocal position
        out: List[Tuple[str, Value]] = []
        while position < len(stream):
            token = stream[position]
            if token == "}":
                position += 1
                return out
            if token == "{":
                position += 1
                out.append(("", block()))
                continue
            if token == "=":  # a stray operator
                position += 1
                continue
            if position + 1 < len(stream) and stream[position + 1] == "=":
                position += 2
                if position < len(stream) and stream[position] == "{":
                    position += 1
                    out.append((_unquote(token), block()))
                elif position < len(stream):
                    out.append((_unquote(token), _unquote(stream[position])))
                    position += 1
                continue
            out.append(("", _unquote(token)))
            position += 1
        return out

    top: List[Tuple[str, Value]] = []
    while position < len(stream):
        top += block()  # a stray `}` at the top level ends a block early; carry on with the rest
    return top


def get(block: List[Tuple[str, Value]], key: str) -> Optional[Value]:
    for name, value in block:
        if name == key:
            return value
    return None


def get_all(block: List[Tuple[str, Value]], key: str) -> List[Value]:
    return [value for name, value in block if name == key]
