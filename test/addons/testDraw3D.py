"""
Test cases for the drawing functions found in the draw3D module of
mamba3D package. 

Python functions:
    drawLine3D
    drawCube
    getIntensityAlongLine3D
"""

from mamba import *
from mambaDraw import *
from mamba3D import *
import unittest
import random

class TestDraw3D(unittest.TestCase):

    def setUp(self):
        self.im1_1 = image3DMb(64,64,64,1)
        self.im1_2 = image3DMb(64,64,64,1)
        self.im1_3 = image3DMb(64,64,64,1)
        self.im1_4 = image3DMb(64,64,64,1)
        self.im1_5 = image3DMb(128,128,128,1)
        self.im8_1 = image3DMb(64,64,64,8)
        self.im8_2 = image3DMb(64,64,64,8)
        self.im8_3 = image3DMb(64,64,64,8)
        self.im8_4 = image3DMb(64,64,64,8)
        self.im8_5 = image3DMb(128,128,128,8)
        self.im32_1 = image3DMb(64,64,64,32)
        self.im32_2 = image3DMb(64,64,64,32)
        self.im32_3 = image3DMb(64,64,64,32)
        self.im32_4 = image3DMb(64,64,64,32)
        self.im32_5 = image3DMb(128,128,128,32)
        
    def tearDown(self):
        del(self.im1_1)
        del(self.im1_2)
        del(self.im1_3)
        del(self.im1_4)
        del(self.im1_5)
        del(self.im8_1)
        del(self.im8_2)
        del(self.im8_3)
        del(self.im8_4)
        del(self.im8_5)
        del(self.im32_1)
        del(self.im32_2)
        del(self.im32_3)
        del(self.im32_4)
        del(self.im32_5)

    def testDrawLine3D(self):
        """Tests the line drawing function in draw3D"""
        (w,h) = self.im8_1.getSize()
        l = self.im8_1.getLength()
        x,y,z = w/2, h/2, l/2
        e = 3
        
        dirs = [
            (0,0,1),
            (0,0,-1),
            (0,1,0),
            (0,1,1),
            (0,1,-1),
            (0,-1,0),
            (0,-1,1),
            (0,-1,-1),
            (1,0,0),
            (1,0,1),
            (1,0,-1),
            (1,1,0),
            (1,1,1),
            (1,1,-1),
            (1,-1,0),
            (1,-1,1),
            (1,-1,-1),
            (-1,0,0),
            (-1,0,1),
            (-1,0,-1),
            (-1,1,0),
            (-1,1,1),
            (-1,1,-1),
            (-1,-1,0),
            (-1,-1,1),
            (-1,-1,-1),
            (1,2,0),
            (1,0,2),
            (0,1,2)
        ]
        
        for d in dirs:
            self.im8_1.reset()
            drawLine3D(self.im8_1, (x,y,z,x+d[0]*e,y+d[1]*e,z+d[2]*e), 255)
            vol = computeVolume3D(self.im8_1)
            evol = (e*max(list(map(abs, d)))+1)*255
            self.assertTrue(vol==evol, "%s : %d" %(repr(d),vol/255))
        
    def testDrawCube(self):
        """Verifies the drawing cubes function"""
        (w,h) = self.im8_1.getSize()
        l = self.im8_1.getLength()
        x,y,z = w/2, h/2, l/2
        e = 3
        
        self.im8_1.reset()
        drawCube(self.im8_1, (x+e,y+e,z+e,x-e,y-e,z-e), 200)
        vol = computeVolume3D(self.im8_1)
        self.assertTrue(vol==pow(2*e+1,3)*200)
        
    def testGetIntensityAlongLine3D(self):
        """Tests the intensity extraction function in draw3D"""
        (w,h) = self.im8_1.getSize()
        l = self.im8_1.getLength()
        x,y,z = w/2, h/2, l/2
        e = 3
        
        for i in range(l):
            self.im8_1[i].fill(i)
        
        dirs = [
            (0,0,1),
            (0,0,-1),
            (0,1,0),
            (0,1,1),
            (0,1,-1),
            (0,-1,0),
            (0,-1,1),
            (0,-1,-1),
            (1,0,0),
            (1,0,1),
            (1,0,-1),
            (1,1,0),
            (1,1,1),
            (1,1,-1),
            (1,-1,0),
            (1,-1,1),
            (1,-1,-1),
            (-1,0,0),
            (-1,0,1),
            (-1,0,-1),
            (-1,1,0),
            (-1,1,1),
            (-1,1,-1),
            (-1,-1,0),
            (-1,-1,1),
            (-1,-1,-1),
            (1,2,0),
            (1,0,2),
            (0,1,2)
        ]
        
        for d in dirs:
            inte = getIntensityAlongLine3D(self.im8_1, (x,y,z,x+d[0]*e,y+d[1]*e,z+d[2]*e))
            if d[2]==0:
                self.assertTrue(inte == (e*max(list(map(abs, d)))+1)*[z])
            elif d[2]<0:
                self.assertTrue(inte == list(range(z,z-e*max(list(map(abs, d)))-1,-1)), "%s : %d" % (repr(d),max(list(map(abs, d)))))
            else:
                self.assertTrue(inte == list(range(z,z+e*max(list(map(abs, d)))+1)), "%s : %d" % (repr(d),max(list(map(abs, d)))))

def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestDraw3D)
    
if __name__ == '__main__':
    unittest.main()
