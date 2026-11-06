# Live authoring in Blender (the escalation path)

Read before posing, keying, re-weighting or re-seating a prop by hand in a live Blender session. The
default route measures the body, picks a preset and lets code do the spatial work. This path is for
everything a preset cannot do, under the same checks and the same independent review.

## When to take it

- `measure_body.py` or a stage verdict says `escalate`: the body is not eligible for a preset (wings,
  extra limbs, tentacles, no legs, a rider fused to its mount), or its measured shape disagrees with the
  job's unit type.
- A role needs motion of its own: no library or preset clip reads as the role on this body, the unit
  must not share clips (UNIT-ANIM-SHARED), or a clip failed the independent review twice.
- A project requires it: some author every new rig and animation live, others give every unit
  unique clips. Follow the project's own rules where they are stricter.

Free live work comes before any paid clip or new generation.

## Set up

1. Use an interactive Blender MCP with code execution and viewport screenshots (the Blender Lab MCP
   the kit pins). Run your own Blender instance on its own port, and never drive another author's.
2. Open the unit's last checkpoint `.blend`, or import the exported `.mesh` with io_pdx_mesh. Repair
   the mesh first with `repair_unit.py` (winding, bridges, weights) so you author on a clean body.
3. Load the helpers once per session:

   ```python
   import importlib, sys
   sys.path.insert(0, r"<repository>/.tools/3d_pipeline/authoring")
   import live_helpers as h
   importlib.reload(h)
   h.setup_scene()
   ```

   Keep them on `sys.path`. Opening a `.blend` clears `bpy.app.driver_namespace`.
4. If you cache vertex groups or weights in your own code, key the cache by the mesh data pointer or
   the vertex count, never by the mesh name. A provider names every body mesh `char1.001`, so a cache
   keyed by name returns the wrong indices after you open another `.blend`. The kit's helpers keep no
   cache.

## Author one role

1. Plan in words first: what the role must read as on the map camera, its key poses (contact,
   passing, peak, recovery) and their frames. A loop's last key equals its first.
2. For each key, in **one** `execute_blender_code` call: pose, check, key. The session evaluates the
   action again between calls, so an unkeyed pose is gone in the next call.
   - Turn one bone or one limb at a time: `h.rot`, `h.lean` (a pitch spread down the spine),
     `h.solve_leg` (knee toward the toes), `h.place_limb`, `h.reach` (a wrist to a point).
   - Temporary IK is fine: `h.ikp` solves once, copies the visual pose and removes the constraint.
   - Plant the feet that carry weight: `h.plant(frame, thigh, shin, foot, [foot groups], mesh)` puts the
     lowest skinned vertex of that foot on the ground and keys the leg.
   - Check every leg: `h.knee_bend(thigh, shin, foot)` must not be negative.
   - Key only the bones you posed: `h.key([...], frame)`. Key before you render: a render evaluates
     the action again, so an unkeyed pose is gone from it.
   - Render: `h.shot(tag, frame)` gives front, left and the HOI4 camera, with back faces culled on
     magenta. Add close-ups with `close={...}` for hands and feet.
3. Look at the in-betweens: `h.strip(tag, frames)` renders one view at several frames.
4. Split long work (an export plus dozens of renders) into several calls. The bridge times out while
   Blender keeps working, so confirm by file timestamps.

Never key from a table, a formula, a loop over frames or another clip's curves. The helpers only
place, measure, render and key what you name at the call site.

## Props in hand

- Fit a one-handed prop with `fit_prop.py` first: it searches 42 grip directions against every clip for free. Come here when its verdict escalates, or for the second hand of a two-handed hold.
- Before posing, check that the prop's grip sits inside the closed hand at rest. A provider rig often
  parks the weapon beside the hip, and every later pose then shows an open palm beside the gun. Key
  the prop bone into the palm first.
- Make each grip once by eye, then record it in the prop's own frame: `grip = h.grip_record(hand,
  prop_base, prop_tip, fingers)`. At every key, `h.seat_grip(grip, hand, upper, fore, frame)` puts the
  wrist, its turn and the finger curl back on the prop, wherever the prop moved. A grip kept in world
  space floats off the prop as soon as it recoils.
- A main hand on a raked pistol grip: turn it so its knuckle line (`h.knuckle_line(index, little)`)
  runs up the grip with the fingers across it, then curl the fingers. A support hand: knuckle line
  along the barrel, palm on the top surface, fingers over the far side. Orient hands from the rest-pose
  finger bones, never from hand-typed rotations.
- Measure contact: `h.grip_gap([knuckle points], prop_object)` should stay under a tenth of the hand's
  length in every key.
- A provider hand that is open or splayed never reads as a grip, however the fingers are curled. Replace
  it with a grip shell: delete the hand past the wrist (every vertex dominated by the hand or finger
  bones), fill and triangulate the wrist, model a fist-sized bevelled block with knuckle bumps on the
  hand's knuckle line, bind it fully to the hand bone, give it the body material with every UV on the
  glove's texel, and seat the prop's grip at the block's centre at every key. Export it as an extra
  shape; the PDX exporter needs triangles after hole fills. A hull of the open fingers reads as a flat
  wedge, and a box around them grows to crate size. Generating the fists closed avoids all of this.
- Slots and vents in a prop whose side walls are missing show magenta: join a dark core inside the prop,
  with the prop's material and a dark texel.
- Keep a held shaft off the body line and at an angle to the map camera. A prop held across the chest
  vanishes into the forearms and torso, and one pointed at the camera vanishes in the map view.
- A rigid pole with a hanging load on one bone cannot lie down believably. Give the pole and the load
  their own bones, or a joint between them, before you pose a fall.
- Show hand contact to the reviewer: `h.flat_colours(True, props=[...])` renders flat colours with the
  prop in yellow. Dark-coated units read nearly black with textures.

## Weights

Weight fixes correct existing weights; they never invent a weight set.

- A crotch whose two sides each follow one thigh tears when the legs part (UNIT-SEAM). Find it with
  `h.seam_vertices(mesh, left_thigh, right_thigh)` and weight it across the pelvis and both thighs:
  `h.weight_seam(mesh, vertices, pelvis, (left_thigh, right_thigh))` (pelvis 0.40, near thigh 0.36,
  far thigh 0.24). `repair_unit.py --repairs weights` does the same blend without a live session.
- Hard edges inside one skin and four-influence limits: `repair_unit.py --repairs weights`.
- Long coats and skirts weighted to the thighs tear and fan in every stride, crouch and lying pose. Give
  them their own bones under the hips, give the thighs at most 0.15 weight on the cloth, and blend
  toward the hem. Key the cloth bones to follow each thigh part of the way.
- Cloth weighted to a tail root follows the tail like a wing. Weight it to the pelvis, but do not
  switch hard: blend its weights across the seam from the tail to the pelvis over a short distance
  (about a quarter of a unit passed UNIT-BRIDGE), or the seam bridges two body parts.
- A cloak weighted to the arms stretches and flaps whenever an arm moves. Move arm weight off any cloth
  more than a short distance from the arm bone segments, ramped over a similar distance, onto the spine
  chain and shoulders. A colour mask alone misses part of the cloth.
- A small island (an ear, a tuft, a strap, a crate part) split between two bones tears into spikes once
  those bones move apart. Bind each island wholly to its dominant bone.
- Measure stretch the kit's way: `h.stretch_share(mesh, frame)` is the share of edges that
  UNIT-ANIM-STRETCH counts at that frame, from the kit's own constants. A hand-made gauge read about
  0.8 times that number. Check the worst frames and keep the share under the kit's limit.

## Rigs with extra limbs

- Count limbs from the geometry, not from a render: `measure_body.py` slices the body and counts the
  separate pieces per slice. A long clawed arm can read as a tentacle in a render.
- Provider rigs on extra limbs can misplace joints as well as weights: a hand bone sitting on a claw, a
  chain bone that owns no vertices. Before posing, check that each bone's head lies inside its own
  vertices and that every chain bone owns some; place joints at the centres of slices taken along the
  limb from the shoulder.
- Before posing a limb, compare its bone head with the mesh cross-section at that height. If the head
  sits outside the section (a knee bone in front of the knee), the posed joint leaves the mesh. Move the
  bone to the section's centre in edit mode first.
- Open wings by turning the finger bones, not the wing-arm bone: turning the wing-arm bone around its
  own head swings the wing roots across the spine into an X. Watch the left and right wing-root
  separation at every frame.

## Posture and reading on the map

- Judge lean from the silhouette, not the bones. A hunched fur mass reads 20 to 30 degrees forward
  while the hips-to-head line leans back. Lift it with `h.lean([Spine02, Spine01, Spine], -degrees,
  (0.3, 0.35, 0.35))`, never with a neck pitch alone, which tears chin fur from the chest.
- On a hunched heavy body an overhead swing hides the head from the map camera. Prefer shoulder-height
  strikes for large bipeds and beasts.
- Roles read at map zoom through whole-body changes, not limb tweaks. A retreat turns the body away
  (about 60 degrees) with the arms pulled back; training moves the feet with lunges; a support attack
  pitches the whole torso into a crouch (on a Meshy humanoid pitch `Hips`, since an upper-spine pitch
  barely moves the head); a death lies flat, face down for spiky or long-limbed bodies.
  `check_unit_files.py` fails two roles with the same motion (UNIT-ANIM-SAME), but a reviewer judges the
  read.
- A digitigrade or splayed leg breaks a two-bone solve with a forward pole: the knee goes out to the
  side and a lifted step reads as a sideways kick. Solve those legs with the pole along the leg's own
  bend, or pose the swing leg by turning the thigh and shin about the body's forward axis. Keep
  `h.knee_bend` for the checks.
- A tail placed to hang and then lie along the ground, with a heading and a little lift, keyed at each
  beat, reads better than a fixed curve, which reads as a rigid rod.
- In a death clip, find what holds the body up before moving it: `h.lowest_regions(frame)` lists the
  lowest point of each body region (and of each separate prop). Move the lowest group, not the hips.
- Ground corrections in a death clip pile up and fight later pose edits. Keep a correction key only at
  the deepest frame of each dip, and delete the stale correction keys before you re-pose a fall.

## Vehicles

Use the `vehicle` unit type for a tank, an armoured car or any wheeled or tracked unit. It has no Meshy
route: rig and animate it here, and the checks judge it against vanilla's vehicle group.

- A generated vehicle often has fused rigid parts: faces that join the chassis to the wheels and the
  turret. Skinning smears wheels into fans and stripes the turret skirt. Rip each bridge face onto one
  part. Turret bridges go to the turret. Outer fender pieces (radius beyond the tyre) go to the chassis.
  The kit welds vertices that coincide (1e-5 of the height), so move the ripped part's seam vertices a
  few millimetres inward, or the stretch check still sees one surface. That opens seam loops, so close
  them afterwards with `repair_unit.py --repairs holes winding`. Keep the gap near 6 mm: with 2 mm the
  caps joined both sides again.
- Put each wheel bone at the centre of its tyre ring, not at the hub vertex or the bounding box. Fit a
  circle to the tyre's rim vertices in the wheel's plane and place the bone head on its centre. An
  off-centre pivot makes the wheel dip below the ground while it spins (UNIT-ANIM-GROUND).
- Keep turret traverse within what the model allows. A turret that is not round shows slivers between the
  skirt and the deck past about 25 degrees of yaw, so author at most 25 degrees. Make the roles read
  through other motion: recoil on the attack, rock and weave on the move, spin on the wheels or tracks,
  a lurch on the retreat and a settling slump on the death.

## Repairing the mesh

- A surface that folds through itself, one the winding repair cannot resolve (a shoulder pad and collar
  in one patch), is fixed by replacing the folded region with the mirrored opposite side. Negate x, swap
  the Left and Right vertex groups, reverse the faces and mirror the corner normals. Then delete the
  remaining fold edges and cap each opening with a fan around a new centre vertex wound like its
  neighbours.
- UNIT-NORMALS means corner normals point against their faces and shade as pale flat facets. The winding
  repair keeps imported normals, so flip those corner normals, or recalculate them on a welded copy and
  copy the result back.
- If an edit leaves the per-face `sharp_face` flags from the import, io_pdx_mesh splits every corner and a
  stream goes past 65,535 vertices (UNIT-STREAM-VERTICES fails after export). Clear them first with
  `h.clear_sharp_faces(mesh)`, which also smooths every face and returns how many were sharp.

## After authoring

1. Run `h.normalize_quaternion_keys(action)` on every clip first. A key and its negation are the same
   rotation, but when two keys sit in opposite hemispheres the blend between them turns the long way
   (a blade sweeps through the ground). It flips those keys and returns how many it changed.
   Export each clip with `h.export_clip(action, path)`, never with the io_pdx_mesh export operator: the
   operator ignores its start and end frames unless the scene's custom-range setting is on and exports
   the scene's range, so clips came out padded or cut to 80 or 85 samples. `export_clip` uses the action's
   own range and fails when the file's sample count differs. It also writes the clip at 30 frames a
   second, the rate vanilla soldiers and horses play at. io_pdx_mesh writes the scene's rate, and a scene
   from factory settings runs at 24. When the scene is not at 30, `export_clip` first scales the action's
   keys so the clip keeps the length it played in the scene, then leaves the scene at 30.
   `h.setup_scene()` sets 30 in a new scene before any action exists, so author at 30 from the start. Then run `check_unit_files.py` with `--mod-root` (it also compares the clips with the mod's
   other units). Every rule must pass, including UNIT-ANIM-KNEE, UNIT-SEAM, UNIT-ANIM-STILL,
   UNIT-ANIM-SAME and UNIT-ANIM-SHARED.
2. Re-time the entity's timed events (muzzle flashes, sounds) in `gfx/entities/*.asset` to the new
   fire and contact frames.
3. Render with `review_unit.py` and hand the sheets to a fresh reviewer, as for any unit. Fresh reviewers
   look at different frames each round, so keep every earlier round's reply and check its findings
   again yourself before the next review: a fix elsewhere can bring an old defect back.
4. Add what you learned to the project's lessons log, so the kit can turn it into a check or helper.
