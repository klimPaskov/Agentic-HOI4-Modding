#!/usr/bin/env python
"""Regenerate the offline Paradox wiki snapshot from the live Hearts of Iron IV wiki.

``paradox_wiki/`` holds one markdown file per wiki modding page, named
``<Page Title> - Hearts of Iron 4 Wiki.md``, plus ``media/`` with every image
those pages reference. ``AGENTS.md`` treats that snapshot as the required wiki
reference, so it has to stay current and self-contained.

For each page the tool:

* fetches the rendered article through the MediaWiki parse API, so the
  community-notice chrome, edit links and footer boxes never reach the markdown;
* converts that HTML to clean markdown - real code fences, rectangular tables,
  LaTeX math kept as text instead of wiki-hosted images, and section anchors
  that intra-snapshot links can target;
* links only to pages the snapshot actually contains, so the result works with
  no network access and carries no outbound hyperlinks;
* reuses the media already on disk by matching image alt text, and downloads
  only genuinely new images;
* restores the wiki's own ``Modding navbox`` as a local navigation list.

The tool writes to ``paradox_wiki/`` in place. Run
``.tools/wiki/verify_wiki_snapshot.py`` afterwards; it is the acceptance check
for the result.

Usage::

    python -B .tools/wiki/sync_wiki_snapshot.py
    python -B .tools/wiki/sync_wiki_snapshot.py --dry-run --out .tmp/wiki-preview
    python -B .tools/wiki/sync_wiki_snapshot.py --only Triggers "Mod structure"
    python -B .tools/wiki/sync_wiki_snapshot.py --prune-media

Requires ``requests``, ``beautifulsoup4`` and ``markdownify``.
"""

from __future__ import annotations

import argparse
import html as htmllib
import json
import os
import re
import sys
import time
from collections import defaultdict

try:
    import requests
    from bs4 import BeautifulSoup, NavigableString, Tag
    import markdownify
    from markdownify import MarkdownConverter
except ImportError:  # pragma: no cover
    sys.exit("This tool needs requests, beautifulsoup4 and markdownify:\n"
             "  python -m pip install requests beautifulsoup4 markdownify")


def find_repo_root(start):
    """Walk up from this file until the snapshot directory is found."""
    current = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(current, "paradox_wiki")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            raise SystemExit("cannot locate the repository root: no paradox_wiki/ "
                             "directory above this script")
        current = parent


HERE = os.path.dirname(os.path.abspath(__file__))
REPO = find_repo_root(HERE)
WIKI_DIR = os.path.join(REPO, "paradox_wiki")
MEDIA_DIR = os.path.join(WIKI_DIR, "media")
DEFAULT_CACHE = os.path.join(REPO, ".tmp", "wiki_cache")
# Set by --cache. Unset means every run fetches the live wiki, which is the
# right default for a snapshot updater.
CACHE_DIR = None

API = "https://hoi4.paradoxwikis.com/api.php"
SITE = "https://hoi4.paradoxwikis.com"
UA = "chaos-redux-wiki-sync/1.0 (maintains a local offline HOI4 modding reference snapshot)"
CAPTURE_DATE = time.strftime("%Y-%m-%d")

# Local file name for a wiki page title. The snapshot keeps the historical
# "Effects" name for the wiki page "Effect" because the rest of the repository
# links to that exact file name.
FILENAME_OVERRIDES = {
    "Effect": "Effects",
}

# Pages the wiki redirects elsewhere; the snapshot has no file for them, so a
# link to one must resolve to the target page plus the target anchor.
REDIRECT_ANCHORS = {
    "Conditions": ("Triggers", None),
    "Trigger": ("Triggers", None),
    "Diplomacy scripted triggers": ("Triggers", None),
    "Scripted trigger": ("Triggers", None),
    "Variables": ("Data structures", "variables"),
    "Variable": ("Data structures", "variables"),
    "Temp variable": ("Data structures", "variables"),
    "Game variable": ("Data structures", "variables"),
    "Array": ("Data structures", "arrays"),
    "Arrays": ("Data structures", "arrays"),
    "Flag": ("Data structures", "flags"),
    "Flags": ("Data structures", "flags"),
    "Event targets": ("Data structures", "event-targets"),
    "Country tag aliases": ("Data structures", "country-tag-aliases"),
    "Modifier": ("Modifiers", None),
    "Static modifier": ("Modifiers", "static-modifiers"),
    "Static modifiers": ("Modifiers", "static-modifiers"),
    "Dynamic modifiers": ("Modifiers", "dynamic-modifiers"),
    "Scripted localisation": ("Localisation", None),
    "Text icon": ("Localisation", "text-icons"),
    "Scripted effect": ("Effect", "scripted-effects"),
    "Meta effect": ("Effect", "meta-effects"),
    "Meta effects": ("Effect", "meta-effects"),
    "SpriteType": ("Graphical asset modding", "spritetype"),
    "Replace path": ("Modding", "replace-path"),
    "User directory": ("Modding", "user-directory"),
    "On action": ("On actions", None),
    "Scope": ("Scopes", None),
    "Cosmetic tag": ("Cosmetic tag modding", None),
    "Game rules": ("Custom difficulty", None),
    "Military industrial organisation": ("Military industrial organization", None),
    "Raids": ("Raid", None),
    "Ideologies": ("Ideology", None),
    "Launch option": ("Launch options", None),
    "Map modes": ("Map", None),
    "AI strategy plans": ("AI modding", None),
    "Opinion": ("Diplomacy", None),
    "Stability": ("Government", None),
    "War support": ("Government", None),
    "Command power": ("Government", None),
    "Buildings": ("Construction", None),
    "Production efficiency": ("Production", None),
    "State category": ("State", None),
    "Decisions": ("List of Decision lists", None),
    "Checksum": ("Patches", None),
    "Ace": ("Air warfare", None),
    "DLC": ("Downloadable content", None),
}

SESSION = requests.Session()
SESSION.headers["User-Agent"] = UA

_last_request = [0.0]
MIN_INTERVAL = 0.6


def api(**params):
    """Call the wiki API with polite pacing and retries."""
    params.setdefault("format", "json")
    params.setdefault("formatversion", "2")
    last = None
    for attempt in range(6):
        gap = time.time() - _last_request[0]
        if gap < MIN_INTERVAL:
            time.sleep(MIN_INTERVAL - gap)
        try:
            resp = SESSION.get(API, params=params, timeout=90)
            _last_request[0] = time.time()
            resp.raise_for_status()
            resp.encoding = "utf-8"
            if not resp.text.strip():
                raise ValueError("empty response body")
            return resp.json()
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(2.5 * (attempt + 1))
    raise RuntimeError(f"wiki API call failed: {params!r}: {last}")


def cached(key, producer):
    """Memoise an API result, but only when --cache asked for one.

    Without a cache directory every call goes to the live wiki, so a normal run
    can never write a stale snapshot.
    """
    if not CACHE_DIR:
        return producer()
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, key + ".json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    value = producer()
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(value, fh, ensure_ascii=False)
    return value


def page_html(title):
    def produce():
        return api(action="parse", page=title, prop="text", disabletoc="1",
                   disablelimitreport="1", disableeditsection="1")["parse"]["text"]
    return cached("html_" + re.sub(r"[^A-Za-z0-9]+", "_", title), produce)


def page_info(titles):
    """Return {title: canonical title} following wiki redirects."""
    def produce():
        out = {}
        uniq = sorted(set(titles))
        for i in range(0, len(uniq), 20):
            batch = uniq[i:i + 20]
            data = api(action="query", titles="|".join(batch), prop="info",
                       redirects="1")
            norm = {n["from"]: n["to"] for n in data["query"].get("normalized", [])}
            red = {r["from"]: r["to"] for r in data["query"].get("redirects", [])}
            for title in batch:
                key = norm.get(title, title)
                out[title] = red.get(key, key)
        return out
    import hashlib
    key = hashlib.sha1("\n".join(sorted(set(titles))).encode("utf-8")).hexdigest()[:16]
    return cached("info_" + key, produce)


# --------------------------------------------------------------------------
# media handling
# --------------------------------------------------------------------------

def old_media_index():
    """Map page title -> ordered list of (alt text, media file name) from the
    markdown currently on disk, so existing downloads keep their file names."""
    index = defaultdict(list)
    if not os.path.isdir(WIKI_DIR):
        return index
    for name in os.listdir(WIKI_DIR):
        if not name.endswith(".md"):
            continue
        title = re.sub(r" - Hearts of Iron 4 Wiki\.md$", "", name)
        with open(os.path.join(WIKI_DIR, name), "r", encoding="utf-8") as fh:
            text = fh.read()
        for m in re.finditer(r"!\[([^\]]*)\]\(([^)]*media/[^)]+)\)", text):
            alt, src = m.group(1), m.group(2)
            base = os.path.basename(src)
            index[title].append((htmllib.unescape(alt), base))
    return index


OLD_MEDIA = old_media_index()
# An image reused across pages was named after the page that first fetched it,
# so alt text also resolves through a snapshot-wide index.
OLD_MEDIA_GLOBAL = {}
for _title in sorted(OLD_MEDIA):
    for _alt, _base in OLD_MEDIA[_title]:
        if _alt:
            OLD_MEDIA_GLOBAL.setdefault(_alt, _base)

NEW_MEDIA = []
UNRESOLVED = []
NO_DOWNLOAD = bool(os.environ.get("WIKI_SYNC_NO_DOWNLOAD"))
_URL_CACHE = {}


def _slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") + "-hearts-of-iron-4-wiki"


def _alt_from_url(url):
    """Fallback alt text: the wiki file name behind an image URL."""
    stem = os.path.basename(url.split("?")[0])
    stem = re.sub(r"^\d+px-", "", stem)
    stem = os.path.splitext(stem)[0]
    return re.sub(r"[_-]+", " ", stem).strip()


def resolve_media(title, alt, url, img_index):
    """Return the markdown image reference for a wiki image, downloading when new."""
    if url.startswith("/"):
        url = SITE + url
    raw_alt = htmllib.unescape(alt or "").strip()
    # Template icons arrive with unsubstituted placeholders; the file name is a
    # far more useful caption.
    if not raw_alt or "{{{" in raw_alt or "}}}" in raw_alt:
        raw_alt = _alt_from_url(url)
    label = f"![{raw_alt}]"

    def reference(base):
        return f"{label}(media/{base})"

    cached_base = _URL_CACHE.get(url)
    if cached_base and os.path.exists(os.path.join(MEDIA_DIR, cached_base)):
        return reference(cached_base)

    for candidate_alt, base in OLD_MEDIA.get(title, []):
        if candidate_alt == raw_alt and os.path.exists(os.path.join(MEDIA_DIR, base)):
            _URL_CACHE[url] = base
            return reference(base)
    base = OLD_MEDIA_GLOBAL.get(raw_alt)
    if base and os.path.exists(os.path.join(MEDIA_DIR, base)):
        _URL_CACHE[url] = base
        return reference(base)

    ext = os.path.splitext(url.split("?")[0])[1].lower() or ".png"
    digest = __import__("hashlib").sha1(url.encode("utf-8")).hexdigest()[:10]
    base = f"{_slug(title)}_{digest}__img{img_index}{ext}"
    _URL_CACHE[url] = base
    target = os.path.join(MEDIA_DIR, base)
    if NO_DOWNLOAD:
        UNRESOLVED.append((title, raw_alt, url, base))
        return reference(base)
    if not os.path.exists(target):
        os.makedirs(MEDIA_DIR, exist_ok=True)
        for attempt in range(4):
            try:
                gap = time.time() - _last_request[0]
                if gap < MIN_INTERVAL:
                    time.sleep(MIN_INTERVAL - gap)
                resp = SESSION.get(url, timeout=90)
                _last_request[0] = time.time()
                resp.raise_for_status()
                with open(target, "wb") as fh:
                    fh.write(resp.content)
                break
            except Exception:  # noqa: BLE001
                if attempt == 3:
                    raise
                time.sleep(2.5 * (attempt + 1))
    NEW_MEDIA.append(base)
    return reference(base)


# --------------------------------------------------------------------------
# HTML -> markdown
# --------------------------------------------------------------------------

DROP_CLASSES = {
    "mw-editsection", "mw-empty-elt", "navbox", "navbox-inner", "navbox-group",
    "navbox-list", "navbox-abovebelow", "noprint", "mw-jump-link",
    "mw-indicators", "printfooter", "catlinks", "mw-references-columns",
}
COMMUNITY_NOTICE = re.compile(r"^This is a community maintained wiki", re.I)
# The wiki renders {{Navbox}} with inline styles rather than a class, so the
# footer navigation boxes are recognised by their frame styling.
NAVBOX_FRAME = re.compile(r"border:\s*1px solid", re.I)
NAVBOX_CENTER = re.compile(r"text-align:\s*center", re.I)
CODE_LANGS = {
    "text": "text", "txt": "text", "python": "python", "py": "python",
    "lua": "lua", "javascript": "javascript", "js": "javascript",
    "css": "css", "html": "html", "xml": "xml", "json": "json", "yaml": "yaml",
    "bash": "bash", "shell": "bash", "c": "c", "cpp": "cpp",
}
PAGE_EXT = {"File", "Image", "Category", "Template", "Help", "Special",
            "Talk", "User", "Module", "MediaWiki", "Portal", "Draft"}

_counter = defaultdict(int)


class WikiConverter(MarkdownConverter):
    """Markdownify subclass tuned for MediaWiki article HTML."""

    def __init__(self, title, known_pages, local_title=None, **options):
        self.title = title
        self.local_title = local_title or title
        self.known = known_pages
        # Deepest heading emitted so far, used to keep levels contiguous.
        self.last_level = 2
        self.anchors = []
        options.setdefault("heading_style", "ATX")
        options.setdefault("bullets", "-")
        options.setdefault("strong_em_symbol", "*")
        options.setdefault("escape_underscores", False)
        options.setdefault("escape_asterisks", True)
        options.setdefault("escape_misc", True)
        options.setdefault("code_language", "text")
        options.setdefault("strip_pre", markdownify.STRIP)
        options.setdefault("newline_style", markdownify.SPACES)
        options.setdefault("keep_inline_images_in", ["td", "th", "li", "p", "dd", "dt"])
        options["code_language_callback"] = self.code_language
        super().__init__(**options)

    # -- helpers -----------------------------------------------------------
    @staticmethod
    def code_language(el):
        node = el
        while node is not None:
            classes = node.get("class") or [] if isinstance(node, Tag) else []
            for cls in classes:
                if cls.startswith("mw-highlight-lang-"):
                    return CODE_LANGS.get(cls[len("mw-highlight-lang-"):], "text")
            node = node.parent
        return "text"

    def wiki_target(self, href):
        """Turn a wiki href into (page title, anchor) or None for non-wiki."""
        if not href:
            return None
        from urllib.parse import unquote
        if href.startswith("#"):
            return (self.title, unquote(href[1:]))
        for prefix in (SITE + "/index.php", SITE + "/", "/index.php", "/"):
            if href.startswith(prefix):
                rest = href[len(prefix):]
                break
        else:
            return None
        # The fragment keeps the wiki's own spelling; only the page title uses
        # the spaces-for-underscores convention.
        anchor = None
        if "#" in rest:
            rest, anchor = rest.split("#", 1)
            anchor = unquote(anchor)
        if rest.startswith("?") or rest.startswith("index.php"):
            m = re.search(r"[?&]title=([^&]+)", rest)
            if not m:
                return None
            page = unquote(m.group(1))
        else:
            page = unquote(rest)
        page = page.replace("_", " ").strip()
        if not page or page.split(":")[0] in PAGE_EXT:
            return None
        return (page, anchor)

    @staticmethod
    def local_name(page):
        return FILENAME_OVERRIDES.get(page, page) + " - Hearts of Iron 4 Wiki.md"

    def link_for(self, page, anchor, text):
        redirect = REDIRECT_ANCHORS.get(page)
        if redirect:
            page, redirect_anchor = redirect
            anchor = anchor or redirect_anchor
        if page not in self.known:
            # The snapshot only ever links to pages it actually contains, so it
            # stays fully usable without network access.
            return text
        target = self.local_name(page)
        suffix = f"#{anchor}" if anchor else ""
        return f"[{text}](<{target}{suffix}>)"

    # -- overrides ---------------------------------------------------------
    def convert_a(self, el, text, parent_tags):
        classes = el.get("class") or []
        if "mw-selflink" in classes or "image" in classes:
            return text
        href = el.get("href") or ""
        target = self.wiki_target(href)
        if target is not None:
            page, anchor = target
            if page == self.title and anchor:
                return f"[{text}](#{anchor})"
            return self.link_for(page, anchor, text)
        if href.startswith("#"):
            return f"[{text}](#{href[1:]})"
        # The snapshot keeps every reference inside the snapshot, so off-wiki
        # links are reduced to their visible text.
        if href:
            return text
        return text

    def convert_img(self, el, text, parent_tags):
        src = el.get("src") or el.get("data-src") or ""
        alt = el.get("alt") or ""
        if not src:
            return ""
        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = SITE + src
        if "/images/" not in src:
            return ""
        _counter[self.local_title] += 1
        return resolve_media(self.local_title, alt, src, _counter[self.local_title])

    def convert_pre(self, el, text, parent_tags):
        code = el.get_text()
        code = code.replace("\u00a0", " ").replace("\u200b", "")
        code = code.replace("\r\n", "\n").strip("\n")
        if el.find_parent("table") is not None:
            return self.inline_code_block(code)
        fence = "```"
        while fence in code:
            fence += "`"
        return f"\n\n{fence}{self.code_language(el)}\n{code}\n{fence}\n\n"

    @staticmethod
    def inline_code_block(code):
        """Render a multi-line code sample so it survives inside a table cell.

        A fenced block would end the table row, so each line becomes its own
        code span and the lines are joined with ``<br>``. Line structure and
        indentation are preserved, and the cell still renders as a block of
        code rather than one long run of text.
        """
        lines = code.split("\n")
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        rendered = []
        for line in lines:
            line = line.rstrip().replace("|", "\\|")
            if not line:
                # An empty cell line: the surrounding joins produce <br><br>.
                rendered.append("")
                continue
            ticks = "`"
            while ticks in line:
                ticks += "`"
            pad = " " if line.startswith("`") or line.endswith("`") else ""
            rendered.append(f"{ticks}{pad}{line}{pad}{ticks}")
        return "<br>".join(rendered)

    def convert_br(self, el, text, parent_tags):
        # A literal newline would split the markdown table row, so line breaks
        # inside a cell stay as inline HTML.
        if el.find_parent(["td", "th"]) is not None:
            return "<br>"
        return super().convert_br(el, text, parent_tags)

    def convert_div(self, el, text, parent_tags):
        classes = set(el.get("class") or [])
        if classes & DROP_CLASSES:
            return ""
        if "mw-highlight" in classes:
            return "\n\n" + text.strip() + "\n\n"
        if "thumb" in classes or "mw-halign" in " ".join(classes):
            caption = el.find("figcaption") or el.find(class_="thumbcaption")
            cap = caption.get_text(" ", strip=True) if caption else ""
            cap = re.sub(r"\s+", " ", cap).strip()
            body = text.strip()
            if cap and body:
                return f"\n\n{body}\n\n*{cap}*\n\n"
            return f"\n\n{body}\n\n" if body else ""
        if "hatnote" in classes or "dablink" in classes or "rellink" in classes:
            note = re.sub(r"[ \t]+", " ", text).strip()
            return f"\n\n*{note}*\n\n"
        if "mw-references-wrap" in classes:
            return "\n\n" + text.strip() + "\n\n"
        if "eu4box" in classes or "metadata" in classes:
            return ""
        return text

    def convert_table(self, el, text, parent_tags):
        classes = set(el.get("class") or [])
        if "navbox" in classes or "infobox" in classes and "metadata" in classes:
            return ""
        return super().convert_table(el, text, parent_tags)

    def convert_hN(self, n, el, text, parent_tags):
        if "_inline" in parent_tags:
            return text
        ids = []
        for node in el.find_all(True):
            if node.get("id"):
                ids.append(node["id"])
        if el.get("id"):
            ids.insert(0, el["id"])
        clean = re.sub(r"\[\s*edit\s*\]", "", text, flags=re.I)
        clean = re.sub(r"\s+", " ", clean).strip()
        clean = clean.replace("[edit]", "").strip()
        if not clean:
            return ""
        # The article starts at level 2 because the page title owns level 1, and
        # the wiki skips levels in places, so a heading never jumps more than one
        # step past the previous one.
        level = 2 if n <= 2 else min(n, self.last_level + 1)
        self.last_level = level
        unique = list(dict.fromkeys(ids))
        anchors = "".join(f'<a id="{i}"></a>' for i in unique)
        # The anchor trails the visible title so the heading still reads as
        # plain text while wiki-style section links keep resolving.
        tail = f" {anchors}" if anchors else ""
        self.anchors.append({"level": level, "id": unique[0] if unique else None,
                             "text": clean, "ids": unique})
        return f"\n\n{'#' * level} {clean}{tail}\n\n"

    def convert_sup(self, el, text, parent_tags):
        if el.get("class") and "reference" in (el.get("class") or []):
            return text
        return super().convert_sup(el, text, parent_tags)

    def convert_style(self, el, text, parent_tags):
        return ""

    def convert_script(self, el, text, parent_tags):
        return ""


# --------------------------------------------------------------------------
# page assembly
# --------------------------------------------------------------------------

def clean_soup(title):
    """Return (soup, article_root, navboxes) with wiki chrome removed."""
    soup = BeautifulSoup(page_html(title), "html.parser")
    root = soup.find("div", class_="mw-parser-output") or soup
    for sel in ["span.mw-editsection", "div.navbox", "table.navbox",
                "div.toc", "table#toc", "style", "script", "link",
                "div.mw-indicators", "div.mw-empty-elt", "span.mw-editsection"]:
        for node in root.select(sel):
            node.decompose()

    navboxes = extract_navboxes(root)
    unwrap_layout_tables(root, soup)
    flatten_nested_tables(root, soup)
    finalise_article(root, soup)
    return soup, root, navboxes


def unwrap_layout_tables(root, soup):
    """Replace wiki layout tables with the blocks they were arranging.

    The wiki uses tables for page layout as well as for data: floated halves, and
    ``eu4box-inline`` boxes whose header sits in a ``th``. Markdown has no layout
    tables, and rendering them as data tables buries the real content in a
    one-cell row. The cells are spliced back into the flow instead, so a box
    header becomes a bold line and any table or code sample inside it stays a
    table or a code block.
    """
    for table in list(root.find_all("table")):
        style = (table.get("style") or "").lower()
        classes = " ".join(table.get("class") or []).lower()
        if "float:" not in style and "eu4box-inline" not in classes:
            continue

        blocks = []
        for row in table.find_all("tr"):
            if row.find_parent("table") is not table:
                continue
            for cell in row.find_all(["td", "th"], recursive=False):
                if cell.name == "th":
                    label = cell.get_text(" ", strip=True)
                    label = label.rstrip("\u25bc\u25b2 ").strip()
                    if label:
                        para = soup.new_tag("p")
                        strong = soup.new_tag("strong")
                        strong.string = label
                        para.append(strong)
                        blocks.append(para)
                    continue
                for child in list(cell.contents):
                    blocks.append(child.extract())
        for block in blocks:
            table.insert_before(block)
        table.decompose()


def flatten_nested_tables(root, soup):
    """Turn a table nested in a table cell into a list.

    Markdown cannot nest tables. Only a table's own rows are considered, so an
    outer wrapper never swallows the rows of a table it merely contains.
    """
    tables = [t for t in root.find_all("table") if t.find_parent("table") is not None]
    for table in reversed(tables):
        headers = [th.get_text(" ", strip=True) for th in table.find_all("th")
                   if th.find_parent("table") is table]
        listing = soup.new_tag("ul")
        for row in table.find_all("tr"):
            if row.find_parent("table") is not table:
                continue
            values = [c.get_text(" ", strip=True)
                      for c in row.find_all(["td", "th"], recursive=False)]
            if not any(values) or values == headers:
                continue
            if headers and len(headers) == len(values):
                entry = "; ".join(f"{h}: {v}" for h, v in zip(headers, values) if v)
            else:
                entry = " - ".join(v for v in values if v)
            if entry:
                item = soup.new_tag("li")
                item.string = entry
                listing.append(item)
        table.replace_with(listing)


def finalise_article(root, soup):
    """Final cleanup pass once layout boxes and nested tables are resolved."""
    # colspan makes a row shorter than its header; expand it so the markdown
    # table keeps a rectangular shape.
    for cell in root.find_all(["td", "th"]):
        try:
            span = int(cell.get("colspan") or 1)
        except (TypeError, ValueError):
            span = 1
        for _ in range(max(0, span - 1)):
            cell.insert_after(soup.new_tag(cell.name))

    # <math> renders as an image hosted on wikipedia.org. Keep the snapshot
    # self-contained and searchable by keeping the LaTeX source instead.
    for span in root.find_all("span", class_="mwe-math-element"):
        tex = None
        annotation = span.find("annotation", attrs={"encoding": "application/x-tex"})
        if annotation is not None and annotation.string:
            tex = annotation.string
        else:
            math_el = span.find("math")
            if math_el is not None and math_el.get("alttext"):
                tex = math_el["alttext"]
        if not tex:
            continue
        tex = tex.strip()
        if tex.startswith("{\\displaystyle"):
            tex = tex[len("{\\displaystyle"):].strip()
            if tex.endswith("}"):
                tex = tex[:-1]
        code = soup.new_tag("code")
        code.string = tex.strip()
        span.replace_with(code)

    # Monospace "path" spans read as inline code in markdown.
    for span in root.find_all("span"):
        style = span.get("style") or ""
        if "monospace" not in style:
            continue
        if span.find(True) is not None:
            continue
        code = soup.new_tag("code")
        code.string = span.get_text()
        span.replace_with(code)

    for node in root.find_all("div"):
        style = node.get("style") or ""
        if "clear: both" in style or "clear:both" in style:
            node.decompose()

    # Community-maintenance banners repeat on every page and carry no content.
    for node in list(root.select("div.eu4box, table.ambox, div.ambox, table.mbox-small-left")):
        text = re.sub(r"\s+", " ", node.get_text(" ", strip=True))
        if COMMUNITY_NOTICE.match(text) or not text:
            node.decompose()

    for node in list(root.select("table.ambox, div.ambox")):
        text = re.sub(r"\s+", " ", node.get_text(" ", strip=True))
        note = soup.new_tag("p")
        note.string = f"*{text}*"
        node.replace_with(note)

    # Word-joiner and non-breaking characters survive the wiki's nowrap
    # templates and only get in the way of searching the snapshot.
    for node in root.find_all(string=True):
        if any(ch in node for ch in ("\u00a0", "\u200b", "\u2011", "\u2009",
                                     "\u200a", "\u202f", "\ufeff")):
            node.replace_with(node.replace("\u00a0", " ").replace("\u200b", "")
                              .replace("\u2011", "-").replace("\u2009", " ")
                              .replace("\u200a", " ").replace("\u202f", " ")
                              .replace("\ufeff", ""))

    # <sup class="reference"> renders as an escaped, linked "[\[1\]](#cite_note-1)".
    # A plain marker keeps the same information without the noise.
    for sup in root.find_all("sup", class_="reference"):
        label = sup.get_text(" ", strip=True).strip("[] \u00a0")
        sup.replace_with(NavigableString(f"[{label}]"))


def extract_navboxes(root):
    """Pull {{Navbox}} footers out of the article and describe them."""
    frames = []
    for div in root.find_all("div"):
        style = div.get("style") or ""
        if NAVBOX_FRAME.search(style) and NAVBOX_CENTER.search(style):
            frames.append(div)
    # keep only outermost frames
    outermost = [d for d in frames
                 if not any(o is not d and o in d.parents for o in frames)]
    boxes = []
    for frame in outermost:
        header = frame.find("b")
        title = header.get_text(" ", strip=True) if header else ""
        groups = []
        for table in frame.find_all("table"):
            cells = table.find_all("td")
            if len(cells) < 2:
                continue
            label = cells[0].get_text(" ", strip=True)
            links = []
            for a in cells[1].find_all("a"):
                href = a.get("href") or ""
                if not href.startswith("/"):
                    continue
                from urllib.parse import unquote
                page = unquote(href[1:]).split("#")[0].replace("_", " ")
                anchor = href.split("#", 1)[1] if "#" in href else None
                links.append((page, anchor, a.get_text(" ", strip=True)))
            if links:
                groups.append((label, links))
        if groups:
            boxes.append({"title": title, "groups": groups})
        frame.decompose()
    return boxes


def split_md_row(line):
    """Split a markdown table row on pipes that are not backslash-escaped."""
    cells, current, i = [], [], 0
    while i < len(line):
        ch = line[i]
        if ch == "\\" and i + 1 < len(line):
            current.append(ch)
            current.append(line[i + 1])
            i += 2
            continue
        if ch == "|":
            cells.append("".join(current))
            current = []
            i += 1
            continue
        current.append(ch)
        i += 1
    cells.append("".join(current))
    return cells


def fix_tables(text):
    """Make every markdown table rectangular and consistently spaced."""
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if (line.strip().startswith("|") and i + 1 < len(lines)
                and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1])):
            block = [split_md_row(line)]
            separator = split_md_row(lines[i + 1])[1:-1]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(split_md_row(lines[i]))
                i += 1
            width = max(len(cells) - 2 for cells in block)
            if width <= 0:
                out.append(line)
                continue
            padded = []
            for cells in block:
                inner = cells[1:-1]
                if len(inner) < width:
                    inner = inner + [""] * (width - len(inner))
                elif len(inner) > width:
                    merged = inner[width - 1].strip()
                    for extra in inner[width:]:
                        merged += " \\| " + extra.strip()
                    inner = inner[:width - 1] + [merged]
                padded.append([c.strip() for c in inner])
            # The wiki leaves all-empty trailing columns behind; drop them.
            while width > 1 and all(row[width - 1] == "" for row in padded):
                width -= 1
                for row in padded:
                    row.pop()
            if len(separator) != width:
                separator = ["---"] * width
            out.append("| " + " | ".join(padded[0]) + " |")
            out.append("| " + " | ".join(s.strip() for s in separator) + " |")
            for row in padded[1:]:
                out.append("| " + " | ".join(row) + " |")
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def convert(local_title, source_title, known_pages):
    soup, root, navboxes = clean_soup(source_title)
    conv = WikiConverter(source_title, known_pages, local_title=local_title)
    body = conv.convert_soup(root)
    body = fix_tables(body)
    body = body.replace("\\=", "=")
    body = unescape_safe_angles(body)
    body = wrap_bracket_placeholders(body)
    body = reduce_escapes(body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    body = re.sub(r"[ \t]+\n", "\n", body)
    body = body.strip() + "\n"
    return body, conv.anchors, navboxes


def build_toc(anchors):
    lines = []
    base = None
    for a in anchors:
        if not a["id"]:
            continue
        if base is None:
            base = a["level"]
        depth = max(0, a["level"] - base)
        lines.append("  " * depth + f"- [{a['text']}](#{a['id']})")
    return "\n".join(lines)


def render_link(page, anchor, label, known):
    redirect = REDIRECT_ANCHORS.get(page)
    tgt_page, tgt_anchor = (redirect[0], anchor or redirect[1]) if redirect else (page, anchor)
    if tgt_page not in known:
        return label
    suffix = f"#{tgt_anchor}" if tgt_anchor else ""
    return f"[{label}](<{WikiConverter.local_name(tgt_page)}{suffix}>)"


def navbox_footer(navboxes, known):
    """Render the wiki's own footer navigation boxes as local link lists."""
    modding = None
    others = []
    for box in navboxes:
        if box["title"].strip().lower() == "modding":
            modding = box
        else:
            others.append(box)
    out = ["## Navigation", ""]
    if modding:
        out += ["**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**", ""]
        for label, links in modding["groups"]:
            rendered, seen = [], set()
            for page, anchor, text in links:
                if (page, anchor) in seen:
                    continue
                seen.add((page, anchor))
                rendered.append(render_link(page, anchor, text, known))
            out.append(f"- **{label}**: " + " • ".join(rendered))
        out.append("")
    for box in others:
        out.append(f"**{box['title']}**")
        out.append("")
        for label, links in box["groups"]:
            rendered, seen = [], set()
            for page, anchor, text in links:
                if (page, anchor) in seen:
                    continue
                seen.add((page, anchor))
                rendered.append(render_link(page, anchor, text, known))
            out.append(f"- **{label}**: " + " • ".join(rendered))
        out.append("")
    return "\n".join(out).strip() + "\n"


def render(local_title, source_title, known_pages):
    body, anchors, navboxes = convert(local_title, source_title, known_pages)
    parts = [f"# {local_title}", ""]
    parts.append(f"*Offline snapshot of the Hearts of Iron IV Wiki page "
                 f"\"{source_title}\", captured {CAPTURE_DATE}.*")
    parts.append("")
    toc = build_toc(anchors)
    if toc:
        parts += ["## Table of contents", "", toc, ""]
    parts += ["---", "", body.rstrip(), ""]
    if navboxes:
        parts += ["---", "", navbox_footer(navboxes, known_pages)]
    text = "\n".join(parts)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.rstrip() + "\n"


HTML_TAGS = {
    "a", "abbr", "area", "article", "aside", "audio", "b", "base", "bdi", "bdo",
    "blockquote", "body", "br", "button", "canvas", "caption", "cite", "code",
    "col", "colgroup", "data", "datalist", "dd", "del", "details", "dfn",
    "dialog", "div", "dl", "dt", "em", "embed", "fieldset", "figcaption",
    "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "head",
    "header", "hgroup", "hr", "html", "i", "iframe", "img", "input", "ins",
    "kbd", "label", "legend", "li", "link", "main", "map", "mark", "menu",
    "meta", "meter", "nav", "noscript", "object", "ol", "optgroup", "option",
    "output", "p", "param", "picture", "pre", "progress", "q", "rp", "rt",
    "ruby", "s", "samp", "script", "search", "section", "select", "slot",
    "small", "source", "span", "strong", "style", "sub", "summary", "sup",
    "svg", "table", "tbody", "td", "template", "textarea", "tfoot", "th",
    "thead", "time", "title", "tr", "track", "u", "ul", "var", "video", "wbr",
}


def reduce_escapes(text):
    """Drop backslashes that markdownify adds but markdown never needs.

    Hyphens, dots, pluses and hashes only need escaping where they could open a
    list or a heading, pipes only inside table rows, and parentheses never
    unless they would close a link. Everything else stays escaped.
    """
    out = []
    for line in text.split("\n"):
        match = re.match(r"^(\s*)(.*)$", line)
        indent, body = match.group(1), match.group(2)
        in_table = body.startswith("|")
        result = []
        i = 0
        while i < len(body):
            ch = body[i]
            if ch != "\\" or i + 1 >= len(body):
                result.append(ch)
                i += 1
                continue
            nxt = body[i + 1]
            at_line_start = not result
            if nxt in "-+.#":
                keep = at_line_start
            elif nxt == ".":
                keep = at_line_start
            elif nxt == "|":
                keep = in_table
            elif nxt == "(":
                keep = bool(result) and result[-1] == "]"
            elif nxt == ")":
                keep = False
            elif nxt == "!":
                keep = at_line_start or (i + 2 < len(body) and body[i + 2] == "[")
            elif nxt == "\\":
                # A literal backslash (a Windows path, say) needs no doubling
                # when a plain word follows it.
                following = body[i + 2] if i + 2 < len(body) else ""
                if following.isalnum():
                    result.append("\\")
                    i += 2
                    continue
                keep = True
            else:
                keep = True
            result.append("\\" + nxt if keep else nxt)
            i += 2
        out.append(indent + "".join(result))
    return "\n".join(out)


def wrap_bracket_placeholders(text):
    """Render escaped "[...]" spans as plain markers or inline code.

    The wiki writes command syntax such as ``[<equipment amount>]`` and numeric
    ranges as plain text, which markdownify has to escape. Bracketed digits are
    footnote markers and read best as plain text; everything else in brackets is
    syntax and becomes inline code, which removes the backslash noise and shows
    the reader what is literal.
    """
    def convert(match):
        inner = match.group(1)
        if "`" in inner or "|" in inner or "<" in inner and ">" not in inner:
            return match.group(0)
        if inner.isdigit():
            return f"[{inner}]"
        return f"`[{inner}]`"

    return re.sub(r"\\\[([^\[\]\n|`]{0,70}?)\\\]", convert, text)


def unescape_safe_angles(text):
    """Drop the backslash before angle brackets that cannot start markup."""
    def replace(match):
        token = match.group(1)
        if token.strip().lower() in HTML_TAGS:
            return match.group(0)
        return f"<{token}>"

    text = re.sub(r"\\<([^<>\\\n]{1,40})\\>", replace, text)
    # A lone "<" that is not followed by a tag start is always literal.
    text = re.sub(r"\\<(?![A-Za-z/!?])", "<", text)
    text = re.sub(r"(?<=[^\n])\\>", ">", text)
    return text


def repair_anchors(directory):
    """Drop fragments that do not exist in the target page.

    The live wiki carries a few stale section links of its own; the snapshot
    should not inherit them, so a link whose anchor is missing keeps its target
    file and loses only the fragment.
    """
    pages = {n: open(os.path.join(directory, n), encoding="utf-8").read()
             for n in os.listdir(directory) if n.endswith(".md")}
    anchors = {n: set(re.findall(r'<a id="([^"]+)"', t)) for n, t in pages.items()}
    fixed = 0
    for name, text in pages.items():
        def replace(match):
            nonlocal fixed
            target, anchor = match.group(1), match.group(2)
            base = target.split("#")[0]
            if base in anchors and anchor not in anchors[base]:
                fixed += 1
                return f"](<{base}>)"
            return match.group(0)

        new = re.sub(r"\]\(<([^>#]+)#([^>]+)>\)", replace, text)

        def replace_same(match):
            if match.group(2) in anchors[name]:
                return match.group(0)
            return match.group(1)

        new = re.sub(r"\[([^\]]*)\]\(#([^)\s]+)\)", replace_same, new)
        if new != text:
            with open(os.path.join(directory, name), "w", encoding="utf-8",
                      newline="\n") as fh:
                fh.write(new)
    return fixed


def local_titles():
    return sorted(re.sub(r" - Hearts of Iron 4 Wiki\.md$", "", n)
                  for n in os.listdir(WIKI_DIR) if n.endswith(".md"))


def prune_media(directory):
    """Delete media files that no page in the snapshot references."""
    if not os.path.isdir(directory):
        return 0
    referenced = set()
    for name in os.listdir(WIKI_DIR):
        if not name.endswith(".md"):
            continue
        text = open(os.path.join(WIKI_DIR, name), encoding="utf-8").read()
        referenced.update(os.path.basename(m)
                          for m in re.findall(r"\]\((media/[^)]+)\)", text))
    removed = 0
    for name in sorted(os.listdir(directory)):
        if name not in referenced:
            os.remove(os.path.join(directory, name))
            removed += 1
    return removed


# Wiki modding pages that belong in the snapshot but have no file yet. Add a
# title here when the live wiki gains a modding page.
NEW_PAGES = ["Mods", "Mod structure", "Nudger", "List of modifiers"]


def main():
    ap = argparse.ArgumentParser(
        description="Refresh the offline Hearts of Iron IV wiki snapshot.")
    ap.add_argument("--only", nargs="*", default=None, metavar="PAGE",
                    help="refresh only these wiki page titles")
    ap.add_argument("--new-only", action="store_true",
                    help="build only the pages listed in NEW_PAGES")
    ap.add_argument("--dry-run", action="store_true",
                    help="convert without writing to paradox_wiki/")
    ap.add_argument("--out", default=None, metavar="DIR",
                    help="directory that --dry-run writes to")
    ap.add_argument("--cache", nargs="?", const=DEFAULT_CACHE, default=None,
                    metavar="DIR",
                    help="cache API responses in DIR (default .tmp/wiki_cache); "
                         "omit to always fetch the live wiki")
    ap.add_argument("--prune-media", action="store_true",
                    help="after writing, delete media files nothing references")
    args = ap.parse_args()

    global CACHE_DIR
    CACHE_DIR = args.cache

    existing = local_titles()
    full_set = sorted(set(existing) | set(NEW_PAGES))
    # Link resolution always uses the whole snapshot, not just this run's filter.
    known = set(full_set) | set(REDIRECT_ANCHORS) | {"Effect", "Effects"}

    targets = full_set
    if args.new_only:
        targets = [t for t in targets if t in set(NEW_PAGES)]
    if args.only:
        wanted = set(args.only) | {FILENAME_OVERRIDES.get(t, t) for t in args.only}
        targets = [t for t in targets if t in wanted
                   or FILENAME_OVERRIDES.get(t, t) in wanted]
        if not targets:
            sys.stderr.write("no page matched --only\n")
            return 1

    out_dir = args.out
    if args.dry_run and out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # Some snapshot files carry the wiki's redirect name (Effects -> Effect);
    # convert the target page but keep the established local file name.
    canonical = page_info(full_set)
    for t in full_set:
        if canonical.get(t, t) != t:
            sys.stderr.write(f"note: {t} redirects to {canonical[t]}\n")

    failures = []
    for i, title in enumerate(targets, 1):
        source = canonical.get(title, title)
        sys.stderr.write(f"[{i}/{len(targets)}] {title}\n")
        sys.stderr.flush()
        try:
            text = render(title, source, known)
        except Exception as exc:  # noqa: BLE001
            failures.append((title, repr(exc)))
            continue
        if args.dry_run:
            if not out_dir:
                continue
            path = os.path.join(out_dir, WikiConverter.local_name(title))
        else:
            path = os.path.join(WIKI_DIR, WikiConverter.local_name(title))
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)

    if NEW_MEDIA:
        sys.stderr.write(f"new media files downloaded: {len(NEW_MEDIA)}\n")
    if UNRESOLVED:
        sys.stderr.write(f"images left for download: {len(UNRESOLVED)}\n")
        if CACHE_DIR:
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(os.path.join(CACHE_DIR, "pending_media.json"), "w",
                      encoding="utf-8") as fh:
                json.dump(UNRESOLVED, fh, ensure_ascii=False, indent=1)

    if failures:
        sys.stderr.write("FAILURES:\n")
        for t, e in failures:
            sys.stderr.write(f"  {t}: {e}\n")
        return 1

    if args.dry_run:
        target_dir = out_dir
    else:
        target_dir = WIKI_DIR
    if target_dir:
        dropped = repair_anchors(target_dir)
        sys.stderr.write(f"stale section links repaired: {dropped}\n")

    if args.prune_media and not args.dry_run:
        removed = prune_media(MEDIA_DIR)
        sys.stderr.write(f"unreferenced media files removed: {removed}\n")

    if not args.dry_run:
        sys.stderr.write("next: python -B .tools/wiki/verify_wiki_snapshot.py\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
