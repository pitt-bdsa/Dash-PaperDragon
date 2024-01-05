# AUTO GENERATED FILE - DO NOT EDIT

#' @export
dashPaperdragon <- function(id=NULL, globalX=NULL, globalY=NULL, imageSrc=NULL, label=NULL, value=NULL, zoomLevel=NULL) {
    
    props <- list(id=id, globalX=globalX, globalY=globalY, imageSrc=imageSrc, label=label, value=value, zoomLevel=zoomLevel)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'DashPaperdragon',
        namespace = 'dash_paperdragon',
        propNames = c('id', 'globalX', 'globalY', 'imageSrc', 'label', 'value', 'zoomLevel'),
        package = 'dashPaperdragon'
        )

    structure(component, class = c('dash_component', 'list'))
}
