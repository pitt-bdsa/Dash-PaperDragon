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
    calculate_shape_bounds,
)

from dashPaperDragon_defaultLayouts import coordinate_display
from dashPaperDragon_config import config
from sampleTileSources import tileSources, tileSourceDict


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


# # Initialize tileSourceDict with image dimensions


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
# tileSourceColumns = [
#     {"field": "layer", "headerName": "Layer", "width": 90},
#     {
#         "field": "visible",
#         "headerName": "Visible",
#         "width": 90,
#         "cellRenderer": "agCheckboxCellRenderer",
#         "editable": True,
#     },
#     {
#         "field": "x_offset",
#         "headerName": "X Offset (px)",
#         "width": 120,
#         "type": "numericColumn",
#         "editable": True,
#     },
#     {
#         "field": "y_offset",
#         "headerName": "Y Offset (px)",
#         "width": 120,
#         "type": "numericColumn",
#         "editable": True,
#     },
#     {
#         "field": "opacity",
#         "headerName": "Opacity",
#         "width": 100,
#         "type": "numericColumn",
#         "editable": True,
#         "valueFormatter": {"function": "params => params.value.toFixed(2)"},
#     },
#     {
#         "field": "rotation",
#         "headerName": "Rotation",
#         "width": 100,
#         "type": "numericColumn",
#         "editable": True,
#     },
#     {
#         "field": "pixelWidth",
#         "headerName": "Image Width",
#         "width": 120,
#         "type": "numericColumn",
#         "editable": False,
#         "valueFormatter": {
#             "function": "params => params.value.toLocaleString() + ' px'"
#         },
#     },
#     {
#         "field": "pixelHeight",
#         "headerName": "Image Height",
#         "width": 120,
#         "type": "numericColumn",
#         "editable": False,
#         "valueFormatter": {
#             "function": "params => params.value.toLocaleString() + ' px'"
#         },
#     },
# ]

# paperJsShapeColumns = [
#     {"field": "objectId", "headerName": "ID", "width": 70, "maxWidth": 70},
#     {"field": "type", "headerName": "Type", "width": 90},
#     {"field": "class", "headerName": "Class", "width": 80},
#     {"field": "fillColor", "headerName": "Color", "width": 90},
#     {
#         "field": "fillOpacity",
#         "headerName": "Opacity",
#         "width": 120,
#         "type": "numericColumn",
#         "editable": True,
#         "cellRenderer": "agSliderCellRenderer",
#         "cellRendererParams": {
#             "minValue": 0,
#             "maxValue": 1,
#             "step": 0.1,
#             "valueFormatter": {"function": "params => params.value.toFixed(2)"},
#         },
#     },
#     {"field": "x", "headerName": "X", "width": 80, "type": "numericColumn"},
#     {"field": "y", "headerName": "Y", "width": 80, "type": "numericColumn"},
#     {"field": "markerSize", "headerName": "Size", "width": 80, "type": "numericColumn"},
#     {"field": "markerColor", "headerName": "Marker Color", "width": 90},
# ]

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
        dbc.Modal(
            [
                dbc.ModalHeader("Add Tile Source"),
                dbc.ModalBody(
                    [
                        dbc.Form(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label("Select Sample Tile Source"),
                                                dbc.Select(
                                                    id="new-tile-source-select",
                                                    options=[
                                                        {
                                                            "label": src.get(
                                                                "label", f"Source {i}"
                                                            ),
                                                            "value": i,
                                                        }
                                                        for i, src in enumerate(
                                                            tileSources
                                                        )
                                                    ],
                                                    value=None,
                                                    className="mb-3",
                                                ),
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                dbc.ModalFooter(
                    [
                        dbc.Button(
                            "Close", id="close-tile-source-modal", className="me-2"
                        ),
                        dbc.Button("Add", id="add-tile-source", color="primary"),
                    ]
                ),
            ],
            id="tile-source-modal",
            is_open=False,
        ),
    ],
    fluid=True,
)
## End of layout

### OutputFromPaper needs to be cleared as well once the message/state has been acknowledged


## NEED TO CLEAR THE MESSAGE ONCE THE EVENT FIRES...
@callback(
    [
        Output("osdShapeData_store", "data"),
        Output("osdViewerComponent", "inputToPaper"),
    ],
    [
        Input("shapeDataTable", "cellRendererData"),
        Input("annotationTable", "selectedRows"),
        Input("make_random_button", "n_clicks"),
        Input("make_random_points_button", "n_clicks"),
        Input("global-opacity-slider", "value"),
        Input("shapeDataTable", "cellValueChanged"),
        Input("osdViewerComponent", "outputFromPaper"),
        Input("add-tile-source", "n_clicks"),
        Input("osdShapeData_store", "data"),
    ],
    [
        State("imageSelect", "value"),
        State("osdShapeData_store", "data"),
        State("osdViewerComponent", "viewportBounds"),
        State("clearItems-toggle", "value"),
        State("new-tile-source-select", "value"),
    ],
    prevent_initial_call=True,
)
def unified_callback(
    cell_renderer_data,
    annotation_selected_rows,
    make_random_boxesClicked,
    make_random_pointsClicked,
    global_opacity,
    cell_changes,
    paper_output,
    add_tile_source_clicks,
    shape_data_update,
    tileSourceIdx,
    current_shapes,
    viewPortBounds,
    clearItems,
    newTileSource,
):
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    print(f"triggered_id: {triggered_id}")
    # Handle zoom button click
    if triggered_id == "shapeDataTable":
        print(ctx.triggered)
        if ctx.triggered[0]["value"]["colId"] == "zoom":

            print("cell_renderer_data: ", cell_renderer_data, "is also set")
            if cell_renderer_data.get("colId") == "zoom":
                row_index = cell_renderer_data.get("rowIndex")
                if (
                    row_index is not None
                    and current_shapes
                    and len(current_shapes) > row_index
                ):
                    shape = current_shapes[row_index]
                    shape_id = shape["userdata"]["objectId"]
                    bounds = calculate_shape_bounds(current_shapes, shape_id)
                    if bounds:
                        return no_update, {
                            "actions": [{"type": "panToBounds", "bounds": bounds}]
                        }
            return no_update, no_update
        elif ctx.triggered[0]["value"] == "cellValueChanged":
            print("cell_changes: ", cell_changes, "is also set")
            # Handle individual shape opacity changes
            if triggered_id == "shapeDataTable" and cell_changes:
                try:
                    change = cell_changes[0]
                    if not isinstance(change, dict) or "data" not in change:
                        return no_update, no_update

                    data = change["data"]
                    if "fillOpacity" not in data:
                        return no_update, no_update

                    shape_id = data.get("objectId")
                    new_opacity = float(data.get("fillOpacity", 0.2))

                    updated_shapes = []
                    for shape in current_shapes:
                        if shape["userdata"]["objectId"] == shape_id:
                            if "args" in shape and len(shape["args"]) > 0:
                                shape["args"][0]["fillOpacity"] = new_opacity
                        updated_shapes.append(shape)

                    return updated_shapes, {
                        "actions": [
                            {"type": "clearItems"},
                            {"type": "drawItems", "itemList": updated_shapes},
                        ]
                    }

                except Exception as e:
                    print(f"Error updating shape opacity: {e}")
                    return no_update, no_update

    # Handle tile source addition
    if (
        triggered_id == "add-tile-source"
        and add_tile_source_clicks
        and newTileSource is not None
    ):
        print(f"\nAdding tile source {newTileSource} to viewer")
        selected_source = tileSources[int(newTileSource)]
        return no_update, {
            "actions": [{"type": "addTileSource", "source": selected_source}]
        }

    # Handle shape data store changes
    if triggered_id == "osdShapeData_store":
        if not shape_data_update:
            return no_update, no_update
        return no_update, {
            "actions": [{"type": "drawItems", "itemList": shape_data_update}]
        }

    # Handle paper events (shape creation, deletion, etc.)
    if triggered_id == "osdViewerComponent":
        if not paper_output:
            return no_update, no_update

        osdEventType = paper_output.get("data", {}).get("callback", None)
        if not osdEventType:
            osdEventType = paper_output.get("callback", None)

        if osdEventType == "grabColor":
            return no_update, {"actions": [{"type": "getColor"}]}
        elif osdEventType in ["mouseLeave", "mouseEnter", "colorGrabbed"]:
            return no_update, no_update

        # Handle shape creation
        if osdEventType == "createItem":
            data = paper_output.get("data", {})
            new_shape = get_box_instructions(
                data["point"]["x"],
                data["point"]["y"],
                data["size"]["width"],
                data["size"]["height"],
                colors[0],
                {"class": classes[0], "objectId": getId()},
            )
            updated_shapes = (
                current_shapes + [new_shape] if not clearItems else [new_shape]
            )
            return updated_shapes, {
                "actions": [
                    {"type": "clearItems"},
                    {"type": "drawItems", "itemList": updated_shapes},
                ]
            }

        # Handle property changes
        elif osdEventType == "propertyChanged":
            changedProp = paper_output.get("data", {}).get("property", "")
            if changedProp == "class":
                newClass = paper_output.get("data", {}).get("item", {}).get("class", "")
                objectId = (
                    paper_output.get("data", {}).get("item", {}).get("objectId", "")
                )
                updated_shapes = []
                for shape in current_shapes:
                    if shape["userdata"]["objectId"] == objectId:
                        shape["userdata"]["class"] = newClass
                    updated_shapes.append(shape)
                return updated_shapes, no_update

        # Handle item deletion
        elif osdEventType == "itemDeleted":
            try:
                itemId = paper_output["data"]["item"][1]["data"]["userdata"]["objectId"]
                updated_shapes = [
                    shape
                    for shape in current_shapes
                    if shape["userdata"]["objectId"] != itemId
                ]
                return updated_shapes, no_update
            except Exception as e:
                print(f"Error handling item deletion: {e}")
                return no_update, no_update

    # Handle global opacity changes
    elif triggered_id == "global-opacity-slider":
        if global_opacity is None:
            return no_update, no_update

        try:
            updated_shapes = []
            for shape in current_shapes:
                if "args" in shape and len(shape["args"]) > 0:
                    shape["args"][0]["fillOpacity"] = global_opacity
                updated_shapes.append(shape)
            return updated_shapes, {
                "actions": [
                    # {"type": "clearItems"},
                    {"type": "drawItems", "itemList": updated_shapes},
                ]
            }

        except Exception as e:
            print(f"Error updating global opacity: {e}")
            return no_update, no_update

    # Handle annotation selection
    elif triggered_id == "annotationTable":
        if not annotation_selected_rows or not tileSourceIdx:
            return no_update, no_update

        # ... rest of annotation handling code ...

    # Handle random shape generation
    if triggered_id == "make_random_button":
        new_shapes = generate_random_boxes(3, viewPortBounds, classes, colors)
        # Add to current shapes or replace, depending on clearItems
        updated_shapes = current_shapes + new_shapes if not clearItems else new_shapes
        return updated_shapes, {
            "actions": [
                {"type": "clearItems"},
                {"type": "drawItems", "itemList": updated_shapes},
            ]
        }

    elif triggered_id == "make_random_points_button":
        new_shapes = generate_random_points(3, viewPortBounds, classes, colors)
        updated_shapes = current_shapes + new_shapes if not clearItems else new_shapes
        return updated_shapes, {
            "actions": [
                {"type": "clearItems"},
                {"type": "drawItems", "itemList": updated_shapes},
            ]
        }

    return no_update, no_update


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
    print(f"update_tileSourceTable called with: {tileSourceIdx}")
    tileSources = tileSourceDict[tileSourceIdx]
    if not isinstance(tileSources, list):
        tileSources = [tileSources]

    rowData = []
    for idx, source in enumerate(tileSources):
        print(f"Processing tile source {idx}: {source}")

        if isinstance(source, str):
            rowData.append(
                {
                    "layer": idx,
                    "visible": True,
                    "width": 1,
                    "height": 1,
                    "x": 0,
                    "y": 0,
                    "opacity": 1,
                    "rotation": 0,
                    "pixelWidth": 10000,  # Default width if not specified
                    "pixelHeight": 8000,  # Default height if not specified
                    "x_offset": 0,
                    "y_offset": 0,
                }
            )
        else:
            # Extract API URL and item ID from the tile source URL
            tile_url = source.get("tileSource", "")
            match = re.match(r"(.*api/v1)/item/(.*?)/tiles/dzi.dzi", tile_url)

            # Get image dimensions from DSA if possible
            pixel_width = 10000  # Default width
            pixel_height = 8000  # Default height

            if match:
                api_url = match.group(1)
                item_id = match.group(2)
                print(
                    f"Fetching metadata from DSA - API URL: {api_url}, Item ID: {item_id}"
                )

                # Get image dimensions from DSA
                metadata = get_dsa_image_metadata(api_url, item_id)
                pixel_width = float(metadata.get("width", 10000))
                pixel_height = float(metadata.get("height", 8000))
                print(
                    f"Retrieved dimensions from DSA - width: {pixel_width}, height: {pixel_height}"
                )
            else:
                # Use dimensions from source if available
                pixel_width = float(source.get("imageWidth", 10000))
                pixel_height = float(source.get("imageHeight", 8000))

            # Get the relative coordinates
            rel_x = float(source.get("x", 0))
            rel_y = float(source.get("y", 0))

            # Calculate pixel offsets
            x_offset = rel_x * pixel_width
            y_offset = rel_y * pixel_height

            print(f"Dimensions - width: {pixel_width}, height: {pixel_height}")
            print(f"Relative coords - x: {rel_x}, y: {rel_y}")
            print(f"Pixel offsets - x: {x_offset}, y: {y_offset}")

            rowData.append(
                {
                    "layer": idx,
                    "visible": source.get("visible", True),
                    "width": source.get("width", 1),
                    "height": source.get("height", 1),
                    "x": rel_x,
                    "y": rel_y,
                    "opacity": source.get("opacity", 1),
                    "rotation": source.get("rotation", 0),
                    "pixelWidth": pixel_width,
                    "pixelHeight": pixel_height,
                    "x_offset": x_offset,
                    "y_offset": y_offset,
                }
            )

            print(f"Added row data: {rowData[-1]}")

    return rowData


# ### Detect changes in xOffset, yOffset, and opacity
@callback(
    Output("osdViewerComponent", "tileSourceProps"),
    Input("tileSourceTable", "cellValueChanged"),
    State("tileSourceTable", "rowData"),  # Add state to get all row data
)
def process_tileSource_changes(changes, all_row_data):
    if not changes:
        return no_update

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
                    # Get the field that was changed
                    changed_field = change.get("colId", "")
                    print(
                        f"Processing change for layer {layer_idx}, field: {changed_field}"
                    )  # Debug log

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

                        # Start with basic props that are always included
                        props = {
                            "index": int(layer_data.get("layer", 0)),
                            "x": rel_x,  # Use relative coordinates for OpenSeadragon
                            "y": rel_y,
                            "opacity": (
                                0 if not is_visible else original_opacity
                            ),  # Set opacity to 0 if not visible
                            "rotation": float(layer_data.get("rotation", 0)),
                            "visible": is_visible,
                        }

                        # Only include width/height if they were explicitly changed
                        if changed_field == "width":
                            props["width"] = float(layer_data.get("width", 1))
                        if changed_field == "height":
                            props["height"] = float(layer_data.get("height", 1))

                        all_props.append(props)
                        print(f"Layer {props['index']} props: {props}")  # Debug log

                    return all_props
                else:
                    print("Unexpected data format:", data)
                    return no_update
            else:
                print("Unexpected change format:", change)
                return no_update
        else:
            print("Unexpected changes format:", changes)
            return no_update

    except Exception as e:
        print("Error processing tile source changes:", e)
        return no_update


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


@callback(
    Output("tile-source-modal", "is_open"),
    [
        Input("open-tile-source-modal", "n_clicks"),
        Input("close-tile-source-modal", "n_clicks"),
        Input("add-tile-source", "n_clicks"),
        Input("new-tile-source-select", "value"),
    ],
    [State("tile-source-modal", "is_open")],
)
def toggle_modal(n1, n2, n3, newTileSource, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return is_open

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if triggered_id == "add-tile-source" and newTileSource is not None:
        print("\nAdding new tile source:")
        print("Selected index:", newTileSource)
        print("Full tile source data:", tileSources[newTileSource])
        print("Current tile source dictionary:", tileSourceDict)

    if n1 or n2 or n3:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run_server(debug=True)
