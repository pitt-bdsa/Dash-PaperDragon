import React, { useState, useEffect, useRef } from 'react';
import PropTypes, { shape } from 'prop-types';
import OpenSeadragon from 'openseadragon';
import { AnnotationToolkit, RectangleTool } from 'osd-paperjs-annotation';

/* OpenSeadragon and PaperJS Component that allows Dash to interact with the OpenSeadragon viewer */
const DashPaperdragon = (props) => {
  const { id, // id of the div element created for this viewer
    config, // configuration options for the component
    tileSources, // the image source to view; can change depending on user input
    zoomLevel, // output property, sent by the component back to dash
    curMousePosition, // output property, sent by the component back to dash
    viewportBounds, // output property, sent by the component back to dash
    outputFromPaper, // output property, seny by the component back to dash
    inputToPaper, // input property, telling the component how to update the paper overlay
    tileSourceProps, // input property, updates tileLayers  x offset, y, rotation or opacity
    setProps,
  } = props;

  // Set up references to common variables
  const viewerRef = useRef(null);
  const tiledImageRef = useRef(null);
  const overlayRef = useRef(null);
  const toolkitRef = useRef(null);
  const paperRef = useRef(null);
  const hoveredItemRef = useRef(null);
  const mousePosRef = useRef({ x: 0, y: 0 });
  const paperMousePosRef = useRef({ x: 0, y: 0 });
  const keyDownRef = useRef(null);
  const creatingRef = useRef(null);

  /** Define actions */
  const actionsRef = useRef({
    drawItems,
    clearItems,
    cycleProp,
    cyclePropReverse,
    deleteItem,
    dashCallback,
    newItem,
  });

  function raiseEvent(eventName, data) {
    executeCallbacks(eventName, data);
  }


  /** Create viewer within a useEffect */
  useEffect(() => {
    if (!viewerRef.current) {
      createViewer();
    }
    // Clean up the viewer when the component unmounts
    return () => {
      if (viewerRef.current) {
        viewerRef.current.destroy();
        viewerRef.current = null;
        tiledImageRef.current = null;
      }
    };
  }, []);


  useEffect(() => {
    const viewer = viewerRef.current;
    // console.log(tileSourceProps, "are being updated")

    if (tileSourceProps) {
      for (let i = 0; i < tileSourceProps.length; i++) {
        let curTileSource = viewer.world.getItemAt(i);
        // for (let prop in tileSourceProps[i]) {
        if (curTileSource) {
          // console.log(tileSourceProps[i].opacity);
          //Updating opacity, position and rotation...
          //Future state could only update properties that have changed, but these operations seem
          //fast enough that it may not be necessary
          curTileSource.setOpacity(tileSourceProps[i].opacity);
          curTileSource.setPosition({ x: tileSourceProps[i].x, y: tileSourceProps[i].y })
          curTileSource.setRotation(tileSourceProps[i].rotation);
        }
      }
      //Iterate through the tilesources and change the opacity
    }
  }, [tileSourceProps]);


  /** add reactive components via useEffect, listening to property changes */

  /** Open an image based on imageSrc property */
  useEffect(() => {
    if (viewerRef.current && tileSources) {
      // Update the image source
      viewerRef.current.open(tileSources);
    }
  }, [tileSources]);

  /* respond to changes in the inputToPaper property */
  useEffect(handleInputToPaper, [inputToPaper]);
  function handleInputToPaper() {
    // if the tiledImage or inputToPaper are null, nothing to do, just return
    if (!inputToPaper || !tiledImageRef.current) {
      return;
    }

    for (const action of inputToPaper.actions) {
      let func = actionsRef.current[action.type];
      if (!func) {
        alert('No action defined for type ' + action.type);
      } else {
        // console.log('Action:', action);
        func(action);
      }
    }



    // clear the inputToPaper property so we can listen for more changes
    setProps(inputToPaper, null);
  }

  // Functions that can be accessed by Dash via actions and/or bindings
  function clearItems() {
    tiledImageRef.current.paperLayer.clear();
  }

  function drawItems(action) {
    const list = action.itemList || [];
    if (!list.length) {
      console.warning('No items were provided in the itemList property');
    }
    for (const i of list) {
      const item = makeItem(i);
      tiledImageRef.current.addPaperItem(item);
    }
  }

  function deleteItem(opts) {
    if (opts.item) {
      opts.item.remove();
    } else if (opts.id) {
      console.log(`deleteItem with id ${opts.id}`);
      tiledImageRef.current.paperItems.filter(i => i.data.userdata.objectId == opts.id).forEach(item => item.remove());
    } else {
      console.error('deleteItem  called without item or id field');
    }

  }

  function newItem(opts) {
    if (creatingRef.current) {
      const item = creatingRef.current;

      paperRef.current.rectangleTool.deactivate(true);
      if (item.isPlaceholder) {
        item.remove();
        console.log('Rectangle aborted');
      } else {
        item.selected = false;
        console.log('Item created', item);
        // makeItem(config.defaultStyle);
        const bounds = item.bounds;
        raiseEvent('item-created', {
          point: { x: bounds.x, y: bounds.y },
          size: { width: bounds.width, height: bounds.height }
        })
        item.remove();
        creatingRef.current = null;
      }

    } else {
      console.log('newItem called', opts, paperRef.current.rectangleTool);
      let placeholder = toolkitRef.current.makePlaceholderItem(config.defaultStyle);

      let item = placeholder.paperItem;

      if (config.defaultStyle.fillOpacity !== undefined) {
        item.fillColor.alpha = config.defaultStyle.fillOpacity;
      }

      item.selected = true;
      item.isPlaceholder = true;
      tiledImageRef.current.addPaperItem(item);
      creatingRef.current = item;
      item.on('item-replaced', (ev) => creatingRef.current = ev.item);
      paperRef.current.rectangleTool.activate();
    }

  }

  function cycleProp(opts, bound, reverse) {
    let item = opts.item;
    let prop = bound.property;
    if (!item || !prop) {
      console.error('There was a problem with the item or property');
      return;
    }

    // look up the array of options for this property from the config object
    let propArray = config.properties[prop];
    if (!propArray || !Array.isArray(propArray)) {
      console.error(`config.${prop} is ${typeof propArray}; it must be an Array to use cycleProp`);
      return;
    }

    // figure out what the new value for this property is, and set it on the item.data object
    let currentVal = item.data.userdata[prop];
    let newIndex = (propArray.indexOf(currentVal) + (reverse ? propArray.length - 1 : 1)) % propArray.length;
    let newVal = propArray[newIndex];
    item.data.userdata[prop] = newVal;

    // look up a style that goes with this property key:value pair
    let style = config.styles && config.styles[prop] && config.styles[prop][newVal];
    if (style) {
      item.set(style);
    }

    // refresh the fill opacity and rescalable properties
    if (item.fillColor) {
      item.fillColor.alpha = item.fillOpacity;
    }
    item.applyRescale();

    raiseEvent('property-changed', { item: item.data.userdata, property: prop });

  }

  function cyclePropReverse(opts, bound) {
    cycleProp(opts, bound, true);
  }

  function dashCallback(action, data) {
    console.log('dashCallback', action, data);
    setProps({ outputFromPaper: { callback: action.callback, data: data } });
  }


  function createViewer() {

    // if viewer exists, return immediately
    if (viewerRef.current) {
      return;
    }

    // Create a new viewer
    const viewer = viewerRef.current = OpenSeadragon({
      id: id,
      prefixUrl: '//openseadragon.github.io/openseadragon/images/', // Update with your image path
      /* TO DO: add additional properties like navigator */
    });

    viewer.addHandler('close', () => tiledImageRef.current = null);
    viewer.world.addHandler('add-item', ev => tiledImageRef.current = ev.item);

    // suppress default OSD keydown handling for a subset of keys
    viewer.addHandler('canvas-key', event => {
      if (['q', 'w', 'e', 'r', 'a', 's', 'd', 'f'].includes(event.originalEvent.key)) {
        event.preventDefaultAction = true;
      }
    });
    // add mouse tracker and other handlers
    setupInfoHandler(viewer);
    setupPaper();

    // for easier debugging: attach objects to window
    window.viewer = viewer;
  }

  function setupPaper() {
    const tk = new AnnotationToolkit(viewerRef.current, { overlay: null, addUI: false });
    console.log('Toolkit:', tk);
    toolkitRef.current = tk;

    const overlay = overlayRef.current = tk.overlay;
    // for easier debugging: attach objects to window
    window.overlay = overlay;
    // grab a reference to paper object
    paperRef.current = overlay.paperScope;

    paperRef.current.rectangleTool = new RectangleTool(overlay.paperScope);

    // add key handlers to the paper view. TODO: this could be handled by mousetracker too I suppose 
    const view = paperRef.current.view;
    view.onKeyUp = ev => {
      keyDownRef.current = false;
      let hitResult = paperRef.current.project.hitTest(paperMousePosRef.current);
      let item = hitResult && hitResult.item;

      executeBoundEvents({ event: 'keyUp', key: ev.key, meta: ev.meta },
        { mousePosition: mousePosRef.current, item: item });
    }
    view.onKeyDown = ev => {
      if (keyDownRef.current) {
        return;
      }
      keyDownRef.current = ev.key;
      let hitResult = paperRef.current.project.hitTest(paperMousePosRef.current);
      let item = hitResult && hitResult.item;

      executeBoundEvents({ event: 'keyDown', key: ev.key, meta: ev.meta },
        { mousePosition: mousePosRef.current, item: item });
    }

    view.onMouseMove = ev => {
      paperMousePosRef.current = ev.point;
    }

  }


  /* Set up the mouse handler functions */
  function setupInfoHandler(viewer) {

    // TO DO: Add or deal with resize handler 
    // let events = ['pan', 'zoom', 'rotate', 'resize'];

    // TODO: add mouse click handler logic, coordinating with paper overlay

    viewer.addHandler('zoom', function (event) {
      const zoomValue = event.zoom;
      setProps({ zoomLevel: zoomValue });
    });

    function onViewportChange(event) {
      let tiledImage = viewer.world.getItemAt(0);
      if (tiledImage) {
        let rect = tiledImage.viewportToImageRectangle(viewer.viewport.getBounds())
        setProps({ viewportBounds: rect });
      }

    }
    viewer.addHandler('viewport-change', onViewportChange);
    viewer.addHandler('open', onViewportChange);


    let moveHandler = function (event) {
      let tiledImage = viewer.world.getItemAt(0);
      if (tiledImage) {
        let imageCoords = tiledImage.viewerElementToImageCoordinates(event.position);
        mousePosRef.current = imageCoords;
        setProps({ curMousePosition: imageCoords });
      }

    }

    let leaveHandler = function () {
      setProps({ curMousePosition: { x: null, y: null } });
    }

    // create a mousetracker for the viewer, and hook up the handlers
    new OpenSeadragon.MouseTracker({ element: viewer.element, moveHandler: moveHandler, leaveHandler: leaveHandler });

  }


  function badAction(a) {
    alert('Bad action, see console');
    console.warning('Bad action:', a);
  }


  function makeItem(definition) {
    // TODO: make this fully configurable from the dash side via config
    if (!definition.paperType) {
      console.error('makeItem requires the object type in the paper field (e.g. paper: Path.Rectangle)');
      return;
    }
    let constructor = paperRef.current;
    for (const part of definition.paperType.split('.')) {
      constructor = constructor[part];
      if (!constructor) {
        console.error(`Bad paper constructor: paper.${definition.paper} does not exist`);
      }
    }

    if (!Array.isArray(definition.args)) {
      definition.args = [definition.args];
    }
    if (!definition.userdata instanceof Object) {
      definition.userdata = {
        userdata: definition.userdata
      };
    }

    let item = new constructor(...definition.args);
    if (item.fillColor) {
      item.fillColor.alpha = item.fillOpacity;
    }

    // bind some extra properties to keep track of where in the array we are, and the original definition of the object
    Object.assign(item.data, definition);

    // add mouseEnter and mouseLeave handlers
    item.onMouseEnter = event => {
      console.log(`Item is ${event.target.data.fillColor}`);
      setProps({ "curShapeObject": event.target.data });
      hoveredItemRef.current = event.target.data;
      executeBoundEvents({ event: 'mouseEnter' }, { item: event.target.data });
    }
    item.onMouseLeave = event => {
      setProps({ "curShapeObject": null });
      hoveredItemRef.current = null;
      executeBoundEvents({ event: 'mouseLeave' }, { item: event.target.data });
    }

    return item;
  }

  function executeCallbacks(eventName, data) {
    if (config.callbacks) {
      let callbacks = config.callbacks.filter(a => a.eventName == eventName).map(a => a.callback);
      for (const cb of callbacks) {
        dashCallback({ callback: cb }, data);
      }
    }
  }

  function executeBoundEvents(filters, opts) {
    if (config.eventBindings) {
      let enterActions = config.eventBindings.filter(a => match(a, filters));
      for (const a of enterActions) {
        const func = actionsRef.current[a.action];
        if (func) {
          func(opts, a);
        } else {
          badAction(a);
        }
      }
    }
  }

  function match(obj, filters) {
    for (const [key, value] of Object.entries(obj)) {
      if (key in filters && filters[key] !== value) {
        return false
      }
    }
    return true;
  }

  return (

    <div >

      <div id={id} style={{ width: '800px', height: '600px' }}></div>
    </div>
  );
}

DashPaperdragon.defaultProps = {};

DashPaperdragon.propTypes = {
  /**
   * The ID used to identify this component in Dash callbacks.
   */
  id: PropTypes.string,
  /**
   * config is a dictionary of options for setting up the component and initial rendering
   */
  config: PropTypes.object,
  /**
   *the tile source for openseadragon
  */
  tileSources: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.array]),

  /**
   * zoomLevel of the current OSD Viewer
   */
  zoomLevel: PropTypes.number,
  /**
   *  Current Mouse Position in Image Coordinates
   *  */
  curMousePosition: PropTypes.object,
  /**
   * viewportBounds of the current OSD Viewer
   */
  viewportBounds: PropTypes.object,
  /**
   * data sent from paper back to dash
   */
  outputFromPaper: PropTypes.object,
  /**
   * data sent from dash to paper
   */
  inputToPaper: PropTypes.object,
  /**
   * sent from dash to update x offset, y offset, rotation, or opacity of the image
   */

  tileSourceProps: PropTypes.array,

  /**
   * Dash-assigned callback that should be called to report property changes
   * to Dash, to make them available for callbacks.
   */
  setProps: PropTypes.func
};

export default DashPaperdragon;



//https://legacy.reactjs.org/warnings/invalid-hook-call-warning.html
/* <input
      value={value}
      onChange={
        /*
            * Send the new value to the parent component.
            * setProps is a prop that is automatically supplied
            * by dash's front-end ("dash-renderer").
            * In a Dash app, this will update the component's
            * props and send the data back to the Python Dash
            * app server if a callback uses the modified prop as
            * Input or State.
            */
// e => setProps({ value: e.target.value })
// / Assuming your array is called 'data' and the column with the unique value is 'columnName'
// const rowIndex = data.findIndex(row => row.columnName === uniqueValue);

// if (rowIndex !== -1) {
//   // Update the row at the found index with the desired changes
//   data[rowIndex].columnName = newValue;
// }
