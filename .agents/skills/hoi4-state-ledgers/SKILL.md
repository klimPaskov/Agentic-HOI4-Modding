---
name: hoi4-state-ledgers
description: Use when implementing or auditing exact state-to-state civilian transfers, sparse aligned cohort registries, state-and-country reception ledgers, or transaction-time state mapmode projections in a Hearts of Iron IV mod.
---

# HOI4 State Ledgers

Use this skill for reusable population-flow infrastructure spanning state and country scope. Keep causes, event prose, historical identities, decision IDs, and owner-specific balance in the owning event, decision, or system skill.

## Source contract

Before editing a transfer or projection surface, read `AGENTS.md`, the relevant owner skill, the offline wiki pages for Data structures, Effects, Triggers, Scopes, and On actions, and installed vanilla documentation for effects, triggers, script concepts, script constants, and scripted map modes. Inspect the existing shared population-loss helper and its paired documentation before adding another debit path.

Use `common/script_constants/` for shared tuning, `common/scripted_effects/` and `common/scripted_triggers/` for the contract, `common/on_actions/` for bounded lifecycle seams, and `common/map_modes/` plus scripted localisation for projections. Do not create a central MCP router or wrapper. For map surfaces, require the actual installed `hoi4.map_inspect` and `hoi4.map_render` evidence before and after relevant changes; use `hoi4.map_rewrite` only for supported declarative writes. If an exact tool is unavailable, record the exact unavailable route and block that evidence; source-only inspection is not equivalent to runtime MCP evidence.

## Exact transfer contract

Make one helper the sole owner of physical population movement. Owner systems submit explicit proof, amounts, route targets, and reason metadata; they do not debit or credit population themselves.

1. Validate a positive request, valid origin state, valid destination state target, route proof, actor proof, and any protected-floor rule before mutating population. Default result and output variables to zero or invalid, and fail closed when proof is missing or ambiguous.
2. Save the destination target only after entering the actual destination state scope. A regular event target may carry that pointer back to the origin for the current effect chain; it is not a durable cohort identity.
3. Read `state_population_k` before the debit, convert with the shared people-per-thousand constant, subtract the protected minimum, clamp the request, and perform the existing exact state-loss helper exactly once.
4. Measure the actual origin debit from before and after state population. Never trust the requested amount as the debit because floors, rounding, and engine reconciliation can change it.
5. Clamp route deaths to the actual origin debit, compute survivors as `actual_debit - route_deaths`, and credit only survivors in the destination state. A destination credit must also be measured from before and after state population.
6. Reconcile any observed owner or controller manpower side effect using the established correction pattern. `add_manpower` is state-local in state scope and country-wide in country scope, so do not infer one from the other.
7. Record route deaths as a slice of the same debit and call the Deaths surface once when requested. A death log must never trigger a second population debit.
8. Keep a conservation residual for review: `actual_debit - route_deaths - actual_destination_credit`. An accepted transaction is valid only when the residual is zero, with bounded engine rounding handled before the acceptance result is published.

Return actual debit, route deaths, survivor credit, destination credit, residual, and a valid or invalid result to the caller. Clear one-shot request variables after both success and rejection so a later decision or event cannot replay stale proof.

## Scope and temporary-variable rules

Normal variables belong to their current country, state, or other scope. Temporary variables do not acquire scope prefixes, so `ROOT.some_temp` and `PREV.some_temp` do not persist or point to another scope. Use normal scoped variables for durable state or country ledgers, event targets for a short-lived scope pointer, and explicit outputs for cross-scope handoff.

Regular event targets are appropriate for a destination or current transaction chain because the engine clears them when the originating effect chain ends. Use global event targets only for intentionally long-lived pointers and provide explicit clear and stale-target handling. Never treat a target name alone as a cohort ID.

Keep state effects in state scope and country effects in country scope. When a helper needs both, measure and update each ledger in its owning scope rather than relying on `OWNER`, `CONTROLLER`, `ROOT`, or `FROM` to remain unchanged through nested scopes. Prefer `state_population_k` over `state_population` for arithmetic to avoid variable overflow.

## Sparse aligned cohort registry

For cohorts that persist beyond one effect chain, use a sparse registry rather than a whole-world scan. Parallel arrays are one row: ID, original state, current host, destination, owning country, amount, source, and lifecycle status. Every append, index update, and removal must touch every array at the same index.

- Use monotonic IDs as identity; array indexes are implementation details and may change after removal.
- Initialize every array and count once, then keep the count equal to the ID array length.
- A new row may retain the origin as an internal placeholder, but status must prevent that placeholder from being treated as a bound destination.
- Resolve by explicit ID first. A state- or country-derived selection is valid only when exactly one row matches; ambiguity, missing rows, stale targets, and invalid ownership fail closed.
- Bind a destination only from the actual destination state scope and update destination, host, and status together.
- Rebind only the destination and current host for a nonterminal row; preserve origin, owner, survivor amount, source, and lifecycle history.
- On cleanup, remove every aligned array element at the same index. Do not erase a live row merely because its origin recovered; retire it only through an explicit terminal transaction or invalidation rule.
- Process only registered active states and countries through bounded hooks or lifecycle callbacks. Do not add unscoped `on_daily`, `on_weekly`, `on_monthly`, `every_state`, or `every_country` scans for registry maintenance.

Use a row status to distinguish active, destination-bound, unsafe-bound, integrated, resettled, returned, and retired states as needed. A status transition is metadata until the owning transaction has already moved the actual people.

## Reception and outcome accounting

Keep reception capacity on the receiving country and reception load on both the destination state and receiving country. The state load answers "how much is in this state"; the country load and capacity answer "how much can this country receive overall." Do not substitute one ledger for the other.

Apply a positive or negative reception delta exactly once per accepted survivor transaction. A credit updates the state and owner-country ledgers by the same actual survivor amount. A debit is valid only when both ledgers can cover the full amount; otherwise it fails closed without changing either ledger. Refresh reception and overcrowding flags or modifiers from those ledgers after the symmetric update.

Integration, resettlement, return, and similar outcomes are accounting projections, not population creation. Record the actual survivor amount and cohort status after the accepted transfer or resolution, and never call a population-adding effect merely to represent an outcome. If a flow ends without movement, record only the proven outcome and its cleanup marker.

## Transaction-time map projections

Global cohort arrays are transaction ledgers, not mapmode inputs. If a mapmode needs origin, outflow, trapped, destination, reception, overload, route status, return, integration, or resettlement visibility, write a state-local projection flag and amount at the existing validated transaction boundary. Do not scan global arrays during map refresh.

Scripted mapmodes have two layers. Use the bottom layer for the primary state role and the top layer for a critical border or route status when that distinction matters. Keep `type = state`, evaluate the current state through the documented `FROM` scope, centralize colors and thickness in script constants, and use `far_text = country`, `near_text = state`, and `update_daily = yes` where the owner surface requires them.

The map engine does not provide a general route-arrow layer. Represent movement with endpoint state projections, border emphasis, and scoped tooltips rather than invented path geometry. Choose a deterministic primary-role priority for overlapping flags and expose secondary roles in tooltip text.

Gate exact ledgers, capacity, source, cohort amount, and outcome totals to the state owner or controller. Public viewers should receive qualitative stage or role text. Distinguish state-local load from owner-country totals in every authorized tooltip, and clear or default every value when the state or country registration retires.

## No-double-counting proof

Before accepting the system, trace every population-changing call site and prove that each accepted movement has exactly one origin debit and at most one measured destination credit. The following are separate and must not be conflated:

- physical origin debit;
- route-death slice of that debit;
- survivor credit in the destination state;
- state and country reception-ledger deltas;
- cohort outcome totals and map projection flags.

Owner adapters may submit pressure, route, border, capacity, or policy proof, but only the transfer owner changes population. Outcome and projection helpers may change ledgers, flags, modifiers, or cohort metadata, but never create the population they describe. A failed route, invalid destination, failed credit, or failed reception delta must leave the corresponding physical and accounting ledgers unchanged.

## Validation and handoff

Run task-specific source checks before parent review:

- verify one physical loss helper owns all movement debits and that Deaths logging is not a second debit;
- verify aligned arrays have identical append, update, and removal sites and that all read variables have initialization and cleanup paths;
- verify no whole-world scan was introduced and every registry processor is bounded to active entries or an explicit lifecycle callback;
- verify route targets are saved from the destination state scope and stale or ambiguous cohort resolution fails closed;
- verify state and country reception deltas are symmetric and mapmode projections are written by validated transactions, not by global-ledger scans;
- verify mapmode definitions use supported layers and state scope, with public versus authorized tooltip disclosure matching the projection data;
- run the owning MCP inspection/render/compare workflow for supported surfaces, or record the exact unavailable route and do not call source-only review runtime evidence;
- exercise valid movement with no deaths, movement with route deaths, protected-floor clamping, blocked or invalid route, partial or failed destination credit, reception credit and debit, ambiguous cohort selection, safe and unsafe destination binding, rebind, terminal resolution, and state-control or annexation cleanup.

The handoff must list changed files, public helper names, scope and target contracts, aligned-array fields and statuses, conservation evidence, projection fields and privacy rules, meaningful validation, skipped checks with reasons, blockers, and parent-owned wiring. Do not put event IDs, historical profiles, one-off balance choices, or private implementation history into this skill.
