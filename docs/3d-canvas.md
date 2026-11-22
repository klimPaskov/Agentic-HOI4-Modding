# 3D units on Tripo's Agentic Canvas

Tripo's [Agentic Canvas](https://studio.tripo3d.ai/canvas) chains Tripo's tools as nodes on one page. Each [preset](3d-units.md#presets) of the 3D route has a Canvas workflow that makes the same files as its card. Use it if you like working on one page. The card stays the default, because the Canvas costs more and is not on every account yet.

**Read this first.**

- **Cost.** A Canvas HD Model node costs 45 credits at the route's settings, where the page's HD Model costs 30 (read on both on 2026-11-22). The rig costs 20 on both and the free preset clips are free on both. So every Canvas model costs 15 credits more than the card. The table below gives each type's price.
- **Access.** Tripo is rolling the Canvas out step by step: Max and Team plans first, other plans later, free accounts may get a trial. If you do not see Agentic Canvas in Tripo's top bar, use the card.
- **One clip per file.** A Canvas Animation node holds one clip and exports one GLB. The kit joins the files for free (`tripo/join_clips.py`, step 6 below).
- **No assistant plans.** Build the workflow node by node as written here, or clone a shared one. Do not ask the Canvas assistant to plan it: on an orc it planned two untextured models, two retopologies and two textures (160 credits against 70 on the page) and stopped before the rig.
- **Credits back.** Tripo returns the credits of a failed node. It also gives 30 credits once a day for one download or share (November 2026).

## Price by type

| Preset | Canvas workflow | Card | Canvas |
| --- | --- | --- | --- |
| `humanoid`, `winged_humanoid`, `rider` | Rigged unit | 50, 70 with a made attack | 65, 85 with a made attack |
| `armed_humanoid`, `large_creature` with a weapon | Armed unit | 80, 100 with a made attack | 110, 130 with a made attack |
| `large_creature` with empty hands | Rigged unit | 50, 70 with a made attack | 65, 85 with a made attack |
| `winged_quadruped`, `quadruped`, `mount_with_rider` (the mount) | Plain model | 30 | 45 |
| `tank`, `plane`, `ship`, `building`, `landmark` | Static model | 20 to 120 (Smart Mesh is free while a trial lasts) | read each node before you run it |

An armed unit with a made attack costs 130 on the Canvas, over the preset's cap of 120. Use the card for it, or agree the extra credits first.

## The workflows

Every workflow starts the same way. Write the job and the card first (`tripo/new_job.py`, then `tripo/make_card.py`, see [3D units](3d-units.md#presets)), because the Canvas nodes take their settings and sentences from the card.

1. **Upload**: the subject's own reference and every researched reference from the card's Sources row.
2. **Generate Image**: Nano Banana 2, the card's step 0 sentence with its pose. It is free inside the monthly picture quota. Compare the picture with the art, detail by detail.

Then the workflow of the type:

**Rigged unit** (a humanoid, winged humanoid, large creature with empty hands, rider):

3. **HD Model** from the picture: Image input, Texture on, Remove Lighting on, 2K, PBR on, Generate in Parts off, Triangle, polycount 20000. It must read **45**.
4. **Rigging** from the HD Model: Humanoid, skeleton preset Mixamo. It must read **20**.
5. **Animation**, one node for each candidate in the card's clip table, each wired from the Rigging node. Open its Library tab, search the preset's name and tick it. Free. Wait until the node has finished before the next one.
6. **Export** each Animation node: GLB, Export Skeleton on, Animation stay in Place on (read each switch first, it remembers the last export). If Chrome blocks the second download from the same tab, allow it or export from a fresh tab. Save each file in `<job folder>/inbox/clips/`, then join them:

   ```
   py -3.13 -B .tools/3d_pipeline/tripo/join_clips.py <job folder>/inbox/clips/*.glb --out <job folder>/inbox/<asset_slug>__rigged.glb
   ```

   It prints the clips it joined. Go on with the card's step 6 (the attack check) on the joined file. When it asks for a made attack, make it with text to motion on an Animation node of the same Rigging node, read its price first, export it and join again. Whether the Canvas Animation node offers text to motion was not checked yet (November 2026). If it does not, a unit that needs a made attack goes the card's way from the start.

**Armed unit** (a humanoid or large creature with a weapon):

3. A second **Generate Image** from the same Upload: the card's step 1 weapon sentence. Free.
4. **HD Model** of the body picture and **HD Model** of the weapon picture, both with the settings above. Each must read **45**.
5. **Rigging** from the body's HD Model, as above (20).
6. **Animation** nodes and **Export** as for a rigged unit, with the joined file saved as `<job folder>/armed/<asset_slug>__body.glb`. Export the weapon's HD Model (GLB, 2K) as `<job folder>/armed/<asset_slug>_weapon__model.glb`. Then follow the card from step 6. Its step 8 puts the weapon in the hand.

**Plain model** (a winged quadruped, a four-legged beast, a mount):

3. **HD Model** with the settings above (45).
4. **Export** it: GLB, 2K, no rig, as `<job folder>/inbox/<asset_slug>__model.glb`. The kit rigs and animates it for free (card step 9).

**Static model** (a tank, plane, ship, building or landmark):

3. **Smart Mesh** from the picture: Triangle, the card's polycount. Read the price on the node before you run it. It makes variants: pick the cleanest as the card's step 2 says.
4. **Texture Generation** on that variant: PBR on, 2K. Read the price first.
5. **Export**: GLB, 2K, as `<job folder>/inbox/<asset_slug>.glb`, next to the job file `new_job.py` wrote. Then the card's step 9.

## Save it, share it, reuse it

- Saving, copying and sharing a workflow is free. To make the next unit of the same type, open your workflow, replace the picture in the Upload node and run the nodes again from Generate Image.
- **Share** (top right of the canvas) gives a link. Set Who can access to "Anyone with the link" to share it. Whoever opens it can clone it into their own account.
- Private assets in a shared workflow show as a "Private asset" placeholder, and the person who clones it puts their own picture there. Never share a workflow that holds someone else's private drawing. On a free account every saved asset is public by default, so a drawing you upload there is published.
