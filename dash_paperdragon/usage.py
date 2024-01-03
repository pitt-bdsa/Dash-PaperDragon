import dash_paperdragon
from dash import Dash, callback, html, Input, Output

app = Dash(__name__)

app.layout = html.Div([
    dash_paperdragon.DashPaperdragon(
        id='input',
        value='my-value',
        label='my-label',
        imageSrc='https://api.digitalslidearchive.org/api/v1/item/5b9f02d7e62914002e94e684/tiles/dzi.dzi',
        zoomLevel=0
    ),
    html.Div(id='output'),
        html.Div(id='zoomLevel_disp')
])


@callback(Output('output', 'children'), Input('input', 'value'))
def display_output(value):
    return 'You have entered {}'.format(value)


@callback(Output('zoomLevel_disp', 'children'), Input('input', 'zoomLevel'))
def updateZoomLevel(value):
    return f'ZoomLevel is {value}'


if __name__ == '__main__':
    app.run_server(debug=True)
