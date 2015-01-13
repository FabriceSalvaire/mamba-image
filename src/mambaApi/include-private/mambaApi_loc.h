/**
 * \file mambaApi_loc.h
 * \date 11-4-2007
 *
 * This file contains the various definitions, global variables
 * macro, struct and functions that are shared between components
 * of the library but are not meant to be exported to the outside
 * world.
 *
 */
 
/*
 * Copyright (c) <2009>, <Nicolas BEUCHER and ARMINES for the Centre de 
 * Morphologie Mathématique(CMM), common research center to ARMINES and MINES 
 * Paristech>
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
#ifndef MB_apilocH
#define MB_apilocH

/* The local header is the only header called inside each component of
 * the library, The global header is meant for the outside world.
 */
#include "mambaApi.h"

/* standard headers */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <malloc.h>

/* if SSE2 is available use it ! it's faster*/
#ifdef __SSE2__
#include <xmmintrin.h>
#include <emmintrin.h>
#endif

/****************************************/
/* Defines                              */
/****************************************/
/**@cond */
/* code that must be skipped by Doxygen */

/* Possible image combinations*/
#define MB_PAIR_1_1     129 /* 128+1 */
#define MB_PAIR_1_8     136 /* 128+8 */
#define MB_PAIR_1_32    160 /* 128+32 */

#define MB_PAIR_8_1     1025 /* 8*128+1 */
#define MB_PAIR_8_8     1032 /* 8*128+8 */
#define MB_PAIR_8_32    1056 /* 8*128+32 */

#define MB_PAIR_32_1    4097 /* 32*128+1 */
#define MB_PAIR_32_8    4104 /* 32*128+8 */
#define MB_PAIR_32_32    4128 /* 32*128+32 */

/* defines to handle 64 bits processor */
/* binary computations are performed on a complete */
/* word so either 32 bits or 64 */
#ifdef BINARY64
    typedef uint64_t binaryT;
    #define SHIFT1BIT 63
#else
    typedef uint32_t binaryT;
    #define SHIFT1BIT 31
#endif
#define BYTEPERWORD sizeof(binaryT)
/**@endcond*/

/** Value used to specify the end of a hierarchical list */
#define MB_LIST_END -1

/****************************************/
/* Macros                               */
/****************************************/

/** Returns the value of the images combination MB_PAIR_x_x */
#define MB_PROBE_PAIR(im_in, im_out) \
    (((im_in->depth)<<7) + (im_out)->depth)
    
/** Returns True if the two images sizes are compatibles */
# define MB_CHECK_SIZE_2(im1, im2) \
    (((im1->width)==(im2->width))&&((im1->height)==(im2->height)))
    
/** Returns True if the three images sizes are compatibles */
# define MB_CHECK_SIZE_3(im1, im2, im3) \
    (MB_CHECK_SIZE_2(im1, im2) && MB_CHECK_SIZE_2(im1, im3))
 
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
} MB_Token;

/** 
 * List control structure that gives you the index
 * of the first and last elements of list.
 */
typedef struct {
    /** first token of the list (x) */
    int firstx;
    /** first token of the list (y) */
    int firsty;
    /** last token of the list (x) */
    int lastx;
    /** last token of the list (y) */
    int lasty;
} MB_ListControl;

/****************************************/
/* Neighbors access                     */
/****************************************/

/** Table giving the offset for the neighbor in square grid (x and y) */ 
extern const int sqNbDir[9][2];

/** Table giving the offset for the neighbor in hexagonal grid (x and y) */
/* the direction depends on the oddness/evenness of the line */
extern const int hxNbDir[2][7][2];

/****************************************/
/* volume arrays                        */
/****************************************/

/** Volume arrays*/
extern const Uint64 MB_VolumePerByte[256];

/****************************************/
/* Internal memory management           */
/****************************************/

void *MB_malloc(int size);
void *MB_aligned_malloc(int size, int alignment);
void MB_free(void *ptr);
void MB_aligned_free(void *ptr);

void *MB_memset(void *s, int c, int size);
void *MB_memcpy(void *dest, const void *src, int size);

#endif
