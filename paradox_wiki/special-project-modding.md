# Special project modding

*Kit page: written by the Agentic HOI4 Modding Kit from the Hearts of Iron IV 1.19.3.0 game files. The wiki has no page for this topic. CC BY-SA 3.0 (see LICENSE.txt).*
<!-- kit:page -->

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" sources="common/special_projects/ common/scientist_traits/ common/characters/_documentation.md common/script_constants/ common/buildings/00_buildings.txt common/defines/00_defines.lua common/ai_strategy/default.txt common/on_actions/12_wuw_on_actions.txt documentation/effects_documentation.md documentation/triggers_documentation.md documentation/modifiers_documentation.md documentation/dynamic_variables_documentation.md documentation/console_commands_documentation.md interface/special_projects/ localisation/english/special_projects_l_english.yml" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Written from: the four documentation files and every vanilla file in `common/special_projects/` (49 projects, 82 generic and 87 unique prototype rewards, 4 specializations, 13 tags), `common/scientist_traits/` (21 traits), the 102 vanilla scientist characters, the facility buildings, the `NProject` defines, script constants, localisation, interface GFX and the effect, trigger, modifier, dynamic-variable and console documentation.
Also checked: use counts in `common/`, `events/` and `history/`, and (read-only string search) whether `hoi4.exe` contains the keys on which the documentation files disagree.
Gaps left: reward selection details, the AI's choice between reward options, the scope of `fire_only_once` and the real default skill level of a scientist are not settled by any game file; they are tagged `[unverified]`. No game was run.
<!-- kit:end id="review" -->

## Table of contents

- [Overview](#Overview)
  - [Project lifecycle](#Project_lifecycle)
- [Files and loading](#Files_and_loading)
- [Specializations and facilities](#Specializations_and_facilities)
  - [Specialization definition](#Specialization_definition)
  - [Facility buildings](#Facility_buildings)
  - [Technologies and breakthrough points](#Technologies_and_breakthrough)
  - [Project tags](#Project_tags)
- [Project definition](#Project_definition)
  - [Scopes inside a project](#Project_scopes)
  - [Output blocks](#Output_blocks)
- [Prototype rewards](#Prototype_rewards)
- [Scientists](#Scientists)
  - [Scientist role](#Scientist_role)
  - [Levels and experience](#Levels_and_experience)
  - [Scientist traits](#Scientist_traits)
- [Script interface](#Script_interface)
  - [Effects](#Effects)
  - [Triggers](#Triggers)
  - [Scopes and variables](#Scopes_and_variables)
  - [Modifiers](#Modifiers)
  - [Script constants](#Script_constants)
  - [On action and event](#On_action_and_event)
  - [Defines](#Defines)
- [AI](#AI)
- [Localisation](#Localisation)
- [GFX](#GFX)
- [DLC gating in vanilla](#DLC_gating)
- [Console commands](#Console_commands)
- [Minimal example](#Minimal_example)
- [Silent failures and traps](#Traps)
- [See also](#See_also)

---

Special projects are long research programs run by a scientist inside a facility building. Each project is one node of a tree per specialization. Researching it costs breakthrough points, resources and time. While it runs it rolls random prototype rewards, and when it completes it unlocks equipment, modules, sub-units, buildings or plain effects. Raids can damage the facility and its project (see [Raid modding](<raid-modding.md>)). 34 of the 49 vanilla projects are gated by `has_dlc` in `allowed` (28 need Gotterdammerung); 15 are not [vanilla-confirmed 1.19.3] `common/special_projects/projects/*.txt`.

Evidence tags used on this page: `[docs]` = the game's own documentation, `[vanilla-confirmed 1.19.3]` = seen in vanilla script, `[unverified]` = plausible but not confirmed. File names in tags are relative to the game folder; `sp/` stands for `common/special_projects/`.

## Overview <a id="Overview"></a>

The parts and where each one is defined:

| Part | Defined in | Role |
| --- | --- | --- |
| Specialization | `sp/specialization/*.txt` | Category of projects, of facilities and of scientist skills. Vanilla: `specialization_nuclear`, `specialization_naval`, `specialization_air`, `specialization_land`. |
| Facility | a building in `common/buildings/` with `specialization = { ... }` | Province building where one project runs. |
| Project | `sp/projects/*.txt` | One node of a specialization's tree. |
| Prototype reward | `sp/prototype_rewards/*.txt` (generic) or inline in a project (unique) | Random event drawn after each prototype iteration. |
| Scientist | `scientist = { }` role on a character | Speeds the project up and gains experience. |
| Scientist trait | `common/scientist_traits/*.txt` | Speed and experience modifiers for the attached project. |
| Breakthrough points | country resource, one pool per specialization | Spent to start a project. |

All rows: [docs] `sp/projects/documentation.md`, `sp/specialization/documentation.md`, `sp/prototype_rewards/documentation.md`, `common/scientist_traits/_documentation.md`, `documentation/effects_documentation.md` (breakthrough points); vanilla specialization ids [vanilla-confirmed 1.19.3] `sp/specialization/specializations.txt`.

### Project lifecycle <a id="Project_lifecycle"></a>

1. **Establishing.** Runs every time the project is started or restarted; cancelling inside it throws the progress away.
2. **Initial research.** Runs once per project. Cancelling keeps the progress.
3. **Prototyping.** Repeated iterations. Each iteration adds `complexity` to a 0 to 100 progress bar and may draw a prototype reward. At 100 the project is complete and `project_output` fires.

[docs] `sp/projects/documentation.md`. `prototype_time` is the length in days of each phase, and the progress ceiling is `PROTOTYPE_PHASE_MAX_PROGRESS = 100` [docs] `sp/projects/documentation.md`, [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` (`NProject`).

Other engine rules from the `NProject` defines [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`:

- A cancelled project needs `DEFAULT_STOP_PROJECT_DAYS = 10` days to stop. The UI says breakthrough points are refunded when a project is cancelled before one iteration has finished (`ONGOING_PROJECT_BREAKTHROUGH_REFUND` in `localisation/english/special_projects_l_english.yml`).
- Research speed has a floor of 0.2 for supply (`MINIMUM_PROJECT_SPEED_FACTOR_FROM_SUPPLY`, full speed at supply 3.0 in the province) and a floor of 0.2 for resource shortage.
- The attached scientist gains `DEFAULT_PROJECT_COMPLETION_SCIENTIST_EXPERIENCE_GAIN = 192` experience when a project completes.
- When a facility is captured, `PROJECT_LOSS_FACTOR_ON_CAPTURE = 0.2` of the project's progress is lost, and the captor receives `PROJECT_CAPTURE_GAIN_RATIO = 0.2` of the difference to its own project (`PROJECT_CAPTURE_DIMINISHING_RETURN = 0.6` shrinks repeat gains).

## Files and loading <a id="Files_and_loading"></a>

| Path | Holds | Top-level shape | Vanilla |
| --- | --- | --- | --- |
| `sp/projects/*.txt` | projects | one `<project_id> = { }` per project, no wrapper | air 8, land 9, naval 19, nuclear 6, radar 1, rocket 6 |
| `sp/prototype_rewards/*.txt` | generic rewards | one `<reward_id> = { }` each, no wrapper | air 17, land 29, naval 20, nuclear 11, rocket 5 |
| `sp/specialization/*.txt` | specializations | one `<specialization_id> = { }` each | `specializations.txt`, 4 |
| `sp/project_tags/*.txt` | project tags | one block `project_tags = { tag tag ... }` | `tags.txt`, 13 tags |
| `common/scientist_traits/*.txt` | scientist traits | one `<trait_id> = { }` each | `00_traits.txt`, 21 |
| `common/characters/*.txt` | scientist role | `scientist = { }` inside a character | 102 characters |
| `common/buildings/*.txt` | facility buildings | normal building definitions | `00_buildings.txt`, 4 facilities |
| `common/script_constants/special_project_constants.txt` | constants used by projects | see [Script constants](#Script_constants) | 6 constant groups |
| `common/scripted_effects/SP_scripted_effects.txt` | variant-creation helper effects | scripted effects | 6 |
| `localisation/<language>/special_projects_l_english.yml` | text | yml | 1448 lines |
| `interface/special_projects.gfx`, `interface/special_projects/project.gfx` | sprites | spriteTypes | see [GFX](#GFX) |
| `interface/unitleaderwindow.gfx` | scientist trait icons | spriteTypes | 21 trait sprites |

All rows: [vanilla-confirmed 1.19.3] for the paths and counts. Folder roles are also stated in [docs] `sp/projects/documentation.md`, `sp/prototype_rewards/documentation.md`, `sp/specialization/documentation.md`, `common/scientist_traits/_documentation.md`.

- Vanilla splits projects by area (one file each) and generic rewards by area (one file each); nothing in the documentation requires that split [vanilla-confirmed 1.19.3].
- `@name = value` script variables at the top of a reward file are file-local: `generic_air_`, `generic_land_` and `generic_naval_prototype_rewards.txt` each define `@base_reward_weight = 2` and `@reward_weight_factor_theme = 0.25` [vanilla-confirmed 1.19.3] `sp/prototype_rewards/generic_*_prototype_rewards.txt`.
- The documentation says nothing about two files defining the same id. To replace a vanilla project, reward or trait, follow the general override rule on [Mod structure](<mod-structure.md>) and keep the same relative path [unverified].

**Do not use `sp/special_projects_documentation.md` as the schema.** It is an early design draft. It shows `special_project_type`, `prototype_cost`, `threshold_min`, `threshold_max`, an `effects` block inside options, `main_scientist`, `every_scientist_in_facility`, `facility_model` and `special_project_sub_specializations`. None of these appears in any vanilla file, and none of them is a string in `hoi4.exe` (read-only search). The shipped schema is in the three `documentation.md` files, and the vanilla files follow it [vanilla-confirmed 1.19.3] `sp/**/*.txt`; that the engine ignores the draft keys is [unverified].

## Specializations and facilities <a id="Specializations_and_facilities"></a>

### Specialization definition <a id="Specialization_definition"></a>

All rows: [docs] `sp/specialization/documentation.md`. Counts: [vanilla-confirmed 1.19.3] `sp/specialization/specializations.txt` (4 specializations).

| Key | Value | Default | Vanilla |
| --- | --- | --- | --- |
| `icon` | GFX name | `GFX_TAG_<id>`, then `GFX_<id>`, then `GFX_PLACEHOLDER_sp_specialization_icon` | 0 set it; `GFX_specialization_nuclear` and the three others exist and are found by the default |
| `blueprint_image` | GFX name, background of the project while it runs | `GFX_TAG_<id>_blueprint`, then `GFX_<id>_blueprint`, then `GFX_PLACEHOLDER_sp_blueprint` | 1 (nuclear: `GFX_generic_plane_blueprint_background`) |
| `program_background` | GFX name, card background of the facility program | `GFX_TAG_<id>_program_item`, then (the doc repeats the TAG form by mistake, presumably `GFX_<id>_program_item`), then `GFX_tiled_plain_bg` | 4 (`"GFX_sp_facility_card_bg"`) |
| `color` | `{ R G B }`, 0 to 255 | grey | 4 |

Vanilla colours are nuclear `{ 255 255 0 }`, naval `{ 0 0 255 }`, air `{ 255 0 0 }`, land `{ 0 255 0 }`, which read as RGB although the documentation labels the order `<b, r, g>` [vanilla-confirmed 1.19.3] `sp/specialization/specializations.txt`.

The specialization id is localised by `<id>` and, in vanilla, `<id>_short` (`specialization_nuclear` is "Nuclear Research", `specialization_nuclear_short` is "Physics") [vanilla-confirmed 1.19.3] `localisation/english/special_projects_l_english.yml`; a `TAG_<id>` key is tried first [docs].

### Facility buildings <a id="Facility_buildings"></a>

The documentation requires one building per specialization, carrying `specialization = <id>` [docs] `sp/specialization/documentation.md`. Vanilla writes it with braces and gives each facility the same shape [vanilla-confirmed 1.19.3] `common/buildings/00_buildings.txt` (`naval_facility`, `nuclear_facility`, `air_facility`, `land_facility`):

```text
air_facility = {
	show_on_map = 1
	base_cost = 10000
	per_controlled_building_extra_cost = 6000
	damage_factor = 0              # not hit by normal strategic bombing
	icon_frame = 17
	value = 1
	spawn_point = special_project_facility_spawn
	specialization = { specialization_air }
	tags = { facility }
	need_supply = yes
	need_detection = yes
	detecting_intel_type = airforce
	disabled_in_dmz = yes
	only_display_if_exists = yes
	special_icon = GFX_specialization_air
	infrastructure_construction_effect = yes
	level_cap = { province_max = 1 state_max = 1 group_by = special_project_facility }
}
```

- `tags = { facility }` is what raids and `damage_building` use to find a facility (`damage_building = { tags = facility ... }`, raid target `building = { tags = facility }`) [vanilla-confirmed 1.19.3] `common/raids/air_raids.txt`, `sp/prototype_rewards/generic_nuclear_prototype_rewards.txt`.
- `spawn_point = special_project_facility_spawn` is a province spawn point with `max = 1`, and `group_by = special_project_facility` puts the four facility types in one group with a shared slot limit [vanilla-confirmed 1.19.3] `common/buildings/00_buildings.txt`. The positions come from rows named `special_project_facility_spawn` in `map/buildings.txt` (10154 rows in vanilla) [vanilla-confirmed 1.19.3]; see the Spawn point section of [Building modding](<building-modding.md#Spawn_point>).
- Facilities are placed in `history/states/*.txt` as province buildings (`1939.1.1 = { buildings = { 9448 = { air_facility = 1 } } }`, 16 state files), or built by focuses with `add_building_construction = { type = land_facility level = 1 instant_build = yes province = <id> }` (for example `common/national_focus/belgium.txt`) [vanilla-confirmed 1.19.3].
- A project unlocks a building through a technology it sets: `nuclear_reactor` carries `hide_if_missing_tech = yes` and `missing_tech_loc = { localization_key = SP_BUILDING_MISSING_PROJECT PROJECT = sp_nuclear_reactor }`, and the project's `country_effects` run `set_technology = { nuclear_reactor = 1 popup = no }` while `facility_state_effects` run `set_building_level = { type = nuclear_reactor level = 1 }` [vanilla-confirmed 1.19.3] `common/buildings/00_buildings.txt`, `sp/projects/nuclear_projects.txt`.
- Further building keys: [Building modding](<building-modding.md#Additional_arguments>).

### Technologies and breakthrough points <a id="Technologies_and_breakthrough"></a>

Technologies carry `special_project_specialization = { specialization_x ... }` (338 lines in 10 files under `common/technologies/`; air, land, naval and nuclear are used, and some technologies list two) [vanilla-confirmed 1.19.3]. The `NProject` defines and the program texts describe "basic research" by a scientist in a matching facility: a research bonus on technologies of that specialization (`BASIC_RESEARCH_TECHNOLOGY_BONUS_FACTOR = 0.02` per skill level) and daily breakthrough progress (`BREAKTHROUGH_DAILY_TECHNOLOGY_GAIN = 12` and `BREAKTHROUGH_DAILY_SCIENTIST_SKILL_GAIN = 5` hundredths of a percent) [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`, `localisation/english/special_projects_l_english.yml` (`PROGRAM_BASIC_RESEARCH*`). That basic research is what a facility without a project does is likely but not stated [unverified]. Progress `1.0` is probably one point, since the constants are `sp_breakthrough_progress` low 0.1, medium 0.25, high 0.5 and the UI shows progress as a percentage [unverified].

### Project tags <a id="Project_tags"></a>

`sp/project_tags/tags.txt` lists the known tags in one `project_tags = { }` block, and a project joins one or more with `project_tags = sp_tag_tank` or `project_tags = { sp_tag_aircraft sp_tag_jet }`. The file's own comment says tags exist to generate modifiers. Vanilla tags: `sp_tag_tank`, `sp_tag_artillery`, `sp_tag_surface_ship`, `sp_tag_submarine`, `sp_tag_nuclear_warfare`, `sp_tag_nuclear_power`, `sp_tag_aircraft`, `sp_tag_rocket`, `sp_tag_helicopter`, `sp_tag_jet`, `sp_tag_bomb`, `sp_tag_guided_bomb`, `sp_tag_radar` [vanilla-confirmed 1.19.3] `sp/project_tags/tags.txt`. All 49 projects use only these tags [vanilla-confirmed 1.19.3]. Each tag is localised by its own id ("Tank Projects") [vanilla-confirmed 1.19.3] `localisation/english/special_projects_l_english.yml`. A custom tag has to be added to `tags.txt` before a project can use it [unverified]. `project_tags` is not described in `sp/projects/documentation.md`; 49 of 49 vanilla projects use it and the key is a string in `hoi4.exe`. `sp_air_radar` repeats the key twice, which loads fine [vanilla-confirmed 1.19.3] `sp/projects/radar_projects.txt`.

## Project definition <a id="Project_definition"></a>

A project is `<project_id> = { ... }` in `sp/projects/`. Evidence for the table: [docs] `sp/projects/documentation.md` for keys, defaults and scopes; the last column is [vanilla-confirmed 1.19.3] `sp/projects/*.txt` (49 projects).

| Key | Value | Default and rules | Vanilla |
| --- | --- | --- | --- |
| `specialization` | specialization id | mandatory | 49 |
| `allowed` | trigger, country scope; only `tag`, `original_tag`, `has_dlc` | default yes. Evaluated once at startup for every country; if true, an instance of the project is created for that country | 41: 34 with `has_dlc` (one combines two DLCs in an `AND`), 7 empty blocks |
| `available` | trigger, project scope, `FROM` = country | project is greyed out while false | 45, written `FROM = { has_tech = ... }` |
| `visible` | same scope as `available` | project is hidden while false | 0 |
| `breakthrough_cost` | `specialization_x = N`, several allowed; a value may be a `{ base modifier }` block with country-scope triggers | 0 of the project's own specialization when omitted | 40, integers only (1 to 3) |
| `prototype_time` | days, at least 1 | mandatory; takes the constants of `sp_time` | 49, always a constant |
| `complexity` | number, or an `sp_complexity` constant | default `DEFAULT_COMPLEXITY = 100` (one iteration); `0` logs an error and falls back to the default | 49, always a constant |
| `resource_cost` | `resources = { steel = 6 aluminium = 6 }` | drained while researching and prototyping; a shortage slows the project; oil is not allowed | 47; steel 42, chromium 31, tungsten 23, aluminium 15, rubber 5 |
| `special_project_parent` | `{ project_id project_id }` | the project appears only when all parents are complete | 18 |
| `project_tags` | tag or `{ tag tag }` | see [Project tags](#Project_tags) | 49 |
| `narrative` | `{ name = key desc = key }` | name key `TAG_<id>` then `<id>`; desc key `TAG_<id>_desc` then `<id>_desc` | 0 |
| `icon` | GFX name | `GFX_<icon>`, then `GFX_TAG_<id>`, then `GFX_<id>`, then `GFX_PLACEHOLDER_sp_project_icon` | 21 |
| `blueprint_image` | GFX name, background while researching | overrides the specialization's | 0 |
| `ai_will_do` | weight block | default 1 | 29 (none in air or nuclear files) |
| `empty_reward_weight` | weight block (`base`, `modifier`) | default `DEFAULT_EMPTY_REWARD_WEIGHT = 1.0`; weight of "no reward" after an iteration | 5 (`base = 0.5`) |
| `project_output` | output block | effects when complete | 49 |
| `unique_prototype_rewards` | rewards only this project can draw | | 43 |
| `generic_prototype_rewards` | `{ reward_id ... }` from the generic database | | 49 |

The `sp_air_radar` project also shows the explicit-icon case: no sprite `GFX_sp_air_radar` exists, so it sets `icon = GFX_sp_nuclear_radar` [vanilla-confirmed 1.19.3] `sp/projects/radar_projects.txt`, `interface/special_projects/project.gfx`.

### Scopes inside a project <a id="Project_scopes"></a>

| Block | Scope | `FROM` | Notes |
| --- | --- | --- | --- |
| `allowed` | country | none | `tag`, `original_tag`, `has_dlc` only |
| `available`, `visible` | project | country | country triggers go inside `FROM = { }` |
| `breakthrough_cost` modifier triggers | country | | |
| `empty_reward_weight`, reward `weight` | project (`ROOT` = project) | country | also `var:facility_state`, `var:facility_province_id`, `var:scientist`, all set in these blocks |
| `ai_will_do` | project | country | see [AI](#AI) for a conflict between the docs and vanilla |
| `country_effects` | country | project | `FROM = { add_project_progress_ratio = ... }` reaches the project |
| `facility_state_effects` | state of the facility | project | `var:facility_province_id` holds the facility province id; skipped when no facility exists |
| `scientist_effects` | character (the scientist) | project | skipped when no scientist exists |
| `limit` inside `enable_*` | n/a | n/a | only `has_dlc` is accepted |

Rows: [docs] `sp/projects/documentation.md`, `sp/prototype_rewards/documentation.md`. Vanilla follows the `available`/`FROM` rule in 41 `FROM = { }` wrappers and the weight rule in `has_project_flag`, `var:scientist` and `FROM = { has_country_flag = ... }` weights [vanilla-confirmed 1.19.3] `sp/projects/*.txt`, `sp/prototype_rewards/*.txt`.

### Output blocks <a id="Output_blocks"></a>

`project_output` (when the project completes) and each option's `iteration_output` (when a reward option is taken) share one content format [docs] `sp/projects/documentation.md`.

| Key | Content | Vanilla use |
| --- | --- | --- |
| `country_effects` | normal country effects | 49 projects (`sp_naval_aip_engine` writes the block twice), 233 reward options |
| `facility_state_effects` | state-scope effects, `var:facility_province_id` | 8 projects, 11 reward options |
| `scientist_effects` | character-scope effects | 6 projects, 57 reward options |
| `enable_equipments` | list of equipment variant ids; optional `limit = { has_dlc = ... }` | 45 projects |
| `enable_equipment_modules` | list of module ids; optional `limit` | 27 projects, 2 reward options |
| `enable_subunits` | list of sub-unit ids; optional `limit` | 17 projects |
| `equipment_bonus` | `{ <equipment type> = { stat = value } }` like ideas, optional `name`, `instant = yes` | 48 reward options, 0 projects |
| `sub_unit_bonus` | same shape as a technology's sub-unit bonus | 0 (documented only) |

Rows: documented content [docs] `sp/projects/documentation.md`; counts [vanilla-confirmed 1.19.3] `sp/projects/*.txt`, `sp/prototype_rewards/*.txt`. `limit` in the three `enable_*` lists accepts only `has_dlc` [docs].

Two patterns recur in vanilla output blocks [vanilla-confirmed 1.19.3] `sp/projects/*.txt`:

- Unlocking a technology: `set_technology = { <tech> = 1 popup = no }` inside `country_effects`, wrapped in `custom_override_tooltip` or followed by `custom_effect_tooltip = { localization_key = SP_UNLOCK_TECH TECH = <tech> }`.
- Equipment bonuses in two forms: the documented `equipment_bonus = { armor = { armor_value = 0.02 } }` block next to `country_effects`, and the effect `add_equipment_bonus = { name = <loc key> bonus = { <type> = { stat = value instant = yes } } }` inside `country_effects` (125 uses). `add_equipment_bonus` also accepts `project = FROM` to take its name from the project [docs] `documentation/effects_documentation.md`.

## Prototype rewards <a id="Prototype_rewards"></a>

A reward is `<reward_id> = { ... }`. Generic rewards live in `sp/prototype_rewards/` and a project lists them in `generic_prototype_rewards`. Unique rewards sit inline in the project's `unique_prototype_rewards`, with the same format. A nameless inline block is documented as an "anonymous" reward that only effects can reach; vanilla has none [docs] `sp/projects/documentation.md`, [vanilla-confirmed 1.19.3].

Evidence for the table: [docs] `sp/prototype_rewards/documentation.md`; counts [vanilla-confirmed 1.19.3] over 82 generic and 87 unique rewards.

| Key | Value | Default and rules | Vanilla |
| --- | --- | --- | --- |
| `narrative` | `{ name desc }` | name `TAG_<id>` then `<id>`; desc `TAG_<id>_desc` then `<id>_desc`. Desc scopes: SpecialProject, Character, State, Country | 0 |
| `icon` | GFX name | `GFX_<icon>`, `GFX_TAG_<id>`, `GFX_<id>`, then `GFX_PLACEHOLDER_sp_project_picture` | 0 |
| `fire_only_once` | yes or no | default no | 169 of 169 |
| `threshold` | `{ min max }` | window of project progress in which the reward can fire; omitted means always eligible. Vanilla uses the 0 to 100 scale | 169 of 169 |
| `weight` | weight block (`base`, `modifier = { factor or add ... }`) | default `ITERATION_REWARD_DEFAULT_WEIGHT = 1.0`; `ROOT` = project, `FROM` = country, `var:facility_state`, `var:facility_province_id`, `var:scientist` | 80 of 82 generic, 87 of 87 unique |
| `allowed` | trigger | default true; the doc example is `original_tag = GER` | 0 |
| `force_reward_if_available` | yes or no | a reward flagged this way is drawn first when eligible; several flagged ones are drawn by weight | 1 (`sp_land_reward_stronghold_network_leadership_approach`) |
| `option` | repeatable, at least one | the choices | 83 generic, 181 unique |
| `option.token` | unique id inside the reward | mandatory; also the loc key of the option name | all |
| `option.default` | yes | the option taken on time-out; first option when none is flagged; flag only one | 21 options |
| `option.narrative` | `{ name }` | name key `TAG_<token>` then `<token>` | 0 |
| `option.iteration_output` | output block | see [Output blocks](#Output_blocks) | all |

Notes:

- **Window.** The doc text says the minimum is inside the window and the maximum is not ("from 0 up to and not including 60"), although its interval notation `(Min, Max]` says the opposite. Write windows so that neither reading matters, for example by not relying on the exact edge value [docs] `sp/prototype_rewards/documentation.md`.
- **Once per what.** `fire_only_once = yes` limits a reward to one firing, but the documentation does not say whether that is per project, per country or per facility [unverified].
- **Progress scale.** The old draft describes 0 to 1 thresholds; vanilla uses 0 to 100 (for example `min = 25 max = 45`) [vanilla-confirmed 1.19.3] `sp/projects/nuclear_projects.txt`.
- **Drawing a reward.** After each iteration the game weighs the eligible rewards of the project together with the empty outcome (`empty_reward_weight`) and draws one. Eligible means the progress is inside `threshold`, `allowed` is true and a `fire_only_once` reward has not fired yet. This reading comes from the weight and threshold descriptions; no document spells out the algorithm [unverified].
- **Themes.** Vanilla generic rewards reduce repeats of one theme by setting a project flag in the output (`FROM = { set_project_flag = <flag> }`) and multiplying the weight when `has_project_flag = <flag>` is true (`factor = @reward_weight_factor_theme`) [vanilla-confirmed 1.19.3] `sp/prototype_rewards/generic_land_prototype_rewards.txt`.
- **Weights.** Three nuclear generic rewards write `weight = { factor = 1.0 }` instead of `base`. It equals the default weight, but `base` is the documented key [vanilla-confirmed 1.19.3] `sp/prototype_rewards/generic_nuclear_prototype_rewards.txt`.
- **From script.** `complete_prototype_reward_option` (project scope) and the console command `sp_prototype_reward` fire a reward option directly; the effect respects `fire_only_once` and `allowed` [docs] `documentation/effects_documentation.md`, `documentation/console_commands_documentation.md`.

## Scientists <a id="Scientists"></a>

### Scientist role <a id="Scientist_role"></a>

A scientist is a character with a `scientist = { }` role. Keys [docs] `common/characters/_documentation.md`; counts over the 102 vanilla scientist characters [vanilla-confirmed 1.19.3] `common/characters/*.txt`:

| Key | Value | Default | Vanilla |
| --- | --- | --- | --- |
| `desc` | loc key | none; the Character modding page lists a bug that it does not show [unverified] | 0 |
| `traits` | `{ scientist_trait_id ... }` | none | 102 |
| `skills` | `{ specialization_x = level ... }` | the docs say every specialization starts at level 1 | 102: level 2 in 83 entries, 1 in 11, 3 in 9 |
| `visible` | trigger, `ROOT` = the character; use `owner = { ... }` for the country | yes | 23 (`owner = { has_completed_focus = ... }`) |

- Vanilla scientists carry a `large` portrait, almost always in the `army` block (`army` 101 blocks, 19 of them also with `small`; `civilian` 3; `navy` 1), and are put into a country with `recruit_character = <id>` in `history/countries/*.txt` (102 of 102; none in `common/` or `events/`) [vanilla-confirmed 1.19.3].
- Exactly one vanilla scientist lists two specializations (`SOV_igor_kurchatov`: nuclear 2 and naval 2) [vanilla-confirmed 1.19.3] `common/characters/SOV.txt`.
- `common/characters/_documentation.md` still says the traits come from the country-leader trait database until a scientist trait database exists. That database now exists (`common/scientist_traits/`), and vanilla scientists use only `scientist_trait_*` ids [docs], [vanilla-confirmed 1.19.3].
- Default skill level: the character documentation says every specialization starts at 1. Vanilla focus code, however, filters scientists with `has_scientist_level = { level > 0 ... }`, which would be pointless if everyone had level 1 [unverified].
- Wiki page: [Character modding](<character-modding.md#Scientists>).

An effect can also create or strip the role (`add_scientist_role`, `remove_scientist_role`, `generate_scientist_character`); a role made by `add_scientist_role` cannot have a `visible` trigger [docs] `documentation/effects_documentation.md`.

### Levels and experience <a id="Levels_and_experience"></a>

Levels run 0 to 5 per specialization. Values come from `NProject` in `common/defines/00_defines.lua`, names from `localisation/english/special_projects_l_english.yml` [vanilla-confirmed 1.19.3].

| Level | Name | Speed modifier on the project | XP needed to reach it from the level below |
| --- | --- | --- | --- |
| 0 | Inadequate | -100% | n/a |
| 1 | Inexperienced | -5% | 100 |
| 2 | Skilled | +5% | 100 |
| 3 | Experienced | +10% | 300 |
| 4 | Expert | +15% | 700 |
| 5 | Mastermind | +25% | 1500 |

- Experience constants for rewards: `sp_scientist_xp_gain` low 70, medium 100, high 150, very_high 200 [vanilla-confirmed 1.19.3] `common/script_constants/special_project_constants.txt`.
- Daily XP for basic research is `SCIENTIST_BASIC_RESEARCH_DAILY_XP_GAIN = 0.28`; recruiting a scientist costs 25, 50, 75 or 100 political power depending on how many are already available; a randomly generated recruit has a 35% chance of one trait; removing a scientist takes 10 days [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.
- Supportive scientists: a facility takes up to 3 (`AMOUNT_OF_SUPPORTIVE_SCIENTISTS`) at 25% effectiveness, assigning a supportive scientist from the faction costs `FACTION_ASSIGN_SCIENTIST_COST = 25` political power, and `can_assign_supportive_scientist_to_faction = specialization_x` tests for a free slot [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`, `common/ai_strategy/default.txt`.
- An injured scientist (`injure_scientist_for_days`) applies `SCIENTIST_INJURED_FACTOR = 0.0` to progress [vanilla-confirmed 1.19.3]; what factor 0.0 means in practice is not stated [unverified].

### Scientist traits <a id="Scientist_traits"></a>

A trait is `<trait_id> = { ... }` in `common/scientist_traits/`. Only modifiers that affect special projects are meaningful there [docs] `common/scientist_traits/_documentation.md`.

| Key | Value | Default | Vanilla |
| --- | --- | --- | --- |
| `name` | loc key | the trait id | 0 (only a commented example line) |
| `icon` | GFX name | `GFX_<trait id>` | 1 (`scientist_trait_genius`) |
| `modifier` | modifier block applied to the project the scientist is attached to | none | 21 |
| `specialization` | `{ specialization_x }`, restricts the trait to that specialization | all specializations | 14 |
| `available` | trigger; the country is `FROM`, `ROOT` and `PREV` | yes | 3 (`has_dlc` checks) |

Rows: [docs] `common/scientist_traits/_documentation.md`; vanilla counts [vanilla-confirmed 1.19.3] `common/scientist_traits/00_traits.txt`. Each of the 21 traits has a sprite `GFX_<trait id>` in `interface/unitleaderwindow.gfx`, and loc keys `<trait id>` and `<trait id>_desc`.

Vanilla traits [vanilla-confirmed 1.19.3] `common/scientist_traits/00_traits.txt`:

- All ids start with `scientist_trait_`; the lists below drop that prefix after the first entry. General: `scientist_trait_genius` (project speed +0.10, breakthrough bonus +0.05, research bonus +0.05), `brilliant_theorist`, `gifted_engineer`, `bright`, `fast_learner` (experience gain +0.10), `resourceful` (facility supply consumption -0.10), `schrodingers_trait` (only `custom_modifier_tooltip`).
- Air: `aircraft_specialist`, `rocketry_specialist`, `electronics_specialist`, `helicopter_expert` (Gotterdammerung), `jet_expert`, `bombs_expert` (Gotterdammerung), `guidance_systems_expert`; each adds `sp_tag_<tag>_speed_factor`.
- Land: `armored_specialist`, `artillery_specialist` (Gotterdammerung or No Step Back).
- Naval: `submarine_specialist`, `surface_ship_specialist`.
- Nuclear: `nuclear_specialist` (`specialization_nuclear_speed_factor`), `nuclear_warfare_expert`, `nuclear_power_expert`.

**Doc example trap.** The example in `common/scientist_traits/_documentation.md` uses `special_project_prototype_speed_factor = 0.5`. That modifier is not in `documentation/modifiers_documentation.md`, vanilla never uses it, and the string is not in `hoi4.exe`. The modifier that exists is `special_project_speed_factor` [docs], [vanilla-confirmed 1.19.3]; that the unknown name is silently ignored is [unverified].

## Script interface <a id="Script_interface"></a>

### Effects <a id="Effects"></a>

Parameters and scopes: [docs] `documentation/effects_documentation.md`. Use counts are lines outside comments in `common/`, `events/` and `history/` [vanilla-confirmed 1.19.3]. Wiki pages: [Effects](<effects.md#Special_Projects>), [Effects (scientists)](<effects.md#Scientists>), [Effects (project scope)](<effects.md#Special_Project_scope>).

| Effect | Scope | Form | Vanilla |
| --- | --- | --- | --- |
| `complete_special_project` | country | `= sp:id`, `= var:x`, `= PREV`, or `{ project = sp:id scientist = <char> state = <state id> iteration_output = { reward  reward = option } show_modifiers = no }` | 277 (266 in `history/countries`) |
| `add_breakthrough_points` | country | `{ specialization = <id or all> value = N }` | 6 |
| `add_breakthrough_progress` | country | `{ specialization = <id or all> value = N }`, value may be an `sp_breakthrough_progress` constant | 335 |
| `generate_scientist_character` | country | `{ portrait portrait_tag_override gender skills traits }`, all optional | 3 |
| `add_scientist_role` | country, character | character: `{ scientist = { traits skills desc } }`; country: adds `character = <id>` | 0 |
| `remove_scientist_role` | country, character | character: `= yes`; country: `{ character = <id> }` | 1 |
| `every_scientist`, `random_scientist` | country | usual iterator keys plus `tooltip`, `random_select_amount`, `include_invisible`, `display_individual_scopes` | 3 and 15 |
| `every_active_scientist`, `random_active_scientist` | country | same, only scientists assigned to a project | 0 |
| `add_scientist_xp` | character | `{ experience = N specialization = <id> }`, `experience` accepts variables | 59 |
| `add_scientist_level` | character | `{ level = N specialization = <id> }` | 15 |
| `add_scientist_trait` | character | `= <trait id>` | 2 |
| `injure_scientist_for_days` | character | `= N` | 5 |
| `add_project_progress_ratio` | project | `= <-1 to 1>`, a share of the whole project; accepts variables | 85 |
| `set_project_flag`, `clr_project_flag`, `modify_project_flag` | project | `= flag`; vanilla uses only the simple `set_project_flag = flag` form | 61, 0, 0 |
| `complete_prototype_reward_option` | project | `{ prototype_reward = id prototyp_reward_option = id show_modifiers = yes }` (the option key is spelled with the typo `prototyp_`) | 0 |
| `add_dynamic_modifier`, `remove_dynamic_modifier`, `force_update_dynamic_modifier` | project (among others) | as in other scopes | no use inside a project scope found |
| `raid_reduce_project_progress_ratio` | state, inside a raid outcome | `= 0 to 1` | 3, all in `common/raids/air_raids.txt` |

`complete_special_project` ignores unfinished parent projects, and because no facility or scientist takes part, `facility_state_effects` and `scientist_effects` of the project are not applied; the documentation names only those two as skipped [docs]. Vanilla uses it to give countries projects already finished in 1936 and 1939, with `scientist` and `state` (for example `project = sp:sp_naval_midget_submarine scientist = GER_hellmuth_walter state = 56`) [vanilla-confirmed 1.19.3] `history/countries/GER - Germany.txt`.

### Triggers <a id="Triggers"></a>

Parameters and scopes: [docs] `documentation/triggers_documentation.md`. Counts: [vanilla-confirmed 1.19.3]. Wiki pages: [Triggers (scientists)](<triggers.md#Scientists>), [Triggers (special projects)](<triggers.md#Special_projects>).

| Trigger | Scope | Form | Vanilla |
| --- | --- | --- | --- |
| `is_special_project_completed` | country | `= sp:id`, `var:x` or `PREV` | 175 |
| `is_special_project_being_researched` | country | same | 2 |
| `has_breakthrough_points` | country | `{ specialization = <id> value = N }` | 0 |
| `has_facility_specialization` | country | `= specialization_x` | 11 |
| `has_scientist_specialization` | country | `= specialization_x`, true when a scientist has level 1 or more there | 0 |
| `can_assign_supportive_scientist_to_faction` | country | `= specialization_x` | 8, AI strategies |
| `any_scientist`, `all_scientists` | country | scope into scientists; `tooltip = key` optional | 5, 0 |
| `any_active_scientist`, `all_active_scientist` | country | active scientists only | 0, 0 |
| `has_scientist_level` | character | `{ level > N specialization = <id> }`, accepts `<`, `>`, `=` | 60 |
| `is_active_scientist` | character | `= yes` or `no` (assigned to a project) | 10 |
| `is_scientist_injured` | character | `= yes` or `no` | 0 |
| `is_in_state` | character | scientists count as being in the state of their facility | see the docs example |
| `has_project_flag` | project | `= flag`, or `{ flag = f value < N days > N date > Y.M.D }` | 65 |

The documentation entries disagree with themselves in places: the heading `all_active_scientist` has an example calling `all_active_scientists`, and the examples of `is_active_scientist` and `is_scientist_injured` both write `is_scientist_active`. Use the headings; vanilla uses `is_active_scientist` [docs], [vanilla-confirmed 1.19.3] `common/factions/goals/faction_goals_short_term.txt`. `has_trait = <scientist trait>` also works in character scope for scientists (`sp/projects/land_projects.txt`) [vanilla-confirmed 1.19.3].

### Scopes and variables <a id="Scopes_and_variables"></a>

- The scope is called `SPECIAL_PROJECT`. A project is reached from country scope with the prefix `sp:`, for example `sp:sp_nuclear_bomb = { add_project_progress_ratio = 0.1 }` (187 lines in `common/` and `events/`) [docs] `documentation/effects_documentation.md`, [vanilla-confirmed 1.19.3] `events/Special_Project_Events.txt`. Wiki: [Scopes](<scopes.md>).
- Dynamic variables on the project scope: `facility_state` (State), `facility_province_id` (province id), `scientist` (Character) [docs] `documentation/dynamic_variables_documentation.md`. Vanilla uses `var:scientist = { ... }` 9 times in weights and `province = var:facility_province_id` 7 times in `damage_building`; `var:facility_state` is documented but never used [vanilla-confirmed 1.19.3] `sp/prototype_rewards/*.txt`.
- Localisation scope objects: `[SpecialProject.GetName]`, `[SpecialProject.Owner]`, `[Character.GetName]`, `[State.GetName]` [docs] `documentation/loc_objects_documentation.md`.
- The building damage helper used by reward outputs: `damage_building = { tags = facility damage = 0.15 province = var:facility_province_id }` (also `repair_speed_modifier`) [docs] `documentation/effects_documentation.md`, [vanilla-confirmed 1.19.3] `sp/prototype_rewards/generic_rocket_prototype_rewards.txt`.

### Modifiers <a id="Modifiers"></a>

Categories and formats: [docs] `documentation/modifiers_documentation.md`. Wiki: [Modifiers](<modifiers.md#Scientists_scope>).

| Modifier | Categories | Notes |
| --- | --- | --- |
| `special_project_speed_factor` | country | all project speed; vanilla uses it in scientist traits, country-leader traits, 5 idea files, 5 dynamic-modifier files and one decision file [vanilla-confirmed 1.19.3] |
| `<project_id>_speed_factor` | country, state | per project, for example `sp_nuclear_bomb_speed_factor`; the docs list all 49 ids |
| `<sp_tag>_speed_factor` | country, state | per tag, for example `sp_tag_rocket_speed_factor` |
| `<specialization_id>_speed_factor` | country, state | for example `specialization_nuclear_speed_factor` |
| `special_project_facility_supply_consumption_factor` | country | used by `scientist_trait_resourceful`, a country-leader trait and a Czechoslovak idea [vanilla-confirmed 1.19.3] |
| `scientist_xp_gain_factor` | character | traits only in vanilla |
| `scientist_research_bonus_factor` | character | technology research bonus from basic research; traits only |
| `scientist_breakthrough_bonus_factor` | character | breakthrough progress from basic research; traits only |
| `female_random_scientist_chance` | country, scientist | unused in vanilla |

The `<...>_speed_factor` family: the documentation lists project ids, the 13 tags and the 4 specialization ids as the types that generate it (66 entries) [docs]. Vanilla localises each used name with `<name>` and `<name>_tt` in `modifiers_l_english.yml` [vanilla-confirmed 1.19.3]; a modifier you add needs both keys for a clean tooltip [unverified].

### Script constants <a id="Script_constants"></a>

`common/script_constants/special_project_constants.txt` [vanilla-confirmed 1.19.3]:

| Group | Values |
| --- | --- |
| `sp_time.prototype` | short 45, medium 60, long 100, very_long 200 (days) |
| `sp_complexity` | each a `{ min max }` range of progress per iteration: small 15 to 25, medium 15 to 20, large 10 to 15, insane 5 to 10 |
| `sp_scientist_xp_gain` | low 70, medium 100, high 150, very_high 200 |
| `sp_progress.gain` / `sp_progress.loss` | low, medium, high = 0.05, 0.1, 0.15 / -0.05, -0.1, -0.15 |
| `sp_military_xp_gain` | low 15, medium 30, high 50 |
| `sp_breakthrough_progress` | low 0.1, medium 0.25, high 0.5 |

- The UI shows "gains X to Y each iteration" and "requires A to B iterations" for range constants, so a range constant gives a different gain each iteration; a plain number gives a fixed one [vanilla-confirmed 1.19.3] `localisation/english/special_projects_l_english.yml` (`SPECIAL_PROJECT_RESEARCH_TIME_MIN_MAX_TOOLTIP_*`). The draw method is [unverified].
- Prefix rule. `prototype_time`, `complexity` and the `value` of `add_breakthrough_progress` take the constant bare (`sp_time.prototype.long`), while scoped-variable positions such as `experience = constant:sp_scientist_xp_gain.low` and `add_project_progress_ratio = constant:sp_progress.gain.low` need `constant:` [docs] `common/script_constants/documentation.md`, [vanilla-confirmed 1.19.3] `sp/projects/*.txt`.
- The constants documentation example shows `sp_basic_research_time`, which does not exist in vanilla [docs] `common/script_constants/documentation.md`.

### On action and event <a id="On_action_and_event"></a>

- `on_project_completion` runs when a project completes, `ROOT` = the country, `FROM` = the project. Vanilla uses it to count Belgian projects [vanilla-confirmed 1.19.3] `common/on_actions/12_wuw_on_actions.txt`. Wiki: [On actions](<on-actions.md#Special_Projects>).
- `events/Special_Project_Events.txt` has one event, `sp_nuclear_project_events.1`, whose option adds 10% progress to `sp:sp_nuclear_bomb` [vanilla-confirmed 1.19.3].

### Defines <a id="Defines"></a>

`NProject` holds the numbers quoted above (`DEFAULT_COMPLEXITY`, `PROTOTYPE_PHASE_MAX_PROGRESS`, `SCIENTIST_SKILL_LEVEL_THRESHOLDS`, `SCIENTIST_SKILL_LEVEL_SPEED_MODIFIER`, supply and capture factors) [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. Wiki: [Defines](<defines.md#NProject>). `FACTION_ASSIGN_SCIENTIST_COST`, `AMOUNT_OF_SUPPORTIVE_SCIENTISTS` and `ASSIGN_FACILITY_TO_FACTION_INITIATIVE_COST` are in `NProject` and `NFactions`.

## AI <a id="AI"></a>

- **Project choice.** `ai_will_do` on a project; default weight 1 [docs] `sp/projects/documentation.md`. 29 projects set it: all 19 naval, all 6 rocket, 3 of 9 land and the radar project; none of the 8 air and 6 nuclear projects. Vanilla writes country triggers as `ROOT = { tag = GER }` (22 uses) and `date > 1940.1.1`, and never uses `FROM` outside comments [vanilla-confirmed 1.19.3] `sp/projects/*.txt`. The documentation says the project is `THIS` and `FROM` is the country. The two statements do not agree, so copy the vanilla `ROOT = { }` form for country checks [docs], [vanilla-confirmed 1.19.3].
- **Rewards.** The documentation describes `weight` and `empty_reward_weight` as the probability of a reward being chosen, so neither the player nor the AI picks which reward comes up; they only pick among its options [docs] `sp/prototype_rewards/documentation.md`, `sp/projects/documentation.md`.
- **Reward options.** `option.default = yes` is the option used on time-out [docs]; how the AI chooses between options is not documented. Vanilla gives no option an `ai_chance`, and the draft's per-option `ai_chance` is not used [vanilla-confirmed 1.19.3], [unverified].
- **Scientists.** Vanilla AI strategies use `type = recruit_scientist` with `id = specialization_x` and `value = 100` (4 strategies, enabled when the country has a matching facility or a free supportive slot), and `type = pp_spend_priority`, `id = supportive_scientist`, `value = 25` [vanilla-confirmed 1.19.3] `common/ai_strategy/default.txt`. These strategy types are not in `common/ai_strategy/_documentation.md`.
- The character-level `ai_will_do` of the draft is not part of the shipped scientist role [vanilla-confirmed 1.19.3] (`common/characters/_documentation.md` lists only `desc`, `traits`, `skills`, `visible`).

## Localisation <a id="Localisation"></a>

Keys from `localisation/english/special_projects_l_english.yml` [vanilla-confirmed 1.19.3]; the fallback order is from [docs] in the three `documentation.md` files. A `TAG_` prefix gives a country-specific text (vanilla: `GER_sp_nuclear_reactor` is "Uranmaschine").

| Text | Key | Notes |
| --- | --- | --- |
| Project name | `TAG_<id>`, then `<id>` | scope Country |
| Project description | `TAG_<id>_desc`, then `<id>_desc` | scopes SpecialProject, Country |
| Reward name and description | `<reward id>`, `<reward id>_desc` | the description may use `[Character.GetName]`, `[SpecialProject.GetName]`, `[State.GetName]` |
| Option name | `<token>` | `<token>_desc` appears only in the file's "old deprecated" block |
| Specialization | `<id>` and `<id>_short` | |
| Tag | `<sp_tag id>` | |
| Scientist trait | `<trait id>`, `<trait id>_desc` | |
| Project speed modifier | `<id>_speed_factor`, `<id>_speed_factor_tt` | in `modifiers_l_english.yml` |
| Unlock tooltips for buildings | `SP_UNLOCK_BUILDING` (`$BUILDING$`), `SP_UNLOCK_BUILDING_ICON_DESC` (`$BUILDING$`, `$BUILDING_DESCRIPTION$`, `$ICON_FRAME$`), `SP_BUILDING_MISSING_PROJECT` (`$PROJECT$`) | the last one is the building's `missing_tech_loc` text |
| Unlock tooltips for other things | `SP_UNLOCK_PROJECT` (`$PROJECT$`), `SP_UNLOCK_TECH` (`$TECH$`), `SP_UNLOCK_TECH_WITH_EXTRA_PROJECT`, `SP_UNLOCK_RAID` (`$RAID_TYPE$`) | used as `custom_effect_tooltip = { localization_key = SP_UNLOCK_TECH TECH = <tech> }` |
| Skill level names | `SCIENTIST_SKILL_LEVEL_NAME_0` to `_5` | engine strings, not per mod |

## GFX <a id="GFX"></a>

Sprite names and fallbacks: [docs] in the three `documentation.md` files; vanilla file locations [vanilla-confirmed 1.19.3] `interface/special_projects.gfx`, `interface/special_projects/project.gfx`, `interface/unitleaderwindow.gfx`.

| Asset | Sprite | Vanilla location | Fallback |
| --- | --- | --- | --- |
| Project icon | `icon`, else `GFX_<id>` | `gfx/interface/special_project/project_icons/<id>.dds` | `GFX_PLACEHOLDER_sp_project_icon` |
| Reward picture | `icon`, else `GFX_<reward id>` | | `GFX_PLACEHOLDER_sp_project_picture` |
| Specialization icon | `GFX_<specialization id>` (`GFX_specialization_nuclear`) | `project.gfx` | `GFX_PLACEHOLDER_sp_specialization_icon` |
| Blueprint background | `blueprint_image` | designer backgrounds such as `GFX_generic_plane_blueprint_background` | `GFX_PLACEHOLDER_sp_blueprint` |
| Facility card background | `program_background` | `GFX_sp_facility_card_bg` (2 frames) | `GFX_tiled_plain_bg` |
| Scientist trait icon | `GFX_<trait id>` | `gfx/interface/traits/scientist_traits/` | none |
| Facility on the map | building `special_icon = GFX_specialization_<x>` | `project.gfx` | |

Project sprites are plain `spriteType` entries. Graphic basics: [Graphical asset modding](<graphical-asset-modding.md#spriteType>).

## DLC gating in vanilla <a id="DLC_gating"></a>

[vanilla-confirmed 1.19.3] `sp/projects/*.txt`, `common/scientist_traits/00_traits.txt`:

- Project `allowed` blocks name: Gotterdammerung 28 (one project, `sp_naval_nuclear_torpedo`, needs Gotterdammerung and Man the Guns), No Compromise No Surrender 3, No Step Back 2, Peace For Our Time 1; 15 projects have no DLC gate (`sp_nuclear_reactor`, `sp_nuclear_bomb`, `sp_air_jet_engine`, `sp_air_radar`, the early submarine projects and others).
- Pieces of a project are gated separately with `limit = { has_dlc = "Gotterdammerung" }` inside `enable_equipments`, `enable_equipment_modules` and `enable_subunits`, and with `if = { limit = { has_dlc = ... } }` inside effects and `available`. Example: `enable_equipment_modules = { limit = { has_dlc = "Gotterdammerung" has_dlc = "No Step Back" } lc_radar }` in `sp_air_radar`.
- Two traits are gated: `scientist_trait_helicopter_expert` and `scientist_trait_bombs_expert` by Gotterdammerung, and `scientist_trait_artillery_specialist` by an `OR` of Gotterdammerung and No Step Back.
- A gated project is never created for a country without the DLC, because `allowed` is checked at startup [docs] `sp/projects/documentation.md`.

## Console commands <a id="Console_commands"></a>

For testing. [docs] `documentation/console_commands_documentation.md`; see also [Console commands](<console-commands.md>).

| Command | Effect |
| --- | --- |
| `sp_unlock_all` | every project is visible and available, parents ignored |
| `sp_available` | every project's `available` returns true |
| `sp_breakthrough <amount> [specialization]` (alias `sp_br`) | create breakthrough points |
| `sp_add_scientist [level] [specialization]`, `sp_add_mastermind` | add a scientist |
| `sp_add_selected_scientist_level`, `sp_set_selected_scientist_level`, `sp_add_selected_scientist_trait`, `sp_remove_selected_scientist_trait` | edit the scientist of the open facility view |
| `sp_fast` | every phase takes 1 day; iterations still all happen |
| `sp_instant` | started projects finish on the next daily tick; iterations and rewards are skipped |
| `sp_prototype_reward <reward>` (alias `spr`) | fire a prototype reward during a project |
| `sp_research_all` (alias `sp_ra`) | research every project |

## Minimal example <a id="Minimal_example"></a>

A land project with one unique reward, in vanilla style. The ids use a `mod_` prefix; `has_tech = railway_gun`, `specialization_land` and the generic reward ids are vanilla. Vanilla patterns are copied from `sp/projects/land_projects.txt`, `sp/prototype_rewards/generic_land_prototype_rewards.txt` and `sp/projects/nuclear_projects.txt` [vanilla-confirmed 1.19.3].

`common/special_projects/projects/mod_land_projects.txt`:

```text
mod_sp_land_siege_gun = {
	specialization = specialization_land
	project_tags = sp_tag_artillery
	icon = GFX_mod_sp_land_siege_gun

	allowed = { has_dlc = "No Step Back" }
	available = { FROM = { has_tech = railway_gun } }

	prototype_time = sp_time.prototype.long
	complexity = sp_complexity.medium
	breakthrough_cost = { specialization_land = 1 }
	resource_cost = { resources = { steel = 10 tungsten = 4 } }

	ai_will_do = {
		base = 1
		modifier = { factor = 0.5 ROOT = { is_major = no } }
	}

	project_output = {
		country_effects = { add_political_power = 25 }
	}

	generic_prototype_rewards = {
		sp_land_generic_reward_scientist_xp_1
		sp_land_generic_reward_major_progress_1
		sp_land_generic_reward_test_failure_1
	}

	unique_prototype_rewards = {
		mod_sp_land_siege_gun_design_reward = {
			fire_only_once = yes
			threshold = { min = 20 max = 60 }
			weight = { base = 100 }

			option = {
				token = mod_sp_land_siege_gun_design_reward_fast
				default = yes
				iteration_output = {
					country_effects = { FROM = { add_project_progress_ratio = constant:sp_progress.gain.low } }
				}
			}
			option = {
				token = mod_sp_land_siege_gun_design_reward_careful
				iteration_output = {
					scientist_effects = {
						add_scientist_xp = {
							experience = constant:sp_scientist_xp_gain.medium
							specialization = specialization_land
						}
					}
				}
			}
		}
	}
}
```

A scientist in `common/characters/MOD.txt`, placed in the country with `recruit_character = MOD_example_scientist` in the country history file:

```text
characters = {
	MOD_example_scientist = {
		name = MOD_example_scientist
		portraits = { army = { large = GFX_portrait_MOD_example_scientist } }
		scientist = {
			traits = { scientist_trait_armored_specialist scientist_trait_bright }
			skills = { specialization_land = 2 }
		}
	}
}
```

Localisation (`l_english`):

```text
 mod_sp_land_siege_gun: "Siege Gun"
 mod_sp_land_siege_gun_desc: "A super-heavy gun for breaking fortified lines."
 mod_sp_land_siege_gun_design_reward: "Barrel Design"
 mod_sp_land_siege_gun_design_reward_desc: "The team has two barrel designs on the table."
 mod_sp_land_siege_gun_design_reward_fast: "Build the short barrel"
 mod_sp_land_siege_gun_design_reward_careful: "Test the long barrel first"
 MOD_example_scientist: "Example Scientist"
 mod_sp_land_siege_gun_speed_factor: "Siege Gun Research Speed"
 mod_sp_land_siege_gun_speed_factor_tt: " $mod_sp_land_siege_gun_speed_factor$: $RIGHT|+=%1$"
```

The sprite in a `.gfx` file under `interface/` (the scientist's portrait sprite `GFX_portrait_MOD_example_scientist` is defined the same way):

```text
spriteTypes = {
	spriteType = {
		name = "GFX_mod_sp_land_siege_gun"
		texturefile = "gfx/interface/special_project/project_icons/mod_sp_land_siege_gun.dds"
	}
}
```

## Silent failures and traps <a id="Traps"></a>

| Trap | What happens | Evidence |
| --- | --- | --- |
| Writing keys from `sp/special_projects_documentation.md` | the keys are not used by any vanilla file and are absent from `hoi4.exe`; the project does not behave as written | 0 vanilla uses, string search [vanilla-confirmed 1.19.3], effect [unverified] |
| Threshold on a 0 to 1 scale | vanilla thresholds run 0 to 100; a 0 to 1 window would cover almost no progress | [vanilla-confirmed 1.19.3] `sp/projects/nuclear_projects.txt` |
| Country trigger directly inside `available` | the scope is the project, so country triggers need `FROM = { }` | [docs], 41 vanilla `FROM` wrappers [vanilla-confirmed 1.19.3] |
| Dynamic condition in `allowed` | `allowed` is evaluated once at startup and only accepts `tag`, `original_tag`, `has_dlc`; use `available` or `visible` for anything that changes | [docs] `sp/projects/documentation.md` |
| `FROM` in project `ai_will_do` | the docs and vanilla disagree; vanilla only uses `ROOT = { }` | [docs], [vanilla-confirmed 1.19.3] |
| `complete_special_project` for a project with facility effects | the facility state and scientist effects are skipped, so a reactor project completed this way builds no reactor | [docs] `documentation/effects_documentation.md` |
| `complete_special_project` for a child project | parents are not checked or completed | [docs] |
| `special_project_prototype_speed_factor` in a trait | not a modifier; use `special_project_speed_factor` | [docs] `documentation/modifiers_documentation.md` |
| Spelling the option key of `complete_prototype_reward_option` correctly | the documented key is `prototyp_reward_option` (missing `e`); copy the documentation exactly | [docs] `documentation/effects_documentation.md` |
| `constant:` prefix on `complexity` or `prototype_time` | those keys take the bare constant; effect values need the prefix | [docs] `common/script_constants/documentation.md`, [vanilla-confirmed 1.19.3] |
| `oil` in `resource_cost` | not allowed | [docs] `sp/projects/documentation.md` |
| New specialization without a facility | the docs require a building that carries the same `specialization`; without one the projects cannot be researched | [docs] `sp/specialization/documentation.md`; effect [unverified] |
| `complexity = 0` | logged as an error and replaced by the default 100 | [docs] |
| `weight = { factor = ... }` | three vanilla rewards write it with the value 1.0 (the default weight); the documented key is `base`, and what `factor` does at that level is not stated | [vanilla-confirmed 1.19.3] `generic_nuclear_prototype_rewards.txt`; effect [unverified] |
| Reading `var:facility_state` in weights | documented, never used by vanilla; `var:facility_province_id` is the province id | [docs], [vanilla-confirmed 1.19.3] |
| Missing `<id>_speed_factor_tt` text for a new project's speed modifier | tooltip shows a raw key | [unverified] |

## See also <a id="See_also"></a>

- [Raid modding](<raid-modding.md>): facility strikes and nuclear raids tie into projects.
- [Character modding](<character-modding.md#Scientists>), [Building modding](<building-modding.md>), [Technology modding](<technology-modding.md>), [Equipment modding](<equipment-modding.md>), [Localisation](<localisation.md>).

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list-of-modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on-actions.md>) • [Data structures](<data-structures.md>) • [Flags](<data-structures.md#Flags>) • [Event targets](<data-structures.md#Event_targets>) • [Country tag aliases](<data-structures.md#Country_tag_aliases>) • [Variables](<data-structures.md#Variables>) • [Arrays](<data-structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement-modding.md>) • [AI](<ai-modding.md>) • [AI focuses](<ai-focuses.md>) • [Autonomous states](<autonomy-state-modding.md>) • [Balances of power](<balance-of-power-modding.md>) • [Bookmarks/Scenarios](<bookmark-modding.md>) • [Game rules](<bookmark-modding.md#Game_rules>) • [Buildings](<building-modding.md>) • [Characters and traits](<character-modding.md>) • [Cosmetic tags](<cosmetic-tag-modding.md>) • [Countries](<country-creation.md>) • [Divisions](<division-modding.md>) • [Decisions](<decision-modding.md>) • [Doctrines](<doctrine-modding.md>) • [Equipment](<equipment-modding.md>) • [Events](<event-modding.md>) • [Factions](<faction-modding.md>) • [Ideas](<idea-modding.md>) • [Ideologies](<ideology-modding.md>) • [Military industrial organizations](<military-industrial-organization-modding.md>) • [National focuses](<national-focus-modding.md>) • [Resources](<resources-modding.md>) • [Scripted GUI](<scripted-gui-modding.md>) • [Technologies and doctrines](<technology-modding.md>)
- **Map**: [Map](<map-modding.md>) • [States](<state-modding.md>) • [Supply areas](<supply-areas-modding.md>) • [Strategic regions](<strategic-region-modding.md>)
- **Graphical**: [Interface](<interface-modding.md>) • [Graphical assets](<graphical-asset-modding.md>) • [Entities](<entity-modding.md>) • [Posteffects](<posteffect-modding.md>) • [Particles](<particle-modding.md>) • [Fonts](<font-modding.md>)
- **Cosmetic**: [Portraits](<portrait-modding.md>) • [Namelists](<namelist-modding.md>) • [Music](<music-modding.md>) • [Sound](<sound-modding.md>)
- **Other**: [Console commands](<console-commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod-structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection-modding.md>) • [Game rule modding](<game-rule-modding.md>) • [Intelligence operation modding](<intelligence-operation-modding.md>) • [Map mode modding](<map-mode-modding.md>) • [Occupation and resistance modding](<occupation-and-resistance-modding.md>) • [Peace conference modding](<peace-conference-modding.md>) • [Raid modding](<raid-modding.md>) • [Script constant modding](<script-constant-modding.md>) • [Special project modding](<special-project-modding.md>)
