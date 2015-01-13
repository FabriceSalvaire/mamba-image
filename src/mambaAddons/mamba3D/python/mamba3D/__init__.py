"""
The mamba3D package defines a set of function and operators along with a
specific display to manipulate 3D image using the mamba library.
"""

# Mamba imports
try:
    import mamba
    _mb_version = mamba.VERSION.split('.')
    if int(_mb_version[0])!=1 and int(_mb_version[1])!=1:
        raise ImportError("mamba3D requires mamba version 1.1 (current=%s)" %
                          _mb_version)
except ImportError:
    print ("Missing Mamba library - http://www.mamba-image.org")
    raise
    
# mamba3D module version
VERSION = "1.1"

# importing all the modules
from display3D import *
from base3D import *
from grids3D import *
from erodil3D import *
from contrasts3D import *
from filter3D import *
from geodesy3D import *
from arithmetic3D import *
from conversion3D import *
from miscellaneous3D import *
from openclose3D import *
from segment3D import *
from statistic3D import *
from draw3D import *
from thinthick3D import *


