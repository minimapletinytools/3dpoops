// wood dowel threading block that attaches directly to a trim router

use <BOSL/threading.scad>

// primary screw parameters
// screw diameter, you may want to make this slightly larger than the nominal size of the rod.
screw_diameter = 26.5; 
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
mounting_plate_width = 100;
mounting_plate_length = 100;

// alignment and screw hole dimensions
center_hole_diameter = 3/8 * 25.4; // 3/8 inch in mm
side_hole_diameter = 7/32 * 25.4;  // 7/32 inch in mm
side_hole_bore_diameter = 10;
side_hole_bore_depth = 10;

// increase mounting hole dimensions by this amount to account for FDM overextrusion
fdm_overextrusion_offset = 0.05; 



// chamfer radius for rounded edges
chamfer_radius = 2; // 2mm radius for rounded corners

// annoying openSCAD stuff
poop = 0.01;

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

        // TODO add mounting holes
    
        {
            // Center hole (3/8" diameter, halfway down)
            translate([0, 0, -height/4])
            cylinder(h = height/2 + poop, d = center_hole_diameter + fdm_overextrusion_offset, center = true);
        }


        // Threaded hole using BOSL library
        {
            translate([0, 0, thread_z_location - height/2])
            rotate([90, 0, 0])
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

        // we actually only want half the hole threaded, cut out the threads from the other half with a screw_diameter cylinder
        {
            translate([0, mounting_plate_width/2, thread_z_location - height/2])
            rotate([90, 0, 0])
            cylinder(h = mounting_plate_width, d = screw_diameter, center = true);
        }

        // now clean out the pointy thread ends to match the beall tap
        {
            translate([0, mounting_plate_width/2, thread_z_location - height/2])
            rotate([90, 0, 0])
            cylinder(h = mounting_plate_width, d = screw_diameter - 1/8 * 25.4, center = true);
        }
    }
}

// Generate the model
wood_threader();
