import React, { useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';
import OpenSeadragon from 'openseadragon';
import paper, { Path, Point, Color } from 'paper';

const OpenseadragonViewer = (props) => {

    const { imageSrc, point_list } = props;

    const viewerRef = useRef(null);
    const paperRef = useRef(null);
    const [currentPtX, setCurrentPtX] = useState('');
    const [currentPtY, setCurrentPtY] = useState('');
    const [viewportX, setViewportX] = useState('');
    const [viewportY, setViewportY] = useState('');

    const [imageX, setImageX] = useState('');
    const [imageY, setImageY] = useState('');

    const [imageSnapX, setImageSnapX] = useState('');
    const [imageSnapY, setImageSnapY] = useState('');
  
  useEffect(() => {
    console.log("adding osd to window")
    window.OpenSeadragon = OpenSeadragon;

    return () => {
      delete window.OpenSeadragon;
    };
  }, []);

  useEffect(() => {
    // Initialize OpenSeadragon
    
    const viewer = OpenSeadragon({
      id: 'openseadragon-viewer',
      prefixUrl: '//openseadragon.github.io/openseadragon/images/', // Update with your image path
    });
    viewer.open(imageSrc);
    viewerRef.current = viewer;

  }, []);

  const handleAnnotationItemClick = (event) => {
    const paperScope = paperRef.current;
    const hitResult = paperScope.project.hitTest(event.point);

    if (hitResult && hitResult.item) {
      console.log('hit', hitResult.item);
      setCurrentPtX(hitResult.item._bounds['011'].rect.x);
      setCurrentPtY(hitResult.item._bounds['011'].rect.y);
    }
  }

  useEffect(() => {
    const viewer = viewerRef.current;

    const paperCanvas = document.createElement('canvas');
    paperCanvas.id = 'paper-canvas';
    paperCanvas.style.zIndex = '1'; // Place the Paper.js canvas above the OpenSeadragon canvas
    paperCanvas.style.position = 'absolute';
    paperCanvas.style.width = viewer.canvas.clientWidth + 'px';
    paperCanvas.style.height = viewer.canvas.clientHeight + 'px';
    paperCanvas.style.top = viewer.canvas.style.top;
    paperCanvas.style.left = viewer.canvas.style.left;
    
    document.getElementsByClassName('openseadragon-canvas')[0].appendChild(paperCanvas);

    const paperScope = new paper.PaperScope();
    console.log(viewer.canvas);
    paperScope.setup(paperCanvas);
    paperScope.view.onClick = handleAnnotationItemClick;

    paperRef.current = paperScope;

    console.log(viewer)
    console.log(viewer.canvas.clientWidth, viewer.canvas.clientHeight);
  }, []);

  useEffect(() => {
    const viewer = viewerRef.current;
    import('osd-paperjs-annotation').then((module) => {
      viewer.addHandler('open', () => {
        let annotationToolkit = new module.OSDPaperjsAnnotation.AnnotationToolkit(viewer);
        annotationToolkit.addAnnotationUI({autoOpen:true});
        // let paperOverlay = new module.OSDPaperjsAnnotation.PaperOverlay(viewer);
        // console.log("test", paperOverlay);
      });
    });
  }, []);

  function updateOverlayScale() {
    const viewer = viewerRef.current;
    const paperScope = paperRef.current;

    const zoom = viewer.viewport.getZoom(); // Get current zoom level
    console.log("zoom", zoom);
  
    // Scale the Paper.js overlay based on the zoom level
    const scale = zoom;
    
    paperScope.view.scale(scale);

    paperScope.project.getItems({ recursive: true }).forEach((item) => {
      item.scale(scale); // Scale each item
      // You can also adjust other properties here if needed, such as position or size
    });
    
  }

  useEffect(() => {
    const viewer = viewerRef.current;
    viewer.addHandler('zoom', function() {
      // updateOverlayScale(); 
    });
  }, []);



  const removePoints = () => {
    const paperScope = paperRef.current;
    paperScope.project.activeLayer.removeChildren();
    paperScope.view.draw();

    enableNavAndPan();
  }

  const plotPoints = () => {

    const viewer = viewerRef.current;
    const paperScope = paperRef.current;
    console.log("pt list", point_list)
    for (let i = 0; i < point_list.length; i++) {

      const randomColor = new Color(Math.random(), Math.random(), Math.random());
      const randomX = point_list[i][0] * viewer.canvas.clientWidth;
      const randomY = point_list[i][1] * viewer.canvas.clientHeight;
      const point = new Point(randomX, randomY);
      
      const path = new paperScope.Path.Rectangle(point, 20);
      path.rescale = {strokeWidth: 2};
      path.fillColor = randomColor;

    }
    disableNavAndPan();
  }

  const disableNavAndPan = () => {
    const viewer = viewerRef.current;
    viewer.setMouseNavEnabled(false);
      viewer.setPanEnabled(false);
  }

  const enableNavAndPan = () => {
    const viewer = viewerRef.current;
    viewer.setMouseNavEnabled(true);
      viewer.setPanEnabled(true);
  }

  const addRect = () => {
    const viewer = viewerRef.current;
    
    var rect = document.createElement("div");
    rect.id = 'rectangle';
    rect.style.backgroundColor = 'rgba(0, 0, 255, 0.5)'; // Blue with 50% opacity
    var image = document.createElement("img")
    image.id = 'right-arrow-overlay';
    image.src = 'http://upload.wikimedia.org/wikipedia/commons/7/7a/Red_Arrow_Right.svg';
    image.width = '20';

    viewer.addOverlay({
      element: rect,
      px: 5500,
      py: 5500,
      width: 3500,
      height: 1500,
      checkResize: false,
      placement: OpenSeadragon.OverlayPlacement.RIGHT
    });
  }

  const addCircle = () => {
    const viewer = viewerRef.current;
    
    var circle = document.createElement("div");
    circle.id = 'circle';
    circle.style.backgroundColor = 'rgba(255, 0, 0, 0.5)'; // Blue with 50% opacity
    circle.style.borderRadius = '50%';
    var image = document.createElement("img")
    image.id = 'right-arrow-overlay';
    image.src = 'http://upload.wikimedia.org/wikipedia/commons/7/7a/Red_Arrow_Right.svg';
    image.width = '20';
    // rect.appendChild(image);

    // // Create and add a rcircle
    // inside a function the width and height | px and py work at a different scale altogether
    viewer.addOverlay({
      element: circle,
      px: 7500,
      py: 7500,
      width: 3500,
      height: 3500,
      checkResize: false,
      placement: OpenSeadragon.OverlayPlacement.RIGHT
    });
  }

  const addTriangle = () => {
    const viewer = viewerRef.current;
    
    var triangle = document.createElement("div");
    triangle.id = 'triangle';
    triangle.style.width = '0';
    triangle.style.height = '0';
    // triangle.style.backgroundColor = 'rgba(0, 255, 0, 0.5)'; // Blue with 50% opacity
    triangle.style.borderLeft = '25px solid transparent';
    triangle.style.borderRight = '25px solid transparent';
    triangle.style.borderBottom = '50px solid rgba(0, 255, 0, 0.5)'
    var image = document.createElement("img")
    image.id = 'right-arrow-overlay';
    image.src = 'http://upload.wikimedia.org/wikipedia/commons/7/7a/Red_Arrow_Right.svg';
    image.width = '20';
    // rect.appendChild(image);

    // // Create and add a rcircle
    // inside a function the width and height | px and py work at a different scale altogether
    viewer.addOverlay({
      element: triangle,
      px: 7500,
      py: 7500,
      width: 3500,
      height: 3500,
      checkResize: false,
      placement: OpenSeadragon.OverlayPlacement.RIGHT
    });
  }

  const setupInfoHandler = (viewer) => {
    let handler= function(event){
      let center = viewer.viewport.getCenter(true);
      setImageSnapX(center.x);
      setImageSnapY(center.y);
    };
    let events = ['pan','zoom','rotate','resize'];
    events.forEach(event=>viewer.addHandler(event, handler));

    let mouseCoords = function(event){
      let viewport = viewer.viewport.viewerElementToViewportCoordinates(event.position);
      let image = viewer.viewport.viewerElementToImageCoordinates(event.position);
      setViewportX(viewport.x);
      setViewportY(viewport.y);
      setImageX(image.x);
      setImageY(image.y);
  }
  let leaveHandler = function(event){
    setViewportX('');
    setViewportY('');
    setImageX('');
    setImageY('');
  }
  new OpenSeadragon.MouseTracker({element: viewer.element, moveHandler: mouseCoords, leaveHandler: leaveHandler});
  }

  useEffect(() => {
    const viewer = viewerRef.current;
    setupInfoHandler(viewer);
  }, []);

  useEffect(() => {
    const viewer = viewerRef.current;
    viewer.viewport.panTo(new OpenSeadragon.Point(Number(imageSnapX), Number(imageSnapY)), true);
  }, [imageSnapX, imageSnapY]);

  const handleImageSnapXChange = (e) => {
    setImageSnapX(e.target.value);
  };

  const handleImageSnapYChange = (e) => {
    setImageSnapY(e.target.value);
  };

    return (
      <>
      <div class="image-info cursor-info">
        <div class="viewport-coords">
          <label>Viewport coordinates:</label>
          <input type="number" value={viewportX} class="x" disabled />
          <input type="number" value={viewportY} class="y" disabled />
        </div>
        <div class="image-coords">
          <label>Image coordinates:</label>
          <input type="number" value={imageX} class="x" disabled />
          <input type="number" value={imageY} class="y" disabled />
        </div>
        <div class="image-snapshot">
          <label>Image coordinates:</label>
          <input type="number" value={imageSnapX} onChange={handleImageSnapXChange} class="x" />
          <input type="number" value={imageSnapY} onChange={handleImageSnapYChange} class="y" />
        </div>
        <div class="annotation-coords">
          <label>Annotation coordinates:</label>
          <input type="number" value={currentPtX} class="x" />
          <input type="number" value={currentPtY} class="y" />
        </div>
      </div>
        <div>
            <div id="openseadragon-viewer" style={{ width: '800px', height: '600px' }}></div>
            {/* <button id="Rectangle" onClick={addRect}>Rectangle</button>
            <button id="Circle" onClick={addCircle}>Circle</button>
            <button id="Triangle" onClick={addTriangle}>Triangle</button> */}
            <button id="Plot" onClick={plotPoints}> Plot Points</button>
            <button id="Clear" onClick={removePoints}> Clear Points</button>
        </div>
        </>
    );
}


OpenseadragonViewer.propTypes = {

    imageSrc: PropTypes.string,
    point_list: PropTypes.arrayOf(
      PropTypes.arrayOf(PropTypes.number)
    ),
};

export default OpenseadragonViewer;