# Starting forces, unit identity, and 3D model planning

This reference belongs to the `hoi4-feature-planning` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## 3.13 Starting forces and reinforcement pathway standard

When a feature creates, releases, transforms, restores, or revives a country that is expected to fight, survive, defend itself, or matter militarily, the spec must define its starting forces. Newly appearing countries should not spawn as empty tags unless they are explicitly non-military administrative placeholders and the spec explains why.

Starting units must be dynamic. Do not define one flat number of divisions for every country. The spec should explain what makes the starting force stronger, weaker, larger, smaller, better equipped, more irregular, more professional, more defensive, more foreign-backed, or stranger.

Useful scaling factors include:

- escalation tier and escalation value
- feature threat, crisis pressure, escalation variant state, and ordinary stage state
- local population, industry, terrain, ports, rail hubs, depots, and capital control
- local legitimacy, public support, militia networks, and command obedience
- defecting army districts, security units, sailors, railway guards, border guards, police forces, or factory guards
- captured equipment, depot vulnerability, foreign aid, volunteer corridors, and faction support
- parent-country weakness, missed deadlines, lost objectives, supply failure, war state, and previous choices
- whether the tag is an ordinary republic, emergency committee, factory state, ancient restoration, partisan movement, cult, railway state, naval state, or other special actor

For every meaningful new or transformed country, map:

- starting division families or template concepts
- expected starting strength in weak, normal, severe, and extreme-route openings
- equipment and manpower source
- whether units are militia, regular defectors, border guards, mountain detachments, factory guards, railway troops, sailors, cavalry, foreign volunteers, ancient levies, or special extreme-route formations
- starting commanders, officer shortages, or leader ties when relevant
- defensive bonuses, training penalties, supply weaknesses, morale problems, or legitimacy risks
- how the package affects threat meters, foreign attention, depot pressure, old-movement resurgence, or parent-country authority
- what report, feature text, or localisation direction should explain why those troops exist

The spec must also map how newly appearing countries can get more units after spawning. This should include decisions, timed objectives, focus rewards, volunteer systems, depot captures, foreign missions, local mobilization, League or faction training, factory guard mobilization, border guard formation, or special extreme-route recruitment where appropriate.

Do not make reinforcement depend only on political power or command power. Use concrete goals and resources such as holding a capital, guarding a border, controlling a depot, controlling rail lines, spending army XP, consuming equipment, committing manpower, using fuel or trains, securing local support, opening a foreign corridor, finishing a construction quota, proving legitimacy by a deadline, placing divisions in required states, or keeping a volunteer route open.

Unit-creating focuses and decisions must be specific. Avoid repeated generic rewards such as `add two infantry divisions` across many countries. A unit reward should explain the institution and story behind the unit, such as capital defense committees, local garrison defections, railway guards, factory guard shifts, mountain pass detachments, Black Banner columns, sailor battalions, Basmachi cavalry, ancient host militias, medical volunteers, foreign-trained cadres, or extreme-route special units.

Each unit-creating focus or decision should define:

- what unit or template family appears
- what unlocks it
- what non-political-power requirements it uses when appropriate
- whether it is repeatable, timed, risky, route-locked, or one-time
- what pressure or threat values it changes
- what downside it creates if repeated or failed
- what AI should do with it
- what blocked localisation direction should communicate when requirements are missing
- what icon, spirit, report event, or commander asset it needs when relevant

For focus trees, military growth should be integrated into branches. Some focuses can spawn units directly, but others should unlock decisions, improve templates, recruit commanders, create volunteer corridors, integrate militias, convert irregulars into regulars, expand special units, or change mobilisation rules. A deep tree should offer different ways to build an army depending on politics, foreign influence, economy, terrain, ideology, and escalation state.

### Distinct army identity and new unit-type gate

When a feature introduces a new type of country with its own army, explicitly assess whether that army needs new unit types instead of only renamed vanilla division templates. Plan at least one distinct unit family when the country's biology, doctrine, recruitment source, battlefield role, equipment relationship, movement, supply behavior, or visual silhouette differs materially from an ordinary national army.

A renamed template made entirely from ordinary vanilla battalions does not count as a new unit type. If vanilla battalions are sufficient, the spec must explain why their mechanics fit and must still define distinct templates, recruitment rules, caps, costs, AI use, progression, and visible identity.

For every planned new unit family, define:

- gameplay role, strengths, weaknesses, intended counterplay, and division-template consumers
- custom sub-unit, support unit, unit category, equipment, modifier, technology, doctrine, and script-enum needs
- manpower, equipment, supply, fuel, training, reinforcement, availability, cap, upgrade, conversion, and cleanup rules
- AI template priorities, role ratios, production needs, recruitment limits, and operational use
- localisation, bespoke vanilla-green large/map-counter art, exact counter tokens, and runtime-consumer requirements
- 3D entity, model, material, idle, movement, attack, death, and validation requirements when the unit should look different on the map

Every custom unit family also needs a sourced voice and sound-design pass. Selection audio is mandatory: define the source, stable identifier, exact engine consumer, binding scope, effective country/original tag, and every consumer under that identity before planning other roles. Recheck the installed infantry voice templates and bindings for the current game version; do not infer selection from idle or entity creation. Define the applicable acknowledgement, movement, idle, attack, retreat, impact, damage, destruction, and death roles; variation needs; runtime identifiers and consumers; looping, distance, volume, mix, and animation synchronization; and the exact vanilla or Internet-sourced files that may satisfy them. Recording, generation, synthesis, and manual authoring are forbidden. Every external file needs provenance, licensing, attribution, intended-use evidence, and an immutable original. If a suitable source cannot be found, the role remains blocked.

Every custom unit family also needs bespoke counter art for every large or map-counter surface it uses. The plan must name the exact installed-vanilla counter definition and DDS to inspect, the matching skill-local counter family, required tokens, frames, states, sizes, final paths, and `hoi4_icon_artist` handoff. Require the vanilla green counter palette sampled from the inspected reference. If the reference cannot be inspected, counter production is blocked; a reused vanilla counter or generic placeholder is not final.

Treat the unit package as part of the country package. A new military country archetype represented only by renamed vanilla formations is a planning failure unless the spec provides a concrete mechanical, visual, and audio justification.

## 3.13.1 3D model and skeletal animation planning standard

When a feature adds a visible unit, building, creature, vehicle, aircraft, naval object, map entity, or other 3D surface, plan the model package as a first-class feature surface rather than treating it as an optional render. A custom unit package also requires a sourced sound-design handoff and bespoke vanilla-green counter package.

Classify the asset before writing the brief: static prop, building, humanoid unit, non-humanoid creature, vehicle, aircraft, naval object, or articulated attachment.

For a unit, define the gameplay consumer, unit category or sub-unit, entity key, `.asset` key, `.mesh` key, material and texture paths, large/map-counter consumers and tokens, idle action, movement action, attack action, death or destruction action when relevant, and the exact country, province, state, or map test that will show it.

For a building or map entity, define the building key, entity key, mesh key, state and province placement, valid state-to-province relationship, level or construction behavior, zoom visibility, rotation, runtime scale, and a test location that is inside the intended state and does not hide the model behind an existing building.

If the parent does not provide a ready reference image, plan exactly one clean Meshy-ready reference image for the asset and route it through the approved image-generation workflow before the provider gate.

Never plan a side-profile sheet, turnaround board, collage, or multi-view board as a Meshy input. Blender QA views and contact sheets are review evidence only and must never be sent to Meshy.

The brief must name the installed vanilla mesh and entity that establish axes, orientation, source geometry height, entity scale, origin, ground or water contact, and effective runtime height.

For humanoid units, the custom source geometry must match the named vanilla source mesh height and the entity scale must be applied exactly once. Record source height, entity scale, effective runtime height, coordinate axes, facing direction, origin, and the measurement evidence in the plan.

For every requested skeletal action, define the semantic role, action name, FPS, frame range, loop policy, root-motion or in-place policy, ground-contact requirement, production/recovery route, runtime binding, and acceptance evidence. Firearm-bearing units plan a weapon-free Meshy 7 body plus separate Meshy 7 geometry tasks/approved firearm-only inputs for each gun, independent task/credit/download lineage, and one supported Meshy body rig/action attempt for eligible bipeds, then Blender fitting, attachment, contact correction, and missing rig, weight, action, or component work. Existing non-firearm repairs plan direct Blender work. Other provider-eligible bipeds plan one supported Meshy rig attempt and one action attempt per missing role; non-bipedal anatomy goes directly to Blender authoring. Unusable provider stages switch to Blender recovery without paid rig/action retries. Require meaningful multi-phase articulated motion, deformation/contact checks, export, and reimport proof; static, transform-only, whole-rig-only, or semantically aliased clips cannot pass. For every custom-unit sound role, define the Internet source-search requirement, selection or movement or engine or idle or attack or impact or special-action or death role when applicable, and the animation action and frame or runtime lifecycle synchronization point.

For every custom-unit counter, define the installed-vanilla definition and DDS reference, matching skill-local contact sheet, native canvas, per-frame size, frame order, alpha/background behavior, exact green palette, silhouette and contrast target, emitted token, required variants, final DDS path, and parent-owned GFX wiring.

Do not let a static render or still mesh stand in for a requested skeletal animation. If an action cannot be produced, the implementation handoff must mark it blocked or needs_user_review with the reason.

The model package must plan provider lineage, Blender source and normalized/repaired/material/rigged/action/pre-export checkpoints, processed textures, PDX material channel mapping, `.mesh` and `.anim` exports, reimport proof, runtime hashes, and final live-consumer screenshots. The sound package must preserve original downloads, original URLs, license and usage terms, access dates, source and derived checksums, and mechanically transformed files only when the license permits. No generated, synthesized, recorded, manually authored, placeholder, test-tone, or unlicensed audio is allowed, and a missing defensible source is a blocker.

The asset plan must distinguish provider source files from final runtime copies. It must require a final hash-aware synchronization step so an older mapped texture, mesh, entity, or animation cannot overwrite the approved runtime candidate.

Route production to `hoi4_3d_model_pipeline` without inherited conversation context and give it the exact job root, reference status or authorized modern-artwork search scope, asset profile, vanilla references, scale relationship, component/action list, selected firearm/non-firearm/repair route, custom-unit sound roles, custom-unit counter consumers/tokens and inspected vanilla paths, dependency lock, baseline planned paid operations, geometry-recovery credit limits, and handoff path. Require the designed-source/rights gate, immutable source and search records, exclusion of historical/documentary source families from the model-reference pool, a substantially original source-informed generated refinement with a source-to-refinement comparison, explicit approval before any source-free fallback, native alpha where needed, and Meshy 7 (`meshy-7`) as the generation model. Normal planned provider calls and bounded geometry recovery are pre-authorized while live balance and capability permit them; rig/action calls are limited to one supported attempt before Blender recovery. The parent owns final sound definitions, runtime wiring, and live validation.

The main implementation agent owns `.asset`, entity, `.gfx`, unit/building/gameplay wiring, valid province and state placement, live runtime validation, and in-game evidence.

### 3D model planning matrix

| Surface | Minimum planned evidence |
| --- | --- |
| Humanoid unit | Vanilla source-height measurement, entity-scale crosswalk, repaired geometry, PDX material audit, idle/move/attack actions, `.mesh`/`.anim` reimport proof, unit consumer, movement test, and screenshot |
| Building or static map entity | Vanilla building precedent, valid state/province pair, entity and `.asset` existence, mesh/material proof, scale and zoom test, construction or level test, and screenshot |
| Creature, vehicle, aircraft, or naval object | Profile-specific axis and contact calibration, topology/material proof, required action list, export/reimport proof, entity/runtime wiring, and domain-appropriate live test |
