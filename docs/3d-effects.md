# Effects for 3D units: muzzle flashes, spells, fire and explosions

Tripo makes a unit's mesh, textures, rig and body clips. It does not make HOI4's effects. This page is the step of the [3D route](3d-units.md) that adds them: muzzle flashes and gun smoke for firing units and tanks, fire for fire creatures, spells and glowing eyes for casters, dust for physical blows, and explosions, fire and smoke for wrecks, sinking ships, crashing planes and destroyed buildings.

## What an effect is in HOI4

An effect is not part of a model. Three things make one, and the game draws it:

1. A **particle system**, a `.asset` file under `gfx/particles` (`particle = { name = "..._file" subsystem = { ... } }`), registered under a name in a `.gfx` file (`pdxparticle = { name = "..._particle" type = "..._file" scale = 1 }`).
2. A **locator**, a named point in the `.mesh`, parented to a bone so it follows the part through every clip. Its offset is in the bone's own frame. Vanilla's tanks carry `barrel` on the bone `barrel_tip`, and its infantry carry `head` on the bone `head`.
3. An **event** in a state of the entity: `event = { time = 0.5 node = "muzzle" particle = "mg_muzzle_particle" keep_particle = yes }`. The state plays a clip, and the event fires the particle at the locator `time` seconds into it.

`time` is in seconds of the clip, the frame divided by 30. `calibrate_effects.py` measured it on vanilla's destroyed landmarks: each one that fires after its start does so within 0.3 s of the frame its clip hides a part. The Forbidden City hides its roof at frame 186 (6.2 s) and fires at 6.0, Nanjing hides a corner at frame 126 (4.2 s) and fires at 4.1. Read as frames, those explosions would go off in the first fifth of a second of a six-second collapse.

A glow that never stops, such as a hooded caster's eyes, is the same thing with an endless particle: an event at time 0 in each state, whose particle keeps vanilla's `duration=-1`. Vanilla's infantry keeps its cigarette smoke at the `head` locator in idle this way, and its buildings keep their map lamps lit. The unit shader (`PdxMeshAdvanced`) also takes emission from the normal map's blue channel, but that lights only the texels already painted, which are too few to read at map size, and it changes the unit's maps (D-86). So a glow is always a particle.

## Effects that fit the unit

Every effect fits its unit (D-127): its era, its weapon and its kind of creature. A world without gunpowder has no muzzle flash, and a medieval or fantasy unit never gets modern gunfire. The kit enforces this with a **setting**: each job says what its unit's world has, and a profile that needs something the setting lacks is refused (EFFECT-FIT). Which effect a creature has comes from its mod's own canon, never from a guess. The kit's profiles are general, one per kind of effect (D-134). The choice for a mod's creature lives in that mod's own job files, in the job's `effects` block, never in the kit.

| Setting tag | Means |
| --- | --- |
| `gunpowder` | firearms, cannons and explosives (HOI4's own era, a modern faction) |
| `magic` | the unit casts spells (a mage, a necromancer) |
| `fire_creature` | the unit shoots or breathes fire by its own nature (a fire demon, a dragon) |

Physical effects (a wing's dust, a stone fist's chips) and ship, plane and building deaths need no tag.

## Locator names

One scheme for every type: `<effect>_<part>`, with `_l` or `_r` by the rig's side (the character's own left, not the viewer's). The profiles place these locators themselves, so a job never names or writes one.

| Locator | Bone | Placed at |
| --- | --- | --- |
| `fire_mouth` | Head | the front of the head skin at mouth height |
| `fire_hand_l`, `fire_hand_r` | LeftHand, RightHand | the hand skin's point farthest from the wrist |
| `glow_eye_l`, `glow_eye_r` | Head | the upper front of the head on that side, pushed back a quarter of the head's depth (inside a hood) |
| `cast_hand_r` | RightHand | the casting hand's tip |
| `gust_wing_l`, `gust_wing_r` | the wing bone at the tip | the wing's tip on that side |
| `dust_hand_l`, `dust_hand_r` | LeftHand, RightHand | the fist's tip |
| `ember_body`, `smoke_body` | Spine02 | the centre of the upper spine's own part |
| `burn` | Spine02 | the burn death (`lib/tripo_burn.py`) |
| `blast_ring`, `fire_deck` | chassie | the turret ring (measured on the turret, hung from the hull) and the deck |

A static model keeps vanilla's names: `barrel`, `hit_effect_locator1` and `2`, `engine1`, `explosion1`, `fire1`.

## The profiles

A profile is one effect of a unit, in `.tools/3d_pipeline/config/effects.json`. Each Tripo preset lists the profiles that fit its type (`effects` in `config/tripo_presets.json`), and a job picks among them.

| Profile | Needs | Locators | Fires in | Frame | Particles |
| --- | --- | --- | --- | --- | --- |
| `tank_cannon` | gunpowder | `barrel` | attack, defend, support_attack | recoil | vanilla's light tank flash and smoke |
| `heavy_cannon` | gunpowder | `barrel` | attack, defend, support_attack | recoil | vanilla's heavy tank flash and smoke |
| `tank_wreck` | gunpowder | `blast_ring`, `fire_deck` | death | part_leaves | vanilla's `vehicle_explode_effect`, then fire and smoke copied from vanilla |
| `firearm` | gunpowder | `muzzle` (an existing weapon locator) | attack, defend, support_attack | recoil | vanilla's rifle flash and smoke |
| `ship_death` | none | `hit_effect_locator1` and `2` | death | start, 0.5 s apart | vanilla's `ship_explosion_particle` |
| `plane_crash` | none | `engine1` | death | start | vanilla's `explosion_particle` |
| `building_destroyed` | none | `explosion1`, `fire1` | death | start, fire 1.5 s later | vanilla's building explosion, fire and dust |
| `hand_mouth_fire` | fire_creature | `fire_hand_l`, `fire_hand_r`, `fire_mouth` | attack | strike | flame from both hands and the mouth, orange-red, with dark smoke |
| `heavy_fire` | fire_creature | `fire_mouth`, `fire_hand_l`, `fire_hand_r` | attack | strike | a heavier lava-orange flame with near-black smoke |
| `ember_idle` | fire_creature | `ember_body` | idle | start, looping | slow embers, copied from vanilla's sparks |
| `wing_gust` | none | `gust_wing_l`, `gust_wing_r` | attack | strike | vanilla's dust cloud thrown from the wing tips |
| `strike_dust` | none | `dust_hand_l`, `dust_hand_r` | attack | strike | vanilla's dust and debris of a damaged building (a stone or earth creature's blow) |
| `eye_glow` | magic | `glow_eye_l`, `glow_eye_r` | every state but death | start, looping | a faint glow, purple by default, copied from vanilla's map lamp |
| `spell_cast` | magic | `cast_hand_r` | attack, support_attack | peak | a swirl with dark wisps, purple by default |
| `smoke_death` | magic | `smoke_body` | death | start | coloured smoke for the whole death, with the swirl, purple by default |
| `fire_breath` | fire_creature | `fire_mouth` | attack | strike | vanilla's flamethrower flame and smoke as they are |

Vanilla has no spells and no creature that shoots fire. Those effects copy the nearest vanilla particle and change only its colour and its size: the flame tank's `flamethrower_particle` for fire and spells, its smoke for wisps, the map lamp `lamp_red_particle` for the eyes, the power line `sparks_effect` for embers, `city_smoke_particle` for a death in smoke. Each coloured subsystem takes the new hue at its own brightness. Grey ones (smoke) keep their colour, unless the particle is marked `tint_grey` (dark or coloured smoke). The size is the `scale` of the registration. Nothing else of the particle changes.

Not covered: loose feathers in a wing beat or a death. Vanilla has no feather particle, and a copy may change only colour and scale, so feathers need a new particle with its own texture. That is a decision for the maintainer, not a route step. A teleport flash waits for a teleport-like clip.

### Where a new locator goes

| Spot | Measured as |
| --- | --- |
| `locator` | an existing locator of the mesh, kept as it is |
| `hand_tip` | the mean of the farthest 5% of the hand's vertices (the hand bone and its children) along the forearm to hand direction |
| `head_front` | the mean of the farthest 5% of the head's lower vertices toward the unit's front (the mouth). The front runs from the heels to the toes, or -z on a model without feet |
| `eye` | on one side of the head (the side runs from the right hand to the left), the farthest 5% of the head's upper vertices toward the front, pushed back by `inset` of the head's depth (0.25 by default) |
| `wing_tip` | of the vertices whose strongest bone is a wing bone, the farthest from the mid-plane on that side, parented to the wing bone carrying most of them |
| `bone_top`, `bone_bottom`, `bone_centre` | the top centre, the bottom centre or the centre of the bone's own part, without the parts mounted on it (the hull's deck, not the turret's roof) |
| `box_share` | a point of the model's box, as shares of its size per axis |

A slot's `parent` hangs the locator from another bone than the one it was measured on. A first try hung the wreck's blast from the turret, and on the review sheet it flew away with the turret.

### When it fires

| Frame rule | Measured as |
| --- | --- |
| `start` | frame 0. A looping particle starts here and glows through the state |
| `recoil` | the first frame the gun moves back: of the locator's bone and its two parents, the one whose own translation moves most, at the frame it passes 10% of that move |
| `strike` | the frame the locator reaches farthest toward the unit's front, from the hips in that frame |
| `part_leaves` | the first frame the locator has moved 2% of the model's height from its place at frame 0 |
| `peak` | the frame the locator is farthest from its place at frame 0 (a hand raised to cast) |

A job may give a slot a whole frame instead (`frames`). A state that has no clip of its own uses its role's clip: defend and support_attack play attack when the unit has no clip for them.

## The step

Run it after the unit's files pass their checks and before the review sheets. No Blender and no credits.

1. Add an `effects` block to the job entry (at the top level or in its `tripo` block). Name only profiles the preset lists and the mod's canon gives the unit, and give the setting the unit's world has:

   ```json
   "effects": {"profiles": ["hand_mouth_fire"], "setting": ["fire_creature"]}
   ```

   A tank: `{"profiles": ["tank_cannon", "tank_wreck"], "setting": ["gunpowder"]}`. A hooded caster: `{"profiles": ["eye_glow", "spell_cast", "smoke_death"], "setting": ["magic"]}`. Another colour: `"colour": {"spell_swirl": [90, 200, 255]}`. A fixed frame: `"frames": {"cast_hand_r": 31}`.

2. Run the step on the unit's files. A Tripo unit:

   ```
   py -3.13 -B .tools/3d_pipeline/tripo/effects_stage.py <job>/runtime/files --job <job entry .json> --preset <preset>
   ```

   A static model (a tank, ship, plane or building) also gets its entity and particle files written:

   ```
   py -3.13 -B .tools/3d_pipeline/tripo/effects_stage.py <job folder>/mod/gfx/models/<folder>/<name> --job <job .json> --preset <preset> --entity <job folder>/mod/gfx/entities/<name>.asset --mod-root <job folder>/mod
   ```

   It writes the new locators into the `.mesh`, the plan `<stem>_effects.json` beside it, and prints each locator and each event with its frame and time. It ends with PASS or FAIL. A static entity's particle events at the same locators are replaced: vanilla's light tank entity, which the static route copies, fired a rifle's flash from the tank gun. A state the entity lacks for a role that fires (a tank's death) is added.

3. Render the effects sheet and look at it:

   ```
   py -3.13 -B .tools/3d_pipeline/tripo/effects_sheet.py <unit files folder> --out <job folder>/review/effects.png
   ```

   Each clip that fires gets a row per view, at the frame before its first event, the event's frame and 2, 6 and 15 frames after. The particles are stand-ins, stamped "particles: stand-in": a short orange flash, a small grey gun-smoke puff, fire that rises, grey smoke that rises slowly and grows, a spell's or eye's glow in its colour, a blast that swells. Look that each one starts on its frame, at its locator, on the right part, and stays with the part. The game-size and close-up sheets (`review_unit.py`, `tripo/weapon_sheets.py`, `tripo/clip_sheet.py`, `tripo/static_sheets.py`) draw the same stand-ins. Give the sheet to a fresh reviewer with this question: does each effect start at its place on its frame and stay on its part? A finding on a creature's effect can come from its clip: a creature's right-hand fire sat by its face because its attack clip, a boxing guard, held that fist there.

4. Wire the unit (`wire_unit.py`, step 12 of the route). It writes the plan's events into the entity's states, the copied particle files to `gfx/particles/<stem>_<particle>.asset` and their registration to `gfx/entities/<stem>_effects_particles.gfx`. The plan's sounds join the job's `sound_plan` at the same frames. A frame the job's own `sound_plan` already gives the role keeps the job's sound.

5. Ask for the in-game checks below.

Run the step again whenever the unit's clips change. EFFECT-FRAME fails a plan whose frames no longer match the clips.

## Sounds

Sounds stay with the `sound_plan`. A profile's slot may name a vanilla soundeffect (`light_armour_fire` for the tank gun, `explosion_fuel_small` for the wreck), and the plan carries it at the same frame as its particle. Fire, spells and dust have no fitting vanilla sound, so they have none until the mod adds one to its `sound_plan`. Every sound event is written as `time = frame / 30`.

## The checks

`tripo/effects_stage.py` and `wire_unit.py` run them, and `--check-only` runs them on an existing plan.

| Rule | Fails when |
| --- | --- |
| EFFECT-FIT | A profile needs a setting tag the job lacks, or the preset does not list it for the type (D-127) |
| EFFECT-LOCATOR | The mesh lacks a plan's locator, or it hangs from another bone |
| EFFECT-FRAME | An event's frame is outside its clip, or its rule now measures another frame (a clip was changed after the step: run it again) |
| EFFECT-ON-PART | In a clip that fires it, a locator's distance to the nearest vertices of its part changes by more than 3% of the model's height. The part bends away from the locator, so the effect would hang in the air. Deaths are left out, since parts fly off there |
| EFFECT-PARTICLE | A vanilla particle is not a registered one, or a copied particle's vanilla file is not in the game folder |

## In-game checks

Only the game draws the real particles. These are checked later by the night runner or on the WSL game copy, never by starting the game during the work. For each unit, place it on the map at the usual zoom and watch each state.

| Effect | Check in the game |
| --- | --- |
| every effect | The particle starts at its locator, on its frame, and moves with its part. Its size against the unit looks like vanilla's at map zoom (the registration's `scale` is the dial). No error about the particle files in `error.log` |
| `tank_cannon`, `heavy_cannon`, `firearm` | The flash is at the muzzle, not inside the barrel or in front of it, on the shot's recoil, and the gun's sound plays with it |
| `tank_wreck` | The explosion bursts at the turret ring as the turret leaves and stays at the hull, the deck burns and smokes after it, and the smoke lasts as long as the wreck shows. Note how long the game holds the death's last frame |
| `ship_death`, `plane_crash`, `building_destroyed` | The explosions come where the hull, engine or roof is, in the order and spacing of the plan |
| `hand_mouth_fire`, `heavy_fire`, `fire_breath` | The flame comes from each hand and the mouth on the strike, toward the front, in its colour, with its smoke, and does not read as a gunshot or hide the head |
| `ember_idle`, `eye_glow` | The glow stays at its place through every state that plays it, faint, and does not grow brighter each time the unit changes state (an endless particle fired again on each state change) |
| `spell_cast`, `smoke_death` | The swirl is at the raised hand on the cast, the death's smoke covers the body as it unravels, in its colour and not fire |
| `wing_gust`, `strike_dust` | The dust comes from the wing tips or the fists on the strike, and nothing glows |
| sounds | Each sound lands on its particle's frame (the seconds rule), not 30 times later |

## What vanilla does

`calibrate_effects.py` surveys the installed game: every particle event of every unit and building entity, the bone each locator follows (read from the entity's mesh), the states and times, the `.asset` file of each particle, and every registered particle, fired by a unit or not. It writes `.tools/3d_pipeline/config/effects_vanilla.json` and the table below. Run it again after a game update:

```
py -3.13 -B .tools/3d_pipeline/calibrate_effects.py
```

The table shows the eight most used particle events of each kind. The JSON holds every one. An infantry weapon's locator has no bone in the table because it lives in the weapon's own mesh, attached to the soldier. Vanilla's cavalry fires no particles at all, and its tanks have no death effects: the `tank_wreck` profile takes its explosion from plane and landmark destructions.

<!-- calibrate_effects begin -->
| Kind | Particle | Locator (bone) | States | Time (s) | Entities | File |
| --- | --- | --- | --- | --- | --- | --- |
| infantry | `rifle_cartridge_particle` | cartridge (none) | attack, defend, support_attack | 0, 0.3, 0.9, 1.015 ... | 15 | `infantry/rifle_cartridge.asset` |
| infantry | `mg_cartridge_particle` | cartridge (none) | attack, defend, support_attack | 0, 0.5 | 13 | `infantry/mg_cartridge.asset` |
| infantry | `mg_muzzle_particle` | muzzle (none) | attack, defend, support_attack | 0, 0.5 | 13 | `infantry/mg_muzzle.asset` |
| infantry | `mg_muzzle_smoke_particle` | muzzle (none) | attack, defend, support_attack | 0, 0.5 | 13 | `infantry/mg_muzzle_smoke.asset` |
| infantry | `cigarette_smoke_particle` | head (none) | idle | 0 | 11 | `infantry/cigarette_smoke.asset` |
| infantry | `pistol_muzzle_particle` | muzzle (none) | attack, defend, support_attack | 0, 0.2, 0.55, 0.6 ... | 8 | `infantry/rifle_muzzle.asset` |
| infantry | `rifle_muzzle_particle` | muzzle (none) | attack, defend, support_attack | 0, 1.015, 1.15 | 8 | `infantry/rifle_muzzle.asset` |
| infantry | `blood_particle` | head (head) | death | 0 | 3 | `infantry/blood.asset` |
| cavalry | none | | | | 0 | |
| artillery | `artillery_cartridge_particle` | smoke (barrel_base) | attack, defend, support_attack | 0.3 | 3 | `infantry/artillery_cartridge.asset` |
| artillery | `artillery_tyre_tracks_particle` | left_wheel (orient_base) | attack, defend, support_attack | 0 | 3 | `infantry/artillery_tyre_tracks.asset` |
| artillery | `artillery_tyre_tracks_particle` | right_wheel (orient_base) | attack, defend, support_attack | 0 | 3 | `infantry/artillery_tyre_tracks.asset` |
| artillery | `light_tank_attack_barrel_particle` | muzzle (barrel_end) | attack, defend, support_attack | 0 | 3 | `vehicles/light_tank_attack_barrel.asset` |
| artillery | `tank_moving_tracks_particle` | left_track_1 (body) | move | 0 | 3 | `vehicles/tank_moving_tracks.asset` |
| artillery | `tank_moving_tracks_particle` | left_track_2 (body) | move | 0 | 3 | `vehicles/tank_moving_tracks.asset` |
| artillery | `tank_moving_tracks_particle` | right_track_1 (body) | move | 0 | 3 | `vehicles/tank_moving_tracks.asset` |
| artillery | `tank_moving_tracks_particle` | right_track_2 (body) | move | 0 | 3 | `vehicles/tank_moving_tracks.asset` |
| tank | `tank_moving_tracks_particle` | left_tracks (chassie, root, tank_base, wheel_suspention) | move, retreat | 0 | 40 | `vehicles/tank_moving_tracks.asset` |
| tank | `tank_moving_tracks_particle` | right_tracks (chassie, root, tank_base, wheel_suspention) | move, retreat | 0 | 40 | `vehicles/tank_moving_tracks.asset` |
| tank | `tank_exhaust_particle` | right_exhaust (chassie) | move, retreat, training | 0 | 30 | `vehicles/tank_exhaust.asset` |
| tank | `tank_exhaust_particle` | left_exhaust (chassie) | move, retreat, training | 0 | 29 | `vehicles/tank_exhaust.asset` |
| tank | `light_tank_attack_barrel_particle` | barrel (barrel_base, barrel_tip, canon_front_tip) | attack, defend, support_attack | 0, 3.4 | 28 | `vehicles/light_tank_attack_barrel.asset` |
| tank | `light_tank_attack_barrel_smoke_particle` | barrel (barrel_base, barrel_tip) | attack, defend, support_attack | 0 | 27 | `vehicles/light_tank_attack_barrel_smoke.asset` |
| tank | `tank_exhaust_particle` | exhaust (chassie, root) | move, move_mud, move_snow, retreat ... | 0 | 10 | `vehicles/tank_exhaust.asset` |
| tank | `heavy_tank_attack_barrel_particle` | barrel (barrel_tip) | attack, defend, support_attack | 0 | 5 | `vehicles/heavy_tank_attack_barrel.asset` |
| vehicle | `cigarette_smoke_particle` | head (head) | idle | 0 | 13 | `infantry/cigarette_smoke.asset` |
| vehicle | `tank_moving_tracks_particle` | left_tracks (chassi, chassie) | attack, move, retreat, support_attack | 0 | 10 | `vehicles/tank_moving_tracks.asset` |
| vehicle | `tank_moving_tracks_particle` | right_tracks (chassi, chassie) | attack, move, retreat, support_attack | 0 | 10 | `vehicles/tank_moving_tracks.asset` |
| vehicle | `mechanized_attack_barrel_particle` | barrel (weapon) | attack, defend, support_attack | 0 | 7 | `vehicles/mechanized_attack_barrel.asset` |
| vehicle | `tank_moving_tracks_particle` | left_wheel (chassi, chassie) | attack, move, retreat | 0 | 6 | `vehicles/tank_moving_tracks.asset` |
| vehicle | `tank_moving_tracks_particle` | right_wheel (chassi, chassie) | attack, move, retreat | 0 | 6 | `vehicles/tank_moving_tracks.asset` |
| vehicle | `mechanized_attack_barrel_small_particle` | barrel (barrel_tip) | attack, defend, support_attack | 0 | 2 | `vehicles/mechanized_attack_barrel.asset` |
| vehicle | `tank_exhaust_particle` | exhaust (chassie) | move, retreat, training | 0 | 2 | `vehicles/tank_exhaust.asset` |
| plane | `explosion_particle` | engine1 (root) | crash | 0 | 24 | `vehicles/explosion.asset` |
| plane | `bomb_particle` | bomb (root) | bomb | 0 | 23 | `vehicles/bomb.asset` |
| plane | `napalm_particle` | bomb (root) | firebomb | 0 | 23 | `vehicles/napalm.asset` |
| plane | `vehicle_explode_effect` | none (none) | explode | 0 | 20 | `vehicles/vehicle_explode_effect.asset` |
| plane | `plane_mg_muzzle_particle` | gun1 (root) | fire | 0 | 19 | `vehicles/plane_mg_muzzle.asset` |
| plane | `explosion_particle` | engine2 (mother, root) | crash | 0 | 18 | `vehicles/explosion.asset` |
| plane | `plane_mg_muzzle_particle` | gun2 (root) | fire | 0, 0.02, 0.3 | 18 | `vehicles/plane_mg_muzzle.asset` |
| plane | `bomb_particle` | none (none) | bomb | 0 | 13 | `vehicles/bomb.asset` |
| ship | `ship_damaged_smoke_particle` | hit_effect_locator2 (root) | damaged_attack, damaged_attack_looping, damaged_defend, damaged_defend_loop | 0, 0.2, 0.5, 0.7 ... | 26 | `vehicles/ship_damaged_smoke.asset` |
| ship | `ship_explosion_particle` | hit_effect_locator2 (root) | damaged_attack, damaged_defend, death | 0, 0.5, 0.9, 1 ... | 26 | `vehicles/ship_explosion.asset` |
| ship | `ship_explosion_particle` | hit_effect_locator1 (root) | damaged_attack, damaged_defend, death | 0, 0.1, 0.8, 1 ... | 25 | `vehicles/ship_explosion.asset` |
| ship | `ship_damaged_smoke_particle` | hit_effect_locator1 (root) | damaged_attack, damaged_attack_looping, damaged_defend, damaged_defend_loop | 0, 0.2 | 24 | `vehicles/ship_damaged_smoke.asset` |
| ship | `ship_idle_particle` | none (none) | death, idle | 0, 2, 2.5, 4 ... | 22 | `ship_idle.asset` |
| ship | `ship_fire_water_shockwave_particle` | none (none) | damaged_defend, damaged_defend_loop, defend | 0 | 21 | `vehicles/ship_fire_water_shockwave.asset` |
| ship | `ship_fire_particle` | turret_01 (Algerie_anim:turret_01, turret_01) | attack, damaged_attack, damaged_attack_looping, damaged_defend_loop ... | 0 | 15 | `vehicles/ship_fire.asset` |
| ship | `ship_fire_particle` | turret_02 (Algerie_anim:turret_02, turret_02) | attack, damaged_attack, damaged_attack_looping, damaged_defend_loop ... | 0.1, 0.15, 0.2 | 15 | `vehicles/ship_fire.asset` |
| building | `building_damaged_particle` | damage_locator_01 (none) | damaged, destroyed, idle | 0.1 | 23 | `environment/building_damaged.asset` |
| building | `building_damaged_particle` | damage_locator_02 (none) | damaged, destroyed, idle | 0.1 | 23 | `environment/building_damaged.asset` |
| building | `building_damaged_particle` | damage_locator_03 (none) | damaged, destroyed | 0.1 | 12 | `environment/building_damaged.asset` |
| building | `ship_damaged_smoke_particle` | fire1 (none) | destroyed | 0.1 | 5 | `vehicles/ship_damaged_smoke.asset` |
| building | `city_fire_2_particle` | damage_locator_02 (none) | burning | 0.2 | 4 | `environment/city_fire_2.asset` |
| building | `city_fire_l_particle` | damage_locator_01 (none) | burning | 0.1 | 4 | `environment/city_fire.asset` |
| building | `city_smoke_particle` | damage_locator_03 (none) | damaged | 0.1 | 4 | `environment/city_smoke.asset` |
| building | `ship_damaged_smoke_particle` | fire2 (none) | destroyed | 0.1 | 4 | `vehicles/ship_damaged_smoke.asset` |
| landmark | `ship_explosion_particle` | explosion1 (Root, base, root) | destroy | 0, 0.2, 1.7, 1.8 ... | 10 | `vehicles/ship_explosion.asset` |
| landmark | `ship_explosion_particle` | explosion2 (base, root) | destroy | 0, 4.1, 4.5, 4.8 ... | 9 | `vehicles/ship_explosion.asset` |
| landmark | `ship_explosion_particle` | explosion3 (base, root) | destroy | 5, 6.5, 7, 8 ... | 8 | `vehicles/ship_explosion.asset` |
| landmark | `ship_explosion_particle` | explosion4 (base, root) | destroy | 4, 7.5, 10.2, 13.5 ... | 8 | `vehicles/ship_explosion.asset` |
| landmark | `building_fire_particle` | fire1 (root) | destroy | 5, 10.5, 17 | 5 | `environment/building_fire.asset` |
| landmark | `building_fire_particle` | fire3 (root) | destroy | 2, 4, 10, 13 ... | 5 | `environment/building_fire.asset` |
| landmark | `vehicle_explode_effect` | impact (Root, destroy_root, root) | destroy | 3.9, 9, 15.5 | 5 | `vehicles/vehicle_explode_effect.asset` |
| landmark | `building_explode_effect` | explosion5 (root) | destroy | 9, 13 | 4 | `environment/building_explode_effect.asset` |
<!-- calibrate_effects end -->
