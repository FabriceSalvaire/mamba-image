"""
Test cases for the hierarchical dual build function.

The function works on greyscale images. All images, both input and output, must
have the same depth.

The function builds (dual operation) an image using the first input image as a
mask.

The function result depends on choice over grid.

Python function:
    hierarDualBuild
    
C functions:
    MB_HierarDualBld
"""

from mamba import *
from mambaDraw import drawLine
import unittest
import random

class TestHierarDualBld(unittest.TestCase):

    def setUp(self):
        # Creating two images for each possible depth
        self.im1_1 = imageMb(1)
        self.im1_2 = imageMb(1)
        self.im1_3 = imageMb(1)
        self.im8_1 = imageMb(8)
        self.im8_2 = imageMb(8)
        self.im8_3 = imageMb(8)
        self.im8_4 = imageMb(8)
        self.im32_1 = imageMb(32)
        self.im32_2 = imageMb(32)
        self.im32_3 = imageMb(32)
        self.im8s2_1 = imageMb(128,128,8)
        self.im8s2_2 = imageMb(128,128,8)
        self.im8s2_3 = imageMb(128,128,8)
        
    def tearDown(self):
        del(self.im1_1)
        del(self.im1_2)
        del(self.im1_3)
        del(self.im8_1)
        del(self.im8_2)
        del(self.im8_3)
        del(self.im8_4)
        del(self.im32_1)
        del(self.im32_2)
        del(self.im32_3)
        del(self.im8s2_1)
        del(self.im8s2_2)
        del(self.im8s2_3)
        if getImageCounter()!=0:
            print "ERROR : Mamba image are not all deleted !"

    def testDepthAcceptation(self):
        """Tests that incorrect depth raises an exception"""
        self.assertRaises(MambaError, hierarDualBuild, self.im1_1, self.im1_2)
        self.assertRaises(MambaError, hierarDualBuild, self.im1_1, self.im8_2)
        self.assertRaises(MambaError, hierarDualBuild, self.im1_1, self.im32_2)
        self.assertRaises(MambaError, hierarDualBuild, self.im8_1, self.im1_2)
        #self.assertRaises(MambaError, hierarDualBuild, self.im8_1, self.im8_2)
        self.assertRaises(MambaError, hierarDualBuild, self.im8_1, self.im32_2)
        self.assertRaises(MambaError, hierarDualBuild, self.im32_1, self.im1_2)
        self.assertRaises(MambaError, hierarDualBuild, self.im32_1, self.im8_2)
        self.assertRaises(MambaError, hierarDualBuild, self.im32_1, self.im32_2)

    def testSizeCheck(self):
        """Tests that different sizes raise an exception"""
        self.assertRaises(MambaError, hierarDualBuild, self.im8s2_1, self.im8_2)
        self.assertRaises(MambaError, hierarDualBuild, self.im8_1, self.im8s2_2)
        
    def _drawTestIm(self, imOut, value):

        (w,h) = imOut.getSize()
        drawLine(imOut, (1,1,1,h/3), value)
        drawLine(imOut, (1,h/3,w/3,h/3), value)
        for i in range(1,min(h/4,w/4)):
            drawLine(imOut, (w/3+(i-1),h/3-i,w/3+i,h/3-i),value)
        drawLine(imOut, (w/3+i,h/3-i,w/3+i,(2*h)/3-i), value)
        for j in range(1,min(h/4,w/4)):
            drawLine(imOut, (w/3+i-(j-1),(2*h)/3-i+j,w/3+i-j,(2*h)/3-i+j),value)
        drawLine(imOut, (w/3+i-j,(2*h)/3-i+j,w/3+i-j-w/5,(2*h)/3-i+j),value)
        drawLine(imOut, (w/3+i-j-w/5,(2*h)/3-i+j,w/3+i-j-w/5,(2*h)/3-i+j-h/6),value)

    def testComputation(self):
        """Tests hierarchical build for both grids"""
        self.im8_1.fill(255)
        self._drawTestIm(self.im8_1, 0)
        
        for i in range(10):
            vi =  random.randint(0,254)
        
            self.im8_4.fill(255)
            self._drawTestIm(self.im8_4, vi)
        
            self.im8_2.fill(255)
            self.im8_2.setPixel(vi, (1,1))
            hierarDualBuild(self.im8_1, self.im8_2, grid=HEXAGONAL)
            (x,y) = compare(self.im8_4, self.im8_2, self.im8_3)
            self.assert_(x<0)
            
            self.im8_2.fill(255)
            self.im8_2.setPixel(vi, (1,1))
            hierarDualBuild(self.im8_1, self.im8_2, grid=SQUARE)
            (x,y) = compare(self.im8_4, self.im8_2, self.im8_3)
            self.assert_(x<0)

    def _drawCross(self, imOut, imExp, x, y, value):
        imOut.setPixel(value, (x,y))
        imOut.setPixel(value, (x-1,y-1))
        imOut.setPixel(value, (x-1,y+1))
        imOut.setPixel(value, (x+1,y-1))
        imOut.setPixel(value, (x+1,y+1))
        if y%2==0:
            imExp.setPixel(value, (x,y))
            imExp.setPixel(value, (x-1,y-1))
            imExp.setPixel(value, (x-1,y+1))
        else:
            imExp.setPixel(value, (x,y))
            imExp.setPixel(value, (x+1,y-1))
            imExp.setPixel(value, (x+1,y+1))
    
    def testGridEffect(self):
        """Verifies that grid is correctly taken into account"""
        self.im8_1.fill(255)
        self.im8_4.fill(255)
        self._drawCross(self.im8_1, self.im8_4, 10,10, 0)
        
        self.im8_2.fill(255)
        self.im8_2.setPixel(0, (10,10))
        hierarDualBuild(self.im8_1, self.im8_2, grid=HEXAGONAL)
        (x,y) = compare(self.im8_4, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
        self.im8_2.fill(255)
        self.im8_2.setPixel(0, (10,10))
        hierarDualBuild(self.im8_1, self.im8_2, grid=SQUARE)
        (x,y) = compare(self.im8_1, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
        


def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestHierarDualBld)

if __name__ == '__main__':
    unittest.main()
