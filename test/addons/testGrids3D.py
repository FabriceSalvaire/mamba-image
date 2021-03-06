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
        
        self.assertTrue(grid.convertFromDir(1, 1)==(0,0))
        self.assertTrue(grid.get2DGrid()==HEXAGONAL)
        self.assertTrue(grid.getTranDir(15)==15)
        self.assertTrue(grid.getZExtension()==0)
        self.assertTrue(grid.getDirections()==[])
        self.assertTrue(grid.maxNeighbors()==0)
        self.assertTrue(grid.getCValue()==core3D.MB3D_INVALID_GRID)
        self.assertTrue(repr(grid)=="mamba3D.3D_GRID_NAME")
        
    def testFCCubicGrid(self):
        """Verifies the face center cubic grid"""
        grid = FACE_CENTER_CUBIC
        
        self.assertTrue(grid.convertFromDir(1, 0)==(0,1))
        self.assertTrue(grid.convertFromDir(1, 1)==(0,1))
        self.assertTrue(grid.convertFromDir(1, 2)==(0,1))
        self.assertTrue(grid.convertFromDir(7, 0)==(-1,0))
        self.assertTrue(grid.convertFromDir(7, 1)==(-1,3))
        self.assertTrue(grid.convertFromDir(7, 2)==(-1,2))
        self.assertRaises(MambaError,grid.convertFromDir,13,0)
        self.assertTrue(grid.get2DGrid()==HEXAGONAL)
        self.assertTrue(grid.getTranDir(1)==4)
        self.assertTrue(grid.getTranDir(7)==10)
        self.assertTrue(grid.getTranDir(8)==11)
        self.assertTrue(grid.getTranDir(9)==12)
        self.assertTrue(grid.getZExtension()==1)
        self.assertTrue(grid.getDirections()==list(range(13)))
        self.assertTrue(grid.maxNeighbors()==12)
        self.assertTrue(grid.getCValue()==core3D.MB3D_FCC_GRID)
        self.assertTrue(repr(grid)=="mamba3D.FACE_CENTER_CUBIC")
        
    def testCCubicGrid(self):
        """Verifies the center cubic grid"""
        grid = CENTER_CUBIC
        
        self.assertTrue(grid.convertFromDir(1, 0)==(0,1))
        self.assertTrue(grid.convertFromDir(1, 1)==(0,1))
        self.assertTrue(grid.convertFromDir(1, 2)==(0,1))
        self.assertTrue(grid.convertFromDir(9, 0)==(-1,0))
        self.assertTrue(grid.convertFromDir(9, 1)==(-1,4))
        self.assertTrue(grid.convertFromDir(9, 2)==(-1,0))
        self.assertRaises(MambaError,grid.convertFromDir,17,0)
        self.assertTrue(grid.get2DGrid()==SQUARE)
        self.assertTrue(grid.getTranDir(0)==0)
        self.assertTrue(grid.getTranDir(1)==5)
        self.assertTrue(grid.getTranDir(9)==13)
        self.assertTrue(grid.getTranDir(10)==14)
        self.assertTrue(grid.getTranDir(15)==11)
        self.assertTrue(grid.getTranDir(12)==16)
        self.assertTrue(grid.getZExtension()==1)
        self.assertTrue(grid.getDirections()==list(range(17)))
        self.assertTrue(grid.maxNeighbors()==16)
        self.assertTrue(grid.getCValue()==core3D.MB3D_INVALID_GRID)
        self.assertTrue(repr(grid)=="mamba3D.CENTER_CUBIC")
        
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
            self.assertTrue(grid.convertFromDir(i, 0)==res)
            self.assertTrue(grid.convertFromDir(i, 1)==res)
            self.assertTrue(grid.convertFromDir(i, 2)==res)
        self.assertRaises(MambaError,grid.convertFromDir,27,0)
        self.assertTrue(grid.get2DGrid()==SQUARE)
        self.assertTrue(grid.getTranDir(1)==5)
        self.assertTrue(grid.getTranDir(9)==18)
        self.assertTrue(grid.getTranDir(14)==19)
        self.assertTrue(grid.getZExtension()==1)
        self.assertTrue(grid.getDirections()==list(range(27)))
        self.assertTrue(grid.maxNeighbors()==26)
        self.assertTrue(grid.getCValue()==core3D.MB3D_CUBIC_GRID)
        self.assertTrue(repr(grid)=="mamba3D.CUBIC")
        
    def testDefaultGrid(self):
        """Verifies the default grid"""
        grid = DEFAULT_GRID3D
        
        self.assertTrue(grid.convertFromDir(1, 0)==(0,1))
        self.assertTrue(grid.convertFromDir(1, 1)==(0,1))
        self.assertTrue(grid.convertFromDir(1, 2)==(0,1))
        self.assertTrue(grid.convertFromDir(7, 0)==(-1,0))
        self.assertTrue(grid.convertFromDir(7, 1)==(-1,3))
        self.assertTrue(grid.convertFromDir(7, 2)==(-1,2))
        self.assertTrue(grid.get2DGrid()==HEXAGONAL)
        self.assertTrue(grid.getTranDir(1)==4)
        self.assertTrue(grid.getTranDir(7)==10)
        self.assertTrue(grid.getTranDir(8)==11)
        self.assertTrue(grid.getTranDir(9)==12)
        self.assertTrue(grid.getZExtension()==1)
        self.assertTrue(grid.getDirections()==list(range(13)))
        self.assertTrue(grid.maxNeighbors()==12)
        self.assertTrue(grid.getCValue()==core3D.MB3D_FCC_GRID)
        self.assertTrue(repr(grid)=="mamba3D.DEFAULT_GRID3D")
        
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
            self.assertTrue(grid.convertFromDir(i, 0)==res)
            self.assertTrue(grid.convertFromDir(i, 1)==res)
            self.assertTrue(grid.convertFromDir(i, 2)==res)
        self.assertTrue(grid.get2DGrid()==SQUARE)
        self.assertTrue(grid.getTranDir(1)==5)
        self.assertTrue(grid.getTranDir(9)==18)
        self.assertTrue(grid.getTranDir(14)==19)
        self.assertTrue(grid.getZExtension()==1)
        self.assertTrue(grid.getDirections()==list(range(27)))
        self.assertTrue(grid.maxNeighbors()==26)
        self.assertTrue(grid.getCValue()==core3D.MB3D_CUBIC_GRID)
        self.assertTrue(repr(grid)=="mamba3D.DEFAULT_GRID3D")
        
        setDefaultGrid3D(FACE_CENTER_CUBIC)
        
    def testGetDirections3D(self):
        """Verifies that the directions are correctly returned"""
        dirs = getDirections3D(CUBIC)
        self.assertTrue(dirs==list(range(27)))
        dirs = getDirections3D(CENTER_CUBIC)
        self.assertTrue(dirs==list(range(17)))
        dirs = getDirections3D(FACE_CENTER_CUBIC)
        self.assertTrue(dirs==list(range(13)))
        dirs = getDirections3D(0)
        self.assertTrue(dirs==[])
        
    def testGridNeighbors3D(self):
        """Verifies that the number of neighbor are correctly returned"""
        nb = gridNeighbors3D(CUBIC)
        self.assertTrue(nb==26)
        nb = gridNeighbors3D(CENTER_CUBIC)
        self.assertTrue(nb==16)
        nb = gridNeighbors3D(FACE_CENTER_CUBIC)
        self.assertTrue(nb==12)
        nb = gridNeighbors3D(0)
        self.assertTrue(nb==0)
    
    def testTransposeDirection3D(self):
        """Verifies that the direction transposition"""
        d = transposeDirection3D(7)
        self.assertTrue(d==10)
        
def getSuite():
    return unittest.TestLoader().loadTestsFromTestCase(TestGrids3D)
    
if __name__ == '__main__':
    unittest.main()
