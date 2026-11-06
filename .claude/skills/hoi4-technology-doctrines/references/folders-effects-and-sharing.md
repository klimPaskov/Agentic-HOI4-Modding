# Hearts of Iron IV Technologies and Doctrines: Folders, research effects and sharing groups

Part of the [hoi4-technology-doctrines](../SKILL.md) skill. Read before defining technology folders and categories, scripting research effects, triggers or bonuses, or adding a technology sharing group.

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
- Folder ids use the British spelling, as in `armour_folder` and `nsb_armour_folder` in `common/technology_tags/00_technology.txt`. [vanilla-confirmed 1.19.4.1]

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
The MIO tech hooks are really spelled `on_mio_tech_reseach_*`, so copy that spelling exactly. [docs] [vanilla-confirmed 1.19.3]

Limited bonuses are consumed by the research that uses them; the interface text keys `RESEARCH_BONUS_USED` and `RESEARCH_BONUS` in `core_l_english.yml` describe the behaviour.
`NDefines.NTechnology.USE_BONUS_REGRET_TIMER` gives three days to reverse a use.

`add_tech_bonus` takes its category from `common/technology_tags/00_technology.txt`, where `construction_tech` is valid and `construction` is not, and `research_bonus` is an idea key rather than an effect. [vanilla-confirmed 1.19.4.1]

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

