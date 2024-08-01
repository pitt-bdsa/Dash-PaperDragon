""" These are various functions that are used to create UI components and do
coordinate transformations and format transformations between GeoJSON, PaperJS, and the
DSA data model."""

## Some of the functions are adopted from the following source:
###https://github.com/pearcetm/osd-paperjs-annotation/blob/main/demo/dsa/adapter.mjs

import uuid
import math
from dash import html, dcc
from pprint import pprint


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

    # args = data["args"][0]
    # Flatten the data
    args = data.get("args", [])
    if args:
        args = args[0]
    print("-------------------")
    print(data)
    # print(data, "was received")

    ### The path is different for rectangles..
    if data["paperType"] == "Path.Rectangle":

        # Flatten the data
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
        flattened_data = {
            "objectId": data["userdata"]["objectId"],
            "fillOpacity": args["fillOpacity"],
            "fillColor": args["fillColor"],
            "class": data["userdata"]["class"],
            "strokeColor": args["strokeColor"],
            "rotation": args.get("rotation"),
        }
        return flattened_data
        # Use .get() to av
    ## TO DO: process segments


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
