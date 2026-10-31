# Portrait modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Portrait modding", revision 97039, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="97039" sources="portraits/ interface/_random_portraits.gfx interface/_leader_portraits.gfx interface/_scientists_portraits.gfx common/characters/ documentation/effects_documentation.md common/countries/cosmetic.txt" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `portraits/00_portraits.txt` and `portraits/998_scientist_portraits.txt`, the five DLC `portraits/` files, the three portrait sprite files in `interface/`, the DDS headers of the portrait images, the `portraits` blocks of 232 files in `common/characters/`, and the portrait effects in `documentation/effects_documentation.md`.
Kit blocks added: sizes and sprite requirements, the full group and category structure (including the `operative` and `scientist` categories the page lacks), a vanilla tag block, how characters and effects pick a portrait.
Gaps left: which category the game picks for each leader type and how it chooses among several matching groups is not written in any game file, so the page's rules for that stay as the wiki states them.
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
**Kit note** Sizes and sprites. The page's 156 by 210 is right for the large portrait: all 154 large sprites of `interface/_random_portraits.gfx` and 496 of 498 large sprites checked in `interface/_leader_portraits.gfx` have exactly that size (the other two are 155 by 210 and 156 by 209). The small icon that goes with each is 65 by 67 pixels (154 of 154 in the random file). [vanilla-confirmed 1.19.3] DDS headers of `gfx/leaders/` and `gfx/interface/ideas/`

Each name in a `portraits/*.txt` file is a sprite name. The sprite comes from a `spriteType` in an `interface/*.gfx` file: `_random_portraits.gfx` for the generic pools (a large sprite `GFX_Portrait_Europe_Generic_1` and a `..._small` partner; `GFX_Portrait_Africa_Generic_1_small` uses `gfx/interface/ideas/idea_africa_generic_1.dds`), `_leader_portraits.gfx` for named leaders, `_scientists_portraits.gfx` for scientists. [vanilla-confirmed 1.19.3] `interface/_random_portraits.gfx`

Vanilla `portraits/` files name 496 distinct sprites, and 26 of them (for example `GFX_portrait_Britain_generic_navy_4`) have no `spriteType` in any `.gfx` file. The base game ships with these dead entries, so a missing sprite is not fatal, but it can never show an image. [vanilla-confirmed 1.19.3] `portraits/00_portraits.txt`, `interface/`. That the game only logs the problem is a guess. [unverified] `portraits/00_portraits.txt`
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

The `operative` and `scientist` categories are missing from the page. A continent block repeats in the DLC files (`01_anniversary_portraits.txt`, `02_tiger_portraits.txt`, `03_mtg_portraits.txt`), so a later file adds to a continent pool; that it appends rather than replaces is an inference. [vanilla-confirmed 1.19.3] `dlc/dlc021_anniversary_pack/portraits/`, `integrated_dlc/dlc022_waking_the_tiger/portraits/`. [unverified] for the append rule.

Vanilla tag blocks also exist for cosmetic tags (`RAJ_UK`, `MAL_UK`, `INS_HOL`, `SAF_COM`, `ETH_african_union`). `RAJ_UK`, `MAL_UK` and `INS_HOL` are defined in `common/countries/cosmetic.txt`. [vanilla-confirmed 1.19.3] `portraits/00_portraits.txt`, `common/countries/cosmetic.txt`. That the game looks up the active cosmetic tag is an inference. [unverified] `portraits/00_portraits.txt`

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
**Kit addition** Other ways a portrait is chosen. See [Character modding](<character-modding.md>) for the full character syntax.

- A character in `common/characters/*.txt` names its own sprites: `portraits = { civilian = { large = GFX_portrait_GER_adolf_hitler small = GFX_portrait_GER_eva_braun_small } }`. Over the 232 vanilla character files, `civilian` is used 1217 times, `army` 3893 and `navy` 38, each with `large` and/or `small`. [vanilla-confirmed 1.19.3] `common/characters/GER.txt`, `common/characters/`
- The effects `set_portraits`, `set_country_leader_portrait` and `set_leader_portrait` change a portrait at runtime. `set_portraits` takes the character file syntax (`army = { small = ... }`, `civilian = { large = ... }`). [docs] `documentation/effects_documentation.md`
- `generate_scientist_character` takes an optional `portrait = GFX_...` (a random one by default) and `portrait_tag_override = TAG`, which makes the random pick use another country's pool. `create_operative_leader` documents the same `portrait_tag_override`, and a `gfx = GFX_...` key for a chosen sprite. [docs] `documentation/effects_documentation.md`
- A random pick is the case where no sprite is given. For it the game uses the pools above, matched on country (the tag block, else the capital's continent, else `default`), role (army, navy, political, operative, scientist) and gender. This is the page's account; the lookup order is not written in a game file. [unverified] `portraits/00_portraits.txt`
<!-- kit:end id="portrait-references" -->

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list-of-modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on-actions.md>) • [Data structures](<data-structures.md>) • [Flags](<data-structures.md#Flags>) • [Event targets](<data-structures.md#Event_targets>) • [Country tag aliases](<data-structures.md#Country_tag_aliases>) • [Variables](<data-structures.md#Variables>) • [Arrays](<data-structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement-modding.md>) • [AI](<ai-modding.md>) • [AI focuses](<ai-focuses.md>) • [Autonomous states](<autonomy-state-modding.md>) • [Balances of power](<balance-of-power-modding.md>) • [Bookmarks/Scenarios](<bookmark-modding.md>) • [Game rules](<bookmark-modding.md#Game_rules>) • [Buildings](<building-modding.md>) • [Characters and traits](<character-modding.md>) • [Cosmetic tags](<cosmetic-tag-modding.md>) • [Countries](<country-creation.md>) • [Divisions](<division-modding.md>) • [Decisions](<decision-modding.md>) • [Doctrines](<doctrine-modding.md>) • [Equipment](<equipment-modding.md>) • [Events](<event-modding.md>) • [Factions](<faction-modding.md>) • [Ideas](<idea-modding.md>) • [Ideologies](<ideology-modding.md>) • [Military industrial organizations](<military-industrial-organization-modding.md>) • [National focuses](<national-focus-modding.md>) • [Resources](<resources-modding.md>) • [Scripted GUI](<scripted-gui-modding.md>) • [Technologies and doctrines](<technology-modding.md>) • [Units](<unit-modding.md>)
- **Map**: [Map](<map-modding.md>) • [States](<state-modding.md>) • [Supply areas](<supply-areas-modding.md>) • [Strategic regions](<strategic-region-modding.md>)
- **Graphical**: [Interface](<interface-modding.md>) • [Graphical assets](<graphical-asset-modding.md>) • [Entities](<entity-modding.md>) • [Posteffects](<posteffect-modding.md>) • [Particles](<particle-modding.md>) • [Fonts](<font-modding.md>)
- **Cosmetic**: [Namelists](<namelist-modding.md>) • [Music](<music-modding.md>) • [Sound](<sound-modding.md>)
- **Other**: [Console commands](<console-commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod-structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection-modding.md>) • [Game rule modding](<game-rule-modding.md>) • [Intelligence operation modding](<intelligence-operation-modding.md>) • [Map mode modding](<map-mode-modding.md>) • [Occupation and resistance modding](<occupation-and-resistance-modding.md>) • [Peace conference modding](<peace-conference-modding.md>) • [Raid modding](<raid-modding.md>) • [Script constant modding](<script-constant-modding.md>) • [Special project modding](<special-project-modding.md>)
