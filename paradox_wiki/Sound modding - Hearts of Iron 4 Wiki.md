# Table of contents

- [Sound](#sound)
- [Sound Effect](#sound-effect)
- [Falloff](#falloff)
- [Categories](#categories)
- [Compressors](#compressors)


---

Sound definitions are found in /Hearts of Iron IV/sound. A sound file should be saved as a **WAV** file in Stereo, as a mono channel, at 44100Hz and as a 32-bit float.

All of the sound definition files must be saved as **.asset** files.

## Sound

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

**always\_load** defines whether the sound is always loaded.

**volume** defines the volume of the sound.

## Sound Effect

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

**random\_sound\_when\_looping** defines whether the soundeffect picks a random sound when looping, rather than picking iteratively.

**max\_audible** defines the maximum amount of instances of the sound effect in one moment.

**max\_audible\_behaviour** defines what happens when more than *max\_audible* instances happens. It is always **fail**.

**volume** defines the volume of the sound effect.

**fade\_in** defines the fade in duration for the sound effect.

**fade\_out** defines the fade out duration for the sound effect.

**looping\_delay\_random\_offset** ???

**delay\_random\_offset** defines the minimum and maximum random offset to the delay between sound loops.

**looping\_playbackrate\_random\_offset** ???

**playbackrate\_random\_offset** defines the minimum and maximum random offset to the playback rate between sound loops.

**volume\_random\_offset** defines the minimum and maximum random offset to the volume between sound loops.

**prevent\_random\_repetition** prevents the same sounds from playing right after it was played

## Falloff

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

**min\_distance** is the minimum distance before falloff is applied, i.e. max volume

**max\_distance** is the maximum distance before no sound is heard.

**height\_scale** is a scalar for the height between the sound source and the player camera.

## Categories

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

## Compressors

There are two global compressors: **master\_compressor** used for sounds and **music\_compressor** used for music. Individual compressors can be defined for sounds within categories.

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

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
