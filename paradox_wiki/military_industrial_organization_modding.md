# Military industrial organization modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Military industrial organization modding", revision 76388, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="76388" sources="common/military_industrial_organization/ common/equipment_groups/mio_equipment_groups.txt common/technology_tags/00_technology.txt common/defines/00_defines.lua common/scripted_triggers/NOR_scripted_triggers.txt common/characters/GER.txt common/country_leader/00_traits.txt documentation/effects_documentation.md documentation/triggers_documentation.md documentation/modifiers_documentation.md localisation/english/military_industrial_organization_l_english.yml hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against the three `_documentation.md` files under `common/military_industrial_organization/`, all 55 `.txt` files in `organizations/` (552 MIO definitions), the 22 policies in `policies/`, `ai_bonus_weights/ai_bonus_weights.txt`, the MIO defines in `common/defines/`, the MIO effects, triggers and modifiers in `documentation/`, and `common/equipment_groups/mio_equipment_groups.txt`.
- Kit blocks added: folder and file facts, a key-by-key check of the MIO and trait tables, the `initial_trait` key fix, the Delta MIO section (`include`, `add_trait`, `override_trait`, `remove_trait`, `delete_included_values`, DLC gating as vanilla does it), policy checks, the AI Bonus Weights section, equipment stat, production and organisation bonus checks (with the funds, size and task capacity defines), and a runtime scripting list.
- Errors found in the wiki text: `documentation.info` files (now `_documentation.md`), `organization_bonus` (real key `organization_modifier`), `naval_supremacy_factor` (documented stat is `naval_dominance_factor`), a tank stat list missing six stats, and positive example values for cost factors that would raise the cost. The two "TODO: Write" sections are answered by kit blocks. `task_capacity` is a documented key that vanilla never writes, and `ENABLE_TASK_CAPACITY` is false.
- Gaps left: the AI scoring formula, how several `ai_bonus_weights` files merge, and what a repeated `trait = { token = ... }` inside a Delta MIO does are not documented. Nothing was run in the game.
<!-- kit:end id="review" -->

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
- [Kit: Scripting MIOs at runtime](#kit-mio-runtime)

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

<!-- kit:begin id="mio-files-notes" at="section:Files_and_Folders" -->
**Kit correction** The `documentation.info` files named above do not exist in 1.19.3. Each of the three folders holds a `_documentation.md` instead, and `organizations/_documentation.md` also lists the equipment stats a trait bonus can use. [vanilla-confirmed 1.19.3] `common/military_industrial_organization/organizations/_documentation.md`, `policies/_documentation.md`, `ai_bonus_weights/_documentation.md`.

**Kit addition** What the three folders hold in 1.19.3. All rows: [vanilla-confirmed 1.19.3] `common/military_industrial_organization/`.

| Folder | Content |
| --- | --- |
| `organizations/` | 55 `.txt` files with 552 top-level MIO definitions: `00_generic_organization.txt` (30 archetypes), one file per country tag, `00_DEBUG_organization.txt`, `mio.txt` (test MIOs, `allowed = { always = no }`) and `_template_organization.txt` (comments only). One shipped file is named `RAJ_GOE_organization .txt`, with a space before the extension. |
| `policies/` | `_air_policies.txt` (5 policies), `_general_policies.txt` (7), `_land_policies.txt` (5), `_navy_policies.txt` (5). |
| `ai_bonus_weights/` | the single file `ai_bonus_weights.txt`. |

The names an MIO refers to are defined elsewhere. `equipment_type` takes equipment types, archetypes, categories and equipment groups. [docs] `common/military_industrial_organization/organizations/_documentation.md`. The 24 `mio_cat_eq_*` groups that vanilla uses are in `common/equipment_groups/mio_equipment_groups.txt`. [vanilla-confirmed 1.19.3] `common/equipment_groups/mio_equipment_groups.txt`. `research_categories` takes technology categories that technologies list in `categories`; the 19 `mio_cat_*` tags are declared in `common/technology_tags/00_technology.txt` and attached to technologies such as those in `common/technologies/armor.txt`. [vanilla-confirmed 1.19.3] `common/technology_tags/00_technology.txt`. See [Equipment modding](<equipment_modding.md>) for equipment archetypes and groups, [Unit modding](<unit_modding.md>) for unit types and [Technology modding](<technology_modding.md>) for technology categories.

MIO names and trait names are localisation keys. A key prefixed with the owner's tag wins over the plain key: `localisation/english/military_industrial_organization_l_english.yml` has `GER_porsche_organization` and `MEX_GER_porsche_organization` side by side. [vanilla-confirmed 1.19.3] `localisation/english/military_industrial_organization_l_english.yml`.
<!-- kit:end id="mio-files-notes" -->

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

<!-- kit:begin id="mio-key-checks" at="section:The_Properties_Explained" -->
**Kit note** Key-by-key check of the table above. Counts are MIO definitions that write the key at MIO level, out of 552 in `organizations/`.

| Key | In 1.19.3 |
| --- | --- |
| `name` | Lookup is `<TAG>_<name>` first, then `<name>`, with TAG the tag of the MIO owner; the key may use scripted localisation with the MIO as scope. [docs] `organizations/_documentation.md`. Written in 113 definitions, mostly Delta MIOs that reuse another name: `GRE_royal_hellenic_naval_shipyard_bftb_organization` points at the key of its non-DLC twin. [vanilla-confirmed 1.19.3] `organizations/GRE_organization.txt`. |
| `icon` | Order is the `icon` value, then `GFX_<TAG>_<MIO token>`, then `GFX_<MIO token>`, then `GFX_idea_unknown`. [docs] `organizations/_documentation.md`. Written in 501 definitions. [vanilla-confirmed 1.19.3] `organizations/`. |
| `background` | Documented as the GFX key of the Details window background, with a standard background chosen by equipment type when absent. [docs] `organizations/_documentation.md`. No vanilla definition writes it. [vanilla-confirmed 1.19.3] 0 of 552. |
| `allowed` | Country scope. Evaluated once at game start for every country, including tags that do not exist yet; a true result creates an instance of the MIO for that country. [docs] `organizations/_documentation.md`. 551 definitions write it; the one that does not inherits it through `include`. [vanilla-confirmed 1.19.3] `organizations/mio.txt`. |
| `visible`, `available` | Both default to `always = yes`, run in MIO scope with `FROM` as the country, and the AI and script treat an MIO as enabled only when both are true. [docs] `organizations/_documentation.md`. Written in 101 and 250 definitions. The country is reached with `FROM`, with `owner` (`owner = { has_completed_focus = ... }` in `GRE_organization.txt`) or by its tag (`AFG = { has_country_flag = ... }` in `AFG_organization.txt`). [vanilla-confirmed 1.19.3] `organizations/`. |
| `equipment_type`, `research_categories` | Written in 62 and 52 definitions; the others inherit both from an archetype with `include`. A Delta MIO may replace `equipment_type` (`BEL_cockerill_shipyards_organization` does). [vanilla-confirmed 1.19.3] `organizations/BEL_organization.txt`. |
| `on_design_team_assigned_to_tech` and the five other `on_*` blocks | Documented as optional on-action effects that run in MIO scope with `FROM` as the country. [docs] `organizations/_documentation.md`. No vanilla definition uses any of them. [vanilla-confirmed 1.19.3] 0 of 552. |
| `research_bonus` | The default is the define `DESIGN_TEAM_RESEARCH_BONUS`, 0.05 in 1.19.3. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. Two definitions set it: `BUL_varna_naval_dockyard_organization` (0) and a test MIO in `mio.txt`. [vanilla-confirmed 1.19.3] `organizations/`. |
| `task_capacity` | A real, documented key: the number of tasks the MIO can run in parallel, with the default taken from the define `DEFAULT_INITIAL_TASK_CAPACITY`. [docs] `organizations/_documentation.md`. No vanilla definition writes it, which is why the page inventory could not find it in vanilla. The defines `ENABLE_TASK_CAPACITY = false` and `DEFAULT_INITIAL_TASK_CAPACITY = 0` ship in 1.19.3. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. With the switch off, `task_capacity`, the modifier `military_industrial_organization_task_capacity` and `add_mio_task_capacity` probably limit nothing. [unverified] **Needs a game run:** set `task_capacity = 1` on a test organisation with `ENABLE_TASK_CAPACITY` left false, and see whether a second task can still be assigned. |
| `ai_will_do` | MIO scope with `FROM` as the country. The result is a multiplier applied to the weights from `ai_bonus_weights`. [docs] `organizations/_documentation.md`. One vanilla MIO writes it, `SPR_hispano_suiza_organization`, as `factor = 1` plus a `modifier` block. [vanilla-confirmed 1.19.3] `organizations/SPR_organization.txt`. |
| `tree_header_text` | `x` is the column of the cell where the label is centred, and a decimal such as 1.2 centres it between two cells; there is room for one line of text. [docs] `organizations/_documentation.md`. Vanilla writes 178 of these blocks with values such as 0.11, 4.2, 6.5 and 8.97, so "0 to 9" is a range, not a list of integers. [vanilla-confirmed 1.19.3] `organizations/`. |
<!-- kit:end id="mio-key-checks" -->

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

<!-- kit:begin id="mio-initial-trait-fix" at="heading:Initial_Trait" -->
**Kit correction** The fifth key in the list below is `organization_modifier`, not `organization_bonus`. `organization_bonus` is not a key in the documentation or in any vanilla file. [docs] `common/military_industrial_organization/organizations/_documentation.md`. [vanilla-confirmed 1.19.3] 0 uses under `common/`. The documentation lists exactly five relevant keys for `initial_trait`: `name`, `limit_to_equipment_type`, `equipment_bonus`, `production_bonus` and `organization_modifier`; without `name` the default key is built from the token `initial_trait`. [docs] `common/military_industrial_organization/organizations/_documentation.md`. The 87 vanilla `initial_trait` blocks use those five keys and nothing else, apart from a stray `token` in two blocks that the engine presumably ignores. [vanilla-confirmed 1.19.3] `common/military_industrial_organization/organizations/`.
<!-- kit:end id="mio-initial-trait-fix" -->

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

<!-- kit:begin id="mio-trait-notes" at="section:Trait_Properties_Explained" -->
**Kit note** Checks of the trait table against the documentation and the 1,279 `trait`, `add_trait` and `override_trait` blocks in vanilla.

- Names and icons follow the same fallback chains as the MIO: a trait without `name` uses the key `<MIO token>_<trait token>`, preferring a `<TAG>_` prefixed version, and a trait without `icon` tries `GFX_<TAG>_<MIO token>_<trait token>`, `GFX_<MIO token>_<trait token>` and then `GFX_idea_unknown`. [docs] `organizations/_documentation.md`. 556 of 557 vanilla `add_trait` blocks set `name` explicitly. [vanilla-confirmed 1.19.3] `organizations/`.
- `parent` takes `traits = { ... }` and `num_parents_needed`, which defaults to 1. `any_parent` is the shorthand for 1 and `all_parents` the shorthand for "all of them". A trait that is not first in the tree needs at least one of the three. [docs] `organizations/_documentation.md`. Vanilla uses `all_parents` and `any_parent` throughout and writes `parent` in only 2 of the 1,279 blocks. [vanilla-confirmed 1.19.3] `organizations/`.
- `mutually_exclusive` must be written on every trait of the set, otherwise the player can take the excluded one second. [docs] `organizations/_documentation.md`.
- `position` is the absolute grid cell, with x=0 y=0 at the top left, unless `relative_position_id` is set, and then it is an offset from that trait. Two traits must not share a cell in one tree. [docs] `organizations/_documentation.md`. Vanilla absolute `y` runs 0 to 4, relative offsets run from -5 to 9, and values may be script constants, as in `position = { x=@tank_hoesch_X y=@tank_hoesch_Y }`. [vanilla-confirmed 1.19.3] `organizations/GER_organization.txt`.
- `visible` and `available` default to `always = yes`, run in MIO scope with `FROM` as the country, and the AI and script treat a trait as enabled only when both hold. [docs] `organizations/_documentation.md`.
- `on_complete` runs in MIO scope with `FROM` as the country, so country effects go inside `FROM = { ... }`: `GER_mio_trait_hoesch_facilities` sets a country flag this way. [vanilla-confirmed 1.19.3] `organizations/GER_organization.txt`.
- `limit_to_equipment_type` may only narrow the MIO's own `equipment_type` list, and equipment groups work there too. [docs] `organizations/_documentation.md`.
- `ai_will_do` on a trait overrides the weights of a "central tree" trait. [docs] `organizations/_documentation.md`. 201 vanilla trait blocks write it: 197 contain only `base` (194 of them `base = 2`) and 4 add a `modifier` block. [vanilla-confirmed 1.19.3] `organizations/`.
- 46 vanilla `trait` blocks in six Delta MIOs (`BEL_cockerill_shipyards_organization` and its `_no_wuw` twin, `NOR_akers_mekaniske_verksted_organization`, `PHI_compania_maritima_de_cebu_organization`, and one block each in two `CHI_` MIOs) repeat the token of an inherited trait and write no `position`, only `limit_to_equipment_type`. The documentation prescribes `override_trait` for changing an inherited trait and says nothing about this form. [vanilla-confirmed 1.19.3] `organizations/BEL_organization.txt`. Whether it replaces the inherited trait or adds a second one is not stated. [unverified]
<!-- kit:end id="mio-trait-notes" -->

## Delta MIO <a id="Delta_MIO"></a>

TODO: Write

<!-- kit:begin id="mio-delta" at="section:Delta_MIO" -->
**Kit addition** The wiki leaves this section as "TODO: Write". A Delta MIO is an MIO that names another MIO with `include` and then changes parts of it. In 1.19.3 the mechanism is documented and heavily used: 516 of the 552 vanilla definitions use `include`. [docs] `common/military_industrial_organization/organizations/_documentation.md`. [vanilla-confirmed 1.19.3] `common/military_industrial_organization/organizations/`.

| Key | Effect |
| --- | --- |
| `include = <MIO token>` | Reuses every part of the named MIO. The included MIO only has to exist somewhere in `organizations/`; there is no load order requirement. |
| any MIO-level key | Written in the including MIO, it replaces the inherited value (`allowed`, `icon`, `research_bonus`, `equipment_type`, `tree_header_text`, and so on). |
| `delete_included_values = { name initial_trait ... }` | Resets the listed MIO-level parameters to their default or empty value. Every MIO-level parameter except the trait keys is eligible. |
| `initial_trait = { ... }` | Normal initial trait keys; only what is written overrides, the rest stays inherited. |
| `add_trait = { ... }` | Adds a trait to the inherited tree, with the normal trait keys. |
| `remove_trait = { <trait token> }` | Removes an inherited trait. |
| `override_trait = { token = <trait token> ... }` | Changes only the listed keys of an inherited trait; `delete_included_values = { ... }` inside it resets the listed trait keys to default. |

All rows: [docs] `common/military_industrial_organization/organizations/_documentation.md`. The documentation warns that when the included and the including MIO sit in two different files, both files must be saved to hot-reload the result. [docs] `common/military_industrial_organization/organizations/_documentation.md`.

Vanilla patterns, all [vanilla-confirmed 1.19.3] in `common/military_industrial_organization/organizations/` unless a file is named:

- The `include` targets are the 30 archetypes of `00_generic_organization.txt` (`generic_infantry_equipment_organization` 50 times, `generic_motorized_mechanized_organization` 42, `generic_artillery_organization` 40, and so on) plus `CZE_tank_destroyer_organization`, `CZE_automatic_weapons_equipment_organization` and the test MIO `my_custom_mio`. No definition includes one that itself uses `include`.
- 23 of the 30 archetypes carry `allowed = { always = no }` (for example `generic_helicopter_organization`, which is also gated by `has_dlc = "Gotterdammerung"`), so they exist only to be included. A Delta MIO therefore writes its own `allowed`; 515 of the 516 do, and the exception, `my_mio_with_include` in `mio.txt`, inherits `always = no`.
- Counts of the trait operations in vanilla: `add_trait` 557, `override_trait` 180, `remove_trait` 7, `delete_included_values` 0. 141 of the 180 `override_trait` blocks set `position`, which is how `GER_porsche_organization` moves `generic_mio_trait_wide_tracks`. The `override_trait` example in the documentation also shows `is_available = { ... }`; the trait key is `available`, so `is_available` is probably a typo. [unverified]

**DLC gating as vanilla does it.** `has_dlc` appears 711 times in `organizations/*.txt`, naming 16 DLCs. The patterns, all [vanilla-confirmed 1.19.3] in `common/military_industrial_organization/organizations/` unless a file is named:

1. A country MIO that needs a DLC puts `has_dlc = "..."` beside the tag check in `allowed`: `AFG_tanks_organization` uses `has_dlc = "Graveyard of Empires"` and `tag = AFG`.
2. A twin without the DLC: `SPR_secn_vanilla_organization` includes `generic_task_force_ship_organization` with `NOT = { has_dlc = "La Resistance" }`, while `SPR_secn_organization` includes `generic_battle_line_ship_organization` with `has_dlc = "La Resistance"`. Both are in `SPR_organization.txt`.
3. An archetype that countries with a bespoke MIO must not also get: `generic_tank_organization` carries 12 `NOT = { AND = { ... has_dlc = "..." } }` blocks, each naming one or two DLCs (13 `has_dlc` checks in all). See `00_generic_organization.txt`.
4. A scripted trigger as shorthand: `NOR_AAT = yes` stands for `original_tag = NOR` plus `has_dlc = "Arms Against Tyranny"`. See `common/scripted_triggers/NOR_scripted_triggers.txt`; `GER_porsche_organization` and the policy `mio_policy_NOR_general_permanent_industrial_revolution` use it.
5. Debug copies in `00_DEBUG_organization.txt` combine `has_dlc = "Arms Against Tyranny"` with `is_debug = yes` and show only when the country has the flag `mio_show_all_archetypes_flag` (`visible`).
6. Foreign MIOs let other countries use a national MIO; `available` then checks the owner, for example `FROM = { NOT = { has_war_with = GER } }` for non-German users of `GER_porsche_organization`.

Example in vanilla style, shortened from `GER_porsche_organization` (not an exact excerpt; every key in it is used by that vanilla definition):

```text
GER_porsche_organization = {
	include = generic_heavy_tank_organization
	icon = GFX_idea_porsche
	allowed = { original_tag = GER }
	override_trait = {
		token = generic_mio_trait_wide_tracks
		position = { x=0 y=0 }
	}
	add_trait = {
		token = GER_mio_trait_hoesch_facilities
		name = GER_mio_trait_hoesch_facilities
		icon = GFX_generic_mio_trait_icon_production_capacity
		special_trait_background = yes
		position = { x=9 y=0 }
		production_bonus = { production_capacity_factor = 0.05 }
	}
}
```

Keys of the example: [vanilla-confirmed 1.19.3] `common/military_industrial_organization/organizations/GER_organization.txt`.
<!-- kit:end id="mio-delta" -->

## Policies <a id="Policies"></a>

Properties of a policies

| Key | Mandatory? | Description | Example |
| --- | --- | --- | --- |
| name | false | Policy name.<br>May use scripted localization, scope will be set with the country owning the policy. | `name = loc_key` |
| icon | false | Icon to use for your policy. | `icon = GFX_mio_policy_my_policy` |
| cost | false | Attach cost in political power.<br>Default is define [DEFAULT INITIAL POLICY ATTACH COST](<defines.md>) "25". | `cost = 10` |
| cooldown | false | Cooldown in days after attaching a policy.<br>Default is define [DEFAULT INITIAL ATTACH POLICY COOLDOWN](<defines.md>) "180". | `cooldown = 60` |
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

<!-- kit:begin id="mio-policies-notes" at="section:Policies" -->
**Kit note** Checks of the policy table against `policies/_documentation.md` and the 22 vanilla policies.

- Each MIO can have one policy attached at a time, and the policy gives bonuses only to the equipment variant or production line the MIO is assigned to. [docs] `common/military_industrial_organization/policies/_documentation.md`.
- `allowed`, `visible`, `available`, `on_add`, `on_remove` and `ai_will_do` all run in MIO scope. `allowed` is evaluated once at game start for every MIO, and a false result removes the policy from that MIO for the rest of the game. The `name` key may be scripted localisation, with the country that owns the policy as scope. [docs] `common/military_industrial_organization/policies/_documentation.md`. To reach the country from a policy trigger, vanilla uses `owner`: `mio_policy_NOR_general_permanent_industrial_revolution` writes `allowed = { owner = { NOR_AAT = yes } }`. [vanilla-confirmed 1.19.3] `common/military_industrial_organization/policies/_general_policies.txt`.
- The defaults in the table are right: `cost` falls back to `DEFAULT_INITIAL_POLICY_ATTACH_COST` (25) and `cooldown` to `DEFAULT_INITIAL_ATTACH_POLICY_COOLDOWN` (180 days). [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.
- In a policy, `equipment_bonus` and `production_bonus` are keyed by an equipment group, category, archetype or type, or by `same_as_mio`, which means all equipment of the attached MIO. [docs] `common/military_industrial_organization/policies/_documentation.md`. 17 of the 24 keyed blocks in vanilla policies use `same_as_mio`; the others name `mio_cat_eq_all_medium_plane`, `large_plane_airframe`, `large_plane_maritime_patrol_plane_airframe`, `heavy_tank_chassis`, `train_equipment`, `railway_gun_equipment` and `ship_hull_carrier`. [vanilla-confirmed 1.19.3] `common/military_industrial_organization/policies/`.
- Vanilla policies write only `icon`, `allowed`, `available`, `equipment_bonus`, `production_bonus` and `organization_modifier`. None writes `name`, `cost`, `cooldown`, `visible`, `on_add`, `on_remove` or `ai_will_do`. The usual gate is `available = { has_mio_size > 5 }`, so a policy opens at MIO size 6; `mio_policy_RAJ_general_ordnance_factory_board` uses `> 7`. [vanilla-confirmed 1.19.3] `common/military_industrial_organization/policies/`. The policy name is its token, localised in `military_industrial_organization_l_english.yml` (`mio_policy_general_ruthless_contracts: "Ruthless Contracts"`). [vanilla-confirmed 1.19.3] `localisation/english/military_industrial_organization_l_english.yml`.
- `mio_policy_land_heavy_gantry_cranes` puts the production stat `production_efficiency_cap_factor` inside `equipment_bonus`, for `heavy_tank_chassis`, `train_equipment` and `railway_gun_equipment`. Whether that applies the bonus to the production line is not documented, so prefer `production_bonus` for production stats. [unverified]
- Policy cost and cooldown can be changed from script and by modifiers. The country effects `add_mio_policy_cost`, `set_mio_policy_cost`, `add_mio_policy_cooldown` and `set_mio_policy_cooldown` take `policy = <token>` and `value = <number>`; `unlock_mio_policy_tooltip` shows an unlock line; `has_mio_policy` and `has_mio_policy_active` test a policy in MIO scope. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`. The country modifiers `military_industrial_organization_policy_cost` and `military_industrial_organization_policy_cooldown` exist in the `war_production` category. [docs] `documentation/modifiers_documentation.md`. Vanilla uses the cost one once, with -0.75, in `common/country_leader/00_traits.txt`. [vanilla-confirmed 1.19.3] `common/country_leader/00_traits.txt`.

Vanilla policy, unchanged apart from spacing:

```text
mio_policy_general_ruthless_contracts = {
	icon = GFX_mio_policy_ruthless_contracts
	allowed = { always = yes }
	available = { has_mio_size > 5 }
	organization_modifier = {
		military_industrial_organization_funds_gain = 0.1
	}
}
```

Source of the example: [vanilla-confirmed 1.19.3] `common/military_industrial_organization/policies/_general_policies.txt`.
<!-- kit:end id="mio-policies-notes" -->

## AI Bonus Weights <a id="AI_Bonus_Weights"></a>

TODO: Write

<!-- kit:begin id="mio-ai-weights" at="section:AI_Bonus_Weights" -->
**Kit addition** The wiki leaves this section as "TODO: Write". The folder `common/military_industrial_organization/ai_bonus_weights/` holds numbers that say how much each trait bonus attracts the AI when it picks traits.

- Format: top-level blocks named after an equipment archetype, each listing `<bonus> = <weight>` pairs, plus one block named `default`. A bigger bonus value pulls the AI harder, and a bigger weight scales that pull. [docs] `common/military_industrial_organization/ai_bonus_weights/_documentation.md`.
- Lookup: the archetype's own weight is used if it exists, otherwise the `default` weight; if neither exists the game logs an error. Every bonus that any MIO uses should therefore have at least a `default` entry. [docs] `common/military_industrial_organization/ai_bonus_weights/_documentation.md`.
- Vanilla content: three archetype blocks, `small_plane_airframe` (`air_attack = 8`, `air_agility = 10`), `small_plane_cas_airframe` (`air_ground_attack = 5`) and `medium_plane_airframe` (`air_ground_attack = 10`), and a `default` block with 85 entries. The entries cover equipment stats (`armor_value = 5`, `breakthrough = 5`, `build_cost_ic = 3.85`, `reliability = 0.5`, `soft_attack = 2.5`), production bonuses (`production_capacity_factor = 10`, `production_cost_factor = 10`, `production_efficiency_cap_factor = 10`, `production_efficiency_gain_factor = 1`, `production_resource_need_factor = 0.9`, `production_resource_penalty_factor = 0.8`, `production_conversion_speed_factor = 1`) and all seven organisation modifiers (each 1). [vanilla-confirmed 1.19.3] `common/military_industrial_organization/ai_bonus_weights/ai_bonus_weights.txt`.
- Every bonus key written in the vanilla traits and policies has a `default` entry (checked over all 55 organisation files and the 22 policies); 25 default entries are not used by any vanilla trait or policy, among them `entrenchment`, `fuel_capacity`, `thrust`, `weight` and `recon`. [vanilla-confirmed 1.19.3] `common/military_industrial_organization/`.
- A mod that uses a stat in a trait bonus that the `default` block lacks gets the logged error described above. To change a weight, copy the whole `default` block into a file of your own in the mod's `ai_bonus_weights/` folder and edit it, so every key keeps a value; how the game merges several files in that folder is not documented. [unverified]
- The documentation example uses `infantry_equipment` as the archetype key. Vanilla uses airframe archetypes only; whether a category or equipment group is accepted as a key is not documented. [unverified]
- Other AI levers for MIOs: the MIO-level `ai_will_do` multiplier, the trait-level `ai_will_do` (see the trait notes above), and the policy `ai_will_do`, which sets how likely the AI is to spend political power on that policy. [docs] `common/military_industrial_organization/organizations/_documentation.md`, `common/military_industrial_organization/policies/_documentation.md`.
- Defines that shape the AI choice, all in `common/defines/00_defines.lua`: `INDUSTRIAL_ORG_TRAIT_UNLOCK_RANDOMNESS`, `INDUSTRIAL_ORG_POLICY_CHANGE_RANDOMNESS`, `INDUSTRIAL_ORG_RESEARCH_ASSIGN_RANDOMNESS` and `INDUSTRIAL_ORG_PRODUCTION_ASSIGN_RANDOMNESS` (each 3, the AI picks at random among that many top choices), `INDUSTRIAL_ORG_POLICY_CHANGE_SCALE` (1.0), `INDUSTRIAL_ORG_TRAIT_RANK_FACTOR` (0.80, traits deeper in the tree count less by this factor) and `INDUSTRIAL_ORG_RESEARCH_BONUS_FACTOR` (10.0, applied to the research bonus when the AI judges design teams). [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. See [Defines](<defines.md>).

The exact scoring formula is not documented.

Shape of the file, shortened from the vanilla file (three of the 85 `default` entries):

```text
small_plane_airframe = {
	air_attack = 8
	air_agility = 10
}

default = {
	armor_value = 5
	production_capacity_factor = 10
	military_industrial_organization_research_bonus = 1
}
```

Values: [vanilla-confirmed 1.19.3] `common/military_industrial_organization/ai_bonus_weights/ai_bonus_weights.txt`.
<!-- kit:end id="mio-ai-weights" -->

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

<!-- kit:begin id="mio-equipment-stats" at="section:Equipment_Boni" -->
**Kit correction** `naval_supremacy_factor` in the Ships table is not a stat in 1.19.3. The documentation lists `naval_dominance_factor`, and `naval_supremacy_factor` appears nowhere under `common/`. [docs] `common/military_industrial_organization/organizations/_documentation.md`. [vanilla-confirmed 1.19.3] 0 files under `common/` contain `naval_supremacy_factor`. No vanilla trait uses `naval_dominance_factor` either; it appears in the documentation and in comments only. [vanilla-confirmed 1.19.3] `common/military_industrial_organization/organizations/00_generic_organization.txt`. The string `naval_dominance_factor` is present in `hoi4.exe`, which fits a real but unused stat. [unverified]

**Kit addition** The Tanks list above is incomplete. The documentation also lists `soft_attack`, `hard_attack`, `ap_attack`, `air_attack`, `fuel_consumption` and `hardness` for tanks. It marks `entrenchment` as needing the NSB DLC and the `dozer_blade` module, and `fuel_capacity` as needing NSB and the `expanded_fuel_tank` module. [docs] `common/military_industrial_organization/organizations/_documentation.md`.

Stats the documentation lists for the other equipment classes. All rows: [docs] `common/military_industrial_organization/organizations/_documentation.md`.

| Equipment class | Stats |
| --- | --- |
| Infantry equipment | `reliability`, `maximum_speed`, `defense`, `breakthrough`, `soft_attack`, `hard_attack`, `ap_attack`, `build_cost_ic` (`hardness`, `armor_value` and `air_attack` exist but are 0 and not shown) |
| Support equipment | `reliability`, `build_cost_ic` |
| Artillery, anti-air, anti-tank, rocket artillery, motorized rocket | `reliability`, `defense`, `breakthrough`, `hardness`, `armor_value`, `soft_attack`, `hard_attack`, `ap_attack`, `air_attack`, `build_cost_ic` |
| Motorized | `maximum_speed`, `reliability`, `hardness`, `breakthrough`, `build_cost_ic`, `fuel_consumption` |
| Mechanized, amphibious mechanized | `maximum_speed`, `reliability`, `defense`, `breakthrough`, `hardness`, `armor_value`, `ap_attack`, `air_attack`, `build_cost_ic`, `fuel_consumption` |
| Armored car | `maximum_speed`, `reliability`, `defense`, `breakthrough`, `hardness`, `armor_value`, `soft_attack`, `hard_attack`, `ap_attack`, `air_attack`, `build_cost_ic`, `fuel_consumption` |
| Train | `armor_value`, `build_cost_ic`, `air_attack` |
| Railway gun | `reliability`, `maximum_speed`, `railway_gun_attack`, `build_cost_ic` |

The same file marks several ship and plane stats as conditional. For planes, `thrust`, `weight` and `night_penalty` need the BBA DLC, and `mines_planting` and `mines_sweeping` need MtG and BBA. For ships, many combat stats (`lg_attack`, `hg_attack`, `torpedo_attack`, `sub_attack`, `anti_air_attack`, `armor_value`, `sub_detection` and others) need modules that carry a base value, and `mines_sweeping` and `mines_planting` need MtG. A bonus on a stat the equipment has no base value for gives nothing unless a module adds it. [docs] `common/military_industrial_organization/organizations/_documentation.md`.

Three stats appear in vanilla `equipment_bonus` blocks but not in the documentation lists: `patrol_coordination`, `fuel_consumption_factor` and `naval_weather_penalty_factor`. All three have an entry in the AI `default` weights. [vanilla-confirmed 1.19.3] `common/military_industrial_organization/organizations/`, `common/military_industrial_organization/ai_bonus_weights/ai_bonus_weights.txt`.
<!-- kit:end id="mio-equipment-stats" -->

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

<!-- kit:begin id="mio-production-notes" at="section:Production_Boni" -->
**Kit correction** The sign matters. The example `production_cost_factor = 0.05` in the table above would make the line more expensive. Savings are negative values: the documentation example is `production_cost_factor = -0.1`, and 83 of the 93 plain numeric vanilla uses are negative, the 10 positive ones being the price of a trade-off trait. The same holds for `production_resource_need_factor` (38 of 41 negative) and `production_resource_penalty_factor` (27 of 28 negative). `production_efficiency_cap_factor`, `production_efficiency_gain_factor`, `production_capacity_factor` and `production_conversion_speed_factor` are positive when they help. [docs] `common/military_industrial_organization/organizations/_documentation.md`. [vanilla-confirmed 1.19.3] `common/military_industrial_organization/organizations/`.

**Kit note** All seven production keys in the table are valid, and vanilla traits use all seven (`production_capacity_factor` 185 times, `production_cost_factor` 114, `production_efficiency_cap_factor` 66, `production_efficiency_gain_factor` 73, `production_resource_need_factor` 41, `production_resource_penalty_factor` 28, `production_conversion_speed_factor` 11). [vanilla-confirmed 1.19.3] `common/military_industrial_organization/organizations/`. A trait's `production_bonus` applies when the MIO is assigned to a production line; in a policy it is keyed by equipment type instead. [docs] `common/military_industrial_organization/organizations/_documentation.md`, `common/military_industrial_organization/policies/_documentation.md`.
<!-- kit:end id="mio-production-notes" -->

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

<!-- kit:begin id="mio-org-notes" at="section:Organization_Boni" -->
**Kit note** The seven keys in the table are exactly the organisation modifiers the documentation allows in `organization_modifier`, in a trait or a policy. [docs] `common/military_industrial_organization/organizations/_documentation.md`. Vanilla trait counts: `military_industrial_organization_research_bonus` 122, `military_industrial_organization_funds_gain` 29, `military_industrial_organization_design_team_assign_cost` 11, `military_industrial_organization_size_up_requirement` 3, `military_industrial_organization_design_team_change_cost` 2, `military_industrial_organization_industrial_manufacturer_assign_cost` 1, `military_industrial_organization_task_capacity` 2 (both in the test file `mio.txt`, with values -50 and -49). [vanilla-confirmed 1.19.3] `common/military_industrial_organization/organizations/`.

The design team assign cost and the industrial manufacturer assign cost are daily political power costs, and the design team change cost is an experience cost for changing the MIO in the equipment designer. [docs] `documentation/effects_documentation.md` (`add_mio_design_team_assign_cost`, `add_mio_design_team_change_cost`, `add_mio_industrial_manufacturer_assign_cost`).

**Kit addition** Defines that set the base numbers behind funds, size and assignment. All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. See [Defines](<defines.md>).

| Define | Value | Meaning in the define comment |
| --- | --- | --- |
| `FUNDS_FOR_SIZE_UP` | 700 | funds an MIO needs to grow one size and earn trait points |
| `FUNDS_FOR_SIZE_UP_LEVEL_FACTOR` | 100 | how much each level multiplies that requirement |
| `FUNDS_FOR_SIZE_UP_LEVEL_POW` | 1.8 | the power applied to the MIO size when computing the requirement |
| `UNLOCKED_TRAITS_PER_SIZE_UP` | 1 | trait points gained per size |
| `FUNDS_FOR_RESEARCH_COMPLETION_PER_RESEARCH_COST` | 500 | funds added when a design team finishes research, times the technology's research cost |
| `FUNDS_FOR_CREATING_EQUIPMENT_VARIANT` | 0 | funds added when a variant is created with the design team assigned |
| `FUNDS_FROM_MANUFACTURER_PER_IC_PER_DAY` | 0.1 | funds per day in proportion to output while a manufacturer is attached to a production line |
| `MAX_FUNDS_FROM_MANUFACTURER_PER_DAY` | 100 | cap per manufacturer per day, 0 for no cap |
| `ASSIGN_DESIGN_TEAM_PP_COST_PER_DAY` | 0.1 | daily political power cost of one MIO on a research slot, 0 disables it |
| `ASSIGN_INDUSTRIAL_MANUFACTURER_PP_COST_PER_DAY` | 0.0 | the same for a production line |
| `ENABLE_TASK_CAPACITY` | false | enables limited task capacity |
| `DEFAULT_INITIAL_TASK_CAPACITY` | 0 | default `task_capacity` of an MIO |

The script effect `complete_mio_trait` ignores the state of the tree and adds one size, so that size and unlocked traits stay aligned. [docs] `documentation/effects_documentation.md`.
<!-- kit:end id="mio-org-notes" -->

## References <a id="References"></a>

<!-- kit:begin id="mio-runtime-script" at="bottom" -->
## Kit: Scripting MIOs at runtime <a id="kit-mio-runtime"></a>

**Kit addition** The MIO scope is entered with `mio:<token> = { ... }`, from a variable (`var:my_mio_var`), or by iterating from a country with `every_military_industrial_organization`, `random_military_industrial_organization`, `any_military_industrial_organization` and `all_military_industrial_organization`. The iterators accept `tooltip`, skip invisible MIOs unless `include_invisible = yes` is given, and the effect iterators also take `random_select_amount` and `display_individual_scopes`. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`. Vanilla enters an MIO this way: `common/characters/GER.txt` contains `mio:GER_porsche_organization = { ... }`. [vanilla-confirmed 1.19.3] `common/characters/GER.txt`. See [Effects](<effects.md>) and [Triggers](<triggers.md>) for the full texts.

All rows below: [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`.

| Group | Names (MIO scope unless noted) |
| --- | --- |
| Funds and size | `add_mio_funds`, `set_mio_funds`, `add_mio_size`, `add_mio_funds_gain_factor`, `set_mio_funds_gain_factor`, `add_mio_size_up_requirement_factor`, `set_mio_size_up_requirement_factor` |
| Research and tasks | `add_mio_research_bonus`, `set_mio_research_bonus`, `add_mio_task_capacity`, `set_mio_task_capacity` |
| Assignment costs | `add_mio_design_team_assign_cost`, `set_mio_design_team_assign_cost`, `add_mio_design_team_change_cost`, `set_mio_design_team_change_cost`, `add_mio_industrial_manufacturer_assign_cost`, `set_mio_industrial_manufacturer_assign_cost` |
| Traits | `complete_mio_trait` (accepts `show_modifiers = no`), `unlock_mio_trait_tooltip` |
| Flags | `set_mio_flag` (with `value` and `days`), `clr_mio_flag`, `modify_mio_flag` |
| Look | `set_mio_icon`, `set_mio_name_key` |
| Country scope | `show_mio_tooltip`, `unlock_military_industrial_organization_tooltip`, `add_mio_policy_cost`, `set_mio_policy_cost`, `add_mio_policy_cooldown`, `set_mio_policy_cooldown` |
| Any scope | `unlock_mio_policy_tooltip` |
| Triggers | `has_mio_size`, `has_mio_trait`, `is_mio_trait_completed`, `is_mio_trait_available`, `has_mio_number_of_completed_traits`, `has_mio_policy`, `has_mio_policy_active`, `has_mio_equipment_type`, `has_mio_research_category`, `has_mio_flag`, `is_mio_assigned_to_task`, `is_mio_available`, `is_mio_visible`, `is_military_industrial_organization` |
| Country triggers | `has_military_industrial_organization` |

Behaviours worth knowing. `add_mio_funds` that pushes funds over the size-up limit grows the MIO, and a negative total is capped at 0 without shrinking it. The `add_mio_*` cost and bonus effects change the base value and modifiers still apply on top; a final value below 0 is capped at 0 without an error. `add_mio_design_team_change_cost` rounds the result down. `is_mio_trait_available` also checks the parent and mutual exclusion rules unless `check_mio_parent_completed = no` or `check_mio_mutually_exclusive = no` is given. `is_mio_available` is true only when both `visible` and `available` hold. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`.
<!-- kit:end id="mio-runtime-script" -->

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list_of_modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on_actions.md>) • [Data structures](<data_structures.md>) • [Flags](<data_structures.md#Flags>) • [Event targets](<data_structures.md#Event_targets>) • [Country tag aliases](<data_structures.md#Country_tag_aliases>) • [Variables](<data_structures.md#Variables>) • [Arrays](<data_structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement_modding.md>) • [AI](<ai_modding.md>) • [AI focuses](<ai_focuses.md>) • [Autonomous states](<autonomy_state_modding.md>) • [Balances of power](<balance_of_power_modding.md>) • [Bookmarks/Scenarios](<bookmark_modding.md>) • [Game rules](<bookmark_modding.md#Game_rules>) • [Buildings](<building_modding.md>) • [Characters and traits](<character_modding.md>) • [Cosmetic tags](<cosmetic_tag_modding.md>) • [Countries](<country_creation.md>) • [Divisions](<division_modding.md>) • [Decisions](<decision_modding.md>) • [Doctrines](<doctrine_modding.md>) • [Equipment](<equipment_modding.md>) • [Events](<event_modding.md>) • [Factions](<faction_modding.md>) • [Ideas](<idea_modding.md>) • [Ideologies](<ideology_modding.md>) • [National focuses](<national_focus_modding.md>) • [Resources](<resources_modding.md>) • [Scripted GUI](<scripted_gui_modding.md>) • [Technologies and doctrines](<technology_modding.md>) • [Units](<unit_modding.md>)
- **Map**: [Map](<map_modding.md>) • [States](<state_modding.md>) • [Supply areas](<supply_areas_modding.md>) • [Strategic regions](<strategic_region_modding.md>)
- **Graphical**: [Interface](<interface_modding.md>) • [Graphical assets](<graphical_asset_modding.md>) • [Entities](<entity_modding.md>) • [Posteffects](<posteffect_modding.md>) • [Particles](<particle_modding.md>) • [Fonts](<font_modding.md>)
- **Cosmetic**: [Portraits](<portrait_modding.md>) • [Namelists](<namelist_modding.md>) • [Music](<music_modding.md>) • [Sound](<sound_modding.md>)
- **Other**: [Console commands](<console_commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod_structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection_modding.md>) • [Defines additions](<defines_additions.md>) • [Game rule modding](<game_rule_modding.md>) • [Intelligence operation modding](<intelligence_operation_modding.md>) • [Map mode modding](<map_mode_modding.md>) • [Occupation and resistance modding](<occupation_and_resistance_modding.md>) • [Peace conference modding](<peace_conference_modding.md>) • [Raid modding](<raid_modding.md>) • [Script constant modding](<script_constant_modding.md>) • [Special project modding](<special_project_modding.md>)
