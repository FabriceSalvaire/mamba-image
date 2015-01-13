/**
 * \file mamba3DApi_loc.h
 * \date 21-05-2011
 *
 * This file contains the various definitions, global variables
 * macro, struct and functions that are shared between components
 * of the library but are not meant to be exported to the outside
 * world.
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
#ifndef MB3D_apilocH
#define MB3D_apilocH

/* The local header is the only header called inside each component of
 * the library, The global header is meant for the outside world.
 */
#include "mamba3DApi.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

/****************************************/
/* Defines                              */
/****************************************/
/**@cond */
/* code that must be skipped by Doxygen */

/* Possible image combinations*/
#define MB3D_PAIR_1_1     129 /* 128+1 */
#define MB3D_PAIR_1_8     136 /* 128+8 */
#define MB3D_PAIR_1_32    160 /* 128+32 */

#define MB3D_PAIR_8_1     1025 /* 8*128+1 */
#define MB3D_PAIR_8_8     1032 /* 8*128+8 */
#define MB3D_PAIR_8_32    1056 /* 8*128+32 */

#define MB3D_PAIR_32_1    4097 /* 32*128+1 */
#define MB3D_PAIR_32_8    4104 /* 32*128+8 */
#define MB3D_PAIR_32_32    4128 /* 32*128+32 */

/**@endcond*/

/** Value used to specify the end of a hierarchical list */
#define MB3D_LIST_END -1

/****************************************/
/* Macros                               */
/****************************************/

/** Returns the value of the images combination MB3D_PAIR_x_x */
#define MB3D_PROBE_PAIR(im_in, im_out) \
    (((im_in->seq[0]->depth)<<7) + im_out->seq[0]->depth)

/** Returns True if the two images sizes are compatibles */
# define MB3D_CHECK_SIZE_2(im1, im2) \
    (((im1->seq[0]->width)  == (im2->seq[0]->width) ) && \
     ((im1->seq[0]->height) == (im2->seq[0]->height)) && \
     ((im1->len) == (im2->len)) )

/****************************************/
/* Structures and Typedef               */
/****************************************/

/** 
 * Token used in hierarchical list.
 * A token gives its next (by position nextx, nexty in image) 
 * token in the list (-1 if the list ends).
 */
typedef struct {
    /** next token (x) */
    int nextx;
    /** next token (y) */
    int nexty;
    /** next token (z) */
    int nextz;
} MB3D_Token;

/** 
 * List control structure that gives you the index
 * of the first and last elements of list.
 */
typedef struct {
    /** first token of the list (x) */
    int firstx;
    /** first token of the list (y) */
    int firsty;
    /** first token of the list (z) */
    int firstz;
    /** last token of the list (x) */
    int lastx;
    /** last token of the list (y) */
    int lasty;
    /** last token of the list (z) */
    int lastz;
} MB3D_ListControl;

/****************************************/
/* Neighbors access                     */
/****************************************/

/** Table giving the offset for the neighbor in cube grid (x, y and z) */ 
extern const int cubeNbDir[27][3];

/** Table giving the offset for the neighbor in face-centered cubic grid (x, y and z) */
/* the direction depends on the coordinates of the line y and planes z*/
extern const int fccNbDir[6][13][3];

/****************************************/
/* Global variables                     */
/****************************************/

/****************************************/
/* functions                            */
/****************************************/

#endif
