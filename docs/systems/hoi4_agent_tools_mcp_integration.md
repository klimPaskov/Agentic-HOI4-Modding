# HOI4 Agent Tools MCP integration

This guide defines a mod-agnostic evidence and recovery contract for the installed HOI4 Agent Tools MCP package.

The mod source remains authoritative for implementation, while accepted specifications or plans express intent when a project uses them.

MCP output is supporting evidence and never replaces source review, the offline wiki, vanilla documentation, tests, owning skills, specialist audits, or parent review.

This document describes an integration contract rather than a live server run, so every user must confirm the installed package version and advertised routes before relying on a capability.

## Evidence contract

Use the narrowest selector supported by the matching route, such as one focus tree, event chain, technology or doctrine surface, weighted pool, scripted GUI, state, province, or map relation.

Capture a stable `hoi4-agent://` artifact URI for every material inspect, render, comparison, diagnostic, proposal, and recovery result.

Record the MCP revision returned with the artifact or source snapshot, and record it as unavailable when the route does not provide one rather than inventing a revision.

For weighted logic, record a named scenario identifier and deterministic scenario hash that cover the candidate pool, external factors, state, cadence, seeds, and terminal conditions used by the analysis.

Record the source-of-truth authority beside each evidence item, including the exact source files and accepted design document that define the intended behavior.

Keep pre-change and post-change evidence paired by selector, resolution, state, and scenario so a reviewer can reproduce the comparison without reconstructing the query.

Inspect, render, compare, and probability analysis are read-only evidence unless a rewrite route is explicitly used.

Renders are deterministic offline previews, not game screenshots, and they do not launch, control, automate, or capture the game.

## Capability matrix

Tool availability is version-dependent, so confirm each name from the installed server before invoking it.

| Surface | Read-only MCP evidence | Write route | Required evidence sequence | Limits |
| --- | --- | --- | --- | --- |
| National focus trees | `hoi4.focus_inspect`, `hoi4.focus_render` | `hoi4.focus_rewrite` when advertised | Inspect and render the exact tree before editing, review any proposal, then inspect and render again after source changes and retain paired evidence. | Layout and diagnostics are evidence, not a completion claim; complex focus weights also require the probability contract. |
| Event chains | `hoi4.event_inspect`, `hoi4.event_render`, `hoi4.event_compare` | None in the installed package | Run a narrow inspect and render before editing, then rerun them after editing and compare the same selector or revision when available. | Analysis is bounded and static, so dynamic destinations and runtime behavior can remain unresolved. |
| Technology and doctrine trees | No Technology Tree Viewer is available in the installed package described by this guide. | None in that package | Inspect source with normal repository tools and consult the offline wiki and vanilla documentation; use `hoi4.tech_inspect`, `hoi4.tech_render`, or `hoi4.tech_compare` only after the installed server explicitly advertises those routes. | Source inspection is not an invented viewer, and absent routes are blockers for MCP-backed technology evidence. |
| Weighted logic | `hoi4.probability_inspect`, `hoi4.probability_evaluate`, `hoi4.probability_sweep`, `hoi4.probability_compare`, `hoi4.probability_simulate`, `hoi4.probability_sequence`, `hoi4.probability_render` | None; the probability auditor remains read-only | Start with inspect, evaluate named scenarios, sweep sensitivities, compare the same scenarios before and after a source patch, and add simulation, sequence, or rendering only under the scenario contract. | A score is not a probability; incomplete pools or external factors make exact conclusions invalid. |
| Scripted GUI | `hoi4.gui_inspect`, `hoi4.gui_render` | `hoi4.gui_rewrite` when the GUI is explicitly in scope | Inspect the exact GUI before editing, render relevant states and resolutions, review the proposed rewrite, then inspect, render, and compare the same states and resolutions after editing. | Do not use a GUI route to redesign shared framework surfaces without an owning scope and parent approval. |
| Map and connected map data | `hoi4.map_inspect`, `hoi4.map_render` | `hoi4.map_rewrite` through Agent Nudger or an equivalent declarative writer | Inspect connected provinces, states, regions, adjacency, supply, and rail data before a proposal, complete dry-run and review before apply, then post-validate and retain recovery evidence. | A map render is offline evidence and does not prove in-game pathing, supply, or consumer behavior. |

If a route is absent, record the exact tool, selector, package version, and error, and mark the affected conclusion blocked or unresolved.

## Mandatory before-and-after workflow

1. Identify the surface owner, source files, accepted design authority, exact selector, and intended validation scenarios before calling MCP.
2. Run the matching narrow read-only inspect route and retain diagnostics, linked files, revision, and artifact URI.
3. Run the matching deterministic render route when the surface has a visual or layout representation, and retain the fidelity or limitation report.
4. For weighted logic, complete the probability scenario contract before evaluating any ranking, timing, or selection result.
5. Review source, offline wiki pages, vanilla documentation, tests, and the owning skill in parallel with MCP evidence.
6. Make the source change through the normal authorized workflow or through the bounded rewrite lifecycle below.
7. Rerun the same inspect and render queries after the change, then use the matching compare route where the package provides one.
8. Preserve pre-change and post-change URIs, revisions, scenario hashes, diagnostics, and unresolved limitations in the handoff or review record.
9. Do not claim a surface is complete when the required route was unavailable, the post-change evidence is missing, or a required scenario remains unresolved.

## Probability scenario contract

Use the probability routes only for a declared surface and scenario rather than treating a single weight dump as balance evidence.

1. Start every weighted audit with `hoi4.probability_inspect` for the relevant adapter or source.
2. Name every analyzed surface and scenario identifier, and preserve the resulting scenario hash.
3. Supply the complete candidate pool whenever the adapter normalizes weights or runs a selection race.
4. Declare prerequisites, availability and visibility gates, bypasses, target validity, external modifiers, state changes, cadence, cooldowns, removal or reset rules, terminal states, uncertain inputs, and seeds.
5. Use `hoi4.probability_evaluate` for named scenarios and exact or bounded traces.
6. Use `hoi4.probability_sweep` for thresholds, sensitivities, timing drift, starvation, dominance, and rank reversals.
7. Use `hoi4.probability_compare` for baseline versus candidate or before versus after results with the same scenario identifiers and hashes.
8. Use `hoi4.probability_simulate` only when explicitly declared uncertain inputs require sampling, and label the result sampled rather than exact.
9. Use `hoi4.probability_sequence` only when a complete custom pool, cadence, state transition, and terminal-state contract is declared.
10. Use `hoi4.probability_render` when a ranking, matrix, timing, sensitivity, sequence, comparison, or unresolved view improves review.
11. Classify every conclusion as exact, bounded, sampled, score-only, or unresolved.

Never state an exact selection probability when the candidate pool or external factors are incomplete, and never describe a score race as a click probability without normalization evidence.

Any patch to a weighted surface follows an audit-patch-compare cycle: establish the named baseline scenarios, let the owning implementation authority change source, and compare the same scenarios after the patch.

## Rewrite and recovery lifecycle

The lifecycle applies to focus, GUI, and map rewrites, including Agent Nudger or an equivalent declarative writer.

1. Scope and authority: confirm the exact files, identifiers, accepted design authority, and allowed write surface before proposing changes.
2. Inspect: obtain the narrow pre-change diagnostics, linked artifacts, source revision, and any required render or probability baseline.
3. Dry-run: validate the complete proposal without mutating source and retain the proposed diff or plan artifact.
4. Review: inspect diagnostics, changed identifiers, linked artifacts, source-of-truth authority, and expected post-validation before authorizing apply.
5. Apply: perform the authorized write through the configured transaction engine, never by bypassing the route with an untracked script or wrapper.
6. Post-validation: re-index or reload the affected surface, rerun inspect and render, compare against the baseline where supported, and record the resulting revision and artifacts.
7. Rollback or recovery: if the write or post-validation fails, retain the exact-byte recovery data and transaction or recovery reference, roll back to the prior source automatically when the engine supports it, and report the failure.

A blocked proposal must not mutate source.

The public MCP surface does not provide caller-managed transaction, apply, or rollback commands in the installed package, so intentional reversal of a successful edit is a new authorized source change, normally through version control.

Do not call a successful source reversal an MCP rollback unless the installed route explicitly exposes and records that operation.

## Route-unavailable behavior

Treat a missing adapter, tool, selector, comparison route, or package capability as a reproducible blocker rather than silently downgrading the evidence standard.

Record the exact route requested, selector, package version, command or transport, error text, and the source-only checks that remain possible.

Mark the affected surface blocked or unresolved, and carry the limitation into the parent review or handoff.

Source review, manual arithmetic, a screenshot, or a guessed wrapper does not substitute for a required MCP route.

The missing Technology Tree Viewer is a package limitation, not permission to label source or technology inspection as viewer evidence.

## Registration and troubleshooting

Install the published package with `npm install --global hoi4-agent-tools`, or use a deliberately pinned version that is compatible with the client and record that version in the evidence record.

For a local mod, register `hoi4-agent-tools.cmd` with the mod directory as its working directory; a mod-local working directory normally lets the server detect the source without a separate selection call.

Use `hoi4-agent-tools-setup --init` only when persistent multi-mod or remote configuration is required.

Use stdio for a local agent process.

For a separate HTTP process, run `hoi4-agent-tools-http --config PATH` with loopback binding, a long bearer token supplied through an environment variable, an exact origin allowlist, and explicit workspace grants.

Non-loopback deployment requires HTTPS, an authenticated identity layer such as OAuth or OIDC, isolation, and the restrictions documented by the package for that deployment mode.

When tools are missing, check `npm list --global hoi4-agent-tools --depth=0`, confirm the target project is trusted, verify the server command resolves, and restart the MCP client after installation or registration changes.

After an upgrade, rerun the package's documented inspector or integration checks and establish a fresh baseline before relying on old revisions or artifacts.

For HTTP failures, distinguish command resolution, transport, origin, authentication, workspace-grant, and route-capability errors, and preserve the exact response in the blocker record without weakening the evidence contract.

Keep bearer tokens and other credentials in environment variables rather than tracked configuration.

## Relationship to the rest of a modding workflow

The offline Paradox wiki and installed vanilla documentation define engine syntax and behavior; source files and accepted design documents define the mod's intended implementation; tests and specialist audits check correctness and balance; parent review owns final integration and completion claims.

MCP adds deterministic structural, visual, map, and probability evidence to that workflow, but it does not authorize an implementation, replace a source-of-truth file, or prove live consumer behavior.

Keep MCP guidance in the skill that owns the surface instead of creating a central router or wrapper that obscures ownership and route gaps.

## Evidence record template

Use a compact record like the following for each reviewable surface:

| Field | Value to record |
| --- | --- |
| Surface and selector | Exact domain, identifier, query, state, resolution, or map relation. |
| Source-of-truth authority | Exact source files and accepted specification or plan, if used. |
| MCP route and package | Tool name, adapter, transport, and installed package version. |
| Artifact URI | Stable `hoi4-agent://` URI for inspect, render, compare, proposal, or recovery evidence. |
| Revision | MCP source or artifact revision, or an explicit unavailable marker. |
| Scenario identifier and hash | Required for weighted logic; include declared seed and external-state inputs. |
| Transaction and recovery | Dry-run, review, apply, post-validation, transaction, and recovery references for rewrites. |
| Result classification | Exact, bounded, sampled, score-only, or unresolved. |
| Limitations and blocker | Missing route, dynamic behavior, incomplete pool, fidelity warning, or other unresolved issue. |

No live-server validation is implied by this documentation-only guide; confirm the installed route and retain fresh evidence when applying it to a mod.
