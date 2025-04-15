"""These are various functions that are used to create UI components and do
coordinate transformations and format transformations between GeoJSON, PaperJS, and the
DSA data model."""

## Some of the functions are adopted from the following source:
###https://github.com/pearcetm/osd-paperjs-annotation/blob/main/demo/dsa/adapter.mjs

import uuid
import math
from dash import html, dcc
from pprint import pprint
import re
import random
from PIL import Image
import io
import base64
import dash_bootstrap_components as dbc
import dash_ag_grid
import requests


# config = {
#     "eventBindings": [
#         {"event": "keyDown", "key": "c", "action": "cycleProp", "property": "class"},
#         {
#             "event": "keyDown",
#             "key": "x",
#             "action": "cyclePropReverse",
#             "property": "class",
#         },
#         {"event": "keyDown", "key": "d", "action": "deleteItem"},
#         {"event": "keyDown", "key": "n", "action": "newItem", "tool": "rectangle"},
#         {
#             "event": "keyDown",
#             "key": "o",
#             "action": "dashCallback",
#             "callback": "grabColor",
#         },
#         {"event": "mouseEnter", "action": "dashCallback", "callback": "mouseEnter"},
#         {"event": "mouseLeave", "action": "dashCallback", "callback": "mouseLeave"},
#     ],
#     "callbacks": [
#         {"eventName": "item-created", "callback": "createItem"},
#         {"eventName": "property-changed", "callback": "propertyChanged"},
#         {"eventName": "item-deleted", "callback": "itemDeleted"},
#         {"eventName": "color-grabbed", "callback": "colorGrabbed"},
#     ],
#     "properties": {"class": classes},
#     "defaultStyle": {
#         "fillColor": colors[0],
#         "strokeColor": colors[0],
#         "rescale": {
#             "strokeWidth": 1,
#         },
#         "fillOpacity": 0.2,
#     },
#     "styles": {
#         "class": {
#             k: {"fillColor": c, "strokeColor": c} for (k, c) in zip(classes, colors)
#         }
#     },
# }


def get_itemId_from_url(url):
    # Extract the item id from the url
    # The url is expected to be in the format: https://api.digitalslidearchive.org/api/v1/item/5b9f0d64e62914002e9547f4/tiles/dzi.dzi
    pattern = r"(.*?)/item/(.*?)/tiles/"
    match = re.search(pattern, url)
    if match:
        api_url = match.group(1)
        item_id = match.group(2)
        # print(f"Before item: {api_url}")
        # print(f"Item ID: {item_id}")  ## Determine if I really should return this as a tuple or not..
        return api_url, item_id
    else:
        return url, None


def standardizeTileSourceOutput(tileSources):
    for tileSource in tileSources:
        if "label" not in tileSource:
            tileSource["label"] = "Tile Source"
        if "value" not in tileSource:
            tileSource["value"] = 0
        if "apiUrl" not in tileSource:
            tileSource["apiUrl"] = ""
    return tileSources


def dsa_to_geo_json(dsa):
    # pprint(dsa)

    feature_collections = []
    if (
        "attributes" in dsa["annotation"]
        and "geojslayer" in dsa["annotation"]["attributes"]
    ):
        feature_collections.append(dsa["annotation"]["attributes"]["geojslayer"])
    else:
        groups = {}
        for f in dsa["annotation"]["elements"]:
            label = f["group"] if "group" in f else dsa["annotation"]["name"]
            if label not in groups:
                groups[label] = {"elements": [], "group": label}
            groups[label]["elements"].append(f)

        # for f in dsa["annotation"]["elements"]:
        #     label = f["group"] if "group" in f else dsa["annotation"]["name"]
        #     if label not in groups:
        #         groups[label] = []
        #         groups[label].append("group")
        #     else:
        #         groups[label].append(f)
        # # print("--------")
        # print(groups, "were groups")

        for label, group_data in groups.items():

            elements = group_data["elements"]
            description = dsa["annotation"]["description"]
            feature_collections.append(
                element_array_to_feature_collection(
                    dsa["_id"], label, elements, description, group_data["group"]
                )
            )
        # for label, elements in groups.items():
        #     description = dsa["annotation"]["description"]
        #     # print(label, elements, description, dsa["_id"])

        #     feature_collections.append(
        #         element_array_to_feature_collection(
        #             dsa["_id"], label, elements, description, elements["group"]
        #         )
        #     )
    # print("-------------------")
    shapeSet = []
    for fc in feature_collections:
        for feature in fc["features"]:
            shapeSet.append(feature)

    print(shapeSet, "was returned")

    return shapeSet


def geo_json_to_dsa(feature_collections):
    if not isinstance(feature_collections, list):
        feature_collections = [feature_collections]

    elements = [feature for fc in feature_collections for feature in fc["features"]]
    elements = [feature_to_element(feature) for feature in elements]
    for element in elements:
        element["group"] = str(fc["label"])

    return elements


def element_to_feature(element):
    def map_element_to_geometry_type(e):
        g = {
            "type": None,
            "coordinates": [],
            "properties": {
                "label": e["label"]["value"] if "label" in e else None,
            },
        }

        if e["type"] == "polyline" and e["closed"] == True:
            g["type"] = "MultiPolygon"
            points = [e["points"]]
            if "holes" in e:
                points.extend(e["holes"])
            g["coordinates"] = [points]
        elif e["type"] == "polyline" and e["closed"] == False:
            g["type"] = "MultiLineString"
            g["coordinates"] = [e["points"]]
            g["properties"]["strokeWidths"] = [e["lineWidth"]]
        elif e["type"] == "arrow":
            g["type"] = "LineString"
            g["coordinates"] = e["points"]
            g["properties"]["subtype"] = "Arrow"
        elif e["type"] == "rectangle":
            g["type"] = "Point"
            g["properties"]["subtype"] = "Rectangle"
            g["coordinates"] = e["center"][:2]
            g["properties"]["width"] = e["width"]
            g["properties"]["height"] = e["height"]
            g["properties"]["angle"] = e["rotation"] * 180 / math.pi
        # Add other conditions for 'rectanglegrid', 'circle', 'ellipse', 'point' here...

        return g if g["type"] else None  # Replace with appropriate error handling

    if element["lineWidth"] < 0.001:
        element["lineWidth"] = 0
    print(element, "is current element")
    f = {
        "type": "Feature",
        "geometry": map_element_to_geometry_type(element),
        "properties": {
            "userdata": {
                "objId": element["id"],
                "class": element["label"]["value"] if "label" in element else None,
            },
            "fillColor": element.get(
                "fillColor", "rgba(255, 255, 255, 0)"
            ),  # default to white transparent
            "strokeColor": element.get(
                "lineColor", "rgba(0, 0, 0, 0)"
            ),  # default to black transparent
            "strokeWidth": element.get("lineWidth", 1),
            "rescale": {
                "strokeWidth": element.get("lineWidth", 1),
            },
            "label": element["label"]["value"] if "label" in element else None,
            "class": element["label"]["value"] if "label" in element else None,
        },
        "userdata": {
            "objId": element["id"],
            "class": element["label"]["value"] if "label" in element else None,
        },
    }

    return f


def element_array_to_feature_collection(
    annotation_id, label, elements, description, group_name
):
    grouped = {
        "featurelist": [],
        "multiPolygons": {},
        "multiLineStrings": {},
        "multiPoints": {},
    }

    for f in elements:
        feature = element_to_feature(
            f
        )  # Use the element_to_feature function from the previous example
        if "user" in f and "MultiPolygon" in f["user"]:
            if f["user"]["MultiPolygon"] not in grouped["multiPolygons"]:
                grouped["multiPolygons"][f["user"]["MultiPolygon"]] = feature
                grouped["featurelist"].append(feature)
            else:
                grouped["multiPolygons"][f["user"]["MultiPolygon"]]["geometry"][
                    "coordinates"
                ].append(feature["geometry"]["coordinates"][0])
        elif "user" in f and "MultiLineString" in f["user"]:
            if f["user"]["MultiLineString"] not in grouped["multiLineStrings"]:
                grouped["multiLineStrings"][f["user"]["MultiLineString"]] = feature
                grouped["featurelist"].append(feature)
            else:
                grouped["multiLineStrings"][f["user"]["MultiLineString"]]["geometry"][
                    "coordinates"
                ].append(feature["geometry"]["coordinates"][0])
        elif "user" in f and "MultiPoint" in f["user"]:
            if f["user"]["MultiPoint"] not in grouped["multiPoints"]:
                grouped["multiPoints"][f["user"]["MultiPoint"]] = feature
                grouped["featurelist"].append(feature)
            else:
                grouped["multiPoints"][f["user"]["MultiPoint"]]["geometry"][
                    "coordinates"
                ].append(feature["geometry"]["coordinates"][0])
        else:
            grouped["featurelist"].append(feature)

    fc = {
        "type": "FeatureCollection",
        "features": grouped["featurelist"],
        "label": label,
        "properties": {
            "userdata": {
                "dsa": {
                    "annotationId": annotation_id,
                    "group": group_name,
                    "annotationDescription": description,
                }
            },
        },
    }

    return fc


def annotation_to_feature_collections(dsa):
    feature_collections = []
    if (
        "attributes" in dsa["annotation"]
        and "geojslayer" in dsa["annotation"]["attributes"]
    ):
        feature_collections.append(dsa["annotation"]["attributes"]["geojslayer"])
    else:
        groups = {}
        for f in dsa["annotation"]["elements"]:
            label = f["group"] if "group" in f else dsa["annotation"]["name"]
            if label not in groups:
                groups[label] = []
                groups[label].append("group")
            groups[label].append(f)

        for label, elements in groups.items():
            description = dsa["annotation"]["description"]
            feature_collections.append(
                element_array_to_feature_collection(
                    dsa["_id"], label, elements, description, elements["group"]
                )
            )

    return feature_collections


def feature_to_element(feature):
    g = feature["geometry"]
    p = feature["properties"]
    e = {
        "type": None,
        "label": {"value": p["label"]},
        "fillColor": (
            get_color_string(p["fillColor"], True) if "fillColor" in p else None
        ),
        "lineColor": get_color_string(p["strokeColor"]) if "strokeColor" in p else None,
        "lineWidth": max(
            0.0001,
            (
                float(p["rescale"]["strokeWidth"])
                if "rescale" in p and "strokeWidth" in p["rescale"]
                else float(p["strokeWidth"])
            ),
        ),  # convert zero to very small number
    }

    if g["type"] == "MultiPolygon":
        multi_polygon_id = str(uuid.uuid4())
        e = [
            feature_to_element(
                {
                    "properties": p,
                    "geometry": {**g, "coordinates": c, "type": "Polygon"},
                }
            )
            for c in g["coordinates"]
        ]
        for single_poly in e:
            single_poly["user"] = {
                **single_poly.get("user", {}),
                "MultiPolygon": multi_polygon_id,
            }

    elif g["type"] == "Polygon":
        e["type"] = "polyline"
        e["closed"] = True
        point_arrays = [[p[0], p[1], 0] for c in g["coordinates"] for p in c]
        e["points"] = point_arrays[0]
        e["holes"] = point_arrays[1:]

    elif g["type"] == "MultiLineString":
        multi_line_string_id = str(uuid.uuid4())
        e = [
            feature_to_element(
                {
                    "properties": {**p, "strokeWidth": p["strokeWidths"][i]},
                    "geometry": {**g, "coordinates": c, "type": "LineString"},
                }
            )
            for i, c in enumerate(g["coordinates"])
        ]
        for single_line_string in e:
            single_line_string["user"] = {
                **single_line_string.get("user", {}),
                "MultiLineString": multi_line_string_id,
            }

    elif g["type"] == "LineString" and "subtype" not in g["properties"]:
        e["type"] = "polyline"
        e["closed"] = False
        e["points"] = [[p[0], p[1], 0] for p in g["coordinates"]]

    elif g["type"] == "LineString" and g["properties"]["subtype"] == "Arrow":
        e["type"] = "arrow"
        e["points"] = [[p[0], p[1], 0] for p in g["coordinates"][:2]]

    elif g["type"] == "Point" and "subtype" not in g["properties"]:
        e["type"] = "point"
        e["center"] = [g["coordinates"][0], g["coordinates"][1], 0]

    elif g["type"] == "Point" and g["properties"]["subtype"] == "Rectangle":
        e["type"] = "rectangle"
        e["center"] = [g["coordinates"][0], g["coordinates"][1], 0]
        e["width"] = g["properties"]["width"]
        e["height"] = g["properties"]["height"]
        e["rotation"] = g["properties"]["angle"] * math.pi / 180

    elif g["type"] == "Point" and g["properties"]["subtype"] == "Ellipse":
        e["type"] = "ellipse"
        e["center"] = [g["coordinates"][0], g["coordinates"][1], 0]
        e["width"] = g["properties"]["majorRadius"] * 2
        e["height"] = g["properties"]["minorRadius"] * 2
        e["rotation"] = g["properties"]["angle"] * math.pi / 180

        if g["properties"]["majorRadius"] == g["properties"]["minorRadius"]:
            e["type"] = "circle"
            e["radius"] = e["width"]
            del e["width"]
            del e["height"]
            del e["rotation"]

    elif g["type"] == "Point" and g["properties"]["subtype"] == "PointText":
        e["type"] = "point"
        e["center"] = [g["coordinates"][0], g["coordinates"][1], 0]
        e["user"] = {"text": g["properties"]["content"], "subtype": "pointtext"}

    elif g["type"] == "Point" and g["properties"]["subtype"] == "RectangleGrid":
        e["type"] = "griddata"
        e["origin"] = [g["coordinates"][0], g["coordinates"][1], 0]
        e["gridWidth"] = g["properties"]["gridWidth"]

    elif g["type"] == "GeometryCollection" and g["properties"]["subtype"] == "Raster":
        e["type"] = "point"
        e["center"] = [
            g["properties"]["raster"]["center"][0],
            g["properties"]["raster"]["center"][1],
            0,
        ]
        e["user"] = {"subtype": "raster", "json": g}

    return e


def convertPaperInstructions_toTableForm(data):
    """Convert Paper.js instructions to table format."""
    print("Converting data:", data)
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
            "rotation": args.get("rotation"),
            "x": args["point"]["x"],
            "y": args["point"]["y"],
            "width": args["size"]["width"],
            "height": args["size"]["height"],
            "type": "Rectangle",
        }
        return flattened_data
    elif data["paperType"] == "Path":
        segments = args.get("segments", [])
        if len(segments) > 2 and args.get("closed", False):
            first_point = segments[0].get("point", {})
            flattened_data = {
                "objectId": data["userdata"]["objectId"],
                "type": data["userdata"].get("type", "Polygon"),
                "fillOpacity": args.get("fillOpacity", 0.2),
                "fillColor": args.get("fillColor", ""),
                "class": data["userdata"]["class"],
                "strokeColor": args.get("strokeColor", ""),
                "x": first_point.get("x"),
                "y": first_point.get("y"),
                "vertices": len(segments),
            }
            return flattened_data
        else:
            point = segments[0].get("point", {})
            flattened_data = {
                "objectId": data["userdata"]["objectId"],
                "type": "Point",
                "fillOpacity": args.get("fillOpacity", 1),
                "fillColor": args.get("fillColor", ""),
                "class": data["userdata"]["class"],
                "strokeColor": args.get("strokeColor", ""),
                "x": point.get("x"),
                "y": point.get("y"),
                "markerSize": args.get("strokeWidth", 10),
                "markerColor": args.get("fillColor", ""),
            }
            return flattened_data
    elif data["paperType"] == "Path.Circle":
        center = args.get("center", {})
        flattened_data = {
            "objectId": data["userdata"]["objectId"],
            "type": "Point",
            "fillOpacity": args.get("fillOpacity", 1),
            "fillColor": args.get("fillColor", ""),
            "class": data["userdata"]["class"],
            "strokeColor": args.get("strokeColor", ""),
            "x": center.get("x"),
            "y": center.get("y"),
            "markerSize": args.get("radius", 10),
            "markerColor": args.get("fillColor", ""),
        }
        return flattened_data
    return None


def flatten_geojson(geojson_objects):
    flattened_data = []
    for obj in geojson_objects:
        flattened_obj = {
            "type": obj["type"],
            "geometry_type": obj["geometry"]["type"],
            "coordinates": obj["geometry"]["coordinates"],
            **obj["properties"],  # Merge properties into the flattened object
        }
        flattened_data.append(flattened_obj)
    return flattened_data


def get_color_string(color, use_parent_fill_opacity):
    r, g, b, a = color
    if use_parent_fill_opacity:
        a = color[3]  # Assuming the fillOpacity is stored in the alpha channel
    return f"rgba({r}, {g}, {b}, {a})"


def make_guid():
    return str(uuid.uuid4())


def create_input_div(label, id_type, idx, value, width="70px"):
    return html.Div(
        [
            html.Label(label),
            dcc.Input(
                id={"type": id_type, "index": idx},
                type="number",
                value=value,
                style={"width": width},
            ),
        ],
        className="mr-3",
    )


def create_slider_div(label, id_type, idx, value):
    return html.Div(
        [
            html.Label(label),
            dcc.Slider(
                id={"type": id_type, "index": idx},
                min=0,
                max=1,
                step=0.05,
                marks={
                    0: "0",
                    0.5: "0.5",
                    1: "1",
                },
                value=value,
                className="slider",
            ),
        ],
        className="mr-3",
        style={"textAlign": "center"},
    )


def create_layer_div(idx, tileSource):
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                f"Layer {idx} ",
                                                className="small",
                                            ),
                                        ],
                                        className="mr-4 align-items-center",
                                        style={"paddingTop": "10px"},
                                    ),
                                    create_input_div(
                                        "X Offset", "x", idx, tileSource.get("x", 0)
                                    ),
                                    create_input_div(
                                        "Y Offset", "y", idx, tileSource.get("y", 0)
                                    ),
                                    create_slider_div(
                                        "Opacity",
                                        "opacity",
                                        idx,
                                        tileSource.get("opacity", 1),
                                    ),
                                    create_input_div(
                                        "Rotation",
                                        "rotation",
                                        idx,
                                        tileSource.get("rotation", 0),
                                    ),
                                ],
                                className="d-flex",
                            ),
                        ],
                        className="mr-3",
                    ),
                ],
                className="d-flex",
            ),
        ],
        className="mb-4",
    )


# tilesource = os.path.join(
#     os.getenv("DSA_API_URL"),
#     f'item/{img["_id"]}/tiles/dzi.dzi?token={gc_token}&style={generate_dsaStyle_string(CHANNEL_COLORS[idx])}',
# )


import urllib
import json
import os


def generate_dsaStyle_string(
    color: str | None = None, opacity: float | None = None
) -> str:
    """Generate a DSA style string.

    Args:
        color (str, optional): The color to use. Defaults to None.
        opacity (float, optional): The opacity to use. Defaults to None.

    Returns:
        str: The encoded style string.

    """
    if color is None:
        color = "#000fff"
    if opacity is None:
        opacity = 0.5

    styleData = {"palette": ["#000000", color], "opacity": opacity}

    encodedStyle = urllib.parse.quote_plus(json.dumps(styleData))
    return encodedStyle


def generate_random_checkerboard(width=2048, height=2048, square_size=256):
    """Generate a random color checkerboard pattern as a base64 encoded PNG."""
    # Create a new image with RGB mode
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    # Generate random colors for each square
    for x in range(0, width, square_size):
        for y in range(0, height, square_size):
            # Generate a random color
            color = (
                random.randint(0, 255),  # R
                random.randint(0, 255),  # G
                random.randint(0, 255),  # B
            )

            # Fill the square with the color
            for i in range(square_size):
                for j in range(square_size):
                    if x + i < width and y + j < height:
                        pixels[x + i, y + j] = color

    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


def get_box_instructions(x, y, w, h, color, userdata=None):
    """Generate instructions for creating a box shape"""
    if userdata is None:
        userdata = {}

    props = {
        "point": {"x": x, "y": y},
        "size": {"width": w, "height": h},
        "fillColor": color,
        "strokeColor": color,
        "fillOpacity": 0.2,
        "strokeWidth": 2,
    }

    userdata["objectId"] = str(uuid.uuid4())
    command = {"paperType": "Path.Rectangle", "args": [props], "userdata": userdata}
    return command


def generate_random_boxes(num_points, bounds, classes, colors):
    """Generate random box shapes within given bounds"""
    out = []
    x = int(bounds["x"])
    w = int(bounds["width"])
    y = int(bounds["y"])
    h = int(bounds["height"])

    for _ in range(num_points):
        className, color = random.choice(list(zip(classes, colors)))
        userdata = {"class": className}

        bx = random.randint(x, x + w)
        by = random.randint(y, y + h)
        bw = random.randint(int(w / 150), int(w / 50))
        bh = random.randint(int(h / 150), int(h / 50))
        instructions = get_box_instructions(bx, by, bw, bh, color, userdata)
        out.append(instructions)

    return out


def generate_random_points(num_points, bounds, classes, colors):
    """Generate random point markers within given bounds"""
    out = []
    x = int(bounds["x"])
    w = int(bounds["width"])
    y = int(bounds["y"])
    h = int(bounds["height"])

    for _ in range(num_points):
        className, color = random.choice(list(zip(classes, colors)))
        userdata = {"class": className, "objectId": str(uuid.uuid4())}

        px = random.randint(x, x + w)
        py = random.randint(y, y + h)

        marker = {
            "paperType": "Path.Circle",
            "args": [
                {
                    "center": {"x": px, "y": py},
                    "radius": 200,
                    "fillColor": color,
                    "strokeColor": color,
                    "fillOpacity": 0.8,
                    "strokeWidth": 4,
                    "rescale": {
                        "strokeWidth": 4,
                        "radius": 200,
                    },
                }
            ],
            "userdata": userdata,
        }
        out.append(marker)

    return out


def get_color_from_pixel(color_data):
    """Convert RGB values to hex color string"""
    if color_data:
        r = color_data.get("r", 0)
        g = color_data.get("g", 0)
        b = color_data.get("b", 0)
        return f"#{r:02x}{g:02x}{b:02x}"
    return "#000000"


def generateImgSrcControlPanel(tileSource, idx):
    """Generate a control panel for tile source properties"""
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
        columnDefs=[
            {
                "field": "layer",
                "headerName": "Layer",
                "editable": False,
                "type": "numericColumn",
            },
            {
                "field": "x",
                "headerName": "X Offset",
                "editable": True,
                "type": "numericColumn",
                "valueFormatter": "params.value.toFixed(2)",
            },
            {
                "field": "y",
                "headerName": "Y Offset",
                "editable": True,
                "type": "numericColumn",
                "valueFormatter": "params.value.toFixed(2)",
            },
            {
                "field": "opacity",
                "headerName": "Opacity",
                "editable": True,
                "type": "numericColumn",
                "cellRenderer": "agSliderCellRenderer",
                "cellRendererParams": {
                    "minValue": 0,
                    "maxValue": 1,
                    "step": 0.1,
                },
                "valueFormatter": "params.value.toFixed(2)",
            },
            {
                "field": "rotation",
                "headerName": "Rotation",
                "editable": True,
                "type": "numericColumn",
                "valueFormatter": "params.value.toFixed(1)",
            },
        ],
        rowData=[
            {
                "layer": idx,
                "x": float(tileSource.get("x", 0)),
                "y": float(tileSource.get("y", 0)),
                "opacity": float(tileSource.get("opacity", 1)),
                "rotation": float(tileSource.get("rotation", 0)),
            }
        ],
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "filter": True,
            "minWidth": 100,
        },
        dashGridOptions={
            "domLayout": "autoHeight",
            "stopEditingWhenCellsLoseFocus": True,
        },
    )


# Add these column definitions and layout components at the end of the file

# Column definitions for AG Grid tables
tileSourceColumns = [
    {
        "field": "layer",
        "headerName": "Layer",
        "width": 80,
        "editable": False,
    },
    {
        "field": "x",
        "headerName": "X Offset",
        "width": 120,
        "editable": True,
        "valueFormatter": lambda params: f"{params.value:.2f}",
    },
    {
        "field": "y",
        "headerName": "Y Offset",
        "width": 120,
        "editable": True,
        "valueFormatter": lambda params: f"{params.value:.2f}",
    },
    {
        "field": "opacity",
        "headerName": "Opacity",
        "width": 120,
        "editable": True,
        "valueFormatter": lambda params: f"{params.value:.2f}",
    },
    {
        "field": "rotation",
        "headerName": "Rotation",
        "width": 120,
        "editable": True,
        "valueFormatter": lambda params: f"{params.value:.2f}",
    },
]

paperJsShapeColumns = [
    {
        "field": "objectId",
        "headerName": "ID",
        "width": 100,
        "editable": False,
    },
    {
        "field": "type",
        "headerName": "Type",
        "width": 100,
        "editable": False,
    },
    {
        "field": "x",
        "headerName": "X",
        "width": 100,
        "editable": False,
        "valueFormatter": lambda params: f"{params.value:.2f}",
    },
    {
        "field": "y",
        "headerName": "Y",
        "width": 100,
        "editable": False,
        "valueFormatter": lambda params: f"{params.value:.2f}",
    },
    {
        "field": "width",
        "headerName": "Width",
        "width": 100,
        "editable": False,
        "valueFormatter": lambda params: f"{params.value:.2f}",
    },
    {
        "field": "height",
        "headerName": "Height",
        "width": 100,
        "editable": False,
        "valueFormatter": lambda params: f"{params.value:.2f}",
    },
    {
        "field": "fillColor",
        "headerName": "Fill Color",
        "width": 120,
        "editable": False,
    },
    {
        "field": "strokeColor",
        "headerName": "Stroke Color",
        "width": 120,
        "editable": False,
    },
    {
        "field": "strokeWidth",
        "headerName": "Stroke Width",
        "width": 100,
        "editable": False,
        "valueFormatter": lambda params: f"{params.value:.2f}",
    },
    {
        "field": "fillOpacity",
        "headerName": "Fill Opacity",
        "width": 100,
        "editable": False,
        "valueFormatter": lambda params: f"{params.value:.2f}",
    },
]

# Layout components
coordinate_display = dbc.Card(
    [
        dbc.CardHeader("Coordinates"),
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.Label("X: "),
                        html.Span(id="x-coord", style={"marginRight": "20px"}),
                        html.Label("Y: "),
                        html.Span(id="y-coord"),
                    ],
                    style={"fontSize": "14px"},
                )
            ]
        ),
    ],
    style={"marginBottom": "10px"},
)

annotation_panel = dbc.Card(
    [
        dbc.CardHeader("Annotation Tools"),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Button(
                                "Rectangle",
                                id="rectangle-button",
                                color="primary",
                                className="me-2",
                                style={"width": "100%", "marginBottom": "5px"},
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            dbc.Button(
                                "Point",
                                id="point-button",
                                color="primary",
                                className="me-2",
                                style={"width": "100%", "marginBottom": "5px"},
                            ),
                            width=6,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Button(
                                "Delete Selected",
                                id="delete-button",
                                color="danger",
                                className="me-2",
                                style={"width": "100%", "marginBottom": "5px"},
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            dbc.Button(
                                "Clear All",
                                id="clear-button",
                                color="warning",
                                className="me-2",
                                style={"width": "100%", "marginBottom": "5px"},
                            ),
                            width=6,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Button(
                                "Get Color",
                                id="get-color-button",
                                color="info",
                                className="me-2",
                                style={"width": "100%", "marginBottom": "5px"},
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            dbc.Button(
                                "Add Checkerboard",
                                id="add_checkerboard_button",
                                color="info",
                                className="me-2",
                                style={"width": "100%", "marginBottom": "5px"},
                            ),
                            width=6,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Button(
                                "⌨️ Key Bindings",
                                id="key-bindings-button",
                                color="secondary",
                                className="me-2",
                                style={"width": "100%", "marginBottom": "5px"},
                            ),
                            width=12,
                        ),
                    ]
                ),
            ]
        ),
    ],
    style={"marginBottom": "10px"},
)

key_bindings_modal = dbc.Modal(
    [
        dbc.ModalHeader("Key Bindings"),
        dbc.ModalBody(
            [
                html.Div(
                    [
                        html.P("Rectangle Tool: 'r'"),
                        html.P("Point Tool: 'p'"),
                        html.P("Delete Selected: 'd'"),
                        html.P("Clear All: 'c'"),
                        html.P("Get Color: 'g'"),
                        html.P("Add Checkerboard: 'a'"),
                        html.P("Cycle Property Forward: 'f'"),
                        html.P("Cycle Property Backward: 'b'"),
                        html.P("Grab Color: 'l'"),
                    ],
                    style={"fontSize": "14px"},
                )
            ]
        ),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-key-bindings", className="ml-auto")
        ),
    ],
    id="key-bindings-modal",
    is_open=False,
)


def generate_key_bindings_modal(config):
    """Generate the key bindings modal component."""
    return dbc.Modal(
        [
            dbc.ModalHeader("Keyboard Shortcuts"),
            dbc.ModalBody(
                [
                    html.Table(
                        [
                            html.Thead(
                                html.Tr(
                                    [
                                        html.Th("Key", style={"width": "100px"}),
                                        html.Th("Action"),
                                    ]
                                )
                            ),
                            html.Tbody(
                                [
                                    html.Tr(
                                        [
                                            html.Td(html.Kbd(binding["key"])),
                                            html.Td(
                                                f"{binding['action']}: {binding.get('property', binding.get('tool', binding.get('callback', '')))}"
                                            ),
                                        ]
                                    )
                                    for binding in config["eventBindings"]
                                    if binding["event"] == "keyDown"
                                ]
                            ),
                        ],
                        className="table table-sm",
                        style={"fontSize": "0.9em"},
                    ),
                    html.Hr(),
                    html.H6("Mouse Actions", className="mt-3"),
                    html.Ul(
                        [
                            html.Li("Click and drag to pan the image"),
                            html.Li("Scroll wheel to zoom in/out"),
                            html.Li("Double-click to reset view"),
                        ],
                        style={"fontSize": "0.9em"},
                    ),
                ]
            ),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-keybindings", className="ms-auto")
            ),
        ],
        id="keybindings-modal",
        size="sm",
        is_open=False,
    )


def generate_annotation_panel():
    """Generate the annotation panel component."""
    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H6("Available Annotations", className="mb-2"),
                            dash_ag_grid.AgGrid(
                                id="annotationTable",
                                columnDefs=[
                                    {
                                        "field": "name",
                                        "headerName": "Name",
                                        "width": 200,
                                    },
                                    {
                                        "field": "description",
                                        "headerName": "Description",
                                        "width": 300,
                                    },
                                    {
                                        "field": "created",
                                        "headerName": "Created",
                                        "width": 150,
                                    },
                                    {
                                        "field": "updated",
                                        "headerName": "Updated",
                                        "width": 150,
                                    },
                                ],
                                rowData=[],
                                defaultColDef={
                                    "resizable": True,
                                    "sortable": True,
                                    "filter": True,
                                },
                                style={"height": "200px", "width": "100%"},
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
        style={"width": "100%"},
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


def createItem(data, colors, classes):
    """Handle item creation callback."""
    x = get_box_instructions(
        data["point"]["x"],
        data["point"]["y"],
        data["size"]["width"],
        data["size"]["height"],
        colors[0],
        {"class": classes[0]},
    )
    return {"actions": [{"type": "drawItems", "itemList": [x]}]}


def deleteItem(id):
    """Handle item deletion callback."""
    return {"actions": [{"type": "deleteItem", "id": id}]}


def itemDeleted(data):
    """Handle item deleted event callback."""
    print("itemDeleted", data)
    return None


def propertyChanged(data):
    """Handle property change callback."""
    print("propertyChanged", data)
    return None


def mouseLeave(args):
    """Handle mouse leave event callback."""
    return None


def mouseEnter(args):
    """Handle mouse enter event callback."""
    return None


def colorGrabbed(args):
    """Handle color grab event callback."""
    return None


def add_tile_source(tileSourceDict, source_config):
    """Add a new tile source to the dictionary.

    Args:
        tileSourceDict (dict): The dictionary containing all tile sources
        source_config (dict): Configuration for the new tile source with keys:
            - label: Name/label for the tile source
            - tileSource: URL or configuration for the tile source
            - x: X offset (default: 0)
            - y: Y offset (default: 0)
            - opacity: Opacity value (default: 1)
            - rotation: Rotation value (default: 0)
            - api_url: (optional) DSA API URL
            - item_id: (optional) DSA item ID

    Returns:
        dict: Updated tileSourceDict
    """
    label = source_config.get("label", f"Layer {len(tileSourceDict)}")

    if isinstance(source_config.get("tileSource"), str):
        # Direct URL
        tile_source = {
            "tileSource": source_config["tileSource"],
            "x": source_config.get("x", 0),
            "y": source_config.get("y", 0),
            "opacity": source_config.get("opacity", 1),
            "rotation": source_config.get("rotation", 0),
        }
    else:
        # DSA configuration
        api_url = source_config.get("api_url")
        item_id = source_config.get("item_id")
        if api_url and item_id:
            tile_source_url = f"{api_url}/item/{item_id}/tiles/dzi.dzi"
            tile_source = {
                "tileSource": tile_source_url,
                "x": source_config.get("x", 0),
                "y": source_config.get("y", 0),
                "opacity": source_config.get("opacity", 1),
                "rotation": source_config.get("rotation", 0),
                "layerIdx": source_config.get("layerIdx", len(tileSourceDict)),
            }
        else:
            raise ValueError("Invalid tile source configuration")

    tileSourceDict[label] = tile_source
    return tileSourceDict


def remove_tile_source(tileSourceDict, label):
    """Remove a tile source from the dictionary.

    Args:
        tileSourceDict (dict): The dictionary containing all tile sources
        label (str): The label/name of the tile source to remove

    Returns:
        dict: Updated tileSourceDict
    """
    if label in tileSourceDict:
        del tileSourceDict[label]
    return tileSourceDict


def generate_tile_source_controls():
    """Generate controls for managing tile sources."""
    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardHeader("Tile Source Management"),
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Input(
                                                id="new-tile-source-url",
                                                type="text",
                                                placeholder="Enter tile source URL",
                                                className="mb-2",
                                            ),
                                            dbc.Input(
                                                id="new-tile-source-label",
                                                type="text",
                                                placeholder="Enter label",
                                                className="mb-2",
                                            ),
                                            dbc.Button(
                                                "Add Tile Source",
                                                id="add-tile-source-button",
                                                color="primary",
                                                className="me-2",
                                            ),
                                        ],
                                        width=6,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Select(
                                                id="remove-tile-source-select",
                                                options=[],  # Will be populated dynamically
                                                className="mb-2",
                                            ),
                                            dbc.Button(
                                                "Remove Tile Source",
                                                id="remove-tile-source-button",
                                                color="danger",
                                                className="me-2",
                                            ),
                                        ],
                                        width=6,
                                    ),
                                ]
                            )
                        ]
                    ),
                ],
                className="mb-3",
            )
        ]
    )
