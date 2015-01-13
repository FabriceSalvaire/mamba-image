/**
 * \file MB_Pixel.c
 * \author Nicolas Beucher
 * \date 29-1-2009
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
 * Puts the pixel value inside a 1-bit line.
 * \param plines pointer on the source image pixel line
 * \param linoff offset inside the source image line
 * \param x the position in the line
 * \param value the value of the pixel (0 or 1)
 */
static INLINE void PUT_PIXEL_1(PLINE *plines, Uint32 linoff,
                               Uint32 x, binaryT value)
{
    binaryT v;
    binaryT mask;
    binaryT offset;
   
    binaryT *px = (binaryT *) (*plines + linoff + (x/(CHARBIT*BYTEPERWORD))*BYTEPERWORD);
    offset = (binaryT) (x%(CHARBIT*BYTEPERWORD));
   
    v = value<<offset;
    mask = ~(1L<<offset);
   
    *px = ((*px)&mask) + v;
}

/**
 * Puts the pixel value inside a 8-bits line.
 * \param plines pointer on the source image pixel line
 * \param linoff offset inside the source image line
 * \param x the position in the line
 * \param value the value of the pixel (0 to 255)
 */
static INLINE void PUT_PIXEL_8(PLINE *plines, Uint32 linoff,
                               Uint32 x, PIX8 value)
{
    PLINE px = (PLINE) (*plines + linoff + x);
    *px = value;
}

/**
 * Puts the pixel value inside a 32-bits line.
 * \param plines pointer on the source image pixel line
 * \param linoff offset inside the source image line
 * \param x the position in the line
 * \param value the value of the pixel
 */
static INLINE void PUT_PIXEL_32(PLINE *plines, Uint32 linoff,
                                Uint32 x, PIX32 value)
{
    PIX32 *px = (PIX32 *) (*plines + linoff + x*4);
    *px = value;
}

/**
 * Puts the pixel value inside the image at the given position
 * \param dest the image 
 * \param pixVal the pixel value
 * \param x position in x of the pixel targeted
 * \param y position in y of the pixel targeted
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_PutPixel(MB_Image *dest, Uint32 pixVal, Uint32 x, Uint32 y) 
{
    PLINE *plines;
    Uint32 linoff;
    binaryT v;

    /* verification over the size */
    if (x>=dest->width || y>=dest->height) {
        return ERR_BAD_SIZE;
    }
   
    /* Setting up line pointers */
    plines = &dest->PLINES[MB_Y_TOP(dest) + y];
    linoff = MB_LINE_OFFSET(dest);

    switch(dest->depth) {
        case 1:
            v = (binaryT) (pixVal!=0);
            PUT_PIXEL_1(plines,linoff, x, v);
            break;
        case 8:
            PUT_PIXEL_8(plines,linoff, x, (PIX8) pixVal);
            break;
        case 32:
            PUT_PIXEL_32(plines,linoff, x, (PIX32) pixVal);
            break;
        default:
            return ERR_BAD_DEPTH;
            break;
    }
    
    return NO_ERR;
}

/**
 * Gets the pixel value from a 1-bit line.
 * \param plines pointer on the source image pixel line
 * \param linoff offset inside the source image line
 * \param x the position in the line
 * \param value the value of the pixel (0 or 1)
 */
static INLINE void GET_PIXEL_1(PLINE *plines, Uint32 linoff,
                               Uint32 x, Uint32 *value)
{
    binaryT mask;
    binaryT offset;
   
    binaryT *px = (binaryT *) (*plines + linoff + (x/(CHARBIT*BYTEPERWORD))*BYTEPERWORD);
    offset = (binaryT) (x%(CHARBIT*BYTEPERWORD));

    mask = (1L<<offset);
   
    *value = (Uint32) (((*px)&mask) != 0);
}

/**
 * Gets the pixel value from a 8-bits line.
 * \param plines pointer on the source image pixel line
 * \param linoff offset inside the source image line
 * \param x the position in the line
 * \param value the value of the pixel (0 to 255)
 */
static INLINE void GET_PIXEL_8(PLINE *plines, Uint32 linoff,
                               Uint32 x, Uint32 *value)
{
    PLINE px = (PLINE) (*plines + linoff + x);
    *value = (Uint32) *px;
}

/**
 * Gets the pixel value inside a 32-bits line.
 * \param plines pointer on the source image pixel line
 * \param linoff offset inside the source image line
 * \param x the position in the line
 * \param value the value of the pixel
 */
static INLINE void GET_PIXEL_32(PLINE *plines, Uint32 linoff,
                               Uint32 x, Uint32 *value)
{
    PIX32 *px = (PIX32 *) (*plines + linoff + x*4);
    *value = (Uint32) *px;
}

/**
 * Gets the pixel value inside the image at the given position
 * \param src the image 
 * \param pixVal the returned pixel value
 * \param x position in x of the pixel targeted
 * \param y position in y of the pixel targeted
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_GetPixel(MB_Image *src, Uint32 *pixVal, Uint32 x, Uint32 y) 
{
    PLINE *plines;
    Uint32 linoff;

    /* verification over the size */
    if (x>=src->width || y>=src->height) {
        return ERR_BAD_SIZE;
    }
   
    /* Setting up line pointers */
    plines = &src->PLINES[MB_Y_TOP(src) + y];
    linoff = MB_LINE_OFFSET(src);

    switch(src->depth) {
        case 1:
            GET_PIXEL_1(plines,linoff, (binaryT) x, pixVal);
            break;
        case 8:
            GET_PIXEL_8(plines,linoff, x, pixVal);
            break;
        case 32:
            GET_PIXEL_32(plines,linoff, x, pixVal);
            break;
        default:
            return ERR_BAD_DEPTH;
            break;
    }
    
    return NO_ERR;
}
