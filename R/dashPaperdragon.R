# AUTO GENERATED FILE - DO NOT EDIT

#' @export
dashPaperdragon <- function(id=NULL, curMousePosition=NULL, curShapeObject=NULL, imageSrc=NULL, shapeList=NULL, viewPortBounds=NULL, zoomLevel=NULL) {
    
    props <- list(id=id, curMousePosition=curMousePosition, curShapeObject=curShapeObject, imageSrc=imageSrc, shapeList=shapeList, viewPortBounds=viewPortBounds, zoomLevel=zoomLevel)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'DashPaperdragon',
        namespace = 'dash_paperdragon',
        propNames = c('id', 'curMousePosition', 'curShapeObject', 'imageSrc', 'shapeList', 'viewPortBounds', 'zoomLevel'),
        package = 'dashPaperdragon'
        )

    structure(component, class = c('dash_component', 'list'))
}
