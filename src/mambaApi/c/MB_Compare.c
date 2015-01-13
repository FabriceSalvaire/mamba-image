/**
 * \file MB_Compare.c
 * \author Nicolas Beucher
 * \date 6-6-2008
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
 * Compares the pixels of two 32-bits images lines
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in pointer on the source image pixel line
 * \param linoff_in offset inside the source image line
 * \param plines_cmp pointer on the comparaison image pixel line
 * \param linoff_cmp offset inside the comparaison image  line
 * \param bytes_in number of bytes inside the line
 * \param x position of the first discordant pixel in x
 */
static INLINE void COMP_LINE_32(PLINE *plines_out, Uint32 linoff_out,
                                PLINE *plines_in, Uint32 linoff_in,
                                PLINE *plines_cmp, Uint32 linoff_cmp,
                                Uint32 bytes_in, Sint32 *x )
{
    Uint32 i;

    PIX32 *pin = (PIX32 *) (*plines_in+linoff_in);
    PIX32 *pcmp = (PIX32 *) (*plines_cmp+linoff_cmp);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out);

    for(i=0;i<bytes_in;i+=4,pin++,pout++,pcmp++){
        if((*pin)!=(*pcmp)){
            *x = (Sint32) (i>>2);
            *pout = *pin;
            break;
        }
    }
}

/**
 * Compares the pixels of two 8-bits images lines
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in pointer on the source image pixel line
 * \param linoff_in offset inside the source image line
 * \param plines_cmp pointer on the comparaison image pixel line
 * \param linoff_cmp offset inside the comparaison image  line
 * \param bytes_in number of bytes inside the line
 * \param x position of the first discordant pixel in x
 */
static INLINE void COMP_LINE_8(PLINE *plines_out, Uint32 linoff_out,
                               PLINE *plines_in, Uint32 linoff_in,
                               PLINE *plines_cmp, Uint32 linoff_cmp,
                               Uint32 bytes_in, Sint32 *x )
{
    Uint32 j;

    PLINE pin = (PLINE) (*plines_in+linoff_in);
    PLINE pcmp = (PLINE) (*plines_cmp+linoff_cmp);
    PLINE pout = (PLINE) (*plines_out+linoff_out);

    for(j=0;j<bytes_in;j++,pin++,pout++,pcmp++){
        if((*pin)!=(*pcmp)){
            *x = (Sint32) j;
            *pout = *pin;
            break;
        }
    }
}


/**
 * Compares the pixels of two binary images lines
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in pointer on the source image pixel line
 * \param linoff_in offset inside the source image line
 * \param plines_cmp pointer on the comparaison image pixel line
 * \param linoff_cmp offset inside the comparaison image  line
 * \param bytes_in number of bytes inside the line
 * \param x position of the first discordant pixel in x
 */
static INLINE void COMP_LINE_1(PLINE *plines_out, Uint32 linoff_out,
                               PLINE *plines_in, Uint32 linoff_in,
                               PLINE *plines_cmp, Uint32 linoff_cmp,
                               Uint32 bytes_in, Sint32 *x )
{
    Uint32 j;
    binaryT pix_reg_in,pix_reg_cmp,pix_reg_index;
    
    binaryT value2shift = 1L; /* <- when the position of the difference is */
                             /* known we shift this value to it*/

    binaryT *pin = (binaryT *) (*plines_in+linoff_in);
    binaryT *pcmp = (binaryT *) (*plines_cmp+linoff_cmp);
    binaryT *pout = (binaryT *) (*plines_out+linoff_out);

    for(j=0;j<bytes_in;j+=BYTEPERWORD,pin++,pout++,pcmp++){
        pix_reg_in = (*pin);
        pix_reg_cmp = (*pcmp);
        if(pix_reg_in!=pix_reg_cmp){
            /* the two pixels registers are different */
            /* we will look for the first pixel in it that is */
            /* different */
            for(pix_reg_index=0; 
                (pix_reg_index<BYTEPERWORD*CHARBIT) && 
                ((pix_reg_in&1)==(pix_reg_cmp&1)); 
                pix_reg_index++){
                /* shifting to access pixel by pixel */
                pix_reg_in = pix_reg_in>>1;
                pix_reg_cmp = pix_reg_cmp>>1;
            }
            /* we put the pixel to 1 in the out image */
            (*pout) |= value2shift<<pix_reg_index;
            *x = (Sint32) (j*CHARBIT + pix_reg_index);
            break;
        }
        
    }
}
 
/**
 * Performs a comparaison between a source image and a given base image.
 * \param src the source image 
 * \param cmp the image to which the source image is compared
 * \param dest destination image 
 * \param px position in x of the first different pixel between the two images (-1 if images are similar)
 * \param py position in y of the first different pixel between the two images (-1 if images are similar)
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Compare(MB_Image *src, MB_Image *cmp, MB_Image *dest, Sint32 *px, Sint32 *py) 
{
    Uint32 i;
    Sint32 x,y;
    PLINE *plines_in, *plines_cmp, *plines_out;
    Uint32 linoff_out, linoff_in, linoff_cmp, bytes_in;
    
    /* verification over image size compatibility */
    if (!MB_CHECK_SIZE_3(src, cmp, dest)) {
        return ERR_BAD_SIZE;
    }
    /* verification over depth */
    if(src->depth != dest->depth) {
        return ERR_BAD_DEPTH;
    }

    /* Setting up line pointers */
    plines_in = &src->PLINES[MB_Y_TOP(src)];
    plines_cmp = &cmp->PLINES[MB_Y_TOP(cmp)];
    plines_out = &dest->PLINES[MB_Y_TOP(dest)];
    linoff_in = MB_LINE_OFFSET(src);
    linoff_cmp = MB_LINE_OFFSET(cmp);
    linoff_out = MB_LINE_OFFSET(dest);
    bytes_in = MB_LINE_COUNT(src);
    
    /* Position of the first pixel which is different in the two images */
    /* the value is -1 when the two images are similar */
    x = -1;
    y = -1;

    switch(MB_PROBE_PAIR(src,cmp)) {

    case MB_PAIR_1_1:
        for(i = 0; i < src->height; i++, plines_in++, plines_out++, plines_cmp++) {
            COMP_LINE_1(plines_out, linoff_out, plines_in, linoff_in, plines_cmp, linoff_cmp, bytes_in, &x);
            /* As soon as a difference has been found the function ends */
            if (x != -1) {
                y = i;
                break;
            }
        }
        break;

    case MB_PAIR_8_8:
        for(i = 0; i < src->height; i++, plines_in++, plines_out++, plines_cmp++) {
            COMP_LINE_8(plines_out, linoff_out, plines_in, linoff_in, plines_cmp, linoff_cmp, bytes_in, &x);
            /* As soon as a difference has been found the function ends */
            if (x != -1) {
                y = i;
                break;
            }
        }
        break;
        
    case MB_PAIR_32_32:
        for(i = 0; i < src->height; i++, plines_in++, plines_out++, plines_cmp++) {
            COMP_LINE_32(plines_out, linoff_out, plines_in, linoff_in, plines_cmp, linoff_cmp, bytes_in, &x);
            /* As soon as a difference has been found the function ends */
            if (x != -1) {
                y = i;
                break;
            }
        }
        break;

    default:
        return ERR_BAD_DEPTH;
        break;
    }

    /* value output */
    *px = x;
    *py = y;

    return NO_ERR;
}

