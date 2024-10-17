## These are tile sources I am using for testing the viewer.
## I am allowing for multiple tile sources to be passed in as an array, and also allowing for multiple layers to be passed in as an array.
## I am creating a convenience

## TileSources should always be an array, even if there's only a single tile source


tileSources = [
    {
        "label": "TCGA-BF-A1Q0-01A-02-TSB",
        "value": 0,
        "_id": "5b9f10a8e62914002e956509",
        "apiUrl": "https://api.digitalslidearchive.org/api/v1/",
        "tileSources": [
            {
                "tileSource": "https://api.digitalslidearchive.org/api/v1/item/5b9f10a8e62914002e956509/tiles/dzi.dzi"
            }
        ],
    },
    {
        "label": "TCGA-2J-AAB4",
        "value": 1,
        "apiUrl": "https://api.digitalslidearchive.org/api/v1/",
        "_id": "5b9f0d63e62914002e9547f0",
        "tileSources": [
            {
                "tileSource": "https://api.digitalslidearchive.org/api/v1/item/5b9f0d63e62914002e9547f0/tiles/dzi.dzi"
            }
        ],
    },
    # {
    #     "label": "TCGA-2J-AAB4-01Z-00-DX1",
    #     "value": 1,
    #     "apiUrl": "https://api.digitalslidearchive.org/api/v1/",
    #     "_id": "5b9f0d64e62914002e9547f4",
    #     "tileSources": [
    #         "https://api.digitalslidearchive.org/api/v1/item/5b9f0d64e62914002e9547f4/tiles/dzi.dzi"
    #     ],
    # },
    # {
    #     "label": "Image stack",
    #     "value": 2,
    #     "apiUrl": "https://api.digitalslidearchive.org/api/v1/",
    #     "tileSources": [
    #         {
    #             "tileSource": "https://api.digitalslidearchive.org/api/v1/item/5b9f0d64e62914002e9547f4/tiles/dzi.dzi",
    #             "_id": "5b9f0d64e62914002e9547f4",
    #             "x": 0,
    #             "y": 0,
    #             "opacity": 1,
    #             "layerIdx": 0,
    #         },
    #         {
    #             "tileSource": "https://api.digitalslidearchive.org/api/v1/item/5b9f0d64e62914002e9547f4/tiles/dzi.dzi",
    #             "_id": "5b9f0d64e62914002e9547f4",
    #             "x": 0.2,
    #             "y": 0.2,
    #             "opacity": 0.2,
    #             "layerIdx": 1,
    #         },
    #     ],
    # },
    # {
    #     "label": "CDG Example",
    #     "value": 2,
    #     "apiUrl": "https://api.digitalslidearchive.org/api/v1/",
    #     "tileSources": [
    #         {
    #             "tileSource": "https://api.digitalslidearchive.org/api/v1/item/5b9f0d64e62914002e9547f4/tiles/dzi.dzi",
    #             "_id": "5b9f0d64e62914002e9547f4",
    #             "x": 0,
    #             "y": 0,
    #             "opacity": 1,
    #             "layerIdx": 0,
    #         }
    #     ],
    # },
    {
        "label": "ISIC Example",
        "value": 3,
        "apiUrl": "https://wsi-deid.pathology.emory.edu/api/v1",
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
                "tileSource": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767ce309a9ffde668bd7a/tiles/dzi.dzi",
                "opacity": 0.5,
            },
            {
                "tileSource": "https://wsi-deid.pathology.emory.edu/api/v1//item/64e767e1309a9ffde668be52/tiles/dzi.dzi",
                "opacity": 0.5,
            },
        ],
    },
]


sampleShapes = [
    {
        "type": "Feature",
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [52981, 17715],
                        [54154, 17715],
                        [54154, 18308],
                        [52981, 18308],
                        [52981, 17715],
                    ]
                ]
            ],
        },
        "properties": {
            "fillColor": "green",
            "strokeColor": "green",
            "userdata": {"class": "d", "objId": 1},
            "fillOpacity": 0.1,
            "strokeWidth": 2,
            "rescale": {"strokeWidth": 2},
        },
        "userdata": {"class": "d", "objId": 1},
    },
    {
        "type": "Feature",
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [45677, 13048],
                        [46572, 13048],
                        [46572, 13345],
                        [45677, 13345],
                        [45677, 13048],
                    ]
                ]
            ],
        },
        "properties": {
            "fillColor": "red",
            "strokeColor": "red",
            "userdata": {"class": "a", "objId": 2},
            "fillOpacity": 0.1,
            "strokeWidth": 2,
            "rescale": {"strokeWidth": 2},
        },
        "userdata": {"class": "a", "objId": 2},
    },
    {
        "type": "Feature",
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [42847, 24844],
                        [43396, 24844],
                        [43396, 25140],
                        [42847, 25140],
                        [42847, 24844],
                    ]
                ]
            ],
        },
        "properties": {
            "fillColor": "purple",
            "strokeColor": "purple",
            "userdata": {"class": "f", "objId": 3},
            "fillOpacity": 0.1,
            "strokeWidth": 2,
            "rescale": {"strokeWidth": 2},
        },
        "userdata": {"class": "f", "objId": 3},
    },
]
