# AUTO GENERATED FILE - DO NOT EDIT

#' @export
dashPaperdragon <- function(id=NULL, config=NULL, curMousePosition=NULL, imageSrc=NULL, inputToPaper=NULL, outputFromPaper=NULL, viewportBounds=NULL, zoomLevel=NULL) {
    
    props <- list(id=id, config=config, curMousePosition=curMousePosition, imageSrc=imageSrc, inputToPaper=inputToPaper, outputFromPaper=outputFromPaper, viewportBounds=viewportBounds, zoomLevel=zoomLevel)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'DashPaperdragon',
        namespace = 'dash_paperdragon',
        propNames = c('id', 'config', 'curMousePosition', 'imageSrc', 'inputToPaper', 'outputFromPaper', 'viewportBounds', 'zoomLevel'),
        package = 'dashPaperdragon'
        )

    structure(component, class = c('dash_component', 'list'))
}
