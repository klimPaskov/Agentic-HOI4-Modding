# HOI4 Subagents: Asset and research routing

Part of the [hoi4-subagents](../SKILL.md) skill. Read before spawning an asset, portrait, icon, quote or audio specialist, writing its prompt, or cleaning up the `docs/assets/` workspace. It holds the "Asset-production agents" subsection, "Asset routing" and "Quote, remark, and audio research routing".

### Asset-production agents

Asset subagents create source files, processed previews, final DDS outputs, contact sheets, manifests, and asset handoffs under the temporary `docs/assets/<feature_slug>/` workspace during active work. They do not wire gameplay, localisation, GFX, GUI, events, focuses, decisions, or workbooks unless the parent gives a narrow exception.

The parent owns temporary-workspace cleanup. Keep the workspace while the feature is active, blocked, awaiting review, or undergoing acceptance scenarios. Before declaring the feature fully complete, promote durable provenance, licensing, attribution, coverage, review, and sprite-handoff facts into permanent feature or plan documentation, verify that no runtime reference points into `docs/assets/`, then delete the complete workspace. An absent workspace is expected after full completion. Never delete a skill-local reference library or an unrelated feature workspace.

## Asset routing

Do not use one broad asset worker for mixed visual packages.

Use:

- `hoi4_asset_source_researcher` for real, archival, historical, documentary, or public-source images when the asset must show real historical material
- `hoi4_portrait_creator` for complete grounded and fictional character portrait production
- `hoi4_generated_feature_art` for generated non-icon fictional, alternate-history, symbolic, extreme-route, or unique event art that is not a final character portrait
- `hoi4_icon_artist` for generated gameplay icon families, formable seals, decision category icons, and small animated icon or button sprites; follow `hoi4-feature-assets` for exact asset-family routing

The parent agent must give each asset subagent a bounded prompt with exact asset names, target sizes, source mode, final folders, sprite names when already registered, reference folders, and constraints.

For flags, the parent prompt must state whether each flag is a base flag, ideology variant, route variant, cosmetic-tag flag, historical flag, or fictional flag. Base flags for existing countries must be preserved unless explicitly in scope. Ideology variants must be distinct designs, not recolors or copied emblems. Historical flags and attested symbols belong with `hoi4_asset_source_researcher`. Fictional or alternate-history variants belong with `hoi4_generated_feature_art`.

Asset subagents may create source files, PNG previews, DDS files, contact sheets, manifests, and `gfx_handoff.md`. The portrait worker additionally owns portrait research or image generation, portrait-specific `.gfx`, and existing character portrait references. It must not edit unrelated localisation, GUI, event, focus, idea, decision, script, history, country, or workbook files unless the parent explicitly expands scope.

## Quote, remark, and audio research routing

Use separate research agents when the text and audio package has enough work to justify it.

Use `hoi4_quote_remark_researcher` for quotes, exact wording, attribution confidence, button text, cultural remarks, slogans, allusions, and short references.

Use `hoi4_audio_researcher` for audio research, license verification, download, `.ogg` conversion, and audio handoff notes.

Use `hoi4_portrait_creator` for every character portrait. Use `hoi4_asset_source_researcher` or `hoi4_generated_feature_art` only for non-portrait image work according to the source mode required by `hoi4-feature-assets`.

The main agent owns final wording, localisation, non-portrait GUI/GFX, audio wiring, playback helpers, caller effects, docs alignment, and live validation. The portrait worker owns portrait-specific `.gfx` and existing character portrait references.

