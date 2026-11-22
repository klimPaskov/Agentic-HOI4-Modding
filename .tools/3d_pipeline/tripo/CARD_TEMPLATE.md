# Tripo card: <asset_slug>

One card per model. Follow it top to bottom in [Tripo Studio](https://studio.tripo3d.ai). Write the credit balance where it asks. Press each paid button once.

| | |
| --- | --- |
| Picture | `<path to the approved 3D-ready picture>` |
| Sources | `<the subject's own reference, and for a real-world subject the real references research found, one per line>` (fill before the first paid press) |
| Kind | unit or static model |
| Unit type | `<unit_type from the job>` |
| Idle posture | `upright` or `hunched` (the job's `tripo.posture`, see step 5) |
| Credit budget | `<credits>` |
| Inbox | `<job folder>/inbox` |
| Balance before | |

## 0. 3D-ready picture (free, only when the art is not ready)

The picture is made from existing references, never from a text prompt alone.

1. Start from the subject's own reference: the owner's drawing or the mod's art.
2. For a real-world subject (a tank, a ship, a uniform, a building style), research real references first: photographs, plans, museum pieces, period art. Save each in the job's `refs` folder or note its link.
3. Give the subject's reference and the researched references to the Image tool together.
4. Write every reference into the Sources row above and into the job's `reference_sources`. The picture review refuses a job whose list is empty.

The picture must show one subject, full body, front view, on a plain light background, arms hanging about 30 degrees away from the body and both hands empty and open. If the art is not like this, open **Image**, model Nano Banana 2, add the art and write: `Redraw this exact <subject> for 3D modelling. Keep <every detail, gear named by the viewer's side>. Invent nothing. Neutral pose for rigging: <pose and hands>. Full body, front view, feet visible, plain light grey background, even soft lighting.` The button must read 0. Compare the result with the art before you go on.

## 1. Model (30)

1. **Model**, **HD Model**. Add the picture.
2. Settings under **Geometry & Texture**: Ultra Mesh Quality off, Texture on, 2K, Remove Lighting on, PBR on, Triangle, polycount 20000. AI model H3.1. Generate in Parts off.
3. The button must read **Generate 30**. Press it once. Turn the model and look at every side.

## 2. Rig (20, units only)

**Rig**: Humanoid, skeleton preset Mixamo, **Auto Rig**.

## 3. Candidate animations (free, units only)

**Animate**, **Preset**. Type each name into the search box and click its tile once.

| Role | Candidates |
| --- | --- |
| idle | `idle` |
| move | `walk` |
| attack | `<presets, or earlier clips under AI Animation>` |
| defend | `hit_to_stomach`, `hit_to_body_01` |
| retreat | `flee_01` |
| death | `defeat`, `defeat_02`, `fall` |

Text-to-motion (20), only if the card says so: `<instruction naming the motion, the hand, the height and the stance>`.

## 4. Export

- Unit: on the Animate page, **Export**. GLB, Export Skeleton on, Animation stay in Place on. **Number of Animations**, **Select All**. Move the downloaded `tripo_convert_<id>.glb` into the inbox as `<asset_slug>__rigged.glb`.
- Static model: on the Model page, **Export**. GLB, 2K. Save into the inbox as `<asset_slug>__model.glb`.

Tripo renames two presets on export: the tile `defeat` exports as `defeat_02`, and `defeat_02` as `defeat_03`.

## 5. Clip choice on the map camera (free, units only)

The game shows the unit about 60 pixels tall from above and in front. There only the outline reads, so pick each clip by how its outline reads there, against the unit's other clips. Do this before the run.

1. Write the idle posture into the job: `"posture": "upright"` or `"posture": "hunched"` in its `tripo` block. A soldier stands upright. An undead, a beast-man or a cowering creature is hunched. For hunched, also set `"idle_pose": "hunch"` when no Tripo idle hunches enough.
2. Run `py -3.13 -B .tools/3d_pipeline/tripo/pose_check.py <inbox>/<asset_slug>__rigged.glb <earlier run's .mesh> --map --idle "<first words of the idle>" --attack <attack candidates> --gait <move and retreat candidates>`, with `--unarmed` for an unarmed unit.
3. Read the `idle posture` line. It must say `hunched` for a hunched unit and `upright` for an upright one.
4. Read each `outline` line. The attack and the defend must each show a hand spread under 0.80, or they read as a T-pose. The attack's strike must be at least 5 px outside the body, or its reach foreshortens into the body and reads as nothing. The attack and the defend must not both be wide spreads, or they read as each other.
5. Take the `attack pick` line. It already leaves out an attack that fails these. Write down the chosen clip for each role here.

| Role | Chosen clip | Map reading |
| --- | --- | --- |
| idle | | posture |
| attack | | spread, strike px |
| defend | | spread |

After the run, `tripo_checks.py` judges the exported clips by the same rules (TRIPO-MAP-POSTURE, TRIPO-MAP-SPREAD, TRIPO-MAP-REACH, TRIPO-MAP-SAME). A unit that fails one goes back to this step, not to review.

| | |
| --- | --- |
| Balance after | |
| Credits spent | |
| Notes (anything that looked wrong) | |
