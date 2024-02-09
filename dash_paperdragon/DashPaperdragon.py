# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashPaperdragon(Component):
    """A DashPaperdragon component.


Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- baseImageWidth (number; optional)

- config (dict; optional):
    config is a dictionary of options for setting up the component and
    initial rendering.

- curMousePosition (dict; optional):
    Current Mouse Position in Image Coordinates.

- inputToPaper (dict; optional):
    data sent from dash to paper.

- outputFromPaper (dict; optional):
    data sent from paper back to dash.

- tileSourceProps (list; optional):
    sent from dash to update x offset, y offset, rotation, or opacity
    of the image.

- tileSources (string | list; optional):
    the tile source for openseadragon.

- viewerHeight (number; optional)

- viewerWidth (number; optional)

- viewportBounds (dict; optional):
    viewportBounds of the current OSD Viewer.

- zoomLevel (number; optional):
    zoomLevel of the current OSD Viewer."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_paperdragon'
    _type = 'DashPaperdragon'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, config=Component.UNDEFINED, tileSources=Component.UNDEFINED, zoomLevel=Component.UNDEFINED, curMousePosition=Component.UNDEFINED, viewportBounds=Component.UNDEFINED, outputFromPaper=Component.UNDEFINED, inputToPaper=Component.UNDEFINED, tileSourceProps=Component.UNDEFINED, baseImageWidth=Component.UNDEFINED, viewerWidth=Component.UNDEFINED, viewerHeight=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'baseImageWidth', 'config', 'curMousePosition', 'inputToPaper', 'outputFromPaper', 'tileSourceProps', 'tileSources', 'viewerHeight', 'viewerWidth', 'viewportBounds', 'zoomLevel']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'baseImageWidth', 'config', 'curMousePosition', 'inputToPaper', 'outputFromPaper', 'tileSourceProps', 'tileSources', 'viewerHeight', 'viewerWidth', 'viewportBounds', 'zoomLevel']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DashPaperdragon, self).__init__(**args)
