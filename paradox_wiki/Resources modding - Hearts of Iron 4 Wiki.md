# Resources modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Resources modding", captured 2026-09-19.*

## Table of contents

- [Resources](#Resources)
  - [Icon frame](#Icon_frame)
  - [CIC](#CIC)
  - [Convoys](#Convoys)
- [Localization](#Localization)
- [Interface](#Interface)
  - [Additional notes](#Additional_notes)

---

## Resources <a id="Resources"></a>

The resources used by the game are found in `/Hearts of Iron IV/common/resources/00_resources.txt`.

The resource file follows this format:

```text
resources = {
    <resource> = {
        icon_frame = <frame>
        cic = <float>
        convoys = <float>
    }
}
```

### Icon frame <a id="Icon_frame"></a>

Icon frame controls which frame from the resource image strip is used for the resource icon. A 'frame' is the 27 by 27 pixel square the icon occupies in the image.

The resource image strip is defined by the **GFX_resources_strip** spritetype, which points to `/Hearts of Iron IV/gfx/interface/resources_strip.dds` by default. By default 1 will refer to the Oil icon, 2 to Aluminium, etc.

The icons are defined in `/Hearts of Iron IV/interface/general_stuff.gfx`. Their definition must be changed if you're adding or removing resources:

```text
	spriteType = {
		name = "GFX_resources_strip"
		texturefile = "gfx/interface/resources_strip.dds"
		noOfFrames = X #X being the number of resources you have,
	}

	spriteType = {
		name = "GFX_missing_resources_strip"
		texturefile = "gfx/interface/missing_resources_strip.dds"
		noOfFrames = X
	}
```

The number of frames strictly corresponds to the amount of resources.

### CIC <a id="CIC"></a>

CIC defines the amount of resources needed to trade for 1 Civilian Factory. By default, this is 0.125, meaning 8 units of that resource are traded for 1 factory. Value can not be larger than 1.

### Convoys <a id="Convoys"></a>

Convoys controls the maximum amount of this resource a single convoy carries. By default, this is 0.1, meaning a convoy can carry 10 of the resource.

## Localization <a id="Localization"></a>

Localisation is defined in `/Hearts of Iron IV/localisation/production_l_<language>.yml` with the following localization keys:

```text
PRODUCTION_MATERIALS_<RESOURCE>:0 "Name of resource"
<resource>_desc:0 "Description of resource"
```

## Interface <a id="Interface"></a>

If implementing different resources, you will need to edit the interface so the game understands how to display the new resource. `/Hearts of Iron IV/interface/countryproductionlineview.gui` is the relevant file here.

Each resource is utilised two GUI elements: *<resource>_icon* and *<resource>_value*, which are found under the **resources** windowtype.

```text
buttonType = {
    name = "<resource>_icon"
    position = { x=0 y=2 }
    spriteType = "GFX_resources_strip"
    frame = 1 # Which icon is used from the spriteType image referred to above.
}

instantTextboxType = {
    name = "<resource>_value"
    position = { x = 31 y = 5 }
    textureFile = ""
    font = "hoi_18mbs"
    borderSize = {x = 0 y = 0}
    text = "999"
    maxWidth = 50
    maxHeight = 20
    format = left
}
```

### Additional notes <a id="Additional_notes"></a>

A fuel can also correspond to the fuel dynamic, however only one resource at a time can do that. This is decided by the FUEL_RESOURCE [define](<Defines - Hearts of Iron 4 Wiki.md>).
Infrastructure's bonus on resource gain is decided by the INFRASTRUCTURE_RESOURCE_BONUS define and applies to all resources the same.

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
