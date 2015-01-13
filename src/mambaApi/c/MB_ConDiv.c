/**
 * \file MB_ConDiv.c
 * \author Nicolas Beucher
 * \date 6-18-2008
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
 * Divides a 8-bits pixels image by a constant value and places the 
 * result in an 8-bits image. 
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in pointer on the source image 1 pixel line
 * \param linoff_in offset inside the source image 1 line
 * \param bytes_in number of bytes inside the line
 * \param value the constant value
 */
static INLINE void CONDIV_LINE_8_8(PLINE *plines_out, Uint32 linoff_out,
                                   PLINE *plines_in, Uint32 linoff_in,
                                   Uint32 bytes_in, Uint32 value)
{
    Uint32 i;
    PIX8 satvalue;

    PLINE pin = (PLINE) (*plines_in+linoff_in);
    PLINE pout = (PLINE) (*plines_out+linoff_out);
    
    if (value>255) {
        satvalue = 255;
    } else if (value<1) {
        satvalue = 1;
    } else {
        satvalue = (PIX8) value;
    }
    
    for(i=0;i<bytes_in;i++,pin++,pout++){
        *pout = (*pin)/satvalue;
    }
}

/**
 * Divides a 32-bits pixels image by a constant value and places the 
 * result in an 32-bits image. 
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in pointer on the source image 1 pixel line
 * \param linoff_in offset inside the source image 1 line
 * \param bytes_in number of bytes inside the line
 * \param value the constant value
 */
static INLINE void CONDIV_LINE_32_32(PLINE *plines_out, Uint32 linoff_out,
                                     PLINE *plines_in, Uint32 linoff_in,
                                     Uint32 bytes_in, Uint32 value)
{
    Uint32 i;
    Uint32 remainder;

    PIX32 *pin = (PIX32 *) (*plines_in+linoff_in);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out);
    
    for(i=0;i<bytes_in;i+=4,pin++,pout++){
        remainder = (*pin%value);
        *pout = ((*pin-remainder)/value);
    }
}

/**
 * Divides (quotient) the pixels of an image by a constant value.
 * \param src the source image
 * \param value the constant value used in the division
 * \param dest the image resulting of the division of image 1 by the value. 
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_ConDiv(MB_Image *src, Uint32 value, MB_Image *dest)
{
    Uint32 i;
    PLINE *plines_in, *plines_out;
    Uint32 linoff_out, linoff_in, bytes_in;
    
    /* verification over image size compatibility */
    if (!MB_CHECK_SIZE_2(src, dest)) {
        return ERR_BAD_SIZE;
    }

    /* Setting up line pointers */
    plines_in = &src->PLINES[MB_Y_TOP(src)];
    plines_out = &dest->PLINES[MB_Y_TOP(dest)];
    linoff_in = MB_LINE_OFFSET(src);
    linoff_out = MB_LINE_OFFSET(dest);
    bytes_in = MB_LINE_COUNT(src);
    
    /* verification over value (cannot divide by 0) */
    if (value==0) {
        return ERR_BAD_VALUE;
    }

    /* The two images must have the same */
    /* depth */
    switch(MB_PROBE_PAIR(src,dest)) {

    case MB_PAIR_8_8:
        /* division with saturation */
        for (i = 0;i < src->height;i++, plines_in++, plines_out++) {
            CONDIV_LINE_8_8( plines_out, linoff_out, plines_in, linoff_in, bytes_in, value );
        }
        break;

    case MB_PAIR_32_32:
        for (i = 0;i < src->height;i++, plines_in++, plines_out++) {
            CONDIV_LINE_32_32( plines_out, linoff_out, plines_in, linoff_in, bytes_in, value );
        }
        break;

    default:
        return ERR_BAD_DEPTH;
        break;
    }

    return NO_ERR;
} 


