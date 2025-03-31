import math
import requests
import random
import urllib
import json

## Define some constants useful for testing and development

globalId = 0

colors = ["red", "orange", "yellow", "green", "blue", "purple"]
classes = ["a", "b", "c", "d", "e", "f"]


CHANNEL_COLORS = [
    "#FF0000",  # Red
    "#00FF00",  # Green
    "#0000FF",  # Blue
    "#FFFF00",  # Yellow
    "#00FFFF",  # Cyan
    "#FF00FF",  # Magenta
    "#FFA500",  # Orange
    "#800080",  # Purple
    "#00FF00",  # Lime
    "#FFC0CB",  # Pink
    "#008080",  # Teal
    "#A52A2A",  # Brown
    "#000080",  # Navy
    "#808000",  # Olive
    "#800000",  # Maroon
]


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


def annotationToGeoJson(annotation):
    # print("Processing Annotation")
    r = requests.get(f"{annotation['apiUrl']}/annotation/{annotation['_id']}")

    if r:
        dsaAnnot = r.json()
        geoJsonBlob = dsa_to_geo_json(dsaAnnot)
        # print()
        return geoJsonBlob
    return


# The globalId is used to generate unique ids for each element in the application
# This may not be thread safe
def getId():
    global globalId
    globalId = globalId + 1
    return globalId


def rgb_to_hsi(r, g, b):
    # Normalize the RGB values to the range [0, 1]
    r /= 255
    g /= 255
    b /= 255

    # Calculate Intensity (I)
    I = (r + g + b) / 3

    # Calculate Saturation (S)
    min_rgb = min(r, g, b)
    S = 1 - (min_rgb / I) if I != 0 else 0

    # Calculate Hue (H)
    H = 0
    if S != 0:
        numerator = 0.5 * ((r - g) + (r - b))
        denominator = math.sqrt((r - g) * (r - g) + (r - b) * (g - b))
        H = math.acos(numerator / denominator) if denominator != 0 else 0

        if b > g:
            H = 2 * math.pi - H

    # Convert Hue to degrees
    H = H * (180 / math.pi)

    return {"H": H, "S": S, "I": I}


def get_color_from_pixel(pixel):
    return "HELLO"
    # return pixel.get('color', 'black')


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
        return {}
    if opacity is None:
        opacity = 0.5

    styleData = {"palette": ["#000000", color], "opacity": opacity}

    encodedStyle = urllib.parse.quote_plus(json.dumps(styleData))
    return encodedStyle
