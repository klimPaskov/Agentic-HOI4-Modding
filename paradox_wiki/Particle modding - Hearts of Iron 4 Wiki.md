# Particle modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Particle modding", captured 2026-09-19.*

## Table of contents

- [Adding a Particle](#Adding_a_Particle)
- [Particle Editor](#Particle_Editor)
- [Adding a Light](#Adding_a_Light)
  - [Animation](#Animation)

---

Particles are special entities used by other entities to create visual effects such as lightning, snow, etc.

Particles are defined in **.asset** files which are found in `/Hearts of Iron IV/gfx/particles/`.

## Adding a Particle <a id="Adding_a_Particle"></a>

## Particle Editor <a id="Particle_Editor"></a>

The particle editor can be accessed by adding *exclusively* **-editor** to your launch options in Steam and **reverting to 1.11**; anything earlier will result in a non functional launcher, anything later will result in a crash upon trying to access the editor. **Since the particle editor can't access new particles made by the mod, it is necessary to overwrite vanilla particles, move the edited particles to your mod files, and then verify integrity after you've finished.** The particle editor can access any vanilla entity, mesh, or particle; once accessed, the vanilla particle can then be edited to fit your needs.

## Adding a Light <a id="Adding_a_Light"></a>

Lights are special types of particles that are referred to in entities, for example the muzzle flash of the gun during the combat animation.

Here is a generic example:

```text
light = {
    name = "name_of_light"

    color = {
        r = { <float> }
        g = { <float> }
        b = { <float> }
    }

    intensity = <float>, fade
    radius = <float>
    falloff = <float>

    position = {
        x = <float>
        y = <float>
        z = <float>
    }

    animation = {
        name = "name_of_animation"
        start = <float>
        duration = <float>
        repeat = yes
        op = <type>
        minValue = <float>
        maxValue = <float>
        curve = {
            <decimal> <decimal> <decimal> <decimal> <decimal> <decimal>
            #example: 0.000 0.000 0.250 1.000 0.500 0.500 0.750 0.000 1.000 1.000
        }
    }
}
```

- **name** is the name of the light.
- **color** is the color of the light. The values take decimal RGB.
- **intensity** is the intensity of the light, and the second value is whether it fades.
- **radius** is the radius of the light.
- **falloff** is the falloff gradient of the light.
- **position** is the position of the light relative to the entity using it.
- **animation** is animation to play for the light.

### Animation <a id="Animation"></a>

- **name** is the name of the animation.
- **start** is the starting position of the curve.
- **duration** is the duration of the animation.
- **repeat** determines whether the animation is repeated.
- **op** determines how multiple sources mix. Can be multiply (MUL), additive (ADD) or absolute (ABS).
- **minValue** is the minimum value on the curve.
- **maxValue** is the maximum value on the curve.
- **curve** is the curve used for the light; each set of two decimals denote an x and y position on the curve graph, the game uses these points to calculate a change in whatever the animation is interacting with. The amount of decimals should always be even; the max y value is determined by "maxValue" argument, the min y value is determined by the "minValue" argument, the max x value is determined by "duration" and the min x value is determined by "start". You can have as many sets of decimals as you want but the last x coordinate must match with the duration and the first must match with "start".

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
