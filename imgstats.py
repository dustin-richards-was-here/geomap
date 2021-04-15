from PIL import Image
import sys
import numpy

img = Image.open(sys.argv[1])
print("Width: " + str(img.width))
print("Height: " + str(img.height))

# find min and max pixel value
min = 9999999
max = -1
arr = numpy.array(img)

for row in arr:
    for pixel in row:
        if pixel < min:
            min = pixel
        elif pixel > max:
            max = pixel

print("Min: " + str(min))
print("Max: " + str(max))
