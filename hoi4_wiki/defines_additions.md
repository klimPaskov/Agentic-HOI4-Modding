# Defines additions

*Kit page: written by the Agentic HOI4 Modding Kit from the Hearts of Iron IV 1.19.3.0 game files and re-checked against 1.19.4.1. It supplements the wiki's Defines page, which it leaves unchanged. CC BY-SA 3.0 (see LICENSE.txt).*
<!-- kit:page -->

<!-- kit:begin id="review" at="top" build="1.19.4.1" checked="2026-11-01" sources="common/defines/ localisation/english/core_l_english.yml" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Written from the three files in `common/defines/` (`00_defines.lua`, `00_graphics.lua`, `01_career_profile.lua`: 4504 defines in 39 categories), parsed with a script and compared name by name and value by value with the 37 category tables of the wiki's [Defines](<defines.md>) page at wiki revision 104682. This text used to sit in kit blocks on that page; it moved here so the wiki page stays an unchanged snapshot.
Contents: an Overrides note, then per category the 617 defines the wiki tables lack (value and meaning, 22 categories), 127 changed values and 58 removed names with likely successors, plus the new categories `NFactions` and `NDoctrines`. The naval "supremacy" to "dominance" rename and the new energy defines are called out.
Gaps left: meanings come from the Lua comments or, where there is none, from the define name. Which defines the engine still reads was not tested. The comparison is with the wiki page as captured at revision 104682; when that page changes, check these tables against it again.
**1.19.4.1 re-check (2026-11-01).** The 1.19.3 define set was rebuilt from the wiki tables plus this page's tables and compared with the 1.19.4.1 files name by name and value by value, by script. 1.19.4.1 has 4523 defines in the same 39 categories: 19 are new, none was removed, and one value changed (`NMarket.REQUEST_AUTOMATION_AUTO_ACCEPT_PURCHASE_DEFAULT`, `false` to `true`). The section [1.19.4.1 changes](#Changes_1_19_4_1) lists them. Every other value in the tables below is the same in 1.19.4.1, but the two arrays the tables quote only in part (`BORDER_COLOR_CUSTOM_HIGHLIGHTS`, `FACTION_INTELLIGENCE_ALLOWED_ADVISOR_TRAIT`) were compared only as far as they are quoted.
<!-- kit:end id="review" -->

## Table of contents

- [Overrides](#Overrides)
- [1.19.4.1 changes](#Changes_1_19_4_1)
- [NGame](#NGame)
- [NDiplomacy](#NDiplomacy)
- [NCountry](#NCountry)
- [NProduction](#NProduction)
- [NBuildings](#NBuildings)
- [NMilitary](#NMilitary)
- [NAir](#NAir)
- [NNavy](#NNavy)
- [NRailwayGun](#NRailwayGun)
- [NAI](#NAI)
- [NOperatives](#NOperatives)
- [NIntel](#NIntel)
- [NSupply](#NSupply)
- [NAITheatre](#NAITheatre)
- [NProject](#NProject)
- [NFactions](#NFactions)
- [NDoctrines](#NDoctrines)
- [NMapMode](#NMapMode)
- [NMapIcons](#NMapIcons)
- [NAirGfx](#NAirGfx)
- [NGraphics](#NGraphics)
- [NInterface](#NInterface)
- [NFrontend](#NFrontend)
- [NSound](#NSound)
- [NCareerProfile](#NCareerProfile)

---

The wiki's [Defines](<defines.md>) page lists the engine defines in one table per category, and its tables date from an older build. This page holds what the installed game's define files add to them: how the files combine, and for each category the defines the wiki table lacks, the values that differ from it, and the names 1.19.3 no longer has. A category with no section here showed no difference in names or values in that comparison. The tables were written for 1.19.3 and still hold for 1.19.4.1; what 1.19.4.1 changed is in its own section after Overrides.

## Overrides <a id="Overrides"></a>

**Kit note** The three vanilla define files in 1.19.4.1 and how they combine. [vanilla-confirmed 1.19.4.1] `common/defines/`

| File | Table it defines | Categories | Defines |
| --- | --- | --- | --- |
| `00_defines.lua` | `NDefines` | 28, from `NGame` to `NDoctrines` | 3244 |
| `00_graphics.lua` | `NDefines_Graphics` | 9: `NWiki`, `NMapMode`, `NMapIcons`, `NAirGfx`, `NGraphics`, `NInterface`, `NFrontend`, `NSound`, `NFriendGUI` | 1258 |
| `01_career_profile.lua` | `NDefines_CareerProfile` | 2: `NCareerProfile`, `NCareerProfileGUI` | 21 |

The last line of `00_graphics.lua` is `for k,v in pairs( NDefines_Graphics ) do NDefines[k] = v end`, and `01_career_profile.lua` ends with the same loop for `NDefines_CareerProfile`. So all 39 categories end up inside `NDefines`, and a mod can write `NDefines.NGraphics.X = ...` or `NDefines_Graphics.NGraphics.X = ...` for graphics defines, and `NDefines.NCareerProfile.X = ...` for the career profile ones. [vanilla-confirmed 1.19.4.1] The counts are from a script that reads the three files and counts `NAME = value` lines per category.

The wiki page covers 37 of these 39 categories. `NFactions` and `NDoctrines` are new; they have sections of their own below. [vanilla-confirmed 1.19.4.1]

Advice that holds for 1.19.3: override single values in a small file of your own and never ship a copy of a vanilla define file. The vanilla files add many defines between builds (the wiki page's tables lack 617 of the 4504 defines in 1.19.3, and 58 of its names are gone; 1.19.4.1 adds 19 more), so a copied file would pin old values and miss new ones. [vanilla-confirmed 1.19.3] `common/defines/` against the wiki page for the counts. A same-name `00_defines.lua` in a mod replaces the vanilla file instead of adding to it, so a copy keeps only its own values and lacks every define it leaves out. A mod file holding only `NDefines = { NCountry = { STARTING_COMMAND_POWER = 10 } }` made the game report every other define missing at load (3060 "is not a lua table" lines, the first reading "Error reading "PEACE_TIME_NAVY_FUEL_FACTOR", "NAI" is not a lua table") and the game then crashed (EXCEPTION_INT_DIVIDE_BY_ZERO). The same file written as `NDefines.NCountry.STARTING_COMMAND_POWER = 10` failed with "attempt to index global 'NDefines' (a nil value)" and crashed the same way. So a partial copy is destructive. The start command power of 10 was never read, because neither variant reached the game. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launch, error.log and the crash folder read.

Name the override file so that it sorts after the vanilla files. The vanilla names are `00_defines.lua`, `00_graphics.lua` and `01_career_profile.lua`; a name such as `zz_my_mod_defines.lua` sorts after all of them. The wiki's remark that "almost any filename can work" does not hold for a name like `00_a.lua`: it does run before `00_defines.lua`, and the vanilla file has not yet created `NDefines`. A `00_a.lua` that sets `NDefines.NCountry.STARTING_COMMAND_POWER = 10` logged "attempt to index global 'NDefines' (a nil value)" and "An error occured when loading defines in common/defines/00_a.lua", then "No oil resource defined." and "No fuel resource defined.", and the game crashed at load (EXCEPTION_INT_DIVIDE_BY_ZERO), with an empty game.log. A `zz_b.lua` ran after the vanilla file: a command power cap of 200 set there alone was read in the game. The mod also held `zz_b.lua`, so the crash is tied to `00_a.lua` by its Lua error line and by the `zz_b.lua`-only run, not by a folder with `00_a.lua` alone. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launch, error.log, the crash folder and a script probe read in game.log.

Syntax traps seen in the vanilla files: values may be expressions (`7 * 24`, `25 * 10`, `90.0/360.0`), strings (`"oil"`), booleans (`true`), arrays (`{ 0.1, 0.2 }`) and nested arrays. Some vanilla lines end in `;` instead of `,`, and one has a decimal comma (`0,4`, see `NCountry` below). [vanilla-confirmed 1.19.4.1]

hoi4.exe contains the message `defines reloaded!`. The console command `reload defines` replied "defines reloaded!" and game.log logged "4489 defines loaded". After a `zz_b.lua` with a command power cap of 200 was replaced by one with 300, the cap read 300 in the game, so a defines edit can be reloaded without restarting. The game also logged a defines pass of its own a few seconds after the file changed and before the command, so the 300 may already have been live, and the command's own effect is not isolated. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply, game.log and a script probe read.

## 1.19.4.1 changes <a id="Changes_1_19_4_1"></a>

**Kit addition** What 1.19.4.1 changed in the define files, from a name-by-name and value-by-value comparison with the 1.19.3 set. 19 defines are new and none was removed. Counts in 1.19.4.1: `00_defines.lua` 3244, `00_graphics.lua` 1258, `01_career_profile.lua` 21. All rows: [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua` or `00_graphics.lua`. The meaning is in my words, taken from the Lua comment.

| Category | Define | 1.19.4.1 value | Meaning |
| --- | --- | --- | --- |
| `NDiplomacy` | `VOLUNTEERS_RECALL_DAYS_PER_UNIT` | `2` | Days to recall volunteers, per army unit in the recall order. |
| `NDiplomacy` | `SEND_VOLUNTEERS_AGAIN_COOLDOWN` | `180` | Days after recalling volunteers before you can send volunteers to the same country again. |
| `NDiplomacy` | `RECALL_VOLUNTEERS_AFTER_ARRIVAL_COOLDOWN` | `180` | Days after volunteers arrive before they can be recalled. |
| `NMilitary` | `MAX_CASUALTY_TRICKLEBACK` | `0.95` | Upper cap on casualty trickleback, so it cannot return more troops than died. |
| `NTrade` | `AUTO_IMPORT_DEFICIT_TOLERANCE` | `0` | Player auto-import accepts a resource balance down to minus this before it imports. |
| `NTrade` | `AUTO_IMPORT_TARGET_MARGIN` | `0` | Balance the player auto-import aims for. It shrinks or cancels trades only above this surplus. |
| `NTrade` | `AUTO_IMPORT_DEFAULT_BUDGET_FRACTION` | `0.25` | Share of usable civilian factories the auto-import budget starts with when first enabled. |
| `NTrade` | `AUTO_IMPORT_MIN_CONVOY_EFFICIENCY` | `0.4` | Auto-import starts no sea trade with a convoy efficiency below this. |
| `NTrade` | `AUTO_IMPORT_FUEL_TOPPING_START_RATIO` | `0.5` | Auto-import spends leftover budget on extra oil once the fuel stockpile falls below this share. |
| `NTrade` | `AUTO_IMPORT_FUEL_TOPPING_STOP_RATIO` | `0.9` | It stops buying extra oil once the fuel stockpile reaches this share. |
| `NTrade` | `AUTO_IMPORT_MAX_ACCEPTED_SHORTAGE` | `99` | Highest shortage a player can accept per resource in the auto-import priority window. |
| `NAI` | `MOBILIZATION_RATIO_REQUIRED_TO_RAISE_MOBILIZATION_LAW` | `0.95` | Share of its target conscription an AI must already have mobilised before a higher conscription law counts as urgent. |
| `NAI` | `LENDLEASE_TO_CAPITULATED_DESIRE_PENALTY` | `500` | Flat lend-lease desire penalty toward a capitulated country the AI does not host. |
| `NInterface` | `AUTO_DIPLOMACY_RESPONSE_ITEM_ALPHA` | `0.3` | Display alpha of diplomatic actions in the automatic response list. |
| `NInterface` | `FOCUS_MINIMAP_SCALE` | `0.035` | Focus tree mini-map panel pixels per canvas pixel. |
| `NInterface` | `FOCUS_MINIMAP_MIN_SIZE` | `48` | Smallest size of the focus tree mini-map panel. |
| `NInterface` | `INFO_WINDOW_GAP_X` | `20` | Gap between a clicked focus or technology and the details window it opens. |
| `NInterface` | `INFO_WINDOW_OFFSET_Y` | `60` | How far above the clicked item a details window starts. |
| `NInterface` | `INFO_WINDOW_CASCADE_OFFSET` | `40` | Diagonal step used when a details window would open on top of another. |

One value changed. The wiki's `NMarket` table shows the 1.19.3 value. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`

| Define | 1.19.3 value | 1.19.4.1 value | Meaning |
| --- | --- | --- | --- |
| `NMarket.REQUEST_AUTOMATION_AUTO_ACCEPT_PURCHASE_DEFAULT` | `false` | `true` | Whether purchase requests from other countries are accepted by default. |

## NGame <a id="NGame"></a>

**Kit addition** NGame in 1.19.3: 26 defines in `common/defines/00_defines.lua`; the wiki's table lists 23. [vanilla-confirmed 1.19.3]

`START_DATE = "1936.1.1.12"` and `END_DATE = "1949.1.1.1"` are unchanged in 1.19.3. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`

`FUEL_RESOURCE` is still `"oil"`, and the two localisation keys the wiki page quotes for changing it, `FUEL_DAILY_GAIN_FROM_OIL` and `FUEL_DAILY_GAIN_OIL_ONLY`, still exist in `localisation/english/core_l_english.yml`. 1.19.3 adds a separate `ENERGY_RESOURCE` (coal). [vanilla-confirmed 1.19.3]

Defines the wiki's table lacks (3). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `MINOR_SAVE_VERSION` | `0` | Minor save version; tells apart savegame formats that stay backward compatible. |
| `OIL_RESOURCE` | `"oil"` | Name of the oil resource. |
| `ENERGY_RESOURCE` | `"coal"` | Resource that gives a country energy. |

Values that differ from the wiki's table (2). The wiki page shows an older value. All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

| Define | Page value | 1.19.3 value |
| --- | --- | --- |
| `SAVE_VERSION` | `25` | `33` |
| `TRADE_ROUTE_RECALCULATE_FREQUENCY_DAYS` | `30` | `45` |

## NDiplomacy <a id="NDiplomacy"></a>

**Kit addition** NDiplomacy in 1.19.3: 217 defines in `common/defines/00_defines.lua`; the wiki's table lists 203. [vanilla-confirmed 1.19.3] 1.19.4.1 adds three volunteer defines (220 in all); see [1.19.4.1 changes](#Changes_1_19_4_1). [vanilla-confirmed 1.19.4.1]

Many `TENSION_*` values on the wiki page are older numbers; the changed ones are in the table below. `TENSION_DECAY_DAILY` is present, which agrees with the wiki page's note that it replaced `TENSION_DECAY`; there is no `TENSION_DECAY` define in 1.19.3. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`

Defines the wiki's table lacks (14). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `TENSION_PEACE_FACTOR_THREAT_FACTOR` | `0.60` | Extra scale in the peace tension reduction: the reduction is multiplied by world threat times this value (see `TENSION_PEACE_FACTOR`). |
| `PEACE_SCORE_TRANSFERRED_FROM_FACTION_INFLUENCE` | `0.1` | Share of your war score passed on to the faction members with the most influence. |
| `PEACE_SCORE_TOP_FACTION_INFLUENCE_AMOUNT` | `2` | How many of the highest-influence faction members receive that extra war score. |
| `FACTION_POWER_RESOURCE_WEIGHT` | `0.05` | Weight of country resources in a faction's power projection. |
| `FACTION_POWER_INDUSTRY_WEIGHT` | `0.1` | Weight of industry in power projection. |
| `FACTION_POWER_ARMY_WEIGHT` | `0.25` | Weight of the army in power projection. |
| `FACTION_POWER_AIR_BOMBER_WEIGHT` | `0.25` | Weight of bombers in power projection. |
| `FACTION_POWER_AIR_WEIGHT` | `0.02` | Weight of non-bomber air equipment in power projection. |
| `FACTION_POWER_NAVAL_CAPITAL_SHIP_WEIGHT` | `5` | Weight of capital ships in power projection. |
| `FACTION_POWER_NAVAL_WEIGHT` | `0.25` | Weight of naval equipment other than capital ships in power projection. |
| `FACTION_POWER_EFFECTS_WEIGHT` | `1` | Weight of the faction's goal status in power projection. |
| `NAVAL_BLOCKADE_BASE_COST` | `50` | Political power cost of issuing a naval blockade. |
| `NAVAL_BLOCKADE_DAILY_COST` | `0.1` | Daily political power cost of each naval blockade. |
| `NAVAL_BLOCKADE_THREAT_THRESHOLD` | `15` | Threat the target must have generated before a naval blockade is allowed. |

Values that differ from the wiki's table (17). The wiki page shows an older value. All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

| Define | Page value | 1.19.3 value |
| --- | --- | --- |
| `TENSION_STATE_VALUE` | `2` | `0.10` |
| `TENSION_NO_CB_WAR` | `10` | `14` |
| `TENSION_CB_WAR` | `7` | `10` |
| `TENSION_ANNEX_NO_CLAIM` | `2` | `0.20` |
| `TENSION_ANNEX_CLAIM` | `0.5` | `0.10` |
| `TENSION_ANNEX_CORE` | `0` | `-0.5` |
| `TENSION_PUPPET` | `1.25` | `0` |
| `TENSION_FORCE_GOVERNMENT` | `0.75` | `-0.5` |
| `TENSION_PEACE_FACTOR` | `0.25` | `0.80` |
| `TENSION_TAKE_ONE_CAPITAL_SHIP` | `0.25` | `0` |
| `TENSION_DEMILITARIZE_ZONE` | `0.25` | `-0.50` |
| `TENSION_WAR_REPARATION` | `0.25` | `0` |
| `TENSION_RESOURCE_RIGHTS` | `0.25` | `0` |
| `TENSION_DISMANTLE_INDUSTRY` | `0.25` | `0` |
| `TENSION_CAPITULATE` | `0.40` | `0` |
| `GUARANTEE_COST` | `25` | `15` |
| `REVOKE_GUARANTEE_COST` | `25` | `15` |

## NCountry <a id="NCountry"></a>

**Kit addition** NCountry in 1.19.3: 179 defines in `common/defines/00_defines.lua`; the wiki's table lists 176. [vanilla-confirmed 1.19.3]

The line `MAX_INTELLIGENCE_INDUSTRY_DATA_DEVIATION = 0,4,` in the vanilla file has a comma where a decimal point was meant. By Lua table-constructor rules the define is read as 0 and the 4 becomes an unnamed array entry. The wiki page shows 0.4. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`

Defines the wiki's table lacks (3). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `NAVY_USE_HOME_BASE_FOR_RANGE` | `true` | If true, task force range is measured from the home base; otherwise from any friendly naval base. |
| `CONVOY_CONTROLLED_ROUTE_COST_REDUCTION_FACTOR` | `0.25` | How many fewer convoys a route needs when it runs through areas you control. |
| `DEFAULT_COASTAL_PROTECTION_STABILITY` | `0.1` | Stability value when the coastal states are fully protected. |

Values that differ from the wiki's table (4). The wiki page shows an older value. All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

| Define | Page value | 1.19.3 value |
| --- | --- | --- |
| `MAX_INTELLIGENCE_INDUSTRY_DATA_DEVIATION` | `0.4` | `0,4` |
| `FEMALE_UNIT_LEADER_BASE_CHANCE` | `{ 0.5, 0.5, 0.5, 0.5, 0.5 }` | `{ 0.5, 0.5, 0.5, 0.5, 0.5, 0.5 }` |
| `GIE_EXILE_ARMY_LEADER_START_LEVEL` | `3` | `1` |
| `SURRENDER_LIMIT_REDUCTION_PER_COLLABORATION` | `0.3` | `0.15` |

## NProduction <a id="NProduction"></a>

**Kit addition** NProduction in 1.19.3: 70 defines in `common/defines/00_defines.lua`; the wiki's table lists 59. [vanilla-confirmed 1.19.3]

Energy is new. `BASE_FACTORY_SPEED`, `BASE_FACTORY_SPEED_MIL` and `BASE_FACTORY_SPEED_NAV` are 4, 3.5 and 2.0 in 1.19.3. The values the wiki page lists for them (5, 4.50, 2.5) are the 1.19.3 values of the new `POWERED_FACTORY_SPEED`, `POWERED_FACTORY_SPEED_MIL` and `POWERED_FACTORY_SPEED_NAV`. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` The console command `energy_ratio` sets the energy ratio for factories without coal consumption. [docs] `documentation/console_commands_documentation.md`

Defines the wiki's table lacks (11). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `MAX_MIL_FACTORIES_VISIBLE_FOR_MIL_EQUIPMENT_LINE` | `15` | Most military factory slots shown on a military equipment production line (no Lua comment). |
| `RESOURCE_TO_ENERGY_COEFFICIENT` | `9.0` | Energy produced per unit of the energy resource (coal). |
| `BASE_COUNTRY_ENERGY_PRODUCTION` | `10.0` | Base energy production of a country. |
| `ENERGY_SCALING_COST_BY_FACTORY_COUNT` | `0.0225` | Scales energy cost with the total number of factories. |
| `BASE_ENERGY_COST` | `0.25` | Energy each factory consumes. |
| `ENERGY_COST_CAP` | `6.6` | Maximum energy cost per factory. |
| `ENERGY_SCALE_PER_TRADE_FACTORY_EXPORT` | `0.25` | How strongly factories gained through trade raise the energy cost scaling. |
| `POWERED_FACTORY_SPEED` | `5` | Factory speed multiplier for a powered factory. The old `BASE_FACTORY_SPEED` value of 5 now lives here. |
| `POWERED_FACTORY_SPEED_MIL` | `4.5` | Powered factory speed multiplier, military factories (the old base value 4.5). |
| `POWERED_FACTORY_SPEED_NAV` | `2.5` | Powered factory speed multiplier, naval factories (the old base value 2.5). |
| `MILITARY_FACTORY_COHERENCY_BONUS` | `250` | Weight the AI adds to a production line already running when it has only one military factory, to stop it switching back and forth. |

Values that differ from the wiki's table (3). The wiki page shows an older value. All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

| Define | Page value | 1.19.3 value |
| --- | --- | --- |
| `BASE_FACTORY_SPEED` | `5` | `4` |
| `BASE_FACTORY_SPEED_MIL` | `4.50` | `3.5` |
| `BASE_FACTORY_SPEED_NAV` | `2.5` | `2.0` |

## NBuildings <a id="NBuildings"></a>

**Kit addition** NBuildings in 1.19.3: 20 defines in `common/defines/00_defines.lua`; the wiki's table lists 20. [vanilla-confirmed 1.19.3]

Values that differ from the wiki's table (1). The wiki page shows an older value. All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

| Define | Page value | 1.19.3 value |
| --- | --- | --- |
| `INFRASTRUCTURE_RESOURCE_BONUS` | `0.2` | `0.15` |

## NMilitary <a id="NMilitary"></a>

**Kit addition** NMilitary in 1.19.3: 382 defines in `common/defines/00_defines.lua`; the wiki's table lists 331, 7 of them removed in 1.19.3. [vanilla-confirmed 1.19.3] 1.19.4.1 adds `MAX_CASUALTY_TRICKLEBACK` (383 in all); see [1.19.4.1 changes](#Changes_1_19_4_1). [vanilla-confirmed 1.19.4.1]

`SUPPLY_USE_FACTOR_MOVING` and `SUPPLY_USE_FACTOR_INACTIVE` still carry the Lua comment "Deprecated/Unused", and `PLAN_COHESION_DISTANCE_MAX_WHEN_LEFT_BEHIND` still says it is unused, deprecated and "will be removed in next major version". All three are still in 1.19.3, so the removal the comment announced has not happened. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`

Defines the wiki's table lacks (58). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `MEDAL_AWARD_CONFIRM_PP_THRESHOLD` | `200.0` | Below this much political power, awarding a medal asks for confirmation; at or above it, the medal is granted directly. |
| `GENERATE_AI_DIV_COMMAND_MEDALS` | `0.10` | Chance that the AI awards a medal when it receives a history entry that allows one. |
| `MAX_NUM_AUTOMEDALS` | `6` | Most medals the automedal system can give. |
| `CAPTAIN_EXPERIENCE_ON_SHIP_MULT` | `1.55` | Multiplier on ship experience when it is passed to the ship's captain. |
| `MAX_CAPTAIN_EXPERIENCE_ON_SHIP` | `8000` | Cap on the experience a ship captain can gain on a ship. |
| `CAPTAIN_EXPERIENCE_ON_SHIP_PER_MEDAL_MULT` | `0.1` | Extra captain experience multiplier per medal the ship holds. |
| `SHORE_BOMBARDMENT_COLLATERAL_DAMAGE_MULTIPLIER` | `40.0` | Factor on shore bombardment damage for collateral damage. |
| `SHORE_BOMBARDMENT_COLLATERAL_DAMAGE_CRIT_CHANCE_FACTOR` | `0.0025` | Chance of a critical hit (heavy damage to a single building) from shore bombardment. |
| `MAX_REGIMENTAL_SUPPORT_WIDTH` | `5` | Width of the regimental support area in the division designer. |
| `MAX_REGIMENTAL_SUPPORT_HEIGHT` | `1` | Height of the regimental support area in the division designer. |
| `MAX_HQ_BATTALION_WIDTH` | `1` | Width of the regiment area in Army HQ templates. |
| `MAX_HQ_BATTALION_HEIGHT` | `4` | Height of the regiment area in Army HQ templates. |
| `MAX_HQ_SUPPORT_WIDTH` | `1` | Width of the support area in Army HQ templates. |
| `MAX_HQ_SUPPORT_HEIGHT` | `4` | Height of the support area in Army HQ templates. |
| `MAX_HQ_REGIMENTAL_SUPPORT_WIDTH` | `0` | Width of the regimental support area in Army HQ templates (0 means none). |
| `MAX_HQ_REGIMENTAL_SUPPORT_HEIGHT` | `0` | Height of the regimental support area in Army HQ templates (0 means none). |
| `REGIMENTAL_SUPPORT_REQUIRED_BATTALIONS` | `{ 3 }` | For each regimental support row, how many battalions the regiment needs before a support can sit in that row. |
| `AI_BATTALION_BUILD_ORDER` | `{ 1, 6, 11, 16, 21, 2, 7, 12, 17, 22, 3, 8, 13, 18, 23, 4, 9, 14, 19, 24, 5, 10, 15, 20, 25 }` | A 5 by 5 grid of numbers; the AI places a battalion at the free position with the lowest number. |
| `REGIMENTAL_SUPPORT_SLOT_COST_MULTIPLIER` | `0.5` | Scale on the slot cost of regimental supports compared with normal support slots. |
| `SPOTTING_QUALITY_NAVAL_RECON_DROP_HOURS` | `12` | Hours after which intel quality drops once naval recon air missions have spotted a unit. |
| `LAND_AIR_COMBAT_STR_DICE_SIZE` | `2` | Number of damage dice for air-to-ground damage to strength. |
| `LAND_AIR_COMBAT_ORG_DICE_SIZE` | `5` | Number of damage dice for air-to-ground damage to organisation. |
| `PLAN_PROVINCE_LOW_VP_DEFENSE_THRESHOLD` | `2.0` | Victory points at which a province counts as low value for area defense orders. |
| `PLAN_PROVINCE_MEDIUM_VP_DEFENSE_THRESHOLD` | `8.0` | Victory points at which a province counts as medium value for area defense orders. |
| `PLAN_PROVINCE_HIGH_VP_DEFENSE_THRESHOLD` | `25.0` | Victory points at which a province counts as high value for area defense orders. |
| `PLAN_PROVINCE_LOW_VP_DEFENSE_IMPORTANCE` | `2.0` | Relative importance of a low-value province in area defense orders. |
| `PLAN_PROVINCE_MEDIUM_VP_DEFENSE_IMPORTANCE` | `5.0` | Relative importance of a medium-value province in area defense orders. |
| `PLAN_PROVINCE_HIGH_VP_DEFENSE_IMPORTANCE` | `10.0` | Relative importance of a high-value province in area defense orders. |
| `PLAN_PROVINCE_CAPITAL_DEFENSE_IMPORTANCE` | `50.0` | Importance boost added when the province is the capital. |
| `PLAN_AREA_DEFENSE_FACILITY` | `15.0` | Value of facilities when the battle plan system rates defense area provinces. |
| `COHESION_IMMOBILE_PLANNING_SPEED_MULTIPLIER` | `0.50` | Factor on all planning speed growth when the immobile cohesion setting is used. |
| `UNIT_LEADER_MODIFIER_COOLDOWN_ON_DEPLOY` | `3` | Base days before a leader that is not deployed takes effect once deployed; 0 is instant. Scaled by HQ template manpower. |
| `UNIT_LEADER_MODIFIER_COOLDOWN_ON_DEPLOY_MIN` | `1` | Shortest deploy cooldown in days, even for very small HQ templates. |
| `UNIT_LEADER_MODIFIER_COOLDOWN_ON_REDEPLOY` | `15` | Days a leader needs to be redeployed to a new unit; 0 is instant. |
| `UNIT_LEADER_MODIFIER_COOLDOWN_ON_WITHDRAW` | `3` | Base days to withdraw a deployed leader; 0 is instant. Scaled by HQ template manpower. |
| `UNIT_LEADER_MODIFIER_COOLDOWN_ON_WITHDRAW_MIN` | `1` | Shortest withdraw cooldown in days, even for very small HQ templates. |
| `UNIT_LEADER_MODIFIER_COOLDOWN_REFERENCE_MANPOWER` | `2000` | Manpower at which the deploy and withdraw delay equals the base value. |
| `UNIT_LEADER_MODIFIER_COOLDOWN_MANPOWER_EXPONENT` | `1.4` | Exponent of the manpower scaling for those delays (above 1 punishes large divisions harder). |
| `FUEL_PENALTY_START_RATIO_BUFFER` | `0.1` | Buffer that keeps the out-of-fuel alert open above the penalty threshold so it does not flicker. |
| `FIGHTING_STRENGTH_DEATH_THRESHOLD` | `0.001` | Fighting strength below which divisions die from attrition. |
| `FIGHTING_STRENGTH_HQ_ALERT_THRESHOLD` | `0.2` | Fighting strength below which a deployed leader's portrait gets an alert glow. |
| `COMMANDER_ABILITY_BASE_RANGE` | `20` | Base radius of commander abilities. |
| `COMMS_MAX_DISTANCE` | `4` | Number of HQ distance steps; if it is at least the size of the scaling arrays, their last value repeats. |
| `PLANNING_CAP_COMMS_SCALING` | `{ 1.0, 0.95, 0.9, 0.85, 0.8 }` | Scaling on the planning cap by how many provinces behind the front the HQ stands (index = provinces). |
| `PLANNING_CAP_NO_HQ_SCALING` | `0.8` | Scaling on the planning cap when there is no HQ (no leader, not deployed, or not on the same root order). |
| `PLANNING_SPEED_COMMS_SCALING` | `{ 1.0, 0.95, 0.9, 0.85, 0.8 }` | Same as the planning cap array, for planning speed. |
| `PLANNING_SPEED_NO_HQ_SCALING` | `0.8` | Planning speed scaling when there is no HQ. |
| `LEADER_MOD_COMMS_SCALING` | `{ 1.06, 1.04, 1.02, 1.01, 1.0 }` | Same distance scaling, for leader modifiers. |
| `LEADER_MOD_NO_HQ_SCALING` | `1.0` | Leader modifier scaling when there is no HQ. |
| `ABILITY_COMMS_SCALING` | `{ 1.06, 1.04, 1.02, 1.01, 1.0 }` | Same distance scaling, for active abilities. |
| `ABILITY_NO_HQ_SCALING` | `1.0` | Active ability scaling when there is no HQ. |
| `GENERAL_PROXIMITY_CLOSE` | `1` | Provinces behind the front a general stays at the "close" proximity setting. |
| `GENERAL_PROXIMITY_MEDIUM` | `2` | Provinces behind the front at the "medium" setting. |
| `GENERAL_PROXIMITY_FAR` | `3` | Provinces behind the front at the "far" setting. |
| `GENERAL_PROXIMITY_DEFAULT` | `1` | Default proximity setting of a deployed general; must match one of the three values above. |
| `GENERAL_RANK_TO_ARMY_HQ_EXP_LEVEL_FACTOR` | `0.5` | Factor on the general's rank (rounded up) that gives the spawned Army HQ division its experience level. |
| `ARMY_HQ_REQUISITION_MINIMUM_REMAINING_PERCENTAGE` | `10` | Deploying an Army HQ never takes divisions below this percentage of their target manpower or equipment. |
| `PREFERRED_PRISON_VP` | `5` | A captured general is jailed in a province with at least this many victory points when one exists. |

Values that differ from the wiki's table (11). The wiki page shows an older value. All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

| Define | Page value | 1.19.3 value |
| --- | --- | --- |
| `LAND_AIR_COMBAT_STR_DAMAGE_MODIFIER` | `0.05` | `0.035` |
| `LAND_AIR_COMBAT_ORG_DAMAGE_MODIFIER` | `0.10` | `0.035` |
| `ATTRITION_EQUIPMENT_LOSS_CHANCE` | `0.1` | `0.005` |
| `ATTRITION_WHILE_MOVING_FACTOR` | `1` | `1.2` |
| `ENEMY_AIR_SUPERIORITY_DEFENSE` | `0.70` | `0.75` |
| `ENEMY_AIR_SUPERIORITY_DEFENSE_STEEPNESS` | `112` | `625` |
| `FIELD_EXPERIENCE_SCALE` | `0.0015` | `0.0008` |
| `NAVAL_INVASION_PLANNING_BONUS_MALUS` | `-1` | `0` |
| `PLAN_COHESION_WEIGHTS` | `{ 1.0, 40.0, 80.0 }` | `{ 1.0, 40.0, 80.0, 100.0 }` |
| `STRATEGIC_SPEED_RAIL_BASE` | `15.0` | `10.0` |
| `HOURS_REQ_REJOIN_BORDER_WAR_FOR_INJURED_UNITS` | `1` | `-1` |

**Kit correction** Defines in the wiki's table that 1.19.3 no longer has (7). The successor column names a define with the same value and a matching name, which is an inference. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` for the absence; [unverified] for the successor.

| Define | Page value | Likely successor |
| --- | --- | --- |
| `ATTRITION_EQUIPMENT_PER_TYPE_LOSS_CHANCE` | `0.1` | none found |
| `PLAN_PROVINCE_LOW_VP_IMPORTANCE_AREA` | `2.0` | `PLAN_PROVINCE_LOW_VP_DEFENSE_IMPORTANCE` |
| `PLAN_PROVINCE_MEDIUM_VP_IMPORTANCE_AREA` | `5.0` | `PLAN_PROVINCE_MEDIUM_VP_DEFENSE_IMPORTANCE` |
| `PLAN_PROVINCE_HIGH_VP_IMPORTANCE_AREA` | `10.0` | `PLAN_PROVINCE_HIGH_VP_DEFENSE_IMPORTANCE` |
| `PLAN_PROVINCE_CAPITAL_IMPORTANCE_AREA` | `50.0` | `PLAN_PROVINCE_CAPITAL_DEFENSE_IMPORTANCE` |
| `NUKE_MIN_DAMAGE_PERCENT` | `0.1` | `NUCLEAR_BOMB_MIN_DAMAGE_PERCENT` in `NRaids` |
| `NUKE_MAX_DAMAGE_PERCENT` | `0.9` | `NUCLEAR_BOMB_MAX_DAMAGE_PERCENT` in `NRaids` |

## NAir <a id="NAir"></a>

**Kit addition** NAir in 1.19.3: 176 defines in `common/defines/00_defines.lua`; the wiki's table lists 166, 5 of them removed in 1.19.3. [vanilla-confirmed 1.19.3]

The wiki page marks `COMBAT_MAX_WINGS_AT_ONCE`, `COMBAT_MAX_WINGS_AT_GROUND_ATTACK` and `COMBAT_MAX_WINGS_AT_ONCE_PORT_STRIKE` as "Deprecated/Unused". The 1.19.3 Lua comments do not say so, so that label is not confirmed. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`

Defines the wiki's table lacks (15). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `AIR_INVASION_PREPARE_DAYS` | `7` | Base days needed to prepare an airborne invasion. |
| `AIR_INVASION_PLAN_CAP` | `1000` | Base number of airborne invasions that can be planned at once. |
| `BASE_AIR_INVASION_DIVISION_CAP` | `1000` | Base number of divisions that can join one airborne invasion. |
| `CARRIER_COMBAT_DAMAGE_STATS_MULTIPLIER` | `0.5` | Multiplier on carrier combat damage stats (no Lua comment). |
| `CARRIER_PERCENTAGE_DEFEND` | `0.35` | Share of planes able to defend a carrier from air attack (the comment cites 15 to 35 percent historically). |
| `SUBMARINE_CARRIER_SIZE_STAT_INCREMENT` | `3` | Planes of capacity that each point of `carrier_size` adds on a submarine. |
| `MISSILE_LAUNCHER_CAPACITY` | `10` | Missiles per slot. |
| `MISSILE_LAUNCHER_SLOTS` | `1` | Missile slots a missile launcher unit has. |
| `STRATEGIC_BOMBING_PROV_BUILD_PRIO_SCALE` | `1.5` | Scale on the selected priority for provincial buildings. |
| `STRATEGIC_BOMBING_STATE_BUILD_PRIO_SCALE` | `1.5` | Scale on the selected priority for state buildings. |
| `STRATEGIC_BOMBING_INFRA_PRIO_SCALE` | `0.7` | Scale on the selected priority for infrastructure. |
| `STRATEGIC_BOMBING_RAILWAY_PRIORITY_SCALE` | `0.2` | Scale of the extra priority given to railways in strategic bombing. |
| `STRATEGIC_BOMBING_STATE_BUILDING_SCALE` | `1.0` | Scale of the state building priority in strategic bombing. |
| `NAVAL_MINES_PLANTING_SPEED_LOWER_BOUND` | `0.001` | Mine planting speed cannot fall below this. |
| `NAVAL_MINES_SWEEPING_SPEED_LOWER_BOUND` | `0.001` | Mine sweeping speed cannot fall below this. |

Values that differ from the wiki's table (4). The wiki page shows an older value. All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

| Define | Page value | 1.19.3 value |
| --- | --- | --- |
| `NAVAL_STRIKE_CARRIER_MULTIPLIER` | `10.0` | `12.0` |
| `ANTI_AIR_ATTACK_TO_DAMAGE_REDUCTION_FACTOR` | `1.0` | `2.5` |
| `MISSION_COMMAND_POWER_COSTS` | `{ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.05, 0.0, 0.0, 0.0, 0.0, 0.0 }` | `{ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0,0, 0,0 }` |
| `MISSION_FUEL_COSTS` | `{ 1.0, 1.0, 0.2, 1.0, 1.0, 1.0, 1.0, 0.75, 1.2, 1.2, 1.0, 0.6, 1.0, 1.0, 1.0, 1.0 }` | `{ 1.0, 1.0, 0.2, 1.0, 1.0, 1.0, 1.0, 0.75, 1.2, 1.2, 1.0, 0.6, 1.0, 1.0, 1.0, 1.0, 0.0, 0,0, 0,0 }` |

**Kit correction** Defines in the wiki's table that 1.19.3 no longer has (5). The successor column names a define with the same value and a matching name, which is an inference. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` for the absence; [unverified] for the successor.

| Define | Page value | Likely successor |
| --- | --- | --- |
| `STRATEGIC_BOMBER_NUKE_AIR_SUPERIORITY` | `0.75` | none found |
| `BOMBING_TARGETING_RANDOM_FACTOR` | `0.25` | none found |
| `BOMBING_PROV_BUILD_PRIO_SCALE` | `1.5` | `STRATEGIC_BOMBING_PROV_BUILD_PRIO_SCALE` |
| `BOMBING_STATE_BUILD_PRIO_SCALE` | `1.5` | `STRATEGIC_BOMBING_STATE_BUILD_PRIO_SCALE` |
| `BOMBING_INFRA_PRIO_SCALE` | `0.7` | `STRATEGIC_BOMBING_INFRA_PRIO_SCALE` |

## NNavy <a id="NNavy"></a>

**Kit addition** NNavy in 1.19.3: 414 defines in `common/defines/00_defines.lua`; the wiki's table lists 340, 18 of them removed in 1.19.3. [vanilla-confirmed 1.19.3]

Naval "supremacy" is called "dominance" in 1.19.3: the old `SUPREMACY_*` and `*_SUPREMACY_*` defines are gone and `DOMINANCE_*` defines exist instead (the removed ones with a clear successor are listed below with their old values). [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`

The wiki page shows `SUBMARINE_REVEAL_BASE_CHANCE`, `SUBMARINE_REVEAL_POW` and `SUBMARINE_BASE_TORPEDO_REVEAL_CHANCE` as current. In 1.19.3 their Lua comments are marked "deprecated, will be removed in the future update", and the rows `SUBMARINE_BASE_STEALTH_VALUE`, `SUBMARINE_REVEAL_DETECTION_MULTIPLIER` and `SUBMARINE_REVEAL_TORPEDO_FIRING_DETECTION_MULTIPLIER` below belong to the reworked detection formula. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`

Defines the wiki's table lacks (92). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `CARRIER_OFFENSIVE_STANCE_SORTIE_RATIO` | `{0.0, 0.25, 0.50, 0.75, 1.0}` | Offensive sortie share per stance step; the defensive share is 1.0 minus the value at the same index. |
| `CARRIER_OFFENSIVE_STANCE_DEFAULT_INDEX` | `2` | Default index into `CARRIER_OFFENSIVE_STANCE_SORTIE_RATIO`. |
| `SELECTED_SORTIE_INITIAL_TIME` | `24` | Hours from combat start during which the selected sortie overrides the default one. |
| `SHIP_SUPPORT_NEED_FACTOR` | `0.1` | Support need of a ship: this factor times the ship's dominance value. |
| `MAX_ADMIRAL_HEADQUARTER_ASSIGNMENTS` | `3` | Most admirals that can be assigned to naval headquarters. |
| `NAVAL_HEADQUARTER_ADJACENCY` | `2` | How many extra strategic region steps from the first one a naval headquarter gives benefits. |
| `CONVOY_BLOCKED_BY_ENEMY_CONTROLLED_REGION` | `true` | If true, a sea region controlled by the enemy counts as blocked for convoys. |
| `NAVAL_DOMINANCE_STRIKE_FORCE_FRACTION` | `0.0006` | Dominance points that make up one percent of the strike force multiplier (1000 dominance gives 60 percent). |
| `NAVAL_DOMINANCE_STRIKE_FORCE_MULTIREGION_DECAY` | `0.05` | Percentage by which the strike force dominance multiplier drops for each extra assigned region. |
| `NAVAL_DOMINANCE_SPOTTING_BONUS` | `0.05` | Dominance bonus to spotting (no Lua comment). |
| `NAVAL_DOMINANCE_ORG_RECOVERY` | `0.1` | Dominance effect on organisation recovery (no Lua comment). |
| `NAVAL_DOMINANCE_SHIP_RECOVERY_CHANCE` | `0.1` | Dominance effect on the chance of ship recovery (no Lua comment). |
| `NAVAL_DOMINANCE_MINES_PLANTING_BONUS` | `0.2` | Mine planting bonus when you hold naval dominance in the region. |
| `NAVAL_DOMINANCE_MINES_SWEEPING_BONUS` | `0.2` | Mine sweeping bonus when you hold naval dominance in the region. |
| `NAVAL_DOMINANCE_CHANCE_OF_ACCIDENT_REDUCTION` | `0.25` | Reduction of the accident chance in naval training when you hold dominance in the region. |
| `UNDERWAY_REPLENISHMENT_PRIORITY` | `7` | Default convoy priority for underway replenishment. |
| `NAVAL_HOMEBASE_CALCULATION_DISTANCE_CUTOFF` | `550` | Distance used to normalise home base scoring; anything beyond scores 0. |
| `NAVAL_HOMEBASE_BUILDING_SCORE_FACTOR` | `0.035` | How much the naval base level counts in the home base score. |
| `NAVAL_HOMEBASE_OWNERSHIP_BONUS` | `0.04` | Score added when the calculating country owns the base. |
| `NAVAL_MISSION_AI_RANGE_THRESHOLD_EPSILON` | `0.25` | Tolerance in the AI range threshold checks for naval missions. |
| `NAVAL_MISSION_AI_CONVOY_NORMALIZATION_TARGET` | `150` | Convoy count the AI normalises against when scoring convoy raiding missions. |
| `CAPITAL_SHIP_COMBAT_RETREAT_MULT` | `0.5` | Multiplier on the combat retreat threshold of capital ships and carriers. |
| `AI_MAX_TASKFORCES_PER_TRAINING_OBJECTIVE` | `5` | Most task forces the AI wants in each training fleet. |
| `NAVAL_HEADQUARTERS_EXPERIENCE_SCALE` | `0.125` | Share of task force experience in its regions that characters in a naval HQ receive. |
| `NAVAL_INVASION_PREPARE_DAYS` | `60` | Base days needed to prepare a naval invasion. |
| `NAVAL_INVASION_PLAN_CAP` | `1` | Base number of naval invasions that can be planned at once. |
| `BASE_NAVAL_INVASION_DIVISION_CAP` | `4` | Base number of divisions that can join one naval invasion. |
| `NAVAL_COMBAT_PLANE_MIN_STACKING_PENALTY` | `80` | Number of planes in a naval combat before stacking penalties start. |
| `NAVAL_COMBAT_PLANE_STACKING_PENALTY_EFFECT` | `0.005` | Reduction in planes able to take off for each plane above that number (with diminishing returns). |
| `SHIP_SILHOUETTE_VALUE_PLANES_CAPITAL` | `10` | Silhouette value of a capital ship, in abstract plane units, for dynamic plane efficacy. |
| `SHIP_SILHOUETTE_VALUE_PLANES_SCREEN` | `5` | Same, for a screen ship. |
| `SHIP_SILHOUETTE_VALUE_PLANES_CARRIER` | `16` | Same, for a carrier. |
| `SHIP_SILHOUETTE_VALUE_PLANES_SUPPORT` | `3` | Same, for a support ship. |
| `SHIP_SILHOUETTE_VALUE_PLANES_CONVOY` | `4` | Same, for a convoy. |
| `SHIP_SILHOUETTE_VALUE_PLANES_SUBMARINE` | `7` | Same, for a submarine. |
| `SCREEN_CAP_REDUCTION_FACTOR` | `0.02` | Reduces screen silhouette weight when capital ships are present: screen value times 1/(1 + caps times weight). |
| `NAVY_REPAIR_BASE_SEARCH_NON_OPERATIONAL_STR` | `0.65` | Strength at or below which the AI treats a fleet as non-operational, cancels its mission and sends it to repair. |
| `NAVY_REPAIR_BASE_PRIORITY_THRESHOLD_LOW` | `2` | Bases above this level get low repair priority. |
| `NAVY_REPAIR_BASE_PRIORITY_THRESHOLD_HIGH` | `7` | Bases above this level get high repair priority; bases between the two levels get medium. |
| `AIR_BASE_DOMINANCE_FACTOR` | `0.02` | Percentage per air base level in the region that counts toward the naval dominance target value. |
| `RADAR_DOMINANCE_FACTOR` | `0.05` | Percentage per radar level in the region that counts toward the naval dominance target value. |
| `DOMINANCE_CONTROLLED_THRESHOLD_RATIO` | `0.60` | Share of the needed dominance over enemies that makes you and your friends control a sea region. |
| `MISSION_FUEL_COSTS_PRIO_FACTOR` | `{ 0.0, 1.0, 1.0, 0.6, 0.6, 0.5, 0.3, 0.6, 0.0, 1.0 }` | Per-mission fuel priority ratio; a higher value means the mission matters more when fuel is short. Order: hold, patrol, strike force and the other naval missions. |
| `STRIKE_FORCE_ON_BASE_FUEL_COST_FACTOR` | `0.25` | Fuel cost factor of a strike force mission while in port. |
| `UNDERWAY_REPLENISHMENT_RANGE_FACTOR` | `0.4` | Range bonus of a task force with underway replenishment active (0.2 means +20 percent). |
| `UNDERWAY_REPLENISHMENT_CONVOY_COST_PER_FUEL` | `0.28` | Convoys that underway replenishment costs per unit of maximum daily fuel use, rounded up. |
| `AGGRESSION_LEVEL_BY_MISSION_WEAKER` | `{ -1, 0, 3, 2, 1, -1, -1, -1, -1, 2 }` | Per-mission AI aggression level when its navy is weaker; indexes into `AGGRESSION_SETTINGS_VALUES` (0 do not engage, 1 low, 2 medium, -1 use the default). |
| `AGGRESSION_LEVEL_BY_MISSION_STRONGER_OR_EQUAL` | `{ -1, 0, 4, 2, 2, -1, -1, -1, -1, 3 }` | Same, when its navy is stronger or equal. |
| `FIELD_EXPERIENCE_FACTOR` | `0.7` | Factor on all naval experience gained from missions. |
| `MISSION_DAILY_EXP_GAIN_PER_SHIP` | `0.3` | Experience each ship gains per 24 hours while training, before modifiers. |
| `MISSION_DAILY_COUNTRY_EXP_FACTOR` | `0.01` | Scale of the daily country navy experience gain. |
| `MISSION_DAILY_COUNTRY_EXP_MANPOWER_FACTOR` | `0.006` | Scale applied to the manpower on mission for the daily country navy experience. |
| `MISSION_DAILY_COUNTRY_EXP_MANPOWER_RATIO_FACTOR` | `0.01` | Scale applied to on-mission manpower per ship of the country for that experience. |
| `MISSION_DAILY_COUNTRY_EXP_SHIP_RATIO_FACTOR` | `300.0` | Scale applied to the ratio of ships on mission for that experience. |
| `MISSION_EXP_RATIOS` | `{ 0.0, 0.2, 0.05, 0.2, 0.2, 0.2, 0.2, 1.0, 0.0, 0.005 }` | Experience multiplier per mission type. Order: hold, patrol, strike force, convoy raiding, convoy escort, mines planting, mines sweeping, train, reserve fleet, naval invasion support. |
| `MISSION_DOMINANCE_RATIOS` | `{ 0.0, 1.0, 1.0, 0.5, 0.5, 0.3, 0.3, 0.0, 0.0, 1.0 }` | Dominance multiplier per mission type, same order as above. |
| `DOMINANCE_PER_SHIP_PER_RANGE_NEUTRAL` | `2000` | Ship range with no dominance bonus or penalty; shorter or longer range scales it (minimum 0). |
| `DOMINANCE_PER_SHIP_PER_SPEED_NEUTRAL` | `20` | Ship speed with no dominance bonus or penalty (minimum 0). |
| `DOMINANCE_PER_SHIP_PER_CARRIER_SIZE` | `0.1` | Dominance bonus per point of carrier size (minimum 0). |
| `DOMINANCE_PER_SHIP_PER_HEAVY_GUN_ATTACK` | `0.01` | Dominance bonus per point of heavy gun attack (minimum 0). |
| `DOMINANCE_DAILY_GAIN_FACTOR` | `0.02` | Daily dominance gain as a fraction of the target value. |
| `DOMINANCE_DAILY_LOSS_FACTOR` | `0.04` | Daily dominance loss as a fraction of the previous target value. |
| `SUPPORT_SHIP_RECOVERY_BASE_STRENGTH_FACTOR` | `0.01` | Share of maximum strength a recovered ship gets back. |
| `MIN_SHIPS_FOR_HIGHER_SHIP_RATIO_PENALTY` | `4` | Fleet size from which the large fleet penalty applies. |
| `MIN_MINE_CAPABLE_RATIO_FOR_ROLE_ASSIGNMENT` | `0.6` | Share of mine-capable ships a task force needs to get the mine icon. |
| `MAX_SHIP_COUNT_FOR_DOMINANCE_PATROL_ROLE_ASSIGNMENT` | `15` | Most ships a task force can have to count as a dominance building patrol (it also needs capital ships). |
| `NAVAL_COMBAT_MEDAL_CHANCE` | `24` | A ship has a 1 in N chance of a medal after a battle. |
| `NAVAL_COMBAT_MEDAL_MIN_DURATION` | `48` | Hours a battle must last before it can give a medal. |
| `NAVAL_COMBAT_MEDAL_LAST_MEDAL_LIMIT` | `30` | Days that must pass before a ship can earn another medal. |
| `NAVAL_COMBAT_MEDAL_ALLOW_CONVOY` | `false` | Whether attacks on convoys count for medals. |
| `MINE_SWEEPING_REGION_TO_TASKFORCE_RATIO` | `1.0` | Task force to region ratio that sets sweeping efficiency, modified by coordination. |
| `MINE_PLANTING_REGION_TO_TASKFORCE_RATIO` | `1.0` | Same, for planting. |
| `COORDINATION_EFFECT_ON_MINE_SWEEPING` | `1.0` | Multiplier on coordination for mine sweeping. |
| `COORDINATION_EFFECT_ON_MINE_PLANTING` | `1.0` | Multiplier on coordination for mine laying. |
| `DOMINANCE_EFFECT_ON_POSITIONING_FOR_CONVOY_ESCORT_MAX_RATIO` | `2.0` | Dominance ratio (times the threshold) at which the positioning bonus from dominance is at its maximum. |
| `DOMINANCE_EFFECT_ON_POSITIONING_FOR_CONVOY_ESCORT` | `0.15` | Positioning increase at that maximum ratio, with full control. |
| `SUBMARINE_BASE_STEALTH_VALUE` | `100` | Reworked detection formula: submarine visibility is subtracted from this for the divisor. Higher means less detection. |
| `SUBMARINE_REVEAL_DETECTION_MULTIPLIER` | `0.065` | Reworked formula: multiplies average submarine detection. Higher means more detection. |
| `SUBMARINE_REVEAL_TORPEDO_FIRING_DETECTION_MULTIPLIER` | `1.1` | Reworked formula: multiplier applied when checking whether a torpedo launch reveals the submarine. |
| `NAVAL_COMBAT_AIR_SUB_TARGET_BASE` | `10` | Base score for planes picking a submarine as a target in naval combat, before screening efficiency. |
| `NAVAL_COMBAT_AIR_SCREEN_TARGET_BASE` | `10` | Same, for screen ships. |
| `NAVAL_COMBAT_AIR_CAPITAL_TARGET_BASE` | `10` | Same, for capital ships. |
| `NAVAL_COMBAT_AIR_CARRIER_TARGET_BASE` | `10` | Same, for carriers. |
| `NAVAL_COMBAT_AIR_CONVOY_TARGET_BASE` | `1.0` | Same, for convoys. |
| `NAVAL_COMBAT_AIR_SUB_TARGET_SCALE` | `10` | Scaled target score for submarines; the maximum applies at zero screening efficiency. |
| `NAVAL_COMBAT_AIR_SCREEN_TARGET_SCALE` | `10` | Same, for screen ships. |
| `NAVAL_COMBAT_AIR_CAPITAL_TARGET_SCALE` | `50` | Same, for capital ships. |
| `NAVAL_COMBAT_AIR_CARRIER_TARGET_SCALE` | `200` | Same, for carriers. |
| `NAVAL_COMBAT_AIR_CONVOY_TARGET_SCALE` | `1.0` | Same, for convoys. |
| `NAVAL_BASE_DOMINANCE_FACTOR` | `0.01` | Base dominance bonus from naval bases in the region. |
| `NAVAL_HEADQUARTERS_FIRST_ADJACENT_FACTOR` | `0.5` | Multiplier on naval HQ dominance in the first adjacent region. |
| `NAVAL_HEADQUARTERS_SECOND_ADJACENT_FACTOR` | `0.25` | Multiplier on naval HQ dominance in the second adjacent region. |

Values that differ from the wiki's table (37). The wiki page shows an older value. All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

| Define | Page value | 1.19.3 value |
| --- | --- | --- |
| `WAR_SCORE_GAIN_FOR_SUNK_SHIP_PRODUCTION_COST_FACTOR` | `0.020` | `0.05` |
| `WAR_SCORE_GAIN_FOR_SUNK_CONVOY` | `0.08` | `0.05` |
| `COMBAT_MIN_HIT_CHANCE` | `0.05` | `0.005` |
| `COMBAT_RETREAT_DECISION_CHANCE` | `0.22` | `0.2` |
| `REPAIR_AND_RETURN_PRIO_LOW` | `0.2` | `0.45` |
| `REPAIR_AND_RETURN_PRIO_MEDIUM` | `0.5` | `0.65` |
| `REPAIR_AND_RETURN_PRIO_LOW_COMBAT` | `0.6` | `0.9` |
| `REPAIR_AND_RETURN_PRIO_MEDIUM_COMBAT` | `0.3` | `0.6` |
| `REPAIR_AND_RETURN_PRIO_HIGH_COMBAT` | `0.1` | `0.4` |
| `REPAIR_AND_RETURN_AMOUNT_SHIPS_MEDIUM` | `0.4` | `0.2` |
| `REPAIR_AND_RETURN_AMOUNT_SHIPS_HIGH` | `0.8` | `0.2` |
| `AMPHIBIOUS_LANDING_PENALTY` | `-0.7` | `-0.5` |
| `SUPPLY_NEED_FACTOR` | `4` | `1` |
| `NAVY_REPAIR_BASE_SEARCH_SCORE_PER_SLOT` | `1.0` | `2.5` |
| `OUT_OF_FUEL_RANGE_FACTOR` | `-0.75` | `0` |
| `AGGRESSION_SETTINGS_VALUES` | `{ 0, 0.5, 0.9, 2.0, 10000 }` | `{ 0, 0.6, 1.25, 2.0, 10000 }` |
| `AGGRESION_MULTIPLIER_FOR_COMBAT` | `1.2` | `1.0` |
| `AGGRESSION_TORPEDO_EFFICIENCY_ON_LIGHT_SHIPS` | `0.1` | `0.2` |
| `AGGRESSION_TORPEDO_EFFICIENCY_ON_HEAVY_SHIPS` | `1.1` | `1.5` |
| `SUBMARINE_ESCAPE_RATIOS` | `{ 1000, 15, 3.0, 1.0, 0.1 }` | `{ 1000, 3.0, 1.0, 0.5, 0.1 }` |
| `MIN_REPAIR_FOR_JOINING_COMBATS` | `{ 0.0, 0.5, 0.7, 0.9 }` | `{ 0.0, 0.5, 0.7, 0.9, 0.0 }` |
| `ATTRITION_WHILE_MOVING_FACTOR` | `1.5` | `1.2` |
| `TRAINING_MAX_DAILY_COUNTRY_EXP` | `3.5` | `1` |
| `AIR_MISSION_SPOTTING_FACTORS` | `{ 0.50, 0, 0.25, 0, 0.50, 0, 0, 0.25, 0, 0, 0, 0, 0.25, 0.50, 1.00, 1.50 }` | `{ 0.50, 0, 0.25, 0, 0.50, 0, 0, 0.25, 0, 0, 0, 0, 0.25, 0.50, 1.00, 1.50, 0, 0 }` |
| `BASE_ESCAPE_SPEED` | `0.045` | `0.05` |
| `SPEED_TO_ESCAPE_SPEED` | `0.95` | `0.5` |
| `ESCAPE_SPEED_PER_COMBAT_DAY` | `0.01` | `0.015` |
| `MAX_ESCAPE_SPEED_FROM_COMBAT_DURATION` | `0.15` | `0.5` |
| `ESCAPE_SPEED_SUB_BASE` | `0.08` | `0.1` |
| `ESCAPE_SPEED_HIDDEN_SUB` | `0.18` | `0.35` |
| `MAX_POSITIONING_BONUS_FROM_SURFACE_DETECTION` | `0.0` | `0.25` |
| `SUBMARINE_REVEAL_ON_MINIMUM_POSITIONING` | `2.0` | `1.0` |
| `TASK_FORCE_ROLE_TO_INSIGNIA` | `{ 6, 15, 22, 26, 16, 17, 29, 1 }` | `{ 6, 15, 22, 26, 30, 31, 29, 1, 5 }` |
| `MIN_SHIP_COUNT_FOR_TASK_FORCE_ROLE_ASSIGNMENT` | `4` | `2` |
| `GUN_HIT_PROFILES` | `{ 80.0, 100.0, 45.0 }` | `{ 70.0, 100.0, 45.0 }` |
| `SUBMARINE_HIDE_TIMEOUT` | `20` | `8` |
| `SUBMARINE_REVEALED_TIMEOUT` | `16` | `12` |

**Kit correction** Defines in the wiki's table that 1.19.3 no longer has (18). The successor column names a define with the same value and a matching name, which is an inference. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` for the absence; [unverified] for the successor.

| Define | Page value | Likely successor |
| --- | --- | --- |
| `WAR_SCORE_DECAY_FOR_BUILT_CONVOY` | `0.01` | none found |
| `NAVAL_INVASION_PREPARE_HOURS` | `168` | `NAVAL_INVASION_PREPARE_DAYS` (unit and value changed) |
| `NAVAL_SUPREMACY_CAN_INVADE` | `0.5` | none found |
| `CARRIER_STACK_PENALTY` | `4` | none found |
| `CARRIER_STACK_PENALTY_EFFECT` | `0.2` | none found |
| `MISSION_SUPREMACY_RATIOS` | `{ 0.0, 1.0, 1.0, 0.5, 0.5, 0.3, 0.3, 0.0, 0.0, 1.0 }` | `MISSION_DOMINANCE_RATIOS` |
| `SUPREMACY_PER_SHIP_PER_MANPOWER` | `0.05` | none found |
| `SUPREMACY_PER_SHIP_PER_IC` | `0.005` | none found |
| `SUPREMACY_PER_SHIP_BASE` | `0` | none found |
| `NAVAL_MINES_NAVAL_SUPREMACY_FACTOR` | `1.0` | none found |
| `MINE_SWEEPING_SUPREMACY_EFFICIENCY_MAX_REGION_TO_TASKFORCE_RATIO` | `1.0` | `MINE_SWEEPING_REGION_TO_TASKFORCE_RATIO` |
| `MINE_PLANTING_SUPREMACY_EFFICIENCY_MAX_REGION_TO_TASKFORCE_RATIO` | `1.0` | `MINE_PLANTING_REGION_TO_TASKFORCE_RATIO` |
| `COORDINATION_EFFECT_ON_MINE_SWEEPING_SUPREMACY_EFFICIENCY` | `1.0` | `COORDINATION_EFFECT_ON_MINE_SWEEPING` |
| `COORDINATION_EFFECT_ON_MINE_PLANTING_SUPREMACY_EFFICIENCY` | `1.0` | `COORDINATION_EFFECT_ON_MINE_PLANTING` |
| `NAVAL_COMBAT_AIR_SUB_TARGET_SCORE` | `10` | `NAVAL_COMBAT_AIR_SUB_TARGET_BASE` and `NAVAL_COMBAT_AIR_SUB_TARGET_SCALE` |
| `NAVAL_COMBAT_AIR_CAPITAL_TARGET_SCORE` | `50` | `NAVAL_COMBAT_AIR_CAPITAL_TARGET_SCALE` (same value) |
| `NAVAL_COMBAT_AIR_CARRIER_TARGET_SCORE` | `200` | `NAVAL_COMBAT_AIR_CARRIER_TARGET_SCALE` (same value) |
| `NAVAL_COMBAT_AIR_CONVOY_TARGET_SCORE` | `1.0` | `NAVAL_COMBAT_AIR_CONVOY_TARGET_SCALE` (same value) |

## NRailwayGun <a id="NRailwayGun"></a>

**Kit addition** NRailwayGun in 1.19.3: 24 defines in `common/defines/00_defines.lua`; the wiki's table lists 26, 2 of them removed in 1.19.3. [vanilla-confirmed 1.19.3]

**Kit correction** Defines in the wiki's table that 1.19.3 no longer has (2). The successor column names a define with the same value and a matching name, which is an inference. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` for the absence; [unverified] for the successor.

| Define | Page value | Likely successor |
| --- | --- | --- |
| `ANNEX_RATIO` | `0.5` | none found |
| `HOURS_BETWEEN_REDISTRIBUTION` | `24` | none found |

## NAI <a id="NAI"></a>

**Kit addition** NAI in 1.19.3: 946 defines in `common/defines/00_defines.lua`; the wiki's table lists 825, 14 of them removed in 1.19.3. [vanilla-confirmed 1.19.3] 1.19.4.1 adds two (948 in all); see [1.19.4.1 changes](#Changes_1_19_4_1). [vanilla-confirmed 1.19.4.1]

`TRANSPORTS_PER_PARATROOPER` still has the Lua comment "Currently unused". [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` `AIFC` is the AI force concentration logic. [vanilla-confirmed 1.19.3] (the Lua comments for `AIFC_UPDATE_FREQUENCY_DAYS` and its neighbours say so)

Defines the wiki's table lacks (135). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `PEACE_TIME_NAVY_FUEL_FACTOR` | `0.25` | Share of available navy fuel the AI may spend on missions in peace time. |
| `PEACE_TIME_NAVY_FUEL_LIMIT` | `0.5` | Top fuel share for peace-time navy use, scaled with world tension. |
| `AI_TASKFORCE_REQUIRED_RESERVE_RATIO` | `0.2` | Part of a task force's optimal composition kept in reserve for reinforcement (rounded up per type). |
| `DIPLOMATIC_ACTION_NAVAL_BLOCKADE_BASE_SCORE` | `-700` | Base score the AI conditions must beat `DIPLOMATIC_ACTION_PROPOSE_SCORE` with before it considers a blockade. |
| `DIPLOMATIC_ACTION_NAVAL_BLOCKADE_DECREMENT_SCORE_PER_EXISTING_BLOCKADE` | `100` | Desire lost for each blockade the AI already has. |
| `DIPLOMATIC_ACTION_NAVAL_BLOCKADE_OPINION_SCALING` | `-2` | Desire change per point of target opinion; must be negative to raise desire. |
| `DIPLOMATIC_ACTION_NAVAL_BLOCKADE_TENSION_FACTOR` | `8` | Factor applied to the threat the target has generated. |
| `DIPLOMATIC_ACTION_NAVAL_BLOCKADE_DECREMENT_SAME_IDEOLOGY` | `2000` | Desire lost when the target has the same ideology. |
| `DIPLOMATIC_ACTION_NAVAL_BLOCKADE_FLEET_SIZE_THRESHOLD` | `100` | Fleet size difference above or below which the desire changes. |
| `DIPLOMATIC_ACTION_NAVAL_BLOCKADE_FLEET_SIZE_SCALING` | `4` | Multiplier on that change. |
| `AI_GUARANTEE_DESIRE_WITH_PRESSURE_MODIFIER` | `15` | Extra guarantee desire when an ideology drift from guarantees modifier is active. |
| `ROCKET_PRIORITIZE_BARRAGE` | `false` | If true the AI prefers rocket barrage over strategic bombing missions. |
| `GUN_EMPLACEMENT_MIN_ASSIGN_SCORE` | `1` | Lowest region score for gun emplacement air missions. |
| `GUN_EMPLACEMENT_MIN_PRIO_ASSIGN_SCORE` | `50` | Lowest region score for critical gun emplacement air missions. |
| `GUN_EMPLACEMENT_ASSIGN_SCORE_REDUCTION_PER_ASSIGNMENT` | `0.5` | Score a region loses for each gun emplacement assigned to it. |
| `INFRASTRUCTURE_PERCENTAGE_AT_WHICH_TO_BUILD_INFRA_CAP_BUILDING` | `0.75` | Infrastructure level at which the AI builds a cap building in a state. |
| `NUM_FACTORIES_IN_STATE_TO_WANT_ENERGY_REDUCTION` | `6` | Military factories the AI wants in a state before it considers an energy reduction cap building. |
| `TOTAL_STATE_EXTRACTED_RESOURCES_FOR_BUILDING_RESOURCE_CAP_BUILDING` | `30.0` | Extracted resources needed before a resource-improving cap building is built. |
| `MINIMUM_MONTHLY_LEND_LEASE_EQUIPMENT` | `10` | The AI offers no lend-lease if the monthly amount would be below this. |
| `LENDLEASE_CONVOY_OVERCOMMIT_PENALTY_INTERVAL` | `3` | For every N convoys the receiver is over capacity, the AI acceptance score drops by 1. |
| `AIR_BASE_ACCESS_SCORE_PENALTY_PER_EXISTING_ACCESS_AT_WAR` | `150` | Score penalty per air base access already held, at war (no Lua comment). |
| `AIR_BASE_ACCESS_SCORE_PENALTY_PER_EXISTING_ACCESS` | `250` | Same penalty outside war (no Lua comment). |
| `START_TRAINING_SUPPLY_LEVEL` | `0.40` | The AI does not start training when the supply ratio is below this. |
| `STOP_TRAINING_SUPPLY_LEVEL` | `0.30` | The AI stops training when the supply ratio is below this. |
| `STOP_TRAINING_FULLY_TRAINED_FACTOR` | `0.95` | The AI stops training once this share of army divisions is fully trained. |
| `STOP_TRAINING_ACTIVE_COMBAT_RATIO` | `0.10` | The AI halts all training when more than this share of divisions is in combat. |
| `REMOVE_OBSOLETE_TEMPLATE_DAYS` | `180` | Days an obsolete, unused template is kept before the AI removes it; zero or less means never. |
| `CONVOY_DEFICIT_BUILD_BOOST_MAX` | `150` | Cap on the convoy build boost caused by a convoy deficit, so lost convoys do not starve warship production. |
| `CANCEL_COMBAT_DISADVANTAGE_RATIO` | `1.5` | Enemy advantage ratio above which the AI may cancel an attack in normal combat. |
| `CANCEL_COMBAT_MIN_DURATION_HOURS` | `48` | Hours a normal combat must have lasted before the AI may cancel it. |
| `CANCEL_INVASION_COMBAT_DISADVANTAGE_RATIO` | `3.5` | Same ratio for invasion combat. |
| `CANCEL_INVASION_COMBAT_MIN_DURATION_HOURS` | `720` | Same minimum duration for invasion combat. |
| `NAVAL_COAST_DEFENSE_TENSION_THRESHOLD` | `0.35` | World tension at which countries start protecting their home coast in advance. |
| `LAND_DEFENSE_RAID_IMPORTANCE` | `500` | Strategic importance of detected raids aimed at the country. |
| `LAND_DEFENSE_FIGHERS_PER_RAID` | `100` | Air superiority planes requested per detected raid. The define name keeps the spelling `FIGHERS`. |
| `LAND_DEFENSE_INTERCEPTORS_PER_RAID` | `100` | Interceptors requested per detected raid. |
| `LAND_DEFENSE_INTERCEPTORS_PER_BOMBERS` | `0.8` | Interceptors requested per enemy bomber. |
| `LAND_DEFENSE_INTERCEPTORS_PER_PLANE` | `0.1` | Interceptors requested per enemy non-bomber plane. |
| `LAND_DEFENSE_SAM_MISSILE_IMPORTANCE_FACTOR` | `0.2` | Importance of using SAM missiles in the strategic importance of regions; higher raises their use. |
| `LAND_COMBAT_MISSILE_IMPORTANCE_FACTOR` | `1.5` | Same for missiles in land combat. |
| `CONSTRUCTION_PRIO_SUPPLY_BUILDING` | `1.10` | Base construction queue priority of supply buildings (supply hubs, ports). |
| `AI_SHIP_SWAP_MIN_DAMAGED_SHIPS` | `2` | Damaged ships a task force needs before the AI swaps them to reserves. |
| `AI_SHIP_SWAP_DAMAGE_THRESHOLD` | `0.33` | Per-ship strength below which a capital ship or carrier counts as damaged enough to swap. |
| `AI_REPAIR_CANCEL_MIN_STRENGTH` | `0.75` | Strength at which the AI pulls non-reserve task forces out of repair. |
| `AI_SURFACE_COMBAT_FUEL_RATIO` | `0.70` | Share of navy fuel kept for surface combat (patrols, strike forces, dominance). |
| `AI_CONVOY_DEFENSE_FUEL_RATIO` | `0.15` | Share of navy fuel kept for convoy escorts; the rest goes to convoy raiding. |
| `INVASION_TARGET_DISTANCE_DENOMINATOR` | `1000` | Divided by the pixel distance to give the distance score of an invasion target. |
| `INVASION_TARGET_NO_PORT_FACTOR` | `0.3` | Score multiplier for invasion targets without a port. |
| `INVASION_TARGET_TRUNCATION_SELECT_THRESHOLD` | `0.6` | Truncation selection threshold for invasion targets (1.0 picks the best, 0.0 picks at random). |
| `INVASION_TARGET_PRIO_NOT_ENEMY_FACTOR` | `0.17` | Priority factor for an invasion target that is not an actual enemy. |
| `MIN_INVASION_UNITS_READY_TO_EXECUTE` | `0.25` | Absolute floor: the AI never launches with fewer than this share of assigned units ready. |
| `INVASION_UNITS_READY_AT_MIN_PLAN` | `0.75` | Share of units ready required at the minimum plan value. |
| `INVASION_UNITS_READY_AT_MAX_PLAN` | `0.25` | Share of units ready required at a very high plan value (1.0 or more). |
| `AI_NAVAL_GOALS_UPDATE_FREQUENCY_DAYS` | `7` | Days between regeneration of naval AI objectives (affects performance). |
| `ARMY_LEADER_ASSIGN_KEEP_CURRENT_LEADER_FACTOR` | `1.2` | Score boost for keeping the current leader; above 1.0 favours the current one. |
| `ARMY_LEADER_ASSIGN_DONT_STEAL_OTHER_FACTOR` | `0.75` | Score reduction for leaders assigned elsewhere; below 1.0 discourages reassigning them. |
| `ARMY_LEADER_ASSIGN_WITHDRAW_DAYS` | `7` | Days without an order the HQ can influence after which a general withdraws from HQ. |
| `ARMY_LEADER_MIN_DIVISIONS_FOR_HQ` | `10` | Divisions an army needs before the AI deploys an HQ unit for it. |
| `MAX_DEPLOYED_ARMY_HQS` | `5` | Most army HQs the AI deploys at once. |
| `MAX_CAPTURED_GENERALS_TO_STOP_HQ_DEPLOY` | `3` | The AI stops deploying new army HQs once this many of its leaders are captured. |
| `AREA_DEFENSE_SETTING_BORDERS` | `false` | Area defense setting for borders (no Lua comment). |
| `AREA_DEFENSE_SETTING_FACILITY` | `false` | Area defense setting for facilities (no Lua comment). |
| `AIFC_UPDATE_FREQUENCY_DAYS` | `5` | Days between runs of AI force concentration (AIFC); lowering it may cost performance. |
| `AIFC_FRESHNESS_BASE_VALUE` | `45.0` | Starting freshness of an AIFC front; at zero the AI gives up the target and picks another. |
| `AIFC_REFRESH_NEED_PER_DAY` | `1.0` | Freshness lost each day. |
| `AIFC_REFRESH_NEED_SUPPLY_FACTOR_PER_DAY` | `0.8` | Freshness lost each day, times the average supply ratio. |
| `AIFC_FRESHNESS_ADD_ON_PROGRESS` | `25.0` | Freshness gained when the AI advances a province along the target path. |
| `AIFC_UNIT_RATIO_BASE` | `0.15` | Share of extra or desired units that can go to force concentration after front minimums are met. |
| `AIFC_MAX_NR_FRONTS` | `4` | How many of the highest-scoring fronts are considered for force concentration. |
| `AIFC_CA_DIVISIONS_PER_PROVINCE` | `3` | Baseline divisions per province the AI wants. |
| `AIFC_ACTIVATE_AVG_ORG_RATIO_THRESHOLD` | `0.2` | The offensive order activates only above this average organisation. |
| `AIFC_ACTIVATE_IN_POSITION_RATIO_THRESHOLD` | `0.3` | The offensive order activates only when more than this share of divisions is in position. |
| `AIFC_OFFENSIVE_DEACTIVATION_DAYS_THRESHOLD` | `5` | Days the conditions must stay unmet before the offensive order is deactivated. |
| `AIFC_UNIT_NUDGE_FREQUENCY_DAYS` | `15` | On average every this many days the AI checks whether another division in the front fits better. |
| `AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_BREAKTHROUGH` | `11.0` | Weight of breakthrough when force concentration scores a division for the offensive (no Lua comment). |
| `AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_SOFT_ATTACK` | `6.0` | Weight of soft attack when force concentration scores a division for the offensive (no Lua comment). |
| `AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_HARD_ATTACK` | `8.0` | Weight of hard attack when force concentration scores a division for the offensive (no Lua comment). |
| `AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_ARMOR` | `30.0` | Weight of armor when force concentration scores a division for the offensive (no Lua comment). |
| `AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_PIERCING` | `4.0` | Weight of piercing when force concentration scores a division for the offensive (no Lua comment). |
| `AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_HARDNESS` | `300.0` | Weight of hardness when force concentration scores a division for the offensive (no Lua comment). |
| `AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_SPEED` | `15.0` | Weight of speed when force concentration scores a division for the offensive (no Lua comment). |
| `AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_INITIATIVE` | `5.0` | Weight of initiative when force concentration scores a division for the offensive (no Lua comment). |
| `AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_ORGANISATION` | `0.3` | Weight of organisation when force concentration scores a division for the offensive (no Lua comment). |
| `AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_HITPOINTS` | `0.3` | Weight of hit points when force concentration scores a division for the offensive (no Lua comment). |
| `AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_DEFENSE` | `-0.2` | Weight of defense when force concentration scores a division for the offensive (no Lua comment). |
| `AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_ENTRENCHMENT` | `-0.5` | Weight of entrenchment when force concentration scores a division for the offensive (no Lua comment). |
| `AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_EXPERIENCE` | `300.0` | Weight of experience when force concentration scores a division for the offensive (no Lua comment). |
| `AIFC_TARGET_IGNORE_VP_THRESHOLD` | `10` | Victory points a target needs to be considered at all. |
| `AIFC_TARGET_SUPPLY_HUB_BASE_SCORE` | `20.0` | Base target score of a supply hub. |
| `AIFC_TARGET_NAVAL_BASE_BASE_SCORE` | `10.0` | Base target score of a naval base. |
| `AIFC_TARGET_NAVAL_BASE_SCORE_PER_LEVEL` | `1.0` | Score added per naval base level. |
| `AIFC_TARGET_VP_SCORE_FACTOR` | `1.0` | Score per victory point. |
| `AIFC_TARGET_CAPITAL_SCORE_EXTRA` | `5.0` | Extra score for capitals on top of the VP score. |
| `AIFC_TARGET_SHORT_PATH_PENALTY_FACTOR` | `0.1` | Penalty factor for short paths (3 provinces or fewer including the start). |
| `AIFC_TARGET_PERSISTED_FACTOR` | `30.0` | Bonus for persisted targets, so the AI picks a target again after the front reforms or a save is loaded. |
| `AIFC_PATH_MAX_COST` | `7.0` | Highest total path cost allowed. Raising it can cause stuttering because larger areas are evaluated. |
| `AIFC_PATH_COST_ADJ_NORMAL` | `1.0` | Path cost for a normal adjacency. |
| `AIFC_PATH_COST_ADJ_STRAIT` | `4.0` | Path cost for a strait crossing. |
| `AIFC_PATH_COST_ADJ_RIVER` | `2.0` | Path cost for a river crossing. |
| `AIFC_PATH_COST_ADJ_RIVER_LARGE` | `3.0` | Path cost for a large river crossing. |
| `AIFC_PATH_COST_TRN_MOUNTAINS` | `3.0` | Force concentration path cost for mountains terrain (no Lua comment). |
| `AIFC_PATH_COST_TRN_FOREST` | `1.2` | Force concentration path cost for forest terrain (no Lua comment). |
| `AIFC_PATH_COST_TRN_DESERT` | `1.2` | Force concentration path cost for desert terrain (no Lua comment). |
| `AIFC_PATH_COST_TRN_HILLS` | `1.2` | Force concentration path cost for hills terrain (no Lua comment). |
| `AIFC_PATH_COST_TRN_JUNGLE` | `3.0` | Force concentration path cost for jungle terrain (no Lua comment). |
| `AIFC_PATH_COST_TRN_PLAINS` | `0.8` | Force concentration path cost for plains terrain (no Lua comment). |
| `AIFC_PATH_COST_TRN_URBAN` | `1.0` | Force concentration path cost for urban terrain (no Lua comment). |
| `AIFC_PATH_COST_TRN_MARSH` | `3.0` | Force concentration path cost for marsh terrain (no Lua comment). |
| `AIFC_PATH_COST_PER_FORT_LEVEL` | `0.3` | Fort level multiplier: cost is multiplied by 1.0 plus this times the fort level (fort levels above 0 only). |
| `AIFC_PATH_COST_HAS_SUPPLY_HUB` | `0.5` | Path cost factor when the entered province has a supply hub. |
| `AIFC_PATH_COST_HAS_NAVAL_BASE` | `0.5` | Path cost factor when the entered province has a naval base. |
| `AIFC_PATH_COST_RAILWAY_CONNECTION` | `0.75` | Path cost factor when the provinces are linked by a railway above level 0. |
| `RAIDS_ENABLE_AI` | `true` | Whether the AI uses the raid system. |
| `RAIDS_CREATE_FREQUENCY_DAYS` | `7` | Days between runs of the AI raid creation logic. |
| `RAIDS_SCORE_DIFF_TO_CANCEL` | `0.3` | Lets the AI cancel low-scoring raids that block higher-scoring ones for lack of command power, when the lower score is under this share of the higher one. |
| `RAIDS_COMMAND_POWER_CAP_TO_CREATE` | `60.0` | The AI only creates raids when the command power cap is at least this. |
| `RAIDS_MIN_SUCCESS_FOR_LAUNCH` | `0.65` | The AI does not launch a raid below this success chance; a raid type can override it with `ai_min_success_chance`. |
| `RAIDS_CANCEL_AFTER_DAYS_LAUNCHABLE` | `60` | Days a raid may stay launchable but unlaunched before the AI cancels it. |
| `RAIDS_NUKE_TARGET_CUT_OFF` | `10` | For nuke targets the AI picks only among this many top-scoring targets. |
| `RAIDS_UNIT_SCORE_SUCCESS_CHANCE_FACTOR` | `500.0` | Multiplier on a unit's success chance modifier when the AI picks raid units. |
| `RAIDS_UNIT_SCORE_DISTANCE_KM_FACTOR` | `0.1` | Multiplier on distance in km when the AI picks raid units. |
| `RAIDS_AVOID_SAME_TARGET_DURATION_DAYS` | `180` | Days after a raid ends or is cancelled during which the AI is less likely to raid the same target. |
| `RAIDS_AVOID_SAME_TARGET_FACTOR` | `0.4` | Score factor for a new raid on a target already raided or tried. |
| `PATROL_FLEETS_PER_INVASION_REGION_ON_PATH` | `2` | Patrol fleet templates the AI tries to use per invasion region on the path when building dominance. |
| `AI_MIN_DOMINANCE_MARGIN` | `200` | The AI tries to exceed the required dominance in a region by at least this much. |
| `CONVOY_DANGER_FOR_MAX_IMPORTANCE` | `400` | Convoy danger at which the importance of protecting a route is at its maximum. |
| `NUM_CONVOYS_FOR_MAX_PROTECTION` | `50` | Convoy count at which that importance is at its maximum. |
| `CONVOY_RAIDING_TARGET_RECALC_DAYS` | `15` | Days between the AI's re-evaluation of convoy raiding regions. |
| `STRIKE_FORCE_TARGET_RECALC_DAYS` | `5` | Days between re-evaluation of strike force regions. |
| `AI_OBJECTIVE_DEFAULT_TARGET_RECALC_DAYS` | `5` | Default days between re-evaluation of naval mission target regions; specific objectives can override it. |
| `DANGEROUS_ENEMY_ARMY_SIZE` | `100` | Enemy army size above which the AI adds naval invasion defense importance. |
| `DANGEROUS_DISTANCE_TO_CAPITAL` | `1000.0` | Pixel distance from the target province to the capital within which the AI adds invasion defense importance. |
| `NAVAL_STRIKE_FORCE_OBJECTIVE_IMPORTANCE` | `{ 0.1875, 0.25, 0,0, 0.0625, 0,0, 0.125, 0,0,0 }` | Importance per naval objective group; the order matters (see the Lua comment for the group order). |
| `MIN_FACTORIES_TO_WANT_TO_IMPORT` | `{ 0, 0, 0, 0, 0, 0, 10 }` | Civilian factories the AI needs before it considers importing a resource; one entry per strategic resource, in resource order. |
| `SUGGESTED_NUM_MAX_CARRIERS` | `4` | Starting guess for how many carriers to plan when evaluating AI builds and task force suggestions. |

Values that differ from the wiki's table (33). The wiki page shows an older value. All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

| Define | Page value | 1.19.3 value |
| --- | --- | --- |
| `RESEARCH_AHEAD_BONUS_FACTOR` | `4.0` | `25.0` |
| `PRODUCTION_EQUIPMENT_SURPLUS_FACTOR` | `0.5` | `0.8` |
| `LAND_DESIGN_ALTERNATIVE_ABSENT` | `1000000` | `30000` |
| `LAND_DESIGN_DEMAND_ABSENT` | `0` | `1` |
| `DESIRE_USE_XP_TO_UNLOCK_ARMY_SPIRIT` | `0.20` | `0.35` |
| `DESIRE_USE_XP_TO_UNLOCK_NAVY_SPIRIT` | `0.20` | `0.35` |
| `DESIRE_USE_XP_TO_UNLOCK_AIR_SPIRIT` | `0.25` | `0.35` |
| `DAYS_BETWEEN_CHECK_BEST_DOCTRINE` | `7` | `30` |
| `HIGH_COMMAND_ADDED_WEIGHT_FACTOR` | `0.25` | `1.10` |
| `CHIEF_ADDED_WEIGHT_FACTOR` | `12.5` | `2.4` |
| `START_TRAINING_EQUIPMENT_LEVEL` | `0.95` | `0.40` |
| `STOP_TRAINING_EQUIPMENT_LEVEL` | `0.90` | `0.25` |
| `UPGRADE_PERCENTAGE_OF_FORCES` | `0.03` | `0.20` |
| `REGION_CONVOY_DANGER_DAILY_DECAY` | `1` | `2` |
| `PRODUCTION_WAIT_TO_FINISH_IF_EXPENSIVE` | `0.25` | `0.1` |
| `NAVAL_MISSION_PATROL_NEAR_CONTROLLED` | `120` | `140` |
| `NAVAL_AIR_SUPERIORITY_IMPORTANCE` | `0.10` | `4.0` |
| `NAVAL_FIGHTERS_PER_PLANE` | `1.0` | `1.1` |
| `LAND_DEFENSE_AIR_SUPERIORITY_IMPORTANCE` | `1.0` | `1.5` |
| `ARMY_CHIEF_SCORE_MULTIPLIER` | `2.0` | `1.0` |
| `AIR_CHIEF_SCORE_MULTIPLIER` | `1.5` | `1.0` |
| `MANPOWER_RATIO_REQUIRED_TO_PRIO_MOBILIZATION_LAW` | `0.4` | `0.55` |
| `UPGRADES_DEFICIT_LIMIT_DAYS` | `7` | `60` |
| `MAX_MISSION_PER_TASKFORCE` | `{ 0, 1.5, 6, 1.5, 4, 2, 2, 0, 0, 10 }` | `{ 0, 1, 4, 1.5, 4, 2, 2, 0, 0, 10 }` |
| `MAX_SCREEN_FORCES_FOR_INVASION_SUPPORT` | `0.25` | `0` |
| `MAX_CAPITAL_FORCES_FOR_INVASION_SUPPORT` | `0.25` | `0` |
| `MAX_PATROL_TO_STRIKE_FORCE_RATIO` | `3.0` | `4.0` |
| `NAVAL_BASE_RATIO_ALLOCATED_FOR_REPAIRS` | `0.25` | `0.5` |
| `NAVAL_BASE_RATIO_ALLOCATED_FOR_REPAIRS_IN_WAR_TIME` | `0.6` | `0.75` |
| `MAX_FUEL_CONSUMPTION_RATIO_FOR_AIR_TRAINING` | `0.20` | `1.0` |
| `MIN_INVASION_PLAN_VALUE_TO_EXECUTE` | `0.2` | `0.3` |
| `MIN_INVASION_ORG_FACTOR_TO_EXECUTE` | `0.75` | `0.4` |
| `INDUSTRIAL_ORG_RESEARCH_BONUS_FACTOR` | `1.0` | `10.0` |

**Kit correction** Defines in the wiki's table that 1.19.3 no longer has (14). The successor column names a define with the same value and a matching name, which is an inference. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` for the absence; [unverified] for the successor.

| Define | Page value | Likely successor |
| --- | --- | --- |
| `PLAN_FRONT_SECTION_MAX_LENGTH` | `18` | none found |
| `PLAN_FRONT_SECTION_MIN_LENGTH` | `10` | none found |
| `NAVAL_SUPREMACY_WEIGHT_PER_DIVISION_ON_INVASION_ORDER` | `6` | none found |
| `DIVISION_DESIGN_WEIGHTS` | `{ 0.5, 1.0, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, -0.25, 0.0, 0.0, 0....` | none found |
| `DIVISION_DESIGN_MANPOWER_WEIGHT` | `0.005` | none found |
| `DIVISION_DESIGN_STOCKPILE_WEIGHT` | `0.01` | none found |
| `DIVISION_DESIGN_COMBAT_WIDTH_WEIGHT` | `-1.0` | none found |
| `DIVISION_DESIGN_COMBAT_WIDTH_TARGET_WEIGHT` | `-200.0` | none found |
| `COMBINED_ARMS_LEVEL` | `1` | none found |
| `HOUR_BAD_COMBAT_REEVALUATE` | `48` | none found |
| `INVASION_DISTANCE_RANDOMNESS` | `300` | none found |
| `LAND_DEFENSE_INTERSEPTORS_PER_BOMBERS` | `0.8` | `LAND_DEFENSE_INTERCEPTORS_PER_BOMBERS` (spelling fixed) |
| `LAND_DEFENSE_INTERSEPTORS_PER_PLANE` | `0.1` | `LAND_DEFENSE_INTERCEPTORS_PER_PLANE` (spelling fixed) |
| `ARMY_LEADER_ASSIGN_KEEP_LEADER` | `500` | `ARMY_LEADER_ASSIGN_KEEP_CURRENT_LEADER_FACTOR` (different scale) |

## NOperatives <a id="NOperatives"></a>

**Kit addition** NOperatives in 1.19.3: 125 defines in `common/defines/00_defines.lua`; the wiki's table lists 124. [vanilla-confirmed 1.19.3]

Defines the wiki's table lacks (1). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `BECOME_SPYMASTER_FI_COST` | `1` | Faction initiative spent to become Spy Master (faction DLC only). |

## NIntel <a id="NIntel"></a>

**Kit addition** NIntel in 1.19.3: 223 defines in `common/defines/00_defines.lua`; the wiki's table lists 217, 3 of them removed in 1.19.3. [vanilla-confirmed 1.19.3]

Defines the wiki's table lacks (9). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `INTEL_TO_SHOW_GRAND_DOCTRINE` | `{ 0.3, 0.3, 0.3 }` | Minimum intel to see a country's grand doctrine, as { army, navy, air }. |
| `INTEL_TO_SHOW_SUBDOCTRINES` | `{ 0.5, 0.5, 0.5 }` | Minimum intel to see subdoctrines, as { army, navy, air }. |
| `INTEL_TO_SHOW_MASTERY` | `{ 0.7, 0.7, 0.7 }` | Minimum intel to see mastery levels, as { army, navy, air }. |
| `NAVAL_DOMINANCE_INTEL_LOW` | `0.4` | You need more intel than this to get any dominance. |
| `NAVAL_DOMINANCE_INTEL_LOW_DOMINANCE_PENALTY_START` | `0.1` | At or below this intel, dominance is cut to the minimum penalty value below. |
| `NAVAL_DOMINANCE_INTEL_LOW_DOMINANCE_MIN_PENALTY` | `0.5` | Share of dominance you keep at the penalty start intel, rising to 1 at `NAVAL_DOMINANCE_INTEL_LOW`. |
| `RAID_MIN_INTEL_FOR_WARNING_ON_LAUNCH` | `0.1` | Intel of the relevant type needed to get a warning when a raid is launched. |
| `RAID_MIN_INTEL_FOR_WARNING_HALFWAY_TO_LAUNCH` | `0.5` | Intel needed for a warning halfway through raid preparation. |
| `RAID_MIN_INTEL_FOR_WARNING_EARLY_PREPARATION` | `0.8` | Intel needed for a warning early in raid preparation. |

Values that differ from the wiki's table (3). The wiki page shows an older value. All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

| Define | Page value | 1.19.3 value |
| --- | --- | --- |
| `AIR_MAPICON_MISSION_COUNT_INTEL_MIN` | `{ 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3 }` | `{ 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3 }` |
| `AIR_MAPICON_MISSION_COUNT_INTEL_MAX` | `{ 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6 }` | `{ 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6 }` |
| `AIR_MAPICON_MISSION_COUNT_INTEL_RANGE_AT_LOWEST_INTEL` | `{ 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5 }` | `{ 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5 }` |

**Kit correction** Defines in the wiki's table that 1.19.3 no longer has (3). The successor column names a define with the same value and a matching name, which is an inference. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` for the absence; [unverified] for the successor.

| Define | Page value | Likely successor |
| --- | --- | --- |
| `NAVAL_SUPREMACY_INTEL_LOW` | `0.4` | `NAVAL_DOMINANCE_INTEL_LOW` |
| `NAVAL_SUPREMACY_INTEL_LOW_SUPREMACY_PENALTY_START` | `0.1` | `NAVAL_DOMINANCE_INTEL_LOW_DOMINANCE_PENALTY_START` |
| `NAVAL_SUPREMACY_INTEL_LOW_SUPREMACY_MIN_PENALTY` | `0.5` | `NAVAL_DOMINANCE_INTEL_LOW_DOMINANCE_MIN_PENALTY` |

## NSupply <a id="NSupply"></a>

**Kit addition** NSupply in 1.19.3: 103 defines in `common/defines/00_defines.lua`; the wiki's table lists 102. [vanilla-confirmed 1.19.3]

`SUPPLY_NODE_MIN_SUPPLY_THRESHOLD` keeps its Lua comment "Currently unused?" in 1.19.3. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`

Defines the wiki's table lacks (1). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `NAVAL_SUPPLY_HUB_REDUCTION_FACTOR` | `0.0` | Share by which a naval supply hub reduces the fleet's supply need. |

## NAITheatre <a id="NAITheatre"></a>

**Kit addition** NAITheatre in 1.19.3: 16 defines in `common/defines/00_defines.lua`; the wiki's table lists 17, 1 of them removed in 1.19.3. [vanilla-confirmed 1.19.3]

**Kit correction** Defines in the wiki's table that 1.19.3 no longer has (1). The successor column names a define with the same value and a matching name, which is an inference. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua` for the absence; [unverified] for the successor.

| Define | Page value | Likely successor |
| --- | --- | --- |
| `AI_THEATRE_PERCENTAGE_OF_UNITS_TO_KEEP_IN_NEIGHBOR_DEFENSIVE_ORDERS` | `0.05` | none found |

## NProject <a id="NProject"></a>

**Kit addition** NProject in 1.19.3: 33 defines in `common/defines/00_defines.lua`; the wiki's table lists 29. [vanilla-confirmed 1.19.3]

Defines the wiki's table lacks (4). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `AMOUNT_OF_SUPPORTIVE_SCIENTISTS` | `3` | Supportive scientists one facility can have. |
| `SUPPORTIVE_SCIENTISTS_FRACTION` | `0.25` | How effective supportive scientists are compared with normal strength. |
| `SUPPORTIVE_SCIENITST_PROGRESS_BONUS` | `0.1` | Share of an iteration's progress given to the supporting scientist country's project. The define name keeps the spelling `SCIENITST`. |
| `SUPPORTIVE_SCIENTISTS_SHARING_BONUS` | `0.05` | Research sharing percentage per supportive scientist, global per faction. |

## NFactions <a id="NFactions"></a>

**Kit addition** NFactions is new. 1.19.3 has 76 defines in this group in `common/defines/00_defines.lua`; the wiki page has no section for it. [vanilla-confirmed 1.19.3]

Defines the wiki's table lacks (76). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `FACTION_INITIATIVE_CHANGE_RULE_COST` | `1` | Faction initiative spent to change a faction rule. |
| `FACTION_DOCTRINE_SHARING_UNLOCK_COST` | `1` | Cost of unlocking doctrine sharing for one folder. |
| `DOCTRINE_SHARING_BASE_MASTERY_GAIN_MONTHLY` | `10` | Base monthly mastery gained while doctrine sharing is on. |
| `DOCTRINE_SHARING_MONTHLY_MASTERY_GAIN_PER_COMMANDER` | `2` | Extra monthly mastery per theater commander while doctrine sharing is on. |
| `AI_FACTION_POWER_PROJECTION_TRESHOLD` | `1000` | AI score turns negative when the faction's power projection is below this. |
| `AI_FACTION_POWER_PROJECTION_VALUE` | `0.01` | AI score per power projection point. |
| `AI_MIN_POWER_PROJECTION_SCORE` | `-100` | Lowest AI score from power projection. |
| `AI_MAX_POWER_PROJECTION_SCORE` | `100` | Highest AI score from power projection. |
| `FACTION_INFLUENCE_LEND_LEASE_FACTOR` | `0.025` | How much a country's contribution to the faction affects its influence. |
| `FACTION_INFLUENCE_WAR_SCORE_FACTOR` | `0.1` | How much the country's war score affects its influence. |
| `FACTION_INFLUENCE_EFFECTS_FACTOR` | `1` | How much faction effects affect influence. |
| `FACTION_INFLUENCE_INDUSTRIAL_CAPACITY_FACTOR` | `5` | How much the country's industry affects influence. |
| `FACTION_INFLUENCE_GARRISON_SUPPORT_PROVIDER_FACTOR` | `0.001` | Influence effect of garrison support provided. |
| `FACTION_INFLUENCE_GARRISON_SUPPORT_RECIEVER_FACTOR` | `-0.001` | Influence effect of garrison support received (negative). The name keeps the spelling `RECIEVER`. |
| `FACTION_INFLUENCE_EXPEDITIONARY_FORCE_PROVIDER_FACTOR` | `0.01` | Influence effect of expeditionary forces provided. |
| `FACTION_CONTRIBUTION_SETTING_INCREASE` | `0.01` | Step size when raising or lowering contribution settings. |
| `FACTION_CONTRIBUTION_DEBT_LIMIT` | `250` | How far into debt you may go by spending contribution. |
| `FACTION_INFLUENCE_EXPEDITIONARY_FORCE_RECIEVER_FACTOR` | `-0.02` | Influence effect of expeditionary forces received (negative). |
| `FACTION_MANPOWER_GIVE_CONTRIBUTION_SCALAR` | `0.1` | Contribution gained per unit of recruitable population given to the faction. |
| `FACTION_MANPOWER_RECIEVE_CONTRIBUTION_SCALAR` | `0.1` | Contribution it costs to receive one unit of recruitable population. |
| `FACTION_INFLUENCE_SCIENTIST_CONTRIBUTION_VALUE` | `0.5` | Contribution you get for one of your scientists working for another country. |
| `ASSIGN_FACILITY_TO_FACTION_INITIATIVE_COST` | `1` | Initiative cost of assigning a facility to a faction. |
| `FACTION_ASSIGN_SCIENTIST_COST` | `25` | Political power cost of assigning a supportive scientist. |
| `FACTION_UNLOCK_COMMANDER_COST` | `1` | Initiative cost of creating a new faction theater. |
| `FACTION_REPLACE_COMMANDER_COST` | `1` | Faction initiative cost of replacing someone else's theater commander. |
| `FACTION_SUPREME_COMMANDER_EFFECTIVENESS` | `0.2` | How effective supreme commanders are compared with their normal field marshal or admiral role. |
| `FACTION_THEATER_COMMANDER_COUNTRY_LIMIT_BASE` | `3` | Countries a theater commander can lead at base. |
| `FACTION_THEATER_COMMANDER_COUNTRY_LIMIT_SKILL_FACTOR` | `1` | Countries added per skill level. |
| `FACTION_THEATER_COMMANDER_REGION_LIMIT_BASE` | `3` | Base region limit of a theater commander. |
| `FACTION_THEATER_COMMANDER_REGION_LIMIT_SKILL_FACTOR` | `1` | Region limit added per skill level. |
| `FACTION_THEATER_COMMANDER_LAND_SUPPLY_USAGE_MODIFIER_BASE` | `0` | Base land supply usage modifier (percent; negative is good). |
| `FACTION_THEATER_COMMANDER_LAND_SUPPLY_USAGE_MODIFIER_SKILL_FACTOR` | `-0.01` | Land supply usage modifier per skill level. |
| `FACTION_THEATER_COMMANDER_NAVY_SUPPLY_USAGE_MODIFIER_BASE` | `0` | Base navy supply usage modifier (percent; negative is good). |
| `FACTION_THEATER_COMMANDER_NAVY_SUPPLY_USAGE_MODIFIER_SKILL_FACTOR` | `-0.01` | Navy supply usage modifier per skill level. |
| `FACTION_THEATER_COMMANDER_SECONDARY_BONUS` | `0.5` | Scale on the supply modifiers when a land commander gives the bonus to the navy and the other way round. |
| `THEATER_COMMANDER_LAND_EXPERIENCE_SCALE` | `0.1` | Experience a theater field marshal gains from land combat. |
| `THEATER_COMMANDER_NAVY_EXPERIENCE_SCALE` | `0.1` | Experience a theater admiral gains from naval combat. |
| `BECOME_FACTION_LEADER_INFLUENCE_THRESHOLD` | `0.4` | Minimum influence share needed to take over faction leadership. |
| `MAX_PROJECT_COUNT` | `3` | Most projects a faction can have. |
| `AI_THEATER_CREATION_PENALTY` | `2.5` | Linear penalty each theater adds to the AI chance of creating another (higher is worse). |
| `BECOME_FACTION_LEADER_INFLUENCE_WEIGHT` | `1` | Weight of faction influence in how close a member is to taking over leadership. |
| `FACTION_INFLUENCE_LEADER_BONUS` | `200` | Influence a faction member gets for being the leader. |
| `FACTION_TAKE_OVER_RELUCTANCE_VERSUS_HUMAN_INFLUENCE` | `1.5` | Extra influence an AI country needs, as a multiplier, compared with a human to take over leadership. |
| `AI_PICK_FROM_TOP_AMOUNT` | `3` | The AI picks what to spend initiative on from this many top options, by weighted random. |
| `AI_PING_AREA_PRIORITY` | `100` | AI strategy value added for pinged regions (area priority). |
| `AI_PING_FRONT_UNIT_REQUEST` | `100` | Value added for pinged regions (front unit requests). |
| `AI_PING_FORCE_CONCENTRATION_FRONT_FACTOR` | `100` | Value added for pinged regions (force concentration front factor). |
| `AI_PING_FORCE_CONCENTRATION_TARGET_WEIGHT` | `100` | Value added for pinged regions (force concentration target weight). |
| `AI_PING_INVASION_UNIT_REQUEST` | `100` | Value added for pinged regions (invasion unit requests). |
| `AI_PING_NAVAL_DOMINANCE` | `100` | Value added for pinged regions (naval dominance). |
| `AI_PING_FORCE_CONCENTRATION_CAREFUL_FACTOR` | `0.5` | Force concentration factor in careful order execution mode. |
| `AI_PING_FORCE_CONCENTRATION_AGGRESSIVE_FACTOR` | `1.2` | Force concentration factor in aggressive order execution mode. |
| `RANK_FOR_SHINY_FLAG` | `1` | The top N factions get a shiny flag on the factions screen. |
| `PEACE_CONFERENCE_MINIMAL_REQUIREMENT` | `0.5` | How much larger your faction power projection must be than the next biggest contender to start getting the peace conference discount (0.5 means 50 percent larger). |
| `PEACE_CONFERENCE_MAX_DISCOUNT` | `0.25` | Largest peace conference discount for the bigger faction; it grows from 0 at the minimal requirement. |
| `MAX_NUM_SHORT_TERM_GOALS` | `1` | Most short-term goals a faction can have at once. |
| `MAX_NUM_MEDIUM_TERM_GOALS` | `1` | Most medium-term goals at once. |
| `MAX_NUM_LONG_TERM_GOALS` | `1` | Most long-term goals at once. |
| `REPLACING_UNFINISHED_FACTION_GOAL_COST` | `1` | Cost of replacing a goal that is not finished. |
| `PASSIVE_INITIATIVE_GENERATION` | `0.015` | Initiative generated per day, scaled by manifest progress and influence share. |
| `MAX_FACTION_THEATERS` | `4` | Most faction theaters that can be created. |
| `AI_FACTION_THEATER_TEMPLATE_SELECTION_RANDOMNESS` | `1` | The AI picks a weighted random template from the top of the list; higher means more random. |
| `AI_FACTION_THEATER_COMMANDER_SELECTION_RANDOMNESS` | `1` | Same randomness for theater commander choice. |
| `FACTION_INTELLIGENCE_ALLOWED_ADVISOR_TRAIT` | `{ "head_of_intelligence", "mastermind_code_cracker", "expert_code_cracker", "spymaster", "spymaster_no_lar"...` | Advisor traits that qualify a political advisor to be chosen as spymaster. |
| `FACTION_INTELLIGENCE_UNLOCK_COST` | `1` | Cost of unlocking faction intelligence (no Lua comment). |
| `FACTION_INTELLIGENCE_SHARING_BONUS` | `0.05` | Bonus from sharing intelligence in a faction. |
| `FACTION_INTELLIGENCE_SHARING_SPY_SLOT_GAIN` | `1` | Operative slots an advisor position unlocks, not counting the spymaster. |
| `FACTION_INTELLIGENCE_HEAD_OF_CRYPTOLOGY_BONUS_COUNTRY` | `0.1` | Bonus the Head of Cryptology gives the country that holds the position. |
| `FACTION_INTELLIGENCE_HEAD_OF_CRYPTOLOGY_BONUS_OTHERS` | `0.05` | Bonus it gives the other faction members. |
| `FACTION_INTELLIGENCE_HEAD_OF_OPERATIONS_BONUS_COUNTRY` | `0.1` | Bonus the Head of Operations gives the country that holds the position. |
| `FACTION_INTELLIGENCE_HEAD_OF_OPERATIONS_BONUS_OTHERS` | `0.05` | Bonus it gives the other faction members. |
| `FACTION_INTELLIGENCE_HEAD_OF_COUNTER_INTEL_BONUS_COUNTRY` | `0.1` | Bonus the Head of Counter Intelligence gives the country that holds the position (the Lua comment says Operations). |
| `FACTION_INTELLIGENCE_HEAD_OF_COUNTER_INTEL_BONUS_OTHERS` | `0.05` | Bonus it gives the other faction members. |
| `FACTION_DEFAULT_ICON` | `"GFX_faction_logo_generic"` | Icon for a generic faction created in game that has no icon set up. |
| `FACTION_DEFAULT_TEMPLATE` | `"faction_template_generic"` | Template used when no faction template is specified. |
| `AI_DAYS_TO_SELECT_GOAL` | `14` | Days the AI takes to select a faction goal (no Lua comment). |

## NDoctrines <a id="NDoctrines"></a>

**Kit addition** NDoctrines is new. 1.19.3 has 12 defines in this group in `common/defines/00_defines.lua`; the wiki page has no section for it. [vanilla-confirmed 1.19.3]

Defines the wiki's table lacks (12). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `DEFAULT_REWARD_MASTERY` | `100.0` | Mastery needed to unlock a doctrine reward when none overrides it. |
| `BASE_MASTERY_GAIN_TARGET_MANPOWER` | `100000.0` | Manpower contributing to mastery beyond which gains show diminishing returns. |
| `TRAINING_MASTERY_GAIN_FACTOR` | `0.1` | How much training counts toward mastery compared with combat and missions. |
| `MAX_MONTHLY_MASTERY_GAIN` | `40.0` | Monthly mastery gain never exceeds this. |
| `MIN_MASTERY_GAIN_PER_DAY` | `0.0` | If there is any mastery gain it is raised to at least this per day. |
| `MASTERY_BAR_ANIMATION_SPEED_PER_DAILY_MASTERY` | `4.0` | How fast the mastery bar animates per point of daily mastery. |
| `MASTERY_BAR_MAX_ANIMATION_SPEED` | `40.0` | Top animation speed of the mastery bar. |
| `MASTERY_BANK_CONVERSION_RATE` | `0.25` | Share of mastery gained after a track is finished or empty that is banked. |
| `MASTERY_BANK_MAX` | `200.0` | Most mastery that can be banked. |
| `MILITARY_ATTACHE_MASTERY_TRANSFER_FACTOR` | `0.1` | Share of the visited country's unit mastery gain, per track, that military attaches add. |
| `THEATER_COMMANDER_UNITS_MASTERY_GAIN_FACTOR_PER_SKILL` | `0.01` | Share of unit mastery gain in a theater passed to the commander's country, per attack plus defense skill point. |
| `NAVAL_MISSION_MASTERY_GAIN_FACTORS` | `{ 0.0, 0.2, 0.05, 0.3, 0.2, 0.2, 0.2, 0.0, 0.0, 0.0 }` | Mastery gain per naval mission type (hold, patrol, strike force, convoy raiding, convoy escort, mines planting, mines sweeping, train, reserve fleet, naval invasion support); the comment says it is reduced like training. |

## NMapMode <a id="NMapMode"></a>

**Kit addition** NMapMode in 1.19.3: 105 defines in `common/defines/00_graphics.lua`; the wiki's table lists 79. [vanilla-confirmed 1.19.3]

Defines the wiki's table lacks (26). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `NAVAL_REGION_TRANSPARENCY_RATIO_MAX` | `0.8` | Highest transparency ratio on the strategic navy region map. |
| `NAVAL_REGION_TRANSPARENCY_RATIO_MIN` | `0.5` | Lowest transparency ratio on the strategic navy region map. |
| `NAVAL_REGION_TRANSPARENCY_RANGE` | `2000.0` | Range of naval dominance drawn on the strategic navy region map. |
| `NAVAL_DOMINANCE_TREND_BAR_HIDE_RATIO` | `0.72` | Camera height ratio (to maximum height) below which the dominance trend bar is hidden. |
| `DEPLOYED_GENERAL_UNIT_LINE_COLOR` | `{ 1.0, 1.0, 1.0, 0.3 }` | Colour of the line between a deployed general and the divisions when no commander ability is active. |
| `DEPLOYED_GENERAL_UNIT_LINE_COLOR_ABILITY_ACTIVE` | `{ 1.0, 0.55, 0.1, 1.0 }` | Colour of that line when at least one commander ability is active. |
| `SHOW_DEPLOYED_GENERAL_COMMUNICATION_LINES` | `true` | Show lines between deployed generals and divisions in range. |
| `SHOW_DEPLOYED_GENERAL_NO_COMMUNICATION_LINES` | `true` | Show lines to divisions out of range. |
| `SHOW_DEPLOYED_GENERAL_FRONT_LINES` | `true` | Show the always-on line from each deployed general to the nearest point of their front. |
| `DEPLOYED_GENERAL_FRONT_LINE_MAX_CAMERA_HEIGHT` | `350.0` | Camera height above which those front lines are hidden. |
| `SHOW_DEPLOYED_GENERAL_BASE_PLATES` | `true` | Draw a round decal under each deployed general as an anchor for the lines. |
| `DEPLOYED_GENERAL_BASE_PLATE_RADIUS` | `2.5` | Radius of that decal in map units. |
| `DEPLOYED_GENERAL_BASE_PLATE_COLOR` | `{ 1.0, 1.0, 1.0, 0.9 }` | Tint of the decal; the alpha scales its whole opacity. |
| `PREPARING_RAID_ARROW_COLOR` | `{ 0.7, 0.7, 0.7, 1.0 }` | Raid map mode arrow colour for raids still in preparation. |
| `READY_RAID_ARROW_COLOR` | `{ 0.7, 0.7, 0, 0.9}` | Arrow colour for raids that can be launched. |
| `ACTIVE_RAID_ARROW_COLOR` | `{ 1, 0, 0, 0.9 }` | Arrow colour for active raids. |
| `COASTAL_FACILITY_OFFSET` | `{-1.5, 0, 1.5}` | World position offset so the facility icon does not overlap port or naval headquarter icons. |
| `NAVAL_HEADQUARTER_OFFSET` | `{1.5, 0, 1.5}` | World position offset so the naval headquarter icon does not overlap port or facility icons. |
| `CONSTRUCTION_PRIMARY_VALID_BUILD_TARGET_PROVINCE_COLOR_INDEX` | `7` | Index into `BORDER_COLOR_CUSTOM_HIGHLIGHTS` for a valid primary build target province. |
| `CONSTRUCTION_PRIMARY_INVALID_BUILD_TARGET_PROVINCE_COLOR_INDEX` | `8` | Same, invalid primary target. |
| `CONSTRUCTION_PRIMARY_FOREIGN_BUILD_TARGET_PROVINCE_COLOR_INDEX` | `9` | Same, foreign primary target. |
| `CONSTRUCTION_SECONDARY_VALID_BUILD_TARGET_PROVINCE_COLOR_INDEX` | `10` | Same, valid secondary target. |
| `CONSTRUCTION_SECONDARY_INVALID_BUILD_TARGET_PROVINCE_COLOR_INDEX` | `11` | Same, invalid secondary target. |
| `CONSTRUCTION_SECONDARY_FOREIGN_BUILD_TARGET_PROVINCE_COLOR_INDEX` | `12` | Same, foreign secondary target. |
| `FACTION_THEATER_COLOR_INDEX` | `13` | Border colour index while editing a faction theater. |
| `FACTION_THEATER_HIGHLIGHT_COLOR_INDEX` | `14` | Border colour index while hovering a faction theater map icon. |

Values that differ from the wiki's table (5). The wiki page shows an older value. All rows: [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua`.

| Define | Page value | 1.19.3 value |
| --- | --- | --- |
| `CONSTRUCTION_MAP_MODE_BUILDING_DEFAULT_COLOR` | `{ 0.43, 0.22, 0.22, 0.25 }` | `{ 0.43, 0.22, 0.22, 0.5 }` |
| `CONSTRUCTION_MAP_MODE_BUILDING_MAX_LEVEL_COLOR` | `{ 0.05, 0.1, 0.7, 0.4 }` | `{ 0.05, 0.1, 0.7, 0.8 }` |
| `CONSTRUCTION_MAP_MODE_BUILDING_LEVEL_LOW_COLOR` | `{ 0.05, 0.22, 0.0, 0.4 }` | `{ 0.2, 0.7, 0.0, 0.5 }` |
| `CONSTRUCTION_MAP_MODE_BUILDING_LEVEL_HI_COLOR` | `{ 0.4, 0.9, 0.0, 0.5 }` | `{ 0.45, 0.98, 0.0, 0.9 }` |
| `FACTIONS_COLOR_NOT_MEMBER` | `{ 0.6, 0.6, 0.6, 0.25 }` | `{ 0.7, 0.7, 0.7, 0.7 }` |

## NMapIcons <a id="NMapIcons"></a>

**Kit addition** NMapIcons in 1.19.3: 515 defines in `common/defines/00_graphics.lua`; the wiki's table lists 408. [vanilla-confirmed 1.19.3]

`DEFAULT_PRIORITY_NAVAL_ACCIDENTS` and `OPERATIVES_PRIORITY_NAVAL_ACCIDENTS` each appear twice in the Lua file with the same value 13, which is harmless. [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua`

Defines the wiki's table lacks (2). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `HOME_BASE_MAP_ICON_SCALE_DEFAULT` | `1.0` | Default scale of the home base map icon. |
| `HOME_BASE_MAP_ICON_SCALE_HIGHLIGHTED` | `1.2` | Scale of the home base map icon when highlighted. |

Map icon priority defines the wiki's table lacks (105). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua`. Each icon type exists once per map mode with the same value in every mode; the wiki page already has the same pattern for other icon types. The word "priority" is read from the name, the Lua has no comment. [unverified]

| Define pattern | Value in every mode | Count |
| --- | --- | --- |
| `<MODE>_PRIORITY_GUN_EMPLACEMENT` | `3` | 21 map modes |
| `<MODE>_PRIORITY_FACILITY` | `3` | 21 map modes |
| `<MODE>_PRIORITY_NAVAL_HEADQUARTER` | `3` | 21 map modes |
| `<MODE>_PRIORITY_NAVAL_DOMINANCE` | `13` | 21 map modes |
| `<MODE>_PRIORITY_STRATEGIC_LOCATION` | `10` | 21 map modes |

The `<MODE>` prefixes are: `DEFAULT`, `DEPLOYMENT_AIR`, `DEPLOYMENT_MILITARY`, `DEPLOYMENT_NAVY`, `DIPLOMACY`, `DIPLOMACY_FABRICATE_CLAIM`, `FACTIONS`, `IDEOLOGY`, `INFRASTRUCTURE`, `MANPOWER`, `OPERATIVES`, `PEACE_CONFERENCE`, `PLAYERS`, `RESISTANCE`, `RESOURCES`, `START_CONSTRUCTION`, `STATES`, `STRATEGIC_AIR`, `STRATEGIC_NAVY`, `STRATEGIC_REGIONS`, `SUPPLY_AREAS`.

Values that differ from the wiki's table (1). The wiki page shows an older value. All rows: [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua`.

| Define | Page value | 1.19.3 value |
| --- | --- | --- |
| `SUPPLY_AREAS_PRIORITY_ADJACENCY_RULE` | `3` | `2` |

## NAirGfx <a id="NAirGfx"></a>

**Kit addition** NAirGfx in 1.19.3: 39 defines in `common/defines/00_graphics.lua`; the wiki's table lists 38. [vanilla-confirmed 1.19.3]

Defines the wiki's table lacks (1). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `RANDOM_SCENARIO_ANIMATION_MAX_DELAY` | `3.0` | Longest delay before an animation of a gfx airplane (currently SAM and gun emplacements) starts. |

## NGraphics <a id="NGraphics"></a>

**Kit addition** NGraphics in 1.19.3: 459 defines in `common/defines/00_graphics.lua`; the wiki's table lists 423, 6 of them removed in 1.19.3. [vanilla-confirmed 1.19.3]

`MOON_LATITUDE` is still commented "NOT USED" in the Lua. [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua`

Defines the wiki's table lacks (42). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `MAP_BUILDINGS_DESTROYED_STATUS` | `60` | Health of the last building level below which the building entity uses its "destroyed" mesh, if it has one. |
| `MAP_BUILDINGS_DESTROYED_DEAD_ZONE` | `80` | Health a destroyed building must climb above before it leaves the destroyed state (a hysteresis zone). |
| `MAP_BUILDINGS_DAMAGED_THRESHOLD` | `0.80` | Average health below which a building entity enters the "damaged" state (burning or smoking). |
| `CITY_DAMAGED_THRESHOLD` | `0.80` | Average health of civilian buildings below which the city entity enters the "damaged" state. |
| `CITY_DESTROYED_THRESHOLD` | `0.30` | Average health of civilian buildings below which the city entity enters the "burning" state. |
| `STRATEGIC_NAVY_COLOR_NEUTRAL_HIGHLIGHTED` | `{0.4, 0.5, 0.6, 0.9}` | Strategic navy colour of highlighted zones without dominance. |
| `STRATEGIC_REGION_COLOR_NAVAL_HEADQUARTER` | `{ 0.4, 0.8, 0, 0.5 }` | Strategic region colour for naval headquarters. |
| `ALLIED_BATTLEPLANS_FACTION_THEATER_COLOR` | `{ 0.86, 0.32, 0.0, 1 }` | Allied battle plan colour for a faction theater. |
| `FACILITY_DISTANCE_CUTOFF` | `900` | Camera distance at which facility buildings disappear. |
| `RAID_SOURCE_MAP_STRIPES_COLOR` | `{ 0.0, 1.0, 1.0, 0.4 }` | Stripe colour for raid source areas on the map. |
| `RAID_SOURCE_MAP_STRIPES_HOVERED_COLOR` | `{ 0.3, 1.0, 1.0, 0.7 }` | Same, when hovered. |
| `RAID_ARROW_BALLISTIC_SHAPE` | `0.02` | Curvature of ballistic raid arrows; higher is more curved, lower is flatter. |
| `RAID_ARROW_BALLISTIC_MAX_HEIGHT` | `30` | Highest altitude of ballistic trajectories. |
| `RAID_ARROW_BALLISTIC_MAX_SEGMENT_LENGTH` | `1` | Longest arrow segment; shorter is smoother. |
| `RAID_ARROW_BALLISTIC_MAX_SEGMENTS` | `100` | Most segments per arrow; overrides the segment length. |
| `RAID_ARROW_AIR_HEIGHT` | `10.0` | Peak altitude of air raid arrows above the higher of source and target. |
| `RAID_ARROW_AIR_SLOPE_SOURCE_STEEPNESS` | `0.2` | Steepness of the climb at the source, from 0 to 1. |
| `RAID_ARROW_AIR_SLOPE_SOURCE_LENGTH` | `50.0` | Length of the climb at the source; higher means more time to reach peak altitude. |
| `RAID_ARROW_AIR_SLOPE_TARGET_STEEPNESS` | `0.2` | Same steepness at the target. |
| `RAID_ARROW_AIR_SLOPE_TARGET_LENGTH` | `0.0` | Same length at the target; 0 ends above the target. |
| `RAID_ARROW_AIR_MAX_SEGMENT_LENGTH` | `1` | Longest segment of an air raid arrow. |
| `RAID_ARROW_AIR_MAX_SEGMENTS` | `100` | Most segments per air raid arrow. |
| `RAID_ARROW_NAVAL_SUBDIVISIONS` | `20` | Subdivisions of the naval raid path spline; more is smoother but slower. |
| `RAID_ARROW_NAVAL_SHARP_TURN_SMOOTHNESS` | `0.10` | Smoothing applied to sharp turns on naval raid paths (0 is off). |
| `RAID_ARROW_NAVAL_USE_MIDPOINTS` | `true` | Whether naval raid paths use midpoints between provinces. |
| `RAID_ARROW_LAND_SUBDIVISIONS` | `20` | Subdivisions of the land raid path spline. |
| `RAID_ARROW_LAND_SHARP_TURN_SMOOTHNESS` | `0.10` | Smoothing applied to sharp turns on land raid paths (0 is off). |
| `RAID_ARROW_LAND_USE_MIDPOINTS` | `true` | Whether land raid paths use midpoints between provinces. |
| `RAID_UNIT_ENTITY_BASE_SCALE` | `2.0` | Base scale of the entity that shows raid progress; the raid script can modify it. |
| `RAID_UNIT_ENTITY_OFFSET` | `{ 0.0, 0.0, 0.0 }` | Offset of that entity from the arrow spline position. |
| `RAID_MAP_ICON_DRAW_DISTANCE_MIN` | `10.0` | Camera distance below which raid map icons are hidden. |
| `RAID_MAP_ICON_DRAW_DISTANCE_MAX` | `500.0` | Camera distance above which raid map icons are hidden in normal map modes. |
| `RAID_MAP_ICON_MAX_DRAW_DISTANCE_IN_RAID_MAP_MODE` | `1600.0` | Camera distance above which raid map icons are hidden in the raid map mode. |
| `RAID_TARGET_ZOOM_HEIGHT` | `200.0` | Camera height when zooming to a raid target. |
| `RAID_UNIT_ZOOM_HEIGHT` | `150.0` | Camera height when zooming to a raid unit. |
| `NAVAL_DOMINANCE_ICON_MAX_DRAW_DISTANCE` | `1000.0` | Camera distance at which naval dominance map icons are hidden. |
| `FACTION_PING_MAP_NONE_SELECT_COLOR` | `{ 0.1, 0.1, 0.3, 0.98 }` | Faction ping map colour when nothing is selected. |
| `FACTION_PING_MAP_AVAILABLE_COLOR` | `{0.3, 0.3, 0.3, 0.5 }` | Colour of an available region. |
| `FACTION_PING_MAP_UNAVAILABLE_COLOR` | `{ 0.1, 0.1, 0.3, 1.0 }` | Colour of an unavailable region. |
| `FACTION_PING_MAP_COLOR` | `{ 0.99, 0.99, 0.99, 0.05 }` | Colour of the selected region. |
| `FACTION_PING_MAP_ALREADY_ASSIGNED_COLOR` | `{ 0.5, 0.5, 0.75, 0.15 }` | Colour of a region already assigned to another theater. |
| `FACTION_PING_MAP_GRADIENT` | `150` | Distance gradient of the selected region. |

Values that differ from the wiki's table (5). The wiki page shows an older value. All rows: [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua`.

| Define | Page value | 1.19.3 value |
| --- | --- | --- |
| `DRAW_MAP_OBJECTS_CUTOFF` | `550.0` | `1100.0` |
| `BORDER_COLOR_CUSTOM_HIGHLIGHTS` | `{ 0.0, 0.61, 0.75, 1.0, 1.0, 0.06, 0.0, 1.0, 0.1, 0.6, 0.2, 1.0, 0.8, 0.3, 0.0, 1.0, 0.0, 0.4, 0.8, 1.0, 0....` | `{ 0.0, 0.61, 0.75, 1.0, 1.0, 0.06, 0.0, 1.0, 0.1, 0.6, 0.2, 1.0, 0.8, 0.3, 0.0, 1.0, 0.0, 0.4, 0.8, 1.0, 0....` |
| `NAVAL_MISSION_ICONS_DISTANCE_CUTOFF` | `900` | `1600` |
| `RAILWAY_CAMERA_CUTOFF` | `200.0` | `300.0` |
| `TRADE_ROUTE_SUPPLIES_TRANSFER_COLOR` | `{ 1.0, 1.0, 1.0, 0.75 }` | `{ 1.0, 1.0, 1.0, 0.35 }` |

**Kit correction** Defines in the wiki's table that 1.19.3 no longer has (6). The successor column names a define with the same value and a matching name, which is an inference. [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua` for the absence; [unverified] for the successor.

| Define | Page value | Likely successor |
| --- | --- | --- |
| `STRATEGIC_NAVY_COLOR_BAD` | `{ 0.8, 0, 0, 1 }` | none found |
| `STRATEGIC_NAVY_COLOR_GOOD` | `{ 0, 0.8, 0, 1 }` | none found |
| `STRATEGIC_NAVY_COLOR_AVERAGE` | `{ 0.8, 0.8, 0, 1 }` | none found |
| `STRATEGIC_NAVY_COLOR_BAD_WHILE_HIGHLIGHTING_HOLD` | `{ 0.7, 0.0, 0.4, 0.5 }` | none found |
| `STRATEGIC_NAVY_COLOR_GOOD_WHILE_HIGHLIGHTING_HOLD` | `{ 0, 0.6, 0.5, 1 }` | none found |
| `STRATEGIC_NAVY_COLOR_AVERAGE_WHILE_HIGHLIGHTING_HOLD` | `{ 0.5, 0.5, 0.6, 1 }` | none found |

## NInterface <a id="NInterface"></a>

**Kit addition** NInterface in 1.19.3: 86 defines in `common/defines/00_graphics.lua`; the wiki's table lists 83. [vanilla-confirmed 1.19.3] 1.19.4.1 adds six (92 in all); see [1.19.4.1 changes](#Changes_1_19_4_1). [vanilla-confirmed 1.19.4.1]

Defines the wiki's table lacks (3). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `AIR_WING_REINFORCEMENT_ICON_SCALE` | `0.9` | Scale of the reinforcement icon in the air wing toolbar strip. |
| `AIR_WING_NICHE_ICON_SCALE` | `0.8` | Scale of the niche icon in the air wing toolbar strip. |
| `FIXED_TOOLTIP_POSITION` | `{ -90, -12 }` | Offset from the bottom right of the screen for a fixed map tooltip (when enabled in settings). |

## NFrontend <a id="NFrontend"></a>

**Kit addition** NFrontend in 1.19.3: 30 defines in `common/defines/00_graphics.lua`; the wiki's table lists 28. [vanilla-confirmed 1.19.3]

Defines the wiki's table lacks (2). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `TIME_TO_SWAP_BACKGROUNDS` | `20` | Seconds before the main menu background changes. |
| `NEW_BACKGROUND_DURATION` | `4` | How many start-ups a new background is shown first: 1 selects it automatically, 0 never, higher values prioritise it that many times. |

## NSound <a id="NSound"></a>

**Kit addition** NSound in 1.19.3: 12 defines in `common/defines/00_graphics.lua`; the wiki's table lists 11. [vanilla-confirmed 1.19.3]

Defines the wiki's table lacks (1). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `ABILITY_GENERIC_SOUND_NAME` | `"ability_generic"` | Sound played in addition to an ability's own sound when the player activates an ability. |

## NCareerProfile <a id="NCareerProfile"></a>

**Kit addition** NCareerProfile in 1.19.3: 16 defines in `common/defines/01_career_profile.lua`; the wiki's table lists 17, 2 of them removed in 1.19.3. [vanilla-confirmed 1.19.3]

Defines the wiki's table lacks (1). All rows: [vanilla-confirmed 1.19.3] `common/defines/01_career_profile.lua`. The meaning is in my words, taken from the Lua comment; "no Lua comment" means it comes from the name only.

| Define | 1.19.3 value | Meaning |
| --- | --- | --- |
| `NEVERMINE_ME_MEDAL_MIN_RATIO` | `0.5` | Least effect mines must have on dominance for the naval region to count for the Nevermine Me medal. |

**Kit correction** Defines in the wiki's table that 1.19.3 no longer has (2). The successor column names a define with the same value and a matching name, which is an inference. [vanilla-confirmed 1.19.3] `common/defines/01_career_profile.lua` for the absence; [unverified] for the successor.

| Define | Page value | Likely successor |
| --- | --- | --- |
| `LORD_OF_THE_SEAS_MEDAL_MIN_SUPREMACY` | `0.75` | none found |
| `NEVERMINE_ME_MEDAL_MIN_SUPREMACY_EFFECT` | `0.5` | `NEVERMINE_ME_MEDAL_MIN_RATIO` |

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list_of_modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on_actions.md>) • [Data structures](<data_structures.md>) • [Flags](<data_structures.md#Flags>) • [Event targets](<data_structures.md#Event_targets>) • [Country tag aliases](<data_structures.md#Country_tag_aliases>) • [Variables](<data_structures.md#Variables>) • [Arrays](<data_structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement_modding.md>) • [AI](<ai_modding.md>) • [AI focuses](<ai_focuses.md>) • [Autonomous states](<autonomy_state_modding.md>) • [Balances of power](<balance_of_power_modding.md>) • [Bookmarks/Scenarios](<bookmark_modding.md>) • [Game rules](<bookmark_modding.md#Game_rules>) • [Buildings](<building_modding.md>) • [Characters and traits](<character_modding.md>) • [Cosmetic tags](<cosmetic_tag_modding.md>) • [Countries](<country_creation.md>) • [Divisions](<division_modding.md>) • [Decisions](<decision_modding.md>) • [Doctrines](<doctrine_modding.md>) • [Equipment](<equipment_modding.md>) • [Events](<event_modding.md>) • [Factions](<faction_modding.md>) • [Ideas](<idea_modding.md>) • [Ideologies](<ideology_modding.md>) • [Military industrial organizations](<military_industrial_organization_modding.md>) • [National focuses](<national_focus_modding.md>) • [Resources](<resources_modding.md>) • [Scripted GUI](<scripted_gui_modding.md>) • [Technologies and doctrines](<technology_modding.md>)
- **Map**: [Map](<map_modding.md>) • [States](<state_modding.md>) • [Supply areas](<supply_areas_modding.md>) • [Strategic regions](<strategic_region_modding.md>)
- **Graphical**: [Interface](<interface_modding.md>) • [Graphical assets](<graphical_asset_modding.md>) • [Entities](<entity_modding.md>) • [Posteffects](<posteffect_modding.md>) • [Particles](<particle_modding.md>) • [Fonts](<font_modding.md>)
- **Cosmetic**: [Portraits](<portrait_modding.md>) • [Namelists](<namelist_modding.md>) • [Music](<music_modding.md>) • [Sound](<sound_modding.md>)
- **Other**: [Console commands](<console_commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod_structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection_modding.md>) • [Defines additions](<defines_additions.md>) • [Game rule modding](<game_rule_modding.md>) • [Intelligence operation modding](<intelligence_operation_modding.md>) • [Map mode modding](<map_mode_modding.md>) • [Occupation and resistance modding](<occupation_and_resistance_modding.md>) • [Peace conference modding](<peace_conference_modding.md>) • [Raid modding](<raid_modding.md>) • [Script constant modding](<script_constant_modding.md>) • [Special project modding](<special_project_modding.md>)
