# Modifiers

*Offline snapshot of the Hearts of Iron IV Wiki page "Modifiers", revision 102188, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.4.1" checked="2026-11-01" revision="102188" sources="documentation/modifiers_documentation.md documentation/effects_documentation.md documentation/triggers_documentation.md documentation/dynamic_variables_documentation.md documentation/console_commands_documentation.md common/dynamic_modifiers/ common/modifier_definitions/ common/modifiers/ common/difficulty_settings/ common/opinion_modifiers/ common/units/unit_modifiers/ common/peace_conference/cost_modifiers/ common/ideas/ common/operations/ localisation/english/modifiers_l_english.yml" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against the modifier documentation (722 modifiers, 38 template families), the dynamic modifier, modifier definition, static modifier, difficulty, opinion modifier and sub-unit modifier files, and the effect, trigger, variable and console documentation.
- Kit blocks added: values and variables, tooltip helpers, dynamic modifier scopes, arguments and add/remove, static, relation, province, balance of power, definition and opinion modifier notes, one table per section for the 167 documented modifiers the page never named, `template-families`, and corrections for sub-unit modifiers, `license_purchase_cost_factor` and the annex and puppet cost note.
- Wiki errors found: sub-unit modifiers exist only when registered, `license_purchase_cost_factor` does not exist, dynamic modifiers also work on special projects, the `scope` claim has no support, annex and puppet cost factors are not removed, several lists are short.
- Gaps left: meanings starting with `~` are guesses; the effect of `scope`, of `days` at or below 0 and of the annex and puppet factors is untested; the Modifier type, scope and version columns were not re-checked, only the names.
**1.19.4.1 re-check (2026-11-01).** About 40 statements depended on files the update changed, and all were re-measured on the 1.19.4.1 files. Numbers that moved: modifier assignments in ideas 13,384 to 13,444 and in dynamic modifiers 5,097 to 5,092, `custom_modifier_tooltip` 367 to 371 uses, `add_dynamic_modifier` calls 1,549 to 1,552, opinion modifiers 810 to 811, and `navy_screen_attack_factor_against` is now used in `common/ideas/japan.txt`; the meaning column cannot be diffed against the old text file. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

## Table of contents

- [Applying a modifier](#Applying_a_modifier)
  - [Tooltip modification](#Tooltip_modification)
- [Dynamic modifiers](#Dynamic_modifiers)
  - [Arguments](#Arguments)
  - [Example](#Example)
  - [Adding a dynamic modifier](#Adding_a_dynamic_modifier)
- [Static modifiers](#Static_modifiers)
  - [Global modifiers](#Global_modifiers)
  - [Difficulty modifiers](#Difficulty_modifiers)
  - [Relation modifiers](#Relation_modifiers)
  - [Province modifiers](#Province_modifiers)
  - [Balance of power modifiers](#Balance_of_power_modifiers)
- [Modifier definitions](#Modifier_definitions)
  - [Examples](#Examples)
  - [Using in variables](#Using_in_variables)
- [Opinion modifiers](#Opinion_modifiers)
  - [Examples](#Examples_2)
  - [Implementation](#Implementation)
- [List of modifiers](#List_of_modifiers)
  - [Kit: How the added tables read](#kit-added-tables-legend)
  - [Kit: Template modifier families](#kit-template-families)
  - [Country scope](#Country_scope)
    - [General](#General)
    - [Politics](#Politics)
    - [Diplomacy](#Diplomacy)
    - [Autonomy](#Autonomy)
    - [Governments in exile](#Governments_in_exile)
    - [Equipment](#Equipment)
    - [Fuel and supply](#Fuel_and_supply)
    - [Buildings](#Buildings)
    - [Resistance and compliance](#Resistance_and_compliance)
    - [Intelligence](#Intelligence)
    - [Operatives](#Operatives)
    - [AI](#AI)
    - [Military outside of combat](#Military_outside_of_combat)
    - [MIOs](#MIOs)
    - [Unit leaders](#Unit_leaders)
    - [General combat](#General_combat)
    - [Land combat](#Land_combat)
    - [Naval invasions](#Naval_invasions)
    - [Naval combat](#Naval_combat)
    - [Carriers and their planes](#Carriers_and_their_planes)
    - [Air combat](#Air_combat)
    - [Targeted modifiers](#Targeted_modifiers)
  - [State scope](#State_scope)
  - [Unit leader scope](#Unit_leader_scope)
  - [Scientists scope](#Scientists_scope)
  - [Strategic region scope](#Strategic_region_scope)
- [Notes and references](#Notes_and_references)

---

A modifier is essentially a variable used in internal calculations. However, unlike [Defines](<defines.md>), modifiers are dynamically changeable within any modifier block. In general, modifiers are typically used to create a consistent and long-lasting effect that can be easily reversed.
Each modifier has the exact same layout: `modifier_name = 0.1`. This adds the specified value to the modifier's total value for the scope where it is applied.`[a]` For example, assuming that there are no other modifiers changing that to the country, having `political_power_gain = 0.2` and `political_power_gain = -0.05` applied to the country (potentially in different modifier blocks) will result in a total of **+0.15** political power gain above the base gain. Due to how modifiers work, **a modifier with the value of 0 will always do nothing.** This also means that negative modifiers will always work and have the opposite effect of positive modifiers.
A modifier's current total value can be received as a variable by reading `modifier@modifier_name`, such as `set_variable = { my_var = modifier@political_power_gain }`. This works for countries and states, but for unit leaders, `unit_modifier@modifier_name` and `leader_modifier@modifier_name` is used instead.

The following are *not* modifiers, even if they are similar:

- Research bonuses allowing to grant a boost to a specific technology category. This is, instead, [an argument within ideas](<idea_modding.md#Modifiers>), which can be applied in the same way for advisors, but not elsewhere.
- Equipment bonuses, such as decreasing the cost to build an equipment archetype. Similarly, this is [an argument within ideas](<idea_modding.md#Modifiers>), which can be applied in the same way for advisors and country leader traits, but not elsewhere.
- Opinion modifiers, which can be applied to change the opinion (including trade influence) within countries, defined in `/Hearts of Iron IV/common/opinion_modifiers/*.txt` files.

## Applying a modifier <a id="Applying_a_modifier"></a>

There are a large variety of ways to apply modifiers, but these are the primary ones:

- [Ideas](<idea_modding.md>) - This primarily includes but is not limited to national spirits and hidden ideas. **These are the simplest way to add a modifier to a country** by using an [effect block](<effects.md>), such as a national focus reward, by using [add_ideas](<effects.md>) or [add_timed_idea](<effects.md>). These only work for countries.
- [Dynamic modifiers](#Dynamic_modifiers) - This is similar to ideas (Showing up in the same screen for countries), but they accept [variables](<data_structures.md>) and can also be applied on states and unit leaders. **These are the primary way to add modifiers to a state.**
- Traits:
  - [Country leader traits](<character_modding.md#Country_leader_traits>) - These can be added to ideas (including advisors which function similarly) and country leaders, which'll apply on the country.
  - [Unit leader traits](<character_modding.md#Unit_leader_traits>) - These can be added to unit leaders and apply effects on the leaders themselves or their units. These are the primary way to add a modifier to a unit leader.
- [Static modifiers](#Static_modifiers):
  - [Global modifiers](#Global_modifiers) - These are entirely hard-coded on *when* they apply, such as those used for stability and war support bonuses. However, these can be changed in *what* they apply.
  - [Provincial modifiers](#Province_modifiers) - These are the primary if not the only way to apply a modifier towards a specific province.
  - [Relation modifiers](#Relation_modifiers) - These are the only way to apply a targeted modifier from one country towards the other without needing to specify a specific country tag within the targeted modifier block.

Each modifier follows the same structure of being assigned a number, such as the following formatting within many blocks **that support modifiers**, such as anything listed above:

```text
modifier = { # While this is present in, for example, ideas or decisions, it's equally likely to see is modifier = { ... } being omitted entirely in other entries, such as country leader traits.
    political_power_gain = 0.1
    disabled_ideas = 1
}
```

No modifiers can have a non-numeric value, including boolean ones that must be 1 to have any effect.
Note that **modifiers do not support if statements**. The closest replica possible of one are [dynamic modifiers](#Dynamic_modifiers), which allow using variables.

<!-- kit:begin id="modifier-values" at="section:Applying_a_modifier" -->
**Kit addition** Precision, variables and reading a modifier total.

- Every modifier value accepts up to 3 decimal places. The decimal places shown in the game's modifier documentation (and in the "dp" columns of the kit tables below) are display only. [docs] `documentation/modifiers_documentation.md`
- A modifier written in an idea, trait or decision never takes a variable. `common/ideas/` holds 13,444 modifier assignments (12,547 in `modifier` blocks and 897 in `targeted_modifier` blocks) and none of them is a variable name or a constant. [vanilla-confirmed 1.19.4.1]
- Outside dynamic modifiers the only non-numeric modifier values in vanilla are `@constant` references: 72 in `common/country_leader/00_traits.txt`, 65 in `common/decisions/` and 5 in `common/military_industrial_organization/`. [vanilla-confirmed 1.19.4.1]
- In `common/dynamic_modifiers/` 4,249 of 5,092 modifier assignments (83 percent) are variable names, so variable values are a dynamic modifier feature. [vanilla-confirmed 1.19.4.1]
- `modifier@token` reads a total in country, state and military industrial organization scope (for example `modifier@military_industrial_organization_research_bonus`), and a state can be addressed by id as `123.modifier@local_manpower`. In unit leader scope use `leader_modifier@token`, `unit_modifier@token` or `sum_unit_terrain_modifier@token`. [docs] `documentation/dynamic_variables_documentation.md`
- `leader_modifier@wounded_chance_factor` is read in `common/on_actions/00_on_actions.txt`. [vanilla-confirmed 1.19.4.1]
- Console: `list_modifiers <scope>` lists the modifiers of the selected country, state or unit leader, and `loc_check_modifiers` checks modifiers for missing localisation. [docs] `documentation/console_commands_documentation.md`
<!-- kit:end id="modifier-values" -->

### Tooltip modification <a id="Tooltip_modification"></a>

Modifier blocks support, within them, the `hidden_modifier = { ... }` block, which can be used to provent the modifiers within from showing up in the tooltip. Additionally, `custom_modifier_tooltip = localisation_key_tt` can be used to add a custom localisation string to appear within the localisation as one of the modifiers. In combination, this will look like the following:

```text
modifier = {
    hidden_modifier = {
        political_power_gain = 0.1
    }
    custom_modifier_tooltip = political_power_gain_tt
}
```

Custom modifiers now support dynamic commands (anything within square brackets). They were previously only usable for non-dynamic localisation

<!-- kit:begin id="tooltip-vanilla" at="section:Tooltip_modification" -->
**Kit addition** Vanilla use of the tooltip helpers.

- `custom_modifier_tooltip` appears 371 times in 54 files (ideas, country leader traits, decisions, dynamic modifiers, continuous focuses, faction rules, occupation laws, unit leader and scientist traits, balance of power). `hidden_modifier` appears 20 times in 5 files (ideas, country leader traits, continuous focuses, ideologies). [vanilla-confirmed 1.19.4.1] `common/`
- Dynamic commands in the tooltip text are confirmed: `GER_motor_and_mech_attack_tt: "[GetMotorMechAttack]"` in `localisation/english/wuw_ideas_l_english.yml` is the `custom_modifier_tooltip` of `GER_blitzkrieg_modifier`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="tooltip-vanilla" -->

## Dynamic modifiers <a id="Dynamic_modifiers"></a>

*If you want to apply a consistent modifier to a country, [it's easier to use ideas instead.](<idea_modding.md>)*

Dynamic modifiers, defined in `/Hearts of Iron IV/common/dynamic_modifiers/*.txt` files, are a type to apply modifiers that accept variables. The modifiers are updated daily, unless the [force_update_dynamic_modifier effect](<effects.md>) is used to forcefully refresh the impact of modifiers. They can be applied to both countries and states, in case of the latter, the variable must be defined for the state, not for the country-owner or controller. They can also be applied to unit leaders.

Unlike ideas, **there is no way to reload definitions of dynamic modifiers** via debug mode or console, any changes to their definitions require a game restart to apply in-game. Additionally, due to the daily refresh of the variable check, these are more poorly optimised than ideas are. Due to this, when it's feasible to not use variables for a country-scoped dynamic modifier, it's both easier and more optimised [to use national spirits instead.](<idea_modding.md>)

The dynamic modifiers are evaluated daily for each scope. The process consists of the following:

- At the beginning of each day, each variable modifier value for each dynamic modifier is temporarily reset to 0, even if the null-coalescing operator is used to assume a different number as the default. Constant values do not get reset.
- Dynamic modifiers are then evaluated in the order that they were given to the scope with `add_dynamic_modifier`.
- The variable values inside of a dynamic modifier are assumed to be 0 until every variable inside is calculated. This includes those that rely on other modifiers, which includes the `modifier@modifier_name` [game variable](<data_structures.md>) or [MTTH variables](<data_structures.md#MTTH_variables>) that utilise that game variable.
- After the variables are calculated for a single dynamic modifier, the modifiers apply to the scope with the dynamic modifier and the game moves onto the next dynamic modifier added to the current scope until each one is calculated.

<!-- kit:begin id="dynamic-scopes" at="section:Dynamic_modifiers" -->
**Kit correction** Dynamic modifiers can also be added to special projects, and the refresh effect is documented.

- `add_dynamic_modifier`, `remove_dynamic_modifier` and `force_update_dynamic_modifier` work in state, country, character (unit leader) and special project scope. The text above names only the first three. [docs] `documentation/effects_documentation.md`
- The header of `common/dynamic_modifiers/0_dynamic_modifiers.txt` says the same ("countries, states, unit leaders or special projects") and says dynamic modifiers are updated daily unless `force_update_dynamic_modifier` forces it. [vanilla-confirmed 1.19.4.1]
- `force_update_dynamic_modifier = yes` refreshes the scope's dynamic modifiers at once. Vanilla calls it three times: twice in `common/national_focus/congo_shared.txt` and once in `common/scripted_effects/PHI_scripted_effects.txt`. [docs] [vanilla-confirmed 1.19.4.1]
- Adding a dynamic modifier that is already present refreshes it ("updates the cooldown if exists"), which matters for timed modifiers. [docs] `documentation/effects_documentation.md`
- `has_dynamic_modifier` tests for one in state, country and character scope. It takes either `has_dynamic_modifier = name` or a block with `modifier` and an optional `scope`. [docs] `documentation/triggers_documentation.md`
- Vanilla defines 679 dynamic modifiers in 11 files under `common/dynamic_modifiers/`. [vanilla-confirmed 1.19.4.1]
- The console documentation lists no command that reloads dynamic modifier definitions, which fits the restart claim above but does not prove it. [unverified]
<!-- kit:end id="dynamic-scopes" -->

### Arguments <a id="Arguments"></a>

- **icon** decides what is the icon used for the dynamic modifier. The icon uses a sprite defined in any `/Hearts of Iron IV/interface/*.gfx` file. If the icon is not specified, it will be hidden.
- **enable** decides when exactly the dynamic modifier's modifiers apply. If the dynamic modifier is set, but the country or state it's set to does not fulfill the requirements, its effects will not apply. Optional.
- **remove_trigger** will automatically remove the dynamic modifier upon the triggers being met. Optional.
- **attacker_modifier** will, if set to true within a state-scoped dynamic modifier, additionally makes the modifier apply to divisions that, while not being present in the state with the dynamic modifier, are attacking an enemy located on that state. Optional, defaults to false.

Modifiers are put directly inside the dynamic modifier as a list. Non-modifier idea attributes such as `equipment_bonus` or `research_bonus` are impossible to use inside of dynamic modifiers.

<!-- kit:begin id="dynamic-arguments" at="section:Arguments" -->
**Kit addition** What vanilla puts inside a dynamic modifier.

- The header of `common/dynamic_modifiers/0_dynamic_modifiers.txt` lists four optional keys and nothing else: `icon` (shown in GUIs only when given), `enable`, `remove_trigger` and `attacker_modifier`. Everything else in the block is a modifier. [vanilla-confirmed 1.19.4.1]
- `attacker_modifier = yes` is used once in vanilla, by `unplanned_offensive` in `0_dynamic_modifiers.txt` (with `army_attack_factor = -0.9` and `army_speed_factor = -0.75`). [vanilla-confirmed 1.19.4.1]
- A value can be a plain number or a variable name: `max_fuel = var_max_fuel` (header example), a scope-prefixed variable such as `global.HABSBURG_army_war_stability_factor` (`common/dynamic_modifiers/HABSBURG_dynamic_modifiers.txt`), or `temporary_state_resource_oil = sabotaged_oil` (`0_dynamic_modifiers.txt`). 843 of the 5,092 assignments are plain numbers. [vanilla-confirmed 1.19.4.1]
- `custom_modifier_tooltip` is used inside dynamic modifiers in 8 files. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="dynamic-arguments" -->

### Example <a id="Example"></a>

```text
dynamic_modifier_name = {
    icon = GFX_idea_unknown
    enable = { always = yes }
    remove_trigger = {
        NOT = {
            has_variable = var_name
        }
    }
    political_power_gain = var_name # Variable value
    weekly_manpower = 1000 # Constant value
    stability_factor = GER.stability_var # Checks specifically GER's variable, regardless of where the modifier is applied
}
```

### Adding a dynamic modifier <a id="Adding_a_dynamic_modifier"></a>

Dynamic modifiers are added via the [add_dynamic_modifier effect](<effects.md>). A typical addition of a dynamic modifier looks like the following:

```text
add_dynamic_modifier = { modifier = dynamic_modifier_name }
```

Since dynamic modifiers do not have assigned scopes, the same modifier can be assigned to either a country, a state, a unit leader, or several at once – this is decided only by where the `add_dynamic_modifier` effect is executed.

Within GUI, a dynamic modifier will take up these places if visible:

- For a country, a dynamic modifier will show up in the list of national spirits, appearing after the regular spirits.
- For a state, a dynamic modifier will show up in the special section for them in the bottom of the selected state view, marked with `dynamic_modifiers_grid` in `/Hearts of Iron IV/interface/countrystateview.gui`.

When adding a dynamic modifier, it is also possible to make it be timed or make it use a different scope as the variable's base. For example, the following code will apply dynamic_modifier_name to GER for 30 days, but the variables will be read off POL:

```text
GER = {
    add_dynamic_modifier = {
        modifier = dynamic_modifier_name
        scope = POL  # The modifier itself will be applied to GER, but the variables will be read off POL.
        days = 30
    }
}
```

In particular, assuming that dynamic_modifier_name is the example dynamic modifier created previously, if you do `set_variable = { POL.var_name = 0.3 }`, then the dynamic modifier assigned to GER as the result of this effect will give 0.3 daily political power gain. However, if the dynamic modifier scopes into ROOT for the variable as `political_power_gain = ROOT.var_name`, then `set_variable = { GER.var_name = 0.3 }` would be done.

A dynamic modifier is removed via [remove_dynamic_modifier](<effects.md>), phrased similarly to add_dynamic_modifier: `remove_dynamic_modifier = { modifier = dynamic_modifier_name }`. If, when added, the dynamic modifier had a scope assigned to it, the scope will have to be specified when removing it as well.

**Modifiers that use variables will not show up in the tooltip of add_dynamic_modifier**, while those that are set to a static value will. While this may make the dynamic modifier appear broken when only reading the tooltip, this will not be actually the case once it gets added. In this case, [the tooltip of the effect can be changed](<effects.md>), with [the effect adding the dynamic modifier hidden](<scopes.md>).

<!-- kit:begin id="dynamic-add-remove" at="section:Adding_a_dynamic_modifier" -->
**Kit correction** Parameters of the effect, and what `scope` really does.

| Key | Meaning | Source |
| --- | --- | --- |
| `modifier` | Name from `common/dynamic_modifiers/`. | [docs] `documentation/effects_documentation.md` |
| `days` | Optional. Makes the modifier temporary. May be a variable. | [docs] `documentation/effects_documentation.md` |
| `scope` | Optional. A state, a country tag or a variable holding one. | [docs] `documentation/effects_documentation.md` |

- The documentation example adds a modifier to state 12 with `scope = GER` and says it is added to the state "but only applies for country GER". Nothing in the documentation or in the header comment says the variables are read from the `scope` target, which is what the wiki text above claims. [docs] `documentation/effects_documentation.md`
- Vanilla uses `scope` to restrict who a state modifier applies to. `GER_blitzkrieg_modifier` is added in `every_state` with `scope = GER` in `common/decisions/GER.txt`, and its values are constants. `scope = THIS.owner` is used the same way in `common/decisions/CHL.txt`. [vanilla-confirmed 1.19.4.1]
- Treat "the variables are read off the `scope` country" as unconfirmed until it is tested. [unverified]
- `remove_dynamic_modifier` and `has_dynamic_modifier` need the same `scope` that `add_dynamic_modifier` used. [docs] `documentation/effects_documentation.md`
- Vanilla has 1,552 `add_dynamic_modifier` calls (1,217 in `common/`, 147 in `events/`, 188 in `history/`). 175 pass `days` (168 positive numbers and 7 use the variable `duration`) and 142 pass `scope`. No call passes a negative `days`, and `remove_dynamic_modifier` appears 730 times. What a zero or negative `days` does is not shown. [vanilla-confirmed 1.19.4.1]
- The usual timed form in vanilla:

```text
add_dynamic_modifier = {
    modifier = GER_blitzkrieg_modifier
    scope = GER
    days = 45
}
```
<!-- kit:end id="dynamic-add-remove" -->

## Static modifiers <a id="Static_modifiers"></a>

Static modifiers are stored in `/Hearts of Iron IV/common/modifiers/*.txt` files, where each code block within is a modifier block with the name being the ID of the static modifier. There are 5 main categories of static modifiers:

<!-- kit:begin id="static-files" at="section:Static_modifiers" -->
**Kit addition** Where vanilla keeps them.

- `common/modifiers/` holds `00_static_modifiers.txt` (global, weather, resistance and compliance, stability, difficulty, intelligence, relation and country-specific modifiers), `01_event_modifiers.txt` (an empty file) and three balance of power files: `AAT_power_balance_modifiers.txt`, `BBA_power_balance_modifiers.txt` and `MUN_power_balance_modifiers.txt`. [vanilla-confirmed 1.19.4.1]
- The header of `00_static_modifiers.txt` says the names are used by code and cannot be removed or renamed. [vanilla-confirmed 1.19.3]
- Some global modifiers are targeted. The comments in `00_static_modifiers.txt` say `passive_decryption_modifier` applies once a country's cipher is fully decrypted and `active_decryption_modifier` applies while active decryption bonuses are used against it. [vanilla-confirmed 1.19.3]
<!-- kit:end id="static-files" -->

### Global modifiers <a id="Global_modifiers"></a>

Global modifiers are applied by the hard-coded game features. Their names mustn't be changed, as the code uses them internally, but their effects can be edited. Examples of global modifiers are the penalty for non-core states or the effects of stability and war support.

### Difficulty modifiers <a id="Difficulty_modifiers"></a>

These are applied within `/Hearts of Iron IV/common/difficulty_settings/*.txt` files. This is used in the menu to strengthen specific countries at the game's start within game rules. If there are no difficulty settings defined, the menu will not be possible to open.
Each difficulty setting is defined as a `difficulty_setting = { ... }` block, which must lie within an overarching `difficulty_settings = { ... }` block. The following arguments can go into difficulty settings:

- `key = localisation_key` is the [localisation](<localisation.md>) key used as the name of the difficulty setting as it shows up in the game rules menu/
- `modifier = static_modifier` sets the static modifier to be used by this difficulty setting.
- `countries = { ... }` is a whitespace-separated list of country tags for which the difficulty setting applies.
- `multiplier = 2.0` is a value by which the static modifier gets multiplied at the max value. As there are 5 levels for each difficulty rule, including 0, this gets split into quarters for each level, with the second being a quarter, the third being a half, and the fourth being three quarters.

An example of a difficulty setting file is the following:

```text
difficulty_settings = {
    difficulty_setting = {
        key = difficulty_weaken_GER
        modifier = weaken_country
        countries = { GER }
        multiplier = 2.0
    }
    difficulty_setting = {
        key = difficulty_weaken_SOV
        modifier = weaken_country
        countries = { SOV UKR BLR }
        multiplier = 2.0
    }
}
```

<!-- kit:begin id="difficulty-vanilla" at="section:Difficulty_modifiers" -->
**Kit note** Vanilla has one file, `common/difficulty_settings/00_difficulty.txt`, with 8 settings. Each uses a quoted key such as `key = "custom_diff_strong_ger"`, `modifier = diff_strong_ai_generic` (defined in `00_static_modifiers.txt`) and `multiplier = 2.0`. `weaken_country` in the example above is not a vanilla modifier. [vanilla-confirmed 1.19.3]
<!-- kit:end id="difficulty-vanilla" -->

### Relation modifiers <a id="Relation_modifiers"></a>

Not to be confused with opinion modifiers. The relation modifiers apply a targeted modifier from one country towards an another one, automatically removed when the trigger is met. ROOT is the country that the modifier is applied to and FROM is the target. An example would be:

```text
test_relation_modifier = {
	valid_relation_trigger = {
		FROM = {
			has_government = ROOT		# same ruling party as ROOT
		}
	}
	compliance_gain = 0.2				# FROM's states have 20% more compliance gain when controlled by ROOT
}
```

They can be added by the add_relation_modifier effect, used as such:

```text
add_relation_modifier = {
	target = TAG
	modifier = test_relation_modifier
}
```

remove_relation_modifier, which works similarly, can remove them.

<!-- kit:begin id="relation-vanilla" at="section:Relation_modifiers" -->
**Kit addition** Relation modifiers in vanilla and their trigger.

- 18 relation modifiers are defined in `common/modifiers/00_static_modifiers.txt` (every entry with a `valid_relation_trigger`), for example `ROM_license_german_equipment`, `free_license` and `SOV_soviet_chinese_relations`. `ROM_license_german_equipment` sets `license_purchase_cost`, `ai_license_acceptance`, `license_production_speed` and `license_tech_difference_speed`. [vanilla-confirmed 1.19.4.1]
- `add_relation_modifier` is called 55 times in vanilla, `remove_relation_modifier` and `has_relation_modifier` 4 times each. [vanilla-confirmed 1.19.4.1]
- `has_relation_modifier = { target = TAG modifier = name }` is the trigger. Effects and trigger run in country scope. [docs] `documentation/effects_documentation.md` `documentation/triggers_documentation.md`
<!-- kit:end id="relation-vanilla" -->

### Province modifiers <a id="Province_modifiers"></a>

Province modifiers apply a modifier to a specific province rather than a state. They can be applied via the add_province_modifier effect, and removed with remove_province_modifier. More info on how to use these can be seen in the [effects](<effects.md>) page.
An example definition looks like

```text
mod_modifier = {
	army_speed_factor = -0.5
	army_defence_factor = 0.5
	dig_in_speed_factor = 0.5
}
```

Many state-scope modifiers will work in province scope as well. In order to make the GFX in GUI, you first need to edit `/Hearts of Iron IV/interface/countrystateview.gui`. The icon must be defined inside custom_icon_container, similarly to other examples. An example definition looks like

```text
iconType = {
	name = "<modifier name>_icon"
	spriteType = "GFX_modifiers_<modifier name>_icon"
	position = { x = 0 y = 0 }
	Orientation = "UPPER_LEFT"
}
```

The spriteType you have defined needs to be defined in `/Hearts of Iron IV/interface/*.gfx` similarly to this example:

```text
spriteType = {
	name = "GFX_modifiers_<modifier name>_icon"
	textureFile = "gfx/interface/modifiers_<modifier name>_icon.dds"
}
```

<!-- kit:begin id="province-params" at="section:Province_modifiers" -->
**Kit addition** Parameters of the effects (scope: state).

- `add_province_modifier` takes `static_modifiers = { mod_1 mod_2 }`, an optional `days` (temporary, may be a variable) and a province selector: `province = 500`, or `province = { ... }` with repeated `id = N`, `all_provinces`, `limit_to_coastal`, `limit_to_border`, `limit_to_naval_base` and `limit_to_victory_point`. `remove_province_modifier` takes the same selectors. [docs] `documentation/effects_documentation.md`
- Vanilla calls `add_province_modifier` 21 times and `remove_province_modifier` 7 times, for example `static_modifiers = { flooded }` with `province = { id = 9498 id = 391 }` in `common/decisions/HOL.txt`. [vanilla-confirmed 1.19.4.1]
- Static modifiers marked `# on Province` in `00_static_modifiers.txt` include `weather_mud`, `weather_extreme_cold`, `flooded` and `unplanned_offensive`. [vanilla-confirmed 1.19.3]
<!-- kit:end id="province-params" -->

### Balance of power modifiers <a id="Balance_of_power_modifiers"></a>

Balance of power modifiers typically include within of themselves the power_balance_daily and/or power_balance_weekly modifiers in order to gradually tip the balance towards one side. For example,

```text
my_bop_modifier = {
    power_balance_weekly = -0.01 # Changes by 1% each week to the left, in the range of -1 to 1.
}
```

Balance of power modifiers are added via [the add_power_balance_modifier effect](<effects.md>) as such:

```text
add_power_balance_modifier = {
    id = my_bop    # The ID of the balance of power
    modifier = my_bop_modifier # The modifier to add
}
```

[The remove_power_balance_modifier effect](<effects.md>), with the same syntax, or [remove_all_power_balance_modifiers](<effects.md>) can be used to remove these from the country.

<!-- kit:begin id="bop-modifiers" at="section:Balance_of_power_modifiers" -->
**Kit addition** Effects, trigger and console commands.

- `add_power_balance_modifier = { id = ... modifier = ... }` runs in any scope. The modifier "must be defined in the static modifier database". `remove_power_balance_modifier` takes the same keys and `remove_all_power_balance_modifiers = { id = ... }` takes only the id. `has_power_balance_modifier` tests for one. [docs] `documentation/effects_documentation.md` `documentation/triggers_documentation.md`
- Console: `bop_addmod <ID> <ModID>` and `bop_rmmod <ID> <ModID>`. [docs] `documentation/console_commands_documentation.md`
- Vanilla calls `add_power_balance_modifier` 38 times and `remove_power_balance_modifier` 61 times. The only definition in `00_static_modifiers.txt` is the test entry `_test_power_balance_mod` (`power_balance_daily = 0.02`). [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="bop-modifiers" -->

## Modifier definitions <a id="Modifier_definitions"></a>

Modifier definitions allow the creation of a custom modifier, which can be accessed as a variable when you wish to use it. After being defined, they function entirely like a new variable, being possible to read as a variable with the same `modifier@modifier_name` procedure. They will not have any effect by default and function only as a way to change the variable's value in an additive way with modifier blocks.
Each modifier token is defined within `/Hearts of Iron IV/common/modifier_definitions/*.txt` files as a separate code block, where the name of the code block serves as the ID of the modifier definition. There are the following arguments that can go inside of it:

- `color_type = good` decides the colour of the modifier's value itself. There are three values, `good`, `bad`, and `neutral`. `neutral` is permamently yellow, while `good` turns the positive values **green** and negative values **red**. `bad` is the reversal of `good`.
- `value_type = percentage` decides the way the number will show up in the tooltip. There are the following values this argument can be set to:
  - `number` will make the exact value of the modifier show up. 0.02 will show up like "Modifier definition: 0.02".
  - `percentage` will make the modifier show up as a percentage on the scale from 0 to 1. 0.2 will show up like "Modifier token: 20%".
  - `percentage_in_hundred` will make the modifier show up as a percentage on the scale from 0 to 100. 10 will show up like "Modifier token: 10%".
  - `yes_no` shows up as a boolean: anything larger than 1 will shows up as `yes`, while 0 will show up as `no`.
- `precision = 1` decides how many numbers will be shown after the period in the tooltip. For example, if it is set to 1, the tooltip will show 0.341 as if it was 0.3. Note that the game inherently does not support more than 3 decimal numbers, so it cannot be larger than 3.
- `postfix` decides what will be added after the value of the modifier in the tooltip. Allowed values are 'none' (Default), 'days', 'hours', and 'daily'.
- `category` decides on the category of the modifier. By default, the category is 'all', which makes it be in every single category. Certain tooltips will only show modifiers if they belong to a certain category. It is possible to set multiple categories for the same modifier definition by defining them one after another.

The allowed values are 'none', 'all', 'country', 'state', 'unit_leader', 'army', 'naval', 'air', 'peace', 'politics', 'ai', 'defensive', 'aggressive', 'war_production', 'military_advancements', 'military_equipment', 'autonomy', 'government_in_exile', and 'intelligence_agency'.

The modifier definition's ID is also used as the [localisation](<localisation.md>) key needed to change the name of the modifier depending on the currently turned on language.

<!-- kit:begin id="definitions-defaults" at="section:Modifier_definitions" -->
**Kit addition** Defaults and vanilla use, from the header of `common/modifier_definitions/modifier_definitions.txt`.

| Key | Allowed values | Default |
| --- | --- | --- |
| `color_type` | `good`, `neutral`, `bad` | `bad` |
| `value_type` | `number`, `percentage`, `percentage_in_hundred`, `yes_no` | `number` |
| `precision` | decimals shown in the tooltip, up to 3 | not stated |
| `postfix` | `none`, `days`, `hours`, `daily` | `none` |
| `category` | `none`, `all`, `naval`, `air`, `unit_leader`, `country`, `state`, `army`, `peace`, `politics`, `ai`, `defensive`, `aggressive`, `war_production`, `military_advancements`, `military_equipment`, `autonomy`, `government_in_exile`, `intelligence_agency` (repeat the key for several) | `all` |

All rows: [vanilla-confirmed 1.19.3] `common/modifier_definitions/modifier_definitions.txt`.

- The header says the game itself never uses these definitions: read them with `modifier@token` (state and country), or `leader_modifier@token` and `unit_modifier@token` (unit leader). The token doubles as the localisation key. [vanilla-confirmed 1.19.3]
- Vanilla defines only three, all in `common/modifier_definitions/lar_operation_modifiers_pre_definition.txt`: `operation_outcome`, `operation_cost` and `operation_infiltrate_outcome`, with the comment that modifiers used in static modifiers must be predefined there. [vanilla-confirmed 1.19.3]
- The modifier documentation also uses the categories `faction`, `character` and `scientist`. [docs] `documentation/modifiers_documentation.md`
- The definition header lists none of those three. [vanilla-confirmed 1.19.3] Whether a definition accepts them is untested. [unverified]
<!-- kit:end id="definitions-defaults" -->

### Examples <a id="Examples"></a>

```text
modifier_definition_example = {
	color_type = good
	value_type = number
	precision = 1
	postfix = daily

	category = country
	category = state
}
modifier_definition_example_2 = {
    color_type = bad
    value_type = percentage
}
```

### Using in variables <a id="Using_in_variables"></a>

The function of modifier definitions is to modify the value of a game variable, which can be read by other variables. You can set a variable to be equal to the sum of all values of the same modifier token in the current scope by doing `set_variable = { var_name = modifier@modifier_token_name }`. This example will set var_name to be equal to the total value of modifier_token_name.

Note that, unlike countries and states, unit leaders use leader_modifier@modifier_definition_name or unit_modifier@modifier_definition_name in their scopes.

Example usage of making a modifier token create civilian factories in random core states monthly, in any [on action](<on_actions.md>) file:

**Example**

```text
on_actions = {
    on_monthly = {
        effect = {
            if = {
                limit = {
                    check_variable = { modifier@modifier_definition_example > 0 }
                }
                for_loop_effect = {
                    start = 0
                    end = modifier@modifier_definition_example
                    random_owned_controlled_state = {
                        limit = {
                            is_core_of = ROOT
                            free_building_slots = {
                                building = industrial_complex
                                size > 0
                                include_locked = no
                            }
                        }
                        add_building_construction = {
                            type = industrial_complex
                            level = 1
                            instant_build = yes
                        }
                    }
                }
            }
        }
    }
}
```

## Opinion modifiers <a id="Opinion_modifiers"></a>

Despite their name, opinion modifiers are not related to modifiers in any way, instead they are used to modify the diplomatic or economic relations between a pair of countries.

The opinion modifiers are made in any `/Hearts of Iron IV/common/opinion_modifiers/*.txt` file as an entry in the `opinion_modifiers = { ... }` block, with the name of the entry being the ID of the opinion modifier. In case of there being several entries with the same ID, the one that was [evaluated later based on the filename and order in files](<modding.md#Loading_files>) will take priority, meaning that copying a base game file is never necessary in a mod.

There are the following attributes that are used in opinion modifiers:

- `trade = yes` is used to decide whether the opinion modifier changes the diplomatic relations or the trade opinion from one country to another. If unset, defaults to being false making it diplomatic.
- `value = -10` is the value of the modifier that decides by how much the diplomatic or trade opinion should change once the opinion modifier is added.
- `decay = 1` details the speed at which the opinion modifier trends towards zero monthly. Optional, defaults to the modifier not changing if unset.
- `days = 10` | `months = 2` | `years = 1` decides the time for how much the opinion modifier should last before it will get automatically removed. A month is interpreted as exactly 30 days, while a year is 365. Optional, the modifier will be permanent if neither is set.
- `min_trust = 10` | `max_trust = -10` detail the minimum and maximum value that the opinion modifier can change to. As the only non-hardcoded way to change the value of an existing opinion modifier is through decay, this can be used to limit how far it can apply.

The [localisation](<localisation.md>) is created in any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file encoded in UTF-8 using the byte order mark (aka UTF-8-BOM), with the localisation key being the name of the modifier.

<!-- kit:begin id="opinion-vanilla" at="section:Opinion_modifiers" -->
**Kit addition** What vanilla actually uses.

- The header of `common/opinion_modifiers/00_opinion_modifiers.txt` lists `value`, `min_trust`, `max_trust`, `decay`, `months`/`years`/`days` and `trade`, and no other keys. [vanilla-confirmed 1.19.3]
- 811 opinion modifiers are defined in 13 files, with 794 distinct ids, so 17 ids are defined twice. Key use: `value` 811, `months` 258, `trade` 58, `years` 55, `decay` 41, and `days`, `min_trust` and `max_trust` once each. [vanilla-confirmed 1.19.4.1]
- `target = yes` appears once, on the second `guarantee` entry (`value = 35`, in `00_opinion_modifiers.txt`) next to a plain `guarantee` with `value = 0`. It is not in the header. [vanilla-confirmed 1.19.4.1] What it does is not shown. [unverified]
- Vanilla examples of the bounds: `justifying_war_goal = { value = -10 min_trust = -10 days = 10 decay = 1 }` and `improve_relation = { value = 0 months = 0 decay = 3 max_trust = 100 }`. [vanilla-confirmed 1.19.3]
- The localisation key is the modifier id, for example `holds_our_cores:` in `localisation/english/diplomacy_l_english.yml`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="opinion-vanilla" -->

### Examples <a id="Examples_2"></a>

Inside of a new `/Hearts of Iron IV/common/opinion_modifiers/*.txt` file:

```text
opinion_modifiers = {
    test_trade_modifier = {
        trade = yes
        value = -100    # Provides -100 trade opinion for 2 months
        months = 2
    }
    test_diplomatic_modifier = {
        value = 20      # Provides +20 diplomatic opinion that decays by 0.5 per month
        decay = 0.5
    }
}
```

Inside of a new `/Hearts of Iron IV/localisation/english/*_l_english.yml` file:

```text
l_english:
 test_trade_modifier: "Testing trade modifier"
 test_diplomatic_modifier: "Testing diplomatic modifier"
```

### Implementation <a id="Implementation"></a>

New opinion modifiers can only be added using the [add_opinion_modifier effect](<effects.md>) (or the similar [reverse_add_opinion_modifier](<effects.md>)) in any effect block, such as a [focus reward](<national_focus_modding.md#Effects>), a [country history file](<country_creation.md>), or an idea's [on_add and on_remove](<idea_modding.md#Effects>). Similarly, already applied new opinion modifiers can only be removed with [remove_opinion_modifier](<effects.md>). When `add_opinion_modifier` is used to apply an opinion modifier, only the country where the effect is executed will change its opinion towards the target.

There is no way to use a modifier block to directly apply an opinion modifier, but it can be simulated by adding or removing an opinion modifier at the same time the modifier block's effects are. For example, this national spirit would simulate applying an opinion modifier towards every other country that has the idea:

**Example code of a national spirit that uses opinion modifiers**

```text
ideas = {
    country = {
        idea_opinion_modifier = {
            on_add = { # Note: Doesn't work if the idea is added within country history or a bookmark's effect.
                every_other_country = { # If it's added in country history, then replicate the effects there as well.
                    limit = {
                        has_idea = idea_opinion_modifier
                    }
                    add_opinion_modifier = {
                        target = ROOT
                        modifier = test_diplomatic_modifier
                    }
                    reverse_add_opinion_modifier = {
                        target = ROOT
                        modifier = test_diplomatic_modifier
                    }
                }
            }
            on_remove = {
                every_other_country = {
                    limit = {
                        has_idea = idea_opinion_modifier
                    }
                    remove_opinion_modifier = {
                        target = ROOT
                        modifier = test_diplomatic_modifier
                    }
                    ROOT = {
                        remove_opinion_modifier = {
                            target = PREV
                            modifier = test_diplomatic_modifier
                        }
                    }
                }
            }
            modifier = {
                custom_modifier_tooltip = add_opinion_modifier_tt # Since on_add/on_remove aren't shown to the player
            }
        }
    }
}
```

<!-- kit:begin id="opinion-effects" at="section:Implementation" -->
**Kit addition** Vanilla calls: `add_opinion_modifier` 2,266, `reverse_add_opinion_modifier` 89, `remove_opinion_modifier` 151 and `has_opinion_modifier` 98. All four run in country scope. [vanilla-confirmed 1.19.4.1] [docs] `documentation/effects_documentation.md` `documentation/triggers_documentation.md`
<!-- kit:end id="opinion-effects" -->

## List of modifiers <a id="List_of_modifiers"></a>

<!-- kit:begin id="list-outdated" at="heading:List_of_modifiers" -->
**Kit correction** The tables below are incomplete for 1.19.3. The game documents 722 plain modifiers and 38 template families (`production_speed_<Building>_factor` and similar). 167 of the 722 are never named on this page; the kit tables under each section add them. [docs] `documentation/modifiers_documentation.md`
<!-- kit:end id="list-outdated" -->

The list of modifiers may be outdated. A complete, but unsorted, list of modifiers can be found in `/Hearts of Iron IV/documentation/modifiers_documentation.html` or `/Hearts of Iron IV/documentation/modifiers_documentation.md`.

<!-- kit:begin id="added-tables-legend" at="section:List_of_modifiers" -->
### Kit: How the added tables read <a id="kit-added-tables-legend"></a>

- Modifier, Categories and Format come from the game documentation. `dp` is the number of decimals the tooltip shows; any value accepts up to 3 decimals. [docs] `documentation/modifiers_documentation.md`
- Meaning is the in-game wording from `localisation/english/modifiers_l_english.yml` and the MIO and effect strings, paraphrased. [vanilla-confirmed 1.19.3] The text file changed in 1.19.4.1 and the old text is gone, so a reworded single row would not show. A word-overlap check of the meaning column against the new file found no row that contradicts it. [unverified]
- A meaning that starts with `~` is a guess from the name and its vanilla use. [unverified]
- An empty meaning means the name is self-explanatory. `(not described in the docs)` means there is no in-game text and no clear vanilla use.
- "Unused in vanilla" means no `key = value` use in `common/`, `events/` or `history/`. [vanilla-confirmed 1.19.4.1]
- Sample checks against vanilla use: `army_non_core_attack_factor` is negative in `common/ideas/australia.txt`; `naval_invasion_prep_days` is -5 and -10 in `special_forces_subdoctrines.txt` and `MTG_naval_Support.txt`; `army_intel_to_others` is -15 and -50 in a trait and a decision; `peace_score_ratio_transferred_to_players` is used by the `diff_*_ai` static modifiers; `river_crossing_factor_against` sits inside `targeted_modifier` in `common/ideas/GER.txt`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="added-tables-legend" -->

<!-- kit:begin id="template-families" at="section:List_of_modifiers" -->
### Kit: Template modifier families <a id="kit-template-families"></a>

The documentation lists these as template entries; each pattern stands for one modifier per slot value. Several wiki rows below name only some of the values. All rows: [docs] `documentation/modifiers_documentation.md`

| Pattern | Categories | Format | What fills the slot |
| --- | --- | --- | --- |
| `<Building>_max_level_terrain_limit`<br>`state_<Building>_max_level_terrain_limit` | country<br>state | 0 dp | Two forms: a building token (54 tokens, for example `bunker`) or a building plus a terrain (770 tokens, for example `bunker_hills`). |
| `production_cost_<Building>_factor`<br>`production_speed_<Building>_factor`<br>`repair_speed_<Building>_factor` | country | 2 dp | 55 building tokens, listed below the table. |
| `state_production_speed_<Building>_factor`<br>`state_repair_speed_<Building>_factor` | state | 2 dp | The same 55 building tokens. |
| `country_resource_<Resource>`<br>`country_resource_cost_<Resource>`<br>`local_resources_<Resource>_factor` | country | 0 dp | 7 resources: `aluminium`, `chromium`, `coal`, `oil`, `rubber`, `steel`, `tungsten`. |
| `state_resource_<Resource>`<br>`state_resource_cost_<Resource>`<br>`temporary_state_resource_<Resource>`<br>`state_resources_<Resource>_factor` | state | 0 dp | The same 7 resources. |
| `experience_gain_<Unit>_combat_factor`<br>`experience_gain_<Unit>_mission_factor`<br>`experience_gain_<Unit>_training_factor` | naval, country | 0 dp | 157 unit tokens: sub-units, ships and aircraft (for example `infantry`, `armored_car`, `destroyer`, `fighter`). The documentation lists three variants (combat, mission, training); the wiki tables name only combat and training. |
| `unit_<Unit>_design_cost_factor` | naval, country, army | 2 dp | The same 157 unit tokens. |
| `<Equipment>_design_cost_factor` | country | 0 dp | 195 equipment, chassis and airframe tokens (for example `infantry_equipment`, `light_tank_chassis`, `medium_plane_fighter_airframe_2`). |
| `module_<EquipmentModule>_design_cost_factor` | naval, country, army | 2 dp | 312 equipment module tokens (for example `engine_1_1x`, `armor_plate_large`). |
| `production_cost_max_<NavalEquipment>` | naval | 0 dp | 9 tokens: `convoy`, `floating_harbor_equipment`, `repair_ship_hull`, `ship_hull_carrier`, `ship_hull_cruiser`, `ship_hull_heavy`, `ship_hull_light`, `ship_hull_submarine`, `support_ship_hull`. |
| `<Doctrine>_mastery_gain_factor` | country | 0 dp | Three kinds of token: the 4 doctrine folders (`air`, `land`, `naval`, `special_forces`), 12 grand doctrines and 95 sub-doctrines. |
| `<Doctrine>_track_mastery_gain_factor` | country | 0 dp | 14 tracks: `armor`, `capital_ships`, `carriers`, `combat_support`, `fighter_aircraft`, `heavy_aircraft`, `infantry`, `medium_aircraft`, `operations`, `screens`, `special_forces_first`, `special_forces_second`, `strike_aircraft`, `submarines`. |
| `<Technology>_cost_factor` | country | 0 dp | 39 technology category tokens, all starting with `cat_` (for example `cat_mobile_warfare`, `cat_synth_oil`, `cat_torpedoes`). Not limited to doctrines. |
| `<IdeaGroup>_cost_factor` | country | 0 dp | 25 idea groups (for example `economy`, `army_chief`, `hidden_ideas`, `army_spirit`). |
| `<IdeaCategory>_category_type_cost_factor` | country | 0 dp | `air_spirit`, `army_spirit`, `navy_spirit`. |
| `<Ideology>_acceptance`<br>`<Ideology>_drift`<br>`<Ideology>_drift_from_guarantees` | politics | 0 dp, 2 dp, 2 dp | `communism`, `democratic`, `fascism`, `neutrality`. |
| `<Operation>_cost`<br>`<Operation>_outcome`<br>`<Operation>_risk` | intelligence_agency | 0 dp | 41, 39 and 42 slot values: operation ids from `common/operations/` (for example `operation_infiltrate_civilian`, `bruneval_raid`, `FRA_coup_in_indochina`) plus the generic tokens `operation`, `operation_coup`, `operation_infiltrate`, `operation_steal_tech` and `target_sabotage`. The three sets differ slightly: `_cost` has no `operation_steal_tech`, and `_outcome` and `_risk` have no `operation_coup`. An operation only reacts to a modifier it names in its own `cost_modifiers`, `outcome_modifiers` or `risk_modifiers` list [docs `common/operations/_documentation.md`]. Vanilla operations name only `operation_cost`, `operation_infiltrate_cost`, `operation_coup_cost`, `target_sabotage_cost`, `operation_outcome`, `operation_infiltrate_outcome`, `operation_steal_tech_outcome`, `boost_resistance_factor`, `target_sabotage_factor`, `operation_risk`, `operation_infiltrate_risk`, `operation_steal_tech_risk` and `target_sabotage_risk`, so per-operation names such as `bruneval_raid_cost` are valid but no vanilla operation reads them [vanilla-confirmed 1.19.4.1 `common/operations/`]. |
| `<SpecialProject>_speed_factor` | country, state | 0 dp | 66 tokens: the `sp_*` projects and `specialization_air`, `specialization_land`, `specialization_naval`, `specialization_nuclear`. |
| `<Trait>_xp_gain_factor` | naval, country, army | 2 dp | For 29 unit leader traits whose token already starts with `trait_` (for example `trait_cautious`, giving `trait_cautious_xp_gain_factor`). |
| `trait_<Trait>_xp_gain_factor` | naval, country, army | 2 dp | For 165 traits whose token has no `trait_` prefix (for example `BALTIC_anti_bolshevik`). |
| `<CombatTactic>_preferred_weight_factor` | country | 2 dp | 56 tokens: `nullCombatTactic` and the `tactic_*` combat tactics. The documentation text calls it a naval weight. |
| `<ModifierStat>_factor`<br>`<ModifierStatValue>_value_factor` | country, state | 0 dp | Only `naval_general_support` and `naval_repair_support`, the support-ratio static modifiers in `common/modifiers/00_static_modifiers.txt`. (not described in the docs) |

The 55 building tokens:

```text
air_base, air_facility, anti_air_building, arms_factory, bunker, canal_kiel, canal_panama,
cataract_dam_mountain, coastal_bunker, commercial_nuclear_reactor, dam, dam_mountain, dockyard,
energy_infrastructure, fuel_silo, industrial_complex, industrial_infrastructure,
infrastructure, land_facility, landmark_berlin_reichstag, landmark_berlin_volkshalle,
landmark_big_ben, landmark_bojnice_castle, landmark_colosseum, landmark_cristo_redentor,
landmark_eiffel_tower, landmark_forbidden_city, landmark_great_wall_section,
landmark_hagia_sophia, landmark_hakko_ichiu, landmark_hofburg_palace, landmark_kremlin,
landmark_nanjing_presidential_palace, landmark_nanjing_presidential_palace_gen,
landmark_nanjing_presidential_palace_prc, landmark_national_diet, landmark_prague_castle,
landmark_sadabad_complex, landmark_statue_of_liberty, landmark_taj_mahal,
landmark_tokyo_imperial_palace, mega_gun_emplacement, naval_base, naval_facility,
naval_headquarters, naval_supply_hub, nuclear_facility, nuclear_reactor,
nuclear_reactor_heavy_water, radar_station, rail_way, rocket_site, stronghold_network,
supply_node, synthetic_refinery
```

Corrections to the rows below. [docs] `documentation/modifiers_documentation.md`

- Resources: there are 7, and `coal` exists for every resource pattern.
- Buildings: `production_speed_<building>_factor`, `repair_speed_<building>_factor`, `production_cost_<building>_factor` and the `state_` variants take 55 tokens, including `air_facility`, `land_facility`, `naval_facility`, `nuclear_facility`, `energy_infrastructure`, `supply_node` and the landmarks.
- Tracks: `<doctrine track>_track_mastery_gain_factor` also accepts `special_forces_first` and `special_forces_second`.
- Mastery: `<land/air/naval>_mastery_gain_factor` also accepts `special_forces`, every grand doctrine and every sub-doctrine.
- Technology cost: `<doctrine category>_cost_factor` is the `<Technology>_cost_factor` family and takes any of the 39 `cat_*` technology categories, not only doctrines.
<!-- kit:end id="template-families" -->

### Country scope <a id="Country_scope"></a>

#### General <a id="General"></a>

General country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| monthly_population | Changes the monthly population gain in states owned by the country. | `monthly_population = 0.5` | Percentual. | Does not work with states. | 1.0 |
| nuclear_production | Enables the production of nukes. | `nuclear_production = 1` | Boolean (only 1). |  | 1.0 |
| nuclear_production_factor | Changes speed at which nukes are produced. | `nuclear_production_factor = 0.5` | Percentual. | Works in state scope, in which case it'll apply to the owner. | 1.0 |
| research_sharing_per_country_bonus | Changes the bonus in research speed per country when technology sharing. | `research_sharing_per_country_bonus = 0.5` | Flat. |  | 1.3 |
| research_sharing_per_country_bonus_factor | Changes the bonus in research speed per country when technology sharing by a percentage. | `research_sharing_per_country_bonus_factor = 0.5` | Percentual. |  | 1.3 |
| research_speed_factor | Changes the research speed. | `research_speed_factor = 0.5` | Percentual. |  | 1.0 |
| special_project_speed_factor | Changes the speed that special projects are completed. | `special_project_speed_factor  = 0.05` | Percentual. |  | 1.16 |
| local_resources_factor | Resource extraction efficiency. Modifies the amount of available resources. | `local_resources_factor = 0.3` | Percentual. |  | 1.0 |
| surrender_limit | Changes the percentage of victory points the country needs to lose control of to capitulate. | `surrender_limit = 0.1` | Percentual. | The larger, the more victory points are needed to capitulate a country. | 1.0 |
| max_surrender_limit_offset | Controls the maximum surrender progress of a nation. | `max_surrender_limit_offset = 0.3` | Flat. | For example, 0.4 means that the country cannot require more than 60% victory points to capitulate, no matter the surrender_limit. | 1.9 |
| forced_surrender_limit | Changes the percentage of victory points the country needs to lose control of to capitulate, bypassing the minimum or maximum. | `forced_surrender_limit = 0.1` | Percentual. | The larger, the more victory points are needed to capitulate a country. Applied after the minimum and maximum are applied, leading to making it possible to have it below 20% or above the maximum defined with max_surrender_limit_offset. | 1.0 |
| country_resource_<resource> | Directly modifies the country's resource stockpile. | `country_resource_oil = 10` | Flat. |  | 1.0 |
| country_resource_cost_<resource> | Directly modifies the country's resource stockpile. | `country_resource_cost_aluminium = 10` | Flat. |  | 1.0 |
| resource_trade_cost_bonus_per_factory | Modifies the country's cost to buy resources from others. | `resource_trade_cost_bonus_per_factory = 1` | Flat. | A positive value will grant more resources for the same amount of factories traded while a negative amount will do the opposite. Does not affect other countries buying resources from the one modified. | 1.16 |
| factory_energy_consumption | Directly modifies the country's energy usage per factory | `factory_energy_consumption = 0.1` | Percentual. |  | 1.17 |

<!-- kit:begin id="add-gen" at="section:General" -->
**Kit addition** Documented modifiers this section does not list (5). Format and meaning columns are explained under [How the added tables read](#kit-added-tables-legend). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `energy_gain_factor` | country | 2 dp | Energy gained per unit of coal |
| `energy_scale_per_trade_factory_export_factor` | country | 2 dp | How much traded factories affect factory energy usage (unused in vanilla) |
| `special_project_facility_supply_consumption_factor` | country | 2 dp | Supply used by special project facilities |
| `thermonuclear_production` | country | bool | Allows thermonuclear bombs |
| `thermonuclear_production_factor` | country | 0 dp | Thermonuclear bomb production rate |
<!-- kit:end id="add-gen" -->

#### Politics <a id="Politics"></a>

Political country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| min_export | Changes the amount of resources to market. | `min_export = 0.5` | Flat. |  | 1.0 |
| trade_opinion_factor | Makes AI more likely to purchase resources from this country. | `trade_opinion_factor = 0.5` | Percentual. |  | 1.0 |
| defensive_war_stability_factor | Changes the penalty to the stability invoked by participating in a defensive war. | `defensive_war_stability_factor = 0.5` | Percentual. |  | 1.0 |
| disabled_ideas | Disables manually changing ideas (including ministers and laws). | `disabled_ideas = 1` | Boolean (only 1). |  | 1.9 |
| \<idea\|character slot>_cost_factor | Changes the cost in political power to add an idea or character within the specified slot. | `political_advisor_cost_factor = 0.5` | Percentual. | Idea slots can be found in common/idea_tags. [Requires an idea or a character of that category to be present in an earlier-evaluated file.](<idea_modding.md>) | 1.4 |
| <idea category type>_category_type_cost_factor | Changes the cost in army experience to add an idea within any of the categories with the specified type. | `air_spirit_category_type_cost_factor = 0.5` | Percentual. | Idea category definitions can be found in `/Hearts of Iron IV/common/idea_tags/*.txt` files, a type is assigned with `type = army_spirit`. | 1.10 |
| <ledger>_advisor_cost_factor | Changes the cost in political power to add an advisor assigned the specified military ledger. | `air_advisor_cost_factor = 0.5` | Percentual. | Ledgers are assigned to categories and characters in common/idea_tags and common/ideas. Modifier works with air, army, and navy. | 1.11 |
| unit_leader_as_advisor_cp_cost_factor | Changes the cost in command power to turn a unit leader into an advisor. | `unit_leader_as_advisor_cp_cost_factor = 0.5` | Percentual. |  | 1.11 |
| improve_relations_maintain_cost_factor | Changes the cost in political power to maintain improvement of relations. | `improve_relations_maintain_cost_factor = 0.5` | Percentual. |  | 1.4 |
| female_random_country_leader_chance | Changes the chance for a randomly-generated country leader to be female. | `female_random_country_leader_chance = 0.3` | Percentual. |  | 1.0 |
| offensive_war_stability_factor | Modifies the stability penalty received from participating in an offensive war. | `offensive_war_stability_factor = 0.3` | Percentual. |  | 1.0 |
| party_popularity_stability_factor | Modifies the stability gained by the popularity of the ruling party. | `party_popularity_stability_factor = 0.3` | Percentual. |  | 1.0 |
| political_power_cost | Daily cost in political power. | `political_power_cost = 0.3` | Flat. |  | 1.0 |
| political_power_gain | Modifies daily gain in political power. | `political_power_gain = 0.3` | Flat. |  | 1.0 |
| political_power_factor | Modifies daily gain in political power by a percentage. | `political_power_factor = 0.3` | Percentual. |  | 1.0 |
| stability_factor | Modifies stability of the country. | `stability_factor = 0.3` | Flat. |  | 1.0 |
| stability_weekly | Modifies weekly stability gain of the country. | `stability_weekly = 0.01` | Flat. |  | 1.0 |
| stability_weekly_factor | Modifies weekly stability gain of the country by a percentage. | `stability_weekly_factor = 0.3` | Percentual. |  | 1.0 |
| war_stability_factor | Modifies the stability loss caused by being at war. | `war_stability_factor = 0.3` | Percentual. |  | 1.0 |
| war_support_factor | Modifies war support of the country. | `war_support_factor = 0.3` | Flat. |  | 1.0 |
| war_support_weekly | Modifies weekly war support gain of the country. | `war_support_weekly = 0.01` | Flat. |  | 1.0 |
| war_support_weekly_factor | Modifies weekly war support gain of the country by a percentage. | `war_support_weekly_factor = 0.3` | Percentual. |  | 1.0 |
| weekly_casualties_war_support | Modifies weekly war support gain of the country depending on the casualties suffered by it. | `weekly_casualties_war_support = 0.006` | Percentual. |  | 1.12 |
| weekly_convoys_war_support | Modifies weekly war support gain of the country depending on the amount of its convoys that have been sunk. | `weekly_convoys_war_support = 0.006` | Percentual. |  | 1.12 |
| weekly_bombing_war_support | Modifies weekly war support gain of the country depending on the enemy bombing of its states. | `weekly_bombing_war_support = 0.006` | Percentual. |  | 1.12 |
| drift_defence_factor | Ideology drift defense. | `drift_defence_factor = 0.3` | Percentual. |  | 1.0 |
| power_balance_daily | Pushes the power balance by a specified amount on each day. | `power_balance_daily = 0.01` | Flat. | Positive values result in it being pushed right, while negatives result in it being pushed left. | 1.12 |
| power_balance_weekly | Pushes the power balance by a specified amount on each week. | `power_balance_weekly = 0.01` | Flat. | Positive values result in it being pushed right, while negatives result in it being pushed left. | 1.12 |
| <ideology>_drift | Daily gain of the specified ideology. | `communism_drift = 0.03` | Flat. |  | 1.0 |
| <ideology>_acceptance | Likelihood of AI to accept offers from countries of the specified ideology. | `fascism_acceptance = 50` | Flat. |  | 1.0 |

<!-- kit:begin id="add-pol" at="section:Politics" -->
**Kit addition** Documented modifiers this section does not list (2). Format and meaning columns are explained under [How the added tables read](#kit-added-tables-legend). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `army_advisor_cost_factor` | army | 0 dp |  |
| `navy_advisor_cost_factor` | naval | 0 dp |  |
<!-- kit:end id="add-pol" -->

#### Diplomacy <a id="Diplomacy"></a>

Diplomatic country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| civil_war_involvement_tension | Changes the world tension amount necessary to intervene in an ally's civil war. | `civil_war_involvement_tension = 0.5` | Flat. |  | 1.0 |
| enemy_declare_war_tension | Changes the world tension required for an enemy to justify a wargoal on us. | `enemy_declare_war_tension = 0.5` | Flat. |  | 1.0 |
| enemy_justify_war_goal_time | Changes the time required for an enemy to justify a wargoal on us. | `enemy_justify_war_goal_time = 0.5` | Percentual. | This also modifies the cost in political power. | 1.0 |
| faction_trade_opinion_factor | Changes the opinion gain gained by trade between faction members. | `faction_trade_opinion_factor = 0.5` | Percentual. |  | 1.0 |
| generate_wargoal_tension | Changes the necessary tension for us to generate a wargoal. | `generate_wargoal_tension = 0.3` | Flat. |  | 1.0 |
| guarantee_cost | Cost in political power for the country to guarantee an another country. | `guarantee_cost = 0.3` | Percentual. |  | 1.4 |
| guarantee_tension | Necessary world tension for the country to guarantee an another country. | `guarantee_tension = 0.3` | Flat. |  | 1.0 |
| join_faction_tension | Necessary world tension for the country to join a faction. | `join_faction_tension = 0.3` | Flat. |  | 1.0 |
| justify_war_goal_time | The amount of time necessary to justify a wargoal. | `justify_war_goal_time = 0.3` | Percentual. | This also modifies the cost in political power. | 1.0 |
| justify_war_goal_when_in_major_war_time | The amount of time necessary to justify a wargoal when in a war with a major country. | `justify_war_goal_when_in_major_war_time = 0.3` | Percentual. | This also modifies the cost in political power. | 1.0 |
| lend_lease_tension | Necessary world tension for the country to lend-lease. | `lend_lease_tension = 0.3` | Flat. |  | 1.0 |
| lend_lease_tension_with_overlord | Necessary world tension for the country to lend-lease to its overlord. | `lend_lease_tension_with_overlord = 0.3` | Flat. |  | 1.13 |
| opinion_gain_monthly | Changes opinion gain from the 'Improve relations' diplomatic action. | `opinion_gain_monthly = 5` | Flat. |  | 1.0 |
| opinion_gain_monthly_factor | Changes opinion gain from the 'Improve relations' diplomatic action by a percentage. | `opinion_gain_monthly_factor = 0.3` | Percentual. |  | 1.0 |
| opinion_gain_monthly_same_ideology | Changes opinion gain from the 'Improve relations' diplomatic action for countries of the same ideology. | `opinion_gain_monthly_same_ideology = 5` | Flat. |  | 1.0 |
| opinion_gain_monthly_same_ideology_factor | Changes opinion gain from the 'Improve relations' diplomatic action for countries of the same ideology by a percentage. | `opinion_gain_monthly_same_ideology_factor = 0.3` | Percentual. |  | 1.0 |
| request_lease_tension | Necessary world tension for the country to request lend-lease. | `request_lease_tension = 0.3` | Percentual. |  | 1.9 |
| annex_cost_factor | Modifies the cost in victory points to annex states in peace deals. | `annex_cost_factor = 0.1` | Percentual. | Partially deprecated, please instead use common/peace_conference/cost_modifiers | 1.0 |
| puppet_cost_factor | Modifies the cost in victory points per state to puppet countries in peace deals. | `puppet_cost_factor = 0.1` | Percentual. | Partially deprecated, please instead use common/peace_conference/cost_modifiers | 1.0 |
| send_volunteer_divisions_required | Changes the number of divisions needed to send volunteers. | `send_volunteer_divisions_required = -0.3` | Percentual. |  | 1.0 |
| send_volunteer_factor | Changes the number of divisions the country can send as volunteers by a percentage. | `send_volunteer_factor = 0.3` | Percentual. |  | 1.0 |
| send_volunteer_size | Changes the number of divisions the country can send as volunteers. | `send_volunteer_size = 5` | Flat. |  | 1.0 |
| send_volunteers_tension | Changes the world tension necessary for the country to send volunteers. | `send_volunteers_tension = -0.1` | Percentual. |  | 1.0 |
| air_volunteer_cap | Changes the amount of airforce you can send as volunteers. | `air_volunteer_cap = 100` | Flat. |  | 1.5 |
| embargo_threshold_factor | Changes the necessary world tension level in order to be able to embargo a country. | `embargo_threshold_factor = 0.2` | Percentual. |  | 1.12 |
| embargo_cost_factor | Changes the cost in political power to send an embargo. | `embargo_cost_factor = 0.3` | Percentual. |  | 1.12 |

<!-- kit:begin id="add-dip" at="section:Diplomacy" -->
**Kit addition** Documented modifiers this section does not list (7). Format and meaning columns are explained under [How the added tables read](#kit-added-tables-legend). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `annex_subject_cost_factor` | country | 2 dp |  |
| `can_guarantee_other_ideologies` | country | bool | Allows guaranteeing countries of other ideologies; the same name is also a `rule` in ideas and ideologies |
| `faction_influence_contribution_factor` | faction | 2 dp | Influence gained in a faction from contribution |
| `faction_influence_war_score_factor` | faction | 2 dp | Influence gained in a faction from war score |
| `faction_subject_contribution_gain` | faction | 2 dp | Reduction in contribution gain caused by being a subject |
| `peace_score_ratio_transferred_to_overlord` | peace | 2 dp | Share of a puppet's peace score that goes to its overlord |
| `peace_score_ratio_transferred_to_players` | peace | 2 dp | Share of AI countries' peace score that goes to human players |
<!-- kit:end id="add-dip" -->

<!-- kit:begin id="annex-puppet-status" at="section:Diplomacy" -->
**Kit correction** The table says `annex_cost_factor` and `puppet_cost_factor` are "partially deprecated". In 1.19.4.1 both are still documented (`annex_cost_factor`: categories peace, aggressive; `puppet_cost_factor`: peace, defensive) and the in-game text still reads "Changes the cost of annexing a country" and "Changes the cost of puppeting a country". [docs] `documentation/modifiers_documentation.md` [vanilla-confirmed 1.19.4.1] `localisation/english/modifiers_l_english.yml`

- Vanilla still sets them: `annex_cost_factor` 22 times in 12 files and `puppet_cost_factor` 21 times in 6 files (country leader traits, balance of power, dynamic modifiers, ideas). [vanilla-confirmed 1.19.4.1]
- `common/peace_conference/cost_modifiers/` is a separate system. Each entry has a `peace_action_type`, an `enable` trigger and a `cost_multiplier` greater than 0, and all active multipliers are multiplied together. [docs] `common/peace_conference/cost_modifiers/_documentation.md`
- No file in `common/peace_conference/` mentions either modifier name. Whether the two modifiers still change peace conference costs is not shown by the files. [vanilla-confirmed 1.19.4.1] [unverified]
<!-- kit:end id="annex-puppet-status" -->

#### Autonomy <a id="Autonomy"></a>

Autonomy-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| autonomy_gain | Daily gain of autonomy. | `autonomy_gain = 0.5` | Flat. | A positive number increase total autonomy, meaning the SUBJECT can be free faster. A negative number decrease total autonomy, meaning the OVERLORD can annex the manpower-slaves faster. | 1.3 |
| autonomy_gain_global_factor | Modifies all gain of autonomy by a subject. | `autonomy_gain_global_factor = 0.5` | Percentual. |  | 1.4 |
| subjects_autonomy_gain | Daily gain of autonomy in our subjects. | `subjects_autonomy_gain = 0.5` | Flat. |  | 1.3 |
| autonomy_gain_ll_to_overlord | Modifies gain of autonomy from lend-leasing to the overlord. | `autonomy_gain_ll_to_overlord = 0.5` | Flat. |  | 1.3 |
| autonomy_gain_ll_to_overlord_factor | Modifies gain of autonomy from lend-leasing to the overlord by a percentage. | `autonomy_gain_ll_to_overlord_factor = 0.5` | Percentual. |  | 1.3 |
| autonomy_gain_ll_to_subject | Modifies loss of autonomy from lend-leasing to the subject. | `autonomy_gain_ll_to_subject = 0.5` | Flat. |  | 1.3 |
| autonomy_gain_ll_to_subject_factor | Modifies loss of autonomy from lend-leasing to the subject by a percentage. | `autonomy_gain_ll_to_subject_factor = 0.5` | Percentual. |  | 1.3 |
| autonomy_gain_trade | Modifies gain of autonomy from the overlord trading with the subject. | `autonomy_gain_trade = 0.5` | Flat. |  | 1.3 |
| autonomy_gain_trade_factor | Modifies gain of autonomy from the overlord trading with the subject by a percentage. | `autonomy_gain_trade_factor = 0.5` | Percentual. |  | 1.3 |
| autonomy_gain_warscore | Modifies gain of autonomy from the subject gaining warscore. | `autonomy_gain_warscore = 0.5` | Flat. |  | 1.3 |
| autonomy_gain_warscore_factor | Modifies gain of autonomy from the subject gaining warscore by a percentage. | `autonomy_gain_warscore_factor = 0.5` | Percentual. |  | 1.3 |
| autonomy_manpower_share | Modifies the amount of manpower the overlord can use from the subject. | `autonomy_manpower_share = 0.5` | Percentual. |  | 1.3 |
| can_master_build_for_us | Makes the overlord be able to build in the subject. | `can_master_build_for_us = 1` | Boolean (only 1). |  | 1.3 |
| cic_to_overlord_factor | Modifies the amount of the subject's civilian industry that goes to the overlord. | `cic_to_overlord_factor = 0.3` | Percentual. |  | 1.3 |
| mic_to_overlord_factor | Modifies the amount of the subject's military industry that goes to the overlord. | `mic_to_overlord_factor = 0.3` | Percentual. |  | 1.3 |
| extra_trade_to_overlord_factor | Modifies the amount of the subject's resources that the overlord can receive via trade. | `extra_trade_to_overlord_factor = 0.3` | Percentual. |  | 1.3 |
| license_subject_master_purchase_cost | Modifies the cost of licensed production from the overlord. | `license_subject_master_purchase_cost = 0.3` | Percentual. |  | 1.4 |
| master_build_autonomy_factor | Modifies loss of autonomy from the overlord building in subject's states by a percentage. | `master_build_autonomy_factor = 0.3` | Percentual. |  | 1.3 |
| master_ideology_drift | Changes daily gain of the overlord's ideology in the country. | `master_ideology_drift = 0.03` | Flat. |  | 1.6 |
| overlord_trade_cost_factor | Modifies the cost of trade between the overlord and the subject in civilian factories. | `overlord_trade_cost_factor = -0.3` | Percentual. |  | 1.3 |

<!-- kit:begin id="add-aut" at="section:Autonomy" -->
**Kit addition** Documented modifiers this section does not list (2). Format and meaning columns are explained under [How the added tables read](#kit-added-tables-legend). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `autonomy_manpower_share_from_subjects` | autonomy | 2 dp | Amount of manpower demanded from subject forces |
| `resources_to_overlord_factor` | autonomy | 2 dp |  |
<!-- kit:end id="add-aut" -->

#### Governments in exile <a id="Governments_in_exile"></a>

Government-in-exile-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| dockyard_donations | Amount of dockyards donated. | `dockyard_donations = 2` | Flat. |  | 1.6 |
| industrial_factory_donations | Amount of civilian factories donated. | `industrial_factory_donations = 2` | Flat. |  | 1.6 |
| military_factory_donations | Amount of military factories donated. | `military_factory_donations = 2` | Flat. |  | 1.6 |
| exile_manpower_factor | Amount of manpower given to the host country. | `exile_manpower_factor = 0.5` | Percentual. |  | 1.6 |
| exiled_government_weekly_manpower | Amount of weekly manpower given to the host country. | `exiled_government_weekly_manpower = 100` | Percentual. |  | 1.11 |
| legitimacy_daily | Changes the amount of legitimacy gained daily. | `legitimacy_daily = 1` | Flat. |  | 1.6 |
| legitimacy_gain_factor | Changes the amount of legitimacy gained daily by a percentage. | `legitimacy_gain_factor = 1` | Percentual. |  | 1.9 |

#### Equipment <a id="Equipment"></a>

Equipment-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| equipment_capture | Changes the combat equipment capture ratio. | `equipment_capture = 0.2` | Flat. |  | 1.0 |
| equipment_capture_factor | Modifies the combat equipment capture ratio. | `equipment_capture_factor = 0.5` | Percentual. |  | 1.0 |
| equipment_conversion_speed | Changes the speed at which equipment is converted. | `equipment_conversion_speed = 0.5` | Percentual. |  | 1.0 |
| equipment_upgrade_xp_cost | Changes the experience cost to upgrade military equipment. | `equipment_upgrade_xp_cost = 0.5` | Percentual. |  | 1.0 |
| license_purchase_cost | Changes the cost of licensed equipment by a percentage. | `license_purchase_cost = 0.5` | Percentual. | Can be used as a targeted modifier. | 1.4 |
| license_purchase_cost_factor | Changes the cost of licensed equipment by a percentage. | `license_purchase_cost_factor = 0.5` | Percentual. | Allowed equipment types are anti_tank_eq, artillery_eq, infantry_eq, and light_tank_eq. Can be used as a targeted modifier. | 1.4 |
| license_purchase_cost_factor | Changes the cost of licensed equipment by a percentage. | `license_purchase_cost_factor = 0.5` | Percentual. | Allowed categories are air, armor, infantry, and naval. Can be used as a targeted modifier. | 1.4 |
| license_tech_difference_speed | Changes the production penalty of licensed equipment by tech difference by a percentage. | `license_tech_difference_speed = 0.5` | Percentual. | Also allows specifying category as license_<category>_tech_difference_speed_factor. Allowed categories are anti_tank_eq, artillery_eq, infantry_eq, and light_tank_eq. That's added in 1.6. Can be used as a targeted modifier. | 1.4 |
| license_production_speed | Changes the production speed of licensed equipment by a percentage. | `license_production_speed = 0.5` | Percentual. | Can be used as a targeted modifier. | 1.4 |
| license_<category>_production_speed_factor | Changes the production speed of licensed equipment by a percentage. | `license_infantry_eq_production_speed_factor = 0.5` | Percentual. | Allowed categories are anti_tank_eq, artillery_eq, infantry_eq, and light_tank_eq. Can be used as a targeted modifier. | 1.6 |
| production_cost_max_<ship type> | Modifies the maximum cost of the ship type. | `production_cost_max_ship_hull_light = 0.3` | Percentual. | Allowed ship types in base game: convoy, ship_hull_carrier, ship_hull_cruiser, ship_hull_heavy, ship_hull_light, ship_hull_submarine | 1.6 |
| production_factory_efficiency_gain_factor | Production efficiency growth. | `production_factory_efficiency_gain_factor = 0.5` | Percentual. |  | 1.0 |
| production_factory_max_efficiency_factor | Production efficiency cap. | `production_factory_max_efficiency_factor = 0.5` | Percentual. |  | 1.0 |
| production_factory_start_efficiency_factor | Production efficiency base. | `production_factory_start_efficiency_factor = 0.5` | Percentual. | These modifiers get added to the base value. So rather than a percent to the base value, they are to be understood as relative to full efficiency. | 1.0 |
| line_change_production_efficiency_factor | Production efficiency retention. | `line_change_production_efficiency_factor = 0.3` | Percentual. |  | 1.0 |
| production_lack_of_resource_penalty_factor | Lack of resources penalty. | `production_lack_of_resource_penalty_factor = 0.5` | Flat. |  | 1.0 |
| floating_harbor_duration | Modifies the duration of floating harbours. | `floating_harbor_duration = 2` | Flat. |  | 1.11 |
| floating_harbor_range | Modifies the range of floating harbours. | `floating_harbor_range = 2` | Flat. |  | 1.11 |
| floating_harbor_supply | Modifies the supply of floating harbours. | `floating_harbor_supply = 2` | Flat. |  | 1.11 |
| railway_gun_bombardment_factor | Modifies the bombardment of railway guns. | `railway_gun_bombardment_factor = 0.3` | Percentual. |  | 1.11 |

<!-- kit:begin id="add-eqp" at="section:Equipment" -->
**Kit addition** Documented modifiers this section does not list (15). Format and meaning columns are explained under [How the added tables read](#kit-added-tables-legend). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `license_air_purchase_cost` | country | 0 dp |  |
| `license_anti_tank_eq_cost_factor` | country | 0 dp |  |
| `license_anti_tank_eq_production_speed_factor` | country | 0 dp |  |
| `license_anti_tank_eq_tech_difference_speed_factor` | country | 0 dp |  |
| `license_armor_purchase_cost` | country | 0 dp |  |
| `license_artillery_eq_cost_factor` | country | 0 dp |  |
| `license_artillery_eq_production_speed_factor` | country | 0 dp |  |
| `license_artillery_eq_tech_difference_speed_factor` | country | 0 dp |  |
| `license_infantry_eq_cost_factor` | country | 0 dp |  |
| `license_infantry_eq_tech_difference_speed_factor` | country | 0 dp |  |
| `license_infantry_purchase_cost` | country | 0 dp |  |
| `license_light_tank_eq_cost_factor` | country | 0 dp |  |
| `license_light_tank_eq_production_speed_factor` | country | 0 dp |  |
| `license_light_tank_eq_tech_difference_speed_factor` | country | 0 dp |  |
| `license_naval_purchase_cost` | country | 0 dp |  |
<!-- kit:end id="add-eqp" -->

<!-- kit:begin id="license-cost-factor-removed" at="section:Equipment" -->
**Kit correction** The two `license_purchase_cost_factor` rows name a modifier that is not in 1.19.4.1. The name is absent from the modifier documentation [docs] `documentation/modifiers_documentation.md` and from all vanilla script and localisation [vanilla-confirmed 1.19.4.1]. A read-only search of `hoi4.exe` finds no string either. [unverified]

The documented names are `license_purchase_cost` (all licences), `license_air_purchase_cost`, `license_armor_purchase_cost`, `license_infantry_purchase_cost` and `license_naval_purchase_cost` (by category), and `license_<archetype>_eq_cost_factor`, `license_<archetype>_eq_production_speed_factor` and `license_<archetype>_eq_tech_difference_speed_factor` for `anti_tank`, `artillery`, `infantry` and `light_tank`. Production speed is `license_production_speed` and `license_tech_difference_speed`. [docs] `documentation/modifiers_documentation.md`
<!-- kit:end id="license-cost-factor-removed" -->

#### Fuel and supply <a id="Fuel_and_supply"></a>

Supply-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| base_fuel_gain | Changes base daily gain of fuel. | `base_fuel_gain = 100` | Flat. |  | 1.6 |
| base_fuel_gain_factor | Changes base daily gain of fuel by a percentage. | `base_fuel_gain_factor = 0.5` | Percentual. |  | 1.6 |
| fuel_cost | Changes hourly cost of fuel. | `fuel_cost = 100` | Flat. |  | 1.6 |
| fuel_gain | Changes daily gain of fuel from our controlled oil. | `fuel_gain = 100` | Flat. |  | 1.6 |
| fuel_gain_factor | Changes daily gain of fuel from our controlled oil by a percentage. | `fuel_gain_factor = 100` | Percentual. |  | 1.6 |
| fuel_gain_from_states | Changes daily gain of fuel. | `fuel_gain_from_states = 100` | Flat. | Refineries use this modifier. | 1.6 |
| fuel_gain_factor_from_states | Changes daily gain of fuel by a percentage. | `fuel_gain_factor_from_states = 0.5` | Percentual. | Modifies fuel gain from refineries. | 1.6 |
| max_fuel | Changes maximum amount of fuel you can have. | `max_fuel = 100` | Flat. |  | 1.6 |
| max_fuel_factor | Changes maximum amount of fuel you can have by a percentage. | `max_fuel_factor = 0.3` | Percentual. |  | 1.6 |
| army_fuel_capacity_factor | Modifies how much fuel a single unit can store before running out. | `army_fuel_capacity_factor = 0.3` | Percentual. |  | 1.6 |
| army_fuel_consumption_factor | Modifies the rate at which the army consumes fuel. | `army_fuel_consumption_factor = 0.3` | Percentual. |  | 1.6 |
| air_fuel_consumption_factor | Modifies the rate at which the airforce consumes fuel. | `air_fuel_consumption_factor = 0.5` | Percentual. |  | 1.6 |
| navy_fuel_consumption_factor | Modifies the rate at which the navy consumes fuel. | `navy_fuel_consumption_factor = 0.3` | Percentual. |  | 1.6 |
| supply_factor | Modifies the total amount of supply the military has. | `supply_factor = 0.3` | Percentual. |  | 1.11 |
| supply_combat_penalties_on_core_factor | Modifies the penalty given by low supply when the army is on a core state. | `supply_combat_penalties_on_core_factor = 0.3` | Percentual. |  | 1.11 |
| supply_consumption_factor | Modifies the rate at which army consumes supply. | `supply_consumption_factor = 0.3` | Percentual. |  | 1.0 |
| no_supply_grace | Modifies the grace period for units without supply. | `no_supply_grace = 120` | Flat. |  | 1.0 |
| out_of_supply_factor | Reduces the penalty that units take when they run out of supplies. | `out_of_supply_factor = 0.2` | Percentual. |  | 1.0 |
| attrition | Modifies the army's attrition. | `attrition = 0.3` | Percentual. | Can also be used in states or provinces. | 1.0 |
| unit_upkeep_attrition_factor | Modifies the unit upkeep. | `unit_upkeep_attrition_factor = 0.3` | Percentual. |  | 1.0 |
| naval_attrition | Modifies attrition suffered by naval units. | `naval_attrition = 0.3` | Percentual. |  | 1.6 |
| heat_attrition | Changes the attrition due to heat. | `heat_attrition = 0.5` | Flat. |  | 1.3 |
| heat_attrition_factor | Changes the attrition due to heat by a percentage. | `heat_attrition_factor = 0.5` | Percentual. |  | 1.3 |
| winter_attrition | Changes the attrition due to winter. | `winter_attrition = 0.5` | Flat. |  | 1.3 |
| winter_attrition_factor | Changes the attrition due to winter by a percentage. | `winter_attrition_factor = 0.5` | Percentual. |  | 1.3 |
| extra_marine_supply_grace | Changes the supply grace given to marines. | `extra_marine_supply_grace = 96` | Flat. |  | 1.0 |
| extra_paratrooper_supply_grace | Changes the supply grace given to paratroopers. | `extra_paratrooper_supply_grace = 96` | Flat. |  | 1.0 |
| special_forces_no_supply_grace | Changes the supply grace period for special forces. | `special_forces_no_supply_grace = 120` | Flat. |  | 1.0 |
| special_forces_out_of_supply_factor | Changes the penalty for special forces out of supply. | `special_forces_out_of_supply_factor = 0.3` | Percentual. |  | 1.0 |
| truck_attrition | Changes the attrition supply trucks suffer from. | `truck_attrition = 3` | Flat. |  | 1.11 |
| truck_attrition_factor | Modifies the attrition supply trucks suffer from. | `truck_attrition_factor = 0.3` | Percentual. |  | 1.11 |

<!-- kit:begin id="add-fuel" at="section:Fuel_and_supply" -->
**Kit addition** Documented modifiers this section does not list (3). Format and meaning columns are explained under [How the added tables read](#kit-added-tables-legend). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `naval_supply_consumption_factor` | naval, defensive, aggressive | 1 dp | Supplies our fleets need to operate |
| `underway_replenishment_convoy_cost` | country | 2 dp | Convoys used to provide underway replenishment |
| `underway_replenishment_range` | country | 2 dp | How far underway replenishment extends fleet range |
<!-- kit:end id="add-fuel" -->

#### Buildings <a id="Buildings"></a>

Building-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| production_speed_buildings_factor | Changes the construction speed of all buildings. | `production_speed_buildings_factor = 0.5` | Percentual. |  | 1.0 |
| production_speed_<building>_factor | Changes the construction speed of a specific building. | `production_speed_industrial_complex_factor = 0.5` | Percentual. |  | 1.0 |
| production_cost_<building>_factor | Changes the base cost of a specific building. | `production_cost_industrial_complex_factor = -0.1` | Percentual. | Localization is missing and must be added yourself. | Unknown |
| civilian_factory_use | Uses the specified amount of civilian factory as a special project. | `civilian_factory_use = 3` | Flat. |  | 1.5 |
| consumer_goods_factor | Modifies the percentage of factories used for consumer goods. | `consumer_goods_factor = 0.1` | Multiplicative. | The modifier adds multiplicatively. For example, `consumer_goods_factor = 0.5` and `consumer_goods_factor = -0.5` will, in total, multiply the consumer goods value by `(1-0.5)(1+0.5)=0.5\cdot 1.5=0.75`. | 1.0 |
| consumer_goods_expected_value | Sets the baseline percentage of expected consumer goods. | `consumer_goods_expected_value = 0.1` | Flat. | Used to be only updated when the economic law was changed. Now gets updated normaly. | 1.13 |
| conversion_cost_civ_to_mil_factor | Changes the cost to convert civilian factories to military factories. | `conversion_cost_civ_to_mil_factor = 0.4` | Percentual. |  | 1.5 |
| conversion_cost_mil_to_civ_factor | Changes the cost to convert military factories to civilian factories. | `conversion_cost_mil_to_civ_factor = 0.4` | Percentual. |  | 1.5 |
| global_building_slots | Changes amount of building slots in our every state. | `global_building_slots = 1` | Flat. |  | 1.0 |
| global_building_slots_factor | Changes amount of building slots in our every state by a percentage. | `global_building_slots_factor = 0.3` | Percentual. |  | 1.0 |
| industrial_capacity_dockyard | Dockyard output. | `industrial_capacity_dockyard = 0.3` | Percentual. |  | 1.3.3 |
| industrial_capacity_factory | Military factory output. | `industrial_capacity_factory = 0.3` | Percentual. |  | 1.0 |
| industry_air_damage_factor | Amount of damage our factories receive from air bombings. | `industry_air_damage_factor = 0.3` | Percentual. |  | 1.0 |
| industry_free_repair_factor | Changes the speed at which buildings repair themselves without factories assigned. | `industry_free_repair_factor = 0.3` | Percentual. |  | 1.0 |
| industry_repair_factor | Changes the speed at which buildings are repaired. | `industry_repair_factor = 0.3` | Percentual. |  | 1.0 |
| production_oil_factor | Synthetic oil gain. | `production_oil_factor = 0.5` | Percentual. |  | 1.0 |
| repair_speed_<building>_factor | Changes the repair speed of a specific building. | `repair_speed_arms_factory_factor = 0.5` | Percentual. |  | 1.0 |
| supply_node_range | Increases the effective range of supply nodes. | `supply_node_range = 0.1` | Percentual. |  | 1.11 |
| static_anti_air_damage_factor | Modifies the damage done to planes by the anti-air buildings. | `static_anti_air_damage_factor = 0.1` | Percentual. |  | 1.0 |
| static_anti_air_hit_chance_factor | Modifies the chance for the anti-air buildings to hit enemy planes. | `static_anti_air_hit_chance_factor = 0.1` | Percentual. |  | 1.0 |
| tech_air_damage_factor | Modifies the damage done to the country's planes by enemy anti-air buildings. | `tech_air_damage_factor = 0.1` | Percentual. |  | 1.0 |
| tech_air_damage_factor | Modifies the damage done to the country's planes by enemy anti-air buildings. | `tech_air_damage_factor = 0.1` | Percentual. |  | 1.0 |
| cic_construction_boost | Modifies the base construction speed from civilian factories. | `cic_construction_boost = 0.1` | Flat. |  | 1.13 |
| cic_construction_boost_factor | Modifies the modifier to the base construction speed from civilian factories. | `cic_construction_boost_factor = 0.1` | Percentual. |  | 1.13 |
| land_bunker_effectiveness_factor | Modifies the effectiveness of land forts in defence. | `land_bunker_effectiveness_factor = 0.1` | Percentual. |  | 1.13 |
| coastal_bunker_effectiveness_factor | Modifies the effectiveness of coastal forts in defence. | `coastal_bunker_effectiveness_factor = 0.1` | Percentual. |  | 1.13 |

<!-- kit:begin id="add-bld" at="section:Buildings" -->
**Kit addition** Documented modifiers this section does not list (5). Format and meaning columns are explained under [How the added tables read](#kit-added-tables-legend). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `industrial_capacity_dockyard_powered` | country, war_production | 2 dp | Output of powered dockyards |
| `industrial_capacity_factory_powered` | country, war_production | 2 dp | Output of powered factories |
| `out_of_power_impact_factor` | country, war_production | 2 dp | Reduces the penalties from lack of power |
| `production_speed_buildings_powered_factor` | country, war_production | 2 dp | Construction speed of powered buildings (unused in vanilla) |
| `production_speed_facility_factor` | country | 2 dp | Construction speed of all facilities |
<!-- kit:end id="add-bld" -->

#### Resistance and compliance <a id="Resistance_and_compliance"></a>

Resistance-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| compliance_growth_on_our_occupied_states | Changes the compliance growth speed on the country's controlled states. | `compliance_growth_on_our_occupied_states = 0.5` | Percentual. |  | 1.9 |
| no_compliance_gain | Disables the compliance gain on our controlled states. | `no_compliance_gain = 1` | Boolean (only 1). | Can also be used in state scope. | 1.9 |
| required_garrison_factor | Changes the required garrison in our occupied states. | `required_garrison_factor = 0.5` | Percentual. | Can also be used in state scope. | 1.9 |
| resistance_activity | Changes the chance for resistance activity to occur on our occupied states. | `resistance_activity = 0.5` | Percentual. |  | 1.9 |
| resistance_damage_to_garrison_on_our_occupied_states | Changes the resistance damage to the garrison in our occupied states. | `resistance_damage_to_garrison_on_our_occupied_states = 0.5` | Percentual. |  | 1.9 |
| resistance_decay_on_our_occupied_states | Changes the resistance decay in our occupied states. | `resistance_decay_on_our_occupied_states = 0.5` | Percentual. |  | 1.9 |
| resistance_growth_on_our_occupied_states | Changes the resistance growth speed in our occupied states. | `resistance_growth_on_our_occupied_states = 0.5` | Percentual. |  | 1.9 |
| resistance_target_on_our_occupied_states | Changes the resistance target in our occupied states. | `resistance_target_on_our_occupied_states = 0.5` | Percentual. |  | 1.9 |
| resistance_target | Changes the resistance target in foreign states occupied by us | `resistance_target = 0.5` | Percentual |  | 1.9 |

#### Intelligence <a id="Intelligence"></a>

Intelligence-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| agency_upgrade_time | Changes the time it takes to upgrade the agency | `agency_upgrade_time = 0.5` | Percentual. |  | 1.9 |
| decryption | Changes the decription capability of the country. | `decryption = 1` | Flat. | Only works with the ![La Résistance](media/ai_modding_04cfcba22e__img6.png)La Résistance DLC disabled. | 1.0 |
| decryption_factor | Changes the decription capability of the country by a percentage. | `decryption_factor = 0.5` | Percentual. | Only works with the ![La Résistance](media/ai_modding_04cfcba22e__img6.png)La Résistance DLC disabled. | 1.0 |
| encryption | Changes the encryption capability of the country. | `encryption = 1` | Flat. | Only works with the ![La Résistance](media/ai_modding_04cfcba22e__img6.png)La Résistance DLC disabled. | 1.0 |
| encryption_factor | Changes the encryption capability of the country by a percentage. | `encryption_factor = 0.5` | Percentual. | Only works with the ![La Résistance](media/ai_modding_04cfcba22e__img6.png)La Résistance DLC disabled. | 1.0 |
| <type>_intel_decryption_bonus | Adds a cipher bonus to the specified intel. | `civilian_intel_decryption_bonus = 0.5` | Percentual. | Types are: airforce, army, civilian, navy. | 1.9 |
| <type>_intel_factor | Modifies the intelligence you receive of the specified type. | `navy_intel_factor = 0.5` | Percentual. | Types are: airforce, army, civilian, navy. | 1.9 |
| <type>_intel_to_others | Changes the amount of intel other countries will receive of the specified type. | `civilian_intel_to_others = 0.5` | Percentual. | Types are: airforce, army, civilian, navy. | 1.9 |
| female_random_operative_chance | Changes the chance for a randomly-generated operative to be female. | `female_random_operative_chance = 0.3` | Percentual. |  | 1.9.1 |
| foreign_subversive_activites | Changes efficiency of foreign subversive activities. | `foreign_subversive_activites = 0.3` | Percentual. |  | 1.9 |
| intel_network_gain | Changes gain of intel network strength. | `intel_network_gain = 1` | Flat. | Can also be used in state scope. | 1.9 |
| intel_network_gain_factor | Changes gain of intel network strength by a percentage. | `intel_network_gain_factor = 0.5` | Percentual. | Can also be used in state scope. | 1.9 |
| subversive_activites_upkeep | Changes the cost of subversive activities. | `subversive_activites_upkeep = 0.5` | Percentual. |  | 1.0 |
| operation_cost | Changes the cost of operations. | `operation_cost = 0.5` | Percentual. | Dynamically created by operations with the `cost_modifiers = { ... }` block. This one is used by each base game operation to modify the operation cost. | 1.9 |
| operation_outcome | Changes the efficiency of operations. | `operation_outcome = 0.5` | Percentual. | Dynamically created by operations with the `outcome_modifiers = { ... }` block. This one is used by each base game operation to modify the operation's outcome chance. | 1.9 |
| operation_risk | Changes the risk of operations. | `operation_risk = 0.5` | Percentual. | Dynamically created by operations with the `risk_modifiers = { ... }` block. This one is used by each base game operation to modify the operation risk. | 1.9 |
| <operation>_cost | Changes the cost of the specified operation. | `operation_infiltrate_cost = 0.5` | Percentual. | Operations are defined in `/Hearts of Iron IV/common/operations/*.txt`. Dynamically created by operations with the `cost_modifiers = { ... }` block. | 1.9 |
| <operation>_outcome | Changes the efficiency of the specified operation. | `operation_coup_government_outcome = 0.5` | Percentual. | Operations are defined in `/Hearts of Iron IV/common/operations/*.txt`. Dynamically created by operations with the `outcome_modifiers = { ... }` block. Note that target_sabotage uses target_sabotage_factor rather than target_sabotage_outcome. | 1.9 |
| <operation>_risk | Changes the risk of the specified operation. | `operation_make_resistance_contacts_risk = 0.5` | Percentual. | Operations are defined in `/Hearts of Iron IV/common/operations/*.txt`. Dynamically created by operations with the `risk_modifiers = { ... }` block. | 1.9 |
| <mission>_factor | Modifies the effect of the specified mission. | `boost_ideology_mission_factor = 0.5` | Percentual. | Types are: boost_ideology_mission, boost_resistance, control_trade_mission, diplomatic_pressure_mission, propaganda_mission, root_out_resistance_effectiveness. | 1.9 |
| commando_trait_chance_factor | Modifies the chance for an operative to get the commando trait when hired. | `commando_trait_chance_factor = 0.5` | Percentual. |  | 1.9 |
| crypto_department_enabled | Enables the crypto department. | `crypto_department_enabled = 1` | Boolean (only 1). |  | 1.9 |
| crypto_strength | Modifies the cryptology level. | `crypto_strength = 1` | Flat. | ![La Résistance](media/ai_modding_04cfcba22e__img6.png)La Résistance DLC enabled. | 1.9 |
| decryption_power | Modifies the decryption power. | `decryption_power = 1` | Flat. | ![La Résistance](media/ai_modding_04cfcba22e__img6.png)La Résistance DLC enabled. | 1.9 |
| decryption_power_factor | Modifies the decryption power by a percentage. | `decryption_power_factor = 0.3` | Percentual. | ![La Résistance](media/ai_modding_04cfcba22e__img6.png)La Résistance DLC enabled. | 1.9 |
| defense_impact_on_blueprint_stealing | Modifies the impact of enemy defense on the blueprint stealing operation. | `defense_impact_on_blueprint_stealing = 0.3` | Percentual. |  | 1.9 |
| intel_from_combat_factor | Modifies the intelligence gained from combat. | `intel_from_combat_factor = 0.3` | Percentual. |  | 1.9 |
| intel_from_operatives_factor | Modifies the intelligence gained from operatives and infiltrated assets. | `intel_from_operatives_factor = 0.3` | Percentual. |  | 1.9 |
| intel_network_gain | Modifies the intelligence network gain. | `intel_network_gain = 0.3` | Flat. |  | 1.9 |
| intel_network_gain_factor | Modifies the intelligence network gain by a percentage. | `intel_network_gain_factor = 0.3` | Percentual. |  | 1.9 |
| intelligence_agency_defense | Modifies the counter intelligence. | `intelligence_agency_defense = 0.3` | Flat. |  | 1.9 |
| root_out_resistance_effectiveness_factor | Modifies the effectiveness of rooting out resistance. | `root_out_resistance_effectiveness_factor = 0.3` | Percentual. |  | 1.9 |

<!-- kit:begin id="add-int" at="section:Intelligence" -->
**Kit addition** Documented modifiers this section does not list (15). Format and meaning columns are explained under [How the added tables read](#kit-added-tables-legend). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `airforce_intel_decryption_bonus` | intelligence_agency | 0 dp | ~ Extra air intel once an enemy cipher is decrypted (used in passive_decryption_modifier and active_decryption_modifier) |
| `airforce_intel_factor` | intelligence_agency | 0 dp | ~ Scales the agency's air force intelligence |
| `airforce_intel_to_others` | country | 1 dp | ~ Air force intel other countries get about us (negative hides us) |
| `army_intel_decryption_bonus` | intelligence_agency | 0 dp | ~ Extra army intel once an enemy cipher is decrypted (used in passive_decryption_modifier and active_decryption_modifier) |
| `army_intel_factor` | intelligence_agency | 0 dp | ~ Scales the agency's army intelligence |
| `army_intel_to_others` | country | 1 dp | ~ Army intel other countries get about us (negative hides us) |
| `boost_resistance_factor` | intelligence_agency | 0 dp | Strengthen Resistance mission efficiency |
| `civilian_intel_factor` | intelligence_agency | 0 dp | ~ Scales the agency's civilian intelligence |
| `control_trade_mission_factor` | intelligence_agency | 0 dp | Control Trade mission effects |
| `diplomatic_pressure_mission_factor` | intelligence_agency | 0 dp | Diplomatic Pressure mission effects |
| `intelligence_operation_speed` | intelligence_agency | 0 dp | Operation speed factor (unused in vanilla) |
| `navy_intel_decryption_bonus` | intelligence_agency | 0 dp | ~ Extra navy intel once an enemy cipher is decrypted (used in passive_decryption_modifier and active_decryption_modifier) |
| `navy_intel_to_others` | country | 1 dp | ~ Navy intel other countries get about us (negative hides us) |
| `operation_infiltrate_outcome` | intelligence_agency | 0 dp | Infiltration operation effectiveness (defined in modifier_definitions) |
| `propaganda_mission_factor` | intelligence_agency | 0 dp | Propaganda mission effects |
<!-- kit:end id="add-int" -->

#### Operatives <a id="Operatives"></a>

These can be used in both the country scope and operative scope, such as traits, unless specified otherwise.

Operative-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| own_operative_capture_chance_factor | Changes the chance for our operatives to be captured. | `own_operative_capture_chance_factor = 0.5` | Percentual. |  | 1.9 |
| own_operative_detection_chance | Changes the chance for our operatives to be detected. | `own_operative_detection_chance = 10` | Flat. |  | 1.9 |
| own_operative_detection_chance_factor | Changes the chance for our operatives to be detected by a percentage. | `own_operative_detection_chance_factor = 0.5` | Percentual. |  | 1.9 |
| own_operative_forced_into_hiding_time_factor | Changes the chance for our operatives to be forced into hiding by a percentage. | `own_operative_forced_into_hiding_time_factor = 0.5` | Percentual. |  | 1.9 |
| own_operative_harmed_time_factor | Changes the chance for our operatives to be harmed by a percentage. | `own_operative_harmed_time_factor = 0.5` | Percentual. |  | 1.9 |
| own_operative_intel_extraction_rate | Changes the rate at which our operatives extract enemy intel. | `own_operative_intel_extraction_rate = 0.5` | Percentual. |  | 1.9 |
| enemy_operative_capture_chance_factor | Changes the chance for an enemy operative to be captured. | `enemy_operative_capture_chance_factor = 0.5` | Percentual. |  | 1.9 |
| enemy_operative_detection_chance | Changes the chance for an enemy operative to be detected. | `enemy_operative_detection_chance = 10` | Flat. |  | 1.9 |
| enemy_operative_detection_chance_factor | Changes the chance for an enemy operative to be detected by a percentage. | `enemy_operative_detection_chance_factor = 0.5` | Percentual. |  | 1.9 |
| enemy_operative_forced_into_hiding_time_factor | Changes the chance for an enemy operative to be forced into hiding by a percentage. | `enemy_operative_forced_into_hiding_time_factor = 0.5` | Percentual. |  | 1.9 |
| enemy_operative_harmed_time_factor | Changes the chance for an enemy operative to be harmed by a percentage. | `enemy_operative_harmed_time_factor = 0.5` | Percentual. |  | 1.9 |
| enemy_operative_intel_extraction_rate | Changes the rate at which the enemy operatives extract our intel. | `enemy_operative_intel_extraction_rate = 0.5` | Percentual. |  | 1.9 |
| enemy_spy_negative_status_factor | Changes the chance an enemy spy can receive a negative status. | `enemy_spy_negative_status_factor = 0.5` | Percentual. |  | 1.9 |
| enemy_operative_recruitment_chance | Modifies the chance to recruit an enemy operative. | `enemy_operative_recruitment_chance = 0.3` | Percentual. | Cannot be used in operative scope. | 1.9 |
| new_operative_slot_bonus | Modifies the operative recruitment choices. | `new_operative_slot_bonus = 1` | Flat. | Cannot be used in operative scope. | 1.9 |
| occupied_operative_recruitment_chance | Modifies the chance to get an operative from occupied territory. | `occupied_operative_recruitment_chance = 0.3` | Percentual. | Cannot be used in operative scope. | 1.9 |
| operative_death_on_capture_chance | Modifies the chance for the country's operative to die on being captured. | `operative_death_on_capture_chance = 0.3` | Percentual. | Cannot be used in operative scope. | 1.9 |
| operative_slot | Modifies the amount of operative slots. | `operative_slot = 1` | Flat. | Cannot be used in operative scope. | 1.9 |

#### AI <a id="AI"></a>

AI-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| ai_badass_factor | AI's threat perception. | `ai_badass_factor = 0.5` | Percentual. |  | 1.0 |
| ai_call_ally_desire_factor | Chance for AI to call allies. | `ai_call_ally_desire_factor = 0.5` | Percentual. |  | 1.0 |
| ai_desired_divisions_factor | The amount of divisions AI seeks to produce. | `ai_desired_divisions_factor = 0.5` | Percentual. |  | 1.0 |
| ai_focus_aggressive_factor | AI's focus on offense. | `ai_focus_aggressive_factor = 0.5` | Percentual. |  | 1.0 |
| ai_focus_defense_factor | AI's focus on defense. | `ai_focus_defense_factor = 0.5` | Percentual. |  | 1.0 |
| ai_focus_aviation_factor | AI's focus on aviation. | `ai_focus_aviation_factor = 0.5` | Percentual. |  | 1.0 |
| ai_focus_military_advancements_factor | AI's focus on advanced military technologies. | `ai_focus_military_advancements_factor = 0.5` | Percentual. |  | 1.0 |
| ai_focus_military_equipment_factor | AI's focus on advanced military equipment. | `ai_focus_military_equipment_factor = 0.5` | Percentual. |  | 1.0 |
| ai_focus_naval_air_factor | AI's focus on building naval airforce. | `ai_focus_naval_air_factor = 0.5` | Percentual. |  | 1.0 |
| ai_focus_naval_factor | AI's focus on building a navy. | `ai_focus_naval_factor = 0.5` | Percentual. |  | 1.0 |
| ai_focus_peaceful_factor | AI's focus on peaceful research and policies. | `ai_focus_peaceful_factor = 0.5` | Percentual. |  | 1.0 |
| ai_focus_war_production_factor | AI's focus on wartime production. | `ai_focus_war_production_factor = 0.5` | Percentual. |  | 1.0 |
| ai_get_ally_desire_factor | AI's desire to be in or expand a faction. | `ai_get_ally_desire_factor = 0.5` | Percentual. |  | 1.0 |
| ai_join_ally_desire_factor | AI's desire to join the wars led by allies. | `ai_join_ally_desire_factor = 0.5` | Percentual. |  | 1.0 |
| ai_license_acceptance | AI's chance to agree licensing equipment. | `ai_license_acceptance = 0.5` | Percentual. | Can be used as a targeted modifier. | 1.4 |

#### Military outside of combat <a id="Military_outside_of_combat"></a>

Military-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| command_power_gain | Changes the daily gain of command power. | `command_power_gain = 0.5` | Flat. |  | 1.5 |
| command_power_gain_mult | Changes the daily gain of command power by a percentage. | `command_power_gain_mult = 0.5` | Percentual. |  | 1.5 |
| conscription | Changes the recruitable percentage of the total population. | `conscription = 0.02` | Flat. |  | 1.0 |
| conscription_factor | Changes the recruitable percentage of the total population by a percent. | `conscription_factor = 0.3` | Percentual. |  | 1.0 |
| experience_gain_army | Modifies the daily gain of army experience. | `experience_gain_army = 0.5` | Flat. |  | 1.0 |
| experience_gain_army_factor | Modifies the gain of army experience by a percentage. | `experience_gain_army_factor = 0.5` | Percentual. |  | 1.0 |
| experience_gain_navy | Modifies the daily gain of naval experience. | `experience_gain_navy = 0.02` | Flat. |  | 1.0 |
| experience_gain_navy_factor | Modifies the gain of naval experience by a percentage. | `experience_gain_navy_factor = 0.3` | Percentual. |  | 1.0 |
| experience_gain_air | Modifies the daily gain of air experience. | `experience_gain_air = 0.05` | Flat. |  | 1.0 |
| experience_gain_air_factor | Modifies the daily gain of air experience by a percentage. | `experience_gain_air_factor = 0.5` | Percentual. |  | 1.0 |
| land_equipment_upgrade_xp_cost | Changes the experience cost to upgrade land army equipment. | `land_equipment_upgrade_xp_cost = 0.3` | Percentual. |  | 1.0 |
| land_reinforce_rate | Changes the rate at which reinforcements to divisions arrive. | `land_reinforce_rate = 0.3` | Percentual. |  | 1.0 |
| max_command_power | Changes maximum command power. | `max_command_power = 20` | Flat. |  | 1.5 |
| max_command_power_mult | Changes maximum command power by a percentage. | `max_command_power_mult = 0.3` | Percentual. |  | 1.5 |
| weekly_manpower | Amount of manpower gained each week. | `weekly_manpower = 1000` | Flat. |  | 1.6 |
| naval_equipment_upgrade_xp_cost | Changes the naval experience cost to upgrade equipment. | `naval_equipment_upgrade_xp_cost = 0.3` | Percentual. |  | 1.0 |
| refit_ic_cost | The IC cost to refit naval equipment. | `refit_ic_cost = 20` | Flat. |  | 1.6 |
| refit_speed | The speed at which naval equipment is refitted. | `refit_speed = 0.5` | Percentual. |  | 1.6 |
| air_equipment_upgrade_xp_cost | Changes the air experience cost to upgrade equipment. | `air_equipment_upgrade_xp_cost = 0.5` | Percentual. |  | 1.0 |
| training_time_factor | Modifies the training time for both army and navy. | `training_time_factor = 0.3` | Percentual. |  | 1.0 |
| minimum_training_level | Changes training level necessary for the unit to deploy. | `minimum_training_level = 0.3` | Percentual. |  | 1.0 |
| max_training | Modifies the required experience to achieve full training. | `max_training = -0.3` | Percentual. |  | 1.0 |
| training_time_army_factor | Modifies the training time for the army. | `training_time_army_factor = 0.3` | Percentual. |  | 1.0 |
| special_forces_training_time_factor | Changes the time it takes to train special forces. | `special_forces_training_time_factor = 0.3` | Percentual. |  | 1.0 |
| <land/air/naval>_doctrine_cost_factor | Changes the cost of buying a new doctrine of the specified type. | `land_doctrine_cost_factor = -0.05` | Percentual. |  | 1.11 |
| <doctrine category>_cost_factor | Modifies the cost of buying a new doctrine of the specified category. | `cat_mobile_warfare_cost_factor = 0.3` | Percentual. | Doctrines are defined in `/Hearts of Iron IV/common/technologies/*.txt`. | 1.11 |
| <land/air/naval>_mastery_gain_factor | Modifies the speed at which mastery in a given doctrine folder is gained. | `land_mastery_gain_factor = 0.15` | Percentual. | Doctrine tracks are defined in `/Hearts of Iron IV/common/doctrines/folders`. |  |
| <doctrine track>_track_mastery_gain_factor | Modifies the speed at which mastery of a given track is gained. | `operations_track_mastery_gain_factor = 0.1` | Percentual. | Doctrine tracks are defined in `/Hearts of Iron IV/common/doctrines/tracks`. currently existing tracks are Army: `infantry`,`combat_support`,`armor`and`operations`  Air: `fighter_aircraft`,`strike_aircraft`,`medium_aircraft`and`heavy_aircraft`  Navy: `capital_ships`,`carriers`,`screens`and`submarines` | 1.17 |
| choose_preferred_tactics_cost | Changes the cost to choose a preferred tactic. | `choose_preferred_tactics_cost = 5` | Flat. |  | 1.11 |
| command_abilities_cost_factor | Changes the cost to choose a command ability. | `command_abilities_cost_factor = -0.3` | Percentual. |  | 1.11 |
| transport_capacity | Modifies how many convoys units require to be transported over sea. | `transport_capacity = 0.3` | Percentual. |  | 1.0 |
| paratroopers_special_forces_contribution_factor | Modifies how much paratroopers contribute to the limit of special forces on a template. | `paratroopers_special_forces_contribution_factor = 0.3` | Percentual. |  | 1.13 |
| marines_special_forces_contribution_factor | Modifies how much marines contribute to the limit of special forces on a template. | `marines_special_forces_contribution_factor = 0.3` | Percentual. |  | 1.13 |
| mountaineers_special_forces_contribution_factor | Modifies how much mountaineers contribute to the limit of special forces on a template. | `mountaineers_special_forces_contribution_factor = 0.3` | Percentual. |  | 1.13 |
| rangers_special_forces_contribution_factor | Modifies how much rangers contribute to the limit of special forces on a template. | `rangers_special_forces_contribution_factor = 0.3` | Percentual. |  | 1.17 |
| special_forces_cap_flat | Modifies how many special forces sub-units can be put into a single template. | `special_forces_cap_flat = 10` | Percentual. |  | 1.13 |
| additional_brigade_column_size | Changes the amount of maximum unlocked slots on each brigade column in division templates. | `additional_brigade_column_size = 1` | Flat. |  | 1.13 |
| unit_<unit type>_design_cost_factor | Modifies how much experience it costs to add a brigade of the specified type to a template. | `unit_artillery_brigade_design_cost_factor = 0.3` | Percentual. | Brigades are defined in `/Hearts of Iron IV/common/units/*.txt` | 1.11 |
| <equipment archetype>_design_cost_factor | Modifies how much experience it costs to add upgrades or modules to a specified equipment archetype. | `strat_bomber_equipment_design_cost_factor = 0.3``ship_hull_heavy_design_cost_factor = -0.2` | Percentual. | Equipment archetypes are defined in `/Hearts of Iron IV/common/units/equipment/*.txt` | 1.11 |
| module_<module type>_design_cost_factor | Modifies how much experience it costs to add a module of the specified type to equipment. | `module_tank_torsion_bar_suspension_design_cost_factor = 0.3` | Percentual. | Modules are defined in `/Hearts of Iron IV/common/units/equipment/modules/*.txt` | 1.11 |

<!-- kit:begin id="add-mil" at="section:Military_outside_of_combat" -->
**Kit addition** Documented modifiers this section does not list (5). Format and meaning columns are explained under [How the added tables read](#kit-added-tables-legend). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `air_doctrine_cost_factor` | country | 2 dp |  |
| `army_experience_from_volunteers` | army | 1 dp |  |
| `naval_doctrine_cost_factor` | country | 2 dp |  |
| `special_forces_doctrine_cost_factor` | country | 2 dp |  |
| `training_time_army` | army, war_production | 1 dp | Division training time (unused in vanilla) |
<!-- kit:end id="add-mil" -->

#### MIOs <a id="MIOs"></a>

These are modifiers related to military industrial organisations.

MIO-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| military_industrial_organization_research_bonus | Modifies the research bonus granted by MIOs. | `military_industrial_organization_research_bonus = 0.3` | Percentual. |  | 1.13 |
| military_industrial_organization_design_team_assign_cost | Modifies the political power cost to assign a design team. | `military_industrial_organization_design_team_assign_cost = 30` | Flat. |  | 1.13 |
| military_industrial_organization_design_team_change_cost | Modifies the political power cost to change a design team. | `military_industrial_organization_design_team_change_cost = 20` | Flat. |  | 1.13 |
| military_industrial_organization_industrial_manufacturer_assign_cost | Modifies the political power cost to assign an industrial manufacturer. | `military_industrial_organization_industrial_manufacturer_assign_cost = 10` | Flat. |  | 1.13 |
| military_industrial_organization_task_capacity | Modifies the amount of tasks possible to assign to the MIO. | `military_industrial_organization_task_capacity = 2` | Flat. |  | 1.13 |
| military_industrial_organization_size_up_requirement | Modifies the requirement to size up a MIO. | `military_industrial_organization_size_up_requirement = 2` | Flat. |  | 1.13 |
| military_industrial_organization_funds_gain | Modifies the amount of funds gained by the MIO. | `military_industrial_organization_funds_gain = 0.3` | Percentual. |  | 1.13 |
| military_industrial_organization_policy_cost | Modifies the political power cost to assign a MIO policy. | `military_industrial_organization_policy_cost = 20` | Flat. |  | 1.13 |
| military_industrial_organization_policy_cooldown | Modifies the cooldown between how often it's possible to change policies. | `military_industrial_organization_policy_cooldown = 5` | Flat. |  | 1.13 |

#### Unit leaders <a id="Unit_leaders"></a>

These are modifiers related to unit leaders in the country scope, rather than being in the unit leader scope.

Unit leader-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| female_random_army_leader_chance | Changes the chance for a randomly-generated army leader to be female. | `female_random_army_leader_chance = 0.3` | Percentual. |  | 1.9.1 |
| assign_army_leader_cp_cost | Modifies the cost to assign an army leader to an army. | `assign_army_leader_cp_cost = -5` | Flat. |  | 1.11 |
| army_leader_cost_factor | The cost in political power to recruit an unit leader for the land army. | `army_leader_cost_factor = 0.5` | Percentual. |  | 1.3 |
| army_leader_start_level | Bonus to the starting level of generic unit leaders. | `army_leader_start_level = 1` | Flat. |  | 1.5 |
| army_leader_start_attack_level | Bonus to the starting level of attack in generic unit leaders. | `army_leader_start_attack_level = 1` | Flat. |  | 1.5 |
| army_leader_start_defense_level | Bonus to the starting level of defense in generic unit leaders. | `army_leader_start_defense_level = 1` | Flat. |  | 1.5 |
| army_leader_start_logistics_level | Bonus to the starting level of logistics in generic unit leaders. | `army_leader_start_logistics_level = 1` | Flat. |  | 1.5 |
| army_leader_start_planning_level | Bonus to the starting level of planning in generic unit leaders. | `army_leader_start_planning_level = 1` | Flat. |  | 1.5 |
| military_leader_cost_factor | The cost in political power to recruit an unit leader. | `military_leader_cost_factor = 0.5` | Percentual. |  | 1.3 |
| female_random_admiral_chance | Changes the chance for a randomly-generated admiral to be female. | `female_random_admiral_chance = 0.3` | Percentual. |  | 1.9.1 |
| assign_navy_leader_cp_cost | Modifies the cost to assign a navy leader to a navy. | `assign_navy_leader_cp_cost = -5` | Flat. |  | 1.11 |
| navy_leader_cost_factor | The cost in political power to recruit an unit leader for the land navy. | `navy_leader_cost_factor = 0.5` | Percentual. |  | 1.3 |
| navy_leader_start_level | Bonus to the starting level of generic unit leaders. | `navy_leader_start_level = 1` | Flat. |  | 1.9 |
| navy_leader_start_attack_level | Bonus to the starting level of attack in generic unit leaders. | `navy_leader_start_attack_level = 1` | Flat. |  | 1.9 |
| navy_leader_start_coordination_level | Bonus to the starting level of coordination in generic unit leaders. | `navy_leader_start_coordination_level = 1` | Flat. |  | 1.9 |
| navy_leader_start_defense_level | Bonus to the starting level of defense in generic unit leaders. | `navy_leader_start_defense_level = 1` | Flat. |  | 1.9 |
| navy_leader_start_maneuvering_level | Bonus to the starting level of maneuvering in generic unit leaders. | `navy_leader_start_maneuvering_level = 1` | Flat. |  | 1.9 |
| grant_medal_cost_factor | Changes the cost in command power to grant a medal to a division commander. | `grant_medal_cost_factor = 0.2` | Percentual. |  | 1.12 |
| field_officer_promotion_penalty | Changes the experience penalty applied to the divisions when a commander is promoted to a field marshal. | `field_officer_promotion_penalty = 0.2` | Percentual. |  | 1.12 |
| female_divisional_commander_chance | Changes the chance to get a female divisional commander. | `female_divisional_commander_chance = 0.2` | Flat. | If no generic female portraits are defined within `/Hearts of Iron IV/portraits/*.txt` files, there will be a silhouette. | 1.12 |

<!-- kit:begin id="add-ldr" at="section:Unit_leaders" -->
**Kit addition** Documented modifiers this section does not list (2). Format and meaning columns are explained under [How the added tables read](#kit-added-tables-legend). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `automatic_grant_medal_chance` | country | 0 dp | ~ Chance that a medal is granted automatically |
| `unit_medal_effectiveness` | country | 0 dp | ~ Strength of the bonuses that unit medals give |
<!-- kit:end id="add-ldr" -->

#### General combat <a id="General_combat"></a>

Note that most of these modifiers are not only in country scope but also in unit leader and navy leader scopes.

Combat-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| offence | Modifies the attack value of our military, navy, and airforce. | `offence = 0.5` | Percentual. | Does not work in country scope, use army_attack_factor instead. | 1.0 |
| defence | Modifies the defence value of our military, navy, and airforce. | `defence = 0.5` | Percentual. | Does not work in country scope, use army_defence_factor instead. | 1.0 |
| <Tactic>_preferred_weight_factor | Modifies the chance for a commander to choose the specified tactic. | `tactic_ambush_preferred_weight_factor = 0.3` | Percentual. | Combat tactics are defined in `/Hearts of Iron IV/common/combat_tactics.txt`. | 1.6 |

#### Land combat <a id="Land_combat"></a>

Note that most of these modifiers are not only in country scope but also in unit leader scope.

Land combat-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| acclimatization_cold_climate_gain_factor | Cold acclimatization gain factor. | `acclimatization_cold_climate_gain_factor = 0.5` | Percentual. |  | 1.0 |
| acclimatization_hot_climate_gain_factor | Hot acclimatization gain factor. | `acclimatization_hot_climate_gain_factor = 0.5` | Percentual. |  | 1.0 |
| air_superiority_bonus_in_combat | The bonus in combat given from having air superiority. | `air_superiority_bonus_in_combat = 0.5` | Percentual. |  | 1.0 |
| army_attack_factor | The bonus to land army's attack. | `army_attack_factor = 0.5` | Percentual. |  | 1.0 |
| army_core_attack_factor | The bonus to land army's attack on core territory. | `army_core_attack_factor = 0.1` | Percentual. |  | 1.0 |
| army_claim_attack_factor | The bonus to land army's attack on claimed territory. | `army_claim_attack_factor = 0.1` | Percentual. |  | 1.17 |
| army_attack_against_major_factor | The bonus to land army's attack against a major country. | `army_attack_against_major_factor = 0.5` | Percentual. |  | 1.11 |
| army_attack_against_minor_factor | The bonus to land army's attack against a non-major country. | `army_attack_against_minor_factor = 0.5` | Percentual. |  | 1.11 |
| army_attack_speed_factor | The bonus to speed at which the land army attacks. | `army_attack_speed_factor = 0.5` | Percentual. |  | 1.0 |
| army_breakthrough_against_major_factor | The bonus to land army's breakthrough against a major country. | `army_breakthrough_against_major_factor = 0.5` | Percentual. |  | 1.11 |
| army_breakthrough_against_minor_factor | The bonus to land army's breakthrough against a non-major country. | `army_breakthrough_against_minor_factor = 0.5` | Percentual. |  | 1.11 |
| army_defence_factor | The bonus to land army's defence. | `army_defence_factor = 0.5` | Percentual. |  | 1.0 |
| army_defence_against_major_factor | The bonus to land army's defence against a major country. | `army_defence_against_major_factor = 0.5` | Percentual. |  | 1.11 |
| army_defence_against_minor_factor | The bonus to land army's defence against a non-major country. | `army_defence_against_minor_factor = 0.5` | Percentual. |  | 1.11 |
| army_core_defence_factor | The bonus to land army's defence on core territory. | `army_core_defence_factor = 0.1` | Percentual. |  | 1.0 |
| army_claim_defence_factor | The bonus to land army's defence on claimed territory. | `army_claim_defence_factor = 0.1` | Percentual. |  | 1.17 |
| army_speed_factor | The bonus to land army's speed. | `army_speed_factor = 0.5` | Percentual. |  | 1.0 |
| army_strength_factor | The bonus to land army's strength. | `army_strength_factor = 0.5` | Percentual. |  | 1.11 |
| <unit type>_attack_factor | The bonus to specified unit type's attack. | `cavalry_attack_factor = 0.5` | Percentual. | Allowed unit types are army_armor, army_artillery, army_infantry, cavalry, mechanized, motorized, special_forces | 1.0 |
| <unit type>_defence_factor | The bonus to the specified unit type's defence. | `army_artillery_defence_factor = 0.5` | Percentual. | Allowed unit types are army_armor, army_artillery, army_infantry, cavalry, mechanized, motorized, special_forces | 1.0 |
| <unit type>_speed_factor | The bonus to specified unit type's speed. | `army_armor_speed_factor = 0.5` | Percentual. | Allowed unit types are army_armor and cavalry. Cavalry_speed_factor is currently broken and not recognized by the game. | 1.0 |
| modifier_army_sub_unit_<unit type>_attack_factor | The bonus to specified unit type's attack. | `modifier_army_sub_unit_armored_car_attack_factor = 0.1` | Percentual. | Allowed unit types are all defined batallions, including those added through mods. | ??? |
| modifier_army_sub_unit_<unit type>_defence_factor | The bonus to the specified unit type's defence. | `modifier_army_sub_unit_armored_car_defence_factor = 0.1` | Percentual. | Allowed unit types are all defined batallions, including those added through mods. | ??? |
| modifier_army_sub_unit_<unit type>_speed_factor | The bonus to specified unit type's speed. | `modifier_army_sub_unit_armored_car_speed_factor = 0.1` | Percentual. | Allowed unit types are all defined batallions, including those added through mods. | ??? |
| army_morale | Modifies the division recovery rate. | `army_morale = 10` | Flat. |  | 1.0 |
| army_morale_factor | Modifies the division recovery rate by a percentage. | `army_morale_factor = 0.3` | Percentual. |  | 1.0 |
| army_org | Modifies the army's organisation. | `army_org = 10` | Flat. |  | 1.0 |
| army_org_factor | Modifies the army's organisation by a percentage. | `army_org_factor = 0.3` | Percentual. |  | 1.0 |
| army_org_regain | Modifies the army's organisation regain speed by a percentage. | `army_org_regain = 0.3` | Percentual. |  | 1.5.1 |
| breakthrough_factor | Modifies the army's breakthrough. | `breakthrough_factor = 0.3` | Percentual. |  | 1.0 |
| cas_damage_reduction | Reduces the damage dealt by close air support. | `cas_damage_reduction = 0.3` | Percentual. |  | 1.0 |
| combat_width_factor | Changes our own combat width. | `combat_width_factor = 0.3` | Percentual. |  | 1.0 |
| coordination_bonus | Changes the bonus to coordination, that is how much damage is done to the primary target instead of being spread out. | `coordination_bonus = 0.3` | Percentual. |  | 1.11 |
| dig_in_speed | Changes entrenchment speed. | `dig_in_speed = 2` | Flat. |  | 1.0 |
| dig_in_speed_factor | Changes entrenchment speed by a percentage. | `dig_in_speed_factor = 0.5` | Percentual. |  | 1.0 |
| experience_gain_army_unit | Changes experience gain by the army divisions. | `experience_gain_army_unit = 0.5` | Flat. |  | 1.0 |
| experience_gain_army_unit_factor | Changes experience gain by the army divisions by a percentage. | `experience_gain_army_unit_factor = 0.5` | Percentual. |  | 1.0 |
| experience_loss_factor | Changes the loss in divisions' experience in combat. | `experience_loss_factor = 0.3` | Percentual. |  | 1.0 |
| initiative_factor | Modifies the initiative. | `initiative_factor = 0.3` | Percentual. |  | 1.11 |
| land_night_attack | Changes the penalty due to attacking at night. | `land_night_attack = 0.5` | Percentual. |  | 1.0 |
| max_dig_in | Changes the maximum entrenchment. | `max_dig_in = 20` | Flat. | Can also apply in state scope. | 1.0 |
| max_dig_in_factor | Changes the maximum entrenchment by a percentage. | `max_dig_in_factor = 0.5` | Percentual. | Can also apply in state scope. | 1.0 |
| max_planning | Changes the maximum planning. | `max_planning = 20` | Flat. |  | 1.0 |
| max_planning_factor | Changes the maximum planning by a percentage. | `max_planning_factor = 0.5` | Percentual. |  | 1.9 |
| pocket_penalty | Reduces the penalty that troops take when they are encircled. | `pocket_penalty = 0.2` | Percentual. |  | 1.0 |
| recon_factor | Changes reconnaisance. | `recon_factor = 0.2` | Percentual. |  | 1.0 |
| recon_factor_while_entrenched | Changes reconnaisance for entrenched divisions. | `recon_factor_while_entrenched = 0.2` | Percentual. |  | 1.0 |
| special_forces_cap | Changes the maximum amount of special forces by a percentage. | `special_forces_cap = 0.5` | Percentual. |  | 1.0 |
| special_forces_min | Changes the minimum amount of special forces. | `special_forces_min = 250` | Flat. |  | 1.0 |
| terrain_penalty_reduction | Decreases the penalties given by terrain. | `terrain_penalty_reduction = 0.3` | Percentual. | Only works in the unit_leader scope despite the modifier being present in vanilla national spirits at the time of writing. | 1.0 |
| org_loss_at_low_org_factor | Modifies the organisation loss for units when they have low organisation. | `org_loss_at_low_org_factor = 0.2` | Percentual. |  | 1.0 |
| org_loss_when_moving | Modifies the organisation loss for units when they are moving. | `org_loss_when_moving = 0.2` | Percentual. |  | 1.0 |
| planning_speed | Modifies the planning speed. | `planning_speed = 0.2` | Percentual. | Works in state scope. | 1.0 |
| experience_gain_<unit type>_combat_factor | Modifies the experience gain in combat for the unit type. | `experience_gain_artillery_combat_factor = 0.3` | Percentual. | Units are defined in `/Hearts of Iron IV/common/units/*.txt` files. | 1.11 |
| experience_gain_<unit type>_training_factor | Modifies the experience gain in training for the unit type. | `experience_gain_destroyer_training_factor = 0.3` | Percentual. | Units are defined in `/Hearts of Iron IV/common/units/*.txt` files. | 1.11 |

<!-- kit:begin id="fix-sub-unit-modifiers" at="section:Land_combat" -->
**Kit correction** The `modifier_army_sub_unit_<unit type>_*` rows say any defined battalion works. In 1.19.3 only the modifiers listed in `sub_unit_modifiers = { ... }` in `common/units/unit_modifiers/unit_modifiers.txt` exist, and the documentation names exactly those 54. To get one for a mod battalion, add its names to that block. [vanilla-confirmed 1.19.3] [docs] `documentation/modifiers_documentation.md`

The stats are `_attack_factor`, `_defence_factor`, `_speed_factor`, `_max_org_factor` and `_org_recovery_cap_factor`. The file marks the speed and max organisation modifiers of `armored_car_recon`, `light_tank_recon` and `blackshirt_assault_battalion` "Cannot be applied to support battalions". Two entries use a sub-unit category instead of a sub-unit: `category_special_forces` (max organisation only) and `category_rocket_artillery` (attack only). All 54 rows: categories `army`, format 2 dp. [vanilla-confirmed 1.19.3]

| Sub-unit token | Attack | Defence | Speed | Max organisation | Organisation recovery cap |
| --- | --- | --- | --- | --- | --- |
| `armored_car` | `modifier_army_sub_unit_armored_car_attack_factor` | `modifier_army_sub_unit_armored_car_defence_factor` | `modifier_army_sub_unit_armored_car_speed_factor` | `modifier_army_sub_unit_armored_car_max_org_factor` |  |
| `armored_car_recon` | `modifier_army_sub_unit_armored_car_recon_attack_factor` | `modifier_army_sub_unit_armored_car_recon_defence_factor` | `modifier_army_sub_unit_armored_car_recon_speed_factor` | `modifier_army_sub_unit_armored_car_recon_max_org_factor` |  |
| `blackshirt_assault_battalion` | `modifier_army_sub_unit_blackshirt_assault_battalion_attack_factor` | `modifier_army_sub_unit_blackshirt_assault_battalion_defence_factor` | `modifier_army_sub_unit_blackshirt_assault_battalion_speed_factor` | `modifier_army_sub_unit_blackshirt_assault_battalion_max_org_factor` |  |
| `camelry` | `modifier_army_sub_unit_camelry_attack_factor` | `modifier_army_sub_unit_camelry_defence_factor` | `modifier_army_sub_unit_camelry_speed_factor` |  |  |
| `category_rocket_artillery` | `modifier_army_sub_unit_category_rocket_artillery_attack_factor` |  |  |  |  |
| `category_special_forces` |  |  |  | `modifier_army_sub_unit_category_special_forces_max_org_factor` |  |
| `cavalry` | `modifier_army_sub_unit_cavalry_attack_factor` | `modifier_army_sub_unit_cavalry_defence_factor` | `modifier_army_sub_unit_cavalry_speed_factor` |  |  |
| `infantry` | `modifier_army_sub_unit_infantry_attack_factor` | `modifier_army_sub_unit_infantry_defence_factor` | `modifier_army_sub_unit_infantry_speed_factor` |  |  |
| `irregular_infantry` | `modifier_army_sub_unit_irregular_infantry_attack_factor` | `modifier_army_sub_unit_irregular_infantry_defence_factor` | `modifier_army_sub_unit_irregular_infantry_speed_factor` | `modifier_army_sub_unit_irregular_infantry_max_org_factor` |  |
| `light_tank_recon` | `modifier_army_sub_unit_light_tank_recon_attack_factor` | `modifier_army_sub_unit_light_tank_recon_defence_factor` | `modifier_army_sub_unit_light_tank_recon_speed_factor` | `modifier_army_sub_unit_light_tank_recon_max_org_factor` |  |
| `long_range_patrol_support` | `modifier_army_sub_unit_long_range_patrol_support_attack_factor` | `modifier_army_sub_unit_long_range_patrol_support_defence_factor` |  |  |  |
| `marine` | `modifier_army_sub_unit_marine_attack_factor` | `modifier_army_sub_unit_marine_defence_factor` | `modifier_army_sub_unit_marine_speed_factor` | `modifier_army_sub_unit_marine_max_org_factor` |  |
| `military_police` | `modifier_army_sub_unit_military_police_attack_factor` | `modifier_army_sub_unit_military_police_defence_factor` | `modifier_army_sub_unit_military_police_speed_factor` | `modifier_army_sub_unit_military_police_max_org_factor` |  |
| `militia` | `modifier_army_sub_unit_militia_attack_factor` | `modifier_army_sub_unit_militia_defence_factor` | `modifier_army_sub_unit_militia_speed_factor` | `modifier_army_sub_unit_militia_max_org_factor` | `modifier_army_sub_unit_militia_org_recovery_cap_factor` |
| `mountaineers` | `modifier_army_sub_unit_mountaineers_attack_factor` | `modifier_army_sub_unit_mountaineers_defence_factor` | `modifier_army_sub_unit_mountaineers_speed_factor` | `modifier_army_sub_unit_mountaineers_max_org_factor` |  |
| `paratrooper` | `modifier_army_sub_unit_paratrooper_attack_factor` | `modifier_army_sub_unit_paratrooper_defence_factor` | `modifier_army_sub_unit_paratrooper_speed_factor` | `modifier_army_sub_unit_paratrooper_max_org_factor` |  |
<!-- kit:end id="fix-sub-unit-modifiers" -->

<!-- kit:begin id="add-land" at="section:Land_combat" -->
**Kit addition** Documented modifiers this section does not list (25). Format and meaning columns are explained under [How the added tables read](#kit-added-tables-legend). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `armor_factor` | army, defensive | 2 dp | (not described in the docs) |
| `army_armor_attack_factor` | army, aggressive | 1 dp |  |
| `army_armor_defence_factor` | army, defensive | 1 dp |  |
| `army_artillery_attack_factor` | army, aggressive | 1 dp |  |
| `army_infantry_attack_factor` | army, aggressive | 1 dp |  |
| `army_infantry_defence_factor` | army, defensive | 1 dp |  |
| `army_non_core_attack_factor` | army, aggressive | 1 dp | Division attack in non-core territory |
| `army_non_core_defence_factor` | army, defensive | 1 dp | Division defence in non-core territory |
| `army_retreat_speed_factor` | army, defensive | 2 dp | Speed of retreating divisions |
| `cannot_retreat_while_attacking` | army, aggressive | bool |  |
| `cannot_retreat_while_defending` | army, defensive | bool |  |
| `casualty_trickleback` | army | 2 dp | (not described in the docs) |
| `cavalry_defence_factor` | army, defensive | 1 dp |  |
| `combat_entrenchment` | army, defensive | 1 dp | Entrenchment combat bonus |
| `mechanized_attack_factor` | army, aggressive | 1 dp |  |
| `mechanized_defence_factor` | army, defensive | 1 dp |  |
| `motorized_attack_factor` | army, aggressive | 1 dp |  |
| `motorized_defence_factor` | army, defensive | 1 dp |  |
| `org_damage_multiplier` | army, defensive | 1 dp | Organisation damage taken |
| `planning_decay_rate_factor` | army, aggressive | 2 dp | How fast a prepared plan decays |
| `shore_bombardment_collateral_damage_factor` | country | 2 dp |  |
| `special_forces_attack_factor` | army, aggressive | 1 dp |  |
| `special_forces_defence_factor` | army, defensive | 1 dp |  |
| `str_damage_multiplier` | army, defensive | 1 dp | Strength damage taken |
| `war_support_reduction_on_damage` | army, defensive | 1 dp | War support lost from casualties |
<!-- kit:end id="add-land" -->

#### Naval invasions <a id="Naval_invasions"></a>

Invasion-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| naval_invasion_prep_speed | Modifies the speed at which a naval invasion is prepared. | `naval_invasion_prep_speed = 10` | Flat. | Can be a targeted modifier or in unit leader scope. | 1.0 |
| naval_invasion_capacity | Modifies the amount of divisions that can have a naval invasion plan going on at the same time. | `naval_invasion_capacity = 10` | Flat. |  | 1.0 |
| naval_invasion_penalty | Modifies the penalty for naval invasions. | `naval_invasion_penalty = 0.3` | Percentual. | Is the opposite of amphibious_invasion_defence. Can also apply in state scope. | 1.0 |
| naval_invasion_planning_bonus_speed | Modifies the speed at which the planning bonus is accumulated during a naval invasion preparation. | `naval_invasion_planning_bonus_speed = 0.3` | Percentual. |  | 1.11 |
| amphibious_invasion | Modifies the speed of units during naval invasions. | `amphibious_invasion = 0.5` | Percentual. |  | 1.6 |
| amphibious_invasion_defence | Modifies the penalty given by naval invasions. | `amphibious_invasion_defence = 0.5` | Percentual. | Is the opposite of naval_invasion_penalty. Can also apply in state scope. | 1.6 |
| invasion_preparation | Modifies the required preparation needed to execute a naval invasion. | `invasion_preparation = 0.3` | Percentual. | Is the opposite of naval_invasion_prep_speed. Can be used in unit leader scope. | 1.6 |

<!-- kit:begin id="add-ninv" at="section:Naval_invasions" -->
**Kit addition** Documented modifiers this section does not list (8). The `air_invasion_*` rows are about airborne invasions and are listed here because the wiki has no airborne section. Format and meaning columns are explained under [How the added tables read](#kit-added-tables-legend). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `air_invasion_division_cap` | air | 0 dp | Max divisions per airborne invasion order |
| `air_invasion_plan_cap` | country | 0 dp | Max airborne invasions that can be planned and prepared at once |
| `air_invasion_prep_days` | country | 1 dp | ~ Days needed to prepare an airborne invasion (unused in vanilla) |
| `air_invasion_preparation` | air, unit_leader | 1 dp | How quickly an airborne invasion can be prepared |
| `naval_commando_raid_distance` | naval | 0 dp | Maximum distance of naval commando raids |
| `naval_invasion_division_cap` | naval | 0 dp | Max divisions per naval invasion order |
| `naval_invasion_plan_cap` | country | 0 dp | Max naval invasions that can be planned and prepared at once |
| `naval_invasion_prep_days` | country | 0 dp | ~ Days needed to prepare a naval invasion (negative shortens it) |
<!-- kit:end id="add-ninv" -->

#### Naval combat <a id="Naval_combat"></a>

Note that most of these modifiers are not only in country scope but also in navy leader scope as well as within equipment modules.

Naval combat-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| convoy_escort_efficiency | Modifies the efficiency of the convoy escort mission. | `convoy_escort_efficiency = 0.5` | Percentual. |  | 1.6 |
| convoy_raiding_efficiency_factor | Modifies the efficiency of the convoy raiding mission. | `convoy_raiding_efficiency_factor = 0.5` | Percentual. |  | 1.6 |
| convoy_retreat_speed | Modifies the speed of convoys retreating. | `convoy_retreat_speed = 0.5` | Percentual. |  | 1.6 |
| critical_receive_chance | Changes the chance for the enemy to get a critical hit on us in naval combat. | `critical_receive_chance = 0.5` | Percentual. |  | 1.6 |
| experience_gain_navy_unit | Modifies the daily gain of experience by the ships. | `experience_gain_navy_unit = 0.02` | Flat. |  | 1.6 |
| experience_gain_navy_unit_factor | Modifies the gain of experience by the ships by a percentage. | `experience_gain_navy_unit_factor = 0.3` | Percentual. |  | 1.6 |
| mines_planting_by_fleets_factor | Modifies the efficiency of the mine planting mission. | `mines_planting_by_fleets_factor = 0.3` | Percentual. |  | 1.6 |
| mines_sweeping_by_fleets_factor | Modifies the efficiency of the mine sweeping mission. | `mines_sweeping_by_fleets_factor = 0.3` | Percentual. |  | 1.6 |
| naval_accidents_chance | Modifies the chance for a ship to be accidentally sunk or damaged. | `naval_accidents_chance = 0.3` | Percentual. |  | 1.6 |
| navy_anti_air_attack | Modifies the attack against enemy airplanes for the country's ships. | `navy_anti_air_attack = 5` | Flat. |  | 1.6 |
| navy_anti_air_attack_factor | Modifies the attack against enemy airplanes for the country's ships by a percentage. | `navy_anti_air_attack_factor = 0.3` | Percentual. |  | 1.6 |
| naval_coordination | Modifies how quickly the fleet can gather or disperse when a target is found or when switching missions. | `naval_coordination = 0.3` | Percentual. |  | 1.6 |
| naval_critical_effect_factor | Modifies the effects of sustained critical hits on our ships. | `naval_critical_effect_factor = 0.3` | Percentual. |  | 1.6 |
| naval_critical_score_chance_factor | Modifies the chance for us to get a critical hit on the enemy in naval combat. | `naval_critical_score_chance_factor = 0.3` | Percentual. |  | 1.6 |
| naval_damage_factor | Modifies the damage dealt by our ships. | `naval_damage_factor = 0.3` | Percentual. |  | 1.6 |
| naval_defense_factor | Modifies the damage received by our ships. | `naval_defense_factor = 0.3` | Percentual. |  | 1.6 |
| naval_detection | Modifies the chance for our ships to detect submarines. | `naval_detection = 0.3` | Percentual. |  | 1.6 |
| naval_enemy_fleet_size_ratio_penalty_factor | Modifies the penalty the enemy receives for having a larger amount of ships than us. | `naval_enemy_fleet_size_ratio_penalty_factor = 0.3` | Percentual. |  | 1.6 |
| naval_enemy_positioning_in_initial_attack | Modifies the positioning of the enemy during the initial naval attack. | `naval_enemy_positioning_in_initial_attack = 3` | Flat. |  | 1.11 |
| naval_enemy_retreat_chance | Modifies the chance for the enemy to retreat. | `naval_enemy_retreat_chance = 0.3` | Percentual. |  | 1.6 |
| naval_has_potf_in_combat_attack | Modifies the attack of the navy when fighting together with the pride of the fleet. | `naval_has_potf_in_combat_attack = 0.3` | Percentual. |  | 1.6 |
| naval_has_potf_in_combat_defense | Modifies the defense of the navy when fighting together with the pride of the fleet. | `naval_has_potf_in_combat_defense = 0.3` | Percentual. |  | 1.6 |
| naval_hit_chance | Modifies the chance for the naval attacks to land. | `naval_hit_chance = 0.3` | Percentual. |  | 1.6 |
| naval_mine_hit_chance | Modifies the chance for a naval mine to hit. | `naval_mine_hit_chance = 0.3` | Percentual. |  | 1.6 |
| naval_mines_damage_factor | Modifies the damage naval mines deal to enemy ships. | `naval_mines_damage_factor = 0.3` | Percentual. |  | 1.6 |
| naval_mines_effect_reduction | Modifies the damage enemy naval mines deal. | `naval_mines_effect_reduction = 0.3` | Percentual. |  | 1.6 |
| naval_morale | Modifies the navy recovery rate. | `naval_morale = 15` | Flat. |  | 1.6 |
| naval_morale_factor | Modifies the navy recovery rate by a percentage. | `naval_morale_factor = 0.3` | Percentual. |  | 1.6 |
| naval_night_attack | Modifies the damage dealt by the country's ships at night. | `naval_night_attack = 0.3` | Percentual. |  | 1.11 |
| naval_retreat_chance | Modifies the chance for the country's ships to retreat. | `naval_retreat_chance = 0.3` | Percentual. |  | 1.6 |
| naval_retreat_chance_after_initial_combat | Modifies the chance for the country's ships to retreat after initial combat. | `naval_retreat_chance_after_initial_combat = 0.3` | Percentual. |  | 1.11 |
| naval_retreat_speed | Modifies the speed at which the country's ships retreat. | `naval_retreat_speed = 0.3` | Percentual. |  | 1.6 |
| naval_retreat_speed_after_initial_combat | Modifies the speed at which the country's ships to retreat after initial combat. | `naval_retreat_speed_after_initial_combat = 0.3` | Percentual. |  | 1.11 |
| naval_speed_factor | Modifies the speed of the country's ships. | `naval_speed_factor = 0.3` | Percentual. |  | 1.6 |
| navy_org | Modifies the navy's organisation. | `navy_org = 10` | Flat. |  | 1.0 |
| navy_org_factor | Modifies the navy's organisation by a percentage. | `navy_org_factor = 0.3` | Percentual. |  | 1.0 |
| navy_max_range | Modifies the navy's maximum range. | `navy_max_range = 10` | Flat. |  | 1.0 |
| navy_max_range_factor | Modifies the navy's maximum range by a percentage. | `navy_max_range_factor = 0.3` | Percentual. |  | 1.0 |
| naval_torpedo_cooldown_factor | Modifies the rate at which the country's ships can fire torpedos. | `naval_torpedo_cooldown_factor = 0.3` | Percentual. |  | 1.6 |
| naval_torpedo_hit_chance_factor | Modifies the likelihood for country's torpedos to hit enemy ships. | `naval_torpedo_hit_chance_factor = 0.3` | Percentual. |  | 1.6 |
| naval_torpedo_reveal_chance_factor | Modifies the chance that the country's submarines reveal themselves when firing torpedos. | `naval_torpedo_reveal_chance_factor = 0.3` | Percentual. |  | 1.6 |
| naval_torpedo_screen_penetration_factor | Modifies the rate at which the country's torpedos penalise enemy screening. | `naval_torpedo_screen_penetration_factor = 0.3` | Percentual. |  | 1.6 |
| naval_torpedo_damage_reduction_factor | Modifies the damage at which enemy torpedos damage the country's ships. | `naval_torpedo_damage_reduction_factor = 0.3` | Percentual. |  | 1.12 |
| naval_torpedo_enemy_critical_chance_factor | Modifies the chance for an enemy torpedo to get a cricical hit against the country's ships. | `naval_torpedo_enemy_critical_chance_factor = 0.3` | Percentual. |  | 1.12 |
| naval_light_gun_hit_chance_factor | Modifies the chance for the country's naval light guns to hit enemy ships. | `naval_light_gun_hit_chance_factor = 0.3` | Percentual. |  | 1.12 |
| naval_heavy_gun_hit_chance_factor | Modifies the chance for the country's naval heavy guns to hit enemy ships. | `naval_heavy_gun_hit_chance_factor = 0.3` | Percentual. |  | 1.12 |
| navy_capital_ship_attack_factor | Modifies the attack of the country's capital ships. | `navy_capital_ship_attack_factor = 0.3` | Percentual. |  | 1.6 |
| navy_capital_ship_defence_factor | Modifies the defence of the country's capital ships. | `navy_capital_ship_defence_factor = 0.3` | Percentual. |  | 1.6 |
| navy_screen_attack_factor | Modifies the attack of the country's screening ships. | `navy_screen_attack_factor = 0.3` | Percentual. |  | 1.6 |
| navy_screen_defence_factor | Modifies the defence of the country's screening ships. | `navy_screen_defence_factor = 0.3` | Percentual. |  | 1.6 |
| navy_submarine_attack_factor | Modifies the attack of the country's submarines. | `navy_submarine_attack_factor = 0.3` | Percentual. |  | 1.6 |
| navy_submarine_defence_factor | Modifies the defence of the country's submarines. | `navy_submarine_defence_factor = 0.3` | Percentual. |  | 1.6 |
| navy_submarine_detection_factor | Modifies the country's detection of enemy submarines. | `navy_submarine_detection_factor = 0.3` | Percentual. |  | 1.6 |
| navy_visibility | Modifies the visibility of the country's navy. | `navy_visibility = 0.3` | Percentual. |  | 1.6 |
| navy_weather_penalty | Modifies the penalty the country's navy gets during poor weather. | `navy_weather_penalty = 0.3` | Percentual. |  | 1.11 |
| night_spotting_chance | Modifies the chance for the country's navy to spot the enemy at night. | `night_spotting_chance = 0.3` | Percentual. |  | 1.11 |
| positioning | Modifies the positioning of the country's navy. | `positioning = 0.3` | Percentual. |  | 1.6 |
| repair_speed_factor | Modifies the speed at which the dockyards repair the navy. | `repair_speed_factor = 0.3` | Percentual. |  | 1.6 |
| screening_efficiency | Modifies the efficiency screen ships operate. | `screening_efficiency = 0.3` | Percentual. |  | 1.6 |
| screening_without_screens | Modifies the base screening without any screen ships assigned. | `screening_without_screens = 0.3` | Percentual. |  | 1.11 |
| ships_at_battle_start | Modifies the number of ships at first contact. | `ships_at_battle_start = 0.3` | Percentual. |  | 1.6 |
| spotting_chance | Modifies the chance to spot enemy ships. | `spotting_chance = 0.3` | Percentual. |  | 1.6 |
| strike_force_movement_org_loss | Modifies the organisation loss from movement during the strike force mission. | `strike_force_movement_org_loss = 0.3` | Percentual. |  | 1.6 |
| sub_retreat_speed | Modifies the retreat speed of submarines. | `sub_retreat_speed = 0.3` | Percentual. |  | 1.6 |
| submarine_attack | Modifies the attack of submarines. | `submarine_attack = 0.3` | Percentual. |  | 1.6 |

<!-- kit:begin id="add-naval" at="section:Naval_combat" -->
**Kit addition** Documented modifiers this section does not list (5). Format and meaning columns are explained under [How the added tables read](#kit-added-tables-legend). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `headquarters_experience_gain_factor` | naval | 2 dp | Experience gained from naval headquarters (unused in vanilla) |
| `max_organisation` | naval | 0 dp | (not described in the docs) |
| `naval_mission_xp_factor` | naval | 3 dp | Naval mission experience (unused in vanilla) |
| `naval_ship_recovery_chance` | naval | 0 dp |  |
| `naval_ship_recovery_chance_factor` | naval | 0 dp | Unused in vanilla |
<!-- kit:end id="add-naval" -->

#### Carriers and their planes <a id="Carriers_and_their_planes"></a>

Carrier-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| navy_carrier_air_agility_factor | Modifies the agility of airplanes executing tasks from carriers. | `navy_carrier_air_agility_factor = 0.3` | Percentual. |  | 1.6 |
| navy_carrier_air_attack_factor | Modifies the attack of airplanes executing tasks from carriers. | `navy_carrier_air_attack_factor = 0.3` | Percentual. |  | 1.6 |
| navy_carrier_air_targetting_factor | Modifies the targeting of airplanes executing tasks from carriers. | `navy_carrier_air_targetting_factor = 0.3` | Percentual. |  | 1.6 |
| air_carrier_night_penalty_reduction_factor | Modifies the reduction of the night penalty for air carriers. | `air_carrier_night_penalty_reduction_factor = 0.5` | Percentual. |  | 1.0 |
| carrier_capacity_penalty_reduction | Modifies the penalty given by overcrowding a carrier with planes. | `carrier_capacity_penalty_reduction = 0.5` | Percentual. |  | 1.6 |
| carrier_traffic | Modifies the traffic of carriers. | `carrier_traffic = 0.5` | Percentual. |  | 1.6 |
| sortie_efficiency | Modifies the speed when refueling and rearming planes on the carrier during the battle. | `sortie_efficiency = 0.3` | Percentual. |  | 1.6 |
| carrier_sortie_hours_delay | Modifies the delay in hours for refueling and rearming planes on the carrier. | `carrier_sortie_hours_delay = 2` | Flat. |  | 1.12 |
| carrier_night_traffic | Modifies the traffic of carriers at night. | `carrier_night_traffic = 0.5` | Percentual. |  | 1.11 |
| fighter_sortie_efficiency | Modifies the speed when refueling and rearming fighter planes on the carrier during the battle. | `fighter_sortie_efficiency = 0.3` | Percentual. |  | 1.6 |

#### Air combat <a id="Air_combat"></a>

Note that most of these modifiers are not only in country scope but also in ace scope.

Air-related country-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| air_accidents_factor | Modifies the chance for air accidents to happen. | `air_accidents_factor = 0.5` | Percentual. |  | 1.0 |
| air_ace_bonuses_factor | Modifies the bonuses the aces grant. | `air_ace_bonuses_factor = 0.5` | Percentual. |  | 1.11 |
| air_ace_generation_chance_factor | Modifies the chance for aces to appear. | `air_ace_generation_chance_factor = 0.5` | Percentual. |  | 1.11 |
| ace_effectiveness_factor | Modifies the effectiveness of aces | `ace_effectiveness_factor = 0.5` | Percentual. |  | 1.0 |
| air_agility_factor | Modifies the agility of the country's airplanes. | `air_agility_factor = 0.5` | Percentual. |  | 1.0 |
| air_attack_factor | Modifies the attack of the country's airplanes. | `air_attack_factor = 0.5` | Percentual. |  | 1.0 |
| air_defence_factor | Modifies the defence of the country's airplanes. | `air_defence_factor = 0.5` | Percentual. |  | 1.0 |
| air_interception_detect_factor | Modifies the chance of detecting an enemy plane while on interception mission. | `air_interception_detect_factor = 0.5` | Percentual. |  | 1.0 |
| naval_strike_targetting_factor | Modifies the ability of planes to target their objectives when executing naval strikes. | `naval_strike_targetting_factor = 0.5` | Percentual. |  | 1.0 |
| port_strike | Modifies the damage done by planes on the port strike mission. | `port_strike = 0.5` | Percentual. |  | 1.0 |
| air_close_air_support_org_damage_factor | Modifies the damage to division organisation by planes on the close air support mission. | `air_close_air_support_org_damage_factor = 0.5` | Percentual. |  | 1.11 |
| air_bombing_targetting | Modifies targetting for ground bombing. | `air_bombing_targetting = 0.5` | Percentual. |  | 1.0 |
| air_cas_efficiency | Modifies efficiency of close-air-support. | `air_cas_efficiency = 0.5` | Percentual. |  | 1.0 |
| air_cas_present_factor | Modifies impact of close-air-support in land combat. | `air_cas_present_factor = 0.5` | Percentual. |  | 1.0 |
| air_escort_efficiency | Modifies ability of planes in dogfights. | `air_escort_efficiency = 0.5` | Percentual. |  | 1.0 |
| air_home_defence_factor | Modifies the defence of airplanes when defending states in the home region (Connected to the country's capital by land) | `air_home_defence_factor = 0.5` | Percentual. |  | 1.11 |
| air_intercept_efficiency | Modifies the efficiency of air interception. | `air_intercept_efficiency = 0.5` | Percentual. |  | 1.0 |
| air_manpower_requirement_factor | Modifies the manpower required to deploy an airplane. | `air_manpower_requirement_factor = -0.5` | Percentual. |  | 1.11 |
| air_maximum_speed_factor | Modifies the maximum speed of the airforce. | `air_maximum_speed_factor = 0.5` | Percentual. |  | 1.0 |
| air_mission_efficiency | Modifies the efficiency of airplanes in missions. | `air_mission_efficiency = 0.5` | Percentual. |  | 1.0 |
| air_mission_xp_gain_factor | Modifies the experience gain for airplanes for doing missions. | `air_mission_xp_gain_factor = 0.5` | Percentual. |  | 1.0 |
| air_nav_efficiency | Modifies the efficiency of airplanes doing port strike and naval bombing missions. | `air_nav_efficiency = 0.5` | Percentual. |  | 1.0 |
| air_night_penalty | Modifies the penalty the airforce receives while at night. | `air_night_penalty = 0.5` | Percentual. |  | 1.0 |
| air_power_projection_factor | Modifies the power projection given out by the airplanes. | `air_power_projection_factor = 0.5` | Percentual. |  | 1.0 |
| air_range_factor | Modifies the range of the airplanes. | `air_range_factor = 0.5` | Percentual. |  | 1.0 |
| air_strategic_bomber_bombing_factor | Modifies the efficiency of the strategic bombing mission. | `air_strategic_bomber_bombing_factor = 0.5` | Percentual. |  | 1.0 |
| air_strategic_bomber_night_penalty | Modifies the penalty for the strategic bombing mission while at night. | `air_strategic_bomber_night_penalty = 0.5` | Percentual. |  | 1.0 |
| air_superiority_detect_factor | Modifies the chance to detect enemy planes while on the air superiority mission. Displays as Fighter Detection. | `air_superiority_detect_factor = 0.5` | Percentual. |  | 1.0 |
| air_superiority_efficiency | Modifies the efficiency of the air superiority mission. | `air_superiority_efficiency = 0.5` | Percentual. |  | 1.0 |
| air_training_xp_gain_factor | Modifies the air experience gain from training. | `air_training_xp_gain_factor = 0.5` | Percentual. |  | 1.6 |
| air_untrained_pilots_penalty_factor | Modifies the penalty given to airplanes which don't have enough experience. | `air_untrained_pilots_penalty_factor = 0.5` | Percentual. |  | 1.6 |
| air_weather_penalty | Modifies the penalty the airplanes receive because of weather. | `air_weather_penalty = 0.5` | Percentual. |  | 1.0 |
| air_wing_xp_loss_when_killed_factor | Modifies the experience loss of airplanes due to airplanes being shot down. | `air_wing_xp_loss_when_killed_factor = 0.5` | Percentual. |  | 1.0 |
| army_bonus_air_superiority_factor | Modifies the bonus to land combat from air superiority. | `army_bonus_air_superiority_factor = 0.5` | Percentual. |  | 1.0 |
| enemy_army_bonus_air_superiority_factor | Modifies the effect to land combat from enemy air superiority. | `enemy_army_bonus_air_superiority_factor = 0.5` | Percentual. |  | 1.0 |
| ground_attack_factor | Modifies the bonus to airplane attack on enemy divisions by a percentage. | `ground_attack_factor = 0.5` | Percentual. |  | 1.0 |
| mines_planting_by_air_factor | Modifies efficiency of airplanes planting mines. | `mines_planting_by_air_factor = 0.5` | Percentual. |  | 1.0 |
| mines_sweeping_by_air_factor | Modifies efficiency of airplanes sweeping mines. | `mines_sweeping_by_air_factor = 0.5` | Percentual. |  | 1.0 |
| strategic_bomb_visibility | Modifies the chance for the enemy to detect our strategic bombers. | `strategic_bomb_visibility = 0.5` | Percentual. |  | 1.0 |
| rocket_attack_factor | Modifies the attack given to rockets. | `rocket_attack_factor = 0.5` | Percentual. |  | 1.0 |

<!-- kit:begin id="add-air" at="section:Air_combat" -->
**Kit addition** Documented modifiers this section does not list (4). Format and meaning columns are explained under [How the added tables read](#kit-added-tables-legend). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `air_strategic_bomber_defence_factor` | air | 2 dp | ~ Defence of strategic bombers |
| `ground_attack` | air, aggressive | 1 dp | Ground attack (unused in vanilla) |
| `naval_strike_agility_factor` | air | 0 dp | Agility of aircraft on naval strike missions |
| `naval_strike_attack_factor` | air | 0 dp | Attack of aircraft on naval strike missions |
<!-- kit:end id="add-air" -->

#### Targeted modifiers <a id="Targeted_modifiers"></a>

These modifiers are targeted, meaning that they must be used in a block for targeted modifiers rather than regular modifiers. These include `targeted_modifier = { ... }` in ideas, traits, advisors, and decisions; [relation modifiers](#Relation_modifiers).
A `targeted_modifier` block is structured as such:

```text
targeted_modifier = {
    tag = FROM    # this can also take a variable that stores a scope
    attack_bonus_against = 0.1
    defense_bonus_against = 0.1
}
```

**This is a completely separate block from `modifier = { ... }`** in ideas, advisors, and decisions; as such it will not work when it's put inside of `modifier = { ... }`.

Targeted modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| extra_trade_to_target_factor | Adds extra produced resources available for trade to target country. | `extra_trade_to_target_factor = 0.5` | Percentual. |  | 1.5 |
| generate_wargoal_tension_against | Changes world tension necessary for us to justify against the target country. | `generate_wargoal_tension_against = 0.5` | Flat. |  | 1.5 |
| cic_to_target_factor | Gives a portion of the country's civilian industry to the specified target. | `cic_to_target_factor = 0.5` | Percentual. |  | 1.5 |
| mic_to_target_factor | Gives a portion of the country's military industry to the specified target. | `mic_to_target_factor = 0.5` | Percentual. |  | 1.5 |
| trade_cost_for_target_factor | The cost for the targeted country to purchase this country's resources. | `trade_cost_for_target_factor = 0.5` | Percentual. |  | 1.5 |
| targeted_legitimacy_daily | Changes daily gain of legitimacy of the target country. | `targeted_legitimacy_daily = 0.5` | Flat. |  | 1.6 |
| attack_bonus_against | Gives an attack bonus against the armies of the specified country. | `attack_bonus_against = 0.5` | Percentual. | Due to a bug, this will not apply to units that are defending. | 1.5 |
| attack_bonus_against_cores | Gives an attack bonus against the armies of the specified country on its core territory. | `attack_bonus_against_cores = 0.5` | Percentual. |  | 1.5 |
| breakthrough_bonus_against | Gives a breakthrough bonus against the armies of the specified country. | `breakthrough_bonus_against = 0.5` | Percentual. |  | 1.5 |
| defense_bonus_against | Gives a defense bonus against the armies of the specified country. | `defense_bonus_against = 0.5` | Percentual. | Due to a bug, this will not apply to units that are attacking. | 1.5 |

<!-- kit:begin id="add-targ" at="section:Targeted_modifiers" -->
**Kit addition** Twelve more targeted modifiers (the section lists ten). They belong in a `targeted_modifier = { tag = X ... }` block, like `attack_bonus_against`. [vanilla-confirmed 1.19.4.1]

- The in-game text of eleven of them ends in "against a country" (for example "Capital Ship Attack Against a Country"), and `river_crossing_factor_against` reads "against country". [vanilla-confirmed 1.19.4.1] `localisation/english/modifiers_l_english.yml`
- All twelve are documented modifiers. [docs] `documentation/modifiers_documentation.md`
- Vanilla uses `spotting_chance_against`, `navy_capital_ship_attack_factor_against` and `navy_screen_attack_factor_against` inside `targeted_modifier` in `common/ideas/japan.txt` (the first two also in `common/ideas/australia.txt`), and `river_crossing_factor_against` in `common/ideas/GER.txt`. The other eight are unused in vanilla. [vanilla-confirmed 1.19.4.1]
- `army_attack_against_major_factor` and its siblings are not targeted: they compare against major and minor countries as a class.

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `amphibious_invasion_against` | naval | 1 dp | Targeted: amphibious invasion strength against one country |
| `invasion_preparation_against` | naval | 1 dp | Targeted: naval invasion preparation against one country |
| `naval_critical_score_chance_factor_against` | naval, unit_leader, aggressive | 2 dp | Targeted: naval critical score chance against one country |
| `naval_hit_chance_against` | naval | 0 dp | Targeted: naval hit chance against one country |
| `navy_capital_ship_attack_factor_against` | naval, aggressive | 2 dp | Targeted: capital ship attack against one country |
| `navy_capital_ship_defence_factor_against` | naval, defensive | 2 dp | Targeted: capital ship defence against one country |
| `navy_screen_attack_factor_against` | naval, aggressive | 2 dp | Targeted: screen ship attack against one country |
| `navy_screen_defence_factor_against` | naval, defensive | 2 dp | Targeted: screen ship defence against one country |
| `navy_submarine_attack_factor_against` | naval, aggressive | 2 dp | Targeted: submarine attack against one country |
| `navy_submarine_defence_factor_against` | naval, defensive | 2 dp | Targeted: submarine defence against one country |
| `river_crossing_factor_against` | army | 2 dp | Targeted: river crossing penalty against one country |
| `spotting_chance_against` | naval | 0 dp | Targeted: naval spotting chance against one country |
<!-- kit:end id="add-targ" -->

### State scope <a id="State_scope"></a>

Several country-scoped modifiers (such as a portion of those in the [land combat section](#Land_combat)) unlisted here can go into state scope. A large portion of state-scoped modifiers can go into province scope.

State-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| army_speed_factor_for_controller | Changes the division speed for the controller of the state. | `army_speed_factor_for_controller = 0.5` | Percentual. |  | 1.0 |
| attrition_for_controller | Changes the attrition for the controller of the state. | `attrition_for_controller = 0.5` | Percentual. |  | 1.0 |
| equipment_capture_for_controller | Changes the equipment capture ratio by the state's controller. | `equipment_capture_for_controller = 0.3` | Flat. |  | 1.13 |
| equipment_capture_factor_for_controller | Modifies the equipment capture ratio by the state's controller. | `equipment_capture_factor_for_controller = 0.3` | Percentual. |  | 1.13 |
| enemy_army_speed_factor | Modifies the speed of divisions at war with the state's owner. | `enemy_army_speed_factor = 0.3` | Percentual. |  | 1.13 |
| enemy_local_supplies | Modifies the supply of divisions at war with the state's owner. | `enemy_local_supplies = 0.3` | Percentual. |  | 1.13 |
| enemy_attrition | Modifies the attrition of divisions at war with the state's owner. | `enemy_attrition = 0.3` | Percentual. |  | 1.13 |
| enemy_truck_attrition_factor | Modifies the truck attrition of divisions at war with the state's owner. | `enemy_truck_attrition_factor = 0.3` | Percentual. |  | 1.13 |
| compliance_gain | Changes the compliance gain in the current state. | `compliance_gain = 0.01` | Flat. | Can also go into country scope. Can also be used as a targeted modifier. | 1.9 |
| compliance_growth | Changes the compliance growth speed in the current state. | `compliance_growth = 0.5` | Percentual. | Can also go into country scope. | 1.9 |
| disable_strategic_redeployment | Disables strategic redeployment in the state. | `disable_strategic_redeployment = 1` | Boolean (only 1). |  | 1.9 |
| disable_strategic_redeployment_for_controller | Disables strategic redeployment in the state for the controller. | `disable_strategic_redeployment_for_controller = 1` | Boolean (only 1). |  | 1.9 |
| enemy_intel_network_gain_factor_over_occupied_tag | Modifies enemy intel network strength gain. | `enemy_intel_network_gain_factor_over_occupied_tag = 0.3` | Percentual. |  | 1.9 |
| local_building_slots | Modifies amount of building slots. | `local_building_slots = 2` | Flat. |  | 1.9 |
| local_building_slots_factor | Modifies amount of building slots by a percentage. | `local_building_slots_factor = 0.3` | Percentual. |  | 1.9 |
| local_factories | Modifies amount of available factories in the state. | `local_factories = 0.3` | Percentual. |  | 1.9 |
| local_factory_energy_consumption | Modifies amount of energy consumed by factories in the state. | `local_factory_energy_consumption = 0.2` | Percentual | The game file documentation incorrectly labels this as a number with zero decimals, yet the code itself uses a decimal, | 1.17 |
| local_factory_energy_consumption_per_infrastructure | Modifies amount of energy consumed by factories depending on the infrastructure of the state. | `local_factory_energy_consumption_per_infrastructure = 0.2` | Percentual |  | 1.17.2 |
| local_factory_sabotage | Modifies chance for factory sabotage. | `local_factory_sabotage = 0.3` | Percentual. |  | 1.9 |
| local_intel_to_enemies | Modifies amount of intel to enemies. | `local_intel_to_enemies = 0.3` | Percentual. |  | 1.9 |
| local_manpower | Modifies amount of available manpower. | `local_manpower = 0.3` | Percentual. |  | 1.4 |
| local_non_core_manpower | Modifies amount of available non-core manpower. | `local_non_core_manpower = 0.3` | Percentual. |  | 1.3.3 |
| local_org_regain | Modifies how much organisation is regained after combat. | `local_org_regain = -0.3` | Percentual. | Can be used in provinces and strategic regions. | 1.0 |
| local_resource_gain_efficiency_per_infrastructure | Modifies amount of available resources gained depending on the infrastructure of the state. | `local_resource_gain_efficiency_per_infrastructure = 0.3` | Percentual. |  | 1.17.2 |
| local_resources | Modifies amount of available resources. | `local_resources = 0.3` | Flat. |  | 1.9 |
| local_supplies | Modifies amount of available supplies. | `local_supplies = 0.3` | Percentual. |  | 1.9 |
| local_supplies_for_controller | Modifies amount of available supplies for the controller. | `local_supplies_for_controller = 0.3` | Percentual. |  | 1.9 |
| local_supply_impact_factor | Modifies the impact that the state's local supplies have. | `local_supply_impact_factor = 0.3` | Percentual. |  | 1.12 |
| local_non_core_supply_impact_factor | Modifies the impact that the state's local supplies have if the state is not cored by the controller of provinces within. | `local_non_core_supply_impact_factor = 0.3` | Percentual. |  | 1.12 |
| mobilization_speed | Modifies the mobilisation speed. | `mobilization_speed = 0.3` | Percentual. |  | 1.9 |
| non_core_manpower | Modifies the amount of recruited non-core manpower. | `non_core_manpower = 0.3` | Percentual. |  | 1.9 |
| max_fuel_building | Modifies the amount of fuel capacity, in thousands, given to the state controller from the building. | `max_fuel_building = 1500` | Percentual. | Does not have to be in a building. | 1.0 |
| recruitable_population | Modifies the amount of recruited manpower. | `recruitable_population = 0.03` | Flat. |  | 1.9 |
| recruitable_population_factor | Modifies the amount of recruited manpower by a percentage. | `recruitable_population_factor = 0.3` | Percentual. |  | 1.9 |
| resistance_damage_to_garrison | Modifies the amount of resistance damage to the garrison. | `resistance_damage_to_garrison = 0.3` | Percentual. |  | 1.9 |
| resistance_decay | Modifies the speed of resistance decay. | `resistance_decay = 0.3` | Percentual. |  | 1.9 |
| resistance_garrison_penetration_chance | Modifies the chance for the garrison to be penetrated. | `resistance_garrison_penetration_chance = 0.3` | Percentual. |  | 1.9 |
| resistance_growth | Modifies the speed of the resistance growth. | `resistance_growth = 0.3` | Percentual. |  | 1.9 |
| resistance_target | Modifies the target of the resistance growth. | `resistance_target = 0.3` | Percentual. |  | 1.9 |
| starting_compliance | Modifies the base compliance value. | `starting_compliance = 0.3` | Percentual. |  | 1.9 |
| state_bunker_max_level_terrain_limit | Modifies the amount of available bunker building slots in the state. | `state_bunker_max_level_terrain_limit = 6` | Flat. |  |  |
| state_coastal_bunker_max_level_terrain_limit | Modifies the amount of available coastal bunker building slots in the state. | `state_coastal_bunker_max_level_terrain_limit = 6` | Flat. |  |  |
| state_production_speed_<building>_factor | Modifies the building speed of the specified building in the state. | `state_production_speed_industrial_complex_factor = 0.3` | Percentual. | Use state_production_speed_buildings_factor for it to apply to all buildings. (added in 1.9) | 1.9.1 |
| state_repair_speed_<building>_factor | Modifies the repair speed of the specified building in the state. | `state_repair_speed_industrial_complex_factor = 0.3` | Percentual. |  | 1.9.1 |
| state_resource_<resource> | Modifies the amount of the specified resource in the state. | `state_resource_oil = 5` | Flat. |  | 1.0 |
| state_resources_factor | Modifies the amount of resources in a state. | `state_resources_factor = 0.2` | Percentual. |  | 1.9 |
| state_resource_cost_<resource> | Modifies the amount of the specified resource in the state. | `state_resource_cost_rubber = 5` | Flat. |  | 1.9 |
| temporary_state_resource_<resource> | Modifies the amount of the specified resource in the state as an added modifier after the base one. | `temporary_state_resource_tungsten = 5` | Flat. |  | 1.0 |
| enemy_operative_detection_chance_over_occupied_tag | Offsets the chance for an enemy operative to be detected for the tag that occupies this state. | `enemy_operative_detection_chance_over_occupied_tag = 5` | Flat. |  | 1.9 |
| enemy_operative_detection_chance_factor_over_occupied_tag | Modifies the chance for an enemy operative to be detected for the tag that occupies this state. | `enemy_operative_detection_chance_factor_over_occupied_tag = 0.5` | Percentual. |  | 1.9 |

<!-- kit:begin id="add-state" at="section:State_scope" -->
**Kit addition** Documented modifiers this section does not list (1). Format and meaning columns are explained under [How the added tables read](#kit-added-tables-legend). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `state_production_speed_facility_factor` | state | 2 dp | Local construction speed of facilities (unused in vanilla) |
<!-- kit:end id="add-state" -->

### Unit leader scope <a id="Unit_leader_scope"></a>

Note that most modifiers in land and naval combat sections also apply.

Unit leader-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| cannot_use_abilities | Disables using abilities. | `cannot_use_abilities = 1` | Boolean (only 1). |  | 1.5 |
| dont_lose_dig_in_on_attack | Disables losing the entrechment bonus during attack. | `dont_lose_dig_in_on_attack = 1` | Boolean (only 1). |  | 1.5 |
| exiled_divisions_attack_factor | Modifies the attack of divisions led by this unit leader if they're exiled. | `exiled_divisions_attack_factor = 0.4` | Percentual. |  | 1.6 |
| exiled_divisions_defense_factor | Modifies the defence of divisions led by this unit leader if they're exiled. | `exiled_divisions_defense_factor = 0.4` | Percentual. |  | 1.6 |
| own_exiled_divisions_attack_factor | Modifies the attack of divisions led by this unit leader if they're exiled and belong to the same country. | `own_exiled_divisions_attack_factor = 0.4` | Percentual. |  | 1.6 |
| own_exiled_divisions_defense_factor | Modifies the defence of divisions led by this unit leader if they're exiled and belong to the same country. | `own_exiled_divisions_defense_factor = 0.4` | Percentual. |  | 1.6 |
| experience_gain_factor | Modifies the experience gained by the unit leader. | `experience_gain_factor = 0.1` | Percentual. |  | 1.5 |
| fortification_collateral_chance | Chance for combat to damage enemy forts. | `fortification_collateral_chance = 0.4` | Percentual. |  | 1.5 |
| fortification_damage | Damage enemy forts receive from combat. | `fortification_damage = 0.4` | Percentual. |  | 1.5 |
| max_commander_army_size | Modifies amount of divisions that can be led by the army leader without penalty. | `max_commander_army_size = 12` | Flat. |  | 1.5 |
| max_army_group_size | Modifies amount of army groups that can be led by the field marshal without penalty. | `max_army_group_size = 1` | Flat. |  | 1.5 |
| paradrop_organization_factor | The amount of organisation paratroopers will have after paradropping. | `paradrop_organization_factor = 0.5` | Percentual. |  | 1.5 |
| paratrooper_aa_defense | The strength of anti-air against paratroopers. | `paratrooper_aa_defense = 0.5` | Percentual. |  | 1.5 |
| paratrooper_weight_factor | Paratrooper transport space factor. | `paratrooper_weight_factor = 0.5` | Percentual. | Can also be used in country scope. | 1.13 |
| promote_cost_factor | The cost to promote the unit leader. | `promote_cost_factor = 0.5` | Percentual. |  | 1.5 |
| reassignment_duration_factor | The length of the reassignment penalty. | `reassignment_duration_factor = 0.5` | Percentual. |  | 1.5 |
| river_crossing_factor | The effects of the river crossing penalty. | `river_crossing_factor = 0.5` | Percentual. |  | 1.5 |
| sickness_chance | The chance for the unit leader to get sick. | `sickness_chance = 0.5` | Percentual. |  | 1.5 |
| skill_bonus_factor | The bonus the unit leader receives from their skillset. | `skill_bonus_factor = 0.5` | Percentual. |  | 1.5 |
| trait_<trait>_xp_gain_factor | Modifies the experience gain towards the specified trait. | `trait_infantry_leader_xp_gain_factor = 0.5` | Percentual. |  | 1.11 |
| terrain_trait_xp_gain_factor | Modifies the experience gain towards all terrain traits (With the type of either basic_terrain_trait or assignable_terrain_trait). | `terrain_trait_xp_gain_factor = 0.5` | Percentual. |  | 1.5 |
| wounded_chance_factor | The chance for the unit leader to get wounded. | `wounded_chance_factor = 0.5` | Percentual. |  | 1.5 |
| shore_bombardment_bonus | Modifies the penalty given by the shore bombardment on divisions. | `shore_bombardment_bonus = 0.5` | Percentual. | Can apply to both army and navy leaders. | 1.5 |

### Scientists scope <a id="Scientists_scope"></a>

Scientist-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| female_random_scientist_chance | The chance of spawn female scientist | `female_random_scientist_chance = 0.05` | Percentual. |  | 1.15 |
| scientist_breakthrough_bonus_factor | Modifiers scientist breakthrough bonus for special projects | `scientist_breakthrough_bonus_factor = -0.25` | Percentual. |  | 1.15 |
| scientist_research_bonus_factor | Modifiers scientist research bonus for special projects | `scientist_research_bonus_factor = 0.15` | Percentual. |  | 1.15 |
| scientist_xp_gain_factor | Modifiers scientist gain xp | `scientist_xp_gain_factor = 0.02` | Percentual. |  | 1.15 |

### Strategic region scope <a id="Strategic_region_scope"></a>

This is limited to static modifiers defined for weather.

Strategic region-scoped modifiers:

| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| air_accidents | Base chance for an air accident to happen. | `air_accidents = 0.3` | Flat. |  | 1.0 |
| air_detection | Base chance for air detection. | `air_detection = -0.1` | Flat. |  | 1.0 |
| naval_strike | Base efficiency for naval strikes. | `naval_strike = -0.1` | Flat. |  | 1.0 |
| navy_casualty_on_sink | Modifies the casualties when ships are sunk in this region. | `navy_casualty_on_sink = -0.1` | Percentual. |  | 1.6 |
| navy_casualty_on_hit | Modifies the casualties when ships are damaged in this region. | `navy_casualty_on_hit = -0.1` | Percentual. |  | 1.6 |

<!-- kit:begin id="weather-statics" at="section:Strategic_region_scope" -->
**Kit addition** The static modifiers that vanilla marks `# on Region` in `common/modifiers/00_static_modifiers.txt` are `weather_rain_light`, `weather_rain_heavy`, `weather_snow`, `weather_blizzard`, `weather_sandstorm` and `weather_arctic_water`. They use far more modifiers than the five listed above: `air_mission_efficiency`, `air_bombing_targetting`, `carrier_traffic`, `local_org_regain`, `naval_detection`, `naval_hit_chance`, `naval_retreat_speed`, `naval_speed_factor`, `org_loss_when_moving`, `positioning`, `supply_factor`, `supply_consumption_factor`, `truck_attrition_factor`, `army_attack_speed_factor`, `naval_attrition` and others. The ones marked `# on Province` (`weather_mud`, `weather_extreme_cold`, `weather_very_cold`, `weather_very_hot`, `weather_extreme_hot`, `weather_ground_snow_medium`, `weather_ground_snow_high`, `flooded`) use land modifiers such as `army_attack_factor`, `army_speed_factor` and `attrition`. [vanilla-confirmed 1.19.3]
<!-- kit:end id="weather-statics" -->

## Notes and references <a id="Notes_and_references"></a>

**^** **a:** A few modifiers, such as consumer_goods_factor, instead get added in a multiplicative fashion.[1] What this means is that, for example, `consumer_goods_factor = 0.1` and `consumer_goods_factor = 0.2` as separate ideas don't sum up to a 0.3 bonus, but instead multiply the consumer goods by `(1+0.1)(1+0.2)=1.1\cdot 1.2=1.32`, resulting in a 32% increase instead of 30%.

1. ↑ Developer Diary | Small Features #1, 1.13 developer diary.

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [List of modifiers](<list_of_modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on_actions.md>) • [Data structures](<data_structures.md>) • [Flags](<data_structures.md#Flags>) • [Event targets](<data_structures.md#Event_targets>) • [Country tag aliases](<data_structures.md#Country_tag_aliases>) • [Variables](<data_structures.md#Variables>) • [Arrays](<data_structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement_modding.md>) • [AI](<ai_modding.md>) • [AI focuses](<ai_focuses.md>) • [Autonomous states](<autonomy_state_modding.md>) • [Balances of power](<balance_of_power_modding.md>) • [Bookmarks/Scenarios](<bookmark_modding.md>) • [Game rules](<bookmark_modding.md#Game_rules>) • [Buildings](<building_modding.md>) • [Characters and traits](<character_modding.md>) • [Cosmetic tags](<cosmetic_tag_modding.md>) • [Countries](<country_creation.md>) • [Divisions](<division_modding.md>) • [Decisions](<decision_modding.md>) • [Doctrines](<doctrine_modding.md>) • [Equipment](<equipment_modding.md>) • [Events](<event_modding.md>) • [Factions](<faction_modding.md>) • [Ideas](<idea_modding.md>) • [Ideologies](<ideology_modding.md>) • [Military industrial organizations](<military_industrial_organization_modding.md>) • [National focuses](<national_focus_modding.md>) • [Resources](<resources_modding.md>) • [Scripted GUI](<scripted_gui_modding.md>) • [Technologies and doctrines](<technology_modding.md>) • [Units](<unit_modding.md>)
- **Map**: [Map](<map_modding.md>) • [States](<state_modding.md>) • [Supply areas](<supply_areas_modding.md>) • [Strategic regions](<strategic_region_modding.md>)
- **Graphical**: [Interface](<interface_modding.md>) • [Graphical assets](<graphical_asset_modding.md>) • [Entities](<entity_modding.md>) • [Posteffects](<posteffect_modding.md>) • [Particles](<particle_modding.md>) • [Fonts](<font_modding.md>)
- **Cosmetic**: [Portraits](<portrait_modding.md>) • [Namelists](<namelist_modding.md>) • [Music](<music_modding.md>) • [Sound](<sound_modding.md>)
- **Other**: [Console commands](<console_commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod_structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection_modding.md>) • [Defines additions](<defines_additions.md>) • [Game rule modding](<game_rule_modding.md>) • [Intelligence operation modding](<intelligence_operation_modding.md>) • [Map mode modding](<map_mode_modding.md>) • [Occupation and resistance modding](<occupation_and_resistance_modding.md>) • [Peace conference modding](<peace_conference_modding.md>) • [Raid modding](<raid_modding.md>) • [Script constant modding](<script_constant_modding.md>) • [Special project modding](<special_project_modding.md>)
