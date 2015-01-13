"""
Test cases for the image supremum computation function.

The function works on all image depths. Input and output images must have the 
same depth.

Here is the list of legal supremum operations :
    sup( 1, 1) = 1
    sup( 8, 8) = 8
    sup(32,32) =32
    
Pixels in the output image are set to the highest value of the corresponding 
pixels in the two input images.

Python function:
    logic with parameter 'sup'
    
C function:
    MB_Sup
"""

from mamba import *
from mambaDraw import drawSquare
import unittest
import random

class TestSup(unittest.TestCase):

    def setUp(self):
        # Creating three images for each possible depth
        self.im1_1 = imageMb(1)
        self.im1_2 = imageMb(1)
        self.im1_3 = imageMb(1)
        self.im8_1 = imageMb(8)
        self.im8_2 = imageMb(8)
        self.im8_3 = imageMb(8)
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
        self.assertRaises(MambaError, logic, self.im8_3, self.im1_2, self.im1_1, 'sup')
        self.assertRaises(MambaError, logic, self.im32_3, self.im1_2, self.im1_1, 'sup')
        self.assertRaises(MambaError, logic, self.im1_3, self.im8_2, self.im1_1, 'sup')
        self.assertRaises(MambaError, logic, self.im8_3, self.im8_2, self.im1_1, 'sup')
        self.assertRaises(MambaError, logic, self.im32_3, self.im8_2, self.im1_1, 'sup')
        self.assertRaises(MambaError, logic, self.im1_3, self.im32_2, self.im1_1, 'sup')
        self.assertRaises(MambaError, logic, self.im8_3, self.im32_2, self.im1_1, 'sup')
        self.assertRaises(MambaError, logic, self.im32_3, self.im32_2, self.im1_1, 'sup')
        self.assertRaises(MambaError, logic, self.im1_3, self.im1_2, self.im8_1, 'sup')
        self.assertRaises(MambaError, logic, self.im8_3, self.im1_2, self.im8_1, 'sup')
        self.assertRaises(MambaError, logic, self.im32_3, self.im1_2, self.im8_1, 'sup')
        self.assertRaises(MambaError, logic, self.im1_3, self.im8_2, self.im8_1, 'sup')
        self.assertRaises(MambaError, logic, self.im32_3, self.im8_2, self.im8_1, 'sup')
        self.assertRaises(MambaError, logic, self.im1_3, self.im32_2, self.im8_1, 'sup')
        self.assertRaises(MambaError, logic, self.im8_3, self.im32_2, self.im8_1, 'sup')
        self.assertRaises(MambaError, logic, self.im32_3, self.im32_2, self.im8_1, 'sup')
        self.assertRaises(MambaError, logic, self.im1_3, self.im1_2, self.im32_1, 'sup')
        self.assertRaises(MambaError, logic, self.im8_3, self.im1_2, self.im32_1, 'sup')
        self.assertRaises(MambaError, logic, self.im32_3, self.im1_2, self.im32_1, 'sup')
        self.assertRaises(MambaError, logic, self.im1_3, self.im8_2, self.im32_1, 'sup')
        self.assertRaises(MambaError, logic, self.im8_3, self.im8_2, self.im32_1, 'sup')
        self.assertRaises(MambaError, logic, self.im32_3, self.im8_2, self.im32_1, 'sup')
        self.assertRaises(MambaError, logic, self.im1_3, self.im32_2, self.im32_1, 'sup')
        self.assertRaises(MambaError, logic, self.im8_3, self.im32_2, self.im32_1, 'sup')

    def testSizeCheck(self):
        """Tests that different sizes raise an exception"""
        self.assertRaises(MambaError, logic, self.im8_3, self.im8_2, self.im8s2_1, 'sup')
        self.assertRaises(MambaError, logic, self.im8_3, self.im8s2_2, self.im8_1, 'sup')
        self.assertRaises(MambaError, logic, self.im8_3, self.im8s2_2, self.im8s2_1, 'sup')
        self.assertRaises(MambaError, logic, self.im8s2_3, self.im8_2, self.im8_1, 'sup')
        self.assertRaises(MambaError, logic, self.im8s2_3, self.im8_2, self.im8s2_1, 'sup')
        self.assertRaises(MambaError, logic, self.im8s2_3, self.im8s2_2, self.im8_1, 'sup')

    def testComputation_1(self):
        """Tests the supremum computation on binary images (OR operator)"""
        (w,h) = self.im1_1.getSize()
        self.im1_1.reset()
        self.im1_2.reset()
        self.im1_3.reset()
        
        drawSquare(self.im1_1,[w/2,0,w-1,h/2-1],1)
        drawSquare(self.im1_3,[w/2,0,w-1,h/2-1],1)
        drawSquare(self.im1_1,[0,h/2,w/2-1,h-1],1)
        drawSquare(self.im1_2,[0,h/2,w/2-1,h-1],1)
        drawSquare(self.im1_3,[0,h/2,w/2-1,h-1],1)
        drawSquare(self.im1_2,[w/2,h/2,w-1,h-1],1)
        drawSquare(self.im1_3,[w/2,h/2,w-1,h-1],1)
        
        logic(self.im1_2, self.im1_1, self.im1_2, 'sup')
        (x,y) = compare(self.im1_3, self.im1_2, self.im1_3)
        self.assert_(x<0)

    def testComputation_8(self):
        """Computes the result of supremum selection on 8-bit images"""
        for i in range(100):
            self.im8_3.reset()
            v1 = random.randint(0, 255)
            v2 = random.randint(0, 255)
            self.im8_1.fill(v1)
            self.im8_2.fill(v2)
            logic(self.im8_2, self.im8_1, self.im8_3, 'sup')
            self.im8_2.fill(max(v1,v2))
            (x,y) = compare(self.im8_3, self.im8_2, self.im8_3)
            self.assert_(x<0)

    def testComputation_32(self):
        """Computes the result of supremum selection on 32-bit images"""
        for i in range(100):
            self.im32_3.reset()
            v1 = random.randint(0,1000000)
            v2 = random.randint(0,1000000)
            self.im32_1.fill(v1)
            self.im32_2.fill(v2)
            logic(self.im32_2, self.im32_1, self.im32_3, 'sup')
            self.im32_2.fill(max(v1,v2))
            (x,y) = compare(self.im32_3, self.im32_2, self.im32_3)
            self.assert_(x<0)
        

def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestSup)
    
if __name__ == '__main__':
    unittest.main()
