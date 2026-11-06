# Project rules: HOI4 MCP usage

Part of the [hoi4-project-rules](../SKILL.md) skill. `CLAUDE.md` summarizes section 0 (HOI4 MCP). Read before using the HOI4 Agent Tools routes, when a route fails, and before reporting MCP evidence.

### HOI4 MCP

The `hoi4-agent-tools` server (`hoi4_agent_tools`) supports focus trees, event chains, technology trees, weighted logic, scripted GUIs, maps, and local documentation and source lookup. HOI4 Mod Setup installs and registers it; for a manual setup follow Registration and troubleshooting in `docs/systems/hoi4_agent_tools_mcp_integration.md`. Its route set changes between releases, so use the routes the connected server advertises in its live tool list instead of a remembered inventory, and read each route's live schema before relying on optional parameters.

Use checks that answer a concrete question about the change and reuse results until their relevant inputs change.
For a tool failure or an unsupported or inconclusive analysis, allow the initial read-only request and at most one retry with corrected or narrower inputs; skip the retry when the tool is known to be unavailable or there is no useful correction.
The limit follows the underlying failure across files, scenarios, tools using the same unsupported capability, agents, and resumed turns. A new request name, an unrelated source edit, or another successful status poll does not reset it; retry only after new information or a tool or input change addresses the failure.
Then read local references and code directly and run the useful available checks. This limit does not excuse a confirmed code defect: fix the defect and recheck the affected behavior.
Record the failed check, the attempts already used, and what would justify trying again once in the existing handoff or work note; do not create another report for unchanged results.
Continue implementation instead of polling unchanged status or repairing external tools unless tooling work was requested. Inspect current source or transaction state before retrying an uncertain mutation.
Tool exposure does not prove service health or the availability of a standalone viewer. A successful read-only domain call establishes that a route works without a separate health check.

- Documentation and source: follow the local reference workflow in `docs/systems/hoi4_agent_tools_mcp_integration.md#local-reference-workflow` for context, search, cited reads, nested definitions and continuations; retain path, line span and revision. When `hoi4.script_validate` is exposed, check effect or trigger bodies under their scope; a true result covers only its `checksPerformed`.
- Focus, event, technology, GUI, and map work: inspect the changed surface, render or compare when that answers a real question, and apply reviewed edits directly or through the matching rewrite route. GUI work follows `hoi4-scripted-gui`; without a renderer, review source geometry, assets, text, and state wiring and state the visual-check limitation.
- Weighted logic: prefer `hoi4.probability_inspect` and representative named scenarios. If an analyzer cannot handle the script, calculate a few relevant cases from the actual code and explain what remains uncertain.
- Diagnostics and IDs: use `hoi4.error_log` only for user-supplied or explicitly requested logs, and `hoi4.mod_index` for a bounded overview or `mode: "next_id"` before allocating IDs. Run `hoi4.script_validate` with each changed file's `path`; inspect `checksPerformed` and `known_mistakes`. Read the surface's `knownMistakes` from `hoi4.reference_context` and retain rule IDs and cited fixes; a listed rule does not establish a current defect.

MCP supports implementation and review; successful MCP output is not a universal completion gate. When a skill calls an MCP route mandatory and it is unavailable, record the exact blocker and report that evidence as missing: source review and local checks can then support completion, but never describe them as MCP proof or live engine validation, and an auditor marks the missing evidence unresolved, never passed.

The detailed capability, artifact, probability-scenario, rewrite-recovery, and troubleshooting notes are in `docs/systems/hoi4_agent_tools_mcp_integration.md`.

<!-- HOI4_MOD_SETUP:COMPONENT:workflow.live_tools:START -->
