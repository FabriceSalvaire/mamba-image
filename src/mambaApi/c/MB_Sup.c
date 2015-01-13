/**
 * \file MB_Sup.c
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
 * Determines the superior value on 32-bits pixels.
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in1 pointer on the source image 1 pixel line
 * \param linoff_in1 offset inside the source image 1 line
 * \param plines_in2 pointer on the source image 2 pixel line
 * \param linoff_in2 offset inside the source image 2 line
 * \param bytes_in number of bytes inside the line
 */
static INLINE void SUP_LINE32(PLINE *plines_out, Uint32 linoff_out,
                              PLINE *plines_in1, Uint32 linoff_in1,
                              PLINE *plines_in2, Uint32 linoff_in2,
                              Uint32 bytes_in)
{
    Uint32 i;

    PIX32 *pin1 = (PIX32 *) (*plines_in1+linoff_in1);
    PIX32 *pin2 = (PIX32 *) (*plines_in2+linoff_in2);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out);

    for(i=0;i<bytes_in;i+=4,pin1++,pin2++,pout++){
        *pout = (*pin1)>(*pin2) ? (*pin1) : (*pin2);
    }
}

/**
 * Determines the superior value on 8-bits pixels.
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in1 pointer on the source image 1 pixel line
 * \param linoff_in1 offset inside the source image 1 line
 * \param plines_in2 pointer on the source image 2 pixel line
 * \param linoff_in2 offset inside the source image 2 line
 * \param bytes_in number of bytes inside the line
 */
static INLINE void SUP_LINE(PLINE *plines_out, Uint32 linoff_out,
                            PLINE *plines_in1, Uint32 linoff_in1,
                            PLINE *plines_in2, Uint32 linoff_in2,
                            Uint32 bytes_in)
{
    Uint32 i;
    
#ifdef __SSE2__
    
    __m128i *pin1 = (__m128i*) (*plines_in1+linoff_in1);
    __m128i *pin2 = (__m128i*) (*plines_in2+linoff_in2);
    __m128i *pout = (__m128i*) (*plines_out+linoff_out);
    
    for(i=0;i<bytes_in;i+=16,pin1++,pin2++,pout++) {
        (*pout) = _mm_max_epu8((*pin2),(*pin1));
    }
    
#else

    PLINE pin1 = (PLINE) (*plines_in1+linoff_in1);
    PLINE pin2 = (PLINE) (*plines_in2+linoff_in2);
    PLINE pout = (PLINE) (*plines_out+linoff_out);

    for(i=0;i<bytes_in;i++,pin1++,pin2++,pout++){
        *pout = (*pin1)>(*pin2) ? (*pin1) : (*pin2);
    }
#endif
}

/**
 * Determines the superior value between the pixels of two images.
 * The result is put in the corresponding pixel position in the destination image.
 * \param src1 image 1
 * \param src2 image 2
 * \param dest destination image
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Sup(MB_Image *src1, MB_Image *src2, MB_Image *dest)
{
    Uint32 i;
    PLINE *plines_in1, *plines_in2, *plines_out;
    Uint32 linoff_out, linoff_in1, linoff_in2, bytes_in;
    
    /* verification over image size compatibility */
    if (!MB_CHECK_SIZE_3(src1, src2, dest)) {
        return ERR_BAD_SIZE;
    }

    /* Setting up line pointers */
    plines_in1 = &src1->PLINES[MB_Y_TOP(src1)];
    plines_in2 = &src2->PLINES[MB_Y_TOP(src2)];
    plines_out = &dest->PLINES[MB_Y_TOP(dest)];
    linoff_in1 = MB_LINE_OFFSET(src1);
    linoff_in2 = MB_LINE_OFFSET(src2);
    linoff_out = MB_LINE_OFFSET(dest);
    bytes_in = MB_LINE_COUNT(src1);

    /* destination image should have the depth that source image */
    if(dest->depth != src1->depth)
        return ERR_BAD_DEPTH;

    /* The two source images must have the same */
    /* depth */
    switch(MB_PROBE_PAIR(src1,src2)) {    
    /* For binary image sup is the result of a OR operation */
    case MB_PAIR_1_1:
        return MB_Or(src1, src2, dest);
        break;
    
    case MB_PAIR_8_8:
        for(i = 0; i < src1->height; i++, plines_out++, plines_in1++, plines_in2++) {
            SUP_LINE(plines_out,linoff_out,plines_in1,linoff_in1,plines_in2,linoff_in2,bytes_in);
        }
        break;

    case MB_PAIR_32_32:
        for(i = 0; i < src1->height; i++, plines_out++, plines_in1++, plines_in2++) {
            SUP_LINE32(plines_out,linoff_out,plines_in1,linoff_in1,plines_in2,linoff_in2,bytes_in);
        }
        break;

    default:
        return ERR_BAD_DEPTH;
        break;
    }

      return NO_ERR;
}
