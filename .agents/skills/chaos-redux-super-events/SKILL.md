---
name: chaos-redux-super-events
description: Use when designing, researching, wiring, or documenting Chaos Redux super-events.
---

# Chaos Redux Super Events

Use this skill when a Chaos Redux task creates, updates, researches, or wires a super-event.

This skill covers super-event presentation, localisation, quote selection, audio research, image handoff, implementation wiring, and documentation.

General event implementation belongs to `chaos-redux-events`.

Visual asset sourcing and processing belongs to `chaos-redux-event-assets`.

## 1. Core purpose

A Chaos Redux super-event is a major presentation moment.

It should mark a major event, major escalation, defeat aftermath, or world-end scenario that deserves stronger treatment than a normal popup.

A super-event package must keep these parts aligned:

- super-event slot
- title localisation
- description localisation
- button text localisation
- quote localisation
- image
- audio id
- audio file
- audio documentation
- event trigger or effect wiring
- settings-aware playback
- event docs
- spreadsheet entry if relevant

Do not wire only one part of a super-event. The image, text, quote, audio, event effect, docs, and spreadsheet must agree.

## 2. When to use this skill

Use this skill for:

- major-event super-events
- evolved minor events that become major enough for super-event treatment
- world-end scenario super-events
- defeat aftermath super-events
- major faction or world-order announcements
- global threat escalation
- large event chain milestones
- super-event quote research
- super-event music research
- super-event audio documentation
- super-event localisation updates
- super-event image handoff to `chaos-redux-event-assets`

Do not use a super-event for every dramatic event. Use it when the campaign moment should feel larger than a normal popup.

## 3. Relationship with other skills

### `chaos-redux-events`

Use `chaos-redux-events` for the full implementation contract:

- event script
- event registration
- event log
- evolutions
- world-end logic
- docs
- spreadsheet updates
- full event system wiring

### `chaos-redux-event-assets`

Use `chaos-redux-event-assets` for:

- super-event image sourcing
- image processing
- PNG previews
- DDS conversion
- `.gfx` sprite wiring
- asset manifests

Super-event images should use internet source images by default unless the event is fictional, symbolic, supernatural, or fully invented.

Super-event images must be marked for user review before final use.

### This skill

This skill owns:

- super-event presentation design
- localisation structure
- quote selection and verification
- audio research and licensing checks
- audio documentation
- super-event package checklist

## 4. Super-event design role

Before wiring a super-event, decide what role it plays.

Common roles:

- first reveal
- escalation
- global response
- faction formation
- world-end scenario
- defeat aftermath
- irreversible political shift
- campaign-ending signal
- rare hidden branch
- ideological victory or collapse

The role should determine the tone, title, image, quote, and audio.

Do not choose a quote, image, or track because it sounds dramatic in isolation. It must fit the exact super-event role.

## 5. Localisation format

Super-event localisation must follow the existing Chaos Redux format.

Example:

```yaml
super_event.1.t: "Undead?"
super_event.1.d: "The dead have risen, spreading terror and chaos.\n\nWitnesses describe scenes of horror as reanimated corpses or \"zombies\" began to terrorize cities and rural areas alike. The outbreak's cause appears to be unknown.\n\nAuthorities are urging the public to remain vigilant and avoid contact with anyone exhibiting unusual behavior."
super_event.1.a: "Do you like to take a yo-yo for a ride?" # Ironic remark
super_event.1.q: "This, then, is how you should pray: 'Our Father in heaven, hallowed be your name.' \n §Y-Matthew 6:9-§!" # An actual quote that fits the situation
```

Required keys:

- `.t` for title
- `.d` for description
- `.a` for button text
- `.q` for quote

Keep the key numbering aligned with the actual super-event slot.

Do not invent a different localisation pattern unless the existing repo pattern has changed.

## 6. Title rules

A good super-event title should be short, memorable, and specific.

It can be:

- direct
- ironic
- ominous
- religious
- political
- military
- bureaucratic
- poetic
- understated

Avoid generic titles such as:

- The End Begins
- World in Flames
- The Final Crisis
- Humanity Falls
- Darkness Rises

Use titles that fit the event's actual identity.

## 7. Description rules

The description should explain the event clearly without turning into a normal event wall of text.

It should:

- give the player enough context
- fit the tone of the event
- avoid overexplaining mechanics
- avoid direct spoilers if the event is meant to remain uncertain
- describe visible consequences or public understanding
- keep uncertainty where the event has not fully revealed itself

For secret or uncertain events, use partial information:

- observers are unsure
- reports conflict
- foreign diplomats avoid clear statements
- intelligence agencies disagree
- governments deny involvement
- regional witnesses give different accounts
- the full meaning is not yet clear

Do not reveal a hidden world-ending branch too early.

## 8. Button text and remark rules

The button text (`.a`) should feel like a reaction to the moment.

It may be:

- ironic
- grim
- understated
- religious
- ideological
- military
- sarcastic
- resigned
- coldly bureaucratic
- a meaningful cultural reference

Button text can use a short cultural reference when it fits the super-event.

Possible sources include:

- songs
- films
- books
- poems
- games
- political slogans
- religious texts
- historical remarks
- internet-era phrases only when the event intentionally fits that tone

Examples of the kind of source that may be considered include Steely Dan lyrics, a line from *The Lord of the Rings*, a film line, or a book line, but only if the reference genuinely fits the event.

Do not choose a reference only because it is recognizable.

Use the configured internet search MCP server from `AGENTS.md` to verify the exact wording and source of any referenced line.

For modern copyrighted songs, films, books, or games, keep the line very short. Prefer a short fragment, a title-like reference, or a paraphrased allusion when a direct quote would be too long.

Avoid generic button text such as:

- OK
- We must act
- This is terrible
- The world will never be the same

The button text should be short enough to fit well in-game.

Document the cultural source in the super-event research note when the button text is a reference.

## 9. Quote rules

The quote (`.q`) should deepen the super-event.

Do not invent quotes.

Do not misattribute quotes.

Do not use a quote unless it fits the specific event.

Use the configured internet search MCP server from `AGENTS.md` to find and verify real quotes.

Prefer quotes that can be checked against a reliable source. Primary sources are best. If a primary source is not available, use reputable quote collections, archives, books, speeches, scripture references, or other traceable sources.

Good quote sources can include:

- public domain literature
- religious texts
- historical speeches
- philosophical works
- political writings
- military memoirs
- legal documents
- poetry
- mythology
- propaganda slogans
- period documents

For the main quote, prefer public domain, historical, religious, literary, philosophical, or political sources when possible.

Avoid:

- invented quotes
- misattributed quotes
- unsourced internet quotes
- quotes that only sound dramatic but do not fit the event
- quotes with uncertain attribution unless clearly marked
- long copyrighted song lyrics, film dialogue, book dialogue, or game dialogue

Modern songs, films, books, and games are better suited for the button text or remark (`.a`) than the main quote (`.q`).

If a modern cultural line is used as the main quote anyway, it must be very short, clearly sourced, and marked for user review.

If attribution is uncertain, mark it uncertain or choose another quote.

## 10. Quote research workflow

Use the configured internet search MCP server from `AGENTS.md` for quote research.

Search for quotes by combining the event's core themes with terms such as:

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

Do not stop at the first quote that sounds good. Find several candidates, compare them, and select the one that best fits the exact super-event role.

For every proposed quote, document:

- quote text
- speaker or author
- source work, speech, book, scripture, or document
- year or approximate period if known
- source link
- why it fits the super-event
- attribution confidence
- notes about uncertainty
- whether the quote is public domain, copyrighted, or unclear when this can be determined

Use direct quotes sparingly and keep them short enough for the super-event UI.

If the quote is too long, use a shorter excerpt.

Do not alter a quote in a way that changes its meaning.

If a translation is used, state that it is a translation when relevant.

If no strong quote is found, continue searching instead of inventing one.

## 10.1 Cultural remark research workflow

The button text (`.a`) can be a meaningful remark or cultural reference.

This is separate from the main quote (`.q`).

Use the configured internet search MCP server from `AGENTS.md` to find and verify cultural references.

Good cultural remark sources can include:

- song lines or titles
- film lines
- book lines
- play lines
- game lines
- well-known slogans
- religious or mythological phrases
- political or military catchphrases

The remark should fit the super-event's tone. It can be ironic, grim, darkly funny, understated, reverent, fatalistic, or bitter.

For modern copyrighted works, keep the direct quote very short. Prefer brief fragments, paraphrased allusions, or title-like references when possible.

For every cultural remark candidate, document:

- remark text
- source work or artist
- author, songwriter, filmmaker, or writer if relevant
- year if known
- source link
- why it fits the super-event
- whether it is a direct quote, short fragment, title reference, or paraphrase
- whether it needs user review

Do not invent a cultural reference.

Do not misquote a line if presenting it as a direct reference.

Do not use a reference that breaks the tone of the event unless the contrast is intentional.

## 11. Quote style by super-event type

### First reveal

Use quotes about discovery, doubt, fear, false peace, hidden rot, or the first sign of collapse.

### Escalation

Use quotes about loss of control, failed containment, pride, punishment, betrayal, war, disease, or mass panic.

### World-end scenario

Use quotes about final judgment, collapse, extinction, fate, prophecy, silence, ruin, or the end of order.

### Defeat aftermath

Use quotes about memory, cost, survival, rebuilding, responsibility, or vigilance.

### Ideological victory or transformation

Use quotes about faith, revolution, obedience, sacrifice, destiny, legitimacy, power, or rebirth.

### Scientific or experimental disaster

Use quotes about knowledge, arrogance, forbidden inquiry, unintended consequences, or the limits of control.

## 12. Audio research purpose

Super-event audio should make the moment feel distinct.

Each super-event should have a unique audio id.

When the final track is not ready, copy an existing audio file as a placeholder so the game can run, but document that it is a placeholder.

The final music should be chosen intentionally.

## 13. Audio research rules

For each proposed track, document:

- title
- composer
- performer or recording source if relevant
- composition public domain status
- recording license status
- source link
- why it fits the super-event
- suggested in-game use
- editing notes
- suitability rating
- uncertainty notes

Check composition rights and recording rights separately.

A public domain composition does not automatically make a recording public domain.

Prefer:

- public domain compositions
- public domain recordings
- clearly licensed recordings
- official archive recordings with clear rights
- government or institutional recordings with clear use status
- user-provided audio with permission

Avoid:

- modern commercial recordings with unclear rights
- YouTube uploads with no license information
- unclear "royalty free" claims
- copyrighted film, game, or trailer music
- tracks where the composition is public domain but the recording is not usable

If the license is unclear, mark it as uncertain or unsuitable and find another option.

Do not claim a track is public domain without checking.

## 14. Audio editing notes

For every suitable track, propose practical editing notes.

Possible notes:

- trim start
- trim ending
- fade in
- fade out
- loop segment
- lower volume
- raise intro volume
- remove silence
- use only first 30 seconds
- use quiet opening only
- avoid loud ending
- match super-event duration

Do not perform destructive edits without preserving the original source file.

Document any edited derivative file.

## 15. Audio implementation expectations

When implementing audio, follow the existing Chaos Redux audio pattern.

The implementation should keep these aligned:

- audio file
- audio id
- `global.current_super_event_audio_id`
- settings-aware playback helper
- super-event slot
- localisation
- documentation

Every super-event must have a unique audio id.

Use the settings-aware playback helper rather than bypassing it.

If the final audio is not available, use a copied existing audio as a placeholder only when the implementation needs a playable file. Mark it clearly as placeholder in docs.

## 16. Audio documentation

Update the music or audio documentation used by the repo.

If the repository uses `.html` documentation for music files, update it.

Document:

- in-game audio id
- file path
- title
- composer
- performer or recording source if relevant
- source link
- license or public domain status
- whether the file is placeholder or final
- editing notes
- super-event slot or event id
- why the track fits

If metadata cannot identify the author, title, or source, and the user did not provide it, ask the user for the missing information instead of guessing.

## 17. Super-event image handoff

Super-event images are handled through `chaos-redux-event-assets`.

Default rule:

- use internet source images for super-event images
- do not generate them with `image_gen` unless the user explicitly asks for fictional, symbolic, supernatural, or fully invented super-event art
- mark super-event images as `needs_user_review` before final use

The super-event skill should define the image direction:

- subject
- tone
- composition need
- symbolism
- source-image search direction
- what to avoid
- why the image fits the super-event

The asset skill handles:

- source search
- source documentation
- image processing
- PNG preview
- DDS conversion
- `.gfx` wiring
- manifest

## 18. Super-event slot wiring

When wiring a super-event, choose the slot intentionally.

Make sure the implementation:

1. sets the correct visibility flag
2. sets `global.current_super_event_audio_id`
3. uses the settings-aware playback helper
4. updates scripted localisation
5. updates player-facing localisation
6. updates image wiring in the correct `.gfx` file
7. updates audio wiring
8. updates docs
9. updates spreadsheet or event catalog if relevant

Do not reuse a slot accidentally.

Do not let two unrelated super-events point to the same current image, text, or audio unless the reuse is intentional and documented.

## 19. World-end super-events

World-end super-events need stricter alignment.

When a super-event represents a world-end scenario:

- guard the branch with the world-end rules from `chaos-redux-events`
- make the terminal state clear
- set the scenario-specific global flag
- set the matching super-event visibility
- stop or gate incompatible future systems and branches
- make the event log, docs, and spreadsheet agree
- choose quote and audio with finality in mind

A world-end super-event should feel like an end-state, not a normal escalation.

## 20. Defeat aftermath super-events

Use defeat aftermath super-events only when the defeated threat was global or near-global, long enough, and costly enough to reshape the campaign.

The super-event should communicate:

- what was defeated
- what the world lost
- what remains unstable
- what new order or memory follows
- why the campaign does not simply return to normal

Quotes and music should usually feel reflective, not triumphant without cost.

## 21. Documentation requirements

The event documentation should explain:

- which super-event exists
- when it fires
- what branch or evolution triggers it
- what slot it uses
- what image it uses
- what audio id it uses
- what quote it uses
- what source the quote came from
- what audio source is used
- whether any image or audio is placeholder
- whether user review is still needed

Do not leave the docs saying only "super-event added."

## 22. Manifest or research note

For every super-event research package, create or update a markdown note.

Recommended path:

```text
docs/super_events/<event_id>_<event_slug>_super_event_research.md
```

The note should include:

- event id
- event slug
- super-event role
- title
- description
- button text
- button text source or cultural reference if applicable
- button text source link if applicable
- quote candidates
- selected quote
- quote source and confidence
- image direction
- image asset manifest path
- audio candidates
- selected audio
- audio source and license notes
- implementation notes
- open questions
- user review status

## 23. Final checklist

Before closing a super-event task, confirm:

1. The super-event role is clear.
2. The slot is chosen intentionally.
3. Title, description, button text, and quote exist.
4. The configured internet search MCP server was used to find and verify real quote candidates.
5. The quote is sourced and not invented.
6. Quote attribution is documented.
7. Button text cultural references are sourced when applicable.
8. Modern copyrighted lyrics, film lines, book lines, or game lines are kept very short and marked for user review when needed.
9. The image direction has been handed to `chaos-redux-event-assets`.
10. The super-event image is sourced or generated according to the asset rules.
11. Super-event image review status is recorded.
12. Audio candidates were researched.
13. Composition rights and recording rights were considered separately.
14. License or public domain status is documented.
15. Selected audio has title, composer, source, and suitability notes.
16. Placeholder audio is clearly marked if used.
17. The audio id is unique.
18. `global.current_super_event_audio_id` is set correctly.
19. Settings-aware playback is used.
20. Scripted localisation is updated.
21. Player-facing localisation is updated.
22. Image wiring is updated.
23. Audio wiring is updated.
24. Music or audio documentation is updated.
25. Event docs are updated.
26. Spreadsheet or event catalog is updated if relevant.