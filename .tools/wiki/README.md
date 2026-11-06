# HOI4 wiki tooling

`hoi4_wiki/` is the kit's own HOI4 wiki, an offline Hearts of Iron IV modding reference for agents. Earlier kit versions named it `paradox_wiki/`. It holds one Markdown file per page, named after the page title in lowercase snake_case (`scripted_gui_modding.md`), `media/` with every image those pages show, `LICENSE.txt` and `SOURCES.json`. Most pages are captured from the Hearts of Iron IV Wiki's modding pages (Category:Modding). The kit corrects and extends them against the installed game, and adds kit pages for systems the wiki does not cover. The project instructions point every implementation task at it, so it has to stay current, self-contained and lean: an agent that reads a page should spend its context on modding knowledge only.

These tools maintain it. None of them launches Hearts of Iron IV.

| Tool | Job |
| --- | --- |
| `sync_wiki_snapshot.py` | re-imports the wiki pages from the live wiki and puts the kit text back |
| `render_wiki.py` | rebuilds pages from the kit sidecars after an edit, without fetching anything |
| `verify_wiki_snapshot.py` | read-only acceptance check for the whole wiki |
| `wiki_status.py` | says which pages are current for the installed game build and which to re-check after an update |
| `kit_blocks.py` | the page, sidecar and manifest format the tools share (no command line) |
| `lean.py` | turns annotated kit text into the lean text of a page (no command line) |
| `steam_depots.py` | lists the game files that changed between two Steam builds, for `wiki_status.py` (no command line) |
| `kit/` | the sidecars: the kit's text and review for each page, with its evidence |
| `manifest.json` | generated: where each page came from and where its kit text sits (never edit it) |
| `game_docs_index.json` | the game documentation index and Steam depot manifest ids for the build the snapshot was last checked against |

## What agents read

A page in `hoi4_wiki/` is a title and its content:

```text
# AI focuses

AI focuses balance competing interests ...

## Focus Types

Names of the nine AI focuses as the game files spell them. ...
```

It has no capture line, table of contents, navigation footer, HTML comments, `<a id>` anchors, review notes, evidence tags or "Kit note" labels. The verify check fails on any of them. Kit text sits in place as plain text, so a correction says what is true in its own words ("The first bullet above misspells the key. It is `initial_value`."). `[unverified]` stays as the word "unverified", because an agent needs to know what is not confirmed. Links between pages are `[text](file.md#slug)`, where the slug is the GitHub-style id of the target heading (`## Focus Types` is `focus-types`, a repeated heading gets `-1`, `-2`).

Attribution for the CC BY-SA 3.0 text is in `hoi4_wiki/LICENSE.txt` and `hoi4_wiki/SOURCES.json`, not on the pages. `SOURCES.json` lists every page's file, its wiki page, URL, revision and capture date, and says that the kit's text is under the same license. HOI4 Agent Tools never indexes either file.

## Where the kit text lives

Never edit kit text in `hoi4_wiki/`. Each page has a sidecar, `.tools/wiki/kit/<page>.md`, and the page is built from it.

For a wiki page the sidecar holds the review and the kit blocks:

```text
# AI focuses

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="34354" sources="common/ai_focuses/ ..." -->
What was checked, what the kit changed, and the gaps that remain.
<!-- kit:end id="review" -->

<!-- kit:begin id="ai-focus-ids-1193" at="section:focus-types" -->
Names of the nine AI focuses as the game files spell them. ... [vanilla-confirmed 1.19.3] `common/ai_focuses/generic.txt`
<!-- kit:end id="ai-focus-ids-1193" -->
```

A kit page's sidecar has `<!-- kit:page -->` under its title, then its review block, then its whole text. The sync never fetches a kit page. If the wiki later gains a page with the same title, the sync says so; move the kit text into kit blocks of the wiki page then. `Defines additions` is a kit page that holds the kit's define tables, so the wiki's Defines page stays an unchanged snapshot.

After editing a sidecar, run `python -B .tools/wiki/render_wiki.py` and commit the sidecar, the page, `manifest.json` and `SOURCES.json` together.

### Kit blocks

- `id`: lowercase letters, digits and hyphens, unique in the sidecar.
- `at` says where the block goes on the page:
  - `top`: under the title, before the wiki text;
  - `bottom`: at the end of the page;
  - `section:<slug>`: at the end of that section's own text, before the next heading;
  - `heading:<slug>`: directly under the heading, before the wiki text (use it for warnings about outdated text).

  `<slug>` is the GitHub-style id of a heading of the wiki text (not of a heading inside a kit block). Blocks that share a place keep their sidecar order.
- Write the block as the plain text a modder should read, in your own words. No "Kit note" labels, no "the kit" self-references. A heading inside a block is an ordinary heading (`### Raid categories`) and must not repeat a heading of the wiki text.
- Never put a block inside a code fence or a table, nest blocks, or edit the markers by hand except for `at` and the review attributes.

When the wiki later removes the heading a block points at, the sync and the rebuild keep the block at the bottom of the page and say so, and the verify check fails until someone points `at` at the new heading. Nothing written locally is dropped.

### Evidence

Every factual statement in kit text carries one evidence tag in the sidecar. The page shows the statement without it.

| Tag | Use it when |
| --- | --- |
| `[game-tested 1.19.3]` | the behaviour was observed in the running game; say how |
| `[vanilla-confirmed 1.19.3]` | the installed vanilla script shows it; give the file and, where useful, a count ("21 of 21 impassable states") |
| `[docs]` | the game's own documentation states it (`documentation/*.md` or a `_documentation.md` under `common/`) for the build in the review block |
| `[unverified]` | it is plausible but neither the game files nor a test confirm it |

Write a tag exactly as shown, with only the build inside the brackets, and name files outside them. Put the tag and its citation **after** the statement it supports: a tag starts a citation that runs to the end of its sentence, table cell, parenthesis or line, and `lean.py` removes both. A short lead-in such as `All rows:` or `Counts are` directly in front of the tag goes with it. A capitalised sentence right after a tag is treated as a new statement and kept. `[unverified]` is not removed: it becomes "unverified" or "(unverified)", and it ends a citation before it, so the hedged clause stays. The verify check reports a tag whose removal would leave a dangling `:`, stray punctuation or a sentence cut short ("file lists are."). Fix those in the sidecar.

When only a game run can settle an `[unverified]` claim, list it in the "In-game checks" section of the current coverage record (`coverage-1.19.3.md`), with its setup, exact steps and expected result, for HOI4 Live Tools or the maintainer. Agents never start the game themselves. When a check is run, retag the claim, correct it if the result differs, and remove its entry from the list.

Write in your own words. Quote only identifiers, values and short examples from the game files or vanilla script, and never write game data from memory: look up every token, scope, default and number. Name the game file a statement comes from in its citation. Keep examples short and in vanilla style.

### Review block

Every sidecar has exactly one `review` block. Its marker records:

| Attribute | Meaning |
| --- | --- |
| `build` | the game build the page was checked against, for example `1.19.3.0`, or `none` |
| `checked` | the date of that check |
| `revision` | the wiki revision that was reviewed (wiki pages only) |
| `sources` | the game files the page was checked against, space separated; a folder ends in `/` (`common/raids/`) |
| `via` | `docs-diff` when `--carry-forward` moved the page to a new build without a full re-read |

Its text says what was checked, what the kit changed, and the gaps that remain. It never reaches the page, so a correction that matters to a modder must also be stated in a kit block. The sync gives a page without a sidecar one with a placeholder review (`build="none"`).

### Manifest

`manifest.json` is written by `render_wiki.py`, the sync and nothing else. For each page it records the source (`wiki` or `kit`), the wiki page, revision and capture date, the SHA-256 of the page's wiki text, the wiki's heading ids mapped to slugs (`anchors`, so re-imported links land on the right heading) and the first and last line each kit block fills (`blocks`). `render_wiki.py` takes the wiki text back out of a page by removing those lines and checks it against the hash, so a hand edit to a page is caught instead of being lost on the next rebuild.

## Refresh workflow

Refreshing the snapshot is its own task. Do it when the wiki has moved, when a game update lands, or before a release.

```powershell
python -B .tools/wiki/sync_wiki_snapshot.py
python -B .tools/wiki/verify_wiki_snapshot.py
python -B .tools/wiki/wiki_status.py
```

1. **Sync.** The run ends with a summary: pages whose wiki revision changed, kit blocks whose heading disappeared upstream, wiki modding pages the snapshot lacks (add them to `NEW_PAGES`), and kit pages the wiki now also has.
2. **Verify.** Fix every finding. A kit block at the bottom usually means its heading was renamed upstream; point `at` at the new slug and run `render_wiki.py`.
3. **Status.** `wiki_status.py` groups the pages: current, wiki text changed since the review, reviewed on an older build, not reviewed. It also lists game documentation files that no page names as a source, which are coverage gaps.
4. **Re-check.** For each flagged page, read the new wiki text in `hoi4_wiki/` next to the kit blocks in its sidecar. Delete kit text the wiki now covers correctly, update the rest, refresh the review text, and run `render_wiki.py`.
5. **Record.** `python -B .tools/wiki/wiki_status.py --mark-reviewed "Page" ...` writes the installed build, today's date and the page's current wiki revision into each sidecar's review marker.
6. Run the verify check again and commit the pages, sidecars, manifest and tools together.

### After a game update

`game_docs_index.json` records, for the build the snapshot was last checked against, every heading of the game's documentation (`documentation/*.md`, the `_documentation.md` files under `common/`, and the equipment designer's `_documentation.info`) with a short hash of its text. After the game updates:

1. Run `python -B .tools/wiki/wiki_status.py`. It prints the entries added, removed or changed in each documentation file since the recorded build, and the pages to re-check: pages whose review names a changed file in `sources`, and pages (wiki text or kit text) that mention a removed or changed effect, trigger, modifier or other entry.
   The index also records the Steam depot manifest ids of its build (`depots`). When the old manifests are still in Steam's `depotcache/` folder, the tool also counts the game files added, removed or changed by folder and flags every page whose `sources` cover a changed script, define or interface file. Most of an update is in those files, not in the documentation: 1.19.4.1 changed two documentation files but 1,511 game files, including both define files. Steam keeps an old manifest only for a while, so run the status soon after an update; a depot without both manifests is reported as not compared.
2. Re-check those pages as above, adding new effects, triggers and modifiers to the pages that list them, and record each review with `--mark-reviewed`. For each tagged statement in the sidecar, find the game files it depends on (the files its citation names, or for a count every folder it scans). A statement whose files did not change keeps its tag; re-measure the others on the new build and retag them `[vanilla-confirmed <new build>]`. Re-check skills' tagged statements the same way. For defines, rebuild the old define set from the Defines page tables plus the `defines_additions.md` tables and compare it with the new files name by name and value by value.
3. `python -B .tools/wiki/wiki_status.py --carry-forward` moves every page that was current on the previous build, and that the diff did not flag, to the new build with `via="docs-diff"`. That records a mechanical check, not a re-read; a later full review removes `via`.
4. `python -B .tools/wiki/wiki_status.py --record` stores the new build's index. Commit it with the sidecars.

`--strict` makes the status tool exit 1 unless every page is current.

## Sync details

For each wiki page the sync fetches the rendered article through the wiki's MediaWiki parse API, not the page skin, so maintenance banners, edit links and footer boxes never reach the Markdown. The HTML is converted with:

- real code fences, so multi-line examples stay inside code blocks and headings stay headings;
- multi-line code samples hoisted out of table cells. A Markdown table row is one line, so a preformatted block cannot live in a cell. The cell keeps an `*(example below)*` pointer, and the sample becomes a fenced block labelled `**Example: <row name>**` directly after its table. Single-line samples stay inline;
- rectangular tables: nested tables become lists, `colspan` is expanded, ragged rows are padded or merged, and all-empty trailing columns are dropped;
- LaTeX math kept as inline text instead of the wiki's formula images;
- no navigation boxes, reference backlink arrows or heading anchors on the page;
- no outbound hyperlinks. A wiki link resolves to a snapshot file when that page is in the snapshot and is reduced to its text otherwise. A link to a section points at the slug of the target heading, and a section the target no longer has is dropped from the link.

The sync then turns the converted page into lean wiki text (`lean.lean_wiki_text`), puts each kit block of the sidecar back at its `at` place, writes the page and records it in `manifest.json`. The capture date in the manifest moves only when the wiki text changed. Kit pages and `SOURCES.json` are rebuilt at the end of the run.

Existing `media/` files are reused by matching image alt text, so a refresh downloads only new images. A page whose kit blocks cannot be placed fails and is left untouched.

| Option | Effect |
| --- | --- |
| `--only PAGE [PAGE ...]` | refresh only the named wiki pages |
| `--new-only` | build only the pages listed in `NEW_PAGES` that have no file yet |
| `--dry-run --out DIR` | convert into `DIR` (pages, `manifest.json`, `SOURCES.json`) without touching `hoi4_wiki/`, the manifest or the sidecars |
| `--cache [DIR]` | reuse cached API responses (default `.tmp/wiki_cache`); omit to always fetch live |
| `--prune-media` | after writing, delete media files no page references |

A normal run fetches the live wiki, so a stale snapshot cannot be written by accident. Use `--cache` only while working on the converter.

### Scope and file names

The snapshot covers the wiki's `Category:Modding` members and the pages in `Template:Modding navbox`; a full sync reports category members it lacks. Add a new wiki modding page to `NEW_PAGES` and refresh. Pages the wiki redirects elsewhere need no file: `REDIRECT_ANCHORS` maps them so links land on the target page and section.

#### File name scheme

A page's file is its title in lowercase snake_case plus `.md`: lowercase every letter, turn each run of other characters into one underscore, and trim the ends. The title is the page's level-1 heading.

| Title | File |
| --- | --- |
| `Defines` | `defines.md` |
| `AI focuses` | `ai_focuses.md` |
| `Scripted GUI modding` | `scripted_gui_modding.md` |
| `Military industrial organization modding` | `military_industrial_organization_modding.md` |

- File names have no spaces, capitals or site name, so they are easy to type, glob and pass between tools. `kit_blocks.file_name(title)` is the one definition; every tool uses it, and the verify check fails a page whose file is not named after its heading. A page's sidecar has the same file name.
- The kit's tools read the title from the heading and never parse it out of the file name.
- **Why underscores.** HOI4 Agent Tools (`hoi4.reference_context`, `hoi4.reference_search`) derives a wiki page's title from its file name: it strips `.md` and turns each `_` into a space, then looks up the pages it needs ("Event modding", "Data structures", "Console commands") by title without regard to case. `event_modding.md` is therefore the page "Event modding". A hyphen would not be read as a space, so the required pages would be reported as `missing` and the console commands page would lose its console-only ranking. Keep `_` between words.
- That reading only recovers titles made of letters, digits and single spaces. A title with punctuation would be read back differently, and the verify check reports it (`agent_title`).
- Media files are `<page-slug>_<url hash>__img<n>.<ext>`, lowercase without spaces, named for the page that first showed the image. The sync reuses a file by its image alt text, so a refresh keeps existing media names.
- Links between pages are written `[text](file-name.md#slug)` and must match the file name letter for letter, so they also resolve on case-sensitive file systems.
- `Effects` keeps its historical title, `Effects`, although the wiki page is `Effect`, so its file is `effects.md`. `FILENAME_OVERRIDES` holds the mapping.
- Keep file names stable; skills and instructions link to them.
- Earlier copies of the snapshot named files `<Page Title> - Hearts of Iron 4 Wiki.md`. The sync refuses to run while any such file is present, because it would write the new files beside them. Replace the whole `hoi4_wiki/` folder with the kit's current one instead.

## Verify details

```powershell
python -B .tools/wiki/verify_wiki_snapshot.py
python -B .tools/wiki/verify_wiki_snapshot.py .tmp/wiki-preview
python -B .tools/wiki/verify_wiki_snapshot.py --quiet
```

It reports maintenance text on a page (HTML comments, anchors, evidence tags, kit labels, capture lines, tables of contents and navigation footers), unbalanced or table-breaking code fences, outbound hyperlinks, page or media file names that break the naming scheme, links to missing files (the link's capitalisation must match the file name), section links whose slug is absent, images with no file, image files nothing references, table rows whose column count differs from their header, pages without exactly one level-1 heading, `:` definition-list lines, a multi-line code sample flattened into one code span of 300 characters or more, code indented four spaces or more inside a table cell, and encoding damage (byte order marks, non-breaking or zero-width characters, mojibake).

With a manifest (the repository's for `hoi4_wiki/`, or `manifest.json` inside a preview folder) it also checks the sidecars: paired markers, one review block, well-formed evidence tags and evidence placement. It rebuilds every page from its sidecar in memory and reports a page that differs (run `render_wiki.py`), a page whose wiki text no longer matches the recorded hash (a hand edit), a kit block whose heading is gone, a page without a sidecar or manifest entry, a stale `SOURCES.json` and a missing `LICENSE.txt`.

It also prints the number of table rows over 400 characters. That is a report, not a failure. Valid Markdown backslash escapes are accepted. Every reported finding is a defect.

## Dependencies

The sync needs Python 3.9 or newer with `requests`, `beautifulsoup4` and `markdownify`, and fails fast with the install command when one is missing:

```powershell
python -m pip install requests beautifulsoup4 markdownify
```

The other tools use only the standard library. The status tool reads `steamapps/appmanifest_394360.acf` next to the game folder and the manifests in `depotcache/` of the game's Steam library or Steam installation, and works without them. It finds the game through `HOI4_GAME_DIR`, `.tools/local_settings.json` or the Steam libraries (`.tools/lib/game.py`) and exits 2 when it cannot. `scripts/test_wiki_validation.py` holds the regression tests for the lean format, the sidecars, the rebuild, the sync's page flow and the verify check.

## Caches and generated files

`--cache` writes under `.tmp/wiki_cache/`, which the repository `.gitignore` excludes. The sync writes nothing else outside `hoi4_wiki/`, `manifest.json` and new sidecars. `render_wiki.py` writes only pages, `manifest.json` and `SOURCES.json`. The status tool writes only sidecar review markers (`--mark-reviewed`, `--carry-forward`) and `game_docs_index.json` (`--record`).

## License

The wiki's text is CC BY-SA 3.0 (see `hoi4_wiki/LICENSE.txt`), and the kit's additions to it are distributed under the same license. `hoi4_wiki/SOURCES.json` lists the source page, revision and capture date of every page. The package's Apache-2.0 license does not apply to the snapshot.

## Copies in other repositories

- **HOI4 Mod Setup** installs the snapshot as the `wiki.snapshot` component of `hoi4-mod-setup.manifest.json`. The sidecars and the manifest stay in the kit; mods do not need them. The manifest workflow on `main` regenerates its file evidence after a merge; for a local release, run `scripts/generate_manifest_evidence.py --revision <commit>` as `RELEASING.md` describes.
- **Mods with their own copy**, such as Chaos Redux, should replace their `hoi4_wiki/` (or the older `paradox_wiki/`) with this one rather than editing it. Replace the whole folder: `git mv paradox_wiki hoi4_wiki` first when the mod still has the old name, so Git keeps the history, then copy this folder over it. Copying over an old snapshot would leave both sets of files. Generic corrections belong in kit blocks here; mod-specific notes belong in the mod's own docs. A mod that refreshes the snapshot itself copies the whole `.tools/wiki/` folder, sidecars and manifest included.
