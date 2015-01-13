/**
 * \file MB_BinHitOrMiss.c
 * \author Nicolas Beucher
 * \date 11-15-2007
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
 * Performs a binary Hit-or-Miss operation on image imIn using the structuring elements es0 and es1.
 * Structuring elements are integer values coding which direction must be taken into account.
 * es0 indicating which neighbor of the current pixel will be checked for 0 value.
 * es1 those which will be evaluated for 1 value.
 *
 * For example, in hexagonal grid, it means that if you want to look for a pattern where the neighbors in
 * direction 6 and 1 are true while the current pixel is false just as neighbors 2 and 5, 
 * you will encode this in the elements es0 and es1 like this :
 *   1 1
 *  0 0 0
 *   X X
 * es0 = 1+4+32
 * es1 = 64+2
 *
 * \param src output image
 * \param dest input image (must be different of src)
 * \param es0 structuring element for 0 value.
 * \param es1 structuring element for 1 value.
 * \param grid grid configuration
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_BinHitOrMiss(MB_Image *src, MB_Image *dest, Uint32 es0, Uint32 es1, enum MB_grid_t grid)
{
    MB_errcode ERC;

    Uint32 mask,ngb_nb;
    Uint32 dir;
    
    /* verification over depth and size */
    if (!MB_CHECK_SIZE_2(src, dest)) {
        return ERR_BAD_SIZE;
    }

    /* images must be binary */
    if (MB_PROBE_PAIR(src, dest)!=MB_PAIR_1_1) {
        return ERR_BAD_DEPTH;
    }
    
    /* verification over src and dest to know */
    /* if they point to the same image which is forbidden */
    if (src==dest) {
        return ERR_BAD_PARAMETER;
    }

    /* central point, mask == 1 */
    if (es1 & 1)
        ERC = MB_Copy(src, dest);
    else
        if (es0 & 1)
            ERC = MB_Inv(src, dest);
        else
            ERC = MB_ConSet(dest, 1);

    if (ERC == NO_ERR) {
        /* the neighbors */
        for(dir = 1, mask = 2, ngb_nb = (grid == MB_HEXAGONAL_GRID) ? 6 : 8;
            dir <= ngb_nb;
            dir++, mask <<= 1) {
            /* Neighbors marked in the ES1 have the priority over those from ES0 */
            if (es1 & mask)
                MB_InfNbb( src, dest, dir, 1, grid, MB_EMPTY_EDGE);
            else
                if (es0 & mask)
                    MB_DiffNbb( src, dest, dir, grid, MB_EMPTY_EDGE);
        }
    }

    return ERC;
}
