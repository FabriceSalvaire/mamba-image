"""
This module provides a set of functions to perform morphological filtering 
operations using mamba. it works with imageMb instances as defined in mamba.
"""

import mamba
import mambaComposed as mC

# contributors: Serge BEUCHER, Nicolas BEUCHER

def alternateFilter(imIn, imOut,n, openFirst, se=mC.DEFAULT_SE):
    """
    Performs an alternate filter operation of size 'n' on image 'imIn' and puts
    the result in 'imOut'. If 'openFirst' is True, the filter begins with an
    opening, a closing otherwise.
    """
    
    if openFirst:
        mC.open(imIn, imOut, n, se=se)
        mC.close(imOut, imOut, n, se=se)
    else:
        mC.close(imIn, imOut, n, se=se)
        mC.open(imOut, imOut, n, se=se)

def fullAlternateFilter(imIn, imOut, n, openFirst, se=mC.DEFAULT_SE):
    """
    Performs a full alternate filter operation (successive alternate filters of
    increasing sizes, from 1 to 'n') on image 'imIn' and puts the result 
    in 'imOut'. 'n' controls the filter size. If 'openFirst' is True, the filter
    begins with an opening, a closing otherwise.
    """
    
    mamba.copy(imIn, imOut)
    for i in range(1,n+1):
        if openFirst:
            mC.open(imOut, imOut, i, se=se)
            mC.close(imOut, imOut, i, se=se)
        else:
            mC.close(imOut, imOut, i, se=se)
            mC.open(imOut, imOut, i, se=se)

def linearAlternateFilter(imIn, imOut, n, openFirst, grid=mamba.DEFAULT_GRID):
    """
    Performs an alternate filter operation on image 'imIn' with openings and
    closings by segments of size 'n' (supremeum of openings and infimum of
    closings) and puts the result in 'imOut'. If 'openFirst' is True, the filter
    begins with an opening, a closing otherwise.
    """
    
    if openFirst:
        mC.supOpen(imIn, imOut, n, grid=grid)
        mC.infClose(imOut, imOut, n, grid=grid)
    else:
        mC.infClose(imIn, imOut, n, grid=grid)
        mC.supOpen(imOut, imOut, n, grid=grid)

def autoMedian(imIn, imOut, n, se=mC.DEFAULT_SE):
    """
    Morphological automedian filter performed with alternate sequential filters.
    """
    
    oc_im = mamba.imageMb(imIn)
    co_im = mamba.imageMb(imIn)
    imWrk = mamba.imageMb(imIn)
    alternateFilter(imIn, oc_im, n, True, se=se)
    alternateFilter(imIn, co_im, n, False, se=se)
    mamba.copy(imIn, imOut)
    mamba.copy(oc_im, imWrk)
    mamba.logic(co_im, imWrk, imWrk, "sup")
    mamba.logic(imWrk, imOut, imOut, "inf")
    mamba.copy(oc_im, imWrk)
    mamba.logic(co_im, imWrk, imWrk, "inf")
    mamba.logic(imWrk, imOut, imOut, "sup")

def simpleLevelling(imIn, imMask, imOut, grid=mamba.DEFAULT_GRID):
    """
    Performs a simple levelling of image 'imIn' controlled by image 'imMask'
    and puts the result in 'imOut'. This operation is composed of two
    geodesic reconstructions. This filter tends to level regions in the 
    image of homogeneous grey values.
    """
    
    imWrk1 = mamba.imageMb(imIn)
    imWrk2 = mamba.imageMb(imIn)
    mask_im = mamba.imageMb(imIn, 1)
    mamba.logic(imIn, imMask, imWrk1, "inf")
    mC.build(imIn, imWrk1, grid=grid)
    mamba.logic(imIn, imMask, imWrk2, "sup")
    mC.dualBuild(imIn, imWrk2, grid=grid)
    mamba.generateSupMask(imIn, imMask, mask_im, False)
    mamba.convertByMask(mask_im, imOut, 0, mamba.computeMaxRange(imIn)[1])
    mamba.logic(imOut, imWrk1, imWrk1, "inf")
    mamba.negate(imOut, imOut)
    mamba.logic(imOut, imWrk2, imOut, "inf")
    mamba.logic(imWrk1, imOut, imOut, "sup")

def strongLevelling(imIn, imOut, n, eroFirst, grid=mamba.DEFAULT_GRID):
    """
    Strong levelling of 'imIn', result in 'imOut'. 'n' defines the size of the
    erosion and dilation of 'imIn' in the operation. If 'eroFirst' is true, the
    operation starts with an erosion, it starts with a dilation otherwise.
    
    This filter is stronger (more efficient) that simpleLevelling. However, the
    order of the initial operations (erosion and dilation) matters.    
    """
    
    imWrk = mamba.imageMb(imIn)
    se = mC.structuringElement(mamba.getDirections(grid), grid)
    if eroFirst:
        mC.erode(imIn, imWrk, n, se=se)
        mC.build(imIn, imWrk, grid=grid)
        mC.dilate(imIn, imOut, n, se=se)
        mC.dualBuild(imWrk, imOut, grid=grid)
    else:
        mC.dilate(imIn, imWrk, n, se=se)
        mC.dualBuild(imIn, imWrk, grid=grid)
        mC.erode(imIn, imOut, n, se=se)
        mC.build(imWrk, imOut, grid=grid)

def largeHexagonalAlternateFilter(imIn, imOut, start, end, step, openFirst):
    """
    Fast full alternate hexagonal filter of image 'imIn'. The initial size
    is equal to 'start', the final one is bounded by 'end' (this size is not
    taken into account), the increment of size is 'step'. If 'openFirst' is
    true, the filter starts with on opening. It starts with a closing otherwise.
    The result is put in 'imOut'.
    This operation is efficient if most of the sizes used in the filter are
    greater than 5. If it is not the case, the 'fullAlternateFilter' should
    be used instead.    
    """
    
    prev = 0
    mamba.copy(imIn, imOut)
    if openFirst:
        for i in range(start, end, step):
            t1 = i + prev
            t2 = 2 * i
            mC.largeHexagonalErode(imOut, imOut, t1)
            mC.largeHexagonalDilate(imOut, imOut, t2)
            prev = i
        mC.largeHexagonalErode(imOut, imOut, prev)
    else:
        for i in range(start, end, step):
            t1 = i + prev
            t2 = 2 * i
            mC.largeHexagonalDilate(imOut, imOut, t1)
            mC.largeHexagonalErode(imOut, imOut, t2)
            prev = i
        mC.largeHexagonalDilate(imOut, imOut, prev)

def largeDodecagonalAlternateFilter(imIn, imOut, start, end, step, openFirst):
    """
    Fast full alternate dodecagonal filter of image 'imIn'. The initial size
    is equal to 'start', the final one is bounded by 'end' (this size is not
    taken into account), the increment of size is 'step'. If 'openFirst' is
    true, the filter starts with on opening. It starts with a closing otherwise.
    The result is put in 'imOut'.
    """
    
    prev = 0
    mamba.copy(imIn, imOut)
    if openFirst:
        for i in range(start, end, step):
            t1 = i + prev
            t2 = 2 * i
            mC.largeDodecagonalErode(imOut, imOut, t1)
            mC.largeDodecagonalDilate(imOut, imOut, t2)
            prev = i
        mC.largeDodecagonalErode(imOut, imOut, prev)
    else:
        for i in range(start, end, step):
            t1 = i + prev
            t2 = 2 * i
            mC.largeDodecagonalDilate(imOut, imOut, t1)
            mC.largeDodecagonalErode(imOut, imOut, t2)
            prev = i
        mC.largeDodecagonalDilate(imOut, imOut, prev)

def largeSquareAlternateFilter(imIn, imOut, start, end, step, openFirst):
    """
    Fast full alternate square filter of image 'imIn'. The initial size
    is equal to 'start', the final one is bounded by 'end' (this size is not
    taken into account), the increment of size is 'step'. If 'openFirst' is
    true, the filter starts with on opening. It starts with a closing otherwise.
    The result is put in 'imOut'.
    This operation is efficient if most of the sizes used in the filter are
    greater than 5. If it is not the case, the 'fullAlternateFilter' should
    be used instead (with a SQUARE structuring element).    
    """
    
    prev = 0
    mamba.copy(imIn, imOut)
    if openFirst:
        for i in range(start, end, step):
            t1 = i + prev
            t2 = 2 * i
            mC.largeSquareErode(imOut, imOut, t1)
            mC.largeSquareDilate(imOut, imOut, t2)
            prev = i
        mC.largeSquareErode(imOut, imOut, prev)
    else:
        for i in range(start, end, step):
            t1 = i + prev
            t2 = 2 * i
            mC.largeSquareDilate(imOut, imOut, t1)
            mC.largeSquareErode(imOut, imOut, t2)
            prev = i
        mC.largeSquareDilate(imOut, imOut, prev)

def largeOctogonalAlternateFilter(imIn, imOut, start, end, step, openFirst):
    """
    Fast full alternate octogonal filter of image 'imIn'. The initial size
    is equal to 'start', the final one is limited by 'end' (this size is not
    taken into account), the increment of size is 'step'. If 'openFirst' is
    true, the filter starts with on opening. It starts with a closing otherwise.
    The result is put in 'imOut'.
    """
    
    prev = 0
    mamba.copy(imIn, imOut)
    if openFirst:
        for i in range(start, end, step):
            t1 = i + prev
            t2 = 2 * i
            mC.largeOctogonalErode(imOut, imOut, t1)
            mC.largeOctogonalDilate(imOut, imOut, t2)
            prev = i
        mC.largeOctogonalErode(imOut, imOut, prev)
    else:
        for i in range(start, end, step):
            t1 = i + prev
            t2 = 2 * i
            mC.largeOctogonalDilate(imOut, imOut, t1)
            mC.largeOctogonalErode(imOut, imOut, t2)
            prev = i
        mC.largeOctogonalDilate(imOut, imOut, prev)


