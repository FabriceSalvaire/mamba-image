/**
 * \file MB_Inv.c
 * \author Nicolas Beucher
 * \date 11-25-2007
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
 * Inverts (NOT operation) the binary pixels of the source line.
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in pointer on the source image pixel line
 * \param linoff_in offset inside the source image line
 * \param bytes_in number of bytes inside the line
 */
static INLINE void INVERT_LINE1(PLINE *plines_out, Uint32 linoff_out,
                                PLINE *plines_in, Uint32 linoff_in,
                                Uint32 bytes_in)
{
    Uint32 i;

    binaryT *pin = (binaryT *) (*plines_in+linoff_in);
    binaryT *pout = (binaryT *) (*plines_out+linoff_out);

    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin++,pout++){
        *pout = ~(*pin);
    }
}

/**
 * Inverts (NOT operation) the pixels of the source line (8-bits pixels).
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in pointer on the source image pixel line
 * \param linoff_in offset inside the source image line
 * \param bytes_in number of bytes inside the line
 */
static INLINE void INVERT_LINE8(PLINE *plines_out, Uint32 linoff_out,
                                PLINE *plines_in, Uint32 linoff_in,
                                Uint32 bytes_in)
{
    Uint32 i;

#ifdef __SSE2__
    __m128i v = _mm_set1_epi8((char) 255);

    __m128i *pin = (__m128i *) (*plines_in+linoff_in);
    __m128i *pout = (__m128i *) (*plines_out+linoff_out);
    
    for(i=0;i<bytes_in;i+=16,pout++,pin++) {
        (*pout) = _mm_sub_epi8(v,(*pin));
    }
    
#else

    binaryT *pin = (binaryT *) (*plines_in+linoff_in);
    binaryT *pout = (binaryT *) (*plines_out+linoff_out);

    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin++,pout++){
        *pout = ~(*pin);
    }
#endif
}

/**
 * Inverts (two-complement operation) the 32-bits pixels of the source line.
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in pointer on the source image pixel line
 * \param linoff_in offset inside the source image line
 * \param bytes_in number of bytes inside the line
 */
static INLINE void INVERT_LINE32(PLINE *plines_out, Uint32 linoff_out,
                                 PLINE *plines_in, Uint32 linoff_in,
                                 Uint32 bytes_in)
{
    Uint32 i;

    binaryT *pin = (binaryT *) (*plines_in+linoff_in);
    binaryT *pout = (binaryT *) (*plines_out+linoff_out);

    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin++,pout++){
        *pout = ~(*pin);
    }
}

/**
 * Inverts the pixels values (negation) of the source image.
 * \param src source image
 * \param dest destination image
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Inv(MB_Image *src, MB_Image *dest) {
    PLINE *plines_in, *plines_out;
    Uint32 linoff_in, linoff_out;
    Uint32 bytes_in;
    Uint32 i;
    
    /* verification over image size compatibility */
    if (!MB_CHECK_SIZE_2(src, dest)) {
        return ERR_BAD_SIZE;
    }
    
    /* Setting up line pointers */
    plines_in  = &src->PLINES[MB_Y_TOP(src)];
    plines_out = &dest->PLINES[MB_Y_TOP(dest)];
    linoff_in = MB_LINE_OFFSET(src);
    linoff_out = MB_LINE_OFFSET(dest);
    bytes_in = MB_LINE_COUNT(src);

    /* Source and dest must have the same depth */
    switch(MB_PROBE_PAIR(src,dest)) {
    case MB_PAIR_1_1:
        for (i = 0; i < src->height; i++, plines_in++, plines_out++) {
            INVERT_LINE1( plines_out, linoff_out, plines_in, linoff_in, bytes_in );
        }
        break;
        
    case MB_PAIR_8_8:
        for (i = 0; i < src->height; i++, plines_in++, plines_out++) {
            INVERT_LINE8( plines_out, linoff_out, plines_in, linoff_in, bytes_in );
        }
        break;

    case MB_PAIR_32_32:
        for (i = 0; i < src->height; i++, plines_in++, plines_out++) {
            INVERT_LINE32( plines_out, linoff_out, plines_in, linoff_in, bytes_in );
        }
        break;

    default:
        return ERR_BAD_DEPTH;
        break;
    }

    return NO_ERR;
} 
