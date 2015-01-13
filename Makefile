################################################################
# Mamba make file
################################################################

.PHONY: clean doc test

all: clean pylib pylibRT pylib3D doc

pylib:
	@cd src/mambaApi/; python setup.py build_ext bdist

pylibRT:
	@cd src/mambaAddons-restricted/realtime-linux/; python setupRT.py build_ext bdist

pylib3D:
	@cd src/mambaAddons/mamba3D/; python setup3D.py build_ext bdist

test:pylib pylib3D
	@cd test; ${MAKE}

clean:
	@cd src/mambaApi/; python setup.py clean -a
	rm -rf src/mambaApi/dist
	rm -rf src/mambaApi/python/mambaCore.py
	rm -rf src/mambaApi/swig/mambaApi_wrap.c
	@cd src/mambaAddons-restricted/realtime-linux/; python setupRT.py clean -a
	rm -rf src/mambaAddons-restricted/realtime-linux/dist
	rm -rf src/mambaAddons-restricted/realtime-linux/python/mambaRealtime/mambaRTCore.py
	rm -rf src/mambaAddons-restricted/realtime-linux/swig/mambaRTApi_wrap.c
	@cd src/mambaAddons/mamba3D/; python setup3D.py clean -a
	rm -rf src/mambaAddons/mamba3D/dist
	rm -rf src/mambaAddons/mamba3D/python/mamba3D/mamba3DCore.py
	rm -rf src/mambaAddons/mamba3D/swig/mamba3DApi_wrap.c
	@cd test; ${MAKE} clean
	@cd doc; ${MAKE} clean
	find . -name "*~" -exec rm {} \;
	
doc:
	@cd doc; ${MAKE} all
	


