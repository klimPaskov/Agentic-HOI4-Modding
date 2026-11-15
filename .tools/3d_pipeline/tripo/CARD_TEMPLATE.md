# Tripo card: <asset_slug>

One card per model. Follow it top to bottom in [Tripo Studio](https://studio.tripo3d.ai). Write the credit balance where it asks. Press each paid button once.

| | |
| --- | --- |
| Picture | `<path to the approved 3D-ready picture>` |
| Kind | unit or static model |
| Unit type | `<unit_type from the job>` |
| Credit budget | `<credits>` |
| Inbox | `<job folder>/inbox` |
| Balance before | |

## 0. 3D-ready picture (free, only when the art is not ready)

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

| | |
| --- | --- |
| Balance after | |
| Credits spent | |
| Notes (anything that looked wrong) | |
