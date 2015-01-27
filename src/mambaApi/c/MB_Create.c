/**
 * \file MB_Create.c
 * \author Nicolas Beucher
 * \date 5-27-2008
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

/* image counter */
Uint32 MB_refcounter = 0;

/** Making sure the image size is multiple of 64 for the width */
#define MB_ROUND_W    64
/** Making sure the image size is multiple of 2 for the heigth */
#define MB_ROUND_H    2
/* When considering the limits on the image size, remember that
 * the function computing the volume which returns Uint64
 * should not overflow on the 32-bit images. (that is, max volume
 * for the 32-bit image is 2^64-1) which yields approx 4.3 billions pixels
 * so roughly 65536*65536 images size.
 * However, if we compute a watershed transform, the number of allowed
 * labels is 2^24 (3 lower bytes of the label image). Therefore, if, in
 * a large image, the number of labels exceeds this value, some basins of
 * the watershed transform will share the same label. You must be aware of
 * this possibility.
 */
/** Image limit size in pixels*/
#define MB_MAX_IMAGE_SIZE    ((Uint64)4294967296)

/**
 * Creates an image (memory allocation) with the correct size and depth given as
 * argument. The size is deduced from the requested size given in argument. 
 * The size must be a multiple of MB_ROUND_W for width and MB_ROUND_H for height.
 * The size cannot be greater than MB_MAX_IMAGE_SIZE.
 * \param image the created image
 * \param width the width of the created image 
 * \param height the height of the created image 
 * \param depth the depth of the created image 
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Create(MB_Image *image, Uint32 width, Uint32 height, Uint32 depth) {
    PLINE *plines = NULL;
    PIX8 *pixarray = NULL;
    Uint32 i;
    Uint32 full_w, full_h;
    Uint64 image_size;
    
    /* computation of the corrected size */
    /* w = n*M + r    where 0 <= r < M
       ((w + M-1)//M)*M = (( (n+1)*M + r-1 )//M)*M
       if r = 0: n*M
       else: (n+1)*M
    */
    width = ((width + MB_ROUND_W-1) / MB_ROUND_W) * MB_ROUND_W;
    height = ((height + MB_ROUND_H-1) / MB_ROUND_H) * MB_ROUND_H;

    /* verification over the image size */
    image_size = ((Uint64) width) * height;
    if (!(width > 0 && height > 0 &&
        image_size <= MB_MAX_IMAGE_SIZE) ) {
        return ERR_BAD_IMAGE_DIMENSIONS;
    }

    /* verification over the depth */
    /* acceptable values are 1, 8, or 32 bits */
    if (depth != 1 && depth != 8 && depth != 32)
        return ERR_BAD_DEPTH;
    
    /* full height in pixel with edge */
    /* full_h = height + 2 * 1 */
    full_h = height + Y_TOP + Y_BOTTOM;
    /* full width in bytes with edge */
    /* full_w = (with*depth + 8-1)/8 + 2 * 16 */
    /* ensure with*depth multiple of 8 + 32 */
    full_w = (width*depth + CHARBIT-1)/CHARBIT + X_LEFT + X_RIGHT; /* in bytes */

    /* memory allocation */
    plines = (PLINE *) MB_malloc(full_h*sizeof(PLINE));
    /*
     * We need aligned memory allocation to be sure that it works correctly with
     * SSE2 instructions enabled. Aligned memory allocation is system dependant.
     */
    pixarray = (PIX8 *) MB_aligned_malloc(full_w*full_h, 16);

    if (pixarray == NULL || plines == NULL) {
        /* in case allocation goes wrong */
        MB_aligned_free(pixarray);
        MB_free(plines);
        return ERR_CANT_ALLOCATE_MEMORY;
    } 
    
    /* Fills in the MB_Image structure */
    MB_memset(pixarray, 0, full_w*full_h);
    image->PLINES = plines;
    image->PIXARRAY = pixarray;
    image->depth = depth;
    image->width = width;
    image->height = height;
    image->allocated = 1; /* we must release PIXARRAY */

    for (i = 0; i < full_h; i++, pixarray += full_w)
        plines[i] = (PLINE) pixarray;

    MB_refcounter++;
    
    return NO_ERR;
}

/* Fixme?: Some code is duplicated here */
MB_errcode create_from_numpy(MB_Image *image,
			     PIX8 *pixel_array, Uint32 array_height, Uint32 array_width,
			     Uint32 width, Uint32 line_step, Uint32 depth) {
    PLINE *plines = NULL;
    Uint32 i;
    Uint64 image_size;

    if (pixel_array == NULL)
      return ERR_BAD_VALUE;

    Uint32 height = array_height - (Y_TOP + Y_BOTTOM);
    // Uint32 width = array_width - (X_LEFT + X_RIGHT)/(depth/CHARBIT);

    /* verification over the image size */
    image_size = ((Uint64) width) * height;
    if (!(width > 0 && height > 0 &&
        image_size <= MB_MAX_IMAGE_SIZE) ) {
        return ERR_BAD_IMAGE_DIMENSIONS;
    }

    /* verification over the depth */
    /* acceptable values are 8 or 32 bits */
    if (depth != 8 && depth != 32)
        return ERR_BAD_DEPTH;
   
    /* memory allocation */
    plines = (PLINE *) MB_malloc(array_height*sizeof(PLINE));

    if (plines == NULL) {
        /* in case allocation goes wrong */
        MB_free(plines);
        return ERR_CANT_ALLOCATE_MEMORY;
    } 
    
    /* Fills in the MB_Image structure */
    image->PLINES = plines;
    image->PIXARRAY = pixel_array;
    image->depth = depth;
    image->width = width;
    image->height = height;
    image->allocated = 0; /* we must not release PIXARRAY */

    for (i = 0; i < array_height; i++, pixel_array += line_step)
        plines[i] = (PLINE) pixel_array;
    
    MB_refcounter++;
    
    return NO_ERR;
}

MB_errcode MB_Create_from_numpy8(MB_Image *image, PIX8 *pixel_array,
				 Uint32 array_height, Uint32 array_width, Uint32 width, Uint32 line_step) {
  return create_from_numpy(image, pixel_array, array_height, array_width, width, line_step, 8);
}

MB_errcode MB_Create_from_numpy32(MB_Image *image, PIX32 *pixel_array,
				  Uint32 array_height, Uint32 array_width, Uint32 width, Uint32 line_step) {
  return create_from_numpy(image, (PIX8 *) pixel_array, array_height, array_width, width, line_step, 32);
}

/**
 * Destroys an image (memory freeing)
 * \param image the image to be destroyed
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Destroy(MB_Image *image) {
    if (image == NULL)
        return NO_ERR;

    MB_free(image->PLINES);
    if (image->allocated)
      MB_aligned_free(image->PIXARRAY);
    MB_free(image);
    if (MB_refcounter > 0)
        MB_refcounter--;
    
    return NO_ERR;
}
