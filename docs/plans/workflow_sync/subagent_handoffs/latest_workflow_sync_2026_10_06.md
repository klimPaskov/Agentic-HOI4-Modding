# Reusable workflow synchronization — 2026-10-06

## Scope and comparison source

The general starter baseline was `f2d47cc2b90d8f882b8113b9d1dd1f2fc2f0129a` on `main`. The read-only sibling-project comparison source was at `4dfdc7c7f847176b11b9b72e701917f78896a38c`, compared against its last commit before the previous sync date, `8c3a4f847ba191ff01e3d36fbe0872bba6fd39c0`, across its project instructions, skills, Codex agents, Codex and MCP configuration, and 3D pipeline tools. Uncommitted work in the comparison checkout was not considered. The window between the previous sync's comparison revision `6162c7e99c6c2e25333f6293315fd2a1a9ccf516` and the base was also reviewed. This pass changed only the general starter.

## Reusable changes applied

| Surface | Change |
| --- | --- |
| `AGENTS_template.md`, `CLAUDE_template.md` | `hoi4.source_lookup` gains the `path` plus `line` locate mode, near-miss `suggestions`, and the `matchLine` to `startLine` hand-off for `hoi4.reference_read`; the existing `view`/`keyPath`/`occurrence`, `nextChildOffset`, `includeReferences`, and `hoi4.script_validate` guidance was already present. The fixed skill list now names `hoi4-native-raids`, `hoi4-save-inspection`, `hoi4-state-ledgers`, and `hoi4-shared-git-commit`. Repo Skills routes `hoi4-state-ledgers`, and the Git section routes shared-checkout commits through `hoi4-shared-git-commit`. Both templates stay identical in rule content. |
| New `hoi4-shared-git-commit` | Isolated temporary-index commit from a shared working tree: owned paths and hunks only, recalculated hunk offsets, exact whitespace, compare-and-swap `update-ref`, real-index reconciliation for mixed files and new paths, and stale `index.lock` handling for cloud-synchronized checkouts. |
| New `hoi4-state-ledgers` | Exact state-to-state population transfer contract, helper output preinitialization, sparse aligned cohort registry, symmetric state and country reception ledgers, transaction-time mapmode projections, no-double-counting proof, and validation scenarios. Project-specific loss helpers and death logs were generalized to "the shared population-loss helper" and "the project's casualty or death-log surface". |
| `hoi4-events` | Numeric `defined_text` output through real localisation keys; plain text without colour codes on light parchment report and news descriptions; PowerShell stdin non-ASCII and `\n` escape preservation; native special-project override rules; event-created country package audit, static named character recruitment and `set_nationality` transfer, and minimum flag coverage for every registered tag; STATE pointer validation; new `Helper output lifetime` section; deterministic max-score selector rule; script constant schema and variable arithmetic evidence; retiring unused helpers; final report-colour audit step; routing to `hoi4-state-ledgers`. |
| `hoi4-events/references/country-activation.md` | Native callback ROOT/FROM contracts (`on_annex`, `on_state_control_changed`), participant-iterator and targeted-decision capture, frozen transaction inputs, receipt nonces and owner/holder accounting partition, and state-owned cadence with deferred one-time verification. |
| `hoi4-decisions-missions` | Primary-action budget is a readability limit, not an engine row limit; native `custom_cost_text` base, `_blocked`, and `_tooltip` keys; display selectors share the authoritative affordability component; emergency variable-fee resolution and verified numeric reader tokens; generic refundable-purchase credit receipts; decision-level `modifier` requires `days_remove`; native mission timer synchronization through `add_days_mission_timeout`; production action contract tests. |
| `hoi4-feature-assets` | Full logical slot to alias to runtime path audit before wiring or count changes, and separate inventory, consumption, provenance, and acceptance measures. |
| `hoi4-portrait-production` | Parallel portrait receipts, parent-owned global counts, and explicit selected-source to runtime DDS mapping. The comparison source keeps this in an asset-skill reference; the starter's portrait contract lives in its own skill. |
| `hoi4-native-raids` | Actor-neutral physical `target_type` filters, state-`ROOT` observation, actor and victim policy in country preflight, and AI authorization before desirability boosts. |
| `hoi4-subagents` | Inline findings for runtimes that refuse subagent report files; byte-preserving committed probability snapshots; resolving each client's actual MCP transport and server before attributing capabilities, and unresolved native task outcomes. |
| `hoi4-3d-model-pipeline` references | Decoded `meshsettings` name and index binding check for every custom model consumer replaces the static-building-only object-name sentence; from the earlier window, tool-agnostic lessons on keying every animated bone, wheel spin keys, pipeline frame rate, empty-handed provider aim correction, short render paths, and entity `clone` variants verified against vanilla `gfx/entities/units_artillery.asset`. |
| Codex agents | `hoi4_documentation_curator`, `hoi4_feature_completion_auditor`, `hoi4_improvement_loop_planner`, `hoi4_localisation_auditor`, `hoi4_scripted_system_architect`, and `hoi4_skill_maintainer` move from `gpt-6-sol` to `gpt-6.1-sol`. The four generated runtime sets needed no regeneration because they do not project the Codex model field. |

## Manifest

`core.skills` already includes `hoi4-*/**`, so the two new skills enter that component without a declaration change. File evidence was regenerated with `scripts/generate_manifest_evidence.py` against the exact content commit, as the publish workflow does.

## Deliberate exclusions

- The comparison source's world-threat registry, sale-price receipt helpers, report-colour audit script, and other named helper files are project-specific; their reusable patterns were generalized instead of copied.
- The comparison source's `run_meshy_mcp.ps1` wrapper CPU fix was not imported. The starter has no such wrapper and routes Meshy through its app-owned launcher pinned to the 0.4.0 contract.
- The earlier-window review-lab command details (`lab_limbs`, `lab_items`, `texture_variant.py`, and their parameters) remain excluded with the review CLI, as in the previous sync. Only tool-agnostic lessons were carried.
- `.codex/config.toml` MCP server settings and `.tools/mcp/*` were left untouched because MCP pinning is owned by a separate change.
- The comparison checkout's `CLAUDE.md` is an untracked stale copy of its `AGENTS.md` and added no rules beyond the source-lookup lines already handled. Completion proof, MCP-mandatory surfaces, and script constant rules already match the starter templates; the parchment colour rule lives in `hoi4-events`, and no separate event spam limit exists in the comparison source.

## Validation and remaining limits

- Repository manifest and setup tests pass: 42 tests under Python 3.13; the agent-sync contract passes for 23 canonical agents and four runtimes, and all four synchronizer checks report current projections.
- `scripts/validate_published_manifests.py` passes against the regenerated manifest.
- No game, Blender, Meshy, or MCP server process was launched.
