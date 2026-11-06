---
name: hoi4-map-states
description: Use when creating, editing or auditing Hearts of Iron IV map and state data, including map files, history/states, strategic regions, buildings, victory points, supply, state scripting, map MCP tools.
---

# HOI4 Map and States

Generic guidance for the Hearts of Iron IV map and state system: what each map file does, how a state is defined, how script changes states at runtime, and which engine mistakes fail silently.
Use `hoi4-decisions-missions` for decisions that target states, and `hoi4-events` for event chains that mutate states.
Dynamic modifiers on states are covered in `hoi4-ideas-modifiers`, state transfers as diplomacy (peace deals, release, annexation) in `hoi4-diplomacy-war`, and `load_oob`, `create_unit`, and division spawning in `hoi4-units-divisions`.

This file is a router. It keeps the decision procedure, the validation procedure, the repository conventions and the silent-failure list, which apply to every task. Open the reference for your phase from the map below before you write or edit anything it covers.

Rules that always apply (full text in the references named):

- Every state needs an `owner`, and ids must stay contiguous (states from 1, provinces from 0, strategic regions sequential). A gap crashes, and so does script that touches an ownerless state. See [State files, categories and buildings](references/state-files-and-buildings.md).
- Geometry changes (new provinces, state splits, strategic regions) go through `hoi4_map_inspect` and `hoi4_map_rewrite`, never hand-edited BMPs and CSVs. See [Map folder and MCP map tools](references/map-folder-and-mcp-tools.md).
- Building effects need the containing state in scope, and `rail_way` is built only with `build_railway`. See [Runtime state effects](references/runtime-state-effects.md).
- `for_loop_effect` over state ids stops at 1,000 iterations, so sweep with a scope iterator. See [State triggers and iteration](references/state-triggers-and-iteration.md).
- Source reading does not prove runtime behaviour. The user performs in-game checks; do not launch the game.

The file-by-file formats for `map/` (provinces, `definition.csv`, strategic regions, adjacencies, supply nodes, railways, bitmaps) are in the existing [map-geometry.md](references/map-geometry.md). Read it before touching any file under `map/`.

## Reference map

- [Source map](references/sources-and-precedents.md): Read to find the authoritative documentation, wiki page and vanilla precedent for a map or state topic before you cite or mirror it. Covers: Contents; Source map.
- [Map folder and MCP map tools](references/map-folder-and-mcp-tools.md): Read before changing map geometry or calling the hoi4_map_inspect and hoi4_map_rewrite tools, and read it together with `references/map-geometry.md` before touching any file under `map/`. Covers: Map folder summary; MCP map tools.
- [State files, categories and buildings](references/state-files-and-buildings.md): Read before writing or editing history/states files, state categories, building definitions or their map models. Covers: State history files: skeleton and keys; State categories and building slots; Buildings (common/buildings) and building models.
- [Runtime state effects](references/runtime-state-effects.md): Read before scripting ownership, control, building, resource, modifier or occupation changes on a state during play. Covers: Runtime state effects.
- [State triggers and iteration](references/state-triggers-and-iteration.md): Read before writing triggers on states, iterating a set of states, or sweeping states with a loop. Covers: Runtime state triggers; Iterating states and the loop cap.
- [State flags, victory points and map modes](references/state-flags-vp-and-map-modes.md): Read before using state flags or variables, victory points, resources, supply, railways or scripted map modes at runtime. Covers: Flags, variables, and modifiers on states; Victory points, resources, supply, railways at runtime; Map modes and map GFX.

## Decision procedure: which mechanism

1. Change what a state or province is at game start (owner, cores, buildings, VPs, resources): edit the `history/states/*.txt` file, not script effects. Use a dated block (`1936.1.1 = { ... }`) when only some bookmarks need the change.
2. Change ownership or control during play: `transfer_state_to` (state scope) or `transfer_state` (country scope) moves owner and controller together. Use `set_state_owner_to` or `set_state_controller_to` only when the two must differ. Use `set_province_controller` for a single province.
3. Give or remove buildings during play: `add_building_construction` (queues construction, `instant_build = yes` skips it), `set_building_level` (sets an exact level), `remove_building`, `damage_building`. Railways and supply hubs use `build_railway` and its own checks, never these (see Buildings).
4. Make a building type that does not exist: `common/buildings`, plus an icon frame, localisation, and (for model-bearing buildings) an entity and `map/buildings.txt` rows.
5. Change the map geometry (new province, state split, new strategic region): use the Agent Nudger MCP routes (`hoi4_map_inspect`, `hoi4_map_inspect` with render arguments (`layer`, `overlays`, `scale`, `tile`, or `area`), `hoi4_map_rewrite`) rather than hand-editing BMPs and CSVs. See MCP map tools. When the geometry follows a hand-drawn reference, work from the original at full detail and follow it for placement and shapes (realm positions, coasts, lakes, ranges, which realms are landlocked). Fill what it simplifies or omits (coast detail, rivers, small lakes, terrain transitions, borders along real features) by judgment checked against the lore, never copy its flaws (sheet edges, flat colour patches, scan seams, lettering), record each inference, and compare renders beside the drawing.
6. Apply a lasting effect to a state without editing its file: a state dynamic modifier (`add_dynamic_modifier` in state scope; see `hoi4-ideas-modifiers`), a state category change (`set_state_category`), or `add_extra_state_shared_building_slots`. Ideas are country-only and cannot carry a state modifier.
7. Track per-state progress or memory: state flags for presence and small integers, state variables for numbers (see Flags, variables).
8. Visualise per-state data on the map: a scripted map mode (see Map modes).
9. Sweep many states: a scope iterator (`every_owned_state` and siblings), never a numeric loop over state ids (see Iterating states).

## Validation procedure

1. Confirm every id you added is unique and contiguous: states from 1, strategic regions sequential, provinces from 0. `hoi4_map_inspect` with `allocationRequests` gives the next free ids.
2. Every province in a state is in one strategic region and every state province exists in `definition.csv`.
3. Every state has an `owner`, a known `state_category`, and localisation for `STATE_<id>` and each `VICTORY_POINTS_<province>`.
4. Every naval base or floating harbour has a `buildings.txt` row naming its adjacent sea province; the file is not empty.
5. Supply nodes and railways reference state-owned land provinces.
6. Re-read any state file the Nudger touched (stripped quotes, version-less loc).
7. For script, check each effect's scope against the effects documentation, use `hoi4_script_validate` on the body under its explicit scope when exposed, and treat a `valid` result as covering only its listed checks.
8. Runtime behaviour (ownership after transfer, production-menu visibility, VP markers) is a live-game question; do not report it as verified from source reading alone.

## Repository conventions

- Tabs for indentation, lowercase snake_case, no `<=` or `>=`, UTF-8 with BOM for localisation.
- No magic numbers: put shared tuning (caps, batch sizes, building levels) in `common/script_constants/` and read them with `constant:category.key` where the field supports it; fields that reject constants take a variable or an `@` constant. Duration fields such as `days =` in timed flags may need a variable assigned from the constant first.
- Reuse and extend the project's dynamic scripted effects library (`common/scripted_effects/<prefix>_dynamic_effects.txt`, named in `CLAUDE.md`) before writing new state helpers, such as the existing state building damage and random-state helpers.
- The 1,000-iteration cap and the whole-world iteration permission rule above come from `CLAUDE.md` sections 1 and 4.
- A hidden-idea carrier is a modifier-free idea whose id is a token for a package-owned setup effect (item 11 of `hoi4-project-rules/references/mechanic-checklist.md`, summarized in `CLAUDE.md` section 4); it is unrelated to states.
- Do not write player-facing text about tuning history; state names and VP names describe the world only.

## Common mistakes and silent failures

1. A state without `owner` that script later touches (crash).
2. Gaps in state ids, province ids, or strategic region ids.
3. A state split across two strategic regions.
4. A new naval base or floating harbour without a `buildings.txt` row (late crash when AI or player uses it) or an empty `buildings.txt`.
5. `need_detection = yes` on a state-level building (map crash when zoomed on by a foreign player).
6. `load_oob` for a country that owns no state (silent no-op).
7. Using `add_building_construction` on `rail_way` (crash per the wiki); use `build_railway`. Supply hubs may use `add_building_construction`, as vanilla does.
8. Calling `add_building_construction` in a country scope (does nothing) or for a provincial building outside the containing state's scope.
9. Looping state ids with `for_loop_effect` past 1,000.
10. `set_state_owner_to` when control should follow; the state keeps the old controller.
11. Province ids that are invalid or belong to no state in `supply_nodes.txt`, `railways.txt`, `unitstacks.txt`, `weatherpositions.txt`, or adjacency rows.
12. LF line endings in `definition.csv` (every continent reads as missing).
13. 32-bit or colour-space-tagged `provinces.bmp`, or editing indexed bitmaps in a tool that rebuilds the palette.
14. Renaming a vanilla state file in a mod (both versions load).
15. Flag triggers in player-visible blocks without a localisation key.
16. Treating `scope_exists` as a state validity check on a stored variable.
17. Treating `add_resource` without `days` as temporary; it stays until a matching negative amount removes it (installed documentation: `days` makes it temporary).
18. Expecting a dated `history` block to run during play; it is evaluated once when the game starts, for dates before the chosen start date.
19. Trusting the wiki claim that `airports.txt` and `rocketsites.txt` are required; the installed game has neither.
20. Forgetting that peace or ceasefire resets `set_province_controller` to the owner.
21. Overriding a vanilla state file under a name that is off by one character, which loads both, since spacing differs even between neighbouring vanilla names (`333-British Borneo.txt`, `1023 - Brunei.txt`). [vanilla-confirmed 1.19.4.1]
22. A start other than 1936 needs the bookmark `date`, the `START_DATE` define and the dated history blocks to describe the same date, as vanilla does at 1936.1.1.12 for its default bookmark and the define. [vanilla-confirmed 1.19.4.1]
    What an inconsistent start date does in game is untested. [unverified]

## Unverified or conflicting points

- `region` versus `area` state triggers: identical installed descriptions; the distinction is not documented.
- `impassable_ignored_links` and `force_link_ownership_to` semantics beyond the vanilla comments.
- Whether scope iterators such as `every_state` are subject to `MAX_EFFECT_ITERATION`; the defines comment names loop effects only.
- `need_detection` meaning: the wiki says "?"; the state-building crash is a live-game observation recorded in this repository, not a documented rule.
- The `hoi4_map_rewrite` operation schema was not readable; no write operation was attempted.
- The wiki claims `add_building_construction` crashes on railways; this was not tested.
- Whether `every_owned_state` or `every_core_state` re-evaluates membership after a `transfer_state_to` inside the loop; the installed documentation only shows `transfer_state_to` inside `every_core_state` and does not describe the iteration order.
- Whether dated history blocks execute in file order or date order.
