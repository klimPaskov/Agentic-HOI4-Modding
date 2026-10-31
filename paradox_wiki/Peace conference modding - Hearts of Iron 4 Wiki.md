# Peace conference modding

*Kit page: written by the Agentic HOI4 Modding Kit from the Hearts of Iron IV 1.19.3.0 game files. The wiki has no page for this topic. CC BY-SA 3.0 (see LICENSE.txt).*
<!-- kit:page -->

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" sources="common/peace_conference/ common/on_actions/ common/factions/ common/autonomous_states/ common/defines/00_defines.lua common/game_rules/ documentation/triggers_documentation.md documentation/effects_documentation.md documentation/dynamic_variables_documentation.md localisation/english/peace_l_english.yml" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Written from the two `_documentation.md` files and every vanilla file under `common/peace_conference/`, the peace-conference on actions, faction peace rules, the `pc_` triggers and the peace defines.
- Cross-checked with the existing wiki pages Faction modding, AI modding, On actions, Triggers and Autonomy state modding; disagreements are listed under Confirmed traps.
- Gaps left: the engine's cost formula is not documented, the `ai_desire` scale is ambiguous in the game's own files, and nothing was run in the game.
<!-- kit:end id="review" -->

## Table of contents

- [Overview](#Overview)
- [Scope chain](#Scope_chain)
- [Action types](#Action_types)
- [Action categories](#Action_categories)
- [Cost modifiers](#Cost_modifiers)
  - [Syntax](#Cost_modifier_syntax)
  - [How modifiers multiply](#How_modifiers_multiply)
  - [Faction rules](#Faction_rules)
  - [Vanilla patterns](#Cost_modifier_patterns)
- [AI peace desires](#AI_peace_desires)
  - [Syntax](#AI_desire_syntax)
  - [The ai_desire scale](#The_ai_desire_scale)
  - [Vanilla patterns](#AI_desire_patterns)
- [Triggers](#Triggers)
- [Effects](#Effects)
- [On actions](#On_actions)
- [Defines](#Defines)
- [Related settings](#Related_settings)
- [Minimal example](#Minimal_example)
- [Confirmed traps](#Confirmed_traps)

---

A peace conference is run by the engine. Mods shape it through data files in `common/peace_conference/`, faction rules, `pc_` triggers, on actions and defines, and can start one from script. [vanilla-confirmed 1.19.3] folders and keys below exist in the installed game.

## Overview <a id="Overview"></a>

| Piece | Where | Top-level block or key | Job |
| --- | --- | --- | --- |
| Action categories | `common/peace_conference/categories/*.txt` | `peace_action_categories` | Group cost modifiers in the cost tooltip |
| Cost modifiers | `common/peace_conference/cost_modifiers/*.txt` | `peace_action_modifiers` | Multiply the cost of one kind of peace action |
| AI desires | `common/peace_conference/ai_peace/*.txt` | `peace_ai_desires` | Change how much the AI wants an action; the cost stays the same |
| Faction rules | `common/factions/rules/*.txt` | `type = peace_conference_rules` with `peace_action_modifiers = { ... }` | Switch named cost modifiers on for a faction |
| Autonomy states | `common/autonomous_states/*.txt` | `use_for_peace_conference_weight`, `peace_conference_initial_freedom` | Weight of a puppet choice and starting freedom after a conference |
| Triggers | `pc_*` and `is_in_peace_conference` | trigger scripts | Read conference state |
| Effects | `start_peace_conference`, `white_peace` | effect scripts | Start a conference or a white peace |
| On actions | `common/on_actions/*.txt` | `on_before_peace_conference_start`, `on_peaceconference_started`, `on_peaceconference_ended` and others | React to a conference |
| Defines | `common/defines/00_defines.lua` | `NDefines.NDiplomacy`, `NAI`, `NNavy`, `NFactions` | Base costs, score handling, AI bidding |

All rows: [vanilla-confirmed 1.19.3] the folders, files and keys exist in the installed game; each is described in its own section below.

Vanilla size: 18 cost modifier files with 108 entries, 15 AI files with 158 entries, and 1 category file with 11 categories. [vanilla-confirmed 1.19.3] `common/peace_conference/`, counted by script.

Related wiki pages: [Faction modding](<Faction modding - Hearts of Iron 4 Wiki.md#Rules>), [AI modding](<AI modding - Hearts of Iron 4 Wiki.md#AI_peace>), [On actions](<On actions - Hearts of Iron 4 Wiki.md#Politics>), [Triggers](<Triggers - Hearts of Iron 4 Wiki.md#Peace_conferences>), [Effects](<Effects - Hearts of Iron 4 Wiki.md#War>), [Autonomy state modding](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) and [Defines](<Defines - Hearts of Iron 4 Wiki.md#NDiplomacy>).

## Scope chain <a id="Scope_chain"></a>

Inside the `enable` block of a cost modifier or an AI desire, the scopes are fixed by the peace action being evaluated:

| Scope | Refers to |
| --- | --- |
| `ROOT` | The negotiator: the country doing the negotiation |
| `FROM` | The taker: the country that will own the result after the conference |
| `FROM.FROM` | The giver: the country that owned it before the conference |
| `FROM.FROM.FROM` | The state, only if the action refers to a state |

All rows: [docs] `common/peace_conference/ai_peace/_documentation.md` and `common/peace_conference/cost_modifiers/_documentation.md` (identical text in both).

- Inside another scope such as `ROOT = { ... }`, `FROM` no longer means the taker. Write `ROOT.FROM`, `ROOT.FROM.FROM` or `ROOT.FROM.FROM.FROM` there. [docs] both `_documentation.md` files.
- Vanilla does this: `ROOT = { has_defensive_war_with = ROOT.FROM.FROM }` and `any_country = { ROOT.FROM.FROM.FROM = { is_core_of = PREV } }`. [vanilla-confirmed 1.19.3] `cost_modifiers/00_generic_peace.txt`.
- At the top level of `enable`, vanilla writes both `FROM.FROM.FROM = { ... }` (`cost_modifiers/00_generic_peace.txt`) and `ROOT.FROM.FROM.FROM = { ... }` (`ai_peace/00_misc.txt`) for the same state. [vanilla-confirmed 1.19.3]
- Bare country triggers sit directly in `enable` in vanilla, for example `is_major = no` and `has_government = democratic` in `ai_peace/00_misc.txt`. The top-level scope is therefore a country. The wiki's AI modding page names it `ROOT`, the negotiator. [vanilla-confirmed 1.19.3] for the usage; [unverified] that it is always the negotiator.
- "Negotiating for ourselves" is written `ROOT = { tag = ROOT.FROM }` or `ROOT.FROM = { tag = ROOT }`. The taker can be another winner, so the two are not always equal. [vanilla-confirmed 1.19.3] `ai_peace/00_misc.txt` (comment "We are negotiating for ourselves") and `ai_peace/ENG.txt`.
- Which country `FROM` is for each action type, read from how vanilla uses it. [unverified] inference from vanilla usage, not stated in the docs:

| Action | `FROM` (taker) | `FROM.FROM` (giver) | Vanilla evidence |
| --- | --- | --- | --- |
| `take_states` | The country that will own the state; `ROOT` itself or a winner that has a core or claim | The loser that owned the state | `generic_is_core_of_puppet` comment "Taker is puppet or will be" |
| `puppet` | The puppet that results | The loser the state comes from | `ai_peace/00_misc.txt` `continuous_puppet` tests `ROOT.FROM = { pc_is_puppeted_by = ROOT }` |
| `liberate` | The liberated country | The loser that held the state | `dormant_national_identity` tests `FROM = { is_unlikely_country_tag = yes }` |
| `force_government` | The country whose government changes | The same country; vanilla reads the target government through `ROOT.FROM` in some entries and `ROOT.FROM.FROM` in others | `democracy_force_government_on_evil_fascism` uses `ROOT.FROM`; `force_gov_puppets` uses `ROOT.FROM.FROM` |

The on action scopes are different: for the conference on actions `ROOT` is the winner and `FROM` is the loser. See [On actions](#On_actions). [docs] `common/on_actions/_documentation.md`.

Peace conference state is not live. Diplomatic relations and state ownership are updated before or after a conference, not during it, so use `pc_` triggers for anything that changes inside the conference. [docs] both `_documentation.md` files.

## Action types <a id="Action_types"></a>

| Type | What the player sees | Cost entries using it | AI entries using it |
| --- | --- | --- | --- |
| `take_states` | A winner takes a state from a loser | 70 | 83 |
| `puppet` | A puppet is created from a loser's state or country | 28 | 58 |
| `liberate` | A country occupied by a loser is restored | 17 | 39 |
| `force_government` | A loser's government is changed to the winner's ideology | 19 | 45 |

- The four type names are the complete documented list. [docs] both `_documentation.md` files.
- `peace_action_type` takes one type or a list, `peace_action_type = { puppet liberate }`. [docs] both `_documentation.md` files.
- Counts: an entry that lists several types is counted once per type. [vanilla-confirmed 1.19.3] `cost_modifiers/` (108 entries) and `ai_peace/` (158 entries).
- Descriptions of what the player sees come from the conference UI strings. [vanilla-confirmed 1.19.3] `localisation/english/peace_l_english.yml` (`PEACE_TAKE_STATES`, `PEACE_PUPPET_COUNTRY_DESC`, `PEACE_LIBERATE_DESC`, `PEACE_FORCE_GOVERNMENT_DESC`).
- Not documented as a type: `take_navy`. The conference window has a take-navy action and a loc key `PEACE_TAKE_NAVY`, and the string `take_navy` exists in `hoi4.exe`, but no vanilla cost or AI file uses it. The wiki's AI modding page says cost modifiers can still be applied to it. Whether a mod can target it from `peace_action_type` is [unverified]. [vanilla-confirmed 1.19.3] `interface/peaceconferencewindow.gui` (`take_navy_action`).
- Stackable add-ons (demilitarized zone, war reparation, resource rights, dismantle industry) are not action types. They add a percentage to an action's cost and can be read with `pc_does_state_stack_demilitarized` and `pc_does_state_stack_dismantled`. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` (`PEACE_COST_FACTOR_STACK_*`) and `localisation/english/peace_l_english.yml`.

## Action categories <a id="Action_categories"></a>

A category groups cost modifiers for display. Modifiers with the same category show as one number in the cost tooltip, and a modifier without a category goes under the default category. [docs] `common/peace_conference/cost_modifiers/_documentation.md`.

```text
peace_action_categories = {
    other = {
        default = yes                  # only allowed for one category
        name = PEACE_ACTION_CATEGORY_OTHER
    }
    is_core = {
        name = PEACE_ACTION_CATEGORY_IS_CORE
    }
}
```

- Exactly one category carries `default = yes`. The vanilla comment says the flag is only allowed for one category. A mod that adds categories must not add a second default. [vanilla-confirmed 1.19.3] `common/peace_conference/categories/00_peace_action_categories.txt`.
- `name` is a localisation key. [vanilla-confirmed 1.19.3] `00_peace_action_categories.txt`; all 11 keys are defined in `localisation/english/peace_l_english.yml`.
- A cost modifier selects a category with `category = <key>`. The key must be one defined under `peace_action_categories`. [docs] `cost_modifiers/_documentation.md`.
- Using an undefined category key: result not tested. [unverified]

Vanilla categories and how many of the 96 categorized cost modifiers use each:

| Key | Loc key | English text | Cost modifiers |
| --- | --- | --- | --- |
| `other` (default) | `PEACE_ACTION_CATEGORY_OTHER` | Other | 2 |
| `occupation` | `PEACE_ACTION_CATEGORY_OCCUPATION` | Occupation | 1 |
| `ideology` | `PEACE_ACTION_CATEGORY_IDEOLOGY` | Ideology | 13 |
| `is_core` | `PEACE_ACTION_CATEGORY_IS_CORE` | Is core | 4 |
| `core_of_ally` | `PEACE_ACTION_CATEGORY_CORE_OF_ALLY` | Core of Ally | 1 |
| `has_claim` | `PEACE_ACTION_CATEGORY_HAS_CLAIM` | Has claim | 1 |
| `defensive_war` | `PEACE_ACTION_CATEGORY_DEFENSIVE_WAR` | Defensive war | 2 |
| `treaties_or_conferences` | `PEACE_ACTION_CATEGORY_CONFERENCES` | Treaties & Conferences | 17 |
| `belonged_to_someone_else` | `PEACE_ACTION_CATEGORY_OTHER_CLAIMANT` | Can Be Liberated | 1 |
| `events_or_focuses` | `PEACE_ACTION_CATEGORY_EVENTS_OR_FOCUSES` | Events or Focuses | 52 |
| `continuous_political_action` | `PEACE_ACTION_CATEGORY_CONTINUOUS_POLITICAL_ACTION` | Continuous Political Action | 2 |

All rows: [vanilla-confirmed 1.19.3] `common/peace_conference/categories/00_peace_action_categories.txt`, `localisation/english/peace_l_english.yml`, and a count over `cost_modifiers/*.txt`.

## Cost modifiers <a id="Cost_modifiers"></a>

A cost modifier multiplies the point cost of a peace action while its `enable` block is true. It does not change AI desire. [docs] `common/peace_conference/cost_modifiers/_documentation.md`.

### Syntax <a id="Cost_modifier_syntax"></a>

```text
peace_action_modifiers = {
    MYM_example = {
        category = is_core               # optional
        peace_action_type = take_states  # one type or { type type }
        enable = {
            FROM.FROM.FROM = { is_core_of = ROOT.FROM }
        }
        cost_multiplier = 0.65           # must be > 0
    }
}
```

| Key | Meaning | Status |
| --- | --- | --- |
| `category` | A key from `peace_action_categories`; omitted means the default category | Optional; set on 96 of 108 vanilla entries |
| `peace_action_type` | The action types the modifier applies to | Present on all 108 |
| `enable` | Trigger block evaluated with the scope chain above; may use any trigger, including `pc_` triggers | Present on all 108 |
| `cost_multiplier` | Number the action cost is multiplied by; the docs say it must be above 0 | Present on all 108 |
| `faction_modifier` | `yes` on the 10 entries of `faction_peace_action_modifiers.txt`; not in the docs; the string exists in `hoi4.exe` | Meaning [unverified] |

Rows 1 to 4: [docs] `cost_modifiers/_documentation.md` for the key and its meaning, [vanilla-confirmed 1.19.3] `cost_modifiers/*.txt` for the counts. Row 5: [vanilla-confirmed 1.19.3] `cost_modifiers/faction_peace_action_modifiers.txt`.

- The 12 vanilla entries without a category are the 10 faction modifiers plus `dormant_national_identity` and `ENG_operation_fork`. [vanilla-confirmed 1.19.3] `cost_modifiers/00_generic_peace.txt`, `ENG_peace.txt`.
- Entry names are internal. Of 260 distinct entry names across cost and AI files, only one matches an English loc key (`JAP_spiritual_mobilization`, which is a focus name that the modifier happens to share), so a new entry needs no localisation. The category name is what the player sees. [vanilla-confirmed 1.19.3] `localisation/english/*.yml` searched for each name.
- `enable` accepts flow control and data checks, not only plain triggers. Vanilla uses `if`/`else_if`/`else`, `OR`, `NOT`, `has_global_flag`, `has_state_flag`, `is_in_array`, `check_variable` and `var:` references. [vanilla-confirmed 1.19.3] `ai_peace/00_misc.txt`, `cost_modifiers/DEN_peace.txt`, `GER_peace.txt`, `yalta_peace.txt`.

### How modifiers multiply <a id="How_modifiers_multiply"></a>

- All cost modifiers that are active for an action are multiplied together. [docs] `cost_modifiers/_documentation.md`.
- The docs advise multipliers near 1.0, roughly 0.4 to 3.0, and warn that extreme values seldom work as well as expected. [docs] `cost_modifiers/_documentation.md`.
- Vanilla multipliers range from 0.05 to 4.0; 0.5 is the most common value (31 entries), then 0.75 (13). [vanilla-confirmed 1.19.3] `cost_modifiers/*.txt`.
- Worked example: `generic_is_core` (0.25) and `generic_occupies_state` (0.80) both active on one `take_states` action give 0.25 x 0.80 = 0.20 of the base cost. The product follows from the multiplication rule. [docs] for the rule, [vanilla-confirmed 1.19.3] `00_generic_peace.txt` for the two values.
- The cost after all modifiers is capped at `PEACE_ACTION_MAX_COST = 9999`. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` (`NDiplomacy`).
- Category affects display only, according to the docs. Whether it also affects the math is not stated. [docs] `cost_modifiers/_documentation.md` for display; [unverified] for the math.
- The base cost that the multipliers act on is built from state value, building values, the `BASE_PEACE_*` and `PEACE_COST_FACTOR_*` defines, bid history and compliance. The combined formula is not documented. [unverified] formula; the inputs are listed under [Defines](#Defines).

### Faction rules <a id="Faction_rules"></a>

A faction rule with `type = peace_conference_rules` lists cost modifier names in `peace_action_modifiers`, and the faction then gets them. The rule's scope is the faction leader. [docs] `common/factions/_documentation.md` and the wiki's [Faction modding](<Faction modding - Hearts of Iron 4 Wiki.md#Modifier>) page.

```text
faction_peace_rule_puppeting_focus = {
    type = peace_conference_rules
    ai_will_do = { base = 0 }
    peace_action_modifiers = {
        faction_rule_modifier_encourage_puppet
    }
    modifier = {
        custom_modifier_tooltip = faction_rule_modifier_encourage_puppet_tt
    }
}
```

- Vanilla ships 7 such rules in `common/factions/rules/peace_rules.txt`, grouped in `rule_group_peace_rules` in `common/factions/rules/groups/rule_groups.txt`. [vanilla-confirmed 1.19.3]
- The 10 modifiers in `faction_peace_action_modifiers.txt` use `enable = { always = yes }` and `faction_modifier = yes`. [vanilla-confirmed 1.19.3] `cost_modifiers/faction_peace_action_modifiers.txt`.
- The rule's tooltip is a separate loc key (`custom_modifier_tooltip`). It is not generated from the multiplier, so keep it in step by hand. [vanilla-confirmed 1.19.3] `localisation/english/factions_l_english.yml`.
- Drift in vanilla: several tooltips promise a 5 percent cost increase on a second action type, but no rule references the three `faction_rule_modifier_extra_cost_*` modifiers. The effect of that gap is [unverified]. [vanilla-confirmed 1.19.3] `peace_rules.txt` and `factions_l_english.yml`.
- The docs say the `enable` block of a rule-backed modifier does not run: the modifier is active while the rule is active. [docs] `common/factions/_documentation.md`. Two vanilla faction modifiers still carry a real `enable` (`faction_rule_modifier_encourage_take_claimed_states` tests `FROM.FROM.FROM = { is_claimed_by = ROOT }`) and their tooltips describe the narrowing. Which reading is true is [unverified]. [vanilla-confirmed 1.19.3] `faction_peace_action_modifiers.txt`.

### Vanilla patterns <a id="Cost_modifier_patterns"></a>

- 16 of the 18 files are per-country (`<TAG>_peace.txt`, `RK_peace.txt`, `yalta_peace.txt`); the rest are `00_generic_peace.txt` and `faction_peace_action_modifiers.txt`. [vanilla-confirmed 1.19.3] `cost_modifiers/`.
- Country entries gate on a completed focus, a flag or an array and use category `events_or_focuses`. [vanilla-confirmed 1.19.3] `cost_modifiers/AST_peace.txt` (shortened):

```text
AST_holding_the_battlefield_take_states_modifier = {
    category = events_or_focuses
    peace_action_type = { take_states }
    enable = {
        ROOT = {
            original_tag = AST
            has_completed_focus = AST_holding_the_battlefield
        }
    }
    cost_multiplier = 0.75
}
```

- State-specific entries tag states with a state flag and test it on `FROM.FROM.FROM`, for example `has_state_flag = yalta_pol` in `yalta_peace.txt` and `DEN_buffert_zone_state_flag` in `DEN_peace.txt`. [vanilla-confirmed 1.19.3]
- Entries that apply only when the negotiator acts for itself test `ROOT.FROM = { tag = ROOT }`; `eat_the_rich` in `00_generic_peace.txt` does. [vanilla-confirmed 1.19.3]
- A guard against capitulation occupation: `generic_occupies_state` adds `compliance > 0` to its state test. The vanilla comment says this stops capitulation-occupation from counting. [vanilla-confirmed 1.19.3] `00_generic_peace.txt`.
- The vanilla comment on `communism_take_state` asks whether the negotiator or the taker should be tested. Read it as an open design question: ideology entries test `ROOT`. [vanilla-confirmed 1.19.3] `00_generic_peace.txt`.

## AI peace desires <a id="AI_peace_desires"></a>

AI desire scripts steer what the AI asks for. They affect AI behaviour but not the cost. [docs] `common/peace_conference/ai_peace/_documentation.md`.

### Syntax <a id="AI_desire_syntax"></a>

```text
peace_ai_desires = {
    MYM_take_homeland_cores = {
        peace_action_type = take_states    # one type or { type type }
        enable = {
            ROOT = { original_tag = MYM }
            ROOT.FROM = { tag = ROOT }
            ROOT.FROM.FROM.FROM = { is_core_of = ROOT.FROM }
        }
        ai_desire = 150
    }
}
```

- Every entry has exactly the keys `peace_action_type`, `enable` and `ai_desire`. All 158 vanilla entries have these three and no others. [vanilla-confirmed 1.19.3] `ai_peace/*.txt`.
- All entries active for an action are summed. A total of 0 or lower means the AI does not take the action. [docs] `ai_peace/_documentation.md`.
- `enable` can hold any trigger, including `pc_` triggers, with the same scope chain as cost modifiers. [docs] `ai_peace/_documentation.md`.
- Humans are not steered by these scripts. Vanilla uses `is_ai = yes` and `is_ai = no` inside `enable` to treat AI and player winners differently ("humans have other biases"). [vanilla-confirmed 1.19.3] `ai_peace/00_misc.txt`.

### The ai_desire scale <a id="The_ai_desire_scale"></a>

The game's own files give two readings of `ai_desire`, and they do not agree:

- Reading A, additive score: "all AI desires that are active are summed", and a total of 0 or lower means no action. [docs] `ai_peace/_documentation.md`.
- Reading B, percent change: the same file's example says `ai_desire = 100` increases desire by 100 percent, 0 means no change and -50 reduces it by 50 percent. [docs] `ai_peace/_documentation.md`.
- Vanilla comments lean to percent wording: `-85` is "85 percent lower desire" (`00_misc.txt`), `-200` is "200 percent lower desire" (`ITA.txt`, `JAP.txt`), `-250` is "250 percent lower desire" (`RAJ.txt`), `75` is "75 percent higher desire" (`ETH.txt`, `SOV.txt`). A drop of more than 100 percent only makes sense as an additive offset. [vanilla-confirmed 1.19.3]
- Other comments lean to offsets: `1100` is "Finite offset" (`USA.txt`) and `70` is "Acceptable values" (`00_misc.txt`). [vanilla-confirmed 1.19.3]
- The wiki's AI modding page says -1000 makes the AI never pursue the action and 1000 makes it the top priority. [unverified] wiki statement; vanilla does use `-1000` twice, for the influence cut-off entries in `00_misc.txt`.
- Vanilla values run from -1000 to 2000. The most common are 200 (28 entries), -200 (25), -100 (15) and 100 (10). [vanilla-confirmed 1.19.3] `ai_peace/*.txt`.

Safe usage that holds under both readings: use -200 or lower to veto an action, use positive values to prefer one, and do not depend on 0 meaning "no change". The exact combination rule, and whether a baseline is added before the sum is tested against zero, is [unverified].

### Vanilla patterns <a id="AI_desire_patterns"></a>

- Veto: `dont_puppet_and_force_government` gives -200 to `puppet` when the giver already had its government forced to the ideology of the top-level country, and `dont_force_government_and_puppet` gives -200 to `force_government` when the giver is already puppeted by `ROOT`. [vanilla-confirmed 1.19.3] `ai_peace/00_misc.txt`.
- Prefer own cores: `take_our_cores` gives 100 to `take_states` when the state is a core of the taker and the negotiator acts for itself. [vanilla-confirmed 1.19.3] `ai_peace/00_misc.txt`.
- Branch by ideology with `if`/`else_if`/`else` in `enable`, ending in `else = { always = no }`. [vanilla-confirmed 1.19.3] `ai_peace/00_misc.txt` (`do_force_government_if_forced_to_our_ideology`).
- Competition awareness: `leave_allied_ai_claims_alone` tests `pc_is_winner`, `pc_current_score > 200` and `pc_turn < 12` on the countries with a core. [vanilla-confirmed 1.19.3] `ai_peace/00_misc.txt`.
- Influence range: `pc_is_state_outside_influence_for_winner` backs the `generic_influence_cutoff*` entries. [vanilla-confirmed 1.19.3] `ai_peace/00_misc.txt`.
- Per-country files (`CHI.txt`, `GER.txt`, `USA.txt`, `yalta.txt`, `warlords.txt` and others) hold focus and event driven preferences. [vanilla-confirmed 1.19.3] `ai_peace/`.

## Triggers <a id="Triggers"></a>

| Trigger | Scope | Value | Checks | Vanilla uses |
| --- | --- | --- | --- | --- |
| `is_in_peace_conference` | COUNTRY | yes/no | The country is in a peace conference now | none |
| `pc_current_score` | COUNTRY | number | The country's conference score; winners only | 1 |
| `pc_does_state_stack_demilitarized` | STATE | yes/no | A demilitarized-zone stackable sits on the state | 2 |
| `pc_does_state_stack_dismantled` | STATE | yes/no | A dismantle-industry stackable sits on the state | none |
| `pc_is_forced_government` | COUNTRY | yes/no | Its government was force-changed in the conference | 2 |
| `pc_is_forced_government_by` | COUNTRY | country | Force-changed by that country | 3 |
| `pc_is_forced_government_to` | COUNTRY | ideology group | Force-changed to that ideology | 16 |
| `pc_is_liberated` | COUNTRY | yes/no | Liberated in the conference | 6 |
| `pc_is_loser` | COUNTRY | yes/no | Is a loser | 13 |
| `pc_is_on_same_side_as` | COUNTRY | country | On the same side (winning or losing) as that country | 4 |
| `pc_is_on_winning_side` | COUNTRY | yes/no | Is on the winning side | none |
| `pc_is_puppeted` | COUNTRY | yes/no | Is a puppet, or was released as a puppet in the conference | 9 |
| `pc_is_puppeted_by` | COUNTRY | country | Puppet of, or released as a puppet by, that country | 13 |
| `pc_is_state_claimed` | STATE | yes/no | Claimed and uncontested in the conference | none |
| `pc_is_state_claimed_and_taken_by` | STATE | country | Claimed with a `take_states` action by that country | none |
| `pc_is_state_claimed_by` | STATE | country | Claimed in the conference by that country | 9 |
| `pc_is_state_outside_influence_for_winner` | STATE | country | Outside the valid influence range of that winner | 3 |
| `pc_is_winner` | COUNTRY | yes/no | Is a winner | 2 |
| `pc_total_score` | COUNTRY | number | The country's conference score; winners only | 2 |
| `pc_turn` | any | number | The current turn number of the conference | 1 |

All rows: [docs] `documentation/triggers_documentation.md` for scope, value and meaning. Vanilla uses counted over `common/`, `events/`, `history/` and `interface/`: [vanilla-confirmed 1.19.3].

- `pc_current_score` and `pc_total_score` have the same description in the docs ("total peace conference score"). Vanilla pairs `pc_current_score > 200` with `pc_turn < 12` in `leave_allied_ai_claims_alone` (its comment: give them some leeway to take demands), and uses `pc_total_score > 800` in `ai_peace/USA.txt` to gate puppeting most of Japan. Reading current as the score still available to spend and total as the whole award is [unverified]. [docs] `documentation/triggers_documentation.md`.
- Both scores are also listed as dynamic variables, so they can be read in variable math. [docs] `documentation/dynamic_variables_documentation.md`.
- `pc_is_state_outside_influence_for_winner` uses `PEACE_TRIGGER_AI_MAX_INFLUENCE_VALUE = 0.99` as the maximum influence value. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.
- The triggers also work in `on_peaceconference_ended`: vanilla tests `pc_does_state_stack_demilitarized = yes` on states 42 and 51 there. [vanilla-confirmed 1.19.3] `common/on_actions/08_bba_on_actions.txt`.
- Outside a conference these triggers have nothing to read. The wiki says they can only be used within peace conferences. [unverified]

## Effects <a id="Effects"></a>

Two effects start a conference from script. Both run in country scope and `ROOT` is the winner. [docs] `documentation/effects_documentation.md`.

```text
SOV = {
    start_peace_conference = {
        tag = FIN               # main loser
        score_factor = 0.2      # 0 to 1, share of the score given to winners; a variable is allowed
        winner_scope = FACTION  # optional, default LIMITED_FACTION
        loser_scope = FACTION   # optional, default LIMITED_FACTION
        message = FIN_agree_peace  # optional popup text key
    }
}
```

- `winner_scope` and `loser_scope` accept `ALL`, `FACTION`, `LIMITED_FACTION` and `LIMITED`. `score_factor = 0.0` means a white peace. [docs] `documentation/effects_documentation.md` (`start_peace_conference`).
- The conference includes only the named loser and its potential subjects as losers. [docs] `documentation/effects_documentation.md`.
- Vanilla calls `start_peace_conference` 10 times, all in `common/scripted_effects/ITA_scripted_effects.txt` (Italy against Ethiopia and the reverse), with only `tag` and a `score_factor` chosen by `surrender_progress`; no vanilla file sets `winner_scope`, `loser_scope` or `message` on it. [vanilla-confirmed 1.19.3]
- `white_peace` takes the country directly or a block with `tag` and `message`: `white_peace = PREV` in `common/on_actions/00_on_actions.txt`, `white_peace = { tag = PREV }` in `common/decisions/BEL.txt`, and a `message` key in `common/national_focus/sweden.txt`. `ROOT` counts as the winner, which affects the conference name and the conference on actions. [docs] `documentation/effects_documentation.md`; [vanilla-confirmed 1.19.3] the three forms.

## On actions <a id="On_actions"></a>

| On action | `ROOT` | `FROM` | Notes |
| --- | --- | --- | --- |
| `on_before_peace_conference_start` | winner | loser | Runs once for every winner against every loser |
| `on_peaceconference_started` | winner | loser | Runs once for every winner against every loser |
| `on_peaceconference_ended` | winner | loser | Runs once for every winner against every loser |
| `on_puppet` | nation being puppeted | overlord | Vanilla comment: used when puppeting in a peace conference |
| `on_liberate` | nation being liberated | leader of the liberators | Vanilla comment in `12_wuw_on_actions.txt` |
| `on_release_as_puppet` | nation being released | overlord | Vanilla comment: puppeting through the occupied territories menu in peacetime, not a conference |
| `on_release_as_free` | free nation | releaser | Vanilla comment in `12_wuw_on_actions.txt` |
| `on_force_government` | not stated | not stated | Listed in the docs; no vanilla file defines it |

Rows 1 to 3: [docs] `common/on_actions/_documentation.md`. Rows 4 to 8: [vanilla-confirmed 1.19.3] `common/on_actions/00_on_actions.txt`, `01_tfv_on_actions.txt`, `12_wuw_on_actions.txt`; the list of names is [docs] `common/on_actions/_documentation.md`.

- Because the three conference on actions run per winner-loser pair, an effect that should run once needs a flag guard. Vanilla's `on_before_peace_conference_start` in `14_sea_on_actions.txt` sets `peace_winner_flag` only when `ROOT` does not have it yet. [docs] `common/on_actions/_documentation.md` for the per-pair calls; [vanilla-confirmed 1.19.3] for the guard.
- Vanilla comments on `on_peaceconference_ended` disagree: `00_on_actions.txt` and `07_nsb_on_actions.txt` say "ROOT - country that just went to peace", while the docs, `14_sea_on_actions.txt` and `16_taog_on_actions.txt` say ROOT is the winner and FROM the loser. Vanilla code treats `ROOT` as the winner, for example `tag = SWI ... FROM = { original_tag = GER }` for Switzerland winning. Use the docs reading. [vanilla-confirmed 1.19.3] `common/on_actions/08_bba_on_actions.txt`.
- The wiki says `white_peace` and conditional surrender also fire the conference on actions. [unverified]
- Multiple `effect = { }` blocks in one on action are normal in vanilla (`08_bba_on_actions.txt` has seven under `on_peaceconference_ended`). [vanilla-confirmed 1.19.3]

```text
on_actions = {
    on_peaceconference_ended = {
        effect = {
            if = {
                limit = {
                    original_tag = GER
                    FROM = { original_tag = HOL }
                }
                remove_ideas = HOL_german_defectors_2
            }
        }
    }
}
```

[vanilla-confirmed 1.19.3] `common/on_actions/04_mtg_on_actions.txt` (shortened).

## Defines <a id="Defines"></a>

All values below are in `common/defines/00_defines.lua`. [vanilla-confirmed 1.19.3] Meanings follow the file comments. See also the wiki [Defines](<Defines - Hearts of Iron 4 Wiki.md#NDiplomacy>) page.

Base costs and cost factors, namespace `NDiplomacy`:

| Define | Value | Meaning |
| --- | --- | --- |
| `BASE_PEACE_PUPPET_FACTOR` | 100 | Base factor for puppet, in percent |
| `BASE_PEACE_LIBERATE_FACTOR` | 100 | Base factor for liberate, in percent |
| `BASE_PEACE_TAKE_UNCONTROLLED_STATE_FACTOR` | 10.0 | Base factor for taking a state you do not control |
| `BASE_PEACE_TAKE_FACTION_CONTROLLED_STATE_FACTOR` | 0.5 | Same, when someone in your faction controls it |
| `BASE_PEACE_FORCE_GOVERNMENT_COST` | 100 | Base cost of forcing a government change |
| `PEACE_COST_FACTOR_CONTESTED_MAX` | 15 | Cap on the contested factor |
| `PEACE_COST_FACTOR_UNCONTESTED_MAX` | 15 | Cap on the uncontested factor |
| `PEACE_COST_FACTOR_CONTESTED_BID` | 1.20 | Cost factor per contested bid on a state |
| `PEACE_COST_FACTOR_UNCONTESTED_BID_MIN` | 1.15 | Minimum factor per turn a bid stays uncontested |
| `PEACE_COST_FACTOR_UNCONTESTED_BID_MAX` | 1.60 | Maximum factor per turn a bid stays uncontested |
| `PEACE_COST_FACTOR_UNCONTESTED_BID_STEP` | 0.15 | Increase of the uncontested factor each turn |
| `PEACE_COST_FACTOR_CAPITAL_SHIP_IC` | 0.005 | Cost of taking one capital ship, per IC |
| `PEACE_COST_FACTOR_SCREENING_SHIP_IC` | 0.005 | Cost of taking a share of screening ships, per IC |
| `PEACE_INCREASE_COST_FACTOR_PER_MISSING_PERCENT_FOR_CAPITULATION` | 0.0012 | Extra cost when the loser has not capitulated, per percent between its surrender level and the base surrender level |
| `PEACE_COST_FACTOR_COMPLIANCE_STEPS` | { 0, 1.0, 30, 0.9, 70, 0.8 } | Occupier discount by compliance: factor 1.0 from 0 percent, 0.9 from 30, 0.8 from 70 |
| `PEACE_COST_FACTOR_STACK_DEMILITARIZED_ZONE` | 0.25 | Cost added by this stackable |
| `PEACE_COST_FACTOR_STACK_WAR_REPARATION` | 0.25 | Cost added by this stackable |
| `PEACE_COST_FACTOR_STACK_RESOURCE_RIGHTS` | 0.25 | Cost added by this stackable |
| `PEACE_COST_FACTOR_STACK_DISMANTLE_INDUSTRY` | 0.25 | Cost added by this stackable |
| `PEACE_TIMED_EFFECT_LENGTH_DEMILITARIZED_ZONE` | 1825 | Days a demilitarized zone lasts (5 years) |
| `PEACE_TIMED_EFFECT_LENGTH_WAR_REPARATION` | 1825 | Days war reparation lasts |
| `PEACE_TIMED_EFFECT_LENGTH_RESOURCE_RIGHTS` | 1825 | Days resource rights last |
| `PEACE_TIMED_EFFECT_RATIO_CIVILIAN_FACTORY_WAR_REPARATION` | 0.5 | Share of civilian factories taken by war reparation |
| `PEACE_TRIGGER_AI_MAX_INFLUENCE_VALUE` | 0.99 | Maximum influence value for `pc_is_state_outside_influence_for_winner` |
| `PEACE_ACTION_MAX_COST` | 9999 | Cap on a peace action's cost after all modifiers |

Score handling, namespace `NDiplomacy`:

| Define | Value | Meaning |
| --- | --- | --- |
| `PEACE_SCORE_SCALE_FACTOR` | 1.35 | Losers' total value times this is the default total score for the winners |
| `PEACE_SCORE_DISTRIBUTION` | { 0.2, 0.2, 0.2, 0.2, 0.2 } | Share of the total score released on each of the first turns |
| `PEACE_SCORE_MINOR_BOOST_FRACTION` | 0.05 | Low-scoring winners get at least this share of the turn's distributed score |
| `PEACE_CONTEST_REFUND_FACTOR` | { 1.0, 0.92, 0.84, 0.76 } | Share of spent score refunded in a contest, per round; the last value repeats |
| `PEACE_SCORE_TRANSFERRED_TO_FACTION_LEADER` | 0.1 | Share moved from members to the leader (game rule) |
| `PEACE_SCORE_RESET_LOW_SCORE_THRESHOLD` | 0.05 | Winners below this war participation give their score to other players |
| `PEACE_SCORE_RESET_LOW_SCORE_MINIMUM_FOR_RECEIVER` | 0.1 | Disables the previous rule if no winner reaches this |
| `PEACE_SCORE_TRANSFERRED_FROM_FACTION_INFLUENCE` | 0.1 | Share of war score given to the top influence members |
| `PEACE_SCORE_TOP_FACTION_INFLUENCE_AMOUNT` | 2 | Number of members that receive it |
| `PEACE_PLAY_SOUND_ON_NEW_TURN` | true | Play the `peace_conference_new_turn` audio hook |
| `PEACE_PLAY_NEW_TURN_SOUND_ONLY_IF_NOT_ALREADY_PLAYING` | true | Do not restart the hook if it is playing |

AI bidding, namespace `NAI`:

| Define | Value | Meaning |
| --- | --- | --- |
| `PEACE_BID_FOLD_TURNS_AGAINST_OTHER_AI` | 2 | Contests between AIs are resolved after this many turns |
| `PEACE_BID_CONTEST_TIE_BREAKER_CONFERENCE_SCORE` | 1.0 | Weight of remaining conference score in the tie break |
| `PEACE_BID_CONTEST_TIE_BREAKER_INFLUENCE_DISTANCE` | 1.0 | Weight of influence distance |
| `PEACE_BID_CONTEST_TIE_BREAKER_COUNTRY_SCORE` | 1.0 | Weight of country score |
| `PEACE_BID_FOLD_AGAINST_PLAYER_CHANCE` | 0.5 | Chance that the AI folds against a human |
| `PEACE_BID_FOLD_AGAINST_LIBERATE_CONTEST` | 1.0 | Chance that the AI backs down against a same-ideology liberate bid |
| `PEACE_AI_GROUP_PEACE_ACTIONS` | true | Group actions instead of greedily taking the most desired |
| `PEACE_AI_EVALUATE_FOR_SUBJECTS` | true | Consider giving states to subjects |
| `PEACE_AI_EVALUATE_FOR_ALLIES` | true | Consider giving states to allies |
| `PEACE_AI_EVALUATE_FOR_NON_ALLIES` | false | Consider giving states to non-allies |
| `PEACE_AI_EVALUATE_OTHER_IF_CORE` | true | Consider other winners that have a core |
| `PEACE_AI_EVALUATE_OTHER_IF_CLAIM` | true | Consider other winners that have a claim |
| `PEACE_AI_EVALUATE_OTHER_ALWAYS` | false | Always consider other winners; the file warns of heavy cost on large conferences |

Other namespaces:

| Define | Namespace | Value | Meaning |
| --- | --- | --- | --- |
| `PEACE_ACTION_TRANSFER_NAVY_EXPERIENCE_RETAINED` | `NNavy` | 0.25 | Share of experience kept by transferred ships |
| `PEACE_CONFERENCE_MINIMAL_REQUIREMENT` | `NFactions` | 0.5 | Power projection lead over the next contester before the discount starts |
| `PEACE_CONFERENCE_MAX_DISCOUNT` | `NFactions` | 0.25 | Discount reached at a 100 percent lead |
| `STATE_VALUE_BASE` | `NCountry` | 10.0 | Base value of a state, used for costs in conferences |

Map and interface defines named `PEACE_CONFERENCE_*` and `PEACE_*_COLOR_INDEX` (58 `PEACE` lines in `common/defines/00_graphics.lua`) only change colours, priorities and border drawing on the conference map. [vanilla-confirmed 1.19.3]

## Related settings <a id="Related_settings"></a>

- Autonomy states: `use_for_peace_conference_weight` is a weight block where `ROOT` is the puppet and `FROM` the potential overlord (vanilla comment in `puppet.txt`: "ROOT is puppet - FROM is potential OVERLORD"); `peace_conference_initial_freedom` sets the freedom a subject starts with after a conference, 0.001 in `supervised_state.txt`. [vanilla-confirmed 1.19.3] `common/autonomous_states/puppet.txt`, `supervised_state.txt`. See [Autonomy state modding](<Autonomy state modding - Hearts of Iron 4 Wiki.md>).
- Modifiers: `annex_cost_factor` and `puppet_cost_factor` (categories peace) still exist and vanilla still uses them in leader traits and balance of power data. The ideology file comments call the ideology versions deprecated in favour of the cost modifiers. [docs] `documentation/modifiers_documentation.md`; [vanilla-confirmed 1.19.3] `common/country_leader/00_traits.txt`, `common/bop/ITA.txt`, `common/ideologies/00_ideologies.txt`.
- Modifiers: `peace_score_ratio_transferred_to_overlord` (in 20 autonomous state files, e.g. `colony.txt` 0.1) and `peace_score_ratio_transferred_to_players` (AI difficulty static modifiers, e.g. `diff_very_easy_ai` 0.25). [docs] `documentation/modifiers_documentation.md`; [vanilla-confirmed 1.19.3] `common/autonomous_states/`, `common/modifiers/00_static_modifiers.txt`.
- Game rules that gate score movement: `peace_score_to_overlord`, `peace_score_to_faction_leader`, `peace_score_reset_low_scores`. [vanilla-confirmed 1.19.3] `common/game_rules/00_game_rules.txt`.

## Minimal example <a id="Minimal_example"></a>

A mod country `MYM` that gets cheaper core states after a focus, wants them, and gains a flag when it wins a conference. File names carry the mod tag so they cannot collide with vanilla files. [vanilla-confirmed 1.19.3] naming follows `AST_peace.txt` and `ai_peace/CHI.txt`.

`common/peace_conference/cost_modifiers/MYM_peace.txt`:

```text
peace_action_modifiers = {
    MYM_cheap_home_cores = {
        category = events_or_focuses
        peace_action_type = take_states
        enable = {
            ROOT = {
                original_tag = MYM
                has_completed_focus = MYM_reclaim_the_homeland
            }
            FROM.FROM.FROM = { is_core_of = ROOT.FROM }
        }
        cost_multiplier = 0.5
    }
}
```

`common/peace_conference/ai_peace/MYM.txt`:

```text
peace_ai_desires = {
    MYM_take_homeland_cores = {
        peace_action_type = take_states
        enable = {
            ROOT = { original_tag = MYM }
            ROOT.FROM = { tag = ROOT }
            ROOT.FROM.FROM.FROM = { is_core_of = ROOT.FROM }
        }
        ai_desire = 150
    }
}
```

`common/on_actions/MYM_on_actions.txt`:

```text
on_actions = {
    on_peaceconference_ended = {
        effect = {
            if = {
                limit = { original_tag = MYM }
                set_country_flag = MYM_won_a_conference
            }
        }
    }
}
```

Checks before shipping: the focus `MYM_reclaim_the_homeland` must exist, the category must be a vanilla or modded key, and `peace_action_type` must be spelled `take_states`. [docs] `cost_modifiers/_documentation.md`. The example follows the vanilla shapes in `AST_peace.txt`, `ai_peace/CHI.txt` and `04_mtg_on_actions.txt`; it was not run in the game. [vanilla-confirmed 1.19.3] for the shapes, [unverified] for runtime behaviour.

## Confirmed traps <a id="Confirmed_traps"></a>

- `FROM` means different things in the two systems. In peace scripts it is the taker. In the conference on actions it is the loser and `ROOT` is the winner. [docs] both `_documentation.md` files and `common/on_actions/_documentation.md`.
- Inside `ROOT = { ... }` or `any_country = { ... }`, `FROM` is not the taker. Use `ROOT.FROM`. [docs] `cost_modifiers/_documentation.md`.
- Vanilla contains the singular `take_state`: `defensive_war_take_state` in `cost_modifiers/00_generic_peace.txt` and `dont_take_state_if_already_puppeted_by_us` in `ai_peace/00_misc.txt`. The documented type is `take_states`. Do not copy the typo. What the engine does with an unknown type is [unverified]. [vanilla-confirmed 1.19.3]
- Vanilla repeats entry names inside one file: `DEN_take_former_overlords_state` (`DEN_peace.txt`), `unlikely_countries` (`ai_peace/00_misc.txt`), `ETH_agreed_expansion` (`ETH.txt`) and `SOV_wants_memel` (`SOV.txt`). Give every entry a unique name; whether the first or the second wins is [unverified]. [vanilla-confirmed 1.19.3]
- The `ai_desire` scale is ambiguous in the game's own files; see [The ai_desire scale](#The_ai_desire_scale). [docs] and [vanilla-confirmed 1.19.3]
- Diplomatic relations and ownership are not updated during a conference. Test `pc_is_puppeted`, `pc_is_liberated`, `pc_is_forced_government` and the other `pc_` triggers for in-conference results. [docs] both `_documentation.md` files.
- The wiki's Triggers page lists `pc_is_untouched_loser` and `pc_is_liberated_by`. Neither is in `documentation/triggers_documentation.md`, in vanilla script, or as a string in `hoi4.exe`. Do not use them. [docs] `documentation/triggers_documentation.md`; [vanilla-confirmed 1.19.3] searched `common/`, `events/`, `history/`.
- `cost_multiplier` must be above 0; a value of 0 or less is invalid. [docs] `cost_modifiers/_documentation.md`.
- Rule-backed modifiers: the docs say `enable` is not evaluated, but two vanilla modifiers carry a narrowing `enable` and a matching tooltip. Test a conditional faction modifier before relying on it. [docs] `common/factions/_documentation.md`; [unverified] which reading holds.
- A mod that adds categories keeps vanilla's `default = yes` and adds none of its own: the vanilla comment allows the flag on one category only. [vanilla-confirmed 1.19.3] `00_peace_action_categories.txt`.
- Tooltips for rule modifiers (`custom_modifier_tooltip` keys) are hand-written, and vanilla's have drifted from the script values. Re-check them after changing a multiplier. [vanilla-confirmed 1.19.3] `localisation/english/factions_l_english.yml`.

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<Collection modding - Hearts of Iron 4 Wiki.md>) • [Game rule modding](<Game rule modding - Hearts of Iron 4 Wiki.md>) • [Intelligence operation modding](<Intelligence operation modding - Hearts of Iron 4 Wiki.md>) • [Map mode modding](<Map mode modding - Hearts of Iron 4 Wiki.md>) • [Occupation and resistance modding](<Occupation and resistance modding - Hearts of Iron 4 Wiki.md>) • [Peace conference modding](<Peace conference modding - Hearts of Iron 4 Wiki.md>) • [Raid modding](<Raid modding - Hearts of Iron 4 Wiki.md>) • [Script constant modding](<Script constant modding - Hearts of Iron 4 Wiki.md>) • [Special project modding](<Special project modding - Hearts of Iron 4 Wiki.md>)
