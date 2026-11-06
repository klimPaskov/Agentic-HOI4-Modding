# 3D units with Meshy and Blender

This page is for modders who want their own 3D units on the HOI4 map: soldiers, archers, riders, beasts. Your coding agent does the work through the `hoi4-3d-model-pipeline` skill. This page explains what you need, what happens, and what to do when a step fails.

## What you need

- **A Meshy account on a paid plan or in the Meshy contributor program.** Meshy creates API tasks only for paying accounts. On the free plan every task is refused and nothing is charged.
- **Your Meshy API key.** HOI4 Mod Setup asks for it and keeps it in the Windows credential store.
- **Blender 5.1 or 5.2.** HOI4 Mod Setup can install Blender 5.2.3 for you. A portable Blender in `%LOCALAPPDATA%\Programs` is found too.
- **Windows.** The Meshy and Blender routes are Windows only today.

In HOI4 Mod Setup, tick **3D models workflow**. It installs the pipeline, the pinned Meshy MCP server, the Blender MCP server, Paradox's `io_pdx_mesh` exporter for your Blender, and registers the two MCP servers for your coding client.

## What a unit costs

Prices come from `.tools/3d_pipeline/config/meshy_pricing.json`.

| Unit | Meshy steps | Credits |
| --- | --- | --- |
| Foot unit (soldier, archer, giant, beast) | model 30, remesh 5, rig 5, six animations at 3 each | about 58 |
| Rider of a mounted unit | model 30, remesh 5, rig 5, three animations | about 49 |
| Mount or four-legged beast | model 30 (Blender rigs and animates it) | 30 |
| Mounted unit (rider plus mount) | both of the above | about 79 |

Blender work costs nothing. Your agent asks you once for a credit budget per unit and never pays for a retry.

## Unit types

Pick one type per unit. The type decides the rig, the animations and how the unit is wired. The full list is in `.tools/3d_pipeline/config/unit_types.json`.

| Type | For | Rig | Animations |
| --- | --- | --- | --- |
| `infantry_melee` | swords, axes, maces | Meshy humanoid | sword slash, parry, wounded retreat, fall |
| `spearman` | spears and pikes | Meshy humanoid | spear walk, thrust, two-handed parry |
| `archer` | bows | Meshy humanoid | archery shot, aim and scan, step back with bow |
| `heavy_brute` | giants, trolls, ogres | Meshy humanoid | slow heavy walk, hammer swing, ground stomp |
| `beast_biped` | yeti, ghouls | Meshy humanoid | lumbering walk, two-fist strike, roar |
| `tree_creature` | ents | Meshy humanoid | unsteady walk, ground slam |
| `rider`, `mounted_archer` | the person on a mount | Meshy humanoid, seated by Blender | the upper body plays the clip, the legs stay astride |
| `mount` | horses, camels, dead horses | Blender quadruped with a `Saddle_Node` | idle, trot, charge, rear, gallop, collapse |
| `quadruped_beast` | wolves, war beasts, elephants | Blender quadruped | idle, walk, charge, rear, gallop, collapse |

Every type gets the six land-unit roles: idle, move, attack, defend, retreat and death. Walks use Meshy's in-place clips, so the unit does not slide.

Mounts are built to vanilla's horse size on the map, which is smaller than vanilla infantry. A mounted unit is two jobs: a `mount` and a `rider`. The mount's entity attaches the rider's entity to its `Saddle_Node`, the way vanilla cavalry does, so one horse can carry several kinds of rider.

## Pick units players will see

A division shows the model of its highest-priority sub-unit (`priority` in the unit's `sub_units` entry). A unit that never leads a template, for example archers next to higher-priority infantry, is drawn only when a player builds a template led by it. Before you pay for a model, check that the unit leads at least one starting or AI division template. Spend credits first on units that lead starting divisions.

## What happens

1. **Reference image.** One clean picture of the unit, without weapons in hand and on a plain background. You look at it and approve it.
2. **Model.** Meshy turns the picture into a textured model. Blender imports it, checks it for holes and loose parts, and scales it against vanilla infantry.
3. **Rig and animations.** Meshy rigs humanoids and animates them from its library. Blender rigs four-legged animals itself and seats riders.
4. **Export.** Blender writes the `.mesh`, one `.anim` per role and three DXT5 textures with mip levels, then re-imports them to prove they load.
5. **Checks.** `check_unit_files.py` reads the exported files and stops on anything the game cannot use.
6. **Hand-over.** The files land in the job's `runtime/files` folder with their final names, next to `runtime/registration.md`, which holds the `.gfx`, `.asset` and entity text to paste.
7. **In game.** You or your live-testing setup place the unit and look at it idle, moving and fighting.

## Automatic checks

Run them on a unit's folder at any time:

```
py -3.13 -B .tools/3d_pipeline/check_unit_files.py gfx/models/units/<unit> --unit-type archer --mod-root .
```

| Check | Why |
| --- | --- |
| At most 50 bones, at most 4 bone weights per vertex | The game's shader skins no more (`gfx/FX/pdxmesh.shader`) |
| Triangles within the profile's budget | Big meshes slow the map down |
| Every animation moves only bones the mesh has | Other bones are ignored and the unit freezes |
| Every role has an animation | A missing role shows a frozen pose |
| A mount has a `Saddle_Node` | The rider has nothing to sit on |
| Textures are DXT5 or DXT1 with mip levels | Without mips the zoomed-out map shimmers. Uncompressed textures use four times the memory |
| Normal maps have a black blue channel | The game reads blue in a normal map as glow |
| Specular maps stay about as dull as vanilla's | Shinier maps show as white speckles on the map. The pipeline scales Meshy's metalness and gloss down to vanilla's range |
| A mount's `Saddle_Node` exports without rotation | The game turns the rider with the node, so a turned node tips him over |
| With `--mod-root`: the mesh, every animation, an entity with every state and a sub-unit sprite are registered | Unregistered files never show |

Add `--repair-textures` to convert old uncompressed or unmipped textures in place. When a mount and its rider share one folder, check each with `--stem`, for example `--stem <unit> --unit-type mount` and `--stem <unit>_rider --unit-type rider`.

## When something fails

Ask where a unit stands at any time. This reads files only and costs nothing:

```
py -3.13 -B .tools/3d_pipeline/run_pilot.py --jobs-config <your 3d_jobs.json> --status <unit>
```

It prints the last steps and the exact next command.

| Problem | What to do |
| --- | --- |
| Meshy answers 402 | Your account is on the free plan. Upgrade or join the contributor program. Nothing was charged |
| "Unreconciled submission" | A paid step may have reached Meshy without an answer. Look the task up in Meshy's task list and record it as the message says. Never start the step again by hand |
| The model has holes or loose parts | Look at the previews. Fix it in Blender, or ask your agent for a new reference image and one more model |
| "No library clip still matches its key" | Meshy renamed a library clip. Pick another clip for that role in `unit_types.json` |
| "This animation is no longer available" | Meshy retired a clip it still lists. The pipeline moves to the role's next clip by itself and releases the refused call's credits, because Meshy charges nothing for it. If no clip is left, add one for that role in `unit_types.json` |
| The quadruped rig says it cannot find four legs | The legs touch each other or the ground is uneven. Your agent can pass measured landmarks instead |
| A hanging prop (a maul on the belt, a quiver) smears when the unit walks | Meshy weighted a loose part to the nearest limbs. Add `loose_part_edits` to the job: each rule's box, in fractions of the unit's height (x and y from the body's centre, z from the ground), selects the loose parts inside it, which are dropped (`"action": "drop"`) or given to one bone (`"action": "bind", "bone": "Hips"`). Put the reason in `loose_part_edits_reason`, which the report keeps. Rerun the job. It costs nothing |
| A check fails after export | Read `runtime/files.json` in the job folder. It names the file and the rule |
| A paid step fails | Run the same command again. Steps that succeeded are reused and never paid twice |
