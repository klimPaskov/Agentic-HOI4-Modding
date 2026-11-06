# List of modifiers

Rows on this page that do not match 1.19.3. The game documents 722 plain modifiers and 38 template families, and 252 of the 722 are never named in the table below; the tables at the bottom add them.

- Not found in the modifier documentation or in any vanilla script or localisation (and not in the strings of `hoi4.exe`): `occupation_cost`, `modifier_enemy_port_superiority_limit`, `paratrooper_count_per_plane`, `max_marshal_army_size`, `max_marshal_army_group_size`, and the air factor rows `air_interception_{attack,defence,agility}_factor`, `air_air_superiority_{attack,defence,agility}_factor`, `air_close_air_support_{attack,defence,agility}_factor`, `air_strategic_bomber_{attack,agility}_factor` and `air_paradrop_{attack,defence,agility}_factor`. The `hoi4.exe` part is a read-only string search. (unverified) In an idea's `modifier` block, `occupation_cost` and `max_marshal_army_size` were rejected at load as "Unknown modifier", and read back by name each gave 0. The other names in this list were not tried.
- `max_commander_army_group_size` is not documented and no script or localisation uses it. The documented names are `max_commander_army_size` and `max_army_group_size`. The string appears once in `hoi4.exe`. It is not a leftover but a live modifier key: an idea with `max_commander_army_group_size = 1` loaded with no error.log line, the modifier read 1 once the idea was added, and the add tooltip showed "General Max Army Group Size". The tooltip text is from OCR of the console reply and partly garbled, and `list_modifiers` was not used.
- `foreign_subversive_activities` is misspelled. The game's token is `foreign_subversive_activites` (one "i" missing), which is what the documentation and 72 vanilla uses write.
- `operation_steal_tech_cost` is not in the documented `<Operation>_cost` list. The documented names are `operation_steal_tech_army_cost`, `operation_steal_tech_navy_cost`, `operation_steal_tech_airforce_cost` and `operation_steal_tech_civilian_cost`; `operation_steal_tech_outcome` and `operation_steal_tech_risk` do exist. A localisation key `operation_steal_tech_cost` exists in `localisation/english/modifiers_l_english.yml`. The old name is not recognised: in an idea's `modifier` block `operation_steal_tech_cost` was rejected at load as "Unknown modifier", and read back by name it gave 0.
- `breakthrough`, `armor_value`, `air_attack`, `air_defence`, `air_agility`, `maximum_speed`, `air_range`, `air_superiority` and `air_bombing` are equipment stats, not entries of the modifier documentation. They are keys of the equipment files in `common/units/equipment/` and of equipment upgrades.
- The explicit lists in some rows are shorter than the game's lists: resources (7, with `coal`), buildings (55, the page names up to 16), `production_cost_max_*` (9 tokens, the page names 6), units for `experience_gain_*` (157, and a third `_mission_factor` variant exists) and `special_forces_doctrine_cost_factor` next to the three `<land/air/naval>` doctrine cost rows. Full lists are in [Template modifier families](#template-modifier-families).

[Modifiers](modifiers.md) listed here are recognized by the game, but not necessarily used in any context.

The listed decimal places is for display only. All numbers support up to 3 decimal places.

| Name | In-game description | Notes |  |  |  |
| --- | --- | --- | --- | --- | --- |
| agency_upgrade_time | Agency upgrade time | Number with 2 decimal places |  |  |  |
| civilian_intel_factor | Civilian Intelligence |  |  |  |  |
| army_intel_factor | Army Intelligence |  |  |  |  |
| navy_intel_factor | Navy Intelligence |  |  |  |  |
| airforce_intel_factor | Air Intelligence |  |  |  |  |
| crypto_department_enabled | Crypto Department Enabled | Boolean |  |  |  |
| crypto_strength | Cryptology Level | Number with 0 decimal places |  |  |  |
| decryption_power | Decryption Power |  |  |  |  |
| decryption_power_factor | Decryption Power Factor | Number with 2 decimal places |  |  |  |
| civilian_intel_decryption_bonus | Decrypted Civilian Cipher Bonus | Number with 0 decimal places |  |  |  |
| army_intel_decryption_bonus | Decrypted Army Cipher Bonus |  |  |  |  |
| navy_intel_decryption_bonus | Decrypted Navy Cipher Bonus |  |  |  |  |
| airforce_intel_decryption_bonus | Decrypted Airforce Cipher Bonus |  |  |  |  |
| operative_slot | Operative slots |  |  |  |  |
| new_operative_slot_bonus | Operative recruitment choices |  |  |  |  |
| female_random_operative_chance | Added Female Operative Chance: |  |  |  |  |
| commando_trait_chance_factor | Chance of recruiting an Operative with the Commando trait |  |  |  |  |
| enemy_operative_recruitment_chance | Enemy nationality recruit chance | Number with 2 decimal places |  |  |  |
| occupied_operative_recruitment_chance | Occupied friendly nationality recruit chance |  |  |  |  |
| operative_death_on_capture_chance | Death chance of our Operative on capture |  |  |  |  |
| intel_network_gain | Intel network strength gain | Number with 2 decimal places |  |  |  |
| intel_network_gain_factor | Intel network strength gain |  |  |  |  |
| intel_from_operatives_factor | Intelligence gained from Operatives and Infiltrated Assets |  |  |  |  |
| intelligence_agency_defense | Counter intelligence |  |  |  |  |
| defense_impact_on_blueprint_stealing | Impact of enemy Counter Intelligence on Steal Blueprints operation | Number with 1 decimal places |  |  |  |
| boost_ideology_mission_factor | Boost Ideology mission effects | Number with 2 decimal places |  |  |  |
| control_trade_mission_factor | Control Trade mission effects |  |  |  |  |
| propaganda_mission_factor | Propaganda mission effects |  |  |  |  |
| diplomatic_pressure_mission_factor | Diplomatic Pressure mission effects |  |  |  |  |
| boost_resistance_factor | Strengthen Resistance efficiency |  |  |  |  |
| root_out_resistance_effectiveness_factor | Root Out Resistance mission effects |  |  |  |  |
| <land/air/naval>_doctrine_cost_factor | Changes the cost of buying a new doctrine of the specified type. | `land_doctrine_cost_factor = -0.05` | Percentual. |  | 1.11 |
| operation_cost<br>operation_outcome<br>operation_risk | Operation <parameter> | Number with 2 decimal places |  |  |  |
| operation_fake_intel_cost<br>operation_fake_intel_outcome<br>operation_fake_intel_risk | False Intelligence <parameter> |  |  |  |  |
| operation_rescue_operative_cost<br>operation_rescue_operative_outcome<br>operation_rescue_operative_risk | Rescue Operative <parameter> |  |  |  |  |
| operation_make_resistance_contacts_cost<br>operation_make_resistance_contacts_outcome<br>operation_make_resistance_contacts_risk | Make Resistance Contacts <parameter> |  |  |  |  |
| operation_boost_resistance_cost<br>operation_boost_resistance_outcome<br>operation_boost_resistance_risk | Strengthen Resistance <parameter> |  |  |  |  |
| operation_collaboration_government_cost<br>operation_collaboration_government_outcome<br>operation_collaboration_government_risk | Prepare Collaboration Government <parameter> |  |  |  |  |
| operation_coup_government_cost<br>operation_coup_government_outcome<br>operation_coup_government_risk | Stage Coup <parameter> |  |  |  |  |
| operation_capture_cipher_cost<br>operation_capture_cipher_outcome<br>operation_capture_cipher_risk | Capture Cipher <parameter> |  |  |  |  |
| operation_coordinated_strike_cost<br>operation_coordinated_strike_outcome<br>operation_coordinated_strike_risk | Coordinated Strike <parameter> |  |  |  |  |
| operation_infiltrate_cost<br>operation_infiltrate_outcome<br>operation_infiltrate_risk | Infiltration <parameter> |  |  |  |  |
| operation_infiltrate_armed_forces_army_cost<br>operation_infiltrate_armed_forces_army_outcome<br>operation_infiltrate_armed_forces_army_risk | Infiltrate Army <parameter> |  |  |  |  |
| operation_infiltrate_armed_forces_navy_cost<br>operation_infiltrate_armed_forces_navy_outcome<br>operation_infiltrate_armed_forces_navy_risk | Infiltrate Navy <parameter> |  |  |  |  |
| operation_infiltrate_armed_forces_airforce_cost<br>operation_infiltrate_armed_forces_airforce_outcome<br>operation_infiltrate_armed_forces_airforce_risk | Infiltrate Airforce <parameter> |  |  |  |  |
| operation_infiltrate_civilian_cost<br>operation_infiltrate_civilian_outcome<br>operation_infiltrate_civilian_risk | Infiltrate Civilian Administration <parameter> |  |  |  |  |
| operation_steal_tech_cost<br>operation_steal_tech_outcome<br>operation_steal_tech_risk | Steal Blueprint <parameter> |  |  |  |  |
| operation_steal_tech_army_cost<br>operation_steal_tech_army_outcome<br>operation_steal_tech_army_risk | Steal Military Blueprints <parameter> |  |  |  |  |
| operation_steal_tech_navy_cost<br>operation_steal_tech_navy_outcome<br>operation_steal_tech_navy_risk | Steal Naval Blueprints <parameter> |  |  |  |  |
| operation_steal_tech_airforce_cost<br>operation_steal_tech_airforce_outcome<br>operation_steal_tech_airforce_risk | Steal Aviation Industry Blueprints <parameter> |  |  |  |  |
| operation_steal_tech_civilian_cost<br>operation_steal_tech_civilian_outcome<br>operation_steal_tech_civilian_risk | Steal Industrial Blueprints <parameter> |  |  |  |  |
| target_sabotage_cost<br>target_sabotage_factor<br>target_sabotage_risk | Sabotage <parameter> |  |  |  |  |
| operation_targeted_sabotage_industry_cost<br>operation_targeted_sabotage_industry_outcome<br>operation_targeted_sabotage_industry_risk | Sabotage Industry <parameter> |  |  |  |  |
| operation_targeted_sabotage_infrastructure_cost<br>operation_targeted_sabotage_infrastructure_outcome<br>operation_targeted_sabotage_infrastructure_risk | Sabotage Infrastructure <parameter> |  |  |  |  |
| operation_targeted_sabotage_resources_cost<br>operation_targeted_sabotage_resources_outcome<br>operation_targeted_sabotage_resources_risk | Sabotage Resources <parameter> |  |  |  |  |
| ai_focus_defense_factor | AI Modifier: Focus on Defense | Number with 1 decimal places; see [AI_focuses#Modding](ai_focuses.md#modding) |  |  |  |
| ai_focus_aggressive_factor | AI Modifier: Focus on Offense |  |  |  |  |
| ai_focus_war_production_factor | AI Modifier: Focus on War Production |  |  |  |  |
| ai_focus_military_advancements_factor | AI Modifier: Focus on Military Advancements |  |  |  |  |
| ai_focus_peaceful_factor | AI Modifier: Focus on Peace |  |  |  |  |
| ai_focus_naval_factor | AI Modifier: Focus on Navy |  |  |  |  |
| ai_focus_naval_air_factor | AI Modifier: Focus on Naval Air |  |  |  |  |
| ai_focus_aviation_factor | AI Modifier: Focus on Aviation |  |  |  |  |
| ai_focus_military_equipment_factor | AI Modifier: Focus on Military Equipment |  |  |  |  |
| ai_badass_factor | AI Modifier: Threat receptivity | Number with 1 decimal places |  |  |  |
| ai_desired_divisions_factor | Factor on how many divisions the country aims to produce. |  |  |  |  |
| ai_get_ally_desire_factor | AI Modifier: Desire to be in or expand a faction | Number with 0 decimal places |  |  |  |
| ai_call_ally_desire_factor | AI Modifier: Call Ally Desire |  |  |  |  |
| ai_join_ally_desire_factor | AI Modifier: Join Ally Desire |  |  |  |  |
| ai_license_acceptance | Acceptance when requesting to buy license |  |  |  |  |
| offence | Attack | Number with 2 decimal places |  |  |  |
| defence | Defense |  |  |  |  |
| attack_bonus_against | Attack bonus against country | Number with 1 decimal places |  |  |  |
| attack_bonus_against_cores | Attack on their core territory |  |  |  |  |
| defense_bonus_against | Defense bonus against country |  |  |  |  |
| land_night_attack | Land Night Attack |  |  |  |  |
| army_attack_factor | Division Attack | Number with 2 decimal places |  |  |  |
| army_defence_factor | Division Defense |  |  |  |  |
| army_core_attack_factor | Division Attack on core territory |  |  |  |  |
| army_core_defence_factor | Division Defense on core territory |  |  |  |  |
| army_speed_factor | Divisions speed |  |  |  |  |
| army_speed_factor_for_controller | Divisions speed | Number with 2 decimal places; state modifier |  |  |  |
| army_org | Division Organization | Number with 1 decimal places |  |  |  |
| army_org_factor | Division Organization |  |  |  |  |
| army_org_regain | Army Organization Regain | Number with 2 decimal places |  |  |  |
| org_loss_when_moving | Org Loss when Moving | Number with 1 decimal places |  |  |  |
| army_morale | Division Recovery Rate |  |  |  |  |
| army_morale_factor | Division Recovery Rate |  |  |  |  |
| breakthrough | Breakthrough | Number with 2 decimal places; must be used in an land eq. category |  |  |  |
| breakthrough_factor | Breakthrough | Number with 2 decimal places |  |  |  |
| breakthrough_bonus_against | Breakthrough bonus against country | Number with 1 decimal places |  |  |  |
| armor_value | Armor | Number with 2 decimal places; must be used in an eq. category |  |  |  |
| dig_in_speed | Entrenchment speed | Number with 0 decimal places |  |  |  |
| dig_in_speed_factor | Entrenchment speed | Number with 1 decimal places |  |  |  |
| max_dig_in | Max Entrenchment | Number with 1 decimal places. Can be applied to a state |  |  |  |
| max_dig_in_factor | Max Entrenchment |  |  |  |  |
| dont_lose_dig_in_on_attack | No Entrenchment Lose On Attack | Boolean |  |  |  |
| recon_factor | Reconnaissance | Number with 1 decimal places |  |  |  |
| recon_factor_while_entrenched | Recon Bonus While Entrenched |  |  |  |  |
| max_planning | Max planning |  |  |  |  |
| max_planning_factor | Max planning factor |  |  |  |  |
| planning_speed | Planning Speed |  |  |  |  |
| supply_consumption_factor | Supply Consumption |  |  |  |  |
| out_of_supply_factor | Out of Supply |  |  |  |  |
| no_supply_grace | Supply Grace |  |  |  |  |
| extra_marine_supply_grace | Extra Marine Supply Grace |  |  |  |  |
| extra_paratrooper_supply_grace | Extra Paratrooper Supply Grace |  |  |  |  |
| attrition | Division Attrition |  |  |  |  |
| attrition_for_controller | Division Attrition | Number with 1 decimal places; state modifier |  |  |  |
| winter_attrition | Winter Attrition | Number with 1 decimal places |  |  |  |
| winter_attrition_factor | Winter Attrition | Number with 2 decimal places |  |  |  |
| heat_attrition | Heat Attrition | Number with 1 decimal places |  |  |  |
| heat_attrition_factor | Heat Attrition | Number with 2 decimal places |  |  |  |
| unit_upkeep_attrition_factor | Unit Upkeep | Number with 0 decimal places |  |  |  |
| land_reinforce_rate | Reinforce Rate | Number with 1 decimal places |  |  |  |
| combat_width_factor | Own Combat Width |  |  |  |  |
| minimum_training_level | Minimum training level | Number with 0 decimal places |  |  |  |
| max_training | Max training | Number with 2 decimal places |  |  |  |
| training_time_factor | Training time |  |  |  |  |
| training_time_army | Division training time | Number with 1 decimal places |  |  |  |
| training_time_army_factor | Division training time |  |  |  |  |
| river_crossing_factor | River Crossing Speed Penalty | Number with 2 decimal places |  |  |  |
| terrain_penalty_reduction | Terrain Penalty Reduction | Number with 1 decimal places |  |  |  |
| pocket_penalty | Encirclement penalty |  |  |  |  |
| fortification_damage | Fort Damage from Combat |  |  |  |  |
| fortification_collateral_chance | Fort Combat Damage Chance |  |  |  |  |
| acclimatization_cold_climate_gain_factor | Cold acclimatization gain factor |  |  |  |  |
| acclimatization_hot_climate_gain_factor | Hot acclimatization gain factor |  |  |  |  |
| special_forces_min | Special Forces Minimum Capacity | Number with 0 decimal places |  |  |  |
| special_forces_cap | Special Forces Capacity Multiplier | Number with 1 decimal places |  |  |  |
| special_forces_training_time_factor | Special Forces Division training time |  |  |  |  |
| special_forces_no_supply_grace | Special Forces Supply Grace |  |  |  |  |
| special_forces_out_of_supply_factor | Special Forces Out of Supply | Number with 2 decimal places |  |  |  |
| army_armor_attack_factor<br>army_armor_defence_factor<br>army_armor_speed_factor army_infantry_attack_factor<br>army_infantry_defence_factor  army_artillery_attack_factor<br>army_artillery_defence_factor  cavalry_attack_factor<br>cavalry_defence_factor  motorized_attack_factor<br>motorized_defence_factor  mechanized_attack_factor<br>mechanized_defence_factor  special_forces_attack_factor<br>special_forces_defence_factor  <unit_type>_attack_factor<br><unit_type>_defence_factor<br><unit_type>_speed_factor | <unit_type> <stat> | Number with 1 decimal places |  |  |  |
| military_leader_cost_factor | Military Leader Cost | Number with 1 decimal places |  |  |  |
| army_leader_cost_factor | Army Leader Cost |  |  |  |  |
| female_random_army_leader_chance | Added Female Army Leader Chance: | Number with 0 decimal places |  |  |  |
| army_leader_start_level | Starting level of new army leaders |  |  |  |  |
| army_leader_start_attack_level | Starting Attack skill level of new army leaders |  |  |  |  |
| army_leader_start_defense_level | Starting Defense skill level of new army leaders |  |  |  |  |
| army_leader_start_logistics_level | Starting Logistics skill level of new army leaders |  |  |  |  |
| army_leader_start_planning_level | Starting Planning skill level of new army leaders |  |  |  |  |
| cannot_use_abilities | Cannot Use Combat Abilities | Boolean |  |  |  |
| skill_bonus_factor | Leader Skill Bonuses | Number with 1 decimal places |  |  |  |
| reassignment_duration_factor | Army reassignment duration |  |  |  |  |
| sickness_chance | Chance to Get Sick | Number with 2 decimal places |  |  |  |
| wounded_chance_factor | Chance to get wounded in combat |  |  |  |  |
| promote_cost_factor | Promotion Cost | Number with 1 decimal places |  |  |  |
| max_commander_army_size | General Max Army Size | Number with 0 decimal places |  |  |  |
| max_commander_army_group_size | General Max Army Group Size |  |  |  |  |
| max_marshal_army_size | Field Marshal Max Army Size |  |  |  |  |
| max_marshal_army_group_size | Field Marshal Max Army Group Size |  |  |  |  |
| experience_gain_factor | Leader Experience Gain | Number with 1 decimal places |  |  |  |
| experience_gain_army | Army Experience Gain | Number with 2 decimal places |  |  |  |
| experience_gain_army_factor | Army Experience Gain | Number with 1 decimal places |  |  |  |
| experience_gain_army_unit | Division Experience Gain |  |  |  |  |
| experience_gain_army_unit_factor | Division Experience Gain |  |  |  |  |
| experience_loss_factor | Experienced soldier losses |  |  |  |  |
| disable_strategic_redeployment | Strategic Redeployment Disabled | Boolean |  |  |  |
| disable_strategic_redeployment_for_controller | Strategic Redeployment Disabled | Boolean; state modifier |  |  |  |
| exiled_divisions_attack_factor | Exiled Divisions Attack | Number with 2 decimal places |  |  |  |
| exiled_divisions_defense_factor | Exiled Divisions Defense |  |  |  |  |
| own_exiled_divisions_attack_factor | Own Exiled Divisions Attack |  |  |  |  |
| own_exiled_divisions_defense_factor | Own Exiled Divisions Defense |  |  |  |  |
| paratrooper_count_per_plane | Paratrooper per Plane | Number with 1 decimal places |  |  |  |
| paradrop_organization_factor | Paratrooper Organization Factor |  |  |  |  |
| paratrooper_aa_defense | Paratrooper Anti Air Defense |  |  |  |  |
| army_bonus_air_superiority_factor | Air Superiority | Number with 2 decimal places |  |  |  |
| enemy_army_bonus_air_superiority_factor | Enemy Air Support |  |  |  |  |
| air_superiority_bonus_in_combat | Air Superiority Bonus in Combat | Number with 1 decimal places |  |  |  |
| cas_damage_reduction | Damage Reduction Against CAS |  |  |  |  |
| shore_bombardment_bonus | Shore Bombardment Bonus |  |  |  |  |
| air_attack | Air Attack | Number with 0 decimal places; must be used in an air eq. category |  |  |  |
| air_attack_factor | Air Attack | Number with 2 decimal places |  |  |  |
| air_defence | Air Defense | Number with 0 decimal places; must be used in an air eq. category |  |  |  |
| air_defence_factor | Air Defense | Number with 2 decimal places |  |  |  |
| air_agility | Agility | Number with 0 decimal places; must be used in an air eq. category |  |  |  |
| air_agility_factor | Agility | Number with 2 decimal places |  |  |  |
| maximum_speed | Max Air Speed | Number with 0 decimal places; must be used in an air eq. category |  |  |  |
| air_maximum_speed_factor | Max Air Speed | Number with 2 decimal places |  |  |  |
| air_accidents | Air Accidents Chance | Number with 1 decimal places |  |  |  |
| air_accidents_factor | Air Accidents Chance | Number with 2 decimal places |  |  |  |
| air_range | Air Range | Number with 0 decimal places; must be used in an air eq. category |  |  |  |
| air_range_factor | Air Range | Number with 2 decimal places |  |  |  |
| air_weather_penalty | Bad Weather Penalty |  |  |  |  |
| air_night_penalty | Night Operations Penalty |  |  |  |  |
| air_detection | Air Detection |  |  |  |  |
| air_fuel_consumption_factor | Air Fuel Consumption | Number with 2 decimal places |  |  |  |
| experience_gain_air | Air Experience Gain |  |  |  |  |
| experience_gain_air_factor | Air Experience Gain | Number with 1 decimal places |  |  |  |
| air_training_xp_gain_factor | Air Wing Training Experience Gain | Number with 0 decimal places |  |  |  |
| air_mission_xp_gain_factor | Air Wing Mission Experience Gain |  |  |  |  |
| air_ace_generation_chance_factor | Ace generation chance | Number with 2 decimal places |  |  |  |
| air_wing_xp_loss_when_killed_factor | Air Wing Experience loss when killed | Number with 0 decimal places |  |  |  |
| air_mission_efficiency | Air Mission Efficiency | Number with 1 decimal places |  |  |  |
| air_superiority_efficiency | Air Superiority Mission Efficiency | Number with 2 decimal places |  |  |  |
| air_intercept_efficiency | Interception Mission Efficiency |  |  |  |  |
| air_cas_efficiency | Air Support Mission Efficiency |  |  |  |  |
| air_escort_efficiency | Escort Efficiency |  |  |  |  |
| air_nav_efficiency | Naval Mission Efficiency |  |  |  |  |
| air_interception_attack_factor<br>air_interception_defence_factor<br>air_interception_agility_factor<br>air_interception_detect_factor air_air_superiority_attack_factor<br>air_air_superiority_defence_factor<br>air_air_superiority_agility_factor<br>air_superiority_detect_factor  air_close_air_support_attack_factor<br>air_close_air_support_defence_factor<br>air_close_air_support_agility_factor  air_strategic_bomber_attack_factor<br>air_strategic_bomber_defence_factor<br>air_strategic_bomber_agility_factor<br>air_strategic_bomber_bombing_factor<br>air_strategic_bomber_night_penalty  naval_strike_attack_factor<br>naval_strike_targetting_factor<br>naval_strike_agility_factor | <Mission> <stat> |  |  |  |  |
| air_paradrop_attack_factor<br>air_paradrop_defence_factor<br>air_paradrop_agility_factor | Paradrop <stat> | Number with 2 decimal places; air_paradrop_agility_factor - exists and localizes but does not seem to do anything at all. |  |  |  |
| air_superiority | Air Superiority | Number with 1 decimal places; must be used in an air eq. category |  |  |  |
| air_cas_present_factor | Ground support | Number with 2 decimal places |  |  |  |
| ground_attack | Ground attack |  |  |  |  |
| ground_attack_factor | Ground attack factor |  |  |  |  |
| air_bombing | Ground Bombing | Number with 1 decimal places; must be used in an air eq. category |  |  |  |
| air_bombing_targetting | Ground Bombing Targeting | Number with 1 decimal places |  |  |  |
| strategic_bomb_visibility | Strategic bombing visibility | Number with 2 decimal places |  |  |  |
| naval_strike_attack_factor | Naval Bombing | Number with 0 decimal places |  |  |  |
| naval_strike_targetting_factor | Naval Targeting |  |  |  |  |
| naval_strike_agility_factor | Naval Agility |  |  |  |  |
| mines_planting_by_air_factor | Aerial minelaying efficiency |  |  |  |  |
| mines_sweeping_by_air_factor | Aerial minesweeping efficiency |  |  |  |  |
| modifier_enemy_port_superiority_limit | Port strike enemy superiority limit: |  |  |  |  |
| rocket_attack_factor | Rocket Damage | Number with 1 decimal places |  |  |  |
| naval_damage_factor | Damage | Number with 2 decimal places |  |  |  |
| naval_defense_factor | Defense |  |  |  |  |
| navy_org | Navy Organization | Number with 1 decimal places |  |  |  |
| navy_org_factor | Navy Organization |  |  |  |  |
| naval_morale | Ship Recovery Rate |  |  |  |  |
| naval_morale_factor | Ship Recovery Rate |  |  |  |  |
| naval_speed_factor | Naval Speed | Number with 0 decimal places |  |  |  |
| navy_max_range | Naval max range |  |  |  |  |
| navy_max_range_factor | Naval max range factor | Number with 2 decimal places |  |  |  |
| navy_fuel_consumption_factor | Navy Fuel Consumption |  |  |  |  |
| naval_attrition | Attrition |  |  |  |  |
| navy_visibility | Visibility |  |  |  |  |
| spotting_chance | Spotting Chance | Number with 0 decimal places |  |  |  |
| ships_at_battle_start | Number of ships in the first contact |  |  |  |  |
| positioning | Positioning | Number with 1 decimal places |  |  |  |
| naval_coordination | Fleet Coordination | Number with 0 decimal places |  |  |  |
| naval_detection | Naval Detection |  |  |  |  |
| naval_strike | Naval Strike |  |  |  |  |
| naval_hit_chance | Naval Hit Chance |  |  |  |  |
| strike_force_movement_org_loss | Strike Force Org loss | Number with 2 decimal places |  |  |  |
| naval_has_potf_in_combat_attack | Attack when in combat alongside the Pride of the Fleet |  |  |  |  |
| naval_has_potf_in_combat_defense | Defense when in combat alongside the Pride of the Fleet |  |  |  |  |
| navy_casualty_on_hit | Casualties factor on hit |  |  |  |  |
| navy_casualty_on_sink | Casualties on sink |  |  |  |  |
| naval_accidents_chance | Accident chance |  |  |  |  |
| critical_receive_chance | Chance to Receive Critical Hit | Number with 1 decimal places |  |  |  |
| naval_critical_effect_factor | Effects of sustained Critical Hits | Number with 2 decimal places |  |  |  |
| naval_critical_score_chance_factor | Chance to score Critical Hit |  |  |  |  |
| navy_submarine_attack_factor<br>navy_submarine_defence_factor<br>navy_submarine_detection_factor navy_screen_attack_factor<br>navy_screen_defence_factor  navy_capital_ship_attack_factor<br>navy_capital_ship_defence_factor  navy_carrier_air_attack_factor<br>navy_carrier_air_targetting_factor<br>navy_carrier_air_agility_factor | <ship_role> <stat> |  |  |  |  |
| screening_efficiency | Screening Efficiency | Number with 1 decimal places |  |  |  |
| convoy_escort_efficiency | Escort efficiency |  |  |  |  |
| submarine_attack | Submarine Attack |  |  |  |  |
| convoy_raiding_efficiency_factor | Convoy Raiding Efficiency | Number with 2 decimal places |  |  |  |
| sortie_efficiency | Sortie efficiency | Number with 0 decimal places |  |  |  |
| fighter_sortie_efficiency | Fighters sortie efficiency |  |  |  |  |
| carrier_traffic | Carrier Traffic |  |  |  |  |
| carrier_capacity_penalty_reduction | Carrier overcrowding | Number with 1 decimal places |  |  |  |
| port_strike | Port strikes |  |  |  |  |
| naval_mine_hit_chance | Chance to hit naval mine | Number with 2 decimal places |  |  |  |
| naval_mines_damage_factor | Naval mines damage | Number with 0 decimal places |  |  |  |
| naval_mines_effect_reduction | Naval mines avoidance |  |  |  |  |
| mines_planting_by_fleets_factor | Naval minelaying efficiency |  |  |  |  |
| mines_sweeping_by_fleets_factor | Naval minesweeping efficiency |  |  |  |  |
| naval_torpedo_hit_chance_factor | Torpedo hit chance | Number with 2 decimal places |  |  |  |
| naval_torpedo_reveal_chance_factor | Torpedo reveal chance |  |  |  |  |
| naval_torpedo_screen_penetration_factor | Torpedo screen penetration |  |  |  |  |
| naval_torpedo_cooldown_factor | Torpedo cooldown |  |  |  |  |
| navy_anti_air_attack | Naval AA attack | Number with 1 decimal places |  |  |  |
| navy_anti_air_attack_factor | Naval AA attack | Number with 2 decimal places |  |  |  |
| naval_retreat_chance | Retreat Decision Chance | Number with 0 decimal places |  |  |  |
| naval_retreat_speed | Fleet speed while retreating |  |  |  |  |
| sub_retreat_speed | Submarine speed while retreating |  |  |  |  |
| convoy_retreat_speed | Convoy speed while retreating |  |  |  |  |
| naval_enemy_retreat_chance | Enemy retreat chance | Number with 2 decimal places |  |  |  |
| naval_enemy_fleet_size_ratio_penalty_factor | Enemy fleet size penalty |  |  |  |  |
| navy_leader_cost_factor | Navy Leader Cost | Number with 1 decimal places |  |  |  |
| female_random_admiral_chance | Added Female Admiral Chance: | Number with 0 decimal places |  |  |  |
| navy_leader_start_level | Starting level of new navy leaders |  |  |  |  |
| navy_leader_start_attack_level | Starting Attack skill level of new navy leaders |  |  |  |  |
| navy_leader_start_defense_level | Starting Defense skill level of new navy leaders |  |  |  |  |
| navy_leader_start_maneuvering_level | Starting Maneuvering skill level of new navy leaders |  |  |  |  |
| navy_leader_start_coordination_level | Starting Coordination skill level of new navy leaders |  |  |  |  |
| experience_gain_navy | Naval Experience Gain | Number with 2 decimal places |  |  |  |
| experience_gain_navy_factor | Naval Experience Gain | Number with 1 decimal places |  |  |  |
| experience_gain_navy_unit_factor | Ship Experience Gain |  |  |  |  |
| experience_gain_navy_unit | Ship Experience Gain |  |  |  |  |
| production_cost_max_convoy<br>production_cost_max_ship_hull_submarine<br>production_cost_max_ship_hull_light<br>production_cost_max_ship_hull_heavy<br>production_cost_max_ship_hull_cruiser<br>production_cost_max_ship_hull_carrier<br>production_cost_max_<hull_type> | <hull> Max Cost | Number with 0 decimal places |  |  |  |
| refit_speed | Naval Equipment Refitting Speed |  |  |  |  |
| refit_ic_cost | Naval Equipment Refitting Cost |  |  |  |  |
| repair_speed_factor | Ship Repair Speed |  |  |  |  |
| transport_capacity | Troop convoy requirements | Number with 2 decimal places |  |  |  |
| invasion_preparation | Invasion Preparation Time | Number with 1 decimal places |  |  |  |
| naval_invasion_prep_speed | Invasion Preparation Speed |  |  |  |  |
| naval_invasion_capacity | Naval Invasion Capacity | Number with 0 decimal places |  |  |  |
| naval_invasion_penalty | Invasion Penalty | Number with 0 decimal places. Can be applied to a state |  |  |  |
| amphibious_invasion | Amphibious Invasion Speed | Number with 1 decimal places |  |  |  |
| amphibious_invasion_defence | Invasion Defense | Number with 0 decimal places. Can be applied to a state |  |  |  |
| democratic_drift<br>communism_drift<br>fascism_drift<br>neutrality_drift<br><ideology_group>_drift | Daily <ideology_group> Support | Number with 2 decimal places |  |  |  |
| democratic_acceptance<br>communism_acceptance<br>fascism_acceptance<br>neutrality_acceptance<br><ideology_group>_acceptance | Acceptance of <ideology_group> Diplomacy |  |  |  |  |
| drift_defence_factor | Ideology drift defense | Number with 1 decimal places |  |  |  |
| master_ideology_drift | Master Ideology Drift | Number with 2 decimal places |  |  |  |
| female_random_country_leader_chance | Added Female Country Leader Chance: | Number with 0 decimal places |  |  |  |
| political_power_cost | Daily Political Power Cost |  |  |  |  |
| political_power_gain | Daily Political Power Gain | Number with 2 decimal places |  |  |  |
| political_power_factor | Political Power Gain |  |  |  |  |
| stability_factor | Stability |  |  |  |  |
| stability_weekly | Weekly Stability |  |  |  |  |
| stability_weekly_factor | Weekly Stability Gain |  |  |  |  |
| party_popularity_stability_factor | Party Popularity Stability Modifier |  |  |  |  |
| war_stability_factor | War Penalty Stability Modifier |  |  |  |  |
| defensive_war_stability_factor | Defensive War Penalty Stability Modifier |  |  |  |  |
| offensive_war_stability_factor | Offensive War Penalty Stability Modifier |  |  |  |  |
| war_support_factor | War Support |  |  |  |  |
| war_support_weekly | Weekly War Support |  |  |  |  |
| war_support_weekly_factor | Weekly War Support Gain |  |  |  |  |
| command_power_gain | Daily Command Power Gain |  |  |  |  |
| command_power_gain_mult | Daily Command Power Gain Multiplier | Number with 0 decimal places |  |  |  |
| max_command_power | Maximum Command Power Increase |  |  |  |  |
| max_command_power_mult | Maximum Command Power Increase Multiplier |  |  |  |  |
| surrender_limit | Surrender Limit | Number with 2 decimal places |  |  |  |
| forced_surrender_limit | Surrender Limit |  |  |  |  |
| max_surrender_limit_offset | Minimum Surrender Limit |  |  |  |  |
| monthly_population | Monthly Population | Number with 1 decimal places |  |  |  |
| conscription | Recruitable Population | Number with 2 decimal places |  |  |  |
| conscription_factor | Recruitable Population Factor | Number with 0 decimal places |  |  |  |
| recruitable_population | Additional Recruitable Population | Number with 3 decimal places |  |  |  |
| recruitable_population_factor | Recruitable Population | Number with 2 decimal places |  |  |  |
| non_core_manpower | Non-core Manpower |  |  |  |  |
| weekly_manpower | Weekly Manpower | Number with 0 decimal places |  |  |  |
| mobilization_speed | Mobilization speed | Number with 2 decimal places |  |  |  |
| research_speed_factor | Research Speed |  |  |  |  |
| research_sharing_per_country_bonus | Technology sharing bonus |  |  |  |  |
| research_sharing_per_country_bonus_factor | Technology sharing bonus |  |  |  |  |
| encryption | Encryption |  |  |  |  |
| encryption_factor | Encryption |  |  |  |  |
| decryption | Decryption |  |  |  |  |
| decryption_factor | Decryption |  |  |  |  |
| civilian_factory_use | Civilian Factory Use | Number with 0 decimal places |  |  |  |
| consumer_goods_factor | Consumer Goods Factories | Number with 2 decimal places |  |  |  |
| min_export | Resources to Market |  |  |  |  |
| trade_opinion_factor | Trade deal opinion factor | Number with 2 decimal places |  |  |  |
| faction_trade_opinion_factor | Faction trade deal opinion factor |  |  |  |  |
| trade_cost_for_target_factor | Target country trade cost |  |  |  |  |
| extra_trade_to_target_factor | Extra trade to overlord |  |  |  |  |
| overlord_trade_cost_factor | Overlord trade cost |  |  |  |  |
| extra_trade_to_overlord_factor | Extra trade to overlord |  |  |  |  |
| autonomy_gain_trade | Freedom gain by trade |  |  |  |  |
| autonomy_gain_trade_factor | Freedom gain by trade |  |  |  |  |
| improve_relations_maintain_cost_factor | Improve relations maintain cost | Number with 0 decimal places |  |  |  |
| opinion_gain_monthly | Improve relations opinion | Number with 1 decimal places |  |  |  |
| opinion_gain_monthly_factor | Improve relations opinion | Number with 2 decimal places |  |  |  |
| opinion_gain_monthly_same_ideology | Same ideology monthly opinion | Number with 1 decimal places |  |  |  |
| opinion_gain_monthly_same_ideology_factor | Same ideology monthly opinion | Number with 2 decimal places |  |  |  |
| guarantee_cost | Guarantee Cost | Number with 0 decimal places |  |  |  |
| guarantee_tension | Guarantee tension limit | Number with 1 decimal places |  |  |  |
| join_faction_tension | Join faction tension limit |  |  |  |  |
| subversive_activites_upkeep | Subversive activities cost | Number with 0 decimal places |  |  |  |
| foreign_subversive_activities | Foreign subversive activities efficiency |  |  |  |  |
| justify_war_goal_time | Justify war goal time | Number with 1 decimal places |  |  |  |
| justify_war_goal_when_in_major_war_time | Justify war goal time when at war with a major |  |  |  |  |
| generate_wargoal_tension | Generate war goal tension limit |  |  |  |  |
| generate_wargoal_tension_against | Generate war goal tension limit against country |  |  |  |  |
| civil_war_involvement_tension | Civil war involvement tension |  |  |  |  |
| enemy_justify_war_goal_time | Justify war goal time on us |  |  |  |  |
| enemy_declare_war_tension | Declare war tension on us |  |  |  |  |
| send_volunteer_divisions_required | Divisions required for sending volunteer force | Number with 1 decimal places |  |  |  |
| send_volunteer_size | Max volunteer force divisions | Number with 0 decimal places |  |  |  |
| send_volunteer_factor | Max volunteer force divisions | Number with 1 decimal places |  |  |  |
| send_volunteers_tension | Send volunteers tension limit |  |  |  |  |
| air_volunteer_cap | Air volunteer cap | Number with 0 decimal places |  |  |  |
| no_compliance_gain | No Compliance Gain | Boolean |  |  |  |
| starting_compliance | Starting Compliance | Number with 0 decimal places |  |  |  |
| required_garrison_factor | Required Garrisons | Number with 0 decimal places; state modifier |  |  |  |
| compliance_gain | Daily Compliance Gain | Number with 3 decimal places; state modifier |  |  |  |
| compliance_growth | Compliance Growth Speed | Number with 0 decimal places; state modifier |  |  |  |
| compliance_growth_on_our_occupied_states | Compliance Growth Speed in our states occupied by the enemy; state modifier |  |  |  |  |
| resistance_activity | Resistance Activity Chance | Number with 1 decimal places; state modifier |  |  |  |
| resistance_garrison_penetration_chance | Garrison Penetration Chance | Number with 2 decimal places; state modifier |  |  |  |
| resistance_growth | Resistance Growth Speed | Number with 0 decimal places; state modifier |  |  |  |
| resistance_growth_on_our_occupied_states | Resistance Growth Speed in our states occupied by the enemy |  |  |  |  |
| resistance_decay | Resistance Decay Speed |  |  |  |  |
| resistance_decay_on_our_occupied_states | Resistance Decay Speed in our states occupied by the enemy |  |  |  |  |
| resistance_target | Resistance Target |  |  |  |  |
| resistance_target_on_our_occupied_states | Resistance Target in our states occupied by the enemy |  |  |  |  |
| resistance_damage_to_garrison | Damage to Garrisons | Number with 2 decimal places; state modifier |  |  |  |
| resistance_damage_to_garrison_on_our_occupied_states | Damage to Enemy Garrisons in our states occupied by the enemy |  |  |  |  |
| legitimacy_daily | Daily Legitimacy Gain | Number with 2 decimal places |  |  |  |
| targeted_legitimacy_daily | Daily Legitimacy Gain | Number with 1 decimal places |  |  |  |
| legitimacy_gain_factor | Legitimacy Gain | Number with 0 decimal places |  |  |  |
| exile_manpower_factor | Daily Exile Manpower | Number with 2 decimal places |  |  |  |
| puppet_cost_factor | Puppet cost | Number with 1 decimal places |  |  |  |
| occupation_cost | Occupation Cost | Number with 2 decimal places |  |  |  |
| annex_cost_factor | Annex cost | Number with 1 decimal places |  |  |  |
| subjects_autonomy_gain | Master impact | Number with 1 decimal places |  |  |  |
| autonomy_gain | Daily autonomy progress gain |  |  |  |  |
| autonomy_gain_global_factor | All autonomy gain |  |  |  |  |
| autonomy_gain_warscore | Freedom gain by war score | Number with 2 decimal places |  |  |  |
| autonomy_gain_ll_to_subject | Freedom gain by subject from lend lease from overlord |  |  |  |  |
| autonomy_gain_ll_to_subject_factor | Freedom gain by subject from lend lease from overlord |  |  |  |  |
| autonomy_gain_ll_to_overlord | Freedom gain by lend lease to overlord |  |  |  |  |
| autonomy_gain_ll_to_overlord_factor | Freedom gain by lend lease to overlord |  |  |  |  |
| autonomy_manpower_share | Subject manpower requirement |  |  |  |  |
| license_subject_master_purchase_cost | License cost between subject and master |  |  |  |  |
| can_master_build_for_us | Master can build constructions on the subject's territory | Boolean |  |  |  |
| master_build_autonomy_factor | Autonomy from building |  |  |  |  |
| cic_to_overlord_factor | Civilian industry to overlord | Number with 2 decimal places |  |  |  |
| mic_to_overlord_factor | Military industry to overlord |  |  |  |  |
| cic_to_target_factor | Civilian industry to target country |  |  |  |  |
| mic_to_target_factor | Military industry to target country |  |  |  |  |
| production_oil_factor | Synthetic Oil | Number with 0 decimal places |  |  |  |
| fuel_cost | Fuel Cost |  |  |  |  |
| base_fuel_gain | Fuel Gain | Number with 2 decimal places |  |  |  |
| base_fuel_gain_factor | Fuel Gain |  |  |  |  |
| fuel_gain | Fuel Gain per Oil | Number with 0 decimal places |  |  |  |
| fuel_gain_factor | Fuel Gain per Oil | Number with 2 decimal places |  |  |  |
| fuel_gain_from_states | Fuel Gain from Refineries |  |  |  |  |
| fuel_gain_factor_from_states | Fuel Gain from Refineries |  |  |  |  |
| max_fuel | Fuel Capacity (K) |  |  |  |  |
| max_fuel_building | Fuel Capacity (K) |  |  |  |  |
| max_fuel_factor | Fuel Capacity |  |  |  |  |
| army_fuel_capacity_factor | Army Fuel Capacity |  |  |  |  |
| army_fuel_consumption_factor | Army Fuel Consumption |  |  |  |  |
| air_fuel_consumption_factor | Air Fuel Consumption |  |  |  |  |
| navy_fuel_consumption_factor | Navy Fuel Consumption |  |  |  |  |
| refit_speed | Refitting Speed | Number with 0 decimal places |  |  |  |
| refit_ic_cost | Refitting Cost |  |  |  |  |
| industrial_factory_donations | Industrial Factory Donations |  |  |  |  |
| military_factory_donations | Military Factory Donations |  |  |  |  |
| dockyard_donations | Dockyard Donations |  |  |  |  |
| global_building_slots | Max Factories in a State |  |  |  |  |
| global_building_slots_factor | Max Factories in a State |  |  |  |  |
| production_speed_buildings_factor | Construction Speed | Number with 2 decimal places |  |  |  |
| production_speed_infrastructure_factor<br>production_speed_rail_way_factor<br>production_speed_supply_node_factor<br>production_speed_industrial_complex_factor<br>production_speed_arms_factory_factor<br>production_speed_dockyard_factor<br>production_speed_fuel_silo_factor<br>production_speed_synthetic_refinery_factor<br>production_speed_naval_base_factor<br>production_speed_radar_station_factor<br>production_speed_air_base_factor<br>production_speed_anti_air_building_factor<br>production_speed_bunker_factor<br>production_speed_coastal_bunker_factor<br>production_speed_rocket_site_factor<br>production_speed_nuclear_reactor_factor<br>production_speed_<building_type>_factor | <building_type> construction speed |  |  |  |  |
| conversion_cost_civ_to_mil_factor | Civilian to Military Factory conversion cost |  |  |  |  |
| conversion_cost_mil_to_civ_factor | Military to Civilian Factory conversion cost |  |  |  |  |
| industrial_capacity_factory | Factory Output |  |  |  |  |
| industrial_capacity_dockyard | Dockyard Output |  |  |  |  |
| production_factory_start_efficiency_factor | Production Efficiency Base |  |  |  |  |
| production_factory_max_efficiency_factor | Production Efficiency Cap |  |  |  |  |
| production_factory_efficiency_gain_factor | Production Efficiency growth |  |  |  |  |
| production_lack_of_resource_penalty_factor | Lack of Resources Penalty |  |  |  |  |
| line_change_production_efficiency_factor | Production Efficiency Retention |  |  |  |  |
| repair_speed_infrastructure_factor<br>repair_speed_industrial_complex_factor<br>repair_speed_arms_factory_factor<br>repair_speed_dockyard_factor<br>repair_speed_fuel_silo_factor<br>repair_speed_synthetic_refinery_factor<br>repair_speed_naval_base_factor<br>repair_speed_radar_station_factor<br>repair_speed_air_base_factor<br>repair_speed_anti_air_building_factor<br>repair_speed_bunker_factor<br>repair_speed_coastal_bunker_factor<br>repair_speed_rocket_site_factor<br>repair_speed_nuclear_reactor_factor<br>repair_speed_<building_type>_factor | <building_type> Repair Speed |  |  |  |  |
| industry_free_repair_factor | Free repair |  |  |  |  |
| industry_repair_factor | Factory Repair Speed |  |  |  |  |
| industry_air_damage_factor | Factory Bomb Vulnerability |  |  |  |  |
| tech_air_damage_factor | Anti-Air Bombing Damage Reduction |  |  |  |  |
| static_anti_air_damage_factor | Static Anti Air damage factor |  |  |  |  |
| static_anti_air_hit_chance_factor | Static Anti Air hit chance factor |  |  |  |  |
| nuclear_production | Allows Nuclear Bomb | Boolean |  |  |  |
| nuclear_production_factor | Nuclear Production | Number with 0 decimal places |  |  |  |
| local_building_slots | Max Factories in State | Number with 0 decimal places; state modifier |  |  |  |
| local_building_slots_factor | Max Factories in State |  |  |  |  |
| local_factories | Local Factories |  |  |  |  |
| local_factory_sabotage | Chance to Sabotage Constructions |  |  |  |  |
| local_intel_to_enemies | Intel to Enemies |  |  |  |  |
| local_manpower | Local Manpower |  |  |  |  |
| local_non_core_manpower | Local Non-core Manpower | Number with 2 decimal places; state modifier |  |  |  |
| local_org_regain | Organization Regain |  |  |  |  |
| local_supplies | Local Supplies | Number with 0 decimal places; state modifier |  |  |  |
| local_supplies_for_controller | Local Supplies |  |  |  |  |
| local_resources | Local Resources |  |  |  |  |
| local_resources_factor | Resource Gain Efficiency | Number with 2 decimal places |  |  |  |
| state_resources_factor | Local Available Resources | Number with 0 decimal places; state modifier |  |  |  |
| state_resource_aluminium<br>state_resource_chromium<br>state_resource_oil<br>state_resource_rubber<br>state_resource_steel<br>state_resource_tungsten<br>state_resource_<resource> | <Resource> |  |  |  |  |
| temporary_state_resource_aluminium<br>temporary_state_resource_chromium<br>temporary_state_resource_oil<br>temporary_state_resource_rubber<br>temporary_state_resource_steel<br>temporary_state_resource_tungsten<br>temporary_state_resource_<resource> | <Resource> |  |  |  |  |
| state_resource_cost_aluminium<br>state_resource_cost_chromium<br>state_resource_cost_oil<br>state_resource_cost_rubber<br>state_resource_cost_steel<br>state_resource_cost_tungsten<br>state_resource_cost_<resource> | <Resource> Consumption |  |  |  |  |
| country_resource_aluminium<br>country_resource_chromium<br>country_resource_oil<br>country_resource_rubber<br>country_resource_steel<br>country_resource_tungsten<br>country_resource_<resource> | <Resource> | Number with 0 decimal places |  |  |  |
| country_resource_cost_aluminium<br>country_resource_cost_chromium<br>country_resource_cost_oil<br>country_resource_cost_rubber<br>country_resource_cost_steel<br>country_resource_cost_tungsten<br>country_resource_cost_<resource> | <Resource> Consumption |  |  |  |  |
| state_production_speed_buildings_factor | Local Construction Speed | Number with 0 decimal places; state modifier |  |  |  |
| state_production_speed_infrastructure_factor<br>state_production_speed_industrial_complex_factor<br>state_production_speed_arms_factory_factor<br>state_production_speed_dockyard_factor<br>state_production_speed_fuel_silo_factor<br>state_production_speed_synthetic_refinery_factor<br>state_production_speed_naval_base_factor<br>state_production_speed_radar_station_factor<br>state_production_speed_air_base_factor<br>state_production_speed_anti_air_building_factor<br>state_production_speed_bunker_factor<br>state_production_speed_coastal_bunker_factor<br>state_production_speed_rocket_site_factor<br>state_production_speed_nuclear_reactor_factor<br>state_production_speed_<building_type>_factor | Local <building_type> construction speed | Number with 2 decimal places; state modifier |  |  |  |
| state_repair_speed_infrastructure_factor<br>state_repair_speed_industrial_complex_factor<br>state_repair_speed_arms_factory_factor<br>state_repair_speed_dockyard_factor<br>state_repair_speed_fuel_silo_factor<br>state_repair_speed_synthetic_refinery_factor<br>state_repair_speed_naval_base_factor<br>state_repair_speed_radar_station_factor<br>state_repair_speed_air_base_factor<br>state_repair_speed_anti_air_building_factor<br>state_repair_speed_bunker_factor<br>state_repair_speed_coastal_bunker_factor<br>state_repair_speed_rocket_site_factor<br>state_repair_speed_nuclear_reactor_factor<br>state_repair_speed_<building_type>_factor | Local <building_type> Repair Speed |  |  |  |  |
| equipment_upgrade_xp_cost | Equipment Experience Cost | Number with 0 decimal places; country modifier |  |  |  |
| land_equipment_upgrade_xp_cost | Land Equipment Experience Cost |  |  |  |  |
| naval_equipment_upgrade_xp_cost | Naval Equipment Experience Cost |  |  |  |  |
| air_equipment_upgrade_xp_cost | Air Equipment Experience Cost |  |  |  |  |
| equipment_conversion_speed | Conversion speed bonus | Number with 1 decimal places |  |  |  |
| equipment_capture | Equipment Capture Ratio Gain |  |  |  |  |
| equipment_capture_factor | Equipment Capture Ratio Modifier |  |  |  |  |
| lend_lease_tension | Lend-lease tension limit |  |  |  |  |
| license_purchase_cost | License purchase cost | Number with 0 decimal places |  |  |  |
| license_production_speed | License production speed |  |  |  |  |
| license_tech_difference_speed | License production speed from technology difference |  |  |  |  |
| license_infantry_purchase_cost<br>license_naval_purchase_cost<br>license_air_purchase_cost<br>license_armor_purchase_cost | <archetype> license purchase cost |  |  |  |  |
| license_infantry_eq_cost_factor<br>license_artillery_eq_cost_factor<br>license_anti_tank_eq_cost_factor<br>license_light_tank_eq_cost_factor | License purchase cost for <archetype> |  |  |  |  |
| license_infantry_eq_production_speed_factor<br>license_artillery_eq_production_speed_factor<br>license_anti_tank_eq_production_speed_factor<br>license_light_tank_eq_production_speed_factor | License production speed for <archetype> |  |  |  |  |
| license_infantry_eq_tech_difference_speed_factor<br>license_artillery_eq_tech_difference_speed_factor<br>license_anti_tank_eq_tech_difference_speed_factor<br>license_light_tank_eq_tech_difference_speed_factor | License production speed from technology difference for <archetype> |  |  |  |  |
| political_advisor_cost_factor<br>economy_cost_factor<br>trade_laws_cost_factor<br>mobilization_laws_cost_factor<br>army_chief_cost_factor<br>navy_chief_cost_factor<br>air_chief_cost_factor<br>high_command_cost_factor<br>theorist_cost_factor<br>materiel_manufacturer_cost_factor<br>naval_manufacturer_cost_factor<br>aircraft_manufacturer_cost_factor<br>tank_manufacturer_cost_factor<br>industrial_concern_cost_factor<br>country_cost_factor<br>hidden_ideas_cost_factor<br><idea_group>_cost_factor | <idea_group> Cost |  |  |  |  |
| experience_gain_infantry_training_factor<br>experience_gain_infantry_combat_factor<br>experience_gain_mountaineers_training_factor<br>experience_gain_mountaineers_combat_factor<br>experience_gain_marine_training_factor<br>experience_gain_marine_combat_factor<br>experience_gain_paratrooper_training_factor<br>experience_gain_paratrooper_combat_factor<br>experience_gain_bicycle_battalion_training_factor<br>experience_gain_bicycle_battalion_combat_factor<br>experience_gain_cavalry_training_factor<br>experience_gain_cavalry_combat_factor<br>experience_gain_armored_car_training_factor<br>experience_gain_armored_car_combat_factor<br>experience_gain_armored_car_recon_training_factor<br>experience_gain_armored_car_recon_combat_factor<br>experience_gain_motorized_training_factor<br>experience_gain_motorized_combat_factor<br>experience_gain_motorized_rocket_brigade_training_factor<br>experience_gain_motorized_rocket_brigade_combat_factor<br>experience_gain_mechanized_training_factor<br>experience_gain_mechanized_combat_factor<br>experience_gain_amphibious_mechanized_training_factor<br>experience_gain_amphibious_mechanized_combat_factor experience_gain_engineer_training_factor<br>experience_gain_engineer_combat_factor<br>experience_gain_recon_training_factor<br>experience_gain_recon_combat_factor<br>experience_gain_military_police_training_factor<br>experience_gain_military_police_combat_factor<br>experience_gain_maintenance_company_training_factor<br>experience_gain_maintenance_company_combat_factor<br>experience_gain_field_hospital_training_factor<br>experience_gain_field_hospital_combat_factor<br>experience_gain_logistics_company_training_factor<br>experience_gain_logistics_company_combat_factor<br>experience_gain_signal_company_training_factor<br>experience_gain_signal_company_combat_factor<br>experience_gain_mot_recon_training_factor<br>experience_gain_mot_recon_combat_factor  experience_gain_artillery_training_factor<br>experience_gain_artillery_combat_factor<br>experience_gain_rocket_artillery_training_factor<br>experience_gain_rocket_artillery_combat_factor<br>experience_gain_anti_air_training_factor<br>experience_gain_anti_air_combat_factor<br>experience_gain_anti_tank_training_factor<br>experience_gain_anti_tank_combat_factor<br>experience_gain_artillery_brigade_training_factor<br>experience_gain_artillery_brigade_combat_factor<br>experience_gain_rocket_artillery_brigade_training_factor<br>experience_gain_rocket_artillery_brigade_combat_factor<br>experience_gain_anti_air_brigade_training_factor<br>experience_gain_anti_air_brigade_combat_factor<br>experience_gain_anti_tank_brigade_training_factor<br>experience_gain_anti_tank_brigade_combat_factor<br>experience_gain_mot_artillery_brigade_training_factor<br>experience_gain_mot_artillery_brigade_combat_factor<br>experience_gain_mot_rocket_artillery_brigade_training_factor<br>experience_gain_mot_rocket_artillery_brigade_combat_factor<br>experience_gain_mot_anti_air_brigade_training_factor<br>experience_gain_mot_anti_air_brigade_combat_factor<br>experience_gain_mot_anti_tank_brigade_training_factor<br>experience_gain_mot_anti_tank_brigade_combat_factor  experience_gain_light_armor_training_factor<br>experience_gain_light_armor_combat_factor<br>experience_gain_light_sp_artillery_brigade_training_factor<br>experience_gain_light_sp_artillery_brigade_combat_factor<br>experience_gain_light_sp_anti_air_brigade_training_factor<br>experience_gain_light_sp_anti_air_brigade_combat_factor<br>experience_gain_light_tank_destroyer_brigade_training_factor<br>experience_gain_light_tank_destroyer_brigade_combat_factor<br>experience_gain_light_tank_recon_training_factor<br>experience_gain_light_tank_recon_combat_factor<br>experience_gain_medium_armor_training_factor<br>experience_gain_medium_armor_combat_factor<br>experience_gain_medium_sp_artillery_brigade_training_factor<br>experience_gain_medium_sp_artillery_brigade_combat_factor<br>experience_gain_medium_sp_anti_air_brigade_training_factor<br>experience_gain_medium_sp_anti_air_brigade_combat_factor<br>experience_gain_medium_tank_destroyer_brigade_training_factor<br>experience_gain_medium_tank_destroyer_brigade_combat_factor<br>experience_gain_heavy_armor_training_factor<br>experience_gain_heavy_armor_combat_factor<br>experience_gain_heavy_sp_artillery_brigade_training_factor<br>experience_gain_heavy_sp_artillery_brigade_combat_factor<br>experience_gain_heavy_sp_anti_air_brigade_training_factor<br>experience_gain_heavy_sp_anti_air_brigade_combat_factor<br>experience_gain_heavy_tank_destroyer_brigade_training_factor<br>experience_gain_heavy_tank_destroyer_brigade_combat_factor<br>experience_gain_super_heavy_armor_training_factor<br>experience_gain_super_heavy_armor_combat_factor<br>experience_gain_super_heavy_sp_artillery_brigade_training_factor<br>experience_gain_super_heavy_sp_artillery_brigade_combat_factor<br>experience_gain_super_heavy_sp_anti_air_brigade_training_factor<br>experience_gain_super_heavy_sp_anti_air_brigade_combat_factor<br>experience_gain_super_heavy_tank_destroyer_brigade_training_factor<br>experience_gain_super_heavy_tank_destroyer_brigade_combat_factor<br>experience_gain_modern_armor_training_factor<br>experience_gain_modern_armor_combat_factor<br>experience_gain_modern_sp_artillery_brigade_training_factor<br>experience_gain_modern_sp_artillery_brigade_combat_factor<br>experience_gain_modern_sp_anti_air_brigade_training_factor<br>experience_gain_modern_sp_anti_air_brigade_combat_factor<br>experience_gain_modern_tank_destroyer_brigade_training_factor<br>experience_gain_modern_tank_destroyer_brigade_combat_factor<br>experience_gain_amphibious_armor_training_factor<br>experience_gain_amphibious_armor_combat_factor  experience_gain_submarine_training_factor<br>experience_gain_submarine_combat_factor<br>experience_gain_destroyer_training_factor<br>experience_gain_destroyer_combat_factor<br>experience_gain_light_cruiser_combat_factor<br>experience_gain_light_cruiser_training_factor<br>experience_gain_heavy_cruiser_training_factor<br>experience_gain_heavy_cruiser_combat_factor<br>experience_gain_battle_cruiser_training_factor<br>experience_gain_battle_cruiser_combat_factor<br>experience_gain_battleship_training_factor<br>experience_gain_battleship_combat_factor<br>experience_gain_carrier_training_factor<br>experience_gain_carrier_combat_factor  experience_gain_fighter_training_factor<br>experience_gain_fighter_combat_factor<br>experience_gain_cv_fighter_training_factor<br>experience_gain_cv_fighter_combat_factor<br>experience_gain_heavy_fighter_training_factor<br>experience_gain_heavy_fighter_combat_factor<br>experience_gain_jet_fighter_training_factor<br>experience_gain_jet_fighter_combat_factor<br>experience_gain_cas_training_factor<br>experience_gain_cas_combat_factor<br>experience_gain_cv_cas_training_factor<br>experience_gain_cv_cas_combat_factor<br>experience_gain_nav_bomber_training_factor<br>experience_gain_nav_bomber_combat_factor<br>experience_gain_cv_nav_bomber_training_factor<br>experience_gain_cv_nav_bomber_combat_factor<br>experience_gain_tac_bomber_training_factor<br>experience_gain_tac_bomber_combat_factor<br>experience_gain_jet_tac_bomber_training_factor<br>experience_gain_jet_tac_bomber_combat_factor<br>experience_gain_strat_bomber_training_factor<br>experience_gain_strat_bomber_combat_factor<br>experience_gain_jet_strat_bomber_training_factor<br>experience_gain_jet_strat_bomber_combat_factor<br>experience_gain_transport_plane_training_factor<br>experience_gain_transport_plane_combat_factor<br>experience_gain_scout_plane_training_factor<br>experience_gain_scout_plane_combat_factor<br>experience_gain_rocket_interceptor_training_factor<br>experience_gain_rocket_interceptor_combat_factor<br>experience_gain_suicide_craft_training_factor<br>experience_gain_suicide_craft_combat_factor<br>experience_gain_guided_missile_training_factor<br>experience_gain_guided_missile_combat_factor  experience_gain_<unit_type>_training_factor<br>experience_gain_<unit_type>_combat_factor | <sub_unit> Training/Combat Experience Gain |  |  |  |  |

## Documented modifiers missing from the table

252 documented modifiers are never named in the table above. They are grouped by theme below. The sub-unit family is a grid after the groups.

- Modifier, Categories and Format come from the game documentation. `dp` is the number of decimals the tooltip shows; any value accepts up to 3 decimals.
- Meaning is the in-game wording from `localisation/english/modifiers_l_english.yml` and the MIO and effect strings, paraphrased. The text file changed in 1.19.4.1 and the old text is gone, so a reworded single row would not show. A word-overlap check of the meaning column against the new file found no row that contradicts it. (unverified)
- A meaning that starts with `~` is a guess from the name and its vanilla use. (unverified)
- An empty meaning means the name is self-explanatory. `(not described in the docs)` means there is no in-game text and no clear vanilla use.
- "Unused in vanilla" means no `key = value` use in `common/`, `events/` or `history/`.
- Sample checks against vanilla use: `army_non_core_attack_factor` is negative in `common/ideas/australia.txt`; `naval_invasion_prep_days` is -5 and -10 in `special_forces_subdoctrines.txt` and `MTG_naval_Support.txt`; `army_intel_to_others` is -15 and -50 in a trait and a decision; `peace_score_ratio_transferred_to_players` is used by the `diff_*_ai` static modifiers; `river_crossing_factor_against` sits inside `targeted_modifier` in `common/ideas/GER.txt`.

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

These only work inside a `targeted_modifier = { tag = X ... }` block. The in-game text of eleven of them ends in "against a country", and `river_crossing_factor_against` reads "against country". Vanilla uses `spotting_chance_against`, `navy_capital_ship_attack_factor_against` and `navy_screen_attack_factor_against` that way in `common/ideas/japan.txt` (the first two also in `common/ideas/australia.txt`) and `river_crossing_factor_against` in `common/ideas/GER.txt`.

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

Only the `modifier_army_sub_unit_*` names listed in `sub_unit_modifiers = { ... }` in `common/units/unit_modifiers/unit_modifiers.txt` exist, and the documentation names exactly these 54. Add a mod battalion's names to that block to get its modifiers. The file marks the speed and max organisation modifiers of `armored_car_recon`, `light_tank_recon` and `blackshirt_assault_battalion` "Cannot be applied to support battalions". `category_special_forces` and `category_rocket_artillery` are sub-unit categories. All 54 rows: categories `army`, format 2 dp.

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

## Template modifier families

Each pattern stands for one modifier per slot value; the documentation lists the slot values as "modified types". The explicit rows above name only some of them.

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

- `<Operation>_cost`, `<Operation>_outcome`, `<Operation>_risk`: An operation only reacts to a modifier it names in its own `cost_modifiers`, `outcome_modifiers` or `risk_modifiers` list (`common/operations/_documentation.md`). Vanilla operations name only `operation_cost`, `operation_infiltrate_cost`, `operation_coup_cost`, `target_sabotage_cost`, `operation_outcome`, `operation_infiltrate_outcome`, `operation_steal_tech_outcome`, `boost_resistance_factor`, `target_sabotage_factor`, `operation_risk`, `operation_infiltrate_risk`, `operation_steal_tech_risk` and `target_sabotage_risk`, so per-operation names such as `bruneval_raid_cost` are valid but no vanilla operation reads them in `common/operations/`.

Corrections to the rows above.

- `country_resource_*`, `country_resource_cost_*` and the state resource rows: there are 7 resources and the 7th is `coal`.
- `production_speed_*`, `repair_speed_*` and the `state_` variants: 55 building tokens, including `air_facility`, `land_facility`, `naval_facility`, `nuclear_facility`, `energy_infrastructure`, `naval_headquarters`, `naval_supply_hub`, `stronghold_network` and the landmarks.
- `production_cost_max_*`: also `floating_harbor_equipment`, `repair_ship_hull` and `support_ship_hull`.
- `experience_gain_<unit>_training_factor` and `_combat_factor` exist for 157 unit tokens, and a `_mission_factor` variant exists for each.
- `<idea_group>_cost_factor`: 25 groups; the row above names 16 and omits nine spirit groups (`army_spirit`, `navy_spirit`, `air_force_spirit`, `academy_spirit`, `division_command_spirit` and four more).
