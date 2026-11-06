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
   - Render: `h.shot(tag, frame)` gives front, left and the HOI4 camera, with back faces culled on
     magenta. Add close-ups with `close={...}` for hands and feet.
   - Key only the bones you posed: `h.key([...], frame)`.
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
- Show hand contact to the reviewer: `h.flat_colours(True, props=[...])` renders flat colours with the
  prop in yellow. Dark-coated units read nearly black with textures.

## Weights

Weight fixes correct existing weights; they never invent a weight set.

- A crotch whose two sides each follow one thigh tears when the legs part (UNIT-SEAM). Find it with
  `h.seam_vertices(mesh, left_thigh, right_thigh)` and weight it across the pelvis and both thighs:
  `h.weight_seam(mesh, vertices, pelvis, (left_thigh, right_thigh))` (pelvis 0.40, near thigh 0.36,
  far thigh 0.24). `repair_unit.py --repairs weights` does the same blend without a live session.
- Hard edges inside one skin and four-influence limits: `repair_unit.py --repairs weights`.

## Posture and reading on the map

- Judge lean from the silhouette, not the bones. A hunched fur mass reads 20 to 30 degrees forward
  while the hips-to-head line leans back. Lift it with `h.lean([Spine02, Spine01, Spine], -degrees,
  (0.3, 0.35, 0.35))`, never with a neck pitch alone, which tears chin fur from the chest.
- On a hunched heavy body an overhead swing hides the head from the map camera. Prefer shoulder-height
  strikes for large bipeds and beasts.

## After authoring

1. Export, then run `check_unit_files.py` with `--mod-root` (it also compares the clips with the mod's
   other units). Every rule must pass, including UNIT-ANIM-KNEE, UNIT-SEAM, UNIT-ANIM-STILL,
   UNIT-ANIM-SAME and UNIT-ANIM-SHARED.
2. Re-time the entity's timed events (muzzle flashes, sounds) in `gfx/entities/*.asset` to the new
   fire and contact frames.
3. Render with `review_unit.py` and hand the sheets to a fresh reviewer, as for any unit.
4. Add what you learned to the project's lessons log, so the kit can turn it into a check or helper.
