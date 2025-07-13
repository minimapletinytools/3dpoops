// replacement threader block for the beall threader
// this design prints the block larger than the beall delrin blocks and does not fit with the wood board that comes with the threader
// it is not necessary, just clamp directly to the block

use <BOSL/threading.scad>

// primary screw parameters
// screw diameter, you may want to make this slightly larger than the nominal size of the rod.
screw_diameter = 26; 
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

// alignment and screw hole dimensions (these are the same as the beall threader)
center_hole_diameter = 3/8 * 25.4; // 3/8 inch in mm
side_hole_diameter = 7/32 * 25.4;  // 7/32 inch in mm
side_hole_spacing = 1.375 * 25.4;  // 1 3/8 inches in mm
side_hole_bore_diameter = 10;
side_hole_non_bore_thickness = thread_z_padding/2;

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
            translate([chamfer_radius, chamfer_radius, chamfer_radius])
            cube([length - 2*chamfer_radius, width - 2*chamfer_radius, height - 2*chamfer_radius]);
            sphere(r = chamfer_radius, $fn = 32);
        }
    
        {
            // Center hole (3/8" diameter, halfway down)
            translate([length/2, width/2, height/4])
            cylinder(h = height/2 + poop, d = center_hole_diameter + fdm_overextrusion_offset, center = true);
        }
        
        // Side holes (7/32" diameter, all the way through)
        // Calculate positions for holes along the 3" dimension (width)
        for (i = [-1, 1]) {
            translate([length/2, width/2 + i * side_hole_spacing / 2, height/2])
            cylinder(h = height + poop, d = side_hole_diameter, center = true);
        }

        // now counterbore the 2 holes we just made
        for (i = [-1, 1]) {
            translate([length/2, width/2 + i * side_hole_spacing / 2, side_hole_non_bore_thickness + screw_diameter/4])
            cylinder(h = screw_diameter/2, d = side_hole_bore_diameter, center = true);
        }

        // Threaded hole using BOSL library
        {
            translate([length/2, width/2 + poop, thread_z_location])
            rotate([90, 0, 0])
            // rotate the rod so that the threads line up with the center hole
            rotate([0, 0, 180])
            // this uses the default thread angle of 30 which matches the beall tap
            threaded_rod(
                d = screw_diameter,
                l = width + poop*2,
                pitch = 25.4/tpi, // Convert TPI to pitch in mm
                internal = true,
                //bevel = true,
                $fn=64
            );
        }

        // we actually only want half the hole threaded, cut out the threads from the other half with a screw_diameter cylinder
        {
            translate([length/2, 0, thread_z_location])
            rotate([90, 0, 0])
            cylinder(h = width, d = screw_diameter, center = true);
        }

        // now clean out the pointy thread ends to match the beall tap
        {
            translate([length/2, 0, thread_z_location])
            rotate([90, 0, 0])
            cylinder(h = width*2, d = screw_diameter - 1/8 * 25.4, center = true);
        }
    }
}

// Generate the model
wood_threader();
