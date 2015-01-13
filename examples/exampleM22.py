# exampleM22.py
# OUT ndf.jpg

## TITLE #######################################################################
# Neutral density filter

## DESCRIPTION #################################################################
# This example implements an algorithmic equivalent to the neutral density
# filter. It shows how to use sequential processing function with Mamba Realtime.
# Explanation and image at:
#
# http://en.wikipedia.org/wiki/Neutral_density_filter.

## SCRIPT ######################################################################
# Importing all the mamba modules.
from mambaRealtime import *
from mamba import *
from mambaComposed import *
# Importing the os module.
import os

def neutralDensityFilter(seqIn, seqIndex, imOut):
    """
    This filter is used in photography for various effects. In particular
    it will remove fast moving objects out of the image. Algorithmic
    implementation is a simple average of pixel values over time. Here, the
    function is adapted to mambaRealtime SEQUENTIAL processing.
    """
    im32 = imageMb(imOut, 32)
    for im in seqIn:
        add(im32, im, im32)
    divConst(im32, len(seqIn), im32)
    copyBytePlane(im32, 0, imOut)
    
def movementFilter(seqIn, seqIndex, imOut):
    """
    Extracts movement inside an image sequence.
    First applies the neutral density filter on the sequence and compare
    (with an absolute difference) its latest image with the result.
    """
    im8_1 = imageMb(imOut)
    im8_2 = imageMb(imOut)
    neutralDensityFilter(seqIn, seqIndex, imOut)
    sub(seqIn[seqIndex], imOut, im8_1)
    sub(imOut, seqIn[seqIndex], im8_2)
    add(im8_1, im8_2, imOut)

# Here we launch the example. The launching command is different on 
# Windows and Linux Mamba Realtime. 
# Note that, on Windows, "0" may not be the number of your webcam. If so,
# change it accordingly.
#
# Also note that the sequence length used by the realtime module is set to
# 20. As the default framerate is 10, it means the sequence will hold
# 2 seconds of video. You can change this value (keep in mind that higher
# values will mean a longer processing time which may decreased framerate).
if os.name == 'nt':
    launchRealtime("0", DSHOW, seqlength=20)
else:
    launchRealtime("/dev/video0", V4L2, seqlength=20)

# starting the processing. You may also try the movement filter by
# replacing neutralDensityFilter by movementFilter in the next line.
setProcessRealtime(neutralDensityFilter, SEQUENTIAL)

