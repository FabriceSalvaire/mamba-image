"""
Test cases for the image creation
    
Python function:
    imageMb   class constructor
    imageMb.getSize
    imageMb.getDepth
    imageMb.load
    imageMb.save
    imageMb.loadRaw
    imageMb.extractRaw
    
C function:
    MB_Create
    MB_Load
    MB_Extract
"""

from __future__ import division
from mamba import *
import mambaCore
import unittest
try:
    import Image
except ImportError:
    from PIL import Image
import random
import os

class TestCreate(unittest.TestCase):

    def testAcceptedSize(self):
        """Verifies that requests for too large or too small ones are refused"""
        self.assertRaises(MambaError, imageMb, 0,0)
        self.assertRaises(MambaError, imageMb, 0xFFFFFFFF,2)

    def testAcceptedDepth(self):
        """Verifies that request for incorrect depth is refused"""
        for i in range(100):
            if i!=1 and i!=8 and i!=32:
                self.assertRaises(MambaError, imageMb, i)
        im1 = imageMb(128,128,1)
        self.assertRaises(MambaError, im1.extractRaw)
        self.assertRaises(MambaError, im1.loadRaw, "")
        
                
    def testSizeDepthParameters(self):
        """Verifies that the size and depth given are correctly handled"""
        for i in range(100):
            wi = random.randint(1,4000)
            hi = random.randint(1,4000)
            wc = ((wi+63)//64)*64
            hc = ((hi+1)//2)*2
            im1 = imageMb(wi,hi,1)
            im8 = imageMb(wi,hi,8)
            im32 = imageMb(wi,hi,32)
            self.assertTrue(im1.getDepth()==1)
            self.assertTrue(im1.getSize()==(wc,hc), "%s : %d,%d" %(str(im1.getSize()), wc, hc))
            self.assertTrue(im8.getDepth()==8)
            self.assertTrue(im8.getSize()==(wc,hc))
            self.assertTrue(im32.getDepth()==32)
            self.assertTrue(im32.getSize()==(wc,hc))
            
    def testConstructor(self):
        """Verifies that imageMb constructor works correctly"""
        wi = random.randint(1,4000)
        hi = random.randint(1,4000)
        ci = random.randint(0,255)
        wc = ((wi+63)//64)*64
        hc = ((hi+1)//2)*2
        imref = imageMb(wi,hi,1)
        # Creating an image and saving it
        Image.new("RGB", (wi,hi), (ci,ci,ci)).save("test.jpg")
        
        im = imageMb()
        self.assertTrue(im.getDepth()==8)
        self.assertTrue(im.getSize()==(256,256))
        im = imageMb(imref)
        self.assertTrue(im.getDepth()==1)
        self.assertTrue(im.getSize()==(wc,hc))
        im = imageMb(1)
        self.assertTrue(im.getDepth()==1)
        self.assertTrue(im.getSize()==(256,256))
        im = imageMb(8)
        self.assertTrue(im.getDepth()==8)
        self.assertTrue(im.getSize()==(256,256))
        im = imageMb(32)
        self.assertTrue(im.getDepth()==32)
        self.assertTrue(im.getSize()==(256,256))
        im = imageMb("test.jpg")
        self.assertTrue(im.getDepth()==8)
        self.assertTrue(im.getSize()==(wc,hc))
        im = imageMb(imref, 1)
        self.assertTrue(im.getDepth()==1)
        self.assertTrue(im.getSize()==(wc,hc))
        im = imageMb(imref, 8)
        self.assertTrue(im.getDepth()==8)
        self.assertTrue(im.getSize()==(wc,hc))
        im = imageMb(imref, 32)
        self.assertTrue(im.getDepth()==32)
        self.assertTrue(im.getSize()==(wc,hc))
        im = imageMb("test.jpg", 1)
        self.assertTrue(im.getDepth()==1)
        self.assertTrue(im.getSize()==(wc,hc))
        im = imageMb("test.jpg", 8)
        self.assertTrue(im.getDepth()==8)
        self.assertTrue(im.getSize()==(wc,hc))
        im = imageMb("test.jpg", 32)
        self.assertTrue(im.getDepth()==32)
        self.assertTrue(im.getSize()==(wc,hc))
        im = imageMb(wi,hi)
        self.assertTrue(im.getDepth()==8)
        self.assertTrue(im.getSize()==(wc,hc))
        im = imageMb(wi,hi,1)
        self.assertTrue(im.getDepth()==1)
        self.assertTrue(im.getSize()==(wc,hc))
        im = imageMb(wi,hi,8)
        self.assertTrue(im.getDepth()==8)
        self.assertTrue(im.getSize()==(wc,hc))
        im = imageMb(wi,hi,32)
        self.assertTrue(im.getDepth()==32)
        self.assertTrue(im.getSize()==(wc,hc))
        
        os.remove("test.jpg")

    def testLoad(self):
        """Ensures that the load method works properly"""
        for i in range(10):
            wi = random.randint(1,4000)
            hi = random.randint(1,4000)
            ci = random.randint(0,255)
            wc = ((wi+63)//64)*64
            hc = ((hi+1)//2)*2
            # Creating an image and saving it
            Image.new("RGB", (wi,hi), (ci,ci,ci)).save("test.jpg")
            im = imageMb("test.jpg")
            self.assertTrue(im.getSize()==(wc,hc), "%s : %d,%d" %(str(im.getSize()), wc, hc))
            vol = computeVolume(im)
            self.assertTrue(vol==ci*wi*hi)
            os.remove("test.jpg")
            
            ci = random.randint(0,255)
            # Creating an image and saving it
            Image.new("RGB", (wi,hi), (ci,ci,ci)).save("test.jpg")
            im.load("test.jpg")
            vol = computeVolume(im)
            self.assertTrue(vol==ci*wi*hi)
            im1 = imageMb(wi,hi,1)
            im1.load("test.jpg")
            self.assertTrue(im1.getDepth()==1)
            im32 = imageMb(wi,hi,32)
            im32.load("test.jpg")
            vol = computeVolume(im32)
            self.assertTrue(vol==ci*wi*hi)
            os.remove("test.jpg")
            
            del(im)
            
    def testSave(self):
        """Ensures that the save method works properly"""
        for i in range(10):
            wi = random.randint(1,4000)
            hi = random.randint(1,4000)
            wc = ((wi+63)//64)*64
            hc = ((hi+1)//2)*2
            im1 = imageMb(wi,hi,1)
            im8 = imageMb(wi,hi,8)
            im32 = imageMb(wi,hi,32)
            im1.save("test1.jpg")
            os.remove("test1.jpg")
            im8.save("test8.jpg")
            os.remove("test8.jpg")
            im32.save("test32.jpg")
            os.remove("test32.jpg")
            
    def testLoadRaw(self):
        """Ensures that the load raw method works correctly"""
        im8 = imageMb(128,128,8)
        im32 = imageMb(128,128,32)
        rawdata = 128*128*"\x11"
        self.assertRaises(AssertionError, im8.loadRaw, rawdata[1:])
        im8.loadRaw(rawdata)
        vol = computeVolume(im8)
        self.assertTrue(vol==128*128*0x11)
        rawdata = 128*128*"\x11\x00\x00\x00"
        self.assertRaises(AssertionError, im32.loadRaw, rawdata[1:])
        im32.loadRaw(rawdata)
        vol = computeVolume(im32)
        self.assertTrue(vol==128*128*0x11, "32: %d,%d" %(vol,128*128*0x11))
        
    def testExtractRaw(self):
        """Ensures that the extract raw method works properly"""
        im8 = imageMb(128,128,8)
        im32 = imageMb(128,128,32)
        im8.fill(0x11)
        rawdata = im8.extractRaw()
        self.assertTrue(len(rawdata)==128*128)
        self.assertTrue(rawdata==128*128*b"\x11")
        im32.fill(0x11223344)
        rawdata = im32.extractRaw()
        self.assertTrue(len(rawdata)==128*128*4)
        self.assertTrue(rawdata==128*128*b"\x44\x33\x22\x11")
        

def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestCreate)
    
if __name__ == '__main__':
    unittest.main()
