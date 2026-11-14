# Tripo card: <asset_slug>

One card per model. Follow it top to bottom in [Tripo Studio](https://studio.tripo3d.ai). Write the credit balance where it asks. Press each paid button once.

| | |
| --- | --- |
| Picture | `<path to the approved picture>` |
| Kind | unit, armed unit, or static model |
| Unit type | `<unit_type from the job>` |
| Credit budget | `<credits>` |
| Inbox | `<job folder>/inbox` |
| Balance before | |

## 1. Model (30)

1. **Model**, **HD Model**. Add the picture.
2. **Generate Multi-Views** (free). Check that left, back and right match the picture.
3. From the views, **Multi-View to 3D**. Settings under **Geometry & Texture**: Ultra Mesh Quality off, Texture on, 2K, Remove Lighting on, PBR on, Triangle, polycount 20000. AI model H3.1. Generate in Parts off.
4. The button must read **Generate 30**. Press it once. Turn the model and look at every side.

## 2. Weapon split (40, armed units only)

1. **Segment**, **Custom**. Instruction: `Separate the model into exactly two parts: the <weapon> (the whole weapon) and the <creature> (everything else, including the hand that holds it).`
2. **Start Segmenting**. Check that the weapon is one colour and the body the other. Press **Save**.

## 3. Rig (20, units only)

**Rig**: Humanoid, skeleton preset Mixamo, **Auto Rig**.

## 4. Animations (free, units only)

**Animate**, **Preset**. Click each preset once and watch it play.

| Role | Preset |
| --- | --- |
| idle | `<preset>` |
| move | `<preset>` |
| attack | `<preset>` |
| defend | `<preset>` |
| retreat | `<preset>` |
| death | `<preset>` |

## 5. Export

- Unit: on the Animate page, **Export**. GLB, Export Skeleton on, Animation stay in Place on, tick the six animations. Save into the inbox as `<asset_slug>__rigged.glb`.
- Static model: on the Model page, **Export**. GLB, 2K. Save into the inbox as `<asset_slug>__model.glb`.

| | |
| --- | --- |
| Balance after | |
| Credits spent | |
| Notes (anything that looked wrong) | |
