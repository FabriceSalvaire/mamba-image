"""
This module provides a set of functions to perform geodesic computations using
Mamba based functions.

It includes build and dualbuild operations, geodesic erosion and dilation, 
computation of maxima and minima...

it works with imageMb instances as defined in mamba.
"""

# Contributors: Serge BEUCHER, Nicolas BEUCHER

from mambaCore import ERR_BAD_DEPTH
import mamba
import mambaComposed as mC

def upperGeodesicDilate(imIn, imMask, imOut, n=1, se=mC.DEFAULT_SE):
    """
    Performs a upper geodesic dilation of image 'imIn' above 'imMask'.
    The result is put inside 'imOut', 'n' controls the size of the dilation.
    'se' specifies the type of structuring element used to perform the 
    computation (DEFAULT_SE by default). 
    
    Warning! 'imMask' and 'imOut' must be different.
    """
    
    mamba.logic(imIn, imMask, imOut, "sup")
    if imIn.getDepth() == 1:
        for i in range(n):
            mamba.diff(imOut, imMask, imOut)
            mC.dilate(imOut, imOut, se=se)
            mamba.logic(imMask, imOut, imOut, "sup")
    else:
        imWrk1 = mamba.imageMb(imIn)
        imWrk2 = mamba.imageMb(imIn, 1)
        for i in range(n):
            mamba.generateSupMask(imOut, imMask, imWrk2, True)
            mamba.convertByMask(imWrk2, imWrk1, 0, mamba.computeMaxRange(imWrk1)[1])
            mamba.logic(imOut, imWrk1, imOut, "inf")
            mC.dilate(imOut, imOut, se=se)
            mamba.logic(imOut, imMask, imOut, "sup")

def lowerGeodesicDilate(imIn, imMask, imOut, n=1, se=mC.DEFAULT_SE):
    """
    Performs a lower geodesic dilation of image 'imIn' below 'imMask'.
    The result is put inside 'imOut', 'n' controls the size of the dilation.
    'se' specifies the type of structuring element used to perform the 
    computation (DEFAULT_SE by default). 
    
    Warning! 'imMask' and 'imOut' must be different.
    """
    
    mamba.logic(imIn, imMask, imOut, "inf")
    for i in range(n):
        mC.dilate(imOut, imOut, se=se)
        mamba.logic(imMask, imOut, imOut, "inf")

def geodesicDilate(imIn, imMask, imOut, n=1, se=mC.DEFAULT_SE):
    """
    This operator is simply an alias of lowerGeodesicDilate. It is kept for
    compatibility reasons.
    """
    
    lowerGeodesicDilate(imIn, imMask, imOut, n, se=se)
    
        
def upperGeodesicErode(imIn, imMask, imOut, n=1, se=mC.DEFAULT_SE):
    """
    Performs a upper geodesic erosion of image 'imIn' above 'imMask'.
    The result is put inside 'imOut', 'n' controls the size of the erosion.
    'se' specifies the type of structuring element used to perform the 
    computation (DEFAULT_SE by default).
    
    Warning! 'imMask' and 'imOut' must be different.
    """
    
    mamba.logic(imIn, imMask, imOut, "sup")
    for i in range(n):
        mC.erode(imOut, imOut, se=se)
        mamba.logic(imOut, imMask, imOut, "sup")

def lowerGeodesicErode(imIn, imMask, imOut, n=1, se=mC.DEFAULT_SE):
    """
    Performs a lower geodesic erosion of image 'imIn' under 'imMask'.
    The result is put inside 'imOut', 'n' controls the size of the erosion.
    'se' specifies the type of structuring element used to perform the 
    computation (DEFAULT_SE by default).

    The binary lower geodesic erosion is realised using the fact that the
    dilation is the dual operation of the erosion.
    
    Warning! 'imMask' and 'imOut' must be different.
    """
    
    if imIn.getDepth() == 1:
        mamba.diff(imMask, imIn, imOut)
        lowerGeodesicDilate(imOut, imMask, imOut, n, se=se)
        mamba.diff(imMask, imOut, imOut)
    else:
        imWrk1 = mamba.imageMb(imIn)
        imWrk2 = mamba.imageMb(imIn, 1)
        mamba.logic(imIn, imMask, imOut, "inf")
        for i in range(n):
            mamba.generateSupMask(imOut, imMask, imWrk2, False)
            mamba.convertByMask(imWrk2, imWrk1, 0, mamba.computeMaxRange(imWrk1)[1])
            mamba.logic(imOut, imWrk1, imOut, "sup")
            mC.erode(imOut, imOut, se=se)
            mamba.logic(imOut, imMask, imOut, "inf")
 
def geodesicErode(imIn, imMask, imOut, n=1, se=mC.DEFAULT_SE):
    """
    This transformation is identical to the previous version and it has been
    kept for compatibilty purposes.
    
    Note that the binary and the greytone operators are different.
    """
    
    if imIn.getDepth() == 1:
        lowerGeodesicErode(imIn, imMask, imOut, n, se=se)
    else:
        upperGeodesicErode(imIn, imMask, imOut, n, se=se)

def build(imMask, imInout, grid=mamba.DEFAULT_GRID):
    """
    Builds image 'imInout' using 'imMask' as a mask. This operator performs the
    geodesic reconstruction of 'imInout' inside the mask image and puts the
    result in the same image.
    
    This operator uses a recursive implementation of the reconstruction.
    
    This function will use the mamba default grid unless specified otherwise in
    'grid'.
    """
    
    vol = 0
    prec_vol = -1
    dirs = mamba.getDirections(grid)[1:]
    while(prec_vol!=vol):
        prec_vol = vol
        for d in dirs:
            vol = mamba.buildNeighbor(imMask, imInout, d, grid)

def dualBuild(imMask, imInout, grid=mamba.DEFAULT_GRID):
    """
    Builds (dual build) image 'imInout' using 'imMask' as a mask. This operator
    performs the geodesic dual reconstruction (by erosions) of 'imInout' inside
    the mask image and puts the result in the same image.
    
    This operator uses a recursive implementation of the reconstruction.
    
    This function will use the mamba default grid unless specified otherwise in
    'grid'.
    """
    
    vol = 0
    prec_vol = -1
    dirs = mamba.getDirections(grid)[1:]
    while(prec_vol!=vol):
        prec_vol = vol
        for d in dirs:
            vol = mamba.dualbuildNeighbor(imMask, imInout, d, grid)

def minima(imIn, imOut, h=1, grid=mamba.DEFAULT_GRID):
    """
    Computes the minima of 'imIn' using a dual build operation and puts the 
    result in 'imOut'. When 'h' is equal to 1 (default value), the operator
    provides the minima of 'imIn'.
    
    Grid used by the dual build operation can be specified by 'grid'.
    
    Only works with 8-bit or 32-bit images as input. 'imOut' must be binary.
    """
    
    imWrk = mamba.imageMb(imIn)
    if imIn.getDepth() == 8:
        mamba.addConst(imIn, h, imWrk)
        mamba.hierarDualBuild(imIn, imWrk, grid=grid)
        mamba.sub(imWrk, imIn, imWrk)
    else:
        mC.ceilingAddConst(imIn, h, imWrk)
        dualBuild(imIn, imWrk, grid=grid)
        mC.floorSub(imWrk, imIn, imWrk)
    mamba.threshold(imWrk, imOut, 1, mamba.computeMaxRange(imIn)[1])

def maxima(imIn, imOut, h=1, grid=mamba.DEFAULT_GRID):
    """
    Computes the maxima of 'imIn' using a build operation and puts the result in
    'imOut'. When 'h' is equal to 1 (default value), the operator provides the
    minima of 'imIn'.
    
    Grid used by the build operation can be specified by 'grid'.
    
    Only works with with 8-bit or 32-bit images as input. 'imOut' must be binary.
    """
    
    imWrk = mamba.imageMb(imIn)   
    if imIn.getDepth() == 8:
        mamba.subConst(imIn, h, imWrk)
        mamba.hierarBuild(imIn, imWrk, grid=grid)
        mamba.sub(imIn, imWrk, imWrk)
    else:
        mC.floorSubConst(imIn, h, imWrk)
        build(imIn, imWrk, grid=grid)
        mC.floorSub(imIn, imWrk, imWrk)
    mamba.threshold(imWrk, imOut, 1, mamba.computeMaxRange(imIn)[1])

def closeHoles(imIn, imOut, grid=mamba.DEFAULT_GRID):
    """
    Close holes in image 'imIn' and puts the result in 'imOut'. This operator
    works on binary and greytone images. In this case, however, it should be 
    used cautiously.
    """
    
    imWrk = mamba.imageMb(imIn)
    mamba.negate(imIn, imIn)
    mC.drawEdge(imWrk)
    mamba.logic(imIn, imWrk, imWrk, "inf")
    build(imIn, imWrk, grid=grid)
    mamba.negate(imIn, imIn)
    mamba.negate(imWrk, imOut)

def removeEdgeParticles(imIn, imOut, grid=mamba.DEFAULT_GRID):
    """
    Removes particles (connected components) touching the edge in image 'imIn'.
    The resulting image is put in image 'imOut'.
    Although this operator may be used with greytone images, it should be
    considered with caution.
    """
    
    imWrk = mamba.imageMb(imIn)
    se = mC.structuringElement(mamba.getDirections(grid), grid)
    mC.dilate(imWrk, imWrk, se=se, edge=mamba.FILLED)
    mamba.logic(imIn, imWrk, imWrk, "inf")
    build(imIn, imWrk, grid=grid)
    mamba.diff(imIn, imWrk, imOut)

def geodesicDistance(imIn, imMask, imOut, se=mC.DEFAULT_SE):
    """
    Computes the geodesic distance function of a set in 'imIn'. This distance
    function uses successive geodesic erosions of 'imIn' performed in the geodesic
    space defined by 'imMask'. The result is stored in 'imOut'. Be sure to use an 
    image of sufficient depth as output.
    
    This geodesic distance is quite slow as it is performed by successive geodesic
    erosions.
    """
    
    if imIn.getDepth() != 1:
        mamba.raiseExceptionOnError(ERR_BAD_DEPTH)
    imOut.reset()
    imWrk = mamba.imageMb(imIn)
    mamba.logic(imIn, imMask, imWrk, "inf")
    while mamba.computeVolume(imWrk) != 0:
        mamba.add(imOut, imWrk, imOut)
        lowerGeodesicErode(imWrk, imMask, imWrk, se=se)

def hierarBuild32(imMask, imOut, grid=mamba.DEFAULT_GRID):
    """
    This reconstruction for 32-bit images uses the 8-bit build operator
    which is designed with a HQ. This operation produces exactly the
    same result as the build operator. Its computation speed is independant
    of the image complexity.

    This operator may be considered as an alternative to the build
    operator for 32-bit images (not necessarily faster).
    """
    
    imWrk1 = mamba.imageMb(imMask)
    imWrk2 = mamba.imageMb(imMask)
    imWrk3 = mamba.imageMb(imMask)
    cutMask = mamba.imageMb(imMask)
    imCut1 = mamba.imageMb(imMask, 8)
    imCut2 = mamba.imageMb(imMask, 8)
    [current_level, max_level] = mamba.computeRange(imOut)
    mC.floorSubConst(imMask, current_level, imWrk1)
    mC.floorSubConst(imOut, current_level, imWrk2)
    imOut.fill(current_level)
    cutMask.fill(255)
    while max_level > current_level:
        mamba.logic(imWrk1, cutMask, imWrk3, "inf")
        mamba.copyBytePlane(imWrk3, 0, imCut1)
        mamba.logic(imWrk2, cutMask, imWrk3, "inf")
        mamba.copyBytePlane(imWrk3, 0, imCut2)
        mamba.hierarBuild(imCut1, imCut2, grid=grid)
        mC.floorSubConst(imWrk1, 255, imWrk1)
        mC.floorSubConst(imWrk2, 255, imWrk2)
        mamba.add(imOut, imCut2, imOut)
        current_level += 255
        
def hierarDualBuild32(imMask, imOut, grid=mamba.DEFAULT_GRID):
    """
    This dual reconstruction for 32-bit images uses the 8-bit dualBuild operator
    which is designed with a HQ. This operation produces exactly the
    same result as the dualBuild operator. Its computation speed is independant
    of the image complexity.  
    
    This operator may be considered as an alternative to the dualBuild
    operator for 32-bit images (not necessarily faster).
    """
    
    imWrk1 = mamba.imageMb(imMask)
    imWrk2 = mamba.imageMb(imMask)
    imWrk3 = mamba.imageMb(imMask)
    cutMask = mamba.imageMb(imMask)
    imCut1 = mamba.imageMb(imMask, 8)
    imCut2 = mamba.imageMb(imMask, 8)
    [current_level, max_level] = mamba.computeRange(imOut)
    mC.floorSubConst(imMask, current_level, imWrk1)
    mC.floorSubConst(imOut, current_level, imWrk2)
    imOut.fill(current_level)
    cutMask.fill(255)
    while max_level > current_level:
        mamba.logic(imWrk1, cutMask, imWrk3, "inf")
        mamba.copyBytePlane(imWrk3, 0, imCut1)
        mamba.logic(imWrk2, cutMask, imWrk3, "inf")
        mamba.copyBytePlane(imWrk3, 0, imCut2)
        mamba.hierarDualBuild(imCut1, imCut2, grid=grid)
        mC.floorSubConst(imWrk1, 255, imWrk1)
        mC.floorSubConst(imWrk2, 255, imWrk2)
        mamba.add(imOut, imCut2, imOut)
        current_level += 255
                

    
