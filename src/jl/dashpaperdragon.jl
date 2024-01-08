# AUTO GENERATED FILE - DO NOT EDIT

export dashpaperdragon

"""
    dashpaperdragon(;kwargs...)

A DashPaperdragon component.

Keyword arguments:
- `id` (String; optional): The ID used to identify this component in Dash callbacks.
- `curMousePosition` (Dict; optional): Current Mouse Position in Image Coordinates
- `curShapeObject` (Dict; optional): curShapeObject is the current shape object that was most recently moused over
- `imageSrc` (String; optional): the tile source for openseadragon
- `shapeList` (Dict; optional): shapeList is a list of shapes to be drawn on the image
- `viewPortBounds` (Dict; optional): viewportBounds of the current OSD Viewer
- `zoomLevel` (Real; optional): zoomLevel of the current OSD Viewer
"""
function dashpaperdragon(; kwargs...)
        available_props = Symbol[:id, :curMousePosition, :curShapeObject, :imageSrc, :shapeList, :viewPortBounds, :zoomLevel]
        wild_props = Symbol[]
        return Component("dashpaperdragon", "DashPaperdragon", "dash_paperdragon", available_props, wild_props; kwargs...)
end

