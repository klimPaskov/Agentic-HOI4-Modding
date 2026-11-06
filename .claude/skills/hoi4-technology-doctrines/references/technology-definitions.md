# Hearts of Iron IV Technologies and Doctrines: Technology definitions, AI weights and localisation

Part of the [hoi4-technology-doctrines](../SKILL.md) skill. Read before writing or changing a technology block, its unlocks, hidden-tech pattern, AI weighting, localisation or tile icon.

## Technology definitions

Vanilla precedents: `GAME/common/technologies/infantry.txt` (visible chain with equipment unlocks), `air_techs.txt` (sub-technologies), `special_projects_tech.txt` (hidden technologies), `NSB_armor.txt` and `MTG_naval.txt` (`allow_branch`, `on_research_complete`, experience boosts).
File names do not matter; every technology is a block inside `technologies = { ... }`.

```
technologies = {
	@1936 = 2						# file-scoped constant for a row position
	my_tech = {
		enable_equipments = { my_equipment_1 }
		enable_equipment_modules = { my_module }
		enable_subunits = { my_subunit }
		enable_building = { building = my_building level = 2 }
		enable_tactic = my_tactic

		path = {
			leads_to_tech = my_tech_2
			research_cost_coeff = 1
		}
		research_cost = 1.5
		start_year = 1936
		folder = {
			name = my_folder
			position = { x = 0 y = @1936 }
		}
		categories = { my_category }
		allow = { }					# researchable? hidden techs use always = no
		allow_branch = { }				# visible? false hides the tech and its path children
		ai_will_do = { base = 2 modifier = { factor = 2 is_major = yes } }
		ai_research_weights = { offensive = -1.0 }

		# country modifiers, sub-unit and category blocks, terrain blocks
		political_power_gain = 0.1
		category_all_infantry = { combat_width = -0.2 urban = { attack = 0.15 } }

		on_research_complete_limit = { }
		on_research_complete = { }
		show_effect_as_desc = yes
	}
}
```

### Field reference

| Field | Behaviour |
| --- | --- |
| `research_cost` | Multiplier of `NDefines.NTechnology.BASE_TECH_COST` (110 in the installed defines; the wiki says 100) |
| `start_year` | Year the tech is intended to be researched; each year ahead adds `BASE_YEAR_AHEAD_PENALTY_FACTOR` (2, meaning plus 200 percent) to the cost, smoothly |
| `folder = { name position }` | Places the tech in a folder; repeat the block for several folders; coordinates are in grid slots, not pixels |
| `path = { leads_to_tech research_cost_coeff }` | Draws the line and assigns the child to this tech's gridbox; the child needs at least one researched `path` parent; a coefficient below 1 makes the child cheaper when this parent was the one researched; `ignore_for_layout = yes` marks a secondary path that must not decide the gridbox |
| `dependencies = { tech = 1 }` | Hard requirements without drawing a line; all must be researched (AND), in contrast with `path` (OR) |
| `XOR = { a b }` | Mutual exclusion; must be written on every technology in the group |
| `sub_technologies = { a b }` | Up to `MAX_SUBTECHS` (3) children shown inside the parent tile; index follows list order; `sub_tech_index` on the child overrides it |
| `categories = { ... }` | Used for AI weights, `research_bonus`, `add_tech_bonus`, sharing groups, and the `*_cost_factor` modifiers; defined in `technology_tags` |
| `allow` | Continuously checked; false blocks manual research but not `set_technology`, and the tile stays visible |
| `allow_branch` | False hides the tech and all `path` descendants (the wiki says the AI then cannot select it either) |
| `doctrine = yes`, `doctrine_name` | Legacy technology-based doctrines; the current doctrine system uses `common/doctrines/` |
| `xp_research_type = army, navy, or air`, `xp_boost_cost`, `xp_research_bonus`, `xp_unlock_cost` | Experience boost or direct unlock; vanilla navy techs use boost cost and bonus |
| `show_equipment_icon = yes` | Shows the unlocked equipment icon in the hover tooltip |
| `force_use_small_tech_layout = yes` | Use the small tile even if the tech unlocks equipment |
| `desc = KEY` | Extra hover text appended to the description |
| `show_effect_as_desc` | Puts modifier and effect text in the description |
| `special_project_specialization`, `is_special_project_tech` | Special project hooks seen in vanilla, outside the scope of this skill |
| `ai_will_do`, `ai_research_weights` | Base 1 per tech; see the AI section |

### Unlocking objects

- Equipment, modules, and sub-units that no technology lists are always available; listing them in a technology gates them behind it.
  This is how country-specific unlocks are made, using a hidden technology.
- `enable_building` unlocks building up to `level`, never more than the building's `max_level`; a later tech with a higher `level` raises the cap.
  Buildings can still be built above the unlocked level by an effect or by a state's history.
- The unlocked equipment's tile icon is `GFX_<tech>_medium`; the equipment uses that icon unless it defines its own.
- Researched through `set_technology = { x = 0 }` ("unresearch"): unlocked database objects stay usable until restart and mutually exclusive techs cannot be removed.
  Treat unlocks as permanent.

### Effects and modifiers on a technology

- `on_research_complete` runs for the researching country when the tech is researched or granted by `set_technology`, but not for technologies listed in a country history file.
  It appears in the tooltip, so a block that sometimes shows nothing needs an `on_research_complete_limit` trigger for the tooltip to render correctly.
- Any country-scoped modifier can be written directly in the technology.
- A sub-unit key or category (`category_all_infantry`) opens a block of unit stat modifiers; a terrain key inside it (or `amphibious`, `river`) scopes them.
  Sub-unit categories are defined in `GAME/common/unit_tags/00_categories.txt`.
- To show a technology's effects in another tooltip use:

```
custom_effect_tooltip = {
	localization_key = generic_enables_tech_tt
	TECH_EFFECT = tech_effect|my_tech
	TECH_NAME = my_tech
}
```

  Vanilla precedent: `GAME/common/decisions/AST.txt` (search `tech_effect`), with the loc key `generic_enables_tech_tt` in `goe_focus_l_english.yml`.

### Hidden technology pattern

```
my_hidden_tech = {
	allow = { always = no }
	start_year = 1936
	enable_equipments = { my_equipment_0 }
	enable_subunits = { my_subunit }
}
```

Vanilla: `GAME/common/technologies/special_projects_tech.txt`.
Grant with `set_technology = { my_hidden_tech = 1 popup = no }`.
Call `mark_technology_tree_layout_dirty = yes` when a condition that feeds `allow_branch` or hidden tech visibility changes and the tree must refresh for that country.
The AI can research a hidden tech unless `allow` is false.

## AI and technology

- The AI picks research by a weight: base 1 (or `ai_will_do`), adjusted by cost, bonuses, and ahead-of-time modifiers; the choice is re-rolled every 7 days (`RESEARCH_DAYS_BETWEEN_WEIGHT_UPDATE` in the defines).
- The wiki states a technology needs at least one of its categories listed in a `common/ai_focuses/*.txt` file for the AI to research it; the installed documentation does not repeat this, so add a category to an AI focus when AI research of a new category matters and report the result as unobserved.
- Per-country overrides use the `research_weight_factor` and `research_tech` AI strategy types and the `research = { category = factor }` block of an AI strategy plan; both are documented by `hoi4-ai-strategies`.
- AI doctrine choice uses `ai_will_do` in the grand doctrine and sub-doctrine blocks (see the vanilla blocks with `original_tag` and `is_major` modifiers).
- Mark hidden techs with `allow = { always = no }` so the AI does not research them.

## Localisation and graphics

- Technology: `<tech>` and `<tech>_desc`.
  A tech without its own name borrows the unlocked equipment's name and description, and a country-prefixed equipment key (`<TAG>_<equipment>`) gives a country-specific name.
  Vanilla `infantry_weapons1` has no key of its own and shows `infantry_equipment_1`.
- Tile icon: `GFX_<tech>_medium`; country override `GFX_<TAG>_<tech>_medium`; sprites live in an `interface/*.gfx` file, vanilla `GAME/interface/Technologies.gfx`.
- Folder: `<folder>` and `<folder>_desc`; folder tab sprite and background sprite are named in the interface files.
- Doctrines: see `references/doctrine-authoring.md`.
- Register sprites in `.gfx` before requesting art so file names do not change later.

