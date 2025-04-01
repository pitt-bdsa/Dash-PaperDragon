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
