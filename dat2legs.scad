// for SDSMT 3DPC geomap project by Dustin Richards, 2021-5

// ------ INPUT PARAMETERS ------

supertile_x = 3; // # of tiles in the width of a supertile
supertile_y = 3; // # of tiles in the height of a supertile

x_size  = 80 * supertile_x; // output model x side length, mm
y_size  = 80 * supertile_y; // output model y side length, mm

// a single 0.1mm layer for 3m of z data
z_mm_per_m = 0.1 / 3; // how many scale model mm correspond to a real-world m

leg_height_base = 10; // minimum leg height, mm
tile_min_elev = 0; // minimum normalized elevation found in the supertile, used to calculate leg_height_comp

leg_xy_size = 10;     // horizontal edge length of legs

leg_offset = 10;  // distance from center of leg to edge of tile, must be at least half of leg_xy_size
strut_height = 5; // thickness of the members that connect the legs together

// ------ END INPUT PARAMETERS ------

// leg height 
leg_height_comp = tile_min_elev * z_mm_per_m;  // leg height added on to base to compensate for tile heights
leg_height = leg_height_base + leg_height_comp;  // overall height of legs, including struts

// locations of legs
leg_gap  = leg_offset - (leg_xy_size/2); // gap between outer edge of leg and edge of supertile
leg1_loc = [leg_offset, y_size-leg_offset, 0];        // top left
leg2_loc = [x_size-leg_offset, y_size-leg_offset, 0]; // top right
leg3_loc = [leg_offset, leg_offset, 0];               // bottom left
leg4_loc = [x_size-leg_offset, leg_offset, 0];        // bottom right
leg5_loc = [x_size/2, y_size/2, 0];                   // middle
leg_locs = [leg1_loc, leg2_loc, leg3_loc, leg4_loc, leg5_loc];

// offset and size for the outer dimension of the struts
strut_outer_offset = [leg_gap, leg_gap, 0];
strut_outer_size = [x_size - (leg_gap*2), y_size - (leg_gap*2), strut_height];

// offset and size for the inner dimension of the struts, used to make a cut
strut_inner_offset = [
  strut_outer_offset[0] + leg_xy_size,
  strut_outer_offset[1] + leg_xy_size,
  0];
strut_inner_size = [
  strut_outer_size[0] - (leg_xy_size*2),
  strut_outer_size[1] - (leg_xy_size*2),
  strut_height];
  
module legs() {
  union() {
    // extrude each leg
    linear_extrude(leg_height) {
      for(i = [0:4])
        translate(leg_locs[i])
          square(leg_xy_size, true);
    }
    
    // make the outer struts
    difference() {
      translate(strut_outer_offset)
        cube(strut_outer_size);
      
      translate(strut_inner_offset)
        cube(strut_inner_size);
    }
    
    // struts for the middle leg
    translate([leg_gap, leg5_loc[1] - (leg_xy_size/2), 0])
      cube([strut_outer_size[0], leg_xy_size, strut_height]);
    translate([leg5_loc[1] - (leg_xy_size/2), leg_gap, 0])
      cube([leg_xy_size, strut_outer_size[1], strut_height]);
  }
}

legs();