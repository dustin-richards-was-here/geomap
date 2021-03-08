// for geomap by dustin richards, 2021-3
infile  = "tileA_1.png"; // input image, PNG greyscale best
x_px    = 200;  // input image width,  pixels
y_px    = 200;  // input image height, pixels
xy_size  = 80;   // output model side length, mm

// maximum possile raw value in the image
//   255 for 8-bit unsigned, 65535 for 16-bit unsigned
//   this script assumes that a 0 pixel indicates "no data", 
//     rather than meaning "lowest value"
z_max_raw = 255;
// maximum real-world height representable by the image (pixel = z_max_raw), m
z_max_m = 2200;
// minimum real-world height representable by the image (pixel = 1), m
z_min_m = 744.29;
// how many scale model mm correspond to a real-world m
z_mm_per_m = 0.1 / 3; // a single 0.1mm layer for 3m of z data
 
// scaling factor for x and y
xy_scale = xy_size / x_px;
// scaling factor for z
z_scale = (z_mm_per_m * (z_max_m - z_min_m)) / 100;
 
// don't need to modify anything below here
scale([xy_scale, xy_scale, z_scale])
    surface(file = infile, invert = false);