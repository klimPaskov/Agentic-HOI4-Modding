# Table of contents

- [Posteffect Values](#posteffect-values)
- [Volumes](#volumes)
  - [Position Volume](#position-volume)
  - [Height Volume](#height-volume)
- [Tips](#tips)

---

Posteffects are color correction effects that are applied to the lighting in certain areas (volumes) on the map map. They are used to tint the lighting for areas where the lighting would be noticable different, i.e. deserts.

All posteffects are found in `/Hearts of Iron IV/gfx/posteffect_volumes.txt`.

## <a id="posteffect-values"></a>Posteffect Values

A posteffect values entry follows this format:

```text
posteffect_values = {
    name = <name>
    inherit = <name>

    lut = <path>

    hdr_min_adjustment = <float>
    hdr_max_adjustment = <float>

    BLOOM_WIDTH = <float>
    BLOOM_SCALE = <float>
    BRIGHT_THRESHOLD = <float>

    tonemap_middlegrey = <float>

}
```

**name** is the name of the posteffect values entry.

**inherit** causes the values for the current posteffect to be inherited from the specified posteffect.

**lut** is the path for the tone map used for this entry.

**hdr\_min\_adjustment** defines the minimum adjustment used in the HDR effect.

**hdr\_max\_adjustment** defines the maximum adjustment used in the HDR effect.

**BLOOM\_WIDTH** defines the width of the bloom effect.

**BLOOM\_SCALE** defines the scale of the bloom effect.

**BRIGHT\_THRESHOLD** defines the threshold of the bloom effect.

**tonemap\_middlegrey** defines the middle grey used in the tone map.

## <a id="volumes"></a>Volumes

### <a id="position-volume"></a>Position Volume

A volume entry specifies an area on the map in which posteffect values are applied. It follows this format:

```text
posteffect_volumes = {
    posteffect_volume = {
        name = <name>
        posteffect_values_day = <name>
        posteffect_values_night = <name>
        posteffect_values_day_winter = <name>
        posteffect_values_night_winter = <name>

        position = {
            <x>
            <y>
            <z>
        }
        size = {
            <width>
            <height>
            <depth>
        }
        fade_distance = <float>
    }
}
```

**name** is the name of the volume entry.

**posteffect\_values\_day** is the posteffect values entry to use during the day.

**posteffect\_values\_night** is the posteffect values entry to use during the night.

**posteffect\_values\_day\_winter** is the posteffect values entry to use during the day during winter months.

**posteffect\_values\_night\_winter** is the posteffect values entry to use during the night during winter months.

**position** defines the location of the volume center.

**size** defines the size of the volume box.

**fade\_distance** defines the fade distance for the posteffect values.

### <a id="height-volume"></a>Height Volume

A height volume entry specifies a height at which to apply posteffect values. It follows this format:

```text
posteffect_volumes = {
    posteffect_height_volume = {
        name = <name>
        posteffect_values_day = <name>
        posteffect_values_night = <name>

        height = <float>
        fade_distance = <float>
    }
}
```

**name** is the name of the volume entry.

**posteffect\_values\_day** is the posteffect values entry to use during the day.

**posteffect\_values\_night** is the posteffect values entry to use during the night.

**height** defines at which height the values are applied.

**fade\_distance** defines the fade distance for the posteffect values.

## <a id="tips"></a>Tips

Make use of the console commands: `PostEffectVolumes.Enabled` and `PostEffectVolumes.Draw` when working with posteffects. Currently developer-only.

You can reload posteffects by using `reload posteffectvolumes` in the console.

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
| Graphical | [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • Posteffects • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Cosmetic | [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Other | [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](https://hoi4.paradoxwikis.com/Mod_structure) • [Mods](https://hoi4.paradoxwikis.com/Mods) • [Nudger](https://hoi4.paradoxwikis.com/Nudger) |
