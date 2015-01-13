/**
 * \file MB_Convert.c
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

/* Local functions */
MB_errcode MB_Convert1to8(MB_Image *src, MB_Image *dest);
MB_errcode MB_Convert8to1(MB_Image *src, MB_Image *dest);

/**
 * Converts an image of a given depth into another depth
 *
 * This function does not depend on the window computation currently
 * set.
 *
 * \param src source image
 * \param dest destination image 
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Convert(MB_Image *src, MB_Image *dest) {

    /* verification over image size compatibility */
    if (!MB_CHECK_SIZE_2(src, dest)) {
        return ERR_BAD_SIZE;
    }

    /* Comparing the depth of the src and the destination */
    switch (MB_PROBE_PAIR(src, dest)) {
    case MB_PAIR_1_1:;
    case MB_PAIR_8_8:
    case MB_PAIR_32_32:
        return MB_Copy(src,dest);
        break;
    case MB_PAIR_1_8:
        return MB_Convert1to8(src,dest);
        break;
    case MB_PAIR_8_1:
        return MB_Convert8to1(src,dest);
        break;
    case MB_PAIR_1_32:
    case MB_PAIR_8_32:
    case MB_PAIR_32_1:
    case MB_PAIR_32_8:
        break;
    default:
        return ERR_BAD_DEPTH;
        break;
    }

    /* If this point is reached we can assume there was an error*/
    return ERR_BAD_DEPTH;
}

/**
 * Converts a binary image to an 8-bit image.
 * Pixels to True are set to 255 and to 0 otherwise
 * \param src source image
 * \param dest destination image 
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Convert1to8(MB_Image *src, MB_Image *dest) {
    Uint32 i,j,u,pix_reg;
    PLINE *plines_in, *plines_out;
    Uint32 linoff_out, linoff_in;
    Uint32 *pin;
    Uint8 *pout;

    /* verification to ensure depth coherency with function purpose */
    if(MB_PROBE_PAIR(src, dest) != MB_PAIR_1_8)
        return ERR_BAD_DEPTH;
        
    /* Setting up line pointers */
    plines_in = &src->PLINES[MB_Y_TOP(src)];
    plines_out = &dest->PLINES[MB_Y_TOP(dest)];
    linoff_in = MB_X_LEFT(src);
    linoff_out = MB_X_LEFT(dest);
    
    /* converting the 1-bit values in 8-bit values */
    for(j=0; j<src->height; j++,plines_in++,plines_out++) {
        pin = (Uint32 *) (*plines_in+linoff_in);
        pout = (Uint8 *) (*plines_out+linoff_out);
        for(i=0; i<src->width; i+=32,pin++) { /* <- this function is not windowed */
            pix_reg = *pin;
            for(u=0;u<32;u++,pout++){
                /* for all the pixels inside the pixel register */
                *pout = (pix_reg&1) ? 0xFF : 0;
                pix_reg = pix_reg>>1;
            }    
        }
    }
    
    return NO_ERR;
}

/**
 * Converts an 8-bit image to a binary image.
 * Pixels at 255 are set to True and to False otherwise
 * \param src source image
 * \param dest destination image 
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Convert8to1(MB_Image *src, MB_Image *dest) {    
    Uint32 i,j;
    Sint32 u;
    PLINE *plines_in, *plines_out;
    Uint32 linoff_out, linoff_in;
    Uint32 *pout, pix_reg;

    /* verification to ensure depth coherency with function purpose */
    if(MB_PROBE_PAIR(src, dest) != MB_PAIR_8_1)
        return ERR_BAD_DEPTH;

    /* Setting up line pointers */
    plines_in = &src->PLINES[MB_Y_TOP(src)];
    plines_out = &dest->PLINES[MB_Y_TOP(dest)];
    linoff_in = MB_X_LEFT(src);
    linoff_out = MB_X_LEFT(dest);
    
    /* converting the 8-bit values in 1-bit values */
    /* if 8-bit value is equal to 255 (white) the bit is set to 1 */
    /* and 0 in all other cases */
    for(j=0; j<src->height; j++,plines_in++,plines_out++) {
        pout = (Uint32 *) (*plines_out+linoff_out);
        for(i=0; i<src->width; i+=32,pout++) { /* <- this function is not windowed */
            /* building the pixel register */
            pix_reg = 0;
            for(u=31;u>-1;u--){
                pix_reg = (pix_reg<<1) | (*(*plines_in+linoff_in+i+u)==0xFF);
            }
            *pout = pix_reg;
        }
    }    
    
    return NO_ERR;
}
