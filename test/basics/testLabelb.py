"""
Test cases for the image labelling function.

The function only works with binary image as input and 32-bit image as output.

For every set of pixels in the input image (pixels set to True that are 
connected), the output image is computed to give the entire pixels set a value
(its label) that is unique inside the image.

The result depends on grid and edge configurations.

Python function:
    label
    
C functions:
    MB_Labelb

Test cases for the MB_Labelb function
"""

from __future__ import division
from mamba import *
import unittest

class TestLabelb(unittest.TestCase):

    def setUp(self):
        # Creating two images for each possible depth
        self.im1_1 = imageMb(1)
        self.im1_2 = imageMb(1)
        self.im1_3 = imageMb(1)
        self.im8_1 = imageMb(8)
        self.im8_2 = imageMb(8)
        self.im32_1 = imageMb(32)
        self.im32_2 = imageMb(32)
        self.im32_3 = imageMb(32)
        self.im1s2_1 = imageMb(128,128,1)
        self.im32s2_1 = imageMb(128,128,32)
        
    def tearDown(self):
        del(self.im1_1)
        del(self.im1_2)
        del(self.im1_3)
        del(self.im8_1)
        del(self.im8_2)
        del(self.im32_1)
        del(self.im32_2)
        del(self.im32_3)
        del(self.im1s2_1)
        del(self.im32s2_1)
        if getImageCounter()!=0:
            print("ERROR : Mamba image are not all deleted !")

    def testDepthAcceptation(self):
        """Tests that incorrect depth raises an exception"""
        self.assertRaises(MambaError, label, self.im1_1, self.im1_2)
        self.assertRaises(MambaError, label, self.im1_1, self.im8_2)
        #self.assertRaises(MambaError, label, self.im1_1, self.im32_2)
        self.assertRaises(MambaError, label, self.im8_1, self.im1_2)
        self.assertRaises(MambaError, label, self.im8_1, self.im8_2)
        self.assertRaises(MambaError, label, self.im8_1, self.im32_2)
        self.assertRaises(MambaError, label, self.im32_1, self.im1_2)
        self.assertRaises(MambaError, label, self.im32_1, self.im8_2)
        self.assertRaises(MambaError, label, self.im32_1, self.im32_2)

    def testSizeCheck(self):
        """Tests that different sizes raise an exception"""
        self.assertRaises(MambaError, label, self.im1s2_1, self.im32_1)
        self.assertRaises(MambaError, label, self.im1_1, self.im32s2_1)
        
    def testParameterRange(self):
        """Verifies that an incorrect parameter raises an exception"""
        for i in range(257, 1000):
            self.assertRaises(MambaError, label, self.im32_1, self.im1_2, 0, i)
        self.assertRaises(MambaError, label, self.im32_1, self.im1_2, 255, 254)

    def testComputationUniqueLabel(self):
        """Labelling only one complex object"""
        (w,h) = self.im1_1.getSize()
        
        self.im1_1.reset()
        
        for x in range(1,w-3,4):
            for hi in range(1,h-1):
                self.im1_1.setPixel(1, (x, hi))
            self.im1_1.setPixel(1, (x+1, hi))
            for hi in range(h-2,0,-1):
                self.im1_1.setPixel(1, (x+2, hi))
            self.im1_1.setPixel(1, (x+3, 1))
        
        n = label(self.im1_1, self.im32_1, grid=SQUARE)
        self.assertTrue(n==1)
        
        n = label(self.im1_1, self.im32_1, grid=HEXAGONAL)
        self.assertTrue(n==1)

    def testComputationMultipleLabel(self):
        """Labelling numerous simple objects"""
        (w,h) = self.im1_1.getSize()
        
        self.im1_1.reset()
        
        n_exp = 0
        vol_exp = 0
        for wi in range(0,w-2,2):
            for hi in range(0,h-2,2):
                self.im1_1.setPixel(1, (wi,hi))
                n_exp=n_exp+1
                vol_exp = vol_exp+n_exp+(n_exp-1)//255
        
        n = label(self.im1_1, self.im32_1, grid=SQUARE)
        self.assertTrue(n==n_exp)
        vol = computeVolume(self.im32_1)
        self.assertTrue(vol==vol_exp)
        
        n = label(self.im1_1, self.im32_1, grid=HEXAGONAL)
        self.assertTrue(n==n_exp)
        vol = computeVolume(self.im32_1)
        self.assertTrue(vol==vol_exp)

    def testComputationGridEffect(self):
        """Verifies grid configuration on labelling"""
        self.im1_1.reset()
        
        # first 'object'
        self.im1_1.setPixel(1, (6,3))
        self.im1_1.setPixel(1, (5,4))
        self.im1_1.setPixel(1, (6,5))
        
        # second 'object'
        self.im1_1.setPixel(1, (4,8))
        self.im1_1.setPixel(1, (5,9))
        self.im1_1.setPixel(1, (4,10))
        
        n = label(self.im1_1, self.im32_1, grid=SQUARE)
        self.assertTrue(n==2)
        
        n = label(self.im1_1, self.im32_1, grid=HEXAGONAL)
        self.assertTrue(n==6)

    def testComputationEdge(self):
        """Verifies that objects touching the edge are correctly labelled"""
        (w,h) = self.im1_1.getSize()
        
        self.im1_1.reset()
        
        self.im1_1.setPixel(1, (0,0))
        self.im1_1.setPixel(1, (w-1,0))
        self.im1_1.setPixel(1, (0,h-1))
        self.im1_1.setPixel(1, (w-1,h-1))
        
        n = label(self.im1_1, self.im32_1, grid=SQUARE)
        self.assertTrue(n==4)
        
        n = label(self.im1_1, self.im32_1, grid=HEXAGONAL)
        self.assertTrue(n==4)

    def testComputationRange(self):
        """Labelling in the lower byte according to range specified"""
        (w,h) = self.im1_1.getSize()
        
        self.im1_1.reset()
        
        for wi in range(0,w-2,2):
            for hi in range(0,h-2,2):
                self.im1_1.setPixel(1, (wi,hi))
        
        n = label(self.im1_1, self.im32_1, 10, 230, grid=SQUARE)
        copyBytePlane(self.im32_1, 0, self.im8_1)
        l = list(range(256))
        l[0] = 10
        lookup(self.im8_1, self.im8_1, l)
        mi, ma = computeRange(self.im8_1)
        self.assertTrue(mi==10)
        self.assertTrue(ma==229)
        
        n = label(self.im1_1, self.im32_1, 10, 230, grid=HEXAGONAL)
        copyBytePlane(self.im32_1, 0, self.im8_1)
        l = list(range(256))
        l[0] = 10
        lookup(self.im8_1, self.im8_1, l)
        mi, ma = computeRange(self.im8_1)
        self.assertTrue(mi==10)
        self.assertTrue(ma==229)
        
def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestLabelb)

if __name__ == '__main__':
    unittest.main()
