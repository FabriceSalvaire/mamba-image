/**
 * \file mamba3DApi.h
 * \date 21-05-2011
 *
 * This file contains the various definitions, global variables
 * macro, struct and functions created for the library.
 */
 
/*
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
#ifndef MB3D_apiH
#define MB3D_apiH

#ifdef __cplusplus
extern "C" {
#endif

/****************************************/
/* Includes                             */
/****************************************/
#include "mambaCommon.h"
#include "MB3D_error.h"

/****************************************/
/* Defines                              */
/****************************************/

/****************************************/
/* Macros                               */
/****************************************/

/****************************************/
/* Structures and Typedef               */
/****************************************/

/** 3D image data structure */
typedef struct {
    /** The images sequence composing the 3D data */
    MB_Image **seq;
    /** the lenght of the sequence */
    int len;
} MB3D_Image;

/** enumerate for grid : either cubic or face centered cubic
 * (fcc, also known as cubic close-packed or ccp)
 * Values are specificly chosen not to match 2D grid values.
 */
enum MB3D_grid_t {
    MB3D_INVALID_GRID = -1, /* Specific case for python defined grid with no match in C core */
    MB3D_CUBIC_GRID = 1024,
    MB3D_FCC_GRID = 1025
};

/****************************************/
/* Global variables                     */
/****************************************/

/****************************************/
/* functions                            */
/****************************************/

/* Watershed segmentation */
MB3D_errcode MB3D_Watershed(MB3D_Image *src, MB3D_Image *marker, unsigned int max_level, enum MB3D_grid_t grid);
/* Basin segmentation */
MB3D_errcode MB3D_Basins(MB3D_Image *src, MB3D_Image *marker, unsigned int max_level, enum MB3D_grid_t grid);
/* reconstruction by hierarchical lists and dual */
MB3D_errcode MB3D_HierarBld(MB3D_Image *mask, MB3D_Image *srcdest, enum MB3D_grid_t grid);
MB3D_errcode MB3D_HierarDualBld(MB3D_Image *mask, MB3D_Image *srcdest, enum MB3D_grid_t grid);
/* labelling */
MB3D_errcode MB3D_Labelb(MB3D_Image *src, MB3D_Image *dest,
                         unsigned int lblow, unsigned int lbhigh,
                         unsigned int *pNbobj,
                         enum MB3D_grid_t grid);
/* Binary set distance */
MB3D_errcode MB3D_Distanceb(MB3D_Image *src, MB3D_Image *dest, enum MB3D_grid_t grid, enum MB_edgemode_t edge);

#ifdef __cplusplus
}
#endif

#endif

