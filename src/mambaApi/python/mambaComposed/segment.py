"""
This module provides a set of functions to perform segmentation
operations using mamba. it works with imageMb instance as defined in mamba.
"""

# Contributors: Nicolas BEUCHER, Serge BEUCHER

import mamba
import mambaComposed as mC

def markerControlledWatershed(imIn, imMarkers, imOut, grid=mamba.DEFAULT_GRID):
    """
    Marker-controlled watershed transform of greytone image 'imIn'. The binary
    image 'imMarkers' contains the markers which control the flooding process.
    'imOut' contains the valued watershed.
    """
    
    im_mark = mamba.imageMb(imIn, 32)
    imWrk = mamba.imageMb(imIn)
    mamba.label(imMarkers, im_mark, grid=grid)
    mamba.watershedSegment(imIn, im_mark, grid=grid)
    mamba.copyBytePlane(im_mark, 3, imWrk)
    mamba.logic(imWrk, imIn, imOut, 'inf')

def valuedWatershed(imIn, imOut, grid=mamba.DEFAULT_GRID):
    """
    Returns the valued watershed of greyscale image 'imIn' into greyscale image
    'imOut'. Each pixel of the watershed lines is given its corresponding value
    in initial image 'imIn'.
    """
    
    im_min = mamba.imageMb(imIn, 1)
    mC.minima(imIn, im_min, grid=grid)
    markerControlledWatershed(imIn, im_min, imOut, grid=grid)

def fastSKIZ(imIn, imOut, grid=mamba.DEFAULT_GRID):
    """
    Fast skeleton by zones of influence of binary image 'imIn'. Result is put in
    binary image 'imOut'. The transformation is faster as it uses the watershed
    transform by hierarchical queues.
    """
    
    imWrk = mamba.imageMb(imIn, 8)
    mamba.convertByMask(imIn, imWrk, 1, 0)
    markerControlledWatershed(imWrk, imIn, imWrk, grid=grid)
    mamba.threshold(imWrk, imOut, 0, 0)

def geodesicSKIZ(imIn, imMask, imOut, grid=mamba.DEFAULT_GRID):
    """
    Geodesic skeleton by zones of influence of binary image 'imIn' inside the
    geodesic mask 'imMask'. The result is in binary image 'imOut'.
    """
    
    imWrk1 = mamba.imageMb(imIn, 8)
    imWrk2 = mamba.imageMb(imIn)
    mamba.copy(imIn, imWrk2)
    mC.build(imMask, imWrk2, grid=grid)
    mamba.convertByMask(imWrk2, imWrk1, 2, 1)
    mamba.sub(imWrk1, imIn, imWrk1)
    markerControlledWatershed(imWrk1, imIn, imWrk1, grid=grid)
    mamba.threshold(imWrk1, imOut, 0, 0)
    mamba.logic(imOut, imWrk2, imOut, "inf")
    
def mosaic(imIn, imOut, imWts, grid=mamba.DEFAULT_GRID):
    """
    Builds the mosaic image of 'imIn' and puts the results into 'imOut'.
    The watershed line (pixel values set to 255) is stored in the 
    greytone image 'imWts'. A mosaic image is a simple image made of various 
    tiles of uniform grey values. It is built using the watershed of 'imIn' 
    gradient and original markers made of gradient minima which are labelled by
    the maximum value of 'imIn' pixels inside them.
    """
   
    imWrk1 = mamba.imageMb(imIn, 1)
    imWrk2 = mamba.imageMb(imIn)
    mamba.copy(imIn, imWrk2)
    im_mark = mamba.imageMb(imIn, 32)
    se = mC.structuringElement(mamba.getDirections(grid), grid)
    mC.gradient(imIn, imOut, se=se)
    mC.minima(imOut, imWrk1, grid=grid) 
    mamba.add(im_mark, imWrk1, im_mark) 
    imWrk1.convert(8)
    mC.build(imWrk1, imWrk2, grid=grid)
    mamba.add(im_mark, imWrk2, im_mark)   
    mamba.watershedSegment(imOut, im_mark, grid=grid)
    mamba.copyBytePlane(im_mark, 3, imWts)
    mamba.subConst(im_mark, 1, im_mark)
    mamba.copyBytePlane(im_mark, 0, imOut)
    
def mosaicGradient(imIn, imOut, grid=mamba.DEFAULT_GRID):
    """
    Builds the mosaic-gradient image of 'imIn' and puts the result in 'imOut'.
    The mosaic-gradient image is built by computing the differences of two
    mosaic images generated from 'imIn', the first one having its watershed
    lines valued by the suprema of the adjacent catchment basins values, the
    second one been valued by the infima.
    """
    
    imWrk1 = mamba.imageMb(imIn)
    imWrk2 = mamba.imageMb(imIn)
    imWrk3 = mamba.imageMb(imIn)
    imWrk4 = mamba.imageMb(imIn)
    imWrk5 = mamba.imageMb(imIn)
    imWrk6 = mamba.imageMb(imIn, 1)
    mosaic(imIn, imWrk2, imWrk3, grid=grid)
    mamba.sub(imWrk2, imWrk3, imWrk1)
    mamba.logic(imWrk2, imWrk3, imWrk2, "sup")
    mamba.negate(imWrk2, imWrk2)
    mamba.threshold(imWrk3, imWrk6, 1, 255)
    mC.multiplePoints(imWrk6, imWrk6, grid=grid)
    mamba.convertByMask(imWrk6, imWrk3, 0, 255)
    se = mC.structuringElement(mamba.getDirections(grid), grid)
    mC.dilate(imWrk1, imWrk4, se=se)
    mC.dilate(imWrk2, imWrk5, se=se)
    while mamba.computeVolume(imWrk3) != 0:
        mC.dilate(imWrk1, imWrk1, 2, se=se)
        mC.dilate(imWrk2, imWrk2, 2, se=se)
        mamba.logic(imWrk1, imWrk3, imWrk1, "inf")
        mamba.logic(imWrk2, imWrk3, imWrk2, "inf")
        mamba.logic(imWrk1, imWrk4, imWrk4, "sup")
        mamba.logic(imWrk2, imWrk5, imWrk5, "sup")
        mC.erode(imWrk3, imWrk3, 2, se=se)
    mamba.negate(imWrk5, imWrk5)
    mamba.sub(imWrk4, imWrk5, imOut)

def basinSegment32(imIn, imMarker, grid=mamba.DEFAULT_GRID, max_level=-1):
    """
    This is the complete equivalent of the basinSegment Mamba function but
    this one works on 32-bit images instead of 8-bit images.
    
    If 'max_level' is negative the function will continue until the whole
    image is flooded.
    """
    
    imWrk1 = mamba.imageMb(imIn)
    imWrk2 = mamba.imageMb(imIn)
    imWrk3 = mamba.imageMb(imIn, 8)
    imMask = mamba.imageMb(imIn)
    (mi, ma) = mamba.computeRange(imIn)
    current_level = mi
    if max_level < 0:
        high_level = ma+1
    else:
        high_level = min(max_level,ma+1)
    mamba.subConst(imIn, mi, imWrk1)
    imMask.fill(255)
    mamba.logic(imWrk1, imMask, imWrk2, "inf")
    mamba.copyBytePlane(imWrk2, 0, imWrk3)
    if high_level-current_level<256:
        if high_level>=(ma+1):
            level=256
        else:
            level=high_level-current_level
    else:
        level=255
    mamba.basinSegment(imWrk3, imMarker, grid=grid, max_level=level)
    current_level += level
    while current_level<high_level:
        mC.floorSubConst(imWrk1, 254, imWrk1)
        mamba.logic(imWrk1, imMask, imWrk2, "inf")
        mamba.copyBytePlane(imWrk2, 0, imWrk3)
        if high_level-current_level<256:
            if high_level>=(ma+1):
                level=256
            else:
                level=high_level-current_level
        else:
            level=255
        mamba.basinSegment(imWrk3, imMarker, grid=grid, max_level=level)
        current_level += level
        
def watershedSegment32(imIn, imMarker, grid=mamba.DEFAULT_GRID, max_level=-1):
    """
    This is the complete equivalent of the watershedSegment Mamba function but
    this one works on 32-bit images instead of 8-bit images.
    
    If 'max_level' is negative the function will continue until the whole
    image is flooded.
    """
    
    imWrk1 = mamba.imageMb(imIn)
    imWrk2 = mamba.imageMb(imIn)
    imWrk3 = mamba.imageMb(imIn, 8)
    imMask = mamba.imageMb(imIn)
    imBinMask = mamba.imageMb(imIn, 1)
    (mi, ma) = mamba.computeRange(imIn)
    current_level = mi
    if max_level < 0:
        high_level = ma+1
    else:
        high_level = min(max_level,ma+1)
    mamba.subConst(imIn, mi, imWrk1)
    imMask.fill(255)
    mamba.logic(imWrk1, imMask, imWrk2, "inf")
    mamba.copyBytePlane(imWrk2, 0, imWrk3)
    if high_level-current_level<256:
        if high_level>=(ma+1):
            level=256
        else:
            level=high_level-current_level
    else:
        level=255
    mamba.watershedSegment(imWrk3, imMarker, grid=grid, max_level=level)
    current_level += level
    while current_level<high_level:
        mC.floorSubConst(imWrk1, 254, imWrk1)
        mamba.copyBytePlane(imMarker, 3, imWrk3)
        mamba.threshold(imWrk3, imBinMask, 0, 254)
        mamba.convertByMask(imBinMask, imWrk2, 0, mamba.computeMaxRange(imWrk2)[1])
        mamba.logic(imMarker, imWrk2, imMarker, "inf")
        mamba.logic(imWrk1, imMask, imWrk2, "inf")
        mamba.copyBytePlane(imWrk2, 0, imWrk3)
        if high_level-current_level<256:
            if high_level>=(ma+1):
                level=256
            else:
                level=high_level-current_level
        else:
            level=255
        mamba.watershedSegment(imWrk3, imMarker, grid=grid, max_level=level)
        current_level += level
