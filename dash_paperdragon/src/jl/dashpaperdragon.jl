# AUTO GENERATED FILE - DO NOT EDIT

export dashpaperdragon

"""
    dashpaperdragon(;kwargs...)

A DashPaperdragon component.
ExampleComponent is an example component.
It takes a property, `label`, and
displays it.
It renders an input with the property `value`
which is editable by the user.
Keyword arguments:
- `id` (String; optional): The ID used to identify this component in Dash callbacks.
- `imageSrc` (String; optional): the tile source for openseadrgon
- `label` (String; required): A label that will be printed when this component is rendered.
- `value` (String; optional): The value displayed in the input.
- `zoomLevel` (Real; optional): zoomLevel of the current OSD Viewer
"""
function dashpaperdragon(; kwargs...)
        available_props = Symbol[:id, :imageSrc, :label, :value, :zoomLevel]
        wild_props = Symbol[]
        return Component("dashpaperdragon", "DashPaperdragon", "dash_paperdragon", available_props, wild_props; kwargs...)
end

