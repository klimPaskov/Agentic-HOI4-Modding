# Skill and agent catalog

Claude Code owns the canonical definitions. Other runtimes use the generated projections described in [Runtime support](runtimes.md).

## Skills

| Skill | Purpose |
| --- | --- |
| [hoi4-3d-model-pipeline](../.claude/skills/hoi4-3d-model-pipeline/SKILL.md) | Create, rig, animate, convert, export, or repair custom Hearts of Iron IV 3D models and prepare their sourced sound and bespoke counter handoffs. |
| [hoi4-ai-strategies](../.claude/skills/hoi4-ai-strategies/SKILL.md) | Use when designing, tuning or debugging HOI4 country AI, from ai_strategy blocks, add_ai_strategy and strategy plans to AI focuses, ai_will_do and ai_chance weights, and AI templates. |
| [hoi4-characters-leaders](../.claude/skills/hoi4-characters-leaders/SKILL.md) | Use when defining, recruiting, promoting or retiring HOI4 characters and their roles (leaders, advisors, commanders, scientists), leader traits, ideologies, portraits and localisation. |
| [hoi4-comfyui](../.claude/skills/hoi4-comfyui/SKILL.md) | Route grounded HOI4 portrait replacement work to the explicitly selected ComfyUI Cloud, Local, or user-run RunPod provider without operating the provider on the user's behalf. |
| [hoi4-comfyui-cloud](../.claude/skills/hoi4-comfyui-cloud/SKILL.md) | Use when the generic HOI4 portrait pipeline selects Comfy Cloud. |
| [hoi4-comfyui-local](../.claude/skills/hoi4-comfyui-local/SKILL.md) | Use when the generic HOI4 portrait pipeline selects a local ComfyUI installation. |
| [hoi4-comfyui-runpod](../.claude/skills/hoi4-comfyui-runpod/SKILL.md) | Use when the generic HOI4 portrait pipeline selects a RunPod ComfyUI workspace. |
| [hoi4-debug-playtest](../.claude/skills/hoi4-debug-playtest/SKILL.md) | Explicit-invocation-only HOI4 debug playtest that fixes a mod from fresh logs and tests it; never use unless the user names this skill or explicitly asks for autonomous desktop playtesting. |
| [hoi4-decisions-missions](../.claude/skills/hoi4-decisions-missions/SKILL.md) | Use when designing, implementing, auditing, or fixing HOI4 decisions, missions, timed objectives, decision categories, costs, cost and mission localisation, AI weights and balance. |
| [hoi4-diplomacy-war](../.claude/skills/hoi4-diplomacy-war/SKILL.md) | Use when scripting Hearts of Iron IV diplomacy, factions, subjects, autonomy, wargoals, war and peace, guarantees, military access, opinion modifiers, annexation, release or state transfers. |
| [hoi4-equipment](../.claude/skills/hoi4-equipment/SKILL.md) | Use when creating, changing or scripting HOI4 equipment, archetypes, variants, bonuses, modular designs, stockpile or production effects, or when equipment or a bonus silently does nothing. |
| [hoi4-events](../.claude/skills/hoi4-events/SKILL.md) | Use when implementing, updating, auditing or documenting HOI4 events and event chains, including country, news and report events, on_actions, event text, localisation, pictures, hooks and validation. |
| [hoi4-feature-assets](../.claude/skills/hoi4-feature-assets/SKILL.md) | Use when a Hearts of Iron IV mod needs final visual assets such as icons, event images, flags, portraits, UI art or animations, including sourcing, DDS conversion, placement and wiring. |
| [hoi4-feature-planning](../.claude/skills/hoi4-feature-planning/SKILL.md) | Use when expanding a Hearts of Iron IV mod feature idea into a deep, implementation-ready specification covering focus trees, decisions, AI, achievements and asset prompts, before coding. |
| [hoi4-focus-trees](../.claude/skills/hoi4-focus-trees/SKILL.md) | Use when designing, implementing, auditing or fixing Hearts of Iron IV national focus trees, including routes, branches, prerequisites, layout, rewards, ideas, AI and localisation. |
| [hoi4-frame-animation](../.claude/skills/hoi4-frame-animation/SKILL.md) | Use when a HOI4 mod needs animated sprites, icons, portraits, GUI pieces, pulses or frame sheets; the final asset is a frame-sheet texture built from real per-frame art, never a GIF. |
| [hoi4-ideas-modifiers](../.claude/skills/hoi4-ideas-modifiers/SKILL.md) | Use when creating or auditing HOI4 ideas, national spirits, hidden ideas, laws, advisor ideas, dynamic, static or custom modifiers, timed ideas and modifier tooltips or localisation. |
| [hoi4-imagegen](../.claude/skills/hoi4-imagegen/SKILL.md) | Use when making or replacing Hearts of Iron IV mod art in any of the 40 families with the hoi4-imagegen MCP, from plan and generate to process, validate, preview, review and install. |
| [hoi4-improvement-loop](../.claude/skills/hoi4-improvement-loop/SKILL.md) | Use when a working or drafted HOI4 feature, focus tree, decision system, country, formable, GUI or asset set still feels thin and needs a concrete expansion spec or improvement handoff. |
| [hoi4-investigate](../.claude/skills/hoi4-investigate/SKILL.md) | Use before fixing any HOI4 mod bug, regression or crash, and to check a "done" report, with a static root-cause protocol from source, vanilla and documentation. |
| [hoi4-live-playtest](../.claude/skills/hoi4-live-playtest/SKILL.md) | Use for explicitly requested live Hearts of Iron IV evidence through the selected live-testing provider, or manual checks when no server is selected. |
| [hoi4-map-states](../.claude/skills/hoi4-map-states/SKILL.md) | Use when creating, editing or auditing Hearts of Iron IV map and state data, including map files, history/states, strategic regions, buildings, victory points, supply, state scripting, map MCP tools. |
| [hoi4-mtth](../.claude/skills/hoi4-mtth/SKILL.md) | Define and use HOI4 MTTH variables safely (base/modifiers, file-scoped constants, and mtth:entry usage in set_variable/set_temp_variable) with guidance for minimizing ai_will_do clutter. |
| [hoi4-native-raids](../.claude/skills/hoi4-native-raids/SKILL.md) | Use when implementing or auditing native Hearts of Iron IV raid types, especially outcome scope, target validation, dispatch, and native costs. |
| [hoi4-portrait-production](../.claude/skills/hoi4-portrait-production/SKILL.md) | Use for HOI4 character portraits, from real-source research and placeholders to Cloud, Local or RunPod styled replacements, fictional portraits, DDS processing, wiring and handoffs. |
| [hoi4-project-rules](../.claude/skills/hoi4-project-rules/SKILL.md) | Use when a HOI4 mod task needs the full project rules summarized in CLAUDE.md, such as coding style, localisation, completion proof, skill routing, MCP use, subagents, specs, checks or git. |
| [hoi4-save-inspection](../.claude/skills/hoi4-save-inspection/SKILL.md) | Use when the user supplies or names a Hearts of Iron IV save, or when runtime state would settle what source reading cannot, with a read-only inspector for plain-text saves. |
| [hoi4-scripted-gui](../.claude/skills/hoi4-scripted-gui/SKILL.md) | Design, implement, repair, or review Hearts of Iron IV scripted GUI layouts using reference images, native controls, and active MCP live previews throughout construction. |
| [hoi4-shared-git-commit](../.claude/skills/hoi4-shared-git-commit/SKILL.md) | Use when committing one finished HOI4 mod change from a shared working tree whose index or files also contain other agents' staged or unstaged work. |
| [hoi4-subagents](../.claude/skills/hoi4-subagents/SKILL.md) | Use when coordinating HOI4 project subagents for implementation, asset production, text and audio research, audits, small patches, planning handoffs or documentation work. |
| [hoi4-super-events](../.claude/skills/hoi4-super-events/SKILL.md) | Use when designing, researching, wiring or documenting Hearts of Iron IV super-events and their localisation, sourced quote, audio and image handoffs, slots and registration. |
| [hoi4-technology-doctrines](../.claude/skills/hoi4-technology-doctrines/SKILL.md) | Use when creating or scripting HOI4 technologies and folders, unlocks, research bonuses, sharing groups, grand doctrines and mastery, or when a tech or doctrine is invisible or unresearchable. |
| [hoi4-text-audio-research](../.claude/skills/hoi4-text-audio-research/SKILL.md) | Use when a Hearts of Iron IV mod task needs sourced quotes, cultural remarks, slogans, title-like references, public-domain text, licensed music, sound cues, or audio source documentation. |
| [hoi4-units-divisions](../.claude/skills/hoi4-units-divisions/SKILL.md) | Use when creating or changing Hearts of Iron IV sub-units, division templates, orders of battle (land, naval, air), division names, unit spawning and removal, manpower and sub-unit stats. |
| [xlsx](../.claude/skills/xlsx/SKILL.md) | Create, edit, analyze, validate, or recalculate mod-maintained XLSX, XLSM, CSV, and TSV files while preserving workbook structure, formulas, formatting, and declared source-of-truth ownership. |

## Agents

Opus maps to `xhigh`, Sonnet to `high`, and Haiku to `medium` reasoning effort in Codex. Claude uses the declared model tier and the same explicit per-agent effort value where the model supports effort controls. Cursor and OpenCode inherit the model; Qoder uses its runtime tool policy.

| Agent | Purpose | Claude tier | Codex effort |
| --- | --- | --- | --- |
| [hoi4-3d-model-pipeline](../.claude/agents/hoi4-3d-model-pipeline.md) | Creates, rigs, animates, processes, exports, audits, and documents bounded HOI4 3D model packages from one approved source-informed input per geometry task using the profile's generation model (currently Meshy 7), Meshy MCP, the Blender HOI4 adapter, and io_pdx_mesh. | Sonnet | high |
| [hoi4-ai-probability-auditor](../.claude/agents/hoi4-ai-probability-auditor.md) | Read-only weighted-logic auditor for HOI4 AI weights, probabilities, MTTH, random selection, focus and research selection, decision and mission scores, strategy factors, and declared weighted pools. | Haiku | medium |
| [hoi4-asset-source-researcher](../.claude/agents/hoi4-asset-source-researcher.md) | Finds, verifies, and documents non-portrait real or archival visual source assets for HOI4 mods. | Haiku | medium |
| [hoi4-audio-researcher](../.claude/agents/hoi4-audio-researcher.md) | Researches, verifies, downloads, edits, converts, and documents licensed or public-domain audio for HOI4 mod presentation surfaces. | Haiku | medium |
| [hoi4-country-package-auditor](../.claude/agents/hoi4-country-package-auditor.md) | Active auditor and small-patch subagent for HOI4 country packages. | Haiku | medium |
| [hoi4-decision-mission-auditor](../.claude/agents/hoi4-decision-mission-auditor.md) | Active auditor and small-patch subagent for HOI4 decisions, missions, timed objectives, decision categories, scripted GUI decision surfaces, costs, tooltips, AI behavior, cleanup, balance, and exploit risk. | Haiku | medium |
| [hoi4-documentation-curator](../.claude/agents/hoi4-documentation-curator.md) | Documentation cleanup and consistency subagent for HOI4 mods. | Haiku | medium |
| [hoi4-event-ui-worker](../.claude/agents/hoi4-event-ui-worker.md) | Active implementation and visual-layout subagent for a scripted GUI window introduced and owned by one named HOI4 event or event mechanic. | Haiku | medium |
| [hoi4-feature-completion-auditor](../.claude/agents/hoi4-feature-completion-auditor.md) | Read-only completion auditor for HOI4 mod feature implementation. | Sonnet | high |
| [hoi4-focus-tree-auditor](../.claude/agents/hoi4-focus-tree-auditor.md) | Active auditor and small-patch subagent for HOI4 focus trees. | Haiku | medium |
| [hoi4-generated-feature-art](../.claude/agents/hoi4-generated-feature-art.md) | Generates and processes non-icon fictional, symbolic, supernatural, alternate-history, Second World War-style report, news, large presentation, UI, flag, faction-emblem, and other feature art for HOI4 mods. | Haiku | medium |
| [hoi4-icon-artist](../.claude/agents/hoi4-icon-artist.md) | Creates generated icon and vanilla-green unit-counter packages plus frame-by-frame small animated sprite packages for HOI4 mods. | Haiku | medium |
| [hoi4-improvement-loop-planner](../.claude/agents/hoi4-improvement-loop-planner.md) | Plan-only improvement loop subagent for HOI4 mods. | Opus | xhigh |
| [hoi4-localisation-auditor](../.claude/agents/hoi4-localisation-auditor.md) | Active auditor and patch subagent for the current HOI4 mod localisation, scripted localisation, dynamic text, tooltip quality, key coverage, encoding, cross-surface consistency, and direct, concise, readable player-facing prose. | Sonnet | high |
| [hoi4-portrait-creator](../.claude/agents/hoi4-portrait-creator.md) | Owns complete HOI4 portrait production: grounded-source research and source placeholders, fictional generated portraits, user-supplied styled-result validation, processing, DDS conversion, portrait wiring, manifests, and handoffs. | Haiku | medium |
| [hoi4-quote-remark-researcher](../.claude/agents/hoi4-quote-remark-researcher.md) | Finds, verifies, compares, and documents quote, response, cultural remark, slogan, title-reference, and allusion candidates for a HOI4 feature. | Haiku | medium |
| [hoi4-repo-explorer](../.claude/agents/hoi4-repo-explorer.md) | Read-only HOI4 mod repository explorer for large or uncertain tasks. | Haiku | medium |
| [hoi4-scripted-system-architect](../.claude/agents/hoi4-scripted-system-architect.md) | Active architect and narrow implementation subagent for reusable HOI4 scripted effects, scripted triggers, script constants, event targets, meta effects, variables, tuning tables, formable helpers, scripted GUI helpers, and dynamic helper logic. | Sonnet | high |
| [hoi4-skill-maintainer](../.claude/agents/hoi4-skill-maintainer.md) | Creates, updates, audits, and trims HOI4 mod repository skills. | Sonnet | high |
| [hoi4-spreadsheet-doc-worker](../.claude/agents/hoi4-spreadsheet-doc-worker.md) | Optional spreadsheet-only worker for mod-maintained CSV/XLSX tables when a repository actually has them or the parent explicitly requests them. | Haiku | medium |
| [hoi4-super-event-art-researcher](../.claude/agents/hoi4-super-event-art-researcher.md) | Researches visual direction and prepares explicitly authorized art packages for a selected Super Event. | Haiku | medium |
| [hoi4-super-event-audio-researcher](../.claude/agents/hoi4-super-event-audio-researcher.md) | Researches, verifies, prepares, and documents licensed audio for a selected Super Event package. | Haiku | medium |
| [hoi4-super-event-quote-researcher](../.claude/agents/hoi4-super-event-quote-researcher.md) | Researches and documents sourced quote and response candidates for a selected Super Event package. | Haiku | medium |

## Live-testing provider choice

HOI4 Mod Setup offers Clausewitz MCP (default), experimental HOI4 Live Tools, and manual testing. [Clausewitz MCP](https://github.com/smerss/Clausewitz-MCP) by smerss is MIT licensed and reads state directly from native Linux HOI4 **1.19.2 only**, without OCR or saves for those reads. Windows uses WSL; macOS uses SSH to Linux. Complete manual Linux/game/server setup and confirm the Linux game and server are ready in HOI4 Mod Setup before registration.

HOI4 Live Tools is Windows verified only; upstream macOS support is incomplete. It is experimental, slower and not thoroughly tested. The app installs its pinned runtime without global registration and manages project registrations for selected coding clients. Manual testing registers no server. Use update or repair to reselect the provider and clients, review changed guidance and registrations, and preserve custom instructions. Follow the selected server tool list; providers do not promise identical operations.
