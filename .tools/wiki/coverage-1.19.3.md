# Wiki snapshot coverage review for HOI4 1.19.3.0

Plan and record of the 2026-10-31 review of `hoi4_wiki/` against Hearts of Iron IV 1.19.3.0 (`Operation Postern v1.19.3.0.c01a (5632)`). Each page's own review block holds its detailed record; this file is the overview. The workflow for later builds is in `README.md`.

## Starting point

- 54 wiki pages, all members of the wiki's `Category:Modding`; the category has no page the snapshot lacked. A full sync on 2026-10-31 brought in the upstream edits made since the 2026-09-19 capture (Effects, Console commands, Localisation, Map modding, National focus modding, Division modding and others).
- No page carried a record of the game build it matched. Several wiki pages were last edited years ago: Posteffect modding (2018), Entity modding (2018), AI focuses (2020), Strategic region modding (2022), Balance of power modding (2023).
- The game ships 52 documentation files: `documentation/*.md` (effects, triggers, modifiers, dynamic variables, localisation objects and formatters, console commands, script concepts, collections, math functions) and about 40 `_documentation.md` files inside `common/` folders.

## Inventory findings

Measured with a scratch script against the installed game (token names compared as whole words):

| Page | Gap found |
| --- | --- |
| Effects | 21 of 553 documented effects never named (loops, scored-country lists, captured generals, `set_leader_*`, `boost_planning`, `add_region_efficiency`, ...) |
| Triggers | 56 of 596 documented triggers never named (collections, temp-variable triggers, `any_of`/`all_of`, captured generals, career profile, nukes, ...) |
| Modifiers | 167 of 722 documented modifiers never named |
| List of modifiers | 252 of 722 documented modifiers never named |
| Data structures | 41 of 375 documented dynamic variables never named (faction influence, nukes, advisor slots, production totals, ...) |
| Console commands | 221 of 430 documented commands never named |
| Doctrine modding | four empty sections (Folders, Grand Doctrines, Tracks, Subdoctrines) although the game documents all four |
| Military industrial organization modding | empty Delta MIO and AI Bonus Weights sections; a TODO |
| Nudger | empty Buildings, Units and References sections |
| Graphical asset, Unit, Equipment, Particle, State, Mods | one or two empty sections each |
| AI modding, Bookmark, Building, Country creation, Defines, Effects, Equipment, Faction, Localisation, Map, Modding, Modifiers, State, Strategic region, Supply areas, Technology, Triggers, Troubleshooting | text marked outdated, obsolete, deprecated, incomplete or "to be added" |
| 28 pages | code examples using keys that appear in neither the game documentation nor vanilla script; each needs a check (many are deliberate placeholders) |

Systems with no page, or only passing mentions (by `common/` folder):

| System | Folders | Plan |
| --- | --- | --- |
| Special projects and scientists | `special_projects/`, `scientist_traits/` | new kit page |
| Raids | `raids/` | new kit page |
| Peace conference rules | `peace_conference/` | new kit page |
| Collections | `collections/`, `documentation/script_collection_*.md` | new kit page |
| Intelligence operations | `operations/`, `operation_phases/`, `operation_tokens/` | new kit page |
| Script constants | `script_constants/` | new kit page |
| Map modes | `map_modes/` | new kit page |
| Game rules | `game_rules/` | new kit page |
| Occupation and resistance | `occupation_laws/`, `resistance_activity/`, `resistance_compliance_modifiers/` | new kit page |
| Intelligence agency upgrades | `intelligence_agency_upgrades/` | kit block on Intelligence agency modding |
| Doctrine system (grand doctrines, tracks, subdoctrines, mastery) | `doctrines/` | kit blocks fill Doctrine modding |
| AI navy, faction theaters, equipment designs, templates | `ai_navy/`, `ai_faction_theaters/`, `ai_equipment/`, `ai_templates/` | kit blocks on AI modding |
| Focus inlay windows, continuous focuses | `focus_inlay_windows/`, `continuous_focus/` | kit blocks on National focus modding |
| Strategic locations | `strategic_locations/` | kit block on State modding |
| Dynamic modifiers, modifier definitions | `dynamic_modifiers/`, `modifier_definitions/` | check the Modifiers sections, add kit blocks |
| Scripted GUI contexts | `scripted_guis/_documentation.md` | kit block on Scripted GUI modding |
| Every other `common/` folder | medals, ribbons, timed activities, synchronized dynamic tokens, ... | folder index kit block on Mod structure |

## Batches

Each batch is one reviewer with explicitly owned files. Reviewers add kit blocks only, never edit wiki text, and return a per-page record. New kit pages are returned as text and saved by the coordinator.

| Batch | Pages |
| --- | --- |
| R1 | Effects |
| R2 | Triggers |
| R3 | Modifiers, List of modifiers |
| R4 | Data structures, Scopes |
| R5 | Console commands, Defines, Troubleshooting |
| R6 | Localisation, On actions, Modding, Mod structure, Mods |
| R7 | Event modding, Decision modding, National focus modding |
| R8 | Idea modding, Character modding, Ideology modding, Cosmetic tag modding |
| R9 | Country creation, State modding, Map modding, Strategic region modding, Supply areas modding, Building modding, Resources modding |
| R10 | Technology modding, Doctrine modding, Equipment modding, Unit modding, Division modding |
| R11 | AI modding, AI focuses, Faction modding, Autonomy state modding, Balance of power modding, Bookmark modding |
| R12 | Military industrial organization modding, Intelligence agency modding, Achievement modding, Scripted GUI modding, Interface modding |
| R13 | Graphical asset modding, Entity modding, Particle modding, Posteffect modding, Font modding, Portrait modding, Namelist modding, Music modding, Sound modding, Nudger |
| N1 | Special project modding, Raid modding |
| N2 | Peace conference modding, Collection modding, Script constant modding |
| N3 | Intelligence operation modding, Map mode modding, Game rule modding, Occupation and resistance modding |

## Rules for reviewers

- The README's page format and evidence tags apply. Every statement in a kit block carries `[game-tested 1.19.3]`, `[vanilla-confirmed 1.19.3]`, `[docs]` or `[unverified]`. Nobody launched the game for this review, so no block claims `[game-tested 1.19.3]`.
- Sources: the installed game's documentation files and vanilla `common/`, `events/`, `history/`, `interface/`, read-only. Confirmed findings from the Hagane Works skills repository (used with its author's permission) were re-checked against 1.19.3 and rewritten; its contradicted claims are excluded.
- Wiki text that is wrong for 1.19.3 gets a `heading:` warning or a `section:` correction; the wiki text itself is never edited.
- Large token lists (missing effects, modifiers, commands) are tables of facts: name, scope or category, and a one-line description in our words, never pasted documentation.

## Results

All 16 batches were merged on 2026-10-31. `wiki_status.py` reports 63 of 63 pages current for 1.19.3.0, the verify check reports no findings, and wiki text outside kit blocks is unchanged on every page. Each page's review block holds its own record: what was checked, what the kit added or corrected, and the gaps left.

- 54 wiki pages carry 563 kit blocks. 9 kit pages were added: Special project, Raid, Peace conference, Collection, Script constant, Intelligence operation, Map mode, Game rule, and Occupation and resistance modding.
- After the review, the Defines page's 26 kit blocks of new-define tables (101 KB) moved to a tenth kit page, Defines additions, so the Defines page keeps its wiki text and a review block only. The Defines row below counts the blocks as written.
- About 1.4 MB of kit text. Evidence tags: 1,609 `[vanilla-confirmed 1.19.3]`, 897 `[docs]`, 536 `[unverified]`, no `[game-tested 1.19.3]` (nobody ran the game).
- Every documented effect, trigger, modifier, dynamic variable and console command is now named on its reference page. Every game documentation file is cited by at least one page's `sources`.
- Every empty section the inventory found is filled, and every stub marker was checked. Most were ordinary prose. The real ones are now covered by kit blocks.
- The coordinator spot-checked about forty of the reviewers' headline claims against the game files before each merge. All held, and one count was corrected (21 impassable states, not 22: one file has the line commented out).

| Page | Kit blocks | Kit text (KB) | vanilla-confirmed / docs / unverified |
| --- | --- | --- | --- |
| Achievement modding | 4 | 8 | 10 / 9 / 8 |
| AI focuses | 3 | 5 | 5 / 3 / 3 |
| AI modding | 16 | 33 | 34 / 34 / 11 |
| Autonomy state modding | 4 | 9 | 7 / 2 / 4 |
| Balance of power modding | 6 | 8 | 10 / 5 / 5 |
| Bookmark modding | 6 | 10 | 13 / 1 / 7 |
| Building modding | 12 | 23 | 27 / 5 / 5 |
| Character modding | 15 | 31 | 29 / 17 / 14 |
| Collection modding | kit page | 34 | 39 / 46 / 14 |
| Console commands | 15 | 39 | 3 / 21 / 35 |
| Cosmetic tag modding | 5 | 7 | 6 / 3 / 3 |
| Country creation | 7 | 13 | 19 / 9 / 3 |
| Data structures | 16 | 30 | 32 / 38 / 10 |
| Decision modding | 12 | 19 | 25 / 10 / 11 |
| Defines | 26 | 101 | 89 / 1 / 13 |
| Division modding | 13 | 19 | 21 / 3 / 7 |
| Doctrine modding | 11 | 34 | 32 / 27 / 4 |
| Effects | 34 | 38 | 55 / 58 / 16 |
| Entity modding | 9 | 10 | 24 / 1 / 2 |
| Equipment modding | 9 | 18 | 19 / 6 / 7 |
| Event modding | 11 | 15 | 23 / 7 / 11 |
| Faction modding | 15 | 25 | 26 / 23 / 2 |
| Font modding | 4 | 6 | 17 / 0 / 1 |
| Game rule modding | kit page | 21 | 33 / 3 / 9 |
| Graphical asset modding | 9 | 14 | 31 / 0 / 5 |
| Idea modding | 11 | 16 | 20 / 4 / 7 |
| Ideology modding | 8 | 12 | 10 / 4 / 5 |
| Intelligence agency modding | 3 | 16 | 28 / 21 / 9 |
| Intelligence operation modding | kit page | 42 | 60 / 40 / 18 |
| Interface modding | 16 | 20 | 26 / 1 / 10 |
| List of modifiers | 3 | 39 | 8 / 12 / 4 |
| Localisation | 12 | 17 | 19 / 12 / 7 |
| Map modding | 19 | 22 | 33 / 1 / 10 |
| Map mode modding | kit page | 18 | 9 / 20 / 12 |
| Military industrial organization modding | 11 | 37 | 48 / 42 / 7 |
| Mod structure | 5 | 21 | 11 / 1 / 5 |
| Modding | 6 | 8 | 12 / 1 / 12 |
| Modifiers | 36 | 50 | 47 / 43 / 7 |
| Mods | 1 | 1 | 2 / 0 / 1 |
| Music modding | 4 | 5 | 10 / 1 / 3 |
| Namelist modding | 6 | 11 | 23 / 2 / 2 |
| National focus modding | 16 | 22 | 36 / 14 / 14 |
| Nudger | 6 | 10 | 16 / 1 / 10 |
| Occupation and resistance modding | kit page | 39 | 53 / 20 / 7 |
| On actions | 15 | 17 | 33 / 12 / 12 |
| Particle modding | 5 | 9 | 16 / 0 / 4 |
| Peace conference modding | kit page | 49 | 68 / 41 / 18 |
| Portrait modding | 3 | 6 | 8 / 2 / 4 |
| Posteffect modding | 4 | 6 | 11 / 1 / 5 |
| Raid modding | kit page | 54 | 68 / 40 / 25 |
| Resources modding | 6 | 7 | 9 / 2 / 0 |
| Scopes | 10 | 14 | 14 / 21 / 5 |
| Script constant modding | kit page | 26 | 30 / 38 / 13 |
| Scripted GUI modding | 13 | 15 | 20 / 22 / 9 |
| Sound modding | 7 | 9 | 22 / 1 / 1 |
| Special project modding | kit page | 63 | 79 / 56 / 20 |
| State modding | 11 | 15 | 23 / 8 / 5 |
| Strategic region modding | 3 | 5 | 7 / 1 / 2 |
| Supply areas modding | 2 | 4 | 5 / 1 / 2 |
| Technology modding | 11 | 17 | 18 / 2 / 6 |
| Triggers | 30 | 48 | 57 / 63 / 12 |
| Troubleshooting | 9 | 20 | 6 / 14 / 27 |
| Unit modding | 9 | 14 | 15 / 0 / 6 |

### Gaps left for later work

- Nothing is `[game-tested 1.19.3]`. The `[unverified]` statements are the candidates for in-game checks, above all the documentation conflicts listed on the kit pages (the `collection_size` comparison rule, the peace `ai_desire` scale, special project reward thresholds, the scope inside raid `target_type` state filters). These four, and MIO `task_capacity` with its switch off, now carry a **Needs a game run** note on the page that makes the claim. The run of 2026-11-02 answered all five, and the notes are gone.
- Version-added columns in the wiki's effect, trigger and modifier tables were not re-checked.
- Engine behaviour that no game file states, such as defines the engine still reads and the order of on_action effects, stays `[unverified]`.

## Evidence re-check on 1.19.4.1 (2026-11-01)

This section was added after the 1.19.3 review. The record above stays as it was. On 2026-11-01 every `[unverified]` statement in the 64 pages and the skills was re-checked against the installed 1.19.4.1 files (`Operation Postern v1.19.4.1.99a5 (f584)`), read-only: `documentation/`, vanilla `common/`, `events/`, `history/`, `interface/`, `gfx/`, `map/` and `localisation/`. Nobody started the game.

### Method

- An inventory script listed every `[unverified]` tag in kit text: 576 tags on 568 lines, 561 in 56 pages and 15 in 10 skill files.
- Ten reviewers each took a set of pages and decided, tag by tag: settled by vanilla or the documentation (retagged), contradicted (corrected and retagged), partly settled (split: the settled part retagged, the rest kept `[unverified]`), engine-only (kept, with an in-game check below), or not checkable at all (kept, with the reason).
- A string found only in hoi4.exe settles nothing. Such claims stay `[unverified]`.
- The coordinator re-ran the counts behind several corrections (`fallback_name` 1,137 and 555 lines, `start_manpower_factor` in 38 files and no `history/units` block, 11 `assume_not_played_if_missing_data` entries, `set_politics` renames in 24 event, 14 focus and 11 scripted effect blocks). Wiki text outside kit blocks is unchanged on every page, and every block keeps its id and place.

### Results

- Outcomes for the 576 tags: 38 settled outright (14 vanilla-confirmed, 15 documented, 9 corrected), 201 split, 294 engine-only, 43 not checkable.
- A split keeps an `[unverified]` tag for the part a game run must settle, so the tag total falls less than the outcomes suggest: 576 `[unverified]` tags before, 551 after. The settled parts added 121 `[vanilla-confirmed 1.19.4.1]` and 85 `[docs]` tags on these files.
- The 294 engine-only tags are covered by the 302 in-game checks below, together with the unverified parts of the splits. Some checks cover several claims.
- The 43 not-checkable tags are mostly the tag legend and gap summaries that only name the tag, successor columns of removed defines (inferred from names and values), meanings read from names, advice, and claims that only a string in hoi4.exe supports.
- No tag was retagged `[game-tested ...]` in this review. The run of 2026-11-02 retagged claims `[game-tested 1.19.4.1]` afterwards: 119 of the 302 checks were settled and removed from the list below, and 100 more carry a note on what was settled and what remains, or on why a try was inconclusive.

Corrections, where the files contradicted the old text:

- Division modding: `start_manpower_factor` is used in `create_unit` division strings in 38 files under `common/` and `events/`, though no `history/units` division block writes it.
- Equipment modding: vanilla writes 41 `picture` values, not 35. 37 of them have a `GFX_<picture>_medium` sprite.
- Raid modding: both vanilla `cancel_trigger` blocks are negated flag checks, so the old reading ("cancelled while true") would cancel those raids at once. The direction is now an open question. `air_agility` is a documented modifier used by 21 of 37 raid types, not only an executable string. The first gap now names only the failure and limited-success split.
- Collection modding: the documented input list is not complete. Vanilla also uses `game:all_majors`.
- Effects: `not_tooltip` is documented, for the trigger `custom_override_tooltip` only.
- Decision modding: the `tag` of a category `custom_icon` is a country tag in all 24 vanilla blocks, not a country flag.
- Bookmark modding: `assume_not_played_if_missing_data` is on 11 entries, including two `base_game` ones, not only on newer DLC entries.
- Smaller fixes with new counts: `fallback_name` lines (Namelist modding), missing `.wav` files across two asset files (Sound modding), portrait file names (Portrait modding), duplicate option tokens in `PRC_ai_behavior` too (Game rule modding), `error.log` named by the game's own map error text (Troubleshooting).

Per page, kit text only. Tags are vanilla-confirmed (any build) / docs / unverified. Skill files without an `[unverified]` tag are left out, so the totals here are lower than the whole-kit counts.

| Page | Tags before | Tags after | Settled | Split | Engine-only | Not checkable |
| --- | --- | --- | --- | --- | --- | --- |
| Achievement modding | 10 / 9 / 9 | 12 / 12 / 8 | 2 | 3 | 4 | 0 |
| AI focuses | 5 / 3 / 3 | 5 / 3 / 3 | 0 | 0 | 2 | 1 |
| AI modding | 35 / 34 / 11 | 38 / 36 / 9 | 3 | 2 | 2 | 4 |
| Autonomy state modding | 8 / 2 / 4 | 10 / 2 / 4 | 0 | 2 | 2 | 0 |
| Balance of power modding | 10 / 5 / 5 | 11 / 7 / 5 | 0 | 2 | 3 | 0 |
| Bookmark modding | 13 / 1 / 7 | 15 / 1 / 7 | 1 | 1 | 5 | 0 |
| Building modding | 27 / 5 / 6 | 27 / 6 / 6 | 0 | 1 | 5 | 0 |
| Character modding | 30 / 17 / 15 | 36 / 17 / 15 | 0 | 6 | 8 | 1 |
| Collection modding | 40 / 46 / 16 | 42 / 46 / 14 | 2 | 5 | 8 | 1 |
| Console commands | 3 / 24 / 36 | 3 / 44 / 29 | 9 | 21 | 6 | 0 |
| Cosmetic tag modding | 6 / 3 / 3 | 9 / 3 / 2 | 1 | 2 | 0 | 0 |
| Country creation | 19 / 9 / 3 | 20 / 9 / 3 | 0 | 0 | 3 | 0 |
| Data structures | 32 / 38 / 11 | 34 / 39 / 10 | 1 | 6 | 4 | 0 |
| Decision modding | 25 / 10 / 11 | 27 / 11 / 11 | 1 | 3 | 7 | 0 |
| Defines | 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 | 0 | 0 |
| Defines additions | 95 / 1 / 13 | 95 / 1 / 13 | 0 | 0 | 3 | 10 |
| Division modding | 21 / 3 / 7 | 25 / 4 / 6 | 2 | 3 | 2 | 0 |
| Doctrine modding | 32 / 27 / 4 | 33 / 28 / 4 | 0 | 3 | 1 | 0 |
| Effects | 55 / 58 / 17 | 65 / 64 / 16 | 2 | 12 | 3 | 0 |
| Entity modding | 24 / 1 / 2 | 25 / 1 / 2 | 0 | 1 | 1 | 0 |
| Equipment modding | 19 / 6 / 8 | 19 / 6 / 8 | 1 | 1 | 5 | 1 |
| Event modding | 23 / 7 / 11 | 27 / 7 / 11 | 0 | 4 | 7 | 0 |
| Faction modding | 26 / 23 / 2 | 27 / 24 / 2 | 0 | 2 | 0 | 0 |
| Font modding | 17 / 0 / 1 | 17 / 0 / 1 | 0 | 0 | 1 | 0 |
| Game rule modding | 33 / 3 / 9 | 33 / 4 / 9 | 0 | 0 | 8 | 1 |
| Graphical asset modding | 31 / 0 / 5 | 34 / 0 / 3 | 2 | 2 | 1 | 0 |
| Idea modding | 21 / 4 / 7 | 28 / 5 / 7 | 0 | 7 | 0 | 0 |
| Ideology modding | 10 / 4 / 5 | 12 / 4 / 5 | 0 | 2 | 3 | 0 |
| Intelligence agency modding | 28 / 21 / 9 | 29 / 22 / 8 | 1 | 3 | 5 | 0 |
| Intelligence operation modding | 60 / 40 / 18 | 61 / 44 / 18 | 0 | 5 | 13 | 0 |
| Interface modding | 26 / 1 / 11 | 29 / 1 / 10 | 1 | 9 | 0 | 1 |
| List of modifiers | 9 / 12 / 5 | 11 / 13 / 5 | 0 | 2 | 1 | 2 |
| Localisation | 19 / 12 / 8 | 22 / 13 / 8 | 0 | 4 | 3 | 1 |
| Map modding | 33 / 1 / 11 | 35 / 1 / 11 | 0 | 2 | 8 | 1 |
| Map mode modding | 9 / 20 / 12 | 10 / 24 / 12 | 0 | 4 | 7 | 1 |
| Military industrial organization modding | 48 / 42 / 7 | 52 / 45 / 7 | 0 | 3 | 4 | 0 |
| Mod structure | 11 / 1 / 6 | 12 / 1 / 6 | 0 | 2 | 3 | 1 |
| Modding | 12 / 1 / 13 | 13 / 1 / 13 | 0 | 2 | 9 | 2 |
| Modifiers | 48 / 43 / 8 | 49 / 46 / 8 | 0 | 1 | 5 | 2 |
| Mods | 2 / 0 / 1 | 2 / 0 / 1 | 0 | 0 | 1 | 0 |
| Music modding | 10 / 1 / 3 | 12 / 1 / 3 | 0 | 3 | 0 | 0 |
| Namelist modding | 23 / 2 / 2 | 23 / 2 / 2 | 0 | 2 | 0 | 0 |
| National focus modding | 36 / 14 / 14 | 39 / 15 / 14 | 0 | 3 | 11 | 0 |
| Nudger | 16 / 1 / 11 | 17 / 1 / 10 | 1 | 0 | 10 | 0 |
| Occupation and resistance modding | 53 / 20 / 7 | 54 / 20 / 7 | 0 | 1 | 5 | 1 |
| On actions | 33 / 12 / 13 | 39 / 17 / 13 | 0 | 6 | 7 | 0 |
| Particle modding | 16 / 0 / 4 | 18 / 0 / 4 | 0 | 4 | 0 | 0 |
| Peace conference modding | 69 / 41 / 19 | 69 / 43 / 19 | 0 | 2 | 16 | 1 |
| Portrait modding | 8 / 2 / 4 | 8 / 2 / 4 | 0 | 3 | 1 | 0 |
| Posteffect modding | 11 / 1 / 5 | 12 / 2 / 5 | 0 | 4 | 1 | 0 |
| Raid modding | 69 / 40 / 26 | 75 / 43 / 26 | 3 | 5 | 17 | 1 |
| Resources modding | 9 / 2 / 0 | 9 / 2 / 0 | 0 | 0 | 0 | 0 |
| Scopes | 14 / 21 / 6 | 18 / 23 / 6 | 0 | 6 | 0 | 0 |
| Script constant modding | 30 / 38 / 13 | 31 / 41 / 12 | 2 | 4 | 4 | 3 |
| Scripted GUI modding | 23 / 22 / 8 | 26 / 23 / 8 | 0 | 7 | 1 | 0 |
| Sound modding | 22 / 1 / 1 | 22 / 1 / 1 | 0 | 1 | 0 | 0 |
| Special project modding | 80 / 56 / 21 | 82 / 58 / 20 | 1 | 2 | 16 | 2 |
| State modding | 23 / 8 / 6 | 23 / 8 / 6 | 0 | 1 | 5 | 0 |
| Strategic region modding | 7 / 1 / 3 | 7 / 1 / 3 | 0 | 0 | 3 | 0 |
| Supply areas modding | 5 / 1 / 3 | 5 / 1 / 3 | 0 | 0 | 3 | 0 |
| Technology modding | 18 / 2 / 6 | 18 / 2 / 5 | 1 | 0 | 5 | 0 |
| Triggers | 58 / 63 / 13 | 63 / 68 / 12 | 1 | 10 | 2 | 0 |
| Troubleshooting | 6 / 14 / 27 | 7 / 16 / 27 | 0 | 5 | 21 | 1 |
| Unit modding | 15 / 0 / 6 | 17 / 0 / 6 | 0 | 2 | 3 | 1 |
| skill hoi4-characters-leaders | 3 / 0 / 1 | 3 / 0 / 1 | 0 | 0 | 1 | 0 |
| skill hoi4-decisions-missions | 6 / 1 / 1 | 7 / 1 / 1 | 0 | 1 | 0 | 0 |
| skill hoi4-diplomacy-war/references/intelligence-operations.md | 3 / 1 / 1 | 3 / 1 / 1 | 0 | 0 | 1 | 0 |
| skill hoi4-equipment/references/mios-and-special-projects.md | 7 / 10 / 1 | 8 / 10 / 1 | 0 | 1 | 0 | 0 |
| skill hoi4-feature-planning | 1 / 1 / 2 | 1 / 1 / 2 | 0 | 0 | 0 | 2 |
| skill hoi4-ideas-modifiers | 5 / 8 / 1 | 5 / 8 / 1 | 0 | 0 | 1 | 0 |
| skill hoi4-investigate | 1 / 1 / 6 | 1 / 1 / 6 | 0 | 0 | 5 | 1 |
| skill hoi4-map-states | 13 / 2 / 1 | 13 / 2 / 1 | 0 | 0 | 1 | 0 |
| skill hoi4-scripted-gui | 1 / 2 / 1 | 1 / 2 / 1 | 0 | 0 | 1 | 0 |
| **Total** | 1669 / 926 / 576 | 1790 / 1011 / 551 | 38 | 201 | 294 | 43 |

### Version-added columns

The effect, trigger and modifier tables carry a "Version Added" column from the wiki. They were checked as far as the installed files allow, and each page now has a kit note under its first table (`version-added-column`).

- The kit's recorded documentation index for 1.19.3.0 (commit `bb39e12`) and for 1.19.4.1 have the same entries in all three files: 553 effects, 596 triggers and 764 modifiers. No entry was added or removed by 1.19.4, so no row should say 1.19.4, and none does. The newest values are 1.19 (`unlock_subunit`) on Effects and 1.17.2 on the other two.
- Older values are not checkable from this machine. `changelog.txt` in the game folder only links to the forum. The documentation names no versions. Steam's depot cache holds only the 1.19.3.0 and 1.19.4.1 manifests of the content depots 394361 and 394362 (the many `394360_*` manifests are Workshop items), so `steam_depots.py` can compare only those two builds, and a manifest lists file hashes, not entries.
- Rows with no usable value (blank, `???`, `Unknown`, or other wiki text slipped into the column) are listed in each page's note: 14 on Effects, 18 on Triggers, 8 on Modifiers.

### Overlong table rows

Of the 343 table rows over 400 characters, 16 were in kit text and the other 327 are wiki text, which the kit does not edit. The reviewers' edits brought the kit count to 19. Long explanations in 10 rows moved into notes under their tables, and one row of modifier names became two. 10 kit rows stay over 400 characters. They are token lists (strategy types, ideology rules, hook names, operation ids), and splitting them would break the table. The verify check now counts 337.

### In-game checks

Each check below settles one or more `[unverified]` claims that only a running game can settle. They are written for HOI4 Live Tools or the maintainer. Agents never start the game. Run one by following its setup and steps, compare with the expected result, then retag the claim `[game-tested 1.19.4.1]` (or correct it) on its page and remove the check from this list. Test-mod snippets were written from the vanilla file shapes and have not been loaded yet, so a first run may need a small fix that `error.log` names. Check ids are stable within this list: grep the page for the kit block named in a check.

#### Achievement modding

`hoi4_wiki/achievement_modding.md`

**G001.** Mod achievement format: unique_id mandatory, ribbon wrapper read, _NAME/_DESC keys, icon path from token plus suffix, condition text built from possible and happened, is_ironman not needed in a mod (kit block `ach-format-notes`)

- Setup: Mod folder b7ach with descriptor. common/achievements/b7.txt: line 1 `unique_id = b7_ach_001`, then `b7_ach = { possible = { difficulty > 1 game_rules_allow_achievements = yes } happened = { date > 1936.01.03 } }` and `b7_rib = { possible = { difficulty > 1 } happened = { date > 1936.01.03 } ribbon = { frames = { 1 1 1 1 } colors = { { 45.0 64.0 102.0 1.0 } { 154.0 73.0 107.0 1.0 } { 238.0 189.0 96.0 1.0 } { 211.0 181.0 128.0 1.0 } } } }`. localisation/english/b7_l_english.yml (UTF-8 with BOM): `l_english:` then ` b7_ach_NAME:0 "B7 Name"` and ` b7_ach_DESC:0 "B7 Desc"`. gfx/achievements/: copy the three vanilla files friend_in_need.dds, friend_in_need_grey.dds, friend_in_need_not_eligible.dds and rename them b7_ach.dds, b7_ach_grey.dds, b7_ach_not_eligible.dds. Delete the old Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log first.
- Steps:
  1. Start the game with only the b7ach mod. Start a new non-ironman game 1936.1.1 as GER.
  2. Open the career profile (Playthrough Overview) and look at the achievements list for 'B7 Name', its icon state and its condition text. Hover it.
  3. Open Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log and game.log and search for 'achievement', 'unique_id' and 'b7'.
  4. Quit. Rename b7_ach_grey.dds to b7_ach_grey_x.dds, restart, look at the same entry and the logs (tests the icon path rule).
  5. Restore the name. Remove the unique_id line from b7.txt, restart and read error.log again.
  6. Remove the b7_ach_NAME and b7_ach_DESC lines, restart and look at the entry text.
  7. Wrap the ribbon in a normal block by moving frames and colors out of `ribbon = { }` to directly under b7_rib, restart and compare the logs.
- Expected: If the claims hold: with unique_id the entry shows 'B7 Name' and 'B7 Desc' although `possible` has no is_ironman (so a mod needs no ironman check), condition text appears with 'Will be earned when:', renaming the grey icon makes the grey state show a missing texture (path = token + suffix), the missing unique_id line writes an 'unique_id is mandatory' style error and hides the entry, and the ribbon works only in the wrapper form. Any other result names which claim is wrong (for example an entry with no loc keys showing the raw token means the keys are not what the engine reads).
- Requirement: Career Profile and Awards say "not available when the Steam client is not running", so this check needs the Steam client running (seen 2026-11-02 in a launch without it).

#### AI focuses

`hoi4_wiki/ai_focuses.md`

**G003.** A country ai_focuses block replaces the whole generic block of that focus for the country (kit block `ai-focus-research-format`)

- Setup: Mod folder b7foc. common/ai_focuses/b7_POL.txt with nine blocks, one per generic focus (ai_focus_defense_POL, ai_focus_aggressive_POL, ai_focus_war_production_POL, ai_focus_military_equipment_POL, ai_focus_military_advancements_POL, ai_focus_peaceful_POL, ai_focus_naval_POL, ai_focus_naval_air_POL, ai_focus_aviation_POL), each `= { research = { armor = 1.0 } }`.
- Steps:
  1. Start a 1936.1.1 game with the mod. Run `observe`, then `tag POL` is not needed: leave POL to the AI.
  2. Run `gamespeed 5` and `pause_in_hours 4380` (six months).
  3. Run `tag POL` and open the research screen. Write down the technologies finished and in progress.
  4. Repeat on a run without the mod and compare.
- Expected: If the country block replaces the generic one, POL with the mod researches mostly armor technologies and no land doctrine or infantry weapon lines beyond the base, unlike the run without the mod. If the generic keys (land_doctrine 100, infantry weapons) still steer research, the blocks merge.
- Run 2026-11-02: tried, inconclusive because the AI-run POL gained the same two techs in six months with and without the `ai_focuses` file, so no steering toward armor was seen (two techs in 183 days, and the AI is not deterministic).

#### AI modding

`hoi4_wiki/ai_modding.md`

**G008.** allowed_types in an ai_equipment design is still read (kit block `ai-equipment-1193`)

- Setup: Mod folder b7eq. Copy common/ai_equipment/generic_tank.txt under the same name and add `allowed_types = { }` (empty) inside one design group, next to its `category`.
- Steps:
  1. Delete error.log. Start 1936.1.1 under AI control and run `gamespeed 5` for 60 days.
  2. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log for 'allowed_types'.
  3. Compare tank designs the AI made against a run without the mod.
- Expected: If the engine ignores allowed_types, there is no log line and designs are the same. An error or a design change means the key is read and the page text is wrong.
- Run 2026-11-02: tried, inconclusive because a silent log does not show that the key is read, and AI tank designs were not compared.

#### Autonomy state modding

`hoi4_wiki/autonomy_state_modding.md`

**G009.** peace_conference_initial_freedom unset gives 0.5 initial freedom for a puppet made in a peace conference (autonomy 'initial freedom' claim). (kit block `autonomy-vanilla-values`)

- Setup: Two mods. Both contain common/autonomous_states/puppet.txt, a byte copy of the vanilla file. Mod A adds the line `peace_conference_initial_freedom = 0.5` after `min_freedom_level = 0.4`. Mod B adds `peace_conference_initial_freedom = 0.9` in the same place. New game, 1936 start, play as GER.
- Steps:
  1. Run 1 with mod A: open the console and type `allowdiplo`.
  2. Declare war on LUX in the diplomacy window, occupy it and take the peace conference.
  3. In the conference make LUX a puppet and read the initial autonomy/freedom value shown for it. Write it down.
  4. Reload the save from before the war with mod B and repeat. Also repeat once with no mod.
- Expected: No mod and mod A show the same value, which means the unset default is 0.5. Mod B shows a different value (about 0.9 freedom). If no mod differs from mod A, the default is not 0.5.
- Run 2026-11-02: tried, inconclusive because ETH capitulated and a conference ended on 1936.01.08, but the AI did not make ETH a puppet of ITA, so `peace_conference_initial_freedom` was not read. Try the other `ai_desire` setup of the G218 recipe.

**G010.** The rule names can_force_government, can_lower_tension, can_not_build_buildings, can_occupy_non_war have an effect in an autonomy rule block; can_join_factions_not_allowed_diplomacy is ignored. (kit block `autonomy-rule-list-fixes`)

- Setup: Mod with common/autonomous_states/puppet.txt, a byte copy of the vanilla file, with one extra line inside its `rule = { ... }` block. Run 1 adds `can_not_build_buildings = yes`. Run 2 adds `can_join_factions_not_allowed_diplomacy = yes`. Run 3 adds `can_join_factions = no`. New game, 1936 start, play as GER.
- Steps:
  1. Run 1: open the console, type `tag MAN`, open the construction screen on a Manchukuo state and try to queue a building. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log.
  2. Run 2: start a new game, type `tag MAN`, open the diplomacy window and try to join a faction. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log.
  3. Run 3: same as run 2 with the third line.
- Expected: Run 1: construction is blocked if the rule has the meaning its name suggests, otherwise MAN can build. Run 2: the log has no error for the long name and MAN behaves as in vanilla, which means the name is ignored (an error line naming it would mean it is an unknown rule). Run 3 is the control: joining a faction is blocked only if can_join_factions is evaluated.
- Run 2026-11-02: settled that the four names load without a message in an autonomy rule block and that `can_join_factions_not_allowed_diplomacy` is reported as an unknown rule. Remains: whether any of the four has its effect, which needs a country that holds the state.

#### Bookmark modding

`hoi4_wiki/bookmark_modding.md`

**G017.** Defaults and effects of the bookmark filter keys, and what version and assume_not_played_if_missing_data do (kit block `bookmark-1193-keys`)

- Setup: Mod folder b7bm. Copy common/bookmarks/the_gathering_storm.txt under the same name. Variant A: unchanged. Variant B: uncomment `sort_unplayed_first = no`. Variant C: uncomment `scrollable_country_list = yes` and `apply_filter_to_majors = yes`.
- Steps:
  1. Start the game with the mod and open the scenario select screen of The Gathering Storm.
  2. Note the order of the country list and the filter buttons. Click the new_content filter and note which countries show.
  3. Repeat for variants B and C.
  4. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log.
- Expected: If the comment defaults are true, variant A equals the explicit yes/no values: countries with unplayed content first, majors also in the small list, no scrollbar. Variant B moves unplayed countries from the top. Variant C adds a scrollbar and the filter hides majors that do not match. The new_content filter should list the countries whose entries have newer `version` values when the profile has not played them.

#### Building modding

`hoi4_wiki/building_modding.md`

**G019.** base_cost_conversion on arms_factory and industrial_complex sets a factory conversion cost. (kit block `building-cost-notes`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). common/buildings/00_buildings.txt: a copy of the vanilla file with base_cost_conversion = 4000 on arms_factory changed to 100.
- Steps:
  1. Run the game once without the mod: new 1936 game as GER, open the construction screen of any state and use the convert option to turn a civilian factory into a military factory. Note the cost shown in the tooltip, then cancel.
  2. Repeat with the mod enabled in the same state.
- Expected: If the tooltip cost or the days drop with the mod, base_cost_conversion is the conversion cost for that building. If nothing changes, the key does something else or nothing.

**G020.** need_detection = yes on the facilities and dams changes what a foreign player sees. (kit block `building-argument-notes`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). common/buildings/00_buildings.txt: vanilla copy with need_detection = yes removed from one facility type (for example naval_base) and added to arms_factory.
- Steps:
  1. New 1936 game as GER with fog of war on. Without the mod, open the map near a French coastal state and look at its building icons.
  2. Repeat with the mod enabled and the key removed from that building type; then add the key to arms_factory and look at a French inland state.
- Expected: If a building with need_detection shows its icon only when detected and the same building without the key shows it always, the key is a detection gate. If the icons look the same, the key has no visible effect for the player.

**G021.** affects_energy = yes marks buildings that count in the state energy calculation. (kit block `building-argument-notes`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). common/buildings/00_buildings.txt: vanilla copy with affects_energy = yes removed from commercial_nuclear_reactor.
- Steps:
  1. New 1936 game as GER. Run: tag GER; eval_effect 64 = { add_building_construction = { type = commercial_nuclear_reactor level = 1 instant_build = yes } }
  2. Run: goto_state 64 and open the state view; read the energy line of the state tooltip.
  3. Repeat in a game without the mod.
- Expected: If the energy figures for state 64 differ between the two runs, affects_energy controls whether the building enters the energy sum. If they are equal, the key does not change the energy tooltip.
- Run 2026-11-02: tried, inconclusive because `energy_ratio` for GER read 1 before and after in every variant, including the control, so a capped ratio could not move. The state tooltip figure and the reactor level were not read.

**G022.** centered = yes on supply_node and radar_station changes the model or icon placement. (kit block `building-model-notes`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). common/buildings/00_buildings.txt: vanilla copy with centered = yes removed from radar_station and added to arms_factory.
- Steps:
  1. New 1936 game as GER. Run: goto_state 64 and zoom to the state.
  2. Take a screenshot of the arms factory models and of the radar station, then repeat without the mod.
- Expected: If the placement or icon position of the arms factory moves toward the province centre and the radar station changes the other way, centered controls placement. If the screenshots are identical, centered has no visible effect.

**G023.** air_defence on anti_air_building acts as a state modifier. (kit block `building-property-keys`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). common/buildings/00_buildings.txt: vanilla copy with air_defence = 1 in anti_air_building changed to 50.
- Steps:
  1. New 1936 game as GER. Run: tag GER; eval_effect 64 = { add_building_construction = { type = anti_air_building level = 1 instant_build = yes } }
  2. Run: goto_state 64 and read the state tooltip and list_modifiers for the state.
  3. Repeat without the mod.
- Expected: If an air defence value changes with the mod (or list_modifiers shows an air defence entry), the key is applied. If both runs match, the key is ignored and the wiki sentence is wrong.

#### Character modding

`hoi4_wiki/character_modding.md`

**G026.** Effect of always_show_on_actions_tooltip = yes on an advisor block (kit block `char-advisor-vanilla`)

- Setup: New game, 1936 start, play as AST, no mods. AST_billy_hughes (common/characters/AST.txt line 101) has the key in his political_advisor block.
- Steps:
  1. Open the Politics tab and the political advisor list.
  2. Hover AST_billy_hughes and screenshot the tooltip.
  3. Hover another AST political advisor that has an on_add block but not the key and screenshot it.
  4. Compare whether the on_add effect lines are shown in both.
- Expected: If the tooltip of AST_billy_hughes lists the on_add effects while the other one does not, the key forces the effect lines into the tooltip. If both look alike, the key has no visible effect here.

**G027.** Navy planning/logistics skill, skill above 9 levels, second scientist specialization, recruit_character outside history, undefined trait id (kit block `char-unit-leader-vanilla`)

- Setup: Mod folder b5_test with descriptor.mod. File common/characters/b5_chars.txt: characters = { B5_adm = { name = B5_adm portraits = { navy = { large = GFX_Portrait_Europe_Generic_1 } } navy_leader = { skill = 3 attack_skill = 3 defense_skill = 3 maneuvering_skill = 3 coordination_skill = 3 planning_skill = 6 logistics_skill = 6 } } B5_gen = { name = B5_gen portraits = { army = { large = GFX_Portrait_Europe_Generic_1 } } corps_commander = { skill = 10 attack_skill = 10 defense_skill = 10 planning_skill = 10 logistics_skill = 10 traits = { nationalist } } } B5_sci = { name = B5_sci portraits = { civilian = { large = GFX_Portrait_Europe_Generic_1 } } scientist = { skills = { specialization_nuclear = 3 specialization_naval = 4 } } } } File events/b5_ev.txt: add_namespace = b5 country_event = { id = b5.1 title = b5.1 desc = b5.1 is_triggered_only = yes option = { name = b5.1 recruit_character = B5_adm recruit_character = B5_gen recruit_character = B5_sci } }
- Steps:
  1. Start a new game, 1936 start, play as GER, with only b5_test enabled.
  2. Open the console and run: event b5.1
  3. Read error.log and search for B5_, nationalist and skill.
  4. Open the army and navy leader screens: hover B5_adm and B5_gen and note skill tooltips and values.
  5. Open the scientist list and hover B5_sci: note which specializations show and their levels.
- Expected: No recruit error means recruit_character works outside history. B5_adm tooltips with planning or logistics values mean the engine takes those keys on navy leaders, none or an error line means it does not. A B5_gen skill value capped at 9 or an error line shows how a level above the table is handled. B5_sci with nuclear 3 and naval 4 means both specializations apply, only nuclear 3 means the second is ignored. An error line naming trait nationalist shows an undefined trait id is reported.
- Run 2026-11-02: settled `recruit_character` outside history (it works and prints a load warning), the ignored navy planning and logistics skills, the skill 10 result and a second scientist specialization (both kept). Remains: the undefined trait id.

**G030.** command_power on a trait is the command power price of the advisor (kit block `char-country-leader-traits-vanilla`)

- Setup: Mod folder b5_test with descriptor.mod. File common/country_leader/b5_traits.txt: leader_traits = { b5_cp_trait = { sprite = 5 random = no command_cap_increase = 10 command_power = 25 } } File common/characters/b5_adv.txt: characters = { B5_cp = { name = B5_cp portraits = { army = { large = GFX_Portrait_Europe_Generic_1 } } advisor = { slot = army_chief idea_token = B5_cp traits = { b5_cp_trait } cost = 1 } } } File events/b5_ev.txt: add_namespace = b5 country_event = { id = b5.3 title = b5.3 desc = b5.3 is_triggered_only = yes option = { name = b5.3 recruit_character = B5_cp } }
- Steps:
  1. Start a new game, 1936 start, play as GER, with only b5_test enabled. Note the command power on the top bar.
  2. Run in the console: event b5.3
  3. Open Politics, military advisors, army chief, and hover B5_cp. Screenshot the tooltip and the hire button state.
  4. Hire B5_cp and note the command power before and after.
- Expected: If hiring needs or spends 25 command power (tooltip price or a drop of 25), command_power on a trait is a price. If nothing is charged, the key is not a price. A max command power increase of 10 shows command_cap_increase works as the wiki says.
- Run 2026-11-02: tried, inconclusive because hiring the advisor by effect took no command power on both routes, an effect hire may skip the price, and the UI hire button was not used.

**G031.** Wiki parent = trait with a separate num_parents_needed is accepted; message for too many parents needed (kit block `char-trait-selection-correction`)

- Setup: Mod folder b5_test with descriptor.mod. File common/unit_leader/b5_traits.txt: leader_traits = { b5_a = { type = all trait_type = basic_trait gui_row = 0 gui_column = 0 } b5_b = { type = all trait_type = basic_trait gui_row = 1 gui_column = 0 parent = b5_a num_parents_needed = 1 } b5_c = { type = all trait_type = basic_trait gui_row = 1 gui_column = 1 parent = { traits = { b5_a } num_parents_needed = 2 } } b5_d = { type = all trait_type = basic_trait gui_row = 1 gui_column = 2 any_parent = { b5_a } } }
- Steps:
  1. Start a new game, 1936 start, play as GER, with only b5_test enabled.
  2. Read error.log and search for b5_ and num_parents_needed.
  3. Open any corps commander in the army leaders screen and look at the trait tree: check whether b5_b, b5_c and b5_d appear under b5_a with a line to it.
- Expected: A line saying num_parents_needed is superior to the number of parents for b5_c confirms that message. b5_b drawn under b5_a with no error means the wiki form is accepted. An error line for b5_b or b5_b missing means only the block form works. b5_d under b5_a confirms any_parent.
- Run 2026-11-02: tried, inconclusive because the wiki form and the 2-parents case loaded without a message, but the parents message may only come when the trait tree window is built, which was not opened.

#### Collection modding

`hoi4_wiki/collection_modding.md`

**G039.** A missing localisation key for a collection name and for a check_variable tooltip shows as the raw key (kit block `(kit page)`)

- Setup: New game, 1936 start, play as GER, only the test mod. Mod files (no localisation file): common/decision_categories/b4.txt: b4_cat = { icon = generic_political_actions } and common/decisions/b4.txt: b4_cat = { b4_dec = { available = { check_variable = { b4_v > 0 tooltip = B4_NO_KEY_A } collection_size = { input = { input = game:scope operators = { country_and_all_subjects } name = B4_NO_KEY_B } value > 5 } } } }
- Steps:
  1. Start with the mod and open the Decisions screen as GER
  2. Hover the b4_dec decision
  3. Take a screenshot of the tooltip and read error.log
- Expected: If the tooltip shows the text B4_NO_KEY_A and B4_NO_KEY_B, a missing key shows as the raw key (for both the collection name and the variable tooltip). Blank text or a crash means the page is wrong.

#### Console commands

`hoi4_wiki/console_commands.md`

**G045.** set_country_flag with another tag and with a duration (kit block `cc-fix-useful`)

- Setup: New game, 1936, GER, no mods.
- Steps:
  1. Console: set_country_flag b1_flag_a
  2. Console: list_flags and note whether b1_flag_a is listed.
  3. Console: set_country_flag b1_flag_b POL, then list_flags POL.
  4. Console: set_country_flag b1_flag_c 5, run 6 in-game days, then list_flags.
- Expected: b1_flag_a is listed. If b1_flag_b appears under POL, another tag works. If it lands on GER or errors, the page's note holds. If b1_flag_c is gone after 5 days, the second argument is a duration.
- Run 2026-11-02: settled that another tag does not work (`set_country_flag b1_flag_b POL` set the flag on GER). Remains: whether the number is a duration (`set_country_flag b1_flag_c 5` printed "set to 5" and the 6-day check was not run).

**G050.** Where loc_check results and details appear, and whether a mod's ignored_loc_keys.txt applies (kit block `cc-modding-highlights`)

- Setup: Test mod b1: Documents/Paradox Interactive/Hearts of Iron IV/mod/b1.mod holds the lines name="b1", path="mod/b1" and supported_version="*". Its content folder is Documents/Paradox Interactive/Hearts of Iron IV/mod/b1/. Add mod/b1/events/b1.txt with the two lines 'add_namespace = b1' and 'country_event = { id = b1.1 title = b1.1.t desc = b1.1.d option = { name = b1.1.a } }' and no localisation. New game, 1936, GER, mod enabled.
- Steps:
  1. Console: loc_check_events. Note the output.
  2. Open Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log and search for b1.1.
  3. Console: loc_check. Note the output.
  4. Create mod/b1/localisation/ignored_loc_keys.txt with the keys b1.1.t, b1.1.d, b1.1.a (one per line, like the vanilla file) and rerun loc_check_events.
- Expected: A result line such as 'N missing loc keys found, check error log' plus error.log lines naming b1.1 confirms the details are in the error log. If the mod copy silences the result, mods can extend the list. If not, only the vanilla file is read.
- Run 2026-11-02: settled where the results go (counts in the console, key lists in error.log). Remains: whether a mod copy of `ignored_loc_keys.txt` applies.

**G053.** What the undocumented tweakable variables do (Draw.*, Audio.*, Debug.*) (kit block `cc-tweakables`)

- Setup: New game, 1936, GER, no mods, debug launcher entry.
- Steps:
  1. Console: Draw.Water, then Draw.Rivers, then Draw.Terrain, one at a time, with a screenshot after each.
  2. Enter each again to toggle it back.
  3. Console: Audio.Debug and note any new text or overlay.
- Expected: Each Draw.* name toggles drawing of that map layer and prints Enabled or Disabled. No visible change means the variable does nothing in this build.
- Run 2026-11-02: `Draw.Water`, `Draw.Rivers`, `Draw.Terrain` and `Audio.Debug` printed "Command available only for developers." Remains: the other Draw.*, Audio.* and Debug.* variables.

#### Cosmetic tag modding

`hoi4_wiki/cosmetic_tag_modding.md`

**G055.** A cosmetic tag can select its own unit entity through a COSMETICTAG_<name>_entity asset. (kit block `cosmetic-other-vanilla`)

- Setup: Mod files: common/countries/cosmetic.txt with `T_GER = { color = rgb { 200 50 50 } color_ui = rgb { 200 50 50 } }`. gfx/entities/t_ger.asset with `entities = { entity = { name = "T_GER_artillery_entity" clone = "FRA_artillery_entity" } }`. localisation/english/t_l_english.yml with `l_english:`, ` T_GER_neutrality:`, ` T_GER_DEF:` lines. New game 1936 as GER with artillery visible on the map.
- Steps:
  1. Type `set_cosmetic_tag GER T_GER`.
  2. Zoom to a German artillery division on the map and take a screenshot.
  3. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log.
- Expected: German artillery shows the French model: the entity is used. The usual German model means the pattern is not applied (or needs another entity name).

#### Country creation

`hoi4_wiki/country_creation.md`

**G056.** A new flag file that breaks the rules (24 bit, RLE, flipped) triggers a slow-down warning or flipped image. (kit block `country-flag-facts`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). gfx/flags/GER.tga: vanilla GER.tga re-saved as 24 bit uncompressed (same 82 x 52 size). Second copy test: save it RLE compressed.
- Steps:
  1. Delete error.log and game.log, launch with the mod, start 1936 as GER.
  2. Look at the German flag in the top bar and the diplomacy screen (screenshot), then read both logs.
- Expected: A warning in a log naming the flag, a flipped image or a slower start shows the rules matter. A normal flag and clean logs means this build accepts the 24 bit file.
- Run 2026-11-02: settled the 24 bit warning and that a 32 bit RLE flag is refused with "Unsupported format" and reported as "File not found". Remains: the flipped image and the slow start, which need a screenshot.

**G057.** COUNTRY_FLAG_TEX_MAX_SIZE and the other max-size defines are the sizes of the textures the flags are packed into. (kit block `country-flag-facts`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). common/defines/zz_b8.lua: NDefines.NGraphics.COUNTRY_FLAG_TEX_MAX_SIZE = 64
- Steps:
  1. Launch with the mod, start a 1936 game as GER, open the diplomacy screen.
  2. Screenshot the flags, then read error.log.
- Expected: Missing or blank flags, or a log line about texture size, means the define limits the packed flag texture. Normal flags and a clean log means the define does not limit what is shown here.
- Run 2026-11-02: tried, inconclusive because `COUNTRY_FLAG_TEX_MAX_SIZE = 64` drew no log line and no crash, and blank or missing flags need a screenshot, which was not taken.

#### Data structures

`hoi4_wiki/data_structures.md`

**G061.** days_left and the three conscription names as variables (kit block `dynamic-variables-1-19-3`)

- Setup: New game, 1936 start, play as GER, only the test mod. Mod file common/scripted_effects/b4.txt: b4_vars = { set_temp_variable = { b4_a = days_left } set_temp_variable = { b4_b = conscription_ratio } set_temp_variable = { b4_c = target_conscription_amount } set_temp_variable = { b4_d = current_conscription_amount } log = "B4 [?b4_a] [?b4_b] [?b4_c] [?b4_d]" }
- Steps:
  1. Start with the mod and read error.log at the main menu
  2. Console: effect GER b4_vars
  3. Read game.log and error.log
- Expected: Numbers in the B4 line (non-zero conscription values) mean the names work as variables. A zero for a name together with an unknown variable error in error.log means it does not.
- Run 2026-11-02: settled for the three conscription names (they are triggers, not variables: variable reads gave 0, trigger reads gave real values). Remains: `days_left`.

#### Decision modding

`hoi4_wiki/decision_modding.md`

**G064.** Unset highlight colour, highlight_only_provinces, name/desc keys, targets with capital, modifier without timer, state_trigger name (kit block `decision-highlight-colours`)

- Setup: Mod folder b5_test with descriptor.mod. File common/decisions/b5_dec.txt: political_actions = { b5_hl_none = { available = { always = yes } highlight_states = { highlight_state_targets = { state = 64 } } } b5_hl_prov = { available = { always = yes } highlight_states = { highlight_state_targets = { state = 64 } highlight_provinces = { 375 478 } highlight_only_provinces = yes } } b5_named = { available = { always = yes } name = b5_custom_name desc = b5_custom_desc } b5_mod = { available = { always = yes } modifier = { political_power_factor = 0.1 } } b5_cap = { available = { always = yes } targets = { capital } } b5_st = { available = { always = yes } state_trigger = any target_trigger = { FROM = { state = 64 } } } } File localisation/english/b5_l_english.yml (UTF-8 with BOM): l_english: b5_hl_none:0 "None" b5_hl_prov:0 "Prov" b5_named:0 "Id name" b5_mod:0 "Mod" b5_cap:0 "Cap" b5_st:0 "St" b5_custom_name:0 "Custom name" b5_custom_desc:0 "Custom desc" (one entry per line in the real file)
- Steps:
  1. Start a new game, 1936 start, play as GER, with only b5_test enabled.
  2. Read error.log and search for b5_ and Decision scripted with modifier.
  3. Open the Political actions decisions and note which of the six decisions are listed and their titles.
  4. Hover b5_hl_none and b5_hl_prov in turn and screenshot the map around Brandenburg (state 64).
  5. Open the state view with state_trigger decision b5_st and check whether a decision entry appears on Brandenburg.
- Expected: b5_hl_none showing no outline means an unset colour is no highlight, a white outline means the wiki is right. b5_hl_prov outlining only provinces 375 and 478 and not the whole state confirms the likely meaning of highlight_only_provinces. b5_named titled Custom name confirms name replaces the id key. An error line about a modifier without days_remove for b5_mod confirms the message. b5_cap listed or an error line shows how capital in targets is handled. A b5_st entry on Brandenburg means state_trigger is accepted, none means only state_target works.
- Run 2026-11-02: settled the modifier-without-timer message and that `state_trigger` is not accepted. Remains: the unset highlight colour, what `highlight_only_provinces` outlines, the name and desc titles and the `capital` target, which need the interface.

**G065.** What the interface does with custom_icon tag, value and desc in a category (kit block `decision-category-vanilla`)

- Setup: New game, 1936 start, play as BUL, no mods. Vanilla: common/decisions/categories/BUL_decision_categories.txt has custom_icon blocks for GER, ENG and SOV.
- Steps:
  1. Open the decisions screen and find the industrial agreements category of BUL.
  2. Screenshot the category header and hover each icon.
  3. Run in the console: tag GER and then tag BUL again, and screenshot the header after each.
- Expected: If one icon per tag is shown, each with the value text and the desc tooltip, and the icon shows only while the tag country exists (the visible block), the reading in the wiki holds. Anything else shows a different meaning.
- Unavailable 2026-11-02: the BUL industrial agreements category needs the Battle for the Bosporus DLC, which was not among the 10 owned DLCs. Run it with that DLC.

**G066.** Missions: visible ignored, cost message, war_with_* keys, cosmetic_tag and cosmetic_ideology (kit block `decision-missions-vanilla`)

- Setup: Mod folder b5_test with descriptor.mod. File common/decisions/b5_mis.txt: political_actions = { b5_m_vis = { days_mission_timeout = 30 activation = { always = no } visible = { always = no } available = { always = yes } } b5_m_cost = { days_mission_timeout = 30 activation = { always = no } cost = 10 available = { always = yes } } b5_m_war = { days_mission_timeout = 1 activation = { always = no } available = { always = no } war_with_on_timeout = ENG war_with_target_on_complete = yes cosmetic_tag = ITA cosmetic_ideology = fascism timeout_effect = { add_stability = 0.01 } } } File common/scripted_effects/b5_fx.txt: b5_fx = { activate_mission = b5_m_vis activate_mission = b5_m_cost activate_mission = b5_m_war }
- Steps:
  1. Start a new game, 1936 start, play as GER, with only b5_test enabled.
  2. Read error.log and search for Cost for normal missions.
  3. Run in the console: effect GER b5_fx
  4. Open the missions list and note which of the three missions show, and hover b5_m_war.
  5. Set the game speed to 5 and let one day pass so b5_m_war times out, then read error.log again.
- Expected: The message Cost for normal missions not implemented for b5_m_cost confirms the exe string. b5_m_vis listed despite visible = no means visible is ignored for missions, not listed means it is honoured. The b5_m_war hover showing a war warning for ENG (and flag ITA fascism) shows war_with_on_timeout and the cosmetic keys work. No warning means the token is not used.
- Run 2026-11-02: settled the cost message. The war and cosmetic keys did nothing in one setup. Remains: whether `visible` is ignored and the mission tooltips.

#### Division modding

`hoi4_wiki/division_modding.md`

**G070.** role and obsolete in a division template change something in the game. (kit block `division-template-keys`)

- Setup: No mod. Vanilla history/units/ITA_1936.txt has templates with `obsolete = yes` (lines 130 and 152). New game 1936 as ITA.
- Steps:
  1. Open the division designer.
  2. Look at the template list for the two templates with `obsolete = yes` (open the file to read their names). Take a screenshot.
  3. Create a new template and compare how it is listed.
- Expected: Obsolete templates are marked or sorted differently in the list: obsolete has an effect. Identical listing means no visible effect. `role` has no visible UI; it needs AI observation, so only `obsolete` is settled here.
- Run 2026-11-02: settled `obsolete` (the three `obsolete = yes` Ascari templates are hidden behind an unticked "Show decommissioned templates" box). Remains: `role`, which needs AI observation, and the ticked view.

**G071.** bonus (CA1.txt) and start_manpower_factor in a history/units division block have an effect. (kit block `division-placement-keys`)

- Setup: Mod files: history/units/T_oob.txt with `division_template = { name = "T Div" regiments = { infantry = { x = 0 y = 0 } } }` and `units = { division = { name = "T plain" location = 11260 division_template = "T Div" } division = { name = "T bonus" location = 11260 division_template = "T Div" bonus = 1 } division = { name = "T manpower" location = 11260 division_template = "T Div" start_manpower_factor = 0.5 } }`. common/scripted_effects/t_fx.txt with `t_fx = { load_oob = "T_oob" }`. New game, 1936 start, play as GER.
- Steps:
  1. Type `effect GER t_fx`.
  2. Select each of the three new divisions and read strength, equipment and experience.
  3. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log.
- Expected: T manpower with about half the strength of T plain means start_manpower_factor is accepted in an OOB block. T bonus differing from T plain shows what bonus does. Equal divisions and a silent log mean the key is ignored, and an error line means it is rejected.
- Run 2026-11-02: settled `start_manpower_factor` (accepted, it halved the starting manpower). Remains: `bonus`. It loaded without an error and changed neither the division count nor the manpower, but experience and equipment were not read.

**G072.** link_numbering_with continues the numbering of another name group. (kit block `division-name-groups`)

- Setup: No mod. Vanilla common/units/names_divisions/GER_names_divisions.txt: motorized group has `link_numbering_with = { GER_Inf_01 }`. New game, 1936 start, play as GER.
- Steps:
  1. Open the division designer and create two infantry templates and one motorized template.
  2. Give each template its name group in the template window (the group list shows the group names).
  3. Train or create one division per template and read the division names.
- Expected: If numbering is shared, the motorized division gets the next free number counted across infantry and motorized divisions (for example 1. Infanterie-Division and 2. Infanterie-Division (mot)). If it starts at 1 independently, the link does nothing visible.

**G073.** ordered_name = N picks the Nth entry of an ordered ship name group, and ship equipment without owner works. (kit block `division-navy-keys`)

- Setup: No mod. history/units/GER_1939_naval_mtg.txt has destroyers with `ordered_name = 5`, 6 and 7. Start the 1939 scenario as GER.
- Steps:
  1. Open the navy screen and find the 2. Zerstorer Flottille.
  2. Read the names of the three destroyers.
  3. Compare with the `ordered` table of the destroyer group in common/units/names_ships/GER_ship_name.txt.
- Expected: The ships are named after the entries numbered 5, 6 and 7 of the matching destroyer group (for example 'Z5 Paul Jacobi'). Names from the fallback format (for example 'Z %d') mean the number is not used as an index. The missing owner claim stays untested here.

**G074.** A support company id placed in a regimental_support block is accepted. (kit block `division-support-correction`)

- Setup: common/scripted_effects/t_fx.txt in a mod with `t_fx = { division_template = { name = "T RS" regiments = { infantry = { x = 0 y = 0 } } regimental_support = { anti_air = { x = 0 y = 0 } } } }`. New game, 1936 start, play as GER.
- Steps:
  1. Type `effect GER t_fx`.
  2. Open the division designer and look for the template T RS.
  3. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log.
- Expected: T RS shows with the anti_air company in the regimental slot and the log is clean: accepted. A missing template or an error line naming anti_air means it is rejected or dropped.
- Run 2026-11-02: tried, inconclusive because the template was created without an error, but `has_template_containing_unit` returned FALSE even for valid companies, so it says nothing about the slot.

#### Effects

`hoi4_wiki/effects.md`

**G079.** Undocumented or stub effects, the effect form of not_tooltip, add_temporary_buff_to_units (kit block `combat-corrections`)

- Setup: New game, 1936 start, play as GER, only the test mod. Mod file common/scripted_effects/b4.txt, one effect per entry: b4_s1 = { ai_message = yes } b4_s2 = { add_scaled_political_power = yes } b4_s3 = { add_temporary_buff_to_units = { combat_offense = 0.1 } } b4_s4 = { every_army_leader = { boost_planning = yes } } b4_s5 = { every_army_leader = { set_leader_name = "B4" } } b4_s6 = { every_army_leader = { replace_unit_leader_trait = { trait = brilliant_strategist replace = <another unit leader trait id from common/unit_leader/> } } } (`replace = yes` crashed the game on 2026-11-02, do not use it) b4_s7 = { custom_override_tooltip = { tooltip = B4_TT not_tooltip = B4_TT_NOT add_stability = 0 } } b4_s8 = { add_region_efficiency = 1 }
- Steps:
  1. Start with the mod and read error.log at the main menu
  2. Console: effect GER b4_s1 up to b4_s8, one at a time
  3. Read error.log after each
- Expected: For each effect: an unknown-effect or bad-key error means it is not accepted in that form (expected for add_temporary_buff_to_units). Silence means the form is accepted. Error text for the stubs often names the keys they expect, copy it into the page. b4_s8 probably errors because GER is not a strategic region scope.
- Run 2026-11-02: settled s1 to s5, s7 and s8 (see the effects page). s6 as first written (`replace = yes`) logged "Invalid trait: yes" at load and crashed the game (EXCEPTION_ACCESS_VIOLATION), so it is not settled. Run s6 alone in its own session with a real trait id for `replace`.

**G081.** Whether set_portraits accepts navy (kit block `character-portrait-groups`)

- Setup: New game, 1936 start, play as GER, only the test mod. Mod file common/scripted_effects/b4.txt: b4_nav = { every_navy_leader = { limit = { always = yes } set_portraits = { navy = { small = GFX_portrait_JAP_kozo_sasaki_imprisoned } } log = "B4 navy portrait set" } }
- Steps:
  1. Start with the mod
  2. Console: effect GER b4_nav
  3. Read game.log and error.log, then open the list of GER navy leaders and take a screenshot
- Expected: No error and a changed portrait mean navy is accepted. An error in error.log naming navy, or no change, means only civilian and army work.
- Run 2026-11-02: tried, inconclusive because `set_portraits` with `navy` ran on seven navy leaders without an error, but whether the portraits changed was not looked at.

#### Entity modding

`hoi4_wiki/entity_modding.md`

**G085.** What the engine copies on `clone`, and what `version` selects (kit block `entity-keys-extra`)

- Setup: Mod b9ent. File gfx/entities/b9.asset: entities = { entity = { clone = "building_nuclear_reactor" name = "b9_clone_test" scale = 3 } } . In gfx/entities/b9.gfx copy the objectTypes entry that links the building `building_nuclear_reactor` to its entity (see gfx/entities/buildings.gfx) and change only its entity name to b9_clone_test.
- Steps:
  1. Start the mod, new 1936 game as GER, console: tag GER.
  2. Get a nuclear reactor onto a GER state: add it with a one-line scripted effect in the mod (set_state_flag is not enough, use add_building_construction or instant_build = yes) and run it with the console command effect.
  3. Open the state view and screenshot the building.
  4. Remove `scale = 3` from the entity, restart, and screenshot again.
  5. For `version`, copy the vanilla entity that sets `version = 1` (gfx/entities/units_vehicles.asset line 698) twice with version 1 and 2 and compare.
- Expected: With only the clone line the model looks the same as the vanilla reactor. With `scale = 3` it is three times larger, so keys written locally override what clone copies. A missing model or an error.log line about the entity means clone does not copy everything. A visible difference between version 1 and 2 shows what `version` selects.

**G086.** An entity event `time` is the start moment inside the state (kit block `entity-event-notes`)

- Setup: Mod b9ent2. Copy the vanilla entity that holds `event = { time = 14 node="mg1" particle = "aa_muzzle_small_particle" ... }` (gfx/entities/buildings.asset line 726) into gfx/entities/b9.asset under a new name. Variant A leaves the times as they are. Variant B sets the two events to `time = 0` and `time = 30`.
- Steps:
  1. Start the mod and trigger the state that holds the events (the strike state of the copied entity).
  2. Capture a screenshot sequence at 5 frames per second during the state.
  3. Repeat for variant B.
- Expected: If `time` is a start moment, the muzzle particle appears at that moment after the state starts, and a value later than the state length never shows. If it is a duration, the particle is on from the state start and lasts that long. The sequence tells the two apart.

#### Equipment modding

`hoi4_wiki/equipment_modding.md`

**G087.** abbreviation, derived_variant_name and visual_level on equipment have a visible use (wiki: visual_level is the image priority in the production screen). (kit block `equipment-keys`)

- Setup: No mod. Vanilla light tank chassis blocks set abbreviation (for example "lt1"), derived_variant_name and visual_level. New game, 1936 start, play as GER.
- Steps:
  1. Open the production screen, the equipment designer and the stockpile screen.
  2. Search the screenshots for the strings `lt1` or `afs0`, and for the localised name 'IW Light Tank'.
  3. In the production screen compare the image order of equipment with visual_level 0 and 3 (see common/units/equipment/*.txt).
- Expected: If the strings or the name appear in a UI element, that key is used there. If nothing appears anywhere, the key has no visible use in these screens. The image order shows the visual_level effect, if any.
- Run 2026-11-02: tried, inconclusive because the production line, the land production picker and the Tank Designer (GER 1936) showed the chassis name and the design name, not the abbreviation (`lt1`) or the `derived_variant_name` text (Light Tank I). The stockpile screen, the division designer equipment and tooltips were not checked, and the `visual_level` effect on the model was not compared.

**G088.** The game builds the equipment picture sprite name as GFX_<picture>_medium. (kit block `equipment-keys`)

- Setup: Mod with interface/t_equip.gfx declaring `spriteType = { name = "GFX_archetype_light_tank_equipment_medium" texturefile = "gfx/interface/ideologies/unknown.dds" }`. New game, 1936 start, play as GER.
- Steps:
  1. Open the production screen and the equipment designer for the light tank.
  2. Take a screenshot.
  3. Open the equipment of a type with a picture and no sprite, for example the amphibious tank (picture `archetype_amphibious_tank_equipment`).
- Expected: The light tank archetype shows the ideology texture: the name pattern is used. The vanilla picture still shows means the sprite name is built another way. The amphibious tank shows what the game does when no sprite exists (a blank or a fallback).

**G089.** A new equipment type needs at least one sub-unit that uses it. (kit block `equipment-types`)

- Setup: Mod with common/units/equipment/t_eq.txt: `equipments = { t_eq_1 = { year = 1936 is_buildable = yes type = land_cruiser resources = { steel = 1 } build_cost_ic = 10 } }`. Add any key the error log then asks for. land_cruiser is in the type enum but no vanilla sub-unit uses it. New game, 1936 start, play as GER.
- Steps:
  1. Open the production screen and look for t_eq_1 in the equipment list.
  2. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log.
- Expected: The equipment is listed and produced: no sub-unit is needed. A missing equipment or an error line about the type supports the wiki rule. Repeat with `type = infantry` as the control.
- Run 2026-11-02: tried, inconclusive because the minimal block loaded with no type error, but the stockpile probe read FALSE for the infantry control too, so usability was not shown, and the production screen was not read.

**G090.** group_by changes how equipment is grouped in the production screen. (kit block `equipment-group-by`)

- Setup: Mod with a byte copy of common/units/equipment/tank_chassis_light.txt (or the file that holds light_tank_chassis) with `group_by = archetype` replaced by `group_by = type`. New game, 1936 start, play as GER.
- Steps:
  1. Open the production screen, the tank equipment list.
  2. Take a screenshot.
  3. Run again without the mod and compare the grouping.
- Expected: A different grouping of tank variants in the list shows the key's effect. The same grouping means no visible effect for tanks. An error line names a rejected value.
- Run 2026-11-02: tried, inconclusive because `group_by = type` on `light_tank_chassis` changed nothing in the GER 1936 land production picker and drew no error line, but GER has only one light tank chassis and one design then, so the picker had nothing to group differently. Needs a later date with several chassis and designs.

**G091.** The extra interface_category_* names found in hoi4.exe (resources, stockpiling, reinforcing, upgrading, outdated) are usable. (kit block `equipment-interface-categories`)

- Setup: Mod with a byte copy of one equipment file (for example common/units/equipment/anti_tank.txt) where one block has `interface_category = interface_category_stockpiling`. New game, 1936 start, play as GER.
- Steps:
  1. Open the production screen and the stockpile screen.
  2. Find the equipment from that block and take a screenshot.
  3. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log.
- Expected: The equipment appears under a new or distinct category: the token is used. An error line or the equipment missing from the lists means the token is not usable. Repeat for the other four names.
- Run 2026-11-02: tried, inconclusive because the five tokens loaded without an error line, but the stockpile probe read FALSE for the control too and no negative control showed that an unknown token logs an error.

#### Event modding

`hoi4_wiki/event_modding.md`

**G092.** hoi4.exe event messages: leader event not triggered only, missing title/desc/option, triggered-only with timer, every-day event (kit block `event-engine-messages`)

- Setup: Mod folder b5_test with descriptor.mod. File events/b5_ev.txt: add_namespace = b5 unit_leader_event = { id = b5.10 title = b5.10 desc = b5.10 option = { name = b5.10 } } country_event = { id = b5.11 } country_event = { id = b5.12 title = b5.12 desc = b5.12 is_triggered_only = yes mean_time_to_happen = { days = 1 } option = { name = b5.12 } } country_event = { id = b5.13 title = b5.13 desc = b5.13 mean_time_to_happen = { days = 1 } option = { name = b5.13 } }
- Steps:
  1. Start a new game, 1936 start, play as GER, with only b5_test enabled.
  2. Read error.log and search for b5.1.
  3. Run: event b5.12 and note whether it fires.
  4. Fast forward a few days (console: fast_forward 5) and note whether b5.13 repeats every day.
- Expected: Each id line next to the quoted messages (leader event has to be triggered only, missing title, desc and options, triggered only without a 1 base-factor, set to trigger every day) confirms the matching row. A message missing for b5.12 means the 1 base-factor message needs another condition. b5.12 firing from the console shows the leftover timer does not block a called event.
- Run 2026-11-02: settled the load messages and that a triggered-only event with a timer can still be called. Remains: whether an event with a timer and a trigger repeats every day (the flag-clearing effect in the run was invalid, so no firing was seen either way).

**G094.** original_recipient_only on an option (kit block `event-option-ai-chance`)

- Setup: Mod folder b5_test with descriptor.mod. File events/b5_ev.txt: add_namespace = b5 country_event = { id = b5.20 title = b5.20 desc = b5.20 is_triggered_only = yes major = yes option = { name = b5.20 original_recipient_only = yes } option = { name = b5.20 } }
- Steps:
  1. Start a new game, 1936 start, play as ENG, with only b5_test enabled.
  2. Run in the console: event b5.20 GER
  3. Screenshot any event popup that ENG gets and count its options. Then run: tag GER and run the same event, and count the options.
- Expected: A popup for ENG with one option and one for GER with two means original_recipient_only hides the option from the other recipients. Equal option counts, or no ENG popup at all, means the claim could not be confirmed this way.

**G097.** What after and minor_flavor do in an event (kit block `event-optional-keys`)

- Setup: Mod folder b5_test with descriptor.mod. File events/b5_ev.txt: add_namespace = b5 country_event = { id = b5.50 title = b5.50 desc = b5.50 is_triggered_only = yes minor_flavor = yes option = { name = b5.50 set_country_flag = b5_opt } after = { set_country_flag = b5_after } }
- Steps:
  1. Start a new game, 1936 start, play as GER, with only b5_test enabled.
  2. Run: event b5.50 and look at the popup (screenshot), then pick the option.
  3. Run: get_country_flag b5_opt and get_country_flag b5_after.
  4. Repeat with minor_flavor = yes removed and compare the popup.
- Expected: b5_after set only after the option means after runs once the option effects finish. A different popup layout with minor_flavor shows its UI effect. If nothing differs, the key has no visible effect.
- Run 2026-11-02: settled that `after` runs once, after the option effects. Remains: what `minor_flavor` changes in the popup.

#### Faction modding

`hoi4_wiki/faction_modding.md`

**G099.** A player without the No Compromise, No Surrender DLC still gets faction templates, goals and rules. (kit block `faction-dlc-and-create`)

- Setup: Disable the NCNS DLC in the launcher playlist. No mod. New game, 1936 start, play as GER.
- Steps:
  1. Type `effect GER t_fx` with `t_fx = { create_faction_from_template = faction_template_generic }` in common/scripted_effects/t_fx.txt (mod file) or create a faction in the diplomacy window.
  2. Open the faction window and read goals, rules and template.
  3. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log.
- Expected: Goals, rules and the template show as in the DLC game: no DLC dependence. An empty faction window or an error line means non-DLC players do not get them.

**G100.** A faction rule typed joining_rule (singular) is accepted but never evaluated. (kit block `faction-rule-types`)

- Setup: Mod files: common/factions/rules/t_rules.txt with `t_join_singular = { type = joining_rule trigger = { always = no } }` and `t_join_plural = { type = joining_rules trigger = { always = no } }`. common/scripted_effects/t_fx.txt with `t_a = { create_faction_from_template = faction_template_generic set_faction_rule = t_join_singular }` and `t_b = { set_faction_rule = t_join_plural }`. New game, 1936 start, play as GER.
- Steps:
  1. Type `effect GER t_a` and open the GER faction window to confirm the rule is set.
  2. Type `tag FRA`, open the diplomacy window and try to join the GER faction.
  3. Start again, type `effect GER t_a` with `t_join_plural` in place of `t_join_singular` in t_a, and repeat step 2.
- Expected: With the plural rule joining is blocked (trigger always = no is evaluated). With the singular rule joining is allowed: the singular type is never evaluated as a joining rule. If both block, the singular token is evaluated too.
- Run 2026-11-02: tried, inconclusive because `set_faction_rule` refused both the singular and the plural joining rule on a template faction, so the singular type was never active.

#### Game rule modding

`hoi4_wiki/game_rule_modding.md`

**G101.** Game rule script lookups: case handling, missing rule or option, new group string needs only loc, tooltip placeholders, duplicate option tokens, allow_achievements in a mod (kit block `(kit page)`)

- Setup: Mod folder b7rules. common/game_rules/b7.txt: `b7_rule = { name = "B7_RULE" group = "B7_GROUP" option = { name = ONE text = "B7_ONE" } option = { name = TWO text = "B7_TWO" } }` and `b7_dup = { name = "B7_DUP" group = "B7_GROUP" option = { name = ONE text = "B7_ONE" } option = { name = ONE text = "B7_TWO" } }`. localisation/english/b7_l_english.yml (UTF-8 with BOM): `l_english:` ` B7_RULE:0 "B7 Rule"` ` B7_DUP:0 "B7 Dup"` ` B7_GROUP:0 "B7 Group"` ` B7_ONE:0 "One"` ` B7_TWO:0 "Two"`. common/scripted_effects/b7.txt: `b7_report = { if = { limit = { has_game_rule = { rule = b7_rule option = ONE } } log = "B7 exact yes" } if = { limit = { has_game_rule = { rule = B7_RULE option = ONE } } log = "B7 rulecase yes" } if = { limit = { has_game_rule = { rule = b7_rule option = one } } log = "B7 optcase yes" } if = { limit = { has_game_rule = { rule = b7_missing option = ONE } } log = "B7 missingrule yes" } if = { limit = { has_game_rule = { rule = b7_rule option = NOPE } } log = "B7 missingopt yes" } if = { limit = { game_rules_allow_achievements = yes } log = "B7 ach yes" } }`. events/b7.txt: `add_namespace = b7` and `country_event = { id = b7.1 is_triggered_only = yes title = "B7" desc = "B7" option = { name = "B7" trigger = { has_game_rule = { rule = b7_rule option = TWO } } } }`. Delete error.log and game.log first.
- Steps:
  1. Start the game with the mod. On the game rules screen note whether the group 'B7 Group' and both rules appear with their labels. Keep b7_rule on ONE and b7_dup on its default. Start 1936.1.1 as GER.
  2. Run `effect GER b7_report`.
  3. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/game.log for lines starting 'B7' and error.log for 'b7_missing', 'NOPE' and 'b7_dup'.
  4. Run `event b7.1 GER`. The option is unavailable. Hover it and read the tooltip text.
  5. Restart, set b7_rule to TWO, set b7_dup to its second option, start a new non-ironman game, run `effect GER b7_report` again and read the logs. Note whether the pause menu or career profile says achievements are disabled.
- Expected: Case: 'B7 rulecase yes' or 'B7 optcase yes' in game.log means the lookup ignores case, and their absence means it is exact. Missing rule or option: an error.log line (or 'yes') shows how it is evaluated, and no line means it is silently false. Group: the group shows 'B7 Group' with only the loc entry. Tooltip: shows 'Game rule B7 Rule is set to the option ...' and whether the option part reads 'Two' (label) or 'TWO' (name). Duplicate tokens: error.log mention or a rule screen showing two same-named options. Achievements: with TWO selected 'B7 ach yes' disappears (the option defaults to not allowing achievements), and the pause or career text tells whether a mod game blocks achievements anyway.
- Run 2026-11-02: settled case handling, the messages for a missing rule or option and a new group string (no load error). Remains: whether `allow_achievements` changes anything in a mod, the group label and tooltip text, and duplicate option tokens.

**G102.** The six rules never read by script (allow_paratroopers, maximum_fort_level, allow_scorched_earth, peace_score_to_overlord, peace_score_to_faction_leader, peace_score_reset_low_scores) act through the engine (kit block `(kit page)`)

- Setup: No mod. New game 1936.1.1 as GER.
- Steps:
  1. On the game rules screen set allow_paratroopers to its option `no` (option names `yes` and `no`, common/game_rules/00_game_rules.txt lines 363 to 368). Start the game.
  2. Run `add_tech paratroopers`. Open the division designer and see whether the paratrooper battalion can be added to a template.
  3. Restart with maximum_fort_level set to its lowest option (read the option names in common/game_rules/00_game_rules.txt first). Open the construction screen of any province and note the highest land fort level that can be queued.
- Expected: If the rule works through the engine, the paratrooper battalion is blocked (or the fort level is capped) even though no script reads the rule. If both behave as before, the rule has no visible effect and the page must say so.

#### Graphical asset modding

`hoi4_wiki/graphical_asset_modding.md`

**G103.** `progressBarType` and `progressbartype` are the same keyword (kit block `gfx-sprite-census`)

- Setup: Mod b9pb. File interface/b9.gfx: spriteTypes = { progressBarType = { name = "GFX_b9_bar1" textureFile1 = "gfx/interface/bop/bop_bar_orange_light.dds" textureFile2 = "gfx/interface/absolute_nothing.dds" size = { x = 360 y = 16 } effectFile = "gfx/FX/progress_minmax.lua" } progressbartype = { name = "GFX_b9_bar2" (same keys) } } . A window as in the base UI mod of check B9-03 with two progressbar elements b1 and b2 using the two sprites (copy a vanilla progressbar element from interface/powerbalanceview.gui).
- Steps:
  1. Start the game and screenshot both bars at half value.
  2. Read error.log for lines that name either sprite.
- Expected: Both bars render the same, with no error.log line, if the two spellings are one keyword. If only one renders, the other spelling is ignored.

**G104.** the `allwaystransparent` spelling is accepted (kit block `gfx-sprite-key-corrections`)

- Setup: Mod b9sp. File interface/b9.gfx: spriteTypes = { spriteType = { name = "GFX_b9_a" texturefile = "gfx/interface/ideas/idea_africa_generic_1.dds" allwaystransparent = yes } spriteType = { name = "GFX_b9_b" texturefile = "gfx/interface/ideas/idea_africa_generic_1.dds" bogus_key_b9 = yes } } , plus the base UI window of check B9-03 with an icon for each sprite.
- Steps:
  1. Start the game with the window on screen.
  2. Read error.log and game.log for lines that name allwaystransparent, bogus_key_b9 or the two sprites.
- Expected: An unknown-key line for bogus_key_b9 but none for allwaystransparent means the typo is accepted. Lines for both mean the typo is rejected. No line for either means the game does not report unknown keys and the check settles nothing.

**G105.** `fontfiles` wins over `path`; font name case; unregistered font names; map font `tahoma_60` is found by name (kit block `gfx-font-key-notes`)

- Setup: Mod b9font. File interface/b9.gfx: bitmapfonts = { bitmapfont = { name = "b9_font" path = "gfx/fonts/hoi_18mbs" fontfiles = { "gfx/fonts/hoi_24header" } } bitmapfont = { name = "tahoma_60" path = "gfx/fonts/hoi_24header" } } . Window of the base UI mod of check B9-03 with three instantTextBoxType texts using font = "b9_font", "B9_FONT" and "hoi_26mbs" (registered nowhere).
- Steps:
  1. Start the game and screenshot the window. Take a screenshot with the game paused. After each edit of the .gui file run the console command reloadinterface.
  2. Read error.log for lines that name Font, B9_FONT or hoi_26mbs.
  3. Open the map view and screenshot the country and state name labels.
- Expected: b9_font is drawn in hoi_24header if fontfiles wins (hoi_18mbs otherwise), and error.log may carry the message about path and fontfiles. B9_FONT matches b9_font if names ignore case. hoi_26mbs is drawn or logged, which shows whether a font works without registration. Map labels in the tahoma_60 override show that the map font is found by name.
- Run 2026-11-02: settled that a font with both `path` and `fontfiles` logs that only `fontfiles` is used. Remains: unregistered font names, the case variant and the `tahoma_60` override.

#### Idea modding

`hoi4_wiki/idea_modding.md`

**G106.** Full GFX_ names in picture and the GFX_idea_unknown fallback (kit block `idea-picture-vanilla`)

- Setup: Mod folder b5_test with descriptor.mod. File common/ideas/b5_ideas.txt: ideas = { country = { b5_full = { picture = GFX_idea_generic_supply_line modifier = { political_power_gain = 0.01 } } b5_bare = { picture = generic_supply_line modifier = { political_power_gain = 0.01 } } b5_none = { picture = b5_no_such_sprite modifier = { political_power_gain = 0.01 } } } }
- Steps:
  1. Start a new game, 1936 start, play as GER, with only b5_test enabled.
  2. Run: add_ideas b5_full b5_bare b5_none
  3. Open the Politics tab and screenshot the national spirit icons of the three ideas.
  4. Read error.log and search for b5_.
- Expected: b5_full and b5_bare showing the same supply line icon means a full sprite name is accepted. A blank or unknown icon for b5_full means only the bare name works. The unknown placeholder icon on b5_none means the engine falls back to GFX_idea_unknown, a blank icon means it does not.
- Run 2026-11-02: tried, inconclusive because the three ideas were added without an error, but icons show only in the interface and no screenshot was taken.

**G110.** What the disabled_ideas modifier disables (kit block `idea-cost-factor-modifiers`)

- Setup: Mod folder b5_test with descriptor.mod. File common/ideas/b5_dis.txt: ideas = { country = { b5_dis = { modifier = { disabled_ideas = 1 } } b5_other = { modifier = { political_power_gain = 0.5 } } } }
- Steps:
  1. Start a new game, 1936 start, play as GER, with only b5_test enabled.
  2. Run: add_ideas b5_other and run: list_modifiers country. Note political_power_gain.
  3. Run: add_ideas b5_dis and run: list_modifiers country again, and open the Politics tab to see whether b5_other looks disabled.
- Expected: political_power_gain from b5_other disappearing or b5_other shown greyed means disabled_ideas switches off other national spirits. No change means it does nothing on its own.
- Run 2026-11-02: settled that `disabled_ideas` does not switch off another national spirit. Remains: what it does disable (laws, advisors, other idea types).

#### Ideology modding

`hoi4_wiki/ideology_modding.md`

**G112.** can_be_boosted = no on an ideology group stops other countries boosting it. (kit block `ideology-example-corrections`)

- Setup: Mod with common/ideologies/00_ideologies.txt, a byte copy of the vanilla file with `can_be_boosted = no` added inside the `fascism` group block (next to `ai_fascist = yes`). New game, 1936 start, play as GER.
- Steps:
  1. Open the diplomacy window of FRA and look for a boost-ideology action toward fascism.
  2. Run again without the mod and compare the available actions.
- Expected: The boost action is missing or disabled with the mod: the key controls boosting. The same actions as vanilla mean the key has no visible effect.

**G115.** set_politics accepts ruling_party = ROOT and ruling_party = var:<var> forms. (kit block `ideology-country-history-vanilla`)

- Setup: common/scripted_effects/t_fx.txt with `t_fx = { ENG = { set_politics = { ruling_party = ROOT } } }`. New game, 1936 start, play as GER.
- Steps:
  1. Type `effect GER t_fx`.
  2. Type `tag ENG` and read the ruling party.
  3. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log.
- Expected: ENG becomes fascism (copies the ROOT country's ruling ideology group): the scope form works that way. ENG unchanged and an error line mean the form is rejected, or it means something else if ENG changes to another ideology.

#### Intelligence agency modding

`hoi4_wiki/intelligence_agency_modding.md`

**G116.** Which of two available blocks counts, and that default picks the historical entry (kit block `ia-agency-file-checks`)

- Setup: Mod file common/intelligence_agencies/zz_b3.txt: block 1 `intelligence_agency = { picture = GFX_intelligence_agency_logo_usa names = { "B3 First" } available = { always = no } available = { always = yes } }`; block 2 `intelligence_agency = { picture = GFX_intelligence_agency_logo_uk names = { "B3 Second" } default = { tag = LUX } available = { always = yes } }`. Mod file common/scripted_effects/b3.txt: `b3_make = { create_intelligence_agency = yes }`. New game, 1936, play LUX, only this mod.
- Steps:
  1. Open the console and run `effect LUX b3_make`.
  2. Open the Intelligence Agency window.
  3. Note the agency name and logo.
  4. Restart, delete the `default` line from block 2 in the mod, run the same steps and note the name and logo again.
  5. Restart, open the logo picker through the new-agency screen (`create_intelligence_agency` with a block form in b3_make instead) and look for the B3 First logo.
- Expected: With default = LUX the agency is named B3 Second with the UK logo, so default selects the historical entry; without it the agency gets another entry, which would mean default is not what picks it. B3 First in the picker means the second available (always = yes) counts; absent means the first (always = no) counts.
- Run 2026-11-02: tried, inconclusive because the default names of the vanilla blocks won in every case and the mod blocks were never chosen, so it cannot be told whether the mod file was read or lost to an earlier block.

**G120.** Whether a sixth branch of your own displays in the upgrade window (kit block `ia-upgrades`)

- Setup: Mod file common/intelligence_agency_upgrades/zz_b3.txt: `branch_b3 = { upgrade_b3_test = { picture = GFX_upgrade_form_department_pic level = { modifier = { intelligence_agency_defense = 1 } } } }`. Check the real picture sprite name first in interface/countryintelligenceagencyview.gfx. Localisation keys branch_b3, upgrade_b3_test and upgrade_b3_test_desc in localisation/english/b3_l_english.yml. New game 1936, play GER.
- Steps:
  1. Run `effect GER b3_create` (see B3-03).
  2. Open the upgrade window and look for a sixth column or an extra entry in the branches grid.
  3. Read error.log.
- Expected: A visible sixth branch with a working upgrade means extra branches display. A missing branch or a layout break means the GUI only handles the five vanilla ones.

**G121.** Which frame sprite suffixes the engine reads (kit block `ia-upgrades`)

- Setup: Mod files: interface/b3.gfx defining GFX_b3_frame_unavailable, GFX_b3_frame_available and GFX_b3_frame_completed using a vanilla frame texture path; upgrade in common/intelligence_agency_upgrades/zz_b3.txt with `frame = GFX_b3_frame`. Repeat with `_current` in place of `_available`. New game, GER.
- Steps:
  1. Create the agency (B3-03) and open the upgrade window in the first variant.
  2. Look at the frame of the upgrade when it is available, in progress and completed.
  3. Swap the sprite names to the second variant and repeat.
  4. Read error.log for missing sprite names.
- Expected: The variant with no error and a visible frame in every state is the suffix set the engine reads. Errors naming the missing suffix point to the other set.

#### Intelligence operation modding

`hoi4_wiki/intelligence_operation_modding.md`

**G122.** Operations need the La Resistance DLC (kit block `(kit page)`)

- Setup: In Documents/Paradox Interactive/Hearts of Iron IV/dlc_load.json add "La Resistance" to the disabled DLC list, no mods. New game 1936, play GER.
- Steps:
  1. Open the Intelligence Agency window.
  2. Run `allowoperations` and `operation_start operation_infiltrate_civilian ENG` (check the exact id in common/operations/00_operations.txt).
  3. Read error.log.
- Expected: No operations UI and a refused command mean the DLC is required. A running operation means it is not. Restore dlc_load.json afterwards.

**G123.** Firing order of on_operation_completed, outcome_execute and operative detection (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. common/on_actions/b3.txt: `on_actions = { on_operation_completed = { effect = { log = "B3 on_operation_completed" } } on_operative_detected_during_operation = { effect = { log = "B3 detected" } } }`. common/operations/zz_b3.txt copies one short operation with outcome_execute = { log = "B3 outcome_execute" } (use ROOT = { log = ... } if country scope is needed). GER, La Resistance.
- Steps:
  1. Run `effect GER b3_create` (see B3-03), then `allowoperations`.
  2. Run `operation_start <id of the copied operation> ENG`.
  3. Run `fast_forward 40`.
  4. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/game.log and error.log after each step.
- Expected: The order of the three B3 lines in game.log is the engine order. The claim holds if on_operation_completed comes first, then outcome_execute, then detection.
- Run 2026-11-02: tried, inconclusive because the setup gave GER no usable operatives (`num_of_operatives=0`), so no operation started or completed.

**G124.** What experience does on an operation (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. common/operations/zz_b3.txt with two copies of one operation, one with experience = 0.5 and one with experience = 5.
- Steps:
  1. Start each with `operation_start`, assign the same operative, run `fast_forward 40`.
  2. Compare the operative's experience before and after.
- Expected: A larger gain with 5 than with 0.5 shows experience is operative experience. No difference means it is something else.
- Run 2026-11-02: tried, inconclusive because the setup gave GER no usable operatives (`num_of_operatives=0`), so neither operation ran. Only a repeat of the same operation was seen refused ("Tried to create the same operation twice against the same target").

**G125.** Whether time_multiplier is read (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. Two copies of one operation in common/operations/zz_b3.txt, one with time_multiplier = 1.0 and cost_multiplier = 0. New game, GER.
- Steps:
  1. Run the operation twice against ENG with `operation_start`.
  2. Compare the day count or cost on the second run for both copies.
- Expected: Different growth in days on the second run shows time_multiplier is read. The same growth means it is ignored.
- Run 2026-11-02: tried, inconclusive because the setup gave GER no usable operatives, so `time_multiplier` was not tested.

**G126.** What target_weight does (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. Copy of an operation with selection_target and a target_weight block that adds 100 for one named state (copy the syntax from 00_operations.txt line 1468).
- Steps:
  1. Let an AI country run the operation (ENG strategy files) for 60 days with `observe`, or start it with `operation_start`.
  2. Note which state is chosen over several runs.
- Expected: The weighted state chosen far more often by the AI shows target_weight steers the AI. If a player-started operation shows no effect, it is AI only.

**G127.** What scale_cost_independent_of_target does on operation_fake_intel (kit block `(kit page)`)

- Setup: No mods. New game, GER.
- Steps:
  1. Run `allowoperations`, run `operation_start operation_fake_intel ENG` and note the equipment cost.
  2. Finish it (`fast_forward 40`), start it against FRA and note the cost again.
  3. Repeat with a copy of the operation without the key.
- Expected: With the key the cost rises on the FRA run, since earlier runs count regardless of target. Without it the cost stays flat across targets.

**G128.** Whether is_staged_coup is read by the engine (kit block `(kit page)`)

- Setup: No mods. GER, La Resistance.
- Steps:
  1. Run `operation_start operation_coup ENG` (check the id) and open the target's trigger `is_staging_coup`, for example by a log effect in a mod on action.
  2. Repeat with a mod copy that removes is_staged_coup.
- Expected: is_staging_coup true only with the key present shows the engine reads it.

**G129.** What prevent_captured_operative_to_die does (kit block `(kit page)`)

- Setup: Mod copy of operation_rescue_operative with the key removed. A captured operative must exist: run `effect GER b3_capture` with `capture_operative = { captured_by = ENG }` on a created operative.
- Steps:
  1. Start the vanilla rescue and the modified one.
  2. Run `fast_forward 40` and check whether the captive survives.
- Expected: The captive surviving only with the key present shows it protects the captive.

**G130.** What happens when every candidate of a phase slot has failing requirements (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. Operation copy with a second `phases = { b3_never = { base = 100 } }` slot and phase b3_never in common/operation_phases/zz_b3.txt with `requirements = { always = no }`.
- Steps:
  1. Run `operation_start <id> ENG`.
  2. Run `operation_test_phase_selection <id> ENG`.
  3. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/game.log and error.log after each step.
- Expected: A refused start, an empty slot, or a log line shows the engine rejects it. A normal run with a fallback phase shows it is tolerated.
- Run 2026-11-02: tried, inconclusive because the setup gave GER no usable operatives, and `operation_test_phase_selection` printed "Failed to seed all phases" with no control on a valid operation.

**G131.** How risk_extra and outcome_extra are used (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. Copy of exfiltration_go_to_ground in common/operation_phases/zz_b3.txt with outcome_extra = "B3 EXTRA TEXT" and outcome = "B3 BASE TEXT".
- Steps:
  1. Run an operation using the phase with `operation_start`.
  2. Use `force_operative_detection` or `prevent_operative_detection` to produce a failure and a success run.
  3. Read the final outcome text in the completion event.
- Expected: B3 EXTRA TEXT in the failing run and B3 BASE TEXT in the clean run shows outcome_extra is chosen by the risk_extra roll. Otherwise vanilla's use of risk_extra as the text is the real channel.

**G133.** How an empty STATIC_INTEL_SOURCE_OPERATION_TOKENS_MAXIMUMS is read (kit block `(kit page)`)

- Setup: No mods. GER.
- Steps:
  1. Run `effect GER b3_tokens` with `add_operation_token = { tag = ENG token = token_army }`.
  2. Open the intel view for ENG and read the army intel breakdown.
- Expected: A visible token intel entry of the token's gain means the empty list is an unlimited cap. No entry means an empty list switches the source off.

**G134.** Whether outcome_extra_execute replaces outcome_execute (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. Operation copy with outcome_extra_chance = 1, outcome_execute = { log = "B3 BASE" } and outcome_extra_execute = { log = "B3 EXTRA" }. Repeat with outcome_extra_chance = 0.
- Steps:
  1. Run the operation with `operation_start` and `fast_forward 40` in each variant.
  2. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/game.log and error.log after each step.
- Expected: Only B3 EXTRA with chance 1 and only B3 BASE with chance 0 shows replace. Both lines with chance 1 shows the extra block adds.

**G135.** Whether an operation's own and unlisted modifiers apply (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. Operation copy zz_b3 with empty cost_modifiers, and a country idea or leader trait with `operation_cost = -0.5` and another with `operation_zz_b3_cost = -0.5` (adapt the id).
- Steps:
  1. Add the first idea with `add_ideas`, read the operation's equipment cost in the UI, remove it.
  2. Repeat with the second idea.
  3. Repeat after adding operation_cost to the operation's cost_modifiers list.
- Expected: A cost change only when the modifier is listed shows unlisted modifiers are ignored. A change from the operation's own id without listing shows own modifiers apply unlisted.

**G136.** Whether a mod on_operative_detected_during_operation replaces vanilla's (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. common/on_actions/b3.txt: `on_actions = { on_operative_detected_during_operation = { effect = { log = "B3 detected" } } }`.
- Steps:
  1. Run an operation to completion (see B3-08) with several operatives.
  2. Read game.log and note whether vanilla outcomes (hiding, capture, harm, death) still occur to the operatives.
- Expected: Vanilla outcomes still happening next to the B3 line means mod blocks add. Vanilla outcomes missing means the mod block replaces them.

**G137.** What operation_equipment_priority does (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. common/ai_strategy/zz_b3.txt for a country with a vanilla operation: `ai_strategy = { type = operation_equipment_priority value = 100 }` (copy the wrapper from ENG_operation_strats.txt). Compare to a control with value = 0.
- Steps:
  1. Run `observe`, fast_forward 90 days.
  2. Compare the production queue of the operation's equipment in both runs.
- Expected: Higher priority for the operation's equipment with 100 shows it raises production priority. No difference leaves the claim unconfirmed.

**G138.** What force_operative_detection, Operation.Instant and print_operation_tokens do (kit block `(kit page)`)

- Setup: No mods. GER with at least one operative and a running operation.
- Steps:
  1. Run `print_operation_tokens` and read the console and game.log.
  2. Run `Operation.Instant` and check if running operations finish at once.
  3. Run `force_operative_detection` and check the operative state.
- Expected: Output of held tokens, instant completion and a forced detection event confirm the name-based reading.
- Run 2026-11-02: tried, inconclusive because the setup gave GER no usable operatives. `print_operation_tokens` printed each token as "<target country> : <token>" and `Operation.Instant` answered "Enabled", but instant completion was not observed.

#### Interface modding

`hoi4_wiki/interface_modding.md`

**G139.** iconType `scale`, `rotation`, `hide` meanings and drawn size without `size` (kit block `if-icon-notes`)

- Setup: Mod b9ui with a descriptor.mod, enabled, new 1936 game as GER. File common/scripted_guis/b9.txt: scripted_gui = { b9_gui = { context_type = player_context window_name = "b9_window" parent_window_token = top_bar visible = { always = yes } } } . File interface/b9.gui: guiTypes = { containerWindowType = { name = "b9_window" position = { x = 300 y = 200 } size = { width = 700 height = 400 } iconType = { name = "i1" spriteType = "GFX_idea_unknown" position = { x = 0 y = 0 } } iconType = { name = "i2" spriteType = "GFX_idea_unknown" position = { x = 100 y = 0 } scale = 0.5 } iconType = { name = "i3" spriteType = "GFX_idea_unknown" position = { x = 200 y = 0 } rotation = 1.5708 } iconType = { name = "i4" spriteType = "GFX_idea_unknown" position = { x = 300 y = 0 } hide = yes } } }
- Steps:
  1. Start the game and look under the top bar.
  2. Take a screenshot with the game paused. After each edit of the .gui file run the console command reloadinterface.
- Expected: i1 is drawn at the pixel size of its sprite. i2 is half that size, so `scale` multiplies the size. i3 is turned a quarter turn, so `rotation` is in radians. i4 is not drawn, so `hide = yes` hides it. Any other picture means that reading is wrong.
- Run 2026-11-02: tried, inconclusive because `scale`, `rotation` and `hide` on `iconType` loaded without a message, and only a screenshot shows their meaning.

**G140.** instantTextBoxType `vertical_alignment`, `multiline`, `truncate`, `text_color_code` meanings (kit block `if-text-notes`)

- Setup: Mod b9ui with a descriptor.mod, enabled, new 1936 game as GER. File common/scripted_guis/b9.txt: scripted_gui = { b9_gui = { context_type = player_context window_name = "b9_window" parent_window_token = top_bar visible = { always = yes } } } . File interface/b9.gui: guiTypes = { containerWindowType = { name = "b9_window" position = { x = 300 y = 200 } size = { width = 700 height = 400 } instantTextBoxType = { name = "t1" position = { x = 0 y = 0 } font = "hoi_18mbs" text = "TOP" maxWidth = 200 maxHeight = 60 vertical_alignment = top } instantTextBoxType = { name = "t2" position = { x = 250 y = 0 } font = "hoi_18mbs" text = "CENTER" maxWidth = 200 maxHeight = 60 vertical_alignment = center } instantTextBoxType = { name = "t3" position = { x = 0 y = 100 } font = "hoi_18mbs" text = "one two three four five six seven eight nine ten" maxWidth = 120 maxHeight = 60 multiline = yes truncate = yes } instantTextBoxType = { name = "t4" position = { x = 250 y = 100 } font = "hoi_18mbs" text = "plain" maxWidth = 200 maxHeight = 20 text_color_code = b } } }
- Steps:
  1. Start the game and screenshot the window. Take a screenshot with the game paused. After each edit of the .gui file run the console command reloadinterface.
  2. Remove `truncate = yes` from t3 and screenshot again.
- Expected: t1 sits at the top of its 60 pixel box and t2 in the middle. t3 wraps over several lines and is cut with an ellipsis when truncate is on, and runs past the box (or is clipped) without it. t4 is drawn in the colour of code b. A different picture means the name-based reading is wrong for that key.
- Run 2026-11-02: tried, inconclusive because the four `instantTextBoxType` keys loaded without a message, and only a screenshot shows their drawing.

**G141.** containerWindowType `scale`, `click_to_front`, `background_margin` meanings (kit block `if-container-attrs`)

- Setup: Mod b9ui with a descriptor.mod, enabled, new 1936 game as GER. File common/scripted_guis/b9.txt: scripted_gui = { b9_gui = { context_type = player_context window_name = "b9_window" parent_window_token = top_bar visible = { always = yes } } } . File interface/b9.gui: guiTypes = { containerWindowType = { name = "b9_window" position = { x = 300 y = 200 } size = { width = 700 height = 400 } containerWindowType = { name = "c1" position = { x = 0 y = 0 } size = { width = 200 height = 100 } scale = 0.5 iconType = { name = "ci" spriteType = "GFX_idea_unknown" position = { x = 0 y = 0 } } } containerWindowType = { name = "c2" position = { x = 300 y = 0 } size = { width = 200 height = 100 } click_to_front = yes iconType = { name = "cj" spriteType = "GFX_idea_unknown" position = { x = 0 y = 0 } } } containerWindowType = { name = "c3" position = { x = 350 y = 20 } size = { width = 200 height = 100 } iconType = { name = "ck" spriteType = "GFX_idea_unknown" position = { x = 0 y = 0 } } } } }
- Steps:
  1. Start the game and screenshot the window. Take a screenshot with the game paused. After each edit of the .gui file run the console command reloadinterface.
  2. Click the icon of c2, then screenshot again (c2 and c3 overlap).
- Expected: c1's content is drawn at half size, so `scale` shrinks a container. c3 is on top of c2 at first. After the click c2 is drawn over c3, so `click_to_front` raises the container. No change means the reading from the names is wrong. `vertical_scroll_step` and `background_margin` are not covered by this check.
- Run 2026-11-02: tried, inconclusive because `scale` and `click_to_front` on `containerWindowType` loaded without a message, and their effect needs a screenshot and a click.

**G142.** `center_lower` is an alias of `center_down` (kit block `if-orientation-notes`)

- Setup: Mod b9ui with a descriptor.mod, enabled, new 1936 game as GER. File common/scripted_guis/b9.txt: scripted_gui = { b9_gui = { context_type = player_context window_name = "b9_window" parent_window_token = top_bar visible = { always = yes } } } . File interface/b9.gui: guiTypes = { containerWindowType = { name = "b9_window" position = { x = 300 y = 200 } size = { width = 700 height = 400 } instantTextBoxType = { name = "o1" position = { x = 0 y = 0 } font = "hoi_18mbs" text = "DOWN" maxWidth = 100 maxHeight = 20 orientation = center_down } instantTextBoxType = { name = "o2" position = { x = 0 y = 0 } font = "hoi_18mbs" text = "LOWER" maxWidth = 100 maxHeight = 20 orientation = center_lower } } }
- Steps:
  1. Start the game and screenshot the window. Take a screenshot with the game paused. After each edit of the .gui file run the console command reloadinterface.
  2. Read error.log for lines that name orientation.
- Expected: If center_lower is the same as center_down, DOWN and LOWER are drawn on top of each other at the bottom centre. If LOWER sits at the top left, the value is unknown and falls back to upper_left, or error.log reports it.
- Run 2026-11-02: tried, inconclusive because an unknown orientation value draws no message, so the log cannot say whether `center_lower` is an alias of `center_down`.

**G143.** `ignore_tab_navigation` works on an editBoxType (string found in hoi4.exe) (kit block `if-editbox-notes`)

- Setup: Mod b9ui with a descriptor.mod, enabled, new 1936 game as GER. File common/scripted_guis/b9.txt: scripted_gui = { b9_gui = { context_type = player_context window_name = "b9_window" parent_window_token = top_bar visible = { always = yes } } } . File interface/b9.gui: guiTypes = { containerWindowType = { name = "b9_window" position = { x = 300 y = 200 } size = { width = 700 height = 400 } editBoxType = { name = "e1" position = { x = 0 y = 0 } size = { x = 150 y = 24 } font = "hoi_18mbs" text = "A" } editBoxType = { name = "e2" position = { x = 0 y = 40 } size = { x = 150 y = 24 } font = "hoi_18mbs" text = "B" ignore_tab_navigation = yes } editBoxType = { name = "e3" position = { x = 0 y = 80 } size = { x = 150 y = 24 } font = "hoi_18mbs" text = "C" } } }
- Steps:
  1. Start the game, click into e1, press Tab, type X, press Tab, type Y. Screenshot.
  2. Read error.log for lines that name ignore_tab_navigation.
- Expected: If the key works, Tab skips e2, so X lands in e2 only when clicked and e3 gets the Tab focus. If Tab visits e2 like the others, or error.log rejects the key, the key does nothing or is unknown.
- Run 2026-11-02: tried, inconclusive because `ignore_tab_navigation` loaded without a message, and Tab behaviour needs keyboard input in the interface.

**G144.** meaning of `dropDownBoxType`, `gridBoxType`, `positionType`, `browserType` (read from names) (kit block `if-other-types`)

- Setup: No mod. New game as GER.
- Steps:
  1. Open the Division Designer (interface/divisiondesignerview.gui uses dropDownBoxType), click a dropdown and screenshot.
  2. Open the production view (gridBoxType) and screenshot.
  3. Note that browserType (interface/browser.gui) and positionType have no simple way to open here, and leave them untested.
- Expected: The dropdown opens and closes and the grids lay out slots in rows. A different result means the name-based meaning is wrong.

#### Localisation

`hoi4_wiki/localisation.md`

**G146.** Both 'Could not find coloring for character' messages are written to a log for an unknown colour letter. (kit block `loc-colour-codes`)

- Setup: Test mod b6loc. events/b6.txt: `add_namespace = b6` newline `country_event = { id = b6.1 title = b6_t desc = b6_d is_triggered_only = yes option = { name = b6_o } }`. localisation/english/b6_l_english.yml (UTF-8 with BOM): `l_english:` then ` b6_t:0 "T"`, ` b6_o:0 "ok"`, ` b6_d:0 "A §Zred§! B"`.
- Steps:
  1. Start a new game with the mod, play GER.
  2. Open the console and run `event b6.1 GER`.
  3. Read logs/error.log and logs/text.log after the event window shows.
- Expected: A line "Could not find coloring for character 'Z'" in a log confirms the message and that it is logged. No line means the engine ignores the letter silently. Note what the event text looks like.
- Run 2026-11-02: settled that an unknown colour letter logs "Could not find coloring for character" for an event window and for a logged loc key. Remains: the "character id" form.

**G148.** The U format letter upper-cases the first letter, $$100 prints a literal dollar, and the four date getters work. (kit block `loc-variable-formats`)

- Setup: Test mod b6fmt (event b6.1 as in B6-04). Loc file with BOM: ` b6_o:0 "ok"`, ` b6_t:0 "T"`, ` b6_d:0 "$b6_o|U$ / $$100 / [?global.date.GetDateString] / [?global.date.GetDateStringNoHour] / [?global.date.GetDateStringNoHourLong] / [?global.date.GetDateStringShortMonth]"`.
- Steps:
  1. Start a new game, play GER.
  2. Run console command `event b6.1 GER`.
  3. Take a screenshot of the event window and read logs/error.log.
- Expected: 'Ok' at the start means U upper-cases. '$100' with one dollar sign means $$ escapes. Four date strings mean the getters work. Literal `[?...]` text or an error line for a getter means it is not valid. Record each result separately.
- Run 2026-11-02: settled `$$100` (prints `$100`) and the four date getters. Remains: `|U`. `$key|U$` gave an empty string, the same reference without `|U` was not tested, and the result is from the log, not from an event window.

**G149.** $ORDER$ in WAR_NAME is the war's ordinal built from ST, ND, RD, TH. (kit block `loc-war-name-keys`)

- Setup: Test mod b6war. events/b6.txt: `add_namespace = b6` newline `country_event = { id = b6.2 title = b6_t desc = b6_d is_triggered_only = yes option = { name = b6_o GER = { declare_war_on = { target = POL type = annex_everything } } } }` plus loc keys b6_t, b6_d, b6_o.
- Steps:
  1. New game, 1936, play GER.
  2. Console: `event b6.2 GER`, choose the option.
  3. Read the war name in the war panel or the declaration notification.
- Expected: A name with an ordinal prefix only for a repeat war between the same pair supports the claim. Any other use of $ORDER$ means the guess is wrong.

#### Map modding

`hoi4_wiki/map_modding.md`

**G151.** What map/colors.txt is used for. (kit block `map-folder-1193`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). map/colors.txt: 200 lines "color = { 255 0 255 }".
- Steps:
  1. Launch with the mod, start a new 1936 game as GER.
  2. Run: mapmode 0, then mapmode 1 up to 12 one by one, take a screenshot of each (look for magenta).
  3. Repeat without the mod and compare.
- Expected: Magenta that appears only with the mod shows where the colour list is used (for example random or per-state colours). If every screenshot is unchanged, the file is unused in these views.

**G153.** The exe error texts for definition.csv and provinces.bmp (no continent, no pixels) are produced, and the corrected-copy file name. (kit block `map-definition-facts`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). map/definition.csv: vanilla copy with the last field of province 2 ("2;0;0;55;land;false;forest;1") changed to 0.
- Steps:
  1. Delete error.log and launch with the mod, start 1936 as GER.
  2. Read error.log.
  3. Then replace the file with a copy that deletes the line of province 3 and read the log again.
  4. Also look in the user folder Documents/Paradox Interactive/Hearts of Iron IV/ for any file ending .fixed.csv.
- Expected: A line like "prov 2 has no continent" and a "has no pixels in provinces.bmp" line for the second copy confirm the texts are produced. A .fixed.csv file shows the real corrected-copy name; no such file means the string is unused.
- Run 2026-11-02: settled the "has no continent" and "has no pixels in provinces.bmp" texts. Remains: the name of the corrected copy (no `.fixed.csv` appeared in the folders searched, but the runner kept no before-and-after file list).

**G157.** The frame_border_* ambient objects are the visible map frame; time_duration is a known key. (kit block `map-ambient-facts`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). map/ambient_object.txt: vanilla copy with the frame_border_entity position changed to 0 0 2500 and time_duration = 5 added to the ambient_wind_entity block.
- Steps:
  1. Launch with the mod, start 1936 as GER, zoom out to the northern map edge and take a screenshot.
  2. Repeat without the mod. Read error.log.
- Expected: The northern frame moving shows it is the frame. An unknown-key line for time_duration shows the key is not read; no line suggests it is accepted.
- Run 2026-11-02: tried, inconclusive because `time_duration = 5` drew no error.log line, which cannot tell accepted from silently ignored, and the frame position needs a screenshot.

#### Map mode modding

`hoi4_wiki/map_mode_modding.md`

**G158.** Scripted map modes: folder is read by the engine, six hard-coded layer names, 0..1 colour channels, gradient from a computed value, console mapmode number, the minimal example works (kit block `(kit page)`)

- Setup: Mod folder b7mm with the page's minimal example: common/map_modes/my_mod_map_modes.txt, localisation/english/my_mod_map_modes_l_english.yml and interface/my_mod_map_modes.gfx with the two GFX_mapmode_buttons_*_small_my_mod_stability sprites (point both at gfx/interface/mapmode/mapmode_buttons_selected_small.dds and the deselected one). Add a second map mode `b7_fac = { top = { type = game_map_mode_factions } bottom = { type = none } far_text = none near_text = none update_daily = no }` with the same loc and sprite pattern for id b7_fac. Delete error.log first.
- Steps:
  1. Start 1936.1.1 as GER with the mod. Look at the map mode bar and the 'all map modes' window for 'Stability' and the second mode.
  2. Select each with the mouse. Note the colours of the major countries.
  3. Run `mapmode 1` and then increase the number by one at a time up to 40, noting which number selects each scripted mode.
  4. Edit the stability channel formula to `set_temp_variable = { green = 2 }` (out of range), run `rebuildlayers` and look at the map.
  5. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log.
- Expected: If the engine reads the folder, both modes appear and the first colours GER-led majors red to green by stability (a computed gradient works). The second shows the vanilla faction colours (the hard-coded layer name is accepted). The number tests give the console index of each scripted mode. The out-of-range value shows whether channels clamp, wrap or break. No entry in the bar means the folder or sprites are wrong, so read error.log first.
- Run 2026-11-02: tried, inconclusive. Three scripted map mode ids raised no error and logged no `color` line after `force_update_map_mode`, and `mapmode 12` to `mapmode 20` answered "Unknown mapmode" (read by OCR). `rebuildlayers` replied "Gradient borders rebuilt." Remains: whether the folder is read and how a scripted mode is selected (`mapmode 0` and names were not tried).

**G159.** if/limit inside color, targets with target_array and target_trigger, and bare FROM in target_trigger (kit block `(kit page)`)

- Setup: Mod folder b7mm2 with loc and sprites as in B7-13 for ids b7_a, b7_b and b7_c. common/map_modes/b7.txt: b7_a = type country, `targets = { target_array = global.majors }`, `color = { if = { limit = { FROM = { is_major = no } } } set_temp_variable = { red = 1 } set_temp_variable = { alpha = 1 } }`. b7_b = type country, `targets = { target_trigger = { FROM = { original_tag = GER } } }`, `color = { set_temp_variable = { green = 1 } set_temp_variable = { alpha = 1 } }`. b7_c = type country, `targets = { targets = { GER ENG } }`, same color. Each file has `bottom = { type = none } far_text = none near_text = none update_daily = no`.
- Steps:
  1. Start 1936.1.1 as GER with the mod and select each mode in the map mode bar (or `mapmode` with the number found in B7-13).
  2. For each, note which countries are coloured.
  3. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log.
- Expected: b7_a: only the majors drawn and an `if` with an unmet limit does not hide non-majors if every major is also drawn red (limit ignored) or hides them if only matching ones are drawn. b7_b: only Germany green means a bare FROM is the drawn country. b7_c: only Germany and England coloured means `targets` works as in targeted decisions. Errors in the log name the key the engine does not accept.
- Run 2026-11-02: tried, inconclusive because the mode could only be selected through `mapmode N`, which was refused, so the log lines of the `color` blocks never ran.

**G160.** Whether a scripted mode's own sprite must use the vanilla 20 by 18 frame size (kit block `(kit page)`)

- Setup: Mod folder b7mm3 with the B7-13 stability mode. Two sprites for its button: variant A a one-frame 20 by 18 DDS, variant B a one-frame 64 by 64 DDS, each as `spriteType = { name = "GFX_mapmode_buttons_selected_small_my_mod_stability" texturefile = "gfx/interface/b7_btn.dds" }` with the deselected sprite defined the same way.
- Steps:
  1. Start the game with variant A and look at the button in the map mode bar. Repeat with variant B.
  2. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log.
- Expected: If the size does not matter, both buttons show (variant B scaled or cropped). A broken or empty button for B means the vanilla size is required or the sprite needs `noOfFrames`.

#### Military industrial organization modding

`hoi4_wiki/military_industrial_organization_modding.md`

**G162.** With ENABLE_TASK_CAPACITY false, task_capacity (and its modifier and effect) limit nothing. (kit block `mio-key-checks`)

- Setup: New game, 1936 start, play as GER, one test mod. File common/military_industrial_organization/organizations/b2_mio.txt: b2_task_mio = { allowed = { original_tag = GER } equipment_type = { infantry_equipment } research_categories = { infantry_weapons } task_capacity = 1 initial_trait = { limit_to_equipment_type = { infantry_equipment } equipment_bonus = { soft_attack = 0.1 } } }. Run A uses the mod as is. Run B adds common/defines/b2_defines.lua with the single line NDefines.NIndustrialOrganisation.ENABLE_TASK_CAPACITY = true
- Steps:
  1. Run A: start with the mod, open the Military-Industrial Organisations screen and select b2_task_mio. Note any task capacity it shows.
  2. Assign a design team of b2_task_mio to an infantry_weapons technology, then try to assign the same MIO to a second task (a production line manufacturer or an equipment variant design). Record whether the second assignment is allowed. Read error.log.
  3. Run B: restart with the defines file and repeat the same two assignments.
- Expected: If run A allows the second task and run B refuses it, ENABLE_TASK_CAPACITY = false makes task_capacity inert, as the wiki says. If run A also refuses the second task, task_capacity applies with the switch off and the wiki sentence is wrong. If no run shows a capacity, compare only the assignment results.
- Run 2026-11-02: settled `task_capacity` itself (inert with the switch off, enforced with it on). Remains: the modifier `military_industrial_organization_task_capacity` and `add_mio_task_capacity`.

**G163.** A trait block that repeats an inherited token with only limit_to_equipment_type replaces the inherited trait or adds a second one. (kit block `mio-trait-notes`)

- Setup: New game, 1936, play as GER, one mod. File common/military_industrial_organization/organizations/b2_child.txt: b2_child = { include = generic_heavy_tank_organization allowed = { original_tag = GER } trait = { token = generic_mio_trait_wide_tracks limit_to_equipment_type = { heavy_tank_chassis } } }
- Steps:
  1. Start the game, open the MIO screen and select b2_child.
  2. Count the trait boxes named for generic_mio_trait_wide_tracks (hover each one and note its equipment list).
  3. Read error.log for the MIO loader.
- Expected: One box with the limited equipment list means the repeated token replaces the inherited trait. Two boxes, or one box with both lists, mean it adds a second trait. A logged duplicate-token error means the form is rejected.
- Run 2026-11-02: tried, inconclusive because the file loaded without an error, but the trait box count is shown only in the interface.

**G165.** A production stat inside a policy equipment_bonus does not apply to a production line. (kit block `mio-policies-notes`)

- Setup: New game, 1936, play as GER, no mod. Vanilla policy mio_policy_land_heavy_gantry_cranes (production_efficiency_cap_factor 0.05 inside equipment_bonus). Console: pp 500 (adds political power, see console_commands_documentation.md).
- Steps:
  1. Run pp 500. Open an armor MIO of size above 5 (the policy needs has_mio_size > 5) and attach the policy.
  2. Assign that MIO as manufacturer to a production line of a heavy tank or train_equipment variant.
  3. Open the production line tooltip, read the efficiency cap with and without the policy attached and take screenshots.
- Expected: A cap that rises by 5 points with the policy means equipment_bonus accepts the production stat. No change means the stat only works in production_bonus and the wiki advice stands. If the policy cannot be attached, record the check as unavailable.

**G167.** A category or equipment group is accepted as an ai_bonus_weights key, not only an archetype. (kit block `mio-ai-weights`)

- Setup: New game, 1936, GER, one mod. File common/military_industrial_organization/ai_bonus_weights/zz_b2.txt holds a copy of the whole vanilla default block (so every stat keeps a weight) plus the blocks infantry_equipment = { soft_attack = 9.999 } and mio_cat_eq_all_medium_tank = { soft_attack = 9.999 }
- Steps:
  1. Start the game with the mod and run one in-game month.
  2. Read error.log and game.log for lines naming infantry_equipment or mio_cat_eq_all_medium_tank.
- Expected: No error for either key suggests both are accepted. An error for mio_cat_eq_all_medium_tank only means groups and categories are refused and only archetypes work. An error for both means even the doc example key is refused.
- Run 2026-11-02: tried, inconclusive because the file with category and equipment group keys loaded without an error, but no line shows the AI using the weights.

**G168.** A trait bonus naval_dominance_factor is accepted and naval_supremacy_factor is not. (kit block `mio-equipment-stats`)

- Setup: New game, 1936, GER, one mod. File common/military_industrial_organization/organizations/b2_naval.txt: b2_naval_mio = { allowed = { original_tag = GER } equipment_type = { ship_hull_light } research_categories = { naval_techs } initial_trait = { limit_to_equipment_type = { ship_hull_light } equipment_bonus = { naval_dominance_factor = 0.1 } } }
- Steps:
  1. Start the game, read error.log for the MIO loader.
  2. Open the MIO screen and hover the initial trait of b2_naval_mio.
  3. Change the stat to naval_supremacy_factor and repeat.
- Expected: naval_dominance_factor in the tooltip with a clean log, and an error for naval_supremacy_factor, means the stat is real and the kit correction is right. Errors for both mean the stat cannot be used.
- Run 2026-11-02: settled that both names are rejected as an unexpected token in an `initial_trait` of a `screen_ship` organisation. Remains: a capital-ship organisation, another trait, and the tooltip.

#### Modding

`hoi4_wiki/modding.md`

**G172.** A userdir.txt in the game folder is the old way to move the user directory and gameDataPath wins. (kit block `modding-user-directory-files`)

- Setup: Needs the maintainer, because the game folder is read only for agents. Create C:/b6userdir and put a userdir.txt in the game folder naming it. Leave launcher-settings.json unchanged.
- Steps:
  1. Start the game, quit.
  2. Check whether C:/b6userdir is populated and whether a log has 'Custom user directory configured in the old style' and 'Overridden by the gameDataPath field'.
  3. Delete userdir.txt afterwards.
- Expected: Message present and C:/b6userdir empty: gameDataPath wins as the page says. C:/b6userdir populated: userdir.txt wins.

**G173.** The listed file and folder names are really used, and dlc_load.json holds enabled_mods and disabled_dlcs. (kit block `modding-user-directory-files`)

- Setup: No mod. Record the content of Documents/Paradox Interactive/Hearts of Iron IV/ (file names, folders) before the run.
- Steps:
  1. In the launcher enable a test mod and disable one DLC, start the game to the main menu, then quit.
  2. List the folder again and open dlc_load.json and mods_registry.json.
  3. Check which names from the claim exist.
- Expected: Names present are used. Absent ones are unused or created on demand (record which). dlc_load.json with enabled_mods and disabled_dlcs confirms the mods.md text.
- Run 2026-11-02: tried, inconclusive because the scratch user folder is a long-lived copy with no before listing, so the listing cannot show which names the game created. A `disabled_dlcs` entry written as the DLC display name or as the path form `dlc/dlc038_arms_against_tyranny/dlc038.dlc` did not disable the DLC (system.log still listed it active), so the accepted form was not found. The game was started without the launcher and may take DLC state from the launcher or Steam instead of `dlc_load.json`.

**G174.** A Workshop item gets a user file named ugc_<id>.mod and editor_postfix is a real setting. (kit block `modding-descriptor-keys`)

- Setup: Maintainer only: needs a Steam Workshop subscription to any HOI4 mod.
- Steps:
  1. Subscribe to a small Workshop mod, let Steam download it, start the game once.
  2. List Documents/Paradox Interactive/Hearts of Iron IV/mod/ for ugc_<id>.mod files.
  3. Open settings.txt if present and look for editor_postfix.
- Expected: A file ugc_<number>.mod matches the format string. A different name means the pattern is wrong. editor_postfix in settings.txt confirms that key.

**G175.** The two map/terrain .bmp files count toward the checksum. (kit block `modding-load-facts`)

- Setup: Test mod b6sum overriding map/terrain/Tree_tint.bmp with a byte-different copy. Control: the mod disabled.
- Steps:
  1. Start without the mod and note the checksum shown in the main menu or in logs/game.log.
  2. Start with the mod and note it again.
- Expected: A different checksum means the engine counts the .bmp. The same checksum means it does not.
- Run 2026-11-02: settled `Tree_tint.bmp` (a changed byte changes one of the 91 values in the `dump_checksum` file). Remains: `Tree_season.bmp` and what each slot stands for.

**G176.** What the other launch options do, including dump_script_doc. (kit block `modding-launch-options`)

- Setup: No mod. Give launch options in the Steam launch options box, one per run.
- Steps:
  1. Run with `-dump_script_doc` and compare the timestamps of the files in documentation/ afterwards.
  2. Run with `-suppress_error_log` and check whether error.log is still written.
  3. Run with `-nofilewatcher`, edit a script file while running and see whether the edit is picked up.
- Expected: documentation/ files rewritten: dump_script_doc regenerates them. For the others record the observed effect or 'no visible effect'.
- Run 2026-11-02: tried, inconclusive because `-dump_script_doc` was not run (it may write into the install documentation folder) and every launch also used `-debug`. `-nofilewatcher` stopped the live reload of an edited scripted effect and `-suppress_error_log` had no visible effect on error.log in that launch.

**G177.** user_dir moves the save folder and dependencies forces load order. (kit block `modding-descriptor-keys`)

- Setup: Test mods b6a and b6b. b6a descriptor: `name="b6a"` `user_dir="b6dir"`. b6b: `name="b6b"` `dependencies={"b6a"}`. Both with common/defines/zz.lua setting STARTING_COMMAND_POWER to different values.
- Steps:
  1. Enable only b6a, start the game, quit, and look for Documents/Paradox Interactive/Hearts of Iron IV/b6dir.
  2. Enable b6b before b6a in the playset and check which define value wins.
- Expected: A b6dir folder confirms user_dir. b6b loading after b6a whatever the playset order confirms dependencies.
- Run 2026-11-02: tried, inconclusive because the `user_dir` folder only appeared empty at start (no save was made) and the load-order half needs two mods in one launch. A `dependencies` entry naming a mod that is not enabled loaded the mod without a message.

#### Modifiers

`hoi4_wiki/modifiers.md`

**G178.** Dynamic modifier definitions need a game restart to be re-read. (kit block `dynamic-scopes`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). common/dynamic_modifiers/b8.txt: b8_dyn = { stability_factor = 0.1 }
- Steps:
  1. Launch with the mod, start 1936 as GER, run: tag GER; eval_effect add_dynamic_modifier = { modifier = b8_dyn }; note the stability line in the tooltip.
  2. Edit the mod file on disk to stability_factor = 0.5, then run reloadinterface, reloadtechnologies, reloadoob in turn.
  3. Check the tooltip, then load a save made before the edit.
- Expected: If the tooltip shows 50 percent after a reload command, no restart is needed. If it shows 10 percent until a full restart, the restart claim holds.

**G181.** target = yes on an opinion modifier changes how it applies. (kit block `opinion-vanilla`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). common/opinion_modifiers/b8.txt: opinion_modifiers = { b8_a = { value = 35 target = yes } b8_b = { value = 35 } }
- Steps:
  1. Start 1936 as GER, run: tag GER; eval_effect add_opinion_modifier = { target = ENG modifier = b8_a }; eval_effect add_opinion_modifier = { target = FRA modifier = b8_b }
  2. Open the diplomacy screen for ENG and FRA and read the opinion tooltips each way.
- Expected: If the two tooltips differ in direction or visibility, target = yes changes how it applies. If both look the same, there is no visible difference.
- Run 2026-11-02: tried, inconclusive because `add_opinion_modifier` showed only the plain entries, and the `target = yes` entry may apply only through a game action that was not exercised.

**G182.** annex_cost_factor and puppet_cost_factor still change peace conference costs. (kit block `annex-puppet-status`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). common/ideas/b8.txt: ideas = { country = { b8_ann = { modifier = { annex_cost_factor = -0.9 } } } }
- Steps:
  1. Start 1936 as GER, run: tag GER; add_ideas b8_ann; eval_effect declare_war_on = { target = POL type = annex_everything }
  2. Run: debug_force_capitulate POL, advance one day, open the peace conference and note the annex cost of Polish states.
  3. Repeat without the idea.
- Expected: A lower cost with the idea shows the modifier still works. Equal costs show it is dead.

#### Music modding

`hoi4_wiki/music_modding.md`

**G183.** limit of 63 characters on a song name (kit block `music-song-notes`)

- Setup: Mod b9mus. File music/b9.asset: two `music = { name = "..." file = "hoi4mainthemeallies.ogg" volume = 0.5 }` blocks, one with a 63 letter name and one with a 64 letter name. An event b9.1 with two options, each `play_song` of one name.
- Steps:
  1. Start the game as GER, run `event b9.1`, pick each option in turn.
  2. Read error.log after each.
- Expected: Both names play with no log line if there is no limit. A refused or logged 64 letter name means the limit is 63.
- Run 2026-11-02: tried, inconclusive because neither the 63 nor the 64 character name was found ("Song doesnt exist"), because the asset had no entry in a station list.

**G185.** `modifier` triggers run in country scope; a bare `factor` modifier applies in every case (kit block `music-chance-notes`)

- Setup: Mod b9mus3. File music/b9_songs.txt: music = { song = "b9_song" chance = { modifier = { factor = 1000 original_tag = GER } } } and a second block for "b9_song2" with chance = { modifier = { factor = 1000 } } . File music/b9.asset defines both names with a vanilla .ogg.
- Steps:
  1. Start as GER, let the music change songs several times (or use the in-game music player) and note the titles.
  2. Repeat after `tag ITA`.
- Expected: b9_song plays as GER and not as ITA if the trigger runs in country scope. b9_song2 plays for both, so a bare factor applies in every case.

#### Namelist modding

`hoi4_wiki/namelist_modding.md`

**G186.** the engine also accepts `fallback_Name` (kit block `namelist-ship-notes`)

- Setup: Mod b9nm. File common/units/names_ships/b9.txt: two GER groups, `type = ship ship_types = { ship_hull_light destroyer } unique = { "Alpha" } fallback_Name = "Spare"` and the same with `fallback_name`. Add a for_countries = { GER } line to each (the second group in a second file).
- Steps:
  1. Start as GER, build three destroyers (give the equipment and ships with a scripted effect) and read the ship names.
  2. Swap the spellings between the groups and repeat.
- Expected: The third ship is named Spare in the lower-case group. If it is named Spare with the capital N too, the spelling is accepted. If it gets another fallback name, the capital N is ignored.

**G187.** the first `ship_types` token is Man the Guns, the second the older type (kit block `namelist-ship-notes`)

- Setup: Man the Guns DLC on, mod b9nm2. File common/units/names_ships/b9.txt: a GER group with ship_types = { ship_hull_light } and unique = { "MtgName" }, a second with ship_types = { destroyer } and unique = { "OldName" }.
- Steps:
  1. Start as GER, make a Man the Guns light hull destroyer and read its name.
  2. Make an older destroyer and read its name.
- Expected: The new hull is named MtgName and the older type OldName if the wiki claim holds. Swapped or mixed names mean it is wrong.

#### National focus modding

`hoi4_wiki/national_focus_modding.md`

**G189.** Messages and effects for one-way exclusive focuses, relative position errors, missing icons, no default icon case, and overlay (kit block `focus-icon-extras`)

- Setup: Mod folder b5_test with descriptor.mod. File common/national_focus/b5_f2.txt: focus_tree = { id = b5_t2 country = { factor = 0 modifier = { add = 1000 tag = LUX } } focus = { id = b5_a x = 0 y = 0 cost = 1 icon = GFX_b5_no_icon mutually_exclusive = { focus = b5_b } relative_position_id = b5_late overlay = GFX_goal_unknown } focus = { id = b5_b x = 2 y = 0 cost = 1 icon = { GFX_goal_unknown = { always = no } } } focus = { id = b5_late x = 4 y = 0 cost = 1 icon = GFX_goal_unknown relative_position_id = b5_a } }
- Steps:
  1. Start a new game, 1936 start, play as LUX, with only b5_test enabled.
  2. Read error.log and search for b5_a, b5_b, b5_late and Missing icon.
  3. Open the focus tree and screenshot b5_a (look for the overlay image on its icon).
- Expected: Lines for the one-way exclusive link, the missing icon and icon shine of b5_a, the relative focus defined later and the circular reference, and the missing default icon case of b5_b confirm the messages. An image drawn on top of the b5_a icon confirms overlay. A line missing means its condition differs.
- Run 2026-11-02: settled the load messages. Remains: the `overlay` image (needs the interface) and a circular-only `relative_position_id` case, because the test tree held both a forward and a circular reference.

#### Nudger

`hoi4_wiki/nudger.md`

**G194.** The Buildings section writes map/buildings.txt in the user directory; Mark/Unmark, Random and Validate behave as their labels say; the marker file holds the marks. (kit block `nudger-buildings`)

- Setup: No mod. Note the modified time of the file buildings_nudger_markers.txt in the game folder.
- Steps:
  1. Run: nudge, open Buildings, pick a state, press Random, then Mark/Unmark on one model, then Validate, then Save.
  2. List files changed in the user folder Documents/Paradox Interactive/Hearts of Iron IV and in the game folder map/.
  3. Open the marker file and the written buildings.txt.
- Expected: The location of the written buildings.txt confirms the inferred path. Changed marker file bytes confirm the marker purpose. Random moving models and Validate reporting issues confirm the label reading.
- Run 2026-11-02: not run, because `buildings_nudger_markers.txt` is in the game install folder, so marking and saving would write there. Needs a disposable game install or the maintainer's go-ahead.

**G195.** A new state without building rows in buildings.txt crashes the game. (kit block `nudger-buildings`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). history/states/9999-B8.txt: a copy of 64-Brandenburg.txt with id = 9999 and two unused provinces, plus the states for them so the map stays valid. No buildings rows.
- Steps:
  1. Launch with the mod and start 1936 as GER.
  2. Read error.log and game.log. If the game crashes, note the last log lines.
- Expected: A crash or a log line about missing building rows confirms the page. A normal start with only a log line means the effect is a warning.

**G196.** The strategic region nudger buttons do what their labels say. (kit block `nudger-strategic-regions`)

- Setup: No mod. New 1936 game as GER.
- Steps:
  1. Run: nudge, open the strategic regions panel.
  2. Press each button once on a copy region, screenshot after each press, do not save.
- Expected: The screenshots show what each button does. If the result differs from its label, the label reading is wrong.
- Run 2026-11-02: tried, inconclusive because only the panel layout was observed. Clicking Eastern Germany opened a panel with the name field, Open File (it showed nothing), Delete region, Update, Save, a Naval Terrains list (Default, Ocean, Fjords and Archipelagos, Shallow Sea, Deep Oceans) and a Modifiers block (Name, Trigger, Update, Delete). Update, Save, Delete region and the terrain and modifier buttons were not pressed, because debug tools can write into the game install at once.

**G197.** The Units section writes map/unitstacks.txt; Auto in Prov and Auto in All generate positions; unit_nudger_markers.txt holds the marks. (kit block `nudger-units`)

- Setup: No mod. Note the modified time of unit_nudger_markers.txt in the game folder.
- Steps:
  1. Run: nudge, open Units, select a province, press Auto in Prov, then Mark/Unmark, then Save.
  2. List files changed in the user folder and in the game folder map/.
- Expected: The written unitstacks.txt location confirms the path. New positions confirm Auto. Changed bytes in the marker file confirm its purpose.
- Run 2026-11-02: not run, for the same reason as G194. `unit_nudger_markers.txt` is in the game install folder. Needs a disposable game install or the maintainer's go-ahead.

#### Occupation and resistance modding

`hoi4_wiki/occupation_and_resistance_modding.md`

**G198.** Resistance target formula and unit mix (kit block `(kit page)`)

- Setup: No mods. Start 1936, play GER.
- Steps:
  1. Run `effect GER b3_annex` with `annex_country = { target = AUS }` or use `annex`, then wait one day.
  2. Open the state's occupation tooltip and read the resistance target breakdown.
  3. Add the `resistance_target` modifier by an idea of 0.1 and read it again.
- Expected: The tooltip breakdown lists each component; compare its sum to the defines and the modifier to see the formula and units.
- Run 2026-11-02: tried, inconclusive because an idea with `resistance_target = 0.1` raised the target of six states by exactly 10, but the tooltip breakdown and the formula were not read.

**G199.** Resistance activity roll timing, and ROOT and FROM inside activity effects (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. common/resistance_activity/zz_b3.txt: `b3_probe = { available = { always = yes } weight = { base = 1000 } max_amount = 1 duration = 10 effect = { log = "B3 act ROOT=[Root.GetName] FROM=[From.GetName] THIS=[This.GetID]" } }`.
- Steps:
  1. Occupy a state, for example `declare war` through a scripted effect on POL, then `debug_force_capitulate POL`.
  2. Use `resistance 100` on the state if needed to raise resistance.
  3. Run `fast_forward 60` and read game.log for the B3 lines and their dates.
- Expected: The spacing of B3 lines gives the roll timing. The printed Root and From names show what ROOT and FROM are.
- Run 2026-11-02: settled `ROOT`, `THIS` and `FROM` and that activities start on the 01:00 tick. Remains: the roll interval, which these lines do not isolate.

**G200.** What alert_level and alert_margin do (kit block `(kit page)`)

- Setup: No mods. An occupied state with resistance near 90.
- Steps:
  1. Use `resistance 100` on the state, then wait a day.
  2. Look at the map for an alert and at the state's alert list.
  3. Lower resistance below 70 and look again.
- Expected: An alert appearing at 90 and clearing near 70 matches level high and margin 20.

#### On actions

`hoi4_wiki/on_actions.md`

**G205.** Which wiki-only and exe-only hook names the engine knows, and whether a misspelled hook name is reported. (kit block `onaction-inventory`)

- Setup: Test mod b6hn. common/on_actions/zz_n.txt with one block per name, each `effect = { log = "B6 name" }`: `on_b6_fake` (control), `on_stage_coup`, `on_guarantee`, `on_military_access`, `on_offer_military_access`, `on_lend_lease`, `on_incoming_lend_lease`, `on_send_expeditionary_force`, `on_return_expeditionary_forces`, `on_request_expeditionary_forces`, `on_ask_for_state_control`, `on_give_state_control`, `on_peace_proposal`, `on_send_attache`, `on_generate_wargoal`, `on_state_owner_changed`, `on_become_faction_member`, `on_subject_annex`, `on_mio_tech_reseach_completed`, `on_mio_tech_research_completed`.
- Steps:
  1. Start a new game with the mod and read logs/error.log at the main menu and after one day.
  2. For each name with no error, do the action in game when known (guarantee and military access in the diplomacy panel, peace proposal at a peace conference) and read game.log for the line.
- Expected: If error.log complains about on_b6_fake only, a name with no complaint is known to the engine, and a name that is also reported does not exist. If nothing complains, unknown names are silent, so only a firing 'B6' line proves a hook exists.

**G206.** ROOT and FROM scopes of on_recall_volunteers (on_force_government has no known trigger). (kit block `onaction-diplomacy`)

- Setup: Test mod b6rv. common/on_actions/zz_r.txt: `on_actions = { on_recall_volunteers = { effect = { log = "B6 root [Root.GetTag] from [From.GetTag]" } } }`.
- Steps:
  1. New game, play GER, send volunteers to a country at war in the diplomacy panel.
  2. Recall them, then read game.log.
- Expected: The log line gives the ROOT and FROM tags. on_force_government stays unchecked.
- Run 2026-11-02: tried, inconclusive because no AI country sent volunteers to BHU in 35 days, so neither hook fired.

#### Particle modding

`hoi4_wiki/particle_modding.md`

**G207.** the trimmed lamp particle and its `particles.gfx` entry run (kit block `particle-add-chain`)

- Setup: Mod b9par with the two example files of block `particle-add-chain` copied unchanged (gfx/particles/my_glow.asset and gfx/entities/my_particles.gfx as given in that block). Attach `my_glow_particle` to a vanilla entity event copied into the mod (particle = "my_glow_particle").
- Steps:
  1. Start the game and trigger that entity.
  2. Screenshot the glow and read error.log.
- Expected: A red glow appears with no particle error, so the trimmed form runs. No glow, or an error that names a missing key, means a dropped key is needed.

**G208.** meaning of `{ a b }` pairs and of a name after a comma (kit block `particle-subsystem-keys`)

- Setup: Mod b9par2: a renamed copy of gfx/particles/lamp_red.asset attached as in the previous particle check, with `size = { 1 3 }` in variant one and `size = 2` in variant two.
- Steps:
  1. Start the game, trigger the particle ten times and screenshot each.
  2. Compare with variant two.
- Expected: A random range gives sizes that differ between emissions inside 1 to 3. A start and end value gives particles that grow from 1 to 3 over their life. Constant sizes mean the pair is neither.

**G209.** the particle editor commands exist in 1.19.4.1 and the editor works (kit block `particle-editor-warning`)

- Setup: No mod. New 1936 game as GER.
- Steps:
  1. Open the console, type `particle_editor create b9_test` and read the reply.
  2. If it is accepted, type `add_subsystem`, `save`, then `exit`.
  3. Look for a new .asset file in the Hearts of Iron IV user folder and read error.log.
- Expected: Each command is accepted or answered as unknown. Accepted commands and a written file show that the editor exists in the release build. A refused `particle_editor` means the exe strings are not live.
- Run 2026-11-02: settled that `particle_editor` exists and that `particle_editor create <name>` writes an invalid `gfx/particles/<name>.asset` into the install folder at once (see the warning on the page). Remains: `add_subsystem`, `save`, `exit` and the editor window, not run to avoid more writes into the install.

**G210.** `intensity = <n>, fade` applies the animation to the intensity (kit block `particle-light-corrections`)

- Setup: Mod b9light. File gfx/entities/map_lights.asset: a vanilla copy where `muzzle_flash` has intensity `15, fade` in variant one and `15` in variant two.
- Steps:
  1. Start the game and watch infantry fire in a battle on the map, capturing a screenshot sequence of one flash.
  2. Compare the two variants.
- Expected: With `, fade` the flash dims over its life. With the plain number it keeps one brightness for the whole event. The same look in both means the suffix does nothing.

#### Peace conference modding

`hoi4_wiki/peace_conference_modding.md`

**G211.** ROOT is the top-level negotiator; FROM per action type (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. common/peace_conference/ai_peace/zz_b3.txt with one entry per action type (take_states, puppet, liberate, force_government), each `enable = { FROM = { tag = POL } }` and a second variant `FROM.FROM = { tag = POL }`, each with ai_desire = 5000. GER vs POL, ENG, and a liberated country.
- Steps:
  1. Declare war on POL by `effect GER b3_war`, then `debug_force_capitulate POL`.
  2. Observe the AI's conference actions in the UI.
  3. Repeat with each variant and compare which variant takes effect.
- Expected: The variant that activates shows which country FROM or FROM.FROM names for that action type. Compare with the table in the page.

**G212.** Whether a mod can target take_navy (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. common/peace_conference/cost_modifiers/zz_b3.txt: `b3_navy = { peace_action_type = take_navy enable = { always = yes } cost_modifier = 5 }` (copy the structure from vanilla).
- Steps:
  1. Start the game and read error.log.
  2. Reach a conference where a navy can be taken and look at its cost.
- Expected: An error naming take_navy shows the type is invalid. A cost change shows it works.
- Run 2026-11-02: tried, inconclusive because a cost modifier with `take_navy` and one with an invented type both loaded without a message, and no conference with a navy to take was reached.

**G213.** Result of an undefined category key (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. Cost modifier entry with `category = b3_nonexistent_category`.
- Steps:
  1. Start the game and read error.log.
  2. Open a conference and read the cost tooltip.
- Expected: A named error, a crash or a missing tooltip line shows the effect. No error means unknown categories are ignored.
- Run 2026-11-02: tried, inconclusive because the undefined category drew no log line and no crash, but the block wrote `peace_action_type = { take_states }` where vanilla writes the scalar form and the conference tooltip was not opened, so "ignored" is not shown.

**G214.** Meaning of faction_modifier = yes (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. Two copies of one cost modifier in zz_b3.txt, one with faction_modifier = yes, active only for a faction member.
- Steps:
  1. Run a conference as a faction member.
  2. Compare the cost tooltip between copies.
- Expected: A different tooltip or cost shows faction_modifier changes how it is listed or applied.

**G215.** Whether category affects the cost math (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. Two cost modifiers, same multiplier 0.5, in different categories.
- Steps:
  1. Open a conference and note the total cost.
  2. Move both to the same category and note the total again.
- Expected: Identical totals confirm category is display only.

**G216.** Effect of the unreferenced faction_rule_modifier_extra_cost modifiers (kit block `(kit page)`)

- Setup: No mods. A faction with rules that promise a 5 percent extra cost.
- Steps:
  1. Pick the rule whose tooltip promises extra cost on a second action type.
  2. Make a first and second action of different types in one conference and compare the costs.
- Expected: No 5 percent increase on the second action means the modifiers are unused.

**G217.** Whether the enable of a rule-backed faction modifier runs (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. Copy faction_rule_modifier_encourage_take_claimed_states into zz_b3.txt with `enable = { always = no }`.
- Steps:
  1. Run a conference as a member of the faction whose rule is active.
  2. Check whether the modifier appears in the cost tooltip.
- Expected: The modifier still applying despite always = no shows the docs are right. Not applying shows enable is evaluated.

**G218.** Scale of ai_desire, combination and special values (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. ai_peace/zz_b3.txt with one entry `enable = { ROOT = { tag = GER } } peace_action_type = take_states ai_desire = 0` and no other entry for that action. Variants 0, 100, -200, -1000, 1000. Disable vanilla entries by test setup where practical (use an isolated country and conference).
- Steps:
  1. Set up a GER win over POL (`effect GER b3_war`, `debug_force_capitulate POL`).
  2. Let the AI negotiate (observer mode `observe`).
  3. Record what the AI takes for each variant.
- Expected: With 0 and no taking, reading A (additive) is right. With 0 and the AI still taking, reading B (percent) is right. Compare 100 and -200 to see the combination.
- Run 2026-11-02: settled that a single `ai_desire = 0` entry does not stop the action (reading B fits). Remains: the -1000 and 1000 variants.

**G219.** pc_current_score vs pc_total_score, and use outside a conference (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. common/on_actions/b3.txt: `on_peaceconference_ended = { effect = { log = "B3 score [?...]" } }` using variables of both scores. Also a trigger `pc_total_score > 0` in an event outside any conference.
- Steps:
  1. Win a war and run a conference, spending some score.
  2. Read game.log for the two numbers before and after spending.
  3. Call the trigger in a decision outside a conference.
- Expected: Current dropping while total stays shows current is the unspent score. A log error outside a conference shows triggers need a conference.
- Run 2026-11-02: tried, inconclusive because the conference started and ended in the same tick with both scores at 0, because the loser had one state.

**G220.** Whether white_peace and conditional surrender fire conference on actions (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. common/on_actions/b3.txt: `on_peaceconference_started = { effect = { log = "B3 started" } } on_peaceconference_ended = { effect = { log = "B3 ended" } }`.
- Steps:
  1. Run `whitepeace GER POL` during a war.
  2. Read game.log.
  3. Repeat with a conditional surrender by `debug_force_capitulate POL` where the capitulation is conditional.
- Expected: B3 lines after a white peace show the on actions fire. Silence shows they do not.
- Run 2026-11-02: settled white peace and capitulation. Remains: a conditional surrender, because `debug_force_capitulate` gave a normal capitulation.

**G221.** The worked example runs without error (kit block `(kit page)`)

- Setup: Copy the example from the page into a mod and add the focus MYM_reclaim_the_homeland.
- Steps:
  1. Start the game, read error.log.
  2. Reach a conference with the focus done and compare the cost.
- Expected: No error and the expected cost change show the example works.

**G222.** Engine behaviour on peace_action_type = take_state (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. Cost modifier with peace_action_type = take_state and multiplier 0.5.
- Steps:
  1. Start the game, read error.log.
  2. Check the cost of a take-states action.
- Expected: A named error shows the type is rejected. No change in cost shows it is silently ignored.
- Run 2026-11-02: tried, inconclusive because `take_state` loaded without an error, but the modifier was disabled and no conference was opened.

**G223.** Which of two same-named entries wins (kit block `(kit page)`)

- Setup: Test mod folder b3test in Documents/Paradox Interactive/Hearts of Iron IV/mod with descriptor.mod; enable it in the launcher playset. ai_peace/zz_b3.txt with two entries named b3_dup, ai_desire = -1000 for the first and 1000 for the second, same enable.
- Steps:
  1. Run a conference with the AI and watch whether the AI takes the action.
- Expected: The AI taking it means the second wins. Not taking means the first wins.
- Run 2026-11-02: tried, inconclusive because the time step failed in all four variants ("cannot read the in-game date"), so the game stayed at 1936.1.1 and no peace conference ran. Needs a rerun with a working time step.

#### Portrait modding

`hoi4_wiki/portrait_modding.md`

**G225.** portrait continent blocks append across files; random pick order is tag, continent, default (kit block `portrait-references`)

- Setup: Mod b9por. File portraits/04_b9.txt: continent = { name = europe army = { male = { "GFX_Portrait_Africa_Generic_1" } } } . Variant two adds ITA = { army = { male = { "GFX_Portrait_Africa_Generic_1" } navy = { male = { "GFX_Portrait_Africa_Generic_1" } } } } . A scripted effect in the mod that runs create_corps_commander ten times with no portrait given.
- Steps:
  1. Start as a European country that has no tag block in portraits/00_portraits.txt, run the effect with the console command effect and screenshot the generals.
  2. Repeat as a non-European country, then as ITA with variant two.
- Expected: If continent blocks append, the new sprite shows beside the vanilla European portraits. If the block replaces the pool, only the new sprite shows. For the order, the ITA block wins for ITA and a country with no block uses the continent pool.

**G226.** the game looks up the active cosmetic tag for portraits (kit block `portrait-structure`)

- Setup: Mod b9por2. File portraits/04_b9.txt: RAJ_UK = { army = { male = { "GFX_Portrait_Africa_Generic_1" } } } . A scripted effect that sets the cosmetic tag RAJ_UK and one that creates ten generals.
- Steps:
  1. Start as ENG with `tag RAJ`, create generals with the effect and screenshot.
  2. Set the cosmetic tag RAJ_UK and create more generals.
- Expected: The African sprite appears for new generals only while RAJ_UK is active, if the cosmetic tag is looked up.

#### Posteffect modding

`hoi4_wiki/posteffect_modding.md`

**G227.** The 1024 by 32 `lut` strip is a 32 step colour cube (kit block `posteffect-values-notes`)

- Setup: Mod b9lut. File gfx/world/b9_lut.tga: a 1024 by 32 24-bit TGA written with a short Python script as an identity cube of 32 slices of 32 by 32 pixels, except slice 31 painted pure red. File gfx/posteffect_volumes.txt: a copy of vanilla where the `standard` and `default` posteffect_values blocks use lut = "gfx/world/b9_lut.tga".
- Steps:
  1. Start the game as GER and screenshot the map at mid zoom.
  2. Repeat with the red slice moved to slice 0.
- Expected: With 32 slices along x, only one band of one colour channel is tinted red, and moving the slice moves the tint to the other end of that band. A whole-map tint, or no change, means another layout.

**G228.** `posteffect_volume` middle number is height; `height` volumes follow camera zoom (kit block `posteffect-position-notes`)

- Setup: Mod b9pe. File gfx/posteffect_volumes.txt: a copy of vanilla with this volume added inside `posteffect_volumes`: posteffect_volume = { name = b9 posteffect_values_day = blue_water posteffect_values_night = blue_water_night position = { 3000.0 100.0 600.0 } size = { 600.0 800.0 400.0 } fade_distance = 50.0 } . Variant two swaps the second and third numbers of position and size. Variant three changes `Base Medium` height from 900 to 300.
- Steps:
  1. Start the game, move the camera over the map area at x 3000 and z 600 (the map is 5632 by 2048 wide) at low zoom and screenshot.
  2. Zoom out fully and screenshot.
  3. Run variants two and three the same way.
- Expected: In variant one a blue water grade covers a patch of 600 by 400 map units that is clear at close zoom and gone at far zoom, if the middle number is height. In variant two the patch moves or vanishes. In variant three the grade switch moves to a different zoom level, if height follows the camera.

#### Raid modding

`hoi4_wiki/raid_modding.md`

**G231.** A raid file without the types root is ignored; duplicate ids across files; a mod file with a vanilla file name overrides the vanilla file. (kit block `(kit page)`)

- Setup: Raid test mod from B2-08 with only E1. Run 1: the mod file paratrooper_raids.txt as described (override by file name). Run 2: also add common/raids/zz_b2_copy.txt, an unmodified copy of vanilla paratrooper_raids.txt, so mine_sabotage_raid is defined twice (1 day and 90 days). Run 3: remove zz_b2_copy.txt and delete the first line types = { and the last closing brace of the mod's paratrooper_raids.txt
- Steps:
  1. Run 1: open the raids screen, choose Mine Sabotage and read the preparation time.
  2. Run 2: repeat, read the preparation time and error.log for a duplicate-id message.
  3. Run 3: repeat and check whether the paratrooper raid types (Mine Sabotage, Pathfinder) still appear.
- Expected: Run 1 showing 1 day confirms override by file name. Run 2 showing 90 days means the later file by name wins, 1 day means the earlier file wins, and an error means duplicates are rejected. In run 3 the types missing (the vanilla file is overridden by name) confirm a file without the root is ignored. If they still load, the root is optional.
- Run 2026-11-02: settled the root-less file (an error at load) and the duplicate id ("Duplicate ID" at the file that sorts second). Remains: whether the root-less type exists in the raids screen, which duplicate wins, and the vanilla file name override.

**G232.** faction_influence_score_on_success adds faction influence on success. (kit block `(kit page)`)

- Setup: Raid test mod from B2-08, plus common/scripted_effects/b2_effects.txt: b2_make_faction = { create_faction = B2_TEST_FACTION }. In mine_sabotage_raid change the success base from 0.6 to 1 and the critical base from 0.15 to 0 so it always succeeds without a critical. Category paratrooper_raids gives 100
- Steps:
  1. Console: effect GER b2_make_faction. Open the faction screen and note GER's influence score.
  2. Create and finish one mine_sabotage_raid (1 day of preparation) and confirm the line 'B2 success' in game.log.
  3. Reopen the faction screen and read GER's influence score again.
- Expected: An increase of about 100 after the success line confirms the category value feeds faction influence. No change means the key does nothing here or needs another condition. A decrease would point to another sign convention.

**G233.** cancel_trigger cancels the raid while true, or while false. (kit block `(kit page)`)

- Setup: Raid test mod from B2-08, but with E1 set to days_to_prepare = 5. Add to mine_sabotage_raid the block cancel_trigger = { has_country_flag = b2_cancel }. Run 2 uses cancel_trigger = { NOT = { has_country_flag = b2_cancel } } instead
- Steps:
  1. Run 1: create a raid and let it prepare. Advance one in-game day and check the raid still exists.
  2. Console: set_flag b2_cancel. Advance one day and check whether the raid is gone.
  3. Run 2: restart, create a raid, never set the flag, advance one day and check whether the raid exists.
- Expected: In run 1 a raid that survives without the flag and disappears after it means the raid is canceled while the trigger is true. In run 2 a raid canceled at once without the flag is consistent with that. A run 2 raid that survives without the flag means the raid is canceled while the trigger is false.

**G234.** Default of fire_only_once and default preparation time when the keys are omitted. (kit block `(kit page)`)

- Setup: Raid test mod from B2-08 but without E1: delete the days_to_prepare line and the fire_only_once line from mine_sabotage_raid and add days_re_enable = 0
- Steps:
  1. Create a raid and read the preparation time shown.
  2. Let it finish (use the days shown), then try to create the same raid again on the same target.
- Expected: A preparation time of 7 days means BASE_DAYS_TO_PREPARE is the default. A second creation being allowed means fire_only_once defaults to no. If the second creation is refused, the default is yes.

**G235.** A prepared raid instance stays when the type's visible turns false. (kit block `(kit page)`)

- Setup: Raid test mod from B2-08 with E1 changed to days_to_prepare = 5 and the visible block replaced by visible = { NOT = { has_country_flag = b2_hide } }
- Steps:
  1. Create a raid and let it prepare for 2 days.
  2. Console: set_flag b2_hide. Look at the raids screen for the raid and for the type.
  3. Advance to the end of preparation and try to launch.
- Expected: The instance remaining and launchable means a prepared instance survives the type being hidden. The instance vanishing or becoming unlaunchable means visible is checked every tick.

**G236.** What range_factor does. (kit block `(kit page)`)

- Setup: Raid test mod from B2-08 plus max_distance = 150 and unlimited_ai_range = no in mine_sabotage_raid. Run 1: range_factor = 1. Run 2: range_factor = 1000
- Steps:
  1. Run 1: open the raids screen, choose Mine Sabotage, count the selectable targets and starting points.
  2. Run 2: repeat and count again.
  3. Run 3: set unlimited_ai_range = yes with range_factor = 20, hand GER to the AI (console: ai) and run one in-game month. Read game.log for 'B2 success' lines.
- Expected: Different counts between runs 1 and 2 mean range_factor scales the distance a player can use. Equal counts, with AI raids only in run 3, mean range_factor matters only for the AI. No effect anywhere means it is unused by this type.

**G237.** naval_commando_raid_distance is added to BASE_NAVAL_COMMANDO_RAID_DISTANCE. (kit block `(kit page)`)

- Setup: New game, 1936, play as INS, Thunder at Our Gates enabled, one mod: common/ideas/b2_ideas.txt with ideas = { country = { b2_idea = { modifier = { naval_commando_raid_distance = 100 } } } }. Vanilla define BASE_NAVAL_COMMANDO_RAID_DISTANCE = 1500
- Steps:
  1. Open the naval commando raids screen and count the targets in range with no extra idea (N0).
  2. Console: add_ideas b2_idea. Count again (N1).
  3. Console: add_ideas idea_INS_hidden_naval_raid_range. Count again (N5000).
- Expected: N1 at least N0 and N5000 clearly larger than N0 mean the modifier adds to the base. N1 much smaller than N0 means the modifier replaces the base distance.

**G238.** What an unknown success modifier name does; how an unsuccessful roll splits between failure and limited_success. (kit block `(kit page)`)

- Setup: Raid test mod from B2-08. Part 1: add to the success formula agility = { reference = 100 weight = 0.5 } (the doc example name). Part 2 (remove that line): success base = 0, critical base = 0, add fire_only_once = no and days_re_enable = 0
- Steps:
  1. Part 1: start, read error.log for agility and check whether the raid UI lists the modifier.
  2. Part 2: run 20 raids on different targets (1 day of preparation each) and count the game.log lines 'B2 failure' and 'B2 limited_success'.
- Expected: A log error or a missing modifier line in part 1 means an unknown name is reported or ignored. Both outcome lines in part 2 mean the split is random (the counts give the ratio). Only 'B2 limited_success' means the split is deterministic when success is 0.
- Run 2026-11-02: tried, inconclusive because the example name `agility` was reported at load as "Custom success chance modifier not correctly set up", but the failure against limited success split was not run.

**G239.** Temporary variables do not cross into events; event targets saved in the outcome do; two raids ending together overwrite a pending variable; final effects run even if launchable is later false. (kit block `(kit page)`)

- Setup: Raid test mod from B2-08 with the success base set to 1. Add events/b2_events.txt: add_namespace = b2 and country_event = { id = b2.1 hidden = yes immediate = { log = 'B2 event temp=[?b2_t]' event_target:b2_actor = { log = 'B2 actor target ok' } } }. In the success actor_effects add set_temp_variable = { b2_t = 7 }, save_event_target_as = b2_actor, var:actor_country = { country_event = { id = b2.1 hours = 1 } } and var:actor_country = { set_variable = { b2_pending = var:ROOT.target_state } log = 'B2 pending set' }. Replace launchable with launchable = { NOT = { has_country_flag = b2_block } }
- Steps:
  1. Launch two raids on two different targets in the same game hour. After they finish read game.log for the lines B2 success, B2 event and B2 pending set.
  2. Create a third raid, launch it, then at once run console set_flag b2_block. Let it finish and read game.log.
- Expected: 'B2 event temp=0' (or an empty value) with 'B2 actor target ok' means temporary variables do not cross and event targets do. 'temp=7' means temporary variables cross. Two 'B2 pending set' lines but one b2_pending value show the overwrite. 'B2 success' for the third raid despite the flag means final effects ignore launchable.

**G240.** JAP_pearl_harbor_strike is hidden without Gotterdammerung. (kit block `(kit page)`)

- Setup: New game, 1936, play as JAP, one mod with common/scripted_effects/b2_effects.txt: b2_focus = { complete_national_focus = JAP_nanshin_ron }. Two runs, with and without the Gotterdammerung DLC in the launcher playset. If the DLC cannot be switched off on this machine, mark the check unavailable
- Steps:
  1. Console: effect JAP b2_focus.
  2. Open the raids screen and look for Pearl Harbor Strike under the air_raids category, with the DLC on and then off.
- Expected: Present with the DLC and missing without it means the category gate hides its types. Present in both means the type has no DLC gate in practice.

**G242.** use_nuke = yes in a type that lists nukes consumes a second nuke; essential equipment and command power are or are not refunded on cancellation. (kit block `(kit page)`)

- Setup: New game, 1936, play as GER, Gotterdammerung enabled, one mod: copy vanilla common/raids/nuclear_raids.txt to the same path and change one use_nuke = no to use_nuke = yes in one outcome of one type. Console: set_flag early_nuclear_raid_unlock, nukes 2, cp 100, ae 20 transport_plane_equipment
- Steps:
  1. Record the nuke count and the command power. Create the modified nuclear raid and record both again.
  2. Cancel it from the raids screen and record both again.
  3. Create it again, let it reach the outcome that has use_nuke = yes and record the nuke count after it.
- Expected: Nukes dropping by 1 at creation and by a second one at the modified outcome means use_nuke = yes consumes a second nuke. A refund of nukes or command power on cancellation means the wiki warning about refunds is wrong. No refund confirms it.

#### Scopes

`hoi4_wiki/scopes.md`

**G243.** count on any_ triggers, the meaning of any_claim and whether global_every_army_leader works outside a country scope (kit block `scope-types-1-19-3`)

- Setup: New game, 1936 start, play as GER, only the test mod. Mod file common/scripted_effects/b4.txt: b4_cnt = { if = { limit = { any_owned_state = { count = 100 is_coastal = yes } } log = "B4 count100" } if = { limit = { any_owned_state = { count = 2 is_coastal = yes } } log = "B4 count2" } if = { limit = { any_claim = yes } log = "B4 claim" } } b4_gl = { global_every_army_leader = { limit = { always = yes } log = "B4 gl country" } random_owned_state = { global_every_army_leader = { limit = { always = yes } log = "B4 gl state" } } }
- Steps:
  1. Start with the mod
  2. Console: effect GER b4_cnt, then effect GER b4_gl
  3. Read game.log and error.log
- Expected: count is accepted if error.log is quiet: B4 count2 appears and B4 count100 does not (GER has more than 2 and fewer than 100 coastal states). An error on count means ordinary any_ iterators do not take it. B4 claim shows whether any_claim is true for a country with claims in 1936. B4 gl state shows whether the effect also works in state scope.
- Run 2026-11-02: settled `count` on `any_` triggers and `global_every_army_leader` outside a country scope. Remains: what `any_claim = yes` matches (false for six countries in 1936, so find one with claims).

**G244.** What CAPITAL and OCCUPIED select, what owner and controller select in state scope, what the clear_global_event_targets keywords select (kit block `scope-keywords`)

- Setup: New game, 1936 start, play as GER, only the test mod. Mod file common/scripted_effects/b4.txt: b4_kw = { CAPITAL = { if = { limit = { is_capital = yes } log = "B4 CAPITAL is capital state" } } random_owned_state = { OCCUPIED = { log = "B4 OCCUPIED [THIS.GetTag]" } if = { limit = { is_owned_by = owner } log = "B4 owner is state owner" } } } b4_cl = { GER = { save_global_event_target_as = b4_g1 } ENG = { save_global_event_target_as = b4_g2 } } b4_cl2 = { clear_global_event_targets = ROOT if = { limit = { has_event_target = b4_g1 } log = "B4 g1 alive" } if = { limit = { has_event_target = b4_g2 } log = "B4 g2 alive" } }
- Steps:
  1. Start with the mod
  2. Console: effect GER b4_kw
  3. Console: effect GER b4_cl, then effect GER b4_cl2
  4. Read game.log and error.log
- Expected: B4 CAPITAL is capital state means CAPITAL in country scope is the capital state. The OCCUPIED line prints which country it selects. B4 owner is state owner means the lowercase keyword is the owner of the state in scope. After b4_cl2, if neither g1 nor g2 is alive then ROOT clears all global targets, if only one is alive the keyword picks targets saved from that scope. Errors in error.log mean the keyword is rejected.
- Run 2026-11-02: settled that `CAPITAL` and `OCCUPIED` are not scope switches, that lower-case `owner` works, and that `clear_global_event_targets = ROOT` and `= THIS` cleared nothing. Remains: `OCCUPIED` in an occupied state, `clear_global_event_targets = yes`, and whether the keywords are valid as effect targets.

#### Scripted GUI modding

`hoi4_wiki/scripted_gui_modding.md`

**G249.** `parent_window_name` versus `parent_window_window`; the `_instance` rule (kit block `sg-parent-keys`)

- Setup: Mod b9ui with a descriptor.mod, enabled, new 1936 game as GER. File common/scripted_guis/b9.txt: scripted_gui = { b9_gui = { context_type = player_context window_name = "b9_window" parent_window_name = "b9_host" visible = { always = yes } } } . File interface/b9.gui: guiTypes = { containerWindowType = { name = "b9_window" position = { x = 300 y = 200 } size = { width = 700 height = 400 } } } . Variant two writes parent_window_window = "b9_host" instead. In b9.gui add a second container b9_host (position x 0 y 100) with a visible icon.
- Steps:
  1. Start the game and screenshot, then read error.log.
  2. Repeat with variant two.
- Expected: The key the engine reads draws b9_window inside b9_host. The other key is ignored or logged. A third variant that nests a container in a gridBoxType shows whether the `_instance` suffix is needed.
- Run 2026-11-02: tried, inconclusive because `parent_window_window` was rejected as an unexpected token and `parent_window_name` parsed, but no screenshot was taken, so no window was seen inside a host.

**G250.** `ai_test_variance` unit, wiki weight forms, `ai_test_parent`, `human_ai` and `scripted_ai.log` (kit block `sg-ai-attribute-notes`)

- Setup: Mod b9sg. File common/scripted_guis/b9.txt: the base scripted GUI of check B9-03 with ai_enabled = { always = yes } ai_test_interval = 24 ai_test_variance = 0.2 ai_check = { always = yes } ai_weights = { b9_button_click = { ai_will_do = { base = 10 } ignore_lower_weights = yes weight = 50 } } and a matching button in b9.gui.
- Steps:
  1. Start as GER, run `human_ai` in the console and let several days pass.
  2. Find scripted_ai.log in the logs folder and read it.
  3. Repeat with ai_test_variance = 24, then with ignore_lower_weights = { factor = 1 }, then with ai_test_parent = b9_gui added, reading error.log each time.
- Expected: scripted_ai.log exists and lists the checks if human_ai writes it. The gaps between tests show whether the variance is hours or a fraction. Rejected keys appear in error.log.
- Run 2026-11-02: settled that `weight` inside an entry is rejected at load while the button is still pressed, that `ai_test_variance` changes how often the AI tests, and that `scripted_ai.log` is written under `human_ai`. Remains: the variance unit, `ai_test_parent`, and the block form of `ignore_lower_weights`, whose button was never pressed.

**G251.** event targets cannot be used in scripted GUIs (kit block `sg-tips-notes`)

- Setup: Mod b9sg2. The base scripted GUI of check B9-03 with a button b9_button and effects = { b9_button_click = { save_event_target_as = b9_t } } , and a visible trigger that tests event_target:b9_t = { always = yes } on the window.
- Steps:
  1. Start the game, click the button, screenshot.
  2. Read error.log.
- Expected: The window changes after the click if event targets work there. An error that names the event target, or no change, shows they do not.

#### Sound modding

`hoi4_wiki/sound_modding.md`

**G252.** a wrong `.wav` path is harmless (kit block `sound-sound-notes`)

- Setup: Mod b9snd. File sound/b9.asset: sound = { name = "b9_ok" file = "audiofiles/building_large_fall_slow_01_01.wav" } and sound = { name = "b9_bad" file = "audiofiles/no_such.wav" } . File sound/b9_fx.asset: a soundeffect block for each, copied from a vanilla soundeffect in sound/gui/gui_sound_effects.asset.
- Steps:
  1. Start the game, open the console, type `Audio.PlayEffect b9_ok`, then `Audio.PlayEffect b9_bad`.
  2. Read error.log.
- Expected: The game starts and keeps running, b9_ok plays and b9_bad is silent. A crash or a refusal to start contradicts the claim. A log line is a warning only.

#### Special project modding

`hoi4_wiki/special_project_modding.md`

**G253.** Replacing a vanilla project by path; duplicate ids; draft keys of special_projects_documentation.md are ignored. (kit block `(kit page)`)

- Setup: New game, 1936, GER, one mod. Copy vanilla common/special_projects/projects/air_projects.txt to the same path and add to sp_air_radar the lines special_project_type = air, prototype_cost = 5 and threshold_min = 0. Run 2 also adds common/special_projects/projects/zz_dup.txt with the unchanged vanilla sp_air_radar block but complexity = 100
- Steps:
  1. Start the game and read error.log for the draft keys.
  2. Open the project in the Special Projects screen and compare the complexity shown in run 1 and run 2.
- Expected: A log line naming the draft keys means they are rejected. No line means they are silently ignored. In run 2 the complexity shown tells which duplicate wins.
- Run 2026-11-02: settled the draft keys (an unexpected token each) and that two files with one project id draw no error. Remains: which duplicate wins and replacing a vanilla project by path.

**G254.** Basic research is what a facility with a scientist and no project does. (kit block `(kit page)`)

- Setup: New game, 1936, GER, no mod. Console: instantconstruction, sp_add_scientist 3 air. Build an air_facility in any state
- Steps:
  1. Assign the scientist to the facility without starting a project. Open the facility window and hover the scientist's program.
  2. Advance 30 days and note the air breakthrough progress and the scientist experience.
- Expected: Tooltip text from PROGRAM_BASIC_RESEARCH with a daily breakthrough gain (about 0.12 percent plus 0.05 percent per skill level) confirms basic research is the idle state. No gain means it needs something else.
- Run 2026-11-02: the tooltip shows basic research for an idle scientist ("Providing 0.15% breakthrough progress and 6.0% technology research bonus for Aerodynamics and Avionics"). Remains: the 30-day gain.

**G261.** What SCIENTIST_INJURED_FACTOR = 0.0 means for progress. (kit block `(kit page)`)

- Setup: SP base mod from B2-23 with project_tags = sp_tag_aircraft and complexity = 2, plus common/scripted_effects/b2_effects.txt b2_injure = { random_scientist = { injure_scientist_for_days = 5 } }. Console: instantconstruction, sp_add_scientist 3 air
- Steps:
  1. Start b2_project_1 and record the progress per day for 2 days.
  2. Console: effect GER b2_injure. Record the progress per day for 5 more days.
- Expected: Progress stopping while the scientist is injured means factor 0.0 zeroes progress. Progress continuing at the same speed means 0.0 reduces nothing.

**G263.** A modifier needs both the <name> and <name>_tt loc keys for a clean tooltip; a missing _tt shows a raw key. (kit block `(kit page)`)

- Setup: SP base mod from B2-23 with project_tags = sp_tag_aircraft, plus a trait b2_trait2 = { modifier = { b2_project_1_speed_factor = 0.5 } } in common/scientist_traits/b2_traits.txt. Run 1: loc has only b2_project_1_speed_factor. Run 2: loc also has b2_project_1_speed_factor_tt
- Steps:
  1. Console: instantconstruction, sp_add_scientist 3 air. Open the facility window and run sp_add_selected_scientist_trait b2_trait2.
  2. Hover the trait and the project speed line in each run.
- Expected: A raw key in run 1 and clean text in run 2 confirms both keys are needed. Clean text in both means the _tt key is optional.

**G264.** A range constant gives a different gain each iteration. (kit block `(kit page)`)

- Setup: SP base mod from B2-23 with project_tags = sp_tag_aircraft, complexity = sp_complexity.small in b2_project_1 (range 15 to 25) and complexity = 20 in a copy b2_project_2. Console: instantconstruction, sp_add_scientist 3 air, sp_fast
- Steps:
  1. Run each project and record the progress after every iteration.
- Expected: Different step sizes per iteration for project 1 and 20 each for project 2 confirm a draw per iteration. Equal steps for both mean one draw per project.

**G265.** How the AI chooses between reward options, and whether an option ai_chance is read. (kit block `(kit page)`)

- Setup: SP base mod from B2-23 with project_tags = sp_tag_aircraft where b2_reward has two options b2_opt1 and b2_opt2, each logging its token with 'B2 option 1' or 'B2 option 2'. Hand GER to the AI (console: ai) with a scientist and a facility already set up. Run 2 adds ai_chance = { base = 100 } to option b2_opt2
- Steps:
  1. Let the AI research the project repeatedly (restart the project) for 20 iterations.
  2. Read game.log and count the lines for each option.
- Expected: Always the first or default option means no AI choice logic. A mix means the AI weighs options. If run 2 shifts the mix toward option 2, an option ai_chance is read.

**G266.** What weight = { factor = 1.0 } does inside a reward weight. (kit block `(kit page)`)

- Setup: SP base mod from B2-23 with project_tags = sp_tag_aircraft, b2_reward using weight = { factor = 1.0 } and a second reward b2_other (weight = { base = 1 }, logs 'B2 other'), and empty_reward_weight = { base = 0 }. Console: instantconstruction, sp_add_scientist 3 air, sp_fast
- Steps:
  1. Run b2_project_1 for 20 iterations and count 'B2 reward fired' and 'B2 other' lines.
  2. Read error.log for an unknown key.
- Expected: Roughly equal counts mean factor acts as the default weight 1.0. Only 'B2 other' lines mean factor is ignored or gives weight 0. An error.log line means the key is not valid there.

**G267.** A specialization without a facility building cannot be researched. (kit block `(kit page)`)

- Setup: New game, 1936, GER, one mod: common/special_projects/specialization/b2_spec.txt with b2_spec = { color = { 10 20 30 } }, and a project of the SP base mod from B2-23 with specialization = b2_spec. No building carries b2_spec
- Steps:
  1. Start the game, read error.log and open the Special Projects screen.
- Expected: A log error or a missing project tree means projects are blocked without a facility building. A visible tree with a start button but no facility to start it in would show the block is only a missing facility.
- Run 2026-11-02: tried, inconclusive because a new specialization and a project of it loaded without a message, and whether the project can be researched was not tested.

#### State modding

`hoi4_wiki/state_modding.md`

**G270.** force_link_ownership_to links an impassable state to another state; the exe message appears when used on a passable state. (kit block `state-impassable`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). history/states/64-Brandenburg.txt: vanilla copy with force_link_ownership_to = 10 added to the state block.
- Steps:
  1. Delete error.log and launch with the mod, start 1936 as GER.
  2. Read error.log and check the owner of state 64.
- Expected: The message "is only effective when used on impassable states" confirms the exe string is live. Ownership unchanged confirms it does nothing on a passable state.
- Run 2026-11-02: settled the message on a passable state (state 64 stayed with GER). Remains: what the link does on an impassable state.

**G271.** One local_supplies unit equals 0.2 supply. (kit block `state-optional-keys`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). history/states/64-Brandenburg.txt: vanilla copy with local_supplies = 5.0 set (or added).
- Steps:
  1. Start 1936 as GER, open the supply map mode and the state 64 tooltip, note the local supply figure.
  2. Repeat with local_supplies = 10.0.
- Expected: A figure step of 1.0 for 5.0 units (0.2 per unit) confirms the factor. Another ratio gives the real factor.

**G273.** Numbers in a dated buildings block are the new total level, not an addition. (kit block `state-buildings-fill`)

- Setup: descriptor.mod: name="b8test", version="1.0", supported_version="1.19.*" (path in mod folder). history/states/64-Brandenburg.txt: base infrastructure = 2 and a block 1939.1.1 = { buildings = { infrastructure = 3 } } (start 1939 bookmark).
- Steps:
  1. Start the 1939 bookmark as GER and read the infrastructure of state 64.
  2. Change the block to infrastructure = 1 and read it again.
- Expected: Level 3 then 1 means total. Level 5 (capped) then 3 means addition.
- Run 2026-11-02: tried, inconclusive because the infrastructure level of state 64 read 5 with the block at 3 and at 1, which fits neither reading and may include other sources or a cap. Read the raw building level as the G021 probe does and add a control without the block.

#### Technology modding

`hoi4_wiki/technology_modding.md`

**G278.** A technology whose allow_branch is met cannot be chosen by the AI. (kit block `tech-triggers-note`)

- Setup: No mod, with the Man the Guns DLC enabled. Vanilla common/technologies/NSB_armor.txt: amphibious_tank_chassis has `allow_branch = { has_dlc = "Man the Guns" }`. New game, 1936 start, play as GER, observe.
- Steps:
  1. Type `observe`, then set maximum speed and let it run to 1 January 1942.
  2. Type `tag GER` and open the technology screen.
  3. Check whether amphibious_tank_chassis has been researched by GER, ITA and JAP (switch with `tag`).
- Expected: If the AI researched the technology although allow_branch is met, the wiki sentence is wrong. If no AI country ever researches it, the sentence is consistent but also fits low AI interest, so repeat with a second gated technology.

**G281.** The hoi4.exe messages about a missing grid box or missing coordinates are produced for a broken technology layout. (kit block `tech-grid-box`)

- Setup: Mod with common/technologies/t_tech.txt holding two techs, both with research_cost = 1, start_year = 1936, categories = { infantry_tech }. `t_parent` has `folder = { name = infantry_folder position = { x = 30 y = 30 } }` and `path = { leads_to_tech = t_child research_cost_coeff = 1 }`. `t_child` has `folder = { name = infantry_folder }` with no position. New game, 1936 start, play as GER.
- Steps:
  1. Start the game and open the technology screen.
  2. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log for 'no coordinates' and 'grid box'.
- Expected: A log line with the quoted text ('has no coordinates in folder') confirms the exe message is produced. A clean log means the message is not raised for this fault.
- Run 2026-11-02: tried, inconclusive because every scratch technology draws the grid-box line, so the line is not specific to a missing position, and the Technology screen was not opened.

**G282.** The extra technology keys desc, show_effect_as_desc, sub_tech_index, force_use_small_tech_layout and show_equipment_icon work as the notes say. (kit block `tech-keys-extra`)

- Setup: Mod with common/technologies/t_tech.txt: one tech as in the previous checks plus `desc = T_DESC_TEST show_effect_as_desc = yes force_use_small_tech_layout = yes`, and localisation T_DESC_TEST: "T desc text". New game, 1936 start, play as GER.
- Steps:
  1. Open the technology screen, find t_tech and take a screenshot.
  2. Hover it and read the tooltip.
- Expected: The tooltip contains 'T desc text' and the node uses the small layout: those keys do what the notes say. Anything missing means that key's meaning is different or unused.
- Run 2026-11-02: tried, inconclusive because the extra keys loaded without an error, and the tooltip text and small layout are interface only.

#### Triggers

`hoi4_wiki/triggers.md`

**G284.** Whether the engine reads DIPLOMACY triggers that vanilla does not define (kit block `diplomacy-scripted-trigger-notes`)

- Setup: New game, 1936 start, play as GER, only the test mod. Mod file common/scripted_triggers/b4.txt: DIPLOMACY_SEND_ATTACHE_ENABLE_TRIGGER = { always = no } DIPLOMACY_LEND_LEASE_CANCEL_ENABLE_TRIGGER = { always = no } DIPLOMACY_EMBARGO_ENABLE_TRIGGER = { always = no }
- Steps:
  1. Start with the mod as GER
  2. Open the diplomacy screen of ENG and look at Send Attache and Embargo
  3. Open a country with a lend lease contract if available, take screenshots, read error.log
- Expected: A greyed out action while the same action is enabled without the mod means the engine reads that name. Embargo is a hoi4.exe string and should be greyed out. If Send Attache stays enabled the name is not read. The same applies to the lend lease name. Repeat with is_diplomatic_action_valid_<other token> to test visibility triggers.

#### Troubleshooting

`hoi4_wiki/troubleshooting.md`

**G285.** How -debug and -debug_mode relate, and whether a Steam launch option reaches hoi4.exe through the launcher (also console_commands cc-intro line 54) (kit block `ts-debug-launch`)

- Setup: New game, 1936 start, play as GER, no mods. Four separate sessions: A) launcher entry 'Open game in Debug Mode'. B) normal launcher entry with Steam launch option -debug. C) normal entry with Steam launch option -debug_mode. D) normal entry, no options.
- Steps:
  1. In each session start the 1936 GER game and open the console.
  2. Enter: eval_effect if = { limit = { is_debug = yes } log = "B1_IS_DEBUG_TRUE" }
  3. Quit, then open Documents/Paradox Interactive/Hearts of Iron IV/logs/game.log and search for B1_IS_DEBUG_TRUE.
  4. Keep the log of each session before starting the next.
- Expected: Session D has no B1_IS_DEBUG_TRUE line. A session with the line has debug mode on. A line in A means -debug_mode counts as debug mode for is_debug. No line in B means a Steam option does not reach hoi4.exe through the launcher, or -debug is not what is_debug reads. Compare C the same way.
- Run 2026-11-02: settled `-debug` against `-debug_mode` against no arguments, with hoi4.exe started directly. Remains: the Steam launch option route through the Paradox launcher, which needs the Steam client.

**G286.** Crash folder name and contents, meta.yml fields, LastRead and LastScript, exceptions.log absence, stack trace without mod info, copied error.log (also ts-fatal-errors and ts-log-files claims) (kit block `ts-crash-folder`)

- Setup: New game, 1936, GER. Test mod b1: Documents/Paradox Interactive/Hearts of Iron IV/mod/b1.mod holds the lines name="b1", path="mod/b1" and supported_version="*". Its content folder is Documents/Paradox Interactive/Hearts of Iron IV/mod/b1/. Add Documents/Paradox Interactive/Hearts of Iron IV/mod/b1/common/scripted_effects/b1.txt with the line 'b1_bad_effect = { b1_unknown_token = yes }'. Move the old Documents/Paradox Interactive/Hearts of Iron IV/crashes/ folder away first. Two sessions: A) mod b1, no launch option. B) mod b1, Steam launch option -crash_data_log.
- Steps:
  1. Start the game, begin the GER game, open the console.
  2. Enter: CrashReporter.SimulateCrash (documented as simulating a crash, the game exits).
  3. Open Documents/Paradox Interactive/Hearts of Iron IV/crashes/ and list the new folder name and every file and sub-folder in it.
  4. Open meta.yml there and note whether LastRead or LastScript lines exist.
  5. Open exception.txt and check whether any line names a mod file.
  6. Check whether logs/error.log inside the crash folder names common/scripted_effects/b1.txt.
  7. Search Documents/Paradox Interactive/Hearts of Iron IV/logs/ for a file named exceptions.log.
  8. Repeat all steps for session B.
- Expected: If the wiki notes hold: a folder crashes/hoi4_<yyyymmdd>_<hhmmss>/ with exception.txt, meta.yml, minidump.dmp, settings copies and a logs/ folder; no exceptions.log anywhere; meta.yml has LastRead (and maybe LastScript) only in session B; exception.txt shows only hoi4.exe frames; the copied error.log names b1.txt. Any difference corrects the matching sentence.
- Run 2026-11-02: three real crashes (no `SimulateCrash`, no `-crash_data_log`) settled the folder name and contents, the missing LastRead and LastScript lines, the missing exceptions.log and the hoi4.exe-only stack trace. Remains: session B with `-crash_data_log`, `SimulateCrash`, and whether the copied error.log names the mod file.
- Run 2026-11-02: session B ran with `-debug -crash_data_log` and `CrashReporter.SimulateCrash`. meta.yml had `LastRead:  (1)` with no file name, filled checksums and no `LastScript` line. Remains: whether the copied error.log names a mod file after a crash from a bad definition, and a `LastRead` line with a file name.

**G289.** The user folder can be moved (userdir=, userdir.txt) and what the exe arguments crash_data_log, nofilewatcher, noai, logprefix=, logpostfix=, userdir= do (kit block `ts-log-files`)

- Setup: No mods. Run hoi4.exe by hand (not through Steam) with the arguments given per step.
- Steps:
  1. Start with: hoi4.exe -userdir=C:/b1user . Check whether C:/b1user is created with a logs/ folder and whether Documents/Paradox Interactive/Hearts of Iron IV/ gets new files.
  2. Start with: hoi4.exe -logprefix=b1_ -logpostfix=_z . List the file names in logs/.
  3. Start with: hoi4.exe -noai . Start a GER game, run 5 days and watch whether AI countries act.
  4. Start with: hoi4.exe -nofilewatcher . Edit a gui file while the game runs and note whether it reloads.
  5. Create userdir.txt in the game folder with the path C:/b1user2 and start normally; check whether that folder is used.
- Expected: Each argument that works leaves the visible effect described. No effect means the exe string is unused. The other names in the page's list (gamelog, dumpdb, dump_history and so on) stay unchecked here.
- Run 2026-11-02: settled `-logprefix=` and `-logpostfix=`. Remains: `-userdir=`, `userdir.txt`, `-noai` and `-nofilewatcher`.

**G290.** Log file names, the line format with no_game_date, and what each log holds (kit block `ts-log-files`)

- Setup: Move the old Documents/Paradox Interactive/Hearts of Iron IV/logs/ folder away. No mods, debug launcher entry.
- Steps:
  1. Start to the main menu, then open logs/game.log and logs/error.log. Note the first lines and the game-date field of each line.
  2. Start a 1936 GER game, console: eval_effect log = "B1_LINE" , then quit.
  3. List every file in logs/ and compare with the table in the Log files section: size, empty or not, one-line summary of each.
  4. Host a multiplayer lobby with no clients and check whether executed_commands.log, posted_commands.log, received_commands.log and sent_commands.log get content.
- Expected: Lines read [hh:mm:ss][no_game_date][file.cpp:line] before a game starts and carry a game date afterwards. File names match the underscore forms. Mark each table row whose content differs.
- Run 2026-11-02: settled the log file names and the line format. Remains: what each log holds (the Holds column) and the multiplayer part.

**G291.** The game ignores map/rocketsites.txt, and the career profile file naming (kit block `ts-menu-loading-fix`)

- Setup: Test mod b1: Documents/Paradox Interactive/Hearts of Iron IV/mod/b1.mod holds the lines name="b1", path="mod/b1" and supported_version="*". Its content folder is Documents/Paradox Interactive/Hearts of Iron IV/mod/b1/. Add mod/b1/map/rocketsites.txt containing the single line 'garbage {'. Steam launch option -crash_data_log.
- Steps:
  1. Start the game with mod b1 to the main menu, then start a 1936 GER game.
  2. Check whether any error or crash mentions rocketsites in logs/error.log or crashes/.
  3. List Documents/Paradox Interactive/Hearts of Iron IV/ for a file matching career_profile_*_v3.pr and for numbers.pr.
- Expected: No error and no crash means the file is not read in 1.19.4.1. The profile file confirms the naming. numbers.pr should be absent.

**G292.** Engine messages appear as the table says, and script errors show two 'near line' numbers (kit block `ts-engine-messages`)

- Setup: Test mod b1: Documents/Paradox Interactive/Hearts of Iron IV/mod/b1.mod holds the lines name="b1", path="mod/b1" and supported_version="*". Its content folder is Documents/Paradox Interactive/Hearts of Iron IV/mod/b1/. Add mod/b1/common/scripted_effects/b1.txt with 'b1_a = { b1_unknown_token = yes }' and 'b1_b = { add_political_power = }'. Add mod/b1/common/scripted_triggers/b1.txt with 'b1_t = { b1_unknown_trigger = yes }'. Add the duplicate-key loc pair from check B1-13.
- Steps:
  1. Start the game with mod b1 to the main menu, quit, then open logs/error.log and logs/text.log.
  2. Search for 'Unknown effect-type', 'Unknown trigger-type', 'Invalid effect' and 'near line:'.
  3. Note which log holds each message and whether each error carries two 'near line' numbers.
- Expected: Messages appear in the logs named in the table's Seen-in column and with two line numbers. A message in another log, or with one number, corrects the table or the sentence.
- Run 2026-11-02: settled unknown tokens (two lines, two numbers), a missing value (one line) and duplicate loc keys in text.log. Remains: the other rows of the message table.

**G293.** Logs are overwritten on start, error.log names file and line, setup.log shows the last loaded entry at a start-up crash, later errors follow the first (kit block `ts-debug-loop`)

- Setup: Test mod b1: Documents/Paradox Interactive/Hearts of Iron IV/mod/b1.mod holds the lines name="b1", path="mod/b1" and supported_version="*". Its content folder is Documents/Paradox Interactive/Hearts of Iron IV/mod/b1/. Add mod/b1/common/scripted_effects/b1.txt with 'b1_a = { b1_unknown_token = yes' (unclosed brace) and mod/b1/common/scripted_effects/b2.txt with 'b1_b = { b1_a = yes }'.
- Steps:
  1. Note the modification time and size of logs/error.log and logs/setup.log, then start the game with mod b1 to the main menu and quit.
  2. Check both files were replaced (new time, no old content).
  3. Open error.log, read the first error and the next ten, and note whether later ones mention b1_a or b2.txt.
  4. Add mod/b1/map/definition.csv with one garbage line and start with -crash_data_log.
  5. Read the tail of logs/setup.log and the error.log copy in the new crashes/ folder.
- Expected: Logs are new after each start. The first error names b1.txt with a line, and later errors cite b1_a or b2.txt. The tail of setup.log names the last database entry loaded before the crash.
- Run 2026-11-02: settled that every launch rewrites the logs and that error.log names file and line, and saw that the setup.log tail did not name the faulty file after a start-up crash (integer divide by zero). Remains: the unclosed brace test, whether later errors follow the first, and the `-crash_data_log` crash with a bad definition.csv.

#### Unit modding

`hoi4_wiki/unit_modding.md`

**G294.** The sub-unit keys of the table (abbreviation, group, priority, stats, ...) have the meaning the page gives. (kit block `unit-keys`)

- Setup: Mod with common/units/t_unit.txt: `sub_units = { t_bat = { abbreviation = "TST" sprite = infantry map_icon_category = infantry priority = 601 active = yes type = { infantry } group = infantry need = { infantry_equipment = 10 } combat_width = 2 max_organisation = 50 manpower = 100 soft_attack = 9 } }` and loc `t_bat: "T Battalion"`, `t_bat_short: "TST"`. New game, 1936 start, play as GER.
- Steps:
  1. Open the division designer, find the T Battalion in the infantry group.
  2. Add it to a template and read the stats shown.
  3. Read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log.
- Expected: The battalion shows with abbreviation TST, the infantry group, width 2, organisation 50, manpower 100 and soft attack 9: those keys mean what the page says. Different values or a missing unit mean that key is read differently.
- Run 2026-11-02: tried, inconclusive because the sub-unit loaded and a template accepted it, but the division designer was not opened.

**G295.** The fort terrain block in a sub-unit gives bonuses against forts (the engine meaning of fort). (kit block `unit-terrain-keys`)

- Setup: No mod. Vanilla common/units/engineer.txt has `fort = { attack = 0.1 defence = 0.25 }`. New game, 1936 start, play as GER.
- Steps:
  1. Open the division designer and add an engineer company to a template.
  2. Hover the engineer company and read the terrain/modifier lines in its tooltip.
- Expected: A 'Fort' line with attack +10% and defence +25% shows the block is read and labelled with the localisation key `fort`. No such line means the tooltip does not show it. Whether the bonus applies in a fort battle needs a combat test.
- Run 2026-11-02: settled the tooltip and the "Fort" label (Attack +10.0%, Defense +25.0% in the Engineer Company tooltip). Remains: whether the bonus applies in a fort battle, which needs a combat test.

**G298.** A sub-unit accepts equipment stats such as naval_speed or air_agility. (kit block `unit-navy-air-note`)

- Setup: Mod with common/units/t_unit.txt: `sub_units = { t_bat = { sprite = infantry map_icon_category = infantry priority = 601 active = yes type = { infantry } group = infantry need = { infantry_equipment = 10 } max_organisation = 50 naval_speed = 10 air_agility = 10 } }`. New game, 1936 start, play as GER.
- Steps:
  1. Start the game and read Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log for naval_speed and air_agility.
  2. Open the division designer and read the stats of the new battalion.
- Expected: An error line naming either key means sub-units reject them. A clean log with no change in the shown stats means they are ignored. A visible effect means they are accepted.
- Run 2026-11-02: tried, inconclusive because a sub-unit with `naval_speed` and `air_agility` loaded and a template accepted it, but the division designer was not opened.

#### skill hoi4-characters-leaders

`.claude/skills/hoi4-characters-leaders/SKILL.md`

**G299.** A second block for an existing ideology group discards the whole block and cascades into invalid-ideology errors (kit block `(skill)`)

- Setup: Mod folder b5_test with descriptor.mod. File common/ideologies/zz_b5_ideologies.txt: ideologies = { neutrality = { types = { b5_type = { can_be_randomly_selected = no } } color = { 100 100 100 } } }
- Steps:
  1. Start a new game, 1936 start, play as GER, with only b5_test enabled.
  2. Read error.log and search for Duplicate database id and is not a valid ideology.
  3. Open the Politics tab and look at the ideology list and the neutrality party popularity. Note if b5_type appears.
- Expected: A Duplicate database id line for neutrality and no b5_type anywhere confirm that the second block is discarded. Many is not a valid ideology lines after it confirm the cascade. If b5_type appears, the second block is merged instead.
- Run 2026-11-02: tried, inconclusive because the second group was rejected ("Duplicate database id neutrality") and no invalid-ideology line followed, but nothing in the folder used `b5_type`, so a cascade could not show, and the Politics tab was not read.

#### skill hoi4-ideas-modifiers

`.claude/skills/hoi4-ideas-modifiers/SKILL.md`

**G300.** One dynamic modifier id bound to two scopes on the same state coexists in the engine (kit block `(skill)`)

- Setup: Mod folder b5_test with descriptor.mod. File common/dynamic_modifiers/b5_dm.txt: b5_dm = { enable = { always = yes } stability_factor = 0.01 } File events/b5_ev.txt: add_namespace = b5 country_event = { id = b5.90 title = b5.90 desc = b5.90 is_triggered_only = yes option = { name = b5.90 12 = { add_dynamic_modifier = { modifier = b5_dm scope = GER } add_dynamic_modifier = { modifier = b5_dm scope = ENG } if = { limit = { has_dynamic_modifier = { modifier = b5_dm scope = GER } } set_state_flag = b5_ger } if = { limit = { has_dynamic_modifier = { modifier = b5_dm scope = ENG } } set_state_flag = b5_eng } } } }
- Steps:
  1. Start a new game, 1936 start, play as GER, with only b5_test enabled.
  2. Run: event b5.90 and pick the option.
  3. Run: list_flags 12 (state 12) and read the state flags. Read error.log for b5_dm.
- Expected: Both b5_ger and b5_eng set means the two scoped bindings coexist and the scope argument is checked. Only one of them means the second add replaced the first. An error line about b5_dm means the setup is invalid and the result does not count.
- Run 2026-11-02: confirmed (both scoped bindings read present, and the second add did not replace the first). The claim sits in the skill `hoi4-ideas-modifiers`, which was not edited here. The observation is on the modifiers page.

#### skill hoi4-investigate

`.claude/skills/hoi4-investigate/SKILL.md`

**G301.** One malformed block can hide later errors in the same file. (kit block `(skill)`)

- Setup: Test mod b6brace. common/ideas/b6.txt: `ideas = { country = { b6_idea = { modifier = { stability_factor = 0.1 }` (closing braces missing), followed by `b6_idea2 = { bogus_key = yes }`.
- Steps:
  1. Start a new game with the mod.
  2. Read logs/error.log.
- Expected: One error at the brace and none for the later bogus key means later errors are hidden. Several cascading errors confirm the cascade.
- Run 2026-11-02: confirmed (one error line at the next token, nothing for the later bogus key). The claim sits in the skill `hoi4-investigate`, which was not edited here. The observation is in step 7 of the debug loop on the troubleshooting page.

**G302.** game.log shows the start date and last subsystem, a crash folder has exception.txt, meta.yml and minidump.dmp and no exceptions.log, and an access violation is not in error.log. (kit block `(skill)`)

- Setup: No mod. Start a new game with the 1939 bookmark, play GER.
- Steps:
  1. Read the start-date line and last lines of logs/game.log.
  2. Run console command `crash` (documented as not available in a release build), or `CrashReporter.SimulateCrash` if accepted.
  3. List crashes/ for the new folder and its files, and read error.log.
- Expected: Start-date line shows 1939 and the last date matches the game. The crash folder lists exception.txt, meta.yml, minidump.dmp and no exceptions.log, and error.log has no access-violation line.
- Run 2026-11-02: settled that crash folders hold exception.txt, meta.yml and minidump.dmp and no exceptions.log, that the copied error.log has no access-violation line, and that the console `crash` command is developer-only. Remains: the 1939 bookmark and game.log part. The claim sits in a skill file, so the retag is on the troubleshooting page.
