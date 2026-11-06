# HOI4 Feature Assets: Coverage audit and completion checklist

Part of the [hoi4-feature-assets](../SKILL.md) skill. Read before reporting any asset package or goal complete.

## 8.1 Requirement-to-runtime coverage audit

Before any asset completion claim, create or refresh a row-level coverage crosswalk from every accepted asset requirement in the current specs, manifest plans, and animation plans. Do not start from the assets that happen to be live. Each accepted row must identify:

- its requirement id and accepted design source
- its intended in-game purpose
- the exact source package and manifest entry
- the exact runtime registration: final asset path plus the `.gfx` sprite or texture, engine lookup id, or other owning definition as applicable
- the live consumer file and id
- the state or visibility binding when the asset is conditional or state-driven
- the current audit record path, evidence, and row status

Before changing asset or portrait wiring or completion counts, audit the full current required logical slot -> registered alias -> actual runtime path matrix, including conditional or regional variants and aliases sharing a path. Preserve the audited requirement, registry, and consumer source revisions or hashes, runtime file hashes, and declared coverage bounds in the audit record before making the change. A partial receipt or historical count must never stand in for the current consumer inventory.

Report file inventory, registered aliases and actual consumption, source provenance and archive packages, and accepted final coverage separately. Count unique consumed runtime paths, unique whole-file hashes, and unique decoded-pixel hashes as separate measures. File presence or alias consumption does not prove source provenance or final acceptance.

For every animation family, also record the purpose and the direction or state semantics that distinguish the family, together with its frame, timing, and loop evidence. Frame totals, live animation-family totals, and registered sprite totals are not coverage proof.

Audit exact rows, not counts. An extra asset or animation cannot satisfy an absent accepted row unless an explicit accepted design amendment identifies that row and names the replacement; link that amendment in the crosswalk. Any missing source package, runtime registration, live consumer, required state or visibility binding, or current audit record leaves the row incomplete.

After a late user correction or accepted spec, manifest-plan, or animation-plan change, rebuild the crosswalk against the current repository and attach a fresh coverage diff listing added, removed or replaced, changed, and still-uncovered rows. Do not reuse the prior audit or its totals for the completion claim.

## 29. Final checklist

Before finishing, confirm:

1. Every required asset from the feature spec is accounted for.
2. Every asset uses the correct source mode: `hoi4_portrait_creator` owns attributed sources and user-supplied styled replacements for grounded portraits and `hoi4-imagegen` for fictional or impossible portraits.
3. The matching reference folder from section 4 was inspected before generation, sourcing, processing, or wiring.
4. Every generated, sourced, or provided asset has a source PNG.
5. Every final asset has a processed PNG preview.
6. Every final asset has a DDS output.
7. DDS files use 32 bit unsigned BGRB 8.8.8.8.
8. DDS files are moved into the correct mod folders.
9. A `gfx_handoff.md` exists for every asset that needs a sprite definition, and the main agent has enough information to wire it.
10. The asset manifest exists.
11. Internet-sourced assets record source links, source date or estimated date range, license or public domain status if available, and era-fit notes for Second World War-era assets.
12. Fictional or non-human portraits produced through `hoi4-imagegen` are clearly marked as fictional or generated in the manifest.
13. Decision category pictures are classified separately from small category icons, scripted GUI backgrounds, and full mechanic-window assets; their canonical reference folder and labeled contact sheet were inspected.
14. Simple categories were not expanded into full scripted GUI asset packs when a static or animated category picture was sufficient.
15. Every formable state-puzzle asset uses exact installed-map state geometry, one shared projection, grey and green qualification states with non-colour cues, clean neighbouring edges, and a manifest aligned with the reusable template.
16. Docs are updated where relevant.
17. The feature implementation or parent handoff knows which sprite names to use.
18. No final asset remains only in a temporary folder.
19. Focus, idea, national spirit, officer corps spirit, decision, decision category, achievement, and tech icons were treated as separate asset types. No idea or decision icon is only a resized, cropped, recolored, padded, or lightly edited focus icon.
20. Every animated asset used `hoi4-frame-animation`, has real source frames, has a static fallback, and has no transform-only final motion.
21. Every unit visual is classified by domain and surface as equipment/technology art, a large land counter, a land/air/naval map counter, a division-template emblem, or a land/air/naval 3D model package; one pipeline was not resized or relabeled to substitute for another. A 3D package also proves the one-image Meshy input rule, provider lineage, vanilla scale calibration, PDX material mapping, topology repair, required skeletal actions, `.mesh`/`.anim` reimport, hash-aware runtime synchronization, parent-owned wiring, and a live consumer.
22. Every advisor, theorist, high-command, officer-corps, or army-small card uses the native `65x67` advisor workflow, the exact accepted template, retained transforms and hashes, and independent native/4x review; it is not a shrunken leader texture.
23. Every sourced portrait has a durable source under `docs/assets/portraits/<feature_slug>/`, a stable runtime basename, an explicit pending source-placeholder or validated final state, and no runtime reference into the archive.

<!-- HOI4_MOD_SETUP_SUPER_EVENTS_START -->
## Super Events images

When the installed `hoi4-super-events` workflow is selected, read its runtime templates and use the declared `457x328` presentation image size. Define the exact role, subject, tone, focal hierarchy, symbolism, source mode, safe text area, prohibited content, final DDS path, and sprite purpose before production. Use sourced archival material for real people, events, places, documents, or objects; use approved generation for fictional, alternate-history, symbolic, or supernatural scenes that do not claim to be historical photographs.

Keep source material, processed previews, provenance, licenses, uncertainty, final DDS output, and GFX handoff together. Review the image at runtime size in the complete popup, then let the main agent wire the sprite, localisation branches, caller, and registration. The examples bundled with `hoi4-super-events` are composition references only and must not be registered as project art.
<!-- HOI4_MOD_SETUP_SUPER_EVENTS_END -->
