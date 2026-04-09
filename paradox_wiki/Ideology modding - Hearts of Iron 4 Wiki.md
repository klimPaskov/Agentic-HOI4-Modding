# Table of contents

- [Ideologies](#ideologies)
- [Ai peace](#ai-peace)
- [Getting the ideology in your game](#getting-the-ideology-in-your-game)
  - [Localisation](#localisation)
  - [GFX](#gfx)
  - [Country history](#country-history)
  - [Political advisor](#political-advisor)


---

Ideologies represent all of the different political beliefs or alignments in the selected nation. An ideology will help to determine the choices and paths that the nation will take.

Ideologies are found in /Hearts of Iron IV/common/ideologies/\*.txt.

## Ideologies

An ideology definition follows this format:

```text
ideologies = {
	
	anarchist = {
	
		types = {
			anarcho_syndicalism = { # Used when assigning ideologies to leaders. Eg. democratic has conservatism, liberalism, and socialism. One value can be defined (yes/no).
				can_be_randomly_selected = no # If no, the subideology will not be randomly selected when creating a new random leader.
				color = { 169 42 42 } # Optional - if not specified, the subideology has the color of its ideology.
			}
		}
		
		dynamic_faction_names = {
			"FACTION_NAME_ANARCHIST_1" # Faction names used by the ai when an ai with this ideology creates a faction. Can be defined in any localisation file.
		}
		
		color = { 169 42 42 } # RGB ideology colour, used in the political pie chart or next to the chart. Can be overwritten in a subideology.
		
		rules = { # Rules for the ideology.  (yes/no)
                        can_create_collaboration_government = # Can create a collaboration government
			can_declare_war_on_same_ideology = # Declare war on same ideology. Not required
			can_force_government = # Can change ideology in peace deal. Required
			can_send_volunteers = # Can send volunteers. Required
			can_puppet = # Can puppet a nation at peace deal. Required
			can_lower_tension = # Lowers tension at peace deal. Not required
			can_only_justify_war_on_threat_country = # Can only justify on a nation that has generated world tension/threat. Not required
			can_guarantee_other_ideologies = # Can guarantee nations with different ideologies. Not required
		}

                can_host_government_in_exile = no #Can host a government in exile
		
		war_impact_on_world_tension = 0.2 # Goes from -1 to 1. Increases or decreases the world tension created by this nation
		faction_impact_on_world_tension = 0.3 # Goes from -1 to 1. Increases or decreases a faction of this ideologies impact on tension
		
		modifiers = { # More rules for the ideology. Every country [[Modifiers|modifier]] can apply.
			generate_wargoal_tension = # Required world tension to start justifying a war (0 to 1)
			join_faction_tension = # Required world tension to join a faction (0 to 1)
			lend_lease_tension = # Required tension to start a lend-lease (0 to 1)
			send_volunteers_tension = # Required tension to send volunteers (0 to 1)
			guarantee_tension = # Required tension to guarantee a nation (0 to 1)
			take_states_cost_factor = # Changes the cost of states in a peace deal. 0.25 would increase state cost by 25% (-1 to 1)
			annex_cost_factor = # Changes the cost of entirely annexing a nation in a peace deal. 0.5 would increase annexing cost by 50% (-1 to 1)
			justify_war_goal_when_in_major_war_time = # Changes the cost of justifying a war while in a major war. 0.5 would decrease time by 50% (0 to 1)
			drift_defence_factor = # Natural drift defence for the ideology # 0.3 would grant 30% drift defence (-1 to 1)
			puppet_cost_factor = # Changes the cost of puppeting a nation in a peace deal (-1 to 1)
		}

		can_be_boosted = no # Can you boost this ideologies popularity in another country (yes/no)
		can_collaborate = yes # Can create collaboration governments
		
		faction_modifiers = {    # Applies to the entire faction if the faction leader has this ideology. Every country [[Modifiers|modifier]] can apply.
			faction_trade_opinion_factor = 0.50 #plus 50% trade opinion
		}
		ai_<ideology> = yes # Determines what ai this ideology will use (democratic, communism, fascism, neutral)
	}
}
```

## Ai peace

AI peace determines the AI's behaviour in a peace deal. The triggers can be seen inside of enable = {} in the files, and they are generally reliant on ideologies.

The files are located in /Hearts of Iron IV/common/ai\_peace/\*.txt and every ideology has its own file. Unless the triggers are adjusted, AI will be likely to use /Hearts of Iron IV/common/ai\_peace/1\_fascist.txt. It is recommended to change the triggers in these files to assign a proper peace AI to the ideology or to create a new file.

## Getting the ideology in your game

### Localisation

The names, descriptions and nouns for ideologies are defined in any /Hearts of Iron IV/localisation/english/\*.yml file, assuming the English language. By default, the base game uses `parties_l_english.yml`  
An ideology has 3 localisation keys: for its name as an adjective matching the ideology's name, for its name as a noun where \_noun is appended, and for its description, used primarily in the country selection menu, where \_desc is appended. Taking an ideology with the name of `my_ideology` as an example, these will look like the following:

```text
my_ideology:0 "My ideologic"
my_ideology_noun:0 "My ideology"
my_ideology_desc:0 "Ideological regime" # Must be short: only shows up in the scenario/bookmark selection screen where it should take up one line.
```

Ideology types are localised similarly, but with just the noun and description:

```text
my_subideology:0 "My ideology type" # Noun
my_subideology_desc:0 "My ideology type's description" # Shows up when hovering over an ideology icon in-game
```

Prefacing a description entry with the country's tag will make it country-specific, as `POL_my_subideology_desc:0 "Description for my_subideology that shows up only for Poland."`

Similarly, each country has ideological names:

```text
TAG_my_ideology:0 "Ideological Country"
TAG_my_ideology_ADJ:0 "Ideological" #Adjective
TAG_my_ideology_DEF:0 "the Ideological Country" #Used to say if the country's name must be prefixed with "the". Leave "the" lowercase, if adding one.
TAG_my_subideology:0 "Sub-ideological Country" #Shows up if the country has the specified ideology type. For instance, "TUR_liberalism" will be used if TUR has a leader with the liberalism ideology type.
```

If you do not define the ideology and just leave it as `TAG:0 "Test"`, it will apply to the country regardless of the ideology unless an ideology-specific name takes priority. This name is also used for the collaboration governments, referenced in localisation as `[GetNonIdeologyName]` or, specifically for cosmetic tags, as `$NONIDEOLOGY$`.

Note that you will also have to add localisation for your ideology's drift. The base game uses /Hearts of Iron IV/localisation/english/modifiers\_l\_english.yml for this.

```text
my_ideology_drift:0 "Daily Ideology Support"
```

### GFX

*See also: [Country creation § Flag](<Country creation - Hearts of Iron 4 Wiki.md#flag>)*

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

Ideology icons are defined as sprites in any /Hearts of Iron IV/interface/\*.gfx file, with the name of the sprite determining when it will be used.  
For entire ideology groups, the sprite naming pattern must be of the sort `name = GFX_ideology_<name>_group`. If some ideology type within `types = { ... }` of the group should have a unique icon, it will be defined as `name = GFX_ideology_<name>`.

It is possible to make a sprite get used only for a certain country by prepending the country tag before the ideology's name (separated with underscores), as `GFX_ideology_<TAG>_<name>_group` for ideology groups and `GFX_ideology_<TAG>_<name>` for ideology types.

Example interface file defining ideology sprites:

```text
spriteTypes = {
    spriteType = {
        name = GFX_ideology_monarchism_group # Will be used for the "monarchism" group.
        texturefile = gfx/interface/ideologies/monarchism_group.dds
    }
    spriteType = {
        name = GFX_ideology_BHR_monarchism_group # Will be used for the "monarchism" group for the country BHR
        texturefile = gfx/interface/ideologies/BHR_monarchism_group.dds
    }
    spriteType = {
        name = GFX_ideology_absolutism # Will be used for the "absolutism" type, possibly within the "monarchism" group.
        texturefile = gfx/interface/ideologies/absolutism.dds
    }
    spriteType = {
        name = GFX_ideology_BHR_absolutism # Will be used for the "absolutism" type for the country BHR
        texturefile = gfx/interface/ideologies/BHR_absolutism.dds
    }
}
```

### Country history

If you want the ideology to appear in a country you will have to add it like this to a countries history file like this: In France, for example
/Hearts of Iron IV/history/countries/FRA - France.txt

```text
set_politics = {
	ruling_party = democratic
	last_election = "1932.5.1"
	election_frequency = 48
	elections_allowed = yes
}
set_popularities = { #This MUST add up to 100 otherwise the ideologies break
	democratic = 69
	fascism = 1
	communism = 30
}
```

France will now need a new leader

```text
create_country_leader = {
	name = "Édouard Daladier"
	desc = "POLITICS_ÉDOUARD_DALADIER_DESC"
	picture = "Portrait_France_Edouard_Daladier.dds"
	expire = "1965.1.1"
	ideology = socialism
	traits = {
		stout_defender
	}
}
```

### Political advisor

In order to add a political advisor increasing the popularity of the ideology, first, a trait that will be added to that advisor must be added in /Hearts of Iron IV/common/country\_leader/\*.txt

```text
<ideology>_booster = {
	random = no
	sprite = 13
	<ideology>_drift = 0.1
	
	ai_will_do = {
		factor = 0
	}
}
```

Localisation can be added like so:

```text
<ideology>_booster:0 "Ideology booster" #Whatever you want to call the person that supports the ideology. Eg. Democratic Politician, Communist Politician, Fascist Politician
```

It is recommended to add the generic advisors in /Hearts of Iron IV/common/ideas/zzz\_generic.txt to ensure the file is loaded after the country-specific ones. A generic advisor can be added following this example:

```text
 <name> = {
			
	allowed = {
		NOT = {
			has_available_idea_with_traits = { idea = <ideology>_booster limit = 1 }		#In order to prevent it from appearing alongside country-specific ones.
		}
	}	
	traits = { <ideology>_booster }
			
	available = {
		if = {
			limit = { has_dlc = "Man the Guns" }	
			NOT = { has_autonomy_state = autonomy_supervised_state }
		}
	}
	
	do_effect = {
		NOT = {
			has_government = <ideology> # You can only select it if your current ideology isn't your new one
		}
	}

	ai_will_do = {
		factor = 0
	}
}
```

More information about GFX and localisation can be found in the [Idea modding](<Idea modding - Hearts of Iron 4 Wiki.md>) page.

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
