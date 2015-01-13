/**
 * \file MBRT_Display.c
 * \author Nicolas Beucher
 * \date 03-29-2009
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
#include "mambaRTApi_loc.h"

/** macro to access the red component of a pixel */
#define RED(pix)  (*(pix+2))
/** macro to access the green component of a pixel */
#define GREEN(pix)  (*(pix+1))
/** macro to access the blue component of a pixel */
#define BLUE(pix)  (*pix)

/**
 * When requested, the framerate is drawn into the screen by calling this function
 * \param wfps the desired framerate
 * \param ofps the obtained framerate
 */
static INLINE void DRAW_FPS_RATE(double ofps, double wfps)
{
    PIX8 * bufp,*pixels;
    int val;
    SDL_Rect rect;
    Uint32 i,j;
    int allowBlackening;
    int bypp,pitch;
    
    /*Locking the screen to be able to blacken the background*/
    allowBlackening = 1;
    if(SDL_MUSTLOCK(context->screen)) {
        if(SDL_LockSurface(context->screen)<0) {
            allowBlackening = 0;
        }
    }
    
    pixels = ((PIX8 *)context->screen->pixels);
    pitch = context->screen->pitch;
    bypp = context->screen->format->BytesPerPixel;
    for(j=(context->sz_y-12-FPS_THICKNESS); allowBlackening && j<context->sz_y; j++) {
        for(i=0; i<context->sz_x; i++) {
            bufp = pixels + j*pitch + i*bypp;
            val = ((int) *bufp) - HISTO_BLACKENING;
            *bufp = val<0 ? 0 :(PIX8) val;
            bufp++;
            val = ((int) *bufp) - HISTO_BLACKENING;
            *bufp = val<0 ? 0 :(PIX8) val;
            bufp++;
            val = ((int) *bufp) - HISTO_BLACKENING;
            *bufp = val<0 ? 0 :(PIX8) val;
        }
    }
    if(SDL_MUSTLOCK(context->screen)) {
        SDL_UnlockSurface(context->screen);
    }
    
    /* drawing the FPS bar */
    rect.x = 7;
    rect.y = context->sz_y-7;
    rect.w = context->sz_x/2+4;
    rect.h = 1;
    SDL_FillRect(context->screen, &rect, FRAME_COLOR);
    rect.y -= (FPS_THICKNESS+3);
    SDL_FillRect(context->screen, &rect, FRAME_COLOR);
    rect.w = 1;
    rect.h = FPS_THICKNESS+4;
    SDL_FillRect(context->screen, &rect, FRAME_COLOR);
    rect.x = context->sz_x/2+10;
    SDL_FillRect(context->screen, &rect, FRAME_COLOR);
    rect.x = 9;
    rect.y = context->sz_y-FPS_THICKNESS-8;
    rect.h = FPS_THICKNESS;
    rect.w = (int) ((context->sz_x/2*(ofps))/wfps);
    rect.w = rect.w>context->sz_x/2 ? context->sz_x/2:rect.w;
    SDL_FillRect(context->screen, &rect, FPS_VALUE_COLOR);
}

/**
 * When resquested, this function draws the image histogram on display
 */
static INLINE void DRAW_HISTO()
{
    PIX8 * bufp,*pixels;
    int val;
    Uint32 i,j,h;
    int allowBlackening, ybegin;
    SDL_Rect rect;
    Uint32 max_histo = 0;
    int bypp,pitch;
    
    /* looking for histo max */
    for(i=0; i<256; i++) {
        if (context->histo[i]>max_histo)
            max_histo = context->histo[i];
    }
    
    /*Locking the screen to be able to blacken the background*/
    allowBlackening = 1;
    ybegin = context->sz_y-13-FPS_THICKNESS;
    h = (context->sz_y/2);
    if(SDL_MUSTLOCK(context->screen)) {
        if(SDL_LockSurface(context->screen)<0) {
            allowBlackening = 0;
        }
    }
    
    pixels = ((PIX8 *)context->screen->pixels);
    pitch = context->screen->pitch;
    bypp = context->screen->format->BytesPerPixel;
    for(j=0; allowBlackening && j<(h+2); j++) {
        for(i=0; i<258; i++) {
            bufp = pixels + (ybegin-1-j)*pitch + (i + 8)*bypp;
            val = ((int) *bufp) - HISTO_BLACKENING;
            *bufp = val<0 ? 0 :(PIX8) val;
            bufp++;
            val = ((int) *bufp) - HISTO_BLACKENING;
            *bufp = val<0 ? 0 :(PIX8) val;
            bufp++;
            val = ((int) *bufp) - HISTO_BLACKENING;
            *bufp = val<0 ? 0 :(PIX8) val;
        }
    }
    if(SDL_MUSTLOCK(context->screen)) {
        SDL_UnlockSurface(context->screen);
    }
    
    /* drawing the frame */
    rect.w = 1;
    rect.x = 7;
    rect.h = h+4;
    rect.y = ybegin-(h+3);
    SDL_FillRect(context->screen, &rect, FRAME_COLOR);
    rect.x = 266;
    SDL_FillRect(context->screen, &rect, FRAME_COLOR);
    rect.x = 7;
    rect.y = ybegin-(h+3);
    rect.w = 260;
    rect.h = 1;
    SDL_FillRect(context->screen, &rect, FRAME_COLOR);
    rect.y = ybegin;
    SDL_FillRect(context->screen, &rect, FRAME_COLOR);
    
    /* drawing histo */
    for(i=0; i<256; i++) {
        rect.w = 1;
        rect.x = 9+i;
        rect.h = ( h*context->histo[i] )/max_histo;
        rect.y = ybegin-1-rect.h;
        SDL_FillRect(context->screen, &rect, HISTO_COLOR);
    }
}

/**
 * Displays a small square indicating the recording is going on
 * The square is blinking on screen
 */
static INLINE void DRAW_RECORD()
{
    SDL_Rect rect;
    
    /* blinking at 2hz */
    /* this is ensured by looking at the call timestamp */
    if ((context->old_call[context->index_fps]/500)%2==0) {
    
        /* drawing the rectangle */
        rect.w = REC_SIZE;
        rect.h = 1;
        rect.x = (context->sz_x)-2*REC_SIZE;
        rect.y = REC_SIZE;
        SDL_FillRect(context->screen, &rect, REC_COLOR);
        rect.w = 1;
        rect.h = REC_SIZE;
        rect.x = (context->sz_x)-2*REC_SIZE;
        rect.y = REC_SIZE;
        SDL_FillRect(context->screen, &rect, REC_COLOR);
        rect.w = REC_SIZE;
        rect.h = 1;
        rect.x = (context->sz_x)-2*REC_SIZE;
        rect.y = 2*REC_SIZE-1;
        SDL_FillRect(context->screen, &rect, REC_COLOR);
        rect.w = 1;
        rect.h = REC_SIZE;
        rect.x = (context->sz_x)-REC_SIZE-1;
        rect.y = REC_SIZE;
        SDL_FillRect(context->screen, &rect, REC_COLOR);
        
        rect.w = REC_SIZE-4;
        rect.h = REC_SIZE-4;
        rect.x = (context->sz_x)-2*REC_SIZE+2;
        rect.y = REC_SIZE+2;
        SDL_FillRect(context->screen, &rect, REC_COLOR);
    }
}

/**
 * Creates the SDL screen display (also use to toggle fullscreen).
 */ 
static INLINE void CREATE_SCREEN()
{
    Uint32 flags;
    
    flags = SDL_HWSURFACE|SDL_DOUBLEBUF;
    if (context->isFullscreen==1) {
        flags |= SDL_FULLSCREEN;
        /* the cursor is disabled in fullscreen */
        SDL_ShowCursor(SDL_DISABLE);
    } else {
        SDL_ShowCursor(SDL_ENABLE);
    }
    
    if (context->screen) {
        SDL_FreeSurface(context->screen);
    }
    
    context->screen = SDL_SetVideoMode(context->sz_x, context->sz_y, 24, flags);
}

/**
 * Initializes SDL and creates the video display (SDL screen)
 * \param width width of the display
 * \param height height of the display
 * \return An error code (NO_ERR if successful)
 */
MBRT_errcode MBRT_CreateDisplay(int width, int height)
{
    int i;
    Uint32 bpp_supported, call;
    
    /* Verification over context */
    if (context==NULL) return ERR_INVD_CTX;
    
    /* Initialization of SDL video part */
    if (SDL_Init (SDL_INIT_VIDEO) < 0)
    {
        /*failure*/
        return ERR_INIT_DISPLAY;
    }
    
    /* SDL_Quit must be called when the program exits */
    atexit(SDL_Quit);
    
    /* supported format verification */
    bpp_supported = SDL_VideoModeOK(width, height, 24, SDL_HWSURFACE|SDL_DOUBLEBUF);
    if (bpp_supported<24) {
        /* format unsupported */
        return ERR_FORMAT_DISPLAY;
    }
    
    /* verification for fullscreen mode */
    bpp_supported = SDL_VideoModeOK(width, height, 24, SDL_HWSURFACE|SDL_DOUBLEBUF|SDL_FULLSCREEN);
    if (bpp_supported!=24) {
        /* supported ! screen is not fullscreen at the beginning */
        context->isFullscreen = 0;
    } else {
        /* Unsupported ! the fullscreen indicator is set to a value */
        /* that will prevent the fullscreen to be toggled on */
        context->isFullscreen = 2;
    }
    
    /* screen size */
    context->sz_x = width;
    context->sz_y = height;
    
    /* the original palette is set to grey level */
    for(i=0;i<256;i++) {
        context->standard_palette[i].r=i;
        context->standard_palette[i].g=i;
        context->standard_palette[i].b=i;
        context->color_palette[i].r = i;
        context->color_palette[i].g = i;
        context->color_palette[i].b = i;
    }
    context->isPalettized = 0;

    /*SDL_screen init*/
    context->screen=NULL;
    CREATE_SCREEN();
    if (context->screen==NULL) {
       /* no screen created */
       return ERR_INIT_DISPLAY;
    }
    SDL_WM_SetCaption(MBRT_TITLE, NULL);
    
    /* framerate information update */
    call = SDL_GetTicks();
    context->isFpsDisplayed = 0;
    for(context->index_fps=0; context->index_fps<FPS_MEAN_SIZE; context->index_fps++) {
        context->old_call[context->index_fps]=call;
    }
    
    /* framerate information update */
    context->isHistoDisplayed = 0;
    
    return NO_ERR;
}

/**
 * Destroys the video display (SDL screen) and quit SDL
 * \return An error code (NO_ERR if successful)
 */
MBRT_errcode MBRT_DestroyDisplay()
{
    if ((context!=NULL) && (context->screen!=NULL)) {
        SDL_FreeSurface(context->screen);
        context->screen = NULL;
    }
    SDL_Quit();
    
    return NO_ERR;
}

/**
 * Updates the display with the content of a given Mamba image structure
 * \param src the image displayed
 * \param wfps input the desired framerate
 * \param ofps output the framerate
 * \return An error code (NO_ERR if successful)
 */
MBRT_errcode MBRT_UpdateDisplay(MB_Image *src, double wfps, double *ofps)
{
    PIX8 *bufp, *pixels, pix;
    Uint32 i,j;
    Uint32 current_call;
    int bypp,pitch;
    SDL_Color *palette;
    
    /* Verification over context */
    if (context==NULL) return ERR_INVD_CTX;
    /* verification over display */
    if (context->screen==NULL) return ERR_INVALID_DISPLAY;
    
    /* only 8-bit images can be displayed*/
    if (src->depth!=8) {
        return ERR_DEPTH;
    }
    
    /* image must have the correct size */
    if ((src->width!=context->sz_x) || (src->height!=context->sz_y)) {
        return ERR_SIZE;
    }
    
    /* color palette */
    if (context->isPalettized) {
        palette = context->color_palette;
    } else {
        palette = context->standard_palette;
    }
    
    /* reset of the histogram */
    if (context->isHistoDisplayed)
        memset(context->histo, 0, 256*sizeof(Uint32));
    
    /*Locking the screen to be able to draw in it */
    if(SDL_MUSTLOCK(context->screen)) {
        if(SDL_LockSurface(context->screen)<0) {
            return ERR_LOCK_DISPLAY;
        }
    }
    
    pixels = ((PIX8 *)context->screen->pixels);
    pitch = context->screen->pitch;
    bypp = context->screen->format->BytesPerPixel;
    for(j=0; j<context->sz_y; j++) {
        for(i=0; i<context->sz_x; i++) {
            bufp = pixels + j*pitch + i*bypp;
            pix = *(src->PLINES[j+Y_TOP]+X_LEFT+i);
            RED(bufp) = palette[pix].r;
            GREEN(bufp) = palette[pix].g;
            BLUE(bufp) = palette[pix].b;
            if (context->isHistoDisplayed)
                context->histo[pix]++;
        }
    }
    
    /* icon display */
    for(i=0; i<16; i++) {
        for(j=0; j<16; j++) {
            if (context->icon[i+16*j]!=0) {
                bufp = pixels + (REC_SIZE+j)*pitch + (REC_SIZE+i)*bypp;
                RED(bufp) = (PIX8) ((FRAME_COLOR>>16)&0xFF);
                GREEN(bufp) = (PIX8) ((FRAME_COLOR>>8)&0xFF);
                BLUE(bufp) = (PIX8) ((FRAME_COLOR)&0xFF);
            }
        }
    }

    if(SDL_MUSTLOCK(context->screen)) {
        SDL_UnlockSurface(context->screen);
    }
    
    /* timestamp recording (used for video recording, blinking, and framerate computation */
    current_call = SDL_GetTicks();
    context->index_fps = (context->index_fps+1)%FPS_MEAN_SIZE;
    context->old_call[context->index_fps]=current_call;
    /* framerate computation averaged over FPS_MEAN_SIZE samples */
    *ofps = (FPS_MEAN_SIZE*1000.0)/((double) (current_call - context->old_call[(context->index_fps+1)%FPS_MEAN_SIZE]));
    
    /* frame rate display */
    if (context->isFpsDisplayed) {
        DRAW_FPS_RATE(*ofps, wfps);
    }
    /* histogram display */
    if (context->isHistoDisplayed) {
        DRAW_HISTO();
    }
    /* recording display */
    if (context->isRecording) {
        DRAW_RECORD();
    }

    SDL_Flip(context->screen);
    return NO_ERR;
}

/**
 * Updates the display with the content of a given Mamba image structure
 * \param srcRed image displayed red channel
 * \param srcGreen image displayed green channel
 * \param srcBlue image displayed blue channel
 * \param wfps input the desired framerate
 * \param ofps output the framerate
 * \return An error code (NO_ERR if successful)
 */
MBRT_errcode MBRT_UpdateDisplayColor(MB_Image *srcRed, MB_Image *srcGreen, MB_Image *srcBlue,
                                     double wfps, double *ofps)
{
    PIX8 *bufp, *pixels;
    Uint32 i,j;
    Uint32 current_call;
    int bypp,pitch;
    
    /* Verification over context */
    if (context==NULL) return ERR_INVD_CTX;
    /* verification over display */
    if (context->screen==NULL) return ERR_INVALID_DISPLAY;
    
    /* only 8-bit images can be displayed*/
    if ( (srcRed->depth!=8) ||
         (srcBlue->depth!=8) ||
         (srcGreen->depth!=8) ) {
        return ERR_DEPTH;
    }
    
    /* histogram cannot be compute with color images */
    context->isHistoDisplayed = 0;
    
    /* image must have the correct size */
    if ((srcRed->width!=context->sz_x) || (srcRed->height!=context->sz_y) ||
        (srcBlue->width!=context->sz_x) || (srcBlue->height!=context->sz_y) ||
        (srcGreen->width!=context->sz_x) || (srcGreen->height!=context->sz_y)) {
        return ERR_SIZE;
    }
    
    /*Locking the screen to be able to draw in it */
    if(SDL_MUSTLOCK(context->screen)) {
        if(SDL_LockSurface(context->screen)<0) {
            return ERR_LOCK_DISPLAY;
        }
    }
    
    pixels = ((PIX8 *)context->screen->pixels);
    pitch = context->screen->pitch;
    bypp = context->screen->format->BytesPerPixel;
    for(j=0; j<context->sz_y; j++) {
        for(i=0; i<context->sz_x; i++) {
            bufp = pixels + j*pitch + i*bypp;
            RED(bufp) = *(srcRed->PLINES[j+Y_TOP]+X_LEFT+i);
            GREEN(bufp) = *(srcGreen->PLINES[j+Y_TOP]+X_LEFT+i);
            BLUE(bufp) = *(srcBlue->PLINES[j+Y_TOP]+X_LEFT+i);
        }
    }
    
    /* icon display */
    for(i=0; i<16; i++) {
        for(j=0; j<16; j++) {
            if (context->icon[i+16*j]!=0) {
                bufp = pixels + (REC_SIZE+j)*pitch + (REC_SIZE+i)*bypp;
                RED(bufp) = (PIX8) ((FRAME_COLOR>>16)&0xFF);
                GREEN(bufp) = (PIX8) ((FRAME_COLOR>>8)&0xFF);
                BLUE(bufp) = (PIX8) ((FRAME_COLOR)&0xFF);
            }
        }
    }

    if(SDL_MUSTLOCK(context->screen)) {
        SDL_UnlockSurface(context->screen);
    }
    
    /* timestamp recording (used for video recording, blinking, and framerate computation */
    current_call = SDL_GetTicks();
    context->index_fps = (context->index_fps+1)%FPS_MEAN_SIZE;
    context->old_call[context->index_fps]=current_call;
    /* framerate computation averaged over FPS_MEAN_SIZE samples */
    *ofps = (FPS_MEAN_SIZE*1000.0)/((double) (current_call - context->old_call[(context->index_fps+1)%FPS_MEAN_SIZE]));
    
    /* frame rate display */
    if (context->isFpsDisplayed) {
        DRAW_FPS_RATE(*ofps, wfps);
    }
    /* recording display */
    if (context->isRecording) {
        DRAW_RECORD();
    }

    SDL_Flip(context->screen);
    return NO_ERR;
}

/**
 * Changes the small (16x16) icon (black and white) in the upper left corner of 
 * the display. This allows to inform the user of some events. The icon is an 
 * array of 256 integers. A 0 value will means the pixel is not drawn, non 0
 * are drawn using the OSD color.
 * \param icon the 16x16 icon pixels array
 * \return An error code (NO_ERR if successful)
 */
MBRT_errcode MBRT_IconDisplay(Uint8 *icon)
{
    
    /* Verification over context */
    if (context==NULL) return ERR_INVD_CTX;
    /* verification over display */
    if (context->screen==NULL) return ERR_INVALID_DISPLAY;
    
    memcpy(context->icon, icon, 256);
    
    return NO_ERR;
}

/**
 * Changes the palette associated with the display
 * \param palette an array containing the complete palette definition (256*3 
 * integers)
 * \return An error code (NO_ERR if successful)
 */
MBRT_errcode MBRT_PaletteDisplay(Uint8 *palette)
{
    int i;
    
    /* Verification over context */
    if (context==NULL) return ERR_INVD_CTX;
    /* verification over display */
    if (context->screen==NULL) return ERR_INVALID_DISPLAY;

    for(i=0;i<256;i++) {
        context->color_palette[i].r = *palette++;
        context->color_palette[i].g = *palette++;
        context->color_palette[i].b = *palette++;
    }
    context->isPalettized = 1;
    
    return NO_ERR;
}

/**
 * Handles event that have occurred in the display
 * \param event_code an integer representing a specific event (output)
 * \return An error code (NO_ERR if successful)
 */
MBRT_errcode MBRT_PollDisplay(MBRT_eventcode *event_code)
{
    SDL_Event event;
    
    /* Normally no events */
    *event_code = NO_EVENT;
    
    /* Verification over context */
    if (context==NULL) return ERR_INVD_CTX;
    /* verification over display */
    if (context->screen==NULL) return ERR_INVALID_DISPLAY;
   
    /* Looking for pending events and handling them */
    while ( SDL_PollEvent(&event) ) {
        switch (event.type) {
            case SDL_QUIT:
                *event_code = EVENT_CLOSE;
                break;
            case SDL_KEYDOWN:
                switch(event.key.keysym.sym) {
                case SDLK_ESCAPE:
                    if (context->isFullscreen==1) {
                        /* in fullscreen mode, the escape is used to exit the */
                        /* fullscreen (too obvious way to move out of the */
                        /* fullscreen that it may cause troubles if the result */
                        /* is to close the complete operation */
                        context->isFullscreen = 0;
                        CREATE_SCREEN();
                    } else {
                        /* in the other case, the realtime process is closed */
                        *event_code = EVENT_CLOSE;
                    }
                    break;
                case SDLK_PAUSE:
                    /* produce a pause event */
                    *event_code = EVENT_PAUSE;
                    break;
                case SDLK_f:
                    /* toggle fullscreen */
                    context->isFullscreen = (1-context->isFullscreen);
                    CREATE_SCREEN();
                    break;
                case SDLK_p:
                    /* toggle the palette */
                    if (context->isPalettized) {
                        context->isPalettized = 0;
                    } else {
                        context->isPalettized = 1;
                    }
                    break;
                case SDLK_r:
                    /* toggle the framerate display */
                    context->isFpsDisplayed = (1-context->isFpsDisplayed);
                    break;
                case SDLK_h:
                    /* toggle the framerate display */
                    context->isHistoDisplayed = (1-context->isHistoDisplayed);
                    break;
                case SDLK_o:
                    /* toggle the process on or off */
                    *event_code = EVENT_PROCESS;
                    break;
                case SDLK_c:
                    /* toggles the color on or off */
                    *event_code = EVENT_COLOR;
                    break;
                default:
                    break;
                }
                break;
            default:
                break;
       }
   }

   return NO_ERR;
}
