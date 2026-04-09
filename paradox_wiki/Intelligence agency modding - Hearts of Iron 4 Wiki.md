# Table of contents

- [Agency file](#agency-file)
- [GFX](#gfx)
- [References](#references)


---

Cosmetically, country-specific intelligence agencies are used in mods only as a localisation and graphical interface, but this guide can also be used on creating generic intelligence agencies.

## Agency file

Intelligence agencies' cosmetics are defined and toggled for countries in it's respective definition in the agencies file, in <yourmod>/common/intelligence\_agencies. By default, this is the 00\_intelligence\_agencies.txt file. It is not recommended to overwrite the vanilla file, and instead to create a new one, for readability and to allow your mod to work better with future updates, DLCs, and other mods. An example for an intelligence agency definition is as follows:

```text
intelligence_agency = {
    picture = GFX_intelligence_agency_NOR_old_norse
    names = { "Hugin" "Munin" }
    
    default = {
        tag = NOR
    }
    available = {
        original_tag = NOR
    }
}
```

The names definition can list either hardcoded strings or localisation scopes (Vanilla files are typically hardcoded). They list out all the possible, random, names that can be given to the intelligence agency. These names are used when you call [create\_intelligence\_agency](<Effect - Hearts of Iron 4 Wiki.md#create-intelligence-agency>), unless another name is provided in the effect. In this example, either Hugin or Munin are used as the intelligence agency name, which is randomly picked when the effect is called.

The default definition contains the trigger for the intelligence agency to be the default choice of any nation. For example, when you choose to create an intelligence agency when playing as the United Kingdom, it defaults with the MI6 icon and either 'SIS' or 'MI6' as it's title, which you can then edit from there.

The available definition contains the trigger for the intelligence agency to be a choice you can make when creating it manually. This only works with the icon, due to how the intelligence agency system works. For example, if you wanted to create a new generic intelligence agency icon, you could define it like so:

```text
intelligence_agency = {
    picture = GFX_intelligence_agency_mod_generic_1
    names = { "Svalbard Intelligence Group" } # This would not appear, but it's safer to have a name for it anyway.
    
    default = {
        always = yes # It's then in the random queue with the rest of the generic intelligence agencies. 'Rooke' is typically priority.
    }
    available = {
        always = yes
    }
}
```

Despite it being only a new icon, you must give it at least one possible name, or else the definition won't be valid.

## GFX

The GFX for the intelligence agencies is slightly more complicated than the standard icon; when you select an intelligence agencies' icon, the selection effect is **not automatically generated**. This means that you must create two frames when defining your icon in a .gfx file, an example of such is as follows:

```text
spriteType = {
    name = "GFX_intelligence_agency_NOR_old_norse"
    textureFile = "gfx/interface/operatives/agencies/agency_logo_NOR_old_norse.dds"
    noOfFrames = 2 # This means it is cut along the X axis 2 times.
}
```

The noOfFrames property means the number of times the sprite icon is split along the X axis, in this case: twice. In terms of intelligence agencies, you do not need to do more than define noOfFrames and to create both your frames for your sprite icon.

The image size of an intelligence agency logo is **234px** by **119px** (x by y). This means the mid-point between your two icon frames should be at 117 pixels along the X axis. The frame on the left should be your unedited, actual intelligence agency icon. The frame on the right should be your icon when it is selected in the intelligence agency creation screen. In vanilla, this means a 2-pixel thick stroke/border with a gradient from white down to the main colour of your agency, and a strong, quickly-fading drop shadow. Once you are sure this is all correct, your GFX definition should be as well.

By default, .gfx files for intelligence agencies are stored in interface/countryintelligenceagencyview.gfx, and the sprite icons are stored in gfx/interface/operatives/agencies.

## References

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
