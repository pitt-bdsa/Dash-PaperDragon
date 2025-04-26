# Base URL for the DSA API
dsa_api_url = "https://api.digitalslidearchive.org/api/v1"

tileSources = [
    {
        "label": "TCGA-2J-AAB4",
        "value": 0,
        "tileSources": [
            {
                "api_url": "https://api.digitalslidearchive.org/api/v1",
                "item_id": "5b9f0d63e62914002e9547f0",
            }
        ],
    },
    {
        "label": "TCGA-BF-A1Q0-01A-02-TSB",
        "value": 0,
        "tileSources": [
            {
                "api_url": "https://api.digitalslidearchive.org/api/v1",
                "item_id": "5b9f10a8e62914002e956509",
            }
        ],
    },
    {
        "label": "TCGA-2J-AAB4-01Z-00-DX1",
        "value": 1,
        "tileSources": [
            {
                "api_url": "https://api.digitalslidearchive.org/api/v1",
                "item_id": "5b9f0d64e62914002e9547f4",
            }
        ],
    },
    {
        "label": "Image stack",
        "value": 2,
        "tileSources": [
            {
                "api_url": "https://api.digitalslidearchive.org/api/v1",
                "item_id": "5b9f0d64e62914002e9547f4",
                "x": 0,
                "y": 0,
                "opacity": 1,
                "layerIdx": 0,
            },
            {
                "api_url": "https://api.digitalslidearchive.org/api/v1",
                "item_id": "5b9f0d64e62914002e9547f4",
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
            "api_url": "https://api.digitalslidearchive.org/api/v1",
            "item_id": "5b9f0d64e62914002e9547f4",
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
                "api_url": "https://wsi-deid.pathology.emory.edu/api/v1",
                "item_id": "64e767e2309a9ffde668be5e",
            },
            {
                "api_url": "https://wsi-deid.pathology.emory.edu/api/v1",
                "item_id": "64e767e4309a9ffde668be70",
            },
            {
                "api_url": "https://wsi-deid.pathology.emory.edu/api/v1",
                "item_id": "64e767e4309a9ffde668be73",
            },
            {
                "api_url": "https://wsi-deid.pathology.emory.edu/api/v1",
                "item_id": "64e767e1309a9ffde668be4f",
            },
            {
                "api_url": "https://wsi-deid.pathology.emory.edu/api/v1",
                "item_id": "64e767e1309a9ffde668be58",
            },
            {
                "api_url": "https://wsi-deid.pathology.emory.edu/api/v1",
                "item_id": "64e767e0309a9ffde668be46",
            },
            {
                "api_url": "https://wsi-deid.pathology.emory.edu/api/v1",
                "item_id": "64e767df309a9ffde668be43",
            },
            {
                "api_url": "https://wsi-deid.pathology.emory.edu/api/v1",
                "item_id": "64e767ce309a9ffde668bd77",
            },
            {
                "api_url": "https://wsi-deid.pathology.emory.edu/api/v1",
                "item_id": "64e767ce309a9ffde668bd7a",
            },
            {
                "api_url": "https://wsi-deid.pathology.emory.edu/api/v1",
                "item_id": "64e767e1309a9ffde668be52",
            },
        ],
    },
]


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
