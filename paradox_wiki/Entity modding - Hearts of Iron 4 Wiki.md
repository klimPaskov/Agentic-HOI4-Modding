# Table of contents

- [Adding a Mesh](#adding-a-mesh)
  - [Animation](#animation)
- [Adding an Entity](#adding-an-entity)
  - [State](#state)
  - [Event](#event)
  - [Attach](#attach)
  - [Sound](#sound)
  - [Locator](#locator)
- [Adding an Animation](#adding-an-animation)


---

Entities are definitions used by Hearts of Iron IV to link models with script objects that are used in places such as `ambient_objects.txt`.

Both **.gfx** and **.asset** files are found in /Hearts of Iron IV/gfx/entities/.

Animations **.asset** files are found in /Hearts of Iron IV/gfx/models/.

## Adding a Mesh

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

### Animation

The animation scope contains these attributes:

- **id** is the name of the animation within the pdxmesh.
- **type** is the name of the actual animation defined in an .asset file.

## Adding an Entity

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

- **name** is the name of the entity that is referred to in places such as **ambient\_objects.txt**.
- **pdxmesh** is the mesh associated with the entity.
- **state** is a scope added for each animation associated with the mesh, linking the animation to an animation state.
- **locator** is a scope that adds a node to the entity.
- **scale** is a scalar for the size of the entity.
- **cull\_radius** is a distance at which the entity is culled from rendering.
- **default\_state** is the default animation state for the entity.
- **get\_state\_from\_parent** inherits the state of the parent entity (i.e. used by the weapon entity that is part of a soldier).
- **attach** is a scope that attachs another entity to a skeleton node of the current entity.

Note that the available states depending on where the entity is used (i.e. a unit entity will get combat states, where as a building entity will get building states, etc). All entities share the **idle** state.

### State

The state scope contains these attributes:

- **name** is the name of the state that a model may enter. All models have an **idle** state.
- **state\_time** is the duration of the current state.
- **looping** determines whether this state loops or not.
- **event** is a scope that applies a particle or sound effect.
- **animation** is the animation state (from the pdxmesh) to play.
- **animation\_blend\_time** is the blend time between the current and the specified animation.
- **animation\_speed** is the playback speed of the animation.
- **next\_state** sets the next state for the current state.
- **chance** determines the chance of this state entry occuring if it shares its name with multiple other state entries (i.e. training, whether to pushup, jumping jack, etc.)
- **propagate\_state** propagates the current state to the specified node.

### Event

The event scope contains these attributes:

- **time** is the duration of the event in seconds.
- **particle** is the particle to display.
- **keep\_particle** determines whether the particle persists past the duration of the event.
- **trigger\_once** determines whether the event occurs only once.
- **sound** is a scope that applies a sound effect.
- **node** specifies a locator node or model node to set the event position origin to.
- **light** specifies a light to display.

### Attach

- **name** is the name of the attached entity.
- **<node>** is the name of the node from the entities skeleton, and the value is the entity to attach.

### Sound

The sound scope contains these attributes:

- **soundeffect** is the sound effect to play.

### Locator

The locator scope contains these attributes:

- **name** is the name of the locator node.
- **position** is the position of the location node, with the values being x, y and z co-ordinates.

## Adding an Animation

Animations for models are added in a **.asset** file found in /Hearts of Iron IV/gfx/models/ or the sub-folders.

Here is a generic example:

```text
animation = {
    name = "animation_name"
    file = "animation_name.anim"
}
```

- **name** is the name of animation that is then referred to in a **pdxmesh**.
- **file** is the relative filepath to the animation.

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
