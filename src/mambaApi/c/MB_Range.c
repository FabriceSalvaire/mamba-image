/**
 * \file MB_Range.c
 * \author Nicolas Beucher
 * \date 5-29-2008
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
#include "mambaApi_loc.h"
#include <stdint.h>

/* functions for each depth */

static INLINE MB_errcode MB_Range1(MB_Image *src, Uint32 *min, Uint32 *max) {
    Uint32 bytes_in;
    Uint32 i,j;
    PLINE *plines;
    Uint32 linoff;
    Uint32 *p;
    
    /* default value */
    /* this way, the first comparison will always be in */
    /* favor of the pixel */

    *max = 0;
    *min = 1;

    /* Setting up line pointers */
    /* and offset to avoid edge of the image */
    plines = &src->PLINES[MB_Y_TOP(src)];
    bytes_in = MB_LINE_COUNT(src);
    linoff = MB_LINE_OFFSET(src);

    /* proceeding line by line */
    for (i = 0; i < src->height; i++, plines++) {
        p = (Uint32 *) (*plines+linoff);
        for(j = 0; j < bytes_in; j+=4, p++) {
            if (*p != 0xFFFFFFFF ) {
                *min = 0;
            }
            if (*p != 0) {
                *max = 1;
            }
            if ( (*max == 1) &&(*min == 0) ) {
                /* if this is the case they will no longer */
                /* change so better stop here ;-) */
                return NO_ERR;
            }
        }
    }

    return NO_ERR;
}

static INLINE MB_errcode MB_Range8(MB_Image *src, Uint32 *min, Uint32 *max) {
    Uint32 i,j;
    PLINE *plines;
    Uint32 linoff, bytes_in;
    PLINE p;
    
    /* default value */
    /* this way, the first comparison will always be in */
    /* favor of the pixel */
    *min = UINT8_MAX;
    *max = 0;

    /* Setting up line pointers */
    /* and offset to avoid edge of the image */
    plines = &src->PLINES[MB_Y_TOP(src)];
    linoff = MB_LINE_OFFSET(src);
    bytes_in = MB_LINE_COUNT(src);

    /* proceeding line by line */
    for (i = 0; i < src->height; i++, plines++) {
        p = (PLINE) (*plines+linoff);
        for(j = 0; j < bytes_in; j++, p++) {
            if (*p < *min ) {
                *min = (Uint32) *p;
            }
            if (*p > *max ) {
                *max = (Uint32) *p;
            }
        }
    }

    return NO_ERR;
}

static INLINE MB_errcode MB_Range32(MB_Image *src,Uint32 *min, Uint32 *max) {
    Uint32 i,j;
    PLINE *plines;
    Uint32 linoff, bytes_in;
    PIX32 *p, loc_min, loc_max;
    
    /* default value */
    /* this way, the first comparison will always be in */
    /* favor of the pixel */
    loc_min = UINT32_MAX;
    loc_max = 0;

    /* Setting up line pointers */
    /* and offset to avoid edge of the image */
    plines = &src->PLINES[MB_Y_TOP(src)];
    linoff = MB_LINE_OFFSET(src);
    bytes_in = MB_LINE_COUNT(src);

    /* proceeding line by line */
    for(i = 0; i < src->height; i++, plines++) {
        p = (PIX32 *) (*plines+linoff);
        for(j = 0; j < bytes_in; j+=4, p++) {
            if (*p < loc_min ) {
                loc_min = *p;
            }
            if (*p > loc_max ) {
                loc_max = *p;
            }
        }
    }

    /* locally computed value are stored in pointed spaces */
    *min = (Uint32) loc_min;
    *max = (Uint32) loc_max;

    return NO_ERR;
}

/**
 * gives the minimum and maximum values of the image pixels
 * i.e its range.
 * \param src source image
 * \param min the minimum value of the pixels
 * \param max the maximum value of the pixels
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Range(MB_Image *src, Uint32 *min, Uint32 *max) {

    /* Comparing the depth of the src and the destination */
    switch (src->depth) {
    case 1:
        return MB_Range1(src,min,max);
        break;
    case 8:
        return MB_Range8(src,min,max);
        break;
    case 32:
        return MB_Range32(src,min,max);
        break;
    default:
        return ERR_BAD_DEPTH;
        break;
    }

    /* If this point is reached we can assume there was an error*/
    return ERR_BAD_VALUE;
}

/**
 * gives the minimum and maximum possible values of the image pixels
 * given the image depth
 * \param src source image
 * \param min the minimum possible value of the pixels
 * \param max the maximum possible value of the pixels
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_depthRange(MB_Image *src, Uint32 *min, Uint32 *max) {

    /* Comparing the depth of the src and the destination */
    switch (src->depth) {
    case 1:
        *min = 0;
        *max = 1;
        return NO_ERR;
        break;
    case 8:
        *min = 0;
        *max = UINT8_MAX;
        return NO_ERR;
        break;
    case 32:
        *min = 0;
        *max = UINT32_MAX;
        return NO_ERR;
        break;
    default:
        return ERR_BAD_DEPTH;
        break;
    }

    /* If this point is reached we can assume there was an error*/
    return ERR_BAD_VALUE;
}

