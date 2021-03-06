/**
 * \file MB_DiffNbb.c
 * \author Nicolas Beucher
 * \date 6-18-2008
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

/****************************************
 * Base functions                       *
 ****************************************
 * 
 * The functions described here realise the basic operations 
 * needed to compute the pixels accordingly to the main function 
 * purpose (minimum, maximum, ...). They can work at a byte level
 * or a bit level.
 */

/**
 * Computes two whole lines from inout and in source images.
 * Usually this function is called for direction with an Y 
 * shift component with line pointer not pointing at the
 * same line position.
 * \param p_inout pointer on the source/destination image pixel line
 * \param off_inout offset inside the source/destination image line
 * \param p_in pointer on the source image pixel line
 * \param off_in offset inside the source image line
 * \param bytes_in number of bytes inside the line
 */
static INLINE void COMP_LINE(PLINE *p_inout, Uint32 off_inout,
                             PLINE *p_in, Uint32 off_in, Uint32 bytes_in )
{
    Uint32 i;

    binaryT *pin = (binaryT *) (*p_in + off_in);
    binaryT *pinout = (binaryT *) (*p_inout + off_inout);
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin++,pinout++) {
        (*pinout) = (*pinout)&(~*pin);
    }
}

/** 
 * Computes a whole line from inout source image with a predefined
 * edge value.
 * Usually this function is called for direction with an Y 
 * shift component when reaching image edge.
 * \param p_inout pointer on the source/destination image pixel line
 * \param off_inout offset inside the source/destination image line
 * \param bytes_in number of bytes inside the line
 * \param edge_val the value representing the outside edge
 */
static INLINE void COMP_EDGE_LINE(PLINE *p_inout, Uint32 off_inout,
                                    Uint32 bytes_in, binaryT edge_val )
{
    Uint32 i;

    binaryT *pinout = (binaryT *) (*p_inout + off_inout);
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pinout++) {
        (*pinout) = (*pinout)&(~edge_val);
    }
}

/**
 * Computes two whole lines from inout and in source images.
 * Usually this function is called for direction with an X 
 * shift component in the left direction (e.g. for minimum this 
 * means that minimum values are shifted to the left).
 * \param p_inout pointer on the source/destination image pixel line
 * \param off_inout offset inside the source/destination image line
 * \param p_in pointer on the source image pixel line that is shifted
 * \param off_in offset inside the source image line
 * \param bytes_in number of bytes inside the line
 * \param edge_val the value representing the outside edge
 */
static INLINE void COMP_LINE_LEFT(PLINE *p_inout, Uint32 off_inout,
                                  PLINE *p_in, Uint32 off_in,
                                  Uint32 bytes_in, binaryT edge_val )
{
    Uint32 i;
    binaryT pix_reg;

    binaryT *pin = (binaryT *) (*p_in + bytes_in -BYTEPERWORD + off_in);
    binaryT *pinout = (binaryT *) (*p_inout + bytes_in -BYTEPERWORD + off_inout);
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin--,pinout--) {
        pix_reg = (*pin);
        (*pinout) =  (*pinout)& (~((pix_reg>>1) | (edge_val<<SHIFT1BIT)));
        edge_val = pix_reg; /* <- edge_val is used to stored the previous pixel register */
    }
}

/**
 * Computes two whole lines from inout and in source images.
 * Usually this function is called for direction with an X 
 * shift component in the right direction (e.g. for minimum this 
 * means that minimum values are shifted to the right).
 * \param p_inout pointer on the source/destination image pixel line
 * \param off_inout offset inside the source/destination image line
 * \param p_in pointer on the source image pixel line that is shifted
 * \param off_in offset inside the source image line
 * \param bytes_in number of bytes inside the line
 * \param edge_val the value representing the outside edge
 */
static INLINE void COMP_LINE_RIGHT(PLINE *p_inout, Uint32 off_inout,
                                   PLINE *p_in, Uint32 off_in,
                                   Uint32 bytes_in, binaryT edge_val )
{
    Uint32 i;
    binaryT pix_reg;

    binaryT *pin = (binaryT *) (*p_in + off_in);
    binaryT *pinout = (binaryT *) (*p_inout + off_inout);
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin++,pinout++) {
        pix_reg = (*pin);
        (*pinout) =  (*pinout)& (~((pix_reg<<1) | (edge_val>>SHIFT1BIT)));
        edge_val = pix_reg;
    }
}

/****************************************
 * Neighbor functions                   *
 ****************************************
 * The functions are described in a separate file to communalize with other
 * neighbor functions */
/** Data type of the value used to represent the edge */
#define EDGE_TYPE binaryT
#include "MB_Neighbor.c"
#undef EDGE_TYPE

/****************************************/
/* Main function                        */
/****************************************/

/**
 * Computes the set difference between two binary image pixels (a central pixel 
 * and its neighbor in the other image)
 * The neighbor depends on the grid used (see MB_ngh.h).
 *
 * \param src source image in which the neighbors are taken
 * \param srcdest source of the central pixel and destination image
 * \param nbrnum the neighbor index
 * \param grid the grid used (either square or hexagonal)
 * \param edge the kind of edge to use (behavior for pixel near edge depends on it)
 *
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_DiffNbb(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, enum MB_grid_t grid, enum MB_edgemode_t edge) {

    Uint32 linoff_in, linoff_inout;
    Uint32 bytes_in;
    PLINE *plines_in, *plines_inout;
    TSWITCHEP *fn;

    /* error management */
    /* verification over image size compatibility */
    if (!MB_CHECK_SIZE_2(src, srcdest)) {
        return ERR_BAD_SIZE;
    }
    /* grid value and possible neighbors are connected, grid value is the */
    /* maximum number of directions */
    if(nbrnum>6 && grid==MB_HEXAGONAL_GRID) {
        return ERR_BAD_DIRECTION;
    }
    if(nbrnum>8 && grid==MB_SQUARE_GRID) {
        return ERR_BAD_DIRECTION;
    }
    /* Only binary images can be processed */
    switch (MB_PROBE_PAIR(src, srcdest)) {
    case MB_PAIR_1_1:
        break;
    default:
        return ERR_BAD_DEPTH;
    }
    
    /* setting up pointers */
    plines_in = &src->PLINES[MB_Y_TOP(src)];
    plines_inout = &srcdest->PLINES[MB_Y_TOP(srcdest)];
    linoff_in  = MB_LINE_OFFSET(src);
    linoff_inout = MB_LINE_OFFSET(srcdest);
    bytes_in = MB_LINE_COUNT(src);

    /* Calling the corresponding function */
    fn = SwitchTo[grid][nbrnum];
    fn(plines_inout, linoff_inout, plines_in, linoff_in, bytes_in, src->height, 1, BIN_FILL_VALUE(edge));
    
    return NO_ERR;
}




