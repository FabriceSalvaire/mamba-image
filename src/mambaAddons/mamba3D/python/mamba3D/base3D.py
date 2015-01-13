"""
This modules defines the basic 3D image class (which inherits from
the sequenceMb class and adds specific features)
"""

# Contributors : Nicolas BEUCHER

# imports
import mambaComposed
import mamba
import mambaCore
import mamba3D as m3D
import mamba3D.mamba3DCore as core3D

################################################################################
# 3D IMAGE CLASS
################################################################################
# image3DMb class 
# This class is the main class of the mamba3D package. It inherits from
# the mambaComposed.sequenceMB class and adds some methods to it (mainly
# for display and loading).

# Image counter
_image3D_index = 1

class image3DMb(mambaComposed.sequenceMb):
    """
    A 3D image is represented by an instance of this class.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Refer to mambaComposed.sequenceMb constructor documentation.
        """
        global _image3D_index
        mambaComposed.sequenceMb.__init__(self, *args, **kwargs)
        
        self.name = "Image3D "+str(_image3D_index)
        _image3D_index = _image3D_index + 1
        
        if kwargs.has_key("displayer"):
            self._displayerUsr = kwargs["displayer"]
        else:
            self._displayerUsr = None
        self._displayerPjt = m3D.getProjDisplayer
        self._displayerVtk = m3D.getVtkDisplayer
        self._displayPjt = None
        self._displayUsr = None
        self._displayVtk = None
        
        self.mb3DIm = core3D.MB3D_Image(list(map(lambda im: im.mbIm, self.seq)))
            
    def __str__(self):
        return 'Mamba 3D image object : '+self.name+' - '+str(self.depth)
        
    def __del__(self):
        if self._displayPjt:
            self._displayPjt.destroy()
        if self._displayUsr:
            self._displayUsr.destroy()
        if self._displayVtk:
            self._displayVtk.destroy()
        del self
    
    def loadRaw(self, path, preprocfunc=None):
        """
        Load a raw file representing a 3D image inside the image3DMb object.
        The file must contains the expected length of data (i.e. 
        width * height * length * (depth/8) ). The function works only
        with 8 and 32-bit images. If needed you can preprocess the data
        using the optional argument preprocfunc which will be called on the read
        data before loading it into the sequence. The preprocfunc must have the
        following prototype : outdata = preprocfunc(indata). The size 
        verification is performed after the preprocessing (enabling you to
        use zip archives and such).
        """
        # Only for 8 and 32 bit images
        depth = self.getDepth()
        if depth==1:
            mamba.raiseExceptionOnError(mambaCore.ERR_BAD_DEPTH)
            
        # Loading the file
        f = file(path, 'rb')
        data = f.read()
        f.close()
        
        # Preprocessing the data if a function was given
        if preprocfunc:
            data = preprocfunc(data)
        
        # Verification over data size
        (w,h) = self.getSize()
        im_size = w*h*(depth/8)
        assert(len(data)==im_size*self.length)
        
        # Loading the data
        for i,im in enumerate(self.seq):
            err = mambaCore.MB_Load(im.mbIm, data[i*im_size:(i+1)*im_size], im_size)
            mamba.raiseExceptionOnError(err)
        self.name = path
        
    def extractRaw(self):
        """
        Extracts and returns the image raw string data.
        This method only works on 8 and 32-bit images.
        """
        data = ""
        for im in self.seq:
            err,s = mambaCore.MB_Extract(im.mbIm)
            mamba.raiseExceptionOnError(err)
            data += s
        return data
        
    def convert(self, depth):
        """
        Converts the image depth to the given 'depth'.
        The conversion algorithm is identical to the conversion used in the 
        convert3D function (see this function for details).
        """
        for im in self.seq:
            im.convert(depth)
        self.depth = depth
        
        self.mb3DIm = core3D.MB3D_Image(list(map(lambda im: im.mbIm, self.seq)))
        
        if self._displayPjt:
            self._displayPjt.connect(list(map(lambda im: im.mbIm, self.seq)), self.name)
            self._displayPjt.updateim()
        if self._displayUsr:
            self._displayUsr.connect(list(map(lambda im: im.mbIm, self.seq)), self.name)
            self._displayUsr.updateim()
        if self._displayVtk:
            self._displayVtk.connect(list(map(lambda im: im.mbIm, self.seq)), self.name)
            self._displayVtk.updateim()
        
    ### Display methods ########################################################
    def showDisplay(self, type="DEFAULT"):
        """
        Called to show the display associated to the image.
        By default, this will activate the VTK display
        """
        gd = mamba.getDisplayer() # <- trick to ensure the root windows is created and hidden
        if type=="DEFAULT":
            # First if there is any display already opened it is showed
            no_display = True
            if self._displayUsr:
                self._displayUsr.show()
                no_display = False
            if self._displayVtk:
                self._displayVtk.show()
                no_display = False
            if self._displayPjt:
                self._displayPjt.show()
                no_display = False
            
            if no_display:
                # If no display is yet open we create one
                # preferentially using user defines display
                # or if not VTK
                if self._displayerUsr:
                    self._displayUsr = self._displayerUsr(self.name)
                    if self._displayUsr:
                        self._displayUsr.connect(list(map(lambda im: im.mbIm, self.seq)), self.name)
                        self._displayUsr.updateim()
                else:
                    self._displayVtk = self._displayerVtk(self.name)
                    if self._displayVtk:
                        self._displayVtk.connect(list(map(lambda im: im.mbIm, self.seq)), self.name)
                        self._displayVtk.updateim()
                
        elif type=="USER":
            if self._displayerUsr:
                if self._displayUsr:
                    self._displayUsr.show()
                else:
                    self._displayUsr = self._displayerUsr(self.name)
                    if self._displayUsr:
                        self._displayUsr.connect(list(map(lambda im: im.mbIm, self.seq)), self.name)
                        self._displayUsr.updateim()
                        
        elif type=="PROJECTION":
            if self._displayerPjt:
                if self._displayPjt:
                    self._displayPjt.show()
                else:
                    self._displayPjt = self._displayerPjt(self.name)
                    if self._displayPjt:
                        self._displayPjt.connect(list(map(lambda im: im.mbIm, self.seq)), self.name)
                        self._displayPjt.updateim()
                        
        elif type=="VTK":
            if self._displayerVtk:
                if self._displayVtk:
                    self._displayVtk.show()
                else:
                    self._displayVtk = self._displayerVtk(self.name)
                    if self._displayVtk:
                        self._displayVtk.connect(list(map(lambda im: im.mbIm, self.seq)), self.name)
                        self._displayVtk.updateim()

    def hideDisplay(self):
        """
        Called to hide the display associated to the image.
        """
        if self._displayPjt:
            self._displayPjt.hide()
        if self._displayUsr:
            self._displayUsr.hide()
        if self._displayVtk:
            self._displayVtk.hide()


    def updateDisplay(self):
        """
        Called when the display associated to the image must be updated 
        (Contrary to mamba, display is not automatically udpated after any
        operation on your image due to performances).
        You can update the display by hitting key F5 in the display window.
        """
        if self._displayPjt:
            self._displayPjt.updateim()
        if self._displayUsr:
            self._displayUsr.updateim()
        if self._displayVtk:
            self._displayVtk.updateim()
            
    def setPalette(self, pal):
        """
        Defines the palette used to convert the image in color for display.
        'pal' may be mamba.rainbow, mamba.inverted_rainbow, mamba.patchwork or
        any user-defined palette.
        """
        if self._displayPjt:
            self._displayPjt.setColorPalette(pal)
        if self._displayUsr:
            self._displayUsr.setColorPalette(pal)
        if self._displayVtk:
            self._displayVtk.setColorPalette(pal)
            
    def resetPalette(self):
        """
        Undefines the palette used to convert the image in color for display.
        The greyscale palette will be used then.
        """
        pal = (0,0,0)
        for i in range(1,256):
            pal += (i,i,i)
        if self._displayPjt:
            self._displayPjt.setColorPalette(pal)
        if self._displayUsr:
            self._displayUsr.setColorPalette(pal)
        if self._displayVtk:
            self._displayVtk.setColorPalette(pal)
            
    def setOpacity(self, opa):
        """
        Defines the opacity palette used for the volume rendering display.
        'opa' is a tuple holding 256 value between 0 and 255. a 0
        indicates that the corresponding value will be transparent and 255
        indicates that the value will block light.
        """
        if self._displayPjt:
            self._displayPjt.setOpacityPalette(opa)
        if self._displayUsr:
            self._displayUsr.setOpacityPalette(opa)
        if self._displayVtk:
            self._displayVtk.setOpacityPalette(opa)
            
    def resetOpacity(self):
        """
        Resets the opacity palette to its default value.
        """
        opa = (0,)
        for i in range(1,256):
            opa += (i,)
        if self._displayPjt:
            self._displayPjt.setOpacityPalette(opa)
        if self._displayUsr:
            self._displayUsr.setOpacityPalette(opa)
        if self._displayVtk:
            self._displayVtk.setOpacityPalette(opa)

    ### Pixel manipulations ####################################################
    def getPixel(self, position):
        """
        Gets the pixel value at 'position'.
        'position' is a tuple holding (x,y,z).
        Returns the value of the pixel.
        """
        (x,y,z) = position
        if z<0 or z>=self.length:
            mamba.raiseExceptionOnError(mambaCore.ERR_BAD_SIZE)
        err, value = mambaCore.MB_GetPixel(self.seq[z].mbIm, x, y)
        mamba.raiseExceptionOnError(err)
        return value
        
    def setPixel(self, value, position):
        """
        Sets the pixel at 'position' with 'value'.
        'position' is a tuple holding (x,y,z).
        """
        (x,y,z) = position
        if z<0 or z>=self.length:
            mamba.raiseExceptionOnError(mambaCore.ERR_BAD_SIZE)
        err = mambaCore.MB_PutPixel(self.seq[z].mbIm, value, position[0], position[1])
        mamba.raiseExceptionOnError(err)

################################################################################
# ERROR HANDLING
################################################################################
_conv3DErrDict = {
    core3D.NO_ERR : mambaCore.NO_ERR,
    core3D.ERR_BAD_SIZE : mambaCore.ERR_BAD_SIZE,
    core3D.ERR_BAD_DEPTH : mambaCore.ERR_BAD_DEPTH,
    core3D.ERR_BAD_PARAMETER : mambaCore.ERR_BAD_PARAMETER,
    core3D.ERR_BAD_VALUE : mambaCore.ERR_BAD_VALUE,
    core3D.ERR_CANT_ALLOCATE_MEMORY : mambaCore.ERR_CANT_ALLOCATE_MEMORY
}
def convert3DErrorToMamba(err):
    global _conv3DErrDict
    try:
        mambaErr = _conv3DErrDict[err]
    except KeyError:
        mambaErr = mambaCore.ERR_UNKNOWN
    return mambaErr

