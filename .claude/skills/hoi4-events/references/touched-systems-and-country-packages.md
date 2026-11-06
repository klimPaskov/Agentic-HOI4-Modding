# HOI4 Events: Touched systems and country packages

Part of the [hoi4-events](../SKILL.md) skill. Read before mapping which files and systems an event touches, and when an event creates a country, a special project override or a unit family.

### Shared unit-family provider integration

Apply this section only when the destination repository already has a shared, extensible unit-family registry or provider API.

When an event or owning system integrates with that API, declare whether the new land sub-unit or equipment-backed family is a standalone provider, a support attachment under an existing provider, or intentionally parent-owned because the engine cannot expose it independently.
A standalone family must use the repository's idempotent owner-registration contract and implement only the callbacks the verified shared consumer exposes, such as eligibility, template construction, sustainment, equipment-token publication, presentation, management, derivatives, removal, and cleanup.
A support attachment remains in the provider-owned transaction or template; a parent-owned disposition records the engine constraint and retains unlock, equipment, sustainment, presentation, and cleanup behavior in the parent package.

Audit every in-scope family and support definition against the repository's actual provider, token, presentation, localisation, and cleanup contracts.
Do not extend a central consumer-maintained switch when the verified owner-provider API can supply the same data; a missing provider row is an integration failure, not permission to add an undocumented fallback.


### 2. Map touched systems before editing

Start from the event file and walk outward.

Common files to inspect or update:

- `events/<event_file>.txt`
- `common/on_actions/*.txt`
- `common/scripted_effects/*.txt`
- `common/scripted_triggers/*.txt`
- `common/script_constants/*.txt`
- `common/scripted_localisation/*.txt`
- `common/decisions/*.txt` and `common/decisions/categories/*.txt`
- `common/national_focus/*.txt`
- `common/ideas/*.txt`
- `common/country_tags/*.txt`, `common/countries/*.txt`, `history/countries/*.txt`, and `history/states/*.txt` when countries are created or transformed
- `common/ai_strategy/*.txt` and other AI files when behavior changes
- `interface/*.gfx` when event pictures or sprites are referenced
- `localisation/<language>/*.yml`
- `gfx/event_pictures/`, `gfx/interface/`, `gfx/leaders/`, `gfx/flags/`, and other asset folders
- `docs/`, specs, plans, manifests, and any explicitly scoped external records when the repository uses them

Use exact ids, namespaces, flags, variables, localisation keys, sprite names, tags, and file stems to search. Avoid broad repo exploration when the files are already known.

### 3. Register optional mod hooks only when they exist

Many mods have their own event registries, debug menus, scenario tools, event lists, or documentation tables. Use those hooks only when the repository actually has them.

Generic rule:

1. Find the existing registration pattern.
2. Add the event id, display name, category, enabled state, or weight in the same shape as existing events.
3. Keep any scripted-localisation selectors aligned with the registration.
4. Keep optional docs or parent-provided tracking records aligned with the in-game text.
5. If the repository has no such system, do not invent one for a normal event.

### 4. Handle supporting gameplay systems

An event often needs more than its own event file.

Touch the relevant systems in the same implementation pass:

- decisions and categories if the event creates player tools or responses
- missions if the player must meet a deadline or map objective
- ideas or dynamic modifiers if the event creates persistent gameplay state
- focus trees if the event creates a route, unlock, or country tree
- country files and history files if the event creates or transforms a country
- AI strategies if the event changes how AI should react
- assets and `.gfx` if visible pictures, icons, flags, portraits, or sprites are used
- documentation when mechanics change

If new reusable dynamic scripted effects or triggers are added, document them in the matching markdown file or repository helper documentation in the same change.

#### Native special-project output overrides

Do not assume duplicate native project IDs safely replace or partially merge definitions across filenames.
For approved vanilla project output changes, use a complete replacement at the same relative vanilla file path unless the relevant engine merge behavior is proven.
Repeating full definitions in a distinct mod filename can duplicate enable-equipment or module list entries.

- Check installed native documentation, current vanilla source, and every existing mod owner of the file and project IDs before editing.
- Retain original tuning, availability, rewards, and file-scoped constants, including other projects in the replaced file, while adding only approved owned output hooks.
- Record vanilla source paths and SHA-256 hashes, then remove only the owned hooks from a comparison copy and verify exact remaining content against those sources.
- Check effective source-ID uniqueness after same-path masking, including other mod files that still declare the IDs.

Source equality establishes preservation only and must not be described as engine validation.

#### Event-created country packages

When auditing event-created country packages, verify the whole playable-country surface, not only the release effect: country files, custom-tag history, additive startup grants for existing countries, tag registration, base and ideology-specific cosmetic localisation with `_DEF` and `_ADJ` variants, flags, decision, focus, and idea icons, focus loading, AI strategy, docs, and manifests. For existing-country variants, set the event-created flag only on the release path and gate every `load_focus_tree` path by that flag. Do not copy vanilla country, state, or unit history only to add the mod's technologies, equipment, facilities, traits, or other additive setup; put that setup in a startup helper called from `on_startup`.

Static named characters that need persistent script tokens must be recruited in history. Do not use runtime `recruit_character` or attempt a character-scope transfer of an unrecruited identity. For dated identities, a bounded `history/general` recruitment pool on a dedicated dormant holder is valid; the holder must have no owned states or gameplay route and must not reuse an event-owned playable holder or a test harness. Check date eligibility and original ownership before transferring from the original owner's country scope with `set_nationality = { target_country = <destination> character = <static_token> }`, and preserve availability dates, roles, identity flags, and retirement gates. Use `generate_scientist_character` only when a generated unnamed identity without a persistent character token is intended; never silently replace approved static identities with generated substitutes. Validate native execution separately from source proof.

Every registered country tag, including stateless dormant or internal history holders, needs valid default and ideology flag lookup coverage in `gfx/flags/` (`82x52`), `gfx/flags/medium/` (`41x26`), and `gfx/flags/small/` (`10x7`), because native flag consumers remain active without territory or a playable route.
Use the `hoi4-feature-assets` flag workflow for this minimum native consumer package, limit asset authorization to that package, and document intentionally shared institutional designs across aliases in the manifest.
Validate actual 32-bit uncompressed bottom-left TGA headers and decoded orientation against installed and repository examples, correcting flag files directly without UI or dynamic-routing workarounds.

