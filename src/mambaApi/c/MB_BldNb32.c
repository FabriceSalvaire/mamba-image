/**
 * \file MB_BldNb32.c
 * \author Nicolas Beucher
 * \date 06-09-2010
 *
 */
 
/*
 * Copyright (c) <2010>, <Nicolas BEUCHER and ARMINES for the Centre de 
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

/****************************************/
/* Base functions                       */
/****************************************/
/* The functions described here realise the basic operation */
/* needed to shift pixels in any directions */

/**
 * Used to rebuild the pixels of a line with a line directly above or below.
 * No shifting inside the line.
 */
static INLINE void BLD_LINE(PLINE *plines_germ, PLINE *plines_germ_nbr, Uint32 linoff_germ,
                            PLINE *plines_mask, Uint32 linoff_mask,
                            Uint32 bytes_in, Uint64 *volume)
{
    Uint32 i;
    Uint64 vol=0;
    PIX32 a;
    
    PIX32 *germ = (PIX32 *) (*plines_germ+linoff_germ); /* inout image */
    PIX32 *mask = (PIX32 *) (*plines_mask+linoff_mask);
    PIX32 *germ_nbr = (PIX32 *) (*plines_germ_nbr+linoff_germ); /* inout image shifted */
    
    for(i=0;i<bytes_in;i+=4,germ++,mask++,germ_nbr++) {
        a = (*germ)>(*germ_nbr) ? (*germ) : (*germ_nbr);
        a = a<(*mask) ? a : (*mask);
        *germ = a;
        vol += a;
    }

    *volume += vol;
}

/**
 * Used to rebuild the pixels of a line when this line is touching the edge.
 */
static INLINE void BLD_EDGE_LINE(PLINE *plines_germ, Uint32 linoff_germ,
                                   PLINE *plines_mask, Uint32 linoff_mask,
                                   Uint32 bytes_in, Uint64 *volume )
{
    Uint32 i;
    Uint64 vol=0;
    PIX32 edge_val = GREY_FILL_VALUE(MB_EMPTY_EDGE);
    
    PIX32 a;

    PIX32 *germ = (PIX32 *) (*plines_germ+linoff_germ); /* inout image */
    PIX32 *mask = (PIX32 *) (*plines_mask+linoff_mask);
    
    for(i=0;i<bytes_in;i+=4,germ++,mask++) {
        a = (*germ)>(edge_val) ? (*germ) : edge_val;
        a = a<(*mask) ? a : (*mask);
        *germ = a;
        vol += a;
    }
    
    *volume += vol;
}

/**
 * Used to rebuild the pixels of a line using the pixels of an above, below line
 * but shifted in the left direction. In fact, to emulate this, we do
 * not look at directly into the above pixels but we look into the above to the right
 * pixels which would have been directly above had the left shifting really
 * happened.
 */
static INLINE void BLD_LINE_LEFT(PLINE *plines_germ, PLINE *plines_germ_nbr, Uint32 linoff_germ,
                                 PLINE *plines_mask, Uint32 linoff_mask, 
                                 Uint32 bytes_in, Uint64 *volume) 
{
    Uint32 i;
    Uint64 vol=0;
    PIX32 edge_val = GREY_FILL_VALUE(MB_EMPTY_EDGE);
    PIX32 a;

    PIX32 *germ = (PIX32 *) (*plines_germ+linoff_germ+bytes_in-4);  /* inout image */
    PIX32 *mask = (PIX32 *) (*plines_mask+linoff_mask+bytes_in-4);
    PIX32 *germ_nbr = (PIX32 *) (*plines_germ_nbr+linoff_germ+bytes_in); /* inout image shifted */
    
    /* the first pixel is inside the edge */
    a = (*germ)>(edge_val) ? (*germ) : edge_val;
    a = a<(*mask) ? a : (*mask);
    *germ = a;
    vol = a;
    germ--;
    mask--;
    germ_nbr--;
    for(i=0;i<bytes_in-4;i+=4,germ--,mask--,germ_nbr--) {
        a = (*germ)>(*germ_nbr) ? (*germ) : (*germ_nbr);
        a = a<(*mask) ? a : (*mask);
        *germ = a;
        vol += a;
    }
    
    *volume += vol;
}

/**
 * Used to rebuild the pixels of a line using the pixels of 
 * the same line but shifted in the left direction. 
 */
static INLINE void BLD_LINE_LEFT_HORZ(PLINE *plines_germ, Uint32 linoff_germ,
                                      PLINE *plines_mask, Uint32 linoff_mask, 
                                      Uint32 bytes_in, Uint64 *volume) 
{
    Uint32 i;
    Uint64 vol=0;
    PIX32 edge_val, a;

    PIX32 *germ = (PIX32 *) (*plines_germ+linoff_germ+bytes_in-4);  /* inout image */
    PIX32 *mask = (PIX32 *) (*plines_mask+linoff_mask+bytes_in-4);
    PIX32 *germ_nbr = (PIX32 *) (*plines_germ+linoff_germ+bytes_in); /* inout image shifted */
    
    edge_val = GREY_FILL_VALUE(MB_EMPTY_EDGE);
    
    /* the first pixel is inside the edge */
    a = (*germ)>(edge_val) ? (*germ) : edge_val;
    a = a<(*mask) ? a : (*mask);
    *germ = a;
    vol = a;
    germ--;
    mask--;
    germ_nbr--;
    for(i=0;i<bytes_in-4;i+=4,germ--,mask--,germ_nbr--) {
        a = (*germ)>(*germ_nbr) ? (*germ) : (*germ_nbr);
        a = a<(*mask) ? a : (*mask);
        *germ = a;
        vol += a;
    }
    
    *volume += vol;
}

/**
 * Used to rebuild the pixels of a line using the pixels of an above, below line
 * but shifted in the right direction. In fact, to emulate this, we do
 * not look at directly into the above pixels but we look into the above to the left
 * pixels which would have been directly above had the right shifting really
 * happened.
 */
static INLINE void BLD_LINE_RIGHT(PLINE *plines_germ, PLINE *plines_germ_nbr, Uint32 linoff_germ,
                                  PLINE *plines_mask, Uint32 linoff_mask, 
                                  Uint32 bytes_in, Uint64 *volume) 
{
    Uint32 i;
    Uint64 vol=0;
    PIX32 edge_val = GREY_FILL_VALUE(MB_EMPTY_EDGE);
    PIX32 a;

    PIX32 *germ = (PIX32 *) (*plines_germ+linoff_germ); /* inout image */
    PIX32 *mask = (PIX32 *) (*plines_mask+linoff_mask);
    PIX32 *germ_nbr = (PIX32 *) (*plines_germ_nbr+linoff_germ-4); /* inout image shifted */
    
    /* the first pixel is inside the edge */
    a = (*germ)>(edge_val) ? (*germ) : edge_val;
    a = a<(*mask) ? a : (*mask);
    *germ = a;
    vol = a;
    germ++;
    mask++;
    germ_nbr++;
    for(i=0;i<bytes_in-4;i+=4,germ++,mask++,germ_nbr++) {
        a = (*germ)>(*germ_nbr) ? (*germ) : (*germ_nbr);
        a = a<(*mask) ? a : (*mask);
        *germ = a;
        vol += a;
    }
    
    *volume += vol;
}

/**
 * Used to rebuild the pixels of a line using the pixels of 
 * the same line but shifted in the right direction.
 */
static INLINE void BLD_LINE_RIGHT_HORZ(PLINE *plines_germ, Uint32 linoff_germ,
                                       PLINE *plines_mask, Uint32 linoff_mask, 
                                       Uint32 bytes_in, Uint64 *volume) 
{
    Uint32 i;
    Uint64 vol=0;
    PIX32 edge_val, a;

    PIX32 *germ = (PIX32 *) (*plines_germ+linoff_germ); /* inout image */
    PIX32 *mask = (PIX32 *) (*plines_mask+linoff_mask);
    PIX32 *germ_nbr = (PIX32 *) (*plines_germ+linoff_germ-4); /* inout image shifted */
    
    edge_val = GREY_FILL_VALUE(MB_EMPTY_EDGE);
    
    /* the first pixel is inside the edge */
    a = (*germ)>(edge_val) ? (*germ) : edge_val;
    a = a<(*mask) ? a : (*mask);
    *germ = a;
    vol = a;
    germ++;
    mask++;
    germ_nbr++;
    for(i=0;i<bytes_in-4;i+=4,germ++,mask++,germ_nbr++) {
        a = (*germ)>(*germ_nbr) ? (*germ) : (*germ_nbr);
        a = a<(*mask) ? a : (*mask);
        *germ = a;
        vol += a;
    }
    
    *volume += vol;
}

/****************************************/
/* Direction functions                  */
/****************************************/
/* The functions are described in a separate file to communalize with other */
/* build functions */
#include "MB_BldDirection.c"

/****************************************/
/* Main function                        */
/****************************************/

/**
 * (re)Builds an image according to a direction and a mask image.
 * The direction depends on the grid used (see MB_ngh.h for definitions of directions).
 *
 * \param mask the mask image
 * \param srcdest the rebuild image
 * \param dirnum the direction number
 * \param pVolume the computed volume of the output image
 * \param grid the grid used (either square or hexagonal)
 *
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_BldNb32(MB_Image *mask, MB_Image *srcdest, Uint32 dirnum, Uint64 *pVolume, enum MB_grid_t grid) {

    Uint32 linoff_mask, linoff_inout;
    Uint32 bytes_in;
    PLINE *plines_mask, *plines_inout;
    TSWITCHEP *fn;

    /* error management */
    /* verification over image size compatibility */
    if (!MB_CHECK_SIZE_2(mask, srcdest)) {
        return ERR_BAD_SIZE;
    }
    /* grid value and possible direction are connected, grid value is the */
    /* maximum number of directions */
    if(dirnum>6 && grid==MB_HEXAGONAL_GRID) {
        return ERR_BAD_DIRECTION;
    }
    if(dirnum>8 && grid==MB_SQUARE_GRID) {
        return ERR_BAD_DIRECTION;
    }
    /* Only binary images can be processed */
    switch (MB_PROBE_PAIR(mask, srcdest)) {
    case MB_PAIR_32_32:
        break;
    default:
        return ERR_BAD_DEPTH;
    }

    /* setting up pointers */
    plines_mask = &mask->PLINES[MB_Y_TOP(mask)];
    plines_inout = &srcdest->PLINES[MB_Y_TOP(srcdest)];
    linoff_mask  = MB_LINE_OFFSET(mask);
    linoff_inout = MB_LINE_OFFSET(srcdest);
    bytes_in = MB_LINE_COUNT(mask);

    /*initial value of volume*/
    *pVolume = 0;

    /* Calling the corresponding function */
    fn = SwitchTo[grid][dirnum];
    fn(plines_inout, linoff_inout, plines_mask, linoff_mask, bytes_in, mask->height, pVolume );
    
    return NO_ERR;
}
