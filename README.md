# geomap
I created this project for the 3D Printing Club at the South Dakota School of Mines and Technology to convert geological survey data of the Black Hills to 3D printable STLs. To reduce labor and printer idle time, this project can combine multiple tiles of data into a single "supertile". Also capable of generating legs to ensure all tiles line up vertically, since they won't otherwise with a fixed base height.

So far, the code has only been tested with 16-bit grayscale TIFF images, but will likely work with others.

### Adjustable parameters
- X, Y, and Z scale factors
- Height of "base" to leave behind after trimming excess off of bottom of data
- Upper and lower outlier thresholds, used to throw out abnormally large or small values
- Supertile grouping size

### Data Flow

	┌────────────────┐
	│                │
	│  input images  ├─┐                                                           ┌─────────────────┐
	│                │ │                  ┌─────────────────────┐                  │                 │
	└────────────────┘ │                  │                     │  dat2stl.scad    │    3D models    │
	                   ├───get-elev.py───►│  intermediate data  ├─────────────────►│  maps and legs  │
	┌────────────────┐ │                  │        .dat         │  dat2legs.scad   │      .stl       │
	│                │ │                  └─────────────────────┘                  │                 │
	│ grid specifier ├─┘                                                           └─────────────────┘
	│      .csv      │
	└────────────────┘

Generated with the wonderful [ASCIIFlow](https://asciiflow.com/) editor.

### Caveats
The main caveat is *very high* memory usage, especially as tiles/supertiles get larger. The Python code isn't too bad, but OpenSCAD generates *very large* STLs. I attempted running a 40MB (5900x3700 px)TIFF through, and was thanked with about 18GB of RAM+swap usage before I had to kill the process. I've run plenty of 2MB (1000x500 px) images without issues.

If you're using supertiles, memory usage depends on input image size as well as the targeted supertile size. If you're using input images that are about 100KB (330x330 px) with a 3x3 supertile size, multiple images will be combined by get-elev.py. The result is OpenSCAD will be given .dat files as if you had given get-elev.py 900KB (990x990 px) images.
