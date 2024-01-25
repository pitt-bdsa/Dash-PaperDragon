import dash_paperdragon
from dash import Dash, callback, html, Input, Output, dcc
import dash_bootstrap_components as dbc
import json, random
from mxifImage_layout import mxif_layout, thumbnailString
import dash_ag_grid
import pandas as pd

app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])




sampleUrl = f'http://localhost:8080/api/v1/item/6596f464714fd1118e983841/tiles/dzi.dzi?style={thumbnailString}'


osdElement =     dash_paperdragon.DashPaperdragon(
        id='osdViewerComponent',
        imageSrc=sampleUrl,
        zoomLevel=0,
        viewPortBounds={"x":0,"y":0,"width":0,"height":0},
        shapeList = {"pointList":[]},
        curMousePosition = {"x":0,"y":0},
        curShapeObject = None,
    )

coordinate_display =dbc.Container([
    dbc.Row([
        dbc.Col(html.H1('Zoom and Mouse Position'), className="mb-4")
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Zoom Level", className="card-title"),
                    html.Div(id='zoomLevel_disp', className="card-text")
                ])
            ], className="mb-3"),width=4
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Viewport Bounds", className="card-title"),
                    html.Div(id='viewportBounds_disp', className="card-text")
                ])
            ], className="mb-6"),width=8
        ),
       
         dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Current Mouse Position", className="card-title"),
                    html.Div(id='mousePos_disp', className="card-text")
                ])
            ], className="mb-6")
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Highlighted Object", className="card-title"),
                    html.Div(id='curObject_disp', className="card-text")
                ])
            ], className="mb-6")
        ),
        dbc.Col(
            dbc.Button("Update Point List", id="updatePointList_button", className="mb-4")
        )
    ]),
    ],
)




app.layout = dbc.Container(
    [dbc.Row(dbc.Col(html.H1("Dash Paperdragon", className="text-center"))), 
     dbc.Row([dbc.Col(osdElement,width=8),dbc.Col(coordinate_display,width=4)]) ]  
)



def generate_random_shapeList(num_points):
    colors = ["red", "blue", "green"]
    point_list = []
    objectClasses = ["little","yellow","different","nuprin"]
    for idx, _ in enumerate(range(num_points)):
        point = {
            "x": random.randint(0, 10000),
            "y": random.randint(0, 10000),
            "width": random.randint(50, 200),
            "height": random.randint(50, 200),
            "color": random.choice(colors),
            "objectClass": random.choice(objectClasses),
            "objectId": f'object_{idx}'
        }
        point_list.append(point)

    return {"pointList": point_list}

@callback(Output('osdViewerComponent', 'shapeList'), Input('updatePointList_button', 'n_clicks'))
def update_shapeList(n_clicks):
    if n_clicks is None:
        return {"pointList":[]}
    else:
        return generate_random_shapeList(1000)


@callback(Output('mousePos_disp', 'children'), Input('osdViewerComponent', 'curMousePosition'))
def update_mouseCoords(curMousePosition):
    return f'{int(curMousePosition["x"])},{int(curMousePosition["y"])}'

@callback(Output('zoomLevel_disp', 'children'), Input('osdViewerComponent', 'zoomLevel'))
def updateZoomLevel(currentZoom):
    return '{:.3f}'.format(currentZoom)

@callback(Output('viewportBounds_disp', 'children'), Input('osdViewerComponent', 'viewPortBounds'))
def update_viewPortBoundsd(viewPortBounds):
    vp = viewPortBounds
    return f'x: {int(vp["x"])} y: {int(vp["y"])} w: {int(vp["width"])} h: {int(vp["height"])}' 


@callback(Output('curObject_disp', 'children'), Input('osdViewerComponent', 'curShapeObject'))
def update_curShapeObject(curShapeObject):
    return f'Current Selected Shape: {json.dumps(curShapeObject)}' 


if __name__ == '__main__':
    app.run_server(debug=True)
