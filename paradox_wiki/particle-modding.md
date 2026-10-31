# Particle modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Particle modding", revision 71496, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="71496" sources="gfx/particles/ gfx/entities/particles.gfx gfx/entities/map_lights.asset gfx/entities/buildings.asset previewer_assets/ hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: the 141 `.asset` files in `gfx/particles/` and its `environment/`, `infantry/` and `vehicles/` folders plus one in the Man the Guns DLC (142 `particle` blocks, 486 subsystems), the `pdxparticle` entries of `gfx/entities/particles.gfx` and `gfx/particles/WW_particles.gfx`, the 9 `light` blocks of `gfx/entities/map_lights.asset`, and token strings in `hoi4.exe`.
Kit blocks added: the filled "Adding a Particle" section (link chain, key tables, a trimmed example), a warning on the particle editor text, corrections for the light section.
Gaps left: no game file explains `{ a b }` pairs, `texture` `x`/`y`, `slave_particles`, `sort` or the force types, so the key tables list only what vanilla sets. The particle editor could not be tried.
<!-- kit:end id="review" -->

## Table of contents

- [Adding a Particle](#Adding_a_Particle)
- [Particle Editor](#Particle_Editor)
- [Adding a Light](#Adding_a_Light)
  - [Animation](#Animation)

---

Particles are special entities used by other entities to create visual effects such as lightning, snow, etc.

Particles are defined in **.asset** files which are found in `/Hearts of Iron IV/gfx/particles/`.

## Adding a Particle <a id="Adding_a_Particle"></a>

<!-- kit:begin id="particle-add-chain" at="section:Adding_a_Particle" -->
**Kit addition** A particle takes three pieces that are linked by name. This is how the vanilla lamp particle is wired.

1. A `particle` block in a `.asset` file under `gfx/particles/`. Its `name` ends in `_file` in vanilla (`lamp_red_file`). Textures are `.dds` files in the same folder tree (`gfx/particles/flare_wide.dds`). [vanilla-confirmed 1.19.3] `gfx/particles/lamp_red.asset`
2. A `pdxparticle` in an `objectTypes` block of a `.gfx` file. Its `type` is the `name` from step 1 and its `name` is the handle that entities use. Vanilla keeps almost all of its 175 in `gfx/entities/particles.gfx` and has one in `gfx/particles/WW_particles.gfx`. [vanilla-confirmed 1.19.3] `gfx/entities/particles.gfx`
3. An entity `event` that names the handle: `event = { time = 0.1 node = "lamp" particle = "lamp_red_particle" }`. Entities are described on [Entity modding](<entity-modding.md>). [vanilla-confirmed 1.19.3] `gfx/entities/buildings.asset`

```text
# gfx/particles/my_glow.asset  (a trimmed copy of lamp_red.asset)
particle = {
	name = "my_glow_file"
	subsystem = {
		name = "glow"
		max_amount = 1
		emitter_type = "point"
		local_space = yes
		billboard = yes
		texture = { file = "gfx/particles/flare_wide.dds" x = 1 y = 1 shader = "ParticleAdditive" }
		color = { x = 200 y = 100 z = 100 alpha = 255,fade_alpha }
		position = { x = 0 y = 0.1 z = 0 }
		duration = -1
		life = { 4 1 }
		emission = 300
		size = 1
	}
	animation = { name = "fade_alpha" start = 0 duration = 1 repeat = no minValue = 0 maxValue = 1
		curve = { 0 0 0.538 0.938 0.918 0.297 1 0 } op = "MUL" time = "life" }
}
```

```text
# gfx/entities/my_particles.gfx
objectTypes = {
	pdxparticle = { name = "my_glow_particle" type = "my_glow_file" scale = 1 }
}
```

Both files are copies of `gfx/particles/lamp_red.asset` and `gfx/entities/particles.gfx` with names changed and some keys dropped. Every key kept in the subsystem is set by all or nearly all of the 486 vanilla subsystems, but the trimmed form was not run in the game. [unverified] `gfx/particles/lamp_red.asset`

`scale` is set in all 175 vanilla `pdxparticle` entries (values such as 1, 1.5 and 2). [vanilla-confirmed 1.19.3] `gfx/entities/particles.gfx`, `gfx/particles/WW_particles.gfx`
<!-- kit:end id="particle-add-chain" -->

<!-- kit:begin id="particle-subsystem-keys" at="section:Adding_a_Particle" -->
**Kit addition** Keys of a `subsystem`, with the number of vanilla subsystems (of 486) that set each. All rows: [vanilla-confirmed 1.19.3] `gfx/particles/**/*.asset`.

| Keys | Sets | Values in vanilla |
| --- | --- | --- |
| `max_amount`, `texture`, `color`, `position`, `duration`, `life`, `emission`, `size` | 486 | `duration = -1` is used for endless emitters |
| `emitter_type` | 475 | `"point"` 304, `"sphere"` 148, `"box"` 23 |
| `name`, `slave_particles`, `invert`, `trail`, `local_space`, `billboard` | 474 | `invert` is always `no`; `trail = yes` once; `billboard` `yes` 353, `no` 121 |
| `rotation` | 466 | a pair such as `{ 0 180 }` |
| `velocity`, `velocity_yaw`, `velocity_pitch` | about 450 | a number or a pair |
| `start`, `hide`, `emitter_yaw`, `emitter_pitch` | 392 to 422 | `hide = yes` in 21 |
| `force` | 277 | the `name` of a `force` block of the same particle |
| `sort` | 261 | `"depth"` 251, `"distance"` 7, `"age"` 3 |
| `particle_pitch`, `particle_yaw`, `rotation_speed`, `rotation_speed_yaw`, `rotation_speed_pitch`, `mass` | 4 to 179 | numbers or pairs |
| `sphere_emitter_radius`, `sphere_emitter_yaw`, `sphere_emitter_pitch` | about 140 | with `emitter_type = "sphere"` |
| `box_emitter_x`, `box_emitter_y`, `box_emitter_z` | about 22 | with `emitter_type = "box"` |
| `emission_pulse_duration`, `emission_pulse_silence` | 6 and 11 | a number or a pair |

`texture` holds `file`, `x`, `y` and `shader`. Shader values: `"ParticleAdditive"` 267, `"ParticleAlphaBlend"` 218, `"ParticlePreAlphaBlend"` 1. `color` holds `x y z` (470) or `r g b` (12) on the 0 to 255 scale, plus `alpha`. [vanilla-confirmed 1.19.3] `gfx/particles/**/*.asset`

A value can be a single number or a pair `{ a b }`, and `size`, `alpha` and similar keys can name an animation after a comma: `alpha = 255.000,smoke_fade`, `size = { 1.000,glow_scale 1.000 }`. What a pair means is not stated in a game file. [vanilla-confirmed 1.19.3] `gfx/particles/flamethrower.asset`. The reading as a range or a start and end value is a guess. [unverified] `gfx/particles/flamethrower.asset`
<!-- kit:end id="particle-subsystem-keys" -->

<!-- kit:begin id="particle-animation-force" at="section:Adding_a_Particle" -->
**Kit addition** Besides subsystems, a `particle` block holds `animation` and `force` blocks that subsystems refer to by name. All rows: [vanilla-confirmed 1.19.3] `gfx/particles/**/*.asset`.

- `animation = { name start duration repeat minValue maxValue curve op time }`: all 509 vanilla animations set all nine keys. `op` is always `"MUL"`. `time` is `"life"` (462), `"life_abs"` (28), `"spawn"` (10) or `"system"` (9). `repeat = yes` in 16. `curve` is a flat list of `x y` pairs, for example `0.000 0.000 0.235 0.375 0.424 0.891 1.000 0.000`.
- `force = { type name amount direction position local_force yaw division }`: 314 forces. `type` is `"planar"` (150), `"friction"` (94), `"turbulence"` (50), `"point"` (17) or `"vortex"` (3). `direction`, `position`, `local_force`, `yaw` and `division` are set in about 280 of them.

```text
force = {
	type = "planar"
	name = "force2"
	position = { 0.000 0.000 0.000 }
	direction = { 0.000 0.100 0.000 }
	local_force = no
	yaw = 0.000
	division = 16
	amount = 2.000
}
```

Vanilla force, whitespace changed. [vanilla-confirmed 1.19.3] `gfx/particles/flamethrower.asset`
<!-- kit:end id="particle-animation-force" -->

## Particle Editor <a id="Particle_Editor"></a>

<!-- kit:begin id="particle-editor-warning" at="heading:Particle_Editor" -->
**Kit note** The version limits in the text below (editor works only on 1.11) cannot be checked from game files. What 1.19.3 ships: `hoi4.exe` contains the commands `particle_editor create`, `add_subsystem`, `clone_subsystem`, `remove_subsystem`, `add_animation`, `remove_animation`, `add_force`, `remove_force`, `add_childsystem`, `back_subsystem`, `forward_subsystem`, `save`, `undo`, `redo`, `restart` and `exit`, and the folder `previewer_assets/assetviewer_interface/previewer_interface.gui` has a button labelled "Particle Editor". [unverified] `hoi4.exe`, `previewer_assets/assetviewer_interface/previewer_interface.gui`

Particles are plain text, so a mod can also write them by hand from the key tables above. [vanilla-confirmed 1.19.3] `gfx/particles/lamp_red.asset`
<!-- kit:end id="particle-editor-warning" -->

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

<!-- kit:begin id="particle-light-corrections" at="section:Adding_a_Light" -->
**Kit correction** Lights are not in `gfx/particles/`. All 9 vanilla `light` blocks are in `gfx/entities/map_lights.asset`: `playerlight`, `muzzle_flash`, `cigarette_light`, `nuke_light`, `rifle_muzzle_flash`, `mg_muzzle_flash`, `citylight`, `nuke_big_light`, `alarm_flash`. An entity event uses one with `light = "<name>"`. [vanilla-confirmed 1.19.3] `gfx/entities/map_lights.asset`, `gfx/entities/buildings.asset`

- `intensity = 1.5, fade` is not "a value plus whether it fades". In all 9 lights the `animation` is named `fade`, and 7 lights write `intensity = <number>, fade` (also `intensity = 30,fade`); `playerlight` and `citylight` write a plain number. The word after the comma matches the animation name, the same pattern as `alpha = 255,smoke_fade` in particles. [vanilla-confirmed 1.19.3] `gfx/entities/map_lights.asset`. The reading as "apply this animation to the intensity" is an inference. [unverified] `gfx/entities/map_lights.asset`
- `op` is `"MUL"` in all 9 lights; the vanilla comment lists `"MUL"/"ADD"/"ABS"`. [vanilla-confirmed 1.19.3] `gfx/entities/map_lights.asset`
- `curve` is a flat list of `time value` pairs, one pair per line in vanilla (4 pairs in `muzzle_flash`). The page's template shows 6 numbers, and its example 10, so the count is free. [vanilla-confirmed 1.19.3] `gfx/entities/map_lights.asset`
- `color` writes each channel as `r = { 1.0 }`, with values 0 to 1. [vanilla-confirmed 1.19.3] `gfx/entities/map_lights.asset`

```text
light = {
	name = "muzzle_flash"
	color = { r = { 1.0 } g = { 0.3 } b = { 0.1 } }
	intensity = 1.5, fade
	radius = 5.7
	falloff = 5
	position = { x = 0 y = 0 z = 0 }
	animation = { name = "fade" start = 0 duration = 0.5 repeat = no op = "MUL" minValue = 0 maxValue = 1
		curve = { 0 0 0.1 1 0.6 0 1 0 } }
}
```

Vanilla light with the layout compressed. [vanilla-confirmed 1.19.3] `gfx/entities/map_lights.asset`
<!-- kit:end id="particle-light-corrections" -->

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

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list-of-modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on-actions.md>) • [Data structures](<data-structures.md>) • [Flags](<data-structures.md#Flags>) • [Event targets](<data-structures.md#Event_targets>) • [Country tag aliases](<data-structures.md#Country_tag_aliases>) • [Variables](<data-structures.md#Variables>) • [Arrays](<data-structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement-modding.md>) • [AI](<ai-modding.md>) • [AI focuses](<ai-focuses.md>) • [Autonomous states](<autonomy-state-modding.md>) • [Balances of power](<balance-of-power-modding.md>) • [Bookmarks/Scenarios](<bookmark-modding.md>) • [Game rules](<bookmark-modding.md#Game_rules>) • [Buildings](<building-modding.md>) • [Characters and traits](<character-modding.md>) • [Cosmetic tags](<cosmetic-tag-modding.md>) • [Countries](<country-creation.md>) • [Divisions](<division-modding.md>) • [Decisions](<decision-modding.md>) • [Doctrines](<doctrine-modding.md>) • [Equipment](<equipment-modding.md>) • [Events](<event-modding.md>) • [Factions](<faction-modding.md>) • [Ideas](<idea-modding.md>) • [Ideologies](<ideology-modding.md>) • [Military industrial organizations](<military-industrial-organization-modding.md>) • [National focuses](<national-focus-modding.md>) • [Resources](<resources-modding.md>) • [Scripted GUI](<scripted-gui-modding.md>) • [Technologies and doctrines](<technology-modding.md>) • [Units](<unit-modding.md>)
- **Map**: [Map](<map-modding.md>) • [States](<state-modding.md>) • [Supply areas](<supply-areas-modding.md>) • [Strategic regions](<strategic-region-modding.md>)
- **Graphical**: [Interface](<interface-modding.md>) • [Graphical assets](<graphical-asset-modding.md>) • [Entities](<entity-modding.md>) • [Posteffects](<posteffect-modding.md>) • [Fonts](<font-modding.md>)
- **Cosmetic**: [Portraits](<portrait-modding.md>) • [Namelists](<namelist-modding.md>) • [Music](<music-modding.md>) • [Sound](<sound-modding.md>)
- **Other**: [Console commands](<console-commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod-structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection-modding.md>) • [Defines additions](<defines-additions.md>) • [Game rule modding](<game-rule-modding.md>) • [Intelligence operation modding](<intelligence-operation-modding.md>) • [Map mode modding](<map-mode-modding.md>) • [Occupation and resistance modding](<occupation-and-resistance-modding.md>) • [Peace conference modding](<peace-conference-modding.md>) • [Raid modding](<raid-modding.md>) • [Script constant modding](<script-constant-modding.md>) • [Special project modding](<special-project-modding.md>)
