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


tileSources = [
    {
        "label": "TCGA-2J-AAB4",
        "value": 0,
        "tileSources": [
            {
                "tileSource": "https://api.digitalslidearchive.org/api/v1/item/5b9f0d63e62914002e9547f0/tiles/dzi.dzi",
            }
        ],
    },
    {
        "label": "TCGA-BF-A1Q0-01A-02-TSB",
        "value": 0,
        "tileSources": [
            {
                "tileSource": "https://api.digitalslidearchive.org/api/v1/item/5b9f10a8e62914002e956509/tiles/dzi.dzi",
            }
        ],
    },
    {
        "label": "TCGA-2J-AAB4-01Z-00-DX1",
        "value": 1,
        "tileSources": [
            {
                "tileSource": "https://api.digitalslidearchive.org/api/v1/item/5b9f0d64e62914002e9547f4/tiles/dzi.dzi",
            }
        ],
    },
    {
        "label": "Image stack",
        "value": 2,
        "tileSources": [
            {
                "tileSource": "https://api.digitalslidearchive.org/api/v1/item/5b9f0d64e62914002e9547f4/tiles/dzi.dzi",
                "x": 0,
                "y": 0,
                "opacity": 1,
                "layerIdx": 0,
            },
            {
                "tileSource": "https://api.digitalslidearchive.org/api/v1/item/5b9f0d64e62914002e9547f4/tiles/dzi.dzi",
                "x": 0.2,
                "y": 0.2,
                "opacity": 0.2,
                "layerIdx": 1,
            },
        ],
    },
    {
        "label": "CDG Example",
        "value": 2,
        "tileSources": {
            "type": "image",
            "url": "https://api.digitalslidearchive.org/api/v1/item/5b9f0d64e62914002e9547f4/tiles/dzi.dzi",
            "crossOriginPolicy": "Anonymous",
            "ajaxWithCredentials": False,
            "x": 0,
            "y": 0,
            "opacity": 1,
            "layerIdx": 0,
        },
    },
    {
        "label": "ISIC Example",
        "value": 3,
        "tileSources": [
            {
                "type": "image",
                "url": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767e2309a9ffde668be5e/tiles/dzi.dzi",
                "crossOriginPolicy": "Anonymous",
                "ajaxWithCredentials": False,
            },
            {
                "type": "image",
                "url": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767e4309a9ffde668be70/tiles/dzi.dzi",
                "crossOriginPolicy": "Anonymous",
                "ajaxWithCredentials": False,
            },
            {
                "type": "image",
                "url": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767e4309a9ffde668be73/tiles/dzi.dzi",
                "crossOriginPolicy": "Anonymous",
                "ajaxWithCredentials": False,
            },
            {
                "type": "image",
                "url": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767e1309a9ffde668be4f/tiles/dzi.dzi",
                "crossOriginPolicy": "Anonymous",
                "ajaxWithCredentials": False,
            },
            {
                "type": "image",
                "url": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767e1309a9ffde668be58/tiles/dzi.dzi",
                "crossOriginPolicy": "Anonymous",
                "ajaxWithCredentials": False,
            },
            {
                "type": "image",
                "url": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767e0309a9ffde668be46/tiles/dzi.dzi",
                "crossOriginPolicy": "Anonymous",
                "ajaxWithCredentials": False,
            },
            {
                "type": "image",
                "url": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767df309a9ffde668be43/tiles/dzi.dzi",
                "crossOriginPolicy": "Anonymous",
                "ajaxWithCredentials": False,
            },
            {
                "type": "image",
                "url": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767ce309a9ffde668bd77/tiles/dzi.dzi",
                "crossOriginPolicy": "Anonymous",
                "ajaxWithCredentials": False,
            },
            {
                "type": "image",
                "url": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767ce309a9ffde668bd7a/tiles/dzi.dzi",
                "crossOriginPolicy": "Anonymous",
                "ajaxWithCredentials": False,
            },
            {
                "type": "image",
                "url": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767e1309a9ffde668be52/tiles/dzi.dzi",
                "crossOriginPolicy": "Anonymous",
                "ajaxWithCredentials": False,
            },
        ],
    },
]

tileSourceDict = {x["label"]: x["tileSources"] for x in tileSources}


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


def convertPaperInstructions_toTableForm(data):
    print("Converting data:", data)  # Debug print
    args = data.get("args", [])
    if args:
        args = args[0]

    if data["paperType"] == "Path.Rectangle":
        flattened_data = {
            "objectId": data["userdata"]["objectId"],
            "fillOpacity": args["fillOpacity"],
            "fillColor": args["fillColor"],
            "class": data["userdata"]["class"],
            "strokeColor": args["strokeColor"],
            "rotation": args.get(
                "rotation"
            ),  # Use .get() to avoid KeyError if 'rotation' is not present
            "x": args["point"]["x"],
            "y": args["point"]["y"],
            "width": args["size"]["width"],
            "height": args["size"]["height"],
            "type": "Rectangle",
        }
        return flattened_data
    elif data["paperType"] == "Path":
        # Handle points
        segments = args.get("segments", [])
        if not segments:
            print("No segments found")  # Debug print
            return None

        point = segments[0].get("point", {})
        print("Point data:", point)  # Debug print

        flattened_data = {
            "objectId": data["userdata"]["objectId"],
            "type": "Point",
            "fillOpacity": 1,
            "fillColor": args.get("fillColor", ""),
            "class": data["userdata"]["class"],
            "strokeColor": args.get("strokeColor", ""),
            "x": point.get("x"),
            "y": point.get("y"),
            "width": args.get("strokeWidth", 1000),
            "height": args.get("strokeWidth", 1000),
        }
        print("Flattened data:", flattened_data)  # Debug print
        return flattened_data
    ## TO DO: process segments


# First, define the column definitions
tileSourceColumns = [
    {"field": "layer", "headerName": "Layer", "width": 70, "maxWidth": 70},
    {
        "field": "visible",
        "headerName": "Visible",
        "width": 80,
        "cellRenderer": "agCheckboxCellRenderer",
        "editable": True,
    },
    {
        "field": "width",
        "headerName": "Width",
        "width": 80,
        "type": "numericColumn",
        "editable": True,
    },
    {
        "field": "height",
        "headerName": "Height",
        "width": 80,
        "type": "numericColumn",
        "editable": True,
    },
    {
        "field": "x",
        "headerName": "X",
        "width": 80,
        "type": "numericColumn",
        "editable": True,
    },
    {
        "field": "y",
        "headerName": "Y",
        "width": 80,
        "type": "numericColumn",
        "editable": True,
    },
    {
        "field": "opacity",
        "headerName": "Opacity",
        "width": 90,
        "type": "numericColumn",
        "editable": True,
        "valueFormatter": "value.toFixed(2)",
    },
    {
        "field": "rotation",
        "headerName": "Rot",
        "width": 70,
        "type": "numericColumn",
        "editable": True,
    },
]

paperJsShapeColumns = [
    {"field": "objectId", "headerName": "ID", "width": 70, "maxWidth": 70},
    {"field": "type", "headerName": "Type", "width": 90},
    {"field": "fillOpacity", "headerName": "Fill %", "width": 80},
    {"field": "fillColor", "width": 90},
    {"field": "class", "width": 80},
    {"field": "x", "width": 80, "type": "numericColumn"},
    {"field": "y", "width": 80, "type": "numericColumn"},
    {"field": "width", "width": 80, "type": "numericColumn"},
    {"field": "height", "width": 80, "type": "numericColumn"},
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
                                html.Div(id="curObject_disp", className="card-text"),
                            ]
                        ),
                        className="mb-1",
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
                                                "height": "200px",  # Fixed height
                                                "width": "100%",
                                            },
                                            dashGridOptions={
                                                "rowHeight": 35,
                                                "headerHeight": 35,
                                                "enableCellTextSelection": True,
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
    ],
    className="no-right-margin g-0",
)


imageSelect_dropdown = html.Div(
    [
        html.Label(
            "Select an image",
            className="text-center mb-3",
            style={"margin-top": "5px", "margin-right": "5px"},
        ),  # "margin-bottom": "5px
        dbc.Select(
            id="imageSelect",
            options=[x["label"] for x in tileSources],
            value=tileSources[0]["label"],
            className="mb-4 d-inline",
            style={"width": "300px", "marginLleft": "10px", "marginTop": "1px"},
        ),
        dbc.Button(
            "Make Random Rects",
            id="make_random_button",
            className="m-1 d-inline",
            style={"marginLeft": "10px", "height": "40px"},  # , "marginTop": "15px"},
        ),
        dbc.Button(
            "Make Random Points",
            id="make_random_points_button",
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
    style={"display": "flex", "flex-direction": "row", "align": "center"},
)


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
    ],
    fluid=True,
)
## End of layout

### OutputFromPaper needs to be cleared as well once the message/state has been acknowledged


## NEED TO CLEAR THE MESSAGE ONCE THE EVENT FIRES...
@callback(
    Output("osdViewerComponent", "inputToPaper", allow_duplicate=True),
    Output("osdShapeData_store", "data"),
    Output("osdViewerComponent", "outputFromPaper"),
    Input("osdViewerComponent", "outputFromPaper"),
    Input("make_random_button", "n_clicks"),
    Input("make_random_points_button", "n_clicks"),
    State("osdViewerComponent", "viewportBounds"),
    State("osdShapeData_store", "data"),
    State("clearItems-toggle", "value"),
    prevent_initial_call=True,
)
def handleOutputFromPaper(
    paperOutput,
    make_random_boxesClicked,
    make_random_pointsClicked,
    viewPortBounds,
    currentShapeData,
    clearItems,
):
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update, {}

    triggered_prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if triggered_prop_id == "osdViewerComponent":
        osdEventType = paperOutput.get("data", {}).get("callback", None)
        if not osdEventType:
            osdEventType = paperOutput.get("callback", None)

        if osdEventType == "grabColor":
            # Changed from sampleColor to getColor
            return {"actions": [{"type": "getColor"}]}, no_update, {}
        elif osdEventType == "colorGrabbed":
            # Handle the grabbed color data
            print("Color grabbed:", paperOutput.get("data", {}).get("color"))
            return no_update, no_update, {}
        elif osdEventType in ["mouseLeave", "mouseEnter"]:
            # print("MOUSE ENTER TRIGGERED")
            # print(paperOutput)  # curObject_disp
            return no_update, no_update, {}
        elif osdEventType == "createItem":
            # print(paperOutput["data"])

            si = get_box_instructions(
                paperOutput["data"]["point"]["x"],
                paperOutput["data"]["point"]["y"],
                paperOutput["data"]["size"]["width"],
                paperOutput["data"]["size"]["height"],
                colors[0],
                {"class": classes[0]},
            )
            currentShapeData.append(si)

            return createItem(paperOutput["data"]), currentShapeData, {}
        elif osdEventType == "propertyChanged":
            ### Handle property change.. probably class change but could be color or other thing in the future
            # print(paperOutput["data"])
            # print(changedProp, "is the changedProp")
            ## TO DO--- THIS IS NOT CONSISTENTLY FIRING ON EVERY CHANGE..

            changedProp = paperOutput.get("data", {}).get("property", "")
            if changedProp == "class":
                newClass = paperOutput.get("data", {}).get("item", {}).get("class", "")
                objectId = (
                    paperOutput.get("data", {}).get("item", {}).get("objectId", "")
                )
                for r in currentShapeData:
                    if r["userdata"]["objectId"] == objectId:
                        r["userdata"]["class"] = newClass
                        print("Changed object class to", newClass)
                        break
                return no_update, currentShapeData, {}
        elif osdEventType == "itemDeleted":
            print(paperOutput["data"]["item"])
            itemId = paperOutput["data"]["item"][1]["data"]["userdata"]["objectId"]
            print("Item Deleted", itemId)
            currentShapeData = [
                x for x in currentShapeData if x["userdata"]["objectId"] != itemId
            ]
            return no_update, currentShapeData, {}
            ### TO DO-- CLARIFY FROM TOM WHAT THE DELETEITEM callback should return in the react component

            ## Note the class is changing, but that also changes the color... will need to think about how to keep all this stuff in sync
        else:
            print("Unhandled osdEventType", osdEventType)
            print(paperOutput, "is the paperOutput")

    elif triggered_prop_id in ["make_random_button", "make_random_points_button"]:
        if triggered_prop_id == "make_random_button":
            shapesToAdd = generate_random_boxes(3, viewPortBounds)
        else:
            shapesToAdd = generate_random_points(3, viewPortBounds)

        inputToPaper = {"actions": []}

        if clearItems:
            inputToPaper["actions"].append({"type": "clearItems"})
            inputToPaper["actions"].append(
                {"type": "drawItems", "itemList": shapesToAdd}
            )
            return inputToPaper, shapesToAdd, {}
        else:
            inputToPaper["actions"].append(
                {"type": "drawItems", "itemList": shapesToAdd}
            )
            currentShapeData = currentShapeData + shapesToAdd
            return inputToPaper, currentShapeData, {}

    else:
        print(triggered_prop_id, "was the triggered prop")

    return no_update, no_update, {}


def get_box_instructions(x, y, w, h, color, userdata={}):
    props = config.get("defaultStyle") | {
        "point": {"x": x, "y": y},
        "size": {"width": w, "height": h},
        "fillColor": color,
        "strokeColor": color,
    }
    userdata["objectId"] = getId()
    command = {"paperType": "Path.Rectangle", "args": [props], "userdata": userdata}

    return command


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


def generate_random_boxes(num_points, bounds):
    out = []

    x = int(bounds["x"])
    w = int(bounds["width"])
    y = int(bounds["y"])
    h = int(bounds["height"])

    for idx, _ in enumerate(range(num_points)):
        className, color = random.choice(list(zip(classes, colors)))
        # color = random.choice(colors)
        userdata = {"class": className}

        bx = random.randint(x, x + w)
        by = random.randint(y, y + h)
        bw = random.randint(int(w / 150), int(w / 50))
        bh = random.randint(int(h / 150), int(h / 50))
        instructions = get_box_instructions(bx, by, bw, bh, color, userdata)

        out.append(instructions)

    return out


def generate_random_points(num_points, bounds):
    out = []

    x = int(bounds["x"])
    w = int(bounds["width"])
    y = int(bounds["y"])
    h = int(bounds["height"])

    for _ in range(num_points):
        className, color = random.choice(list(zip(classes, colors)))
        userdata = {"class": className, "objectId": getId()}

        px = random.randint(x, x + w)
        py = random.randint(y, y + h)

        instructions = {
            "paperType": "Path",
            "args": [
                {
                    "segments": [{"point": {"x": px, "y": py}}],
                    "strokeColor": color,
                    "strokeWidth": 1000,  # Much bigger
                    "fillColor": color,
                }
            ],
            "userdata": userdata,
        }
        out.append(instructions)

    return out


## This call back will get fairly complicated as it not only handled objects created in python
## but also objects created in the paperjs side
# @callback(
#     Output("osdViewerComponent", "inputToPaper"), Input("osdShapeData_store", "data")
# )
# def update_osdShapeData_store(data):
#     ## This may not always update openseadragon depending on what changes occurred

#     return data


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


def get_color_from_pixel(color_data):
    """Convert RGB values to hex color string"""
    if color_data:
        r = color_data.get("r", 0)
        g = color_data.get("g", 0)
        b = color_data.get("b", 0)
        return f"#{r:02x}{g:02x}{b:02x}"
    return "#000000"


# Update the tile source properties display function
def generateImgSrcControlPanel(tileSource, idx):
    if isinstance(tileSource, str):
        tileSource = {
            "tileSource": tileSource,
            "x": 0,
            "y": 0,
            "opacity": 1,
            "rotation": 0,
        }

    return dash_ag_grid.AgGrid(
        id={"type": "tileSource-grid", "index": idx},
        columnDefs=tileSourceColumns,
        rowData=[
            {
                "layer": idx,
                "x": tileSource.get("x", 0),
                "y": tileSource.get("y", 0),
                "opacity": tileSource.get("opacity", 1),
                "rotation": tileSource.get("rotation", 0),
            }
        ],
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "filter": True,
        },
        style={"height": "52px"},  # Just enough for one row
        dashGridOptions={"domLayout": "autoHeight"},
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
                }
            )
        else:
            rowData.append(
                {
                    "layer": idx,
                    "visible": source.get(
                        "visible", True
                    ),  # Get existing visibility or default to True
                    "width": source.get(
                        "width", 1
                    ),  # Get existing width or default to 1
                    "height": source.get(
                        "height", 1
                    ),  # Get existing height or default to 1
                    "x": source.get("x", 0),
                    "y": source.get("y", 0),
                    "opacity": source.get("opacity", 1),
                    "rotation": source.get("rotation", 0),
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

                        props = {
                            "index": int(layer_data.get("layer", 0)),
                            "x": float(layer_data.get("x", 0)),
                            "y": float(layer_data.get("y", 0)),
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
    Output("curObject_disp", "children"), Input("osdViewerComponent", "curShapeObject")
)
def update_curShapeObject(curShapeObject):
    if curShapeObject:
        return json.dumps(curShapeObject.get("userdata", {}))
    else:
        return no_update


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


if __name__ == "__main__":
    app.run_server(debug=True)


# Create a callback to update the opacity property when the slider value changes
# @callback(
#     [Output({'type': 'slider', 'index': i}, 'value') for i in range(len(data))],
#     [Input({'type': 'slider', 'index': i}, 'value') for i in range(len(data))]
# )
# def update_opacity(*slider_values):
#     print(slider_values)
#     return slider_values


# inputToPaper = {}  ## this will be an array of commands to send to paper if needed

# if paperOutput is None:
#     paperOutput = {}

# callback = callbacks.get(paperOutput.get("callback"))

# if callback and paperOutput.get("callback"):
#     inputToPaper = callback(paperOutput.get("data"))
#     ### Not sure if I need to append this..
#     ## If action type is drawItems than I need to append to the currentShapeData
#     if inputToPaper.get("actions")[0].get("type") == "drawItems":
#         currentShapeData.append(inputToPaper["actions"][0]["itemList"])
#         # print("CSD-->", currentShapeData)
#         return inputToPaper, currentShapeData
#         # inputToShapreDataStore = currentShapeData

#     # currentShapeData.append()

# if make_random_boxesClicked and not paperOutput.get("callback"):
#     # bounds = paperOutput.get("viewportBounds")
#     shapesToAdd = generate_random_boxes(3, viewPortBounds)

#     # shapesToAdd = generate_paperjs_polygon("tbd")
#     # print(shapesToAdd)

#     # print(shapesToAdd)
#     return inputToPaper, shapesToAdd

# ### Need to interrogate the inputToPaper object and see if I need to update the data store

# # print("ITP", inputToPaper, "PO:", paperOutput)
# return inputToPaper, no_update
