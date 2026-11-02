# Generated source art and review

Generated art comes from `hoi4-imagegen`. Use only its tools, families, models and providers, and never invent a tool, model, size, reference argument, or backend. The family fixes the canvas and background: the tool plans for it, records the dimensions the provider returned, and fits the candidate to the runtime canvas in `hoi4.image_process`. Ask for one image per call.

<!-- HOI4_MOD_SETUP:IMAGE_GENERATION_PROVIDER:START -->
Default route: `hoi4-imagegen` (MCP server `hoi4_imagegen`). The loop for one asset, in the order the tool enforces it:

1. `hoi4.image_status` (provider, key or login, model) and `hoi4.image_families { family }` (the measured canvas, the mod's override, the style sources it will use and why).
2. Add references with `hoi4.image_references` (role `style_anchor`, `subject_anchor` or `geometry_anchor`, and a rights note). Style references come from the mod first (its copy of this skill's `assets/` folder and its existing assets of the family) and from the vanilla shelf second; vanilla references may always be sent to a provider when they help.
3. The group tool of the family's group with a required `family`: `hoi4.image_icon`, `hoi4.image_picture`, `hoi4.image_portrait`, `hoi4.image_flag`, `hoi4.image_unit` or `hoi4.image_interface`. Without `approve` it is the free plan with the cost estimate; with `approve: true` and an `idempotency_key` it generates one asset.
4. `hoi4.image_process`, `hoi4.image_validate` (the family's full check set), `hoi4.image_preview`, `hoi4.image_review` and `hoi4.image_install`. `hoi4.image_edit` refines a rejected candidate and `hoi4.image_ledger` shows what belongs together. `hoi4.image_audit` finds cross-family reuse in the whole mod.

Providers: the ChatGPT login (`hoi4-imagegen login`; gpt-6-luna at high effort, and the backend's image tool chooses the quality) or a key in the environment (`OPENAI_API_KEY`, `GEMINI_API_KEY`, `FAL_KEY`) or a ComfyUI endpoint. The `hoi4-imagegen` skill has the refusals and the facts to keep straight. If no provider is configured, stop and report the blocker.
<!-- HOI4_MOD_SETUP:IMAGE_GENERATION_PROVIDER:END -->

Before generation, identify the asset type, exact consumer, subject, intended footprint, composition, palette, reserved space, and prohibited additions. Label every supplied reference by filename and role: edit target, permitted subject anchor, style anchor, geometry/composition anchor, or explicit insertion layer. State which properties may transfer. A style reference does not authorize copying its identity, lettering, frame, or unrelated canvas. Portrait sourcing rules and exact map geometry remain authoritative.

Inspect local images before editing. Supply references through the actual tool schema, with the smallest input set that contains every required target. Do not rely on an unseen filename or ambiguous “previous image” to convey a reference.

When a candidate is close, correct one coherent defect on the current accepted candidate, inspect the result, and continue from the accepted output. Preserve accepted candidates and record rejected branches. A substantially wrong composition or requested alternative can justify a new generation. Restate invariants in every edit: subject, pose, proportions, palette, consumer footprint, reserved space, background/alpha, and unchanged regions. Keep functional UI controls and changing labels native.

For alpha-backed families, `hoi4.image_process` accepts only real transparency proven from the pixels, and every edit and processing step must preserve it. Check zero-alpha unused corners and padding, complete subject edges, and absence of fake checkerboard, matte, halo, key colour, or unintended holes. Opaque scene art, portraits, flags, and painted panels retain their required backgrounds. If the provider returns an opaque picture, regenerate with a model that has native alpha, or use a matte workflow only when the background is one flat colour, then check the edges; otherwise report the blocker.

If transparent output fails, use a focused `hoi4.image_edit` or a matte workflow, never an unconfigured service or local process. Keep the accepted subject, preserve the untouched input, record the processing route, and inspect clipped edges, colour spill, internal holes, and changed bounds before promotion.

Review the full-resolution candidate and the exact native-size processed preview against the brief and matching vanilla family. Check silhouette, framing, palette, edges, transparency, reserved space, and forbidden additions. For animation, also inspect frame order, anchor drift, changing footprint, timing, and loop seam under `hoi4-frame-animation`. A successful generation, file timestamp, spec-folder location, or old status label is not approval. Record explicit user direction or parent acceptance within existing authorization, the selected candidate, and unresolved defects before DDS promotion.

Keep source paths, prompts, accepted-candidate lineage, processing recipe, review findings, and runtime crosswalk together. Ordinary local revisions do not need repeated hand-copied hashes in every note. Preserve machine-generated provenance hashes, source/crop pixel-equality evidence, security and download checksums, provider lineage, uncertain-mutation guards, and deployed-runtime integrity checks wherever their owning contract requires them.
