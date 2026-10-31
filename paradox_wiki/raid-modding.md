# Raid modding

*Kit page: written by the Agentic HOI4 Modding Kit from the Hearts of Iron IV 1.19.3.0 game files. The wiki has no page for this topic. CC BY-SA 3.0 (see LICENSE.txt).*
<!-- kit:page -->

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" sources="common/raids/ common/defines/00_defines.lua common/ai_strategy/ common/on_actions/ documentation/effects_documentation.md documentation/triggers_documentation.md documentation/console_commands_documentation.md interface/military_raids/ interface/buildings/landmarks.gfx localisation/english/military_raids_l_english.yml gfx/entities/" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Written from: `common/raids/_documentation.md` (read in full), all 8 vanilla raid files (37 raid types) and the category file (5 categories), the `NRaids` and `NAI` defines, the RAID_INSTANCE effect and trigger documentation, raid localisation, raid GFX and entities. Every rule taken from the kit's `hoi4-native-raids` skill was re-checked against these files and is tagged where it appears.
Also checked: whether `hoi4.exe` contains the keys on which the documentation and vanilla disagree (read-only string search).
Gaps left: how the three success factors become four outcomes, the meaning of `range_factor` and `cancel_trigger` (undocumented), and the scope a `target_type` state filter runs in are not settled by any game file; they are tagged `[unverified]`. No game was run.
<!-- kit:end id="review" -->

## Table of contents

- [Overview](#Overview)
  - [Raid lifecycle](#Raid_lifecycle)
- [Files and loading](#Files_and_loading)
- [Raid categories](#Raid_categories)
- [Raid type reference](#Raid_type_reference)
  - [Gating and triggers](#Gating_and_triggers)
  - [Timing, cost and units](#Timing_cost_and_units)
  - [Targets](#Targets)
  - [Presentation keys](#Presentation_keys)
  - [AI keys](#AI_keys)
- [Success chance](#Success_chance)
  - [Predefined modifiers](#Predefined_modifiers)
  - [Custom modifiers](#Custom_modifiers)
  - [Risk dial](#Risk_dial)
  - [How the odds become outcomes](#Odds_to_outcomes)
- [Outcomes and scopes](#Outcomes_and_scopes)
  - [Effects and triggers for raids](#Effects_and_triggers)
- [Raids and special projects](#Raids_and_special_projects)
- [Localisation](#Localisation)
- [GFX, entities and sounds](#GFX)
- [AI](#AI)
- [DLC gating in vanilla](#DLC_gating)
- [Defines](#Defines)
- [Console commands](#Console_commands)
- [Minimal example](#Minimal_example)
- [Confirmed traps](#Confirmed_traps)
- [Practice notes (kit skill)](#Practice_notes)
- [See also](#See_also)

---

Raids are one-off strikes that a country prepares and launches against a province, a state or a building: air bombing, paratrooper drops, marine commando landings, land infiltrations and nuclear strikes. A raid type defines what the raid needs, what it can hit, what it costs, how likely it is to work and what each result does. All definitions live in `common/raids/`. The system is DLC-gated in vanilla: 35 of the 37 raid types name a DLC in `allowed` (22 need Gotterdammerung), and only `nuclear_strike` and `JAP_pearl_harbor_strike` name none [vanilla-confirmed 1.19.3] `common/raids/*.txt`.

Evidence tags used on this page: `[docs]` = the game's own documentation, `[vanilla-confirmed 1.19.3]` = seen in vanilla script, `[unverified]` = plausible but not confirmed. File names in tags are relative to the game folder; `raids/` stands for `common/raids/`.

## Overview <a id="Overview"></a>

| Part | Defined in | Role |
| --- | --- | --- |
| Raid category | `raids/categories/*.txt`, root `categories = { }` | Groups raid types in the raid UI, sets the detection intel source, can allow free targeting |
| Raid type | `raids/*.txt`, root `types = { }` | One definition: gating, target, cost, units, odds, outcomes |
| Raid instance | created in game | A raid being assembled, prepared, launched; the scope of outcome blocks |

All rows: [docs] `raids/_documentation.md`; roots and counts [vanilla-confirmed 1.19.3] `raids/*.txt`, `raids/categories/raid_categories.txt`.

### Raid lifecycle <a id="Raid_lifecycle"></a>

1. **Create.** The player picks a target, a type, a unit and a starting point. Creating costs `command_power` allocation and needs `essential_equipment` in the stockpile.
2. **Assembling.** The raid collects its equipment.
3. **Preparing.** Takes `days_to_prepare` days; the `prep_time` success modifier follows this progress.
4. **Prepared.** The raid can be launched when `launchable` is true and the intel on the target is high enough, by hand or by auto-launch above a chosen success chance.
5. **In progress.** The unit travels along the `arrow` path at `speed_multiplier` times the global raid speed.
6. **Ended.** One of four outcomes runs. A raid can also be canceled, and is canceled by the game when its unit disappears, cannot reach the starting point, or the starting point moves out of range.

The phases and the outcome names are the localisation strings `RAID_INST_PHASE_*`, `RAID_INST_OUTCOME_*` and `raid_canceled_*`; the order follows the documentation of `essential_equipment`, `additional_equipment` and `days_to_prepare` [docs] `raids/_documentation.md`, [vanilla-confirmed 1.19.3] `localisation/english/military_raids_l_english.yml`. The outcome report stays on the map for `RAID_OUTCOME_REPORT_DAYS_TO_LIVE = 30` days [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

## Files and loading <a id="Files_and_loading"></a>

| File | Content | Types |
| --- | --- | --- |
| `raids/categories/raid_categories.txt` | the 5 categories | |
| `raids/air_raids.txt` | generic air raids | 6: `facility_strike`, `lock_bombing_raid`, `dam_bombing_raid`, `oilfield_raid`, `mega_gun_emplacement_strike`, `mega_gun_emplacement_strike_no_bba` |
| `raids/air_raids_custom.txt` | country-specific air raids | 13 |
| `raids/nuclear_raids.txt` | nuclear and thermonuclear strikes | 6 |
| `raids/paratrooper_raids.txt` | generic paratrooper raids | 2: `mine_sabotage_raid`, `pathfinder_raid` |
| `raids/paratrooper_raids_custom.txt` | country-specific | 2 |
| `raids/land_infiltration_raids.txt` | generic land raid | 1: `rescue_captured_general` |
| `raids/land_infiltration_custom.txt` | country-specific | 4 |
| `raids/naval_commando_raids.txt` | marine commando raids | 3 |

All rows: [vanilla-confirmed 1.19.3] `raids/*.txt`. File names are free; the category of a type comes from its `category` key, not from the file.

- **Root blocks.** Every raid file starts with `types = { ... }` and the category file with `categories = { ... }`. The documentation template shows the type and category bodies without these roots; follow vanilla [vanilla-confirmed 1.19.3] (8 of 8 type files, 1 of 1 category file). That a file without the root is ignored is [unverified].
- **Duplicates.** The documentation does not say what happens when two files define one id. Override a vanilla type by reusing its file name [unverified].
- **Ids.** Country-specific types are prefixed with a tag (`GER_eben_emael_raid`); the prefix is part of the id, and the localisation key is `raid_type_<id>` [vanilla-confirmed 1.19.3] `raids/paratrooper_raids_custom.txt`, `localisation/english/military_raids_l_english.yml`.

## Raid categories <a id="Raid_categories"></a>

A category is `<category_id> = { ... }` in `raids/categories/`. Keys: [docs] `raids/_documentation.md`; vanilla counts [vanilla-confirmed 1.19.3] `raids/categories/raid_categories.txt` (5 categories).

| Key | Value | Meaning | Vanilla |
| --- | --- | --- | --- |
| `intel_source` | `air`, `naval`, `army` or `civilian` | the intel type used to detect raids of this category | 5 of 5 |
| `visible` | country trigger | whether the category is shown | 4 of 5 |
| `available` | country trigger | whether the category is active | 4 of 5 |
| `free_targeting` | yes | the UI lets the player aim any province; raid types in the category still need `province = any` | 1 (`nuclear_raids`) |
| `faction_influence_score_on_success` | number | not documented; the key is a string in `hoi4.exe`; by its name it feeds faction influence on success [unverified] | 5 of 5: air 200, paratrooper 100, nuclear -100, land 50, naval 50 |

| Category | `intel_source` | Gate in vanilla |
| --- | --- | --- |
| `air_raids` | air | visible with Gotterdammerung |
| `paratrooper_raids` | air | visible with Gotterdammerung, available with `has_tech = paratroopers` |
| `nuclear_raids` | air | `free_targeting = yes`; available when `is_special_project_completed = sp:sp_nuclear_bomb` or `num_of_nukes > 0` |
| `land_infiltration_raids` | army | visible with Thunder at Our Gates, or with No Compromise No Surrender for China |
| `naval_commando_raids` | naval | visible with Thunder at Our Gates for `INS`, `AST` or `SIA` |

Second table: [vanilla-confirmed 1.19.3] `raids/categories/raid_categories.txt`. The define `NUCLEAR_RAID_CATEGORY_NAME = "nuclear_raids"` names the category the rocket "nuclear" button opens, so that category id is fixed by the engine [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` (`NRaids`).

Category text and sprites: `raid_category_<id>`, `raid_category_header_<id>`, `tooltip_raid_category_<id>`, `raid_category_fluff_text_<id>` (a `TAG_` prefix gives a country-specific fluff text), `GFX_raid_category_small_<id>` and `GFX_raid_unit_icon_<id>`, each with an `unknown` fallback sprite [vanilla-confirmed 1.19.3] `localisation/english/military_raids_l_english.yml`, `interface/military_raids/military_raids.gfx`.

## Raid type reference <a id="Raid_type_reference"></a>

A raid type is `<raid_type_id> = { ... }` inside `types = { }`. Meanings: [docs] `raids/_documentation.md`. Counts: [vanilla-confirmed 1.19.3] `raids/*.txt`, n = 37 types (a block that may repeat is counted per block).

### Gating and triggers <a id="Gating_and_triggers"></a>

| Key | Value | Rule | Vanilla |
| --- | --- | --- | --- |
| `category` | category id | mandatory in practice | 37 |
| `allowed` | trigger | mainly country-specific raids and DLC locks; default always | 37 |
| `visible` | trigger | whether the type is shown before targets are considered; keep it cheap | 37 |
| `show_target` | trigger | whether a specific target is shown; `FROM` = target country | 37 |
| `available` | trigger | being able to prepare the raid | 36 |
| `launchable` | trigger | being able to start a prepared raid | 27 |
| `launchable_from` | trigger, scope = country controlling the starting point (base, fleet) | optional | 0 |
| `cancel_trigger` | trigger | not documented; the string is in `hoi4.exe`; vanilla uses `NOT = { has_country_flag = ... }`, so the raid is probably canceled while it is true [unverified] | 2 |
| `fire_only_once` | yes or no | the raid can be executed once; default no [unverified] | 23 (16 yes, 7 no) |
| `days_re_enable` | days | wait before the same target can be raided again; 0 means no cooldown; default `RAID_DEFAULT_TARGET_COOLDOWN_DAYS = 365` | 5 (0, 0, 0, 60, 120) |

Scopes [docs] `raids/_documentation.md`, [vanilla-confirmed 1.19.3] `raids/*.txt`:

- In `allowed`, `visible`, `show_target`, `available`, `launchable` and `ai_will_do` the scope is the acting country. `FROM` is the target country. `var:target_state` and `var:target_province` are set where a target exists. `ROOT` is the acting country, as in `CZE = { NOT = { has_war_with = ROOT } }` in `visible` of `SOV_transport_volunteers_to_CZE` and `ROOT.indochina_states` in `show_target` of `SIA_indochina_port_raid`.
- A state id can be used as a scope in these blocks: `34 = { is_owned_and_controlled_by = BEL }` in `GER_eben_emael_raid`.
- Vanilla writes the usual gate: `show_target = { NOT = { is_in_faction_with = FROM } }` and `launchable = { has_war_with = FROM }`.
- `visible`, `available` and `launchable` are different gates: type display, preparation, launch. Whether a prepared instance stays when the type's `visible` turns false is not settled by any game file [unverified].

### Timing, cost and units <a id="Timing_cost_and_units"></a>

| Key | Value | Rule | Vanilla |
| --- | --- | --- | --- |
| `days_to_prepare` | days | preparation length; the define `NRaids.BASE_DAYS_TO_PREPARE = 7` is described as the base number of days, and whether it is the default for an omitted key is [unverified] | 37 (30 in 17 types, 90 in 9, 14 and 15 in 7, others 35 to 120) |
| `command_power` | number | command power allocation cost | 37 (5 to 40; 20 in 12 types) |
| `speed_multiplier` | number | unit speed factor, default 1, on top of the global `RAID_UNIT_SPEED_MULTIPLIER = 0.1` | 12 (0.08 to 20) |
| `essential_equipment` | `{ archetype = amount }` | must be in the stockpile to create the raid; collected after creation | 13 |
| `additional_equipment` | `{ archetype = amount }` | collected after creation; not needed to create. Together with `essential_equipment` the larger of the two amounts is used, they do not add up | 12 |
| `nuke_type` | `nuclear_bomb` or `thermonuclear_bomb` | the nuke kind when the `nukes` key is used | 3 (all `thermonuclear_bomb`) |
| `unit_requirements` | repeatable block | a unit that matches any one block may take part | 51 blocks |
| `starting_point` | block | where the raid starts | 37 |
| `max_distance` | distance units | hard cap on source-to-target path length; the AI ignores it with `unlimited_ai_range = yes` | 1 (`rescue_captured_general`, 20) |
| `range_factor` | number | not documented; used with `unlimited_ai_range`; meaning [unverified] | 3 (14 and 20) |

- `unit_requirements` takes `equipment = { type = { <equipment type> } amount = { min = N max = M } modules = { <module> } }` or `battalion_types = { <sub-unit> = { min = N } }`. Vanilla equipment types: `strategic_bomber` 18, `tactical_bomber` 4, `nuclear_missile_equipment` 4, `strat_bomber_intercontinental_equipment` 2, and one each of `heavy_fighter`, `cas`, `naval_bomber`, `transport_plane_equipment`. Battalion types: `infantry`, `militia`, `paratrooper`, `mountaineers`, `marine`.
- `essential_equipment` and `additional_equipment` keys are equipment archetypes, the pseudo-entries `nukes` and `convoy` (vanilla `convoy = 40` for marine raids), and the docs add that ship hulls (`ship_hull_light = 5`) are allowed and are taken from existing fleets. Vanilla: `nukes = 1` 6, `convoy = 40` 3, `transport_plane_equipment` 5 or 10 in 4, and `support_equipment` and `infantry_equipment` as additional equipment.
- `starting_point` takes `types = { air_base naval_base rocket_site carrier submarine }` (vanilla: `air_base` 24, `rocket_site` 2, `naval_base` 2, `submarine` 2, `carrier` 1), `building_types = { supply_node }` (a list of building ids or tags; vanilla also `naval_base`, `rail_way`, `bunker`) and `allow_faction_buildings = yes` (use buildings in allied territory; vanilla 6 uses, five with `building_types` and one with `types`).

[docs] `raids/_documentation.md`; vanilla values [vanilla-confirmed 1.19.3] `raids/*.txt`.

### Targets <a id="Targets"></a>

`target_type = { ... }` (singular, 37 of 37 types) lists what the raid can hit [vanilla-confirmed 1.19.3]. Forms:

| Form | Meaning | Vanilla |
| --- | --- | --- |
| `province = any` | any province; needs a category with `free_targeting = yes` | 6 (nuclear) |
| `province = <id>` | one fixed province; the key may repeat for several | 8 entries in 7 types (`PRC_probe_border_defenses_raid` repeats it) |
| `building = { type = <building> }` | a building by id | 14 uses (landmarks, `naval_base`, `supply_node`, `mega_gun_emplacement`) |
| `building = { tags = <tag> }` | a building by tag | 3 uses (`facility`, `locks_building`, `dam_building`) |
| `state = { <state triggers> }` | any state that passes the triggers, for example `oil > 24`, `steel > 69`, `is_coastal = yes`, `is_core_of = MAL` | 6 types |
| `captured_army_leader = yes` | a captured commander (the target is a character) | 1 (`rescue_captured_general`) |

- The documentation also lists `level = { min = X max = Y }` and `is_coastal = yes` inside `building` and `type = <type/tag>`; vanilla never uses `level` or `is_coastal` there, and spells the tag form `tags` [docs] `raids/_documentation.md`, [vanilla-confirmed 1.19.3].
- A raid hitting a facility with `building = { tags = facility }` ties raids to special projects (see [Raids and special projects](#Raids_and_special_projects)).
- The scope a `state = { }` filter runs in is not documented. Vanilla writes `is_owned_by = FROM` there in two types, which only makes sense if `FROM` is bound in the filter. A claim that the state is `ROOT` there is [unverified]; do not read the acting country through `ROOT` in a target filter.
- The target name in the UI is `RAID_TARGET_NAME` ("$WHAT in $LOCATION"), or your own key set with `target_loc_key`, which can use `$LOCATION$` [docs] `raids/_documentation.md`, [vanilla-confirmed 1.19.3] `localisation/english/military_raids_l_english.yml`.

### Presentation keys <a id="Presentation_keys"></a>

| Key | Value | Rule | Vanilla |
| --- | --- | --- | --- |
| `custom_map_icon` | GFX name | overrides the automatic `GFX_raid_type_icon_<id>` lookup | 25 |
| `custom_terrain_icon` | GFX name | overrides the background chosen from the target terrain | 0 |
| `target_icon` | GFX name | icon of the target | 37 |
| `unit_icon`, `equipment_icon` | GFX name | documented | 0 |
| `target_loc_key` | loc key | custom target name | 16 |
| `launch_sound` | sound effect id | played at launch | 37 |
| `arrow` | `{ type = line / ballistic / air / naval / land }` | travel path style | 37 (air 25, land 5, ballistic 4, naval 3) |
| `unit_model` | `{ entity default_entity equipment start_offset scale }` | what travels; see below | 17 |
| `unit_animations` | `{ stage = { state intro at_progress } }` | animation by travel progress | 5 |

- `unit_model.entity` is looked up as the country entity (`GER_<name>`), then the culture entity (`westerngfx_<name>`), then `<name>`, then `default_entity`. `equipment = air_transport` uses an air equipment model (only air equipment is supported). `start_offset` moves the start so convoys begin at sea. `scale` is multiplied by the graphics define `RAID_UNIT_ENTITY_BASE_SCALE` (2.0 in `common/defines/00_graphics.lua`). Vanilla uses `entity` 8, `equipment` 5, `scale` 5, `start_offset` 3; `default_entity` 0.
- `unit_animations` stages must be listed in ascending `at_progress` order; the stage with the highest `at_progress` not above the current progress wins; a state missing on the entity is skipped without error.

[docs] `raids/_documentation.md`; counts [vanilla-confirmed 1.19.3] `raids/*.txt`.

### AI keys <a id="AI_keys"></a>

| Key | Value | Rule | Vanilla |
| --- | --- | --- | --- |
| `ai_will_do` | weight block | the AI only does the raid when the weight is above 0; `FROM` = target country; `var:target_state`, `var:target_province` | 35 |
| `ai_min_success_chance` | 0.0 to 1.0 | per-type override of `RAIDS_MIN_SUCCESS_FOR_LAUNCH` (0.65) | 2 |
| `unlimited_ai_range` | yes | the AI ignores `max_distance` | 3 |

See [AI](#AI).

## Success chance <a id="Success_chance"></a>

`success_factors = { success = { ... } critical = { ... } disaster = { ... } }`. [docs] `raids/_documentation.md`, counts [vanilla-confirmed 1.19.3] `raids/*.txt`:

- `success` is the chance that the raid succeeds (all 37 types define it). `critical` is the chance that a success is critical (conditional; 21 types). `disaster` is the chance of the worst outcome (not conditional; 1 type, `CZE_sokolov_raid_pfot`). Nuclear raids define only `success`.
- Each formula has an optional `base` (default 0.0) and any number of modifiers.
- A modifier has `weight` (the largest change it can make, positive or negative, additive; required), `reference` (the value of the measured property at which the full weight applies; default 1.0), `start_weight` (the weight at the start point; default 0.0) and `start_reference` (the property value of the start point; the start point is 0 when it is omitted). The weight changes linearly between the start point and the reference. `start_weight = -0.1` with `weight = 0.1` and `reference = 100` gives -10% at 0, 0 at 50 and +10% at 100.

### Predefined modifiers <a id="Predefined_modifiers"></a>

Meanings and reference ranges: [docs] `raids/_documentation.md`. Use counts in `success` formulas: [vanilla-confirmed 1.19.3] `raids/*.txt`.

| Name | Measures | Vanilla |
| --- | --- | --- |
| `prep_time` | preparation progress, 0 to 1 | 0 |
| `experience` | experience of the unit, 0 to 1 | 33 |
| `anti_air` | anti-air in the target state, about 0 to 5 | 25 |
| `resistance` | resistance in the target state, 0 to 100 | 9 |
| `enemy_units` | enemy divisions in the target province; province targets only | 8 |
| `air_superiority` | your air superiority over the target region, 0 to 1 | 32 |
| `interception` | enemy planes on interception in the region | 25 |
| `intel` | your intel on the target (vanilla reference 100) | 36 |
| `air_defence` | air unit's air defence (docs: typically 0 to 50; vanilla reference 100) | 21 |
| `air_agility` | air unit's agility (docs: typically 0 to 50; vanilla reference 100) | 21 |
| `strategic_bomber` | air unit's strategic bombing, 0 to 1 | 0 |
| `reliability` | air unit's reliability, 0 to 1 | 21 |
| `recon` | land unit's recon, about 0 to 10 | 11 |
| `organisation` | land unit's organisation, 0 to 100 or more | 12 |
| `strength` | land unit's strength, 0 to 1 | 12 |
| `radar` | enemy radar in the region; not in the documentation | 2 (nuclear strike types) |

`radar` has loc keys `success_modifier_radar*`, so it is a real predefined modifier that the documentation omits [vanilla-confirmed 1.19.3] `raids/nuclear_raids.txt`, `localisation/english/military_raids_l_english.yml`. The documentation's own example writes `agility`; the predefined name is `air_agility` (a string in `hoi4.exe`, used by 21 vanilla types). What an unknown name does is [unverified].

### Custom modifiers <a id="Custom_modifiers"></a>

A name that is not predefined is a custom modifier, sampled from a script formula [docs] `raids/_documentation.md`:

```text
INS_infrastructure_modifier_militia = {
	scope = state                     # country, state, character or unit; needed when the formula reads a variable
	formula = {
		base = 1
		modifier = { factor = infrastructure_level }   # dynamic variable of the scope
	}
	weight = -0.15
	reference = 5
	can_actor_affect = no             # shown as an action the acting country can take
	can_target_affect = yes           # shown as a counter-measure for the target
}
```

- The formula is a normal MTTH-style block. Triggers in it make the scope implicit: `has_completed_focus = X` with `add = 1` needs no `scope`. A formula that reads a variable needs `scope` because variables cannot be sampled from more than one source [docs].
- A custom modifier that uses only unit or character scope also shows up in the unit selection menu [docs].
- Vanilla: 13 custom modifiers with `formula`, with scopes `state` 6, `country` 2, `character` 2, `unit` 1; variable reads seen: `infrastructure_level` (state), `level` (character), `var:INS_level_of_militias` (country) [vanilla-confirmed 1.19.3] `raids/naval_commando_raids.txt`, `raids/land_infiltration_custom.txt`.
- Text: `success_modifier_<name>` (required), plus optional `_negative`, `_improvement` (required when `can_actor_affect = yes`), `_counterplay` and `_source` [docs]. For `air_superiority`, vanilla also has `_source_counterplay`.

### Risk dial <a id="Risk_dial"></a>

The player can set the risk of a raid to low, medium or high. `NRaids` adds +0, +0.10 and +0.25 to the success chance and the same amounts to the disaster chance [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` (`RAID_*_RISK_SETTING_*`). The localisation says the success chance can be capped by a high disaster risk (`tooltip_success_chance_capped_by_risk`) [vanilla-confirmed 1.19.3].

### How the odds become outcomes <a id="Odds_to_outcomes"></a>

There are four outcomes: `failure`, `limited_success`, `success`, `critical_success`. The documentation says `failure`, "critical failure" and "disaster" are one thing, the worst outcome, and the UI string for `failure` is "Critical Failure" (`RAID_INST_OUTCOME_FAILURE`) [docs], [vanilla-confirmed 1.19.3]. 36 of 37 types have no `disaster` formula at all [vanilla-confirmed 1.19.3]. How the game splits an unsuccessful roll between `failure` and `limited_success` is not documented [unverified].

## Outcomes and scopes <a id="Outcomes_and_scopes"></a>

`success_levels = { failure = { } limited_success = { } success = { } critical_success = { } }`. All 37 vanilla types define all four [vanilla-confirmed 1.19.3] `raids/*.txt`. Keys inside a level [docs] `raids/_documentation.md`:

| Key | Scope | Content | Vanilla (of 148 level blocks) |
| --- | --- | --- | --- |
| `actor_effects` | raid instance | effects listed as affecting the raiding country | 144 |
| `victim_effects` | raid instance | effects listed as affecting the raided country | 134 |
| `division_effects` | division (unit) | effects on the raiding division | 48 |
| `visual_effect` | map | `{ entity = "name" animation = "attack" }` spawned on the target province | 121 |
| `custom_sound` | | sound effect for this outcome | 12 (nuclear) |
| `destroy_additional_equipment` | | share of the additional equipment destroyed, default 100% | 0 |

- **Names are only for the UI.** `actor_effects` and `victim_effects` run in the same scope, the raid instance. Separating them only splits the outcome report into two lists [docs].
- **Enter a scope before country or state effects.** Vanilla never puts a country or state effect directly inside either block. The first-level entries are raid effects (`raid_damage_units` 122, `raid_add_unit_experience` 121, `add_raid_history_entry` 48), `var:` scopes (`var:target_state` 122, `var:actor_country` 101, `var:victim_country` 31, `var:target_leader` 3, `var:target_province` 1), numeric state scopes (`16 = { }`), `event_target:` scopes, and a few scope-less helpers (`set_temp_variable` 3, `damage_units` 3) [vanilla-confirmed 1.19.3] `raids/*.txt`.
- **Variables** of the raid instance: `var:actor_country`, `var:victim_country`, `var:target_state`, `var:target_province` [docs]. Rescue raids also use `var:target_leader` [vanilla-confirmed 1.19.3] `raids/land_infiltration_raids.txt`.
- **ROOT stays the raid instance** inside nested scopes, so a nested block can read the instance with `ROOT`: `province = var:ROOT.target_province`, `scope = var:ROOT.victim_country`, `state = var:ROOT.target_state` [docs], [vanilla-confirmed 1.19.3] (36 uses in `air_raids_custom.txt` alone).
- **Temporary variables survive scope changes.** `set_temp_variable = { PRC_equipment_producer = var:victim_country }` in `actor_effects`, then `producer = PRC_equipment_producer` inside `var:actor_country = { }` [vanilla-confirmed 1.19.3] `raids/land_infiltration_custom.txt`.
- **Events from outcomes.** Vanilla fires events from inside a scoped block with a delay, for example `var:victim_country = { country_event = { id = INS_revolution_events.11 hours = 4 } }` (23 uses), and records completion with country flags such as `has_successfully_bombed_a_landmark_flag` [vanilla-confirmed 1.19.3] `raids/naval_commando_raids.txt`, `raids/air_raids_custom.txt`. No on action, trigger or effect in the documentation reports a finished raid; vanilla `common/on_actions/` has no raid hook [vanilla-confirmed 1.19.3]. Pass actors and targets to the event as event targets saved in the outcome; temporary variables do not cross into events [unverified].

### Effects and triggers for raids <a id="Effects_and_triggers"></a>

Parameters: [docs] `documentation/effects_documentation.md`. Wiki: [Effects (raid scope)](<effects.md#Raid_scope>), [Effects (raids)](<effects.md#Raids>).

| Effect | Scope | Form | Vanilla |
| --- | --- | --- | --- |
| `raid_damage_units` | raid instance | `{ damage = N org_damage = N str_damage = N plane_loss = N ratio = yes }`. `damage` is strength and organisation damage; `org_damage` and `str_damage` override it; `plane_loss` is planes lost; with `ratio = yes` all values are fractions of the current amount | 122 |
| `raid_add_unit_experience` | raid instance | `= 0.0 to 1.0`, progress toward the maximum level, accepts a variable | 121 |
| `add_raid_history_entry` | raid instance | `= yes` | 48 |
| `raid_reduce_project_progress_ratio` | state, inside a raid outcome | `= 0 to 1`, share of a special project's total progress | 3 |
| `damage_building` | state, country | `{ type = <id> or tags = <tag> damage = N province = <id or var> state = <id or var> repair_speed_modifier = -N }`; `damage` is in levels | 80, in 20 types |
| `launch_nuke` | country | `{ province = <id> or state = <id> controller = <tag> use_nuke = yes/no nuke_type = <type> }` | 13, nuclear raids |
| `destroy_unit`, `add_divisional_commander_xp` | division | in `division_effects` | 10, 46 |

Triggers: only `hidden_trigger` and `meta_trigger` are listed for the raid instance scope [docs] `documentation/triggers_documentation.md`. Use ordinary country and state triggers inside `var:` scopes. Raid-related country triggers seen in `visible`, `show_target` and `available`: `is_special_project_completed = sp:...`, `has_naval_invasion_against_state = { state = var:target_state preparation > 0.1 }`, `has_any_captured_general = yes`, `is_leader_visible = var:target_leader`, `num_of_nukes > 0`, `is_in_array = { array = potential_and_current_enemies value = FROM }` [vanilla-confirmed 1.19.3] `raids/*.txt`. The scripted effect `bathe_in_hellfire_nuclear` used by the nuclear strike comes from `common/scripted_effects/RAJ_GOE_scripted_effects.txt` [vanilla-confirmed 1.19.3].

Dynamic modifiers are the usual way to leave a mark on the target: `var:target_state = { add_dynamic_modifier = { modifier = sokolov_raided_limited_success_modifier days = 30 } }` (56 uses in 15 types); `scope = var:ROOT.victim_country` limits a modifier to the victim [vanilla-confirmed 1.19.3] `raids/paratrooper_raids_custom.txt`, `raids/land_infiltration_custom.txt`.

## Raids and special projects <a id="Raids_and_special_projects"></a>

Raids and [special projects](<special-project-modding.md>) meet in four places [vanilla-confirmed 1.19.3]:

- **Unlocking.** Raid gates read projects: `lock_bombing_raid` and `dam_bombing_raid` are `available` after `is_special_project_completed = sp:sp_air_bouncing_bomb`; the mega-gun strike after `sp:sp_air_earthshaker_bomb`; the four missile strikes (nuclear and thermonuclear, land and submarine) are `visible` after `sp:sp_nuclear_warheads`, `thermonuclear_strike` after `sp:sp_thermo_nuclear_bomb`, and `nuclear_strike` and the nuclear category after `sp:sp_nuclear_bomb` or while the country holds nukes (`raids/air_raids.txt`, `raids/nuclear_raids.txt`, `raids/categories/raid_categories.txt`).
- **Targets.** `facility_strike` targets `building = { tags = facility }`, the tag the four facility buildings carry. Leftover assets exist for facility raids that no vanilla type defines (`raid_type_paratrooper_facility_sabotage` and `raid_type_commando_facility_raid` texts, `GFX_raid_type_icon_paratrooper_facility_sabotage`).
- **Damage to a project.** Inside `var:target_state = { }`, `raid_reduce_project_progress_ratio = 0.05` (limited success), `0.15` (success) or `0.25` (critical success) cuts the facility's project progress, next to `damage_building = { tags = facility damage = 0.55 province = var:ROOT.target_province repair_speed_modifier = -0.25 }` (damage 0.15, 0.55 and 0.85 levels at the three success levels). The failure outcome only damages the building, by 0.05 (`raids/air_raids.txt`).
- **Tooltips.** `SP_UNLOCK_RAID` and `SP_UNLOCK_RAID_CATEGORY` are the unlock tooltips in `special_projects_l_english.yml`; a technology uses the first as `custom_effect_tooltip = { localization_key = SP_UNLOCK_RAID RAID_TYPE = raid_type_mine_sabotage_raid }` (the full `raid_type_<id>` key is the parameter) (`common/technologies/infantry.txt`).

Nothing makes a raid unlock automatically: a raid type is available when its own triggers are true, so unlocking is done with flags, focuses or completed projects tested in `visible` or `available` [vanilla-confirmed 1.19.3] `raids/*.txt`.

## Localisation <a id="Localisation"></a>

Keys from `localisation/english/military_raids_l_english.yml` and `TAOG_raids_l_english.yml` [vanilla-confirmed 1.19.3]:

| Text | Key | Notes |
| --- | --- | --- |
| Raid type name | `raid_type_<id>` | `<id>` includes any tag prefix |
| Raid type description | `raid_type_<id>_desc` | shown in the target tooltip |
| Category name and headers | `raid_category_<cat>`, `raid_category_header_<cat>`, `tooltip_raid_category_<cat>`, `raid_category_fluff_text_<cat>` | fluff text accepts a `TAG_` prefix |
| Target name | the `target_loc_key` key, default `RAID_TARGET_NAME` | variables `$WHAT$`, `$LOCATION$` |
| Success modifier | `success_modifier_<name>` plus `_negative`, `_improvement`, `_counterplay`, `_source` | for custom and predefined modifiers |
| Outcome tooltips | any key used with `custom_effect_tooltip` in an outcome | for example `raid_aborted_tt`, `raid_facility_damage_tt` with `DAMAGE = 55` |
| Outcome names | `RAID_INST_OUTCOME_FAILURE` ("Critical Failure"), `_LIMITED_SUCCESS`, `_SUCCESS`, `_CRITICAL_SUCCESS`, `_CANCELED` | engine strings |
| Dynamic modifier names | the modifier id, for example `dam_blown_modifier` | modifiers raids add |
| Unlock tooltips | `SP_UNLOCK_RAID`, `SP_UNLOCK_RAID_CATEGORY` | in `special_projects_l_english.yml` |

The documentation lists the loc keys of custom modifiers [docs] `raids/_documentation.md`; the rest is read from the vanilla yml files. Wiki: [Localisation](<localisation.md>).

## GFX, entities and sounds <a id="GFX"></a>

Rules [docs] `raids/_documentation.md`; vanilla names [vanilla-confirmed 1.19.3] `interface/military_raids/military_raids.gfx`, `interface/buildings/landmarks.gfx`, `gfx/entities/particle_entities.asset`, `gfx/entities/nuke.asset`, `sound/gui/gtd/gtd_gui.asset`.

| Asset | Name | Notes |
| --- | --- | --- |
| Map icon of the raid type | `custom_map_icon`, else `GFX_raid_type_icon_<id>` | |
| Target-building variant | the icon above plus `_<building id>` | `GFX_raid_type_icon_facility_raid` has `_land_facility`, `_naval_facility`, `_air_facility`, `_nuclear_facility` variants |
| Target icon | `target_icon`, 2-frame sprites in `landmarks.gfx` | `GFX_facility_icon`, `GFX_dam_icon`, `GFX_canal_icon`, `GFX_other_target_icon`, `GFX_naval_base_target_icon`, `GFX_oilfield_target_icon`, `GFX_mine_target_icon` |
| Category buttons | `GFX_raid_category_small_<cat>`, `GFX_raid_unit_icon_<cat>` | fallback `..._unknown` |
| Outcome icons | `GFX_raid_outcome_failure`, `_limited_success`, `_success`, `_critical_success`, `GFX_raid_disaster_icon` | |
| Outcome effects | `visual_effect` entities | `raid_failed_entity`; `air_raids_1_`, `air_raids_2_`, `air_raids_paradrop_`, `air_raids_naval_`, `air_raids_leaflet_`, `land_raids_` each with `limited_success_entity`, `success_entity`, `critical_success_entity`; `nuke_entity` |
| Travelling unit | `unit_model.entity` | for example `westerngfx_traderoute_convoy` (`gfx/entities/units_ships.asset`) |
| Launch sounds | `launch_sound` | `raid_launch_air`, `raid_launch_marine`, `raid_launch_paratrooper`, `raid_launch_nuclear_missile`, `raid_launch_nuclear_strike` |
| Outcome sound | `custom_sound` | `raid_result_success_nuclear`, `raid_result_critical_success_nuclear` |

Wiki: [Graphical asset modding](<graphical-asset-modding.md#spriteType>), [Entity modding](<entity-modding.md>), [Sound modding](<sound-modding.md>).

## AI <a id="AI"></a>

- **Weight.** `ai_will_do` on the raid type. The AI only does a raid when the resulting weight is above 0. Scope is the acting country, `FROM` the target, with `var:target_state` and `var:target_province`. A vanilla comment says a weight of 1 roughly stands for 1% of the success chance, that the base should stay at 1, and that reductions should use `factor` so the weight never drops to 0 by accident [docs] `raids/_documentation.md`, [vanilla-confirmed 1.19.3] `raids/naval_commando_raids.txt`.
- **Keeping the AI off or on.** `factor = 0` modifiers gate the AI to potential enemies: `NOT = { is_in_array = { array = potential_and_current_enemies value = FROM } }` (facility strike and the nuclear types) [vanilla-confirmed 1.19.3] `raids/air_raids.txt`. Unique raids use a high base (`base = 100`).
- **Success threshold.** The AI launches only above `RAIDS_MIN_SUCCESS_FOR_LAUNCH = 0.65`, or the type's `ai_min_success_chance`; it cancels a raid that has been launchable for `RAIDS_CANCEL_AFTER_DAYS_LAUNCHABLE = 60` days [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` (`NAI`).
- **Other `NAI` defines:** `RAIDS_ENABLE_AI = true`, `RAIDS_CREATE_FREQUENCY_DAYS = 7`, `RAIDS_COMMAND_POWER_CAP_TO_CREATE = 60.0`, `RAIDS_SCORE_DIFF_TO_CANCEL = 0.3`, `RAIDS_NUKE_TARGET_CUT_OFF = 10`, `RAIDS_AVOID_SAME_TARGET_DURATION_DAYS = 180`, `RAIDS_AVOID_SAME_TARGET_FACTOR = 0.4` [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.
- **Country bias.** The AI strategy type `raid_target_country` (`id` = target tag, `value` = percent change in how likely it is targeted): `ENG_raids` uses `value = 200` against `GER` [docs] `common/ai_strategy/_documentation.md`, [vanilla-confirmed 1.19.3] `common/ai_strategy/ENG.txt`. Wiki: [AI modding](<ai-modding.md#AI_strategies>).
- **Range.** `unlimited_ai_range = yes` lets the AI ignore `max_distance`. The marine raid range is `BASE_NAVAL_COMMANDO_RAID_DISTANCE = 1500` km and the country modifier `naval_commando_raid_distance` is probably added to it (an Indonesian idea sets 5000) [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`, `common/ideas/indonesia.txt`; the addition is [unverified].

## DLC gating in vanilla <a id="DLC_gating"></a>

Raid types: [vanilla-confirmed 1.19.3] `raids/*.txt`, `allowed` blocks, 37 types.

| DLC in `allowed` | Types |
| --- | --- |
| Gotterdammerung | 22 (generic air, paratrooper and missile types and many country raids; `SIA_indochina_port_raid` also needs Thunder at Our Gates) |
| No Compromise, No Surrender | 6 (`CHI_*` bombings, `PRC_*`, `CHI_great_wall_raid_land`) |
| Thunder at Our Gates | 6 (`rescue_captured_general`, `INS_*`, `SIA_*`, `AST_*`) |
| By Blood Alone | 2 (both mega-gun strikes, together with Gotterdammerung) |
| Peace For Our Time | 2 (`SOV_transport_volunteers_to_CZE`, `CZE_sokolov_raid_pfot`) |
| none | `nuclear_strike`, `JAP_pearl_harbor_strike` |

Categories add their own gates (see [Raid categories](#Raid_categories)): `air_raids` and `paratrooper_raids` are hidden without Gotterdammerung, so `JAP_pearl_harbor_strike` (category `air_raids`) is probably gated too [unverified]. Country raids combine `has_dlc` with `tag` or `original_tag` in `allowed` [vanilla-confirmed 1.19.3].

## Defines <a id="Defines"></a>

Wiki: [Defines](<defines.md#NRaids>). Values [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`:

| Define | Value | Use |
| --- | --- | --- |
| `NRaids.BASE_DAYS_TO_PREPARE` | 7 | base preparation days |
| `NRaids.RAID_DEFAULT_TARGET_COOLDOWN_DAYS` | 365 | default `days_re_enable` |
| `NRaids.RAID_UNIT_SPEED_MULTIPLIER` | 0.1 | global speed factor |
| `RAID_UNIT_ENTITY_BASE_SCALE` (`00_graphics.lua`) | 2.0 | base scale of the travelling unit entity |
| `NRaids.RAID_*_RISK_SETTING_SUCCESS_MODIFIER` | 0.0, 0.1, 0.25 | low, medium, high risk |
| `NRaids.RAID_*_RISK_SETTING_DISASTER_MODIFIER` | 0, 0.1, 0.25 | low, medium, high risk |
| `NRaids.TARGET_DETECTION_INTEL_TRESHOLD` | 20.0 | intel needed to detect a target |
| `NRaids.TARGET_INTEL_*` | 0.5 per intel type, +15 neighbour, +25 decryption, -5 per enemy counter-intel | how `intel` is built |
| `NRaids.NUCLEAR_RAID_CATEGORY_NAME` | `"nuclear_raids"` | fixed category id |
| `NRaids.NUCLEAR_BOMB_*`, `THERMONUCLEAR_BOMB_*` | damage and production scale | nukes |
| `NAI.RAIDS_*` | see [AI](#AI) | AI behaviour |

## Console commands <a id="Console_commands"></a>

`prepareraids [0.0 to 1.0]` completes the preparation of all active raids, and `endraids [1 to 4 or failure, limitedsuccess, success, criticalsuccess]` ends them with an outcome. Both are marked "Not available in release build" [docs] `documentation/console_commands_documentation.md`. Wiki: [Console commands](<console-commands.md>).

## Minimal example <a id="Minimal_example"></a>

An air raid on enemy naval bases with a new category, modelled on `SIA_indochina_port_raid` and `facility_strike`. Ids use a `mod_` prefix; `air_raids` is the vanilla category [vanilla-confirmed 1.19.3] `raids/air_raids_custom.txt`, `raids/air_raids.txt`.

`common/raids/mod_air_raids.txt`:

```text
types = {
	mod_port_strike = {
		category = air_raids
		days_to_prepare = 30
		command_power = 20
		fire_only_once = no
		days_re_enable = 120

		allowed = { has_dlc = "Gotterdammerung" }
		visible = { }
		show_target = { NOT = { is_in_faction_with = FROM } }
		available = { }
		launchable = { has_war_with = FROM }

		ai_will_do = {
			base = 1
			modifier = {
				factor = 0
				NOT = { is_in_array = { array = potential_and_current_enemies value = FROM } }
			}
		}

		target_type = { building = { type = naval_base } }
		target_icon = GFX_naval_base_target_icon
		custom_map_icon = GFX_raid_type_icon_other_raid
		launch_sound = raid_launch_air
		arrow = { type = air }

		unit_requirements = {
			equipment = { type = { strategic_bomber } amount = { min = 10 } }
		}
		starting_point = { types = { air_base } }

		success_factors = {
			success = {
				base = 0.65
				experience = { reference = 1.0 weight = 0.2 start_weight = -0.2 }
				anti_air = { reference = 5 weight = -0.25 }
				intel = { reference = 100 weight = 0.3 }
			}
			critical = { base = 0.1 }
		}

		success_levels = {
			failure = {
				actor_effects = {
					raid_damage_units = { plane_loss = 40 ratio = no }
					raid_add_unit_experience = 0.05
				}
				visual_effect = { entity = "raid_failed_entity" animation = "attack" }
			}
			limited_success = {
				victim_effects = {
					var:target_state = { damage_building = { type = naval_base damage = 1 province = var:ROOT.target_province } }
				}
				actor_effects = {
					raid_damage_units = { plane_loss = 25 ratio = no }
					raid_add_unit_experience = 0.1
				}
				visual_effect = { entity = "air_raids_naval_limited_success_entity" animation = "attack" }
			}
			success = {
				victim_effects = {
					var:target_state = { damage_building = { type = naval_base damage = 2 province = var:ROOT.target_province } }
				}
				actor_effects = {
					raid_damage_units = { plane_loss = 15 ratio = no }
					raid_add_unit_experience = 0.15
					add_raid_history_entry = yes
				}
				visual_effect = { entity = "air_raids_naval_success_entity" animation = "attack" }
			}
			critical_success = {
				victim_effects = {
					var:target_state = { damage_building = { type = naval_base damage = 3 province = var:ROOT.target_province } }
				}
				actor_effects = {
					raid_damage_units = { plane_loss = 5 ratio = no }
					raid_add_unit_experience = 0.2
					add_raid_history_entry = yes
					var:actor_country = { add_political_power = 25 }
				}
				visual_effect = { entity = "air_raids_naval_critical_success_entity" animation = "attack" }
			}
		}
	}
}
```

Localisation:

```text
 raid_type_mod_port_strike: "Port Strike"
 raid_type_mod_port_strike_desc: "Bombers hit an enemy naval base to wreck its wharves."
```

A new category for it, in `common/raids/categories/mod_raid_categories.txt`, with the text and sprites it needs:

```text
categories = {
	mod_sabotage_raids = {
		intel_source = army
		visible = { has_dlc = "Thunder at Our Gates" }
	}
}
```

```text
 raid_category_mod_sabotage_raids: "Sabotage"
 raid_category_header_mod_sabotage_raids: "Sabotage Raids"
 tooltip_raid_category_mod_sabotage_raids: "Small sabotage raids behind enemy lines."
 raid_category_fluff_text_mod_sabotage_raids: "Saboteur Command"
```

Sprites named `GFX_raid_category_small_mod_sabotage_raids` and `GFX_raid_unit_icon_mod_sabotage_raids` replace the `unknown` fallbacks [vanilla-confirmed 1.19.3] `interface/military_raids/military_raids.gfx`.

## Confirmed traps <a id="Confirmed_traps"></a>

| Trap | What the files show | Evidence |
| --- | --- | --- |
| `target_types` (plural) from the documentation template | vanilla uses `target_type` in 37 of 37 types; the plural is not a string in `hoi4.exe` | [vanilla-confirmed 1.19.3], string search; that the plural is ignored is [unverified] |
| `preparation_time` and `cost` from the template | vanilla uses `days_to_prepare` and `command_power`; `preparation_time` is not a standalone string in `hoi4.exe` | [vanilla-confirmed 1.19.3], string search |
| Writing a type or category without its root block | all vanilla files use `types = { }` or `categories = { }` | [vanilla-confirmed 1.19.3]; effect of omitting [unverified] |
| `agility` from the documentation's success example | the predefined modifier is `air_agility` | [vanilla-confirmed 1.19.3] |
| Looking for `radar` in the modifier list | it is used by vanilla and missing from the documentation | [vanilla-confirmed 1.19.3] |
| Country or state effects directly in `actor_effects` or `victim_effects` | both blocks start in raid instance scope; vanilla always enters `var:...` first | [docs], [vanilla-confirmed 1.19.3] |
| `building = { type = <tag> }` | the documentation says `type` takes a type or tag; vanilla uses `type` for ids and `tags` for tags | [docs], [vanilla-confirmed 1.19.3] |
| `province = any` without `free_targeting` | the only types using it are in the one category that sets `free_targeting = yes` | [docs], [vanilla-confirmed 1.19.3] |
| `weight` of an `ai_will_do` pushed to 0 by a negative add | the AI never does the raid; the vanilla comment advises `factor` over negative `add` | [docs], [vanilla-confirmed 1.19.3] |
| `critical` read as an absolute chance | it is conditional on success; `disaster` is not | [docs] |
| Putting the same amount in `essential_equipment` and `additional_equipment` and expecting double | the larger amount is used | [docs] |
| Re-raiding the same target quickly | without `days_re_enable` the cooldown is 365 days | [docs] `raids/_documentation.md`, [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` |
| `failure` shown as "Critical Failure" | `failure`, "critical failure" and "disaster" are one outcome | [docs], [vanilla-confirmed 1.19.3] |
| `provinve` in the `launch_nuke` documentation | the documentation example spells the key `provinve`; vanilla uses `province` | [docs] `documentation/effects_documentation.md`, [vanilla-confirmed 1.19.3] |
| `use_nuke = yes` in an outcome of a type that already lists `nukes` in `essential_equipment` | would consume a second nuke; vanilla always writes `use_nuke = no` there | [docs], [vanilla-confirmed 1.19.3] (13 of 13); the double use is [unverified] |
| Reading `ROOT` as the acting country inside `target_type` state filters | not settled by any game file | [unverified] |

## Practice notes (kit skill) <a id="Practice_notes"></a>

These rules come from the kit's `hoi4-native-raids` skill and were checked against the files above.

- Put the cost of creating a raid in `essential_equipment` and `command_power`, and do not debit or refund the same cost in an outcome: the documentation defines both as native payments [docs] `raids/_documentation.md`. Vanilla shows the pattern: the nuclear types take the nuke with `essential_equipment = { nukes = 1 }`, and all 13 of their `launch_nuke` calls say `use_nuke = no` [vanilla-confirmed 1.19.3] `raids/nuclear_raids.txt`; the reason, avoiding a second consumption, is inferred [unverified]. Promising refunds on cancellation is [unverified].
- Keep country helpers that need the acting country as `ROOT` out of the raid instance: enter `var:actor_country` first, or fire an event from there, as vanilla does with delayed events [vanilla-confirmed 1.19.3]. A hidden actor event with saved event targets is the kit's pattern [unverified].
- For several raid types that share one reward path, use separate markers (flags or fixed hidden events) per type; a single pending variable can be overwritten by raids that end together [unverified].
- Credit a delayed reward or achievement only from the outcome block that ran, not from raid creation: no creation hook exists in the documentation [docs], [vanilla-confirmed 1.19.3] (the only completion records are flags and events set inside outcomes).
- At resolution, test again the target and actor that make the effect valid; the final `success_levels` effects run whatever `launchable` said earlier [unverified].

## See also <a id="See_also"></a>

- [Special project modding](<special-project-modding.md>): facilities, projects and the `facility_strike` link.
- [Effects](<effects.md#Raid_scope>), [Defines](<defines.md#NRaids>), [AI modding](<ai-modding.md>), [Localisation](<localisation.md>), [Interface modding](<interface-modding.md>).

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list-of-modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on-actions.md>) • [Data structures](<data-structures.md>) • [Flags](<data-structures.md#Flags>) • [Event targets](<data-structures.md#Event_targets>) • [Country tag aliases](<data-structures.md#Country_tag_aliases>) • [Variables](<data-structures.md#Variables>) • [Arrays](<data-structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement-modding.md>) • [AI](<ai-modding.md>) • [AI focuses](<ai-focuses.md>) • [Autonomous states](<autonomy-state-modding.md>) • [Balances of power](<balance-of-power-modding.md>) • [Bookmarks/Scenarios](<bookmark-modding.md>) • [Game rules](<bookmark-modding.md#Game_rules>) • [Buildings](<building-modding.md>) • [Characters and traits](<character-modding.md>) • [Cosmetic tags](<cosmetic-tag-modding.md>) • [Countries](<country-creation.md>) • [Divisions](<division-modding.md>) • [Decisions](<decision-modding.md>) • [Doctrines](<doctrine-modding.md>) • [Equipment](<equipment-modding.md>) • [Events](<event-modding.md>) • [Factions](<faction-modding.md>) • [Ideas](<idea-modding.md>) • [Ideologies](<ideology-modding.md>) • [Military industrial organizations](<military-industrial-organization-modding.md>) • [National focuses](<national-focus-modding.md>) • [Resources](<resources-modding.md>) • [Scripted GUI](<scripted-gui-modding.md>) • [Technologies and doctrines](<technology-modding.md>)
- **Map**: [Map](<map-modding.md>) • [States](<state-modding.md>) • [Supply areas](<supply-areas-modding.md>) • [Strategic regions](<strategic-region-modding.md>)
- **Graphical**: [Interface](<interface-modding.md>) • [Graphical assets](<graphical-asset-modding.md>) • [Entities](<entity-modding.md>) • [Posteffects](<posteffect-modding.md>) • [Particles](<particle-modding.md>) • [Fonts](<font-modding.md>)
- **Cosmetic**: [Portraits](<portrait-modding.md>) • [Namelists](<namelist-modding.md>) • [Music](<music-modding.md>) • [Sound](<sound-modding.md>)
- **Other**: [Console commands](<console-commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod-structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection-modding.md>) • [Defines additions](<defines-additions.md>) • [Game rule modding](<game-rule-modding.md>) • [Intelligence operation modding](<intelligence-operation-modding.md>) • [Map mode modding](<map-mode-modding.md>) • [Occupation and resistance modding](<occupation-and-resistance-modding.md>) • [Peace conference modding](<peace-conference-modding.md>) • [Raid modding](<raid-modding.md>) • [Script constant modding](<script-constant-modding.md>) • [Special project modding](<special-project-modding.md>)
