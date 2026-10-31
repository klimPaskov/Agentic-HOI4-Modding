# Decision modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Decision modding", revision 103880, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="103880" sources="common/decisions/ common/wargoals/ dlc/ common/defines/00_graphics.lua documentation/effects_documentation.md documentation/dynamic_variables_documentation.md documentation/console_commands_documentation.md hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `common/decisions/_documentation.md`, all 88 decision files (4,148 decisions) and 57 category files (597 categories) in `common/decisions/`, the decision effects, triggers and dynamic variables in `documentation/`, the colour define in `common/defines/00_graphics.lua`, and message strings in `hoi4.exe`.
- Kit blocks added: gate semantics and vanilla gating habits, the `state_target` key name, key usage counts, timer notes, mission facts with the related effects and triggers, `war_with_*` keys, highlight colour indexes, category keys.
- Errors found in the wiki text: the DLC name "One Step Back" (should be "No Step Back"), the wargoal `puppet_focus_wargoal` (should be `puppet_wargoal_focus`) and the trigger `has_command_power` (should be `command_power`); highlight colours are indexes into a 15 entry define, not 0 to 3, and an unset colour is probably "no highlight"; `visible` is written in 315 of 443 vanilla missions although the wiki says it does nothing there; the state selector is `state_target` in vanilla and `state_trigger` in the documentation.
- Gaps left: `war_with_on_timeout` and `war_with_target_on_complete` are real tokens that no vanilla file uses, and the meaning of `name`, `desc`, `cosmetic_tag` and category `custom_icon` is inferred from usage only. `BHR_category`, `QAT_category`, `find_resources` and `develop_infrastructure` are placeholder names in the wiki examples.
<!-- kit:end id="review" -->

## Table of contents

- [Basic creation](#Basic_creation)
- [Arguments for decisions and categories](#Arguments_for_decisions_and_categories)
  - [Triggers](#Triggers)
  - [Icon](#Icon)
  - [Priority](#Priority)
  - [State highlighting](#State_highlighting)
  - [Province Highlighting](#Province_Highlighting)
- [Arguments for categories](#Arguments_for_categories)
  - [Picture](#Picture)
  - [Visibility when empty](#Visibility_when_empty)
  - [Map area](#Map_area)
  - [Scripted GUI](#Scripted_GUI)
- [Category examples](#Category_examples)
- [Arguments for decisions](#Arguments_for_decisions)
  - [Effects on selection](#Effects_on_selection)
  - [Decision reappearing](#Decision_reappearing)
  - [Decision cost](#Decision_cost)
  - [Timer upon selection](#Timer_upon_selection)
  - [AI](#AI)
  - [Warning for war](#Warning_for_war)
  - [Fixed random seed](#Fixed_random_seed)
- [Decision examples](#Decision_examples)
- [Missions](#Missions)
  - [Mission example](#Mission_example)
- [Targeted decisions](#Targeted_decisions)
  - [Checking for target](#Checking_for_target)
    - [Triggers overview](#Triggers_overview)
  - [Warning for war](#Warning_for_war_2)
  - [Additional note](#Additional_note)
  - [Targeted decision example](#Targeted_decision_example)
- [State targeted decisions](#State_targeted_decisions)
  - [Example](#Example)

---

Decisions and missions represent actions that the player can or must take, each one stored within a category. Decisions themselves are defined within `/Hearts of Iron IV/common/decisions/*.txt` files, while categories are defined within `/Hearts of Iron IV/common/decisions/categories/*.txt`. While it's typical to put the country's tag within the filename, it is actually irrelevant: files can take on any filename and there will be no difference in how they will be read.

## Basic creation <a id="Basic_creation"></a>

Each decision must be stored within a category. Decision categories are defined within any `/Hearts of Iron IV/common/decisions/categories/*.txt` file. An incredibly basic decision category definition looks like the following:

```text
my_decision_category = {
}
```

This will create the `my_decision_category` category, which can be used within decisions.

Afterwards, decisions can be created for that category in any `/Hearts of Iron IV/common/decisions/*.txt` file. Decisions are assigned to a category by putting them within that category's block, encompassed with the curly brackets, as in the following example:

```text
my_decision_category = {
    my_decision_1 = {
    }
    my_decision_2 = {
    }
}
```

This will create the `my_decision_1` and `my_decision_2` decisions, with the default icon and no effect, and assign them to the `my_decision_category` category.

A decision's name according to the currently-turned on language can be defined in any [localisation](<localisation.md>) file, taking the decision's name as key, and the decision's name with _desc added in the end as the name for the localisation key for the description. As an example, the localisation for these decisions for the English language will look like the following within any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file:

```yaml
l_english:
 my_decision_category: "My decision category"
 my_decision_category_desc: "My decision category's description"
 my_decision_1: "My decision"
 my_decision_1_desc: "My decision's description"
 my_decision_2: "My decision without a description"
```

## Arguments for decisions and categories <a id="Arguments_for_decisions_and_categories"></a>

The following arguments can be used in either decisions or decision categories, usually with similar effect.

### Triggers <a id="Triggers"></a>

Usually, it is desirable to restrict the decision so that it might not always be possible to take, such as restricting it to a certain country. In order to do that, there are several [trigger](<triggers.md>) blocks, serving different purposes. A decision will only be available or visible if the corresponding conditions are met in both the category and the decision.

`allowed` is a trigger block that checks only at the game's start or when loading a save, primarily used to restrict a decision to a country (As `tag = BHR` or `original_tag = POL`) and/or a DLC (As `has_dlc = "One Step Back"`). If a decision's or a category's allowed is unfulfilled, it will never appear unless it becomes true on the save being reloaded or decisions themselves being reloaded. If left out, assumes to be always allowed. **This only checks once!**

```text
allowed = {
    original_tag = BHR
}
```

`visible` is a trigger block that continuously checks every frame if allowed was met, required to make the decision or the entire category be visible in the decision selection screen. In case for targeted decisions, both FROM and ROOT can be checked here, but using target_trigger is recommended when possible for optimisation purposes. It is preferable to put country or DLC checks into allowed instead. **Does nothing for missions!**

```text
visible = {
    is_subject = no
}
```

`available` is a trigger block that continuously checks every frame if visible was met, required to be possible to actually take the decisions. If false, the decision (or, in case of categories, decisions within) will remain visible (unless set otherwise), but will be greyed out and be impossible to complete. This is applied on top of the political power cost. Applied differently for missions.

```text
available = {
    has_war = yes
}
```

<!-- kit:begin id="decision-gates" at="section:Triggers" -->
**Kit addition** Gate semantics, from `common/decisions/_documentation.md`. All rows: [docs] `common/decisions/_documentation.md`.

| Block | THIS and FROM | When checked | Purpose |
| --- | --- | --- | --- |
| `allowed` | THIS = country | once per game at start, or when a save is loaded | drops decisions a country can never have, usually with `original_tag = XXX`; important for performance on targeted decisions |
| `visible` | THIS = country; FROM = target country or state when targeted | on every interface refresh, if `allowed` was true | whether the decision is listed; can get expensive on targeted decisions |
| `available` | the same as `visible` | on every interface refresh, if `allowed` and `visible` were true | whether a listed decision can be taken now; no condition here should be impossible to meet |
| `target_root_trigger` | THIS = country | once a day (one of the 24 hourly ticks, depending on the country), if `allowed` was true | cheap pre-check of the acting country; should be a subset of `visible` |
| `target_trigger` | THIS = country; FROM = target country or state | once a day for each state or country in the world, if `allowed` and `target_root_trigger` were true | picks the targets; each match creates its own decision entry; should be a subset of `visible` |

- In targeted decisions THIS (ROOT) is the country that takes the decision and FROM is the target, in `visible`, `available` and `target_trigger`. [docs] `common/decisions/_documentation.md`.
- Vanilla gates with `allowed`: 2,513 of 4,148 decisions have one. 1,588 test `original_tag`, 298 test `tag`, 211 are empty and 96 are `allowed = { always = no }`, the pattern for decisions that only appear through an activation effect. [vanilla-confirmed 1.19.3] `common/decisions/`.
- Categories follow the same habit: 582 of 597 have `allowed`, and 386 of those test `original_tag` (212 with only that test, 161 together with `has_dlc`). Country categories are gated with `allowed = { original_tag = X }`. [vanilla-confirmed 1.19.3] `common/decisions/categories/`.
- The effects documentation says `activate_mission` and `activate_targeted_decision` ignore the normal trigger conditions of what they activate. [docs] `documentation/effects_documentation.md`.
- Vanilla pairs `allowed = { always = no }` with an activation effect, with the comment "Activated from effect" (for example in `common/decisions/JAP.txt`). [vanilla-confirmed 1.19.3] `common/decisions/`.
- The `has_dlc` example in the `allowed` text above uses a DLC name that does not exist. The DLC is called "No Step Back" (`dlc/dlc034_no_step_back/dlc034.dlc`; about 950 vanilla lines write `has_dlc = "No Step Back"`), and no vanilla file contains "One Step Back". [vanilla-confirmed 1.19.3]
- The documentation also names a `state_trigger` key; see the note on state targeted decisions below for what vanilla writes instead. [docs] `common/decisions/_documentation.md`.
<!-- kit:end id="decision-gates" -->

### Icon <a id="Icon"></a>

The icon is the small picture displayed to the left of decision's or category's name. Icons use sprites, defined in any `/Hearts of Iron IV/interface/*.gfx` file, by default in `decisions.gfx`. Within a decision or a category, it is set with `icon = icon_name`.
Note that the game automatically inserts either `GFX_decision_` or a `GFX_decision_category_`, depending on whether it's in a decision or a category. As such, the example with icon_name will make it use the `GFX_decision_icon_name` sprite for decisions and the `GFX_decision_category_icon_name` for categories, or, other way around, to use `GFX_decision_sprite_name` in a decision, it should have `icon = sprite_name`.
However, `icon = GFX_decision_icon_name` will also work, as the game will check the spriteType with the exact same name as well. Overall, it's to the developer's discretion whether to include `GFX_decision_`/`GFX_decision_category_` in the icon or not. Additionally, you can use triggers inside of the icon definition when it is a decision, as follows:

```text
icon = {
    key = GFX_decision_my_icon_one
    trigger = {
        has_country_flag = USE_ICON_ONE
    }
}

icon = GFX_decision_my_icon_two
```

### Priority <a id="Priority"></a>

Priority is used to change the order in which decisions or categories are displayed from top to bottom, with a higher priority being closer to the top. By default, a decision has the priority of 1. Decision priority can be set in a short form for a static value or in a long form, similar to [ai_will_do](#AI) formatting.
In short form, the following code will set a decision or category to have the priority value of 10: `priority = 10`
In long form, the following code will have a priority value of 13 for POL and 3 for other countries:

```text
priority = {
	base = 3
	modifier = {
		add = 10
		tag = POL
	}
}
```

### State highlighting <a id="State_highlighting"></a>

A decision or all decisions within a category can be set to highlight a state or several with an outline when hovering over it in the selection menu. This is the code required to do that:

```text
highlight_states = {
    highlight_state_targets = {
        state = 123
        state = 321
    }
    highlight_color_while_active = 3
    highlight_color_before_active = 2
}
```

`highlight_state_targets` selects a specific state or several that will be highlighted. If the state is unknown, then `highlight_states_trigger` can be used as a trigger block instead, evaluated for every state on the map.

`highlight_color_before_active` is the colour that the state highlighting will have before selecting the decision, from 0 to 3. If not set, it will default to a white outline.

`highlight_color_while_active` is the colour that the state highlighting will have after selecting the decision during the timer before it gets removed, from 0 to 3. If not set, it will default to a white outline.

<!-- kit:begin id="decision-highlight-colours" at="section:State_highlighting" -->
**Kit correction** `highlight_color_before_active` and `highlight_color_while_active` are indexes into the `BORDER_COLOR_CUSTOM_HIGHLIGHTS` list in `common/defines/00_graphics.lua`. The list has 15 entries (0 to 14), not four. [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua`.

| Index | Meaning in the define's comment |
| --- | --- |
| 0 | mouse hover |
| 1 | bad, while active |
| 2 | good, while active |
| 3 | bad, while passive |
| 4 | good, while passive |
| 5 and 6 | controlled and neutral positive, not ours and neutral negative |
| 7 to 12 | construction targets: valid, invalid and foreign, primary then secondary |
| 13 and 14 | faction theater colours |

All rows: [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua`.

- The wiki says an unset colour is a white outline. The error text in `hoi4.exe` says the value should be -1 for no highlight, "the default if not specified", or an index into that list. Treat an unset colour as no highlight. [unverified] (string in `hoi4.exe`).
- Vanilla values: `highlight_color_while_active` is 1 (21 uses), 2 (21) or 3 (2); `highlight_color_before_active` is 3 (20) or 2 (1). [vanilla-confirmed 1.19.3] `common/decisions/`.
- Inside `highlight_states` blocks vanilla uses `highlight_state_targets` 751 times and `highlight_states_trigger` 101 times (one in a category). [vanilla-confirmed 1.19.3] `common/decisions/`, `common/decisions/categories/`.
<!-- kit:end id="decision-highlight-colours" -->

### Province Highlighting <a id="Province_Highlighting"></a>

In addition to highlighting states, it is also possible to highlight individual provinces since patch 'Stella Pollaris': 1.13.6. This is the code required to do that:

```text
highlight_states = {
    highlight_state_targets = { state = 123 }
    highlight_provinces = { 123 213 321 232 }
}
```

With `highlight_provinces = { ... }` being the effect that stores the individual provinces to be highlighted.

<!-- kit:begin id="decision-highlight-provinces" at="section:Province_Highlighting" -->
**Kit addition** `highlight_provinces` is used 13 times in vanilla. Two decisions (`common/decisions/HOL.txt`, `common/decisions/IRQ.txt`) add `highlight_only_provinces = yes` next to it, which the wiki does not mention; the token exists in `hoi4.exe`, and the likely meaning is that only the listed provinces are outlined and not the whole state. [vanilla-confirmed 1.19.3] for the usage, [unverified] for the meaning.

```text
highlight_states = {
    highlight_state_targets = { state = 7 }
    highlight_provinces = { 9498 391 11456 6241 }
    highlight_only_provinces = yes
}
```
<!-- kit:end id="decision-highlight-provinces" -->

## Arguments for categories <a id="Arguments_for_categories"></a>

These can only be used within categories and cannot be used in separate decisions.

### Picture <a id="Picture"></a>

A decision category can have a picture defined in addition to its regular icon. A picture will show up to the left of the category's description, shifting it to the left. Pictures use sprites, defined in any `/Hearts of Iron IV/interface/*.gfx` file, by default in `decisions.gfx`. A sprite with the name of `GFX_decision_category_picture` can be set as the category's picture with `picture = GFX_decision_category_picture`. **A category must have a description defined in localisation for the picture to appear.**

### Visibility when empty <a id="Visibility_when_empty"></a>

By default, a decision category is invisible unless there's at least one visible decision within. This isn't always helpful, as the category may display information vital for the player in its description. To override that, you can add a line consisting of `visible_when_empty = yes` within the decision category.

### Map area <a id="Map_area"></a>

A decision category can be assigned a map area, which will show up in the top of the decision list similarly to a decision. Clicking on the button will move the camera to the specified state or states, while setting the zoom level to the set amount. This is recommended to do in decision categories containing [decisions targeted towards states](#State_targeted_decisions). A map area definition looks like the following:

```text
on_map_area = {
    state = 123
    name = my_localisation_key
    zoom = 850
    target_root_trigger = {
        tag = ENG
    }
}
```

`state` sets a singular state that's used as the centre of the area where the camera will move. If the map area is to be dynamic, then formatting similar to targeted decisions can be used, with `targets`, `target_array`, and `target_trigger` being available and mixable.
`name` is the [localisation](<localisation.md>) key that will be used as the name of the pseudo-decision that moves the camera to the map area.
`zoom` is the zoom level for the map area, set in the amount of pixels off the ground, meaning that a lower value results in it being zoomed in more. For comparison, by default, the player can change the camera zoom between 50[1] and 3000[2].
Additionally, each of the trigger blocks defined for decisions and categories (aside from `available`) can go inside of `on_map_area`, such as `target_root_trigger`.

An example map_area with a dynamic target trigger:

```text
on_map_area = {
    target_array = controlled_states
    name = occupied_states_map_area
    zoom = 150
    target_trigger = {
        FROM = {
            NOT = { is_owned_by = ROOT }
        }
    }
}
```

### Scripted GUI <a id="Scripted_GUI"></a>

A decision category can be set to have a scripted graphical user interface container within the category, showing up below the description. The scripted GUI in question must have the decision_category context type for this to work. This is set with `scripted_gui = my_scripted_gui`. See details on the [dedicated page for scripted GUI](<scripted-gui-modding.md>).

## Category examples <a id="Category_examples"></a>

```text
POL_my_category = {
    allowed = {
        tag = POL
    }
    priority = 10
    picture = GFX_decision_category_picture
    icon = POL_category
    visible_when_empty = yes
    scripted_gui = POL_scripted_gui
}
```

```text
my_map_category = {
    visible = {
        has_completed_focus = my_focus
    }
    icon = my_map
    highlight_states = {
        highlight_states_trigger = {
            is_owned_by = ROOT
            is_capital = yes
        }
    }
    on_map_area = {
        state = 123
        targets = { capital }
        zoom = 350
    }
}
```

<!-- kit:begin id="decision-category-vanilla" at="section:Category_examples" -->
**Kit addition** Category keys in vanilla 1.19.3 (597 categories in 57 files of `common/decisions/categories/`). Counts are categories that use the key. All rows: [vanilla-confirmed 1.19.3] `common/decisions/categories/`.

| Key | Categories | Notes |
| --- | --- | --- |
| `allowed` | 582 | see the gate note above |
| `icon` | 556 | |
| `visible` | 436 | |
| `priority` | 436 | |
| `picture` | 252 | |
| `visible_when_empty` | 185 | 143 write `no`, 42 write `yes` |
| `on_map_area` | 39 | 55 blocks; every block has `name` and `zoom`; `state` in 43, `target_array` in 24, `target_trigger` in 16, `target_root_trigger` in 9 and `targets` in 9 |
| `scripted_gui` | 17 | |
| `available` | 12 | |
| `custom_icon` | 9 | 24 blocks, each with `tag`, `value`, `desc` and `visible` |
| `visibility_type` | 3 | `map_and_decisions_view` twice, `always` once |
| `highlight_states` | 1 | |

- `visibility_type` and `custom_icon` are not described on this page or in `common/decisions/_documentation.md`. In `custom_icon`, `value` and `desc` hold localisation keys and `tag` names a country flag; that reading comes from the usage in `BUL_decision_categories.txt` and `HOL_decision_categories.txt` only. [unverified]
- 14 vanilla categories contain no decision, for example `BRA_propaganda_campaigns` and `USA_war_measures`. [vanilla-confirmed 1.19.3] `common/decisions/`.
- The `targets = { capital }` line in the wiki's map category example has no vanilla precedent: `targets` holds country tags, state ids and the word `host`. Use `state`, `target_array` or `target_trigger` for a dynamic map area. [unverified]
<!-- kit:end id="decision-category-vanilla" -->

## Arguments for decisions <a id="Arguments_for_decisions"></a>

These can only be used within decisions and cannot be used in categories.

<!-- kit:begin id="decision-keys-vanilla" at="section:Arguments_for_decisions" -->
**Kit addition** Decision keys in vanilla 1.19.3. Counts are decisions that use the key (4,148 decisions in 88 files). All rows: [vanilla-confirmed 1.19.3] `common/decisions/`.

| Key | Decisions | Files | Values seen |
| --- | --- | --- | --- |
| `targets` | 280 | 38 | country tags, state ids (bare or as `state = N`, 118 entries), and `host` (10 uses, all in `NOR.txt`) |
| `target_array` | 179 | 27 | `ROOT.core_states` 19, `ROOT.allies` 14, `subjects` 13, `ROOT.subjects` 9, `exiles` 8, `global.is_chinese_warlord` 8 |
| `targets_dynamic` | 51 | 8 | always `yes` |
| `target_non_existing` | 11 | 7 | always `yes` |
| `state_target` | 278 | 47 | see the note on state targeted decisions |
| `on_map_mode` | 528 | 52 | `map_only` 267, `map_and_decisions_view` 167, `decision_view_only` 94 |
| `highlight_states` | 856 | 43 | |
| `activation` | 382 | 43 | 371 of them in missions |
| `days_mission_timeout` | 443 | 46 | number, script constant or variable |
| `timeout_effect` | 436 | 46 | |
| `is_good` | 432 | 48 | `no` 327, `yes` 105 |
| `selectable_mission` | 66 | 12 | `no` 54, `yes` 12 |
| `fixed_random_seed` | 102 | 13 | `no` 98, `yes` 4 |
| `targeted_modifier` | 37 | 9 | |
| `name` | 71 | 12 | a localisation key, often shared by several decisions |
| `desc` | 21 | 1 | a localisation key |
| `cosmetic_tag` and `cosmetic_ideology` | 21 each | 2 | missions in `ITA.txt` and `SOV.txt` |

- `name` and `desc` replace the localisation key a decision would otherwise take from its id, and `cosmetic_tag` with `cosmetic_ideology` pick the flag shown on a mission. That reading comes from the usage (for example `ENG_trade_unions_demand_minister_appointment_1` through `_5` all use one `name`) and was not tested. [unverified]
<!-- kit:end id="decision-keys-vanilla" -->

### Effects on selection <a id="Effects_on_selection"></a>

`complete_effect` is the block of [effects](<effects.md>) that gets executed immediately when the decision is selected (Starting the timer if it has one).

```text
complete_effect = {
    annex_country = { target = QAT }
}
```

### Decision reappearing <a id="Decision_reappearing"></a>

By default, a decision reappears on the very next day after being taken. In order to increase the cooldown in days, `days_re_enable = 123` can be used to put in more days in the cooldown.

In order to make the decision disappear forever upon being completed, the `fire_only_once = yes` line of code will ensure that, making the decision only be possible to fire once per country.

### Decision cost <a id="Decision_cost"></a>

In order to assign a political power cost to a decision, the `cost = <int>` argument is used. The cost can be assigned a [variable](<data-structures.md>). As an example of a decision which is assigned a cost of 50 political power:

```text
find_resources = {
    develop_infrastructure = {
        cost = 50
        available = {
            has_manpower > 499
        }
        complete_effect = {
            random_owned_state = {
                 add_building_construction = { type = infrastructure level = 2 instant_build = yes }
            }
            add_manpower = -500
        }
    }
}
```

Alternatively, a decision can also take a custom localisation string as the cost. This is done with the following:

```text
custom_cost_trigger = {
    <triggers>
}
custom_cost_text = <localisation key>
```

If custom_cost_trigger is fulfilled, then <localisation key> will be used for localisation, otherwise, <localisation key>_blocked will be. <localisation key>_tooltip will be used when hovering over the cost. Using the example of the following:

```text
custom_cost_trigger = {
    command_power > 14
}
custom_cost_text = decision_cost_CP_15
```

The localisation file will have the following:

```yaml
l_english:
 decision_cost_CP_15: "£command_power  §Y15§!"
 decision_cost_CP_15_blocked: "£command_power  §R15§!"
 decision_cost_CP_15_tooltip: "It costs £command_power  §Y15§! to take the decision"
```

In order to show icons, [text icons](<localisation.md#Text_icons>) are used.
**A custom cost will not actually cost anything**, and what you set it to cost will have to be subtracted within the `complete_effect` of the decision, preferably as a hidden effect.

As the custom cost can't be used in conjunction with the regular cost, if it includes political power, the AI will not be aware that it should save up an amount of it before taking the decision. This can be remidified with `ai_hint_pp_cost = 100`: this attribute will make the AI think that the decision will use 100 political power regardless of whether it does or not, making sure it will save up that much before trying to use it. This must be a constant amount rather than being a variable.

<!-- kit:begin id="decision-cost-notes" at="section:Decision_cost" -->
**Kit addition** Cost keys in vanilla 1.19.3. All counts: [vanilla-confirmed 1.19.3] `common/decisions/`.

- `cost` is set in 2,920 decisions: 2,554 integers, 10 script constants and 356 variable names.
- `custom_cost_trigger` and `custom_cost_text` are always used together (368 decisions each, 38 files). The `_blocked` suffix described above exists in vanilla localisation, for example `decision_cost_50_convoy_25_pp_blocked` in `localisation/english/aat_tooltips_l_english.yml`.
- `ai_hint_pp_cost` is set in 72 decisions.
- The console command `easy_decisions` makes every decision with `days_remove` take one day to be removed and removes all costs and cost triggers, which helps when testing. [docs] `documentation/console_commands_documentation.md`.
<!-- kit:end id="decision-cost-notes" -->

### Timer upon selection <a id="Timer_upon_selection"></a>

In order to add a timer between the decision being selected and some of its effects applying, `days_remove = 123` is used to define the amount of days. If set to `-1`, the decision will never be removed by the timer running out, although additional trigger blocks can remove it.

As for defining the effects that would be executed when the timer ends, `remove_effect = { ... }` is used as an effect block. Note that `complete_effect = { ... }` is when the decision is selected starting the timer, rather than when the timer ends. In other words, this timer appears after the decision was completed and stays there until the decision is removed. Additionally, `remove_trigger = { ... }` is used to instantly remove the decision once the triggers within are met for the country, also firing the `remove_effect = { ... }` block.

Additionally, it is possible to make the decision apply [modifiers](<modifiers.md>) during the timer's duration, with the `modifier = { ... }` providing a modifier block. [Similarly to ideas](<idea-modding.md#Modifiers>), `targeted_modifier = { ... }` also exists as a way to apply [targeted modifiers](<modifiers.md#Targeted_modifiers>), in the same formatting with `tag = BHR` setting the target, such as the following example:

```text
targeted_modifier = {
    tag = ENG
    attack_bonus_against = 0.1
    defense_bonus_against = -0.15
}
```

In order to make the timer cancel early without providing the effects, `visible = { ... }` does not work by default.
Instead, `cancel_trigger = { ... }` is used as a trigger block. Upon it being evaluated as true, the decision timer ends without `remove_effect = { ... }` being executed. `cancel_if_not_visible = yes`, false by default, serves as an easy way to add visible's triggers into the `cancel_trigger = { ... }` block.
Upon the decision being cancelled, `cancel_effect = { ... }` is an effect block that gets executed. This can be useful as a way to reverse the effects applied within the complete effect.

<!-- kit:begin id="decision-timer-notes" at="section:Timer_upon_selection" -->
**Kit addition** Timer keys in vanilla 1.19.3 (4,148 decisions). All counts: [vanilla-confirmed 1.19.3] `common/decisions/`.

- `days_remove` is set in 2,124 decisions: 1,771 integers (19 of them `-1`), 20 script constants such as `@DAYS_REMOVE_INFILTRATE_STATE`, and 333 variable names (89 written `name?default`). 17 of the 19 `-1` decisions also have a `remove_trigger` or `cancel_trigger`, so the decision ends on a condition and not on time.
- Every one of the 928 decisions with a non-empty `modifier` block also has `days_remove` or `days_mission_timeout`. The 109 decisions that have neither carry an empty `modifier = {}`. `hoi4.exe` has the message "Decision scripted with modifier, but no days_remove duration. ID: %s", so give every decision that has a `modifier` a timer. [unverified] (string in `hoi4.exe`).
- `cancel_if_not_visible` is set in 392 decisions (375 `yes`, 17 `no`). `cancel_trigger` is in 634, `cancel_effect` in 402, `remove_effect` in 2,063 and `remove_trigger` in 25.
- `days_re_enable` is set in 402 decisions; 123 write `0`. It also takes a variable, for example `SOV_default_propaganda_campaign_cooldown`.
<!-- kit:end id="decision-timer-notes" -->

### AI <a id="AI"></a>

*Main article: [AI modding § AI will do](<ai-modding.md>)*

The chance for AI to pick a decision is decided by the `ai_will_do = { ... }` block within a decision, which is a [MTTH block](<ai-modding.md#MTTH_blocks>). **By default, a decision will never be chosen by AI,** and that block is required to make AI choose it.

As a [MTTH block](<ai-modding.md#MTTH_blocks>), the structure consists of `factor = 10` or `base = 10` to choose the initial value and `modifier = { ... }` as trigger blocks assigning `add`/`factor`/`base` in the order. For example, the following will make the decision be never chosen by AI, unless the country is at war with ITA, in which case it has 10 weight:

```text
ai_will_do = {
    base = 0
    modifier = {
        add = 10
        has_war_with = ITA
    }
}
```

### Warning for war <a id="Warning_for_war"></a>

If your decision leads to a nation declaring war on another nation, there are several arguments that can be used to inform the targeted nation that a war is coming, as well as alert the AI to begin moving troops onto the border:
`war_with_on_remove = TAG` will make the game assume that the decision, within its `remove_effect` will declare war on the specified country, making it prepare when the timer starts.
`war_with_on_complete = TAG` will make the game assume that the decision, within its `complete_effect` will declare war on the specified country, making it prepare when the decision becomes available.

These arguments do not work for targeted decisions; see [Targeted Decisions: Warning for War](#Warning_for_war_2).

<!-- kit:begin id="decision-war-with-keys" at="section:Warning_for_war" -->
**Kit addition** The `war_with_*` family. All six names below exist as tokens in `hoi4.exe`; a `war_with_on_add` form does not exist in any vanilla script or in `hoi4.exe`. Vanilla counts are for `common/decisions/`. [vanilla-confirmed 1.19.3] for the counts, [unverified] for the `hoi4.exe` tokens.

| Key | Value | Vanilla use |
| --- | --- | --- |
| `war_with_on_complete` | tag | 2 decisions, both in `CZE.txt` (`HUN` and `AUS`) |
| `war_with_on_remove` | tag; may repeat | 7 decisions in 5 files (`FIN.txt`, `INS.txt`, `JAP.txt`, `PRC.txt`, `SLO.txt`); one in `PRC.txt` lists three tags |
| `war_with_on_timeout` | tag | none |
| `war_with_target_on_complete` | `yes` | none |
| `war_with_target_on_remove` | `yes` | 5 decisions in `JAP.txt`, `USA.txt` and `WTT_border_conflicts.txt` |
| `war_with_target_on_timeout` | `yes` | 6 missions in `JAP.txt` and `WTT_border_conflicts.txt` |

- The two names with no vanilla use (`war_with_on_timeout`, `war_with_target_on_complete`) appear in the wiki examples on this page. They are real tokens, but untested, so check the tooltip in game before relying on them. [unverified]
- Vanilla missions that warn a target of a coming war use `war_with_target_on_timeout = yes` together with `allowed = { always = no }` and activation by effect, for example `JAP_border_conflict_warning_SOV` in `JAP.txt`. [vanilla-confirmed 1.19.3] `common/decisions/JAP.txt`.
<!-- kit:end id="decision-war-with-keys" -->

### Fixed random seed <a id="Fixed_random_seed"></a>

Decisions, by default, use a fixed random seed. What this means is that such scopes as [random_list](<effects.md>) or [random_owned_controlled_state](<scopes.md>) will pick the same thing each time that the decision is used, making a choice when the game starts. `fixed_random_seed = no` will make sure that the random seed is dynamic, making it possible for a different outcome to happen.

## Decision examples <a id="Decision_examples"></a>

QAT_category and BHR_category are assumed to already have been created within any `/Hearts of Iron IV/common/decisions/categories/*.txt` file.

```text
QAT_category = {
    QAT_example = {
        allowed = {
            tag = QAT
        }
        icon = QAT_example      #For GFX_decision_QAT_example
        fire_only_once = yes
        days_remove = 100
        war_with_on_remove = BHR
        modifier = {
            training_time_factor = -0.3
        }
        remove_effect = {
            create_wargoal = {
                target = BHR
                type = puppet_focus_wargoal
            }
        }
        cancel_trigger = {
            OMA = {
                is_subject_of = BHR
            }
        }
        cancel_effect = {
            BHR = {
                puppet = ROOT
            }
        }
    }
}
```

```text
BHR_category = {
    BHR_example = {
        allowed = {
            tag = BHR
        }
        visible = {
            has_war_with = QAT
        }
        available = {
            QAT = {
                surrender_progress > 0.5
            }
        }
        icon = GFX_decision_BHR_example
        priority = 10
        days_re_enable = 200
        custom_cost_trigger = {
            has_command_power > 14
        }
        custom_cost_text = decision_cost_CP_15
        war_with_on_complete = OMA
        fixed_random_seed = no
        complete_effect = {
            hidden_effect = {
                add_command_power = -15
            }
            annex_country = { target = QAT }
            random = {
                chance = 50
                OMA = { load_oob = "OMA_prepared" }
            }
            declare_war_on = {
                target = OMA
                type = annex_everything
            }
        }
    }
}
```

<!-- kit:begin id="decision-example-corrections" at="section:Decision_examples" -->
**Kit correction** Errors in the two decision examples below. Sources: `common/wargoals/00_invasion.txt`, `common/decisions/`, `documentation/triggers_documentation.md`.

| In the example | In 1.19.3 |
| --- | --- |
| `type = puppet_focus_wargoal` in `QAT_example` | the wargoal is `puppet_wargoal_focus`; the name written in the example exists nowhere in the game files |
| `has_command_power > 14` in `BHR_example` | no trigger called `has_command_power` exists; the trigger is `command_power > 14`, which vanilla writes 13 times in `custom_cost_trigger` blocks |

All rows: [vanilla-confirmed 1.19.3] and, for `command_power`, [docs].

- `QAT_category` and `BHR_category` are placeholders for categories you define in `common/decisions/categories/`, and `find_resources` (category) and `develop_infrastructure` (decision) in the cost example are invented names. No vanilla category or decision uses any of the four names. [vanilla-confirmed 1.19.3] `common/decisions/`.
<!-- kit:end id="decision-example-corrections" -->

## Missions <a id="Missions"></a>

Missions are another type of decisions, activated when the triggers are true and requiring the player to do an action in order for the mission to have a positive outcome. These mostly use the same attributes as regular decisions, but there are some crucial differences. In particular:

- `days_mission_timeout = 123` is the amount of days that the mission will last for and is the attribute that turns a decision into a mission.
- `timeout_effect = { ... }` are the effects that will be executed for the country if the timer runs out or is uninterrupted.
- `available = { ... }` decides on triggers that make the mission possible to select, executing `complete_effect`. **Defaults to always being true, making it disappear instantly**.
- `selectable_mission = yes`, if set, turns the mission into one that where the player must select the button. If unset or set to false, then the complete effect will fire as soon as `available` is true.
- `activation = { ... }` decides on triggers that must be met for the decision to appear, assuming `allowed` was true on the game's start. This is checked daily. **`visible = { ... }` does nothing and shouldn't be used in missions.**
  The `activate_mission = mission_name` [effect](<effects.md>) can bypass both `allowed` and `activation`, and it's usually better-optimised to use it to make the decision appear instead of relying on it being done automatically.
- `is_good = yes` changes the tooltips shown to the player on a non-selectable mission. By default or if set to false, the tooltip states that the `available` will complete the mission, calling `timeout_effect` the effects if it's not completed. If set to true, `complete_effect` will instead change to "Effects when failed". This is purely graphical and may be used to better communicate to the player whether they should seek to complete the prerequisites or to avoid them being true.
- `war_with_on_timeout = TAG` will make the game assume that the mission, within its `timeout_effect = { ... }` will declare war on the specified country. This is used to make the AI prepare for a declaration of war and amass its troops on the border. This will also grant a notification to the target and all of its allies that a wargoal is being justified.

Other attributes, such as `cancel_trigger` or `cancel_effect` generally may be used inside of missions and should work how they do outside of them.

<!-- kit:begin id="decision-missions-vanilla" at="section:Missions" -->
**Kit addition** Missions in vanilla 1.19.3: a mission is a decision with `days_mission_timeout`, and there are 443 of them in 46 files. All counts: [vanilla-confirmed 1.19.3] `common/decisions/`.

- 441 have `available`, 435 have `timeout_effect`, 402 set `is_good`, 371 have `activation`, 258 have `allowed`, 163 have `complete_effect` and 65 set `selectable_mission`.
- The wiki says `visible` does nothing in missions. Vanilla still writes a `visible` block in 315 of the 443 missions (36 of them empty). `common/decisions/_documentation.md` does not say that `visible` is ignored for missions, so this stays open. [unverified]
- Only 3 missions carry a `cost`: `TSR_pay_for_support_from_warlord_PP`, `_manpower` and `_equipment` in `CHI_warlord_decisions.txt`, all with `selectable_mission = yes`. `hoi4.exe` has the message "Cost for normal missions not implemented. ID: %s", so do not put `cost` on a mission that is not selectable. [unverified] (string in `hoi4.exe`).

Documented effects, triggers and dynamic variables for decisions and missions. All rows: [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`, `documentation/dynamic_variables_documentation.md`. Uses are counted over `events/`, `common/` and `history/` ([vanilla-confirmed 1.19.3]).

| Name | What the documentation says | Vanilla uses |
| --- | --- | --- |
| `activate_decision = <id>` | activates the decision for the scoped country | 46 |
| `activate_mission = <id>` | activates a mission and ignores its normal trigger conditions; cannot activate a mission that is already active | 572 |
| `activate_targeted_decision = { target = <TAG or state> decision = <id> }` | activates a targeted decision or mission and ignores its trigger conditions, cooldown and `fire_only_once`; cannot activate it while it is active in the interface | 190 |
| `remove_decision = <id>` | removes an active decision without running `remove_effect` or starting a cooldown; ignores `fire_only_once` | 7 |
| `remove_mission = <id>` | removes a mission without running its complete or timeout effects | 51 |
| `remove_targeted_decision = { target = <TAG> decision = <id> }` | removes a targeted decision or mission | 36 |
| `remove_decision_on_cooldown = <id>` | removes a decision from cooldown so that it can be reactivated or removed | 11 |
| `add_days_remove = { decision = <id> days = N }` | adds days to the `days_remove` value of a decision | 1 |
| `add_days_mission_timeout = { mission = <id> days = N }` | adds days to a mission's timeout | 180 |
| `unlock_decision_tooltip = <id>` or a block with `decision`, `show_effect_tooltip`, `show_modifiers` | shows what a decision does; both show flags default to `no` | 688 |
| `unlock_decision_category_tooltip`, `activate_mission_tooltip` | tooltip helpers for a category and for a mission | 133 and 16 |
| `has_decision = <id>`, `has_active_mission = <id>` | country triggers for an active decision and an active mission | 107 and 293 |
| `days_mission_timeout@<mission id>`, `days_decision_timeout@<decision id>` | country dynamic variables: days left on a timed mission or decision, for example `days_mission_timeout@GER_mefo_bills_mission` | used in `GER.txt` |
<!-- kit:end id="decision-missions-vanilla" -->

### Mission example <a id="Mission_example"></a>

```text
my_mission = {
    activation = {
        has_civil_war = yes
    }
    available = {
        has_civil_war = no
        has_war = yes
    }
    cancel_trigger = {
        has_war = no
    }
    icon = mission_icon     # For GFX_decision_mission_icon
    is_good = yes
    war_with_on_timeout = SOV
    days_mission_timeout = 100
    selectable_mission = yes
    complete_effect = {
        add_ideas = my_idea
    }
    timeout_effect = {
        declare_war_on = {
            target = SOV
            type = annex_everything
        }
    }
}
```

## Targeted decisions <a id="Targeted_decisions"></a>

In addition to regular decisions that are taken by the country towards that same country, it is possible to make a decision be targeted towards a different country or group of countries. In that case, the decision will clone itself for each country that it gets targeted towards, putting the flag of the country in the bottom right of the decision's icon. The targeted country will be possible to reference in code using [FROM](<scopes.md>), while ROOT is still the country that gets the decision. **Despite what the names imply, FROM is the target of the decision rather than the country doing it.**
`fire_only_once`, in this case, will make the decision fire only once per each target country: a decision targeted towards BLR will not disappear if a decision of the same ID targered towards LIT gets completed.
Missions, as well as regular decisions, can be made targeted.

A decision becomes targeted if any way to check for a target is added within the decision:

### Checking for target <a id="Checking_for_target"></a>

There are several ways to limit the selection of targets. If any of these three is present in the decision, it will be marked as targeted.

The primary way to limit the selection to a select few countries is `targets = { TAG TAG }`. In that case, if you want the game to check every country with that original tag (including civil war rebellions and other types of dynamic countries), then `targets_dynamic = yes` line of code will ensure that the game will check more than the country that the country tag truly belongs to. Additionally, by default, it's impossible to target a non-existing country. The `target_non_existing = yes` argument can be used to remove that restriction.

Additionally, it is possible to use [arrays](<data-structures.md>) to limit a selection with `target_array = array_name`, where the array must be assigned to the country. [You can see a list of arrays automatically generated by the game here.](<data-structures.md#Game_arrays>)

Together with any of the previous two ways or without them, `target_trigger = { ... }` is a trigger block evaluated daily for both FROM and ROOT, if `target_root_trigger` is evaluated as true.

For targeted decisions, `target_root_trigger` is also possible to use, as a trigger block that continuously checks every day if allowed was met, required to make the decision or the entire category be visible in the decision selection screen. **This checks only ROOT**, being executed before `target_trigger = { ... }` is. This exists for optimisation purposes, as it takes much less time to check the condition for one country daily than for every combination of countries.

#### Triggers overview <a id="Triggers_overview"></a>

- `allowed = { ... }` checks the country that should get this decision and only checks upon the game's start or when reloading decisions such as by loading a savegame. If false, the decision is permamently disabled.
- `target_root_trigger = { ... }` checks the country the country that should get this decision, every day. If false, the decision will not appear until the next daily check. **Despite only checking one country, this still makes the decision targeted.**
- `target_trigger = { ... }` checks any countries (or states) that meet `targets = { ... }` and `target_array = array_name`, if they're present. In here, ROOT (default scope) is the country that gets the decision and FROM is the potential target of the decision. This is checked daily, making the decision not appear until the next day's check if false. Putting this automatically makes the decision targeted.
- `visible = { ... }` and `available = { ... }` are checked every tick. If the decision is targeted, then FROM is checked alongside ROOT, otherwise only ROOT is checked.

### Warning for war <a id="Warning_for_war_2"></a>

The regular arguments of `war_with_on_` do not work if using FROM as a target. Instead, there are alternatives for targeted decisions specifically:

`war_with_target_on_complete = yes` - Equivalent to `war_with_on_complete = FROM`
`war_with_target_on_remove = yes` - Equivalent to `war_with_on_remove = FROM`
`war_with_target_on_timeout = yes` - Equivalent to `war_with_on_timeout = FROM`

<!-- kit:begin id="decision-war-with-target" at="section:Warning_for_war_2" -->
**Kit note** The three `war_with_target_on_*` keys take only `yes` in vanilla (11 uses in `common/decisions/`), and they stand for FROM, the target of the decision. The table of all six `war_with_*` keys is in the note on the first "Warning for war" section above. [vanilla-confirmed 1.19.3] `common/decisions/`.
<!-- kit:end id="decision-war-with-target" -->

### Additional note <a id="Additional_note"></a>

Similarly to missions, the `activate_targeted_decision = { target = TAG decision = my_decision }` effect exists. If possible, it is recommended to use this effect instead of letting it automatically activate, making it never allowed. For instance, if the targeted decision activates by being at war with a country, [on_war_relation_added in on_actions](<on-actions.md>) can be used to activate it instead of using `target_array = enemies`.

### Targeted decision example <a id="Targeted_decision_example"></a>

```text
my_targeted_decision = {
    target_root_trigger = {
        has_completed_focus = my_focus
    }
    targets = { BHR QAT SAU OMA YEM IRQ SYR LEB ISR PAL }
    targets_dynamic = yes
    target_trigger = {
        FROM = {
            has_idea = my_idea
        }
    }
    icon = my_icon
    cost = 20
    war_with_target_on_complete = yes
    complete_effect = {
        create_wargoal = {
            target = FROM
            type = annex_everything
        }
    }
}
```

## State targeted decisions <a id="State_targeted_decisions"></a>

If the decision has `state_target = yes` then, instead, it'll be targeted towards a state. Possible values are: yes, no, any, any_owned_state, any_controlled_state, continent_key (europe, africa, north_america...). This will only have an effect if no 'targets' are specified, else this should be set to 'any' (or 'yes') if targets are used. Unless omitted or set to "no", makes the decision a state targeted decision. Which states will be checked depends on value:
\- any (or yes): will check every state in the game against the 'target_trigger'.
\- any_owned_state: will check every state owned by the country. This is equivalent to adding 'is_owned_by = ROOT' in the target_trigger.
\- any_controlled_state: will check every state controlled by the country. This is equivalent to adding 'is_controlled_by = ROOT' in the target_trigger.
\- continent_key (europe, africa, north_america...): will check every state in the continent. This is equivalent to adding 'is_on_continent = xxx' in the target_trigger.

When using explicit targets such as via `targets = {}` or `target_array = yes` only `state_target = yes/any` will work the others will produce an error

Targeting still works the same way, with it having FROM as a state scope instead. `targets` becomes `targets = { 123 321 }` or, in case of one state total, `targets = { state = 123 }` can be used as well.

Decisions targeted towards states will have the icon appear over the states while the decision menu is open. To prevent confusion, a [map area](#Map_area) can be added to the decision category.

Additionally, The argument `on_map_mode` will determine where the targeted decisions appear in.

`on_map_mode = map_only` will make the targeted decisions only appear on the map.
`on_map_mode = decision_view_only` will make the targeted decisions only appear in the decisions menu.
`on_map_mode = map_and_decisions_view` will make the targeted decisions appear on both the map and the decisions menu.

<!-- kit:begin id="decision-state-target-key" at="section:State_targeted_decisions" -->
**Kit correction** `common/decisions/_documentation.md` calls the state selector `state_trigger` (values `yes`, `no`, `any`, `any_owned_state`, `any_controlled_state` or a continent key such as `europe`). Vanilla never writes `state_trigger`; all 278 state targeted decisions write `state_target`. Use `state_target`. [docs] for the documented name, [vanilla-confirmed 1.19.3] `common/decisions/` for the usage.

- `state_target` values in vanilla: `yes` 210, `any_controlled_state` 34, `any_owned_state` 19, and continent keys 15 (`asia`, `middle_east` and `africa` 3 each, `south_america` and `europe` 2 each, `north_america` and `australia` 1 each). `any` is never written. [vanilla-confirmed 1.19.3] `common/decisions/`.
- The 138 vanilla decisions that combine `state_target` with `targets` or `target_array` all use `state_target = yes`. The 140 that use `yes`, `any_owned_state`, `any_controlled_state` or a continent key without explicit targets all have a `target_trigger`. This matches the documentation: the selector only matters without explicit targets, and with them it must be `any` or `yes`. [vanilla-confirmed 1.19.3] and [docs] `common/decisions/_documentation.md`.
- The documentation says `any_owned_state` is the faster equal of `owner = ROOT` in the `target_trigger`, `any_controlled_state` of `is_controlled_by = ROOT`, and a continent key of `is_on_continent = <key>`. [docs] `common/decisions/_documentation.md`.
- Both `state_trigger` and `state_target` exist as tokens in `hoi4.exe`, so whether the documented name is accepted as an alias is unknown. [unverified]
- `on_map_mode` is set in 528 decisions; the values are listed in the key table in the "Arguments for decisions" section. [vanilla-confirmed 1.19.3] `common/decisions/`.
<!-- kit:end id="decision-state-target-key" -->

### Example <a id="Example"></a>

```text
my_state_targeted_decision = {
    state_target = yes
    target_root_trigger = {
        has_completed_focus = my_focus
    }
    target_array = GER.core_states
    target_trigger = {
        FROM = {
            is_owned_by = ROOT
        }
    }
    on_map_mode = map_and_decisions_view
    icon = my_icon
    cost = 20
    complete_effect = {
        FROM = {
            remove_core_of = GER
        }
    }
}
```

1. ↑ `CAMERA_MIN_HEIGHT = 50.0` in [Defines](<defines.md>)
2. ↑ `CAMERA_MAX_HEIGHT = 3000.0` in [Defines](<defines.md>)

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list-of-modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on-actions.md>) • [Data structures](<data-structures.md>) • [Flags](<data-structures.md#Flags>) • [Event targets](<data-structures.md#Event_targets>) • [Country tag aliases](<data-structures.md#Country_tag_aliases>) • [Variables](<data-structures.md#Variables>) • [Arrays](<data-structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement-modding.md>) • [AI](<ai-modding.md>) • [AI focuses](<ai-focuses.md>) • [Autonomous states](<autonomy-state-modding.md>) • [Balances of power](<balance-of-power-modding.md>) • [Bookmarks/Scenarios](<bookmark-modding.md>) • [Game rules](<bookmark-modding.md#Game_rules>) • [Buildings](<building-modding.md>) • [Characters and traits](<character-modding.md>) • [Cosmetic tags](<cosmetic-tag-modding.md>) • [Countries](<country-creation.md>) • [Divisions](<division-modding.md>) • [Doctrines](<doctrine-modding.md>) • [Equipment](<equipment-modding.md>) • [Events](<event-modding.md>) • [Factions](<faction-modding.md>) • [Ideas](<idea-modding.md>) • [Ideologies](<ideology-modding.md>) • [Military industrial organizations](<military-industrial-organization-modding.md>) • [National focuses](<national-focus-modding.md>) • [Resources](<resources-modding.md>) • [Scripted GUI](<scripted-gui-modding.md>) • [Technologies and doctrines](<technology-modding.md>) • [Units](<unit-modding.md>)
- **Map**: [Map](<map-modding.md>) • [States](<state-modding.md>) • [Supply areas](<supply-areas-modding.md>) • [Strategic regions](<strategic-region-modding.md>)
- **Graphical**: [Interface](<interface-modding.md>) • [Graphical assets](<graphical-asset-modding.md>) • [Entities](<entity-modding.md>) • [Posteffects](<posteffect-modding.md>) • [Particles](<particle-modding.md>) • [Fonts](<font-modding.md>)
- **Cosmetic**: [Portraits](<portrait-modding.md>) • [Namelists](<namelist-modding.md>) • [Music](<music-modding.md>) • [Sound](<sound-modding.md>)
- **Other**: [Console commands](<console-commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod-structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection-modding.md>) • [Game rule modding](<game-rule-modding.md>) • [Intelligence operation modding](<intelligence-operation-modding.md>) • [Map mode modding](<map-mode-modding.md>) • [Occupation and resistance modding](<occupation-and-resistance-modding.md>) • [Peace conference modding](<peace-conference-modding.md>) • [Raid modding](<raid-modding.md>) • [Script constant modding](<script-constant-modding.md>) • [Special project modding](<special-project-modding.md>)
