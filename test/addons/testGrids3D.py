"""
Test cases for the grids facilities classes and functions found in the
grids3D module of mamba3D package.

Python functions and classes:
    _grid3D
    _gridFCCubic3D
    _gridCCubic3D
    _gridCubic3D
    _gridDefault3D
    setDefaultGrid3D
    getDirections3D
    gridNeighbors3D
    transposeDirection3D
"""

from mamba import *
from mambaDraw import *
from mamba3D import *
import unittest
import random

class TestGrids3D(unittest.TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def testDummyGrid(self):
        """Verifies the dummy grid class"""
        grid = grids3D._grid3D()
        
        self.assert_(grid.convertFromDir(1, 1)==(0,0))
        self.assert_(grid.get2DGrid()==HEXAGONAL)
        self.assert_(grid.getTranDir(15)==15)
        self.assert_(grid.getZExtension()==0)
        self.assert_(grid.getDirections()==[])
        self.assert_(grid.maxNeighbors()==0)
        self.assert_(grid.getCValue()==core3D.MB3D_INVALID_GRID)
        self.assert_(repr(grid)=="mamba3D.3D_GRID_NAME")
        
    def testFCCubicGrid(self):
        """Verifies the face center cubic grid"""
        grid = FACE_CENTER_CUBIC
        
        self.assert_(grid.convertFromDir(1, 0)==(0,1))
        self.assert_(grid.convertFromDir(1, 1)==(0,1))
        self.assert_(grid.convertFromDir(1, 2)==(0,1))
        self.assert_(grid.convertFromDir(7, 0)==(-1,0))
        self.assert_(grid.convertFromDir(7, 1)==(-1,3))
        self.assert_(grid.convertFromDir(7, 2)==(-1,2))
        self.assertRaises(MambaError,grid.convertFromDir,13,0)
        self.assert_(grid.get2DGrid()==HEXAGONAL)
        self.assert_(grid.getTranDir(1)==4)
        self.assert_(grid.getTranDir(7)==10)
        self.assert_(grid.getTranDir(8)==11)
        self.assert_(grid.getTranDir(9)==12)
        self.assert_(grid.getZExtension()==1)
        self.assert_(grid.getDirections()==range(13))
        self.assert_(grid.maxNeighbors()==12)
        self.assert_(grid.getCValue()==core3D.MB3D_FCC_GRID)
        self.assert_(repr(grid)=="mamba3D.FACE_CENTER_CUBIC")
        
    def testCCubicGrid(self):
        """Verifies the center cubic grid"""
        grid = CENTER_CUBIC
        
        self.assert_(grid.convertFromDir(1, 0)==(0,1))
        self.assert_(grid.convertFromDir(1, 1)==(0,1))
        self.assert_(grid.convertFromDir(1, 2)==(0,1))
        self.assert_(grid.convertFromDir(9, 0)==(-1,0))
        self.assert_(grid.convertFromDir(9, 1)==(-1,4))
        self.assert_(grid.convertFromDir(9, 2)==(-1,0))
        self.assertRaises(MambaError,grid.convertFromDir,17,0)
        self.assert_(grid.get2DGrid()==SQUARE)
        self.assert_(grid.getTranDir(0)==0)
        self.assert_(grid.getTranDir(1)==5)
        self.assert_(grid.getTranDir(9)==13)
        self.assert_(grid.getTranDir(10)==14)
        self.assert_(grid.getTranDir(15)==11)
        self.assert_(grid.getTranDir(12)==16)
        self.assert_(grid.getZExtension()==1)
        self.assert_(grid.getDirections()==range(17))
        self.assert_(grid.maxNeighbors()==16)
        self.assert_(grid.getCValue()==core3D.MB3D_INVALID_GRID)
        self.assert_(repr(grid)=="mamba3D.CENTER_CUBIC")
        
    def testCubicGrid(self):
        """Verifies the cubic grid"""
        grid = CUBIC
        
        for i in range(27):
            if i>=18:
                res = (1,i-18)
            elif i>=9:
                res = (-1,i-9)
            else:
                res = (0,i)
            self.assert_(grid.convertFromDir(i, 0)==res)
            self.assert_(grid.convertFromDir(i, 1)==res)
            self.assert_(grid.convertFromDir(i, 2)==res)
        self.assertRaises(MambaError,grid.convertFromDir,27,0)
        self.assert_(grid.get2DGrid()==SQUARE)
        self.assert_(grid.getTranDir(1)==5)
        self.assert_(grid.getTranDir(9)==18)
        self.assert_(grid.getTranDir(14)==19)
        self.assert_(grid.getZExtension()==1)
        self.assert_(grid.getDirections()==range(27))
        self.assert_(grid.maxNeighbors()==26)
        self.assert_(grid.getCValue()==core3D.MB3D_CUBIC_GRID)
        self.assert_(repr(grid)=="mamba3D.CUBIC")
        
    def testDefaultGrid(self):
        """Verifies the default grid"""
        grid = DEFAULT_GRID3D
        
        self.assert_(grid.convertFromDir(1, 0)==(0,1))
        self.assert_(grid.convertFromDir(1, 1)==(0,1))
        self.assert_(grid.convertFromDir(1, 2)==(0,1))
        self.assert_(grid.convertFromDir(7, 0)==(-1,0))
        self.assert_(grid.convertFromDir(7, 1)==(-1,3))
        self.assert_(grid.convertFromDir(7, 2)==(-1,2))
        self.assert_(grid.get2DGrid()==HEXAGONAL)
        self.assert_(grid.getTranDir(1)==4)
        self.assert_(grid.getTranDir(7)==10)
        self.assert_(grid.getTranDir(8)==11)
        self.assert_(grid.getTranDir(9)==12)
        self.assert_(grid.getZExtension()==1)
        self.assert_(grid.getDirections()==range(13))
        self.assert_(grid.maxNeighbors()==12)
        self.assert_(grid.getCValue()==core3D.MB3D_FCC_GRID)
        self.assert_(repr(grid)=="mamba3D.DEFAULT_GRID3D")
        
    def testSetDefaultGrid3D(self):
        """Verifies that modification of the default 3D grid works"""
        setDefaultGrid3D(0)
        setDefaultGrid3D(CUBIC)
        grid = DEFAULT_GRID3D
        
        for i in range(27):
            if i>=18:
                res = (1,i-18)
            elif i>=9:
                res = (-1,i-9)
            else:
                res = (0,i)
            self.assert_(grid.convertFromDir(i, 0)==res)
            self.assert_(grid.convertFromDir(i, 1)==res)
            self.assert_(grid.convertFromDir(i, 2)==res)
        self.assert_(grid.get2DGrid()==SQUARE)
        self.assert_(grid.getTranDir(1)==5)
        self.assert_(grid.getTranDir(9)==18)
        self.assert_(grid.getTranDir(14)==19)
        self.assert_(grid.getZExtension()==1)
        self.assert_(grid.getDirections()==range(27))
        self.assert_(grid.maxNeighbors()==26)
        self.assert_(grid.getCValue()==core3D.MB3D_CUBIC_GRID)
        self.assert_(repr(grid)=="mamba3D.DEFAULT_GRID3D")
        
        setDefaultGrid3D(FACE_CENTER_CUBIC)
        
    def testGetDirections3D(self):
        """Verifies that the directions are correctly returned"""
        dirs = getDirections3D(CUBIC)
        self.assert_(dirs==range(27))
        dirs = getDirections3D(CENTER_CUBIC)
        self.assert_(dirs==range(17))
        dirs = getDirections3D(FACE_CENTER_CUBIC)
        self.assert_(dirs==range(13))
        dirs = getDirections3D(0)
        self.assert_(dirs==[])
        
    def testGridNeighbors3D(self):
        """Verifies that the number of neighbor are correctly returned"""
        nb = gridNeighbors3D(CUBIC)
        self.assert_(nb==26)
        nb = gridNeighbors3D(CENTER_CUBIC)
        self.assert_(nb==16)
        nb = gridNeighbors3D(FACE_CENTER_CUBIC)
        self.assert_(nb==12)
        nb = gridNeighbors3D(0)
        self.assert_(nb==0)
    
    def testTransposeDirection3D(self):
        """Verifies that the direction transposition"""
        d = transposeDirection3D(7)
        self.assert_(d==10)
        
def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestGrids3D)
    
if __name__ == '__main__':
    unittest.main()
