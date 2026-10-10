# Universal installed-map state-registry consumer workflow

Use this workflow when a formable or event-owned state puzzle is built from an installed map. A repository-level registry may own map geometry; a consumer owns only its finite candidate set, projection, live qualification policy, generated outputs, and category attachments. This document is reference guidance, not a runtime file.

## Source and build contract

When available, use the repository's canonical state-geometry registry and consumer compiler. Treat the registry as immutable build input. Record the installed map revision, provinces/definition/state-history provenance, dimensions and wrap metadata, state IDs, province membership, geometry checksums, ordered map roots, consumer specification, generated manifest, and output hashes. Never hand-edit registry geometry, stretch an old mask, redraw a state, or compile against a different map revision.

If the repository does not provide a registry builder/compiler, do not invent a tool name or claim that this skill supplies one. Record the exact capability gap and keep the consumer blocked until the owner provides a reproducible installed-map extraction and validation path.

## Required build order

1. Resolve the active map from the documented game/mod load order and run the available provenance check. Fail closed on map hash, dimensions, state-ID, state-history, or row-run mismatches.
2. Declare a finite consumer specification with formable/category id, candidate state IDs, optional visibility groups, owner/controller/core policy, alternate groups, projection, output paths, and exact helper identifiers. Do not introduce arbitrary state IDs at runtime.
3. Compile one unresolved and one qualifying piece per candidate from the same installed geometry. Record the map revision and source geometry hash in the manifest. Do not promote staged or missing-DDS output.
4. Generate runtime GFX/GUI/scripted-GUI/localisation surfaces only from complete manifests. Reject duplicate normalized IDs, unsafe paths, missing assets, invalid helper identifiers, and missing category attachments.
5. Complete `category_attachment_audit.md` immediately after generation. Enumerate every in-scope category and copy the exact generated GUI identifier and window into each row.

## Runtime contract

The state piece, hover, summary, formation decision `available` trigger, and AI-facing decision logic must use the same live qualification policy. Do not cache green pieces or use `on_daily`, `on_weekly`, `on_monthly`, a whole-world scan, or an unverified refresh loop for presentation. A dirty variable is acceptable only when the engine contract requires it and every scoped state-change caller updates it; it must never replace live decision eligibility.

State pieces are informational. They have no fake buttons, state-changing click actions, or AI-only path. The ordinary formation decision remains the only action.

## Mandatory evidence

Use the installed read-only map inspect/render routes for candidate state membership and geometry, then the GUI inspect/render routes for the linked category, generated window, piece bounds, hover regions, states, and supported resolutions. Record actual artifact URIs, revisions, diagnostics, and unavailable-route blockers. Source-only review is not equivalent engine evidence.

For each final DDS, retain converter output and decoded round-trip evidence with dimensions, hashes, header checks, alpha extrema, and pixel equality. A map or GUI artifact does not prove DDS integrity.

## Handoff minimum

List the registry and consumer spec paths, map roots and content hashes, provenance result, manifest, candidate/visibility policy, generated runtime files, completed category crosswalk, map and GUI artifacts, DDS round-trip evidence, skipped checks, blockers, and every simplification. A deferred candidate, missing DDS, unavailable MCP route, unresolved scope, or staged build is incomplete until explicitly resolved.
