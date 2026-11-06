# HOI4 Diplomacy and War: Source map

Part of the [hoi4-diplomacy-war](../SKILL.md) skill. Read to find the authoritative documentation, wiki page and vanilla precedent for a diplomacy topic before you cite or mirror it.

## Contents

- Source map
- Decision procedure: which mechanism for which goal
- Scope and target rules for diplomacy effects
- Factions
- Subjects and autonomous states
- Diplomatic relations
- Wargoals, declaring war, and joining wars
- Peace: white peace, limited conferences, and conference hooks
- Territory, release, annexation, and puppets
- On actions for diplomacy and war
- Scripted diplomatic actions
- AI hooks
- Localisation and tooltips
- Validation
- Repository conventions
- Common mistakes
- Unverified or conflicting points

Argument tables and longer skeletons are in `references/syntax-reference.md` inside this skill folder. Intelligence agencies and operations are in `references/intelligence-operations.md`.
Read it when you need exact parameters of an effect or trigger, the list of autonomy game rules, faction rule types, or vanilla file indexes.

## Source map

`GAME` means the installed Hearts of Iron IV folder named in `CLAUDE.md`.
`WIKI` means the offline snapshot in `hoi4_wiki/` at the mod root.
Installed documentation outranks the wiki; record any disagreement.

| Topic | Authoritative text | Vanilla precedent |
| --- | --- | --- |
| Effect syntax | `GAME/documentation/effects_documentation.md` (search the effect name); `WIKI/effects.md` sections "Diplomacy", "Autonomy", "War", "Factions" | Decisions, events, and `GAME/common/scripted_effects/00_scripted_effects.txt` |
| Trigger syntax | `GAME/documentation/triggers_documentation.md` | |
| Factions: goals, rules, rule groups, templates, manifests, member upgrades | `GAME/common/factions/_documentation.md`; `WIKI/faction_modding.md` | `GAME/common/factions/templates/generic_factions.txt`, `rules/joining_rules.txt`, `rules/war_declaration_rules.txt`, `goals/faction_goals_short_term.txt` |
| Autonomous states | `WIKI/autonomy_state_modding.md` (there is no installed documentation file for this folder) | `GAME/common/autonomous_states/puppet.txt`, `dominion.txt`, `integrated_puppet.txt` |
| Wargoal types | No installed or wiki documentation page; read the vanilla definition | `GAME/common/wargoals/00_invasion.txt` |
| Opinion modifiers | Header comments of `GAME/common/opinion_modifiers/00_opinion_modifiers.txt`; wiki Effects, "Diplomacy" | `00_opinion_modifiers.txt`, `00_diplomatic.txt` |
| Scripted diplomatic actions | Commented template at the top of `GAME/common/scripted_diplomatic_actions/scripted_diplomatic_actions.txt` | The same file (documentation only in vanilla) |
| Peace conference cost modifiers and AI desires | `GAME/common/peace_conference/cost_modifiers/_documentation.md`, `ai_peace/_documentation.md` | `cost_modifiers/00_generic_peace.txt`, `ai_peace/00_misc.txt` |
| On actions | `GAME/common/on_actions/_documentation.md` (list, updated 2024-11); `WIKI/on_actions.md` (scopes) | `GAME/common/on_actions/00_on_actions.txt` |
| Rules, game-rule options | `WIKI/autonomy_state_modding.md` rule table; `set_rule` / `has_rule` in the effects and triggers docs | |
| Decision war warnings | `WIKI/decision_modding.md` ("Warning for war", missions) | |
| Tuning constants | `GAME/common/defines/00_defines.lua` (`NDefines.NCountry`, `NFactions`, `NAI`, wargoal and tension entries); `WIKI/defines.md` | |

Use the hoi4 MCP routes (`hoi4_reference_search`, `hoi4_reference_read`, `hoi4_source_lookup`, `hoi4_script_validate`) to cite exact lines.
If a route fails once, retry once with narrower input, then read the local file directly.

