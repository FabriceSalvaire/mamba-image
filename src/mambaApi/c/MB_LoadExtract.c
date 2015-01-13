/**
 * \file MB_LoadExtract.c
 * \author Nicolas Beucher
 * \date 5-28-2008
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
 * Loads a grey scale image data with data given in argument
 * \param image the image to fill
 * \param indata the data to fill the image with (complete pixels values)
 * \param len the length of data given
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Load8(MB_Image *image, PIX8 *indata, Uint32 len) {
    Uint32 i;
    PLINE *plines;
    Uint32 linoff;
    PLINE p;

    /* Only 8 bit image can be loaded */
    if (image->depth!=8) {
        return ERR_BAD_DEPTH;
    }
    /* the data given must be sufficient to fill the image */
    if (len!=(image->height*image->width)) {
        return ERR_LOAD_DATA;
    }

    /* Setting up line pointers */
    /* and offset to avoid edge of the image */
    plines = &image->PLINES[MB_Y_TOP(image)];
    linoff = MB_X_LEFT(image);

    /* proceeding line by line */
    for (i = 0; i < image->height; i++, plines++) {
        p = (PLINE) (*plines+linoff);
        MB_memcpy(p,indata+i*image->width,image->width);
    }

    return NO_ERR;
}

/**
 * Loads a 32-bits image data with data given in argument
 * \param image the image to fill
 * \param indata the data to fill the image with (complete pixels values)
 * \param len the length of data given
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Load32(MB_Image *image, PIX8 *indata, Uint32 len) {
    Uint32 i;
    PLINE *plines;
    Uint32 linoff;
    PLINE p;

    /* Only 32 bit image can be loaded */
    if (image->depth!=32) {
        return ERR_BAD_DEPTH;
    }
    /* the data given must be sufficient to fill the image */
    if (len!=(image->height*image->width*4)) {
        return ERR_LOAD_DATA;
    }

    /* Setting up line pointers */
    /* and offset to avoid edge of the image */
    plines = &image->PLINES[MB_Y_TOP(image)];
    linoff = MB_X_LEFT(image);

    /* proceeding line by line */
    for (i = 0; i < image->height; i++, plines++) {
        p = (PLINE) (*plines+linoff);
        MB_memcpy(p,indata+i*image->width*4,image->width*4);
    }

    return NO_ERR;
}

/**
 * Loads an image data with data given in argument
 * \param image the image to fill
 * \param indata the data to fill the image with (complete pixels values)
 * \param len the length of data given
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Load(MB_Image *image, PIX8 *indata, Uint32 len) {
    MB_errcode err = NO_ERR;
    
    switch(image->depth) {
        case 8:
            err = MB_Load8(image, indata, len);
            break;
        case 32:
            err = MB_Load32(image, indata, len);
            break;
        default:
            err = ERR_BAD_DEPTH;
            break;
    }
    
    return err;
}


/**
 * Reads a grey scale image data contents and put it in an array
 * \param image the image to read
 * \param outdata pointer to the array created (malloc) and filled with the 
 * pixel data of the image
 * \param len the length in bytes of data extracted
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Extract8(MB_Image *image, PIX8 **outdata, Uint32 *len) {
    Uint32 i;
    PLINE *plines;
    Uint32 linoff;
    PLINE pout;

    if (image->depth!=8) {
        return ERR_BAD_DEPTH;
    }

    /* allocating the memory */
    *outdata = MB_malloc((image->height*image->width)*sizeof(PIX8));

    /* Setting up line pointers */
    /* and offset to avoid edge of the image */
    plines = &image->PLINES[MB_Y_TOP(image)];
    linoff = MB_X_LEFT(image);

    /* proceeding line by line */
    for (i = 0; i < image->height; i++, plines++) {
        pout = (PLINE) (*plines+linoff);
        MB_memcpy(*outdata+i*image->width,pout,image->width);
    }
    
    *len = image->height*image->width;

    return NO_ERR;
}

/**
 * Reads a 32-bits image data contents and put it in an array
 * \param image the image to read
 * \param outdata pointer to the array created (malloc) and filled with the 
 * pixel data of the image
 * \param len the length in bytes of data extracted
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Extract32(MB_Image *image, PIX8 **outdata, Uint32 *len) {
    Uint32 i;
    PLINE *plines;
    Uint32 linoff;
    PLINE pout;

    if (image->depth!=32) {
        return ERR_BAD_DEPTH;
    }

    /* allocating the memory */
    *outdata = MB_malloc((image->height*image->width*4)*sizeof(PIX8));

    /* Setting up line pointers */
    /* and offset to avoid edge of the image */
    plines = &image->PLINES[MB_Y_TOP(image)];
    linoff = MB_X_LEFT(image);

    /* proceeding line by line */
    for (i = 0; i < image->height; i++, plines++) {
        pout = (PLINE) (*plines+linoff);
        MB_memcpy(*outdata+i*image->width*4,pout,image->width*4);
    }
    
    *len = image->height*image->width*4;

    return NO_ERR;
}

/**
 * Reads an image data contents and put it in an array
 * \param image the image to read
 * \param outdata pointer to the array created (malloc) and filled with the 
 * pixel data of the image
 * \param len the length in bytes of data extracted (0 if an error occured)
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Extract(MB_Image *image, PIX8 **outdata, Uint32 *len) {
    MB_errcode err = NO_ERR;
    
    switch(image->depth) {
        case 8:
            err = MB_Extract8(image, outdata, len);
            break;
        case 32:
            err = MB_Extract32(image, outdata, len);
            break;
        default:
            *len = 0;
            err = ERR_BAD_DEPTH;
            break;
    }
    
    return err;
}
