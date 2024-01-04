import dash_paperdragon
from dash import Dash, callback, html, Input, Output
import dash_bootstrap_components as dbc

app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])


osdElement =     dash_paperdragon.DashPaperdragon(
        id='input',
        value='my-value',
        label='my-label',
        imageSrc='https://api.digitalslidearchive.org/api/v1/item/5b9f02d7e62914002e94e684/tiles/dzi.dzi',
        zoomLevel=0,
        globalX=0,
        globalY=0,
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
            ], className="mb-4")
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Viewport X", className="card-title"),
                    html.Div(id='viewportX_disp', className="card-text")
                ])
            ], className="mb-4")
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Viewport Y", className="card-title"),
                    html.Div(id='viewportY_disp', className="card-text")
                ])
            ], className="mb-4")
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Mouse X Position", className="card-title"),
                    html.Div(id='mousePosX_disp', className="card-text")
                ])
            ], className="mb-4")
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Mouse Y Position", className="card-title"),
                    html.Div(id='mousePosY_disp', className="card-text")
                ])
            ], className="mb-4")
        )
    ])])


app.layout = dbc.Container(
    [dbc.Row(dbc.Col(html.H1("Dash Paperdragon", className="text-center"))), 
     dbc.Row([dbc.Col(osdElement,width=8),dbc.Col(coordinate_display,width=4)]) ]  
)



@callback(Output('viewportX_disp', 'children'), Input('input', 'globalX'))
def update_viewport_x(viewport_x):
    return '{:.3f}'.format(viewport_x)
    

@callback(Output('viewportY_disp', 'children'), Input('input', 'globalY'))
def update_viewport_y(viewport_y):
    return '{:.3f}'.format(viewport_y)


@callback(Output('zoomLevel_disp', 'children'), Input('input', 'zoomLevel'))
def updateZoomLevel(currentZoom):
    return '{:.3f}'.format(currentZoom)


if __name__ == '__main__':
    app.run_server(debug=True)
