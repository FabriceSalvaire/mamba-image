from __future__ import print_function
import numpy as np
import mamba

def fill_index(image):
    data = np.arange(0, image.full_height*image.full_width)
    data.shape = (image.full_height, image.full_width)
    image1.array[...] = data

def fill_random(image):
    data = np.array(np.random.rand(image.height*image.width)*100, dtype=image.array.dtype)
    data.shape = image.height, image.width
    image.view[...] = data

height, width = 10, 5

for depth in (8, 32):

    print("\ndepth {}".format(depth))

    image1 = mamba.NumpyWrapper(height, width, depth)
    image2 = image1.clone()
    image3 = image1.clone()
  
    for image in (image1, image2):
        fill_random(image)
        # fill_index(image)

    # image_mb1 = mamba.imageMb(width, height, depth)
    # image_mb1.fill(1)
    # image_mb2 = mamba.imageMb(width, height, depth)
    # image_mb2.fill(2)
    # image_mb3 = mamba.imageMb(width, height, depth)
    # mamba.add(image_mb1, image_mb2, image_mb3)
    # print("Mb", image_mb3.getPixel((1,1)))

    image_mb1 = mamba.imageMb(image1)
    image_mb2 = mamba.imageMb(image2)
    image_mb3 = mamba.imageMb(image3)
    assert(image_mb1.mbIm.height == image1.adjusted_height)
    assert(image_mb1.mbIm.width == image1.adjusted_width)

    # for y in range(height):
    #     for x in range(width):
    #         print(x, y, image_mb1.getPixel((x, y)))
    
    mamba.add(image_mb1, image_mb2, image_mb3)
    for image in (image1, image2, image3):
        print(image.view)
    assert(np.array_equal(image1.array + image2.array, image3.array))
