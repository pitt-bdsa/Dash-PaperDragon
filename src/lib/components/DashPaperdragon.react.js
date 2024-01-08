import React, { useState, useEffect, useRef } from 'react';
import PropTypes, { shape } from 'prop-types';
import OpenSeadragon from 'openseadragon';
import { PaperOverlay } from 'osd-paperjs-annotation';

/* OpenSeadragon and PaperJS Component that allows Dash to interact with the OpenSeadragon viewer */
const DashPaperdragon = (props) => {
  const { id, setProps, imageSrc, zoomLevel, curMousePosition, viewPortBounds, shapeList, curShapeObject } = props;
  const viewerRef = useRef(null);
  // const [viewportX, setViewportX] = useState('');
  // const [viewportY, setViewportY] = useState('');

  const [imageX, setImageX] = useState('');
  const [imageY, setImageY] = useState('');

  /* TO DO... maybe separate the handlers for on zoom, pan and resize so I am not updating all the properties
every time; hwoever this may be ok since the handlers are only called when the event occurs */

  /* Set up the mouse handler functions */
  const setupInfoHandler = (viewer) => {

    // TO DO: Add or deal with resize handler 
    // let events = ['pan', 'zoom', 'rotate', 'resize'];


    let mouseCoords = function (event) {
      let viewport = viewer.viewport.viewerElementToViewportCoordinates(event.position);
      let image = viewer.viewport.viewerElementToImageCoordinates(event.position);

      /* TO DO: Clarify diff between setImageX and setProps in terms of react functionality */
      // setImageX(image.x);
      // setImageY(image.y);
      // setProps({ globalX: image.x });
      // setProps({ globalY: image.y });
      setProps({ curMousePosition: image })


    }
    let leaveHandler = function (event) {
      // setViewportX('');
      // setViewportY('');
      setImageX('');
      setImageY('');
    }
    new OpenSeadragon.MouseTracker({ element: viewer.element, moveHandler: mouseCoords, leaveHandler: leaveHandler });
  }


  useEffect(() => {
    // Initialize OpenSeadragon
    const viewer = OpenSeadragon({
      id: 'openseadragon-viewer',
      prefixUrl: '//openseadragon.github.io/openseadragon/images/', // Update with your image path
      /* TO DO: add additional properties like navigator */
    });
    viewer.open(imageSrc);
    viewerRef.current = viewer;

    window.viewer = viewer; // for debugging
    window.overlay = viewer.createPaperOverlay();
    window.paper = window.overlay.paperScope;

    setupInfoHandler(viewer);

  }, []);


  function bindDashPointList(tiledImage, shapeList) {

    for (let shape of shapeList.pointList) {

      let curRect = new paper.Path.Rectangle({
        point: [shape.x, shape.y],
        size: [shape.width, shape.height],
        strokeColor: shape.color,
        fillColor: shape.color,
        rescale: {
          strokeWidth: 1
        }
      });
      shape.PaperItem = curRect;
      tiledImage.addPaperItem(curRect);

      curRect.fillColor.alpha = 0.2;
      curRect.onMouseEnter = function (event) { console.log(shape.color); setProps({ "curShapeObject": shape }) }
      curRect.onMouseLeave = function (event) { console.log(shape.color, "says goodbye") }
    }
  }


  /* Track the current zoom level of the widget*/
  useEffect(() => {
    const viewer = viewerRef.current;
    viewer.addHandler('zoom', function (event) {
      const zoomValue = event.zoom;
      setProps({ zoomLevel: zoomValue });
    });
  }, []);

  /* Track the current viewport of the widget*/
  useEffect(() => {
    const viewer = viewerRef.current;
    viewer.addHandler('viewport-change', function (event) {
      let rect = viewer.viewport.viewportToImageRectangle(viewer.viewport.getBounds())

      setProps({ viewPortBounds: rect });

    });
  }, []);

  /* Bind the infoHandler function to the current viewer */
  useEffect(() => {
    const viewer = viewerRef.current;
    setupInfoHandler(viewer);
  }, []);

  /* Create something to detect changes in the shapeList array */
  useEffect(() => {

    try {
      const viewer = viewerRef.current;
      let tiledImage = viewer.world.getItemAt(0);
      console.log(tiledImage)
      if (tiledImage) {

        tiledImage.paperLayer.clear();
        bindDashPointList(tiledImage, shapeList);
      }
    }
    catch (error) {
      console.log(error)
    }

  }, [shapeList]);


  return (

    <div id={id} >

      <div id="openseadragon-viewer" style={{ width: '800px', height: '600px' }}></div>
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
   * shapeList is a list of shapes to be drawn on the image
   */
  shapeList: PropTypes.object,
  /**
   *the tile source for openseadragon
  */
  imageSrc: PropTypes.string,
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
  viewPortBounds: PropTypes.object,
  /**
   * 
   * curShapeObject is the current shape object that was most recently moused over  
   */
  curShapeObject: PropTypes.object,
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