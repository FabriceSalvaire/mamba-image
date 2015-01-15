Description
-----------

This Git repository corresponds to an unofficial repository for the `Mamba Image library for Python
<http://www.mamba-image.org>`_ initialised from the source of the release V1.1.3.

Mamba is an open-source Mathematical Morphology library written in C and Python.  I believe it is
the most complete implementation available in open source.  It was developed by `Serge Beucher
<http://cmm.ensmp.fr/~beucher/sbpage_eng.html>`_, Nicolas Beucher and Michel Bilodeau.  Serge
Beucher and Michel Bilodeau are researchers in the `CMM <http://cmm.ensmp.fr>`_ laboratory where the
Mathematical Morphology was invented by `Jean Serra <http://cmm.ensmp.fr/~serra/aaccueil.htm>`_.
The source code originates from a software so called `Micromorph <http://cmm.ensmp.fr/Micromorph>`_
developed and commercialised by CMM in the past.

The project home page is located `here <http://www.mamba-image.org>`_ and look at this `page
<http://www.mamba-image.org/about.html>`_ for history and licence.

Links to Open Source Mathematical Morphology libraries
------------------------------------------------------

Note: all these libraries have a Python interface.

* `scikit-image <http://scikit-image.org>`_
 * is an image processing library written in Python and Cython.
 * It is more complete than OpenCV (for Mathematical Morphology).
 * But not adapted for large image.

* `OpenCV <http://opencv.org>`_
 * is under very active development,
 * but quite incomplete for Mathematical Morphology, for example reconstruction is not implemented.

* `ITK <http://www.itk.org>`_
 * is implemented using strict coding rules,
 * but it is generally quite slower.

* `SMIL <http://smil.cmm.mines-paristech.fr/doc/index.html>`_
 * stands for Simple Image Processing Lirary
 * is developed by Matthieu Faessel and ARMINE
 * should be open source, but source code is not yet made available
 * see this presentation to learn more about SMIL`pdf <http://cmm.ensmp.fr/~faessel/documents/2013_03_SMIL_LRDE.pdf>`_
   It compares Mamba, SMIL, Morph-M and Fulguro.

* `Fulguro <http://fulguro.sourceforge.net/index.html>`_
 * is no more active
 * developed by Christophe Clienti

* `Yayi <http://raffi.enficiaud.free.fr>`_
 * is no more active
 * developed by Raffi Enficiaud

* `OpenMorpho <http://openmorpho.sourceforge.net>`_
 * is no more active and doesn't have a Python interface.

`Morph-M <http://cmm.ensmp.fr/Morph-M>`_ is a proprietary library developed by the `Centre de
Morphologie Mathématique <<http://cmm.ensmp.fr>'_.

`ImageJ <http://fiji.sc/Fiji>`_ has some plugins on the topic.

Ideas for Improvements
----------------------

* speed: make use of more recent SIMD than SSE2, look at OpenCV and Fulguro
* documentation: use sphinx to generate a nice HTML documentation
* cosmetic: homogenisation of the coding (space, DOS encoding, etc.)

Changes
-------

* Python3 support (basic and advanced test suit pass excepted 3 tests)
* Numpy support, see file *examples/numpy_wrapper.py* for usage
* pillow support
* some cosmetics to homogenise the coding (added space)

Building
--------

The procedure to build Mamba is described in the *readme* file.

To compile and install the Mamba library, run these commands from the *src/mambaApi* directory :

.. code-block:: sh

  python setup.py build_ext build
  python setup.py install

You can also run make from the top directory.

.. End
