Portraits used by random country leaders and military leaders are specified in /Hearts of Iron IV/portraits. It is necessary to specify the files in /Hearts of Iron IV/interface/\_random\_portraits.gfx, otherwise the game will not display the images.

# Portraits

Portraits are used to assign a pool of images to specific groups of countries, or a specific country that will then be used when the player generates a military leader or through an effect their country leader or military leader is replaced.

It follows this format:

```text
default = {
    # ...
}
continent = {
    name = <continent>
    # ...
}
<tag> = {
    # ...
}
```

**default** is the fallback portraits used when no other definition matches the current scope.

**continent** defines the portraits per continent, meaning they apply to any nation with their capital in the specified continent.

**tag** defines the portraits for the specified tag, overriding the **continent** definition if it also matches one.

The actual portrait definitions are as follows:

```text
male = {
    <path>
}
female = {
    <path>
}
    
army = {
    male = {
        <path>
    }
    female = {
        <path>
    }
}
navy = {
    male = {
        <path>
    }
    female = {
        <path>
    }
}
political = {
    <ideology> = {
        male = {
            <path>
        }
        female = {
            <path>
        }
    }
}
```

Multiple paths can be used to add a pool of portraits to each definition.

The top **male** and **female** paths may be used for any type of leader.

The **army** paths are used for Field Marshals and Corps Commanders.

The **navy** paths are used for Naval Commanders.

The **political** paths are used for country leaders of the specified ideologies.

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
