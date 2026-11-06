# HOI4 Subagents: Agent roster

Part of the [hoi4-subagents](../SKILL.md) skill. Read before choosing which specialist to spawn, or when a task could fit several agents. It holds each role's job, model tier and boundaries.

## Available subagents

Canonical subagent definitions are the Claude Code files in `.claude/agents/<hyphen-name>.md`; prose uses the snake_case routing names. The `model` field sets each role's Claude tier (Opus for `hoi4_improvement_loop_planner`; Sonnet for `hoi4_3d_model_pipeline`, `hoi4_feature_completion_auditor`, `hoi4_localisation_auditor`, `hoi4_scripted_system_architect`, and `hoi4_skill_maintainer`; Haiku for every other role). After changing a canonical file, run `python .tools/sync/sync_agents.py` to regenerate the Codex, Cursor, Qoder, and OpenCode projections, and use `--check` to detect stale or missing outputs. Never hand-edit a projection.

Use `hoi4_repo_explorer` only for read-only repo exploration when touched-file mapping, pattern search, vanilla reference mapping, missing-file recovery, dependency mapping, or edit-order planning is actually unclear. It is not a default preflight agent.

Use `hoi4_improvement_loop_planner` for feature improvement loop planning, detailed expansion specs, historical and regional research notes, and implementation-ready improvement handoffs. This replaces the old mechanic-expander role. It writes plans and addenda. It does not patch gameplay files.

Use `hoi4_asset_source_researcher` for non-portrait real or archival image sourcing, historical flags, historical symbols, user-provided source photos, source-image processing, and report, news, or custom feature images that must depict real historical material.

Use `hoi4_portrait_creator` for every character portrait. It researches and archives grounded sources, creates crops and placeholders, validates styled finals from the selected Cloud, Local, or RunPod route, invokes the image generator for fictional or impossible subjects, processes PNG/DDS outputs, installs portrait-specific wiring, and writes manifests and handoffs.

Use `hoi4_generated_feature_art` for generated non-icon art, including fictional or alternate-history report images, news images, large presentation images, custom feature images, fictional flags, faction emblems, UI panels, dossier art, progression-state base art, and animated non-icon presentation pieces. Do not route final character portraits through this worker.

Use `hoi4_icon_artist` for generated gameplay icon families, bespoke vanilla-green custom-unit counters, formable seals, scripted GUI icons, and small animated icon or button sprites. Follow `hoi4-feature-assets` for the exact owning UI surface and reference folder.

Use `hoi4_3d_model_pipeline` for bounded custom HOI4 3D model work covering provider candidates, Blender processing, model textures, rigs, skeletal actions, sourced custom-unit audio research and synchronization design, `.mesh`/`.anim` export, QA evidence, and runtime handoffs.

Use `hoi4_quote_remark_researcher` for main quotes, exact wording checks, attribution confidence, source comparison, button text, cultural remarks, slogans, allusions, and short references.

Use `hoi4_audio_researcher` for licensed or public-domain audio research, including presentation cues, source verification, download, `.ogg` conversion, and audio handoff notes.

Use `hoi4_focus_tree_auditor` for focus tree audits and active small patches covering branch depth, route coverage, icons, localisation, rewards, prerequisites, mutual exclusions, AI, focus-formable links, and simplification.

Use `hoi4_decision_mission_auditor` for decision and mission audits and active small patches covering category lifecycle, objective quality, costs, tooltips, scripted GUI decision hooks, AI behavior, cleanup, balance, and exploit risk.

Use `hoi4_event_ui_worker` to create or improve the scripted GUI window that one named event or event-owned mechanic specifically adds. It uses the model tier set in its canonical agent file and the active MCP live-preview and comparison workflow from `hoi4-scripted-gui`, while `hoi4-decisions-missions` retains gameplay action integrity. It must not audit event logs, event-detail frameworks, settings, shared framework windows, or unrelated existing UIs.

Use `hoi4_country_package_auditor` for country package audits and active small patches covering tags, history, states, leaders, portraits, flags, parties, focus loading, ideas, advisors, units, technologies, claims, cores, localisation, AI, formables, and playable setup.

Use `hoi4_localisation_auditor` for localisation and scripted localisation audits and active small patches covering missing keys, duplicate keys, encoding, tooltip quality, broken dynamic text, namespace consistency, dynamic cost text, and cross-surface text mismatch.

Use `hoi4_scripted_system_architect` for reusable scripted system design and active narrow implementation covering scripted effects, scripted triggers, script constants, event targets, meta effects, variables, tuning values, formable helpers, scripted GUI button helpers, and dynamic helper logic.

Use `hoi4_documentation_curator` for documentation cleanup and consistency during long implementation. It reconciles specs, plans, docs, handoffs, manifests, prompts, reports, and README files, writes source-of-truth maps and resume packets, marks superseded docs, records plan dispositions, and flags contradictions. It patches documentation surfaces only and does not edit gameplay files, localisation, assets, external tabular data files, or workbooks unless explicitly in scope.

Use `hoi4_feature_completion_auditor` for read-only spec-versus-implementation audits covering events, mechanics, assets, docs, text and audio packages, focus trees, decisions, validation, and accepted plan addenda.

Use `hoi4_ai_probability_auditor` for read-only audits of AI weights, MTTH, event `ai_chance`, random lists, focus and research selection, decision and mission scores, AI strategy factors, and declared custom weighted pools. It must use the HOI4 MCP probability workflow and return scenario-specific evidence; do not treat another focus, decision, country, or completion audit as a substitute for this specialized pass.

Use `hoi4_spreadsheet_doc_worker` only for mod-maintained spreadsheets, CSV exports, or workbooks when the repository actually has them or the parent explicitly requests them. It uses the spreadsheet skill and preserves the named file structure without assuming the mod has that kind of external record.

Do not route new work to obsolete planner aliases. Use `hoi4_improvement_loop_planner` and the `hoi4-improvement-loop` skill.

