/**
 * \file MB_SupFarNb8.c
 * \author Nicolas Beucher
 * \date 25-6-2010
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
    
#ifdef __SSE2__

    __m128i *pin = (__m128i*) (*p_in + off_in);
    __m128i *pinout = (__m128i*) (*p_out + off_out);
    
    for(i=0;i<bytes_in;i+=16,pin++,pinout++) {
        (*pinout) = _mm_max_epu8((*pinout),(*pin));
    }
    
#else

    PLINE pin = (PLINE) (*p_in + off_in);
    PLINE pinout = (PLINE) (*p_out + off_out);
    
    for(i=0;i<bytes_in;i++,pin++,pinout++) {
        (*pinout) = (*pinout)>(*pin) ? (*pinout) : (*pin);
    }
#endif
}

/**
 * Used to fill a complete line with a given value (used to fill voided line following
 * a displacement in y).
 * \param p_out pointer on the destination image pixel line
 * \param off_out offset inside the destination image line
 * \param bytes_in number of bytes inside the line
 * \param fill_val the value used to fill the line
 */
static INLINE void SHIFT_EDGE_LINE(PLINE *p_out, Uint32 off_out, Uint32 bytes_in, Uint32 fill_val )
{
    Uint32 i;

#ifdef __SSE2__
    
    __m128i edge = _mm_set1_epi32((int) fill_val);
    __m128i *pinout = (__m128i*) (*p_out + off_out);
    
    for(i=0;i<bytes_in;i+=16,pinout++) {
        (*pinout) = _mm_max_epu8((*pinout),edge);
    }
    
#else

    PLINE pinout = (PLINE) (*p_out + off_out);
    
    for(i=0;i<bytes_in;i++,pinout++) {
        (*pinout) = (*pinout)>(fill_val) ? (*pinout) : (fill_val);
    }
#endif
}

/**
 * Used to displace a complete line in the left direction.
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
                                   Sint32 count, Uint32 fill_val)
{
    Uint32 i;

#ifdef __SSE2__

    Uint32 reg_dec, ins_reg_dec;
    __m128i reg1, reg2;
	__m128i edge, *pin, *pout;

    /* count cannot exceed the number of pixel in a line */
    reg_dec = ((Uint32) count)<bytes_in ? count/16 : bytes_in/16;
    ins_reg_dec = count % 16;

    edge = _mm_set1_epi32((int) fill_val);
    pin = (__m128i *) (*p_in + off_in + reg_dec*16);
    pout = (__m128i *) (*p_out + off_out);
    
    if (ins_reg_dec==0) {
        /* no intra register shifting */
        for(i=0;i<(bytes_in-reg_dec*16);i+=16,pin++,pout++) {
            (*pout) = _mm_max_epu8((*pout),(*pin));
        }
    } else {
        /* intra register shifting */
        for(i=0;i<(bytes_in-reg_dec*16);i+=16,pin++,pout++) {
            reg1 = (*pin);
            reg2 = (i==(bytes_in-(reg_dec+1)*16)) ? edge : (*(pin+1));
            switch(ins_reg_dec) {
                case 1:
                    reg1 = _mm_srli_si128(reg1, 1);
                    reg2 = _mm_slli_si128 (reg2, 15);
                    break;
                case 2:
                    reg1 = _mm_srli_si128(reg1, 2);
                    reg2 = _mm_slli_si128 (reg2, 14);
                    break;
                case 3:
                    reg1 = _mm_srli_si128(reg1, 3);
                    reg2 = _mm_slli_si128 (reg2, 13);
                    break;
                case 4:
                    reg1 = _mm_srli_si128(reg1, 4);
                    reg2 = _mm_slli_si128 (reg2, 12);
                    break;
                case 5:
                    reg1 = _mm_srli_si128(reg1, 5);
                    reg2 = _mm_slli_si128 (reg2, 11);
                    break;
                case 6:
                    reg1 = _mm_srli_si128(reg1, 6);
                    reg2 = _mm_slli_si128 (reg2, 10);
                    break;
                case 7:
                    reg1 = _mm_srli_si128(reg1, 7);
                    reg2 = _mm_slli_si128 (reg2, 9);
                    break;
                case 8:
                    reg1 = _mm_srli_si128(reg1, 8);
                    reg2 = _mm_slli_si128 (reg2, 8);
                    break;
                case 9:
                    reg1 = _mm_srli_si128(reg1, 9);
                    reg2 = _mm_slli_si128 (reg2, 7);
                    break;
                case 10:
                    reg1 = _mm_srli_si128(reg1, 10);
                    reg2 = _mm_slli_si128 (reg2, 6);
                    break;
                case 11:
                    reg1 = _mm_srli_si128(reg1, 11);
                    reg2 = _mm_slli_si128 (reg2, 5);
                    break;
                case 12:
                    reg1 = _mm_srli_si128(reg1, 12);
                    reg2 = _mm_slli_si128 (reg2, 4);
                    break;
                case 13:
                    reg1 = _mm_srli_si128(reg1, 13);
                    reg2 = _mm_slli_si128 (reg2, 3);
                    break;
                case 14:
                    reg1 = _mm_srli_si128(reg1, 14);
                    reg2 = _mm_slli_si128 (reg2, 2);
                    break;
                case 15:
                    reg1 = _mm_srli_si128(reg1, 15);
                    reg2 = _mm_slli_si128 (reg2, 1);
                    break;
                default:
                case 0:
                    break;
            }
/*            reg1 = _mm_srli_si128_s (reg1, ins_reg_dec);  >> */
/*            reg2 = _mm_slli_si128_s (reg2, 16-ins_reg_dec);  << */
            reg1 = _mm_or_si128 (reg1, reg2); /* | */
            (*pout) = _mm_max_epu8((*pout),reg1);
        }
    }
    
    /* The created space is filled with the fill value */
    for(i=0;i<reg_dec;i++,pout++) {
        (*pout) = _mm_max_epu8((*pout),edge);
    }
    
#else
	PLINE pin, pout;

    /* count cannot exceed the number of pixel in a line */
    count = ((Uint32) count)<bytes_in ? count : bytes_in;
    
    pin = (PLINE) (*p_in + off_in + count);
    pout = (PLINE) (*p_out + off_out);
    
    for(i=0; i<(bytes_in-((Uint32) count)); i++,pout++,pin++) {
        (*pout) = (*pout)>(*pin) ? (*pout) : (*pin);
    }
    for(i=0; i<((Uint32) count); i++,pout++) {
        (*pout) = (*pout)>(fill_val) ? (*pout) : (fill_val);
    }

#endif
}

/**
 * Used to displace a complete line in the right direction.
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
                                    Sint32 count, Uint32 fill_val)
{
    Uint32 i;

#ifdef __SSE2__

    Uint32 reg_dec, ins_reg_dec;
    __m128i reg1, reg2;
	__m128i edge, *pin, *pout;

    /* count cannot exceed the number of pixel in a line */
    reg_dec = ((Uint32) count)<bytes_in ? count/16 : bytes_in/16;
    ins_reg_dec = count % 16;

    edge = _mm_set1_epi32((int) fill_val);
    pin = (__m128i *) (*p_in + off_in + bytes_in - (reg_dec+1)*16);
    pout = (__m128i *) (*p_out + off_out + bytes_in - 16);
    
    if (ins_reg_dec==0) {
        /* no intra register shifting */
        for(i=0;i<(bytes_in-reg_dec*16);i+=16,pin--,pout--) {
            (*pout) = _mm_max_epu8((*pout),(*pin));
        }
    } else {
        /* intra register shifting */
        for(i=0;i<(bytes_in-reg_dec*16);i+=16,pin--,pout--) {
            reg1 = (*pin);
            reg2 = (i==(bytes_in-(reg_dec+1)*16)) ? edge : (*(pin-1));
            switch(ins_reg_dec) {
                case 1:
                    reg1 = _mm_slli_si128(reg1, 1);
                    reg2 = _mm_srli_si128 (reg2, 15);
                    break;
                case 2:
                    reg1 = _mm_slli_si128(reg1, 2);
                    reg2 = _mm_srli_si128 (reg2, 14);
                    break;
                case 3:
                    reg1 = _mm_slli_si128(reg1, 3);
                    reg2 = _mm_srli_si128 (reg2, 13);
                    break;
                case 4:
                    reg1 = _mm_slli_si128(reg1, 4);
                    reg2 = _mm_srli_si128 (reg2, 12);
                    break;
                case 5:
                    reg1 = _mm_slli_si128(reg1, 5);
                    reg2 = _mm_srli_si128 (reg2, 11);
                    break;
                case 6:
                    reg1 = _mm_slli_si128(reg1, 6);
                    reg2 = _mm_srli_si128 (reg2, 10);
                    break;
                case 7:
                    reg1 = _mm_slli_si128(reg1, 7);
                    reg2 = _mm_srli_si128 (reg2, 9);
                    break;
                case 8:
                    reg1 = _mm_slli_si128(reg1, 8);
                    reg2 = _mm_srli_si128 (reg2, 8);
                    break;
                case 9:
                    reg1 = _mm_slli_si128(reg1, 9);
                    reg2 = _mm_srli_si128 (reg2, 7);
                    break;
                case 10:
                    reg1 = _mm_slli_si128(reg1, 10);
                    reg2 = _mm_srli_si128 (reg2, 6);
                    break;
                case 11:
                    reg1 = _mm_slli_si128(reg1, 11);
                    reg2 = _mm_srli_si128 (reg2, 5);
                    break;
                case 12:
                    reg1 = _mm_slli_si128(reg1, 12);
                    reg2 = _mm_srli_si128 (reg2, 4);
                    break;
                case 13:
                    reg1 = _mm_slli_si128(reg1, 13);
                    reg2 = _mm_srli_si128 (reg2, 3);
                    break;
                case 14:
                    reg1 = _mm_slli_si128(reg1, 14);
                    reg2 = _mm_srli_si128 (reg2, 2);
                    break;
                case 15:
                    reg1 = _mm_slli_si128(reg1, 15);
                    reg2 = _mm_srli_si128 (reg2, 1);
                    break;
                default:
                case 0:
                    break;
            }
/*            reg1 = _mm_slli_si128_s (reg1, ins_reg_dec);  << */
/*            reg2 = _mm_srli_si128_s (reg2, 16-ins_reg_dec);  >> */
            reg1 = _mm_or_si128 (reg1, reg2); /* | */
            (*pout) = _mm_max_epu8((*pout),reg1);
        }
    }
    
    /* The created space is filled with the fill value */
    for(i=0;i<reg_dec;i++,pout--) {
        (*pout) = _mm_max_epu8((*pout),edge);
    }

    
#else
	PLINE pin, pout;
    
    /* count cannot exceed the number of pixel in a line */
    count = ((Uint32) count)<bytes_in ? count : bytes_in;
    
    pin = (PLINE) (*p_in + bytes_in -1 + off_in - count);
    pout = (PLINE) (*p_out + bytes_in -1 + off_out);
    
    for(i=0;i<bytes_in-((Uint32) count);i++,pin--,pout--) {
        (*pout) = (*pout)>(*pin) ? (*pout) : (*pin);
    }
    for(i=0; i<((Uint32) count); i++,pout--) {
        (*pout) = (*pout)>(fill_val) ? (*pout) : (fill_val);
    }
#endif
}

/****************************************/
/* Direction functions                  */
/****************************************/
/* The functions are described in a separate file to communalize with other */
/* shift functions */
/** Data type of the value used to represent the edge */
#define EDGE_TYPE Uint32
#include "MB_ShftDirection.c"
#undef EDGE_TYPE

/****************************************/
/* Main function                        */
/****************************************/

/**
 * Looks for the maximum between two grey scale image pixels (a central pixel and its 
 * far neighbor in the other image)
 * The neighbor depends on the grid used (see MB_ngh.h).
 *
 * \param src source image in which the neighbor are taken
 * \param srcdest source of the central pixel and destination image
 * \param nbrnum the neighbor index
 * \param count the amplitude of the shift (in pixels)
 * \param grid the grid used (either square or hexagonal)
 * \param edge the kind of edge to use (behavior for pixels near edge depends on it)
 *
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_SupFarNb8(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, Uint32 count, enum MB_grid_t grid, enum MB_edgemode_t edge)
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
    case MB_PAIR_8_8:
        break;
    default:
        return ERR_BAD_DEPTH;
    }
    
    /* if count is to zero it amounts to a simple copy of src into dest */
    /* otherwise its a shift */
    if (count==0) {
        return MB_Sup(src, srcdest, srcdest);
    }
    
    /* As the function used are direction function we need to transpose the */
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
    fn(plines_out, linoff_out, plines_in, linoff_in, bytes_in, (Sint32) src->height, count, GREY_FILL_VALUE(edge));

    return NO_ERR;
}
