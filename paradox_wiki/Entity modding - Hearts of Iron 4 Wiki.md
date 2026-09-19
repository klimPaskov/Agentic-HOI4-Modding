# Entity modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Entity modding", captured 2026-09-19.*

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

### Event <a id="Event"></a>

The event scope contains these attributes:

- **time** is the duration of the event in seconds.
- **particle** is the particle to display.
- **keep_particle** determines whether the particle persists past the duration of the event.
- **trigger_once** determines whether the event occurs only once.
- **sound** is a scope that applies a sound effect.
- **node** specifies a locator node or model node to set the event position origin to.
- **light** specifies a light to display.

### Attach <a id="Attach"></a>

- **name** is the name of the attached entity.
- **<node>** is the name of the node from the entities skeleton, and the value is the entity to attach.

### Sound <a id="Sound"></a>

The sound scope contains these attributes:

- **soundeffect** is the sound effect to play.

### Locator <a id="Locator"></a>

The locator scope contains these attributes:

- **name** is the name of the locator node.
- **position** is the position of the location node, with the values being x, y and z co-ordinates.

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

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
