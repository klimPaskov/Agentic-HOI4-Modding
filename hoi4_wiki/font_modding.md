# Font modding

## Creating a new font

Making a new font requires the program BMFont, which is used to generate the font page and descriptor file from a font.

Once BMFont is installed, open it up and open the options menu then font settings, import your font file, and select the font from the dropdown menu (font files can be found and downloaded at Google Fonts). After that is done, you can begin to configure the font settings.

### Font settings

Having imported your font, it is time to set up how you want the font to look. To do this, open the Font Settings menu again. Below are the fields you need to change:

- **Charset**: set this to Unicode.
- **Size**: this is the size of each character in the outputted bitmap, set this to your desired size.
  - Note larger sizes will increase the final output's used space and may split your result between multiple bitmaps. The only way to use multiple bitmaps is through separately defined outputted font files, so keep as much as you can on one bitmap.
- **Match char height**: tick this so each character has the same height.
- **Font smoothing**: tick this if your font's edges look overly sharp in-game.
- **Outline thickness**: if you want your font to have an outline, set the desired thickness here.
  - Note, this will increase the character size in the font's bitmap, thus taking more space.

After this is complete press "OK" to save your changes

### Export options

Having set up your font, it is time to set up how you want to export a font bitmap the game can read. To do this, open the Export Options menu. Below are the fields you may want to change:

- **Padding**: controls the padding between each character in the font image. Only needed if you intend to manually edit the font file and don't want the characters too close together.
- **Bit depth**: Set this to 32
- **Spacing**: controls the minimum space between characters in the font image. Set this to 1-1; set it higher if you experience characters bleeding into each other.
- **Width** & **Height**: the size of the exported font bitmap. Adjust this so that all the characters fit on one image.
  - Note, increasing WxH drastically increases the file size. The game cannot process a single font graphic above 16 MB, with Paradox using 16,001KB at max for Chinese fonts. This limit is quickly reached without the heavier compression modes; you can work around this by [defining multiple linked font bitmaps to one font](#defining-bitmaps), as Paradox does with the 11 linked 14-16MB Chinese font bitmaps.
- **Channels**: controls how the characters are composited. Set them all to **glyph** unless you have specified an outline, in which case set the alpha channel (A) to **outline**, with the rest as **glyph**.
- **Presets**: Unnecessary if manually choosing channels above. Pick any that fits your text, but only pick ones with alpha.
- **Font descriptor**: needs to be set to text.
- **Textures**: needs to be set to .dds
- **Compression**: select the form of compression the file uses. For DDS:
  - None uses no compression, however, results in enormous file sizes and may prevent HoI4 from processing the bitmap. Use only on smaller font exports.
  - DXT1 is the highest compressed, worst quality, 1-or-0 transparency (no fading, opaque, or completely transparent).
  - DXT3 is moderately compressed, with higher quality transparency (supports fading).
  - DXT5 is lightly compressed, with the highest possible quality and transparency, with the lowest compression (aside from None).

After this is complete press "OK" to save your changes.

### Selecting font characters

To the right are checkboxes for different types of characters, if a character is used that is not in the font it will show as a question mark in a box. Choose whichever ones fit what you're using the font for. Characters can be manually chosen by clicking the character's graphic on the left-hand window - this allows fine-tuning of what characters make it into the bitmap.

In every scenario, the 1-3 blank boxes from Latin and Latin-1 Supplement (the latter might not appear) **must** be chosen so spacing works properly. Otherwise, words will appear without spacing.

Recommended characters for tooltips are:

- Latin + Latin-1 Supplement
- Latin Extended-A + B
- Latin Extended Additional
- General Punctuation

Recommended characters for map fonts depend on the language:

- Latin Alphabet (symbols can be excluded):
  - Latin + Latin-1 Supplement
  - Latin Extended-A + B
  - Latin Extended Additional

- Cyrillic Alphabet:
  - Latin + Latin-1 Supplement (blank spacing boxes)
  - Cyrillic + Cyrillic Supplement
  - Cyrillic Extended-B

### Saving the font

Having set the font as you would like it, check that the characters all fit on one page by clicking V on your keyboard. If they don't, and you don't plan on using multiple font bitmaps, you need to increase the size of the font image width and height or decrease the font size.

Save the font by clicking "Save bitmap font as..." (CTRL+S) in the options menu.

**Both the image and font file must be named the exact same** except for the file's extension. While the \*.fnt file provides which image file should be used, the game opts to use the file with the same name before the internally defined one. This can also be seen by the file extension lacking from the [bitmapfont definition](#defining-bitmaps). The bitmapfont definition does not need the same name as the font files and can be customized.

The font's location is decided by the [bitmapfont definition](#defining-bitmaps), so it is not necessary to use the `/Hearts of Iron IV/gfx/fonts/` folder, however, the base game keeps all of its fonts there. The map font is the `tahoma_60` bitmapfont, which links to the `/Hearts of Iron IV/gfx/fonts/hoi_mapfont4` files by default, and the appropriate `../chinese/` and `../japanese/` folders.

What vanilla shows about the `.fnt` and its bitmap.

- A `.fnt` is a BMFont text descriptor: an `info` line, a `common` line, an optional `page` line, `chars count=`, one `char id=` line per glyph and optional `kerning first= second= amount=` lines.
- The `page` line often names a file that does not exist. `hoi_18.fnt` names `hoi_18_0.dds` and the folder holds `hoi_18.dds`; `hoi_mapfont4.fnt` names `Hoi4_mapfont_tahoma84_merged_0.dds` and the folder holds `hoi_mapfont4.dds`. This matches the page: the bitmap with the same name as the `.fnt` is the one that loads.
- `garamond_16.fnt` has no `page` line at all and sits next to `garamond_16.tga`, with no `.dds`, and `ToolTip_Font` uses it. So a same-name `.tga` also works.
- Of the font `.dds` files in `gfx/fonts/` and its subfolders, 278 are DXT5, 2 are DXT3, 1 is DXT1 and 85 are uncompressed.
- The 11 Chinese map font bitmaps `hoi_mapfont4_<n>of11EX.dds` are 4096 pixels wide, 3400 to 4000 high, DXT5. The largest is 16,384,128 bytes, which is the "16,001KB" the page mentions.
- Vanilla spells the Cyrillic bitmaps `..._cryllic` (for example `hoi_18_cryllic.dds`). The spelling is only a file name, so any name works if `fontfiles` matches it.

### Quick check-list

- Open BMFont and select a font.
- Set the font settings appropriately and save changes.
- Export the font with proper settings and necessary character sets.
- **Remove _0 from the end of the name of the resulting .dds file** to make it have the same name as the file defining the font.
- Add [kerning](#kerning) to the font if necessary.
- *If adding a new font rather than editing an existing one*, add a [bitmapfont = { ... } definition](#defining-bitmaps).

## Kerning

While many do, some fonts will not be exported with kerning information included in the font file. You can confirm this by opening the \*.fnt file, and checking for lines starting with `kerning first=`. This can lead to character overlaps in-game which can be unsightly. To fix this, you need to add kerning information to your font file.

To do this, open your font file and add a new line following this format for each kerning pair:

```text
kerning first=<symbol position> second=<symbol position> amount=<pixel width>
```

A character's position within a font can be seen in BMFont by looking at the lower-right status bar when hovering over a character in the font canvas. The pixel amount is the space between the first and second character. Manually creating each kerning pair is not very feasible. Using a programming language (such as Python) to generate the kerning lines for you is much faster. Below is an example script you can use in Python 3.x or above:

```python
    file = open( "kerning.txt", "wt" )

    # Add the symbol positions of the blank symbol slots here.
    exclude = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 , 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 26,
                27, 28, 29, 30, 31, 127, 129, 141, 143, 144, 156, 173, 181]

    for x in range( 1, 255 ):
        for y in range(1, 255):
            if x not in exclude:
                if y not in exclude:
                    file.write( "kerning first={0}  second={1}  amount=1\n".format( x, y ) )

    file.close()
```

Kerning is optional. 27 of the 59 `.fnt` files in the top level of `gfx/fonts/` have no `kerning` line, including `hoi_18.fnt` and `hoi_mapfont4.fnt`. The most kerning lines in one file is 4819 (`vic_36.fnt`); `garamond_16.fnt` has 199, for example `kerning first=44  second=148 amount=-1`. The script above writes one line for nearly every pair of the 253 codes, which is far more than any vanilla font has.

## Defining bitmaps

To link a new font in `/Hearts of Iron IV/gfx/fonts`, an entry must be created in a `/Hearts of Iron IV/interface/*.gfx` file. **If editing an already existing font, this entry already exists and does not need to be modified.** An example entry looks like the following:

```text
bitmapfonts = {
    bitmapfont = {
        name = "my_font"
        fontfiles = {
            "gfx/fonts/font_bitmap_1"
            "gfx/fonts/font_bitmap_2"
        }
        color = 0xffffffff

        textcolors = {
            G = { 86 172 91 }
        }
    }
}
```

- `name` specifies the name of the font. This gets used for [interface elements that use text](interface_modding.md) to signify which font file gets used. **This is everything that fonts are used for**, except for the map font, which is always `tahoma_60`. To find where a base game's bitmapfont is used, it is best to [search every \*.gui file in the interface folder using a text editor](modding.md) and check the search results for a complete list.
- `fontfiles` provides the location of all bitmaps used in the font, which is the path to the `/Hearts of Iron IV/gfx/fonts/*.fnt` file without the .fnt extension. The files should have no overlapping characters defined. If a font uses one font file in total, `path = "gfx/fonts/my_font"` can be used instead.
- `color` defines the colour of the font in hex code of the ARGB format. The first 2 characters after the `0x` define the transparency of the font, `00` meaning full transparency and `FF` meaning full opacity. The latter 6 characters provide the RGB hex code, each colour defined on the scale from `00` to `FF`.
- `textcolors` provides an override of [text colours](localisation.md), allowing to change a particular text colour to give a different colour when used on this font compared to the default value.

Vanilla facts for a `bitmapfont` entry.

- The base game defines 44 fonts in 7 `interface/*.gfx` files. `interface/fonts.gfx` only holds two debug fonts, so a mod puts its own fonts in a new `interface/*.gfx` file.
- A `.gui` file picks a font with `font = "<name>"`, and the same name is used for `buttonFont`. The most used names are `hoi_18mbs` and `hoi_16mbs`.
- `color = 0xAARRGGBB`. Vanilla uses `0xffffffff`, `0xff000000`, `0xffbbbbbb` and others. One font (`hoi_22chat`) has a nine digit value, `0x4ffffffff`; write eight digits.
- Latin and Cyrillic live in separate bitmaps that one font lists together, for example `hoi_18` plus `hoi_18_cryllic`. 24 of the 44 fonts use `fontfiles`; 20 use `path`.

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

Vanilla entry, unchanged apart from layout.

The map font is `tahoma_60` (`path = "gfx/fonts/hoi_mapfont4"`). No vanilla `.gui` or `.gfx` file refers to it with `font =`, so the engine must look it up by name; that is consistent with the page. The name also exists as a token string in `hoi4.exe` (executable string, so the lookup by name is not settled). (unverified) `hoi4.exe`

### Overriding bitmaps

Additionally, it is possible to override a bitmapfont when the game is set to use a specific language. Primarily, fonts are overwritten for languages that don't use the Latin alphabet, and thus can't be small enough to fit into a 16 MB file (i.e. Simplified Chinese). By default, HoI4 has the necessary Cyrillic and Latin map font characters in one file, but the list of (Simplified) Chinese logographs is so enormous **it must encompass 11 ~4096x4000 bitmaps** with an override block in `/Hearts of Iron IV/interface/code_chinese.gfx`.

The aforementioned overwrite entries in a `/Hearts of Iron IV/interface/*.gfx` file looks like the following example:

```text
bitmapfonts = {
    bitmapfont_override = {
        name = "my_font"
        fontfiles = {
            "gfx/fonts/font_bitmap_1"
            "gfx/fonts/font_bitmap_2"
        }
        languages = { "l_russian" "l_polish" }
    }
}
```

- `path = "gfx/fonts/my_font"` may again be used instead of `fontfiles =` should you only use one bitmap.
- `languages =` must equate to one of the supported languages in HoI4. All accepted languages have folders in `/Hearts of Iron IV/localisation`.

The work involved in generating multiple bitmaps is the only downside. However, using multiple bitmaps is an effective way to organize fonts between different alphabets. Should a mod use custom fonts in entirety, it also provides more space to use larger/higher quality characters and font designs without aliasing.

The page names `interface/code_chinese.gfx`; the file is `interface/core_chinese.gfx`. Where vanilla keeps the language overrides:

| Language code | Where | Override files |
| --- | --- | --- |
| `l_simp_chinese` | `interface/core_chinese.gfx` (37 overrides), `interface/chatfonts.gfx`, `interface/load_screen_font.gfx` | `gfx/fonts/chinese/`, usually four `..._<n>of4` bitmaps per font, eleven for `tahoma_60` |
| `l_korean` | `interface/core_korean.gfx` (37), `interface/chatfonts.gfx`, `interface/load_screen_font.gfx` | `gfx/fonts/korean/`, one bitmap per font |
| `l_japanese` | `interface/core.gfx` (37) | `gfx/fonts/japanese/`, one bitmap per font (two for `tahoma_60`) |
| `l_russian` `l_polish` | `interface/core.gfx` (16) | the normal Latin and Cyrillic bitmaps, listed together |

All 139 vanilla `bitmapfont_override` blocks use `fontfiles`; none uses `path`, and the `languages` list takes one or two codes (`"l_russian" "l_polish"` is the only pair). The page's remark that `path` may replace `fontfiles` in an override is not shown by any game file.

The language codes are the keys of `localisation/languages.yml`: `l_english`, `l_braz_por`, `l_french`, `l_german`, `l_polish`, `l_russian`, `l_spanish`, `l_japanese`, `l_simp_chinese`, `l_korean`.

A font that has no override for the active language keeps its default bitmap. Vanilla overrides 41 of its 44 fonts (all fonts of `core.gfx`, `chatfonts.gfx` and `load_screen_font.gfx`) for Chinese, Korean and Japanese; only the debug fonts `garamond_12`, `cw_3d_debug` and `null_font` have no override. English, French, German, Spanish and Portuguese have none.
