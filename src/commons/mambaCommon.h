/**
 * \file mambaCommon.h
 * \date 31-03-2009
 *
 * This file contains the various definitions, macro, struct that are commons 
 * between the various modules of the library
 *
 * The copyright license of Mamba is reminded here :
 *
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
#ifndef MB_commonH
#define MB_commonH

#ifdef __cplusplus
extern "C" {
#endif

/****************************************/
/* Includes                             */
/****************************************/
#include <stdint.h>

/****************************************/
/* Defines                              */
/****************************************/
/**@cond */
/* code that must be skipped by Doxygen */

/* compiler specific */
#ifdef _MSC_VER
    #define INLINE __inline
#else
    #define INLINE inline
#endif

#define Y_TOP       1
#define X_LEFT      16 /*this is the size of a vector __m128i*/

#define Y_BOTTOM    Y_TOP
#define X_RIGHT     X_LEFT

/* bit per character */
#define CHARBIT 8
/**@endcond*/

/****************************************/
/* Macros                               */
/****************************************/

/** Getting image frame offset from left */
#define MB_X_LEFT(im)   X_LEFT
/** Getting image frame offset from right */
#define MB_X_RIGHT(im)  X_RIGHT
/** Getting image frame offset from top */
#define MB_Y_TOP(im)    Y_TOP
/** Getting image frame offset from bottom */
#define MB_Y_BOTTOM(im) Y_BOTTOM

/** Returns the size in bytes of an image line */
#define MB_LINE_COUNT(im) \
    ((im->width*im->depth)/CHARBIT)

/** Returns the size in bytes of the line offset */
#define MB_LINE_OFFSET(im) \
    (MB_X_LEFT(im))
    

#ifdef BINARY64
    /** How to fill the edge (binary bits images) */
    #define BIN_FILL_VALUE(edge) ((edge==MB_FILLED_EDGE) ? UINT64_MAX:0)
#else
    /** How to fill the edge (binary bits images) */
    #define BIN_FILL_VALUE(edge) ((edge==MB_FILLED_EDGE) ? UINT32_MAX:0)
#endif

/** How to fill the edge (8 bits images) */
#define GREY_FILL_VALUE(edge) ((edge==MB_FILLED_EDGE) ? UINT32_MAX:0)
/** How to fill the edge (32 bits images) */
#define I32_FILL_VALUE(edge) ((edge==MB_FILLED_EDGE) ? UINT32_MAX:0)

/****************************************/
/* Structures and Typedef               */
/****************************************/

/* standard value typedefs */
/** Unsigned 8 bit value type */
typedef uint8_t Uint8;
/** Unsigned 16 bit value type */
typedef uint16_t Uint16;
/** Unsigned 32 bit value type*/
typedef uint32_t Uint32;
/** Unsigned 64 bit value type */
typedef uint64_t Uint64;
/** Signed 8 bit value type */
typedef int8_t Sint8;
/** Signed 16 bit value type */
typedef int16_t Sint16;
/** Signed 32 bit value type */
typedef int32_t Sint32;
/** Signed 64 bit value type */
typedef int64_t Sint64;

/** grey-scale pixels value type */
typedef uint8_t PIX8;
/** Pixels line pointers type */
typedef PIX8 *PLINE;

/** Signed 32-bit pixels value type */
typedef uint32_t PIX32;
/** 32-bit pixels line pointers type */
typedef PIX32 *PLINE32;

/** Images structure with the width, height and depth;
 * the pixels array (PIXARRAY) and entry point array to 
 * each line of the image (PLINES)
 *
 * \image html imageStruct.jpg
 * \image latex imageStruct.jpg "Image structure and variables" width=15cm
 */
typedef struct {
    /** The width of the image */
    Uint32 width;
    /** The height of the image */
    Uint32 height;
    /** The depth of the image */
    Uint32 depth;
    /** accesors to pixel lines */
    PLINE *PLINES;
    /** pixel array */
    PIX8 *PIXARRAY;
} MB_Image;

/** enumerate for grid : either square or hexagonal
 */
enum MB_grid_t {
    MB_HEXAGONAL_GRID = 1,
    MB_SQUARE_GRID = 0
};

/** enumerate for edge mode : either empty or filled */
enum MB_edgemode_t {
    MB_EMPTY_EDGE = 0,
    MB_FILLED_EDGE = 1
};

/****************************************/

/* Neighboring directions are coded by the numbers as follows:
 * on the rectangular grid
 *  8  1  2
 *  7  0  3
 *  6  5  4
 *
 * on the hexagonal grid
 *   6  1
 * 5   0  2
 *   4  3
 */

#ifdef __cplusplus
}
#endif

#endif

