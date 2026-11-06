# Entity modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="23379" sources="gfx/entities/ gfx/models/ map/ambient_object.txt documentation/effects_documentation.md common/raids/ common/national_focus/" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all `.asset` files of the base game and DLC (393 files, 3439 `entity` blocks, 1296 `animation` blocks, 9 `light` blocks), the `pdxmesh` blocks of `gfx/entities/*.gfx` and `gfx/models/**/*.gfx`, `map/ambient_object.txt`, and the entity effects in `documentation/effects_documentation.md`.
Kit blocks added: a correction of the file name in the intro, extra `pdxmesh` and `entity` keys, the real meaning of `propagate_state`, event and attach notes, locator and animation examples, where entities are used.
Gaps left: what `clone`, `version`, `game_data` and the event `id` do inside the engine is not written in any game file. The particle editor and the `state` names each unit class expects are not documented.
**1.19.4.1 re-check (2026-11-01).** 12 tagged statements depended on files the update changed (the `.asset` files of Waking the Tiger and `gfx/models/`, `common/national_focus/chile.txt`) or on the DLC folder the manifest diff cannot compare, and all of them were re-measured directly on the installed files. The `.asset` census now finds 3,567 `entity` blocks (the earlier 3,439 cannot be reproduced), 11,154 `event` blocks and 6,191 `attach` lines, and most state, event and `clone` counts rose; `override_model` lines in `common/` went from 171 to 141. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="entity-intro-correction" at="heading:adding-a-mesh" -->
The intro names `ambient_objects.txt`. The file in 1.19.3 is `map/ambient_object.txt` (singular); `gfx/entities/ambient_objects.gfx` holds the meshes. Each `type = "<entity name>"` block in the map file places one entity, for example `type = "ambient_wind_entity"`. [vanilla-confirmed 1.19.3] `map/ambient_object.txt`

Vanilla `.asset` files for entities are in `gfx/entities/` (26 files) and in the `gfx/entities/` folders of the DLC that add units. Animation `.asset` files sit with the models under `gfx/models/**` (one per unit class, for example `gfx/models/units/tanks/animation_tanks.asset`). [vanilla-confirmed 1.19.4.1] `gfx/entities/`, `gfx/models/`
<!-- kit:end id="entity-intro-correction" -->

<!-- kit:begin id="entity-mesh-notes" at="section:adding-a-mesh" -->
Keys of a `pdxmesh` that the page does not list, with vanilla counts over 1409 meshes: `meshsettings = { name index texture_diffuse texture_normal texture_specular shader }` (803 blocks), `variant = { weight = 1.0 pdxmesh = "<mesh>" }` (19) and `cull_distance` (7). Full tables and an example are in [Graphical asset modding](graphical_asset_modding.md#object-types). [vanilla-confirmed 1.19.4.1] `gfx/entities/tanks.gfx`, `gfx/entities/infantry.gfx`, `gfx/entities/mapitems.gfx`

`file` is a path from the game root (`gfx/models/units/tanks/ENG_tank_light.mesh`). The `.anim` files, the `.mesh` and the textures of one model sit together in one folder, and `texture_diffuse` and its siblings give only the file name. [vanilla-confirmed 1.19.3] `gfx/models/units/tanks/`, `gfx/entities/tanks.gfx`

Animation ids in vanilla meshes (12731 `animation` lines) are free names, chosen to match the `state` names of the entity. The most common are `idle` (1141), `move` (783), `attack` (742), `death` (488), `training` (474), `cavalry_idle` and `cavalry_move` (470 each), `jumping_jacks` and `pushup` (451 each), `retreat` (436) and `support_attack` (434). [vanilla-confirmed 1.19.4.1] `gfx/entities/*.gfx`
<!-- kit:end id="entity-mesh-notes" -->

<!-- kit:begin id="entity-keys-extra" at="section:adding-an-entity" -->
Entity keys in vanilla that the page does not list. Counts are over the 3567 `entity` blocks of all `.asset` files of the base game and DLC. All rows: [vanilla-confirmed 1.19.4.1] `gfx/entities/*.asset`.

| Key | Uses | Example |
| --- | --- | --- |
| `clone` | 1582 | `clone = "building_nuclear_reactor"` before `name = "building_nuclear_reactor_heavy_water"` |
| `version` | 127 | `version = 1` (a few `version = 2`) |
| `game_data = { texture_anim_speed = ... }` | 169 | an entity level block |
| `cull_radius` | 17 | the page documents it |
| `get_state_from_parent` | 74 | the page documents it |
| `locator = { name position rotation }` | 120 | `rotation` is set in 17 |

An entity that only clones another and sets a new `name` is valid:

```text
entity = {
	clone = "building_nuclear_reactor"
	name = "building_nuclear_reactor_heavy_water"
}
```

[vanilla-confirmed 1.19.3] `gfx/entities/buildings.asset`

No game documentation file and no comment in `gfx/entities/` explains `clone` or `version`. [vanilla-confirmed 1.19.4.1] `documentation/*.md`, `gfx/entities/*.asset`. What the engine copies on `clone`, and what `version` selects, is untested. [unverified] `gfx/entities/units_vehicles.asset`

A larger vanilla entity with attached sub-entities and a propagated state:

```text
entity = {
	name = "FIN_mechanized_entity"
	version = 1
	pdxmesh = "motorized_frame_mesh"
	default_state = "idle"
	state = { name = "idle" animation = "idle" animation_blend_time = 0.3 animation_speed = 1.0 }
	state = { name = "attack" animation = "move" animation_blend_time = 0.0 animation_speed = 1.0
		propagate_state = { infantry = "move" } }
	attach = { name = "vehicle" vehicle = "FIN_mechanized_vehicle_entity" }
	attach = { name = "infantry" infantry = "FIN_vehicle_infantry_rifle_entity" }
}
```

Shortened from vanilla. [vanilla-confirmed 1.19.3] `gfx/entities/units_vehicles.asset`
<!-- kit:end id="entity-keys-extra" -->

<!-- kit:begin id="entity-state-correction" at="section:state" -->
`propagate_state` does not take `node = "idle"`. In vanilla its keys are the names of `attach` entries (`infantry`, `rider`, `cavalry`, `rifle1`, `rifle2`, `lighter`) and the value is the state to put that attached entity in: `propagate_state = { infantry = "move" }`. The `node` form from the page never appears. [vanilla-confirmed 1.19.4.1] `gfx/entities/units_vehicles.asset`, `gfx/entities/units_infantry.asset`, `gfx/entities/units_cavalry.asset`

State keys used in vanilla but missing from the page: `time_offset` (1), a nested `attach` (9), a nested `scale` (1) and `game_data = { hitmiss_effect = { time = 0.1 type = big } }` on ship states (196). `looping` is written as `no` in 3398 states and `yes` in 16. [vanilla-confirmed 1.19.4.1] `gfx/entities/_units_battleships_DLC.asset`, `gfx/entities/*.asset`

Most used state names: `idle` (2547), `training` (2246), `move` (1451), `attack` (1426), `retreat` (1217), `defend` (1165), `support_attack` (1125), `death` (475), then aircraft states `crash`, `bomb`, `firebomb`, `explode` and `fire`. `chance` is mostly 1 or 2; it picks between states that share a name, as the page says. [vanilla-confirmed 1.19.4.1] `gfx/entities/*.asset`
<!-- kit:end id="entity-state-correction" -->

<!-- kit:begin id="entity-event-notes" at="section:event" -->
Event keys counted over 11154 vanilla `event` blocks: `time` (9484), `particle` (8831), `keep_particle` (8702), `node` (8039), `sound` (4972), `trigger_once` (3961), `light` (517) and `id` (228). `id` is not on the page; it is used by aircraft states (`event = { time = 0.2 id = a_fire }`). [vanilla-confirmed 1.19.4.1] `gfx/entities/*.asset`, `gfx/entities/units_planes.asset`

`time` behaves as the moment inside the state at which the event fires. One vanilla state fires the same muzzle particle at `time = 0` and again at `time = 14`, so the page's wording "duration of the event" is misleading. [vanilla-confirmed 1.19.3] `gfx/entities/buildings.asset`. The reading as a start time is an inference. [unverified] `gfx/entities/buildings.asset`

- `particle` takes the `name` of a `pdxparticle` in a `.gfx` file, not the `name` of the `particle` in the `.asset` (see [Particle modding](particle_modding.md)). [vanilla-confirmed 1.19.3] `gfx/entities/buildings.asset`, `gfx/entities/particles.gfx`
- `light` takes a `light` name from `gfx/entities/map_lights.asset`: `playerlight`, `muzzle_flash`, `cigarette_light`, `nuke_light`, `rifle_muzzle_flash`, `mg_muzzle_flash`, `citylight`, `nuke_big_light`, `alarm_flash`. [vanilla-confirmed 1.19.3] `gfx/entities/map_lights.asset`
- `sound = { soundeffect = <name> }` takes a `soundeffect` name (see [Sound modding](sound_modding.md)). `soundeffect` is the only key ever used inside that block (4972 uses). [vanilla-confirmed 1.19.4.1] `gfx/entities/buildings.asset`

```text
event = { time = 0 node = "mg1" particle = "aa_muzzle_small_particle" keep_particle = yes light = "mg_muzzle_flash" sound = { soundeffect = mechanized_units_mg_fire } }
```

Vanilla event. [vanilla-confirmed 1.19.3] `gfx/entities/buildings.asset`
<!-- kit:end id="entity-event-notes" -->

<!-- kit:begin id="entity-attach-notes" at="section:attach" -->
Vanilla has 6191 `attach` lines. The key next to `name` is either a skeleton or locator node name (`Right_Hand_node` 718, `Left_Hand_node` 712, `Root_node_2` 692, `mid_back_node` 579, `Saddle_Node` 241) or a role name for a sub-entity slot (`infantry` 899, `vehicle` 332, `cavalry` 258, `horse` 250, `artillery` 238, `combined` 44, `bike` 40). The value is an entity name. `propagate_state` refers to the same `name`. [vanilla-confirmed 1.19.4.1] `gfx/entities/units_infantry.asset`, `gfx/entities/units_vehicles.asset`
<!-- kit:end id="entity-attach-notes" -->

<!-- kit:begin id="entity-locator-example" at="section:locator" -->
Vanilla locators give the spots that events point at with `node = "<locator name>"`. A dockyard has two damage locators, and its `damaged` state fires a particle from each:

```text
entity = {
	name = "building_dockyard_1"
	pdxmesh = "building_dockyard_1"
	scale = 0.8
	locator = { name = "damage_locator_01" position = { 1.7 1.0 -1.7 } }
	locator = { name = "damage_locator_02" position = { -0.1 1.0 0.5 } }
	default_state = "idle"
	state = { name = "idle" }
	state = { name = "damaged"
		event = { time = 0.1 node = "damage_locator_01" particle = "building_damaged_particle" }
		event = { time = 0.1 node = "damage_locator_02" particle = "building_damaged_particle" }
	}
}
```

Vanilla entity, whitespace changed. [vanilla-confirmed 1.19.3] `gfx/entities/buildings.asset`
<!-- kit:end id="entity-locator-example" -->

<!-- kit:begin id="entity-animation-example" at="section:adding-an-animation" -->
`file` is relative to the folder of the `.asset` that holds the block, and the `.anim` files sit in that folder. Vanilla has 1296 `animation` blocks, all with exactly the keys `name` and `file`:

```text
animation = {
	name = "ENG_tank_light_attack_animation"
	file = "ENG_tank_light_attack.anim"
}
```

[vanilla-confirmed 1.19.3] `gfx/models/units/tanks/animation_tanks.asset`
<!-- kit:end id="entity-animation-example" -->

<!-- kit:begin id="entity-where-used" at="bottom" -->
Where an entity name is used in script, with what vanilla and the documentation show.

- `division_template = { override_model = <entity> }` gives a division template its own model, for example `override_model = CHL_infantry_alt_0_entity` in `common/national_focus/chile.txt` (141 `override_model = <..._entity>` lines in `common/`). [vanilla-confirmed 1.19.4.1] `common/national_focus/chile.txt`
- Raid outcomes name an entity: `entity = "raid_failed_entity"` in `common/raids/air_raids.txt`. [vanilla-confirmed 1.19.3] `common/raids/air_raids.txt`
- The effects `create_entity`, `destroy_entity`, `set_entity_position`, `set_entity_movement`, `set_entity_rotation`, `set_entity_scale` and `set_entity_animation` act on entities by `id`. Vanilla script never calls `create_entity`. [docs] `documentation/effects_documentation.md`. The zero use count is [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`
- Buildings use an entity named `building_<building id>`; see [Building modding](building_modding.md#models). [vanilla-confirmed 1.19.3] `gfx/entities/buildings.asset`
<!-- kit:end id="entity-where-used" -->
