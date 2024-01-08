# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashPaperdragon(Component):
    """A DashPaperdragon component.


Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- curMousePosition (dict; optional):
    Current Mouse Position in Image Coordinates.

- curShapeObject (dict; optional):
    curShapeObject is the current shape object that was most recently
    moused over.

- imageSrc (string; optional):
    the tile source for openseadragon.

- shapeList (dict; optional):
    shapeList is a list of shapes to be drawn on the image.

- viewPortBounds (dict; optional):
    viewportBounds of the current OSD Viewer.

- zoomLevel (number; optional):
    zoomLevel of the current OSD Viewer."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_paperdragon'
    _type = 'DashPaperdragon'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, shapeList=Component.UNDEFINED, imageSrc=Component.UNDEFINED, zoomLevel=Component.UNDEFINED, curMousePosition=Component.UNDEFINED, viewPortBounds=Component.UNDEFINED, curShapeObject=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'curMousePosition', 'curShapeObject', 'imageSrc', 'shapeList', 'viewPortBounds', 'zoomLevel']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'curMousePosition', 'curShapeObject', 'imageSrc', 'shapeList', 'viewPortBounds', 'zoomLevel']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DashPaperdragon, self).__init__(**args)
