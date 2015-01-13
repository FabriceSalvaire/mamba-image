# exampleA25.py
# OUT smiling-face.png

## TITLE #######################################################################
# Realtime face recognition : connecting Mamba Realtime and OpenCV

## DESCRIPTION #################################################################
# This example is similar to the previous face recognition example. But, instead
# of using a fixed image, the face recognition is performed in realtime from a
# video coming from a webcam. The openCV face recognition algorithm is pipelined
# in the mambaRealtime process and applied on the video acquired by the webcam.

## SCRIPT ######################################################################
# Importing mamba, mambaComposed, mambaDraw, mambaExtra and mambaRealtime.
from mambaRealtime import *
from mamba import *
from mambaComposed import *
from mambaDraw import *
from mambaExtra import *

# Importing opencv.
import cv

import os

def Mamba2openCV(imIn):
    """
    Creates an OpenCV image from the mamba image 'imIn'. The function only
    works with 8-bit images (other cases will return None).
    """
    if imIn.getDepth()!=8:
        return None

    (w, h) = imIn.getSize()
    cvImOut = cv.CreateImage((w,h), cv.IPL_DEPTH_8U, 1)
    cv.SetData(cvImOut, imIn.extractRaw())
    
    return cvImOut

def openCV2Mamba(cvImIn, imOut):
    """
    Loads the data contained in the openCV image 'cvImOut' into mamba image
    'imOut'. Images size and depth must be identical for the function to
    operate (the function will quit silently otherwise).
    """
    if cvImIn.depth!=cv.IPL_DEPTH_8U:
        return
    if imOut.getDepth()!=8:
        return
    if cv.GetSize(cvImIn)!=imOut.getSize():
        return
    imOut.loadRaw(cvImIn.tostring())

def detectFaces(imIn):
    """
    This function detects faces inside Mamba image 'imIn' by first converting
    it into an OpenCV image and then applying the appropriate functions.
    The function returns a tuple containing the coordinates of the bounding
    box around all the faces in the image. 
    """
    
    cvim = Mamba2openCV(imIn)
    size = cv.GetSize(cvim)

    # Preparing the image.
    storage = cv.CreateMemStorage(0)
    # equalize histogram.
    cv.EqualizeHist(cvim, cvim)
    # detect objects (faces)
    cascade = cv.Load(FACE_CASCADE_PATH)
    faces = cv.HaarDetectObjects(cvim, cascade, storage, 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (50, 50))
    #cv.HaarDetectObjects(image, cascade, storage, 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (50, 50))
    faces_bb = ()
    for face in faces:
        face_coord = face[0]
        faces_bb += ((face_coord[0], face_coord[1], face_coord[0]+face_coord[2], face_coord[1]+face_coord[3]),)       
    return faces_bb
    
def mainFaceRecognition(imIn, imOut):
    """
    Main face recognition procedure. In order to be called by mambaRealtime,
    this procedure must have a single mamba input image and a single output.
    """
    
    imbin = imageMb(imIn, 1)
    faces = detectFaces(imIn)
    # Drawing a box around each detected face.
    for f in faces:
        drawBox(imbin, f, 1)
        drawBox(imbin, map(lambda x : x+1, f), 1)
        drawBox(imbin, map(lambda x : x-1, f), 1)
    copy(imIn, imOut)
    multiSuperpose(imOut, imbin)
    
# Launching mambaRealtime (adapts itself to your system).
# Modify FACE_CASCADE_PATH so that it points to your local installation of the
# cascade file
if os.name == 'nt':
    FACE_CASCADE_PATH = 'C:\opencv\data\haarcascades/haarcascade_frontalface_alt.xml'
    launchRealtime("0", DSHOW)
else:
    FACE_CASCADE_PATH = '/usr/share/opencv/haarcascades/haarcascade_frontalface_alt.xml'
    launchRealtime("/dev/video0", V4L2)
    
# The box is displayed in red.
pal = tagOneColorPalette(255, (255,0,0))
setProcessRealtime(mainFaceRecognition, INSTANT)
setPaletteRealtime(pal)

