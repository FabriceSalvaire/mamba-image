# exampleE4.py
# IN snake.png

## TITLE #######################################################################
# Image properties

## DESCRIPTION #################################################################
# This example shows you how to get image properties like size and depth.
# It also describes how the image constructor can be used to create images
# sharing the same properties.

## SCRIPT ######################################################################
from __future__ import print_function
# Importing the mamba module
from mamba import *

# Loading an image
im = imageMb('images/snake.png')

# This image is 320x230 in 8-bit greyscale
print(im.getSize())
print(im.getDepth())

# Creating an image with the same properties
im1 = imageMb(im)
print(im1.getSize())
print(im1.getDepth())

# Creating an image with the same properties except for depth
im2 = imageMb(im, 1)
print(im2.getSize())
print(im2.getDepth()) # <- here the return is 1


