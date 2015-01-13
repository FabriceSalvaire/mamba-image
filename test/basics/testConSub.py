"""
Test cases for the image constant subtraction function.

The function works with 8-bit and 32-bit images. The function returns an image where 
the pixels of the input image have been subtracted with a given constant value. 
Thus the result image must at least be as deep as the input image. If not, the 
function raises an error.

Here is the list of legal subtraction operations (where c is the constant):
     8 - c = 8
     8 - c =32
    32 - c =32
    
On 8-bit images, the result is saturated so that it does not exceed the range
(0-255) of possible values.

Python function:
    subConst
    
C function:
    MB_ConSub
"""

from mamba import *
import unittest
import random

class TestConSub(unittest.TestCase):

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
        if getImageCounter()!=0:
            print("ERROR : Mamba image are not all deleted !")

    def testDepthAcceptation(self):
        """Tests that incorrect depth raises an exception"""
        self.assertRaises(MambaError, subConst, self.im1_2, 1, self.im1_1)
        self.assertRaises(MambaError, subConst, self.im1_2, 1, self.im8_1)
        self.assertRaises(MambaError, subConst, self.im1_2, 1, self.im32_1)
        self.assertRaises(MambaError, subConst, self.im8_2, 1, self.im1_1)
        #self.assertRaises(MambaError, subConst, self.im8_2, 1, self.im8_1)
        #self.assertRaises(MambaError, subConst, self.im8_2, 1, self.im32_1)
        self.assertRaises(MambaError, subConst, self.im32_2, 1, self.im1_1)
        self.assertRaises(MambaError, subConst, self.im32_2, 1, self.im8_1)
        #self.assertRaises(MambaError, subConst, self.im32_2, 1, self.im32_1)

    def testSizeCheck(self):
        """Tests that different sizes raise an exception"""
        self.assertRaises(MambaError, subConst, self.im8s2_2, 1, self.im8_1)
        self.assertRaises(MambaError, subConst, self.im8_2, 1, self.im8s2_1)

    def testComputation_8_8(self):
        """Subtracts a constant to a 8-bit image and puts the result in a 8-bit image"""
        self.im8_1.fill(255)
        self.im8_3.reset()
        for i in range(256):
            subConst(self.im8_1, i, self.im8_2)
            self.assertTrue(self.im8_2.getPixel((0,0))==255-i)
            
        (x,y) = compare(self.im8_3, self.im8_2, self.im8_3)
        self.assertTrue(x<0)
        
        subConst(self.im8_1, 999, self.im8_2)
        self.assertTrue(self.im8_2.getPixel((0,0))==0)
        
        self.im8_1.reset()
        subConst(self.im8_1, -255, self.im8_2)
        self.assertTrue(self.im8_2.getPixel((0,0))==255)
        
        subConst(self.im8_2, -1, self.im8_2)
        self.assertTrue(self.im8_2.getPixel((0,0))==255, "%d/255" % (self.im8_2.getPixel((0,0))))

    def testComputation_8_32(self):
        """Subtracts a constant to a 8-bit image and puts the result in a 32-bit image"""
        self.im8_1.fill(255)
        self.im32_3.fill(0xffffffff+256-999)
        for i in range(1000):
            subConst(self.im8_1, i, self.im32_2)
            if (255-i < 0):
                exp_val = 0xffffffff+(256-i)
            else:
                exp_val = 255-i
            self.assertTrue(self.im32_2.getPixel((0,0))==exp_val)
            
        (x,y) = compare(self.im32_3, self.im32_2, self.im32_3)
        self.assertTrue(x<0)

    def testComputation_32_32(self):
        """Subtracts a constant to a 32-bit image and puts the result in a 32-bit image"""
        for i in range(1000):
            v = random.randint(1,100000)
            self.im32_1.fill(v)
            subConst(self.im32_1, i, self.im32_2)
            if (v-i < 0):
                exp_val = 0xffffffff+(v+1-i)
            else:
                exp_val = v-i
            self.assertTrue(self.im32_2.getPixel((0,0))==exp_val)
        

def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestConSub)
    
if __name__ == '__main__':
    unittest.main()
