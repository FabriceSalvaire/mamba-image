"""
This module contains operators acting on partitions. Two types of operators are
defined: operators acting on each cell of the partition independently, or
operators considering each cell of the partition as a node of a weighted graph.
In the first case, each cell of the partition is considered as a binary set and
the defined operation is applied on each cell to produce a new transformation
(which is not necessarily a partition). In the second case, the partition is
considered as a graph and morphological operators are defined on this graph.
These operators provide morphological transformations on graphs, without the
need to explicitly define this graph structure from the partition.
"""

# Contributor: Serge BEUCHER

import mamba
import mambaComposed as mC

def cellsErode(imIn, imOut, n=1, se=mC.DEFAULT_SE, edge=mamba.FILLED):
    """
    Simultaneous erosion of size 'n' (default 1) of all the cells of the partition
    image 'imIn' with 'se' structuring element. The resulting partition is put in
    'imOut'.
    'edge' is set to FILLED by default.
    This operation works on 8-bit and 32-bit partitions.
    """
    
    imWrk1 = mamba.imageMb(imIn)
    imWrk2 = mamba.imageMb(imIn, 1)
    mC.dilate(imIn, imWrk1, n=n, se=se)
    mC.erode(imIn, imOut, n=n, se=se, edge=edge)
    mamba.generateSupMask(imOut, imWrk1, imWrk2, False)
    mamba.convertByMask(imWrk2, imWrk1, 0, mamba.computeMaxRange(imIn)[1])
    mamba.logic(imOut, imWrk1, imOut, "inf")
    

def cellsOpen(imIn, imOut, n=1, se=mC.DEFAULT_SE, edge=mamba.FILLED):
    """
    Simultaneous opening of size 'n' (default 1) of all the cells of the partition
    image 'imIn' with 'se' structuring element. The resulting partition is put in
    'imOut'.
    'edge' is set to FILLED by default.
    This operation works on 8-bit and 32-bit partitions.
    """
    
    imWrk = mamba.imageMb(imIn)
    cellsErode(imIn, imWrk, n, se=se, edge=edge)
    mC.dilate(imWrk, imOut, n, se=se.transpose())
       

def cellsComputeDistance(imIn, imOut, grid=mamba.DEFAULT_GRID, edge=mamba.EMPTY):
    """
    Computation of the distance function for each cell of the partition image 'imIn'.
    The result is put in the 32-bit image 'imOut'.
    This operator works on hexagonal or square 'grid' and 'edge' is set to EMPTY by
    default.
    """
    
    imWrk1 = mamba.imageMb(imIn)
    imWrk2 = mamba.imageMb(imIn, 1)
    se = mC.structuringElement(mamba.getDirections(grid), grid)
    cellsErode(imIn, imWrk1, 1, se=se, edge=edge)
    mamba.threshold(imWrk1, imWrk2, 1, 255)
    mamba.computeDistance(imWrk2, imOut, grid=grid, edge=edge)
    mamba.addConst(imOut, 1, imOut)


def equalNeighbor(imIn, imOut, nb, grid=mamba.DEFAULT_GRID, edge=mamba.FILLED):
    """
    This operator compares the value of each pixel of image 'imIn' with the value
    of its neighbor in direction given by 'nb'. If the values are equal, the pixel
    is unchanged. Otherwise, it takes value 0.
    This operator works on hexagonal or square 'grid' and 'edge' is set to FILLED
    by default.
    This operator works for 8-bit and 32-bit images.
    """
    
    imWrk1 = mamba.imageMb(imIn)
    imWrk2 = mamba.imageMb(imIn, 1)
    mamba.copy(imIn, imWrk1)
    mamba.copy(imIn, imOut)
    mamba.supNeighbor(imIn, imWrk1, nb, 1, grid=grid, edge=edge)
    mamba.infNeighbor(imOut, imOut, nb, 1, grid=grid, edge=edge)
    mamba.generateSupMask(imOut, imWrk1, imWrk2, False)
    mamba.convertByMask(imWrk2, imWrk1, 0, mamba.computeMaxRange(imIn)[1])
    mamba.logic(imOut, imWrk1, imOut, "inf")
    

def nonEqualNeighbor(imIn, imOut, nb, grid=mamba.DEFAULT_GRID, edge=mamba.FILLED):
    """
    This operator compares the value of each pixel of image 'imIn' with the value
    of its neighbor in direction given by 'nb'. If the values are different, the pixel
    is unchanged. Otherwise, it takes value 0.
    This operator works on hexagonal or square 'grid' and 'edge' is set to FILLED
    by default.
    This operator works for 8-bit and 32-bit images.
    """
    
    imWrk1 = mamba.imageMb(imIn)
    imWrk2 = mamba.imageMb(imIn)
    imWrk3 = mamba.imageMb(imIn, 1)
    mamba.copy(imIn, imWrk1)
    mamba.copy(imIn, imWrk2)
    mamba.supNeighbor(imWrk1, imWrk1, nb, 1, grid=grid, edge=edge)
    mamba.infNeighbor(imWrk2, imWrk2, nb, 1, grid=grid, edge=edge)
    mamba.generateSupMask(imWrk1, imWrk2, imWrk3, True)
    mamba.convertByMask(imWrk3, imWrk1, 0, mamba.computeMaxRange(imIn)[1])
    mamba.logic(imIn, imWrk1, imOut, "inf")

   
def cellsHMT(imIn, imOut, dse, edge=mamba.EMPTY):
    """
    A Hit-Or-Miss transform is performed on each cell of the partition 'imIn'. 'dse'
    is a double structuring element (see thinthick.py module). The result is put
    in 'imOut'. 'edge' is set to EMPTY by default.
    """
    
    imWrk1 = mamba.imageMb(imIn)
    imWrk2 = mamba.imageMb(imIn)
    cse0 = dse.getStructuringElement(0)
    cse1 = dse.getStructuringElement(1)
    mamba.copy(imIn, imOut)
    mamba.copy(imIn, imWrk1)
    for dir in cse1.getDirections(withoutZero=True):
        equalNeighbor(imWrk1, imWrk2, dir, grid=cse1.getGrid(), edge=edge)
        mamba.logic(imOut, imWrk2, imOut, "inf")
    for dir in cse0.getDirections(withoutZero=True):
        nonEqualNeighbor(imWrk1, imWrk2, dir, grid=cse0.getGrid(), edge=edge)
        mamba.logic(imOut, imWrk2, imOut, "inf")


def cellsThin(imIn, imOut, dse, edge=mamba.EMPTY):
    """
    A simple thinning transform is performed on each cell of the partition 'imIn'.
    'dse' is a double structuring element (see thinthick.py module). The result
    is put in 'imOut'. 'edge' is set to EMPTY by default. 
    """
    
    imWrk = mamba.imageMb(imIn)
    cellsHMT(imIn, imWrk, dse, edge=edge)
    mamba.sub(imIn, imWrk, imOut)

  
def cellsFullThin(imIn, imOut, dse, edge=mamba.EMPTY):
    """
    A full thinning transform is performed on each cell of the partition 'imIn'
    until idempotence. 'dse' is a double structuring element. The result
    is put in 'imOut'. 'edge' is set to EMPTY by default. 
    """
    
    imWrk = mamba.imageMb(imIn)
    mamba.copy(imIn, imOut)
    v1 = mamba.computeVolume(imOut)
    v2 = 0
    while v1 != v2:
        v2 = v1
        for i in range(mamba.gridNeighbors(dse.getGrid())):
            cellsThin(imOut, imOut, dse, edge=edge)
            dse = dse.rotate()
        v1 = mamba.computeVolume(imOut)


def cellsBuild(imIn, imInOut, grid=mamba.DEFAULT_GRID):
    """
    Geodesic reconstruction of the cells of the partition image 'imIn' which are
    marked by the image 'imInOut'. The marked cells take the value of their
    corresponding marker. The result is stored in 'imInOut'.
    The images can be 8-bit or 32-bit images.
    'grid' can be set to HEXAGONAL or SQUARE.    
    """
    
    imWrk1 = mamba.imageMb(imIn)
    imWrk2 = mamba.imageMb(imIn)
    imWrk3 = mamba.imageMb(imIn, 1)
    vol = 0
    prec_vol = -1
    dirs = mamba.getDirections(grid)[1:]
    while (prec_vol!=vol):
        prec_vol = vol
        for d in dirs:
            mamba.copy(imIn, imWrk1)
            mamba.copy(imIn, imWrk2)
            mamba.supNeighbor(imWrk1, imWrk1, d, 1, grid=grid)
            mamba.infNeighbor(imWrk2, imWrk2, d, 1, grid=grid)
            mamba.generateSupMask(imWrk2, imWrk1, imWrk3, False)
            mamba.convertByMask(imWrk3, imWrk1, 0, mamba.computeMaxRange(imIn)[1])
            mC.linearDilate(imInOut, imWrk2, d, 1, grid=grid)
            mamba.logic(imWrk2, imWrk1, imWrk2, "inf")
            mamba.buildNeighbor(imWrk1, imWrk2, d, grid=grid)
            mamba.logic(imWrk2, imInOut, imInOut, "sup")
        vol = mamba.computeVolume(imInOut)

        
def cellsExtract(imIn, imMarkers, imOut, grid=mamba.DEFAULT_GRID):
    """
    Geodesic reconstruction and extraction of the cells of the partition image
    'imIn' which are marked by the binary marker image 'imMarkers'. The marked
    cells keep their initial value. The result is stored in 'imOut'.
    The images can be 8-bit or 32-bit images.
    'grid' can be set to HEXAGONAL or SQUARE.
    """
    
    imWrk1 = mamba.imageMb(imIn)
    imWrk2 = mamba.imageMb(imIn)
    mamba.copy(imIn, imWrk1)
    mamba.convertByMask(imMarkers, imWrk2, 0, mamba.computeMaxRange(imIn)[1])
    mamba.logic(imIn, imWrk2,imOut, "inf")
    cellsBuild(imWrk1, imOut, grid=grid)
    
    
def cellsOpenByBuild(imIn, imOut, n=1, se=mC.DEFAULT_SE):
    """
    Opening by reconstruction of size 'n' (default 1) of the partition image
    'imIn'. 'se' defines the structuring element. The result is put in 'imOut'.    
    The images can be 8-bit or 32-bit images.
    """
    
    imWrk = mamba.imageMb(imIn)
    mamba.copy(imIn, imWrk)
    cellsErode(imIn, imOut, n=n, se=se)
    cellsBuild(imWrk, imOut, grid=se.getGrid())

  
def partitionErode(imIn, imOut, n=1, grid=mamba.DEFAULT_GRID):
    """
    Graph erosion of the corresponding partition image 'imIn'. The size is given
    by 'n'. The corresponding partition image of the resulting eroded graph is
    put in 'imOut'.
    'grid' can be set to HEXAGONAL or SQUARE.
    """
    
    imWrk = mamba.imageMb(imIn)
    mamba.negate(imIn, imWrk)
    mamba.copy(imWrk, imOut)
    se = mC.structuringElement(mamba.getDirections(grid), grid)
    for i in range(n):
        mC.dilate(imOut, imOut, se=se)
        cellsBuild(imWrk, imOut, grid=grid)
    mamba.negate(imOut, imOut)
    
    
def partitionDilate(imIn, imOut, n=1, grid=mamba.DEFAULT_GRID):
    """
    Graph dilation of the corresponding partition image 'imIn'. The size is given
    by 'n'. The corresponding partition image of the resulting dilated graph is
    put in 'imOut'.
    'grid' can be set to HEXAGONAL or SQUARE.    
    """
    
    imWrk = mamba.imageMb(imIn)
    mamba.copy(imIn, imOut)
    mamba.copy(imIn, imWrk)
    se = mC.structuringElement(mamba.getDirections(grid), grid)
    for i in range(n):
        mC.dilate(imOut, imOut, se=se)
        cellsBuild(imWrk, imOut, grid=grid)

    
