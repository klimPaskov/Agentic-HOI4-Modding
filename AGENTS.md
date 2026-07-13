# Agentic HOI4 Modding Guidelines

This repository is a reusable workflow kit for coding agents working on
Hearts of Iron IV mods. Start the agent from the target mod's Git root so it
can read that mod's `AGENTS.md`, skills, offline wiki, and documentation.

## MCP setup

Install the MCP server once on the machine that runs the coding agent:

```powershell
npm install --global hoi4-agent-tools@1.2.0
hoi4-agent-tools-setup --init `
  --mod-root "C:\Users\<you>\OneDrive\Documents\Paradox Interactive\Hearts of Iron IV\mod" `
  --game-root "C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV"
hoi4-agent-tools-setup --print-client-config
```

Use the real Documents or OneDrive path. The `--mod-root` value is the parent
directory whose immediate children are mods. Add another `--mod-root` when
mods are stored in another collection. Copy the printed `globalInstall` or
`codexTomlGlobal` entry into the agent's MCP settings, then reload the agent.
The setup command writes the server config; it does not edit the agent's
settings.

After reload, call `hoi4.mods` and use the returned workspace ID. The server
discovers every configured mod, so agents do not need a per-mod MCP setup.

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
