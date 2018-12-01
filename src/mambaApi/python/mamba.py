"""
This is the main module of the Mamba Image library. It provides basic functions 
and classes needed for handling images and defining mathematical morphology 
transformations and algorithms.

This module also contains image display functionalities and other user-friendly
features.
"""

from __future__ import division

from . import mambaCore
from . import mambaUtils as mbUtls
from .mambaDisplay import getDisplayer
from .mambaError import raiseExceptionOnError, raiseWarning

import os.path

try:
    import numpy as np
except:
    np = None

VERSION = "1.1.3"

###############################################################################
#  Definitions

class _grid(object):
    def __init__(self, id, default=False):
        self.id = id
        self.default = default
        
    def __repr__(self):
        if self.default:
            return "DEFAULT_GRID"
        elif self.id==mambaCore.MB_HEXAGONAL_GRID:
            return "HEXAGONAL"
        elif self.id==mambaCore.MB_SQUARE_GRID:
            return "SQUARE"
        else:
            return ""
            
    def __cmp__(self, other):
        return cmp(self.id, other.id)
            

HEXAGONAL = _grid(mambaCore.MB_HEXAGONAL_GRID)
""" Value to be used when working on an hexagonal grid. """

SQUARE = _grid(mambaCore.MB_SQUARE_GRID)
""" Value to be used when working on a square grid. """

DEFAULT_GRID = _grid(mambaCore.MB_HEXAGONAL_GRID, True)
""" Value holding the default grid (set to HEXAGONAL at Mamba startup). """

class _edge(object):
    def __init__(self, id):
        self.id = id
        
    def __repr__(self):
        if self.id==mambaCore.MB_EMPTY_EDGE:
            return "EMPTY"
        elif self.id==mambaCore.MB_FILLED_EDGE:
            return "FILLED"
        else:
            return ""
            
    def __cmp__(self, other):
        return cmp(self.id, other.id)

EMPTY = _edge(mambaCore.MB_EMPTY_EDGE)
""" Value to be used when setting an empty edge. """

FILLED = _edge(mambaCore.MB_FILLED_EDGE)
""" Value to be used when setting a filled edge. """

###############################################################################
#  Local variables and constants

_image_index = 1
_always_show = False

###############################################################################
# Public functions are functions dealing with grid, counter and such

def setDefaultGrid(grid):
    """
    This function will change the value of the default grid used in each 
    operator that needs to specify one.
    
    'grid' must be either HEXAGONAL or SQUARE.
    
    You can of course manually change the variable DEFAULT_GRID by yourself.
    Using this function is however recommended if you are not sure of what you 
    are doing.
    """
    if grid==HEXAGONAL or grid==SQUARE:
        DEFAULT_GRID.id = grid.id
    else:
        raiseWarning("Invalid grid for default")

def getDirections(grid=DEFAULT_GRID):
    """
    Returns a list containing all the possible directions available in 'grid' 
    (set to DEFAULT_GRID by default).
    
    If the 'grid' value is incorrect, the function returns an empty list.
    """
    if grid.id==mambaCore.MB_HEXAGONAL_GRID:
        return range(7)
    elif grid.id==mambaCore.MB_SQUARE_GRID:
        return range(9)
    else:
        return []

def gridNeighbors(grid=DEFAULT_GRID):
    """
    Returns the number of neighbors of a point in 'grid' (6 or 8).
    
    If the 'grid' value is incorrect, the function returns 0.
    """
    if grid.id==mambaCore.MB_HEXAGONAL_GRID:
        return 6
    elif grid.id==mambaCore.MB_SQUARE_GRID:
        return 8
    else:
        return 0

def rotateDirection(d, step=1, grid=DEFAULT_GRID):
    """
    Calculates the value of the new direction starting from direction 'd' after 
    'step' rotations (default value 1). If 'step' is positive, rotations are 
    performed clockwise. They are counterclockwise if 'sterp' is negative.
    Calculation is made according to the grid. Direction 0 is taken into account 
    (and always unchanged).
    """
    if d == 0:
        return 0
    else:
        return (d + step - 1)%gridNeighbors(grid) + 1

def transposeDirection(d, grid=DEFAULT_GRID):
    """
    Calculates the transposed (opposite) direction value of direction 'd' 
    (corresponds to a rotation of gridNeighbors/2 steps).
    """
    o = rotateDirection(d, gridNeighbors(grid)//2, grid)
    return o
    
def tidyDisplays(displayer=None):
    """
    Tidies the displayed images.
    This function will try to optimize, given the actual screen size, the 
    position of the images so that every one may be visible (not always)
    possible if many images are displayed).
    """
    if not displayer:
        displayer = getDisplayer()
    displayer.tidyWindows()
    
def setImageIndex(index):
    """
    Sets the image index used for naming to a given value 'index'
    """
    global _image_index
    
    _image_index = index

def setShowImages(showThem):
    """
    Activates automatically the display for new images when 'showThem' is set to
    True.
    """
    global _always_show
    
    _always_show = showThem

def getShowImages():
    """
    Returns the display status ('always_show' value).
    """
    global _always_show
    
    return _always_show
    
def getImageCounter():
    """
    Returns the number of images actually defined and allocated in the Mamba
    library. This function may be useful for debugging purposes.
    """
    return mambaCore.cvar.MB_refcounter

###############################################################################
#  Color palettes
#  Three color palettes are defined: rainbow, inverted_rainbow and patchwork

rainbow = (0,0,0)
for _i in range(51): #red to yellow
    rainbow = rainbow + (255,_i*5,0)
for _i in range(51): #yellow to green
    rainbow = rainbow + (255-_i*5,255,0)
for _i in range(51): #green to indigo
    rainbow = rainbow + (0,255,_i*5)
for _i in range(51): #indigo to blue
    rainbow = rainbow + (0,255-_i*5,255)
for _i in range(51): #blue to purple
    rainbow = rainbow + (_i*5,0,255)
    
inverted_rainbow = (0,0,0)
for _i in range(51): #purple to blue
    inverted_rainbow = inverted_rainbow + (255-_i*5,0,255)
for _i in range(51): #blue to indigo
    inverted_rainbow = inverted_rainbow + (0,_i*5,255)
for _i in range(51): #indigo to green
    inverted_rainbow = inverted_rainbow + (0,255,255-_i*5)
for _i in range(51): #green to yellow
    inverted_rainbow = inverted_rainbow + (_i*5,255,0)
for _i in range(51): #yellow to red
    inverted_rainbow = inverted_rainbow + (255,255-_i*5,0)

patchwork = ()
_blue_val = (0, 146, 36, 219, 109, 182, 73, 255)
_green_val = (0, 85, 170, 255)
_red_val = (0, 73, 182, 109, 219, 36, 146, 255)
for _i in range (8):
    for _j in range(4):
        for _k in range(8):
            patchwork = patchwork + (_red_val[_k], _green_val[_j], _blue_val[_i])

###############################################################################
#  Classes

class NumpyWrapper(object):

    MB_ROUND_WIDTH = 64 # px
    MB_ROUND_HEIGHT = 2 # px
    
    Y_TOP = Y_BOTTOM = 1 # line
    X_LEFT = X_RIGHT = 16 # bytes = 16 uint8 = 8 uint16 = 4 uint32 = 2 uint64
    
    CHARBIT = 8 # bits
    
    MB_MAX_IMAGE_SIZE = 4294967296 # px

    def __init__(self, height, width, depth):

        self.height = height
        self.width = width
        self.depth = depth

        if np is None:
            raise NameError("Could not import Numpy")

        print("height, width = ({}, {}) depth {}".format(height, width, depth))
    
        # computation of the corrected size
        # w = n*M + r    where 0 <= r < M
        # ((w + M-1)//M)*M = (( (n+1)*M + r-1 )//M)*M
        # if r = 0: n*M
        # else: (n+1)*M
        self.adjusted_width = ((width + self.MB_ROUND_WIDTH-1) // self.MB_ROUND_WIDTH) * self.MB_ROUND_WIDTH
        self.adjusted_height = ((height + self.MB_ROUND_HEIGHT-1) // self.MB_ROUND_HEIGHT) * self.MB_ROUND_HEIGHT

        print("adjusted height, width = ({}, {})".format(self.adjusted_height, self.adjusted_width))
        
        # verification over the image size
        image_size = self.adjusted_width * self.adjusted_height
        if not (self.adjusted_width > 0 and self.adjusted_height > 0 and image_size <= self.MB_MAX_IMAGE_SIZE):
            raise NameError('Bad image dimensions')

        # verification over the depth
        # acceptable values are 8, or 32 bits
        if depth not in (8, 32):
            raise NameError('Bad depth')
    
        # full height in pixel with edge
        # full_h = height + 2 * 1
        self.full_height = self.adjusted_height + self.Y_TOP + self.Y_BOTTOM
        # full width in bytes with edge
        # full_w = (with*depth + 8-1)/8 + 2 * 16
        # ensure with*depth multiple of 8 + 32
        self.line_step = (self.adjusted_width*depth + self.CHARBIT-1)//self.CHARBIT + self.X_LEFT + self.X_RIGHT
        pixel_byte_size = depth//self.CHARBIT
        self.full_width = self.line_step//pixel_byte_size
        self.x_offset = self.X_LEFT//pixel_byte_size

        print("offset y, x = ({}, {})".format(self.Y_TOP, self.x_offset))
        print("full height, width = ({}, {})".format(self.full_height, self.full_width))

        if depth == 8:
            dtype = np.uint8
        elif depth == 32:
            dtype = np.uint32

        self.array = np.zeros((self.full_height, self.full_width), dtype=dtype)

    @property
    def view(self):
        return self.array[self.Y_TOP:self.Y_TOP+self.height, self.x_offset:self.x_offset+self.width]

    def clone(self):
        return self.__class__(self.height, self.width, self.depth)

class imageMb(object):
    """
    Defines the imageMb class and its methods.
    All mamba images are represented by this class.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor for a Mamba image object.
        
        This constructor allows a wide range of possibilities for defining an image:
            * imageMb(): without arguments will create an empty greyscale image.
            * imageMb(im): will create an image using the same size and depth
              than 'im'.
            * imageMb(depth): will create an image with the desired 'depth' (1, 8 or 32).
            * imageMb(path): will load the image located in 'path'.
            * imageMb(im, depth): will create an image using the same size than 'im' 
            and the specified 'depth'.
            * imageMb(path, depth): will load the image located in 'path' and 
            convert it to the specified 'depth'.
            * imageMb(width, height): will create an image with size 'width'x'height'.
            * imageMb(width, height, depth): will create an image with size 
            'width'x'height' and the specified 'depth'.
            
        When not specified, the width and height of the image will be set to 
        256x256. The default depth is 8 (greyscale).
        
        When loading an image from a file, please note that Mamba accepts all 
        kinds of images (actually all the PIL supported formats). You can specify
        the RGB filter that will be used to convert a color image into a greyscale 
        image by adding the rgbfilter=<your_filter> to the argument of the
        constructor.
        """
        global _image_index
        
        # List of all the parameters that must be retrieved from the arguments
        rgbfilter = None
        displayer = None
        
        # First we look into the dictionnary to see if they were specified
        # specifically by the user
        if "rgbfilter" in kwargs:
            rgbfilter = kwargs["rgbfilter"]
        if "displayer" in kwargs:
            displayer = kwargs["displayer"]
            
        # We analyze the arguments given to the constructor
        if len(args)==0:
            # First case : no argument was given
            # -> imageMb()
            self.mbIm = mbUtls.create(256, 256, 8)
            self.name = "Image "+str(_image_index)
            _image_index = _image_index + 1
        elif len(args)==1:
            # Second case : the user gives only one argument
            if isinstance(args[0], imageMb):
                # -> imageMb(im)
                self.mbIm = mbUtls.create(args[0].mbIm.width, args[0].mbIm.height, args[0].mbIm.depth)
                self.name = "Image "+str(_image_index)
                _image_index = _image_index + 1
            elif isinstance(args[0], NumpyWrapper):
                self.mbIm = mbUtls.create_from_numpy(args[0])
                self.name = "Image "+str(_image_index)
                _image_index = _image_index + 1
            elif isinstance(args[0], str):
                # -> imageMb(path)
                self.mbIm = mbUtls.load(args[0], rgb2l=rgbfilter)
                self.name = os.path.split(args[0])[1]
            else:
                # -> imageMb(depth)
                self.mbIm = mbUtls.create(256, 256, args[0])
                self.name = "Image "+str(_image_index)
                _image_index = _image_index + 1
        elif len(args)==2:
            # Third case : two arguments
            if isinstance(args[0], imageMb):
                # -> imageMb(im, depth)
                self.mbIm = mbUtls.create(args[0].mbIm.width, args[0].mbIm.height, args[1])
                self.name = "Image "+str(_image_index)
                _image_index = _image_index + 1
            elif isinstance(args[0], str):
                # -> imageMb(path, depth)
                next_mbIm = mbUtls.load(args[0], rgb2l=rgbfilter)
                if args[1]==1:
                    self.mbIm = mbUtls.create(next_mbIm.width,next_mbIm.height,1)
                    err = mambaCore.MB_Convert(next_mbIm, self.mbIm)
                    raiseExceptionOnError(err)
                elif args[1]==8:
                    self.mbIm = next_mbIm
                else:
                    self.mbIm = mbUtls.create(next_mbIm.width,next_mbIm.height,32)
                    err = mambaCore.MB_CopyBytePlane(next_mbIm, self.mbIm, 0)
                    raiseExceptionOnError(err)
                self.name = os.path.split(args[0])[1]
            else:
                # -> imageMb(width, height)
                self.mbIm = mbUtls.create(args[0], args[1], 8)
                self.name = "Image "+str(_image_index)
                _image_index = _image_index + 1
        else:
            # Last case: at least 3 arguments are given
            # -> imageMb(width, height, depth)
            self.mbIm = mbUtls.create(args[0], args[1], args[2])
            self.name = "Image "+str(_image_index)
            _image_index = _image_index + 1
        
        self.displayId = ''
        self.palette = None
        if displayer:
            self.gd = displayer
        else:
            self.gd = None
        if getShowImages():
            self.showDisplay()
            
    def __str__(self):
        return 'Mamba image object : '+self.name+' - '+str(self.mbIm.depth)
        
    def __del__(self):
        if hasattr(self, "displayId") and self.displayId != '':
            self.gd.destroyWindow(self.displayId)
        del self
    
    def getSize(self):
        """
        Returns the size (a tuple width and height) of the image.
        """
        return (self.mbIm.width, self.mbIm.height)
    
    def getDepth(self):
        """
        Returns the depth of the image.
        """
        return self.mbIm.depth
        
    def setName(self, name):
        """
        Use this function to set the image 'name'.
        """
        self.name = name
        if self.displayId != '':
            self.gd.retitleWindow(self.displayId, name)
            
    def getName(self):
        """
        Returns the name of the image.
        """
        return self.name
            
    def setPalette(self, pal):
        """
        Defines the palette used to convert the image in color for display
        and save. 'pal' may be rainbow, inverted_rainbow, patchwork or any
        user-defined palette.
        """
        self.palette = pal
        if self.displayId != '':
            self.gd.colorizeWindow(self.displayId, self.palette)
            
    def resetPalette(self):
        """
        Undefines the palette used to convert the image in color for display
        and save. The greyscale palette will be used then.
        """
        self.palette = None
        if self.displayId != '':
            self.gd.colorizeWindow(self.displayId, self.palette)
            
    def load(self, path, rgbfilter=None):
        """
        Loads the image in 'path' into the Mamba image.
        
        The optional 'rgbfilter' argument can be used to specify how to convert
        a color image into a greyscale image. It is a sequence of 3 float values 
        indicating the amount of red, green and blue to take from the image to
        obtain the grey value.
        By default, the color conversion uses the ITU-R 601-2 luma transform (see
        PIL documentation for details).
        """
        next_mbIm = mbUtls.load(path, size=(self.mbIm.width,self.mbIm.height), rgb2l=rgbfilter)
        if self.mbIm.depth==1:
            err = mambaCore.MB_Convert(next_mbIm, self.mbIm)
            raiseExceptionOnError(err)
        elif self.mbIm.depth==8:
            err = mambaCore.MB_Copy(next_mbIm, self.mbIm)
            raiseExceptionOnError(err)
        else:
            err = mambaCore.MB_CopyBytePlane(next_mbIm, self.mbIm, 0)
            raiseExceptionOnError(err)
        self.setName(os.path.split(path)[1])
        if self.displayId != '':
            self.gd.reconnectWindow(self.displayId, self)
        
    def save(self, path):
        """
        Saves the image at the corresponding 'path' using PIL library.
        The format is automatically deduced by PIL from the image name extension.
        Note that, if the image comes with a palette, the image is saved with
        this palette.        
        """
        mbUtls.save(self.mbIm, path, self.palette)
        
    def loadRaw(self, data):
        """
        Fills the image with the raw string 'data'. The length of data must
        fit the image size and depth.
        This method only works on 8 and 32-bit images.
        """
        assert(len(data)==self.mbIm.width*self.mbIm.height*(self.mbIm.depth//8))
        err = mambaCore.MB_Load(self.mbIm,data,len(data))
        raiseExceptionOnError(err)
        self.updateDisplay()
        
    def extractRaw(self):
        """
        Extracts and returns the image raw string data.
        This method only works on 8 and 32-bit images.
        """
        err,data = mambaCore.MB_Extract(self.mbIm)
        raiseExceptionOnError(err)
        return data
        
    def fill(self, v):
        """
        Completely fills the image with a given value 'v'.
        A zero value makes the image completely dark.
        """
        err = mambaCore.MB_ConSet(self.mbIm,v)
        raiseExceptionOnError(err)
        self.updateDisplay()

    def reset(self):
        """
        Resets the image (all the pixels are put to 0).
        This method is equivalent to im.fill(0).
        """
        self.fill(0)
    
    def convert(self, depth):
        """
        Converts the image depth to the given 'depth'.
        The conversion algorithm is identical to the conversion used in the 
        convert function (see this function for details).
        """
        next_mbIm = mbUtls.create(self.mbIm.width,self.mbIm.height,depth)
        err = mambaCore.MB_Convert(self.mbIm, next_mbIm)
        raiseExceptionOnError(err)

        del self.mbIm
        self.mbIm = next_mbIm
        if self.displayId != '':
            self.gd.reconnectWindow(self.displayId, self)
        
    ### Display methods ########################################################
    def updateDisplay(self):
        """
        Called when the display associated to the image must be updated 
        (the image has changed).
        """
        if self.displayId != '':
            self.gd.updateWindow(self.displayId)
            
    def freezeDisplay(self):
        """
        Called to freeze the display of the image. Thus the image may evolve but
        the display will not show these evolutions until the method unfreezeDisplay
        is called.
        """
        if self.displayId != '':
            self.gd.controlWindow(self.displayId, "FREEZE")
            
    def unfreezeDisplay(self):
        """
        Called to unfreeze the display of the image. Thus the image display will
        be updated along with the modifications inside the image.
        """
        if self.displayId != '':
            self.gd.controlWindow(self.displayId, "UNFREEZE")
            
    def showDisplay(self):
        """
        Called to show the display associated to the image.
        Showing the display may significantly slow down your operations.
        """
        if self.displayId != '':
            self.gd.showWindow(self.displayId)
        else:
            if self.gd == None:
                self.gd = getDisplayer()
            self.displayId = self.gd.addWindow(im=self)
            self.gd.showWindow(self.displayId)
            
    def hideDisplay(self):
        """
        Called to hide the display associated to the image.
        If the display is hidden, the computations go faster.
        """
        if self.displayId != '':
            self.gd.hideWindow(self.displayId)
        
    ### Pixel manipulations ####################################################
    def setPixel(self, value, position):
        """
        Sets the pixel at 'position' with 'value'.
        'position' is a tuple holding (x,y).
        """
        err = mambaCore.MB_PutPixel(self.mbIm, value, position[0], position[1])
        raiseExceptionOnError(err)
        self.updateDisplay()
        
    def fastSetPixel(self, value, position):
        """
        Sets the pixel at 'position' with 'value'.
        'position' is a tuple holding (x,y).
        
        This function will not update the display to enable a faster drawing.
        So make sure to call the updateDisplay() method once your drawing is 
        finished, if you want to see the result.
        """
        err = mambaCore.MB_PutPixel(self.mbIm, value, position[0], position[1])
        raiseExceptionOnError(err)
        
    def getPixel(self, position):
        """
        Gets the pixel value at 'position'.
        'position' is a tuple holding (x,y).
        Returns the value of the pixel.
        """
        err, value = mambaCore.MB_GetPixel(self.mbIm, position[0], position[1])
        raiseExceptionOnError(err)
        return value
        
###############################################################################
#  Computation functions

def copy(imIn, imOut):
    """
    Copies 'imIn' image into 'imOut' image. 
    
    'imIn' and 'imOut' can be 1-bit, 8-bit or 32-bit images.
    The images must have the same depth and size.
    """
    err = mambaCore.MB_Copy(imIn.mbIm, imOut.mbIm)
    raiseExceptionOnError(err)
    imOut.updateDisplay()

def copyLine(imIn, nIn, imOut, nOut):
    """
    Copies the line numbered 'nIn' of image 'imIn' into 'imOut' at line 
    index 'nOut'.
    
    'imIn' and 'imOut' can be 1-bit, 8-bit or 32-bit images.
    The images must have the same depth and size.
    """
    err = mambaCore.MB_CopyLine(imIn.mbIm, imOut.mbIm, nIn, nOut)
    raiseExceptionOnError(err)
    imOut.updateDisplay()

def cropCopy(imIn, posIn, imOut, posOut, size):
    """
    Copies the pixels of 'imIn' in 'imOut' starting from position 'posIn' (tuple 
    x,y) in 'imIn' to position 'posOut' in 'imOut'. The size of the copy in 
    controlled by 'size' (tuple w,h). The actual size will be computed
    so as not to exceed the images border.

    The images must be of the same depth but can have different sizes. Only non
    binary images are accepted (8-bit or 32-bit).
    """
    err = mambaCore.MB_CropCopy(imIn.mbIm, posIn[0], posIn[1],
                                imOut.mbIm, posOut[0], posOut[1],
                                size[0], size[1])
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def convert(imIn, imOut):
    """
    Converts the contents of 'imIn' to the depth of 'imOut' and puts the result
    in 'imOut'.
    
    Only greyscale to binary and binary to greyscale conversion are supported.
    Value 255 is in a greyscale image is considered as 1 in a binary one. All other
    values are transformed to 0. The reverse convention applies.
    """
    err = mambaCore.MB_Convert(imIn.mbIm, imOut.mbIm)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def convertByMask(imIn, imOut, mFalse, mTrue):
    """
    Converts a binary image 'imIn' into a greyscale image (8-bit) or a 32-bit 
    image and puts the result in 'imOut'.
    
    white pixels of 'imIn' are set to value 'mTrue' in the output image and the 
    black pixels set to value 'mFalse'.
    """
    err = mambaCore.MB_Mask(imIn.mbIm, imOut.mbIm, mFalse, mTrue)
    raiseExceptionOnError(err)
    imOut.updateDisplay()

def negate(imIn, imOut):
    """
    Negates the image 'imIn' and puts the result in 'imOut'.
    
    The operation is a binary complement for binary images and a negation for
    greyscale and 32-bit images.
    """
    err = mambaCore.MB_Inv(imIn.mbIm, imOut.mbIm)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def shift(imIn, imOut, d, amp, fill, grid=DEFAULT_GRID):
    """
    Shifts image 'imIn' in direction 'd' of the 'grid' over an amplitude of 'amp'.
    The emptied space is filled with 'fill' value. The result is put in 'imOut'.
    
    'grid' value can be HEXAGONAL or SQUARE and is set to DEFAULT_GRID by 
    default.
    
    'imIn' and 'imOut' can be 1-bit, 8-bit or 32-bit images of same size and depth.
    """
    
    # shifting function depend on the image depth
    if imIn.getDepth()==32:
        err = mambaCore.MB_Shift32(imIn.mbIm, imOut.mbIm, d, amp, fill, grid.id)
    elif imIn.getDepth()==8:
        err = mambaCore.MB_Shift8(imIn.mbIm, imOut.mbIm, d, amp, fill, grid.id)
    else:
        err = mambaCore.MB_Shiftb(imIn.mbIm, imOut.mbIm, d, amp, fill, grid.id)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def shiftVector(imIn, imOut, vector, fill):
    """
    Shifts image 'imIn' by 'vector' (tuple with dx,dy).
    The emptied space is filled with 'fill' value.
    The result is put in 'imOut'.
    
    'imIn' and 'imOut' can be 1-bit, 8-bit or 32-bit images of same size and
    depth.
    """
    
    # shifting function depend on the image depth
    if imIn.getDepth()==32:
        err = mambaCore.MB_ShiftVector32(imIn.mbIm, imOut.mbIm, vector[0], vector[1], fill)
    elif imIn.getDepth()==8:
        err = mambaCore.MB_ShiftVector8(imIn.mbIm, imOut.mbIm, vector[0], vector[1], fill)
    else:
        err = mambaCore.MB_ShiftVectorb(imIn.mbIm, imOut.mbIm, vector[0], vector[1], fill)
    raiseExceptionOnError(err)
    imOut.updateDisplay()

def infNeighbor(imIn, imInout, nb, count, grid=DEFAULT_GRID, edge=FILLED):
    """
    Performs a minimum operation between the 'imInout' image pixels and their 
    neighbor 'nb' according to 'grid' in image 'imIn'. The result is put in 'imOut'. 
    
    The operation is repeated 'count' times if the two images imIn' and 'imInOut' 
    are referring to the same data. Otherwise, 'count' is not taken into account.
    
    'grid' value can be HEXAGONAL or SQUARE. 'edge' value can be EMPTY or FILLED.
    
    If a neighboring point falls outside the image window, its value in the operation
    is defined by 'edge'. If 'edge' is EMPTY, its value is 0. If 'edge' is FILLED,
    its value equals the maximal allowed value according to the depth of 'imIn'
    image.
    
    'imIn' and 'imOut' can be 1-bit, 8-bit or 32-bit images of same size and depth.
    """
    
    if imIn.getDepth()==1:
        err = mambaCore.MB_InfNbb(imIn.mbIm, imInout.mbIm, nb, count, grid.id, edge.id)
    elif imIn.getDepth()==8:
        err = mambaCore.MB_InfNb8(imIn.mbIm, imInout.mbIm, nb, count, grid.id, edge.id)
    else:
        err = mambaCore.MB_InfNb32(imIn.mbIm, imInout.mbIm, nb, count, grid.id, edge.id)
    raiseExceptionOnError(err)
    imInout.updateDisplay()

def infFarNeighbor(imIn, imInout, nb, amp, grid=DEFAULT_GRID, edge=FILLED):
    """
    Performs a minimum operation between the 'imInout' image pixels and their 
    neighbor 'nb' at distance 'amp' according to 'grid' in image 'imIn'. The result
    is put in 'imOut'. 
   
    'grid' value can be HEXAGONAL or SQUARE. 'edge' value can be EMPTY or FILLED.
    
    If a neighboring point falls outside the image window, its value in the operation
    is defined by 'edge'. If 'edge' is EMPTY, its value is 0. If 'edge' is FILLED,
    its value equals the maximal allowed value according to the depth of 'imIn'
    image.
    
    'imIn' and 'imOut' can be 1-bit, 8-bit or 32-bit images of same size and depth.
    """
    
    if imIn.getDepth()==1:
        err = mambaCore.MB_InfFarNbb(imIn.mbIm, imInout.mbIm, nb, amp, grid.id, edge.id)
    elif imIn.getDepth()==8:
        err = mambaCore.MB_InfFarNb8(imIn.mbIm, imInout.mbIm, nb, amp, grid.id, edge.id)
    else:
        err = mambaCore.MB_InfFarNb32(imIn.mbIm, imInout.mbIm, nb, amp, grid.id, edge.id)
    raiseExceptionOnError(err)
    imInout.updateDisplay()

def infVector(imIn, imInout, vector, edge=FILLED):
    """
    Performs a minimum operation between the 'imInout' image pixels and their
    corresponding pixels in image 'imIn' after it has been shifted by
    'vector' (tuple dx,dy). The result is put in 'imOut'.
   
    'edge' value can be EMPTY or FILLED.
    
    If a neighboring point falls outside the image window, its value in the operation
    is defined by 'edge'. If 'edge' is EMPTY, its value is 0. If 'edge' is FILLED,
    its value equals the maximal allowed value according to the depth of 'imIn'
    image.
    
    'imIn' and 'imOut' can be 1-bit, 8-bit or 32-bit images of same size and depth.
    """
    if imIn.getDepth()==1:
        err = mambaCore.MB_InfVectorb(imIn.mbIm, imInout.mbIm, vector[0], vector[1], edge.id)
    elif imIn.getDepth()==8:
        err = mambaCore.MB_InfVector8(imIn.mbIm, imInout.mbIm, vector[0], vector[1], edge.id)
    else:
        err = mambaCore.MB_InfVector32(imIn.mbIm, imInout.mbIm, vector[0], vector[1], edge.id)
    raiseExceptionOnError(err)
    imInout.updateDisplay()

def supNeighbor(imIn, imInout, nb, count, grid=DEFAULT_GRID, edge=EMPTY):
    """
    Performs a maximum operation between the 'imInout' image pixels and their 
    neighbor 'nb' according to 'grid' in image 'imIn'. The result is put in 'imOut'. 
   
    The operation is repeated 'count' times if the two images imIn' and 'imInOut' 
    are referring to the same data. Otherwise, 'count' is not taken into account.
    
    'grid' value can be HEXAGONAL or SQUARE. 'edge' value can be EMPTY or FILLED.
    
    If a neighboring point falls outside the image window, its value in the operation
    is defined by 'edge'. If 'edge' is EMPTY, its value is 0. If 'edge' is FILLED,
    its value equals the maximal allowed value according to the depth of 'imIn'
    image.
    
    'imIn' and 'imOut' can be 1-bit, 8-bit or 32-bit images of same size and depth.
    """
    
    if imIn.getDepth()==1:
        err = mambaCore.MB_SupNbb(imIn.mbIm, imInout.mbIm, nb, count, grid.id, edge.id)
    elif imIn.getDepth()==8:
        err = mambaCore.MB_SupNb8(imIn.mbIm, imInout.mbIm, nb, count, grid.id, edge.id)
    else:
        err = mambaCore.MB_SupNb32(imIn.mbIm, imInout.mbIm, nb, count, grid.id, edge.id)
    raiseExceptionOnError(err)
    imInout.updateDisplay()

def supFarNeighbor(imIn, imInout, nb, amp, grid=DEFAULT_GRID, edge=EMPTY):
    """
    Performs a maximum operation between the 'imInout' image pixels and their 
    neighbor 'nb' at distance 'amp' according to 'grid' in image 'imIn'. The result
    is put in 'imOut'. 
   
    'grid' value can be HEXAGONAL or SQUARE. 'edge' value can be EMPTY or FILLED.
    
    If a neighboring point falls outside the image window, its value in the operation
    is defined by 'edge'. If 'edge' is EMPTY, its value is 0. If 'edge' is FILLED,
    its value equals the maximal allowed value according to the depth of 'imIn'
    image.
    
    'imIn' and 'imOut' can be 1-bit, 8-bit or 32-bit images of same size and depth.
    """
    err = mambaCore.ERR_BAD_DEPTH # If a 32bit image is given an error should be raised
    
    if imIn.getDepth()==1:

        err = mambaCore.MB_SupFarNbb(imIn.mbIm, imInout.mbIm, nb, amp, grid.id, edge.id)
    elif imIn.getDepth()==8:
        err = mambaCore.MB_SupFarNb8(imIn.mbIm, imInout.mbIm, nb, amp, grid.id, edge.id)
    else:
        err = mambaCore.MB_SupFarNb32(imIn.mbIm, imInout.mbIm, nb, amp, grid.id, edge.id)
    raiseExceptionOnError(err)
    imInout.updateDisplay()

def supVector(imIn, imInout, vector, edge=EMPTY):
    """
    Performs a maximum operation between the 'imInout' image pixels and their
    corresponding pixels in image 'imIn' after it has been shifted by
    'vector' (tuple dx,dy). The result is put in 'imOut'.
   
    'edge' value can be EMPTY or FILLED.
    
    If a neighboring point falls outside the image window, its value in the operation
    is defined by 'edge'. If 'edge' is EMPTY, its value is 0. If 'edge' is FILLED,
    its value equals the maximal allowed value according to the depth of 'imIn'
    image.
    
    'imIn' and 'imOut' can be 1-bit, 8-bit or 32-bit images of same size and depth.
    """
    if imIn.getDepth()==1:
        err = mambaCore.MB_SupVectorb(imIn.mbIm, imInout.mbIm, vector[0], vector[1], edge.id)
    elif imIn.getDepth()==8:
        err = mambaCore.MB_SupVector8(imIn.mbIm, imInout.mbIm, vector[0], vector[1], edge.id)
    else:
        err = mambaCore.MB_SupVector32(imIn.mbIm, imInout.mbIm, vector[0], vector[1], edge.id)
    raiseExceptionOnError(err)
    imInout.updateDisplay()
   
def diffNeighbor(imIn, imInout, nb, grid=DEFAULT_GRID, edge=EMPTY):
    """
    Performs a set difference operation between the 'imInout' image pixels and 
    their neighbor 'nb' according to 'grid' in image 'imIn'. The result is put 
    in 'imOut'. 
   
    'grid' value can be HEXAGONAL or SQUARE. 'edge' value can be EMPTY or FILLED.
    
    If a neighboring point falls outside the image window, its value in the operation
    is defined by 'edge'. If 'edge' is EMPTY, its value is 0. If 'edge' is FILLED,
    its value equals the maximal allowed value according to the depth of 'imIn'
    image.
    
    'imIn' and 'imOut' can be 1-bit or 8-bit images of same size and depth. It does not work on
    32-bit images.
    """
    err = mambaCore.ERR_BAD_DEPTH # If a 32-bit image is given an error should be raised
    
    if imIn.getDepth()==8:
        err = mambaCore.MB_DiffNb8(imIn.mbIm, imInout.mbIm, nb, grid.id, edge.id)
    elif imIn.getDepth()==1:
        err = mambaCore.MB_DiffNbb(imIn.mbIm, imInout.mbIm, nb, grid.id, edge.id)
    raiseExceptionOnError(err)
    imInout.updateDisplay()

def buildNeighbor(imMask, imInout, d, grid=DEFAULT_GRID):
    """
    Builds image 'imInout' in direction 'd' according to 'grid' using 'imMask'
    as a mask (the propagation is performed only in 'd' direction).
    
    The function also returns the volume of the image 'imInout' after the
    build operation.
    
    'grid' value can be HEXAGONAL or SQUARE.
    """
    
    volume = 0
    err = mambaCore.ERR_BAD_DEPTH # If a 32-bit image is given an error should be raised
    
    if imMask.getDepth()==1:
        err,volume = mambaCore.MB_BldNbb(imMask.mbIm,imInout.mbIm,d, grid.id)
    elif imMask.getDepth()==8:
        err,volume = mambaCore.MB_BldNb8(imMask.mbIm,imInout.mbIm,d, grid.id)
    else:
        err,volume = mambaCore.MB_BldNb32(imMask.mbIm,imInout.mbIm,d, grid.id)
    raiseExceptionOnError(err)
    imInout.updateDisplay()
    return volume
    
def dualbuildNeighbor(imMask, imInout, d, grid=DEFAULT_GRID):
    """
    Dual builds image 'imInout' in direction 'd' according to 'grid' using 
    'imMask' as a mask (the propagation is performed only in 'd' direction).
    
    The function also returns the volume of the image 'imInout' after the
    build operation.
    
    'grid' value can be HEXAGONAL or SQUARE.
    """
    
    volume = 0
    err = mambaCore.ERR_BAD_DEPTH # If a 32-bit image is given an error should be raised
    
    if imMask.getDepth()==1:
        err,volume = mambaCore.MB_DualBldNbb(imMask.mbIm,imInout.mbIm,d, grid.id)
    elif imMask.getDepth()==8:
        err,volume = mambaCore.MB_DualBldNb8(imMask.mbIm,imInout.mbIm,d, grid.id)
    else:
        err,volume = mambaCore.MB_DualBldNb32(imMask.mbIm,imInout.mbIm,d, grid.id)
    raiseExceptionOnError(err)
    imInout.updateDisplay()
    return volume
    
def hitOrMiss(imIn, imOut, cse0, cse1, grid=DEFAULT_GRID):
    """
    Performs a binary Hit-or-miss operation on image 'imIn' using the coded
    structuring elements 'cse0' and 'cse1'. Result is put in 'imOut'.
    
    WARNING! 'imIn' and 'imOut' must be different images.
    
    'grid' value can be HEXAGONAL or SQUARE.

    Structuring elements are integer values coding which directions
    must be taken into account. 'cse0' indicates which neighbor of the
    current pixel will be checked for a 0 value and 'cse1' those which will
    be evaluated for a 1 value. A neighbor in direction d is simply coded
    with the value 2**d. If you want to use multiple directions, just add their 
    codes to obtain the final structuring element coding.
    The edge is always set to EMPTY (therefore, there is 'edge' argument).
    
    You can also find a helper function (hitormissPatternSelector) in the 
    mambaExtra module.
    """
    
    err = mambaCore.MB_BinHitOrMiss(imIn.mbIm, imOut.mbIm, cse0, cse1, grid.id)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def compare(imIn1, imIn2, imOut):
    """
    Compares the two images 'imIn1' and 'imIn2'.
    The comparison is performed pixelwise by scanning the two images from top left
    to bottom right and it stops as soon as a pixel is different in the two images.
    The corresponding pixel in 'imOut' is set to the value of the pixel of 
    'imIn1'.
    
    The function returns a tuple holding the position of the first mismatching 
    pixel. The tuple value is (-1,-1) if the two images are identical.
    
    'imOut' is not reset at the beginning of the comparison.
    
    'imIn1', imIn2' and 'imOut' can be 1-bit, 8-bit or 32-bit images of same
    size and depth.
    """
    err, x, y =  mambaCore.MB_Compare(imIn1.mbIm, imIn2.mbIm,imOut.mbIm)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    return (x,y)
    
def add(imIn1, imIn2, imOut):
    """
    Adds 'imIn2' pixel values to 'imIn1' pixel values and puts the result in
    'imOut'. The operation can be sum up in the following formula : 
    
    imOut = imIn1 + imIn2.

    You can mix formats in the addition operation (a binary image can be added
    to a greyscale image, etc...).
    However you must ensure that the output image is as deep as the deepest of 
    the two added images.
    
    The operation is also saturated for greyscale images (e.g. on a 8-bit
    greyscale image, 255+1=255). With 32-bit images, the addition is not saturated.
    """
    err = mambaCore.MB_Add(imIn1.mbIm, imIn2.mbIm,imOut.mbIm)
    raiseExceptionOnError(err)
    imOut.updateDisplay()

def sub(imIn1, imIn2, imOut):
    """
    Subtracts 'imIn2' pixel values to 'imIn1' pixel values and put the result 
    in 'imOut'. The operation can be sum up in the following formula :
    
    imOut = imIn1 - imIn2

    You can mix formats in the substraction operation (a binary image can be
    substracted to a greyscale image, etc...). 
    However you must ensure that the output image is as deep as the deepest of 
    the two substracted images.
    
    The operation is also saturated for grey-scale images (e.g. on a grey scale 
    image 0-1=0) but not for 32-bit images.
    """
    err = mambaCore.MB_Sub(imIn1.mbIm, imIn2.mbIm,imOut.mbIm)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def mul(imIn1, imIn2, imOut):
    """
    Multiplies 'imIn2' pixel values with 'imIn1' pixel values and put the result
    in 'imOut'. The operation can be sum up in the following formula :
    
    imOut = imIn1 * imIn2

    You can mix formats in the multiply operation (a binary image can be
    multiplied with a greyscale image, etc...). 
    However you must ensure that the output image is as deep as the deepest of 
    the two input images.
    
    The operation is also saturated for greyscale images (e.g. on a greyscale 
    image 255*255=255).
    """
    err = mambaCore.MB_Mul(imIn1.mbIm, imIn2.mbIm,imOut.mbIm)
    raiseExceptionOnError(err)
    imOut.updateDisplay()

def diff(imIn1, imIn2, imOut):
    """
    Performs a set difference between 'imIn1' and 'imIn2' and puts the result in
    'imOut'. The set difference will copy 'imIn1' pixels in 'imOut' if the 
    corresponding pixel in 'imIn2' is lower and will write 0 otherwise:
    
    imOut = imIn1 if imIn1 > imin2
    imOut = 0 otherwise.
    
    'imIn1', imIn2' and 'imOut' can be 1-bit, 8-bit or 32-bit images of same
    size and depth.
    """
    err = mambaCore.MB_Diff(imIn1.mbIm, imIn2.mbIm,imOut.mbIm)
    raiseExceptionOnError(err)
    imOut.updateDisplay()

def logic(imIn1, imIn2 , imOut, log):
    """
    Performs a logic operation between the pixels of images 'imIn1' and 'imIn2'
    and put the result in 'imOut'.
    The logic operation to be performed is indicated through argument 'log'.
    The allowed logical operations in 'log' are : 
    
    "and", "or", "xor", ""inf" or "sup". 
    
    "and" performs a bitwise AND operation, "or" a bitwise OR and "xor" a bitwise XOR.
    "inf" calculates the minimum and "sup" the maximum between corresponding pixel values.

    'imIn1', imIn2' and 'imOut' can be 1-bit, 8-bit or 32-bit images of same
    size and depth.
    """
    if log=="and":
        err = mambaCore.MB_And(imIn1.mbIm, imIn2.mbIm,imOut.mbIm)
    elif log=="or":
        err = mambaCore.MB_Or(imIn1.mbIm, imIn2.mbIm,imOut.mbIm)
    elif log=="xor":
        err = mambaCore.MB_Xor(imIn1.mbIm, imIn2.mbIm,imOut.mbIm)
    elif log=="inf":
        err = mambaCore.MB_Inf(imIn1.mbIm, imIn2.mbIm,imOut.mbIm)
    elif log=="sup":
        err = mambaCore.MB_Sup(imIn1.mbIm, imIn2.mbIm,imOut.mbIm)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def threshold(imIn, imOut, low, high):
    """
    Performs a threshold operation over image 'imIn'.
    The result is put in binary image 'imOut'.
    
    All the pixels that have a strictly lower value than 'low' or 
    strictly higher than 'high' are set to false.
    Otherwise they are set to true.
    
    'imIn' can be a 8-bit or 32-bit image.
    """
    err = mambaCore.MB_Thresh(imIn.mbIm, imOut.mbIm, low, high)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def generateSupMask(imIn1, imIn2, imOut, strict):
    """
    Generates a binary mask image in 'imOut' where pixels are set to 1 when they
    are greater (strictly if 'strict' is set to True, greater or equal otherwise)
    in image 'imIn1' than in image 'imIn2'.
    
    'imIn1' and imIn2' can be 1-bit, 8-bit or 32-bit images of same
    size and depth.
    """
    err = mambaCore.MB_SupMask(imIn1.mbIm, imIn2.mbIm,imOut.mbIm, int(strict))
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def computeVolume(imIn):
    """
    Computes the volume of the image 'imIn', i.e. the sum of its pixel values.
    The computed integer value is returned by the function.
    
    'imIn' can be a 1-bit, 8-bit or 32-bit image.
    """
    err, volume = mambaCore.MB_Volume(imIn.mbIm)
    raiseExceptionOnError(err)
    return volume
    
def checkEmptiness(imIn):
    """
    Checks if image 'imIn' is empty (i.e. completely black).
    Returns True if so, False otherwise.
    
    'imIn' can be a 1-bit, 8-bit or 32-bit image.
    """
    err, isEmpty = mambaCore.MB_Check(imIn.mbIm)
    raiseExceptionOnError(err)
    return bool(isEmpty)
    
def computeMaxRange(imIn):
    """
    Returns a tuple with the minimum and maximum possible pixel values given the
    depth of image 'imIn'. The values are returned in a tuple holding the 
    minimum and the maximum.
    """
    err, min, max = mambaCore.MB_depthRange(imIn.mbIm)
    raiseExceptionOnError(err)
    return (min, max)

def computeRange(imIn):
    """
    Computes the range, i.e. the minimum and maximum values, of image 'imIn'.
    The values are returned in a tuple holding the minimum and the maximum.
    """
    err, min, max = mambaCore.MB_Range(imIn.mbIm)
    raiseExceptionOnError(err)
    return (min, max)
    
def getHistogram(imIn):
    """
    Returns a list holding the histogram of the greyscale image 'imIn' (0 to 255).
    """
    histo = 256*[0]
    err, histo = mambaCore.MB_Histo(imIn.mbIm,histo)
    raiseExceptionOnError(err)
    return histo
    
def lookup(imIn, imOut, lutable):
    """
    Converts the greyscale image 'imIn' using the look-up table 'lutable'
    and puts the result in greyscale image 'imOut'.
    
    'lutable' is a list containing 256 values with the first one corresponding 
    to 0 and the last one to 255.
    """
    err = mambaCore.MB_Lookup(imIn.mbIm,imOut.mbIm,lutable)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def addConst(imIn, v, imOut):
    """
    Adds 'imIn' pixel values to value 'v' and puts the result in 'imOut'. 
    The operation can be sum up in the following formula:
    
    imOut = imIn + v

    'imIn' and imOut' can be 8-bit or 32-bit images of same
    size and depth.
    
    The operation is saturated (limited to 255) for greyscale images.
    """
    err = mambaCore.MB_ConAdd(imIn.mbIm,v,imOut.mbIm)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def subConst(imIn, v, imOut):
    """
    Subtracts 'v' value to 'imIn' pixel values and puts the result in 'imOut'. 
    The operation can be sum up in the following formula: 
    
    imOut = imIn - v

    'imIn' and imOut' can be 8-bit or 32-bit images of same
    size and depth.
    
    The operation is saturated (lower limit is 0) for greyscale images.
    """
    err = mambaCore.MB_ConSub(imIn.mbIm,v,imOut.mbIm)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def mulConst(imIn, v, imOut):
    """
    Multiplies 'imIn' pixel values with value 'v' and puts the result in 'imOut'.
    The operation can be sum up in the following formula:
    
    imOut = imIn * v 

    The operation is saturated for greyscale images. You cannot use it with 
    binary images.
    """
    err = mambaCore.MB_ConMul(imIn.mbIm,v,imOut.mbIm)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def divConst(imIn, v, imOut):
    """
    Divides 'imIn' pixel values by value 'v' and puts the result in 'imOut'. 
    The operation can be sum up in the following formula: 
    
    imOut = imIn / v
    (or more acurately : imIn = imOut * v + r, r being the ignored reminder)

    A zero value in 'v' will return an error.
    For a 8-bit image, v will be restricted between 1 and 255.
    You cannot use it with binary images.
    """
    err = mambaCore.MB_ConDiv(imIn.mbIm,v,imOut.mbIm)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def label(imIn, imOut, lblow=1, lbhigh=256, grid=DEFAULT_GRID):
    """
    Labels the binary image 'imIn' and puts the result in 32-bit image 'imOut'.
    Returns the number of connected components found by the labeling algorithm.
    The labelling will be performed according to the 'grid' (HEXAGONAL is 
    6-Neighbors and SQUARE is 8-Neighbors).
    
    'lblow' and 'lbhigh' are used to restrain the possible values in the
    lower byte of 'imOut' pixel values. these values (and all their multiples of 
    256) are then reserved for another use (see Mamba User Manual for further details).
    """

    err, nbobj = mambaCore.MB_Labelb(imIn.mbIm,imOut.mbIm, lblow, lbhigh, grid.id)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    return nbobj
    
def copyBitPlane(imIn, plane, imOut):
    """
    Inserts or extracts a bit plane.
    If 'imIn' is a binary image, it is inserted at 'plane' position in 
    greyscale 'imOut'.
    If 'imIn' is a greyscale image, its bit plane at 'plane' position is 
    extracted and put into binary image 'imOut'.
    
    Plane values are 0 (LSB) to 7 (MSB).
    """ 
    err = mambaCore.MB_CopyBitPlane(imIn.mbIm,imOut.mbIm, plane)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def copyBytePlane(imIn, plane, imOut):
    """
    Inserts or extracts a byte plane.
    If 'imIn' is a greyscale image, it is inserted at 'plane' position in 
    32-bit 'imOut'.
    If 'imIn' is a 32-bit image, its byte plane at 'plane' position is 
    extracted and put into 'imOut'.
    
    Plane values are 0 (LSByte) to 3 (MSByte).
    """
    err = mambaCore.MB_CopyBytePlane(imIn.mbIm,imOut.mbIm, plane)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def computeDistance(imIn, imOut, grid=DEFAULT_GRID, edge=EMPTY):
    """
    Computes for each white pixel of binary 'imIn' the minimum distance to
    reach a connected component boundary while constantly staying in the set. 
    The result is put in 32-bit 'imOut'.
    
    The distance computation will be performed according to the 'grid' (HEXAGONAL
    is 6-Neighbors and SQUARE is 8-Neighbors). 'edge' can be FILLED or EMPTY.
    """

    err = mambaCore.MB_Distanceb(imIn.mbIm,imOut.mbIm, grid.id, edge.id)
    raiseExceptionOnError(err)
    imOut.updateDisplay()
    
def watershedSegment(imIn, imMarker, grid=DEFAULT_GRID, max_level=256):
    """
    Segments greyscale image 'imIn' using the watershed algorithm. 'imMarker' is
    used both as the marker image (the wells from which the flooding proceeds) 
    and as the output image. It is a 32-bit image. 'max_level' can be used to 
    limit the flooding process to a specific level (useful if you want to survey
    the flooding level by level).
    
    'grid' will change the number of neighbors considered by the algorithm 
    (HEXAGONAL is 6-Neighbors and SQUARE is 8-Neighbors).
    
    The result is put inside 'imMarker'. The three first byte planes contain
    the actual segmentation (each region has a specific label according to the
    original marker). The last plane represents the actual watershed line
    (pixels set to 255).
    """
    
    err = mambaCore.MB_Watershed(imIn.mbIm, imMarker.mbIm, max_level, grid.id)
    raiseExceptionOnError(err)
    imMarker.updateDisplay()
    
def basinSegment(imIn, imMarker, grid=DEFAULT_GRID, max_level=256):
    """
    Segments greyscale image 'imIn' using the watershed algorithm. 'imMarker' is
    used both as the marker image (the wells from which the flooding proceeds) 
    and as the output image. It is a 32-bit image. 'max_level' can be used to 
    limit the flooding process to a specific level (useful if you want to survey
    the flooding level by level).
    
    'grid' will change the number of neighbors considered by the algorithm 
    (HEXAGONAL is 6-Neighbors and SQUARE is 8-Neighbors).
    
    The result is put inside 'imMarker'. The three first byte planes contain
    the actual segmentation (each segment has a specific label according to the
    original marker). This function only return catchment basins (no watershed 
    line) and is faster than watershedSegment if you are not interested in the 
    watershed line.
    """
    
    err = mambaCore.MB_Basins(imIn.mbIm, imMarker.mbIm, max_level, grid.id)
    raiseExceptionOnError(err)
    imMarker.updateDisplay()
    
def hierarBuild(imMask, imInout, grid=DEFAULT_GRID):
    """
    Builds image 'imInout' using 'imMask' as a mask. This function only
    works with greyscale images and uses a hierarchical list algorithm to
    compute the result.
    
    'grid' will set the number of neighbors considered by the algorithm 
    (HEXAGONAL is 6-Neighbors and SQUARE is 8-Neighbors).
    
    This function is identical to build but it is faster. However, it works 
    only with greyscale images.
    """
    
    err = mambaCore.MB_HierarBld(imMask.mbIm, imInout.mbIm, grid.id)
    raiseExceptionOnError(err)
    imInout.updateDisplay()
    
def hierarDualBuild(imMask, imInout, grid=DEFAULT_GRID):
    """
    Builds (dual build) image 'imInout' using 'imMask' as a mask. This function 
    only works with greyscale images and uses a hierarchical list algorithm to
    compute the result.
    
    'grid' will set the number of neighbors considered by the algorithm 
    (HEXAGONAL is 6-Neighbors and SQUARE is 8-Neighbors).
    
    This function is identical to build but it is faster. However, it works 
    only with greyscale images.
    """
    
    err = mambaCore.MB_HierarDualBld(imMask.mbIm, imInout.mbIm, grid.id)
    raiseExceptionOnError(err)
    imInout.updateDisplay()

def extractFrame(imIn, threshold):
    """
    Extracts the smallest frame inside the image 'imIn' that includes all the
    pixels whose value is greater or equal to 'threshold'.
    
    'imIn' can be a 8-bit or 32-bit image.
    """
    err, x1, y1, x2, y2 = mambaCore.MB_Frame(imIn.mbIm, threshold)
    raiseExceptionOnError(err)
    return (x1, y1, x2, y2)
