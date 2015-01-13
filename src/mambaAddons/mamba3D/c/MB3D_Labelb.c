/**
 * \file MB3D_Labelb.c
 * \author Nicolas Beucher
 * \date 26-09-2011
 *
 */
 
/*
 * Copyright (c) <2011>, <Nicolas BEUCHER>
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
#include "mamba3DApi_loc.h"

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
} MB3D_Label;

/****************************************/
/* Base functions                       */
/****************************************/
/* The functions described here realise the basic operations */
/* needed to label pixels */

/* this functions gives the value of the pixel inside the image */
/* with its position */
static PIX32 GET_VAL(MB3D_Image *im, int x, int y, int z)
{
    PIX32 *p, value;
    
    if( (z >= (int)(im->len)) || 
        (z <  0) ||
        (y >= (int)(im->seq[0]->height)) ||
        (y <  0) ||
        (x >= (int)(im->seq[0]->width)) ||
        (x <  0) ) {
        value = 0;
    } else {
        p = (PIX32 *) (im->seq[z]->PLINES[y+MB_Y_TOP(im->seq[z])] + MB_LINE_OFFSET(im->seq[z]) + x*4);
        value = *p;
    }

    return value;
}

/* recursive function to find the root label*/
static PIX32 FIND_ABOVE_LABEL(MB3D_Label *labels, PIX32 inlabel)
{
    if (labels->EQ[inlabel]==inlabel) {
        return inlabel;
    } else {
        labels->EQ[inlabel] = FIND_ABOVE_LABEL(labels, labels->EQ[inlabel]);
        return labels->EQ[inlabel];
    }
}

/* function returning the corrected label to use.*/
/* The corrected label have values that follow each other */
/* along a specific rule to allow lblow and lbhml values */
/* to exclude some value in the first byte */
static PIX32 FIND_CORRECT_LABEL(MB3D_Label *labels, PIX32 inlabel, PIX32 lblow, PIX32 lbhml)
{
    inlabel = FIND_ABOVE_LABEL(labels, inlabel);

    if (labels->CEQ[inlabel]==0) {
        labels->CEQ[inlabel] = lblow + (labels->ccurrent%lbhml) + 256*(labels->ccurrent/lbhml);
        labels->ccurrent++;
    }
    
    return labels->CEQ[inlabel];
}

/** Table giving the offset for the previous neighbor in cube grid (x, y and z) */ 
const int cubePreDir[13][3] = {
    {0,-1,0},{1,-1,0},{-1,0,0},{-1,-1,0},
    {0,0,-1},{0,-1,-1},{1,-1,-1},{1,0,-1},{1,1,-1},{0,1,-1},{-1,1,-1},{-1,0,-1},{-1,-1,-1},
};

/** Table giving the offset for the neighbor in face-centered cubic grid (x, y and z) */
/* the direction depends on the coordinates of the line y and planes z*/
const int fccPreDir[6][6][3] = {
    /*1        5        6         7        8         9        */
    {{0,-1,0},{-1,0,0},{-1,-1,0},{0,0,-1},{-1,0,-1},{-1,-1,-1}},
    {{1,-1,0},{-1,0,0},{0,-1,0}, {0,0,-1},{-1,0,-1},{0,-1,-1}},
    
    {{0,-1,0},{-1,0,0},{-1,-1,0},{0,0,-1},{0,1,-1}, {-1,1,-1}},
    {{1,-1,0},{-1,0,0},{0,-1,0}, {0,0,-1},{1,1,-1}, {0,1,-1}},
    
    {{0,-1,0},{-1,0,0},{-1,-1,0},{0,0,-1},{0,-1,-1},{1,0,-1}},
    {{1,-1,0},{-1,0,0},{0,-1,0}, {0,0,-1},{1,-1,-1},{1,0,-1}}
};

/* function returning the corrected label for a pixel at a given position */
/* in cubic grid */
static PIX32 GET_CUBIC_LABEL(MB3D_Image *dest, MB3D_Label *labels, int x, int y, int z)
{
    PIX32 value, label, rlab;
    int i;
    
    label = 0;
    for(i=0; i<13; i++) {
        value = GET_VAL(dest, x+cubePreDir[i][0], y+cubePreDir[i][1], z+cubePreDir[i][2]);
        rlab = FIND_ABOVE_LABEL(labels, value);
        if (rlab!=0) {
            /* when the neighbor pixel has a label we take it */
            if (label==0) {
                /* No label yet for the position x,y,z */
                label = rlab;
            } else {
                /* our pixel already has a label */
                /* we must then put a correspondance between those two */
                labels->EQ[rlab] = label;
            }
        }
    }
    
    if (label==0) {
        /* no neighbors labelled we take one */
        label = (labels->current);
        labels->EQ[label] = label;
        labels->current++;
    }
    
    return label;
}

/* function returning the corrected label for a pixel at a given position */
/* in cubic grid */
static PIX32 GET_FCC_LABEL(MB3D_Image *dest, MB3D_Label *labels, int x, int y, int z)
{
    PIX32 value, label, rlab;
    int i,dirSelect;
    
    /* Computing the directions to use depending on the y and z of the */
    /* pixel */
    dirSelect = ((z%3)<<1)+(y%2);
    
    label = 0;
    for(i=0; i<6; i++) {
        value = GET_VAL(dest,
                        x+fccPreDir[dirSelect][i][0],
                        y+fccPreDir[dirSelect][i][1],
                        z+fccPreDir[dirSelect][i][2]);
        rlab = FIND_ABOVE_LABEL(labels, value);
        if (rlab!=0) {
            /* when the neighbor pixel has a label we take it */
            if (label==0) {
                /* No label yet for the position x,y,z */
                label = rlab;
            } else {
                /* our pixel already has a label */
                /* we must then put a correspondance between those two */
                labels->EQ[rlab] = label;
            }
        }
    }
    
    if (label==0) {
        /* no neighbors labelled we take one */
        label = (labels->current);
        labels->EQ[label] = label;
        labels->current++;
    }
    
    return label;
}

/****************************************
 * Grid functions                       *
 ****************************************
 * The functions described here perform labeling depending on the grid
 */

/* CUBIC */

/**
 * Labelizes the object found in src image over a cubic grid.
 * \param dest the 32-bit 3D image where object are labelled
 * \param src the binary source 3D image where the object must be labelled
 * \param labels the labels arrays and context
 */
static void MB3D_cubeLabel(MB3D_Image *dest, MB3D_Image *src, MB3D_Label *labels)
{
    int x,y,z,posbinx;
    MB_Image *imSrc, *imDest;
    PIX32 *pout, *pin;
    
    for(z=0; z<dest->len; z++) {
        imDest = dest->seq[z];
        imSrc = src->seq[z];
        for(y=0; y<(int) (imDest->height); y++) {
            pout = (PIX32 *) (imDest->PLINES[y+MB_Y_TOP(imDest)] + MB_LINE_OFFSET(imDest));
            pin = (PIX32 *) (imSrc->PLINES[y+MB_Y_TOP(imSrc)] + MB_LINE_OFFSET(imSrc));
            posbinx = 0;
            for(x=0; x<(int) (imDest->width); x++, pout++) {
                if (posbinx==32) {
                    /* if the end of the binary register in pin is reached */
                    /* then we select the next starting at 0 */
                    posbinx = 0;
                    pin++;
                }
                
                if ( (((*pin)>>posbinx) & 0x1) == 0x1) {
                    /* if the pixel in the src binary register is not */
                    /* empty then we label it in the dest image */
                    *pout = GET_CUBIC_LABEL(dest,labels,x,y,z);
                }
                /* next pixel in the binary register pin */
                posbinx++;
            }
        }
    }
}

/* FACE CENTERED CUBIC */

/**
 * Labelizes the object found in src image over a face centered cubic grid.
 * \param dest the 32-bit 3D image where object are labelled
 * \param src the binary source 3D image where the object must be labelled
 * \param labels the labels arrays and context
 */
static void MB3D_fccLabel(MB3D_Image *dest, MB3D_Image *src, MB3D_Label *labels)
{
    int x,y,z,posbinx;
    MB_Image *imSrc, *imDest;
    PIX32 *pout, *pin;
    
    for(z=0; z<dest->len; z++) {
        imDest = dest->seq[z];
        imSrc = src->seq[z];
        for(y=0; y<(int) (imDest->height); y++) {
            pout = (PIX32 *) (imDest->PLINES[y+MB_Y_TOP(imDest)] + MB_LINE_OFFSET(imDest));
            pin = (PIX32 *) (imSrc->PLINES[y+MB_Y_TOP(imSrc)] + MB_LINE_OFFSET(imSrc));
            posbinx = 0;
            for(x=0; x<(int) (imDest->width); x++, pout++) {
        
                if (posbinx==32) {
                    /* if the end of the binary register in pin is reached */
                    /* then we select the next starting at 0 */
                    posbinx = 0;
                    pin++;
                }
                
                if ( (((*pin)>>posbinx) & 0x1) == 0x1) {
                    /* if the pixel in the src binary register is not */
                    /* empty then we label it in the dest image */
                    *pout = GET_FCC_LABEL(dest,labels,x,y,z);
                }
                /* next pixel in the binary register pin */
                posbinx++;
            }
        }
    }
}

/****************************************
 * Tidying function                     *
 ****************************************
 * The functions tidy the label
 */

/**
 * Tidies the label.
 * \param dest the label 3D image to tidy.
 * \param lblow the lowest value allowed for label on the low byte (must be inferior to lbhigh)
 * \param lbhigh the first high value NOT allowed for label on the low byte (maximum allowed is 256)
 * \param labels the labels arrays and context
 */
static INLINE void MB3D_TidyLabel(MB3D_Image *dest,
                                  PIX32 lblow, PIX32 lbhigh,
                                  MB3D_Label *labels)
{
    Uint32 x,y;
	int z;
    MB_Image *im;
    PIX32 *pout;
    
    for(z=0; z<dest->len; z++) {
        im = dest->seq[z];
        for(y=0; y<im->height; y++) {
            pout = (PIX32 *) (im->PLINES[y+MB_Y_TOP(im)] + MB_LINE_OFFSET(im));
            for(x=0; x<im->width; x++, pout++) {
                if (*pout!=0) {
                    *pout = FIND_CORRECT_LABEL(labels, *pout, lblow, lbhigh-lblow);
                }
            }
        }
    }
}

/************************************************/
/*High level function and global variables      */
/************************************************/

/**
 * Labeling the object found in src 3D image.
 *
 * \param src the binary source 3D image where the object must be labelled
 * \param dest the 32-bit 3D image where object are labelled
 * \param lblow the lowest value allowed for label on the low byte (must be inferior to lbhigh)
 * \param lbhigh the first high value NOT allowed for label on the low byte (maximum allowed is 256)
 * \param pNbobj the number of object founds
 * \param grid the grid used (either square or hexagonal)
 * \return An error code (NO_ERR if successful)
 */
MB3D_errcode MB3D_Labelb(MB3D_Image *src, MB3D_Image *dest,
                         unsigned int lblow, unsigned int lbhigh,
                         unsigned int *pNbobj,
                         enum MB3D_grid_t grid)
{
    MB3D_Label labels;
    int z;
    Uint32 full_w, full_h;
    
    /* verification over image size compatibility */
    if (!MB3D_CHECK_SIZE_2(src, dest)) {
        return ERR_BAD_SIZE;
    }
    /* Only binary images can be processed */
    /* the output is necessarly a 32-bit image */
    switch (MB3D_PROBE_PAIR(src, dest)) {
    case MB3D_PAIR_1_32:
        break;
    default:
        return ERR_BAD_DEPTH;
    }
    /* Verification over parameter given in entry*/
    if (lblow>=lbhigh) return ERR_BAD_VALUE;
    if (lbhigh>256) return ERR_BAD_VALUE;
    /* invalid grid case */
    if (grid==MB3D_INVALID_GRID)
        return ERR_BAD_PARAMETER;
    
    /* Initializing the algorithm parameters */
    labels.current = 1;
    labels.ccurrent = 0;
    labels.maxEQ = (src->seq[0]->width * src->seq[0]->height * src->len);
    labels.EQ = malloc(labels.maxEQ*sizeof(PIX32));
    labels.CEQ = malloc(labels.maxEQ*sizeof(PIX32));
    if(labels.EQ==NULL || labels.CEQ==NULL){
        /* in case allocation goes wrong */
        free(labels.EQ);
        free(labels.CEQ);
        return ERR_CANT_ALLOCATE_MEMORY;
    } 
    memset(labels.EQ, 0, labels.maxEQ*sizeof(PIX32));
    memset(labels.CEQ, 0, labels.maxEQ*sizeof(PIX32));
    
    /* the label image is reset */
    full_h = dest->seq[0]->height + Y_TOP + Y_BOTTOM;
    full_w = (dest->seq[0]->width*dest->seq[0]->depth+CHARBIT-1)/CHARBIT + X_LEFT + X_RIGHT;
    for(z=0; z<dest->len; z++) {
        memset(dest->seq[z]->PIXARRAY, 0, full_w*full_h);
    }
    
    /* Calling the corresponding function */
    switch(grid) {
        case MB3D_CUBIC_GRID:
            MB3D_cubeLabel(dest, src, &labels);
            break;
        case MB3D_FCC_GRID:
            MB3D_fccLabel(dest, src, &labels);
            break;
        default:
            free(labels.EQ);
            free(labels.CEQ);
            return ERR_BAD_PARAMETER;
            break;
    }
    MB3D_TidyLabel(dest, (PIX32) lblow, (PIX32) lbhigh, &labels);
    
    *pNbobj = (int) (labels.ccurrent);
    
    /* freeing the labels arrays */
    free(labels.EQ);
    free(labels.CEQ);

    return NO_ERR;
}

