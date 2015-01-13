"""
This module regroups functions/operators that could not be regrouped with other
operators because of their unique nature or other peculiarity. As such, it
regroups some utility functions.
"""

import mamba
import mambaCore
import mambaComposed as mC

# Contributors: Serge BEUCHER, Nicolas BEUCHER

# Specific operators  
  
def isotropicDistance(imIn, imOut, edge=mamba.FILLED):
    """
    Computes the distance function of a set in 'imIn'. This distance function
    uses dodecagonal erosions and the grid is assumed to be hexagonal.
    The procedure is quite slow but the result is more aesthetic.
    This operator also illustrates how to perform successive dodecagonal
    operations of increasing sizes.
    """
    
    if imIn.getDepth() != 1:
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_DEPTH)
    imOut.reset()
    oldn = 0
    size = 0
    imWrk1 = mamba.imageMb(imIn)
    imWrk2 = mamba.imageMb(imIn)
    mamba.copy(imIn, imWrk1)
    while mamba.computeVolume(imWrk1) != 0:
        mamba.add(imOut, imWrk1, imOut)
        size += 1
        n = int(0.4641*size)
        n += abs(n % 2 - size % 2)
        if (n - oldn) == 1:
            mamba.copy(imWrk1, imWrk2)
            mC.erode(imWrk1, imWrk1, 1, se=mC.HEXAGON, edge=edge)
        else:
            mC.conjugateHexagonalErode(imWrk2, imWrk1, 1, edge=edge)
        oldn = n

# Utility operators

def drawEdge(imOut, thick=1):
    """
    Draws a frame around the edge of 'imOut' whose value equals the maximum
    range value and whose thickness is given by 'thick' (default 1).
    """
    
    imOut.reset()
    se=mC.structuringElement([0,1,2,3,4,5,6,7,8], mamba.SQUARE)
    mC.dilate(imOut, imOut, thick, se=se, edge=mamba.FILLED)

# Saturated arithmetic operators (for 32-bit images)

def ceilingAddConst(imIn, v, imOut):
    """
    Adds a constant value 'v' to image 'imIn' and puts the result in 'imOut'. If
    imIn + v is larger than the maximal possible value in imOut, the result is
    truncated and limited to this maximal value.
    
    Note that this operator is mainly useful for 32-bit images, as the result
    of the addition is always truncated for 8-bit images.
    """
    
    imMask = mamba.imageMb(imIn, 1)
    imWrk = mamba.imageMb(imIn)
    mamba.addConst(imIn, v, imWrk)
    mamba.generateSupMask(imIn, imWrk, imMask, True)
    mamba.convertByMask(imMask, imOut, 0, mamba.computeMaxRange(imOut)[1])
    mamba.logic(imOut, imWrk, imOut, "sup")
    
def ceilingAdd(imIn1, imIn2, imOut):
    """
    Adds image 'imIn2' to image 'imIn1' and puts the result in 'imOut'. If
    imIn1 + imIn2 is larger than the maximal possible value in imOut, the result
    is truncated and limited to this maximal value.
    
    Altough it is possible to use a 8-bit image for imIn2, it is recommended to
    use the same depth for all the images.
    
    Note that this operator is mainly useful for 32-bit images, as the result
    of the addition is always truncated for 8-bit images.
    """
    
    imMask = mamba.imageMb(imIn1, 1)
    imWrk = mamba.imageMb(imIn1)
    mamba.add(imIn1, imIn2, imWrk)
    mamba.generateSupMask(imIn1, imWrk, imMask, True)
    mamba.convertByMask(imMask, imOut, 0, mamba.computeMaxRange(imOut)[1])
    mamba.logic(imOut, imWrk, imOut, "sup")

def floorSubConst(imIn, v, imOut):
    """
    Subtracts a constant value 'v' to image 'imIn' and puts the result in 'imOut'.
    If imIn - v is negative, the result is truncated and limited to 0.
    
    Note that this operator is mainly useful for 32-bit images, as the result
    of the subtraction is always truncated for 8-bit images.
    """
    
    imMask = mamba.imageMb(imIn, 1)
    imWrk = mamba.imageMb(imIn)
    mamba.subConst(imIn, v, imWrk)
    mamba.generateSupMask(imIn, imWrk, imMask, False)
    mamba.convertByMask(imMask, imOut, 0, mamba.computeMaxRange(imOut)[1])
    mamba.logic(imOut, imWrk, imOut, "inf")
   
def floorSub(imIn1, imIn2, imOut):
    """
    subtracts image 'imIn2' from image 'imIn1' and puts the result in 'imOut'.
    If imIn1 - imIn2 is negative, the result is truncated and limited to 0.
    
    Altough it is possible to use a 8-bit image for imIn2, it is recommended to
    use the same depth for all the images.
    
    Note that this operator is mainly useful for 32-bit images, as the result
    of the subtractiontion is always truncated for 8-bit images.
    """
    
    imMask = mamba.imageMb(imIn1, 1)
    imWrk = mamba.imageMb(imIn1)
    mamba.sub(imIn1, imIn2, imWrk)
    mamba.generateSupMask(imIn1, imWrk, imMask, False)
    mamba.convertByMask(imMask, imOut, 0, mamba.computeMaxRange(imOut)[1])
    mamba.logic(imOut, imWrk, imOut, "inf")

def translate(imIn, imOut, deltaX, deltaY, v=0):
    """
    Performs the translation of image 'imIn' by a vector ('deltaX', 'deltaY') and
    puts the result in 'imOut'. It is possible to fill the void regions of the
    translated image with the value 'v' (default 0).
    """
    
    if deltaX < 0:
        dirH = 7
    else:
        dirH = 3
    if deltaY < 0:
        dirV = 1
    else:
        dirV = 5
    mamba.shift(imIn, imOut, dirH, abs(deltaX), v, grid=mamba.SQUARE)
    mamba.shift(imOut, imOut, dirV, abs(deltaY), v, grid=mamba.SQUARE)

def mulRealConst(imIn, v, imOut, nearest=False):
    """
    Multiplies image imIn by a real positive constant value v and puts the 
    result in image imOut. inIn and imOut can be 8-bit or 32-bit images.
    If imOut is a greyscale image (8-bit), the result is saturated (results
    of the multiplication greater than 255 are limited to this value).
    The constant v is truncated so that only its two first decimal digits
    are taken into account.
    If 'nearest' is true, the result is rounded to the nearest integer value.
    If not (default), the result is simply truncated.    
    """
    if imIn.getDepth()==1 or imOut.getDepth()==1:
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_DEPTH)
    imWrk1 = mamba.imageMb(imIn, 32)
    imWrk2 = mamba.imageMb(imIn, 1)
    v1 = int(v * 100)
    if imIn.getDepth()==8:
        imWrk1.reset()
        mamba.copyBytePlane(imIn, 0, imWrk1)
    else:
        mamba.copy(imIn, imWrk1)
    mamba.mulConst(imWrk1, v1, imWrk1)
    if nearest:
        mamba.addConst(imWrk1, 50, imWrk1)
    mamba.divConst(imWrk1, 100, imWrk1)
    if imOut.getDepth()==8:
        mamba.threshold(imWrk1, imWrk2, 255, mamba.computeMaxRange(imWrk1)[1])
        mamba.copyBytePlane(imWrk1, 0, imOut)
        imWrk2.convert(8)
        mamba.logic(imOut, imWrk2, imOut, "sup")
    else:
        mamba.copy(imWrk1, imOut)
        
    

