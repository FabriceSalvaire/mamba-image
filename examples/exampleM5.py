# exampleM5.py
# OUT dem.png

## TITLE #######################################################################
# Reading, loading and downscaling TIFF images

## DESCRIPTION #################################################################
# This example shows you how to create 32-bit mamba images using data from
# TIFF formated images. TIFF format accepts a wide range of pixel coding (1-bit
# to 64-bit) so it might be a good choice to read them with a specific 
# function to ensure that they are correctly processed before loading up an image with
# the data. We also show how to downscale a 32-bit image into a greyscale image.
# This example will in the end allow you to see a DEM file that you can found
# at http://www.mapmart.com/samples.aspx (NED 10 meter).

## SCRIPT ######################################################################
# Importing the mamba module, the mambaComposed package and the mambaExtra 
# module
from mamba import *
import mambaExtra
import mambaComposed as mC
# This example needs to import PIL and the struct package
import Image
import struct

# Reusing the palette from a previous example as it gives a better
# reading of the DEM files
paletteDEM = (
0, 0, 131, 0, 0, 135, 0, 0, 139, 0, 0, 143, 0, 0, 147, 0, 0, 151, 0, 0, 155, 0, 0,
159, 0, 0, 163, 0, 0, 167, 0, 0, 171, 0, 0, 175, 0, 0, 179, 0, 0, 183, 0, 0, 187,
0, 0, 191, 0, 0, 195, 0, 0, 199, 0, 0, 203, 0, 0, 207, 0, 0, 211, 0, 0, 215, 0, 0,
219, 0, 0, 223, 0, 0, 227, 0, 0, 231, 0, 0, 235, 0, 0, 239, 0, 0, 243, 0, 0, 247,
0, 0, 251, 0, 0, 255, 0, 3, 255, 0, 7, 255, 0, 11, 255, 0, 15, 255, 0, 19, 255, 0,
23, 255, 0, 27, 255, 0, 31, 255, 0, 35, 255, 0, 39, 255, 0, 43, 255, 0, 47, 255, 0,
51, 255, 0, 55, 255, 0, 59, 255, 0, 63, 255, 0, 67, 255, 0, 71, 255, 0, 75, 255, 0,
79, 255, 0, 83, 255, 0, 87, 255, 0, 91, 255, 0, 95, 255, 0, 99, 255, 0, 103, 255,
0, 107, 255, 0, 111, 255, 0, 115, 255, 0, 119, 255, 0, 123, 255, 0, 127, 255, 0,
131, 255, 0, 135, 255, 0, 139, 255, 0, 143, 255, 0, 147, 255, 0, 151, 255, 0, 155,
255, 0, 159, 255, 0, 163, 255, 0, 167, 255, 0, 171, 255, 0, 175, 255, 0, 179, 255,
0, 183, 255, 0, 187, 255, 0, 191, 255, 0, 195, 255, 0, 199, 255, 0, 203, 255, 0,
207, 255, 0, 211, 255, 0, 215, 255, 0, 219, 255, 0, 223, 255, 0, 227, 255, 0, 231,
255, 0, 235, 255, 0, 239, 255, 0, 243, 255, 0, 247, 255, 0, 251, 255, 0, 255, 255,
3, 255, 255, 7, 255, 251, 11, 255, 247, 15, 255, 243, 19, 255, 239, 23, 255, 235,
27, 255, 231, 31, 255, 227, 35, 255, 223, 39, 255, 219, 43, 255, 215, 47, 255, 211,
51, 255, 207, 55, 255, 203, 59, 255, 199, 63, 255, 195, 67, 255, 191, 71, 255, 187,
75, 255, 183, 79, 255, 179, 83, 255, 175, 87, 255, 171, 91, 255, 167, 95, 255, 163,
99, 255, 159, 103, 255, 155, 107, 255, 151, 111, 255, 147, 115, 255, 143, 119, 255,
139, 123, 255, 135, 127, 255, 131, 131, 255, 127, 135, 255, 123, 139, 255, 119, 143,
255, 115, 147, 255, 111, 151, 255, 107, 155, 255, 103, 159, 255, 99, 163, 255, 95,
167, 255, 91, 171, 255, 87, 175, 255, 83, 179, 255, 79, 183, 255, 75, 187, 255, 71,
191, 255, 67, 195, 255, 63, 199, 255, 59, 203, 255, 55, 207, 255, 51, 211, 255, 47,
215, 255, 43, 219, 255, 39, 223, 255, 35, 227, 255, 31, 231, 255, 27, 235, 255, 23,
239, 255, 19, 243, 255, 15, 247, 255, 11, 251, 255, 7, 255, 255, 3, 255, 255, 0, 255,
251, 0, 255, 247, 0, 255, 243, 0, 255, 239, 0, 255, 235, 0, 255, 231, 0, 255, 227,
0, 255, 223, 0, 255, 219, 0, 255, 215, 0, 255, 211, 0, 255, 207, 0, 255, 203, 0,
255, 199, 0, 255, 195, 0, 255, 191, 0, 255, 187, 0, 255, 183, 0, 255, 179, 0, 255,
175, 0, 255, 171, 0, 255, 167, 0, 255, 163, 0, 255, 159, 0, 255, 155, 0, 255, 151,
0, 255, 147, 0, 255, 143, 0, 255, 139, 0, 255, 135, 0, 255, 131, 0, 255, 127, 0,
255, 123, 0, 255, 119, 0, 255, 115, 0, 255, 111, 0, 255, 107, 0, 255, 103, 0, 255,
99, 0, 255, 95, 0, 255, 91, 0, 255, 87, 0, 255, 83, 0, 255, 79, 0, 255, 75, 0, 255,
71, 0, 255, 67, 0, 255, 63, 0, 255, 59, 0, 255, 55, 0, 255, 51, 0, 255, 47, 0, 255,
43, 0, 255, 39, 0, 255, 35, 0, 255, 31, 0, 255, 27, 0, 255, 23, 0, 255, 19, 0, 255,
15, 0, 255, 11, 0, 255, 7, 0, 255, 3, 0, 255, 0, 0, 251, 0, 0, 247, 0, 0, 243, 0,
0, 239, 0, 0, 235, 0, 0, 231, 0, 0, 227, 0, 0, 223, 0, 0, 219, 0, 0, 215, 0, 0,
211, 0, 0, 207, 0, 0, 203, 0, 0, 199, 0, 0, 195, 0, 0, 191, 0, 0, 187, 0, 0, 183,
0, 0, 179, 0, 0, 175, 0, 0, 171, 0, 0, 167, 0, 0, 163, 0, 0, 159, 0, 0, 155, 0,
0, 151, 0, 0, 147, 0, 0, 143, 0, 0, 139, 0, 0, 135, 0, 0, 131, 0, 0
)

def createImageFromTIFF(path, fmt=""):
    """
    Opens a TIFF image and creates a 32-bit deep Mamba image.
    'path' indicates where to find the TIFF file.
    'fmt' indicates the format of the TIFF file in the same format 
    found in the python struct module (see http://docs.python.org/library/struct.html).
    If not given the function will try determine the format with meta
    data using PIL.
    """
    
    # Opening the TIFF image and extracting all the needed informations
    tiffim = Image.open(path)
    mode = tiffim.mode
    (w,h) = tiffim.size
    data = tiffim.tostring()
    
    # Creating the mamba image
    im32 = imageMb(w, h, 32)
    
    # Because Mamba works with images size that are multiple of 64 for
    # width and 2 for height, the created 32-bit image can have a different
    # size than the TIFF image that will request correction later
    (wc, hc) = im32.getSize()
    
    # Converting the data to appropriate format
    if fmt!="":
        # format given
        pass
    elif mode=="I;16":
        fmt = "H"
    elif mode=="I;32":
        fmt = "I"
    elif mode=="F;32":
        fmt = "f"
    else:
        raise ValueError("Cannot determines format for mode "+mode)
        
    wdata = ""
    bypd = struct.calcsize(fmt)
    for y in range(h):
        unpack_data = struct.unpack(w*fmt, data[y*w*bypd:(y+1)*w*bypd])
        unpack_data = map(int, unpack_data)
        wldata = struct.pack(w*"I", *unpack_data) + (wc-w)*"\x00\x00\x00\x00"
        wdata += wldata
    if h!=hc:
        # last line to add
        wdata += wc*"\x00\x00\x00\x00"
        
    # Loading the data inside the mamba image
    import mambaCore
    err = mambaCore.MB_Load(im32.mbIm, wdata, len(wdata))
    raiseExceptionOnError(err)
    
    return im32

def downscale(imIn, imOut):
    """
    Downscale a 32-bit image 'imIn', whom range can go from 0 up to 4G, to a 
    greyscale image 'imOut' of range 0 to 255. This function will ensure
    that the minimum of 'imIn' will be mapped to 0 in 'imOut' and that the
    maximum will be mapped to 255. All other values will be mapped linearly
    between those two.
    """
    
    imWrk = imageMb(imIn)
    (mi, ma) = computeRange(imIn)
    subConst(imIn, mi, imWrk)
    mulConst(imWrk, 255, imWrk)
    divConst(imWrk, ma-mi, imWrk)
    copyBytePlane(imWrk, 0, imOut)
    
imDEM = createImageFromTIFF("NED10Meter.tif")
imDEM_8 = imageMb(imDEM, 8)
imDEM_8.setPalette(paletteDEM)
downscale(imDEM,imDEM_8)
imDEM_8.save("dem.png")
