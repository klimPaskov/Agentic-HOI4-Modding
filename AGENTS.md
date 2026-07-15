# Agentic HOI4 Modding Guidelines

This repository is a reusable workflow kit for coding agents working on
Hearts of Iron IV mods. Start the agent from the target mod's Git root so it
can read that mod's `AGENTS.md`, skills, offline wiki, and documentation.

## MCP setup

Install the MCP server once on the machine that runs the coding agent:

```powershell
npm install --global hoi4-agent-tools@2.0.0
```

Register the global server with the target mod as its working directory. For
Codex, the entry is:

```toml
[mcp_servers.hoi4_agent_tools]
command = "hoi4-agent-tools.cmd"
cwd = "C:\\Users\\<you>\\OneDrive\\Documents\\Paradox Interactive\\Hearts of Iron IV\\mod\\<your_mod>"
```

Reload the agent after installing or changing the registration. No server
config, mod-selection command, or per-mod initialization is needed. Run
`hoi4-agent-tools-setup --init` only for a persistent multi-mod or remote
configuration.

After reload, call the domain tool you need directly. When the MCP working
directory is the target mod, omit `workspaceId`; the server resolves it from
that directory. Explicit workspace IDs remain available for configured
multi-mod or remote deployments.

## Normal agent workflow

Use MCP whenever a task benefits from shared HOI4 parsing, layout, rendering,
diagnostics, or declarative transactions. The agent chooses the call as part of
its normal workflow; do not add a separate approval step or a second editor.
Keep the repository's skills, plans, `AGENTS.md`, and subagents in control of
design and task routing. MCP is one focused implementation tool and should not
replace those instructions or consume the whole context.

| Work | Inspect | Review | Apply |
| --- | --- | --- | --- |
| Focus trees | `hoi4.focus_inspect` | `hoi4.focus_render` | `hoi4.focus_rewrite` |
| Event chains | `hoi4.event_inspect` | `hoi4.event_render`, `hoi4.event_compare` | Edit normal mod source |
| Scripted GUI | `hoi4.gui_inspect` | `hoi4.gui_render` | `hoi4.gui_rewrite` |
| Maps | `hoi4.map_inspect` | `hoi4.map_render` | `hoi4.map_rewrite` |

For focus-tree cleanup, use `layoutMode: "compact"`; set `reviewScale: 0.25`
for very large trees if the default render budget is exceeded. For a new tree,
pass a complete focus plan. For GUI work, pass a complete scenario and source or
patch package. For map work, inspect connected province, state, region,
adjacency, supply, and railway data before applying declarative operations.
Read linked HTML, SVG, PNG, JSON, and diff resources when inline MCP results
are shortened.

For event work, begin with `hoi4.event_inspect` in `scan` or `roots` mode,
record its revision, then narrow the task with `trace`, `explain_path`,
`state_flow`, or `impact`. Edit the source files normally and finish with
`hoi4.event_compare` using that revision as `before`, `lint`, and a focused
`hoi4.event_render` view. These three event tools analyze source without
rewriting it. Prefer bounded selectors and compact results; open linked JSON
only when the summary does not contain enough evidence.

## HOI4 source workflow

- Read the relevant pages in `paradox_wiki/` before editing HOI4 syntax.
- Read the matching files in the installed game's `documentation/` folder and
  inspect a vanilla example for the system being changed.
- Use the matching skill under `.agents/skills/` before focus, event, decision,
  asset, planning, animation, or improvement work. Use
  `hoi4-mcp-workbench` for MCP routing and setup details.
- Let the main agent own final wiring, review, validation, and completion
  reporting. Subagents stay bounded to their assigned handoff.
- Keep all edits in Git. Review the diff and run the repository's relevant
  tests after MCP writes. Report incomplete routes, missing assets,
  localisation, diagnostics, or setup failures instead of replacing them with
  placeholders.
