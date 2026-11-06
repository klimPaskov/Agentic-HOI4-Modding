# Particle modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="71496" sources="gfx/particles/ gfx/entities/particles.gfx gfx/entities/map_lights.asset gfx/entities/buildings.asset previewer_assets/ hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: the 141 `.asset` files in `gfx/particles/` and its `environment/`, `infantry/` and `vehicles/` folders plus one in the Man the Guns DLC (142 `particle` blocks, 486 subsystems), the `pdxparticle` entries of `gfx/entities/particles.gfx` and `gfx/particles/WW_particles.gfx`, the 9 `light` blocks of `gfx/entities/map_lights.asset`, and token strings in `hoi4.exe`.
Kit blocks added: the filled "Adding a Particle" section (link chain, key tables, a trimmed example), a warning on the particle editor text, corrections for the light section.
Gaps left: no game file explains `{ a b }` pairs, `texture` `x`/`y`, `slave_particles`, `sort` or the force types, so the key tables list only what vanilla sets. The particle editor could not be tried.
**1.19.4.1 re-check (2026-11-01).** 3 tagged statements depended on files the update changed (the subsystem, animation and force tables over `gfx/particles/**/*.asset`, where `mg_muzzle_tommy.asset` changed), and all of them were re-measured. Every count is unchanged (142 particles, 486 subsystems, 509 animations, 314 forces), and the 16 `particle_editor` command strings are still in the 1.19.4.1 `hoi4.exe`. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="particle-add-chain" at="section:adding-a-particle" -->
A particle takes three pieces that are linked by name. This is how the vanilla lamp particle is wired.

1. A `particle` block in a `.asset` file under `gfx/particles/`. Its `name` ends in `_file` in vanilla (`lamp_red_file`). Textures are `.dds` files in the same folder tree (`gfx/particles/flare_wide.dds`). [vanilla-confirmed 1.19.3] `gfx/particles/lamp_red.asset`
2. A `pdxparticle` in an `objectTypes` block of a `.gfx` file. Its `type` is the `name` from step 1 and its `name` is the handle that entities use. Vanilla keeps almost all of its 175 in `gfx/entities/particles.gfx` and has one in `gfx/particles/WW_particles.gfx`. [vanilla-confirmed 1.19.3] `gfx/entities/particles.gfx`
3. An entity `event` that names the handle: `event = { time = 0.1 node = "lamp" particle = "lamp_red_particle" }`. Entities are described on [Entity modding](entity_modding.md). [vanilla-confirmed 1.19.3] `gfx/entities/buildings.asset`

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

Both files are copies of `gfx/particles/lamp_red.asset` and `gfx/entities/particles.gfx` with names changed and some keys dropped. Every key kept in the subsystem is set by at least 474 of the 486 vanilla subsystems. [vanilla-confirmed 1.19.4.1] `gfx/particles/**/*.asset`. The trimmed form was not run in the game. [unverified] `gfx/particles/lamp_red.asset`

`scale` is set in all 175 vanilla `pdxparticle` entries (values such as 1, 1.5 and 2). [vanilla-confirmed 1.19.3] `gfx/entities/particles.gfx`, `gfx/particles/WW_particles.gfx`
<!-- kit:end id="particle-add-chain" -->

<!-- kit:begin id="particle-subsystem-keys" at="section:adding-a-particle" -->
Keys of a `subsystem`, with the number of vanilla subsystems (of 486) that set each. All rows: [vanilla-confirmed 1.19.4.1] `gfx/particles/**/*.asset`.

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

`texture` holds `file`, `x`, `y` and `shader`. Shader values: `"ParticleAdditive"` 267, `"ParticleAlphaBlend"` 218, `"ParticlePreAlphaBlend"` 1. `color` holds `x y z` (470) or `r g b` (12) on the 0 to 255 scale, plus `alpha`. [vanilla-confirmed 1.19.4.1] `gfx/particles/**/*.asset`

A value can be a single number or a pair `{ a b }`, and `size`, `alpha` and similar keys can name an animation after a comma: `alpha = 255.000,smoke_fade`, `size = { 1.000,glow_scale 1.000 }`. What a pair means is not stated in a game file. [vanilla-confirmed 1.19.4.1] `gfx/particles/flamethrower.asset`, `documentation/*.md`. The reading as a range or a start and end value is a guess and is untested. [unverified] `gfx/particles/flamethrower.asset`
<!-- kit:end id="particle-subsystem-keys" -->

<!-- kit:begin id="particle-animation-force" at="section:adding-a-particle" -->
Besides subsystems, a `particle` block holds `animation` and `force` blocks that subsystems refer to by name. All rows: [vanilla-confirmed 1.19.4.1] `gfx/particles/**/*.asset`.

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

<!-- kit:begin id="particle-editor-warning" at="heading:particle-editor" -->
Warning: `particle_editor create <name>` writes `gfx/particles/<name>.asset` into the game install folder immediately, not into the user folder or a mod, and the written file is not a valid asset in 1.19.4.1. Its texture and shader blocks hold raw memory bytes instead of the texture path and the shader name. Do not run the command against a game install you play from. In the test, `particle_editor create b9_test` replied "Created new effect: b9 test" with an empty "Path:" and wrote a 1515 byte file into the install at once. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply and the install folder checked.

The version limits in the text below (editor works only on 1.11) cannot be checked from game files. What 1.19.4.1 ships: `hoi4.exe` contains the commands `particle_editor create`, `add_subsystem`, `clone_subsystem`, `remove_subsystem`, `add_animation`, `remove_animation`, `add_force`, `remove_force`, `add_childsystem`, `back_subsystem`, `forward_subsystem`, `save`, `undo`, `redo`, `restart` and `exit`, and the folder `previewer_assets/assetviewer_interface/previewer_interface.gui` has a button labelled "Particle Editor". The button label is [vanilla-confirmed 1.19.4.1] `previewer_assets/assetviewer_interface/previewer_interface.gui`. The command names are executable strings. `particle_editor` itself exists in the release build: `help particle_editor` replied "particle_editor - Spawns a particle editor", and the command alone replied "Load a particle effect before running the editor". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. `add_subsystem`, `save` and `exit` were not run to avoid more writes into the install, and no editor window was seen, so whether the editor works is untested. [unverified] `hoi4.exe`

Particles are plain text, so a mod can also write them by hand from the key tables above. [vanilla-confirmed 1.19.3] `gfx/particles/lamp_red.asset`
<!-- kit:end id="particle-editor-warning" -->

<!-- kit:begin id="particle-light-corrections" at="section:adding-a-light" -->
Lights are not in `gfx/particles/`. All 9 vanilla `light` blocks are in `gfx/entities/map_lights.asset`: `playerlight`, `muzzle_flash`, `cigarette_light`, `nuke_light`, `rifle_muzzle_flash`, `mg_muzzle_flash`, `citylight`, `nuke_big_light`, `alarm_flash`. An entity event uses one with `light = "<name>"`. [vanilla-confirmed 1.19.3] `gfx/entities/map_lights.asset`, `gfx/entities/buildings.asset`

- `intensity = 1.5, fade` is not "a value plus whether it fades". In all 9 lights the `animation` is named `fade`, and 7 lights write `intensity = <number>, fade` (also `intensity = 30,fade`); `playerlight` and `citylight` write a plain number. The word after the comma matches the animation name, the same pattern as `alpha = 255,smoke_fade` in particles. [vanilla-confirmed 1.19.4.1] `gfx/entities/map_lights.asset`, recounted: 9 of 9 lights, 7 with the suffix. The reading as "apply this animation to the intensity" is an inference. [unverified] `gfx/entities/map_lights.asset`
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
