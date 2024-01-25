import dash
from dash import html, State, Input, Output
import urllib.parse
import pandas as pd
import json
import dash_ag_grid 


mxif_layout = html.Div( "Maya Table")



# ?style=%s'%simpleThumb
simpleThumb = {'bands': [
    {'frame': 0, 'palette': ['#000000', '#0000ff'],
        'min': 'auto', 'max': 16},
    {'frame': 1, 'palette': ['#000000', '#00ff00'], 'max': 120},
    {'frame': 3, 'palette': ['#000000', '#ff0000'], 'max': 122},
    {'frame': 8, 'palette': ['000000', '#ffff00'], 'max': 112},
    {'frame': 14, 'palette': ['000000', '#ff00ff'], 'max': 110}]}

thumbnailString = urllib.parse.quote_plus(json.dumps(simpleThumb))
