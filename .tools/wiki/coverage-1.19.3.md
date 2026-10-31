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

Filled in when the batches are merged.
