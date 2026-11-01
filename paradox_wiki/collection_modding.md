# Collection modding

*Kit page: written by the Agentic HOI4 Modding Kit from the Hearts of Iron IV 1.19.3.0 game files and re-checked against 1.19.4.1. The wiki has no page for this topic. CC BY-SA 3.0 (see LICENSE.txt).*
<!-- kit:page -->

<!-- kit:begin id="review" at="top" build="1.19.4.1" checked="2026-11-01" sources="common/collections/ documentation/script_collection_input.md documentation/script_collection_operator.md documentation/script_concept_documentation.md documentation/script_math_functions.md documentation/triggers_documentation.md documentation/effects_documentation.md localisation/english/collections_l_english.yml localisation/english/triggers_l_english.yml" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Written from `common/collections/_documentation.md`, the three collection concept and reference documents, the collection triggers and effects in the trigger and effect documentation, and all 74 vanilla named collections plus their uses in faction goals, manifests, decisions and focuses.
- Documentation conflicts found (operator filter key, comparison inclusivity, two misprinted examples) are listed under Confirmed traps.
- Gaps left: scope behaviour inside `every_collection_element` and `all_collection_elements` is only partly documented, and nothing was run in the game.
**1.19.4.1 re-check (2026-11-01).** 22 statements depended on files the update changed (vanilla scans of `common/`, `events/` and `history/`, the English collection and trigger localisation, and the two script-constant files) and all 22 were re-measured. The update adds an undocumented collection input, `game:all_majors`, used inline in 40 files, so `any_collection_element` went from 45 uses in 1 file to 180 in 42, vanilla consumers now include 7 decision, 20 focus and 18 event files, and the `operators` block count went from 345 to 348 (`faction_members` 186 to 189, `collection_size` 120 in 5 files to 122 in 6, `every_collection_element` 25 uses to 26). Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

## Table of contents

- [Overview](#Overview)
- [Collection structure](#Collection_structure)
- [Named collections](#Named_collections)
- [Inputs](#Inputs)
- [Operators](#Operators)
- [Inline collections](#Inline_collections)
- [Triggers and effects that use collections](#Consumers)
  - [Triggers](#Collection_triggers)
  - [Effects and math](#Collection_effects)
  - [Other keys that take a collection](#Other_collection_keys)
- [Scopes inside a collection](#Collection_scopes)
- [Tooltips and localisation](#Collection_tooltips)
- [Comparison notes](#Comparison_notes)
- [Examples](#Collection_examples)
- [Collections and loops](#Collections_and_loops)
- [Confirmed traps](#Confirmed_traps)

---

A collection is a group of scopable game objects of one type, such as countries or states, built from live game data where it is used. It lets one trigger count, test or iterate over things like "every state owned by any faction member". [docs] `common/collections/_documentation.md`, `documentation/script_concept_documentation.md`.

## Overview <a id="Overview"></a>

- A collection has an `input`, optional `operators` applied in order, and an optional `name`. [docs] `documentation/script_concept_documentation.md`.
- Collections are read-only descriptions. They cannot be stored in a variable or changed after the fact; they are rebuilt where they are used. [unverified] inferred from the docs, which describe no write operation.
- Define a named collection once in `common/collections/*.txt` and refer to it as `collection:<name>`, or write an anonymous collection inline where it is needed. [docs] `common/collections/_documentation.md`.
- Vanilla defines 74 named collections in two files, `collections.txt` (72) and `generic_collections.txt` (2). Every collection block in vanilla script (348 with `operators`) uses only the keys `input`, `operators` and `name`. [vanilla-confirmed 1.19.4.1] `common/collections/`, counted over `common/`, `events/` and `history/`.
- Vanilla consumers are faction goals and manifests (4 files, the large majority of the `operators` blocks), plus 7 decision files, 20 focus files and 18 event files. Most of those test `game:all_majors` with `any_collection_element`. [vanilla-confirmed 1.19.4.1] `common/factions/goals/`, `common/decisions/USA.txt`, `common/national_focus/germany.txt`, `japan.txt`, `chile.txt`, counted over `common/`, `events/` and `history/`.

Related pages: [Data structures](<data_structures.md#Arrays>) for arrays and loops, [Math functions](<data_structures.md#Math_functions>), [Faction modding](<faction_modding.md#Goals>), [Effects](<effects.md#Any_scope>), [Triggers](<triggers.md#Any_scope>), [Script constant modding](<script_constant_modding.md>).

## Collection structure <a id="Collection_structure"></a>

| Property | Meaning | Required |
| --- | --- | --- |
| `input` | The starting set; a reference such as `game:all_states`, `collection:NAME` or `constant:NAME`, or a nested collection block | Yes |
| `operators` | A list of steps applied to every item in order | No |
| `name` | Text that describes the collection in tooltips | No |

All rows: [docs] `documentation/script_concept_documentation.md`. Vanilla sets `name` on 67 of 74 named collections. [vanilla-confirmed 1.19.3] `common/collections/`.

- How it is built: each item of the input goes through the first operator, each result goes through the second, and so on. With input `game:scope` (a country) and operators `faction_members owned_states`, the first step gives every faction member and the second gives each member's owned states. [docs] `documentation/script_concept_documentation.md`.
- Shorthand: a collection that only has an input can be written as the input alone, so `my_collection = game:all_states` equals `my_collection = { input = game:all_states }`. [docs] `documentation/script_concept_documentation.md`.
- No uniqueness guarantee. If an operator reaches the same object through several items, the collection holds it several times, for example a state that is a core of several faction members. Counts include the repeats. [docs] `documentation/script_concept_documentation.md`.
- Operator order matters. In vanilla, `limit` is the last entry in every chain that has one (for example `faction_members controlled_states limit`). [vanilla-confirmed 1.19.4.1] counted over all 348 `operators` blocks; [unverified] that another order fails.

## Named collections <a id="Named_collections"></a>

Put the definition in any file under `common/collections/`. The block name must be unique. [docs] `common/collections/_documentation.md`.

```text
mymod_owned_coastal_states = {
    input = game:scope
    operators = {
        owned_states
        limit = { is_coastal = yes }
    }
    name = MYMOD_COLLECTION_OWNED_COASTAL_STATES
}
```

Use it with the `collection:` prefix: `input = collection:mymod_owned_coastal_states`. [docs] `common/collections/_documentation.md`.

- A named collection can use another named collection as its input, as vanilla does with `world_uncapitulated_democratic_countries` (input `collection:world_democratic_countries`). [vanilla-confirmed 1.19.3] `common/collections/collections.txt`.
- A named collection may use a script constant as input: `input = constant:state_groups.balkans`. [vanilla-confirmed 1.19.3] `common/collections/collections.txt` (11 uses).
- Names in vanilla are unique across the two files (74 of 74). Prefix your own names with the mod tag; what happens when a mod reuses a vanilla name is [unverified]. [vanilla-confirmed 1.19.3] `common/collections/`.
- Vanilla has two collections whose names equal the operator they wrap, `faction_members` and `country_and_all_subjects`, defined at the end of `generic_collections.txt`. The math iterator `every_collection` uses the first one by bare name. [vanilla-confirmed 1.19.3] `common/collections/generic_collections.txt`, `common/factions/goals/faction_goals_short_term.txt`.
- The `name` value is a localisation key; vanilla keys are `COLLECTION_*` entries in `localisation/english/collections_l_english.yml`. See [Tooltips and localisation](#Collection_tooltips). [vanilla-confirmed 1.19.4.1]

## Inputs <a id="Inputs"></a>

| Input | Needs scope | Gives | Documented in | Vanilla named collections using it |
| --- | --- | --- | --- | --- |
| `collection:NAME` | any | A named collection | input reference | 10 |
| `constant:NAME` | any | A script constant that holds a list, for example `constant:country_groups.islamic_world` | input reference | 11 |
| `game:all_countries` | any | All existing countries, including governments in exile | input reference | 13 |
| `game:all_majors` | any | A list of countries, named "Major Powers" in tooltips (not documented) | not documented | none |
| `game:all_possible_countries` | any | All countries, including those that do not exist | input reference | none |
| `game:all_states` | any | All existing states | input reference | 24 |
| `game:scope` | the scope object | The current scope object | input reference | 16 |
| `game:empty` | any | An empty collection | collections documentation only | none |
| `country:faction_members` | COUNTRY | All members of the country's faction, empty without a faction | collections documentation only | none |

All rows except `game:all_majors`: [docs] `documentation/script_collection_input.md` and `common/collections/_documentation.md` (the last two rows); the last column is [vanilla-confirmed 1.19.4.1] `common/collections/`, and a count of `none` also holds for all other vanilla script, except that `game:all_majors` is used inline in other script.

- `game:all_majors` appears in no documentation file. Vanilla script writes it 132 times in 40 files, always inline (131 times as `collection = game:all_majors` in `any_collection_element`, once as an `input`). The only other trace is the built-in tooltip name `COLLECTION_ALL_MAJORS`, "Major Powers". That it holds the major powers is inferred from the name and the uses. [vanilla-confirmed 1.19.4.1] `common/national_focus/chile.txt`, `common/decisions/CHL.txt`, `localisation/english/collections_l_english.yml`; [unverified] which countries it holds.

- `game:scope` is the object the trigger or effect runs on. Operators such as `faction_members` need that object to be a country. [docs] `common/collections/_documentation.md` ("Some collections require a scope"); [unverified] what happens in a wrong scope type.
- Type rule: the input sets the item type (countries or states), and an operator must fit that type. [unverified] inferred from the operator documentation.
- Every vanilla `constant:` input points to a list constant (`array = country` or `array = state` in its schema). See [Script constant modding](<script_constant_modding.md>). [vanilla-confirmed 1.19.4.1] `common/script_constants/country_groups.txt`, `state_groups.txt`.

## Operators <a id="Operators"></a>

| Operator | Applies to | Result | Notes from the docs |
| --- | --- | --- | --- |
| `controlled_states` | country | All states the country controls | Used for the tooltip name when it is the first operator |
| `country_and_all_subjects` | country | The country and all its subjects; only the country if it has none | Used for the tooltip name when first |
| `faction_members` | country | All faction members including the country; empty if there are none | Used for the tooltip name when first |
| `limit = { ... }` | any item | Keeps the items for which the trigger is true | Heading in the operator document is `limit = PAYLOAD` |
| `owned_states` | country | All states the country owns | Used for the tooltip name when first |

All rows: [docs] `documentation/script_collection_operator.md`.

- The filter key is `limit`. The operator document's own example writes `trigger = { has_government = democratic }`, but vanilla uses `limit` in all 194 filters and `trigger` never. Use `limit`. [vanilla-confirmed 1.19.4.1] counted over `common/`, `events/` and `history/`; the example is [docs].
- Vanilla operator use across 348 blocks: `faction_members` 189, `controlled_states` 56, `country_and_all_subjects` 2, `owned_states` 1, `limit` 194. The common chains are `faction_members` alone (108), `faction_members controlled_states` (45) and `limit` alone (157). [vanilla-confirmed 1.19.4.1]
- `faction_members` is empty for a country that is in no faction, not a collection of that country. For "me and my subjects", use `country_and_all_subjects`. [docs] `documentation/script_collection_operator.md`.
- Inside `limit`, the scope is the item being tested, and `PREV`, `ROOT` and `FROM` come from the place where the collection is used. See [Scopes inside a collection](#Collection_scopes). [docs] `common/collections/_documentation.md`.

## Inline collections <a id="Inline_collections"></a>

An anonymous collection is written where a collection is expected, with the same keys as a named one. It has no identifier, so it cannot be referenced from elsewhere; its optional `name` property is only tooltip text. [docs] `common/collections/_documentation.md`.

```text
collection_size = {
    input = {
        input = game:scope
        operators = {
            faction_members
            controlled_states
            limit = { is_core_of = PREV }
        }
        name = MYMOD_FACTION_CONTROLLED_CORES
    }
    value > 9
}
```

- The `input` of a trigger can itself be a nested collection block, as here. [docs] `documentation/script_collection_input.md` (`game scope` example).
- Give inline collections a `name`. Without one the tooltip falls back to the name of the input, which reads poorly for a filtered set. [docs] `documentation/script_concept_documentation.md`. Vanilla names 326 of its 348 collection blocks that have `operators`. [vanilla-confirmed 1.19.4.1]

## Triggers and effects that use collections <a id="Consumers"></a>

The key that carries the collection is not the same everywhere. Check the table before copying.

### Triggers <a id="Collection_triggers"></a>

| Trigger | Scope | Collection key | Other keys | Vanilla uses |
| --- | --- | --- | --- | --- |
| `collection_size` | any | `input` | `value` with `<`, `>` or `=`, repeatable; a variable is allowed | 122 in 6 files |
| `any_collection_element` | any | `collection` | trigger block; optional `count` | 180 in 42 files |
| `all_collection_elements` | any | `collection` | trigger block | none |
| `collection_contains` | any | `collection` | `countries = { ENG GER }` (all listed) or `country = FRA` | none |
| `count_in_collection` | COUNTRY | `collection` | `unit`, `buildings`, `manpower`, `equipment_ratio`, `unit_category`, `stockpile`, and `size` | 26 in 3 files |
| `has_resources_in_collection` | COUNTRY | `collection` | `resource`, `amount`, `extracted`, `buildings` | 88 in 5 files |

All rows: [docs] `documentation/triggers_documentation.md` for scope, keys and meaning; vanilla uses [vanilla-confirmed 1.19.4.1] counted over `common/`, `events/`, `history/`, comments excluded.

- `collection_size` input forms: `input = collection:NAME`, `input = constant:NAME`, `input = game:all_states`, or a nested block. All appear in vanilla. [vanilla-confirmed 1.19.4.1] `common/decisions/USA.txt`, `common/factions/goals/`.
- `any_collection_element` and `all_collection_elements` check their trigger block against the elements of the collection. With `count = N`, `any_collection_element` needs at least N true elements. The docs example tests `is_core_of = PREV`; `PREV` there most likely means the scope that holds the trigger. [docs] `documentation/triggers_documentation.md`; [unverified] for the meaning of `PREV` inside the block.
- `collection_contains` only checks countries. [docs] `documentation/triggers_documentation.md`.
- `count_in_collection` rules: `unit`, `buildings` and `manpower` are mutually exclusive. `manpower = yes` counts deployed manpower. `equipment_ratio` (default 0) only works for land units. `unit_category` takes a list of sub-unit categories. `stockpile` counts an equipment archetype in stockpiles. [docs] `documentation/triggers_documentation.md`.
- `has_resources_in_collection` rules: `extracted = yes` checks extracted amount instead of balance, `buildings = yes` checks only amount from local buildings, and the two are mutually exclusive; both default to `no`. [docs] `documentation/triggers_documentation.md`.
- Vanilla values for `count_in_collection`: `unit = capital_ship`, `screen_ship`, `submarine`, `fighter`; `buildings = { arms_factory }`, `{ industrial_complex }`; `stockpile = infantry_equipment`; `unit_category = { paratrooper }` with `equipment_ratio = 0.9`. [vanilla-confirmed 1.19.3] `common/factions/goals/faction_goals_medium_term.txt`, `faction_goals_short_term.txt`.
- Vanilla `collection` takes either a block or a plain reference, for example `collection = collection:country_and_all_subjects` in `has_resources_in_collection`. [vanilla-confirmed 1.19.4.1] `common/national_focus/germany.txt`.
- Collection triggers are also valid in `ai_will_do` `modifier` blocks of faction goals. [vanilla-confirmed 1.19.3] `common/factions/goals/faction_goals_short_term.txt`.
- `hidden_trigger` can wrap `all_collection_elements` with `tooltip_evaluation = eval` to run side effects such as `add_to_temp_variable` while a tooltip is built. [docs] `documentation/triggers_documentation.md` (`hidden_trigger` example).

### Effects and math <a id="Collection_effects"></a>

```text
every_collection_element = {
    input = {
        input = game:scope
        operators = {
            faction_members
            limit = { is_subject = yes }
        }
        name = ALL_FACTION_MEMBERS
    }
    custom_effect_tooltip = ALL_FACTION_MEMBERS
    add_political_power = 25
}
```

- `every_collection_element` is usable in any scope, takes `input`, and needs a country scope when the collection does (`country:faction_members`). [docs] `documentation/effects_documentation.md`.
- Its effects run on each element: vanilla puts country effects such as `add_faction_influence_ratio` and `add_timed_idea` in the block, so the element is the scope. [vanilla-confirmed 1.19.3] `common/factions/goals/faction_goals_short_term.txt`.
- Vanilla adds a `custom_effect_tooltip` with the collection's name to give the loop a readable header. [vanilla-confirmed 1.19.3] `common/factions/goals/faction_goals_short_term.txt`.
- The effect's own example puts `limit` beside the inner `input`. Vanilla never does that: none of its 26 uses puts `limit` beside `input`, and the 18 that filter do it through `operators = { ... limit = { ... } }`. Follow vanilla. [docs] `documentation/effects_documentation.md`; [vanilla-confirmed 1.19.4.1] `common/factions/goals/`.
- Math expressions have a collection iterator, `every_collection`, that takes a named collection by bare name and applies statements to the accumulator for each element, with the element scoped. Vanilla uses it to sum `num_researched_technologies` over `faction_members`. [docs] `documentation/script_math_functions.md`, `documentation/script_concept_documentation.md`; [vanilla-confirmed 1.19.3] `common/factions/goals/faction_goals_short_term.txt` (5 uses).

```text
set_temp_variable = {
    total_techs = {
        value = 0
        every_collection = {
            named_collection = faction_members
            add = num_researched_technologies
        }
    }
}
```

[vanilla-confirmed 1.19.3] shape from `common/factions/goals/faction_goals_short_term.txt` (shortened).

### Other keys that take a collection <a id="Other_collection_keys"></a>

- Faction goal `ratio_progress` and manifest progress use `total_amount_collection` and `completed_amount_collection`. The progress is the size of the completed collection divided by the size of the total one, and each key excludes its fixed-value twin (`total_amount`, `completed_amount`). The scope is the faction leader. [docs] `common/factions/_documentation.md`.
- Vanilla values are written as `collection:NAME`, `game:all_states` or `game:all_countries`, or as a block. [vanilla-confirmed 1.19.3] `common/factions/goals/faction_manifests.txt` (36 and 39 uses), `faction_goals_medium_term.txt`.
- The wiki's [Faction modding](<faction_modding.md#Progression_based_goal>) page shows the same keys with nested blocks. [unverified]

## Scopes inside a collection <a id="Collection_scopes"></a>

For the `limit` of an operator or of a named collection: [docs] `common/collections/_documentation.md`.

| Name | Refers to |
| --- | --- |
| `THIS` (the scope itself) | The element of the collection that is being tested |
| `PREV` | The previous scope, set by the place where the collection is used |
| `ROOT` | `PREV.ROOT` |
| `FROM` | `PREV.FROM` |

- The structure mirrors `every_xxx` effects. [docs] `common/collections/_documentation.md`.
- Vanilla leans on this: a limit such as `is_core_of = PREV` asks whether a state is a core of the country that holds the trigger, and `is_controlled_by_ROOT_or_ally = yes` or `is_on_same_continent_as = ROOT` rely on `ROOT` being the intended country at the use site. [vanilla-confirmed 1.19.3] `common/collections/collections.txt`.
- Because `ROOT` is resolved at the use site, a named collection that mentions `ROOT` only makes sense in contexts where `ROOT` is the right country (faction goals in vanilla). [unverified] inference from the vanilla uses.

## Tooltips and localisation <a id="Collection_tooltips"></a>

- A collection is described in tooltips by its `name`. With no name it uses the input's name. [docs] `documentation/script_concept_documentation.md`.
- The name is a localisation key (or, in the concept document's example, a quoted string). Vanilla keys are plain loc keys such as `COLLECTION_COUNTRIES_AT_PEACE`, `ALL_FACTION_MEMBERS` and `FACTION_NAME`. [vanilla-confirmed 1.19.4.1] `localisation/english/collections_l_english.yml`, `factions_l_english.yml`.
- Built-in names exist for inputs and first operators: `COLLECTION_ALL_COUNTRIES`, `COLLECTION_ALL_POSSIBLE_COUNTRIES`, `COLLECTION_ALL_STATES`, `COLLECTION_ALL_MAJORS`, `COLLECTION_FACTION_MEMBERS`, `COLLECTION_OP_FACTION_MEMBERS`, `COLLECTION_OP_OWNED_STATES`, `COLLECTION_OP_CONTROLLED_STATES` and `COLLECTION_OP_COUNTRY_AND_ALL_SUBJECTS`. The operator document says the first operator provides the localisation when the input accepts it. [vanilla-confirmed 1.19.4.1] `localisation/english/collections_l_english.yml`; [docs] `documentation/script_collection_operator.md`.
- Loc keys can embed scope text, for example `COLLECTION_STATES_MY_CONTINENT: "States in [ROOT.GetCountryContinent]"`. [vanilla-confirmed 1.19.4.1] `localisation/english/collections_l_english.yml`.
- Trigger tooltips come from fixed keys with the collection name filled in: `TRIGGER_COLLECTION_SIZE`, `TRIGGER_COLLECTION_SIZE_INLINE`, `TRIGGER_COLLECTION_CONTAINS`, `TRIGGER_COLLECTION_CONTAINS_MANY`, `TRIGGER_ALL_COLLECTION_ELEMENTS_STARTS`, `TRIGGER_ANY_COLLECTION_ELEMENT_STARTS`, `TRIGGER_COUNT_IN_COLLECTION` and `TRIGGER_HAVE_RESOURCES_IN_COLLECTION`. You do not write these. [vanilla-confirmed 1.19.4.1] `localisation/english/triggers_l_english.yml`.
- A name key that has no localisation entry shows as the raw key. [unverified]

## Comparison notes <a id="Comparison_notes"></a>

- `collection_size` accepts `<`, `>` and `=`, several comparisons at once, and variables on the right. [docs] `documentation/triggers_documentation.md`.
- The docs warn that the comparison is inclusive: `value > X` actually means `value >= X`, and likewise for `<`. [docs] `documentation/triggers_documentation.md`.
- Vanilla does not follow that warning. It writes `value > 0` for "at least one" and `value < 1` for "none", for example the goal that is complete when no faction-owned core state is left without full control. Under an inclusive reading `value > 0` would always be true and `value < 1` would allow one item. [vanilla-confirmed 1.19.3] `common/factions/goals/faction_goals_long_term.txt`.
- Which reading the engine applies is [unverified]. Avoid boundary cases that depend on it: compare with a margin, or pair the check with a second condition.
- **Needs a game run** [unverified] Only a run settles the boundary: with a collection of exactly 3 items, see whether `value > 3` passes (inclusive reading) or fails (strict reading), and the same for `value < 3`. Test `count_in_collection` and `has_resources_in_collection` the same way, because the documentation says nothing about their inclusivity.
- For `count_in_collection` (`size`) and `has_resources_in_collection` (`amount`) the docs say nothing about inclusivity. Vanilla uses `size > 19`, `size > 99` and `amount > 799`. [vanilla-confirmed 1.19.4.1] `common/factions/goals/faction_goals_medium_term.txt`, `common/national_focus/germany.txt`.

## Examples <a id="Collection_examples"></a>

All examples follow shapes in the docs or in vanilla. They were not run in the game. [docs] shapes; [unverified] runtime.

Count faction members of one government (inline, country scope):

```text
collection_size = {
    input = {
        input = game:scope
        operators = {
            faction_members
            limit = { has_government = democratic }
        }
        name = MYMOD_DEMOCRATIC_MEMBERS
    }
    value > 3
}
```

Vanilla has this as the named collection `democratic_faction_members`, used as `input = collection:democratic_faction_members`. [vanilla-confirmed 1.19.3] `common/collections/collections.txt`.

Count owned states with a limit (country scope):

```text
collection_size = {
    input = {
        input = game:scope
        operators = {
            owned_states
            limit = { is_core_of = PREV }
        }
        name = MYMOD_OWNED_CORES
    }
    value > 9
}
```

Use the named collection from [Named collections](#Named_collections) in a decision, with its loc entry `MYMOD_COLLECTION_OWNED_COASTAL_STATES: "Owned coastal states"`:

```text
available = {
    collection_size = {
        input = collection:mymod_owned_coastal_states
        value > 4
    }
}
```

At least three faction-controlled states are cores of the holder (`count`):

```text
any_collection_element = {
    collection = {
        input = game:scope
        operators = { faction_members controlled_states }
        name = MYMOD_FACTION_CONTROLLED_STATES
    }
    is_core_of = PREV
    count = 3
}
```

[docs] `documentation/triggers_documentation.md` (`any_collection_element` example).

Resource check over a country and its subjects:

```text
has_resources_in_collection = {
    collection = collection:country_and_all_subjects
    resource = steel
    amount > 799
    extracted = yes
}
```

[vanilla-confirmed 1.19.4.1] `common/national_focus/germany.txt`.

## Collections and loops <a id="Collections_and_loops"></a>

Collections and [arrays with loops](<data_structures.md#Arrays>) solve overlapping problems. The concept document says arrays plus triggers can give the same result in many cases, and that collections are expected to be more efficient and easier to script. [docs] `documentation/script_concept_documentation.md`.

| Need | Collection | Array or scope loop |
| --- | --- | --- |
| Count items that match a condition | `collection_size` with a `limit`; one trigger | Fill an array with `add_to_array`, then loop with `for_each_loop` or count in a temp variable |
| Test that every item matches | `all_collection_elements` | `all_of_scopes` or `all_of` over an array |
| Test that some item matches | `any_collection_element` (with `count`) | `any_of_scopes` or `any_of` over an array |
| Run effects on each item | `every_collection_element` | `for_each_scope_loop` over an array |
| Add up a number over items | `every_collection` in a math expression | `for_each_loop` and a temp variable |
| Combine sets, such as members then their states | Chain operators in one block | Nested loops |
| Keep a list between triggers | Not possible; rebuild it each time | Arrays live in variables and can be changed |
| Tooltip | Built in, titled by `name` | Supply `tooltip` yourself |

- Collections only describe sets that the game already knows (countries, states) through the listed inputs and operators. Anything else, such as a custom list of states built by an event, belongs in an array or a script constant. [docs] `documentation/script_collection_input.md`; [unverified] that no other input exists.
- Scope iterators such as `any_owned_state` or `every_neighbor_state` remain the shortest choice for a single hop. [unverified]

## Confirmed traps <a id="Confirmed_traps"></a>

- Different consumers use different key names for the collection: `input` (`collection_size`, `every_collection_element`, nested blocks), `collection` (`any_collection_element`, `all_collection_elements`, `collection_contains`, `count_in_collection`, `has_resources_in_collection`) and `named_collection` (the math iterator). [docs] `documentation/triggers_documentation.md`, `effects_documentation.md`, `script_math_functions.md`.
- The operator filter is `limit`. The operator document's example uses `trigger`, which no vanilla file does. [vanilla-confirmed 1.19.4.1] 194 uses of `limit` in `operators` blocks, none of `trigger`.
- Two documentation examples are misprinted. The input document's `game all_possible_countries` example writes `collection = collection:all_possible_countries` where `game:all_possible_countries` is meant, and the `has_resources_in_collection` example in the trigger documentation writes `game:scope` without `input =`. Copy the block shape from vanilla instead. [docs] `documentation/script_collection_input.md`, `documentation/triggers_documentation.md`; [vanilla-confirmed 1.19.3] `common/factions/goals/faction_goals_short_term.txt`.
- `limit` beside `input` (as in the `every_collection_element` documentation example) never appears in vanilla; keep filters inside `operators`. [vanilla-confirmed 1.19.4.1] 0 of 348 collection blocks.
- `faction_members` yields an empty collection for a country without a faction. Counting "my faction" in an unaligned country gives 0, not 1. [docs] `documentation/script_collection_operator.md`.
- Collections may hold the same object more than once, and counts include the repeats. [docs] `documentation/script_concept_documentation.md`.
- Inclusive comparison versus vanilla's `value > 0` and `value < 1`: see [Comparison notes](#Comparison_notes). [docs] and [vanilla-confirmed 1.19.3]; the truth is [unverified].
- `ROOT` and `FROM` in a collection's `limit` come from the place of use, so a named collection that depends on them is only valid where those scopes mean the same thing. [docs] `common/collections/_documentation.md`.
- `country:faction_members`, `game:empty` and `game:all_possible_countries` are documented but unused in vanilla; test them before relying on them. [docs] `common/collections/_documentation.md`, `documentation/script_collection_input.md`; [vanilla-confirmed 1.19.4.1] no use in `common/`, `events/` or `history/`.
- `collection_contains` supports countries only. [docs] `documentation/triggers_documentation.md`.

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
