# Doctrine authoring

Read this file when you add or change a doctrine folder, grand doctrine, track, or sub-doctrine.
`GAME` is the installed Hearts of Iron IV folder named in `CLAUDE.md`.
The syntax comes from the four `_documentation.md` files under `GAME/common/doctrines/` and the vanilla files named below.

## Object model and file layout

| Object | Folder under `common/doctrines/` | Role |
| --- | --- | --- |
| Folder | `folders/` | A tab such as `land`, `naval`, `air`, `special_forces`; one grand doctrine active per folder |
| Grand doctrine | `grand_doctrines/` | Root of a folder; chosen with experience; lists the tracks and the milestones |
| Track | `tracks/` | A slot for one sub-doctrine; defines the default mastery sources |
| Sub-doctrine | `subdoctrines/` (any subfolder) | Chosen into a track with experience; carries the rewards |

A track is tiny.
The sub-doctrine says which track it fits, and the grand doctrine says which tracks it has.
A milestone is the grand doctrine's extra reward for completing a track; milestones are in the same order as `tracks`.

## Folder

```
my_folder = {
	allowed = { always = yes }		# false hides the folder
	name = "my_folder_loc_key"
	tab_gfx = GFX_my_doctrine_tab_large	# tab button sprite
	color_frame = 1				# frame index used by UI colouring
	ledger = army				# army, navy, air, all, hidden
	ledger_gfx = GFX_my_doctrine_folder_icon
	sound = ui_doctrine_tab_land
}
```

Vanilla: `GAME/common/doctrines/folders/doctrine_folders.txt`.
The vanilla tab sprites are `GFX_landdoctrine_tab_large` and similar in `GAME/interface/countrytechtreeview.gfx`; the ledger icons live there too (`GFX_land_doctrine_folder_icon`).
Modifiers for a new folder automatically exist as `<folder>_doctrine_cost_factor` and `<folder>_mastery_gain_factor` (see the modifier list in `SKILL.md`).

## Track

```
my_track = {
	name = DOCTRINE_TRACK_MY_TRACK		# loc key
	background = GFX_my_track_bg
	background_offset = 10			# optional horizontal offset
	frame = GFX_my_track_frame		# optional
	icon = GFX_my_track_milestone_icon
	icon_frame = GFX_doctrine_decor_land
	active = { }				# optional: gates selection and mastery gain, including banked mastery
	mastery = {
		multiplier = 1.0		# higher means less manpower is needed for the same mastery
		sub_units = { }		# specific sub-units that contribute
		categories = { category_all_infantry }
		equipment = { }		# sub-units with these equipment categories contribute
	}
}
```

Vanilla: `GAME/common/doctrines/tracks/land_doctrine_tracks.txt` (`infantry`, `combat_support`, `armor`, `operations`).
Vanilla sprites: `GFX_doctrine_milestone_armored_land`, `GFX_doctrine_decor_land` in `GAME/interface/doctrines/doctrines.gfx`.
Track mastery sources can be overridden per sub-doctrine.

## Grand doctrine

```
my_grand_doctrine = {
	folder = my_folder
	name = GRAND_DOCTRINE_MY_GRAND_DOCTRINE
	description = GRAND_DOCTRINE_MY_GRAND_DOCTRINE_DESC
	icon = GFX_doctrine_my_grand_doctrine_medium
	available = { always = yes }
	visible = { }				# optional
	xp_cost = 100
	xp_type = army				# army, navy, or air
	ai_will_do = {
		base = 1
		modifier = { factor = 0 is_major = no }
	}
	tracks = { infantry armor }
	max_track_rows = 2			# optional
	max_track_columns = 2			# optional

	# activation effects (see below)
	planning_speed = 0.20
	enable_tactic = tactic_unexpected_thrust

	milestones = {				# same order as tracks
		{ org_loss_when_moving = -0.15 enable_tactic = tactic_delay }
		{ additional_brigade_column_size = 1 }
	}
}
```

Vanilla: `GAME/common/doctrines/grand_doctrines/land_grand_doctrines.txt`.
Vanilla milestones also run a small `effect` block that increments a counter variable; copy that only when a script needs to count milestones.

## Sub-doctrine

```
my_subdoctrine = {
	track = armor				# a single track or a list { infantry armor }
	allow_in_multiple_tracks = yes		# optional
	name = SUBDOCTRINE_MY_SUBDOCTRINE
	description = SUBDOCTRINE_MY_SUBDOCTRINE_DESC
	icon = GFX_doctrine_my_subdoctrine_medium
	reward_gfx = GFX_my_reward_strip	# optional: frames 1..X are rewards, X+1..2X the greyed versions
	xp_cost = 100
	xp_type = army
	available = { always = yes }
	visible = { }
	ai_will_do = { base = 1 }
	xor = { other_subdoctrine }		# optional mutual exclusion across tracks in the folder

	# activation effects on selection
	enable_tactic = tactic_breakthrough

	rewards = {
		first_reward = {		# named block: loc key <subdoctrine>_first_reward
			category_tanks = { max_organisation = 2 default_morale = 0.05 }
		}
		second_reward = {
			mastery = 150		# optional: overrides NDoctrines DEFAULT_REWARD_MASTERY
			category_all_armor = { breakthrough = 0.1 }
		}
	}

	mastery = {				# optional override of the track's mastery sources
		multiplier = 5.0
		sub_units = { bicycle_battalion }
		categories = { }
		equipment = { }
	}
}
```

Vanilla: `GAME/common/doctrines/subdoctrines/land/armor_subdoctrines.txt` (named rewards; a DLC-split pair `armored_spearhead` and `armored_spearhead_no_lar` differing only in `visible`), `infantry_subdoctrines.txt` (a `mastery` override at line ~394), `special_forces/special_forces_subdoctrines.txt` (`xor`).
The `_documentation.md` example shows unnamed `{ }` reward blocks and a TODO about unlocking; vanilla uses named blocks, so name every reward and write its localisation.

## Activation effects (all four object levels)

- Country modifiers directly, or inside `modifiers = { }`.
- `enable_tactic = tactic_name`; tactics are defined in `GAME/common/combat_tactics.txt`.
- Sub-unit or category stat blocks: `category_tanks = { max_organisation = 1 }` and `armored_car = { max_organisation = 2 }`.
- `equipment_bonus = { capital_ship = { naval_range = 0.10 instant = yes } }`; removed when the doctrine is replaced.
- `effect = { ... }` for scripted effects, for example `add_tech_bonus`.

The documentation states only that `equipment_bonus` is removed when the doctrine changes, and that the `add_equipment_bonus` effect is not.
Treat an `effect` block as a one-time scripted effect with no documented removal, and do not put state changes there that must be undone when the doctrine is replaced.

## Localisation

Read `GAME/localisation/english/doctrines_l_english.yml` for the full set.
Keys seen there:

- `GRAND_DOCTRINE_<NAME>` and `GRAND_DOCTRINE_<NAME>_DESC` (the loc keys are whatever `name` and `description` name).
- `SUBDOCTRINE_<NAME>` and `SUBDOCTRINE_<NAME>_DESC`.
- `<subdoctrine>_<reward>` for each named reward.
- `DOCTRINE_TRACK_<NAME>` for the track name.
- `<folder>` name key through the folder `name`.
- Mastery gain modifier text is generated automatically for the documented modifier families, so no hand-written key is needed for them.
- Window text keys such as `DOCTRINE_MILESTONE_TITLE` and `MILESTONE_UNLOCK_EXPLANATION` are shared and should not be redefined.

Localisation files are UTF-8 with BOM; a DLC-split sub-doctrine needs its reward keys defined for both ids, vanilla reuses the text with `$armored_spearhead_force_concentration$`.

## Graphics and interface

- Sprites for grand doctrine and sub-doctrine icons: `GFX_doctrine_<name>_medium`, defined as `SpriteType` entries in `GAME/interface/doctrines/doctrines.gfx` (for example `GFX_doctrine_mobile_warfare_medium`, `GFX_doctrine_armored_spearhead_medium`).
- Reward strips, mastery bars, and frames: `GFX_mastery_reward_level`, `GFX_mastery_reward_icons`, `GFX_mastery_reward_frame` in the same file.
- The doctrine window is `GAME/interface/doctrines/doctrines_view.gui`.
  Its `folders_grid` carries the comment "Will be filled with *doctrine_folder_tab*", and the file defines generic `doctrine_list_item`, `doctrine_track_item`, and `reward_item` templates with no per-folder containers, so the window appears to build folders, tracks, and rewards from data; the `tab_gfx` field in the folder documentation ("tab button icon to be displayed at the top of the doctrine UI") is the expected way to set a new tab image.
  This reading comes from the file structure and was not confirmed in the game.
- `GAME/interface/countrytechtreeview.gui` and `countrydoctrinetreeview.gui` hold the older technology-based doctrine folder windows (`land_doctrine_folder` and the like).
  The current doctrine system does not need them, and `hoi4.tech_inspect` reports `legacyDoctrines: 0` for the repository workspace.
  Visual placement was not checked in the game.

## Assigning doctrines to countries

- Country history: `set_grand_doctrine = new_mobile_warfare` and `set_sub_doctrine = mobile_infantry` appear in vanilla history files (for example `GAME/history/countries/GER - Germany.txt`, which also gates them in date blocks).
- In a focus, event, or decision: `set_grand_doctrine` unlocks and assigns; `set_sub_doctrine` uses the first matching track unless `folder` and `track` are given.
- Mastery boosts in vanilla: `add_mastery_bonus = { bonus = 0.15 days = 180 name = KEY track = operations }` in `GAME/common/decisions/JAP.txt`.
- Idea modifiers: `land_mastery_gain_factor = 0.1`, `new_mobile_warfare_mastery_gain_factor = 0.15`, `operations_track_mastery_gain_factor = 0.15`; cost: `land_doctrine_cost_factor = 0.2`.

## Consistency checklist

1. Every `tracks` entry in the grand doctrine exists in `tracks/`.
2. Every sub-doctrine `track` entry exists and is listed in at least one grand doctrine of that folder.
3. `milestones` contains one block per track, in the track order.
4. `xp_type` matches the folder's intended experience pool.
5. `ai_will_do` exists on grand doctrines and sub-doctrines the AI should choose; the documentation does not state the AI behaviour when it is missing.
6. Names, descriptions, rewards, and track names have localisation keys.
7. Icons are registered in a `.gfx` file.
8. `xor` lists are symmetric where exclusivity is intended.
9. Sub-doctrine rewards that use unit categories use categories from `GAME/common/unit_tags/00_categories.txt` or valid sub-unit ids.
10. Mastery sources in the track or override cover sub-units the country will actually field, otherwise mastery never accrues.
