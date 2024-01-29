# AUTO GENERATED FILE - DO NOT EDIT

export dashpaperdragon

"""
    dashpaperdragon(;kwargs...)

A DashPaperdragon component.

Keyword arguments:
- `id` (String; optional): The ID used to identify this component in Dash callbacks.
- `config` (Dict; optional): config is a dictionary of options for setting up the component and initial rendering
- `curMousePosition` (Dict; optional): Current Mouse Position in Image Coordinates
- `imageSrc` (String; optional): the tile source for openseadragon
- `inputToPaper` (Dict; optional): data sent from dash to paper
- `outputFromPaper` (Dict; optional): data sent from paper back to dash
- `viewportBounds` (Dict; optional): viewportBounds of the current OSD Viewer
- `zoomLevel` (Real; optional): zoomLevel of the current OSD Viewer
"""
function dashpaperdragon(; kwargs...)
        available_props = Symbol[:id, :config, :curMousePosition, :imageSrc, :inputToPaper, :outputFromPaper, :viewportBounds, :zoomLevel]
        wild_props = Symbol[]
        return Component("dashpaperdragon", "DashPaperdragon", "dash_paperdragon", available_props, wild_props; kwargs...)
end

