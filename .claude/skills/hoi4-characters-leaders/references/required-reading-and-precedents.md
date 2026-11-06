# HOI4 Characters, Leaders and Traits: Required reading and precedents

Part of the [hoi4-characters-leaders](../SKILL.md) skill. Read before writing or reviewing any character script, to find the authoritative documentation and the vanilla files to mirror.

## Contents

- Required reading and vanilla precedents
- Mental model and decision table
- Character definition
- Portraits and GFX wiring (overview)
- Country leader role, ideologies and parties
- Advisor role
- Unit leader roles
- Scientists and operatives
- Country leader traits (also used by advisors and ideas)
- Unit leader traits (summary)
- Lifecycle at runtime
- Generated characters
- Triggers and scopes
- Localisation
- Repository conventions
- Common mistakes and silent failures
- Validation checklist

## Required reading and vanilla precedents

With the HOI4 MCP, use `hoi4.reference_search` / `hoi4.reference_read` for the sections below and `hoi4.source_lookup` for vanilla definitions; if a route fails once, retry once, then read the local files directly.
Installed documentation is more authoritative than the wiki. Root: the installed Hearts of Iron IV folder named in `CLAUDE.md`.

| Topic | Primary source |
| --- | --- |
| Character database root, `can_be_captured`, `scientist` block | `common/characters/_documentation.md` (short; the wiki page is the fuller reference) |
| Character-scope effects and country-scope character effects | `documentation/effects_documentation.md` (`## Effects for scope CHARACTER` list, then `## <effect>`) |
| Character, unit-leader and country-leader triggers | `documentation/triggers_documentation.md` (`## Triggers for scope CHARACTER` list, `## <trigger>`) |
| Localisation objects for characters and unit leaders | `documentation/loc_objects_documentation.md` (`## Character`, `## UnitLeader`) |
| Modifier names usable in traits | `documentation/modifiers_documentation.md` (`country`, `army`, `naval`, `air`, `unit_leader`, `character`, `scientist` scopes) |
| Script constants | `documentation/script_concept_documentation.md`, `common/script_constants/documentation.md` |
| Unit leader trait schema | Header comment of `common/unit_leader/00_traits.txt` |
| Idea categories and character slots | `common/idea_tags/00_idea.txt` |
| Ideology types | `common/ideologies/00_ideologies.txt` |

Offline wiki (`hoi4_wiki/`): `character_modding.md` (primary), `country_creation.md` (Starting characters, Character names, Character portraits), `ideology_modding.md`, `idea_modding.md` (advisor-as-idea arguments, categories), `portrait_modding.md`, `scopes.md` (character iterators, `owner`, `party_leader`), `effects.md` and `triggers.md`.

Vanilla precedents to mirror:

- Character files: `common/characters/GER.txt` (country leaders, advisors with `visible`/`available`/`on_add`, corps commanders, field marshals, admirals, scientists, `allowed_civil_war`), `common/characters/AFG.txt` (`instance` blocks by DLC).
- Country leader and advisor traits: `common/country_leader/00_traits.txt` (header constants, leader traits, `army_chief_*` tiers).
- Unit leader traits: `common/unit_leader/00_traits.txt` (documented schema), `NSB_traits.txt`, `common/unit_leader/00_*_skills.txt` (skill level costs and modifiers).
- Country history recruiting: `history/countries/GER - Germany.txt` and any other tag file (`recruit_character`, then `set_politics`).
- Generic characters by effect: `history/general/generic_advisors.txt`, `china_shared_advisors.txt`, `spain_shared_advisors.txt`.
- Runtime role changes: `common/decisions/TUR.txt` (`remove_unit_leader_role = yes`), `common/decisions/CHI_decisions.txt` (`add_corps_commander_role`), `common/national_focus/belgium.txt` (`set_nationality` then `add_advisor_role`), `common/scripted_effects/SOV_scripted_effects.txt` (`has_character`, `set_nationality`, `promote_character = { character = ... ideology = ... }`).
- Portrait pools for generated characters: `portraits/*.txt`; generated-leader names: `common/names/*.txt`.
- Sprites: `interface/ideas.gfx` (`GFX_idea_traits_strip`), `interface/unitleaderwindow.gfx` (unit leader trait icons `GFX_trait_<id>`), `interface/*_characters.gfx` for portrait sprite files.
- Localisation: `localisation/english/nsb_characters_l_english.yml` (character names), `traits_l_english.yml` (trait names and descriptions), `parties_l_english.yml` (ideology and party names), `ideas_l_english.yml` (advisor idea tokens).
- Abilities for unit leaders: `common/abilities/*.txt`.

