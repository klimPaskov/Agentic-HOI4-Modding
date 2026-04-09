# Table of contents

- [Flag](#flag)
- [Map colour](#map-colour)
- [Localisation](#localisation)
- [Other changes](#other-changes)
- [Application](#application)
- [Notes and references](#notes-and-references)


---

Cosmetic tags are a feature used to change the cosmetic appearance of a country.

Unlike regular tags, cosmetic tags do not require any definition to work and are not limited to 3 letters. A cosmetic tag changes the cosmetic aspects of the country that has it. In debug mode, the name of the cosmetic tag is shown when hovering over the country's flag in the politics or diplomacy view. The country may only have at most one cosmetic tag, setting a new one will remove the previous one.

Most commonly, this is used to change the flag, name, and/or the colour of the country as it appears on the map, but it may also be used to change other information, such as the names and portraits of randomly-generated characters or entities used for the troop models. If a cosmetic tag doesn't change the appearance of a cosmetic aspect, it will remain unchanged from the default after the country gets it. The content for cosmetic tags is nearly always added identically to base cosmetic content, with the country tag replaced with the cosmetic tag.

## Flag

*See also: [Country creation § Flag](<Country creation - Hearts of Iron 4 Wiki.md#flag>)*

Flags are added in for cosmetic tags the same way as they would be added for the base appearance of countries: three 32-bit [TGA-file](http://en.wikipedia.org/wiki/Truevision_TGA) flags with no RLE encoding with the bottom-left origin point are added into /Hearts of Iron IV/gfx/flags and its subfolders and their usage is based off the filename.

- **Standard**
  - Size requirement: 82x52 pixels
  - Resulting filesize: 16.6 or 17.1 KiB

- **Medium**
  - Size requirement: 41x26 pixels
  - Resulting filesize: 4.2 or 4.69 KiB

- **Small**
  - Size requirement: 10x7 pixels
  - Resulting filesize: 324 or 819 bytes

The name of the flag follows the same pattern as for regular flags: if ideology-specific, `COSMETICTAG_ideology.tga`, for the non-ideology fallback `COSMETICTAG.tga`. **The fallback does not have priority over an ideology-specific base country flag.** If the country TAG may choose between `TAG_ideology.tga` and `COSMETICTAG.tga`, it will use the former. Therefore, if the cosmetic tag should change the flag, adding ideology-specific flags for cosmetic tags is mandatory, unless the base country doesn't have ideology-specific flags itself.

## Map colour

*See also: [Country creation § Country file](<Country creation - Hearts of Iron 4 Wiki.md#country-file>)*

The map colours of a cosmetic tag, if they should change, are assigned in the /Hearts of Iron IV/common/countries/cosmetic.txt file. The file follows the exact same formatting as the colors.txt file used for regular tags:

```text
COSMETICTAG = {
    color = rgb { 2  10  222 }
    color_ui = rgb { 255 255 155 }
}
```

Either the [RGB colour model](http://en.wikipedia.org/wiki/RGB_color_model) or the [HSV colour model](http://en.wikipedia.org/wiki/HSL_and_HSV) may be used, signified by the `rgb`/`hsv` before the brackets. The RGB model may use decimals between 0 and 1 or between 0 and 255 for each value, while the HSV model must have its values limited to decimals between 0 and 1.

## Localisation

*See also: [Country creation § Localisation](<Country creation - Hearts of Iron 4 Wiki.md#localisation>)*

For the English language, the name of the country is created in any /Hearts of Iron IV/localisation/english/\*\_l\_english.yml file encoded in UTF-8 with the byte order mark (or UTF-8-BOM). Either of the three versions of the name will overwrite the base country equivalent, for example:

```text
l_english
COSMETICTAG_neutrality
"Cosmetic
 
tag"

 
COSMETICTAG_neutrality_ADJ
"Cosmetic"

 
COSMETICTAG_neutrality_DEF
"The
 
cosmetic
 
tag"
```

The cosmetic tag takes priority over the base localisation of the country. Each automatically-applying variation of the name may also be used, such as checking whether the country is a subject or if the check is moved to the ideology type within the ideology group, such as:

```text
l_english
COSMETICTAG_despotism_subject
"$OVERLORDADJ$
 
despotist
 
cosmetic
 
tag"
```

## Other changes

Other than these main uses, cosmetic tags serve several more minor cosmetic changes.

- Randomly-generated names: A cosmetic tag may have its entry in /Hearts of Iron IV/common/names overwrite the entries used for the base country. This is used for randomly-generated character and idea (outside of the `country` category) names. This may be used to show that a different culture from usual dominates the government of the country. This is done in the exact same way as with a country tag:

```text
COSMETICTAG = {
    male = { names = { examplename } }
    female = { names = { examplename } }
    surnames = { examplesurname }
}
```

- Randomly-generated portraits: A cosmetic tag may have its entry in /Hearts of Iron IV/portraits overwrite the entries used for the base country. This is used for randomly-generated characters. This is done in the exact same way as with a country tag:

```text
EUROPEAN_COSMETIC_TAG = {
    army = { male = { "GFX_Portrait_Europe_Generic_land_1" } }
    navy = { male = { "GFX_Portrait_Europe_Generic_navy_1" } }
}
```

- Entities used for units: A cosmetic tag may have the [entities](<Entity modding - Hearts of Iron 4 Wiki.md>) used for its [units](<Unit modding - Hearts of Iron 4 Wiki.md>) be changed from the default in /Hearts of Iron IV/gfx/entities/\*.asset files. This is done similarly to regular countries, by prepending the name of the cosmetic tag to the name of the entity, such as this entry that clones the ![Flag of France](media/cosmetic-tag-modding-hearts-of-iron-4-wiki_8daa0f4184__img1.png) French artillery entity for the country with COSMETICTAG:

```text
entity = {
    name = "COSMETICTAG_artillery_entity"
    clone = "FRA_artillery_entity"
}
```

## Application

The cosmetic tag may be applied in any [effect](<Effect - Hearts of Iron 4 Wiki.md>) block, and is limited to only being possible to add or remove via them. Effect blocks include but are not limited to focus rewards, event options, decision effects, and country history files.

`set_cosmetic_tag = COSMETICTAG` is used to apply the cosmetic tag to the country where the effect is executed. The tooltip will show that "Country will become known as the Cosmetic Tag", using the name of the country with the definite article (\_DEF name, by the suffix in localisation) in the first part and the \_DEF name of the cosmetic tag afterwards. If it appears in the tooltip that the name of the country doesn't change while the cosmetic tag is intended to, this is a sign that the \_DEF name isn't defined. If the name shouldn't change, [it may be better to hide the tooltip from the player](<Effect - Hearts of Iron 4 Wiki.md#hidden-effect>) to avoid confusion.

`drop_cosmetic_tag = yes` is used to remove the cosmetic tag that the country currently has. It has no tooltip.

Example event that sets a cosmetic tag:

```text
country_event = {
    id = event.1
    title = event.1.t
    desc = event.1.desc
    
    is_triggered_only = yes
    
    option = {
        name = event.1.a
        set_cosmetic_tag = COSMETICTAG
    }
}
```

[On actions](<On actions - Hearts of Iron 4 Wiki.md>) are commonly used to dynamically apply or remove cosmetic tags depending on the game circumstances, such as ideology change or puppeting (on actions are only able to detect puppeting in peace conferences and when releasing a country; [if puppeting is done via an effect](<Effect - Hearts of Iron 4 Wiki.md#puppet>), then set\_cosmetic\_tag has to be in the same effect block that puppets the country).  
An example on action that applies a cosmetic tag only when the country is ![{{{1}}}](media/cosmetic-tag-modding-hearts-of-iron-4-wiki_8daa0f4184__img2.png)non-aligned is as such:

```text
on_actions = {
    on_ruling_party_change = { # Note: the on action only runs after the game's start
        effect = {
            if = {
                limit = {
                    original_tag = ABC
                    has_government = neutrality
                }
                set_cosmetic_tag = ABC_neutrality
            }
            else_if = {
                limit = {
                    original_tag = ABC
                }
                drop_cosmetic_tag = yes
            }
        }
    }
}
```

## Notes and references

**[^](#ref-a)** **a:** If the correct settings of 32 bitdepth/bits per pixel and no RLE encoding are used, saving the flag should result in a consistent filesize each time. Paint.net, however, adds an approximately 500 byte large watermark to the end of the file if it is used to save the flag, which is not present when GIMP or Photoshop are used instead. The filesize is as shown in the Windows File Explorer and may differ in rounding if viewed elsewhere, such as the image editor's export menu.

1. [↑](#cite-ref-1) `NDefines.NGraphics.COUNTRY_FLAG_TEX_WIDTH = 82`, `NDefines.NGraphics.COUNTRY_FLAG_TEX_HEIGHT = 52`, `NDefines.NGraphics.COUNTRY_FLAG_MEDIUM_TEX_WIDTH = 41`, `NDefines.NGraphics.COUNTRY_FLAG_MEDIUM_TEX_HEIGHT = 26`, `NDefines.NGraphics.COUNTRY_FLAG_SMALL_TEX_WIDTH = 10`, `NDefines.NGraphics.COUNTRY_FLAG_SMALL_TEX_HEIGHT = 7` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>)

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
