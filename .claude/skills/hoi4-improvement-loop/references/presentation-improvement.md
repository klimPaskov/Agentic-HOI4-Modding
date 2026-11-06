# HOI4 Improvement Loop: Improving scripted GUI, assets, super-events and sourced text or audio

Part of the [hoi4-improvement-loop](../SKILL.md) skill. Read when the addendum touches a scripted GUI, animated presentation, asset or model, super-event, or sourced text or audio.

## Scripted GUI and animated presentation improvement

A scripted GUI is useful when the player needs to manage a living system visually. It is not useful when a normal decision category would be clearer.

Apply the decision skill's category-picture eligibility gate before proposing static or animated pictures. Basic value tables and ordinary decisions can remain simple, while meters, extra custom controls, rich panels, interactive state puzzles, and other animations exclude an additional picture. Choose animation for useful state feedback rather than as a depth requirement.

A GUI addendum should describe what the player sees, what values matter, what buttons can be clicked, what costs they use, what tooltips explain, what states or targets are locked, what warning states appear, what animation communicates, and how the UI closes or changes when the mechanic ends.

Follow [hoi4-scripted-gui](../../hoi4-scripted-gui/SKILL.md): choose or create a reference before implementation, map it to native controls and background regions, define coherent review scenarios and supported resolutions, and require live MCP previews throughout construction rather than only a final screenshot.

Good scripted GUI use cases include congress vote boards, patron influence networks, formable progress panels, crisis meters, corruption webs, occult pressure seals, expedition logistics boards, faction cohesion screens, target cards, and reform panels with competing factions.

Every GUI action needs script ownership. Buttons need costs, requirements, tooltips, scripted effects, scripted triggers, AI equivalents, cleanup, and validation. Animation should clarify state. A glow can show availability. A pulse can show danger. A float loop can show active power. Particles can show extreme-route corruption. Animation should not replace readable text.

Animated leader portraits should be reserved for major identity changes, extreme-route leaders, supernatural leaders, final formables, route reveals, and dramatic defeat aftermath. Define the trigger, static fallback, source mode, visual mood, frame behavior, sprite handoff, and removal or replacement condition.

## Asset and visual improvement

Visual improvement should support mechanic clarity. It should not become decoration detached from gameplay.

When an improvement changes a unit, building, creature, vehicle, aircraft, naval object, or map entity, include a 3D model review instead of treating the model as a final-render detail. Check whether the feature needs a static prop, a calibrated humanoid unit, a domain-specific mesh, or a building entity, then name the vanilla mesh/entity precedent, source-height/entity-scale crosswalk, one-image Meshy input rule, PDX material mapping, required skeletal actions, `.mesh`/`.anim` exports, reimport evidence, runtime hashes, valid map placement, and live consumer.

Route bounded production to `hoi4_3d_model_pipeline` without inherited conversation context. Require the designed-source/rights gate, a substantially original source-informed refinement with a source-to-refinement comparison, explicit approval before any source-free fallback, native alpha where needed, the profile's generation model (currently Meshy 7), the route chosen under the 3D production guide's Route selection, and a `credit_budget` the user approves once. Require substantive multi-phase motion, complete required components, Internet-sourced-only unit audio, and bespoke vanilla-green counters backed by exact installed-vanilla inspection. Keep provider source, Blender checkpoints, processed textures, counter and sound handoffs, and runtime evidence separate from the parent-owned `.asset`, entity, `.gfx`, gameplay wiring, and in-game proof.

An asset addendum can define route-specific report images, decision icons, idea icons, focus icon families, flags, portraits, faction emblems, scripted GUI panels, animated sprites, animated portrait variants, progression states, and contact sheets.

For animated assets, define the state. The asset worker needs to know what frame set means inactive, active, dangerous, locked, completed, corrupted, hidden, or formed. The main agent needs static fallbacks and sprite names. The docs need manifest data to prove the asset was sourced or generated correctly.

Use source-based assets for real people, real flags, real symbols, and real historical images. Use generated assets for fictional, symbolic, supernatural, or impossible content. If an asset cannot be sourced or generated safely, mark it blocked instead of substituting a weak image.

Use `docs/assets/<feature_slug>/` only as a temporary feature-scoped evidence and working folder for source files, previews, contact sheets, manifests, animation plans, and handoffs. Keep it while implementation or review is active, blocked, or incomplete. Before the feature is fully complete, promote durable provenance, coverage, review, and runtime-wiring facts into permanent feature or plan documentation, verify that no runtime reference points into `docs/assets/`, and delete the complete workspace. A closure handoff should treat the absent workspace as expected, not as a missing asset. Never delete skill-local reference assets or another feature's workspace.

## Super-event improvement

A super-event addendum should explain why the moment is larger than a normal popup. Define the campaign threshold first: first reveal, faction formation, global escalation, defeat aftermath, campaign-ending threshold, hidden route reveal, final formable reveal, or regional order change.

A good super-event addendum includes trigger meaning, title direction, description direction, button tone, quote direction, image direction, sourced-audio direction, documentation, and catalog alignment where the repository maintains one. It should not choose a dramatic quote, image, or sound without a campaign threshold that justifies it. Formables deserve super-events only when they materially alter a region, revive a major identity, complete a hidden route, or announce a new bloc.

## Text and audio research improvement

Sourced quote, remark, or audio research addendum should explain why the moment is larger than a normal popup. Define the role first. Examples include first reveal, faction formation, global escalation, defeat aftermath, campaign-ending threshold, hidden route reveal, final formable reveal, or regional order change.

A good quote, remark, or audio research addendum includes trigger meaning, title direction, description direction, button tone, quote direction, image direction, audio direction, docs, and alignment with any explicitly scoped external records. It should not choose a dramatic quote or image without a campaign threshold that justifies it.

Formables can deserve sourced text or audio packages when they alter a region, revive a major historical identity, complete a hidden route, or announce a new bloc. Most small formables do not need one.

