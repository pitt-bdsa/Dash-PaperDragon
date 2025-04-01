import dash_paperdragon
from dash import (
    Dash,
    callback,
    html,
    Input,
    Output,
    dcc,
    State,
    ALL,
    MATCH,
    callback_context,
    no_update,
)
import dash_bootstrap_components as dbc
import json, random
import dash_ag_grid
from pprint import pprint
import requests
from sampleTileSources import tileSources
import re
from dashPaperDragonHelpers import (
    generate_random_checkerboard,
    get_box_instructions,
    generate_random_boxes,
    generate_random_points,
    get_color_from_pixel,
    generateImgSrcControlPanel,
    generate_key_bindings_modal,
    generate_annotation_panel,
    convertPaperInstructions_toTableForm,
    get_dsa_image_metadata,
    get_dsa_annotations,
    get_dsa_annotation_list,
    createItem,
    deleteItem,
    itemDeleted,
    propertyChanged,
    mouseLeave,
    mouseEnter,
    colorGrabbed,
)


def get_dsa_image_metadata(api_url, item_id):
    """Fetch image metadata from DSA server"""
    try:
        metadata_url = f"{api_url}/item/{item_id}/tiles"
        response = requests.get(metadata_url)
        if response.status_code == 200:
            metadata = response.json()
            return {
                "width": metadata.get("sizeX", 0),
                "height": metadata.get("sizeY", 0),
            }
        else:
            print(
                f"Failed to fetch metadata for item {item_id}: {response.status_code}"
            )
            return {"width": 0, "height": 0}
    except Exception as e:
        print(f"Error fetching metadata: {e}")
        return {"width": 0, "height": 0}


def get_dsa_annotations(api_url, item_id):
    """Fetch annotations from DSA and convert them to shape format."""
    try:
        response = requests.get(f"{api_url}/annotation/item/{item_id}")
        response.raise_for_status()
        annotations = response.json()

        shapes = []
        for annotation in annotations:
            # Convert DSA annotation to GeoJSON
            geojson = dsa_to_geo_json(annotation)

            # Process each feature in the GeoJSON
            for feature in geojson["features"]:
                shape = {
                    "id": feature["properties"].get("userdata", {}).get("id", ""),
                    "type": feature["geometry"]["type"],
                    "coordinates": feature["geometry"]["coordinates"],
                    "label": feature["properties"].get("label", ""),
                    "fillColor": feature["properties"].get("fillColor", "#ff0000"),
                    "strokeColor": feature["properties"].get("strokeColor", "#000000"),
                }
                shapes.append(shape)

        return shapes
    except Exception as e:
        print(f"Error fetching DSA annotations: {e}")
        return []


def get_dsa_annotation_list(api_url, item_id):
    """Fetch list of available annotations for an item from DSA."""
    try:
        response = requests.get(f"{api_url}/annotation", params={"itemId": item_id})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching annotation list: {e}")
        return []


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# For now these are global variables; can be redis if multiple windows can interact with the same server
colors = ["red", "orange", "yellow", "green", "blue", "purple"]
classes = ["a", "b", "c", "d", "e", "f"]

globalId = 0


def getId():
    global globalId
    globalId = globalId + 1
    return globalId


# possible bindings for actions:
# keyDown
# keyUp
# mouseEnter
# mouseLeave
# click ?

# supported actions:
# cycleProp (property)
# cyclePropReverse (property)
# deleteItem
# newItem
# dashCallback (callback)

# supported callback functions:
# createItem


# Initialize tileSourceDict with image dimensions
tileSourceDict = {}
for source in tileSources:
    label = source["label"]
    tile_sources = source["tileSources"]

    if isinstance(tile_sources, list):
        # Handle multiple tile sources
        processed_sources = []
        for ts in tile_sources:
            if isinstance(ts, str):
                processed_sources.append(
                    {
                        "tileSource": ts,
                        "x": 0,
                        "y": 0,
                        "opacity": 1,
                        "rotation": 0,
                    }
                )
            else:
                # Construct tile source URL from API URL and item ID
                tile_source_url = f"{ts['api_url']}/item/{ts['item_id']}/tiles/dzi.dzi"
                processed_sources.append(
                    {
                        "tileSource": tile_source_url,
                        "x": ts.get("x", 0),
                        "y": ts.get("y", 0),
                        "opacity": ts.get("opacity", 1),
                        "rotation": ts.get("rotation", 0),
                        "layerIdx": ts.get("layerIdx", 0),
                    }
                )
        tileSourceDict[label] = processed_sources
    else:
        # Handle single tile source
        if isinstance(tile_sources, str):
            tileSourceDict[label] = {
                "tileSource": tile_sources,
                "x": 0,
                "y": 0,
                "opacity": 1,
                "rotation": 0,
            }
        else:
            # Construct tile source URL from API URL and item ID
            tile_source_url = f"{tile_sources['api_url']}/item/{tile_sources['item_id']}/tiles/dzi.dzi"
            tileSourceDict[label] = {
                "tileSource": tile_source_url,
                "x": tile_sources.get("x", 0),
                "y": tile_sources.get("y", 0),
                "opacity": tile_sources.get("opacity", 1),
                "rotation": tile_sources.get("rotation", 0),
                "layerIdx": tile_sources.get("layerIdx", 0),
            }


config = {
    "eventBindings": [
        {"event": "keyDown", "key": "c", "action": "cycleProp", "property": "class"},
        {
            "event": "keyDown",
            "key": "x",
            "action": "cyclePropReverse",
            "property": "class",
        },
        {"event": "keyDown", "key": "d", "action": "deleteItem"},
        {"event": "keyDown", "key": "n", "action": "newItem", "tool": "rectangle"},
        {
            "event": "keyDown",
            "key": "o",
            "action": "dashCallback",
            "callback": "grabColor",
        },
        {"event": "mouseEnter", "action": "dashCallback", "callback": "mouseEnter"},
        {"event": "mouseLeave", "action": "dashCallback", "callback": "mouseLeave"},
    ],
    "callbacks": [
        {"eventName": "item-created", "callback": "createItem"},
        {"eventName": "property-changed", "callback": "propertyChanged"},
        {"eventName": "item-deleted", "callback": "itemDeleted"},
        {"eventName": "color-grabbed", "callback": "colorGrabbed"},
    ],
    "properties": {"class": classes},
    "defaultStyle": {
        "fillColor": colors[0],
        "strokeColor": colors[0],
        "rescale": {
            "strokeWidth": 1,
        },
        "fillOpacity": 0.2,
    },
    "styles": {
        "class": {
            k: {"fillColor": c, "strokeColor": c} for (k, c) in zip(classes, colors)
        }
    },
}


def cbCreateItem(args):
    return createItem(args)


def cbItemDeleted(args):
    print(args)
    print("Item Deleted")
    return itemDeleted(args)


def cbMouseEnter(args):
    return mouseEnter(args)


def cbMouseLeave(args):
    return mouseLeave(args)


def cbPropertyChanged(args):
    return propertyChanged(args)


def cbColorGrabbed(args):
    return colorGrabbed(args)


callbacks = {
    "createItem": cbCreateItem,
    "itemDeleted": cbItemDeleted,
    "mouseEnter": cbMouseEnter,
    "mouseLeave": cbMouseLeave,
    "propertyChanged": cbPropertyChanged,
    "colorGrabbed": cbColorGrabbed,
}


# First, define the column definitions
tileSourceColumns = [
    {"field": "layer", "headerName": "Layer", "width": 90},
    {
        "field": "visible",
        "headerName": "Visible",
        "width": 90,
        "cellRenderer": "agCheckboxCellRenderer",
        "editable": True,
    },
    {
        "field": "x_offset",
        "headerName": "X Offset (px)",
        "width": 120,
        "type": "numericColumn",
        "editable": True,
    },
    {
        "field": "y_offset",
        "headerName": "Y Offset (px)",
        "width": 120,
        "type": "numericColumn",
        "editable": True,
    },
    {
        "field": "opacity",
        "headerName": "Opacity",
        "width": 100,
        "type": "numericColumn",
        "editable": True,
        "valueFormatter": {"function": "params => params.value.toFixed(2)"},
    },
    {
        "field": "rotation",
        "headerName": "Rotation",
        "width": 100,
        "type": "numericColumn",
        "editable": True,
    },
    {
        "field": "pixelWidth",
        "headerName": "Image Width",
        "width": 120,
        "type": "numericColumn",
        "editable": False,
        "valueFormatter": {
            "function": "params => params.value.toLocaleString() + ' px'"
        },
    },
    {
        "field": "pixelHeight",
        "headerName": "Image Height",
        "width": 120,
        "type": "numericColumn",
        "editable": False,
        "valueFormatter": {
            "function": "params => params.value.toLocaleString() + ' px'"
        },
    },
]

paperJsShapeColumns = [
    {"field": "objectId", "headerName": "ID", "width": 70, "maxWidth": 70},
    {"field": "type", "headerName": "Type", "width": 90},
    {"field": "class", "headerName": "Class", "width": 80},
    {"field": "fillColor", "headerName": "Color", "width": 90},
    {
        "field": "fillOpacity",
        "headerName": "Opacity",
        "width": 120,
        "type": "numericColumn",
        "editable": True,
        "cellRenderer": "agSliderCellRenderer",
        "cellRendererParams": {
            "minValue": 0,
            "maxValue": 1,
            "step": 0.1,
            "valueFormatter": {"function": "params => params.value.toFixed(2)"},
        },
    },
    {"field": "x", "headerName": "X", "width": 80, "type": "numericColumn"},
    {"field": "y", "headerName": "Y", "width": 80, "type": "numericColumn"},
    {"field": "markerSize", "headerName": "Size", "width": 80, "type": "numericColumn"},
    {"field": "markerColor", "headerName": "Marker Color", "width": 90},
]

## Create element
osdElement = dash_paperdragon.DashPaperdragon(
    id="osdViewerComponent",
    # tileSources = tileSources[0],  //Can set a default tilesource here if you want
    config=config,
    zoomLevel=0,
    viewportBounds={"x": 0, "y": 0, "width": 0, "height": 0},
    curMousePosition={"x": 0, "y": 0},
    inputToPaper=None,
    outputFromPaper=None,
    viewerWidth=800,
    # curShapeObject=[],
)

## Make HTML layout
coordinate_display = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("Zoom Level", className="mb-1"),
                                html.Div(id="zoomLevel_disp", className="card-text"),
                            ]
                        ),
                        className="mb-1",
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("Viewport Bounds", className="mb-1"),
                                html.Div(
                                    id="viewportBounds_disp", className="card-text"
                                ),
                            ]
                        ),
                        className="mb-1",
                    ),
                    width=8,
                ),
            ],
            className="g-2",  # Reduce gap between cards
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("Mouse Position", className="mb-1"),
                                html.Div(id="mousePos_disp", className="card-text"),
                            ]
                        ),
                        style={"height": "3.5rem"},
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("Selected Color", className="mb-1"),
                                html.Div(id="color_disp", className="card-text"),
                            ]
                        ),
                        style={"height": "3.5rem"},
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("Highlighted Object", className="mb-1"),
                                html.Div(
                                    id="curObject_disp",
                                    className="card-text",
                                    style={
                                        "overflowY": "auto",
                                        "maxHeight": "2rem",  # Adjusted height for content
                                        "whiteSpace": "pre-wrap",
                                        "wordBreak": "break-all",
                                        "fontSize": "0.9em",
                                        "cursor": "pointer",
                                        "padding": "2px 4px",
                                        "border": "1px solid transparent",  # For hover effect
                                        "transition": "all 0.2s ease",  # Smooth transition for hover
                                        "backgroundColor": "rgba(0,0,0,0.02)",  # Slight background
                                        "borderRadius": "4px",  # Rounded corners
                                    },
                                ),
                            ],
                            style={"padding": "0.5rem"},  # Reduce padding in card body
                        ),
                        style={
                            "height": "3.5rem",  # Fixed card height
                            "minWidth": "200px",  # Ensure minimum width
                        },
                    ),
                    width=4,
                ),
            ],
            className="g-2",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H6(
                                            "Tile Source Properties", className="mb-2"
                                        ),
                                        html.Div(id="imgScrControls_data"),
                                        dash_ag_grid.AgGrid(
                                            id="tileSourceTable",
                                            columnDefs=tileSourceColumns,
                                            rowData=[],
                                            defaultColDef={
                                                "resizable": True,
                                                "sortable": True,
                                                "filter": True,
                                                "editable": True,
                                            },
                                            style={
                                                "height": "150px",  # Fixed height
                                                "width": "100%",
                                            },
                                            dashGridOptions={
                                                "rowHeight": 35,
                                                "headerHeight": 35,
                                                "enableCellTextSelection": True,
                                                "stopEditingWhenCellsLoseFocus": True,
                                                "enterMovesDown": False,
                                                "enterMovesDownAfterEdit": False,
                                            },
                                        ),
                                    ],
                                    className="p-2",
                                ),  # Reduce padding
                            ],
                            className="mb-2",
                        ),  # Reduce margin
                    ],
                    width=12,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H6("Shape Table", className="mb-2"),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Label(
                                                            "Global Opacity:",
                                                            className="me-2",
                                                        ),
                                                        dcc.Slider(
                                                            id="global-opacity-slider",
                                                            min=0,
                                                            max=1,
                                                            step=0.1,
                                                            value=0.2,
                                                            marks={
                                                                i / 10: str(i / 10)
                                                                for i in range(11)
                                                            },
                                                            tooltip={
                                                                "placement": "bottom",
                                                                "always_visible": True,
                                                            },
                                                        ),
                                                    ],
                                                    className="mb-2",
                                                ),
                                            ],
                                        ),
                                        dash_ag_grid.AgGrid(
                                            id="shapeDataTable",
                                            columnDefs=paperJsShapeColumns,
                                            rowData=[],
                                            defaultColDef={
                                                "resizable": True,
                                                "sortable": True,
                                                "filter": True,
                                                "minWidth": 80,
                                            },
                                            style={
                                                "height": "200px",
                                                "width": "100%",
                                            },
                                            dashGridOptions={
                                                "rowHeight": 35,
                                                "headerHeight": 35,
                                                "enableCellTextSelection": True,
                                                "rowSelection": "single",
                                            },
                                        ),
                                    ],
                                    className="p-2",
                                ),
                            ],
                            className="mb-2",
                        ),
                    ],
                    width=12,
                ),
            ]
        ),
    ],
    className="no-right-margin g-0",
)

annotation_panel = generate_annotation_panel()


imageSelect_dropdown = html.Div(
    [
        html.Label(
            "Select an image",
            className="text-center mb-3",
            style={"marginTop": "5px", "marginRight": "5px"},
        ),
        dbc.Select(
            id="imageSelect",
            options=[x["label"] for x in tileSources],
            value="TCGA-BF-A1Q0-01A-02-TSB",
            className="mb-4 d-inline",
            style={"width": "300px", "marginLleft": "10px", "marginTop": "1px"},
        ),
        dbc.Button(
            "Make Random Rects",
            id="make_random_button",
            className="m-1 d-inline",
            style={"marginLeft": "10px", "height": "40px"},
        ),
        dbc.Button(
            "Make Random Points",
            id="make_random_points_button",
            className="m-1 d-inline",
            style={"marginLeft": "10px", "height": "40px"},
        ),
        dbc.Button(
            "⌨️ Key Bindings",
            id="show-keybindings",
            color="secondary",
            outline=True,
            size="sm",
            className="m-1 d-inline",
            style={"marginLeft": "10px", "height": "40px"},
        ),
        dbc.Switch(
            id="clearItems-toggle",
            label="Clear Items",
            value=False,
            className="mt-2 d-inline",
        ),
    ],
    style={"display": "flex", "flexDirection": "row", "align": "center"},
)


# Create the modal for key bindings
key_bindings_modal = generate_key_bindings_modal(config)


app.layout = dbc.Container(
    [
        dcc.Store(id="osdShapeData_store", data=[]),
        dbc.Row(dbc.Col(html.H1("Dash Paperdragon", className="text-center"))),
        dbc.Row(
            [
                dbc.Col([imageSelect_dropdown, osdElement], width=8),
                dbc.Col(
                    coordinate_display,
                    width=4,
                ),
            ],
        ),
        dbc.Row([dbc.Col(annotation_panel)]),
        key_bindings_modal,  # Add the modal to the layout
    ],
    fluid=True,
)
## End of layout

### OutputFromPaper needs to be cleared as well once the message/state has been acknowledged


## NEED TO CLEAR THE MESSAGE ONCE THE EVENT FIRES...
@callback(
    Output("osdShapeData_store", "data"),
    [
        Input("annotationTable", "selectedRows"),
        Input("make_random_button", "n_clicks"),
        Input("make_random_points_button", "n_clicks"),
        Input("global-opacity-slider", "value"),
        Input("shapeDataTable", "cellValueChanged"),  # Add this input
    ],
    [
        State("imageSelect", "value"),
        State("osdShapeData_store", "data"),
        State("osdViewerComponent", "viewportBounds"),
        State("clearItems-toggle", "value"),
    ],
)
def update_shape_data_store(
    selected_rows,
    make_random_boxesClicked,
    make_random_pointsClicked,
    global_opacity,
    cell_changes,
    tileSourceIdx,
    current_shapes,
    viewPortBounds,
    clearItems,
):
    """Central callback that manages all shape data store updates"""
    ctx = callback_context
    if not ctx.triggered:
        return no_update

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Initialize current_shapes if None
    if current_shapes is None:
        current_shapes = []

    # Handle individual shape opacity changes
    if triggered_id == "shapeDataTable":
        if not cell_changes or not current_shapes:
            return no_update

        try:
            # Get the most recent change
            change = cell_changes[0]
            if not isinstance(change, dict) or "data" not in change:
                return no_update

            data = change["data"]
            if not isinstance(data, dict):
                return no_update

            # Check if this is an opacity change
            if "fillOpacity" not in data:
                return no_update

            # Get the shape ID and new opacity value
            shape_id = data.get("objectId")
            new_opacity = float(data.get("fillOpacity", 0.2))

            # Update the shape in the store
            updated_shapes = []
            for shape in current_shapes:
                if shape["userdata"]["objectId"] == shape_id:
                    # Update the opacity in the shape's args
                    if "args" in shape and len(shape["args"]) > 0:
                        shape["args"][0]["fillOpacity"] = new_opacity
                updated_shapes.append(shape)

            return updated_shapes

        except Exception as e:
            print(f"Error updating shape opacity: {e}")
            return no_update

    # Handle global opacity changes
    elif triggered_id == "global-opacity-slider":
        if global_opacity is None:
            return no_update

        try:
            # Update opacity for all shapes
            updated_shapes = []
            for shape in current_shapes:
                if "args" in shape and len(shape["args"]) > 0:
                    shape["args"][0]["fillOpacity"] = global_opacity
                updated_shapes.append(shape)
            return updated_shapes

        except Exception as e:
            print(f"Error updating global opacity: {e}")
            return no_update

    # Handle annotation selection
    elif triggered_id == "annotationTable":
        if not selected_rows or not tileSourceIdx:
            return no_update

        # Get the selected annotation
        selected_ann = selected_rows[0]

        # Get the tile source
        tile_source = tileSourceDict[tileSourceIdx]
        if isinstance(tile_source, list):
            tile_source = tile_source[0]

        # Extract API URL and item ID
        if isinstance(tile_source, dict) and "tileSource" in tile_source:
            tile_url = tile_source["tileSource"]
            match = re.match(r"(.*api/v1)/item/(.*?)/tiles/dzi.dzi", tile_url)
            if match:
                api_url = match.group(1)
                item_id = match.group(2)

                try:
                    # Fetch the annotation data
                    response = requests.get(
                        f"{api_url}/annotation/{selected_ann['_id']}/geojson"
                    )
                    response.raise_for_status()
                    geojson_data = response.json()

                    # Convert to Paper.js format
                    new_shapes = []
                    for feature in geojson_data.get("features", []):
                        props = feature.get("properties", {})
                        shape_id = props.get("id", "")

                        # Get colors from DSA properties, with fallbacks
                        fill_color = props.get("fillColor")
                        if not fill_color or fill_color == "rgba(0, 0, 0, 0)":
                            fill_color = props.get("color", "rgba(255, 0, 0, 0.2)")

                        stroke_color = props.get("lineColor")
                        if not stroke_color:
                            stroke_color = props.get(
                                "strokeColor", props.get("color", "rgb(255, 0, 0)")
                            )

                        # Map DSA properties to Paper.js properties
                        paper_style = {
                            "fillColor": fill_color,
                            "strokeColor": stroke_color,
                            "strokeWidth": props.get("lineWidth", 2),
                            "fillOpacity": 0.2,
                        }

                        # Get the coordinates
                        coords = feature["geometry"]["coordinates"]
                        if feature["geometry"]["type"] == "Polygon":
                            points = coords[0]
                            shape = {
                                "paperType": "Path",
                                "args": [
                                    {
                                        "segments": [
                                            {"point": {"x": p[0], "y": p[1]}}
                                            for p in points
                                        ],
                                        "closed": True,
                                        **paper_style,
                                    }
                                ],
                                "userdata": {
                                    "class": "a",
                                    "objectId": getId(),
                                    "dsaId": shape_id,
                                    "type": props.get("type", "polygon"),
                                },
                            }
                            new_shapes.append(shape)

                    return current_shapes + new_shapes if not clearItems else new_shapes

                except Exception as e:
                    print(f"Error loading annotation: {e}")
                    return no_update

    # Handle random shape generation
    elif triggered_id in ["make_random_button", "make_random_points_button"]:
        if triggered_id == "make_random_button":
            new_shapes = generate_random_boxes(3, viewPortBounds, classes, colors)
        else:
            new_shapes = generate_random_points(3, viewPortBounds, classes, colors)

        return current_shapes + new_shapes if not clearItems else new_shapes

    return no_update


@callback(
    Output("osdViewerComponent", "inputToPaper"),
    [
        Input("shapeDataTable", "selectedRows"),
        Input("osdViewerComponent", "outputFromPaper"),
        Input("osdShapeData_store", "data"),  # Add shape data store as input
    ],
    [
        State("osdShapeData_store", "data"),
    ],
)
def update_paper_view(selected_rows, paper_output, shape_data_update, shape_data):
    """Unified callback to handle shape selection, paper events, and shape data updates"""
    ctx = callback_context
    if not ctx.triggered:
        return no_update

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Handle shape data store changes
    if triggered_id == "osdShapeData_store":
        if not shape_data_update:
            return no_update

        return {
            "actions": [
                {"type": "clearItems"},
                {"type": "drawItems", "itemList": shape_data_update},
            ]
        }

    # Handle shape table selection
    if triggered_id == "shapeDataTable":
        if not selected_rows or not shape_data:
            return no_update

        selected_shape = selected_rows[0]
        shape_id = selected_shape.get("objectId")

        # Find the full shape data for the selected shape
        full_shape = next(
            (
                shape
                for shape in shape_data
                if shape["userdata"]["objectId"] == shape_id
            ),
            None,
        )

        if not full_shape:
            return no_update

        # Calculate the bounds of the shape based on its type
        if full_shape["paperType"] == "Path.Rectangle":
            # For rectangles, we have point and size
            point = full_shape["args"][0]["point"]
            size = full_shape["args"][0]["size"]
            bounds = {
                "x": point["x"],
                "y": point["y"],
                "width": size["width"],
                "height": size["height"],
            }
        elif full_shape["paperType"] == "Path":
            # For paths/polygons, calculate bounds from segments
            segments = full_shape["args"][0].get("segments", [])
            if segments:
                x_coords = [seg["point"]["x"] for seg in segments]
                y_coords = [seg["point"]["y"] for seg in segments]
                bounds = {
                    "x": min(x_coords),
                    "y": min(y_coords),
                    "width": max(x_coords) - min(x_coords),
                    "height": max(y_coords) - min(y_coords),
                }
            else:
                # For points, create a small bounds around the point
                point = segments[0]["point"]
                bounds = {
                    "x": point["x"] - 100,
                    "y": point["y"] - 100,
                    "width": 200,
                    "height": 200,
                }
        elif full_shape["paperType"] == "Path.Circle":
            # For circles (points), create bounds around the center
            center = full_shape["args"][0]["center"]
            radius = full_shape["args"][0]["radius"]
            # Create a much larger square bounds around the circle
            padding = radius * 20  # Increased padding for better visibility
            bounds = {
                "x": center["x"] - padding,
                "y": center["y"] - padding,
                "width": padding * 2,
                "height": padding * 2,
            }
        else:
            return no_update

        # Add padding to the bounds (10% on each side)
        padding = {"x": bounds["width"] * 0.1, "y": bounds["height"] * 0.1}
        bounds["x"] -= padding["x"]
        bounds["y"] -= padding["y"]
        bounds["width"] += padding["x"] * 2
        bounds["height"] += padding["y"] * 2

        return {"actions": [{"type": "zoomToBounds", "bounds": bounds}]}

    # Handle Paper.js events
    elif triggered_id == "osdViewerComponent":
        if not paper_output:
            return no_update

        osdEventType = paper_output.get("data", {}).get("callback", None)
        if not osdEventType:
            osdEventType = paper_output.get("callback", None)

        if osdEventType == "grabColor":
            return {"actions": [{"type": "getColor"}]}
        elif osdEventType in ["mouseLeave", "mouseEnter", "colorGrabbed"]:
            return no_update

    return no_update


def generate_paperjs_polygon(shapeInfo):
    jsPolygon = [
        {
            "paperType": "Path",
            "args": [
                {
                    "fillColor": "red",
                    "strokeColor": "red",
                    "rescale": {"strokeWidth": 1},
                    "fillOpacity": 0.2,
                    "segments": [
                        {"x": 7849, "y": 19637},
                        {"x": 8823, "y": 20637},
                        {"x": 7849, "y": 21637},
                    ],
                    "closed": True,
                }
            ],
            "userdata": {"class": "a", "objectId": 40},
        },
        # Other shapes...
    ]

    return jsPolygon


## This updates the mouse tracker
@callback(
    Output("mousePos_disp", "children"), Input("osdViewerComponent", "curMousePosition")
)
def update_mouseCoords(curMousePosition):
    return (
        f'{int(curMousePosition["x"])},{int(curMousePosition["y"])}'
        if curMousePosition["x"] is not None
        else ""
    )


## Update the zoom state
@callback(
    Output("zoomLevel_disp", "children"), Input("osdViewerComponent", "zoomLevel")
)
def updateZoomLevel(currentZoom):
    return "{:.3f}".format(currentZoom)


## Update the viewportBounds display
@callback(
    Output("viewportBounds_disp", "children"),
    Input("osdViewerComponent", "viewportBounds"),
)
def update_viewportBounds(viewPortBounds):
    vp = viewPortBounds
    return (
        f'x:{int(vp["x"])} y:{int(vp["y"])} w:{int(vp["width"])} h:{int(vp["height"])}'
    )


# osdShapeData
@callback(Output("shapeDataTable", "rowData"), Input("osdShapeData_store", "data"))
def updateShapeDataTable(shapeData):
    ### The structure of the data stats with
    ##  array of actions
    ## Then need to parse the actions to get the itemList
    if not shapeData:
        return []

    flattened_data = []
    for shp in shapeData:
        flattened_data.append(convertPaperInstructions_toTableForm(shp))
    return flattened_data


@callback(Output("osdViewerComponent", "tileSources"), Input("imageSelect", "value"))
def update_imageSrc(tileSourceIdx):
    print("update_imageSrc called with:", tileSourceIdx)
    newTileSource = tileSourceDict[tileSourceIdx]
    return newTileSource


@callback(Output("tileSourceTable", "rowData"), Input("imageSelect", "value"))
def update_tileSourceTable(tileSourceIdx):
    tileSources = tileSourceDict[tileSourceIdx]
    if not isinstance(tileSources, list):
        tileSources = [tileSources]

    rowData = []
    for idx, source in enumerate(tileSources):
        if isinstance(source, str):
            rowData.append(
                {
                    "layer": idx,
                    "visible": True,  # Default to visible
                    "width": 1,  # Default scale
                    "height": 1,  # Default scale
                    "x": 0,
                    "y": 0,
                    "opacity": 1,
                    "rotation": 0,
                    "pixelWidth": 0,  # Will be updated when image loads
                    "pixelHeight": 0,  # Will be updated when image loads
                    "x_offset": 0,  # Will be calculated from x * pixelWidth
                    "y_offset": 0,  # Will be calculated from y * pixelHeight
                }
            )
        else:
            # Get the relative coordinates and image dimensions
            rel_x = source.get("x", 0)
            rel_y = source.get("y", 0)
            pixel_width = source.get("imageWidth", 0)
            pixel_height = source.get("imageHeight", 0)

            # Calculate pixel offsets using the correct dimensions
            x_offset = int(rel_x * pixel_width) if pixel_width else 0  # x uses width
            y_offset = int(rel_y * pixel_height) if pixel_height else 0  # y uses height

            rowData.append(
                {
                    "layer": idx,
                    "visible": source.get("visible", True),
                    "width": source.get("width", 1),
                    "height": source.get("height", 1),
                    "x": rel_x,  # Keep the relative coordinates for internal use
                    "y": rel_y,
                    "opacity": source.get("opacity", 1),
                    "rotation": source.get("rotation", 0),
                    "pixelWidth": pixel_width,
                    "pixelHeight": pixel_height,
                    "x_offset": x_offset,  # Add pixel-based offsets
                    "y_offset": y_offset,
                }
            )
    return rowData


# ### Detect changes in xOffset, yOffset, and opacity
@callback(
    Output("imgScrControls_data", "children"),
    Output("osdViewerComponent", "tileSourceProps"),
    Input("tileSourceTable", "cellValueChanged"),
    State("tileSourceTable", "rowData"),  # Add state to get all row data
)
def process_tileSource_changes(changes, all_row_data):
    if not changes:
        return no_update, no_update

    try:
        # Transform grid changes into tile source properties
        if isinstance(changes, list) and len(changes) > 0:
            # Get the most recent change
            change = changes[0]
            if isinstance(change, dict) and "data" in change:
                data = change["data"]
                if isinstance(data, dict):
                    # Get the layer index and ensure it's an integer
                    layer_idx = int(data.get("layer", 0))
                    print(f"Processing change for layer {layer_idx}")  # Debug log

                    # Create props for all layers to maintain their state
                    all_props = []
                    for row in all_row_data:
                        layer_data = row
                        original_opacity = float(layer_data.get("opacity", 1))
                        is_visible = bool(layer_data.get("visible", True))
                        pixel_width = float(layer_data.get("pixelWidth", 10000))
                        pixel_height = float(layer_data.get("pixelHeight", 8000))

                        # Convert pixel offsets back to relative coordinates
                        x_offset = float(layer_data.get("x_offset", 0))
                        y_offset = float(layer_data.get("y_offset", 0))
                        rel_x = x_offset / pixel_width if pixel_width else 0
                        rel_y = y_offset / pixel_height if pixel_height else 0

                        props = {
                            "index": int(layer_data.get("layer", 0)),
                            "x": rel_x,  # Use relative coordinates for OpenSeadragon
                            "y": rel_y,
                            "opacity": (
                                0 if not is_visible else original_opacity
                            ),  # Set opacity to 0 if not visible
                            "rotation": float(layer_data.get("rotation", 0)),
                            "visible": is_visible,
                            "width": float(layer_data.get("width", 1)),
                            "height": float(layer_data.get("height", 1)),
                        }
                        all_props.append(props)
                        print(f"Layer {props['index']} props: {props}")  # Debug log

                    return html.Div(), all_props
                else:
                    print("Unexpected data format:", data)
                    return no_update, no_update
            else:
                print("Unexpected change format:", change)
                return no_update, no_update
        else:
            print("Unexpected changes format:", changes)
            return no_update, no_update

    except Exception as e:
        print("Error processing tile source changes:", e)
        return no_update, no_update


@callback(
    Output("curObject_disp", "children"),
    Output("curObject_disp", "style"),
    Input("osdViewerComponent", "curShapeObject"),
)
def update_curShapeObject(curShapeObject):
    base_style = {
        "overflowY": "auto",
        "maxHeight": "2rem",
        "whiteSpace": "pre-wrap",
        "wordBreak": "break-all",
        "fontSize": "0.9em",
        "padding": "2px 4px",
        "backgroundColor": "rgba(0,0,0,0.02)",
        "borderRadius": "4px",
    }

    if curShapeObject:
        return json.dumps(curShapeObject.get("userdata", {})), base_style
    return "No object selected", base_style


@callback(Output("color_disp", "children"), Input("osdViewerComponent", "pixelColor"))
def update_color_display(color_data):
    if color_data:
        color_string = get_color_from_pixel(color_data)
        return html.Div(
            [
                html.Div(
                    style={
                        "backgroundColor": color_string,
                        "width": "15px",
                        "height": "15px",
                        "display": "inline-block",
                        "marginRight": "5px",
                        "border": "1px solid #ddd",
                    }
                ),
                html.Div(
                    [
                        html.Span(
                            color_string,
                            style={
                                "fontFamily": "monospace",
                                "marginRight": "5px",
                                "fontSize": "0.9em",
                            },
                        ),
                        html.Span(
                            f"({color_data['r']},{color_data['g']},{color_data['b']})",
                            style={
                                "color": "#666",
                                "fontSize": "0.8em",
                                "whiteSpace": "nowrap",
                            },
                        ),
                    ],
                    style={
                        "display": "inline-block",
                        "overflow": "hidden",
                        "textOverflow": "ellipsis",
                        "whiteSpace": "nowrap",
                        "maxWidth": "calc(100% - 25px)",  # Account for color swatch width
                    },
                ),
            ],
            style={
                "display": "flex",
                "alignItems": "center",
                "width": "100%",
                "height": "100%",
            },
        )
    return "No color selected"


def createItem(data):
    # cprint("createItem", data)
    # print("Some how called this?")
    x = get_box_instructions(
        data["point"]["x"],
        data["point"]["y"],
        data["size"]["width"],
        data["size"]["height"],
        colors[0],
        {"class": classes[0]},
    )
    out = {"actions": [{"type": "drawItems", "itemList": [x]}]}
    return out
    # return out


# this is if you want to trigger deleting and item from the python side
def deleteItem(id):
    output = {"actions": [{"type": "deleteItem", "id": id}]}
    return output


# this listens to a deletion event triggered from the client side
def itemDeleted(data):
    print("itemDeleted", data)
    return None


def propertyChanged(data):
    print("propertyChanged", data)
    return None


def mouseLeave(args):
    return None


def mouseEnter(args):
    # print(args)
    return None


def colorGrabbed(args):
    return None  # or handle the color grabbed event if needed


# Add a callback to update the annotation table when image selection changes
@callback(
    Output("annotationTable", "rowData"),
    Input("imageSelect", "value"),
)
def update_annotation_table(tileSourceIdx):
    print("update_annotation_table called with:", tileSourceIdx)
    if not tileSourceIdx:
        print("No tileSourceIdx provided")
        return []

    # Get the selected tile source
    tile_source = tileSourceDict[tileSourceIdx]
    if isinstance(tile_source, list):
        # For image stack, use the first source
        tile_source = tile_source[0]
        print("Using first source from image stack:", tile_source)

    # Extract API URL and item ID from the tile source URL
    if isinstance(tile_source, dict) and "tileSource" in tile_source:
        tile_url = tile_source["tileSource"]
        print("Processing tile URL:", tile_url)
        match = re.match(r"(.*api/v1)/item/(.*?)/tiles/dzi.dzi", tile_url)
        if match:
            api_url = match.group(1)
            item_id = match.group(2)
            print(f"Found API URL: {api_url}, Item ID: {item_id}")
            annotations = get_dsa_annotation_list(api_url, item_id)
            print(f"Found {len(annotations)} annotations")

            # Format the annotations for display
            formatted_annotations = []
            for ann in annotations:
                formatted_annotations.append(
                    {
                        "name": ann.get("name", ""),
                        "description": ann.get("description", ""),
                        "created": ann.get("created", ""),
                        "updated": ann.get("updated", ""),
                        "_id": ann.get("_id", ""),  # Add the _id field for selection
                    }
                )
            return formatted_annotations
        else:
            print("No match found in tile URL pattern")
    else:
        print("Invalid tile source format")

    return []


# Add callback to toggle the modal
@callback(
    Output("keybindings-modal", "is_open"),
    [
        Input("show-keybindings", "n_clicks"),
        Input("close-keybindings", "n_clicks"),
    ],
    [State("keybindings-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run_server(debug=True)
