"""
This module provides functions, classes and methods to display mamba images
using the Tkinter library.
"""

import mambaCore
import mambaUtils as mbUtls
from mambaError import raiseExceptionOnError, raiseWarning, MambaError

try:
    import Tkinter as tk
except ImportError:
    print ("Missing Tkinter library")
    raise
try:
    import ImageTk
    import Image
except ImportError:
    try:
        from PIL import ImageTk
        from PIL import Image
    except ImportError:
        print ("Missing PIL or PILLOW libraries - See MAMBA User Manual")
        raise

###############################################################################
#  Local variables and constants

_icon_max_size = 64
_default_resize_process = Image.NEAREST

_MAXW = 400
_MAXH = 400
_MINW = 200
_MINH = 200

###############################################################################
#  Utilities functions
#
# These functions do not perform computations but allow you to load, save or 
# convert mamba image structures easily. They also allow you to set the global
# variables used for computations.
# 
# Some of these functions are made public and some are restrained to this module
# use only (they are encapsulated into easier-to-use functions or methods).
    
    
def _copyFromClipboard(size=None):
    """
    Looks into the clipboard to see if an image is present and extract it if 
    this is the case.
    
    WARNING! Under Linux, this function uses pygtk and gtk ! The function may
    not work to your liking. Under Windows, it uses the ImageGrab module present
    with the PIL distribution.
    
    Returns a mamba image structure or None if no image was found.
    """
    import platform
        
    im = None

    if platform.system()=='Windows':
        # Under Windows
        try:
            import ImageGrab
        except ImportError:
            from PIL import ImageGrab
        # The image is extracted from the clipboard.
        # !! There is a bug in PIL 1.1.6 with the clipboard:
        # !! it is not closed if there is no image in it
        # !! and thus this can have very bad effects on Windows
        # !! copy/paste operations.
        im_clipbd = ImageGrab.grabclipboard()
    
        if im_clipbd!=None:
            im = mbUtls.loadFromPILFormat(im_clipbd, size=size)
    
    return im

###############################################################################
#  Classes
#
# This class is used to create windows for image display.
# The class inherits Tkinter.Toplevel to do so.
# Functions are offered to update, retitle, show or hide the display.
class _imageDisplay(tk.Toplevel):

    # Constructor ##############################################################
    def __init__(self, master, name):
    
        # Window creation
        tk.Toplevel.__init__(self,master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.canvas_vb = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.canvas_vb.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.canvas_hb = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.canvas_hb.grid(row=1, column=0, sticky=tk.E+tk.W)
        self.canvas = tk.Canvas(self,
                                bd=0,
                                xscrollcommand=self.canvas_hb.set,
                                yscrollcommand=self.canvas_vb.set)
        self.canvas_hb.config(command=self.canvas.xview)
        self.canvas_vb.config(command=self.canvas.yview)
        self.canvas.grid(row=0, column=0, sticky=tk.E+tk.W+tk.S+tk.N)
        self.createInfoBar()
        self.canvas_hb.grid_remove()
        self.canvas_vb.grid_remove()
        
        # Internal variables
        self.mbIm = None
        self.pal = None
        self.palactive = True
        self.frozen = False
        self.freezeids = []
        self.name = name
        self.imid = None
        self.mouse_x = 0
        self.mouse_y = 0
        self.std_geometry = ""
        
        # Context menu
        self.createContextMenu()
        
        # Events bindings
        self.canvas.bind("<Motion>", self.mouseMotionEvent)
        self.canvas.bind("<Configure>", self.resizeEvent)
        self.canvas.bind("<Button-3>", self.contextMenuEvent)
        self.canvas.bind("<Button-4>", self.mouseEvent)
        self.canvas.bind("<Button-5>", self.mouseEvent)
        self.bind("<MouseWheel>", self.mouseEvent)
        self.canvas.bind("<Button-1>", self.mouseEvent)
        self.canvas.bind("<ButtonRelease-1>", self.mouseEvent)
        self.bind("<KeyPress>", self.keyboardEvent)
        self.bind("<Control-v>", self.copyEvent)
        self.bind("<Control-f>", self.freezeEvent)
        self.bind("<Control-r>", self.restoreEvent)
        self.bind("<FocusIn>", self.focusEvent)
        
        # Upon creation, the image is automatically withdrawn.
        self.withdraw()
        
    # Sub-creation functions ###################################################
        
    def createContextMenu(self):
        # Creates the contextual menu.
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="save as..", command=self.saveImage)
        self.context_menu.add_command(label="load", command=self.loadImage)
        self.context_menu.add_command(label="paste..", 
                                      command=self.pasteFromClipBoard,
                                      state=tk.DISABLED)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="100%", command=self.resetZoom)
        self.context_menu.add_command(label="200%", command=self.doubleZoom)
        submenu = tk.Menu(self.context_menu, tearoff=0)
        INTERP_PROC = [
            ("NEAREST (fastest)", 1),
            ("BILINEAR", 2),
            ("BICUBIC", 3),
            ("ANTIALIAS (slowest)", 4),
        ]
        self.interp_proc = tk.IntVar()
        self.interp_proc.set(1) 
        for label, val in INTERP_PROC :
            submenu.add_radiobutton(label=label, 
                                    variable=self.interp_proc, 
                                    value=val, 
                                    command=self.changeInterpolation)
        self.context_menu.add_cascade(label="interpolation", menu=submenu)
        self.context_menu.add_separator()
        
    def createInfoBar(self):
        # Creates the info status bar.
        statusbar = tk.Frame(self)
        statusbar.columnconfigure(0, weight=1)
        statusbar.grid(row=2, column=0, columnspan=2, sticky=tk.E+tk.W)
        self.infos = []
        for i in range(3):
            v = tk.StringVar(self)
            tk.Label(statusbar, anchor=tk.W, textvariable=v).grid(row=0, column=i, sticky=tk.E+tk.W)
            self.infos.append(v)
    
    # Events handling functions ################################################
    
    def focusEvent(self, event):
        # The window is activated.
        self.updateim()
        
    def resizeEvent(self, event):
        # Handles the resizing of the display window.
        self.csize = [event.width, event.height]
        self.drawImage()
        
        # For a zoom of only one, the scrollbar is removed.
        if self.dsize[0] <= self.csize[0]:
            self.canvas_hb.grid_remove()
        else:
            self.canvas_hb.grid()
        if self.dsize[1] <= self.csize[1]:
            self.canvas_vb.grid_remove()
        else:
            self.canvas_vb.grid()
        
    def mouseMotionEvent(self, event):
        # Indicates the position of the mouse inside the image.
        # Displays in the info bar the position inside the image along with the
        # pixel value.
        x = self.canvas.canvasx(event.x) - max((self.csize[0]-self.dsize[0])/2,0)
        y = self.canvas.canvasy(event.y) - max((self.csize[1]-self.dsize[1])/2,0)
        x = max(min(x,self.dsize[0]-1), 0)
        y = max(min(y,self.dsize[1]-1), 0)
        if self.mbIm.depth == 32:
            x = int((float(x)/self.dsize[0])*self.osize[0])%(self.osize[0]/2)
            y = int((float(y)/self.dsize[1])*self.osize[1])%(self.osize[1]/2)
            err, v = mambaCore.MB_GetPixel(self.mbIm, x, y)
            raiseExceptionOnError(err)
            v = hex(v)
        else:
            x = int((float(x)/self.dsize[0])*self.osize[0])
            y = int((float(y)/self.dsize[1])*self.osize[1])
            err, v = mambaCore.MB_GetPixel(self.mbIm, x, y)
            raiseExceptionOnError(err)
            v = str(v)
        self.infos[2].set("At ("+str(x)+","+str(y)+") = "+v)
        
        if event.state&0x0100==0x0100 :
            if not self.dsize[0] <= self.csize[0]:
                dx = event.x-self.mouse_x
                posx = self.canvas_hb.get()[0] - float(dx)/self.dsize[0]
                self.canvas.xview_moveto(posx)
            if not self.dsize[1] <= self.csize[1]:
                dy = event.y-self.mouse_y
                posy = self.canvas_vb.get()[0] - float(dy)/self.dsize[1]
                self.canvas.yview_moveto(posy)
            
        self.mouse_x = event.x
        self.mouse_y = event.y
    
    def mouseEvent(self, event):
        # Handles mouse events (except menu pop up)
        # Mainly zoom in or out using the mouse wheel, and moving the image
        if event.type=="4":
            if event.num==1:
                self.canvas.config(cursor="fleur")
            elif event.num==4:
                # Mouse wheel scroll up under linux
                # ZOOM IN
                if self.zoom<=0.25:
                    self.setZoom(self.zoom*2)
                else:
                    self.setZoom(self.zoom+0.25)
            elif event.num==5:
                # Mouse wheel scroll down under linux
                # ZOOM OUT
                if self.zoom<=0.25:
                    zoom = self.zoom/2
                    if not (int(self.zoom*self.osize[0])<10 or int(self.zoom*self.osize[0])<10):
                        self.setZoom(zoom)
                else:
                    self.setZoom(self.zoom-0.25)
            
        elif event.type=="5":
            if event.num==1:
                # Button 1 released
                self.canvas.config(cursor="arrow")
            
        elif event.type=="38":
            # Mouse wheel under windows
            if event.delta>0:
                # ZOOM IN
                for i in range(abs(event.delta)/120):
                    if self.zoom<=0.25:
                        self.setZoom(self.zoom*2)
                    else:
                        self.setZoom(self.zoom+0.25)
            else:
                # ZOOM OUT
                for i in range(abs(event.delta)/120):
                    if self.zoom<=0.25:
                        zoom = self.zoom/2
                        if not (int(self.zoom*self.osize[0])<10 or int(self.zoom*self.osize[0])<10):
                            self.setZoom(zoom)
                    else:
                        self.setZoom(self.zoom-0.25)

    def keyboardEvent(self, event):
        # Handles keyboard events,
        # such as zoom in (z) or out (a), activation of the color palette (p)
        # or restore original size (r).
        xo = max((self.csize[0]-self.dsize[0])/2, 0)
        yo = max((self.csize[1]-self.dsize[1])/2, 0)
        if event.char == "z":
            # ZOOM IN
            if self.zoom<=0.25:
                self.setZoom(self.zoom*2)
            else:
                self.setZoom(self.zoom+0.25)
        elif event.char == "a":
            # ZOOM OUT
            if self.zoom<=0.25:
                zoom = self.zoom/2
                if not (int(self.zoom*self.osize[0])<10 or int(self.zoom*self.osize[0])<10):
                    self.setZoom(zoom)
            else:
                self.setZoom(self.zoom-0.25)
        elif event.char == "p":
            # PALETTE ACTIVATION
            self.palactive = not self.palactive
            self.updateim()
    
    def freezeEvent(self, event):
        # Freeze/Unfreeze event
        if self.frozen:
            self.unfreeze()
        else:
            self.freeze()
    
    def restoreEvent(self, event):
        # Restore original size event
        # The window size and parameter are reset.
        self.canvas_hb.grid_remove()
        self.canvas_vb.grid_remove()
        if self.mbIm.depth==32:
            imsize = [self.osize[0]/2,self.osize[1]/2]
        else:
            imsize = self.osize[:]
        self.zoom = 1.0
        while imsize[0]<_MINW or imsize[1]<_MINH:
            imsize[0] = imsize[0]*2
            imsize[1] = imsize[1]*2
            self.zoom = self.zoom*2
        while imsize[0]>_MAXW or imsize[1]>_MAXH:
            imsize[0] = imsize[0]/2
            imsize[1] = imsize[1]/2
            self.zoom = self.zoom/2
        self.csize = imsize[:]
        self.dsize = imsize[:]
        self.canvas.config(width=imsize[0],height=imsize[1],
                           scrollregion=(0,0,imsize[0]-1,imsize[1]-1))
        if self.mbIm.depth==32:
            self.zoom = self.zoom/2
        self.title((self.frozen and "Frozen - " or "") + self.name + 
                   " - " + str(self.mbIm.depth) + 
                   " - [" + str(int(self.zoom*100)) + "%]")
        self.updateim()
        # Restoring the standard geometry.
        self.geometry(self.std_geometry)
        

    def copyEvent(self, event):
        # Handles copy shortcut event.
        # If an image is present into the clipboard we get it. 
        self._im_to_paste = _copyFromClipboard(size=self.osize)
        if self._im_to_paste and self.mbIm.depth==8:
            self.pasteFromClipBoard()
                             
    def contextMenuEvent(self, event):
        # Draws a contextual menu on a mouse right click.
        # If an image is present into the clipboard,
        # we get it. 
        self._im_to_paste = _copyFromClipboard(size=self.osize)
        
        # If an image was retrieved from the clipboard and the image is not a
        # 32-bit image, the paste menu is enabled.
        if self._im_to_paste and self.mbIm.depth==8:
            self.context_menu.entryconfigure(2, state=tk.ACTIVE)
        else:
            self.context_menu.entryconfigure (2, state=tk.DISABLED)
        
        self.context_menu.post(event.x_root, event.y_root)
        
    # Contextual Menu functions ################################################
    def resetZoom(self):
        self.setZoom(1.0)
    def doubleZoom(self):
        self.setZoom(2.0)
    def loadImage(self):
        # Loads the image from the selected file.
        # The name associated with the image will not be changed.
        import tkFileDialog
        f_name = tkFileDialog.askopenfilename()
        if f_name:
            im = mbUtls.load(f_name, size=(self.mbIm.width,self.mbIm.height))
            if self.mbIm.depth==1:
                err = mambaCore.MB_Convert(im, self.mbIm)
                raiseExceptionOnError(err)
            elif self.mbIm.depth==8:
                err = mambaCore.MB_Copy(im, self.mbIm)
                raiseExceptionOnError(err)
            else:
                err = mambaCore.MB_CopyBytePlane(im, self.mbIm, 0)
                raiseExceptionOnError(err)
            self.updateim()
    def saveImage(self):
        # Saves the image into the selected file.
        import tkFileDialog
        filetypes=[("JPEG", "*.jpg"),("PNG", "*.png"),("all files","*")]
        f_name = tkFileDialog.asksaveasfilename(defaultextension='.jpg', filetypes=filetypes)
        if f_name:
            mbUtls.save(self.mbIm, f_name, self.palactive and self.pal)
    def pasteFromClipBoard(self):
        # Pastes the image obtained in the clipboard.
        err = mambaCore.MB_Copy(self._im_to_paste, self.mbIm)
        raiseExceptionOnError(err)
        self.title((self.frozen and "Frozen - " or "") + self.name + 
                   " - " + str(self.mbIm.depth) + 
                   " - [" + str(int(self.zoom*100)) + "%]")
        self.updateim()
        del(self._im_to_paste)
        self._im_to_paste = None
    def changeInterpolation(self):
        # The interpolation process is changed.
        v = self.interp_proc.get() 
        if v==1:
            self.resize_process = Image.NEAREST
        elif v==2:
            self.resize_process = Image.BILINEAR
        elif v==3:
            self.resize_process = Image.BICUBIC
        elif v==4:
            self.resize_process = Image.ANTIALIAS
        self.drawImage()
        
    # Helper functions #########################################################
    
    def setZoom(self, zoom):
        # Sets the zoom value and changes the display accordingly.
        oz = self.zoom
        self.zoom = zoom
        self.dsize[0] = int(self.zoom*self.osize[0])
        self.dsize[1] = int(self.zoom*self.osize[1])
        self.canvas.config(scrollregion=(0,0,self.dsize[0]-1,self.dsize[1]-1))
        self.drawImage()
        self.title((self.frozen and "Frozen - " or "") + self.name + 
                   " - " + str(self.mbIm.depth) + 
                   " - [" + str(int(self.zoom*100)) + "%]")
        
        # For a zoom of only one, the scrollbar is removed.
        if self.dsize[0] <= self.csize[0]:
            self.canvas_hb.grid_remove()
        else:
            self.canvas_hb.grid()
        if self.dsize[1] <= self.csize[1]:
            self.canvas_vb.grid_remove()
        else:
            self.canvas_vb.grid()
        
    def drawImage(self):
        # Draws the image inside the canvas.
        self.tkpi = ImageTk.PhotoImage(self.pilImage.resize(self.dsize, self.resize_process))
        if self.imid:
            self.canvas.delete(self.imid)
        self.imid = self.canvas.create_image(max((self.csize[0]-self.dsize[0])/2, 0),
                                             max((self.csize[1]-self.dsize[1])/2, 0),
                                             anchor=tk.NW,
                                             image=self.tkpi)
        
    # Public interface functions ###############################################
    
    def freeze(self):
        # freezes the display so that update has no effect
        self.frozen = True
        self.title((self.frozen and "Frozen - " or "") + self.name +
                   " - " + str(self.mbIm.depth) + 
                   " - [" + str(int(self.zoom*100)) + "%]")
    
    def unfreeze(self):
        # Unfreezes the display
        self.frozen = False
        self.title((self.frozen and "Frozen - " or "") + self.name +
                   " - " + str(self.mbIm.depth) + 
                   " - [" + str(int(self.zoom*100)) + "%]")
        self.updateim()
        
    def updateim(self):
        # Updates the display with the new contents of the mamba image.
        if self.mbIm and self.state()=="normal" and not self.frozen:
            self.pilImage = mbUtls.convertToPILFormat(self.mbIm, self.palactive and self.pal)
            err, volume = mambaCore.MB_Volume(self.mbIm)
            self.infos[0].set("volume : "+str(volume))
            self.icon = ImageTk.PhotoImage(self.pilImage.resize(self.icon_size, Image.NEAREST))
            self.tk.call('wm','iconphoto', self._w, self.icon)
            self.drawImage()
        
    def connect(self, im, pal=None):
        # "Connects" the window to a mamba image.
        
        # Size of the image, canvas and display
        self.osize = [im.width, im.height]
        imsize = self.osize[:]
        self.zoom = 1.0
        while imsize[0]<_MINW or imsize[1]<_MINH:
            imsize[0] = imsize[0]*2
            imsize[1] = imsize[1]*2
            self.zoom = self.zoom*2
        while imsize[0]>_MAXW or imsize[1]>_MAXH:
            imsize[0] = imsize[0]/2
            imsize[1] = imsize[1]/2
            self.zoom = self.zoom/2
        self.csize = imsize[:]
        self.dsize = imsize[:]
        self.canvas.config(width=imsize[0],height=imsize[1],
                           scrollregion=(0,0,imsize[0]-1,imsize[1]-1))
        
        # PIL image and icon
        self.resize_process = _default_resize_process
        m = max(self.osize)
        self.icon_size = ((_icon_max_size*self.osize[0])/m,(_icon_max_size*self.osize[1])/m)
        
        # Adding size info to menu.
        size_info = str(self.osize[0]) + " x " + str(self.osize[1])
        self.context_menu.add_command(label=size_info)
        
        self.mbIm = im
        self.pal = pal
        if self.mbIm.depth==32:
            self.osize[0] = self.osize[0]*2
            self.osize[1] = self.osize[1]*2
            self.zoom = self.zoom/2
        self.title((self.frozen and "Frozen - " or "") + self.name + 
                   " - " + str(self.mbIm.depth) + 
                   " - [" + str(int(self.zoom*100)) + "%]")
        self.updateim()
        
    def colorize(self, pal):
        # Changes the color palette associated with the window.
        self.pal = pal
        self.palactive = True
        self.updateim()
        
    def retitle(self, name):
        # Changes the title of the window.
        self.name = name
        self.title((self.frozen and "Frozen - " or "") + self.name + 
                   " - " + str(self.mbIm.depth) + 
                   " - [" + str(int(self.zoom*100)) + "%]")
        self.updateim()
            
    def show(self):
        # Shows the display (enabling update).
        if self.state()!="normal":
            self.deiconify()
            self.updateim()
            
    def hide(self):
        # Hides the display.
        self.withdraw()

# Class created to handle the references to all the display windows. The mamba
# image actually don't use a direct call to the display but uses the Displayer
# class _MbDisplayer: instead.
class mambaDisplayer:
    """
    This generic class is provided to allow advanced users to define their own
    way to display mamba images. To do so, you must create your own displayer
    class inheriting this one. Then create an instance of it and give it as an
    argument of you mamba image like :
    
        im = imageMb(displayer=your_own_displayer_instance)
        
    or you can redefine the getDisplayer function making your displayer the
    default for all the mamba images created after the redefinition.
    
    As an example, you can look into the mambaDisplay.py file to see the 
    standard displayer provided with mamba based on Tkinter.
    """

    def addWindow(self, im):
        """
        Creates a window for mamba image 'im'.
        
        You can access name, palette information and other information related
        to the mamba image object.
        
        The low level structure is accessible inside the mamba image class
        through attribute mbIm. It is useful to work with low-level mambaCore
        functions (direct access to C level functions) and more particularly
        to obtain the data inside the images in a raw string (see MB_Extract).
        
        The function must return the id of the window (also called its key) 
        that the mamba image (imageMb) will store for later interaction with 
        the display. If an error occurred, returns an empty string.
        """
        return ''
        
    def showWindow(self, wKey):
        """
        Method used to recall and redisplay a window that has been hidden,
        iconified or withdrawn from the screen. 'wKey' indicates the particular
        window to redisplay.
        
        The function is also called right after the creation of the window. It 
        can be called even if the window was not hidden, iconified or withdrawn.
        """
        pass
        
    def controlWindow(self, wKey, ctrl):
        """
        Method used to control the display of a window identified by 'wKey'. The
        'ctrl' parameter indicates the type of operation to perform. Here are 
        the value the displayer must support :
            - "FREEZE"   : freeze the display so that update will no longer be 
                           possible until the window is unfreezed.
            - "UNFREEZE" : unfreeze the display and automatically update it.
        
        Other controls must be ignored quietly.
        """
        pass
       
    def updateWindow(self, wKey):
        """
        If an event occurred that modified the mamba image associated to window
        'wKey', this method will be called.
        
        For optimization sake, it is advised to disregard calls to this function
        when the concerned window is hidden.
        """
        pass
       
    def hideWindow(self, wKey):
        """
        Method used to hide a window from the screen. 'wKey' indicates the 
        particular window to withdraw.
        
        The function can be called even if the window is already hidden, 
        iconified or withdrawn.
        """
        pass
       
    def reconnectWindow(self, wKey, im):
        """
        Reconnects the window identified by 'wKey' with image 'im'.
        
        This event may happen if the internal reference of the image given
        to addWindow upon creation of window 'wKey' changed, making the stored
        one in the displayer obsolete. This is the case when the image is 
        converted or when a load occurred.
        """
        pass
       
    def colorizeWindow(self, wKey, pal=None):
        """
        A change of color palette occurred in the image associated with window
        'wKey'. The new palette is given by 'pal'. If not given, the image must 
        be displayed in greyscale.
        """
        pass

    def destroyWindow(self, wKey):
        """
        Destroys the window identified by 'wKey'.
        """
        pass
       
    def retitleWindow(self, wKey, name):
        """
        Changes the 'name' of the window identified by 'wKey'.
        """
        pass
        
    def tidyWindows(self):
        """
        Tidies the display to ensure that all the windows are visible.
        
        In particular, this method is called by the mamba tidyDisplays()
        function.
        """
        pass

# Real displayer (inherits from the generic displayer)
class _MbDisplayer(mambaDisplayer):
    
    def __init__(self):
        self.windows = {}
        self.root = tk.Tk()
        self.root.withdraw()
        self.screen_size = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        # mainloop hack
        self.root.mainloop = self._dummy_mainloop
        tk.mainloop = self._dummy_mainloop
        
    def _dummy_mainloop(self, n=0):
        # Dummy mainloop to replace the mainloop that must not be called
        pass
    
    def addWindow(self, im=None):
        # Creates a window for image 'im'.
        # Returns the id of the window (its key).
        imd = _imageDisplay(self.root, im.name)
        imd.protocol("WM_DELETE_WINDOW", imd.withdraw)
        self.windows[str(imd)] = imd
        imd.connect(im.mbIm, im.palette)
        return str(imd)[:]
        
    def showWindow(self, wKey):
        # Displays the window identified by 'key'.
        self.windows[wKey].show()
        self.root.update()
        # Storing the standard geometry.
        if not self.windows[wKey].std_geometry:
            geo = self.windows[wKey].geometry()
            geo = geo.split("-")[0].split("+")[0]
            self.windows[wKey].std_geometry = geo
        
    def controlWindow(self, wKey, ctrl):
        # Controls the window
        if ctrl=="FREEZE":
            self.windows[wKey].freeze()
        elif ctrl=="UNFREEZE":
            self.windows[wKey].unfreeze()
        self.root.update()
       
    def updateWindow(self, wKey):
        # Updates the window identified by 'key'.
        self.windows[wKey].updateim()
        self.root.update()
       
    def hideWindow(self, wKey):
        # Hides the window identified by 'key'.
        self.windows[wKey].hide()
        self.root.update()
       
    def reconnectWindow(self, wKey, im):
        # Reconnects the window identified by 'key' with image 'im' using
        # palette 'pal' if specified.
        self.windows[wKey].connect(im.mbIm, im.palette)
        self.root.update()
       
    def colorizeWindow(self, wKey, pal=None):
        # Colorizes (applies palette 'pal' to) the window identified by 'key'.
        # If 'pal' is not specified then uncolorize.
        self.windows[wKey].colorize(pal)
        self.root.update()

    def destroyWindow(self, wKey):
        # Destroys the window identified by 'key'.
        self.windows[wKey].destroy()
        del(self.windows[wKey].mbIm)
        del(self.windows[wKey])
       
    def retitleWindow(self, wKey, name):
        # Changes the 'name' of the window identified by 'key'.
        self.windows[wKey].retitle(name)
        self.root.update()
        
    def tidyWindows(self):
        # Tidies the display to ensure that all the windows are visible.
        x = self.screen_size[0]/20
        y = (19*self.screen_size[1])/20
        maxw = 0
#        wkeys = self.windows.keys()
#        wkeys.sort()
#        for wKey in wkeys:
        for toplvlw in self.root.winfo_children():
            if isinstance(toplvlw, tk.Toplevel):
                geo = toplvlw.geometry()
                geo = geo.split("-")[0].split("+")[0]
                l = geo.split("x")
                w = int(l[0])+5
                h = int(l[1])+30 # for window decoration
                if y-h<(self.screen_size[1]/20):
                    x = x + maxw
                    if x>(19*self.screen_size[0])/20:
                        x = self.screen_size[0]/20
                    y = (19*self.screen_size[1])/20
                    maxw = 0
                    y = y - h
                    geo = geo+"+"+str(x)+"+"+str(y)
                else:
                    y = y - h
                    geo = geo+"+"+str(x)+"+"+str(y)
                toplvlw.geometry(geo)
                if w>maxw:
                    maxw=w

_global_displayer = None

###############################################################################
#  Functions for image display management and handling

def getDisplayer():
    """
    Returns the reference to the displayer used by mamba images when they need to
    be displayed.
    """
    global _global_displayer
    if not _global_displayer:
        _global_displayer = _MbDisplayer()
    return _global_displayer
    
def setMaxDisplay(size):
    """
    Set the maximum 'size' (tuple with w and h) above which the image
    is automatically downsized upon displaying.
    """
    global _MAXH, _MAXW
    
    _MAXW = size[0]
    _MAXH = size[1]
    
def setMinDisplay(size):
    """
    Set the minimum 'size' (tuple with w and h) below which the image
    is automatically upsized upon displaying.
    """
    global _MINW, _MINH
    
    _MINW = size[0]
    _MINH = size[1]

