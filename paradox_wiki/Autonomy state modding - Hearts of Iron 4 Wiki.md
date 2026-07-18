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

## <a id="arguments"></a>Arguments

- **id** is the ID of the autonomy state, unique to each one. It is necessary to define to distinguish it from other autonomy states.
- **default**: If true, the game will attempt to make the 'puppet' option in peace deals as well as the 'puppet' effect use this autonomy state among other default autonomy states. By default, set to no.
- **is\_puppet** decides whether the subject is a puppet or not, making is\_puppet and is\_puppet\_of triggers true in that case. By default, set to no.
- **use\_overlord\_color** makes the subject have the same country color as the overlord.
- **min\_freedom\_level** decides the order in which autonomy states are placed. The autonomy states with lower freedom levels have less autonomy than those with higher when the game places the autonomy states for the subject to lose or gain a level. This also decides how many autonomy points the subject needs to gain or lose a level, calculated by the difference between freedom levels multiplied by 5000<a id="cite-ref-1"></a>[[1]](#cite-note-1). As such, it would take 500 points to go from an autonomous state with the min\_freedom\_level of 0.1 to being annexed.
- **manpower\_influence** decides how large of a portion of the subject's manpower the overlord can use in colonial divisions.
- **rule** sets the game rules for the subject to either yes or no.
| Game rule list |
| --- |
| The following game rules exist as possible options: - Internal name; Localised name; Notes - <a id="can-access-market"></a> can\_access\_market; Can access International Market (Puppets and Overlords can always access each other's market);  - <a id="can-be-spymaster"></a> can\_be\_spymaster; Can be Spy Master;  - <a id="can-boost-other-ideologies"></a> can\_boost\_other\_ideologies; Can boost popularity of other ideologies;  - <a id="can-boost-own-ideology"></a> can\_boost\_own\_ideology; Can boost own party popularity in other countries;  - <a id="can-create-collaboration-government"></a> can\_create\_collaboration\_government; Can create collaboration governments;  - <a id="can-create-factions"></a> can\_create\_factions; Can Create Factions;  - <a id="can-declare-war-on-same-ideology"></a> can\_declare\_war\_on\_same\_ideology; Can declare war on country with the same ideology group without a war goal;  - <a id="can-declare-war-without-wargoal-when-in-war"></a> can\_declare\_war\_without\_wargoal\_when\_in\_war; Can declare war on a neighbor without a wargoal when at war with a major;  - <a id="can-decline-call-to-war"></a> can\_decline\_call\_to\_war; Can decline call to war;  - <a id="can-force-government"></a> can\_force\_government; Can force government of another country to adopt the same ideology;  - <a id="can-generate-female-aces"></a> can\_generate\_female\_aces; Women in your country are allowed to become military pilots;  - <a id="can-generate-female-country-leaders"></a> can\_generate\_female\_country\_leaders; Can generate female country leaders;  - <a id="can-generate-female-unit-leaders"></a> can\_generate\_female\_unit\_leaders; Can generate female unit leaders;  - <a id="can-guarantee-other-ideologies"></a> can\_guarantee\_other\_ideologies; Can guarantee other ideologies;  - <a id="can-join-factions"></a> can\_join\_factions; Can join factions;  - <a id="can-join-factions-not-allowed-diplomacy"></a> can\_join\_factions\_not\_allowed\_diplomacy; Country's name is not allowed to join factions;  - <a id="can-join-opposite-factions"></a> can\_join\_opposite\_factions; Can Join Factions led by another Ideology;  - <a id="can-lower-tension"></a> can\_lower\_tension; Lowers World Tension with Guarantees;  - <a id="can-not-build-buildings"></a> can\_not\_build\_buildings; CAN\_NOT\_BUILD\_BUILDINGS; Doesn't seem to work. - <a id="can-not-declare-war"></a> can\_not\_declare\_war; Can not declare wars; Prevents generating wargoals, but not using existing ones. - <a id="can-occupy-non-war"></a> can\_occupy\_non\_war; Can hold territory owned by a country they are not at war with;  - <a id="can-only-justify-war-on-threat-country"></a> can\_only\_justify\_war\_on\_threat\_country; Can justify war goals against a country that have not generated world tension;  - <a id="can-puppet"></a> can\_puppet; Can puppet a country;  - <a id="can-send-volunteers"></a> can\_send\_volunteers; Can send volunteer forces;  - <a id="can-use-kamikaze-pilots"></a> can\_use\_kamikaze\_pilots; Can use kamikaze pilots;  - <a id="contributes-operatives"></a> contributes\_operatives; Contributes Operatives to Spy Master: Yes; Only has an effect for subjects. - <a id="units-deployed-to-overlord"></a> units\_deployed\_to\_overlord; Control over deployed units go to overlord; Only has an effect for subjects. |

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

## <a id="icon"></a>Icon
| General sprite overview |
| --- |
| For loading GFX, the game uses the sprite system. Sprites are code definitions that attach a name to an image file, as well as optionally adding additional information, such as animation, the amount of frames, the way that the image will be loaded, and so on. This means **placing an image into the gfx folder isn't enough for it to work**, a sprite has to use that image file as well. Sprites are defined in any /Hearts of Iron IV/interface/\*.gfx file (this is separate from gfx/interface/), opened with a text editor. To create a new .gfx file, a text file can be created and renamed to change the extension (on Windows, the [Windows Explorer needs to show the extensions, which it doesn't by default](https://support.microsoft.com/en-gb/windows/common-file-name-extensions-in-windows-da4a4430-8e76-89c5-59f7-1cdbbc75cb01)). In particular, sprites are defined within a `spriteTypes = { ... }` block, as to separate from fonts and map arrows also defined in that folder, while the simplest sprite with the least mandatory properties is a `spriteType = { ... }`. The simplest sprite definition looks like the following:   `spriteTypes = { spriteType = { name = GFX_first_sprite # In some cases, beginning with GFX_ is mandatory for it to work. texturefile = gfx/interface/folder/filename.dds # The folder and filename don't matter, as long as they are correct } # Only the forward slash '/' (can be doubled as '//') can be used to separate folders. spriteType = { # The image doesn't have to be .dds, as .tga and .png are acceptable. name = GFX_second_sprite texturefile = gfx/interface/folder2/filename2.dds noOfFrames = 2 # Splits the image into 2 halves, which may be switched between dynamically in GUI } }`   In this case, this creates a sprite with the name of `GFX_first_sprite` and attaches the /Hearts of Iron IV/gfx/interface/folder/filename.dds image to it, and a second sprite similarly. The second sprite will be split into 2 frames: this is decided by having the left half of the image as the first frame and the right half as the second frame (more frames would further split the image horizontally). This doesn't make the sprite animated, just turns on the option to switch between the two halves as needed. `GFX_second_sprite:1` serves as a reference to the first frame, and GUI can be set up to change the shown frame depending on context, such as with radio stations.  In order to add animation, a [frameAnimatedSpriteType](<Graphical asset modding - Hearts of Iron 4 Wiki.md#frameanimatedspritetype>) is used.  **It's never mandatory to copy a base game file to change a sprite**. If there are duplicate definitions of a sprite with the same name in different files, the game will prioritise the one that would be [evaluated later, based on the filename](<Modding - Hearts of Iron 4 Wiki.md#loading-files>), and the older sprite will be ignored in entirety. This can be ensured by beginning the replacement file's name with a symbol late in the ASCII character table. Typically the lowercase letter 'z' is used for this purpose. For example, to change the amount of frames in `GFX_idea_traits_strip` to 10, it is possible to define a sprite with that name with 10 frames in the mod's modname/interface/zz\_replace.gfx file instead of copying over the base game file.  Since most .gfx files define integral parts of the user interface, copying them over can lead to the mod's loaded files missing sprites upon a major game update, which would appear in-game as the default image, which is the error dog by default. As to ease the burden of needing to check the interface files, it's best to never copy over .gfx files, unless more additions would be actively harmful to the mod, such as with interface/subuniticons.gfx |

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

## <a id="localisation"></a>Localisation

The localisation is set in an .yml file in the localisation/ folder. Using the prior example of autonomy\_mod\_new, a localisation entry will look like `autonomy_mod_new:0 "Mod's new autonomy state"`

It is possible to set a country-specific entry. An entry with `GER_autonomy_mod_new:0 "New mod Germany"` will make Germany have that name if its autonomy level is autonomy\_mod\_new. Similarly, `ENG_FRA_autonomy_mod_new:0 "New mod French UK"` will make the United Kingdom have that name if its overlord is France and the autonomy state is autonomy\_mod\_new.

## <a id="example"></a>Example

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

## <a id="related-defines"></a>Related defines

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

## <a id="additional-notes"></a>Additional notes

For a country to start the game as a subject, this can be done using the [set\_autonomy](<Effects - Hearts of Iron 4 Wiki.md#set-autonomy>) effect in the history files. When doing this, it is preferable to do it in the subject's history file scoping to the overlord's tag, as shown below.

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

When creating autonomy systems, avoid 2 different states having the same min\_freedom\_level.

## <a id="references"></a>References

<a id="cite-note-1"></a>1. [↑](#cite-ref-1) `NDefines.NCountry.AUTONOMOUS_TOTAL_SCORE = 5000` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>).

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
