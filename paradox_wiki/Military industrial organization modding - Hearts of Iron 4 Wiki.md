# Military industrial organization modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Military industrial organization modding", captured 2026-09-19.*

## Table of contents

- [Warning](#Warning)
- [Designing an MIO](#Designing_an_MIO)
  - [What can you mod?](#What_can_you_mod.3F)
  - [Files and Folders](#Files_and_Folders)
  - [The Error Log](#The_Error_Log)
- [Full MIO](#Full_MIO)
  - [Layout](#Layout)
  - [The Properties Explained](#The_Properties_Explained)
  - [Trait Layout](#Trait_Layout)
  - [Designing a trait](#Designing_a_trait)
  - [Initial Trait](#Initial_Trait)
  - [Trait Properties Explained](#Trait_Properties_Explained)
- [Delta MIO](#Delta_MIO)
- [Policies](#Policies)
- [AI Bonus Weights](#AI_Bonus_Weights)
- [Appendix: Boni](#Appendix:_Boni)
  - [Equipment Boni](#Equipment_Boni)
  - [Production Boni](#Production_Boni)
  - [Organization Boni](#Organization_Boni)
- [References](#References)

---

Military Industrial Organizations (MIOs) represent the applied research and development of your country.
They boost your research in their area of focus and modify the stats of equipment produced with their aid.

## Warning <a id="Warning"></a>

Military Industrial Organizations and their policies are loaded only *when creating a new game.*
it is not possible to inject new MIOs/policies into an ongoing game - for development / test runs, you must always create a new game.

You can freely modify what boni a trait grants, what icon to use or the localization. Adding traits is also possible, but removing existing traits can lead to errors.

## Designing an MIO <a id="Designing_an_MIO"></a>

### What can you mod? <a id="What_can_you_mod.3F"></a><a id="What_can_you_mod?"></a>

Fundamentally, MIO modding has four aspects you can modify:

- A fully independent Military Industrial Organization (Full MIO or Archetype)
- A MIO modification, based on another MIO, adding, removing or changing traits granted (Delta MIO)
- A Policy that can be applied to MIOs (typically after reaching Level 6+)
- AI Bonus Weights, which governs how the AI will prioritize boni granted by traits

### Files and Folders <a id="Files_and_Folders"></a>

MIOs are defined in `/Hearts of Iron IV/common/military_industrial_organization/organizations/`, where you can place any number of MIOs in any number of txt files, encoded in UTF8 *without* a Byte Order Mark (BOM).
For example, the game itself comes with one default "generic organization" file, containing the baseline templates, then one for each TAG that has alterations / extensions to that baseline.

Policies are defined in `/Hearts of Iron IV/common/military_industrial_organization/policies/`, again allowing any number of policies in any number of txt files, encoded in UTF8 *without* a Byte Order Mark (BOM).

Finally, AI Bonus Weights are defined in `/Hearts of Iron IV/common/military_industrial_organization/ai_bonus_weights/`

In all three directories of the game you can find a "documentation.info" text file describing some of the thoughts of the designers and some guidance.

### The Error Log <a id="The_Error_Log"></a>

While this is true for most aspects of modding, checking the error log has never been more critical than when modding MIOs:
The simple fact that most errors impact the start of a game, are unfixable once it is running and that MIOs affect the game in the long run make it simple to waste a lot of time only to have to reset after all.

You can find the error.log text file in "%userprofile%\Documents\Paradox Interactive\Hearts of Iron IV\logs".
Check it first after game start and browsing through the MIO menus (browsing the menus will trigger any errors associated with visibility filters).

## Full MIO <a id="Full_MIO"></a>

### Layout <a id="Layout"></a>

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

### The Properties Explained <a id="The_Properties_Explained"></a>

Properties of a Full MIO

| Key | Mandatory? | Description | Example |
| --- | --- | --- | --- |
| name | false | If provided, it will resolve the displayname of the MIO in the following order: 1. <tag>_<name> 2. <name> | name = LOC_infernal_mio_tanks |
| icon | false | The Icon to use for the MIO in the interface | icon = GFX_idea_generic_tank_manufacturer_1 |
| background | false | The background image for the Details window. If not specified, one of standard backgrounds will be used based on supported equipment types | background = GFX_key |
| equipment_type | true | List of equipment types the MIO affects. Used to select which production lines the MIO can be applied to and what the various boni in the traits will affect | equipment_type = { mio_cat_eq_all_light_tank mio_cat_eq_all_medium_tank } |
| research_categories | true | List of research categories affected by the MIO. | research_categories = { mio_cat_tech_light_armor_and_modules mio_cat_tech_medium_armor_and_modules } |
| allowed | true | The condition checked AT GAME START whether the MIO is applicable to a given country. *At this time, some conditions do not yet apply - for example, the player has not yet taken control, so the "is_ai" condition is meaningless.* | allowed = { always = true } |
| visible | false | Whether the MIO is visible to the nation. Is evaluated in the MIO scope, the country is available in the FROM scope. An MIO must be visible *and* available for the AI to be able to use it. | visible = { always = true } |
| available | false | Whether the MIO is available to the nation. Will be grayed out in the UI if not. Is evaluated in the MIO scope, the country is available in the FROM scope. An MIO must be visible *and* available for the AI to be able to use it. | available = { always = true } |
| on_design_team_assigned_to_tech | false | Event that triggers when the MIO is attached to a research project | na |
| on_design_team_assigned_to_variant | false | Event that triggers when the MIO is attached to a model in the ship/tank/aircraft designer | na |
| on_industrial_manufacturer_assigned | false | Event that triggers when the MIO is attached to a production line | na |
| on_industrial_manufacturer_unassigned | false | Event that triggers when unassigned from a production line | na |
| on_tech_research_cancelled | false | Event that triggers when the associated research is cancelled (be sure to add some deeply annoyed researches with crippling country penalties) | na |
| on_tech_research_completed | false | Event that triggers when the associated research is completed successfully | na |
| research_bonus | false | How much research % bonus the MIO grants by default to associated research. Defaults to the DESIGN_TEAM_RESEARCH_BONUS define value | research_bonus = 0.2 |
| task_capacity | false | How many things the MIO can do in parallel. Defaults to the DEFAULT_INITIAL_TASK_CAPACITY define value | task_capacity = 3 |
| ai_will_do | false | How the AI prioritizes using this MIO compared to alternatively available MIOs | na |
| tree_header_text | false | Can be provided multiple times. The headers shown above the trait tree in the MIO menu. "x" represents how far to the right it is placed with "0" being at the left border and "9" being as right as it goes. Text can be a localization key or the straight label. | *(example below)* |
| initial_trait | true | The initial trait the MIO has without having to invest anything into it. | See "Trait Layout" |
| trait | true | Can be repeated any number of times. The individual traits of the MIO that can be unlocked. | See "Trait Layout" |

**Example: tree_header_text**

```text
tree_header_text = {
    text = my_flavor_text_loc_key
    x = 1
}
```

### Trait Layout <a id="Trait_Layout"></a>

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

### Designing a trait <a id="Designing_a_trait"></a>

As we can see from the layout, designing a trait comes to a few key steps:

- Metadata
- Conditions
- Placement and relationship with other traits
- Boni granted
- AI (usually omitted)

From a metadata perspective, the "token" is a unique name *within* the current MIO. You can keep it simple without worrying about conflicts with other MIOs.
A nice icon helps visually distinguish your trait. The easiest way to figure that one out is to search in "00_generic_organization.txt" for a trait that offers the same kind of boni as yours does and copy it from there.
The name is if you want to select a custom localization key (by default it's "<mio_name>_<trait_token>").

Conditions are great to tie an MIO into the Focus tree of a nation. Use "available" for generic unlock conditions, while "visible" is great if the MIO is available in different situations. While for full TAG-based deltas, we would usually prefer going with a Delta MIO, consider the civil war situation in Spain, where you want to just replace one trait with another, depending on just which of the rebel factions - just define multiple traits on the same coordinates and switch between visibility.

Placement and relationship is where things easily get most complex. Fundamentally, you have a placement board of 10 slots wide and 5 high (you can go deeper, but then users have to scroll).
This makes X go from 0 to 9 and y from 0 to 4.
The parent settings determine the tree structure of your MIO. No parents means the trait can be picked right away - consider placing them at the top of your tree (y = 0) and build down from there. "any_parent" offers "any one among these" kind of parent logic, "all_parents" offers "every single one of them" kind of dependencies. The rarely seen plain "parent" node allows "at least X out of these" kinds of dependencies.
Mutual exclusion, finally, is great for making the player pick between two or more options, where they can't just grab *all* of them. Be sure to place this condition on *all* traits in the mutual exclusion set, otherwise the player can first pick the trait with the exclusion and then afterwards the other one.

Boni granted - a list of those below in the Appendix - allow you to define the actual benefits (and trade-offs) the trait grants.
These fall into three categories:

- Equipment: Effects that modify the equipment produced. This is what makes your tanks tougher, your ships faster and your fighters dodgier.
- Production: Effects that make production faster or cheaper, the line efficiency grow faster or to greater heights or conversion of equipment swifter.
- Organization: Effects that modify the MIO: Support more lines, greater research boni, faster growth, cheaper to assign, etc.

Finally, there's the AI, but best do not touch that unless you really want to.
Trait prioritization is best handled through how the AI weighs boni (see chapter below on how to mod that).

### Initial Trait <a id="Initial_Trait"></a>

The initial trait you assign to a MIO differs in a few aspects:

- It has no position on the board
- It has no icon
- There is no decision to be made

In other words, most of the trait properties are not relevant to the initial trait. In fact, all properties are optional, but only these five matter at all:

- name: Localization key, overrides the default "<mio name>_initial_trait" key.
- limit_to_equipment_type: Narrows the equipment bonus of the initial trait to just a sub-set of its equipment types
- equipment_bonus: Boni granted to equipment
- production_bonus: Boni granted to the production of the related equipment
- organization_bonus: Boni granted to the MIO itself

### Trait Properties Explained <a id="Trait_Properties_Explained"></a>

Properties of a trait

| Key | Mandatory? | Description | Example |
| --- | --- | --- | --- |
| token | true | System name of the trait. Must be provided, can be simple | `token = gunnery_1` |
| name | false | Localization key, overwriting the default key of "<mio name>_<trait token>". If defined, the system will prioritize "<tag>_<trait name>" over "<trait name>" | `name = my_MIO_gunnery_1_Name` |
| icon | false | Icon to use for your trait. Defaults to GFX_idea_unknown. Check the icons other traits with the same boni use. | `icon = GFX_generic_mio_trait_icon_hg_attack` |
| special_trait_background | false | If yes, trait background will be golden to indicate an interesting trait. Defaults to "no". | `special_trait_background = yes` |
| parent | false | Provide a custom trait dependency link. This allows setting conditions such as "Have at least 2 out of these traits." See "any_parent" or "all_parents" for simpler dependencies | *(example below)* |
| any_parent | false | Any one of the listed traits must already have been selected. | `any_parent = { gunnery_1 stealth_1 }` |
| all_parents | false | Every single one of the listed traits must already have been selected. | `all_parents = { gunnery_1 stealth_1 }` |
| mutually_exclusive | false | Have multiple traits exclude each other. Must be defined in each of the traits to work as expected. | `mutually_exclusive = { heavy_guns_specialization }` |
| position | true | Where on the board to place the trait. (x = 0 y = 0) is the upper-left corner, (x = 9 y = 4) is the lower right. It is possible (but not recommended) to go lower by using an y value greater than 4, but that requires the player to scroll and is not recommended. | `position = { x = 0 y = 0 }` |
| relative_position_id | false | By providing this setting, turn the "position"-provided coordinates into coordinates relative to the listed trait. "position = { x=0 y=1 }" would then become "directly beneath the parent trait" | `relative_position_id = gunnery_1` |
| visible | false | Whether the trait is shown on the MIO traits menu. The condition executes in the current MIO's scope, the country is available in the FROM scope. | *(example below)* |
| available | false | Whether the trait is available (or greyed out). Useful for tying MIOs into the Focus Tree. The condition executes in the current MIO's scope, the country is available in the FROM scope. | *(example below)* |
| on_complete | false | Event that happens when the player selects the trait. Again, a way to integrate the MIO into the narrative of the country. The event executes in the current MIO's scope, the country is available in the FROM scope. | *(example below)* |
| limit_to_equipment_type | false | By default, Equipment and Production boni apply to all equipment types supported by the MIO. This condition allows you to narrow it down to a smaller subset. Useful for specialization traits. | `limit_to_equipment_type = { mio_cat_eq_all_light_tank }` |
| equipment_bonus | false | Actual improvements applied to all produced equipment the MIO applies to (unless further constrained through limit_to_equipment_type) | *(example below)* |
| production_bonus | false | Improvements applied to the production lines, such as accelerated efficiency gains, greater output or improved conversion rates. | *(example below)* |
| organization_modifier | false | Boni granted to the MIO itself, such as cheaper assignment, improved research boni or increased task limit. | *(example below)* |
| ai_will_do | false | Override the default prioritization weights the AI would usually apply to this trait, based on the boni given. Usually not recommended. | *(example below)* |

**Example: parent**

```text
parent = {
	traits = {
		gunnery_1 stealth_1 mines_1
	}
	num_parents_needed = 2
}
```

**Example: visible**

```text
visible = {
	FROM = { has_country_flag = <flag name> }
}
```

**Example: available**

```text
available = {
	FROM = { has_completed_focus = <focus name> }
}
```

**Example: on_complete**

```text
on_complete = {
	FROM = { set_country_flag = <flag name> }
}
```

**Example: equipment_bonus**

```text
equipment_bonus = {
	armor_value = -0.05
	defense =-0.05
	build_cost_ic = -0.03
}
```

**Example: production_bonus**

```text
production_bonus = {
	production_efficiency_gain_factor = 0.15
	production_resource_need_factor = -0.15
}
```

**Example: organization_modifier**

```text
organization_modifier = {
	military_industrial_organization_research_bonus = 0.05
}
```

**Example: ai_will_do**

```text
ai_will_do = {
	base = 2
	modifier = {
		factor = 1.5
		date > 1937.1.1
	}
}
```

## Delta MIO <a id="Delta_MIO"></a>

TODO: Write

## Policies <a id="Policies"></a>

Properties of a policies

| Key | Mandatory? | Description | Example |
| --- | --- | --- | --- |
| name | false | Policy name.<br>May use scripted localization, scope will be set with the country owning the policy. | `name = loc_key` |
| icon | false | Icon to use for your policy. | `icon = GFX_mio_policy_my_policy` |
| cost | false | Attach cost in political power.<br>Default is define [DEFAULT INITIAL POLICY ATTACH COST](<Defines - Hearts of Iron 4 Wiki.md>) "25". | `cost = 10` |
| cooldown | false | Cooldown in days after attaching a policy.<br>Default is define [DEFAULT INITIAL ATTACH POLICY COOLDOWN](<Defines - Hearts of Iron 4 Wiki.md>) "180". | `cooldown = 60` |
| allowed | true | Evaluated when starting the game.<br>If trigger returns false, the policy will never be considered later in-game. | *(example below)* |
| visible | false | Evaluated when displaying the policy screen.<br>Default is "always = yes". | `visible = { has_mio_size > 3 }` |
| available | false | Evaluated when displaying the policy screen.<br>Default is "always = yes". | `available = { has_mio_size > 5}` |
| equipment_bonus | false | Defines the bonus given when the policy is attached and the MIO is assigned to an equipment variant.<br>Note: it's different from equipment_bonus in traits. Here you have to give the equipment group/category/archetype/type. | *(example below)* |
| production_bonus | false | Defines the bonus given when the policy is attached and the MIO is assigned to a production line.<br>Note: it's different from production_bonus in traits. Here you have to give the equipment group/category/archetype/type. | *(example below)* |
| organization_modifier | false | Defines modifiers that will apply on the MIOs. | *(example below)* |
| on_add | false | Effects executed when the policy is attached. | `on_add = { ... }` |
| on_remove | false | Effects executed when the policy is un-attached. | `on_remove = { ... }` |
| ai_will_do | false | AI weight modifier for this policy.<br>Note: this affects how likely AI is to spend PP on this policy. | *(example below)* |

**Example: allowed**

```text
allowed = {
	OR = {
		has_mio_equipment_type = motorized
		has_mio_equipment_type = mechanized
	}
}
```

**Example: equipment_bonus**

```text
equipment_bonus = {
	infantry_equipment = {
		soft_attack = 0.1
	}
}
```

**Example: production_bonus**

```text
production_bonus = {
	infantry_equipment = {
		production_cost_factor = -0.1
	}
}
```

**Example: organization_modifier**

```text
organization_modifier = {
	military_industrial_organization_research_bonus = 0.1
}
```

**Example: ai_will_do**

```text
ai_will_do = {
	...
}
```

## AI Bonus Weights <a id="AI_Bonus_Weights"></a>

TODO: Write

## Appendix: Boni <a id="Appendix:_Boni"></a>

### Equipment Boni <a id="Equipment_Boni"></a>

List of stats that can be used for different equipments.

**Tanks**

| Modifier |
| --- |
| maximum_speed |
| reliability |
| defense |
| breakthrough |
| armor_value |
| build_cost_ic |
| entrenchment |
| fuel_capacity |

**Ships**

| Modifier |
| --- |
| lg_armor_piercing |
| lg_attack |
| hg_armor_piercing |
| hg_attack |
| torpedo_attack |
| sub_attack |
| anti_air_attack |
| armor_value |
| surface_detection |
| sub_detection |
| sub_visibility |
| surface_visibility |
| naval_speed |
| reliability |
| naval_range |
| max_strength |
| fuel_consumption |
| build_cost_ic |
| manpower |
| naval_supremacy_factor |
| naval_torpedo_enemy_critical_chance_factor |
| naval_torpedo_damage_reduction_factor |
| carrier_size |
| mines_sweeping |
| mines_planting |
| naval_torpedo_hit_chance_factor |
| naval_light_gun_hit_chance_factor |
| naval_heavy_gun_hit_chance_factor |

**Planes**

| Key |
| --- |
| air_superiority |
| reliability |
| naval_strike_attack |
| naval_strike_targetting |
| manpower |
| fuel_consumption |
| build_cost_ic |
| resources |
| thrust |
| weight |
| maximum_speed |
| air_range |
| air_agility |
| air_attack |
| air_defence |
| surface_detection |
| sub_detection |
| air_ground_attack |
| air_bombing |
| mines_planting |
| mines_sweeping |
| night_penalty |

### Production Boni <a id="Production_Boni"></a>

All production boni apply to the production lines the MIO has been attached to.

Production Boni

| Key | Description | Example |
| --- | --- | --- |
| production_cost_factor | Reduces the production cost. | production_cost_factor = 0.05 |
| production_capacity_factor | Increases the production output, accelerating the # items produced per day. | production_capacity_factor = 0.1 |
| production_efficiency_cap_factor | Increase the maximum production efficiency. Keep in mind, ships don't have that ... | production_efficiency_cap_factor = 0.2 |
| production_efficiency_gain_factor | Increase the rate, at which the production efficiency increases. Keep in mind, ships don't have that ... | production_efficiency_gain_factor = 0.24 |
| production_resource_need_factor | Change the amount of raw resources (Iron, Tungsten, Chromium, ...) needed. | production_resource_need_factor = -0.1 |
| production_resource_penalty_factor | Modify the penalty the production line suffers from not having enough resources. | production_resource_penalty_factor = -0.1 |
| production_conversion_speed_factor | Change the speed, at which equipment conversions are performed. | production_conversion_speed_factor = 0.5 |

### Organization Boni <a id="Organization_Boni"></a>

Organization Boni apply to the MIO globally and not to a specific equipment line / product.
As such they cannot be constrained.

Organization Boni

| Key | Description | Example |
| --- | --- | --- |
| military_industrial_organization_research_bonus | A flat increase to the research bonus percentage applied by the MIO. If previously it gave 20% bonus and receives a "0.1" bonus here, it will then give a 30% bonus to research. | military_industrial_organization_research_bonus = 0.1 |
| military_industrial_organization_design_team_assign_cost | Modifier over how much it costs to assign an MIO in the Tank/Aircraft/Ship designer. | military_industrial_organization_design_team_assign_cost = -0.2 |
| military_industrial_organization_design_team_change_cost | Modifier over how much it costs to pull the latest changes from an already assigned MIO for a given Tank/Aircraft/Ship design. | military_industrial_organization_design_team_change_cost = -0.1 |
| military_industrial_organization_industrial_manufacturer_assign_cost | How much does it cost to assign a MIO to an industrial (that is non-designer) production line. | military_industrial_organization_industrial_manufacturer_assign_cost = -0.2 |
| military_industrial_organization_task_capacity | Flat increase to the number of tasks an MOI can be assigned to in parallel. | military_industrial_organization_task_capacity = 5 |
| military_industrial_organization_size_up_requirement | Modifies the funds it takes to level up an MIO, effectively accelerating the rate at which you unlock traits. Consider applying this if you design a MIO with an above-average number of traits. | military_industrial_organization_size_up_requirement = -0.1 |
| military_industrial_organization_funds_gain | Modifies the rate at which funds are obtained, which are then used to level the MIO and unlock molre traits. Another lever to increase the levelling rate of an MIO. | military_industrial_organization_funds_gain = 0.2 |

## References <a id="References"></a>

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
