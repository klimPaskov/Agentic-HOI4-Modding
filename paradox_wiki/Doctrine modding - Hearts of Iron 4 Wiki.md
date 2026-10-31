# Doctrine modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Doctrine modding", revision 96850, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="96850" sources="common/doctrines/ documentation/effects_documentation.md documentation/triggers_documentation.md documentation/modifiers_documentation.md common/defines/00_defines.lua common/ai_strategy/doctrines.txt common/script_enums.txt interface/doctrines/ localisation/english/doctrines_l_english.yml" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against `common/doctrines/_documentation.md` and the four sub-folder documentation files, every vanilla file in `common/doctrines/` (4 folders, 12 grand doctrines, 14 tracks, 95 subdoctrines), the effect, trigger and modifier documentation, the `NDoctrines` and AI defines, and the doctrine GUI and localisation files.
Kit blocks added: `doctrine-lists-swapped` (the wiki's two lists carry each other's headings), `doctrine-overview`, `doctrine-effects-triggers`, `doctrine-folders`, `doctrine-grand-doctrines`, `doctrine-tracks`, `doctrine-subdoctrines`, `doctrine-mastery`, `doctrine-modifiers-ai`, `doctrine-example`, `doctrine-traps`.
Gaps left: the exact mastery formula (diminishing returns, reserve mechanics) is known only from defines and localisation; fewer than four rewards per subdoctrine and a `modifiers = { }` block were not observed in vanilla.
<!-- kit:end id="review" -->

## Table of contents

- [Structure](#Structure)
  - [Kit: How the doctrine files link](#kit-doctrine-overview)
- [Triggers and Effects](#Triggers_and_Effects)
  - [List of doctrine-related triggers:](#List_of_doctrine-related_triggers:)
  - [List of doctrine-related effects:](#List_of_doctrine-related_effects:)
    - [Kit: Doctrine effect and trigger syntax](#kit-doctrine-effects-triggers)
- [Folders](#Folders)
  - [Kit: Folder files](#kit-doctrine-folders)
- [Grand Doctrines](#Grand_Doctrines)
  - [Kit: Grand doctrine files](#kit-doctrine-grand-doctrines)
- [Tracks](#Tracks)
  - [Kit: Track files](#kit-doctrine-tracks)
- [Subdoctrines](#Subdoctrines)
  - [Kit: Subdoctrine files](#kit-doctrine-subdoctrines)
- [Kit: Mastery](#kit-doctrine-mastery)
- [Kit: Doctrine modifiers, localisation and AI](#kit-doctrine-modifiers-ai)
- [Kit: Minimal grand doctrine with one track and one subdoctrine](#kit-doctrine-example)
- [Kit: Doctrine traps](#kit-doctrine-traps)

---

\*Please help improve this article or section by expanding it .\*

## Structure <a id="Structure"></a>

The files are structured as follows:

- `common/doctrines/folders/*.txt` - Doctrine folders
- `common/doctrines/grand_doctrines/*.txt` - Grand Doctrines
- `common/doctrines/tracks/*.txt` - Subdoctrine Tracks
- `common/doctrines/subdoctrines/*.txt` (or any subfolder) - Subdoctrines

<!-- kit:begin id="doctrine-overview" at="section:Structure" -->
### Kit: How the doctrine files link <a id="kit-doctrine-overview"></a>

**Kit addition** Vocabulary of the doctrine system: a **folder** is a doctrine category, a **grand doctrine** is the mutually exclusive root of a folder and is bought with XP, a **track** is a slot for one subdoctrine and its rewards, a **milestone** is the extra reward for completing a track, a **subdoctrine** is the root of one track and is bought with XP, **mastery** is the progress inside a track, and a **reward** is unlocked by mastery and belongs to a subdoctrine. [docs] `common/doctrines/_documentation.md`

| File kind | Key that links it | Points at |
| --- | --- | --- |
| Grand doctrine | `folder = land` | a folder id |
| Grand doctrine | `tracks = { infantry armor }` | track ids, in display order |
| Grand doctrine | `milestones = { { ... } { ... } }` | one anonymous block per entry of `tracks`, same order |
| Subdoctrine | `track = infantry` or `track = { a b }` | track ids it can be slotted into |
| Track | (none) | the track file names no folder, grand doctrine or subdoctrine |

The track file is deliberately tiny: the subdoctrine names the track it fits, and the grand doctrine names the tracks it contains. [docs] `common/doctrines/tracks/_documentation.md`

Vanilla size in 1.19.3: 4 folders (`folders/doctrine_folders.txt`), 12 grand doctrines in 4 files, 14 tracks in 4 files, 95 subdoctrines in 13 files under `subdoctrines/air/`, `land/`, `sea/` and `special_forces/`. The wiki says subdoctrine files may sit in any subfolder; the other three kinds are flat in vanilla. [vanilla-confirmed 1.19.3] `common/doctrines/`

The doctrine window is built from this data. `interface/doctrines/doctrines_view.gui` has an empty `folders_grid` that the game fills with one `doctrine_folder_tab` per folder, and a `tracks_grid` sized by code from the number of tracks, so a new folder, track, grand doctrine or subdoctrine needs sprites and localisation but no new container window. The `countrydoctrinetreeview.gui` containers that the Technology modding page describes belong to the old tech-based doctrine screen: none of the 552 vanilla technologies uses `doctrine = yes`. [vanilla-confirmed 1.19.3] `interface/doctrines/doctrines_view.gui`, `common/technologies/`

The grand doctrine ids the game uses are `new_mobile_warfare`, `superior_firepower`, `grand_battleplan`, `mass_assault`, `new_fleet_in_being`, `new_convoy_raiding`, `new_base_strike`, `new_strategic_destruction`, `new_battlefield_support`, `new_operational_integrity`, `special_forces_quantity` and `special_forces_quality`. The id `mobile_warfare`, which the effect and trigger documentation use in their examples, is not a vanilla grand doctrine id. [vanilla-confirmed 1.19.3] `common/doctrines/grand_doctrines/` (12 ids)
<!-- kit:end id="doctrine-overview" -->

## Triggers and Effects <a id="Triggers_and_Effects"></a>

### List of doctrine-related triggers: <a id="List_of_doctrine-related_triggers:"></a>

<!-- kit:begin id="doctrine-lists-swapped" at="heading:List_of_doctrine-related_triggers:" -->
**Kit correction** The two list headings are swapped. The first list (`set_grand_doctrine`, `set_sub_doctrine`, `add_mastery`, `add_daily_mastery`, `add_mastery_bonus`) holds effects, and the second list (`has_any_grand_doctrine`, `has_completed_subdoctrine`, `has_doctrine`, `has_completed_track`, `has_subdoctrine_in_track`, `has_mastery`, `has_mastery_level`) holds triggers. All twelve run in country scope. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md` (scope COUNTRY for each). `has_any_grand_doctrine` is missing from `common/doctrines/_documentation.md` but is in the trigger documentation. [docs]
<!-- kit:end id="doctrine-lists-swapped" -->

- set_grand_doctrine - Gives a country the specified grand doctrine.
- set_sub_doctrine - Gives a country the specified subdoctrine.
- add_mastery - Adds doctrine mastery.
- add_daily_mastery - Gives daily mastery for a specified duration
- add_mastery_bonus - Get a bonus to doctrine mastery gain for a certain duration.

### List of doctrine-related effects: <a id="List_of_doctrine-related_effects:"></a>

- has_any_grand_doctrine - Checks if any grand doctrine in folder is currently active for the country.
- has_completed_subdoctrine - Checks if the current country has ever completed the specified subdoctrine (even if it was later switched out).
- has_doctrine - Checks if the given grand doctrine or subdoctrine is currently active for the country.
- has_completed_track - Checks if the given subdoctrine track has been completed
- has_subdoctrine_in_track - Checks if any subdoctrine is currently assigned to (any instance of) the given track.
- has_mastery - Checks if any track of the given type has at least X mastery.
- has_mastery_level - Checks if the country has reached the specified number of mastery levels (rewards) for the given subdoctrine.

<!-- kit:begin id="doctrine-effects-triggers" at="section:List_of_doctrine-related_effects:" -->
#### Kit: Doctrine effect and trigger syntax <a id="kit-doctrine-effects-triggers"></a>

**Kit addition** Effects, all in country scope. Syntax and filters: [docs] `documentation/effects_documentation.md`.

| Effect | Syntax | Notes |
| --- | --- | --- |
| `set_grand_doctrine` | `set_grand_doctrine = new_mobile_warfare` | Activates (unlocks and assigns) the grand doctrine. Vanilla country history files call it at top level, one line per folder. |
| `set_sub_doctrine` | `set_sub_doctrine = mobile_infantry`, or a block with `sub_doctrine`, optional `folder`, optional `track` | Without a block it goes into the first matching track. `track` is a 0-based index among all tracks of the folder, not only the matching ones. |
| `add_mastery` | block with `amount` plus filters | One-time mastery. |
| `add_daily_mastery` | block with `amount` (per day), `days`, `name` plus filters | `name` is a localisation key shown as the source of the gain. |
| `add_mastery_bonus` | block with `bonus` (0.1 is +10%), `days`, `name` plus filters | Temporary factor on mastery gain. |
| `add_doctrine_cost_reduction` | block with `name`, `cost_reduction`, `uses`, `category` | Limited-use XP discount. `category` is a technology category such as `land_doctrine`, `air_doctrine`, `naval_doctrine` or `special_forces_doctrine`. |

Mastery filters, all optional: `folder`, `grand_doctrine`, `sub_doctrine`, `track`, and `index` (0-based track index within the folder). A missing filter passes, so a block with only `amount` hits every active track of every folder. [docs] `documentation/effects_documentation.md`

```text
add_mastery_bonus = {
    bonus = 0.15
    days = 180
    name = JAP_supreme_council_for_direction_of_war
    track = operations
}
add_doctrine_cost_reduction = {
    name = CZE_send_observers_to_the_italo_ethiopian_war
    cost_reduction = 0.05
    uses = 1
    category = land_doctrine
}
```

`add_doctrine_cost_reduction` appears in 79 vanilla files; `category` is `land_doctrine` in 183 blocks, `air_doctrine` in 121, `naval_doctrine` in 111, `special_forces_doctrine` in 83 and `cat_marines_doctrine` in 3, all names from `technology_categories`. `add_mastery_bonus` appears in 41 files, `add_mastery` in 22, `add_daily_mastery` in 2, `set_sub_doctrine` in 10 and `set_grand_doctrine` in 319 (318 of them under `history/`). The two snippets come from `common/decisions/JAP.txt` and `common/decisions/CZE.txt`. [vanilla-confirmed 1.19.3]

Triggers, all in country scope. [docs] `documentation/triggers_documentation.md`

| Trigger | Syntax | True when |
| --- | --- | --- |
| `has_any_grand_doctrine` | `= land` | any grand doctrine is assigned to that folder |
| `has_doctrine` | `= new_mobile_warfare` or `= mobile_infantry` | that grand doctrine or subdoctrine is currently active |
| `has_completed_subdoctrine` | `= mobile_infantry` | the subdoctrine was ever completed, even if swapped out later |
| `has_completed_track` | `= infantry` | the track is completed |
| `has_subdoctrine_in_track` | `= infantry` | some subdoctrine sits in any instance of the track |
| `has_mastery` | `{ amount = 200 track = infantry }` | any track of that type has at least that mastery |
| `has_mastery_level` | `{ amount = 2 sub_doctrine = mobile_infantry }` | that many rewards of the subdoctrine are reached |

Vanilla uses `has_doctrine` in 16 files, `has_mastery_level` in 3, `has_completed_track` in 2 (including `common/achievements.txt`), `has_completed_subdoctrine` and `has_subdoctrine_in_track` in 1 each, and `has_any_grand_doctrine` and `has_mastery` in none. [vanilla-confirmed 1.19.3] `common/`, `events/`, `history/`

The documentation also lists the trigger `land_doctrine_level` ("checks researched land doctrine level"). No vanilla file uses it, and whether it still returns anything now that doctrines are not technologies is not confirmed. [docs] `documentation/triggers_documentation.md` [unverified]
<!-- kit:end id="doctrine-effects-triggers" -->

## Folders <a id="Folders"></a>

<!-- kit:begin id="doctrine-folders" at="section:Folders" -->
### Kit: Folder files <a id="kit-doctrine-folders"></a>

**Kit addition** Folders live in `common/doctrines/folders/*.txt`. A folder is the top-level category; each grand doctrine belongs to exactly one folder, and a custom folder may have any name. [docs] `common/doctrines/folders/_documentation.md`

| Key | Type | Meaning |
| --- | --- | --- |
| block name | identifier | Folder id. Used by `folder =` in grand doctrines, by the mastery filters, by `has_any_grand_doctrine` and in generated modifier names. |
| `allowed` | trigger block | If it is false the folder is not available. Vanilla `special_forces` requires `has_dlc` "No Compromise, No Surrender" or "Arms Against Tyranny"; the other three use `always = yes`. |
| `name` | localisation key | Folder title. Vanilla values are `land_doctrine_folder`, `naval_doctrine_folder`, `air_doctrine_folder` and `OFFICER_CORP_SPECIAL_FORCES_DOCTRINE`. |
| `tab_gfx` | sprite | Tab button at the top of the doctrine window. Vanilla tab sprites have 2 frames. |
| `color_frame` | integer | Frame index for window pieces whose background colour depends on the folder. Vanilla: land 1, naval 2, air 3, special_forces 4. |
| `ledger` | enum | Intelligence ledger that shows the folder: `army`, `navy`, `air`, `all` or `hidden`. Vanilla uses `army` (land, special_forces), `navy` (naval) and `air`. |
| `ledger_gfx` | sprite | Button icon in the ledger. |
| `sound` | sound effect | Played when the player switches to the folder. Vanilla uses `ui_doctrine_tab_land`, `_naval`, `_air` and `_special_forces`. |

Key list and meanings: [docs] `common/doctrines/folders/_documentation.md`. Vanilla values: [vanilla-confirmed 1.19.3] `common/doctrines/folders/doctrine_folders.txt`.

The folder ids are `land`, `naval`, `air` and `special_forces`. The navy folder is `naval`, but the XP type of its doctrines is `navy`. [vanilla-confirmed 1.19.3] `common/doctrines/folders/doctrine_folders.txt`, `common/doctrines/grand_doctrines/sea_grand_doctrines.txt`

```text
my_folder = {
    allowed = { always = yes }
    name = my_doctrine_folder
    tab_gfx = GFX_landdoctrine_tab_large
    color_frame = 1
    ledger = army
    ledger_gfx = GFX_land_doctrine_folder_icon
    sound = ui_doctrine_tab_land
}
```

Vanilla defines `<name>` and `<name>_desc` for the three base folders (`land_doctrine_folder` and `land_doctrine_folder_desc` in `localisation/english/research_l_english.yml`), and the sprites `GFX_landdoctrine_tab_large` and `GFX_land_doctrine_folder_icon` in `interface/countrytechtreeview.gfx`. [vanilla-confirmed 1.19.3] Whether the doctrine window reads the `_desc` key is [unverified].
<!-- kit:end id="doctrine-folders" -->

## Grand Doctrines <a id="Grand_Doctrines"></a>

<!-- kit:begin id="doctrine-grand-doctrines" at="section:Grand_Doctrines" -->
### Kit: Grand doctrine files <a id="kit-doctrine-grand-doctrines"></a>

**Kit addition** Grand doctrines live in `common/doctrines/grand_doctrines/*.txt`. The player picks any available grand doctrine of a folder and pays its XP; this applies its immediate effects and makes its tracks available. Each track has a milestone, a further reward for completing that track. [docs] `common/doctrines/grand_doctrines/_documentation.md`

| Key | Type | Meaning |
| --- | --- | --- |
| block name | identifier | Grand doctrine id (`has_doctrine`, `set_grand_doctrine`, the `<id>_mastery_gain_factor` modifier). |
| `folder` | folder id | The folder it belongs to. |
| `name` | localisation key | Title. |
| `description` | localisation key | Description, may be bound loc. |
| `icon` | sprite | GFX name. |
| `available` | trigger block | Whether it can be selected. |
| `visible` | trigger block | Whether it is shown in the list at all. |
| `xp_cost` | integer | XP price. |
| `xp_type` | `army`, `navy` or `air` | Which XP pool pays. |
| `ai_will_do` | weight block | AI desire. |
| `tracks` | list of track ids | The tracks this grand doctrine offers, in display order. |
| `max_track_rows`, `max_track_columns` | integer | Optional limits for the track grid; unlimited by default. |
| `milestones` | list of anonymous blocks | One block per track, in the same order as `tracks`. Each holds activation effects. |
| activation effects | modifiers, `enable_tactic`, unit stats, `equipment_bonus`, `effect` | Applied on activation; see below. |

Table: [docs] `common/doctrines/grand_doctrines/_documentation.md`. Every vanilla grand doctrine sets all of these except `visible`, `max_track_rows` and `max_track_columns`, which no vanilla grand doctrine uses. [vanilla-confirmed 1.19.3] `common/doctrines/grand_doctrines/*.txt` (12 of 12)

Activation effects are shared by grand doctrines, milestones, subdoctrines and rewards. [docs] `common/doctrines/grand_doctrines/_documentation.md`

| Form | Example | Notes |
| --- | --- | --- |
| Country modifier | `planning_speed = 0.20` | Written directly. The documentation also allows an explicit `modifiers = { ... }` block, which no vanilla doctrine file uses. |
| Tactic | `enable_tactic = tactic_unexpected_thrust` | Tactic ids come from `common/combat_tactics.txt`. |
| Unit stat bonus | `category_tanks = { max_organisation = 1 }` or `armored_car = { ... }` | The key is a unit category or a sub-unit id. A terrain block may nest inside (`snow = { attack = 0.15 }`). |
| Equipment bonus | `equipment_bonus = { capital_ship = { naval_range = 0.10 instant = yes } }` | Use this, not the `add_equipment_bonus` effect, because the effect does not remove the bonus when the doctrine changes. The key is an equipment type, archetype or equipment group. |
| Scripted effect | `effect = { add_tech_bonus = { ... } }` | Any country effect, for example `add_tech_bonus` or `unlock_subunit`. |

The forms and the equipment bonus remark: [docs] `common/doctrines/grand_doctrines/_documentation.md`. Vanilla confirms `snow` inside a unit block and `effect = { unlock_subunit = rangers_support }` in `common/doctrines/subdoctrines/special_forces/special_forces_subdoctrines.txt`, and tactic ids in `common/combat_tactics.txt`. [vanilla-confirmed 1.19.3] Equipment groups are defined as the [Equipment modding](<Equipment modding - Hearts of Iron 4 Wiki.md>) page and `common/equipment_groups/_documentation.md` describe. [docs]

Vanilla grand doctrines. [vanilla-confirmed 1.19.3] `common/doctrines/grand_doctrines/`

| Folder | `xp_type` | `xp_cost` | Ids | Tracks (in order) |
| --- | --- | --- | --- | --- |
| land | army | 100 | `new_mobile_warfare`, `superior_firepower`, `grand_battleplan`, `mass_assault` | `infantry`, `combat_support`, `armor`, `operations` |
| naval | navy | 100 | `new_fleet_in_being`, `new_convoy_raiding`, `new_base_strike` | `submarines`, `screens`, `carriers`, `capital_ships` |
| air | air | 100 | `new_strategic_destruction`, `new_battlefield_support`, `new_operational_integrity` | `fighter_aircraft`, `strike_aircraft`, `medium_aircraft`, `heavy_aircraft` |
| special_forces | army | 60 | `special_forces_quantity`, `special_forces_quality` | `special_forces_first`, `special_forces_second` |

The vanilla AI weight for the base folders is `base = 1` with `modifier = { factor = 0 is_major = no }`. Names are plain localisation keys: id `new_mobile_warfare` uses `name = GRAND_DOCTRINE_MOBILE_WARFARE` and `description = GRAND_DOCTRINE_MOBILE_WARFARE_DESC`. Icons are `GFX_doctrine_<x>_medium` sprites in `interface/doctrines/doctrines.gfx`. [vanilla-confirmed 1.19.3] `localisation/english/doctrines_l_english.yml`, `interface/doctrines/doctrines.gfx`
<!-- kit:end id="doctrine-grand-doctrines" -->

## Tracks <a id="Tracks"></a>

<!-- kit:begin id="doctrine-tracks" at="section:Tracks" -->
### Kit: Track files <a id="kit-doctrine-tracks"></a>

**Kit addition** Tracks live in `common/doctrines/tracks/*.txt`. A track becomes available once a grand doctrine that lists it is active. It holds a subdoctrine at its root, a series of rewards that unlock automatically as mastery grows, and a milestone from the grand doctrine that fires once every reward is unlocked. [docs] `common/doctrines/tracks/_documentation.md`

| Key | Type | Meaning |
| --- | --- | --- |
| block name | identifier | Track id (`track =` in subdoctrines, `tracks = { }` in grand doctrines, mastery filters, `has_completed_track`). |
| `name` | localisation key | Track title, may be bound loc. |
| `background` | sprite | Background image of the track column. |
| `background_offset` | integer | Horizontal offset of the background. |
| `frame` | sprite | Frame image around the track. |
| `icon` | sprite | Milestone icon. |
| `icon_frame` | sprite | Frame around the milestone icon. |
| `active` | trigger block | While false, subdoctrines of the track cannot be selected and mastery gain, including banked mastery, is off. |
| `mastery` | block | What counts towards mastery: `multiplier`, `sub_units`, `categories`, `equipment` (see the mastery block below). |

Table: [docs] `common/doctrines/tracks/_documentation.md`. Vanilla tracks set only `name`, `background`, `icon`, `icon_frame` and `mastery`. `active` appears once, on `special_forces_second` (`can_unlock_second_track_of_sf_doctrine = yes`, a scripted trigger that checks the variable `sf_trees`); `frame` and `background_offset` are never used. [vanilla-confirmed 1.19.3] `common/doctrines/tracks/*.txt`, `common/scripted_triggers/00_scripted_triggers.txt`

Vanilla track ids. [vanilla-confirmed 1.19.3] `common/doctrines/tracks/`

| File | Track ids | Mastery source |
| --- | --- | --- |
| `land_doctrine_tracks.txt` | `infantry`, `combat_support`, `armor`, `operations` | `categories` (`category_all_infantry`, `category_tanks`, ...); `armor` also lists `sub_units = { armored_car }` |
| `sea_doctrine_tracks.txt` | `capital_ships`, `carriers`, `screens`, `submarines` | `equipment = { capital_ship }`, `carrier`, `screen_ship`, `submarine` |
| `air_doctrine_track.txt` | `fighter_aircraft`, `strike_aircraft`, `medium_aircraft`, `heavy_aircraft` | `equipment` lists such as `fighter interceptor` |
| `special_forces_tracks.txt` | `special_forces_first`, `special_forces_second` | `categories = { category_special_forces }` |

Sprites: the track backgrounds (`GFX_grand_battleplan_bg`, `GFX_mob_warfare_bg` and the others) are defined in `interface/countrytechnologyview.gfx`; the milestone icons and decor frames (`GFX_doctrine_milestone_infantry_land`, `GFX_doctrine_decor_land`, 2 frames each) are in `interface/doctrines/doctrines.gfx`. The track title key is its `name` (`DOCTRINE_TRACK_INFANTRY` and siblings in `localisation/english/doctrines_l_english.yml`). [vanilla-confirmed 1.19.3]
<!-- kit:end id="doctrine-tracks" -->

## Subdoctrines <a id="Subdoctrines"></a>

<!-- kit:begin id="doctrine-subdoctrines" at="section:Subdoctrines" -->
### Kit: Subdoctrine files <a id="kit-doctrine-subdoctrines"></a>

**Kit addition** Subdoctrines live in `common/doctrines/subdoctrines/` (any subfolder). A subdoctrine sits at the root of one track. Paying its XP applies its immediate effects and starts the automatic unlock of its rewards as mastery grows. [docs] `common/doctrines/subdoctrines/_documentation.md`

| Key | Type | Meaning |
| --- | --- | --- |
| block name | identifier | Subdoctrine id (`has_doctrine`, `set_sub_doctrine`, `<id>_mastery_gain_factor`). |
| `track` | track id or `{ id id }` | Track or tracks it can fill. |
| `allow_in_multiple_tracks` | `yes`/`no` | Optional, default `no`. If `yes`, the subdoctrine may sit in several tracks at the same time. |
| `name`, `description` | localisation keys | Title and description (bound loc). |
| `icon` | sprite | GFX name. |
| `available` | trigger block | Whether it can be selected. |
| `visible` | trigger block | Whether it is shown in the list at all. |
| `reward_gfx` | sprite | Optional icon strip that replaces the default reward icons: frames 1 to X are rewards 1 to X, frames X+1 to 2X are the same grayed out. |
| `xp_cost`, `xp_type` | integer, `army`/`navy`/`air` | XP price and pool. |
| `ai_will_do` | weight block | AI desire. |
| `xor` | list of subdoctrine ids | Subdoctrines that cannot be active at the same time in a different track of the same folder. Swapping this subdoctrine for an `xor` one on the same track is allowed. |
| `mastery` | block | Replaces the track's mastery conditions: `multiplier`, `sub_units`, `categories`, `equipment`. |
| activation effects | see the grand doctrine table | Applied when the subdoctrine is activated. |
| `rewards` | block of reward blocks | Unlocked in order by mastery. |

Table: [docs] `common/doctrines/subdoctrines/_documentation.md`.

Reward blocks. Each reward is a block with an optional `mastery = <number>` (mastery needed for this reward; the default is `NDefines.NDoctrines.DEFAULT_REWARD_MASTERY`, 100) and then the same activation effects as a grand doctrine. The documentation draws rewards as anonymous blocks, but all 474 vanilla rewards are named blocks (`cavalry_charge = { ... }`, or `reward_1`, `reward_2` and so on in special forces). The reward's localisation key is the subdoctrine id, an underscore and the reward id: `mobile_infantry_cavalry_charge`. [docs] `common/doctrines/subdoctrines/_documentation.md`; [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`, `localisation/english/doctrines_l_english.yml` (`mobile_infantry_cavalry_charge`, `mountaineers_1_reward_1`)

What vanilla does. [vanilla-confirmed 1.19.3] `common/doctrines/subdoctrines/`

- 95 subdoctrines; 94 have 5 rewards and `peoples_war` has 4.
- 44 rewards set `mastery`: 40 use 60 and 4 use 50. The rest use the default 100.
- `xp_cost` is 100 for 83 subdoctrines, 60 for 8 and 50 for 4.
- 92 set `available` (all but `tank_destroyer_force`, `field_engineering` and `coastal_defence_fleet`) and 85 set `ai_will_do`; the 10 without it are `battleship_antiair_screen`, `escort_carrier_support`, `broad_naval_support`, `anti_aircraft_cruisers`, `screen_support_focus`, `jeune_ecole`, `patrol_boats`, `submarine_coastal_defense`, `coastal_minelaying` and `long_range_submarines`. 47 set `visible`, usually `has_dlc = "..."` or its negation.
- `track` is a list only for the 8 special forces subdoctrines (`track = { special_forces_first special_forces_second }`), and those 8 are the only users of `xor`: `mountaineers_1` against `mountaineers_2`, and the same pairing for marines, paratroopers and rangers.
- `allow_in_multiple_tracks` and `reward_gfx` are in the documentation but unused by vanilla.
- `mastery` overrides exist in 10 subdoctrines: the 8 special forces ones (`multiplier = 6`, `categories`), `light_task_forces` (`multiplier = 2`, `sub_units`) and `mounted_infantry` (`categories` only).
- Subdoctrine `effect` blocks hold `add_tech_bonus` (`category` such as `motorized_equipment`, `rocketry`, `helicopter_tech`, `support_tech`, `cat_heavy_armor`) and `unlock_subunit`.

The sprite `GFX_mastery_reward_icons` has 10 frames in `interface/doctrines/doctrines.gfx`. If that is the default reward strip, it covers 5 rewards and a sixth reward would need `reward_gfx`. [vanilla-confirmed 1.19.3] for the frame count, [unverified] for the inference.

Localisation: `SUBDOCTRINE_<NAME>` and `SUBDOCTRINE_<NAME>_DESC` for the subdoctrine, then one key per reward. The documentation's TODO note mentions a `_desc` suffix for rewards; the reward keys checked in vanilla have only the name key. [vanilla-confirmed 1.19.3] `localisation/english/doctrines_l_english.yml`
<!-- kit:end id="doctrine-subdoctrines" -->

<!-- kit:begin id="doctrine-mastery" at="bottom" -->
## Kit: Mastery <a id="kit-doctrine-mastery"></a>

**Kit addition** Mastery rules that decide how fast rewards unlock.

- A track's `mastery` block says which units feed it. `multiplier` scales how much manpower contributes (the documentation example: 2.0 means half the manpower is needed for the same mastery). `sub_units` lists sub-unit ids, `categories` lists unit categories from `common/unit_tags/00_categories.txt`, and `equipment` lists equipment types (`capital_ship`, `carrier`, `screen_ship`, `submarine`, `fighter` and so on). The subdoctrine's own `mastery` block overrides the track's. [docs] `common/doctrines/tracks/_documentation.md`, `common/doctrines/subdoctrines/_documentation.md`
- Every `equipment` value that vanilla tracks use appears in `script_enum_equipment_category`. [vanilla-confirmed 1.19.3] `common/script_enums.txt`
- The tuning values live in `NDefines.NDoctrines`: `DEFAULT_REWARD_MASTERY` 100, `BASE_MASTERY_GAIN_TARGET_MANPOWER` 100000 (gain has diminishing returns beyond it), `TRAINING_MASTERY_GAIN_FACTOR` 0.1 (training counts a tenth of combat), `MAX_MONTHLY_MASTERY_GAIN` 40, `MIN_MASTERY_GAIN_PER_DAY` 0, `MASTERY_BANK_CONVERSION_RATE` 0.25, `MASTERY_BANK_MAX` 200, `MILITARY_ATTACHE_MASTERY_TRANSFER_FACTOR` 0.1, `THEATER_COMMANDER_UNITS_MASTERY_GAIN_FACTOR_PER_SKILL` 0.01, and `NAVAL_MISSION_MASTERY_GAIN_FACTORS` per naval mission. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` (`NDoctrines`)
- Banking: while a track is completed, or has no subdoctrine yet, a share of the mastery it gains is reserved instead (rate and cap from the two bank defines) and becomes initial mastery when a subdoctrine is assigned. Switching the grand doctrine resets all mastery. [vanilla-confirmed 1.19.3] `localisation/english/doctrines_l_english.yml` (`MASTERY_BANK_EXPLANATION_EMPTY`, `MASTERY_BANK_EXPLANATION_FULL`, `MASTERY_INITIAL_FROM_RESERVE`, `SWITCH_GRAND_DOCTRINE_MASTERY_RESET`)
- Other mastery sources shown in the interface: faction doctrine sharing (`DOCTRINE_SHARING_BASE_MASTERY_GAIN_MONTHLY` 10 and `DOCTRINE_SHARING_MONTHLY_MASTERY_GAIN_PER_COMMANDER` 2), theater commanders, military attaches and Theorist advisors. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`, `localisation/english/doctrines_l_english.yml`
- Effects that grant mastery directly are `add_mastery`, `add_daily_mastery` and `add_mastery_bonus`; the triggers that read it are `has_mastery` and `has_mastery_level` (syntax above).
<!-- kit:end id="doctrine-mastery" -->

<!-- kit:begin id="doctrine-modifiers-ai" at="bottom" -->
## Kit: Doctrine modifiers, localisation and AI <a id="kit-doctrine-modifiers-ai"></a>

**Kit addition** Country modifiers that touch doctrines. [docs] `common/doctrines/_documentation.md`, `documentation/modifiers_documentation.md`

| Modifier | Effect | Vanilla example |
| --- | --- | --- |
| `<folder>_doctrine_cost_factor` | XP cost of the grand doctrines and subdoctrines of that folder; `-0.15` is 15% cheaper | `land_doctrine_cost_factor = -0.1`, `naval_doctrine_cost_factor`, `air_doctrine_cost_factor`, `special_forces_doctrine_cost_factor` |
| `<folder>_mastery_gain_factor` | mastery gain of every track in that folder | `land_mastery_gain_factor = 0.1`, `naval_mastery_gain_factor = 0.1` |
| `<grand doctrine id>_mastery_gain_factor` | mastery gain of the tracks under that grand doctrine | `new_mobile_warfare_mastery_gain_factor = 0.15` |
| `<subdoctrine id>_mastery_gain_factor` | mastery gain of the tracks that hold that subdoctrine | `guerilla_war_mastery_gain_factor`, `peoples_war_mastery_gain_factor` |
| `<track id>_track_mastery_gain_factor` | mastery gain of that track | `fighter_aircraft_track_mastery_gain_factor = 0.05`, `operations_track_mastery_gain_factor` |

`common/doctrines/_documentation.md` writes the first mastery form as `[folder_name]_track_mastery_gain_factor` with the example `land_track_mastery_gain_factor`. The modifier documentation and vanilla script disagree with it: the folder form has no `_track` (`land_mastery_gain_factor`, 13 vanilla uses; `land_track_mastery_gain_factor` has none), and `_track_` belongs to track ids. Use the forms in the table. [vanilla-confirmed 1.19.3] `common/ideas/*.txt`, `common/country_leader/00_traits.txt`. `documentation/modifiers_documentation.md` lists `air land naval special_forces` under `<Doctrine>_mastery_gain_factor` next to every grand doctrine and subdoctrine id, and the 14 track ids under `<Doctrine>_track_mastery_gain_factor`. [docs]

The documentation says the localisation of the mastery gain modifiers is mapped automatically, so they need no keys of their own. [docs] `common/doctrines/_documentation.md`

AI. `ai_will_do` on a grand doctrine or subdoctrine is a country-scope weight block (`base`, `modifier = { factor = N <triggers> }`); vanilla steers it with `original_tag` (factor 95 for countries that historically used the doctrine) and `is_major`. The AI also reads `NDefines.NAI.DESIRE_USE_XP_TO_UNLOCK_LAND_DOCTRINE`, `_NAVAL_DOCTRINE` and `_AIR_DOCTRINE` (0.5 each) and re-evaluates its best doctrine every `DAYS_BETWEEN_CHECK_BEST_DOCTRINE` (30) days. `common/ai_strategy/doctrines.txt` uses `has_doctrine = new_mobile_warfare` and the other ids as `enable` conditions for `role_ratio` and `force_concentration_factor` strategies. [vanilla-confirmed 1.19.3] `common/doctrines/`, `common/defines/00_defines.lua`, `common/ai_strategy/doctrines.txt`

Localisation and sprites at a glance. [vanilla-confirmed 1.19.3] `localisation/english/doctrines_l_english.yml`, `localisation/english/research_l_english.yml`, `interface/doctrines/doctrines.gfx`

| Object | Keys to define |
| --- | --- |
| Folder | `<name>` and `<name>_desc`; sprites for `tab_gfx` and `ledger_gfx`; a `sound` name |
| Grand doctrine | `name` and `description` (vanilla `GRAND_DOCTRINE_<NAME>` and `_DESC`); an `icon` sprite |
| Track | `name` (vanilla `DOCTRINE_TRACK_<NAME>`); `background`, `icon` and `icon_frame` sprites |
| Subdoctrine | `name` and `description` (vanilla `SUBDOCTRINE_<NAME>` and `_DESC`); an `icon` sprite; one key per reward, `<subdoctrine>_<reward>` |
<!-- kit:end id="doctrine-modifiers-ai" -->

<!-- kit:begin id="doctrine-example" at="bottom" -->
## Kit: Minimal grand doctrine with one track and one subdoctrine <a id="kit-doctrine-example"></a>

**Kit addition** A working shape for a new land grand doctrine, built from vanilla ids and sprites so it needs no new art. Structure and keys follow the vanilla files and the documentation. The three rewards are fewer than any vanilla subdoctrine has (4 or 5), so whether the game accepts them was not observed; add rewards up to 5 to match vanilla. [vanilla-confirmed 1.19.3] `common/doctrines/`; [docs] the five `_documentation.md` files under `common/doctrines/`; the reward count [unverified]

```text
# common/doctrines/grand_doctrines/my_doctrines.txt
my_grand_doctrine = {
    folder = land
    name = MY_GRAND_DOCTRINE
    description = MY_GRAND_DOCTRINE_DESC
    icon = GFX_doctrine_mobile_warfare_medium
    available = { always = yes }
    xp_cost = 100
    xp_type = army
    ai_will_do = { base = 1 }
    tracks = { my_track }
    planning_speed = 0.1
    milestones = {
        { army_speed_factor = 0.05 }
    }
}

# common/doctrines/tracks/my_tracks.txt
my_track = {
    name = MY_TRACK
    background = "GFX_grand_battleplan_bg"
    icon = "GFX_doctrine_milestone_infantry_land"
    icon_frame = "GFX_doctrine_decor_land"
    mastery = { multiplier = 1.0 categories = { category_all_infantry } }
}

# common/doctrines/subdoctrines/my_subdoctrines.txt
my_subdoctrine = {
    track = my_track
    name = MY_SUBDOCTRINE
    description = MY_SUBDOCTRINE_DESC
    icon = GFX_doctrine_mobile_infantry_medium
    available = { always = yes }
    xp_cost = 100
    xp_type = army
    ai_will_do = { base = 1 }
    category_all_infantry = { breakthrough = 0.1 }
    rewards = {
        drill = { mastery = 60 category_all_infantry = { max_organisation = 5 } }
        discipline = { category_all_infantry = { defense = 0.05 } }
        initiative = { category_all_infantry = { soft_attack = 0.05 } }
    }
}
```

```text
# localisation/english/my_doctrines_l_english.yml
l_english:
 MY_GRAND_DOCTRINE: "My Grand Doctrine"
 MY_GRAND_DOCTRINE_DESC: "Description."
 MY_TRACK: "My Track"
 MY_SUBDOCTRINE: "My Subdoctrine"
 MY_SUBDOCTRINE_DESC: "Description."
 my_subdoctrine_drill: "Drill"
 my_subdoctrine_discipline: "Discipline"
 my_subdoctrine_initiative: "Initiative"
```

Give a country the doctrines from script with `set_grand_doctrine = my_grand_doctrine` and `set_sub_doctrine = my_subdoctrine`, or let the player buy them in the land doctrine tab. Ids also form modifier names (`my_grand_doctrine_mastery_gain_factor`), so keep them unique and prefixed. [docs] `common/doctrines/_documentation.md`
<!-- kit:end id="doctrine-example" -->

<!-- kit:begin id="doctrine-traps" at="bottom" -->
## Kit: Doctrine traps <a id="kit-doctrine-traps"></a>

**Kit note** Mistakes to avoid when writing doctrine script.

- Milestones pair with tracks by position, so `milestones` needs exactly as many blocks as `tracks` has entries. All 12 vanilla grand doctrines match: the 10 land, naval and air ones list 4 tracks and 4 milestones, the 2 special forces ones list 2 and 2. [vanilla-confirmed 1.19.3] `common/doctrines/grand_doctrines/*.txt`
- Use the vanilla ids in triggers and effects: `has_doctrine = mobile_warfare` (the documentation's example) matches nothing because the id is `new_mobile_warfare`. [vanilla-confirmed 1.19.3] `common/doctrines/grand_doctrines/land_grand_doctrines.txt`
- Write `xor` on both sides. Vanilla lists the partner on both subdoctrines (`mountaineers_1` has `xor = { mountaineers_2 }` and `mountaineers_2` has `xor = { mountaineers_1 }`). [vanilla-confirmed 1.19.3] `common/doctrines/subdoctrines/special_forces/special_forces_subdoctrines.txt`
- Put doctrine equipment bonuses in an `equipment_bonus` block, not the `add_equipment_bonus` effect, so the bonus goes away when the doctrine is replaced. [docs] `common/doctrines/grand_doctrines/_documentation.md`
- The navy folder id is `naval` but its `xp_type` is `navy`, and its cost modifier is `naval_doctrine_cost_factor`. [vanilla-confirmed 1.19.3] `common/doctrines/grand_doctrines/sea_grand_doctrines.txt`
- A grand doctrine's `visible`, `max_track_rows` and `max_track_columns`, a subdoctrine's `allow_in_multiple_tracks` and `reward_gfx`, a track's `frame` and `background_offset`, and an explicit `modifiers = { }` block are documented but never used by vanilla, so treat them as untested. [vanilla-confirmed 1.19.3] absence in `common/doctrines/`
<!-- kit:end id="doctrine-traps" -->

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<Collection modding - Hearts of Iron 4 Wiki.md>) • [Game rule modding](<Game rule modding - Hearts of Iron 4 Wiki.md>) • [Intelligence operation modding](<Intelligence operation modding - Hearts of Iron 4 Wiki.md>) • [Map mode modding](<Map mode modding - Hearts of Iron 4 Wiki.md>) • [Occupation and resistance modding](<Occupation and resistance modding - Hearts of Iron 4 Wiki.md>) • [Peace conference modding](<Peace conference modding - Hearts of Iron 4 Wiki.md>) • [Raid modding](<Raid modding - Hearts of Iron 4 Wiki.md>) • [Script constant modding](<Script constant modding - Hearts of Iron 4 Wiki.md>) • [Special project modding](<Special project modding - Hearts of Iron 4 Wiki.md>)
