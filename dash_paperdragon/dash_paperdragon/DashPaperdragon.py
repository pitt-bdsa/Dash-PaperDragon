# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashPaperdragon(Component):
    """A DashPaperdragon component.
ExampleComponent is an example component.
It takes a property, `label`, and
displays it.
It renders an input with the property `value`
which is editable by the user.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- globalX (number; optional):
    globalX of the current OSD Viewer.

- globalY (number; optional):
    globalY of the current OSD Viewer.

- imageSrc (string; optional):
    the tile source for openseadrgon.

- label (string; required):
    A label that will be printed when this component is rendered.

- value (string; optional):
    The value displayed in the input.

- zoomLevel (number; optional):
    zoomLevel of the current OSD Viewer."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_paperdragon'
    _type = 'DashPaperdragon'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, label=Component.REQUIRED, value=Component.UNDEFINED, imageSrc=Component.UNDEFINED, zoomLevel=Component.UNDEFINED, globalX=Component.UNDEFINED, globalY=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'globalX', 'globalY', 'imageSrc', 'label', 'value', 'zoomLevel']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'globalX', 'globalY', 'imageSrc', 'label', 'value', 'zoomLevel']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['label']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(DashPaperdragon, self).__init__(**args)
