# Technology modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="104524" sources="common/technologies/ common/technology_tags/00_technology.txt common/technology_sharing/ interface/countrytechtreeview.gui interface/countrytechtreeview.gfx common/defines/00_defines.lua documentation/effects_documentation.md documentation/triggers_documentation.md common/doctrines/ hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against all 552 technologies in the 13 vanilla files of `common/technologies/`, `common/technology_tags/00_technology.txt` (16 folders, 133 categories), the 90 technology sharing groups, the 118 `gridboxtype` blocks of `interface/countrytechtreeview.gui`, `NDefines.NTechnology`, the technology effects and triggers in the documentation, and tokens in `hoi4.exe`. The "to be added" marker the inventory flagged is only the phrase "need to be added" in the Folders section and needs no action.
Kit blocks added: `tech-triggers-note`, `tech-effects-triggers`, `tech-enabling-note`, `tech-cost-note`, `tech-grid-box`, `tech-categories`, `tech-xp-note`, `tech-doctrines-warning` (doctrines are no longer technologies), `tech-keys-extra`, `tech-folders`, `tech-sharing-extra`.
Gaps left: whether the engine accepts the `ledger` values `military` and `all` (no vanilla folder uses them), the AI category rule and the `on_research_complete` behaviour for history-file technologies are repeated from the wiki and not confirmed; the GUI sections were checked for names and counts only.
**1.19.4.1 re-check (2026-11-01).** 16 statements depended on files the update changed (five files in `common/technologies/`, `00_technology.txt` in `common/technology_tags/`, `countrytechtreeview.gui`, and the folders behind the `add_tech_bonus` counts), and all 16 were re-measured: the 552 technologies, 133 categories, 16 folders, the enabling and layout key counts and the folder membership are unchanged. Changed: `countrytechtreeview.gui` holds 117 `gridboxtype` blocks (was 118), of which 62 are branch grids with 59 distinct names (was 63 and 60), and `add_tech_bonus` is now counted outside comments as 1946 blocks, 2155 `category` lines, 187 `technology` lines and 90 distinct categories (the old totals 1966, 2156, 189 and 91 could not be reproduced). Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="tech-triggers-note" at="section:triggers" -->
Vanilla use of the two trigger blocks: `allow` appears in 132 of 552 technologies and `allow_branch` in 47. All 47 `allow_branch` blocks are DLC gates (`has_dlc` in 38, `NOT = { has_dlc = ... }` in 9), so in practice it is the "branch exists only with this DLC" switch. The wiki's last sentence for `allow_branch` (that the AI cannot select the technology when it is met) is not supported by anything in vanilla. [vanilla-confirmed 1.19.4.1] `common/technologies/*.txt`; the AI sentence [unverified]
<!-- kit:end id="tech-triggers-note" -->

<!-- kit:begin id="tech-effects-triggers" at="section:effects" -->
### Technology effects and triggers

`on_research_complete_limit` is the supported form: `hoi4.exe` holds the message "limit inside on_research_complete is deprecated, use on_research_complete_limit outside of on_research_complete instead". Vanilla has 107 technologies with `on_research_complete` and 12 with `on_research_complete_limit`. [vanilla-confirmed 1.19.4.1] `common/technologies/*.txt`. The message is real: a test technology with a `limit` inside `on_research_complete` drew "limit inside on_research_complete is deprecated, use on_research_complete_limit outside of on_research_complete instead" at load with the file and line, and one with `on_research_complete_limit` outside the block drew none. In the old form the technology still loaded but its block was misparsed, so its `log` effect never ran. In the new form the effect block ran when the technology was set with `set_technology`. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log and game.log read. The limit used was `always = yes`, so whether it filters was not tested.

Country-scope effects and triggers about technology, from the game documentation. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`

| Name | Kind | Syntax and notes |
| --- | --- | --- |
| `set_technology` | effect | `set_technology = { <tech> = 1 popup = no }`; `popup` defaults to yes. `= 0` removes the technology. |
| `add_tech_bonus` | effect | One-use research bonus. Vanilla blocks use `name` (loc key), `bonus` (for example 0.5), `uses`, and either `category` or `technology`, plus an optional `ahead_reduction`. |
| `steal_random_tech_bonus` | effect | Random bonus in categories or folders where the target is ahead; needs at least one `category` or `folder`; keys `base_bonus`, `instant`, `dynamic`, `ahead_reduction`, `bonus`, `name`, `target`, `uses`. |
| `inherit_technology` | effect | Copies the technology state from the target country. |
| `mark_technology_tree_layout_dirty` | effect | `= yes` refreshes the hidden technologies for the scoped country. |
| `select_tech_tree_icon_origin` | effect | Makes the tree use another country's icons. |
| `add_research_slot`, `set_research_slots` | effect | Change the number of research slots. |
| `add_to_tech_sharing_group`, `remove_from_tech_sharing_group` | effect | `= <group id>`. |
| `modify_tech_sharing_bonus` | effect | `{ id = <group id> bonus = 0.2 }`. |
| `has_tech`, `can_research`, `is_researching_technology` | trigger | `= <tech>`. |
| `has_tech_bonus` | trigger | `{ technology = <tech> category = <category> }`. |
| `num_researched_technologies` | trigger | Compared with a number. |
| `amount_research_slots`, `original_research_slots` | trigger | Current and starting number of slots. |
| `is_in_tech_sharing_group`, `num_tech_sharing_groups` | trigger | Membership checks. |

`add_tech_bonus` appears in 1946 vanilla blocks outside comments: 2155 `category` lines in total, `technology` in 187, `ahead_reduction` in 177. Every one of the 90 distinct `category` values is a name from `technology_categories` (see the category list below). `mark_technology_tree_layout_dirty` and `select_tech_tree_icon_origin` are documented but not used by any vanilla file. [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`
<!-- kit:end id="tech-effects-triggers" -->

<!-- kit:begin id="tech-enabling-note" at="section:enabling-objects" -->
Vanilla use of the enabling keys across 552 technologies: `enable_equipments` 223, `enable_equipment_modules` 136, `enable_subunits` 70, `enable_building` 14 (always `building` plus `level`). `enable_tactic` appears in none of them; vanilla enables combat tactics through the `enable_tactic` line of a doctrine instead (see the [Doctrine modding](doctrine_modding.md) page), so the wiki's `enable_tactic = my_tactic` in a technology is not used in vanilla. [vanilla-confirmed 1.19.4.1] `common/technologies/*.txt`, `common/doctrines/`. It does not unlock the tactic in 1.19.4.1: a test technology with `enable_tactic = tactic_breakthrough` loaded with no error.log line, and after `set_technology` gave the technology, `has_tactic = tactic_breakthrough` still read FALSE. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log and game.log read. The technology was set, not researched, and `has_tactic` is a trigger, so no real combat was run.
<!-- kit:end id="tech-enabling-note" -->

<!-- kit:begin id="tech-cost-note" at="section:technologys-cost" -->
`NDefines.NTechnology.BASE_TECH_COST` is 110 in 1.19.3, not 100, so `research_cost = 1` is about 110 days of default research, not 100; the reference [1] at the bottom of the page is out of date for the same reason. The other cited defines still hold: `BASE_YEAR_AHEAD_PENALTY_FACTOR` 2, `MAX_SUBTECHS` 3, `MAX_TECH_SHARING_BONUS` 0.5 and `NAI.RESEARCH_DAYS_BETWEEN_WEIGHT_UPDATE` 7. Other `NTechnology` defines worth knowing: `BASE_RESEARCH_POINTS_SAVED` 30 (per slot), `LICENSE_PRODUCTION_TECH_BONUS` 0.2, `MIN_RESEARCH_SPEED` 0.1, `USE_BONUS_REGRET_TIMER` 3 days, and the three `DEFAULT_XP_*` research cost defaults (0). [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`
<!-- kit:end id="tech-cost-note" -->

<!-- kit:begin id="tech-grid-box" at="section:position" -->
### The grid box rule, verified

A technology only renders in a folder when the tree GUI has a grid box for its branch. `interface/countrytechtreeview.gui` holds 117 `gridboxtype` blocks: 62 are technology branch grids named `<first technology>_tree` (59 distinct names; `experimental_rockets_tree` is repeated in three folders and `early_ship_hull_light_tree` in two), and 55 belong to other windows (`special_project_specialization_list` 23, `stats_grid` 7, `leader_bonuses_grid` 7, `support_category_multipliers_grid` 7, `terrain_modifiers_grid` 5, `subunit_stats_grid` 4, `air_missions_grid` 2). [vanilla-confirmed 1.19.4.1] `interface/countrytechtreeview.gui`

Check against the technologies: the 59 (folder, technology) pairs where no other technology of the same folder paths to the technology (the branch roots) all have a grid box named `<tech>_tree` in the file; none is missing. Technologies that are reached by `path` use the grid box of the root they connect to. [vanilla-confirmed 1.19.4.1] `common/technologies/*.txt`, `interface/countrytechtreeview.gui`

`hoi4.exe` holds the messages that report a break in this rule: "Found no grid box for tech %s", "Found multiple potential grid boxes for tech %s (%s and %s)" (the case `ignore_for_layout = yes` on a secondary `path` avoids; vanilla uses it 3 times), "couldn't find grid box window with name %s", "Technology %s has no coordinates in folder %s for parent %s", "Mutually exclusive Technologies %s and %s have different starting points in folder %s for parent %s" and "Subtechnology %s has two parents (%s and %s), which is undefined behaviour supported". [unverified] (strings seen only in `hoi4.exe`)

A `path` block does not need `leads_to_tech`: vanilla has `path = { research_cost_coeff = 1 }` on 8 technologies (the `excavation` chain, `motorised_infantry`, `heavy_battleship2`, `NOR_rikstanken_tech`). [vanilla-confirmed 1.19.4.1] `common/technologies/industry.txt`

Tab buttons: the `folder_tabs` window has a `<folder>_tab` button for each of the 12 technology folders that vanilla fills (`industry_folder_tab` included), and item windows are named `techtree_<folder>_item` and `techtree_<folder>_small_item`. [vanilla-confirmed 1.19.4.1] `interface/countrytechtreeview.gui`
<!-- kit:end id="tech-grid-box" -->

<!-- kit:begin id="tech-categories" at="section:categories" -->
### Technology categories in 1.19.4.1

`common/technology_tags/00_technology.txt` defines 133 distinct categories in `technology_categories = { }`. The file says not to change tags without changing every reference, and that names must be unique. Vanilla technologies use 105 of them in `categories`. The `category` of `add_tech_bonus` comes from this list: `industry` and `construction_tech` are valid, `construction` and `infrastructure` are not in it, and all 90 distinct categories that vanilla passes to `add_tech_bonus` are in it. [vanilla-confirmed 1.19.4.1] `common/technology_tags/00_technology.txt`, `common/`, `history/`, `events/`

```text
light_air medium_air heavy_air armor cat_light_armor cat_medium_armor cat_heavy_armor artillery
cat_anti_tank cat_anti_air naval_air infantry_weapons motorized_equipment
cat_mechanized_equipment naval_equipment rocketry nuclear industry electronics
cat_fortification land_doctrine air_doctrine naval_doctrine strategic_destruction_tree
battlefield_support_tree operational_integrity_tree jet_technology trade_interdiction_tree
convoy_defense_tree light_fighter cat_heavy_fighter tactical_bomber cat_strategic_bomber
naval_bomber cas_bomber ship_modules_tech dd_tech ca_tech cv_tech bc_tech bb_tech shbb_tech
ss_tech tp_tech synth_resources fleet_in_being_tree encryption_tech decryption_tech
computing_tech radar_tech infantry_tech marine_tech construction_tech excavation_tech
submarine_doctrine air_equipment cat_mobile_warfare cat_superior_firepower
cat_grand_battle_plan cat_mass_assault cat_deep_battle cat_mass_mobilization cat_base_strike
cat_trade_interdiction cat_fleet_in_being cat_strategic_destruction cat_battlefield_support
cat_operational_integrity night_vision base_strike_main mot_rockets support_tech para_tech
engineers_tech recon_tech mountaineers_tech rangers_tech_cat military_police_tech hospital_tech
logistics_tech signal_company_tech maintenance_company_tech naval_mines
concentrated_industry_category dispersed_industry_category asw_tech naval_minesweeping
naval_minelaying cat_scout_plane train_tech cat_production cat_synth_rubber cat_synth_oil
cat_armored_cars cat_special_forces_generic cat_torpedoes cat_ship_light_battery
cat_ship_medium_battery cat_ship_heavy_battery plane_modules_tech cat_air_guns cat_air_engine
cat_air_bombs special_forces_doctrine cat_maritime_patrol cat_mountaineers_doctrine
cat_marines_doctrine cat_paratroopers_doctrine cat_rangers_doctrine naval_armor naval_artillery
helicopter_tech pykrete_tech transport_planes_cat mio_cat_tech_all_armor_and_modules
mio_cat_tech_light_armor_and_modules mio_cat_tech_medium_armor_and_modules
mio_cat_tech_heavy_armor_and_modules mio_cat_all_artillery_equipment
mio_cat_all_light_fighter_and_modules mio_cat_all_cas_and_modules
mio_cat_all_naval_bomber_and_modules mio_cat_all_light_aircraft_and_modules
mio_cat_all_medium_aircraft_and_modules mio_cat_all_heavy_aircraft_and_modules
mio_cat_tech_all_capital_ship_and_modules mio_cat_tech_all_screen_ship_and_modules
mio_cat_tech_all_submarine_and_modules mio_cat_tech_all_carrier_and_modules
mio_cat_tech_all_cruiser_and_modules mio_cat_tech_all_destroyer_and_modules
mio_cat_tech_all_motorized_mechanized mio_cat_artillery
```

The `mio_cat_*` entries at the end are the categories for military industrial organizations. [vanilla-confirmed 1.19.4.1] `common/technology_tags/00_technology.txt`
<!-- kit:end id="tech-categories" -->

<!-- kit:begin id="tech-xp-note" at="section:experience-costs" -->
Vanilla uses `xp_research_type` on 20 technologies, always `navy`, together with `xp_boost_cost` and `xp_research_bonus` (the Man the Guns boost). No technology sets `xp_unlock_cost`; the wiki says that form was commonly used with doctrines, which are no longer technologies. The defines `DEFAULT_XP_UNLOCK_RESEARCH_COST`, `DEFAULT_XP_BOOST_RESEARCH_COST` and `DEFAULT_XP_BOOST_RESEARCH_BONUS` default to 0. [vanilla-confirmed 1.19.4.1] `common/technologies/*.txt`, `common/defines/00_defines.lua`
<!-- kit:end id="tech-xp-note" -->

<!-- kit:begin id="tech-doctrines-warning" at="heading:doctrines" -->
Doctrines are not technologies in 1.19.4.1. None of the 552 vanilla technologies uses `doctrine = yes` or `doctrine_name`, no technology is placed in `land_doctrine_folder`, `naval_doctrine_folder`, `air_doctrine_folder` or `special_forces_doctrine_folder` (the four folders still exist in `technology_folders` with `doctrine = yes`), and the doctrine window is built from `common/doctrines/` instead. Write new doctrines as grand doctrines, tracks and subdoctrines; see the [Doctrine modding](doctrine_modding.md) page. [vanilla-confirmed 1.19.4.1] `common/technologies/*.txt`, `common/technology_tags/00_technology.txt`, `common/doctrines/`
<!-- kit:end id="tech-doctrines-warning" -->

<!-- kit:begin id="tech-keys-extra" at="section:additional" -->
### Technology keys the page omits

Keys in vanilla technologies that the page does not mention. Counts are technologies out of 552. Source: [vanilla-confirmed 1.19.4.1] `common/technologies/*.txt`, with the exe tokens as [unverified] for meaning.

| Key | Count | Notes |
| --- | --- | --- |
| `special_project_specialization` | 334 | A list such as `{ specialization_land }`; values seen: `specialization_land`, `specialization_naval`, `specialization_air`, `specialization_nuclear`. Feeds the special project system; see the [Special project modding](special_project_modding.md) page. |
| `is_special_project_tech` | 49 | `yes` on the technologies that special projects unlock. |
| `XOR` and `xor` | 5 and 2 | Both spellings occur in vanilla; the wiki uses both. |
| `dependencies` | 4 | `{ <tech> = 1 }` AND list, as the page describes. |
| `sub_tech_index` | 3 | Overrides the sub-technology slot. |
| `sub_technologies` | 23 | List of sub-technologies, at most `MAX_SUBTECHS` (3) per technology. |
| `show_effect_as_desc` | 23 | `yes` 22, `no` 1. |
| `force_use_small_tech_layout`, `show_equipment_icon` | 12, 7 | Always `yes`. |
| `ai_research_weights` | 19 | Keys seen: `offensive`, `defensive`, `rubber`, `oil`. |
| `desc` | 1 | Extra tooltip text key. |

Unit and category bonus blocks (`category_all_infantry`, `armored_car`, `destroyer`, ...) are written directly inside the technology, as the Modifiers section says; vanilla has many hundreds of them. Folder blocks use only `name` and `position`; `path` uses `leads_to_tech`, `research_cost_coeff` and `ignore_for_layout`. [vanilla-confirmed 1.19.4.1] `common/technologies/*.txt`
<!-- kit:end id="tech-keys-extra" -->

<!-- kit:begin id="tech-folders" at="section:folders" -->
### The real folder ids

`common/technology_tags/00_technology.txt` defines 16 folders. The armour folders use the British spelling, `armour_folder` and `nsb_armour_folder`; `armor_folder` does not exist. [vanilla-confirmed 1.19.4.1] `common/technology_tags/00_technology.txt`

| Folder id | `ledger` | `available` | Technologies in vanilla |
| --- | --- | --- | --- |
| `infantry_folder` | army | always | 43 |
| `support_folder` | army | always | 42 |
| `armour_folder` | army | without "No Step Back" | 18 |
| `nsb_armour_folder` | army | "No Step Back" | 28 |
| `artillery_folder` | army | always | 28 |
| `air_techs_folder` | air | without "By Blood Alone" | 34 |
| `bba_air_techs_folder` | air | "By Blood Alone" | 41 |
| `naval_folder` | navy | without "Man the Guns" | 32 |
| `mtgnavalfolder` | navy | "Man the Guns" | 38 |
| `mtgnavalsupportfolder` | navy | "Man the Guns" | 43 |
| `industry_folder` | civilian | always | 43 |
| `electronics_folder` | civilian | always | 33 |
| `land_doctrine_folder` | army | always (`doctrine = yes`) | 0 |
| `naval_doctrine_folder` | navy | always (`doctrine = yes`) | 0 |
| `air_doctrine_folder` | air | always (`doctrine = yes`) | 0 |
| `special_forces_doctrine_folder` | hidden | "Arms Against Tyranny" or "No Compromise, No Surrender" (`doctrine = yes`) | 0 |

411 technologies have a `folder` block, and 12 of them sit in more than one folder: 4 in both `armour_folder` and `nsb_armour_folder`, 4 in both air folders, 2 in `naval_folder` and `mtgnavalsupportfolder`, and one each in `electronics_folder` with `support_folder` and `infantry_folder` with `support_folder`. Base-game and DLC variants of a folder mostly hold different technology ids. Vanilla `ledger` values are `army`, `navy`, `air`, `civilian` and `hidden`; the wiki's `military` and `all` are not used by vanilla (20 `ledger` lines: army 8, navy 5, air 4, civilian 2, hidden 1). [vanilla-confirmed 1.19.4.1] `common/technologies/*.txt`, `common/technology_tags/00_technology.txt`, `common/doctrines/folders/doctrine_folders.txt`
<!-- kit:end id="tech-folders" -->

<!-- kit:begin id="tech-sharing-extra" at="section:technology-sharing-groups" -->
Vanilla defines 90 technology sharing groups in 11 files of `common/technology_sharing/`. Keys: `id`, `name`, `desc`, `picture` and `research_sharing_per_country_bonus` in all 90, `available` in 89, `categories` in 30 and `is_faction_sharing` in 1. The usual bonus is 0.1 per member and the usual picture `GFX_technology_sharing_default`. Membership is changed with `add_to_tech_sharing_group`, `remove_from_tech_sharing_group` and `modify_tech_sharing_bonus = { id = <group> bonus = 0.2 }`, and read with `is_in_tech_sharing_group` and `num_tech_sharing_groups`. `NTechnology.MAX_TECH_SHARING_BONUS` is 0.5, the cap the page cites. [vanilla-confirmed 1.19.3] `common/technology_sharing/*.txt`, `common/defines/00_defines.lua`; [docs] `documentation/effects_documentation.md`
<!-- kit:end id="tech-sharing-extra" -->
