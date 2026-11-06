# HOI4 Super-Events: Audio implementation

Part of the [hoi4-super-events](../SKILL.md) skill. Read before downloading, converting, editing or wiring a super-event track and its sound definitions.

## 14. Audio implementation workflow

For every super-event audio package:

1. Select the track after repository and internet-source checks.
2. Verify the track title, creator or composer, source, license, duration, and usage terms.
3. Download the selected audio from its legitimate source.
4. Preserve the downloaded source file under the temporary feature-scoped `docs/assets/<feature_slug>/` source-audio path when practical. Before the feature is fully complete, promote durable source, license, attribution, and conversion facts into permanent audio documentation, verify that no runtime reference points into `docs/assets/`, and delete the feature-scoped workspace. Keep it for blocked or incomplete work.
5. Convert the final cue to a game-ready `.wav`.
6. Place the final `.wav` in the repository's established feature-scoped sound folder with a stable, unique basename.
7. Add or update the base `sound` definition in the repository's sound asset file so it points to the final WAV and has a unique sound definition id.
8. Add or update settings-volume `soundeffect` wrappers when the repository uses them. Each wrapper must point to the base sound and follow the existing `max_audible`, behavior, and naming pattern.
9. Route playback through the repository's verified settings-aware helper when one exists; otherwise mirror the closest installed vanilla sound-playback precedent and document the contract.
10. Update the relevant feature documentation and canonical audio catalog when one exists. Every final cue entry must list the super-event id, track identity, and source/rights details. If user-approved reuse exists, document every id and the approval.
11. Verify the final file paths, sound definitions, volume wrappers, ids, helper call, and docs before calling the super-event complete.

Use the existing repository settings-aware sound helper when one exists. Do not bypass a repository-owned volume or settings contract.

## 15. Audio editing notes

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

## 16. Audio implementation expectations

When implementing audio, follow the existing repository audio pattern and the closest installed vanilla precedent.

The implementation should keep these aligned:

- final sound file
- base sound definition
- required volume-wrapper soundeffects
- audio id
- the repository audio-selector variable
- settings-aware sound helper
- super-event slot
- localisation
- documentation

Every super-event must have a specific audio id and a unique final track. Shared audio ids or shared tracks are allowed only when the user explicitly approved the exact reuse.

Use the repository's settings-aware playback helper rather than bypassing it.

Fallbacks are not allowed without discussing them with the user. If final audio is unavailable, stop and explain the blocker instead of silently leaving default or placeholder audio.

