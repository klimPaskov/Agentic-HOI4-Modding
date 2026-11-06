# Military industrial organization modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="76388" sources="common/military_industrial_organization/ common/equipment_groups/mio_equipment_groups.txt common/technology_tags/00_technology.txt common/defines/00_defines.lua common/scripted_triggers/NOR_scripted_triggers.txt common/characters/GER.txt common/country_leader/00_traits.txt documentation/effects_documentation.md documentation/triggers_documentation.md documentation/modifiers_documentation.md localisation/english/military_industrial_organization_l_english.yml hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against the three `_documentation.md` files under `common/military_industrial_organization/`, all 55 `.txt` files in `organizations/` (552 MIO definitions), the 22 policies in `policies/`, `ai_bonus_weights/ai_bonus_weights.txt`, the MIO defines in `common/defines/`, the MIO effects, triggers and modifiers in `documentation/`, and `common/equipment_groups/mio_equipment_groups.txt`.
- Kit blocks added: folder and file facts, a key-by-key check of the MIO and trait tables, the `initial_trait` key fix, the Delta MIO section (`include`, `add_trait`, `override_trait`, `remove_trait`, `delete_included_values`, DLC gating as vanilla does it), policy checks, the AI Bonus Weights section, equipment stat, production and organisation bonus checks (with the funds, size and task capacity defines), and a runtime scripting list.
- Errors found in the wiki text: `documentation.info` files (now `_documentation.md`), `organization_bonus` (real key `organization_modifier`), `naval_supremacy_factor` (documented stat is `naval_dominance_factor`), a tank stat list missing six stats, and positive example values for cost factors that would raise the cost. The two "TODO: Write" sections are answered by kit blocks. `task_capacity` is a documented key that vanilla never writes, and `ENABLE_TASK_CAPACITY` is false.
- Gaps left: the AI scoring formula, how several `ai_bonus_weights` files merge, and what a repeated `trait = { token = ... }` inside a Delta MIO does are not documented. Nothing was run in the game before 2026-11-02, and since then only the statements tagged `[game-tested 1.19.4.1]` have been.
**1.19.4.1 re-check (2026-11-01).** 34 statements depended on files the update changed (`BRA_organization.txt` and `CHI_organization.txt`, `mio_equipment_groups.txt`, the technology tags, the MIO localisation file, `common/characters/GER.txt` and `common/country_leader/00_traits.txt`), and all 34 were re-measured. One MIO definition was added (552 to 553 definitions, `include` 516 to 517, `allowed` 551 to 552, `icon` 501 to 502, `name` 113 to 114, `available` 250 to 251, `has_dlc` 711 to 712), and two figures that no longer reproduce were corrected (trait `ai_will_do` with `base = 2` 194 to 190, relative trait offsets "-5 to 9" now "-5 to 7"). Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="mio-files-notes" at="section:files-and-folders" -->
The `documentation.info` files named above do not exist in 1.19.3. Each of the three folders holds a `_documentation.md` instead, and `organizations/_documentation.md` also lists the equipment stats a trait bonus can use. [vanilla-confirmed 1.19.3] `common/military_industrial_organization/organizations/_documentation.md`, `policies/_documentation.md`, `ai_bonus_weights/_documentation.md`.

What the three folders hold in 1.19.4.1. All rows: [vanilla-confirmed 1.19.4.1] `common/military_industrial_organization/`.

| Folder | Content |
| --- | --- |
| `organizations/` | 55 `.txt` files with 553 top-level MIO definitions: `00_generic_organization.txt` (30 archetypes), one file per country tag, `00_DEBUG_organization.txt`, `mio.txt` (test MIOs, `allowed = { always = no }`) and `_template_organization.txt` (comments only). One shipped file is named `RAJ_GOE_organization .txt`, with a space before the extension. |
| `policies/` | `_air_policies.txt` (5 policies), `_general_policies.txt` (7), `_land_policies.txt` (5), `_navy_policies.txt` (5). |
| `ai_bonus_weights/` | the single file `ai_bonus_weights.txt`. |

The names an MIO refers to are defined elsewhere. `equipment_type` takes equipment types, archetypes, categories and equipment groups. [docs] `common/military_industrial_organization/organizations/_documentation.md`. The 24 `mio_cat_eq_*` groups that vanilla uses are in `common/equipment_groups/mio_equipment_groups.txt`. [vanilla-confirmed 1.19.4.1] `common/equipment_groups/mio_equipment_groups.txt`. `research_categories` takes technology categories that technologies list in `categories`; the 19 `mio_cat_*` tags are declared in `common/technology_tags/00_technology.txt` and attached to technologies such as those in `common/technologies/armor.txt`. [vanilla-confirmed 1.19.4.1] `common/technology_tags/00_technology.txt`. See [Equipment modding](equipment_modding.md) for equipment archetypes and groups, [Unit modding](unit_modding.md) for unit types and [Technology modding](technology_modding.md) for technology categories.

MIO names and trait names are localisation keys. A key prefixed with the owner's tag wins over the plain key: `localisation/english/military_industrial_organization_l_english.yml` has `GER_porsche_organization` and `MEX_GER_porsche_organization` side by side. [vanilla-confirmed 1.19.4.1] `localisation/english/military_industrial_organization_l_english.yml`.
<!-- kit:end id="mio-files-notes" -->

<!-- kit:begin id="mio-key-checks" at="section:the-properties-explained" -->
Key-by-key check of the table above. Counts are MIO definitions that write the key at MIO level, out of 553 in `organizations/`.

| Key | In 1.19.3 |
| --- | --- |
| `name` | Lookup is `<TAG>_<name>` first, then `<name>`, with TAG the tag of the MIO owner; the key may use scripted localisation with the MIO as scope. [docs] `organizations/_documentation.md`. Written in 114 definitions, all Delta MIOs that reuse another name: `GRE_royal_hellenic_naval_shipyard_bftb_organization` points at the key of its non-DLC twin. [vanilla-confirmed 1.19.4.1] `organizations/GRE_organization.txt`. |
| `icon` | Order is the `icon` value, then `GFX_<TAG>_<MIO token>`, then `GFX_<MIO token>`, then `GFX_idea_unknown`. [docs] `organizations/_documentation.md`. Written in 502 definitions. [vanilla-confirmed 1.19.4.1] `organizations/`. |
| `background` | Documented as the GFX key of the Details window background, with a standard background chosen by equipment type when absent. [docs] `organizations/_documentation.md`. No vanilla definition writes it. [vanilla-confirmed 1.19.4.1] 0 of 553. |
| `allowed` | Country scope. Evaluated once at game start for every country, including tags that do not exist yet; a true result creates an instance of the MIO for that country. [docs] `organizations/_documentation.md`. 552 definitions write it; the one that does not inherits it through `include`. [vanilla-confirmed 1.19.4.1] `organizations/mio.txt`. |
| `visible`, `available` | Both default to `always = yes`, run in MIO scope with `FROM` as the country, and the AI and script treat an MIO as enabled only when both are true. [docs] `organizations/_documentation.md`. Written in 101 and 251 definitions. [vanilla-confirmed 1.19.4.1] `organizations/`. How script reaches the country is in the note below the table. |
| `equipment_type`, `research_categories` | Written in 62 and 52 definitions; the others inherit both from an archetype with `include`. A Delta MIO may replace `equipment_type` (`BEL_cockerill_shipyards_organization` does). [vanilla-confirmed 1.19.4.1] `organizations/BEL_organization.txt`. |
| `on_design_team_assigned_to_tech` and the five other `on_*` blocks | Documented as optional on-action effects that run in MIO scope with `FROM` as the country. [docs] `organizations/_documentation.md`. No vanilla definition uses any of them. [vanilla-confirmed 1.19.4.1] 0 of 553. |
| `research_bonus` | The default is the define `DESIGN_TEAM_RESEARCH_BONUS`, 0.05 in 1.19.3. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. Two definitions set it: `BUL_varna_naval_dockyard_organization` (0) and a test MIO in `mio.txt`. [vanilla-confirmed 1.19.4.1] `organizations/`. |
| `task_capacity` | A real, documented key: the number of tasks the MIO can run in parallel, with the default taken from the define `DEFAULT_INITIAL_TASK_CAPACITY`. [docs] `organizations/_documentation.md`. No vanilla definition writes it, which is why the page inventory could not find it in vanilla. The switch that turns it on is off in 1.19.4.1: see the note below the table. |
| `ai_will_do` | MIO scope with `FROM` as the country. The result is a multiplier applied to the weights from `ai_bonus_weights`. [docs] `organizations/_documentation.md`. One vanilla MIO writes it, `SPR_hispano_suiza_organization`, as `factor = 1` plus a `modifier` block. [vanilla-confirmed 1.19.4.1] `organizations/SPR_organization.txt`. |
| `tree_header_text` | `x` is the column of the cell where the label is centred, and a decimal such as 1.2 centres it between two cells; there is room for one line of text. [docs] `organizations/_documentation.md`. Vanilla writes 178 of these blocks with values such as 0.11, 4.2, 6.5 and 8.97, so "0 to 9" is a range, not a list of integers. [vanilla-confirmed 1.19.4.1] `organizations/`. |

Notes on rows of the table above:

- `visible`, `available`: The country is reached with `FROM`, with `owner` (`owner = { has_completed_focus = ... }` in `GRE_organization.txt`) or by its tag (`AFG = { has_country_flag = ... }` in `AFG_organization.txt`). [vanilla-confirmed 1.19.4.1] `organizations/`.
- `task_capacity`: The defines `ENABLE_TASK_CAPACITY = false` and `DEFAULT_INITIAL_TASK_CAPACITY = 0` ship in 1.19.4.1. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua` (the define's comment reads "Enable limited task capacity for MIOs"). With the switch off, `task_capacity` limits nothing: a test MIO with `task_capacity = 1` became the manufacturer of two infantry lines at once, and both line badges read "IGC Task MIO". With a mod define that sets `ENABLE_TASK_CAPACITY = true`, the MIO picker gains a Capacity column, the test MIO showed 1/1 after the first line, vanilla MIOs showed 0/0 (`DEFAULT_INITIAL_TASK_CAPACITY = 0`), and the second assignment did not take. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, two launches, MIO picker screenshots. The modifier `military_industrial_organization_task_capacity` and `add_mio_task_capacity` were not tested, so their effect with the switch off is [unverified].
<!-- kit:end id="mio-key-checks" -->

<!-- kit:begin id="mio-initial-trait-fix" at="heading:initial-trait" -->
The fifth key in the list below is `organization_modifier`, not `organization_bonus`. `organization_bonus` is not a key in the documentation or in any vanilla file. [docs] `common/military_industrial_organization/organizations/_documentation.md`. [vanilla-confirmed 1.19.4.1] 0 uses under `common/`. The documentation lists exactly five relevant keys for `initial_trait`: `name`, `limit_to_equipment_type`, `equipment_bonus`, `production_bonus` and `organization_modifier`; without `name` the default key is built from the token `initial_trait`. [docs] `common/military_industrial_organization/organizations/_documentation.md`. The 87 vanilla `initial_trait` blocks use those five keys and nothing else, apart from a stray `token` in two blocks that the engine presumably ignores. [vanilla-confirmed 1.19.4.1] `common/military_industrial_organization/organizations/`.
<!-- kit:end id="mio-initial-trait-fix" -->

<!-- kit:begin id="mio-trait-notes" at="section:trait-properties-explained" -->
Checks of the trait table against the documentation and the 1,279 `trait`, `add_trait` and `override_trait` blocks in vanilla.

- Names and icons follow the same fallback chains as the MIO: a trait without `name` uses the key `<MIO token>_<trait token>`, preferring a `<TAG>_` prefixed version, and a trait without `icon` tries `GFX_<TAG>_<MIO token>_<trait token>`, `GFX_<MIO token>_<trait token>` and then `GFX_idea_unknown`. [docs] `organizations/_documentation.md`. 556 of 557 vanilla `add_trait` blocks set `name` explicitly. [vanilla-confirmed 1.19.4.1] `organizations/`.
- `parent` takes `traits = { ... }` and `num_parents_needed`, which defaults to 1. `any_parent` is the shorthand for 1 and `all_parents` the shorthand for "all of them". A trait that is not first in the tree needs at least one of the three. [docs] `organizations/_documentation.md`. Vanilla uses `all_parents` and `any_parent` throughout and writes `parent` in only 2 of the 1,279 blocks. [vanilla-confirmed 1.19.4.1] `organizations/`.
- `mutually_exclusive` must be written on every trait of the set, otherwise the player can take the excluded one second. [docs] `organizations/_documentation.md`.
- `position` is the absolute grid cell, with x=0 y=0 at the top left, unless `relative_position_id` is set, and then it is an offset from that trait. Two traits must not share a cell in one tree. [docs] `organizations/_documentation.md`. Vanilla absolute `y` runs 0 to 4, relative offsets run from -5 to 7, and values may be script constants, as in `position = { x=@tank_hoesch_X y=@tank_hoesch_Y }`. [vanilla-confirmed 1.19.4.1] `organizations/GER_organization.txt`.
- `visible` and `available` default to `always = yes`, run in MIO scope with `FROM` as the country, and the AI and script treat a trait as enabled only when both hold. [docs] `organizations/_documentation.md`.
- `on_complete` runs in MIO scope with `FROM` as the country, so country effects go inside `FROM = { ... }`: `GER_mio_trait_hoesch_facilities` sets a country flag this way. [vanilla-confirmed 1.19.3] `organizations/GER_organization.txt`.
- `limit_to_equipment_type` may only narrow the MIO's own `equipment_type` list, and equipment groups work there too. [docs] `organizations/_documentation.md`.
- `ai_will_do` on a trait overrides the weights of a "central tree" trait. [docs] `organizations/_documentation.md`. 201 vanilla trait blocks write it: 197 contain only `base` (190 of them `base = 2`) and 4 add a `modifier` block, which also has `base = 2`. [vanilla-confirmed 1.19.4.1] `organizations/`.
- 46 vanilla `trait` blocks in six Delta MIOs (`BEL_cockerill_shipyards_organization` and its `_no_wuw` twin, `NOR_akers_mekaniske_verksted_organization`, `PHI_compania_maritima_de_cebu_organization`, and one block each in two `CHI_` MIOs) repeat the token of an inherited trait and write no `position`, only `limit_to_equipment_type`. The documentation prescribes `override_trait` for changing an inherited trait and says nothing about this form. [vanilla-confirmed 1.19.4.1] `organizations/BEL_organization.txt`. Whether it replaces the inherited trait or adds a second one is not stated. [unverified]
<!-- kit:end id="mio-trait-notes" -->

<!-- kit:begin id="mio-delta" at="section:delta-mio" -->
The wiki leaves this section as "TODO: Write". A Delta MIO is an MIO that names another MIO with `include` and then changes parts of it. In 1.19.4.1 the mechanism is documented and heavily used: 517 of the 553 vanilla definitions use `include`. [docs] `common/military_industrial_organization/organizations/_documentation.md`. [vanilla-confirmed 1.19.4.1] `common/military_industrial_organization/organizations/`.

| Key | Effect |
| --- | --- |
| `include = <MIO token>` | Reuses every part of the named MIO. The included MIO only has to exist somewhere in `organizations/`; there is no load order requirement. |
| any MIO-level key | Written in the including MIO, it replaces the inherited value (`allowed`, `icon`, `research_bonus`, `equipment_type`, `tree_header_text`, and so on). |
| `delete_included_values = { name initial_trait ... }` | Resets the listed MIO-level parameters to their default or empty value. Every MIO-level parameter except the trait keys is eligible. |
| `initial_trait = { ... }` | Normal initial trait keys; only what is written overrides, the rest stays inherited. |
| `add_trait = { ... }` | Adds a trait to the inherited tree, with the normal trait keys. |
| `remove_trait = { <trait token> }` | Removes an inherited trait. |
| `override_trait = { token = <trait token> ... }` | Changes only the listed keys of an inherited trait; `delete_included_values = { ... }` inside it resets the listed trait keys to default. |

All rows: [docs] `common/military_industrial_organization/organizations/_documentation.md`. The documentation warns that when the included and the including MIO sit in two different files, both files must be saved to hot-reload the result. [docs] `common/military_industrial_organization/organizations/_documentation.md`.

Vanilla patterns, all [vanilla-confirmed 1.19.4.1] in `common/military_industrial_organization/organizations/` unless a file is named:

- The `include` targets are the 30 archetypes of `00_generic_organization.txt` (`generic_infantry_equipment_organization` 50 times, `generic_motorized_mechanized_organization` 42, `generic_artillery_organization` 40, and so on) plus `CZE_tank_destroyer_organization`, `CZE_automatic_weapons_equipment_organization` and the test MIO `my_custom_mio`. No definition includes one that itself uses `include`.
- 23 of the 30 archetypes carry `allowed = { always = no }` (for example `generic_helicopter_organization`, which is also gated by `has_dlc = "Gotterdammerung"`), so they exist only to be included. A Delta MIO therefore writes its own `allowed`; 516 of the 517 do, and the exception, `my_mio_with_include` in `mio.txt`, inherits `always = no`.
- Counts of the trait operations in vanilla: `add_trait` 557, `override_trait` 180, `remove_trait` 7, `delete_included_values` 0. 141 of the 180 `override_trait` blocks set `position`, which is how `GER_porsche_organization` moves `generic_mio_trait_wide_tracks`. [vanilla-confirmed 1.19.4.1] `organizations/*.txt`, counted at MIO level. The `override_trait` example in the documentation also shows `is_available = { ... }`. The trait key is `available` [docs] `organizations/_documentation.md`, and no vanilla file writes `is_available` [vanilla-confirmed 1.19.4.1] (0 uses under `organizations/`). The engine does not accept `is_available`: inside `override_trait` it was rejected at load as "Unexpected token: is_available", and the trait stayed available (`is_mio_trait_available` TRUE), while `available = { always = no }` worked and made it unavailable. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read and `is_mio_trait_available` read in game.log. The game's own `organizations/_documentation.md` uses `is_available` in its `override_trait` example, so that example is wrong. The trait was read with the trigger, not on the screen.

**DLC gating as vanilla does it.** `has_dlc` appears 712 times in `organizations/*.txt`, naming 16 DLCs. The patterns, all [vanilla-confirmed 1.19.4.1] in `common/military_industrial_organization/organizations/` unless a file is named:

1. A country MIO that needs a DLC puts `has_dlc = "..."` beside the tag check in `allowed`: `AFG_tanks_organization` uses `has_dlc = "Graveyard of Empires"` and `tag = AFG`.
2. A twin without the DLC: `SPR_secn_vanilla_organization` includes `generic_task_force_ship_organization` with `NOT = { has_dlc = "La Resistance" }`, while `SPR_secn_organization` includes `generic_battle_line_ship_organization` with `has_dlc = "La Resistance"`. Both are in `SPR_organization.txt`.
3. An archetype that countries with a bespoke MIO must not also get: `generic_tank_organization` carries 12 `NOT = { AND = { ... has_dlc = "..." } }` blocks, each naming one or two DLCs (13 `has_dlc` checks in all). See `00_generic_organization.txt`.
4. A scripted trigger as shorthand: `NOR_AAT = yes` stands for `original_tag = NOR` plus `has_dlc = "Arms Against Tyranny"`. See `common/scripted_triggers/NOR_scripted_triggers.txt`; `GER_porsche_organization` and the policy `mio_policy_NOR_general_permanent_industrial_revolution` use it.
5. Debug copies in `00_DEBUG_organization.txt` combine `has_dlc = "Arms Against Tyranny"` with `is_debug = yes` and show only when the country has the flag `mio_show_all_archetypes_flag` (`visible`).
6. Foreign MIOs let other countries use a national MIO; `available` then checks the owner, for example `FROM = { NOT = { has_war_with = GER } }` for non-German users of `GER_porsche_organization`.

Example in vanilla style, shortened from `GER_porsche_organization` (not an exact excerpt; every key in it is used by that vanilla definition):

```text
GER_porsche_organization = {
	include = generic_heavy_tank_organization
	icon = GFX_idea_porsche
	allowed = { original_tag = GER }
	override_trait = {
		token = generic_mio_trait_wide_tracks
		position = { x=0 y=0 }
	}
	add_trait = {
		token = GER_mio_trait_hoesch_facilities
		name = GER_mio_trait_hoesch_facilities
		icon = GFX_generic_mio_trait_icon_production_capacity
		special_trait_background = yes
		position = { x=9 y=0 }
		production_bonus = { production_capacity_factor = 0.05 }
	}
}
```

Keys of the example: [vanilla-confirmed 1.19.3] `common/military_industrial_organization/organizations/GER_organization.txt`.
<!-- kit:end id="mio-delta" -->

<!-- kit:begin id="mio-policies-notes" at="section:policies" -->
Checks of the policy table against `policies/_documentation.md` and the 22 vanilla policies.

- Each MIO can have one policy attached at a time, and the policy gives bonuses only to the equipment variant or production line the MIO is assigned to. [docs] `common/military_industrial_organization/policies/_documentation.md`.
- `allowed`, `visible`, `available`, `on_add`, `on_remove` and `ai_will_do` all run in MIO scope. `allowed` is evaluated once at game start for every MIO, and a false result removes the policy from that MIO for the rest of the game. The `name` key may be scripted localisation, with the country that owns the policy as scope. [docs] `common/military_industrial_organization/policies/_documentation.md`. To reach the country from a policy trigger, vanilla uses `owner`: `mio_policy_NOR_general_permanent_industrial_revolution` writes `allowed = { owner = { NOR_AAT = yes } }`. [vanilla-confirmed 1.19.3] `common/military_industrial_organization/policies/_general_policies.txt`.
- The defaults in the table are right: `cost` falls back to `DEFAULT_INITIAL_POLICY_ATTACH_COST` (25) and `cooldown` to `DEFAULT_INITIAL_ATTACH_POLICY_COOLDOWN` (180 days). [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.
- In a policy, `equipment_bonus` and `production_bonus` are keyed by an equipment group, category, archetype or type, or by `same_as_mio`, which means all equipment of the attached MIO. [docs] `common/military_industrial_organization/policies/_documentation.md`. 17 of the 24 keyed blocks in vanilla policies use `same_as_mio`; the others name `mio_cat_eq_all_medium_plane`, `large_plane_airframe`, `large_plane_maritime_patrol_plane_airframe`, `heavy_tank_chassis`, `train_equipment`, `railway_gun_equipment` and `ship_hull_carrier`. [vanilla-confirmed 1.19.3] `common/military_industrial_organization/policies/`.
- Vanilla policies write only `icon`, `allowed`, `available`, `equipment_bonus`, `production_bonus` and `organization_modifier`. None writes `name`, `cost`, `cooldown`, `visible`, `on_add`, `on_remove` or `ai_will_do`. The usual gate is `available = { has_mio_size > 5 }`, so a policy opens at MIO size 6; `mio_policy_RAJ_general_ordnance_factory_board` uses `> 7`. [vanilla-confirmed 1.19.3] `common/military_industrial_organization/policies/`. The policy name is its token, localised in `military_industrial_organization_l_english.yml` (`mio_policy_general_ruthless_contracts: "Ruthless Contracts"`). [vanilla-confirmed 1.19.4.1] `localisation/english/military_industrial_organization_l_english.yml`.
- `mio_policy_land_heavy_gantry_cranes` puts the production stat `production_efficiency_cap_factor` inside `equipment_bonus`, for `heavy_tank_chassis`, `train_equipment` and `railway_gun_equipment`. Whether that applies the bonus to the production line is not documented, so prefer `production_bonus` for production stats. [unverified]
- Policy cost and cooldown can be changed from script and by modifiers. The country effects `add_mio_policy_cost`, `set_mio_policy_cost`, `add_mio_policy_cooldown` and `set_mio_policy_cooldown` take `policy = <token>` and `value = <number>`; `unlock_mio_policy_tooltip` shows an unlock line; `has_mio_policy` and `has_mio_policy_active` test a policy in MIO scope. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`. The country modifiers `military_industrial_organization_policy_cost` and `military_industrial_organization_policy_cooldown` exist in the `war_production` category. [docs] `documentation/modifiers_documentation.md`. Vanilla uses the cost one once, with -0.75, in `common/country_leader/00_traits.txt`. [vanilla-confirmed 1.19.4.1] `common/country_leader/00_traits.txt`.

Vanilla policy, unchanged apart from spacing:

```text
mio_policy_general_ruthless_contracts = {
	icon = GFX_mio_policy_ruthless_contracts
	allowed = { always = yes }
	available = { has_mio_size > 5 }
	organization_modifier = {
		military_industrial_organization_funds_gain = 0.1
	}
}
```

Source of the example: [vanilla-confirmed 1.19.3] `common/military_industrial_organization/policies/_general_policies.txt`.
<!-- kit:end id="mio-policies-notes" -->

<!-- kit:begin id="mio-ai-weights" at="section:ai-bonus-weights" -->
The wiki leaves this section as "TODO: Write". The folder `common/military_industrial_organization/ai_bonus_weights/` holds numbers that say how much each trait bonus attracts the AI when it picks traits.

- Format: top-level blocks named after an equipment archetype, each listing `<bonus> = <weight>` pairs, plus one block named `default`. A bigger bonus value pulls the AI harder, and a bigger weight scales that pull. [docs] `common/military_industrial_organization/ai_bonus_weights/_documentation.md`.
- Lookup: the archetype's own weight is used if it exists, otherwise the `default` weight; if neither exists the game logs an error. Every bonus that any MIO uses should therefore have at least a `default` entry. [docs] `common/military_industrial_organization/ai_bonus_weights/_documentation.md`.
- Vanilla content: three archetype blocks, `small_plane_airframe` (`air_attack = 8`, `air_agility = 10`), `small_plane_cas_airframe` (`air_ground_attack = 5`) and `medium_plane_airframe` (`air_ground_attack = 10`), and a `default` block with 85 entries. The entries cover equipment stats (`armor_value = 5`, `breakthrough = 5`, `build_cost_ic = 3.85`, `reliability = 0.5`, `soft_attack = 2.5`), production bonuses (`production_capacity_factor = 10`, `production_cost_factor = 10`, `production_efficiency_cap_factor = 10`, `production_efficiency_gain_factor = 1`, `production_resource_need_factor = 0.9`, `production_resource_penalty_factor = 0.8`, `production_conversion_speed_factor = 1`) and all seven organisation modifiers (each 1). [vanilla-confirmed 1.19.3] `common/military_industrial_organization/ai_bonus_weights/ai_bonus_weights.txt`.
- Every bonus key written in the vanilla traits and policies has a `default` entry (checked over all 55 organisation files and the 22 policies); 25 default entries are not used by any vanilla trait or policy, among them `entrenchment`, `fuel_capacity`, `thrust`, `weight` and `recon`. [vanilla-confirmed 1.19.4.1] `common/military_industrial_organization/`.
- A mod that uses a stat in a trait bonus that the `default` block lacks gets the logged error described above. [docs] To change a weight, copy the whole `default` block into a file of your own in the mod's `ai_bonus_weights/` folder and edit it, so every key keeps a value. The game does not merge several files in that folder: a second file that defined `default` was rejected at load as "Duplicate database id default". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read. No missing-weight line followed in 35 game days, and which `default` the AI used afterwards was not shown. Blocks with other ids in an extra file were not tested.
- The documentation example uses `infantry_equipment` as the archetype key. [docs] Vanilla uses airframe archetypes only (3 of 3 non-default blocks). [vanilla-confirmed 1.19.4.1] Whether a category or equipment group is accepted as a key is not documented. [unverified]
- Other AI levers for MIOs: the MIO-level `ai_will_do` multiplier, the trait-level `ai_will_do` (see the trait notes above), and the policy `ai_will_do`, which sets how likely the AI is to spend political power on that policy. [docs] `common/military_industrial_organization/organizations/_documentation.md`, `common/military_industrial_organization/policies/_documentation.md`.
- Defines that shape the AI choice, all in `common/defines/00_defines.lua`: `INDUSTRIAL_ORG_TRAIT_UNLOCK_RANDOMNESS`, `INDUSTRIAL_ORG_POLICY_CHANGE_RANDOMNESS`, `INDUSTRIAL_ORG_RESEARCH_ASSIGN_RANDOMNESS` and `INDUSTRIAL_ORG_PRODUCTION_ASSIGN_RANDOMNESS` (each 3, the AI picks at random among that many top choices), `INDUSTRIAL_ORG_POLICY_CHANGE_SCALE` (1.0), `INDUSTRIAL_ORG_TRAIT_RANK_FACTOR` (0.80, traits deeper in the tree count less by this factor) and `INDUSTRIAL_ORG_RESEARCH_BONUS_FACTOR` (10.0, applied to the research bonus when the AI judges design teams). [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. See [Defines](defines.md).

The exact scoring formula is not documented.

Shape of the file, shortened from the vanilla file (three of the 85 `default` entries):

```text
small_plane_airframe = {
	air_attack = 8
	air_agility = 10
}

default = {
	armor_value = 5
	production_capacity_factor = 10
	military_industrial_organization_research_bonus = 1
}
```

Values: [vanilla-confirmed 1.19.3] `common/military_industrial_organization/ai_bonus_weights/ai_bonus_weights.txt`.
<!-- kit:end id="mio-ai-weights" -->

<!-- kit:begin id="mio-equipment-stats" at="section:equipment-boni" -->
`naval_supremacy_factor` in the Ships table is not a stat in 1.19.4.1. The documentation lists `naval_dominance_factor`, and `naval_supremacy_factor` appears nowhere under `common/`. [docs] `common/military_industrial_organization/organizations/_documentation.md`. [vanilla-confirmed 1.19.4.1] 0 files under `common/` contain `naval_supremacy_factor`. No vanilla trait uses `naval_dominance_factor` either; it appears in the documentation and in comments only. [vanilla-confirmed 1.19.4.1] `common/military_industrial_organization/organizations/00_generic_organization.txt`. The string `naval_dominance_factor` is present in `hoi4.exe`, which fits a real but unused stat. [unverified] The documented name was not accepted in a test either: in the `equipment_bonus` of an `initial_trait` of a `screen_ship` organisation, `naval_dominance_factor` was rejected at load as "Unexpected token: naval_dominance_factor", the same error `naval_supremacy_factor` and a made-up stat got, and all three organisations still existed. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read at load. The test organisation had no `limit_to_equipment_type`. The stat might need a capital-ship organisation or a trait other than `initial_trait`, and the tooltip was not read.

The Tanks list above is incomplete. The documentation also lists `soft_attack`, `hard_attack`, `ap_attack`, `air_attack`, `fuel_consumption` and `hardness` for tanks. It marks `entrenchment` as needing the NSB DLC and the `dozer_blade` module, and `fuel_capacity` as needing NSB and the `expanded_fuel_tank` module. [docs] `common/military_industrial_organization/organizations/_documentation.md`.

Stats the documentation lists for the other equipment classes. All rows: [docs] `common/military_industrial_organization/organizations/_documentation.md`.

| Equipment class | Stats |
| --- | --- |
| Infantry equipment | `reliability`, `maximum_speed`, `defense`, `breakthrough`, `soft_attack`, `hard_attack`, `ap_attack`, `build_cost_ic` (`hardness`, `armor_value` and `air_attack` exist but are 0 and not shown) |
| Support equipment | `reliability`, `build_cost_ic` |
| Artillery, anti-air, anti-tank, rocket artillery, motorized rocket | `reliability`, `defense`, `breakthrough`, `hardness`, `armor_value`, `soft_attack`, `hard_attack`, `ap_attack`, `air_attack`, `build_cost_ic` |
| Motorized | `maximum_speed`, `reliability`, `hardness`, `breakthrough`, `build_cost_ic`, `fuel_consumption` |
| Mechanized, amphibious mechanized | `maximum_speed`, `reliability`, `defense`, `breakthrough`, `hardness`, `armor_value`, `ap_attack`, `air_attack`, `build_cost_ic`, `fuel_consumption` |
| Armored car | `maximum_speed`, `reliability`, `defense`, `breakthrough`, `hardness`, `armor_value`, `soft_attack`, `hard_attack`, `ap_attack`, `air_attack`, `build_cost_ic`, `fuel_consumption` |
| Train | `armor_value`, `build_cost_ic`, `air_attack` |
| Railway gun | `reliability`, `maximum_speed`, `railway_gun_attack`, `build_cost_ic` |

The same file marks several ship and plane stats as conditional. For planes, `thrust`, `weight` and `night_penalty` need the BBA DLC, and `mines_planting` and `mines_sweeping` need MtG and BBA. For ships, many combat stats (`lg_attack`, `hg_attack`, `torpedo_attack`, `sub_attack`, `anti_air_attack`, `armor_value`, `sub_detection` and others) need modules that carry a base value, and `mines_sweeping` and `mines_planting` need MtG. A bonus on a stat the equipment has no base value for gives nothing unless a module adds it. [docs] `common/military_industrial_organization/organizations/_documentation.md`.

Three stats appear in vanilla `equipment_bonus` blocks but not in the documentation lists: `patrol_coordination`, `fuel_consumption_factor` and `naval_weather_penalty_factor`. All three have an entry in the AI `default` weights. [vanilla-confirmed 1.19.4.1] `common/military_industrial_organization/organizations/`, `common/military_industrial_organization/ai_bonus_weights/ai_bonus_weights.txt`.
<!-- kit:end id="mio-equipment-stats" -->

<!-- kit:begin id="mio-production-notes" at="section:production-boni" -->
The sign matters. The example `production_cost_factor = 0.05` in the table above would make the line more expensive. Savings are negative values: the documentation example is `production_cost_factor = -0.1`, and 83 of the 93 plain numeric vanilla uses are negative, the 10 positive ones being the price of a trade-off trait. The same holds for `production_resource_need_factor` (38 of 41 negative) and `production_resource_penalty_factor` (27 of 28 negative). `production_efficiency_cap_factor`, `production_efficiency_gain_factor`, `production_capacity_factor` and `production_conversion_speed_factor` are positive when they help. [docs] `common/military_industrial_organization/organizations/_documentation.md`. [vanilla-confirmed 1.19.4.1] `common/military_industrial_organization/organizations/`.

All seven production keys in the table are valid, and vanilla traits use all seven (`production_capacity_factor` 185 times, `production_cost_factor` 114, `production_efficiency_cap_factor` 66, `production_efficiency_gain_factor` 73, `production_resource_need_factor` 41, `production_resource_penalty_factor` 28, `production_conversion_speed_factor` 11). [vanilla-confirmed 1.19.4.1] `common/military_industrial_organization/organizations/`. A trait's `production_bonus` applies when the MIO is assigned to a production line; in a policy it is keyed by equipment type instead. [docs] `common/military_industrial_organization/organizations/_documentation.md`, `common/military_industrial_organization/policies/_documentation.md`.
<!-- kit:end id="mio-production-notes" -->

<!-- kit:begin id="mio-org-notes" at="section:organization-boni" -->
The seven keys in the table are exactly the organisation modifiers the documentation allows in `organization_modifier`, in a trait or a policy. [docs] `common/military_industrial_organization/organizations/_documentation.md`. Vanilla trait counts: `military_industrial_organization_research_bonus` 122, `military_industrial_organization_funds_gain` 29, `military_industrial_organization_design_team_assign_cost` 11, `military_industrial_organization_size_up_requirement` 3, `military_industrial_organization_design_team_change_cost` 2, `military_industrial_organization_industrial_manufacturer_assign_cost` 1, `military_industrial_organization_task_capacity` 2 (both in the test file `mio.txt`, with values -50 and -49). [vanilla-confirmed 1.19.4.1] `common/military_industrial_organization/organizations/`.

The design team assign cost and the industrial manufacturer assign cost are daily political power costs, and the design team change cost is an experience cost for changing the MIO in the equipment designer. [docs] `documentation/effects_documentation.md` (`add_mio_design_team_assign_cost`, `add_mio_design_team_change_cost`, `add_mio_industrial_manufacturer_assign_cost`).

Defines that set the base numbers behind funds, size and assignment. All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. See [Defines](defines.md).

| Define | Value | Meaning in the define comment |
| --- | --- | --- |
| `FUNDS_FOR_SIZE_UP` | 700 | funds an MIO needs to grow one size and earn trait points |
| `FUNDS_FOR_SIZE_UP_LEVEL_FACTOR` | 100 | how much each level multiplies that requirement |
| `FUNDS_FOR_SIZE_UP_LEVEL_POW` | 1.8 | the power applied to the MIO size when computing the requirement |
| `UNLOCKED_TRAITS_PER_SIZE_UP` | 1 | trait points gained per size |
| `FUNDS_FOR_RESEARCH_COMPLETION_PER_RESEARCH_COST` | 500 | funds added when a design team finishes research, times the technology's research cost |
| `FUNDS_FOR_CREATING_EQUIPMENT_VARIANT` | 0 | funds added when a variant is created with the design team assigned |
| `FUNDS_FROM_MANUFACTURER_PER_IC_PER_DAY` | 0.1 | funds per day in proportion to output while a manufacturer is attached to a production line |
| `MAX_FUNDS_FROM_MANUFACTURER_PER_DAY` | 100 | cap per manufacturer per day, 0 for no cap |
| `ASSIGN_DESIGN_TEAM_PP_COST_PER_DAY` | 0.1 | daily political power cost of one MIO on a research slot, 0 disables it |
| `ASSIGN_INDUSTRIAL_MANUFACTURER_PP_COST_PER_DAY` | 0.0 | the same for a production line |
| `ENABLE_TASK_CAPACITY` | false | enables limited task capacity |
| `DEFAULT_INITIAL_TASK_CAPACITY` | 0 | default `task_capacity` of an MIO |

The script effect `complete_mio_trait` ignores the state of the tree and adds one size, so that size and unlocked traits stay aligned. [docs] `documentation/effects_documentation.md`.
<!-- kit:end id="mio-org-notes" -->

<!-- kit:begin id="mio-runtime-script" at="bottom" -->
## Scripting MIOs at runtime

The MIO scope is entered with `mio:<token> = { ... }`, from a variable (`var:my_mio_var`), or by iterating from a country with `every_military_industrial_organization`, `random_military_industrial_organization`, `any_military_industrial_organization` and `all_military_industrial_organization`. The iterators accept `tooltip`, skip invisible MIOs unless `include_invisible = yes` is given, and the effect iterators also take `random_select_amount` and `display_individual_scopes`. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`. Vanilla enters an MIO this way: `common/characters/GER.txt` contains `mio:GER_porsche_organization = { ... }`. [vanilla-confirmed 1.19.4.1] `common/characters/GER.txt`. See [Effects](effects.md) and [Triggers](triggers.md) for the full texts.

All rows below: [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`.

| Group | Names (MIO scope unless noted) |
| --- | --- |
| Funds and size | `add_mio_funds`, `set_mio_funds`, `add_mio_size`, `add_mio_funds_gain_factor`, `set_mio_funds_gain_factor`, `add_mio_size_up_requirement_factor`, `set_mio_size_up_requirement_factor` |
| Research and tasks | `add_mio_research_bonus`, `set_mio_research_bonus`, `add_mio_task_capacity`, `set_mio_task_capacity` |
| Assignment costs | `add_mio_design_team_assign_cost`, `set_mio_design_team_assign_cost`, `add_mio_design_team_change_cost`, `set_mio_design_team_change_cost`, `add_mio_industrial_manufacturer_assign_cost`, `set_mio_industrial_manufacturer_assign_cost` |
| Traits | `complete_mio_trait` (accepts `show_modifiers = no`), `unlock_mio_trait_tooltip` |
| Flags | `set_mio_flag` (with `value` and `days`), `clr_mio_flag`, `modify_mio_flag` |
| Look | `set_mio_icon`, `set_mio_name_key` |
| Country scope | `show_mio_tooltip`, `unlock_military_industrial_organization_tooltip`, `add_mio_policy_cost`, `set_mio_policy_cost`, `add_mio_policy_cooldown`, `set_mio_policy_cooldown` |
| Any scope | `unlock_mio_policy_tooltip` |
| Triggers | `has_mio_size`, `has_mio_trait`, `is_mio_trait_completed`, `is_mio_trait_available`, `has_mio_number_of_completed_traits`, `has_mio_policy`, `has_mio_policy_active`, `has_mio_equipment_type`, `has_mio_research_category`, `has_mio_flag`, `is_mio_assigned_to_task`, `is_mio_available`, `is_mio_visible`, `is_military_industrial_organization` |
| Country triggers | `has_military_industrial_organization` |

Behaviours worth knowing. `add_mio_funds` that pushes funds over the size-up limit grows the MIO, and a negative total is capped at 0 without shrinking it. The `add_mio_*` cost and bonus effects change the base value and modifiers still apply on top; a final value below 0 is capped at 0 without an error. `add_mio_design_team_change_cost` rounds the result down. `is_mio_trait_available` also checks the parent and mutual exclusion rules unless `check_mio_parent_completed = no` or `check_mio_mutually_exclusive = no` is given. `is_mio_available` is true only when both `visible` and `available` hold. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`.
<!-- kit:end id="mio-runtime-script" -->
