"""
Test cases for the image basin segmentation function.

The function works on 8-bit images and returns in a 32-bit image, the watershed
segmentation (only the catchment basins) as found using the same 32-bit image as 
an initialisation for wells.

The function is not idempotent. However you can control the level reached by the
flooding process.
    
Python function:
    basinSegment
    
C function:
    MB_Basins
"""
from __future__ import division
from mamba import *
import unittest
import random

class TestBasin(unittest.TestCase):

    def setUp(self):
        # Creating two images for each possible depth
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
        self.im32s2_1 = imageMb(128,128,32)
        
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
        del(self.im32s2_1)
        if getImageCounter()!=0:
            print("ERROR : Mamba image are not all deleted !")

    def testDepthAcceptation(self):
        """Tests that incorrect depth raises an exception"""
        self.assertRaises(MambaError, basinSegment, self.im1_1, self.im1_2)
        self.assertRaises(MambaError, basinSegment, self.im1_1, self.im8_2)
        self.assertRaises(MambaError, basinSegment, self.im1_1, self.im32_2)
        self.assertRaises(MambaError, basinSegment, self.im8_1, self.im1_2)
        self.assertRaises(MambaError, basinSegment, self.im8_1, self.im8_2)
        #self.assertRaises(MambaError, basinSegment, self.im8_1, self.im32_2)
        self.assertRaises(MambaError, basinSegment, self.im32_1, self.im1_2)
        self.assertRaises(MambaError, basinSegment, self.im32_1, self.im8_2)
        self.assertRaises(MambaError, basinSegment, self.im32_1, self.im32_2)

    def testSizeCheck(self):
        """Tests that different sizes raise an exception"""
        self.assertRaises(MambaError, basinSegment, self.im8s2_1, self.im32_1)
        self.assertRaises(MambaError, basinSegment, self.im8_1, self.im32s2_1)
        
    def testParameterAcceptation(self):
        """Tests that incoherent parameters produce an exception"""
        for i in range(257,400):
            self.assertRaises(MambaError, basinSegment, self.im8_1, self.im32_2, max_level=i)

    def testComputationSquare(self):
        """Verifies that the basin computation is correct for a simple wall image in square grid"""
        (w,h) = self.im8_1.getSize()
        
        for i in range(w//4,(3*w)//4):
            # creating a wall image
            self.im8_1.reset()
            for hi in range(h):
                self.im8_1.setPixel(255, (i,hi))
                
            exp_vol = (i*50+(w-1-i)*100)*h
            exp_vol1 = exp_vol+50*h
            exp_vol2 = exp_vol+100*h
                    
            # adding 2 well
            self.im32_1.reset()
            self.im32_1.setPixel(50, (w//4-1,h//2))
            self.im32_1.setPixel(100, ((3*w)//4,h//2))
            
            basinSegment(self.im8_1, self.im32_1, grid=SQUARE)
            copyBytePlane(self.im32_1, 0, self.im8_2)
            vol = computeVolume(self.im8_2)
            self.assertTrue(exp_vol1<=vol and exp_vol2>=vol, "wall at %d [%d,%d]: %d/%d/%d" %(i,w//4,(3*w)//4,vol,exp_vol1,exp_vol2))

    def testComputationHexagonal(self):
        """Verifies that the basin computation is correct for a simple wall image in hexagonal grid"""
        (w,h) = self.im8_1.getSize()
        
        for i in range(w//4,(3*w)//4):
            # creating a wall image
            self.im8_1.reset()
            for hi in range(h):
                self.im8_1.setPixel(255, (i,hi))
                
            exp_vol = (i*50+(w-1-i)*100)*h
            exp_vol1 = exp_vol+50*h
            exp_vol2 = exp_vol+100*h
                    
            # adding 2 well
            self.im32_1.reset()
            self.im32_1.setPixel(50, (w//4-1,h//2))
            self.im32_1.setPixel(100, ((3*w)//4,h//2))
            
            basinSegment(self.im8_1, self.im32_1, grid=HEXAGONAL)
            copyBytePlane(self.im32_1, 0, self.im8_2)
            vol = computeVolume(self.im8_2)
            self.assertTrue(exp_vol1<=vol and exp_vol2>=vol, "wall at %d [%d,%d]: %d/%d/%d" %(i,w//4,(3*w)//4,vol,exp_vol1,exp_vol2))

    def testComputationControl(self):
        """Verifies that the waterlevel control parameter works correctly"""
        (w,h) = self.im8_1.getSize()
        
        for wi in range(w):
            for hi in range(h):
                self.im8_1.setPixel(wi, (wi,hi))
                
        for max_level in range(0,257):
                
            # adding well
            self.im32_1.reset()
            self.im32_1.setPixel(1, (0,0))
        
            basinSegment(self.im8_1, self.im32_1, max_level=max_level)
            copyBytePlane(self.im32_1, 0, self.im8_2)
            exp_vol = max_level==0 and 1 or ((max_level+1)*h)
            exp_vol = min(exp_vol,w*h)
            vol = computeVolume(self.im8_2)
            self.assertTrue(vol==exp_vol, "level %d : %d/%d" %(max_level,vol,exp_vol))

    def testComputationInit(self):
        """Tests that the basins correctly handles an image with values in MSByte"""
        (w,h) = self.im8_1.getSize()
        
        for i in range(w//4,(3*w)//4):
            # creating a wall image
            self.im8_1.reset()
            for hi in range(h):
                self.im8_1.setPixel(255, (i,hi))
                
            exp_vol = (i*50+(w-1-i)*100)*h
            exp_vol1 = exp_vol+50*h
            exp_vol2 = exp_vol+100*h
                    
            # adding 2 well
            self.im32_1.fill(0x01000000)
            self.im32_1.setPixel(0x01000000+50, (w//4-1,h//2))
            self.im32_1.setPixel(0x01000000+100, ((3*w)//4,h//2))
            
            basinSegment(self.im8_1, self.im32_1, grid=SQUARE)
            copyBytePlane(self.im32_1, 0, self.im8_2)
            vol = computeVolume(self.im8_2)
            self.assertTrue(exp_vol1<=vol and exp_vol2>=vol, "wall at %d [%d,%d]: %d/%d/%d" %(i,w//4,(3*w)//4,vol,exp_vol1,exp_vol2))
            

def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestBasin)

if __name__ == '__main__':
    unittest.main()
