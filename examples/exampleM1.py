# exampleM1.py
# IN snake.png
# OUT snake_ero10rt.png

## TITLE #######################################################################
# Erosion and structuring elements

## DESCRIPTION #################################################################
# This example shows you how to create a structuring element and how to use it 
# with the erode function.

## SCRIPT ######################################################################
# Importing the mamba module and the mambaComposed package
from mamba import *
import mambaComposed as mC

# Opening and creating images 
im1 = imageMb('images/snake.png')
im2 = imageMb(im1)

# Creating a reversed triangle (as opposed to the TRIANGLE found in Mamba 
# source) structuring element
reverse_triangle = mC.structuringElement([0,1,6], grid=HEXAGONAL)

# Performing an erosion of size 10 with the created structuring element
mC.erode(im1, im2, 10, se=reverse_triangle)

im2.save("output/snake_ero10rt.png")
