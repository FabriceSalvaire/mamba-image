"""
This module provides a set of functions which perform measure
operations on mamba images. It works with imageMb instances as defined in mamba.
"""

# Contributors: Serge BEUCHER, Nicolas BEUCHER

from __future__ import division

from mambaIm.mambaCore import ERR_BAD_DEPTH
from mambaIm import mamba
import math

def computeArea(imIn, scale=(1.0, 1.0)):
    """
    Calculates the area of the binary image 'imIn'. 'scale' is a tuple 
    containing the horizontal scale factor (distance between two adjacent 
    horizontal points) and the vertical scale factor (distance between two 
    successive lines) of image 'imIn' (default is 1.0 for both). The result is
    a float (when default values are used, the result value is identical to the
    computeVolume operator).
    
    Note that, with hexagonal grid, the "scale' default values do not correspond
    to an isotropic grid (where triangles would be equilateral).
    
    Beware, if the input image 'imIn' is not a binary image, the function raises
    an error.
    """
    
    if imIn.getDepth() != 1:
        mamba.raiseExceptionOnError(ERR_BAD_DEPTH)
    a = scale[0]*scale[1]*mamba.computeVolume(imIn)
    return a

def computeDiameter(imIn, dir, scale=(1.0, 1.0), grid=mamba.DEFAULT_GRID):
    """
    Computes the diameter (diametral variation) of binary image 'imIn' in 
    direction 'dir'. 'scale' is a tuple defining the horizontal and vertical
    scale factors (default is 1.0).
    
    Beware, if the input image 'imIn' is not a binary image, the function raises
    an error.
    """
    
    if imIn.getDepth() != 1:
        mamba.raiseExceptionOnError(ERR_BAD_DEPTH)
    if dir == 0:
        return 0.0
    dir = ((dir - 1)%(mamba.gridNeighbors(grid)//2)) +1
    imWrk = mamba.imageMb(imIn)
    mamba.copy(imIn, imWrk)
    mamba.diffNeighbor(imIn, imWrk, dir, grid=grid)
    if grid == mamba.HEXAGONAL:
        l = scale[1]
        if dir != 2:
            l = 2*l*scale[0]/math.sqrt(scale[0]*scale[0] + 4*scale[1]*scale[1])
    else:
        if dir == 1:
            l = scale[0]
        elif dir == 3:
            l = scale[1]
        else:
            l = scale[0]*scale[1]/math.sqrt(scale[0]*scale[0] + scale[1]*scale[1])
    l = l*mamba.computeVolume(imWrk)
    return l

def computePerimeter(imIn, scale=(1.0, 1.0), grid=mamba.DEFAULT_GRID):
    """
    Computes the perimeter of all particles in binary image 'imIn' according
    to the Cauchy-Crofton formula. 'scale' is a tuple defining the horizontal
    and vertical scale factors (default is 1.0).
    
    The edge of the image is always set to 'EMPTY'.
    
    Beware, if the input image 'imIn' is not a binary image, the function raises
    an error.
    """
    
    if imIn.getDepth() != 1:
        mamba.raiseExceptionOnError(ERR_BAD_DEPTH)
    p = 0.
    for i in range(1, mamba.gridNeighbors(grid)//2 + 1):
        p += computeDiameter(imIn, i, scale=scale, grid=grid)
    p = 2*math.pi*p/mamba.gridNeighbors(grid)
    return p
    
def computeConnectivityNumber(imIn, grid=mamba.DEFAULT_GRID):
    """
    Computes the connectivity number (Euler_Poincare constant) of image 'ImIn'.
    The result is an integer number.
    
    Beware, if the input image 'imIn' is not a binary image, the function raises
    an error.
    """
    
    if imIn.getDepth() != 1:
        mamba.raiseExceptionOnError(ERR_BAD_DEPTH)
    imWrk  = mamba.imageMb(imIn)
    if grid == mamba.HEXAGONAL:
        mamba.hitOrMiss(imIn, imWrk, 66, 1, grid=grid)
        n = mamba.computeVolume(imWrk)
        mamba.hitOrMiss(imIn, imWrk, 2, 5, grid=grid)
        n = n - mamba.computeVolume(imWrk)   
    else:
        mamba.hitOrMiss(imIn, imWrk, 56, 1, grid=grid)
        n = mamba.computeVolume(imWrk)
        mamba.hitOrMiss(imIn, imWrk, 16, 41, grid=grid)
        n = n - mamba.computeVolume(imWrk)
        mamba.hitOrMiss(imIn, imWrk, 40, 17, grid=grid)
        n = n + mamba.computeVolume(imWrk)
    return n

def computeComponentsNumber(imIn, grid=mamba.DEFAULT_GRID):
    """
    Computes the number of connected components in image 'imIn'. The result is
    an integer value.
    """
    
    imWrk =  mamba.imageMb(imIn, 32)
    return  mamba.label(imIn, imWrk, grid=grid)
    

def computeFeretDiameters(imIn, scale=(1.0, 1.0)):
    """
    computes the global Feret diameters (horizontal and vertical) of binary 
    image 'imIn' and returns the result in a tuple (hDf, vDf). These diameters 
    correspond to the horizontal and vertical dimensions of the smallest 
    bonding box containing all the particles of 'imIn'
    """
    
    s = mamba.extractFrame(imIn, 1)
    return (scale[0]*(s[2]-s[0]), scale[1]*(s[3]-s[1]))

