# Sound modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Sound modding", captured 2026-09-19.*

## Table of contents

- [Sound](#Sound)
- [Sound Effect](#Sound_Effect)
- [Falloff](#Falloff)
- [Categories](#Categories)
- [Compressors](#Compressors)

---

Sound definitions are found in `/Hearts of Iron IV/sound`. A sound file should be saved as a **WAV** file in Stereo, as a mono channel, at 44100Hz and as a 32-bit float.

All of the sound definition files must be saved as **.asset** files.

## Sound <a id="Sound"></a>

A **sound** entry is used to define a sound. It follows this format:

```text
sound = {
    name = <name>
    file = <path>
    always_load = <bool>
    volume = <float>
}
```

**name** is the name of the sound definition that is referred to by other files.

**file** is the path to the sound file, relative to the Hearts of Iron IV **sound** folder.

**always_load** defines whether the sound is always loaded.

**volume** defines the volume of the sound.

## Sound Effect <a id="Sound_Effect"></a>

A **soundeffect** entry is used to define a soundeffect. It follows this format:

```text
soundeffect = {
    name = <name>
    falloff = <name>
    sounds = {
        sound = <name>
        weighted_sound = {
            sound = <name>
            weight = int
        }
    }

    loop = <bool>
    is3d = <bool>
    random_sound_when_looping = <bool>

    max_audible = <int>
    max_audible_behaviour = <type>

    volume = <float>
    fade_in = <float>
    fade_out = <float>

	looping_delay_random_offset = <bool>
    delay_random_offset = {
        <float>
        <float>
    }

	looping_playbackrate_random_offset = <bool>
    playbackrate_random_offset = {
        <float>
        <float>
    }

    volume_random_offset = {
        <float>
        <float>
    }

    prevent_random_repetition = <bool>
}
```

**name** is the name of the soundeffect.

**falloff** is the falloff entry used by the sound effect.

**sounds** is the sound entries used by the sound effect.

**loop** defines whether the soundeffect loops.

**is3d** defines whether the sound effect should utilise 3D sound.

**random_sound_when_looping** defines whether the soundeffect picks a random sound when looping, rather than picking iteratively.

**max_audible** defines the maximum amount of instances of the sound effect in one moment.

**max_audible_behaviour** defines what happens when more than *max_audible* instances happens. It is always **fail**.

**volume** defines the volume of the sound effect.

**fade_in** defines the fade in duration for the sound effect.

**fade_out** defines the fade out duration for the sound effect.

**looping_delay_random_offset** ???

**delay_random_offset** defines the minimum and maximum random offset to the delay between sound loops.

**looping_playbackrate_random_offset** ???

**playbackrate_random_offset** defines the minimum and maximum random offset to the playback rate between sound loops.

**volume_random_offset** defines the minimum and maximum random offset to the volume between sound loops.

**prevent_random_repetition** prevents the same sounds from playing right after it was played

## Falloff <a id="Falloff"></a>

Falloff entries define the falloff attributes for sound. They are added in sound effects, and follow this format:

```text
falloff = {
    name = <name>

    min_distance = <float>
    max_distance = <float>
    height_scale = <float>
}
```

**name** is the name of the falloff entry.

**min_distance** is the minimum distance before falloff is applied, i.e. max volume

**max_distance** is the maximum distance before no sound is heard.

**height_scale** is a scalar for the height between the sound source and the player camera.

## Categories <a id="Categories"></a>

Sound effects can be placed in sound categories that apply a specific compressor to the sounds. The categories follow this format:

```text
category = {
    name = <name>
    soundeffects = {
        <name>
    }
    compressor = {
        enabled = yes
        pregain = <float>
        postgain = <float>
        ratio = <float>
        threshold = <float>
        attacktime = <float>
        releasetime = <float>
    }
}
```

**name** is the name of the soundeffect category.

**soundeffects** is a list of the sound effects belong to the category.

**compressor** is the compressor to use for the category, see below for more information on the attributes.

## Compressors <a id="Compressors"></a>

There are two global compressors: **master_compressor** used for sounds and **music_compressor** used for music. Individual compressors can be defined for sounds within categories.

The compressors use the following format:

```text
<name> = {
    pregain = <float>
    postgain = <float>
    ratio = <float>
    threshold = <float>
    attacktime = <float>
    releasetime = <float>
}
```

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
