# Tripo card: <asset_slug>

One card per unit or static model. Write it with `py -3.13 -B .tools/3d_pipeline/tripo/make_card.py --jobs-config <your 3d_jobs.json> <asset_slug>`, which fills this template from the job entry and its preset (`config/tripo_presets.json`), keeps only the steps the job needs and refuses an entry that would leave a step open. Start a new job with `tripo/new_job.py`, which writes the entry from the preset. Follow the card top to bottom in [Tripo Studio](https://studio.tripo3d.ai). Write the credit balance where it asks. Press each paid button once.

| | |
| --- | --- |
| Kit commit | `<kit commit>` (the card follows the kit at this commit. If you pull a newer kit mid-run, write a new card) |
| Preset | `<preset>`: <preset label>. <preset proven> |
| Picture | `<picture>` |
| Sources | <sources> |
| Unit type | `<unit_type>` |
<!-- tripo_rig -->
| Idle posture | `<posture>` (the job's `tripo.posture`, see step 7) |
<!-- /tripo_rig -->
| Credit budget | <credit_budget> (the preset: <preset budget>) |
| Canvas workflow | <canvas>. The same steps on Tripo's Agentic Canvas, for an account that has it |
| Job folder | `<job folder>` |
| Balance before | |
<!-- armed -->

**The weapon**: <weapon>, held in the rig's `<hand>`. The picture is a front view, so that is the viewer's <viewer side>. Every hand on this card is named by the rig's side.
<!-- /armed -->

## 0. 3D-ready picture (free, only when the art is not ready)

The picture is made from existing references, never from a text prompt alone. Every reference is already in the Sources row and the job's `reference_sources`.

1. Open **Image**, model Nano Banana 2.
2. Add the subject's own reference and every researched reference from the Sources row, except a source marked `private, never uploaded`: an owner's drawing never goes to Tripo or any other online service (D-123). Its 3D-ready picture is made offline or by the mod's own image lane, and only that picture comes here.
3. Write the redraw instruction below. Fill each part in angle brackets.
4. Check that the button reads 0, then press it.
5. Compare the result with the art, detail by detail, before you go on.

`<picture sentence>`

<picture rules>

How to write `<every detail>`:

<!-- unit -->
- Name each piece of gear by the viewer's side: "a leather bracer on the viewer's left wrist".
- Gear the art shows on one side only stays on that side: "only on the viewer's left wrist".
- Gear on a side the art hides (behind a weapon, behind the body) is not guessed: write "the viewer's right wrist is not visible, do not add a bracer there".
<!-- /unit -->
<!-- static -->
- Name every part the references show, where it sits and its colour: "a short-barrelled gun in a round turret set to the front", "three road wheels a side".
- A part the references do not show is not guessed: write "the rear is not visible, do not add an engine deck there".
<!-- /static -->
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

<!-- static -->
## 2. Model (Smart Mesh, free while it shows Trial, else 100, and its texture 20)

1. On the home page add the picture and pick **Clean Topology** (Smart Mesh). Set Triangle and polycount <polycount> (<polycount reason>).
2. The button shows **Trial** or a struck price while this account has a Smart Mesh trial. Then it is free. Otherwise it must read **100**. Press it once. It makes 4 variants.
3. Turn each variant and look at every side. Pick the one whose parts are cleanest and closest to the picture: round wheels and a round barrel, closed walls and roofs, no loose slabs or wedges.
4. Press **Texture** on that variant. It must read **20**. Press it once.
<!-- /static -->
<!-- model -->
## 2. Model (30)

1. **Model**, **HD Model**. Add the body picture.
2. Settings under **Geometry & Texture**: Ultra Mesh Quality off, Texture on, 2K, Remove Lighting on, PBR on, Triangle, polycount 20000. AI model H3.1. Generate in Parts off.
3. The button must read **Generate 30**. Press it once. Turn the model and look at every side.
4. **Export** the model (GLB, free) and run `py -3.13 -B .tools/3d_pipeline/tripo/span_check.py <model.glb> <picture>`. It must print `pass`. On `fail` (TRIPO-SPAN-PICTURE: wings, arms or tail not as wide as drawn) make the model again and do not rig it.
<!-- armed -->
5. For the weapon, start a new asset. Tripo keeps the settings of the last asset but not its picture, so add the weapon picture and read the settings again.
6. The button must read **Generate 30**. Press it once. Look at every side.
7. On the weapon's Model page press **Export**: GLB, 2K. Tripo names the file after the model's title (for example `orc character 3d model.glb`). Save it as `<job folder>/armed/<asset_slug>_weapon__model.glb`.
<!-- /armed -->
<!-- shield -->
8. Make and export the shield the same way, as `<job folder>/armed/<asset_slug>_shield__model.glb`.
<!-- /shield -->
<!-- /model -->
<!-- tripo_rig -->

## 3. Rig (20)

**Rig**: Humanoid, skeleton preset Mixamo, **Auto Rig**.
<!-- winged -->

**When Tripo says "Not Ready for Auto-Rigging".** Large wings make Tripo's pre-rig check doubt a humanoid rig. It shows this dialog about ten seconds after the press, with **Generate with T-Pose** and **Try Rigging Anyway**. Do not take the T-pose: the picture's pose is the one the route wants, and a T-pose picture means a new model (30).

Each press of **Auto Rig** locks the asset on Tripo's side for about 6 minutes, and every further press starts the lock again. A rig request inside the lock is refused (HTTP 406, Tripo's code 12003, no charge), so quick presses and a quick **Try Rigging Anyway** do nothing. That is why the devil's first presses failed. After the lock has run out, **Try Rigging Anyway** does rig: the angel was rigged that way, about 6.5 minutes after its last press, and charged once (2026-11-22). The order:

1. Read the balance in the header. If it has already dropped by 20, the rig is running: wait, and press nothing.
2. Wait at least 6 minutes after any earlier press of **Auto Rig** or **Try Rigging Anyway** on this asset.
3. Check that **Auto Rig** reads 20, then press it once.
4. When the dialog shows, leave it open and press nothing for at least 6 minutes.
5. Press **Try Rigging Anyway** once. The charge of 20 shows at once. The rig itself can take many minutes when Tripo is busy: the asset tile reads "Queuing", and on the angel it took over 20 minutes and its first preset sat in "Retargeting" for over 15. Do not press again while it waits. It is done when the page shows "Rigged models can be used for animation" and the button reads **Retry 20**. On the devil one press after a wait rigged with no dialog at all. The angel's presses never did.
6. Never press twice in a row. A second press restarts the lock and the wait, and once the lock has passed every press is a new paid rig. Do not press **Retry**: it rigs again, charges 20 again and drops every clip applied. A rig that `rig_check.py` fails is repaired with `arm_seat.py` (step 6). Write the ledger's balance after only when the drop shows.
<!-- /winged -->

## 4. Candidate animations (free)

**Animate**, **Preset**. Type each name into the search box and click the middle of its tile once. Wait until **Retargeting** has gone before the next tile. The search matches names only.

<clip table>
<!-- winged -->

**The wings.** Tripo's rig has no wing bones. The route adds them and moves the wings by fixed rules per role (`docs/3d-units.md`, Secondary chains: cloaks and wings), so pick each clip for the body alone. The job keeps `"chains": [{"region": "wings"}]`, `"defend_pose": "guard"` (the guard is posed by rule, the wings wrap forward) and `"retreat_pose": "look_back"` (the wings fold along the back, the head looks back) in its `tripo` block. A burn death (`"death_kind": "burn"`) takes a standing reaction, so its row lists `hit_to_stomach`.
<!-- /winged -->

Every clip must fit the unit: its era, its weapon and its kind of creature. Never a modern boxing, kick or dance preset, even when it passes the checks (D-127). The table lists only presets that may fit, and `make_card.py` and the intake refuse a job whose roles name one of the `never_fitting` patterns in `config/tripo_presets.json`.

<!-- unarmed -->
Text-to-motion (20), <paid clip when>: name the motion, both hands, their height and the stance, written to fit the unit on the first try, for example `<paid clip>`. At most 266 characters.
<!-- /unarmed -->
<!-- armed -->
The free library has no overhead weapon blow. Searches for `attack`, `smash`, `swing`, `slam` and `hammer` find nothing (2026-11-22). The boxing and kick presets never fit a unit (D-127). For a hammer, a club, a mallet or an axe swung overhead, plan one text-to-motion attack (20) from the start.

Text-to-motion (20): `<paid clip>` Change the body words to fit the unit. Name the hand by the character's own side, which is the rig's `<hand>`. At most 266 characters.
<!-- /armed -->
<!-- /tripo_rig -->

## 5. Export

<!-- tripo_rig -->
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
<!-- /tripo_rig -->
<!-- kit_rig -->
On the Model page press **Export**, GLB, 2K, with no rig. Save it as `<job folder>/inbox/<asset_slug>__model.glb`. The kit rigs and animates it in step 9, for free. Your Tripo steps are done: release the Tripo tab.
<!-- /kit_rig -->
<!-- static -->
On the picked variant press **Export**, GLB, 2K. Save it as `<job folder>/inbox/<asset_slug>.glb`, next to the job file `<job folder>/inbox/<asset_slug>.json` that `new_job.py` wrote (it names the model and its kind, `<model_kind>`). Your Tripo steps are done: release the Tripo tab.
<!-- /static -->
<!-- tripo_rig -->

## 6. Before you leave Tripo (free)

Keep the Tripo tab and its sign-in until this step passes. A text-to-motion clip is made on the same rigged model, so it cannot be made after you leave.

First check the rig. Run `py -3.13 -B .tools/3d_pipeline/tripo/rig_check.py <the rigged export>` on the file of step 5. It must print `rig: pass`. On `rig: fail` (TRIPO-RIG-ARMS) Tripo's auto-rig put the arm chain outside the arms, as large wings made it do on the ZIN devil. For a winged unit repair it free: `py -3.13 -B .tools/3d_pipeline/tripo/arm_seat.py <the rigged export> --out <job folder>/inbox/<asset_slug>__rigged.glb`, then run `rig_check.py` on that file. It moves the arm joints onto the mesh's own arm and gives the wing skin to the shoulder for the route's wing chains, and every clip already applied keeps working. Do not press **Retry** on the Rig page instead: it charges 20, drops every applied clip, and on the devil its second rig was worse (91% of the skin on the head, no right hand joint). When `arm_seat.py` refuses or the check still fails, stop and ask before any paid step.

When a fresh rig is needed (the asset's rig is lost or its retries degenerate: on the devil both retries bound over 90% of the skin to the head), rig a fresh asset instead of retrying:

1. On the Model page press **Upload 3D Model** (free) and add the model's own export, the GLB you saved from its Model page for the span check (step 2).
2. Tripo shows **Find the Best Angle** with the model seen from its side. Press **Confirm** without turning it. Turning it there rotated the devil's mesh a quarter turn against the skeleton Tripo then built, and the rig was unusable.
3. Rig the new asset once (steps above), apply the clips again (the clips you made are under **AI Animation**, free), export, and run `rig_check.py` again.

<!-- unarmed -->
1. Run `py -3.13 -B .tools/3d_pipeline/tripo/clip_check.py <job folder>/inbox/<asset_slug>__rigged.glb --samples all --attack <free attacks> <earlier clips> --json <job folder>/evidence/clips.json`.
<!-- /unarmed -->
<!-- armed -->
1. Run `py -3.13 -B .tools/3d_pipeline/tripo/clip_check.py <job folder>/armed/<asset_slug>__body.glb --samples all --attack <free attacks> <earlier clips> --json <job folder>/evidence/clips.json`.
<!-- /armed -->
2. Read the `attack:` line. `attack: pass` names the candidates that pass. Go to step 7. With no free or earlier attack to check (the table names none for this unit), go to 3.
3. `attack: none passes` (exit code 3): make the text-to-motion clip of step 4 now (20). Write the ledger row first.
4. Export again in a fresh browser tab (step 5) and run step 6 again.
5. When the attack budget is spent and still none passes, stop and ask before more credits.

## 7. Clip choice on the map camera (free)

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
<!-- /tripo_rig -->
<!-- armed -->

## 8. Put the weapon in the hand (free, Blender)

1. Check that the job's `tripo.weapon` reads `"hand": "<hand>"`, `"part": "tripo_part_1"`, `"bone": "Weapon"` and `"release_roles": ["death"]`.
2. Run `py -3.13 -B .tools/3d_pipeline/tripo/arm_unit.py --jobs-config <your 3d_jobs.json> <asset_slug>`. It closes the `<hand>` around the weapon, holds the weapon up in idle, move, defend and retreat, fades the hold as the attack starts, drops the weapon at the death's fall, keeps it out of the body in every role and writes `<job folder>/inbox/<asset_slug>__rigged.glb`. It waits for the machine by itself.
3. Exit 0: go to step 9. Any other exit names the stage that failed and its report in `<job folder>/evidence`. Read the Armed units section of `docs/3d-units.md` before you change a grip option.
<!-- /armed -->

## 9. The run (free, Blender)

<!-- static -->
1. Run `py -3.13 -B .tools/3d_pipeline/tripo/static_model.py <job folder>/inbox/<asset_slug>.json --out <job folder>`. It turns the model into HOI4 files under `<job folder>/mod` and runs the checks. Read its one-line verdict.
2. Run `py -3.13 -B .tools/3d_pipeline/tripo/static_sheets.py <job folder>/mod/<static folder>/<asset_slug> --model-kind <model_kind> --out <job folder>/review`, look at the sheets yourself, then give them to a fresh reviewer.
<!-- /static -->
<!-- unit -->
Follow step 2 of `docs/3d-units.md` for the picture review if it is not recorded yet, then steps 8 to 10 there: `tripo_intake.py`, `run_pilot.py` and the checks. Every one of them waits for the machine by itself.
<!-- /unit -->

Then let your agent wire the model into the mod (step 12 of `docs/3d-units.md`).

| | |
| --- | --- |
| Balance after | |
| Credits spent | |
| Notes (anything that looked wrong) | |
