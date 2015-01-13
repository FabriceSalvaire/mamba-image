"""
This module defines the 3D grids (cubic and face-centered cubic) that can be
used with the 3D operators.

The modules also defines utility functions to handle 3D grids.
"""

# Contributors : Nicolas BEUCHER

import mamba3D as m3D
import mamba3DCore as core3D
import mamba
import mambaCore

# 3D Grid support ##############################################################
class _grid3D:

    def convertFromDir(self, direction, zindex):
        # The direction in 3D correspond to
        # various elements : the plane offset (0 if the
        # direction does not change it, 1 to go to the
        # previous offset, ...), the 2D direction as defined
        # by mamba in the offset plane
        # 
        # The input is the direction in the 3D grid and the
        # actual position of the plane of the starting point
        return (0,0)
        
    def get2DGrid(self):
        # Used to indicates the 2D grid on which the 3D grid is based.
        return mamba.HEXAGONAL
        
    def getTranDir(self, d):
        # Returns the transposed direction of d in the grid
        return d
        
    def getZExtension(self):
        # Returns the biggest distance in plane a neighbor pixel can be
        # from the central point
        return 0
        
    def getDirections(self):
        # Returns the available directions on the grid
        return []
        
    def maxNeighbors(self):
        # Returns the maximum of neighbors a point can have in this grid
        return 0
        
    def getCValue(self):
        # Returns the C core value corresponding to the grid
        #(see type MB3D_grid_t). Returns MB3D_INVALID_GRID if the
        # grid as no corresponding C core grid value.
        return core3D.MB3D_INVALID_GRID
        
    def __repr__(self):
        # the name of the grid
        return "mamba3D.3D_GRID_NAME"
        

class _gridFCCubic3D(_grid3D):

    def __init__(self):
        self.name = "FACE_CENTER_CUBIC"
        self.basegrid = mamba.HEXAGONAL
                     #0     #1     #2     #3     #4     #5     #6
        listConv0 = [(0,0), (0,1), (0,2), (0,3), (0,4), (0,5), (0,6),
                     #7      #8      #9
                     (-1,0), (-1,5), (-1,6),
                     #10    #11    #12
                     (1,6), (1,1), (1,0)
                    ]
                     #0     #1     #2     #3     #4     #5     #6
        listConv1 = [(0,0), (0,1), (0,2), (0,3), (0,4), (0,5), (0,6),
                     #7      #8      #9
                     (-1,3), (-1,4), (-1,0),
                     #10    #11    #12
                     (1,5), (1,0), (1,4)
                    ]
                     #0     #1     #2     #3     #4     #5     #6
        listConv2 = [(0,0), (0,1), (0,2), (0,3), (0,4), (0,5), (0,6),
                     #7      #8      #9
                     (-1,2), (-1,0), (-1,1),
                     #10    #11    #12
                     (1,0), (1,2), (1,3)
                    ]
        self.listConvs = [listConv0, listConv1, listConv2]
    def convertFromDir(self, direction, zindex):
        try:
            conversion = self.listConvs[zindex%3][direction]
        except IndexError:
            mamba.raiseExceptionOnError(mambaCore.ERR_BAD_DIRECTION)
        return conversion
    def getZExtension(self):
        return 1
    def get2DGrid(self):
        return self.basegrid
    def getTranDir(self, d):
        if d==0:
            return 0
        elif d<7:
            return ((d+2)%6)+1
        elif d<10:
            return d+3
        else:
            return d-3
    def getDirections(self):
        return range(len(self.listConvs[0]))
    def maxNeighbors(self):
        return len(self.listConvs[0])-1
    def getCValue(self):
        return core3D.MB3D_FCC_GRID
    def __repr__(self):
        return "mamba3D."+self.name
    
FACE_CENTER_CUBIC = _gridFCCubic3D()

class _gridCCubic3D(_grid3D):

    def __init__(self):
        self.name = "CENTER_CUBIC"
        self.basegrid = mamba.SQUARE
                     #0     #1     #2     #3     #4     #5     #6     #7     #8
        listConv0 = [(0,0), (0,1), (0,2), (0,3), (0,4), (0,5), (0,6), (0,7), (0,8),
                     #9      #10     #11     #12
                     (-1,0), (-1,7), (-1,8), (-1,1),
                     #13    #14    #15    #16
                     (1,8), (1,1), (1,0), (1,7)
                    ]
                     #0     #1     #2     #3     #4     #5     #6     #7     #8
        listConv1 = [(0,0), (0,1), (0,2), (0,3), (0,4), (0,5), (0,6), (0,7), (0,8),
                     #9      #10     #11     #12
                     (-1,4), (-1,5), (-1,0), (-1,3),
                     #13    #14    #15    #16
                     (1,0), (1,3), (1,4), (1,5)
                    ]
        self.listConvs = [listConv0, listConv1]
    def convertFromDir(self, direction, zindex):
        try:
            conversion = self.listConvs[zindex%2][direction]
        except IndexError:
            mamba.raiseExceptionOnError(mambaCore.ERR_BAD_DIRECTION)
        return conversion
    def getZExtension(self):
        return 1
    def get2DGrid(self):
        return self.basegrid
    def getTranDir(self, d):
        if d==0:
            return 0
        elif d<9:
            return ((d+3)%8)+1
        elif d<13:
            return d+4
        else:
            return d-4
    def getDirections(self):
        return range(17)
    def maxNeighbors(self):
        return 16
    def getCValue(self):
        return core3D.MB3D_INVALID_GRID
    def __repr__(self):
        return "mamba3D."+self.name

CENTER_CUBIC = _gridCCubic3D()

class _gridCubic3D(_grid3D):

    def __init__(self):
        self.name = "CUBIC"
        self.basegrid = mamba.SQUARE
        self.transpDict={
            0:0,1:5,5:1,2:6,6:2,3:7,7:3,4:8,8:4,
            9:18,18:9,19:14,14:19,20:15,15:20,
            21:16,16:21,22:17,17:22,23:10,10:23,
            24:11,11:24,25:12,12:25,26:13,13:26
            }
    def convertFromDir(self, direction, zindex):
        if direction>26 or direction<0:
            mamba.raiseExceptionOnError(mambaCore.ERR_BAD_DIRECTION)
        if direction<9:
            return (0,direction)
        elif direction<18:
            return (-1,direction-9)
        else:
            return (1,direction-18)
    def getZExtension(self):
        return 1
    def get2DGrid(self):
        return self.basegrid
    def getTranDir(self, d):
        return self.transpDict[d]
    def getDirections(self):
        return range(27)
    def maxNeighbors(self):
        return 26
    def getCValue(self):
        return core3D.MB3D_CUBIC_GRID
    def __repr__(self):
        return "mamba3D."+self.name

CUBIC = _gridCubic3D()
        
class _gridDefault3D(_grid3D):

    def __init__(self):
        self.name = "DEFAULT_GRID3D"
        self.proxyGrid = None
    def setProxyGrid(self, grid):
        if isinstance(grid, _grid3D):
            self.proxyGrid = grid
        else:
            mamba.raiseWarning("Invalid 3D grid for default")
    def convertFromDir(self, direction, zindex):
        return self.proxyGrid.convertFromDir(direction,zindex)
    def getZExtension(self):
        return self.proxyGrid.getZExtension()
    def get2DGrid(self):
        return self.proxyGrid.get2DGrid()
    def getTranDir(self, d):
        return self.proxyGrid.getTranDir(d)
    def getDirections(self):
        return self.proxyGrid.getDirections()
    def maxNeighbors(self):
        return self.proxyGrid.maxNeighbors()
    def getCValue(self):
        return self.proxyGrid.getCValue()
    def __repr__(self):
        return "mamba3D."+self.name

DEFAULT_GRID3D = _gridDefault3D()
DEFAULT_GRID3D.setProxyGrid(FACE_CENTER_CUBIC)

###############################################################################
# Public functions to deal with grid

def setDefaultGrid3D(grid):
    """
    This function will change the value of the default grid used in each 
    operator that needs to specify one.
    
    'grid' must be a valid 3D grid.
    
    You can of course manually change the variable DEFAULT_GRID3D by yourself.
    Using this function is however recommended if you are not sure of what you 
    are doing.
    """
    global DEFAULT_GRID3D
    DEFAULT_GRID3D.setProxyGrid(grid)

def getDirections3D(grid=DEFAULT_GRID3D):
    """
    Returns a list containing all the possible directions available in 'grid' 
    (set to DEFAULT_GRID3D by default).
    
    If the 'grid' value is incorrect, the function returns an empty list.
    """
    if isinstance(grid, _grid3D):
        return grid.getDirections()
    else:
        return []

def gridNeighbors3D(grid=DEFAULT_GRID3D):
    """
    Returns the number of neighbors of a point in 'grid'.
    
    If the 'grid' value is incorrect, the function returns 0.
    """
    if isinstance(grid, _grid3D):
        return grid.maxNeighbors()
    else:
        return 0
        
def transposeDirection3D(d, grid=DEFAULT_GRID3D):
    """
    Calculates the transposed (opposite) direction value of direction 'd' 
    """
    return grid.getTranDir(d)
    
