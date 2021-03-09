// for SDSMT 3DPC geomap project by Dustin Richards, 2021-3

infile  = "tileA_1_16bit_unsigned.dat"; // input heightmap
stamp   = infile; // id to stamp on the bottom

x_px    = 200;    // heightmap # of columns
y_px    = 200;    // heightmap # of rows
x_size  = 80;     // output model x side length, mm
y_size  = x_size; // output model y side length, mm

// how many scale model mm correspond to a real-world m
z_mm_per_m = 0.1 / 3; // a single 0.1mm layer for 3m of z data
 
// scaling factors for x and y
x_scale = x_size / x_px;
y_scale = y_size / y_px;
// scaling factor for z
z_scale = z_mm_per_m;

// distance to indent the id and arrow stamps for the bottom, mm
stamp_depth = 0.5;

difference() {
    // , scale, and mirror the heightmap
    translate([0, y_size, 0])
        scale([x_scale, y_scale, z_scale])
        mirror([0, 1, 0])
        surface(file = infile, invert = false);
    
    // stamp an id in the bottom
    linear_extrude(stamp_depth)
        translate([x_size/2, y_size/2, 0])
        scale([0.5, 0.5, 1])
        rotate([180, 0, 180])
        text(stamp, halign="center", valign="center");
    
    // stamp an arrow in the bottom
    linear_extrude(stamp_depth)
        translate([x_size / 2, y_size * 3 / 4, 0])
        scale([0.5, 0.5, 1])
        arrow();
}

module arrow() polygon( points = [
    [0, 20], [10, 0], [5, 0], [5, -20], 
    [-5, -20], [-5, 0], [-10, 0]
]);