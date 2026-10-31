# Entity modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Entity modding", revision 23379, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="23379" sources="gfx/entities/ gfx/models/ map/ambient_object.txt documentation/effects_documentation.md common/raids/ common/national_focus/" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all `.asset` files of the base game and DLC (393 files, 3439 `entity` blocks, 1296 `animation` blocks, 9 `light` blocks), the `pdxmesh` blocks of `gfx/entities/*.gfx` and `gfx/models/**/*.gfx`, `map/ambient_object.txt`, and the entity effects in `documentation/effects_documentation.md`.
Kit blocks added: a correction of the file name in the intro, extra `pdxmesh` and `entity` keys, the real meaning of `propagate_state`, event and attach notes, locator and animation examples, where entities are used.
Gaps left: what `clone`, `version`, `game_data` and the event `id` do inside the engine is not written in any game file. The particle editor and the `state` names each unit class expects are not documented.
<!-- kit:end id="review" -->

## Table of contents

- [Adding a Mesh](#Adding_a_Mesh)
  - [Animation](#Animation)
- [Adding an Entity](#Adding_an_Entity)
  - [State](#State)
  - [Event](#Event)
  - [Attach](#Attach)
  - [Sound](#Sound)
  - [Locator](#Locator)
- [Adding an Animation](#Adding_an_Animation)

---

Entities are definitions used by Hearts of Iron IV to link models with script objects that are used in places such as `ambient_objects.txt`.

Both **.gfx** and **.asset** files are found in `/Hearts of Iron IV/gfx/entities/`.

Animations **.asset** files are found in `/Hearts of Iron IV/gfx/models/`.

## Adding a Mesh <a id="Adding_a_Mesh"></a>

<!-- kit:begin id="entity-intro-correction" at="heading:Adding_a_Mesh" -->
**Kit correction** The intro names `ambient_objects.txt`. The file in 1.19.3 is `map/ambient_object.txt` (singular); `gfx/entities/ambient_objects.gfx` holds the meshes. Each `type = "<entity name>"` block in the map file places one entity, for example `type = "ambient_wind_entity"`. [vanilla-confirmed 1.19.3] `map/ambient_object.txt`

Vanilla `.asset` files for entities are in `gfx/entities/` (26 files) and in the `gfx/entities/` folders of the DLC that add units. Animation `.asset` files sit with the models under `gfx/models/**` (one per unit class, for example `gfx/models/units/tanks/animation_tanks.asset`). [vanilla-confirmed 1.19.3] `gfx/entities/`, `gfx/models/`
<!-- kit:end id="entity-intro-correction" -->

To add a mesh, you need to add a **.gfx** file in your mod that includes a mesh definition. Here is a generic example:

```text
objectTypes = {
    pdxmesh = {
        name = "name_of_mesh"
        file = "gfx/models/name_of_mesh.mesh"
        animation = { id = "idle" type = "name_of_animation" }
        scale = 1.0
    }
}
```

- **name** is the name of the mesh that is then referred to in an **.asset** file.
- **file** is the relative filepath to the model that the mesh it associated with.
- **animation** is a scope added for each animation associated with the mesh.
- **scale** is a scalar for the size of the model.

<!-- kit:begin id="entity-mesh-notes" at="section:Adding_a_Mesh" -->
**Kit addition** Keys of a `pdxmesh` that the page does not list, with vanilla counts over 1409 meshes: `meshsettings = { name index texture_diffuse texture_normal texture_specular shader }` (803 blocks), `variant = { weight = 1.0 pdxmesh = "<mesh>" }` (19) and `cull_distance` (7). Full tables and an example are in [Graphical asset modding](<graphical-asset-modding.md#Object_Types>). [vanilla-confirmed 1.19.3] `gfx/entities/tanks.gfx`, `gfx/entities/infantry.gfx`, `gfx/entities/mapitems.gfx`

`file` is a path from the game root (`gfx/models/units/tanks/ENG_tank_light.mesh`). The `.anim` files, the `.mesh` and the textures of one model sit together in one folder, and `texture_diffuse` and its siblings give only the file name. [vanilla-confirmed 1.19.3] `gfx/models/units/tanks/`, `gfx/entities/tanks.gfx`

Animation ids in vanilla meshes (12731 `animation` lines) are free names, chosen to match the `state` names of the entity. The most common are `idle` (1141), `move` (783), `attack` (742), `death` (488), `training` (474), `cavalry_idle` and `cavalry_move` (470 each), `retreat` (436) and `support_attack` (434). [vanilla-confirmed 1.19.3] `gfx/entities/*.gfx`
<!-- kit:end id="entity-mesh-notes" -->

### Animation <a id="Animation"></a>

The animation scope contains these attributes:

- **id** is the name of the animation within the pdxmesh.
- **type** is the name of the actual animation defined in an .asset file.

## Adding an Entity <a id="Adding_an_Entity"></a>

Once a mesh is defined, you then need to add an entity definition to use it within script. This is done within a **.asset** file that you need to add within your mod.

Here is a comprehesive example of all possible attributes:

```text
entity = {
    name = "name_of_entity"
    pdxmesh = "mesh_to_use"
    scale = 1.0
    cull_radius = 100

    default_state = "idle"
    get_state_from_parent = yes

    locator = {
        name = "example"
        position = { 0.0 0.0 0.0 }
    }

    state = {
        name = "idle"
        state_time = 0.0

        animation = "idle"
        animation_blend_time = 0.0
        animation_speed = 1.0
        looping = yes

        next_state = "idle"

        chance = 2
        propagate_state = {
            node = "idle"
        }

        event = {
            time = 1.0
            trigger_once = yes

            node = "example_node"
            light=  "example_light"

            particle = "example_particle"
            keep_particle = yes

            sound = {
                soundeffect = "example_soundeffect"
            }
        }
    }

    attach = {
        name = "name"
        <node> = "example_entity"
    }
}
```

- **name** is the name of the entity that is referred to in places such as **ambient_objects.txt**.
- **pdxmesh** is the mesh associated with the entity.
- **state** is a scope added for each animation associated with the mesh, linking the animation to an animation state.
- **locator** is a scope that adds a node to the entity.
- **scale** is a scalar for the size of the entity.
- **cull_radius** is a distance at which the entity is culled from rendering.
- **default_state** is the default animation state for the entity.
- **get_state_from_parent** inherits the state of the parent entity (i.e. used by the weapon entity that is part of a soldier).
- **attach** is a scope that attachs another entity to a skeleton node of the current entity.

Note that the available states depending on where the entity is used (i.e. a unit entity will get combat states, where as a building entity will get building states, etc). All entities share the **idle** state.

<!-- kit:begin id="entity-keys-extra" at="section:Adding_an_Entity" -->
**Kit addition** Entity keys in vanilla that the page does not list. Counts are over the 3439 `entity` blocks. All rows: [vanilla-confirmed 1.19.3] `gfx/entities/*.asset`.

| Key | Uses | Example |
| --- | --- | --- |
| `clone` | 1506 | `clone = "building_nuclear_reactor"` before `name = "building_nuclear_reactor_heavy_water"` |
| `version` | 127 | `version = 1` (a few `version = 2`) |
| `game_data = { texture_anim_speed = ... }` | 169 | an entity level block |
| `cull_radius` | 17 | the page documents it |
| `get_state_from_parent` | 63 | the page documents it |
| `locator = { name position rotation }` | 120 | `rotation` is set in 17 |

An entity that only clones another and sets a new `name` is valid:

```text
entity = {
	clone = "building_nuclear_reactor"
	name = "building_nuclear_reactor_heavy_water"
}
```

[vanilla-confirmed 1.19.3] `gfx/entities/buildings.asset`

What the engine copies on `clone`, and what `version` selects, is not stated in any game file. [unverified] `gfx/entities/units_vehicles.asset`

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

### State <a id="State"></a>

The state scope contains these attributes:

- **name** is the name of the state that a model may enter. All models have an **idle** state.
- **state_time** is the duration of the current state.
- **looping** determines whether this state loops or not.
- **event** is a scope that applies a particle or sound effect.
- **animation** is the animation state (from the pdxmesh) to play.
- **animation_blend_time** is the blend time between the current and the specified animation.
- **animation_speed** is the playback speed of the animation.
- **next_state** sets the next state for the current state.
- **chance** determines the chance of this state entry occuring if it shares its name with multiple other state entries (i.e. training, whether to pushup, jumping jack, etc.)
- **propagate_state** propagates the current state to the specified node.

<!-- kit:begin id="entity-state-correction" at="section:State" -->
**Kit correction** `propagate_state` does not take `node = "idle"`. In vanilla its keys are the names of `attach` entries (`infantry`, `rider`, `cavalry`, `rifle1`, `rifle2`, `lighter`) and the value is the state to put that attached entity in: `propagate_state = { infantry = "move" }`. The `node` form from the page never appears. [vanilla-confirmed 1.19.3] `gfx/entities/units_vehicles.asset`, `gfx/entities/units_infantry.asset`, `gfx/entities/units_cavalry.asset`

State keys used in vanilla but missing from the page: `time_offset` (1), a nested `attach` (9), a nested `scale` (1) and `game_data = { hitmiss_effect = { time = 0.1 type = big } }` on ship states (196). `looping` is written as `no` in 3173 states and `yes` in 16. [vanilla-confirmed 1.19.3] `gfx/entities/_units_battleships_DLC.asset`, `gfx/entities/*.asset`

Most used state names: `idle` (2439), `training` (2156), `move` (1402), `attack` (1377), `retreat` (1198), `defend` (1135), `support_attack` (1095), `death` (456), then aircraft states `crash`, `bomb`, `firebomb`, `explode` and `fire`. `chance` is mostly 1 or 2; it picks between states that share a name, as the page says. [vanilla-confirmed 1.19.3] `gfx/entities/*.asset`
<!-- kit:end id="entity-state-correction" -->

### Event <a id="Event"></a>

The event scope contains these attributes:

- **time** is the duration of the event in seconds.
- **particle** is the particle to display.
- **keep_particle** determines whether the particle persists past the duration of the event.
- **trigger_once** determines whether the event occurs only once.
- **sound** is a scope that applies a sound effect.
- **node** specifies a locator node or model node to set the event position origin to.
- **light** specifies a light to display.

<!-- kit:begin id="entity-event-notes" at="section:Event" -->
**Kit note** Event keys counted over 11012 vanilla `event` blocks: `time` (9381), `particle` (8727), `keep_particle` (8598), `node` (7935), `sound` (4868), `trigger_once` (3961), `light` (466) and `id` (228). `id` is not on the page; it is used by aircraft states (`event = { time = 0.2 id = a_fire }`). [vanilla-confirmed 1.19.3] `gfx/entities/*.asset`, `gfx/entities/units_planes.asset`

`time` behaves as the moment inside the state at which the event fires. One vanilla state fires the same muzzle particle at `time = 0` and again at `time = 14`, so the page's wording "duration of the event" is misleading. [vanilla-confirmed 1.19.3] `gfx/entities/buildings.asset`. The reading as a start time is an inference. [unverified] `gfx/entities/buildings.asset`

- `particle` takes the `name` of a `pdxparticle` in a `.gfx` file, not the `name` of the `particle` in the `.asset` (see [Particle modding](<particle-modding.md>)). [vanilla-confirmed 1.19.3] `gfx/entities/buildings.asset`, `gfx/entities/particles.gfx`
- `light` takes a `light` name from `gfx/entities/map_lights.asset`: `playerlight`, `muzzle_flash`, `cigarette_light`, `nuke_light`, `rifle_muzzle_flash`, `mg_muzzle_flash`, `citylight`, `nuke_big_light`, `alarm_flash`. [vanilla-confirmed 1.19.3] `gfx/entities/map_lights.asset`
- `sound = { soundeffect = <name> }` takes a `soundeffect` name (see [Sound modding](<sound-modding.md>)). `soundeffect` is the only key ever used inside that block (4868 uses). [vanilla-confirmed 1.19.3] `gfx/entities/buildings.asset`

```text
event = { time = 0 node = "mg1" particle = "aa_muzzle_small_particle" keep_particle = yes light = "mg_muzzle_flash" sound = { soundeffect = mechanized_units_mg_fire } }
```

Vanilla event. [vanilla-confirmed 1.19.3] `gfx/entities/buildings.asset`
<!-- kit:end id="entity-event-notes" -->

### Attach <a id="Attach"></a>

- **name** is the name of the attached entity.
- **<node>** is the name of the node from the entities skeleton, and the value is the entity to attach.

<!-- kit:begin id="entity-attach-notes" at="section:Attach" -->
**Kit note** Vanilla has 6163 `attach` lines. The key next to `name` is either a skeleton or locator node name (`Right_Hand_node` 711, `Left_Hand_node` 705, `Root_node_2` 685, `mid_back_node` 572, `Saddle_Node` 241) or a role name for a sub-entity slot (`infantry` 899, `vehicle` 332, `cavalry` 258, `horse` 250, `artillery` 238, `combined` 44, `bike` 40). The value is an entity name. `propagate_state` refers to the same `name`. [vanilla-confirmed 1.19.3] `gfx/entities/units_infantry.asset`, `gfx/entities/units_vehicles.asset`
<!-- kit:end id="entity-attach-notes" -->

### Sound <a id="Sound"></a>

The sound scope contains these attributes:

- **soundeffect** is the sound effect to play.

### Locator <a id="Locator"></a>

The locator scope contains these attributes:

- **name** is the name of the locator node.
- **position** is the position of the location node, with the values being x, y and z co-ordinates.

<!-- kit:begin id="entity-locator-example" at="section:Locator" -->
**Kit note** Vanilla locators give the spots that events point at with `node = "<locator name>"`. A dockyard has two damage locators, and its `damaged` state fires a particle from each:

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

## Adding an Animation <a id="Adding_an_Animation"></a>

Animations for models are added in a **.asset** file found in `/Hearts of Iron IV/gfx/models/` or the sub-folders.

Here is a generic example:

```text
animation = {
    name = "animation_name"
    file = "animation_name.anim"
}
```

- **name** is the name of animation that is then referred to in a **pdxmesh**.
- **file** is the relative filepath to the animation.

<!-- kit:begin id="entity-animation-example" at="section:Adding_an_Animation" -->
**Kit note** `file` is relative to the folder of the `.asset` that holds the block, and the `.anim` files sit in that folder. Vanilla has 1296 `animation` blocks, all with exactly the keys `name` and `file`:

```text
animation = {
	name = "ENG_tank_light_attack_animation"
	file = "ENG_tank_light_attack.anim"
}
```

[vanilla-confirmed 1.19.3] `gfx/models/units/tanks/animation_tanks.asset`
<!-- kit:end id="entity-animation-example" -->

<!-- kit:begin id="entity-where-used" at="bottom" -->
**Kit addition** Where an entity name is used in script, with what vanilla and the documentation show.

- `division_template = { override_model = <entity> }` gives a division template its own model, for example `override_model = CHL_infantry_alt_0_entity` in `common/national_focus/chile.txt` (171 `override_model = <..._entity>` lines in `common/`). [vanilla-confirmed 1.19.3] `common/national_focus/chile.txt`
- Raid outcomes name an entity: `entity = "raid_failed_entity"` in `common/raids/air_raids.txt`. [vanilla-confirmed 1.19.3] `common/raids/air_raids.txt`
- The effects `create_entity`, `destroy_entity`, `set_entity_position`, `set_entity_movement`, `set_entity_rotation`, `set_entity_scale` and `set_entity_animation` act on entities by `id`. Vanilla script never calls `create_entity`. [docs] `documentation/effects_documentation.md`. The zero use count is [vanilla-confirmed 1.19.3] `common/`, `events/`, `history/`
- Buildings use an entity named `building_<building id>`; see [Building modding](<building-modding.md#Models>). [vanilla-confirmed 1.19.3] `gfx/entities/buildings.asset`
<!-- kit:end id="entity-where-used" -->

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list-of-modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on-actions.md>) • [Data structures](<data-structures.md>) • [Flags](<data-structures.md#Flags>) • [Event targets](<data-structures.md#Event_targets>) • [Country tag aliases](<data-structures.md#Country_tag_aliases>) • [Variables](<data-structures.md#Variables>) • [Arrays](<data-structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement-modding.md>) • [AI](<ai-modding.md>) • [AI focuses](<ai-focuses.md>) • [Autonomous states](<autonomy-state-modding.md>) • [Balances of power](<balance-of-power-modding.md>) • [Bookmarks/Scenarios](<bookmark-modding.md>) • [Game rules](<bookmark-modding.md#Game_rules>) • [Buildings](<building-modding.md>) • [Characters and traits](<character-modding.md>) • [Cosmetic tags](<cosmetic-tag-modding.md>) • [Countries](<country-creation.md>) • [Divisions](<division-modding.md>) • [Decisions](<decision-modding.md>) • [Doctrines](<doctrine-modding.md>) • [Equipment](<equipment-modding.md>) • [Events](<event-modding.md>) • [Factions](<faction-modding.md>) • [Ideas](<idea-modding.md>) • [Ideologies](<ideology-modding.md>) • [Military industrial organizations](<military-industrial-organization-modding.md>) • [National focuses](<national-focus-modding.md>) • [Resources](<resources-modding.md>) • [Scripted GUI](<scripted-gui-modding.md>) • [Technologies and doctrines](<technology-modding.md>) • [Units](<unit-modding.md>)
- **Map**: [Map](<map-modding.md>) • [States](<state-modding.md>) • [Supply areas](<supply-areas-modding.md>) • [Strategic regions](<strategic-region-modding.md>)
- **Graphical**: [Interface](<interface-modding.md>) • [Graphical assets](<graphical-asset-modding.md>) • [Posteffects](<posteffect-modding.md>) • [Particles](<particle-modding.md>) • [Fonts](<font-modding.md>)
- **Cosmetic**: [Portraits](<portrait-modding.md>) • [Namelists](<namelist-modding.md>) • [Music](<music-modding.md>) • [Sound](<sound-modding.md>)
- **Other**: [Console commands](<console-commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod-structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection-modding.md>) • [Game rule modding](<game-rule-modding.md>) • [Intelligence operation modding](<intelligence-operation-modding.md>) • [Map mode modding](<map-mode-modding.md>) • [Occupation and resistance modding](<occupation-and-resistance-modding.md>) • [Peace conference modding](<peace-conference-modding.md>) • [Raid modding](<raid-modding.md>) • [Script constant modding](<script-constant-modding.md>) • [Special project modding](<special-project-modding.md>)
