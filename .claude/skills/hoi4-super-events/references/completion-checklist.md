# HOI4 Super-Events: Completion checklist

Part of the [hoi4-super-events](../SKILL.md) skill. Read before reporting completion of any super-event task.

## 18. Audio validation checklist

Before finishing any super-event task, confirm:

- the final `.wav` exists
- the final `.wav` is game-ready for the HOI4 sound pipeline
- the file is in the correct feature-scoped sound folder
- the selected track is between 1 and 2 minutes long, or the exception is documented
- the base sound definition in the repository sound asset file points to the correct `.wav`
- the required settings-volume soundeffect wrappers point to the base sound and use the helper naming contract
- the super-event points to the correct audio id and uses the repository settings-aware playback helper
- the canonical audio catalog documents every super-event track and shows the super-event ID or IDs using it
- documentation records the source, license, and duration
- documentation records the downloaded source path, final `.wav` path, sound definition id, volume-wrapper ids, and super-event use
- no generated test-tone, oscillator, beep, primitive waveform, or noise-bed cue remains in any completed super-event track
- every completed super-event has a unique final track unless exact reuse was explicitly approved by the user and documented
- no placeholder, default, mismatched, or wrong-format audio remains for completed super-events

## 26. Final checklist

Before closing a super-event task, confirm:

1. The super-event role is clear.
2. The slot is chosen intentionally.
3. Title, description, button text, and quote exist.
4. The repository web research workflow from `AGENTS.md` was used to find and verify real quote candidates.
5. The quote is sourced and not invented.
6. Quote attribution is documented.
7. Button text cultural references are sourced when applicable.
8. Modern copyrighted lyrics, film lines, book lines, or game lines are kept very short.
9. The image direction has been handed to `hoi4-feature-assets`.
10. The super-event image is sourced or generated according to the asset rules.
11. An approved existing track was checked first.
12. If no approved track existed, the repository web research workflow from `AGENTS.md` was used.
13. Audio candidates were researched against the event tone, role, and pacing.
14. Composition rights and recording rights were considered separately.
15. Tracks with unclear licensing were rejected.
16. License or public domain status is documented.
17. Selected audio has title, creator or composer, source, license, duration, usage terms, and suitability notes.
18. The final `.wav` exists in the correct feature-scoped sound folder.
19. The selected track is between 1 and 2 minutes long, or the exception is documented.
20. The base sound definition in the repository sound asset file points to the correct `.wav`.
21. Required settings-volume soundeffect wrappers point to the base sound and follow the helper naming contract.
22. the canonical audio catalog records the final track, source/rights details, and super-event ID or IDs.
23. The audio id is specific to the super-event or intentionally shared and documented.
24. the repository audio-selector variable is set correctly.
25. the repository settings-aware playback helper uses the settings-aware sound helper.
26. Scripted localisation is updated, including `GetSuperEventImage`. otherwise the slot can show default art while the text/audio work.
27. Player-facing localisation is updated.
28. Image wiring is updated.
29. Audio wiring is updated.
30. Audio documentation is updated with source, license, duration, paths, sound definition id, volume-wrapper ids, super-event use, and conversion steps.
31. No placeholder, default, mismatched, or wrong-format audio remains for completed super-events.
32. Event docs are updated.
33. Spreadsheet or event catalog is updated if relevant.
