---
name: hoi4-super-events-planning
description: Use when a selected Super Events workflow needs an implementation-ready plan for a campaign-scale presentation moment.
---

# HOI4 Super Events Planning

Use this selected-only add-on after the optional `hoi4-super-events` package is installed. Do not install or reference it in an unselected base project.

## Required sources

Read the accepted feature brief, the installed `hoi4-super-events` skill, and the relevant sections of `hoi4-feature-planning`, `hoi4-events`, `hoi4-feature-assets`, and `hoi4-text-audio-research`. Inspect the project’s existing event, GUI, GFX, scripted localisation, localisation, sound, documentation, and naming patterns before proposing identifiers or paths.

## Ownership

This skill owns the presentation plan and cross-surface acceptance contract. `hoi4-feature-planning` owns the surrounding feature design, `hoi4-events` owns ordinary event logic, and `hoi4-super-events` owns the installed runtime contract.

## Planning workflow

1. Confirm that the moment is campaign-scale: a first reveal, irreversible escalation, world-order change, rare ideological victory, catastrophic collapse, global defeat, or genuine campaign ending.
2. Record the owning gameplay caller and the state transition that must be established before presentation.
3. Reserve or propose one stable project-scoped registration ID without reusing an established ID.
4. Define the title, description, quote, response, image, and audio directions as research briefs rather than invented final assets.
5. Specify every runtime branch, sprite, localisation key, caller, duplicate-suppression rule, close cleanup, documentation update, and acceptance scenario required by the installed package.
6. Route quote, audio, and art work through `hoi4-super-events-subagents` only when the work is substantial enough to justify a narrow subagent.

The plan must tie tone to the exact role. A formation, negotiated federation, violent restoration, hidden-route reveal, defeat aftermath, and terminal collapse should not share generic dramatic language or interchangeable art.

## Audio decision

Audio is generically optional in the reusable runtime. Record `optional` when the selected project has not made audio part of the accepted feature contract; missing audio must not block the visual package in that case.

Record `required` only when the user, accepted specification, or established project convention explicitly requires a final cue for this moment. A project-specific required cue blocks completion until it is sourced, rights-checked, converted through the project’s verified route, registered, wired, documented, and validated. Do not silently downgrade required audio to optional or promote optional audio to a requirement.

## Required handoff

The plan must include the presentation role, owning caller, established-before-show state, stable registration ID, title and description direction, quote themes, response tone, image direction and source mode, audio decision, research questions, runtime touchpoints, documentation targets, cleanup behavior, and one named acceptance scenario.

## Validation

Reject a plan that has no live caller, maps multiple unrelated moments to one ID, invents project commands or sound helpers, assumes Chaos Redux paths or prefixes, or treats a dramatic image as sufficient justification for the feature.

## Update triggers

Update this skill when the installed runtime’s registration model, required branches, planning handoff, audio decision rule, caller boundary, or acceptance evidence changes.

## Completion standard

The main agent can implement the selected presentation package without guessing identifiers, ownership, research scope, audio requirement, cleanup behavior, or acceptance evidence.
