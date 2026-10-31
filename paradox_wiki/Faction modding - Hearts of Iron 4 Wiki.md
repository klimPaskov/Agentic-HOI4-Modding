# Faction modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Faction modding", revision 104712, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="104712" sources="common/factions/ common/defines/00_defines.lua common/ai_strategy/ common/peace_conference/ interface/factions/factions.gfx localisation/english/factions_l_english.yml documentation/effects_documentation.md documentation/triggers_documentation.md documentation/modifiers_documentation.md documentation/dynamic_variables_documentation.md documentation/console_commands_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `common/factions/_documentation.md`, all vanilla files under `common/factions/` (goals, rules, groups, templates, member upgrades, icon pool), the NFactions defines and the faction effects, triggers, modifiers and console commands.
- Kit blocks added: `faction-dlc-and-create`, `faction-folders`, `faction-goal-slots`, `faction-goal-placement`, `faction-goal-ai`, `faction-manifest-fix`, `faction-rule-types`, `faction-peace-rules`, `faction-rule-groups`, `faction-member-upgrades`, `faction-template-notes`, `faction-effects-more`, `faction-triggers-more`, `faction-modifiers-fix`, `faction-ai-and-defines` (bottom).
- Errors found: rule `type` tokens `joining_rule`, `war_declaration_rule` and `call_to_war_rule` are plural in the engine and in all vanilla files; member upgrades use `desc`, not `description`; the manifest example is unbalanced and puts `scale`, `range` and `progress_sections` outside `ratio_progress`, where vanilla has them inside; five modifier names in the last list no longer exist in the modifier documentation.
- Gaps left: whether the faction system still needs the "No Compromise, No Surrender" DLC for non-owners is not confirmed; the singular rule type tokens are probably dead but untested.
<!-- kit:end id="review" -->

## Table of contents

- [Basics](#Basics)
  - [Without DLC](#Without_DLC)
  - [With DLC](#With_DLC)
    - [Short overview](#Short_overview)
- [Goals](#Goals)
  - [Overview](#Overview)
  - [Structure](#Structure)
    - [Triggers](#Triggers)
    - [Effects](#Effects)
    - [Progression based goal](#Progression_based_goal)
      - [Arguments of `ratio_progress`](#Arguments_of_ratio_progress)
    - [AI](#AI)
    - [Code examples](#Code_examples)
      - [Short term goal code example](#Short_term_goal_code_example)
      - [Medium term goal code example](#Medium_term_goal_code_example)
      - [Long term goal code example](#Long_term_goal_code_example)
- [Manifests](#Manifests)
  - [Structure](#Structure_2)
    - [Progress](#Progress)
    - [Example code of manifest](#Example_code_of_manifest)
- [Rules](#Rules)
  - [Syntax](#Syntax)
    - [Triggers](#Triggers_2)
    - [Modifier](#Modifier)
    - [Effect](#Effect)
    - [AI block](#AI_block)
    - [Localisation](#Localisation)
    - [Rule groups](#Rule_groups)
      - [Syntax](#Syntax_2)
    - [Code examples](#Code_examples_2)
- [Member upgrades](#Member_upgrades)
  - [Syntax](#Syntax_3)
    - [Group](#Group)
- [Templates](#Templates)
  - [Syntax](#Syntax_4)
    - [Triggers](#Triggers_3)
    - [Manifest,rules,goals](#Manifest.2Crules.2Cgoals)
    - [Code example:](#Code_example:)
- [Triggers and Effects](#Triggers_and_Effects)
  - [List of faction-related effects](#List_of_faction-related_effects)
  - [List of faction-related triggers](#List_of_faction-related_triggers)
  - [List of faction-related modifiers](#List_of_faction-related_modifiers)

---

## Basics <a id="Basics"></a>

### Without DLC <a id="Without_DLC"></a>

If you don’t own dlc “**No Compromise, No Surrender”** then you don’t have access towards most of the new faction system. If you don’t want your mod to be dependent on dlc ownership but still want to use basic faction you can do [create_faction_from_template](<Effects - Hearts of Iron 4 Wiki.md>).

<!-- kit:begin id="faction-dlc-and-create" at="section:Without_DLC" -->
**Kit note** Two facts about creating factions in 1.19.3.

- The effect documentation calls `create_faction = LOC_KEY` deprecated and says to prefer `create_faction_from_template`, and that `create_faction` uses `FACTION_DEFAULT_EFFECT_TEMPLATE` if the "Deeper Factions" DLC is enabled (no vanilla file defines that name). Vanilla still uses `create_faction =` in 44 files and `create_faction_from_template` in 90. [docs] `documentation/effects_documentation.md`; [vanilla-confirmed 1.19.3] `common/`, `events/`, `history/`, files counted by script.
- `NDefines.NFactions.FACTION_DEFAULT_TEMPLATE = "faction_template_generic"` is the template used when none is named "when playing with NCNS", and `FACTION_DEFAULT_ICON = "GFX_faction_logo_generic"` is the icon of a generic faction without one. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. Whether a player without the "No Compromise, No Surrender" DLC gets templates, goals and rules is not confirmed here [unverified]. No vanilla template or rule file contains a `has_dlc` check.

`create_faction_from_template` takes either the template id or a block: `create_faction_from_template = { template = <id> name = <loc key> icon = <GFX> color = { r g b } }`; `name`, `icon` and `color` are optional overrides (vanilla blocks set `template` with `name`, and sometimes `icon`; no vanilla block sets `color`, and the documentation example writes it as fractions). [docs] `documentation/effects_documentation.md`; [vanilla-confirmed 1.19.3] `common/`, `events/`, `history/`.
<!-- kit:end id="faction-dlc-and-create" -->

### With DLC <a id="With_DLC"></a>

Faction with DLC is really modable in almost every aspect of it for you to change. Most of it based on [template](#Templates), that contains rest of components of factions. It contains [goals](#Goals), icon, color, rules, [manifests](#Manifests). To create faction you still use [create_faction_from_template](<Effects - Hearts of Iron 4 Wiki.md>).

#### Short overview <a id="Short_overview"></a>

- [Goals](#Goals) - “quest” for multiple countries or leader country
- [Rules](#Rules) - set of regulations used inside of faction
- Icon - visual logo of faction
- Color - color of faction used in faction map mode, if not specified uses leader color
- [Manifests](#Manifests) - global, continuous goal that used to give faction a modifier or a rule depending on the conditions.
- [Member upgrades](#Member_upgrades) - manpower sharing
- Template - a way to combine all above things

<!-- kit:begin id="faction-folders" at="section:Short_overview" -->
**Kit addition** Layout of `common/factions/` in 1.19.3 and how big vanilla is. All rows: [vanilla-confirmed 1.19.3] `common/factions/`, counted by script; the list of blocks is also in `common/factions/_documentation.md` [docs].

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

## Goals <a id="Goals"></a>

### Overview <a id="Overview"></a>

Faction’s goals are the way to have “quest” for multiple countries without using missions or events. There are three types of goals in the game, Short-term, Medium-term and Long-term. They are defined in

`common/factions/goals/*.txt` and every faction can have up to one of three types present in the game. **It's not mandatory for faction to start with goals.** Default scope is faction leader, FROM is faction member who views current goal. **FROM is not supported inside `complete_effect, remove_effect, cancel_effect`**.

<!-- kit:begin id="faction-goal-slots" at="section:Overview" -->
**Kit addition** How many goals a faction holds, and the goal-related scopes.

- A faction holds one goal per category by default: `NFactions.MAX_NUM_SHORT_TERM_GOALS`, `MAX_NUM_MEDIUM_TERM_GOALS` and `MAX_NUM_LONG_TERM_GOALS` are all 1. `add_faction_goal_slot = { category = medium_term value = 1 }` (categories `short_term`, `medium_term`, `long_term`) adds slots; vanilla calls it from USA decisions and Chinese focuses, 8 files in all. `REPLACING_UNFINISHED_FACTION_GOAL_COST = 1` is the initiative cost of replacing an unfinished goal and `AI_DAYS_TO_SELECT_GOAL = 14` is the AI's pick interval. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`, `common/decisions/USA.txt`, `common/national_focus/china_nationalist_sea.txt`; [docs] `documentation/effects_documentation.md`. The console command `faction_goal_slot <category> <amount>` (alias `fgs`) does the same. [docs] `documentation/console_commands_documentation.md`.
- Scopes, from the documentation: `visible` and `available` run with ROOT = faction leader and FROM = the member viewing; `completed`, `cancel`, `complete_effect`, `cancel_effect`, `select_effect` and `remove_effect` run in the faction leader's scope. An empty `completed` means the goal is never completed. `select_effect` and `remove_effect` run only when the goal is chosen or removed after game start. [docs] `common/factions/_documentation.md`.
- `group` feeds the UI filter. The documentation says the filter icon is the sprite `GFX_<group>` and its name the loc key `<group>_FACTION_GOAL_FILTER`. Vanilla reuses the focus filters (`FOCUS_FILTER_ANNEXATION` 40 goals, `FOCUS_FILTER_CONSOLIDATION` 40, `FOCUS_FILTER_NAVY_XP` 16, and others) and one custom group, `resources_to_market_icon` (28 goals), whose loc key `resources_to_market_icon_FACTION_GOAL_FILTER` is in `localisation/english/factions_l_english.yml`. [docs] `common/factions/_documentation.md`; [vanilla-confirmed 1.19.3] `common/factions/goals/`.
- `allowed` and `locked_goal` are not in the documentation but vanilla uses them (`allowed` in 107 goals, `locked_goal = yes` in one long-term goal). [vanilla-confirmed 1.19.3] `common/factions/goals/`.
<!-- kit:end id="faction-goal-slots" -->

### Structure <a id="Structure"></a>

`goal_id` - id of your goal, must be unique.

`name` - [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key for visible name of goal

`description` - [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key for visible description of goal

`category = short_term/medium_term/long_term` Determines to which category goal would be assigned,there’s no difference between categories, but it’s good practice to have easier goal in short_term, medium difficulty goal inside medium_term, and long term goal inside long_term.

`group = GROUP_ID` - group to sort goal, accepts [search filters](<National focus modding - Hearts of Iron 4 Wiki.md#Search_filters>) from focuses and any custom you make, creation of new one works exactly same as focus [search filters](<National focus modding - Hearts of Iron 4 Wiki.md#Search_filters>).

`locked_goal = { yes/no }` - makes goal "locked". Goal would become irreplaceable manually, unless you complete it.

`is_manifest = { yes/no }` - decide whether it's goal or [manifest](#Manifests). By default set to no (so it's a goal)

#### Triggers <a id="Triggers"></a>

`visible = { }`- is a [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block that continuously checks every frame if a condition was met, required to make the goal to be visible in the goal selection screen. Since it checks every frame, it's preferable to put country or DLC checks into allowed instead.

`available = { }` - is a [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block that continuously checks every frame if a condition was met, required to make the goal available to be chosen in the goal selection screen. If conditions aren't met the goal wouldn't be possible to select, but difference with visible is that it will still be visible and display why it's not available to be selected when hovered over.

`allowed = { }` - is a [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block that gets checked only at the game's start or when loading a save, primarily used to restrict an idea to a country (As `tag = BHR` or `original_tag = POL`) and/or a DLC (As `has_dlc = "One Step Back"`). If an goal's allowed is unfulfilled, it will never appear within the selection unless it becomes true on the save being reloaded; however, manual assignment via `add_faction_goal` bypasses the check. If left out, assumes to be always allowed. **This only checks once!**

`completed = { }`- is a [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block that decides if a goal has been completed. Here you are supposed to put all conditions of goal that you want faction to complete. Default scope is the leader of the faction.

`cancel = { }` - is a [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block that decides if a goal should be removed, once it's condition is true. Triggers the goal's cancel_effect.

#### Effects <a id="Effects"></a>

`complete_effect = { }` - is an [effect](<Effects - Hearts of Iron 4 Wiki.md>) block that executes effects for completing a goal, by default only the faction leader will get rewarded for completing goal. (Since default scope of goal is leader)

`select_effect = { }` - is an [effect](<Effects - Hearts of Iron 4 Wiki.md>) block that executes effects once a goal has been selected. **This block won't fire if goal is added through a faction template**

`remove_effect = { }` - is an [effect](<Effects - Hearts of Iron 4 Wiki.md>) block that executes effects once a goal has been removed. The only difference with `cancel_effect` is that this effect will be executed if goal has been changed, while other only runs once a goal has been canceled because the conditions in it's `cancel` trigger have been met.

`cancel_effect = { }` - is [an effect](<Effects - Hearts of Iron 4 Wiki.md>) block that execute effects once a goal has been cancelled. The only difference with `remove_effect` is that this effect will be executed if a goal has been canceled because it's cancel conditions have been met, the other will run if goal has been changed.

#### Progression based goal <a id="Progression_based_goal"></a>

Goals mainly use `completed` trigger with `complete_effect` to give rewards for complete goals. Even though it's primary way, it's not the only one to complete them. Ratio_progress is block that's turns goals into a continuous goals unlocking new potential way of using them. Imagine you want to base your goal around conquered land of certain faction or make it based on resource count of faction, maybe you want a quest to be complete once 80% of states in faction would have factories. That's all possible with ratio_progress.

`ratio_progress = { }` - is a block where you can do all those cool thing mentioned above.

##### Arguments of `ratio_progress` <a id="Arguments_of_ratio_progress"></a>

All these thing mentioned bellow must be used inside ratio_progress, otherwise they won't work.

`total_amount_collection = collection_id` - uses a collection to define the elements that are considered for completion.

`completed_amount_collection = collection_id` - uses a collection to check which elements in `total_amount_completion>` are complete

**Code example:**

```text
ratio_progress = {
		total_amount_collection = {
			input = collection:african_states
		}
		completed_amount_collection = {
			input = collection:african_states
			operators = {
				limit = {
					is_controlled_by_ROOT_or_ally = yes
		    }
		}
	}
}
```

*This code will make goal 100% done, once faction leader or any faction member controls all african states* For more collections or info on how to use them see `common/collections/_documentation.md`

`total_amount = MY_VALUE` - variable, or fixed value, that defines maximum amount.

`completed_amount = MY_OTHER_VALUE` - variable, or fixed value, that defines amount you have completed already.

**Code example:**

```text
ratio_progress = {
		total_amount = 10
		completed_amount = myVar # 8
}
```

*This code will make goal 100% done, once myVar will become 10, tooltip will show that you completed 8/10*

**You can't use the collection and non-collection versions of the same type e.g total_amount and total_amount_collection at the same time as they are mutually exclusive. However you can use total_amount_collection and completed_amount at the same time. Goal won't be completed if ratio reaches 100% unless auto_complete = yes used.**

`progress_sections = { }` - is a block that contains sections, sections work like sections in [bop](<Balance of power modding - Hearts of Iron 4 Wiki.md>). This can be used so that, when being within a certain threshold of completion, modifiers get enabled.

**Example code:**

```text
 progress_sections = {
      my_first_milestone = {
        min = 0
        max = 0.49
        modifier = {
          stability_factor = 0.05
        }
      }
      my_second_milestone = {
        min = 0.5
        max = 0.69
        modifier = {
          army_attack_factor = 0.05
        }
      }
      my_third_milestone = {
        min = 0.7
        max = 0.9
        modifier = {
          war_support_factor = 0.05
        }
      }
    }
```

`min = X` - minimal value for a milestone to become active. Percentual with 1 as maximum and 0 as minimum

`max = Y` - maximum value for a milestone to be active Percentual with 1 as maximum and 0 as minimum

`modifier = { }` - [modifier](<Modifiers - Hearts of Iron 4 Wiki.md>) a block that all members gets while a milestone is active.

`rule = { }` - rules apply to all members while a threshold is active.

**Game rule list**

The following game rules exist as possible options:

| Internal name | Localised name | Notes |
| --- | --- | --- |
| can_access_market | Can access International Market (Puppets and Overlords can always access each other's market) |  |
| can_be_spymaster | Can be Spy Master |  |
| can_boost_other_ideologies | Can boost popularity of other ideologies |  |
| can_boost_own_ideology | Can boost own party popularity in other countries |  |
| can_create_collaboration_government | Can create collaboration governments |  |
| can_create_factions | Can Create Factions |  |
| can_declare_war_on_same_ideology | Can declare war on country with the same ideology group without a war goal |  |
| can_declare_war_without_wargoal_when_in_war | Can declare war on a neighbor without a wargoal when at war with a major |  |
| can_decline_call_to_war | Can decline call to war |  |
| can_force_government | Can force government of another country to adopt the same ideology |  |
| can_generate_female_aces | Women in your country are allowed to become military pilots |  |
| can_generate_female_country_leaders | Can generate female country leaders |  |
| can_generate_female_unit_leaders | Can generate female unit leaders |  |
| can_guarantee_other_ideologies | Can guarantee other ideologies |  |
| can_join_factions | Can join factions |  |
| can_join_factions_not_allowed_diplomacy | Country's name is not allowed to join factions |  |
| can_join_opposite_factions | Can Join Factions led by another Ideology |  |
| can_lower_tension | Lowers World Tension with Guarantees |  |
| can_not_build_buildings | CAN_NOT_BUILD_BUILDINGS | Doesn't seem to work. |
| can_not_declare_war | Can not declare wars | Prevents generating wargoals, but not using existing ones. |
| can_occupy_non_war | Can hold territory owned by a country they are not at war with |  |
| can_only_justify_war_on_threat_country | Can justify war goals against a country that have not generated world tension |  |
| can_puppet | Can puppet a country |  |
| can_send_volunteers | Can send volunteer forces |  |
| can_use_kamikaze_pilots | Can use kamikaze pilots |  |
| contributes_operatives | Contributes Operatives to Spy Master: Yes | Only has an effect for subjects. |
| units_deployed_to_overlord | Control over deployed units go to overlord | Only has an effect for subjects. |

**Additional things**

`auto_complete = { yes/no }` - automatically complete a goal if the progress reaches 100%, only works if ratio_progress is present in goal. Works with range and will make goal completed once range = { max = X } ratio is completed.

`completed_amount_custom_tooltip` - overrides the default tooltip of the completed amount with any of your choice.

`total_amount_custom_tooltip` - overrides default tooltip of the total amount with any of your choice.

`range = { min = X max = Y }` - defines how the ratio calculated above is mapped to the goal's progress, if max value = 0.8 it means that goal will be completed once the ratio between the total amount and the completed amount is be 80% or more. If min value = 0.2 it's means that if the ratio is 20% the goal 0% completed.

**Both min and max are optional, by default min = 0, max = 1. Min can actually be greater than max, in which case the progress will increase as the ratio decreases and vice versa**

`scale = { }` - is a [modifier](<Modifiers - Hearts of Iron 4 Wiki.md>) that the faction leader gets once progress becomes 100% (works with range)

`reversed= { }` - is a [modifier](<Modifiers - Hearts of Iron 4 Wiki.md>) that the faction leader gets once progress becomes 0% (works with range)

<!-- kit:begin id="faction-goal-placement" at="section:Arguments_of_ratio_progress" -->
**Kit correction** Where the progress keys sit in vanilla, and the collection forms it uses. All lines: [vanilla-confirmed 1.19.3] `common/factions/goals/faction_manifests.txt` and the three goal files.

- `range`, `scale`, `reversed` and `progress_sections` are written inside `ratio_progress = { }` in the vanilla manifests (91 matching lines in `faction_manifests.txt`); every manifest has only `name`, `description`, `is_manifest` and `ratio_progress` at its top level. `auto_complete = yes` is written on the goal itself, outside `ratio_progress` (3 medium-term goals). The documentation also shows `progress_sections` in a plain `progress = { }` block, which no vanilla goal uses.
- A `progress_sections` entry may have only `min` (`manifest_fulfilled = { min = @manifest_fulfilled_value ... }` with the file constant `@manifest_fulfilled_value = 0.75`); `max` is then simply absent. Each section holds `modifier`, and the documentation names `rule` as well. `on_activate` and `on_deactivate` are disabled for faction goals. [docs] `common/factions/_documentation.md`.
- Collections take three forms: `total_amount_collection = collection:states_on_my_continent`, `= game:all_states`, or a block `completed_amount_collection = { input = collection:the_northern_mandate_states operators = { limit = { is_controlled_by_ROOT_or_ally = yes } } name = COLLECTION_FACTION_CONTROLS_NORTHERN_MANDATE }` where `name` is a loc key for the tooltip line. `input = game:scope` with `operators = { faction_members }` walks the faction. ROOT inside them is the faction leader. See [Collection modding](<Collection modding - Hearts of Iron 4 Wiki.md>) for the input and operator syntax.
- Fixed amounts also accept variables: one manifest uses `total_amount = global.global_resource_extracted_total` and `completed_amount = faction_resource_extracted_total` with `total_amount_custom_tooltip` and `completed_amount_custom_tooltip`.
- The documentation says `total_amount` and `total_amount_collection` are mutually exclusive, and so are `completed_amount` and `completed_amount_collection`; mixing a total collection with a fixed completed amount is allowed, as the wiki says. [docs] `common/factions/_documentation.md`.
<!-- kit:end id="faction-goal-placement" -->

#### AI <a id="AI"></a>

`ai_will_do = { }` decides on how likely ai will replace an empty goal slot with this goal, works exactly same as all other ai_will_do blocks in the game. For more information check [AI_modding](<AI modding - Hearts of Iron 4 Wiki.md>)

<!-- kit:begin id="faction-goal-ai" at="section:AI" -->
**Kit note** The documentation's goal `ai_will_do` uses `factor` (example `factor = 200`) and runs in the scope of the faction member that would pick the goal. Vanilla writes it in 153 of 156 goals. [docs] `common/factions/_documentation.md`; [vanilla-confirmed 1.19.3] `common/factions/goals/`. Faction initiative spending by the AI is a separate system, see the end of this page.
<!-- kit:end id="faction-goal-ai" -->

#### Code examples <a id="Code_examples"></a>

##### Short term goal code example <a id="Short_term_goal_code_example"></a>

```text
my_short_term_faction_goal_id =  {

  name = my_short_term_faction_goal_name
  description = my_short_term_faction_goal_desc
  group = MY_CUSTOM_GROUP
  category = short_term

  completed = {
    has_war_with = POL
  }

  allowed = {
    original_tag = GER
  }

  complete_effect = {
    add_political_power = 100
    add_faction_initiative = 1
  }

}
```

##### Medium term goal code example <a id="Medium_term_goal_code_example"></a>

```text
my_medium_term_faction_goal_id =  {

  name = my_medium_term_faction_goal_name
  description = my_medium_term_faction_goal_desc
  group = MY_CUSTOM_GROUP
  category = medium_term

  allowed = {
    original_tag = GER
  }

  available = {
    industrial_complex > 50
  }

  visible = {
    has_war_with = POL
  }

  locked_goal = yes

  completed = {
    has_war_with = ENG
  }

  complete_effect = {
    add_stability = 0.1
  }

}
```

##### Long term goal code example <a id="Long_term_goal_code_example"></a>

```text
my_long_term_faction_goal_id =  {

  name = my_long_term_faction_goal_name
  description = my_long_term_faction_goal_desc
  group = MY_CUSTOM_GROUP
  category = long_term

  allowed = {
    original_tag = GER
  }

  select_effect = {
    add_faction_goal = my_medium_term_faction_goal_id
  }

  remove_effect = {
    add_stability = -0.1
  }

  cancel = {
    has_war_with = SOV
  }

  cancel_effect = {
    add_political_power = 200
  }

}
```

## Manifests <a id="Manifests"></a>

Manifests - global, continuous goal that used to give faction a modifier or a rule depending on the conditions. They are defined in `common/factions/goals/*.txt` Example of those conditions can be conquered land or countries that have your ideology. In comparison to goals you can't change manifest in game also manifests is set in templates of faction and every faction supposed to have one.

### Structure <a id="Structure_2"></a>

`manifest_id` - id of your manifest, must be unique.

`name` - [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key for visible name of goal

`description` - [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key for visible description of goal

`is_manifest = yes` - decide whether it's goal or [manifest](#Manifests). By default set to no (so it's a goal). Mandatory for manifests

#### Progress <a id="Progress"></a>

Manifests only other arguments is `ratio_progress` and regular `progress`, to see about `ratio_progress` check this section [progression based goal](#Progression_based_goal).

`progress` = { } - is a block where you can add multiple progress_sections. Basically worse version of ratio progress. Don't use it

`progress_sections = { }` - is a block that contains sections, sections work like sections in [bop](<Balance of power modding - Hearts of Iron 4 Wiki.md>). This can be used so that, when being within a certain threshold of completion, modifiers get enabled.

#### Example code of manifest <a id="Example_code_of_manifest"></a>

```text
my_manifest_id =  {
  name = my_manifest_name
  description = my_manifest_desc
  is_manifest = yes

  ratio_progress = {
    total_amount_collection = {
      input = collection:african_states
    }

    completed_amount_collection = {
      input = collection:african_states
      operators = {
        limit = {
          is_controlled_by_ROOT_or_ally = yes
        }
    }
  }

  scale = {
    stability_factor = 0.1
  }

  reversed = {
    stability_factor = -0.1
  }

  range = { max = 0.67 min = 0.42 }

  progress_sections = {
    my_section = {
      min = 0.1
      max = 0.3

      modifier = {
        stability_factor = 0.1
      }
    }
}
```

<!-- kit:begin id="faction-manifest-fix" at="section:Example_code_of_manifest" -->
**Kit correction** The manifest example above is missing two closing braces, and its indentation puts `scale`, `reversed`, `range` and `progress_sections` beside `ratio_progress`. Vanilla has them inside it (see `faction-goal-placement` above). A balanced manifest in the vanilla shape, shortened from `faction_manifest_regional_expansionism`:

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

## Rules <a id="Rules"></a>

Rules - set of regulations used inside of faction. Rules can define how faction operates, as well as just give modifiers based on current rule applied. Rules have their own type and groups. Types define in which situation the rule is applicable and what scope will be used. Groups used to combine same purpose rule into one category. **Rule won't show up unless it's added to at least one rule group**. Rules can be defined in `"common/factions/rules/any_name.txt."`

### Syntax <a id="Syntax"></a>

`faction_rule_id = { }` - id of your rule, must be unique.

`type = type_token` - decides type of your rule, can be anything but game uses these predetermined tokens for in game faction rules.

**value**

**defintion**

**scopes**

joining_rule
Checks whether a country can join the faction
ROOT = joining country, FROM = faction leader
war_declaration_rule
Checks who can declare wars
ROOT = country declaring the war, FROM = target country
call_to_war_rule
Checks who can call to war
ROOT = country calling to the war, FROM = target country
member_rules
Checks whether a member can change faction goals (note documentation might be wrong)
ROOT = faction leader
change_leader_rules
Checks which country can become the faction leader
ROOT = country that becomes the faction leader
peace_conference_rules
Supposed to contain a list of peace_action_modifiers to apply during a peace conferences
ROOT = faction leader

<!-- kit:begin id="faction-rule-types" at="section:Syntax" -->
**Kit correction** The rule `type` tokens in the table above are wrong for three rows, and one type is missing.

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

All rows: [vanilla-confirmed 1.19.3] `common/factions/rules/*.txt`, counted by script. The plural strings `joining_rules`, `war_declaration_rules`, `call_to_war_rules`, `change_leader_rules`, `dismissal_rules`, `member_rules` and `peace_conference_rules` are also standalone strings in `hoi4.exe`; the singular `joining_rule`, `war_declaration_rule` and `call_to_war_rule` that the documentation and the table above give are not, and neither is `contribution_rule`, which only works through its `effect` block (see below). Because `type` accepts any token, a rule typed `joining_rule` is probably accepted and then never evaluated as a joining rule [unverified]. Copy the vanilla spelling.

More facts about rule keys, from the documentation and vanilla:

- `dismissal_rules` rules put their condition in `dismiss_member_trigger`; `member_rules` has two vanilla uses: `goals_only_faction_leader` (a `trigger` of `is_faction_leader = yes`, which limits who may set goals) and `government_in_exile_allowed` (`government_in_exile_allowed_trigger`). The wiki line "can change faction goals (documentation might be wrong)" is right for the first; the documentation's "can become government in exile" describes the second. [vanilla-confirmed 1.19.3] `common/factions/rules/faction_set_goal_rules.txt`, `goverment_in_exile_rules.txt`.
- `contribution_rule` rules (`manpower_contribution_small`, `_medium`, `_high`) use `available = { has_faction_military_unlocked = yes }` and `effect = { set_faction_member_upgrade_min = { upgrade = faction_manpower_sharing1 } }` to set the minimum member upgrade. [vanilla-confirmed 1.19.3] `common/factions/rules/manpower_contribution_rule.txt`.
- `available` and `can_remove` do not stop `set_faction_rule` or `remove` effects; they only gate the player's choice. Rule `ai_will_do` runs in the faction leader's scope and a value of 0 or less means the AI never picks the rule. Vanilla writes `ai_will_do = { base = 0 modifier = { add = 1 ... } }` (62 of 64 rules). The rule name is shown through the loc key of the rule id with Country and Faction loc scopes (`joining_rule_non_fascist` in `localisation/english/factions_l_english.yml`). [docs] `common/factions/_documentation.md`; [vanilla-confirmed 1.19.3] `common/factions/rules/`.
- The game rule table earlier on this page is the autonomy `rule` table. It has one name the game does not know, one missing name and four names vanilla never uses; see [Autonomy state modding](<Autonomy state modding - Hearts of Iron 4 Wiki.md>), block `autonomy-rule-list-fixes`, for the corrected list. That table belongs to `rule = { }` in autonomy states and progress sections, not to faction rules.
<!-- kit:end id="faction-rule-types" -->

#### Triggers <a id="Triggers_2"></a>

`visible = { }`- is a [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block that continuously checks every frame if a condition was met, required to make the rule to be visible in the rule list screen.

`available = { }` - is a [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block that continuously checks every frame if a condition was met, required to make the rule available to be chosen in the rules list. If conditions aren't met the rule wouldn't be possible to select, but difference with visible is that it will still be visible and display why it's not available to be selected when hovered over.

`can_remove = { }` - is a [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block that decides if the rule can be removed, if currently active. Default scope is faction leader. By default is true, so rule is allowed to be deleted.

`trigger = { }` - is a [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block that used to define the rule. For example is_major = yes inside the block will make it so only major countries would allow to use this rule.

`government_in_exile_allowed_trigger = { }` - special [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block that used to define whether government in exile allowed in faction or not.

`dismiss_member_trigger = { }` - special [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block that used to define who can be kicked out of faction. Works exactly same as trigger but used to define who can be exiled from faction.

#### Modifier <a id="Modifier"></a>

`modifier = { }` - [modifier](<Modifiers - Hearts of Iron 4 Wiki.md>) a block that all members gets while a rule is active.

`peace_action_modifiers = { }` - special block that gets available if peace_conference_rules type is active. Used to apply modifier during peace conferences. Peace action modifiers can be found in `"common/peace_conference/cost_modifiers"` **Enable trigger will not run for the modifier - the modifier is enabled as long as the rule is active.**

<!-- kit:begin id="faction-peace-rules" at="section:Modifier" -->
**Kit note** Peace rules in vanilla: 7 rules of type `peace_conference_rules` in `common/factions/rules/peace_rules.txt` (`faction_peace_rule_puppeting_focus`, `_no_puppeting`, `_liberation_focus`, `_ideology_focus`, `_conquest_focus`, `faction_peace_take_claimed_focus`, `faction_peace_china_focus`). Each lists names from `common/peace_conference/cost_modifiers/` in `peace_action_modifiers = { }` and adds a `modifier = { custom_modifier_tooltip = ... }` line for the tooltip. `rule_group_peace_rules` holds them all. [vanilla-confirmed 1.19.3] `common/factions/rules/peace_rules.txt`, `common/factions/rules/groups/rule_groups.txt`. The cost modifier syntax and how modifiers multiply are on [Peace conference modding](<Peace conference modding - Hearts of Iron 4 Wiki.md>).
<!-- kit:end id="faction-peace-rules" -->

#### Effect <a id="Effect"></a>

`effect = { }` - is an [effect](<Effects - Hearts of Iron 4 Wiki.md>) block that executes effects for the rule.

#### AI block <a id="AI_block"></a>

`ai_will_do = { }` decides on how likely ai will chose this rule, works exactly same as all other ai_will_do blocks in the game. For more information check [AI_modding](<AI modding - Hearts of Iron 4 Wiki.md>)

#### Localisation <a id="Localisation"></a>

To learn more check [localisation](<Localisation - Hearts of Iron 4 Wiki.md>)

```text
my_faction_rule_id: "My faction rule name!"
```

#### Rule groups <a id="Rule_groups"></a>

Rule groups - used to combine same purpose rule into one category. They are defined "common/factions/rules/groups". It's recommended to have all rules inside one group of same type. However it's not mandatory. Also it's not required for one group to contain all rules of same type.

##### Syntax <a id="Syntax_2"></a>

`group_id = { }` - id of your group, must be unique.

`default_rule = rule_id` - used to define rule that's would be used by default in group

`rules = { }` - list of rules in this group, you can define rules right there which is not recommend.

<!-- kit:begin id="faction-rule-groups" at="section:Syntax_2" -->
**Kit note** In vanilla `rule_groups.txt` every `default_rule` line is commented out (`#default_rule = ...`), so no vanilla group sets one; the starting rules come from each template's `default_rules`, which the documentation says override the groups' defaults. Group ids in vanilla: `rule_group_ideology`, `rule_group_geographical`, `rule_group_war_relation`, `rule_group_dismissal_ideology`, `rule_group_dismissal_actions`, `rule_group_war_declaration_declarer`, `rule_group_call_to_war`, `rule_group_peace_rules`, `rule_group_leader_faction` and others (19 in all). A rule that is in no group never shows up. [vanilla-confirmed 1.19.3] `common/factions/rules/groups/rule_groups.txt`; [docs] `common/factions/_documentation.md`.
<!-- kit:end id="faction-rule-groups" -->

#### Code examples <a id="Code_examples_2"></a>

**Rules:**

```text

my_rule_id = {
	type = joining_rule

	trigger = {
		original_tag = ITA
	}

	modifier = {
		weekly_manpower = 1000
	}
	ai_will_do = {
		base = 10
	}
}

my_rule_2_id = {
	type = my_custom_type

	visible = {
		original_tag = SOV
	}

	available = {
		has_political_power > 200
	}
	can_remove = {
		always = no
	}

	trigger = {
		is_faction_leader = yes
	}

	effect = {
		declare_war_on = {
			target = ENG
			type = annex_everything
		}
	}
}
```

**Rule Groups:**

```text

rule_group_my_custom_rules_1 = {
	default_rule = my_rule_id
	rules = {
		my_rule_id
	}
}
rule_group_my_custom_rules_2 = {
	rules = {
		my_rule_2_id
	}
}
```

## Member upgrades <a id="Member_upgrades"></a>

Members upgrades - is mechanic used in factions, that can be changed by faction leader. Only thing it's impacts how much manpower each faction members contributes towards shared manpower pool that can be used to garrison needed manpower. **It's recommended to have 4 members upgrade in one group, since it's default value that interface made for.**

### Syntax <a id="Syntax_3"></a>

`member upgrade_id = { }` - id of member upgrade, should be unique, block used to create new instance

`name` - [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key for visible name of faction member upgrade. Not required, by default used group name

`description` - [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key for a visible description of faction member upgrade. Not required, by default used group description

`icon` - the icon that will be displayed while active. Will override the group's icon

`upgrade_cost` - The amount of faction initiative that it cost to replace this upgrade with another

`bonus` - A numerical value to dictate the amount manpower country contributes

#### Group <a id="Group"></a>

`member upgrade_id = { }` - id of member upgrades group, should be unique, block used to create new instance

`name` - [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key for visible name of faction member upgrade.

`description` - [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key for visible description of faction member upgrade

`icon` - The icon that will be displayed while active.

`upgrades = { }` - The faction upgrades within this group, this list will be sorted on their bonus

`upgrade_type = faction_member_upgrade_manpower` - Currently only supported type, others won't show up, can be used to overwrite default one.

`default_upgrade = upgrade_id` - used to set default member upgrade. **Note: upgrade that chosen as default should be included in upgrades block**

<!-- kit:begin id="faction-member-upgrades" at="section:Group" -->
**Kit correction** The key for the text of an upgrade or a group is `desc`, not `description`: the documentation lists `name`, `desc`, `icon`, `upgrade_cost`, `bonus` for an upgrade and `name`, `desc`, `icon`, `upgrades` for a group, and the vanilla files use `desc` (`FACTION_MANPOWER_CONTRIBUTION_VALUE_DESC`). [docs] `common/factions/_documentation.md`; [vanilla-confirmed 1.19.3] `common/factions/member_upgrades/`.

Vanilla defines 4 upgrades in `common/factions/member_upgrades/member_upgrades.txt` (`manpower_contribution_full_enable` with `bonus = 0.0`, `faction_manpower_sharing1` to `3` with 0.05, 0.1 and 0.15) and the group `faction_member_upgrade_manpower_group` with `default_upgrade = manpower_contribution_full_enable`, `upgrade_type = faction_member_upgrade_manpower` and `icon = GFX_manpower_contribution`. The documentation says `faction_member_upgrade_manpower` is the only upgrade type with code support and that its `bonus` is the percentage of a country's manpower moved into the faction pool. No vanilla upgrade sets `upgrade_cost`. [vanilla-confirmed 1.19.3] `common/factions/member_upgrades/member_groups/member_upgrade_groups.txt`.

Related script: `set_faction_member_upgrade_min = { upgrade = <id> }` (the documentation example misspells it `set_faction_upgrade_min`), `set_faction_upgrade = <token>` and the trigger `faction_upgrade_level > <token>`. Vanilla uses only `set_faction_member_upgrade_min` (3 times, in contribution rules); `set_faction_upgrade` and `faction_upgrade_level` are documented and not used. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`; [vanilla-confirmed 1.19.3] `common/factions/rules/manpower_contribution_rule.txt`.
<!-- kit:end id="faction-member-upgrades" -->

## Templates <a id="Templates"></a>

Faction templates - the way to combine all mentioned above things, plus add customization (name, icon). Templates can be used for two purposes, first: make predetermined faction template (e.g. Axis, Allies, Comintern), second: create a blank template for faction (e.g. fascist countries faction, south-American countries faction).

### Syntax <a id="Syntax_4"></a>

`name` - [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key for a visible name of faction.

`icon` - `[GFX definition or direct path to image]` - logo of the faction visible in the game. **Note: factions logo icons are strip of two logos in one file with size of 200x100, with each taking 100 pixels, so interface definition of logo must contain noOfFrames = 2, as any other image of game with stripped frames. As well as logo must have miniature definition with same name and addition _miniature at the end.**

`color = { }` - color of faction used in faction map mode, by default uses faction leader color, must be specified in RGB as in other parts of the game.

`can_leader_join_other_factions = { yes/no }` - setting that allows this faction leader to join another faction, if set to yes leader can't leave faction unless he dismantles it, if set to no leader can leave, previous faction get destroyed and all members get invited to the new faction

#### Triggers <a id="Triggers_3"></a>

`visible = { }`- is a [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block that continuously checks every frame if a condition was met, required to make the template to be visible in the faction creation screen. **If left empty template won't show up in faction creation screen**

`available = { }` - is a [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block that continuously checks every frame if a condition was met, required to make the template to be chosen in the faction creation screen. If conditions aren't met the template wouldn't be possible to select, but difference with visible is that it will still be visible and display why it's not available to be selected when hovered over.

#### Manifest,rules,goals <a id="Manifest.2Crules.2Cgoals"></a><a id="Manifest,rules,goals"></a>

`manifest = manifest_id` - faction manifest set for this faction. For more info see [manifests](#Manifests)

`goals = { }` - a block where you can set the default goals, there's could be only 3 goals of different types, goals can be defined inside the block or can be specified existing goal id. For more info see [goals](#Goals)

`default_rules = { }` - a block where you can set the default rules of faction, this block overrides default rules in the group. For more info see [rules](#Rules)

<!-- kit:begin id="faction-template-notes" at="section:Manifest.2Crules.2Cgoals" -->
**Kit note** Template facts for 1.19.3. [docs] `common/factions/_documentation.md` unless marked.

- `visible` empty means the template is never offered in the creation screen, which is how script-only templates are made; `available` empty means always available. Vanilla fallbacks use `visible = { always = no }`. Of 69 vanilla templates, 19 set `visible`, 9 set `available`, 19 set `can_leader_join_other_factions`; every one sets `manifest`, `goals`, `default_rules` and `icon`. [vanilla-confirmed 1.19.3] `common/factions/templates/`.
- `color` is documented by the wiki but no vanilla template sets it: the only lines are commented out with the note "this should default to faction leader's color". [vanilla-confirmed 1.19.3] `common/factions/templates/generic_factions.txt`.
- `name` is a loc key, but vanilla also has literal values such as `name = Axis`. [vanilla-confirmed 1.19.3] `common/factions/templates/axis.txt`.
- `goals` takes ids or inline definitions, at most one per category by default (see `faction-goal-slots`).
- Logo sprites: `GFX_faction_logo_axis` has `noOfFrames = 2` and a 200 by 100 texture; the `GFX_faction_logo_axis_miniature` sprite is a separate 32 by 32 texture. 29 `_miniature` sprites are defined in the same file. [vanilla-confirmed 1.19.3] `interface/factions/factions.gfx` and the DDS headers.
<!-- kit:end id="faction-template-notes" -->

#### Code example: <a id="Code_example:"></a>

```text
faction_template_my_faction = {

  name = my_faction_name

  icon = GFX_faction_logo_my_logo

  color = {

    51 222 51

  }

  manifest = my_faction_manifest

  goals = {

    my_short_term_faction_goal

    my_medium_term_faction_goal

    my_long_term_faction_goal

  }

  default_rules = {

    call_to_war_rule_independent_only

    joining_rule_non_communist

    faction_peace_rule_conquest_focus

    change_leader_rule_manpower

    change_leader_rule_manifest_below_35

    dismissal_rule_offensive_war

  }

}
```

## Triggers and Effects <a id="Triggers_and_Effects"></a>

### List of faction-related effects <a id="List_of_faction-related_effects"></a>

- create_faction - creates a faction without a template (OBSOLETE)
- create_faction_from_template - the new fancy way of creating factions
- dismantle_faction - dismantles faction
- set_faction_leader - changes faction's leader
- set_faction_spymaster - changes faction's spymaster
- set_faction_name - changes faction's name
- add_to_faction - adds a country to a faction
- remove_from_faction - removes a country from a faction
- leave_faction - removes the current country from faction
- set_faction_rule - sets a rule on a faction
- set_faction_manifest - changes faction's manifest (main goal)
- add_faction_goal - adds a goal to a faction
- remove_faction_goal - removes a goal from a faction
- add_faction_initiative - adds FI to faction
- add_faction_power_projection - adds power to the faction
- add_faction_influence_score - adds influence to the country in the faction
- add_faction_influence_ratio - adds influence to the country based on the given ratio of the faction's total influence

<!-- kit:begin id="faction-effects-more" at="section:List_of_faction-related_effects" -->
**Kit addition** Faction effects in the 1.19.3 effect documentation that the list above lacks. All rows: [docs] `documentation/effects_documentation.md`.

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

### List of faction-related triggers <a id="List_of_faction-related_triggers"></a>

- faction_manifest_fulfillment - compares the current country faction's manifest fulfillmens to a value
- has_faction_template - checks if the current country is in a faction created from a template
- faction_power_projection - compares the current country faction's power to a value
- faction_influence_score - checks influence value of current country in the faction
- faction_influence_ratio - checks influence ratio of current country in the faction
- faction_influence_rank - checks influence rank in the faction of the current country
- has_faction_goal - checks if the current country's faction has an active or completed goal
- has_completed_faction_goal - checks if the current country's faction has completed a goal
- faction_goal_fulfillment - checks goal fulfillment for the current country's faction
- has_manpower_to_become_leader - checks if the current country exceeds the current faction leader and its subjects in deployed manpower
- has_industry_to_become_leader - checks if the current country exceeds the faction leader in number of factories

<!-- kit:begin id="faction-triggers-more" at="section:List_of_faction-related_triggers" -->
**Kit addition** Faction triggers in the 1.19.3 trigger documentation that the list above lacks. All rows: [docs] `documentation/triggers_documentation.md`, country scope.

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

### List of faction-related modifiers <a id="List_of_faction-related_modifiers"></a>

- faction_influence_war_score_factor - war score modifier for faction influence
- faction_influence_industrial_capacity_factor - industrial capacity modifier for faction influence
- faction_influence_garrison_support_provider_factor - garrison support provider modifier for faction influence
- faction_influence_garrison_support_reciver_factor - garrison support reciver modifier for faction influence
- faction_influence_expeditionary_force_provider_factor - expeditionary force provider modifier for faction influence
- faction_influence_expeditionary_force_reciver_factor - expeditionary force reciver modifier for faction influence

<!-- kit:begin id="faction-modifiers-fix" at="section:List_of_faction-related_modifiers" -->
**Kit correction** Only `faction_influence_war_score_factor` of the six modifiers above is in the 1.19.3 modifier documentation. The other five (`faction_influence_industrial_capacity_factor`, `faction_influence_garrison_support_provider_factor`, `faction_influence_garrison_support_reciver_factor`, `faction_influence_expeditionary_force_provider_factor`, `faction_influence_expeditionary_force_reciver_factor`) appear only in the faction documentation text, not in the modifier documentation or any vanilla script. The matching weights are now defines in `NDefines.NFactions` (`FACTION_INFLUENCE_INDUSTRIAL_CAPACITY_FACTOR` 5, `FACTION_INFLUENCE_GARRISON_SUPPORT_PROVIDER_FACTOR` 0.001, `FACTION_INFLUENCE_EXPEDITIONARY_FORCE_PROVIDER_FACTOR` 0.01 and so on). Do not use the five names as modifiers. [docs] `documentation/modifiers_documentation.md` (names absent); [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` (the defines).

Faction modifiers that do exist in the modifier documentation: `faction_influence_contribution_factor`, `faction_influence_war_score_factor`, `faction_subject_contribution_gain`, `faction_trade_opinion_factor` and `join_faction_tension`. [docs] `documentation/modifiers_documentation.md`.
<!-- kit:end id="faction-modifiers-fix" -->

<!-- kit:begin id="faction-ai-and-defines" at="bottom" -->
## Kit: AI spending of faction initiative, defines and console <a id="kit-faction-ai-and-defines"></a>

**AI strategy types.** The AI spends faction initiative (FI) according to `ai_strategy` blocks of type `spent_faction_initiative_priority` with an `id` and a `value`. Valid ids: `program`, `unlock_doctrine_sharing`, `unlock_faction_commander`. Intelligence advisor roles use their own types: `become_spymaster`, `become_head_of_crypto`, `become_head_of_counter_intel`, `become_head_of_operations`. Rule choices are weighted by the rule's own `ai_will_do`. [docs] `common/factions/_documentation.md`; [vanilla-confirmed 1.19.3] `common/ai_strategy/default.txt`, `ENG.txt`, `GER.txt`, `USA.txt`. See [AI modding](<AI modding - Hearts of Iron 4 Wiki.md>) for the strategy block format.

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

Peace rules and their cost modifiers are covered on [Peace conference modding](<Peace conference modding - Hearts of Iron 4 Wiki.md>); goal collections on [Collection modding](<Collection modding - Hearts of Iron 4 Wiki.md>).
<!-- kit:end id="faction-ai-and-defines" -->

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
