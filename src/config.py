# Global variables.
import json

COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]

CLASSES = ["a", "b", "c", "d", "e", "f"]

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

DASH_PAPERDRAGON_CONFIG = {
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
        {"event": "keyDown", "key": "l", "action": "grabColor"},
        {"event": "mouseEnter", "action": "dashCallback", "callback": "mouseEnter"},
        {"event": "mouseLeave", "action": "dashCallback", "callback": "mouseLeave"},
    ],
    "callbacks": [
        {"eventName": "item-created", "callback": "createItem"},
        {"eventName": "property-changed", "callback": "propertyChanged"},
        {"eventName": "item-deleted", "callback": "itemDeleted"},
        {"eventName": "item-edited", "callback": "itemEdited"},
    ],
    "properties": {"class": CLASSES[0]},
    "defaultStyle": {
        "fillColor": COLORS[0],
        "strokeColor": COLORS[0],
        "rescale": {
            "strokeWidth": 1,
        },
        "fillOpacity": 0.2,
    },
    "styles": {
        "class": {
            k: {"fillColor": c, "strokeColor": c} for (k, c) in zip(CLASSES, COLORS)
        }
    },
}

DSA_LAB_FLDS = {"Ezana": "6606ccfc8811fb66024cfbf3", "Jay": "66a1504f575d65c8654fd584"}


# tilesource = os.path.join(
#     os.getenv("DSA_API_URL"),
#     f'item/{img["_id"]}/tiles/dzi.dzi?token={gc_token}&style={generate_dsaStyle_string(CHANNEL_COLORS[idx])}',
# )


import urllib
import json


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
