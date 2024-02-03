% Auto-generated: do not edit by hand
\name{dashPaperdragon}

\alias{dashPaperdragon}

\title{DashPaperdragon component}

\description{

}

\usage{
dashPaperdragon(id=NULL, baseImageWidth=NULL, config=NULL,
curMousePosition=NULL, inputToPaper=NULL,
outputFromPaper=NULL, tileSourceProps=NULL,
tileSources=NULL, viewportBounds=NULL, zoomLevel=NULL)
}

\arguments{
\item{id}{Character. The ID used to identify this component in Dash callbacks.}

\item{baseImageWidth}{Numeric. }

\item{config}{Named list. config is a dictionary of options for setting up the component and initial rendering}

\item{curMousePosition}{Named list. Current Mouse Position in Image Coordinates}

\item{inputToPaper}{Named list. data sent from dash to paper}

\item{outputFromPaper}{Named list. data sent from paper back to dash}

\item{tileSourceProps}{Unnamed list. sent from dash to update x offset, y offset, rotation, or opacity of the image}

\item{tileSources}{Character | unnamed list. the tile source for openseadragon}

\item{viewportBounds}{Named list. viewportBounds of the current OSD Viewer}

\item{zoomLevel}{Numeric. zoomLevel of the current OSD Viewer}
}

\value{named list of JSON elements corresponding to React.js properties and their values}

