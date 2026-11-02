# Portrait modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Portrait modding", revision 97039, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.4.1" checked="2026-11-01" revision="97039" sources="portraits/ interface/_random_portraits.gfx interface/_leader_portraits.gfx interface/_scientists_portraits.gfx common/characters/ documentation/effects_documentation.md common/countries/cosmetic.txt" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `portraits/00_portraits.txt` and `portraits/998_scientist_portraits.txt`, the five DLC `portraits/` files, the three portrait sprite files in `interface/`, the DDS headers of the portrait images, the `portraits` blocks of 232 files in `common/characters/`, and the portrait effects in `documentation/effects_documentation.md`.
Kit blocks added: sizes and sprite requirements, the full group and category structure (including the `operative` and `scientist` categories the page lacks), a vanilla tag block, how characters and effects pick a portrait.
Gaps left: which category the game picks for each leader type and how it chooses among several matching groups is not written in any game file, so the page's rules for that stay as the wiki states them.
**1.19.4.1 re-check (2026-11-01).** 4 tagged statements depended on files the update changed (`interface/_leader_portraits.gfx`, `gfx/leaders/`, `common/characters/` and `common/countries/cosmetic.txt`), and all of them were re-measured. The character files now use `civilian` 1,505 times, `army` 4,554 and `navy` 42 (earlier 1,217, 3,893 and 38), and the leader portrait size check now covers every sprite whose image is in `gfx/leaders/` (1,124 of 1,126 are 156 by 210). The 496 sprites named in `portraits/` and the 26 without a `spriteType` are unchanged. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

## Table of contents

- [Portraits](#Portraits)

---

Portraits are usually 156 by 210 pixels.

Portraits used by random country leaders and military leaders are specified in `/Hearts of Iron IV/portraits`. It is necessary to specify the files in `/Hearts of Iron IV/interface/_random_portraits.gfx`, otherwise the game will not display the images.

## Portraits <a id="Portraits"></a>

Portraits are used to assign a pool of images to specific groups of countries, or a specific country, that will then be used when the player generates a military leader or through an effect their country leader or military leader is replaced.

It follows this format:

```text
default = {
    # ...
}
continent = {
    name = <continent>
    # ...
}
<tag> = {
    # ...
}
```

**default** is the fallback portrait used when no other definition matches the current scope.

**continent** defines the portraits per continent, meaning they apply to any nation with its capital in the specified continent.

**tag** defines the portraits for the specified tag, overriding the **continent** definition if it also matches one.

The actual portrait definitions are as follows:

```text
male = {
    <path>
}
female = {
    <path>
}

army = {
    male = {
        <path>
    }
    female = {
        <path>
    }
}
navy = {
    male = {
        <path>
    }
    female = {
        <path>
    }
}
political = {
    <ideology> = {
        male = {
            <path>
        }
        female = {
            <path>
        }
    }
}
```

Multiple paths can be used to add a pool of portraits to each definition.

The top **male** and **female** paths may be used for any type of leader.

The **army** paths are used for Field Marshals and Corps Commanders.

The **navy** paths are used for Naval Commanders.

The **political** paths are used for country leaders of the specified ideologies.

<!-- kit:begin id="portrait-sizes-sprites" at="section:Portraits" -->
**Kit note** Sizes and sprites. The page's 156 by 210 is right for the large portrait: all 154 large sprites of `interface/_random_portraits.gfx` and 1,124 of the 1,126 sprites of `interface/_leader_portraits.gfx` whose image is in `gfx/leaders/` have exactly that size (the other two are 155 by 210 and 156 by 209). The small icon that goes with each is 65 by 67 pixels (154 of 154 in the random file). [vanilla-confirmed 1.19.4.1] DDS headers of `gfx/leaders/` and `gfx/interface/ideas/`

Each name in a `portraits/*.txt` file is a sprite name. The sprite comes from a `spriteType` in an `interface/*.gfx` file: `_random_portraits.gfx` for the generic pools (a large sprite `GFX_Portrait_Europe_Generic_1` and a `..._small` partner; `GFX_Portrait_Africa_Generic_1_small` uses `gfx/interface/ideas/idea_africa_generic_1.dds`), `_leader_portraits.gfx` for named leaders, `_scientists_portraits.gfx` for scientists. [vanilla-confirmed 1.19.3] `interface/_random_portraits.gfx`

Vanilla `portraits/` files name 496 distinct sprites, and 26 of them (for example `GFX_portrait_Britain_generic_navy_4`) have no `spriteType` in any `.gfx` file. The base game ships with these dead entries, so a missing sprite is not fatal, but it can never show an image. [vanilla-confirmed 1.19.4.1] `portraits/00_portraits.txt`, `interface/`. The count is 496 with commented names and 494 without, and the 26 are the same either way, found in all 7 `portraits/` files (base game and DLC). The game only logs the problem, as far as a test went: the console command `debug_checkportraitssanity` ran in 1.19.4.1, replied "Finished analyzing character portraits - check result in error.log", wrote 90 new error.log lines for undefined portrait sprites and missing textures (for example "Couldn't find texture file: 'gfx/leaders/ETH/portrait_ETH_generic_male_3.dds'"), and the game ran a further day with no crash. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console and error.log read. No line named `GFX_portrait_Britain_generic_navy_4`, and the screenshot part with a British navy leader was not done.
<!-- kit:end id="portrait-sizes-sprites" -->

<!-- kit:begin id="portrait-structure" at="section:Portraits" -->
**Kit addition** The structure of the vanilla portrait files, which is wider than the page's outline.

| Part | Vanilla | Notes |
| --- | --- | --- |
| `default = { }` | 1 block, in `00_portraits.txt` | holds `male`, `female` and `operative`; its `army` and `navy` parts are commented out |
| `continent = { name = <c> ... }` | 7 in each file that has them | `<c>` is `europe`, `north_america`, `south_america`, `australia`, `africa`, `asia` or `middle_east` |
| `<TAG> = { }` | 43 in `00_portraits.txt` | all have `army` and `navy`, 9 also have `political` |
| `army`, `navy` | inside a continent or tag block | `male = { }` and `female = { }` lists |
| `political` | inside a continent or tag block | keys are the four ideology groups `communism`, `democratic`, `fascism`, `neutrality`, each with `male`/`female` |
| `operative` | `default` and the continent blocks of La Resistance | `male`/`female` lists; one tag block (`RAJ`) |
| `scientist` | continent blocks and 9 tag blocks of `998_scientist_portraits.txt` | `male`/`female` lists |

All rows: [vanilla-confirmed 1.19.3] `portraits/00_portraits.txt`, `portraits/998_scientist_portraits.txt`, `dlc/dlc028_la_resistance/portraits/027_lar_portraits.txt`.

The `operative` and `scientist` categories are missing from the page. A continent block repeats in the DLC files (`01_anniversary_portraits.txt`, `02_tiger_portraits.txt`, `03_mtg_portraits.txt`), so a later file adds to a continent pool; that it appends rather than replaces is an inference. [vanilla-confirmed 1.19.4.1] `dlc/dlc021_anniversary_pack/portraits/`, `integrated_dlc/dlc022_waking_the_tiger/portraits/`, `integrated_dlc/dlc023_man_the_guns/portraits/`: all 7 continents repeat in each of the three files. [unverified] for the append rule.

Vanilla tag blocks also exist for cosmetic tags (`RAJ_UK`, `MAL_UK`, `INS_HOL`, `SAF_COM`, `ETH_african_union`). `RAJ_UK`, `MAL_UK` and `INS_HOL` are defined in `common/countries/cosmetic.txt`. [vanilla-confirmed 1.19.4.1] `portraits/00_portraits.txt`, `common/countries/cosmetic.txt`. `SAF_COM` and `ETH_african_union` are not in `cosmetic.txt`, and `ETH_african_union` has its block in `dlc/dlc036_by_blood_alone/portraits/05_bba_portraits.txt`, not in `00_portraits.txt`. That the game looks up the active cosmetic tag is an inference and is untested. [unverified] `portraits/00_portraits.txt`

```text
FIN = {
	army = {
		male = {
			"GFX_portrait_Finland_Generic_land_1"
			"GFX_portrait_Finland_Generic_land_2"
		}
	}
	navy = {
		male = { "GFX_portrait_Finland_Generic_navy_1" }
	}
	political = {
		democratic = { male = { "GFX_Portrait_Europe_Generic_2" } }
		fascism = { male = { "GFX_Portrait_Europe_Generic_3" } }
	}
}
```

Shortened from vanilla. [vanilla-confirmed 1.19.3] `portraits/00_portraits.txt`
<!-- kit:end id="portrait-structure" -->

<!-- kit:begin id="portrait-references" at="section:Portraits" -->
**Kit addition** Other ways a portrait is chosen. See [Character modding](<character_modding.md>) for the full character syntax.

- A character in `common/characters/*.txt` names its own sprites: `portraits = { civilian = { large = GFX_portrait_GER_adolf_hitler small = GFX_portrait_GER_eva_braun_small } }`. Over the 232 vanilla character files, `civilian` is used 1505 times, `army` 4554 and `navy` 42, each with `large` and/or `small`. [vanilla-confirmed 1.19.4.1] `common/characters/GER.txt`, `common/characters/`
- The effects `set_portraits`, `set_country_leader_portrait` and `set_leader_portrait` change a portrait at runtime. `set_portraits` takes the character file syntax (`army = { small = ... }`, `civilian = { large = ... }`). [docs] `documentation/effects_documentation.md`
- `generate_scientist_character` takes an optional `portrait = GFX_...` (a random one by default) and `portrait_tag_override = TAG`, which makes the random pick use another country's pool. `create_operative_leader` documents the same `portrait_tag_override`, and a `gfx = GFX_...` key for a chosen sprite. [docs] `documentation/effects_documentation.md`
- A random pick is the case where no sprite is given. For it the game uses the pools above, matched on country (the tag block, else the capital's continent, else `default`), role (army, navy, political, operative, scientist) and gender. This is the page's account; the lookup order is not written in a game file and is untested. [unverified] `portraits/00_portraits.txt`
<!-- kit:end id="portrait-references" -->

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list_of_modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on_actions.md>) • [Data structures](<data_structures.md>) • [Flags](<data_structures.md#Flags>) • [Event targets](<data_structures.md#Event_targets>) • [Country tag aliases](<data_structures.md#Country_tag_aliases>) • [Variables](<data_structures.md#Variables>) • [Arrays](<data_structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement_modding.md>) • [AI](<ai_modding.md>) • [AI focuses](<ai_focuses.md>) • [Autonomous states](<autonomy_state_modding.md>) • [Balances of power](<balance_of_power_modding.md>) • [Bookmarks/Scenarios](<bookmark_modding.md>) • [Game rules](<bookmark_modding.md#Game_rules>) • [Buildings](<building_modding.md>) • [Characters and traits](<character_modding.md>) • [Cosmetic tags](<cosmetic_tag_modding.md>) • [Countries](<country_creation.md>) • [Divisions](<division_modding.md>) • [Decisions](<decision_modding.md>) • [Doctrines](<doctrine_modding.md>) • [Equipment](<equipment_modding.md>) • [Events](<event_modding.md>) • [Factions](<faction_modding.md>) • [Ideas](<idea_modding.md>) • [Ideologies](<ideology_modding.md>) • [Military industrial organizations](<military_industrial_organization_modding.md>) • [National focuses](<national_focus_modding.md>) • [Resources](<resources_modding.md>) • [Scripted GUI](<scripted_gui_modding.md>) • [Technologies and doctrines](<technology_modding.md>) • [Units](<unit_modding.md>)
- **Map**: [Map](<map_modding.md>) • [States](<state_modding.md>) • [Supply areas](<supply_areas_modding.md>) • [Strategic regions](<strategic_region_modding.md>)
- **Graphical**: [Interface](<interface_modding.md>) • [Graphical assets](<graphical_asset_modding.md>) • [Entities](<entity_modding.md>) • [Posteffects](<posteffect_modding.md>) • [Particles](<particle_modding.md>) • [Fonts](<font_modding.md>)
- **Cosmetic**: [Namelists](<namelist_modding.md>) • [Music](<music_modding.md>) • [Sound](<sound_modding.md>)
- **Other**: [Console commands](<console_commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod_structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection_modding.md>) • [Defines additions](<defines_additions.md>) • [Game rule modding](<game_rule_modding.md>) • [Intelligence operation modding](<intelligence_operation_modding.md>) • [Map mode modding](<map_mode_modding.md>) • [Occupation and resistance modding](<occupation_and_resistance_modding.md>) • [Peace conference modding](<peace_conference_modding.md>) • [Raid modding](<raid_modding.md>) • [Script constant modding](<script_constant_modding.md>) • [Special project modding](<special_project_modding.md>)
