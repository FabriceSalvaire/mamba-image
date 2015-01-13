Rem ## Mamba Documentation generation batch file ##

Rem this batch files is here to produce the documentation in a windows
Rem environment. 

Rem You will need miktek, doxygen, python and mamba installed on your
Rem computer with the appropriate binaries path included in your
Rem PATH environment variable to make it work. Also make sure that
Rem all the files in directory style/ (mamba latex style mamba.sty, logo image
Rem mamba_logo.png and license icon by.pdf) are foundable as a package for miktex

Rem 3D USER MANUAL
copy style\mamba_logo.pdf mb3D-um\
copy style\by.pdf mb3D-um\
pushd mb3D-um\
pdflatex mb3D-um.tex
pdflatex mb3D-um.tex
copy mb3D-um.pdf ..
del /Q/F mamba_logo.pdf
del /Q/F by.pdf
popd 

Rem  3D PYTHON REFERENCE
copy style\mamba_logo.pdf 3Dpy_ref\
copy style\by.pdf 3Dpy_ref\
pushd 3Dpy_ref
python createPython3DRef.py
copy 3Dpyref.pdf ..
python createPython3DQuickRef.py
copy 3Dpyquickref.pdf ..
del /Q/F mamba_logo.pdf
del /Q/F by.pdf
popd

