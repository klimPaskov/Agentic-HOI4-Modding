---
name: hoi4-comfyui
description: Route grounded HOI4 portrait replacement work to the explicitly selected ComfyUI Cloud, Local, or user-run RunPod provider without operating the provider on the user's behalf.
---

# HOI4 ComfyUI provider router

Use this router only when `hoi4_portrait_creator` has classified a grounded portrait as needing a user-supplied HOI4-style replacement. Read `hoi4-portrait-production` first, then select exactly one provider skill: `hoi4-comfyui-cloud`, `hoi4-comfyui-local`, or `hoi4-comfyui-runpod`.

Provider selection is explicit and recorded in the portrait handoff. Do not infer a provider from availability, silently switch providers, or treat a queued job as a final portrait. The user supplies the styled result; the portrait owner validates identity, framing, dimensions, provenance, DDS processing, stable runtime names, and final-versus-source-placeholder state.

Agents do not operate RunPod. For Cloud and Local routes, agents still use only the configured endpoint and credentials boundary named by the parent; they do not discover arbitrary installations, expose credentials, or substitute another workflow. If authorization, endpoint, models, custom nodes, hardware, or user-supplied output is missing, leave the portrait pending and report the exact blocker.

This router does not apply to fictional or impossible portraits: `hoi4_portrait_creator` uses native ImageGen for those subjects. It also does not own generic non-portrait art, final gameplay wiring, or live in-game validation.
