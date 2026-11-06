---
name: hoi4-ideologies
description: Use when defining or auditing HOI4 ideologies in common/ideologies, ideology groups and sub-ideologies, parties, popularities, ideology rules, drift and ideology localisation or GFX.
---

# HOI4 Ideologies

Scope: `common/ideologies/` definitions, groups and sub-ideologies (types), party names and popularities, ideology rules and the script hooks that read them.
The leader role and a character's `ideology` belong to `hoi4-characters-leaders`. Ideas, advisor traits and idea `rule` blocks belong to `hoi4-ideas-modifiers`. Political routes belong to `hoi4-focus-trees`.

`GAME` is the installed game (1.19.4.2). `WIKI` is `hoi4_wiki/` at the kit root (written for 1.19.4.1).
Tags: `[vanilla-confirmed 1.19.4.2]` was read in `GAME`. `[docs]` comes from installed documentation or the wiki. `[game-tested 1.19.4.1]` repeats a launch the wiki records (no game was launched for this skill). `[unverified]` has no source.

## Source map

| Topic | Wiki | Installed |
| --- | --- | --- |
| Definition file, keys, rules | [Ideologies](../../../hoi4_wiki/ideology_modding.md#ideologies), [Loading files](../../../hoi4_wiki/modding.md#loading-files) | `common/ideologies/00_ideologies.txt` |
| Localisation, party names | [Localisation](../../../hoi4_wiki/ideology_modding.md#localisation), [Name](../../../hoi4_wiki/country_creation.md#name) | `localisation/english/`: `parties_l_english.yml`, `modifiers_l_english.yml`, `factions_l_english.yml` |
| Icons, flags | [GFX](../../../hoi4_wiki/ideology_modding.md#gfx), [Flag](../../../hoi4_wiki/country_creation.md#flag) | `interface/countrypoliticsview.gfx`, `gfx/flags/` |
| Starting politics, triggers | [Country history](../../../hoi4_wiki/ideology_modding.md#country-history) | `history/countries/`, `documentation/effects_documentation.md`, `triggers_documentation.md` |
| Booster advisors, drift | [Political advisor](../../../hoi4_wiki/ideology_modding.md#political-advisor) | `history/general/generic_advisors.txt`, `documentation/modifiers_documentation.md` |
| Leaders, portraits, bookmarks | [Country leaders](../../../hoi4_wiki/character_modding.md#country-leaders), [Bookmarks](../../../hoi4_wiki/bookmark_modding.md#attributes) | `common/characters/`, `portraits/00_portraits.txt`, `common/bookmarks/` |

Leader side: [country leader role](../hoi4-characters-leaders/references/country-leader-role-and-traits.md#country-leader-role-ideologies-and-parties). Idea rules: [idea fields](../hoi4-ideas-modifiers/references/idea-files-and-fields.md). Route design: [political depth](../hoi4-focus-trees/references/political-depth-and-route-locks.md).

## Checklist

1. Ideologies are read from `common/ideologies/*.txt` as one `ideologies = { <group> = { ... } }` block, and vanilla has one file with 4 groups (`democratic`, `communism`, `fascism`, `neutrality`) and 22 types. [vanilla-confirmed 1.19.4.2]
2. Groups go in `ruling_party`, `set_popularities`, `add_popularity`, `has_government`, `has_ideology_group`, `start_civil_war` (`ideology`, `ruling_party`) and bookmark `ideology`. [vanilla-confirmed 1.19.4.2]
3. Types (sub-ideologies, the keys of a group's `types = { }`) go in a character's `country_leader` `ideology`, `has_country_leader_ideology`, `has_ideology` and `set_country_leader_ideology`. [vanilla-confirmed 1.19.4.2]
4. Give a new group a new id and at least one type, because a leader's `ideology` must be a type, and never repeat a vanilla id (a second `neutrality` block was rejected at load). [docs] [game-tested 1.19.4.1]
5. To change a vanilla group, replace the whole `00_ideologies.txt` and keep every vanilla type. [unverified]
6. Every vanilla group sets `types`, `dynamic_faction_names`, `color`, `rules`, `modifiers`, `war_impact_on_world_tension`, `faction_impact_on_world_tension`, one `ai_<name> = yes`, `ai_ideology_wanted_units_factor` and `ai_give_core_state_control_threshold`, so copy a whole group. Optional: `faction_modifiers`, `can_collaborate` (communism, fascism) and `can_host_government_in_exile` (democratic). A type block is empty, except `can_be_randomly_selected = no` on four types. [vanilla-confirmed 1.19.4.2]
7. `rules` keys in vanilla are `can_create_collaboration_government`, `can_declare_war_on_same_ideology`, `can_force_government`, `can_send_volunteers`, `can_puppet`, `can_lower_tension`, `can_only_justify_war_on_threat_country` and `can_guarantee_other_ideologies`. `democratic` sets all eight, the others only `can_force_government`, `can_send_volunteers` and `can_puppet`, which the wiki marks required. [vanilla-confirmed 1.19.4.2] [docs]
8. The AI keys are `ai_democratic`, `ai_communist`, `ai_fascist` and `ai_neutral` (not `communism` or `neutrality`), and an invented `ai_test` failed to load with `Unexpected token`. [vanilla-confirmed 1.19.4.2] [game-tested 1.19.4.1]
9. `color = { r g b }` sits on the group with 0 to 255 values (`democratic` is 0 0 255). The wiki allows a type `color`, and no vanilla type sets one. [vanilla-confirmed 1.19.4.2] [docs]
10. `modifiers` takes country modifiers, every vanilla key is in `modifiers_documentation.md`, and `hidden_modifier = { }` wraps a hidden one. The wiki's `take_states_cost_factor` is not a modifier. [vanilla-confirmed 1.19.4.2]
11. `dynamic_faction_names` lists localisation keys (vanilla `FACTION_NAME_*` in `factions_l_english.yml`). [vanilla-confirmed 1.19.4.2]
12. `set_popularities` takes group keys only and must total exactly 100, and an unlisted group becomes 0. All 412 literal blocks in `history/` total 100, every country file has one, and they list only the four vanilla groups, so a new group starts at 0 everywhere. [vanilla-confirmed 1.19.4.2] [docs]
13. `set_politics` keys in vanilla are `ruling_party` (a group), `elections_allowed`, `election_frequency` (months), `last_election` (a date string), and `name` with `long_name` as party loc keys. The documentation omits the date and frequency keys. [vanilla-confirmed 1.19.4.2] [docs]
14. `add_popularity = { ideology = <group> popularity = <fraction> }` is a country effect with vanilla values such as 0.05 and 0.1. [vanilla-confirmed 1.19.4.2]
15. Party names have no generic key. Vanilla writes `<TAG>_<group>_party` and `_party_long`, or passes keys to `set_party_name = { ideology = <group> name = KEY long_name = KEY }`. [vanilla-confirmed 1.19.4.2]
16. Country triggers are `has_government = <group>` (or a country scope), `<group> > 0.3` for popularity (documented as `ideology_support_trigger`) and `has_elections = yes|no`. [vanilla-confirmed 1.19.4.2] [docs]
17. Rule names are used at runtime: vanilla Italy tests `has_rule = can_only_justify_war_on_threat_country` and then runs `set_rule = { can_only_justify_war_on_threat_country = no }`. `clear_rule` undoes it. [vanilla-confirmed 1.19.4.2]
18. Localisation: `<group>` (adjective), `<group>_noun`, `<group>_desc`. A type has `<type>` and `<type>_desc` only. `modifiers_l_english.yml` holds `<group>_drift`, `<group>_acceptance` and `<group>_drift_from_guarantees`. Files are UTF-8 with BOM, header `l_english:`. Country names use `<TAG>_<group>` with `_ADJ` and `_DEF`, and `<TAG>_<type>` exists too (`ARG_marxism`). [vanilla-confirmed 1.19.4.2]
19. Icons are `GFX_ideology_<group>_group`, `GFX_ideology_anarchism` (the only type icon) and `GFX_ideology_unknown`, uncompressed DDS, about 66 px, in `gfx/interface/ideologies/`. A mod needs its own `interface/*.gfx` entries. The country form `GFX_ideology_<TAG>_<group>_group` worked in the politics view. [vanilla-confirmed 1.19.4.2] [game-tested 1.19.4.1]
20. Flags are `gfx/flags/`, `medium/` and `small/` files named `<TAG>_<group>.tga` with `<TAG>.tga` as fallback, uncompressed 32-bit, and 300 of 362 vanilla tags have all four group flags. [vanilla-confirmed 1.19.4.2] [docs]
21. Generated leaders draw portraits from `portraits/*.txt` blocks `political = { <group> = { male = { ... } } }`, keyed by the four vanilla groups, so add one per new group. [vanilla-confirmed 1.19.4.2] [docs]
22. Vanilla booster advisors exist for three groups only (`communist_revolutionary`, `democratic_reformer`, `fascist_demagogue`, each with `<group>_drift = 0.1`), built by `generate_character` in `generic_advisors.txt`. `neutrality` has none. [vanilla-confirmed 1.19.4.2]
23. Vanilla scripts hard-code the four groups: `has_government = fascism` and the like are in `common/modifiers/00_static_modifiers.txt`, `common/autonomous_states/`, `common/on_actions/` and `common/factions/goals/`, and bookmarks use four `ideology` values. A new group matches none of them. [vanilla-confirmed 1.19.4.2]
24. Peace AI desires are in `common/peace_conference/ai_peace/` (see its `_documentation.md` and [Ai peace](../../../hoi4_wiki/ideology_modding.md#ai-peace)) and costs in `cost_modifiers/`, so write rules for a new group there. [docs]

## Silent failures

- A type name in `ruling_party`, `set_popularities`, `add_popularity` or `has_government`. Vanilla never does it, and the result is [unverified].
- Popularities that do not total 100 fail to be set, and a group left out sits at 0, so a new group has no support in that country. No logged line is known. [docs]
- A new group may also need a leader of one of its types to appear. [unverified]
- A group missing from the `portraits/` `political` pools may leave generated leaders without a portrait. [unverified]
- A missing localisation key shows the raw key and a missing sprite shows the error image. [docs]
- A repeated group id (`Duplicate database id`) and an unknown group key (`Unexpected token`) are load errors in `error.log`. The game still started after the repeated id. [game-tested 1.19.4.1]
- A file under `<mod>/<extra folder>/common/ideologies/` is ignored. [docs]
- `<newgroup>_drift` or `<newgroup>_acceptance` in an idea or trait: the documentation lists the four groups only, so the effect is [unverified].
- The vanilla conditions in item 23 are false for a new group, so ideology-gated modifiers, autonomy rules and faction goals skip it. [vanilla-confirmed 1.19.4.2]

## Validation

- `.tools/check.py localisation` parses `.yml` and checks tag names. It hard-codes the four groups when accepting `<TAG>_<group>` for `TAG`, so define plain `TAG`, `TAG_ADJ` and `TAG_DEF` too. It has no rule for `common/ideologies/`, so `<group>`, `_noun`, `_desc`, drift, party and faction-name keys are not proved. [docs] (`audit_localisation_static.py`)
- `.tools/check.py asset-wiring` proves a `spriteType` points at an existing file. It has no rule for implicit `GFX_ideology_*` names, and a flag passes when any `<TAG>.tga` or `<TAG>_<suffix>.tga` exists, so a missing flag for your group is not caught. [docs] (`audit_asset_wiring_static.py`)
- `hoi4.script_validate` checks effect and trigger bodies under a scope, and a true result covers only its `checksPerformed`. Its file mode lists events, decisions, focuses, scripted helpers and on-actions, not `common/ideologies/` or `history/countries/`, and it does not prove argument meaning such as group versus type. [docs] ([MCP integration](../../../docs/systems/hoi4_agent_tools_mcp_integration.md))
- Load errors and the politics screen need a game launch (`hoi4-debug-playtest`, `hoi4-live-playtest`). [docs]

## Unverified or open points

- What `can_be_boosted` does. The wiki lists it and no vanilla group sets it. [unverified]
- Whether `<newgroup> > 0.3`, `has_government = <newgroup>` and a bookmark `ideology = <newgroup>` work. [unverified]
- Whether `has_rule` reflects the ruling group's `rules` block. Vanilla Italy's use suggests it. [unverified]
- Order of `set_politics` and `recruit_character`. The leader skill says recruit first, but vanilla `history/countries/GER - Germany.txt` has `set_politics` at line 856 and `recruit_character = GER_adolf_hitler` at line 888. [vanilla-confirmed 1.19.4.2]
- `set_party_rule` has 0 vanilla uses and its documentation spells the key `ideologly`. [unverified]
