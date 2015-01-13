# exampleA11.py
# IN electrop.png
# OUT finalMarkers.png blobsContours.png

## TITLE #######################################################################
# Blobs segmentation in an electrophoresis gel

## DESCRIPTION #################################################################
# This (historical) example is one of the first applications of the marker-
# controlled watershed segmentation. The initial image is a two-dimensional
# electrophoresis gel. This technique allows to separate and identify proteins.
# This example illustrates the different steps of the blobs segmentation. 

## SCRIPT ######################################################################
# Importing the mamba module and the mambaComposed package
from mamba import *
import mambaComposed as mC
import mambaExtra as mE

# Reading the initial image.
imIn = imageMb('electrop.png')

# Defining working images.
imWrk1 = imageMb(imIn)
blobsMarkers = imageMb(imIn, 1)
backgroundMarker= imageMb(imIn, 1)
imWrk2 = imageMb(imIn, 1)
finalMarkers = imageMb(imIn, 1)
blobsContours = imageMb(imIn, 1)

# The initial image is filtered with an alternate filter of size 2.
mC.alternateFilter(imIn, imWrk1, 2, True)

# The minima of this filtered image can be used as markers of the blobs.
mC.minima(imWrk1, blobsMarkers)

# Then, we must generate a background marker. This marker can be obtained by
# a marker-controlled watershed of the initial image.
mC.markerControlledWatershed(imIn, blobsMarkers, imWrk1)
threshold(imWrk1, backgroundMarker, 1, 255)

# The two sets of markers are merged. We must however insure that they are
# separated by at least one pixel.
mC.dilate(backgroundMarker, imWrk2)
diff(blobsMarkers, imWrk2, blobsMarkers)
logic(blobsMarkers, backgroundMarker, finalMarkers, "sup")
finalMarkers.save('finalMarkers.png')
# The contours of the blobs are obtained by a marker-controlled watershed of
# the gradient image.
mC.gradient(imIn, imWrk1)
mC.markerControlledWatershed(imWrk1, finalMarkers, imWrk1)
threshold(imWrk1, blobsContours, 1, 255)

# Superposing the result to the original image and saving the result.
mE.multiSuperpose(imIn, blobsContours)
pal = mE.tagOneColorPalette(255, (255,0,0))
imIn.setPalette(pal)
imIn.save('blobsContours.png')
