#!/usr/bin/python3

# Author: Dustin Richards <richards.dustinb@gmail.com>
# Dec 14, 2021
# Extracts min/max elevation stats from a grid of TIF file
# version 1.0

# assumes unsigned 16-bit gray .tif files

# information on grid_file argument (gridCSVFile variable below):
#  you must provide a csv file that contains the file names of all the tiles in the grid
#  elements separated by commas, rows separated by newlines
#  your favorite spreadsheet software should be able to generate this with the help of some functions

# usage:
# python3 get-stats.py grid_file [directory with .tif files]

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

# any data points greater than this value will be ignore
outlierUpperThreshold = 1000000
# any data points below this value will be ignored
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

# makes sure all files listed in gridCSVFile are present in direc
print("Checking that files listed in " + gridCSVFile + " are in " + direc + "...")
for i in range(gridHeight):
    for j in range(gridWidth):
        fpath = direc + "/" + gridChipsShort[i][j]
        if not os.path.isfile(fpath):
            print("Error: " + fpath + " not found, exiting.")
            exit()
        gridChips[i][j] = fpath

maxHeight = 0
minHeight = 9999999
maxHeightTile = None
minHeightTile = None

for row in gridChips:
    for filename in row:
        print(filename)

        # read image
        tif = Image.open(filename)
        # convery to a numpy array
        arr = np.array(tif)

        # check for a new min or max
        localMaxHeight = arr.max()
        localMinHeight = arr.min()
        if localMaxHeight > maxHeight:
            maxHeight = localMaxHeight
            maxHeightTile = filename
        if localMinHeight < minHeight:
            minHeight = localMinHeight
            minHeightTile = filename

print("Max height:", maxHeight, "in tile", maxHeightTile)
print("Min height:", minHeight, "in tile", minHeightTile)
