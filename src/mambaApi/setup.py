
# setup.py
# This is the default distutils setup function of Mamba Image library

# The behavior of this script may vary depending on the system on which you
# are operating. This script is the minimal, safest way to compile and
# package the mamba library. It is guaranteed to work on all supported systems
# and with all supported compilers. However it may not produce the fastest and
# most optimized version of the library (this is indeed true on 32-bits systems
# for which the SSE2 is not enabled by default).

# To produce more optimized results use the other setup scripts
#   -> setup_mingw32_SSE2.py : optimized setup script for 32-bits systems using
#      gcc compiler (mingw32 on Windows). Produces a version using SSE2 
#      instructions. Works only with GCC (see script header for information).
#   -> setup_visualcpp_SSE2.py : optimized setup script for 32-bits Windows system
#      using the Visual C++ compiler. Produces a version using SSE2 
#      instructions. Works only with Visual C++ (see script header for information).

# If there is no optimized setup script for your system, it can be for two reasons.
# Firstly, the default script is already the best one you can get or secondly, your
# system is not currently supported by Mamba.

import distutils
from distutils.core import setup, Extension
import platform
import os

# importing the source definitions and the tools functions
import setup_tools

################################################################################
# Extension modules and Packages
################################################################################

# platform specific compilation defines
if platform.architecture()[0] == '64bit':
    DEF_MACROS = [('BINARY64', None)]
    SWIGDEF64 = ['-DBINARY64']
    ext_version = ''
else:
    DEF_MACROS = []
    SWIGDEF64 = []
    ext_version = '.noSSE2'
# compiler options
INC_DIRS = ['./include','./include-private','../commons']
# swig options
SWIG_OPTS = SWIGDEF64 + ['-I' + x for x in INC_DIRS] + ['-outdir','python']

# Base module and associated packages
#""""""""""""""""""""""""""""""""""""
EXTENSION = [
        Extension("_mambaCore",
                  setup_tools.files,
                  swig_opts=SWIG_OPTS,
                  include_dirs=INC_DIRS,
                  define_macros=DEF_MACROS)
            ]

################################################################################
# Meta-data
################################################################################

NAME = "Mamba Image"
VERSION = setup_tools.getVersion(os.path.join("python","mamba.py"))+ext_version
DESCRIPTION = "A fast and simple mathematical morphology image analysis library for python"
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
      ext_modules = EXTENSION,
      packages = setup_tools.PACKAGES,
      package_dir = {'': 'python'},
      extra_path = 'mambaIm',
      package_data = setup_tools.package_data,
      scripts = setup_tools.scripts
      )
