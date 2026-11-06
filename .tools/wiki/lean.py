"""Turn the kit's annotated text into the lean text agents read in hoi4_wiki/.

Kit text is written once, in the sidecar files under ``.tools/wiki/kit/``, with
the evidence that backs each statement::

    `set_autonomy` runs in country scope. [docs] `documentation/effects_documentation.md`.

The page in ``hoi4_wiki/`` gets the same text without its evidence::

    `set_autonomy` runs in country scope.

Rules, applied to each line outside code fences:

* An evidence tag (``[docs]``, ``[vanilla-confirmed <build>]``, ``[game-tested <build>]``)
  starts a citation that runs to the end of its sentence, its table cell, its
  parenthesis or its line, and is removed together with the citation. A short
  lead-in such as ``All rows:`` directly in front of the tag goes with it.
* ``[unverified]`` stays as a plain hedge: ``(unverified)``, or ``unverified``
  after a verb such as ``is``.
* ``<a id="..."></a>`` anchors are dropped and a heading's ``Kit:`` prefix is removed.

Write evidence after the statement it supports, never before it: a tag that
opens a sentence would take the sentence with it, and the verify check reports
every line where that happens (``evidence_problems``).

Standard library only; Python 3.9 or newer.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_blocks  # the page format, next to this module

FENCE = "`" * 3
EVIDENCE = re.compile(r"\[(?:docs|(?:vanilla-confirmed|game-tested)(?: [0-9][0-9.]*)?)\]")
UNVERIFIED = "[unverified]"
ANY_TAG = re.compile(r"\[(?:docs|unverified|(?:vanilla-confirmed|game-tested)(?: [0-9][0-9.]*)?)\]")
ANCHOR = re.compile(r"\s*<a id=\"[^\"]*\"></a>")
HEADING = re.compile(r"^(#{1,6}) (.*)$")
ANGLE_LINK = re.compile(r"\]\(<([^<>()\s]+)>\)")
# A sentence that ends on a word that cannot end one ("file lists are."): its object was cut.
CUT_SENTENCE = re.compile(r"\b(?:is|are|was|were|the|a|an|of|in|from|by|to|and|or|with|for|at|as|that|these)[.;:,]",
                          re.I)
KIT_HEADING = re.compile(r"^(#{1,6} )Kit(?: (?:addition|note|correction))?: (\S)(.*)$")
# Where a clause starts: line start, list marker, sentence end, semicolon, bold label or cell.
CLAUSE_START = re.compile(r"(?:^\s*(?:[-*]|\d+\.)?\s*|[.!?;] +|\*\* +|\| +)")
# A short phrase directly in front of a tag that only announces it ("vanilla uses [...]").
CHAIN = re.compile(r"^\s*(?:[^.;:|\[\n]{0,60}?:?\s*)?(?:\[docs\]|\[vanilla-confirmed|\[game-tested)")
# A clause after a comma that says something new ("..., so the table is wrong").
CLAUSE_BREAK = re.compile(r", (?:so|but|and whether|whether|which|while|although|though|because|yet) ")
# A tag followed by a capitalised sentence: the sentence is a statement, not the tag's citation.
CLAIM_AFTER = re.compile(r"(?::?\s+\[(?:docs|vanilla-confirmed[^\]]*|game-tested[^\]]*)\])*:?\s+(?!HOI4\b)[A-Z]")
HEDGE_VERB = re.compile(r"\b(?:is|are|was|were|be|been|stays|stay|remains|remain|left|still|as)\s*$")
LEAD_IN_WORDS = 12
# "<subject> is|are [tag] ...": a short sentence that only says where its subject was checked.
COPULA_LEAD = re.compile(r"^(?:[A-Z]|All |The )[^.;:]*\b(?:is|are)$")
COPULA_WORDS = 8
# Labels that only say what a citation covers ("All rows:", "Use column:", "Counts:").
EVIDENCE_LABEL = re.compile(
    r"^(?:All|Every|Each|Both|Rows?|Counts?|Sources?|Source of|Evidence|Use counts?|Syntax|Checked)\b"
    r"|\b(?:columns?|rows?|lines|bullets|items|counts|sources)$", re.I)


def _code_spans(line: str) -> List[Tuple[int, int]]:
    """Character ranges of the inline code spans on a line."""
    spans, index = [], 0
    while True:
        start = line.find("`", index)
        if start < 0:
            return spans
        run = len(line[start:]) - len(line[start:].lstrip("`"))
        end = line.find("`" * run, start + run)
        if end < 0:
            return spans
        spans.append((start, end + run))
        index = end + run


def _inside(spans: List[Tuple[int, int]], position: int) -> bool:
    return any(start <= position < end for start, end in spans)


def _stop(line: str, index: int, depth: int) -> str:
    """Why a citation ends at ``line[index]`` (outside inline code), or an empty string."""
    char = line[index]
    if char == "|" and (index == 0 or line[index - 1] != "\\"):
        return "cell"
    if depth > 0:
        return ""
    if char == ")":
        return "paren"
    if char == ";" and not CHAIN.match(line[index + 1:]):
        return "semicolon"
    if char in ".!?" and re.match(r"(?:\s*$| +(?:[A-Z\[*`(\"]|\d))", line[index + 1:]):
        return "sentence"
    if char == "," and CLAUSE_BREAK.match(line, index):
        return "clause"
    if line.startswith(UNVERIFIED, index):
        return "hedge"
    return ""


def _citation_end(line: str, start: int, spans: List[Tuple[int, int]]) -> Tuple[int, str]:
    """Where the citation that starts at `start` ends, and why.

    Returns (index, reason). The citation covers ``line[start:index]``; reason is
    ``line``, ``cell``, ``paren``, ``sentence``, ``semicolon``, ``clause``, ``hedge``
    or ``code``. A hedge (``[unverified]``) is a statement, not evidence: the citation
    ends at the last comma or semicolon before it, so the hedged clause stays.
    """
    depth, index, clause = 0, start, -1
    while index < len(line):
        if _inside(spans, index):
            span_end = next(end for begin, end in spans if begin <= index < end)
            rest = line[span_end:]
            if depth == 0 and re.match(r" [A-Z]", rest) and not re.match(r" [A-Z][a-z]* ?[0-9]", rest):
                return span_end, "code"
            index = span_end
            continue
        reason = _stop(line, index, depth)
        if reason == "hedge":
            return (clause if clause >= 0 else index), reason
        if reason:
            return index, reason
        if line[index] in ",;" and depth == 0:
            clause = index
        depth += {"(": 1, ")": -1}.get(line[index], 0)
        index += 1
    return len(line), "line"


def _lead_in(line: str, start: int, keep: bool) -> int:
    """Start of a short ``Label:`` clause directly in front of the tag at `start`, or `start`.

    ``Counts: [vanilla-confirmed ...] `common/ideas/``` loses its label with the citation.
    With `keep`, a label that ends the line stays, because it introduces the list,
    table or example below it.
    """
    head = line[:start].rstrip(" ")
    clause = max((m.end() for m in CLAUSE_START.finditer(head) if m.end() < len(head)), default=0)
    label = head[clause:]
    if COPULA_LEAD.search(label) and len(label.split()) <= COPULA_WORDS and "](" not in label:
        # "Counts are [vanilla-confirmed ...] `common/units/`." is a citation sentence.
        return clause
    if not head.endswith(":"):
        return start
    if not label or len(label.split()) > LEAD_IN_WORDS or "](" in label:
        return start
    if keep and not EVIDENCE_LABEL.search(label.rstrip(":").strip()):
        return start
    return clause


def _strip_evidence(line: str, introduces: bool = False) -> Tuple[str, List[str]]:
    """Remove every evidence citation from one line; return it and the removed parts.

    `introduces` says the next line starts a list, table or code block, so a label
    such as ``Example:`` at the end of this line stays.
    """
    removed: List[str] = []
    while True:
        spans = _code_spans(line)
        match = next((m for m in EVIDENCE.finditer(line) if not _inside(spans, m.start())), None)
        if match is None:
            return line, removed
        start = match.start()
        if CLAIM_AFTER.match(line, match.end()):
            # A capitalised sentence after the tag is a statement, not a citation: drop the tag only.
            before, after = line[:start].rstrip(" "), line[match.end():].lstrip(" :")
            removed.append(match.group(0))
            line = (before + " " + after) if before else after
            continue
        end, reason = _citation_end(line, match.end(), spans)
        keep_label = introduces and line[end:].strip(" .") == ""
        start = _lead_in(line, start, keep_label)
        before, after = line[:start].rstrip(" "), line[end:]
        if keep_label and before.endswith(":"):
            after = after.lstrip(" .")
        removed.append(line[start:end].strip())
        line = _join(before, after, reason)


def _join(before: str, after: str, reason: str) -> str:
    """The line once a citation between `before` and `after` is gone."""
    bare = before.strip() in ("", "-", "*")  # nothing in front but perhaps a list marker
    ended = bare or bool(re.search(r"[.!?:;|]$", before))
    if reason in ("sentence", "semicolon") and ended and after[:1] in ".;":
        # The text before already ends its sentence, so the citation's terminator goes too,
        # and the clause after a dropped semicolon starts a new sentence.
        after = after[1:]
        if reason == "semicolon":
            after = re.sub(r"^( *)([a-z])", lambda m: m.group(1) + m.group(2).upper(), after)
    if reason == "cell":
        return before + " " + after
    if bare:
        return (before.rstrip() + " " + after.lstrip(" ")) if before.strip() else after.lstrip(" ")
    if after == "" or re.match(r"^[.,;:)!?]", after):
        return before + after
    return before + " " + after.lstrip(" ")


def _hedge(line: str) -> str:
    """Render each remaining ``[unverified]`` as plain words."""
    spans = _code_spans(line)
    out, cursor = [], 0
    for match in re.finditer(re.escape(UNVERIFIED), line):
        if _inside(spans, match.start()):
            continue
        before = line[cursor:match.start()]
        word = "unverified" if HEDGE_VERB.search(line[:match.start()]) else "(unverified)"
        out.append(before + word)
        cursor = match.end()
    out.append(line[cursor:])
    return "".join(out)


def _tidy(line: str) -> str:
    spans = _code_spans(line)
    if spans:
        # Tidy only the prose between code spans.
        parts, cursor = [], 0
        for start, end in spans:
            parts.append(_tidy_prose(line[cursor:start]))
            parts.append(line[start:end])
            cursor = end
        parts.append(_tidy_prose(line[cursor:]))
        return "".join(parts).rstrip()
    return _tidy_prose(line).rstrip()


def _tidy_prose(text: str) -> str:
    """Spacing and punctuation a removed citation leaves behind; an ellipsis is left alone."""
    text = re.sub(r"(?<=\S) {2,}(?=\S)", " ", text)
    text = re.sub(r" +([,;:!?)]|\.(?!\.))", r"\1", text)
    text = re.sub(r"\( *\)", "", text)
    text = re.sub(r"\(\s*[;,]\s*", "(", text)
    text = re.sub(r"\s*[;,]\s*\)", ")", text)
    text = re.sub(r"(?<!\.)([.!?])(?:[;,]|\.(?!\.))", r"\1", text)
    return text


def lean_line(line: str, introduces: bool = False) -> Tuple[str, List[str]]:
    """The lean form of one prose line, and the citations it lost."""
    heading = KIT_HEADING.match(line)
    if heading:
        line = heading.group(1) + heading.group(2).upper() + heading.group(3)
    line = ANGLE_LINK.sub(r"](\1)", ANCHOR.sub("", line))
    stripped, removed = _strip_evidence(line, introduces)
    stripped = _hedge(stripped)
    if removed or stripped != line:
        stripped = _tidy(stripped)
    if removed and line.rstrip().endswith(":") and stripped.strip() and not re.search(r"[:.]$", stripped):
        # A line that introduced something keeps its colon when its citation goes.
        stripped = stripped.rstrip(",; ") + ":"
    return stripped, removed


STRUCTURE = re.compile(r"^\s*(?:[-*] |\d+\. |\||" + FENCE + ")")


def _introduces(lines: List[str], index: int) -> bool:
    """Whether the next non-blank line after `index` starts a list, table or code block."""
    for line in lines[index + 1:]:
        if line.strip():
            return bool(STRUCTURE.match(line))
    return False


def lean_text(text: str) -> str:
    """The lean form of annotated kit text (see the module docstring)."""
    return lean_text_report(text)[0]


def lean_text_report(text: str) -> Tuple[str, List[Tuple[int, str, str, List[str]]]]:
    """Lean text plus, per changed line, (line number, before, after, removed citations)."""
    out: List[str] = []
    changes: List[Tuple[int, str, str, List[str]]] = []
    inside = False
    lines = text.split("\n")
    for number, line in enumerate(lines, 1):
        if line.lstrip().startswith(FENCE):
            inside = not inside
            out.append(line)
            continue
        if inside:
            out.append(line)
            continue
        lean, removed = lean_line(line, _introduces(lines, number - 1))
        if lean != line:
            changes.append((number, line, lean, removed))
        if line.strip() and not lean.strip():
            continue  # a line that held only evidence
        out.append(lean)
    result = re.sub(r"\n{3,}", "\n\n", "\n".join(out))
    return result, changes


def evidence_problems(text: str) -> List[str]:
    """Lines whose lean form reads badly: the evidence was not written after its statement.

    Each entry names the line number and what is wrong.
    """
    problems = []
    lines = text.split("\n")
    for number, before, after, removed in lean_text_report(text)[1]:
        if not removed:
            continue
        stripped = _blank_code(after).strip()
        ends = _blank_code(before).rstrip()[-1:]
        intro = stripped.endswith(":") and _introduces(lines, number - 1)
        if stripped and re.search(r"[:;,]$", stripped) and ends != stripped[-1] and not stripped.startswith("|") and not intro:
            problems.append(f"line {number}: evidence removal leaves a dangling '{stripped[-1]}'")
        if re.search(r"[.!?:]\s*;|;\s*[.;]|^\s*[;,.]", stripped):
            problems.append(f"line {number}: evidence removal leaves stray punctuation")
        if len(CUT_SENTENCE.findall(stripped)) > len(CUT_SENTENCE.findall(_blank_code(before))):
            problems.append(f"line {number}: evidence removal cuts a sentence short; write the "
                            "evidence after the statement, not in the middle of it")
        if re.match(r"^\s*(?:[-*]|\d+\.)\s+\S", before) and re.match(r"^\s*(?:[-*]|\d+\.)\s*$", after):
            problems.append(f"line {number}: a list item holds only evidence")
    return problems


def _blank_code(line: str) -> str:
    """The line with each inline code span replaced by ``x``, so its punctuation is ignored."""
    out, cursor = [], 0
    for start, end in _code_spans(line):
        out.append(line[cursor:start] + "x")
        cursor = end
    return "".join(out) + line[cursor:]


def tags_outside_code(line: str) -> List[str]:
    """Evidence tags on a line that are not inside inline code."""
    spans = _code_spans(line)
    return [m.group(0) for m in ANY_TAG.finditer(line) if not _inside(spans, m.start())]


def heading_text(line: str) -> Optional[str]:
    """The visible text of a Markdown heading line, or None."""
    match = HEADING.match(line)
    return ANCHOR.sub("", match.group(2)).strip() if match else None


# --- wiki text from the converter -------------------------------------------

CAPTURE = re.compile(r"^\*(Offline snapshot of the Hearts of Iron IV Wiki page|Kit page)\b")
LINK = re.compile(r"(\]\()<?([^()<>\s]*)>?(\))")
BACKLINK = re.compile(r"^(\s*\d+\. )↑ (?:\d+\.\d+ )*")
FURNITURE_HEADINGS = ("Table of contents", "Navigation")


def _fence_mask(lines: List[str]) -> List[bool]:
    """For each line, whether it is inside (or opens or closes) a code fence."""
    mask, inside = [], False
    for line in lines:
        fence = line.lstrip().startswith(FENCE)
        mask.append(inside or fence)
        if fence:
            inside = not inside
    return mask


def anchor_map(lines: List[str]) -> Dict[str, str]:
    """Wiki heading id -> GitHub-style slug, for a converted page whose headings carry ``<a id>``.

    Slugs are numbered over the headings the lean page keeps (the title included, the
    table of contents and navigation footer left out), the way GitHub numbers repeats.
    """
    seen: Dict[str, int] = {}
    out: Dict[str, str] = {}
    for line, fenced in zip(lines, _fence_mask(lines)):
        match = None if fenced else HEADING.match(line)
        if not match:
            continue
        title = ANCHOR.sub("", match.group(2)).strip()
        if len(match.group(1)) == 2 and title in FURNITURE_HEADINGS:
            continue
        title = KIT_PREFIX.sub("", title)
        base = kit_blocks.slug(title)
        count = seen.get(base, 0)
        seen[base] = count + 1
        name = base if count == 0 else f"{base}-{count}"
        for anchor in re.findall(r"<a id=\"([^\"]+)\"></a>", line):
            out[anchor] = name
    return out


KIT_PREFIX = re.compile(r"^Kit(?: (?:addition|note|correction))?: ")


def rewrite_links(text: str, page: str, anchors: Dict[str, Dict[str, str]]) -> Tuple[str, int]:
    """Point every page link at a slug instead of a wiki heading id, without angle brackets.

    ``[x](<effects.md#Country_scope>)`` becomes ``[x](effects.md#country-scope)``. A
    fragment no page heading has is dropped (a same-page link keeps only its text).
    Returns the text and the number of fragments dropped.
    """
    dropped = 0

    def replace(match: "re.Match[str]") -> str:
        nonlocal dropped
        target = match.group(2)
        name, _, fragment = target.partition("#")
        if name and not name.endswith(".md"):
            return match.group(0)
        if not fragment:
            return f"]({name})"
        known = anchors.get(name or page)
        if known is None:
            return f"]({target})"
        if fragment in known.values():
            return f"]({name}#{fragment})"
        if fragment in known:
            return f"]({name}#{known[fragment]})"
        dropped += 1
        return f"]({name})" if name else "](#)"

    out = []
    for line, fenced in zip(text.split("\n"), _fence_mask(text.split("\n"))):
        out.append(line if fenced else LINK.sub(replace, line))
    result = re.sub(r"\[([^\]]*)\]\(#\)", r"\1", "\n".join(out))
    return result, dropped


def strip_furniture(text: str) -> str:
    """A converted page without its capture line, table of contents, rules and navigation footer."""
    lines = text.rstrip("\n").split("\n")
    fenced = _fence_mask(lines)
    keep = [True] * len(lines)
    capture = next((i for i, line in enumerate(lines[:12]) if CAPTURE.match(line)), None)
    if capture is not None:
        keep[capture] = False
    for i, line in enumerate(lines[:12]):
        if line.strip() == "<!-- kit:page -->":
            keep[i] = False
    start = 0 if capture is None else capture + 1
    toc = next((i for i in range(len(lines)) if not fenced[i] and lines[i] == "## Table of contents"), None)
    if toc is not None:
        rule = next((i for i in range(toc, len(lines)) if lines[i].strip() == "---"), toc)
        for i in range(toc, rule + 1):
            keep[i] = False
    else:
        rule = next((i for i in range(start, min(len(lines), start + 40)) if lines[i].strip() == "---"
                     and not fenced[i]), None)
        if rule is not None:
            keep[rule] = False
    navigation = [i for i in range(len(lines)) if not fenced[i] and lines[i] == "## Navigation"]
    if navigation:
        footer = navigation[-1]
        before = footer - 1
        while before > 0 and lines[before].strip() == "":
            before -= 1
        if lines[before].strip() == "---":
            footer = before
        for i in range(footer, len(lines)):
            keep[i] = False
    out = [line for line, wanted in zip(lines, keep) if wanted]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip("\n") + "\n"


def lean_wiki_text(text: str, page: str, anchors: Dict[str, Dict[str, str]]) -> str:
    """The lean form of a page the converter produced: no furniture, anchors or backlink arrows."""
    lines = strip_furniture(text).split("\n")
    out = []
    for line, fenced in zip(lines, _fence_mask(lines)):
        if not fenced:
            line = BACKLINK.sub(r"\1", ANCHOR.sub("", line)) if line.strip() else line
        out.append(line)
    linked, _ = rewrite_links("\n".join(out), page, anchors)
    return re.sub(r"\n{3,}", "\n\n", linked).strip("\n") + "\n"
