/**
 * \file MB_Distanceb.c
 * \author Nicolas Beucher
 * \date 12-27-2008
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

/****************************************/
/* Definitions                          */
/****************************************/
/* definitions created here are meant to simplify readability */

/** pixel value defines */
#define IS_SET(pix) ((pix)!=0)

/* neighbor pixel reading and accessing */
/* macros work with the pointer to the pixel */
/** Macro returning the value of a pixel */
#define VAL(p_pix) (*p_pix)
/** Macro returning the value of the left neighbor pixel */
#define LEFT(p_pix) (*(p_pix-1))
/** Macro returning the value of the right neighbor pixel */
#define RIGHT(p_pix) (*(p_pix+1))

/** When a filled edge is selected, we must ensure that pixels touching the 
 * edge will be set to an 'infinite' distance, i.e. greater than every possible
 * distance. As the image size is limited to 4100x4100, we select a greater 
 * value than this to emulate the edge infinite distance 
 *
 * <- 65536 should be ok even if the image size is extended */
#define EDGE_DIST 0x00010000

/****************************************/
/* Base functions                       */
/****************************************/
/* The functions described here realise the basic operations */
/* needed to label pixels */

/*************************Minima functions*************************************/

/* minimum value over 2 values */
static INLINE PIX32 FIND_MIN2(PIX32 v1, PIX32 v2)
{
    return (v1<v2) ? v1 : v2;
}

/* minimum value over 3 values */
static INLINE PIX32 FIND_MIN3(PIX32 v1, PIX32 v2, PIX32 v3)
{
    return FIND_MIN2(v3, FIND_MIN2(v1, v2));
}

/* minimum value over 4 values */
static INLINE PIX32 FIND_MIN4(PIX32 v1, PIX32 v2, PIX32 v3, PIX32 v4)
{
    return FIND_MIN2(FIND_MIN2(v3, v4), FIND_MIN2(v1, v2));
}

/*************************Border Line functions********************************/

/**
 * Distance for lower line
 * 
 * This function is called by the second pass. Thus there is already a distance
 * computed into out image. This is the distance to the nearest top left edge
 * of the set (for pixels that are true in the input image).
 *
 * The fonction handles pixels in the bottom line of the image (adjacent to
 * image edge).
 */
static INLINE void DOWNEDGE_LINE(PLINE *plines_out, Uint32 linoff_out,
                                   PLINE *plines_in, Uint32 linoff_in,
                                   Uint32 bytes_in, Uint32 bytes_out,
                                   binaryT edge_val)
{
    Uint32 i;
    Sint32 j;
    binaryT pix_register, pix0, pix2;
    PIX32 prov;
    
    binaryT *pin = (binaryT *) (*plines_in+linoff_in+bytes_in-BYTEPERWORD);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out+bytes_out-4);
    
    /* previous value initialisation */
    pix2 = edge_val&1;
    RIGHT(pout) = (PIX32) edge_val&EDGE_DIST;
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin--) {
        /* reading the input line register by register */
        pix_register = (*pin);
        for(j=SHIFT1BIT; j>-1; j--,pout--) {
            /* for each pixel in the binary register */
            /* we will analyze its value and determines */
            /* its distance to the set edge */
            pix0 = (pix_register>>j)&1;
            if (pix0) {
                if (pix2 && (edge_val&1)) {
                    /* the pixel is set and its neighbor too */
                    /* as the output image is already filled */
                    /* we have to compute if the pixel is nearer */
                    /* the upper left edge or the lower right */
                    /* one.*/
                    prov = FIND_MIN2(RIGHT(pout), EDGE_DIST) + 1;
                    VAL(pout) = FIND_MIN2(VAL(pout), prov);
                } else {
                    VAL(pout) = 1;
                }
            } else {
                VAL(pout) = 0;
            }
            pix2 = pix0;
        }
    }
}

/**
 * Distance for upper line
 * 
 * This function is called by the first pass. The output image is thus empty.
 *
 * The fonction handles pixels in the top line of the image (adjacent to
 * image edge).
 */
static INLINE void UPEDGE_LINE(PLINE *plines_out, Uint32 linoff_out,
                                 PLINE *plines_in, Uint32 linoff_in,
                                 Uint32 bytes_in,
                                 binaryT edge_val)
{
    Uint32 i,j;
    binaryT pix_register, pix5;
    
    binaryT *pin = (binaryT *) (*plines_in+linoff_in);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out);
    
    /* previous value initialisation */
    pix5 = edge_val;
    LEFT(pout) = (PIX32) edge_val&EDGE_DIST;
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin++) {
        /* reading the input line register by register */
        pix_register = (*pin);
        for(j=0; j<CHARBIT*BYTEPERWORD; j++,pout++) {
            /* for each pixel in the binary register */
            /* we will analyze its value and determines */
            /* its distance to the set edge given the */
            /* distance of its neighbors */
            if (pix_register&1) {
                if ((pix5&1) && (edge_val&1)) {
                    /* All its neighbors are set */
                    VAL(pout) = FIND_MIN2(LEFT(pout),EDGE_DIST)+1;
                } else {
                    /* the pixel is in the edge */
                    /* one of its neighbor is empty */
                    VAL(pout) = 1;
                }
            } else {
                VAL(pout) = 0;
            }
            pix5 = pix_register;
            /* next pixel */
            pix_register = pix_register>>1;
        }
    }
}


/*************************Hexagonal functions**********************************/

/**
 * labeling the odd lines for hexagonal grid 
 * 
 * This function is called by the second pass. Thus there is already a distance
 * computed into out image. This is the distance to the nearest top left edge
 * of the set (for pixels that are true in the input image).
 * 
 * the "pre" line pointers link to the previously computed lines. As we are
 * moving from down right to up left the previous line are the line below the
 * line being computed.
 */
static INLINE void DR2UL_HDIS_LINE_ODD(PLINE *plines_out, PLINE *plines_outpre,
                                       Uint32 linoff_out,
                                       PLINE *plines_in, PLINE *plines_inpre,
                                       Uint32 linoff_in,
                                       Uint32 bytes_in, Uint32 bytes_out,
                                       binaryT edge_val)
{
    Uint32 i;
    Sint32 j;
    /* pixels are numbered by the neighbor they are representing in the */
    /* hexagonal grid. pix0 being the central pixel. See grid definition */
    /* for more detail */
    binaryT pix0, pix2, pix3, pix4;
    
    binaryT current_pixel_register;
    binaryT preline_pixel_register;
    PIX32 prov;

    /* lines init */
    binaryT *pin = (binaryT *) (*plines_in+linoff_in+bytes_in-BYTEPERWORD);
    binaryT *pinpre = (binaryT *) (*plines_inpre+linoff_in+bytes_in-BYTEPERWORD);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out+bytes_out-4);
    PIX32 *poutpre = (PIX32 *) (*plines_outpre+linoff_out+bytes_out-4);
    
    /* previous value initialisation */
    pix2 = pix3 = edge_val&1;
    RIGHT(poutpre) = (PIX32) edge_val&EDGE_DIST;
    RIGHT(pout) = (PIX32) edge_val&EDGE_DIST;
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin--,pinpre--) {
        /* reading the input lines register by register */
        current_pixel_register = (*pin);
        preline_pixel_register = (*pinpre);
        for(j=SHIFT1BIT; j>-1; j--,pout--,poutpre--) {
            /* for each pixel in the binary register */
            /* we will analyze its value and determines */
            /* its distance to the set edge given the */
            /* distance of its neighbors */
            pix0 = (current_pixel_register>>j)&1;
            pix4 = (preline_pixel_register>>j)&1;
            if (pix0) {
                if (pix2 & pix3& pix4) {
                    prov = FIND_MIN3(RIGHT(poutpre), VAL(poutpre), RIGHT(pout))+1;
                    VAL(pout) = FIND_MIN2(VAL(pout), prov);
                } else {
                    VAL(pout) = 1;
                }
            } else {
                VAL(pout) = 0;
            }
            /* previous pixel storing */
            pix2 = pix0;
            pix3 = pix4;
        }
    }
}

/**
 * labeling the odd lines for hexagonal grid 
 * 
 * This function is called by the first pass.
 * 
 * the "pre" line pointers link to the previously computed lines. As we are
 * moving from up left to down right the previous line are the line above the
 * line being computed.
 */
static INLINE void UL2DR_HDIS_LINE_ODD(PLINE *plines_out, PLINE *plines_outpre,
                                       Uint32 linoff_out,
                                       PLINE *plines_in, PLINE *plines_inpre,
                                       Uint32 linoff_in,
                                       Uint32 bytes_in,
                                       binaryT edge_val)
{
    Uint32 i,j;
    /* pixels are numbered by the neighbor they are representing in the */
    /* hexagonal grid. pix0 being the central pixel. See grid definition */
    /* for more detail */
    binaryT pix0, pix61, pix5;
    
    binaryT current_pixel_register;
    binaryT preline_pixel_register;

    /* lines init */
    binaryT *pin = (binaryT *) (*plines_in+linoff_in);
    binaryT *pinpre = (binaryT *) (*plines_inpre+linoff_in);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out);
    PIX32 *poutpre = (PIX32 *) (*plines_outpre+linoff_out);
    
    /* previous value initialisation */
    pix5 = edge_val&1;
    LEFT(pout) = (PIX32) edge_val&EDGE_DIST;
    preline_pixel_register = (*pinpre);
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin++) {
        /* reading the input lines register by register */
        current_pixel_register = (*pin);
        for(j=0; j<SHIFT1BIT; j++,pout++,poutpre++) {
            /* for each pixel in the binary register */
            /* ! except the last one ! */
            /* we will analyze its value and determines */
            /* its distance to the set edge given the */
            /* distance of its neighbors */
            pix0 = (current_pixel_register)&1;
            pix61 = (preline_pixel_register)&3;
            if (pix0) {
                if (pix5==1 && pix61==3) {
                    VAL(pout) = FIND_MIN3(VAL(poutpre), RIGHT(poutpre), LEFT(pout))+1;
                } else {
                    VAL(pout) = 1;
                }
            } else {
                VAL(pout) = 0;
            }
            pix5 = pix0;
            /* next pixel */
            current_pixel_register = current_pixel_register>>1;
            preline_pixel_register = preline_pixel_register>>1;
        }
        /* the last pixel must be processed separately as one of its neighbor */
        /* is not in the preline_pixel_register but in the next one */
        pinpre++; /* <- to access the next register */
        pix0 = (current_pixel_register)&1;
        pix61 = (preline_pixel_register&1); /*<- pix61 is used to store the last pixel */
                                            /* of the former preline register */
        
        if (i<(bytes_in-BYTEPERWORD)) {
            /* If the end of the line is not reached we acces the nex register */
            /* of the previous line */
            preline_pixel_register = *pinpre;
        } else {
            /* in the other case the register is set to the edge value */
            preline_pixel_register = edge_val;
            RIGHT(poutpre) = (PIX32) edge_val&EDGE_DIST;
        }
        
        pix61 |= ((preline_pixel_register&1)<<1);
        if (pix0) {
            if (pix5==1 && pix61==3) {
                VAL(pout) = FIND_MIN3(VAL(poutpre), RIGHT(poutpre), LEFT(pout))+1;
            } else {
                VAL(pout) = 1;
            }
        } else {
            VAL(pout) = 0;
        }
        
        /* previous pixel storing */
        pix5 = pix0;
        /* next pixel */
        pout++;
        poutpre++;
    }
}

/**
 * labeling the even lines for hexagonal grid
 * 
 * This function is called by the second pass. Thus there is already a distance
 * computed into out image. This is the distance to the nearest top left edge
 * of the set (for pixels that are true in the input image).
 * 
 * the "pre" line pointers link to the previously computed lines. As we are
 * moving from down right to up left the previous line are the line below the
 * line being computed.
 */
static INLINE void DR2UL_HDIS_LINE_EVEN(PLINE *plines_out, PLINE *plines_outpre,
                                        Uint32 linoff_out,
                                        PLINE *plines_in, PLINE *plines_inpre,
                                        Uint32 linoff_in,
                                        Uint32 bytes_in, Uint32 bytes_out,
                                        binaryT edge_val)
{
    Uint32 i;
    Sint32 j;
    /* pixels are numbered by the neighbor they are representing in the */
    /* hexagonal grid. pix0 being the central pixel. See grid definition */
    /* for more detail */
    binaryT pix43,pix0,pix2;
    
    binaryT current_pixel_register;
    binaryT preline_pixel_register;
    PIX32 prov;
    
    /* lines init */
    binaryT *pin = (binaryT *) (*plines_in+linoff_in+bytes_in-BYTEPERWORD);
    binaryT *pinpre = (binaryT *) (*plines_inpre+linoff_in+bytes_in-BYTEPERWORD);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out+bytes_out-4);
    PIX32 *poutpre = (PIX32 *) (*plines_outpre+linoff_out+bytes_out-4);
    
    /* previous value initialisation */
    RIGHT(pout) = (PIX32) edge_val&EDGE_DIST;
    pix2 = edge_val&1;
    preline_pixel_register = (*pinpre);
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin--) {
        /* reading the input lines register by register */
        current_pixel_register = (*pin);
        for(j=SHIFT1BIT; j>0; j--,pout--,poutpre--) {
            /* for each pixel in the binary register */
            /* ! except the last one ! */
            /* we will analyze its value and determines */
            /* its distance to the set edge given the */
            /* distance of its neighbors */
            pix0 = (current_pixel_register>>j)&1;
            pix43 = (preline_pixel_register>>(j-1))&3;
            if (pix0) {
                if (pix2==1 && pix43==3) {
                    prov = FIND_MIN3(LEFT(poutpre), VAL(poutpre), RIGHT(pout))+1;
                    VAL(pout) = FIND_MIN2(VAL(pout), prov);
                } else {
                    VAL(pout) = 1;
                }
            } else {
                VAL(pout) = 0;
            }
            pix2 = pix0;
        }
        /* the last pixel must be processed separately as one of its neighbor */
        /* is not in the preline_pixel_register but in the next one */
        pinpre--;
        pix0 = (current_pixel_register)&1;
        pix43 = (preline_pixel_register&1)<<1;
        
        if (i<(bytes_in-BYTEPERWORD)) {
            /* If the end of the line is not reached we acces the nex register */
            /* of the previous line */
            preline_pixel_register = *pinpre;
        } else {
            /* in the other case the register is set to the edge value */
            preline_pixel_register = edge_val;
            LEFT(poutpre) = (PIX32) edge_val&EDGE_DIST;
        }
        
        pix43 |= ((preline_pixel_register>>SHIFT1BIT)&1) ;
        if (pix0) {
            if (pix2==1 && pix43==3) {
                prov = FIND_MIN3(LEFT(poutpre), VAL(poutpre), RIGHT(pout))+1;
                VAL(pout) = FIND_MIN2(VAL(pout), prov);
            } else {
                VAL(pout) = 1;
            }
        } else {
            VAL(pout) = 0;
        }
        /* previous pixel storing */
        pix2 = pix0;
        /* next pixel */
        pout--;
        poutpre--;
    }
}

/**
 * labeling the even lines for hexagonal grid 
 * 
 * This function is called by the first pass.
 * 
 * the "pre" line pointers link to the previously computed lines. As we are
 * moving from up left to down right the previous line are the line above the
 * line being computed.
 */
static INLINE void UL2DR_HDIS_LINE_EVEN(PLINE *plines_out, PLINE *plines_outpre,
                                        Uint32 linoff_out,
                                        PLINE *plines_in, PLINE *plines_inpre,
                                        Uint32 linoff_in,
                                        Uint32 bytes_in,
                                        binaryT edge_val)
{
    Uint32 i,j;
    /* pixels are numbered by the neighbor they are representing in the */
    /* hexagonal grid. pix0 being the central pixel. See grid definition */
    /* for more detail */
    binaryT pix6,pix1,pix0,pix5;
    
    binaryT current_pixel_register;
    binaryT preline_pixel_register;
    
    /* lines init */
    binaryT *pin = (binaryT *) (*plines_in+linoff_in);
    binaryT *pinpre = (binaryT *) (*plines_inpre+linoff_in);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out);
    PIX32 *poutpre = (PIX32 *) (*plines_outpre+linoff_out);
    
    /* previous value initialisation */
    LEFT(pout) = (PIX32) edge_val&EDGE_DIST;
    LEFT(poutpre) = (PIX32) edge_val&EDGE_DIST;
    pix6 = pix5 = edge_val&1;
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin++,pinpre++) {
        /* reading the input lines register by register */
        current_pixel_register = (*pin);
        preline_pixel_register = (*pinpre);
        for(j=0; j<CHARBIT*BYTEPERWORD; j++,pout++,poutpre++) {
            /* for each pixel in the binary register */
            /* we will analyze its value and determines */
            /* its distance to the set edge given the */
            /* distance of its neighbors */
            pix0 = (current_pixel_register)&1;
            pix1 = (preline_pixel_register)&1;
            if (pix0) {
                if (pix1 & pix5 & pix6) {
                    VAL(pout) = FIND_MIN3(LEFT(poutpre), VAL(poutpre), LEFT(pout))+1;
                } else {
                    VAL(pout) = 1;
                }
            } else {
                VAL(pout) = 0;
            }
            /* previous pixel storing */
            pix5 = pix0;
            pix6 = pix1;
            /* next pixel */
            current_pixel_register = current_pixel_register>>1;
            preline_pixel_register = preline_pixel_register>>1;
        }
    }
}

/*************************Square functions*************************************/

/**
 * labeling the lines for square grid when going from up left to down right
 * 
 * This function is called by the first pass.
 * 
 * the "pre" line pointers link to the previously computed lines. As we are
 * moving from up left to down right the previous line are the line above the
 * line being computed.
 */
static INLINE void UL2DR_QDIS_LINE(PLINE *plines_out, PLINE *plines_outpre,
                                   Uint32 linoff_out,
                                   PLINE *plines_in, PLINE *plines_inpre,
                                   Uint32 linoff_in,
                                   Uint32 bytes_in,
                                   binaryT edge_val)
{
    Uint32 i;
    Sint32 j;
    /* pixels are numbered by the neighbor they are representing in the */
    /* hexagonal grid. pix0 being the central pixel. See grid definition */
    /* for more detail */
    binaryT pix0,pix1,pix2,pix7,pix8;
    
    binaryT current_pixel_register;
    binaryT preline_pixel_register;
    
    /* lines init */
    binaryT *pin = (binaryT *) (*plines_in+linoff_in);
    binaryT *pinpre = (binaryT *) (*plines_inpre+linoff_in);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out);
    PIX32 *poutpre = (PIX32 *) (*plines_outpre+linoff_out);
    
    /* previous value initialisation */
    /*The first value are set to max according to the edge type*/
    LEFT(pout) = (PIX32) edge_val&EDGE_DIST;
    LEFT(poutpre) = (PIX32) edge_val&EDGE_DIST;
    pix7 = pix8 = edge_val&1;
    preline_pixel_register = (*pinpre);
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin++) {
        /* reading the input lines register by register */
        current_pixel_register = (*pin);
        for(j=SHIFT1BIT; j>0; j--,pout++,poutpre++) {
            /* for each pixel in the binary register */
            /* ! except the last one ! */
            /* we will analyze its value and determines */
            /* its distance to the set edge given the */
            /* distance of its neighbors */
            pix0 = (current_pixel_register)&1;
            pix1 = (preline_pixel_register)&1;
            pix2 = (preline_pixel_register>>1)&1;
            if (pix0) {
                /* the pixel is set to 1 */
                if (pix1 & pix2 & pix7 & pix8) {
                    /* if all the neighbor are set to 1, it means that 
                     * the pixel in p2 must be set to the minimal distance of its
                     * neighbor plus 1 */
                    VAL(pout) = FIND_MIN4(LEFT(poutpre), VAL(poutpre), RIGHT(poutpre), LEFT(pout))+1;
                } else {
                    /* Otherwise it is in the edge ! so 1 */
                    VAL(pout) = 1;
                }
            } else {
                VAL(pout) = 0;
            }
            /* previous pixel storing */
            pix8 = pix1;
            pix7 = pix0;
            /* next pixel */
            current_pixel_register = current_pixel_register>>1;
            preline_pixel_register = preline_pixel_register>>1;
        }
        /* the last pixel must be processed separately as one of its neighbor */
        /* is not in the preline_pixel_register but in the next one */
        pinpre++;
        pix0 = (current_pixel_register)&1;
        pix1 = (preline_pixel_register)&1;
        
        if (i<(bytes_in-BYTEPERWORD)) {
            /* If the end of the line is not reached we acces the nex register */
            /* of the previous line */
            preline_pixel_register = (*pinpre);
        } else {
            /* in the other case the register is set to the edge value */
            preline_pixel_register = edge_val;
            RIGHT(poutpre) = (PIX32) edge_val&EDGE_DIST;
        }
        
        pix2 = (preline_pixel_register)&1;
        if (pix0) {
            if (pix1 & pix2 & pix7 & pix8) {
                VAL(pout) = FIND_MIN4(LEFT(poutpre), VAL(poutpre), RIGHT(poutpre), LEFT(pout))+1;
            } else {
                VAL(pout) = 1;
            }
        } else {
            VAL(pout) = 0;
        }
        /* previous pixel storing */
        pix8 = pix1;
        pix7 = pix0;
        /* next pixel */
        pout++;
        poutpre++;
    }
}
/**
 * labeling the lines for square grid when going from down right to up left
 * 
 * This function is called by the second pass. Thus there is already a distance
 * computed into out image. This is the distance to the nearest top left edge
 * of the set (for pixel that are true in the input image).
 * 
 * the "pre" line pointers link to the previously computed lines. As we are
 * moving from down right to up left the previous line are the line below the
 * line being computed.
 */
static INLINE void DR2UL_QDIS_LINE(PLINE *plines_out, PLINE *plines_outpre,
                                   Uint32 linoff_out,
                                   PLINE *plines_in, PLINE *plines_inpre,
                                   Uint32 linoff_in,
                                   Uint32 bytes_in, Uint32 bytes_out,
                                   binaryT edge_val)
{
    Uint32 i;
    Sint32 j;
    /* pixels are numbered by the neighbor they are representing in the */
    /* hexagonal grid. pix0 being the central pixel. See grid definition */
    /* for more detail */
    binaryT pix0,pix3,pix4,pix5,pix6;
    
    binaryT current_pixel_register;
    binaryT preline_pixel_register;
    binaryT prov;
    PIX32 p32prov;
    
    /* lines init */
    binaryT *pin = (binaryT *) (*plines_in+linoff_in+bytes_in-BYTEPERWORD);
    binaryT *pinpre = (binaryT *) (*plines_inpre+linoff_in+bytes_in-BYTEPERWORD);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out+bytes_out-4);
    PIX32 *poutpre = (PIX32 *) (*plines_outpre+linoff_out+bytes_out-4);
    
    /* previous value initialisation */
    /*The first value are set to max according to the edge type*/
    RIGHT(pout) = (PIX32) edge_val&EDGE_DIST;
    RIGHT(poutpre) = (PIX32) edge_val&EDGE_DIST;
    pix3 = pix4 = edge_val&1;
    preline_pixel_register = (*pinpre);
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin--) {
        /* reading the input lines register by register */
        current_pixel_register = (*pin);
        for(j=SHIFT1BIT; j>0; j--,pout--,poutpre--) {
            /* for each pixel in the binary register */
            /* ! except the last one ! */
            /* we will analyze its value and determines */
            /* its distance to the set edge given the */
            /* distance of its neighbors */
            pix0 = (current_pixel_register>>j)&1;
            prov = (preline_pixel_register>>(j-1));
            pix6 = prov&1;
            pix5 = (prov&2)>>1;
            if (pix0) {
                if (pix3 & pix4 & pix5 & pix6) {
                    p32prov = FIND_MIN4(LEFT(poutpre), VAL(poutpre), RIGHT(poutpre), RIGHT(pout))+1;
                    VAL(pout) = FIND_MIN2(VAL(pout), p32prov);
                } else {
                    VAL(pout) = 1;
                }
            } else {
                VAL(pout) = 0;
            }
            /* previous pixel storing */
            pix3 = pix0;
            pix4 = pix5;
        }
        /* the last pixel must be processed separately as one of its neighbor */
        /* is not in the preline_pixel_register but in the next one */
        pinpre--;
        pix0 = (current_pixel_register)&1;
        pix5 = (preline_pixel_register)&1;
        
        if (i<(bytes_in-BYTEPERWORD)) {
            /* If the end of the line is not reached we acces the nex register */
            /* of the previous line */
            preline_pixel_register = (*pinpre);
        } else {
            /* in the other case the register is set to the edge value */
            preline_pixel_register = edge_val;
            LEFT(poutpre) = (PIX32) edge_val&EDGE_DIST;
        }
        
        pix6 = (preline_pixel_register>>SHIFT1BIT)&1;
        if (pix0) {
            if (pix3 & pix4 & pix5 & pix6) {
                p32prov = FIND_MIN4(LEFT(poutpre), VAL(poutpre), RIGHT(poutpre), RIGHT(pout))+1;
                VAL(pout) = FIND_MIN2(VAL(pout), p32prov);
            } else {
                VAL(pout) = 1;
            }
        } else {
            VAL(pout) = 0;
        }
        /* previous pixel storing */
        pix3 = pix0;
        pix4 = pix5;
        /*next pixel*/
        pout--;
        poutpre--;
    }
}

/****************************************
 * Grid functions                       *
 ****************************************
 * The functions described here perform labeling depending on the grid
 */

/* SQUARE */

/**
 * Computes distance for pixels inside a set over a square grid.
 * Two passes are needed.
 * \param plines_out pointer on the destination image lines
 * \param linoff_out offset inside the destination image lines
 * \param plines_in pointer on the source image that is pixel lines
 * \param linoff_in offset inside the source image lines
 * \param bytes_in number of bytes inside the in line
 * \param bytes_out number of bytes inside the out line
 * \param nb_lines number of lines in the image processed
 * \param edge_val the value used for the edge
 */
static void MB_QDistance(PLINE *plines_out, Uint32 linoff_out,
                         PLINE *plines_in, Uint32 linoff_in,
                         Uint32 bytes_in, Uint32 bytes_out,
                         Uint32 nb_lines, binaryT edge_val)
{
    Uint32 i;
    PLINE *plines_outpre = plines_out;
    PLINE *plines_inpre = plines_in;
    plines_outpre--;
    plines_inpre--;
   
    /* do the first line */
    UPEDGE_LINE(plines_out,linoff_out,plines_in,linoff_in,bytes_in,edge_val);

    for(i = 1; i < nb_lines; i++) {
        plines_in++, plines_inpre++, plines_out++, plines_outpre++;
        UL2DR_QDIS_LINE(plines_out,plines_outpre,linoff_out,plines_in,plines_inpre,linoff_in,bytes_in,edge_val);
    }  
  
    /*
     * second pass from down right corner to upper left DR2UL 
     */
    plines_outpre = plines_out;
    plines_inpre = plines_in;
    plines_outpre++;
    plines_inpre++;
  
    DOWNEDGE_LINE(plines_out,linoff_out,plines_in,linoff_in,bytes_in,bytes_out,edge_val);

    for(i = 1; i < nb_lines; i++) {
        plines_in--, plines_inpre--, plines_out--, plines_outpre--;
        DR2UL_QDIS_LINE(plines_out,plines_outpre,linoff_out,plines_in,plines_inpre,linoff_in,bytes_in,bytes_out,edge_val);
    }
}


/* HEXAGONAL */

/**
 * Computes distance for pixels inside a set over an hexagonal grid.
 * Two passes are needed.
 * \param plines_out pointer on the destination image lines
 * \param linoff_out offset inside the destination image lines
 * \param plines_in pointer on the source image pixel lines
 * \param linoff_in offset inside the source image lines
 * \param bytes_in number of bytes inside the in line
 * \param bytes_out number of bytes inside the out line
 * \param nb_lines number of lines in the image processed
 * \param edge_val the value used for the edge
 */
static void MB_HDistance(PLINE *plines_out, Uint32 linoff_out,
                         PLINE *plines_in, Uint32 linoff_in,
                         Uint32 bytes_in, Uint32 bytes_out,
                         Uint32 nb_lines, binaryT edge_val)
{
    Uint32 i;
    PLINE *plines_outpre = plines_out;
    PLINE *plines_inpre = plines_in;
    plines_outpre--;
    plines_inpre--;

    /* 
     * first pass from upper left corner to down right UL2DR 
     */

    /* do the first -- even -- line */
    UPEDGE_LINE(plines_out,linoff_out,plines_in,linoff_in,bytes_in,edge_val);

    /* do the second -- odd -- line */
    plines_in++, plines_inpre++, plines_out++, plines_outpre++;
    UL2DR_HDIS_LINE_ODD(plines_out,plines_outpre,linoff_out,plines_in,plines_inpre,linoff_in,bytes_in,edge_val);

    for(i = 2; i < nb_lines; i+=2) {
        /* do even line */
        plines_in++, plines_inpre++, plines_out++, plines_outpre++;
        UL2DR_HDIS_LINE_EVEN(plines_out,plines_outpre,linoff_out,plines_in,plines_inpre,linoff_in,bytes_in,edge_val);
        /* do odd line */
        plines_in++, plines_inpre++, plines_out++, plines_outpre++;
        UL2DR_HDIS_LINE_ODD(plines_out,plines_outpre,linoff_out,plines_in,plines_inpre,linoff_in,bytes_in,edge_val);
    }
  
    /*
     * second pass from down right corner to upper left DR2UL 
     */
    plines_outpre = plines_out;
    plines_inpre = plines_in;
    plines_outpre++;
    plines_inpre++;
  
    DOWNEDGE_LINE(plines_out,linoff_out,plines_in,linoff_in,bytes_in,bytes_out,edge_val);

    plines_in--, plines_inpre--, plines_out--, plines_outpre--;
    DR2UL_HDIS_LINE_EVEN(plines_out,plines_outpre,linoff_out,plines_in,plines_inpre,linoff_in,bytes_in,bytes_out,edge_val);

    for(i = 2; i < nb_lines; i+=2) {
        /* do odd line */
        plines_in--, plines_inpre--, plines_out--, plines_outpre--;
        DR2UL_HDIS_LINE_ODD(plines_out,plines_outpre,linoff_out,plines_in,plines_inpre,linoff_in,bytes_in,bytes_out,edge_val);
        /* do even line */
        plines_in--, plines_inpre--, plines_out--, plines_outpre--;
        DR2UL_HDIS_LINE_EVEN(plines_out,plines_outpre,linoff_out,plines_in,plines_inpre,linoff_in,bytes_in,bytes_out,edge_val);
    }
}

/************************************************/
/*High level function and global variables    */
/************************************************/

/** typedef for the definition of function arguments */
typedef void (TSWITCHEP) (PLINE *plines_out, Uint32 linoff_out,
                          PLINE *plines_in, Uint32 linoff_in,
                          Uint32 bytes_in, Uint32 bytes_out,
                          Uint32 nb_lines, binaryT edge_val);

/** 
 * array giving the function to use to go in a given direction with
 * regards to the grid in use (hexagonal or square).
 */
static TSWITCHEP *SwitchTo[2] =
{ /* square grid */
     MB_QDistance,
  /* hexagonal grid*/
     MB_HDistance
};

/**
 * Computes for each pixel the distance to the edge of the set in which the pixel is found
 *
 * The algorithm works with two passes, first from the top left to the bottom
 * right and then back.
 *
 * \param src the binary source image
 * \param dest the 32-bits image in which the distance for each pixel is stored
 * \param grid the grid used (either square or hexagonal)
 * \param edge the kind of edge to use (behavior for pixels near edge depends on it)
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Distanceb(MB_Image *src, MB_Image *dest, enum MB_grid_t grid, enum MB_edgemode_t edge) {

    Uint32 linoff_in, linoff_out;
    Uint32 bytes_in, bytes_out;
    PLINE *plines_in, *plines_out;
    TSWITCHEP *fn;
    
    /* verification over image size compatibility */
    if (!MB_CHECK_SIZE_2(src, dest)) {
        return ERR_BAD_SIZE;
    }
    
    /* Only binary images can be processed */
    /* the output is necessarly a 32-bit image */
    switch (MB_PROBE_PAIR(src, dest)) {
    case MB_PAIR_1_32:
        break;
    default:
        return ERR_BAD_DEPTH;
    }
    
    /* setting up pointers */
    plines_in = &src->PLINES[MB_Y_TOP(src)];
    plines_out = &dest->PLINES[MB_Y_TOP(dest)];
    linoff_in  = MB_LINE_OFFSET(src);
    linoff_out = MB_LINE_OFFSET(dest);
    bytes_in = MB_LINE_COUNT(src);
    bytes_out = MB_LINE_COUNT(dest);
    
    /* Calling the corresponding function */
    fn = SwitchTo[grid];
    fn(plines_out, linoff_out, plines_in, linoff_in, bytes_in, bytes_out, src->height, BIN_FILL_VALUE(edge));
    
    return NO_ERR;
}
