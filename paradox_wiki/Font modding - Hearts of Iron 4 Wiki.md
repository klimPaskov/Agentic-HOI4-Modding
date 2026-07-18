# Table of contents

- [Creating a new font](#creating-a-new-font)
  - [Font settings](#font-settings)
  - [Export options](#export-options)
  - [Selecting font characters](#selecting-font-characters)
  - [Saving the font](#saving-the-font)
  - [Quick check-list](#quick-check-list)
- [Kerning](#kerning)
- [Defining bitmaps](#defining-bitmaps)
  - [Overriding bitmaps](#overriding-bitmaps)

---

## <a id="creating-a-new-font"></a>Creating a new font

Making a new font requires the program [BMFont](http://www.angelcode.com/products/bmfont/), which is used to generate the font page and descriptor file from a font.

Once BMFont is installed, open it up and open the options menu then font settings, import your font file, and select the font from the dropdown menu (font files can be found and downloaded at Google Fonts). After that is done, you can begin to configure the font settings.

### <a id="font-settings"></a>Font settings

Having imported your font, it is time to set up how you want the font to look. To do this, open the Font Settings menu again. Below are the fields you need to change:

- **Charset**: set this to Unicode.
- **Size**: this is the size of each character in the outputted bitmap, set this to your desired size.
  - Note larger sizes will increase the final output's used space and may split your result between multiple bitmaps. The only way to use multiple bitmaps is through separately defined outputted font files, so keep as much as you can on one bitmap.
- **Match char height**: tick this so each character has the same height.
- **Font smoothing**: tick this if your font's edges look overly sharp in-game.
- **Outline thickness**: if you want your font to have an outline, set the desired thickness here.
  - Note, this will increase the character size in the font's bitmap, thus taking more space.

After this is complete press "OK" to save your changes

### <a id="export-options"></a>Export options

Having set up your font, it is time to set up how you want to export a font bitmap the game can read. To do this, open the Export Options menu. Below are the fields you may want to change:

- **Padding**: controls the padding between each character in the font image. Only needed if you intend to manually edit the font file and don't want the characters too close together.
- **Bit depth**: Set this to 32
- **Spacing**: controls the minimum space between characters in the font image. Set this to 1-1; set it higher if you experience characters bleeding into each other.
- **Width** & **Height**: the size of the exported font bitmap. Adjust this so that all the characters fit on one image.
  - Note, increasing WxH drastically increases the file size. The game cannot process a single font graphic above 16 MB, with Paradox using 16,001KB at max for Chinese fonts. This limit is quickly reached without the heavier compression modes; you can work around this by [defining multiple linked font bitmaps to one font](<Font modding - Hearts of Iron 4 Wiki.md#defining-bitmaps>), as Paradox does with the 11 linked 14-16MB Chinese font bitmaps.
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

### <a id="selecting-font-characters"></a>Selecting font characters

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

### <a id="saving-the-font"></a>Saving the font

Having set the font as you would like it, check that the characters all fit on one page by clicking V on your keyboard. If they don't, and you don't plan on using multiple font bitmaps, you need to increase the size of the font image width and height or decrease the font size.

Save the font by clicking "Save bitmap font as..." (CTRL+S) in the options menu.

**Both the image and font file must be named the exact same** except for the file's extension. While the \*.fnt file provides which image file should be used, the game opts to use the file with the same name before the internally defined one. This can also be seen by the file extension lacking from the [bitmapfont definition](#defining-bitmaps). The bitmapfont definition does not need the same name as the font files and can be customized.

The font's location is decided by the [bitmapfont definition](#defining-bitmaps), so it is not necessary to use the `/Hearts of Iron IV/gfx/fonts/` folder, however, the base game keeps all of its fonts there. The map font is the `tahoma_60` bitmapfont, which links to the `/Hearts of Iron IV/gfx/fonts/hoi_mapfont4` files by default, and the appropriate `../chinese/` and `../japanese/` folders.

### <a id="quick-check-list"></a>Quick check-list

- Open BMFont and select a font.
- Set the font settings appropriately and save changes.
- Export the font with proper settings and necessary character sets.
- **Remove \_0 from the end of the name of the resulting .dds file** to make it have the same name as the file defining the font.
- Add [kerning](#kerning) to the font if necessary.
- *If adding a new font rather than editing an existing one*, add a [bitmapfont = { ... } definition](#defining-bitmaps).

## <a id="kerning"></a>Kerning

While many do, some fonts will not be exported with kerning information included in the font file. You can confirm this by opening the \*.fnt file, and checking for lines starting with `kerning first=`. This can lead to character overlaps in-game which can be unsightly. To fix this, you need to add kerning information to your font file.

To do this, open your font file and add a new line following this format for each kerning pair:

```text
kerning first=<symbol position> second=<symbol position> amount=<pixel width>
```

A character's position within a font can be seen in BMFont by looking at the lower-right status bar when hovering over a character in the font canvas. The pixel amount is the space between the first and second character. Manually creating each kerning pair is not very feasible. Using a programming language (such as Python) to generate the kerning lines for you is much faster. Below is an example script you can use in Python 3.x or above:

```text
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

## <a id="defining-bitmaps"></a>Defining bitmaps

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

- `name` specifies the name of the font. This gets used for [interface elements that use text](<Interface modding - Hearts of Iron 4 Wiki.md>) to signify which font file gets used. **This is everything that fonts are used for**, except for the map font, which is always `tahoma_60`. To find where a base game's bitmapfont is used, it is best to [search every \*.gui file in the interface folder using a text editor](<Modding - Hearts of Iron 4 Wiki.md#search-in-files>) and check the search results for a complete list.
- `fontfiles` provides the location of all bitmaps used in the font, which is the path to the `/Hearts of Iron IV/gfx/fonts/*.fnt` file without the .fnt extension. The files should have no overlapping characters defined. If a font uses one font file in total, `path = "gfx/fonts/my_font"` can be used instead.
- `color` defines the colour of the font in hex code of the ARGB format. The first 2 characters after the `0x` define the transparency of the font, `00` meaning full transparency and `FF` meaning full opacity. The latter 6 characters provide the RGB hex code, each colour defined on the scale from `00` to `FF`.
- `textcolors` provides an override of [text colours](<Localisation - Hearts of Iron 4 Wiki.md#colouring-characters>), allowing to change a particular text colour to give a different colour when used on this font compared to the default value.

### <a id="overriding-bitmaps"></a>Overriding bitmaps

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

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

|  |  |
| --- | --- |
| Documentation | [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](https://hoi4.paradoxwikis.com/Conditions) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](https://hoi4.paradoxwikis.com/List_of_modifiers) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) ([Flags](<Data structures - Hearts of Iron 4 Wiki.md#flags>), [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#event-targets>), [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#country-tag-aliases>), [Variables](<Data structures - Hearts of Iron 4 Wiki.md#variables>), [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#arrays>)) |

|  |  |
| --- | --- |
| Scripting | [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) ([Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#game-rules>)) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Map | [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Graphical | [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • Fonts |

|  |  |
| --- | --- |
| Cosmetic | [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Other | [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](https://hoi4.paradoxwikis.com/Mod_structure) • [Mods](https://hoi4.paradoxwikis.com/Mods) • [Nudger](https://hoi4.paradoxwikis.com/Nudger) |
