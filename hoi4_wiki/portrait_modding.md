# Portrait modding

Portraits are usually 156 by 210 pixels.

Portraits used by random country leaders and military leaders are specified in `/Hearts of Iron IV/portraits`. It is necessary to specify the files in `/Hearts of Iron IV/interface/_random_portraits.gfx`, otherwise the game will not display the images.

## Portraits

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

Sizes and sprites. The page's 156 by 210 is right for the large portrait: all 154 large sprites of `interface/_random_portraits.gfx` and 1,124 of the 1,126 sprites of `interface/_leader_portraits.gfx` whose image is in `gfx/leaders/` have exactly that size (the other two are 155 by 210 and 156 by 209). The small icon that goes with each is 65 by 67 pixels (154 of 154 in the random file). DDS headers of `gfx/leaders/` and `gfx/interface/ideas/`

Each name in a `portraits/*.txt` file is a sprite name. The sprite comes from a `spriteType` in an `interface/*.gfx` file: `_random_portraits.gfx` for the generic pools (a large sprite `GFX_Portrait_Europe_Generic_1` and a `..._small` partner; `GFX_Portrait_Africa_Generic_1_small` uses `gfx/interface/ideas/idea_africa_generic_1.dds`), `_leader_portraits.gfx` for named leaders, `_scientists_portraits.gfx` for scientists.

Vanilla `portraits/` files name 496 distinct sprites, and 26 of them (for example `GFX_portrait_Britain_generic_navy_4`) have no `spriteType` in any `.gfx` file. The base game ships with these dead entries, so a missing sprite is not fatal, but it can never show an image. The count is 496 with commented names and 494 without, and the 26 are the same either way, found in all 7 `portraits/` files (base game and DLC). The game only logs the problem, as far as a test went: the console command `debug_checkportraitssanity` ran in 1.19.4.1, replied "Finished analyzing character portraits - check result in error.log", wrote 90 new error.log lines for undefined portrait sprites and missing textures (for example "Couldn't find texture file: 'gfx/leaders/ETH/portrait_ETH_generic_male_3.dds'"), and the game ran a further day with no crash. No line named `GFX_portrait_Britain_generic_navy_4`, and the screenshot part with a British navy leader was not done.

The structure of the vanilla portrait files, which is wider than the page's outline.

| Part | Vanilla | Notes |
| --- | --- | --- |
| `default = { }` | 1 block, in `00_portraits.txt` | holds `male`, `female` and `operative`; its `army` and `navy` parts are commented out |
| `continent = { name = <c> ... }` | 7 in each file that has them | `<c>` is `europe`, `north_america`, `south_america`, `australia`, `africa`, `asia` or `middle_east` |
| `<TAG> = { }` | 43 in `00_portraits.txt` | all have `army` and `navy`, 9 also have `political` |
| `army`, `navy` | inside a continent or tag block | `male = { }` and `female = { }` lists |
| `political` | inside a continent or tag block | keys are the four ideology groups `communism`, `democratic`, `fascism`, `neutrality`, each with `male`/`female` |
| `operative` | `default` and the continent blocks of La Resistance | `male`/`female` lists; one tag block (`RAJ`) |
| `scientist` | continent blocks and 9 tag blocks of `998_scientist_portraits.txt` | `male`/`female` lists |

The `operative` and `scientist` categories are missing from the page. A continent block repeats in the DLC files (`01_anniversary_portraits.txt`, `02_tiger_portraits.txt`, `03_mtg_portraits.txt`), so a later file adds to a continent pool; that it appends rather than replaces is an inference. (unverified) for the append rule.

Vanilla tag blocks also exist for cosmetic tags (`RAJ_UK`, `MAL_UK`, `INS_HOL`, `SAF_COM`, `ETH_african_union`). `RAJ_UK`, `MAL_UK` and `INS_HOL` are defined in `common/countries/cosmetic.txt`. `SAF_COM` and `ETH_african_union` are not in `cosmetic.txt`, and `ETH_african_union` has its block in `dlc/dlc036_by_blood_alone/portraits/05_bba_portraits.txt`, not in `00_portraits.txt`. That the game looks up the active cosmetic tag is an inference and is untested. (unverified) `portraits/00_portraits.txt`

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

Shortened from vanilla.

Other ways a portrait is chosen. See [Character modding](character_modding.md) for the full character syntax.

- A character in `common/characters/*.txt` names its own sprites: `portraits = { civilian = { large = GFX_portrait_GER_adolf_hitler small = GFX_portrait_GER_eva_braun_small } }`. Over the 232 vanilla character files, `civilian` is used 1505 times, `army` 4554 and `navy` 42, each with `large` and/or `small`.
- The effects `set_portraits`, `set_country_leader_portrait` and `set_leader_portrait` change a portrait at runtime. `set_portraits` takes the character file syntax (`army = { small = ... }`, `civilian = { large = ... }`).
- `generate_scientist_character` takes an optional `portrait = GFX_...` (a random one by default) and `portrait_tag_override = TAG`, which makes the random pick use another country's pool. `create_operative_leader` documents the same `portrait_tag_override`, and a `gfx = GFX_...` key for a chosen sprite.
- A random pick is the case where no sprite is given. For it the game uses the pools above, matched on country (the tag block, else the capital's continent, else `default`), role (army, navy, political, operative, scientist) and gender. This is the page's account; the lookup order is not written in a game file and is untested. (unverified) `portraits/00_portraits.txt`
