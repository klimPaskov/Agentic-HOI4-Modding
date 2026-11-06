# Script constant modding

A script constant is a named value, or a named list, that is defined once in `common/script_constants/` and reused from other script files, from collections and from localisation. Unlike the file-local `@` constants, it is global and typed by a schema.

## Overview

- Constants define simple and complex script values that are reusable in different files. Only parameters that are documented to support script constants accept them.
- Script constants can replace the script macro `@` where a value should be shared between files. They have a negligible load time cost and no runtime cost.
- A constant is read through its category and key path, for example `constant:propaganda.SIA.propaganda_cost_increase`.
- Vanilla ships 4 constant files with 9 categories. They are used by special projects, the propaganda decisions, scripted effects, scripted triggers and scripted localisation of the SIA tag, faction goals, collections, three more decision files (`BUL.txt`, `CHI_decisions.txt`, `NORDIC.txt`), three focus files (`bulgaria.txt`, `china_communist_sea.txt`, `china_nationalist_sea.txt`) and one Nordic scripted trigger.

Related pages: [Data structures](data_structures.md#constants) for `@` constants, [Localisation](localisation.md#formatting-variables) for `[?variable]`, [Collection modding](collection_modding.md), [Triggers](triggers.md#any-scope).

## File layout

- Folder: `common/script_constants/`, any number of `.txt` files.
- Vanilla files: `country_groups.txt`, `propaganda_campaigns.txt`, `special_project_constants.txt`, `state_groups.txt`.
- One file can hold several categories, as `special_project_constants.txt` does (6 categories).
- Each category is a top-level block. Its first entry must be `schema`; the data entries follow.

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

## Schema and value types

| Schema entry | Meaning | Source |
| --- | --- | --- |
| `key = name` | The data entries must use this exact key; mutually exclusive with `any_key` | |
| `any_key = yes` | Any key is accepted; the docs describe it as alphabetic characters with no dots | |
| `data = int` | The value is an integer | |
| `data = fixed_point` | The value is a floating point number | |
| `data = { ... }` | A complex entry: a list of schema objects, each with its own `key` or `any_key` and `data` | |
| `array = country` | The entries are lists of country tags | |
| `array = state` | The entries are lists of state ids | |

Shapes used by vanilla, with the key path they produce:

| Schema | Data | Reference path |
| --- | --- | --- |
| `any_key`, `data = int` | `low = 70` | `category.low` |
| `any_key`, `data = { { any_key = yes data = fixed_point } }` | `gain = { low = 0.05 }` | `category.gain.low` |
| `any_key`, `data = { { key = min data = int } { key = max data = int } }` | `small = { min = 15 max = 25 }` | `category.small` (whole entry) |
| `any_key`, `array = country` | `nordics = { SWE NOR FIN DEN ICE }` | `category.nordics` |

- The documentation says `any_key` accepts alphabetic characters, but vanilla keys include upper case, digits and underscores (`SIA`, `continental_europe_1936`). Treat the "alphabetic" note as loose.
- `int` is for whole numbers and `fixed_point` for floating point numbers, so any non-integer value needs `fixed_point`.

## Vanilla constants

| Category | File | Entries | Used as | Vanilla references |
| --- | --- | --- | --- | --- |
| `country_groups` | `country_groups.txt` | `nordics`, `continental_europe_1936`, `literally_china`, `chinese_warlords`, `islamic_world` | `target` of country iterators; collection input | 10 (`chinese_warlords` unused) |
| `state_groups` | `state_groups.txt` | `balkans`, `comintern_starting_border`, `mare_nostrum_states`, `pax_romana_states`, `central_powers_border_states`, `bul_black_sea_states`, `bul_aegean_sea_states`, `bul_adriatic_sea_states` | Collection input; `target` of `any_state_of` | 18 |
| `propaganda` | `propaganda_campaigns.txt` | `SIA` with 11 keys (slot indexes, costs, campaign durations) | Variable values, `days_remove`, event `days`, loc | 71 |
| `sp_complexity` | `special_project_constants.txt` | `small`, `medium`, `large`, `insane`, each with `min` and `max` | Bare `complexity = sp_complexity.large` | 49 |
| `sp_time` | `special_project_constants.txt` | `prototype` with `short`, `medium`, `long`, `very_long` | Bare `prototype_time = sp_time.prototype.long` | 49 |
| `sp_scientist_xp_gain` | `special_project_constants.txt` | `low`, `medium`, `high`, `very_high` | `experience = constant:...` | 57 |
| `sp_progress` | `special_project_constants.txt` | `gain` and `loss`, each `low`, `medium`, `high` | `add_project_progress_ratio = constant:...` | 81 |
| `sp_military_xp_gain` | `special_project_constants.txt` | `low`, `medium`, `high` | `army_experience`, `navy_experience`, `air_experience` | 9 |
| `sp_breakthrough_progress` | `special_project_constants.txt` | `low`, `medium`, `high` | Bare `value = sp_breakthrough_progress.medium` in `add_breakthrough_progress` | 21 |

## Referencing a constant

### In script values

- Any scoped variable accepts a script constant that points to a single fixed-point value, through the prefix `constant:`.
- Pattern: `constant:<category>.<key>` or `constant:<category>.<key>.<key>`.
- Vanilla uses it as the right-hand side of variable effects and checks, and as a value for timers and rewards.

```text
set_variable = { SIA_new_propaganda_campaign_duration = constant:propaganda.SIA.default_propaganda_campaign_duration }
check_variable = { SIA_poster_left_icon_frame = constant:propaganda.SIA.propaganda_empty_slot_index }
multiply_variable = { SIA_propaganda_cost = constant:propaganda.SIA.propaganda_cost_increase }
country_event = { id = TAOG_siam_movie_campaign_events.101 days = constant:propaganda.SIA.default_propaganda_campaign_old_days }
```

- Other vanilla positions: `days_remove` and `days_re_enable` in decisions (`common/decisions/SIA.txt`), `experience = constant:sp_scientist_xp_gain.very_high` and `add_project_progress_ratio = constant:sp_progress.gain.high` in special project rewards, and `check_variable` inside a scripted trigger and a scripted localisation.

### Bare form in documented parameters

- Some parameters are documented to take a constant directly, without the `constant:` prefix: `add_breakthrough_progress` (`value`), `add_design_template_bonus` (`uses`, `cost_factor`) and `reduce_focus_completion_cost` (`cost`).
- Vanilla uses the bare form for special project fields: `prototype_time = sp_time.prototype.medium`, `complexity = sp_complexity.medium` and `value = sp_breakthrough_progress.low`. `complexity` takes the whole `{ min max }` entry.
- The concept document shows the same bare style, `some_fixed_point_supporting_constants = numeric_constants.e`, next to the prefixed `some_scoped_variable = constant:numeric_constants.pi`.
- Which parameters accept the bare form, and which accept only the prefixed form, is decided per parameter. When in doubt, use `constant:` only in variable positions and copy the bare form from vanilla only for the parameters above. (unverified) beyond the listed cases. In a variable position the bare form is not accepted: assigning the bare `cat.key` to a variable gave 0 with no error line, while `constant:cat.key` gave the value (40).

### Lists as targets and collection inputs

- Six triggers accept a constant list in `target`: `all_country_of`, `any_country_of`, `any_country_with_original_tag_of`, `any_other_country_of`, `any_other_country_with_original_tag_of` and `any_state_of`.

```text
any_other_country_with_original_tag_of = {
    target = constant:country_groups.nordics
    has_defensive_war = yes
}
```

The trigger documentation prints the path with a colon, `constant:country_groups:nordics`; see Confirmed traps.

- A list constant can be the `input` of a collection, named or inline: `input = constant:state_groups.balkans`. See [Collection modding](collection_modding.md#inputs).
- A list constant cannot be used where a single number is expected. The concept document limits variable use to constants that point to a single fixed-point value.

### In localisation

- Vanilla reads a constant in a localisation string through the variable display syntax: `[?constant:propaganda.SIA.default_propaganda_campaign_cooldown]`. It is the only use in the English localisation.

```text
SIA_propaganda_campaign_cooldown_tt: "This campaign will be available again [?constant:propaganda.SIA.default_propaganda_campaign_cooldown] days after its removal."
```

- Formatting characters after a pipe, such as `[?constant:...|0]`, follow the normal `[?variable]` rules. See [Localisation](localisation.md#formatting-variables). (unverified) for constants in general. In loc text `[?constant:cat.key|1]` gave 0.5 for a fixed point constant of 0.5, and `[?constant:MYM_costs.large|0]` gave 40.
- No other loc syntax for constants is documented, and no interface file references one.

## Scoping and naming

- Constants are global database entries, and every scoped variable can read them through the `constant:` prefix.
- The category is the first path segment and must be unique in the database. Vanilla categories never repeat across files: 9 categories in 4 files, each defined once. When two files define the same category, the entries merge and the later file wins for a key that both define, with no error: file a with `one = 1` and file b with `one = 2 two = 3` gave one = 2 and two = 3, and the mirrored pair (file a `one = 2 two = 3`, file b `one = 1`) gave one = 1 and two = 3. A mod file that repeated the vanilla category `sp_military_xp_gain` with all its keys plus a new key added the new key (8), and the vanilla key `high` stayed at 50. The vanilla copy repeated every vanilla key, so replace and merge look the same there, and the merge shows only in the mod to mod test. File order is assumed to be by name (a before b), since the names were not swapped.
- Prefix your own categories with the mod tag (`MYM_costs`) so they cannot collide. (unverified)
- Keys cannot contain dots. The dot is the path separator in every vanilla reference.
- Keys inside one category follow the schema: `any_key = yes` accepts any key, `key = name` accepts exactly that one.
- Constants can be used in any script file except for other script constants files.

## Interaction with @ constants

| | `@` constant | Script constant |
| --- | --- | --- |
| Defined | In the file that uses it, as `@NAME = value` | In `common/script_constants/` |
| Visible in | That file only | Any script file except other script constant files |
| Types | Numbers and strings, and used in `.gui` files too | Schema types: `int`, `fixed_point`, nested entries, lists of countries or states |
| Reference | `@NAME` | `constant:category.key`, or the bare path where documented |
| Works everywhere | In most script and interface files | Only in parameters documented to support it |

The `@` column: the concept document calls `@` file local. Vanilla defines top-level `@` constants in 43 files (23 `.gui`, 20 `.txt`) with numbers and quoted strings as values. "Works everywhere ... in most script and interface files" is the wiki's description on [Data structures](data_structures.md#constants) and stays unverified.

- No vanilla line combines the two: nothing writes `@NAME = constant:...` or puts `@` inside a script constant file. Both work anyway: `@IGC_B_G247 = constant:cat.key` gave 10, and an `@` macro used as a value inside a script constants file (`v = @igc_b_g247_c`) gave 5, with no error line.
- Use `@` for a value shared inside one file, for strings, and for interface coordinates. Use a script constant for a number or list that several files, collections or tooltips need. (unverified) recommendation drawn from the two descriptions above.
- 43 vanilla files define `@` constants at the top level; none of them is a script constant file.

## Reloading

- Script constants are injected into the script when it loads. Reloading the script constant database is not enough: after it, the database that uses the constant must be reloaded too.
- In practice, restart the game after changing a constant file instead of relying on a partial reload. (unverified)

## Short example

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

The example combines the schema shapes of `sp_scientist_xp_gain` and `country_groups` with the reference forms from vanilla. It was not run in the game, so how it behaves at run time is unverified.

## Limits

- Constants work only where a parameter says it supports them. The documented ones are the variable positions, the six `target` triggers, collection `input` and the three effects named above.
- Vanilla also uses constants in the special project fields `prototype_time`, `complexity` and `add_breakthrough_progress`, which the special project documentation does not describe as constant-aware.
- A variable accepts a single fixed-point value only. Entries with `min`/`max` and country or state lists work only in parameters that expect that shape.
- A constant file cannot use other script constants. No expression syntax for constants is documented: the concept document's math expression section does not mention script constants.
- Changes need a script reload that follows the database reload; see [Reloading](#reloading).
- No effect or trigger sets or changes a constant at run time. They are fixed data. That the engine offers no other way is unverified.

## Confirmed traps

- The trigger documentation writes the constant path with a colon, `constant:country_groups:nordics`. Vanilla and the concept document use a dot: `constant:country_groups.nordics`. Use the dot.
- The same trigger examples use `country_groups` for `any_state_of`, which wants a list of states. Use a `state_groups` entry or another `array = state` constant there. A country list fails in a state iterator: `any_state_of` with `target = constant:country_groups.nordics` logged "constant:country_groups.nordics is not an array of state ids" at load and read false, while a state list constant worked. The colon spelling `constant:country_groups:nordics` from the trigger documentation is not valid either: it read false and logged "Could not find constant category country_groups:nordics", so the engine reads `country_groups:nordics` as a category name.
- The effect documentation's `cost_factor = cost.high` example refers to a constant `cost` that does not exist in vanilla. Define it yourself before copying it.
- `propaganda_campaigns.txt` declares `data = int` for the `SIA` keys but gives `propaganda_cost_increase` the value `1.35`, and vanilla multiplies a variable by it. A non-integer under `data = int` is stored as a whole number with no error: a test constant of 1.35 under `data = int` read 1, and 0.5 under `data = fixed_point` kept its decimals. 1.35 became 1, so rounding and truncating cannot be told apart. Declare `fixed_point` for any non-integer in your own files.
- The special project documentation lists `complexity` values as the enums `simple`, `medium`, `complex`, `very_complex`, `insane`. The real constant keys are `small`, `medium`, `large`, `insane`.
- The documentation's `sp_complexity` example shows `small` as 20 to 30 while vanilla has 15 to 25; the documentation example is illustrative.
- `sp_basic_research_time` appears only in the documentation example. It is not a vanilla constant.
- Constants are not available everywhere `@` is. Using one in a parameter that is not documented to support it is not a documented case, so check the parameter against the lists above.
- Reloading only the constant database leaves old values in scripts that are already loaded.
