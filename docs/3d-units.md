# 3D units with Tripo and Blender

This page is for modders who want their own 3D units on the HOI4 map: soldiers, archers, riders, beasts and vehicles. Tripo makes the model from your picture, rigs it and animates it. Blender turns the result into HOI4 files. Your coding agent does the work through the `hoi4-3d-model-pipeline` skill. You approve the picture and the credit budget, and you look at the result.

Tripo is the default generator since November 2026. Models made earlier with Meshy stay usable, and the Meshy steps still run for old jobs (see [Old Meshy jobs](#old-meshy-jobs)).

**What is proven.** An unarmed humanoid unit (a zombie soldier) went the whole route below and passed a fresh review in November 2026. That run used a wrong size (see Size in [The route step by step](#the-route-step-by-step)), so its size on the map is checked again after a rerun. Armed units with a separate weapon, winged units and other bodies are in progress. See [Armed units](#armed-units) and [Known limits](#known-limits) before you spend credits on them.

## How to use it

1. In HOI4 Mod Setup, tick **3D models workflow** (see [Setup](#setup)). Sign in to [Tripo Studio](https://studio.tripo3d.ai) in your browser.
2. Tell your coding agent: "Make a 3D unit for `<unit>` with the `hoi4-3d-model-pipeline` skill." That skill is the one entry point.
3. Approve the reference picture and the credit budget when it asks.
4. Pick how Tripo is driven:
   - **By hand.** The agent gives you one short card per model. You click through Tripo and save the export into the inbox folder. About ten minutes a model.
   - **By agent.** The agent drives Tripo in your Chrome through Claude in Chrome, while you stay signed in.
5. The agent picks the export up, picks the clips by measurement, runs the Blender stage and the checks, and shows you renders. Every step prints a one-line verdict: `pass` names the next command, `fail` names the free fix, `escalate` means no script can fix it.
6. A reviewer that did not make the unit looks at the renders. The unit is finished when it passes. Then look at it in game. If a step fails, see [When something fails](#when-something-fails).

## What it is

| Step | Where | Who |
| --- | --- | --- |
| A 3D-ready picture from your art (neutral pose, empty hands) | Tripo's free image tool | you, or the agent in Chrome |
| Picture to textured model | Tripo web app | you, or the agent in Chrome |
| Rig, apply candidate animations, export | Tripo web app | you, or the agent in Chrome |
| Pick one clip per role by measurement | your PC | the agent |
| Intake, fit to HOI4, export `.mesh`, `.anim` and textures | Blender, on your PC | the agent |
| Checks, repairs, independent review | your PC | the agent and a fresh reviewer |

Tripo has no key to set up and the kit calls no Tripo API. Everything in Tripo happens in its web app, under your own sign-in, and models leave Tripo only through its own Export button. Blender is the one shared stage for every generator, so a model from Tripo, from Meshy or from your own files ends in the same checks and the same review.

### Rigging and animation

Units are rigged with Tripo's auto-rig and animated with its free preset library. The agent applies several candidate presets for each role and keeps the one that measures best (see [Pick the clips by measurement](#pick-the-clips-by-measurement)). Where no preset reads as the role, it makes one text-to-motion clip from a written instruction. Clips you made before stay in your Tripo account and can be applied to a new model for free. Manual rigging or keyframing in Blender is only for small fixes, or when no tool or preset works, and the agent records the reason in the job.

## Setup

The Blender stage is Windows only today. In HOI4 Mod Setup, tick **3D models workflow**. It installs:

- The kit's 3D pipeline (`.tools/3d_pipeline/`) and the `hoi4-3d-model-pipeline` skill.
- Blender 5.2.3, when no Blender 5.1 or 5.2 is installed. A portable Blender in `%LOCALAPPDATA%\Programs` is found too. Set `BLENDER_EXE` to use a particular one.
- The `io_pdx_mesh` add-on for that Blender, which reads and writes HOI4's `.mesh` and `.anim` files.
- The Blender Lab MCP server, registered for your coding client. It also installs the pinned Meshy MCP server, which only old Meshy jobs use. HOI4 Mod Setup may still ask for a Meshy key. Leave it empty when you use Tripo.

**The Tripo account.** A free account can try the route (about 13 models a month, public models, non-commercial use). A paid plan gives private models, commercial use and enough credits for a unit roster. You sign in yourself. The agent never types your password.

**A new worktree or a pipeline update needs the adapter set up again.** The Blender adapter checks its own source files against hashes in `.tools/3d_pipeline/config/blender_hoi4_adapter.json`, which is not tracked. A fresh worktree has no such file, and a merge that adds or changes an adapter source makes the adapter refuse with "source closure changed ... rebootstrap". Run `py -3.13 -B .tools/3d_pipeline/bootstrap_3d_workflow.py --without-meshy` from the repository. It also rewrites `.codex/config.toml` and `.tools/3d_pipeline/config/dependencies.lock.json` with paths of your machine. Put those two back with `git checkout`, and never commit them. It leaves a background Blender running as an MCP server (`--command blender_mcp`). Stop that one process before a run that waits for no Blender to be running.

**By agent needs Chrome.** The agent uploads your pictures and collects the exports through the Claude in Chrome extension. In Chrome's settings, turn off "Ask where to save each file before downloading", so exports land in your Downloads folder without a dialog. A browser pane inside a coding client cannot upload a local picture, and it asks you to confirm each download, so it only suits the by-hand mode.

## What a unit costs

Tripo prices its steps in credits. These were read from the app on a Pro plan in November 2026, with the settings in [Tripo settings](#tripo-settings). Check the number on the button before you press it.

| Step | Credits |
| --- | --- |
| 3D-ready picture in Tripo's image tool (Nano Banana 2) | free within the monthly quota (100 on Pro) |
| Model from one picture | 30 |
| Auto-rig | 20 |
| Preset animations (96 in the library), and your own earlier clips applied to a new model | free |
| Text-to-motion, one clip of up to 5 seconds | 20 |
| Export | free |

| Unit | Steps | Credits |
| --- | --- | --- |
| Unarmed foot unit where presets fit every role | picture, model, rig, presets | 50 |
| Unarmed foot unit with one made attack (the zombie) | picture, model, rig, presets, one text-to-motion clip | 70 |
| Static model (building, landmark, ship hull) | model | 30 |

Every step on your PC is free. Your agent asks you once for a credit budget per unit, notes the balance before and after each Tripo step in the job's ledger, and stops at the budget.

**Spend credits where players look.** A division shows the model of its highest-priority sub-unit (`priority` in the unit's `sub_units` entry). A unit that never leads a template is drawn only when a player builds a template led by it. Pay first for units that lead starting divisions.

## The route step by step

Run every command from the repository root. Your agent writes the job registry (`3d_jobs.json`) with one entry per unit: its `unit_type`, `"provider": "tripo"`, `credit_budget`, `anatomy`, its size, and a `tripo` block with the clip for each role.

**Size.** `target_height_m` is the unit's mesh height in HOI4 units, not metres, and `runtime_entity_scale` is its entity scale. Vanilla infantry is 7.35 tall at scale 0.8. Give a soldier-sized unit 7.35, and scale that for a smaller or larger body. `run_pilot.py` refuses a job whose unit would stand under half or over three times the height of its vanilla scale reference on the map. Review sheets frame every unit to fit, so they never show a wrong size.

### 1. A 3D-ready picture

Tripo copies the picture's pose into the rig, so the picture must be ready for rigging:

- One subject, full body, front view, feet visible, on a plain light background.
- Arms hang relaxed about 30 degrees away from the body, with background showing between each arm and the torso.
- Both hands empty, open and relaxed. A held weapon or a clenched fist rigs badly and deforms.
- Every detail of your art kept: face, clothing, gear on the correct side.

If your art is not like this, the agent redraws it in Tripo's image tool (**Image**, model Nano Banana 2, free within the quota) with an instruction that names every detail to keep and only the pose and hands to change. Name gear by the side of the picture ("on the viewer's left"), because "his left" gets swapped. Check the result against the original before you pay for a model. You approve the picture and answer the anatomy questions in `.tools/3d_pipeline/config/body_presets.json`.

### 2. Card and inbox

The agent writes one card per model from `.tools/3d_pipeline/tripo/CARD_TEMPLATE.md` and makes the job's inbox folder. The card names the picture, every Tripo setting, the candidate presets for each role and the file name to save under. In the by-hand mode you follow it. In the by-agent mode the agent follows it.

### 3. Model (Tripo, 30 credits)

In Tripo Studio open **Model**, **HD Model**, add the picture and generate with the settings on the card. One good picture is enough. Look at the result from all sides before you pay for the rig.

### 4. Rig (Tripo, 20 credits)

Open **Rig**: **Humanoid**, skeleton preset **Mixamo**, **Auto Rig**.

### 5. Candidate animations (Tripo, free)

Open **Animate**. Apply every candidate preset on the card, using the search box to find each one by name. A good set for a humanoid is `idle`, `walk`, `hit_to_stomach`, `hit_to_body_01`, `flee_01`, `defeat`, `defeat_02`, `fall` and `box_01`. Clips you made earlier are under **AI Animation** and cost nothing to apply again.

If no candidate can read as the attack, write one text-to-motion clip (20 credits). Name the motion, the hand, the height and the stance, for example "lunges one step forward, both arms straight at shoulder height, grabbing, torso upright, feet planted". The clip is named after the instruction text.

### 6. Export into the inbox

On the Animate page press **Export**: format **GLB**, **Export Skeleton** on, **Animation stay in Place** on. Under **Number of Animations** press **Select All**. Tripo builds the file in about a minute and saves it as `tripo_convert_<id>.glb`. Move it into the job's inbox as `<asset>__rigged.glb`.

With **Animation stay in Place** off, every clip carries its travel in the hips, and the loop, grounding and weapon-drop rules fail on it. The intake and the grip stage measure each role clip's hips travel in the file (`lib/glb_root.py`) and refuse one that moves more than a tenth of the hip height.

Add clips later to the same rigged model the body came from. Tripo can hold several rigs of one model under different tasks, and a new rig does not match the old one: on the orc the joint rotations differed by up to 0.77 in quaternion distance, and the weapon settings tuned for the first rig put the axe into the body. Compare the vertex count and the joints' rest transforms with the earlier export before you use the new one.

Two preset names change on export: the tile `defeat` exports as `defeat_02`, and the tile `defeat_02` exports as `defeat_03`. Read the clip names from the exported file, not from the tiles.

### 7. Pick the clips (free)

The agent measures every clip in the export and writes the role map into the job's `tripo.roles` (see [Pick the clips by measurement](#pick-the-clips-by-measurement)). `clip_check.py` gives each clip's stretch and ground numbers. A role's value is the clip's exported name, or its first words for a text-to-motion clip.

```
py -3.13 -B .tools/3d_pipeline/tripo/clip_check.py <job folder>/inbox/<asset>__rigged.glb --samples all --json <job folder>/evidence/clips.json
```

### 8. Intake (free)

```
py -3.13 -B .tools/3d_pipeline/tripo_intake.py --jobs-config <your 3d_jobs.json> <unit> --inbox <job folder>/inbox --credits <spent> --credits-note "<steps>"
```

The intake records each file's name, size and SHA-256, then prepares it for the shared stage in Blender. It renames Tripo's bones to the kit's names, folds the finger bones into the hands so the unit stays within HOI4's 50 bones, writes one file per role, and applies the [Tripo defaults](#tripo-defaults).

### 9. Blender stage and export (free)

```
py -3.13 -B .tools/3d_pipeline/run_pilot.py --jobs-config <your 3d_jobs.json> <unit>
```

Blender scales the unit against vanilla infantry, grounds every clip, and writes the `.mesh`, one `.anim` per role and three DXT5 textures with mip levels, then imports them again to prove they load.

### 10. Checks, repair and review (free)

```
py -3.13 -B .tools/3d_pipeline/measure_body.py <job folder>
py -3.13 -B .tools/3d_pipeline/check_unit_files.py <unit folder> --unit-type <type> --mod-root . --verdict <job folder>/evidence/check.json
py -3.13 -B .tools/3d_pipeline/check_holes.py <unit folder> --out <job folder>/evidence/holes
py -3.13 -B .tools/3d_pipeline/tripo/tripo_checks.py <unit folder> --jobs-config <your 3d_jobs.json> --slug <unit> --json <job folder>/evidence/tripo_checks.json
```

`measure_body.py` checks that the model fits the job's unit type (see [Check the body before you rig it](#check-the-body-before-you-rig-it)). `check_unit_files.py` reads the exported files (see [Automatic checks](#automatic-checks)), and `check_holes.py` looks for holes a player would see (see [Holes the player sees](#holes-the-player-sees)). `tripo_checks.py` adds the checks for faults Tripo's clips make (see [Tripo checks](#tripo-checks)). Each verdict names the repair to run, or escalates.

`repair_unit.py` fixes the mesh faults the checks name, in Blender, with no credits. The verdict gives the exact command, for example:

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

Repairs never make new bones, a new weight set or new keyframes. The copy goes to `<job folder>/repair/files`, and `repair_report.json` lists what changed with the check results before and after. Nothing under `gfx/` changes.

`review_unit.py` then renders every clip, and a reviewer who did not make the unit lists every defect it sees. The unit is finished only when it passes (see [Independent review](#independent-review)). For colour, `tripo/colour_compare.py` renders the unit and a vanilla unit under the same light and prints the brightness and saturation of each.

### 11. Hand-over and in game

The export lands in the job's `runtime/files` folder under its final names, next to `runtime/registration.md`, which holds the `.gfx`, `.asset` and entity text. The newest copy that passed its check is the one you review. Put it into the mod only after a fresh reviewer passes it, with step 12. Then you, or your live-testing setup, place the unit in game and look at it idle, moving and fighting.

### 12. Wire the unit into the mod (free)

Run this only after the fresh review passes. `wire_unit.py` puts the job's registration into your mod and says what the mod still lacks:

```
py -3.13 -B .tools/3d_pipeline/wire_unit.py <job folder or unit slug> --mod-root <mod> [--dry-run] [--json]
```

It writes the `pdxmesh`, animation and entity blocks, each between `# wire_unit begin <stem> <kind>` and `# wire_unit end <stem> <kind>` comments. A rerun replaces only the lines between its own markers, and nothing else in a file is touched. It copies the mesh, animations and textures into the model folder that `registration.md` names, and skips a file whose SHA-256 already matches. The `.gfx` and entity `.asset` go to `gfx/entities/<prefix>_units.gfx` and `.asset`, or to the file that already holds the markers. `--gfx-file` and `--entity-file` choose other files, and `--prefix` sets the prefix. If the mod already defines one of the names outside the markers, it stops and writes nothing.

It never writes sub-units or localisation. It checks that a sub-unit has `sprite = <stem>` and that the keys `<id>` and `<id>_desc` exist, and lists what is missing. It lists the counter sprites `GFX_unit_<sprite>_icon_medium` and `_medium_white` and whether the mod or only the game defines each.

Add a `sound_plan` to the job to get sound events: a list of `{role, soundeffect, frame}`. The tool writes `event = { time = <frame> sound = { soundeffect = "..." } }` into the entity state for that role. Whether the game reads `time` as frames or seconds is not verified yet, so check the sound in game. Sounds are never generated. Without a plan it prints a "no sound plan" warning.

After writing, it runs `check_unit_files.py --mod-root` and the static wiring audit and prints one verdict, PASS or FAIL with the list. A missing sprite or localisation key is a FAIL but does not stop the write. Only audit errors about this unit count, and `--strict-audit` counts every error in the mod. `--dry-run` prints the plan, changes nothing, and ends `DRY-RUN` or `DRY-RUN-FAIL`. The exit code is 1 on any FAIL and 2 on unreadable input.

## Pick the clips by measurement

The agent picks one clip per role by these rules, and records every candidate's numbers in the job. `clip_check.py` gives stretch and ground. Spin, hand reach, pelvis travel and the tumble test are read from the clip's joint positions in the exported GLB. The kit has no single command for them yet, so the agent computes them and records how. `TRIPO-NOT-DOWN` and limb-in-torso run in `tripo_checks.py` on the exported unit, so a death candidate is confirmed there after the run.

1. Every candidate must pass the stretch, spin and ground checks, and a death must pass limb-in-torso.
2. **Attack.** The largest forward reach of the hands (wrist ahead of the chest, as a share of the body's height) plus the travel of the pelvis. It must be at least 0.2.
3. **Death.** It must end lying down, on the front or the back (TRIPO-NOT-DOWN), and must not tumble: the feet never above the head, the pelvis never turned past 120 degrees. Among those, the lowest limb-in-torso wins.
4. **Defend and retreat.** The lowest stretch among the candidates that pass.
5. **Idle and move.** `idle` and `walk`, unless they fail a check.
6. **When no candidate passes a role,** use the fixed default for the body type: idle `idle`, move `walk`, defend `hit_to_stomach`, retreat `flee_01`, death `defeat_03` (the tile labelled `defeat_02`), and attack `box_01` for an unarmed unit. Then make one text-to-motion clip for the role.

Whether an attack reads as an attack stays a judgement. A clip that passes every number can still look like a guard. The fresh reviewer decides. If the review fails the attack, make one text-to-motion clip (20 credits). If that fails too, stop and ask.

## Tripo defaults

The intake and the Blender stage apply these to every Tripo job without a setting. The last two can be changed in the job's `tripo` block. They come from comparing Tripo units with vanilla infantry under the same light.

| Default | What it does | Why |
| --- | --- | --- |
| No gamma grade on the colour map (`runtime_diffuse_gamma` 1.0) | Keeps Tripo's colours as made | A brighter grade washed the unit out against vanilla |
| Gloss mapped onto vanilla's range (`config/vanilla_gloss.json`), specular level 56 | Tripo's gloss is remapped onto the gloss of vanilla infantry | Without it cloth looks wet in game |
| Maps resized one channel at a time | The packed specular map keeps its channels apart | Resizing them together blended gloss into colour |
| Snap easing, 14 degrees a frame (`tripo.ease_snaps`, `false` to switch it off) | Spreads a joint's sudden turn over the frames around it | Tripo's clips snap a joint in one frame, which reads as a twitch |
| Arm level for an unarmed attack (`tripo.arm_level`, target `tripo.arm_level_target` 0.85) | Turns both upper arms by a constant angle so the hands reach forward at about shoulder height | Tripo's text-to-motion attacks hold the hands above the head and hide it. Set `"arm_level": []` to switch it off |
| Settle to the first pose for attack, defend and retreat (`tripo.settle`, `false` or a shorter list to limit it) | Appends frames that blend every bone from the clip's last pose back to frame 1, over a length its own motion sets (no bone turns faster than the clip's fast motion, at most 10.5 degrees a frame) | The game loops these clips. An attack that ended with the axe low across the hips began upright beside the body and popped back by 119 degrees |
| Per-frame grounding of the exported clips (every Tripo job) | After the mesh repairs, puts the lowest point of every frame on the ground (a death is only lifted), the weapon the unit let go of never deciding where it is | Blender grounds the clips at 24 frames a second and the export resamples at 30, so a toe dipped under the ground between keys (the orc's move 0.17%, its retreat 0.55%) |
| Legs of a death (every Tripo job) | When the boots hang above the ground at the end of a death, turns the legs toward the rest pose by the smallest share that brings the boots to the ground, ramped in once the body has come down. It tries both knees first, then both thighs, then all four joints | The orc lay with both lower legs bent up and the boots 5.6% of its height in the air. The zombie lay on its back with both thighs lifted at the hip and the boots 4.3% up, and straightening its knees lifted them further. Vanilla's boots stay on the ground |
| Upper body of a death (every Tripo job) | When the hips lie on the ground at the end of a death but the chest, the head or a hand stays more than 10.2% of the height up, turns the trunk's bones, then the neck, then each upper arm toward the ground. Each takes the smallest turn that brings its parts within 4% of the ground, judged as the ground pass will lift the body, and never one that pushes a part through the ground. Each turn is ramped in once the hips are down and the chest, head and hands have stopped moving. A dropped weapon below a turned arm keeps its place on the ground | The orc's death ended with the hips down but the head 16% and both hands 19% of its height up, the arms out level. Two reviewers read a body frozen in a dive. The settle laid the spine 22 degrees and the arms 6 and 40 degrees down: chest 2.1%, head 3.2%, hands 3.4% and 4.0%. Vanilla's deaths end with every part within 8.2% |
| Waist untwist for every role (`tripo.untwist`, `false` or a shorter list to limit it) | Where the shoulders turn against the standing feet about the up axis further than vanilla's worst clip of that role, turns Spine, Spine01 and Spine02 back by the excess, split evenly. A frame where a foot is lifted or steep gives no reading and takes the excess of the frames around it | Tripo's flee_01 retreat wrung the zombie's and the orc's waist. The orc's poleaxe attack turned the chest 68 degrees against the feet while its Hips bone turned with the chest, so the old measure against the hip line read 28 and passed. Vanilla's attacks reach 38 against the standing feet |
| Weights smoothed where the clips stretch (every Tripo job, `tripo.smooth_weights` `false` to switch it off) | On the exported mesh, finds the edges every clip stretches or squashes by the kit's own measure, smooths the weights of their vertices and two rings around them, and keeps the strength that lowers the deformed edges most while no clip gets worse. A held weapon and the cloak and wing chains are locked | Tripo's weights have hard borders. The zombie's armpits and back swelled and its waist stretched, and the leg-seam repair changed nothing. The rule cut the zombie's deformed edges by 18% and the orc's by 22% |
| Weights fitted to the unit's own clips (every Tripo job, `tripo.fit_weights` `false` to switch it off) | After the smoothing, takes the vertices of every edge a clip still stretches or squashes and three rings around them, and solves for the weights that keep those edges' lengths in sampled frames of every clip. Each vertex may use only the bones near it, at most four. The strength that lowers the deformed edges most while no clip gets worse is kept, and an edge the fit would make grow past its clip's worst fades the change out there. A held weapon and the armour plates are locked, and so is cloth bound to the cloak's chains for 70% or more of its weight. The cloak's blend into the body, under 70%, is fitted | Tripo's weights let a limb follow bones it should not. The orc's free upper arm and forearm held up to 90% of the upper spine, so the forearm bent like a hose. Measured on the round-4 units after the smoothing: deformed edges fell from 2385 to 1619 on the zombie and from 7199 to 4536 on the orc. On the orc the forearm fell from 1100 to 209 and the chest under the arms from 254 to 40. Bone-heat weights and joint bands made the clips worse and were dropped. The orc's right flank sheared between the thigh, the chest and the cloak under the raised axe arm, and 1,626 of its 2,206 vertices carry some cloak weight. Fitting the cloak's blend took the flank's worst attack frame from 291 to 158 deformed edges and its retreat from 278 to 141, and the whole unit from 4,450 to 3,098. Capping the thigh's weight above the hip joint made every clip worse |

Review sheets render from the packed material the game uses, so what you see on the sheet is what the map shows.

### Secondary chains: cloaks and wings

Tripo's humanoid rig has no cloth or wing bones. It binds a long cloak to the thighs, and a wing membrane to the arms and shoulders. Add `"chains"` to the job's `tripo` block and the intake gives that region its own bone chains, rebinds it and keys it in every role clip by fixed rules:

```
"tripo": {"roles": {...}, "chains": [{"region": "cloak"}]}
"tripo": {"roles": {...}, "chains": [{"region": "wings"}]}
```

Nothing in the job sets a number. The stage reads the body and follows these rules (`lib/tripo_chains.py`, run in Blender by `tripo/chain_stage.py`):

| Step | Rule |
| --- | --- |
| Region | Cloak: the region TRIPO-CLOAK-STRETCH measures, grown along the mesh into the cloth beside it that Tripo bound to the torso, hips or thighs, behind the hips and off every limb. Wings: everything farther from the mid-plane than 0.18 of the unit's width, without the forearms and hands, left and right |
| Bone budget | HOI4 allows 50 bones. What the kit's bones leave is shared equally by the regions' sides. A pair of wings is two sides |
| Chain shape | A chain bone is half a thigh long. Bones per chain are the region's length over that, 2 to 4. Chains are its width over that, 2 to 6. Over budget, bones per chain drop to 3 first, then chains to 2 |
| Placement | Cloak: an even fan of chains across its width, each hanging from the upper spine. Wings: a fan from the wing root at the upper back, each chain moved onto a finger ridge where the wing has one |
| Weights | Each vertex takes two neighbouring chains and two bones of each, so at most 4 influences. The region takes the chains whole. The chain weights blend into the body's over one chain bone outward from the region's border |
| Cloak motion | All chains move as one sheet. Each bone follows the upper spine at the top and the hips at the hem, through a spring at the swing rate of a pendulum as long as the bone. The sheet is pushed off the legs and torso along the hips' back direction, never points above the horizontal, and stays above the ground |
| Wing motion | A fold pose per role and a flap: a sine on each bone, a little later down the chain. Idle folded and still with a slow breath, move half spread with a beat per step, attack spread with one strong beat, defend at the side floor, retreat flapping hard and turned to show its face, death folding first and sagging flat with the body. A folded fan keeps 70% of its spread so the membrane never squashes |
| Loops | Idle and move end where they start |

The chains are keyed before the snap easing, so a bone a collision turned fast is eased like any other joint. The intake report lists the plan under `chains`: the bones, the region sizes and each role's fastest chain turn.

Three checks cover the regions. TRIPO-WING-STRETCH is TRIPO-CLOAK-STRETCH for wings. TRIPO-CHAIN-IN-BODY fails a clip in which more than 1% of the cloak or wing points sit deeper than 1% of the height inside the rest of the body. TRIPO-CHAIN-GROUND fails one in which more than 1% of them sink 1% of the height under the ground. They run for `--cape` or `--wings`, or for a job whose `tripo.chains` names the region. TRIPO-CLOAK-STRETCH counts the cloak's chain bones as cloak bones.

For a winged unit, set `target_height_m` so that the body without the wings is a soldier's height.

**Armour plates.** Add `{"region": "plates"}` to `chains` when the unit wears plates over its shoulders and chest. Tripo splits a plate's weight across the joint it covers, so a pauldron bends whenever the arm lifts. The stage finds the plates by rule from the rig's joints. A pauldron is the surface within 60% of the upper arm's length of the shoulder joint, outside it, and no lower than 20% of that length under it. A chest plate is the surface ahead of the upper spine, between the middle spine and the neck, inside the shoulders. Plates that touch form one assembly, so no seam between them tears. Each assembly is bound wholly to the bone nearest the root of those that hold at least a tenth of its weight. The weight blends back into the body over a ring as wide as the assembly, and the ring stops before any other plate. Plates take no bones. They are bound after the chains, so a chain's blend never reaches into a plate. TRIPO-PLATE-STRETCH fails a plate that stretches more than vanilla clothing does at its worst, 2%.

**What the chains keep clear of.** The chains are kept out of capsules round the legs, the torso, the head and the arms. A chain's blend never reaches a forearm, hand, shin or foot: the share fades out before them over one chain bone.

**Wing room.** A wing's poses are capped by the body:

- A fold swings it back until it lies along the back.
- Every pose swings it back at least to the side floor: the least swing past which swinging further hides little more of the body from the side (within 2% of the body of a full swing). A spread wing lies behind the shoulders and from the side covers the back of the shoulder and the arm. On the demon the floor is 37 degrees.
- When the torso turns, the wing on the side that comes forward swings back by the turn as well, because the review cameras stay put.
- A down-stroke stops when the lowest chain hangs straight down.
- A death folds the wings fully in the first 15% of the clip, or by the fall if that comes sooner. The fall starts when the hips drop 5% of the height. While the torso still stands, each wing is lifted in its own plane until its lowest chain stays above both knees, so a kneeling body has no wing across its legs. Only after the fall starts does the wing sag in its own plane until its highest chain lies level, and the back swing lasts only while the torso stands, so the wings lie flat beside a fallen body.
- Each bone adds 0.3 of its parent's flap, so the tips do not curl into spikes.

**Wing motion per role.** Idle is folded along the back and still, with one slow breath per loop. Move is half spread and beats once per step, with the down-stroke as a foot strikes. The steps are read from the clip's feet. Attack is spread to the side floor with one strong beat. Defend stays at the floor, because a wrap forward crossed the body from the side. Retreat beats hard and is turned so its face shows in the side and map views: it keeps the floor's swing and tilts its top back by the angle, up to 20 degrees, that makes its smaller face share largest. Swung further back (72 and 82 degrees on the demon) the beating membrane squashed past UNIT-ANIM-STRETCH.

**Chain checks.** TRIPO-CHAIN-IN-BODY allows 4.5% of the cloak or wing points inside the body. Vanilla GER infantry clothing reaches 4.25% with its own clips. Points modelled inside at rest are left out. A point is inside only when the ray votes say so and its winding number about the body is above one half. The body is open where the region was cut out of Tripo's single skin. Ray votes along fixed directions flipped when the torso bent, even for cloth that had not moved into the body. TRIPO-WING-FRONT fails a clip in which the wings hide more than 5% of the body in the front or map view, or more than 10% of the limbs and head in a side view. From the side a wing's root always covers some of the upper back, so the side views judge the arms, legs and head where a viewer sees them, not a far arm behind the torso. A fresh review accepted side views up to 5.3% and failed them from 17.5%. A death is judged in the map view, and in the side views only while the torso stands. TRIPO-WING-EDGE-ON fails a beating wing (the attack and the retreat) whose silhouette in a side or the map view has a median under 40% of its silhouette seen square-on. The retreat the review read as a spike measured 26% to 38%, an accepted idle 47% to 55%. TRIPO-WING-IDLE-MOVE fails when the move's wings move less than three times as much as the idle's at map size. The pair the review found alike measured 1.6 times. TRIPO-NOT-DOWN leaves out cloth and wings carried by chains, because it asks whether the body lies down.

Tested in November 2026: on an orc the plates stopped bending (0% stretch) and the cloak stretch passed in every clip (the attack fell from 13.8% to 2.7%). The 10.2% of cloak points the attack seemed to put in the body was the old inside test: the same files measure 0.5% once the winding number must agree. The combined orc (weapon, cloak and plates) passes every check. On a demon the side views of the attack fell from 21% to 3% and of the retreat from 5% to 2%, and idle and move now differ at map size. Still failing on the demon: the defend's side view while the torso twists (14%), the death's side views during the stagger and the fall (14% and 17%) and its map view (5.2%), and the retreat's face share (36% to 37% against 40%). None of them has been seen by a fresh reviewer yet.

## Tripo checks

`tripo/tripo_checks.py` reads the unit's runtime files and fails what a viewer fails on a Tripo unit. Each limit is measured on vanilla clips or on clips a reviewer failed.

| Rule | Fails when |
| --- | --- |
| TRIPO-HANDS-HIGH | In an unarmed unit's attack a hand is above the head in more than 20% of frames, or above the shoulders in more than 80% |
| TRIPO-LOOP-POP | The last frame of an idle, move, attack, defend or retreat clip is more than 8 degrees from its first at some joint. Vanilla's role clips measure 0.0 to 6.3, the orc's attack measured 119 |
| TRIPO-FOOT-BELOW-GROUND | A foot or toe sinks more than 0.1% of the height under the ground in a clip that is not a death. `UNIT-ANIM-GROUND` reads the toes too, but its limit is vanilla's worst clip of all (4.2%, a push-up), and vanilla's own role clips sink at most 0.9% |
| TRIPO-DEATH-FEET | In the last 15 frames of a death the boots hang more than 1% of the height above the ground. Vanilla's deaths end within 0.6% |
| TRIPO-DEATH-REST | A death ends with the hips on the ground and the chest, the head or a hand more than 10.2% of the height above it. Vanilla's deaths end with every part within 8.2% |
| TRIPO-WAIST-TWIST | The shoulders turn against the standing feet about the up axis more than a quarter past vanilla's worst clip of that role (retreat 19.6, move 18.4, idle 69.7, attack and defend 38.3, death 30.8 degrees, measured on GER infantry). Only frames with both feet on the ground and level count, so a run or a stride gives no reading. Vanilla's charges hold the chest up to 69 degrees off a running foot, so a measure that read strides would pass any attack |
| TRIPO-NOT-DOWN | A death clip does not end lying down, on the front or the back: the body ends taller than 40% of its standing height, plus however much thicker than a human's (0.22 of the height) its torso is, or its torso is more than half upright. The ogre's torso is 0.40 deep, so it may lie at 58% |
| TRIPO-LIMB-IN-TORSO | In a death clip an arm or a leg passes deep into the torso (limit set from vanilla's infantry deaths) |
| TRIPO-CLOAK-STRETCH | A cloak stretches more than vanilla clothing. Runs only for a job with `"cape": true` (read through `--jobs-config` and `--slug`), or with `--cape` |
| TRIPO-WEAPON-IN-BODY, TRIPO-WEAPON-BELOW-GROUND | A held or dropped weapon is inside the body or under the ground in any frame of the exported clips (armed units) |
| TRIPO-SHIELD-IN-BODY, TRIPO-SHIELD-BELOW-GROUND | The same for a shield held in the other hand (a job with `tripo.shield`, see [Shields](#shields)) |
| TRIPO-PLATE-STRETCH | An armour plate bound by the plates rule stretches more than 2% |
| TRIPO-WING-FRONT | The wings hide more than 5% of the body in the front or map view, or more than 10% of the limbs and head in a side view |
| TRIPO-WING-EDGE-ON | A beating wing (attack, retreat) shows less than 40% of its face in a side or the map view, as a median over the clip |
| TRIPO-WING-IDLE-MOVE | At map size the move's wings move less than three times as much as the idle's |
| TRIPO-GRIP-ENCLOSURE, TRIPO-GRIP-THUMB | The hand does not wrap the haft, or the thumb is on the wrong side (armed units) |
| TRIPO-BLADE-FACING | The weapon's blade is seen edge-on from the front in the idle pose (armed units) |

## Armed units

Tripo's rig bends a weapon modelled into the hand, and Tripo's clips animate an empty-handed body. The kit has a separate-weapon route in progress: the body is modelled with empty hands, the weapon is its own model, and the kit puts the weapon in the hand, closes the fingers around it (`tripo/grip_weapon.py`) and keeps it out of the body by turning the wrist. It was tested on an orc with a long axe in November 2026 and did not pass review yet:

- The rule keeps the weapon out of the body in idle, move, defend and retreat without changing how they read.
- An attack made for an empty hand does not become a weapon swing. With the weapon cleared from the body it reads as a stiff hold. A weapon attack needs a clip made for the weapon.
- A long weapon carried down in a death clip passes through the body or the ground.
- A coarse Tripo hand does not wrap a haft tightly.

**The clearance follows the cloak.** A cloak that gets its own bone chains (`tripo.chains`) swings a few percent of the height off the rigid pose the grip stage clears the weapon in, and the swing can carry cloth through a weapon that only just cleared it (the orc's retreat, 2.2% of the weapon's points inside the body in 8 frames, all of them against the cloak). The clearance rule keeps the weapon `--soft-share` (4% of the height) clear of the cloak's vertices as well, wherever the body has a cloak by the check's own region rule, with no job setting. The check on the exported files stays the judge: a frame fails the grip stage only by the check's own test.

**A dropped weapon's stillness is judged on the exported files.** The grip stage measures the weapon after landing on its own GLB (11.9% of the height on the orc) and the exported death differs (the retarget, the easing and the pipeline's grounding of each frame), so the stage prints it as a diagnostic and fails only for the weapon inside the body or under the ground. `tripo_checks.py` reports `moved_in_last_half_share` for every clip.

**A clip that ends still is trimmed.** Tripo's text-to-motion attacks run for the length asked and then hold their last pose (the orc's attack chops by frame 80 and stands still to frame 120). The intake cuts the still tail of attack, defend and retreat clips by one rule (`lib/tripo_trim.py`): the motion is the joint turn per frame summed over the body, the floor is 5% of the clip's own peak (its 95th percentile), and the clip keeps half a second after the last frame above the floor. It cuts only when that saves a fifth of the clip and leaves a second. Idle, move and death are never cut by the rule. A job's own `tripo.trim` for a role wins, and `"auto_trim": false` (or a list of roles) switches the rule off.

The weapon checks judge the exported `.mesh` and `.anim` files, the ones the game loads. TRIPO-WEAPON-IN-BODY and TRIPO-WEAPON-BELOW-GROUND are measured there, frame by frame. The grip stage's own GLB is only a diagnostic. In a death clip the weapon is dropped before the body falls: the hand lets go at the start of the fall, and the weapon tumbles to the ground on its own path, flat and clear of where the body will lie. The retarget keeps the weapon bone's location for this. A coarse Tripo hand cannot wrap a haft tightly. A job may set `tripo.weapon.grip_check` to `"advisory"`, so TRIPO-GRIP-ENCLOSURE is reported but does not fail the unit, and a reviewer judges the hand at game zoom. TRIPO-GRIP-THUMB still counts.

Until an armed unit passes a fresh review, keep armed units to weapons held low and short, or plan live work in Blender for the attack.

### Shields

A shield held in the free hand is a second rigid part. Model it on its own like the weapon, then run `tripo/shield_stage.py` on the grip stage's GLB, before the intake:

```
blender -b --factory-startup --python .tools/3d_pipeline/tripo/shield_stage.py -- <gripped.glb> <shield.glb> --out <shielded.glb> --report <report.json> --hand RightHand --hold-clips <the weapon's hold clips> --hold-fade-clips <attack> --release-clips <death> --clearance-clips <every role clip>
```

The stage runs the grip stage's own steps on the free hand. Only the grip on the shield is its own rule (`lib/tripo_shield.py`), read from the model with no per-unit number:

| Step | Rule |
| --- | --- |
| Size | The shield's longest axis is `--height-share` of the body's height, 0.65 by default (the dwarf's art) |
| Outer edge | The side the shield's middle bows to, away from the line between its ends. The spikes of a crescent are there |
| Grip | The fist closes round the middle of the inner edge, on a bar along the long axis just inside the hollow. The bar has a held haft's radius, 1.5% of the height |
| Roll | The shield reaches out of the back of the fist (`--roll 180`), so the palm and the fingers stay outside it and a hanging arm holds the outer edge away from the body |
| Hold | The grip goes to the unit's side with the long axis upright, by default high enough that the lower end is 8% of the height over the ground |
| Binding | Weight 1.0 on its own bone `Shield`, a child of the hand, as mesh `tripo_part_2`. With the weapon the unit has 24 bones of HOI4's 50 |
| Clearance | The weapon's rule: the hand turns about the wrist, frame by frame, until the shield leaves the body and the ground. The fist's zone round the grip is not judged |
| Death | The weapon's rule: the fist lets go at the start of the fall and the shield lies flat on the ground clear of the body and the dropped weapon (`--release-clips <death>`). `--fall-fade-clips <death>` keeps it in the fist instead, as vanilla keeps a rifle, and the clearance then judges every frame |

The job names the shield in its `tripo` block. The intake then binds `tripo_part_2` to `Shield` and the weight rules leave the bone alone. In its `release_roles` the bone keeps its location keys and never decides where the ground is, so a shield kept in the fist leaves the list out:

```
"tripo": {"weapon": {...}, "shield": {"part": "tripo_part_2", "bone": "Shield", "release_roles": ["death"]}}
```

`tripo_checks.py` judges it on the exported files with the weapon's two rules, TRIPO-SHIELD-IN-BODY and TRIPO-SHIELD-BELOW-GROUND. Each part's check leaves the other part out of the body.

Tested in November 2026 on the round-4 dwarf (glaive in the left hand, the crescent shield, 0.65 of his height, in the right fist), measured on the exported files by the shield checks:

| Role | Shield kept in the fist, outer edge held out | Dropped, earlier hold |
| --- | --- | --- |
| Idle, move | 0% | 0% |
| Defend | 1.5% in the body in 2 frames | 2.8% in 77 frames |
| Retreat | 1.3% in 8 frames | 2.3% in 7 frames |
| Attack | 35.7% in 51 frames | 41.7% in 69 frames |
| Death | 5.1% in the body in 2 frames, 3.8% under the ground in 5, and the body ends 56% of its height tall (TRIPO-NOT-DOWN) | 0% and 0%, the body ends 39% tall |

The death rule follows from the last row. Kept in the fist, the shield ends standing on its edge beside the fallen body, and the wrist turn cannot lay it flat. Dropped, it lands flat, 4.3% of the height clear of the body. The outer-edge target of the hold brought the outer edge from 56.5 degrees off the side (the idle) to under 1.5 degrees in every held clip, and the grip moved 8 to 14% of the height from the hold point instead of 5 to 9%. The attack fails as the weapon's does, because Tripo's attack holds both hands on one haft before the body, and needs a clip made for a shield.

## Tripo settings

These gave the best result for the price in the kit's own tests (an orc and a zombie, November 2026). They are a starting point, not a law.

| Setting | Value | Why |
| --- | --- | --- |
| Tool | Model, HD Model | Comes textured. Smart Mesh sculpts sharper detail but comes untextured, in loose parts, and costs more |
| AI model | H3.1 | Same price as H3.0 at these settings |
| Input | One 3D-ready picture | It was enough for a clean model. Generated side views did not improve the result |
| Ultra Mesh Quality | off | It adds 15 credits. The map camera does not show the difference |
| Texture | on, 2K, Remove Lighting on, PBR on | HOI4 unit textures are 1K to 2K. PBR gives the normal and roughness maps the pipeline packs |
| Topology | Triangle | HOI4 meshes are triangles |
| Polycount | 20,000 | The unit profile's working budget |
| Generate in Parts | off | One skin rigs and deforms best |
| Rig | Humanoid, Mixamo skeleton | The intake maps Mixamo's bone names to the kit's |
| Export | GLB, skeleton on, stay in place on | In-place walks do not slide on the map |

Give two units of one type different presets where the library has a second one that passes, so they do not move alike.

### By agent: how the agent drives Tripo

The agent works in your Chrome through Claude in Chrome, on the tab where you are signed in to Tripo Studio. It follows the same card as you would.

- It loads `.tools/3d_pipeline/tripo/tripo_studio.js` into the page. The helpers read the credit balance and the price on each button and refuse to press Generate when the price differs from the card. On the Animate page it types each preset's name into the search box (`TS.search`) and clicks the tile it finds (`TS.presetPoint`).
- It uploads the picture with the extension's file upload, never through a file dialog.
- It presses each paid button once, then waits for the new task. A second press starts a second paid task.
- It never reloads the Tripo page in the middle of a paid step.
- Exports go to your Downloads folder. The agent moves them into the inbox and renames them. It takes only a file created after its own click (newer than a marker file it touches first), never "the newest file of that type", because Downloads also holds your own files and a blocked download leaves an old file the newest.
- Chrome lets one page start one download on its own. A second export from the same tab is blocked without a message, so the agent opens a fresh tab for each further download. A multi-view group's download button saves only its first view.
- Tripo's image tool saves its pictures as WebP with a `.png` name. The job's reference must be a real PNG, so the agent converts each downloaded picture before it uses it.
- It writes the balance before and after each paid step into the job's ledger, and stops at the budget.

This ran end to end on several models in November 2026. Tripo changes its page from time to time. When a helper stops finding a button, the agent says so and you finish that step by hand from the card.

## Old Meshy jobs

A job without `"provider": "tripo"` still runs the Meshy route: `run_pilot.py --phase candidate <unit>` makes the model through the Meshy API, and `run_pilot.py <unit>` rigs and animates it from Meshy's clip library. That route needs a Meshy key and a paid Meshy plan, and its prices are in `.tools/3d_pipeline/config/meshy_pricing.json`. `plan_clips.py` plans Meshy library clips so that two units do not share one. Exported Meshy units need nothing from Meshy any more: the checks, repairs, weapon fit and review all run on the files you have.

## Unit types and bodies

Pick one type per unit in the job's `unit_type`. The type sets the rig, the clips and how the unit is wired. The full list is in `.tools/3d_pipeline/config/unit_types.json`.

| Type | For | Body | Rig | Clips |
| --- | --- | --- | --- | --- |
| `infantry_melee` | swords, axes, maces | humanoid | Tripo humanoid | sword slash, parry, wounded retreat, fall |
| `spearman` | spears and pikes | humanoid | Tripo humanoid | spear walk, thrust, two-handed parry |
| `archer` | bows | humanoid | Tripo humanoid | archery shot, aim and scan, step back with bow |
| `heavy_brute` | giants, trolls, ogres | large biped | Tripo humanoid | slow heavy walk, hammer swing, ground stomp |
| `beast_biped` | yeti, ghouls | large biped | Tripo humanoid | lumbering walk, two-fist strike, roar |
| `tree_creature` | ents | large biped | Tripo humanoid | unsteady walk, ground slam |
| `rider`, `mounted_archer` | the person on a mount | humanoid | Tripo humanoid, seated by Blender | the upper body plays the clip, the legs stay astride |
| `mount` | horses, camels, dead horses | quadruped | Blender quadruped with a `Saddle_Node` | idle, trot, charge, rear, gallop, collapse |
| `quadruped_beast` | wolves, war beasts, elephants | quadruped | Blender quadruped | idle, walk, charge, rear, gallop, collapse |
| `vehicle` | tanks, armoured cars, other wheeled or tracked units | none | live in Blender | idle, drive, fire, brace, reverse, wreck |

Every type gets the six land-unit roles: idle, move, attack, defend, retreat and death. A Tripo job picks one clip per role from the candidates it exported (see [Pick the clips by measurement](#pick-the-clips-by-measurement)), and the export's stay-in-place option keeps walks from sliding. The clips column above describes the motion each role should read as. For an old Meshy job most roles list two library candidates in `unit_types.json`, so the clip plan can give two units of one type different clips. A `vehicle` has `calibration_group: vehicle`: its checks use vanilla's tanks and trucks as the limit, not its soldiers.

Mounts are built to vanilla's horse size on the map, which is smaller than vanilla infantry. A mounted unit is two jobs, a `mount` and a `rider`. The mount's entity attaches the rider's entity to its `Saddle_Node`, the way vanilla cavalry does, so one horse can carry several kinds of rider.

### Tripo quadrupeds and mounts

Tripo's rig is for humanoids. For a `mount` or `quadruped_beast`, export Tripo's plain textured model (not rigged) into the inbox as `<asset>__model.glb`. The intake records it, and `run_pilot.py` rigs and animates it with the kit's quadruped rules (`adapter/quadruped_layout.py`), with no Tripo rig or clips and no credits after the model. The job adds:

```
"unit_type": "mount", "provider": "tripo", "size_vs_horse": 1.7, "size_vs_horse_reason": "...",
"tripo": {"load": true},
"rider": {"folder": "<exported rider unit>", "stem": "<its stem>", "roles": {"move": "idle", "retreat": "idle", "death": "idle"}}
```

Every number comes from a rule:

| Step | Rule |
| --- | --- |
| Size | The mount's back stands `size_vs_horse` times vanilla's horse on the map (the horse's `Saddle_Node` is 3.68 units up there). `size_vs_horse` is the species' withers height over a horse's, stated with its source. The back is measured on the model, so the mesh height follows (`lib/mount_size.py`, report `blender/reports/mount_size.json`) |
| Rider size | An attached entity's scale multiplies its parent's: vanilla's rifle is 0.73 of the soldier's height on the map only that way. So the rider entity gets the scale that makes it vanilla's rider size, 3.82 units on the map |
| Facing | The animal's length is its longest horizontal extent, and the end with the higher head faces forward |
| Legs | A leg's bones take only the skin within 2.2 of the leg's radii of its own line, so a trunk or straps beside a leg never follow it |
| Load | With `tripo.load`, the load is found by rule (`adapter/quadruped_load.py`). Its deck is the lowest height band with at least half of the most upward-facing flat surface. Its cut is the deck's own underside. The load is everything above the cut joined to the deck's footprint, and outside the footprint only what rises above the deck. It is bound wholly to its own bone, `Load`, a child of the Spine that never turns, and fades into the body over 6% of the body's height. The `Saddle_Node` is a child of `Load` |
| Pillar legs | A leg whose radius is more than 0.15 of its length (the belly's height) is a pillar leg, an elephant's (0.22 to 0.25, a horse's 0.05). Its joints below the shoulder and hip bend 0.06 over that share as far as a runner's. Such an animal walks where a runner trots and trots where a runner gallops. It attacks with a runner's whole rear at 0.4 (a stamp with the forefeet a little off the ground) and defends braced: legs apart, weight back, head and tusks low. A neck shorter than 0.3 of the body's length (withers to poll) bends that much less. Fresh reviews read a horse's bend on the elephant as legs crumpling under the body, its lunging head as crushed into the chest, and a full rear as the attack |
| Back | Under a load the back does not bend: Pelvis, Spine and Chest keep still and the legs, neck, head and tail move |
| Saddle_Node | On the floor of the load (the deck or an upper storey) where the rider's room holds the fewest load vertices. The room is the rider's height and, in plan, the cells its own clips sweep (with the job's `rider.roles` map), or a circle a fifth of its height wide without a rider. The load's faces are sampled densely, so a wide plank counts where it crosses the room. Ties go to the lower floor, then to the floor's centre |
| Rider fit | The largest rider, from vanilla's size down to half of it in 5% steps, whose room holds no load at all. The rider entity's scale follows that share (`rider_share` in `mount_size.json`). The war elephant's tower was modelled for a crew 0.6 of a vanilla rider, and a full-size rider stood through its upper floor |
| Death | The body rolls about the edge of the side it falls toward, and every frame is shifted sideways so the torso's centre stays over its standing spot. It rolls onto its side only until the load reaches lower than the torso. Then the final pose is tuned: the largest roll and the smallest turn of the neck against it with no part lower than the torso by more than 1% of the body's height, so neither a dropped head nor the tower holds the dead body off the ground |
| Loops | The charge runs two whole strides, so the attack ends in its first pose |
| Repairs | `winding`, `bridges`, `holes`, `weights` and `normals`. Tripo makes the animal and its load as one skin: `bridges` cuts a part fused to another, and `weights` blends a join inside one skin, such as a hanging tail grown into a hind leg |

The Tripo route's other rules apply as for a humanoid: grounding of every exported frame, the weight smoothing (with the `Load` bone locked) and the stretch checks. `tripo_checks.py` runs quadruped rules instead of the humanoid ones: TRIPO-LOOP-POP, TRIPO-FOOT-BELOW-GROUND for the hooves, TRIPO-NOT-DOWN (the torso ends within 5% of the height of the ground), TRIPO-LOAD-BELOW-GROUND and TRIPO-LOAD-STRETCH (more than 0.5% of the load's edges stretch: a plank never bends).

Tested in November 2026 on a war elephant carrying a two-storey tower (one Tripo model, 30 credits, nothing after it): the file checks and the quadruped Tripo checks pass, the tower stays rigid and the rider stands on the upper deck. Four fresh reviews failed it, the last on three major and seven minor defects. Still open after the last: the skin stretches at the shoulders, hips and elbows in the rear and the fall (the distance weights are hard at the leg joints), the head twists where the neck turns against the roll, the fallen body keeps its legs straight, and retreat reads like a faster move.

Review a mount with its rider on the node. `review_unit.py` and `tripo/weapon_sheets.py` take `--rider <folder> --rider-stem <stem> --rider-scale <scale> --rider-roles move=idle retreat=idle death=idle` and draw the rider entity on the `Saddle_Node`, playing its mapped clip in each of the mount's clips. The registration names the rider's mesh and entity after the mount, so a foot unit's files can ride without clashing with that unit's own blocks.

### Check the body before you rig it

The body column names a body preset in `.tools/3d_pipeline/config/body_presets.json`. `measure_body.py` counts the feet on the ground and measures the torso and the reach of the lower body, then says which preset the model fits and how sure it is. It measures the body only, not separate plates, a quiver or a weapon. It fails a model with pieces floating apart from the body, so you drop them before paying for the rig. It passes when the job's unit type uses that preset. It fails when they disagree, for example a `beast_biped` job whose model came out on four legs, and names the unit types that fit. It escalates when no preset fits, for example a body with wings, extra arms or tentacles, which is rigged and animated live in Blender. It reads files only.

The anatomy you gave in step 1 tells the check what a measurement cannot see: `"anatomy": {"legs": 2, "arms": 2, "wings": false, "tail": false, "extra_limbs": false, "vehicle": false, "rider_on_mount": false}`. When you know better than the measurement, set `"body_preset"` in the job and say why in `"body_preset_reason"`.

## Automatic checks

Run them on a unit's folder at any time with the command in step 10. Without `--verdict` it lists every finding.

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
| UNIT-DDS-SHINY | Specular maps stay about as dull as vanilla's | Shinier maps show as white speckles. The pipeline scales Meshy's metalness and gloss down to vanilla's range, and maps Tripo's gloss onto vanilla's |
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

A missing face, a face turned the wrong way, or a one-sided sheet seen from behind shows the ground through the unit. An open-edge count cannot tell those from the open edges a model keeps on trims, plates and straps that never show, so the rigged unit profiles judge holes by looking (`"holes": "silhouette"`). The model check in step 3 only records open edges. `check_holes.py` takes a unit folder or a provider `.glb` (steps 3 and 10).

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

It renders each clip from front, left, back, right, the map camera and below. Every round shows the same frames: one every half second of each clip and its last (`--step`), so two rounds can be compared. On top of those come the frames a check flagged (`--findings <tripo_checks.json>`) and the frames where the surface stretches most and where the unit sits lowest and highest, each captioned with why it is there. These extremes move when a clip changes a little (the orc's lowest attack frame moved from 18 to 38 between two rounds), so they are never shown in place of the fixed frames. A long clip's sheet is split into pages of six frames. Back faces are hidden as in the game on a magenta background, so magenta inside the unit is a hole, and a dark disc marks the ground. Each clip also gets a diagnostics sheet in flat colours: yellow to red where the surface stretches or squashes, cyan at an open edge, blue below the ground. It writes `REVIEW_REQUEST.md` with the reviewer instructions and the quality bar. Keep `--out` in the job folder, never under `gfx/`, or the renders ship with the mod.

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
| Skin that swells or stretches at a joint in the clips, red on the diagnostics sheet around armpits, waist or hips | `repair_unit.py ... --repairs stretch` (add `--locked-bones <weapon bone>` for a held weapon) |
| A foot above or below the ground | `repair_unit.py ... --repairs ground` |
| The weapon through the head or body | `fit_prop.py` again on the same copy, first with a shorter `--length` such as 0.4, then another `--grip` between 0.1 and 0.3. A two-handed hold is made live |
| A part that tears or crushes only in some clips (a death or an attack that twists the torso hard), or a clip that does not read as its role | No script fixes the motion itself. Find another preset or tool for those clips, or ask before paying for others. Keying them by hand in Blender is the last resort, with the reason recorded |

Fix the free ones first, in this order: the mesh repairs, then the weapon. Render again and ask a new reviewer, then take what is left to Blender.

### Small fixes and last resort: live Blender

When a small fix is needed, or no rig tool or preset works for a unit (wings, extra arms, a tail, a vehicle, a clip that failed review twice), your agent may pose the unit in a live Blender session through the Blender Lab MCP, one key at a time, and look at every key before it keeps it. It records why a tool or preset could not do the job. It costs nothing.

The kit's helpers in `.tools/3d_pipeline/authoring/live_helpers.py` turn, place, measure, render and key only what the agent names. They solve a leg with the knee toward the toes, put a hand on a point with a temporary IK, plant a foot, spread a lean down the spine, weight a crotch seam, keep a hand on a weapon wherever it moves, and render the reviewer's views. `export_clip` writes a clip over the action's own frame range at 30 frames a second. `normalize_quaternion_keys` flips keys that would make a joint turn the long way. `stretch_share` gives the share of edges the stretch check counts at a frame. `lowest_regions` lists the lowest point of each body region and prop, to find what holds a dead body up. `clear_sharp_faces` removes import flags that push a stream past 65,535 vertices.

The agent's guide is the skill's [live authoring reference](../.claude/skills/hoi4-3d-model-pipeline/references/live-authoring.md), including vehicles (wheel pivots, fused rigid parts, turret traverse). The result goes through the same checks and the same review as any other unit.

## Static and rigid-part models

Buildings, landmarks, ships, tanks and planes have their own route. Tripo makes a plain textured model (no rig and no clips, 30 credits: HD Model, PBR on, 20,000 triangles, Generate in Parts off). One free script turns it into HOI4 files, and a second renders the review sheets:

```
py -3.13 -B .tools/3d_pipeline/tripo/static_model.py <inbox>/<name>.json --out <job folder>
py -3.13 -B .tools/3d_pipeline/tripo/static_sheets.py <job folder>/mod/gfx/models/<folder>/<name> --model-kind <kind> --out <job folder>/review
```

The job file holds `name` and `model_kind`: `building`, `landmark`, `ship`, `vehicle` (a tank) or `plane`. The GLB is `<name>.glb` next to it. Add `--plan` to see what the stage would do, without Blender. The script writes a small mod tree under `<job folder>/mod`: the `.mesh`, one `.anim` per role and the three DXT5 textures under `gfx/models/<folder>/<name>/`, and `gfx/entities/<name>.asset` with the `pdxmesh`, the `animation` blocks and the entity. Then it runs the checks below and prints a verdict.

Every number comes from vanilla files. `calibrate_static_kinds.py` measures them and writes `config/static_kinds.json`, each with the files it came from. Run it again after a game update. The role clips are read from the installed game when a model is made.

| Kind | Size | Parts and bones | Clips |
| --- | --- | --- | --- |
| `building` | the area the map camera sees of vanilla's four facilities, entity scale 0.6 | one static shape, no bones, a `Collision` box, the `lamp` locator | none |
| `landmark` | the largest side of 19 vanilla landmarks, or the height of a tall and thin one (an obelisk on a wide base), unless its base is wider than vanilla's widest (see below) | all on `root`, a `Collision` box | none |
| `ship` | a destroyer's length, the waterline at zero, the hull cut at vanilla's draft | vanilla's two-bone contract: all on `ship` under `root`, the destroyer's locators | the destroyer's idle and death. Like vanilla's support ship and freighter, a one-piece hull has no attack clip: its attack and defend states play idle, and the entity's muzzle and water effects show the shot |
| `vehicle` | the area the map camera sees (length times width and height at its 55 degree elevation) of nine vanilla light tanks | hull on `chassie`, turret on `turret`, barrel on `barrel_base`, tracks on `wheel_suspention`, each road wheel on its own bone, vanilla's bone names, a `Collision` box, the `barrel`, `exhaust` and track locators | a light tank's idle, move and attack, a heavy tank's death |
| `plane` | the wingspan of twelve vanilla light planes | body on `root`, propeller on `propeller` | the fighter idle, with the propeller spinning |

What the stage does, in order:

- **Facing.** The model is turned so its front faces -y, as vanilla's do. A tank's front is where its turret reaches further (the barrel), a ship's bow is its narrower end, a plane's nose is the end nearer the wing. Set `front` in the job file when a rule gets it wrong.
- **Size and place.** Scaled to the kind's vanilla size at the reference entity's scale, centred and grounded where vanilla's are. A ship's waterline is where its hull reaches 95 % of its beam, as on vanilla hulls.
- **Triangles and textures.** Faces turned against their neighbours are turned back, piece by piece (a piece keeps Blender's recalculated winding only when it leaves fewer conflicts, and then each face at odds with two or more neighbours is turned while that helps), doubled faces are dropped and closed pieces facing inward are turned out, once after the weld and again after the holes are closed. Small open loops (up to 32 edges) are closed, as `repair_unit.py --repairs holes` does, in one flat colour so the texture does not swirl across them. A building's or landmark's open rim on the ground (a paved disc with no underside) is closed as well. Then the model is reduced to the triangle budget and texture size of the most detailed vanilla model of the kind: faces that lie flat together are merged first, then the rest is collapsed. The silhouettes are compared before and after the reduction, before the holes are closed, and a reduction that changes the outline fails the stage (STATIC-SHAPE). A cap over an opening adds to the outline by design. The maps are packed for `PdxMeshAdvanced`: the normal map as RRxG, the gloss remapped onto the distribution of the kind's vanilla specular maps, the specular level vanilla's.
- **Rigid parts.** A tank's turret starts above the largest step in the plan area of its height slices, where the slices above are turret-sized. On vanilla's own light tanks this rule puts 92 to 100 % of the surface where their skinning does. The barrel is the thin run in front of the turret. A plane's propeller is the blade disc at the nose. A tank modelled in pieces (Tripo's Smart Mesh) also gives up its road wheels (round pieces inside the track loop, their vertices about one distance from the axle and their rim going round, as far as vanilla's wheels) and its track runs (pieces half the hull long): on vanilla's light tanks this rule finds every vertex their wheel bones carry. A wheel must also look the same turned half a turn, as vanilla's do, unless its rim closes a full circle (a toothed sprocket). A bogie arm or a coarse wheel that would turn like a spinning diamond stays on the hull. A plane's propeller ends at the cowling, the first slice behind the blade disc as narrow as the stretch behind it. Each part is split off with its own vertices, and each cut is closed with a cap in the colours around it, so a turning turret shows no hole. A piece the turret cut only clipped (lying wholly within 5 % of the turret's height above the cut, such as a fender corner or a bolt) stays on the hull, so it does not fly with the turret.
- **Scrolling tracks.** A tank's track runs scroll as vanilla's do. They get a second material with vanilla's `PdxMeshAdvancedAnim` shader and a tread texture of their own (`<name>_tracks_*.dds`): vanilla's tread size (64 by 32) and number of links a tile (5), in the colour Tripo painted the runs. Their UVs run across the run (0.03 to 0.97, as vanilla's) and along the hull at the density vanilla's light tank has (6.05 tile lengths a main measure). The `.gfx` lists that second stream as `index = 1` of the shape, and vanilla's entity carries `texture_anim_speed = 0.5`, which scrolls it. The review sheets scroll the tread in the move clip at that speed.
- **Clips.** Each role plays vanilla's clip of the kind, moved onto the model's own pivots and scaled to its size: the barrel recoils by the share of its own length vanilla's does. A tank's turret also turns 21.7 degrees (vanilla's idle traverse) before the shot and back after it. A propeller turns 36 degrees a frame over whole turns, so the loop does not jump, and the plane is lifted so the spinning blades clear the ground. Road wheels turn by vanilla's road-wheel spin, faster for a smaller wheel so the rim moves as far. No frame sinks below the ground (a death keeps vanilla's settling), and a turret blown off in a death turns onto its flat base, drops to the ground and lands clear of the hull and its running gear, moved the short way off it with a clearance of a tenth of its own size. A cut part is set off its cut by a hair, so the file checks do not weld its rim to the body's.
- **Mod text.** The entity is vanilla's entity for the kind, renamed. An event at a node the model lacks is dropped, and a state playing an animation the model lacks plays `idle`.

The checks are `check_unit_files.py <folder> --model-kind <kind>`, the unit rules with the kind's roles and its group's limits (`vehicle` for tanks, buildings and landmarks, `air_naval` for ships and planes), plus these:

| Rule | Check |
| --- | --- |
| STATIC-SIZE, STATIC-GROUND | The size and the ground (a ship's waterline and draft) are vanilla's |
| STATIC-TRIANGLES, STATIC-SHADER | Within the kind's budget, with its shader (a tank's track runs may use `PdxMeshAdvancedAnim`) |
| STATIC-BONES, STATIC-LOCATORS, STATIC-COLLISION | The bones, locators and 8-vertex `Collision` box vanilla's entity and clips use |
| STATIC-RIGID | Every rendered vertex follows one bone wholly, so no part bends |
| STATIC-PART-GAP | No part lifts off the part it is mounted on in any frame, deaths excepted |
| STATIC-LANDING | At a death's last frame a part blown off its mount lies on its base (within 5 degrees) and on the ground (within 1 % of the height) |

`static_sheets.py` renders the close-up review of `review_unit.py` with fixed notes that say what the kind is (a tank has tracks, not feet), a 1024 px close-up of the rest pose from the front and the back quarter (a ship's mast and a plane's gun stubs are small on the six-view sheets), and a game-size sheet: the model and the vanilla model nearest the kind's median size, side by side, at the pixels a metre a vanilla soldier gets on the map. A ship's water is drawn see-through, so its hull shows as it sinks. Give `REVIEW_REQUEST.md` and the sheets to a fresh reviewer as for a unit.

## Other model kinds

The notes below come from models made by hand before the [static route](#static-and-rigid-part-models). They still hold for a model made outside it.

**Buildings and landmarks (proven on one model).**

- A tall and thin landmark (height over twice the larger side of its upper half) is sized on its height, but its base is bounded too. Vanilla's four (Big Ben, the Eiffel Tower, Hakko Ichiu, the Statue of Liberty) stand on bases of 0.17, 0.43, 0.88 and 0.82 times their height, so the contract's `size.tall_base.max_share` is 0.8757. A model whose largest horizontal side is wider than that share of the height it would get is sized on the base (largest side divided by 0.8757), so a wide paved plaza does not read as a larger monument than vanilla's. STATIC-SIZE measures the same way. An obelisk with a plaza 1.12 times its height wide came out as tall as the Statue of Liberty and 1.40 times as wide at its base. It is now 0.80 times as tall and 1.09 times as wide.
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

**Textures for any 3D model.** Use DXT5 with a full mip chain. The 2D image tool (`convert_to_dds.py`) writes uncompressed BGRA with one mip level, which suits interface images but not models. Put the `.dds` files in the model's folder and run `check_unit_files.py <folder> --repair-textures`, which rewrites them as DXT5 with mips and clears a normal map's blue channel.


## Known limits

- **Armed units.** The separate-weapon route has not passed review yet (see [Armed units](#armed-units)). An attack made for an empty hand does not read as a weapon swing, and a long weapon carried down in a death clip passes through the body or the ground.
- **Quadruped mounts.** The Tripo quadruped route has not passed review yet (see [Tripo quadrupeds and mounts](#tripo-quadrupeds-and-mounts)). Its distance weights stretch the skin at the leg joints in the rear and the fall.
- **Wings, tails and extra limbs.** Tripo's humanoid rig has no wing bones. [Secondary chains](#secondary-chains-cloaks-and-wings) give wings their own bones and motion, but the membrane can still cross in front of the body in some clips. Tails and extra limbs have no step yet.
- **Cloaks and armour.** [Secondary chains](#secondary-chains-cloaks-and-wings) stop a long cloak stretching, but some of it can still pass into the body in hard clips. Armour plates whose weight Tripo split between bones still bend a little.
- **Two-handed polearms.** A polearm held rigidly in one hand fails two-handed library swings: it crosses the head and torso and the free hand flails. There is no two-handed grip step yet. Pick one-handed clips, or fit a shorter shaft gripped near its centre.
- **A weapon sinking in a death clip.** No free repair lifts a held prop out of the ground yet. Run `fit_prop.py` again (a higher `--ground-weight`, such as 40 instead of 10, cleared it on one unit), or turn the wrist live in Blender.
- **Torso twist.** Library clips often fail review where the torso twists hard, in attacks and deaths. Expect to look for another preset, and sometimes a small live fix.
- **Static models at vanilla's budget.** A Tripo model of 20,000 triangles collapsed to a tank's 3,948 crumples its hull and running gear and thins the barrel to a blade (STATIC-SHAPE fails). Tripo's own low-poly at the budget is no better: spiky shards and a flat blade for a barrel. Make static models with Tripo's Smart Mesh at about the kind's budget (`triangle_budget` in `config/static_kinds.json`): clean hard-surface pieces, a round barrel, separate wheels and tracks.
- **Tank tracks** scroll only on a tank modelled in pieces (Smart Mesh), where the route finds its track runs. A tank in one piece keeps its tracks in the body's atlas, and its move reads as a bob. The tread is drawn by the kit (plates, a grouser and a gap a link), not taken from Tripo's texture, so close up it shows vanilla-style links in the run's own colour rather than the painted detail.
- **Open wall shells and facade notches** (a Smart Mesh factory): walls and window bays modelled as single open surfaces show as hollow recesses, and an open loop larger than 32 edges stays a notch. A new Tripo source fixes it (another Smart Mesh variant, or a closed-surface setting). A kit feature that closes large open loops would risk filling openings that belong to the design.
- **Creases, a notched capstone and thin wings** (a Smart Mesh obelisk and its eagle): a folded face, a rough cap and paper-thin wings are in the source mesh. A new Tripo source fixes them. No kit rule straightens a folded face without guessing the intended shape.
- **A higher Smart Mesh polygon count is not always better** (12,000 asked against about 6,000). The monument's figures got sharper, but its plaza came as loose wedge-shaped slabs with the ground showing between them. The factory's roofs and walls came out wavy, and 3 of its edges stay turned against their neighbours whichever way they face, so UNIT-WINDING fails. Route both counts and keep the one the review finds cleaner.
- **UNIT-PROP-CLIP** reads a point behind an open, one-sided sheet such as a cape as inside the body. Look at the named frames before changing a clip.
- **Review rounds** converge only with fixed notes and scoped rounds. Without them each fresh reviewer raises new minor items.
- **Small looks at game size.** At the map camera a unit is a few dozen pixels tall. A pale face or a torn hem is lost there. Judge fidelity on the close sheets and readability on the game-size sheet.

## When something fails

Ask where a unit stands at any time. This reads files only, costs nothing, and prints the last steps and the exact next command:

```
py -3.13 -B .tools/3d_pipeline/run_pilot.py --jobs-config <your 3d_jobs.json> --status <unit>
```

| Problem | What to do |
| --- | --- |
| Tripo's page looks signed out, or the sign-in code page vanishes | Tripo's service may be down for a few minutes. Wait, then load the page again. Nothing is lost: finished models stay in your Assets |
| A paid Tripo button was pressed and nothing seems to happen | Do not press it again. Look at the Assets panel and the credit balance first. A new tile or a lower balance means the task started |
| Tripo's Export button does nothing (no progress, no file) | It happened after many exports in one session. Do not keep pressing it. Look for a blocked-download icon in Chrome's address bar and for Tripo's export limit on your plan, then try again later. The model and its applied clips stay in your Assets |
| A clip in the export has a different name from its tile | Tripo renames on export: the tile `defeat` exports as `defeat_02` and `defeat_02` as `defeat_03`. A text-to-motion clip is named after its instruction. Write the exported name, or its first words, into `tripo.roles` |
| TRIPO-HANDS-HIGH fails | The attack holds the hands above the head. The arm-level default fixes it for an unarmed unit. If it is switched off, switch it on again, or pick another attack |
| TRIPO-NOT-DOWN or TRIPO-LIMB-IN-TORSO fails | Pick another death clip by the rule in [Pick the clips by measurement](#pick-the-clips-by-measurement). `defeat_03` passed on a humanoid |
| The weapon bends or shears in an animation | The weapon was modelled into the hand and rigged with the body. Redraw the picture with empty hands and make the weapon its own model (see [Armed units](#armed-units)) |
| Tripo's rig prompt sends you to a T-pose picture | Tripo prefers a T-pose or A-pose. The rig still works on a relaxed pose with arms away from the body. Use the T Pose picture template only when the rig fails |
| The rigged export is named `download.glb` | Tripo's server names it. Rename it to the name on the card when you move it into the inbox |
| The intake says it finds no export | The file name must be `<asset>__rigged.glb`, `<asset>__segmented.glb` or `<asset>__model.glb`, in the inbox folder you passed |
| Meshy answers 402 (old Meshy jobs) | Your account is on the free plan. Upgrade or join the contributor program. Nothing was charged |
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
