// for SDSMT 3DPC geomap project by Dustin Richards, 2021-3

// ------ INPUT PARAMETERS ------

supertile_x = 3; // # of tiles in the width of a supertile
supertile_y = 3; // # of tiles in the height of a supertile

x_px    = 334 * supertile_x;    // heightmap # of columns
y_px    = 334 * supertile_y;    // heightmap # of rows
x_size  = 80 * supertile_x;     // output model x side length, mm
y_size  = 80 * supertile_y;     // output model y side length, mm

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
leg_height = 20;
leg_xy_size = 10;
leg_hole_depth = 1;

// locations of legs
leg_offset = 10;
leg_gap  = leg_offset - (leg_xy_size/2); // gap between outer edge of leg and edge of supertile
leg1_loc = [leg_offset, y_size-leg_offset, 0];        // top left
leg2_loc = [x_size-leg_offset, y_size-leg_offset, 0]; // top right
leg3_loc = [leg_offset, leg_offset, 0];               // bottom left
leg4_loc = [x_size-leg_offset, leg_offset, 0];        // bottom right
leg_locs = [leg1_loc, leg2_loc, leg3_loc, leg4_loc];

// leg connecting struts
strut_height = 5;
strut_outer_offset = [leg_gap, leg_gap, 0];
strut_outer_size = [x_size - (leg_gap*2), y_size - (leg_gap*2), strut_height];
strut_inner_offset = [
  strut_outer_offset[0] + leg_xy_size,
  strut_outer_offset[1] + leg_xy_size,
  0];
strut_inner_size = [
  strut_outer_size[0] - (leg_xy_size*2),
  strut_outer_size[1] - (leg_xy_size*2),
  strut_height];


module legs() {
  linear_extrude(leg_height) {
    for(i = [0:3])
      translate(leg_locs[i])
      square(leg_xy_size, true);
  }
  
  difference() {
    translate(strut_outer_offset)
      cube(strut_outer_size);
    
    translate(strut_inner_offset)
      cube(strut_inner_size);
  }
}

module arrow() polygon( points = [
  [0, 20], [10, 0], [5, 0], [5, -20], 
  [-5, -20], [-5, 0], [-10, 0]
]);

module leg_hole() {
  cube([leg_xy_size, leg_xy_size, leg_hole_depth], center=true);
}

legs();