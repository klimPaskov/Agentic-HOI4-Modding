# Offline Paradox wiki snapshot tooling

`paradox_wiki/` is the kit's offline Hearts of Iron IV modding reference. It holds one Markdown file per page, named after the page title in lowercase kebab-case (`scripted-gui-modding.md`), `media/` with every image those pages show, and `LICENSE.txt`. Most pages are captured from the wiki's modding pages. The kit corrects and extends them against the installed game in kit blocks, and adds kit pages for systems the wiki does not cover. The project instructions point every implementation task at it, so it has to stay current and self-contained, and read cleanly as plain Markdown.

These tools maintain it. None of them launches Hearts of Iron IV.

| Tool | Job |
| --- | --- |
| `sync_wiki_snapshot.py` | refreshes the wiki pages from the live wiki and keeps every kit block |
| `verify_wiki_snapshot.py` | read-only acceptance check for the whole snapshot |
| `wiki_status.py` | says which pages are current for the installed game build and which to re-check after an update |
| `kit_blocks.py` | the page format the three tools share (no command line) |
| `game_docs_index.json` | the game documentation index for the build the snapshot was last checked against |

## Page format

```text
# Effects

*Offline snapshot of the Hearts of Iron IV Wiki page "Effect", revision 105661, captured 2026-10-31. ...*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="105661" sources="documentation/effects_documentation.md" -->
**Kit review (1.19.3.0):** what was checked, what the kit added or corrected, and the gaps left.
<!-- kit:end id="review" -->

## Table of contents
...
---
(wiki text, with kit blocks in place)
---
## Navigation
```

The capture line names the wiki page, its revision and the capture date. The sync regenerates everything outside kit blocks, so **never edit wiki text in place**: a hand edit there is lost on the next refresh.

### Kit blocks

A kit block is local text that survives every refresh:

```text
<!-- kit:begin id="set-autonomy-scope" at="section:Autonomy" -->
**Kit note** [docs] `set_autonomy` runs in country scope ...
<!-- kit:end id="set-autonomy-scope" -->
```

- `id`: lowercase letters, digits and hyphens, unique on the page.
- `at` says where the block belongs. The sync puts it back there in the fresh page:
  - `top`: under the capture line, before the table of contents (used by the review block);
  - `bottom`: after the last section, before the navigation footer;
  - `section:<anchor>`: at the end of that section's own text, before the next heading;
  - `heading:<anchor>`: directly under the heading, before the wiki text (use it for warnings about outdated text).

  `<anchor>` is an `<a id="...">` of a wiki heading on the same page. Blocks that share a place keep their order.
- The first line inside the block says it is kit text: `**Kit note**`, `**Kit correction**`, `**Kit addition**`, `**Kit review ...**`, or a heading that contains "Kit".
- A heading inside a block carries an anchor starting with `kit-`, for example `### Kit: raid categories <a id="kit-raid-categories"></a>`. The sync adds it to the table of contents.
- Never put a kit block inside a code fence or a table, nest blocks, or edit the markers by hand except for `at` and the review attributes.

When the wiki later removes the heading a block points at, the sync keeps the block at the bottom of the page and says so, and the verify check fails until someone moves it. Nothing written locally is dropped.

### Kit pages

A kit page covers a system the wiki has no page for. It uses the same file name pattern (no prefix: the marker below and the capture line identify it), has `<!-- kit:page -->` on the line after its capture line (`*Kit page: written by the Agentic HOI4 Modding Kit ...*`), and keeps the review block and the `---` furniture of a wiki page. The sync never fetches a kit page. It refreshes the page's table of contents and navigation footer, and lists every kit page in the navigation footer of all pages. If the wiki later gains a page with the same title, the sync says so; move the kit text into kit blocks on the wiki page then.

### Review block and evidence

Every page has exactly one `review` block at `top`. Its marker records:

| Attribute | Meaning |
| --- | --- |
| `build` | the game build the page was checked against, for example `1.19.3.0`, or `none` |
| `checked` | the date of that check |
| `revision` | the wiki revision that was reviewed (wiki pages only) |
| `sources` | the game files the page was checked against, space separated; a folder ends in `/` (`common/raids/`) |
| `via` | `docs-diff` when `--carry-forward` moved the page to a new build without a full re-read |

Its text says what was checked, what the kit changed, and the gaps that remain. The sync adds a placeholder review (`build="none"`) to a page that has none.

Every factual statement in a kit block carries one evidence tag:

| Tag | Use it when |
| --- | --- |
| `[game-tested 1.19.3]` | the behaviour was observed in the running game; say how |
| `[vanilla-confirmed 1.19.3]` | the installed vanilla script shows it; give the file and, where useful, a count ("21 of 21 impassable states") |
| `[docs]` | the game's own documentation states it (`documentation/*.md` or a `_documentation.md` under `common/`) for the build in the review block |
| `[unverified]` | it is plausible but neither the game files nor a test confirm it |

Write in your own words. Quote only identifiers, values and short examples from the game files or vanilla script, and never write game data from memory: look up every token, scope, default and number. Name the game file a statement comes from. Keep examples short and in vanilla style.

## Refresh workflow

Refreshing the snapshot is its own task. Do it when the wiki has moved, when a game update lands, or before a release.

```powershell
python -B .tools/wiki/sync_wiki_snapshot.py
python -B .tools/wiki/verify_wiki_snapshot.py
python -B .tools/wiki/wiki_status.py
```

1. **Sync.** The run ends with a summary: pages whose wiki revision changed, kit blocks whose heading disappeared upstream, wiki modding pages the snapshot lacks (add them to `NEW_PAGES`), and kit pages the wiki now also has.
2. **Verify.** Fix every finding. A misplaced kit block usually means its heading was renamed upstream; point `at` at the new anchor.
3. **Status.** `wiki_status.py` groups the pages: current, wiki text changed since the review, reviewed on an older build, not reviewed. It also lists game documentation files that no page names as a source, which are coverage gaps.
4. **Re-check.** For each flagged page, read the new wiki text next to its kit blocks. Delete kit text the wiki now covers correctly, update the rest, and refresh the review text.
5. **Record.** `python -B .tools/wiki/wiki_status.py --mark-reviewed "Page" ...` writes the installed build, today's date and the current wiki revision into each page's review marker.
6. Run the verify check again and commit the snapshot and tools together.

### After a game update

`game_docs_index.json` records, for the build the snapshot was last checked against, every heading of the game's documentation (`documentation/*.md`, the `_documentation.md` files under `common/`, and the equipment designer's `_documentation.info`) with a short hash of its text. After the game updates:

1. Run `python -B .tools/wiki/wiki_status.py`. It prints the entries added, removed or changed in each documentation file since the recorded build, and the pages to re-check: pages that name a changed file in `sources`, and pages that mention a removed or changed effect, trigger, modifier or other entry.
2. Re-check those pages as above, adding new effects, triggers and modifiers to the pages that list them, and record each review with `--mark-reviewed`.
3. `python -B .tools/wiki/wiki_status.py --carry-forward` moves every page that was current on the previous build, and that the diff did not flag, to the new build with `via="docs-diff"`. That records a mechanical check, not a re-read; a later full review removes `via`.
4. `python -B .tools/wiki/wiki_status.py --record` stores the new build's index. Commit it with the pages.

`--strict` makes the status tool exit 1 unless every page is current.

## Sync details

For each wiki page the sync fetches the rendered article through the wiki's MediaWiki parse API, not the page skin, so maintenance banners, edit links and footer boxes never reach the Markdown. The HTML is converted with:

- real code fences, so multi-line examples stay inside code blocks and headings stay headings;
- multi-line code samples hoisted out of table cells. A Markdown table row is one line, so a preformatted block cannot live in a cell. The cell keeps an `*(example below)*` pointer, and the sample becomes a fenced block labelled `**Example: <row name>**` directly after its table. Single-line samples stay inline;
- rectangular tables: nested tables become lists, `colspan` is expanded, ragged rows are padded or merged, and all-empty trailing columns are dropped;
- LaTeX math kept as inline text instead of the wiki's formula images;
- section anchors after each heading, so links within the snapshot resolve while the heading still reads cleanly;
- the wiki's `Modding navbox` restored as a local navigation list, with a line for the kit pages;
- no outbound hyperlinks. A wiki link resolves to a snapshot file when that page is in the snapshot and is reduced to its text otherwise.

Existing `media/` files are reused by matching image alt text, so a refresh downloads only new images. A run that cannot read a page's kit blocks back fails for that page and leaves the file untouched.

| Option | Effect |
| --- | --- |
| `--only PAGE [PAGE ...]` | refresh only the named wiki pages |
| `--new-only` | build only the pages listed in `NEW_PAGES` that have no file yet |
| `--dry-run --out DIR` | convert into `DIR` without touching `paradox_wiki/` (kit blocks are still merged) |
| `--cache [DIR]` | reuse cached API responses (default `.tmp/wiki_cache`); omit to always fetch live |
| `--prune-media` | after writing, delete media files no page references |

A normal run fetches the live wiki, so a stale snapshot cannot be written by accident. Use `--cache` only while working on the converter.

### Scope and file names

The snapshot covers the wiki's `Category:Modding` members and the pages in `Template:Modding navbox`; a full sync reports category members it lacks. Add a new wiki modding page to `NEW_PAGES` and refresh. Pages the wiki redirects elsewhere need no file: `REDIRECT_ANCHORS` maps them so links land on the target page and section.

#### File name scheme

A page's file is its title in lowercase kebab-case plus `.md`: lowercase every letter, turn each run of other characters into one hyphen, and trim the ends. The title is the page's level-1 heading.

| Title | File |
| --- | --- |
| `Defines` | `defines.md` |
| `AI focuses` | `ai-focuses.md` |
| `Scripted GUI modding` | `scripted-gui-modding.md` |
| `Military industrial organization modding` | `military-industrial-organization-modding.md` |

- File names have no spaces, capitals or site name, so they are easy to type, glob and pass between tools. `kit_blocks.file_name(title)` is the one definition; the sync, verify and status tools all use it, and the verify check fails a page whose file is not named after its heading.
- Tools read the title from the heading and never parse it out of the file name.
- Kit pages follow the same pattern. The `<!-- kit:page -->` marker and the "written by the kit" capture line identify them; no tool needs a prefix.
- Media files are `<page-slug>_<url hash>__img<n>.<ext>`, lowercase without spaces, named for the page that first showed the image. The sync reuses a file by its image alt text, so a refresh keeps existing media names.
- Links between pages are written `[text](<file-name.md#anchor>)` and must match the file name letter for letter, so they also resolve on case-sensitive file systems.
- `Effects` keeps its historical title, `Effects`, although the wiki page is `Effect`, so its file is `effects.md`. `FILENAME_OVERRIDES` holds the mapping.
- Keep file names and heading anchors stable; skills and instructions link to them.
- Earlier copies of the snapshot named files `<Page Title> - Hearts of Iron 4 Wiki.md`. The sync refuses to run while any such file is present, because it would write the new files beside them. Replace the whole `paradox_wiki/` folder with the kit's current one instead.

## Verify details

```powershell
python -B .tools/wiki/verify_wiki_snapshot.py
python -B .tools/wiki/verify_wiki_snapshot.py .tmp/wiki-preview
python -B .tools/wiki/verify_wiki_snapshot.py --quiet
```

It reports unbalanced or table-breaking code fences, outbound hyperlinks, page or media file names that break the naming scheme, links to missing files (the link's capitalisation must match the file name), section links whose anchor is absent, images with no file, image files nothing references, table rows whose column count differs from their header, pages without exactly one level-1 heading, `:` definition-list lines, a multi-line code sample flattened into one code span of 300 characters or more, code indented four spaces or more inside a table cell, encoding damage (byte order marks, non-breaking or zero-width characters, mojibake), kit blocks that are unpaired, misplaced, unlabelled or point at a missing heading, snapshot pages without a review block, and a missing `LICENSE.txt`.

It also prints the number of table rows over 400 characters. That is a report, not a failure. Valid Markdown backslash escapes are accepted. Every reported finding is a defect.

## Dependencies

The sync needs Python 3.9 or newer with `requests`, `beautifulsoup4` and `markdownify`, and fails fast with the install command when one is missing:

```powershell
python -m pip install requests beautifulsoup4 markdownify
```

The verify and status tools use only the standard library. The status tool finds the game through `HOI4_GAME_DIR`, `.tools/local_settings.json` or the Steam libraries (`.tools/lib/game.py`) and exits 2 when it cannot. `scripts/test_wiki_validation.py` holds the regression tests for the verify check and the kit-block format.

## Caches and generated files

`--cache` writes under `.tmp/wiki_cache/`, which the repository `.gitignore` excludes. The sync writes nothing else outside `paradox_wiki/`. The status tool writes only with `--mark-reviewed`, `--carry-forward` (review markers) and `--record` (`game_docs_index.json`).

## License

The wiki's text is CC BY-SA 3.0 (see `paradox_wiki/LICENSE.txt`), and the kit's additions to it are distributed under the same license. Every capture line carries the attribution. The package's Apache-2.0 license does not apply to the snapshot.

## Copies in other repositories

- **HOI4 Mod Setup** installs the snapshot as the `wiki.snapshot` component of `hoi4-mod-setup.manifest.json`. The manifest workflow on `main` regenerates its file evidence after a merge; for a local release, run `scripts/generate_manifest_evidence.py --revision <commit>` as `RELEASING.md` describes.
- **Mods with their own copy**, such as Chaos Redux, should replace their `paradox_wiki/` with this one rather than editing it. Replace the whole folder: every file name changed with the move to kebab-case names, so copying over an old snapshot would leave both sets of files. Generic corrections belong in kit blocks here; mod-specific notes belong in the mod's own docs. Copy `kit_blocks.py`, `wiki_status.py` and `game_docs_index.json` with the updated sync and verify tools when the mod refreshes the snapshot itself.
