# Setup tools and common parameters.

# This script specifies functions and variables that are common between different
# setup scripts.

import os
import re
import platform

################################################################################
# Tool functions
################################################################################

# Functions to extract meta-data
def getVersion(filename):
    for line in open(filename).readlines():
        m = re.search("VERSION\s*=\s*\"([^\"]+)\"", line)
        if m:
            return m.group(1)
    return None

################################################################################
# Common parameters
################################################################################

# List of source files
MB_API_SWIG = os.path.join("swig","mambaApi.i")

MB_API_SRC = [
    "MB_Add","MB_And","MB_Compare","MB_ConAdd",
    "MB_ConDiv","MB_ConMul","MB_ConSet","MB_ConSub","MB_Convert",
    "MB_Create","MB_Diff","MB_Error","MB_Histo","MB_Inf","MB_InfNb8",
    "MB_InfNbb","MB_Inv","MB_LoadExtract","MB_Lookup","MB_Or","MB_Shiftb",
    "MB_Sub","MB_Sup","MB_SupNb8","MB_SupNbb","MB_Thresh","MB_Volume","MB_Xor",
    "MB_DiffNb8","MB_DiffNbb","MB_Mask","MB_CopyBitPlane","MB_BinHitOrMiss",
    "MB_Range", "MB_BldNbb", "MB_BldNb8", "MB_Labelb", "MB_CopyBytePlane",
    "MB_InfNb32", "MB_SupNb32", "MB_Shift32", "MB_Distanceb", "MB_Check",
    "MB_Pixel", "MB_DualBldNb8", "MB_DualBldNbb", "MB_Watershed",
    "MB_Mul", "MB_Frame", "MB_Basins", "MB_SupMask", "MB_Shift8", "MB_Utils",
    "MB_Copy", "MB_InfFarNbb", "MB_InfFarNb8", "MB_InfFarNb32", "MB_SupFarNbb", 
    "MB_SupFarNb8", "MB_SupFarNb32", "MB_HierarBld", "MB_HierarDualBld",
    "MB_DualBldNb32", "MB_BldNb32", "MB_SupVectorb", "MB_SupVector8",
    "MB_SupVector32", "MB_InfVectorb", "MB_InfVector8", "MB_InfVector32",
    "MB_ShiftVectorb", "MB_ShiftVector8", "MB_ShiftVector32"
    ]
MB_API_SRC.sort() #Compilation in alphabetic order 

files = []
files.append(MB_API_SWIG)
for s in MB_API_SRC:
    files.append(os.path.join("c", s+".c"))

PACKAGES = ['','mambaComposed','mambaShell']

################################################################################
# IDLE Shell data and scripts
################################################################################

package_data = {'mambaShell': ['*.ico','*.bmp']}
scripts = []
if platform.platform().find("Windows")>=0:
    scripts = ['scripts/mamba_post_install.py']
