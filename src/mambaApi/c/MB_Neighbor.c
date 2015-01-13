/**
 * \file MB_Neighbor.c
 * \author Nicolas Beucher
 * \date 1-5-2010
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

/* This file is used to describes the way to perform computation for each 
 * neighbor and each grid. To work they must be included inside each file 
 * performing neighbor computation operations such as :
 *    MB_DiffNb8.c
 *    MB_DiffNbb.c
 *    MB_SupNb32.c
 *    MB_SupNb8.c
 *    MB_SupNbb.c
 *    MB_InfNb32.c
 *    MB_InfNb8.c
 *    MB_InfNbb.c
 *
 * The inclusion must be done like this example for MB_DiffNb8.c :
 *    #define EDGE_TYPE Uint32
 *    #include "MB_Neighbor.c"
 *    #undef EDGE_TYPE
 * 
 * Because the function here perform shift to achieve the meighbor 
 * computations they always performed the shift in the transposed direction.
 * Indeed for neighbor 1 to face the central pixel it need to be shift in
 * direction 5 on the SQUARE grid or 4 in the HEXAGONAL grid.
 */

/****************************************
 * Neighbor functions                   *
 ****************************************
 * The functions described here shift the pixels in a given so that the 
 * pixel of the given neighbor could be juxtaposed with the central one
 */

/* SQUARE */

/**
 * Computes the result with neighbor 1 (SQUARE GRID)
 * \param plines_inout pointer on the destination image lines
 * \param off_inout offset inside the destination image lines
 * \param plines_in pointer on the source image that is shifted pixel lines
 * \param off_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param nb_lines number of lines in the image processed
 * \param count the shift amplitude
 * \param edge_val the value used to fill the edge
 */
static void MB_QCompNbr1(PLINE *plines_inout, Uint32 linoff_inout,
                         PLINE *plines_in, Uint32 linoff_in,
                         Uint32 bytes_in, Uint32 nb_lines,
                         Uint32 count, EDGE_TYPE edge_val )
{
    PLINE *p_in;
    PLINE *p_inout;

    Uint32 i;
    
    p_in = &plines_in[nb_lines-2];
    p_inout = &plines_inout[nb_lines-1];

    while(count-- > 0) {
        for(i = 1; i < nb_lines; i++, p_in--, p_inout--) {
            COMP_LINE(p_inout,linoff_inout,p_in,linoff_in,bytes_in);
        }
        COMP_EDGE_LINE(p_inout,linoff_inout,bytes_in,edge_val);
        p_in = &plines_inout[nb_lines-2];
        p_inout = &plines_inout[nb_lines-1];
    }
}

/**
 * Computes the result with neighbor 2 (SQUARE GRID)
 * \param plines_inout pointer on the destination image lines
 * \param off_inout offset inside the destination image lines
 * \param plines_in pointer on the source image that is shifted pixel lines
 * \param off_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param nb_lines number of lines in the image processed
 * \param count the shift amplitude
 * \param edge_val the value used to fill the edge
 */
static void MB_QCompNbr2(PLINE *plines_inout, Uint32 linoff_inout,
                         PLINE *plines_in, Uint32 linoff_in,
                         Uint32 bytes_in, Uint32 nb_lines,
                         Uint32 count, EDGE_TYPE edge_val )
{
    PLINE *p_in;
    PLINE *p_inout;

    Uint32 i;

    p_in = &plines_in[nb_lines-2];
    p_inout = &plines_inout[nb_lines-1];

    while(count-- > 0) {
        for(i = 1; i < nb_lines; i++, p_in--, p_inout--) {
            COMP_LINE_LEFT(p_inout,linoff_inout,p_in,linoff_in,bytes_in,edge_val);
        }
        COMP_EDGE_LINE(p_inout,linoff_inout,bytes_in,edge_val);
        p_in = &plines_inout[nb_lines-2];
        p_inout = &plines_inout[nb_lines-1];
    }
}

/**
 * Computes the result with neighbor 3 (SQUARE GRID)
 * \param plines_inout pointer on the destination image lines
 * \param off_inout offset inside the destination image lines
 * \param plines_in pointer on the source image that is shifted pixel lines
 * \param off_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param nb_lines number of lines in the image processed
 * \param count the shift amplitude
 * \param edge_val the value used to fill the edge
 */
static void MB_QCompNbr3(PLINE *plines_inout, Uint32 linoff_inout,
                         PLINE *plines_in, Uint32 linoff_in,
                         Uint32 bytes_in, Uint32 nb_lines,
                         Uint32 count, EDGE_TYPE edge_val )
{
    PLINE *p_in;
    PLINE *p_inout;

    Uint32 i;

    p_in = plines_in;
    p_inout = plines_inout;
    
    while(count-- > 0) {
        for(i = 0; i < nb_lines; i++, p_in++, p_inout++) {
              COMP_LINE_LEFT(p_inout,linoff_inout,p_in,linoff_in,bytes_in,edge_val);
        }
        p_in = plines_inout;
        p_inout = plines_inout;
    }
}

/**
 * Computes the result with neighbor 4 (SQUARE GRID)
 * \param plines_inout pointer on the destination image lines
 * \param off_inout offset inside the destination image lines
 * \param plines_in pointer on the source image that is shifted pixel lines
 * \param off_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param nb_lines number of lines in the image processed
 * \param count the shift amplitude
 * \param edge_val the value used to fill the edge
 */
static void MB_QCompNbr4(PLINE *plines_inout, Uint32 linoff_inout,
                         PLINE *plines_in, Uint32 linoff_in,
                         Uint32 bytes_in, Uint32 nb_lines,
                         Uint32 count, EDGE_TYPE edge_val )
{
    PLINE *p_in;
    PLINE *p_inout;

    Uint32 i;

    p_in = &plines_in[1];
    p_inout = plines_inout;

    while(count-- > 0) {
        for(i = 1; i < nb_lines; i++, p_in++, p_inout++) {
            COMP_LINE_LEFT(p_inout,linoff_inout,p_in,linoff_in,bytes_in,edge_val);
        }
        COMP_EDGE_LINE(p_inout,linoff_inout,bytes_in,edge_val);
        p_in = &plines_inout[1];
        p_inout = plines_inout;
    }
}

/**
 * Computes the result with neighbor 5 (SQUARE GRID)
 * \param plines_inout pointer on the destination image lines
 * \param off_inout offset inside the destination image lines
 * \param plines_in pointer on the source image that is shifted pixel lines
 * \param off_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param nb_lines number of lines in the image processed
 * \param count the shift amplitude
 * \param edge_val the value used to fill the edge
 */
static void MB_QCompNbr5(PLINE *plines_inout, Uint32 linoff_inout,
                         PLINE *plines_in, Uint32 linoff_in,
                         Uint32 bytes_in, Uint32 nb_lines,
                         Uint32 count, EDGE_TYPE edge_val )
{
    PLINE *p_in;
    PLINE *p_inout;

    Uint32 i;
    
    p_in = &plines_in[1];
    p_inout = plines_inout;

    while(count-- > 0) {
        for(i = 1; i < nb_lines; i++, p_in++, p_inout++) {
            COMP_LINE(p_inout,linoff_inout,p_in,linoff_in,bytes_in);
        }
        COMP_EDGE_LINE(p_inout,linoff_inout,bytes_in,edge_val);
        p_in = &plines_inout[1];
        p_inout = plines_inout;
    }
}

/**
 * Computes the result with neighbor 6 (SQUARE GRID)
 * \param plines_inout pointer on the destination image lines
 * \param off_inout offset inside the destination image lines
 * \param plines_in pointer on the source image that is shifted pixel lines
 * \param off_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param nb_lines number of lines in the image processed
 * \param count the shift amplitude
 * \param edge_val the value used to fill the edge
 */
static void MB_QCompNbr6(PLINE *plines_inout, Uint32 linoff_inout,
                         PLINE *plines_in, Uint32 linoff_in,
                         Uint32 bytes_in, Uint32 nb_lines,
                         Uint32 count, EDGE_TYPE edge_val )
{
    PLINE *p_in;
    PLINE *p_inout;

    Uint32 i;

    p_in = &plines_in[1];
    p_inout = plines_inout;

    while(count-- > 0) {
        for(i = 1; i < nb_lines; i++, p_in++, p_inout++) {
            COMP_LINE_RIGHT(p_inout,linoff_inout,p_in,linoff_in,bytes_in,edge_val);
        }
        COMP_EDGE_LINE(p_inout,linoff_inout,bytes_in,edge_val);
        p_in = &plines_inout[1];
        p_inout = plines_inout;
    }
}

/**
 * Computes the result with neighbor 7 (SQUARE GRID)
 * \param plines_inout pointer on the destination image lines
 * \param off_inout offset inside the destination image lines
 * \param plines_in pointer on the source image that is shifted pixel lines
 * \param off_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param nb_lines number of lines in the image processed
 * \param count the shift amplitude
 * \param edge_val the value used to fill the edge
 */
static void MB_QCompNbr7(PLINE *plines_inout, Uint32 linoff_inout,
                         PLINE *plines_in, Uint32 linoff_in,
                         Uint32 bytes_in, Uint32 nb_lines,
                         Uint32 count, EDGE_TYPE edge_val )
{
    PLINE *p_in;
    PLINE *p_inout;

    Uint32 i;

    p_in = &plines_in[nb_lines - 1];
    p_inout = &plines_inout[nb_lines-1];
    
    while(count-- > 0) {
        for( i = 0; i < nb_lines; i++, p_in--, p_inout-- ) {
              COMP_LINE_RIGHT(p_inout,linoff_inout,p_in,linoff_in,bytes_in,edge_val);
        }
        p_in = &plines_in[nb_lines-1];
        p_inout = &plines_inout[nb_lines-1];
    }
}

/**
 * Computes the result with neighbor 8 (SQUARE GRID)
 * \param plines_inout pointer on the destination image lines
 * \param off_inout offset inside the destination image lines
 * \param plines_in pointer on the source image that is shifted pixel lines
 * \param off_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param nb_lines number of lines in the image processed
 * \param count the shift amplitude
 * \param edge_val the value used to fill the edge
 */
static void MB_QCompNbr8(PLINE *plines_inout, Uint32 linoff_inout,
                         PLINE *plines_in, Uint32 linoff_in,
                         Uint32 bytes_in, Uint32 nb_lines,
                         Uint32 count, EDGE_TYPE edge_val )
{
    PLINE *p_in;
    PLINE *p_inout;

    Uint32 i;

    p_in = &plines_in[nb_lines-2];
    p_inout = &plines_inout[nb_lines-1];

    while(count-- > 0) {
        for(i = 1; i < nb_lines; i++, p_in--, p_inout--) {
            COMP_LINE_RIGHT(p_inout,linoff_inout,p_in,linoff_in,bytes_in,edge_val);
        }
        COMP_EDGE_LINE(p_inout,linoff_inout,bytes_in,edge_val);
        p_in = &plines_inout[nb_lines-2];
        p_inout = &plines_inout[nb_lines-1];
    }
}

/* HEXAGONAL
 * Remark for the hex mode: we suppose that the first line of AOI
 * is always of even parity. This means that the line 0 of the image 
 * is of even parity,
 */

/**
 * Computes the result with neighbor 1 (HEXAGONAL GRID)
 * \param plines_inout pointer on the destination image lines
 * \param off_inout offset inside the destination image lines
 * \param plines_in pointer on the source image that is shifted pixel lines
 * \param off_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param nb_lines number of lines in the image processed
 * \param count the shift amplitude
 * \param edge_val the value used to fill the edge
 */
static void MB_HCompNbr1(PLINE *plines_inout, Uint32 linoff_inout,
                         PLINE *plines_in, Uint32 linoff_in,
                         Uint32 bytes_in, Uint32 nb_lines,
                         Uint32 count, EDGE_TYPE edge_val )
{
    PLINE *p_in;
    PLINE *p_inout;

    Uint32 i;

    p_in = &plines_in[nb_lines-2];
    p_inout = &plines_inout[nb_lines-1];

    /* Note that in the cases where Y decreases (as here), we proceed from
     * bottom up, and, therefore, begin with odd line rather then the even one.
     */
    while(count-- > 0) {
        for(i = 2; i < nb_lines; i += 2) {
            COMP_LINE_LEFT(p_inout,linoff_inout,p_in,linoff_in,bytes_in,edge_val);
            p_in--, p_inout--;
            COMP_LINE(p_inout,linoff_inout,p_in,linoff_in,bytes_in);
            p_in--, p_inout--;
        }
        COMP_LINE_LEFT(p_inout,linoff_inout,p_in,linoff_in,bytes_in,edge_val);
        p_inout--;
        COMP_EDGE_LINE(p_inout,linoff_inout,bytes_in,edge_val);
        p_in = &plines_inout[nb_lines-2];
        p_inout = &plines_inout[nb_lines-1];
    }
}

/**
 * Computes the result with neighbor 3 (HEXAGONAL GRID)
 * \param plines_inout pointer on the destination image lines
 * \param off_inout offset inside the destination image lines
 * \param plines_in pointer on the source image that is shifted pixel lines
 * \param off_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param nb_lines number of lines in the image processed
 * \param count the shift amplitude
 * \param edge_val the value used to fill the edge
 */
static void MB_HCompNbr3(PLINE *plines_inout, Uint32 linoff_inout,
                         PLINE *plines_in, Uint32 linoff_in,
                         Uint32 bytes_in, Uint32 nb_lines,
                         Uint32 count, EDGE_TYPE edge_val )
{
    PLINE *p_in;
    PLINE *p_inout;

    Uint32 i;
    p_in = &plines_in[1];
    p_inout = plines_inout;

    while(count-- > 0) {
        for(i = 2; i < nb_lines; i += 2) {
            COMP_LINE(p_inout,linoff_inout,p_in,linoff_in,bytes_in);
            p_in++, p_inout++;
            COMP_LINE_LEFT(p_inout,linoff_inout,p_in,linoff_in,bytes_in,edge_val);
            p_in++, p_inout++;
        }
        COMP_LINE(p_inout,linoff_inout,p_in,linoff_in,bytes_in);
        p_inout++;
        COMP_EDGE_LINE(p_inout,linoff_inout,bytes_in,edge_val);
        p_in = &plines_inout[1];
        p_inout = plines_inout;
    }
}

/**
 * Computes the result with neighbor 4 (HEXAGONAL GRID)
 * \param plines_inout pointer on the destination image lines
 * \param off_inout offset inside the destination image lines
 * \param plines_in pointer on the source image that is shifted pixel lines
 * \param off_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param nb_lines number of lines in the image processed
 * \param count the shift amplitude
 * \param edge_val the value used to fill the edge
 */
static void MB_HCompNbr4(PLINE *plines_inout, Uint32 linoff_inout,
                         PLINE *plines_in, Uint32 linoff_in,
                         Uint32 bytes_in, Uint32 nb_lines,
                         Uint32 count, EDGE_TYPE edge_val )
{

    PLINE *p_in;
    PLINE *p_inout;

    Uint32 i;

    p_in = &plines_in[1];
    p_inout = plines_inout;

    while(count-- > 0) {
        for(i = 2; i < nb_lines; i += 2) {
            COMP_LINE_RIGHT(p_inout,linoff_inout,p_in,linoff_in,bytes_in,edge_val);
            p_in++, p_inout++;
            COMP_LINE(p_inout,linoff_inout,p_in,linoff_in,bytes_in);
            p_in++, p_inout++;
        }
        COMP_LINE_RIGHT(p_inout,linoff_inout,p_in,linoff_in,bytes_in,edge_val);
        p_inout++;
        COMP_EDGE_LINE(p_inout,linoff_inout,bytes_in,edge_val);
        p_in = &plines_in[1];
        p_inout = plines_inout;
    }
}

/**
 * Computes the result with neighbor 6 (HEXAGONAL GRID)
 * \param plines_inout pointer on the destination image lines
 * \param off_inout offset inside the destination image lines
 * \param plines_in pointer on the source image that is shifted pixel lines
 * \param off_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param nb_lines number of lines in the image processed
 * \param count the shift amplitude
 * \param edge_val the value used to fill the edge
 */
static void MB_HCompNbr6(PLINE *plines_inout, Uint32 linoff_inout,
                         PLINE *plines_in, Uint32 linoff_in,
                         Uint32 bytes_in, Uint32 nb_lines,
                         Uint32 count, EDGE_TYPE edge_val )
{

      PLINE *p_in, *p_inout;
      
    Uint32 i;
    
    p_in = &plines_in[nb_lines-2];
    p_inout = &plines_inout[nb_lines-1];

    /* Note that in the cases where Y decreases (as here), we proceed from
     * bottom up, and, therefore, begin with odd line rather then the even one.
     */
    while(count-- > 0) {
        for(i = 2; i < nb_lines; i += 2) {
            COMP_LINE(p_inout,linoff_inout,p_in,linoff_in,bytes_in);
            p_in--, p_inout--;
            COMP_LINE_RIGHT(p_inout,linoff_inout,p_in,linoff_in,bytes_in,edge_val);
            p_in--, p_inout--;
        }
        COMP_LINE(p_inout,linoff_inout,p_in,linoff_in,bytes_in);
        p_inout--;
        COMP_EDGE_LINE(p_inout,linoff_inout,bytes_in,edge_val);
        p_in = &plines_inout[nb_lines-2];
        p_inout = &plines_inout[nb_lines-1];
    }
}

/* SPECIAL */

/**
 * Computes the result with neighbor 0 (no moves)
 * \param plines_inout pointer on the destination image lines
 * \param off_inout offset inside the destination image lines
 * \param plines_in pointer on the source image that is shifted pixel lines 
 * \param off_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param nb_lines number of lines in the image processed
 * \param count the shift amplitude
 * \param edge_val the value used to fill the edge
 */
static void MB_QCompNbr0(PLINE *plines_inout, Uint32 linoff_inout,
                         PLINE *plines_in, Uint32 linoff_in,
                         Uint32 bytes_in, Uint32 nb_lines,
                         Uint32 count, EDGE_TYPE edge_val )
{ 
    Uint32 i;

    for(i = 0; i < nb_lines; i++, plines_in++, plines_inout++) {
        COMP_LINE( plines_inout, linoff_inout, plines_in, linoff_in, bytes_in);
    }
}

/**
 * Does nothing.
 * This function exists to handle impossible movement cases in hexagonal grid.
 * \param plines_inout pointer on the destination image lines
 * \param off_inout offset inside the destination image lines
 * \param plines_in pointer on the source image that is shifted pixel lines
 * \param off_in offset inside the source image lines
 * \param bytes_in number of bytes inside the line
 * \param nb_lines number of lines in the image processed
 * \param count the shift amplitude
 * \param edge_val the value used to fill the edge
 */
static void MB_Stub(PLINE *plines_inout, Uint32 linoff_inout,
                    PLINE *plines_in, Uint32 linoff_in,
                    Uint32 bytes_in, Uint32 nb_lines,
                    Uint32 count, EDGE_TYPE edge_val )
{
}

/************************************************/
/*High level function and global variables    */
/************************************************/

/** typedef for the definition of function arguments */
typedef void (TSWITCHEP) (PLINE *plines_inout, Uint32 linoff_inout,
                          PLINE *plines_in, Uint32 linoff_in,
                          Uint32 bytes_in, Uint32 nb_lines,
                          Uint32 count, EDGE_TYPE edge_val );

/**
 * array giving the function to use for a given neighbor with
 * regards to the grid in use (hexagonal or square).
 */
static TSWITCHEP *SwitchTo[2][9] =
{
  { /* square neighbors */
     MB_QCompNbr0, /* No movement, so simple set diff */
     MB_QCompNbr1,
     MB_QCompNbr2,
     MB_QCompNbr3,
     MB_QCompNbr4,
     MB_QCompNbr5,
     MB_QCompNbr6,
     MB_QCompNbr7,
     MB_QCompNbr8
  },
  { /* hexagonal neighbors */
     MB_QCompNbr0, /* No movement, so simple set diff */
     MB_HCompNbr1,
     MB_QCompNbr3, /*hexagonal neighbor 2 is similar to square neighbor 3*/ 
     MB_HCompNbr3,
     MB_HCompNbr4,
     MB_QCompNbr7, /*hexagonal neighbor 5 is similar to square neighbor 7*/ 
     MB_HCompNbr6,
     MB_Stub,
     MB_Stub
  }
};
