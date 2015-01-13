/**
 * \file MB_Labelb.c
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

/* neighbor pixel reading and accessing */
/* macros work with the pointer to the pixel */
/** Macro returning the value of a pixel */
#define VAL(p_pix) (*p_pix)
/** Macro returning the value of the left neighbor pixel */
#define LEFT(p_pix) (*(p_pix-1))
/** Macro returning the value of the right neighbor pixel */
#define RIGHT(p_pix) (*(p_pix+1))

/****************************************/
/* Global variables                     */
/****************************************/

/**
 * Label structure holding all the information needed to handle
 * labels attribution and creation.
 */
typedef struct {
    /** Equivalence between label in an image */
    PIX32 *EQ;
    /** Equivalence between corrected label in an image */
    PIX32 *CEQ;
    /** The greatest number of label possible according to current image size */
    Uint32 maxEQ;
    /** Current label index (value given to the next label) */
    PIX32 current;
    /** Current corrected label index (value given to the next label) */
    PIX32 ccurrent;
} MB_Label;

/****************************************/
/* Base functions                       */
/****************************************/
/* The functions described here realise the basic operations */
/* needed to label pixels */

/* recursive function to find the root label*/
static PIX32 FIND_ABOVE_LABEL(MB_Label *labels, PIX32 inlabel)
{
    if (labels->EQ[inlabel]==inlabel) {
        return inlabel;
    } else {
        return FIND_ABOVE_LABEL(labels, labels->EQ[inlabel]);
    }
}

/* function returning the corrected label to use.*/
/* The corrected label have values that follow each other */
/* along a specific rule to allow lblow and lbhml values */
/* to exclude some value in the first byte */
static PIX32 FIND_CORRECT_LABEL(MB_Label *labels, PIX32 inlabel, PIX32 lblow, PIX32 lbhml)
{
    inlabel = FIND_ABOVE_LABEL(labels, inlabel);

    if (labels->CEQ[inlabel]==0) {
        labels->CEQ[inlabel] = lblow + (labels->ccurrent%lbhml) + 256*(labels->ccurrent/lbhml);
        labels->ccurrent++;
    }
    
    return labels->CEQ[inlabel];
}

/**
 * labeling the upper line (near the image edge)
 *
 * \param plines_out pointer on the destination image pixel line
 * \param linoff_out offset inside the destination image line
 * \param plines_in pointer on the source image pixel line
 * \param linoff_in offset inside the source image line
 * \param bytes_in number of bytes inside the line
 * \param labels the labels arrays and context
 */
static INLINE void EDGE_LINE(PLINE *plines_out, Uint32 linoff_out,
                               PLINE *plines_in, Uint32 linoff_in,
                               Uint32 bytes_in, MB_Label *labels)
{
    Uint32 i,j;
    binaryT pix_reg, previous_pix;

    binaryT *pin = (binaryT *) (*plines_in+linoff_in);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out);
    
    /* previous values initialisation */
    previous_pix = 0;
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin++) {
        /* reading a register of pixels */
        pix_reg = (*pin);
        for(j=0; j<CHARBIT*BYTEPERWORD; j++,pout++) {
            /* for all the pixels in the register */
            if (pix_reg&1) {
                /* the pixel need to be labelled */
                if (previous_pix&1) {
                    /* with the same label as its neighbor since the */
                    /* neighbor is set (and thus already labelled) */
                    /* (only one neighbor since the other are in the */
                    /* edge) */
                    VAL(pout) = LEFT(pout);
                } else {
                    /* or with a new label value */
                    VAL(pout) = (labels->current);
                    /* which mark the label as being used */
                    labels->EQ[labels->current] = labels->current;
                    labels->current++;
                }
            }
            previous_pix = pix_reg;
            /* next pixel */
            pix_reg = pix_reg>>1;
        }
    }
}

/**
 * labeling the odd lines for hexagonal grid
 * 
 * \param plines_out pointer on the current line in the destination image
 * \param plines_outpre pointer to the previous line in the destination image
 * \param linoff_out offset inside the destination image lines
 * \param plines_in pointer on the current line in the source image
 * \param plines_inpre pointer to the previous line in the source image
 * \param linoff_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param labels the labels arrays and context
 */
static INLINE void HLAB_LINE_ODD(PLINE *plines_out, PLINE *plines_outpre,
                                 Uint32 linoff_out,
                                 PLINE *plines_in, PLINE *plines_inpre,
                                 Uint32 linoff_in,
                                 Uint32 bytes_in, MB_Label *labels)
{
    Uint32 i,j;
    binaryT pix_reg_cur, pix_reg_pre, previous_pix;
    binaryT neighbor_state;

    binaryT *pin = (binaryT *) (*plines_in+linoff_in);
    binaryT *pinpre = (binaryT *) (*plines_inpre+linoff_in);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out);
    PIX32 *poutpre = (PIX32 *) (*plines_outpre+linoff_out);
    
    /* previous values initialisation */
    previous_pix = 0;
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin++) {
        /* reading a register of pixels in the two sources lines*/
        pix_reg_cur = (*pin);
        pix_reg_pre = (*pinpre);
        for(j=1; j<CHARBIT*BYTEPERWORD; j++,pout++,poutpre++) {
            /* for all the pixels in the registers */
            /* except the last one */
            if (pix_reg_cur&1) {
                neighbor_state = (previous_pix&1) |
                                 ((pix_reg_pre&3)<<1);
                /* The neighbor state gives the values of the neighbor bit of the currently */
                /* evaluated bit (a&1). It allows to determine which value will take the label */
                /* in the output image (pout).*/
                /* We always take the label of the last labelled neighbor */
                /* in case more than one neighbor is labelled, the equivalence */
                /* table is updated */
                switch(neighbor_state) {
                case 1:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                    break;
                case 2:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, VAL(poutpre));
                    break;
                case 3:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                    if (VAL(poutpre) != VAL(pout))
                        labels->EQ[VAL(pout)] = FIND_ABOVE_LABEL(labels, VAL(poutpre));
                    break;
                case 4:
                case 6:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, RIGHT(poutpre));
                    break;
                case 5:
                case 7:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                    if (RIGHT(poutpre) != VAL(pout))
                        labels->EQ[VAL(pout)] = FIND_ABOVE_LABEL(labels, RIGHT(poutpre));
                    break;
                default: /* case 0 */
                    VAL(pout) = (labels->current);
                    /* no neighbors labelled we take one */
                    labels->EQ[labels->current] = labels->current;
                    labels->current++;
                    break;
                }
            }
            previous_pix = pix_reg_cur;
            /* next pixel */
            pix_reg_cur = pix_reg_cur>>1;
            pix_reg_pre = pix_reg_pre>>1;
        }
        /* the last pixel cannot be processed because one of its neighbor is not */
        /* inside the previous line pixel register */
        /* to process it we then need to fetch the neighbor in the next register */
        pinpre++;
        pix_reg_pre = pix_reg_pre|((*pinpre&1)<<1);
        if (pix_reg_cur&1) {
            neighbor_state = (previous_pix&1) |
                             ((pix_reg_pre&3)<<1);
            /* The neighbor state gives the values of the neighbor bit of the currently */
            /* evaluated bit (a&1). It allows to determine which value will take the label */
            /* in the output image (p2).*/
            switch(neighbor_state) {
            case 1:
                VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                break;
            case 2:
                VAL(pout) = FIND_ABOVE_LABEL(labels, VAL(poutpre));
                break;
            case 3:
                VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                if (VAL(poutpre) != VAL(pout))
                    labels->EQ[VAL(pout)] = FIND_ABOVE_LABEL(labels, VAL(poutpre));
                break;
            case 4:
            case 6:
                VAL(pout) = FIND_ABOVE_LABEL(labels, RIGHT(poutpre));
                break;
            case 5:
            case 7:
                VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                if (RIGHT(poutpre) != VAL(pout))
                    labels->EQ[VAL(pout)] = FIND_ABOVE_LABEL(labels, RIGHT(poutpre));
                break;
            default: /* case 0 */
                VAL(pout) = (labels->current);
                /* no neighbors labelled we take one */
                labels->EQ[labels->current] = labels->current;
                labels->current++;
                break;
            }
        }
        previous_pix = pix_reg_cur;
        /* next pixel */
        pout++;
        poutpre++;
    }
}

/**
 * labeling the even lines for hexagonal grid
 * 
 * \param plines_out pointer on the current line in the destination image
 * \param plines_outpre pointer to the previous line in the destination image
 * \param linoff_out offset inside the destination image lines
 * \param plines_in pointer on the current line in the source image
 * \param plines_inpre pointer to the previous line in the source image
 * \param linoff_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param labels the labels arrays and context
 */
static INLINE void HLAB_LINE_EVEN(PLINE *plines_out, PLINE *plines_outpre,
                                  Uint32 linoff_out,
                                  PLINE *plines_in, PLINE *plines_inpre,
                                  Uint32 linoff_in,
                                  Uint32 bytes_in, MB_Label *labels)
{
    Uint32 i,j;
    binaryT pix_reg_cur, pix_reg_pre, previous_pix_cur, previous_pix_pre;
    binaryT neighbor_state;

    binaryT *pin = (binaryT *) (*plines_in+linoff_in);
    binaryT *pinpre = (binaryT *) (*plines_inpre+linoff_in);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out);
    PIX32 *poutpre = (PIX32 *) (*plines_outpre+linoff_out);
    
    /* previous values initialisation */
    previous_pix_cur = 0;
    previous_pix_pre = 0;
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin++,pinpre++) {
        /* reading a register of pixels in the two sources lines*/
        pix_reg_cur = (*pin);
        pix_reg_pre = (*pinpre);
        for(j=0; j<CHARBIT*BYTEPERWORD; j++,pout++,poutpre++) {
            /* for all the pixels in the registers */
            if (pix_reg_cur&1) {
                neighbor_state = (previous_pix_cur&1) |
                                 ((previous_pix_pre&1)<<1) |
                                 ((pix_reg_pre&1)<<2);
                /* The neighbor state gives the values of the neighbor bit of the currently */
                /* evaluated bit (a&1). It allows to determine which value will take the label */
                /* in the output image (pout).*/
                /* We always take the label of the last labelled neighbor */
                /* in case more than one neighbor is labelled, the equivalence */
                /* table is updated */
                switch(neighbor_state) {
                case 1:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                    break;
                case 2:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(poutpre));
                    break;
                case 3:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                    if (LEFT(poutpre) != VAL(pout))
                        labels->EQ[VAL(pout)] = FIND_ABOVE_LABEL(labels, LEFT(poutpre));
                    break;
                case 4:
                case 6:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, VAL(poutpre));
                    break;
                case 5:
                case 7:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                    if (VAL(poutpre) != VAL(pout))
                        labels->EQ[VAL(pout)] = FIND_ABOVE_LABEL(labels, VAL(poutpre));
                    break;
                default: /* case 0 */
                    VAL(pout) = (labels->current);
                    /* no neighbors labelled we take one */
                    labels->EQ[labels->current] = labels->current;
                    labels->current++;
                    break;
                }
            }
            previous_pix_cur = pix_reg_cur;
            previous_pix_pre = pix_reg_pre;
            /* next pixel */
            pix_reg_cur = pix_reg_cur>>1;
            pix_reg_pre = pix_reg_pre>>1;
        }
    }
}

/**
 * labeling the lines for square grid
 * 
 * \param plines_out pointer on the current line in the destination image
 * \param plines_outpre pointer to the previous line in the destination image
 * \param linoff_out offset inside the destination image lines
 * \param plines_in pointer on the current line in the source image
 * \param plines_inpre pointer to the previous line in the source image
 * \param linoff_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param labels the labels arrays and context
 */
static INLINE void QLAB_LINE(PLINE *plines_out, PLINE *plines_outpre,
                             Uint32 linoff_out,
                             PLINE *plines_in, PLINE *plines_inpre,
                             Uint32 linoff_in,
                             Uint32 bytes_in, MB_Label *labels)
{
    Uint32 i,j;
    binaryT pix_reg_cur, pix_reg_pre, previous_pix_cur, previous_pix_pre;
    binaryT neighbor_state;

    binaryT *pin = (binaryT *) (*plines_in+linoff_in);
    binaryT *pinpre = (binaryT *) (*plines_inpre+linoff_in);
    PIX32 *pout = (PIX32 *) (*plines_out+linoff_out);
    PIX32 *poutpre = (PIX32 *) (*plines_outpre+linoff_out);
    
    /* previous values initialisation */
    previous_pix_cur = 0;
    previous_pix_pre = 0;
    
    for(i=0;i<bytes_in;i+=BYTEPERWORD,pin++) {
        /* reading a register of pixels in the two sources lines*/
        pix_reg_cur = (*pin);
        pix_reg_pre = (*pinpre);
        for(j=1; j<CHARBIT*BYTEPERWORD; j++,pout++,poutpre++) {
            /* for all the pixels in the registers */
            /* except the last one */
            if (pix_reg_cur&1) {
                neighbor_state = (previous_pix_cur&1) |
                                 ((previous_pix_pre&1)<<1) |
                                 ((pix_reg_pre&3)<<2);
                /* The neighbor state gives the values of the neighbor bit of the currently */
                /* evaluated bit (a&1). It allows to determine which value will take the label */
                /* in the output image (pout).*/
                /* We always take the label of the last labelled neighbor */
                /* in case more than one neighbor is labelled, the equivalence */
                /* table is updated */
                switch(neighbor_state) {
                case 1:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                    break;
                case 2:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(poutpre));
                    break;
                case 3:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                    if (LEFT(poutpre) != VAL(pout))
                        labels->EQ[VAL(pout)] = FIND_ABOVE_LABEL(labels, LEFT(poutpre));
                    break;
                case 4:
                case 6:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, VAL(poutpre));
                    break;
                case 5:
                case 7:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                    if (VAL(poutpre) != VAL(pout))
                        labels->EQ[VAL(pout)] = FIND_ABOVE_LABEL(labels, VAL(poutpre));
                    break;
                case 8:
                case 10:
                case 12:
                case 14:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, RIGHT(poutpre));
                    break;
                case 9:
                case 11:
                case 13:
                case 15:
                    VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                    if (RIGHT(poutpre) != VAL(pout))
                        labels->EQ[VAL(pout)] = FIND_ABOVE_LABEL(labels, RIGHT(poutpre));
                    break;
                default: /* case 0 */
                    VAL(pout) = (labels->current);
                    /* no neighbors labelled we take one */
                    labels->EQ[labels->current] = labels->current;
                    labels->current++;
                    break;
                }
            }
            previous_pix_cur = pix_reg_cur;
            previous_pix_pre = pix_reg_pre;
            /* next pixel */
            pix_reg_cur = pix_reg_cur>>1;
            pix_reg_pre = pix_reg_pre>>1;
        }
        /* the last pixel cannot be processed because one of its neighbor is not */
        /* inside the previous line pixel register */
        /* to process it we then need to fetch the neighbor in the next register */
        pinpre++;
        pix_reg_pre = pix_reg_pre|((*pinpre&1)<<1);
        if (pix_reg_cur&1) {
            neighbor_state = (previous_pix_cur&1) |
                             ((previous_pix_pre&1)<<1) |
                             ((pix_reg_pre&3)<<2);
            /* The neighbor state gives the values of the neighbor bit of the currently */
            /* evaluated bit (a&1). It allows to determine which value will take the label */
            /* in the output image (p2).*/
            switch(neighbor_state) {
            case 1:
                VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                break;
            case 2:
                VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(poutpre));
                break;
            case 3:
                VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                if (LEFT(poutpre) != VAL(pout))
                    labels->EQ[VAL(pout)] = FIND_ABOVE_LABEL(labels, LEFT(poutpre));
                break;
            case 4:
            case 6:
                VAL(pout) = FIND_ABOVE_LABEL(labels, VAL(poutpre));
                break;
            case 5:
            case 7:
                VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                if (VAL(poutpre) != VAL(pout))
                    labels->EQ[VAL(pout)] = FIND_ABOVE_LABEL(labels, VAL(poutpre));
                break;
            case 8:
            case 10:
            case 12:
            case 14:
                VAL(pout) = FIND_ABOVE_LABEL(labels, RIGHT(poutpre));
                break;
            case 9:
            case 11:
            case 13:
            case 15:
                VAL(pout) = FIND_ABOVE_LABEL(labels, LEFT(pout));
                if (RIGHT(poutpre) != VAL(pout))
                    labels->EQ[VAL(pout)] = FIND_ABOVE_LABEL(labels, RIGHT(poutpre));
                break;
            default: /* case 0 */
                VAL(pout) = (labels->current);
                /* no neighbors labelled we take one */
                labels->EQ[labels->current] = labels->current;
                labels->current++;
                break;
            }
        }
        previous_pix_cur = pix_reg_cur;
        previous_pix_pre = pix_reg_pre;
        /* next pixel */
        pout++;
        poutpre++;
    }
}

/****************************************
 * Grid functions                         *
 ****************************************
 * The functions described here perform labeling depending on the grid
 */

/* SQUARE */

/**
 * Labelizes the object found in src image over a square grid.
 * \param plines_out pointer on the destination image lines
 * \param off_out offset inside the destination image lines
 * \param plines_in pointer on the source image pixel lines
 * \param off_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param nb_lines number of lines inside the image processed
 * \param labels the labels arrays and context
 */
static void MB_QLabel(PLINE *plines_out, Uint32 linoff_out,
                      PLINE *plines_in, Uint32 linoff_in,
                      Uint32 bytes_in, Uint32 nb_lines,
                      MB_Label *labels)
{
    Uint32 i;
    PLINE *plines_outpre = plines_out;
    PLINE *plines_inpre = plines_in;
    plines_outpre--;
    plines_inpre--;
   
    /* do the first line */
    EDGE_LINE(plines_out,linoff_out,plines_in,linoff_in,bytes_in,labels);

    for(i = 1; i < nb_lines; i++) {
        /* do even line */
        plines_in++, plines_inpre++, plines_out++, plines_outpre++;
        QLAB_LINE(plines_out,plines_outpre,linoff_out,plines_in,plines_inpre,linoff_in,bytes_in,labels);
    }
}

/* HEXAGONAL */

/**
 * Labelizes the object found in src image over an hexagonal grid.
 * \param plines_out pointer on the destination image lines
 * \param off_out offset inside the destination image lines
 * \param plines_in pointer on the source image pixel lines
 * \param off_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param nb_lines number of lines inside the image processed
 * \param labels the labels arrays and context
 */
static void MB_HLabel(PLINE *plines_out, Uint32 linoff_out,
                 PLINE *plines_in, Uint32 linoff_in,
                 Uint32 bytes_in, Uint32 nb_lines,
                 MB_Label *labels)
{
    Uint32 i;
    PLINE *plines_outpre = plines_out;
    PLINE *plines_inpre = plines_in;
    plines_outpre--;
    plines_inpre--;
   
    /* do the first -- even -- line */
    EDGE_LINE(plines_out,linoff_out,plines_in,linoff_in,bytes_in,labels);

    /* do the second -- odd -- line */
    plines_in++, plines_inpre++, plines_out++, plines_outpre++;
    HLAB_LINE_ODD(plines_out,plines_outpre,linoff_out,plines_in,plines_inpre,linoff_in,bytes_in,labels);

    for(i = 2; i < nb_lines; i+=2) {
        /* do even line */
        plines_in++, plines_inpre++, plines_out++, plines_outpre++;
        HLAB_LINE_EVEN(plines_out,plines_outpre,linoff_out,plines_in,plines_inpre,linoff_in,bytes_in,labels);
        /* do odd line */
        plines_in++, plines_inpre++, plines_out++, plines_outpre++;
        HLAB_LINE_ODD(plines_out,plines_outpre,linoff_out,plines_in,plines_inpre,linoff_in,bytes_in,labels);
    }
}

/****************************************
 * Tidying function                     *
 ****************************************
 * The functions tidy the label
 */

/**
 * Tidies the label.
 * \param plines_out pointer on the destination image lines
 * \param off_out offset inside the destination image lines
 * \param bytes number of bytes inside the line
 * \param nb_lines number of lines inside the image processed
 * \param lblow the lowest value allowed for label on the low byte (must be inferior to lbhigh)
 * \param lbhigh the first high value NOT allowed for label on the low byte (maximum allowed is 256)
 * \param labels the labels arrays and context
 */
static INLINE void MB_TidyLabel(PLINE *plines_out, Uint32 linoff_out, 
                                Uint32 bytes, Uint32 nb_lines,
                                PIX32 lblow, PIX32 lbhigh,
                                MB_Label *labels)
{
    Uint32 u,v;
    PIX32 *p1;
    
    for(u=0; u<nb_lines; u++, plines_out++) {
        p1 = (PIX32 *) (*plines_out + linoff_out);
        for(v=0; v<bytes; v+=4, p1++) {
            if (*p1!=0) {
                *p1 = FIND_CORRECT_LABEL(labels, *p1, lblow, lbhigh-lblow);
            }
        }            
    }
}

/************************************************/
/*High level function and global variables    */
/************************************************/

/** typedef for the definition of function arguments */
typedef void (TSWITCHEP) (PLINE *plines_out, Uint32 linoff_out,
              PLINE *plines_in, Uint32 linoff_in,
              Uint32 bytes_in, Uint32 nb_lines,
              MB_Label *labels);

/** 
 * array giving the function to use to go in a given direction with
 * regard to the grid in use (hexagonal or square).
 */
static TSWITCHEP *SwitchTo[2] =
{ /* square grid */
     MB_QLabel,
  /* hexagonal grid*/
     MB_HLabel
};

/**
 * Labeling the object found in src image.
 *
 * \param src the binary source image where the object must be labelled
 * \param dest the 32-bit image where object are labelled
 * \param lblow the lowest value allowed for label on the low byte (must be inferior to lbhigh)
 * \param lbhigh the first high value NOT allowed for label on the low byte (maximum allowed is 256)
 * \param pNbobj the number of object founds
 * \param grid the grid used (either square or hexagonal)
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_Labelb(MB_Image *src, MB_Image *dest, Uint32 lblow, Uint32 lbhigh, Uint32 *pNbobj, enum MB_grid_t grid) {

    Uint32 linoff_in, linoff_out;
    Uint32 bytes_in, bytes_out;
    PLINE *plines_in, *plines_out;
    MB_Label labels;
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
    /* Verification over parameter given in entry*/
    if (lblow>=lbhigh) return ERR_BAD_VALUE;
    if (lbhigh>256) return ERR_BAD_VALUE;
    
    /* Initializing the algorithm parameters */
    labels.current = 1;
    labels.ccurrent = 0;
    labels.maxEQ = (src->width*src->height)/4;
    labels.EQ = MB_malloc(labels.maxEQ*sizeof(PIX32));
    labels.CEQ = MB_malloc(labels.maxEQ*sizeof(PIX32));
    if(labels.EQ==NULL || labels.CEQ==NULL){
        /* in case allocation goes wrong */
        MB_free(labels.EQ);
        MB_free(labels.CEQ);
        return ERR_CANT_ALLOCATE_MEMORY;
    } 
    MB_memset(labels.EQ, 0, labels.maxEQ*sizeof(PIX32));
    MB_memset(labels.CEQ, 0, labels.maxEQ*sizeof(PIX32));
    
    /* the label image is reset */
    MB_ConSet(dest, 0);
    
    /* setting up pointers */
    plines_in = &src->PLINES[MB_Y_TOP(src)];
    plines_out = &dest->PLINES[MB_Y_TOP(dest)];
    linoff_in  = MB_LINE_OFFSET(src);
    linoff_out = MB_LINE_OFFSET(dest);
    bytes_in = MB_LINE_COUNT(src);
    bytes_out = MB_LINE_COUNT(dest);
    
    /* Calling the corresponding function */
    fn = SwitchTo[grid];
    fn(plines_out, linoff_out, plines_in, linoff_in, bytes_in, src->height, &labels);

    MB_TidyLabel(plines_out, linoff_out, bytes_out, src->height, (PIX32) lblow, (PIX32) lbhigh, &labels);
    
    *pNbobj = (int) (labels.ccurrent);
    
    /* freeing the labels arrays */
    MB_free(labels.EQ);
    MB_free(labels.CEQ);

    return NO_ERR;
}

