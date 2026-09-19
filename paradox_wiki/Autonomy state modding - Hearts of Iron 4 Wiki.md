# Autonomy state modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Autonomy state modding", captured 2026-09-19.*

## Table of contents

- [Arguments](#Arguments)
- [Icon](#Icon)
- [Localisation](#Localisation)
- [Example](#Example)
- [Related defines](#Related_defines)
- [Additional notes](#Additional_notes)
- [References](#References)

---

Different levels of the autonomy system are defined in `/Hearts of Iron IV/common/autonomous_states/*.txt`, and new ones can be created.

## Arguments <a id="Arguments"></a>

- **id** is the ID of the autonomy state, unique to each one. It is necessary to define to distinguish it from other autonomy states.
- **default**: If true, the game will attempt to make the 'puppet' option in peace deals as well as the 'puppet' effect use this autonomy state among other default autonomy states. By default, set to no.
- **is_puppet** decides whether the subject is a puppet or not, making is_puppet and is_puppet_of triggers true in that case. By default, set to no.
- **use_overlord_color** makes the subject have the same country color as the overlord.
- **min_freedom_level** decides the order in which autonomy states are placed. The autonomy states with lower freedom levels have less autonomy than those with higher when the game places the autonomy states for the subject to lose or gain a level. This also decides how many autonomy points the subject needs to gain or lose a level, calculated by the difference between freedom levels multiplied by 5000[1]. As such, it would take 500 points to go from an autonomous state with the min_freedom_level of 0.1 to being annexed.
- **manpower_influence** decides how large of a portion of the subject's manpower the overlord can use in colonial divisions.
- **rule** sets the game rules for the subject to either yes or no.

| Game rule list |
| --- |
| The following game rules exist as possible options:  - Internal name: can_access_market; Localised name: Can access International Market ( Puppets and Overlords can always access each other's market) - Internal name: can_be_spymaster; Localised name: Can be Spy Master - Internal name: can_boost_other_ideologies; Localised name: Can boost popularity of other ideologies - Internal name: can_boost_own_ideology; Localised name: Can boost own party popularity in other countries - Internal name: can_create_collaboration_government; Localised name: Can create collaboration governments - Internal name: can_create_factions; Localised name: Can Create Factions - Internal name: can_declare_war_on_same_ideology; Localised name: Can declare war on country with the same ideology group without a war goal - Internal name: can_declare_war_without_wargoal_when_in_war; Localised name: Can declare war on a neighbor without a wargoal when at war with a major - Internal name: can_decline_call_to_war; Localised name: Can decline call to war - Internal name: can_force_government; Localised name: Can force government of another country to adopt the same ideology - Internal name: can_generate_female_aces; Localised name: Women in your country are allowed to become military pilots - Internal name: can_generate_female_country_leaders; Localised name: Can generate female country leaders - Internal name: can_generate_female_unit_leaders; Localised name: Can generate female unit leaders - Internal name: can_guarantee_other_ideologies; Localised name: Can guarantee other ideologies - Internal name: can_join_factions; Localised name: Can join factions - Internal name: can_join_factions_not_allowed_diplomacy; Localised name: Country's name is not allowed to join factions - Internal name: can_join_opposite_factions; Localised name: Can Join Factions led by another Ideology - Internal name: can_lower_tension; Localised name: Lowers World Tension with Guarantees - Internal name: can_not_build_buildings; Localised name: CAN_NOT_BUILD_BUILDINGS; Notes: Doesn't seem to work. - Internal name: can_not_declare_war; Localised name: Can not declare wars; Notes: Prevents generating wargoals, but not using existing ones. - Internal name: can_occupy_non_war; Localised name: Can hold territory owned by a country they are not at war with - Internal name: can_only_justify_war_on_threat_country; Localised name: Can justify war goals against a country that have not generated world tension - Internal name: can_puppet; Localised name: Can puppet a country - Internal name: can_send_volunteers; Localised name: Can send volunteer forces - Internal name: can_use_kamikaze_pilots; Localised name: Can use kamikaze pilots - Internal name: contributes_operatives; Localised name: Contributes Operatives to Spy Master: Yes; Notes: Only has an effect for subjects. - Internal name: units_deployed_to_overlord; Localised name: Control over deployed units go to overlord; Notes: Only has an effect for subjects. |

- **modifier** sets the modifier for the subject. All country [modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) can apply.
- **ai_subject_wants_higher** decides whether or not the AI subject focuses on gaining a higher autonomy. If set to 0, AI will never gain an autonomy level through the autonomy system.
- **ai_overlord_wants_lower** decides whether or not the AI overlord focuses on gaining a lower autonomy for the subject. If set to 0, AI will never decrease the autonomy level through the autonomy system.
- **ai_overlord_wants_garrison** decides the triggers when the AI overlord garrisons the subject's territory as if it was their own land.
- **allowed** are the necessary triggers the subject must meet for the autonomy state to apply. The OVERLORD scope can be used to scope into the overlord.
- **use_for_peace_conference_weight** decides the chance for a potential overlord to puppet the country in the peace deal, where ROOT is the subject and FROM is the overlord.
- **can_take_level** sets the necessary triggers the subject must meet to be able to gain a level through the autonomy system.
- **can_lose_level** sets the necessary triggers the subject must meet for the overlord to be able to decrease the autonomy level through the autonomy system.
- **peace_conference_initial_freedom** is the initial freedom level of the country that gets set to this autonomy after a peace conference on a scale from 0 to 1. If not specified, assumed to be 0.5.
- **allowed_levels_filter** decides which autonomy levels a country with this autonomous state can change to, alongside autonomy_free. If not specified, all levels will be allowed.

## Icon <a id="Icon"></a>

| General sprite overview |
| --- |
| For loading GFX, the game uses the sprite system. Sprites are code definitions that attach a name to an image file, as well as optionally adding additional information, such as animation, the amount of frames, the way that the image will be loaded, and so on. This means **placing an image into the gfx folder isn't enough for it to work**, a sprite has to use that image file as well. Sprites are defined in any `/Hearts of Iron IV/interface/*.gfx` file (this is separate from `gfx/interface/`), opened with a text editor. To create a new .gfx file, a text file can be created and renamed to change the extension (on Windows, the Windows Explorer needs to show the extensions, which it doesn't by default). In particular, sprites are defined within a `spriteTypes = { ... }` block, as to separate from fonts and map arrows also defined in that folder, while the simplest sprite with the least mandatory properties is a `spriteType = { ... }`. The simplest sprite definition looks like the following: `spriteTypes = {`<br>`    spriteType = {`<br>`        name = GFX_first_sprite                         # In some cases, beginning with GFX_ is mandatory for it to work.`<br>`        texturefile = gfx/interface/folder/filename.dds # The folder and filename don't matter, as long as they are correct`<br>`    }                                                   # Only the forward slash '/' (can be doubled as '//') can be used to separate folders.`<br>`    spriteType = {                                      # The image doesn't have to be .dds, as .tga and .png are acceptable.`<br>`        name = GFX_second_sprite`<br>`        texturefile = gfx/interface/folder2/filename2.dds`<br>`        noOfFrames = 2 # Splits the image into 2 halves, which may be switched between dynamically in GUI`<br>`    }`<br>`}` In this case, this creates a sprite with the name of `GFX_first_sprite` and attaches the `/Hearts of Iron IV/gfx/interface/folder/filename.dds` image to it, and a second sprite similarly. The second sprite will be split into 2 frames: this is decided by having the left half of the image as the first frame and the right half as the second frame (more frames would further split the image horizontally). This doesn't make the sprite animated, just turns on the option to switch between the two halves as needed. `GFX_second_sprite:1` serves as a reference to the first frame, and GUI can be set up to change the shown frame depending on context, such as with radio stations.<br> In order to add animation, a [frameAnimatedSpriteType](<Graphical asset modding - Hearts of Iron 4 Wiki.md#frameAnimatedSpriteType>) is used.  **It's never mandatory to copy a base game file to change a sprite**. If there are duplicate definitions of a sprite with the same name in different files, the game will prioritise the one that would be [evaluated later, based on the filename](<Modding - Hearts of Iron 4 Wiki.md#Loading_files>), and the older sprite will be ignored in entirety. This can be ensured by beginning the replacement file's name with a symbol late in the ASCII character table. Typically the lowercase letter 'z' is used for this purpose. For example, to change the amount of frames in `GFX_idea_traits_strip` to 10, it is possible to define a sprite with that name with 10 frames in the mod's `modname/interface/zz_replace.gfx` file instead of copying over the base game file.<br> Since most .gfx files define integral parts of the user interface, copying them over can lead to the mod's loaded files missing sprites upon a major game update, which would appear in-game as the default image, which is the error dog by default. As to ease the burden of needing to check the interface files, it's best to never copy over .gfx files, unless more additions would be actively harmful to the mod, such as with `interface/subuniticons.gfx` |

For the icon, the game will use a sprite named in the format of `GFX_<autonomy state>_icon`. An `/Hearts of Iron IV/interface/*.gfx` file containing such a definition may look like the following:

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

## Localisation <a id="Localisation"></a>

The localisation is set in an .yml file in the localisation/ folder. Using the prior example of autonomy_mod_new, a localisation entry will look like `autonomy_mod_new:0 "Mod's new autonomy state"`

It is possible to set a country-specific entry. An entry with `GER_autonomy_mod_new:0 "New mod Germany"` will make Germany have that name if its autonomy level is autonomy_mod_new. Similarly, `ENG_FRA_autonomy_mod_new:0 "New mod French UK"` will make the United Kingdom have that name if its overlord is France and the autonomy state is autonomy_mod_new.

## Example <a id="Example"></a>

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

## Related defines <a id="Related_defines"></a>

Certain [Defines](<Defines - Hearts of Iron 4 Wiki.md>) affect the autonomy system in a certain way. These are:

- **RESOURCE_SENT_AUTONOMY_DAILY_BASE** (0) Base autonomy gain from the overlord purchasing the subject's resources through trade.
- **RESOURCE_SENT_AUTONOMY_DAILY_FACTOR** (0.005) Autonomy gain multiplier from the overlord purchasing the subject's resources through trade.
- **WAR_SCORE_AUTONOMY_BASE** (0) Base autonomy gain from the subject gaining war score in a war.
- **WAR_SCORE_AUTONOMY_FACTOR** (0.6) Autonomy gain multiplier from the subject gaining war score in a war.
- **LL_TO_OVERLORD_AUTONOMY_DAILY_BASE** (0) Base autonomy gain from the subject lend-leasing to the overlord.
- **LL_TO_OVERLORD_AUTONOMY_DAILY_FACTOR** (0.05) Autonomy gain multiplier from the subject lend-leasing to the overlord.
- **LL_TO_PUPPET_AUTONOMY_DAILY_BASE** (0) Base autonomy gain from the overlord lend-leasing to the subject. Must be negative in order to lose autonomy.
- **LL_TO_PUPPET_AUTONOMY_DAILY_FACTOR** (-0.01) Autonomy gain multiplier from the overlord lend-leasing to the subject. Must be negative in order to lose autonomy.
- **AUTONOMY_FREEDOM_FROM_CAPITULATE** (0.5) Upon the overlord capitulating, the subject receives a large gain to the autonomy progress.
- **ATTACHE_TO_SUBJECT_EFFECT** (-0.05) Base autonomy gain from the overlord sending an attache to the subject. Must be negative in order to lose autonomy.
- **ATTACHE_TO_OVERLORD_EFFECT** (0.05) Base autonomy gain from the subject sending an attache to the overlord.
- **AUTONOMY_LEVEL_CHANGE_PP_COST_BASE** (50) The cost in political power to change between autonomy states.
- **AUTONOMY_LEVEL_CHANGE_PP_ANNEX** (300) The cost in political power to annex a subject.
- **AUTONOMY_LEVEL_CHANGE_PP_FREE** (300) The cost in political power to gain independence as a subject.
- **MAX_SCORE_DIFF_TO_CHANGE_AUTONOMY** (10) The maximum difference between the current freedom score and the cap for the next or previous level allowed for changing.
- **MASTER_BUILD_AUTONOMY_FACTOR** (-0.7) Autonomy gain multiplier from the overlord building in the subject's states. Must be negative in order to lose autonomy.
- **AUTONOMOUS_TOTAL_SCORE** (5000) The total amount of autonomy points between the country's annexation and independence.
- **AUTONOMOUS_SPILLOVER** (0.025) The amount that can be saved between levels.

## Additional notes <a id="Additional_notes"></a>

For a country to start the game as a subject, this can be done using the [set_autonomy](<Effects - Hearts of Iron 4 Wiki.md>) effect in the history files. When doing this, it is preferable to do it in the subject's history file scoping to the overlord's tag, as shown below.

```text
TAG = {
    set_autonomy = {
        target = TAG2
        autonomy_state = autonomy_mod_new
    }
}
```

Autonomy effects are known to overwrite the political setup of a country, both in terms of leaders, ruling party and popularities. Therefore it has to be placed in the lines before recruiting characters and defining politics. Setting the autonomy level in the overlord's history file is one of the main sources of issues of ideologies being incorrect, due to the overwriting political definitions for the same reason. This happens due to the loading order, **but it is not recommended to make changes to the countries' loading order for this purpose.**

If deciding to create a new autonomy system similar to Japan's unique autonomies, it is necessary to disable the default autonomy states so that they could not be used via `allowed = {}` in them or via `allowed_levels_filter = {}` in the new autonomies. Note that if you choose the second option, you would still need to disable the default autonomies so that they do not appear while puppeting.

If a new autonomy level should only be possible to be manually assigned via the `set_autonomy` [effect](<Effects - Hearts of Iron 4 Wiki.md>), then it's possible to set up allowed as such, using the autonomy state with the id of `autonomy_my_state`:

```text
allowed = {
    OR = {
        is_subject = no
        has_autonomy_state = autonomy_my_state
    }
}
```

That makes the autonomy state impossible to achieve through gaining or losing levels, as the `allowed` block is false if the subject has any other autonomy. This will ensure that `set_autonomy` will be possible to execute, *as long as the target country is independent at the time*, and that it wouldn't get cleared after being assigned, while it has that autonomy state.

When creating autonomy systems, avoid 2 different states having the same min_freedom_level.

## References <a id="References"></a>

1. ↑ `NDefines.NCountry.AUTONOMOUS_TOTAL_SCORE = 5000` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>).

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
