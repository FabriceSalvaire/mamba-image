"""
Test cases for display front-end fonction and optional user-defined displayer

Python functions and method:
    imageMb.showDisplay
    imageMb.hideDisplay
    imageMb.updateDisplay
    imageMb.freezeDisplay
    imageMb.unfreezeDisplay
    imageMb.setName
    imageMb.setPalette
    imageMb.resetPalette
    tidyDisplays
    setShowImages
    getShowImages
    sequenceMb.showAllImages
    sequenceMb.showImage
    sequenceMb.hideAllImages
    sequenceMb.hideImage
"""

from mamba import *
from mambaComposed import *
import mambaDisplay
import unittest
import random
try:
    import Image
except ImportError:
    from PIL import Image

class testDisplayer(mambaDisplay.mambaDisplayer):

    def __init__(self):
        self.dict_fun = {
            "addWindow" : 0,
            "showWindow" : 0,
            "controlWindow" : 0,
            "updateWindow" : 0,
            "hideWindow" : 0,
            "reconnectWindow" : 0,
            "colorizeWindow" : 0,
            "destroyWindow" : 0,
            "retitleWindow" : 0,
            "tidyWindows" : 0
        }

    def addWindow(self, im):
        self.dict_fun["addWindow"] += 1
        return 'dummy_key'
        
    def showWindow(self, wKey):
        self.dict_fun["showWindow"] += 1
        
    def controlWindow(self, wKey, ctrl):
        self.dict_fun["controlWindow"] += 1
       
    def updateWindow(self, wKey):
        self.dict_fun["updateWindow"] += 1
       
    def hideWindow(self, wKey):
        self.dict_fun["hideWindow"] += 1
       
    def reconnectWindow(self, wKey, im):
        self.dict_fun["reconnectWindow"] += 1
       
    def colorizeWindow(self, wKey, pal=None):
        self.dict_fun["colorizeWindow"] += 1

    def destroyWindow(self, wKey):
        self.dict_fun["destroyWindow"] += 1
       
    def retitleWindow(self, wKey, name):
        self.dict_fun["retitleWindow"] += 1
        
    def tidyWindows(self):
        self.dict_fun["tidyWindows"] += 1
        
    def getStatsOnFun(self, fun):
        return self.dict_fun[fun]
        
    def eraseStatsOnFun(self):
        for k in self.dict_fun.keys():
            self.dict_fun[k] = 0

class TestDisplayFE(unittest.TestCase):

    def setUp(self):
        self.testDisp = testDisplayer()
        
    def tearDown(self):
        del(self.testDisp)
        if getImageCounter()!=0:
            print "ERROR : Mamba image are not all deleted !"
            
    def testShowAndHideDisplay(self):
        """Verifies the activation/deactivation of the display front-end methods"""
        im = imageMb(displayer=self.testDisp)
        
        im.hideDisplay()
        self.assert_(self.testDisp.getStatsOnFun("hideWindow")==0)
        
        im.showDisplay()
        self.assert_(self.testDisp.getStatsOnFun("addWindow")==1)
        self.assert_(self.testDisp.getStatsOnFun("showWindow")==1)
        
        im.hideDisplay()
        self.assert_(self.testDisp.getStatsOnFun("hideWindow")==1, "hideWindow = %d" % (self.testDisp.getStatsOnFun("hideWindow")))
        
        im.showDisplay()
        self.assert_(self.testDisp.getStatsOnFun("addWindow")==1)
        self.assert_(self.testDisp.getStatsOnFun("showWindow")==2)
        
        im2 = imageMb()
        im2.showDisplay()
        del(im2)
        
    def testUpdateDisplay(self):
        """Verifies the display update front-end method"""
        im = imageMb(displayer=self.testDisp)
        
        im.showDisplay()
        self.assert_(self.testDisp.getStatsOnFun("addWindow")==1)
        self.assert_(self.testDisp.getStatsOnFun("showWindow")==1)
        
        self.testDisp.eraseStatsOnFun()
        
        im.updateDisplay()
        self.assert_(self.testDisp.getStatsOnFun("updateWindow")==1)
        
    def testModificationDisplay(self):
        """Verifies that the display is notified of some internal changes"""
        im = imageMb(displayer=self.testDisp)
        (w,h) = im.getSize()
        
        im.showDisplay()
        self.assert_(self.testDisp.getStatsOnFun("addWindow")==1)
        self.assert_(self.testDisp.getStatsOnFun("showWindow")==1)
        
        Image.new("RGB", (w,h), (10,10,10)).save("test.jpg")
        im.load("test.jpg")
        self.assert_(self.testDisp.getStatsOnFun("reconnectWindow")==1)
        os.remove("test.jpg")
        
        im.convert(1)
        self.assert_(self.testDisp.getStatsOnFun("reconnectWindow")==2)
        
    def testFreezeDisplay(self):
        """Verifies the display freeze and unfreeze front-end methods"""
        im = imageMb(displayer=self.testDisp)
        
        im.showDisplay()
        self.assert_(self.testDisp.getStatsOnFun("addWindow")==1)
        self.assert_(self.testDisp.getStatsOnFun("showWindow")==1)
        
        im.freezeDisplay()
        self.assert_(self.testDisp.getStatsOnFun("controlWindow")==1)
        im.unfreezeDisplay()
        self.assert_(self.testDisp.getStatsOnFun("controlWindow")==2)
        
    def testNameDisplay(self):
        """Verifies that display is informed when image name change"""
        im = imageMb(displayer=self.testDisp)
        
        im.setName("test1")
        self.assert_(self.testDisp.getStatsOnFun("retitleWindow")==0)
        
        im.showDisplay()
        self.assert_(self.testDisp.getStatsOnFun("addWindow")==1)
        self.assert_(self.testDisp.getStatsOnFun("showWindow")==1)
        
        im.setName("test1")
        self.assert_(self.testDisp.getStatsOnFun("retitleWindow")==1)
        
    def testPaletteDisplay(self):
        """Verifies that the palette is correctly transmitted to display"""
        im = imageMb(displayer=self.testDisp)
        
        im.setPalette(rainbow)
        self.assert_(self.testDisp.getStatsOnFun("colorizeWindow")==0)
        im.resetPalette()
        self.assert_(self.testDisp.getStatsOnFun("colorizeWindow")==0)
        
        im.showDisplay()
        self.assert_(self.testDisp.getStatsOnFun("addWindow")==1)
        self.assert_(self.testDisp.getStatsOnFun("showWindow")==1)
        
        im.setPalette(rainbow)
        self.assert_(self.testDisp.getStatsOnFun("colorizeWindow")==1)
        im.resetPalette()
        self.assert_(self.testDisp.getStatsOnFun("colorizeWindow")==2)
        
    def testTidyDisplays(self):
        """Verifies that the tidyDisplays function correctly calls the displayer"""
        im = imageMb(displayer=self.testDisp)
        
        im.showDisplay()
        self.assert_(self.testDisp.getStatsOnFun("addWindow")==1)
        self.assert_(self.testDisp.getStatsOnFun("showWindow")==1)
        
        tidyDisplays(displayer=self.testDisp)
        self.assert_(self.testDisp.getStatsOnFun("tidyWindows")==1)
        
        tidyDisplays() # Standard displayer call (no effect on the test displayer
        self.assert_(self.testDisp.getStatsOnFun("tidyWindows")==1)
        
    def testSetShowImages(self):
        """Verifies that the automatic display activation is working"""
        self.assert_(getShowImages()==False)
        
        setShowImages(True)
        self.assert_(getShowImages()==True)
        im1 = imageMb(displayer=self.testDisp)
        self.assert_(self.testDisp.getStatsOnFun("addWindow")==1)
        self.assert_(self.testDisp.getStatsOnFun("showWindow")==1)
        
        self.testDisp.eraseStatsOnFun()
        
        setShowImages(False)
        self.assert_(getShowImages()==False)
        im2 = imageMb(displayer=self.testDisp)
        self.assert_(self.testDisp.getStatsOnFun("addWindow")==0)
        self.assert_(self.testDisp.getStatsOnFun("showWindow")==0)
        
    def testSequenceDisplay(self):
        """Verifies sequence display front-end method"""
        li = random.randint(10,25)
        im = imageMb(displayer=self.testDisp)
        seq = sequenceMb(im, li, displayer=self.testDisp)
        
        seq.showAllImages()
        self.assert_(self.testDisp.getStatsOnFun("addWindow")==li)
        self.assert_(self.testDisp.getStatsOnFun("showWindow")==li)
        
        seq.hideAllImages()
        self.assert_(self.testDisp.getStatsOnFun("hideWindow")==li)
        
        seq.showImage(li/2)
        self.assert_(self.testDisp.getStatsOnFun("showWindow")==li+1)
        
        seq.hideImage(li/2)
        self.assert_(self.testDisp.getStatsOnFun("hideWindow")==li+1)
    
def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestDisplayFE)
    
if __name__ == '__main__':
    unittest.main()
