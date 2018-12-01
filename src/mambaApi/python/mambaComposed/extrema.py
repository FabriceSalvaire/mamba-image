"""
This module provides a set of operators dealing with maxima and minima of a function.
New operators linked to the notion of dynamics are provided. This module uses Mamba
functions available in geodesy.py.

it works with imageMb instances as defined in mamba.
"""

# Contributor: Serge BEUCHER

from mambaIm import mamba
import mambaComposed as mC

def minDynamics(imIn, imOut, h, grid=mamba.DEFAULT_GRID):
    """
    Extracts the minima of 'imIn' with a dynamics higher or equal to 'h' and puts
    the result in 'imOut'.
    
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
        mC.dualBuild(imIn, imWrk, grid=grid)
        mC.floorSub(imWrk, imIn, imWrk)
    mamba.threshold(imWrk, imOut, h, mamba.computeMaxRange(imIn)[1])
    
def maxDynamics(imIn, imOut, h, grid=mamba.DEFAULT_GRID):
    """
    Extracts the maxima of 'imIn' with a dynamics higher or equal to 'h' and puts
    the result in 'imOut'.
    
    Grid used by the dual build operation can be specified by 'grid'.
    
    Only works with 8-bit or 32-bit images as input. 'imOut' must be binary.
    """
    
    imWrk = mamba.imageMb(imIn)   
    if imIn.getDepth() == 8:
        mamba.subConst(imIn, h, imWrk)
        mamba.hierarBuild(imIn, imWrk, grid=grid)
        mamba.sub(imIn, imWrk, imWrk)
    else:
        mC.floorSubConst(imIn, h, imWrk)
        mC.build(imIn, imWrk, grid=grid)
        mC.floorSub(imIn, imWrk, imWrk)
    mamba.threshold(imWrk, imOut, h, mamba.computeMaxRange(imIn)[1])


def deepMinima(imIn, imOut, h, grid=mamba.DEFAULT_GRID):
    """
    Computes the minima of the dual reconstruction of  image 'imIn' by imin + h
    and puts the  result in 'imOut'.
    
    Grid used by the dual build operation can be specified by 'grid'.
    
    Only works with 8-bit or 32-bit images as input. 'imOut' must be binary.
    """
    
    imWrk = mamba.imageMb(imIn)
    if imIn.getDepth() == 8:
        mamba.addConst(imIn, h, imWrk)
        mamba.hierarDualBuild(imIn, imWrk, grid=grid)
    else:
        mC.ceilingAddConst(imIn, h, imWrk)
        mC.dualBuild(imIn, imWrk, grid=grid)
    mC.minima(imWrk, imOut, 1, grid=grid)

def highMaxima(imIn, imOut, h, grid=mamba.DEFAULT_GRID):
    """
    Computes the maxima of the reconstruction of  image 'imIn' by imin + h
    and puts the  result in 'imOut'.

    Grid used by the build operation can be specified by 'grid'.
    
    Only works with 8-bit or 32-bit images as input. 'imOut' must be binary.
    """
    
    imWrk = mamba.imageMb(imIn)   
    if imIn.getDepth() == 8:
        mamba.subConst(imIn, h, imWrk)
        mamba.hierarBuild(imIn, imWrk, grid=grid)
    else:
        mC.floorSubConst(imIn, h, imWrk)
        mC.build(imIn, imWrk, grid=grid)
    mC. maxima(imWrk, imOut, 1, grid=grid)
    
def maxPartialBuild(imIn, imMask, imOut, grid=mamba.DEFAULT_GRID):
    """
    Performs the partial reconstruction of 'imIn' with its maxima which are
    contained in the binary mask 'imMask'. The result is put in 'imOut'.
    
    'imIn' and 'imOut' must be different and greyscale images.
    """
    
    imWrk = mamba.imageMb(imIn, 1)
    mC.maxima(imIn, imWrk, 1, grid=grid)
    mamba.logic(imMask, imWrk, imWrk, "inf")
    mamba.convertByMask(imWrk, imOut, 0, mamba.computeMaxRange(imIn)[1])
    mamba.logic(imIn, imOut, imOut, "inf")
    mC.build(imIn, imOut)

def minPartialBuild(imIn, imMask, imOut, grid=mamba.DEFAULT_GRID):
    """
    Performs the partial reconstruction of 'imIn' with its minima which are
    contained in the binary mask 'imMask'. The result is put in 'imOut'.
    
    'imIn' and 'imOut' must be different and greyscale images.
    """
    
    imWrk = mamba.imageMb(imIn, 1)
    mC.minima(imIn, imWrk, 1, grid=grid)
    mamba.logic(imMask, imWrk, imWrk, "inf")
    mamba.convertByMask(imWrk, imOut, mamba.computeMaxRange(imIn)[1], 0)
    mamba.logic(imIn, imOut, imOut, "sup")
    mC.dualBuild(imIn, imOut)

    

