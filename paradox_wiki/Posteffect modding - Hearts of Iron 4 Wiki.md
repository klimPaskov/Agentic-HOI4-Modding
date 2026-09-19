# Posteffect modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Posteffect modding", captured 2026-09-19.*

## Table of contents

- [Posteffect Values](#Posteffect_Values)
- [Volumes](#Volumes)
  - [Position Volume](#Position_Volume)
  - [Height Volume](#Height_Volume)
- [Tips](#Tips)

---

Posteffects are color correction effects that are applied to the lighting in certain areas (volumes) on the map map. They are used to tint the lighting for areas where the lighting would be noticable different, i.e. deserts.

All posteffects are found in `/Hearts of Iron IV/gfx/posteffect_volumes.txt`.

## Posteffect Values <a id="Posteffect_Values"></a>

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

**hdr_min_adjustment** defines the minimum adjustment used in the HDR effect.

**hdr_max_adjustment** defines the maximum adjustment used in the HDR effect.

**BLOOM_WIDTH** defines the width of the bloom effect.

**BLOOM_SCALE** defines the scale of the bloom effect.

**BRIGHT_THRESHOLD** defines the threshold of the bloom effect.

**tonemap_middlegrey** defines the middle grey used in the tone map.

## Volumes <a id="Volumes"></a>

### Position Volume <a id="Position_Volume"></a>

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

**posteffect_values_day** is the posteffect values entry to use during the day.

**posteffect_values_night** is the posteffect values entry to use during the night.

**posteffect_values_day_winter** is the posteffect values entry to use during the day during winter months.

**posteffect_values_night_winter** is the posteffect values entry to use during the night during winter months.

**position** defines the location of the volume center.

**size** defines the size of the volume box.

**fade_distance** defines the fade distance for the posteffect values.

### Height Volume <a id="Height_Volume"></a>

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

**posteffect_values_day** is the posteffect values entry to use during the day.

**posteffect_values_night** is the posteffect values entry to use during the night.

**height** defines at which height the values are applied.

**fade_distance** defines the fade distance for the posteffect values.

## Tips <a id="Tips"></a>

Make use of the console commands: `PostEffectVolumes.Enabled` and `PostEffectVolumes.Draw` when working with posteffects. Currently developer-only.

You can reload posteffects by using `reload posteffectvolumes` in the console.

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
