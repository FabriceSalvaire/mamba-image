Rem ## Mamba Building script for windows ##

Rem this batch file cleans your mamba source directory and builds
Rem the windows installer for Mamba, Mamba 3D and Mamba Realtime

Rem CLEANING
pushd src\mambaApi\
python setup_visualcpp_SSE2.py clean -a
popd
rmdir /Q /S src\mambaApi\dist
del /Q /F src\mambaApi\python\mambaCore.py
del /Q /F src\mambaApi\swig\mambaApi_wrap.c
del /Q /F src\mambaApi\setup_tools.pyc
pushd src\mambaAddons-restricted\realtime-win\
python setupRT.py clean -a
popd
rmdir /Q /S src\mambaAddons-restricted\realtime-win\dist
del /Q /F src\mambaAddons-restricted\realtime-win\python\mambaRealtime\mambaRTCore.py
del /Q /F src\mambaAddons-restricted\realtime-win\swig\mambaRTApi_wrap.c
pushd src\mambaAddons\mamba3D\
python setup3D.py clean -a
popd
rmdir /Q /S src\mambaAddons\mamba3D\dist
del /Q /F src\mambaAddons\mamba3D\python\mamba3D\mamba3DCore.py
del /Q /F src\mambaAddons\mamba3D\swig\mamba3DApi_wrap.c

Rem COMPILING Mamba Library
pushd src\mambaApi\
python setup_visualcpp_SSE2.py build_ext bdist_wininst --install-script=mamba_post_install.py --bitmap=../../doc/style/mamba_logo.bmp
popd

Rem COMPILING Mamba Realtime
pushd src\mambaAddons-restricted\realtime-win\
python setupRT.py build_ext bdist_wininst --bitmap=../../../doc/style/mamba_logo.bmp
popd

Rem COMPILING Mamba 3D
pushd src\mambaAddons\mamba3D\
python setup3D.py build_ext bdist_wininst --bitmap=../../../doc/style/mamba_logo.bmp
popd