"""
Test cases for the various uncategorized functions found in the miscellaneous
module of mambaComposed package.

Python functions:
    isotropicDistance
    drawEdge
    ceilingAddConst
    ceilingAdd
    floorSubConst
    floorSub
    translate
"""

from mamba import *
from mambaComposed import *
from mambaDraw import *
import unittest
import random

class TestMiscellaneous(unittest.TestCase):

    def setUp(self):
        self.im1_1 = imageMb(1)
        self.im1_2 = imageMb(1)
        self.im1_3 = imageMb(1)
        self.im8_1 = imageMb(8)
        self.im8_2 = imageMb(8)
        self.im8_3 = imageMb(8)
        self.im32_1 = imageMb(32)
        self.im32_2 = imageMb(32)
        self.im32_3 = imageMb(32)
        
    def tearDown(self):
        del(self.im1_1)
        del(self.im1_2)
        del(self.im1_3)
        del(self.im8_1)
        del(self.im8_2)
        del(self.im8_3)
        del(self.im32_1)
        del(self.im32_2)
        del(self.im32_3)
        if getImageCounter()!=0:
            print "ERROR : Mamba image are not all deleted !"
        
    def testIsotropicDistanceDepthAcceptance(self):
        """Verifies that isotropicDistance refuses non binary input images"""
        self.assertRaises(MambaError, isotropicDistance, self.im8_1, self.im8_2)
        self.assertRaises(MambaError, isotropicDistance, self.im32_1, self.im8_2)
        
    def testIsotropicDistance(self):
        """Tests the computation of an isotropic distance"""
        (w,h) = self.im1_1.getSize()
        
        self.im1_1.reset()
        drawSquare(self.im1_1, (w/2-1, h/2-1, w/2+1, h/2+1), 1)
        
        self.im8_3.reset()
        drawSquare(self.im8_3, (w/2-1, h/2-1, w/2+1, h/2+1), 1)
        self.im8_3.setPixel(2, (w/2, h/2))
        isotropicDistance(self.im1_1, self.im8_1)
        (x,y) = compare(self.im8_1, self.im8_3, self.im8_2)
        self.assert_(x<0)
        
    def testDrawEdge(self):
        """Verifies that the edge is correctly drawn"""
        (w,h) = self.im8_1.getSize()
        
        for thick in range(10):
            self.im8_1.reset()
            drawEdge(self.im8_1, thick)
            self.im8_3.fill(255)
            drawSquare(self.im8_3, (thick, thick, w-1-thick, h-1-thick), 0)
            (x,y) = compare(self.im8_1, self.im8_3, self.im8_2)
            self.assert_(x<0)
        
    def testCeilingAdd(self):
        """Verifies the saturated (ceiling) addition for 32-bit images"""
        (w,h) = self.im32_1.getSize()
        
        self.im32_1.fill(0xffffff80)
        for i in range(256):
            self.im32_3.fill(i)
            ceilingAdd(self.im32_1, self.im32_3, self.im32_2)
            vol = computeVolume(self.im32_2)/(w*h)
            value = min(0xffffff80+i, 0xffffffff)
            self.assert_(vol==value)
        
    def testCeilingAddConst(self):
        """Verifies the saturated (ceiling) constant addition for 32-bit images"""
        (w,h) = self.im32_1.getSize()
        
        self.im32_1.fill(0xffffff80)
        for i in range(256):
            ceilingAddConst(self.im32_1, i, self.im32_2)
            vol = computeVolume(self.im32_2)/(w*h)
            value = min(0xffffff80+i, 0xffffffff)
            self.assert_(vol==value)
        
    def testFloorSub(self):
        """Verifies the saturated (floor) subtraction for 32-bit images"""
        (w,h) = self.im32_1.getSize()
        
        self.im32_1.fill(0x80)
        for i in range(256):
            self.im32_3.fill(i)
            floorSub(self.im32_1, self.im32_3, self.im32_2)
            vol = computeVolume(self.im32_2)/(w*h)
            value = max(0x80-i, 0)
            self.assert_(vol==value, "%d: %d %d" % (i,vol, value))
        
    def testFloorSubConst(self):
        """Verifies the saturated (floor) constant subtraction for 32-bit images"""
        (w,h) = self.im32_1.getSize()
        
        self.im32_1.fill(0x80)
        for i in range(256):
            floorSubConst(self.im32_1, i, self.im32_2)
            vol = computeVolume(self.im32_2)/(w*h)
            value = max(0x80-i, 0)
            self.assert_(vol==value)
            
    def testTranslate(self):
        """Verifies the translation operator"""
        (w,h) = self.im8_1.getSize()
        
        self.im8_1.reset()
        self.im8_1.setPixel(128, (w/2,h/2))
        
        for i in range(10):
            xi = random.randint(-w/4,w/4)
            yi = random.randint(-h/4,h/4)
            translate(self.im8_1, self.im8_2, xi, yi, 0)
            self.im8_3.reset()
            self.im8_3.setPixel(128, (w/2+xi,h/2+yi))
            (x,y) = compare(self.im8_2, self.im8_3, self.im8_2)
            self.assert_(x<0)
            translate(self.im8_1, self.im8_2, -xi, -yi, 0)
            self.im8_3.reset()
            self.im8_3.setPixel(128, (w/2-xi,h/2-yi))
            (x,y) = compare(self.im8_2, self.im8_3, self.im8_2)
            self.assert_(x<0)
        
    def testMulRealConstDepthAcceptance(self):
        """Verifies that mulRealConst refuses binary input images"""
        self.assertRaises(MambaError, mulRealConst, self.im1_1, 1.0, self.im8_2)
        self.assertRaises(MambaError, mulRealConst, self.im32_1, 1.0, self.im1_2)
        
    def testMulRealConst(self):
        """Tests the real value multiplication"""
        self.im8_1.fill(1)
        
        self.im8_3.fill(1)
        mulRealConst(self.im8_1, 1.6, self.im8_2, nearest=False)
        (x,y) = compare(self.im8_3, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
        self.im8_3.fill(2)
        mulRealConst(self.im8_1, 1.6, self.im8_2, nearest=True)
        (x,y) = compare(self.im8_3, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
        self.im8_1.fill(10)
        self.im8_3.fill(15)
        mulRealConst(self.im8_1, 1.5, self.im8_2)
        (x,y) = compare(self.im8_3, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
        self.im32_1.fill(1000)
        self.im32_3.fill(1500)
        mulRealConst(self.im32_1, 1.5, self.im32_2)
        (x,y) = compare(self.im32_3, self.im32_2, self.im32_3)
        self.assert_(x<0)
        
        self.im8_1.fill(200)
        self.im8_3.fill(255)
        self.im32_3.fill(260)
        mulRealConst(self.im8_1, 1.3, self.im8_2)
        (x,y) = compare(self.im8_3, self.im8_2, self.im8_3)
        self.assert_(x<0)
        mulRealConst(self.im8_1, 1.3, self.im32_2)
        (x,y) = compare(self.im32_3, self.im32_2, self.im32_3)
        self.assert_(x<0)
        

def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestMiscellaneous)
    
if __name__ == '__main__':
    unittest.main()
