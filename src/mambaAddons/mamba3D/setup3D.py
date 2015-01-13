# setup.py
# This is the distutils setup function of Mamba Image library
import distutils
import os
import re
from distutils.core import setup, Extension
import platform

# Functions to extract meta-data
# (svn revision used as a patch number definition)
def getVersion(filename):
    for line in open(filename).readlines():
        m = re.search("VERSION\s*=\s*\"([^\"]+)\"", line)
        if m:
            return m.group(1)
    return None

################################################################################
# Extension modules and Packages
################################################################################

# The C extension
#""""""""""""""""

# List of source files for the 3D C module
MB3D_API_SRC = [
    os.path.join("c","MB3D_Watershed.c"),
    os.path.join("c","MB3D_Basins.c"),
    os.path.join("c","MB3D_Distanceb.c"),
    os.path.join("c","MB3D_HierarBld.c"),
    os.path.join("c","MB3D_HierarDualBld.c"),
    os.path.join("c","MB3D_Labelb.c")
    ]
MB3D_API_SRC.sort() #Compilation in alphabetic order 

MB3D_API_SRC = [os.path.join("swig","mamba3DApi.i")]+MB3D_API_SRC

# swig options
MB3D_SWIG_OPTS = ['-I./include',
                '-I./include-private',
                '-I../../commons',
                '-outdir','python/mamba3D']

# add it to extensions
EXTENSIONS = [
    Extension("mamba3D._mamba3DCore",
              MB3D_API_SRC,
              swig_opts=MB3D_SWIG_OPTS,
              include_dirs=['./include','./include-private','../../commons'])
]
PACKAGES = ['mamba3D']

################################################################################
# Meta-data
################################################################################

NAME = "Mamba 3D"
VERSION = getVersion(os.path.join("python",os.path.join("mamba3D","__init__.py")))
DESCRIPTION = "A 3D extension for the mamba library"
AUTHOR = "Nicolas BEUCHER", "nicolas.beucher@ensta.org"
HOMEPAGE = "www.mamba-image.org"

################################################################################
# SETUP FUNCTION
################################################################################

setup(name = NAME,
      author = AUTHOR[0], author_email = AUTHOR[1],
      description = DESCRIPTION,
      version = VERSION,
      url = HOMEPAGE,
      license = "License X11",
      long_description = DESCRIPTION,
      ext_modules = EXTENSIONS,
      packages = PACKAGES,
      package_dir = {'': 'python'}
      )
