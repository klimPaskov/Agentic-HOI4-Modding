# Game rule modding

A game rule is a named setting with a short list of options that the player picks in the game setup. The rule file only declares the setting and its texts. A rule changes nothing by itself: script reads it with `has_game_rule`, or the engine reads it for a few hard-coded rules.

## Overview

- Rules live in `common/game_rules/*.txt`. Vanilla has one file, `00_game_rules.txt`, with 86 root blocks. The block name is the rule id.
- The header comment of that file documents the format: `name`, `required_dlc`, `desc`, `group`, `icon` and `option` / `default` blocks with `name`, `text` and `allow_achievements`.
- Of the 86 rules, 51 are AI behaviour rules, 15 set up the world at game start, 11 are about foreign policy, and the rest are gameplay, peace score, covert action and UI rules.

## File format

### Rule keys

Key counts are over the 86 vanilla rules.

| Key | Value | Used by | Meaning |
| --- | --- | --- | --- |
| `name` | loc key | 86 | Rule title in the game rules screen. |
| `group` | loc key | 86 | Category of the rule. The header says a rule may sit in several groups; vanilla uses exactly one. |
| `option` | block | 434 in total | One choice. |
| `default` | block | 78 rules | One choice that is the default. Same keys as `option`. |
| `required_dlc` | DLC name in quotes | 61 | The rule is only available with that DLC. |
| `icon` | sprite name | 16 | Optional icon beside the title. |
| `desc` | loc key | 0 | Named in the header comment (rule long description), but no vanilla rule sets it. Every option has its own `desc` instead. |

The header comment lists `name`, `required_dlc`, `desc`, `group`, `icon`, `option` and `default`.

### Option keys

Counts over the 512 `option` and `default` blocks (434 plus 78).

| Key | Used by | Meaning |
| --- | --- | --- |
| `name` | 512 | The option token. This is the value `has_game_rule` compares with. Quoted or bare; vanilla mixes both. |
| `text` | 512 | Loc key of the option label. Vanilla reuses shared keys such as `RULE_OPTION_FREE`. |
| `desc` | 512 | Loc key of the hover text. Not in the header comment, but present on every vanilla option. |
| `allow_achievements` | 170 | `yes` or `no`, see the next section. The header documents it. |
| `required_dlc` | 69 | The option only exists with that DLC. Not in the header comment. |
| `exclude_dlc` | 14 | The option only exists without that DLC. Not in the header comment. |

### Default option and achievements

- The first `option` is the default unless a block is written with the `default` token, which overrides that.
- 78 rules use a `default` block. The 8 rules without one use their first option: `allow_licensing`, `allow_kick_faction`, `allow_take_over_faction`, `allow_coups`, `allow_party_boosting`, `allow_paratroopers`, `maximum_fort_level`, `allow_scorched_earth`.
- A `default` block does not have to come first: in `peace_score_to_faction_leader` the option `YES` is listed first and `NO` is the default.
- `allow_achievements = no` blocks achievements when that option is selected. If the key is missing it is `yes` for the default option and `no` for every other option.
- Vanilla sets `allow_achievements = yes` on chosen non-default options, for example `AI_ONLY` in `allow_coups` and `FASCIST` in `GER_ai_behavior`.
- The trigger `game_rules_allow_achievements = yes` is true when every active rule option allows achievements. It is in the `possible` block of the vanilla achievements (293 lines in `common/achievements.txt`).
- The wiki's Bookmark modding page says a modded game already has another checksum and no achievements, so `allow_achievements` changes nothing in a mod. (unverified)

### Groups

- A group is only a string. No block defines it; the string is the loc key of the group name. `localisation/english/game_rules_l_english.yml` holds the names.
- Vanilla uses seven groups: `RULE_GROUP_AI_BEHAVIOR` (51 rules), `RULE_GROUP_GAME_SETUP` (15), `RULE_GROUP_GENERAL_FOREIGN_POLICY` (11), `RULE_GROUP_GAMEPLAY` (3), `RULE_GROUP_PEACE_SCORE` (3), `RULE_GROUP_COVERT_ACTIONS` (2), `RULE_GROUP_GENERAL_UI` (1).
- A mod that uses a new group string only needs a loc entry for it. (unverified) inferred from the vanilla pattern. A test rule with a new group string and a loc entry loaded with no error.log line. The group label in the interface was not looked at.

### DLC filters

- Rule-level `required_dlc` appears on 61 rules, with 15 different DLC names. The names are written the way the game spells them, with no accents: `"La Resistance"`, `"Gotterdammerung"`.
- Option-level `required_dlc` and `exclude_dlc` let one option id exist in two versions. `AST_ai_behavior` has two `RANDOM` options, one with `exclude_dlc = "Thunder at Our Gates"` and one with `required_dlc = "Thunder at Our Gates"`.
- Base-game script reads rules that need a DLC. `allow_release_nations` has `required_dlc = "Death or Dishonor"` and `common/scripted_triggers/diplomacy_scripted_triggers.txt` reads it 49 times without a DLC check on that name. What a missing rule evaluates to is not documented; the wiki says error.log entries may follow. (unverified) for the result. The documentation says nothing about it.

## Localisation and GFX

Vanilla keys are in `localisation/english/game_rules_l_english.yml`.

| Text | Source key | Vanilla example |
| --- | --- | --- |
| Rule title | `name` | `RULE_ALLOW_COUPS: "Coups"` |
| Group title | the `group` string | `RULE_GROUP_COVERT_ACTIONS: "Covert Actions"` |
| Option label | option `text` | `RULE_OPTION_FREE: "Free"` (shared by many rules) |
| Option hover text | option `desc` | `RULE_ALLOW_COUPS_FREE_DESC` |
| Trigger tooltip | built in | `TRIGGER_HAS_GAME_RULE: "Game rule §Y$RULE$§! is set to the option §Y$OPTION$§!."` in `triggers_l_english.yml` |

- AI behaviour rule titles start with a flag token: `GER_AI_BEHAVIOR: "@GER Germany"`.
- `$RULE$` and `$OPTION$` in the trigger tooltip are filled from the rule title and option label. (unverified)
- `icon` names a `spriteType`. Vanilla defines them in `interface/game_rules.gfx` with textures in `gfx/game_rules/`; 16 of 17 textures are 29 by 30 pixels and `allow_paratroopers.dds` is 32 by 32.
- The icon is optional: 70 of the 86 vanilla rules have none.

## Reading a rule in script

```text
has_game_rule = {
	rule = allow_coups
	option = FREE
}
```

- `has_game_rule` works in any scope and takes `rule` and `option`. It is true when the player set that rule to that option.
- Use it in any trigger block: `available`, `visible`, `allowed`, `limit`, `enable`, `allow_branch`, scripted triggers. Wrap it in `NOT = {}` for "any other option".
- There is no effect that sets a rule. Rules are fixed at game setup.
- There is no way to read the chosen option as a value. Test each option with its own `has_game_rule` block.

### Patterns in vanilla

Counts are `has_game_rule` calls in `.txt` files.

| Pattern | Where it appears | Example |
| --- | --- | --- |
| Diplomacy gate | `common/scripted_triggers/` (diplomacy triggers) | `allow_release_nations` 49 calls, `allow_access` 12, `allow_wargoals` 10, `allow_lend_lease` 10 |
| Covert action gate | `common/operations/`, `common/scripted_triggers/` | `allow_coups` in `operation_coup_government` and the coup triggers |
| Focus branch visibility | `common/national_focus/` (`allow_branch`), 1014 calls | `obsolete_focus_branches_visibility`, options `HIDE` and `SHOW`; the scripted trigger `has_hide_rule` wraps the `HIDE` test |
| One-time world change | `on_startup` in `common/on_actions/00_on_actions.txt` and `04_mtg_on_actions.txt` (150 calls in on actions) | `germany_fragmentation_status` with `GERMANY_FRAGMENTED` calls `release` for the German states |
| AI plan choice | `common/ai_strategy/`, `common/ai_strategy_plans/` (125 files) | `enable` of a plan tests the rule or a country flag |

### AI behaviour rules

- All 51 AI behaviour rules have a `default` option named `DEFAULT` and an option `RANDOM`; 47 also have an option with `HISTORICAL` in its name. The other options are one per national path.
- `RANDOM` is resolved once at game start. `on_startup` tests `option = RANDOM` (60 times in `common/on_actions/00_on_actions.txt`), rolls a `random_list` and sets a country flag such as `GER_AI_RANDOM_KAISER`. The plan's `enable` then reads `OR = { has_country_flag = GER_AI_RANDOM_KAISER has_game_rule = { rule = GER_ai_behavior option = KAISER } }`. Only one plan, `CHL_historical_strategy_plan.txt`, tests `RANDOM` itself, together with a flag.
- See [AI modding](ai_modding.md#ai-strategy-plans) for plan syntax.

### Hard-coded rules

- Six rules are never read by vanilla script: `allow_paratroopers`, `maximum_fort_level`, `allow_scorched_earth`, `peace_score_to_overlord`, `peace_score_to_faction_leader`, `peace_score_reset_low_scores`. Their effect must come from the engine; script can still test them with `has_game_rule`. That the engine reads them is unverified.
- The peace score rules go with defines such as `PEACE_SCORE_TRANSFERRED_TO_FACTION_LEADER = 0.1` and `PEACE_SCORE_RESET_LOW_SCORE_THRESHOLD = 0.05`. The comment above them says to update the matching loc keys when the values change.

## Related systems

- Difficulty settings (`common/difficulty_settings/`, the sliders in the same screen) are another system. See [Bookmark modding](bookmark_modding.md#difficulty-settings).
- The `rule = { ... }` block inside an autonomy state sets permissions for the subject (for example `can_not_declare_war = yes`). It is unrelated to this page: see [Autonomous states](autonomy_state_modding.md).
- The documentation entry for `has_game_rule` is in [Triggers](triggers.md).

## Minimal example

Built on the vanilla `allow_coups` and `peace_score_to_overlord` blocks. The names are made up.

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

## Traps

- Rule and option names in vanilla script do not always match the case of the definition: 17 rule ids differ only by case (script `SWE_AI_BEHAVIOR`, definition `SWE_ai_behavior`) and 4 option names do (`default` against `DEFAULT`). No vanilla call names a rule that does not exist, so the engine very likely ignores case. Copy the spelling of the definition anyway. The engine does ignore case: `has_game_rule` matched the rule name in upper case and the option name in lower case, and both read TRUE.
- The same option token may appear in two option blocks of one rule when `required_dlc` or `exclude_dlc` separates them. Do not reuse a token otherwise. Behaviour for plain duplicates is unverified.
- `has_game_rule` with a rule or option that is spelled wrongly is not caught by the file format. Search your script for every `rule =` after you rename a rule. The game does report it when the script loads: a missing rule drew "has_game_rule: game rule <name> does not exist", a wrong option drew "game rule option <name> is not valid for the rule <rule>", and both tests evaluated FALSE.
- A new rule changes script only: giving it a hard-coded effect is not possible. For a visible behaviour, add `has_game_rule` to the triggers, `allow_branch` blocks or on actions that should change. (unverified) inferred from the six vanilla rules that script never reads.
