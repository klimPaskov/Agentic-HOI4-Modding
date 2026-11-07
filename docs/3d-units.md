# 3D units with Meshy and Blender

This page is for modders who want their own 3D units on the HOI4 map: soldiers, archers, riders, beasts and vehicles. Your coding agent does the work through the `hoi4-3d-model-pipeline` skill. You approve the picture and the credit budget, and you look at the result. This page explains what you need, what each step does, and what to do when one fails.

## What it is

Two routes make a unit. Both end in the same checks and the same independent review.

| Route | Used for | How it works |
| --- | --- | --- |
| Default | Soldiers, archers, riders, giants, mounts, four-legged beasts | Meshy makes the model from one picture, then rigs and animates humanoids from its clip library. The kit's scripts check, repair and fit the result the same way every time. Each step is one command that prints a one-line verdict |
| Live authoring in Blender | Whatever a verdict escalates: clips that do not read as their role, a body no preset fits (wings, extra arms, tentacles), vehicles | Your agent poses the unit key by key in a live Blender session through the Blender Lab MCP, and looks at every key before keeping it |

A verdict is `pass` (it names the next command), `fail` (it names the free fix to run) or `escalate` (no script can fix it, so the unit goes to [live authoring](#author-animations-live-in-blender)). Run the command the verdict names and keep going until the unit passes the review.

## Setup

The Meshy and Blender routes are Windows only today. In HOI4 Mod Setup, tick **3D models workflow**. It installs:

- The kit's 3D pipeline (`.tools/3d_pipeline/`) and the `hoi4-3d-model-pipeline` skill.
- Blender 5.2.3, when no Blender 5.1 or 5.2 is installed. A portable Blender in `%LOCALAPPDATA%\Programs` is found too. Set `BLENDER_EXE` to use a particular one.
- The `io_pdx_mesh` add-on for that Blender, which reads and writes HOI4's `.mesh` and `.anim` files.
- The pinned Meshy MCP server and the Blender Lab MCP server, registered for your coding client.

**The Meshy key.** Meshy creates API tasks only for accounts on a paid plan or in the Meshy contributor program. On the free plan every task is refused with HTTP 402 and nothing is charged, although the balance still shows the free monthly credits. HOI4 Mod Setup asks for your API key and keeps it in the Windows credential store.

**Without Meshy.** No free step makes a new model from a picture. Every step after the paid ones needs no key: the checks, the hole check, the repairs, the weapon fit, the review and live authoring all run on a model you already have. A static building can be built and textured in Blender with no provider at all (see [Other model kinds](#other-model-kinds)).

## What a unit costs

Prices come from `.tools/3d_pipeline/config/meshy_pricing.json`.

| Unit | Meshy steps | Credits |
| --- | --- | --- |
| Foot unit (soldier, archer, giant, beast) | model 30, remesh 5, rig 5, six animations at 3 each | about 58 |
| Rider of a mounted unit | model 30, remesh 5, rig 5, three animations | about 49 |
| Mount or four-legged beast | model 30, remesh 5 (Blender rigs and animates it) | 35 |
| Mounted unit (rider plus mount) | both of the above | about 84 |

A held weapon is its own model job, priced from the same file. A vehicle pays only for Meshy's model steps: Meshy cannot rig it, so it is rigged and animated in Blender.

Every step after the paid ones is free: the body and hole checks, the weapon fit, the file checks, the repairs, the review and live authoring. Your agent asks you once for a credit budget per unit and never pays for a retry. To see what a job has spent:

```
py -3.13 -B .tools/3d_pipeline/run_pilot.py --credits-report <job folder>
```

**Spend credits where players look.** A division shows the model of its highest-priority sub-unit (`priority` in the unit's `sub_units` entry). A unit that never leads a template, for example archers next to higher-priority infantry, is drawn only when a player builds a template led by it. Before you pay for a model, check that the unit leads at least one starting or AI division template, and pay first for units that lead starting divisions.

## The route step by step

Run every command from the repository root. Your agent writes the job registry (`3d_jobs.json`) with one entry per unit: its `unit_type`, `credit_budget` and `anatomy`. `<unit folder>` is the newest copy of the unit that passed its check (see step 11).

### 1. Reference image

One clean picture of the unit, without weapons in hand and on a plain background. A unit that will hold a weapon has its hands closed in fists, because Meshy's rig has no finger bones and an open hand cannot be posed into a grip later. A rider and its mount are two pictures and two jobs. You look at the picture, approve it, and answer the anatomy questions in `.tools/3d_pipeline/config/body_presets.json` (legs, arms, wings, a tail, extra limbs, a vehicle, a rider on a mount). They go into the job as `anatomy`.

### 2. Clip plan (free)

Two units of the same type would play the same library clips, and players notice. Only reskins of one base unit (the same body and rig with a different look, such as a winter uniform) may share them. Plan the clips before any is paid for:

```
py -3.13 -B .tools/3d_pipeline/plan_clips.py --jobs-config <your 3d_jobs.json> --write
```

It goes through your jobs in order and gives each role the first candidate clip of the unit type that no other unit plays yet. A job with `"reskin_of": "<base job>"` gets exactly its base's clips, and a job that lists its own `required_actions` keeps them. When every candidate for a role is taken, the verdict escalates and names the unit and the role: author that clip in Blender, add another candidate to the unit type in `unit_types.json`, or decide that the units may share. Without `--write` it only reports. A registry with `"animation_policy": "authored"` plans no library clip and lists every role for live authoring.

### 3. Model (paid)

```
py -3.13 -B .tools/3d_pipeline/run_pilot.py --jobs-config <your 3d_jobs.json> --phase candidate <unit>
```

Meshy turns the picture into a textured model. Blender imports it, scales it against vanilla infantry and records its open edges. Holes are judged in the next step.

### 4. Body and hole check (free)

```
py -3.13 -B .tools/3d_pipeline/measure_body.py <job folder>
py -3.13 -B .tools/3d_pipeline/check_holes.py <job folder>/provider/downloads/generation_model.glb --out <job folder>/evidence/holes
```

`measure_body.py` checks that the model fits the job's unit type (see [Check the body before you rig it](#check-the-body-before-you-rig-it)). When it passes, its verdict names `check_holes.py` on the same model, which looks for holes a player would see (see [Holes the player sees](#holes-the-player-sees)). A hole is cheapest to fix now, before the rig. Pay for nothing more until both pass.

### 5. Rig, animations and export (paid)

```
py -3.13 -B .tools/3d_pipeline/run_pilot.py --jobs-config <your 3d_jobs.json> <unit>
```

Meshy rigs humanoids and animates them with the planned library clips. Blender rigs four-legged animals itself and seats riders. Blender then writes the `.mesh`, one `.anim` per role at 30 frames a second, and three DXT5 textures with mip levels, and imports them again to prove they load. Steps that already succeeded are reused and never paid twice.

### 6. Weapon in hand (free)

An armed unit's weapon is a separate model. `fit_prop.py` fits it to the hand against every clip and binds it there (see [Put the weapon in the hand](#put-the-weapon-in-the-hand)).

### 7. File checks (free)

```
py -3.13 -B .tools/3d_pipeline/check_unit_files.py <unit folder> --unit-type <type> --mod-root . --verdict <job folder>/evidence/check.json
```

It reads the exported files (see [Automatic checks](#automatic-checks)). Its verdict names the repair to run, or escalates. When it passes, it names the hole check and then the review.

### 8. Hole check (free)

```
py -3.13 -B .tools/3d_pipeline/check_holes.py <unit folder> --out <job folder>/evidence/holes
```

The same check as step 4, now at rest and in every clip.

### 9. Free repair

`repair_unit.py` fixes the mesh faults the checks name, in Blender, without Meshy. The verdict gives the exact command, for example:

```
py -3.13 -B .tools/3d_pipeline/repair_unit.py <unit folder> --out <job folder>/repair --repairs winding holes
```

| Repair | Fixes |
| --- | --- |
| `winding` | Triangles facing the wrong way and inside-out parts (UNIT-WINDING, UNIT-INSIDE-OUT) |
| `bridges` | Surfaces fusing body parts that move apart, such as an arm pressed into the hips. The joining faces are cut and both sides closed (UNIT-BRIDGE). A bridge inside one continuous skin, such as an ear root, is not cut but listed under `weight_seams` for `weights` |
| `holes` | Open loops of at most `--max-hole-edges` edges, 16 by default. The check suggests 32 (UNIT-HOLE) |
| `weights` | Hard weight edges inside one skin, and a crotch whose two sides follow one leg each (UNIT-SEAM). Weights are blended over a few rings, then each vertex keeps at most four influences |
| `ground` | Feet off or under the ground: the root's translation keys are shifted so the lowest point meets the ground in every frame. A death clip is only lifted where it sinks (UNIT-ANIM-GROUND). Needs no Blender |

Repairs never make new bones, a new weight set or new keyframes. The skeleton, materials and the weights of every vertex not cut stay as they were, so the `.anim` files still play. The copy goes to `<job folder>/repair/files`, and `repair_report.json` lists what changed with the check results before and after. Nothing under `gfx/` changes. Mesh repairs come before the weapon: when a repair is needed, run it, then fit the weapon again on the repaired copy (a refit replaces the old weapon).

### 10. Independent review (free)

`review_unit.py` renders every clip, and a reviewer who did not make the unit lists every defect it sees. The unit is finished only when that list is empty (see [Independent review](#independent-review)).

### 11. Hand-over and in game

The export lands in the job's `runtime/files` folder under its final names, next to `runtime/registration.md`, which holds the `.gfx`, `.asset` and entity text to paste. Each later step writes a full copy of the unit to its own folder (`<job folder>/props/files`, `<job folder>/repair/files`). The newest copy that passed its check is the one you review. Copy it into `gfx/` only after a fresh reviewer passes it. Then you, or your live-testing setup, place the unit in game and look at it idle, moving and fighting.

## Unit types and bodies

Pick one type per unit in the job's `unit_type`. The type sets the rig, the clips and how the unit is wired. The full list is in `.tools/3d_pipeline/config/unit_types.json`.

| Type | For | Body | Rig | Clips |
| --- | --- | --- | --- | --- |
| `infantry_melee` | swords, axes, maces | humanoid | Meshy humanoid | sword slash, parry, wounded retreat, fall |
| `spearman` | spears and pikes | humanoid | Meshy humanoid | spear walk, thrust, two-handed parry |
| `archer` | bows | humanoid | Meshy humanoid | archery shot, aim and scan, step back with bow |
| `heavy_brute` | giants, trolls, ogres | large biped | Meshy humanoid | slow heavy walk, hammer swing, ground stomp |
| `beast_biped` | yeti, ghouls | large biped | Meshy humanoid | lumbering walk, two-fist strike, roar |
| `tree_creature` | ents | large biped | Meshy humanoid | unsteady walk, ground slam |
| `rider`, `mounted_archer` | the person on a mount | humanoid | Meshy humanoid, seated by Blender | the upper body plays the clip, the legs stay astride |
| `mount` | horses, camels, dead horses | quadruped | Blender quadruped with a `Saddle_Node` | idle, trot, charge, rear, gallop, collapse |
| `quadruped_beast` | wolves, war beasts, elephants | quadruped | Blender quadruped | idle, walk, charge, rear, gallop, collapse |
| `vehicle` | tanks, armoured cars, other wheeled or tracked units | none | live in Blender | idle, drive, fire, brace, reverse, wreck |

Every type gets the six land-unit roles: idle, move, attack, defend, retreat and death. Most Meshy roles list two library candidates, so the clip plan can give two units of one type different clips. Walks use Meshy's in-place clips, so the unit does not slide. A `vehicle` has `calibration_group: vehicle`: its checks use vanilla's tanks and trucks as the limit, not its soldiers.

Mounts are built to vanilla's horse size on the map, which is smaller than vanilla infantry. A mounted unit is two jobs, a `mount` and a `rider`. The mount's entity attaches the rider's entity to its `Saddle_Node`, the way vanilla cavalry does, so one horse can carry several kinds of rider.

### Check the body before you rig it

The body column names a body preset in `.tools/3d_pipeline/config/body_presets.json`. `measure_body.py` counts the feet on the ground and measures the torso and the reach of the lower body, then says which preset the model fits and how sure it is. It measures the body only, not separate plates, a quiver or a weapon. It fails a model with pieces floating apart from the body, so you drop them before paying for the rig. It passes when the job's unit type uses that preset. It fails when they disagree, for example a `beast_biped` job whose model came out on four legs, and names the unit types that fit. It escalates when no preset fits, for example a body with wings, extra arms or tentacles, which is rigged and animated live in Blender. It reads files only.

The anatomy you gave in step 1 tells the check what a measurement cannot see: `"anatomy": {"legs": 2, "arms": 2, "wings": false, "tail": false, "extra_limbs": false, "vehicle": false, "rider_on_mount": false}`. When you know better than the measurement, set `"body_preset"` in the job and say why in `"body_preset_reason"`.

## Automatic checks

Run them on a unit's folder at any time with the command in step 7. Without `--verdict` it lists every finding.

| Rule | Check | Why |
| --- | --- | --- |
| UNIT-BONES, UNIT-INFLUENCES | At most 50 bones, at most 4 bone weights per vertex | The game's shader skins no more (`gfx/FX/pdxmesh.shader`) |
| UNIT-TRIANGLES, UNIT-STREAM-VERTICES | Triangles within the profile's budget, at most 65,535 vertices per stream | Big meshes slow the map down |
| UNIT-ANIM-JOINTS | Every animation moves only bones the mesh has | Other bones are ignored and the unit freezes |
| UNIT-ANIM-FPS | Every clip of a soldier, rider or creature plays at 30 frames a second | Vanilla's do, and Paradox's own exporter knows only 15, 30 and 60. A Blender scene from factory settings runs at 24, so a clip keyed for 30 and written at 24 plays a quarter too slowly. The kit's exports retime to 30 and keep each clip's length in seconds |
| UNIT-ROLE-MISSING | Every role has an animation | A missing role shows a frozen pose |
| UNIT-NODE-MISSING, UNIT-NODE-ORIENTATION | A mount has a `Saddle_Node`, exported without rotation | The rider has nothing to sit on, and a turned node tips him over |
| UNIT-DDS-MIPS, UNIT-DDS-FORMAT | Textures are DXT5 or DXT1 with mip levels | Without mips the zoomed-out map shimmers. Uncompressed textures use four times the memory |
| UNIT-DDS-EMISSIVE | Normal maps have a black blue channel | The game reads blue in a normal map as glow |
| UNIT-DDS-SHINY | Specular maps stay about as dull as vanilla's | Shinier maps show as white speckles. The pipeline scales Meshy's metalness and gloss down to vanilla's range |
| UNIT-HOLE | No more open edges, and no larger open loop, than vanilla units | The game hides back faces, so a gap shows the ground through the unit |
| UNIT-WINDING, UNIT-INSIDE-OUT | No triangles facing the wrong way, and no part turned inside out | The same culling makes them look like holes from one side |
| UNIT-NORMALS | No larger share of corner normals pointing against their faces than vanilla's worst | They shade as pale flat facets |
| UNIT-BRIDGE | No surface joining body parts that move apart, such as a hand fused to a thigh | Every clip tears the join into spikes and webs |
| UNIT-ANIM-STRETCH | No frame stretches or squashes the surface more than vanilla clips do | Catches weights leaking across body parts and torn joins in every frame |
| UNIT-ANIM-GROUND | Feet stay on the ground in every frame (a dead body may lie anywhere) | Floating and sinking units |
| UNIT-SEAM | No seam between the legs whose two sides follow one leg each, unblended | Parting the legs tears the seam open |
| UNIT-ANIM-KNEE | No knee bends backward in any frame | A leg solver can pick the wrong side, and the unit walks like a bird |
| UNIT-ANIM-STILL | Every clip moves at least as much as the stillest vanilla clip | A near-frozen clip reads as a static pose |
| UNIT-ANIM-SPIN | No joint turns farther in one frame than vanilla's fastest (37 degrees for soldiers, riders and creatures) | Keys on opposite sides of the quaternion sphere make Blender turn the long way, and a limb or polearm sweeps through the ground or the head in a frame or two |
| UNIT-LOOSE-PART | Every separate part (a strap, a plate, a quiver) is skinned and stays on the body in every frame, as close as vanilla's `GER_infantry` and `cavalry_horse` parts do. Any number of parts is fine. A held prop (a separate shape bound wholly to one bone) is one part however many pieces it has, judged against the hand that holds it | A part that floats off the body, or slides away when the unit moves, looks broken at every zoom |
| UNIT-PROP-CLIP (warning) | Names the frames in which a held prop goes inside the body, with the holding hand and forearm left out, in-betweens included | A polearm can swing through a head or a leg between two clear keys |
| UNIT-ANIM-SAME | No two roles of one unit play the same motion (a rider's idle, move and retreat may, since the mount's gait carries it) | Each role must read as itself |
| UNIT-ANIM-SHARED | With `--mod-root`: no clip is one another unit of the mod already plays, unless this unit is its reskin (`--reskin-of <unit>`) | Every unit has its own animations |
| UNIT-REG-* | With `--mod-root`: the mesh, every animation, an entity with every state and a sub-unit sprite are registered | Unregistered files never show |

The surface and motion limits are the worst values measured on the game's own units of the same group: `organic` for soldiers, riders, mounts and animals, `vehicle` for tanks, guns and trucks, `air_naval` for planes and ships. They live in `.tools/3d_pipeline/config/deformation_calibration.json`. After a game update, measure them again with `calibrate_deformation.py "<game folder>" --out .tools/3d_pipeline/config/deformation_calibration.json`. Never raise a limit by hand to pass a unit: fix the unit.

`--verdict <file>` gives the short verdict instead of the full list. It escalates a rule no script fixes, such as a knee that bends backward or a clip another unit plays. `--repair-textures` first rewrites uncompressed or unmipped textures as DXT5 with mips. When a mount and its rider share one folder, check each with `--stem`, for example `--stem <unit> --unit-type mount` and `--stem <unit>_rider --unit-type rider`.

### Holes the player sees

A missing face, a face turned the wrong way, or a one-sided sheet seen from behind shows the ground through the unit. An open-edge count cannot tell those from the open edges a model keeps on trims, plates and straps that never show, so the rigged unit profiles judge holes by looking (`"holes": "silhouette"`). The model check in step 3 only records open edges. `check_holes.py` takes a unit folder or a provider `.glb` (steps 4 and 8).

It renders the unit in Blender from 17 views (eight around it, low and high, and the map camera), at rest and at several frames of every clip, once with back faces hidden and once with them shown. Pixels that only back faces cover are holes. Vanilla shows a few specks too, such as a sleeve seen edge-on, so the unit passes when its largest patch is no larger than the largest `GER_infantry` and `cavalry_horse` show the same way: 58 pixels in a death clip and 50 in every other clip, at the 256-pixel tile size. Death clips have their own limit, because a body lying down shows larger specks from low views. The 50 comes from the horse's one-sided reins. A `.glb` is checked at rest, before the rig.

`sheets/holes_worst.png` shows the worst views, the unit grey and the holes red. A failing verdict names the free `repair_unit.py --repairs winding holes`. The limits live in `.tools/3d_pipeline/config/silhouette_calibration.json`. After a game update, measure them again with `calibrate_holes.py "<game folder>" --work <scratch folder>`, which takes about half an hour.

### Put the weapon in the hand

Soldiers, riders, giants and other armed units hold their weapon, which is generated as a separate model. `fit_prop.py` puts it in the hand:

```
py -3.13 -B .tools/3d_pipeline/fit_prop.py <unit folder> --prop <weapon job>/provider/downloads/generation_model.glb --bone RightHand --length 0.55 --grip 0.15 --out <job folder>/props
```

It scales the weapon to `--length` of the unit's height and puts its grip (`--grip` of its length from the butt) in the palm. A smart-topology prop that arrives in many small pieces keeps them: pieces within 3 % of the prop's size of each other chain into one prop, and only lone fragments are dropped. It tries 42 directions over every clip and keeps the one whose far end least often passes through the body or into the ground. Then it binds the weapon to the hand bone and writes the unit with the weapon's three textures to `<job folder>/props/files`. The clips are not touched. Running it again on the same folder replaces the weapon it fitted before.

The verdict passes when the weapon never goes below the ground and passes through the body in at most 2 % of its sampled points. It also writes `<job folder>/props/registration_prop.md`, the `meshsettings` block to paste into the unit's `pdxmesh`. If no direction clears the clips, try a shorter `--length` (0.4 clears most heads and hips), then another `--grip` between 0.1 and 0.3, or `--butt low`. A weapon held in both hands always needs live work for the second hand.

### Independent review

Checks count things. They cannot tell you that a cape tears into spikes in the death clip, or that a sword passes through a leg. Look at every clip from every side, and let someone else look, because the person who made a unit sees what they meant to make.

```
py -3.13 -B .tools/3d_pipeline/review_unit.py <unit folder> --mod-root . --out <job folder>/evidence/review
```

It renders each clip from front, left, back, right, the map camera and below, at evenly spaced frames plus the frames where the surface stretches most and where the unit sits lowest and highest. Back faces are hidden as in the game on a magenta background, so magenta inside the unit is a hole, and a dark disc marks the ground. Each clip also gets a diagnostics sheet in flat colours: yellow to red where the surface stretches or squashes, cyan at an open edge, blue below the ground. It writes `REVIEW_REQUEST.md` with the reviewer instructions and the quality bar. Keep `--out` in the job folder, never under `gfx/`, or the renders ship with the mod.

Give `REVIEW_REQUEST.md` and the sheets, and nothing else, to a reviewer that has not seen how the unit was made: a new agent session, a subagent or a friend. Do not tell it what you fixed or what you think is fine. Save its whole reply and record it:

```
py -3.13 -B .tools/3d_pipeline/review_unit.py <unit folder> --out <job folder>/evidence/review --record reply.md
```

The unit passes only on `VERDICT: pass` with `DEFECTS: none`. Any listed defect fails it. After a fail, fix the cause, export again and ask a new reviewer. Keep every reply as the record that the unit was looked at.

### Review rounds

The bar stays at zero findings (decision 3D-7). Rounds converge only when every reviewer gets the same request, and the camera angles never change between rounds:

- **Fixed notes.** If part of the unit's look could pass for a defect, such as a torn hem or torn wing membranes, say so once in a notes file in the job folder and pass it every round with `--note-file <job folder>/review_notes.md` (or `--note "..."`). The reviewer still judges everything the note does not name, including any hole in the body.
- **The checklist.** The reviewer goes through the quality bar item by item and ends with a `CHECKLIST:` block. A reply that skips an item is recorded as a fail.
- **Changed clips, then a full round.** After you fix some clips, `--clips attack death` renders only those and the rest pose, and the reviewer judges only them. A unit is accepted only after a full round, without `--clips`, by a new reviewer. When an intermediate round passes, the verdict names that full round.
- **Close-ups.** A reviewer can misread a small dark feature seen side-on, such as a large black eye read as an open mouth. A closed mesh with no winding conflict has no hole there. Name the feature in the notes and render with `--size 768`.

## When the reviewer finds defects

The checks pass anything within vanilla's limits, so a reviewer can still see defects:

| The reviewer sees | Fix |
| --- | --- |
| A hole (magenta, red on `holes_worst.png`, or a cyan rim on the diagnostics sheet) | `repair_unit.py ... --repairs winding holes --max-hole-edges 32`, then check the copy. Holes left after that need faces rebuilt in Blender, or a new model |
| Surface that tears or smears where two body parts meet, red on the diagnostics sheet in every clip | `repair_unit.py ... --repairs bridges weights` |
| A foot above or below the ground | `repair_unit.py ... --repairs ground` |
| The weapon through the head or body | `fit_prop.py` again on the same copy, first with a shorter `--length` such as 0.4, then another `--grip` between 0.1 and 0.3. A two-handed hold is made live |
| A part that tears or crushes only in some clips (a death or an attack that twists the torso hard), or a clip that does not read as its role | No script fixes the motion itself. Author those clips live in Blender, or ask before paying for other clips |

Fix the free ones first, in this order: the mesh repairs, then the weapon. Render again and ask a new reviewer, then take what is left to Blender.

### Author animations live in Blender

Some units need motion no library clip gives them: a body with wings, extra arms or a tail, a creature on which human clips look wrong, a vehicle, a project that wants every clip to be its own, or a clip that failed review twice. Your agent then poses the unit in a live Blender session through the Blender Lab MCP, one key at a time, and looks at every key before it keeps it. It costs nothing.

The kit's helpers in `.tools/3d_pipeline/authoring/live_helpers.py` turn, place, measure, render and key only what the agent names. They solve a leg with the knee toward the toes, put a hand on a point with a temporary IK, plant a foot, spread a lean down the spine, weight a crotch seam, keep a hand on a weapon wherever it moves, and render the reviewer's views. `export_clip` writes a clip over the action's own frame range at 30 frames a second. `normalize_quaternion_keys` flips keys that would make a joint turn the long way. `stretch_share` gives the share of edges the stretch check counts at a frame. `lowest_regions` lists the lowest point of each body region and prop, to find what holds a dead body up. `clear_sharp_faces` removes import flags that push a stream past 65,535 vertices.

The agent's guide is the skill's [live authoring reference](../.claude/skills/hoi4-3d-model-pipeline/references/live-authoring.md), including vehicles (wheel pivots, fused rigid parts, turret traverse). The result goes through the same checks and the same review as any other unit.

## Other model kinds

Units are the tested route. For other models, only the parts below have been proven, each on one model, outside the unit scripts.

**Buildings and landmarks (proven on one model).**

- A building can be textured with no image: one joined mesh, procedural Blender materials, smart UV project and packed islands, then Cycles bakes colour, ambient occlusion, a tangent normal map and the specular maps, packed for the PDX shader. A whole castle baked in about 40 seconds.
- Blender's Brick Texture node samples only two axes, so walls facing one way come out as vertical stripes. Pick the projection per face by its dominant normal axis (triplanar).
- `io_pdx_mesh` refuses faces with more than four corners ("Tangent space can only be computed for tris/quads"). Triangulate before export.
- Every landmark needs a second `collision` shape with the material shader `Collision`. Vanilla landmarks have one 8-vertex box.
- If your mod's state history or `map/buildings.txt` is generated by a tool, do not edit it by hand. Add a new spawn point, keep automatic nudging on, and place the building with an `on_startup` effect that runs `set_building_level` in state scope with the province given. Keep the map rows in a note for the generator.

**Ships (proven on one model).**

- Rebuild vanilla's ship contract exactly, measured from vanilla's destroyer, support ship, freighter, light cruiser and battleship: bow toward -Y, waterline at z = 0, a `root` bone (0,0,0 to 0,0.05,0) with a child `ship` bone (0,0,0.363 to 0,0.25,0.363), every vertex weighted 1.0 to `ship`, mesh data named `<object>Shape` (the `meshsettings` name), material `PDXmat_<object>Shape` with `PdxMeshAdvanced`, the locators `front_moving_water_effect`, `back_moving_water_effect` and `miss_effect_*` as plain empties, `hit_effect_locator1` and `hit_effect_locator2` parented to `ship`, and a `pCube1` collision box. Export with the skeleton option on. That round-trips cleanly through `io_pdx_mesh`.
- Give UV space by part, not evenly. Scale each island to a density by material (hull sides 2.0, sail 1.6, deck 1.0, oars 0.7, underwater hull 0.5), but floor every island at about 0.7 of the reference: islands under a pixel bake black.
- Bake ambient occlusion with 128 samples. 16 leaves speckles along thin painted bands.
- A sail can be a thin closed loft with its emblem drawn in the material from the object's coordinates. It bakes crisp at 1024 with no hand UV and shows from both sides without relying on culling.

**Planes.** Not yet covered.

**Textures for any 3D model.** Use DXT5 with a full mip chain. The 2D image tool (`convert_to_dds.py`) writes uncompressed BGRA with one mip level, which suits interface images but not models. Put the `.dds` files in the model's folder and run `check_unit_files.py <folder> --repair-textures`, which rewrites them as DXT5 with mips and clears a normal map's blue channel.

## Known limits

- **Two-handed polearms.** A polearm held rigidly in one hand fails two-handed library swings: it crosses the head and torso and the free hand flails. There is no two-handed grip step yet. Pick one-handed clips, or fit a shorter shaft gripped near its centre.
- **A weapon sinking in a death clip.** No free repair lifts a held prop out of the ground yet. Run `fit_prop.py` again (a higher `--ground-weight`, such as 40 instead of 10, cleared it on one unit), or turn the wrist live in Blender.
- **Torso twist.** Library clips often fail review where the torso twists hard, in attacks and deaths. Expect some live authoring.
- **Planes** are not covered.
- **UNIT-PROP-CLIP** reads a point behind an open, one-sided sheet such as a cape as inside the body. Look at the named frames before changing a clip.
- **Review rounds** converge only with fixed notes and scoped rounds. Without them each fresh reviewer raises new minor items.

## When something fails

Ask where a unit stands at any time. This reads files only, costs nothing, and prints the last steps and the exact next command:

```
py -3.13 -B .tools/3d_pipeline/run_pilot.py --jobs-config <your 3d_jobs.json> --status <unit>
```

| Problem | What to do |
| --- | --- |
| Meshy answers 402 | Your account is on the free plan. Upgrade or join the contributor program. Nothing was charged |
| "Unreconciled submission" | A paid step may have reached Meshy without an answer. Look the task up in Meshy's task list and record it as the message says. Never start the step again by hand |
| A paid step fails | Run the same command again. Steps that succeeded are reused and never paid twice |
| The body or hole check fails on the model | Read the verdict. Change `unit_type`, drop floating pieces, or ask for a new reference image and one more model |
| "No library clip still matches its key" | Meshy renamed a library clip. Pick another clip for that role in `unit_types.json` |
| "This animation is no longer available" | Meshy retired a clip it still lists. The pipeline moves to the role's next clip by itself and releases the refused call's credits. If no clip is left, add one for that role in `unit_types.json` |
| The quadruped rig cannot find four legs | The legs touch each other or the ground is uneven. Your agent can pass measured landmarks instead |
| A hanging prop (a maul on the belt, a quiver) smears when the unit walks | Meshy weighted a loose part to the nearest limbs. Add `loose_part_edits` to the job: each rule's box, in fractions of the unit's height (x and y from the body's centre, z from the ground), selects the loose parts inside it, which are dropped (`"action": "drop"`) or given to one bone (`"action": "bind", "bone": "Hips"`). Put the reason in `loose_part_edits_reason`. Rerun the job. It costs nothing |
| A check fails after export | Read `runtime/files.json` in the job folder. It names the file and the rule |
| UNIT-ANIM-FPS fails on a clip made by hand | Export it again with `export_clip`, which writes 30 frames a second and keeps the clip's length. A unit whose entity events (sounds, flashes) are timed in another rate's frames keeps that rate: `export_clip(action, path, fps=24)`, and check it with `--fps 24` |
| UNIT-NORMALS fails | No free repair: the winding repair keeps imported normals. In Blender, flip those corner normals, or recalculate them on a welded copy and copy the result back |
| UNIT-STREAM-VERTICES fails after a Blender edit | Run `clear_sharp_faces` on the mesh and export again |
| Holes remain after `repair_unit.py` | Rebuild the faces in Blender, or make a new model |
