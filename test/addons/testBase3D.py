"""
Test cases for the base class and functions found in the base3D module of
mamba3D package. 

Python classes and functions:
    image3DMb
    convert3DErrorToMamba
"""

from mamba import *
from mambaDraw import *
from mamba3D import *
import unittest
import random
import mambaCore
import mamba3D.mamba3DCore as core3D
import os

class TestBase3D(unittest.TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def testDepthAcceptation(self):
        """Tests that incorrect depth raises an exception"""
        im1 = image3DMb(1)
        self.assertRaises(MambaError,im1.loadRaw,"test.data")
        self.assertRaises(MambaError,im1.extractRaw)
        
    def testSizeCheck(self):
        """Verifies that the functions check the size of the image"""
        im1 = image3DMb()
        (w,h) = im1.getSize()
        l = im1.getLength()
        self.assertRaises(MambaError,im1.setPixel,0,(0,0,-1))
        self.assertRaises(MambaError,im1.setPixel,0,(0,0,l))
        self.assertRaises(MambaError,im1.getPixel,(0,0,-1))
        self.assertRaises(MambaError,im1.getPixel,(0,0,l))
        
    def testImage3DMb(self):
        """Verifies 3D image creation"""
        im1 = image3DMb(128,128,30)
        im2 = image3DMb(64,64,1,1)
        im1.fill(1)
        
        self.assert_(isinstance(im1, image3DMb))
        self.assert_(isinstance(im2, image3DMb))
        self.assert_(im1.getLength()==30)
        self.assert_(im2.getLength()==1)
        self.assert_(im1.getDepth()==8)
        self.assert_(im2.getDepth()==1)
        s = str(im1)
        self.assert_(s!='')
        
    def testImage3DMbPixels(self):
        """Verifies pixel extraction and setting in 3D images"""
        im1 = image3DMb()
        im2 = image3DMb(1)
        (w,h) = im1.getSize()
        l = im1.getLength()
        
        for i in range(100):
            im1.reset()
            im2.reset()
            
            xi = random.randint(0,w-1)
            yi = random.randint(0,h-1)
            zi = random.randint(0,l-1)
            vi = random.randint(0,255)
            
            im1.setPixel(vi, (xi,yi,zi))
            vol = computeVolume3D(im1)
            self.assert_(vol==vi)
            v = im1.getPixel((xi,yi,zi))
            self.assert_(v==vi)
            
            im2.setPixel(1, (xi,yi,zi))
            vol = computeVolume3D(im2)
            self.assert_(vol==1)
            v = im2.getPixel((xi,yi,zi))
            self.assert_(v==1)
            
    def _preprocfunc(self, data):
        return len(data)*"\x22"
            
    def testLoadRaw3D(self):
        """Ensures that the load raw method works correctly in 3D"""
        im8 = image3DMb(64,64,4,8)
        im32 = image3DMb(64,64,4,32)
        f = file("test.dat","w")
        f.write((64*64*4-1)*"\x11")
        f.close()
        self.assertRaises(AssertionError, im8.loadRaw, "test.dat")
        f = file("test.dat","w")
        f.write(64*64*4*"\x11")
        f.close()
        im8.loadRaw("test.dat")
        vol = computeVolume3D(im8)
        self.assert_(vol== 64*64*4*0x11)
        f = file("test.dat","w")
        f.write(64*64*4*"\x12")
        f.close()
        im8.loadRaw("test.dat", preprocfunc=self._preprocfunc)
        vol = computeVolume3D(im8)
        self.assert_(vol== 64*64*4*0x22)
        f = file("test.dat","w")
        f.write((64*64*4-1)*"\x11\x00\x00\x00")
        f.close()
        self.assertRaises(AssertionError, im32.loadRaw, "test.dat")
        f = file("test.dat","w")
        f.write(64*64*4*"\x11\x00\x00\x00")
        f.close()
        im32.loadRaw("test.dat")
        vol = computeVolume3D(im32)
        self.assert_(vol== 64*64*4*0x11, "32: %d,%d" %(vol,128*128*0x11))
        
        os.remove("test.dat")
        
    def testExtractRaw(self):
        """Ensures that the extract raw method works properly in 3D"""
        im8 = image3DMb(64,64,6,8)
        im32 = image3DMb(64,64,6,32)
        im8.fill(0x11)
        rawdata = im8.extractRaw()
        self.assert_(len(rawdata)==64*64*6)
        self.assert_(rawdata==64*64*6*"\x11")
        im32.fill(0x11223344)
        rawdata = im32.extractRaw()
        self.assert_(len(rawdata)==64*64*6*4)
        self.assert_(rawdata==64*64*6*"\x44\x33\x22\x11")
            
    def testImage3DMbConvert(self):
        """Tests the convert method of 3D images"""
        im1 = image3DMb(64,64,64,8,displayer=image3DDisplay)
        im1.showDisplay("VTK")
        im1.showDisplay("PROJECTION")
        im1.showDisplay("USER")
        im2 = image3DMb(64,64,64,1)
        
        self.assert_(im1.getDepth()==8)
        self.assert_(im2.getDepth()==1)
        im1.convert(8)
        im2.convert(1)
        self.assert_(im1.getDepth()==8)
        self.assert_(im2.getDepth()==1)
        im1.convert(1)
        im2.convert(8)
        self.assert_(im1.getDepth()==1)
        self.assert_(im2.getDepth()==8)
        
    def testImage3DMbDisplay(self):
        """Verifies display management in 3D images"""
        opa = range(256)
        im1 = image3DMb(64,64,64)
        im2 = image3DMb(64,64,64)
        im3 = image3DMb(64,64,64)
        im4 = image3DMb(64,64,64,displayer=image3DDisplay)
        im5 = image3DMb(64,64,64,displayer=image3DDisplay)
        
        im1.showDisplay()
        im2.showDisplay("VTK")
        im3.showDisplay("PROJECTION")
        im4.showDisplay("USER")
        im5.showDisplay()
        
        im1.setPalette(rainbow)
        im2.setPalette(rainbow)
        im3.setPalette(rainbow)
        im4.setPalette(rainbow)
        im5.setPalette(rainbow)
        
        im1.resetPalette()
        im2.resetPalette()
        im3.resetPalette()
        im4.resetPalette()
        im5.resetPalette()
        
        im1.setOpacity(opa)
        im2.setOpacity(opa)
        im3.setOpacity(opa)
        im4.setOpacity(opa)
        im5.setOpacity(opa)
        
        im1.resetOpacity()
        im2.resetOpacity()
        im3.resetOpacity()
        im4.resetOpacity()
        im5.resetOpacity()
        
        im1.hideDisplay()
        im2.hideDisplay()
        im3.hideDisplay()
        im4.hideDisplay()
        im5.hideDisplay()
        
        im1.showDisplay()
        im2.showDisplay()
        im3.showDisplay()
        im4.showDisplay()
        im5.showDisplay()
        
        im1.updateDisplay()
        im2.updateDisplay()
        im3.updateDisplay()
        im4.updateDisplay()
        im5.updateDisplay()
        
        im1.hideDisplay()
        im2.hideDisplay()
        im3.hideDisplay()
        im4.hideDisplay()
        im5.hideDisplay()
        
        im1.showDisplay()
        im2.showDisplay("VTK")
        im3.showDisplay("PROJECTION")
        im4.showDisplay("USER")
        im5.showDisplay()
            
    def testConvert3DErrorToMamba(self):
        """Verifies the error conversion mechanism"""
        self.assert_(convert3DErrorToMamba(0)==0)
        self.assert_(convert3DErrorToMamba(core3D.ERR_CANT_ALLOCATE_MEMORY+1)==mambaCore.ERR_UNKNOWN)

def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestBase3D)
    
if __name__ == '__main__':
    unittest.main()
