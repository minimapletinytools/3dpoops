// wood dowel threading block that attaches directly to a trim router

use <BOSL/threading.scad>

// primary screw parameters
// screw diameter, you may want to make this slightly larger than the nominal size of the rod.
screw_diameter = 19.2; 
// threads per inch (6 to match the beall threader)
tpi = 6; 

// Convert to inches for calculations (1 inch = 25.4 mm)
screw_diameter_inch = screw_diameter / 25.4;

// Main dimensions
// screw goes in this direction, make this longer for more support I guess. 2.5 seems fine.
width = 2.5 * 25.4;  
// length of the threading block
length = screw_diameter * 2.5;
// height of the threading block
height = (screw_diameter_inch + 0.75) * 25.4;

// center hole location parameters
thread_z_padding = 3/8 * 25.4; // 1/4 inch in mm
thread_z_location = thread_z_padding + screw_diameter_inch/2 * 25.4; // 1/4" + screw radius in mm

// mounting plate dimensions
mounting_plate_thickness = 10;
mounting_plate_width = 120;
mounting_plate_length = 120;

// alignment and screw hole dimensions
center_hole_diameter = 3/8 * 25.4; // 3/8 inch in mm
side_hole_diameter = 7/32 * 25.4;  // 7/32 inch in mm
side_hole_bore_diameter = 10;
side_hole_bore_depth = 10;

// chamfer radius for rounded edges
chamfer_radius = 2; // 2mm radius for rounded corners

// Logo parameters
// add the minimaple logo 吕 
enable_logo = true;
// scale factor for the logo (1.0 = original size)
logo_scale = 1;
// depth to engrave in mm
logo_depth = 1;          

// annoying openSCAD stuff
poop = 0.01;

// Logo module - the 吕 character made of two boxes
module logo() {
    logo_width = 7;           // Width of the bottom box
    logo_height = 4;           // Height of the bottom box
    logo_top_scale = 0.8;      // Ratio of top box width to bottom box
    logo_spacing = 1.5;          // Vertical gap between the two boxes

     minkowski() {
        rotate([90,0,0]) {
            scale([logo_scale, logo_scale, 1]) {  // scale X and Y, keep Z (depth) unchanged
                union() {
                    // Bottom box
                    translate([-logo_width/2, -logo_height/2, 0])
                        cube([logo_width, logo_height, logo_depth+poop]);
                    
                    // Top box
                    translate([-logo_width*logo_top_scale/2, logo_height/2 + logo_spacing, 0])
                        cube([logo_width*logo_top_scale, logo_height, logo_depth+poop]);
                }
            }
        };
        sphere(r = 0.2, $fn = 24); 
    }
}

module wood_threader() {

    difference() {
        // Main rectangular body
        // chamfer the edges of the block
        
        minkowski() {
            union() {
                translate([-length/2 + chamfer_radius, -width/2 + chamfer_radius, -height/2 + chamfer_radius])
                    cube([length - 2*chamfer_radius, width - 2*chamfer_radius, height - 2*chamfer_radius]);
                // make a mounting plate at the bottom of the block
                translate([-mounting_plate_length/2, -mounting_plate_width/2,  -height/2 + chamfer_radius ])
                    cube([mounting_plate_length, mounting_plate_width, mounting_plate_thickness]);
            }
            sphere(r = chamfer_radius, $fn = 32);
        }


        // Add logo if enabled
        if (enable_logo) {
            // Position logo on the top face of the block
            z_offset = height/2+poop;
            x_offset = 0;  // center horizontally
            y_offset = 0;  // center front-to-back
            
            translate([x_offset, y_offset, z_offset])
                rotate([90, 0, 0])  // keep upright
                    logo();
        }


        // mounting holes for direct tapping M5 screws spaced 100mm apart (adjust this to fit your router)
        for (i = [-1, 1]) {
            for (j = [-1, 1]) {
                translate([i * 50, j * 50, 0])
                    cylinder(h = 100, d = 4.8, center = true);
            }
        }
    
        {
            // Center hole (3/8" diameter, halfway down)
            translate([0, 0, -height/4])
            cylinder(h = height/2 + poop, d = center_hole_diameter, center = true);
        }


        // Threaded hole using BOSL library
        // the reason we don't start the thread in the middle of the block is so that we can consistently align the start of the threads with the center of the hole (threads grow out from the middle in bosl library)
        {
            translate([0, 0, thread_z_location - height/2])
            rotate([90, 0, 0])
            // the center of the thread starts on the +x axis in the center of therod so we need to rotate by 90 degrees for alignment
            rotate([0, 0, 90])
            // this uses the default thread angle of 30 which matches the beall tap
            threaded_rod(
                d = screw_diameter,
                l = mounting_plate_width + 10,
                pitch = 25.4/tpi, // Convert TPI to pitch in mm
                internal = true,
                //bevel = true,
                $fn=64
            );
        }

        // we actually only want half the hole threaded, cut out the threads from the other half with a screw_diameter cylinder with some awkward cutouts
        {
            //translate([0, mounting_plate_width/2 + 25.4/tpi/2, thread_z_location - height/2])
            difference()
            {
                
                // make the cylinder go 1/4 of a tooth past the center
                overstep = 25.4/tpi*1/4;
                translate([0, mounting_plate_width/2 - overstep, thread_z_location - height/2])
                    rotate([90, 0, 0])
                        cylinder(h = mounting_plate_width, d = screw_diameter, center = true);

                // now chop off the bottom corner of the cylinder so that the threads reach the hole
                translate([screw_diameter/2, -overstep*4/3, -screw_diameter/2])
                   cube([screw_diameter, overstep*8/3, screw_diameter], center = true);
            }
        }

        // cut off the top so we can see what's going on
        //translate([0, 0, height])
        //    cube([100, 100, 100], center = true);

        // now clean out the pointy thread ends to match the beall tap
        /*
        {
            translate([0, mounting_plate_width/2, thread_z_location - height/2])
            rotate([90, 0, 0])
            cylinder(h = mounting_plate_width, d = screw_diameter - 1/8 * 25.4, center = true);
        }*/
    }
}

// Generate the model
wood_threader();

