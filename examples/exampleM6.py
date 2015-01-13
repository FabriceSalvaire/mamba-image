# exampleM6.py
# OUT steiner3D.png

## TITLE #######################################################################
# Creating Steiner polyhedrons in 3D

## DESCRIPTION #################################################################
# This example shows you how to construct Steiner polyhedrons with dilations.
# It shows 3D image creation, display and use in computations. This example
# is also a good introduction to the various 3D grids and their directions.

## SCRIPT ######################################################################
# Importing the mamba module, the mambaComposed package and the mambaExtra 
# module
from mamba3D import *
from mamba import *
from mambaComposed import *
from mambaExtra import *
    
def steiner3D(imOut, n, directions, grid=DEFAULT_GRID3D):
    """
    Steiner polyhedrons are built by dilating a central pixel along
    a given direction then dilating the result along another direction
    and repeating the process. 'directions' is the list of directions
    according to 'grid'. 'n' indicates the number of times the operation
    is repeated (the size of the resulting polyhedron). This is not 
    a processing function, it is just meant to draw polyhedrons so there
    is only an output 'imOut'. The display is updated at the end.
    """
    imOut.reset()
    (w,h) = imOut.getSize()
    l = imOut.getLength()
    
    v = computeMaxRange(imOut[0])[1]
    imOut.setPixel(v, (w/2,h/2,l/2))
    
    ses = []
    for d in directions:
        ses.append(structuringElement3D([0,d],grid))
    
    for i in range(n):
        for se in ses:
            dilate3D(imOut, imOut, 1, se=se)
    imOut.updateDisplay()

im3D = image3DMb()
im3D.showDisplay()
# We will choose orange to display the polyhedron
# At this point, it is worth signaling that the result will look
# better using the isosurface process (Use <F1> on the display to
# modify it).
pal = tagOneColorPalette(255, (255,150,0))
im3D.setPalette(pal)

# Drawing a rhombododecahedron
steiner3D(im3D, 30, [11,15,22,26], CUBIC)
# If you look at the display after this step you will see
# a strange blur. It is because the directions does not allow to fill all
# the space so we close the 1 pixel gaps with CUBE3X3X3
close3D(im3D, im3D, 1, CUBE3X3X3)
im3D.updateDisplay()

