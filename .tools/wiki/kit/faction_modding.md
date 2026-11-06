# Faction modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="104712" sources="common/factions/ common/defines/00_defines.lua common/ai_strategy/ common/peace_conference/ interface/factions/factions.gfx localisation/english/factions_l_english.yml documentation/effects_documentation.md documentation/triggers_documentation.md documentation/modifiers_documentation.md documentation/dynamic_variables_documentation.md documentation/console_commands_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `common/factions/_documentation.md`, all vanilla files under `common/factions/` (goals, rules, groups, templates, member upgrades, icon pool), the NFactions defines and the faction effects, triggers, modifiers and console commands.
- Kit blocks added: `faction-dlc-and-create`, `faction-folders`, `faction-goal-slots`, `faction-goal-placement`, `faction-goal-ai`, `faction-manifest-fix`, `faction-rule-types`, `faction-peace-rules`, `faction-rule-groups`, `faction-member-upgrades`, `faction-template-notes`, `faction-effects-more`, `faction-triggers-more`, `faction-modifiers-fix`, `faction-ai-and-defines` (bottom).
- Errors found: rule `type` tokens `joining_rule`, `war_declaration_rule` and `call_to_war_rule` are plural in the engine and in all vanilla files; member upgrades use `desc`, not `description`; the manifest example is unbalanced and puts `scale`, `range` and `progress_sections` outside `ratio_progress`, where vanilla has them inside; five modifier names in the last list no longer exist in the modifier documentation.
- Gaps left: whether the faction system still needs the "No Compromise, No Surrender" DLC for non-owners is not confirmed; the singular rule type tokens are probably dead but untested.
**1.19.4.1 re-check (2026-11-01).** Eight tagged statements depended on files the update changed (the call-to-war and war-declaration rule files, the AI strategy files, and vanilla-wide scans of `common/`, `events/` and `history/`), and all were re-measured together with the executable strings behind them. Two facts changed: 61 of 64 rules write `ai_will_do` (62 counted the doubled block in `dismissal_rule_offensive_war`), and one `create_faction_from_template` block, in `italy.txt`, sets `template` and `icon` without `name`. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="faction-dlc-and-create" at="section:without-dlc" -->
Two facts about creating factions in 1.19.3.

- The effect documentation calls `create_faction = LOC_KEY` deprecated and says to prefer `create_faction_from_template`, and that `create_faction` uses `FACTION_DEFAULT_EFFECT_TEMPLATE` if the "Deeper Factions" DLC is enabled (no vanilla file defines that name). Vanilla still uses `create_faction =` in 44 files and `create_faction_from_template` in 90. [docs] `documentation/effects_documentation.md`; [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`, files counted by script.
- `NDefines.NFactions.FACTION_DEFAULT_TEMPLATE = "faction_template_generic"` is the template used when none is named "when playing with NCNS", and `FACTION_DEFAULT_ICON = "GFX_faction_logo_generic"` is the icon of a generic faction without one. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. Whether a player without the "No Compromise, No Surrender" DLC gets templates, goals and rules is not confirmed here [unverified]. No vanilla template or rule file contains a `has_dlc` check. [vanilla-confirmed 1.19.4.1] `common/factions/templates/`, `common/factions/rules/`. One goal file does, for "La Resistance" (`common/factions/goals/faction_goals_short_term.txt`).

`create_faction_from_template` takes either the template id or a block: `create_faction_from_template = { template = <id> name = <loc key> icon = <GFX> color = { r g b } }`; `name`, `icon` and `color` are optional overrides (vanilla blocks set `template` with `name`, and sometimes `icon`, except one block in `common/national_focus/italy.txt` that sets only `template` and `icon`; no vanilla block sets `color`, and the documentation example writes it as fractions). [docs] `documentation/effects_documentation.md`; [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`.
<!-- kit:end id="faction-dlc-and-create" -->

<!-- kit:begin id="faction-folders" at="section:short-overview" -->
Layout of `common/factions/` in 1.19.4.1 and how big vanilla is. All rows: [vanilla-confirmed 1.19.4.1] `common/factions/`, counted by script; the list of blocks is also in `common/factions/_documentation.md` [docs].

| Folder or file | Holds | Vanilla |
| --- | --- | --- |
| `goals/faction_goals_short_term.txt`, `..._medium_term.txt`, `..._long_term.txt` | goals, `category` matches the file | 63, 72 and 21 goals |
| `goals/faction_manifests.txt` | manifests (`is_manifest = yes`) | 37 manifests |
| `rules/*.txt` | rules, one file per rule type | 64 rules in 9 files |
| `rules/groups/rule_groups.txt` | rule groups | 19 groups |
| `templates/*.txt` | faction templates | 69 templates in 10 files |
| `member_upgrades/member_upgrades.txt`, `member_upgrades/member_groups/member_upgrade_groups.txt` | manpower contribution upgrades and their group | 4 upgrades, 1 group |
| `upgrades/upgrades.txt`, `upgrades/groups/upgrade_groups.txt` | an older upgrade layout | both files are empty |
| `icons/pool.txt` | `faction_icon_pool = { icons = { GFX_... } }` | 20 generic faction logos |

The documentation lists the same templates, goals, rules, groups and member upgrade blocks but names no folders; the folder names above are the ones vanilla uses. Rule files: `joining_rules.txt`, `war_declaration_rules.txt`, `call_to_war_rules.txt`, `change_leader_rules.txt`, `dismissal_rules.txt`, `peace_rules.txt`, `manpower_contribution_rule.txt`, `faction_set_goal_rules.txt` and `goverment_in_exile_rules.txt` (sic).
<!-- kit:end id="faction-folders" -->

<!-- kit:begin id="faction-goal-slots" at="section:overview" -->
How many goals a faction holds, and the goal-related scopes.

- A faction holds one goal per category by default: `NFactions.MAX_NUM_SHORT_TERM_GOALS`, `MAX_NUM_MEDIUM_TERM_GOALS` and `MAX_NUM_LONG_TERM_GOALS` are all 1. `add_faction_goal_slot = { category = medium_term value = 1 }` (categories `short_term`, `medium_term`, `long_term`) adds slots; vanilla calls it from USA decisions and Chinese focuses, 8 files in all. `REPLACING_UNFINISHED_FACTION_GOAL_COST = 1` is the initiative cost of replacing an unfinished goal and `AI_DAYS_TO_SELECT_GOAL = 14` is the AI's pick interval. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`, `common/decisions/USA.txt`, `common/national_focus/china_nationalist_sea.txt`; [docs] `documentation/effects_documentation.md`. The console command `faction_goal_slot <category> <amount>` (alias `fgs`) does the same. [docs] `documentation/console_commands_documentation.md`.
- Scopes, from the documentation: `visible` and `available` run with ROOT = faction leader and FROM = the member viewing; `completed`, `cancel`, `complete_effect`, `cancel_effect`, `select_effect` and `remove_effect` run in the faction leader's scope. An empty `completed` means the goal is never completed. `select_effect` and `remove_effect` run only when the goal is chosen or removed after game start. [docs] `common/factions/_documentation.md`.
- `group` feeds the UI filter. The documentation says the filter icon is the sprite `GFX_<group>` and its name the loc key `<group>_FACTION_GOAL_FILTER`. Vanilla reuses the focus filters (`FOCUS_FILTER_ANNEXATION` 40 goals, `FOCUS_FILTER_CONSOLIDATION` 40, `FOCUS_FILTER_NAVY_XP` 16, and others) and one custom group, `resources_to_market_icon` (28 goals), whose loc key `resources_to_market_icon_FACTION_GOAL_FILTER` is in `localisation/english/factions_l_english.yml`. [docs] `common/factions/_documentation.md`; [vanilla-confirmed 1.19.3] `common/factions/goals/`.
- `allowed` and `locked_goal` are not in the documentation but vanilla uses them (`allowed` in 107 goals, `locked_goal = yes` in one long-term goal). [vanilla-confirmed 1.19.3] `common/factions/goals/`.
<!-- kit:end id="faction-goal-slots" -->

<!-- kit:begin id="faction-goal-placement" at="section:arguments-of-ratio_progress" -->
Where the progress keys sit in vanilla, and the collection forms it uses. All lines: [vanilla-confirmed 1.19.3] `common/factions/goals/faction_manifests.txt` and the three goal files.

- `range`, `scale`, `reversed` and `progress_sections` are written inside `ratio_progress = { }` in the vanilla manifests (91 matching lines in `faction_manifests.txt`); every manifest has only `name`, `description`, `is_manifest` and `ratio_progress` at its top level. `auto_complete = yes` is written on the goal itself, outside `ratio_progress` (3 medium-term goals). The documentation also shows `progress_sections` in a plain `progress = { }` block, which no vanilla goal uses.
- A `progress_sections` entry may have only `min` (`manifest_fulfilled = { min = @manifest_fulfilled_value ... }` with the file constant `@manifest_fulfilled_value = 0.75`); `max` is then simply absent. Each section holds `modifier`, and the documentation names `rule` as well. `on_activate` and `on_deactivate` are disabled for faction goals. [docs] `common/factions/_documentation.md`.
- Collections take three forms: `total_amount_collection = collection:states_on_my_continent`, `= game:all_states`, or a block `completed_amount_collection = { input = collection:the_northern_mandate_states operators = { limit = { is_controlled_by_ROOT_or_ally = yes } } name = COLLECTION_FACTION_CONTROLS_NORTHERN_MANDATE }` where `name` is a loc key for the tooltip line. `input = game:scope` with `operators = { faction_members }` walks the faction. ROOT inside them is the faction leader. See [Collection modding](collection_modding.md) for the input and operator syntax.
- Fixed amounts also accept variables: one manifest uses `total_amount = global.global_resource_extracted_total` and `completed_amount = faction_resource_extracted_total` with `total_amount_custom_tooltip` and `completed_amount_custom_tooltip`.
- The documentation says `total_amount` and `total_amount_collection` are mutually exclusive, and so are `completed_amount` and `completed_amount_collection`; mixing a total collection with a fixed completed amount is allowed, as the wiki says. [docs] `common/factions/_documentation.md`.
<!-- kit:end id="faction-goal-placement" -->

<!-- kit:begin id="faction-goal-ai" at="section:ai" -->
The documentation's goal `ai_will_do` uses `factor` (example `factor = 200`) and runs in the scope of the faction member that would pick the goal. Vanilla writes it in 153 of 156 goals. [docs] `common/factions/_documentation.md`; [vanilla-confirmed 1.19.3] `common/factions/goals/`. Faction initiative spending by the AI is a separate system, see the end of this page.
<!-- kit:end id="faction-goal-ai" -->

<!-- kit:begin id="faction-manifest-fix" at="section:example-code-of-manifest" -->
The manifest example above is missing two closing braces, and its indentation puts `scale`, `reversed`, `range` and `progress_sections` beside `ratio_progress`. Vanilla has them inside it (see `faction-goal-placement` above). A balanced manifest in the vanilla shape, shortened from `faction_manifest_regional_expansionism`:

```text
faction_manifest_regional_expansionism = {
    name = regional_expansionism_goal_name
    description = regional_expansionism_goal_desc
    is_manifest = yes
    ratio_progress = {
        total_amount_collection = collection:states_on_my_continent
        completed_amount_collection = collection:faction_states_on_my_continent
        range = { max = 0.67 }
        scale = { party_popularity_stability_factor = 0.10 }
        progress_sections = {
            manifest_fulfilled = {
                min = 0.75
                modifier = { monthly_population = 0.15 generate_wargoal_tension = -0.15 }
            }
        }
    }
}
```

Example: [vanilla-confirmed 1.19.3] `common/factions/goals/faction_manifests.txt` (the vanilla file writes `min = @manifest_fulfilled_value`). A template names its manifest with `manifest = <id>`, and a manifest sets no `category`.
<!-- kit:end id="faction-manifest-fix" -->

<!-- kit:begin id="faction-rule-types" at="section:syntax" -->
The rule `type` tokens in the table above are wrong for three rows, and one type is missing.

| Documented token | Token vanilla uses | Rules in vanilla |
| --- | --- | --- |
| `joining_rule` | `joining_rules` | 24 |
| `war_declaration_rule` | `war_declaration_rules` | 11 |
| `call_to_war_rule` | `call_to_war_rules` | 5 |
| `change_leader_rules` | `change_leader_rules` | 5 |
| `member_rules` | `member_rules` | 2 |
| `peace_conference_rules` | `peace_conference_rules` | 7 |
| (not documented) | `dismissal_rules` | 7 |
| (free token) | `contribution_rule` | 3 |

All rows: [vanilla-confirmed 1.19.4.1] `common/factions/rules/*.txt`, counted by script. The plural strings `joining_rules`, `war_declaration_rules`, `call_to_war_rules`, `change_leader_rules`, `dismissal_rules`, `member_rules` and `peace_conference_rules` are also standalone strings in `hoi4.exe`; the singular `joining_rule`, `war_declaration_rule` and `call_to_war_rule` that the documentation and the table above give are not, and neither is `contribution_rule`, which only works through its `effect` block (see below). Because `type` accepts any token, a rule typed `joining_rule` is probably accepted and then never evaluated as a joining rule [unverified]. The documentation lists the singular tokens as the special ones. [docs] `common/factions/_documentation.md`. Copy the vanilla spelling.

More facts about rule keys, from the documentation and vanilla:

- `dismissal_rules` rules put their condition in `dismiss_member_trigger`; `member_rules` has two vanilla uses: `goals_only_faction_leader` (a `trigger` of `is_faction_leader = yes`, which limits who may set goals) and `government_in_exile_allowed` (`government_in_exile_allowed_trigger`). The wiki line "can change faction goals (documentation might be wrong)" is right for the first; the documentation's "can become government in exile" describes the second. [vanilla-confirmed 1.19.3] `common/factions/rules/faction_set_goal_rules.txt`, `goverment_in_exile_rules.txt`.
- `contribution_rule` rules (`manpower_contribution_small`, `_medium`, `_high`) use `available = { has_faction_military_unlocked = yes }` and `effect = { set_faction_member_upgrade_min = { upgrade = faction_manpower_sharing1 } }` to set the minimum member upgrade. [vanilla-confirmed 1.19.3] `common/factions/rules/manpower_contribution_rule.txt`.
- `available` and `can_remove` do not stop `set_faction_rule` or `remove` effects; they only gate the player's choice. Rule `ai_will_do` runs in the faction leader's scope and a value of 0 or less means the AI never picks the rule. Vanilla writes `ai_will_do = { base = 0 modifier = { add = 1 ... } }` (61 of 64 rules). The rule name is shown through the loc key of the rule id with Country and Faction loc scopes (`joining_rule_non_fascist` in `localisation/english/factions_l_english.yml`). [docs] `common/factions/_documentation.md`; [vanilla-confirmed 1.19.4.1] `common/factions/rules/`.
- The game rule table earlier on this page is the autonomy `rule` table. It has one name the game does not know, one missing name and four names vanilla never uses; see [Autonomy state modding](autonomy_state_modding.md), block `autonomy-rule-list-fixes`, for the corrected list. That table belongs to `rule = { }` in autonomy states and progress sections, not to faction rules.
<!-- kit:end id="faction-rule-types" -->

<!-- kit:begin id="faction-peace-rules" at="section:modifier" -->
Peace rules in vanilla: 7 rules of type `peace_conference_rules` in `common/factions/rules/peace_rules.txt` (`faction_peace_rule_puppeting_focus`, `_no_puppeting`, `_liberation_focus`, `_ideology_focus`, `_conquest_focus`, `faction_peace_take_claimed_focus`, `faction_peace_china_focus`). Each lists names from `common/peace_conference/cost_modifiers/` in `peace_action_modifiers = { }` and adds a `modifier = { custom_modifier_tooltip = ... }` line for the tooltip. `rule_group_peace_rules` holds them all. [vanilla-confirmed 1.19.3] `common/factions/rules/peace_rules.txt`, `common/factions/rules/groups/rule_groups.txt`. The cost modifier syntax and how modifiers multiply are on [Peace conference modding](peace_conference_modding.md).
<!-- kit:end id="faction-peace-rules" -->

<!-- kit:begin id="faction-rule-groups" at="section:syntax-1" -->
In vanilla `rule_groups.txt` every `default_rule` line is commented out (`#default_rule = ...`), so no vanilla group sets one; the starting rules come from each template's `default_rules`, which the documentation says override the groups' defaults. Group ids in vanilla: `rule_group_ideology`, `rule_group_geographical`, `rule_group_war_relation`, `rule_group_dismissal_ideology`, `rule_group_dismissal_actions`, `rule_group_war_declaration_declarer`, `rule_group_call_to_war`, `rule_group_peace_rules`, `rule_group_leader_faction` and others (19 in all). A rule that is in no group never shows up. [vanilla-confirmed 1.19.3] `common/factions/rules/groups/rule_groups.txt`; [docs] `common/factions/_documentation.md`.
<!-- kit:end id="faction-rule-groups" -->

<!-- kit:begin id="faction-member-upgrades" at="section:group" -->
The key for the text of an upgrade or a group is `desc`, not `description`: the documentation lists `name`, `desc`, `icon`, `upgrade_cost`, `bonus` for an upgrade and `name`, `desc`, `icon`, `upgrades` for a group, and the vanilla files use `desc` (`FACTION_MANPOWER_CONTRIBUTION_VALUE_DESC`). [docs] `common/factions/_documentation.md`; [vanilla-confirmed 1.19.3] `common/factions/member_upgrades/`.

Vanilla defines 4 upgrades in `common/factions/member_upgrades/member_upgrades.txt` (`manpower_contribution_full_enable` with `bonus = 0.0`, `faction_manpower_sharing1` to `3` with 0.05, 0.1 and 0.15) and the group `faction_member_upgrade_manpower_group` with `default_upgrade = manpower_contribution_full_enable`, `upgrade_type = faction_member_upgrade_manpower` and `icon = GFX_manpower_contribution`. The documentation says `faction_member_upgrade_manpower` is the only upgrade type with code support and that its `bonus` is the percentage of a country's manpower moved into the faction pool. No vanilla upgrade sets `upgrade_cost`. [vanilla-confirmed 1.19.3] `common/factions/member_upgrades/member_groups/member_upgrade_groups.txt`.

Related script: `set_faction_member_upgrade_min = { upgrade = <id> }` (the documentation example misspells it `set_faction_upgrade_min`), `set_faction_upgrade = <token>` and the trigger `faction_upgrade_level > <token>`. Vanilla uses only `set_faction_member_upgrade_min` (3 times, in contribution rules); `set_faction_upgrade` and `faction_upgrade_level` are documented and not used. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`; [vanilla-confirmed 1.19.4.1] `common/factions/rules/manpower_contribution_rule.txt`.
<!-- kit:end id="faction-member-upgrades" -->

<!-- kit:begin id="faction-template-notes" at="section:manifestrulesgoals" -->
Template facts for 1.19.3. [docs] `common/factions/_documentation.md` unless marked.

- `visible` empty means the template is never offered in the creation screen, which is how script-only templates are made; `available` empty means always available. Vanilla fallbacks use `visible = { always = no }`. Of 69 vanilla templates, 19 set `visible`, 9 set `available`, 19 set `can_leader_join_other_factions`; every one sets `manifest`, `goals`, `default_rules` and `icon`. [vanilla-confirmed 1.19.3] `common/factions/templates/`.
- `color` is documented by the wiki but no vanilla template sets it: the only lines are commented out with the note "this should default to faction leader's color". [vanilla-confirmed 1.19.3] `common/factions/templates/generic_factions.txt`.
- `name` is a loc key, but vanilla also has literal values such as `name = Axis`. [vanilla-confirmed 1.19.3] `common/factions/templates/axis.txt`.
- `goals` takes ids or inline definitions, at most one per category by default (see `faction-goal-slots`).
- Logo sprites: `GFX_faction_logo_axis` has `noOfFrames = 2` and a 200 by 100 texture; the `GFX_faction_logo_axis_miniature` sprite is a separate 32 by 32 texture. 29 `_miniature` sprites are defined in the same file. [vanilla-confirmed 1.19.3] `interface/factions/factions.gfx` and the DDS headers.
<!-- kit:end id="faction-template-notes" -->

<!-- kit:begin id="faction-effects-more" at="section:list-of-faction-related-effects" -->
Faction effects in the 1.19.3 effect documentation that the list above lacks. All rows: [docs] `documentation/effects_documentation.md`.

| Effect | Use |
| --- | --- |
| `add_faction_goal_slot` | `{ category = short_term/medium_term/long_term value = 1 }`, adds goal slots; used in vanilla |
| `set_faction_member_upgrade_min` | `{ upgrade = <member upgrade id> }`, sets the minimum contribution level; used in vanilla |
| `set_faction_upgrade` | `= <token>`, sets a member upgrade; not used in vanilla |
| `set_faction_military_unlocked` | `= yes`, unlocks the faction's military section; used in 2 vanilla files |
| `set_faction_research_unlocked` | `= yes`, unlocks the faction's research section; used in 1 vanilla file |
| `every_faction_member` | scope iterator over the faction (only the country itself if it has none), with `limit`, `random_select_amount`, `tooltip`, `display_individual_scopes` |

`create_faction` is marked deprecated in the documentation, see `faction-dlc-and-create`.
<!-- kit:end id="faction-effects-more" -->

<!-- kit:begin id="faction-triggers-more" at="section:list-of-faction-related-triggers" -->
Faction triggers in the 1.19.3 trigger documentation that the list above lacks. All rows: [docs] `documentation/triggers_documentation.md`, country scope.

| Trigger | Use |
| --- | --- |
| `is_faction_leader`, `is_in_faction`, `is_in_faction_with` | Membership checks; the last takes a country |
| `num_faction_members` | `num_faction_members > 10` |
| `faction_upgrade_level` | `faction_upgrade_level > <upgrade token>` |
| `has_faction_military_unlocked`, `has_faction_research_unlocked` | `= yes/no` |
| `faction_goal_fulfillment` | `{ goal = <id> value > 0.5 }`; the value operators `>` and `<` can repeat |
| `compare_ideology_with_faction` | `{ value > 0.5 leader = FROM }`, ideology support of the ruling party for the faction it wants to join |
| `can_assign_supportive_scientist_to_faction` | free supportive scientist slot, takes a specialization |

Dynamic variables for the same data: `faction_leader`, `faction_members` (array), `faction_manifest_fulfillment`, `faction_power_projection`, `faction_influence_score`, `faction_influence_ratio`, `faction_influence_rank`, `faction_resource_extracted@<resource>`, `faction_resource_extracted_total` and `num_faction_members`. [docs] `documentation/dynamic_variables_documentation.md`.
<!-- kit:end id="faction-triggers-more" -->

<!-- kit:begin id="faction-modifiers-fix" at="section:list-of-faction-related-modifiers" -->
Only `faction_influence_war_score_factor` of the six modifiers above is in the 1.19.3 modifier documentation. The other five (`faction_influence_industrial_capacity_factor`, `faction_influence_garrison_support_provider_factor`, `faction_influence_garrison_support_reciver_factor`, `faction_influence_expeditionary_force_provider_factor`, `faction_influence_expeditionary_force_reciver_factor`) appear only in the faction documentation text, not in the modifier documentation or any vanilla script. The matching weights are now defines in `NDefines.NFactions` (`FACTION_INFLUENCE_INDUSTRIAL_CAPACITY_FACTOR` 5, `FACTION_INFLUENCE_GARRISON_SUPPORT_PROVIDER_FACTOR` 0.001, `FACTION_INFLUENCE_EXPEDITIONARY_FORCE_PROVIDER_FACTOR` 0.01 and so on). Do not use the five names as modifiers. [docs] `documentation/modifiers_documentation.md` (names absent); [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` (the defines).

Faction modifiers that do exist in the modifier documentation: `faction_influence_contribution_factor`, `faction_influence_war_score_factor`, `faction_subject_contribution_gain`, `faction_trade_opinion_factor` and `join_faction_tension`. [docs] `documentation/modifiers_documentation.md`.
<!-- kit:end id="faction-modifiers-fix" -->

<!-- kit:begin id="faction-ai-and-defines" at="bottom" -->
## AI spending of faction initiative, defines and console

**AI strategy types.** The AI spends faction initiative (FI) according to `ai_strategy` blocks of type `spent_faction_initiative_priority` with an `id` and a `value`. Valid ids: `program`, `unlock_doctrine_sharing`, `unlock_faction_commander`. Intelligence advisor roles use their own types: `become_spymaster`, `become_head_of_crypto`, `become_head_of_counter_intel`, `become_head_of_operations`. Rule choices are weighted by the rule's own `ai_will_do`. [docs] `common/factions/_documentation.md`; [vanilla-confirmed 1.19.4.1] `common/ai_strategy/default.txt`, `ENG.txt`, `GER.txt`, `USA.txt`. See [AI modding](ai_modding.md) for the strategy block format.

```text
default_add_faction_facility = {
    enable = { always = yes }
    abort_when_not_enabled = yes
    ai_strategy = {
        type = spent_faction_initiative_priority
        id = program
        value = 5
    }
}
```

Example: [docs] `common/factions/_documentation.md` (same block as quoted there).

**Defines** (`NDefines.NFactions`). All values: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

| Define | Value | Meaning |
| --- | --- | --- |
| `FACTION_INITIATIVE_CHANGE_RULE_COST` | 1 | FI cost of changing a rule |
| `FACTION_DOCTRINE_SHARING_UNLOCK_COST` | 1 | FI cost of unlocking doctrine sharing for one folder |
| `FACTION_UNLOCK_COMMANDER_COST` | 1 | FI cost of creating a faction theater |
| `FACTION_REPLACE_COMMANDER_COST` | 1 | FI cost of replacing another country's theater commander |
| `ASSIGN_FACILITY_TO_FACTION_INITIATIVE_COST` | 1 | FI cost of assigning a facility to the faction |
| `PASSIVE_INITIATIVE_GENERATION` | 0.015 | FI per day, scaled by manifest progress and influence share |
| `MAX_FACTION_THEATERS` | 4 | Most theaters a faction can have |
| `MAX_PROJECT_COUNT` | 3 | Most projects a faction can have |
| `BECOME_FACTION_LEADER_INFLUENCE_THRESHOLD` | 0.4 | Influence share needed to take over leadership |
| `FACTION_INFLUENCE_LEADER_BONUS` | 200 | Influence a leader gets for leading |
| `FACTION_DEFAULT_TEMPLATE`, `FACTION_DEFAULT_ICON` | `faction_template_generic`, `GFX_faction_logo_generic` | Defaults for a template-less faction |

**Console commands.** `faction_initiative <amount> [tag]` (alias `fi`) adds FI; `faction_influence <amount> [tag]` (alias `finf`) adds stored influence; `faction_goal_slot <category> <amount>` (alias `fgs`); `faction_unlock military` or `research` (alias `fu`) unlocks a faction section. [docs] `documentation/console_commands_documentation.md`.

Peace rules and their cost modifiers are covered on [Peace conference modding](peace_conference_modding.md); goal collections on [Collection modding](collection_modding.md).
<!-- kit:end id="faction-ai-and-defines" -->
