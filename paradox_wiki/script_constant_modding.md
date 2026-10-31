# Script constant modding

*Kit page: written by the Agentic HOI4 Modding Kit from the Hearts of Iron IV 1.19.3.0 game files. The wiki has no page for this topic. CC BY-SA 3.0 (see LICENSE.txt).*
<!-- kit:page -->

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" sources="common/script_constants/ documentation/script_concept_documentation.md documentation/triggers_documentation.md documentation/effects_documentation.md common/special_projects/ common/collections/ common/factions/goals/ common/decisions/ localisation/english/TAOG_decisions_l_english.yml" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Written from `common/script_constants/documentation.md`, the script constants section of the script concept document, the 4 vanilla constant files, and every `constant:` and bare constant reference found in vanilla script and localisation.
- Documentation conflicts found (a misprinted reference form, an out-of-date schema note) and one vanilla schema mismatch are listed under Confirmed traps.
- Gaps left: behaviour when a schema is violated, when two files share a category name, and whether constants can be nested inside `@` values; nothing was run in the game.
<!-- kit:end id="review" -->

## Table of contents

- [Overview](#Overview)
- [File layout](#File_layout)
- [Schema and value types](#Schema_and_value_types)
- [Vanilla constants](#Vanilla_constants)
- [Referencing a constant](#Referencing_a_constant)
  - [In script values](#Reference_in_script)
  - [Bare form in documented parameters](#Reference_bare_form)
  - [Lists as targets and collection inputs](#Reference_lists)
  - [In localisation](#Reference_in_localisation)
- [Scoping and naming](#Scoping_and_naming)
- [Interaction with @ constants](#Interaction_with_at_constants)
- [Reloading](#Reloading)
- [Short example](#Short_example)
- [Limits](#Limits)
- [Confirmed traps](#Confirmed_traps)

---

A script constant is a named value, or a named list, that is defined once in `common/script_constants/` and reused from other script files, from collections and from localisation. Unlike the file-local `@` constants, it is global and typed by a schema. [docs] `documentation/script_concept_documentation.md`, `common/script_constants/documentation.md`.

## Overview <a id="Overview"></a>

- Constants define simple and complex script values that are reusable in different files. Only parameters that are documented to support script constants accept them. [docs] `common/script_constants/documentation.md`.
- Script constants can replace the script macro `@` where a value should be shared between files. They have a negligible load time cost and no runtime cost. [docs] `documentation/script_concept_documentation.md`.
- A constant is read through its category and key path, for example `constant:propaganda.SIA.propaganda_cost_increase`. [vanilla-confirmed 1.19.3] `common/scripted_effects/SIA_scripted_effects.txt`.
- Vanilla ships 4 constant files with 9 categories. They are used by special projects, the propaganda decisions and scripted effects of the SIA tag, faction goals, collections, one Chinese decision and one Nordic scripted trigger. [vanilla-confirmed 1.19.3] `common/script_constants/` and the files named below.

Related pages: [Data structures](<data_structures.md#Constants>) for `@` constants, [Localisation](<localisation.md#Formatting_variables>) for `[?variable]`, [Collection modding](<collection_modding.md>), [Triggers](<triggers.md#Any_scope>).

## File layout <a id="File_layout"></a>

- Folder: `common/script_constants/`, any number of `.txt` files. [docs] `common/script_constants/documentation.md`.
- Vanilla files: `country_groups.txt`, `propaganda_campaigns.txt`, `special_project_constants.txt`, `state_groups.txt`. [vanilla-confirmed 1.19.3] `common/script_constants/`.
- One file can hold several categories, as `special_project_constants.txt` does (6 categories). [vanilla-confirmed 1.19.3]
- Each category is a top-level block. Its first entry must be `schema`; the data entries follow. [docs] `common/script_constants/documentation.md`.

```text
category_name = {
    schema = {
        any_key = yes
        data = int
    }
    small = 10
    large = 40
}
```

[docs] shape from `common/script_constants/documentation.md`; [vanilla-confirmed 1.19.3] the same shape in `special_project_constants.txt` (`sp_scientist_xp_gain`).

## Schema and value types <a id="Schema_and_value_types"></a>

| Schema entry | Meaning | Source |
| --- | --- | --- |
| `key = name` | The data entries must use this exact key; mutually exclusive with `any_key` | [docs] |
| `any_key = yes` | Any key is accepted; the docs describe it as alphabetic characters with no dots | [docs] |
| `data = int` | The value is an integer | [docs] |
| `data = fixed_point` | The value is a floating point number | [docs] |
| `data = { ... }` | A complex entry: a list of schema objects, each with its own `key` or `any_key` and `data` | [docs] |
| `array = country` | The entries are lists of country tags | [vanilla-confirmed 1.19.3] `country_groups.txt` |
| `array = state` | The entries are lists of state ids | [vanilla-confirmed 1.19.3] `state_groups.txt` |

All [docs] rows: `common/script_constants/documentation.md`.

Shapes used by vanilla, with the key path they produce:

| Schema | Data | Reference path |
| --- | --- | --- |
| `any_key`, `data = int` | `low = 70` | `category.low` |
| `any_key`, `data = { { any_key = yes data = fixed_point } }` | `gain = { low = 0.05 }` | `category.gain.low` |
| `any_key`, `data = { { key = min data = int } { key = max data = int } }` | `small = { min = 15 max = 25 }` | `category.small` (whole entry) |
| `any_key`, `array = country` | `nordics = { SWE NOR FIN DEN ICE }` | `category.nordics` |

All rows: [vanilla-confirmed 1.19.3] `common/script_constants/*.txt`.

- The documentation says `any_key` accepts alphabetic characters, but vanilla keys include upper case, digits and underscores (`SIA`, `continental_europe_1936`). Treat the "alphabetic" note as loose. [docs] `common/script_constants/documentation.md`; [vanilla-confirmed 1.19.3] `propaganda_campaigns.txt`, `country_groups.txt`.
- `int` is for whole numbers and `fixed_point` for floating point numbers, so any non-integer value needs `fixed_point`. [docs] `common/script_constants/documentation.md`.

## Vanilla constants <a id="Vanilla_constants"></a>

| Category | File | Entries | Used as | Vanilla references |
| --- | --- | --- | --- | --- |
| `country_groups` | `country_groups.txt` | `nordics`, `continental_europe_1936`, `literally_china`, `chinese_warlords`, `islamic_world` | `target` of country iterators; collection input | 5 (`chinese_warlords` unused) |
| `state_groups` | `state_groups.txt` | `balkans`, `comintern_starting_border`, `mare_nostrum_states`, `pax_romana_states`, `central_powers_border_states` | Collection input | 9 |
| `propaganda` | `propaganda_campaigns.txt` | `SIA` with 11 keys (slot indexes, costs, campaign durations) | Variable values, `days_remove`, event `days`, loc | 74 |
| `sp_complexity` | `special_project_constants.txt` | `small`, `medium`, `large`, `insane`, each with `min` and `max` | Bare `complexity = sp_complexity.large` | 49 |
| `sp_time` | `special_project_constants.txt` | `prototype` with `short`, `medium`, `long`, `very_long` | Bare `prototype_time = sp_time.prototype.long` | 49 |
| `sp_scientist_xp_gain` | `special_project_constants.txt` | `low`, `medium`, `high`, `very_high` | `experience = constant:...` | 57 |
| `sp_progress` | `special_project_constants.txt` | `gain` and `loss`, each `low`, `medium`, `high` | `add_project_progress_ratio = constant:...` | 81 |
| `sp_military_xp_gain` | `special_project_constants.txt` | `low`, `medium`, `high` | `army_experience`, `navy_experience`, `air_experience` | 9 |
| `sp_breakthrough_progress` | `special_project_constants.txt` | `low`, `medium`, `high` | Bare `value = sp_breakthrough_progress.medium` in `add_breakthrough_progress` | 21 |

All rows: [vanilla-confirmed 1.19.3] `common/script_constants/`, references counted over `common/`, `events/`, `history/`, `interface/` and `localisation/english/` (occurrences, bare and prefixed forms counted by category).

## Referencing a constant <a id="Referencing_a_constant"></a>

### In script values <a id="Reference_in_script"></a>

- Any scoped variable accepts a script constant that points to a single fixed-point value, through the prefix `constant:`. [docs] `documentation/script_concept_documentation.md`.
- Pattern: `constant:<category>.<key>` or `constant:<category>.<key>.<key>`. [vanilla-confirmed 1.19.3] `constant:sp_scientist_xp_gain.low`, `constant:sp_progress.gain.medium`, `constant:propaganda.SIA.propaganda_empty_slot_index`.
- Vanilla uses it as the right-hand side of variable effects and checks, and as a value for timers and rewards. [vanilla-confirmed 1.19.3] `common/scripted_effects/SIA_scripted_effects.txt`:

```text
set_variable = { SIA_new_propaganda_campaign_duration = constant:propaganda.SIA.default_propaganda_campaign_duration }
check_variable = { SIA_poster_left_icon_frame = constant:propaganda.SIA.propaganda_empty_slot_index }
multiply_variable = { SIA_propaganda_cost = constant:propaganda.SIA.propaganda_cost_increase }
country_event = { id = TAOG_siam_movie_campaign_events.101 days = constant:propaganda.SIA.default_propaganda_campaign_old_days }
```

- Other vanilla positions: `days_remove` and `days_re_enable` in decisions (`common/decisions/SIA.txt`), `experience = constant:sp_scientist_xp_gain.very_high` and `add_project_progress_ratio = constant:sp_progress.gain.high` in special project rewards, and `check_variable` inside a scripted trigger and a scripted localisation. [vanilla-confirmed 1.19.3] `common/special_projects/`, `common/scripted_triggers/SIA_scripted_triggers.txt`, `common/scripted_localisation/TAOG_SIA_scripted_loc.txt`.

### Bare form in documented parameters <a id="Reference_bare_form"></a>

- Some parameters are documented to take a constant directly, without the `constant:` prefix: `add_breakthrough_progress` (`value`), `add_design_template_bonus` (`uses`, `cost_factor`) and `reduce_focus_completion_cost` (`cost`). [docs] `documentation/effects_documentation.md`.
- Vanilla uses the bare form for special project fields: `prototype_time = sp_time.prototype.medium`, `complexity = sp_complexity.medium` and `value = sp_breakthrough_progress.low`. `complexity` takes the whole `{ min max }` entry. [vanilla-confirmed 1.19.3] `common/special_projects/projects/land_projects.txt`.
- The concept document shows the same bare style, `some_fixed_point_supporting_constants = numeric_constants.e`, next to the prefixed `some_scoped_variable = constant:numeric_constants.pi`. [docs] `documentation/script_concept_documentation.md`.
- Which parameters accept the bare form, and which accept only the prefixed form, is decided per parameter. When in doubt, use `constant:` only in variable positions and copy the bare form from vanilla only for the parameters above. [unverified] beyond the listed cases.

### Lists as targets and collection inputs <a id="Reference_lists"></a>

- Six triggers accept a constant list in `target`: `all_country_of`, `any_country_of`, `any_country_with_original_tag_of`, `any_other_country_of`, `any_other_country_with_original_tag_of` and `any_state_of`. [docs] `documentation/triggers_documentation.md`.

```text
any_other_country_with_original_tag_of = {
    target = constant:country_groups.nordics
    has_defensive_war = yes
}
```

[vanilla-confirmed 1.19.3] `common/scripted_triggers/NORDIC_scripted_triggers.txt`. The trigger documentation prints the path with a colon, `constant:country_groups:nordics`; see Confirmed traps.

- A list constant can be the `input` of a collection, named or inline: `input = constant:state_groups.balkans`. See [Collection modding](<collection_modding.md#Inputs>). [docs] `documentation/script_collection_input.md`; [vanilla-confirmed 1.19.3] `common/collections/collections.txt` (11 uses) and `common/factions/goals/faction_goals_medium_term.txt`.
- A list constant cannot be used where a single number is expected. The concept document limits variable use to constants that point to a single fixed-point value. [docs] `documentation/script_concept_documentation.md`.

### In localisation <a id="Reference_in_localisation"></a>

- Vanilla reads a constant in a localisation string through the variable display syntax: `[?constant:propaganda.SIA.default_propaganda_campaign_cooldown]`. It is the only use in the English localisation. [vanilla-confirmed 1.19.3] `localisation/english/TAOG_decisions_l_english.yml` (`SIA_propaganda_campaign_cooldown_tt`).

```text
SIA_propaganda_campaign_cooldown_tt: "This campaign will be available again [?constant:propaganda.SIA.default_propaganda_campaign_cooldown] days after its removal."
```

- Formatting characters after a pipe, such as `[?constant:...|0]`, follow the normal `[?variable]` rules. See [Localisation](<localisation.md#Formatting_variables>). [unverified] for constants specifically.
- No other loc syntax for constants is documented, and no interface file references one. [vanilla-confirmed 1.19.3] searched `localisation/`, `interface/`.

## Scoping and naming <a id="Scoping_and_naming"></a>

- Constants are global database entries, and every scoped variable can read them through the `constant:` prefix. [docs] `common/script_constants/documentation.md`.
- The category is the first path segment and must be unique in the database. Vanilla categories never repeat across files. What happens when a mod reuses a vanilla category or defines the same category twice is [unverified]. [vanilla-confirmed 1.19.3] `common/script_constants/`.
- Prefix your own categories with the mod tag (`MYM_costs`) so they cannot collide. [unverified]
- Keys cannot contain dots. [docs] `common/script_constants/documentation.md`. The dot is the path separator in every vanilla reference. [vanilla-confirmed 1.19.3]
- Keys inside one category follow the schema: `any_key = yes` accepts any key, `key = name` accepts exactly that one. [docs] `common/script_constants/documentation.md`.
- Constants can be used in any script file except for other script constants files. [docs] `documentation/script_concept_documentation.md`.

## Interaction with @ constants <a id="Interaction_with_at_constants"></a>

| | `@` constant | Script constant |
| --- | --- | --- |
| Defined | In the file that uses it, as `@NAME = value` | In `common/script_constants/` |
| Visible in | That file only | Any script file except other script constant files |
| Types | Numbers and strings, and used in `.gui` files too | Schema types: `int`, `fixed_point`, nested entries, lists of countries or states |
| Reference | `@NAME` | `constant:category.key`, or the bare path where documented |
| Works everywhere | In most script and interface files | Only in parameters documented to support it |

The script constant column: [docs] `documentation/script_concept_documentation.md` and `common/script_constants/documentation.md`. The `@` column: the concept document calls `@` file local; the rest is the wiki's description on [Data structures](<data_structures.md#Constants>). [unverified]

- No vanilla line combines the two: nothing writes `@NAME = constant:...` or puts `@` inside a script constant file. Whether either works is [unverified]. [vanilla-confirmed 1.19.3] searched `common/`, `events/`, `history/`, `interface/`.
- Use `@` for a value shared inside one file, for strings, and for interface coordinates. Use a script constant for a number or list that several files, collections or tooltips need. [unverified] recommendation drawn from the two descriptions above.
- 41 vanilla files define `@` constants at the top level; none of them is a script constant file. [vanilla-confirmed 1.19.3] counted over `common/`, `events/`, `history/` and `interface/`.

## Reloading <a id="Reloading"></a>

- Script constants are injected into the script when it loads. Reloading the script constant database is not enough: after it, the database that uses the constant must be reloaded too. [docs] `documentation/script_concept_documentation.md`, `common/script_constants/documentation.md`.
- In practice, restart the game after changing a constant file instead of relying on a partial reload. [unverified]

## Short example <a id="Short_example"></a>

`common/script_constants/MYM_constants.txt`:

```text
MYM_costs = {
    schema = {
        any_key = yes
        data = int
    }
    small = 10
    large = 40
}

MYM_groups = {
    schema = {
        any_key = yes
        array = country
    }
    baltic = { EST LAT LIT }
}
```

Use in script:

```text
set_variable = { MYM_current_cost = constant:MYM_costs.large }
any_other_country_with_original_tag_of = {
    target = constant:MYM_groups.baltic
    has_war = yes
}
```

Use in a localisation entry: `MYM_cost_tt: "Costs [?constant:MYM_costs.large] political power."`

The example combines the schema shapes of `sp_scientist_xp_gain` and `country_groups` with the reference forms from vanilla. It was not run in the game. [vanilla-confirmed 1.19.3] shapes; [unverified] runtime.

## Limits <a id="Limits"></a>

- Constants work only where a parameter says it supports them. The documented ones are the variable positions, the six `target` triggers, collection `input` and the three effects named above. [docs] `common/script_constants/documentation.md`, `documentation/triggers_documentation.md`, `documentation/effects_documentation.md`, `documentation/script_collection_input.md`.
- Vanilla also uses constants in the special project fields `prototype_time`, `complexity` and `add_breakthrough_progress`, which the special project documentation does not describe as constant-aware. [vanilla-confirmed 1.19.3] `common/special_projects/projects/land_projects.txt`.
- A variable accepts a single fixed-point value only. Entries with `min`/`max` and country or state lists work only in parameters that expect that shape. [docs] `documentation/script_concept_documentation.md`.
- A constant file cannot use other script constants. [docs] `documentation/script_concept_documentation.md`. No expression syntax for constants is documented. [unverified]
- Changes need a script reload that follows the database reload; see [Reloading](#Reloading). [docs]
- No effect or trigger sets or changes a constant at run time. They are fixed data. [unverified] no such effect is documented.

## Confirmed traps <a id="Confirmed_traps"></a>

- The trigger documentation writes the constant path with a colon, `constant:country_groups:nordics`. Vanilla and the concept document use a dot: `constant:country_groups.nordics`. Use the dot. [docs] `documentation/triggers_documentation.md` (six triggers); [vanilla-confirmed 1.19.3] `common/scripted_triggers/NORDIC_scripted_triggers.txt`.
- The same trigger examples use `country_groups` for `any_state_of`, which wants a list of states. Use a `state_groups` entry or another `array = state` constant there. [docs] `documentation/triggers_documentation.md`; [unverified] that a country list fails in a state iterator.
- The effect documentation's `cost_factor = cost.high` example refers to a constant `cost` that does not exist in vanilla. Define it yourself before copying it. [docs] `documentation/effects_documentation.md`; [vanilla-confirmed 1.19.3] no `cost` category in `common/script_constants/`.
- `propaganda_campaigns.txt` declares `data = int` for the `SIA` keys but gives `propaganda_cost_increase` the value `1.35`, and vanilla multiplies a variable by it. Whether the engine rounds it is [unverified]; declare `fixed_point` for any non-integer in your own files. [vanilla-confirmed 1.19.3] `common/script_constants/propaganda_campaigns.txt`, `common/scripted_effects/SIA_scripted_effects.txt`.
- The special project documentation lists `complexity` values as the enums `simple`, `medium`, `complex`, `very_complex`, `insane`. The real constant keys are `small`, `medium`, `large`, `insane`. [docs] `common/special_projects/special_projects_documentation.md`; [vanilla-confirmed 1.19.3] `common/script_constants/special_project_constants.txt`.
- The documentation's `sp_complexity` example shows `small` as 20 to 30 while vanilla has 15 to 25; the documentation example is illustrative. [docs] and [vanilla-confirmed 1.19.3]
- `sp_basic_research_time` appears only in the documentation example. It is not a vanilla constant. [docs] `common/script_constants/documentation.md`; [vanilla-confirmed 1.19.3] no such category.
- Constants are not available everywhere `@` is. Using one in a parameter that is not documented to support it is not a documented case, so check the parameter against the lists above. [docs] `common/script_constants/documentation.md`.
- Reloading only the constant database leaves old values in scripts that are already loaded. [docs] `documentation/script_concept_documentation.md`.

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
