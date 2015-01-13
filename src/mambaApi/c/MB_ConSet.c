/**
 * \file MB_ConSet.c
 * \author Nicolas Beucher
 * \date 11-29-2007
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

/**
 * Fills a line with a pattern value
 * \param plines pointer on the destination image pixel line
 * \param linoff offset inside the destination image line
 * \param bytes number of bytes inside the line
 * \param pattern the pattern filling the line
 */
static INLINE void FILL_LINE(PLINE *plines, Uint32 linoff, Uint32 bytes, Uint32 pattern)
{
    Uint32 i;

    Uint32 *pout = (Uint32 *) (*plines+linoff);

    for(i=0;i<bytes;i+=4,pout++){
        *pout = pattern;
    }
}

/**
 * Fills an image with a specific value
 * \param dest the image
 * \param value the value to fill the image
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_ConSet(MB_Image *dest, Uint32 value) {
    Uint32 i,pattern32;
    PLINE *plines;
    Uint32 linoff, bytes;

    /* Setting up line pointers */
    plines = &dest->PLINES[MB_Y_TOP(dest)];
    linoff = MB_LINE_OFFSET(dest);
    bytes = MB_LINE_COUNT(dest);
    
    /* pattern depends on the depth of the image */
    switch(dest->depth) {
    case 1:
        /* pattern computation */
        /* in binary image, value is eitheir one or zero */
        pattern32 = (value) ? 0XFFFFFFFF : 0;
        break;

    case 8:
        /* pattern computation */
        /* the pattern is set by a concatenation of value to */
        /* reach the size of an Uint32 */
        pattern32 = value;
        pattern32 = pattern32<0xFF ? value : 0xFF;
        pattern32 |= pattern32 << CHARBIT;
        pattern32 |= pattern32 << (CHARBIT*2);
        break;

    case 32:
        /* pretending the signed 32 bit is unsigned */
        pattern32 = value;
        break;
        
    default:
        return ERR_BAD_DEPTH;
        break;
    }

    /* Lines fill */
    for(i = 0; i < dest->height; i++, plines++) {
        FILL_LINE( plines, linoff, bytes, pattern32 );
    }

    return NO_ERR;
} 
