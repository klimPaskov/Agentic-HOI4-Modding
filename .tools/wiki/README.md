# Offline Paradox wiki snapshot tooling

`paradox_wiki/` is the repository's required Hearts of Iron IV modding reference. It holds one markdown file per wiki modding page, named `<Page Title> - Hearts of Iron 4 Wiki.md`, plus `media/` with every image those pages reference. `AGENTS.md` points every implementation task at it, so it has to stay current, self-contained, and clean enough to read as ordinary markdown.

These two tools maintain it. They never launch Hearts of Iron IV and never claim engine evidence.

## Refresh the snapshot

```powershell
python -B .tools/wiki/sync_wiki_snapshot.py
python -B .tools/wiki/verify_wiki_snapshot.py
```

`sync_wiki_snapshot.py` writes `paradox_wiki/` in place. `verify_wiki_snapshot.py` is the acceptance check and exits non-zero when the snapshot is not self-contained; always run it after a refresh and commit both together.

### What the sync does

For each page it fetches the rendered article through the wiki's MediaWiki parse API — not the page skin — so the community-maintenance banners, edit links, and footer boxes never reach the markdown. The parsed HTML is then converted with:

- real code fences, so multi-line examples stay inside code blocks and headings stay headings;
- multi-line code samples hoisted out of table cells. A markdown table row is a single line, so a preformatted block cannot live in a cell: renderers collapse the indentation and copied text loses it. A cell holding a multi-line sample keeps a `*(example below)*` pointer, and the sample becomes a fenced code block labelled `**Example: <row name>**` directly after its table. Single-line samples stay inline, where they read correctly;
- rectangular markdown tables: nested tables become lists, `colspan` is expanded, ragged rows are padded or merged, and all-empty trailing columns are dropped;
- LaTeX math left as inline text instead of the wiki's Wikipedia-hosted formula images;
- section anchors trailing each heading, so intra-snapshot links resolve while the heading text still reads cleanly;
- the wiki's own `Modding navbox` restored as a local navigation list;
- no outbound hyperlinks at all. A wiki link resolves to a snapshot file when that page is in the snapshot, and is reduced to its visible text otherwise.

Existing `media/` files are reused by matching image alt text, so a refresh only downloads genuinely new images.

### Options

| Option | Effect |
| --- | --- |
| `--only PAGE [PAGE ...]` | refresh only the named wiki pages |
| `--new-only` | build only the pages listed in `NEW_PAGES` that have no file yet |
| `--dry-run --out DIR` | convert without touching `paradox_wiki/` |
| `--cache [DIR]` | reuse cached API responses (default `.tmp/wiki_cache`); omit to always fetch live |
| `--prune-media` | after writing, delete media files no page references |

A normal run intentionally fetches the live wiki, so an accidental stale snapshot is not possible. Use `--cache` only while iterating on the converter.

### Adding a wiki page

The snapshot is scoped to the wiki's modding documentation — its `Category:Modding` members and the pages in `Template:Modding navbox`. When the wiki gains a modding page, add its title to `NEW_PAGES` in `sync_wiki_snapshot.py` and refresh. Pages the wiki redirects elsewhere need no file: they are mapped in `REDIRECT_ANCHORS` so links land on the target page and section.

`Effects` keeps its historical file name, `Effects - Hearts of Iron 4 Wiki.md`, because the rest of the repository links to that exact path, even though the wiki page is now `Effect`. That mapping lives in `FILENAME_OVERRIDES`.

## Validate the snapshot

```powershell
python -B .tools/wiki/verify_wiki_snapshot.py
python -B .tools/wiki/verify_wiki_snapshot.py .tmp/wiki-preview
python -B .tools/wiki/verify_wiki_snapshot.py --quiet
```

It reports unbalanced or table-breaking code fences, outbound hyperlinks, links to missing files, section links whose anchor is absent, images with no file, image files nothing references, table rows whose column count differs from their header, pages without exactly one level-1 heading, `:` definition-list lines (not CommonMark, and a four-space-indented one renders as a code block), a multi-line code sample flattened into a single code span of 300 characters or more, code inside a table cell that is indented four spaces or more (a hoisting miss, since a renderer collapses it), and encoding damage such as byte order marks, escaped punctuation, non-breaking or zero-width characters, and mojibake.

It also prints the number of table rows over 400 characters. That is a report, not a failure: a markdown table row is one line by definition, so rows carrying a code example are legitimately long.

A single `escape_artifact` line is expected on a healthy snapshot: some backslash escapes (`\*`, `` \` ``, `\|` inside table cells, `\[`, a leading `\-`) are genuinely required markdown. Treat any other finding as a defect.

## Dependencies

Both tools need Python 3.9 or newer with `requests`, `beautifulsoup4`, and `markdownify`:

```powershell
python -m pip install requests beautifulsoup4 markdownify
```

The sync tool fails fast with that command when an import is missing.

## Caches and generated files

`--cache` writes under `.tmp/wiki_cache/`, which the repository root `.gitignore` already excludes. No tool in this directory writes anything else outside `paradox_wiki/`.

## Downstream copy

`agentic_hoi4_modding` mirrors this snapshot for its setup package. After committing a refresh here, copy `paradox_wiki/` there, commit it, and regenerate that repository's `hoi4-mod-setup.manifest.json` with its own `scripts/generate_manifest_evidence.py --revision <new commit>` so the wiki component pins the refreshed hashes.
