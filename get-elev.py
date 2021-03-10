# Author: Dustin Richards <richards.dustinb@gmail.com>
# March 1, 2021
# Extracts elevation data from a TIF file
# I wrote this in four hours, don't @ me
# version 1.1

# assumes 8-bit gray .tif files (grayscale values 0-255)

# the simplest way to use this script is to drop it into a directory with a
#   bunch of .tif files and double-click it

# usage:
# python3 get-elev.py [image1].tif [image2].tif [image3].tif ...
# python3 get-elev.py *.tif (to get all .tif files in directory)
# python3 get-elev.py (also gets all .tif files in directory)

from PIL import Image
from glob import glob
from time import localtime, strftime
import pandas as pd
import numpy
import math
import sys
import os

print("Running...")

# get a list of files
if len(sys.argv) == 1: # if there isn't an argument
    files = glob("*.tif") # get all the .tif files in the current directory

elif sys.argv[1].find("*") != -1: # if the argument has a wildcard
    files = glob(sys.argv[1]) # expand the wilcard

elif len(sys.argv) > 1: # if there's a list of files
    files = sys.argv[1:len(sys.argv)].copy() # use the list of files

# save a reference to stdout
orig_stdout = sys.stdout

# storage variables for pandas
names = []
maximums = []
minimums = []
toplefts = []
toprights = []
bottomlefts = []
bottomrights = []

# get the current time for use in some file/directory names
timeNow = strftime("%Y-%m-%d_%H-%M-%S", localtime())

# attempt to create a results directory
resultsDirName = "results_" + timeNow
os.mkdir(resultsDirName)

for fileNum in range(0, len(files)):
    # get the filename we're using
    filename = files[fileNum]
    # redirect program output to stdout
    sys.stdout = orig_stdout

    # print out a progress message
    percentage = fileNum / (len(files)) * 100
    percentageString = "{:d}".format(math.floor(percentage))
    print("[" + percentageString + "%] " + filename)

    # read image
    tif = Image.open(filename)
    # get width and height
    width = tif.width
    height = tif.height
    # convert to a 2d numpy array
    elevarr = numpy.array(tif)
    # create an empty array for the output to OpenSCAD
    scadarr = numpy.array([[0] * width] * height)

    # switch to the results directory
    os.chdir(resultsDirName)

    # extract just the filename, sans the path and extension
    filename_noext = os.path.basename(filename).rsplit('.', 1)[0]
    # attempt to create a directory for the output
    # catch and handle exceptions for if the file exists. Probably also catches
    #  other errors, but we're not going to think about that too much
    try:
        os.mkdir(filename_noext)
    except OSError as error:
        print("Directory " + filename_noext + " exists, overwriting...")
    os.chdir(filename_noext)

    # output a csv with the raw elevation data
    numpy.savetxt(filename_noext + ".csv", elevarr, delimiter=",", fmt="%1u")

    # make a copy of the data with everything shifted down by (750 - 90) meters
    #   750 = lowest value in range
    #   90  = buffer to leave 3mm of plastic below lowest point
    for i in range(0, height):
        for j in range(0, width):
            scadarr[i][j] = elevarr[i][j] - (750 - 90)

    # output the shifted down data for OpenSCAD to use
    numpy.savetxt(filename_noext + ".dat", scadarr, fmt="%1u")

    # get the elevations of the corners
    topleft = elevarr[0][0]
    topright = elevarr[0][width-1]
    bottomleft = elevarr[height-1][0]
    bottomright = elevarr[height-1][width-1]

    # get the min and max elevation
    maximum = numpy.amax(elevarr)
    minimum = numpy.amin(elevarr)

    # store to the storage arrays
    names.append(filename_noext)
    toplefts.append(topleft)
    toprights.append(topright)
    bottomlefts.append(bottomleft)
    bottomrights.append(bottomright)
    maximums.append(maximum)
    minimums.append(minimum)

    # redirect print to stdout
    with open(filename_noext + "_stats.txt", 'w') as f:
        sys.stdout = f
        print(filename_noext)
        print("Units: meters")
        print("Min: " + str(minimum))
        print("Max: " + str(maximum))
        print("Top left:  " + str(topleft))
        print("Top right: " + str(topright))
        print("Bottom left : " + str(bottomleft))
        print("Bottom right: " + str(bottomright))

    # return to the original directory
    os.chdir("../..")

# restore stdout
sys.stdout = orig_stdout

stats = {"minimums": minimums,
         "maximums": maximums,
         "toplefts": toplefts,
         "toprights": toprights,
         "bottomlefts": bottomlefts,
         "bottomrights": bottomrights}

df = pd.DataFrame(stats, index=names)
df.to_csv("get-elev_all_stats_" + timeNow + ".csv")

print("Done!")
