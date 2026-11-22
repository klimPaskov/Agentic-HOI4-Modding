# 3D units on Tripo's Agentic Canvas

Tripo's [Agentic Canvas](https://studio.tripo3d.ai/canvas) chains Tripo's tools as nodes on one page. Each [preset](3d-units.md#presets) of the 3D route has a Canvas workflow that makes the same files as its card. Use it if you like working on one page. The card stays the default, because the Canvas costs more and is not on every account yet.

**Read this first.**

- **Cost.** A Canvas HD Model node costs 45 credits at the route's settings, where the page's HD Model costs 30 (read on both on 2026-11-22). The rig costs 20 on both and the free preset clips are free on both. So every Canvas model costs 15 credits more than the card. The table below gives each type's price.
- **Access.** Tripo is rolling the Canvas out step by step: Max and Team plans first, other plans later, free accounts may get a trial. If you do not see Agentic Canvas in Tripo's top bar, use the card.
- **One clip per file.** A Canvas Animation node holds one clip and exports one GLB. The kit joins the files for free (`tripo/join_clips.py`, step 6 below).
- **No assistant plans.** Build the workflow node by node as written here, or clone a shared one. Do not ask the Canvas assistant to plan it: on an armed humanoid it planned two untextured models, two retopologies and two textures (160 credits against 70 on the page) and stopped before the rig.
- **The assistant cannot pick the type.** It cannot see an Upload node's picture, and with the picture attached in its chat it called a test picture of a humanoid with empty hands an armed humanoid. The kit's `tripo/pick_preset.py` picks the type by fixed rules.
- **Credits back.** Tripo returns the credits of a failed node. It also gives 30 credits once a day for one download or share (November 2026).

## Price by type

| Preset | Canvas workflow | Card | Canvas |
| --- | --- | --- | --- |
| `humanoid`, `winged_humanoid`, `rider` | Rigged unit | 50, 70 with a made attack | 65, 85 with a made attack |
| `armed_humanoid`, `large_creature` with a weapon | Armed unit | 80, 100 with a made attack | 95, 115 with a made attack, the weapon made on the page. 110, 130 with the weapon on the Canvas too |
| `large_creature` with empty hands | Rigged unit | 50, 70 with a made attack | 65, 85 with a made attack |
| `winged_quadruped`, `quadruped`, `mount_with_rider` (the mount) | Plain model | 30 | 45 |
| `tank`, `plane`, `ship`, `building`, `landmark` | Static model | 20 to 120 (Smart Mesh is free while a trial lasts) | read each node before you run it |

Make an armed unit's weapon on the page, as the card's step 2 does, and the body and rig on the Canvas: that keeps it at 95, or 115 with a made attack, inside the preset's cap of 120. With the weapon on the Canvas too it costs 130 with a made attack, over the cap.

**Proven on 2026-11-22.** The armed-humanoid route test, a unit with a hand axe, ran the armed workflow this way: the Canvas body 45, the axe on the page 30, the Canvas rig 20, nine free preset clips, 95 credits in all. The joined clips passed the card's attack check (`chop`), so no made attack was needed.

## The workflows

Every workflow starts the same way. Write the job and the card first (`tripo/new_job.py`, then `tripo/make_card.py`, see [3D units](3d-units.md#presets)), because the Canvas nodes take their settings and sentences from the card.

1. **Upload**: the subject's own reference and every researched reference from the card's Sources row, but never a private drawing (D-123): give only the 3D-ready picture made from it. By hand, the Upload node opens your file picker. An agent calls `CV.stubPicker()` from `tripo/tripo_canvas.js` first and feeds the file through its browser tool, because it cannot drive the system picker.
2. **Generate Image**: Nano Banana 2, the card's step 0 sentence with its pose. It is free inside the monthly picture quota. Compare the picture with the art, detail by detail.

Then the workflow of the type:

**Rigged unit** (a humanoid, winged humanoid, large creature with empty hands, rider):

3. **HD Model** from the picture: Image input, Texture on, Remove Lighting on, 2K, PBR on, Generate in Parts off, Triangle, polycount 20000. It must read **45**.
4. **Rigging** from the HD Model: Humanoid, skeleton preset Mixamo. It must read **20**.
5. **Animation**, one node for each candidate in the card's clip table, each made from the Rigging node: select and hover the Rigging result and press its **Animation** chip. Open the new node's **Library** tab, search the preset's name and tick it. Free. The nodes generate side by side, so add them all, then wait.
6. **Export** each Animation node from its **Export** chip: GLB, 2K. The dialog starts with **Number of Animations** 0: open it and press **Select All** (the one clip). Switch **Export Skeleton** and **Animation stay in Place** on (stay in place starts off). Chrome starts one download per page load, so reload the canvas page before each further export. Save each file in `<job folder>/inbox/clips/`, then join them:

   ```
   py -3.13 -B .tools/3d_pipeline/tripo/join_clips.py <job folder>/inbox/clips/*.glb --out <job folder>/inbox/<asset_slug>__rigged.glb
   ```

   It prints the clips it joined. Go on with the card's step 6 (the attack check) on the joined file. When it asks for a made attack, make it on a new Animation node of the same Rigging node: its **Generate** tab is text to motion, 20 credits for up to 5 seconds, the card's step 4 prompt. Export it and join again.

**Armed unit** (a humanoid or large creature with a weapon):

3. A second **Generate Image** from the same Upload: the card's step 1 weapon sentence. Free.
4. **HD Model** of the body picture with the settings above (**45**). Make the weapon on Tripo's page instead, as the card's step 2 does (**30**): its file is the same, and it saves 15 credits. A weapon HD Model node on the Canvas reads 45.
5. **Rigging** from the body's HD Model, as above (20).
6. **Animation** nodes and **Export** as for a rigged unit, with the joined file saved as `<job folder>/armed/<asset_slug>__body.glb`. Export the weapon model (GLB, 2K) as `<job folder>/armed/<asset_slug>_weapon__model.glb`. Then follow the card from step 6. Its step 8 puts the weapon in the hand.

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
