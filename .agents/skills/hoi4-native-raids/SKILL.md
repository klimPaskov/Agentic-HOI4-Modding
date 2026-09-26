---
name: hoi4-native-raids
description: Use when implementing or auditing native Hearts of Iron IV raid types, especially outcome scope, target validation, dispatch, and native costs.
---

# HOI4 Native Raids

Use this skill for `common/raids/` definitions and effects launched by their `success_levels`. Use `hoi4-events` for related event chains and `hoi4-decisions-missions` for separate decision or mission surfaces.

## Read the engine contract

Inspect the installed vanilla `common/raids/_documentation.md`, relevant vanilla raid definitions, and installed effect and trigger documentation before editing. The installed documentation controls native fields and scope. Record the exact vanilla precedent in the handoff.

## Scope and dispatch

- In raid preflight (`allowed`, `visible`, `show_target`, `available`, `launchable`, and AI selection), the evaluated scope is the actor country; `FROM` refers to the target country when applicable.
- In `success_levels`, both `actor_effects` and `victim_effects` begin in `RAID_INSTANCE` scope. Their names organize outcome UI, not effect scope. Enter `var:actor_country`, `var:victim_country`, or `var:target_state` explicitly before country or state effects. `ROOT` remains the raid instance inside nested blocks.
- If a country helper requires the actor country as `ROOT`, fire an immediate hidden actor `country_event` from `var:actor_country`. Save needed actor, victim, and target scopes as regular event targets in the originating chain before firing it. Regular event targets carry into events fired by that chain; temporary variables do not. Recheck pointers in the receiving event.
- For outcome dispatch across several raid types, use disjoint marker families with an exact-one selection check, or separate fixed hidden event IDs. One country or global pending scalar is unsafe because concurrent raids can overwrite it.
- Credit a delayed reward or achievement only from the actual `success_levels` callback carrying the required outcome marker and accepted proof. Keep credit idempotent; raid creation or preparation proves no outcome.

## Cost and final gate

- Put equipment needed to create a raid in native `essential_equipment` and Command Power allocation in native `command_power`. Do not debit or refund the same native payment again in scripted effects.
- Keep `visible`, `available`, and `launchable` distinct: they control type display, preparation, and starting a prepared raid. If installed documentation does not settle whether a prepared instance remains visible after a type's `visible` gate closes, record that as a live-game question.
- At resolution, recheck the exact target and current policy authorizing the effect, including actor, victim, state, and province where relevant. If the final gate can reject an effect, make the outcome tooltip conditional or neutral.
- Do not promise cancellation refunds or resource recovery without verified engine behavior for that case.

## Evidence and handoff

Check every preflight and outcome branch against the source definition, call sites, event target lifecycle, native cost fields, tooltips, and a vanilla precedent. Use the installed HOI4 MCP route for any related event or weighted surface required by project instructions. Preserve the relevant scenario, revision, coverage, and unresolved findings. Record unverified runtime behavior as uncertainty and leave live-game validation to the user.
