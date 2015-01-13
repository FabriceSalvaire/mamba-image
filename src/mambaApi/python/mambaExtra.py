"""
This module defines specific functions and classes which can be considered
as extras for the Mamba image library. They provide optional display methods,
interactive tools and bridges for exchanging images between the Mamba and
PIL libraries.
"""

from __future__ import division
import six

import mambaCore
import mambaUtils as mbUtls
import mambaComposed as mC
import mamba
import mambaDraw

try:
    if six.PY3:
        import tkinter as tk
        import tkinter.filedialog as tkFileDialog
    else:
        import Tkinter as tk
        import tkFileDialog
except ImportError:
    print ("Missing Tkinter library")
    raise
try:
    import ImageTk
    import Image
    import ImageDraw
except ImportError:
    try:
        from PIL import ImageTk
        from PIL import Image
        from PIL import ImageDraw
    except ImportError:
        print ("Missing PIL or PILLOW libraries - See MAMBA User Manual")
        raise
    

###############################################################################
#  Definitions
_icon_size = (64, 64)
_resize_process = Image.NEAREST

_MAXH = 400
_MAXW = 400
_MINH = 200
_MINW = 200

################################################################################
# Dynamic threshold
################################################################################
# This display opens a window in which the image can be thresholded dynamically
# using the keyboard.

class _imageThreshold(tk.Toplevel):

    # Constructor ##############################################################
    def __init__(self, mbIm):
        tk.Toplevel.__init__(self, None)
        self.mbIm = mbIm
        self.mbImThresh = mbUtls.create(self.mbIm.width,self.mbIm.height,1)
        self.body()
        self.grab_set()
        self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.initial_focus.focus_set()
        
        # Events bindings
        self.canvas.bind("<Motion>", self.mouseMotionEvent)
        self.canvas.bind("<Configure>", self.resizeEvent)
        self.canvas.bind("<Button-4>", self.mouseEvent)
        self.canvas.bind("<Button-5>", self.mouseEvent)
        self.bind("<MouseWheel>", self.mouseEvent)
        self.canvas.bind("<Button-1>", self.mouseEvent)
        self.canvas.bind("<ButtonRelease-1>", self.mouseEvent)
        self.bind("<KeyPress>", self.keyboardEvent)
        
        self.wait_window(self)

    def body(self):
        # Size of the image, canvas and display.
        self.osize = [self.mbIm.width,self.mbIm.height]
        imsize = self.osize[:]
        self.zoom = 1.0
        while  imsize < [_MINW, _MINH]:
            imsize[0] = imsize[0]*2
            imsize[1] = imsize[1]*2
            self.zoom = self.zoom*2
        while imsize > [_MAXW, _MAXH]:
            imsize[0] = imsize[0]//2
            imsize[1] = imsize[1]//2
            self.zoom = self.zoom/2
        
        self.title('thresholder - %d%%' % (int(self.zoom*100)))
        self.csize = imsize[:]
        self.dsize = imsize[:]
        self.imid = None
        self.mouse_x = 0
        self.mouse_y = 0
        self.computeThresholdLimits()
        
        # Resize configuration
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Threshold infos
        self.thresholdInfos = tk.StringVar(self)
        lab = tk.Label(self, anchor=tk.W, textvariable=self.thresholdInfos)
        lab.grid(row=0, column=0, columnspan=2, sticky=tk.E+tk.W)
        self.thresholdInfos.set("threshold - low : "+str(self.low)+" - high : "+str(self.high))
        # Image display
        self.canvas_vb = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.canvas_vb.grid(row=1, column=1, sticky=tk.N+tk.S)
        self.canvas_hb = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.canvas_hb.grid(row=2, column=0, sticky=tk.E+tk.W)
        self.canvas = tk.Canvas(self,
                                bd=0,
                                xscrollcommand=self.canvas_hb.set,
                                yscrollcommand=self.canvas_vb.set)
        self.canvas_hb.config(command=self.canvas.xview)
        self.canvas_vb.config(command=self.canvas.yview)
        self.canvas.grid(row=1, column=0, sticky=tk.E+tk.W+tk.S+tk.N)
        self.canvas_hb.grid_remove()
        self.canvas_vb.grid_remove()        
        self.canvas.config(width=imsize[0],height=imsize[1],
                           scrollregion=(0,0,imsize[0]-1,imsize[1]-1))
        # Statusbar
        statusbar = tk.Frame(self)
        statusbar.columnconfigure(1, weight=1)
        statusbar.grid(row=3, column=0, columnspan=2, sticky=tk.E+tk.W)
        self.bclose = tk.Button(statusbar, text="close", command=self.close)
        self.bclose.grid(row=0, column=0, sticky=tk.W)
        self.bsave = tk.Button(statusbar, text="save", command=self.saveImage)
        self.bsave.grid(row=0, column=1, sticky=tk.W)
        self.infos= tk.StringVar(self)
        lab = tk.Label(statusbar, anchor=tk.W, textvariable=self.infos)
        lab.grid(row=0, column=2, sticky=tk.E+tk.W)

        self.updateim()
        
    def computeThresholdLimits(self):
        if self.mbIm.depth==8:
            self.low = 0
            self.lowlim = 0
            self.high = 255
            self.highlim = 255
        elif self.mbIm.depth==32:
            self.low = 0
            self.lowlim = 0
            self.high = 0xffffffff
            self.highlim = 0xffffffff
    
    # Events handling functions ################################################
        
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
        
    def keyboardEvent(self, event):
        # Handles keyboard events
        
        #zoom
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
                
        # threshold change
        elif event.char == "q":
            self.low = min(self.low+1, self.high)
            self.thresholdInfos.set("threshold - low : "+str(self.low)+" - high : "+str(self.high))
            self.updateim()
        elif event.char == "w":
            self.low = max(self.low-1, self.lowlim)
            self.thresholdInfos.set("threshold - low : "+str(self.low)+" - high : "+str(self.high))
            self.updateim()
        elif event.char == "s":
            self.high = min(self.high+1, self.highlim)
            self.thresholdInfos.set("threshold - low : "+str(self.low)+" - high : "+str(self.high))
            self.updateim()
        elif event.char == "x":
            self.high = max(self.high-1, self.low)
            self.thresholdInfos.set("threshold - low : "+str(self.low)+" - high : "+str(self.high))
            self.updateim()
    
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
                for i in range(abs(event.delta)//120):
                    if self.zoom<=0.25:
                        self.setZoom(self.zoom*2)
                    else:
                        self.setZoom(self.zoom+0.25)
            else:
                # ZOOM OUT
                for i in range(abs(event.delta)//120):
                    if self.zoom<=0.25:
                        zoom = self.zoom/2
                        if not (int(self.zoom*self.osize[0])<10 or int(self.zoom*self.osize[0])<10):
                            self.setZoom(zoom)
                    else:
                        self.setZoom(self.zoom-0.25)
            
    def mouseMotionEvent(self, event):
        # Indicates the position of the mouse inside the image.
        x = self.canvas.canvasx(event.x) - max((self.csize[0]-self.dsize[0])//2,0)
        y = self.canvas.canvasy(event.y) - max((self.csize[1]-self.dsize[1])//2,0)
        
        x = max(min(x,self.dsize[0]-1), 0)
        y = max(min(y,self.dsize[1]-1), 0)
        x = int((float(x)/self.dsize[0])*self.osize[0])
        y = int((float(y)/self.dsize[1])*self.osize[1])
        err, v1 = mambaCore.MB_GetPixel(self.mbIm, x, y)
        err, vt = mambaCore.MB_GetPixel(self.mbImThresh, x, y)
        vt = bool(vt)
        self.infos.set("At ("+str(x)+","+str(y)+") = ["+str(v1)+","+str(vt)+"]")
        
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
        
    # Helper functions #########################################################
    
    def setZoom(self, zoom):
        # Sets the zoom value and changes the display accordingly.
        oz = self.zoom
        self.zoom = zoom
        self.dsize[0] = int(self.zoom*self.osize[0])
        self.dsize[1] = int(self.zoom*self.osize[1])
        self.canvas.config(scrollregion=(0,0,self.dsize[0]-1,self.dsize[1]-1))
        self.drawImage()
        self.title('thresholder - %d%%' % (int(self.zoom*100)))
        
        # For a zoom of only one, the scrollbar is removed.
        if self.dsize[0] <= self.csize[0]:
            self.canvas_hb.grid_remove()
        else:
            self.canvas_hb.grid()
        if self.dsize[1] <= self.csize[1]:
            self.canvas_vb.grid_remove()
        else:
            self.canvas_vb.grid()
            
    def updateim(self):
        # Updates the display with the new contents of the mamba image.
        
        err = mambaCore.MB_Thresh(self.mbIm, self.mbImThresh, self.low, self.high)
        self.pilImage = mbUtls.convertToPILFormat(self.mbImThresh)
        self.icon = ImageTk.PhotoImage(self.pilImage.resize(_icon_size, _resize_process))
        self.tk.call('wm','iconphoto', self._w, self.icon)
        self.drawImage()
        
    def drawImage(self):
        # Draws the image inside the canvas.
        self.tkpi = ImageTk.PhotoImage(self.pilImage.resize(self.dsize))
        if self.imid:
            self.canvas.delete(self.imid)
        self.imid = self.canvas.create_image(max((self.csize[0]-self.dsize[0])//2, 0),
                                             max((self.csize[1]-self.dsize[1])//2, 0),
                                             anchor=tk.NW,
                                             image=self.tkpi)
        self.update()
        
    def saveImage(self):
        # Save the displayed image in a specified location
        import tkFileDialog
        filetypes=[("JPEG", "*.jpg"),("PNG", "*.png"),("all files","*")]
        f_name = tkFileDialog.asksaveasfilename(defaultextension='.jpg', filetypes=filetypes)
        if f_name:
            self.pilImage.convert("RGB").save(f_name)

    def close(self, event=None):
        # Closes the window and sets the result.
        self.withdraw()
        self.update_idletasks()
        self.result = (self.low, self.high)
        self.destroy()

# Caller function
def dynamicThreshold(imIn):
    """
    Opens a separate display in which you can dynamically perform a threshold
    operation over image 'imIn'.
    
    Once the close button is pressed, the result of the dynamic threshold is
    returned. This result is a tuple (low, high) used to obtain the image
    displayed using the threshold operation from mamba.
    
    While the window is opened, you can increase or decrease the low level using
    keys Q and W respectively. The high level is modified by the keys S 
    (increasing) and X (decreasing).
    """
    if imIn.getDepth()==1:
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_DEPTH)
    import mambaDisplay
    mambaDisplay.getDisplayer() # To activate Tk root window and hide it
    im = _imageThreshold(imIn.mbIm)
    return im.result
    
    
################################################################################
# Interactive segment
################################################################################
# This display opens a window in which the image can be segmented interactively
# by the user

class _imageSegment(tk.Toplevel):

    # Constructor ##############################################################
    def __init__(self, imIn, imOut):
        tk.Toplevel.__init__(self, None)
        self.imIn = imIn
        self.imOut = imOut
        self.imWrk = mamba.imageMb(imIn)
        mamba.copy(imIn, self.imWrk)
        self.markers = []
        self.body()
        self.grab_set()
        self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.initial_focus.focus_set()
        
        # Events bindings
        self.canvas.bind("<Motion>", self.mouseMotionEvent)
        self.canvas.bind("<Configure>", self.resizeEvent)
        self.canvas.bind("<Button-4>", self.mouseEvent)
        self.canvas.bind("<Button-5>", self.mouseEvent)
        self.bind("<MouseWheel>", self.mouseEvent)
        self.canvas.bind("<Button-1>", self.mouseEvent)
        self.canvas.bind("<ButtonRelease-1>", self.mouseEvent)
        self.bind("<KeyPress>", self.keyboardEvent)
        self.bind("<Control-KeyPress-z>", self.undoEvent)
        
        self.wait_window(self)

    def body(self):
        # Size of the image, canvas and display.
        self.osize = list(self.imIn.getSize())
        imsize = self.osize[:]
        self.zoom = 1.0
        while  imsize < [_MINW, _MINH]:
            imsize[0] = imsize[0]*2
            imsize[1] = imsize[1]*2
            self.zoom = self.zoom*2
        while imsize > [_MAXW, _MAXH]:
            imsize[0] = imsize[0]//2
            imsize[1] = imsize[1]//2
            self.zoom = self.zoom/2
        
        self.title('interactive segment - %d%%' % (int(self.zoom*100)))
        self.csize = imsize[:]
        self.dsize = imsize[:]
        self.imid = None
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_move = False
        self.palette = ()
        for i in range(254):
            self.palette += (i,i,i)
        self.palette += (0,255,0)
        self.palette += (255,0,0)
        
        # Resize configuration
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # infos
        l = tk.Label(self, text="Press Ctrl-Z to erase last marker (e to erase all)")
        l.grid(row=0, column=0, columnspan=2)
        
        # Image display
        self.canvas_vb = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.canvas_vb.grid(row=1, column=1, sticky=tk.N+tk.S)
        self.canvas_hb = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.canvas_hb.grid(row=2, column=0, sticky=tk.E+tk.W)
        self.canvas = tk.Canvas(self,
                                bd=0,
                                xscrollcommand=self.canvas_hb.set,
                                yscrollcommand=self.canvas_vb.set)
        self.canvas_hb.config(command=self.canvas.xview)
        self.canvas_vb.config(command=self.canvas.yview)
        self.canvas.grid(row=1, column=0, sticky=tk.E+tk.W+tk.S+tk.N)
        self.canvas_hb.grid_remove()
        self.canvas_vb.grid_remove()        
        self.canvas.config(width=imsize[0],height=imsize[1],
                           scrollregion=(0,0,imsize[0]-1,imsize[1]-1))
        # Statusbar
        statusbar = tk.Frame(self)
        statusbar.columnconfigure(1, weight=1)
        statusbar.grid(row=3, column=0, columnspan=2, sticky=tk.E+tk.W)
        self.bclose = tk.Button(statusbar, text="close", command=self.close)
        self.bclose.grid(row=0, column=0, sticky=tk.W)
        self.infos= tk.StringVar(self)
        lab = tk.Label(statusbar, anchor=tk.W, textvariable=self.infos)
        lab.grid(row=0, column=2, sticky=tk.E+tk.W)

        self.updateim()
    
    # Events handling functions ################################################
        
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
            
    def undoEvent(self, event):
        # Called when the user press Ctrl-Z
        # Remove the last marker
        if self.markers:
            self.markers = self.markers[:-1]
            self.updateim()
        
    def keyboardEvent(self, event):
        # Handles keyboard events
        
        #zoom
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
                
        # Marker erase
        elif event.char == "e":
            self.markers = []
            self.updateim()
    
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
                if not self.mouse_move:
                    x = self.canvas.canvasx(event.x) - max((self.csize[0]-self.dsize[0])//2,0)
                    y = self.canvas.canvasy(event.y) - max((self.csize[1]-self.dsize[1])//2,0)
                    if x<self.dsize[0] and x>=0 and y<self.dsize[1] and y>=0:
                        x = int((float(x)/self.dsize[0])*self.osize[0])
                        y = int((float(y)/self.dsize[1])*self.osize[1])
                        if event.state&0x0004==0x0004:
                            # If the ctrl key is hold the point is added
                            # to the previous one to form a line
                            self.markers[-1] += (x,y)
                        else:
                            self.markers.append((x,y))
                        self.updateim()
                self.mouse_move = False
            
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
                for i in range(abs(event.delta)//120):
                    if self.zoom<=0.25:
                        zoom = self.zoom/2
                        if not (int(self.zoom*self.osize[0])<10 or int(self.zoom*self.osize[0])<10):
                            self.setZoom(zoom)
                    else:
                        self.setZoom(self.zoom-0.25)
            
    def mouseMotionEvent(self, event):
        # Indicates the position of the mouse inside the image.
        x = self.canvas.canvasx(event.x) - max((self.csize[0]-self.dsize[0])//2,0)
        y = self.canvas.canvasy(event.y) - max((self.csize[1]-self.dsize[1])//2,0)
        
        x = max(min(x,self.dsize[0]-1), 0)
        y = max(min(y,self.dsize[1]-1), 0)
        x = int((float(x)/self.dsize[0])*self.osize[0])
        y = int((float(y)/self.dsize[1])*self.osize[1])
        v1 = self.imIn.getPixel((x, y))
        self.infos.set("At ("+str(x)+","+str(y)+") = ["+str(v1)+"]")
        
        if event.state&0x0100==0x0100:
            self.mouse_move = True
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
        
    # Helper functions #########################################################
    
    def setZoom(self, zoom):
        # Sets the zoom value and changes the display accordingly.
        oz = self.zoom
        self.zoom = zoom
        self.dsize[0] = int(self.zoom*self.osize[0])
        self.dsize[1] = int(self.zoom*self.osize[1])
        self.canvas.config(scrollregion=(0,0,self.dsize[0]-1,self.dsize[1]-1))
        self.drawImage()
        self.title('interactive segment - %d%%' % (int(self.zoom*100)))
        
        # For a zoom of only one, the scrollbar is removed.
        if self.dsize[0] <= self.csize[0]:
            self.canvas_hb.grid_remove()
        else:
            self.canvas_hb.grid()
        if self.dsize[1] <= self.csize[1]:
            self.canvas_vb.grid_remove()
        else:
            self.canvas_vb.grid()
            
    def updateim(self):
        # Updates the display with the new contents of the mamba image.
        self.imOut.reset()
        if self.markers:
            im1 = mamba.imageMb(self.imIn)
            # Putting the markers
            for i,pixel in enumerate(self.markers):
                if len(pixel)==2:
                    self.imOut.setPixel(i+1, pixel)
                else:
                    for pi in range(0,len(pixel)-2,2):
                        mambaDraw.drawLine(self.imOut, pixel[pi:pi+4], i+1)
            # Computing the gradient
            mC.gradient(self.imIn, im1)
            mamba.watershedSegment(im1, self.imOut)
            mamba.copyBytePlane(self.imOut, 3, self.imWrk)
            mamba.subConst(self.imIn, 2, im1)
            for i,pixel in enumerate(self.markers):
                if len(pixel)==2:
                    im1.setPixel(254, pixel)
                else:
                    for pi in range(0,len(pixel)-2,2):
                        mambaDraw.drawLine(im1, pixel[pi:pi+4], 254)
            mamba.logic(im1, self.imWrk, self.imWrk, "sup")
            self.pilImage = mbUtls.convertToPILFormat(self.imWrk.mbIm, self.palette)
        else:
            mamba.copy(self.imIn, self.imWrk)
            self.pilImage = mbUtls.convertToPILFormat(self.imWrk.mbIm)
        self.icon = ImageTk.PhotoImage(self.pilImage.resize(_icon_size, _resize_process))
        self.tk.call('wm','iconphoto', self._w, self.icon)
        self.drawImage()
        
    def drawImage(self):
        # Draws the image inside the canvas.
        self.tkpi = ImageTk.PhotoImage(self.pilImage.resize(self.dsize))
        if self.imid:
            self.canvas.delete(self.imid)
        self.imid = self.canvas.create_image(max((self.csize[0]-self.dsize[0])//2, 0),
                                             max((self.csize[1]-self.dsize[1])//2, 0),
                                             anchor=tk.NW,
                                             image=self.tkpi)
        self.update()

    def close(self, event=None):
        # Closes the window and sets the result.
        self.withdraw()
        self.update_idletasks()
        self.result = self.markers
        self.destroy()

# Caller function
def interactiveSegment(imIn, imOut):
    """
    Opens an interactive display where you can select the marker and perform
    a segmentation using the watershed algorithm on greyscale image 'imIn'.
    
    Once the close button is pressed, the result of the segmentation is
    returned in 32-bit imgae 'imOut'.
    
    Returns the list of markers selected by the user (list of tuple in 
    the (x,y) format).
    """
    if imIn.getDepth()!=8 or imOut.getDepth()!=32:
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_DEPTH)
    import mambaDisplay
    mambaDisplay.getDisplayer() # To activate Tk root window and hide it
    im = _imageSegment(imIn, imOut)
    imOut.updateDisplay()
    return im.result[:]
    
################################################################################
# Superpose display
################################################################################
# This displays 2 images using imposition techniques

class _imageSuperpose(tk.Toplevel):

    # Constructor ##############################################################
    def __init__(self, Im1, Im2):
        tk.Toplevel.__init__(self, None)
        # im2 is the deepest
        if Im1.getDepth() > Im2.getDepth():
            self.mbIm1 = Im2.mbIm
            self.mbIm2 = Im1.mbIm
            self.name1 = Im2.getName()
            self.name2 = Im1.getName()
        else:
            self.mbIm1 = Im1.mbIm
            self.mbIm2 = Im2.mbIm
            self.name1 = Im1.getName()
            self.name2 = Im2.getName()
        self.mbImOut = mbUtls.create(self.mbIm1.width,self.mbIm1.height,8)
        self.body()
        self.grab_set()
        self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.initial_focus.focus_set()
        
        # Events bindings
        self.canvas.bind("<Motion>", self.mouseMotionEvent)
        self.canvas.bind("<Configure>", self.resizeEvent)
        self.canvas.bind("<Button-4>", self.mouseEvent)
        self.canvas.bind("<Button-5>", self.mouseEvent)
        self.bind("<MouseWheel>", self.mouseEvent)
        self.canvas.bind("<Button-1>", self.mouseEvent)
        self.canvas.bind("<ButtonRelease-1>", self.mouseEvent)
        self.bind("<KeyPress>", self.keyboardEvent)
        for c in self.legendCols:
            c.bind("<Button-1>", self.colorChangeEvent)
        self.wait_window(self)

    def body(self):
        # Size of the image, canvas and display
        self.osize = [self.mbIm1.width,self.mbIm1.height]
        imsize = self.osize[:]
        self.zoom = 1.0
        while  imsize < [_MINW, _MINH]:
            imsize[0] = imsize[0]*2
            imsize[1] = imsize[1]*2
            self.zoom = self.zoom*2
        while imsize > [_MAXW, _MAXH]:
            imsize[0] = imsize[0]//2
            imsize[1] = imsize[1]//2
            self.zoom = self.zoom/2
        self.csize = imsize[:]
        self.dsize = imsize[:]
        self.imid = None
        self.mouse_x = 0
        self.mouse_y = 0
        
        self.title('superposer - %d%%' % (int(self.zoom*100)))
        
        # Resize configuration
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Threshold infos
        self.legendF = tk.Frame(self)
        self.legendF.grid(row=0, column=0, columnspan=2, sticky=tk.E+tk.W)
        self.legendF.columnconfigure(1, weight=1)
        self.legendCols = []

        # Image display
        self.canvas_vb = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.canvas_vb.grid(row=1, column=1, sticky=tk.N+tk.S)
        self.canvas_hb = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.canvas_hb.grid(row=2, column=0, sticky=tk.E+tk.W)
        self.canvas = tk.Canvas(self,
                                bd=0,
                                xscrollcommand=self.canvas_hb.set,
                                yscrollcommand=self.canvas_vb.set)
        self.canvas_hb.config(command=self.canvas.xview)
        self.canvas_vb.config(command=self.canvas.yview)
        self.canvas.grid(row=1, column=0, sticky=tk.E+tk.W+tk.S+tk.N)
        self.canvas_hb.grid_remove()
        self.canvas_vb.grid_remove()        
        self.canvas.config(width=imsize[0],height=imsize[1],
                           scrollregion=(0,0,imsize[0]-1,imsize[1]-1))
        
        # Statusbar
        statusbar = tk.Frame(self)
        statusbar.columnconfigure(1, weight=1)
        statusbar.grid(row=3, column=0, columnspan=2, sticky=tk.E+tk.W)
        self.bclose = tk.Button(statusbar, text="close", command=self.close)
        self.bclose.grid(row=0, column=0, sticky=tk.W)
        self.bsave = tk.Button(statusbar, text="save", command=self.saveImage)
        self.bsave.grid(row=0, column=1, sticky=tk.W)
        self.infos= tk.StringVar(self)
        lab = tk.Label(statusbar, anchor=tk.W, textvariable=self.infos)
        lab.grid(row=0, column=2, sticky=tk.E+tk.W)

        self.updateim()
        
    # Events handling functions ################################################
        
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
        
    def keyboardEvent(self, event):
        # Handles keyboard events.
        
        #zoom
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
                for i in range(abs(event.delta)//120):
                    if self.zoom<=0.25:
                        self.setZoom(self.zoom*2)
                    else:
                        self.setZoom(self.zoom+0.25)
            else:
                # ZOOM OUT
                for i in range(abs(event.delta)//120):
                    if self.zoom<=0.25:
                        zoom = self.zoom/2
                        if not (int(self.zoom*self.osize[0])<10 or int(self.zoom*self.osize[0])<10):
                            self.setZoom(zoom)
                    else:
                        self.setZoom(self.zoom-0.25)
            
    def mouseMotionEvent(self, event):
        # Indicates the mouse position inside the image.
        x = self.canvas.canvasx(event.x) - max((self.csize[0]-self.dsize[0])//2,0)
        y = self.canvas.canvasy(event.y) - max((self.csize[1]-self.dsize[1])//2,0)
        
        x = max(min(x,self.dsize[0]-1), 0)
        y = max(min(y,self.dsize[1]-1), 0)
        x = int((float(x)/self.dsize[0])*self.osize[0])
        y = int((float(y)/self.dsize[1])*self.osize[1])
        err, v1 = mambaCore.MB_GetPixel(self.mbIm1, x, y)
        err, v2 = mambaCore.MB_GetPixel(self.mbIm2, x, y)
        self.infos.set("At ("+str(x)+","+str(y)+") = ["+str(v1)+","+str(v2)+"]")
        
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
        
    def colorChangeEvent(self, event):
        # Color change in the legend
        import tkColorChooser
        new_color = tkColorChooser.askcolor(event.widget.cget("bg"))
        if new_color[0]==None:
            return

        if self.mbIm1.depth==1 and self.mbIm2.depth==1:
            event.widget.config(bg=new_color[1])
            event.widget.color_tuple = new_color[0]
            palette = (0,0,0)
            for c in self.legendCols:
                palette = palette + c.color_tuple
            palette = palette+252*(0,0,0)
        elif self.mbIm1.depth==1 and self.mbIm2.depth==8:
            palette = (0,0,0)
            for i in range(1,255):
                palette = palette+(i,i,i)
            palette = palette+new_color[0]
            event.widget.config(bg=new_color[1])
        else:
            return
        
        self.pilImage = mbUtls.convertToPILFormat(self.mbImOut, palette)
        self.icon = ImageTk.PhotoImage(self.pilImage.resize(_icon_size, _resize_process))
        self.tk.call('wm','iconphoto', self._w, self.icon)
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
        self.title('superposer - %d%%' % (int(self.zoom*100)))
        
        # For a zoom of only one, the scrollbar is removed.
        if self.dsize[0] <= self.csize[0]:
            self.canvas_hb.grid_remove()
        else:
            self.canvas_hb.grid()
        if self.dsize[1] <= self.csize[1]:
            self.canvas_vb.grid_remove()
        else:
            self.canvas_vb.grid()
            
    def updateim(self):
        # Updates the display with the new contents of the mamba image.
        if self.mbIm1.depth==1 and self.mbIm2.depth==1:
            # both images are binary
            err = mambaCore.MB_ConSet(self.mbImOut,0)
            err = mambaCore.MB_Add(self.mbImOut,self.mbIm1,self.mbImOut)
            err = mambaCore.MB_ConMul(self.mbImOut,2,self.mbImOut)
            err = mambaCore.MB_Add(self.mbImOut,self.mbIm2,self.mbImOut)
            palette = (0,0,0, 255,0,0, 0,255,0, 0,0,255)+252*(0,0,0)
            colors = ["#ff0000","#00ff00","#0000ff"]
            texts = ["in image 2 only ("+self.name2+")",
                     "in image 1 only ("+self.name1+")",
                     "in both images ("+self.name1+" and "+self.name2+")"]
            for i in range(3):
                c=tk.Canvas(self.legendF, height=10, width=10, bg=colors[i], bd=2, relief=tk.RIDGE)
                c.grid(row=i, column=0)
                c.color_tuple = palette[i*3+3:i*3+6]
                self.legendCols.append(c)
                l=tk.Label(self.legendF, text=texts[i], anchor=tk.NW)
                l.grid(row=i, column=1, sticky=tk.W+tk.E)
            self.pilImage = mbUtls.convertToPILFormat(self.mbImOut, palette)
            
        elif self.mbIm1.depth==1 and self.mbIm2.depth==8:
            # image 1 is binary, 2 is greyscale
            prov = mbUtls.create(self.mbIm1.width,self.mbIm1.height,8)
            err = mambaCore.MB_Convert(self.mbIm1,self.mbImOut)
            err = mambaCore.MB_ConSub(self.mbIm2,1,prov)
            err = mambaCore.MB_Sup(self.mbImOut,prov,self.mbImOut,)
            palette = (0,0,0)
            for i in range(1,255):
                palette = palette+(i,i,i)
            palette = palette+(255,0,255)
            c=tk.Canvas(self.legendF, height=10, width=10, bg="#808080", bd=2, relief=tk.RIDGE)
            c.grid(row=0, column=0)
            l=tk.Label(self.legendF, text="greyscale image ("+self.name2+")", anchor=tk.NW)
            l.grid(row=0, column=1, sticky=tk.W+tk.E)
            c=tk.Canvas(self.legendF, height=10, width=10, bg="#ff00ff", bd=2, relief=tk.RIDGE)
            c.grid(row=1, column=0)
            self.legendCols.append(c)
            l=tk.Label(self.legendF, text="binary image ("+self.name1+")", anchor=tk.NW)
            l.grid(row=1, column=1, sticky=tk.W+tk.E)
            self.pilImage = mbUtls.convertToPILFormat(self.mbImOut, palette)
            
        elif self.mbIm1.depth==8 and self.mbIm2.depth==8:
            # both images are greyscale
            err = mambaCore.MB_Copy(self.mbIm1,self.mbImOut)
            im1 = mbUtls.convertToPILFormat(self.mbIm1)
            im2 = mbUtls.convertToPILFormat(self.mbIm2)
            self.pilImage = Image.new("RGB", im1.size)
            pix = self.pilImage.load()
            d1 = list(im1.getdata())
            d2 = list(im2.getdata())
            w,h = im1.size
            for i,v1 in enumerate(d1):
                v2 = d2[i]
                if v1[0]<v2[0]:
                    pix[i%w, i//w] = (v1[0], 0, 0)
                elif v1==v2:
                    pix[i%w, i//w] = (0, 0, v1[0])
                else:
                    pix[i%w, i//w] = (0, v1[0], 0)
        
        self.icon = ImageTk.PhotoImage(self.pilImage.resize(_icon_size, _resize_process))
        self.tk.call('wm','iconphoto', self._w, self.icon)
        self.drawImage()
        
    def drawImage(self):
        # Draws the image inside the canvas.
        self.tkpi = ImageTk.PhotoImage(self.pilImage.resize(self.dsize))
        if self.imid:
            self.canvas.delete(self.imid)
        self.imid = self.canvas.create_image(max((self.csize[0]-self.dsize[0])//2, 0),
                                             max((self.csize[1]-self.dsize[1])//2, 0),
                                             anchor=tk.NW,
                                             image=self.tkpi)
        self.update()
        
    def saveImage(self):
        # Save the displayed image in a specified location
        import tkFileDialog
        filetypes=[("JPEG", "*.jpg"),("PNG", "*.png"),("all files","*")]
        f_name = tkFileDialog.asksaveasfilename(defaultextension='.jpg', filetypes=filetypes)
        if f_name:
            self.pilImage.convert("RGB").save(f_name)

    def close(self, event=None):
        # Closes the window and set the result.
        self.withdraw()
        self.update_idletasks()
        self.destroy()

# Caller function
def superpose(imIn1, imIn2):
    """
    Draws images 'imIn1' and 'imIn2' in a common display.
    
    If both images are binary, the display is a combination of their pixel values,
    i.e. black where the pixel is black in both images, blue (default color) if 
    the pixel is set in both images, green (default color) if the pixel is set 
    only in 'imIn1' and red (default color) if it is only set in 'imIn2'.
    
    If one image is greyscale and the other is binary, the binary image is
    redrawn over the greyscale image in purple (default color).
    
    Image superposition is not possible if both images are greyscale.
    
    The default colors can be changed while displaying by clicking the corresponding
    color box in the caption above the display window. A color palette will appear
    where a new color can be selected.
    
    """
    if imIn1.getDepth()==32 or imIn2.getDepth()==32:
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_DEPTH)
    if imIn1.getSize()!=imIn2.getSize():
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_SIZE)
    import mambaDisplay
    mambaDisplay.getDisplayer() # To activate Tk root window and hide it
    im = _imageSuperpose(imIn1, imIn2)
    
def multiSuperpose(imInout, *imIns):
    """
    Superpose multiple binary images ('imIns') to the greyscale image
    'imInout'. The binary images are put above the greyscale. The
    result is meant to be seen with an appropriate color palette.
    """
    imWrk = mamba.imageMb(imInout)
    
    mamba.subConst(imInout, len(imIns), imInout)
    for i,im in enumerate(imIns):
        mamba.convertByMask(im, imWrk, 0, 256-len(imIns)+i)
        mamba.logic(imInout, imWrk, imInout, "sup")
    
################################################################################
# Mix/Split color image 
################################################################################
# Mixes three greyscale images to create a color image (RGB) or split a
# color image (RGB) into its three color channels.

def mix(imInR, imInG, imInB):
    """
    Mixes mamba images 'imInR' (red channel), 'imInG' (green channel) and 
    'imInB' (blue channel) into a color image.
    The function returns a PIL image.
    """
    if imInR.getDepth()!=8 or imInG.getDepth()!=8 or imInB.getDepth()!=8:
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_DEPTH)
    if imInR.getSize()!=imInG.getSize() or imInR.getSize()!=imInB.getSize():
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_SIZE)
    (w,h) = imInR.getSize()
    err, sR = mambaCore.MB_Extract(imInR.mbIm)
    mamba.raiseExceptionOnError(err)
    err, sG = mambaCore.MB_Extract(imInG.mbIm)
    mamba.raiseExceptionOnError(err)
    err, sB = mambaCore.MB_Extract(imInB.mbIm)
    mamba.raiseExceptionOnError(err)
    s = six.b("")
    for i in range(0,h*w,w):
        s = s + sR[i: i+w]
        s = s + sG[i: i+w]
        s = s + sB[i: i+w]
    im = Image.fromstring("RGB", (w,h), s, "raw", "RGB;L", 0 ,1)
    return im

def split(pilimIn, imOutR, imOutG, imOutB):
    """
    Splits a color PIL image 'pilimIn' into its three color channels (Red,
    Green and Blue) and puts the three resulting images into 'imOutR', 'imOutG'
    and 'imOutB' respectively.
    """
    if imOutR.getDepth()!=8 or imOutG.getDepth()!=8 or imOutB.getDepth()!=8:
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_DEPTH)
    if imOutR.getSize()!=imOutG.getSize() or imOutR.getSize()!=imOutB.getSize():
        mamba.raiseExceptionOnError(mambaCore.ERR_BAD_SIZE)
    pilim = pilimIn.convert("RGB")
    (wc,hc) = imOutR.getSize()
    (w,h)= pilim.size
    # Because the images can have a different size, it means that we must
    # force the sizes to fit.
    if (wc!=w) or (hc!=h):
        prov_im = Image.new("RGB", (wc,hc), 0)
        pilim_crop = pilim.crop((0,0,min(wc, w),min(hc, h)))
        prov_im.paste(pilim_crop, (0,0,min(wc, w),min(hc, h)))
        pilim = prov_im
        
    s = pilim.tostring("raw", "RGB;L", 0 ,1)
    sR = six.b("")
    sG = six.b("")
    sB = six.b("")
    for i in range(0,hc):
        sR = sR + s[3*i*wc: (3*i+1)*wc]
        sG = sG + s[(3*i+1)*wc: (3*i+2)*wc]
        sB = sB + s[(3*i+2)*wc: (3*i+3)*wc]
    
    err = mambaCore.MB_Load(imOutR.mbIm,sR,len(sR))
    mamba.raiseExceptionOnError(err)
    imOutR.updateDisplay()
    err = mambaCore.MB_Load(imOutG.mbIm,sG,len(sG))
    mamba.raiseExceptionOnError(err)
    imOutG.updateDisplay()
    err = mambaCore.MB_Load(imOutB.mbIm,sB,len(sB))
    mamba.raiseExceptionOnError(err)
    imOutB.updateDisplay()

################################################################################
# Hit-or-Miss pattern selector
################################################################################
# Helps the user to create patterns for the Hit-or-Miss operator.

class _hitormissPatternSelector(tk.Toplevel):
    _BL = 35
    _DEC = 5
    textStatus = ["Undef", "True", "False"]
    
    def __init__(self, grid):
        tk.Toplevel.__init__(self, None)
        self.title('pattern selector')
        self.resizable(False, False)
        self.grid = grid
        self.gridStatus = 9*[0]
        self.body()
        self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.validate)
        self.initial_focus.focus_set()
        self.canvas.bind("<Button-1>", self.mouseButtonEvent)
        self.wait_window(self)

    def body(self):
        # Resize configuration
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Threshold infos
        self.legendF = tk.Frame(self)
        self.legendF.grid(row=0, column=0, columnspan=2, sticky=tk.E+tk.W)
        self.legendF.columnconfigure(1, weight=1)

        # Image display
        self.canvas = tk.Canvas(self,bd=0)
        self.canvas.grid(row=1, column=0, sticky=tk.E+tk.W+tk.S+tk.N)
        self.canvas.config(width=6*self._BL+2*self._DEC,
                           height=7*self._BL+2*self._DEC,
                           scrollregion=(0,0,6*self._BL+2*self._DEC,7*self._BL+2*self._DEC),
                           bg="white")
        self.drawGrid()
        
        # Statusbar
        statusbar = tk.Frame(self)
        statusbar.columnconfigure(1, weight=1)
        statusbar.grid(row=2, column=0, columnspan=2, sticky=tk.E+tk.W)
        self.bclose = tk.Button(statusbar, text="validate", command=self.validate)
        self.bclose.grid(row=0, column=0, sticky=tk.W)
        
    def drawGrid(self):
        if self.grid==mamba.HEXAGONAL:
            self.drawHexagon("0", self.gridStatus[0], 2*self._BL,2*self._BL)      #0
            self.drawHexagon("1", self.gridStatus[1], 3*self._BL,0)               #1
            self.drawHexagon("2", self.gridStatus[2], 4*self._BL,2*self._BL)      #2
            self.drawHexagon("3", self.gridStatus[3], 3*self._BL,4*self._BL)      #3
            self.drawHexagon("4", self.gridStatus[4], self._BL,4*self._BL)        #4
            self.drawHexagon("5", self.gridStatus[5], 0,2*self._BL)               #5
            self.drawHexagon("6", self.gridStatus[6], self._BL,0)                 #6
        else:
            self.drawSquare("0", self.gridStatus[0], 2*self._BL,2*self._BL)       #0
            self.drawSquare("1", self.gridStatus[1], 2*self._BL,0)                #1
            self.drawSquare("2", self.gridStatus[2], 4*self._BL,0)                #2
            self.drawSquare("3", self.gridStatus[3], 4*self._BL,2*self._BL)       #3
            self.drawSquare("4", self.gridStatus[4], 4*self._BL,4*self._BL)       #4
            self.drawSquare("5", self.gridStatus[5], 2*self._BL,4*self._BL)       #5
            self.drawSquare("6", self.gridStatus[6], 0,4*self._BL)                #6
            self.drawSquare("7", self.gridStatus[7], 0,2*self._BL)                #7
            self.drawSquare("8", self.gridStatus[8], 0,0)                         #8
        
    def drawSquare(self,text,status,x,y):
        x=x+self._DEC
        y=y+self._DEC
        if status==1:
            color = "#80b080"
        elif status==2:
            color = "#b08080"
        else:
            color = ""
        self.canvas.create_rectangle(x,y,
                                     x+2*self._BL,y+2*self._BL,
                                     outline="black",
                                     width=2,
                                     fill=color)
        self.canvas.create_text (x+self._BL,y+self._BL, text=text)
        self.canvas.create_text (x+self._BL,y+1.5*self._BL, text=self.textStatus[status])
        
    def drawHexagon(self,text,status,x,y):
        x=x+self._DEC
        y=y+self._DEC
        if status==1:
            color = "#80b080"
        elif status==2:
            color = "#b08080"
        else:
            color = ""
        self.canvas.create_polygon(x,y+self._BL,
                                   x+self._BL,y,
                                   x+2*self._BL,y+self._BL,
                                   x+2*self._BL,y+2*self._BL,
                                   x+self._BL,y+3*self._BL,
                                   x,y+2*self._BL,
                                   outline="black",
                                   width=2,
                                   fill=color)
        self.canvas.create_text (x+self._BL,y+1.5*self._BL, text=text)
        self.canvas.create_text (x+self._BL,y+2*self._BL, text=self.textStatus[status])
        
    def updateGridStatusHexagonal(self,x,y):
        if x>self._BL and x<3*self._BL and y>abs(x-2*self._BL) and y<(3*self._BL-abs(x-2*self._BL)):
            self.gridStatus[6] = (self.gridStatus[6]+1)%3;
        elif x>3*self._BL and x<5*self._BL and y>abs(x-4*self._BL) and y<(3*self._BL-abs(x-4*self._BL)):
            self.gridStatus[1] = (self.gridStatus[1]+1)%3;
        elif x>0 and x<2*self._BL and y>2*self._BL+abs(x-self._BL) and y<(5*self._BL-abs(x-self._BL)):
            self.gridStatus[5] = (self.gridStatus[5]+1)%3;
        elif x>2*self._BL and x<4*self._BL and y>2*self._BL+abs(x-3*self._BL) and y<(5*self._BL-abs(x-3*self._BL)):
            self.gridStatus[0] = (self.gridStatus[0]+1)%3;
        elif x>4*self._BL and x<6*self._BL and y>2*self._BL+abs(x-5*self._BL) and y<(5*self._BL-abs(x-5*self._BL)):
            self.gridStatus[2] = (self.gridStatus[2]+1)%3;
        elif x>self._BL and x<3*self._BL and y>4*self._BL+abs(x-2*self._BL) and y<(7*self._BL-abs(x-2*self._BL)):
            self.gridStatus[4] = (self.gridStatus[4]+1)%3;
        elif x>3*self._BL and x<5*self._BL and y>4*self._BL+abs(x-4*self._BL) and y<(7*self._BL-abs(x-4*self._BL)):
            self.gridStatus[3] = (self.gridStatus[3]+1)%3;
        
    def updateGridStatusSquare(self,x,y):
        if x>0 and x<2*self._BL and y>0 and y<2*self._BL:
            self.gridStatus[8] = (self.gridStatus[8]+1)%3;
        elif x>2*self._BL and x<4*self._BL and y>0 and y<2*self._BL:
            self.gridStatus[1] = (self.gridStatus[1]+1)%3;
        elif x>4*self._BL and x<6*self._BL and y>0 and y<2*self._BL:
            self.gridStatus[2] = (self.gridStatus[2]+1)%3;
        elif x>0 and x<2*self._BL and y>2*self._BL and y<4*self._BL:
            self.gridStatus[7] = (self.gridStatus[7]+1)%3;
        elif x>2*self._BL and x<4*self._BL and y>2*self._BL and y<4*self._BL:
            self.gridStatus[0] = (self.gridStatus[0]+1)%3;
        elif x>4*self._BL and x<6*self._BL and y>2*self._BL and y<4*self._BL:
            self.gridStatus[3] = (self.gridStatus[3]+1)%3;
        elif x>0 and x<2*self._BL and y>4*self._BL and y<6*self._BL:
            self.gridStatus[6] = (self.gridStatus[6]+1)%3;
        elif x>2*self._BL and x<4*self._BL and y>4*self._BL and y<6*self._BL:
            self.gridStatus[5] = (self.gridStatus[5]+1)%3;
        elif x>4*self._BL and x<6*self._BL and y>4*self._BL and y<6*self._BL:
            self.gridStatus[4] = (self.gridStatus[4]+1)%3;
    
    def mouseButtonEvent(self, event):
        # Indicates the position of the mouse inside the image.
        x = self.canvas.canvasx(event.x)-self._DEC
        y = self.canvas.canvasy(event.y)-self._DEC
        if self.grid==mamba.HEXAGONAL:
            self.updateGridStatusHexagonal(x,y)
        else:
            self.updateGridStatusSquare(x,y)
        for id in self.canvas.find_all():
            self.canvas.delete(id)
        self.drawGrid()
        
    def validate(self, event=None):
        # Closes the window and sets the result.
        self.withdraw()
        self.update_idletasks()
        es0 = 0
        es1 = 0
        for i in range(len(self.gridStatus)):
            if self.gridStatus[i]==1:
                es1 = es1 + pow(2,i)
            elif self.gridStatus[i]==2:
                es0 = es0 + pow(2,i)
        self.result = (es0,es1)
        self.destroy()
        
# Caller function
def hitormissPatternSelector(grid=mamba.DEFAULT_GRID):
    """
    Helps the user to create patterns for the Hit-or-Miss operator defined in 
    the Mamba module.
    
    The function returns inside a tuple the structuring elements 'es0' and 'es1'
    (in that order) used as entry in the hitOrMiss function. 
    
    You can select the desired grid for the pattern selector. If not specified,
    the function will use the grid currently in use.
    
    Example with the hitOrMiss function :
        hitOrMiss(imIn, imOut, *hitormissPatternSelector())
    
    """
    import mambaDisplay
    mambaDisplay.getDisplayer() # To activate Tk root window and hide it
    ps = _hitormissPatternSelector(grid)
    return ps.result
    
################################################################################
# Palette extra functions
################################################################################

def tagOneColorPalette(value, color):
    """
    Creates a palette that tags a specific 'value' inside an image with a given 
    'color', a tuple (red, green, blue), while the rest of the image stays in 
    greyscale.
    """
    pal = ()
    if value<0 or value>255:
        raise ValueError("value must be inside range [0,255] : %d" % (value))
    for i in range(value):
        pal = pal + (i,i,i)
    pal = pal + tuple(color)
    for i in range(value+1,256):
        pal = pal + (i,i,i)
    return pal
    
def changeColorPalette(palette, value, color):
    """
    Modifies the given 'palette' so that the given 'value' is tagged using
    the new color 'color',  a tuple (red, green, blue). The rest of the
    palette is unmodified. Returns the created palette.
    """
    pal = list(palette)
    for i in range(3):
        pal[value*3+i] = color[i]
    return tuple(pal)
    
################################################################################
# PIL conversion functions
################################################################################

def Mamba2PIL(imIn):
    """
    Creates and returns a PIL image using the Mamba image 'imIn'.
    
    If the mamba image uses a palette, it will be integrated inside the PIL
    image.
    """
    return mbUtls.convertToPILFormat(imIn.mbIm, imIn.palette)

def PIL2Mamba(pilim, imOut):
    """
    The PIL image 'pilim' is used to load the Mamba image 'imOut'.
    """
    depth = imOut.getDepth()
    (width, height) = imOut.getSize()
    next_mbIm = mbUtls.loadFromPILFormat(pilim, size=(width,height))
    if depth==1:
        err = mambaCore.MB_Convert(next_mbIm, imOut.mbIm)
        mamba.raiseExceptionOnError(err)
    elif depth==8:
        err = mambaCore.MB_Copy(next_mbIm, imOut.mbIm)
        mamba.raiseExceptionOnError(err)
    else:
        err = mambaCore.MB_CopyBytePlane(next_mbIm, imOut.mbIm, 0)
        mamba.raiseExceptionOnError(err)

    if imOut.displayId != '':
        imOut.gd.reconnectWindow(imOut.displayId, imOut)
