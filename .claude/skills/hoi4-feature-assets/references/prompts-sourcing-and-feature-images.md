# HOI4 Feature Assets: Prompts, sourcing and feature images

Part of the [hoi4-feature-assets](../SKILL.md) skill. Read before writing an image-generation prompt, sourcing an internet image, making report, news or large presentation images or flags, or sourcing music for a presentation.

## 11. Image generation prompt rules

Every image-generation prompt should be specific enough to produce usable game art. `hoi4-imagegen` adds the family's rules (canvas, transparency, no frame or text) itself, so the brief states the subject, mood and what to avoid.

A good prompt should include:

- asset type
- target in-game use
- subject
- visual style
- readability requirements
- what must be avoided
- whether the result must be readable at small size

Do not ask for vague "cool icon" style outputs.

Do not rely on text inside generated images. Generated text is unreliable.

Prefer strong symbols, clear silhouettes, and readable composition.

For transparent icon prompts, explicitly request a transparent canvas, no fake checkerboard, no white rim, no white/colored outline, no glow, no sticker border, no opaque square background, and a clean silhouette suitable for HOI4 UI.

## 12. Internet source image rules

When using internet source images:

1. Search for images that fit the event tone, target use, and intended era.
2. For Second World War-era event assets, search for source images from roughly 1936 to 1945 unless the feature spec gives a narrower date range.
3. Prefer contemporary or near-contemporary public domain, archival, official, museum, library, newspaper, map, press photograph, propaganda poster, government record, military record, period illustration, or clearly licensed sources.
4. Reject modern photographs, reenactments, film stills, postwar streets, uniforms, props, weapons, vehicles, buildings, AI-looking reconstructions, and later stylized images when they do not fit the era.
5. Record source links, source date or estimated date range, and license or public domain status when available.
6. If licensing, date, or era fit is unclear, mark it as uncertain in the manifest.
7. Process the image into the correct HOI4 size and style.
8. Preserve the source image path and processed preview path.

For public-facing or uncertain assets, keep the manifest honest about the source status, date uncertainty, and Second World War-era fit uncertainty.

## 13. Report event images

Read [`references/event-images-and-flags.md`](event-images-and-flags.md) whenever a task creates report or news event images or flags. It contains the complete standard for this section and its subsections.

## 14. News event images

News event images may use internet-sourced imagery or generated period-news imagery. Prefer generated news images when the event needs a unique fictional or alternate-history scene, invented crisis, or scene that is unlikely to exist in archives. Use real sources when the image must depict a real person, real historical scene, or real archival item.

News images should look like black-and-white documentary photographs or period news illustrations.

For Second World War-era subjects, prefer contemporary newspapers, news photographs, war correspondents' photographs, press agency images, propaganda posters, maps, official visual records, military archive images, museum or library scans, or period illustrations. Do not use modern reenactment photos, modern news photos, film stills, or later images that do not fit the era.

Use:

- old news photograph or period press illustration style
- Second World War-era visual fit when the feature belongs to that era
- clear central subject
- strong contrast
- period-appropriate composition
- no modern UI overlays
- no modern clothing, streets, weapons, vehicles, buildings, or props unless they are intentionally part of the event
- no generated text

Target size:

```text
397x153
```

News images must be black and white.

Generated news images must be converted to black and white during processing, with period press contrast/grain and no modern color remnants. Record the source link and license or public domain status for internet-sourced images, or the generation prompt and source-mode rationale for generated images.

## 15. Large feature presentation images

Large feature presentation images may use internet-sourced imagery or generated art. Prefer generated custom feature images for fictional, alternate-history, symbolic, supernatural, extreme-route, or emotionally specific moments where a unique composed image better fits the feature role. Use internet sources when the image must depict a real historical person, real photographed event, or real archival artifact.

Large feature presentation images should have:

- strong central composition
- clear dramatic theme
- readable subject
- enough contrast for HOI4 UI
- Second World War-era visual fit when the feature belongs to that era
- no generated text
- no modern clothing, streets, weapons, vehicles, buildings, props, film stills, or reenactment imagery when they do not fit the era
- no cluttered small details that disappear at final size

Target size:

Use the exact target size required by the repository UI surface, image slot, or parent prompt. Do not assume a fixed custom-presentation size when the repository has no matching surface.

If sourced quote, remark, or audio research needs music, use `hoi4-text-audio-research` and research suitable public domain or clearly licensed music. Use feature-scoped paths such as `music/<feature_slug>/` and `sound/<feature_slug>/` only when the repository uses that convention or the parent requests it. Never create final music or audio from generated test tones, primitive waveforms, beeps, noise beds, or local oscillator output; that includes sine, square, triangle, and sawtooth waveforms.

For each track, document:

- title
- composer
- performer or recording source if relevant
- public domain status or license status
- source link
- why it fits
- suggested in-game use
- editing notes

Do not claim public domain status without checking.

If the license is unclear, mark it as uncertain or unsuitable.

## 20. Flags

Read [`references/event-images-and-flags.md`](event-images-and-flags.md) whenever a task creates report or news event images or flags. It contains the complete standard for this section and its subsections.

