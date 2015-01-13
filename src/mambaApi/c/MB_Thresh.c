/**
 * \file MB_Thresh.c
 * \author Nicolas Beucher
 * \date 6-7-2008
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
 * Applies the treshold function to a line of an 8-bits image.
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in pointer on the source image pixel line
 * \param linoff_in offset inside the source image line
 * \param bytes_in number of bytes inside the line in im_out
 * \param ublow low value for the threshold
 * \param ubhigh high value for threshold
 */
static INLINE void THRESH_LINE_8_1(
                    PLINE *plines_out, Uint32 linoff_out, 
                    PLINE *plines_in, Uint32 linoff_in,
                    Uint32 bytes_in, PIX8 ublow, PIX8 ubhigh )
{
    Uint32 i,j;
    binaryT pixel2bin;
    binaryT bin_pixels;

    PLINE pin = (PLINE) (*plines_in+linoff_in);
    binaryT *pout = (binaryT *) (*plines_out+linoff_out);

    for(i=0;i<bytes_in;i+=BYTEPERWORD,pout++){
        /* the output binary pixel (bit) are all set to zero first */
        bin_pixels = 0;
        /* pixel2bin represent the first pixel (LSB) */
        pixel2bin = 1;
        for(j=0; j<BYTEPERWORD*CHARBIT; j++, pin++) {
            /* if the read value on pin is in range, the pixel bit is set to 1 */
            if (((*pin)>=ublow) && ((*pin)<=ubhigh)) {
                bin_pixels|=pixel2bin;
            }
            /* Shifting so that pixel2bin represent the next pixel */
            pixel2bin=pixel2bin<<1;
        }
        *pout = bin_pixels;
    }
}

/**
 * Applies the treshold function to a line of an 32-bits image.
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in pointer on the source image pixel line
 * \param linoff_in offset inside the source image line
 * \param bytes_in number of bytes inside the line in im_out
 * \param low low value for the threshold
 * \param high high value for threshold
 */
static INLINE void THRESH_LINE_32_1(PLINE *plines_out, Uint32 linoff_out, 
                   PLINE *plines_in, Uint32 linoff_in,
                   Uint32 bytes_in, PIX32 low, PIX32 high )
{
    Uint32 i,j;
    binaryT pixel2bin;
    binaryT bin_pixels;

    PIX32 *pin = (PIX32 *) (*plines_in+linoff_in);
    binaryT *pout = (binaryT *) (*plines_out+linoff_out);

    for(i=0;i<bytes_in;i+=BYTEPERWORD,pout++){
        /* the output binary pixel (bit) are all set to zero first */
        bin_pixels = 0;
        /* pixel2bin represent the first pixel (LSB) */
        pixel2bin = 1;
        for(j=0; j<BYTEPERWORD*CHARBIT; j++, pin++) {
            /* if the read value on pin is in range, the pixel bit is set to 1 */
            if (((*pin)>=low) && ((*pin)<=high)) {
                bin_pixels|=pixel2bin;
            }
            /* Shifting so that pixel2bin represent the next pixel */
            pixel2bin=pixel2bin<<1;
        }
        *pout = bin_pixels;
    }
}

/**
 * Fills a binary image according to the following rules :
 * if pixel value lower than low or higher than high the binary pixel
 * is set to 0, in other cases the pixel is set to 1.
 * \param src source image
 * \param dest destination image
 * \param low low value for threshold
 * \param high high value for treshold
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Thresh(MB_Image *src, MB_Image *dest, Uint32 low, Uint32 high)
{
    Uint32 i;
    PLINE *plines_in, *plines_out;
    Uint32 linoff_out, linoff_in, bytes_in;
    
    /* verification over image size compatibility */
    if (!MB_CHECK_SIZE_2(src, dest)) {
        return ERR_BAD_SIZE;
    }
    
    /* checking input parameters value */
    if (low>high) {
        return ERR_BAD_VALUE;
    }
    
    /* Setting up line pointers */
    plines_in = &src->PLINES[MB_Y_TOP(src)];
    plines_out = &dest->PLINES[MB_Y_TOP(dest)];
    linoff_in = MB_LINE_OFFSET(src);
    linoff_out = MB_LINE_OFFSET(dest);
    /* for this function the number of bytes is the number of */
    /* the binary image */
    bytes_in = MB_LINE_COUNT(dest);

    /* The dest image is a binary */
    switch(MB_PROBE_PAIR(src,dest)) {

    case MB_PAIR_8_1:
        for (i = 0; i < src->height; i++, plines_in++, plines_out++) {
            THRESH_LINE_8_1(plines_out, linoff_out, plines_in, linoff_in, bytes_in, (PIX8) low, (PIX8) high);
        }
        break;

    case MB_PAIR_32_1:
        for (i = 0; i < src->height; i++, plines_in++, plines_out++) {
            THRESH_LINE_32_1(plines_out, linoff_out, plines_in, linoff_in, bytes_in, (PIX32) low, (PIX32) high);
        }
        break;

    default:
        return ERR_BAD_DEPTH;
        break;
    }

    return NO_ERR;
}
