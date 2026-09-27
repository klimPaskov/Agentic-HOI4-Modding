# Reusable workflow synchronization — 2026-09-28

## Scope and comparison source

The general starter baseline was `a957ba3b6b3e23b315630809d5e7e73e2155682a` on `main`. The read-only sibling-project comparison source was at `6162c7e99c6c2e25333f6293315fd2a1a9ccf516`; its working tree contained active skill and 3D-tool edits. This pass changed only the general starter.

The starter already contained the earlier September 26–27 workflow sync, current MCP 3.6.0 pin, source-coverage rules, engine-semantics guidance, decision-trigger performance notes, and the 16,384-pixel animation texture limit. This pass reconciled the remaining portable deltas rather than replacing its templates or specialized tools wholesale.

## Reusable changes applied

| Surface | Change |
| --- | --- |
| `hoi4-decisions-missions` | Fractional cost rows and tooltips must show enough precision to match the debit; display caches cannot govern fresh affordability or payment. The decision auditor now checks for rounded quotes and stale display caches. |
| `hoi4-events` | Event-option audits qualify reused option ids with the parent event, include the complete local candidate pool, inspect current route schemas and returned completeness fields, treat candidate overrides as assumptions, and report option shares as conditional on the event firing. |
| `hoi4-scripted-gui` | MCP renders are visual-review evidence and do not execute the game. The skill now requires exact fixture/source matching, records render timeouts and truncated outputs as open evidence, retrieves linked artifacts through supported bounded resource reads, and checks actual disabled-action appearance and source predicates. |
| `hoi4-subagents` and probability auditor | Probability scenario schemas are treated as version- and route-dependent; scenario dates, controller maps, and typed scope bindings are used only when the live schema accepts them. Candidate overrides and unresolved pool data are not presented as campaign facts. |
| Event UI and localisation auditors | Canonical Codex roles now use the same render-fidelity limits and disabled-action evidence rules. |
| 3D pipeline | The bootstrap keeps the upstream io_pdx_mesh 0.91 archive immutable and derives a deterministic Blender 5.2 compatibility archive in memory. It verifies the source, derived archive, and installed patch-file hashes before export. The app-owned Meshy 0.4.0 credential route remains intact. |

The 22 actual skill files under `.agents/skills/` were audited: `hoi4-3d-model-pipeline`, `hoi4-comfyui`, `hoi4-comfyui-cloud`, `hoi4-comfyui-local`, `hoi4-comfyui-runpod`, `hoi4-debug-playtest`, `hoi4-decisions-missions`, `hoi4-events`, `hoi4-feature-assets`, `hoi4-feature-planning`, `hoi4-focus-trees`, `hoi4-frame-animation`, `hoi4-improvement-loop`, `hoi4-mtth`, `hoi4-native-raids`, `hoi4-portrait-production`, `hoi4-save-inspection`, `hoi4-scripted-gui`, `hoi4-subagents`, `hoi4-super-events`, `hoi4-text-audio-research`, and `xlsx`. Existing generic guidance in the other skills was retained where it already matched or exceeded the comparison source.

The 23 canonical `.codex/agents/*.toml` definitions remain the authoring source. Four generated runtime sets were regenerated and checked: Qoder, Cursor, OpenCode, and Claude Code each contain 23 synchronized agents. The current runtime guide and synchronizer implementation were already aligned; no changes were needed there. `AGENTS_template.md` and `CLAUDE_template.md` already carried the current general engine, reference-coverage, approval, and completion rules.

## Deliberate exclusions and tool boundary

Project-specific registries and receipt rules were excluded. No feature allocator, country/event/asset content, local adapter configuration, absolute paths, provider jobs, or generated runtime state was copied. The experimental appendage-authoring helper was excluded because it is tied to a separate review CLI and conflicts with the starter's no-scripted-rig-authoring boundary.

The comparison checkout's newer Meshy wrapper was not imported. The general package continues to route credentials only through its verified app-owned launcher, pinned to the 0.4.0 contract. The optional Meshy Text-to-Motion route remains live-schema-gated; changing its host-owned launcher requires a compatible HOI4 Mod Setup release.

The compatibility builder was checked against the comparison checkout's current upstream io_pdx_mesh archive. Its edited builder produced a two-byte-different result from that checkout's prebuilt archive and lock, so the starter locks the deterministic output of its own builder instead: SHA-256 `A0ED30187494889B5415D579C823D888CFEAF197A3D4FC6A2D024E6BB0E10697`, 244,643 bytes. The derived archive and installed file hashes are recorded in `.tools/3d_pipeline/config/dependencies.lock.json`; the source release archive remains unchanged.

## Validation and remaining limits

- Repository manifest/setup tests pass: 37 tests under Python 3.13.5; the agent-sync contract passes for 23 canonical agents and four runtimes.
- The provider-free 3D pipeline suite passes: 262 tests under Python 3.13.5. All four runtime synchronizers report 23 generated agents current.
- In-memory regeneration from the comparison checkout's upstream archive matches the starter's locked compatibility archive and all three installed-file hashes under Python 3.13.5.
- No Blender process, paid Meshy request, or HOI4 game launch was run. The new bootstrap path has unit coverage; live Blender export remains a job-specific gate.
- GitHub Actions regenerates manifest evidence against the exact committed source revision after the content commit.
