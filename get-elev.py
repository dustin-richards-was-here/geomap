# Author: Dustin Richards <richards.dustinb@gmail.com>
# March 1, 2021
# Extracts elevation data from a TIF file
# version 1.1

# assumes unsigned 16-bit gray .tif files

# the simplest way to use this script is to drop it into a directory with a
#   bunch of .tif files and double-click it

# usage:
# python3 get-elev.py [directory with .tif files]

from PIL import Image
from glob import glob
from time import localtime, strftime
import subprocess
import pandas as pd
import numpy as np
import math
import sys
import os

# ==== THESE ARE USER DEFINED VARIABLES, EDIT THESE TO CUSTOMIZE THE OUTPUT ====

# csv file that contains the file names of all the tiles in the grid
#  elements separated by commas, rows separated by newlines
#  your favorite spreadsheet software should be able to generate this with the help of some functions
gridCSVFile = "./grid.csv" 
# how many tiles wide a supertile should be
supertileWidth = 3
# how many tiles tall a supertile should be
supertileHeight = 3
# how many units to leave on the bottom of a supertile, supertiles will be offset down so that this
#  is the minimum value
#  the .scad uses 0.1mm output per 3m input, so for a 1mm base, use 30 here
supertileBaseHeight = 30 # 1 mm base

# ==== END OF USER DEFINED VARIABLES ====

print("Running...")

# import the csv containing the files that form the terrain map grid
gridChipsShort = np.genfromtxt(gridCSVFile, delimiter=',', dtype=str)
gridWidth =  gridChipsShort.shape[1]
gridHeight = gridChipsShort.shape[0]

# setup for supertile formation
gridChips = [[0 for i in range(gridWidth)] for j in range(gridHeight)]
supertileGridWidth = math.ceil(gridWidth / supertileWidth)
supertileGridHeight = math.ceil(gridHeight / supertileHeight)
supertileFiles = [[0 for x in range(supertileGridWidth)] for y in range(supertileGridHeight)]
tileWidth = 0
tileHeight = 0

if len(sys.argv) == 1: # if there isn't an argument
    direc = "./"
elif len(sys.argv) == 2: # if there is a single argument, should be a directory containing the images
    direc = sys.argv[1]

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

# makes sure all files listed in gridCSVFile are present in direc
print("Checking that files listed in " + gridCSVFile + " are in " + direc + "...")
for i in range(len(gridChipsShort)):
    for j in range(len(gridChipsShort[0])):
        fpath = direc + "/" + gridChipsShort[i][j]
        if not os.path.isfile(fpath):
            print("Error: " + fpath + " not found, exiting.")
            exit()
        gridChips[i][j] = fpath

# load a single tile and get its dimensions to use later
tif = Image.open(gridChips[0][0])
tileWidth = tif.width
tileHeight = tif.height

# divide up the tiles into groups of supertiles
i = 0
j = 0
supertile_i = 0
supertile_j = 0
tempSuperHeight = 0
tempSuperWidth = 0
tempSupertile = []
tempSupertileRow = []

while i < gridHeight:
    # form all supertiles possible in a row
    while j < gridWidth:
        # form a single supertile
        # pull up to supertileHeight rows of supertileWidth length
        while i + tempSuperHeight < gridHeight and tempSuperHeight < supertileHeight:
            
            # pull up to supertileWidth tiles from the row
            while j + tempSuperWidth < gridWidth and tempSuperWidth < supertileWidth:
                #tempSupertile[tempSuperHeight][tempSuperWidth] = gridChips[i+tempSuperHeight][j+tempSuperWidth]
                tempSupertileRow.append(gridChips[i+tempSuperHeight][j+tempSuperWidth])
                tempSuperWidth += 1
        
            tempSupertile.append(tempSupertileRow.copy())
            tempSupertileRow.clear()

            tempSuperHeight += 1
            tempSuperWidth = 0

        # increment j by the width of a supertile
        j += supertileWidth

        # save the supertile we just formed
        supertileFiles[supertile_i][supertile_j] = tempSupertile.copy()
        supertile_j += 1

        # clear out the temp supertile
        #for k in range(0, supertileHeight):
        #    tempSupertile[k] = [0]*supertileWidth
        tempSupertile.clear()
        tempSuperHeight = 0

    # increment i by the height of a supertile
    i += supertileHeight
    supertile_i += 1
    supertile_j = 0
    j = 0

# form the supertile arrays
for supertileFileRow in supertileFiles:
    for supertile in supertileFileRow:
        # filename for the output, extract just the name of the top-left tile sans path and extension
        supertileName = supertile[0][0].split('/')
        supertileName = supertileName[len(supertileName)-1].split('.')[0]
        print("\nProcessing supertile " + supertileName)
        # array of arrays, one for each tile in the supertile, data values
        tempTileVals = [[0 for i in range(tileWidth)] for j in range(tileHeight)]

        # load the data from each tile into its respective array element
        for i in range(len(supertile)):
            for j in range(len(supertile[0])):
                # read image
                print(supertile[i][j])
                tif = Image.open(supertile[i][j])
                # convert to a 2d numpy array
                tempTileVals[i][j] = np.array(tif)

        # tempSupertileVals holds all the values for a single supertile in a single 2d array
        supertileTilesX = j+1 # width of the supertile in tiles
        supertileTilesY = i+1 # height of the supertile in tiles
        supertileWidthPx = supertileTilesX * tileWidth
        supertileHeightPx = supertileTilesY * tileHeight
        tempSupertileVals = [[0 for i in range(supertileWidthPx)] for j in range(supertileHeightPx)]

        # we'll keep track of the minimum value in each supertile in order to remove excess plastic on the bottom of it
        min = 999999999

        # extract the data from the individual tile arrays and form a supertile
        for i in range(len(tempSupertileVals)):
            row = math.floor(i / tileHeight)
            for j in range(len(tempSupertileVals[0])):
                col = math.floor(j / tileWidth)
                tileRow = i % tileHeight
                tileCol = j % tileWidth
                tempSupertileVals[i][j] = tempTileVals[row][col][tileRow][tileCol]
                # track the minimum value in the supertile
                if tempSupertileVals[i][j] < min:
                    min = tempSupertileVals[i][j]

        offset = min - supertileBaseHeight
        for i in range(len(tempSupertileVals)):
            for j in range(len(tempSupertileVals[0])):
                tempSupertileVals[i][j] -= offset
    
        # save the supertile .dat
        supertileBaseName = resultsDirName + "/supertile_" + supertileName
        np.savetxt(supertileBaseName + ".dat", tempSupertileVals, fmt="%1u")

        # run OpenSCAD to generate a tile stl
        print("Generating 3D model for supertile...")
        outfileArg = supertileBaseName + ".stl"
        supertileXArg = "supertile_x=" + str(supertileTilesX)
        supertileYArg = "supertile_y=" + str(supertileTilesY)
        infileArg     = "infile=\"" + supertileBaseName + ".dat\""
        subprocess.run(["openscad-nightly", 
            "-o", outfileArg,
            "-D", supertileXArg,
            "-D", supertileYArg,
            "-D", infileArg,
            "dat2stl.scad"])
        print("Done!")

        # run OpenSCAD to generate a legs stl
        print("Generating 3D model for legs...")


exit()

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
    elevarr = np.array(tif)
    # create an empty array for the output to OpenSCAD
    scadarr = np.array([[0] * width] * height)

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
    np.savetxt(filename_noext + ".csv", elevarr, delimiter=",", fmt="%1u")

    # make a copy of the data with everything shifted down by (750 - 90) meters
    #   750 = lowest value in range
    #   90  = buffer to leave 3mm of plastic below lowest point
    for i in range(0, height):
        for j in range(0, width):
            scadarr[i][j] = elevarr[i][j] - (750 - 90)

    # output the shifted down data for OpenSCAD to use
    np.savetxt(filename_noext + ".dat", scadarr, fmt="%1u")

    # get the elevations of the corners
    topleft = elevarr[0][0]
    topright = elevarr[0][width-1]
    bottomleft = elevarr[height-1][0]
    bottomright = elevarr[height-1][width-1]

    # get the min and max elevation
    maximum = np.amax(elevarr)
    minimum = np.amin(elevarr)

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
df.to_csv("all_stats_" + timeNow + ".csv")

print("Done!")
