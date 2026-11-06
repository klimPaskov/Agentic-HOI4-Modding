# List of modifiers

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="87096" sources="documentation/modifiers_documentation.md documentation/effects_documentation.md documentation/dynamic_variables_documentation.md common/dynamic_modifiers/ common/modifier_definitions/ common/modifiers/ common/units/equipment/ common/units/unit_modifiers/ common/operations/ localisation/english/modifiers_l_english.yml" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against the modifier documentation (722 plain modifiers and 38 template families), the unit modifier registry, the modifier definition and dynamic modifier files, and the in-game modifier text.
- Kit blocks added: `list-corrections` (names that do not exist in 1.19.3, a misspelt token, equipment stats that are not modifiers, short lists), `missing-from-table` (the 252 documented modifiers the table never names, in themed tables and a sub-unit grid) and `template-families`.
- Gaps left: meanings starting with `~` are guesses from names; the unused modifiers were not tested in game; the Notes column of the table was not re-checked, only the names.
**1.19.4.1 re-check (2026-11-01).** Eight statements depended on files the update changed (vanilla-wide scans, the equipment and operation files and the modifier text file), and all eight were re-measured. Two facts changed: `navy_screen_attack_factor_against` is now used in `common/ideas/japan.txt`, and the in-game text of `river_crossing_factor_against` does not end in "against a country"; the 20 "unused in vanilla" modifiers, the 72 `foreign_subversive_activites` uses and the 13 operation modifier names are unchanged, and the meaning column cannot be diffed against the old text file. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="list-corrections" at="top" -->
Rows on this page that do not match 1.19.3. The game documents 722 plain modifiers and 38 template families, and 252 of the 722 are never named in the table below; the tables at the bottom add them. [docs] `documentation/modifiers_documentation.md`

- Not found in the modifier documentation or in any vanilla script or localisation (and not in the strings of `hoi4.exe`): `occupation_cost`, `modifier_enemy_port_superiority_limit`, `paratrooper_count_per_plane`, `max_marshal_army_size`, `max_marshal_army_group_size`, and the air factor rows `air_interception_{attack,defence,agility}_factor`, `air_air_superiority_{attack,defence,agility}_factor`, `air_close_air_support_{attack,defence,agility}_factor`, `air_strategic_bomber_{attack,agility}_factor` and `air_paradrop_{attack,defence,agility}_factor`. [docs] [vanilla-confirmed 1.19.4.1] The `hoi4.exe` part is a read-only string search. [unverified] In an idea's `modifier` block, `occupation_cost` and `max_marshal_army_size` were rejected at load as "Unknown modifier", and read back by name each gave 0. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read and the modifier read in game.log. The other names in this list were not tried.
- `max_commander_army_group_size` is not documented and no script or localisation uses it. The documented names are `max_commander_army_size` and `max_army_group_size`. [docs] [vanilla-confirmed 1.19.4.1] `documentation/modifiers_documentation.md`, search of the data folders. The string appears once in `hoi4.exe`. It is not a leftover but a live modifier key: an idea with `max_commander_army_group_size = 1` loaded with no error.log line, the modifier read 1 once the idea was added, and the add tooltip showed "General Max Army Group Size". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log and game.log read. The tooltip text is from OCR of the console reply and partly garbled, and `list_modifiers` was not used.
- `foreign_subversive_activities` is misspelled. The game's token is `foreign_subversive_activites` (one "i" missing), which is what the documentation and 72 vanilla uses write. [docs] [vanilla-confirmed 1.19.4.1]
- `operation_steal_tech_cost` is not in the documented `<Operation>_cost` list. The documented names are `operation_steal_tech_army_cost`, `operation_steal_tech_navy_cost`, `operation_steal_tech_airforce_cost` and `operation_steal_tech_civilian_cost`; `operation_steal_tech_outcome` and `operation_steal_tech_risk` do exist. A localisation key `operation_steal_tech_cost` exists in `localisation/english/modifiers_l_english.yml`. [docs] [vanilla-confirmed 1.19.4.1] The old name is not recognised: in an idea's `modifier` block `operation_steal_tech_cost` was rejected at load as "Unknown modifier", and read back by name it gave 0. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read at load and the modifier read in game.log.
- `breakthrough`, `armor_value`, `air_attack`, `air_defence`, `air_agility`, `maximum_speed`, `air_range`, `air_superiority` and `air_bombing` are equipment stats, not entries of the modifier documentation. [docs] They are keys of the equipment files in `common/units/equipment/` and of equipment upgrades. [vanilla-confirmed 1.19.4.1]
- The explicit lists in some rows are shorter than the game's lists: resources (7, with `coal`), buildings (55, the page names up to 16), `production_cost_max_*` (9 tokens, the page names 6), units for `experience_gain_*` (157, and a third `_mission_factor` variant exists) and `special_forces_doctrine_cost_factor` next to the three `<land/air/naval>` doctrine cost rows. Full lists are in [Template modifier families](#template-modifier-families). [docs] `documentation/modifiers_documentation.md`
<!-- kit:end id="list-corrections" -->

<!-- kit:begin id="missing-from-table" at="bottom" -->
## Documented modifiers missing from the table

252 documented modifiers are never named in the table above. They are grouped by theme below. The sub-unit family is a grid after the groups. All rows: [docs] `documentation/modifiers_documentation.md`

- Modifier, Categories and Format come from the game documentation. `dp` is the number of decimals the tooltip shows; any value accepts up to 3 decimals. [docs] `documentation/modifiers_documentation.md`
- Meaning is the in-game wording from `localisation/english/modifiers_l_english.yml` and the MIO and effect strings, paraphrased. [vanilla-confirmed 1.19.3] The text file changed in 1.19.4.1 and the old text is gone, so a reworded single row would not show. A word-overlap check of the meaning column against the new file found no row that contradicts it. [unverified]
- A meaning that starts with `~` is a guess from the name and its vanilla use. [unverified]
- An empty meaning means the name is self-explanatory. `(not described in the docs)` means there is no in-game text and no clear vanilla use.
- "Unused in vanilla" means no `key = value` use in `common/`, `events/` or `history/`. [vanilla-confirmed 1.19.4.1]
- Sample checks against vanilla use: `army_non_core_attack_factor` is negative in `common/ideas/australia.txt`; `naval_invasion_prep_days` is -5 and -10 in `special_forces_subdoctrines.txt` and `MTG_naval_Support.txt`; `army_intel_to_others` is -15 and -50 in a trait and a decision; `peace_score_ratio_transferred_to_players` is used by the `diff_*_ai` static modifiers; `river_crossing_factor_against` sits inside `targeted_modifier` in `common/ideas/GER.txt`. [vanilla-confirmed 1.19.4.1]

### General country modifiers (8)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `energy_gain_factor` | country | 2 dp | Energy gained per unit of coal |
| `energy_scale_per_trade_factory_export_factor` | country | 2 dp | How much traded factories affect factory energy usage (unused in vanilla) |
| `factory_energy_consumption` | country | 2 dp | Energy each factory uses |
| `resource_trade_cost_bonus_per_factory` | country | 0 dp | ~ Extra resources received per factory traded; the wiki says a positive value favours the buyer |
| `special_project_facility_supply_consumption_factor` | country | 2 dp | Supply used by special project facilities |
| `special_project_speed_factor` | country | 2 dp |  |
| `thermonuclear_production` | country | bool | Allows thermonuclear bombs |
| `thermonuclear_production_factor` | country | 0 dp | Thermonuclear bomb production rate |

### Politics (9)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `air_advisor_cost_factor` | air | 0 dp |  |
| `army_advisor_cost_factor` | army | 0 dp |  |
| `disabled_ideas` | country | bool | ~ Blocks changing ideas by hand, including ministers and laws |
| `navy_advisor_cost_factor` | naval | 0 dp |  |
| `power_balance_daily` | country | 2 dp | Daily balance of power change |
| `power_balance_weekly` | country | 2 dp | Weekly balance of power change |
| `weekly_bombing_war_support` | country | 2 dp | Weekly war support change from enemy bombing |
| `weekly_casualties_war_support` | country | 2 dp | Weekly war support change from combat casualties |
| `weekly_convoys_war_support` | country | 2 dp | Weekly war support change from sunk convoys |

### Diplomacy (11)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `annex_subject_cost_factor` | country | 2 dp |  |
| `can_guarantee_other_ideologies` | country | bool | Allows guaranteeing countries of other ideologies; the same name is also a `rule` in ideas and ideologies |
| `embargo_cost_factor` | country, politics | 1 dp | Cost of sending an embargo |
| `embargo_threshold_factor` | country, politics | 1 dp | World tension a target must reach before it can be embargoed |
| `faction_influence_contribution_factor` | faction | 2 dp | Influence gained in a faction from contribution |
| `faction_influence_war_score_factor` | faction | 2 dp | Influence gained in a faction from war score |
| `faction_subject_contribution_gain` | faction | 2 dp | Reduction in contribution gain caused by being a subject |
| `lend_lease_tension_with_overlord` | country | 1 dp | ~ World tension needed before the country can lend-lease to its overlord |
| `peace_score_ratio_transferred_to_overlord` | peace | 2 dp | Share of a puppet's peace score that goes to its overlord |
| `peace_score_ratio_transferred_to_players` | peace | 2 dp | Share of AI countries' peace score that goes to human players |
| `request_lease_tension` | country | 1 dp | ~ World tension needed before the country can request lend-lease |

### Autonomy (3)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `autonomy_gain_warscore_factor` | autonomy | 2 dp | Freedom gained from war participation |
| `autonomy_manpower_share_from_subjects` | autonomy | 2 dp | Amount of manpower demanded from subject forces |
| `resources_to_overlord_factor` | autonomy | 2 dp |  |

### Governments in exile (1)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `exiled_government_weekly_manpower` | country, war_production | 0 dp | Weekly manpower from an exiled government |

### Equipment (4)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `floating_harbor_duration` | country | 0 dp |  |
| `floating_harbor_range` | country | 0 dp |  |
| `floating_harbor_supply` | country | 0 dp |  |
| `railway_gun_bombardment_factor` | country | 0 dp |  |

### Fuel and supply (7)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `naval_supply_consumption_factor` | naval, defensive, aggressive | 1 dp | Supplies our fleets need to operate |
| `supply_factor` | country, state | 0 dp | Supply efficiency |
| `supply_node_range` | country | 0 dp | Range of supply nodes |
| `truck_attrition` | country, state | 2 dp | Unused in vanilla |
| `truck_attrition_factor` | country, state | 0 dp | Attrition of supply trucks |
| `underway_replenishment_convoy_cost` | country | 2 dp | Convoys used to provide underway replenishment |
| `underway_replenishment_range` | country | 2 dp | How far underway replenishment extends fleet range |

### Buildings (10)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `cic_construction_boost` | country, war_production | 1 dp | ~ Flat bonus to base construction line speed |
| `cic_construction_boost_factor` | country, war_production | 1 dp | ~ Multiplier on the base construction line speed boost |
| `coastal_bunker_effectiveness_factor` | country, state | 0 dp |  |
| `consumer_goods_expected_value` | country, war_production | 1 dp | Expected number of factories put on consumer goods |
| `industrial_capacity_dockyard_powered` | country, war_production | 2 dp | Output of powered dockyards |
| `industrial_capacity_factory_powered` | country, war_production | 2 dp | Output of powered factories |
| `land_bunker_effectiveness_factor` | country, state | 0 dp |  |
| `out_of_power_impact_factor` | country, war_production | 2 dp | Reduces the penalties from lack of power |
| `production_speed_buildings_powered_factor` | country, war_production | 2 dp | Construction speed of powered buildings (unused in vanilla) |
| `production_speed_facility_factor` | country | 2 dp | Construction speed of all facilities |

### Intelligence (7)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `airforce_intel_to_others` | country | 1 dp | ~ Air force intel other countries get about us (negative hides us) |
| `army_intel_to_others` | country | 1 dp | ~ Army intel other countries get about us (negative hides us) |
| `civilian_intel_to_others` | country | 1 dp | ~ Civilian intel other countries get about us (negative hides us) |
| `foreign_subversive_activites` | country | 0 dp | ~ Efficiency of foreign subversive activities; the game spells it "activites" |
| `intel_from_combat_factor` | country | 2 dp | Intelligence gained from combat |
| `intelligence_operation_speed` | intelligence_agency | 0 dp | Operation speed factor (unused in vanilla) |
| `navy_intel_to_others` | country | 1 dp | ~ Navy intel other countries get about us (negative hides us) |

### Operatives (15)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `enemy_operative_capture_chance_factor` | unit_leader, country | 0 dp |  |
| `enemy_operative_detection_chance` | unit_leader, country | 2 dp | Flat offset to the chance of detecting enemy operatives |
| `enemy_operative_detection_chance_factor` | unit_leader, country | 0 dp |  |
| `enemy_operative_detection_chance_factor_over_occupied_tag` | unit_leader, country | 0 dp | ~ Detection chance factor for enemy operatives, scoped to the tag that occupies the state |
| `enemy_operative_detection_chance_over_occupied_tag` | unit_leader, country | 2 dp | ~ Flat detection offset for enemy operatives, scoped to the tag that occupies the state |
| `enemy_operative_forced_into_hiding_time_factor` | unit_leader, country | 0 dp | ~ Time enemy operatives stay in hiding (unused in vanilla) |
| `enemy_operative_harmed_time_factor` | unit_leader, country | 0 dp | ~ Time enemy operatives stay harmed (unused in vanilla) |
| `enemy_operative_intel_extraction_rate` | unit_leader, country | 0 dp | Rate at which enemy operatives extract our intel |
| `enemy_spy_negative_status_factor` | country, state | 0 dp | Marked [wip] in the in-game text; unused in vanilla |
| `own_operative_capture_chance_factor` | unit_leader, country | 0 dp |  |
| `own_operative_detection_chance` | unit_leader, country | 2 dp | Flat offset to the chance our operatives are detected |
| `own_operative_detection_chance_factor` | unit_leader, country | 0 dp |  |
| `own_operative_forced_into_hiding_time_factor` | unit_leader, country | 0 dp | ~ Time our operatives stay in hiding (unused in vanilla) |
| `own_operative_harmed_time_factor` | unit_leader, country | 0 dp | ~ Time our operatives stay harmed (unused in vanilla) |
| `own_operative_intel_extraction_rate` | unit_leader, country | 0 dp | Rate at which our operatives extract enemy intel (unused in vanilla) |

### Military outside of combat (10)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `additional_brigade_column_size` | country | 0 dp | ~ Extra unlockable slots in each brigade column of division templates |
| `air_doctrine_cost_factor` | country | 2 dp |  |
| `army_experience_from_volunteers` | army | 1 dp |  |
| `marines_special_forces_contribution_factor` | army | 0 dp | How much marines count toward the special forces cap |
| `mountaineers_special_forces_contribution_factor` | army | 0 dp | How much mountaineers count toward the special forces cap |
| `naval_doctrine_cost_factor` | country | 2 dp |  |
| `paratroopers_special_forces_contribution_factor` | army | 0 dp | How much paratroopers count toward the special forces cap |
| `rangers_special_forces_contribution_factor` | army | 0 dp | How much rangers count toward the special forces cap |
| `special_forces_cap_flat` | army | 0 dp | ~ Flat increase to the special forces cap of a template |
| `special_forces_doctrine_cost_factor` | country | 2 dp |  |

### MIOs (9)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `military_industrial_organization_design_team_assign_cost` | war_production | 0 dp | Design team assign cost |
| `military_industrial_organization_design_team_change_cost` | war_production | 0 dp | Design team change cost |
| `military_industrial_organization_funds_gain` | war_production | 0 dp | Funds gain |
| `military_industrial_organization_industrial_manufacturer_assign_cost` | war_production | 0 dp | Industrial manufacturer assign cost |
| `military_industrial_organization_policy_cooldown` | war_production | 0 dp | Policy cooldown (unused in vanilla) |
| `military_industrial_organization_policy_cost` | war_production | 0 dp | Policy cost, shown in political power |
| `military_industrial_organization_research_bonus` | war_production | 0 dp | Research bonus that MIOs give |
| `military_industrial_organization_size_up_requirement` | war_production | 0 dp | Requirement for sizing up an MIO |
| `military_industrial_organization_task_capacity` | war_production | 0 dp | Task capacity of an MIO |

### Unit leaders (10)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `assign_army_leader_cp_cost` | country, army | 0 dp | Command power cost to assign an army leader (unused in vanilla) |
| `assign_navy_leader_cp_cost` | naval, country | 0 dp | Command power cost to assign a navy leader (unused in vanilla) |
| `automatic_grant_medal_chance` | country | 0 dp | ~ Chance that a medal is granted automatically |
| `choose_preferred_tactics_cost` | country | 0 dp | ~ Cost to choose a preferred tactic |
| `command_abilities_cost_factor` | country, army | 2 dp | Cost of commander abilities |
| `female_divisional_commander_chance` | country | 0 dp | Unused in vanilla |
| `field_officer_promotion_penalty` | country | 0 dp | ~ Penalty on divisions when their commander is promoted to field marshal |
| `grant_medal_cost_factor` | country | 1 dp | Cost to grant a medal |
| `unit_leader_as_advisor_cp_cost_factor` | unit_leader, country | 1 dp | ~ Command power cost to turn a commander into an advisor |
| `unit_medal_effectiveness` | country | 0 dp | ~ Strength of the bonuses that unit medals give |

### Land combat (27)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `armor_factor` | army, defensive | 2 dp | (not described in the docs) |
| `army_attack_against_major_factor` | army, aggressive | 1 dp | Attack against major countries |
| `army_attack_against_minor_factor` | army, aggressive | 1 dp | Attack against minor countries |
| `army_attack_speed_factor` | army | 2 dp | Speed of divisions that are attacking into enemy territory |
| `army_breakthrough_against_major_factor` | army, defensive | 1 dp | Breakthrough against major countries |
| `army_breakthrough_against_minor_factor` | army, defensive | 1 dp | Breakthrough against minor countries |
| `army_claim_attack_factor` | army, aggressive | 1 dp | ~ Attack in territory the owner claims |
| `army_claim_defence_factor` | army, defensive | 1 dp | ~ Defence in territory the owner claims |
| `army_defence_against_major_factor` | army, defensive | 1 dp | Defence against major countries |
| `army_defence_against_minor_factor` | army, defensive | 1 dp | Defence against minor countries |
| `army_non_core_attack_factor` | army, aggressive | 1 dp | Division attack in non-core territory |
| `army_non_core_defence_factor` | army, defensive | 1 dp | Division defence in non-core territory |
| `army_retreat_speed_factor` | army, defensive | 2 dp | Speed of retreating divisions |
| `army_strength_factor` | army | 2 dp | ~ Strength of army units |
| `cannot_retreat_while_attacking` | army, aggressive | bool |  |
| `cannot_retreat_while_defending` | army, defensive | bool |  |
| `casualty_trickleback` | army | 2 dp | (not described in the docs) |
| `combat_entrenchment` | army, defensive | 1 dp | Entrenchment combat bonus |
| `coordination_bonus` | army, aggressive | 1 dp | Share of damage that goes to the primary target in combat (the rest is spread) |
| `initiative_factor` | unit_leader, country | 1 dp |  |
| `org_damage_multiplier` | army, defensive | 1 dp | Organisation damage taken |
| `org_loss_at_low_org_factor` | army | 2 dp | Organisation loss once organisation is below 25% |
| `planning_decay_rate_factor` | army, aggressive | 2 dp | How fast a prepared plan decays |
| `shore_bombardment_collateral_damage_factor` | country | 2 dp |  |
| `str_damage_multiplier` | army, defensive | 1 dp | Strength damage taken |
| `supply_combat_penalties_on_core_factor` | army, aggressive | 1 dp | Combat penalties from low supply on core territory |
| `war_support_reduction_on_damage` | army, defensive | 1 dp | War support lost from casualties |

### Invasions (9)

The `air_invasion_*` rows are about airborne invasions. 

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `air_invasion_division_cap` | air | 0 dp | Max divisions per airborne invasion order |
| `air_invasion_plan_cap` | country | 0 dp | Max airborne invasions that can be planned and prepared at once |
| `air_invasion_prep_days` | country | 1 dp | ~ Days needed to prepare an airborne invasion (unused in vanilla) |
| `air_invasion_preparation` | air, unit_leader | 1 dp | How quickly an airborne invasion can be prepared |
| `naval_commando_raid_distance` | naval | 0 dp | Maximum distance of naval commando raids |
| `naval_invasion_division_cap` | naval | 0 dp | Max divisions per naval invasion order |
| `naval_invasion_plan_cap` | country | 0 dp | Max naval invasions that can be planned and prepared at once |
| `naval_invasion_planning_bonus_speed` | army, aggressive | 0 dp | ~ Speed at which the planning bonus builds up while preparing a naval invasion |
| `naval_invasion_prep_days` | country | 0 dp | ~ Days needed to prepare a naval invasion (negative shortens it) |

### Naval combat (15)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `headquarters_experience_gain_factor` | naval | 2 dp | Experience gained from naval headquarters (unused in vanilla) |
| `max_organisation` | naval | 0 dp | (not described in the docs) |
| `naval_enemy_positioning_in_initial_attack` | naval, unit_leader, aggressive | 0 dp | Positioning of the defending enemy in the initial attack |
| `naval_heavy_gun_hit_chance_factor` | naval, unit_leader, aggressive | 2 dp |  |
| `naval_light_gun_hit_chance_factor` | naval, unit_leader, aggressive | 2 dp |  |
| `naval_mission_xp_factor` | naval | 3 dp | Naval mission experience (unused in vanilla) |
| `naval_night_attack` | naval, aggressive | 1 dp | Attack of all ships in night engagements |
| `naval_retreat_chance_after_initial_combat` | naval, unit_leader, defensive | 0 dp | Chance the enemy leaves combat once the initial stage has passed |
| `naval_retreat_speed_after_initial_combat` | naval, unit_leader, defensive | 0 dp | Retreat speed once the initial stage has passed |
| `naval_ship_recovery_chance` | naval | 0 dp |  |
| `naval_ship_recovery_chance_factor` | naval | 0 dp | Unused in vanilla |
| `naval_torpedo_damage_reduction_factor` | naval, unit_leader, defensive | 2 dp | Reduces damage from enemy torpedoes |
| `naval_torpedo_enemy_critical_chance_factor` | naval, unit_leader, defensive | 2 dp | Critical chance of enemy torpedoes against us |
| `night_spotting_chance` | naval | 1 dp | Spotting chance against enemy vessels at night |
| `screening_without_screens` | naval, country | 1 dp | Screening bonus when only capital ships are in the fleet |

### Carriers and their planes (3)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `air_carrier_night_penalty_reduction_factor` | air | 2 dp | ~ Reduces the night penalty of carrier air operations |
| `carrier_night_traffic` | air | 2 dp | ~ Carrier air traffic capacity at night |
| `carrier_sortie_hours_delay` | naval, unit_leader, aggressive | 0 dp | Delay, in hours, before carrier air wings can sortie again |

### Air combat (8)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `ace_effectiveness_factor` | air | 1 dp | ~ Scales how strong air aces are |
| `air_ace_bonuses_factor` | air | 0 dp | ~ Scales the bonuses that aces give |
| `air_close_air_support_org_damage_factor` | air | 0 dp | ~ Organisation damage that close air support deals to divisions |
| `air_home_defence_factor` | air | 0 dp | ~ Air defence strength when defending the home region |
| `air_manpower_requirement_factor` | air | 2 dp | ~ Manpower needed to deploy aircraft |
| `air_power_projection_factor` | air | 0 dp | ~ Scales the power projection that aircraft give |
| `air_untrained_pilots_penalty_factor` | air | 0 dp | ~ Penalty on new air wings that have untrained pilots |
| `navy_weather_penalty` | air | 2 dp | Penalty on naval operations in bad weather |

### Targeted modifiers (12)

These only work inside a `targeted_modifier = { tag = X ... }` block. The in-game text of eleven of them ends in "against a country", and `river_crossing_factor_against` reads "against country". Vanilla uses `spotting_chance_against`, `navy_capital_ship_attack_factor_against` and `navy_screen_attack_factor_against` that way in `common/ideas/japan.txt` (the first two also in `common/ideas/australia.txt`) and `river_crossing_factor_against` in `common/ideas/GER.txt`. [vanilla-confirmed 1.19.4.1]

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `amphibious_invasion_against` | naval | 1 dp | Targeted: amphibious invasion strength against one country |
| `invasion_preparation_against` | naval | 1 dp | Targeted: naval invasion preparation against one country |
| `naval_critical_score_chance_factor_against` | naval, unit_leader, aggressive | 2 dp | Targeted: naval critical score chance against one country |
| `naval_hit_chance_against` | naval | 0 dp | Targeted: naval hit chance against one country |
| `navy_capital_ship_attack_factor_against` | naval, aggressive | 2 dp | Targeted: capital ship attack against one country |
| `navy_capital_ship_defence_factor_against` | naval, defensive | 2 dp | Targeted: capital ship defence against one country |
| `navy_screen_attack_factor_against` | naval, aggressive | 2 dp | Targeted: screen ship attack against one country |
| `navy_screen_defence_factor_against` | naval, defensive | 2 dp | Targeted: screen ship defence against one country |
| `navy_submarine_attack_factor_against` | naval, aggressive | 2 dp | Targeted: submarine attack against one country |
| `navy_submarine_defence_factor_against` | naval, defensive | 2 dp | Targeted: submarine defence against one country |
| `river_crossing_factor_against` | army | 2 dp | Targeted: river crossing penalty against one country |
| `spotting_chance_against` | naval | 0 dp | Targeted: naval spotting chance against one country |

### State scope (13)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `enemy_army_speed_factor` | state, army | 2 dp | Speed of enemy divisions in the state |
| `enemy_attrition` | state, army, defensive, aggressive | 1 dp | Attrition of enemy divisions in the state |
| `enemy_intel_network_gain_factor_over_occupied_tag` | state | 0 dp | Enemy intel network strength gain |
| `enemy_local_supplies` | state, war_production | 0 dp | Local supplies available to enemy divisions in the state |
| `enemy_truck_attrition_factor` | state | 0 dp | Truck attrition of enemy divisions in the state |
| `equipment_capture_factor_for_controller` | state | 1 dp | Equipment capture ratio factor for the controller of the state |
| `equipment_capture_for_controller` | state | 1 dp | Equipment capture ratio gain for the controller of the state |
| `local_factory_energy_consumption` | state | 0 dp | Energy used by factories in the state |
| `local_factory_energy_consumption_per_infrastructure` | state | 2 dp | Factory energy requirement per point of infrastructure |
| `local_non_core_supply_impact_factor` | state | 0 dp | ~ Impact of local supplies in states the controller does not core |
| `local_resource_gain_efficiency_per_infrastructure` | state | 2 dp | Resource gain per point of infrastructure |
| `local_supply_impact_factor` | state | 0 dp | ~ Impact of the state's local supplies |
| `state_production_speed_facility_factor` | state | 2 dp | Local construction speed of facilities (unused in vanilla) |

### Unit leader scope (3)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `max_army_group_size` | unit_leader | 0 dp | ~ Army groups a field marshal can lead without penalty |
| `paratrooper_weight_factor` | unit_leader, country | 1 dp | ~ Transport space paratroopers take |
| `terrain_trait_xp_gain_factor` | naval, country, army | 2 dp | Experience gain toward terrain traits |

### Scientists scope (4)

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `female_random_scientist_chance` | country, scientist | 0 dp | Unused in vanilla |
| `scientist_breakthrough_bonus_factor` | character | 2 dp | Scientist breakthrough bonus |
| `scientist_research_bonus_factor` | character | 2 dp | Scientist research bonus |
| `scientist_xp_gain_factor` | character | 2 dp |  |


### Sub-unit modifiers (54)

Only the `modifier_army_sub_unit_*` names listed in `sub_unit_modifiers = { ... }` in `common/units/unit_modifiers/unit_modifiers.txt` exist, and the documentation names exactly these 54. Add a mod battalion's names to that block to get its modifiers. The file marks the speed and max organisation modifiers of `armored_car_recon`, `light_tank_recon` and `blackshirt_assault_battalion` "Cannot be applied to support battalions". `category_special_forces` and `category_rocket_artillery` are sub-unit categories. All 54 rows: categories `army`, format 2 dp. [vanilla-confirmed 1.19.3] [docs] `documentation/modifiers_documentation.md`

| Sub-unit token | Attack | Defence | Speed | Max organisation | Organisation recovery cap |
| --- | --- | --- | --- | --- | --- |
| `armored_car` | `modifier_army_sub_unit_armored_car_attack_factor` | `modifier_army_sub_unit_armored_car_defence_factor` | `modifier_army_sub_unit_armored_car_speed_factor` | `modifier_army_sub_unit_armored_car_max_org_factor` |  |
| `armored_car_recon` | `modifier_army_sub_unit_armored_car_recon_attack_factor` | `modifier_army_sub_unit_armored_car_recon_defence_factor` | `modifier_army_sub_unit_armored_car_recon_speed_factor` | `modifier_army_sub_unit_armored_car_recon_max_org_factor` |  |
| `blackshirt_assault_battalion` | `modifier_army_sub_unit_blackshirt_assault_battalion_attack_factor` | `modifier_army_sub_unit_blackshirt_assault_battalion_defence_factor` | `modifier_army_sub_unit_blackshirt_assault_battalion_speed_factor` | `modifier_army_sub_unit_blackshirt_assault_battalion_max_org_factor` |  |
| `camelry` | `modifier_army_sub_unit_camelry_attack_factor` | `modifier_army_sub_unit_camelry_defence_factor` | `modifier_army_sub_unit_camelry_speed_factor` |  |  |
| `category_rocket_artillery` | `modifier_army_sub_unit_category_rocket_artillery_attack_factor` |  |  |  |  |
| `category_special_forces` |  |  |  | `modifier_army_sub_unit_category_special_forces_max_org_factor` |  |
| `cavalry` | `modifier_army_sub_unit_cavalry_attack_factor` | `modifier_army_sub_unit_cavalry_defence_factor` | `modifier_army_sub_unit_cavalry_speed_factor` |  |  |
| `infantry` | `modifier_army_sub_unit_infantry_attack_factor` | `modifier_army_sub_unit_infantry_defence_factor` | `modifier_army_sub_unit_infantry_speed_factor` |  |  |
| `irregular_infantry` | `modifier_army_sub_unit_irregular_infantry_attack_factor` | `modifier_army_sub_unit_irregular_infantry_defence_factor` | `modifier_army_sub_unit_irregular_infantry_speed_factor` | `modifier_army_sub_unit_irregular_infantry_max_org_factor` |  |
| `light_tank_recon` | `modifier_army_sub_unit_light_tank_recon_attack_factor` | `modifier_army_sub_unit_light_tank_recon_defence_factor` | `modifier_army_sub_unit_light_tank_recon_speed_factor` | `modifier_army_sub_unit_light_tank_recon_max_org_factor` |  |
| `long_range_patrol_support` | `modifier_army_sub_unit_long_range_patrol_support_attack_factor` | `modifier_army_sub_unit_long_range_patrol_support_defence_factor` |  |  |  |
| `marine` | `modifier_army_sub_unit_marine_attack_factor` | `modifier_army_sub_unit_marine_defence_factor` | `modifier_army_sub_unit_marine_speed_factor` | `modifier_army_sub_unit_marine_max_org_factor` |  |
| `military_police` | `modifier_army_sub_unit_military_police_attack_factor` | `modifier_army_sub_unit_military_police_defence_factor` | `modifier_army_sub_unit_military_police_speed_factor` | `modifier_army_sub_unit_military_police_max_org_factor` |  |
| `militia` | `modifier_army_sub_unit_militia_attack_factor` | `modifier_army_sub_unit_militia_defence_factor` | `modifier_army_sub_unit_militia_speed_factor` | `modifier_army_sub_unit_militia_max_org_factor` | `modifier_army_sub_unit_militia_org_recovery_cap_factor` |
| `mountaineers` | `modifier_army_sub_unit_mountaineers_attack_factor` | `modifier_army_sub_unit_mountaineers_defence_factor` | `modifier_army_sub_unit_mountaineers_speed_factor` | `modifier_army_sub_unit_mountaineers_max_org_factor` |  |
| `paratrooper` | `modifier_army_sub_unit_paratrooper_attack_factor` | `modifier_army_sub_unit_paratrooper_defence_factor` | `modifier_army_sub_unit_paratrooper_speed_factor` | `modifier_army_sub_unit_paratrooper_max_org_factor` |  |
<!-- kit:end id="missing-from-table" -->

<!-- kit:begin id="template-families" at="bottom" -->
## Template modifier families

Each pattern stands for one modifier per slot value; the documentation lists the slot values as "modified types". The explicit rows above name only some of them. All rows: [docs] `documentation/modifiers_documentation.md`

| Pattern | Categories | Format | What fills the slot |
| --- | --- | --- | --- |
| `<Building>_max_level_terrain_limit`<br>`state_<Building>_max_level_terrain_limit` | country<br>state | 0 dp | Two forms: a building token (54 tokens, for example `bunker`) or a building plus a terrain (770 tokens, for example `bunker_hills`). |
| `production_cost_<Building>_factor`<br>`production_speed_<Building>_factor`<br>`repair_speed_<Building>_factor` | country | 2 dp | 55 building tokens, listed in the Modifiers page under [Template modifier families](modifiers.md#template-modifier-families). |
| `state_production_speed_<Building>_factor`<br>`state_repair_speed_<Building>_factor` | state | 2 dp | The same 55 building tokens. |
| `country_resource_<Resource>`<br>`country_resource_cost_<Resource>`<br>`local_resources_<Resource>_factor` | country | 0 dp | 7 resources: `aluminium`, `chromium`, `coal`, `oil`, `rubber`, `steel`, `tungsten`. |
| `state_resource_<Resource>`<br>`state_resource_cost_<Resource>`<br>`temporary_state_resource_<Resource>`<br>`state_resources_<Resource>_factor` | state | 0 dp | The same 7 resources. |
| `experience_gain_<Unit>_combat_factor`<br>`experience_gain_<Unit>_mission_factor`<br>`experience_gain_<Unit>_training_factor` | naval, country | 0 dp | 157 unit tokens: sub-units, ships and aircraft (for example `infantry`, `armored_car`, `destroyer`, `fighter`). The documentation lists three variants (combat, mission, training); the wiki tables name only combat and training. |
| `unit_<Unit>_design_cost_factor` | naval, country, army | 2 dp | The same 157 unit tokens. |
| `<Equipment>_design_cost_factor` | country | 0 dp | 195 equipment, chassis and airframe tokens (for example `infantry_equipment`, `light_tank_chassis`, `medium_plane_fighter_airframe_2`). |
| `module_<EquipmentModule>_design_cost_factor` | naval, country, army | 2 dp | 312 equipment module tokens (for example `engine_1_1x`, `armor_plate_large`). |
| `production_cost_max_<NavalEquipment>` | naval | 0 dp | 9 tokens: `convoy`, `floating_harbor_equipment`, `repair_ship_hull`, `ship_hull_carrier`, `ship_hull_cruiser`, `ship_hull_heavy`, `ship_hull_light`, `ship_hull_submarine`, `support_ship_hull`. |
| `<Doctrine>_mastery_gain_factor` | country | 0 dp | Three kinds of token: the 4 doctrine folders (`air`, `land`, `naval`, `special_forces`), 12 grand doctrines and 95 sub-doctrines. |
| `<Doctrine>_track_mastery_gain_factor` | country | 0 dp | 14 tracks: `armor`, `capital_ships`, `carriers`, `combat_support`, `fighter_aircraft`, `heavy_aircraft`, `infantry`, `medium_aircraft`, `operations`, `screens`, `special_forces_first`, `special_forces_second`, `strike_aircraft`, `submarines`. |
| `<Technology>_cost_factor` | country | 0 dp | 39 technology category tokens, all starting with `cat_` (for example `cat_mobile_warfare`, `cat_synth_oil`, `cat_torpedoes`). Not limited to doctrines. |
| `<IdeaGroup>_cost_factor` | country | 0 dp | 25 idea groups (for example `economy`, `army_chief`, `hidden_ideas`, `army_spirit`). |
| `<IdeaCategory>_category_type_cost_factor` | country | 0 dp | `air_spirit`, `army_spirit`, `navy_spirit`. |
| `<Ideology>_acceptance`<br>`<Ideology>_drift`<br>`<Ideology>_drift_from_guarantees` | politics | 0 dp, 2 dp, 2 dp | `communism`, `democratic`, `fascism`, `neutrality`. |
| `<Operation>_cost`<br>`<Operation>_outcome`<br>`<Operation>_risk` | intelligence_agency | 0 dp | 41, 39 and 42 slot values: operation ids from `common/operations/` (for example `operation_infiltrate_civilian`, `bruneval_raid`, `FRA_coup_in_indochina`) plus the generic tokens `operation`, `operation_coup`, `operation_infiltrate`, `operation_steal_tech` and `target_sabotage`. The three sets differ slightly: `_cost` has no `operation_steal_tech`, and `_outcome` and `_risk` have no `operation_coup`. Which of them vanilla operations read is in the note below the table. |
| `<SpecialProject>_speed_factor` | country, state | 0 dp | 66 tokens: the `sp_*` projects and `specialization_air`, `specialization_land`, `specialization_naval`, `specialization_nuclear`. |
| `<Trait>_xp_gain_factor` | naval, country, army | 2 dp | For 29 unit leader traits whose token already starts with `trait_` (for example `trait_cautious`, giving `trait_cautious_xp_gain_factor`). |
| `trait_<Trait>_xp_gain_factor` | naval, country, army | 2 dp | For 165 traits whose token has no `trait_` prefix (for example `BALTIC_anti_bolshevik`). |
| `<CombatTactic>_preferred_weight_factor` | country | 2 dp | 56 tokens: `nullCombatTactic` and the `tactic_*` combat tactics. The documentation text calls it a naval weight. |
| `<ModifierStat>_factor`<br>`<ModifierStatValue>_value_factor` | country, state | 0 dp | Only `naval_general_support` and `naval_repair_support`, the support-ratio static modifiers in `common/modifiers/00_static_modifiers.txt`. (not described in the docs) |

Notes on rows of the table above:

- `<Operation>_cost`, `<Operation>_outcome`, `<Operation>_risk`: An operation only reacts to a modifier it names in its own `cost_modifiers`, `outcome_modifiers` or `risk_modifiers` list (`common/operations/_documentation.md`) [docs]. Vanilla operations name only `operation_cost`, `operation_infiltrate_cost`, `operation_coup_cost`, `target_sabotage_cost`, `operation_outcome`, `operation_infiltrate_outcome`, `operation_steal_tech_outcome`, `boost_resistance_factor`, `target_sabotage_factor`, `operation_risk`, `operation_infiltrate_risk`, `operation_steal_tech_risk` and `target_sabotage_risk`, so per-operation names such as `bruneval_raid_cost` are valid but no vanilla operation reads them in `common/operations/` [vanilla-confirmed 1.19.4.1].

Corrections to the rows above. [docs] `documentation/modifiers_documentation.md`

- `country_resource_*`, `country_resource_cost_*` and the state resource rows: there are 7 resources and the 7th is `coal`.
- `production_speed_*`, `repair_speed_*` and the `state_` variants: 55 building tokens, including `air_facility`, `land_facility`, `naval_facility`, `nuclear_facility`, `energy_infrastructure`, `naval_headquarters`, `naval_supply_hub`, `stronghold_network` and the landmarks.
- `production_cost_max_*`: also `floating_harbor_equipment`, `repair_ship_hull` and `support_ship_hull`.
- `experience_gain_<unit>_training_factor` and `_combat_factor` exist for 157 unit tokens, and a `_mission_factor` variant exists for each.
- `<idea_group>_cost_factor`: 25 groups; the row above names 16 and omits nine spirit groups (`army_spirit`, `navy_spirit`, `air_force_spirit`, `academy_spirit`, `division_command_spirit` and four more).
<!-- kit:end id="template-families" -->
