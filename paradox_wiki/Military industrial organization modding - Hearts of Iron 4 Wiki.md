# Table of contents

- [Warning](#warning)
- [Designing an MIO](#designing-an-mio)
  - [What can you mod?](#what-can-you-mod)
  - [Files and Folders](#files-and-folders)
  - [The Error Log](#the-error-log)
- [Full MIO](#full-mio)
  - [Layout](#layout)
  - [The Properties Explained](#the-properties-explained)
  - [Trait Layout](#trait-layout)
  - [Designing a trait](#designing-a-trait)
  - [Initial Trait](#initial-trait)
  - [Trait Properties Explained](#trait-properties-explained)
- [Delta MIO](#delta-mio)
- [Policies](#policies)
- [AI Bonus Weights](#ai-bonus-weights)
- [Appendix: Boni](#appendix-boni)
  - [Equipment Boni](#equipment-boni)
  - [Production Boni](#production-boni)
  - [Organization Boni](#organization-boni)
- [References](#references)


---

Military Industrial Organizations (MIOs) represent the applied research and development of your country.
They boost your research in their area of focus and modify the stats of equipment produced with their aid.

## Warning

Military Industrial Organizations and their policies are loaded only *when creating a new game.*
it is not possible to inject new MIOs/policies into an ongoing game - for development / test runs, you must always create a new game.

You can freely modify what boni a trait grants, what icon to use or the localization. Adding traits is also possible, but removing existing traits can lead to errors.

## Designing an MIO

### What can you mod?

Fundamentally, MIO modding has four aspects you can modify:

- A fully independent Military Industrial Organization (Full MIO or Archetype)
- A MIO modification, based on another MIO, adding, removing or changing traits granted (Delta MIO)
- A Policy that can be applied to MIOs (typically after reaching Level 6+)
- AI Bonus Weights, which governs how the AI will prioritize boni granted by traits

### Files and Folders

MIOs are defined in /Hearts of Iron IV/common/military\_industrial\_organization/organizations/, where you can place any number of MIOs in any number of txt files, encoded in UTF8 *without* a Byte Order Mark (BOM).
For example, the game itself comes with one default "generic organization" file, containing the baseline templates, then one for each TAG that has alterations / extensions to that baseline.

Policies are defined in /Hearts of Iron IV/common/military\_industrial\_organization/policies/, again allowing any number of policies in any number of txt files, encoded in UTF8 *without* a Byte Order Mark (BOM).

Finally, AI Bonus Weights are defined in /Hearts of Iron IV/common/military\_industrial\_organization/ai\_bonus\_weights/

In all three directories of the game you can find a "documentation.info" text file describing some of the thoughts of the designers and some guidance.

### The Error Log

While this is true for most aspects of modding, checking the error log has never been more critical than when modding MIOs:
The simple fact that most errors impact the start of a game, are unfixable once it is running and that MIOs affect the game in the long run make it simple to waste a lot of time only to have to reset after all.

You can find the error.log text file in "%userprofile%\Documents\Paradox Interactive\Hearts of Iron IV\logs".
Check it first after game start and browsing through the MIO menus (browsing the menus will trigger any errors associated with visibility filters).

## Full MIO

### Layout

```text
<MIO Name> = {
	# Optional Localization Key
	name = LOC_infernal_mio_tanks
	icon = GFX_key

	equipment_type = { <equipment type> <equipment type> }
	research_categories = { <research type> <research type> }

	# Mandatory. In Country Scope.
	allowed = <condition>
	# Optional. In MIO Scope. FROM = country.
	visible = <condition>
	# Optional. In MIO Scope. FROM = country.
	available = <condition>

	# Additional Events if desired
#	on_design_team_assigned_to_tech = { ... }
#	on_design_team_assigned_to_variant = { ... }
#	on_industrial_manufacturer_assigned = { ... }
#	on_tech_research_cancelled = { ... }
#	on_tech_research_completed = { ... }
#	on_industrial_manufacturer_unassigned = { ... }

	# Bonus to assigned research
	research_bonus = 0.2
	# How many tasks can the MIO perform simultaneously?
	task_capacity = 999

	# Provide custom AI weights to help the AI choose the right MIO
#	ai_will_do = {
#		...
#	}

	# As many headers as desired.
	tree_header_text = {
		text = "Label1" # Either plain text or localization key
		x = 0 # Just where on the header bar is the label placed. 0 = Leftmost, 9 = Rightmost
	}
	tree_header_text = {
		text = "Label2"
		x = 2
	}
	tree_header_text = {
		text = "Label3"
		x = 4
	}
	tree_header_text = {
		text = "LabelN"
		x = 8
	}

	initial_trait = <initial trait>

	trait = <trait>
	trait = <trait>
	trait = <trait>
	# ... as many more as needed
}
```

### The Properties Explained

- **name**
  - Mandatory?: false
  - Description: If provided, it will resolve the displayname of the MIO in the following order: 1. <tag>_<name> 2. <name>
  - Example: name = LOC_infernal_mio_tanks

- **icon**
  - Mandatory?: false
  - Description: The Icon to use for the MIO in the interface
  - Example: icon = GFX_idea_generic_tank_manufacturer_1

- **background**
  - Mandatory?: false
  - Description: The background image for the Details window. If not specified, one of standard backgrounds will be used based on supported equipment types
  - Example: background = GFX_key

- **equipment_type**
  - Mandatory?: true
  - Description: List of equipment types the MIO affects. Used to select which production lines the MIO can be applied to and what the various boni in the traits will affect
  - Example: equipment_type = { mio_cat_eq_all_light_tank mio_cat_eq_all_medium_tank }

- **research_categories**
  - Mandatory?: true
  - Description: List of research categories affected by the MIO.
  - Example: research_categories = { mio_cat_tech_light_armor_and_modules mio_cat_tech_medium_armor_and_modules }

- **allowed**
  - Mandatory?: true
  - Description:
    ```text
    The condition checked AT GAME START whether the MIO is applicable to a given country.
    At this time, some conditions do not yet apply - for example, the player has not yet taken control, so the "is_ai" condition is meaningless.
    ```
  - Example: allowed = { always = true }

- **visible**
  - Mandatory?: false
  - Description:
    ```text
    Whether the MIO is visible to the nation. Is evaluated in the MIO scope, the country is available in the FROM scope. An MIO must be visible
    and
    available for the AI to be able to use it.
    ```
  - Example: visible = { always = true }

- **available**
  - Mandatory?: false
  - Description:
    ```text
    Whether the MIO is available to the nation. Will be grayed out in the UI if not. Is evaluated in the MIO scope, the country is available in the FROM scope. An MIO must be visible
    and
    available for the AI to be able to use it.
    ```
  - Example: available = { always = true }

- **on_design_team_assigned_to_tech**
  - Mandatory?: false
  - Description: Event that triggers when the MIO is attached to a research project
  - Example: na

- **on_design_team_assigned_to_variant**
  - Mandatory?: false
  - Description: Event that triggers when the MIO is attached to a model in the ship/tank/aircraft designer
  - Example: na

- **on_industrial_manufacturer_assigned**
  - Mandatory?: false
  - Description: Event that triggers when the MIO is attached to a production line
  - Example: na

- **on_industrial_manufacturer_unassigned**
  - Mandatory?: false
  - Description: Event that triggers when unassigned from a production line
  - Example: na

- **on_tech_research_cancelled**
  - Mandatory?: false
  - Description: Event that triggers when the associated research is cancelled (be sure to add some deeply annoyed researches with crippling country penalties)
  - Example: na

- **on_tech_research_completed**
  - Mandatory?: false
  - Description: Event that triggers when the associated research is completed successfully
  - Example: na

- **research_bonus**
  - Mandatory?: false
  - Description: How much research % bonus the MIO grants by default to associated research. Defaults to the DESIGN_TEAM_RESEARCH_BONUS define value
  - Example: research_bonus = 0.2

- **task_capacity**
  - Mandatory?: false
  - Description: How many things the MIO can do in parallel. Defaults to the DEFAULT_INITIAL_TASK_CAPACITY define value
  - Example: task_capacity = 3

- **ai_will_do**
  - Mandatory?: false
  - Description: How the AI prioritizes using this MIO compared to alternatively available MIOs
  - Example: na

- **tree_header_text**
  - Mandatory?: false
  - Description: Can be provided multiple times. The headers shown above the trait tree in the MIO menu. "x" represents how far to the right it is placed with "0" being at the left border and "9" being as right as it goes. Text can be a localization key or the straight label.
  - Example:
    ```text
    tree_header_text = {
        text = my_flavor_text_loc_key
        x = 1
    }
    ```

- **initial_trait**
  - Mandatory?: true
  - Description: The initial trait the MIO has without having to invest anything into it.
  - Example: See "Trait Layout"

- **trait**
  - Mandatory?: true
  - Description: Can be repeated any number of times. The individual traits of the MIO that can be unlocked.
  - Example: See "Trait Layout"

### Trait Layout

```text
trait = {
	token = upgrade_1 # mandatory
	name = loc_key # optional

	icon = GFX_key # optional

	special_trait_background = yes # optional - default no

	parent = {
		traits = { parent traits }
		num_parents_needed = X
	}
	any_parent = { parent traits }
	all_parents = { parent traits}

	mutually_exclusive= { upgrade4 }

	position = { x=1 y=0 }
	relative_position_id = trait_token

	visible = <condition>
	available = <condition>

   	on_complete = <event>

	limit_to_equipment_type = { ... } # optional
	equipment_bonus = <boni>
	production_bonus = <boni>
	organization_modifier = <boni>

	ai_will_do = <modifier> # optional
}
```

### Designing a trait

As we can see from the layout, designing a trait comes to a few key steps:

- Metadata
- Conditions
- Placement and relationship with other traits
- Boni granted
- AI (usually omitted)

From a metadata perspective, the "token" is a unique name *within* the current MIO. You can keep it simple without worrying about conflicts with other MIOs.
A nice icon helps visually distinguish your trait. The easiest way to figure that one out is to search in "00\_generic\_organization.txt" for a trait that offers the same kind of boni as yours does and copy it from there.
The name is if you want to select a custom localization key (by default it's "<mio\_name>\_<trait\_token>").

Conditions are great to tie an MIO into the Focus tree of a nation. Use "available" for generic unlock conditions, while "visible" is great if the MIO is available in different situations. While for full TAG-based deltas, we would usually prefer going with a Delta MIO, consider the civil war situation in Spain, where you want to just replace one trait with another, depending on just which of the rebel factions - just define multiple traits on the same coordinates and switch between visibility.

Placement and relationship is where things easily get most complex. Fundamentally, you have a placement board of 10 slots wide and 5 high (you can go deeper, but then users have to scroll).
This makes X go from 0 to 9 and y from 0 to 4.
The parent settings determine the tree structure of your MIO. No parents means the trait can be picked right away - consider placing them at the top of your tree (y = 0) and build down from there. "any\_parent" offers "any one among these" kind of parent logic, "all\_parents" offers "every single one of them" kind of dependencies. The rarely seen plain "parent" node allows "at least X out of these" kinds of dependencies.
Mutual exclusion, finally, is great for making the player pick between two or more options, where they can't just grab *all* of them. Be sure to place this condition on *all* traits in the mutual exclusion set, otherwise the player can first pick the trait with the exclusion and then afterwards the other one.

Boni granted - a list of those below in the Appendix - allow you to define the actual benefits (and trade-offs) the trait grants.
These fall into three categories:

- Equipment: Effects that modify the equipment produced. This is what makes your tanks tougher, your ships faster and your fighters dodgier.
- Production: Effects that make production faster or cheaper, the line efficiency grow faster or to greater heights or conversion of equipment swifter.
- Organization: Effects that modify the MIO: Support more lines, greater research boni, faster growth, cheaper to assign, etc.

Finally, there's the AI, but best do not touch that unless you really want to.
Trait prioritization is best handled through how the AI weighs boni (see chapter below on how to mod that).

### Initial Trait

The initial trait you assign to a MIO differs in a few aspects:

- It has no position on the board
- It has no icon
- There is no decision to be made

In other words, most of the trait properties are not relevant to the initial trait. In fact, all properties are optional, but only these five matter at all:

- name: Localization key, overrides the default "<mio name>\_initial\_trait" key.
- limit\_to\_equipment\_type: Narrows the equipment bonus of the initial trait to just a sub-set of its equipment types
- equipment\_bonus: Boni granted to equipment
- production\_bonus: Boni granted to the production of the related equipment
- organization\_bonus: Boni granted to the MIO itself

### Trait Properties Explained

- **token**
  - Mandatory?: true
  - Description: System name of the trait. Must be provided, can be simple
  - Example:
    ```text
    token = gunnery_1
    ```

- **name**
  - Mandatory?: false
  - Description: Localization key, overwriting the default key of "<mio name>_<trait token>". If defined, the system will prioritize "<tag>_<trait name>" over "<trait name>"
  - Example:
    ```text
    name = my_MIO_gunnery_1_Name
    ```

- **icon**
  - Mandatory?: false
  - Description: Icon to use for your trait. Defaults to GFX_idea_unknown. Check the icons other traits with the same boni use.
  - Example:
    ```text
    icon = GFX_generic_mio_trait_icon_hg_attack
    ```

- **special_trait_background**
  - Mandatory?: false
  - Description: If yes, trait background will be golden to indicate an interesting trait. Defaults to "no".
  - Example:
    ```text
    special_trait_background = yes
    ```

- **parent**
  - Mandatory?: false
  - Description: Provide a custom trait dependency link. This allows setting conditions such as "Have at least 2 out of these traits." See "any_parent" or "all_parents" for simpler dependencies
  - Example:
    ```text
    parent = {
    	traits = {
    		gunnery_1 stealth_1 mines_1
    	}
    	num_parents_needed = 2
    }
    ```

- **any_parent**
  - Mandatory?: false
  - Description: Any one of the listed traits must already have been selected.
  - Example:
    ```text
    any_parent = { gunnery_1 stealth_1 }
    ```

- **all_parents**
  - Mandatory?: false
  - Description: Every single one of the listed traits must already have been selected.
  - Example:
    ```text
    all_parents = { gunnery_1 stealth_1 }
    ```

- **mutually_exclusive**
  - Mandatory?: false
  - Description: Have multiple traits exclude each other. Must be defined in each of the traits to work as expected.
  - Example:
    ```text
    mutually_exclusive = { heavy_guns_specialization }
    ```

- **position**
  - Mandatory?: true
  - Description:
    ```text
    Where on the board to place the trait. (x = 0 y = 0) is the upper-left corner, (x = 9 y = 4) is the lower right. It is possible (but not recommended) to go lower by using an y value greater than 4, but that requires the player to scroll and is not recommended.
    ```
  - Example:
    ```text
    position = { x = 0 y = 0 }
    ```

- **relative_position_id**
  - Mandatory?: false
  - Description:
    ```text
    By providing this setting, turn the "position"-provided coordinates into coordinates relative to the listed trait. "position = { x=0 y=1 }" would then become "directly beneath the parent trait"
    ```
  - Example:
    ```text
    relative_position_id = gunnery_1
    ```

- **visible**
  - Mandatory?: false
  - Description: Whether the trait is shown on the MIO traits menu. The condition executes in the current MIO's scope, the country is available in the FROM scope.
  - Example:
    ```text
    visible = {
    	FROM = { has_country_flag = <flag name> }
    }
    ```

- **available**
  - Mandatory?: false
  - Description: Whether the trait is available (or greyed out). Useful for tying MIOs into the Focus Tree. The condition executes in the current MIO's scope, the country is available in the FROM scope.
  - Example:
    ```text
    available = {
    	FROM = { has_completed_focus = <focus name> }
    }
    ```

- **on_complete**
  - Mandatory?: false
  - Description: Event that happens when the player selects the trait. Again, a way to integrate the MIO into the narrative of the country. The event executes in the current MIO's scope, the country is available in the FROM scope.
  - Example:
    ```text
    on_complete = {
    	FROM = { set_country_flag = <flag name> }
    }
    ```

- **limit_to_equipment_type**
  - Mandatory?: false
  - Description: By default, Equipment and Production boni apply to all equipment types supported by the MIO. This condition allows you to narrow it down to a smaller subset. Useful for specialization traits.
  - Example:
    ```text
    limit_to_equipment_type = { mio_cat_eq_all_light_tank }
    ```

- **equipment_bonus**
  - Mandatory?: false
  - Description: Actual improvements applied to all produced equipment the MIO applies to (unless further constrained through limit_to_equipment_type)
  - Example:
    ```text
    equipment_bonus = {
    	armor_value = -0.05
    	defense =-0.05
    	build_cost_ic = -0.03
    }
    ```

- **production_bonus**
  - Mandatory?: false
  - Description: Improvements applied to the production lines, such as accelerated efficiency gains, greater output or improved conversion rates.
  - Example:
    ```text
    production_bonus = {
    	production_efficiency_gain_factor = 0.15
    	production_resource_need_factor = -0.15
    }
    ```

- **organization_modifier**
  - Mandatory?: false
  - Description: Boni granted to the MIO itself, such as cheaper assignment, improved research boni or increased task limit.
  - Example:
    ```text
    organization_modifier = {
    	military_industrial_organization_research_bonus = 0.05
    }
    ```

- **ai_will_do**
  - Mandatory?: false
  - Description: Override the default prioritization weights the AI would usually apply to this trait, based on the boni given. Usually not recommended.
  - Example:
    ```text
    ai_will_do = {
    	base = 2
    	modifier = {
    		factor = 1.5
    		date > 1937.1.1
    	}
    }
    ```

## Delta MIO

TODO: Write

## Policies

- **name**
  - Mandatory?: false
  - Description:
    ```text
    Policy name.
    May use scripted localization, scope will be set with the country owning the policy.
    ```
  - Example:
    ```text
    name = loc_key
    ```

- **icon**
  - Mandatory?: false
  - Description: Icon to use for your policy.
  - Example:
    ```text
    icon = GFX_mio_policy_my_policy
    ```

- **cost**
  - Mandatory?: false
  - Description:
    ```text
    Attach cost in political power.
    Default is define
    DEFAULT INITIAL POLICY ATTACH COST
    "25".
    ```
  - Example:
    ```text
    cost = 10
    ```

- **cooldown**
  - Mandatory?: false
  - Description:
    ```text
    Cooldown in days after attaching a policy.
    Default is define
    DEFAULT INITIAL ATTACH POLICY COOLDOWN
    "180".
    ```
  - Example:
    ```text
    cooldown = 60
    ```

- **allowed**
  - Mandatory?: true
  - Description:
    ```text
    Evaluated when starting the game.
    If trigger returns false, the policy will never be considered later in-game.
    ```
  - Example:
    ```text
    allowed = { 
    	OR = {
    		has_mio_equipment_type = motorized
    		has_mio_equipment_type = mechanized
    	} 
    }
    ```

- **visible**
  - Mandatory?: false
  - Description:
    ```text
    Evaluated when displaying the policy screen.
    Default is "always = yes".
    ```
  - Example:
    ```text
    visible = { has_mio_size > 3 }
    ```

- **available**
  - Mandatory?: false
  - Description:
    ```text
    Evaluated when displaying the policy screen.
    Default is "always = yes".
    ```
  - Example:
    ```text
    available = { has_mio_size > 5}
    ```

- **equipment_bonus**
  - Mandatory?: false
  - Description:
    ```text
    Defines the bonus given when the policy is attached and the MIO is assigned to an equipment variant.
    Note: it's different from equipment_bonus in traits. Here you have to give the equipment group/category/archetype/type.
    ```
  - Example:
    ```text
    equipment_bonus = {
    	infantry_equipment = {
    		soft_attack = 0.1
    	}
    }
    ```

- **production_bonus**
  - Mandatory?: false
  - Description:
    ```text
    Defines the bonus given when the policy is attached and the MIO is assigned to a production line.
    Note: it's different from production_bonus in traits. Here you have to give the equipment group/category/archetype/type.
    ```
  - Example:
    ```text
    production_bonus = {
    	infantry_equipment = {
    		production_cost_factor = -0.1
    	}
    }
    ```

- **organization_modifier**
  - Mandatory?: false
  - Description: Defines modifiers that will apply on the MIOs.
  - Example:
    ```text
    organization_modifier = {
    	military_industrial_organization_research_bonus = 0.1
    }
    ```

- **on_add**
  - Mandatory?: false
  - Description: Effects executed when the policy is attached.
  - Example:
    ```text
    on_add = { ... }
    ```

- **on_remove**
  - Mandatory?: false
  - Description: Effects executed when the policy is un-attached.
  - Example:
    ```text
    on_remove = { ... }
    ```

- **ai_will_do**
  - Mandatory?: false
  - Description:
    ```text
    AI weight modifier for this policy.
    Note: this affects how likely AI is to spend PP on this policy.
    ```
  - Example:
    ```text
    ai_will_do = {
    	...
    }
    ```

## AI Bonus Weights

TODO: Write

## Appendix: Boni

### Equipment Boni

List of stats that can be used for different equipments.

**Tanks**

- **maximum_speed**

- **reliability**

- **defense**

- **breakthrough**

- **armor_value**

- **build_cost_ic**

- **entrenchment**

- **fuel_capacity**

**Ships**

- **lg_armor_piercing**

- **lg_attack**

- **hg_armor_piercing**

- **hg_attack**

- **torpedo_attack**

- **sub_attack**

- **anti_air_attack**

- **armor_value**

- **surface_detection**

- **sub_detection**

- **sub_visibility**

- **surface_visibility**

- **naval_speed**

- **reliability**

- **naval_range**

- **max_strength**

- **fuel_consumption**

- **build_cost_ic**

- **manpower**

- **naval_supremacy_factor**

- **naval_torpedo_enemy_critical_chance_factor**

- **naval_torpedo_damage_reduction_factor**

- **carrier_size**

- **mines_sweeping**

- **mines_planting**

- **naval_torpedo_hit_chance_factor**

- **naval_light_gun_hit_chance_factor**

- **naval_heavy_gun_hit_chance_factor**

**Planes**

- **air_superiority**

- **reliability**

- **naval_strike_attack**

- **naval_strike_targetting**

- **manpower**

- **fuel_consumption**

- **build_cost_ic**

- **resources**

- **thrust**

- **weight**

- **maximum_speed**

- **air_range**

- **air_agility**

- **air_attack**

- **air_defence**

- **surface_detection**

- **sub_detection**

- **air_ground_attack**

- **air_bombing**

- **mines_planting**

- **mines_sweeping**

- **night_penalty**

### Production Boni

All production boni apply to the production lines the MIO has been attached to.

- **production_cost_factor**
  - Description: Reduces the production cost.
  - Example: production_cost_factor = 0.05

- **production_capacity_factor**
  - Description: Increases the production output, accelerating the # items produced per day.
  - Example: production_capacity_factor = 0.1

- **production_efficiency_cap_factor**
  - Description: Increase the maximum production efficiency. Keep in mind, ships don't have that ...
  - Example: production_efficiency_cap_factor = 0.2

- **production_efficiency_gain_factor**
  - Description: Increase the rate, at which the production efficiency increases. Keep in mind, ships don't have that ...
  - Example: production_efficiency_gain_factor = 0.24

- **production_resource_need_factor**
  - Description: Change the amount of raw resources (Iron, Tungsten, Chromium, ...) needed.
  - Example: production_resource_need_factor = -0.1

- **production_resource_penalty_factor**
  - Description: Modify the penalty the production line suffers from not having enough resources.
  - Example: production_resource_penalty_factor = -0.1

- **production_conversion_speed_factor**
  - Description: Change the speed, at which equipment conversions are performed.
  - Example: production_conversion_speed_factor = 0.5

### Organization Boni

Organization Boni apply to the MIO globally and not to a specific equipment line / product.
As such they cannot be constrained.

- **military_industrial_organization_research_bonus**
  - Description: A flat increase to the research bonus percentage applied by the MIO. If previously it gave 20% bonus and receives a "0.1" bonus here, it will then give a 30% bonus to research.
  - Example: military_industrial_organization_research_bonus = 0.1

- **military_industrial_organization_design_team_assign_cost**
  - Description: Modifier over how much it costs to assign an MIO in the Tank/Aircraft/Ship designer.
  - Example: military_industrial_organization_design_team_assign_cost = -0.2

- **military_industrial_organization_design_team_change_cost**
  - Description: Modifier over how much it costs to pull the latest changes from an already assigned MIO for a given Tank/Aircraft/Ship design.
  - Example: military_industrial_organization_design_team_change_cost = -0.1

- **military_industrial_organization_industrial_manufacturer_assign_cost**
  - Description: How much does it cost to assign a MIO to an industrial (that is non-designer) production line.
  - Example: military_industrial_organization_industrial_manufacturer_assign_cost = -0.2

- **military_industrial_organization_task_capacity**
  - Description: Flat increase to the number of tasks an MOI can be assigned to in parallel.
  - Example: military_industrial_organization_task_capacity = 5

- **military_industrial_organization_size_up_requirement**
  - Description: Modifies the funds it takes to level up an MIO, effectively accelerating the rate at which you unlock traits. Consider applying this if you design a MIO with an above-average number of traits.
  - Example: military_industrial_organization_size_up_requirement = -0.1

- **military_industrial_organization_funds_gain**
  - Description: Modifies the rate at which funds are obtained, which are then used to level the MIO and unlock molre traits. Another lever to increase the levelling rate of an MIO.
  - Example: military_industrial_organization_funds_gain = 0.2

## References

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
