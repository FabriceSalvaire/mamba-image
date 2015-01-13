"""
This module contains morphological Hit-or-Miss, thinning and thickening
operators of the Mamba3D library, They use image3DMb instances as defined
in the mamba3D package.
"""

# Contributor: Nicolas BEUCHER

import mamba3D as m3D
import mambaComposed as mC
import mamba
import mambaCore

################################################################################
# Double (bi-phased) structuring elements definitions
################################################################################

class doubleStructuringElement3D:
    """
    This class allows to define a doublet of structuring elements used in a coded 
    format by Hit-or-Miss, thin and thick operations and their corresponding methods.
    """
    
    def __init__(self, *args):
        """
        Double structuring 3D element constructor. A double structuring
        element is defined by the first (background points) and second 
        (foreground points) structuring elements 3D.
        
        You can define it in two ways:
            * doubleStructuringElement3D(se0, se1): where 'se0' and 'se1' are 
            instances of the class structuringElement3D found in erodil3D
            module. These structuring elements must be defined on the same grid.
            * doubleStructuringElement3D(dse0, dse1, grid): where 'dse0' and
            'dse1' are direction lists and 'grid' defines the grid on which the
            two structuring elements are defined.
            
        If the constructor is called with inapropriate arguments, it raises a
        ValueError exception.
        """
        
        if len(args)==2:
            if args[0].getGrid()!=args[1].getGrid():
                raise ValueError("Grid value mismatch")
            self.se0 = args[0]
            self.se1 = args[1]
            self.grid = self.se0.getGrid()
        elif len(args)==3:
            self.se0 = m3D.structuringElement3D(args[0], args[2])
            self.se1 = m3D.structuringElement3D(args[1], args[2])
            self.grid = args[2]
        else:
            raise ValueError("Incorrect constructor call")
        
    def __repr__(self):
        return "doubleStructuringElement("+repr(self.se0)+", "+repr(self.se1)+")"
        
    def getGrid(self):
        """
        Returns the grid on which the double stucturing element is defined.
        """
        
        return self.grid
    
    def getStructuringElement3D(self, ground):
        """
        Returns the structuring element of the foreground if 'ground' is set to
        1 or the structuring element of the background otherwise.
        """
        
        if ground==1:
            return self.se1
        else:
            return self.se0
        
    def flip(self):
        """
        Flips the doublet of structuring elements. Flipping corresponds
        to a swap: the doublet (se0, se1) becomes (se1, se0).
        """
        
        return doubleStructuringElement3D(self.se1, self.se0)
    
################################################################################
# Hit-or-Miss, thin and thick binary operators
################################################################################
    
def binaryHMT3D(imIn, imOut, dse, edge=mamba.EMPTY):
    """
    Performs a binary Hit-or-miss operation on 3D image 'imIn' using the 
    doubleStructuringElement3D 'dse'. Result is put in 'imOut'.
    
    WARNING! 'imIn' and 'imOut' must be different images.
    """
    
    (width,height) = imIn.getSize()
    depth = imIn.getDepth()
    inl = imIn.getLength()
    outl = imOut.getLength()
    if depth!=1:
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_DEPTH)
    if inl!=outl:
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_SIZE)
    zext = dse.grid.getZExtension()
    imWrk = m3D.image3DMb(width, height, outl+zext*2, depth)
    
    # Border handling
    imWrk.reset()
    m3D.copy3D(imIn, imWrk, firstPlaneOut=1)
    if edge==mamba.FILLED:
        m3D.negate3D(imWrk, imWrk)
        for i in range(zext):
            imWrk[i].reset()
            imWrk[outl+zext*2-1-i].reset()
        dse = dse.flip()

    # Central point
    if dse.se1.hasZero():
        m3D.copy3D(imWrk, imOut, firstPlaneIn=1)
    else:
        if dse.se0.hasZero():
            for i in range(outl):
                mamba.negate(imWrk[i+1], imOut[i])
        else:
            imOut.fill(1)

    # Others directions
    dirs = m3D.getDirections3D(dse.getGrid())
    dirs.remove(0)
    dirs0 = dse.se0.getDirections()
    dirs1 = dse.se1.getDirections()
    grid2D = dse.getGrid().get2DGrid()
    for d in dirs:
        if d in dirs1:
            for i in range(outl):
                (planeOffset, dc) = dse.getGrid().convertFromDir(d,i)
                mamba.infNeighbor(imWrk[i+1+planeOffset], imOut[i], dc, 1, grid=grid2D, edge=edge)
        elif d in dirs0:
            for i in range(outl):
                (planeOffset, dc) = dse.getGrid().convertFromDir(d,i)
                mamba.diffNeighbor(imWrk[i+1+planeOffset], imOut[i], dc, grid=grid2D, edge=edge)
    
def thin3D(imIn, imOut, dse, edge=mamba.EMPTY):
    """
    Elementary thinning operator with 'dse' double structuring element.
    'imIn' and 'imOut' are binary 3D images.
    
    'edge' is set to EMPTY by default.
    """
        
    imWrk = m3D.image3DMb(imIn)
    binaryHMT3D(imIn, imWrk, dse, edge=edge)
    m3D.diff3D(imIn, imWrk, imOut)
    
def thick3D(imIn, imOut, dse):
    """
    Elementary thickening operator with 'dse' double structuring element.
    'imIn' and 'imOut' are binary 3D images.
    
    The edge is always EMPTY (as for mamba.hitOrMiss).
    """
        
    imWrk = m3D.image3DMb(imIn)
    binaryHMT3D(imIn, imWrk, dse)
    m3D.logic3D(imIn, imWrk, imOut, "sup") 

