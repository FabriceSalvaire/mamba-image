"""
Test cases for the utility functions found in mamba.

These tests cover all the functions that are not performing any computations.
"""

from __future__ import division
from mamba import *
from mambaComposed import *
from mambaDraw import *
import unittest
import random
try:
    import Image
except ImportError:
    from PIL import Image

class TestVarious(unittest.TestCase):

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
            print("ERROR : Mamba image are not all deleted !")
            
    def testGridAndEdgeRepr(self):
        """Verifies that the representation of the grid and edge value is correct"""
        self.assertTrue(repr(EMPTY)=="EMPTY")
        self.assertTrue(repr(FILLED)=="FILLED")
        self.assertTrue(repr(HEXAGONAL)=="HEXAGONAL")
        self.assertTrue(repr(SQUARE)=="SQUARE")
        self.assertTrue(repr(DEFAULT_GRID)=="DEFAULT_GRID")
        DEFAULT_GRID.id = 40
        DEFAULT_GRID.default = False
        self.assertTrue(repr(DEFAULT_GRID)=="")
        DEFAULT_GRID.default = True
        setDefaultGrid(HEXAGONAL)
        id = EMPTY.id
        EMPTY.id = 40
        self.assertTrue(repr(EMPTY)=="")
        EMPTY.id = id
        
    def testSetDefaultGrid(self):
        """Tests that modifying the default grid is correctly taken into account"""
        (w,h) = self.im8_1.getSize()
        
        self.im8_1.reset()
        self.im8_1.setPixel(255, (w//2,h//2))
        setDefaultGrid(SQUARE)
        supNeighbor(self.im8_1, self.im8_1, 2, 1)
        v = self.im8_1.getPixel((w//2-1,h//2+1))
        self.assertTrue(v==255)
        v = self.im8_1.getPixel((w//2-1,h//2))
        self.assertTrue(v==0)
        self.im8_1.reset()
        self.im8_1.setPixel(255, (w//2,h//2))
        setDefaultGrid(HEXAGONAL)
        supNeighbor(self.im8_1, self.im8_1, 2, 1)
        v = self.im8_1.getPixel((w//2-1,h//2+1))
        self.assertTrue(v==0)
        v = self.im8_1.getPixel((w//2-1,h//2))
        self.assertTrue(v==255)
        DEFAULT_GRID.id = 40
        setDefaultGrid(DEFAULT_GRID)
        self.assertTrue(getDirections()==[])
        self.assertTrue(gridNeighbors()==0)
        setDefaultGrid(HEXAGONAL)
        
    def testImageNaming(self):
        """Verifies that image names methods are correctly working"""
        nb = random.randint(-10000, -1000)
        self.im8_1.setName("test %d" % (nb))
        self.assertTrue(self.im8_1.getName()=="test %d" % (nb))
        
        setImageIndex(nb)
        im = imageMb()
        self.assertTrue(im.getName()=="Image %d" % (nb))
        im = imageMb()
        self.assertTrue(im.getName()=="Image %d" % (nb+1))
        
        self.assertTrue(str(im)!="")
        
    def testRGBFilter(self):
        """Verifies that the RGB filtering used when loading image works"""
        imref = imageMb()
        (w,h) = imref.getSize()
        
        for i in range(20):
            ri = random.randint(0,255)
            gi = random.randint(0,255)
            bi = random.randint(0,255)
            
            # Creates an image and saving it
            Image.new("RGB", (w,h), (ri,gi,bi)).save("test.bmp")
            
            im = imageMb("test.bmp", rgbfilter=(1.0,0.0,0.0))
            vol = computeVolume(im)
            self.assertTrue(vol==w*h*ri or vol==w*h*(ri-1) or vol==w*h*(ri+1),
                         "%d %d %d %d %d" %(vol, ri, gi, bi, im.getPixel((0,0))) )
            
            im = imageMb("test.bmp", rgbfilter=(0.0,1.0,0.0))
            vol = computeVolume(im)
            self.assertTrue(vol==w*h*gi or vol==w*h*(gi-1) or vol==w*h*(gi+1),
                         "%d %d %d %d %d" %(vol, ri, gi, bi, im.getPixel((0,0))) )
            
            im = imageMb("test.bmp", rgbfilter=(0.0,0.0,1.0))
            vol = computeVolume(im)
            self.assertTrue(vol==w*h*bi or vol==w*h*(bi-1) or vol==w*h*(bi+1),
                         "%d %d %d %d %d" %(vol, ri, gi, bi, im.getPixel((0,0))) )
            
            os.remove("test.bmp")
        

def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestVarious)
    
if __name__ == '__main__':
    unittest.main()
