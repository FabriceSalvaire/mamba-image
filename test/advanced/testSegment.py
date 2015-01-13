"""
Test cases for the segmentation (watershed based) functions found in the segment
module of mambaComposed package.

Python functions and classes:
    markerControlledWatershed
    valuedWatershed
    fastSKIZ
    geodesicSKIZ
    mosaic
    mosaicGradient
    watershedSegment32
    basinSegment32
"""

from mamba import *
from mambaDraw import *
from mambaComposed import *
import unittest
import random

class TestSegment(unittest.TestCase):

    def setUp(self):
        self.im1_1 = imageMb(1)
        self.im1_2 = imageMb(1)
        self.im1_3 = imageMb(1)
        self.im1_4 = imageMb(1)
        self.im8_1 = imageMb(8)
        self.im8_2 = imageMb(8)
        self.im8_3 = imageMb(8)
        self.im8_4 = imageMb(8)
        self.im8_5 = imageMb(8)
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
        del(self.im8_5)
        del(self.im32_1)
        del(self.im32_2)
        del(self.im32_3)
        del(self.im32_4)
        if getImageCounter()!=0:
            print "ERROR : Mamba image are not all deleted !"
            
    def _drawWells(self, imOut, wall=[1,2,3,4]):
        (w,h) = imOut.getSize()
        
        imOut.reset()
        if wall.count(1)>0:
            drawLine(imOut, (w/2,0,w/2,h/2), 20)
        if wall.count(2)>0:
            drawLine(imOut, (0,h/2,w/2,h/2), 40)
        if wall.count(3)>0:
            drawLine(imOut, (w/2,h/2+1,w/2,h-1), 60)
        if wall.count(4)>0:
            drawLine(imOut, (w/2+1,h/2,w-1,h/2), 80)
        imOut.setPixel(255, (w/2,h/2))
        
    def testMarkerControlledWatershed(self):
        """Verifies the marker controlled valued watershed computation"""
        (w,h) = self.im8_1.getSize()
        
        self._drawWells(self.im8_1)
        
        self.im1_1.reset()
        self.im1_1.setPixel(1, (3*w/4,h/4))
        self.im1_1.setPixel(1, (w/4,h/4))
        self.im1_1.setPixel(1, (w/4,3*h/4))
        self.im1_1.setPixel(1, (3*w/4,3*h/4))
        markerControlledWatershed(self.im8_1, self.im1_1, self.im8_2, SQUARE)
        (x,y) = compare(self.im8_1, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
        self.im1_1.reset()
        self.im1_1.setPixel(1, (3*w/4,h/4))
        self.im1_1.setPixel(1, (w/4,h/4))
        self._drawWells(self.im8_3, wall=[1,4])
        markerControlledWatershed(self.im8_1, self.im1_1, self.im8_2, SQUARE)
        (x,y) = compare(self.im8_3, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
        self.im1_1.reset()
        self.im1_1.setPixel(1, (w/4,h/4))
        self.im1_1.setPixel(1, (3*w/4,3*h/4))
        self._drawWells(self.im8_3, wall=[3,4])
        markerControlledWatershed(self.im8_1, self.im1_1, self.im8_2, SQUARE)
        (x,y) = compare(self.im8_3, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
        self.im1_1.reset()
        self.im1_1.setPixel(1, (w/4,h/4))
        self.im1_1.setPixel(1, (w/4,3*h/4))
        self._drawWells(self.im8_3, wall=[2,4])
        markerControlledWatershed(self.im8_1, self.im1_1, self.im8_2, SQUARE)
        (x,y) = compare(self.im8_3, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
        self.im1_1.reset()
        self.im1_1.setPixel(1, (3*w/4,h/4))
        self.im1_1.setPixel(1, (3*w/4,3*h/4))
        self._drawWells(self.im8_3, wall=[3,4])
        markerControlledWatershed(self.im8_1, self.im1_1, self.im8_2, SQUARE)
        (x,y) = compare(self.im8_3, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
        self.im1_1.reset()
        self.im1_1.setPixel(1, (w/4,3*h/4))
        self.im1_1.setPixel(1, (3*w/4,3*h/4))
        self._drawWells(self.im8_3, wall=[3,4])
        markerControlledWatershed(self.im8_1, self.im1_1, self.im8_2, SQUARE)
        (x,y) = compare(self.im8_3, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
        self.im1_1.reset()
        self.im1_1.setPixel(1, (3*w/4,h/4))
        self.im1_1.setPixel(1, (w/4,3*h/4))
        self._drawWells(self.im8_3, wall=[2,4])
        markerControlledWatershed(self.im8_1, self.im1_1, self.im8_2, SQUARE)
        (x,y) = compare(self.im8_3, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
        self.im1_1.reset()
        self.im1_1.setPixel(1, (3*w/4,h/4))
        self.im1_1.setPixel(1, (w/4,h/4))
        self.im1_1.setPixel(1, (3*w/4,3*h/4))
        self._drawWells(self.im8_3, wall=[1,3,4])
        markerControlledWatershed(self.im8_1, self.im1_1, self.im8_2, SQUARE)
        (x,y) = compare(self.im8_3, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
        self.im1_1.reset()
        self.im1_1.setPixel(1, (3*w/4,h/4))
        self.im1_1.setPixel(1, (w/4,3*h/4))
        self.im1_1.setPixel(1, (3*w/4,3*h/4))
        self._drawWells(self.im8_3, wall=[2,3,4])
        markerControlledWatershed(self.im8_1, self.im1_1, self.im8_2, SQUARE)
        (x,y) = compare(self.im8_3, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
        self.im1_1.reset()
        self.im1_1.setPixel(1, (3*w/4,h/4))
        self.im1_1.setPixel(1, (w/4,h/4))
        self.im1_1.setPixel(1, (w/4,3*h/4))
        self._drawWells(self.im8_3, wall=[1,2,4])
        markerControlledWatershed(self.im8_1, self.im1_1, self.im8_2, SQUARE)
        (x,y) = compare(self.im8_3, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
        self.im1_1.reset()
        self.im1_1.setPixel(1, (w/4,h/4))
        self.im1_1.setPixel(1, (w/4,3*h/4))
        self.im1_1.setPixel(1, (3*w/4,3*h/4))
        self._drawWells(self.im8_3, wall=[2,3,4])
        markerControlledWatershed(self.im8_1, self.im1_1, self.im8_2, SQUARE)
        (x,y) = compare(self.im8_3, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
    def testValuedWatershed(self):
        """Verifies the minima controlled valued watershed computation"""
        (w,h) = self.im8_1.getSize()
        
        self._drawWells(self.im8_1)
        
        valuedWatershed(self.im8_1,self.im8_2, SQUARE)
        (x,y) = compare(self.im8_1, self.im8_2, self.im8_3)
        self.assert_(x<0)
        
    def testFastSKIZ(self):
        """Verifies the fast SKIZ operator based on watershed"""
        (w,h) = self.im1_1.getSize()
        
        self.im1_1.reset()
        self.im1_1.setPixel(1, (3*w/4,h/4))
        self.im1_1.setPixel(1, (w/4,h/4))
        self.im1_1.setPixel(1, (w/4,3*h/4))
        self.im1_1.setPixel(1, (3*w/4,3*h/4))
        self.im1_3.fill(1)
        drawLine(self.im1_3, (w/2,0,w/2,h-1), 0)
        drawLine(self.im1_3, (0,h/2,w-1,h/2), 0)
        fastSKIZ(self.im1_1, self.im1_2, SQUARE)
        (x,y) = compare(self.im1_3, self.im1_2, self.im1_3)
        self.assert_(x<0)
        
    def testGeodesicSKIZ(self):
        """Verifies the geodesic SKIZ operator based on watershed"""
        (w,h) = self.im1_1.getSize()
        
        self.im1_1.reset()
        self.im1_1.setPixel(1, (3*w/4,h/4))
        self.im1_1.setPixel(1, (w/4,h/4))
        self.im1_1.setPixel(1, (w/4,3*h/4))
        self.im1_1.setPixel(1, (3*w/4,3*h/4))
        self.im1_4.reset()
        drawSquare(self.im1_4, (5,5,w-6,h/2-6), 1)
        drawSquare(self.im1_4, (5,h/2+5,w-6,h-6), 1)
        drawSquare(self.im1_4, (w/2+5,5,w-6,h-6), 1)
        copy(self.im1_4, self.im1_3)
        drawLine(self.im1_3, (w/2,0,w/2,h-1), 0)
        drawLine(self.im1_3, (0,h/2,w-1,h/2), 0)
        geodesicSKIZ(self.im1_1, self.im1_4, self.im1_2, SQUARE)
        (x,y) = compare(self.im1_3, self.im1_2, self.im1_3)
        self.assert_(x<0)
        
    def _drawSquares(self, imOut):
        (w,h) = imOut.getSize()
        
        for i in range(w/4):
            drawSquare(imOut, (i,i,w-1-i,h-1-i), i+1)
        for i in range(w/4):
            drawSquare(imOut, (i+w/4,i+w/4,w-1-i-w/4,h-1-i-w/4), w/2+i*2)
        
    def testMosaic(self):
        """Verifies the computation of mosaic image using watershed segment"""
        (w,h) = self.im8_1.getSize()
        
        self._drawSquares(self.im8_1)
        mosaic(self.im8_1, self.im8_2, self.im8_3, SQUARE)
            
        self.im8_5.fill(1)
        drawSquare(self.im8_5, (w/4,w/4+1,w-2-w/4,h-1-w/4), w-2)
        (x,y) = compare(self.im8_2, self.im8_5, self.im8_5)
        self.assert_(x<0)
        self.im8_5.reset()
        drawBox(self.im8_5, (w/4,w/4,w-1-w/4,h-1-w/4), 255)
        (x,y) = compare(self.im8_3, self.im8_5, self.im8_5)
        self.assert_(x<0)
        
        mosaic(self.im8_1, self.im8_1, self.im8_3, SQUARE)
            
        self.im8_5.fill(1)
        drawSquare(self.im8_5, (w/4,w/4+1,w-2-w/4,h-1-w/4), w-2)
        (x,y) = compare(self.im8_1, self.im8_5, self.im8_5)
        self.assert_(x<0)
        
    def testMosaicGradient(self):
        """Verifies the computation of mosaic gradient using watershed segment"""
        (w,h) = self.im8_1.getSize()
        
        self._drawSquares(self.im8_1)
        mosaicGradient(self.im8_1, self.im8_2, SQUARE)
            
        self.im8_5.reset()
        drawBox(self.im8_5, (w/4,w/4,w-1-w/4,h-1-w/4), w-3)
        (x,y) = compare(self.im8_2, self.im8_5, self.im8_5)
        self.assert_(x<0)
        
        mosaicGradient(self.im8_1, self.im8_1, SQUARE)
            
        self.im8_5.reset()
        drawBox(self.im8_5, (w/4,w/4,w-1-w/4,h-1-w/4), w-3)
        (x,y) = compare(self.im8_1, self.im8_5, self.im8_5)
        self.assert_(x<0)
        
        # Doesn't test anything just here to enter the mosaicGradient while
        # loop and make sure everything is ok inside
        for i in range(w):
            for j in range(h):
                self.im8_1.fastSetPixel(random.randint(0,255), (i,j))
        mosaicGradient(self.im8_1, self.im8_1)
        
    def testWatershedSegment32Square(self):
        """Verifies the 32-bit watershed segment operator with SQUARE grid"""
        (w,h) = self.im32_1.getSize()
        
        for i in range(w/4,(3*w)/4):
            # creating a wall image
            self.im32_1.reset()
            self.im8_1.reset()
            for hi in range(h):
                self.im32_1.setPixel(127*(i-w/4+1), (i,hi))
                self.im8_1.setPixel(255, (i,hi))
                
            exp_vol = (i*50+(w-1-i)*100)*h
            exp_vol1 = exp_vol+50*h
            exp_vol2 = exp_vol+100*h
                    
            # adding 2 well
            self.im32_2.reset()
            self.im32_2.setPixel(50, (w/4-1,h/2))
            self.im32_2.setPixel(100, ((3*w)/4,h/2))
            
            if i%4==0:
                level = 127*(i-w/4+1)+1
                watershedSegment32(self.im32_1, self.im32_2, max_level=level, grid=SQUARE)
                copyBytePlane(self.im32_2, 3, self.im8_2)
                (x,y) = compare(self.im8_1, self.im8_2, self.im8_3)
                self.assert_(x<0, "wall at %d [%d,%d]: %d,%d" %(i,w/4,(3*w)/4,x,y))
            elif i%4==1:
                level = -1
                watershedSegment32(self.im32_1, self.im32_2, max_level=level, grid=SQUARE)
                copyBytePlane(self.im32_2, 3, self.im8_2)
                (x,y) = compare(self.im8_1, self.im8_2, self.im8_3)
                self.assert_(x<0, "wall at %d [%d,%d]: %d,%d" %(i,w/4,(3*w)/4,x,y))
            elif i%4==2:
                level = 128
                watershedSegment32(self.im32_1, self.im32_2, max_level=level, grid=SQUARE)
                copyBytePlane(self.im32_2, 0, self.im8_2)
                vol = computeVolume(self.im8_2)
                self.assert_(exp_vol==vol)
                copyBytePlane(self.im32_2, 3, self.im8_2)
                (x,y) = compare(self.im8_1, self.im8_2, self.im8_3)
                self.assert_(x>0)
            else:
                level = 384
                watershedSegment32(self.im32_1, self.im32_2, max_level=level, grid=SQUARE)
                copyBytePlane(self.im32_2, 0, self.im8_2)
                vol = computeVolume(self.im8_2)
                self.assert_(exp_vol==vol)
                copyBytePlane(self.im32_2, 3, self.im8_2)
                (x,y) = compare(self.im8_1, self.im8_2, self.im8_3)
                self.assert_(x>0)

    def testWatershedSegment32Hexagonal(self):
        """Verifies the 32-bit watershed segment operator with HEXAGONAL grid"""
        (w,h) = self.im32_1.getSize()
        
        for i in range(w/4,(3*w)/4):
            # creating a wall image
            self.im32_1.reset()
            self.im8_1.reset()
            for hi in range(h):
                self.im32_1.setPixel(5000, (i,hi))
                self.im8_1.setPixel(255, (i,hi))
                    
            # adding 2 well
            self.im32_2.reset()
            self.im32_2.setPixel(50, (w/4-1,h/2))
            self.im32_2.setPixel(100, ((3*w)/4,h/2))
            
            if i%2==0:
                level = 5001
            else:
                level = -1
            watershedSegment32(self.im32_1, self.im32_2, max_level=level, grid=HEXAGONAL)
            copyBytePlane(self.im32_2, 3, self.im8_2)
            (x,y) = compare(self.im8_1, self.im8_2, self.im8_3)
            self.assert_(x<0, "wall at %d [%d,%d]: %d,%d" %(i,w/4,(3*w)/4,x,y))
            
    def _draw(self,im,draws,x,y):
        for j,line in enumerate(draws):
            for i,pixel in enumerate(line):
                im.setPixel(pixel, (x+i,y+j))
                
    def _get(self,im,x,y,w,h):
        draws = []
        for j in range(h):
            line = []
            for i in range(w):
                line.append(im.getPixel((x+i,y+j)))
            draws.append(line)
        return draws
        
    def testWatershedSegment32ButtonHole(self):
        """Tests that the watershed 32-bit is correctly computed in a button hole"""
        (w,h) = self.im32_1.getSize()

        for i in range(4):
            self.im32_1.fill(7)
            self._draw(self.im32_1, [[2,2,2,2,2,2],
                                    [7,7,7,7,7,7],
                                    [2,7,5,6,2,2],
                                    [2,6,5,6,2,2],
                                    [2,2,6,4,3,2],
                                    [2,2,3,4,2,2],
                                    [2,2,2,2,4,2]], w/2, h/2)
            mulConst(self.im32_1, random.randint(20,105), self.im32_1)
            self.im32_2.reset()
            self._draw(self.im32_2,[[1,1,1,1,1,1],
                                    [0,0,0,0,0,0],
                                    [2,0,0,0,3,3],
                                    [2,0,0,0,3,3],
                                    [2,2,0,0,0,3],
                                    [2,2,0,0,3,3],
                                    [2,2,2,2,0,3]], w/2, h/2)
            
            watershedSegment32(self.im32_1, self.im32_2, grid=HEXAGONAL)
            copyBytePlane(self.im32_2, 3, self.im8_2)
            obt_draws = self._get(self.im8_2, w/2, h/2, 6, 7)
            exp_draws = [[0,0,0,0,0,0],
                         [255,0,255,255,255,255],
                         [0,255,255,0,0,0],
                         [0,0,255,0,0,0],
                         [0,0,0,255,0,0],
                         [0,0,0,255,0,0],
                         [0,0,0,0,255,0]]
            self.assert_(obt_draws==exp_draws, "%s!=%s" % (str(obt_draws), str(exp_draws)))
            copyBytePlane(self.im32_2, 0, self.im8_2)
            obt_draws = self._get(self.im8_2, w/2, h/2, 6, 7)
            exp_draws = [[1,1,1,1,1,1],
                         [1,1,1,1,1,1],
                         [2,1,3,3,3,3],
                         [2,2,3,3,3,3],
                         [2,2,2,3,3,3],
                         [2,2,2,3,3,3],
                         [2,2,2,2,3,3]]
            self.assert_(obt_draws==exp_draws, "%s!=%s" % (str(obt_draws), str(exp_draws)))
            
    def testWatershedSegment32ThickWTS(self):
        """Tests that thick watershed are correctly computed by the 32-bit operator"""
        (w,h) = self.im32_1.getSize()
        
        for i in range(4):
            self.im32_1.fill(6)
            self._draw(self.im32_1, [[2,6,2,6,2],
                                     [2,2,6,6,2],
                                     [6,6,6,6,6],
                                     [2,2,6,6,2],
                                     [2,6,2,6,2]], w/2, h/2+1)
            mulConst(self.im32_1, random.randint(20,105), self.im32_1)
            self.im32_2.reset()
            self._draw(self.im32_2, [[1,0,2,0,3],
                                     [1,1,0,0,3],
                                     [0,0,0,0,0],
                                     [4,4,0,0,5],
                                     [4,0,6,0,5]], w/2, h/2+1)
            
            watershedSegment32(self.im32_1, self.im32_2, grid=HEXAGONAL)
            copyBytePlane(self.im32_2, 3, self.im8_2)
            obt_draws = self._get(self.im8_2, w/2, h/2+1, 5, 5)
            exp_draws = [[0,255,0,255,0],[0,0,255,255,0],[255,255,255,255,255],[0,0,255,255,0],[0,255,0,255,0]]
            self.assert_(obt_draws==exp_draws, "%s!=%s" % (str(obt_draws), str(exp_draws)))
            
    def testBasinSegment32Square(self):
        """Verifies the 32-bit basin segment operator with SQUARE grid"""
        (w,h) = self.im32_1.getSize()
        
        for i in range(w/4,(3*w)/4):
            # creating a wall image
            self.im32_1.reset()
            for hi in range(h):
                self.im32_1.setPixel(127*(i-w/4+1), (i,hi))
                
            exp_vol = (i*50+(w-1-i)*100)*h
            exp_vol1 = exp_vol+50*h
            exp_vol2 = exp_vol+100*h
                    
            # adding 2 well
            self.im32_2.reset()
            self.im32_2.setPixel(50, (w/4-1,h/2))
            self.im32_2.setPixel(100, ((3*w)/4,h/2))
            
            if i%4==0:
                level = 127*(i-w/4+1)+1
            elif i%4==1:
                level = -1
            elif i%4==2:
                level = 128
            else:
                level = 384
            basinSegment32(self.im32_1, self.im32_2, max_level=level, grid=SQUARE)
            copyBytePlane(self.im32_2, 0, self.im8_2)
            vol = computeVolume(self.im8_2)
            self.assert_(exp_vol1<=vol and exp_vol2>=vol, "wall at %d [%d,%d]: %d/%d/%d" %(i,w/4,(3*w)/4,vol,exp_vol1,exp_vol2))
            
    def testBasinSegment32Hexagonal(self):
        """Verifies the 32-bit basin segment operator with HEXAGONAL grid"""
        (w,h) = self.im32_1.getSize()
        
        for i in range(w/4,(3*w)/4):
            # creating a wall image
            self.im32_1.reset()
            for hi in range(h):
                self.im32_1.setPixel(5000, (i,hi))
                
            exp_vol = (i*50+(w-1-i)*100)*h
            exp_vol1 = exp_vol+50*h
            exp_vol2 = exp_vol+100*h
                    
            # adding 2 well
            self.im32_2.reset()
            self.im32_2.setPixel(50, (w/4-1,h/2))
            self.im32_2.setPixel(100, ((3*w)/4,h/2))
            
            if i%2==0:
                level = 5001
            else:
                level = -1
            basinSegment32(self.im32_1, self.im32_2, max_level=level, grid=HEXAGONAL)
            copyBytePlane(self.im32_2, 0, self.im8_2)
            vol = computeVolume(self.im8_2)
            self.assert_(exp_vol1<=vol and exp_vol2>=vol, "wall at %d [%d,%d]: %d/%d/%d" %(i,w/4,(3*w)/4,vol,exp_vol1,exp_vol2))

def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestSegment)
    
if __name__ == '__main__':
    unittest.main()
