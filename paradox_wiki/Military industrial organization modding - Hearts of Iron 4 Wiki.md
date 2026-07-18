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

## <a id="warning"></a>Warning

Military Industrial Organizations and their policies are loaded only *when creating a new game.*
it is not possible to inject new MIOs/policies into an ongoing game - for development / test runs, you must always create a new game.

You can freely modify what boni a trait grants, what icon to use or the localization. Adding traits is also possible, but removing existing traits can lead to errors.

## <a id="designing-an-mio"></a>Designing an MIO

### <a id="what-can-you-mod-3f"></a><a id="what-can-you-mod"></a>What can you mod?

Fundamentally, MIO modding has four aspects you can modify:

- A fully independent Military Industrial Organization (Full MIO or Archetype)
- A MIO modification, based on another MIO, adding, removing or changing traits granted (Delta MIO)
- A Policy that can be applied to MIOs (typically after reaching Level 6+)
- AI Bonus Weights, which governs how the AI will prioritize boni granted by traits

### <a id="files-and-folders"></a>Files and Folders

MIOs are defined in /Hearts of Iron IV/common/military\_industrial\_organization/organizations/, where you can place any number of MIOs in any number of txt files, encoded in UTF8 *without* a Byte Order Mark (BOM).
For example, the game itself comes with one default "generic organization" file, containing the baseline templates, then one for each TAG that has alterations / extensions to that baseline.

Policies are defined in /Hearts of Iron IV/common/military\_industrial\_organization/policies/, again allowing any number of policies in any number of txt files, encoded in UTF8 *without* a Byte Order Mark (BOM).

Finally, AI Bonus Weights are defined in /Hearts of Iron IV/common/military\_industrial\_organization/ai\_bonus\_weights/

In all three directories of the game you can find a "documentation.info" text file describing some of the thoughts of the designers and some guidance.

### <a id="the-error-log"></a>The Error Log

While this is true for most aspects of modding, checking the error log has never been more critical than when modding MIOs:
The simple fact that most errors impact the start of a game, are unfixable once it is running and that MIOs affect the game in the long run make it simple to waste a lot of time only to have to reset after all.

You can find the error.log text file in "%userprofile%\Documents\Paradox Interactive\Hearts of Iron IV\logs".
Check it first after game start and browsing through the MIO menus (browsing the menus will trigger any errors associated with visibility filters).

## <a id="full-mio"></a>Full MIO

### <a id="layout"></a>Layout

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

### <a id="the-properties-explained"></a>The Properties Explained

Properties of a Full MIO
| Key | Mandatory? | Description | Example |
| --- | --- | --- | --- |
| name | false | If provided, it will resolve the displayname of the MIO in the following order: 1. <tag>\_<name> 2. <name> | name = LOC\_infernal\_mio\_tanks |
| icon | false | The Icon to use for the MIO in the interface | icon = GFX\_idea\_generic\_tank\_manufacturer\_1 |
| background | false | The background image for the Details window. If not specified, one of standard backgrounds will be used based on supported equipment types | background = GFX\_key |
| equipment\_type | true | List of equipment types the MIO affects. Used to select which production lines the MIO can be applied to and what the various boni in the traits will affect | equipment\_type = { mio\_cat\_eq\_all\_light\_tank mio\_cat\_eq\_all\_medium\_tank } |
| research\_categories | true | List of research categories affected by the MIO. | research\_categories = { mio\_cat\_tech\_light\_armor\_and\_modules mio\_cat\_tech\_medium\_armor\_and\_modules } |
| allowed | true | The condition checked AT GAME START whether the MIO is applicable to a given country. *At this time, some conditions do not yet apply - for example, the player has not yet taken control, so the "is\_ai" condition is meaningless.* | allowed = { always = true } |
| visible | false | Whether the MIO is visible to the nation. Is evaluated in the MIO scope, the country is available in the FROM scope. An MIO must be visible *and* available for the AI to be able to use it. | visible = { always = true } |
| available | false | Whether the MIO is available to the nation. Will be grayed out in the UI if not. Is evaluated in the MIO scope, the country is available in the FROM scope. An MIO must be visible *and* available for the AI to be able to use it. | available = { always = true } |
| on\_design\_team\_assigned\_to\_tech | false | Event that triggers when the MIO is attached to a research project | na |
| on\_design\_team\_assigned\_to\_variant | false | Event that triggers when the MIO is attached to a model in the ship/tank/aircraft designer | na |
| on\_industrial\_manufacturer\_assigned | false | Event that triggers when the MIO is attached to a production line | na |
| on\_industrial\_manufacturer\_unassigned | false | Event that triggers when unassigned from a production line | na |
| on\_tech\_research\_cancelled | false | Event that triggers when the associated research is cancelled (be sure to add some deeply annoyed researches with crippling country penalties) | na |
| on\_tech\_research\_completed | false | Event that triggers when the associated research is completed successfully | na |
| research\_bonus | false | How much research % bonus the MIO grants by default to associated research. Defaults to the DESIGN\_TEAM\_RESEARCH\_BONUS define value | research\_bonus = 0.2 |
| task\_capacity | false | How many things the MIO can do in parallel. Defaults to the DEFAULT\_INITIAL\_TASK\_CAPACITY define value | task\_capacity = 3 |
| ai\_will\_do | false | How the AI prioritizes using this MIO compared to alternatively available MIOs | na |
| tree\_header\_text | false | Can be provided multiple times. The headers shown above the trait tree in the MIO menu. "x" represents how far to the right it is placed with "0" being at the left border and "9" being as right as it goes. Text can be a localization key or the straight label. | `tree_header_text = { text = my_flavor_text_loc_key x = 1 }` |
| initial\_trait | true | The initial trait the MIO has without having to invest anything into it. | See "Trait Layout" |
| trait | true | Can be repeated any number of times. The individual traits of the MIO that can be unlocked. | See "Trait Layout" |

### <a id="trait-layout"></a>Trait Layout

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

### <a id="designing-a-trait"></a>Designing a trait

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

### <a id="initial-trait"></a>Initial Trait

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

### <a id="trait-properties-explained"></a>Trait Properties Explained

Properties of a trait
| Key | Mandatory? | Description | Example |
| --- | --- | --- | --- |
| token | true | System name of the trait. Must be provided, can be simple | `token = gunnery_1` |
| name | false | Localization key, overwriting the default key of "<mio name>\_<trait token>". If defined, the system will prioritize "<tag>\_<trait name>" over "<trait name>" | `name = my_MIO_gunnery_1_Name` |
| icon | false | Icon to use for your trait. Defaults to GFX\_idea\_unknown. Check the icons other traits with the same boni use. | `icon = GFX_generic_mio_trait_icon_hg_attack` |
| special\_trait\_background | false | If yes, trait background will be golden to indicate an interesting trait. Defaults to "no". | `special_trait_background = yes` |
| parent | false | Provide a custom trait dependency link. This allows setting conditions such as "Have at least 2 out of these traits." See "any\_parent" or "all\_parents" for simpler dependencies | `parent = { traits = { gunnery_1 stealth_1 mines_1 } num_parents_needed = 2 }` |
| any\_parent | false | Any one of the listed traits must already have been selected. | `any_parent = { gunnery_1 stealth_1 }` |
| all\_parents | false | Every single one of the listed traits must already have been selected. | `all_parents = { gunnery_1 stealth_1 }` |
| mutually\_exclusive | false | Have multiple traits exclude each other. Must be defined in each of the traits to work as expected. | `mutually_exclusive = { heavy_guns_specialization }` |
| position | true | Where on the board to place the trait. (x = 0 y = 0) is the upper-left corner, (x = 9 y = 4) is the lower right. It is possible (but not recommended) to go lower by using an y value greater than 4, but that requires the player to scroll and is not recommended. | `position = { x = 0 y = 0 }` |
| relative\_position\_id | false | By providing this setting, turn the "position"-provided coordinates into coordinates relative to the listed trait. "position = { x=0 y=1 }" would then become "directly beneath the parent trait" | `relative_position_id = gunnery_1` |
| visible | false | Whether the trait is shown on the MIO traits menu. The condition executes in the current MIO's scope, the country is available in the FROM scope. | `visible = { FROM = { has_country_flag = <flag name> } }` |
| available | false | Whether the trait is available (or greyed out). Useful for tying MIOs into the Focus Tree. The condition executes in the current MIO's scope, the country is available in the FROM scope. | `available = { FROM = { has_completed_focus = <focus name> } }` |
| on\_complete | false | Event that happens when the player selects the trait. Again, a way to integrate the MIO into the narrative of the country. The event executes in the current MIO's scope, the country is available in the FROM scope. | `on_complete = { FROM = { set_country_flag = <flag name> } }` |
| limit\_to\_equipment\_type | false | By default, Equipment and Production boni apply to all equipment types supported by the MIO. This condition allows you to narrow it down to a smaller subset. Useful for specialization traits. | `limit_to_equipment_type = { mio_cat_eq_all_light_tank }` |
| equipment\_bonus | false | Actual improvements applied to all produced equipment the MIO applies to (unless further constrained through limit\_to\_equipment\_type) | `equipment_bonus = { armor_value = -0.05 defense =-0.05 build_cost_ic = -0.03 }` |
| production\_bonus | false | Improvements applied to the production lines, such as accelerated efficiency gains, greater output or improved conversion rates. | `production_bonus = { production_efficiency_gain_factor = 0.15 production_resource_need_factor = -0.15 }` |
| organization\_modifier | false | Boni granted to the MIO itself, such as cheaper assignment, improved research boni or increased task limit. | `organization_modifier = { military_industrial_organization_research_bonus = 0.05 }` |
| ai\_will\_do | false | Override the default prioritization weights the AI would usually apply to this trait, based on the boni given. Usually not recommended. | `ai_will_do = { base = 2 modifier = { factor = 1.5 date > 1937.1.1 } }` |

## <a id="delta-mio"></a>Delta MIO

TODO: Write

## <a id="policies"></a>Policies

Properties of a policies
| Key | Mandatory? | Description | Example |
| --- | --- | --- | --- |
| name | false | Policy name. May use scripted localization, scope will be set with the country owning the policy. | `name = loc_key` |
| icon | false | Icon to use for your policy. | `icon = GFX_mio_policy_my_policy` |
| cost | false | Attach cost in political power. Default is define [DEFAULT INITIAL POLICY ATTACH COST](<Defines - Hearts of Iron 4 Wiki.md#default-initial-policy-attach-cost>) "25". | `cost = 10` |
| cooldown | false | Cooldown in days after attaching a policy. Default is define [DEFAULT INITIAL ATTACH POLICY COOLDOWN](<Defines - Hearts of Iron 4 Wiki.md#default-initial-attach-policy-cooldown>) "180". | `cooldown = 60` |
| allowed | true | Evaluated when starting the game. If trigger returns false, the policy will never be considered later in-game. | `allowed = { OR = { has_mio_equipment_type = motorized has_mio_equipment_type = mechanized } }` |
| visible | false | Evaluated when displaying the policy screen. Default is "always = yes". | `visible = { has_mio_size > 3 }` |
| available | false | Evaluated when displaying the policy screen. Default is "always = yes". | `available = { has_mio_size > 5}` |
| equipment\_bonus | false | Defines the bonus given when the policy is attached and the MIO is assigned to an equipment variant. Note: it's different from equipment\_bonus in traits. Here you have to give the equipment group/category/archetype/type. | `equipment_bonus = { infantry_equipment = { soft_attack = 0.1 } }` |
| production\_bonus | false | Defines the bonus given when the policy is attached and the MIO is assigned to a production line. Note: it's different from production\_bonus in traits. Here you have to give the equipment group/category/archetype/type. | `production_bonus = { infantry_equipment = { production_cost_factor = -0.1 } }` |
| organization\_modifier | false | Defines modifiers that will apply on the MIOs. | `organization_modifier = { military_industrial_organization_research_bonus = 0.1 }` |
| on\_add | false | Effects executed when the policy is attached. | `on_add = { ... }` |
| on\_remove | false | Effects executed when the policy is un-attached. | `on_remove = { ... }` |
| ai\_will\_do | false | AI weight modifier for this policy. Note: this affects how likely AI is to spend PP on this policy. | `ai_will_do = { ... }` |

## <a id="ai-bonus-weights"></a>AI Bonus Weights

TODO: Write

## <a id="appendix-boni"></a>Appendix: Boni

### <a id="equipment-boni"></a>Equipment Boni

List of stats that can be used for different equipments.

**Tanks**
| Modifier |
| --- |
| maximum\_speed |
| reliability |
| defense |
| breakthrough |
| armor\_value |
| build\_cost\_ic |
| entrenchment |
| fuel\_capacity |

**Ships**
| Modifier |
| --- |
| lg\_armor\_piercing |
| lg\_attack |
| hg\_armor\_piercing |
| hg\_attack |
| torpedo\_attack |
| sub\_attack |
| anti\_air\_attack |
| armor\_value |
| surface\_detection |
| sub\_detection |
| sub\_visibility |
| surface\_visibility |
| naval\_speed |
| reliability |
| naval\_range |
| max\_strength |
| fuel\_consumption |
| build\_cost\_ic |
| manpower |
| naval\_supremacy\_factor |
| naval\_torpedo\_enemy\_critical\_chance\_factor |
| naval\_torpedo\_damage\_reduction\_factor |
| carrier\_size |
| mines\_sweeping |
| mines\_planting |
| naval\_torpedo\_hit\_chance\_factor |
| naval\_light\_gun\_hit\_chance\_factor |
| naval\_heavy\_gun\_hit\_chance\_factor |

**Planes**
| Key |
| --- |
| air\_superiority |
| reliability |
| naval\_strike\_attack |
| naval\_strike\_targetting |
| manpower |
| fuel\_consumption |
| build\_cost\_ic |
| resources |
| thrust |
| weight |
| maximum\_speed |
| air\_range |
| air\_agility |
| air\_attack |
| air\_defence |
| surface\_detection |
| sub\_detection |
| air\_ground\_attack |
| air\_bombing |
| mines\_planting |
| mines\_sweeping |
| night\_penalty |

### <a id="production-boni"></a>Production Boni

All production boni apply to the production lines the MIO has been attached to.

Production Boni
| Key | Description | Example |
| --- | --- | --- |
| production\_cost\_factor | Reduces the production cost. | production\_cost\_factor = 0.05 |
| production\_capacity\_factor | Increases the production output, accelerating the # items produced per day. | production\_capacity\_factor = 0.1 |
| production\_efficiency\_cap\_factor | Increase the maximum production efficiency. Keep in mind, ships don't have that ... | production\_efficiency\_cap\_factor = 0.2 |
| production\_efficiency\_gain\_factor | Increase the rate, at which the production efficiency increases. Keep in mind, ships don't have that ... | production\_efficiency\_gain\_factor = 0.24 |
| production\_resource\_need\_factor | Change the amount of raw resources (Iron, Tungsten, Chromium, ...) needed. | production\_resource\_need\_factor = -0.1 |
| production\_resource\_penalty\_factor | Modify the penalty the production line suffers from not having enough resources. | production\_resource\_penalty\_factor = -0.1 |
| production\_conversion\_speed\_factor | Change the speed, at which equipment conversions are performed. | production\_conversion\_speed\_factor = 0.5 |

### <a id="organization-boni"></a>Organization Boni

Organization Boni apply to the MIO globally and not to a specific equipment line / product.
As such they cannot be constrained.

Organization Boni
| Key | Description | Example |
| --- | --- | --- |
| military\_industrial\_organization\_research\_bonus | A flat increase to the research bonus percentage applied by the MIO. If previously it gave 20% bonus and receives a "0.1" bonus here, it will then give a 30% bonus to research. | military\_industrial\_organization\_research\_bonus = 0.1 |
| military\_industrial\_organization\_design\_team\_assign\_cost | Modifier over how much it costs to assign an MIO in the Tank/Aircraft/Ship designer. | military\_industrial\_organization\_design\_team\_assign\_cost = -0.2 |
| military\_industrial\_organization\_design\_team\_change\_cost | Modifier over how much it costs to pull the latest changes from an already assigned MIO for a given Tank/Aircraft/Ship design. | military\_industrial\_organization\_design\_team\_change\_cost = -0.1 |
| military\_industrial\_organization\_industrial\_manufacturer\_assign\_cost | How much does it cost to assign a MIO to an industrial (that is non-designer) production line. | military\_industrial\_organization\_industrial\_manufacturer\_assign\_cost = -0.2 |
| military\_industrial\_organization\_task\_capacity | Flat increase to the number of tasks an MOI can be assigned to in parallel. | military\_industrial\_organization\_task\_capacity = 5 |
| military\_industrial\_organization\_size\_up\_requirement | Modifies the funds it takes to level up an MIO, effectively accelerating the rate at which you unlock traits. Consider applying this if you design a MIO with an above-average number of traits. | military\_industrial\_organization\_size\_up\_requirement = -0.1 |
| military\_industrial\_organization\_funds\_gain | Modifies the rate at which funds are obtained, which are then used to level the MIO and unlock molre traits. Another lever to increase the levelling rate of an MIO. | military\_industrial\_organization\_funds\_gain = 0.2 |

## <a id="references"></a>References

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
