/**
 * \file mambaRTApi_loc.h
 * \date 03-27-2009
 *
 * This file contains the various definitions, global variables
 * macro, struct and functions that are shared between components
 * of the library but are not meant to be exported to the outside
 * world.
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
#ifndef MBRT_apilocH
#define MBRT_apilocH


/* The local header is the only header called inside each component of
 * the library, The global header is meant for the outside world.
 */
//#include <windows.h>
//#include <objbase.h>

#pragma include_alias( "dxtrans.h", "qedit.h" )
#define __IDxtCompositor_INTERFACE_DEFINED__
#define __IDxtAlphaSetter_INTERFACE_DEFINED__
#define __IDxtJpeg_INTERFACE_DEFINED__
#define __IDxtKey_INTERFACE_DEFINED__

#include <qedit.h> // Sample Grabber, Null Renderer
//
//#pragma comment (lib, "strmiids.lib")

#include "mambaRTApi.h"
#include <SDL.h> 

// FFmpeg libraries are pure C and thus must be identified as such to 
// work with visual C++ which seems to handle correctly C++ code. 
// In the case of mambaRealtime code, the C++ is a consequence of 
// directshow library. Most of the code is a ripe off mambaRealtime
// for Linux which is pure C
#ifdef __cplusplus
extern "C" {
#endif

#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libswscale/swscale.h>

#ifdef __cplusplus
}
#endif

/****************************************/
/* Defines                              */
/****************************************/

#define MBRT_TITLE "Mamba RealTime"

#define FRAME_COLOR 0xffc000

#define FPS_VALUE_COLOR 0xffc000
#define FPS_THICKNESS 3
#define FPS_MEAN_SIZE 20

#define HISTO_BLACKENING 60
#define HISTO_COLOR     0xffffff

#define REC_SIZE 16
#define REC_COLOR  0xc00000

/****************************************/
/* Macros                               */
/****************************************/
 
/****************************************/
/* Structures and Typedef               */
/****************************************/

/* device description structure */
typedef struct {
    /* directshow objects */
    IGraphBuilder         *pGraph;
    ICaptureGraphBuilder2 *pBuild;
    IBaseFilter           *pCap;
    ISampleGrabber        *pGrab;
    IMediaControl         *pCtrl;
    /* device properties */
    int devnum;
    int w,h;
    /* buffer handling for pixels */
    int size;
    void * buffer;
} MBRT_dshowvidT;

/* audio video codec API */
typedef struct {
    AVFormatContext *format_ctx;
    AVCodecContext *codec_ctx; 
    int videoStream;
    AVFrame *frame;
    AVFrame *yuvframe;
    AVFrame *rgbframe;
    AVPacket packet;
} MBRT_avcvidT;

/* union for all the possible cases for video acquisition device */
typedef union
{
    MBRT_dshowvidT dshow;
    MBRT_avcvidT avc;
} MBRT_vidUnion;

/* Realtime library context struct */
typedef struct {
    /* video device */
    MBRT_vidType type;
    int fd;
    MBRT_vidUnion video;
    /* screen */
    SDL_Surface *screen;
    /* display size*/
    Uint32 sz_x;
    Uint32 sz_y;
    /*palette*/
    SDL_Color color_palette[256];
    SDL_Color standard_palette[256];
    Uint32 isPalettized;
    /* framerate information and display */
    Uint32 isFpsDisplayed;
    Uint32 old_call[FPS_MEAN_SIZE];
    int index_fps;
    /* histogram */
    Uint32 histo[256];
    Uint32 isHistoDisplayed;
    /* icon */
    Uint8 icon[256];
    /* fullscreen */
    Sint32 isFullscreen;
    /* recording */
    Uint32 isRecording;
    AVFormatContext *rec_fmt_ctx;
    AVFrame *pictureRGB;
    AVFrame *picture;
    struct SwsContext *img_convert_ctx;
    uint8_t *video_outbuf;
    
} MBRT_Context;

/****************************************/
/* context global pointer               */
/****************************************/

/** Structure holding the complete context information (display, device, ...) */
extern MBRT_Context *context;

/****************************************/
/* video type specific functions        */
/****************************************/

/*DSHOW*/
MBRT_errcode MBRT_CreateVideoAcq_dshow(int device);
MBRT_errcode MBRT_DestroyVideoAcq_dshow(void);
MBRT_errcode MBRT_GetAcqSize_dshow(int *acq_w, int *acq_h);
MBRT_errcode MBRT_GetAcqFrameRate_dshow(double *fps);
MBRT_errcode MBRT_GetImageFromAcq_dshow(MB_Image *dest);
MBRT_errcode MBRT_GetColorImageFromAcq_dshow(MB_Image *destRed, MB_Image *destGreen, MB_Image *destBlue);
MBRT_errcode MBRT_StopAcq_dshow();
MBRT_errcode MBRT_StartAcq_dshow();
/*AVC*/
MBRT_errcode MBRT_CreateVideoAcq_avc(char *video_path);
MBRT_errcode MBRT_DestroyVideoAcq_avc(void);
MBRT_errcode MBRT_GetAcqSize_avc(int *acq_w, int *acq_h);
MBRT_errcode MBRT_GetAcqFrameRate_avc(double *fps);
MBRT_errcode MBRT_GetImageFromAcq_avc(MB_Image *dest);
MBRT_errcode MBRT_GetColorImageFromAcq_avc(MB_Image *destRed, MB_Image *destGreen, MB_Image *destBlue);
MBRT_errcode MBRT_StopAcq_avc();
MBRT_errcode MBRT_StartAcq_avc();


#endif
