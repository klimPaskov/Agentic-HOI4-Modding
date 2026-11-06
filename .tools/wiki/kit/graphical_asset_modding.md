# Graphical asset modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="73705" sources="interface/ gfx/entities/ gfx/particles/WW_particles.gfx gfx/models/ gfx/fonts/ hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: every `.gfx` file under `interface/`, `gfx/`, `dlc/*/` and `integrated_dlc/*/` (214 files with `spriteTypes`, 118 with `objectTypes`, 7 with `bitmapfonts`), `interface/core.gfx`, `interface/arrows.gfx`, `gfx/entities/*.gfx`, `gfx/particles/WW_particles.gfx`, the `.fnt` and `.dds` files in `gfx/fonts/`, and token strings in `hoi4.exe`.
Kit blocks added: sprite kind census, key corrections for `spriteType` and its animation block, notes for frame animated, progress bar and cornered tile sprites, a correction for the `maskedShieldType` example, the filled "Object Types" and "Font Types" sections.
Gaps left: no game file explains `steps`, `looping`, `play_on_show`, `tilingCenter`, `dx_offset` or the `gfx/FX/*.lua` effect files, so their meaning stays as the wiki states it.
**1.19.4.1 re-check (2026-11-01).** 27 tagged statements depended on files the update changed (the `interface/*.gfx` and `.gui` files, and the DLC `gfx/` folders that the sprite and object counts scan), and all of them were re-measured directly on the installed files, including the files of the DLC folder the manifest diff cannot compare. Sprite counts rose (29,966 sprites, 160 `corneredTileSpriteType`, 76 `textSpriteType`), as did `alwaystransparent` (3,292), and a few font and key counts moved; the object file count is 97 (the earlier 118 cannot be reproduced and the update removed no `.gfx` file), and the earlier 'every DLC has an interface folder' claim is 12 of 16. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="gfx-sprite-census" at="section:sprite-types" -->
Sprite block kinds in 1.19.4.1, counted over the `.gfx` files of `interface/` (including its subfolders), `gfx/`, `dlc/*/` and `integrated_dlc/*/`. Keywords and keys are not case sensitive in practice: vanilla writes `spriteType` 18551 times and `SpriteType` 11415 times, and both `texturefile` and `textureFile`. [vanilla-confirmed 1.19.4.1] `interface/*.gfx`

| Keyword | Uses | What it is |
| --- | --- | --- |
| `spriteType` / `SpriteType` | 29966 | plain image, described below |
| `frameAnimatedSpriteType` | 160 | frame sheet played over time |
| `corneredTileSpriteType` | 160 | stretchable image with fixed borders |
| `progressbartype` | 106 | progress bar from two textures |
| `textSpriteType` | 76 | same keys as `spriteType`, used for button sprites such as `GFX_error_log_button` |
| `maskedShieldType` | 13 | flag shield with a mask |
| `pieChartType` | 5 | keys `name`, `size` (one number) and optionally `colors = { rgb = { 0 0.7 0 } ... }` |
| `circularProgressBarType` | 4 | keys `name`, `textureFile1`, `textureFile2`, `size`, `rotation`, `amount` |
| `LineChartType` | 3 | keys `name`, `size = { x = 380 y = 120 }`, `linewidth` |

All rows: [vanilla-confirmed 1.19.4.1] `interface/countrypoliticsview.gfx`, `interface/mapicons.gfx`, `interface/countryintelledger.gfx`, `interface/countrydiplomacyview.gfx`.

`progressBarType` with a capital B appears in 4 blocks of `interface/powerbalanceview.gfx` with the same keys as `progressbartype` minus the colours; it is probably the same keyword. [vanilla-confirmed 1.19.4.1] 4 of 4 blocks, and no other `.gfx` or `.gui` file writes this spelling, `interface/powerbalanceview.gfx`. Both spellings are accepted as the same keyword: a sprite defined with `progressBarType` and one defined with `progressbartype` were each found by a gui icon when its window was created, with no error.log line, while a sprite that does not exist drew "Failed to create gui object. Could not find sprite type [NAME]". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read at game start. The windows are created at game start, before they are shown, and the look of the two bars was not seen.

Sprite files are not only `interface/*.gfx`. Vanilla also uses `interface/building_roster/`, `interface/buildings/`, `interface/career_profile/`, `interface/doctrines/`, `interface/factions/`, `interface/international_market/`, `interface/military_industrial_organization/`, `interface/military_raids/`, `interface/pdx_online/`, `interface/special_projects/` and the `interface/` folder of 12 of the 16 DLC folders (`dlc/*/` and `integrated_dlc/*/`). [vanilla-confirmed 1.19.4.1] `interface/`
<!-- kit:end id="gfx-sprite-census" -->

<!-- kit:begin id="gfx-sprite-key-corrections" at="section:spritetype" -->
Notes on the keys above, checked against all vanilla `spriteTypes` blocks.

- The page spells the transparency key `allwaystransparent`. Vanilla writes `alwaystransparent` (also `alwaysTransparent`) about 3292 times in `.gfx` and `.gui` files, and the extra-`l` spelling only 8 times in `interface/popupwindow.gfx` and `interface/traittree.gfx`. Write `alwaystransparent = yes`. [vanilla-confirmed 1.19.4.1] `interface/*.gfx`, `interface/*.gui` The extra-`l` spelling is accepted in a `spriteType`, though: it drew no error.log line, while an unknown key in the same block was reported as "Unexpected token: <key>" with the file and line. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read at load. Whether the sprite becomes click-through was not seen.
- Both spellings exist as token strings in `hoi4.exe`, so the typo is probably also accepted (executable strings only). [unverified] `hoi4.exe`
- `legacy_lazy_load` is only ever written as `no` in vanilla (4865 uses, no `yes`). [vanilla-confirmed 1.19.4.1] `interface/*.gfx`
- Keys vanilla puts on `spriteType` that the page lacks: `clicksound` (23 sprites, the name of a sound effect such as `click_chat`, see [Sound modding](sound_modding.md)), `loadType` (`"INGAME"` 77 times and `"FRONTEND"` 6 times over all sprite kinds), `generate_mip_maps = yes` (4), `framedirectiony = yes` (4), `dx_offset = { x = -0.5 y = -0.5 }` (7) and `masking_texture` (1). [vanilla-confirmed 1.19.4.1] `interface/chat.gfx`, `interface/core.gfx`, `interface/*.gfx`
- No game file states what `loadType`, `generate_mip_maps`, `framedirectiony` or `dx_offset` do: no file under `documentation/` names them and no `.gfx` comment explains them. [vanilla-confirmed 1.19.4.1] `documentation/*.md`, `interface/*.gfx`
- Animation block: vanilla has 6372 `animation` blocks, and each sets the ten keys `animationmaskfile`, `animationtexturefile`, `animationrotation`, `animationlooping`, `animationtime`, `animationdelay`, `animationblendmode`, `animationtype`, `animationrotationoffset` and `animationtexturescale`. [vanilla-confirmed 1.19.4.1] `interface/abilitylist.gfx`
- `animationblendmode` values in vanilla: `"add"` 6365 times, `"normal"` 4 times, `"overlay"` 3 times. `"multiply"`, which the page lists, is never used. [vanilla-confirmed 1.19.4.1] `interface/*.gfx`
- `animationtype` values in vanilla: `"scrolling"` 6318 times, `"rotating"` 25, `"rotating_ccw"` 24, `"pulsing"` 5. `rotating_ccw` is missing from the page. [vanilla-confirmed 1.19.4.1] `interface/*.gfx`
- `animationframes` appears in only 3 blocks and holds a list of frame numbers (`animationframes = { 1 2 3 }`), not a frame count as the page says. [vanilla-confirmed 1.19.4.1] `interface/crypto.gfx`, `interface/social_view.gfx`
- `effectFile` is written at most once per sprite in vanilla (0 of 14,948 `spriteType` blocks have two). The page says several can be given; that is not shown by any game file. [vanilla-confirmed 1.19.4.1] `interface/*.gfx`
<!-- kit:end id="gfx-sprite-key-corrections" -->

<!-- kit:begin id="gfx-frameanimated-notes" at="section:frameanimatedspritetype" -->
All 160 vanilla `frameAnimatedSpriteType` blocks set `name`, `noOfFrames`, `animation_rate_fps` and `looping`. `play_on_show` is set in 153 and `pause_on_loop` in 156. `animation_rate_fps` is not an integer: vanilla uses 15 (41 blocks), 1 (36), 1.5 (26), 12 (18), 24 (10), 2 (9), 7 (5) and 0.5 (3), and 12 more blocks use other rates. [vanilla-confirmed 1.19.4.1] `interface/*.gfx`

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

Example block. [vanilla-confirmed 1.19.4.1] `interface/alerts.gfx`
<!-- kit:end id="gfx-frameanimated-notes" -->

<!-- kit:begin id="gfx-progressbar-notes" at="section:progressbartype" -->
All 106 vanilla `progressbartype` blocks set `name`, `textureFile1`, `textureFile2`, `size` and `effectFile`. `color` and `colortwo` come as a pair in 83 blocks, `horizontal` is set in 38 and `steps` in 16 (values 3, 5, 408, 500, 10000 and 1000000). Colours are decimal 0 to 1. The page's default of 100 for `steps` is not stated in any game file. [vanilla-confirmed 1.19.4.1] `interface/countryproductionlineview.gfx`, `interface/*.gfx`

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

<!-- kit:begin id="gfx-cornered-notes" at="section:corneredtilespritetype" -->
In the 160 vanilla `corneredTileSpriteType` blocks `borderSize` is set in 155, `size` in 132 and `tilingCenter` in 104. `animation_rate_spf` and `looping` appear in 2 blocks only (values 2 and 4). A block with `size = { x = 0 y = 0 }` exists, so a zero size is accepted. [vanilla-confirmed 1.19.4.1] `interface/*.gfx`, `interface/core_bare_minimum.gfx`

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

<!-- kit:begin id="gfx-maskedshield-correction" at="heading:maskedshieldtype" -->
The example under this heading opens with `corneredTileSpriteType`, which is a copy error. A masked shield block starts with `maskedShieldType`. All 13 vanilla blocks set `name`, `textureFile1` (the shield image), `textureFile2` (the mask) and `effectFile`; one also sets `alwaystransparent = yes`. [vanilla-confirmed 1.19.4.1] `interface/core.gfx`

```text
maskedShieldType = {
	name = "GFX_minishield"
	textureFile1 = "gfx//interface//minishield.tga"
	textureFile2 = "gfx//interface//minimask.tga"
	effectFile = "gfx//FX//maskedflag.lua"
}
```
<!-- kit:end id="gfx-maskedshield-correction" -->

<!-- kit:begin id="gfx-object-types" at="section:object-types" -->
`objectTypes = { ... }` blocks define 3D and map objects. Vanilla has 97 files with an `objectTypes` block, holding 1409 `pdxmesh`, 175 `pdxparticle`, 8 `arrowType` and 6 `animatedmaptext` entries. [vanilla-confirmed 1.19.4.1] `gfx/entities/*.gfx`, `gfx/models/`, `interface/core.gfx`, `interface/arrows.gfx`

| Block | Found in | Keys |
| --- | --- | --- |
| `pdxmesh` | `gfx/entities/*.gfx`, `gfx/models/**/*.gfx`, DLC `gfx/` folders | `name`, `file` (a `.mesh` path from the game root), `scale` (177 of 1409), `cull_distance` (7), repeated `animation = { id = "<state>" type = "<animation name>" }`, repeated `meshsettings`, repeated `variant` |
| `pdxparticle` | `gfx/entities/particles.gfx` (173), `gfx/particles/WW_particles.gfx` | `name`, `type` (the `name` of a `particle` in a `gfx/particles/**/*.asset`), `scale` |
| `arrowType` | `interface/arrows.gfx` | `name`, `texture`, `normal`, `specular`, `effect` (all 8 set all five) |
| `animatedmaptext` | `interface/core.gfx` | see the next section |

All rows: [vanilla-confirmed 1.19.4.1] the files named in the table.

`meshsettings` keys in vanilla: `name` (the mesh shape name), `index`, `texture_diffuse`, `texture_normal`, `texture_specular` and `shader`. Texture names are relative to the folder of the `.mesh` file. Shader values: `"PdxMeshAdvanced"` 645, `"PdxMeshAdvancedAnim"` 56, `"PdxMeshTrain"` 49, `"PdxMeshAdvancedSnow"` 49. `variant = { weight = 1.0 pdxmesh = "<other mesh>" }` is used 19 times, for cavalry horses. [vanilla-confirmed 1.19.4.1] `gfx/entities/tanks.gfx`, `gfx/entities/infantry.gfx`

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

For `animatedmaptext`, vanilla defines six entries in `interface/core.gfx`: `MessageMapText`, `ProvinceTaxText`, `ProvinceDirectTaxText`, `CombatLoss`, `siegeinfo` and `debugtext`. One of them gives `color` four values, so alpha is allowed. That a mod cannot add new names, as the page says, is not shown by any game file. [vanilla-confirmed 1.19.4.1] `interface/core.gfx`

How `pdxmesh` names are used by entities is on [Entity modding](entity_modding.md); how `pdxparticle` names are used is on [Particle modding](particle_modding.md).
<!-- kit:end id="gfx-object-types" -->

<!-- kit:begin id="gfx-font-types" at="section:font-types" -->
Fonts are defined by `bitmapfonts = { ... }` blocks. Vanilla has 44 `bitmapfont` and 139 `bitmapfont_override` entries in 7 files of `interface/`. The font bitmaps themselves are `.fnt` plus `.dds` pairs in `gfx/fonts/` and its `chinese/`, `japanese/` and `korean/` subfolders. [vanilla-confirmed 1.19.4.1] `interface/core.gfx`, `gfx/fonts/`

| File | `bitmapfont` | `bitmapfont_override` | Content |
| --- | --- | --- | --- |
| `interface/core.gfx` | 37 | 53 | the main fonts, the global `textcolors`, overrides for `l_japanese` (37) and `l_russian` `l_polish` (16) |
| `interface/core_chinese.gfx` | 0 | 37 | overrides for `l_simp_chinese` |
| `interface/core_korean.gfx` | 0 | 37 | overrides for `l_korean` |
| `interface/chatfonts.gfx` | 2 | 4 | `standard_font`, `chat_input_font` |
| `interface/load_screen_font.gfx` | 2 | 8 | `loadscreen_header`, `loadscreen_tip` |
| `interface/fonts.gfx` | 2 | 0 | debug fonts `garamond_12`, `cw_3d_debug` |
| `interface/core_bare_minimum.gfx` | 1 | 0 | `null_font` |

All rows: [vanilla-confirmed 1.19.4.1] the files named in the table.

The fonts most used by the base `interface/*.gui` files, counted as `font =` lines: `hoi_18mbs` (1354), `hoi_16mbs` (769), `hoi_36header` (190), `hoi_24header` (138), `hoi_20b` (113), `hoi4_typewriter16` (92), `hoi_20bs` (91), `vic_18` (70), `hoi_18b` (69), `Main_16` (58). [vanilla-confirmed 1.19.4.1] `interface/*.gui`

The language codes that vanilla puts in `languages = { ... }` are `l_japanese`, `l_simp_chinese`, `l_korean`, `l_russian` and `l_polish`. The game's language list also has `l_english`, `l_braz_por`, `l_french`, `l_german` and `l_spanish`, which vanilla never overrides. [vanilla-confirmed 1.19.4.1] `localisation/languages.yml`, `interface/core.gfx`

See [Font modding](font_modding.md) for making the bitmaps.
<!-- kit:end id="gfx-font-types" -->

<!-- kit:begin id="gfx-font-key-notes" at="section:bitmapfont" -->
Facts about `bitmapfont` keys from the vanilla files.

- The global `textcolors` block in `interface/core.gfx` defines 23 symbols: `C L W B G R b g Y H T O`, the digits `0` to `9` and `t`. Colours are integer `{ r g b }`. A `textcolors` block inside one `bitmapfont` overrides only the symbols it lists, for that font. [vanilla-confirmed 1.19.4.1] `interface/core.gfx`
- `color` is `0xAARRGGBB`; vanilla uses values like `0xffffffff` and `0xff7799ff`. `border_color` is set in one font (`Main_14`, `0x00000000`). [vanilla-confirmed 1.19.4.1] `interface/core.gfx`
- `cursor_offset = { 0 4 }` is written as two numbers on one line and set on 3 header fonts. The page shows it as two lines. [vanilla-confirmed 1.19.4.1] `interface/core.gfx`, `interface/load_screen_font.gfx`
- `path` is used in 20 fonts, `fontfiles` in 24. The exe has the message "Font '%s' has both path and fontfiles scripted? Will only use fontfiles", so `fontfiles` wins when both are present. [vanilla-confirmed 1.19.4.1] `interface/core.gfx`. No vanilla font block writes both (0 of 44). The message is real: a test font with both keys drew "Font 'igc_e_font' has both path and fontfiles scripted? Will only use fontfiles" in error.log at load. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read. The claim that `fontfiles` wins rests on that engine message, not on a screenshot of the rendered font.
<!-- kit:end id="gfx-font-key-notes" -->
