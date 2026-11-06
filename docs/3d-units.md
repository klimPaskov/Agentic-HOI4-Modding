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
7. **Independent review.** `review_unit.py` renders every clip from six sides, including the map camera, and a reviewer who did not make the unit lists every defect it sees. The unit is finished only when that list is empty. See [Independent review](#independent-review).
8. **In game.** You or your live-testing setup place the unit and look at it idle, moving and fighting.

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
| No more open edges, and no larger open loop, than vanilla units | The game hides back faces, so a gap shows the ground through the unit |
| No triangles facing the wrong way, and no part turned inside out | The same culling makes them look like holes from one side |
| No surface joining body parts that move apart, such as a hand fused to a thigh | Every clip tears the join into spikes and webs |
| No frame stretches or squashes the surface more than vanilla clips do | Catches weights leaking across body parts and torn joins in every frame, not only the frames someone looked at |
| Feet stay on the ground in every frame (a dead body may lie anywhere) | Floating and sinking units |
| No seam between the legs whose two sides follow one leg each, unblended | Parting the legs tears the seam open |
| No knee bends backward in any frame | A leg solver can pick the wrong side, and the unit walks like a bird |
| Every clip moves at least as much as the stillest vanilla clip | A near-frozen clip reads as a static pose on the map |
| No two roles of one unit play the same motion | Each role must read as itself: a retreat that is the walk, a defend that is the idle |
| With `--mod-root`: no clip is one another unit of the mod already plays, unless the unit is a reskin of it (`--reskin-of <unit>`) | Every unit has its own animations. Reskins of one base unit, with the same body and rig, may share them |
| With `--mod-root`: the mesh, every animation, an entity with every state and a sub-unit sprite are registered | Unregistered files never show |

The surface and deformation limits are the worst values measured on the game's own soldiers, riders and horses (or on its vehicles, for a unit type with `"calibration_group": "vehicle"`). They live in `.tools/3d_pipeline/config/deformation_calibration.json`. After a game update, measure them again with `calibrate_deformation.py "<game folder>" --out .tools/3d_pipeline/config/deformation_calibration.json`. Never raise a limit by hand to pass a unit: fix the unit.

Add `--verdict <job folder>/evidence/check.json` for a short verdict instead of the full list. It says `pass` and names the review command, `fail` with the exact repair command to run next, or `escalate` when no script can fix a rule, such as a knee that bends backward or a clip shared with another unit, and points to live authoring. `repair_unit.py` and `review_unit.py` print the same kind of verdict, so you can follow a unit from one step to the next.

Add `--repair-textures` to convert old uncompressed or unmipped textures in place. When a mount and its rider share one folder, check each with `--stem`, for example `--stem <unit> --unit-type mount` and `--stem <unit>_rider --unit-type rider`.

## Independent review

Checks count things. They cannot tell you that a cape tears into spikes in the death clip, or that a sword passes through a leg. Look at every clip from every side, and let someone else look, because the person who made a unit sees what they meant to make.

```
py -3.13 -B .tools/3d_pipeline/review_unit.py gfx/models/units/<unit> --mod-root . --out <job folder>/evidence/review
```

It renders each clip at several frames, always including the frames where the surface stretches most and where the unit sits lowest and highest, from front, left, back, right, the map camera and below. Back faces are hidden as in the game and the background is magenta, so any magenta inside the unit is a hole. A dark disc marks the ground. You get one contact sheet per clip and `REVIEW_REQUEST.md`, which holds the reviewer instructions and the quality bar. Each clip also gets a diagnostics sheet at its worst frames, in flat colours that show what the checks measure: yellow to red where the surface stretches or squashes, cyan at the rim of a hole, blue below the ground. It shows the reviewer where to look.

Give `REVIEW_REQUEST.md` and the sheets, and nothing else, to a reviewer that has not seen how the unit was made: a new agent session or subagent, or a friend. Do not tell it what you already fixed or what you think is fine. Save its whole reply and record it:

```
py -3.13 -B .tools/3d_pipeline/review_unit.py gfx/models/units/<unit> --out <job folder>/evidence/review --record reply.md
```

The unit passes only on `VERDICT: pass` with no listed defect. After a fail, fix the cause, export again and ask a new reviewer. Keep the replies: they are the record that the unit was looked at.

The renders need Blender with io_pdx_mesh, which HOI4 Mod Setup installs. Set `BLENDER_EXE` to use a particular Blender.

## Repair an exported unit for free

`repair_unit.py` fixes the mesh faults the checks name, in Blender, without Meshy:

```
py -3.13 -B .tools/3d_pipeline/repair_unit.py gfx/models/units/<unit> --out <job folder>/repair --repairs winding bridges
```

| Repair | Fixes |
|---|---|
| `winding` | Triangles facing the wrong way and inside-out parts (UNIT-WINDING, UNIT-INSIDE-OUT) |
| `bridges` | Surfaces fusing body parts that move apart, such as an arm pressed into the hips. The joining faces are cut and both sides are closed (UNIT-BRIDGE, and the stretch it causes). A bridge inside one continuous skin, such as an ear root between head and shoulder, is not cut: the report lists it under `weight_seams`, and it needs blended weights instead |
| `holes` | Small open loops, up to `--max-hole-edges` edges (UNIT-HOLE) |
| `weights` | Hard weight edges inside one skin, and a crotch whose two sides follow one leg each (UNIT-SEAM): the existing weights are blended over a few rings around each seam, then each vertex keeps at most four influences |
| `ground` | Feet off or under the ground in a clip: the root bone's existing translation keys are shifted so the lowest point meets the ground in every frame. A death clip is only lifted where it sinks (UNIT-ANIM-GROUND). Needs no Blender |

Repairs never make new bones, a new weight set or new keyframes: a clip that does not read as its role, or a prop that passes through the body, needs its motion authored again in Blender. It writes the repaired copy to `<job folder>/repair/files` and leaves `gfx/` alone. The skeleton, materials and the weights of every vertex it does not cut stay as they were, so the unit's `.anim` files still play. `repair_report.json` lists what changed and the check results before and after. Review the copy with `review_unit.py`, and copy it into `gfx/` only after a fresh reviewer passes it.

## Author animations live in Blender

Some units need motion no library clip gives them: a body with wings, extra arms or a tail, a creature on which human clips look wrong, a project that wants every unit's clips to be its own, or a clip that failed the review twice. Then your agent poses the unit by hand in a live Blender session, through an interactive Blender MCP, one key at a time, and looks at every key before it keeps it. It costs nothing.

The kit gives that session helpers in `.tools/3d_pipeline/authoring/live_helpers.py`: solve a leg with the knee toward the toes, put a hand on a point with a temporary IK, plant a foot on the ground at a key, spread a lean down the spine, weight a crotch seam across the pelvis and both thighs, keep a hand on a weapon wherever the weapon moves, and render the views a reviewer sees. They never make keys on their own. The agent's guide is the skill's `references/live-authoring.md`.

The result goes through the same checks and the same independent review as any other unit.

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
