# exampleM4.py
# IN colorful.jpg
# OUT colorful_grad.png

## TITLE #######################################################################
# Color channels manipulations

## DESCRIPTION #################################################################
# This example shows you how to extract a specific color channel out of an
# image and how to reconstruct color images with three mamba images and the
# mix function. The colorful image was taken from wikimedia at 
# http://commons.wikimedia.org/wiki/File:Ebenthal_Schlosswirt_20052010_06.jpg.

## SCRIPT ######################################################################
# Importing the mamba module, the mambaComposed package and the mambaExtra 
# module
from mamba import *
import mambaExtra
import mambaComposed as mC

# Opening the image for each color channel (red, green and blue)
imRed = imageMb('colorful.jpg', rgbfilter=(1.0, 0.0, 0.0))
imGreen = imageMb('colorful.jpg', rgbfilter=(0.0, 1.0, 0.0))
imBlue = imageMb('colorful.jpg', rgbfilter=(0.0, 0.0, 1.0))

# We will perform a half gradient on each color channel
mC.halfGradient(imRed, imRed)
mC.halfGradient(imGreen, imGreen)
mC.halfGradient(imBlue, imBlue)

# Then we recombine the three channel image into one using the 
# mix function. This function actually returns a PIL image
pilim = mambaExtra.mix(imRed, imGreen, imBlue)

# We save it
pilim.save("colorful_grad.png")
