---
name: hoi4-super-events-text-audio-research
description: Use for selected-only Super Event quote, response, cultural-fit, and audio research with narrow handoffs.
---

# HOI4 Super Events Text and Audio Research

Use this selected-only add-on with `hoi4-super-events` and the generic `hoi4-text-audio-research` skill. The generic skill supplies sourcing, attribution, copyright, licensing, and conversion rules; this add-on supplies the registration-aware presentation handoff.

## Required sources

Read the accepted presentation brief, the installed `hoi4-super-events` skill, the relevant generic research sections, the named permanent research note, and only the project audio folders or catalogues explicitly identified by the parent. Do not infer Chaos Redux paths, formats, settings helpers, or catalogues.

## Research split

Use `hoi4_super_event_quote_researcher` for main quote candidates, exact wording, attribution confidence, response text, cultural remarks, slogans, allusions, and copyright risk. Use `hoi4_super_event_audio_researcher` for source and license checks, composition and recording rights, legitimate download, project-verified conversion, and audio handoff evidence.

The parent must spawn each agent with `fork_context=false` and provide the stable registration ID, presentation role, owning caller, exact research question, accepted tone, audio decision, named input paths, and handoff path.

## Text rules

The title should be short, memorable, and specific. The description should explain the visible consequence without becoming a wall of mechanical text or spoiling intentionally hidden information. The response should read as a reaction to the moment and may use a very short source-aware cultural reference when it fits.

Never invent or misattribute a quote. Compare several candidates, prefer primary and traceable sources, mark uncertainty, keep modern copyrighted excerpts very short, and reject language that sounds dramatic but does not fit the exact reveal, escalation, victory, defeat, aftermath, or ending role.

## Audio rules

Audio is optional for the reusable runtime. When the accepted design leaves it optional, research may return a candidate or a clear blocker, and the visual package remains valid without playback.

When the accepted project design requires audio, the task is incomplete until one intentional final recording is sourced, rights-checked, converted through the repository’s verified workflow, assigned a project-scoped sound ID, wired by the main agent, and documented. Check composition and recording rights separately. Reject unclear licensing, placeholder provenance, mismatched tracks, default cues, primitive waveform or test-tone substitutes, and undocumented reuse.

Do not assume a file format, duration, volume helper, sound path, or conversion command. Read those facts from the selected project and preserve source files and derivative steps according to its established workflow.

## Required handoff

The text handoff records considered candidates, selected quote and response, author or speaker, source work, date or period, source URL, attribution confidence, copyright note, fit explanation, backups, stable registration ID, presentation role, and title and description direction.

The audio handoff records the audio decision, considered candidates, selected track when available, title, creator or composer, performer or recording source, source URL, license and confidence, duration, attribution, source and final paths, editing and conversion steps, proposed project-scoped sound ID, owning caller, trigger and close behavior, uniqueness or approved reuse, and blockers.

## Update triggers

Update this skill when the runtime text branches, research subagents, source evidence, copyright rules, audio requirement semantics, project-audio handoff, or completion evidence changes.

## Completion standard

The main agent receives a source-aware text package and an honestly optional or explicitly required audio package without needing to rediscover provenance, rights, registration context, or wiring intent.
