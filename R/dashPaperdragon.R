# AUTO GENERATED FILE - DO NOT EDIT

#' @export
dashPaperdragon <- function(id=NULL, config=NULL, curMousePosition=NULL, inputToPaper=NULL, outputFromPaper=NULL, tileSources=NULL, viewportBounds=NULL, zoomLevel=NULL) {
    
    props <- list(id=id, config=config, curMousePosition=curMousePosition, inputToPaper=inputToPaper, outputFromPaper=outputFromPaper, tileSources=tileSources, viewportBounds=viewportBounds, zoomLevel=zoomLevel)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'DashPaperdragon',
        namespace = 'dash_paperdragon',
        propNames = c('id', 'config', 'curMousePosition', 'inputToPaper', 'outputFromPaper', 'tileSources', 'viewportBounds', 'zoomLevel'),
        package = 'dashPaperdragon'
        )

    structure(component, class = c('dash_component', 'list'))
}
