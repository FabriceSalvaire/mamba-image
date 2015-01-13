"""
This module regroups various functions/operators to perform conversion
based on image depth.
"""

# Contributors : Nicolas BEUCHER

import mamba3D as m3D
import mamba
import mambaCore
        
# Conversion and similar operators #############################################
    
def convert3D(imIn, imOut):
    """
    Converts the contents of 'imIn' to the depth of 'imOut' and puts the result
    in 'imOut'.
    
    Only greyscale to binary and binary to greyscale conversion are supported.
    Value 255 is in a greyscale image is considered as 1 in a binary one. All other
    values are transformed to 0. The reverse convention applies.
    
    This function works with 3D images.
    """
    outl = imOut.getLength()
    inl = imIn.getLength()
    if inl!=outl:
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_SIZE)
    
    for i in range(outl):
        mamba.convert(imIn[i], imOut[i])
    
def convertByMask3D(imIn, imOut, mFalse, mTrue):
    """
    Converts a binary image 'imIn' into a greyscale image (8-bit) or a 32-bit 
    image and puts the result in 'imOut'.
    
    white pixels of 'imIn' are set to value 'mTrue' in the output image and the 
    black pixels set to value 'mFalse'.
    
    This function works with 3D images.
    """
    outl = imOut.getLength()
    inl = imIn.getLength()
    if inl!=outl:
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_SIZE)
    
    for i in range(outl):
        mamba.convertByMask(imIn[i], imOut[i], mFalse, mTrue)

def threshold3D(imIn, imOut, low, high):
    """
    Performs a threshold operation over image 'imIn'.
    The result is put in binary image 'imOut'.
    
    All the pixels that have a strictly lower value than 'low' or 
    strictly higher than 'high' are set to false.
    Otherwise they are set to true.
    
    'imIn' can be a 8-bit or 32-bit image.
    
    This function works with 3D images.
    """
    outl = imOut.getLength()
    inl = imIn.getLength()
    if inl!=outl:
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_SIZE)
    
    for i in range(outl):
        mamba.threshold(imIn[i], imOut[i], low, high)
    
def generateSupMask3D(imIn1, imIn2, imOut, strict):
    """
    Generates a 3D binary mask image in 'imOut' where pixels are set to 1 when
    they are greater (strictly if 'strict' is set to True, greater or equal
    otherwise) in 3D image 'imIn1' than in 3D image 'imIn2'.
    
    'imIn1' and imIn2' can be 1-bit, 8-bit or 32-bit images of same
    size, length and depth.
    """
    outl = imOut.getLength()
    in1l = imIn1.getLength()
    in2l = imIn2.getLength()
    if in1l!=outl or in2l!=outl:
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_SIZE)
    
    for i in range(outl):
        mamba.generateSupMask(imIn1[i], imIn2[i], imOut[i], strict)
        
def lookup3D(imIn, imOut, lutable):
    """
    Converts the greyscale 3D image 'imIn' using the look-up table 'lutable'
    and puts the result in greyscale 3D image 'imOut'.
    
    'lutable' is a list containing 256 values with the first one corresponding 
    to 0 and the last one to 255.
    """
    outl = imOut.getLength()
    inl = imIn.getLength()
    if inl!=outl:
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_SIZE)
    
    for i in range(outl):
        mamba.lookup(imIn[i], imOut[i], lutable)

