# exampleE10.py
# OUT display_proj.png

## TITLE #######################################################################
# Display in mamba3D

## DESCRIPTION #################################################################
# This example shows you how to select and activate the various displays
# available in mamba 3D package. The foot image data used can be 
# downloaded at http://tc18.liris.cnrs.fr/code_data_set/3D_images.html.

## SCRIPT ######################################################################
# Importing the mamba module
from mamba3D import *

# Creating an image and loading the data
im3D = image3DMb()
im3D.loadRaw("foot.raw.gz")

# Activating the display. This will make a window appear
im3D.showDisplay() # Same effect can be achieved with im3D.showDisplay("VTK")

# This line will activate a volume rendering display if you have VTK
# installed on your computer. You can rotate (holding your mouse left
# button while moving it), zoom in and out (same movement while holding
# the right button) and displace the image (this time by holding both the
# left button and the shift key on your keyboard while moving the mouse).
# This allows you to view more precisely any area of your image. You can
# restore the initial settings by pressing r (Although this does not seem
# to affect rotation).

# If you want to activate a more precise display or if you don't have
# VTK installed you may want to use the plane projection display
im3D.showDisplay("PROJECTION")

# You can navigate through planes moving your mouse while holding <ctrl> down.
# The mouse motion will allow you to change the plane following it (the
# displayer enables a red cross to indicate where you are in the image data).

# You can also alternatively display a 2D image extracted from the 3D image
im3D[128].showDisplay()
