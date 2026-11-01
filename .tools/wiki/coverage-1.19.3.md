# Wiki snapshot coverage review for HOI4 1.19.3.0

Plan and record of the 2026-10-31 review of `paradox_wiki/` against Hearts of Iron IV 1.19.3.0 (`Operation Postern v1.19.3.0.c01a (5632)`). Each page's own review block holds its detailed record; this file is the overview. The workflow for later builds is in `README.md`.

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

- Nothing is `[game-tested 1.19.3]`. The `[unverified]` statements are the candidates for in-game checks, above all the documentation conflicts listed on the kit pages (the `collection_size` comparison rule, the peace `ai_desire` scale, special project reward thresholds, the scope inside raid `target_type` state filters). These four, and MIO `task_capacity` with its switch off, now carry a **Needs a game run** note on the page that makes the claim.
- Version-added columns in the wiki's effect, trigger and modifier tables were not re-checked.
- Engine behaviour that no game file states, such as defines the engine still reads and the order of on_action effects, stays `[unverified]`.
