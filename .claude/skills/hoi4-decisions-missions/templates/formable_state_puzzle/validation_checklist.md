# Formable state-puzzle validation checklist

This checklist records evidence for a copied owner implementation. It does not claim that the skill-local package is loaded by the game.

## Manifest and installed geometry

- [ ] `state_manifest.example.json` validates against `state_manifest.schema.json` before any example value is copied.
- [ ] The owner manifest records the active installed `map/provinces.bmp`, `definition.csv`, and every state-history file with revision and SHA-256 values.
- [ ] Every state entry lists the exact state id, localisation key, province ids, row-run or mask checksum, source bounding box, transparent bounding box, projection, canvas position, and shared-border rule.
- [ ] The geometry extraction report is archived beside the owner implementation and its checksum matches the manifest.
- [ ] A map revision change causes every state mask and projected position to be rebuilt.

## Piece and sprite contract

- [ ] There is exactly one state-piece icon and one hover region for every manifest state.
- [ ] Neighbouring pieces use one origin, scale, projection, and border policy and do not leave a seam gap or double outline.
- [ ] The unresolved composite is grey, hatched, and outlined.
- [ ] The qualifying composite is green and carries a check or solid inner keyline.
- [ ] The GFX file contains only static sprite registrations and uses owner runtime asset paths after copying.
- [ ] No animation frame, movement, pulse, or transform-only effect appears in the piece, cue, border, or static alternative.

## Shared eligibility and refresh

- [ ] One state-scope helper owns the owner, controller, core, subject, ally, and occupation policy.
- [ ] Each generated state wrapper calls that helper instead of repeating its clauses.
- [ ] The live count uses descending `count_triggers` over every per-state wrapper, or a documented event-refreshed count calls the same helper once per manifest state and writes only owner-scoped count, required-count, and dirty variables.
- [ ] The summary status and formation decision availability call the same territory helper.
- [ ] Alternate-group rules are explicit in the manifest and composed by the territory helper.
- [ ] The formation decision evaluates the territory helper at availability time and cannot be bypassed by presentation state.
- [ ] When the optional variable path is used, refresh calls cover the decision open/visibility path and every already-scoped state-transfer, control, focus, or event effect that can change a required state.
- [ ] No whole-world daily, weekly, monthly, or other periodic iterator was added for the display.

## Hover, summary, and decision context

- [ ] The hover names the current state and resolves current owner, current controller, control result, core result, and qualification result.
- [ ] Owner and controller fallback text is shown when either scope is absent.
- [ ] The summary shows the current qualifying count, display denominator, and final readiness status without raw variable names.
- [ ] The scripted GUI uses `context_type = decision_category` and stays within the compact category description width.
- [ ] The state pieces are informational icons only and expose no dead click region or fake button.
- [ ] The static-category alternative gate is recorded and is false whenever the puzzle is needed.

## AI and lifecycle

- [ ] The AI uses the same formation decision trigger and territory helper without opening or clicking the human-facing GUI.
- [ ] The GUI has no action effects and no AI-only shortcut.
- [ ] When the optional variable path is used, completion, cancellation, route invalidation, and country identity changes call the owner cleanup effect.
- [ ] Optional cleanup clears only owner-owned count, required-count, dirty, and selected-state variables.
- [ ] Costs, route gates, alternate minima, control policy, and refresh tuning live in the owner manifest, script constants, or documented tuning file rather than call-site literals.

## Assets, localisation, and evidence

- [ ] Every GFX texture path resolves under the owner asset package and never points into the skill-local directory.
- [ ] The YAML localisation file is UTF-8 with BOM and contains category, summary, requirement, hover, owner/controller fallback, control, core, and status keys.
- [ ] A GUI inspect artifact covers the linked category, hierarchy, click regions, hover regions, and sprite properties.
- [ ] Full-window renders cover every supported resolution and show both unresolved and qualifying states.
- [ ] The same named scenarios are used to compare piece status, summary status, and formation decision availability.
- [ ] Any unavailable MCP route, unresolved engine dynamic-list scope, missing geometry artifact, or deferred in-game check is recorded with the exact reason.
