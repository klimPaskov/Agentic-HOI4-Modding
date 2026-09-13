# Latest reusable workflow documentation delta

## Scope and accepted decision

Feature slug: `workflow_sync`.
The parent authorized bounded documentation parity corrections against sibling `../chaos_redux`, using source HEAD `5c5d3b0020a06f7fd9ac4bef8a3f40e633a2e42f` plus its dirty working-tree documentation.
The starter intentionally has no root `AGENTS.md`; `AGENTS_template.md` is its adaptation authority, and `AGENTS_chaos_redux.md` remains an optional example.
Existing dirty September 8 sync work was preserved; this handoff does not identify the entire Git diff as this worker's edits.
All state ledgers and Chaos-only systems remain excluded from the sync.
No gameplay, assets, skills, agent TOMLs, manifest metadata, synchronizers, or 3D code were changed by this worker.

## Source-of-truth map

| Surface | Authority and evidence | Disposition |
| --- | --- | --- |
| Starter project instructions | `AGENTS_template.md`; parent-approved reusable corrections | Updated, not replaced wholesale from Chaos Redux. |
| Optional example | `AGENTS_chaos_redux.md` | Updated only for the bounded reusable rules; existing project-specific examples were not expanded. |
| Source approval discipline | `../chaos_redux/AGENTS.md`, Specs and Plans, source lines 145–149 | Reused: distinguish decisions, acceptance basis, implementation evidence, and proposals; document location or status does not prove approval. |
| Category-picture eligibility | `../chaos_redux/.agents/skills/chaos-redux-decisions-missions/SKILL.md`, source lines 678–680 and 834 | Reused as a concise instruction-level gate; the owning decision skill retains the complete workflow. |
| Runtime policy | Canonical `.codex/agents/*.toml`; target `git ls-files` reports 23 tracked agents in each of `.qoder/agents`, `.cursor/agents`, `.opencode/agent`, and `.claude/agents` | Preserve all four generated, tracked projections and single-source authoring. |
| MCP evidence contract | `docs/systems/hoi4_agent_tools_mcp_integration.md`; `AGENTS_template.md`; manifest-pinned bootstrap policy | Corrected read-only technology routes and aligned pinned installation guidance; this is documentation, not fresh service evidence. |
| Source runtime relocation | Dirty source `AGENTS.md` removes its runtime section; `../chaos_redux/.codex/README.md` retains a three-runtime description | Do not import the older runtime description or remove starter four-runtime guidance. |

## Files changed and exact corrections

- `AGENTS_template.md`: corrected the obsolete ignored/machine-local projection claim to generated-but-tracked; added explicit acceptance-basis discipline and one disposition per plan/addendum; added the simple-category picture eligibility gate; distinguished exposed tools, usable MCP routes, and standalone viewer availability.
- `AGENTS_chaos_redux.md`: added the same acceptance/disposition discipline and picture gate; explicitly named all three read-only technology routes and their blocker behavior; distinguished standalone viewer availability from tool exposure and service health.
- `README.md`: replaced the standalone-viewer-as-MCP-health-gate claim with the requirement for all three advertised and usable technology MCP routes; added the separate standalone viewer check; joined two accidental hard wraps in opening list items.
- `.tools/README.md`: corrected the projection tracking claim; added the source's reusable preservation rule for uncertain or recently active tooling whose owner or replacement is not yet clear.
- `docs/systems/hoi4_agent_tools_mcp_integration.md`: moved `hoi4.tech_render` and `hoi4.tech_compare` into the read-only column; explicitly made GUI rewrite optional while keeping inspect/render/comparison and visible-defect correction mandatory; aligned registration guidance with manifest-pinned `hoi4-agent-tools@2.5.2`, registry integrity, runtime-entry evidence, and exact-version blocker behavior; separated standalone viewer availability from service health and mandatory technology routes.
- `docs/plans/workflow_sync/subagent_handoffs/latest_docs_delta_2026_09_13.md`: created this handoff.

No security, dependency-integrity, immutable-provenance, provider-download, runtime synchronization, or probability-scenario hashes were removed.
The scenario-specific baseline and same-scenario `hoi4.probability_compare` handoff requirements remain intact.

## Contradictions and dispositions

| Item | Evidence | Disposition |
| --- | --- | --- |
| Generated tracking contradiction | Starter README and sync README said all four projections were tracked, while template and tools README said three were ignored/machine-local; path-specific Git counts prove all four tracked. | Resolved in template and tools README; README and sync README tracking claims left unchanged. |
| Technology write classification | MCP guide previously placed render/compare under Write route. | Resolved: all three technology routes are read-only. |
| Unpinned installation advice | MCP guide previously allowed generic global installation despite the pinned template, README, and manifest bootstrap. | Resolved in guide; root owns manifest evidence regeneration. |
| Viewer/tool conflation | Starter README treated Technology Tree Viewer availability as identical to the three technology MCP tools; current source AGENTS distinguishes those capabilities. | Resolved without importing the source-local absent-viewer claim or weakening mandatory actual routes. |
| Optional GUI rewrite ambiguity | MCP matrix implied a proposed rewrite was required; existing starter instructions and source contract permit direct authorized edits. | Resolved in matrix and recovery prose; internal server validation remains enabled and required visual evidence is preserved. |
| Skill organization, preservation, conflict handling, and repetitive hash bookkeeping | Separate non-3D skill delta audit and canonical agent review are parent-assigned ownership. | Left for the owning skill maintainer and parent; do not remove security/provenance hashes under a bookkeeping cleanup. |
| Model-policy contradictions | Source AGENTS names GPT-6-astra for manual Blender work; canonical model configuration and 3D behavior are parent-owned. | Left unchanged by this worker; parent must reconcile canonical policies without importing stale model guidance. |

No feature plan or handoff was promoted to accepted design by this worker.
No gameplay completion, balance result, asset completion, or live acceptance was inferred.

## Duplicate, superseded, and stale instructions

No documents were deleted, merged, superseded, or moved.
The source's runtime-block removal leaves its runtime explanation in `.codex/README.md` without an explicit caller reference in current source AGENTS.
If the parent later adopts relocation, add a concise caller link to an installed, runtime-neutral document and update manifest distribution paths in the same change; copying the source's older three-runtime README is not an appropriate replacement.
Existing `.tools/sync/README.md` remains the starter's detailed four-runtime synchronizer document.
No new central MCP router, skill, or wrapper was introduced.

## Markdown audit and validation

The two opening README list items split between “common” and “and specialized”, and between “adapt” and “these components”, were joined onto their original list-item lines.
Paragraph boundaries, headings, lists, tables, code blocks, and intentional sentence-per-line approval prose were preserved.
A bounded fence-aware adjacent-prose-line scan over the five edited documents found no remaining candidate mid-sentence hard wraps.
Targeted searches found no remaining obsolete machine-local/ignored projection claims, unpinned generic npm installation advice, or standalone-viewer-as-required-MCP-health-gate wording in the five edited documents.
Path-specific `git ls-files` established 23 tracked agents per generated runtime directory.
The pinned package was cross-checked against the existing manifest declaration without modifying manifest metadata.
`git diff --check` passed for the five edited documents; Git reported normal LF-to-CRLF working-copy warnings.

No game, launcher, MCP runtime, package installation, web research, binary asset inspection, or gameplay validation was run.
Fresh MCP scenarios, renders, tool health, and standalone viewer presence are unresolved runtime checks, not claims of this documentation pass.
Source-only documentation review is not substituted for mandatory MCP evidence on an implementation surface.

## Parent follow-up and remaining risks

- Regenerate manifest file sizes and hashes after all concurrent owner edits finish; existing metadata may describe the pre-edit starter bytes.
- Review and integrate the separate skill-maintainer handoff for skill organization, preservation/conflict rules, and redundant bookkeeping changes.
- Reconcile canonical model policies and 3D changes in the parent's owned paths.
- Preserve four-runtime support, tracked projection distribution, existing dirty changes, and the exclusion boundary.
- Do not treat source-local package health or absent capabilities as a reusable starter fact.

This handoff records documentation corrections only and does not claim overall workflow-sync or gameplay completion.
