---
name: hoi4-super-events-subagents
description: Use to route selected-only Super Event quote, audio, and art work to narrow context-complete subagents.
---

# HOI4 Super Events Subagents

Use this selected-only add-on with `hoi4-super-events` and the generic `hoi4-subagents` skill. It adds three narrow routes without changing the generic base-agent registry.

## Global rule

Every custom subagent must be spawned with `fork_context=false`. The parent prompt must contain every task constraint, accepted decision, current status, relevant path, prior handoff, forbidden scope, and output path needed for the bounded job. Never rely on inherited conversation context.

## Routes

| Need | Agent |
| --- | --- |
| Quote candidates, exact wording, attribution, response text, cultural fit, and copyright notes | `hoi4_super_event_quote_researcher` |
| Audio candidates, source and license verification, download, project-verified conversion, and audio handoff | `hoi4_super_event_audio_researcher` |
| Image direction, source-mode research, named-reference review, and explicitly authorized image-package production | `hoi4_super_event_art_researcher` |

Use the generic `hoi4-subagents` routes for unrelated event research, broad feature planning, ordinary assets, audits, localisation review, scripted-system architecture, documentation curation, and other non-selected workflows.

## Required parent prompt

Every selected-only prompt includes the mod root, stable registration ID, presentation role, owning caller, accepted plan path, exact research or production question, named input paths, exact output and handoff paths, user constraints, source-mode or audio decision, and forbidden files. Include project conventions only when verified from named files.

For quote work, include title and description direction, desired response tone, themes, source constraints, and maximum practical UI length. For audio work, include whether audio is generic optional or project-specific required, the exact role and pacing, named project audio references, accepted format or conversion workflow when verified, and uniqueness or approved-reuse rules. For art work, include target dimensions, composition role, source mode, named references, prohibited imagery, final paths, and whether production is authorized or the task is research-only.

## Ownership boundary

Subagents return research notes, source files, processed assets, manifests, and handoff notes only within explicitly granted paths. They do not edit gameplay, event, localisation, scripted localisation, GUI, GFX, sound definitions, documentation outside the named note, or registry files.

The main agent reviews every handoff and owns final wording, implementation, registration branches, caller effects, sprite wiring, audio wiring, close cleanup, documentation alignment, validation, and completion claims.

## Handoff quality

Every handoff lists files created or changed, candidates considered, selected recommendation, sources and confidence, uncertainty, blockers, validation performed, and exact next wiring steps. Audio handoffs state whether absence blocks completion. Art handoffs state source mode and provenance. Quote handoffs distinguish direct quotation, short fragment, title reference, and paraphrased allusion.

## Update triggers

Update this skill when selected-only agent names, context requirements, ownership, output paths, audio blocking semantics, art source modes, handoff fields, or audit expectations change.

## Completion standard

Each narrow job returns sufficient evidence for the main agent to implement or report a blocker without broad repository exploration, invented context, or unauthorized edits.
