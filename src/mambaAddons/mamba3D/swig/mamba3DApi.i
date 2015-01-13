/* Mamba 3D API SWIG wrapper for python
 * 
 * Copyright (c) <2011>, <Nicolas BEUCHER>
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation files
 * (the "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish, 
 * distribute, sublicense, and/or sell copies of the Software, and to permit 
 * persons to whom the Software is furnished to do so, subject to the following 
 * conditions: The above copyright notice and this permission notice shall be 
 * included in all copies or substantial portions of the Software.
 *
 * Except as contained in this notice, the names of the above copyright 
 * holders shall not be used in advertising or otherwise to promote the sale, 
 * use or other dealings in this Software without their prior written 
 * authorization.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

%module mamba3DCore

/* Inclusion inside the c file wrapper created by swig*/
%{
#include "mamba3DApi.h"
%}

/* Typemaps definition */
%include <typemaps.i>
%include <stdint.i>
%include <exception.i>

/* extending the MB3D_Image structure with creator and destructor */
%extend MB3D_Image {
    
    /* 3D Image constructor */
    /* Works with a python list of mamba image pointer */
    /* given as argument */
    MB3D_Image(PyObject *list) {
        MB3D_Image *im;
        PyObject *impointerObj;
        int i;
        void *impointer = 0 ;
        int res = 0 ;
        
        im = (MB3D_Image *) malloc(sizeof(MB3D_Image));
        if (PyList_Check(list)) {
            im->len = PyList_Size(list);
            im->seq = (MB_Image **) malloc(im->len*sizeof(MB_Image *));
            for (i=0; i<im->len; i++) {
                impointerObj = PyList_GetItem(list,i);
                res = SWIG_ConvertPtr(impointerObj, &impointer, NULL, 0 );
                if (SWIG_IsOK(res)) {
                    im->seq[i] = (MB_Image *) impointer;
                } else {
                    PyErr_SetString(PyExc_TypeError,"list must contain MB_Image");
                    free(im->seq);
                    free(im);
                    return NULL;
                }
            }
        } else {
            PyErr_SetString(PyExc_TypeError,"not a list");
            free(im);
            return NULL;
        }
        
        return im;
    }
    
    /* 3D Image destructor */
    ~MB3D_Image() {
        free($self->seq);
        free($self);
    }    
}

%apply unsigned int *OUTPUT {unsigned int *pNbobj};

/* the functions and variables wrapped */
%include "MB3D_error.h"
%include "mamba3DApi.h"




