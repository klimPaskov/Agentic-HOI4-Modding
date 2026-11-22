# Tripo card: <asset_slug>

One card per unit or static model. Write it with `py -3.13 -B .tools/3d_pipeline/tripo/make_card.py --jobs-config <your 3d_jobs.json> <asset_slug>`, which fills this template from the job entry, keeps only the steps the job needs and refuses an entry that would leave a step open. Follow the card top to bottom in [Tripo Studio](https://studio.tripo3d.ai). Write the credit balance where it asks. Press each paid button once.

| | |
| --- | --- |
| Kit commit | `<kit commit>` (the card follows the kit at this commit. If you pull a newer kit mid-run, write a new card) |
| Picture | `<picture>` |
| Sources | <sources> |
| Unit type | `<unit_type>` |
| Idle posture | `<posture>` (the job's `tripo.posture`, see step 7) |
| Credit budget | <credit_budget> |
| Job folder | `<job folder>` |
| Balance before | |
<!-- armed -->

**The weapon**: <weapon>, held in the rig's `<hand>`. The picture is a front view, so that is the viewer's <viewer side>. Every hand on this card is named by the rig's side.
<!-- /armed -->

## 0. 3D-ready picture (free, only when the art is not ready)

The picture is made from existing references, never from a text prompt alone. Every reference is already in the Sources row and the job's `reference_sources`.

1. Open **Image**, model Nano Banana 2.
2. Add the subject's own reference and every researched reference from the Sources row.
3. Write the redraw instruction below. Fill each part in angle brackets.
4. Check that the button reads 0, then press it.
5. Compare the result with the art, detail by detail, before you go on.

`Redraw this exact <subject> for 3D modelling. Keep <every detail>. Invent nothing. Neutral pose for rigging: arms hanging about 30 degrees away from the body, both hands empty, open and relaxed. Full body, front view, feet visible, plain light grey background, even soft lighting.`

For a building or landmark, use this instead. The Image tool takes three uploads at most, so put related photos side by side in one picture.

`A 3D-ready picture of one <building> in the style of the references. Keep <every detail>. Only a small yard just round the building, with a ragged edge that can sink into the terrain, no square paved plate. Every post, brace and beam thick and chunky. Elevated three-quarter view, the whole building in frame, plain light grey background, soft even light with no cast shadows, no smoke, no people, no trees.`

Before you go on, look at the picture: no plate base, and no brace thinner than about 1.5 % of the building's longest side. Redraw it (free) if either fails.

How to write `<every detail>`:

- Name each piece of gear by the viewer's side: "a leather bracer on the viewer's left wrist".
- Gear the art shows on one side only stays on that side: "only on the viewer's left wrist".
- Gear on a side the art hides (behind a weapon, behind the body) is not guessed: write "the viewer's right wrist is not visible, do not add a bracer there".
<!-- armed -->
- End with `Remove the <weapon> completely. Both hands are empty.` The weapon is its own model (step 2).
<!-- /armed -->
<!-- armed -->

## 1. Weapon picture (free)

1. Open **Image** again, model Nano Banana 2, and add the same art.
2. Write: `Redraw only the <weapon> from this picture for 3D modelling. Keep its exact shape, proportions, materials, colours and every mark. Remove the hand and everything else. Invent nothing. The whole <weapon> standing upright, head at the top, seen from the side that shows the head's shape, on a plain light grey background, even soft lighting.`
3. Check that the button reads 0, then press it.
4. Compare the weapon with the art. The grip stage scales it by the job's `tripo.weapon.grip_options`: `length_ratio` (its length over the body's height in the art) and `grip` (where the hand holds it, from the butt). Read both from the art again and correct the job if they differ.
<!-- /armed -->
<!-- shield -->
5. Make the shield's picture the same way: `Redraw only the <shield> from this picture ...`, the shield seen from the front.
<!-- /shield -->

## 2. Model (30)

1. **Model**, **HD Model**. Add the body picture.
2. Settings under **Geometry & Texture**: Ultra Mesh Quality off, Texture on, 2K, Remove Lighting on, PBR on, Triangle, polycount 20000. AI model H3.1. Generate in Parts off.
3. The button must read **Generate 30**. Press it once. Turn the model and look at every side.
<!-- armed -->
4. For the weapon, start a new asset. Tripo keeps the settings of the last asset but not its picture, so add the weapon picture and read the settings again.
5. The button must read **Generate 30**. Press it once. Look at every side.
6. On the weapon's Model page press **Export**: GLB, 2K. Tripo names the file after the model's title (for example `orc character 3d model.glb`). Save it as `<job folder>/armed/<asset_slug>_weapon__model.glb`.
<!-- /armed -->
<!-- shield -->
7. Make and export the shield the same way, as `<job folder>/armed/<asset_slug>_shield__model.glb`.
<!-- /shield -->

## 3. Rig (20, units only)

**Rig**: Humanoid, skeleton preset Mixamo, **Auto Rig**.

## 4. Candidate animations (free, units only)

**Animate**, **Preset**. Type each name into the search box and click the middle of its tile once. Wait until **Retargeting** has gone before the next tile. The search matches names only.

<!-- unarmed -->
| Role | Candidates |
| --- | --- |
| idle | `idle` |
| move | `walk` |
| attack | `box_01`, and every earlier clip under **AI Animation** made for an unarmed unit |
| defend | `hit_to_stomach`, `hit_to_body_01` |
| retreat | `flee_01` |
| death | `defeat`, `defeat_02`, `fall` |

Text-to-motion (20), only when step 6 says no attack passes: name the motion, both hands, their height and the stance, for example `lunges one huge fast step, both arms thrust straight forward at chest height, then jerks back`. At most 280 characters.
<!-- /unarmed -->
<!-- armed -->
| Role | Candidates |
| --- | --- |
| idle | `idle` |
| move | `walk` |
| attack | `chop`, and every earlier clip under **AI Animation** made for a weapon in one hand |
| defend | `hit_to_stomach`, `hit_to_body_01` |
| retreat | `flee_01` |
| death | `defeat`, `defeat_02`, `fall` |

The free library has no overhead weapon blow. Searches for `attack`, `smash`, `swing`, `slam` and `hammer` find nothing (2026-11-22). `box_01` is an empty-hand punch and does not read as a weapon swing. For a hammer, a club, a mallet or an axe swung overhead, plan one text-to-motion attack (20) from the start.

Text-to-motion (20): `A heavy warrior raises the <weapon> in his own <hand words> high over his head, then smashes it down hard in front of him, torso leaning forward, feet planted.` Change the body words to fit the unit. Name the hand by the character's own side, which is the rig's `<hand>`. At most 280 characters.
<!-- /armed -->

## 5. Export

1. On the Animate page press **Export**. Format GLB.
2. **Export Skeleton** must read on. **Animation stay in Place** must read on. Tripo remembers each switch from the last export, so read it first (its `aria-checked` is `true` when on) and click it only when it reads off.
3. Under **Number of Animations** press **Select All**.
4. Tripo builds the file in about a minute and saves it as `tripo_convert_<id>.glb`.
<!-- unarmed -->
5. Move it into the inbox as `<job folder>/inbox/<asset_slug>__rigged.glb`.
<!-- /unarmed -->
<!-- armed -->
5. Move it to `<job folder>/armed/<asset_slug>__body.glb`. Not into the inbox: the inbox gets the gripped body from step 8.
<!-- /armed -->

Tripo renames two presets on export: the tile `defeat` exports as `defeat_02`, and `defeat_02` as `defeat_03`. Read clip names from the file, not from the tiles.

A static model: on the Model page press **Export**, GLB, 2K, and save it as `<job folder>/inbox/<asset_slug>__model.glb`. Steps 3 to 8 do not apply.

## 6. Before you leave Tripo (free)

Keep the Tripo tab and its sign-in until this step passes. A text-to-motion clip is made on the same rigged model, so it cannot be made after you leave.

<!-- unarmed -->
1. Run `py -3.13 -B .tools/3d_pipeline/tripo/clip_check.py <job folder>/inbox/<asset_slug>__rigged.glb --samples all --attack box_01 <earlier clips> --json <job folder>/evidence/clips.json`.
<!-- /unarmed -->
<!-- armed -->
1. Run `py -3.13 -B .tools/3d_pipeline/tripo/clip_check.py <job folder>/armed/<asset_slug>__body.glb --samples all --attack chop <earlier clips> --json <job folder>/evidence/clips.json`.
<!-- /armed -->
2. Read the `attack:` line. `attack: pass` names the candidates that pass. Go to step 7.
3. `attack: none passes` (exit code 3): make the text-to-motion clip of step 4 now (20). Write the ledger row first.
4. Export again in a fresh browser tab (step 5) and run step 6 again.
5. When the attack budget is spent and still none passes, stop and ask before more credits.

## 7. Clip choice on the map camera (free, units only)

The game shows the unit about 60 pixels tall from above and in front. There only the outline reads, so pick each clip by how its outline reads there, against the unit's other clips.

1. Write the idle posture into the job: `"posture": "upright"` or `"posture": "hunched"` in its `tripo` block. A soldier stands upright. An undead, a beast-man or a cowering creature is hunched. For hunched, also set `"idle_pose": "hunch"` when no Tripo idle hunches enough.
2. A first run has no earlier `.mesh` of this body. Then write each role into the job's `tripo.roles` by the step 6 numbers (the candidate with the lowest stretch that passes), finish the card once, and come back to this step with that run's mesh, `<job folder>/runtime/files/<runtime_stem>.mesh`.
<!-- unarmed -->
3. Run `py -3.13 -B .tools/3d_pipeline/tripo/pose_check.py <job folder>/inbox/<asset_slug>__rigged.glb <earlier run's .mesh> --unarmed --map --idle "<first words of the idle>" --attack <attack candidates> --gait <move and retreat candidates>`.
<!-- /unarmed -->
<!-- armed -->
3. Run `py -3.13 -B .tools/3d_pipeline/tripo/pose_check.py <job folder>/armed/<asset_slug>__body.glb <earlier run's .mesh> --hand <hand> --map --idle "<first words of the idle>" --attack <attack candidates> --gait <move and retreat candidates>`.
<!-- /armed -->
4. Read the `idle posture` line. It must say `hunched` for a hunched unit and `upright` for an upright one.
5. Read each `outline` line. The attack and the defend must each show a hand spread under 0.80, or they read as a T-pose. The attack's strike must be at least 5 px outside the body, or its reach foreshortens into the body and reads as nothing. The attack and the defend must not both be wide spreads, or they read as each other.
6. Take the `attack pick` line. It already leaves out an attack that fails these.
7. Write the chosen clip for each role into the job's `tripo.roles` and here. A text-to-motion clip is named by its first words, before the first comma.

| Role | Chosen clip | Map reading |
| --- | --- | --- |
| idle | | posture |
| attack | | spread, strike px |
| defend | | spread |

After the run, `tripo_checks.py` judges the exported clips by the same rules (TRIPO-MAP-POSTURE, TRIPO-MAP-SPREAD, TRIPO-MAP-REACH, TRIPO-MAP-SAME). A unit that fails one goes back to this step, not to review.
<!-- armed -->

## 8. Put the weapon in the hand (free, Blender)

1. Check that the job's `tripo.weapon` reads `"hand": "<hand>"`, `"part": "tripo_part_1"`, `"bone": "Weapon"` and `"release_roles": ["death"]`.
2. Run `py -3.13 -B .tools/3d_pipeline/tripo/arm_unit.py --jobs-config <your 3d_jobs.json> <asset_slug>`. It closes the `<hand>` around the weapon, holds the weapon up in idle, move, defend and retreat, fades the hold as the attack starts, drops the weapon at the death's fall, keeps it out of the body in every role and writes `<job folder>/inbox/<asset_slug>__rigged.glb`. It waits for the machine by itself.
3. Exit 0: go to step 9. Any other exit names the stage that failed and its report in `<job folder>/evidence`. Read the Armed units section of `docs/3d-units.md` before you change a grip option.
<!-- /armed -->

## 9. The run (free, Blender)

Follow step 2 of `docs/3d-units.md` for the picture review if it is not recorded yet, then steps 8 to 10 there: `tripo_intake.py`, `run_pilot.py` and the checks. Every one of them waits for the machine by itself.

| | |
| --- | --- |
| Balance after | |
| Credits spent | |
| Notes (anything that looked wrong) | |
