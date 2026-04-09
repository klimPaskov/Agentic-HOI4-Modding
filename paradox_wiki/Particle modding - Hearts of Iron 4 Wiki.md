# Table of contents

- [Adding a Particle](#adding-a-particle)
- [Particle Editor](#particle-editor)
- [Adding a Light](#adding-a-light)
  - [Animation](#animation)


---

Particles are special entities used by other entities to create visual effects such as lightning, snow, etc.

Particles are defined in **.asset** files which are found in /Hearts of Iron IV/gfx/particles/.

## Adding a Particle

## Particle Editor

The particle editor can be accessed by adding *exclusively* **-editor** to your launch options in Steam and **reverting to 1.11**; anything earlier will result in a non functional launcher, anything later will result in a crash upon trying to access the editor. **Since the particle editor can't access new particles made by the mod, it is necessary to overwrite vanilla particles, move the edited particles to your mod files, and then verify integrity after you've finished.** The particle editor can access any vanilla entity, mesh, or particle; once accessed, the vanilla particle can then be edited to fit your needs.

## Adding a Light

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

### Animation

- **name** is the name of the animation.
- **start** is the starting position of the curve.
- **duration** is the duration of the animation.
- **repeat** determines whether the animation is repeated.
- **op** determines how multiple sources mix. Can be multiply (MUL), additive (ADD) or absolute (ABS).
- **minValue** is the minimum value on the curve.
- **maxValue** is the maximum value on the curve.
- **curve** is the curve used for the light; each set of two decimals denote an x and y position on the curve graph, the game uses these points to calculate a change in whatever the animation is interacting with. The amount of decimals should always be even; the max y value is determined by "maxValue" argument, the min y value is determined by the "minValue" argument, the max x value is determined by "duration" and the min x value is determined by "start". You can have as many sets of decimals as you want but the last x coordinate must match with the duration and the first must match with "start".

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
