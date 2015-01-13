/**
 * \file MB_HierarBld.c
 * \author Nicolas Beucher
 * \date 19-08-2010
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

/** typedef for the definition of neighbor function arguments */
typedef void (TSWITCHEP) (void *ctx, int x, int y);

/** Structure holding the function contextual information 
 * such as the size of the processed image, the pointer to the pixel lines,
 * the array of tokens and the current flooding level
 */
typedef struct {
    /** The width of the processed images */
    Uint32 width;
    /** The height of the processed images */
    Uint32 height;
    
    /** The memory used to hold the elements of the hierarchical list */
    MB_Token *TokensArray;
    /** The hierarchical list entries for watershed segmentation */
    MB_ListControl HierarchicalList[256];
    /** The memory to hold the status of each pixel */
    Uint32 *pix_status;
    
    /** pointer to the lines of the mask image */
    PLINE *plines_mask;
    /** offset in the mask image lines */
    Uint32 linoff_mask;
    /** pointer to the line of the source/destination image */
    PLINE *plines_srcdest;
    /** offset in the source/destination image lines */
    Uint32 linoff_srcdest;
    /** size in byte of the image lines */
    Uint32 bytes;
    
    /** Variable indicating which level in the hierarchical list
     * the "water" as attained. Only this level and above can be filled with new
     * tokens.
     */
    PIX8 current_water_level;
    
    /** meta function which redirects the neighbor function according to the grid */
    TSWITCHEP *InsertNeighbors;
} MB_Hierarbld_Ctx;

/****************************************
 * Hierarchical list functions          *
 ****************************************/

/**
 * Inserts a token in the hierarchical list
 * This function only uses the tokens of the first half (for initialization)
 * \param local_ctx pointer to the structure holding all the information needed 
 * by the algorithm
 * \param x the position in x of the concerned pixel
 * \param y the position in y of the concerned pixel
 * \param bytes number of bytes inside the line
 */
static INLINE void MB_InsertInHierarchicalList_1(MB_Hierarbld_Ctx *local_ctx, int x, int y, PIX8 value)
{
    int position;
    int lposition;
    int lx, ly;
    
    /* the token corresponding to the pixel process is */
    /* updated/created. */
    position = x + y*local_ctx->width;
    local_ctx->TokensArray[position].nextx = MB_LIST_END;
    local_ctx->TokensArray[position].nexty = MB_LIST_END;
    
    /* insertion in the hierarchical list */
    /* the token is inserted after the last value in the list */
    lx = local_ctx->HierarchicalList[value].lastx;
    ly = local_ctx->HierarchicalList[value].lasty;
    lposition = lx+ly*local_ctx->width;
    if (lposition>=0) {
        /*There is a last value, the list is not empty*/
        local_ctx->TokensArray[lposition].nextx = x;
        local_ctx->TokensArray[lposition].nexty = y;
        local_ctx->HierarchicalList[value].lastx = x;
        local_ctx->HierarchicalList[value].lasty = y;
    }
    else {
        /* The list is empty, so we create it.*/
        local_ctx->HierarchicalList[value].firstx = x;
        local_ctx->HierarchicalList[value].firsty = y;
        local_ctx->HierarchicalList[value].lastx = x;
        local_ctx->HierarchicalList[value].lasty = y;
    }
}

/**
 * Inserts a token in the hierarchical list
 * This function only uses the tokens of the second half (for flooding).
 * The function also changes the status of the pixel to QUEUED.
 * \param local_ctx pointer to the structure holding all the information needed 
 * by the algorithm
 * \param x the position in x of the concerned pixel
 * \param y the position in y of the concerned pixel
 * \param bytes number of bytes inside the line
 */
static INLINE void MB_InsertInHierarchicalList_2(MB_Hierarbld_Ctx *local_ctx, int x, int y, PIX8 value)
{
    int position;
    int lposition;
    int lx, ly;
    
    /* the token corresponding to the pixel process is */
    /* updated/created. */
    /* the y is increased by local_ctx->height to make sure the second half */
    /* of the token is used */
    position = x + (y+local_ctx->height)*local_ctx->width;
    local_ctx->TokensArray[position].nextx = MB_LIST_END;
    local_ctx->TokensArray[position].nexty = MB_LIST_END;
    
    /* insertion in the hierarchical list */
    /* the token is inserted after the last value in the list */
    lx = local_ctx->HierarchicalList[value].lastx;
    ly = local_ctx->HierarchicalList[value].lasty;
    lposition = lx+ly*local_ctx->width;
    if (lposition>=0) {
        /*There is a last value, the list is not empty*/
        local_ctx->TokensArray[lposition].nextx = x;
        local_ctx->TokensArray[lposition].nexty = y+local_ctx->height;
        local_ctx->HierarchicalList[value].lastx = x;
        local_ctx->HierarchicalList[value].lasty = y+local_ctx->height;
    }
    else {
        /* The list is empty, so we create it.*/
        local_ctx->HierarchicalList[value].firstx = x;
        local_ctx->HierarchicalList[value].firsty = y+local_ctx->height;
        local_ctx->HierarchicalList[value].lastx = x;
        local_ctx->HierarchicalList[value].lasty = y+local_ctx->height;
    }
    
    /* change the pixel status */
    local_ctx->pix_status[x+ y*local_ctx->width] = 0x1;
}

/**
 * Initializes the hierarchical list with the marker image
 * \param local_ctx pointer to the structure holding all the information needed 
 * by the algorithm
 */
static INLINE void MB_HierarchyInit(MB_Hierarbld_Ctx *local_ctx)
{
    Uint32 i,j;
    PLINE pvalue, pmask;
    
    /*All the control are reset */
    for(i=0;i<256;i++) {
        local_ctx->HierarchicalList[i].firstx = local_ctx->HierarchicalList[i].lastx = MB_LIST_END;
        local_ctx->HierarchicalList[i].firsty = local_ctx->HierarchicalList[i].lasty = MB_LIST_END;
    }
     
    /* All the pixels are inserted inside the hierarchical list */
    local_ctx->current_water_level = 255;
    for(i=0; i<local_ctx->height; i++) {
        pvalue = (PLINE) (local_ctx->plines_srcdest[i] + local_ctx->linoff_srcdest);
        pmask = (PLINE) (local_ctx->plines_mask[i] + local_ctx->linoff_mask);
        for(j=0; j<local_ctx->bytes; j++, pvalue++, pmask++) {
            *pvalue = *pvalue<*pmask ? *pvalue : *pmask;
            MB_InsertInHierarchicalList_1(local_ctx,j,i,*pvalue);
        }
    }

    /* All pixels status are set to 0 (CANDIDATE) */
    MB_memset(local_ctx->pix_status, 0, local_ctx->width*local_ctx->height*sizeof(Uint32));
    
}

/****************************************
 * Neighbor functions                   *
 ****************************************/

/**
 * Inserts the neighbors of pixel (x,y) in the hierarchical list so that they
 * can be flooded when the water reaches their level (SQUARE GRID).
 * \param ctx pointer to the structure holding all the information needed 
 * by the algorithm
 * \param x the x position of the processed pixel 
 * \param y the x position of the processed pixel 
 */
static void MB_InsertNeighbors_square(void *ctx, int x, int y)
{
    Uint32 i;
    PIX8 value, *p, pmask;
    int nbx,nby;
    MB_Hierarbld_Ctx *local_ctx = (MB_Hierarbld_Ctx *) ctx;
    
    /* the pixel is processed only if it has not been already processed */
    if (local_ctx->pix_status[x+ y*local_ctx->width] != 0xff) {
        /* the value of the pixel in the rebuild image */
        value = *(local_ctx->plines_srcdest[y] + local_ctx->linoff_srcdest + x);
        /* pixel status is now FINAL */
        local_ctx->pix_status[x+ y*local_ctx->width] = 0xff;
        
        /* For the 8 neighbors of the pixel */
        for(i=1; i<9; i++) {
            /* position */
            nbx = x+sqNbDir[i][0];
            nby = y+sqNbDir[i][1];
            
            /* The neighbor must be in the image */
            if (nbx>=0 && nbx<((int) local_ctx->width) && nby>=0 && nby<((int) local_ctx->height)) {
                if (local_ctx->pix_status[nbx+ nby*local_ctx->width] == 0) {
                    /* if the neighbor status is CANDIDATE */
                    /* we modified its value with the minimum between the value of the */
                    /* mask at its position and the value of the pixel currently processed */
                    pmask = *(local_ctx->plines_mask[nby] + local_ctx->linoff_mask + nbx);
                    p = (local_ctx->plines_srcdest[nby] + local_ctx->linoff_srcdest + nbx);
                    *p = value<pmask ? value : pmask;
                    MB_InsertInHierarchicalList_2(local_ctx, nbx, nby, *p);
                }
            }
        }
    }
}

/**
 * Inserts the neighbors of pixel (x,y) in the hierarchical list so that they
 * can be flooded when the water reaches their level (HEXAGONAL GRID).
 * \param ctx pointer to the structure holding all the information needed 
 * by the algorithm
 * \param x the x position of the processed pixel 
 * \param y the x position of the processed pixel 
 */
static void MB_InsertNeighbors_hexagonal(void *ctx, int x, int y)
{
    Uint32 i;
    PIX8 value, *p, pmask;
    int nbx,nby;
    MB_Hierarbld_Ctx *local_ctx = (MB_Hierarbld_Ctx *) ctx;
    
    /* the pixel is processed only if it has not been already processed */
    if (local_ctx->pix_status[x+ y*local_ctx->width] != 0xff) {
        /* the value of the pixel in the rebuild image */
        value = *(local_ctx->plines_srcdest[y] + local_ctx->linoff_srcdest + x);
        /* pixel status is now FINAL */
        local_ctx->pix_status[x+ y*local_ctx->width] = 0xff;
        
        /* For the 6 neighbors of the pixel */
        for(i=1; i<7; i++) {
            /* position */
            nbx = x+hxNbDir[y%2][i][0];
            nby = y+hxNbDir[y%2][i][1];
            
            /* The neighbor must be in the image */
            if (nbx>=0 && nbx<((int) local_ctx->width) && nby>=0 && nby<((int) local_ctx->height)) {
                if (local_ctx->pix_status[nbx+ nby*local_ctx->width] == 0) {
                    /* if the neighbor status is CANDIDATE */
                    /* we modified its value with the minimum between the value of the */
                    /* mask at its position and the value of the pixel currently processed */
                    pmask = *(local_ctx->plines_mask[nby] + local_ctx->linoff_mask + nbx);
                    p = (local_ctx->plines_srcdest[nby] + local_ctx->linoff_srcdest + nbx);
                    *p = value<pmask ? value : pmask;
                    MB_InsertInHierarchicalList_2(local_ctx, nbx, nby, *p);
                }
            }
        }
    }
}

/****************************************
 * Flooding function                    *
 ****************************************/
 
/**
 * Simulates the flooding process using the hierarchical list. Tokens are
 * extracted out of the current water level list and processed. The process consists
 * in inserting in the list all its neighbor that are not already processed.
 * \param local_ctx pointer to the structure holding all the information needed 
 * by the algorithm
 */
static INLINE void MB_Flooding(MB_Hierarbld_Ctx *local_ctx)
{
    int fx,fy,pos;
    Uint32 i;
    
    for(i=0; i<256; i++, local_ctx->current_water_level = 255-i) {
        fx = local_ctx->HierarchicalList[local_ctx->current_water_level].firstx;
        fy = local_ctx->HierarchicalList[local_ctx->current_water_level].firsty;
        while(fx>=0) {
            pos = fx+fy*local_ctx->width;
            local_ctx->InsertNeighbors(local_ctx,fx,fy%(local_ctx->height));
            fx = local_ctx->TokensArray[pos].nextx;
            fy = local_ctx->TokensArray[pos].nexty;
        }
    }
}

/************************************************/
/*High level function and global variables      */
/************************************************/

/**
 * (re)Builds an image according to a mask image and using a hierarchical list
 * to compute the rebuild.
 *
 * \param mask the mask image
 * \param srcdest the rebuild image
 * \param grid the grid used (either square or hexagonal)
 *
 * \return An error code (NO_ERR if successful)
 */
MB_errcode MB_HierarBld(MB_Image *mask, MB_Image *srcdest, enum MB_grid_t grid) {
    MB_Hierarbld_Ctx local_ctx;
    
    /* verification over depth and size */
    if (!MB_CHECK_SIZE_2(srcdest, mask)) {
        return ERR_BAD_SIZE;
    }

    /* Only grey scale can be rebuild */
    switch (MB_PROBE_PAIR(srcdest, mask)) {
    case MB_PAIR_8_8:
        break;
    default:
        return ERR_BAD_DEPTH;
    }
    
    /* local context initialisation */
    local_ctx.width = srcdest->width;
    local_ctx.height = srcdest->height;

    /* setting up pointers */
    local_ctx.plines_srcdest = &srcdest->PLINES[MB_Y_TOP(srcdest)];
    local_ctx.plines_mask = &mask->PLINES[MB_Y_TOP(mask)];
    local_ctx.linoff_srcdest = MB_LINE_OFFSET(srcdest);
    local_ctx.linoff_mask = MB_LINE_OFFSET(mask);
    local_ctx.bytes = MB_LINE_COUNT(mask);
    
    /* Allocating the token array */
    /* We need two token per pixel for this algorithm */
    /* the init will use the first half and the flooding the other */
    local_ctx.TokensArray = MB_malloc(2*srcdest->width*srcdest->height*sizeof(MB_Token));
    if(local_ctx.TokensArray==NULL){
        /* in case allocation goes wrong */
        return ERR_CANT_ALLOCATE_MEMORY;
    }
    /* Allocating the pixel status array */
    local_ctx.pix_status = MB_malloc(srcdest->width*srcdest->height*sizeof(Uint32));
    if(local_ctx.pix_status==NULL){
        /* in case allocation goes wrong */
        return ERR_CANT_ALLOCATE_MEMORY;
    }
    
    /* grid initialisation */
    if (grid==MB_SQUARE_GRID) {
         local_ctx.InsertNeighbors = MB_InsertNeighbors_square;
     } else {
         local_ctx.InsertNeighbors = MB_InsertNeighbors_hexagonal;
    }

    /* Initialisation */
    MB_HierarchyInit(&local_ctx);
    
    /* Actual flooding */
    MB_Flooding(&local_ctx);
    
    /* freeing the token array */
    MB_free(local_ctx.TokensArray);
    /* freeing the pixel status array */
    MB_free(local_ctx.pix_status);
    
    return NO_ERR;
}
