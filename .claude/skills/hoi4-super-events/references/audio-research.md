# HOI4 Super-Events: Audio research

Part of the [hoi4-super-events](../SKILL.md) skill. Read before searching for, evaluating or rejecting a super-event track.

## 12. Audio research purpose

Super-event audio should make the moment feel distinct.

Register the final super-event cue as sound and play it through the settings-aware sound helper.

Core rule: a super-event task is not complete unless its audio is selected, verified, converted to a game-ready WAV, registered, wired, and documented.

Every super-event implementation must include complete sound wiring. Do not leave a completed super-event on default, placeholder, mismatched, wrong-format, or undocumented audio.

Every super-event must have its own unique final track, unique audio id, and unique sound registration unless the user explicitly approves a specific reuse before implementation. Do not reuse another super-event's track just because the moments are related.

The final cue should be an intentional musical recording by default, such as a chant, hymn, orchestral excerpt, song, march, or other track with musical structure. Do not use pure sound effects, drones, pulses, room tone, one-shot stingers, abstract ambience, or texture beds for a super-event unless the user explicitly asks for non-musical audio and the exception is documented.

Never create or accept a super-event track from generated test tones, primitive waveforms, signal-generator output, metronome clicks, generated beeps, simple oscillator layers, noise beds, or quick local synthesis. This includes sine, square, triangle, sawtooth, and similar waveforms, even when mixed with noise or effects. If no real licensed track is available, stop and report the blocker instead of manufacturing a cue.

Never describe a final cue with placeholder provenance such as "restored legacy", "legacy audio package", "repository history", or similar implementation-history wording in player-facing or attribution documentation. The repository's canonical audio catalog, when present, and the audio docs must name the actual source title, creator or composer, performer or recording source when known, source URL, license, and duration. Use attribution status `verified` only after the identity and source/license have been checked.

The final cue should be chosen intentionally.

## 13. Audio research rules

Before looking outside the repository, check whether an approved suitable track already exists in the repo. Inspect:

- existing `sound/*.wav`
- the repository sound asset file
- the repository's canonical audio catalog, if one exists
- existing docs or manifests that identify source and license

Use an existing track only when its source, license, duration, and intended use are already documented well enough to trust, and when its tone fits the specific super-event role and pacing.

If no approved suitable track exists, search the internet using the repository web research workflow from `AGENTS.md`. Do not use unapproved web browsing tools for this repo.

Find audio that fits the exact super-event tone, role, and pacing. Prefer tracks between 1 and 2 minutes long. If a better track falls outside that range, document the exception before use and trim the final in-game file to 2 minutes or less unless the user explicitly approves a longer final track.

Prefer:

- public domain audio
- Creative Commons audio
- government or institutional recordings with clear use terms
- official archive recordings with clear rights
- user-provided audio with explicit permission
- otherwise clearly licensed audio that permits the intended mod use

Reject:

- generated test-tone or oscillator audio, including sine, square, triangle, sawtooth, beep, pulse, and noise-bed cues
- tracks that are primarily sound effects, drones, stingers, loops, abstract ambience, or texture beds when the request is for a structured musical cue
- tracks with unclear licensing
- YouTube uploads with no license information
- vague "royalty free" claims without usage terms
- modern commercial recordings with unclear rights
- copyrighted film, game, trailer, or album recordings without clear permission
- tracks where the composition is public domain but the recording is not usable

For each candidate and final selected track, verify and document:

- title
- creator or composer
- performer or recording source if relevant
- source URL
- license
- license confidence
- duration
- usage terms
- attribution text if required
- source link
- why it fits the super-event
- suggested in-game use
- editing notes
- suitability rating
- uncertainty notes

Check composition rights and recording rights separately.

A public domain composition does not automatically make a recording public domain.

If the license is unclear, mark it unsuitable and find another option. Do not wire uncertain audio into a completed super-event.

Do not claim a track is public domain without checking.

