# Asset source rules

This reference belongs to the `hoi4-feature-assets` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## 3. Asset source rules

Choose the source mode based on asset type.

### Scene-first and mood-first selection rule

Do not default feature art to maps, cartographic overlays, arrows, staff tables, conference rooms, or generic war-room compositions unless that is the strongest visual for the specific asset.

For a feature, many visuals should focus on the actor, force, symbol, ritual, creature, crowd, machine, government, army, leader, or strange condition behind the event. The image should usually make the event feel active and dangerous, not merely show that territory changed.

Prefer visuals that show:

- a country, movement, army, cult, council, machine, plague, or supernatural force as the subject
- people, banners, ruins, storms, fires, shadows, masks, relics, halls, crowds, weapons, monuments, or rituals
- obsession, wrath, zeal, panic, corruption, transformation, prophecy, dread, awe, or other feature-specific mood
- fantasy, surreal, mythic, occult, symbolic, or unexplained elements when the event concept supports them
- a clear subject and strong atmosphere over neutral geography

Avoid making the main visual read like:

- a map has changed
- borders have shifted
- officers are discussing an expansion route
- the art is mainly a strategic diagram with decoration
- the scene is a generic command table without a strong feature identity

Maps may still appear as secondary props when useful, but they should rarely be the main visual idea for fictional, alternate-history, extreme-route, supernatural, symbolic, or strange event assets.

### Use the image generator for generated symbolic or fictional assets

The image generator is the image-generation route selected for this project. HOI4 Mod Setup fills in the provider-specific details below from the manifest table. If no route is configured, stop and report the blocker instead of building a substitute pipeline.

<!-- HOI4_MOD_SETUP:IMAGE_GENERATION_PROVIDER:START -->
[The selected image-generation provider details are added by HOI4 Mod Setup.]
<!-- HOI4_MOD_SETUP:IMAGE_GENERATION_PROVIDER:END -->

Use the image generator by default for:

- idea icons
- focus icons
- decision icons
- decision category icons
- achievement icons
- fictional flags
- faction emblems
- fictional feature illustrations (final character portraits use `hoi4_portrait_creator`)
- UI panels
- progression-state base art
- other symbolic or fictional static assets

When creating generated assets, follow the selected image-generation route. Do not define a separate image-generation route in this skill.

Read [generation-and-review.md](generation-and-review.md) before generated source production or editing. It defines reference roles, focused revision, provider-supported transparency and editing, and acceptance checks.

For transparent icons, follow the selected provider section: ask for native transparent output when it is supported, or use its listed background-removal fallback and check the saved alpha. The final PNG must have real transparency, no fake checkerboard, no white halo, no white outline, and no opaque square background unless the asset type explicitly uses a painted backdrop.

If the selected image-generation route is unavailable, report that clearly and stop before using an unconfigured service.

For generated animated assets, use the image generator through `hoi4-frame-animation`. Each animation frame must be generated or edited as its own source frame according to a frame plan. Do not use local filters, transforms, glow pulses, or offsets as the source of final motion.

### Choose source mode for event photo assets

Report images, news images, and custom feature images may be either internet-sourced or generated.

Use internet-sourced imagery when the asset must show a real photographed person, specific real battle, real place, real object, real newspaper, real poster, real map, real archive item, or other verifiable historical material.

Use the image generator when the event is fictional, alternate-history, symbolic, supernatural, extreme-route, or when a unique scene is more important than matching an existing archive image. Generated event-photo assets should be prompted as period-authentic documentary material, not modern cinematic concept art.

For generated Second World War-era report, news, or custom feature images:

- prompt for 1936-1945 photographic technology, period composition, period clothing, period vehicles, period architecture, and documentary realism
- avoid modern streets, uniforms, props, weapons, vehicles, signage, UI overlays, cinematic color grading, and readable generated text
- keep the source PNG, processed preview, final DDS, prompt, and manifest entry
- record the source mode as generated and explain why generation fit better than sourcing
- never use generated images for real leader portraits or to fabricate a real person's likeness

Follow the repository web research rules from `AGENTS.md` when searching for source images.

For internet-sourced event photo assets that are meant to represent the Second World War era, search for period-matching source imagery from roughly 1936 to 1945 unless the feature spec gives a narrower date range. Prefer contemporary photographs, war correspondents' photographs, press agency images, propaganda posters, maps, newspapers, official records, government or military archive images, museum scans, library scans, and period illustrations. Do not use modern photographs, reenactment images, film stills, AI-looking reconstructions, postwar uniforms, streets, weapons, vehicles, buildings, colorized tourist photos, reenactments, or modern props when they do not fit the era. If no suitable period source can be found, either generate a period-authentic fictional/documentary image when the asset does not require a real source, or mark the asset as blocked or `needs_user_review`.

Record the image source, source link, author or archive if available, license or public domain status if available, estimated date or date range, why the image fits the Second World War era, and any uncertainty in the manifest.

### Real leader portraits

Do not generate a leader portrait for a real person.

For real people, use an attributed internet or user-provided source, create the exact crop, archive it under `docs/assets/portraits/`, and wire the source placeholder. Prefer public-domain, archival, official, or clearly licensed images that fit the period.

Real leader portraits preserve the immutable source and exact crop researched by `hoi4_portrait_creator`. The user creates the HOI4-style final through the configured provider route; the portrait worker validates and installs it.

Record the source link, author or archive if available, license or public domain status if available, source image path, processed PNG path, final DDS path when applicable, and sprite name.

For generated or sourced one-person leader portraits, the asset handoff must identify the portrait's gender presentation and any matching leader-name pool requirement. Female-presenting portraits must not be paired with male names and should require `female = yes` where a country leader is created directly. Male-presenting portraits must not be paired with female names or `female = yes`. Council, board, office, crowd, and symbolic-institution portraits should keep institutional leader names instead of personal random-name pools.


### Fictional leader portraits

Fictional or impossible portraits use the image generator through `hoi4_portrait_creator`, which owns generation, review, processing, DDS conversion, wiring, and handoff.

Portrait-worker output should follow HOI4 leader portrait conventions: 156x210 final DDS unless an existing sprite uses another size, bust or upper-torso framing, strong face or governing-body focal point, subdued painterly finish, period-appropriate uniform or civilian clothing, transparent or HOI4-compatible portrait background as required by the existing asset pattern, and no text, labels, watermarks, modern UI, or meme-like exaggeration.

For generated one-person leader portraits, record the portrait's apparent gender presentation in the manifest and handoff. Female-presenting portraits require female leader-name pools and female leader metadata where the implementation surface supports it. Male-presenting portraits require male leader-name pools and must not be paired with female metadata. Never hand off a portrait in a way that lets implementation randomly assign names from the opposite gender pool. Council, committee, junta, crowd, office, or symbolic-body portraits should be marked as institutional leaders and use institutional names instead of personal random-name pools.

For council or collective leaders, use one clear symbolic council portrait rather than a cluttered crowd. Keep the subject readable at leader portrait size and document that the leader is fictional or collective.

### User-provided assets

If the user provides an image, treat it as a source asset.

Record that the image was user-provided in the manifest.

Still crop, resize, convert, place, wire, and document it like any other source asset.
