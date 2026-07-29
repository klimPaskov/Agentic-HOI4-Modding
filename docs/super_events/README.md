# Super Events package

This folder documents the optional reusable Super Events runtime installed by
HOI4 Mod Setup. The package stays absent unless the user selects the Super
Events workflow.

The installed runtime uses the confirmed project namespace in every scripted
identifier. Its filenames remain stable so updates can compare installed,
local, and incoming content safely.

The base DDS and PSD files were copied, at the maintainer’s direction, from
the tracked Chaos Redux versions at commit
`41044613ad6711dc39d9b7d0f12ac7100766b752`. No separate license declaration
was present in that repository during this update, so this note records
lineage without making an unsupported rights claim.

## Included runtime

- `interface/hoi4ms_super_events.gui`
- `interface/hoi4ms_super_events.gfx`
- `common/scripted_guis/hoi4ms_super_events.txt`
- `common/scripted_effects/hoi4ms_super_events.txt`
- `common/scripted_localisation/hoi4ms_super_events.txt`
- `events/hoi4ms_super_event_examples.txt`
- `localisation/english/hoi4ms_super_events_l_english.yml`
- `gfx/super_events/` background, default preview, example image, and editable Photoshop templates
- `gfx/interface/super_event_option.dds`
- `.agents/skills/hoi4-super-events/assets/examples/` composition references and contact sheet

## Smoke test

Start HOI4 with `-debug`, load the mod, open the console, and run:

```text
event <mod_prefix>_super_event.1
```

The hidden example event opens the default Super Event. Closing it clears the
visibility flag and current registration value.

## Register another Super Event

1. Reserve a new integer ID in the project’s permanent Super Events registry.
2. Add one sprite to `interface/hoi4ms_super_events.gfx`.
3. Add matching ID branches to all four `defined_text` blocks in
   `common/scripted_localisation/hoi4ms_super_events.txt`.
4. Add title, description, quote, and response localisation.
5. Add a caller that invokes `<mod_prefix>_show_super_event` with the reserved
   ID.
6. Research and document the image, quote, remark, and optional audio with the
   installed `hoi4-super-events` and `hoi4-text-audio-research` skills.
7. Validate the GUI, GFX, scripted localisation, caller, assets, and close
   cleanup as one package.

Never reuse an ID for a different moment. Keep audio optional until a track has
verified source and usage rights; a missing track must not break the visual
Super Event.
