# Font modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="72880" sources="interface/core.gfx interface/core_chinese.gfx interface/core_korean.gfx interface/chatfonts.gfx interface/fonts.gfx interface/load_screen_font.gfx interface/core_bare_minimum.gfx gfx/fonts/ localisation/languages.yml" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 7 vanilla files that hold `bitmapfonts` blocks, the 59 `.fnt` descriptors and the font bitmaps in `gfx/fonts/` (including `chinese/`, `japanese/`, `korean/`), `localisation/languages.yml`, and token strings in `hoi4.exe`.
Kit blocks added: how the game finds the bitmap behind a `.fnt`, kerning in vanilla, the correct override file names and language codes, notes for a `bitmapfont` entry, a minimal vanilla-style entry.
Gaps left: the BMFont steps (settings, export, character sets) cannot be checked from game files; the map font lookup for `tahoma_60` happens inside the engine.
**1.19.4.1 re-check (2026-11-01).** 11 tagged statements depended on files the update changed (`interface/core.gfx` and the `.gui` files) and all of them were re-measured on the installed files. Every count is unchanged (44 fonts in 7 files, 139 overrides, 24 `fontfiles` and 20 `path`), and `gfx/fonts/` and `localisation/languages.yml` are byte-identical. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="font-bitmap-lookup" at="section:saving-the-font" -->
What vanilla shows about the `.fnt` and its bitmap.

- A `.fnt` is a BMFont text descriptor: an `info` line, a `common` line, an optional `page` line, `chars count=`, one `char id=` line per glyph and optional `kerning first= second= amount=` lines. [vanilla-confirmed 1.19.3] `gfx/fonts/garamond_16.fnt`, `gfx/fonts/hoi_mapfont4.fnt`
- The `page` line often names a file that does not exist. `hoi_18.fnt` names `hoi_18_0.dds` and the folder holds `hoi_18.dds`; `hoi_mapfont4.fnt` names `Hoi4_mapfont_tahoma84_merged_0.dds` and the folder holds `hoi_mapfont4.dds`. This matches the page: the bitmap with the same name as the `.fnt` is the one that loads. [vanilla-confirmed 1.19.3] `gfx/fonts/`
- `garamond_16.fnt` has no `page` line at all and sits next to `garamond_16.tga`, with no `.dds`, and `ToolTip_Font` uses it. So a same-name `.tga` also works. [vanilla-confirmed 1.19.4.1] `gfx/fonts/garamond_16.fnt`, `interface/core.gfx`
- Of the font `.dds` files in `gfx/fonts/` and its subfolders, 278 are DXT5, 2 are DXT3, 1 is DXT1 and 85 are uncompressed. [vanilla-confirmed 1.19.3] `gfx/fonts/`
- The 11 Chinese map font bitmaps `hoi_mapfont4_<n>of11EX.dds` are 4096 pixels wide, 3400 to 4000 high, DXT5. The largest is 16,384,128 bytes, which is the "16,001KB" the page mentions. [vanilla-confirmed 1.19.3] `gfx/fonts/chinese/`
- Vanilla spells the Cyrillic bitmaps `..._cryllic` (for example `hoi_18_cryllic.dds`). The spelling is only a file name, so any name works if `fontfiles` matches it. [vanilla-confirmed 1.19.4.1] `gfx/fonts/`, `interface/core.gfx`
<!-- kit:end id="font-bitmap-lookup" -->

<!-- kit:begin id="font-kerning-vanilla" at="section:kerning" -->
Kerning is optional. 27 of the 59 `.fnt` files in the top level of `gfx/fonts/` have no `kerning` line, including `hoi_18.fnt` and `hoi_mapfont4.fnt`. The most kerning lines in one file is 4819 (`vic_36.fnt`); `garamond_16.fnt` has 199, for example `kerning first=44  second=148 amount=-1`. The script above writes one line for nearly every pair of the 253 codes, which is far more than any vanilla font has. [vanilla-confirmed 1.19.3] `gfx/fonts/*.fnt`
<!-- kit:end id="font-kerning-vanilla" -->

<!-- kit:begin id="font-define-notes" at="section:defining-bitmaps" -->
Vanilla facts for a `bitmapfont` entry.

- The base game defines 44 fonts in 7 `interface/*.gfx` files. `interface/fonts.gfx` only holds two debug fonts, so a mod puts its own fonts in a new `interface/*.gfx` file. [vanilla-confirmed 1.19.4.1] `interface/core.gfx`, `interface/fonts.gfx`
- A `.gui` file picks a font with `font = "<name>"`, and the same name is used for `buttonFont`. The most used names are `hoi_18mbs` and `hoi_16mbs`. [vanilla-confirmed 1.19.4.1] `interface/*.gui`
- `color = 0xAARRGGBB`. Vanilla uses `0xffffffff`, `0xff000000`, `0xffbbbbbb` and others. One font (`hoi_22chat`) has a nine digit value, `0x4ffffffff`; write eight digits. [vanilla-confirmed 1.19.4.1] `interface/core.gfx`
- Latin and Cyrillic live in separate bitmaps that one font lists together, for example `hoi_18` plus `hoi_18_cryllic`. 24 of the 44 fonts use `fontfiles`; 20 use `path`. [vanilla-confirmed 1.19.4.1] `interface/core.gfx`

```text
bitmapfonts = {
	bitmapfont = {
		name = "AnimatedMapText"
		fontfiles = {
			"gfx/fonts/hoi_18"
			"gfx/fonts/hoi_18_cryllic"
		}
		color = 0xff7799ff
	}
}
```

Vanilla entry, unchanged apart from layout. [vanilla-confirmed 1.19.4.1] `interface/core.gfx`

The map font is `tahoma_60` (`path = "gfx/fonts/hoi_mapfont4"`). No vanilla `.gui` or `.gfx` file refers to it with `font =`, so the engine must look it up by name; that is consistent with the page. [vanilla-confirmed 1.19.4.1] `interface/core.gfx`. The name also exists as a token string in `hoi4.exe` (executable string, so the lookup by name is not settled). [unverified] `hoi4.exe`
<!-- kit:end id="font-define-notes" -->

<!-- kit:begin id="font-override-correction" at="section:overriding-bitmaps" -->
The page names `interface/code_chinese.gfx`; the file is `interface/core_chinese.gfx`. Where vanilla keeps the language overrides:

| Language code | Where | Override files |
| --- | --- | --- |
| `l_simp_chinese` | `interface/core_chinese.gfx` (37 overrides), `interface/chatfonts.gfx`, `interface/load_screen_font.gfx` | `gfx/fonts/chinese/`, usually four `..._<n>of4` bitmaps per font, eleven for `tahoma_60` |
| `l_korean` | `interface/core_korean.gfx` (37), `interface/chatfonts.gfx`, `interface/load_screen_font.gfx` | `gfx/fonts/korean/`, one bitmap per font |
| `l_japanese` | `interface/core.gfx` (37) | `gfx/fonts/japanese/`, one bitmap per font (two for `tahoma_60`) |
| `l_russian` `l_polish` | `interface/core.gfx` (16) | the normal Latin and Cyrillic bitmaps, listed together |

All rows: [vanilla-confirmed 1.19.4.1] the files named in the table.

All 139 vanilla `bitmapfont_override` blocks use `fontfiles`; none uses `path`, and the `languages` list takes one or two codes (`"l_russian" "l_polish"` is the only pair). The page's remark that `path` may replace `fontfiles` in an override is not shown by any game file. [vanilla-confirmed 1.19.4.1] `interface/core.gfx`, `interface/core_chinese.gfx`

The language codes are the keys of `localisation/languages.yml`: `l_english`, `l_braz_por`, `l_french`, `l_german`, `l_polish`, `l_russian`, `l_spanish`, `l_japanese`, `l_simp_chinese`, `l_korean`. [vanilla-confirmed 1.19.3] `localisation/languages.yml`

A font that has no override for the active language keeps its default bitmap. Vanilla overrides 41 of its 44 fonts (all fonts of `core.gfx`, `chatfonts.gfx` and `load_screen_font.gfx`) for Chinese, Korean and Japanese; only the debug fonts `garamond_12`, `cw_3d_debug` and `null_font` have no override. English, French, German, Spanish and Portuguese have none. [vanilla-confirmed 1.19.4.1] `interface/core.gfx`
<!-- kit:end id="font-override-correction" -->
