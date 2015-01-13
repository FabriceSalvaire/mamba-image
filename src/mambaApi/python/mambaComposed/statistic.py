"""
This module provides a set of functions to compute statistical values inside
a mamba image.
"""

# contributor: Nicolas BEUCHER

import mamba

def getMean(imIn):
    """
    Returns the average value (float) of the pixels of 'imIn' (which must be a
    greyscale image).
    """
    
    histo = mamba.getHistogram(imIn)
    s = sum(histo)
    t = 0
    for i,v in enumerate(histo):
        t = t + i*v
    return float(t)/float(s)

def getMedian(imIn):
    """
    Returns the median value of the pixels of 'imIn'.

    The median value is defined as the first pixel value for which at least
    half of the pixels are below it. 
    
    'imIn' must be a greyscale image.
    """
    
    histo = mamba.getHistogram(imIn)
    s = sum(histo)
    t = 0
    for i,v in enumerate(histo):
        t = t+v
        if t>s/2:
            break
    return i

def getVariance(imIn):
    """
    Returns the pixels variance (estimator without bias) of image 'imIn' (which 
    must be a greyscale image)..
    """
    
    mean = getMean(imIn)
    histo = mamba.getHistogram(imIn)
    s = sum(histo)
    t = 0
    for i,v in enumerate(histo):
        t = t+v*(i-mean)*(i-mean)
    return t/(s-1)
