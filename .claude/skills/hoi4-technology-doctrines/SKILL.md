---
name: hoi4-technology-doctrines
description: Use when creating, changing, or scripting Hearts of Iron IV technologies, technology folders and categories, sub-technologies, technology unlocks, research bonuses, technology sharing, grand doctrines, doctrine tracks, sub-doctrines, mastery, or the technology tree viewer and inspector tools. Also use when a technology or doctrine is invisible, unresearchable, unlocks nothing, or grants no bonus.
---

# Hearts of Iron IV Technologies and Doctrines

Use this skill for `common/technologies/`, `common/technology_tags/`, `common/technology_sharing/`, `common/doctrines/`, the technology tree and doctrine interface files, and the effects, triggers, and modifiers that grant, test, or speed up research and doctrines.
Equipment definitions that a technology unlocks belong to `hoi4-equipment`, sub-units and templates to `hoi4-units-divisions`, ideas that carry `research_bonus` to `hoi4-ideas-modifiers`, and AI weighting strategies to `hoi4-ai-strategies`.

In this skill `GAME` means the installed Hearts of Iron IV folder named in `CLAUDE.md` and `WIKI` means the repository folder `paradox_wiki`.
Installed documentation is more authoritative than the wiki; where they disagree this skill says so.

## Read the engine contract first

Use `hoi4.reference_context` with `surface = technology`, then `hoi4.reference_search` and `hoi4.reference_read` for the cited sections, and `hoi4.source_lookup` for vanilla definitions.
If a route fails once, retry once with narrower input, then read the local files directly.

| Question | Read |
| --- | --- |
| Technology fields, cost, paths, folders, GUI, sharing groups | `WIKI/Technology modding - Hearts of Iron 4 Wiki.md` |
| Doctrine concepts, effects, triggers, modifiers | `GAME/common/doctrines/_documentation.md` |
| Doctrine folder, grand doctrine, track, and sub-doctrine syntax | `GAME/common/doctrines/folders/_documentation.md`, `grand_doctrines/_documentation.md`, `tracks/_documentation.md`, `subdoctrines/_documentation.md` |
| Effects (`set_technology`, `add_tech_bonus`, `set_grand_doctrine`, and the rest) | `GAME/documentation/effects_documentation.md` |
| Triggers (`has_tech`, `has_doctrine`, `has_mastery`, and the rest) | `GAME/documentation/triggers_documentation.md` |
| Modifiers (`research_speed_factor`, `<folder>_doctrine_cost_factor`, mastery gain factors) | `GAME/documentation/modifiers_documentation.md` |
| Defines (`NTechnology`, `NDoctrines`) | `GAME/common/defines/00_defines.lua` |
| Research weighting for the AI | `WIKI/Technology modding - Hearts of Iron 4 Wiki.md` (AI weighting), `WIKI/AI focuses - Hearts of Iron 4 Wiki.md`, `hoi4-ai-strategies` |

The tree and folder interface authoring detail is in `references/technology-tree-gui.md`.
Doctrine authoring skeletons, loc keys, and GUI notes are in `references/doctrine-authoring.md`.

## Decision table

| Goal | Mechanism |
| --- | --- |
| A visible researchable technology | Technology in a folder with a position, plus the folder container, item containers, and a gridbox in the folder window |
| A technology only a script or country setup can grant | Hidden technology: `allow = { always = no }`, no `folder`, granted by `set_technology` |
| Unlock equipment, modules, sub-units, buildings, or tactics | `enable_equipments`, `enable_equipment_modules`, `enable_subunits`, `enable_building`, `enable_tactic` on the technology |
| One extra ahead-of-time or branch-gated variant tile | `sub_technologies` on the parent |
| Apply a flat country modifier on research | Any country-scoped modifier written directly in the technology |
| Boost a sub-unit or category, optionally per terrain | Sub-unit or category block inside the technology |
| Run an effect once on research | `on_research_complete` with optional `on_research_complete_limit` |
| Grant a free partial boost to future research | `add_tech_bonus` (limited uses) |
| Speed research of one category | `research_bonus = { category = factor }` in an idea or leader trait |
| Speed all research | The `research_speed_factor` modifier |
| Share research between countries | A `technology_sharing_group` plus `add_to_tech_sharing_group` |
| Give or replace doctrines | `set_grand_doctrine` and `set_sub_doctrine`; mastery through `add_mastery`, `add_daily_mastery`, `add_mastery_bonus` |
| A new doctrine system | Folder, grand doctrines, tracks, sub-doctrines in `common/doctrines/` |
| Understand or verify an existing tree | The `hoi4.tech_inspect`, `hoi4.tech_render`, and `hoi4.tech_inspect` with `mode: "compare"` tools |

## Repository conventions that apply

- Indent with tabs, never use `<=` or `>=`, put tuning values in `common/script_constants/`, and reuse the project's dynamic scripted effects library (`common/scripted_effects/<prefix>_dynamic_effects.txt`, named in `CLAUDE.md`) before adding new ones.
- Localisation is UTF-8 with BOM and keys carry no `:0`; player-facing text describes the current world state.
- Keep technology folders and categories that the mod adds in their own file under `common/technology_tags/` (for example `<prefix>_tech_tags.txt`), a separate file of the same two top-level blocks the vanilla `00_technology.txt` uses.
- The repository holds a full copy of `interface/countrytechtreeview.gui` and `.gfx`; GUI additions for new folders go into that copy, and a game update needs a re-merge of the vanilla changes.
- A new concrete equipment type, sub-unit, special project, doctrine, or general system must be registered with the test-country setup effect described in `CLAUDE.md`.
- Document each new mechanic in `docs/` with the icons it needs, the `.gfx` file that references them, and the names used in code and localisation.

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

## Folders and categories

Defined in `common/technology_tags/*.txt`:

```
technology_categories = { my_category cat_my_other }

technology_folders = {
	my_folder = {
		ledger = army			# army, air, navy, military, civilian, all, hidden
		available = { has_dlc = "..." }	# optional visibility trigger
		doctrine = yes			# only for legacy doctrine folders
	}
}
```

- Folder localisation: `<folder>` and `<folder>_desc`.
- Category localisation: `<category>` for bonuses and sharing, and `<category>_research` for the `research_bonus` modifier text.
- A folder shows nothing until its interface exists: a folder tab button, a folder container with gridboxes, and item containers.
  Without them the AI can still research it and `set_technology` still works, but a player cannot research there.
  Authoring detail is in `references/technology-tree-gui.md`.
- Category words in `GAME/common/technology_tags/00_technology.txt` include `mio_cat_*` entries that military industrial organizations use; keep any renamed categories consistent across every reference.

## Technology effects, triggers, and research bonuses

| Name | Notes |
| --- | --- |
| `set_technology = { a = 1 b = 0 popup = no }` | Value 1 grants, 0 removes; removal does not reset progress, so a researchable tech can be researched again in one day |
| `add_tech_bonus` | `bonus`, `uses`, `ahead_reduction`, `category` or `technology` (repeatable), `name`; vanilla focuses use `name`, `bonus = 1`, `uses = 1`, `category` |
| `steal_random_tech_bonus` | Needs a category or folder; falls back to `base_bonus`; `instant = yes` unlocks directly |
| `add_research_slot`, `set_research_slots` | Negative values subtract |
| `inherit_technology = TAG` | Copies another country's researched techs, useful for releasing a country |
| `select_tech_tree_icon_origin` | Use another country's tech icons |
| `has_tech = x` | Researched |
| `can_research = x` | Country may research it now |
| `is_researching_technology = x` | In progress |
| `has_tech_bonus = { technology = x category = y }` | A limited bonus exists |
| `amount_research_slots`, `original_research_slots`, `num_researched_technologies` | Counts; `>` or `<` comparisons |
| `researched_techs` | Dynamic array of researched technologies |
| `is_in_tech_sharing_group`, `num_tech_sharing_groups` | Sharing membership |
| `research_speed_factor` | Country modifier for all research |
| `<Technology>_cost_factor` | Dynamic modifier by category (documented types are the `cat_*` categories) |
| `research_bonus = { <category> = 0.1 }` | Idea or leader trait block; negative values slow research |

The installed `GAME/common/on_actions/_documentation.md` lists no on action for a country completing a technology; the only research-related ones are the military industrial organization actions such as `on_mio_tech_reseach_completed`.
Use `on_research_complete` on the tech itself.

Limited bonuses are consumed by the research that uses them; the interface text keys `RESEARCH_BONUS_USED` and `RESEARCH_BONUS` in `core_l_english.yml` describe the behaviour.
`NDefines.NTechnology.USE_BONUS_REGRET_TIMER` gives three days to reverse a use.

## Technology sharing groups

`common/technology_sharing/*.txt`:

```
technology_sharing_group = {
	id = my_research
	name = my_research_name
	desc = my_research_desc
	picture = GFX_technology_sharing_default
	research_sharing_per_country_bonus = 0.1
	is_faction_sharing = yes		# optional
	categories = { infantry_weapons industry }	# optional
	available = { is_in_faction_with = ENG }	# checked per member; false kicks the country out
}
```

Add and remove through `add_to_tech_sharing_group = id`, `remove_from_tech_sharing_group = id`, and `modify_tech_sharing_bonus = { id = id bonus = 0.2 }`.
Membership is only ever granted by the effect.
The bonus cap is `MAX_TECH_SHARING_BONUS` (0.5).
Vanilla: `GAME/common/technology_sharing/00_tech_sharing_groups.txt`; the group picture is a sprite in `interface/technology_sharing.gfx`.

## Doctrines

The current system is data in `common/doctrines/`: a **folder** holds mutually exclusive **grand doctrines**; a grand doctrine lists **tracks**; each track holds one **sub-doctrine** whose **rewards** unlock as **mastery** accrues; completing a track gives the grand doctrine's **milestone** for that track.
Grand doctrines and sub-doctrines cost experience of one `xp_type` (`army`, `navy`, `air`).

Folder files: `folders/`, `grand_doctrines/`, `tracks/`, `subdoctrines/` (any subfolder).
Vanilla precedents: `GAME/common/doctrines/folders/doctrine_folders.txt`, `grand_doctrines/land_grand_doctrines.txt` (`new_mobile_warfare`), `tracks/land_doctrine_tracks.txt`, `subdoctrines/land/armor_subdoctrines.txt`.

Key rules:

- Use the exact vanilla ids.
  The grand doctrine ids are `new_mobile_warfare`, `superior_firepower`, `grand_battleplan`, `mass_assault`, `new_strategic_destruction`, `new_battlefield_support`, `new_operational_integrity`, `new_fleet_in_being`, `new_convoy_raiding`, `new_base_strike`, `special_forces_quantity`, and `special_forces_quality`.
  The installed `_documentation.md` example `set_grand_doctrine = mobile_warfare` is not a vanilla id; history files use `new_mobile_warfare`.
- Activation effects are written directly in a grand doctrine, milestone, sub-doctrine, or reward: country modifiers (optionally in `modifiers = { }`), `enable_tactic`, sub-unit and category stat blocks, `equipment_bonus`, and `effect = { }` for scripted effects.
- Named reward blocks make localisation keys `<subdoctrine>_<reward>` (see `armored_spearhead_force_concentration` in `GAME/localisation/english/doctrines_l_english.yml`); the file notes a `_desc` key is also read.
- Mastery accrues from the manpower of the sub-units, categories, or equipment configured in the track's `mastery` block, overridden per sub-doctrine; tuning lives in `NDoctrines` in the defines (`DEFAULT_REWARD_MASTERY` 100, `MAX_MONTHLY_MASTERY_GAIN` 40, bank values).
- A reward's `mastery = N` overrides the default amount needed for that reward.
- `xor = { ... }` on a sub-doctrine blocks others from being active simultaneously in other tracks of the same folder; replacing on the same track is still allowed.
- `allow_in_multiple_tracks = yes` lets one sub-doctrine sit in several tracks at once.
- `track` on a sub-doctrine may be a list.
- Track `active` is a trigger that gates sub-doctrine selection and mastery gain (including banked mastery).
- Use `equipment_bonus` in doctrine blocks, not the `add_equipment_bonus` effect, because only the former is removed when the doctrine changes.

Effects: `set_grand_doctrine = id`, `set_sub_doctrine = id` or the extended form with `sub_doctrine`, `folder`, `track` (0-based index among all tracks in the folder), `add_mastery`, `add_daily_mastery`, `add_mastery_bonus`, and `add_doctrine_cost_reduction` (a limited-use cost reduction).
Filters on the mastery effects are `folder`, `grand_doctrine`, `sub_doctrine`, `track`, and `index`; a missing filter matches all.

Triggers: `has_doctrine` (grand or sub), `has_any_grand_doctrine = <folder>`, `has_subdoctrine_in_track = <track>`, `has_completed_subdoctrine`, `has_completed_track`, `has_mastery = { amount track }`, `has_mastery_level = { amount sub_doctrine }`, and `land_doctrine_level` (documented as checking the researched land doctrine level).

Modifiers (confirmed against `GAME/documentation/modifiers_documentation.md` and vanilla usage):

- `<folder>_doctrine_cost_factor`, for example `land_doctrine_cost_factor` and `naval_doctrine_cost_factor`.
- `<folder>_mastery_gain_factor`, for example `land_mastery_gain_factor`.
- `<track>_track_mastery_gain_factor`, for example `operations_track_mastery_gain_factor`.
- `<grand_doctrine>_mastery_gain_factor` and `<sub_doctrine>_mastery_gain_factor`.
- The installed `_documentation.md` writes the folder form as `land_track_mastery_gain_factor`; the modifier list and vanilla ideas use `land_mastery_gain_factor`, so use the latter.

Details for writing a new folder, grand doctrine, track, and sub-doctrine, their localisation and sprites, and the interface notes are in `references/doctrine-authoring.md`.

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

## Tools

The `hoi4_agent_tools` technology tools are read-only.
Verify with the connected tool list before relying on them; first call returns a resource link and a code such as `TECH_INSPECTED_PARTIAL`.

- `hoi4.tech_inspect` `mode`: `scan`, `folders`, `trace` (with `direction`, `maxDepth`), `explain`, `unlocks` (with `technologyId` or a `targetId` and `targetKind`), `bonus_coverage`, `lint`, `impact` (rename or removal), `helper_expansion`.
  Narrow with `technologyId`, `folderId`, or `categoryId`.
- `hoi4.tech_render` `view`: `summary`, `folder`, `dependencies`, `technology`, `doctrine`, `exclusive`, `memberships`, `bonuses`, `grants`, `unlocks`, `metadata`, `assets`, `unresolved`; an optional `scenario` takes a year and researched ids.
- `hoi4.tech_inspect` with `mode: "compare"` compares revisions or proposed sources; it never writes.
- On a large workspace the first call reports `validation.passed = false` with the check "Helper projections were deferred"; the counts, folder list, and linked artifact are still usable evidence, and the deferral is not a defect.
- Follow the repository retry rule: one read-only request plus at most one corrected retry per failure, then read source directly and say the check was not run.
- Use `helper_expansion` only after confirming the server version and task negotiation as required by `CLAUDE.md`.

## Common mistakes and silent failures

- Tech is unreachable: no `path` parent, no gridbox for a tech without `path`, no `folder` block, or `allow_branch` is false.
- A tech without `path` parents and without its own gridbox definition in the folder window does not render (wiki).
- Tech shows but cannot be researched: `allow` is false, which is the intended hidden-tech pattern.
- Equipment or sub-unit still locked: the tech lists a mistyped id, the tech was not granted, or the object is `active = yes` elsewhere.
- `on_research_complete` did not fire for a starting tech: history-file techs do not run it.
- Unresearching a tech with `set_technology = { x = 0 }` leaves unlocks usable and cannot remove exclusive techs.
- A category-based bonus does nothing: the category is not in `technology_tags`, or the technology does not list it in `categories`.
- `XOR` written on one side only does not make the techs exclusive.
- Doctrine rewards named in the wrong order: milestones follow the order of `tracks` in the grand doctrine; rewards follow the list order in the sub-doctrine.
- `set_grand_doctrine` or `set_sub_doctrine` used with an id from the documentation example instead of a vanilla id.
- A track filter `index` or `track` number is 0-based among all tracks in the folder.
- A technology cost change is ignored because a `start_year` far in the future adds large ahead-of-time penalties; compute the cost with the defines before balancing.

## Validation

- `hoi4.tech_inspect` with `mode = unlocks` or `trace` on each new technology, and `lint` for the changed folder when the workspace allows it.
- `hoi4.script_validate` on effect and trigger bodies with `scope = country`.
- Check each `enable_*` id resolves with `hoi4.source_lookup`, each category exists, each localisation key and sprite exists, and the folder interface pieces exist for any visible folder.
- For doctrines, confirm every track listed in a grand doctrine exists, every sub-doctrine names a valid track, the milestone count equals the track count, and each reward has a localisation key.
- Report the checks that were not run, such as tree layout, tooltip text, and mastery accrual rates, as unobserved.
