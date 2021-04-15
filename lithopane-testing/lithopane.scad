// for SDSMT 3DPC geomap project by Dustin Richards, 2021-3

// ------ INPUT PARAMETERS ------
//infile  = "tileA_1_16bit_unsigned_shifted.dat"; // input heightmap
infile  = "../results_2021-04-04_21-53-39/tC_3/tC_3.dat"; // input heightmap
stamp   = infile; // id to stamp on the bottom

x_px    = 334;    // heightmap # of columns
y_px    = 334;    // heightmap # of rows
x_size  = 80;     // output model x side length, mm
y_size  = x_size; // output model y side length, mm

// how many scale model mm correspond to a real-world m
z_mm_per_m = 0.1 / 3; // a single 0.1mm layer for 3m of z data

// lowest value found in infile
minimum = 1198 - (750 - 90);
// ------ END INPUT PARAMETERS ------
 
// scaling factors for x and y
x_scale = x_size / x_px;
y_scale = y_size / y_px;
// scaling factor for z
z_scale = z_mm_per_m;

// distance to indent the id and arrow stamps for the bottom, mm
stamp_depth = 0.5;

// size of legs
leg_xy_size = 10;
leg_hole_depth = 3;

// locations of legs
leg_offset = 10;
leg1_loc = [leg_offset, y_size-leg_offset, 0];        // top left
leg2_loc = [x_size-leg_offset, y_size-leg_offset, 0]; // top right
leg3_loc = [leg_offset, leg_offset, 0];               // bottom left
leg4_loc = [x_size-leg_offset, leg_offset, 0];        // bottom right
leg_locs = [leg1_loc, leg2_loc, leg3_loc, leg4_loc];

module map() {
  difference() {
    // import, scale, and mirror the heightmap
    translate([0, y_size, 0])
      scale([x_scale, y_scale, z_scale])
      mirror([0, 1, 0])
      surface(file = infile, invert = false);

    // stamp an id in the bottom
    linear_extrude(stamp_depth)
      translate([x_size/2, y_size*2/3, 0])
      scale([0.5, 0.5, 1])
      rotate([180, 0, 180])
      text(stamp, halign="center", valign="center");

    // stamp an arrow in the bottom
    translate([x_size/2, y_size/3, 0])
      linear_extrude(stamp_depth)
      arrow();
    
    // holes for legs
    for (i = [0:3])
    {
      translate(leg_locs[i])leg_hole();
    }
  }
}

module arrow() polygon( points = [
  [0, 20], [10, 0], [5, 0], [5, -20], 
  [-5, -20], [-5, 0], [-10, 0]
]);

module leg_hole() {
  cube([leg_xy_size, leg_xy_size, leg_hole_depth], center=true);
}

map();
//leg_hole();