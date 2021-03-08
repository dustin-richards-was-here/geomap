//  somewhat rough OpenSCAD lithophane - scruss, 2019-10
 infile  = "tileA_1_highprec_highres_blur.png";    // input image, PNG greyscale best
 x_px    = 500;  // input image width,  pixels
 y_px    = 500;  // input image height, pixels
 z_min   = 0.4;  // minimum output thickness, mm
 z_max   = 70;    // maximum output thickness, mm
 y_size  = 80;   // output model side length, mm
 // don't need to modify anything below here
 scale([y_size / y_px, y_size / y_px, (z_max - z_min)/100])surface(file = infile, invert = false);
 //cube([x_px * y_size / y_px, y_size, z_min]);