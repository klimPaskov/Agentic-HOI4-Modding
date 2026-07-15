---
name: hoi4-mcp-workbench
description: Use the installed HOI4 MCP server from coding-agent workflows to analyze event chains and to inspect, render, create, clean, and validate national focus trees, scripted GUIs, and maps in an external mod workspace.
---

# HOI4 MCP Workbench

Use the MCP server as a normal coding-agent tool alongside repository skills,
`AGENTS.md`, and bounded subagents. It edits the configured mod workspace; it
does not replace the agent's planning, source review, or final validation.

## Setup once per machine

1. Install Node.js 22 or newer.
2. Install the package:

   ```powershell
   npm install --global hoi4-agent-tools@2.0.0
   ```

   If the npm release is not available yet, clone the standalone project and
   run `npm install --global . --ignore-scripts` from its root.

3. Register the server with the mod being edited as its process working
   directory:

   ```toml
   [mcp_servers.hoi4_agent_tools]
   command = "hoi4-agent-tools.cmd"
   cwd = "C:\\Users\\<you>\\OneDrive\\Documents\\Paradox Interactive\\Hearts of Iron IV\\mod\\<your_mod>"
   ```

4. Reload the coding agent. With a mod-local `cwd`, the server infers the
   current workspace; call the domain tool directly and omit `workspaceId`.
   No server configuration or mod-selection command is needed. Use
   `hoi4-agent-tools-setup --init` only for persistent multi-mod or remote
   deployments.

## Tool routing

- Focus work: `hoi4.focus_inspect`, `hoi4.focus_render`, then
  `hoi4.focus_rewrite`. Use `layoutMode: "compact"` for cleanup or a complete
  plan for a new tree. Review diagnostics and the rendered artifact before
  continuing with unrelated edits. For very large trees, set
  `reviewScale: 0.25` when the default render budget is too large.
- Event work: use `hoi4.event_inspect` with `scan` or `roots`, then narrow the
  chain with `trace`, `explain_path`, `state_flow`, or `impact`. Record the
  returned revision, edit event and connected source files with the agent's
  normal file workflow, then pass that revision to `hoi4.event_compare` as
  `before`. Finish with `hoi4.event_inspect` in `lint` mode and a focused
  `hoi4.event_render` view. Event tools are read-only. Comparison covers the
  workspace graph and does not take a chain selector.
- Scripted GUI work: `hoi4.gui_inspect`, `hoi4.gui_render`, and
  `hoi4.gui_rewrite`. Provide a deterministic window scenario and render the
  states and resolutions that matter.
- Map work: `hoi4.map_inspect`, `hoi4.map_render`, and `hoi4.map_rewrite`.
  Inspect province geometry and connected state/region data before a
  declarative rewrite.

MCP responses contain compact summaries and links to larger HTML, SVG, PNG,
JSON, and diff artifacts. Read linked artifacts when the inline result is
bounded. Keep the agent's stdout available for MCP data and send diagnostics or
progress to the normal agent log channel.

## Workflow rules

- Let the coding agent decide when MCP helps; do not add a separate approval
  step to the workflow.
- Keep `hoi4-focus-trees`, event, asset, planning, and subagent skills active.
  They define design and repository rules; MCP performs shared inspection,
  layout, rendering, and file transactions.
- Keep event calls narrow. Use selectors, direction, depth, and node limits;
  read linked JSON only when the compact summary is insufficient. Do not load
  an entire overview into context for a one-chain task.
- For new focus trees, write the route plan first, then pass the complete plan
  to `hoi4.focus_rewrite`. For GUI and map creation, provide the full source or
  declarative operations required by the tool schema.
- Use the offline wiki and installed vanilla documentation required by the
  repository instructions before editing HOI4 syntax. MCP diagnostics augment
  that review; they do not replace it.
- Inspect `git diff` and run the repository's tests after writes. Never claim a
  render or rewrite succeeded from a placeholder, static diagram, or an
  unvalidated response.
- If the server is unavailable, report the exact setup or tool error and keep
  the work scoped; do not silently substitute a mock MCP result.
