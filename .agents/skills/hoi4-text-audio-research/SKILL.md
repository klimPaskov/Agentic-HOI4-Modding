---
name: hoi4-text-audio-research
description: Use when a Hearts of Iron IV mod task needs sourced quotes, cultural remarks, slogans, title-like references, public-domain text, licensed music, sound cues, or audio source documentation.
---

# HOI4 Text and Audio Research

Use this skill when a HOI4 modding task needs researched text or audio for any feature, event, focus route, decision category, custom GUI, loading screen, main menu change, news item, report image package, achievement theme, country reveal, formable proclamation, or other presentation surface.

This skill is optional. Most features do not need quote, remark, or audio research. Use it only when the user, specification, asset prompt, implementation task, or documentation target asks for sourced wording, cultural reference checks, or music and audio licensing.

This skill does not implement gameplay code. It does not wire sound definitions, GUI, event files, localisation files, focus files, decision files, or `.gfx` files unless the parent explicitly grants that scope. Its purpose is to produce reliable source notes, recommended text candidates, usable audio candidates, and handoff material that the main agent can implement.

General event implementation belongs to `hoi4-events`. Visual asset sourcing and processing belongs to `hoi4-feature-assets`. Animated visual work belongs to `hoi4-frame-animation`.

## 1. Core purpose

Text and audio research prevents two common failures:

- using invented or misattributed quotes because they sound plausible
- using audio or cultural references without checking source, license, fit, or copyright risk

A complete research handoff should let the implementation agent know what is safe to use, what is uncertain, what is unsuitable, and what still needs approval.

Use this skill for:

- quote research
- public-domain text research
- cultural remark research
- slogan, proverb, scripture, poem, speech, book, song, film, or game allusion checks
- title-like reference checks
- source and attribution verification
- copyright risk notes for short modern references
- music and audio source research
- audio license verification
- audio download and conversion handoff when permitted
- documentation of source, license, duration, and intended use

Do not use this skill just to make ordinary localisation sound dramatic. If the task only needs normal event text, focus text, decision text, or tooltips, write those through the owning implementation skill.

## 2. Relationship with research subagents

Use the narrow research subagents when actual research work is large enough to split out.

| Need | Spawn |
| --- | --- |
| Quote candidates, exact wording checks, attribution confidence, public-domain text, cultural remarks, slogans, allusions, and short references | `hoi4_quote_remark_researcher` |
| Music or audio candidates, license checks, legitimate downloads, conversion notes, and audio handoff notes | `hoi4_audio_researcher` |

The main agent owns final localisation, final sound wiring, final `.gfx` or `.gui` wiring, final documentation integration, and completion claims. Research subagents return evidence and recommendations. They do not make final implementation claims.

## 3. When to use quote or remark research

Use quote or remark research when a feature needs any of these:

- a main quotation
- a short reaction line based on a real source
- a cultural remark
- a title-like reference
- a slogan
- a proverb
- a scripture reference
- a poem excerpt
- a speech excerpt
- a public-domain literary allusion
- a short song, film, book, or game reference
- attribution notes for a source-dependent line

Do not invent quotes. Do not invent slogans and present them as real. Do not use unsourced quote-site wording as if it were reliable.

If the source matters, verify it.

## 4. What a good quote does

A quote should deepen the feature's specific role. It should not be chosen only because it sounds severe, clever, grim, or famous.

Good quote sources can include:

- public-domain literature
- religious texts
- historical speeches
- philosophical works
- political writings
- military memoirs
- legal documents
- poetry
- mythology
- period documents
- official archives
- propaganda material when source and context are clear

Avoid:

- invented quotes
- misattributed quotes
- unsourced internet quote collections
- modern copyrighted passages that are too long
- quotes whose source cannot be checked
- quotes that fit only in a vague emotional sense

If attribution is uncertain, mark it uncertain or choose another quote. Do not hide uncertainty.

## 5. Quote research workflow

Start with the feature role and the tone needed. Search for sources that match the exact role instead of only the general topic.

Search terms can combine the feature's themes with:

- quote
- speech
- poem
- scripture
- proverb
- historical quote
- public domain quote
- literature quote
- military quote
- political quote
- philosophical quote
- archive
- primary source

Do not stop at the first usable line. Find several candidates, compare them, and recommend the best one.

For each considered quote, record:

- quote text
- speaker or author
- source work, speech, book, scripture, legal text, archive, or collection
- year or approximate period when known
- source URL or repository source path
- source type, such as primary source, archive scan, reputable edition, secondary collection, or uncertain quote site
- why it fits the feature role
- attribution confidence
- copyright or public-domain note when known
- uncertainty notes

Use direct quotes sparingly. Keep excerpts short enough for the intended UI surface.

If a translation is used, state that it is a translation when relevant. Do not alter a quote in a way that changes its meaning.

## 6. Cultural remark and short reference rules

A cultural remark is a short source-aware reaction or allusion. It can be useful for an event option, decision button, achievement hint, custom GUI button, loading quote, presentation card, or other visible surface.

Possible sources include:

- songs
- films
- books
- plays
- poems
- games
- political slogans
- military catchphrases
- religious or mythological phrases
- period idioms
- folk sayings
- propaganda lines

The remark should fit the feature's tone. It can be ironic, grim, understated, reverent, fatalistic, bitter, bureaucratic, absurd, or plain, depending on the feature.

For modern copyrighted works, keep any direct quote very short. Prefer brief fragments, title-like references, or paraphrased allusions when a direct quote would create risk.

Do not use long modern song lyrics, film dialogue, book dialogue, or game dialogue.

Do not misquote a line if presenting it as a direct reference.

For every remark candidate, record:

- remark text or allusion description
- source work or cultural source
- author, songwriter, filmmaker, writer, speaker, or institution if relevant
- year if known
- source URL or repository source path
- whether it is a direct quote, short fragment, title reference, slogan, paraphrase, or allusion
- copyright risk note
- why it fits the feature
- why it should not be used if it is rejected

## 7. Title-like reference rules

A title-like reference can borrow the shape of a source without copying a long passage. It can work for feature names, route labels, decision categories, achievement working labels, or custom GUI panels.

Use it carefully.

A title-like reference should:

- be short
- fit the feature's exact role
- avoid copying a protected line at length
- avoid misleading attribution
- remain readable to players who do not know the source
- avoid turning serious material into a joke unless the feature supports that tone

Document the source and whether the phrase is a direct title, adapted title, public-domain source, common phrase, or modern allusion.

## 8. Source reliability standard

Prefer sources in this order:

1. primary source scans, official transcripts, archive records, legal documents, scripture editions, or original texts
2. reliable editions from libraries, universities, publishers, museums, government archives, or reputable collections
3. reputable secondary works that cite the primary source
4. quote collections only when they identify a traceable original source
5. unsourced quote websites only as search leads, not as final authority

A quote from an unsourced quote site is not verified. Use it only to find a better source.

For modern cultural references, use official lyrics pages, official scripts, publisher excerpts, rights holder pages, reputable databases, or short clips only as needed to verify exact wording. Keep copyright limits in mind.

## 9. Copyright and length discipline

Do not reproduce long copyrighted material.

For modern songs, films, games, books, and other protected works:

- keep direct quoted fragments short
- prefer paraphrase or title-like allusion
- avoid lyrics except for very short fragments
- avoid long dialogue excerpts
- mark copyright risk clearly
- choose public-domain or historical sources when possible

For public-domain works, still keep quotes concise for UI readability.

If the user requests a long copyrighted passage, do not provide it. Provide a short compliant excerpt, a paraphrase, or a source note instead.

## 10. Audio research purpose

Audio research is needed when a mod feature requires a final music track, cue, loop, sound wrapper, menu track, custom event cue, custom GUI sound, loading music, victory cue, defeat cue, route reveal cue, or other audio asset.

The goal is not to find something that sounds vaguely dramatic. The goal is to find legally usable audio that fits the exact feature role and can be documented.

A complete audio task should identify:

- the final selected audio
- source title
- creator or composer
- performer or recording source if relevant
- source URL or repository source path
- license and usage terms
- duration
- editing or trim notes
- final file path recommendation
- suggested sound definition id or music id when useful
- uncertainty or blockers

## 11. Audio source rules

Before looking outside the repository, check whether the parent identified an approved existing audio folder, track list, manifest, or music documentation file. Do not browse the entire repo unless the parent asks for reuse checks.

Use an existing track only when:

- its source is known
- its license is documented well enough to trust
- its duration and format are known or can be checked
- its tone fits the exact requested role
- reuse is allowed by the parent or repository convention

If no approved suitable track exists, search for audio with clear rights.

Prefer:

- public-domain audio
- Creative Commons audio with compatible terms
- official archive recordings with clear use terms
- government or institutional recordings with clear rights
- user-provided audio with explicit permission
- otherwise clearly licensed audio that permits the intended mod use

Reject:

- generated test tones or oscillator output
- simple beeps, noise beds, and primitive local synthesis used as final music
- tracks that are only sound effects when the task asks for music
- tracks with unclear licensing
- YouTube uploads with no license information
- vague royalty-free claims without usage terms
- modern commercial recordings with unclear rights
- copyrighted film, game, trailer, or album music without permission
- public-domain compositions paired with recordings that are not usable

Composition rights and recording rights are separate. A public-domain composition does not automatically make a modern recording public domain.

## 12. Audio shape and fit

Audio length depends on the feature.

Common shapes:

- short UI cue: a few seconds
- button or alert sound: under a few seconds
- event or presentation cue: roughly 30 seconds to 2 minutes
- menu or loading music: longer tracks or loops
- ambient custom GUI loop: short loop only if the user or repository accepts ambience for that role
- victory or defeat cue: often 30 seconds to 2 minutes

Choose audio by role:

- reveal: clarity, tension, discovery, or a first sign of change
- escalation: pressure, loss of control, momentum, or threat
- defeat aftermath: cost, memory, relief, or uneasy recovery
- ideological victory: ritual, movement, march, anthem, hymn, or public claim
- country formation: proclamation, ceremony, regional identity, or state-building
- custom GUI ambience: quiet enough not to annoy repeated play
- main menu or loading: broad identity of the mod, not one isolated feature

Avoid tracks that sound generally dramatic but do not fit the requested role.

## 13. Audio documentation workflow

For every candidate and final selected track, document:

- title
- creator or composer
- performer or recording source if relevant
- source URL or repository source path
- license
- license confidence
- usage terms
- duration
- source file path if downloaded
- final converted path if conversion was performed
- attribution text if required
- why it fits the feature
- suggested in-game use
- editing notes
- suitability rating
- uncertainty notes

If license, title, creator, source, or duration cannot be identified, mark the track unsuitable or blocked unless the user provides the missing information.

Do not call an audio package complete while source or license is unclear.

## 14. Audio editing and conversion notes

Preserve original downloaded source files when practical.

Possible editing notes:

- trim start
- trim ending
- fade in
- fade out
- loop segment
- lower volume
- raise intro volume
- remove silence
- use only a short opening section
- avoid a loud ending
- normalize volume for UI use

Do not make destructive edits without preserving the source file.

For HOI4 audio, final `.ogg` files commonly need stable sample rate and format. Use repository and vanilla precedents for exact format expectations. When a repository has an existing audio conversion workflow, follow it. If no workflow exists, provide a clear conversion recommendation and mark any uncertainty.

## 15. Audio implementation handoff

The main agent owns final sound wiring. A research handoff should provide enough data to wire without guessing.

Include when useful:

- suggested final `.ogg` path
- suggested source archive path
- suggested music id or sound id
- suggested sound definition id
- suggested volume or trim notes
- suggested loop behavior
- attribution text if required
- documentation row or manifest entry text
- blockers that prevent final wiring

Do not edit sound definitions unless the parent explicitly grants that scope.


## 17. Research note shape

A compact research note should usually include:

```text
# <feature_slug> text and audio research

## Scope
- Feature:
- Requested surface:
- Owner:
- Research question:

## Quote candidates
| Candidate | Source | Confidence | Fit | Risk |
| --- | --- | --- | --- | --- |

## Selected quote
- Text:
- Author or speaker:
- Source:
- Date or period:
- Source URL or path:
- Confidence:
- Copyright or public-domain note:
- Fit note:

## Cultural remark candidates
| Candidate | Source | Type | Risk | Fit |
| --- | --- | --- | --- | --- |

## Selected remark
- Text or allusion:
- Source:
- Type:
- Copyright risk:
- Fit note:

## Audio candidates
| Track | Creator | Source | License | Duration | Fit | Status |
| --- | --- | --- | --- | --- | --- | --- |

## Selected audio
- Title:
- Creator or composer:
- Performer or recording source:
- Source URL or path:
- License:
- Duration:
- Source file:
- Final converted file:
- Suggested id:
- Editing notes:
- Fit note:
- Uncertainty:

## Implementation handoff
- Localisation owner:
- Sound owner:
- Asset owner:
- Documentation owner:
- Blockers:
```

Use only the sections that fit the actual task. Do not create empty research tables for things the feature does not need.

## 18. Completion standard

Sourced quote, remark, or audio research task is complete when the main agent receives:

- selected quote or a clear no-quote recommendation
- selected cultural remark or a clear no-remark recommendation
- selected audio candidate or a clear audio blocker
- source links or repository paths
- attribution confidence
- license and copyright notes
- fit explanation tied to the exact feature role
- final file or conversion handoff when audio was downloaded or processed
- explicit blockers and uncertainty

Do not treat an unverified quote, uncertain audio license, placeholder track, unsourced cultural reference, or missing attribution as complete.
