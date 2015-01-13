
# setup.py
# This is the distutils setup function of Mamba Image library

# This version is intended for 32-bits Windows systems using the Visual C++
# compiler and will produce a version of Mamba using SSE2 instructions.

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
DEF_MACROS = [('__SSE2__',None)]
# compiler options
INC_DIRS = ['./include','./include-private','../commons']
# swig options
SWIG_OPTS = map(lambda v: '-I'+v, INC_DIRS) + ['-outdir','python']

# Base module and associated packages
#""""""""""""""""""""""""""""""""""""
# add it to extensions
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
VERSION = setup_tools.getVersion(os.path.join("python","mamba.py"))
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
