import dash_paperdragon
from dash import Dash, callback, html, Input, Output, dcc, State
import dash_bootstrap_components as dbc
import json, random

app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

imageSet = [{"label": "TCGA-2J-AAB4", "value":"https://api.digitalslidearchive.org/api/v1/item/5b9f0d63e62914002e9547f0/tiles/dzi.dzi"},
{"label":"TCGA-2J-AAB4-01Z-00-DX1", "value": "https://api.digitalslidearchive.org/api/v1/item/5b9f0d64e62914002e9547f4/tiles/dzi.dzi"}]

# For now these are global variables; can be redis if multiple windows can interact with the same server
colors = ["red", "orange", "yellow", "green", "blue", "purple"]
classes = ['a', 'b', 'c', 'd', 'e', 'f']

globalId = 0
def getId():
    global globalId
    globalId = globalId + 1
    return globalId

# possible bindings for actions:
# keyDown
# keyUp
# mouseEnter
# mouseLeave
# click ? 

# supported actions:
# cycleProp (property)
# cyclePropReverse (property)
# deleteItem
# newItem
# dashCallback (callback)

# supported callback functions:
# createItem

config = {
    "eventBindings": [
        {"event": "keyDown", "key": "c", "action": "cycleProp", "property": "class" },
        {"event": "keyDown", "key": "x", "action": "cyclePropReverse", "property": "class"},
        {"event": "keyDown", "key": "d", "action": "deleteItem"},
        {"event": "keyDown", "key": "n", "action": "newItem", "tool": "rectangle"},
        {"event": "mouseEnter", "action": "dashCallback", "callback": "mouseEnter"},
        {"event": "mouseLeave", "action": "dashCallback", "callback": "mouseLeave"},
    ],
    'callbacks':[
        {'eventName':'item-created', 'callback':'createItem'},
        {'eventName':'property-changed', 'callback':'propertyChanged'},
        {'eventName':'item-deleted', 'callback':'itemDeleted'}
    ],
    'properties':{
        'class': classes
    },
    'defaultStyle':{
        'fillColor':colors[0],
        'strokeColor':colors[0],
        'rescale':{
            'strokeWidth':1,
        },
        'fillOpacity':0.2,
    },
    'styles':{
        'class':{k:{'fillColor':c, 'strokeColor':c} for (k, c) in zip(classes, colors)}
    }
}
def cbCreateItem(args):
    return createItem(args)

def cbItemDeleted(args):
    return itemDeleted(args)

def cbMouseEnter(args):
    return mouseEnter(args)

def cbMouseLeave(args):
    return mouseLeave(args)

def cbPropertyChanged(args):
    return propertyChanged(args)

callbacks = {
    'createItem': cbCreateItem,
    'itemDeleted': cbItemDeleted,
    'mouseEnter': cbMouseEnter,
    'mouseLeave': cbMouseLeave,
    'propertyChanged': cbPropertyChanged,
}

## Create element
osdElement =     dash_paperdragon.DashPaperdragon(
        id='osdViewerComponent',
        config = config,
        imageSrc='https://api.digitalslidearchive.org/api/v1/item/5b9f02d7e62914002e94e684/tiles/dzi.dzi',
        zoomLevel=0,
        viewportBounds={"x":0,"y":0,"width":0,"height":0},
        curMousePosition = {"x":0,"y":0},
        inputToPaper = None,
        outputFromPaper = None,
    )

## Make HTML layout
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
            dbc.Button("Make Random Rects", id="make_random_button", className="mb-4")
        )
    ])],
)


app.layout = dbc.Container(
    [dbc.Row(dbc.Col(html.H1("Dash Paperdragon", className="text-center"))), 
     dbc.Row( dbc.Select(id="imageSelect", options=imageSet, value=imageSet[0]["value"], className="mb-4"), style={"width": "400px"}),
     dbc.Row([dbc.Col(osdElement,width=8),dbc.Col(coordinate_display,width=4)]) ]  
)
## End of layout

@callback(Output('osdViewerComponent', 'inputToPaper', allow_duplicate=True),
          Output('osdViewerComponent', 'outputFromPaper'),
          Input('osdViewerComponent', 'outputFromPaper'),
          prevent_initial_call = True)
def handleOutputFromPaper(paperOutput):
    inputToPaper = None
    outputFromPaper = None
    
    if paperOutput is None:
        paperOutput = {}

    callback = callbacks.get(paperOutput.get('callback'))
   
    if callback:
        inputToPaper = callback(paperOutput.get('data'))
    
    return inputToPaper, outputFromPaper

def get_box_instructions(x, y, w, h, color, userdata = {}):
    props = config.get('defaultStyle') | {
            'point': {'x': x, 'y': y},
            'size': {'width': w, 'height': h},
            'fillColor':color,
            'strokeColor': color,
        }
    userdata['objectId'] = getId()
    command = {
            'paperType': 'Path.Rectangle',
            'args': [props],
            'userdata':userdata
        }

    return command

def generate_random_boxes(num_points, bounds):
    
    out = []
    
    x = int(bounds["x"])
    w = int(bounds["width"])
    y = int(bounds["y"])
    h = int(bounds["height"])

    for idx, _ in enumerate(range(num_points)):
        
        className, color = random.choice(list(zip(classes, colors)))
        # color = random.choice(colors)
        userdata = {'class': className}
        
        bx = random.randint(x, x + w)
        by = random.randint(y, y + h)
        bw = random.randint(int(w / 150), int(w / 50))
        bh = random.randint(int(h / 150), int(h / 50))
        instructions = get_box_instructions(bx, by, bw, bh ,color, userdata)
        
        out.append(instructions)

    return out

@callback(Output('osdViewerComponent', 'inputToPaper'),
          Input('make_random_button', 'n_clicks'),
          State('osdViewerComponent', 'viewportBounds'),
          prevent_initial_call=True)
def make_random_boxes(n_clicks, bounds):
    out = { 
        "actions": [
            {
                "type": "clearItems"
            },
            {
                "type": "drawItems",
                "itemList": generate_random_boxes(1000, bounds)
            }
        ]
    }
    return out

## This updates the mouse tracker
@callback(Output('mousePos_disp', 'children'), 
          Input('osdViewerComponent', 'curMousePosition'))
def update_mouseCoords(curMousePosition):
    return f'{int(curMousePosition["x"])},{int(curMousePosition["y"])}' if curMousePosition["x"] is not None else ''

## Update the zoom state
@callback(Output('zoomLevel_disp', 'children'), 
          Input('osdViewerComponent', 'zoomLevel'))
def updateZoomLevel(currentZoom):
    return '{:.3f}'.format(currentZoom)

## Update the viewportBounds display
@callback(Output('viewportBounds_disp', 'children'), 
          Input('osdViewerComponent', 'viewportBounds'))
def update_viewportBounds(viewPortBounds):
    vp = viewPortBounds
    return f'x: {int(vp["x"])} y: {int(vp["y"])} w: {int(vp["width"])} h: {int(vp["height"])}' 


# @callback(Output('curObject_disp', 'children'), Input('osdViewerComponent', 'curShapeObject'))
# def update_curShapeObject(curShapeObject):
#     return f'Current Selected Shape: {json.dumps(curShapeObject)}' 


@callback(Output('osdViewerComponent', 'imageSrc'), 
          Input('imageSelect', 'value'))
def update_imageSrc(imageSrc):
    return imageSrc

def createItem(data):
    print('createItem', data)
    x = get_box_instructions(data['point']['x'], 
                             data['point']['y'], 
                             data['size']['width'],
                             data['size']['height'], 
                             colors[0], 
                             {'class':classes[0]})
    out = { 
        "actions": [
            {
                "type": "drawItems",
                "itemList": [x]
            }
        ]
    }
    return out

# this is if you want to trigger deleting and item from the python side
def deleteItem(id):
    output = {'actions':[{'type':'deleteItem', 'id': id}]}
    return output

# this listens to a deletion event triggered from the client side
def itemDeleted(data):
    print('itemDeleted', data)
    return None

def propertyChanged(data):
    print('propertyChanged', data)
    return None

def mouseLeave(args):
    return None

def mouseEnter(args):
    return None

if __name__ == '__main__':
    app.run_server(debug=True)



