# AUTO GENERATED FILE - DO NOT EDIT

#' @export
dashPaperdragon <- function(id=NULL, baseImageWidth=NULL, config=NULL, curMousePosition=NULL, curShapeObject=NULL, inputToPaper=NULL, outputFromPaper=NULL, tileSourceProps=NULL, tileSources=NULL, viewerHeight=NULL, viewerWidth=NULL, viewportBounds=NULL, zoomLevel=NULL) {
    
    props <- list(id=id, baseImageWidth=baseImageWidth, config=config, curMousePosition=curMousePosition, curShapeObject=curShapeObject, inputToPaper=inputToPaper, outputFromPaper=outputFromPaper, tileSourceProps=tileSourceProps, tileSources=tileSources, viewerHeight=viewerHeight, viewerWidth=viewerWidth, viewportBounds=viewportBounds, zoomLevel=zoomLevel)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'DashPaperdragon',
        namespace = 'dash_paperdragon',
        propNames = c('id', 'baseImageWidth', 'config', 'curMousePosition', 'curShapeObject', 'inputToPaper', 'outputFromPaper', 'tileSourceProps', 'tileSources', 'viewerHeight', 'viewerWidth', 'viewportBounds', 'zoomLevel'),
        package = 'dashPaperdragon'
        )

    structure(component, class = c('dash_component', 'list'))
}
