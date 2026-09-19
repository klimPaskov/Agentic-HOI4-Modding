# Faction modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Faction modding", captured 2026-09-19.*

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

## Goals <a id="Goals"></a>

### Overview <a id="Overview"></a>

Faction’s goals are the way to have “quest” for multiple countries without using missions or events. There are three types of goals in the game, Short-term, Medium-term and Long-term. They are defined in

`common/factions/goals/*.txt` and every faction can have up to one of three types present in the game. **It's not mandatory for faction to start with goals.** Default scope is faction leader, FROM is faction member who views current goal. **FROM is not supported inside `complete_effect, remove_effect, cancel_effect`**.

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

#### AI <a id="AI"></a>

`ai_will_do = { }` decides on how likely ai will replace an empty goal slot with this goal, works exactly same as all other ai_will_do blocks in the game. For more information check [AI_modding](<AI modding - Hearts of Iron 4 Wiki.md>)

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

### List of faction-related modifiers <a id="List_of_faction-related_modifiers"></a>

- faction_influence_war_score_factor - war score modifier for faction influence
- faction_influence_industrial_capacity_factor - industrial capacity modifier for faction influence
- faction_influence_garrison_support_provider_factor - garrison support provider modifier for faction influence
- faction_influence_garrison_support_reciver_factor - garrison support reciver modifier for faction influence
- faction_influence_expeditionary_force_provider_factor - expeditionary force provider modifier for faction influence
- faction_influence_expeditionary_force_reciver_factor - expeditionary force reciver modifier for faction influence

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
