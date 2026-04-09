# Table of contents

- [Arguments](#arguments)
- [Icon](#icon)
- [Localisation](#localisation)
- [Example](#example)
- [Related defines](#related-defines)
- [Additional notes](#additional-notes)
- [References](#references)


---

Different levels of the autonomy system are defined in /Hearts of Iron IV/common/autonomous\_states/\*.txt, and new ones can be created.

## Arguments

- **id** is the ID of the autonomy state, unique to each one. It is necessary to define to distinguish it from other autonomy states.
- **default**: If true, the game will attempt to make the 'puppet' option in peace deals as well as the 'puppet' effect use this autonomy state among other default autonomy states. By default, set to no.
- **is\_puppet** decides whether the subject is a puppet or not, making is\_puppet and is\_puppet\_of triggers true in that case. By default, set to no.
- **use\_overlord\_color** makes the subject have the same country color as the overlord.
- **min\_freedom\_level** decides the order in which autonomy states are placed. The autonomy states with lower freedom levels have less autonomy than those with higher when the game places the autonomy states for the subject to lose or gain a level. This also decides how many autonomy points the subject needs to gain or lose a level, calculated by the difference between freedom levels multiplied by 5000. As such, it would take 500 points to go from an autonomous state with the min\_freedom\_level of 0.1 to being annexed.
- **manpower\_influence** decides how large of a portion of the subject's manpower the overlord can use in colonial divisions.
- **rule** sets the game rules for the subject to either yes or no.

- **The following game rules exist as possible options:**
  - Column 2: Internal name
  - Column 3: Localised name
  - Column 4: Notes
  - Column 5: can_access_market
  - Column 6:
    ```text
    Can access International Market (
    Puppets
    and
    Overlords
    can always access each other's market)
    ```
  - Column 8: can_be_spymaster
  - Column 9: Can be Spy Master
  - Column 11: can_boost_other_ideologies
  - Column 12: Can boost popularity of other ideologies
  - Column 14: can_boost_own_ideology
  - Column 15: Can boost own party popularity in other countries
  - Column 17: can_create_collaboration_government
  - Column 18: Can create collaboration governments
  - Column 20: can_create_factions
  - Column 21: Can Create Factions
  - Column 23: can_declare_war_on_same_ideology
  - Column 24: Can declare war on country with the same ideology group without a war goal
  - Column 26: can_declare_war_without_wargoal_when_in_war
  - Column 27: Can declare war on a neighbor without a wargoal when at war with a major
  - Column 29: can_decline_call_to_war
  - Column 30: Can decline call to war
  - Column 32: can_force_government
  - Column 33: Can force government of another country to adopt the same ideology
  - Column 35: can_generate_female_aces
  - Column 36: Women in your country are allowed to become military pilots
  - Column 38: can_generate_female_country_leaders
  - Column 39: Can generate female country leaders
  - Column 41: can_generate_female_unit_leaders
  - Column 42: Can generate female unit leaders
  - Column 44: can_guarantee_other_ideologies
  - Column 45: Can guarantee other ideologies
  - Column 47: can_join_factions
  - Column 48: Can join factions
  - Column 50: can_join_factions_not_allowed_diplomacy
  - Column 51:
    ```text
    Country's name
    is not allowed to join factions
    ```
  - Column 53: can_join_opposite_factions
  - Column 54: Can Join Factions led by another Ideology
  - Column 56: can_lower_tension
  - Column 57: Lowers World Tension with Guarantees
  - Column 59: can_not_build_buildings
  - Column 60: CAN_NOT_BUILD_BUILDINGS
  - Column 61: Doesn't seem to work.
  - Column 62: can_not_declare_war
  - Column 63: Can not declare wars
  - Column 64: Prevents generating wargoals, but not using existing ones.
  - Column 65: can_occupy_non_war
  - Column 66: Can hold territory owned by a country they are not at war with
  - Column 68: can_only_justify_war_on_threat_country
  - Column 69: Can justify war goals against a country that have not generated world tension
  - Column 71: can_puppet
  - Column 72: Can puppet a country
  - Column 74: can_send_volunteers
  - Column 75: Can send volunteer forces
  - Column 77: can_use_kamikaze_pilots
  - Column 78: Can use kamikaze pilots
  - Column 80: contributes_operatives
  - Column 81: Contributes Operatives to Spy Master: Yes
  - Column 82: Only has an effect for subjects.
  - Column 83: units_deployed_to_overlord
  - Column 84: Control over deployed units go to overlord
  - Column 85: Only has an effect for subjects.

- **Internal name**
  - Column 2: Localised name
  - Column 3: Notes

- **can_access_market**
  - Column 2:
    ```text
    Can access International Market (
    Puppets
    and
    Overlords
    can always access each other's market)
    ```

- **can_be_spymaster**
  - Column 2: Can be Spy Master

- **can_boost_other_ideologies**
  - Column 2: Can boost popularity of other ideologies

- **can_boost_own_ideology**
  - Column 2: Can boost own party popularity in other countries

- **can_create_collaboration_government**
  - Column 2: Can create collaboration governments

- **can_create_factions**
  - Column 2: Can Create Factions

- **can_declare_war_on_same_ideology**
  - Column 2: Can declare war on country with the same ideology group without a war goal

- **can_declare_war_without_wargoal_when_in_war**
  - Column 2: Can declare war on a neighbor without a wargoal when at war with a major

- **can_decline_call_to_war**
  - Column 2: Can decline call to war

- **can_force_government**
  - Column 2: Can force government of another country to adopt the same ideology

- **can_generate_female_aces**
  - Column 2: Women in your country are allowed to become military pilots

- **can_generate_female_country_leaders**
  - Column 2: Can generate female country leaders

- **can_generate_female_unit_leaders**
  - Column 2: Can generate female unit leaders

- **can_guarantee_other_ideologies**
  - Column 2: Can guarantee other ideologies

- **can_join_factions**
  - Column 2: Can join factions

- **can_join_factions_not_allowed_diplomacy**
  - Column 2:
    ```text
    Country's name
    is not allowed to join factions
    ```

- **can_join_opposite_factions**
  - Column 2: Can Join Factions led by another Ideology

- **can_lower_tension**
  - Column 2: Lowers World Tension with Guarantees

- **can_not_build_buildings**
  - Column 2: CAN_NOT_BUILD_BUILDINGS
  - Column 3: Doesn't seem to work.

- **can_not_declare_war**
  - Column 2: Can not declare wars
  - Column 3: Prevents generating wargoals, but not using existing ones.

- **can_occupy_non_war**
  - Column 2: Can hold territory owned by a country they are not at war with

- **can_only_justify_war_on_threat_country**
  - Column 2: Can justify war goals against a country that have not generated world tension

- **can_puppet**
  - Column 2: Can puppet a country

- **can_send_volunteers**
  - Column 2: Can send volunteer forces

- **can_use_kamikaze_pilots**
  - Column 2: Can use kamikaze pilots

- **contributes_operatives**
  - Column 2: Contributes Operatives to Spy Master: Yes
  - Column 3: Only has an effect for subjects.

- **units_deployed_to_overlord**
  - Column 2: Control over deployed units go to overlord
  - Column 3: Only has an effect for subjects.

- **modifier** sets the modifier for the subject. All country [modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) can apply.
- **ai\_subject\_wants\_higher** decides whether or not the AI subject focuses on gaining a higher autonomy. If set to 0, AI will never gain an autonomy level through the autonomy system.
- **ai\_overlord\_wants\_lower** decides whether or not the AI overlord focuses on gaining a lower autonomy for the subject. If set to 0, AI will never decrease the autonomy level through the autonomy system.
- **ai\_overlord\_wants\_garrison** decides the triggers when the AI overlord garrisons the subject's territory as if it was their own land.
- **allowed** are the necessary triggers the subject must meet for the autonomy state to apply. The OVERLORD scope can be used to scope into the overlord.
- **use\_for\_peace\_conference\_weight** decides the chance for a potential overlord to puppet the country in the peace deal, where ROOT is the subject and FROM is the overlord.
- **can\_take\_level** sets the necessary triggers the subject must meet to be able to gain a level through the autonomy system.
- **can\_lose\_level** sets the necessary triggers the subject must meet for the overlord to be able to decrease the autonomy level through the autonomy system.
- **peace\_conference\_initial\_freedom** is the initial freedom level of the country that gets set to this autonomy after a peace conference on a scale from 0 to 1. If not specified, assumed to be 0.5.
- **allowed\_levels\_filter** decides which autonomy levels a country with this autonomous state can change to, alongside autonomy\_free. If not specified, all levels will be allowed.

## Icon

- **For loading GFX, the game uses the sprite system. Sprites are code definitions that attach a name to an image file, as well as optionally adding additional information, such as animation, the amount of frames, the way that the image will be loaded, and so on. This means**
  - Example:
    ```text
    spriteTypes = {
        spriteType = {
            name = GFX_first_sprite                         # In some cases, beginning with GFX_ is mandatory for it to work.
            texturefile = gfx/interface/folder/filename.dds # The folder and filename don't matter, as long as they are correct
        }                                                   # Only the forward slash '/' (can be doubled as '//') can be used to separate folders.
        spriteType = {                                      # The image doesn't have to be .dds, as .tga and .png are acceptable.
            name = GFX_second_sprite
            texturefile = gfx/interface/folder2/filename2.dds
            noOfFrames = 2 # Splits the image into 2 halves, which may be switched between dynamically in GUI
        }
    }
    ```

For the icon, the game will use a sprite named in the format of `GFX_<autonomy state>_icon`. An /Hearts of Iron IV/interface/\*.gfx file containing such a definition may look like the following:

```text
spriteTypes = {
    spriteType = {
        name = "GFX_autonomy_mod_new_icon"
        textureFile = "gfx/interface/autonomy/autonomy_mod_new_icon.dds"
    }
    spriteType = {
        name = "GFX_example_icon"
        texturefile = "another_folder/image_name.dds"
    }
}
```

## Localisation

The localisation is set in an .yml file in the localisation/ folder. Using the prior example of autonomy\_mod\_new, a localisation entry will look like `autonomy_mod_new:0 "Mod's new autonomy state"`

It is possible to set a country-specific entry. An entry with `GER_autonomy_mod_new:0 "New mod Germany"` will make Germany have that name if its autonomy level is autonomy\_mod\_new. Similarly, `ENG_FRA_autonomy_mod_new:0 "New mod French UK"` will make the United Kingdom have that name if its overlord is France and the autonomy state is autonomy\_mod\_new.

## Example

```text
autonomy_state = {
	id = autonomy_example
	
	default = yes					#Will be a possible option for peace deals
	is_puppet = yes
	
	use_overlord_color = yes
	
	min_freedom_level = 0.2				#Puts it as 0.2 on the autonomy level scale, which is the same as an integrated puppet.

	peace_conference_initial_freedom = 0.9		#Close to independence
	
	manpower_influence = 0.9
	
	rule = {
		can_not_declare_war = yes
		can_decline_call_to_war = no
		units_deployed_to_overlord = yes
		can_be_spymaster = no
		contributes_operatives = no
		can_create_collaboration_government = no
	}
	
	modifier = {
		autonomy_manpower_share = 1.0
		can_master_build_for_us = 1
		extra_trade_to_overlord_factor = 1.0
		overlord_trade_cost_factor = -0.9
		cic_to_overlord_factor = 0.75
		mic_to_overlord_factor = 0.75
		research_sharing_per_country_bonus_factor = -0.5
	}
	
	ai_subject_wants_higher = {
		factor = 0.0
	}
	
	ai_overlord_wants_lower = {
		factor = 0.0
	}

	allowed = {
		has_dlc = "Together for Victory"
		OVERLORD = {
			tag = FRA
		}
	}

	allowed_levels_filter = {
		autonomy_example
		autonomy_example_1
		autonomy_example_2
	}

	use_for_peace_conference_weight = {
		base = 0
		modifier = {
			add = 10
			FROM = {
				has_wargoal_against = { target = ROOT type = puppet_wargoal_focus }
			}			# Adds 10 to the chance if the overlord has a wargoal to puppet the country.
		}
		modifier = {
			factor = 2
			tag = ENG	# Multiplies the chance by 2 if the subject is UK.	
		}
	}

	can_take_level = {
		OVERLORD = {
			NOT = {
				controls_state = 123
			}	# If the overlord does not control state 123, the subject can gain a level.
		}
	}

	can_lose_level = {
		OVERLORD = {
			controls_state = 123
		}	# If the overlord controls state 123, it can decrease the subject's autonomy level.
	}
}
```

## Related defines

Certain [Defines](<Defines - Hearts of Iron 4 Wiki.md>) affect the autonomy system in a certain way. These are:

- **RESOURCE\_SENT\_AUTONOMY\_DAILY\_BASE** (0) Base autonomy gain from the overlord purchasing the subject's resources through trade.
- **RESOURCE\_SENT\_AUTONOMY\_DAILY\_FACTOR** (0.005) Autonomy gain multiplier from the overlord purchasing the subject's resources through trade.
- **WAR\_SCORE\_AUTONOMY\_BASE** (0) Base autonomy gain from the subject gaining war score in a war.
- **WAR\_SCORE\_AUTONOMY\_FACTOR** (0.6) Autonomy gain multiplier from the subject gaining war score in a war.
- **LL\_TO\_OVERLORD\_AUTONOMY\_DAILY\_BASE** (0) Base autonomy gain from the subject lend-leasing to the overlord.
- **LL\_TO\_OVERLORD\_AUTONOMY\_DAILY\_FACTOR** (0.05) Autonomy gain multiplier from the subject lend-leasing to the overlord.
- **LL\_TO\_PUPPET\_AUTONOMY\_DAILY\_BASE** (0) Base autonomy gain from the overlord lend-leasing to the subject. Must be negative in order to lose autonomy.
- **LL\_TO\_PUPPET\_AUTONOMY\_DAILY\_FACTOR** (-0.01) Autonomy gain multiplier from the overlord lend-leasing to the subject. Must be negative in order to lose autonomy.
- **AUTONOMY\_FREEDOM\_FROM\_CAPITULATE** (0.5) Upon the overlord capitulating, the subject receives a large gain to the autonomy progress.
- **ATTACHE\_TO\_SUBJECT\_EFFECT** (-0.05) Base autonomy gain from the overlord sending an attache to the subject. Must be negative in order to lose autonomy.
- **ATTACHE\_TO\_OVERLORD\_EFFECT** (0.05) Base autonomy gain from the subject sending an attache to the overlord.
- **AUTONOMY\_LEVEL\_CHANGE\_PP\_COST\_BASE** (50) The cost in political power to change between autonomy states.
- **AUTONOMY\_LEVEL\_CHANGE\_PP\_ANNEX** (300) The cost in political power to annex a subject.
- **AUTONOMY\_LEVEL\_CHANGE\_PP\_FREE** (300) The cost in political power to gain independence as a subject.
- **MAX\_SCORE\_DIFF\_TO\_CHANGE\_AUTONOMY** (10) The maximum difference between the current freedom score and the cap for the next or previous level allowed for changing.
- **MASTER\_BUILD\_AUTONOMY\_FACTOR** (-0.7) Autonomy gain multiplier from the overlord building in the subject's states. Must be negative in order to lose autonomy.
- **AUTONOMOUS\_TOTAL\_SCORE** (5000) The total amount of autonomy points between the country's annexation and independence.
- **AUTONOMOUS\_SPILLOVER** (0.025) The amount that can be saved between levels.

## Additional notes

When setting the autonomy level in the country's history file, it is possible that it will overwrite the party popularities and the ruling party of the subject. In order to prevent that to happening, it is recommended to scope into the overlord as

```text
TAG = {
	if = {
		limit = {
			has_dlc = "Together for Victory"
		}
		set_autonomy = {
			target = TAG2
			autonomy_state = autonomy_mod_new
		}
	}
	else = {
		puppet = TAG2
	}
}
```

in the subject's history file, also putting it before defining the ruling party and popularities. Alternatively, the order of tags in /Hearts of Iron IV/common/country\_tags/ can be changed so that the overlord is defined earlier than the subject.

If deciding to create a new autonomy system similar to Japan's unique autonomies, it is necessary to disable the default autonomy states so that they could not be used via `allowed = {}` in them or via `allowed_levels_filter = {}` in the new autonomies. Note that if you choose the second option, you would still need to disable the default autonomies so that they do not appear while puppeting.

If a new autonomy level should only be possible to be manually assigned via the `set_autonomy` [effect](<Effect - Hearts of Iron 4 Wiki.md>), then it's possible to set up allowed as such, using the autonomy state with the id of `autonomy_my_state`:

```text
allowed = {
    OR = {
        is_subject = no
        has_autonomy_state = autonomy_my_state
    }
}
```

That makes the autonomy state impossible to achieve through gaining or losing levels, as the `allowed` block is false if the subject has any other autonomy. This will ensure that `set_autonomy` will be possible to execute, *as long as the target country is independent at the time*, and that it wouldn't get cleared after being assigned, while it has that autonomy state.

When creating autonomy systems, avoid 2 different states having the same min\_freedom\_level.

## References

1. [↑](#cite-ref-1) `NDefines.NCountry.AUTONOMOUS_TOTAL_SCORE = 5000` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>).

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
