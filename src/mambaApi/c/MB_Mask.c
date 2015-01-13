/**
 * \file MB_Mask.c
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

/**
 * Converts a binary image line in a grey scale image (8-bits) line using
 * value maskf to replace 0 and maskt to replace 1.
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in pointer on the source image pixel line
 * \param linoff_in offset inside the source image line
 * \param bytes_in number of bytes inside the line
 * \param maskf for 0 (false) pixel value
 * \param maskt for 1 (true) pixel value
 */
 static INLINE void MASK_LINE8(PLINE *plines_out, Uint32 linoff_out,
                               PLINE *plines_in, Uint32 linoff_in,
                               Uint32 bytes_in, PIX8 maskf, PIX8 maskt)
{
    Uint32 i,u;
    binaryT pix_reg;
    
    binaryT *pin = (binaryT *) (*plines_in+linoff_in);
    PLINE pout = (PLINE) (*plines_out+linoff_out);
        
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin++) {
        pix_reg = *pin;
        for(u=0;u<BYTEPERWORD*CHARBIT;u++,pout++){
            /* for all the pixels in the register */
            *pout = (pix_reg&1) ? maskt : maskf;
            /* next pixel */
            pix_reg = pix_reg>>1;
        }    
    }
}

/**
 * Converts a binary image line in a 32-bits image line using
 * value maskf to replace 0 and maskt to replace 1.
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in pointer on the source image pixel line
 * \param linoff_in offset inside the source image line
 * \param bytes_in number of bytes inside the line
 * \param maskf for 0 (false) pixel value
 * \param maskt for 1 (true) pixel value
 */
 static INLINE void MASK_LINE32(PLINE *plines_out, Uint32 linoff_out,
                                PLINE *plines_in, Uint32 linoff_in,
                                Uint32 bytes_in, PIX32 maskf, PIX32 maskt)
{
    Uint32 i,u;
    binaryT pix_reg;
    
    binaryT *pin = (binaryT *) (*plines_in+linoff_in);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out);
        
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin++) {
        pix_reg = *pin;
        for(u=0;u<BYTEPERWORD*CHARBIT;u++,pout++){
            /* for all the pixels in the register */
            *pout = (pix_reg&1) ? maskt : maskf;
            /* next pixel */
            pix_reg = pix_reg>>1;
        }    
    }
}

/**
 * Converts a binary image in a grey scale image (8-bits) or in a 32-bits image
 * using value maskf to replace 0 and maskt to replace 1.
 * \param src binary source image
 * \param dest destination image 
 * \param maskf for 0 (false) pixel value
 * \param maskt for 1 (true) pixel value
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Mask(MB_Image *src, MB_Image *dest, Uint32 maskf, Uint32 maskt) {
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
    linoff_in = MB_X_LEFT(src);
    linoff_out = MB_X_LEFT(dest);
    bytes_in = MB_LINE_COUNT(src);

    /* verification to ensure depth coherency with function purpose */
    switch(MB_PROBE_PAIR(src, dest)) {
        case MB_PAIR_1_8:
            /* converting the 1-bit values in 8-bit values */
            for(i=0;i<src->height;i++,plines_in++,plines_out++) {
                MASK_LINE8(plines_out, linoff_out, plines_in, linoff_in, bytes_in, (PIX8) maskf, (PIX8) maskt);
            }
            break;
        case MB_PAIR_1_32:
            /* converting the 1-bit values in 32-bit values */
            for(i=0;i<src->height;i++,plines_in++,plines_out++) {
                MASK_LINE32(plines_out, linoff_out, plines_in, linoff_in, bytes_in, (PIX32) maskf, (PIX32) maskt);
            }
            break;
        default:
            return ERR_BAD_DEPTH;
            break;
    }
    
    return NO_ERR;
}

