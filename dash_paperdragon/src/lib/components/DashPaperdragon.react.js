import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import OpenSeadragon from 'openseadragon';
import {PaperOverlay} from 'osd-paperjs-annotation';

/**
 * ExampleComponent is an example component.
 * It takes a property, `label`, and
 * displays it.
 * It renders an input with the property `value`
 * which is editable by the user.
 */
const DashPaperdragon = (props) => {
  const { id, label, setProps, value, imageSrc, zoomLevel, globalX, globalY } = props;



  const viewerRef = useRef(null);
  const [currentPtX, setCurrentPtX] = useState('');
  const [currentPtY, setCurrentPtY] = useState('');
  const [viewportX, setViewportX] = useState('');
  const [viewportY, setViewportY] = useState('');

  const [imageX, setImageX] = useState('');
  const [imageY, setImageY] = useState('');

  const [imageSnapX, setImageSnapX] = useState('');
  const [imageSnapY, setImageSnapY] = useState('');



  /* Set up the mouse handler functions */
  const setupInfoHandler = (viewer) => {
    let handler = function (event) {
      let center = viewer.viewport.getCenter(true);
      setImageSnapX(center.x);
      setImageSnapY(center.y);
    };
    let events = ['pan', 'zoom', 'rotate', 'resize'];
    events.forEach(event => viewer.addHandler(event, handler));

    let mouseCoords = function (event) {
      let viewport = viewer.viewport.viewerElementToViewportCoordinates(event.position);
      let image = viewer.viewport.viewerElementToImageCoordinates(event.position);
      setViewportX(viewport.x);
      setViewportY(viewport.y);
      setImageX(image.x);
      setImageY(image.y);

      setProps({ globalX: image.x });
      setProps({ globalY: image.y });

    }
    let leaveHandler = function (event) {
      setViewportX('');
      setViewportY('');
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
    });
    viewer.open(imageSrc);
    viewerRef.current = viewer;

    window.overlay = viewer.createPaperOverlay();

    setupInfoHandler(viewer);

  }, []);

  //   /* Track the current zoom level of the widget*/
  useEffect(() => {
    const viewer = viewerRef.current;
    viewer.addHandler('zoom', function (event) {
      const zoomValue = event.zoom;
      setProps({ zoomLevel: zoomValue });
    });
  }, []);



  /* Bind the infoHandler function to the current viewer */
  useEffect(() => {
    const viewer = viewerRef.current;
    setupInfoHandler(viewer);
  }, []);



  return (
    <div id={id}>
      ExampleComponent: {label}&nbsp;
      <div id="openseadragon-viewer" style={{ width: '800px', height: '600px' }}></div>
      <input
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
          e => setProps({ value: e.target.value })
        }
      />

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
   * A label that will be printed when this component is rendered.
   */
  label: PropTypes.string.isRequired,

  /**
   * The value displayed in the input.
   */
  value: PropTypes.string,
  /**
   *the tile source for openseadrgon
  */
  imageSrc: PropTypes.string,
  /**
   * zoomLevel of the current OSD Viewer
   */
  zoomLevel: PropTypes.number,
  /**
   * globalX of the current OSD Viewer
   */
  globalX: PropTypes.number,
  /**
   * globalY of the current OSD Viewer
   */
  globalY: PropTypes.number,
  /**
   * Dash-assigned callback that should be called to report property changes
   * to Dash, to make them available for callbacks.
   */
  setProps: PropTypes.func
};

export default DashPaperdragon;
