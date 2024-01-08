import dash_paperdragon
from dash import Dash, callback, html, Input, Output, dcc
import dash_bootstrap_components as dbc
import json

app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])


osdElement =     dash_paperdragon.DashPaperdragon(
        id='input',
        imageSrc='https://api.digitalslidearchive.org/api/v1/item/5b9f02d7e62914002e94e684/tiles/dzi.dzi',
        zoomLevel=0,
        
        viewPortBounds={"x":0,"y":0,"width":0,"height":0},
        shapeList = {"pointList":[]},
        curMousePosition = {"x":0,"y":0},
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
            dbc.Button("Update Point List", id="updatePointList_button", className="mb-4")
        )
    ])],
)


app.layout = dbc.Container(
    [dbc.Row(dbc.Col(html.H1("Dash Paperdragon", className="text-center"))), 
     dbc.Row([dbc.Col(osdElement,width=8),dbc.Col(coordinate_display,width=4)]) ]  
)


import random
def generate_random_point_list(num_points):
    colors = ["red", "blue", "green"]
    point_list = []
    objectClasses = ["little","yellow","different","nuprin"]
    for _ in range(num_points):
        point = {
            "x": random.randint(0, 10000),
            "y": random.randint(0, 10000),
            "width": random.randint(50, 200),
            "height": random.randint(50, 200),
            "color": random.choice(colors),
            "objectClass": random.choice(objectClasses)
        }
        point_list.append(point)

    return {"pointList": point_list}

@callback(Output('input', 'shapeList'), Input('updatePointList_button', 'n_clicks'))
def update_shapeList(n_clicks):
    if n_clicks is None:
        return {"pointList":[]}
    else:
        return generate_random_point_list(1000)


@callback(Output('mousePos_disp', 'children'), Input('input', 'curMousePosition'))
def update_mouseCoords(curMousePosition):
    return f'{int(curMousePosition["x"])},{int(curMousePosition["y"])}'

@callback(Output('zoomLevel_disp', 'children'), Input('input', 'zoomLevel'))
def updateZoomLevel(currentZoom):
    return '{:.3f}'.format(currentZoom)


@callback(Output('viewportBounds_disp', 'children'), Input('input', 'viewPortBounds'))
def update_viewPortBoundsd(viewPortBounds):
    vp = viewPortBounds
    return f'x: {int(vp["x"])} y: {int(vp["y"])} w: {int(vp["width"])} h: {int(vp["height"])}' 

if __name__ == '__main__':
    app.run_server(debug=True)
