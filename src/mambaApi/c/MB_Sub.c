/**
 * \file MB_Sub.c
 * \author Nicolas Beucher
 * \date 13-6-2007
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
 * Subtracts the 1-bit pixels of a line to the 8-bits pixels of another. 
 * The results is put in a 8-bits pixels line.
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in1 pointer on the source image 1-bit pixel line
 * \param linoff_in1 offset inside the source image line
 * \param plines_in2 pointer on the source image 8-bit pixel line
 * \param linoff_in2 offset inside the source image line
 * \param bytes number of bytes inside the line
 */
static INLINE void SUB_LINE_8_1_8(PLINE *plines_out, Uint32 linoff_out,
                                  PLINE *plines_in1, Uint32 linoff_in1,
                                  PLINE *plines_in2, Uint32 linoff_in2,
                                  Uint32 bytes_in)
{
    Uint32 i,u;
    binaryT pix_reg;
    Sint16 prov;
    
    PLINE pin1 = (PLINE) (*plines_in1+linoff_in1);
    binaryT *pin2 = (binaryT *) (*plines_in2+linoff_in2);
    PLINE pout = (PLINE) (*plines_out+linoff_out);

    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin2++){
        pix_reg = *pin2;
        for(u=0;u<BYTEPERWORD*CHARBIT;u++,pin1++,pout++){
            prov = (Sint16) *pin1 - (pix_reg&1);
            if (prov < 0) {
                *pout = 0;
            } else {
                *pout = (PIX8) prov;
            }
            /* next pixel in the register */
            pix_reg = pix_reg>>1;
        }
    }
}

/**
 * Subtracts the 8-bits pixels of a line to the 8-bits pixels of another. 
 * The results is put in a 8-bits pixels line.
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in1 pointer on the source image 1-bit pixel line
 * \param linoff_in1 offset inside the source image line
 * \param plines_in2 pointer on the source image 8-bit pixel line
 * \param linoff_in2 offset inside the source image line
 * \param bytes number of bytes inside the line
 */
static INLINE void SUB_LINE_8_8_8(PLINE *plines_out, Uint32 linoff_out,
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
        (*pout) = _mm_subs_epu8((*pin1),(*pin2));
    }
    
#else
    Sint16 prov;
    
    PLINE pin1 = (PLINE) (*plines_in1+linoff_in1);
    PLINE pin2 = (PLINE) (*plines_in2+linoff_in2);
    PLINE pout = (PLINE) (*plines_out+linoff_out);

    for(i=0;i<bytes_in;i++,pin1++,pin2++,pout++){
        prov = ((Sint16) *pin1) - *pin2; 
        if (prov < 0) {
            *pout = 0;
        } else {
            *pout = (PIX8) prov;
        }
    }
#endif
} 

/**
 * Subtracts the 8-bits pixels of a line to the 8-bits pixels of another. 
 * The results is put in a 32-bits pixels line.
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in1 pointer on the source image 1-bit pixel line
 * \param linoff_in1 offset inside the source image line
 * \param plines_in2 pointer on the source image 8-bit pixel line
 * \param linoff_in2 offset inside the source image line
 * \param bytes number of bytes inside the line
 */
static INLINE void SUB_LINE_8_8_32(PLINE *plines_out, Uint32 linoff_out,
                                   PLINE *plines_in1, Uint32 linoff_in1,
                                   PLINE *plines_in2, Uint32 linoff_in2,
                                   Uint32 bytes_in)
{
    Uint32 i;
    
    PLINE pin1 = (PLINE) (*plines_in1+linoff_in1);
    PLINE pin2 = (PLINE) (*plines_in2+linoff_in2);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out);

    for(i=0;i<bytes_in;i++,pin1++,pin2++,pout++){
        *pout = (PIX32) *pin1 - *pin2;
    }
}

/**
 * Subtracts the 32-bits pixels of a line to the 32-bits pixels of another. 
 * The results is put in a 32-bits pixels line.
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in1 pointer on the source image 1-bit pixel line
 * \param linoff_in1 offset inside the source image line
 * \param plines_in2 pointer on the source image 8-bit pixel line
 * \param linoff_in2 offset inside the source image line
 * \param bytes number of bytes inside the line
 */
static INLINE void SUB_LINE_32_32_32(PLINE *plines_out, Uint32 linoff_out,
                                     PLINE *plines_in1, Uint32 linoff_in1,
                                     PLINE *plines_in2, Uint32 linoff_in2,
                                     Uint32 bytes_in) 
{
    Uint32 i;
    
    PIX32 *pin1 = (PIX32 *) (*plines_in1+linoff_in1);
    PIX32 *pin2 = (PIX32 *) (*plines_in2+linoff_in2);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out);

    for(i=0;i<bytes_in;i+=4,pin1++,pin2++,pout++){
        *pout = *pin1 - *pin2;
    }
}

/**
 * Subtracts the 8-bits pixels of a line to the 32-bits pixels of another. 
 * The results is put in a 32-bits pixels line.
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in1 pointer on the source image 1-bit pixel line
 * \param linoff_in1 offset inside the source image line
 * \param plines_in2 pointer on the source image 8-bit pixel line
 * \param linoff_in2 offset inside the source image line
 * \param bytes number of bytes inside the line
 */
static INLINE void SUB_LINE_8_32_32(PLINE *plines_out, Uint32 linoff_out,
                                    PLINE *plines_in1, Uint32 linoff_in1,
                                    PLINE *plines_in2, Uint32 linoff_in2,
                                    Uint32 bytes_in) 
{
    Uint32 i;
    
    PLINE pin1 = (PLINE) (*plines_in1+linoff_in1);
    PIX32 *pin2 = (PIX32 *) (*plines_in2+linoff_in2);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out);

    for(i=0;i<bytes_in;i+=4,pin1++,pin2++,pout++){
        *pout = *pin1 - *pin2;
    }
}

/**
 * Subtracts the 32-bits pixels of a line to the 8-bits pixels of another. 
 * The results is put in a 32-bits pixels line.
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in1 pointer on the source image 1-bit pixel line
 * \param linoff_in1 offset inside the source image line
 * \param plines_in2 pointer on the source image 8-bit pixel line
 * \param linoff_in2 offset inside the source image line
 * \param bytes number of bytes inside the line
 */
static INLINE void SUB_LINE_32_8_32(PLINE *plines_out, Uint32 linoff_out,
                                    PLINE *plines_in1, Uint32 linoff_in1,
                                    PLINE *plines_in2, Uint32 linoff_in2,
                                    Uint32 bytes_in) 
{
    Uint32 i;
    
    PIX32 *pin1 = (PIX32 *) (*plines_in1+linoff_in1);
    PLINE pin2 = (PLINE) (*plines_in2+linoff_in2);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out);

    for(i=0;i<bytes_in;i++,pin1++,pin2++,pout++){
        *pout = *pin1 - *pin2;
    }
}

/**
 * Subtracts the values of pixels of the second image to the values of
 * the pixels in the first image
 * \param src1 image 1
 * \param src2 image 2
 * \param dest image resulting of the subtraction 
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Sub(MB_Image *src1, MB_Image *src2, MB_Image *dest)
{
    PLINE *plines_in1, *plines_in2, *plines_out;
    Uint32 linoff_in1, linoff_in2, linoff_out, bytes_in;
    Uint32 i;
    
    /* verification over image size compatibility */
    if (!MB_CHECK_SIZE_3(src1, src2, dest)) {
        return ERR_BAD_SIZE;
    }
    
    /* Destination image depth must be at least the same or higher */
    /* than image 1 or 2 depth otherwise the function returns with an error. */
    if( (dest->depth < src1->depth) || (dest->depth < src2->depth) )
        return ERR_BAD_DEPTH;
    
    /* Setting up the pointers */
    plines_in1 = &src1->PLINES[MB_Y_TOP(src1)];
    plines_in2 = &src2->PLINES[MB_Y_TOP(src2)];
    plines_out = &dest->PLINES[MB_Y_TOP(dest)];
    
    /* Setting up offset */
    linoff_in1 = MB_LINE_OFFSET(src1);
    linoff_in2 = MB_LINE_OFFSET(src2);
    linoff_out = MB_LINE_OFFSET(dest);
    bytes_in = MB_LINE_COUNT(src2);
    
    switch(MB_PROBE_PAIR(src1,src2)) {
    
    /* subtracting a binary image to binary image amounts to a set difference*/
    case MB_PAIR_1_1:
        return MB_Diff(src1, src2, dest);
        break;
    
    /* subtracting a binary image to an 8-bit image */
    case MB_PAIR_8_1:
        if(dest->depth !=8)
            return ERR_BAD_DEPTH;
        for (i = 0; i < src1->height; i++, plines_out++, plines_in1++, plines_in2++) {
            SUB_LINE_8_1_8(plines_out, linoff_out, plines_in1, linoff_in1, plines_in2, linoff_in2, bytes_in);
        }
        break;

    /* subtracting a binary image to an 8-bit image */
    case MB_PAIR_8_8:
        if(dest->depth == 8) {
            for (i = 0; i < src1->height; i++, plines_out++, plines_in1++, plines_in2++) {
                SUB_LINE_8_8_8(plines_out, linoff_out, plines_in1, linoff_in1, plines_in2, linoff_in2, bytes_in);
            }
        }
        if(dest->depth == 32) {
            for (i = 0; i < src1->height; i++, plines_out++, plines_in1++, plines_in2++) {
                SUB_LINE_8_8_32(plines_out, linoff_out, plines_in1, linoff_in1, plines_in2, linoff_in2, bytes_in);
            }
        }
        break;

    case MB_PAIR_32_32:
        for (i = 0; i < src1->height; i++, plines_out++, plines_in1++, plines_in2++) {
            SUB_LINE_32_32_32(plines_out, linoff_out, plines_in1, linoff_in1, plines_in2, linoff_in2, bytes_in);
        }
        break;

    case MB_PAIR_8_32:
        for (i = 0; i < src1->height; i++, plines_out++, plines_in1++, plines_in2++) {
            SUB_LINE_8_32_32(plines_out, linoff_out, plines_in1, linoff_in1, plines_in2, linoff_in2, bytes_in);
        }
        break;

    case MB_PAIR_32_8:
        for (i = 0; i < src1->height; i++, plines_out++, plines_in1++, plines_in2++) {
            SUB_LINE_32_8_32(plines_out, linoff_out, plines_in1, linoff_in1, plines_in2, linoff_in2, bytes_in);
        }
        break;

    default:
        return ERR_BAD_DEPTH;
        break;
    }
    
    return NO_ERR;
}
