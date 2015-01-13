"""
Test cases for the image set difference by neighbor function.

The function works on all images depths. All images, both input and output, must
have the same depth.

Here is the list of legal operations :
     1 / 1 = 1
     8 / 8 = 8
    32 /32 =32
    
The result in output is the set difference (see testDiff for a definition). In
this case however, the pixels inside the second input image (which is also the 
output image) are compared with their neighbors (specified to the function) 
inside the first image.

The result depends on grid and edge configurations. Allowed values for neighbor
is restricted according to grid configuration.

Python function:
    diffNeighbor
    
C functions:
    MB_DiffNbb
    MB_DiffNb8
"""

from mamba import *
import unittest
import random

class TestDiffNb(unittest.TestCase):

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
        
        self.directions = [
            (0,0),
            (0,-1),
            (1,-1),
            (1,0),
            (1,1),
            (0,1),
            (-1,1),
            (-1,0),
            (-1,-1)
        ]
        
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
            print "ERROR : Mamba image are not all deleted !"

    def testDepthAcceptation(self):
        """Tests that incorrect depth raises an exception"""
        #self.assertRaises(MambaError, diffNeighbor, self.im1_1, self.im1_2,0)
        self.assertRaises(MambaError, diffNeighbor, self.im1_1, self.im8_2,0)
        self.assertRaises(MambaError, diffNeighbor, self.im1_1, self.im32_2,0)
        self.assertRaises(MambaError, diffNeighbor, self.im8_1, self.im1_2,0)
        #self.assertRaises(MambaError, diffNeighbor, self.im8_1, self.im8_2,0)
        self.assertRaises(MambaError, diffNeighbor, self.im8_1, self.im32_2,0)
        self.assertRaises(MambaError, diffNeighbor, self.im32_1, self.im1_2,0)
        self.assertRaises(MambaError, diffNeighbor, self.im32_1, self.im8_2,0)
        self.assertRaises(MambaError, diffNeighbor, self.im32_1, self.im32_2,0)

    def testSizeCheck(self):
        """Tests that different sizes raise an exception"""
        self.assertRaises(MambaError, diffNeighbor, self.im8s2_1, self.im8_2,0)
        self.assertRaises(MambaError, diffNeighbor, self.im8_1, self.im8s2_2,0)
        
    def testParameterAcceptation(self):
        """Tests that incoherent parameters produce an exception"""
        for i in range(7,50):
            self.assertRaises(MambaError, diffNeighbor, self.im1_1, self.im1_2,i,grid=HEXAGONAL)
            self.assertRaises(MambaError, diffNeighbor, self.im8_1, self.im8_2,i,grid=HEXAGONAL)
            self.assertRaises(MambaError, diffNeighbor, self.im32_1, self.im32_2,i,grid=HEXAGONAL)
        for i in range(9,50):
            self.assertRaises(MambaError, diffNeighbor, self.im1_1, self.im1_2,i,grid=SQUARE)
            self.assertRaises(MambaError, diffNeighbor, self.im8_1, self.im8_2,i,grid=SQUARE)
            self.assertRaises(MambaError, diffNeighbor, self.im32_1, self.im32_2,i,grid=SQUARE)
            
    def _shiftMat(self, mat, d, fill=0):
        ret_mat = [[fill,fill,fill],[fill,fill,fill],[fill,fill,fill]]
        dx, dy = self.directions[d]
        for i in range(3):
            for j in range(3):
                if j+dy>=0 and j+dy<3 and i+dx>=0 and i+dx<3:
                    ret_mat[j][i] = mat[j+dy][i+dx]
        
        return ret_mat

    def _setDiffMat(self, mat1, mat2):
        ret_mat = [[0,0,0],[0,0,0],[0,0,0]]
        for i in range(3):
            for j in range(3):
                ret_mat[j][i] = mat1[j][i]>mat2[j][i] and mat1[j][i] or 0
        
        return ret_mat

    def _drawMat(self, im, mat, x, y):
        # draws a matrix centered in x,y
        for i in range(3):
            for j in range(3):
                im.setPixel(mat[j][i], ((x-1)+i, (y-1)+j))

    def testComputationSquare_1(self):
        """Tests set difference by neighbor computations in square grid on binary images"""
        (w,h) = self.im1_1.getSize()
        
        mat = [[1,1,1],[1,1,1],[1,1,1]]
        
        for wi in range(1,w-1):
            for d in getDirections():
                self.im1_1.reset()
                self.im1_2.reset()
                self._drawMat(self.im1_1, mat, wi, 10)
                mat_shi = self._shiftMat(mat, d)
                mat_exp = self._setDiffMat(mat, mat_shi)
                self._drawMat(self.im1_2, mat_exp, wi, 10)
                diffNeighbor(self.im1_1, self.im1_1, d, grid=SQUARE, edge=EMPTY)
                (x,y) = compare(self.im1_2, self.im1_1, self.im1_3)
                self.assert_(x<0, "in dir %d (%d,10) : at (%d,%d)" % (d,wi,x,y))
            for d in getDirections():
                self.im1_1.reset()
                self.im1_2.reset()
                self._drawMat(self.im1_1, mat, wi, 13)
                mat_shi = self._shiftMat(mat, d)
                mat_exp = self._setDiffMat(mat, mat_shi)
                self._drawMat(self.im1_2, mat_exp, wi, 13)
                diffNeighbor(self.im1_1, self.im1_1, d, grid=SQUARE, edge=EMPTY)
                (x,y) = compare(self.im1_2, self.im1_1, self.im1_3)
                self.assert_(x<0)

    def testComputationSquare_8(self):
        """Tests set difference by neighbor computations in square grid on 8-bit images"""
        (w,h) = self.im8_1.getSize()
        
        mat = [[9,2,3],[8,1,4],[7,6,5]]
        
        for wi in range(1,w-1):
            for d in getDirections():
                self.im8_1.reset()
                self.im8_2.reset()
                self._drawMat(self.im8_1, mat, wi, 10)
                mat_shi = self._shiftMat(mat, d)
                mat_exp = self._setDiffMat(mat, mat_shi)
                self._drawMat(self.im8_2, mat_exp, wi, 10)
                diffNeighbor(self.im8_1, self.im8_1, d, grid=SQUARE, edge=EMPTY)
                (x,y) = compare(self.im8_2, self.im8_1, self.im8_3)
                self.assert_(x<0)
            for d in getDirections():
                self.im8_1.reset()
                self.im8_2.reset()
                self._drawMat(self.im8_1, mat, wi, 13)
                mat_shi = self._shiftMat(mat, d)
                mat_exp = self._setDiffMat(mat, mat_shi)
                self._drawMat(self.im8_2, mat_exp, wi, 13)
                diffNeighbor(self.im8_1, self.im8_1, d, grid=SQUARE, edge=EMPTY)
                (x,y) = compare(self.im8_2, self.im8_1, self.im8_3)
                self.assert_(x<0)
                
    def _shiftMatHE(self, mat, d, fill=0):
        if d==0:
            ret_mat = mat[:]
        elif d==1:
            ret_mat = [[fill,fill,fill],mat[0][:], mat[1][1:3]+[fill]]
        elif d==2:
            ret_mat = self._shiftMat(mat, 3, fill)
        elif d==3:
            ret_mat = [mat[1][1:3]+[fill],mat[2][:],[fill,fill,fill]]
        elif d==4:
            ret_mat = [mat[1][:],[fill]+mat[2][0:2],[fill,fill,fill]]
        elif d==5:
            ret_mat = self._shiftMat(mat, 7, fill)
        elif d==6:
            ret_mat = [[fill,fill,fill],[fill]+mat[0][0:2], mat[1][:]]
        else:
            self.assert_(False, "Invalid directions in Hexagonal grid")
        
        return ret_mat
                
    def _shiftMatHO(self, mat, d, fill=0):
        if d==0:
            ret_mat = mat[:]
        elif d==1:
            ret_mat = [[fill,fill,fill],mat[0][1:3]+[fill], mat[1][:]]
        elif d==2:
            ret_mat = self._shiftMat(mat, 3, fill)
        elif d==3:
            ret_mat = [mat[1][:],mat[2][1:3]+[fill],[fill,fill,fill]]
        elif d==4:
            ret_mat = [[fill]+mat[1][0:2],mat[2][:],[fill,fill,fill]]
        elif d==5:
            ret_mat = self._shiftMat(mat, 7, fill)
        elif d==6:
            ret_mat = [[fill,fill,fill],mat[0][:], [fill]+mat[1][0:2]]
        else:
            self.assert_(False, "Invalid directions in Hexagonal grid")
        
        return ret_mat

    def testComputationHexagonal_1(self):
        """Tests set difference by neighbor computations in hexagonal grid on binary images"""
        (w,h) = self.im1_1.getSize()
        
        mat = [[1,1,1],[1,1,1],[1,1,1]]
        
        for wi in range(1,w-1):
            for d in getDirections():
                self.im1_1.reset()
                self.im1_2.reset()
                self._drawMat(self.im1_1, mat, wi, 10)
                mat_shi = self._shiftMatHE(mat, d)
                mat_exp = self._setDiffMat(mat, mat_shi)
                self._drawMat(self.im1_2, mat_exp, wi, 10)
                diffNeighbor(self.im1_1, self.im1_1, d, grid=HEXAGONAL, edge=EMPTY)
                (x,y) = compare(self.im1_2, self.im1_1, self.im1_3)
                self.assert_(x<0)
            for d in getDirections():
                self.im1_1.reset()
                self.im1_2.reset()
                self._drawMat(self.im1_1, mat, wi, 13)
                mat_shi = self._shiftMatHO(mat, d)
                mat_exp = self._setDiffMat(mat, mat_shi)
                self._drawMat(self.im1_2, mat_exp, wi, 13)
                diffNeighbor(self.im1_1, self.im1_1, d, grid=HEXAGONAL, edge=EMPTY)
                (x,y) = compare(self.im1_2, self.im1_1, self.im1_3)
                self.assert_(x<0, "(%d,10) in dir %d" %(wi,d))

    def testComputationHexagonal_8(self):
        """Tests set difference by neighbor computations in hexagonal grid on 8-bit images"""
        (w,h) = self.im8_1.getSize()
        
        mat = [[9,2,3],[8,1,4],[7,6,5]]
        
        for wi in range(1,w-1):
            for d in getDirections():
                self.im8_1.reset()
                self.im8_2.reset()
                self._drawMat(self.im8_1, mat, wi, 10)
                mat_shi = self._shiftMatHE(mat, d)
                mat_exp = self._setDiffMat(mat, mat_shi)
                self._drawMat(self.im8_2, mat_exp, wi, 10)
                diffNeighbor(self.im8_1, self.im8_1, d, grid=HEXAGONAL, edge=EMPTY)
                (x,y) = compare(self.im8_2, self.im8_1, self.im8_3)
                self.assert_(x<0)
            for d in getDirections():
                self.im8_1.reset()
                self.im8_2.reset()
                self._drawMat(self.im8_1, mat, wi, 13)
                mat_shi = self._shiftMatHO(mat, d)
                mat_exp = self._setDiffMat(mat, mat_shi)
                self._drawMat(self.im8_2, mat_exp, wi, 13)
                diffNeighbor(self.im8_1, self.im8_1, d, grid=HEXAGONAL, edge=EMPTY)
                (x,y) = compare(self.im8_2, self.im8_1, self.im8_3)
                self.assert_(x<0)
                
    def testEdgeEffect_1(self):
        """Verifies that edge value is correctly taken into account on binary image"""
        (w,h) = self.im1_1.getSize()
        exp_volume = [0, w+h/2, h, w+h/2-1, w+h/2, h, w+h/2-1]
        for d in getDirections():
            self.im1_1.fill(1)
            diffNeighbor(self.im1_1, self.im1_1, d, grid=HEXAGONAL, edge=EMPTY)
            vol = computeVolume(self.im1_1)
            self.assert_(vol==exp_volume[d], "%d : %d/%d [%d]" % (d,vol,exp_volume[d],w*h))
        exp_volume = [0, w, h+w-1, h, h+w-1, w, h+w-1, h, h+w-1]
        for d in getDirections():
            self.im1_1.fill(1)
            diffNeighbor(self.im1_1, self.im1_1, d, grid=SQUARE, edge=EMPTY)
            vol = computeVolume(self.im1_1)
            self.assert_(vol==exp_volume[d], "%d : %d/%d [%d]" % (d,vol,exp_volume[d],w*h))
                
    def testEdgeInocuity_1(self):
        """Verifies edge inocuity when computing binary image"""
        (w,h) = self.im1_1.getSize()
        for d in getDirections():
            self.im1_1.fill(0)
            diffNeighbor(self.im1_1, self.im1_1, d, grid=HEXAGONAL, edge=EMPTY)
            vol = computeVolume(self.im1_1)
            self.assert_(vol==0)
        for d in getDirections():
            self.im1_1.fill(0)
            diffNeighbor(self.im1_1, self.im1_1, d, grid=SQUARE, edge=EMPTY)
            vol = computeVolume(self.im1_1)
            self.assert_(vol==0)
        for d in getDirections():
            self.im1_1.fill(1)
            diffNeighbor(self.im1_1, self.im1_1, d, grid=HEXAGONAL, edge=FILLED)
            vol = computeVolume(self.im1_1)
            self.assert_(vol==0, "%d : %d" % (d,vol))
            self.im1_1.fill(0)
            diffNeighbor(self.im1_1, self.im1_1, d, grid=HEXAGONAL, edge=FILLED)
            vol = computeVolume(self.im1_1)
            self.assert_(vol==0)
        for d in getDirections():
            self.im1_1.fill(1)
            diffNeighbor(self.im1_1, self.im1_1, d, grid=SQUARE, edge=FILLED)
            vol = computeVolume(self.im1_1)
            self.assert_(vol==0)
            self.im1_1.fill(0)
            diffNeighbor(self.im1_1, self.im1_1, d, grid=SQUARE, edge=FILLED)
            vol = computeVolume(self.im1_1)
            self.assert_(vol==0)
                
    def testEdgeEffect_8(self):
        """Verifies that edge value is correctly taken into account on 8-bit image"""
        (w,h) = self.im8_1.getSize()
        exp_volume = [0, w+h/2, h, w+h/2-1, w+h/2, h, w+h/2-1]
        for d in getDirections():
            self.im8_1.fill(255)
            diffNeighbor(self.im8_1, self.im8_1, d, grid=HEXAGONAL, edge=EMPTY)
            vol = computeVolume(self.im8_1)
            self.assert_(vol/255==exp_volume[d], "%d : %d/%d [%d]" % (d,vol,exp_volume[d],w*h))
        exp_volume = [0, w, h+w-1, h, w+h-1, w, w+h-1, h, h+w-1]
        for d in getDirections():
            self.im8_1.fill(255)
            diffNeighbor(self.im8_1, self.im8_1, d, grid=SQUARE, edge=EMPTY)
            vol = computeVolume(self.im8_1)
            self.assert_(vol/255==exp_volume[d], "%d : %d/%d [%d]" % (d,vol,exp_volume[d],w*h))
                
    def testEdgeInocuity_8(self):
        """Verifies edge inocuity when computing 8-bit image"""
        (w,h) = self.im8_1.getSize()
        for d in getDirections():
            self.im8_1.fill(0)
            diffNeighbor(self.im8_1, self.im8_1, d, grid=HEXAGONAL, edge=EMPTY)
            vol = computeVolume(self.im8_1)
            self.assert_(vol==0)
        for d in getDirections():
            self.im8_1.fill(0)
            diffNeighbor(self.im8_1, self.im8_1, d, grid=SQUARE, edge=EMPTY)
            vol = computeVolume(self.im8_1)
            self.assert_(vol==0)
        for d in getDirections():
            self.im8_1.fill(255)
            diffNeighbor(self.im8_1, self.im8_1, d, grid=HEXAGONAL, edge=FILLED)
            vol = computeVolume(self.im8_1)
            self.assert_(vol==0)
            self.im8_1.fill(0)
            diffNeighbor(self.im8_1, self.im8_1, d, grid=HEXAGONAL, edge=FILLED)
            vol = computeVolume(self.im8_1)
            self.assert_(vol==0)
        for d in getDirections():
            self.im8_1.fill(255)
            diffNeighbor(self.im8_1, self.im8_1, d, grid=SQUARE, edge=FILLED)
            vol = computeVolume(self.im8_1)
            self.assert_(vol==0)
            self.im8_1.fill(0)
            diffNeighbor(self.im8_1, self.im8_1, d, grid=SQUARE, edge=FILLED)
            vol = computeVolume(self.im8_1)
            self.assert_(vol==0)


def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestDiffNb)
    
if __name__ == '__main__':
    unittest.main()
