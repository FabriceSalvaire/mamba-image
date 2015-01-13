# exampleM9.py
# IN snake.png
# OUT snake_contrast.png

## TITLE #######################################################################
# Contrast enhancement using top hat operators

## DESCRIPTION #################################################################
# This example presents a contrast enhancement technique based on the
# black top hat and white top hat operators.

## SCRIPT ######################################################################
# Importing the mamba module, the mambaComposed package
import mamba
import mambaComposed as mC

def contrastEnhancer(imIn, imOut, n=1, se=mC.DEFAULT_SE):
    """
    Increase the contrast of image 'imIn' and put the result in
    image 'imOut'. Parameter 'n' will control the size and 'se' the
    structuring element used by the top hat operators.
    """

    imWrk = mamba.imageMb(imIn)
    mC.whiteTopHat(imIn, imWrk, n, se=se)
    mamba.add(imIn, imWrk, imOut)
    mC.blackTopHat(imIn, imWrk, n, se=se)
    mamba.sub(imOut, imWrk, imOut) 
    
im = mamba.imageMb("snake.png")
imContrast = mamba.imageMb(im)
contrastEnhancer(im, imContrast, 10)
imContrast.save("snake_contrast.png")

