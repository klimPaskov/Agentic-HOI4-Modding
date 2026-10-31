# Graphical asset modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Graphical asset modding", revision 73705, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="73705" sources="interface/ gfx/entities/ gfx/particles/WW_particles.gfx gfx/models/ gfx/fonts/ hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: every `.gfx` file under `interface/`, `gfx/`, `dlc/*/` and `integrated_dlc/*/` (214 files with `spriteTypes`, 118 with `objectTypes`, 7 with `bitmapfonts`), `interface/core.gfx`, `interface/arrows.gfx`, `gfx/entities/*.gfx`, `gfx/particles/WW_particles.gfx`, the `.fnt` and `.dds` files in `gfx/fonts/`, and token strings in `hoi4.exe`.
Kit blocks added: sprite kind census, key corrections for `spriteType` and its animation block, notes for frame animated, progress bar and cornered tile sprites, a correction for the `maskedShieldType` example, the filled "Object Types" and "Font Types" sections.
Gaps left: no game file explains `steps`, `looping`, `play_on_show`, `tilingCenter`, `dx_offset` or the `gfx/FX/*.lua` effect files, so their meaning stays as the wiki states it.
<!-- kit:end id="review" -->

## Table of contents

- [Sprite Types](#Sprite_Types)
  - [spriteType](#spriteType)
- [frameAnimatedSpriteType](#frameAnimatedSpriteType)
- [progressbartype](#progressbartype)
- [corneredTileSpriteType](#corneredTileSpriteType)
- [maskedShieldType](#maskedShieldType)
- [Object Types](#Object_Types)
- [animatedmaptext](#animatedmaptext)
- [Font Types](#Font_Types)
- [textcolors](#textcolors)
- [bitmapfont](#bitmapfont)
- [bitmapfont_override](#bitmapfont_override)

---

Graphical assets are image files that have been defined in a `.gfx` file. This binds the image to a script name that is then referred to in the `.gui` interface files.

Graphical asset files can be found in `/Hearts of Iron IV/interface/*.gfx`.

Note that for many assets, such as technology and equipment asset definitions, the image can be specified for a specific tag, i.e. `GFX_ENG_<name>`, which only displays the asset for the specified tag. This will override the base asset of the same name. This also applies to graphical culture, i.e. `GFX_african_<name>`.

## Sprite Types <a id="Sprite_Types"></a>

<!-- kit:begin id="gfx-sprite-census" at="section:Sprite_Types" -->
**Kit addition** Sprite block kinds in 1.19.3, counted over the `.gfx` files of `interface/` (including its subfolders), `gfx/`, `dlc/*/` and `integrated_dlc/*/`. Keywords and keys are not case sensitive in practice: vanilla writes `spriteType` 18542 times and `SpriteType` 11373 times, and both `texturefile` and `textureFile`. [vanilla-confirmed 1.19.3] `interface/*.gfx`

| Keyword | Uses | What it is |
| --- | --- | --- |
| `spriteType` / `SpriteType` | 29915 | plain image, described below |
| `frameAnimatedSpriteType` | 160 | frame sheet played over time |
| `corneredTileSpriteType` | 154 | stretchable image with fixed borders |
| `progressbartype` | 106 | progress bar from two textures |
| `textSpriteType` | 69 | same keys as `spriteType`, used for button sprites such as `GFX_error_log_button` |
| `maskedShieldType` | 13 | flag shield with a mask |
| `pieChartType` | 5 | keys `name`, `size` (one number) and optionally `colors = { rgb = { 0 0.7 0 } ... }` |
| `circularProgressBarType` | 4 | keys `name`, `textureFile1`, `textureFile2`, `size`, `rotation`, `amount` |
| `LineChartType` | 3 | keys `name`, `size = { x = 380 y = 120 }`, `linewidth` |

All rows: [vanilla-confirmed 1.19.3] `interface/countrypoliticsview.gfx`, `interface/mapicons.gfx`, `interface/countryintelledger.gfx`, `interface/countrydiplomacyview.gfx`.

`progressBarType` with a capital B appears in 4 blocks of `interface/powerbalanceview.gfx` with the same keys as `progressbartype` minus the colours; it is probably the same keyword. [unverified] `interface/powerbalanceview.gfx`

Sprite files are not only `interface/*.gfx`. Vanilla also uses `interface/building_roster/`, `interface/buildings/`, `interface/career_profile/`, `interface/doctrines/`, `interface/factions/`, `interface/military_industrial_organization/`, `interface/special_projects/` and the `interface/` folder of every DLC. [vanilla-confirmed 1.19.3] `interface/`
<!-- kit:end id="gfx-sprite-census" -->

### spriteType <a id="spriteType"></a>

A **spriteType** and **textSpriteType** asset entry follows this format:

```text
spriteTypes = {
    spriteType = {
        name = "GFX_<name>"
        texturefile = <path>
        noOfFrames = <int>
        effectFile = <path>

        allwaystransparent = <bool>
        legacy_lazy_load = <bool>
        transparencecheck = <bool>

        animation = {
            animationmaskfile = <path>
            animationtexturefile = <path>
            animationrotation = <float>
            animationlooping = <bool>
            animationtime = <float>
            animationdelay = <float>
            animationblendmode = <mode>
            animationtype = <type>
            animationrotationoffset = {
                x = <float>
                y = <float>
            }
            animationtexturescale = {
                x = <float>
                y = <float>
            }
            animationframes = {
                <int> <int> # etc
            }
        }
    }
}
```

**name** is the name you have given to the asset. This may be prefixed with various other segments, such as *idea* for idea images, etc.

**texturefile** is the path to the image, based of the `/Hearts of Iron IV/`, meaning you only include the folders within this folder, not the full filepath.

**noOfFrames** is used for images with multiple *frames* within, for example `GFX_unit_level` has five images within for each of the unit level images, and so would have `noOfFrames = 5` set within its asset definition.

**effectFile** is used to define an effect state to apply to the image, i.e. the button press effect on a button image. Effects are found in `/Hearts of Iron IV/gfx/FX/*.lua`. Multiple can be defined to add multiple effects.

**allwaystransparent** defines whether or not an image can be clicked on and interacted with. If yes, the image will have no tooltip and can not be clicked on when used in game.

**legacy_lazy_load** defines whether the image is lazy loaded.

**transparencecheck** defines whether the image is bound by its alpha channel with regards to player clicks. Otherwise the bounding box is the image dimensions.

**animation** scope is used to add animation to an image. It uses the following attributes:

- **animationmaskfile** controls the mask image for the animation.
- **animationtexturefile** controls the color image used for the animation.
- **animationrotation** controls the rotation of the animation image. By default it is -90 clockwise.
- **animationlooping** controls whether the animation loops.
- **animationtime** controls the duration of the animation. It is measured in seconds.
- **animationdelay** controls the delay between animation loops. It is measured in seconds.
- **animationblendmode** controls the blend mode for the animation image. Can be *add*, *multiply* or *overlay*.
- **animationtype** controls the type of animation. Can be *scrolling*, *rotating* or *pulsing*.
- **animationrotationoffset** controls the *x* and *y* offsets for the rotation.
- **animationtexturescale** controls the scale of the animation image.
- **animationframes** sets the number of frames within the animation image.

Be wary that the maximum file size for a sprite .dds files is around 16MB

<!-- kit:begin id="gfx-sprite-key-corrections" at="section:spriteType" -->
**Kit correction** Notes on the keys above, checked against all vanilla `spriteTypes` blocks.

- The page spells the transparency key `allwaystransparent`. Vanilla writes `alwaystransparent` (also `alwaysTransparent`) about 3254 times in `.gfx` and `.gui` files, and the extra-`l` spelling only 8 times in `interface/popupwindow.gfx` and `interface/traittree.gfx`. Write `alwaystransparent = yes`. [vanilla-confirmed 1.19.3] `interface/*.gfx`, `interface/*.gui`
- Both spellings exist as token strings in `hoi4.exe`, so the typo is probably also accepted. [unverified] `hoi4.exe`
- `legacy_lazy_load` is only ever written as `no` in vanilla (4864 uses, no `yes`). [vanilla-confirmed 1.19.3] `interface/*.gfx`
- Keys vanilla puts on `spriteType` that the page lacks: `clicksound` (23 sprites, the name of a sound effect such as `click_chat`, see [Sound modding](<Sound modding - Hearts of Iron 4 Wiki.md>)), `loadType` (`"INGAME"` 77 times and `"FRONTEND"` 6 times over all sprite kinds), `generate_mip_maps = yes` (4), `framedirectiony = yes` (3), `dx_offset = { x = -0.5 y = -0.5 }` (7) and `masking_texture` (1). [vanilla-confirmed 1.19.3] `interface/chat.gfx`, `interface/core.gfx`, `interface/*.gfx`
- No game file states what `loadType`, `generate_mip_maps`, `framedirectiony` or `dx_offset` do. [unverified] `interface/*.gfx`
- Animation block: vanilla has 6372 `animation` blocks, and each sets the ten keys `animationmaskfile`, `animationtexturefile`, `animationrotation`, `animationlooping`, `animationtime`, `animationdelay`, `animationblendmode`, `animationtype`, `animationrotationoffset` and `animationtexturescale`. [vanilla-confirmed 1.19.3] `interface/abilitylist.gfx`
- `animationblendmode` values in vanilla: `"add"` 6365 times, `"normal"` 4 times, `"overlay"` 3 times. `"multiply"`, which the page lists, is never used. [vanilla-confirmed 1.19.3] `interface/*.gfx`
- `animationtype` values in vanilla: `"scrolling"` 6318 times, `"rotating"` 25, `"rotating_ccw"` 24, `"pulsing"` 5. `rotating_ccw` is missing from the page. [vanilla-confirmed 1.19.3] `interface/*.gfx`
- `animationframes` appears in only 3 blocks and holds a list of frame numbers (`animationframes = { 1 2 3 }`), not a frame count as the page says. [vanilla-confirmed 1.19.3] `interface/crypto.gfx`, `interface/social_view.gfx`
- `effectFile` is written once per sprite in vanilla (no sprite has two). The page says several can be given; that is not shown by any game file. [unverified] `interface/*.gfx`
<!-- kit:end id="gfx-sprite-key-corrections" -->

## frameAnimatedSpriteType <a id="frameAnimatedSpriteType"></a>

A **frameAnimatedSpriteType** asset entry follows this format:

```text
spriteTypes = {
    frameAnimatedSpriteType = {
        name = "GFX_<name>"
        texturefile = "<path>"
        noOfFrames = <int>
        effectFile = "<path>"

        animation_rate_fps = <int>
        looping = <bool>
        play_on_show = <bool>
        pause_on_loop = <float>

        allwaystransparent = <bool>
    }
}
```

**name** is the name you have given to the asset. This may be prefixed with various other segments, such as *idea* for idea images, etc.

**texturefile** is the path to the image, based of the `/Hearts of Iron IV/`, meaning you only include the folders within this folder, not the full filepath.

**noOfFrames** is used for images with multiple *frames* within, for example `GFX_unit_level` has five images within for each of the unit level images, and so would have `noOfFrames = 5` set within its asset definition.

**effectFile** is used to define an effect state to apply to the image, i.e. the button press effect on a button image. Effects are found in `/Hearts of Iron IV/gfx/FX/*.lua`. Multiple can be defined to add multiple effects.

**animation_rate_fps** is the rate at which the animation plays.

**looping** defines whether the animation loops.

**play_on_show** defines whether the animations starts playing when visible.

**pause_on_loop** defines the length of time to pause for after an animation loop.

**allwaystransparent** defines whether the image is bound by its alpha channel with regards to player clicks. Otherwise the bounding box is the image dimensions.

<!-- kit:begin id="gfx-frameanimated-notes" at="section:frameAnimatedSpriteType" -->
**Kit note** All 160 vanilla `frameAnimatedSpriteType` blocks set `name`, `noOfFrames`, `animation_rate_fps` and `looping`. `play_on_show` is set in 153 and `pause_on_loop` in 156. `animation_rate_fps` is not an integer: vanilla uses 15 (41 blocks), 1 (38), 1.5 (26), 12 (18), 24 (10), 2 (9), 7 (5) and 0.5 (3). [vanilla-confirmed 1.19.3] `interface/*.gfx`

```text
frameAnimatedSpriteType = {
	name = "GFX_green_alert_glow"
	texturefile = "gfx/interface/green_alert_glow.dds"
	noOfFrames = 2
	animation_rate_fps = 0.5
	looping = yes
	play_on_show = yes
	pause_on_loop = 0.0
	alwaystransparent = yes
	effectFile = "gfx/FX/buttonstate_blendframes.lua"
}
```

Example block. [vanilla-confirmed 1.19.3] `interface/alerts.gfx`
<!-- kit:end id="gfx-frameanimated-notes" -->

## progressbartype <a id="progressbartype"></a>

A **progressbartype** asset entry is used for progress bars. It follows this format:

```text
spriteTypes = {
    progressbartype = {
        name = "GFX_<name>"
        textureFile1 = "<path>"
        textureFile2 = "<path>"
        color = { <r> <g> <b> [<a>] }
        colortwo = { <r> <g> <b> [<a>] }
        size = {
            x = <int>
            y = <int>
        }
        effectFile = <path>
        horizontal = <bool>
        steps = <int>
    }
}
```

**name** is the name you have given to the asset. This may be prefixed with various other segments, such as *idea* for idea images, etc.
**textureFile1** is the image to use for the progress bar.
**textureFile2** is the image to use for the background of the progress bar.
**color** defines the unprogressed color of the bar. It is decimal RGBA. Alpha is optional.
**colortwo** defines the progressed color of the bar. It is decimal RGBA. Alpha is optional.
**size** defines the size of the progress bar section in height and width.
**effectFile** is used to define an effect state to apply to the image, i.e. the button press effect on a button image. Effects are found in `/Hearts of Iron IV/gfx/FX/*.lua`. Multiple can be defined to add multiple effects.
**horizontal** defines whether the progress bar is horizontal or not. By default a bar is horizontal.
**steps** defines the precision of the progressbar or into how many frames it's split into. Defaults to 100 if unset.

<!-- kit:begin id="gfx-progressbar-notes" at="section:progressbartype" -->
**Kit note** All 106 vanilla `progressbartype` blocks set `name`, `textureFile1`, `textureFile2`, `size` and `effectFile`. `color` and `colortwo` come as a pair in 83 blocks, `horizontal` is set in 38 and `steps` in 16 (values 3, 5, 408, 500, 10000 and 1000000). Colours are decimal 0 to 1. The page's default of 100 for `steps` is not stated in any game file. [vanilla-confirmed 1.19.3] `interface/countryproductionlineview.gfx`, `interface/*.gfx`

```text
progressbartype = {
	name = "GFX_efficiency_progressbar"
	color = { 0.0 0.5 0.0 }
	colortwo = { 1.0 0.0 0.0 }
	textureFile1 = "gfx\\interface\\efficiency_progressbar.dds"
	textureFile2 = "gfx\\interface\\efficiency_progressbar_bg_transparent.dds"
	size = { x = 93 y = 9 }
	effectFile = "gfx/FX/progress_startend.lua"
}
```

Example block. Vanilla paths mix `/`, `//` and `\\` separators. [vanilla-confirmed 1.19.3] `interface/countryproductionlineview.gfx`
<!-- kit:end id="gfx-progressbar-notes" -->

## corneredTileSpriteType <a id="corneredTileSpriteType"></a>

A **corneredTileSpriteType** asset entry is used for tiling textures that tile to fill the size of the interface element they are used in. It follows this format:

```text
spriteTypes = {
    corneredTileSpriteType = {
        name = "GFX_<name>"
        texturefile = "<path>"
        noOfFrames = <int>
        size = {
            x = <int>
            y = <int>
        }
        borderSize = {
            x = <int>
            y = <int>
        }
        effectFile = <path>

        allwaystransparent = <bool>
        tilingCenter = <bool>

        looping = <bool>
        animation_rate_spf = <int>
    }
}
```

**name** is the name you have given to the asset. This may be prefixed with various other segments, such as *idea* for idea images, etc.

**texturefile** is the path to the image, based of the `/Hearts of Iron IV/`, meaning you only include the folders within this folder, not the full filepath.

**noOfFrames** is used for images with multiple *frames* within, for example `GFX_unit_level` has five images within for each of the unit level images, and so would have `noOfFrames = 5` set within its asset definition.

**size** determines the size of the tile.

**borderSize** determines the size of the border.

**effectFile** is used to define an effect state to apply to the image, i.e. the button press effect on a button image. Effects are found in `/Hearts of Iron IV/gfx/FX/*.lua`. Multiple can be defined to add multiple effects.

**allwaystransparent** defines whether the image is bound by its alpha channel with regards to player clicks. Otherwise the bounding box is the image dimensions.

**tilingCenter** defines whether the center of the image is used for tiling, rather than the top left corner.

**looping** defines whether the animation loops.

**animation_rate_spf** defiens the framerate at which the animation plays.

<!-- kit:begin id="gfx-cornered-notes" at="section:corneredTileSpriteType" -->
**Kit note** In the 154 vanilla `corneredTileSpriteType` blocks `borderSize` is set in 153, `size` in 129 and `tilingCenter` in 101. `animation_rate_spf` and `looping` appear in 2 blocks only (values 2 and 4). A block with `size = { x = 0 y = 0 }` exists, so a zero size is accepted. [vanilla-confirmed 1.19.3] `interface/*.gfx`, `interface/core_bare_minimum.gfx`

```text
corneredTileSpriteType = {
	name = "gfx_transp_white_fade"
	size = { x = 40 y = 40 }
	textureFile = "gfx/interface/transp_white_fade.dds"
	borderSize = { x = 1 y = 1 }
}
```

Example block. [vanilla-confirmed 1.19.3] `interface/core_bare_minimum.gfx`
<!-- kit:end id="gfx-cornered-notes" -->

## maskedShieldType <a id="maskedShieldType"></a>

<!-- kit:begin id="gfx-maskedshield-correction" at="heading:maskedShieldType" -->
**Kit correction** The example under this heading opens with `corneredTileSpriteType`, which is a copy error. A masked shield block starts with `maskedShieldType`. All 13 vanilla blocks set `name`, `textureFile1` (the shield image), `textureFile2` (the mask) and `effectFile`; one also sets `alwaystransparent = yes`. [vanilla-confirmed 1.19.3] `interface/core.gfx`

```text
maskedShieldType = {
	name = "GFX_minishield"
	textureFile1 = "gfx//interface//minishield.tga"
	textureFile2 = "gfx//interface//minimask.tga"
	effectFile = "gfx//FX//maskedflag.lua"
}
```
<!-- kit:end id="gfx-maskedshield-correction" -->

A **maskedShieldType** asset entry is used for country shields. It follows this format:

```text
spriteTypes = {
    corneredTileSpriteType = {
        name = "GFX_<name>"
        textureFile1 = <path>
        textureFile2 = <path>
        effectFile = <path>
    }
}
```

**name** is the name you have given to the asset. This may be prefixed with various other segments, such as *idea* for idea images, etc.

**textureFile1** is the image to use for the shield background

**textureFile2** is the image to use for the shield mask.

**effectFile** is used to define an effect state to apply to the image, i.e. the button press effect on a button image. Effects are found in `/Hearts of Iron IV/gfx/FX/*.lua`. Multiple can be defined to add multiple effects.

## Object Types <a id="Object_Types"></a>

<!-- kit:begin id="gfx-object-types" at="section:Object_Types" -->
**Kit addition** `objectTypes = { ... }` blocks define 3D and map objects. Vanilla has 118 files with an `objectTypes` block, holding 1409 `pdxmesh`, 175 `pdxparticle`, 8 `arrowType` and 6 `animatedmaptext` entries. [vanilla-confirmed 1.19.3] `gfx/entities/*.gfx`, `gfx/models/`, `interface/core.gfx`, `interface/arrows.gfx`

| Block | Found in | Keys |
| --- | --- | --- |
| `pdxmesh` | `gfx/entities/*.gfx`, `gfx/models/**/*.gfx`, DLC `gfx/` folders | `name`, `file` (a `.mesh` path from the game root), `scale` (177 of 1409), `cull_distance` (7), repeated `animation = { id = "<state>" type = "<animation name>" }`, repeated `meshsettings`, repeated `variant` |
| `pdxparticle` | `gfx/entities/particles.gfx` (173), `gfx/particles/WW_particles.gfx` | `name`, `type` (the `name` of a `particle` in a `gfx/particles/**/*.asset`), `scale` |
| `arrowType` | `interface/arrows.gfx` | `name`, `texture`, `normal`, `specular`, `effect` (all 8 set all five) |
| `animatedmaptext` | `interface/core.gfx` | see the next section |

All rows: [vanilla-confirmed 1.19.3] the files named in the table.

`meshsettings` keys in vanilla: `name` (the mesh shape name), `index`, `texture_diffuse`, `texture_normal`, `texture_specular` and `shader`. Texture names are relative to the folder of the `.mesh` file. Shader values: `"PdxMeshAdvanced"` 645, `"PdxMeshAdvancedAnim"` 56, `"PdxMeshTrain"` 49, `"PdxMeshAdvancedSnow"` 49. `variant = { weight = 1.0 pdxmesh = "<other mesh>" }` is used 19 times, for cavalry horses. [vanilla-confirmed 1.19.3] `gfx/entities/tanks.gfx`, `gfx/entities/infantry.gfx`

The vanilla comment above the `variant` lines calls the feature work in progress and gives two limits: all variants must use the same `.mesh` file, and an entity cannot override `meshsettings`. [vanilla-confirmed 1.19.3] `gfx/entities/infantry.gfx`

```text
objectTypes = {
	pdxmesh = {
		name = "FIN_light_armor_mesh"
		file = "gfx/models/units/tanks/FIN_light_armor.mesh"
		animation = { id = "idle" type = "FIN_light_armor_idle_animation" }
		meshsettings = {
			name = "FIN_light_armorShape"
			index = 1
			texture_diffuse = "FIN_light_armor_diffuse.dds"
			texture_normal = "FIN_light_armor_normal.dds"
			texture_specular = "FIN_light_armor_specular.dds"
			shader = "PdxMeshAdvanced"
		}
	}
	pdxparticle = {
		name = "lamp_red_particle"
		type = "lamp_red_file"
		scale = 1.5
	}
}
```

Both blocks are shortened from vanilla. [vanilla-confirmed 1.19.3] `gfx/entities/tanks.gfx`, `gfx/entities/particles.gfx`

For `animatedmaptext`, vanilla defines six entries in `interface/core.gfx`: `MessageMapText`, `ProvinceTaxText`, `ProvinceDirectTaxText`, `CombatLoss`, `siegeinfo` and `debugtext`. One of them gives `color` four values, so alpha is allowed. That a mod cannot add new names, as the page says, is not shown by any game file. [vanilla-confirmed 1.19.3] `interface/core.gfx`

How `pdxmesh` names are used by entities is on [Entity modding](<Entity modding - Hearts of Iron 4 Wiki.md>); how `pdxparticle` names are used is on [Particle modding](<Particle modding - Hearts of Iron 4 Wiki.md>).
<!-- kit:end id="gfx-object-types" -->

## animatedmaptext <a id="animatedmaptext"></a>

A **animatedmaptext** asset entry is used for text that appears from the map. It follows this format:

```text
objectTypes = {
    animatedmaptext = {
        name = <name>
        speed = <float>
        textblock = {
            text = <string>
            color = { <r> <g> <b> }
            font = <path>
            position = {
                x = <int>
                y = <int>
            }
            size = {
                x = <int>
                y = <int>
            }
            format = <type>
            cull_distance = <float>f
        }
    }
}
```

**name** is the name of the map text. It is not possible to add custom ones.

**speed** is the fade time of the text.

**textblock** controls the attributes of the text that appears.

## Font Types <a id="Font_Types"></a>

<!-- kit:begin id="gfx-font-types" at="section:Font_Types" -->
**Kit addition** Fonts are defined by `bitmapfonts = { ... }` blocks. Vanilla has 44 `bitmapfont` and 139 `bitmapfont_override` entries in 7 files of `interface/`. The font bitmaps themselves are `.fnt` plus `.dds` pairs in `gfx/fonts/` and its `chinese/`, `japanese/` and `korean/` subfolders. [vanilla-confirmed 1.19.3] `interface/core.gfx`, `gfx/fonts/`

| File | `bitmapfont` | `bitmapfont_override` | Content |
| --- | --- | --- | --- |
| `interface/core.gfx` | 37 | 53 | the main fonts, the global `textcolors`, overrides for `l_japanese` (37) and `l_russian` `l_polish` (16) |
| `interface/core_chinese.gfx` | 0 | 37 | overrides for `l_simp_chinese` |
| `interface/core_korean.gfx` | 0 | 37 | overrides for `l_korean` |
| `interface/chatfonts.gfx` | 2 | 4 | `standard_font`, `chat_input_font` |
| `interface/load_screen_font.gfx` | 2 | 8 | `loadscreen_header`, `loadscreen_tip` |
| `interface/fonts.gfx` | 2 | 0 | debug fonts `garamond_12`, `cw_3d_debug` |
| `interface/core_bare_minimum.gfx` | 1 | 0 | `null_font` |

All rows: [vanilla-confirmed 1.19.3] the files named in the table.

The fonts most used by the base `interface/*.gui` files, counted as `font =` lines: `hoi_18mbs` (1341), `hoi_16mbs` (751), `hoi_36header` (190), `hoi_24header` (136), `hoi_20b` (101), `hoi4_typewriter16` (92), `hoi_20bs` (88), `vic_18` (70), `hoi_18b` (68), `Main_16` (58). [vanilla-confirmed 1.19.3] `interface/*.gui`

The language codes that vanilla puts in `languages = { ... }` are `l_japanese`, `l_simp_chinese`, `l_korean`, `l_russian` and `l_polish`. The game's language list also has `l_english`, `l_braz_por`, `l_french`, `l_german` and `l_spanish`, which vanilla never overrides. [vanilla-confirmed 1.19.3] `localisation/languages.yml`, `interface/core.gfx`

See [Font modding](<Font modding - Hearts of Iron 4 Wiki.md>) for making the bitmaps.
<!-- kit:end id="gfx-font-types" -->

## textcolors <a id="textcolors"></a>

A **textcolors** entry defines the text colors used in localization with the § symbol. It follows this format:

```text
bitmapfonts = {
    textcolors = {
        <symbol> = { <r> <g> <b> }
    }
}
```

**symbol** is the character used in the localization, i.e. **H**.

**RGB** is the color that the symbol applies. It is integer RGB.

## bitmapfont <a id="bitmapfont"></a>

A **bitmapfont** entry defines a font used in the game. It follows this format:

```text
bitmapfonts = {
    bitmapfont = {
        name = <name>
        path = <path>
        color = <hex>
        border_color = <hex>
        fontfiles = {
            <path>
            <path>
        }
        textcolors = {
            <symbol> = { <r> <g> <b> }
        }
        cursor_offset = {
            <int>
            <int>
        }
    }
}
```

**name** is the reference name of the font for other graphics files.

**path** is the path to the font. Fonts are found in `/Hearts of Iron IV/gfx/fonts/`.

**color** is the default color of the font. It is a hexadecimal RGB code.

**border_color** is the border color of the font. It is a hexadecimal RGB code.

**fontfiles** is used when there are multiple font images for one font, i.e. to support English and Cyrillic. This is used in place of **path**.

**textcolors** alters the global textcolors for the font it is nested within.

**cursor_offset** offsets the text cursor for the font. Defines the *x* position and then the *y* position.

<!-- kit:begin id="gfx-font-key-notes" at="section:bitmapfont" -->
**Kit note** Facts about `bitmapfont` keys from the vanilla files.

- The global `textcolors` block in `interface/core.gfx` defines 23 symbols: `C L W B G R b g Y H T O`, the digits `0` to `9` and `t`. Colours are integer `{ r g b }`. A `textcolors` block inside one `bitmapfont` overrides only the symbols it lists, for that font. [vanilla-confirmed 1.19.3] `interface/core.gfx`
- `color` is `0xAARRGGBB`; vanilla uses values like `0xffffffff` and `0xff7799ff`. `border_color` is set in one font (`Main_14`, `0x00000000`). [vanilla-confirmed 1.19.3] `interface/core.gfx`
- `cursor_offset = { 0 4 }` is written as two numbers on one line and set on 3 header fonts. The page shows it as two lines. [vanilla-confirmed 1.19.3] `interface/core.gfx`, `interface/load_screen_font.gfx`
- `path` is used in 20 fonts, `fontfiles` in 24. The exe has the message "Font '%s' has both path and fontfiles scripted? Will only use fontfiles", so `fontfiles` wins when both are present. [vanilla-confirmed 1.19.3] `interface/core.gfx`. The exe message is [unverified] `hoi4.exe`
<!-- kit:end id="gfx-font-key-notes" -->

## bitmapfont_override <a id="bitmapfont_override"></a>

A **bitmapfont_override** entry is used to override a font for a specific locale. It follows this format:

```text
bitmapfonts = {
    bitmapfont_override = {
        name = <name>
        fontfiles = {
            <path>
            <path>
        }
        languages = {
            <language>
            <language>
        }
    }
}
```

**name** is the name of the font to override.

**fontfiles** is used when their are multiple font images for one font, i.e. to support English and Cryllic. This is used inplace of **path**.

**languages** defines which languages this override applies for.

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
