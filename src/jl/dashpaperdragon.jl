# AUTO GENERATED FILE - DO NOT EDIT

export dashpaperdragon

"""
    dashpaperdragon(;kwargs...)

A DashPaperdragon component.

Keyword arguments:
- `id` (String; optional): The ID used to identify this component in Dash callbacks.
- `baseImageWidth` (Real; optional)
- `config` (Dict; optional): config is a dictionary of options for setting up the component and initial rendering
- `curMousePosition` (Dict; optional): Current Mouse Position in Image Coordinates
- `inputToPaper` (Dict; optional): data sent from dash to paper
- `outputFromPaper` (Dict; optional): data sent from paper back to dash
- `tileSourceProps` (Array; optional): sent from dash to update x offset, y offset, rotation, or opacity of the image
- `tileSources` (String | Array; optional): the tile source for openseadragon
- `viewportBounds` (Dict; optional): viewportBounds of the current OSD Viewer
- `zoomLevel` (Real; optional): zoomLevel of the current OSD Viewer
"""
function dashpaperdragon(; kwargs...)
        available_props = Symbol[:id, :baseImageWidth, :config, :curMousePosition, :inputToPaper, :outputFromPaper, :tileSourceProps, :tileSources, :viewportBounds, :zoomLevel]
        wild_props = Symbol[]
        return Component("dashpaperdragon", "DashPaperdragon", "dash_paperdragon", available_props, wild_props; kwargs...)
end

