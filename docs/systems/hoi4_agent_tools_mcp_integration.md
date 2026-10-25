# HOI4 Agent Tools MCP integration

This guide defines a mod-agnostic evidence and recovery contract for the installed HOI4 Agent Tools MCP package.

The mod source remains authoritative for implementation, while accepted specifications or plans express intent when a project uses them.

MCP output is supporting evidence and never replaces source review, the offline wiki, vanilla documentation, tests, owning skills, specialist audits, or parent review.

This document describes an integration contract rather than a live server run, so every user must confirm the installed package version and advertised routes before relying on a capability.

The supplied Codex registration allows 120 seconds for startup and 600 seconds per tool call; Claude Code uses its own MCP timeouts, which the `MCP_TIMEOUT` and `MCP_TOOL_TIMEOUT` environment variables can raise.
Keep source selectors and GUI scenario matrices bounded; complex source renders can take several minutes.
Use negotiated task support only after confirming it in the connected client and server.
Tool exposure does not prove service health or the availability of a standalone viewer application. Verify standalone Technology Tree Viewer availability separately when needed and record a missing viewer as a package gap.

## Evidence contract

Use the narrowest selector supported by the matching route, such as one focus tree, event chain, technology or doctrine surface, weighted pool, scripted GUI, state, province, or map relation.

Capture a stable `hoi4-agent://` artifact URI for every material inspect, render, comparison, diagnostic, proposal, and recovery result.
Use the actual MCP registration key when reading a resource, rather than assuming it matches the npm package name. The supplied configuration uses `hoi4_agent_tools`. Follow byte-range continuation metadata until the resource is complete.

Record the MCP revision returned with the artifact or source snapshot, and record it as unavailable when the route does not provide one rather than inventing a revision.

For weighted logic, record a named scenario identifier and deterministic scenario hash that cover the candidate pool, external factors, state, cadence, seeds, and terminal conditions used by the analysis.

Record the source-of-truth authority beside each evidence item, including the exact source files and accepted design document that define the intended behavior.

Keep pre-change and post-change evidence paired by selector, resolution, state, and scenario so a reviewer can reproduce the comparison without reconstructing the query.

Inspect, render, compare, and probability analysis are read-only evidence unless a rewrite route is explicitly used.

Renders are deterministic offline previews, not game screenshots, and they do not launch, control, automate, or capture the game.

## Capability matrix

This package pins HOI4 Agent Tools 4.0.3 and its 28-tool contract. The table lists those routes; use the names the connected server advertises in its live tool list, and read each live schema before relying on optional parameters.

| Surface | Read-only MCP evidence | Write route | Required evidence sequence | Limits |
| --- | --- | --- | --- | --- |
| Local references | `hoi4.reference_context`, `hoi4.reference_search`, `hoi4.reference_read`, `hoi4.source_lookup` | None | Select the work surface, search exact rules, read the pertinent cited sections, and inspect exact vanilla/mod definitions. | A citation bundle identifies sources; it does not prove that their detailed rules were read. Missing or skipped sources require a targeted local read or a recorded gap; resolve live `omittedSources` by increasing the result limit or targeted search/read. |
| National focus trees | `hoi4.focus_inspect`, `hoi4.focus_render` (PNG by default; `png: false` for vector only) | `hoi4.focus_rewrite` when advertised | Inspect and render the exact tree before editing, review any proposal, then inspect and render again after source changes and retain paired evidence. | Layout and diagnostics are evidence, not a completion claim; complex focus weights also require the probability contract. |
| Event chains | `hoi4.event_inspect`, `hoi4.event_render`, `hoi4.event_inspect` with `mode: "compare"` | None in the installed package | Run a narrow inspect and render before editing, then rerun them after editing and compare the same selector or revision when available. | Analysis is bounded and static, so dynamic destinations and runtime behavior can remain unresolved. |
| Technology and doctrine trees | `hoi4.tech_inspect`, `hoi4.tech_render`, `hoi4.tech_inspect` with `mode: "compare"` | None; these routes are read-only | Inspect the selected tree, render a reviewable layout, and compare related trees or variants. | Keep source review and MCP evidence together; never invent viewer evidence for a route that is not advertised. |
| Weighted logic | `hoi4.probability_inspect` (inventory and evaluation), `hoi4.probability_analyze` (`analysis`: `sweep`, `compare`, `simulate`, `sequence`, or `render`) | None; the probability auditor remains read-only | Start with inspect, evaluate named scenarios, sweep sensitivities, compare the same scenarios before and after a source patch, and add simulation, sequence, or rendering only under the scenario contract. | A score is not a probability; incomplete pools or external factors make exact conclusions invalid. |
| Scripted GUI | `hoi4.gui_inspect`, `hoi4.gui_render` | Optional `hoi4.gui_rewrite` when the GUI is explicitly in scope | Inspect the exact GUI before editing, render relevant states and resolutions, apply the reviewed edit directly or through the optional rewrite, then inspect, render, and compare the same states and resolutions after editing. | Do not use a GUI route to redesign shared framework surfaces without an owning scope and parent approval. Rewrite success is not visual acceptance. |
| Map and connected map data | `hoi4.map_inspect`, `hoi4.map_inspect` with render arguments (`layer`, `overlays`, `scale`, `tile`, or `area`) | `hoi4.map_rewrite` or an equivalent declarative writer | Inspect connected provinces, states, regions, adjacency, supply, and rail data before a proposal, review the edit, submit one rewrite call, then retain post-validation and recovery evidence. | A map render is offline evidence and does not prove in-game pathing, supply, or consumer behavior. |

If a route is absent, record the exact tool, selector, package version, and error once, then continue with local references and source review as described under Route-unavailable behavior.

## Local reference workflow

Confirm the connected reference routes and their live schemas once per unchanged connection. Begin with `hoi4.reference_context` for the relevant surface, then search and read exact rules not already returned. A list of source citations is navigation; read the pertinent excerpts. Reuse those excerpts while their revision and relevance are unchanged instead of opening the same files again. Installed documentation defines current syntax; check a vanilla precedent when available. If retrieval fails, read the relevant local files and record the gap once.

Check `omittedSources` for available sources skipped by a bounded context response and cover required omissions with a larger limit or targeted search/read. `missing` identifies absent files. Read relevant `knownMistakes` with their cited symptoms and fixes; a returned rule does not prove a defect in the mod.

Use `hoi4.source_lookup` for exact definitions, overrides and consumers. Keep `includeReferences: false` for definition-only reads when consumers are irrelevant. For a diagnostic or diff position, pass `path` and `line` instead of `symbol`; the result identifies indexed owners and the innermost `keyPath`. Locate first, then use the returned owner identifier and path for a separate symbol-navigation request; do not mix locate and navigation selectors.

When supported, select a nested block with a bounded `keyPath` and `view: "structure"`. Repeated keys use zero-based `occurrence`; continue children with `nextChildOffset` as `childOffset`, the same selectors and `expectedRevision`. Source-text continuation uses `nextLine` and `nextColumn` as `fromLine` and `fromColumn`; continue only the needed block. Verify near-miss `suggestions` instead of treating them as matches. For a reference-search hit inside a long section, pass `matchLine` as `reference_read.startLine` and preserve its source id and revision.

Prefer `hoi4.script_validate` file mode (`path`) for changed script files. Inspect `checksPerformed` and unresolved commands, and check `KNOWN_MISTAKE_<RULE>` findings when `known_mistakes` ran. Snippet validation does not establish that this file-level pass ran. A true result proves only performed checks; unchecked argument semantics and game execution need other evidence. Fix confirmed source defects and recheck the affected behavior under the route-unavailable limits.

## Before-and-after workflow

Use the steps that answer a concrete question about the change, and reuse results until their inputs change.

1. Identify the surface owner, source files, accepted design authority, exact selector, and intended validation scenarios before calling MCP.
2. Run the matching narrow read-only inspect route and retain diagnostics, linked files, revision, and artifact URI.
3. Run the matching deterministic render route when the surface has a visual or layout representation, and retain the fidelity or limitation report.
4. For weighted logic, complete the probability scenario contract before evaluating any ranking, timing, or selection result.
5. Review source, pertinent cited offline wiki and installed-documentation sections, tests, and the owning skill in parallel with MCP evidence.
6. Make the source change through the normal authorized workflow or through the bounded rewrite lifecycle below.
7. Rerun the same inspect and render queries after the change, then use the matching compare route where the package provides one.
8. Preserve pre-change and post-change URIs, revisions, scenario hashes, diagnostics, and unresolved limitations in the handoff or review record.
9. Report which conclusions rest on MCP evidence and which on source review or calculation; never describe source review as MCP proof or live engine validation.

## Local documentation and source discovery

Use `hoi4.reference_context` for the current work surface, `hoi4.reference_search` for a command or behavior, and `hoi4.reference_read` for the exact cited section. Preserve its path, line span, and revision. Follow the returned continuation only when more of that section is needed. `hoi4.source_lookup` provides exact definitions, override status, and indexed usages through the same configured workspace. Installed game documentation is the primary syntax reference, and the offline wiki supplies broader guidance; do not fetch the wiki website. Whole-page reading is unnecessary when the cited sections cover the task. If a route or local source is unavailable, read the pertinent local file directly and record the exact gap. When a live context result includes `omittedSources`, raise the result limit or use targeted search/read to cover those required sources; `missing` identifies absent files instead. At a limit of 1, installed documentation can occupy the only result; a limit of 2 or more can retain both available required source kinds. Context excerpts select question-matching sections within required files, but still require reading the cited rules. Domain-specific inspect, render, compare, and scenario evidence remains required.

When supported by the live schema, use `source_lookup` with `view = structure` and a bounded `keyPath` to inspect one nested source block.
Repeated keys require their zero-based `occurrence`; structural continuation uses `nextChildOffset` as `childOffset` with the same query settings and `expectedRevision`.
Use definition-only event and scripted-helper reads when consumers are not needed.
When the live schema accepts `path` and `line` instead of `symbol`, `source_lookup` returns the indexed definitions containing that line, innermost first, and a `keyPath` from the innermost definition; use it to cite or navigate from a diagnostic, diff, or editor position.
A lookup that finds no definition may return `suggestions`, which are near-miss identifiers to verify rather than matches.
Search results carry `matchLine`; pass it as `startLine` to `reference_read` to land on the answering line inside a long section, including a single wiki table entry.
Installed `dlc/` and `integrated_dlc/` folders are read-only source layers between the base game and the mod, ordered by DLC ID, and a mod's `descriptor.mod` `replace_path` entries apply to analysis as the game applies them. An installed DLC folder does not show that a playset enables that DLC.

When exposed, `hoi4.script_validate` checks an effect or trigger body under a declared scope using installed native-command documentation.
Supply external scope bindings only when their types are known.
A true result covers only `checksPerformed`; `valid = null`, unresolved helpers, unchecked argument blocks, and omitted findings require further source inspection.
These checks do not establish parameter semantics or game execution.
With a mod-relative `path` instead of a body, `hoi4.script_validate` checks every effect and trigger body of an event, decision, national focus, scripted helper, or on-action file under the scope its structure fixes, and treats the mod's own scripted effects and triggers as known commands.
Run it on each changed script file before handing work to live testing: its errors predict load errors the game reports, such as a dynamic variable compared as a trigger or a scope link outside its scopes.
Its warnings cover player-facing text (colour codes in news and report events, development wording, unlocalised flags in requirement tooltips) and visible events that would reach one player once per loop iteration; treat each as a defect to fix or a recorded decision.

For launch diagnostics, `hoi4.error_log` reads the last existing `logs/error.log`, groups patterns, reports source freshness and new/persisting/fixed entries, and attaches a matching `knownMistake` rule and fix. It never launches the game. Use `scope: "mod"` and category/text filters; stale logs are historical evidence.

Use `hoi4.mod_index` with `mode: "overview"` for descriptor, counts and namespaces, or `mode: "next_id"` with a `kind` and namespace/prefix before allocating an ID across source layers.

`hoi4.reference_context` exposes the surface's reviewed `knownMistakes`. File-mode `hoi4.script_validate` reports applicable rules as `KNOWN_MISTAKE_<RULE>` and `known_mistakes` in `checksPerformed`; retain the rule ID, symptom and fix. Coverage is limited to reported checks; resolved rules do not run.

## Probability scenario contract

Use the probability routes only for a declared surface and scenario rather than treating a single weight dump as balance evidence.

1. Start every weighted audit with `hoi4.probability_inspect` for the relevant adapter or source.
2. Name every analyzed surface and scenario identifier, and preserve the resulting scenario hash.
3. Supply the complete candidate pool whenever the adapter normalizes weights or runs a selection race.
4. Declare prerequisites, availability and visibility gates, bypasses, target validity, external modifiers, state changes, cadence, cooldowns, removal or reset rules, terminal states, uncertain inputs, and seeds.
5. Pass named `scenarioSet` values to `hoi4.probability_inspect` for exact or bounded traces. Inspection evaluates by default; `evaluate: false` returns only inventory. Omitted scenarios use a fact-free state and leave missing facts unresolved.
6. Use `hoi4.probability_analyze` with `analysis: "sweep"` for thresholds, sensitivities, timing drift, starvation, dominance, and rank reversals.
7. Before editing a weighted source, save an immutable pre-edit source copy and the exact scenario fixture; record their paths and SHA-256 hashes. Use `hoi4.probability_analyze` with `analysis: "compare"` with real `before.path` and `after.path` source paths and the identical `scenarioSet`. Keep revision and hash evidence outside those source objects.
8. Use `hoi4.probability_analyze` with `analysis: "simulate"` only when explicitly declared uncertain inputs require sampling, and label the result sampled rather than exact.
9. Use `hoi4.probability_analyze` with `analysis: "sequence"` only when a complete custom pool, cadence, state transition, and terminal-state contract is declared.
10. Use `hoi4.probability_analyze` with `analysis: "render"` when a ranking, matrix, timing, sensitivity, sequence, comparison, or unresolved view improves review.
11. Classify every conclusion as exact, bounded, sampled, score-only, or unresolved.

Never state an exact selection probability when the candidate pool or external factors are incomplete, and never describe a score race as a click probability without normalization evidence.

Any patch to a weighted surface follows an audit-patch-compare cycle: establish named baseline scenarios, preserve the exact pre-edit source and fixture, let the owning implementation authority change source, and compare the same scenarios after the patch. A saved analysis URI cannot replace the pre-edit source. If that source is missing or a deleted candidate prevents a valid comparison, retain before and after inspect evidence and mark the numeric delta unresolved; never compare the current file to itself.

## Rewrite and recovery lifecycle

The lifecycle applies to focus, GUI, and map rewrites, including Agent Nudger or an equivalent declarative writer.

1. Scope and authority: confirm the exact files, identifiers, accepted design authority, and allowed write surface before proposing changes.
2. Inspect: obtain the narrow pre-change diagnostics, linked artifacts, source revision, and any required render or probability baseline.
3. Review the bounded source proposal and its intended validation before calling the rewrite.
4. Rewrite: submit one authorized domain rewrite through the shared engine. Validation, stale-source checks, atomic replacement, post-validation, and failure recovery remain internal to that call.
5. Post-validation: review returned diagnostics and artifacts, rerun required inspect/render comparisons, and record the resulting revision.
6. Recovery: retain any failure and restoration evidence. Never request a transaction ID, plan hash, separate apply call, or rollback command; intentional reversal after success is a new authorized source change.

A blocked proposal must not mutate source.
GUI preview scenarios accept `flags`, `variables`, and `closedFlags: true`, which treats undeclared flags as unset; set them so tabbed windows and flag-driven panels render one page at a time, and treat `GUI_UNRESOLVED_VISIBILITY_OVERLAP` as missing scenario facts rather than a layout defect.

For scripted GUI work, the optional rewrite's automatic transaction success or post-write/index validation is not itself a completion gate. An authorized reviewed GUI edit may be applied directly without another fallback approval solely because that optional rewrite blocks or rolls back; required inspect/render evidence, matched comparisons, and correction of visible in-scope defects remain mandatory. This rule does not disable the server's internal validation.

The public MCP surface does not provide caller-managed transaction, apply, or rollback commands in the installed package, so intentional reversal of a successful edit is a new authorized source change, normally through version control.

Do not call a successful source reversal an MCP rollback unless the installed route explicitly exposes and records that operation.

## Route-unavailable behavior

For a tool failure or an unsupported or inconclusive analysis, allow the initial read-only request and at most one retry with corrected or narrower inputs; skip the retry when the route is known to be unavailable or there is no useful correction.
The limit follows the underlying failure across files, scenarios, routes that need the same capability, agents, and resumed turns; a new request name, an unrelated source edit, or a successful status poll does not reset it.

Record the exact route requested, selector, package version, command or transport, error text, the attempts already used, and what would justify one more attempt, in the existing handoff or work note.

Then continue with the useful local checks: the pertinent wiki and installed-documentation sections, the source, tests, and calculations from the actual script for weighted logic.
Those checks can support completion, but they are source review, not MCP evidence or observed game behavior, and the report must say so.

An unavailable route does not excuse a confirmed defect: fix it and recheck the affected behavior.
Inspect current source or transaction state before retrying an uncertain mutation.

## Registration and troubleshooting

HOI4 Mod Setup installs and verifies the exact package version recorded in `hoi4-mod-setup.manifest.json`. For a manual setup, run `python -I .tools/mcp/bootstrap_hoi4_agent_tools.py`, which installs the same recorded version with its registry-integrity and runtime-entry checks; `npm install --global hoi4-agent-tools` installs the newest release instead. Isolated Python mode prevents project-local modules from shadowing standard libraries; the automatic app route remains authoritative for source-script verification.

The bootstrap requires native x64 Node.js 22.19+ within major 22, or Node.js 24
LTS. It uses a private, SHA-512-pinned npm CLI: 11.19.0 on Windows and 10.9.9 on
Linux. These versions reproduce the reviewed platform package trees; npm 10
and 11 handle cross-platform optional dependencies differently. The user's
ambient npm executable/config is not changed by the private CLI. Installing a
missing compatible Node.js distribution also installs its bundled npm. The
private CLI runs from a fresh neutral temporary
directory with empty user/global configuration, an isolated home/cache and no
inherited npm or Node overrides. Temporary files are removed on ordinary
completion and never reused after interruption. All package, entry and tree
integrity checks remain mandatory; do not replace a reviewed hash to accept a
different npm realization.

When measuring a new release, use the same pinned npm version for each platform
and verify both supported Node majors in clean Windows/Linux x64 runners.

For an explicitly reviewed development archive, use `python -I .tools/mcp/bootstrap_hoi4_agent_tools.py --local-tarball C:/path/to/hoi4-agent-tools-4.0.3.tgz`. This opt-in verifies exact SHA-512 and retains full installed-tree, count, runtime-entry, and wrapper checks. Dependencies and the private npm toolchain still use the fixed registry. There is no automatic fallback or downgrade; the default route verifies the published registry pin.

To refresh a published pin, obtain `npm view hoi4-agent-tools@4.0.3 dist.integrity --json --registry=https://registry.npmjs.org`, install that exact version into a new empty prefix with `npm install --global --prefix C:/path/to/new-clean-prefix --ignore-scripts --no-audit --no-fund --registry=https://registry.npmjs.org hoi4-agent-tools@4.0.3`, then run `python scripts/refresh_mcp_package_pin.py --prefix C:/path/to/new-clean-prefix --integrity <reviewed-sha512-value>`. The helper measures the bounded full tree and runtime entry, verifies version and any present npm lock integrity, and synchronizes the bootstrap and manifest contract. Run the contract tests and projection checks, commit source changes, then regenerate manifest evidence from that exact source commit. The generator reads immutable Git blobs, never working-tree bytes.

If the recorded version is unavailable or fails verification, record the package/version blocker instead of silently substituting an unpinned clone.

The repository bootstrap (`.tools/mcp/bootstrap_hoi4_agent_tools.py`) verifies registry integrity first, then keeps a matching complete installed tree without reinstalling it. It uninstalls any other installed copy before the exact install, because npm upgrades a shrinkwrapped package in place without pruning modules the previous release needed, so an in-place upgrade never matches the reviewed tree. Replacing the package requires every HOI4 MCP client to be closed or disconnected first: a running server keeps Sharp's native libraries loaded, and npm cannot replace them.

For a local mod, register `hoi4-agent-tools.cmd` (Windows) or `hoi4-agent-tools` with the mod directory as its working directory: the project `.mcp.json` entry `hoi4_agent_tools` for Claude Code, and `[mcp_servers.hoi4_agent_tools]` in `.codex/config.toml` for Codex; a mod-local working directory normally lets the server detect the source without a separate selection call.

Use `hoi4-agent-tools-setup --init` only when persistent multi-mod or remote configuration is required.

Use stdio for a local agent process.
A stdio server exits when its launching process exits. Codex keeps one server per subagent connected after the subagent finishes, so the Codex registration sets `HOI4_AGENT_STDIO_IDLE_EXIT_MINUTES = "30"`; leave that variable out of registrations for long interactive sessions.

For a separate HTTP process, run `hoi4-agent-tools-http --config PATH` with loopback binding, a long bearer token supplied through an environment variable, an exact origin allowlist, and explicit workspace grants.

Non-loopback deployment requires HTTPS, an authenticated identity layer such as OAuth or OIDC, isolation, and the restrictions documented by the package for that deployment mode.

When tools are missing, check `npm list --global hoi4-agent-tools --depth=0`, confirm the target project is trusted, verify the server command resolves, and restart the MCP client after installation or registration changes.

If npm reports `EBUSY` for a loaded native DLL, close or reconnect existing HOI4 MCP clients and rerun the exact-package bootstrap.
Keep the archive, runtime-entry, and full package-tree checks intact; a busy file does not justify weakening them.

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
| Rewrite and recovery | Single rewrite call, returned diff/artifacts, post-validation and failure/restoration evidence. |
| Result classification | Exact, bounded, sampled, score-only, or unresolved. |
| Limitations and blocker | Missing route, dynamic behavior, incomplete pool, fidelity warning, or other unresolved issue. |

No live-server validation is implied by this documentation-only guide; confirm the installed route and retain fresh evidence when applying it to a mod.
