# Game rule modding

*Kit page: written by the Agentic HOI4 Modding Kit from the Hearts of Iron IV 1.19.3.0 game files and re-checked against 1.19.4.1. The wiki has no page for this topic. CC BY-SA 3.0 (see LICENSE.txt).*
<!-- kit:page -->

<!-- kit:begin id="review" at="top" build="1.19.4.1" checked="2026-11-01" sources="common/game_rules/ common/achievements.txt common/on_actions/ common/scripted_triggers/ common/ai_strategy/ common/ai_strategy_plans/ common/operations/ documentation/triggers_documentation.md interface/game_rules.gfx localisation/english/game_rules_l_english.yml" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Written from: the header comment and all 86 rules of `common/game_rules/00_game_rules.txt`, every `has_game_rule` use in vanilla script (2253 calls, counted by folder, rule and option), the two rule triggers in `documentation/triggers_documentation.md`, the rule sprites and `game_rules_l_english.yml`.
The wiki covers the file format in a section of [Bookmark modding](<bookmark_modding.md#Game_rules_2>). This page adds the 1.19.3 key census, the script-side patterns and the traps. The wiki redirect "Game rules" points at Custom difficulty, which is a different system.
Gaps left: how the engine matches rule and option names (case), what a missing rule evaluates to, and the six hard-coded rules are inferred from vanilla only.
**1.19.4.1 re-check (2026-11-01).** Ten statements depended on files the update changed (achievements, on actions, diplomacy triggers, the game rules localisation, and every script file that the has_game_rule counts cover), and all ten were re-measured on the installed files. Two numbers moved: the total of has_game_rule calls is now 2256 (the review text above says 2253), and 17 rule ids (was 18) differ from their definition only by case. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

## Table of contents

- [Overview](#Overview)
- [File format](#File_format)
  - [Rule keys](#Rule_keys)
  - [Option keys](#Option_keys)
  - [Default option and achievements](#Default_option_and_achievements)
  - [Groups](#Groups)
  - [DLC filters](#DLC_filters)
- [Localisation and GFX](#Localisation_and_GFX)
- [Reading a rule in script](#Reading_a_rule_in_script)
  - [Patterns in vanilla](#Patterns_in_vanilla)
  - [AI behaviour rules](#AI_behaviour_rules)
  - [Hard-coded rules](#Hard-coded_rules)
- [Related systems](#Related_systems)
- [Minimal example](#Minimal_example)
- [Traps](#Traps)

---

A game rule is a named setting with a short list of options that the player picks in the game setup. The rule file only declares the setting and its texts. A rule changes nothing by itself: script reads it with `has_game_rule`, or the engine reads it for a few hard-coded rules. [vanilla-confirmed 1.19.4.1] `common/game_rules/00_game_rules.txt` and a search of all vanilla script for `has_game_rule`.

## Overview <a id="Overview"></a>

- Rules live in `common/game_rules/*.txt`. Vanilla has one file, `00_game_rules.txt`, with 86 root blocks. The block name is the rule id. [vanilla-confirmed 1.19.3] `common/game_rules/00_game_rules.txt`.
- The header comment of that file documents the format: `name`, `required_dlc`, `desc`, `group`, `icon` and `option` / `default` blocks with `name`, `text` and `allow_achievements`. [vanilla-confirmed 1.19.3] header of `00_game_rules.txt`.
- Of the 86 rules, 51 are AI behaviour rules, 15 set up the world at game start, 11 are about foreign policy, and the rest are gameplay, peace score, covert action and UI rules. [vanilla-confirmed 1.19.3] counted by `group` in `00_game_rules.txt`.

## File format <a id="File_format"></a>

### Rule keys <a id="Rule_keys"></a>

Key counts are over the 86 vanilla rules. [vanilla-confirmed 1.19.3] `00_game_rules.txt`.

| Key | Value | Used by | Meaning |
| --- | --- | --- | --- |
| `name` | loc key | 86 | Rule title in the game rules screen. |
| `group` | loc key | 86 | Category of the rule. The header says a rule may sit in several groups; vanilla uses exactly one. |
| `option` | block | 434 in total | One choice. |
| `default` | block | 78 rules | One choice that is the default. Same keys as `option`. |
| `required_dlc` | DLC name in quotes | 61 | The rule is only available with that DLC. |
| `icon` | sprite name | 16 | Optional icon beside the title. |
| `desc` | loc key | 0 | Named in the header comment (rule long description), but no vanilla rule sets it. Every option has its own `desc` instead. |

The header comment lists `name`, `required_dlc`, `desc`, `group`, `icon`, `option` and `default`. [vanilla-confirmed 1.19.3] header of `00_game_rules.txt`.

### Option keys <a id="Option_keys"></a>

Counts over the 512 `option` and `default` blocks (434 plus 78). [vanilla-confirmed 1.19.3] `00_game_rules.txt`.

| Key | Used by | Meaning |
| --- | --- | --- |
| `name` | 512 | The option token. This is the value `has_game_rule` compares with. Quoted or bare; vanilla mixes both. |
| `text` | 512 | Loc key of the option label. Vanilla reuses shared keys such as `RULE_OPTION_FREE`. |
| `desc` | 512 | Loc key of the hover text. Not in the header comment, but present on every vanilla option. |
| `allow_achievements` | 170 | `yes` or `no`, see the next section. The header documents it. |
| `required_dlc` | 69 | The option only exists with that DLC. Not in the header comment. |
| `exclude_dlc` | 14 | The option only exists without that DLC. Not in the header comment. |

### Default option and achievements <a id="Default_option_and_achievements"></a>

- The first `option` is the default unless a block is written with the `default` token, which overrides that. [vanilla-confirmed 1.19.3] header of `00_game_rules.txt`.
- 78 rules use a `default` block. The 8 rules without one use their first option: `allow_licensing`, `allow_kick_faction`, `allow_take_over_faction`, `allow_coups`, `allow_party_boosting`, `allow_paratroopers`, `maximum_fort_level`, `allow_scorched_earth`. [vanilla-confirmed 1.19.3] `00_game_rules.txt`.
- A `default` block does not have to come first: in `peace_score_to_faction_leader` the option `YES` is listed first and `NO` is the default. [vanilla-confirmed 1.19.3] `00_game_rules.txt`.
- `allow_achievements = no` blocks achievements when that option is selected. If the key is missing it is `yes` for the default option and `no` for every other option. [vanilla-confirmed 1.19.3] header of `00_game_rules.txt`.
- Vanilla sets `allow_achievements = yes` on chosen non-default options, for example `AI_ONLY` in `allow_coups` and `FASCIST` in `GER_ai_behavior`. [vanilla-confirmed 1.19.3] `00_game_rules.txt`.
- The trigger `game_rules_allow_achievements = yes` is true when every active rule option allows achievements. It is in the `possible` block of the vanilla achievements (293 lines in `common/achievements.txt`). [docs] `documentation/triggers_documentation.md`; [vanilla-confirmed 1.19.4.1] `common/achievements.txt`.
- The wiki's Bookmark modding page says a modded game already has another checksum and no achievements, so `allow_achievements` changes nothing in a mod. [unverified]

### Groups <a id="Groups"></a>

- A group is only a string. No block defines it; the string is the loc key of the group name. [vanilla-confirmed 1.19.4.1] no `common/` file defines a group; `localisation/english/game_rules_l_english.yml` holds the names.
- Vanilla uses seven groups: `RULE_GROUP_AI_BEHAVIOR` (51 rules), `RULE_GROUP_GAME_SETUP` (15), `RULE_GROUP_GENERAL_FOREIGN_POLICY` (11), `RULE_GROUP_GAMEPLAY` (3), `RULE_GROUP_PEACE_SCORE` (3), `RULE_GROUP_COVERT_ACTIONS` (2), `RULE_GROUP_GENERAL_UI` (1). [vanilla-confirmed 1.19.3] `00_game_rules.txt`.
- A mod that uses a new group string only needs a loc entry for it. [unverified] inferred from the vanilla pattern.

### DLC filters <a id="DLC_filters"></a>

- Rule-level `required_dlc` appears on 61 rules, with 15 different DLC names. The names are written the way the game spells them, with no accents: `"La Resistance"`, `"Gotterdammerung"`. [vanilla-confirmed 1.19.3] `00_game_rules.txt`.
- Option-level `required_dlc` and `exclude_dlc` let one option id exist in two versions. `AST_ai_behavior` has two `RANDOM` options, one with `exclude_dlc = "Thunder at Our Gates"` and one with `required_dlc = "Thunder at Our Gates"`. [vanilla-confirmed 1.19.3] `00_game_rules.txt`.
- Base-game script reads rules that need a DLC. `allow_release_nations` has `required_dlc = "Death or Dishonor"` and `common/scripted_triggers/diplomacy_scripted_triggers.txt` reads it 49 times without a DLC check on that name. What a missing rule evaluates to is not documented; the wiki says error.log entries may follow. [vanilla-confirmed 1.19.4.1] for the reads, [unverified] for the result.

## Localisation and GFX <a id="Localisation_and_GFX"></a>

Vanilla keys are in `localisation/english/game_rules_l_english.yml`. [vanilla-confirmed 1.19.4.1]

| Text | Source key | Vanilla example |
| --- | --- | --- |
| Rule title | `name` | `RULE_ALLOW_COUPS: "Coups"` |
| Group title | the `group` string | `RULE_GROUP_COVERT_ACTIONS: "Covert Actions"` |
| Option label | option `text` | `RULE_OPTION_FREE: "Free"` (shared by many rules) |
| Option hover text | option `desc` | `RULE_ALLOW_COUPS_FREE_DESC` |
| Trigger tooltip | built in | `TRIGGER_HAS_GAME_RULE: "Game rule §Y$RULE$§! is set to the option §Y$OPTION$§!."` in `triggers_l_english.yml` |

- AI behaviour rule titles start with a flag token: `GER_AI_BEHAVIOR: "@GER Germany"`. [vanilla-confirmed 1.19.4.1] `game_rules_l_english.yml`.
- `$RULE$` and `$OPTION$` in the trigger tooltip are filled from the rule title and option label. [unverified]
- `icon` names a `spriteType`. Vanilla defines them in `interface/game_rules.gfx` with textures in `gfx/game_rules/`; 16 of 17 textures are 29 by 30 pixels and `allow_paratroopers.dds` is 32 by 32. [vanilla-confirmed 1.19.3] `interface/game_rules.gfx`, DDS headers.
- The icon is optional: 70 of the 86 vanilla rules have none. [vanilla-confirmed 1.19.3] `00_game_rules.txt`.

## Reading a rule in script <a id="Reading_a_rule_in_script"></a>

```text
has_game_rule = {
	rule = allow_coups
	option = FREE
}
```

- `has_game_rule` works in any scope and takes `rule` and `option`. It is true when the player set that rule to that option. [docs] `documentation/triggers_documentation.md`.
- Use it in any trigger block: `available`, `visible`, `allowed`, `limit`, `enable`, `allow_branch`, scripted triggers. Wrap it in `NOT = {}` for "any other option". [vanilla-confirmed 1.19.3] `common/operations/00_operations.txt` (`allowed` of `operation_coup_government`).
- There is no effect that sets a rule. Rules are fixed at game setup. [vanilla-confirmed 1.19.3] no effect name in `documentation/effects_documentation.md` mentions game rules.
- There is no way to read the chosen option as a value. Test each option with its own `has_game_rule` block. [docs] only the trigger above exists.

### Patterns in vanilla <a id="Patterns_in_vanilla"></a>

Counts are `has_game_rule` calls in `.txt` files. [vanilla-confirmed 1.19.4.1] whole game folder.

| Pattern | Where it appears | Example |
| --- | --- | --- |
| Diplomacy gate | `common/scripted_triggers/` (diplomacy triggers) | `allow_release_nations` 49 calls, `allow_access` 12, `allow_wargoals` 10, `allow_lend_lease` 10 |
| Covert action gate | `common/operations/`, `common/scripted_triggers/` | `allow_coups` in `operation_coup_government` and the coup triggers |
| Focus branch visibility | `common/national_focus/` (`allow_branch`), 1014 calls | `obsolete_focus_branches_visibility`, options `HIDE` and `SHOW`; the scripted trigger `has_hide_rule` wraps the `HIDE` test |
| One-time world change | `on_startup` in `common/on_actions/00_on_actions.txt` and `04_mtg_on_actions.txt` (150 calls in on actions) | `germany_fragmentation_status` with `GERMANY_FRAGMENTED` calls `release` for the German states |
| AI plan choice | `common/ai_strategy/`, `common/ai_strategy_plans/` (125 files) | `enable` of a plan tests the rule or a country flag |

### AI behaviour rules <a id="AI_behaviour_rules"></a>

- All 51 AI behaviour rules have a `default` option named `DEFAULT` and an option `RANDOM`; 47 also have an option with `HISTORICAL` in its name. The other options are one per national path. [vanilla-confirmed 1.19.3] `00_game_rules.txt`.
- `RANDOM` is resolved once at game start. `on_startup` tests `option = RANDOM` (60 times in `common/on_actions/00_on_actions.txt`), rolls a `random_list` and sets a country flag such as `GER_AI_RANDOM_KAISER`. The plan's `enable` then reads `OR = { has_country_flag = GER_AI_RANDOM_KAISER has_game_rule = { rule = GER_ai_behavior option = KAISER } }`. Only one plan, `CHL_historical_strategy_plan.txt`, tests `RANDOM` itself, together with a flag. [vanilla-confirmed 1.19.4.1] `common/on_actions/00_on_actions.txt`, `common/ai_strategy_plans/GER_alternate_strategy_plan.txt`.
- See [AI modding](<ai_modding.md#AI_strategy_plans>) for plan syntax.

### Hard-coded rules <a id="Hard-coded_rules"></a>

- Six rules are never read by vanilla script: `allow_paratroopers`, `maximum_fort_level`, `allow_scorched_earth`, `peace_score_to_overlord`, `peace_score_to_faction_leader`, `peace_score_reset_low_scores`. Their effect must come from the engine; script can still test them with `has_game_rule`. [vanilla-confirmed 1.19.4.1] search of every `.txt` file for `has_game_rule`; engine reading is [unverified].
- The peace score rules go with defines such as `PEACE_SCORE_TRANSFERRED_TO_FACTION_LEADER = 0.1` and `PEACE_SCORE_RESET_LOW_SCORE_THRESHOLD = 0.05`. The comment above them says to update the matching loc keys when the values change. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

## Related systems <a id="Related_systems"></a>

- Difficulty settings (`common/difficulty_settings/`, the sliders in the same screen) are another system. See [Bookmark modding](<bookmark_modding.md#Difficulty_settings>).
- The `rule = { ... }` block inside an autonomy state sets permissions for the subject (for example `can_not_declare_war = yes`). It is unrelated to this page: see [Autonomous states](<autonomy_state_modding.md>). [vanilla-confirmed 1.19.3] `common/autonomous_states/colony.txt`.
- The documentation entry for `has_game_rule` is in [Triggers](<triggers.md>).

## Minimal example <a id="Minimal_example"></a>

Built on the vanilla `allow_coups` and `peace_score_to_overlord` blocks. [vanilla-confirmed 1.19.3] shape only; the names are made up.

`common/game_rules/my_mod_game_rules.txt`

```text
my_mod_secret_deals = {
	name = "RULE_MY_MOD_SECRET_DEALS"
	group = "RULE_GROUP_MY_MOD"
	default = {
		name = ALLOWED
		text = "RULE_MY_MOD_OPTION_ALLOWED"
		desc = "RULE_MY_MOD_SECRET_DEALS_ALLOWED_DESC"
	}
	option = {
		name = BLOCKED
		text = "RULE_MY_MOD_OPTION_BLOCKED"
		desc = "RULE_MY_MOD_SECRET_DEALS_BLOCKED_DESC"
	}
}
```

`localisation/english/my_mod_rules_l_english.yml`

```text
l_english:
 RULE_GROUP_MY_MOD: "My Mod"
 RULE_MY_MOD_SECRET_DEALS: "Secret deals"
 RULE_MY_MOD_OPTION_ALLOWED: "Allowed"
 RULE_MY_MOD_OPTION_BLOCKED: "Blocked"
 RULE_MY_MOD_SECRET_DEALS_ALLOWED_DESC: "Countries may make secret deals."
 RULE_MY_MOD_SECRET_DEALS_BLOCKED_DESC: "Nobody may make secret deals."
```

Reading it, for example in a decision:

```text
available = {
	has_game_rule = {
		rule = my_mod_secret_deals
		option = ALLOWED
	}
}
```

## Traps <a id="Traps"></a>

- Rule and option names in vanilla script do not always match the case of the definition: 17 rule ids differ only by case (script `SWE_AI_BEHAVIOR`, definition `SWE_ai_behavior`) and 4 option names do (`default` against `DEFAULT`). No vanilla call names a rule that does not exist, so the engine very likely ignores case. Copy the spelling of the definition anyway. [vanilla-confirmed 1.19.4.1] cross-check of all calls against `00_game_rules.txt`; case-insensitivity is [unverified].
- The same option token may appear in two option blocks of one rule when `required_dlc` or `exclude_dlc` separates them. Do not reuse a token otherwise. [vanilla-confirmed 1.19.3] `AST_ai_behavior`. Behaviour for plain duplicates is [unverified].
- `has_game_rule` with a rule or option that is spelled wrongly is not caught by the file format. Search your script for every `rule =` after you rename a rule. [unverified]
- A new rule changes script only: giving it a hard-coded effect is not possible. For a visible behaviour, add `has_game_rule` to the triggers, `allow_branch` blocks or on actions that should change. [unverified] inferred from the six vanilla rules that script never reads.

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list_of_modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on_actions.md>) • [Data structures](<data_structures.md>) • [Flags](<data_structures.md#Flags>) • [Event targets](<data_structures.md#Event_targets>) • [Country tag aliases](<data_structures.md#Country_tag_aliases>) • [Variables](<data_structures.md#Variables>) • [Arrays](<data_structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement_modding.md>) • [AI](<ai_modding.md>) • [AI focuses](<ai_focuses.md>) • [Autonomous states](<autonomy_state_modding.md>) • [Balances of power](<balance_of_power_modding.md>) • [Bookmarks/Scenarios](<bookmark_modding.md>) • [Game rules](<bookmark_modding.md#Game_rules>) • [Buildings](<building_modding.md>) • [Characters and traits](<character_modding.md>) • [Cosmetic tags](<cosmetic_tag_modding.md>) • [Countries](<country_creation.md>) • [Divisions](<division_modding.md>) • [Decisions](<decision_modding.md>) • [Doctrines](<doctrine_modding.md>) • [Equipment](<equipment_modding.md>) • [Events](<event_modding.md>) • [Factions](<faction_modding.md>) • [Ideas](<idea_modding.md>) • [Ideologies](<ideology_modding.md>) • [Military industrial organizations](<military_industrial_organization_modding.md>) • [National focuses](<national_focus_modding.md>) • [Resources](<resources_modding.md>) • [Scripted GUI](<scripted_gui_modding.md>) • [Technologies and doctrines](<technology_modding.md>)
- **Map**: [Map](<map_modding.md>) • [States](<state_modding.md>) • [Supply areas](<supply_areas_modding.md>) • [Strategic regions](<strategic_region_modding.md>)
- **Graphical**: [Interface](<interface_modding.md>) • [Graphical assets](<graphical_asset_modding.md>) • [Entities](<entity_modding.md>) • [Posteffects](<posteffect_modding.md>) • [Particles](<particle_modding.md>) • [Fonts](<font_modding.md>)
- **Cosmetic**: [Portraits](<portrait_modding.md>) • [Namelists](<namelist_modding.md>) • [Music](<music_modding.md>) • [Sound](<sound_modding.md>)
- **Other**: [Console commands](<console_commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod_structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection_modding.md>) • [Defines additions](<defines_additions.md>) • [Game rule modding](<game_rule_modding.md>) • [Intelligence operation modding](<intelligence_operation_modding.md>) • [Map mode modding](<map_mode_modding.md>) • [Occupation and resistance modding](<occupation_and_resistance_modding.md>) • [Peace conference modding](<peace_conference_modding.md>) • [Raid modding](<raid_modding.md>) • [Script constant modding](<script_constant_modding.md>) • [Special project modding](<special_project_modding.md>)
