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
import dashPaperDragonHelpers as hlprs
import requests


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
        "label": "TCGA-BF-A1Q0-01A-02-TSB",
        "value": 0,
        "tileSources": "https://api.digitalslidearchive.org/api/v1/item/5b9f10a8e62914002e956509/tiles/dzi.dzi",
    },
    {
        "label": "TCGA-2J-AAB4",
        "value": 0,
        "tileSources": "https://api.digitalslidearchive.org/api/v1/item/5b9f0d63e62914002e9547f0/tiles/dzi.dzi",
    },
    {
        "label": "TCGA-2J-AAB4-01Z-00-DX1",
        "value": 1,
        "tileSources": [
            "https://api.digitalslidearchive.org/api/v1/item/5b9f0d64e62914002e9547f4/tiles/dzi.dzi"
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
        "tileSources": [
            {
                "tileSource": "https://api.digitalslidearchive.org/api/v1/item/5b9f0d64e62914002e9547f4/tiles/dzi.dzi",
                "x": 0,
                "y": 0,
                "opacity": 1,
                "layerIdx": 0,
            }
        ],
    },
    {
        "label": "ISIC Example",
        "value": 3,
        "tileSources": [
            {
                "tileSource": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767e2309a9ffde668be5e/tiles/dzi.dzi"
            },
            {
                "tileSource": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767e4309a9ffde668be70/tiles/dzi.dzi"
            },
            {
                "tileSource": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767e4309a9ffde668be73/tiles/dzi.dzi"
            },
            {
                "tileSource": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767e1309a9ffde668be4f/tiles/dzi.dzi"
            },
            {
                "tileSource": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767e1309a9ffde668be58/tiles/dzi.dzi"
            },
            {
                "tileSource": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767e0309a9ffde668be46/tiles/dzi.dzi"
            },
            {
                "tileSource": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767df309a9ffde668be43/tiles/dzi.dzi"
            },
            {
                "tileSource": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767ce309a9ffde668bd77/tiles/dzi.dzi"
            },
            {
                "tileSource": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767ce309a9ffde668bd7a/tiles/dzi.dzi"
            },
            {
                "tileSource": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767e1309a9ffde668be52/tiles/dzi.dzi"
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
        {"event": "keyDown", "key": "e", "action": "editItem", "tool": "rectangle"},
        {"event": "mouseEnter", "action": "dashCallback", "callback": "mouseEnter"},
        {"event": "mouseLeave", "action": "dashCallback", "callback": "mouseLeave"},
    ],
    "callbacks": [
        {"eventName": "item-created", "callback": "createItem"},
        {"eventName": "property-changed", "callback": "propertyChanged"},
        {"eventName": "item-deleted", "callback": "itemDeleted"},
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


callbacks = {
    "createItem": cbCreateItem,
    "itemDeleted": cbItemDeleted,
    "mouseEnter": cbMouseEnter,
    "mouseLeave": cbMouseLeave,
    "propertyChanged": cbPropertyChanged,
}


geoJsonShapeColumns = [
    {"field": "userdata.objId", "headerName": "objId", "width": 80, "sortable": True},
    {"field": "userdata.class", "width": 80},
    {"field": "type", "headerName": "Type", "width": 120},
    {"field": "properties.fillOpacity", "headerName": "fill %", "width": 80},
    {"field": "properties.strokeColor"},
    {"field": "properties.fillColor", "width": 100},
    {"field": "rotation"},
]


annotationTableCols = [
    {"field": "annotation.name"},
    {"field": "_version"},
    {"field": "updated"},
    {"field": "_id"},
]

dsaAnnotation_table = dash_ag_grid.AgGrid(
    id="annotationTable",
    columnDefs=annotationTableCols,
    columnSizeOptions={"defaultMaxWidth": 200},
    # columnSize="sizeToFit",
    defaultColDef={
        "resizable": True,
        "sortable": True,
        "defaultMaxWidth": 150,
    },
    dashGridOptions={
        "pagination": True,
        "paginationAutoPageSize": True,
        "rowSelection": "single",
    },
    style={"height": "300px"},
)


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
)

## Make HTML layout
coordinate_display = html.Div(
    [
        dbc.Row([dbc.Col(html.H2("Zoom and Mouse Position"), className="mb-2")]),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H5("Zoom Level", className="card-title"),
                                    html.Div(
                                        id="zoomLevel_disp", className="card-text"
                                    ),
                                ]
                            )
                        ],
                        className="mb-1",
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H5("Viewport Bounds", className="card-title"),
                                    html.Div(
                                        id="viewportBounds_disp", className="card-text"
                                    ),
                                ]
                            )
                        ],
                        className="mb-1",
                    ),
                    width=8,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H6("Mouse Position", className="card-title"),
                                    html.Div(id="mousePos_disp", className="card-text"),
                                ]
                            )
                        ],
                        className="img-control-grid",
                        style={"height": "3.5rem"},
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H6(
                                        "Highlighted Object", className="card-title"
                                    ),
                                    html.Div(
                                        id="curObject_disp", className="card-text"
                                    ),
                                ]
                            )
                        ],
                        className="mb-1 img-control-card",
                    ),
                    width=8,
                ),
            ]
        ),
        dbc.Row(
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5("Tile Source Properties", className="card-title"),
                            html.Div(id="osdTileProperties", className="card-text"),
                            html.Div(id="imgScrControls_data", className="card-text"),
                        ]
                    )
                ],
                className="img-control-card",
            )
        ),
        dbc.Row(
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5("Shape Table", className="card-title text-center"),
                            dash_ag_grid.AgGrid(
                                id="shapeDataTable",
                                columnDefs=geoJsonShapeColumns,
                                columnSizeOptions={"defaultMaxWidth": 200},
                                # columnSize="sizeToFit",
                                defaultColDef={
                                    "resizable": True,
                                    "sortable": True,
                                    "defaultMaxWidth": 150,
                                },
                                style={"height": "300px"},
                            ),
                        ],
                        style={
                            "margin": "0px",
                            "padding": "0px",
                            "margin-bottom": "10px",
                            # "height": "200px",
                        },
                    )
                ],
                className="img-control-card",
                style={"height": "300px"},
            )
        ),
        dbc.Row(
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5(
                                "Annotation Table", className="card-title text-center"
                            ),
                            dsaAnnotation_table,
                        ],
                        style={
                            "margin": "0px",
                            "padding": "0px",
                            "margin-bottom": "10px",
                        },
                    )
                ],
                className="img-control-card",
                style={"height": "100px"},
            )
        ),
    ],
    className=" g-0",
    # style={"display": "flex", "flex-direction": "row"},
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
    State("osdViewerComponent", "viewportBounds"),
    State("osdShapeData_store", "data"),
    State("clearItems-toggle", "value"),
    Input("annotationTable", "selectedRows"),
    prevent_initial_call=True,
)
def handleOutputFromPaper(
    paperOutput,
    make_random_boxesClicked,
    viewPortBounds,
    currentShapeData,
    clearItems,
    selectedAnnotation,
):
    ### Need to determine which input triggered the callback

    ctx = callback_context

    if not ctx.triggered:
        return no_update, no_update, {}

    triggered_prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
    ## if the osdViewerComponent is the trigger then we need to process the outputFromPaper

    ## Process the annotation table selection and pull the annotation and then push
    ## it to the paperdragon, also need to convert the DSA format
    if triggered_prop_id == "annotationTable":
        shapesToAdd = annotationToGeoJson(selectedAnnotation[0])

        inputToPaper = {"actions": []}

        # If I don't clear items, I also need to update the shapesToAdd
        if clearItems:
            inputToPaper["actions"].append({"type": "clearItems"})
        inputToPaper["actions"].append({"type": "drawItems", "itemList": shapesToAdd})
        # print(shapesToAdd)
        return inputToPaper, shapesToAdd, {}

    if triggered_prop_id == "osdViewerComponent":
        osdEventType = paperOutput.get("data", {}).get("callback", None)
        if not osdEventType:
            osdEventType = paperOutput.get("callback", None)

        if osdEventType in ["mouseLeave", "mouseEnter"]:
            return no_update, no_update, {}
        elif osdEventType == "createItem":
            # print(paperOutput["data"])

            si = get_box_instructions(
                paperOutput["data"]["point"]["x"],
                paperOutput["data"]["point"]["y"],
                paperOutput["data"]["size"]["width"],
                paperOutput["data"]["size"]["height"],
                colors[0],
                {"class": classes[0], "objId": getId()},
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

    # {'callback': 'propertyChanged', 'data': {'item': {'class': 'e', 'objectId': 1}, 'property': 'class'}} is the paperOutput

    elif triggered_prop_id == "make_random_button":
        ### Clear Items.. or not..

        shapesToAdd = generate_random_boxes(3, viewPortBounds)
        inputToPaper = {"actions": []}

        # If I don't clear items, I also need to update the shapesToAdd
        if clearItems:
            inputToPaper["actions"].append({"type": "clearItems"})
            inputToPaper["actions"].append(
                {"type": "drawItems", "itemList": shapesToAdd}
            )
            return inputToPaper, shapesToAdd, {}

        else:
            ## Add new items to paper, and also update the local array store
            inputToPaper["actions"].append(
                {"type": "drawItems", "itemList": shapesToAdd}
            )
            currentShapeData = currentShapeData + shapesToAdd
            return inputToPaper, currentShapeData, {}

    else:
        print(triggered_prop_id, "was the triggered prop")

    return no_update, no_update, {}


#     return command
def get_box_instructions(x, y, w, h, color, userdata={}):
    # Define the coordinates of the rectangle (polygon in GeoJSON)
    coordinates = [
        [x, y],  # Bottom left corner
        [x + w, y],  # Bottom right corner
        [x + w, y + h],  # Top right corner
        [x, y + h],  # Top left corner
        [x, y],  # Back to bottom left corner to close the polygon
    ]

    # Create the GeoJSON object
    geojson = {
        "type": "Feature",
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": [[coordinates]],
        },
        "properties": {
            "fillColor": color,
            "strokeColor": color,
            "userdata": userdata,
            "fillOpacity": 0.1,
            "strokeWidth": 2,
            "rescale": {"strokeWidth": 2},
        },
        "userdata": userdata,
    }

    return geojson


def generate_random_boxes(num_points, bounds):
    out = []

    x = int(bounds["x"])
    w = int(bounds["width"])
    y = int(bounds["y"])
    h = int(bounds["height"])

    for idx, _ in enumerate(range(num_points)):
        className, color = random.choice(list(zip(classes, colors)))
        # color = random.choice(colors)
        userdata = {"class": className, "objId": getId()}

        bx = random.randint(x, x + w)
        by = random.randint(y, y + h)
        bw = random.randint(int(w / 150), int(w / 50))
        bh = random.randint(int(h / 150), int(h / 50))
        instructions = get_box_instructions(bx, by, bw, bh, color, userdata)

        out.append(instructions)

    return out


@callback(
    Output("annotationTable", "rowData"),
    Input("imageSelect", "value"),
)
def populate_dsa_annotation_table(imageSelect):
    imgTileSources = tileSourceDict[imageSelect]

    if isinstance(imgTileSources, list):
        imgTileSource = imgTileSources[0]
    else:
        imgTileSource = imgTileSources

    ## Now see if it is a dict
    if isinstance(imgTileSource, dict):
        imgTileSource = imgTileSource["tileSource"]

    tsParts = imgTileSource.split("/item/")
    apiUrl = tsParts[0]
    itemId = tsParts[1].split("/")[0]

    annotationUrl = f"{apiUrl}/annotation?itemId={itemId}"

    r = requests.get(annotationUrl)

    annotationData = r.json()
    for a in annotationData:
        a["apiUrl"] = apiUrl

    return annotationData


### This will pull the annotations from the DSA for the given item, I am going to focus on
### the first item tilesources


def annotationToGeoJson(annotation):
    # print("Processing Annotation")

    r = requests.get(f"{annotation['apiUrl']}/annotation/{annotation['_id']}")

    if r:
        dsaAnnot = r.json()
        geoJsonBlob = hlprs.dsa_to_geo_json(dsaAnnot)
        # print()
        return geoJsonBlob
    return


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


def generateImgSrcControlPanel(tileSource, idx):
    if isinstance(tileSource, str):
        tileSource = {"tileSource": tileSource, "x": 0, "y": 0, "opacity": 1}

    return hlprs.create_layer_div(idx, tileSource)


# osdShapeData
@callback(Output("shapeDataTable", "rowData"), Input("osdShapeData_store", "data"))
def updateShapeDataTable(shapeData):
    ### The structure of the data stats with array of actions
    ## Then need to parse the actions to get the itemList
    if not shapeData:
        return []

    flattened_data = []
    for shp in shapeData:
        # flattened_data.append(hlprs.convertPaperInstructions_toTableForm(shp))
        flattened_data.append(shp)
    return flattened_data


@callback(Output("osdTileProperties", "children"), Input("imageSelect", "value"))
def createTileSourceControls(tileSourceIdx):
    newTileSources = tileSourceDict.get(tileSourceIdx, None)
    imgSrcControls = []

    # Handle cases of both single channel and multi-channel images
    if isinstance(newTileSources, list):
        for idx, tileSource in enumerate(newTileSources):
            imgSrcControls.append(generateImgSrcControlPanel(tileSource, idx))
    else:
        imgSrcControls.append(generateImgSrcControlPanel(newTileSources, 0))

    return imgSrcControls


# ### Detect changes in xOffset, yOffset, and opacity
@callback(
    Output("imgScrControls_data", "children"),
    Output("osdViewerComponent", "tileSourceProps"),
    Input({"type": "x", "index": ALL}, "value"),
    Input({"type": "y", "index": ALL}, "value"),
    Input({"type": "opacity", "index": ALL}, "value"),
    Input({"type": "rotation", "index": ALL}, "value"),
)
def process_tileSource_changes(x, y, opacity, rotation):
    ctx = callback_context
    if not ctx.triggered:
        return no_update

    # Transform the complex array to the specified format
    transformed_array = []
    indexes = set()

    complex_array = ctx.inputs_list

    # First, gather all unique indexes to create a template for the dictionaries
    for group in complex_array:
        for item in group:
            indexes.add(item["id"]["index"])

    # Initialize dictionaries for each index
    for index in indexes:
        transformed_array.append({"index": index})

    # Populate the dictionaries with values from the complex array
    for group in complex_array:
        for item in group:
            index = item["id"]["index"]
            type_ = item["id"]["type"]
            value = item["value"]
            # Find the dictionary with the matching index and update it with the new value
            for dict_ in transformed_array:
                if dict_["index"] == index:
                    dict_[type_] = value

    ## This controls whether the text version for transformed array is displayed on the screen
    # print(transformed_array)
    return no_update, transformed_array


@callback(
    Output("curObject_disp", "children"), Input("osdViewerComponent", "curShapeObject")
)
def update_curShapeObject(curShapeObject):

    print(curShapeObject, "is current shape detected..")
    if curShapeObject:
        return json.dumps(curShapeObject.get("properties", {}).get("userdata", {}))
    else:
        return no_update


@callback(Output("osdViewerComponent", "tileSources"), Input("imageSelect", "value"))
def update_imageSrc(tileSourceIdx):
    newTileSource = tileSourceDict[tileSourceIdx]
    return newTileSource


def createItem(data):
    # cprint("createItem", data)
    x = get_box_instructions(
        data["point"]["x"],
        data["point"]["y"],
        data["size"]["width"],
        data["size"]["height"],
        colors[0],
        {"class": classes[0], "objId": getId()},
    )
    out = {"actions": [{"type": "drawItems", "itemList": [x]}]}
    return out


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
    print("Mouse Leave", args)
    return None


def mouseEnter(args):
    print(args)
    return None


if __name__ == "__main__":
    app.run_server(debug=True)
