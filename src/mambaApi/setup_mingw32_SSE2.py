
# setup.py
# This is the distutils setup function of Mamba Image library

# This version is intended for 32-bits systems using the GCC compiler and will 
# produce a version of Mamba using SSE2 instructions.

# On Linux systems, GCC is already the default compiler for the setup script.
# However, on Windows, you will have to specify gcc as your compiler using
# the -c option of the build_ext command (-cmingw32).

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
DEF_MACROS = []
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
                  define_macros=DEF_MACROS,
                  extra_compile_args = ['-m32', '-msse2'])
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
