Description
-----------

This Git repository corresponds to an unofficial repository for the `Mamba Image library for Python
<http://www.mamba-image.org>`_ initialised from the source of the release V1.1.3.

Mamba is an open-source Mathematical Morphology library written in C and Python. I believe it is the
most complete implementation available in open source.

The project home page is located `here <http://www.mamba-image.org>`_ and look at this `page
<http://www.mamba-image.org/about.html>`_ for history and licence.

Links to Open Source Mathematical Morphology libraries
------------------------------------------------------

* `scikit-image <http://scikit-image.org>` is an image processing library written in Python and
  Cython. It is more complete than OpenCV (for Mathematical Morphology).
* `OpenCV <http://opencv.org>`_ is under very active development but quite incomplete for
  Mathematical Morphology, for example reconstruction is not implemented.
* `ITK <http://www.itk.org>`_ is implemented using strict coding rules, but it is generally quite slower.


* `Fulguro <http://fulguro.sourceforge.net/index.html>`_ is no more active.
* `OpenMorpho <http://openmorpho.sourceforge.net>`_ is no more active.

Ideas for Improvements
----------------------

* speed: make use of more recent SIMD than SSE2, look at OpenCV and Fulguro
* documentation: use sphinx to generate a nice HTML documentation
* cosmetic: homogenisation of the coding (space, DOS encoding, etc.)

Changes
-------

* Python3 support
* some cosmetics to homogenise the coding (added space)

.. End
