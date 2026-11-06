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

| Type | For | Body | Rig | Animations |
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

### Check the body before you rig it

The body column names a body preset (`.tools/3d_pipeline/config/body_presets.json`). After Meshy makes the model, and before you pay for a rig or clips, measure it:

```
py -3.13 -B .tools/3d_pipeline/measure_body.py <job folder>
```

It counts the feet on the ground and measures the torso and the reach of the lower body, then says which preset the model fits and how sure it is. It measures the body only, not separate plates, a quiver or a weapon, and it fails a model with pieces floating apart from the body, so you drop them before paying for the rig. It passes when the job's unit type uses that preset. It fails when they disagree, for example a `beast_biped` job whose model came out on four legs, and names the unit types that fit. It escalates when no preset fits, for example a body with wings, extra arms or tentacles: such a unit is rigged and animated live in Blender (see [Author animations live in Blender](#author-animations-live-in-blender)). It reads files only and costs nothing.

Give the job its anatomy, answered from the reference image when you review it, so the check knows what a measurement cannot see: `"anatomy": {"legs": 2, "arms": 2, "wings": false, "tail": false, "extra_limbs": false, "vehicle": false, "rider_on_mount": false}` in the job's registry entry. When you know better than the measurement, set `"body_preset"` and say why in `"body_preset_reason"`.

Every type gets the six land-unit roles: idle, move, attack, defend, retreat and death. Walks use Meshy's in-place clips, so the unit does not slide.

Mounts are built to vanilla's horse size on the map, which is smaller than vanilla infantry. A mounted unit is two jobs: a `mount` and a `rider`. The mount's entity attaches the rider's entity to its `Saddle_Node`, the way vanilla cavalry does, so one horse can carry several kinds of rider.

## Give every unit its own animations

Two units of the same type would play the same library clips, and players notice. Only reskins of one base unit (the same body and rig with a different look, such as a winter uniform) may share them. Before you pay for any clip, plan them:

```
py -3.13 -B .tools/3d_pipeline/plan_clips.py --jobs-config <your 3d_jobs.json> --write
```

It goes through your jobs in order and gives each role the first candidate clip of the unit type that no other unit plays yet. A job with `"reskin_of": "<base job>"` gets exactly its base's clips, and a job that lists its own `required_actions` keeps them. When every candidate for a role is taken, the verdict escalates and names the unit and the role: author that clip in Blender, add another candidate to the unit type in `unit_types.json`, or ask whether the units may share. Without `--write` it only reports. After export, `check_unit_files.py --mod-root .` fails a clip another unit plays; check a reskin with `--reskin-of <base unit>`.

A project whose animations are all authored by hand sets `"animation_policy": "authored"` in its job registry. Then the plan lists every role for live authoring and plans no library clip.

## Pick units players will see

A division shows the model of its highest-priority sub-unit (`priority` in the unit's `sub_units` entry). A unit that never leads a template, for example archers next to higher-priority infantry, is drawn only when a player builds a template led by it. Before you pay for a model, check that the unit leads at least one starting or AI division template. Spend credits first on units that lead starting divisions.

## What happens

Each step is one command, and each prints a one-line verdict. `pass` names the next command. `fail` names the free fix to run. `escalate` means no script can fix it and the unit needs hands-on work (see [Author animations live in Blender](#author-animations-live-in-blender)). Run the command the verdict names, and keep going until the unit passes the review.

1. **Reference image.** One clean picture of the unit, without weapons in hand and on a plain background. A unit that will hold a weapon has its hands closed in fists, because an open hand cannot be posed into a grip later. You look at it, approve it, and answer the anatomy questions in `.tools/3d_pipeline/config/body_presets.json` (legs, arms, wings, a tail, extra limbs, a vehicle, a rider on a mount). They go into the job as `anatomy`.
2. **Model.** `run_pilot.py --jobs-config <your 3d_jobs.json> --phase candidate <unit>` has Meshy turn the picture into a textured model (paid), and Blender imports it, checks it for holes and scales it against vanilla infantry.
3. **Body check.** `measure_body.py <job folder>` measures the model and checks that it fits the job's unit type (see [Check the body before you rig it](#check-the-body-before-you-rig-it)). It costs nothing. Pay for nothing more until it passes.
4. **Rig, animations and export.** First, `plan_clips.py --jobs-config <your 3d_jobs.json> --write` gives every unit its own library clips (see [Give every unit its own animations](#give-every-unit-its-own-animations)). Then `run_pilot.py --jobs-config <your 3d_jobs.json> <unit>` continues the job. Meshy rigs humanoids and animates them from its library (paid). Blender rigs four-legged animals itself and seats riders. Blender then writes the `.mesh`, one `.anim` per role and three DXT5 textures with mip levels, and re-imports them to prove they load. Steps that already succeeded are reused, never paid twice.
5. **Weapon in hand.** An armed unit's weapon is a separate model. `fit_prop.py` fits it to the hand against every clip and binds it there (see [Put the weapon in the hand](#put-the-weapon-in-the-hand)). It costs nothing.
6. **Checks.** `check_unit_files.py <unit folder> --unit-type <type> --mod-root . --verdict <job folder>/evidence/check.json` reads the exported files. Its verdict names the repair to run, or escalates.
7. **Free repair.** `repair_unit.py` fixes what the check names (holes, faces turned the wrong way, fused body parts, hard weight seams, feet off the ground) in a copy, then the check runs on the copy.
8. **Hand-over.** The export lands in the job's `runtime/files` folder with its final names, next to `runtime/registration.md`, which holds the `.gfx`, `.asset` and entity text to paste. Each later step writes a full copy of the unit to its own folder (`<job folder>/props/files`, `<job folder>/repair/files`): the newest copy that passed its check is the one you review and install.
9. **Independent review.** `review_unit.py` renders every clip from six sides, including the map camera, plus a diagnostics sheet per clip, and a reviewer who did not make the unit lists every defect it sees. The unit is finished only when that list is empty. See [Independent review](#independent-review).
10. **In game.** You or your live-testing setup place the unit and look at it idle, moving and fighting.

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
| Every clip of a soldier, rider or creature plays at 30 frames a second | Vanilla's do, and Paradox's own exporter knows only 15, 30 and 60. A Blender scene from factory settings runs at 24, so a clip keyed for 30 and written at 24 plays a quarter too slowly. The kit's exports write 30 and keep each clip's length in seconds |
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
| Every separate part (a strap, a plate, a quiver, a weapon) is skinned and stays on the body in every frame, as close as vanilla soldiers' and horses' parts do. Any number of parts is fine. A weapon fitted as its own shape and bound to the hand counts as one part, however many pieces it has, and must stay in that hand | A part that floats off the body, or slides away from where it rests when the unit moves, looks broken at every zoom |
| No two roles of one unit play the same motion (a rider's idle, move and retreat may: the mount's gait carries it) | Each role must read as itself: a retreat that is the walk, a defend that is the idle |
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

Rounds converge when every reviewer gets the same request:

- **Fixed notes.** If part of the unit's look could be mistaken for a defect, such as a ragged, torn hem or torn wing membranes, say so once in a notes file in the job folder and pass it every round with `--note-file <job folder>/review_notes.md` (or `--note "..."`). The reviewer still judges everything the note does not name, including any hole in the body.
- **The checklist.** The reviewer goes through the quality bar item by item and ends the reply with a `CHECKLIST:` block. A reply that skips an item is recorded as a fail, and a new reviewer gets the same request.
- **Changed clips only, then a full round.** After you fix some clips, render and review only those: `--clips attack death` renders them and the rest pose, and the request tells the reviewer to judge only them. A unit is accepted only after a full round, without `--clips`, by a new reviewer. The verdict names that round when an intermediate one passes.

The camera angles never change between rounds.

### When the reviewer finds defects

The checks pass anything within vanilla's limits, so a reviewer can still see defects. Each kind has its fix:

| The reviewer sees | Fix |
| --- | --- |
| A small hole (magenta, or a cyan rim on the diagnostics sheet) | `repair_unit.py ... --repairs holes --max-hole-edges 32`, then check the copy |
| Surface that tears or smears where two body parts meet, red on the diagnostics sheet in every clip | `repair_unit.py ... --repairs bridges weights` |
| A foot above or below the ground | `repair_unit.py ... --repairs ground` |
| The weapon through the head or body | `fit_prop.py` again on the same copy (it replaces the weapon it fitted before), first with a shorter `--length` such as 0.4, then another `--grip` between 0.1 and 0.3; a two-handed hold is made by hand |
| A part that tears or crushes only in some clips (a death or an attack that twists the torso hard), or a clip that does not read as its role | No script fixes the motion itself: author those clips again in Blender ([Author animations live in Blender](#author-animations-live-in-blender)), or ask the user before paying for other clips |

Fix the free ones first, in this order: the mesh repairs, then the weapon, since `repair_unit.py` runs on whatever the copy holds. Render again and ask a new reviewer, then take what is left to Blender.

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

## Put the weapon in the hand

Soldiers, riders, giants and other armed units hold their weapon in hand, and the weapon is generated as a separate model. `fit_prop.py` puts it there for free:

```
py -3.13 -B .tools/3d_pipeline/fit_prop.py gfx/models/units/<unit> --prop <weapon job>/provider/downloads/generation_model.glb --bone RightHand --length 0.55 --grip 0.15 --out <job folder>/props
```

It scales the weapon to `--length` of the unit's height, puts its grip (`--grip` of its length from the butt) in the palm, and tries 42 directions over every clip. It keeps the one whose far end least often passes through the body or into the ground, binds the weapon to the hand bone and writes the unit again, with the weapon's three textures, to `<job folder>/props/files`. The clips are not touched.

Its verdict passes when the weapon stays out of the ground and almost never passes through the body, and names the check to run next. It also writes `<job folder>/props/registration_prop.md`: the `meshsettings` block that gives the weapon's shape its own textures, to paste into the unit's `pdxmesh` block when you register the unit. If no direction clears the clips, try another `--grip` or `--butt`, or seat the weapon by hand in Blender. A weapon held in both hands always needs that hand-made step for the second hand.

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
