# Table of contents

- [Window assignment](#window-assignment)
- [Parent window](#parent-window)
- [Context](#context)
- [Dirty](#dirty)
- [Visible](#visible)
- [Effects](#effects)
- [Triggers](#triggers)
  - [Temporary variable usage](#temporary-variable-usage)
- [Dynamic Lists](#dynamic-lists)
- [Properties](#properties)
- [AI](#ai)
  - [AI enabled](#ai-enabled)
  - [AI Test Attributes](#ai-test-attributes)
  - [AI Check](#ai-check)
  - [AI Test Scopes](#ai-test-scopes)
  - [AI Check Scope](#ai-check-scope)
  - [AI Weights](#ai-weights)
  - [AI Parents](#ai-parents)
- [Template](#template)
- [Scripted Localization](#scripted-localization)
- [Tips](#tips)
- [See also](#see-also)


---

Scripted GUIs are used to assign scripted functionality to newly-created elements in the user interface, allowing it to modify the game's state or change depending on conditions.

Scripted GUIs are defined as /Hearts of Iron IV/common/scripted\_guis/\*.txt files. The folder name must be in plural. The scripted GUI will assign functionality to user interface elements, which themselves are defined in /Hearts of Iron IV/interface/\*.gui files.

Most commonly, flags, variables, and arrays are used in the implementation of GUI. For example, implementing a button that opens up a window is most commonly done by assigning a flag to be set on the button press and making the window visibility depend on the flag being set on the country.

A scripted GUI is defined as a block within a `scripted_gui = { ... }` container, where the name of the block determines the internal ID of the scripted GUI.

## Window assignment

*See also: [Interface modding](<Interface modding - Hearts of Iron 4 Wiki.md>)*

Scripted GUIs are assigned to `containerWindowType`s and apply to every interface element located within them. This is done with `window_name = example_container`.

In order for a container to be a valid target for scripted GUI, it must be entirely independent, not present in any other container window. For example, in the following code in an /Hearts of Iron IV/interface/\*.gui file, only `independent_container` can be assigned:

```text
guiTypes = {
    containerWindowType = {
        name = "independent_container" # Can be used in the window_name of scripted GUI
        position = { x = 0 y = 0 }
        size = { width = 100% height= 210 }
        
        containerWindowType = {
            name = "nested_container" # Located inside of another container, thus impossible to assign scripted GUI
            position = { x = 0 y = 0 }
            size = { width = 100 height= 100 }
        }
    }
}
```

The scripted GUI will affect every single element located inside of the container window, even if they're present in a further-nested container.

Most commonly, the containers used by scripted GUI are defined inside of fully separate interface files to ensure no overlap.

## Parent window

By default, a newly-created container window will show up on top of most other UI elements. Assigning a parent window is done in order to make the UI be attached to a particular container. This makes the container window only visible when the parent window is visible, assigns the drawing order to be directly on top of the parent's elements, and makes the container follow the animations done by the parent.

There are two ways to do so in particular:

- `parent_window_token = top_bar` will attach to a particular base game window identified by its token.
- `parent_window_name = container_name` will attach it to a container which has the specified name.

- **top_bar**

For `parent_window_token`, a notable argument is `top_bar`. The topbar is positioned lower in the drawing order than most pop-up menus in the game. Therefore, assigning a scripted GUI to have a parent of the topbar will make it be hidden by menus such as the national focus selection or the politics tab. As the topbar container actually covers the entire screen, using it as the token will not result in the container being clipped off.

`parent_window_name = example_container` can be used with most containers. If the parent container is itself independent, then directly entering the name of the container will result in the scripted GUI's window be attached to it.  
If the parent container is nested inside another one, then it's necessary to append \_instance. As such, a nested container with `name = "nested_container"` can be assigned as a parent with `parent_window_name = nested_container_instance`. This can also be used to place the scripted GUI lower in the drawing order. For example, to create a custom dynamic background for a base game's UI window, it's possible to create an "anchor" container window inside of it and then use it as the parent window:

```text
guiTypes = {
    containerWindowType = {
        name = "countrypoliticsview"
        position = { x=-606 y=78}
        size = { width=550 height=100%% }
        
        <...>    
        
        iconType ={
            name ="pol_view_bg"
            spriteType = "GFX_pol_view_bg"
            position = { x= 0 y = 44 }
            Orientation = "UPPER_LEFT"
        }    
        
        containerWindowType = { # This container will be placed right above the background of the political view and below each of its elements
            name = "politics_anchor" # The scripted GUI will have parent_window_name = politics_anchor_instance
            position = { x = 0 y = 44 } # This will ensure that, for example, national spirits will be placed above the scripted GUI and not get hidden.
            size = { width = 100% height = 100% }
        }
        
        <...>
    }
}
```

`parent_window_name` is unable to accept container windows that are used by a gridboxType.

## Context

The context determines the information about the game state that is available to the scripted GUI to read or modify. This is determined with `context_type = player_context` in the scripted GUI. If unset, no information will be given to the UI, making it impossible to have it have any effect or be dynamic, including in localisation. Assigning any context type will make it possible to use the scripted GUI to modify the game's state, in part using any effects and [triggers](<Triggers - Hearts of Iron 4 Wiki.md>), including [scopes](<Scopes - Hearts of Iron 4 Wiki.md>).

In each of the options, [ROOT](<Scopes - Hearts of Iron 4 Wiki.md#root>) always corresponds to the country that sees the scripted GUI (or "player country", which may be controlled by AI). However, the default scope depends on the context.

- **player_context**
  - Description: The baseline context. The default scope is the player country, which is also always ROOT in every context.

- **selected_country_context**
  - Description: The default scope is the currently-selected country. The scripted GUI will not appear if no country is selected. AI evaluates this for every other country, unless otherwise restricted.

- **selected_state_context**
  - Description: The default scope is the currently-selected state. The scripted GUI will not appear if no state is selected. AI evaluates this for every state, unless otherwise restricted.

- **decision_category**
  - Description:
    ```text
    Allows the GUI to read a decision category as context in order to embed itself in its description.
    Necessary to attach the scripted GUI to a decision category with the
    scripted_gui
    attribute in the category.
    The scripted GUI shouldn't have any parent window. Temporary data strcuture usage may not always work correctly with this context type.
    ```

- **diplomatic_action**
  - Description:
    ```text
    Allows the GUI to read a scripted diplomatic action as context in order to be sent to the target upon its selection. Necessary to attach the scripted GUI to a scripted diplomatic action in a
    /Hearts of Iron IV/common/scripted_diplomatic_actions/*.txt
    file.
    ```

- **national_focus_context**
  - Description: Gui will be attached to a national focus view for the targeted country, the country which owns the national focus view

- **country_mapicon**
  - Description: The GUI will show up next to every country when viewing the world map. The default scope is the country that it appears on.

- **state_mapicon**
  - Description: The GUI will show up next to every state when viewing the world map. The default scope is the state that it appears on.

If the default scope differs from ROOT, then PREV is useful to refer to it with further scoping.

## Dirty

Defines when the scripted GUI should be updated; by default guis are updated every tick. For large GUIs, this can make them quite performance heavy; as such it's recommended to use a [dirty](https://en.wikipedia.org/wiki/Dirty_bit)[variable](<Data structures - Hearts of Iron 4 Wiki.md#variables>) to tell the game when to update a GUI instead of having them be updated constantly. If you do, the GUI will only update when the variable's value changes. Note that this only applies to updating the properties of the GUI, but not to the GUI itself's visibility. Dirty variables can be declared like such:

```text
dirty = example_variable
```

## Visible

Defines when the scripted GUI is visible for the current scope.

Note that the scripted GUI has to be visible for the AI if it is to use it.

## Effects

Defines what effects should be attached to button elements within the interface. **<element>** should be the name of the element.

There are additional modifiers added before the **click** suffix that alter the type of click recognized. These are fairly obvious to understand, and can be chained.

Modifiers:

- right
- alt
- control
- shift

For example: `my_button_alt_right_click = { }`

## Triggers

Defines when interface elements are usable or visible. By default elements are clickable and visible. Note that this allows the manipulation of single elements without affecting the overall parent window.

`<element>_<modifiers>_click_enabled` evaluates when the specified element should be clickable.

Note that `<element>_click_enabled` overrides the specific triggers such as `<element>_right_click_enabled`.

`<element>_visible` evaluates when the specified element should be visible. This can be used for any interface element, such as icons and text.

Note that if an element is not visible, the AI will be unable to click on it as well.

### Temporary variable usage

In addition to determining when an element is clickable or visible, the `triggers` block of a Scripted GUI can also have temporary variables (as well as temporary arrays) set inside of an `<element>_<trigger>` block and those temporary data structures can be used in both the `properties` and `dynamic_lists` section of a Scripted GUI.

Here is an example of this concept in action:

```text
triggers = {
	my_temp_array_calculator_click_enabled = {
		clear_temp_array = my_temp_array
		all_of = {
			array = my_array
			add_to_temp_array = { my_temp_array = v }
		}
	}

	my_element_click_enabled = {
		if = {
			limit = {
				has_completed_focus = my_focus
			}
			set_temp_variable = { my_temp_var = 1 }
		}
		else = {
			set_temp_variable = { my_temp_var = 2 }
		}
	}
}

properties = {
	my_element = {
		frame = my_temp_var
	}
}

dynamic_lists = {
	my_gridbox = {
		array = my_temp_array
		entry_container = "my_entry_container"
	}
}
```

## Dynamic Lists

This is a special feature that is to be used in tandem with grid boxes within interface modding. It will draw a gui for each value inside of the array chosen where the grid box with the same name is.

Here is some example code of how the scripted gui should look:

```text
scripted_gui = {
	Example_GUI = {
	
		context_type = player_context
		
		window_name = "Example_GUI_Window"

		visible = {
			
		}

		dynamic_lists = {
			Example_Grid_Box = {
					#The array to use. Will call a gui for each index.
					array = Example_Array

					#value of the current array index. Optional. Default value is v.
					value = v

					#current array index. Optional. Default value is i.
					index = i
					
					#This will change the scope to the value if yes
					change_scope = no

					#The GUI drawn for each index
					entry_container = "Example_GUI_Array"
			}
		}
		effects = {
			#Example Buttons to show it working
			Button_1_click = {
				add_to_array = {Example_Array = 1}
			}
			Button_2_click = {
				remove_from_array = {Example_Array = 1}
			}
		}
		triggers = {

		}
		properties = {

		}
	}
}
```

And this would be the corresponding gui:

```text
guiTypes = {
	#Example Scripted GUI Window
	containerWindowType = {
		name = "Example_GUI_Window"
		size = { width = 400 height = 300 }
		Orientation = upper_left
		moveable = yes
		position = { x = 650 y = 250 }
					
		background = {
			name = "Background"
			quadTextureSprite = "GFX_tiled_window2_1b_border"
		}
		
		#Not required to put the gridbox within another container, but it allows for scrolling with the correct background and scrollbar type. This one is transparent.
			
		#Example Buttons for array
		buttonType = {
			name ="Button_1"
			quadTextureSprite ="GFX_button_261x34"
			position = { x=50 y=15 }
			#This will write onto the button the value and index of the array
			buttonText = "Add 1 to array"
			buttonFont = "hoi_16mbs"
			Orientation = centre
		}
			
		buttonType = {
			name ="Button_2"
			quadTextureSprite ="GFX_button_261x34"
			position = { x=50 y=50 }
			#This will write onto the button the value and index of the array
			buttonText = "Remove 1 from array"
			buttonFont = "hoi_16mbs"
			Orientation = centre
		} 
		containerWindowType = {
			name = "Example_Container_For_Grid"
			Orientation = upper_left
			size = {width=400 height=200}
			position = {x=0 y=100}
			verticalScrollbar = "right_vertical_slider_intel"
			scroll_wheel_factor = 40
			smooth_scrolling = yes
					
			background = {
				name = "Background"
				quadTextureSprite = "GFX_tiled_window_transparent"
			}
			
			gridBoxType = {
				name = "Example_Grid_Box"
				position = { x = 50 y = 0}
				#The size of the gridbox
				size = { width = 100%% height = 100%% }
				Orientation = upper_left
				#The slot size
				slotsize = {width=400 height=50 }
				format = "UPPER_LEFT"
				#the maximum horizontal gui elements
				max_slots_horizontal = 1
				#the maximum vertical gui elements
				#max_slots_vertical = 1
			}
		}
	}

	#Example GUI for each Array Index. This will use an already existing button as an example.
	containerWindowType = {
		name = "Example_GUI_Array"
		size = {width=400 height=50}
			
		buttonType = {
			name ="Example_GUI"
			quadTextureSprite ="GFX_button_261x34"
			position = { x=0 y=0 }
			#This will write onto the button the value and index of the array
			buttonText = "v: [?v] i: [?i]"
			buttonFont = "hoi_16mbs"
		}
	}
}
```

## Properties

Properties allow for specified elements to be manipulated whilst in-game, allowing for their texture and position to be changed.

Properties support manipulating the frame of a texture directly with the **frame** attribute, which changes the frame to the value given by a specified variable.

Likewise, properties support manipulating the x and y coordinates for an element, with the **x** and **y** attributes which change the element position to the value given by a specified variable.

The **image** attribute determines the texture used:

```text
properties = {
    my_icon = {
        image = "GFX_my_texture"
    }
}
```

This would assign an **icon element** with the name of **my\_icon** with a texture **GFX\_my\_texture**.

At first glance, this may seem useless, but the power here is that the string accepts scripted localization. This means you can create a scripted localization entry that supplies the texture string.

```text
properties = {
    my_icon = {
        image = "[get_my_icon_texture]"
    }
}
```

```text
defined_text = {
    name = get_my_icon_texture
    
    text = {
        trigger = {
            <triggers>
        }
        localization_key = "GFX_my_texture_1"
    }
    text = {
        trigger = {
            <triggers>
        }
        localization_key = "GFX_my_texture_2"
    }
}
```

This is an example of using scripted localization to supply the property with the texture string.

## AI

The true usefulness of scripted GUIs is that they can be used by the AI, meaning new features can be properly implemented with custom interfaces that the AI can navigate.

### AI enabled

The first step is to determine when the AI is enabled for the GUI.

```text
ai_enabled = {
    <triggers>
}
```

This scope is checked during initialization, and any AI that fail are never checked again.

This is the best optimization, as it means invalid AIs will never be checked again, but it is only checked once.

### AI Test Attributes

These attributes determine when the AI checks the scripted GUI.

**ai\_test\_interval** determines how often the AI checks, in hours. By default set to 24.  
**ai\_test\_variance** determines the variance in time (In percent) for the check, which is the specified variance divided by 2 for plus and minus. By default set to 0.2   
As such, an interval of 100 with a variance of 0.2 will make the AI check every 90 to 110 hours (100±[10% of 100, which is 10]).

### AI Check

This scope is checked on every tick of the interval specified by **ai\_test\_interval**. If it evaluates as false, the AI will ignore the GUI for the tick.

### AI Test Scopes

The AI needs to be told who it should target when using scripted GUIs. You can imagine this as the AI clicking on the countries or states.

You can specify nothing, but this will result in the AI checking every possible country or state, which will harm performance, and so should be avoided unless required.

For **player\_context** and **decision\_category**, **ai\_test\_scopes** is not needed as the only checked scope is the country using the GUI.

For **selected\_country\_context** the AI will check every country in the world by default. By specifying an **ai\_test\_scopes**, the AI will be limited to the specified range of countries.

The tokens for **selected\_country\_context**:

- test\_self\_country
- test\_enemy\_countries
- test\_ally\_countries
- test\_neighbouring\_countries
- test\_neighbouring\_ally\_countries
- test\_neighbouring\_enemy\_countries

You can combine multiple **ai\_test\_scopes** by adding multiple to the definition.

For **selected\_state\_context** the AI will check every state in the world by default. By specifying an **ai\_test\_scopes**, the AI will be limited to the specified range of states.

The tokens for **selected\_state\_context**:

- test\_self\_owned\_states
- test\_enemy\_owned\_states
- test\_ally\_owned\_states
- test\_self\_controlled\_states
- test\_enemy\_controlled\_states
- test\_ally\_controlled\_states
- test\_neighbouring\_states
- test\_neighbouring\_enemy\_states
- test\_neighbouring\_ally\_states
- test\_our\_neighbouring\_states - AIs edge states
- test\_our\_neighbouring\_states\_against\_allies - AIs edge states to allies
- test\_our\_neighbouring\_states\_against\_enemies - AIs edge states to enemies
- test\_contesded\_states - states that shares provinces between enemy countries

You can combine multiple **ai\_test\_scopes** by adding multiple to the definition.

You can define **test\_if\_only\_major** which will limit the other scopes to only major countries or states owned by them.

You can define **test\_if\_only\_coastal** which will limit the other scopes to only coastal countries or states.

### AI Check Scope

Now the AI knows what to target, it is possible to filter these with triggers.

```text
ai_check_scope = {
    <triggers>
}
```

### AI Weights

The AI also needs to be told how to handle the actual clickable elements within the GUI. This happens with the **ai\_weights** scope.

You add an entry for the element and define a set of factors within the **ai\_will\_do** scope.

You can use **factor** or **add**, although only one should be present in the same scope.

Whilst the weight for an element is above 0, the AI will attempt to click it.

By default, the AI will only select one element per tick, clicking the element with the highest score. To allow the AI to click more than one element, specify **ai\_max\_weight\_taken\_per\_test = <int>**, which sets the maximum number of actions the AI will take.

By default, each action has an AI weight of 1. You can define a higher *cost* by adding the **weight** attribute to the **ai\_will\_do**.

The **ignore\_lower\_weights** attribute is added to the **ai\_will\_do** scope to tell the AI to ignore every action below the specified weight whilst its factor is above 0.

This allows the AI to ignore other actions as it may need to *save* a resource to take the action. Without this, the AI would take another action that may take the same resource and so would never take the first action, even when the factor is higher, as it would never save enough resources to take it.

### AI Parents

You can define an AI parent that means the AI for different scripted GUIs is processed together. This is useful if different GUIs may use resources that another would deplete, and so by processing the AI together, the actions can be properly limited.

## Template

```text
scripted_gui = {
    <name> = {
        window_name = <string>
        context_type = <type>
        parent_window_token = <string>
         
        visible = {
            <triggers>
        }
        
        effects = {
            <element>_click = {
                <effects>
            }
            <element>_<modifier>_click = {
                <effects>
            }
        }
        
        triggers = {
            <element>_click_enabled = {
                <triggers>
            }
            <element>_visible = {
                <triggers>
            }
        }
        
        properties = {
            <element> = {
                image = <string>
                frame = <var>
                x = <var>
                y = <var>
            }
        }
        
        ai_enabled = {
            <triggers>
        }
        
        ai_test_parent = <string>
        
        ai_test_interval = <int>
        ai_test_variance = <float>
        ai_test_scopes = <type>
        
        ai_check = {
            <triggers>
        }
        
        ai_check_scope = {
            <triggers>
        }
        
        ai_max_weight_taken_per_test = <int>
        
        ai_weights = {
            <element>_<modifiers>_click = {
                ai_will_do = {
                    base = <int>
                    factor = <float>
                    add = <float>
                    
                    modifier = {
                        factor = <float>
                        add = <float>
                        
                        <triggers>
                    }
                }
                ignore_lower_weights = {
                    factor = <float>
                }
            }
        }
    }
}
```

## Scripted Localization

There is a special localization command that allows a scripted GUI element to display its effect within a tooltip.

`[!<element>_<action>]`

For example:

`MY_TOOLTIP: "[!test_button_click]"`

A similar command is available for the triggers for that particular element.

`[!<element>_<action>_enabled]`

For example:

`MY_TOOLTIP: "[!test_button_click_enabled]"`

## Tips

You can use the console command **human\_ai** to enable AI for the current human country. This writes the AI checks and the results of said checks to the *scripted\_ai.log*.

Event targets **CANNOT** be used in scripted GUIs, it will break everything. Make use of variable scopes instead.

Scripted effects and triggers can be used in scripted GUIs, and can be useful to separate the GUI logic and the gameplay logic.

## See also

- [Scripted GUI Tutorial](https://forum.paradoxplaza.com/forum/index.php?threads/1084697) by a Paradox developer.
- Script examples by a Paradox developer: [Gitlab](https://gitlab.com/shultays/script_examples), [Steam](https://steamcommunity.com/sharedfiles/filedetails/?id=1678247250).

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
