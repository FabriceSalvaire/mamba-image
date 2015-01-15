/**
 * \file mambaApi.h
 * \date 11-4-2007
 *
 * This file contains the various definitions, global variables
 * macro, struct and functions created for the library.
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

#ifndef MB_apiH
#define MB_apiH

#ifdef __cplusplus
extern "C" {
#endif

/****************************************/
/* Includes                             */
/****************************************/
#include "mambaCommon.h"
#include "MB_error.h"

/****************************************/
/* Defines                              */
/****************************************/

/****************************************/
/* Macros                               */
/****************************************/

/****************************************/
/* Structures and Typedef               */
/****************************************/

/****************************************/
/* Global variables                     */
/****************************************/

/** image counter */
extern Uint32 MB_refcounter;

/************************************************/
/* Image Creation and Manipulation Functions    */
/************************************************/

/* Creation : memory allocation */
MB_errcode MB_Create(MB_Image *image, Uint32 width, Uint32 height, Uint32 depth);
  MB_errcode MB_Create_from_numpy8(MB_Image *image, PIX8 *pixel_array,
				   Uint32 array_height, Uint32 array_width, Uint32 width, Uint32 line_step);
MB_errcode MB_Create_from_numpy32(MB_Image *image, PIX32 *pixel_array,
				  Uint32 array_height, Uint32 array_width, Uint32 width, Uint32 line_step);
/* destruction */
MB_errcode MB_Destroy(MB_Image *image);
/* loading pixel data in a created image */
MB_errcode MB_Load(MB_Image *image, PIX8 *indata, Uint32 len);
/* extracting pixel data from an image */
MB_errcode MB_Extract(MB_Image *image, PIX8 **outdata, Uint32 *len);
/* converting an image format into another */
MB_errcode MB_Convert(MB_Image *src, MB_Image *dest);
/* copying an image into another one */
MB_errcode MB_Copy(MB_Image *src, MB_Image *dest);
/* copying a line into another one */
MB_errcode MB_CopyLine(MB_Image *src, MB_Image *dest, Uint32 insrc_pos, Uint32 indest_pos);
/* copying an image into another one with cropping */
MB_errcode MB_CropCopy(MB_Image *src, Uint32 x_src, Uint32 y_src,
                       MB_Image *dest, Uint32 x_dest, Uint32 y_dest,
                       Uint32 w, Uint32 h);
/* Pixel value manipulations */
MB_errcode MB_PutPixel(MB_Image *dest, Uint32 pixVal, Uint32 x, Uint32 y);
MB_errcode MB_GetPixel(MB_Image *src, Uint32 *pixVal, Uint32 x, Uint32 y);

/****************************************/
/* Image Processing Functions           */
/****************************************/

/* Logic AND */
MB_errcode MB_And(MB_Image *src1, MB_Image *src2, MB_Image *dest);
/* Logic OR */
MB_errcode MB_Or(MB_Image *src1, MB_Image *src2, MB_Image *dest);
/* Logic XOR */
MB_errcode MB_Xor(MB_Image *src1, MB_Image *src2, MB_Image *dest);
/* Logic NOT */
MB_errcode MB_Inv(MB_Image *src, MB_Image *dest);
/* Inferior image */
MB_errcode MB_Inf(MB_Image *src1, MB_Image *src2, MB_Image *dest);
/* Inferior per neighbor image */
MB_errcode MB_InfNbb(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, Uint32 count, enum MB_grid_t grid, enum MB_edgemode_t edge);
MB_errcode MB_InfNb8(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, Uint32 count, enum MB_grid_t grid, enum MB_edgemode_t edge);
MB_errcode MB_InfNb32(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, Uint32 count, enum MB_grid_t grid, enum MB_edgemode_t edge);
/* Inferior per far neighbor image */
MB_errcode MB_InfFarNbb(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, Uint32 count, enum MB_grid_t grid, enum MB_edgemode_t edge);
MB_errcode MB_InfFarNb8(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, Uint32 count, enum MB_grid_t grid, enum MB_edgemode_t edge);
MB_errcode MB_InfFarNb32(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, Uint32 count, enum MB_grid_t grid, enum MB_edgemode_t edge);
/* Inferior per vector */
MB_errcode MB_InfVectorb(MB_Image *src, MB_Image *srcdest, Sint32 dx, Sint32 dy, enum MB_edgemode_t edge);
MB_errcode MB_InfVector8(MB_Image *src, MB_Image *srcdest, Sint32 dx, Sint32 dy, enum MB_edgemode_t edge);
MB_errcode MB_InfVector32(MB_Image *src, MB_Image *srcdest, Sint32 dx, Sint32 dy, enum MB_edgemode_t edge);
/* Superior image */
MB_errcode MB_Sup(MB_Image *src1, MB_Image *src2, MB_Image *dest);
/* Superior per neighbor image */
MB_errcode MB_SupNbb(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, Uint32 count, enum MB_grid_t grid, enum MB_edgemode_t edge);
MB_errcode MB_SupNb8(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, Uint32 count, enum MB_grid_t grid, enum MB_edgemode_t edge);
MB_errcode MB_SupNb32(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, Uint32 count, enum MB_grid_t grid, enum MB_edgemode_t edge);
/* Superior per far neighbor image */
MB_errcode MB_SupFarNbb(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, Uint32 count, enum MB_grid_t grid, enum MB_edgemode_t edge);
MB_errcode MB_SupFarNb8(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, Uint32 count, enum MB_grid_t grid, enum MB_edgemode_t edge);
MB_errcode MB_SupFarNb32(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, Uint32 count, enum MB_grid_t grid, enum MB_edgemode_t edge);
/* Superior per vector */
MB_errcode MB_SupVectorb(MB_Image *src, MB_Image *srcdest, Sint32 dx, Sint32 dy, enum MB_edgemode_t edge);
MB_errcode MB_SupVector8(MB_Image *src, MB_Image *srcdest, Sint32 dx, Sint32 dy, enum MB_edgemode_t edge);
MB_errcode MB_SupVector32(MB_Image *src, MB_Image *srcdest, Sint32 dx, Sint32 dy, enum MB_edgemode_t edge);
/*Superior mask generator */
MB_errcode MB_SupMask(MB_Image *src1, MB_Image *src2, MB_Image *dest, Uint32 strict);
/* Adds two images */
MB_errcode MB_Add(MB_Image *src1, MB_Image *src2, MB_Image *dest);
/* Substracts two images */
MB_errcode MB_Sub(MB_Image *src1, MB_Image *src2, MB_Image *dest);
/* Multiplies two images */
MB_errcode MB_Mul(MB_Image *src1, MB_Image *src2, MB_Image *dest);
/* Shift function */
MB_errcode MB_Shiftb(MB_Image *src, MB_Image *dest, Uint32 dirnum, Uint32 count, Uint32 long_filler_pix, enum MB_grid_t grid);
MB_errcode MB_Shift8(MB_Image *src, MB_Image *dest, Uint32 dirnum, Uint32 count, Uint32 long_filler_pix, enum MB_grid_t grid);
MB_errcode MB_Shift32(MB_Image *src, MB_Image *dest, Uint32 dirnum, Uint32 count, Uint32 long_filler_pix, enum MB_grid_t grid);
/* Shift by vector */
MB_errcode MB_ShiftVectorb(MB_Image *src, MB_Image *dest, Sint32 dx, Sint32 dy, Uint32 long_filler_pix);
MB_errcode MB_ShiftVector8(MB_Image *src, MB_Image *dest, Sint32 dx, Sint32 dy, Uint32 long_filler_pix);
MB_errcode MB_ShiftVector32(MB_Image *src, MB_Image *dest, Sint32 dx, Sint32 dy, Uint32 long_filler_pix);
/* Image set difference */
MB_errcode MB_Diff(MB_Image *src1, MB_Image *src2, MB_Image *dest);
/* set Diff by neighbouring function */
MB_errcode MB_DiffNbb(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, enum MB_grid_t grid, enum MB_edgemode_t edge);
MB_errcode MB_DiffNb8(MB_Image *src, MB_Image *srcdest, Uint32 nbrnum, enum MB_grid_t grid, enum MB_edgemode_t edge);
/* constant addition to image */
MB_errcode MB_ConAdd(MB_Image *src, Sint32 value, MB_Image *dest);
/* constant substraction to image */
MB_errcode MB_ConSub(MB_Image *src, Sint32 value, MB_Image *dest);
/* constant multiplication to image */
MB_errcode MB_ConMul(MB_Image *src, Uint32 value, MB_Image *dest);
/* constant division to image */
MB_errcode MB_ConDiv(MB_Image *src, Uint32 value, MB_Image *dest);
/* filling image with value */
MB_errcode MB_ConSet(MB_Image *dest, Uint32 value);
/* Image volume computation */
MB_errcode MB_Volume(MB_Image *src, Uint64 *pVolume);
/* Image emptiness check */
MB_errcode MB_Check(MB_Image *src, Uint32 *isEmpty);
/* Lookup Table modification */
MB_errcode MB_Lookup(MB_Image *src, MB_Image *dest, Uint32 *ptab);
/* Histogram of the image */
MB_errcode MB_Histo(MB_Image *src, Uint32 *phisto);
/* Image comparaison */
MB_errcode MB_Compare(MB_Image *src, MB_Image *cmp, MB_Image *dest, Sint32 *px, Sint32 *py);
/* Threshold function */
MB_errcode MB_Thresh(MB_Image *src, MB_Image *dest, Uint32 low, Uint32 high);
/* Build by neighbouring function */
MB_errcode MB_BldNbb(MB_Image *mask, MB_Image *srcdest, Uint32 dirnum, Uint64 *pVolume, enum MB_grid_t grid);
MB_errcode MB_BldNb8(MB_Image *mask, MB_Image *srcdest, Uint32 dirnum, Uint64 *pVolume, enum MB_grid_t grid);
MB_errcode MB_BldNb32(MB_Image *mask, MB_Image *srcdest, Uint32 dirnum, Uint64 *pVolume, enum MB_grid_t grid);
/* Build by hierarchical algorithm */
MB_errcode MB_HierarBld(MB_Image *mask, MB_Image *srcdest, enum MB_grid_t grid);
/* Dual Build by neighbouring function */
MB_errcode MB_DualBldNbb(MB_Image *mask, MB_Image *srcdest, Uint32 dirnum, Uint64 *pVolume, enum MB_grid_t grid);
MB_errcode MB_DualBldNb8(MB_Image *mask, MB_Image *srcdest, Uint32 dirnum, Uint64 *pVolume, enum MB_grid_t grid);
MB_errcode MB_DualBldNb32(MB_Image *mask, MB_Image *srcdest, Uint32 dirnum, Uint64 *pVolume, enum MB_grid_t grid);
/* Dual Build by hierarchical algorithm */
MB_errcode MB_HierarDualBld(MB_Image *mask, MB_Image *srcdest, enum MB_grid_t grid);
/* Mask function to convert binary images to grey scale image*/
MB_errcode MB_Mask(MB_Image *src, MB_Image *dest, Uint32 maskf, Uint32 maskt);
/* pixel range in an image */
MB_errcode MB_Range(MB_Image *src, Uint32 *min, Uint32 *max);
/* maximum pixel range in an image given its depth*/
MB_errcode MB_depthRange(MB_Image *src, Uint32 *min, Uint32 *max);
/* bit plane manipulations */
MB_errcode MB_CopyBitPlane(MB_Image *src, MB_Image *dest, Uint32 plane);
/* byte plane manipulations */
MB_errcode MB_CopyBytePlane(MB_Image *src, MB_Image *dest, Uint32 plane);
/* binary hit or miss */
MB_errcode MB_BinHitOrMiss(MB_Image *src, MB_Image *dest, Uint32 es0, Uint32 es1, enum MB_grid_t grid);
/* labeling binary images */
MB_errcode MB_Labelb(MB_Image *src, MB_Image *dest, Uint32 lblow, Uint32 lbhigh, Uint32 *pNbobj, enum MB_grid_t grid);
/* Compute the set edge distance distance */
MB_errcode MB_Distanceb(MB_Image *src, MB_Image *dest, enum MB_grid_t grid, enum MB_edgemode_t edge);
/* Watershed segmentation (watershed line and basins)*/
MB_errcode MB_Watershed(MB_Image *src, MB_Image *marker, Uint32 max_level, enum MB_grid_t grid);
MB_errcode MB_Basins(MB_Image *src, MB_Image *marker, Uint32 max_level, enum MB_grid_t grid);
/* Including frame computing */
MB_errcode MB_Frame(MB_Image *src, Uint32 thresval, Uint32 *ulx, Uint32 *uly, Uint32 *brx, Uint32 *bry);

#ifdef __cplusplus
}
#endif

#endif

