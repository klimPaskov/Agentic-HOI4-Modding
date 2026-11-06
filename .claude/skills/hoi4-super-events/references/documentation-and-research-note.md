# HOI4 Super-Events: Documentation and research note

Part of the [hoi4-super-events](../SKILL.md) skill. Read before documenting a super-event's audio, event docs or its research note.

## 17. Audio documentation

Always update the repository's canonical audio catalog when one exists. Every final super-event track entry must show the super-event ID using the track. User-approved reuse must list every affected ID and the audio docs must explain why reuse was approved.

Update any additional audio documentation used by the repo.

For each super-event audio package, document:

- title
- creator or composer
- performer or recording source if relevant
- source URL
- license
- license confidence
- usage terms
- duration
- attribution text if required
- downloaded source path
- final `.wav` path
- base sound definition id
- required volume-wrapper soundeffect ids
- super-event id or key using the track
- the canonical audio catalog row with the final track and super-event ID or IDs
- editing or conversion steps
- uncertainties, if any
- why the track fits the super-event tone, role, and pacing

If metadata cannot identify the author, title, source, license, or duration, and the user did not provide it, reject the track or add the missing information to the next batch of questions (Upfront consultation in `CLAUDE.md`) instead of guessing. Ask about track reuse and longer tracks in the upfront consultation, not mid-task.

## 23. Documentation requirements

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
- whether any image is placeholder
- confirmation that audio is final and not placeholder/default

Do not leave the docs saying only "super-event added."

## 24. Manifest or research note

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
- image asset manifest path or permanent asset-provenance/crosswalk note. If the temporary `docs/assets/` manifest was deleted after completion, record the permanent note that replaced its durable facts instead of leaving a broken path.
- audio candidates
- selected audio
- track title
- creator or composer
- performer or recording source if relevant
- source URL
- license
- license confidence
- duration
- attribution text if required
- downloaded source path
- final `.wav` path
- base sound definition id
- required volume-wrapper soundeffect ids
- super-event id or key using the track
- the canonical audio catalog row with the final track and super-event ID or IDs
- editing or conversion steps
- uncertainties, if any
- implementation notes
- open questions

