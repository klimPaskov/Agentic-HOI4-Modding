# Intelligence operation modding

An intelligence operation is a timed covert mission that a country starts against a target country with a number of its operatives. It is built from three kinds of definition: the operation itself, its phases and the tokens it can award or require. The system is part of La Résistance: the on action file is `05_lar_on_actions.txt` and the loc file `lar_operations_l_english.yml`, and the wiki's Intelligence agency page says the DLC is needed. The DLC requirement itself is unverified.

## Overview

| Folder | Defines | Vanilla content |
| --- | --- | --- |
| `common/operations/` | Operations: cost, duration, access rules, outcome. | 39 operations in 6 files: `00_operations.txt` (20), `LaR_FRA_operations.txt` (10), `LaR_historical_operations.txt` (4), `NSB_historical_operations.txt` (3), `POL_historical_operations.txt` (1), `SIA_operations.txt` (1) |
| `common/operation_phases/` | Phases: the steps an operation passes through. | 82 phases in 16 files |
| `common/operation_tokens/` | Tokens: lasting marks of infiltration against a country. | `00_OperationTokens.txt`, 5 tokens |

- Operation ids, phase ids and token ids are separate namespaces. A phase can be shared by many operations: 29 of the 39 vanilla operations use `infiltration_border`, and `SIA_operations.txt` builds a DLC operation only from phases that already existed.
- Operatives (the people who run operations) are not defined in these folders. See Operatives below and [Character modding](character_modding.md#unit-leader-traits) for operative traits.
- Effects, triggers and modifiers of the system are in [Effects](effects.md#operatives), [Triggers](triggers.md#operatives), [Modifiers](modifiers.md#operatives) and the `NOperatives` section of [Defines](defines.md#noperatives) (its 1.19.3 additions are in [Defines additions](defines_additions.md#noperatives)).

## Scopes and life cycle

| Where | Scope | `ROOT` | `FROM` | `FROM.FROM` |
| --- | --- | --- | --- | --- |
| `allowed`, `operation_target` | country | the origin country | not set | not set |
| `visible`, `available`, `requirements`, phase `requirements` | country | the origin country | the target country | not set |
| `on_start`, `outcome_potential`, `outcome_execute`, `outcome_extra_execute` | operation | the origin country | the target country | the selected state, only if the operation has a `selection_target` |
| `phases` weights (`modifier` blocks) | country | the origin country | the target country | not set |

- Inside operation scope, effects are usually wrapped: `ROOT = { ... }` for the origin, `FROM = { ... }` for the target, `FROM.FROM = { ... }` for the state.
- Sequence: the player or AI picks an operation and a target, equipment is collected (preparing), operatives run the phases (running), then the operation completes. The triggers `is_preparing_operation`, `has_finished_collecting_for_operation`, `is_running_operation` and `num_finished_operations` read these states.
- On completion `on_operation_completed` fires, then `outcome_execute` (or `outcome_extra_execute`) runs once, and each assigned operative is checked for detection (`on_operative_detected_during_operation`). The wiki's On actions page gives this order. The scope comment in vanilla gives `THIS` as the operation, `ROOT` as the initiating country and `FROM` as the target; the order itself is unverified.
- Prepared operations are removed after `NOperatives.NUM_DAYS_BEFORE_REMOVING_PREPARED_OPERATIONS = 60` days.

## Operation definition

One root block per operation; the block name is the operation id. The folder is `common/operations/*.txt`.

### Keys the documentation describes

"Vanilla" counts are over the 39 vanilla operations.

| Key | Value | Meaning | Vanilla |
| --- | --- | --- | --- |
| `icon` | sprite | Icon in the operations list. | 39 |
| `name`, `desc` | loc key or text | Title and description; scripted localisation allowed. | 39, keys equal to the id and `<id>_desc` |
| `priority` | number | Order in the list of operations; higher comes first. | 25, values 0 to 18 |
| `days` | number | Duration in days. | 39, values 3 to 270 |
| `operatives` | number | Operatives needed to start. | 39, values 1 to 3 |
| `network_strength` | integer 0 to 100 | Hard requirement on the intelligence network strength in the target. | 39, values 10 to 75 |
| `phases` | block, repeatable | One block per phase slot. See Phases. | 117, three per operation |
| `danger_level` | number | Danger level the target perceives when the operation starts. Default 0. | 0 |
| `allowed`, `visible`, `available`, `requirements` | triggers | Access rules, see that section. | 20, 39, 28, 10 |
| `operation_target` | `{ targets = { TAG } }` | Countries that can be targeted. All when missing. | 0 |
| `selection_target`, `target_type` | block, `province` or `strategic_region` | Enables choosing a place in the target. | 14, 1 |
| `equipment`, `return_on_complete` | blocks | Cost, see Costs and equipment. | 36, 0 |
| `required_tokens`, `awarded_tokens` | token ids | See Tokens. | 10, 5 |
| `cost_modifiers`, `outcome_modifiers` | modifier ids | Modifiers that change cost and outcome chance. See Outcomes and risk. | 30, 31 |
| `on_start` | effect | Runs when the operation starts. Operation scope. | 18 |
| `outcome_potential` | effect | Only builds the reward tooltip. | 39 |
| `outcome_execute`, `outcome_extra_execute` | effects | The result. The documentation calls the second `outcome_execute_extra`; vanilla and `hoi4.exe` use `outcome_extra_execute`. | 39, 20 |
| `outcome_extra_chance` | number | Chance of the extra outcome ("bonus outcome" in the UI). | 20, values 0.25 to 0.5 |
| `ai_will_do` | weight block | AI score. The AI drops a prepared operation whose score falls below `OPERATION_AI_MINIMUM_SCORE` (10.0). | 0 |
| `will_lead_to_war_with` | `yes` | Warns the AI that the operation leads to war with the target. | 1 |

- `awarded_tokens` is "for display purposes only in tooltips". It grants nothing; the outcome effect must call `add_operation_token`.
- `outcome_potential` "is for description purposes only": the engine builds the reward tooltip from it, so put the same effects there or a `custom_effect_tooltip` that explains them. Vanilla repeats the real effects or uses `custom_effect_tooltip`.
- The docs example for `visible` says that without one the game shows operations whose network is below `NOperatives.INTEL_NETWORK_MIN_DEFAULT_FOR_SHOWING` (25) or at half the required strength, and also filters by operation count. Write your own `visible` (all 39 vanilla operations do) to avoid depending on that.
- `outcome_extra_chance` is a fraction in vanilla (0.25, 0.33, 0.5), not a percentage as in the doc example.

### Keys only vanilla uses

Not in the documentation. Counts over the 39 vanilla operations. The strings are also in `hoi4.exe`.

| Key | Used by | Values and meaning |
| --- | --- | --- |
| `map_icon` | 39 | Sprite for the map icon. |
| `risk_chance` | 39 | 0 to 0.5. Base risk for the operatives. The UI describes risk as the likelihood that an operative is captured or killed after completion (`OPERATION_OUTLOOK_DESC`). |
| `risk_modifiers` | 29 | Modifier ids that change the risk. |
| `experience` | 23 | 0.5 to 5. Probably the experience the operatives earn. (unverified) |
| `cost_multiplier` | 9 | 0 (2), 0.05 (4), 0.25 (3). Overrides the default cost growth for repeats against the same target: the define comment says cost and time grow by `DEFAULT_OPERATION_COST_MULTIPLIER` (0.15) and `DEFAULT_OPERATION_TIME_MULTIPLIER` (0.0) per earlier run, "can be overridden using time_multiplier & cost_multiplier". The rescue operations use 0. |
| `time_multiplier` | 0 | Named in that define comment; the string is in `hoi4.exe`. (unverified) |
| `selection_target_state` | 13 | State-scope trigger that filters which states can be picked, for example `has_resistance = yes` or `is_capital = no`. |
| `target_weight` | 3 | Weight block (`base`, `modifier` with `add`, temp variables), probably for the AI's choice of state. (unverified) |
| `scale_cost_independent_of_target` | 1 | On `operation_fake_intel`. Probably counts earlier runs regardless of target. (unverified) |
| `is_staged_coup`, `is_captured_cipher` | 1 each | Markers on the coup and cipher operations; the triggers `is_staging_coup` and `is_target_of_coup` suggest the engine reads the first. (unverified) |
| `prevent_captured_operative_to_die` | 1 | On `operation_rescue_operative`. Probably protects the captive while the rescue runs. (unverified) |

## Phases

### Phase slots in an operation

```text
phases = { #infiltration
	infiltration_border = { base = 25 }
	infiltration_paradrop = {
		base = 25
		modifier = {
			ROOT = { has_equipment = { transport_plane_equipment < 1 } }
			factor = 0
		}
	}
}
```

- Each `phases = { ... }` block is one slot. It lists candidate phase ids with a `base` weight and any number of `modifier` blocks (`add` or `factor` plus triggers). The game picks one phase per slot. The slots share the duration of the operation evenly.
- All 39 vanilla operations use exactly three slots, usually infiltration, a middle step and exfiltration. Other counts are allowed by the documentation.
- A slot with one candidate and `base = 100` fixes that phase, as the historical operations do (`heavy_water_infiltration`, `heavy_water_attack`, `heavy_water_exfiltration`).
- Candidates whose phase `requirements` fail are invalid; this is checked weekly, and operations whose phases were chosen in advance are re-seeded when one becomes invalid. Keep at least one candidate without requirements in every slot (`infiltration_diplomatic`, `exfiltration_go_to_ground` in vanilla). Neither of those two vanilla phases has a `requirements` block. Whether a slot with no valid candidate breaks the operation is unverified.
- Weights in `modifier` blocks use `factor = 0` to remove a candidate and `factor = 20` to favour it (`infiltration_diplomatic` when nobody is at war).
- The entries `phase_1`, `phase_2` and `phase_3` of `00_operation_phases.txt` are test placeholders that no operation uses.

### Phase definition

Root block per phase in `common/operation_phases/*.txt`; the block name is the phase id.

| Key | Meaning | Vanilla |
| --- | --- | --- |
| `name`, `desc` | Title and description. Scripted localisation allowed. | 82 |
| `icon` | Small sprite (`..._small`). | 82 |
| `picture` | Large picture. | 82 |
| `outcome` | Outcome text used to build the final story. | 75 |
| `map_icon` | Map icon. Falls back to `icon`. | 0 |
| `outcome_extra` | Alternative outcome text; falls back to `outcome`. The doc says it is meant for runs where something risky happened. | 0 |
| `requirements` | Trigger, country scope, `ROOT` and `FROM` as in operations. Shown in the UI. | 26 |
| `equipment` | Cost, scaled by the operation's multiplier. | 72 |
| `return_on_complete` | `yes` refunds this phase's equipment at the end. Default `no`. | 2 |
| `risk_extra` | Loc key of the story text when the operatives were at risk. Not in the documentation. | 7 |

- The seven `risk_extra` users are exfiltration-type phases (four in `lar_exfiltration.txt`, plus `launch_coup_exfiltration`, `heavy_water_exfiltration`, `bruneval_exfiltration`); the values end in `_outcome_fail`. Vanilla never sets `outcome_extra`. Copy the vanilla pattern: `outcome` on every phase, `risk_extra` on exfiltration-style phases. The docs say `outcome_extra` text is used when a `risk_extra` happened and falls back to `outcome`. How the engine uses `risk_extra`, which vanilla sets in place of `outcome_extra`, is unverified.
- A phase is only used when an operation's `phases` blocks name it. Vanilla splits the phases over 16 files by theme (`lar_infiltration.txt`, `lar_exfiltration.txt`, `lar_targeted_sabotage.txt`, ...).

## Costs and equipment

- `equipment = { infantry_equipment = 5000 }` is an operation's base cost in equipment types. Vanilla uses `infantry_equipment` (17 operations, 50 to 12000), `support_equipment` (14) and `civilian_factories` (2). Phases also use `transport_plane_equipment` (1 or 2) and `small_plane_airframe`.
- `civilian_factories = { amount = 15 days = 5 }` allocates factories over time, like the intelligence agency cost. It is "exceptionally" supported as an equipment type in operations and phases. Example in `operation_coordinated_strike`.
- Equipment is consumed unless `return_on_complete = yes` is set. The operation's key and each phase's key refund independently.
- Repeat runs against one target cost more by `DEFAULT_OPERATION_COST_MULTIPLIER` (0.15) each. Set `cost_multiplier = 0` for a flat price, as the rescue operations do.
- The AI adds operation equipment to its production needs through `OPERATION_EQUIPMENT_NEED_PRODUCTION_MULT = 1.0`.

## Tokens

Root block per token in `common/operation_tokens/*.txt`. A country can hold only one token of an id against another country; tokens do not stack.

| Key | Meaning | Vanilla |
| --- | --- | --- |
| `name`, `desc` | Loc keys. | 5 (`OPERATION_TOKEN_INFILTRATED_ARMY`, `..._DESC`) |
| `icon` | Sprite shown on the token (`GFX_infiltrate_army_bg`). | 5 |
| `text_icon` | Sprite for loc text (`GFX_text_infiltrate_army_token`). Not in the documentation. | 5 |
| `intel_source`, `intel_gain` | The token raises one intel source (`navy`, `army`, `civilian`, `airforce`) by this amount; one gain per token. | 5, gain 10 (5 for `token_resistance_contacts`) |
| `targeted_modifier` | Id of a targeted modifier applied to the relation while the token is held. Repeatable. | 0 |

The docs only show the placeholder `targeted_modifier_id1` and no vanilla token uses the key. What a valid `targeted_modifier` id looks like is unverified. An id that does not exist is reported at load as `missing static modifier definition: <id>`, so the id names a static modifier definition. The token could still be granted and held: `has_operation_token` was TRUE and `print_operation_tokens` listed it. The effect of the token on relations was not tested.

Vanilla ids: `token_army`, `token_navy`, `token_airforce`, `token_civilian`, `token_resistance_contacts`.

Script access, all in country scope with `tag` naming the target:

```text
ROOT = { add_operation_token = { tag = FROM token = token_civilian } }
remove_operation_token = { tag = GER token = token_civilian }
has_operation_token = { tag = GER token = token_civilian }
```

- `required_tokens` blocks launching until the token is held. Operations that consume one remove it in `outcome_execute` (`remove_operation_token`).
- The token ids can be used outside operations: the coup operation checks `token_army` to enlarge the rebels.
- Token intel is a static intel source; its maximums are set by `NIntel.STATIC_INTEL_SOURCE_OPERATION_TOKENS_MAXIMUMS`, an empty list in vanilla. How the empty list is read is unverified.

## Access, requirements and targets

- `allowed`: "visible to the player", checked with the origin country only. Vanilla uses it for fixed restrictions: `original_tag`, a DLC, or a game rule such as `NOT = { has_game_rule = { rule = allow_coups option = BLOCKED } }`. See [Game rule modding](game_rule_modding.md).
- `visible`: whether the player sees the operation. Vanilla shows operations when `network_national_coverage` over the target is above 0, when the right token is held, and so on.
- `available`: whether the player can launch the operation. Vanilla uses `has_war_with`, `can_declare_war_on`, `has_wargoal_against` here.
- `requirements`: like `available`, but checked while the operation runs as well; if it stops holding the operation is cancelled.
- `network_strength`: the operation also needs that strength in the target. The trigger form is `network_strength = { target = FROM state = 110 value > 50 }`; `network_national_coverage = { target = FROM value > 0 }` reads coverage.
- `selection_target = { targets = { FROM } }` lets the player pick a place in the target; the state is then `FROM.FROM`. 14 vanilla operations use `targets = { FROM }`. Use `selection_target_state = { ... }` to limit selectable states. `target_type = strategic_region` selects a strategic region instead (`operation_coordinated_strike`).
- `operation_target = { targets = { ENG } }` limits target countries; vanilla never uses it and writes country restrictions in `visible` or `available`.
- Historical operations combine `allowed`, `visible`, `available` and flags: see `heavy_water_raid`.

## Outcomes and risk

- `outcome_execute` runs once per finished operation. `outcome_extra_execute` runs instead of it when the `outcome_extra_chance` roll succeeds. Vanilla extra blocks repeat the base reward and add more, so the extra block replaces the base one. "replaces" is unverified, read from `operation_infiltrate_civilian` and `operation_targeted_sabotage_industry`.
- Typical effects in vanilla: `add_operation_token`, `add_intel`, `add_decryption`, `steal_random_tech_bonus`, `start_civil_war`, `add_resistance_target`, `declare_war_on` with `execute_operation_coordinated_strike`, `free_random_operative`, `release_captured_generals_from`.
- `execute_operation_coordinated_strike = { amount = 12 }` runs the Coordinated Strike simulation `amount` times and works only in operation scope.
- `risk_chance` is the base risk; `risk_modifiers`, `outcome_modifiers` and `cost_modifiers` list modifier ids that adjust risk, bonus-outcome chance and cost. Vanilla lists a generic id and often a family id: `risk_modifiers = { operation_infiltrate_risk operation_risk }`.
- The generic modifiers are `operation_cost`, `operation_outcome` and `operation_risk`, category `intelligence_agency`. For every operation id the game also offers `<operation>_cost`, `<operation>_outcome` and `<operation>_risk`, and a few family names (`operation_infiltrate_*`, `operation_steal_tech_*`, `operation_coup_cost`, `target_sabotage_*`). Whether a new operation's own three modifiers apply without being listed is not stated; list the generic ones to be safe. The advice is unverified.
- `operation_targeted_sabotage_industry` and `_infrastructure` list `operation_risk` under `outcome_modifiers` and `operation_outcome` under `risk_modifiers`, the reverse of `operation_targeted_sabotage_resources`. Do not copy the swapped pair.
- What happens to each operative after completion is scripted in the on action `on_operative_detected_during_operation`. Scope is the operative, `ROOT` the origin, `FROM` the target, `FROM.FROM` the selected state. Vanilla rolls 45 hiding, 25 capture, 25 harm, 5 kill. Override it in a mod on action to change consequences for every operation. (unverified)

## Operatives

| Need | Tool |
| --- | --- |
| Create an operative | `create_operative_leader = { name = "..." GFX = GFX_portrait_x traits = { operative_linguist } bypass_recruitment = no available_to_spy_master = yes nationalities = { FRA } female = yes }` in country scope. Also `portrait_tag_override`, `gender`. |
| Loop over them | `every_operative`, `random_operative`, `any_operative_leader`, `all_operative_leader` in country or operation scope. |
| Change state | `capture_operative`, `free_operative`, `free_random_operative`, `kill_operative`, `turn_operative`, `harm_operative_leader`, `force_operative_leader_into_hiding`, `capture_by` (generals). |
| Query | `is_operative`, `is_operative_captured`, `has_captured_operative`, `operative_leader_mission`, `operative_leader_operation`, `num_of_operatives`, `num_operative_slots`, `num_free_operative_slots`, `is_spymaster`. |
| Variables | `operatives` array, `operation_country`, `operation_state`, `operation_type`, `operative_captor`, `own_capture_chance_factor`, `intel_yield_factor_on_capture`. |
| Fire an event | `operative_leader_event = { id = my.1 days = 3 recipient = ROOT set_from_from = FROM }` |

The `create_operative_leader` keys in the first row: counted over 122 vanilla calls, `bypass_recruitment` 120, `nationalities` 116, `name` and `traits` 105, `available_to_spy_master` 104, `GFX` 99, `gender` 30, `female` 26, `portrait_tag_override` 14, lowercase `gfx` 6.

- Operatives are not characters; they are created only with `create_operative_leader`. Operative traits are unit leader traits with `type = operative` in `common/unit_leader/`; `00_traits.txt` has 12 (`operative_commando`, `operative_seducer`, `operative_linguist`, `operative_tough`, and so on) and they use modifiers such as `operation_steal_tech_risk`. See [Character modding](character_modding.md#unit-leader-traits).
- `operative_leader_event` is an event type like `country_event`. Vanilla ones have `id`, `title`, `desc`, `is_triggered_only = yes`, `major = no` and `option` blocks. Extra arguments of the firing effect: `originator`, `recipient`, `set_root`, `set_from`, `set_from_from` change the scopes seen by the localisation. See [Event modding](event_modding.md).
- Operative on actions: `on_operation_completed`, `on_operative_detected_during_operation`, `on_operative_on_mission_spotted`, `on_operative_captured`, `on_operative_death`, `on_fully_decrypted_cipher` and `on_activated_active_decryption_bonuses` have blocks in `common/on_actions/05_lar_on_actions.txt`, with the scopes in the comments above each. `on_operative_created` and `on_operative_recruited` are in the on action list but their vanilla blocks are commented out. See [On actions](on_actions.md#la-résistance).
- Maximum recruited operatives: `NOperatives.MAX_RECRUITED_OPERATIVES = 10`.
- Operatives can also run missions (build intel network, counter intelligence, root out resistance and others). Mission tokens are used by `operative_leader_mission` and the AI strategy `operative_mission`.

## AI

- `ai_will_do` in an operation behaves like any weight block, but no vanilla operation sets it.
- The AI runs operations through strategies. `type = operative_operation` names an operation, a target and a score; `operation_equipment_priority` is listed without a description (vanilla pairs it with `value = 100` next to an `operative_operation`, so it presumably raises the production priority of the operation's equipment (unverified)); `operative_mission` assigns operatives to missions such as `build_intel_network` that support the operation.

```text
ai_strategy = {
	type = operative_operation
	operation = operation_boost_resistance
	value = 2500
	operation_target = GER
}
ai_strategy = { type = operation_equipment_priority value = 100 }
```

- `state` and `region` lines (and `priority`) in `operative_operation` steer the AI to places in the target.
- Vanilla also has a generic planner: the scripted effect `update_operation_ai` picks a target with the scorer `ai_generic_operation_target_scorer`, scores a hard-coded list of operations (stored as `token:operation_infiltrate_civilian`, and so on), writes the variables `generic_operation_target` and `generic_operation_type_to_run`, and the strategy `run_generic_operation` reads them. A custom operation is not in that list, so add your own `operative_operation` strategy.
- Country files such as `ENG_operation_strats.txt` show the usual shape: an `enable` trigger with dates, wars and `num_of_operatives`, `abort_when_not_enabled = yes`, then the strategies.
- Operation-related AI defines: `OPERATION_AI_MINIMUM_SCORE = 10.0`, `OPERATION_EQUIPMENT_NEED_PRODUCTION_MULT = 1.0`.
- `will_lead_to_war_with = yes` makes the AI prepare for the war an operation will cause (as `operation_coordinated_strike` does).

## Localisation

All keys below are vanilla patterns.

| Text | Key | Example |
| --- | --- | --- |
| Operation name | the `name` value, usually the id | `operation_infiltrate_civilian: "Infiltrate Civilian Administration"` |
| Operation description | the `desc` value, `<id>_desc` | description uses `[From.GetNameDef]` |
| Phase name, description | `<phase>`, `<phase>_desc` | `infiltration_border`, `infiltration_border_desc` |
| Phase outcome | `<phase>_outcome` | `infiltration_border_outcome` |
| Phase bad outcome | `<phase>_outcome_fail` (the `risk_extra` value) | `exfiltration_border_outcome_fail` |
| Token | `OPERATION_TOKEN_INFILTRATED_ARMY`, `..._DESC` | "Army Infiltration" |
| Tooltip effect | the key in `custom_effect_tooltip` | `coordinated_strike_tt` |
| Risk and outcome labels | `OPERATION_RISK_HEADER`, `OPERATION_OUTCOME_HEADER`, `RISK_LOW`, `RISK_MID`, `RISK_HIGH`, `OUTCOME_BASE`, `OUTCOME_GOOD`, `OUTCOME_VGOOD` | "SAFE", "RISKY", "DEADLY" |
| Modifier names | `operation_<id>_cost`, `_outcome`, `_risk` in `modifiers_l_english.yml` | "Stage Coup risk" |

- In scripted localisation inside operation text, `From` and `Root` follow the operation scopes above.

## GFX

Sprites are plain `spriteType` entries; vanilla keeps them in `interface/lar_operations.gfx` and `interface/operationoverview.gfx`, with token text icons in `interface/texticons.gfx`.

| Use | Sprite pattern | Size |
| --- | --- | --- |
| Operation `icon` | `GFX_operations_<name>` (`gfx/interface/operations/`) | 85 by 85 |
| Operation `map_icon` | `GFX_operations_<name>_map` (`gfx/interface/operations/map/`) | 48 by 48 |
| Phase `picture` | `GFX_phase_<name>` (`gfx/interface/operations/images/`) | 210 by 176 |
| Phase `icon` | `GFX_phase_<name>_small` (`gfx/interface/operations/phases_small/`) | 59 by 58 |
| Token `icon` | `GFX_infiltrate_<kind>_bg` (`gfx/interface/operations/`) | 33 by 29 |
| Token `text_icon` | `GFX_text_infiltrate_<kind>_token` (`gfx/texticons/`) | 24 by 21 |

Historical operations name sprites `GFX_historical_<name>`. For agency logos see [Intelligence agency modding](intelligence_agency_modding.md#gfx).

## Testing

Also in [Console commands](console_commands.md).

- `operation_start <operation id> <target tag>` starts an operation; `operation_debug` takes the same arguments; `allowoperations` allows every operation; `operation_test_phase_selection <operation id> <target tag>` tests phase selection; `prevent_operative_detection` stops a country from detecting and harming foreign operatives; `emulate_ai_operative_assignment <tag>` logs what the operative AI would assign this tick.
- `force_operative_detection` (alias `snitch`), `Operation.Instant` and `print_operation_tokens` have no usable description in the documentation. Their effect is read from the name only and is unverified.

## Minimal example

An operation that reuses vanilla phases and tokens. Built from the shapes of `SIA_operations.txt` and `operation_infiltrate_civilian`. The ids are made up.

`common/operations/my_mod_operations.txt`

```text
my_mod_sabotage_morale = {
	icon = GFX_operations_targeted_sabotage
	map_icon = GFX_operations_targeted_sabotage_map
	name = my_mod_sabotage_morale
	desc = my_mod_sabotage_morale_desc
	priority = 20
	days = 60
	network_strength = 35
	operatives = 2

	visible = {
		network_national_coverage = { target = FROM value > 0 }
	}
	available = {
		has_war_with = FROM
	}
	equipment = {
		infantry_equipment = 500
	}

	risk_chance = 0.2
	experience = 2
	outcome_extra_chance = 0.25
	risk_modifiers = { operation_risk }
	outcome_modifiers = { operation_outcome }
	cost_modifiers = { operation_cost }

	outcome_potential = {
		FROM = { add_stability = -0.05 }
	}
	outcome_execute = {
		FROM = { add_stability = -0.05 }
	}
	outcome_extra_execute = {
		FROM = { add_stability = -0.1 }
	}

	phases = { #infiltration
		infiltration_border = { base = 25 }
		infiltration_diplomatic = { base = 25 }
	}
	phases = {
		targeted_sabotage_plant_explosives = { base = 100 }
	}
	phases = { #exfiltration
		exfiltration_border = { base = 30 }
		exfiltration_go_to_ground = { base = 30 }
	}
}
```

`localisation/english/my_mod_operations_l_english.yml`

```text
l_english:
 my_mod_sabotage_morale: "Sabotage Morale"
 my_mod_sabotage_morale_desc: "Our agents will undermine the will of [From.GetNameDef] to fight."
```

## Traps

- `awarded_tokens` is display only. Without `add_operation_token` in the outcome the operation awards nothing.
- Use `outcome_extra_execute`, not the `outcome_execute_extra` of the documentation; `hoi4.exe` does not contain the second spelling.
- `outcome_extra_chance` is 0 to 1 in vanilla. A value of 50 as in the doc example is not confirmed to work.
- `outcome_potential` must match what `outcome_execute` does, or the tooltip lies. Effects run only from `outcome_execute`.
- Open a country scope before country effects. Vanilla outcomes use `ROOT = {}`, `FROM = {}`, `FROM.FROM = {}` (the state) or a tag such as `GER = {}`; `every_state` and `random_list` also appear directly.
- A slot whose candidates all have failing requirements has no valid phase. Give each slot a candidate without requirements. The docs say a phase whose `requirements` fail is invalid. What happens when every candidate of a slot is invalid is unverified.
- The two `operation_targeted_sabotage_industry` and `_infrastructure` blocks with swapped risk and outcome modifier lists look like a vanilla slip; do not copy them.
- `FROM.FROM` is only set when the operation has a `selection_target`.
