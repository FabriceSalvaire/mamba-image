"""
Test cases for the functions implementing extrema operators found in the 
extrema module of mamba package.

Python functions and classes:
    minDynamics
    maxDynamics
    deepMinima
    highMaxima
    maxPartialBuild
    minPartialBuild
"""

from __future__ import division
from mamba import *
from mambaComposed import *
from mambaDraw import *
import unittest
import random

class TestExtrema(unittest.TestCase):

    def setUp(self):
        self.im1_1 = imageMb(1)
        self.im1_2 = imageMb(1)
        self.im1_3 = imageMb(1)
        self.im1_4 = imageMb(1)
        self.im8_1 = imageMb(8)
        self.im8_2 = imageMb(8)
        self.im8_3 = imageMb(8)
        self.im8_4 = imageMb(8)
        self.im32_1 = imageMb(32)
        self.im32_2 = imageMb(32)
        self.im32_3 = imageMb(32)
        self.im32_4 = imageMb(32)
        
    def tearDown(self):
        del(self.im1_1)
        del(self.im1_2)
        del(self.im1_3)
        del(self.im1_4)
        del(self.im8_1)
        del(self.im8_2)
        del(self.im8_3)
        del(self.im8_4)
        del(self.im32_1)
        del(self.im32_2)
        del(self.im32_3)
        del(self.im32_4)
            
    def _drawBaseImage(self, imOut):
        (w,h) = imOut.getSize()
        drawSquare(imOut, (0,0,w//4,h-1), 50)
        drawSquare(imOut, (w//4+1,0,w//4+20,h-1),100)
        drawSquare(imOut, (w//4+21,0,3*w//4,h-1), 70)
        drawSquare(imOut, (3*w//4+1,0,3*w//4+20,h-1),110)
        drawSquare(imOut, (3*w//4+21,0,255,h-1),50)
        return (w,h)
        
    def testMinDynamics8(self):
        """Verifies the dynamic minima function on greyscale image"""
        (w,h) = self._drawBaseImage(self.im8_1)
        negate(self.im8_1, self.im8_1)
        minDynamics(self.im8_1, self.im1_1, 30, SQUARE)
        self.im1_2.reset()
        drawSquare(self.im1_2, (w//4+1,0,w//4+20,h-1),1)
        drawSquare(self.im1_2, (3*w//4+1,0,3*w//4+20,h-1),1)
        (x,y) = compare(self.im1_1,self.im1_2,self.im1_3)
        self.assertTrue(x<0)
        self.im1_2.reset()
        minDynamics(self.im8_1, self.im1_1, 40, SQUARE)
        drawSquare(self.im1_2, (3*w//4+1,0,3*w//4+20,h-1),1)
        (x,y) = compare(self.im1_1,self.im1_2,self.im1_3)
        self.assertTrue(x<0)
        
    def testMinDynamics32(self):
        """Verifies the dynamic minima function on 32-bit image"""
        (w,h) = self._drawBaseImage(self.im32_1)
        negate(self.im32_1, self.im32_1)
        minDynamics(self.im32_1, self.im1_1, 30, SQUARE)
        self.im1_2.reset()
        drawSquare(self.im1_2, (w//4+1,0,w//4+20,h-1),1)
        drawSquare(self.im1_2, (3*w//4+1,0,3*w//4+20,h-1),1)
        (x,y) = compare(self.im1_1,self.im1_2,self.im1_3)
        self.assertTrue(x<0)
        self.im1_2.reset()
        minDynamics(self.im32_1, self.im1_1, 40, SQUARE)
        drawSquare(self.im1_2, (3*w//4+1,0,3*w//4+20,h-1),1)
        (x,y) = compare(self.im1_1,self.im1_2,self.im1_3)
        self.assertTrue(x<0)
        
    def testMaxDynamics8(self):
        """Verifies the dynamic maxima function on greyscale image"""
        (w,h) = self._drawBaseImage(self.im8_1)
        maxDynamics(self.im8_1, self.im1_1, 30, SQUARE)
        self.im1_2.reset()
        drawSquare(self.im1_2, (w//4+1,0,w//4+20,h-1),1)
        drawSquare(self.im1_2, (3*w//4+1,0,3*w//4+20,h-1),1)
        (x,y) = compare(self.im1_1,self.im1_2,self.im1_3)
        self.assertTrue(x<0)
        self.im1_2.reset()
        maxDynamics(self.im8_1, self.im1_1, 40, SQUARE)
        drawSquare(self.im1_2, (3*w//4+1,0,3*w//4+20,h-1),1)
        (x,y) = compare(self.im1_1,self.im1_2,self.im1_3)
        self.assertTrue(x<0)
        
    def testMaxDynamics32(self):
        """Verifies the dynamic maxima function on 32-bit image"""
        (w,h) = self._drawBaseImage(self.im32_1)
        maxDynamics(self.im32_1, self.im1_1, 30, SQUARE)
        self.im1_2.reset()
        drawSquare(self.im1_2, (w//4+1,0,w//4+20,h-1),1)
        drawSquare(self.im1_2, (3*w//4+1,0,3*w//4+20,h-1),1)
        (x,y) = compare(self.im1_1,self.im1_2,self.im1_3)
        self.assertTrue(x<0)
        self.im1_2.reset()
        maxDynamics(self.im32_1, self.im1_1, 40, SQUARE)
        drawSquare(self.im1_2, (3*w//4+1,0,3*w//4+20,h-1),1)
        (x,y) = compare(self.im1_1,self.im1_2,self.im1_3)
        self.assertTrue(x<0)
        
    def testDeepMinima8(self):
        """Verifies the deep minima function on greyscale image"""
        (w,h) = self._drawBaseImage(self.im8_1)
        negate(self.im8_1, self.im8_1)
        deepMinima(self.im8_1, self.im1_1, 29, SQUARE)
        self.im1_2.reset()
        drawSquare(self.im1_2, (w//4+1,0,w//4+20,h-1),1)
        drawSquare(self.im1_2, (3*w//4+1,0,3*w//4+20,h-1),1)
        (x,y) = compare(self.im1_1,self.im1_2,self.im1_3)
        self.assertTrue(x<0)
        self.im1_2.reset()
        deepMinima(self.im8_1, self.im1_1, 30, SQUARE)
        drawSquare(self.im1_2, (3*w//4+1,0,3*w//4+20,h-1),1)
        (x,y) = compare(self.im1_1,self.im1_2,self.im1_3)
        self.assertTrue(x<0)
        
    def testDeepMinima32(self):
        """Verifies the deep minima function on 32-bit image"""
        (w,h) = self._drawBaseImage(self.im32_1)
        negate(self.im32_1, self.im32_1)
        deepMinima(self.im32_1, self.im1_1, 29, SQUARE)
        self.im1_2.reset()
        drawSquare(self.im1_2, (w//4+1,0,w//4+20,h-1),1)
        drawSquare(self.im1_2, (3*w//4+1,0,3*w//4+20,h-1),1)
        (x,y) = compare(self.im1_1,self.im1_2,self.im1_3)
        self.assertTrue(x<0)
        self.im1_2.reset()
        deepMinima(self.im32_1, self.im1_1, 30, SQUARE)
        drawSquare(self.im1_2, (3*w//4+1,0,3*w//4+20,h-1),1)
        (x,y) = compare(self.im1_1,self.im1_2,self.im1_3)
        self.assertTrue(x<0)
        
    def testHighMaxima8(self):
        """Verifies the high maxima function on greyscale image"""
        (w,h) = self._drawBaseImage(self.im8_1)
        highMaxima(self.im8_1, self.im1_1, 29, SQUARE)
        self.im1_2.reset()
        drawSquare(self.im1_2, (w//4+1,0,w//4+20,h-1),1)
        drawSquare(self.im1_2, (3*w//4+1,0,3*w//4+20,h-1),1)
        (x,y) = compare(self.im1_1,self.im1_2,self.im1_3)
        self.assertTrue(x<0)
        self.im1_2.reset()
        highMaxima(self.im8_1, self.im1_1, 30, SQUARE)
        drawSquare(self.im1_2, (3*w//4+1,0,3*w//4+20,h-1),1)
        (x,y) = compare(self.im1_1,self.im1_2,self.im1_3)
        self.assertTrue(x<0)
        
    def testHighMaxima32(self):
        """Verifies the high maxima function on 32-bit image"""
        (w,h) = self._drawBaseImage(self.im32_1)
        highMaxima(self.im32_1, self.im1_1, 29, SQUARE)
        self.im1_2.reset()
        drawSquare(self.im1_2, (w//4+1,0,w//4+20,h-1),1)
        drawSquare(self.im1_2, (3*w//4+1,0,3*w//4+20,h-1),1)
        (x,y) = compare(self.im1_1,self.im1_2,self.im1_3)
        self.assertTrue(x<0)
        self.im1_2.reset()
        highMaxima(self.im32_1, self.im1_1, 30, SQUARE)
        drawSquare(self.im1_2, (3*w//4+1,0,3*w//4+20,h-1),1)
        (x,y) = compare(self.im1_1,self.im1_2,self.im1_3)
        self.assertTrue(x<0)
        
    def testMaxPartialBuild(self):
        """Verifies the maxima partial build operator"""
        (w,h) = self._drawBaseImage(self.im8_1)
        self.im1_1.reset()
        drawSquare(self.im1_1, (w//2,0,w-1,h-1), 1)
        maxPartialBuild(self.im8_1, self.im1_1, self.im8_2, SQUARE)
        drawSquare(self.im8_3, (0,0,w//4,h-1), 50)
        drawSquare(self.im8_3, (w//4+1,0,w//4+20,h-1),70)
        drawSquare(self.im8_3, (w//4+21,0,3*w//4,h-1), 70)
        drawSquare(self.im8_3, (3*w//4+1,0,3*w//4+20,h-1),110)
        drawSquare(self.im8_3, (3*w//4+21,0,255,h-1),50)
        (x,y) = compare(self.im8_3,self.im8_2,self.im8_3)
        self.assertTrue(x<0)
        
    def testMinPartialBuild(self):
        """Verifies the minima partial build operator"""
        (w,h) = self._drawBaseImage(self.im8_1)
        negate(self.im8_1, self.im8_1)
        self.im1_1.reset()
        drawSquare(self.im1_1, (w//2,0,w-1,h-1), 1)
        minPartialBuild(self.im8_1, self.im1_1, self.im8_2, SQUARE)
        drawSquare(self.im8_3, (0,0,w//4,h-1), 50)
        drawSquare(self.im8_3, (w//4+1,0,w//4+20,h-1),70)
        drawSquare(self.im8_3, (w//4+21,0,3*w//4,h-1), 70)
        drawSquare(self.im8_3, (3*w//4+1,0,3*w//4+20,h-1),110)
        drawSquare(self.im8_3, (3*w//4+21,0,255,h-1),50)
        negate(self.im8_3, self.im8_3)
        (x,y) = compare(self.im8_3,self.im8_2,self.im8_3)
        self.assertTrue(x<0)
def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestExtrema)
    
if __name__ == '__main__':
    unittest.main()

