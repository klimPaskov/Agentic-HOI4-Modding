# Collection modding

A collection is a group of scopable game objects of one type, such as countries or states, built from live game data where it is used. It lets one trigger count, test or iterate over things like "every state owned by any faction member".

## Overview

- A collection has an `input`, optional `operators` applied in order, and an optional `name`.
- Collections are read-only descriptions. They cannot be changed after the fact; they are rebuilt where they are used. (unverified) inferred from the docs, which describe no write operation.
- A collection cannot be stored in a variable. `set_temp_variable` with `game:all_states` or `game:all_countries` as the value left the variable at 0, and the engine wrote no error for either. The failure is silent, so a read-back of 0 is the only sign.
- Define a named collection once in `common/collections/*.txt` and refer to it as `collection:<name>`, or write an anonymous collection inline where it is needed.
- Vanilla defines 74 named collections in two files, `collections.txt` (72) and `generic_collections.txt` (2). Every collection block in vanilla script (348 with `operators`) uses only the keys `input`, `operators` and `name`.
- Vanilla consumers are faction goals and manifests (4 files, the large majority of the `operators` blocks), plus 7 decision files, 20 focus files and 18 event files. Most of those test `game:all_majors` with `any_collection_element`.

Related pages: [Data structures](data_structures.md#arrays) for arrays and loops, [Math functions](data_structures.md#math-functions), [Faction modding](faction_modding.md#goals), [Effects](effects.md#any-scope), [Triggers](triggers.md#any-scope), [Script constant modding](script_constant_modding.md).

## Collection structure

| Property | Meaning | Required |
| --- | --- | --- |
| `input` | The starting set; a reference such as `game:all_states`, `collection:NAME` or `constant:NAME`, or a nested collection block | Yes |
| `operators` | A list of steps applied to every item in order | No |
| `name` | Text that describes the collection in tooltips | No |

Vanilla sets `name` on 67 of 74 named collections.

- How it is built: each item of the input goes through the first operator, each result goes through the second, and so on. With input `game:scope` (a country) and operators `faction_members owned_states`, the first step gives every faction member and the second gives each member's owned states.
- Shorthand: a collection that only has an input can be written as the input alone, so `my_collection = game:all_states` equals `my_collection = { input = game:all_states }`.
- No uniqueness guarantee. If an operator reaches the same object through several items, the collection holds it several times, for example a state that is a core of several faction members. Counts include the repeats.
- In vanilla, `limit` is the last entry in every chain that has one (194 of 348, for example `faction_members controlled_states limit`). Another order also worked in a test: with `input = game:all_countries`, `operators = { limit = { tag = GER } owned_states }` and the limit-last order both gave GER's states (`value > 2` was true), so order did not matter there. Other chains were not tried.

## Named collections

Put the definition in any file under `common/collections/`. The block name must be unique.

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

Use it with the `collection:` prefix: `input = collection:mymod_owned_coastal_states`.

- A named collection can use another named collection as its input, as vanilla does with `world_uncapitulated_democratic_countries` (input `collection:world_democratic_countries`).
- A named collection may use a script constant as input: `input = constant:state_groups.balkans`.
- Names in vanilla are unique across the two files (74 of 74). Prefix your own names with the mod tag. A mod collection that reused the vanilla name `world_democratic_countries` took the place of the vanilla one: the vanilla result (more than 3 democracies) did not appear, and the engine printed no duplicate or override warning. The replacing definition was itself rejected at load ("Collection input type is empty", for `input = game:empty`), so the run cannot tell a clean replacement from an invalid collection read as empty. The vanilla `world_uncapitulated_democratic_countries`, which is built on the reused name, also read 0 elements.
- Vanilla has two collections whose names equal the operator they wrap, `faction_members` and `country_and_all_subjects`, defined at the end of `generic_collections.txt`. The math iterator `every_collection` uses the first one by bare name.
- The `name` value is a localisation key; vanilla keys are `COLLECTION_*` entries in `localisation/english/collections_l_english.yml`. See [Tooltips and localisation](#tooltips-and-localisation).

## Inputs

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

- `game:all_majors` appears in no documentation file. Vanilla script writes it 132 times in 40 files, always inline (131 times as `collection = game:all_majors` in `any_collection_element`, once as an `input`). The only other trace is the built-in tooltip name `COLLECTION_ALL_MAJORS`, "Major Powers". It holds exactly the seven major powers of the 1936 start. `every_collection_element` with `input = game:all_majors`, written directly and as a block, logged GER, ENG, SOV, FRA, ITA, JAP and USA in that order, the same tags as an `is_major = yes` scan. `collection_size` over it was above 6 and not above 7. The set may change if a country's major status changes.

- `game:scope` is the object the trigger or effect runs on. Operators such as `faction_members` need that object to be a country. In a wrong scope type the operator fails at run time and matches nothing: with `game:scope` inside a state scope, `faction_members` logged "Collection operator faction_members doesn't support GetSize for objects of type state" at every evaluation (1082 lines) and the check read false, while the country-scope controls read true.
- Type rule: the input sets the item type (countries or states), and an operator must fit that type. (unverified) inferred from the operator documentation.
- Every vanilla `constant:` input points to a list constant (`array = country` or `array = state` in its schema). See [Script constant modding](script_constant_modding.md).

## Operators

| Operator | Applies to | Result | Notes from the docs |
| --- | --- | --- | --- |
| `controlled_states` | country | All states the country controls | Used for the tooltip name when it is the first operator |
| `country_and_all_subjects` | country | The country and all its subjects; only the country if it has none | Used for the tooltip name when first |
| `faction_members` | country | All faction members including the country; empty if there are none | Used for the tooltip name when first |
| `limit = { ... }` | any item | Keeps the items for which the trigger is true | Heading in the operator document is `limit = PAYLOAD` |
| `owned_states` | country | All states the country owns | Used for the tooltip name when first |

- The filter key is `limit`. The operator document's own example writes `trigger = { has_government = democratic }`, but vanilla uses `limit` in all 194 filters and `trigger` never. Use `limit`.
- Vanilla operator use across 348 blocks: `faction_members` 189, `controlled_states` 56, `country_and_all_subjects` 2, `owned_states` 1, `limit` 194. The common chains are `faction_members` alone (108), `faction_members controlled_states` (45) and `limit` alone (157).
- `faction_members` is empty for a country that is in no faction, not a collection of that country. For "me and my subjects", use `country_and_all_subjects`.
- Inside `limit`, the scope is the item being tested, and `PREV`, `ROOT` and `FROM` come from the place where the collection is used. See [Scopes inside a collection](#scopes-inside-a-collection).

## Inline collections

An anonymous collection is written where a collection is expected, with the same keys as a named one. It has no identifier, so it cannot be referenced from elsewhere; its optional `name` property is only tooltip text.

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

- The `input` of a trigger can itself be a nested collection block, as here.
- Give inline collections a `name`. Without one the tooltip falls back to the name of the input, which reads poorly for a filtered set. Vanilla names 326 of its 348 collection blocks that have `operators`.

## Triggers and effects that use collections

The key that carries the collection is not the same everywhere. Check the table before copying.

### Triggers

| Trigger | Scope | Collection key | Other keys | Vanilla uses |
| --- | --- | --- | --- | --- |
| `collection_size` | any | `input` | `value` with `<`, `>` or `=`, repeatable; a variable is allowed | 122 in 6 files |
| `any_collection_element` | any | `collection` | trigger block; optional `count` | 180 in 42 files |
| `all_collection_elements` | any | `collection` | trigger block | none |
| `collection_contains` | any | `collection` | `countries = { ENG GER }` (all listed) or `country = FRA` | none |
| `count_in_collection` | COUNTRY | `collection` | `unit`, `buildings`, `manpower`, `equipment_ratio`, `unit_category`, `stockpile`, and `size` | 26 in 3 files |
| `has_resources_in_collection` | COUNTRY | `collection` | `resource`, `amount`, `extracted`, `buildings` | 88 in 5 files |

- `collection_size` input forms: `input = collection:NAME`, `input = constant:NAME`, `input = game:all_states`, or a nested block. All appear in vanilla. Writing `operators` beside `input` in `collection_size` is rejected at load with "Invalid trigger 'operators'" and "Unknown trigger-type: operators", so put the operators in the nested block form.
- `any_collection_element` and `all_collection_elements` check their trigger block against the elements of the collection. With `count = N`, `any_collection_element` needs at least N true elements. The docs example tests `is_core_of = PREV`. `PREV` inside the block is not the scope that holds the trigger. In a trigger held by ENG that was nested inside GER, `PREV = { tag = ENG }` was false and `PREV = { tag = GER }` was true, so `PREV` was the scope outside the one holding the trigger. Only this one nesting was tested.
- `collection_contains` only checks countries.
- `count_in_collection` needs one of `unit`, `buildings` or `manpower`. With none of them the trigger fails to load with "count_in_collection:No valid target type specified, please provide one of Building, Unit or Manpower".
- `count_in_collection` rules: `unit`, `buildings` and `manpower` are mutually exclusive. `manpower = yes` counts deployed manpower. `equipment_ratio` (default 0) only works for land units. `unit_category` takes a list of sub-unit categories. `stockpile` counts an equipment archetype in stockpiles.
- `has_resources_in_collection` with an inline collection that has no `name` is refused with "Collection game:scope must define a name".
- `has_resources_in_collection` rules: `extracted = yes` checks extracted amount instead of balance, `buildings = yes` checks only amount from local buildings, and the two are mutually exclusive; both default to `no`.
- Vanilla values for `count_in_collection`: `unit = capital_ship`, `screen_ship`, `submarine`, `fighter`; `buildings = { arms_factory }`, `{ industrial_complex }`; `stockpile = infantry_equipment`; `unit_category = { paratrooper }` with `equipment_ratio = 0.9`.
- Vanilla `collection` takes either a block or a plain reference, for example `collection = collection:country_and_all_subjects` in `has_resources_in_collection`.
- Collection triggers are also valid in `ai_will_do` `modifier` blocks of faction goals.
- `hidden_trigger` can wrap `all_collection_elements` with `tooltip_evaluation = eval` to run side effects such as `add_to_temp_variable` while a tooltip is built.

### Effects and math

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

- `every_collection_element` is usable in any scope, takes `input`, and needs a country scope when the collection does (`country:faction_members`).
- Its effects run on each element: vanilla puts country effects such as `add_faction_influence_ratio` and `add_timed_idea` in the block, so the element is the scope.
- Vanilla adds a `custom_effect_tooltip` with the collection's name to give the loop a readable header.
- The effect's own example puts `limit` beside the inner `input`. Vanilla never does that: none of its 26 uses puts `limit` beside `input`, and the 18 that filter do it through `operators = { ... limit = { ... } }`. Follow vanilla.
- Math expressions have a collection iterator, `every_collection`, that takes a named collection by bare name and applies statements to the accumulator for each element, with the element scoped. Vanilla uses it to sum `num_researched_technologies` over `faction_members`.

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

### Other keys that take a collection

- Faction goal `ratio_progress` and manifest progress use `total_amount_collection` and `completed_amount_collection`. The progress is the size of the completed collection divided by the size of the total one, and each key excludes its fixed-value twin (`total_amount`, `completed_amount`). The scope is the faction leader.
- Vanilla values are written as `collection:NAME`, `game:all_states` or `game:all_countries`, or as a block.
- The wiki's [Faction modding](faction_modding.md#progression-based-goal) page shows the same keys with nested blocks, and vanilla writes them that way too (4 blocks in 2 files).

## Scopes inside a collection

For the `limit` of an operator or of a named collection:

| Name | Refers to |
| --- | --- |
| `THIS` (the scope itself) | The element of the collection that is being tested |
| `PREV` | The previous scope, set by the place where the collection is used |
| `ROOT` | `PREV.ROOT` |
| `FROM` | `PREV.FROM` |

- The structure mirrors `every_xxx` effects.
- Vanilla leans on this: a limit such as `is_core_of = PREV` asks whether a state is a core of the country that holds the trigger, and `is_controlled_by_ROOT_or_ally = yes` or `is_on_same_continent_as = ROOT` rely on `ROOT` being the intended country at the use site.
- `ROOT` inside the `limit` of a named collection is the `ROOT` of the place where the collection is used, not the scope that holds the trigger. With `limit = { is_owned_by = ROOT }`, an effect started from LUX that then entered GER counted LUX's states (more than 0 and no more than 5), and the same effect started from GER counted more than 5. Inside that `limit`, `PREV` was the scope where `collection_size` ran (ENG in the test). One nesting (GER then ENG) was tested, and each `PREV` result was seen once.
- Because `ROOT` is resolved at the use site, a named collection that mentions `ROOT` only makes sense in contexts where `ROOT` is the right country (faction goals in vanilla). (unverified) inference from the vanilla uses.

## Tooltips and localisation

- A collection is described in tooltips by its `name`. With no name it uses the input's name.
- The name is a localisation key (or, in the concept document's example, a quoted string). Vanilla keys are plain loc keys such as `COLLECTION_COUNTRIES_AT_PEACE`, `ALL_FACTION_MEMBERS` and `FACTION_NAME`.
- Built-in names exist for inputs and first operators: `COLLECTION_ALL_COUNTRIES`, `COLLECTION_ALL_POSSIBLE_COUNTRIES`, `COLLECTION_ALL_STATES`, `COLLECTION_ALL_MAJORS`, `COLLECTION_FACTION_MEMBERS`, `COLLECTION_OP_FACTION_MEMBERS`, `COLLECTION_OP_OWNED_STATES`, `COLLECTION_OP_CONTROLLED_STATES` and `COLLECTION_OP_COUNTRY_AND_ALL_SUBJECTS`. The operator document says the first operator provides the localisation when the input accepts it.
- Loc keys can embed scope text, for example `COLLECTION_STATES_MY_CONTINENT: "States in [ROOT.GetCountryContinent]"`.
- Trigger tooltips come from fixed keys with the collection name filled in: `TRIGGER_COLLECTION_SIZE`, `TRIGGER_COLLECTION_SIZE_INLINE`, `TRIGGER_COLLECTION_CONTAINS`, `TRIGGER_COLLECTION_CONTAINS_MANY`, `TRIGGER_ALL_COLLECTION_ELEMENTS_STARTS`, `TRIGGER_ANY_COLLECTION_ELEMENT_STARTS`, `TRIGGER_COUNT_IN_COLLECTION` and `TRIGGER_HAVE_RESOURCES_IN_COLLECTION`. You do not write these.
- A name key that has no localisation entry shows as the raw key. (unverified)

## Comparison notes

- `collection_size` accepts `<`, `>` and `=`, several comparisons at once, and variables on the right.
- The docs warn that the comparison is inclusive: `value > X` actually means `value >= X`, and likewise for `<`. The engine does not follow that warning in 1.19.4.1, see below.
- Vanilla does not follow that warning. It writes `value > 0` for "at least one" and `value < 1` for "none", for example the goal that is complete when no faction-owned core state is left without full control. Under an inclusive reading `value > 0` would always be true and `value < 1` would allow one item.
- The engine reads `collection_size` comparisons strictly. With a collection of exactly 3 items, `value > 3` and `value < 3` were false, `value = 3` was true, and `value > 2` and `value < 4` were true. With an empty collection, `value > 0` and `value < 0` were false, `value = 0` was true, and `value > -1` and `value < 1` were true. So `value > 0` means at least one and `value < 1` means none, as vanilla writes them.
- `count_in_collection` is strict too. Over a country collection for Luxembourg with `buildings = { industrial_complex }` (3 civilian factories), `size > 2` and `size < 4` were true and `size > 3` and `size < 3` were false. Given a state collection (`owned_states`), the building count was 0. `size = 3` is refused with "Not a valid compare token in trigger '='".
- `has_resources_in_collection` is strict too. Over Luxembourg, rubber 0 (extracted and balance) gave `amount > 0` and `amount < 0` false and `amount > -1` and `amount < 1` true. Steel extracted 20 gave `amount > 20` and `amount < 20` false and `amount > 19` and `amount < 21` true. Steel balance 8 gave `amount > 8` and `amount < 8` false and `amount > 7` and `amount < 9` true.
- For `count_in_collection` (`size`) and `has_resources_in_collection` (`amount`) the docs say nothing about inclusivity. Vanilla uses `size > 19`, `size > 99` and `amount > 799`.

## Examples

All examples follow shapes in the docs or in vanilla. In a test run all five Examples-section shapes and the two effect-section examples parsed and ran in a country scope with no error.log line, and every example printed its finish line. A math `every_collection` over the named collection `faction_members` returned 55, the same as over `country_and_all_subjects`. One example had no elements, so it shows parsing only. The test country's faction membership was not logged, so the equal totals do not show whether `faction_members` is empty without a faction (see the note on that below).

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

Vanilla has this as the named collection `democratic_faction_members`, used as `input = collection:democratic_faction_members`.

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

Use the named collection from [Named collections](#named-collections) in a decision, with its loc entry `MYMOD_COLLECTION_OWNED_COASTAL_STATES: "Owned coastal states"`:

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

Resource check over a country and its subjects:

```text
has_resources_in_collection = {
    collection = collection:country_and_all_subjects
    resource = steel
    amount > 799
    extracted = yes
}
```

## Collections and loops

Collections and [arrays with loops](data_structures.md#arrays) solve overlapping problems. The concept document says arrays plus triggers can give the same result in many cases, and that collections are expected to be more efficient and easier to script.

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

- Collections only describe sets that the game already knows (countries, states) through the listed inputs and operators. Anything else, such as a custom list of states built by an event, belongs in an array or a script constant. The list is not complete, because vanilla also uses the undocumented `game:all_majors` (see Inputs).
- Scope iterators such as `any_owned_state` or `every_neighbor_state` remain the shortest choice for a single hop. (unverified)

## Confirmed traps

- Different consumers use different key names for the collection: `input` (`collection_size`, `every_collection_element`, nested blocks), `collection` (`any_collection_element`, `all_collection_elements`, `collection_contains`, `count_in_collection`, `has_resources_in_collection`) and `named_collection` (the math iterator).
- The operator filter is `limit`. The operator document's example uses `trigger`, which no vanilla file does.
- Two documentation examples are misprinted. The input document's `game all_possible_countries` example writes `collection = collection:all_possible_countries` where `game:all_possible_countries` is meant, and the `has_resources_in_collection` example in the trigger documentation writes `game:scope` without `input =`. Copy the block shape from vanilla instead.
- `limit` beside `input` (as in the `every_collection_element` documentation example) never appears in vanilla; keep filters inside `operators`.
- `faction_members` yields an empty collection for a country without a faction. Counting "my faction" in an unaligned country gives 0, not 1.
- Collections may hold the same object more than once, and counts include the repeats.
- Inclusive comparison versus vanilla's `value > 0` and `value < 1`: see [Comparison notes](#comparison-notes). The docs say inclusive. The engine is strict, so vanilla's `value > 0` means at least one.
- `ROOT` and `FROM` in a collection's `limit` come from the place of use, so a named collection that depends on them is only valid where those scopes mean the same thing.
- `country:faction_members`, `game:empty` and `game:all_possible_countries` are documented but unused in vanilla; test them before relying on them.
- `collection_contains` supports countries only.
