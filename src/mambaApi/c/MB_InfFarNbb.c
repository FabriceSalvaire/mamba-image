/**
 * \file MB_InfFarNbb.c
 * \author Nicolas Beucher
 * \date 24-6-2010
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
/* Base functions            */
/****************************************/
/* The functions described here realise the basic operations */
/* needed to shift pixel in any directions */

/**
 * Used to displace a complete line in an y direction.
 * \param p_out pointer on the destination image pixel line
 * \param off_out offset inside the destination image line
 * \param p_in pointer on the source image pixel line
 * \param off_in offset inside the source image line
 * \param bytes_in number of bytes inside the line
 */
static INLINE void SHIFT_LINE(PLINE *p_out, Uint32 off_out,
                              PLINE *p_in, Uint32 off_in,
                              Uint32 bytes_in )
{
    Uint32 i;

    binaryT *pin = (binaryT *) (*p_in + off_in);
    binaryT *pout = (binaryT *) (*p_out + off_out);
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin++,pout++) {
        (*pout) = (*pout)&(*pin);
    }
}

/**
 * Used to fill a complete line with a given value (used to fill voided lines following
 * a displacement in y).
 * \param p_out pointer on the destination image pixel line
 * \param off_out offset inside the destination image line
 * \param bytes_in number of bytes inside the line
 * \param fill_val the value used to fill the line
 */
static INLINE void SHIFT_EDGE_LINE(PLINE *p_out, Uint32 off_out, Uint32 bytes_in, binaryT fill_val )
{
    Uint32 i;

    binaryT *pout = (binaryT *) (*p_out + off_out);
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pout++) {
        (*pout) = (*pout)&(fill_val);
    }
}

/**
 * Used to displace a complete line in the right direction.
 * The shift is done to the left as the byte order is Little Endian.
 * \param p_out pointer on the destination image pixel line
 * \param off_out offset inside the destination image line
 * \param p_in pointer on the source image pixel line
 * \param off_in offset inside the source image line
 * \param bytes_in number of bytes inside the line
 * \param count the shift amplitude
 * \param fill_val the value used to fill the line
 */
static INLINE void SHIFT_LINE_RIGHT(PLINE *p_out, Uint32 off_out,
                                    PLINE *p_in, Uint32 off_in,
                                    Uint32 bytes_in,
                                    Sint32 count, binaryT fill_val)
{
    Uint32 i;
    Uint32 reg_dec;
    binaryT reg1, reg2, ins_reg_dec;
	binaryT *pin, *pout;

    reg_dec = count / (BYTEPERWORD*CHARBIT);
    ins_reg_dec = (binaryT) count % (BYTEPERWORD*CHARBIT);
    
    /* count cannot exceed the number of pixel in a line */
    reg_dec = reg_dec<(bytes_in/BYTEPERWORD) ? reg_dec : (bytes_in/BYTEPERWORD);

    pin = (binaryT *) (*p_in + off_in + bytes_in - (reg_dec+1)*BYTEPERWORD);
    pout = (binaryT *) (*p_out + off_out + bytes_in - BYTEPERWORD);
    
    if (ins_reg_dec==0) {
        /* no intra register shifting */
        for(i=0;i<(bytes_in-reg_dec*BYTEPERWORD);i+=BYTEPERWORD,pin--,pout--) {
            (*pout) &= (*pin);
        }
    } else {
        /* intra register shiffting */
        for(i=0;i<(bytes_in-reg_dec*BYTEPERWORD);i+=BYTEPERWORD,pin--,pout--) {
            reg1 = (*pin);
            reg2 = (i==(bytes_in-(reg_dec+1)*BYTEPERWORD)) ? fill_val : (*(pin-1));
            (*pout) &= (reg1<<ins_reg_dec) | (reg2>>(SHIFT1BIT+1-ins_reg_dec));
        }
    }
    
    /* The created space is filled with the fill value */
    for(i=0;i<reg_dec;i++,pout--) {
        (*pout) &= fill_val;
    }
}

/**
 * Used to displace a complete line in the left direction.
 * The shift is done to the right as the byte order is Little Endian.
 * \param p_out pointer on the destination image pixel line
 * \param off_out offset inside the destination image line
 * \param p_in pointer on the source image pixel line
 * \param off_in offset inside the source image line
 * \param bytes_in number of bytes inside the line
 * \param count the shift amplitude
 * \param fill_val the value used to fill the line
 */
static INLINE void SHIFT_LINE_LEFT(PLINE *p_out, Uint32 off_out,
                                   PLINE *p_in, Uint32 off_in,
                                   Uint32 bytes_in,
                                   Sint32 count, binaryT fill_val)
{
    Uint32 i;
    Uint32 reg_dec;
    binaryT reg1, reg2, ins_reg_dec;
	binaryT *pin, *pout;

    reg_dec = count / (BYTEPERWORD*CHARBIT);
    ins_reg_dec = (binaryT) count % (BYTEPERWORD*CHARBIT);
    
    /* count cannot exceed the number of pixel in a line */
    reg_dec = reg_dec<(bytes_in/BYTEPERWORD) ? reg_dec : (bytes_in/BYTEPERWORD);

    pin = (binaryT *) (*p_in + off_in + reg_dec*BYTEPERWORD);
    pout = (binaryT *) (*p_out + off_out);
    
    if (ins_reg_dec==0) {
        /* no intra register shifting */
        for(i=0;i<(bytes_in-reg_dec*BYTEPERWORD);i+=BYTEPERWORD,pin++,pout++) {
            (*pout) &= (*pin);
        }
    } else {
        /* intra register shiffting */
        for(i=0;i<(bytes_in-reg_dec*BYTEPERWORD);i+=BYTEPERWORD,pin++,pout++) {
            reg1 = (*pin);
            reg2 = (i==(bytes_in-(reg_dec+1)*BYTEPERWORD)) ? fill_val : (*(pin+1));
            (*pout) &= (reg1>>ins_reg_dec) | (reg2<<(SHIFT1BIT+1-ins_reg_dec));
        }
    }
    
    /* The created space is filled with the fill value */
    for(i=0;i<reg_dec;i++,pout++) {
        (*pout) &= fill_val;
    }
}

/****************************************/
/* Direction functions                  */
/****************************************/
/* The functions are described in a separate file to communalize with other */
/* shift functions */
/** Data type of the value used to represent the edge */
#define EDGE_TYPE binaryT
#include "MB_ShftDirection.c"
#undef EDGE_TYPE

/****************************************/
/* Main function                        */
/****************************************/

/**
 * Looks for the minimum between two binary image pixels (a central pixel and its 
 * far neighbor in the other image)
 * The neighbor depends on the grid used (see MB_ngh.h).
 *
 * \param src source image in which the neighbor are taken
 * \param srcdest source of the central pixel and destination image
 * \param nbrnum the neighbor index
 * \param count the amplitude of the shift (in pixels)
 * \param grid the grid used (either square or hexagonal)
 * \param edge the kind of edge to use (behavior for pixel near edge depends on it)
 *
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_InfFarNbb(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, Uint32 count, enum MB_grid_t grid, enum MB_edgemode_t edge)
{
    Uint32 bytes_in;
    Uint32 linoff_in, linoff_out;
    PLINE *plines_in, *plines_out;
    TSWITCHEP *fn;
    Uint32 neighbors_nb, tran_dir;

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
    /* Only binary and greyscale images can be processed */
    switch (MB_PROBE_PAIR(src, srcdest)) {
    case MB_PAIR_1_1:
        break;
    default:
        return ERR_BAD_DEPTH;
    }
    
    /* if count is to zero it amounts to a simple copy of src into dest */
    /* otherwise its a shift */
    if (count==0) {
        return MB_Inf(src, srcdest, srcdest);
    }
    
    /* As the functions used are direction functions we need to transpose the */
    /* neighbor value into the direction of the shift to perfom so that the */
    /* central pixel and the far neighbor pixel face each other (the neighbor */
    /* image is the one that is shifted) */
    neighbors_nb = grid==MB_HEXAGONAL_GRID ? 6 : 8;
    tran_dir = nbrnum==0 ? 0 : (nbrnum+neighbors_nb/2-1)%neighbors_nb + 1;

    /* setting up pointers */
    plines_in = &src->PLINES[MB_Y_TOP(src)];
    plines_out = &srcdest->PLINES[MB_Y_TOP(srcdest)];
    linoff_in  = MB_LINE_OFFSET(src);
    linoff_out = MB_LINE_OFFSET(srcdest);
    bytes_in = MB_LINE_COUNT(src);

    /* Calling the corresponding function */
    fn = SwitchTo[grid][tran_dir];
    fn(plines_out, linoff_out, plines_in, linoff_in, bytes_in, (Sint32) src->height, count, BIN_FILL_VALUE(edge));

    return NO_ERR;
}
