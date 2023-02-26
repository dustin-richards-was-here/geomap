#!/usr/bin/python3

# Author: Dustin Richards <richards.dustinb@gmail.com>
# March 1, 2021
# Extracts elevation data from a grid of TIF files and generates 3D models
#  using OpenSCAD

# assumes unsigned 16-bit gray .tif files

# information on grid_file argument (gridCSVFile variable below):
#  you must provide a csv file that contains the file names of all the tiles in the grid
#  elements separated by commas, rows separated by newlines
#  your favorite spreadsheet software should be able to generate this with the help of some functions

# usage:
# python3 generate-models.py grid_file [directory with .tif files]

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

# how many tiles wide a supertile should be
supertileWidth = 3
# how many tiles tall a supertile should be
supertileHeight = 3
# how many units to leave on the bottom of a supertile, supertiles will be offset down so that this
#  is the minimum value
#  the .scad uses 0.1mm output per 3m input, so for a 1mm base, use 30 here
supertileBaseHeight = 30 # 1 mm base
# any data points greater than this value will be set to 0
outlierUpperThreshold = 1000000
# any data points below this value will not be used to calculate the minimum of a supertile
#  if your model is coming out with a large amount of unneeded material on the bottom, try raising this
outlierLowerThreshold = 100

# ==== END OF USER DEFINED VARIABLES ====

def printUsage():
    print("Usage:", sys.argv[0], "grid_file [input_directory]")
    print("See comments in script for details on how grid_file should be structured")
    print("input_directory should be a directory containing 16-bit gray .tif files")
    print("Files listed in grid_file MUST be in input_directory")

# --- handle command line inputs ---
numArgs = len(sys.argv)

# check if first argument is present, grid specifier .csv
if numArgs >= 2:
    gridCSVFile = sys.argv[1]
# if not, quit
else:
    printUsage()
    exit()

# check for a second argument, input directory
if numArgs >= 3:
    direc = sys.argv[2]
# if none, assume current directory
else:
    direc = "./"

print("Running...")

# import the csv containing the files that form the terrain map grid
gridChipsShort = np.genfromtxt(gridCSVFile, delimiter=',', dtype=str)

# grid size special case: 1x1
if gridChipsShort.shape == ():
    gridHeight = 1
    gridWidth = 1
    gridChipsTemp = gridChipsShort.item()
    gridChipsShort = [["", ""],["", ""]]
    gridChipsShort[0][0] = gridChipsTemp
else:
    gridWidth =  gridChipsShort.shape[1]
    gridHeight = gridChipsShort.shape[0]

# setup for supertile formation
gridChips = [[0 for i in range(gridWidth)] for j in range(gridHeight)]
supertileGridWidth = math.ceil(gridWidth / supertileWidth)
supertileGridHeight = math.ceil(gridHeight / supertileHeight)
supertileFiles = [[0 for x in range(supertileGridWidth)] for y in range(supertileGridHeight)]
tileWidth = 0
tileHeight = 0

# save a reference to stdout
orig_stdout = sys.stdout

# get the current time for use in some file/directory names
timeNow = strftime("%Y-%m-%d_%H-%M-%S", localtime())

# attempt to create a results directory
resultsDirName = "results_" + timeNow
os.mkdir(resultsDirName)

# makes sure all files listed in gridCSVFile are present in direc
print("Checking that files listed in " + gridCSVFile + " are in " + direc + "...")
for i in range(gridHeight):
    for j in range(gridWidth):
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
                #  only count value above the lower outlier threshold
                if tempSupertileVals[i][j] < min and tempSupertileVals[i][j] > outlierLowerThreshold:
                    min = tempSupertileVals[i][j]

        # offset is the value to remove from the supertile so we don't have a bunch of extra
        #  plastic on the bottom. This is also the height used to generate legs with dat2legs.scad
        #  so all supertiles will line up vertically.
        offset = min - supertileBaseHeight
        for i in range(len(tempSupertileVals)):
            for j in range(len(tempSupertileVals[0])):
                tempSupertileVals[i][j] -= offset
                # throw out outliers
                if tempSupertileVals[i][j] > outlierUpperThreshold:
                    tempSupertileVals[i][j] = 0
                # fix any values that were brought below zero by the offset
                if tempSupertileVals[i][j] < 0:
                    tempSupertileVals[i][j] = 0
    
        # save the supertile .dat
        supertileBaseName = resultsDirName + "/supertile_" + supertileName
        np.savetxt(supertileBaseName + ".dat", tempSupertileVals, fmt="%1u")

        # run OpenSCAD to generate a tile stl
        print("Generating 3D model for supertile...")
        outfileArg = supertileBaseName + ".stl"
        supertileXArg = "supertile_x=" + str(supertileTilesX)
        supertileYArg = "supertile_y=" + str(supertileTilesY)
        infileArg     = "infile=\"" + supertileBaseName + ".dat\""
        subprocess.run(["openscad", 
            "-o", outfileArg,
            "-D", supertileXArg,
            "-D", supertileYArg,
            "-D", infileArg,
            "dat2stl.scad"])
        print("Done!")
